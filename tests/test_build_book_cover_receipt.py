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


class BuildBookCoverReceiptTests(unittest.TestCase):
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
