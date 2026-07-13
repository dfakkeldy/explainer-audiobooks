"""Behavior tests for the portable audiobook-cover compositor."""

from __future__ import annotations

import base64
import importlib.util
import io
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "skill" / "scripts" / "make_cover.py"
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("make_cover", SCRIPT)
assert SPEC and SPEC.loader
make_cover = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(make_cover)

# A valid 1×1 transparent PNG; enough to test portable data-URI embedding.
PIXEL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4"
    "z8DwHwAFgAI/ScLk7wAAAABJRU5ErkJggg=="
)


class MakeCoverArtLoadingTests(unittest.TestCase):
    def test_spec_mode_rejects_legacy_flags_instead_of_falling_back(self) -> None:
        stderr = io.StringIO()
        with tempfile.TemporaryDirectory() as raw_dir, \
                mock.patch.object(
                    sys,
                    "argv",
                    [
                        str(SCRIPT),
                        "--spec",
                        "candidate.json",
                        "--title",
                        "Wrong",
                        "--out",
                        str(Path(raw_dir) / "cover.png"),
                    ],
                ), \
                mock.patch.object(sys, "stderr", stderr), \
                self.assertRaises(SystemExit) as raised:
            make_cover.main()
        self.assertEqual(2, raised.exception.code)
        self.assertIn("--spec cannot be combined with legacy cover flags", stderr.getvalue())

    def test_spec_mode_rejects_equals_form_legacy_flags(self) -> None:
        stderr = io.StringIO()
        with tempfile.TemporaryDirectory() as raw_dir, \
                mock.patch.object(
                    sys,
                    "argv",
                    [
                        str(SCRIPT),
                        "--spec=candidate.json",
                        "--title=Wrong",
                        "--out",
                        str(Path(raw_dir) / "cover.png"),
                    ],
                ), \
                mock.patch.object(sys, "stderr", stderr), \
                self.assertRaises(SystemExit) as raised:
            make_cover.main()
        self.assertEqual(2, raised.exception.code)
        self.assertIn("--spec cannot be combined with legacy cover flags", stderr.getvalue())

    def test_load_raster_art_embeds_a_png_data_uri(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            image = Path(raw_dir) / "hero.png"
            image.write_bytes(PIXEL_PNG)

            art = make_cover.load_art(image)

            self.assertEqual("raster", art.kind)
            self.assertTrue(art.content.startswith("data:image/png;base64,"))
            embedded = make_cover.embed_art(art, 0, 0, 1600, 1200)
            self.assertIn('<image href="data:image/png;base64,', embedded)
            self.assertIn('preserveAspectRatio="xMidYMid meet"', embedded)

    def test_load_svg_art_preserves_its_viewbox_and_vector_content(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            image = Path(raw_dir) / "hero.svg"
            image.write_text(
                '<svg viewBox="0 0 300 400"><circle cx="150" cy="200" r="80"/></svg>',
                encoding="utf-8",
            )

            art = make_cover.load_art(image)

            self.assertEqual("svg", art.kind)
            self.assertEqual("0 0 300 400", art.viewbox)
            self.assertIn("<circle", art.content)
            embedded = make_cover.embed_art(art, 0, 0, 1600, 1200, "xMidYMid slice")
            self.assertIn('viewBox="0 0 300 400"', embedded)
            self.assertIn('preserveAspectRatio="xMidYMid slice"', embedded)

    def test_no_art_hero_keeps_the_original_signature_before_the_motif(self) -> None:
        svg = make_cover.build_svg(
            "A Better System",
            "A practical guide",
            "Dan Fakkeldy",
            "AUDIOBOOK",
            "A Better System",
            "#2ee8b6",
            None,
            "hero",
            "bright",
        )

        signature = svg.index('<path d="M0 0 H1600 V34')
        badge = svg.index('letter-spacing="13"')
        panel = svg.index('<rect x="130" y="420" width="1340" height="1180"')
        motif = svg.index('<circle cx="800" cy="720"')
        self.assertLess(signature, panel)
        self.assertLess(badge, panel)
        self.assertLess(panel, motif)

    def test_cli_defaults_to_bright_tone_and_keeps_dark_opt_in(self) -> None:
        def render_svg(arguments: list[str]) -> str:
            captured: list[str] = []

            def capture(svg_path: str, _png_path: str) -> bool:
                captured.append(Path(svg_path).read_text(encoding="utf-8"))
                return True

            with tempfile.TemporaryDirectory() as raw_dir, \
                    mock.patch.object(
                        sys,
                        "argv",
                        [
                            str(SCRIPT),
                            *arguments,
                            "--out",
                            str(Path(raw_dir) / "cover.png"),
                        ],
                    ), \
                    mock.patch.object(make_cover, "rasterize", side_effect=capture):
                self.assertEqual(0, make_cover.main())
            return captured[0]

        bright_svg = render_svg(["--title", "A Better System"])
        dark_svg = render_svg(["--title", "A Better System", "--tone", "dark"])

        self.assertIn('fill="#17130F"', bright_svg)
        self.assertIn('fill="#F6F3EE"', dark_svg)

    @unittest.skipUnless(
        shutil.which("magick") or shutil.which("convert"),
        "ImageMagick is required for raster-cover composition",
    )
    def test_cli_renders_a_full_size_cover_from_png_art(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            output_dir = Path(raw_dir)
            image = output_dir / "hero.png"
            image.write_bytes(PIXEL_PNG)

            for layout in ("bleed", "hero"):
                with self.subTest(layout=layout):
                    cover = output_dir / f"cover-{layout}.png"
                    result = subprocess.run(
                        [
                            sys.executable,
                            str(SCRIPT),
                            "--title",
                            "A Better System",
                            "--subtitle",
                            "A practical guide",
                            "--author",
                            "Dan Fakkeldy",
                            "--art",
                            str(image),
                            "--accent",
                            "#2ee8b6",
                            "--tone",
                            "bright",
                            "--layout",
                            layout,
                            "--out",
                            str(cover),
                        ],
                        capture_output=True,
                        text=True,
                        check=False,
                    )

                    self.assertEqual(0, result.returncode, result.stderr)
                    payload = cover.read_bytes()
                    self.assertEqual(b"\x89PNG\r\n\x1a\n", payload[:8])
                    self.assertEqual((1600, 2560), struct.unpack(">II", payload[16:24]))


if __name__ == "__main__":
    unittest.main()
