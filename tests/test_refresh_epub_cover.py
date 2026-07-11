"""Round-trip and fail-closed tests for EPUB cover replacement."""

from __future__ import annotations

import binascii
import hashlib
import struct
import sys
import unittest
import zipfile
import zlib
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).parents[1] / "skill" / "scripts"))
import refresh_epub_cover  # noqa: E402


def make_png(path: Path, dimensions: tuple[int, int], color: str = "#D62828") -> Path:
    width, height = dimensions
    rgb = bytes.fromhex(color.removeprefix("#"))

    def chunk(kind: bytes, data: bytes) -> bytes:
        payload = kind + data
        return struct.pack(">I", len(data)) + payload + struct.pack(">I", binascii.crc32(payload))

    # The utility only needs IHDR dimensions, but these chunks also make a valid
    # one-colour PNG without pulling an imaging dependency into the test suite.
    import zlib

    scanline = b"\x00" + rgb * width
    pixels = zlib.compress(scanline * height)
    data = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", pixels)
        + chunk(b"IEND", b"")
    )
    path.write_bytes(data)
    return path


def make_epub_fixture(
    directory: Path,
    *,
    cover_href: str | None = "cover-old.png",
    cover_properties: tuple[str, ...] = ("cover-image",),
    legacy: bool = False,
    media_type: str = "image/png",
) -> Path:
    source = directory / "source.epub"
    manifest_items = []
    for index, properties in enumerate(cover_properties):
        href = cover_href if index == 0 else f"cover-{index}.png"
        manifest_items.append(
            f'<item id="cover{index}" href="{href}" media-type="{media_type}" '
            f'properties="{properties}"/>'
        )
    legacy_meta = '<meta name="cover" content="cover0"/>' if legacy else ""
    opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0">
  <metadata>{legacy_meta}</metadata>
  <manifest>{''.join(manifest_items)}
    <item id="chapter" href="chapter.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
</package>"""
    old_cover = make_png(directory / "old.png", (600, 900), "#111111").read_bytes()
    with zipfile.ZipFile(source, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        archive.writestr(
            "META-INF/container.xml",
            '<?xml version="1.0"?><container xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
            '<rootfiles><rootfile full-path="OEBPS/content.opf"/></rootfiles></container>',
        )
        archive.writestr("OEBPS/content.opf", opf)
        for index in range(len(cover_properties)):
            href = cover_href if index == 0 else f"cover-{index}.png"
            href_path = urlsplit(href or "").path
            if href_path and not href_path.startswith("../"):
                archive.writestr(f"OEBPS/{href_path}", old_cover)
        archive.writestr("OEBPS/chapter.xhtml", b"<p>untouched chapter bytes</p>")
    return source


def assert_epub_invariants(test: unittest.TestCase, output: Path, source: Path) -> None:
    with zipfile.ZipFile(source) as before, zipfile.ZipFile(output) as after:
        test.assertEqual(before.namelist(), after.namelist())
        test.assertEqual(before.read("OEBPS/chapter.xhtml"), after.read("OEBPS/chapter.xhtml"))
        test.assertEqual("mimetype", after.infolist()[0].filename)
        test.assertEqual(zipfile.ZIP_STORED, after.infolist()[0].compress_type)
        changed = [name for name in before.namelist() if before.read(name) != after.read(name)]
        test.assertEqual(["OEBPS/cover-old.png"], changed)


class RefreshEpubCoverTests(unittest.TestCase):
    def test_replaces_declared_cover_and_preserves_epub(self) -> None:
        with TemporaryDirectory() as raw_dir:
            tmp_path = Path(raw_dir)
            source = make_epub_fixture(tmp_path, cover_href="cover-old.png")
            new_cover = make_png(tmp_path / "new.png", (1600, 2560), "#D62828")
            result = refresh_epub_cover.replace_epub_cover(source, new_cover, tmp_path / "out.epub")
            self.assertEqual("OEBPS/content.opf", result.opf_path)
            self.assertEqual("OEBPS/cover-old.png", result.cover_member)
            self.assertEqual((1600, 2560), (result.width, result.height))
            self.assertEqual(hashlib.sha256(new_cover.read_bytes()).hexdigest(), result.sha256)
            assert_epub_invariants(self, tmp_path / "out.epub", source)

    def test_legacy_cover_meta_lookup(self) -> None:
        with TemporaryDirectory() as raw_dir:
            root = Path(raw_dir)
            source = make_epub_fixture(root, cover_properties=("",), legacy=True)
            cover = make_png(root / "new.png", (1600, 2560))
            result = refresh_epub_cover.replace_epub_cover(source, cover, root / "out.epub")
            self.assertEqual("OEBPS/cover-old.png", result.cover_member)

    def test_rejects_zero_cover_items(self) -> None:
        self._assert_rejected((), "no cover image")

    def test_rejects_two_cover_image_items(self) -> None:
        self._assert_rejected(("cover-image", "cover-image"), "ambiguous cover image")

    def test_rejects_path_traversal(self) -> None:
        self._assert_rejected(("cover-image",), "escapes EPUB root", cover_href="../../cover.png")

    def test_rejects_jpeg_candidate(self) -> None:
        self._assert_rejected(("cover-image",), "cover must be PNG", media_type="image/jpeg")

    def test_rejects_wrong_dimensions(self) -> None:
        with TemporaryDirectory() as raw_dir:
            root = Path(raw_dir)
            source = make_epub_fixture(root)
            cover = make_png(root / "new.png", (1200, 1800))
            with self.assertRaisesRegex(ValueError, "1600x2560"):
                refresh_epub_cover.replace_epub_cover(source, cover, root / "out.epub")

    def test_rejects_truncated_png_with_valid_signature_and_ihdr(self) -> None:
        with TemporaryDirectory() as raw_dir:
            root = Path(raw_dir)
            source = make_epub_fixture(root)
            valid = make_png(root / "valid.png", (1600, 2560)).read_bytes()
            cover = root / "truncated.png"
            cover.write_bytes(valid[:33])
            with self.assertRaisesRegex(ValueError, "invalid PNG"):
                refresh_epub_cover.replace_epub_cover(source, cover, root / "out.epub")

    def test_rejects_png_with_decodable_zlib_but_incomplete_pixels(self) -> None:
        with TemporaryDirectory() as raw_dir:
            root = Path(raw_dir)
            source = make_epub_fixture(root)
            valid = make_png(root / "valid.png", (1600, 2560)).read_bytes()
            idat = valid.index(b"IDAT")
            chunk_start = idat - 4
            chunk_length = struct.unpack(">I", valid[chunk_start:idat])[0]
            chunk_end = idat + 4 + chunk_length + 4

            def chunk(kind: bytes, data: bytes) -> bytes:
                payload = kind + data
                return (
                    struct.pack(">I", len(data))
                    + payload
                    + struct.pack(">I", binascii.crc32(payload))
                )

            malformed = (
                valid[:chunk_start]
                + chunk(b"IDAT", zlib.compress(b""))
                + valid[chunk_end:]
            )
            cover = root / "incomplete-pixels.png"
            cover.write_bytes(malformed)
            with self.assertRaisesRegex(ValueError, "invalid PNG"):
                refresh_epub_cover.replace_epub_cover(source, cover, root / "out.epub")

    def test_rejects_indexed_png_without_palette(self) -> None:
        with TemporaryDirectory() as raw_dir:
            root = Path(raw_dir)
            source = make_epub_fixture(root)

            def chunk(kind: bytes, data: bytes) -> bytes:
                payload = kind + data
                return (
                    struct.pack(">I", len(data))
                    + payload
                    + struct.pack(">I", binascii.crc32(payload))
                )

            scanline = b"\x00" + bytes(1600)
            malformed = (
                b"\x89PNG\r\n\x1a\n"
                + chunk(b"IHDR", struct.pack(">IIBBBBB", 1600, 2560, 8, 3, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(scanline * 2560))
                + chunk(b"IEND", b"")
            )
            cover = root / "indexed-without-palette.png"
            cover.write_bytes(malformed)

            with self.assertRaisesRegex(ValueError, "invalid PNG"):
                refresh_epub_cover.replace_epub_cover(source, cover, root / "out.epub")

    def test_rejects_cover_href_fragment(self) -> None:
        self._assert_rejected(
            ("cover-image",),
            "internal EPUB path",
            cover_href="cover-old.png#alternate",
        )

    def test_rebuilt_validation_rejects_changed_non_cover_payload(self) -> None:
        with TemporaryDirectory() as raw_dir:
            root = Path(raw_dir)
            source_path = make_epub_fixture(root)
            rebuilt_path = root / "rebuilt.epub"
            with zipfile.ZipFile(source_path) as source, zipfile.ZipFile(
                rebuilt_path, "w"
            ) as rebuilt:
                for info in source.infolist():
                    payload = source.read(info)
                    if info.filename == "OEBPS/chapter.xhtml":
                        payload = b"changed"
                    rebuilt.writestr(info, payload)
            with zipfile.ZipFile(source_path) as source, zipfile.ZipFile(
                rebuilt_path
            ) as rebuilt:
                with self.assertRaisesRegex(ValueError, "payload changed"):
                    refresh_epub_cover._validate_rebuilt_epub(
                        source,
                        rebuilt,
                        "OEBPS/cover-old.png",
                        source.read("OEBPS/cover-old.png"),
                    )

    def _assert_rejected(
        self,
        properties: tuple[str, ...],
        message: str,
        **fixture_options: object,
    ) -> None:
        with TemporaryDirectory() as raw_dir:
            root = Path(raw_dir)
            source = make_epub_fixture(root, cover_properties=properties, **fixture_options)
            cover = make_png(root / "new.png", (1600, 2560))
            with self.assertRaisesRegex(ValueError, message):
                refresh_epub_cover.replace_epub_cover(source, cover, root / "out.epub")


if __name__ == "__main__":
    unittest.main()
