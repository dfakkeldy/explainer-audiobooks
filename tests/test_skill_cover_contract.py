from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
FILES = {
    "cover": ROOT / "skill" / "references" / "cover-art.md",
    "long": ROOT / "skill" / "SKILL.md",
    "custom": ROOT / "skills" / "custom-learning-audiobook" / "SKILL.md",
    "package": ROOT / "skills" / "custom-learning-audiobook" / "references" / "package-and-qc.md",
}


class SkillCoverContractTests(unittest.TestCase):
    def test_active_workflows_use_spec_selection_and_receipt_verification(self) -> None:
        text = "\n".join(path.read_text(encoding="utf-8") for path in FILES.values())
        for required in ("--spec", "cover-selection.json", "explicit-user-choice", "--cover-selection", "cover_receipts.py verify"):
            self.assertIn(required, text)

    def test_candidate_contract_varies_typography_as_well_as_art(self) -> None:
        for key in ("cover", "long", "custom", "package"):
            text = FILES[key].read_text(encoding="utf-8")
            self.assertIn("title strategy", text)
            self.assertIn("font", text)
            self.assertIn("line breaks", text)

    def test_active_commands_do_not_teach_the_legacy_template(self) -> None:
        for key in ("cover", "long", "custom", "package"):
            text = FILES[key].read_text(encoding="utf-8")
            self.assertNotIn("--layout bleed", text)
            self.assertNotIn("lower 25–35% reserved", text)
            self.assertNotIn("lower third carries the title", text)


if __name__ == "__main__":
    unittest.main()
