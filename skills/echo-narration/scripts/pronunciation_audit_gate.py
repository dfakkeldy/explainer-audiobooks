#!/usr/bin/env python3
"""Refuse a rendered audiobook whose pronunciation audit shows guessed words.

Run it after validate_pronunciation_audit.py on the same audit. It fails when:

- fallback: a decision came from Echo's letter-rule guess (source "fallback",
  rule IDs g2p.fallback.* and g2p.compound.*);
- article-initialism: an "A" was read as the article ɐ ("uh") where it is the
  first letter of a hyphen-spelled initialism (A-I, A-P-I: "uh-EYE"). A real
  article before a separate word ("A GPU", "a U-turn") passes;
- initialism-readings: one initialism (2-6 capitals, optional s) was read more
  than one way in the book. Echo records every all-caps word, and caps words
  such as THE, TO, USE or READ are rightly read more than one way (THE is
  "thee" before a vowel; READ carries an inline reading per sense). So a caps
  word is compared only when at least one of its readings spells it letter by
  letter or was guessed. A word that is truly both (US as "us" and as letters)
  goes in the accept file.

Each problem prints the word, its count, and the time and context of each use.

It also reads the capture markers of a partial probe render
(`.anchors-ch*.json` in the run's audio work directory), whose
`pronunciationEvidence` holds the same decisions, so a one-chapter probe can
show zero fallbacks before the full render.

An accept file lists the exact words that truly can't be fixed, each with a
reason. The narration wrapper passes `research/pronunciation-gate-accepted.json`
from the run root when it exists; by default there is none:

    {"schemaVersion": 1,
     "accepted": [{"check": "fallback", "word": "Quorvane",
                   "reason": "author's spelling; no reading Echo accepts yet"}]}

Exit codes: 0 pass, 1 gate failed, 64 usage, 65 unreadable input.
"""
from __future__ import annotations

import argparse
import json
import re
import stat
import sys
from collections import defaultdict
from pathlib import Path

CHECKS = ("fallback", "article-initialism", "initialism-readings")
# Echo's audit context holds five words either side of the decision's word.
CONTEXT_RADIUS = 5
BLOCK_ID = re.compile(r"s[0-9]+-b[0-9]+\Z")
INITIALISM = re.compile(r"[A-Z]{2,6}s?")
EDGE_PUNCTUATION = re.compile(r"^[^\w]+|[^\w]+$")
# A-I or A-P-I inside one context word, alone or after a dash, slash or quote.
SPELLED_INITIALISM = re.compile(r"(?:^|[^\w-])[Aa](?:-[A-Z])+")
# misaki's US letter names (us_gold.json "A".."Z") without stress marks. It
# spells an initialism by joining these, so a letter-by-letter reading matches.
LETTER_NAMES = {
    "A": "A", "B": "bi", "C": "si", "D": "di", "E": "i", "F": "ɛf", "G": "ʤi",
    "H": "Aʧ", "I": "I", "J": "ʤA", "K": "kA", "L": "ɛl", "M": "ɛm", "N": "ɛn",
    "O": "O", "P": "pi", "Q": "kju", "R": "ɑɹ", "S": "ɛs", "T": "ti", "U": "ju",
    "V": "vi", "W": "dʌbəlju", "X": "ɛks", "Y": "wI", "Z": "zi",
}
PLURAL_ENDINGS = ("z", "s", "ᵻz", "ɪz", "əz")
SHOWN_PER_WORD = 12


class GateInputError(ValueError):
    """The audit or accept file can't be read."""


def read_json(path: Path, label: str) -> object:
    try:
        if stat.S_ISLNK(path.lstat().st_mode) or not path.is_file():
            raise GateInputError(f"{label} must be a regular file: {path}")
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise GateInputError(f"cannot read {label} {path}: {error}") from error


def load_accepted(path: Path | None) -> dict[tuple[str, str], str]:
    if path is None:
        return {}
    data = read_json(path, "accept file")
    if not isinstance(data, dict) or set(data) != {"schemaVersion", "accepted"} \
            or data["schemaVersion"] != 1 or not isinstance(data["accepted"], list):
        raise GateInputError("accept file must be {\"schemaVersion\": 1, \"accepted\": [...]}")
    accepted: dict[tuple[str, str], str] = {}
    for index, entry in enumerate(data["accepted"]):
        label = f"accepted[{index}]"
        if not isinstance(entry, dict) or set(entry) != {"check", "word", "reason"}:
            raise GateInputError(f"{label} must have exactly check, word and reason")
        if entry["check"] not in CHECKS:
            raise GateInputError(f"{label}.check must be one of {', '.join(CHECKS)}")
        for key in ("word", "reason"):
            if not isinstance(entry[key], str) or not entry[key].strip():
                raise GateInputError(f"{label}.{key} must be a nonempty string")
        accepted[(entry["check"], entry["word"])] = entry["reason"].strip()
    return accepted


def timestamp(decision: dict) -> str:
    def clock(seconds: float) -> str:
        whole = int(seconds)
        return f"{whole // 3600}:{whole % 3600 // 60:02d}:{whole % 60:02d}"

    for field, prefix in (("bookRelativeAudioRange", ""), ("chapterRelativeAudioRange", "chapter-relative ")):
        span = decision.get(field)
        if isinstance(span, dict) and isinstance(span.get("start"), (int, float)):
            chapter = decision.get("chapterIndex")
            where = f"ch{chapter} " if prefix and isinstance(chapter, int) else ""
            return where + prefix + clock(span["start"])
    return "untimed"


def block_of(decision: dict) -> str:
    block = str(decision.get("blockID", ""))
    match = BLOCK_ID.search(block)
    return match.group(0) if match else block


def clean(word: str) -> str:
    return EDGE_PUNCTUATION.sub("", word)


def follows_initialism(decision: dict) -> bool:
    """True when this article "A" is really the first letter of an initialism."""
    words = str(decision.get("sourceContext", "")).split(" ")
    word_start = decision.get("wordStart")
    if not isinstance(word_start, int) or word_start < 0:
        return False
    index = min(word_start, CONTEXT_RADIUS)
    if index >= len(words):
        return False
    # Echo's context words are split on spaces, so A-I is one word ("A-I",
    # "work—A-I", "and/A-I") whose A this decision read. A real article before a
    # separate word ("a U-turn") passes.
    return SPELLED_INITIALISM.search(words[index]) is not None


def spelled_out(word: str, ipa: str) -> bool:
    """True when the reading says the word's capitals letter by letter."""
    letters = word[:-1] if word.endswith("s") else word
    spelled = "".join(LETTER_NAMES.get(letter, "?") for letter in letters)
    said = re.sub(r"[ˈˌ\s]", "", ipa).replace("ᵊ", "ə")
    if said == spelled:
        return True
    return word.endswith("s") and any(said == spelled + ending for ending in PLURAL_ENDINGS)


def says_letters(word: str, ipa: str, guessed: bool) -> bool:
    """True when this reading treats the caps word as an initialism.

    Echo gives the same rule ID (g2p.lexicon.<word>) to a lexicon word and a
    lexicon initialism (AI is g2p.lexicon.ai too), and inline readings of caps
    heteronyms (READ, USE) are epub.inline like any other, so the reading
    decides: letter by letter, or a guess.
    """
    return guessed or spelled_out(word, ipa)


def findings(decisions: list[dict]) -> list[tuple[str, str, list[dict], str]]:
    """(check, word, decisions, detail) for each problem, in book order."""
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    readings: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    lettered: set[str] = set()
    for decision in decisions:
        word = str(decision.get("sourceWord", ""))
        rule = str(decision.get("ruleID", ""))
        ipa = str(decision.get("selectedIPA", "")).strip()
        guessed = decision.get("source") == "fallback" or rule.startswith("g2p.fallback")
        if guessed:
            groups[("fallback", word)].append(decision)
        if word in ("A", "a") and ipa == "ɐ" and follows_initialism(decision):
            groups[("article-initialism", word)].append(decision)
        caps = clean(word)
        if INITIALISM.fullmatch(caps):
            readings[caps][ipa].append(decision)
            if says_letters(caps, ipa, guessed):
                lettered.add(caps)
    readings = {word: by_ipa for word, by_ipa in readings.items() if word in lettered}
    result = []
    for (check, word), items in groups.items():
        if check == "fallback":
            ipas = sorted({str(d.get("selectedIPA", "")) for d in items})
            detail = f"not in Echo's lexicon, so it guessed ({', '.join(ipas)}); give it IPA in the EPUB"
        else:
            detail = "read as the article 'uh' (ɐ) at the start of an initialism; write it closed (AI, API)"
        result.append((check, word, items, detail))
    for word, by_ipa in readings.items():
        if len(by_ipa) > 1:
            items = [d for ipa_items in by_ipa.values() for d in ipa_items]
            counts = ", ".join(f"{ipa} x{len(found)}" for ipa, found in by_ipa.items())
            result.append(("initialism-readings", word, items,
                           f"read {len(by_ipa)} ways ({counts}); give it one reading for the whole book"))
    return result


def load_decisions(path: Path) -> list[dict]:
    """Decisions from a pronunciation audit or from one capture marker."""
    payload = read_json(path, "pronunciation audit")
    if isinstance(payload, dict) and "decisions" not in payload \
            and isinstance(payload.get("pronunciationEvidence"), dict):
        payload = payload["pronunciationEvidence"]
    decisions = payload.get("decisions") if isinstance(payload, dict) else None
    if not isinstance(decisions, list) or not all(isinstance(d, dict) for d in decisions):
        raise GateInputError(f"{path} has no pronunciation decisions array")
    return decisions


def run(paths: list[Path], accept_path: Path | None) -> tuple[list[str], list[str], int]:
    """(problem lines, notes, number of problems)."""
    decisions = [d for path in paths for d in load_decisions(path)]
    accepted = load_accepted(accept_path)
    lines: list[str] = []
    notes: list[str] = []
    used: set[tuple[str, str]] = set()
    problems = 0
    for check, word, items, detail in findings(decisions):
        if (check, word) in accepted:
            used.add((check, word))
            notes.append(f"accepted {check} '{word}' x{len(items)}: {accepted[(check, word)]}")
            continue
        problems += 1
        lines.append(f"FAIL {check} '{word}' x{len(items)}: {detail}")
        for decision in items[:SHOWN_PER_WORD]:
            lines.append(f"  {timestamp(decision)}  {block_of(decision)}  "
                         f"{decision.get('selectedIPA', '')}  \"{decision.get('sourceContext', '')}\"")
        if len(items) > SHOWN_PER_WORD:
            lines.append(f"  ... and {len(items) - SHOWN_PER_WORD} more")
    for check, word in sorted(set(accepted) - used):
        notes.append(f"accept file lists {check} '{word}', which this audit doesn't need; remove it")
    return lines, notes, problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("audit_json", type=Path, nargs="+",
                        help="the pronunciation audit, or a probe render's .anchors-ch*.json captures")
    parser.add_argument("--accept", type=Path, help="accept file listing words that truly can't be fixed")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exit_:
        return 0 if exit_.code == 0 else 64
    try:
        lines, notes, problems = run(args.audit_json, args.accept)
    except GateInputError as error:
        print(f"pronunciation_gate: {error}", file=sys.stderr)
        return 65
    for note in notes:
        print(f"pronunciation_gate: {note}", file=sys.stderr)
    if problems:
        for line in lines:
            print(f"pronunciation_gate: {line}", file=sys.stderr)
        print(f"pronunciation_gate: {problems} problem(s). Fix the EPUB (IPA for every guessed word, closed "
              "initialisms with one reading) and render again; list a word in the accept file only when it "
              "truly can't be fixed", file=sys.stderr)
        return 1
    print("pronunciation_gate: clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
