import copy
import hashlib
import json
import os
import shutil
import stat
import struct
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
            self.release_m4b.parent,
            self.private_dir / "continuity",
            self.private_dir / "revisions",
        ):
            directory.mkdir(parents=True, exist_ok=True)

        self.manuscript = self.book_dir / "fixture-fiction.md"
        self.epub = self.book_dir / "fixture-fiction.epub"
        self.sidecar = self.book_dir / "fixture-fiction.alignment.json"
        self.cover = self.book_dir / "cover.png"
        self.cover.write_bytes(b"portrait cover")
        self.epub_uid = "urn:uuid:00000000-0000-4000-8000-000000000001"
        self.chapter_specs = (
            ("ch01.md", "Chapter One", "The lamp survived."),
            ("ch02.md", "Chapter Two", "The tide withdrew."),
            ("ch03.md", "Chapter Three", "The signal answered."),
        )
        self.chapter_paths = []
        for filename, title, body in self.chapter_specs:
            chapter_path = self.chapters / filename
            chapter_path.write_text(f"## {title}\n\n{body}\n", encoding="utf-8")
            self.chapter_paths.append(chapter_path)
        self.chapter = self.chapter_paths[0]
        self.write_public_story_outputs()
        self.sidecar.write_text('[{"blockId":"b1","timestamp":0}]\n', encoding="utf-8")
        self.release_m4b.write_bytes(b"release audiobook")
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

        self.fiction_artifacts = {
            "authorization": self.research / "unattended-decisions.json",
            "storyBible": self.private_dir / "story-bible.md",
            "continuity": self.private_dir / "continuity" / "final.md",
            "revisionReview": self.private_dir
            / "revisions"
            / "full-manuscript-review.md",
            "proseQC": self.private_dir / "revisions" / "full-prose-qc.md",
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

    def write_public_story_outputs(self) -> None:
        lines = [
            "# Fixture Fiction",
            "",
            "by Dan Fakkeldy",
            "",
            "Roughly 9 words.",
            "",
            "---",
            "",
        ]
        for _filename, title, body in self.chapter_specs:
            lines.extend([f"## {title}", "", body, "", "---", ""])
        self.manuscript.write_text("\n".join(lines), encoding="utf-8")

        container = (
            '<?xml version="1.0" encoding="utf-8"?>'
            '<container version="1.0" '
            'xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
            '<rootfiles><rootfile full-path="OEBPS/content.opf" '
            'media-type="application/oebps-package+xml"/></rootfiles></container>'
        )
        manifest = [
            '<item id="cover-image" href="cover.png" media-type="image/png" properties="cover-image"/>',
            '<item id="coverpage" href="cover.xhtml" media-type="application/xhtml+xml"/>',
            '<item id="css" href="style.css" media-type="text/css"/>',
            '<item id="titlepage" href="titlepage.xhtml" media-type="application/xhtml+xml"/>',
            '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
            '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>',
        ]
        spine = ['<itemref idref="coverpage"/>', '<itemref idref="titlepage"/>']
        chapter_documents = {}
        for index, (_filename, title, body) in enumerate(self.chapter_specs):
            item_id = f"chap{index:02d}"
            href = f"{item_id}.xhtml"
            manifest.append(
                f'<item id="{item_id}" href="{href}" media-type="application/xhtml+xml"/>'
            )
            spine.append(f'<itemref idref="{item_id}"/>')
            chapter_documents[f"OEBPS/{href}"] = (
                '<?xml version="1.0" encoding="utf-8"?>'
                '<!DOCTYPE html>'
                '<html xmlns="http://www.w3.org/1999/xhtml" '
                'xmlns:epub="http://www.idpf.org/2007/ops" lang="en">'
                f'<head><meta charset="utf-8"/><title>{title}</title>'
                '<link rel="stylesheet" type="text/css" href="style.css"/></head><body>'
                f'<section epub:type="chapter"><h1>{title}</h1><p>{body}</p>'
                '</section></body></html>'
            )
        opf = (
            '<?xml version="1.0" encoding="utf-8"?>'
            '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" '
            'unique-identifier="bookid"><metadata '
            'xmlns:dc="http://purl.org/dc/elements/1.1/">'
            f'<dc:identifier id="bookid">{self.epub_uid}</dc:identifier>'
            '<dc:title>Fixture Fiction</dc:title>'
            '<dc:creator>Dan Fakkeldy</dc:creator>'
            '<dc:contributor>GPT-5.6</dc:contributor><dc:language>en</dc:language>'
            '<meta property="dcterms:modified">2026-01-01T00:00:00Z</meta>'
            '<meta name="cover" content="cover-image"/>'
            '</metadata>'
            '<manifest>' + "".join(manifest) + '</manifest>'
            '<spine toc="ncx">' + "".join(spine) + '</spine></package>'
        )
        titlepage = (
            '<?xml version="1.0" encoding="utf-8"?>'
            '<!DOCTYPE html>'
            '<html xmlns="http://www.w3.org/1999/xhtml" '
            'xmlns:epub="http://www.idpf.org/2007/ops" lang="en"><head>'
            '<meta charset="utf-8"/><title>Fixture Fiction</title>'
            '<link rel="stylesheet" type="text/css" href="style.css"/></head><body>'
            '<section epub:type="titlepage" class="title-page">'
            '<h1>Fixture Fiction</h1><p class="author">by Dan Fakkeldy</p>'
            '</section></body></html>'
        )
        coverpage = (
            '<?xml version="1.0" encoding="utf-8"?>'
            '<!DOCTYPE html>'
            '<html xmlns="http://www.w3.org/1999/xhtml" '
            'xmlns:epub="http://www.idpf.org/2007/ops" lang="en"><head>'
            '<meta charset="utf-8"/><title>Cover</title>'
            '<style>html,body{margin:0;padding:0;height:100%}'
            'img{display:block;width:100%;height:auto}</style></head><body>'
            '<section epub:type="cover"><img src="cover.png" '
            'alt="Fixture Fiction cover"/></section></body></html>'
        )
        nav_items = "".join(
            f'<li><a href="chap{index:02d}.xhtml">{title}</a></li>'
            for index, (_filename, title, _body) in enumerate(self.chapter_specs)
        )
        nav = (
            '<?xml version="1.0" encoding="utf-8"?>'
            '<!DOCTYPE html>'
            '<html xmlns="http://www.w3.org/1999/xhtml" '
            'xmlns:epub="http://www.idpf.org/2007/ops" lang="en"><head>'
            '<meta charset="utf-8"/><title>Table of Contents</title>'
            '<link rel="stylesheet" type="text/css" href="style.css"/></head><body>'
            '<nav epub:type="toc" id="toc"><h1>Table of Contents</h1><ol>'
            + nav_items
            + '</ol></nav></body></html>'
        )
        navpoints = "".join(
            '<navPoint id="np{index}" playOrder="{order}">'
            '<navLabel><text>{title}</text></navLabel>'
            '<content src="chap{index:02d}.xhtml"/></navPoint>'.format(
                index=index,
                order=index + 1,
                title=title,
            )
            for index, (_filename, title, _body) in enumerate(self.chapter_specs)
        )
        ncx = (
            '<?xml version="1.0" encoding="utf-8"?>'
            '<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">'
            f'<head><meta name="dtb:uid" content="{self.epub_uid}"/></head>'
            '<docTitle><text>Fixture Fiction</text></docTitle><navMap>'
            + navpoints
            + '</navMap></ncx>'
        )
        with zipfile.ZipFile(self.epub, "w") as archive:
            archive.writestr(
                "mimetype",
                "application/epub+zip",
                compress_type=zipfile.ZIP_STORED,
            )
            archive.writestr("META-INF/container.xml", container)
            archive.writestr("OEBPS/style.css", verifier._BUILDER_EPUB_CSS)
            archive.writestr("OEBPS/content.opf", opf)
            archive.writestr("OEBPS/nav.xhtml", nav)
            archive.writestr("OEBPS/toc.ncx", ncx)
            archive.writestr("OEBPS/titlepage.xhtml", titlepage)
            archive.writestr("OEBPS/cover.png", self.cover.read_bytes())
            archive.writestr("OEBPS/cover.xhtml", coverpage)
            for name, document in chapter_documents.items():
                archive.writestr(name, document)

    def write_fiction_receipt(self) -> None:
        payload = {
            "schemaVersion": 1,
            "status": "first-listen",
            "productionMode": "unattended-first-listen",
            "privacy": "private",
            "permissionToPublish": False,
            "humanReadingStatus": "pending",
            "canonicalChapterSHA256": {
                chapter.name: self.digest(chapter) for chapter in self.chapter_paths
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

    def read_fiction_receipt(self) -> dict[str, object]:
        return json.loads(self.fiction_receipt.read_text(encoding="utf-8"))

    def rebind_changed_fiction_receipt(self, payload: dict[str, object]) -> None:
        self.fiction_receipt.write_text(
            json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8"
        )
        self.receipt["privateEvidence"]["fictionReceiptSHA256"] = self.digest(
            self.fiction_receipt
        )
        self.write_publication_receipt()

    def write_echo_success_receipt(self) -> None:
        self.echo_input_receipt = self.research / (
            f"echo-render-inputs-{self.run_id}.env"
        )
        self.write_echo_input_receipt(self.echo_input_receipt)
        payload = {
            "schemaVersion": 3,
            **self.renderer_identity,
            "attemptID": self.attempt_id,
            "runID": self.run_id,
            "attemptReceiptSHA256": "8" * 64,
            "inputReceiptFileName": f"echo-render-inputs-{self.run_id}.env",
            "inputReceiptSHA256": self.digest(self.echo_input_receipt),
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

    def write_echo_input_receipt(
        self,
        path: Path,
        *,
        chapters: list[dict[str, object]] | None = None,
        default_voice: str = "bf_emma",
        plan_sha256: str | None = None,
        plan_id: str | None = None,
    ) -> None:
        assignments = chapters if chapters is not None else self.cast_chapters
        payload = (
            f"voice={default_voice}\n"
            "chapter_voices="
            + ",".join(
                f"{row['chapter']}={row['voice']}" for row in assignments
            )
            + "\n"
            f"voice_plan_sha256={plan_sha256 or self.voice_plan_sha256}\n"
            f"voice_plan_id={plan_id or self.voice_plan_id}\n"
        )
        path.write_text(payload, encoding="utf-8")

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

    def rebind_changed_public_manuscript(self) -> None:
        self.receipt["artifacts"]["manuscript"]["sha256"] = self.digest(
            self.manuscript
        )
        self.write_publication_receipt()

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
        changed_input_path = self.research / success["inputReceiptFileName"]
        self.write_echo_input_receipt(changed_input_path)
        success["inputReceiptSHA256"] = self.digest(changed_input_path)
        self.echo_success_receipt.unlink()
        self.echo_input_receipt.unlink()
        self.echo_input_receipt = changed_input_path
        self.echo_success_receipt = changed_path
        self.echo_success_receipt.write_text(
            json.dumps(success, sort_keys=True) + "\n", encoding="utf-8"
        )
        self.receipt["privateEvidence"]["echoSuccessReceiptSHA256"] = self.digest(
            self.echo_success_receipt
        )
        self.write_publication_receipt()

    def rewrite_epub_member(self, member: str, payload: str | bytes) -> None:
        rewritten = self.root / "rewritten.epub"
        with zipfile.ZipFile(self.epub) as source, zipfile.ZipFile(
            rewritten, "w"
        ) as destination:
            found = False
            for info in source.infolist():
                if info.filename == member:
                    destination.writestr(info, payload)
                    found = True
                else:
                    destination.writestr(info, source.read(info))
            if not found:
                destination.writestr(member, payload)
        rewritten.replace(self.epub)

    def add_epub_members(self, members: dict[str, bytes]) -> None:
        rewritten = self.root / "rewritten-with-members.epub"
        with zipfile.ZipFile(self.epub) as source, zipfile.ZipFile(
            rewritten, "w"
        ) as destination:
            for info in source.infolist():
                destination.writestr(info, source.read(info))
            for name, payload in members.items():
                destination.writestr(name, payload)
        rewritten.replace(self.epub)

    def rewrite_epub_central_sizes(
        self, updates: dict[str, tuple[int, int]]
    ) -> None:
        payload = bytearray(self.epub.read_bytes())
        eocd = payload.rfind(b"PK\x05\x06")
        self.assertNotEqual(-1, eocd)
        entry_count = struct.unpack_from("<H", payload, eocd + 10)[0]
        cursor = struct.unpack_from("<I", payload, eocd + 16)[0]
        seen: set[str] = set()
        for _index in range(entry_count):
            self.assertEqual(b"PK\x01\x02", payload[cursor : cursor + 4])
            filename_size, extra_size, comment_size = struct.unpack_from(
                "<HHH", payload, cursor + 28
            )
            name = bytes(
                payload[cursor + 46 : cursor + 46 + filename_size]
            ).decode("utf-8")
            if name in updates:
                compressed_size, uncompressed_size = updates[name]
                struct.pack_into("<I", payload, cursor + 20, compressed_size)
                struct.pack_into("<I", payload, cursor + 24, uncompressed_size)
                seen.add(name)
            cursor += 46 + filename_size + extra_size + comment_size
        self.assertEqual(set(updates), seen)
        self.epub.write_bytes(payload)

    def rewrite_epub_declared_member_count(self, count: int) -> None:
        payload = bytearray(self.epub.read_bytes())
        eocd = payload.rfind(b"PK\x05\x06")
        self.assertNotEqual(-1, eocd)
        struct.pack_into("<H", payload, eocd + 8, count)
        struct.pack_into("<H", payload, eocd + 10, count)
        self.epub.write_bytes(payload)

    def rewrite_epub_member_metadata(
        self, member: str, *, comment: bytes = b"", extra: bytes = b""
    ) -> None:
        rewritten = self.root / "rewritten-metadata.epub"
        with zipfile.ZipFile(self.epub) as source, zipfile.ZipFile(
            rewritten, "w"
        ) as destination:
            destination.comment = source.comment
            for info in source.infolist():
                content = source.read(info)
                if info.filename == member:
                    info.comment = comment
                    info.extra = extra
                destination.writestr(info, content)
        rewritten.replace(self.epub)

    def epub_raw_records(
        self, payload: bytearray
    ) -> tuple[int, int, dict[str, tuple[int, int]]]:
        eocd = payload.rfind(b"PK\x05\x06")
        self.assertNotEqual(-1, eocd)
        entry_count = struct.unpack_from("<H", payload, eocd + 10)[0]
        central_offset = struct.unpack_from("<I", payload, eocd + 16)[0]
        cursor = central_offset
        records: dict[str, tuple[int, int]] = {}
        for _index in range(entry_count):
            self.assertEqual(b"PK\x01\x02", payload[cursor : cursor + 4])
            filename_size, extra_size, comment_size = struct.unpack_from(
                "<HHH", payload, cursor + 28
            )
            name = bytes(
                payload[cursor + 46 : cursor + 46 + filename_size]
            ).decode("utf-8")
            local_offset = struct.unpack_from("<I", payload, cursor + 42)[0]
            records[name] = (cursor, local_offset)
            cursor += 46 + filename_size + extra_size + comment_size
        return eocd, central_offset, records

    def rewrite_epub_local_header(
        self,
        member: str,
        *,
        flags: int | None = None,
        method: int | None = None,
        crc: int | None = None,
        compressed_size: int | None = None,
        uncompressed_size: int | None = None,
        filename: bytes | None = None,
    ) -> None:
        payload = bytearray(self.epub.read_bytes())
        _eocd, _central_offset, records = self.epub_raw_records(payload)
        _central, local = records[member]
        self.assertEqual(b"PK\x03\x04", payload[local : local + 4])
        filename_size = struct.unpack_from("<H", payload, local + 26)[0]
        if flags is not None:
            struct.pack_into("<H", payload, local + 6, flags)
        if method is not None:
            struct.pack_into("<H", payload, local + 8, method)
        if crc is not None:
            struct.pack_into("<I", payload, local + 14, crc)
        if compressed_size is not None:
            struct.pack_into("<I", payload, local + 18, compressed_size)
        if uncompressed_size is not None:
            struct.pack_into("<I", payload, local + 22, uncompressed_size)
        if filename is not None:
            self.assertEqual(filename_size, len(filename))
            payload[local + 30 : local + 30 + filename_size] = filename
        self.epub.write_bytes(payload)

    def add_epub_local_extra(self, member: str, extra: bytes) -> None:
        payload = bytearray(self.epub.read_bytes())
        old_eocd, old_central_offset, records = self.epub_raw_records(payload)
        _central, local = records[member]
        self.assertEqual(max(offset for _central, offset in records.values()), local)
        filename_size, old_extra_size = struct.unpack_from("<HH", payload, local + 26)
        self.assertEqual(0, old_extra_size)
        data_start = local + 30 + filename_size
        payload[data_start:data_start] = extra
        struct.pack_into("<H", payload, local + 28, len(extra))
        new_eocd = old_eocd + len(extra)
        struct.pack_into("<I", payload, new_eocd + 16, old_central_offset + len(extra))
        self.epub.write_bytes(payload)

    def add_epub_gap_before_central_directory(self, hidden: bytes) -> None:
        payload = bytearray(self.epub.read_bytes())
        old_eocd, old_central_offset, _records = self.epub_raw_records(payload)
        payload[old_central_offset:old_central_offset] = hidden
        new_eocd = old_eocd + len(hidden)
        struct.pack_into("<I", payload, new_eocd + 16, old_central_offset + len(hidden))
        self.epub.write_bytes(payload)

    def add_epub_preamble(self, hidden: bytes) -> None:
        payload = bytearray(self.epub.read_bytes())
        old_eocd, old_central_offset, records = self.epub_raw_records(payload)
        payload[:0] = hidden
        shift = len(hidden)
        for old_central, old_local in records.values():
            struct.pack_into("<I", payload, old_central + shift + 42, old_local + shift)
        struct.pack_into("<I", payload, old_eocd + shift + 16, old_central_offset + shift)
        self.epub.write_bytes(payload)

    def rewrite_epub_external_attributes(self, member: str, attributes: int) -> None:
        payload = bytearray(self.epub.read_bytes())
        _eocd, _central_offset, records = self.epub_raw_records(payload)
        central, _local = records[member]
        struct.pack_into("<I", payload, central + 38, attributes)
        self.epub.write_bytes(payload)

    def read_epub_member(self, member: str) -> str:
        with zipfile.ZipFile(self.epub) as archive:
            return archive.read(member).decode("utf-8")

    def probes(self, *, chapter_count: int = 3):
        chapters = [
            {"start_time": f"{index}.0", "end_time": f"{index + 1}.0"}
            for index in range(chapter_count)
        ]
        return mock.patch.object(
            verifier.subprocess,
            "run",
            return_value=subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout=json.dumps(
                    {
                        "format": {"duration": f"{chapter_count}.0"},
                        "chapters": chapters,
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

    def assert_epub_rejected_before_probe(self, pattern: str) -> None:
        with mock.patch.object(
            verifier.subprocess,
            "run",
            side_effect=AssertionError("external probe ran before EPUB preflight"),
        ), self.assertRaisesRegex(ValueError, pattern):
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

    def test_rejects_m4b_chapter_count_that_differs_from_canonical_story(self) -> None:
        with self.probes(chapter_count=2), self.assertRaisesRegex(
            ValueError, "chapter count|chapter.*coverage|cardinality"
        ):
            self.verify()

    def test_rejects_cast_chapter_count_that_differs_from_canonical_story(self) -> None:
        cast = json.loads(self.voice_cast.read_text(encoding="utf-8"))
        changed_chapters = [
            *cast["chapters"],
            {
                "chapter": 4,
                "role": "Mara",
                "voice": "bf_emma",
                "experimental": False,
            },
        ]
        canonical_plan = (
            "default=bf_emma\n"
            "1=bf_emma\n"
            "2=am_michael\n"
            "3=af_bella\n"
            "4=bf_emma\n"
        )
        changed_plan_sha256 = hashlib.sha256(
            canonical_plan.encode("utf-8")
        ).hexdigest()
        changed_plan_id = f"plan-{changed_plan_sha256[:12]}"
        cast["chapterCount"] = 4
        cast["chapters"] = changed_chapters
        cast["voicePlanSHA256"] = changed_plan_sha256
        cast["voicePlanID"] = changed_plan_id
        cast["verifiedArtifacts"]["voicePlanSHA256"] = changed_plan_sha256
        self.voice_cast.write_text(
            json.dumps(cast, sort_keys=True) + "\n", encoding="utf-8"
        )

        success = json.loads(self.echo_success_receipt.read_text(encoding="utf-8"))
        changed_run_id = self.run_id.rsplit("-plan-", 1)[0] + "-" + changed_plan_id
        success["runID"] = changed_run_id
        success["inputReceiptFileName"] = f"echo-render-inputs-{changed_run_id}.env"
        success["artifactRelativePath"] = (
            f"echo-renders/{changed_run_id}/{self.attempt_id}"
        )
        success["resumeStateFileName"] = f"echo-resume-state-{changed_run_id}.json"
        changed_input = self.research / success["inputReceiptFileName"]
        self.write_echo_input_receipt(
            changed_input,
            chapters=changed_chapters,
            plan_sha256=changed_plan_sha256,
            plan_id=changed_plan_id,
        )
        success["inputReceiptSHA256"] = self.digest(changed_input)
        changed_success = self.research / (
            f"echo-render-success-{changed_run_id}-{self.attempt_id}.json"
        )
        self.echo_success_receipt.unlink()
        self.echo_input_receipt.unlink()
        self.echo_input_receipt = changed_input
        self.echo_success_receipt = changed_success
        self.echo_success_receipt.write_text(
            json.dumps(success, sort_keys=True) + "\n", encoding="utf-8"
        )
        self.receipt["privateEvidence"].update(
            {
                "voiceCastSHA256": self.digest(self.voice_cast),
                "voicePlanSHA256": changed_plan_sha256,
                "echoSuccessReceiptSHA256": self.digest(self.echo_success_receipt),
            }
        )
        self.write_publication_receipt()

        self.assert_rejected("chapter count|chapter.*coverage|cardinality")

    def test_rejects_echo_input_receipt_not_bound_to_full_voice_plan(self) -> None:
        payload = self.echo_input_receipt.read_text(encoding="utf-8").replace(
            self.voice_plan_sha256, "f" * 64
        )
        self.echo_input_receipt.write_text(payload, encoding="utf-8")
        success = json.loads(self.echo_success_receipt.read_text(encoding="utf-8"))
        success["inputReceiptSHA256"] = self.digest(self.echo_input_receipt)
        self.echo_success_receipt.write_text(
            json.dumps(success, sort_keys=True) + "\n", encoding="utf-8"
        )
        self.receipt["privateEvidence"]["echoSuccessReceiptSHA256"] = self.digest(
            self.echo_success_receipt
        )
        self.write_publication_receipt()

        self.assert_rejected("input receipt.*voice.plan|voice.plan.*input receipt")

    def test_rejects_echo_input_receipt_changed_after_provenance_validation(
        self,
    ) -> None:
        real_validate = verifier.validate_echo_success_receipt
        changed = False

        def validate_then_change(*args: object, **kwargs: object) -> None:
            nonlocal changed
            real_validate(*args, **kwargs)
            self.echo_input_receipt.write_text(
                "voice=af_bella\nchapter_voices=1=af_bella\n",
                encoding="utf-8",
            )
            changed = True

        with mock.patch.object(
            verifier,
            "validate_echo_success_receipt",
            side_effect=validate_then_change,
        ):
            self.assert_rejected("input.*changed|changed.*input")
        self.assertTrue(changed)

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
        changed_input = self.research / success["inputReceiptFileName"]
        self.write_echo_input_receipt(changed_input)
        success["inputReceiptSHA256"] = self.digest(changed_input)
        self.echo_success_receipt.unlink()
        self.echo_input_receipt.unlink()
        self.echo_input_receipt = changed_input
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

    def test_rejects_public_manuscript_substituted_from_canonical_chapters(self) -> None:
        self.manuscript.write_text("# Unrelated substituted story\n", encoding="utf-8")
        self.rebind_changed_public_manuscript()
        self.assert_rejected("canonical.*Markdown|Markdown.*canonical|story content")

    def test_rejects_markdown_content_before_the_builder_title(self) -> None:
        original = self.manuscript.read_text(encoding="utf-8")
        self.manuscript.write_text(
            "Hidden story before the builder title.\n\n" + original,
            encoding="utf-8",
        )
        self.rebind_changed_public_manuscript()
        self.assert_rejected("Markdown.*builder|Markdown.*canonical|story content")

    def test_rejects_markdown_content_before_a_canonical_chapter_heading(self) -> None:
        original = self.manuscript.read_text(encoding="utf-8")
        changed = original.replace(
            "---\n\n## Chapter One",
            "---\n\nHidden story before the chapter heading.\n\n## Chapter One",
            1,
        )
        self.assertNotEqual(original, changed)
        self.manuscript.write_text(changed, encoding="utf-8")
        self.rebind_changed_public_manuscript()
        self.assert_rejected("Markdown.*builder|Markdown.*canonical|story content")

    def test_rejects_public_epub_substituted_from_canonical_chapters(self) -> None:
        self.epub.write_bytes(b"unrelated substituted EPUB")
        self.rebind_changed_public_epub()
        self.assert_rejected(
            "canonical.*EPUB|EPUB.*canonical|EPUB.*story|zip|end record"
        )

    def test_rejects_substituted_narrated_epub_spine_content(self) -> None:
        substituted = (
            '<?xml version="1.0" encoding="utf-8"?>'
            '<html xmlns="http://www.w3.org/1999/xhtml" '
            'xmlns:epub="http://www.idpf.org/2007/ops"><head>'
            '<title>Chapter Two</title></head><body>'
            '<section epub:type="chapter"><h1>Chapter Two</h1>'
            '<p>An unrelated story replaced the narrated spine.</p>'
            '</section></body></html>'
        )
        self.rewrite_epub_member("OEBPS/chap01.xhtml", substituted)
        self.rebind_changed_public_epub()
        self.assert_rejected(
            "EPUB.*canonical|canonical.*EPUB|spine.*content|EPUB chapter.*invalid|doctype"
        )

    def test_rejects_embedded_cover_substituted_from_the_public_cover(self) -> None:
        original = self.cover.read_bytes()
        substituted = bytes([original[0] ^ 1]) + original[1:]
        self.assertEqual(len(original), len(substituted))
        self.rewrite_epub_member("OEBPS/cover.png", substituted)
        self.rebind_changed_public_epub()
        self.assert_rejected("embedded.*cover|cover.*public|cover.*bytes|cover.*SHA")

    def test_rejects_inline_formatting_not_derived_from_canonical_markdown(self) -> None:
        member = "OEBPS/chap00.xhtml"
        original = self.read_epub_member(member)
        changed = original.replace(
            "<p>The lamp survived.</p>",
            "<p><strong>The lamp survived.</strong></p>",
            1,
        )
        self.assertNotEqual(original, changed)
        self.rewrite_epub_member(member, changed)
        self.rebind_changed_public_epub()
        self.assert_rejected("inline|canonical|paragraph")

    def test_rejects_non_uuid_identifier_even_when_ncx_matches(self) -> None:
        for member in ("OEBPS/content.opf", "OEBPS/toc.ncx"):
            original = self.read_epub_member(member)
            changed = original.replace(
                self.epub_uid,
                "Hidden arbitrary story identifier",
                1,
            )
            self.assertNotEqual(original, changed)
            self.rewrite_epub_member(member, changed)
        self.rebind_changed_public_epub()
        self.assert_rejected("UUID|identifier|NCX.*uid")

    def test_rejects_container_descendant_wrapper(self) -> None:
        member = "META-INF/container.xml"
        original = self.read_epub_member(member)
        changed = original.replace(
            "<rootfiles>", "<wrapper><rootfiles>", 1
        ).replace("</rootfiles>", "</rootfiles></wrapper>", 1)
        self.assertNotEqual(original, changed)
        self.rewrite_epub_member(member, changed)
        self.rebind_changed_public_epub()
        self.assert_rejected("container.*structure|container.*content|rootfiles")

    def test_rejects_manifest_direct_story_text(self) -> None:
        member = "OEBPS/content.opf"
        original = self.read_epub_member(member)
        changed = original.replace(
            "<manifest>", "<manifest>Hidden manifest story text.", 1
        )
        self.assertNotEqual(original, changed)
        self.rewrite_epub_member(member, changed)
        self.rebind_changed_public_epub()
        self.assert_rejected("manifest.*text|manifest.*content|package.*content")

    def test_rejects_spine_direct_story_text(self) -> None:
        member = "OEBPS/content.opf"
        original = self.read_epub_member(member)
        changed = original.replace(
            '<spine toc="ncx">',
            '<spine toc="ncx">Hidden spine story text.',
            1,
        )
        self.assertNotEqual(original, changed)
        self.rewrite_epub_member(member, changed)
        self.rebind_changed_public_epub()
        self.assert_rejected("spine.*text|spine.*content|package.*content")

    def test_rejects_manifest_and_spine_child_tail_story_text(self) -> None:
        cases = (
            (
                "manifest tail",
                '<item id="css" href="style.css" media-type="text/css"/>',
                '<item id="css" href="style.css" media-type="text/css"/>'
                "Hidden manifest item tail.",
            ),
            (
                "spine tail",
                '<itemref idref="titlepage"/>',
                '<itemref idref="titlepage"/>Hidden spine item tail.',
            ),
        )
        baseline = self.epub.read_bytes()
        for name, target, replacement in cases:
            with self.subTest(name=name):
                self.epub.write_bytes(baseline)
                member = "OEBPS/content.opf"
                original = self.read_epub_member(member)
                changed = original.replace(target, replacement, 1)
                self.assertNotEqual(original, changed)
                self.rewrite_epub_member(member, changed)
                self.rebind_changed_public_epub()
                self.assert_rejected("tail|manifest.*content|spine.*content")

    def test_rejects_unknown_attributes_on_epub_structural_roles(self) -> None:
        cases = (
            (
                "titlepage head",
                "OEBPS/titlepage.xhtml",
                "<head>",
                '<head data-story="hidden">',
            ),
            (
                "navigation list",
                "OEBPS/nav.xhtml",
                "<ol>",
                '<ol data-story="hidden">',
            ),
            (
                "NCX navigation map",
                "OEBPS/toc.ncx",
                "<navMap>",
                '<navMap data-story="hidden">',
            ),
        )
        baseline = self.epub.read_bytes()
        for name, member, target, replacement in cases:
            with self.subTest(name=name):
                self.epub.write_bytes(baseline)
                original = self.read_epub_member(member)
                changed = original.replace(target, replacement, 1)
                self.assertNotEqual(original, changed)
                self.rewrite_epub_member(member, changed)
                self.rebind_changed_public_epub()
                self.assert_rejected("attribute|structure|identity|content")

    def test_rejects_xml_content_ignored_by_elementtree_structure(self) -> None:
        cases = (
            (
                "comment",
                "OEBPS/chap00.xhtml",
                '<section epub:type="chapter">',
                '<section epub:type="chapter"><!-- Hidden comment story. -->',
            ),
            (
                "processing instruction",
                "OEBPS/chap00.xhtml",
                '<section epub:type="chapter">',
                '<section epub:type="chapter"><?hidden story?>',
            ),
            (
                "internal doctype",
                "OEBPS/chap00.xhtml",
                "<!DOCTYPE html>",
                '<!DOCTYPE html [<!ENTITY hidden "Hidden story">]>',
            ),
            (
                "unknown namespace declaration",
                "OEBPS/chap00.xhtml",
                '<html xmlns="http://www.w3.org/1999/xhtml"',
                '<html xmlns:hidden="urn:hidden-story" '
                'xmlns="http://www.w3.org/1999/xhtml"',
            ),
        )
        baseline = self.epub.read_bytes()
        for name, member, target, replacement in cases:
            with self.subTest(name=name):
                self.epub.write_bytes(baseline)
                original = self.read_epub_member(member)
                changed = original.replace(target, replacement, 1)
                self.assertNotEqual(original, changed)
                self.rewrite_epub_member(member, changed)
                self.rebind_changed_public_epub()
                self.assert_rejected("XML|comment|processing|doctype|namespace|content")

    def test_rejects_zip_comments_and_member_extra_metadata(self) -> None:
        baseline = self.epub.read_bytes()
        for name in ("archive comment", "member comment", "member extra"):
            with self.subTest(name=name):
                self.epub.write_bytes(baseline)
                if name == "archive comment":
                    with zipfile.ZipFile(self.epub, "a") as archive:
                        archive.comment = b"Hidden archive story."
                elif name == "member comment":
                    self.rewrite_epub_member_metadata(
                        "OEBPS/chap00.xhtml", comment=b"Hidden member story."
                    )
                else:
                    hidden = b"Hidden member extra story."
                    self.rewrite_epub_member_metadata(
                        "OEBPS/chap00.xhtml",
                        extra=struct.pack("<HH", 0xCAFE, len(hidden)) + hidden,
                    )
                self.rebind_changed_public_epub()
                self.assert_rejected("EPUB.*(comment|extra|metadata|identity)")

    def test_rejects_local_only_zip_extra_before_probe(self) -> None:
        self.add_epub_local_extra(
            "OEBPS/chap02.xhtml",
            struct.pack("<HH", 0xCAFE, 19) + b"Hidden local story.",
        )
        self.rebind_changed_public_epub()
        self.assert_epub_rejected_before_probe("EPUB.*(local|extra|envelope)")

    def test_rejects_local_zip_method_and_flag_disagreement_before_probe(self) -> None:
        baseline = self.epub.read_bytes()
        cases = (
            ("method", {"method": zipfile.ZIP_DEFLATED}),
            ("encryption flag", {"flags": 0x1}),
            ("data descriptor flag", {"flags": 0x8}),
        )
        for name, fields in cases:
            with self.subTest(name=name):
                self.epub.write_bytes(baseline)
                self.rewrite_epub_local_header("OEBPS/chap00.xhtml", **fields)
                self.rebind_changed_public_epub()
                self.assert_epub_rejected_before_probe(
                    "EPUB.*(local|method|flag|encryption|descriptor|envelope)"
                )

    def test_rejects_nonregular_zip_member_modes_before_probe(self) -> None:
        baseline = self.epub.read_bytes()
        cases = (
            ("FIFO", (stat.S_IFIFO | 0o600) << 16),
            ("character device", (stat.S_IFCHR | 0o600) << 16),
            ("socket", (stat.S_IFSOCK | 0o600) << 16),
            ("directory", (stat.S_IFDIR | 0o700) << 16),
            ("DOS directory", 0x10),
            ("DOS device", 0x40),
        )
        for name, attributes in cases:
            with self.subTest(name=name):
                self.epub.write_bytes(baseline)
                self.rewrite_epub_external_attributes(
                    "OEBPS/chap00.xhtml", attributes
                )
                self.rebind_changed_public_epub()
                self.assert_epub_rejected_before_probe(
                    "EPUB.*(regular|mode|special|directory|device|envelope)"
                )

    def test_rejects_zip_preamble_and_hidden_gap_before_probe(self) -> None:
        baseline = self.epub.read_bytes()
        for name in ("preamble", "gap"):
            with self.subTest(name=name):
                self.epub.write_bytes(baseline)
                if name == "preamble":
                    self.add_epub_preamble(b"Hidden preamble story.")
                else:
                    self.add_epub_gap_before_central_directory(
                        b"Hidden gap story."
                    )
                self.rebind_changed_public_epub()
                self.assert_epub_rejected_before_probe(
                    "EPUB.*(preamble|gap|envelope|local)"
                )

    def test_rejects_zip_local_name_size_and_crc_disagreement_before_probe(self) -> None:
        baseline = self.epub.read_bytes()
        payload = bytearray(baseline)
        _eocd, _central_offset, records = self.epub_raw_records(payload)
        central, _local = records["OEBPS/chap00.xhtml"]
        central_crc = struct.unpack_from("<I", payload, central + 16)[0]
        central_compressed = struct.unpack_from("<I", payload, central + 20)[0]
        central_uncompressed = struct.unpack_from("<I", payload, central + 24)[0]
        cases = (
            ("filename", {"filename": b"OEBPS/xhap00.xhtml"}),
            ("CRC", {"crc": central_crc ^ 1}),
            ("compressed size", {"compressed_size": central_compressed + 1}),
            ("uncompressed size", {"uncompressed_size": central_uncompressed + 1}),
        )
        for name, fields in cases:
            with self.subTest(name=name):
                self.epub.write_bytes(baseline)
                self.rewrite_epub_local_header("OEBPS/chap00.xhtml", **fields)
                self.rebind_changed_public_epub()
                self.assert_epub_rejected_before_probe(
                    "EPUB.*(filename|size|CRC|local|envelope)"
                )

    def test_rejects_stored_member_with_different_uncompressed_size(self) -> None:
        payload = bytearray(self.epub.read_bytes())
        _eocd, _central_offset, records = self.epub_raw_records(payload)
        central, _local = records["mimetype"]
        compressed_size = struct.unpack_from("<I", payload, central + 20)[0]
        uncompressed_size = struct.unpack_from("<I", payload, central + 24)[0]
        self.assertEqual(compressed_size, uncompressed_size)
        self.rewrite_epub_central_sizes(
            {"mimetype": (compressed_size, uncompressed_size + 1)}
        )
        self.rewrite_epub_local_header(
            "mimetype", uncompressed_size=uncompressed_size + 1
        )
        self.rebind_changed_public_epub()
        self.assert_epub_rejected_before_probe("EPUB.*(stored|size|envelope)")

    def test_rejects_zip64_extract_version_without_zip64_fields(self) -> None:
        payload = bytearray(self.epub.read_bytes())
        _eocd, _central_offset, records = self.epub_raw_records(payload)
        central, local = records["OEBPS/chap00.xhtml"]
        struct.pack_into("<H", payload, central + 6, 45)
        struct.pack_into("<H", payload, local + 4, 45)
        self.epub.write_bytes(payload)
        self.rebind_changed_public_epub()
        self.assert_epub_rejected_before_probe("EPUB.*(ZIP64|classic|version|envelope)")

    def test_rejects_zip_trailing_bytes_before_probe(self) -> None:
        with self.epub.open("ab") as stream:
            stream.write(b"Hidden trailing story.")
        self.rebind_changed_public_epub()
        self.assert_epub_rejected_before_probe("EPUB.*(trailing|end|comment|envelope)")

    def test_rejects_oversized_public_cover_before_content_read(self) -> None:
        os.truncate(self.cover, verifier._EPUB_MAX_COVER_BYTES + 1)
        cover_identity = self.cover.stat()
        real_fdopen = verifier.os.fdopen

        def fail_if_cover_content_is_opened(descriptor, *args, **kwargs):
            opened = os.fstat(descriptor)
            if (opened.st_dev, opened.st_ino) == (
                cover_identity.st_dev,
                cover_identity.st_ino,
            ):
                raise AssertionError("oversized cover content was opened")
            return real_fdopen(descriptor, *args, **kwargs)

        with mock.patch.object(
            verifier.os, "fdopen", side_effect=fail_if_cover_content_is_opened
        ), self.assertRaisesRegex(ValueError, "[Cc]over.*(large|size|limit)"):
            self.verify()

    def test_snapshot_capture_accepts_exact_cover_size_limit(self) -> None:
        os.truncate(self.cover, verifier._EPUB_MAX_COVER_BYTES)
        snapshot = verifier._snapshot_file(
            self.cover,
            "fiction portraitCover artifact",
            capture=True,
            max_bytes=verifier._EPUB_MAX_COVER_BYTES,
        )
        self.assertEqual(verifier._EPUB_MAX_COVER_BYTES, snapshot.size)
        self.assertEqual(verifier._EPUB_MAX_COVER_BYTES, len(snapshot.content or b""))

    def test_snapshot_capture_enforces_limit_if_file_grows_during_read(self) -> None:
        self.cover.write_bytes(b"x")
        cover_identity = self.cover.stat()
        cover_path = self.cover
        real_fdopen = verifier.os.fdopen
        grew = False

        class GrowingStream:
            def __init__(self, stream):
                self.stream = stream

            def __enter__(self):
                self.stream.__enter__()
                return self

            def __exit__(self, *args):
                return self.stream.__exit__(*args)

            def fileno(self):
                return self.stream.fileno()

            def read(self, size=-1):
                nonlocal grew
                chunk = self.stream.read(size)
                if not grew:
                    grew = True
                    os.truncate(cover_path, verifier._EPUB_MAX_COVER_BYTES + 1)
                return chunk

        def growing_cover_stream(descriptor, *args, **kwargs):
            stream = real_fdopen(descriptor, *args, **kwargs)
            opened = os.fstat(stream.fileno())
            if (opened.st_dev, opened.st_ino) == (
                cover_identity.st_dev,
                cover_identity.st_ino,
            ):
                return GrowingStream(stream)
            return stream

        with mock.patch.object(
            verifier.os, "fdopen", side_effect=growing_cover_stream
        ), self.assertRaisesRegex(ValueError, "[Cc]over.*(grew|large|size|limit)"):
            verifier._snapshot_file(
                self.cover,
                "fiction portraitCover artifact",
                capture=True,
                max_bytes=verifier._EPUB_MAX_COVER_BYTES,
            )

    def test_final_cover_reattest_rechecks_cap_before_content_read(self) -> None:
        real_readme = verifier._verify_fiction_readme
        real_fdopen = verifier.os.fdopen
        cover_identity = self.cover.stat()

        def grow_cover_after_readme(book_dir: Path, *private_paths: Path):
            snapshot = real_readme(book_dir, *private_paths)
            os.truncate(self.cover, verifier._EPUB_MAX_COVER_BYTES + 1)
            return snapshot

        def fail_if_oversized_cover_is_opened(descriptor, *args, **kwargs):
            opened = os.fstat(descriptor)
            if (
                (opened.st_dev, opened.st_ino)
                == (cover_identity.st_dev, cover_identity.st_ino)
                and opened.st_size > verifier._EPUB_MAX_COVER_BYTES
            ):
                raise AssertionError("oversized cover was read during final reattestation")
            return real_fdopen(descriptor, *args, **kwargs)

        with mock.patch.object(
            verifier, "_verify_fiction_readme", side_effect=grow_cover_after_readme
        ), mock.patch.object(
            verifier.os, "fdopen", side_effect=fail_if_oversized_cover_is_opened
        ), self.probes(), self.assertRaisesRegex(
            ValueError, "[Cc]over.*(large|size|limit|changed)"
        ):
            self.verify()

    def test_rejects_non_builder_epub_language_even_when_all_xhtml_matches(self) -> None:
        opf = self.read_epub_member("OEBPS/content.opf").replace(
            "<dc:language>en</dc:language>",
            "<dc:language>hidden-story-language</dc:language>",
            1,
        )
        self.rewrite_epub_member("OEBPS/content.opf", opf)
        for member in (
            "OEBPS/titlepage.xhtml",
            "OEBPS/nav.xhtml",
            "OEBPS/cover.xhtml",
            "OEBPS/chap00.xhtml",
            "OEBPS/chap01.xhtml",
            "OEBPS/chap02.xhtml",
        ):
            document = self.read_epub_member(member).replace(
                'lang="en"', 'lang="hidden-story-language"', 1
            )
            self.rewrite_epub_member(member, document)
        self.rebind_changed_public_epub()
        self.assert_rejected("language|builder")

    def test_rejects_epub_role_size_and_ratio_declarations_before_probe(self) -> None:
        cases = (
            ("oversized CSS", "OEBPS/style.css", 1_000, 70_000),
            ("oversized cover", "OEBPS/cover.png", 1_000, 20 * 1024 * 1024),
            ("oversized XML", "META-INF/container.xml", 1_000, 2 * 1024 * 1024),
            ("high-ratio CSS", "OEBPS/style.css", 1, 60_000),
            ("high-ratio cover", "OEBPS/cover.png", 1, 1_000_000),
            ("high-ratio XML", "OEBPS/content.opf", 1, 500_000),
            ("zero compressed nonempty", "OEBPS/chap00.xhtml", 0, 1),
            ("oversized compressed member", "OEBPS/cover.png", 20 * 1024 * 1024, 14),
        )
        baseline = self.epub.read_bytes()
        for name, member, compressed_size, uncompressed_size in cases:
            with self.subTest(name=name):
                self.epub.write_bytes(baseline)
                self.rewrite_epub_central_sizes(
                    {member: (compressed_size, uncompressed_size)}
                )
                self.rebind_changed_public_epub()
                self.assert_epub_rejected_before_probe(
                    "EPUB.*(size|ratio|compressed|resource|limit)"
                )

    def test_rejects_epub_member_count_before_probe(self) -> None:
        self.add_epub_members(
            {f"OEBPS/extra-{index:03d}.bin": b"" for index in range(70)}
        )
        self.rebind_changed_public_epub()
        self.assert_epub_rejected_before_probe("EPUB.*(member count|too many|limit)")

    def test_rejects_epub_declared_member_count_before_probe(self) -> None:
        self.rewrite_epub_declared_member_count(65_535)
        self.rebind_changed_public_epub()
        self.assert_epub_rejected_before_probe("EPUB.*(member count|too many|limit)")

    def test_rejects_epub_aggregate_size_declarations_before_probe(self) -> None:
        extra_names = [f"OEBPS/extra-{index:03d}.bin" for index in range(40)]
        self.add_epub_members({name: b"" for name in extra_names})
        self.rewrite_epub_central_sizes(
            {name: (1_800_000, 2_000_000) for name in extra_names}
        )
        self.rebind_changed_public_epub()
        self.assert_epub_rejected_before_probe("EPUB.*(aggregate|total|compressed|limit)")

    def test_rejects_visible_xhtml_text_inside_a_chapter_section(self) -> None:
        member = "OEBPS/chap00.xhtml"
        original = self.read_epub_member(member)
        changed = original.replace(
            '<section epub:type="chapter"><h1>',
            '<section epub:type="chapter">Hidden direct section text.<h1>',
            1,
        )
        self.assertNotEqual(original, changed)
        self.rewrite_epub_member(member, changed)
        self.rebind_changed_public_epub()
        self.assert_rejected("EPUB.*content|EPUB.*structure|chapter")

    def test_rejects_visible_xhtml_content_outside_the_chapter_section(self) -> None:
        member = "OEBPS/chap00.xhtml"
        original = self.read_epub_member(member)
        changed = original.replace(
            "</section></body>",
            "</section><p>Hidden story outside the chapter section.</p></body>",
            1,
        )
        self.assertNotEqual(original, changed)
        self.rewrite_epub_member(member, changed)
        self.rebind_changed_public_epub()
        self.assert_rejected("EPUB.*content|EPUB.*structure|chapter")

    def test_rejects_stylesheet_generated_story_content(self) -> None:
        self.rewrite_epub_member(
            "OEBPS/style.css",
            'body::before{content:"Hidden generated story content."}',
        )
        self.rebind_changed_public_epub()
        self.assert_rejected("EPUB.*stylesheet|EPUB.*style|builder")

    def test_rejects_a_narrated_chapter_marked_linear_no(self) -> None:
        member = "OEBPS/content.opf"
        original = self.read_epub_member(member)
        changed = original.replace(
            '<itemref idref="chap00"/>',
            '<itemref idref="chap00" linear="no"/>',
            1,
        )
        self.assertNotEqual(original, changed)
        self.rewrite_epub_member(member, changed)
        self.rebind_changed_public_epub()
        self.assert_rejected("linear|spine|narrated")

    def test_rejects_unspined_bibliography_xhtml_with_story_content(self) -> None:
        bibliography = (
            '<?xml version="1.0" encoding="utf-8"?>'
            '<html xmlns="http://www.w3.org/1999/xhtml" '
            'xmlns:epub="http://www.idpf.org/2007/ops" lang="en"><head>'
            '<meta charset="utf-8"/><title>Hidden Story</title>'
            '<link rel="stylesheet" type="text/css" href="style.css"/></head><body>'
            '<section epub:type="bibliography"><h1>Hidden Story</h1>'
            '<p>Arbitrary unspined story content.</p></section></body></html>'
        )
        self.rewrite_epub_member("OEBPS/appendix.xhtml", bibliography)
        opf_member = "OEBPS/content.opf"
        original_opf = self.read_epub_member(opf_member)
        changed_opf = original_opf.replace(
            "</manifest>",
            '<item id="appendix" href="appendix.xhtml" '
            'media-type="application/xhtml+xml"/></manifest>',
            1,
        )
        self.assertNotEqual(original_opf, changed_opf)
        self.rewrite_epub_member(opf_member, changed_opf)
        self.rebind_changed_public_epub()
        self.assert_rejected("unspined|XHTML|EPUB.*role|EPUB.*content")

    def test_rejects_extra_unspined_chapter_xhtml(self) -> None:
        extra = (
            '<?xml version="1.0" encoding="utf-8"?>'
            '<html xmlns="http://www.w3.org/1999/xhtml" '
            'xmlns:epub="http://www.idpf.org/2007/ops"><head>'
            '<title>Hidden Chapter</title></head><body>'
            '<section epub:type="chapter"><h1>Hidden Chapter</h1>'
            '<p>Unspined canonical-looking story.</p></section></body></html>'
        )
        self.rewrite_epub_member("OEBPS/hidden-chapter.xhtml", extra)
        self.rebind_changed_public_epub()
        self.assert_rejected(
            "unmanifested|unspined|EPUB.*chapter|extra or missing package file"
        )

    def test_accepts_story_outputs_from_the_unchanged_builder(self) -> None:
        output = self.root / "real-builder-output"
        subprocess.run(
            [
                "/usr/local/bin/python3",
                str(
                    Path(__file__).resolve().parents[1]
                    / "skill/scripts/build_book.py"
                ),
                "--chapters-dir",
                str(self.chapters),
                "--out-dir",
                str(output),
                "--title",
                "Fixture Fiction",
                "--subtitle",
                "A Fixture Subtitle",
                "--author",
                "Dan Fakkeldy",
                "--contributor",
                "GPT-5.6",
                "--cover",
                str(self.cover),
                "--slug",
                "fixture-fiction",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        shutil.copy2(output / self.manuscript.name, self.manuscript)
        shutil.copy2(output / self.epub.name, self.epub)
        self.rebind_changed_public_manuscript()
        self.rebind_changed_public_epub()

        with self.probes():
            self.verify()

    def test_accepts_builder_inline_emphasis_from_canonical_markdown(self) -> None:
        self.chapter.write_text(
            "## Chapter One\n\nThe **lamp** _survived_.\n",
            encoding="utf-8",
        )
        private_receipt = self.read_fiction_receipt()
        private_receipt["canonicalChapterSHA256"][self.chapter.name] = self.digest(
            self.chapter
        )
        self.rebind_changed_fiction_receipt(private_receipt)
        output = self.root / "inline-builder-output"
        subprocess.run(
            [
                "/usr/local/bin/python3",
                str(
                    Path(__file__).resolve().parents[1]
                    / "skill/scripts/build_book.py"
                ),
                "--chapters-dir",
                str(self.chapters),
                "--out-dir",
                str(output),
                "--title",
                "Fixture Fiction",
                "--author",
                "Dan Fakkeldy",
                "--contributor",
                "GPT-5.6",
                "--cover",
                str(self.cover),
                "--slug",
                "fixture-fiction",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        shutil.copy2(output / self.manuscript.name, self.manuscript)
        shutil.copy2(output / self.epub.name, self.epub)
        self.rebind_changed_public_manuscript()
        self.rebind_changed_public_epub()

        with self.probes():
            self.verify()

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

    def test_private_qc_delegate_consumes_only_captured_receipt_and_artifact_bytes(
        self,
    ) -> None:
        real_delegate = verifier.verify_fiction_receipt
        original_receipt = self.fiction_receipt.read_bytes()
        original_story_bible = self.fiction_artifacts["storyBible"].read_bytes()
        invalid_receipt = self.read_fiction_receipt()
        invalid_receipt["status"] = "rejected"
        invalid_receipt_bytes = (
            json.dumps(invalid_receipt, sort_keys=True) + "\n"
        ).encode("utf-8")

        for target in ("receipt", "storyBible"):
            with self.subTest(target=target):
                observed = None
                live_path = (
                    self.fiction_receipt
                    if target == "receipt"
                    else self.fiction_artifacts["storyBible"]
                )
                replacement_bytes = (
                    invalid_receipt_bytes
                    if target == "receipt"
                    else b"substituted invalid story bible bytes\n"
                )

                def delegate_probe(chapters: Path, receipt: Path):
                    nonlocal observed
                    saved = self.root / f"saved-private-{target}"
                    replacement = self.root / f"replacement-private-{target}"
                    replacement.write_bytes(replacement_bytes)
                    live_path.replace(saved)
                    replacement.replace(live_path)
                    try:
                        if target == "receipt":
                            observed = Path(receipt).read_bytes()
                        else:
                            delegated_receipt = json.loads(
                                Path(receipt).read_text(encoding="utf-8")
                            )
                            relative = delegated_receipt["artifacts"]["storyBible"][
                                "path"
                            ]
                            observed = (
                                Path(receipt).parent.parent / relative
                            ).read_bytes()
                    finally:
                        live_path.unlink()
                        saved.replace(live_path)
                    return real_delegate(Path(chapters), Path(receipt))

                with mock.patch.object(
                    verifier, "verify_fiction_receipt", side_effect=delegate_probe
                ), self.probes():
                    self.verify()
                expected = (
                    original_receipt
                    if target == "receipt"
                    else original_story_bible
                )
                self.assertEqual(expected, observed)

    def test_verifier_locally_rejects_nonexact_private_receipt_schema(self) -> None:
        base = self.read_fiction_receipt()

        def add_extra_artifact(payload: dict[str, object]) -> None:
            payload["artifacts"]["unexpected"] = copy.deepcopy(
                payload["artifacts"]["storyBible"]
            )

        def add_extra_record_field(payload: dict[str, object]) -> None:
            payload["artifacts"]["storyBible"]["note"] = "not governed"

        mutations = (
            ("boolean schema", lambda value: value.__setitem__("schemaVersion", True)),
            ("float schema", lambda value: value.__setitem__("schemaVersion", 1.0)),
            ("extra top level", lambda value: value.__setitem__("unexpected", True)),
            (
                "wrong status",
                lambda value: value.__setitem__("status", "governed-final"),
            ),
            (
                "integer permission",
                lambda value: value.__setitem__("permissionToPublish", 0),
            ),
            (
                "extra gate",
                lambda value: value["gates"].__setitem__("unexpected", "pass"),
            ),
            ("extra artifact", add_extra_artifact),
            ("extra artifact record field", add_extra_record_field),
        )
        for name, mutate in mutations:
            with self.subTest(name=name):
                changed = copy.deepcopy(base)
                mutate(changed)
                self.rebind_changed_fiction_receipt(changed)
                with mock.patch.object(
                    verifier, "verify_fiction_receipt", return_value={}
                ):
                    self.assert_rejected("private fiction receipt|fiction production")
                self.rebind_changed_fiction_receipt(base)

    def test_verifier_locally_requires_exact_current_canonical_chapter_coverage(
        self,
    ) -> None:
        extra = self.chapters / "ch04.md"
        extra.write_text("## Hidden Chapter\n\nHidden story.\n", encoding="utf-8")
        try:
            with mock.patch.object(verifier, "verify_fiction_receipt", return_value={}):
                self.assert_rejected("chapter coverage|canonical chapter")
        finally:
            extra.unlink()

    def test_rejects_canonical_chapter_coverage_changed_during_private_delegate(
        self,
    ) -> None:
        real_delegate = verifier.verify_fiction_receipt
        extra = self.chapters / "ch04.md"

        def add_live_chapter(chapters: Path, receipt: Path):
            extra.write_text("## Hidden Chapter\n\nHidden story.\n", encoding="utf-8")
            return real_delegate(Path(chapters), Path(receipt))

        try:
            with mock.patch.object(
                verifier, "verify_fiction_receipt", side_effect=add_live_chapter
            ), self.probes(), self.assertRaisesRegex(
                ValueError, "chapter coverage|changed during verification"
            ):
                self.verify()
        finally:
            extra.unlink(missing_ok=True)

    def test_rejects_canonical_chapter_added_after_all_story_consumers(self) -> None:
        real_readme = verifier._verify_fiction_readme
        extra = self.chapters / "ch04.md"

        def add_late_chapter(book_dir: Path, *sensitive_paths: Path):
            snapshot = real_readme(Path(book_dir), *sensitive_paths)
            extra.write_text("## Hidden Chapter\n\nHidden late story.\n", encoding="utf-8")
            return snapshot

        try:
            with mock.patch.object(
                verifier, "_verify_fiction_readme", side_effect=add_late_chapter
            ), self.probes(), self.assertRaisesRegex(
                ValueError, "chapter coverage|changed.*chapter|canonical chapter"
            ):
                self.verify()
        finally:
            extra.unlink(missing_ok=True)

    def test_verifier_locally_rejects_unsafe_private_artifact_paths(self) -> None:
        base = self.read_fiction_receipt()
        story_bytes = self.fiction_artifacts["storyBible"].read_bytes()
        path_cases = (
            ("absolute in root", str(self.fiction_artifacts["storyBible"])),
            ("drive forward", "C:/private/story-bible.md"),
            ("drive backslash", "C:\\private\\story-bible.md"),
            ("UNC", "\\\\server\\share\\story-bible.md"),
            ("device", "\\\\?\\C:\\story-bible.md"),
            ("traversal", "nested/../story-bible.md"),
        )
        for name, relative in path_cases:
            with self.subTest(name=name):
                candidate = Path(relative)
                created = False
                if not candidate.is_absolute():
                    candidate = self.private_dir / candidate
                if candidate != self.fiction_artifacts["storyBible"]:
                    candidate.parent.mkdir(parents=True, exist_ok=True)
                    candidate.write_bytes(story_bytes)
                    created = True
                changed = copy.deepcopy(base)
                changed["artifacts"]["storyBible"] = {
                    "path": relative,
                    "sha256": self.digest(candidate),
                }
                self.rebind_changed_fiction_receipt(changed)
                try:
                    with mock.patch.object(
                        verifier, "verify_fiction_receipt", return_value={}
                    ):
                        self.assert_rejected("relative POSIX-safe|artifact path")
                finally:
                    self.rebind_changed_fiction_receipt(base)
                    if created:
                        candidate.unlink()

    def test_verifier_requires_exact_canonical_private_artifact_paths(self) -> None:
        base = self.read_fiction_receipt()
        for name, canonical_path in self.fiction_artifacts.items():
            with self.subTest(name=name):
                alternative = self.private_dir / "alternate" / canonical_path.name
                alternative.parent.mkdir(parents=True, exist_ok=True)
                alternative.write_bytes(canonical_path.read_bytes())
                changed = copy.deepcopy(base)
                changed["artifacts"][name] = {
                    "path": alternative.relative_to(self.private_dir).as_posix(),
                    "sha256": self.digest(alternative),
                }
                self.rebind_changed_fiction_receipt(changed)
                try:
                    with mock.patch.object(
                        verifier, "verify_fiction_receipt", return_value={}
                    ):
                        self.assert_rejected("canonical.*path|path.*canonical")
                finally:
                    self.rebind_changed_fiction_receipt(base)
                    alternative.unlink()

    def test_rejects_private_paths_and_evidence_names_in_public_readme(self) -> None:
        private_values = (
            "/Users/alice/Secret/client-notes.md",
            "file:///private/fixture-fiction/story-bible.md",
            r"C:\private\fixture-fiction\voice-cast.json",
            r"\\server\share\fixture-fiction\continuity.md",
            r"\\?\C:\private\fixture-fiction\receipt.json",
            ".build/fiction-audiobooks/fixture-fiction/research/notes.md",
            "_production/narration/voice-cast.json",
            "research/release-notes.md",
            "chapters/ch01.md",
            "continuity/rolling.md",
            "revisions/full-manuscript-review.md",
            "brief.md",
            "outline.md",
            self.voice_cast.name,
            self.fiction_receipt.name,
            self.echo_success_receipt.name,
        )
        readme = self.book_dir / "README.md"
        for value in private_values:
            with self.subTest(value=value):
                readme.write_text(
                    f"{FICTION_DISCLOSURE}\n\nInternal evidence: {value}\n",
                    encoding="utf-8",
                )
                self.assert_rejected("README.*private|private.*README|local path|evidence")

    def test_rejects_home_expansion_paths_in_public_readme(self) -> None:
        private_values = (
            "$HOME/Library/Application Support/Explainer Audiobooks/"
            "fiction-voice-preferences.json",
            "$HOME\\Library\\Application Support\\Explainer Audiobooks\\"
            "fiction-voice-preferences.json",
            "${HOME}/Library/Application Support/private-notes.md",
            "${HOME}\\Library\\Application Support\\private-notes.md",
            "~/Library/Application Support/private-notes.md",
            "$USERPROFILE\\AppData\\Local\\private-notes.md",
            "%USERPROFILE%\\AppData\\Local\\private-notes.md",
        )
        readme = self.book_dir / "README.md"
        for value in private_values:
            with self.subTest(value=value):
                readme.write_text(
                    f"{FICTION_DISCLOSURE}\n\nInternal evidence: {value}\n",
                    encoding="utf-8",
                )
                self.assert_rejected("README.*private|private.*README|local path")

    def test_allows_public_readme_prose_without_private_evidence_references(self) -> None:
        (self.book_dir / "README.md").write_text(
            f"{FICTION_DISCLOSURE}\n\n"
            "Read the public Markdown manuscript or EPUB, then download the M4B "
            "from the GitHub release.\n",
            encoding="utf-8",
        )

        with self.probes():
            self.verify()

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

    def test_external_media_probe_timeouts_fail_closed(self) -> None:
        valid_media = json.dumps(
            {
                "format": {"duration": "1.0"},
                "chapters": [{"start_time": "0.0", "end_time": "1.0"}],
            }
        )
        for target in ("unzip", "ffprobe"):
            with self.subTest(target=target):

                def bounded_probe(command, **kwargs):
                    timeout = kwargs.get("timeout")
                    if (
                        command[0] == target
                        and isinstance(timeout, (int, float))
                        and 0 < timeout <= 60
                    ):
                        raise subprocess.TimeoutExpired(command, timeout)
                    return subprocess.CompletedProcess(
                        args=command,
                        returncode=0,
                        stdout=valid_media,
                        stderr="",
                    )

                with mock.patch.object(
                    verifier.subprocess, "run", side_effect=bounded_probe
                ), self.assertRaisesRegex(ValueError, "timed out|timeout"):
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
                                "format": {"duration": "3.0"},
                                "chapters": [
                                    {"start_time": "0.0", "end_time": "1.0"},
                                    {"start_time": "1.0", "end_time": "2.0"},
                                    {"start_time": "2.0", "end_time": "3.0"},
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

    def test_external_probes_consume_immutable_bytes_during_transient_swap(self) -> None:
        for target in ("epub", "release"):
            with self.subTest(target=target):
                original_path = self.epub if target == "epub" else self.release_m4b
                original_bytes = original_path.read_bytes()
                observed_probe_bytes = None

                def transient_swap(command, **_kwargs):
                    nonlocal observed_probe_bytes
                    command_target = "epub" if command[0] == "unzip" else "release"
                    if command_target == target:
                        saved = self.root / f"saved-{target}"
                        replacement = self.root / f"replacement-{target}"
                        replacement.write_bytes(f"transient {target} bytes".encode())
                        original_path.replace(saved)
                        replacement.replace(original_path)
                        try:
                            observed_probe_bytes = Path(command[-1]).read_bytes()
                        finally:
                            original_path.unlink()
                            saved.replace(original_path)
                    return subprocess.CompletedProcess(
                        args=command,
                        returncode=0,
                        stdout=json.dumps(
                            {
                                "format": {"duration": "3.0"},
                                "chapters": [
                                    {"start_time": "0.0", "end_time": "1.0"},
                                    {"start_time": "1.0", "end_time": "2.0"},
                                    {"start_time": "2.0", "end_time": "3.0"},
                                ],
                            }
                        ),
                        stderr="",
                    )

                with mock.patch.object(
                    verifier.subprocess, "run", side_effect=transient_swap
                ):
                    self.verify()
                self.assertEqual(original_bytes, observed_probe_bytes)

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
