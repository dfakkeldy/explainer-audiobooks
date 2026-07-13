from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "skill" / "scripts"))
from cover_spec import CoverSpecError, load_cover_spec

FONT_MANIFEST = Path(__file__).parents[1] / "skill" / "assets" / "fonts" / "manifest.json"
SCHEMA = Path(__file__).parents[1] / "skill" / "schemas" / "cover-spec-v1.schema.json"


def valid_payload() -> dict[str, object]:
    return {
        "schema_version": 2,
        "variant": "portrait",
        "candidate": {"id": "candidate-a", "direction_name": "Full Bleed Display"},
        "metadata": {
            "title": "Rodents in the Walls",
            "subtitle": "Squirrels and Other Houseguests",
            "author": "Dan Fakkeldy",
            "label": "AUDIOBOOK",
        },
        "canvas": {
            "width": 1600,
            "height": 2560,
            "background": "#132238",
            "safe_margin": 96,
        },
        "art": {
            "path": "art.svg",
            "mode": "bleed",
            "anchor": "center",
            "box": [0, 0, 1600, 2560],
            "opacity": 1,
            "blend_mode": "normal",
        },
        "layers": [
            {
                "kind": "text",
                "role": "label",
                "text": "AUDIOBOOK",
                "font_id": "geometric-sans",
                "box": [96, 110, 900, 70],
                "size": 36,
                "line_height": 44,
                "tracking": 8,
                "align": "left",
                "colour": "#EF5735",
                "opacity": 1,
                "rotation": 0,
                "baseline_shift": 0,
                "contrast_against": "#132238",
            },
            {
                "kind": "text",
                "role": "title",
                "title_order": 1,
                "text": "RODENTS",
                "font_id": "display-condensed",
                "box": [96, 220, 1408, 300],
                "size": 250,
                "line_height": 260,
                "tracking": 1,
                "align": "left",
                "colour": "#EF5735",
                "opacity": 1,
                "rotation": 0,
                "baseline_shift": 0,
                "contrast_against": "#132238",
            },
            {
                "kind": "text",
                "role": "title",
                "title_order": 2,
                "text": "IN THE WALLS",
                "font_id": "editorial-serif",
                "font_variation": {"wght": 780, "opsz": 96, "SOFT": 30, "WONK": 1},
                "box": [96, 510, 1408, 310],
                "size": 188,
                "line_height": 200,
                "tracking": 0,
                "align": "left",
                "colour": "#F6EDDA",
                "opacity": 1,
                "rotation": 0,
                "baseline_shift": 0,
                "contrast_against": "#132238",
            },
            {
                "kind": "text",
                "role": "subtitle",
                "text": "Squirrels and Other Houseguests",
                "font_id": "geometric-sans",
                "box": [96, 2100, 1408, 130],
                "size": 48,
                "line_height": 58,
                "tracking": 0,
                "align": "left",
                "colour": "#F6EDDA",
                "opacity": 1,
                "rotation": 0,
                "baseline_shift": 0,
                "contrast_against": "#132238",
            },
            {
                "kind": "text",
                "role": "author",
                "text": "Dan Fakkeldy",
                "font_id": "geometric-sans",
                "box": [96, 2320, 1408, 90],
                "size": 42,
                "line_height": 50,
                "tracking": 2,
                "align": "left",
                "colour": "#F6EDDA",
                "opacity": 1,
                "rotation": 0,
                "baseline_shift": 0,
                "contrast_against": "#132238",
            },
        ],
    }


def valid_square_payload() -> dict[str, object]:
    payload = valid_payload()
    payload["variant"] = "square"
    payload["canvas"].update(width=2400, height=2400, safe_margin=120)
    payload["art"]["box"] = [0, 0, 2400, 2400]
    for layer in payload["layers"]:
        layer["box"][0] = 120
    payload["layers"][0]["box"][1] = 120
    payload["layers"][3]["box"] = [120, 1950, 1408, 130]
    payload["layers"][4]["box"] = [120, 2150, 1408, 90]
    return payload


def write_fixture(root: Path, payload: object) -> Path:
    (root / "art.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 2560"><rect width="1600" height="2560" fill="#132238"/></svg>',
        encoding="utf-8",
    )
    path = root / "cover-spec.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


class CoverSpecValidationTests(unittest.TestCase):
    def test_loads_legacy_v1_as_portrait_without_mutating_source(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            payload = valid_payload()
            payload["schema_version"] = 1
            payload.pop("variant")
            path = write_fixture(Path(raw), payload)
            before = path.read_bytes()

            loaded = load_cover_spec(path, FONT_MANIFEST)

            self.assertEqual((loaded.variant, loaded.width, loaded.height), ("portrait", 1600, 2560))
            self.assertEqual(before, path.read_bytes())
            self.assertNotIn("variant", loaded.data)

    def test_v2_requires_explicit_known_variant(self) -> None:
        for variant in (None, "album"):
            with self.subTest(variant=variant), tempfile.TemporaryDirectory() as raw:
                payload = valid_payload()
                if variant is None:
                    payload.pop("variant")
                else:
                    payload["variant"] = variant
                with self.assertRaises(CoverSpecError):
                    load_cover_spec(write_fixture(Path(raw), payload), FONT_MANIFEST)

    def test_schema_matches_runtime_text_and_coordinate_constraints(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        text_layer = schema["$defs"]["text_layer"]
        role_rules = {
            rule.get("if", {}).get("properties", {}).get("role", {}).get("const"): rule.get("then", {})
            for rule in text_layer.get("allOf", [])
        }
        expected_role_rules = {
            "title": {
                "required": ["title_order"],
                "properties": {"size": {"minimum": 72}, "line_height": {"minimum": 72}},
            },
            "subtitle": {
                "properties": {"size": {"minimum": 36}, "line_height": {"minimum": 36}},
            },
        }
        for role, expected in expected_role_rules.items():
            with self.subTest(role=role):
                self.assertIn(role, role_rules)
                self.assertEqual(expected, role_rules[role])

        expected_x = {"type": "number", "minimum": -2400, "maximum": 4800}
        expected_y = {"type": "number", "minimum": -2560, "maximum": 5120}
        with self.subTest(definition="box"):
            self.assertEqual(
                [
                    expected_x,
                    expected_y,
                    {"type": "number", "minimum": 1, "maximum": 4800},
                    {"type": "number", "minimum": 1, "maximum": 5120},
                ],
                schema["$defs"]["box"]["prefixItems"],
            )
        with self.subTest(definition="point"):
            self.assertEqual([expected_x, expected_y], schema["$defs"]["point"]["prefixItems"])

    def test_accepts_exact_portrait_and_square_canvas(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            portrait = load_cover_spec(write_fixture(Path(raw), valid_payload()), FONT_MANIFEST)
            self.assertEqual(
                (portrait.variant, portrait.width, portrait.height),
                ("portrait", 1600, 2560),
            )

        with tempfile.TemporaryDirectory() as raw:
            square = load_cover_spec(write_fixture(Path(raw), valid_square_payload()), FONT_MANIFEST)
            self.assertEqual(
                (square.variant, square.width, square.height),
                ("square", 2400, 2400),
            )

    def test_rejects_unknown_variant_and_crossed_dimensions(self) -> None:
        for variant, width, height in [
            ("album", 2400, 2400),
            ("portrait", 2400, 2400),
            ("square", 1600, 2560),
        ]:
            with self.subTest(variant=variant, width=width, height=height):
                payload = valid_payload()
                payload["variant"] = variant
                payload["canvas"].update(width=width, height=height)
                with tempfile.TemporaryDirectory() as raw, self.assertRaises(CoverSpecError):
                    load_cover_spec(write_fixture(Path(raw), payload), FONT_MANIFEST)

    def test_square_may_omit_but_not_rewrite_subtitle(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            square = valid_square_payload()
            square["metadata"]["subtitle"] = ""
            square["layers"] = [
                layer for layer in square["layers"] if layer.get("role") != "subtitle"
            ]
            load_cover_spec(
                write_fixture(Path(raw), square),
                FONT_MANIFEST,
                canonical_subtitle="The exact canonical subtitle",
            )

        with tempfile.TemporaryDirectory() as raw:
            rewritten = valid_square_payload()
            rewritten["metadata"]["subtitle"] = "Shortened words"
            with self.assertRaisesRegex(CoverSpecError, "metadata subtitle"):
                load_cover_spec(
                    write_fixture(Path(raw), rewritten),
                    FONT_MANIFEST,
                    canonical_subtitle="The exact canonical subtitle",
                )

    def test_rejects_distinct_unicode_title_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            payload = valid_payload()
            payload["metadata"]["title"] = "Rodénts in the Walls"
            payload["layers"][1]["text"] = "RODÈNTS"
            with self.assertRaisesRegex(CoverSpecError, "title layers must reproduce canonical title"):
                load_cover_spec(write_fixture(Path(raw), payload), FONT_MANIFEST)

    def test_accepts_canonical_unicode_and_apostrophe_variants(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            payload = valid_payload()
            payload["metadata"]["title"] = "Rodént’s in the Walls"
            payload["layers"][1]["text"] = "RODE\u0301NT'S"
            try:
                spec = load_cover_spec(write_fixture(Path(raw), payload), FONT_MANIFEST)
            except CoverSpecError as error:
                self.fail(f"canonical Unicode/apostrophe variants were rejected: {error}")
            self.assertEqual("Rodént’s in the Walls", spec.metadata["title"])

    def test_loads_valid_spec_and_reconstructs_canonical_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            spec = load_cover_spec(write_fixture(Path(raw), valid_payload()), FONT_MANIFEST)
            self.assertEqual("Rodents in the Walls", spec.metadata["title"])
            self.assertEqual((1600, 2560), spec.dimensions)
            second = load_cover_spec(write_fixture(Path(raw), valid_payload()), FONT_MANIFEST)
            self.assertEqual(spec.spec_sha256, second.spec_sha256)
            self.assertEqual(64, len(spec.art_sha256))
            self.assertEqual(3, len(spec.fonts))

    def test_rejects_wrong_canvas_without_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            payload = valid_payload()
            payload["canvas"]["width"] = 1200
            with self.assertRaisesRegex(CoverSpecError, "canvas must be 1600x2560"):
                load_cover_spec(write_fixture(Path(raw), payload), FONT_MANIFEST)

    def test_rejects_title_token_omission(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            payload = valid_payload()
            payload["layers"][2]["text"] = "THE WALLS"
            with self.assertRaisesRegex(CoverSpecError, "title layers must reproduce canonical title"):
                load_cover_spec(write_fixture(Path(raw), payload), FONT_MANIFEST)

    def test_rejects_unknown_font_and_path_escape(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            payload = valid_payload()
            payload["layers"][1]["font_id"] = "system-georgia"
            with self.assertRaisesRegex(ValueError, "unknown font_id"):
                load_cover_spec(write_fixture(Path(raw), payload), FONT_MANIFEST)
            payload = valid_payload()
            payload["art"]["path"] = "../outside.png"
            with self.assertRaisesRegex(CoverSpecError, "art path escapes run folder"):
                load_cover_spec(write_fixture(Path(raw), payload), FONT_MANIFEST)

    def test_rejects_text_outside_safe_bounds_and_unbounded_effects(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            payload = valid_payload()
            payload["layers"][0]["box"] = [20, 110, 900, 70]
            with self.assertRaisesRegex(CoverSpecError, "outside 96px safe margin"):
                load_cover_spec(write_fixture(Path(raw), payload), FONT_MANIFEST)
            payload = valid_payload()
            payload["layers"][1]["shadow"] = {
                "colour": "#000000", "dx": 0, "dy": 80, "blur": 12, "opacity": 0.5
            }
            with self.assertRaisesRegex(CoverSpecError, "shadow dy must be between -48 and 48"):
                load_cover_spec(write_fixture(Path(raw), payload), FONT_MANIFEST)

    def test_rejects_run_text_or_axis_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            payload = valid_payload()
            payload["layers"][1]["runs"] = [{"text": "RODENT", "colour": "#EF5735"}]
            with self.assertRaisesRegex(CoverSpecError, "runs must concatenate to layer text"):
                load_cover_spec(write_fixture(Path(raw), payload), FONT_MANIFEST)
            payload = valid_payload()
            payload["layers"][2]["font_variation"]["wght"] = 950
            with self.assertRaisesRegex(CoverSpecError, "axis wght must be between 100 and 900"):
                load_cover_spec(write_fixture(Path(raw), payload), FONT_MANIFEST)

    def test_requires_declared_purpose_for_compositional_fields(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            payload = valid_payload()
            payload["layers"].insert(0, {
                "kind": "field",
                "box": [0, 0, 1600, 500],
                "fill": {"kind": "solid", "colour": "#EF5735"},
                "opacity": 1,
                "blend_mode": "normal"
            })
            with self.assertRaisesRegex(CoverSpecError, "field layer requires compositional purpose"):
                load_cover_spec(write_fixture(Path(raw), payload), FONT_MANIFEST)

    def test_rejects_unknown_layer_keys_and_unsupported_glyphs(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            payload = valid_payload()
            payload["layers"][1]["script"] = "alert(1)"
            with self.assertRaisesRegex(CoverSpecError, "unknown keys"):
                load_cover_spec(write_fixture(Path(raw), payload), FONT_MANIFEST)
            payload = valid_payload()
            payload["layers"][1]["text"] = "RODENTS☃"
            with self.assertRaisesRegex(CoverSpecError, "unsupported glyph"):
                load_cover_spec(write_fixture(Path(raw), payload), FONT_MANIFEST)

    def test_rejects_ascii_codepoint_absent_from_hash_pinned_face_before_rendering(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            payload = valid_payload()
            payload["layers"][1]["text"] = "RODENTS\u007f"
            with self.assertRaisesRegex(CoverSpecError, r"unsupported glyph U\+007F.*display-condensed"):
                load_cover_spec(write_fixture(Path(raw), payload), FONT_MANIFEST)

    def test_rejects_malformed_json_shapes_with_validation_errors(self) -> None:
        malformed_payloads: list[tuple[str, object]] = [("top-level", [])]

        candidate = valid_payload()
        candidate["candidate"] = {"id": 7, "direction_name": "Display"}
        malformed_payloads.append(("candidate id", candidate))

        metadata = valid_payload()
        metadata["metadata"] = []
        malformed_payloads.append(("metadata", metadata))

        canvas = valid_payload()
        canvas["canvas"] = "1600x2560"
        malformed_payloads.append(("canvas", canvas))

        art_path = valid_payload()
        art_path["art"]["path"] = 42
        malformed_payloads.append(("art path", art_path))

        invalid_art_path = valid_payload()
        invalid_art_path["art"]["path"] = "art\u0000.svg"
        malformed_payloads.append(("invalid art path", invalid_art_path))

        art_mode = valid_payload()
        art_mode["art"]["mode"] = []
        malformed_payloads.append(("art mode", art_mode))

        text_role = valid_payload()
        text_role["layers"][1]["role"] = []
        malformed_payloads.append(("text role", text_role))

        layer_kind = valid_payload()
        layer_kind["layers"][1]["kind"] = []
        malformed_payloads.append(("layer kind", layer_kind))

        font_variation = valid_payload()
        font_variation["layers"][2]["font_variation"] = []
        malformed_payloads.append(("font variation", font_variation))

        runs = valid_payload()
        runs["layers"][1]["runs"] = ["RODENTS"]
        malformed_payloads.append(("runs", runs))

        outline = valid_payload()
        outline["layers"][1]["outline"] = []
        malformed_payloads.append(("outline", outline))

        shadow = valid_payload()
        shadow["layers"][1]["shadow"] = []
        malformed_payloads.append(("shadow", shadow))

        for label, payload in malformed_payloads:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as raw:
                with self.assertRaises(CoverSpecError):
                    load_cover_spec(write_fixture(Path(raw), payload), FONT_MANIFEST)

    def test_rejects_boolean_version_and_numeric_values(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            payload = valid_payload()
            payload["schema_version"] = True
            with self.assertRaises(CoverSpecError):
                load_cover_spec(write_fixture(Path(raw), payload), FONT_MANIFEST)

            payload = valid_payload()
            payload["layers"][1]["size"] = True
            with self.assertRaises(CoverSpecError):
                load_cover_spec(write_fixture(Path(raw), payload), FONT_MANIFEST)

    def test_rejects_unknown_keys_inside_effects(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            payload = valid_payload()
            payload["layers"][1]["shadow"] = {
                "colour": "#000000",
                "dx": 0,
                "dy": 8,
                "blur": 12,
                "opacity": 0.5,
                "script": "alert(1)",
            }
            with self.assertRaisesRegex(CoverSpecError, "unknown keys"):
                load_cover_spec(write_fixture(Path(raw), payload), FONT_MANIFEST)

    def test_low_or_unverifiable_contrast_is_advisory(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            payload = valid_payload()
            payload["layers"][0]["colour"] = "#132238"
            payload["layers"][1].pop("contrast_against")
            spec = load_cover_spec(write_fixture(Path(raw), payload), FONT_MANIFEST)
            self.assertTrue(any("advisory contrast ratio" in warning for warning in spec.warnings))
            self.assertTrue(any("contrast is unverified" in warning for warning in spec.warnings))


if __name__ == "__main__":
    unittest.main()
