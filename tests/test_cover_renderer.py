from __future__ import annotations

import json
import shutil
import struct
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parents[1] / "skill" / "scripts"))
import cover_renderer
from cover_renderer import CoverRenderError, render_cover_spec

FONT_MANIFEST = Path(__file__).parents[1] / "skill" / "assets" / "fonts" / "manifest.json"


def base_spec() -> dict[str, object]:
    metadata = {
        "title": "Rodents in the Walls",
        "subtitle": "A Field Guide",
        "author": "Dan Fakkeldy",
        "label": "AUDIOBOOK",
    }

    def text(
        role: str,
        value: str,
        order: int,
        y: int,
        size: int,
        font_id: str,
        colour: str,
    ) -> dict[str, object]:
        layer: dict[str, object] = {
            "kind": "text",
            "role": role,
            "text": value,
            "font_id": font_id,
            "box": [96, y, 1408, size + 70],
            "size": size,
            "line_height": size + 10,
            "tracking": 0,
            "align": "left",
            "colour": colour,
            "opacity": 1,
            "rotation": 0,
            "baseline_shift": 0,
            "contrast_against": "#132238",
        }
        if role == "title":
            layer["title_order"] = order
        return layer

    return {
        "schema_version": 1,
        "candidate": {"id": "full-bleed", "direction_name": "Full Bleed"},
        "metadata": metadata,
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
            text("label", "AUDIOBOOK", 0, 120, 32, "geometric-sans", "#EF5735"),
            text("title", "RODENTS", 1, 240, 220, "display-condensed", "#EF5735"),
            text("title", "IN THE WALLS", 2, 500, 150, "editorial-serif", "#F6EDDA"),
            text("subtitle", "A Field Guide", 0, 2100, 46, "geometric-sans", "#F6EDDA"),
            text("author", "Dan Fakkeldy", 0, 2320, 38, "geometric-sans", "#F6EDDA"),
        ],
    }


def write_spec(root: Path, payload: dict[str, object], name: str) -> Path:
    (root / "art.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 2560">'
        '<rect width="1600" height="2560" fill="#132238"/>'
        '<circle cx="800" cy="1500" r="440" fill="#274664"/></svg>',
        encoding="utf-8",
    )
    path = root / f"{name}.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


@unittest.skipUnless(
    shutil.which("rsvg-convert") and shutil.which("magick"),
    "renderer tools required",
)
class CoverRendererTests(unittest.TestCase):
    def test_renders_full_bleed_band_and_expressive_runs(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            variants = []
            plain = base_spec()
            variants.append(("full", plain))
            band = base_spec()
            band["candidate"] = {"id": "band", "direction_name": "Integrated Band"}
            band["layers"].insert(
                0,
                {
                    "kind": "field",
                    "box": [0, 120, 1600, 650],
                    "fill": {"kind": "solid", "colour": "#EF5735"},
                    "opacity": 0.92,
                    "blend_mode": "normal",
                    "purpose": "carry the title using the plaster accent from the art",
                },
            )
            variants.append(("band", band))
            expressive = base_spec()
            expressive["candidate"] = {
                "id": "expressive",
                "direction_name": "Shadow Branches",
            }
            expressive["layers"][1]["runs"] = [
                {
                    "text": "R",
                    "rotation": -4,
                    "baseline_shift": 12,
                    "colour": "#EF5735",
                },
                {
                    "text": "O",
                    "rotation": 2,
                    "baseline_shift": -8,
                    "colour": "#F6EDDA",
                },
                {
                    "text": "DENTS",
                    "rotation": -1,
                    "baseline_shift": 0,
                    "colour": "#EF5735",
                },
            ]
            variants.append(("expressive", expressive))
            for name, payload in variants:
                with self.subTest(name=name):
                    spec = write_spec(root, payload, name)
                    result = render_cover_spec(spec, root / f"{name}.png", FONT_MANIFEST)
                    header = result.output_path.read_bytes()[:29]
                    self.assertEqual(b"\x89PNG\r\n\x1a\n", header[:8])
                    self.assertEqual((1600, 2560), struct.unpack(">II", header[16:24]))
                    self.assertEqual(2, header[25])
                    thumbnail_header = result.thumbnail_path.read_bytes()[:29]
                    self.assertEqual(b"\x89PNG\r\n\x1a\n", thumbnail_header[:8])
                    self.assertEqual((160, 256), struct.unpack(">II", thumbnail_header[16:24]))
                    self.assertEqual(2, thumbnail_header[25])
                    self.assertTrue(result.receipt_path.is_file())

    def test_same_inputs_produce_identical_cover_and_receipt_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            spec = write_spec(root, base_spec(), "stable")
            first = render_cover_spec(spec, root / "first.png", FONT_MANIFEST)
            second = render_cover_spec(spec, root / "second.png", FONT_MANIFEST)
            self.assertEqual(first.cover_sha256, second.cover_sha256)
            first_receipt = json.loads(first.receipt_path.read_text(encoding="utf-8"))
            second_receipt = json.loads(second.receipt_path.read_text(encoding="utf-8"))
            for receipt in (first_receipt, second_receipt):
                receipt["output"] = "cover.png"
                receipt["thumbnail"] = "cover-thumbnail.png"
            self.assertEqual(first_receipt, second_receipt)

    def test_invalid_spec_leaves_no_partial_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            payload = base_spec()
            payload["canvas"]["width"] = 1200
            spec = write_spec(root, payload, "invalid")
            output = root / "invalid.png"
            with self.assertRaisesRegex(ValueError, "1600x2560"):
                render_cover_spec(spec, output, FONT_MANIFEST)
            self.assertFalse(output.exists())
            self.assertFalse((root / "invalid-thumbnail.png").exists())
            self.assertFalse((root / "invalid.render.json").exists())

    def test_rejects_output_outside_the_specification_run_folder(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            spec = write_spec(root, base_spec(), "safe")
            escaped = root.parent / f"{root.name}-escaped.png"
            try:
                with self.assertRaisesRegex(ValueError, "output path escapes"):
                    render_cover_spec(spec, escaped, FONT_MANIFEST)
                self.assertFalse(escaped.exists())
            finally:
                escaped.unlink(missing_ok=True)

    def test_render_failure_preserves_existing_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            spec = write_spec(root, base_spec(), "existing")
            output = root / "existing.png"
            thumbnail = root / "existing-thumbnail.png"
            receipt = root / "existing.render.json"
            output.write_bytes(b"existing cover")
            thumbnail.write_bytes(b"existing thumbnail")
            receipt.write_text("existing receipt\n", encoding="utf-8")

            with mock.patch.object(
                cover_renderer,
                "_render",
                side_effect=CoverRenderError("rasterizer failed"),
            ), self.assertRaisesRegex(CoverRenderError, "rasterizer failed"):
                render_cover_spec(spec, output, FONT_MANIFEST)

            self.assertEqual(b"existing cover", output.read_bytes())
            self.assertEqual(b"existing thumbnail", thumbnail.read_bytes())
            self.assertEqual("existing receipt\n", receipt.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
