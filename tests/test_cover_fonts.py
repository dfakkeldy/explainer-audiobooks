from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "skill" / "scripts"))
from cover_fonts import CoverFontError, load_font_manifest


class CoverFontManifestTests(unittest.TestCase):
    def make_manifest(self, root: Path) -> Path:
        font = root / "Demo.ttf"
        licence = root / "demo-OFL.txt"
        font.write_bytes(b"font-bytes")
        licence.write_text("SIL OPEN FONT LICENSE Version 1.1", encoding="utf-8")
        payload = {
            "manifest_version": 1,
            "source_commit": "a" * 40,
            "fonts": [
                {
                    "font_id": "display-condensed",
                    "family": "Demo",
                    "style": "Black",
                    "roles": ["title", "label"],
                    "path": "Demo.ttf",
                    "sha256": hashlib.sha256(font.read_bytes()).hexdigest(),
                    "license": "OFL-1.1",
                    "license_path": "demo-OFL.txt",
                    "license_sha256": hashlib.sha256(licence.read_bytes()).hexdigest(),
                    "source_url": "https://example.invalid/Demo.ttf",
                    "glyph_coverage": ["latin", "latin-ext"],
                    "width_factor": 0.48,
                    "axes": {},
                }
            ],
        }
        manifest = root / "manifest.json"
        manifest.write_text(json.dumps(payload), encoding="utf-8")
        return manifest

    def test_loads_hash_checked_font_record(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = load_font_manifest(self.make_manifest(Path(raw)))
            record = manifest.require("display-condensed", role="title")
            self.assertEqual("Demo", record.family)
            self.assertEqual(0.48, record.width_factor)
            self.assertTrue(record.path.is_file())

    def test_rejects_tampered_font_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = self.make_manifest(Path(raw))
            (Path(raw) / "Demo.ttf").write_bytes(b"tampered")
            with self.assertRaisesRegex(CoverFontError, "font hash mismatch"):
                load_font_manifest(path)

    def test_rejects_unknown_role_and_unknown_identifier(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = load_font_manifest(self.make_manifest(Path(raw)))
            with self.assertRaisesRegex(CoverFontError, "does not support role author"):
                manifest.require("display-condensed", role="author")
            with self.assertRaisesRegex(CoverFontError, "unknown font_id"):
                manifest.require("missing", role="title")

    def test_rejects_asset_path_escape(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            manifest_path = self.make_manifest(root)
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            payload["fonts"][0]["path"] = "../outside.ttf"
            manifest_path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(CoverFontError, "escapes font directory"):
                load_font_manifest(manifest_path)


if __name__ == "__main__":
    unittest.main()
