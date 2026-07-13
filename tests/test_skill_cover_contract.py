from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
FILES = {
    "cover": ROOT / "skill" / "references" / "cover-art.md",
    "long": ROOT / "skill" / "SKILL.md",
    "custom": ROOT / "skills" / "custom-learning-audiobook" / "SKILL.md",
    "package": ROOT / "skills" / "custom-learning-audiobook" / "references" / "package-and-qc.md",
    "public": ROOT / "docs" / "how-these-were-made.md",
    "readme": ROOT / "README.md",
    "make": ROOT / "docs" / "make-your-own.md",
}


class SkillCoverContractTests(unittest.TestCase):
    def assert_in_order(self, text: str, markers: tuple[str, ...]) -> None:
        cursor = 0
        for marker in markers:
            position = text.find(marker, cursor)
            self.assertNotEqual(-1, position, f"missing or out-of-order marker: {marker}")
            cursor = position + len(marker)

    def test_each_active_skill_uses_the_complete_governed_workflow(self) -> None:
        for key in ("long", "custom"):
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
                "cover_receipts.py select",
                "/usr/local/bin/python3 skill/scripts/build_book.py",
                "Native Echo/Kokoro M4B",
                "/usr/local/bin/python3 skill/scripts/cover_receipts.py verify",
                "--m4b",
                "/usr/local/bin/python3 skill/scripts/sync_selected_cover.py",
                "--apply",
            ),
        )
        self.assertGreaterEqual(
            text.count("/usr/local/bin/python3 skill/scripts/sync_selected_cover.py"),
            2,
        )
        self.assertNotIn("cp <build>/dist/<Output-Filename-Base>.epub", text)

    def test_custom_skill_finishes_manuscript_before_build_and_audio(self) -> None:
        text = FILES["custom"].read_text(encoding="utf-8")
        self.assert_in_order(
            text,
            (
                "**Humanize and complete prose QC before packaging.**",
                "**Build the governed EPUB.**",
                "**Render native Echo audio.**",
                "/usr/local/bin/python3 skill/scripts/cover_receipts.py verify",
                "--m4b",
                "**Package and copy.**",
            ),
        )

    def test_package_reference_orders_prose_build_audio_verify_and_copy(self) -> None:
        text = FILES["package"].read_text(encoding="utf-8")
        self.assert_in_order(
            text,
            (
                "## Prose QC",
                "## EPUB And Markdown",
                "## Echo M4B And Alignment",
                "## Final Cover Receipt Verification",
                "--m4b",
                "## Copy Rules",
            ),
        )

    def test_public_repo_delivery_uses_governed_sync(self) -> None:
        text = FILES["package"].read_text(encoding="utf-8")
        self.assertIn("--public-destination", text)
        for forbidden in (
            'cp "$DIST/$SLUG.epub"',
            'cp "$DIST/cover-$SELECTED.png"',
        ):
            self.assertNotIn(forbidden, text)

    def test_private_icloud_copy_requires_an_explicit_user_request(self) -> None:
        required = (
            "Private or sensitive packages stay in the agreed private project "
            "folder and receive an iCloud Books reading copy only on an explicit "
            "user request."
        )
        forbidden = (
            "default listening/delivery surface for public-safe and private books",
            "public-safe and private books unless the user explicitly says not",
            "always create a complete icloud drive delivery folder for finished packages unless",
            "copy the complete package to the icloud drive `books/<title>/` delivery folder by default",
        )
        for key in ("custom", "package"):
            text = " ".join(FILES[key].read_text(encoding="utf-8").split())
            self.assertIn(required, text)
            for old_wording in forbidden:
                self.assertNotIn(old_wording, text.casefold())

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
        for key in ("cover", "long", "custom", "package", "public", "readme", "make"):
            text = FILES[key].read_text(encoding="utf-8")
            for marker in required:
                with self.subTest(file=key, marker=marker):
                    self.assertIn(marker, text)

    def test_active_skills_teach_paired_commands_not_new_single_cover_selection(self) -> None:
        for key in ("long", "custom", "package"):
            text = FILES[key].read_text(encoding="utf-8")
            for marker in ("cover_pairs.py", "select-pair", "--m4b-cover", "replace_m4b_cover.py", "--paired-artifact-dir"):
                with self.subTest(file=key, marker=marker):
                    self.assertIn(marker, text)
            self.assertIn("verification-only compatibility", text)

    def test_public_docs_state_governed_sync_boundaries_and_migration_scope(self) -> None:
        for key in ("public", "readme", "make"):
            text = FILES[key].read_text(encoding="utf-8")
            self.assertIn("public/iCloud/site sync", text)
            self.assertIn("private", text)
        combined = "\n".join(FILES[key].read_text(encoding="utf-8") for key in ("long", "custom", "package", "public", "readme", "make"))
        self.assertIn("five-book migration", combined)
        self.assertIn("not a universal future rule", combined)

    def test_active_new_work_uses_complete_paired_interfaces(self) -> None:
        for key in ("long", "custom", "package", "cover"):
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
                "--selection \"$DIST/cover-selection.json\"",
                "--m4b-cover \"$PAIR/m4b-cover.png\"",
                "--portrait-cover \"$PAIR/cover.png\"",
                "--paired-artifact-dir \"$PAIR\"",
                "--intent reuse",
                "--apply",
            ):
                with self.subTest(file=key, marker=marker):
                    self.assertIn(marker, text)

    def test_active_new_work_does_not_run_single_cover_renderer(self) -> None:
        for key in ("long", "custom", "package", "cover"):
            text = FILES[key].read_text(encoding="utf-8")
            self.assertNotIn("/make_cover.py \\\n  --spec", text)

    def test_active_paired_selection_uses_current_cli_vocabulary(self) -> None:
        legacy_markers = {
            "custom": "The older command below is verification-only compatibility",
            "package": "The following single-cover commands are verification-only compatibility",
        }
        for key, legacy_marker in legacy_markers.items():
            text = FILES[key].read_text(encoding="utf-8")
            active_text = text.split(legacy_marker, 1)[0]
            self.assertIn("selection_source=user", active_text)
            self.assertNotIn("selection_source=explicit-user-choice", active_text)

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
        for key in ("long", "custom", "package", "cover", "public", "readme", "make"):
            with self.subTest(file=key):
                normalized = " ".join(FILES[key].read_text(encoding="utf-8").split())
                self.assert_in_order(normalized, markers)


if __name__ == "__main__":
    unittest.main()
