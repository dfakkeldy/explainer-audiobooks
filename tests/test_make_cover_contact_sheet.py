"""Behavior tests for the audiobook-cover contact-sheet renderer."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parents[1] / "skill" / "scripts"))
import make_cover_contact_sheet  # noqa: E402


def make_entries(
    root: Path, count: int, size: tuple[int, int] = (1600, 2560)
) -> list[dict[str, str]]:
    entries = []
    for index in range(count):
        cover = root / f"cover-{index}.png"
        Image.new("RGB", size, (index * 17 % 255, 60, 120)).save(cover)
        entries.append({"title": f"Book {index + 1}", "cover": str(cover)})
    return entries


def make_single_entry(
    root: Path, *, title: str, image: Image.Image, suffix: str
) -> list[dict[str, str]]:
    cover = root / f"cover{suffix}"
    image.save(cover)
    return [{"title": title, "cover": str(cover)}]


class MakeCoverContactSheetTests(unittest.TestCase):
    def test_builds_three_column_contact_sheet_in_manifest_order(self) -> None:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as raw_dir:
            root = Path(raw_dir)
            entries = make_entries(root, count=11)
            result = make_cover_contact_sheet.render(entries, root / "sheet.png")

            self.assertEqual(11, result.cover_count)
            self.assertEqual(3, result.columns)
            self.assertEqual(4, result.rows)
            with Image.open(result.path) as sheet:
                self.assertEqual("RGB", sheet.mode)
                self.assertEqual((1008, 2328), sheet.size)
                expected = [Image.open(entry["cover"]).resize((320, 512)).getpixel((0, 0)) for entry in entries]
                actual = []
                for index in range(len(entries)):
                    column = index % 3
                    row = index // 3
                    actual.append(sheet.getpixel((column * 344, row * 588)))
                self.assertEqual(expected, actual)

    def test_rejects_wrong_cover_dimensions(self) -> None:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as raw_dir:
            root = Path(raw_dir)
            entries = make_entries(root, count=1, size=(800, 1280))
            with self.assertRaisesRegex(ValueError, r"entry 1.*1600x2560"):
                make_cover_contact_sheet.render(entries, root / "sheet.png")

    def test_rejects_jpeg_cover(self) -> None:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as raw_dir:
            root = Path(raw_dir)
            entries = make_single_entry(
                root,
                title="JPEG Book",
                image=Image.new("RGB", (1600, 2560), "navy"),
                suffix=".jpg",
            )
            with self.assertRaisesRegex(ValueError, r"entry 1.*PNG format.*JPEG"):
                make_cover_contact_sheet.render(entries, root / "sheet.png")

    def test_rejects_grayscale_png_cover(self) -> None:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as raw_dir:
            root = Path(raw_dir)
            entries = make_single_entry(
                root,
                title="Grayscale Book",
                image=Image.new("L", (1600, 2560), 80),
                suffix=".png",
            )
            with self.assertRaisesRegex(ValueError, r"entry 1.*RGB mode.*L"):
                make_cover_contact_sheet.render(entries, root / "sheet.png")

    def test_rejects_rgba_png_cover(self) -> None:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as raw_dir:
            root = Path(raw_dir)
            entries = make_single_entry(
                root,
                title="RGBA Book",
                image=Image.new("RGBA", (1600, 2560), (20, 40, 60, 128)),
                suffix=".png",
            )
            with self.assertRaisesRegex(ValueError, r"entry 1.*RGB mode.*RGBA"):
                make_cover_contact_sheet.render(entries, root / "sheet.png")

    def test_rejects_missing_cover_and_identifies_entry(self) -> None:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as raw_dir:
            root = Path(raw_dir)
            entries = [{"title": "Missing Book", "cover": str(root / "missing.png")}]
            with self.assertRaisesRegex(ValueError, r"entry 1.*Missing Book.*missing.png"):
                make_cover_contact_sheet.render(entries, root / "sheet.png")

    def test_rejects_duplicate_titles_and_identifies_entry(self) -> None:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as raw_dir:
            root = Path(raw_dir)
            entries = make_entries(root, count=2)
            entries[1]["title"] = entries[0]["title"]
            with self.assertRaisesRegex(ValueError, r"entry 2.*duplicate title.*Book 1"):
                make_cover_contact_sheet.render(entries, root / "sheet.png")

    def test_rejects_empty_input(self) -> None:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as raw_dir:
            root = Path(raw_dir)
            with self.assertRaisesRegex(ValueError, "at least one entry"):
                make_cover_contact_sheet.render([], root / "sheet.png")

    def test_draws_a_label_in_every_cell(self) -> None:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as raw_dir:
            root = Path(raw_dir)
            entries = make_entries(root, count=5)
            result = make_cover_contact_sheet.render(entries, root / "sheet.png")

            with Image.open(result.path) as sheet:
                for index in range(len(entries)):
                    column = index % 3
                    row = index // 3
                    left = column * 344
                    top = row * 588 + 512
                    label = sheet.crop((left, top, left + 320, top + 52))
                    self.assertIsNotNone(
                        label.getbbox(), f"entry {index + 1} should have a label band"
                    )
                    self.assertTrue(
                        any(pixel != (255, 255, 255) for pixel in label.getdata()),
                        f"entry {index + 1} label band should contain text",
                    )

    def test_long_label_cannot_invade_gutter_or_neighbor(self) -> None:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as raw_dir:
            root = Path(raw_dir)
            entries = make_entries(root, count=2)
            entries[0]["title"] = "A very long audiobook title " * 30
            result = make_cover_contact_sheet.render(entries, root / "sheet.png")

            with Image.open(result.path) as sheet:
                gutter = sheet.crop((320, 512, 344, 564))
                self.assertTrue(
                    all(pixel == (255, 255, 255) for pixel in gutter.getdata()),
                    "long labels must remain clipped to their 320px cell",
                )


if __name__ == "__main__":
    unittest.main()
