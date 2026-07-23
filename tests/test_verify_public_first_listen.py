import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from skill.scripts import verify_public_first_listen as verifier


DISCLOSURE = (
    "This edition has passed package and audio checks. The creator's full "
    "listening review is still underway."
)
GOVERNED_FINAL_DISCLOSURE = (
    "This edition has passed package and audio checks. The creator completed "
    "the full listening review and approved this edition for publication."
)


def artifact(root: Path, name: str, payload: bytes) -> dict[str, str]:
    path = root / name
    path.write_bytes(payload)
    return {"file": name, "sha256": hashlib.sha256(payload).hexdigest()}


class PublicFirstListenVerifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.book_dir = Path(self.temporary_directory.name)
        self.receipt = {
            "schemaVersion": 1,
            "slug": "fixture-book",
            "editionId": "public-first-listen-2026-07-18",
            "publicationStatus": "public-first-listen",
            "humanListeningStatus": "pending",
            "classification": "public-safe",
            "permissionToPublish": True,
            "permissionGrantedAt": "2026-07-18",
            "disclosure": DISCLOSURE,
            "sourceArtIncluded": True,
            "artifacts": {
                "manuscript": artifact(self.book_dir, "fixture-book.md", b"# Fixture\n"),
                "epub": artifact(self.book_dir, "fixture-book.epub", b"epub-fixture"),
                "m4b": artifact(self.book_dir, "fixture-book.m4b", b"m4b-fixture"),
                "alignment": artifact(
                    self.book_dir,
                    "fixture-book.alignment.json",
                    b'[{"blockId":"b1","timestamp":0}]\n',
                ),
                "portraitCover": artifact(self.book_dir, "cover.png", b"portrait"),
                "squareCover": artifact(self.book_dir, "m4b-cover.png", b"square"),
            },
        }
        (self.book_dir / "cover-source.png").write_bytes(b"source art")
        (self.book_dir / "cover-render.json").write_text(
            json.dumps({"source_art": "cover-source.png"}), encoding="utf-8"
        )
        (self.book_dir / "README.md").write_text(DISCLOSURE, encoding="utf-8")
        self.write_receipt()

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write_receipt(self) -> None:
        (self.book_dir / "publication.json").write_text(
            json.dumps(self.receipt), encoding="utf-8"
        )

    def probes(self):
        return mock.patch.object(
            verifier.subprocess,
            "run",
            return_value=subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout=json.dumps({"format": {"duration": "1.0"}, "chapters": [{}]}),
                stderr="",
            ),
        )

    def assert_rejected(self, pattern: str) -> None:
        with self.probes(), self.assertRaisesRegex(ValueError, pattern):
            verifier.verify_public_package(self.book_dir)

    def test_verifies_generic_public_package(self) -> None:
        with self.probes():
            verifier.verify_public_package(self.book_dir)

    def test_verifies_governed_final_public_package(self) -> None:
        self.receipt["publicationStatus"] = "governed-final"
        self.receipt["humanListeningStatus"] = "accepted"
        self.receipt["disclosure"] = GOVERNED_FINAL_DISCLOSURE
        self.write_receipt()
        (self.book_dir / "README.md").write_text(
            GOVERNED_FINAL_DISCLOSURE, encoding="utf-8"
        )

        with self.probes():
            verifier.verify_public_package(self.book_dir)

    def test_rejects_wrong_publication_or_listening_status(self) -> None:
        for field, value in (("publicationStatus", "governed-final"), ("humanListeningStatus", "accepted")):
            with self.subTest(field=field):
                self.receipt[field] = value
                self.write_receipt()
                self.assert_rejected(field)
                self.receipt[field] = "public-first-listen" if field == "publicationStatus" else "pending"

    def test_rejects_private_classification_or_missing_permission(self) -> None:
        for field, value in (("classification", "private"), ("permissionToPublish", False)):
            with self.subTest(field=field):
                self.receipt[field] = value
                self.write_receipt()
                self.assert_rejected(field)
                self.receipt[field] = "public-safe" if field == "classification" else True

    def test_rejects_wrong_disclosure_and_readme_without_disclosure(self) -> None:
        self.receipt["disclosure"] = "close enough"
        self.write_receipt()
        self.assert_rejected("disclosure")
        self.receipt["disclosure"] = DISCLOSURE
        self.write_receipt()
        (self.book_dir / "README.md").write_text("status only", encoding="utf-8")
        self.assert_rejected("README")

    def test_rejects_slug_filename_missing_file_and_hash_mismatch(self) -> None:
        cases = (
            ("slug", "other-book", "manuscript"),
            ("missing", None, "missing"),
            ("hash", "0" * 64, "SHA-256"),
        )
        for kind, value, pattern in cases:
            with self.subTest(kind=kind):
                if kind == "slug":
                    self.receipt["slug"] = value
                elif kind == "missing":
                    (self.book_dir / "fixture-book.m4b").unlink()
                else:
                    self.receipt["artifacts"]["m4b"]["sha256"] = value
                self.write_receipt()
                self.assert_rejected(pattern)
                if kind == "slug":
                    self.receipt["slug"] = "fixture-book"
                elif kind == "missing":
                    self.receipt["artifacts"]["m4b"] = artifact(self.book_dir, "fixture-book.m4b", b"m4b-fixture")
                else:
                    self.receipt["artifacts"]["m4b"] = artifact(self.book_dir, "fixture-book.m4b", b"m4b-fixture")

    def test_rejects_absolute_and_file_url_values_anywhere(self) -> None:
        for value in (
            "/Users/private/book",
            "file:///private/book",
            "FILE:///private/book",
            "FiLe:///private/book",
            "C:\\private\\book",
        ):
            with self.subTest(value=value):
                self.receipt["nested"] = {"value": value}
                self.write_receipt()
                self.assert_rejected("absolute path")
                self.receipt.pop("nested")

    def test_rejects_forbidden_internal_files(self) -> None:
        for name in ("echo-render-inputs.json", "pronunciation-audit.json", "pronunciation-reel.m4a", "resume-state.json", "research/notes.md"):
            with self.subTest(name=name):
                path = self.book_dir / name
                path.parent.mkdir(exist_ok=True)
                path.write_text("private", encoding="utf-8")
                self.assert_rejected("forbidden")
                if path.parent == self.book_dir:
                    path.unlink()
                else:
                    path.unlink()
                    path.parent.rmdir()

    def test_requires_named_source_art_when_included(self) -> None:
        (self.book_dir / "cover-source.png").unlink()
        self.assert_rejected("source art")

    def test_rejects_source_art_when_receipt_says_absent(self) -> None:
        self.receipt["sourceArtIncluded"] = False
        self.write_receipt()
        self.assert_rejected("source art")

    def test_rejects_nested_stale_source_art_when_receipt_says_absent(self) -> None:
        self.receipt["sourceArtIncluded"] = False
        (self.book_dir / "cover-source.png").unlink()
        nested = self.book_dir / "assets"
        nested.mkdir()
        (nested / "cover-source.png").write_bytes(b"stale source art")
        self.write_receipt()
        self.assert_rejected("source art")

    def test_rejects_artifact_symlink_to_outside_content(self) -> None:
        external = self.book_dir.parent / "external.m4b"
        external.write_bytes(b"m4b-fixture")
        artifact_path = self.book_dir / "fixture-book.m4b"
        artifact_path.unlink()
        artifact_path.symlink_to(external)
        self.assert_rejected("symlink")

    def test_rejects_symlinked_directory_anywhere_in_package(self) -> None:
        external_directory = self.book_dir.parent / f"{self.book_dir.name}-external-directory"
        external_directory.mkdir()
        (self.book_dir / "linked-assets").symlink_to(external_directory, target_is_directory=True)
        self.assert_rejected("symlink")

    def test_rejects_declared_source_art_symlink(self) -> None:
        external = self.book_dir.parent / "external-source.png"
        external.write_bytes(b"source art")
        declared_art = self.book_dir / "cover-source.png"
        declared_art.unlink()
        declared_art.symlink_to(external)
        self.assert_rejected("symlink")

    @unittest.skipUnless(
        shutil.which("unzip") and shutil.which("ffprobe") and shutil.which("ffmpeg"),
        "requires unzip, ffprobe, and ffmpeg",
    )
    def test_accepts_a_package_with_real_unzip_and_ffprobe(self) -> None:
        with zipfile.ZipFile(self.book_dir / "fixture-book.epub", "w") as archive:
            archive.write(self.book_dir / "fixture-book.md", "fixture-book.md")
        chapters = self.book_dir / "chapters.ffmeta"
        chapters.write_text(
            ";FFMETADATA1\n[CHAPTER]\nTIMEBASE=1/1000\nSTART=0\nEND=100\ntitle=Chapter 1\n",
            encoding="utf-8",
        )
        subprocess.run(
            [
                "ffmpeg", "-loglevel", "error", "-f", "lavfi", "-i",
                "sine=frequency=1000:duration=0.1", "-i", str(chapters),
                "-map_metadata", "1", "-c:a", "aac", "-y",
                str(self.book_dir / "fixture-book.m4b"),
            ],
            check=True,
        )
        self.receipt["artifacts"]["epub"] = artifact(
            self.book_dir, "fixture-book.epub", (self.book_dir / "fixture-book.epub").read_bytes()
        )
        self.receipt["artifacts"]["m4b"] = artifact(
            self.book_dir, "fixture-book.m4b", (self.book_dir / "fixture-book.m4b").read_bytes()
        )
        self.write_receipt()
        verifier.verify_public_package(self.book_dir)
