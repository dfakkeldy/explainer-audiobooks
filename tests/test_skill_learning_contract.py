from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]


class SkillLearningContractTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_shared_reference_defines_separate_verdicts_and_structured_records(self) -> None:
        path = ROOT / "skill" / "references" / "learning-design.md"
        self.assertTrue(path.is_file())
        text = path.read_text(encoding="utf-8").lower()
        for phrase in (
            "learning-brief.json",
            "learning-outline.json",
            "chapter-plans.json",
            "coverage-ledger.json",
            "continuity.json",
            "learning-review.json",
            "curriculum and orientation",
            "chapter teaching",
            "structural and beginner-reader",
            "prose style",
            "packaging and acoustic",
            "cannot substitute",
            "retroactive",
            "learning_design_qc.py",
            "learning-design-receipt.json",
        ):
            self.assertIn(phrase, text)

    def test_production_skills_require_both_independent_receipts(self) -> None:
        for relative in ("skill/SKILL.md", "skills/custom-learning-audiobook/SKILL.md"):
            with self.subTest(relative=relative):
                text = self.read(relative)
                self.assertIn("references/learning-design.md", text)
                self.assertIn("learning_design_qc.py", text)
                self.assertIn("--learning-receipt", text)
                self.assertIn("--prose-receipt", text)
                self.assertIn("legacy-without-learning-receipt", text)
                self.assertIn("new or revised", text)

    def test_supporting_references_use_the_same_learning_evidence(self) -> None:
        for relative in (
            "skill/references/frontier-manuscript-pipeline.md",
            "skill/references/narration-style.md",
            "skills/custom-learning-audiobook/references/intake-and-research.md",
            "skills/custom-learning-audiobook/references/package-and-qc.md",
        ):
            with self.subTest(relative=relative):
                text = self.read(relative)
                self.assertIn("learning-design", text)
                self.assertIn("chapter-plans.json", text)
                self.assertIn("learning-review.json", text)

    def test_shared_contract_requires_orientation_and_complete_explanation_paths(self) -> None:
        text = self.read("skill/references/learning-design.md")
        for phrase in (
            "openingOrientation",
            "priorKnowledge",
            "knowledgeDelta",
            "definition",
            "reason",
            "mechanism",
            "concreteCase",
            "boundary",
            "misconception",
            "expectedAbility",
            "reviewedChapterSHA256",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
