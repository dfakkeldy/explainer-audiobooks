from __future__ import annotations

import importlib.util
import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
MODULE_PATH = (
    ROOT / "skills" / "echo-narration" / "scripts" / "echo_voice_plan.py"
)
SPEC = importlib.util.spec_from_file_location("echo_voice_plan_test_module", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {MODULE_PATH}")
VOICE_PLAN = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VOICE_PLAN
SPEC.loader.exec_module(VOICE_PLAN)


class EchoVoicePlanTests(unittest.TestCase):
    def test_canonicalizes_assignments_by_display_chapter(self) -> None:
        plan = VOICE_PLAN.voice_plan(
            "am_michael",
            ["28=bm_daniel", "1=af_heart", "12=am_fenrir"],
        )
        self.assertEqual(
            ("1=af_heart", "12=am_fenrir", "28=bm_daniel"),
            plan["canonicalAssignments"],
        )
        self.assertRegex(plan["voicePlanID"], r"^plan-[0-9a-f]{12}$")
        self.assertRegex(plan["voicePlanSHA256"], r"^[0-9a-f]{64}$")

    def test_plan_hash_binds_default_voice_and_every_mapping(self) -> None:
        original = VOICE_PLAN.voice_plan("am_michael", ["1=af_heart"])
        changed_mapping = VOICE_PLAN.voice_plan("am_michael", ["1=af_bella"])
        changed_default = VOICE_PLAN.voice_plan("am_puck", ["1=af_heart"])
        self.assertNotEqual(
            original["voicePlanSHA256"], changed_mapping["voicePlanSHA256"]
        )
        self.assertNotEqual(
            original["voicePlanSHA256"], changed_default["voicePlanSHA256"]
        )

    def test_accepts_the_complete_english_voice_catalog(self) -> None:
        assignments = [
            f"{index}={voice}"
            for index, voice in enumerate(sorted(VOICE_PLAN.VOICE_IDS), start=1)
        ]
        plan = VOICE_PLAN.voice_plan("am_michael", assignments)
        self.assertEqual(28, len(plan["chapterVoices"]))

    def test_rejects_duplicates_malformed_chapters_and_unknown_voices(self) -> None:
        cases = (
            ["1=af_heart", "1=af_bella"],
            ["0=af_heart"],
            ["01=af_heart"],
            ["1=not_a_voice"],
        )
        for assignments in cases:
            with self.subTest(assignments=assignments):
                with self.assertRaises(VOICE_PLAN.VoicePlanError):
                    VOICE_PLAN.voice_plan("am_michael", assignments)

    def test_legacy_uniform_env0_bytes_are_unchanged(self) -> None:
        result = subprocess.run(
            [sys.executable, str(MODULE_PATH), "--default-voice", "am_michael", "--format", "env0"],
            check=False,
            capture_output=True,
        )
        self.assertEqual(0, result.returncode, result.stderr.decode())
        self.assertEqual(
            b"VOICE\0am_michael\0CHAPTER_VOICES_CANONICAL\0\0"
            b"VOICE_PLAN_SHA256\0f54fe6d603ea42f277ce3cf4dc0f0da6056341034acf4ec6d5b7db099a5d7cae\0"
            b"VOICE_PLAN_ID\0am_michael\0",
            result.stdout,
        )

    def test_resolves_an_echo_authoritative_block_plan(self) -> None:
        """The adapter passes only sealed absolute inputs to Echo and preserves its receipt."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            epub = root / "book.epub"
            plan = root / "voice-plan.json"
            echo = root / "echo-cli"
            epub.write_bytes(b"fixture EPUB")
            plan.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "source": {"epubSHA256": hashlib.sha256(epub.read_bytes()).hexdigest()},
                        "defaultSpeakerID": "narrator",
                        "speakers": [{"id": "narrator", "voiceID": "am_michael"}],
                        "assignments": [],
                    }
                ),
                encoding="utf-8",
            )
            receipt = {
                "blockCount": 2,
                "defaultVoice": "am_michael",
                "sourceEPUBSHA256": hashlib.sha256(epub.read_bytes()).hexdigest(),
                "voicePlanID": "plan-" + "b" * 12,
                "voicePlanSHA256": "b" * 64,
            }
            echo.write_text(
                "#!/usr/bin/env python3\n"
                "import json, sys\n"
                f"assert sys.argv[1:] == ['resolve-voice-plan', '--epub', {str(epub)!r}, '--voice-plan', {str(plan)!r}]\n"
                f"print(json.dumps({receipt!r}, sort_keys=True, separators=(',', ':')))\n",
                encoding="utf-8",
            )
            echo.chmod(echo.stat().st_mode | stat.S_IXUSR)

            resolved = VOICE_PLAN.resolve_block_plan(echo, epub, plan)

            self.assertEqual(receipt, resolved)

    def test_block_env0_has_the_exact_ordered_receipt_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            epub = root / "book.epub"
            plan = root / "voice-plan.json"
            canonical = root / "canonical.json"
            resolution = root / "resolution.json"
            echo = root / "echo-cli"
            epub.write_bytes(b"fixture EPUB")
            source_sha = hashlib.sha256(epub.read_bytes()).hexdigest()
            plan.write_text(
                json.dumps({"schemaVersion": 1, "source": {"epubSHA256": source_sha}}),
                encoding="utf-8",
            )

            echo.write_text(
                "#!/usr/bin/env python3\nimport json\nprint(json.dumps({\n"
                f"'blockCount': 2, 'defaultVoice': 'am_michael', 'sourceEPUBSHA256': '{source_sha}', "
                "'voicePlanID': 'plan-" + "b" * 12 + "', 'voicePlanSHA256': '" + "b" * 64 + "'}, "
                "sort_keys=True, separators=(',', ':')))\n",
                encoding="utf-8",
            )
            echo.chmod(echo.stat().st_mode | stat.S_IXUSR)
            result = __import__("subprocess").run(
                [
                    sys.executable, str(MODULE_PATH), "--echo-cli", str(echo),
                    "--epub", str(epub), "--voice-plan", str(plan),
                    "--canonical-plan", str(canonical), "--resolution", str(resolution),
                    "--format", "env0",
                ], capture_output=True, check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr.decode())
            canonical_sha = hashlib.sha256(canonical.read_bytes()).hexdigest()
            resolution_sha = hashlib.sha256(resolution.read_bytes()).hexdigest()
            self.assertEqual(
                (
                    "VOICE", "am_michael", "CHAPTER_VOICES_CANONICAL", "",
                    "VOICE_PLAN_MODE", "block", "VOICE_PLAN_SHA256", "b" * 64,
                    "VOICE_PLAN_ID", "plan-" + "b" * 12, "VOICE_PLAN_BLOCK_COUNT", "2",
                    "VOICE_PLAN_CANONICAL_PATH", str(canonical),
                    "VOICE_PLAN_CANONICAL_SHA256", canonical_sha,
                    "VOICE_PLAN_RESOLUTION_PATH", str(resolution),
                    "VOICE_PLAN_RESOLUTION_SHA256", resolution_sha,
                ),
                tuple(result.stdout.decode().split("\0")[:-1]),
            )

    def test_rejects_unbound_or_noncanonical_echo_receipts(self) -> None:
        """A formatting or identity drift must not create a run-scoped receipt."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            epub = root / "book.epub"
            plan = root / "voice-plan.json"
            echo = root / "echo-cli"
            epub.write_bytes(b"fixture EPUB")
            plan.write_text("{}", encoding="utf-8")
            source_sha = hashlib.sha256(epub.read_bytes()).hexdigest()
            valid = (
                '{"blockCount":2,"defaultVoice":"am_michael","sourceEPUBSHA256":"'
                + source_sha + '","voicePlanID":"plan-' + "b" * 12
                + '","voicePlanSHA256":"' + "b" * 64 + '"}'
            )
            for receipt in (
                valid.replace("plan-" + "b" * 12, "plan-" + "a" * 12),
                valid.replace('"blockCount":2,', '"blockCount":2, '),
                valid.replace('"am_michael"', '["am_michael"]'),
            ):
                with self.subTest(receipt=receipt[:32]):
                    echo.write_text(
                        "#!/usr/bin/env python3\nimport sys\n"
                        f"sys.stdout.buffer.write({receipt.encode()!r})\n",
                        encoding="utf-8",
                    )
                    echo.chmod(echo.stat().st_mode | stat.S_IXUSR)
                    with self.assertRaises(VOICE_PLAN.VoicePlanError):
                        VOICE_PLAN.resolve_block_plan(echo, epub, plan)

    def test_rejects_every_invalid_resolver_boundary(self) -> None:
        """No malformed Echo receipt or unsafe adapter input reaches sealing."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            epub = root / "book.epub"
            plan = root / "voice-plan.json"
            echo = root / "echo-cli"
            epub.write_bytes(b"fixture EPUB")
            plan.write_text("{}", encoding="utf-8")
            source_sha = hashlib.sha256(epub.read_bytes()).hexdigest()
            receipt = {
                "blockCount": 2, "defaultVoice": "am_michael",
                "sourceEPUBSHA256": source_sha, "voicePlanID": "plan-" + "b" * 12,
                "voicePlanSHA256": "b" * 64,
            }
            cases = []
            for key, value in (
                ("sourceEPUBSHA256", "a" * 64), ("defaultVoice", "not_a_voice"),
                ("blockCount", 0), ("blockCount", -1),
            ):
                payload = dict(receipt)
                payload[key] = value
                cases.append(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode())
            cases.extend((
                json.dumps({key: value for key, value in receipt.items() if key != "blockCount"}, sort_keys=True, separators=(",", ":")).encode(),
                json.dumps({**receipt, "extra": True}, sort_keys=True, separators=(",", ":")).encode(),
                b'{"blockCount":2,"blockCount":2,"defaultVoice":"am_michael","sourceEPUBSHA256":"' + source_sha.encode() + b'","voicePlanID":"plan-' + b"b" * 12 + b'","voicePlanSHA256":"' + b"b" * 64 + b'"}',
                b"x" * (64 * 1024 + 1),
            ))
            for raw in cases:
                with self.subTest(raw=raw[:16]):
                    echo.write_text("#!/usr/bin/env python3\nimport sys\n" f"sys.stdout.buffer.write({raw!r})\n")
                    echo.chmod(echo.stat().st_mode | stat.S_IXUSR)
                    with self.assertRaises(VOICE_PLAN.VoicePlanError):
                        VOICE_PLAN.resolve_block_plan(echo, epub, plan)
            echo.write_text("#!/usr/bin/env python3\nimport sys\nsys.stderr.write('noisy')\n" f"sys.stdout.buffer.write({json.dumps(receipt, sort_keys=True, separators=(',', ':')).encode()!r})\n")
            echo.chmod(echo.stat().st_mode | stat.S_IXUSR)
            with self.assertRaises(VOICE_PLAN.VoicePlanError):
                VOICE_PLAN.resolve_block_plan(echo, epub, plan)
            echo.write_text("#!/usr/bin/env python3\nraise SystemExit(7)\n")
            echo.chmod(echo.stat().st_mode | stat.S_IXUSR)
            with self.assertRaises(VOICE_PLAN.VoicePlanError):
                VOICE_PLAN.resolve_block_plan(echo, epub, plan)

    def test_rejects_unsafe_inputs_and_duplicate_authored_json_before_sealing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            epub = root / "book.epub"
            plan = root / "voice-plan.json"
            echo = root / "echo-cli"
            canonical = root / "canonical.json"
            resolution = root / "resolution.json"
            epub.write_bytes(b"fixture EPUB")
            plan.write_text('{"schemaVersion":1,"schemaVersion":1}', encoding="utf-8")
            echo.write_text("#!/usr/bin/env python3\nraise SystemExit(0)\n")
            echo.chmod(echo.stat().st_mode | stat.S_IXUSR)
            with self.assertRaises(VOICE_PLAN.VoicePlanError):
                VOICE_PLAN.seal_block_plan(echo, epub, plan, canonical, resolution)
            self.assertFalse(canonical.exists())
            self.assertFalse(resolution.exists())
            directory_path = root / "directory"
            directory_path.mkdir()
            link = root / "echo-link"
            link.symlink_to(echo)
            for candidate in (Path("relative"), root / "missing", directory_path, link):
                with self.subTest(candidate=candidate):
                    with self.assertRaises(VOICE_PLAN.VoicePlanError):
                        VOICE_PLAN.resolve_block_plan(candidate, epub, plan)


if __name__ == "__main__":
    unittest.main()
