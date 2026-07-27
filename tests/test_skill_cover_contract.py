from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
FILES = {
    "cover": ROOT / "skill" / "references" / "cover-art.md",
    "long": ROOT / "skill" / "SKILL.md",
    "unattended": ROOT / "skill" / "references" / "unattended-production.md",
    "public": ROOT / "docs" / "how-these-were-made.md",
    "readme": ROOT / "README.md",
    "make": ROOT / "docs" / "make-your-own.md",
}


class SkillCoverContractTests(unittest.TestCase):
    def assert_in_order(self, text: str, markers: tuple[str, ...]) -> None:
        cursor = 0
        for marker in markers:
            position = text.find(marker, cursor)
            self.assertNotEqual(
                -1, position, f"missing or out-of-order marker: {marker}"
            )
            cursor = position + len(marker)

    def test_each_active_skill_uses_the_complete_governed_workflow(self) -> None:
        for key in ("long",):
            text = FILES[key].read_text(encoding="utf-8")
            for required in (
                "render_cover_pair(",
                "cover-selection.json",
                "--selection-source user",
                "--cover-selection",
                "Echo/Kokoro",
                "cover_receipts.py verify",
                "--m4b",
                "sync_selected_cover.py",
                "dry run",
                "--apply",
            ):
                with self.subTest(skill=key, required=required):
                    self.assertIn(required, text)

    def test_long_skill_orders_selection_build_audio_verify_and_delivery(self) -> None:
        text = FILES["long"].read_text(encoding="utf-8")
        self.assert_in_order(
            text,
            (
                "select-pair",
                "build_book.py --cover ... --m4b-cover ... --cover-selection ...",
                "Native Echo/Kokoro M4B",
                "cover_receipts.py verify",
                "sync_selected_cover.py",
                "--apply",
            ),
        )
        self.assertNotIn("cp <build>/dist/<Output-Filename-Base>.epub", text)

    def test_public_method_states_governed_chronology(self) -> None:
        text = FILES["public"].read_text(encoding="utf-8")
        self.assert_in_order(
            text,
            (
                "explicit pair selection",
                "paired receipt",
                "EPUB portrait",
                "M4B square",
                "post-embed verification",
                "sync",
            ),
        )

    def test_candidate_contract_varies_typography_as_well_as_art(self) -> None:
        for key in ("cover", "long"):
            text = FILES[key].read_text(encoding="utf-8")
            self.assertIn("title strategy", text)
            self.assertIn("font", text)
            self.assertIn("line breaks", text)

    def test_active_commands_do_not_teach_the_legacy_template(self) -> None:
        for key in ("cover", "long"):
            text = FILES[key].read_text(encoding="utf-8")
            self.assertNotIn("--layout bleed", text)
            self.assertNotIn("lower 25–35% reserved", text)
            self.assertNotIn("lower third carries the title", text)

    def test_active_surfaces_teach_the_universal_paired_cover_contract(self) -> None:
        required = (
            "exactly three",
            "1600×2560",
            "cover.png",
            "2400×2400",
            "m4b-cover.png",
            "explicit pair selection",
            "paired receipt",
            "EPUB portrait",
            "M4B square",
            "post-embed verification",
        )
        for key in ("cover", "long", "public", "readme", "make"):
            text = FILES[key].read_text(encoding="utf-8")
            for marker in required:
                with self.subTest(file=key, marker=marker):
                    self.assertIn(marker, text)

    def test_active_skills_teach_paired_commands_not_new_single_cover_selection(
        self,
    ) -> None:
        for key in ("long",):
            text = FILES[key].read_text(encoding="utf-8")
            for marker in (
                "cover_pairs.py",
                "select-pair",
                "--m4b-cover",
                "replace_m4b_cover.py",
                "--paired-artifact-dir",
            ):
                with self.subTest(file=key, marker=marker):
                    self.assertIn(marker, text)
            self.assertIn("verification-only compatibility", text)

    def test_public_docs_state_governed_sync_boundaries_and_migration_scope(
        self,
    ) -> None:
        for key in ("public", "readme", "make"):
            text = FILES[key].read_text(encoding="utf-8")
            self.assertIn("public/iCloud/site sync", text)
            self.assertIn("private", text)
        combined = "\n".join(
            FILES[key].read_text(encoding="utf-8")
            for key in ("long", "public", "readme", "make")
        )
        self.assertIn("five-book migration", combined)
        self.assertIn("not a universal future rule", combined)

    def test_private_icloud_copy_requires_an_explicit_user_request(self) -> None:
        text = FILES["unattended"].read_text(encoding="utf-8")
        self.assertIn(
            "only when the user explicitly requests it, a private iCloud\n"
            "reading copy",
            text,
        )

    def test_active_new_work_uses_complete_paired_interfaces(self) -> None:
        # The full copy-paste command sequence lives in exactly one normative
        # reference ("cover", for the explainer-audiobook skill). The skill
        # body carries only the contract summary plus a pointer — duplicated
        # command blocks drift.
        for key in ("cover",):
            text = FILES[key].read_text(encoding="utf-8")
            for marker in (
                "render_cover_pair(",
                "portrait_spec=",
                "square_spec=",
                "portrait_output=",
                "square_output=",
                "portrait_thumbnail=",
                "square_thumbnail=",
                "portrait_receipt=",
                "square_receipt=",
                "--portrait-render-receipt",
                "--square-render-receipt",
                "--privacy-classification",
                "--selection-source user",
                '--selection "$DIST/cover-selection.json"',
                '--m4b-cover "$PAIR/m4b-cover.png"',
                '--paired-artifact-dir "$PAIR"',
                "--intent reuse",
                "--apply",
            ):
                with self.subTest(file=key, marker=marker):
                    self.assertIn(marker, text)

        for key, pointer in (("long", "references/cover-art.md"),):
            text = FILES[key].read_text(encoding="utf-8")
            self.assertIn("Complete paired command example", text)
            self.assertIn(pointer, text)

        # The narration wrapper embeds the square cover itself; mutating a
        # narrated M4B invalidates the pronunciation audit. Every active
        # surface states the rule and none teaches the old mutation flow.
        for key in ("long", "cover"):
            text = FILES[key].read_text(encoding="utf-8")
            self.assertIn("Never run `replace_m4b_cover.py`", text)
            self.assertNotIn('--portrait-cover "$PAIR/cover.png"', text)

    def test_active_new_work_does_not_run_single_cover_renderer(self) -> None:
        for key in ("long", "cover"):
            text = FILES[key].read_text(encoding="utf-8")
            self.assertNotIn("/make_cover.py \\\n  --spec", text)

    def test_delegated_public_cover_choice_is_distinct_from_autoselection(self) -> None:
        for key in ("cover",):
            with self.subTest(file=key):
                text = FILES[key].read_text(encoding="utf-8")
                self.assertIn("delegated-editorial-choice", text)
                self.assertIn("editorial-autoselection", text)
                self.assertIn("explicitly delegates", text)

    def test_paired_chronology_is_literal_and_ordered(self) -> None:
        markers = (
            "research → three source directions",
            "portrait/square render pairs",
            "thumbnail review",
            "explicit pair selection",
            "paired receipt",
            "EPUB portrait + M4B square embedding",
            "post-embed verification",
            "governed public/iCloud/site sync",
        )
        for key in ("long", "cover", "public", "readme", "make"):
            with self.subTest(file=key):
                normalized = " ".join(FILES[key].read_text(encoding="utf-8").split())
                self.assert_in_order(normalized, markers)


if __name__ == "__main__":
    unittest.main()
