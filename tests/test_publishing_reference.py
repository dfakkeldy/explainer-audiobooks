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
            '--out "$PAIR/cover-selection.json"',
            '--selection "$PAIR/cover-selection.json"',
            "sync_selected_cover.py",
            "--public-destination",
            "--intent reuse",
            "--apply",
            "echo_pronunciation_narrate.sh",
            "verify_public_first_listen.py",
        ):
            self.assertIn(needle, text, f"publishing reference missing {needle!r}")

    def test_changed_square_requires_governed_renarration_before_verification(self) -> None:
        text = DOC.read_text(encoding="utf-8")
        changed_pair = text.index("If the selected square cover changed")
        wrapper = text.index("echo_pronunciation_narrate.sh", changed_pair)
        accepted_selector = text.index("echo-render-current-accepted.json", wrapper)
        verify = text.index("cover_receipts.py verify", accepted_selector)
        self.assertLess(changed_pair, wrapper)
        self.assertLess(wrapper, accepted_selector)
        self.assertLess(accepted_selector, verify)
        self.assertIn("Do not reuse an M4B rendered with different square art", text)

    def test_both_public_sync_commands_use_the_pair_receipt_and_permission_gate(self) -> None:
        text = DOC.read_text(encoding="utf-8")
        shell_blocks = text.split("```bash\n")[1:]
        sync_blocks = [
            block.split("```", 1)[0]
            for block in shell_blocks
            if "sync_selected_cover.py" in block.split("```", 1)[0]
        ]
        self.assertEqual(2, len(sync_blocks))
        for block in sync_blocks:
            with self.subTest(block=block):
                self.assertIn('--selection "$PAIR/cover-selection.json"', block)
                self.assertIn('--paired-artifact-dir "$PAIR"', block)
                self.assertIn("--public-destination", block)
        self.assertNotIn('$DIST/cover-selection.json', text)

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
