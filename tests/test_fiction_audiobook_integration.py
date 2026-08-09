from __future__ import annotations

import hashlib
import json
import os
import re
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
import cover_receipts
import echo_voice_plan
import fiction_voice_preferences
import stage_echo_delivery
from skill.scripts import verify_public_first_listen
from tests.test_echo_narration_runtime import (
    AUDIT_VALIDATOR as RUNTIME_AUDIT_VALIDATOR,
    LEASE_HELPER as RUNTIME_LEASE_HELPER,
    PREFLIGHT as RUNTIME_PREFLIGHT,
    STATE_HELPER as RUNTIME_STATE_HELPER,
)
from tests import test_echo_narration_runtime as echo_narration_runtime


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def flat_file_bytes(directory: Path) -> dict[str, bytes]:
    entries = list(directory.iterdir())
    if any(not path.is_file() for path in entries):
        raise AssertionError(f"expected only regular files in {directory}")
    return {path.name: path.read_bytes() for path in entries}


def tree_file_bytes(directory: Path) -> dict[str, bytes]:
    return {
        path.relative_to(directory).as_posix(): path.read_bytes()
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }


class FictionAudiobookIntegrationTests(unittest.TestCase):
    def test_routed_pre_render_authoring_examples_pass_validate_cast(self) -> None:
        """The routed craft reference must be usable without inventing a schema."""
        craft = (
            ROOT
            / "skills"
            / "fiction-audiobook"
            / "references"
            / "express-fiction-craft.md"
        ).read_text(encoding="utf-8")

        def example(heading: str) -> dict[str, object]:
            match = re.search(
                re.escape(heading) + r".*?```json\n(.*?)\n```", craft, re.DOTALL
            )
            self.assertIsNotNone(match, f"missing routed {heading} example")
            assert match is not None
            return json.loads(match.group(1))

        plan = example("#### `echo-voice-plan.json` (schema 1)")
        cast = example("#### `voice-cast.json` (schema 2)")
        self.assertEqual(
            {
                "schemaVersion",
                "source",
                "defaultSpeakerID",
                "speakers",
                "assignments",
            },
            set(plan),
        )
        self.assertEqual(
            {
                "schemaVersion",
                "slug",
                "narrationMode",
                "sourceEPUBSHA256",
                "defaultSpeakerID",
                "speakers",
                "authoredVoicePlan",
                "resolvedVoicePlan",
                "verifiedArtifacts",
            },
            set(cast),
        )
        self.assertTrue(
            any("blocks" in assignment for assignment in plan["assignments"])
        )
        self.assertTrue(
            any("range" in assignment for assignment in plan["assignments"])
        )
        self.assertIsNone(cast["resolvedVoicePlan"])
        self.assertIsNone(cast["verifiedArtifacts"])
        self.assertIn(
            "`story-bible.md` under `## Narration attribution convention`", craft
        )

        with tempfile.TemporaryDirectory() as raw_root:
            root = Path(raw_root).resolve()
            epub = root / "frozen.epub"
            plan_path = root / "echo-voice-plan.json"
            cast_path = root / "voice-cast.json"
            preferences = root / "preferences.json"
            epub.write_bytes(b"frozen source fixture")
            source_sha256 = sha256(epub)
            plan_bytes = json.dumps(
                plan, sort_keys=True, indent=2
            ).replace("<SOURCE_EPUB_SHA256>", source_sha256).encode("utf-8") + b"\n"
            plan_path.write_bytes(plan_bytes)
            cast_bytes = (
                json.dumps(cast, sort_keys=True, indent=2)
                .replace("<SOURCE_EPUB_SHA256>", source_sha256)
                .replace("<AUTHORED_PLAN_SHA256>", sha256(plan_path))
                .encode("utf-8")
                + b"\n"
            )
            cast_path.write_bytes(cast_bytes)
            write_json(preferences, fiction_voice_preferences.initial_preferences())
            validated = subprocess.run(
                [
                    sys.executable,
                    str(
                        ROOT
                        / "skills"
                        / "fiction-audiobook"
                        / "scripts"
                        / "fiction_voice_preferences.py"
                    ),
                    "validate-cast",
                    "--cast",
                    str(cast_path),
                    "--voice-plan",
                    str(plan_path),
                    "--preferences",
                    str(preferences),
                    "--format",
                    "argv0",
                ],
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, validated.returncode, validated.stderr.decode())
            self.assertEqual(
                ["--voice-plan", str(plan_path)],
                [token.decode("utf-8") for token in validated.stdout.split(b"\0") if token],
            )

    def test_real_production_artifacts_remain_bound_through_private_and_public_delivery(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            run_root = Path(raw_root).resolve() / "private-run"
            chapters_dir = run_root / "chapters"
            research = run_root / "research"
            continuity = run_root / "continuity"
            revisions = run_root / "revisions"
            covers = run_root / "covers"
            dist = run_root / "dist"
            narration = run_root / "narration"
            for directory in (
                chapters_dir,
                research,
                continuity,
                revisions,
                covers,
                narration,
            ):
                directory.mkdir(parents=True)

            chapter_specs = (
                ("ch01.md", "Chapter One", "The lamp survived the first tide."),
                ("ch02.md", "Chapter Two", "The signal crossed the dark water."),
                ("ch03.md", "Chapter Three", "At dawn, the harbor answered."),
            )
            chapters: list[Path] = []
            for filename, title, body in chapter_specs:
                chapter = chapters_dir / filename
                chapter.write_text(f"## {title}\n\n{body}\n", encoding="utf-8")
                chapters.append(chapter)

            evidence = {
                "authorization": research / "unattended-decisions.json",
                "storyBible": run_root / "story-bible.md",
                "continuity": continuity / "final.md",
                "revisionReview": revisions / "full-manuscript-review.md",
                "proseQC": revisions / "full-prose-qc.md",
            }
            for name, path in evidence.items():
                path.write_text(f"{name}: verified\n", encoding="utf-8")

            fiction_receipt = research / "fiction-production-receipt.json"
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
            original_fiction_receipt = fiction_receipt.read_bytes()
            original_fiction_receipt_sha256 = hashlib.sha256(
                original_fiction_receipt
            ).hexdigest()

            def assert_fiction_receipt_unchanged() -> None:
                current = fiction_receipt.read_bytes()
                self.assertEqual(original_fiction_receipt, current)
                self.assertEqual(
                    original_fiction_receipt_sha256,
                    hashlib.sha256(current).hexdigest(),
                )

            portrait_cover = covers / "cover.png"
            square_cover = covers / "m4b-cover.png"
            Image.new("RGB", (1600, 2560), (20, 42, 68)).save(portrait_cover)
            Image.new("RGB", (2400, 2400), (68, 42, 20)).save(square_cover)

            build_book.build(
                chapters_dir,
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
            assert_fiction_receipt_unchanged()
            with zipfile.ZipFile(built_epub) as archive:
                self.assertEqual(
                    portrait_cover.read_bytes(), archive.read("OEBPS/cover.png")
                )
            verified_pair = cover_receipts.verify_receipt_free_pair(
                portrait_cover, square_cover, built_epub
            )
            self.assertEqual(sha256(portrait_cover), verified_pair.portrait_sha256)
            self.assertEqual(sha256(square_cover), verified_pair.square_sha256)
            self.assertEqual(sha256(built_epub), verified_pair.epub_sha256)
            self.assertEqual(
                ("portrait-png", "square-png", "epub-portrait-bytes"),
                verified_pair.checks,
            )
            assert_fiction_receipt_unchanged()

            source_epub_sha256 = sha256(built_epub)
            speakers = [
                {
                    "speakerID": "narrator",
                    "role": "Narrator",
                    "voiceID": "bf_emma",
                    "experimental": False,
                },
                {
                    "speakerID": "mara",
                    "role": "Mara",
                    "voiceID": "am_michael",
                    "experimental": False,
                },
                {
                    "speakerID": "ivo",
                    "role": "Ivo",
                    "voiceID": "af_bella",
                    "experimental": True,
                },
            ]
            authored_plan = narration / "echo-voice-plan.json"
            write_json(
                authored_plan,
                {
                    "schemaVersion": 1,
                    "source": {"epubSHA256": source_epub_sha256},
                    "defaultSpeakerID": "narrator",
                    "speakers": [
                        {"id": row["speakerID"], "voiceID": row["voiceID"]}
                        for row in speakers
                    ],
                    "assignments": [
                        {"speakerID": "mara", "blocks": ["s2-b3"]},
                        {"speakerID": "ivo", "ranges": ["s3-b1:s3-b2"]},
                    ],
                },
            )
            resolved_plan_sha256 = "b" * 64
            plan = {
                "blockCount": 3,
                "defaultVoice": "bf_emma",
                "sourceEPUBSHA256": source_epub_sha256,
                "voicePlanID": f"plan-{resolved_plan_sha256[:12]}",
                "voicePlanSHA256": resolved_plan_sha256,
            }
            canonical_plan = narration / (
                f"echo-voice-plan-plan-{resolved_plan_sha256}.json"
            )
            shutil.copy2(authored_plan, canonical_plan)
            resolution_receipt = narration / (
                f"echo-voice-plan-resolution-plan-{resolved_plan_sha256}.json"
            )
            resolution_receipt.write_text(
                json.dumps(plan, sort_keys=True, separators=(",", ":")) + "\n",
                encoding="utf-8",
            )
            cast = {
                "schemaVersion": 2,
                "slug": "fixture-ensemble",
                "narrationMode": "block",
                "sourceEPUBSHA256": source_epub_sha256,
                "defaultSpeakerID": "narrator",
                "speakers": speakers,
                "authoredVoicePlan": {
                    "fileName": authored_plan.name,
                    "sha256": sha256(authored_plan),
                },
                "resolvedVoicePlan": None,
                "verifiedArtifacts": None,
            }
            self.assertEqual(
                cast,
                fiction_voice_preferences.validate_block_cast(
                    cast,
                    authored_plan,
                    fiction_voice_preferences.initial_preferences(),
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
                f"{renderer_identity['echoSourceSHA']}-"
                f"plan-{plan['voicePlanSHA256']}"
            )
            attempt_id = "7" * 64
            success_receipt = narration / (
                f"echo-render-success-{run_id}-{attempt_id}.json"
            )
            input_receipt = narration / f"echo-render-inputs-{run_id}.env"
            input_receipt.write_text(
                "voice=bf_emma\n"
                "chapter_voices=\n"
                "voice_plan_mode=block\n"
                f"voice_plan_sha256={plan['voicePlanSHA256']}\n"
                f"voice_plan_id={plan['voicePlanID']}\n"
                f"voice_plan_block_count={plan['blockCount']}\n"
                f"voice_plan_canonical_path={canonical_plan}\n"
                f"voice_plan_canonical_sha256={sha256(canonical_plan)}\n"
                f"voice_plan_resolution_path={resolution_receipt}\n"
                f"voice_plan_resolution_sha256={sha256(resolution_receipt)}\n",
                encoding="utf-8",
            )
            audit = narration / "fixture-ensemble.pronunciation-audit.json"
            reel = (
                narration
                / "listening"
                / run_id
                / attempt_id
                / "fixture-ensemble.pronunciation-reel.m4a"
            )
            reel.parent.mkdir(parents=True)
            reel.write_bytes(b"fixture internal listening reel")
            capture = narration / f"audio-work-{run_id}" / ".anchors-ch1.json"
            capture.parent.mkdir()
            write_json(
                capture,
                {
                    "schemaVersion": 2,
                    "identity": {
                        "schemaVersion": 2,
                        "voicePlanSHA256": plan["voicePlanSHA256"],
                        "chapterVoicePlanSHA256": "c" * 64,
                    },
                },
            )
            write_json(
                audit,
                {
                    "schemaVersion": 7,
                    "renderVersion": 12,
                    "voice": "mixed",
                    "chapterVoices": {},
                    "voicePlanSHA256": plan["voicePlanSHA256"],
                    "blockVoices": {"s2-b3": "am_michael"},
                    "coverage": "complete",
                    "legacyChapterIndexes": [],
                    "audiobookFileName": final_m4b.name,
                    "audiobookSHA256": sha256(final_m4b),
                    "listeningReelFileName": reel.name,
                    "listeningReelSHA256": sha256(reel),
                    "watchCounts": {},
                    "decisions": [],
                    "diagnostics": [],
                },
            )
            write_json(
                success_receipt,
                {
                    "schemaVersion": 4,
                    **renderer_identity,
                    "attemptID": attempt_id,
                    "runID": run_id,
                    "attemptReceiptSHA256": "8" * 64,
                    "inputReceiptFileName": f"echo-render-inputs-{run_id}.env",
                    "inputReceiptSHA256": sha256(input_receipt),
                    "sourceEPUBFileName": built_epub.name,
                    "sourceEPUBSHA256": sha256(built_epub),
                    "artifactRelativePath": f"echo-renders/{run_id}/{attempt_id}",
                    "resumeStateFileName": f"echo-resume-state-{run_id}.json",
                    "resumeStateSHA256": "a" * 64,
                    "audiobookFileName": final_m4b.name,
                    "audiobookSHA256": sha256(final_m4b),
                    "sidecarFileName": sidecar.name,
                    "sidecarSHA256": sha256(sidecar),
                    "auditFileName": audit.name,
                    "auditSHA256": sha256(audit),
                    "reelFileName": reel.name,
                    "reelRelativePath": (
                        f"listening/{run_id}/{attempt_id}/{reel.name}"
                    ),
                    "reelSHA256": sha256(reel),
                    "voicePlanMode": "block",
                    "voicePlanID": plan["voicePlanID"],
                    "voicePlanSHA256": plan["voicePlanSHA256"],
                    "voicePlanBlockCount": plan["blockCount"],
                    "voicePlanCanonicalFileName": canonical_plan.name,
                    "voicePlanCanonicalSHA256": sha256(canonical_plan),
                    "voicePlanResolutionFileName": resolution_receipt.name,
                    "voicePlanResolutionSHA256": sha256(resolution_receipt),
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
            self.assertEqual(plan, verified_cast["resolvedVoicePlan"])
            self.assertEqual(
                plan,
                fiction_voice_preferences.validate_completed_cast(
                    verified_cast, cast_path=cast_path
                ),
            )
            persisted_preferences = fiction_voice_preferences.load_preferences(
                preferences_path
            )
            self.assertEqual(saved_preferences, persisted_preferences)
            self.assertEqual(1, len(persisted_preferences["uses"]))
            self.assertEqual(
                {
                    "slug": "fixture-ensemble",
                    "recordedAt": "2026-08-08T14:00:00+00:00",
                    "sourceEPUBSHA256": sha256(built_epub),
                    "audiobookSHA256": sha256(final_m4b),
                    "sidecarSHA256": sha256(sidecar),
                    "voicePlanSHA256": plan["voicePlanSHA256"],
                    "successReceiptSHA256": sha256(success_receipt),
                    "narrationMode": "block",
                    "speakers": [
                        {"speakerID": row["speakerID"], "voice": row["voiceID"]}
                        for row in speakers
                    ],
                },
                persisted_preferences["uses"][0],
            )
            assert_fiction_receipt_unchanged()

            production = run_root / "production"
            expected_production_directories = {
                "source",
                "checks",
                "narration",
                "covers",
                "publication",
                "previous",
            }
            for name in expected_production_directories:
                (production / name).mkdir(parents=True)
            for path in chapters:
                shutil.copy2(path, production / "source" / path.name)
            for path in (
                evidence["authorization"],
                evidence["storyBible"],
                evidence["continuity"],
            ):
                shutil.copy2(path, production / "source" / path.name)
            for path in (
                fiction_receipt,
                evidence["revisionReview"],
                evidence["proseQC"],
                audit,
            ):
                shutil.copy2(path, production / "checks" / path.name)
            for path in (
                cast_path,
                authored_plan,
                canonical_plan,
                resolution_receipt,
                input_receipt,
                success_receipt,
            ):
                shutil.copy2(path, production / "narration" / path.name)
            for path in (reel, capture):
                destination = production / "narration" / path.relative_to(narration)
                destination.parent.mkdir(parents=True)
                shutil.copy2(path, destination)
            shutil.copy2(portrait_cover, production / "covers/cover.png")
            shutil.copy2(square_cover, production / "covers/m4b-cover.png")
            publication_gate = {
                "decision": "private",
                "recordedAt": "2026-08-09T14:00:00+00:00",
                "publicGate": {
                    "originalFiction": True,
                    "noPrivateSource": True,
                    "noLivingPersonTarget": True,
                    "noLivingAuthorImitation": True,
                    "coverRightsVerified": True,
                },
                "reason": "fixture private-delivery evidence",
            }
            write_json(production / "publication/public-gate.json", publication_gate)
            expected_source_bytes = {
                "ch01.md": chapters[0].read_bytes(),
                "ch02.md": chapters[1].read_bytes(),
                "ch03.md": chapters[2].read_bytes(),
                "unattended-decisions.json": evidence["authorization"].read_bytes(),
                "story-bible.md": evidence["storyBible"].read_bytes(),
                "final.md": evidence["continuity"].read_bytes(),
            }
            expected_check_bytes = {
                "fiction-production-receipt.json": original_fiction_receipt,
                "full-manuscript-review.md": evidence["revisionReview"].read_bytes(),
                "full-prose-qc.md": evidence["proseQC"].read_bytes(),
                audit.name: audit.read_bytes(),
            }
            expected_narration_bytes = {
                "voice-cast.json": cast_path.read_bytes(),
                authored_plan.name: authored_plan.read_bytes(),
                canonical_plan.name: canonical_plan.read_bytes(),
                resolution_receipt.name: resolution_receipt.read_bytes(),
                input_receipt.name: input_receipt.read_bytes(),
                success_receipt.name: success_receipt.read_bytes(),
                reel.relative_to(narration).as_posix(): reel.read_bytes(),
                capture.relative_to(narration).as_posix(): capture.read_bytes(),
            }
            expected_cover_bytes = {
                "cover.png": portrait_cover.read_bytes(),
                "m4b-cover.png": square_cover.read_bytes(),
            }
            expected_publication_bytes = {
                "public-gate.json": (
                    json.dumps(publication_gate, indent=2, sort_keys=True) + "\n"
                ).encode("utf-8")
            }
            self.assertEqual(
                expected_production_directories,
                {path.name for path in production.iterdir()},
            )
            self.assertEqual(
                expected_source_bytes, flat_file_bytes(production / "source")
            )
            self.assertEqual(
                expected_check_bytes, flat_file_bytes(production / "checks")
            )
            self.assertEqual(
                expected_narration_bytes,
                tree_file_bytes(production / "narration"),
            )
            self.assertEqual(
                expected_cover_bytes, flat_file_bytes(production / "covers")
            )
            self.assertEqual(
                expected_publication_bytes,
                flat_file_bytes(production / "publication"),
            )
            self.assertEqual({}, flat_file_bytes(production / "previous"))
            assert_fiction_receipt_unchanged()

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
            staged_production = private_delivery / "_production"
            self.assertEqual(
                expected_production_directories,
                {path.name for path in staged_production.iterdir()},
            )
            delivery_manifest = (
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "slug": "fixture-ensemble",
                        "editionId": "first-listen-2026-08-08",
                        "rootArtifacts": {
                            "fixture-ensemble.m4b": sha256(final_m4b),
                            "fixture-ensemble.epub": sha256(built_epub),
                            "fixture-ensemble.alignment.json": sha256(sidecar),
                            "cover.png": sha256(portrait_cover),
                        },
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n"
            ).encode("utf-8")
            self.assertEqual(
                expected_source_bytes,
                flat_file_bytes(staged_production / "source"),
            )
            self.assertEqual(
                {**expected_check_bytes, "delivery-manifest.json": delivery_manifest},
                flat_file_bytes(staged_production / "checks"),
            )
            self.assertEqual(
                expected_narration_bytes,
                tree_file_bytes(staged_production / "narration"),
            )
            self.assertEqual(
                expected_cover_bytes,
                flat_file_bytes(staged_production / "covers"),
            )
            self.assertEqual(
                expected_publication_bytes,
                flat_file_bytes(staged_production / "publication"),
            )
            self.assertEqual({}, flat_file_bytes(staged_production / "previous"))
            staged_fiction_receipt = (
                staged_production / "checks/fiction-production-receipt.json"
            )
            self.assertEqual(
                original_fiction_receipt, staged_fiction_receipt.read_bytes()
            )
            self.assertEqual(
                original_fiction_receipt_sha256, sha256(staged_fiction_receipt)
            )
            for name, source_cover, dimensions in (
                ("cover.png", portrait_cover, (1600, 2560)),
                ("m4b-cover.png", square_cover, (2400, 2400)),
            ):
                staged_cover = staged_production / "covers" / name
                self.assertEqual(source_cover.read_bytes(), staged_cover.read_bytes())
                with Image.open(staged_cover) as image:
                    self.assertEqual("RGB", image.mode)
                    self.assertEqual(dimensions, image.size)
            assert_fiction_receipt_unchanged()

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

            staged_cast = staged_production / "narration/voice-cast.json"
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
                    "fictionReceiptSHA256": original_fiction_receipt_sha256,
                    "voiceCastSHA256": sha256(staged_cast),
                    "voicePlanSHA256": plan["voicePlanSHA256"],
                    "echoSuccessReceiptSHA256": sha256(staged_success_receipt),
                },
            }
            write_json(public_stage / "publication.json", publication)
            assert_fiction_receipt_unchanged()

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
                                    {"start_time": "0.0", "end_time": "4.0"},
                                    {"start_time": "4.0", "end_time": "8.0"},
                                    {"start_time": "8.0", "end_time": "12.5"},
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
                    fiction_receipt,
                    chapters_dir,
                    staged_success_receipt,
                )
            assert_fiction_receipt_unchanged()
            self.assertEqual(
                original_fiction_receipt, staged_fiction_receipt.read_bytes()
            )

            public_files = list(public_stage.iterdir())
            self.assertEqual(6, len(public_files))
            self.assertFalse(any(path.suffix == ".m4b" for path in public_files))
            self.assertFalse((public_stage / "m4b-cover.png").exists())
            public_bytes = b"".join(path.read_bytes() for path in public_files)
            self.assertNotIn(str(run_root).encode("utf-8"), public_bytes)
            self.assertNotIn(str(private_delivery).encode("utf-8"), public_bytes)

    def test_frozen_epub_block_cast_workflow_uses_real_installed_boundaries(
        self,
    ) -> None:
        """Exercise the resolver, env0, lease, wrapper, state, and audit seams."""
        harness = echo_narration_runtime.EchoPronunciationPreflightTests("runTest")
        harness.setUp()
        self.addCleanup(harness.doCleanups)
        harness.use_run_lane("fiction-audiobooks")
        run_root = harness.run_root
        portrait_cover = run_root / "dist" / "candidate-1" / "cover.png"
        square_cover = run_root / "dist" / "candidate-1" / "m4b-cover.png"
        chapters = run_root / "chapters"
        chapter = chapters / "ch01.md"
        chapter.write_text(
            "## Chapter One\n\n"
            "The beacon waited for the storm.\n\n"
            "“Go now,” Mara said.\n\n"
            "Ivo took the oars without answering.\n",
            encoding="utf-8",
        )
        build_book.build(
            chapters,
            run_root / "dist",
            "Fixture Block Ensemble",
            "Dan Fakkeldy",
            "",
            "fixture",
            cover=portrait_cover,
            m4b_cover=square_cover,
        )
        epub = run_root / "dist" / "fixture.epub"
        source_sha256 = sha256(epub)
        self.assertIn(
            "The beacon waited for the storm.\n\n"
            "“Go now,” Mara said.\n\n"
            "Ivo took the oars without answering.",
            (run_root / "dist" / "fixture.md").read_text(encoding="utf-8"),
        )

        environment = harness.environment()
        environment.pop("VOICE")
        environment.update(
            {
                "ECHO_RUN_LANE": "fiction-audiobook",
                "FAKE_EMIT_REEL": "1",
            }
        )
        inventory_command = (
            "set -euo pipefail\n"
            f"source {RUNTIME_PREFLIGHT}\n"
            'EPUB="$RUN_ROOT/dist/$SLUG.epub"\n'
            'EPUB_SHA256=$(/usr/bin/shasum -a 256 "$EPUB" | awk \'{print $1}\')\n'
            'INVENTORY="$RUN_ROOT/research/echo-block-inventory-$EPUB_SHA256.json"\n'
            "echo_pronunciation_resolve_installed_renderer 0\n"
            "echo_pronunciation_validate_renderer_paths\n"
            "echo_pronunciation_attest_renderer\n"
            "CANONICAL_LEASE_ROOT=$(echo_pronunciation_canonical_lease_root)\n"
            f'LEASE_HELPER="{RUNTIME_LEASE_HELPER}"\n'
            '"$LEASE_HELPER" --lock-root "$CANONICAL_LEASE_ROOT" \\\n'
            '  --resource "$ECHO_RENDERER_BUILD_ROOT" -- \\\n'
            '  /usr/bin/env "ECHO_RESOURCE_DIR=$ECHO_RESOURCE_DIR" \\\n'
            '  "$CLI" export-blocks --epub "$EPUB" --out "$INVENTORY"\n'
        )
        exported = subprocess.run(
            ["bash", "-c", inventory_command],
            cwd=harness.explainer,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, exported.returncode, exported.stderr)
        inventory = (
            run_root / "research" / f"echo-block-inventory-{source_sha256}.json"
        )
        inventory_payload = json.loads(inventory.read_text(encoding="utf-8"))
        self.assertEqual(1, inventory_payload["version"])
        self.assertEqual(source_sha256, inventory_payload["source"]["epubSHA256"])
        self.assertEqual(["s2-b3", "s2-b4", "s2-b5"], [
            block["id"] for block in inventory_payload["blocks"]
        ])
        self.assertTrue(
            all("speaker" not in block for block in inventory_payload["blocks"])
        )
        self.assertIn("CALL=export-blocks:--epub", harness.installed_probe_log.read_text())

        narration = run_root / "_production" / "narration"
        narration.mkdir(parents=True)
        speakers = [
            {
                "speakerID": "narrator",
                "role": "Narrator",
                "voiceID": "am_michael",
                "experimental": False,
            },
            {
                "speakerID": "mara",
                "role": "Mara",
                "voiceID": "bf_emma",
                "experimental": False,
            },
            {
                "speakerID": "ivo",
                "role": "Ivo",
                "voiceID": "bm_george",
                "experimental": False,
            },
        ]
        authored_plan = narration / "echo-voice-plan.json"
        write_json(
            authored_plan,
            {
                "schemaVersion": 1,
                "source": {"epubSHA256": source_sha256},
                "defaultSpeakerID": "narrator",
                "speakers": [
                    {"id": row["speakerID"], "voiceID": row["voiceID"]}
                    for row in speakers
                ],
                "assignments": [
                    {"speakerID": "mara", "blocks": ["s2-b3"]},
                    {
                        "speakerID": "ivo",
                        "range": {"start": "s2-b4", "end": "s2-b4"},
                    },
                ],
            },
        )
        cast = {
            "schemaVersion": 2,
            "slug": "fixture",
            "narrationMode": "block",
            "sourceEPUBSHA256": source_sha256,
            "defaultSpeakerID": "narrator",
            "speakers": speakers,
            "authoredVoicePlan": {
                "fileName": authored_plan.name,
                "sha256": sha256(authored_plan),
            },
            "resolvedVoicePlan": None,
            "verifiedArtifacts": None,
        }
        cast_path = narration / "voice-cast.json"
        write_json(cast_path, cast)
        preferences = run_root / "preferences.json"
        write_json(preferences, fiction_voice_preferences.initial_preferences())
        validated = subprocess.run(
            [
                sys.executable,
                str(
                    ROOT
                    / "skills"
                    / "fiction-audiobook"
                    / "scripts"
                    / "fiction_voice_preferences.py"
                ),
                "validate-cast",
                "--cast",
                str(cast_path),
                "--voice-plan",
                str(authored_plan),
                "--preferences",
                str(preferences),
                "--format",
                "argv0",
            ],
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, validated.returncode, validated.stderr.decode())
        voice_arguments = [
            token.decode("utf-8") for token in validated.stdout.split(b"\0") if token
        ]
        self.assertEqual(["--voice-plan", str(authored_plan)], voice_arguments)

        first_sha256 = "0123456789ab" + "b" * 52
        harness.fake_voice_plan_sha.write_text(first_sha256 + "\n", encoding="utf-8")
        first_log = run_root / "research" / "first-render.log"
        first_environment = dict(environment, FAKE_NARRATE_LOG=str(first_log))
        first = harness.run_narrate(*voice_arguments, environment=first_environment)
        self.assertEqual(0, first.returncode, first.stderr)
        self.assertNotIn("VOICE", environment)
        rendered_arguments = [
            line.removeprefix("ARG=")
            for line in first_log.read_text(encoding="utf-8").splitlines()
            if line.startswith("ARG=")
        ]
        self.assertNotIn("--voice", rendered_arguments)
        self.assertIn("--voice-plan", rendered_arguments)

        research = run_root / "research"
        first_input = next(
            candidate
            for candidate in research.glob("echo-render-inputs-*.env")
            if harness.receipt_fields(candidate)["voice_plan_sha256"] == first_sha256
        )
        first_fields = harness.receipt_fields(first_input)
        first_selector = json.loads(
            (research / "echo-render-current-accepted.json").read_text(encoding="utf-8")
        )
        first_run_id = first_fields["run_id"]
        self.assertTrue(first_run_id.endswith(f"plan-{first_sha256}"))
        first_attempt = research / "echo-render-current-attempt.json"
        first_success = research / first_selector["successReceiptFileName"]
        first_state = research / f"echo-resume-state-{first_run_id}.json"
        first_artifacts = run_root / "dist" / first_selector["artifactRelativePath"]
        first_reel = research / "listening" / first_selector["runID"] / first_selector[
            "attemptID"
        ] / "fixture.pronunciation-reel.m4b"
        first_audit = first_artifacts / "fixture.pronunciation-audit.json"
        first_success_payload = json.loads(first_success.read_text(encoding="utf-8"))
        first_audit_payload = json.loads(first_audit.read_text(encoding="utf-8"))
        self.assertEqual(4, first_success_payload["schemaVersion"])
        self.assertEqual(2, json.loads(
            (Path(first_fields["work_dir"]) / ".anchors-ch0.json").read_text(
                encoding="utf-8"
            )
        )["identity"]["schemaVersion"])
        self.assertEqual(7, first_audit_payload["schemaVersion"])
        self.assertEqual(3, len(first_audit_payload["blockVoices"]))
        self.assertEqual(
            first_success_payload["voicePlanBlockCount"],
            len(first_audit_payload["blockVoices"]),
        )

        evidence = subprocess.run(
            [
                "/usr/local/bin/python3",
                str(RUNTIME_STATE_HELPER),
                "block-delivery-evidence",
                "--attempt",
                str(first_attempt),
                "--selector",
                str(research / "echo-render-current-accepted.json"),
                "--receipt",
                str(first_success),
                "--input-receipt",
                str(first_input),
                "--format",
                "env0",
            ],
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, evidence.returncode, evidence.stderr.decode())
        evidence_fields = dict(
            token.decode("utf-8").split("=", 1)
            for token in evidence.stdout.split(b"\0")
            if token
        )
        self.assertEqual("block", evidence_fields["voice_plan_mode"])
        self.assertEqual(
            first_success_payload["reelRelativePath"],
            evidence_fields["reel_relative_path"],
        )
        self.assertEqual(first_sha256, evidence_fields["voice_plan_sha256"])
        self.assertEqual("3", evidence_fields["voice_plan_block_count"])

        delivered = subprocess.run(
            [
                "/usr/local/bin/python3",
                str(RUNTIME_STATE_HELPER),
                "verify-delivery",
                "--attempt",
                str(first_attempt),
                "--selector",
                str(research / "echo-render-current-accepted.json"),
                "--receipt",
                str(first_success),
                "--input-receipt",
                str(first_input),
                "--state-receipt",
                str(first_state),
                "--epub",
                str(epub),
                "--audiobook",
                str(first_artifacts / "fixture.m4b"),
                "--sidecar",
                str(first_artifacts / "fixture.alignment.json"),
                "--audit",
                str(first_audit),
                "--reel",
                str(first_reel),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, delivered.returncode, delivered.stderr)
        audited = subprocess.run(
            [
                "/usr/local/bin/python3",
                str(RUNTIME_AUDIT_VALIDATOR),
                str(first_audit),
                "--audiobook",
                str(first_artifacts / "fixture.m4b"),
                "--reel",
                str(first_reel),
                "--voice-plan-sha256",
                evidence_fields["voice_plan_sha256"],
                "--block-count",
                evidence_fields["voice_plan_block_count"],
            ],
            env=first_environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, audited.returncode, audited.stderr)

        recorded = fiction_voice_preferences.record_use(
            cast_path,
            epub,
            first_artifacts / "fixture.m4b",
            first_artifacts / "fixture.alignment.json",
            first_success,
            "2026-08-09T14:00:00+00:00",
            preferences,
        )
        self.assertEqual(first_sha256, recorded["uses"][0]["voicePlanSHA256"])

        second_sha256 = "0123456789ab" + "c" * 52
        harness.fake_voice_plan_sha.write_text(second_sha256 + "\n", encoding="utf-8")
        second_environment = dict(environment, FAKE_NARRATE_LOG=str(run_root / "research" / "second-render.log"))
        refused_resume = harness.run_narrate(
            *voice_arguments,
            "--resume",
            "--resume-state",
            str(first_state),
            environment=second_environment,
        )
        self.assertEqual(64, refused_resume.returncode, refused_resume.stderr)
        self.assertIn("canonical", refused_resume.stderr)
        second = harness.run_narrate(*voice_arguments, environment=second_environment)
        self.assertEqual(0, second.returncode, second.stderr)
        second_input = next(
            candidate
            for candidate in research.glob("echo-render-inputs-*.env")
            if harness.receipt_fields(candidate)["voice_plan_sha256"] == second_sha256
        )
        second_fields = harness.receipt_fields(second_input)
        self.assertEqual(first_fields["voice_plan_id"], second_fields["voice_plan_id"])
        for field in (
            "run_id",
            "work_dir",
            "narration_db",
            "voice_plan_canonical_path",
            "voice_plan_resolution_path",
        ):
            with self.subTest(field=field):
                self.assertNotEqual(first_fields[field], second_fields[field])
        self.assertTrue((Path(first_fields["work_dir"]) / ".anchors-ch0.json").is_file())
        self.assertTrue((Path(second_fields["work_dir"]) / ".anchors-ch0.json").is_file())

        production = run_root / "_production"
        for name in ("source", "checks", "narration", "covers", "publication", "previous"):
            (production / name).mkdir(parents=True, exist_ok=True)
        shutil.copy2(chapter, production / "source" / chapter.name)
        for name in ("brief.md", "story-bible.md", "outline.md"):
            (production / "source" / name).write_text("fixture\n", encoding="utf-8")
        shutil.copy2(first_audit, production / "checks" / first_audit.name)
        (production / "checks" / "verify-delivery.txt").write_text(
            delivered.stdout, encoding="utf-8"
        )
        (production / "checks" / "audit-validator.txt").write_text(
            audited.stdout, encoding="utf-8"
        )
        for path in (
            cast_path,
            authored_plan,
            Path(first_fields["voice_plan_canonical_path"]),
            Path(first_fields["voice_plan_resolution_path"]),
            first_input,
            first_attempt,
            first_state,
            first_success,
            research / "echo-render-current-accepted.json",
            first_artifacts / "fixture.alignment.json",
            first_reel,
            Path(first_fields["work_dir"]) / ".anchors-ch0.json",
        ):
            destination = production / "narration" / path.name
            if path == first_reel:
                destination = production / "narration" / "listening" / path.name
            elif path.name == ".anchors-ch0.json":
                destination = production / "narration" / "captures" / path.name
            destination.parent.mkdir(parents=True, exist_ok=True)
            if path != destination:
                shutil.copy2(path, destination)
        shutil.copy2(portrait_cover, production / "covers" / "cover.png")
        shutil.copy2(square_cover, production / "covers" / "m4b-cover.png")
        write_json(
            production / "publication" / "public-gate.json",
            {
                "decision": "private",
                "recordedAt": "2026-08-09T14:01:00+00:00",
                "publicGate": {
                    "originalFiction": True,
                    "noPrivateSource": False,
                    "noLivingPersonTarget": True,
                    "noLivingAuthorImitation": True,
                    "coverRightsVerified": True,
                },
                "reason": "controlled fixture remains private",
            },
        )
        self.assertTrue((production / "publication" / "public-gate.json").is_file())
        library = run_root / "library"
        library.mkdir()
        destination = library / "fixture"
        stage_echo_delivery.stage_delivery(
            stage_echo_delivery.DeliveryRequest(
                slug="fixture",
                edition_id="fixture-private-v1",
                m4b=first_artifacts / "fixture.m4b",
                epub=epub,
                alignment=first_artifacts / "fixture.alignment.json",
                cover=portrait_cover,
                production=production,
                destination=destination,
            ),
            apply=True,
        )
        self.assertEqual(
            {
                "fixture.m4b",
                "fixture.epub",
                "fixture.alignment.json",
                "cover.png",
                "_production",
            },
            {path.name for path in destination.iterdir()},
        )
        staged_narration = destination / "_production" / "narration"
        self.assertTrue((staged_narration / "listening" / first_reel.name).is_file())
        self.assertTrue((staged_narration / "captures" / ".anchors-ch0.json").is_file())
        self.assertTrue(
            (destination / "_production" / "publication" / "public-gate.json").is_file()
        )

    def test_three_chapter_block_workflow_is_public_safe_and_identity_bound(
        self,
    ) -> None:
        """Keep the complete character-cast workflow inside one fake renderer fixture."""
        harness = echo_narration_runtime.EchoPronunciationPreflightTests("runTest")
        harness.setUp()
        self.addCleanup(harness.doCleanups)
        harness.use_run_lane("fiction-audiobooks")
        run_root = harness.run_root
        chapters = run_root / "chapters"
        chapter_specs = (
            (
                "ch01.md",
                "Chapter One",
                (
                    "The narrator watched the rain find the harbor.",
                    "“The lantern is lit,” Mara said.",
                    "Ivo folded the chart and faced the tide.",
                ),
            ),
            (
                "ch02.md",
                "Chapter Two",
                (
                    "The narrator counted three distant bells.",
                    "“We leave at dawn,” Mara said.",
                    "Ivo carried the oars down to the boat.",
                ),
            ),
            (
                "ch03.md",
                "Chapter Three",
                (
                    "The narrator found the harbor waiting quietly.",
                    "“The signal held,” Mara said.",
                    "Ivo smiled and tied the last knot.",
                ),
            ),
        )
        for filename, title, paragraphs in chapter_specs:
            (chapters / filename).write_text(
                f"## {title}\n\n" + "\n\n".join(paragraphs) + "\n",
                encoding="utf-8",
            )

        portrait_cover = run_root / "dist" / "candidate-1" / "cover.png"
        square_cover = run_root / "dist" / "candidate-1" / "m4b-cover.png"
        build_book.build(
            chapters,
            run_root / "dist",
            "Fixture Three Chapter Ensemble",
            "Dan Fakkeldy",
            "",
            "fixture",
            cover=portrait_cover,
            m4b_cover=square_cover,
            contributor="GPT-5.6",
        )
        epub = run_root / "dist" / "fixture.epub"
        markdown = run_root / "dist" / "fixture.md"
        source_sha256 = sha256(epub)
        self.assertEqual(3, len(list(chapters.glob("ch*.md"))))
        for _filename, _title, paragraphs in chapter_specs:
            for paragraph in paragraphs:
                self.assertIn(paragraph, markdown.read_text(encoding="utf-8"))

        research = run_root / "research"
        continuity = run_root / "continuity"
        revisions = run_root / "revisions"
        continuity.mkdir()
        revisions.mkdir()
        evidence = {
            "authorization": research / "unattended-decisions.json",
            "storyBible": run_root / "story-bible.md",
            "continuity": continuity / "final.md",
            "revisionReview": revisions / "full-manuscript-review.md",
            "proseQC": revisions / "full-prose-qc.md",
        }
        for name, path in evidence.items():
            path.write_text(f"{name}: verified\n", encoding="utf-8")
        fiction_receipt = research / "fiction-production-receipt.json"
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
                    filename: sha256(chapters / filename)
                    for filename, _title, _paragraphs in chapter_specs
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

        environment = harness.environment()
        environment.pop("VOICE")
        environment.update(
            {
                "ECHO_RUN_LANE": "fiction-audiobook",
                "FAKE_EMIT_REEL": "1",
            }
        )
        inventory_command = (
            "set -euo pipefail\n"
            f"source {RUNTIME_PREFLIGHT}\n"
            'EPUB="$RUN_ROOT/dist/$SLUG.epub"\n'
            'EPUB_SHA256=$(/usr/bin/shasum -a 256 "$EPUB" | awk \'{print $1}\')\n'
            'INVENTORY="$RUN_ROOT/research/echo-block-inventory-$EPUB_SHA256.json"\n'
            "echo_pronunciation_resolve_installed_renderer 0\n"
            "echo_pronunciation_validate_renderer_paths\n"
            "echo_pronunciation_attest_renderer\n"
            "CANONICAL_LEASE_ROOT=$(echo_pronunciation_canonical_lease_root)\n"
            f'LEASE_HELPER="{RUNTIME_LEASE_HELPER}"\n'
            '"$LEASE_HELPER" --lock-root "$CANONICAL_LEASE_ROOT" \\\n'
            '  --resource "$ECHO_RENDERER_BUILD_ROOT" -- \\\n'
            '  /usr/bin/env "ECHO_RESOURCE_DIR=$ECHO_RESOURCE_DIR" \\\n'
            '  "$CLI" export-blocks --epub "$EPUB" --out "$INVENTORY"\n'
        )
        exported = subprocess.run(
            ["bash", "-c", inventory_command],
            cwd=harness.explainer,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, exported.returncode, exported.stderr)
        inventory = research / f"echo-block-inventory-{source_sha256}.json"
        inventory_payload = json.loads(inventory.read_text(encoding="utf-8"))
        self.assertEqual(source_sha256, inventory_payload["source"]["epubSHA256"])
        self.assertEqual(["s2-b3", "s2-b4", "s2-b5"], [
            block["id"] for block in inventory_payload["blocks"]
        ])
        self.assertTrue(
            all(
                not any(
                    forbidden in key.lower()
                    for forbidden in ("speaker", "voice", "plan")
                )
                for block in inventory_payload["blocks"]
                for key in block
            )
        )

        narration = run_root / "_production" / "narration"
        narration.mkdir(parents=True)
        speakers = [
            {
                "speakerID": "narrator",
                "role": "Narrator",
                "voiceID": "am_michael",
                "experimental": False,
            },
            {
                "speakerID": "mara",
                "role": "Mara",
                "voiceID": "bf_emma",
                "experimental": False,
            },
            {
                "speakerID": "ivo",
                "role": "Ivo",
                "voiceID": "bm_george",
                "experimental": False,
            },
        ]
        authored_plan = narration / "echo-voice-plan.json"
        write_json(
            authored_plan,
            {
                "schemaVersion": 1,
                "source": {"epubSHA256": source_sha256},
                "defaultSpeakerID": "narrator",
                "speakers": [
                    {"id": row["speakerID"], "voiceID": row["voiceID"]}
                    for row in speakers
                ],
                "assignments": [
                    {"speakerID": "mara", "blocks": ["s2-b3"]},
                    {
                        "speakerID": "ivo",
                        "range": {"start": "s2-b4", "end": "s2-b5"},
                    },
                ],
            },
        )
        cast_path = narration / "voice-cast.json"
        write_json(
            cast_path,
            {
                "schemaVersion": 2,
                "slug": "fixture",
                "narrationMode": "block",
                "sourceEPUBSHA256": source_sha256,
                "defaultSpeakerID": "narrator",
                "speakers": speakers,
                "authoredVoicePlan": {
                    "fileName": authored_plan.name,
                    "sha256": sha256(authored_plan),
                },
                "resolvedVoicePlan": None,
                "verifiedArtifacts": None,
            },
        )
        preferences = run_root / "preferences.json"
        write_json(preferences, fiction_voice_preferences.initial_preferences())
        validated = subprocess.run(
            [
                sys.executable,
                str(
                    ROOT
                    / "skills"
                    / "fiction-audiobook"
                    / "scripts"
                    / "fiction_voice_preferences.py"
                ),
                "validate-cast",
                "--cast",
                str(cast_path),
                "--voice-plan",
                str(authored_plan),
                "--preferences",
                str(preferences),
                "--format",
                "argv0",
            ],
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, validated.returncode, validated.stderr.decode())
        voice_arguments = [
            token.decode("utf-8") for token in validated.stdout.split(b"\0") if token
        ]
        self.assertEqual(["--voice-plan", str(authored_plan)], voice_arguments)

        first_sha256 = "0123456789ab" + "b" * 52
        harness.fake_voice_plan_sha.write_text(first_sha256 + "\n", encoding="utf-8")
        partial = harness.run_narrate(
            *voice_arguments,
            environment=dict(environment, FAKE_NARRATE_EXIT="2"),
        )
        self.assertEqual(2, partial.returncode, partial.stderr)
        first_input = next(
            candidate
            for candidate in research.glob("echo-render-inputs-*.env")
            if harness.receipt_fields(candidate)["voice_plan_sha256"] == first_sha256
        )
        first_fields = harness.receipt_fields(first_input)
        first_state = research / f"echo-resume-state-{first_fields['run_id']}.json"
        first_capture = Path(first_fields["work_dir"]) / ".anchors-ch0.json"
        self.assertTrue(first_capture.is_file())
        self.assertEqual(
            2,
            json.loads(first_capture.read_text(encoding="utf-8"))["identity"][
                "schemaVersion"
            ],
        )
        partial_state = json.loads(first_state.read_text(encoding="utf-8"))
        self.assertEqual(4, partial_state["schemaVersion"])
        self.assertEqual(first_sha256, partial_state["voicePlanSHA256"])

        resumed = harness.run_narrate(
            "--resume",
            "--resume-state",
            str(first_state),
            *voice_arguments,
            environment=environment,
        )
        self.assertEqual(0, resumed.returncode, resumed.stderr)
        selector = json.loads(
            (research / "echo-render-current-accepted.json").read_text(
                encoding="utf-8"
            )
        )
        success_receipt = research / selector["successReceiptFileName"]
        success = json.loads(success_receipt.read_text(encoding="utf-8"))
        state = json.loads(first_state.read_text(encoding="utf-8"))
        resolution = json.loads(
            Path(first_fields["voice_plan_resolution_path"]).read_text(
                encoding="utf-8"
            )
        )
        authored_payload = json.loads(authored_plan.read_text(encoding="utf-8"))
        self.assertEqual(source_sha256, authored_payload["source"]["epubSHA256"])
        self.assertEqual(source_sha256, resolution["sourceEPUBSHA256"])
        self.assertEqual(source_sha256, success["sourceEPUBSHA256"])
        self.assertEqual(source_sha256, sha256(epub))
        for value in (
            first_fields["voice_plan_sha256"],
            state["voicePlanSHA256"],
            success["voicePlanSHA256"],
        ):
            self.assertEqual(first_sha256, value)

        artifact_root = run_root / "dist" / selector["artifactRelativePath"]
        self.assertEqual(
            {
                "fixture.m4b",
                "fixture.alignment.json",
                "fixture.pronunciation-audit.json",
            },
            {path.name for path in artifact_root.iterdir()},
        )
        alignment = json.loads(
            (artifact_root / "fixture.alignment.json").read_text(encoding="utf-8")
        )
        self.assertEqual([{"blockId": "s2-b3", "timestamp": 0}], alignment)
        self.assertTrue(
            all(
                not any(
                    forbidden in key.lower()
                    for forbidden in ("speaker", "voice", "plan")
                )
                for anchor in alignment
                for key in anchor
            )
        )
        audit = json.loads(
            (artifact_root / "fixture.pronunciation-audit.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(7, audit["schemaVersion"])
        self.assertEqual(first_sha256, audit["voicePlanSHA256"])
        self.assertEqual(3, len(audit["blockVoices"]))

        recorded = fiction_voice_preferences.record_use(
            cast_path,
            epub,
            artifact_root / "fixture.m4b",
            artifact_root / "fixture.alignment.json",
            success_receipt,
            "2026-08-09T14:00:00+00:00",
            preferences,
        )
        completed_cast = json.loads(cast_path.read_text(encoding="utf-8"))
        self.assertEqual(first_sha256, recorded["uses"][0]["voicePlanSHA256"])
        self.assertEqual(
            first_sha256,
            completed_cast["resolvedVoicePlan"]["voicePlanSHA256"],
        )
        self.assertEqual(
            source_sha256,
            completed_cast["verifiedArtifacts"]["sourceEPUBSHA256"],
        )

        first_attempt = research / "echo-render-current-attempt.json"
        first_attempt_bytes = first_attempt.read_bytes()
        accepted_selector = research / "echo-render-current-accepted.json"
        accepted_selector_bytes = accepted_selector.read_bytes()
        changed_sha256 = "0123456789ab" + "c" * 52
        harness.fake_voice_plan_sha.write_text(changed_sha256 + "\n", encoding="utf-8")
        changed = harness.run_narrate(
            "--resume",
            "--resume-state",
            str(first_state),
            *voice_arguments,
            environment=environment,
        )
        self.assertEqual(64, changed.returncode, changed.stderr)
        changed_input = next(
            candidate
            for candidate in research.glob("echo-render-inputs-*.env")
            if harness.receipt_fields(candidate)["voice_plan_sha256"] == changed_sha256
        )
        changed_fields = harness.receipt_fields(changed_input)
        self.assertNotEqual(first_fields["run_id"], changed_fields["run_id"])
        self.assertNotEqual(first_input, changed_input)
        self.assertFalse(Path(changed_fields["work_dir"]).exists())
        self.assertFalse(Path(changed_fields["narration_db"]).exists())
        self.assertFalse(
            (research / f"echo-resume-state-{changed_fields['run_id']}.json").exists()
        )
        self.assertEqual(first_attempt_bytes, first_attempt.read_bytes())
        self.assertEqual(accepted_selector_bytes, accepted_selector.read_bytes())
        self.assertTrue(first_capture.is_file())
        self.assertTrue(Path(first_fields["narration_db"]).is_file())
        self.assertTrue(success_receipt.is_file())

        production = run_root / "_production"
        for name in ("source", "checks", "narration", "covers", "publication", "previous"):
            (production / name).mkdir(parents=True, exist_ok=True)
        for filename, _title, _paragraphs in chapter_specs:
            shutil.copy2(chapters / filename, production / "source" / filename)
        for path in evidence.values():
            shutil.copy2(path, production / "source" / path.name)
        for path in (
            fiction_receipt,
            artifact_root / "fixture.pronunciation-audit.json",
        ):
            shutil.copy2(path, production / "checks" / path.name)
        first_reel = research / success["reelRelativePath"]
        for path in (
            cast_path,
            authored_plan,
            Path(first_fields["voice_plan_canonical_path"]),
            Path(first_fields["voice_plan_resolution_path"]),
            first_input,
            first_attempt,
            first_state,
            success_receipt,
            research / "echo-render-current-accepted.json",
            artifact_root / "fixture.alignment.json",
        ):
            destination = production / "narration" / path.name
            if path != destination:
                shutil.copy2(path, destination)
        captures = production / "narration" / "captures"
        captures.mkdir()
        shutil.copy2(first_capture, captures / first_capture.name)
        listening = production / "narration" / "listening"
        listening.mkdir()
        shutil.copy2(first_reel, listening / first_reel.name)
        shutil.copy2(portrait_cover, production / "covers" / "cover.png")
        shutil.copy2(square_cover, production / "covers" / "m4b-cover.png")
        write_json(
            production / "publication" / "public-gate.json",
            {
                "decision": "private",
                "recordedAt": "2026-08-09T14:01:00+00:00",
                "publicGate": {
                    "originalFiction": True,
                    "noPrivateSource": False,
                    "noLivingPersonTarget": True,
                    "noLivingAuthorImitation": True,
                    "coverRightsVerified": True,
                },
                "reason": "controlled fixture remains private",
            },
        )
        icloud_root = run_root / "icloud"
        icloud_root.mkdir()
        private_delivery = icloud_root / "fixture"
        stage_echo_delivery.stage_delivery(
            stage_echo_delivery.DeliveryRequest(
                slug="fixture",
                edition_id="fixture-private-v1",
                m4b=artifact_root / "fixture.m4b",
                epub=epub,
                alignment=artifact_root / "fixture.alignment.json",
                cover=portrait_cover,
                production=production,
                destination=private_delivery,
            ),
            apply=True,
        )
        self.assertEqual(
            {
                "fixture.m4b",
                "fixture.epub",
                "fixture.alignment.json",
                "cover.png",
                "_production",
            },
            {path.name for path in private_delivery.iterdir()},
        )
        self.assertTrue(
            (private_delivery / "_production" / "narration" / "captures" / first_capture.name).is_file()
        )
        self.assertTrue(
            (private_delivery / "_production" / "narration" / "listening" / first_reel.name).is_file()
        )

        public_stage = run_root / "public-candidate"
        public_stage.mkdir()
        public_markdown = public_stage / markdown.name
        public_epub = public_stage / epub.name
        public_alignment = public_stage / "fixture.alignment.json"
        public_cover = public_stage / "cover.png"
        for source, destination in (
            (markdown, public_markdown),
            (epub, public_epub),
            (artifact_root / "fixture.alignment.json", public_alignment),
            (portrait_cover, public_cover),
        ):
            shutil.copy2(source, destination)
        (public_stage / "README.md").write_text(
            verify_public_first_listen.FICTION_DISCLOSURE,
            encoding="utf-8",
        )
        publication = {
            "schemaVersion": 2,
            "packageKind": "fiction-audiobook",
            "slug": "fixture",
            "editionId": "fixture-public-v1",
            "publicationStatus": "public-first-listen",
            "humanReadingStatus": "pending",
            "humanListeningStatus": "pending",
            "classification": "public-safe",
            "permissionToPublish": True,
            "permissionGrantedAt": "2026-08-09T14:02:00+00:00",
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
                    "file": public_alignment.name,
                    "sha256": sha256(public_alignment),
                },
                "portraitCover": {
                    "file": public_cover.name,
                    "sha256": sha256(public_cover),
                },
            },
            "release": {
                "tag": "fiction-fixture-fixture-public-v1",
                "assetFile": "fixture.m4b",
                "assetSHA256": sha256(private_delivery / "fixture.m4b"),
            },
            "privateEvidence": {
                "fictionReceiptSHA256": sha256(fiction_receipt),
                "voiceCastSHA256": sha256(cast_path),
                "voicePlanSHA256": first_sha256,
                "echoSuccessReceiptSHA256": sha256(success_receipt),
            },
        }
        write_json(public_stage / "publication.json", publication)
        self.assertEqual(first_sha256, publication["privateEvidence"]["voicePlanSHA256"])
        self.assertEqual("pending", publication["humanReadingStatus"])
        self.assertEqual("pending", publication["humanListeningStatus"])

        real_subprocess_run = subprocess.run

        def run_media_probe(command: list[str], **kwargs: object) -> object:
            if command[0] == "ffprobe":
                return subprocess.CompletedProcess(
                    args=command,
                    returncode=0,
                    stdout=json.dumps(
                        {
                            "format": {"duration": "12.0"},
                            "chapters": [
                                {"start_time": "0.0", "end_time": "4.0"},
                                {"start_time": "4.0", "end_time": "8.0"},
                                {"start_time": "8.0", "end_time": "12.0"},
                            ],
                        }
                    ),
                    stderr="",
                )
            return real_subprocess_run(command, **kwargs)

        with mock.patch.object(
            verify_public_first_listen.subprocess,
            "run",
            side_effect=run_media_probe,
        ):
            verify_public_first_listen.verify_public_fiction_package(
                public_stage,
                private_delivery / "fixture.m4b",
                cast_path,
                fiction_receipt,
                chapters,
                success_receipt,
            )
        public_files = list(public_stage.iterdir())
        self.assertEqual(6, len(public_files))
        self.assertEqual(
            {
                "README.md",
                "cover.png",
                "fixture.alignment.json",
                "fixture.epub",
                "fixture.md",
                "publication.json",
            },
            {path.name for path in public_files},
        )
        self.assertFalse(any(path.suffix == ".m4b" for path in public_files))
        public_bytes = b"".join(path.read_bytes() for path in public_files)
        self.assertNotIn(str(run_root).encode("utf-8"), public_bytes)
        self.assertNotIn(str(private_delivery).encode("utf-8"), public_bytes)


if __name__ == "__main__":
    unittest.main()
