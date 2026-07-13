from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from PIL import Image

sys.path.insert(0, str(Path(__file__).parents[1] / "skill" / "scripts"))
import cover_pairs
from cover_pairs import CoverRenderError, render_cover_pair
from tests.test_cover_renderer import FONT_MANIFEST, base_spec


@unittest.skipUnless(
    shutil.which("rsvg-convert") and shutil.which("magick"),
    "renderer tools required",
)
class CoverPairTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.art = self.root / "art.svg"
        self.art.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2400 2560">'
            '<rect width="2400" height="2560" fill="#132238"/></svg>',
            encoding="utf-8",
        )
        self.portrait_spec = self.write_spec("portrait", "portrait")
        self.square_spec = self.write_spec("square", "square")
        self.outputs = (
            self.root / "portrait.png",
            self.root / "square.png",
            self.root / "portrait-thumbnail.png",
            self.root / "square-thumbnail.png",
            self.root / "portrait.render.json",
            self.root / "square.render.json",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_spec(
        self, name: str, variant: str, candidate_id: str = "open-machine"
    ) -> Path:
        payload = base_spec()
        payload["schema_version"] = 2
        payload["variant"] = variant
        payload["candidate"]["id"] = candidate_id
        if variant == "square":
            payload["canvas"].update(width=2400, height=2400, safe_margin=120)
            payload["art"]["box"] = [0, 0, 2400, 2400]
            for layer in payload["layers"]:
                layer["box"][0] = 120
            payload["layers"][0]["box"][1] = 120
            payload["layers"][3]["box"] = [120, 1950, 1408, 130]
            payload["layers"][4]["box"] = [120, 2150, 1408, 90]
        path = self.root / f"{name}.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def render_pair(self, portrait: Path, square: Path):
        return render_cover_pair(
            portrait, square, *self.outputs, font_manifest_path=FONT_MANIFEST
        )

    def install_existing_outputs(self) -> dict[Path, bytes]:
        sentinels = {}
        for index, path in enumerate(self.outputs):
            content = f"existing-{index}".encode()
            path.write_bytes(content)
            sentinels[path] = content
        return sentinels

    def assert_outputs_equal(self, sentinels: dict[Path, bytes]) -> None:
        self.assertEqual(
            {path: path.read_bytes() for path in sentinels}, sentinels
        )

    def test_pair_requires_same_candidate_and_source_hash(self) -> None:
        different = self.write_spec("different", "square", "different-candidate")
        with self.assertRaisesRegex(CoverRenderError, "candidate"):
            self.render_pair(self.portrait_spec, different)

        payload = json.loads(self.square_spec.read_text(encoding="utf-8"))
        (self.root / "other.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg"><rect fill="#ffffff"/></svg>',
            encoding="utf-8",
        )
        payload["art"]["path"] = "other.svg"
        changed_art = self.root / "changed-art.json"
        changed_art.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(CoverRenderError, "source"):
            self.render_pair(self.portrait_spec, changed_art)

    def test_pair_publishes_both_variants_and_receipts(self) -> None:
        result = self.render_pair(self.portrait_spec, self.square_spec)
        self.assertEqual(result.candidate_id, "open-machine")
        with Image.open(self.outputs[0]) as image:
            self.assertEqual(image.size, (1600, 2560))
        with Image.open(self.outputs[1]) as image:
            self.assertEqual(image.size, (2400, 2400))
        self.assertEqual(result.portrait.variant, "portrait")
        self.assertEqual(result.square.variant, "square")
        self.assertTrue(all(path.is_file() for path in self.outputs))
        portrait_receipt = json.loads(self.outputs[4].read_text(encoding="utf-8"))
        square_receipt = json.loads(self.outputs[5].read_text(encoding="utf-8"))
        self.assertEqual(portrait_receipt["output"], self.outputs[0].name)
        self.assertEqual(portrait_receipt["thumbnail"], self.outputs[2].name)
        self.assertEqual(square_receipt["output"], self.outputs[1].name)
        self.assertEqual(square_receipt["thumbnail"], self.outputs[3].name)

    def test_second_render_failure_preserves_all_existing_pair_files(self) -> None:
        sentinels = self.install_existing_outputs()
        real_render = cover_pairs.render_cover_spec
        calls = 0

        def fail_second(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise CoverRenderError("forced second render failure")
            return real_render(*args, **kwargs)

        with mock.patch("cover_pairs.render_cover_spec", side_effect=fail_second):
            with self.assertRaises(CoverRenderError):
                self.render_pair(self.portrait_spec, self.square_spec)
        self.assert_outputs_equal(sentinels)

    def test_publish_failure_restores_all_six_existing_outputs(self) -> None:
        sentinels = self.install_existing_outputs()
        replacements = 0
        real_replace = os.replace

        def fail_on_sixth(source, destination):
            nonlocal replacements
            replacements += 1
            if replacements == 6:
                raise OSError("forced sixth publish failure")
            return real_replace(source, destination)

        with mock.patch("cover_pairs._replace", side_effect=fail_on_sixth):
            with self.assertRaises(OSError):
                self.render_pair(self.portrait_spec, self.square_spec)
        self.assert_outputs_equal(sentinels)

    def test_pair_rejects_any_output_alias_or_hardlink_before_render(self) -> None:
        self.outputs[0].write_bytes(b"shared inode")
        os.link(self.outputs[0], self.outputs[1])
        with mock.patch("cover_pairs.render_cover_spec") as renderer:
            with self.assertRaisesRegex(CoverRenderError, "alias"):
                self.render_pair(self.portrait_spec, self.square_spec)
            renderer.assert_not_called()

    def test_pair_rejects_output_hardlinked_to_input_before_render(self) -> None:
        os.link(self.portrait_spec, self.outputs[0])
        with mock.patch("cover_pairs.render_cover_spec") as renderer:
            with self.assertRaisesRegex(CoverRenderError, "alias"):
                self.render_pair(self.portrait_spec, self.square_spec)
            renderer.assert_not_called()
