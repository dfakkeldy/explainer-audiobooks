from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import multiprocessing
import os
import stat
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).parents[1]
MODULE_PATH = (
    ROOT / "skills" / "fiction-audiobook" / "scripts" / "fiction_voice_preferences.py"
)
NARRATION_SCRIPT = (
    ROOT / "skills" / "echo-narration" / "scripts" / "echo_pronunciation_narrate.sh"
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
        input_receipt = self.root / f"echo-render-inputs-{run_id}.env"
        input_receipt.write_text(
            "\n".join(
                (
                    f"voice={cast['defaultVoice']}",
                    "chapter_voices="
                    + ",".join(
                        f"{row['chapter']}={row['voice']}" for row in cast["chapters"]
                    ),
                    f"voice_plan_sha256={cast['voicePlanSHA256']}",
                    f"voice_plan_id={plan_id}",
                )
            )
            + "\n",
            encoding="utf-8",
        )
        receipt.write_text(
            json.dumps(
                {
                    "schemaVersion": 3,
                    **renderer,
                    "attemptID": attempt_id,
                    "runID": run_id,
                    "attemptReceiptSHA256": "8" * 64,
                    "inputReceiptFileName": input_receipt.name,
                    "inputReceiptSHA256": sha256(input_receipt),
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

    def test_validate_cast_cli_tokens_are_consumable_by_the_narration_wrapper(self) -> None:
        cast_path = self.root / "voice-cast.json"
        cast_path.write_text(json.dumps(self.valid_cast()), encoding="utf-8")
        completed = subprocess.run(
            [
                sys.executable,
                str(MODULE_PATH),
                "validate-cast",
                "--cast",
                str(cast_path),
                "--preferences",
                str(self.preferences_path),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        tokens = json.loads(completed.stdout)
        self.assertEqual(
            [
                "--chapter-voice", "1=bf_emma",
                "--chapter-voice", "2=am_michael",
                "--chapter-voice", "3=af_bella",
                "--chapter-voice", "4=bf_emma",
            ],
            tokens,
        )

        environment = os.environ.copy()
        environment["ECHO_RUN_LANE"] = "controlled-invalid-lane"
        wrapper = subprocess.run(
            [str(NARRATION_SCRIPT), *tokens],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(64, wrapper.returncode)
        self.assertIn(
            "ECHO_RUN_LANE must be audiobook or fiction-audiobook", wrapper.stderr
        )
        self.assertNotIn("usage:", wrapper.stderr)

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

    def test_preference_lock_rejects_a_transient_parent_directory_swap(self) -> None:
        parent = self.preferences_path.parent
        parent.mkdir()
        replacement = self.root / "replacement-private"
        replacement.mkdir()
        preserved = self.root / "preserved-private"
        lock_path = parent / f".{self.preferences_path.name}.lock"
        original_open = os.open
        swapped = False

        def transient_open(
            path: os.PathLike[str] | str,
            flags: int,
            mode: int = 0o777,
            *,
            dir_fd: int | None = None,
        ) -> int:
            nonlocal swapped
            path_value = Path(path)
            if not swapped and dir_fd is None and path_value in {parent, lock_path}:
                swapped = True
                parent.rename(preserved)
                replacement.rename(parent)
                try:
                    return original_open(path, flags, mode)
                finally:
                    parent.rename(replacement)
                    preserved.rename(parent)
            if dir_fd is None:
                return original_open(path, flags, mode)
            return original_open(path, flags, mode, dir_fd=dir_fd)

        with mock.patch.object(os, "open", transient_open):
            with self.assertRaisesRegex(ValueError, "changed|stable|directory"):
                module.set_verdict(
                    self.preferences_path,
                    "Bella",
                    "liked",
                    "",
                    "2026-08-08T13:00:00+00:00",
                )
        self.assertTrue(swapped)
        self.assertFalse(self.preferences_path.exists())

    def test_preference_lock_rejects_lock_path_replacement_while_waiting(self) -> None:
        parent = self.preferences_path.parent
        parent.mkdir()
        lock_path = parent / f".{self.preferences_path.name}.lock"
        displaced = parent / "displaced.lock"
        original_flock = module.fcntl.flock
        swapped = False

        def replace_after_acquire(descriptor: int, operation: int) -> object:
            nonlocal swapped
            result = original_flock(descriptor, operation)
            if operation == module.fcntl.LOCK_EX and not swapped:
                swapped = True
                lock_path.rename(displaced)
                lock_path.write_text("replacement", encoding="utf-8")
            return result

        with mock.patch.object(module.fcntl, "flock", replace_after_acquire):
            with self.assertRaisesRegex(ValueError, "lock path changed"):
                module.set_verdict(
                    self.preferences_path,
                    "Bella",
                    "liked",
                    "",
                    "2026-08-08T13:00:00+00:00",
                )
        self.assertTrue(swapped)
        self.assertFalse(self.preferences_path.exists())

    def test_lock_replacement_after_acquire_cannot_lose_a_successful_writer(self) -> None:
        context = multiprocessing.get_context("fork")
        parent = self.preferences_path.parent
        parent.mkdir()
        lock_path = parent / f".{self.preferences_path.name}.lock"
        displaced = parent / "displaced.lock"
        first_ready = context.Event()
        release_first = context.Event()
        second_finished = context.Event()
        outcomes = context.Queue()
        real_dump = json.dump

        def first_writer() -> None:
            def pause_before_write(*args: object, **kwargs: object) -> object:
                first_ready.set()
                if not release_first.wait(timeout=5):
                    raise RuntimeError("first writer was not released")
                return real_dump(*args, **kwargs)

            module.json.dump = pause_before_write
            try:
                module.set_verdict(
                    self.preferences_path,
                    "Bella",
                    "liked",
                    "first writer",
                    "2026-08-08T13:00:00+00:00",
                )
            except BaseException as error:
                outcomes.put(("first", "error", type(error).__name__, str(error)))
            else:
                outcomes.put(("first", "ok"))
            finally:
                module.json.dump = real_dump

        def second_writer() -> None:
            try:
                module.set_verdict(
                    self.preferences_path,
                    "Nicole",
                    "disliked",
                    "second writer",
                    "2026-08-08T13:00:01+00:00",
                )
            except BaseException as error:
                outcomes.put(("second", "error", type(error).__name__, str(error)))
            else:
                outcomes.put(("second", "ok"))
            finally:
                second_finished.set()

        first = context.Process(target=first_writer)
        second = context.Process(target=second_writer)
        first.start()
        self.assertTrue(first_ready.wait(timeout=5))
        lock_path.rename(displaced)
        lock_path.write_text("replacement lock\n", encoding="utf-8")
        second.start()
        second_finished.wait(timeout=0.5)
        release_first.set()
        for worker in (first, second):
            worker.join(timeout=10)
            self.assertFalse(worker.is_alive())
            self.assertEqual(0, worker.exitcode)

        saved_outcomes = {
            outcome[0]: outcome[1:] for outcome in (outcomes.get(), outcomes.get())
        }
        self.assertEqual("error", saved_outcomes["first"][0])
        self.assertEqual("ValueError", saved_outcomes["first"][1])
        self.assertRegex(saved_outcomes["first"][2], "lock path changed")
        self.assertEqual(("ok",), saved_outcomes["second"])
        saved = module.load_preferences(self.preferences_path)
        self.assertNotIn("af_bella", saved["verdicts"])
        self.assertEqual("disliked", saved["verdicts"]["af_nicole"]["verdict"])

    def test_parent_swap_after_acquire_cannot_redirect_a_successful_write(self) -> None:
        parent = self.preferences_path.parent
        parent.mkdir()
        preserved = self.root / "preserved-private"
        replacement = self.root / "replacement-private"
        real_atomic_json = module._atomic_json
        swapped = False

        def redirecting_atomic_json(path: Path, payload: object, label: str) -> None:
            nonlocal swapped
            if label != "preferences store":
                real_atomic_json(path, payload, label)
                return
            swapped = True
            parent.rename(preserved)
            parent.mkdir()
            try:
                real_atomic_json(path, payload, label)
            finally:
                parent.rename(replacement)
                preserved.rename(parent)

        with mock.patch.object(
            module, "_atomic_json", side_effect=redirecting_atomic_json
        ):
            with self.assertRaisesRegex(ValueError, "parent directory changed"):
                module.set_verdict(
                    self.preferences_path,
                    "Bella",
                    "liked",
                    "must stay canonical",
                    "2026-08-08T13:00:00+00:00",
                )

        self.assertTrue(swapped)
        self.assertFalse(self.preferences_path.exists())
        self.assertFalse((replacement / self.preferences_path.name).exists())

    def test_target_replacement_after_atomic_commit_cannot_report_success(self) -> None:
        parent = self.preferences_path.parent
        parent.mkdir()
        attacker_path = parent / "attacker-preferences.json"
        attacker_path.write_text(
            json.dumps(module.initial_preferences(), sort_keys=True) + "\n",
            encoding="utf-8",
        )
        attacker_path.chmod(0o600)
        real_replace = os.replace
        replaced = False

        def replace_then_substitute(
            source: object, destination: object, *args: object, **kwargs: object
        ) -> None:
            nonlocal replaced
            real_replace(source, destination, *args, **kwargs)
            if destination == self.preferences_path.name:
                replaced = True
                real_replace(attacker_path, self.preferences_path)

        with mock.patch.object(
            module.os, "replace", side_effect=replace_then_substitute
        ):
            with self.assertRaisesRegex(ValueError, "preferences store.*changed"):
                module.set_verdict(
                    self.preferences_path,
                    "Bella",
                    "liked",
                    "must remain the committed bytes",
                    "2026-08-08T13:00:00+00:00",
                )

        self.assertTrue(replaced)
        saved = module.load_preferences(self.preferences_path)
        self.assertNotIn("af_bella", saved["verdicts"])

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

    def test_record_use_rejects_same_plan_id_with_a_different_full_plan_hash(self) -> None:
        cast_path = self.root / "voice-cast.json"
        cast = self.valid_cast()
        cast_path.write_text(json.dumps(cast), encoding="utf-8")
        epub, m4b, sidecar, receipt = self.write_success_fixture(cast)
        success = json.loads(receipt.read_text(encoding="utf-8"))
        input_receipt = receipt.parent / success["inputReceiptFileName"]
        forged_hash = cast["voicePlanSHA256"][:12] + "0" * 52
        if forged_hash == cast["voicePlanSHA256"]:
            forged_hash = cast["voicePlanSHA256"][:12] + "1" * 52
        input_receipt.write_text(
            input_receipt.read_text(encoding="utf-8").replace(
                f"voice_plan_sha256={cast['voicePlanSHA256']}",
                f"voice_plan_sha256={forged_hash}",
            ),
            encoding="utf-8",
        )
        success["inputReceiptSHA256"] = sha256(input_receipt)
        receipt.write_text(json.dumps(success, sort_keys=True) + "\n", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "full voice-plan hash"):
            module.record_use(
                cast_path,
                epub,
                m4b,
                sidecar,
                receipt,
                "2026-08-08T14:00:00+00:00",
                self.preferences_path,
            )

    def test_echo_input_receipt_is_a_hashed_strict_regular_sibling(self) -> None:
        cast = self.valid_cast()
        _epub, _m4b, _sidecar, receipt = self.write_success_fixture(cast)
        success = json.loads(receipt.read_text(encoding="utf-8"))
        input_receipt = receipt.parent / success["inputReceiptFileName"]

        input_receipt.write_text(
            input_receipt.read_text(encoding="utf-8")
            + f"voice_plan_id={cast['voicePlanID']}\n",
            encoding="utf-8",
        )
        success["inputReceiptSHA256"] = sha256(input_receipt)
        with self.assertRaisesRegex(ValueError, "duplicate.*voice_plan_id"):
            module.validate_echo_success_receipt(success, receipt, cast)

        input_receipt.unlink()
        outside = self.root / "outside-input.env"
        outside.write_text("voice=bf_emma\n", encoding="utf-8")
        input_receipt.symlink_to(outside)
        success["inputReceiptSHA256"] = sha256(outside)
        with self.assertRaisesRegex(ValueError, "regular non-symlink"):
            module.validate_echo_success_receipt(success, receipt, cast)

    def test_echo_input_receipt_rejects_a_transient_path_swap_during_read(self) -> None:
        cast = self.valid_cast()
        _epub, _m4b, _sidecar, receipt = self.write_success_fixture(cast)
        success = json.loads(receipt.read_text(encoding="utf-8"))
        input_receipt = receipt.parent / success["inputReceiptFileName"]
        initial_bytes = input_receipt.read_bytes() + b"marker=initial\n"
        swapped_bytes = input_receipt.read_bytes() + b"marker=swapped\n"
        input_receipt.write_bytes(initial_bytes)
        replacement = self.root / "replacement-input.env"
        replacement.write_bytes(swapped_bytes)
        success["inputReceiptSHA256"] = hashlib.sha256(swapped_bytes).hexdigest()
        original_read_bytes = Path.read_bytes

        def transient_swap(path: Path) -> bytes:
            if path != input_receipt:
                return original_read_bytes(path)
            preserved = self.root / "preserved-input.env"
            input_receipt.rename(preserved)
            replacement.rename(input_receipt)
            try:
                return original_read_bytes(input_receipt)
            finally:
                input_receipt.rename(replacement)
                preserved.rename(input_receipt)

        with mock.patch.object(Path, "read_bytes", transient_swap):
            with self.assertRaisesRegex(ValueError, "changed|differ"):
                module.validate_echo_success_receipt(success, receipt, cast)

    def test_concurrent_feedback_and_record_use_preserve_both_updates(self) -> None:
        context = multiprocessing.get_context("fork")
        cast_path = self.root / "voice-cast.json"
        cast = self.valid_cast()
        cast_path.write_text(json.dumps(cast), encoding="utf-8")
        epub, m4b, sidecar, receipt = self.write_success_fixture(cast)
        write_barrier = context.Barrier(2)
        real_atomic_json = module._atomic_json

        def coordinated_atomic_json(path: Path, payload: object, label: str) -> None:
            if label == "preferences store":
                try:
                    write_barrier.wait(timeout=0.5)
                except threading.BrokenBarrierError:
                    pass
            real_atomic_json(path, payload, label)

        def record_worker() -> None:
            module.record_use(
                cast_path,
                epub,
                m4b,
                sidecar,
                receipt,
                "2026-08-08T14:00:00+00:00",
                self.preferences_path,
            )

        def verdict_worker() -> None:
            module.set_verdict(
                self.preferences_path,
                "Bella",
                "liked",
                "clear and warm",
                "2026-08-08T14:00:01+00:00",
            )

        module._atomic_json = coordinated_atomic_json
        try:
            workers = (
                context.Process(target=record_worker),
                context.Process(target=verdict_worker),
            )
            for worker in workers:
                worker.start()
            for worker in workers:
                worker.join(timeout=10)
                self.assertFalse(worker.is_alive())
                self.assertEqual(0, worker.exitcode)
        finally:
            module._atomic_json = real_atomic_json

        saved = module.load_preferences(self.preferences_path)
        self.assertEqual("liked", saved["verdicts"]["af_bella"]["verdict"])
        self.assertEqual(1, len(saved["uses"]))
        self.assertEqual(0o600, stat.S_IMODE(self.preferences_path.stat().st_mode))

    def test_concurrent_first_feedback_writers_create_one_shared_lock(self) -> None:
        context = multiprocessing.get_context("fork")
        create_barrier = context.Barrier(2)
        results = context.Queue()
        original_open = os.open
        lock_name = f".{self.preferences_path.name}.lock"

        def feedback_worker(voice: str, verdict: str, timestamp: str) -> None:
            def coordinated_open(
                path: os.PathLike[str] | str,
                flags: int,
                mode: int = 0o777,
                *,
                dir_fd: int | None = None,
            ) -> int:
                if (
                    isinstance(path, (str, bytes, os.PathLike))
                    and Path(path).name == lock_name
                    and flags & os.O_CREAT
                ):
                    create_barrier.wait(timeout=5)
                if dir_fd is None:
                    return original_open(path, flags, mode)
                return original_open(path, flags, mode, dir_fd=dir_fd)

            module.os.open = coordinated_open
            try:
                module.set_verdict(
                    self.preferences_path,
                    voice,
                    verdict,
                    "concurrent first write",
                    timestamp,
                )
            except BaseException as error:
                results.put(("error", type(error).__name__, str(error)))
            else:
                results.put(("ok", voice, verdict))
            finally:
                module.os.open = original_open

        workers = (
            context.Process(
                target=feedback_worker,
                args=("Bella", "liked", "2026-08-08T14:00:00+00:00"),
            ),
            context.Process(
                target=feedback_worker,
                args=("Nicole", "disliked", "2026-08-08T14:00:01+00:00"),
            ),
        )
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join(timeout=10)
            self.assertFalse(worker.is_alive())
            self.assertEqual(0, worker.exitcode)

        outcomes = [results.get(timeout=1) for _ in workers]
        self.assertEqual(["ok", "ok"], sorted(outcome[0] for outcome in outcomes))
        saved = module.load_preferences(self.preferences_path)
        self.assertEqual("liked", saved["verdicts"]["af_bella"]["verdict"])
        self.assertEqual("disliked", saved["verdicts"]["af_nicole"]["verdict"])

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
