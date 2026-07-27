from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
DESIGN = (
    ROOT
    / "docs"
    / "superpowers"
    / "specs"
    / "2026-07-26-audiobook-defortification-design.md"
)
PLAN = (
    ROOT
    / "docs"
    / "superpowers"
    / "plans"
    / "2026-07-26-audiobook-defortification.md"
)


class AudiobookDefortificationDesignContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.design = DESIGN.read_text(encoding="utf-8")
        self.plan = PLAN.read_text(encoding="utf-8")

    def test_no_remaining_claim_that_echo_accepts_an_optional_word_list(self) -> None:
        combined = (self.design + "\n" + self.plan).casefold()
        self.assertNotIn("optional word list is still supported", combined)
        self.assertNotIn("word list is genuinely useful input", combined)

    def test_migration_checklist_covers_both_installed_skill_hosts(self) -> None:
        for host in ("~/.claude/skills", "~/.agents/skills"):
            for name in (
                "explainer-audiobook",
                "custom-learning-audiobook",
                "audiobook",
            ):
                with self.subTest(host=host, name=name):
                    self.assertIn(f"`{host}/{name}`", self.design)


if __name__ == "__main__":
    unittest.main()
