from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]


class SkillProseContractTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_shared_declaudification_reference_defines_prevention_and_density_gate(self) -> None:
        path = ROOT / "skill" / "references" / "declaudification.md"
        self.assertTrue(path.is_file())
        text = path.read_text(encoding="utf-8").lower()
        for phrase in (
            "reader-management",
            "phrase family",
            "density",
            "hard failure",
            "state the fact directly",
            "--fail-on-style",
            "--style-receipt-out",
        ):
            self.assertIn(phrase, text)

    def test_every_audiobook_skill_uses_the_shared_gate(self) -> None:
        for relative in (
            "skill/SKILL.md",
            "skills/custom-learning-audiobook/SKILL.md",
            "skills/longform-book-development/SKILL.md",
        ):
            with self.subTest(relative=relative):
                text = self.read(relative)
                self.assertIn("declaudification.md", text)
                self.assertIn("AI-writing patterns to avoid", text)

        for relative in (
            "skill/SKILL.md",
            "skills/custom-learning-audiobook/SKILL.md",
        ):
            with self.subTest(production_skill=relative):
                text = self.read(relative)
                self.assertIn("--fail-on-style", text)
                self.assertIn("--prose-receipt", text)

    def test_humanizer_contract_requires_global_inventory_and_hash_bound_receipt(self) -> None:
        text = self.read("skill/references/humanizer-pass.md")
        for phrase in (
            "independent inventory",
            "chapter by chapter",
            "whole manuscript",
            "before and after",
            "accepted",
            "rejected",
            "chapter hashes",
        ):
            self.assertIn(phrase, text)

    def test_longform_handoff_carries_disliked_patterns_and_positive_voice_sample(self) -> None:
        text = self.read("skills/longform-book-development/references/handoff-packet.md")
        self.assertIn("Disliked phrase families", text)
        self.assertIn("Positive voice sample", text)
        self.assertIn("De-Claudification gate: required", text)


if __name__ == "__main__":
    unittest.main()
