from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from PIL import Image

sys.path.insert(0, str(Path(__file__).parents[1] / "skill" / "scripts"))
import build_book


def selection(path: Path, cover: Path, slug: str = "fixture-book") -> Path:
    payload = {
        "receipt_version": 1, "book_slug": slug, "edition_id": "v1",
        "selected_candidate": "c1", "direction_name": "Fixture", "schema_version": 1,
        "spec_sha256": "1" * 64, "source_art_sha256": "2" * 64,
        "rendered_cover_sha256": hashlib.sha256(cover.read_bytes()).hexdigest(),
        "font_manifest_version": 1, "font_manifest_sha256": "3" * 64,
        "dimensions": [1600, 2560], "colour_mode": "RGB",
        "selected_at": "2026-07-12T13:00:00-03:00",
        "selection_source": "explicit-user-choice",
        "privacy": {"classification": "public-safe", "permission_to_publish": "granted"}
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def paired_selection(path: Path, cover: Path, square: Path) -> Path:
    payload = {
        "schema_version": 2, "book_slug": "fixture-book", "edition_id": "v2",
        "candidate": {"id": "c1", "direction_name": "Fixture"},
        "source_art_sha256": "2" * 64,
        "variants": {
            "portrait": {"specification_sha256": "1" * 64, "render_receipt_sha256": "3" * 64,
                         "cover_sha256": hashlib.sha256(cover.read_bytes()).hexdigest(),
                         "dimensions": [1600, 2560], "thumbnail_sha256": "4" * 64,
                         "subtitle_included": False},
            "square": {"specification_sha256": "5" * 64, "render_receipt_sha256": "6" * 64,
                       "cover_sha256": hashlib.sha256(square.read_bytes()).hexdigest(),
                       "dimensions": [2400, 2400], "thumbnail_sha256": "7" * 64,
                       "subtitle_included": False},
        },
        "font_manifest_sha256": "8" * 64, "selection_source": "user",
        "selected_at": "2026-07-13T13:00:00-03:00",
        "privacy": {"classification": "public-safe", "permission_to_publish": True},
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


class BuildBookCoverReceiptTests(unittest.TestCase):
    def test_paired_build_requires_fresh_square_before_outputs(self) -> None:
        for state in ("missing", "stale"):
            with self.subTest(state=state), tempfile.TemporaryDirectory() as raw:
                root = Path(raw); chapters = root / "chapters"; out = root / "dist"
                chapters.mkdir(); (chapters / "ch01.md").write_text("# One\n\nText.", encoding="utf-8")
                cover = root / "cover.png"; square = root / "m4b-cover.png"
                Image.new("RGB", (1600, 2560), "#132238").save(cover)
                Image.new("RGB", (2400, 2400), "#233248").save(square)
                receipt = paired_selection(root / "selection.json", cover, square)
                if state == "missing": square.unlink()
                else: Image.new("RGB", (2400, 2400), "#334258").save(square)
                with self.assertRaisesRegex(ValueError, "square"):
                    build_book.build(chapters, out, "Fixture", "Dan", "", "fixture-book",
                                     cover=cover, cover_selection=receipt, m4b_cover=square)
                self.assertFalse(out.exists())

    def test_paired_build_verifies_both_assets_before_and_epub_after_embedding(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); chapters = root / "chapters"; out = root / "dist"
            chapters.mkdir(); (chapters / "ch01.md").write_text("# One\n\nText.", encoding="utf-8")
            cover = root / "cover.png"; square = root / "m4b-cover.png"
            Image.new("RGB", (1600, 2560), "#132238").save(cover)
            Image.new("RGB", (2400, 2400), "#233248").save(square)
            receipt = paired_selection(root / "selection.json", cover, square)
            with mock.patch.object(build_book, "verify_package", wraps=build_book.verify_package) as verify:
                build_book.build(chapters, out, "Fixture", "Dan", "", "fixture-book",
                                 cover=cover, cover_selection=receipt, m4b_cover=square)
            self.assertEqual(2, verify.call_count)
            self.assertEqual(square, verify.call_args_list[0].kwargs["m4b_cover_path"])
            self.assertNotIn("epub_path", verify.call_args_list[0].kwargs)
            self.assertEqual(square, verify.call_args_list[1].kwargs["m4b_cover_path"])
            self.assertIn("epub_path", verify.call_args_list[1].kwargs)
    def test_build_verifies_receipt_before_and_after_embedding(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); chapters = root / "chapters"; out = root / "dist"
            chapters.mkdir(); (chapters / "ch01.md").write_text("# One\n\nA complete chapter.", encoding="utf-8")
            cover = root / "cover.png"; Image.new("RGB", (1600, 2560), "#132238").save(cover)
            receipt = selection(root / "cover-selection.json", cover)
            build_book.build(chapters, out, "Fixture", "Dan Fakkeldy", "", "fixture-book", cover=cover, cover_selection=receipt)
            with zipfile.ZipFile(out / "fixture-book.epub") as archive:
                self.assertEqual(cover.read_bytes(), archive.read("OEBPS/cover.png"))

    def test_build_rejects_stale_cover_or_wrong_slug(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); chapters = root / "chapters"; out = root / "dist"
            chapters.mkdir(); (chapters / "ch01.md").write_text("# One\n\nA complete chapter.", encoding="utf-8")
            cover = root / "cover.png"; Image.new("RGB", (1600, 2560), "#132238").save(cover)
            receipt = selection(root / "cover-selection.json", cover, slug="other-book")
            with self.assertRaisesRegex(ValueError, "selection book_slug"):
                build_book.build(chapters, out, "Fixture", "Dan Fakkeldy", "", "fixture-book", cover=cover, cover_selection=receipt)

    def test_build_rejects_stale_cover_before_writing_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); chapters = root / "chapters"; out = root / "dist"
            chapters.mkdir(); (chapters / "ch01.md").write_text("# One\n\nA complete chapter.", encoding="utf-8")
            cover = root / "cover.png"; Image.new("RGB", (1600, 2560), "#132238").save(cover)
            receipt = selection(root / "cover-selection.json", cover)
            Image.new("RGB", (1600, 2560), "#384C67").save(cover)

            with self.assertRaisesRegex(ValueError, "selected cover hash"):
                build_book.build(chapters, out, "Fixture", "Dan Fakkeldy", "", "fixture-book", cover=cover, cover_selection=receipt)

            self.assertFalse(out.exists())

    def test_build_rejects_selection_without_cover_before_writing_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); chapters = root / "chapters"; out = root / "dist"
            chapters.mkdir(); (chapters / "ch01.md").write_text("# One\n\nA complete chapter.", encoding="utf-8")
            cover = root / "cover.png"; Image.new("RGB", (1600, 2560), "#132238").save(cover)
            receipt = selection(root / "cover-selection.json", cover)

            with self.assertRaisesRegex(ValueError, "requires an existing --cover"):
                build_book.build(chapters, out, "Fixture", "Dan Fakkeldy", "", "fixture-book", cover_selection=receipt)

            self.assertFalse(out.exists())

    def test_failed_post_embed_verification_removes_new_epub_and_preserves_existing(self) -> None:
        for existing in (None, b"previous-valid-epub"):
            with self.subTest(existing=existing is not None), tempfile.TemporaryDirectory() as raw:
                root = Path(raw); chapters = root / "chapters"; out = root / "dist"
                chapters.mkdir(); (chapters / "ch01.md").write_text("# One\n\nA complete chapter.", encoding="utf-8")
                cover = root / "cover.png"; Image.new("RGB", (1600, 2560), "#132238").save(cover)
                receipt = selection(root / "cover-selection.json", cover)
                epub = out / "fixture-book.epub"
                if existing is not None:
                    out.mkdir()
                    epub.write_bytes(existing)

                with mock.patch.object(build_book, "verify_package", side_effect=ValueError("embedded cover mismatch")), self.assertRaisesRegex(ValueError, "embedded cover mismatch"):
                    build_book.build(chapters, out, "Fixture", "Dan Fakkeldy", "", "fixture-book", cover=cover, cover_selection=receipt)

                if existing is None:
                    self.assertFalse(epub.exists())
                else:
                    self.assertEqual(existing, epub.read_bytes())
                self.assertEqual([], list(out.glob(".fixture-book.epub.*.incoming")))


if __name__ == "__main__":
    unittest.main()
