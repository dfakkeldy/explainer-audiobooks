from __future__ import annotations

import json
import os
import shutil
import stat
import struct
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parents[1] / "skill" / "scripts"))
import cover_renderer
from cover_renderer import CoverRenderError, render_cover_spec
from PIL import Image

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
    def test_renders_square_cover_thumbnail_and_receipt_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            payload = base_spec()
            payload["schema_version"] = 2
            payload["variant"] = "square"
            payload["canvas"].update(width=2400, height=2400, safe_margin=120)
            payload["art"]["box"] = [0, 0, 2400, 2400]
            for layer in payload["layers"]:
                layer["box"][0] = 120
            payload["layers"][0]["box"][1] = 120
            payload["layers"][3]["box"] = [120, 1950, 1408, 130]
            payload["layers"][4]["box"] = [120, 2150, 1408, 90]
            spec = write_spec(root, payload, "square")
            cover = root / "square.png"
            thumbnail = root / "square-thumbnail.png"
            receipt = root / "square.render.json"

            result = render_cover_spec(
                spec, cover, thumbnail, receipt, FONT_MANIFEST
            )

            with Image.open(cover) as image:
                self.assertEqual((image.mode, image.size), ("RGB", (2400, 2400)))
            with Image.open(thumbnail) as image:
                self.assertEqual((image.mode, image.size), ("RGB", (160, 160)))
            self.assertEqual(result.variant, "square")
            payload = json.loads(receipt.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema_version"], 1)
            self.assertEqual(payload["variant"], "square")
            self.assertEqual(payload["dimensions"], [2400, 2400])
            self.assertEqual(payload["thumbnail_dimensions"], [160, 160])

    def test_pinned_title_fonts_render_distinct_pixels(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            cover_hashes: set[str] = set()
            font_ids = (
                "display-condensed",
                "editorial-serif",
                "geometric-sans",
            )

            for font_id in font_ids:
                payload = base_spec()
                for layer in payload["layers"]:
                    if layer["role"] == "title":
                        layer["font_id"] = font_id
                spec = write_spec(root, payload, font_id)
                result = render_cover_spec(
                    spec,
                    root / f"{font_id}.png",
                    FONT_MANIFEST,
                )
                cover_hashes.add(result.cover_sha256)

            self.assertEqual(len(font_ids), len(cover_hashes))

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


class CoverRendererSafetyTests(unittest.TestCase):
    def assert_input_alias_rejected(
        self,
        spec: Path,
        output: Path,
        protected_sources: tuple[Path, ...],
        manifest: Path = FONT_MANIFEST,
    ) -> None:
        snapshots = {
            source: (stat.S_IFMT(source.lstat().st_mode), source.read_bytes())
            for source in protected_sources
        }
        with mock.patch.object(
            cover_renderer,
            "_render",
            side_effect=AssertionError("rendering began before alias rejection"),
        ) as render, self.assertRaisesRegex(
            CoverRenderError,
            "artifact path aliases renderer input",
        ):
            render_cover_spec(spec, output, manifest)
        render.assert_not_called()
        for source, (file_type, payload) in snapshots.items():
            self.assertEqual(file_type, stat.S_IFMT(source.lstat().st_mode))
            self.assertEqual(payload, source.read_bytes())

    def test_rejects_output_aliasing_spec_before_render(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw).resolve()
            spec = write_spec(root, base_spec(), "candidate")
            self.assert_input_alias_rejected(spec, spec, (spec,))

    def test_rejects_output_aliasing_art_before_render(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw).resolve()
            spec = write_spec(root, base_spec(), "candidate")
            art = root / "art.svg"
            self.assert_input_alias_rejected(spec, art, (art,))

    def test_rejects_derived_receipt_aliasing_spec_before_render(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw).resolve()
            original = write_spec(root, base_spec(), "candidate")
            spec = root / "cover.render.json"
            original.replace(spec)
            self.assert_input_alias_rejected(spec, root / "cover.png", (spec,))

    def test_rejects_derived_thumbnail_aliasing_spec_before_render(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw).resolve()
            original = write_spec(root, base_spec(), "candidate")
            spec = root / "cover-thumbnail.png"
            original.replace(spec)
            self.assert_input_alias_rejected(spec, root / "cover.png", (spec,))

    def test_rejects_aliases_to_full_custom_font_manifest_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw).resolve()
            spec = write_spec(root, base_spec(), "candidate")
            fonts = root / "fonts"
            shutil.copytree(FONT_MANIFEST.parent, fonts)
            manifest = fonts / "manifest.json"
            protected = {
                "manifest": manifest,
                "unselected font": fonts / "IBMPlexMono-Bold.ttf",
                "unselected license": fonts / "licenses" / "ibm-plex-mono-OFL.txt",
            }
            for label, output in protected.items():
                with self.subTest(alias=label):
                    self.assert_input_alias_rejected(
                        spec,
                        output,
                        (output,),
                        manifest,
                    )

    def test_rejects_final_artifact_paths_resolving_to_same_location(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw).resolve()
            spec = write_spec(root, base_spec(), "candidate")
            output = root / "cover.png"
            receipt = root / "cover.render.json"
            receipt.symlink_to(output.name)
            with mock.patch.object(
                cover_renderer,
                "_render",
                side_effect=AssertionError("rendering began before collision rejection"),
            ) as render, self.assertRaisesRegex(
                CoverRenderError,
                "artifact paths collide",
            ):
                render_cover_spec(spec, output, FONT_MANIFEST)
            render.assert_not_called()
            self.assertTrue(receipt.is_symlink())
            self.assertEqual(output.name, os.readlink(receipt))

    @staticmethod
    def fake_render(
        _svg: Path,
        destination: Path,
        width: int,
        height: int,
        _environment: dict[str, str],
    ) -> None:
        destination.write_bytes(f"rendered {width}x{height}".encode("ascii"))

    def test_render_uses_an_isolated_fontconfig_for_selected_fonts(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw).resolve()
            font_root = root / "fonts & <pinned>"
            shutil.copytree(FONT_MANIFEST.parent, font_root)
            manifest = font_root / "manifest.json"
            spec = write_spec(root, base_spec(), "candidate")
            dimensions_by_raw: dict[Path, tuple[int, int]] = {}

            def fake_run(
                command: list[str],
                *,
                check: bool,
                capture_output: bool,
                env: dict[str, str] | None = None,
            ) -> None:
                self.assertTrue(check)
                self.assertTrue(capture_output)
                if command[0] == "rsvg-convert":
                    self.assertIsNotNone(env)
                    assert env is not None
                    self.assertIsNot(env, os.environ)
                    self.assertEqual("fc", env["PANGOCAIRO_BACKEND"])
                    self.assertEqual("/global/fonts.conf", os.environ["FONTCONFIG_FILE"])
                    self.assertEqual("global", os.environ["PANGOCAIRO_BACKEND"])

                    config_path = Path(env["FONTCONFIG_FILE"])
                    self.assertTrue(config_path.is_absolute())
                    config = ET.parse(config_path).getroot()
                    self.assertEqual([], config.findall("include"))
                    self.assertEqual(
                        {str(font_root.resolve())},
                        {node.text for node in config.findall("dir")},
                    )
                    cache_nodes = config.findall("cachedir")
                    self.assertEqual(1, len(cache_nodes))
                    cache_path = Path(cache_nodes[0].text or "")
                    self.assertTrue(cache_path.is_absolute())
                    self.assertEqual(config_path.parent, cache_path.parent)
                    self.assertTrue(cache_path.is_dir())
                    raw_config = config_path.read_text(encoding="utf-8")
                    self.assertIn("&amp;", raw_config)
                    self.assertIn("&lt;", raw_config)

                    output = Path(command[command.index("-o") + 1])
                    dimensions_by_raw[output] = (
                        int(command[command.index("-w") + 1]),
                        int(command[command.index("-h") + 1]),
                    )
                    output.write_bytes(b"raw")
                    return

                source = Path(command[1])
                width, height = dimensions_by_raw[source]
                normalized = Path(command[-1].removeprefix("PNG24:"))
                header = bytearray(29)
                header[:8] = b"\x89PNG\r\n\x1a\n"
                header[16:24] = struct.pack(">II", width, height)
                header[25] = 2
                normalized.write_bytes(header)

            with mock.patch.dict(
                os.environ,
                {
                    "FONTCONFIG_FILE": "/global/fonts.conf",
                    "PANGOCAIRO_BACKEND": "global",
                },
                clear=False,
            ), mock.patch.object(
                cover_renderer.shutil,
                "which",
                side_effect=lambda name: f"/fake/{name}",
            ), mock.patch.object(
                cover_renderer.subprocess,
                "run",
                side_effect=fake_run,
            ):
                result = render_cover_spec(spec, root / "cover.png", manifest)

            self.assertTrue(result.output_path.is_file())
            self.assertTrue(result.thumbnail_path.is_file())
            self.assertTrue(result.receipt_path.is_file())

    def test_publish_failure_restores_existing_thumbnail_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw).resolve()
            spec = write_spec(root, base_spec(), "candidate")
            output = root / "cover.png"
            thumbnail = root / "cover-thumbnail.png"
            receipt = root / "cover.render.json"
            target = root / "thumbnail-target.bin"
            output.write_bytes(b"existing cover")
            target.write_bytes(b"linked thumbnail target")
            raw_target = target.name
            thumbnail.symlink_to(raw_target)
            receipt.write_bytes(b"existing receipt")
            real_replace = os.replace

            def fail_receipt_publish(source: Path, destination: Path) -> None:
                if Path(destination) == receipt:
                    raise OSError("receipt publication failed")
                real_replace(source, destination)

            with mock.patch.object(
                cover_renderer,
                "_render",
                side_effect=self.fake_render,
            ), mock.patch.object(
                cover_renderer.os,
                "replace",
                side_effect=fail_receipt_publish,
            ), self.assertRaisesRegex(
                CoverRenderError,
                "rendered artifacts could not be published",
            ):
                render_cover_spec(spec, output, FONT_MANIFEST)

            self.assertEqual(b"existing cover", output.read_bytes())
            self.assertTrue(thumbnail.is_symlink())
            self.assertEqual(raw_target, os.readlink(thumbnail))
            self.assertEqual(b"linked thumbnail target", target.read_bytes())
            self.assertEqual(b"existing receipt", receipt.read_bytes())

    def test_publish_failure_restores_dangling_thumbnail_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw).resolve()
            spec = write_spec(root, base_spec(), "candidate")
            output = root / "cover.png"
            thumbnail = root / "cover-thumbnail.png"
            receipt = root / "cover.render.json"
            output.write_bytes(b"existing cover")
            raw_target = "missing-thumbnail-target.bin"
            thumbnail.symlink_to(raw_target)
            receipt.write_bytes(b"existing receipt")
            real_replace = os.replace

            def fail_receipt_publish(source: Path, destination: Path) -> None:
                if Path(destination) == receipt:
                    raise OSError("receipt publication failed")
                real_replace(source, destination)

            with mock.patch.object(
                cover_renderer,
                "_render",
                side_effect=self.fake_render,
            ), mock.patch.object(
                cover_renderer.os,
                "replace",
                side_effect=fail_receipt_publish,
            ), self.assertRaisesRegex(
                CoverRenderError,
                "rendered artifacts could not be published",
            ):
                render_cover_spec(spec, output, FONT_MANIFEST)

            self.assertEqual(b"existing cover", output.read_bytes())
            self.assertTrue(thumbnail.is_symlink())
            self.assertEqual(raw_target, os.readlink(thumbnail))
            self.assertFalse((root / raw_target).exists())
            self.assertEqual(b"existing receipt", receipt.read_bytes())

    def test_rollback_continues_after_one_destination_cannot_be_restored(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw).resolve()
            spec = write_spec(root, base_spec(), "candidate")
            output = root / "cover.png"
            thumbnail = root / "cover-thumbnail.png"
            receipt = root / "cover.render.json"
            output.write_bytes(b"existing cover")
            thumbnail.write_bytes(b"existing thumbnail")
            receipt.write_bytes(b"existing receipt")
            real_replace = os.replace

            def fail_publish_and_one_restore(source: Path, destination: Path) -> None:
                source_path = Path(source)
                destination_path = Path(destination)
                if destination_path == receipt:
                    raise OSError("receipt publication failed")
                if destination_path == thumbnail and source_path.name == "backup-1":
                    raise OSError("thumbnail rollback failed")
                real_replace(source, destination)

            with mock.patch.object(
                cover_renderer,
                "_render",
                side_effect=self.fake_render,
            ), mock.patch.object(
                cover_renderer.os,
                "replace",
                side_effect=fail_publish_and_one_restore,
            ), self.assertRaisesRegex(
                CoverRenderError,
                "rollback failed",
            ):
                render_cover_spec(spec, output, FONT_MANIFEST)

            self.assertEqual(b"existing cover", output.read_bytes())
            self.assertEqual(b"existing receipt", receipt.read_bytes())


if __name__ == "__main__":
    unittest.main()
