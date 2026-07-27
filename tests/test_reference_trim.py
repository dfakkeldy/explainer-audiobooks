from __future__ import annotations

import unittest
from pathlib import Path

REPO = Path(__file__).parents[1]
REFS = REPO / "skill" / "references"

SURVIVING = (
    "narration-style.md", "voice-design.md", "cover-art.md",
    "curriculum-patterns.md", "declaudification.md", "humanizer-pass.md",
    "frontier-manuscript-pipeline.md", "road-book-mode.md", "learning-design.md",
)

RETIRED_VOCABULARY = (
    "unattended-first-listen",
    "governed-final",
    "public-first-listen",
    "comprehension pilot",
    "learning receipt",
    "package-or-blocker",
)


class ReferenceTrimTests(unittest.TestCase):
    def test_surviving_references_exist(self) -> None:
        for name in SURVIVING:
            self.assertTrue((REFS / name).is_file(), f"missing reference: {name}")

    def test_retired_reference_and_templates_are_gone(self) -> None:
        self.assertFalse((REFS / "unattended-production.md").exists())
        self.assertFalse((REPO / "skill" / "templates" / "learning-design").exists())

    def test_surviving_references_drop_retired_vocabulary(self) -> None:
        for name in SURVIVING:
            text = (REFS / name).read_text(encoding="utf-8")
            for banned in RETIRED_VOCABULARY:
                self.assertNotIn(banned, text, f"{name} still teaches {banned!r}")

    def test_skill_only_cites_references_that_exist(self) -> None:
        skill = (REPO / "skill" / "SKILL.md").read_text(encoding="utf-8")
        for line in skill.splitlines():
            if "references/" in line and ".md" in line:
                for token in line.replace("`", " ").replace("(", " ").replace(")", " ").split():
                    if token.startswith("references/") and token.endswith(".md"):
                        self.assertTrue(
                            (REFS / token.split("/", 1)[1]).is_file(),
                            f"SKILL.md cites missing {token}",
                        )

    def test_learning_design_retains_the_teaching_and_blind_review_contracts(self) -> None:
        text = (REFS / "learning-design.md").read_text(encoding="utf-8").casefold()
        for marker in (
            "chapter teaching plan",
            "durable outcome",
            "prerequisites",
            "definition",
            "reason",
            "mechanism",
            "concrete case",
            "misconception",
            "expected ability",
            "blind sequential beginner review",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_road_book_retains_concept_and_working_memory_budgets(self) -> None:
        text = (REFS / "road-book-mode.md").read_text(encoding="utf-8").casefold()
        for marker in (
            "concept budget",
            "audio working-memory budget",
            "optional material",
            "main listen must remain complete",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
