import copy
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
FICTION_DISCLOSURE = (
    "This original AI-generated fiction edition is published under CC BY 4.0 "
    "as a public first-listen. Automated package and audio checks passed; human "
    "reading and listening reviews remain pending."
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
                stdout=json.dumps(
                    {
                        "format": {"duration": "1.0"},
                        "chapters": [
                            {"start_time": "0.0", "end_time": "1.0"}
                        ],
                    }
                ),
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


class FictionPublicPackageVerifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name).resolve()
        self.book_dir = self.root / "public" / "fixture-fiction"
        self.private_dir = self.root / "private"
        self.chapters = self.private_dir / "chapters"
        self.research = self.private_dir / "research"
        self.private_dist = self.private_dir / "dist"
        self.release_m4b = self.root / "release" / "fixture-fiction.m4b"
        self.voice_cast = self.private_dir / "voice-cast.json"
        self.fiction_receipt = self.research / "fiction-production-receipt.json"
        self.cast_chapters = [
            {"chapter": 1, "role": "Mara", "voice": "bf_emma", "experimental": False},
            {"chapter": 2, "role": "Ivo", "voice": "am_michael", "experimental": False},
            {"chapter": 3, "role": "Sera", "voice": "af_bella", "experimental": False},
        ]
        canonical_plan = "default=bf_emma\n1=bf_emma\n2=am_michael\n3=af_bella\n"
        self.voice_plan_sha256 = hashlib.sha256(canonical_plan.encode("utf-8")).hexdigest()
        self.voice_plan_id = f"plan-{self.voice_plan_sha256[:12]}"
        self.renderer_identity = {
            "rendererSchemaVersion": 1,
            "rendererRoot": "/Applications/Echo.app",
            "rendererBuildRoot": "/Applications/Echo.app/Contents/Resources/renderer",
            "installerSourceSHA": "1" * 40,
            "echoSourceSHA": "2" * 40,
            "rendererManifestSHA256": "3" * 64,
            "echoCLI_SHA256": "4" * 64,
            "echoResourcesSHA256": "5" * 64,
            "echoRenderVersion": 12,
            "modelPolicyRevision": "fixture-policy-v1",
            "modelExpectedByteCount": 123456,
            "modelBytesAttested": False,
        }
        for directory in (
            self.book_dir,
            self.chapters,
            self.research,
            self.private_dist,
            self.release_m4b.parent,
            self.private_dir / "continuity",
            self.private_dir / "revisions",
        ):
            directory.mkdir(parents=True, exist_ok=True)

        self.manuscript = self.book_dir / "fixture-fiction.md"
        self.epub = self.book_dir / "fixture-fiction.epub"
        self.sidecar = self.book_dir / "fixture-fiction.alignment.json"
        self.cover = self.book_dir / "cover.png"
        self.manuscript.write_text("# Fixture Fiction\n", encoding="utf-8")
        self.epub.write_bytes(b"epub fixture")
        self.sidecar.write_text('[{"blockId":"b1","timestamp":0}]\n', encoding="utf-8")
        self.cover.write_bytes(b"portrait cover")
        self.release_m4b.write_bytes(b"release audiobook")
        self.private_manuscript = self.private_dist / self.manuscript.name
        self.private_epub = self.private_dist / self.epub.name
        self.private_manuscript.write_bytes(self.manuscript.read_bytes())
        self.private_epub.write_bytes(self.epub.read_bytes())
        self.run_id = (
            f"{self.digest(self.epub)[:12]}-"
            f"{self.renderer_identity['echoCLI_SHA256'][:12]}-"
            f"{self.renderer_identity['echoResourcesSHA256'][:12]}-"
            f"{self.renderer_identity['rendererManifestSHA256'][:12]}-"
            f"{self.renderer_identity['echoSourceSHA']}-{self.voice_plan_id}"
        )
        self.attempt_id = "7" * 64
        self.echo_success_receipt = self.research / (
            f"echo-render-success-{self.run_id}-{self.attempt_id}.json"
        )

        self.chapter = self.chapters / "ch01.md"
        self.chapter.write_text("## Chapter One\n\nThe lamp survived.\n", encoding="utf-8")
        self.fiction_artifacts = {
            "authorization": self.research / "unattended-decisions.json",
            "storyBible": self.private_dir / "story-bible.md",
            "continuity": self.private_dir / "continuity" / "final.md",
            "revisionReview": self.private_dir / "revisions" / "review.md",
            "proseQC": self.private_dir / "revisions" / "prose-qc.md",
        }
        for name, path in self.fiction_artifacts.items():
            path.write_text(f"{name}: verified\n", encoding="utf-8")
        self.write_fiction_receipt()

        self.write_echo_success_receipt()
        self.write_voice_cast()
        self.receipt = self.valid_publication_receipt()
        self.write_publication_receipt()
        (self.book_dir / "README.md").write_text(FICTION_DISCLOSURE, encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    @staticmethod
    def digest(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def write_fiction_receipt(self) -> None:
        payload = {
            "schemaVersion": 1,
            "status": "first-listen",
            "productionMode": "unattended-first-listen",
            "privacy": "private",
            "permissionToPublish": False,
            "humanReadingStatus": "pending",
            "canonicalChapterSHA256": {self.chapter.name: self.digest(self.chapter)},
            "buildOutputs": {
                "slug": "fixture-fiction",
                "manuscript": {
                    "path": str(self.private_manuscript.relative_to(self.private_dir)),
                    "sha256": self.digest(self.private_manuscript),
                },
                "epub": {
                    "path": str(self.private_epub.relative_to(self.private_dir)),
                    "sha256": self.digest(self.private_epub),
                },
            },
            "artifacts": {
                name: {
                    "path": str(path.relative_to(self.private_dir)),
                    "sha256": self.digest(path),
                }
                for name, path in self.fiction_artifacts.items()
            },
            "gates": {
                "manuscriptClosed": "pass",
                "storyBibleReconciled": "pass",
                "continuityReconciled": "pass",
                "revisionPassesCompleted": "pass",
                "proseQCPassed": "pass",
            },
            "negativeHumanVerdictOverrides": True,
            "receiptDoesNotCertifyHumanAcceptance": True,
        }
        self.fiction_receipt.write_text(
            json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8"
        )

    def write_echo_success_receipt(self) -> None:
        payload = {
            "schemaVersion": 3,
            **self.renderer_identity,
            "attemptID": self.attempt_id,
            "runID": self.run_id,
            "attemptReceiptSHA256": "8" * 64,
            "inputReceiptFileName": f"echo-render-inputs-{self.run_id}.env",
            "inputReceiptSHA256": "9" * 64,
            "sourceEPUBFileName": self.epub.name,
            "sourceEPUBSHA256": self.digest(self.epub),
            "artifactRelativePath": f"echo-renders/{self.run_id}/{self.attempt_id}",
            "resumeStateFileName": f"echo-resume-state-{self.run_id}.json",
            "resumeStateSHA256": "a" * 64,
            "audiobookFileName": self.release_m4b.name,
            "audiobookSHA256": self.digest(self.release_m4b),
            "sidecarFileName": self.sidecar.name,
            "sidecarSHA256": self.digest(self.sidecar),
            "auditFileName": "fixture-fiction.pronunciation-audit.json",
            "auditSHA256": "b" * 64,
        }
        self.echo_success_receipt.write_text(
            json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8"
        )

    def write_voice_cast(self) -> None:
        payload = {
            "schemaVersion": 1,
            "slug": "fixture-fiction",
            "chapterCount": 3,
            "defaultVoice": "bf_emma",
            "chapters": self.cast_chapters,
            "voicePlanSHA256": self.voice_plan_sha256,
            "voicePlanID": self.voice_plan_id,
            "verifiedArtifacts": {
                "sourceEPUBSHA256": self.digest(self.epub),
                "audiobookSHA256": self.digest(self.release_m4b),
                "sidecarSHA256": self.digest(self.sidecar),
                "voicePlanSHA256": self.voice_plan_sha256,
            },
        }
        self.voice_cast.write_text(
            json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8"
        )

    def valid_publication_receipt(self) -> dict[str, object]:
        return {
            "schemaVersion": 2,
            "packageKind": "fiction-audiobook",
            "slug": "fixture-fiction",
            "editionId": "first-listen-2026-08-08",
            "publicationStatus": "public-first-listen",
            "humanReadingStatus": "pending",
            "humanListeningStatus": "pending",
            "classification": "public-safe",
            "permissionToPublish": True,
            "permissionGrantedAt": "2026-08-08T12:00:00+00:00",
            "author": "Dan Fakkeldy",
            "contributor": "GPT-5.6",
            "aiGenerated": True,
            "contentLicense": "CC-BY-4.0",
            "disclosure": FICTION_DISCLOSURE,
            "publicGate": {
                "originalFiction": True,
                "noPrivateSource": True,
                "noLivingPersonTarget": True,
                "noLivingAuthorImitation": True,
                "coverRightsVerified": True,
            },
            "coverRights": {
                "basis": "generated",
                "status": "verified",
                "coverSHA256": self.digest(self.cover),
            },
            "artifacts": {
                "manuscript": {"file": self.manuscript.name, "sha256": self.digest(self.manuscript)},
                "epub": {"file": self.epub.name, "sha256": self.digest(self.epub)},
                "alignment": {"file": self.sidecar.name, "sha256": self.digest(self.sidecar)},
                "portraitCover": {"file": self.cover.name, "sha256": self.digest(self.cover)},
            },
            "release": {
                "tag": "fiction-fixture-fiction-first-listen-2026-08-08",
                "assetFile": self.release_m4b.name,
                "assetSHA256": self.digest(self.release_m4b),
            },
            "privateEvidence": {
                "fictionReceiptSHA256": self.digest(self.fiction_receipt),
                "voiceCastSHA256": self.digest(self.voice_cast),
                "voicePlanSHA256": self.voice_plan_sha256,
                "echoSuccessReceiptSHA256": self.digest(self.echo_success_receipt),
            },
        }

    def write_publication_receipt(self) -> None:
        (self.book_dir / "publication.json").write_text(
            json.dumps(self.receipt, sort_keys=True) + "\n", encoding="utf-8"
        )

    def rebind_changed_public_epub(self) -> None:
        epub_hash = self.digest(self.epub)
        self.receipt["artifacts"]["epub"]["sha256"] = epub_hash
        cast = json.loads(self.voice_cast.read_text(encoding="utf-8"))
        cast["verifiedArtifacts"]["sourceEPUBSHA256"] = epub_hash
        self.voice_cast.write_text(
            json.dumps(cast, sort_keys=True) + "\n", encoding="utf-8"
        )
        self.receipt["privateEvidence"]["voiceCastSHA256"] = self.digest(
            self.voice_cast
        )

        success = json.loads(self.echo_success_receipt.read_text(encoding="utf-8"))
        changed_run_id = (
            f"{epub_hash[:12]}-"
            f"{self.renderer_identity['echoCLI_SHA256'][:12]}-"
            f"{self.renderer_identity['echoResourcesSHA256'][:12]}-"
            f"{self.renderer_identity['rendererManifestSHA256'][:12]}-"
            f"{self.renderer_identity['echoSourceSHA']}-{self.voice_plan_id}"
        )
        success["runID"] = changed_run_id
        success["inputReceiptFileName"] = f"echo-render-inputs-{changed_run_id}.env"
        success["sourceEPUBSHA256"] = epub_hash
        success["artifactRelativePath"] = (
            f"echo-renders/{changed_run_id}/{self.attempt_id}"
        )
        success["resumeStateFileName"] = f"echo-resume-state-{changed_run_id}.json"
        changed_path = self.research / (
            f"echo-render-success-{changed_run_id}-{self.attempt_id}.json"
        )
        self.echo_success_receipt.unlink()
        self.echo_success_receipt = changed_path
        self.echo_success_receipt.write_text(
            json.dumps(success, sort_keys=True) + "\n", encoding="utf-8"
        )
        self.receipt["privateEvidence"]["echoSuccessReceiptSHA256"] = self.digest(
            self.echo_success_receipt
        )
        self.write_publication_receipt()

    def probes(self):
        return mock.patch.object(
            verifier.subprocess,
            "run",
            return_value=subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout=json.dumps(
                    {
                        "format": {"duration": "1.0"},
                        "chapters": [
                            {"start_time": "0.0", "end_time": "1.0"}
                        ],
                    }
                ),
                stderr="",
            ),
        )

    def verify(self) -> None:
        verifier.verify_public_fiction_package(
            self.book_dir,
            self.release_m4b,
            self.voice_cast,
            self.fiction_receipt,
            self.chapters,
            self.echo_success_receipt,
        )

    def assert_rejected(self, pattern: str) -> None:
        with self.probes(), self.assertRaisesRegex(ValueError, pattern):
            self.verify()

    def test_accepts_release_backed_fiction_with_exact_public_surface(self) -> None:
        self.assertEqual(
            {
                "README.md",
                "fixture-fiction.md",
                "fixture-fiction.epub",
                "fixture-fiction.alignment.json",
                "cover.png",
                "publication.json",
            },
            {path.name for path in self.book_dir.iterdir()},
        )
        with self.probes():
            self.verify()

    def test_rejects_forged_minimal_echo_receipt_without_governed_provenance(self) -> None:
        forged = {
            "schemaVersion": 3,
            "sourceEPUBFileName": self.epub.name,
            "sourceEPUBSHA256": self.digest(self.epub),
            "audiobookFileName": self.release_m4b.name,
            "audiobookSHA256": self.digest(self.release_m4b),
            "sidecarFileName": self.sidecar.name,
            "sidecarSHA256": self.digest(self.sidecar),
            "voicePlanSHA256": self.voice_plan_sha256,
        }
        self.echo_success_receipt.write_text(
            json.dumps(forged, sort_keys=True) + "\n", encoding="utf-8"
        )
        self.receipt["privateEvidence"]["echoSuccessReceiptSHA256"] = self.digest(
            self.echo_success_receipt
        )
        self.write_publication_receipt()
        self.assert_rejected("provenance|renderer|attempt|run")

    def test_rejects_echo_run_id_not_derived_from_source_and_renderer(self) -> None:
        success = json.loads(self.echo_success_receipt.read_text(encoding="utf-8"))
        changed_run_id = f"{'f' * 12}-{self.run_id.split('-', 1)[1]}"
        success["runID"] = changed_run_id
        success["inputReceiptFileName"] = f"echo-render-inputs-{changed_run_id}.env"
        success["artifactRelativePath"] = (
            f"echo-renders/{changed_run_id}/{self.attempt_id}"
        )
        success["resumeStateFileName"] = f"echo-resume-state-{changed_run_id}.json"
        changed_path = self.research / (
            f"echo-render-success-{changed_run_id}-{self.attempt_id}.json"
        )
        self.echo_success_receipt.unlink()
        self.echo_success_receipt = changed_path
        self.echo_success_receipt.write_text(
            json.dumps(success, sort_keys=True) + "\n", encoding="utf-8"
        )
        self.receipt["privateEvidence"]["echoSuccessReceiptSHA256"] = self.digest(
            self.echo_success_receipt
        )
        self.write_publication_receipt()
        self.assert_rejected("runID.*source|runID.*renderer")

    def test_rejects_completed_cast_that_breaks_the_immutable_contract(self) -> None:
        cast = json.loads(self.voice_cast.read_text(encoding="utf-8"))
        cast["chapters"][2]["voice"] = "not_a_voice"
        self.voice_cast.write_text(
            json.dumps(cast, sort_keys=True) + "\n", encoding="utf-8"
        )
        self.receipt["privateEvidence"]["voiceCastSHA256"] = self.digest(
            self.voice_cast
        )
        self.write_publication_receipt()
        self.assert_rejected("unknown Echo voice")

    def test_rejects_public_manuscript_substituted_after_private_build(self) -> None:
        self.manuscript.write_text("# Unrelated substituted story\n", encoding="utf-8")
        self.receipt["artifacts"]["manuscript"]["sha256"] = self.digest(
            self.manuscript
        )
        self.write_publication_receipt()
        self.assert_rejected("private build.*manuscript|manuscript.*private build")

    def test_rejects_public_epub_substituted_after_private_build(self) -> None:
        self.epub.write_bytes(b"unrelated substituted EPUB")
        self.rebind_changed_public_epub()
        self.assert_rejected("private build.*EPUB|EPUB.*private build")

    def test_rejects_local_audio_square_cover_extra_item_or_directory(self) -> None:
        for name, directory in (
            ("fixture-fiction.m4b", False),
            ("m4b-cover.png", False),
            ("seventh.txt", False),
            ("assets", True),
        ):
            with self.subTest(name=name):
                path = self.book_dir / name
                path.mkdir() if directory else path.write_bytes(b"not public")
                self.assert_rejected("exactly|unexpected|root")
                path.rmdir() if directory else path.unlink()

    def test_rejects_mismatched_release_cast_plan_receipts_chapter_cover_or_artifact(self) -> None:
        mutations = (
            ("release", lambda: self.release_m4b.write_bytes(b"changed audio"), "release|M4B|SHA-256"),
            ("cast", lambda: self.voice_cast.write_text(self.voice_cast.read_text() + " "), "voice cast|SHA-256"),
            ("plan", lambda: self.receipt["privateEvidence"].__setitem__("voicePlanSHA256", "e" * 64), "voice-plan|voicePlan"),
            ("fiction receipt", lambda: self.fiction_receipt.write_text(self.fiction_receipt.read_text() + " "), "fiction receipt|SHA-256"),
            ("chapter", lambda: self.chapter.write_text("changed chapter", encoding="utf-8"), "chapter hash"),
            ("cover rights", lambda: self.receipt["coverRights"].__setitem__("coverSHA256", "e" * 64), "cover"),
            ("artifact", lambda: self.receipt["artifacts"]["epub"].__setitem__("sha256", "e" * 64), "epub|EPUB|SHA-256"),
        )
        for name, mutate, pattern in mutations:
            with self.subTest(name=name):
                original_receipt = copy.deepcopy(self.receipt)
                file_snapshots = {
                    path: path.read_bytes()
                    for path in (self.release_m4b, self.voice_cast, self.fiction_receipt, self.chapter)
                }
                mutate()
                self.write_publication_receipt()
                self.assert_rejected(pattern)
                self.receipt = original_receipt
                for path, payload in file_snapshots.items():
                    path.write_bytes(payload)

    def test_rejects_any_false_public_gate(self) -> None:
        for field in tuple(self.receipt["publicGate"]):
            with self.subTest(field=field):
                self.receipt["publicGate"][field] = False
                self.write_publication_receipt()
                self.assert_rejected(field)
                self.receipt["publicGate"][field] = True

    def test_rejects_nonpending_human_states(self) -> None:
        for field in ("humanReadingStatus", "humanListeningStatus"):
            with self.subTest(field=field):
                self.receipt[field] = "accepted"
                self.write_publication_receipt()
                self.assert_rejected(field)
                self.receipt[field] = "pending"

    def test_rejects_inaccurate_public_metadata_and_disclosure(self) -> None:
        cases = (
            ("author", "Someone Else", "author"),
            ("contributor", "", "contributor"),
            ("aiGenerated", False, "aiGenerated"),
            ("contentLicense", "proprietary", "license|contentLicense"),
            ("disclosure", "close enough", "disclosure"),
        )
        for field, value, pattern in cases:
            with self.subTest(field=field):
                original = self.receipt[field]
                self.receipt[field] = value
                self.write_publication_receipt()
                self.assert_rejected(pattern)
                self.receipt[field] = original

    def test_accepts_only_supported_cover_rights_bases_with_required_provenance(self) -> None:
        for basis in (
            "original",
            "generated",
            "public-domain",
            "permissively-licensed",
            "explicit-permission",
        ):
            with self.subTest(basis=basis):
                self.receipt["coverRights"]["basis"] = basis
                if basis in {"permissively-licensed", "explicit-permission"}:
                    self.receipt["coverRights"]["provenanceNote"] = "Documented rights grant."
                else:
                    self.receipt["coverRights"].pop("provenanceNote", None)
                self.write_publication_receipt()
                with self.probes():
                    self.verify()

        self.receipt["coverRights"]["basis"] = "found-online"
        self.write_publication_receipt()
        self.assert_rejected("basis")
        for basis in ("permissively-licensed", "explicit-permission"):
            with self.subTest(missing_provenance=basis):
                self.receipt["coverRights"]["basis"] = basis
                self.receipt["coverRights"].pop("provenanceNote", None)
                self.write_publication_receipt()
                self.assert_rejected("provenance")

    def test_rejects_nonexact_schema_v2_objects_and_underived_release_tag(self) -> None:
        mutations = (
            ("top-level", lambda receipt: receipt.__setitem__("extra", True)),
            (
                "artifact record",
                lambda receipt: receipt["artifacts"]["epub"].__setitem__(
                    "extra", "self-attested"
                ),
            ),
            (
                "release record",
                lambda receipt: receipt["release"].__setitem__("extra", True),
            ),
            (
                "private evidence record",
                lambda receipt: receipt["privateEvidence"].__setitem__(
                    "extra", "f" * 64
                ),
            ),
            (
                "cover rights record",
                lambda receipt: receipt["coverRights"].__setitem__(
                    "provenanceNote", "not valid for generated art"
                ),
            ),
            (
                "release tag",
                lambda receipt: receipt["release"].__setitem__(
                    "tag", "fiction-unrelated-edition"
                ),
            ),
        )
        for label, mutate in mutations:
            with self.subTest(label=label):
                original = copy.deepcopy(self.receipt)
                mutate(self.receipt)
                self.write_publication_receipt()
                self.assert_rejected("exact|tag|coverRights|privateEvidence")
                self.receipt = original

    def test_rejects_absolute_or_file_url_values_in_public_json(self) -> None:
        for value in (
            "/private/evidence",
            "file:///private/evidence",
            "C:\\private\\evidence",
            "\\\\server\\share\\private",
            "\\\\?\\C:\\private\\evidence",
            "\\\\.\\PhysicalDrive0",
        ):
            with self.subTest(value=value):
                self.receipt["unexpected"] = {"path": value}
                self.write_publication_receipt()
                try:
                    self.assert_rejected("absolute path")
                finally:
                    self.receipt.pop("unexpected")

        self.sidecar.write_text('[{"path":"file:///private/alignment"}]', encoding="utf-8")
        sidecar_hash = self.digest(self.sidecar)
        self.receipt["artifacts"]["alignment"]["sha256"] = sidecar_hash
        cast = json.loads(self.voice_cast.read_text(encoding="utf-8"))
        cast["verifiedArtifacts"]["sidecarSHA256"] = sidecar_hash
        self.voice_cast.write_text(json.dumps(cast, sort_keys=True) + "\n", encoding="utf-8")
        success = json.loads(self.echo_success_receipt.read_text(encoding="utf-8"))
        success["sidecarSHA256"] = sidecar_hash
        self.echo_success_receipt.write_text(
            json.dumps(success, sort_keys=True) + "\n", encoding="utf-8"
        )
        self.receipt["privateEvidence"]["voiceCastSHA256"] = self.digest(self.voice_cast)
        self.receipt["privateEvidence"]["echoSuccessReceiptSHA256"] = self.digest(
            self.echo_success_receipt
        )
        self.write_publication_receipt()
        self.assert_rejected("absolute path")

    def test_rejects_duplicate_keys_in_every_evidence_json(self) -> None:
        evidence = (
            (self.book_dir / "publication.json", '{"schemaVersion":2,"schemaVersion":2}'),
            (self.voice_cast, '{"schemaVersion":1,"schemaVersion":1}'),
            (self.fiction_receipt, '{"schemaVersion":1,"schemaVersion":1}'),
            (self.echo_success_receipt, '{"schemaVersion":3,"schemaVersion":3}'),
            (self.sidecar, '[{"blockId":"b1","blockId":"b1"}]'),
        )
        for path, payload in evidence:
            with self.subTest(path=path.name):
                original = path.read_bytes()
                path.write_text(payload, encoding="utf-8")
                self.assert_rejected("duplicate JSON key")
                path.write_bytes(original)

    def test_rejects_nonfinite_numbers_in_json(self) -> None:
        publication_path = self.book_dir / "publication.json"
        for value in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(value=value):
                publication_path.write_text(
                    '{"schemaVersion":2,"unsafe":' + value + "}", encoding="utf-8"
                )
                self.assert_rejected("non-finite JSON number")
        self.write_publication_receipt()
        self.sidecar.write_text("[NaN]", encoding="utf-8")
        self.assert_rejected("non-finite JSON number")

    def test_rejects_nonfinite_or_nonpositive_media_duration(self) -> None:
        for duration in ("Infinity", "NaN", "0", "-1"):
            with self.subTest(duration=duration), mock.patch.object(
                verifier.subprocess,
                "run",
                return_value=subprocess.CompletedProcess(
                    args=[],
                    returncode=0,
                    stdout=json.dumps(
                        {
                            "format": {"duration": duration},
                            "chapters": [
                                {"start_time": "0.0", "end_time": "1.0"}
                            ],
                        }
                    ),
                    stderr="",
                ),
            ), self.assertRaisesRegex(ValueError, "duration"):
                self.verify()

    def test_rejects_malformed_ffprobe_types_and_chapter_records(self) -> None:
        malformed_media = (
            {"format": {"duration": True}, "chapters": [{"start_time": "0", "end_time": "1"}]},
            {"format": {"duration": 1}, "chapters": [{"start_time": "0", "end_time": "1"}]},
            {"format": {"duration": "1"}, "chapters": [{}]},
            {"format": {"duration": "1"}, "chapters": [{"start_time": 0, "end_time": "1"}]},
            {"format": {"duration": "1"}, "chapters": [{"start_time": "1", "end_time": "1"}]},
            {"format": {"duration": "1"}, "chapters": [{"start_time": "0", "end_time": "1", "extra": True}]},
            {"format": {"duration": "1", "extra": True}, "chapters": [{"start_time": "0", "end_time": "1"}]},
            {"format": {"duration": "1"}, "chapters": [{"start_time": "0", "end_time": "1"}], "extra": True},
        )
        for media in malformed_media:
            with self.subTest(media=media), mock.patch.object(
                verifier.subprocess,
                "run",
                return_value=subprocess.CompletedProcess(
                    args=[], returncode=0, stdout=json.dumps(media), stderr=""
                ),
            ), self.assertRaisesRegex(ValueError, "ffprobe|duration|chapter"):
                self.verify()

    def test_rejects_epub_or_release_replaced_during_external_probe(self) -> None:
        for target in ("epub", "release"):
            with self.subTest(target=target):
                epub_bytes = self.epub.read_bytes()
                release_bytes = self.release_m4b.read_bytes()

                def substitute(command, **_kwargs):
                    if target == "epub" and command[0] == "unzip":
                        self.epub.write_bytes(b"replacement during unzip")
                    if target == "release" and command[0] == "ffprobe":
                        self.release_m4b.write_bytes(b"replacement during ffprobe")
                    return subprocess.CompletedProcess(
                        args=command,
                        returncode=0,
                        stdout=json.dumps(
                            {
                                "format": {"duration": "1.0"},
                                "chapters": [
                                    {"start_time": "0.0", "end_time": "1.0"}
                                ],
                            }
                        ),
                        stderr="",
                    )

                try:
                    with mock.patch.object(
                        verifier.subprocess, "run", side_effect=substitute
                    ), self.assertRaisesRegex(
                        ValueError, "changed during verification"
                    ):
                        self.verify()
                finally:
                    self.epub.write_bytes(epub_bytes)
                    self.release_m4b.write_bytes(release_bytes)

    def test_rejects_voice_cast_replaced_between_parse_and_hash(self) -> None:
        changed_cast = json.loads(self.voice_cast.read_text(encoding="utf-8"))
        changed_cast["chapters"][0]["voice"] = "not_a_voice"
        changed_bytes = (json.dumps(changed_cast, sort_keys=True) + "\n").encode()
        self.receipt["privateEvidence"]["voiceCastSHA256"] = hashlib.sha256(
            changed_bytes
        ).hexdigest()
        self.write_publication_receipt()
        real_loads = verifier.json.loads
        replaced = False

        def substitute_after_parse(payload, *args, **kwargs):
            nonlocal replaced
            value = real_loads(payload, *args, **kwargs)
            if not replaced and isinstance(value, dict) and "voicePlanID" in value:
                replacement = self.root / "replacement-voice-cast.json"
                replacement.write_bytes(changed_bytes)
                replacement.replace(self.voice_cast)
                replaced = True
            return value

        with mock.patch.object(
            verifier.json, "loads", side_effect=substitute_after_parse
        ), self.probes(), self.assertRaisesRegex(
            ValueError, "changed during verification|voice cast SHA-256"
        ):
            self.verify()

    def test_rejects_public_and_external_evidence_symlinks(self) -> None:
        external_cover = self.root / "external-cover.png"
        external_cover.write_bytes(self.cover.read_bytes())
        self.cover.unlink()
        self.cover.symlink_to(external_cover)
        self.assert_rejected("symlink")

        self.cover.unlink()
        self.cover.write_bytes(external_cover.read_bytes())
        target_cast = self.root / "target-cast.json"
        target_cast.write_bytes(self.voice_cast.read_bytes())
        self.voice_cast.unlink()
        self.voice_cast.symlink_to(target_cast)
        self.assert_rejected("symlink")

    def test_rejects_symlink_ancestors_for_public_root_and_all_evidence(self) -> None:
        public_alias = self.root / "public-alias"
        public_alias.symlink_to(self.book_dir.parent, target_is_directory=True)
        with self.probes(), self.assertRaisesRegex(ValueError, "symlink ancestor"):
            verifier.verify_public_fiction_package(
                public_alias / self.book_dir.name,
                self.release_m4b,
                self.voice_cast,
                self.fiction_receipt,
                self.chapters,
                self.echo_success_receipt,
            )

        evidence_cases = {
            "release": self.root / "release-alias" / self.release_m4b.name,
            "cast": self.root / "private-alias" / self.voice_cast.name,
            "fiction": self.root / "private-alias" / "research" / self.fiction_receipt.name,
            "chapters": self.root / "private-alias" / self.chapters.name,
            "echo": self.root / "private-alias" / "research" / self.echo_success_receipt.name,
        }
        (self.root / "release-alias").symlink_to(
            self.release_m4b.parent, target_is_directory=True
        )
        (self.root / "private-alias").symlink_to(
            self.private_dir, target_is_directory=True
        )
        originals = {
            "release": self.release_m4b,
            "cast": self.voice_cast,
            "fiction": self.fiction_receipt,
            "chapters": self.chapters,
            "echo": self.echo_success_receipt,
        }
        for label, aliased_path in evidence_cases.items():
            with self.subTest(label=label):
                paths = dict(originals)
                paths[label] = aliased_path
                with self.probes(), self.assertRaisesRegex(
                    ValueError, "symlink ancestor"
                ):
                    verifier.verify_public_fiction_package(
                        self.book_dir,
                        paths["release"],
                        paths["cast"],
                        paths["fiction"],
                        paths["chapters"],
                        paths["echo"],
                    )

    def test_cli_rejects_partial_evidence_and_accepts_all_evidence(self) -> None:
        self.assertEqual(
            64,
            verifier.main(
                [str(self.book_dir), "--release-m4b", str(self.release_m4b)]
            ),
        )
        with self.probes():
            self.assertEqual(
                0,
                verifier.main(
                    [
                        str(self.book_dir),
                        "--release-m4b", str(self.release_m4b),
                        "--voice-cast", str(self.voice_cast),
                        "--fiction-receipt", str(self.fiction_receipt),
                        "--chapters-dir", str(self.chapters),
                        "--echo-success-receipt", str(self.echo_success_receipt),
                    ]
                ),
            )
