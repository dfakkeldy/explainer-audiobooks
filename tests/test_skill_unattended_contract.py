from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]


class SkillUnattendedContractTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        text = (ROOT / relative).read_text(encoding="utf-8").casefold()
        return " ".join(text.split())

    def test_all_book_skills_route_through_the_shared_contract(self) -> None:
        for relative in (
            "skill/SKILL.md",
            "skills/custom-learning-audiobook/SKILL.md",
            "skills/longform-book-development/SKILL.md",
            "skills/fiction-book-development/SKILL.md",
        ):
            with self.subTest(skill=relative):
                self.assertIn("unattended-production.md", self.read(relative))

    def test_shared_contract_defines_modes_triggers_and_defaults(self) -> None:
        contract = self.read("skill/references/unattended-production.md")
        for marker in (
            "unattended-first-listen",
            "governed-final",
            "overnight",
            "wake up",
            "ready to listen",
            "start a few books",
            "curious beginner",
            "road-book",
            "am_michael",
            "am_puck",
            "private",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, contract)

    def test_unattended_mode_records_decisions_instead_of_asking_preferences(self) -> None:
        contract = self.read("skill/references/unattended-production.md")
        for marker in (
            "research/unattended-decisions.json",
            '"productionmode"',
            '"humanlisteningstatus": "pending"',
            "do not ask about routine preferences",
            "safe reversible default",
            "requestevidence",
            "deliveryintent",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, contract)

    def test_batch_items_finish_with_a_package_or_blocker(self) -> None:
        contract = self.read("skill/references/unattended-production.md")
        for marker in (
            "package-or-blocker",
            "blocker receipt",
            "does not stop the remaining books",
            "resumable next action",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, contract)

    def test_unattended_mode_never_implies_publication_or_human_acceptance(self) -> None:
        contract = self.read("skill/references/unattended-production.md")
        for marker in (
            "never auto-publish",
            "humancomprehensionpilot: pending",
            "humanlistening: pending",
            "negative human verdict",
            "editorial-autoselection",
            "permission_to_publish: false",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, contract)

    def test_explicit_authorization_can_promote_a_verified_first_listen(self) -> None:
        contract = self.read("skill/references/unattended-production.md")
        for marker in (
            "public-first-listen",
            "explicit publication authorization",
            "humanlisteningstatus: pending",
            "full listening review is still underway",
            "negative human verdict supersedes",
            "never auto-publish",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, contract)


if __name__ == "__main__":
    unittest.main()
