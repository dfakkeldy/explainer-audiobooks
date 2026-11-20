"""The post-render pronunciation gate, on small synthetic audits.

Every fixture sentence is invented for these tests.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "echo-narration" / "scripts"
GATE = SCRIPTS / "pronunciation_audit_gate.py"
WRAPPER = SCRIPTS / "echo_pronunciation_narrate.sh"


def decision(word: str, ipa: str, context: str, *, word_start: int = 5, source: str = "monitoredLexicon",
             rule: str | None = None, start: float | None = 1652.0, block: str = "s4-b6") -> dict:
    """One audit decision in Echo's shape; the context holds five words either side."""
    payload = {
        "blockID": f"epub-runner-fixture-fixture.epub-{block}",
        "wordStart": word_start,
        "wordEnd": word_start,
        "normalizedWord": word.lower(),
        "sourceWord": word,
        "sourceContext": context,
        "selectedIPA": ipa,
        "kokoroTokenIDs": [1],
        "source": source,
        "ruleID": rule or f"g2p.lexicon.{word.lower()}",
        "rationale": "fixture",
        "chapterIndex": 2,
    }
    if start is not None:
        payload["chapterRelativeAudioRange"] = {"start": start - 100, "end": start - 99}
        payload["bookRelativeAudioRange"] = {"start": start, "end": start + 1}
        payload["timingPrecision"] = "exactSynthesisWord"
    return payload


def epub_ipa(word: str, ipa: str, context: str, **fields: object) -> dict:
    """A decision whose reading came from IPA written in the EPUB."""
    return decision(word, ipa, context, source="epubInline", rule="epub.inline.ipa-v1", **fields)


CLEAN = [
    # The real article before a word, a letter or a whole initialism stays "uh".
    decision("A", "ɐ", "sat on the old step. A heron waded past the reeds"),
    decision("a", "ɐ", "the lane was shut. Take a U-turn at the mill"),
    decision("A", "ɐ", "the shop by the pier. A GPU there costs more than"),
    # A letter-by-letter A in a hyphen-spelled initialism, read as a letter.
    decision("A", "ˈA", "we asked them whether an A-I tool could sort the mail"),
    epub_ipa("AI", "ˌAˈI", "lunch the crew asked the AI to tidy the notes"),
    epub_ipa("AI.", "ˌAˈI", "clerks sent the forms to AI."),
]


class PronunciationAuditGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def audit(self, decisions: list[dict]) -> Path:
        path = self.dir / "fixture.pronunciation-audit.json"
        path.write_text(json.dumps({"schemaVersion": 7, "decisions": decisions}, ensure_ascii=False),
                        encoding="utf-8")
        return path

    def accept(self, payload: object) -> Path:
        path = self.dir / "pronunciation-gate-accepted.json"
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return path

    def run_gate(self, *args: object) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(GATE), *map(str, args)], capture_output=True, text=True)

    def test_clean_audit_passes(self) -> None:
        result = self.run_gate(self.audit(CLEAN))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("pronunciation_gate: clean\n", result.stdout)

    def test_fallback_words_fail_with_count_time_and_context(self) -> None:
        decisions = CLEAN + [
            decision("glimmerwick", "ɡlˈɪmɚwɪk", "the baker lit the old glimmerwick, and the oven warmed",
                     source="fallback", rule="g2p.fallback.glimmerwick", start=1652.01),
            decision("glimmerwick", "ɡlˈɪmɚwɪk", "day later. With the old glimmerwick, the loaves came out",
                     source="fallback", rule="g2p.fallback.glimmerwick", start=1655.94),
            decision("overplanks", "ˌOvɚplˈæŋks", "the dock rests on long overplanks of pine and tar",
                     source="fallback", rule="g2p.compound.overplanks", start=None, block="s9-b2"),
            decision("Tobrin", "tˈɑbɹɪn", "list of rowers: Mara Lind, Tobrin Holt, Ivo Pek and Ana",
                     source="monitoredLexicon", rule="g2p.fallback.tobrin"),
        ]
        result = self.run_gate(self.audit(decisions))
        self.assertEqual(1, result.returncode)
        self.assertIn("FAIL fallback 'glimmerwick' x2: not in Echo's lexicon, so it guessed (ɡlˈɪmɚwɪk)",
                      result.stderr)
        self.assertIn("0:27:32  s4-b6  ɡlˈɪmɚwɪk  \"the baker lit the old glimmerwick,", result.stderr)
        self.assertIn("0:27:35  s4-b6", result.stderr)
        self.assertIn("FAIL fallback 'overplanks' x1", result.stderr)
        self.assertIn("untimed  s9-b2", result.stderr)
        self.assertIn("FAIL fallback 'Tobrin' x1", result.stderr)
        self.assertIn("pronunciation_gate: 3 problem(s)", result.stderr)
        self.assertEqual("", result.stdout)

    def test_article_reading_of_a_hyphen_spelled_initialism_fails(self) -> None:
        decisions = CLEAN + [
            decision("A", "ɐ", "the council hopes to link A-I use with bus routes, parks and",
                     word_start=17, start=199.0),
            decision("A", "ɐ", "the A-P-I logs grew over the winter months", word_start=1, start=1936.0),
            decision("A", "ɐ", "\"A-I can wait,\" the clerk said, and the line", word_start=0, start=3600.0),
            # A-I joined to the word before by an em dash or a slash is one context word.
            decision("A", "ɐ", "the crew finished the job—A-I made the rest quick", word_start=4, start=4210.0),
            decision("A", "ɐ", "most of the staff said people/A-P-I use kept rising", start=4800.0),
        ]
        result = self.run_gate(self.audit(decisions))
        self.assertEqual(1, result.returncode)
        self.assertIn("FAIL article-initialism 'A' x5: read as the article 'uh' (ɐ)", result.stderr)
        self.assertIn("write it closed (AI, API)", result.stderr)
        for clock in ("0:03:19", "0:32:16", "1:00:00", "1:10:10", "1:20:00"):
            with self.subTest(clock=clock):
                self.assertIn(clock, result.stderr)

    def test_dash_or_slash_before_a_real_article_passes(self) -> None:
        decisions = CLEAN + [
            decision("a", "ɐ", "the trail ended at the gate—a U-turn was the only way", word_start=6),
            decision("a", "ɐ", "pick the stairs or/a ramp by the front door", word_start=3),
        ]
        result = self.run_gate(self.audit(decisions))
        self.assertEqual(0, result.returncode, result.stderr)

    def test_one_initialism_with_two_readings_fails(self) -> None:
        # Echo's lexicon spells AI letter by letter with its own stress, and its
        # rule ID looks like an ordinary word's (g2p.lexicon.ai). It still counts.
        decisions = CLEAN + [decision("AI", "ˈAˌI", "a chapter heading about AI and the tides", word_start=4,
                                      start=600.0)]
        result = self.run_gate(self.audit(decisions))
        self.assertEqual(1, result.returncode)
        self.assertIn("FAIL initialism-readings 'AI' x3: read 2 ways (ˌAˈI x2, ˈAˌI x1)", result.stderr)
        self.assertIn("0:10:00", result.stderr)

    def test_plural_initialism_spelled_two_ways_fails(self) -> None:
        decisions = CLEAN + [
            epub_ipa("GPUs", "ʤˌipˌijˈuz", "the lab bought six new GPUs for the winter", start=700.0),
            decision("GPUs", "ʤˈipˌijˌuz", "old GPUs sat in a box by the door", word_start=1, start=800.0),
            decision("LLMs", "ˌɛlˌɛlˈɛmz", "two LLMs wrote the first draft of it", word_start=1),
        ]
        result = self.run_gate(self.audit(decisions))
        self.assertEqual(1, result.returncode)
        self.assertIn("FAIL initialism-readings 'GPUs' x2: read 2 ways", result.stderr)
        self.assertNotIn("'LLMs'", result.stderr)

    def test_caps_words_read_as_ordinary_words_pass(self) -> None:
        # misaki reads THE as "thee" before a vowel and "thuh" before a consonant,
        # and TO, USE and US by context too. None of these is an initialism.
        def word(text: str, ipa: str, context: str, at: int) -> dict:
            return decision(text, ipa, context, word_start=at)

        decisions = CLEAN + [
            word("THE", "ði", "the last page said THE END in red ink", 4),
            word("THE", "ðə", "she yelled GET THE DOOR from the porch", 3),
            word("THE", "ðə", "a road sign read THE ROAD AHEAD IS SHUT", 4),
            word("TO", "tə", "the poster said RUN TO THE BOAT", 4),
            word("TO", "tʊ", "the poster said GO TO EACH DOCK", 4),
            word("USE", "jˈuz", "a tag said DO NOT USE THIS PUMP", 5),
            word("USE", "jˈus", "a tag said FOR STAFF USE ONLY", 5),
            word("US", "jˌuˈɛs", "she flew to the US in May", 4),
            epub_ipa("US", "jˌuˈɛs", "the US team won the race", word_start=1),
            # Caps heteronyms carry an inline reading per sense, as the pre-render check asks.
            epub_ipa("READ", "ɹˈid", "the sign over the desk said READ ME FIRST", word_start=5),
            epub_ipa("READ", "ɹˈɛd", "the stamp on the file said READ AND FILED", word_start=5),
            decision("LIVE", "lˈIv", "the red lamp said LIVE ON AIR", word_start=4, source="homograph",
                     rule="homograph.live.adjective"),
            decision("LIVE", "lˈɪv", "the poster said WE LIVE HERE NOW", word_start=3, source="homograph",
                     rule="homograph.live.verb"),
        ]
        result = self.run_gate(self.audit(decisions))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("pronunciation_gate: clean\n", result.stdout)

    def test_caps_word_read_as_a_word_and_as_letters_fails_unless_accepted(self) -> None:
        audit = self.audit(CLEAN + [
            decision("US", "ˌʌs", "the banner said LET US SING", word_start=4),
            decision("US", "jˌuˈɛs", "she flew to the US in May", word_start=4),
        ])
        result = self.run_gate(audit)
        self.assertEqual(1, result.returncode)
        self.assertIn("FAIL initialism-readings 'US' x2: read 2 ways", result.stderr)
        accept = self.accept({"schemaVersion": 1, "accepted": [
            {"check": "initialism-readings", "word": "US", "reason": "the pronoun in a caps banner"}]})
        result = self.run_gate(audit, "--accept", accept)
        self.assertEqual(0, result.returncode, result.stderr)

    def test_accept_file_waives_exact_words_with_a_reason(self) -> None:
        audit = self.audit(CLEAN + [
            decision("Quorvane", "kwˈɔɹveɪn", "a note from Quorvane and her crew, which", word_start=3,
                     source="fallback", rule="g2p.fallback.quorvane"),
            decision("glimmerwick", "ɡlˈɪmɚwɪk", "the old glimmerwick said", word_start=2, source="fallback",
                     rule="g2p.fallback.glimmerwick"),
        ])
        accept = self.accept({"schemaVersion": 1, "accepted": [
            {"check": "fallback", "word": "Quorvane", "reason": "author's own spelling; no reading yet"},
            {"check": "fallback", "word": "Brannoc", "reason": "fixed earlier"},
        ]})
        result = self.run_gate(audit, "--accept", accept)
        self.assertEqual(1, result.returncode)
        self.assertIn("accepted fallback 'Quorvane' x1: author's own spelling", result.stderr)
        self.assertIn("FAIL fallback 'glimmerwick'", result.stderr)
        self.assertNotIn("FAIL fallback 'Quorvane'", result.stderr)
        self.assertIn("lists fallback 'Brannoc', which this audit doesn't need", result.stderr)
        accept = self.accept({"schemaVersion": 1, "accepted": [
            {"check": "fallback", "word": "Quorvane", "reason": "no reading yet"},
            {"check": "fallback", "word": "glimmerwick", "reason": "no reading yet"},
        ]})
        self.assertEqual(0, self.run_gate(audit, "--accept", accept).returncode)

    def test_accept_file_must_name_the_check_word_and_reason(self) -> None:
        audit = self.audit(CLEAN)
        for entry in ({"check": "fallback", "word": "Brannoc", "reason": " "},
                      {"check": "everything", "word": "Brannoc", "reason": "why"},
                      {"check": "fallback", "word": "Brannoc"},
                      {"check": "fallback", "word": "Brannoc", "reason": "why", "extra": 1}):
            with self.subTest(entry=entry):
                result = self.run_gate(audit, "--accept", self.accept({"schemaVersion": 1, "accepted": [entry]}))
                self.assertEqual(65, result.returncode, result.stderr)
        link = self.dir / "linked.json"
        link.symlink_to(self.accept({"schemaVersion": 1, "accepted": []}))
        result = self.run_gate(audit, "--accept", link)
        self.assertEqual(65, result.returncode)
        self.assertIn("must be a regular file", result.stderr)

    def test_probe_render_captures_show_fallbacks_before_the_full_render(self) -> None:
        guessed = decision("Brannoc", "bɹˈænək", "a card from Brannoc about the boat", word_start=3,
                           source="fallback", rule="g2p.fallback.brannoc", start=None)
        guessed["chapterRelativeAudioRange"] = {"start": 151.7, "end": 152.5}
        markers = []
        for index, decisions in enumerate(([guessed], CLEAN)):
            marker = self.dir / f".anchors-ch{index}.json"
            marker.write_text(json.dumps({"anchors": [], "duration": 1.0, "identity": {},
                                          "pronunciationEvidence": {"decisions": decisions, "diagnostics": []}}),
                              encoding="utf-8")
            markers.append(marker)
        result = self.run_gate(*markers)
        self.assertEqual(1, result.returncode)
        self.assertIn("FAIL fallback 'Brannoc' x1", result.stderr)
        self.assertIn("ch2 chapter-relative 0:02:31", result.stderr)
        self.assertEqual(0, self.run_gate(markers[1]).returncode)

    def test_unreadable_audit_is_an_input_error(self) -> None:
        bad = self.dir / "bad.pronunciation-audit.json"
        bad.write_text("{not json", encoding="utf-8")
        self.assertEqual(65, self.run_gate(bad).returncode)
        bad.write_text(json.dumps({"decisions": "none"}), encoding="utf-8")
        self.assertEqual(65, self.run_gate(bad).returncode)
        self.assertEqual(64, self.run_gate().returncode)


class NarrationWrapperRunsTheGateTests(unittest.TestCase):
    def test_wrapper_runs_the_gate_on_the_published_audit_before_accepting(self) -> None:
        wrapper = WRAPPER.read_text(encoding="utf-8")
        gate = wrapper.index('"$SCRIPT_DIR/pronunciation_audit_gate.py" "$AUDIT"')
        last_validation = wrapper.rindex('"$SCRIPT_DIR/validate_pronunciation_audit.py" "$AUDIT"')
        self.assertLess(last_validation, gate)
        self.assertLess(gate, wrapper.index("write-success --receipt"))
        self.assertLess(gate, wrapper.index("accept-attempt"))
        self.assertIn('GATE_ACCEPT="$RUN_ROOT/research/pronunciation-gate-accepted.json"', wrapper)
        self.assertIn("pronunciation gate failed", wrapper)

    def test_delivery_verification_runs_the_gate(self) -> None:
        narrating = (ROOT / "skills" / "echo-narration" / "references" / "narrating.md").read_text(
            encoding="utf-8")
        self.assertEqual(2, narrating.count("scripts/pronunciation_audit_gate.py"))
        self.assertIn("pronunciation_gate: clean", narrating)


if __name__ == "__main__":
    unittest.main()
