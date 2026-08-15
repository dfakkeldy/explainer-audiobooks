from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
FILES = {
    "cover": ROOT / "skill" / "references" / "cover-art.md",
    "skill": ROOT / "skill" / "SKILL.md",
    "publishing": ROOT / "skill" / "references" / "publishing-a-public-edition.md",
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

    def test_private_skill_renders_pairs_without_public_publishing_tools(self) -> None:
        text = FILES["skill"].read_text(encoding="utf-8")
        for marker in (
            "exactly three",
            "render_cover_pair(",
            "1600×2560",
            "cover.png",
            "2400×2400",
            "m4b-cover.png",
            "subject specificity",
            "thumbnail legibility",
            "portrait/square coherence",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)
        for parked in (
            "cover_receipts.py",
            "sync_selected_cover.py",
            "verify_public_first_listen.py",
        ):
            with self.subTest(parked=parked):
                self.assertNotIn(parked, text)

    def test_public_runbook_orders_selection_build_verify_and_sync(self) -> None:
        text = FILES["publishing"].read_text(encoding="utf-8")
        self.assert_in_order(
            text,
            (
                "select-pair",
                "build_book.py",
                "cover_receipts.py verify",
                "Dry-run first",
                "sync_selected_cover.py",
                "--apply",
            ),
        )
        self.assertNotIn("cp <build>/dist/<Output-Filename-Base>.epub", text)

    def test_candidate_contract_varies_typography_as_well_as_art(self) -> None:
        text = FILES["cover"].read_text(encoding="utf-8")
        self.assertIn("title strategy", text)
        self.assertIn("font", text)
        self.assertIn("line breaks", text)

    def test_active_commands_do_not_teach_the_legacy_template(self) -> None:
        for key in ("cover", "skill"):
            text = FILES[key].read_text(encoding="utf-8")
            self.assertNotIn("--layout bleed", text)
            self.assertNotIn("lower 25–35% reserved", text)
            self.assertNotIn("lower third carries the title", text)
            self.assertNotIn("/make_cover.py \\\n  --spec", text)

    def test_active_surfaces_teach_the_paired_rendering_contract(self) -> None:
        required = (
            "exactly three",
            "1600×2560",
            "cover.png",
            "2400×2400",
            "m4b-cover.png",
        )
        for key in ("cover", "skill", "public", "readme", "make"):
            text = FILES[key].read_text(encoding="utf-8")
            for marker in required:
                with self.subTest(file=key, marker=marker):
                    self.assertIn(marker, text)

    def test_docs_distinguish_private_default_from_public_promotion(self) -> None:
        for key in ("readme", "make"):
            text = FILES[key].read_text(encoding="utf-8")
            self.assertIn("auto-select", text)
            self.assertIn("private", text)
            self.assertIn("publishing-a-public-edition.md", text)
            self.assertNotIn("The human\nmakes the explicit pair selection", text)
        public = FILES["public"].read_text(encoding="utf-8")
        self.assertIn("public/iCloud/site sync", public)
        combined = "\n".join(
            FILES[key].read_text(encoding="utf-8")
            for key in ("public", "readme", "make")
        )
        self.assertIn("five-book migration", combined)
        self.assertIn("not a universal future rule", combined)

    def test_private_icloud_copy_requires_an_explicit_user_request(self) -> None:
        text = FILES["publishing"].read_text(encoding="utf-8")
        self.assertIn(
            "only when the user explicitly requests it, a private iCloud\n"
            "reading copy",
            text,
        )

    def test_public_runbook_uses_complete_paired_interfaces(self) -> None:
        text = FILES["publishing"].read_text(encoding="utf-8")
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
            '--out "$PAIR/cover-selection.json"',
            '--selection "$PAIR/cover-selection.json"',
            '--m4b-cover "$PAIR/m4b-cover.png"',
            '--paired-artifact-dir "$PAIR"',
            "--public-destination",
            "echo_pronunciation_narrate.sh",
            "--intent reuse",
            "--apply",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)
        self.assertIn("publishing-a-public-edition.md", FILES["cover"].read_text(encoding="utf-8"))

    def test_legacy_mutation_is_confined_to_public_compatibility_runbook(self) -> None:
        publishing = FILES["publishing"].read_text(encoding="utf-8")
        self.assertIn("replace_m4b_cover.py", publishing)
        self.assertIn("legacy artifacts only", publishing)
        self.assertNotIn("replace_m4b_cover.py", FILES["skill"].read_text(encoding="utf-8"))
        self.assertNotIn('--portrait-cover "$PAIR/cover.png"', publishing)

    def test_public_method_uses_wrapper_embedding_not_post_echo_replacement(self) -> None:
        text = FILES["public"].read_text(encoding="utf-8")
        self.assertIn("governed Echo wrapper embeds", text)
        self.assertIn("legacy artifacts only", text)
        self.assertNotIn("square-art replacement preserves", text)

    def flattened(self, key: str) -> str:
        return " ".join(FILES[key].read_text(encoding="utf-8").split())

    def test_route_parity_and_flat_graphic_slot(self) -> None:
        text = self.flattened("cover")
        for marker in (
            "Designed flat graphic",
            "route follows the direction",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)
        for key in FILES:
            text = self.flattened(key)
            for stale in (
                "generated raster art is mandatory",
                "Never choose SVG merely",
                "approved vector fallback",
                "Do not use SVG or programmatic vector artwork",
                "Do not substitute bespoke SVG",
                "flat graphic or type-led direction",
            ):
                with self.subTest(file=key, stale=stale):
                    self.assertNotIn(stale, text)

    def test_candidate_slate_biases_high_key_and_requires_flat_graphic(self) -> None:
        for key in ("cover", "skill"):
            text = self.flattened(key)
            for marker in (
                "At least two of the three complete pairs must be intentionally high-key",
                "one of those high-key pairs must be a Designed flat graphic",
                "The third candidate is tonally unrestricted",
            ):
                with self.subTest(file=key, marker=marker):
                    self.assertIn(marker, text)

    def test_high_key_is_a_reviewed_visual_contract_not_a_label(self) -> None:
        text = self.flattened("cover")
        for marker in (
            "High-key means that the overall impression is luminous and open",
            "does not mean white-only, pastel, washed out, low-contrast",
            "`high-key` or `tonally unrestricted`",
            "both its portrait and square renders",
            "revised or regenerated",
            "[TONAL INTENT: HIGH-KEY / TONALLY UNRESTRICTED]",
            "High-key treatment is the tie-breaker",
            "darker direction earned the choice",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_raster_prompt_bans_ai_render_tells(self) -> None:
        text = self.flattened("cover")
        for marker in (
            "airbrushed radial glow",
            "winding road or river",
            "hyper-smooth 3D product render",
            "melted or smeared detail",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)
        for stale in ("cinematic editorial photograph", "painterly realism"):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, text)


if __name__ == "__main__":
    unittest.main()
