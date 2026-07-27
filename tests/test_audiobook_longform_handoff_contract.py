from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).parents[1]
AUDIOBOOK = REPO / "skill" / "SKILL.md"
LONGFORM = REPO / "skills" / "longform-book-development" / "SKILL.md"
PACKET = (
    REPO
    / "skills"
    / "longform-book-development"
    / "references"
    / "handoff-packet.md"
)


class AudiobookLongformHandoffContractTests(unittest.TestCase):
    def test_ordinary_request_asks_exactly_five_questions(self) -> None:
        text = AUDIOBOOK.read_text(encoding="utf-8")
        ordinary = text.split("### Ordinary request", 1)[1].split(
            "### Complete longform handoff", 1
        )[0]
        numbered_questions = re.findall(r"(?m)^([1-5])\. ", ordinary)
        self.assertEqual(["1", "2", "3", "4", "5"], numbered_questions, ordinary)
        self.assertNotRegex(ordinary, r"(?m)^6\. ")
        self.assertIn("host's available batched input mechanism", ordinary)
        self.assertNotIn("AskUserQuestion", ordinary)

    def test_skill_defines_cross_repo_narration_and_durable_source_contracts(self) -> None:
        audiobook = AUDIOBOOK.read_text(encoding="utf-8")
        for marker in (
            "absolute `BOOK_ROOT`",
            "`$BOOK_ROOT/source/brief.md`",
            "`$BOOK_ROOT/source/outline.md`",
            "`$BOOK_ROOT/source/research/`",
            "`$BOOK_ROOT/source/chapters/`",
            "`$BOOK_ROOT/source/feedback.md`",
            "references/narrating.md",
            "NARRATION_SCRIPT",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, audiobook)

    def test_skill_scopes_standing_private_delivery_authorization_to_dan(self) -> None:
        audiobook = AUDIOBOOK.read_text(encoding="utf-8")
        self.assertIn("standing private iCloud authorization", audiobook)
        self.assertIn("Dan-specific", audiobook)
        self.assertIn("other user or context", audiobook)
        self.assertIn("explicitly opts in", audiobook)

    def test_complete_handoff_skips_repeated_intake_and_converges_on_start(self) -> None:
        audiobook = AUDIOBOOK.read_text(encoding="utf-8")
        longform = LONGFORM.read_text(encoding="utf-8")
        packet = PACKET.read_text(encoding="utf-8")

        self.assertIn("skip the five-question intake", audiobook)
        self.assertIn("without repeating the five-question intake", longform)
        self.assertIn("After either route", audiobook)
        self.assertIn("state the plan in one line", audiobook)
        self.assertIn("no approval pause", audiobook)

        shared_requirements = (
            "audience",
            "outcome",
            "length",
            "privacy",
            "listening context",
            "governing question",
            "narrative spine",
            "chapter",
            "section",
            "source locators",
            "story",
            "voice",
            "figure",
            "craft passes",
            "blind beginner",
            "narration risks",
            "author",
            "contributor",
            "delivery",
        )
        for requirement in shared_requirements:
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, audiobook.lower())
                self.assertIn(requirement, packet.lower())


if __name__ == "__main__":
    unittest.main()
