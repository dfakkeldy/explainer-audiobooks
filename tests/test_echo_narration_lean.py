from __future__ import annotations

import unittest
from pathlib import Path

REPO = Path(__file__).parents[1]
WRAPPER = REPO / "skills" / "custom-learning-audiobook" / "scripts" / "echo_pronunciation_narrate.sh"


class EchoNarrationLeanTests(unittest.TestCase):
    def setUp(self) -> None:
        if not WRAPPER.is_file():
            self.skipTest(f"wrapper not at {WRAPPER}; Task 3 moves it")
        self.text = WRAPPER.read_text(encoding="utf-8")

    def test_wrapper_does_not_require_a_pronunciation_plan(self) -> None:
        self.assertNotIn("PRONUNCIATION_PLAN is required", self.text)
        self.assertNotIn("PRONUNCIATION_PLAN must be the canonical run plan", self.text)

    def test_wrapper_does_not_invoke_the_deleted_qc_script(self) -> None:
        self.assertNotIn("pronunciation_plan_qc.py", self.text)

    def test_pronunciation_plan_variable_is_gone(self) -> None:
        self.assertNotIn("PRONUNCIATION_PLAN", self.text)

    def test_retired_scripts_are_gone(self) -> None:
        for retired in (
            REPO / "skill" / "scripts" / "pronunciation_plan_qc.py",
            REPO / "skill" / "scripts" / "build_pronunciation_probe_reel.py",
            REPO / "skills" / "custom-learning-audiobook" / "scripts" / "echo_learning_pilot_narrate.sh",
        ):
            self.assertFalse(retired.exists(), f"{retired} should be deleted")


if __name__ == "__main__":
    unittest.main()
