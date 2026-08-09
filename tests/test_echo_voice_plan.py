from __future__ import annotations

import importlib.util
import hashlib
import json
import os
import stat
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
                "'voicePlanID': 'plan-" + "b" * 12 + "', 'voicePlanSHA256': '" + "b" * 64 + "'\n}))\n",
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


if __name__ == "__main__":
    unittest.main()
