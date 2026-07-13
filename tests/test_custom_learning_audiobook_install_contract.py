from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
VALIDATOR = ROOT / "tools" / "validate_custom_learning_skill_install.py"
LIVE_HERMES_IMPORT = (
    Path.home() / ".hermes" / "skills" / "openclaw-imports" / "custom-learning-audiobook"
)
DISABLED_MARKER = "DISABLED: canonical skill required"
CANONICAL_ROUTE = "/Users/dfakkeldy/.hermes/skills/custom-learning-audiobook"


class InstalledCustomLearningSkillContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.tmp = Path(self.temporary.name)
        self.candidate = self.tmp / "candidate"
        self.canonical = self.tmp / "canonical"
        self.external = self.tmp / "external"
        self.links = [self.tmp / f"agent-{index}" for index in range(4)]
        for root in (self.candidate, self.canonical, self.external):
            (root / "references").mkdir(parents=True)
            (root / "scripts").mkdir()
        for link in self.links:
            link.symlink_to(self.canonical, target_is_directory=True)
        self.write_skill(self.candidate, "candidate")
        self.write_skill(self.canonical, "old canonical")
        self.write_disabled_external()

    @staticmethod
    def write_skill(root: Path, value: str) -> None:
        (root / "SKILL.md").write_text(value, encoding="utf-8")
        (root / "references" / "package-and-qc.md").write_text(
            value,
            encoding="utf-8",
        )
        (root / "scripts" / "echo_pronunciation_preflight.sh").write_text(
            value,
            encoding="utf-8",
        )
        (root / "scripts" / "validate_pronunciation_audit.py").write_text(
            value,
            encoding="utf-8",
        )

    def write_disabled_external(self) -> None:
        content = f"{DISABLED_MARKER}\nUse {CANONICAL_ROUTE}.\n"
        (self.external / "SKILL.md").write_text(content, encoding="utf-8")
        (self.external / "references" / "package-and-qc.md").write_text(
            content,
            encoding="utf-8",
        )

    def run_validator(self) -> subprocess.CompletedProcess[str]:
        command = [
            "/usr/local/bin/python3",
            str(VALIDATOR),
            "--candidate-root",
            str(self.candidate),
            "--canonical-root",
            str(self.canonical),
            "--external-root",
            str(self.external),
        ]
        for link in self.links:
            command.extend(("--link", str(link)))
        return subprocess.run(command, capture_output=True, text=True)

    def test_reports_pending_when_installed_canonical_content_is_old(self) -> None:
        result = self.run_validator()
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn("installed_skill_parity: pending-integration", result.stdout)

    def test_reports_current_after_candidate_is_integrated(self) -> None:
        for relative_path in (
            "SKILL.md",
            "references/package-and-qc.md",
            "scripts/echo_pronunciation_preflight.sh",
            "scripts/validate_pronunciation_audit.py",
        ):
            shutil.copy2(
                self.candidate / relative_path,
                self.canonical / relative_path,
            )
        result = self.run_validator()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("installed_skill_parity: current", result.stdout)

    def test_reports_pending_when_canonical_lacks_a_new_helper(self) -> None:
        for relative_path in (
            "SKILL.md",
            "references/package-and-qc.md",
            "scripts/echo_pronunciation_preflight.sh",
            "scripts/validate_pronunciation_audit.py",
        ):
            shutil.copy2(
                self.candidate / relative_path,
                self.canonical / relative_path,
            )
        (self.canonical / "scripts" / "echo_pronunciation_preflight.sh").unlink()
        result = self.run_validator()
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn("installed_skill_parity: pending-integration", result.stdout)

    @unittest.skipUnless(LIVE_HERMES_IMPORT.exists(), "live Hermes import is absent")
    def test_live_independent_hermes_import_is_disabled_and_canonical_routed(self) -> None:
        for path in (
            LIVE_HERMES_IMPORT / "SKILL.md",
            LIVE_HERMES_IMPORT / "references" / "package-and-qc.md",
        ):
            text = path.read_text(encoding="utf-8")
            self.assertIn(DISABLED_MARKER, text)
            self.assertIn(CANONICAL_ROUTE, text)


if __name__ == "__main__":
    unittest.main()
