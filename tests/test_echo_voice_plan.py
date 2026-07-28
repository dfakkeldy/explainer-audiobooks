from __future__ import annotations

import importlib.util
import sys
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


if __name__ == "__main__":
    unittest.main()
