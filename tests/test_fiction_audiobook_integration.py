from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from PIL import Image


ROOT = Path(__file__).parents[1]
for scripts in (
    ROOT / "skill" / "scripts",
    ROOT / "skills" / "fiction-audiobook" / "scripts",
    ROOT / "skills" / "echo-narration" / "scripts",
):
    sys.path.insert(0, str(scripts))

import build_book
import echo_voice_plan
import fiction_voice_preferences
import stage_echo_delivery
from skill.scripts import verify_public_first_listen


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


class FictionAudiobookIntegrationTests(unittest.TestCase):
    def test_real_production_artifacts_remain_bound_through_private_and_public_delivery(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            run_root = Path(raw_root).resolve() / "private-run"
            source = run_root / "source"
            checks = run_root / "checks"
            covers = run_root / "covers"
            dist = run_root / "dist"
            narration = run_root / "narration"
            for directory in (source, checks, covers, narration):
                directory.mkdir(parents=True)

            chapter_specs = (
                ("ch01.md", "Chapter One", "The lamp survived the first tide."),
                ("ch02.md", "Chapter Two", "The signal crossed the dark water."),
                ("ch03.md", "Chapter Three", "At dawn, the harbor answered."),
            )
            chapters: list[Path] = []
            for filename, title, body in chapter_specs:
                chapter = source / filename
                chapter.write_text(f"## {title}\n\n{body}\n", encoding="utf-8")
                chapters.append(chapter)

            evidence = {
                "authorization": source / "unattended-decisions.json",
                "storyBible": source / "story-bible.md",
                "continuity": source / "continuity-final.md",
                "revisionReview": checks / "revision-receipt.json",
                "proseQC": checks / "prose-qc-receipt.json",
            }
            for name, path in evidence.items():
                path.write_text(f"{name}: verified\n", encoding="utf-8")

            fiction_receipt = checks / "fiction-production-receipt.json"
            write_json(
                fiction_receipt,
                {
                    "schemaVersion": 1,
                    "status": "first-listen",
                    "productionMode": "unattended-first-listen",
                    "privacy": "private",
                    "permissionToPublish": False,
                    "humanReadingStatus": "pending",
                    "canonicalChapterSHA256": {
                        chapter.name: sha256(chapter) for chapter in chapters
                    },
                    "artifacts": {
                        name: {
                            "path": path.relative_to(run_root).as_posix(),
                            "sha256": sha256(path),
                        }
                        for name, path in evidence.items()
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
                },
            )

            portrait_cover = covers / "cover.png"
            square_cover = covers / "m4b-cover.png"
            Image.new("RGB", (1600, 2560), (20, 42, 68)).save(portrait_cover)
            Image.new("RGB", (2400, 2400), (68, 42, 20)).save(square_cover)

            build_book.build(
                source,
                dist,
                "Fixture Ensemble",
                "Dan Fakkeldy",
                "",
                "fixture-ensemble",
                cover=portrait_cover,
                m4b_cover=square_cover,
                contributor="GPT-5.6",
                fiction_receipt=fiction_receipt,
            )
            built_markdown = dist / "fixture-ensemble.md"
            built_epub = dist / "fixture-ensemble.epub"
            self.assertTrue(built_markdown.is_file())
            self.assertTrue(built_epub.is_file())
            with zipfile.ZipFile(built_epub) as archive:
                self.assertEqual(
                    portrait_cover.read_bytes(), archive.read("OEBPS/cover.png")
                )

            cast_chapters = [
                {
                    "chapter": 1,
                    "role": "Mara",
                    "voice": "bf_emma",
                    "experimental": False,
                },
                {
                    "chapter": 2,
                    "role": "Ivo",
                    "voice": "am_michael",
                    "experimental": False,
                },
                {
                    "chapter": 3,
                    "role": "Sera",
                    "voice": "af_bella",
                    "experimental": False,
                },
            ]
            plan = echo_voice_plan.voice_plan(
                "bf_emma",
                [f"{row['chapter']}={row['voice']}" for row in cast_chapters],
            )
            cast = {
                "schemaVersion": 1,
                "slug": "fixture-ensemble",
                "chapterCount": 3,
                "defaultVoice": "bf_emma",
                "chapters": cast_chapters,
                "voicePlanSHA256": plan["voicePlanSHA256"],
                "voicePlanID": plan["voicePlanID"],
                "verifiedArtifacts": None,
            }
            self.assertEqual(
                plan,
                fiction_voice_preferences.validate_cast(
                    cast, fiction_voice_preferences.initial_preferences()
                ),
            )
            cast_path = narration / "voice-cast.json"
            write_json(cast_path, cast)

            final_m4b = dist / "fixture-ensemble.m4b"
            sidecar = dist / "fixture-ensemble.alignment.json"
            final_m4b.write_bytes(b"fixture final audiobook")
            write_json(sidecar, [{"blockId": "b1", "timestamp": 0}])
            renderer_identity = {
                "rendererSchemaVersion": 1,
                "rendererRoot": str(run_root / "installed-renderer"),
                "rendererBuildRoot": str(run_root / "installed-renderer/renderer"),
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
            run_id = (
                f"{sha256(built_epub)[:12]}-"
                f"{renderer_identity['echoCLI_SHA256'][:12]}-"
                f"{renderer_identity['echoResourcesSHA256'][:12]}-"
                f"{renderer_identity['rendererManifestSHA256'][:12]}-"
                f"{renderer_identity['echoSourceSHA']}-{plan['voicePlanID']}"
            )
            attempt_id = "7" * 64
            success_receipt = narration / (
                f"echo-render-success-{run_id}-{attempt_id}.json"
            )
            write_json(
                success_receipt,
                {
                    "schemaVersion": 3,
                    **renderer_identity,
                    "attemptID": attempt_id,
                    "runID": run_id,
                    "attemptReceiptSHA256": "8" * 64,
                    "inputReceiptFileName": f"echo-render-inputs-{run_id}.env",
                    "inputReceiptSHA256": "9" * 64,
                    "sourceEPUBFileName": built_epub.name,
                    "sourceEPUBSHA256": sha256(built_epub),
                    "artifactRelativePath": f"echo-renders/{run_id}/{attempt_id}",
                    "resumeStateFileName": f"echo-resume-state-{run_id}.json",
                    "resumeStateSHA256": "a" * 64,
                    "audiobookFileName": final_m4b.name,
                    "audiobookSHA256": sha256(final_m4b),
                    "sidecarFileName": sidecar.name,
                    "sidecarSHA256": sha256(sidecar),
                    "auditFileName": "fixture-ensemble.pronunciation-audit.json",
                    "auditSHA256": "b" * 64,
                },
            )

            preferences_path = run_root / "preferences.json"
            saved_preferences = fiction_voice_preferences.record_use(
                cast_path,
                built_epub,
                final_m4b,
                sidecar,
                success_receipt,
                "2026-08-08T14:00:00+00:00",
                preferences_path,
            )
            verified_cast = json.loads(cast_path.read_text(encoding="utf-8"))
            expected_verified = {
                "sourceEPUBSHA256": sha256(built_epub),
                "audiobookSHA256": sha256(final_m4b),
                "sidecarSHA256": sha256(sidecar),
                "voicePlanSHA256": plan["voicePlanSHA256"],
            }
            self.assertEqual(expected_verified, verified_cast["verifiedArtifacts"])
            self.assertEqual(1, len(saved_preferences["uses"]))
            self.assertEqual(
                [
                    {"chapter": 1, "voice": "bf_emma"},
                    {"chapter": 2, "voice": "am_michael"},
                    {"chapter": 3, "voice": "af_bella"},
                ],
                saved_preferences["uses"][0]["chapters"],
            )

            production = run_root / "production"
            for name in stage_echo_delivery.PRODUCTION_DIRECTORIES:
                (production / name).mkdir(parents=True)
            for path in source.iterdir():
                shutil.copy2(path, production / "source" / path.name)
            for path in checks.iterdir():
                shutil.copy2(path, production / "checks" / path.name)
            shutil.copy2(cast_path, production / "narration" / cast_path.name)
            shutil.copy2(
                success_receipt,
                production / "narration" / success_receipt.name,
            )
            shutil.copy2(portrait_cover, production / "covers/cover.png")
            shutil.copy2(square_cover, production / "covers/m4b-cover.png")

            library_root = run_root / "library"
            library_root.mkdir()
            private_delivery = library_root / "fixture-ensemble"
            stage_echo_delivery.stage_delivery(
                stage_echo_delivery.DeliveryRequest(
                    slug="fixture-ensemble",
                    edition_id="first-listen-2026-08-08",
                    m4b=final_m4b,
                    epub=built_epub,
                    alignment=sidecar,
                    cover=portrait_cover,
                    production=production,
                    destination=private_delivery,
                ),
                apply=True,
            )
            self.assertEqual(
                {
                    "fixture-ensemble.m4b",
                    "fixture-ensemble.epub",
                    "fixture-ensemble.alignment.json",
                    "cover.png",
                    "_production",
                },
                {path.name for path in private_delivery.iterdir()},
            )

            public_stage = Path(raw_root).resolve() / "public-stage"
            public_stage.mkdir()
            public_markdown = public_stage / built_markdown.name
            public_epub = public_stage / built_epub.name
            public_sidecar = public_stage / sidecar.name
            public_cover = public_stage / "cover.png"
            shutil.copy2(built_markdown, public_markdown)
            shutil.copy2(built_epub, public_epub)
            shutil.copy2(sidecar, public_sidecar)
            shutil.copy2(portrait_cover, public_cover)
            (public_stage / "README.md").write_text(
                verify_public_first_listen.FICTION_DISCLOSURE, encoding="utf-8"
            )

            staged_production = private_delivery / "_production"
            staged_cast = staged_production / "narration/voice-cast.json"
            staged_fiction_receipt = (
                staged_production / "checks/fiction-production-receipt.json"
            )
            staged_success_receipt = (
                staged_production / "narration" / success_receipt.name
            )
            edition_id = "first-listen-2026-08-08"
            publication = {
                "schemaVersion": 2,
                "packageKind": "fiction-audiobook",
                "slug": "fixture-ensemble",
                "editionId": edition_id,
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
                "disclosure": verify_public_first_listen.FICTION_DISCLOSURE,
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
                    "coverSHA256": sha256(public_cover),
                },
                "artifacts": {
                    "manuscript": {
                        "file": public_markdown.name,
                        "sha256": sha256(public_markdown),
                    },
                    "epub": {"file": public_epub.name, "sha256": sha256(public_epub)},
                    "alignment": {
                        "file": public_sidecar.name,
                        "sha256": sha256(public_sidecar),
                    },
                    "portraitCover": {
                        "file": public_cover.name,
                        "sha256": sha256(public_cover),
                    },
                },
                "release": {
                    "tag": f"fiction-fixture-ensemble-{edition_id}",
                    "assetFile": "fixture-ensemble.m4b",
                    "assetSHA256": sha256(private_delivery / "fixture-ensemble.m4b"),
                },
                "privateEvidence": {
                    "fictionReceiptSHA256": sha256(staged_fiction_receipt),
                    "voiceCastSHA256": sha256(staged_cast),
                    "voicePlanSHA256": plan["voicePlanSHA256"],
                    "echoSuccessReceiptSHA256": sha256(staged_success_receipt),
                },
            }
            write_json(public_stage / "publication.json", publication)

            self.assertEqual(built_markdown.read_bytes(), public_markdown.read_bytes())
            self.assertEqual(built_epub.read_bytes(), public_epub.read_bytes())
            self.assertEqual(portrait_cover.read_bytes(), public_cover.read_bytes())
            with zipfile.ZipFile(public_epub) as archive:
                self.assertEqual(public_cover.read_bytes(), archive.read("OEBPS/cover.png"))

            real_subprocess_run = subprocess.run

            def run_media_probe(command: list[str], **kwargs: object) -> object:
                if command[0] == "ffprobe":
                    return subprocess.CompletedProcess(
                        args=command,
                        returncode=0,
                        stdout=json.dumps(
                            {
                                "format": {"duration": "12.5"},
                                "chapters": [
                                    {"start_time": "0.0", "end_time": "12.5"}
                                ],
                            }
                        ),
                    )
                return real_subprocess_run(command, **kwargs)

            with mock.patch.object(
                verify_public_first_listen.subprocess,
                "run",
                side_effect=run_media_probe,
            ):
                verify_public_first_listen.verify_public_fiction_package(
                    public_stage,
                    private_delivery / "fixture-ensemble.m4b",
                    staged_cast,
                    staged_fiction_receipt,
                    staged_production / "source",
                    staged_success_receipt,
                )

            public_files = list(public_stage.iterdir())
            self.assertEqual(6, len(public_files))
            self.assertFalse(any(path.suffix == ".m4b" for path in public_files))
            self.assertFalse((public_stage / "m4b-cover.png").exists())
            public_bytes = b"".join(path.read_bytes() for path in public_files)
            self.assertNotIn(str(run_root).encode("utf-8"), public_bytes)
            self.assertNotIn(str(private_delivery).encode("utf-8"), public_bytes)


if __name__ == "__main__":
    unittest.main()
