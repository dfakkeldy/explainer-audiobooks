import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from PIL import Image

from skill.scripts import public_audio_recovery as recovery
from skill.scripts.public_audio_recovery import (
    validate_public_json,
    verify_block_parity,
)


class PublicAudioRecoveryModuleTests(unittest.TestCase):
    def test_recovery_module_exists(self):
        self.assertIsNotNone(
            importlib.util.find_spec("skill.scripts.public_audio_recovery")
        )

    def test_legacy_pair_interfaces_exist(self):
        self.assertTrue(callable(getattr(recovery, "verify_legacy_cover_pair", None)))
        self.assertTrue(callable(getattr(recovery, "write_legacy_cover_pair", None)))

    def test_manifest_interfaces_and_exact_slug_sets_exist(self):
        self.assertTrue(callable(getattr(recovery, "build_recovery_manifest", None)))
        self.assertTrue(callable(getattr(recovery, "verify_recovery_manifest", None)))
        self.assertTrue(callable(getattr(recovery, "build_recovery_record", None)))
        self.assertTrue(callable(getattr(recovery, "verify_recovery_record", None)))
        self.assertEqual(
            recovery.RECOVERED_SLUGS,
            (
                "echo-from-the-inside",
                "why-it-feels-right",
                "you-are-the-architect",
                "the-bug-is-a-clue",
                "tests-first",
                "git-happens",
                "findable",
                "the-voice-in-the-machine",
            ),
        )
        self.assertEqual(
            recovery.REMUXED_SLUGS,
            recovery.RECOVERED_SLUGS + ("rodents-in-the-walls",),
        )

    def test_cli_exposes_record_verify_and_record_cover_commands(self):
        result = subprocess.run(
            [sys.executable, str(Path(recovery.__file__)), "--help"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("record-cover", result.stdout)
        self.assertIn("record", result.stdout)
        self.assertIn("verify", result.stdout)


class PublicAudioRecoveryValidationTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def write_json(self, name: str, value: object) -> Path:
        path = self.root / name
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def test_block_parity_requires_every_anchor_and_monotonic_time(self):
        sidecar = self.write_json(
            "sidecar.json",
            [
                {"blockId": "a", "timestamp": 0.0},
                {"blockId": "b", "timestamp": 1.5},
            ],
        )
        blocks = self.write_json(
            "blocks.json", {"blocks": [{"id": "a"}, {"id": "b"}]}
        )

        self.assertEqual(verify_block_parity(sidecar, blocks), (2, 2))

    def test_block_parity_rejects_unresolved_anchor(self):
        sidecar = self.write_json(
            "sidecar.json", [{"blockId": "missing", "timestamp": 0.0}]
        )
        blocks = self.write_json("blocks.json", {"blocks": [{"id": "present"}]})

        with self.assertRaisesRegex(ValueError, "unresolved anchor"):
            verify_block_parity(sidecar, blocks)

    def test_block_parity_rejects_empty_and_nonmonotonic_sidecars(self):
        blocks = self.write_json("blocks.json", {"blocks": [{"id": "a"}]})
        empty = self.write_json("empty.json", [])
        backwards = self.write_json(
            "backwards.json",
            [
                {"blockId": "a", "timestamp": 2.0},
                {"blockId": "a", "timestamp": 1.0},
            ],
        )

        with self.assertRaisesRegex(ValueError, "non-empty list"):
            verify_block_parity(empty, blocks)
        with self.assertRaisesRegex(ValueError, "monotonic"):
            verify_block_parity(backwards, blocks)

    def test_public_json_rejects_absolute_paths_recursively(self):
        for value in (
            {"source": "/Users/example/archive/book.m4b"},
            {"nested": [{"source": "file:///private/tmp/book.m4b"}]},
            {"source": "C:\\archive\\book.m4b"},
        ):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "absolute path"):
                    validate_public_json(value)

    def test_public_json_accepts_relative_paths_and_hashes(self):
        validate_public_json(
            {
                "path": "books/example/example.m4b",
                "sha256": "0" * 64,
                "counts": [1, 2, 3],
            }
        )


class LegacyCoverPairReceiptTests(unittest.TestCase):
    slug = "fixture-book"

    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.book_dir = Path(self.temporary_directory.name) / self.slug
        self.book_dir.mkdir()
        self._write_image("cover.png", (1600, 2560), (245, 235, 220))
        self._write_image("m4b-cover-source.png", (1024, 1024), (30, 60, 90))
        self._write_image("m4b-cover.png", (2400, 2400), (220, 80, 50))
        self._write_image("m4b-cover-thumbnail.png", (160, 160), (220, 80, 50))
        (self.book_dir / "m4b-cover-spec.json").write_text(
            '{"schema_version":2,"variant":"square"}\n', encoding="utf-8"
        )
        (self.book_dir / "m4b-cover.render.json").write_text(
            '{"renderer_version":1}\n', encoding="utf-8"
        )
        with zipfile.ZipFile(
            self.book_dir / f"{self.slug}.epub", "w", zipfile.ZIP_STORED
        ) as archive:
            archive.write(self.book_dir / "cover.png", "OEBPS/cover.png")

    def tearDown(self):
        self.temporary_directory.cleanup()

    def _write_image(
        self, name: str, dimensions: tuple[int, int], colour: tuple[int, int, int]
    ) -> None:
        Image.new("RGB", dimensions, colour).save(self.book_dir / name)

    def test_writer_creates_a_verifiable_public_pair_receipt(self):
        receipt = recovery.write_legacy_cover_pair(
            self.book_dir, "fixture-direction", "Fixture Direction"
        )

        recovery.verify_legacy_cover_pair(self.book_dir, receipt)
        payload = json.loads(receipt.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["book_slug"], self.slug)
        self.assertEqual(payload["candidate_id"], "fixture-direction")
        self.assertEqual(payload["selection_source"], "user-approved-derivation")
        self.assertEqual(payload["portrait"]["dimensions"], [1600, 2560])
        self.assertEqual(payload["square"]["dimensions"], [2400, 2400])
        self.assertEqual(
            payload["portrait"]["sha256"],
            payload["portrait"]["epub_cover_sha256"],
        )
        validate_public_json(payload)

    def test_verifier_rejects_tampered_square_bytes(self):
        receipt = recovery.write_legacy_cover_pair(
            self.book_dir, "fixture-direction", "Fixture Direction"
        )
        self._write_image("m4b-cover.png", (2400, 2400), (10, 20, 30))

        with self.assertRaisesRegex(ValueError, "square.*hash mismatch"):
            recovery.verify_legacy_cover_pair(self.book_dir, receipt)

    def test_verifier_rejects_epub_cover_drift(self):
        receipt = recovery.write_legacy_cover_pair(
            self.book_dir, "fixture-direction", "Fixture Direction"
        )
        with zipfile.ZipFile(
            self.book_dir / f"{self.slug}.epub", "w", zipfile.ZIP_STORED
        ) as archive:
            archive.writestr("OEBPS/cover.png", b"different")

        with self.assertRaisesRegex(ValueError, "EPUB.*hash mismatch"):
            recovery.verify_legacy_cover_pair(self.book_dir, receipt)

    def test_writer_rejects_invalid_identity(self):
        for candidate_id, direction_name in (
            ("Wrong ID", "Fixture Direction"),
            ("fixture-direction", ""),
        ):
            with self.subTest(candidate_id=candidate_id, direction_name=direction_name):
                with self.assertRaises(ValueError):
                    recovery.write_legacy_cover_pair(
                        self.book_dir, candidate_id, direction_name
                    )


class RecoveryManifestContractTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def write_json(self, name: str, value: object) -> Path:
        path = self.root / name
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def test_builder_rejects_an_incomplete_source_map_before_media_work(self):
        source_map = self.write_json(
            "sources.json",
            {
                "schema_version": 1,
                "books": {
                    "echo-from-the-inside": {
                        "m4b": "/archive/echo.m4b",
                        "sidecar": "/archive/echo.alignment.json",
                    }
                },
            },
        )

        with self.assertRaisesRegex(ValueError, "source map slug set mismatch"):
            recovery.build_recovery_manifest(self.root, source_map, self.root / "blocks")

    def test_verifier_rejects_an_incomplete_public_manifest(self):
        manifest = self.write_json(
            "manifest.json",
            {
                "schema_version": 1,
                "edition_id": "public-audio-recovery-2026-07",
                "books": [],
            },
        )

        with self.assertRaisesRegex(ValueError, "manifest slug order mismatch"):
            recovery.verify_recovery_manifest(self.root, manifest, self.root / "blocks")

    def test_verifier_rejects_absolute_paths_before_file_checks(self):
        books = [
            {
                "slug": slug,
                "final_m4b_path": (
                    "/private/archive/book.m4b"
                    if index == 0
                    else f"books/{slug}/{slug}.m4b"
                ),
            }
            for index, slug in enumerate(recovery.REMUXED_SLUGS)
        ]
        manifest = self.write_json(
            "manifest.json",
            {
                "schema_version": 1,
                "edition_id": "public-audio-recovery-2026-07",
                "books": books,
            },
        )

        with self.assertRaisesRegex(ValueError, "absolute path"):
            recovery.verify_recovery_manifest(self.root, manifest, self.root / "blocks")


class PublicPackageCoverContractTests(unittest.TestCase):
    repo_root = Path(__file__).parents[1]
    required_legacy_assets = (
        "m4b-cover-source.png",
        "m4b-cover-spec.json",
        "m4b-cover.png",
        "m4b-cover-thumbnail.png",
        "m4b-cover.render.json",
        "legacy-cover-pair.json",
    )

    def test_all_six_legacy_packages_have_verified_square_companions(self):
        missing = [
            f"books/{slug}/{name}"
            for slug in recovery.LEGACY_PAIR_SLUGS
            for name in self.required_legacy_assets
            if not (self.repo_root / "books" / slug / name).is_file()
        ]
        self.assertEqual(missing, [], "missing legacy square assets")
        for slug in recovery.LEGACY_PAIR_SLUGS:
            with self.subTest(slug=slug):
                book_dir = self.repo_root / "books" / slug
                recovery.verify_legacy_cover_pair(
                    book_dir, book_dir / "legacy-cover-pair.json"
                )


@unittest.skipUnless(
    shutil.which("ffmpeg")
    and shutil.which("ffprobe")
    and shutil.which("AtomicParsley")
    and (shutil.which("magick") or shutil.which("convert")),
    "media verification tools are required",
)
class RecoveryRecordIntegrationTests(unittest.TestCase):
    slug = "echo-from-the-inside"

    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.book_dir = self.root / "books" / self.slug
        self.book_dir.mkdir(parents=True)
        Image.new("RGB", (1600, 2560), (240, 230, 210)).save(
            self.book_dir / "cover.png"
        )
        Image.new("RGB", (2400, 2400), (30, 90, 140)).save(
            self.book_dir / "m4b-cover.png"
        )
        with zipfile.ZipFile(
            self.book_dir / f"{self.slug}.epub", "w", zipfile.ZIP_STORED
        ) as archive:
            archive.write(self.book_dir / "cover.png", "OEBPS/cover.png")
        self.sidecar = self.root / "source.alignment.json"
        self.sidecar.write_text(
            '[{"blockId":"a","timestamp":0.0}]\n', encoding="utf-8"
        )
        shutil.copy2(
            self.sidecar, self.book_dir / f"{self.slug}.alignment.json"
        )
        self.blocks = self.root / "blocks.json"
        self.blocks.write_text(
            '{"blocks":[{"id":"a","kind":"paragraph"}]}\n',
            encoding="utf-8",
        )
        metadata = self.root / "metadata.txt"
        metadata.write_text(
            ";FFMETADATA1\n"
            "title=Fixture Audio\n"
            "[CHAPTER]\nTIMEBASE=1/1000\nSTART=0\nEND=500\ntitle=One\n",
            encoding="utf-8",
        )
        base = self.root / "base.m4b"
        subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-y",
                "-f",
                "lavfi",
                "-i",
                "sine=frequency=440:duration=0.5",
                "-i",
                str(metadata),
                "-map",
                "0:a:0",
                "-map_metadata",
                "1",
                "-map_chapters",
                "1",
                "-c:a",
                "aac",
                "-b:a",
                "32k",
                str(base),
            ],
            check=True,
        )
        self.source_m4b = self.root / "source.m4b"
        subprocess.run(
            [
                "AtomicParsley",
                str(base),
                "--artwork",
                str(self.book_dir / "cover.png"),
                "--output",
                str(self.source_m4b),
            ],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            [
                sys.executable,
                str(
                    Path(__file__).parents[1]
                    / "skill"
                    / "scripts"
                    / "replace_m4b_cover.py"
                ),
                "--m4b",
                str(self.source_m4b),
                "--cover",
                str(self.book_dir / "m4b-cover.png"),
                "--out",
                str(self.book_dir / f"{self.slug}.m4b"),
            ],
            check=True,
            capture_output=True,
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_record_binds_unchanged_media_sidecar_blocks_and_square_art(self):
        record = recovery.build_recovery_record(
            self.root,
            self.slug,
            self.source_m4b,
            self.sidecar,
            self.blocks,
        )

        self.assertEqual(record["slug"], self.slug)
        self.assertEqual(record["anchor_count"], 1)
        self.assertEqual(record["resolved_anchor_count"], 1)
        self.assertEqual(record["exported_block_count"], 1)
        self.assertEqual(
            record["source_media_signature"], record["final_media_signature"]
        )
        self.assertEqual(
            record["source_sidecar_sha256"], record["final_sidecar_sha256"]
        )
        validate_public_json(record)

    def test_record_rejects_changed_source_sidecar_bytes(self):
        (self.book_dir / f"{self.slug}.alignment.json").write_text(
            '[{"blockId":"a","timestamp":0.25}]\n', encoding="utf-8"
        )

        with self.assertRaisesRegex(ValueError, "sidecar bytes changed"):
            recovery.build_recovery_record(
                self.root,
                self.slug,
                self.source_m4b,
                self.sidecar,
                self.blocks,
            )

    def test_record_verifier_recomputes_current_package_evidence(self):
        record = recovery.build_recovery_record(
            self.root,
            self.slug,
            self.source_m4b,
            self.sidecar,
            self.blocks,
        )

        recovery.verify_recovery_record(self.root, record, self.blocks)
        record["final_m4b_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "final M4B hash mismatch"):
            recovery.verify_recovery_record(self.root, record, self.blocks)


if __name__ == "__main__":
    unittest.main()
