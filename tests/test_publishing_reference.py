from __future__ import annotations

import unittest
from pathlib import Path

REPO = Path(__file__).parents[1]
DOC = REPO / "skill" / "references" / "publishing-a-public-edition.md"
SCRIPTS = REPO / "skill" / "scripts"


class PublishingReferenceTests(unittest.TestCase):
    def test_parked_scripts_still_exist(self) -> None:
        for name in (
            "cover_receipts.py",
            "sync_selected_cover.py",
            "verify_public_first_listen.py",
            "replace_m4b_cover.py",
        ):
            self.assertTrue((SCRIPTS / name).is_file(), f"parked script missing: {name}")

    def test_reference_exists_and_covers_the_parked_flow(self) -> None:
        text = DOC.read_text(encoding="utf-8")
        for needle in (
            "cover_receipts.py",
            "select-pair",
            "--selection-source user",
            "--privacy-classification",
            "--permission-to-publish",
            "sync_selected_cover.py",
            "--intent reuse",
            "--apply",
            "verify_public_first_listen.py",
        ):
            self.assertIn(needle, text, f"publishing reference missing {needle!r}")

    def test_reference_states_it_is_not_the_private_lane(self) -> None:
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("not used when making a book for yourself", text)

    def test_cover_art_points_here(self) -> None:
        cover_art = (REPO / "skill" / "references" / "cover-art.md").read_text(encoding="utf-8")
        self.assertIn("publishing-a-public-edition.md", cover_art)

    def test_skill_does_not_route_the_private_lane_through_publishing(self) -> None:
        skill = (REPO / "skill" / "SKILL.md").read_text(encoding="utf-8")
        for banned in ("sync_selected_cover.py", "cover_receipts.py", "verify_public_first_listen.py"):
            self.assertNotIn(banned, skill, f"SKILL.md still routes through {banned}")


if __name__ == "__main__":
    unittest.main()
