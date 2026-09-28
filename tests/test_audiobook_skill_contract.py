from __future__ import annotations

import unittest
from pathlib import Path

REPO = Path(__file__).parents[1]
SKILL = REPO / "skill" / "SKILL.md"


class AudiobookSkillContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = SKILL.read_text(encoding="utf-8")

    def test_skill_is_named_audiobook(self) -> None:
        self.assertTrue(self.text.startswith("---\n"))
        header = self.text.split("\n---\n", 1)[0]
        self.assertIn("name: audiobook", header)

    def test_skill_is_lean(self) -> None:
        lines = self.text.splitlines()
        self.assertLess(len(lines), 200, f"SKILL.md is {len(lines)} lines")

    def test_semantic_voice_casting_reference_is_routed(self) -> None:
        self.assertIn("references/semantic-voice-casting.md", self.text)

    def test_production_validates_the_semantic_cast_before_handoff(self) -> None:
        self.assertIn("validate the semantic cast", " ".join(self.text.split()))
        self.assertNotIn("validate the\nsemantic ledger", self.text)

    def test_intake_asks_five_questions_then_starts(self) -> None:
        for needle in (
            "what should the listener be able to do",
            "Who is it for",
            "already know",
            "how long",
            "specific real thing",
        ):
            self.assertIn(needle, self.text)
        self.assertIn("state the plan in one line", self.text)

    def test_finish_line_is_the_fixed_contract(self) -> None:
        normalized = " ".join(self.text.split())
        for needle in (
            "../skills/echo-narration/references/complete-delivery.md",
            "epub-pronunciation.md",
            "`<Book Title>.epub` with the portrait cover embedded",
            "pronunciation annotations",
            "complete Echo narration with the square cover embedded",
            "`<Book Title>.alignment.json`",
            "`verify-sidecar`",
            "`cover.png` (portrait) and `m4b-cover.png` (square)",
            "com~apple~CloudDocs/Books",
        ):
            with self.subTest(needle=needle):
                self.assertIn(needle, normalized)

    def test_writing_is_left_to_the_author(self) -> None:
        normalized = " ".join(self.text.split())
        self.assertIn("Write the best book you can.", normalized)
        self.assertIn(
            "No humanizer pass, AI-tell sweep, or prose-style gate is required.",
            normalized,
        )
        self.assertIn("story ledger", normalized)
        self.assertIn("may only assert what the research supports", normalized)
        for retired in (
            "--fail-on-style",
            "prose_qc",
            "humanizer-pass.md",
            "declaudification.md",
            "claim-traceability",
            "de-listification",
        ):
            with self.subTest(retired=retired):
                self.assertNotIn(retired, self.text)

    def test_defaults_are_recorded(self) -> None:
        for needle in ("am_michael", "am_puck", "Dan Fakkeldy", "road-book"):
            self.assertIn(needle, self.text)
        self.assertIn("af_heart", self.text)

    def test_pillow_interpreter_is_documented(self) -> None:
        self.assertIn("/usr/local/bin/python3", self.text)

    def test_delivery_layout_is_specified(self) -> None:
        for needle in ("source/", "previous/", "feedback.md", "brief.md"):
            self.assertIn(needle, self.text)
        self.assertIn("com~apple~CloudDocs/Books", self.text)

    def test_preserve_on_revision_rule_survives(self) -> None:
        self.assertIn("what is working and must not change", self.text)

    def test_practical_road_book_support_is_routed_from_the_skill(self) -> None:
        normalized = " ".join(self.text.split())
        for marker in (
            "situation-choice-consequence",
            "`Key points` checkpoint",
            "two to four",
            "with no new facts",
            "retrieval handles",
            "drifted listener",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, normalized)

    def test_retired_gate_vocabulary_is_gone(self) -> None:
        for banned in (
            "learning receipt",
            "--learning-receipt",
            "prose-style-receipt",
            "unattended-first-listen",
            "governed-final",
            "public-first-listen",
            "permission-to-publish",
            "comprehension pilot",
            "probe reel",
            "package-or-blocker",
            "coverage ledger",
        ):
            self.assertNotIn(banned, self.text, f"retired gate vocabulary present: {banned!r}")


if __name__ == "__main__":
    unittest.main()
