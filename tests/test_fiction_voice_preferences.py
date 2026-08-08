from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
MODULE_PATH = (
    ROOT / "skills" / "fiction-audiobook" / "scripts" / "fiction_voice_preferences.py"
)
SPEC = importlib.util.spec_from_file_location("fiction_voice_preferences_test_module", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {MODULE_PATH}")
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FictionVoicePreferencesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        self.preferences_path = self.root / "private" / "preferences.json"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def valid_cast(self) -> dict[str, object]:
        chapters = [
            {"chapter": 1, "role": "Mara", "voice": "bf_emma", "experimental": False},
            {"chapter": 2, "role": "Ivo", "voice": "am_michael", "experimental": False},
            {"chapter": 3, "role": "Sera", "voice": "af_bella", "experimental": False},
            {"chapter": 4, "role": "Mara", "voice": "bf_emma", "experimental": False},
        ]
        plan = module.voice_plan(
            "bf_emma", [f"{row['chapter']}={row['voice']}" for row in chapters]
        )
        return {
            "schemaVersion": 1,
            "slug": "storm-lighthouse",
            "chapterCount": 4,
            "defaultVoice": "bf_emma",
            "chapters": chapters,
            "voicePlanSHA256": plan["voicePlanSHA256"],
            "voicePlanID": plan["voicePlanID"],
            "verifiedArtifacts": None,
        }

    def write_success_fixture(
        self,
        cast: dict[str, object],
        *,
        receipt_plan_id: str | None = None,
    ) -> tuple[Path, Path, Path, Path]:
        epub = self.root / "storm-lighthouse.epub"
        m4b = self.root / "storm-lighthouse.m4b"
        sidecar = self.root / "storm-lighthouse.alignment.json"
        epub.write_bytes(b"epub source")
        m4b.write_bytes(b"audiobook")
        sidecar.write_text('{"anchors": []}\n', encoding="utf-8")
        renderer_root = self.root / "installed-renderer"
        renderer_build_root = renderer_root / "renderer"
        renderer_build_root.mkdir(parents=True, exist_ok=True)
        renderer = {
            "rendererSchemaVersion": 1,
            "rendererRoot": str(renderer_root),
            "rendererBuildRoot": str(renderer_build_root),
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
        plan_id = receipt_plan_id or cast["voicePlanID"]
        run_id = (
            f"{sha256(epub)[:12]}-{renderer['echoCLI_SHA256'][:12]}-"
            f"{renderer['echoResourcesSHA256'][:12]}-"
            f"{renderer['rendererManifestSHA256'][:12]}-"
            f"{renderer['echoSourceSHA']}-{plan_id}"
        )
        attempt_id = "7" * 64
        receipt = self.root / f"echo-render-success-{run_id}-{attempt_id}.json"
        receipt.write_text(
            json.dumps(
                {
                    "schemaVersion": 3,
                    **renderer,
                    "attemptID": attempt_id,
                    "runID": run_id,
                    "attemptReceiptSHA256": "8" * 64,
                    "inputReceiptFileName": f"echo-render-inputs-{run_id}.env",
                    "inputReceiptSHA256": "9" * 64,
                    "sourceEPUBFileName": epub.name,
                    "sourceEPUBSHA256": sha256(epub),
                    "artifactRelativePath": f"echo-renders/{run_id}/{attempt_id}",
                    "resumeStateFileName": f"echo-resume-state-{run_id}.json",
                    "resumeStateSHA256": "a" * 64,
                    "audiobookFileName": m4b.name,
                    "audiobookSHA256": sha256(m4b),
                    "sidecarFileName": sidecar.name,
                    "sidecarSHA256": sha256(sidecar),
                    "auditFileName": "storm-lighthouse.pronunciation-audit.json",
                    "auditSHA256": "b" * 64,
                },
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        return epub, m4b, sidecar, receipt

    def test_missing_store_supplies_the_standing_heart_blacklist(self) -> None:
        preferences = module.load_preferences(self.preferences_path)
        self.assertIn("af_heart", preferences["blacklist"])
        self.assertFalse(self.preferences_path.exists())

    def test_cast_requires_three_to_five_known_nonblacklisted_voices(self) -> None:
        cast = self.valid_cast()
        module.validate_cast(cast, module.load_preferences(self.preferences_path))
        for voice, message in (
            ("af_heart", "blacklisted"),
            ("not_a_voice", "unknown Echo voice"),
        ):
            changed = copy.deepcopy(cast)
            changed["chapters"][2]["voice"] = voice
            with self.assertRaisesRegex(ValueError, message):
                module.validate_cast(changed, module.load_preferences(self.preferences_path))

        too_few = copy.deepcopy(cast)
        too_few["chapters"][2]["voice"] = "bf_emma"
        with self.assertRaisesRegex(ValueError, "three to five"):
            module.validate_cast(too_few, module.load_preferences(self.preferences_path))

        too_many = copy.deepcopy(cast)
        too_many["chapters"].append(
            {"chapter": 5, "role": "Nia", "voice": "bm_george", "experimental": False}
        )
        too_many["chapters"].append(
            {"chapter": 6, "role": "Orr", "voice": "bf_isabella", "experimental": False}
        )
        too_many["chapters"].append(
            {"chapter": 7, "role": "Pax", "voice": "bm_lewis", "experimental": False}
        )
        too_many["chapterCount"] = 7
        too_many_plan = module.voice_plan(
            too_many["defaultVoice"],
            [f"{row['chapter']}={row['voice']}" for row in too_many["chapters"]],
        )
        too_many["voicePlanSHA256"] = too_many_plan["voicePlanSHA256"]
        too_many["voicePlanID"] = too_many_plan["voicePlanID"]
        with self.assertRaisesRegex(ValueError, "three to five"):
            module.validate_cast(too_many, module.load_preferences(self.preferences_path))

    def test_recurring_role_keeps_one_voice_and_every_chapter_is_present(self) -> None:
        inconsistent = self.valid_cast()
        inconsistent["chapters"][3]["voice"] = "bm_george"
        with self.assertRaisesRegex(ValueError, "recurring role"):
            module.validate_cast(inconsistent, module.load_preferences(self.preferences_path))
        missing = self.valid_cast()
        missing["chapters"].pop(1)
        with self.assertRaisesRegex(ValueError, "every chapter"):
            module.validate_cast(missing, module.load_preferences(self.preferences_path))

    def test_experimental_rows_are_limited_and_use_previously_untried_voices(self) -> None:
        cast = self.valid_cast()
        module.validate_cast(cast, module.load_preferences(self.preferences_path))

        first_experiment = copy.deepcopy(cast)
        first_experiment["chapters"][2]["experimental"] = True
        module.validate_cast(first_experiment, module.load_preferences(self.preferences_path))

        two_experiments = copy.deepcopy(cast)
        two_experiments["chapters"][1]["experimental"] = True
        two_experiments["chapters"][2]["experimental"] = True
        module.validate_cast(two_experiments, module.load_preferences(self.preferences_path))

        three_experiments = copy.deepcopy(cast)
        for row in three_experiments["chapters"][:3]:
            row["experimental"] = True
        with self.assertRaisesRegex(ValueError, "at most two experimental"):
            module.validate_cast(three_experiments, module.load_preferences(self.preferences_path))

        tried = module.initial_preferences()
        tried["uses"].append(
            {
                "slug": "earlier-book",
                "recordedAt": "2026-08-08T12:00:00+00:00",
                "sourceEPUBSHA256": "a" * 64,
                "audiobookSHA256": "b" * 64,
                "sidecarSHA256": "c" * 64,
                "voicePlanSHA256": "d" * 64,
                "successReceiptSHA256": "e" * 64,
                "chapters": [{"chapter": 1, "voice": "af_bella"}],
            }
        )
        with self.assertRaisesRegex(ValueError, "experimental voice was already used"):
            module.validate_cast(first_experiment, tried)

    def test_feedback_resolves_bella_and_blacklists_future_casts(self) -> None:
        module.set_verdict(
            self.preferences_path, "Bella", "blacklisted", "too breathy",
            "2026-08-08T13:00:00+00:00",
        )
        saved = module.load_preferences(self.preferences_path)
        self.assertIn("af_bella", saved["blacklist"])
        self.assertEqual("blacklisted", saved["verdicts"]["af_bella"]["verdict"])
        self.assertEqual(0o600, stat.S_IMODE(self.preferences_path.stat().st_mode))
        with self.assertRaisesRegex(ValueError, "blacklisted"):
            module.validate_cast(self.valid_cast(), saved)

        module.set_verdict(
            self.preferences_path, "Bella", "disliked", "not a reversal",
            "2026-08-08T13:00:30+00:00",
        )
        self.assertIn("af_bella", module.load_preferences(self.preferences_path)["blacklist"])

        module.set_verdict(
            self.preferences_path, "af_bella", "clear", "", "2026-08-08T13:01:00+00:00"
        )
        cleared = module.load_preferences(self.preferences_path)
        self.assertNotIn("af_bella", cleared["blacklist"])
        self.assertNotIn("af_bella", cleared["verdicts"])
        module.set_verdict(
            self.preferences_path, "af_heart", "clear", "", "2026-08-08T13:02:00+00:00"
        )
        self.assertIn("af_heart", module.load_preferences(self.preferences_path)["blacklist"])
        module.set_verdict(
            self.preferences_path, "af_heart", "liked", "otherwise pleasant",
            "2026-08-08T13:03:00+00:00",
        )
        self.assertIn("af_heart", module.load_preferences(self.preferences_path)["blacklist"])
        module.set_verdict(
            self.preferences_path, "af_heart", "blacklisted", "",
            "2026-08-08T13:04:00+00:00",
        )
        heart = module.load_preferences(self.preferences_path)["blacklist"]["af_heart"]
        self.assertEqual("standing audiobook preference", heart["reason"])

    def test_preference_store_rejects_symlinks_and_invalid_persisted_shapes(self) -> None:
        target = self.root / "target.json"
        target.write_text(json.dumps(module.initial_preferences()), encoding="utf-8")
        self.preferences_path.parent.mkdir()
        self.preferences_path.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "symlink"):
            module.load_preferences(self.preferences_path)
        self.preferences_path.unlink()

        invalid = module.initial_preferences()
        del invalid["blacklist"]["af_heart"]
        self.preferences_path.write_text(json.dumps(invalid), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "af_heart"):
            module.load_preferences(self.preferences_path)

        invalid = module.initial_preferences()
        invalid["uses"].append(
            {
                "slug": "unchecked-history",
                "recordedAt": "2026-08-08T12:00:00+00:00",
                "sourceEPUBSHA256": "a" * 64,
                "audiobookSHA256": "b" * 64,
                "sidecarSHA256": "c" * 64,
                "voicePlanSHA256": "d" * 64,
                "chapters": [{"chapter": 1, "voice": "af_bella"}],
            }
        )
        self.preferences_path.write_text(json.dumps(invalid), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "successReceiptSHA256"):
            module.load_preferences(self.preferences_path)

    def test_preference_store_refuses_a_symlink_ancestor_before_an_atomic_write(self) -> None:
        destination = self.root / "real-private-store"
        destination.mkdir()
        ancestor = self.root / "linked-private-store"
        ancestor.symlink_to(destination, target_is_directory=True)
        through_ancestor = ancestor / "nested" / "preferences.json"

        with self.assertRaisesRegex(ValueError, "symlink"):
            module.set_verdict(
                through_ancestor, "Bella", "liked", "", "2026-08-08T13:00:00+00:00"
            )
        self.assertFalse((destination / "nested" / "preferences.json").exists())

    def test_schema_versions_must_be_the_integer_one_not_boolean_or_float(self) -> None:
        for version in (True, 1.0):
            with self.subTest(store_version=version):
                invalid_preferences = module.initial_preferences()
                invalid_preferences["schemaVersion"] = version
                self.preferences_path.parent.mkdir(exist_ok=True)
                self.preferences_path.write_text(
                    json.dumps(invalid_preferences), encoding="utf-8"
                )
                with self.assertRaisesRegex(ValueError, "schemaVersion"):
                    module.load_preferences(self.preferences_path)

            with self.subTest(cast_version=version):
                invalid_cast = self.valid_cast()
                invalid_cast["schemaVersion"] = version
                with self.assertRaisesRegex(ValueError, "schemaVersion"):
                    module.validate_cast(
                        invalid_cast, module.load_preferences(self.root / "other.json")
                    )

    def test_record_use_requires_exact_artifacts_and_is_idempotent_after_cast_verification(self) -> None:
        cast_path = self.root / "voice-cast.json"
        cast = self.valid_cast()
        cast_path.write_text(json.dumps(cast), encoding="utf-8")
        epub, m4b, sidecar, receipt = self.write_success_fixture(cast)

        saved = module.record_use(
            cast_path, epub, m4b, sidecar, receipt,
            "2026-08-08T14:00:00+00:00", self.preferences_path,
        )
        sealed = json.loads(cast_path.read_text(encoding="utf-8"))
        self.assertEqual(
            {
                "sourceEPUBSHA256": sha256(epub),
                "audiobookSHA256": sha256(m4b),
                "sidecarSHA256": sha256(sidecar),
                "voicePlanSHA256": cast["voicePlanSHA256"],
            },
            sealed["verifiedArtifacts"],
        )
        self.assertEqual(1, len(saved["uses"]))
        retried = module.record_use(
            cast_path, epub, m4b, sidecar, receipt,
            "2026-08-08T14:01:00+00:00", self.preferences_path,
        )
        self.assertEqual(1, len(retried["uses"]))

        for path, changed in ((epub, b"changed epub"), (m4b, b"changed m4b"), (sidecar, b"changed sidecar")):
            path.write_bytes(changed)
            with self.assertRaisesRegex(ValueError, "differs from success receipt"):
                module.record_use(
                    cast_path, epub, m4b, sidecar, receipt,
                    "2026-08-08T14:02:00+00:00", self.preferences_path,
                )
            path.write_bytes({epub: b"epub source", m4b: b"audiobook", sidecar: b'{"anchors": []}\n'}[path])

    def test_record_use_accepts_real_echo_receipt_without_voice_plan_hash(self) -> None:
        cast_path = self.root / "voice-cast.json"
        cast = self.valid_cast()
        cast_path.write_text(json.dumps(cast), encoding="utf-8")
        epub, m4b, sidecar, receipt = self.write_success_fixture(cast)
        success = json.loads(receipt.read_text(encoding="utf-8"))
        self.assertNotIn("voicePlanSHA256", success)
        receipt.write_text(json.dumps(success), encoding="utf-8")

        saved = module.record_use(
            cast_path,
            epub,
            m4b,
            sidecar,
            receipt,
            "2026-08-08T14:00:00+00:00",
            self.preferences_path,
        )

        self.assertEqual(1, len(saved["uses"]))
        self.assertEqual(
            cast["voicePlanSHA256"],
            json.loads(cast_path.read_text(encoding="utf-8"))["verifiedArtifacts"][
                "voicePlanSHA256"
            ],
        )

    def test_record_use_rejects_real_echo_run_derived_for_another_plan(self) -> None:
        cast_path = self.root / "voice-cast.json"
        cast = self.valid_cast()
        cast_path.write_text(json.dumps(cast), encoding="utf-8")
        epub, m4b, sidecar, receipt = self.write_success_fixture(
            cast, receipt_plan_id="plan-000000000000"
        )

        with self.assertRaisesRegex(ValueError, "runID|voice-plan|voice plan"):
            module.record_use(
                cast_path,
                epub,
                m4b,
                sidecar,
                receipt,
                "2026-08-08T14:00:00+00:00",
                self.preferences_path,
            )

    def test_record_use_rejects_changed_plan_and_can_resume_after_verified_cast_write(self) -> None:
        cast_path = self.root / "voice-cast.json"
        cast = self.valid_cast()
        epub, m4b, sidecar, receipt = self.write_success_fixture(cast)
        invalid_cast = copy.deepcopy(cast)
        invalid_cast["voicePlanSHA256"] = "f" * 64
        cast_path.write_text(json.dumps(invalid_cast), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "voice-plan hash"):
            module.record_use(
                cast_path, epub, m4b, sidecar, receipt,
                "2026-08-08T14:00:00+00:00", self.preferences_path,
            )

        sealed = copy.deepcopy(cast)
        sealed["verifiedArtifacts"] = {
            "sourceEPUBSHA256": sha256(epub),
            "audiobookSHA256": sha256(m4b),
            "sidecarSHA256": sha256(sidecar),
            "voicePlanSHA256": cast["voicePlanSHA256"],
        }
        cast_path.write_text(json.dumps(sealed), encoding="utf-8")
        resumed = module.record_use(
            cast_path, epub, m4b, sidecar, receipt,
            "2026-08-08T14:03:00+00:00", self.preferences_path,
        )
        self.assertEqual(1, len(resumed["uses"]))

    def test_record_use_rejects_a_cast_without_the_explicit_null_to_verified_field(self) -> None:
        cast_path = self.root / "voice-cast.json"
        cast = self.valid_cast()
        del cast["verifiedArtifacts"]
        cast_path.write_text(json.dumps(cast), encoding="utf-8")
        epub, m4b, sidecar, receipt = self.write_success_fixture(cast)
        with self.assertRaisesRegex(ValueError, "verifiedArtifacts"):
            module.record_use(
                cast_path, epub, m4b, sidecar, receipt,
                "2026-08-08T14:00:00+00:00", self.preferences_path,
            )

    def test_completed_cast_enforces_only_the_immutable_canonical_contract(self) -> None:
        completed = self.valid_cast()
        completed["verifiedArtifacts"] = {
            "sourceEPUBSHA256": "a" * 64,
            "audiobookSHA256": "b" * 64,
            "sidecarSHA256": "c" * 64,
            "voicePlanSHA256": completed["voicePlanSHA256"],
        }
        plan = module.validate_completed_cast(completed)
        self.assertEqual(completed["voicePlanSHA256"], plan["voicePlanSHA256"])

        cases = []
        missing = copy.deepcopy(completed)
        missing["chapters"].pop()
        cases.append(("coverage", missing, "every chapter"))
        unknown = copy.deepcopy(completed)
        unknown["chapters"][2]["voice"] = "not_a_voice"
        cases.append(("unknown voice", unknown, "unknown Echo voice"))
        too_few = copy.deepcopy(completed)
        too_few["chapters"][2]["voice"] = "bf_emma"
        cases.append(("ensemble", too_few, "three to five"))
        inconsistent = copy.deepcopy(completed)
        inconsistent["chapters"][3]["voice"] = "am_michael"
        cases.append(("recurring role", inconsistent, "recurring role"))
        wrong_hash = copy.deepcopy(completed)
        wrong_hash["voicePlanSHA256"] = "f" * 64
        cases.append(("plan hash", wrong_hash, "voice-plan hash"))
        wrong_id = copy.deepcopy(completed)
        wrong_id["voicePlanID"] = "plan-000000000000"
        cases.append(("plan identity", wrong_id, "voice-plan identity"))
        unfinished = copy.deepcopy(completed)
        unfinished["verifiedArtifacts"] = None
        cases.append(("unfinished", unfinished, "verifiedArtifacts"))
        for name, cast, pattern in cases:
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, pattern):
                module.validate_completed_cast(cast)


if __name__ == "__main__":
    unittest.main()
