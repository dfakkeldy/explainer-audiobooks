from __future__ import annotations

import json
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

    def test_production_skills_plan_listener_pronunciation_before_full_audio(
        self,
    ) -> None:
        for relative in (
            "skill/SKILL.md",
            "skills/custom-learning-audiobook/SKILL.md",
            "skills/custom-learning-audiobook/references/intake-and-research.md",
            "skills/custom-learning-audiobook/references/package-and-qc.md",
            "skills/longform-book-development/SKILL.md",
            "skills/longform-book-development/references/handoff-packet.md",
        ):
            with self.subTest(relative=relative):
                text = self.read(relative)
                self.assertIn("pronunciation-plan.json", text)
                self.assertIn("listener", text.lower())

        package = self.read(
            "skills/custom-learning-audiobook/references/package-and-qc.md"
        )
        self.assertIn("build_pronunciation_probe_reel.py", package)
        self.assertIn("pronunciation_plan_qc.py", package)

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

    def test_curriculum_pattern_is_selected_and_preserved(self) -> None:
        reference = self.read("skill/references/curriculum-patterns.md").lower()
        for phrase in (
            "mechanism-first spiral",
            "end-to-end trace",
            "problem progression",
            "terminology inventory",
            "curriculumpattern",
            "fitevidence",
        ):
            self.assertIn(phrase, reference)
        for relative in (
            "skill/SKILL.md",
            "skills/custom-learning-audiobook/SKILL.md",
            "skills/longform-book-development/SKILL.md",
            "skills/longform-book-development/references/handoff-packet.md",
        ):
            with self.subTest(relative=relative):
                self.assertIn("curriculum-patterns.md", self.read(relative))

    def test_learning_templates_cover_every_required_record(self) -> None:
        root = ROOT / "skill" / "templates" / "learning-design"
        expected = {
            "learning-brief.json",
            "learning-outline.json",
            "chapter-plans.json",
            "coverage-ledger.json",
            "continuity.json",
            "learning-review.json",
        }
        self.assertEqual(expected, {path.name for path in root.glob("*.json")})
        for name in expected:
            with self.subTest(name=name):
                payload = json.loads((root / name).read_text(encoding="utf-8"))
                self.assertEqual(1, payload["schemaVersion"])

        review = json.loads((root / "learning-review.json").read_text(encoding="utf-8"))
        self.assertEqual({}, review["reviewedChapterSHA256"])
        self.assertEqual("pending", review["structure"]["verdict"])
        self.assertEqual("pending", review["beginnerReader"]["verdict"])

    def test_longform_handoff_cannot_advance_without_learning_architecture(self) -> None:
        skill = self.read("skills/longform-book-development/SKILL.md")
        handoff = self.read("skills/longform-book-development/references/handoff-packet.md")
        for phrase in (
            "learning-design.md",
            "opening orientation",
            "prior knowledge",
            "target history",
            "prerequisites",
            "knowledge delta",
            "explanation path",
            "development draft",
            "canonical production",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, skill + "\n" + handoff)

    def test_humanizer_reports_learning_defects_instead_of_smoothing_them(self) -> None:
        text = self.read("skill/references/humanizer-pass.md")
        for phrase in (
            "cannot certify pedagogy",
            "structural blocker",
            "missing orientation",
            "chapter-order",
            "unexplained terms",
            "shallow mechanisms",
            "missing worked examples",
            "return to learning review",
            "whole-book acceptance",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
