from __future__ import annotations

import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
VALIDATOR = ROOT / "tools" / "validate_custom_learning_skill_install.py"
LIVE_HERMES_IMPORT = (
    Path.home()
    / ".hermes"
    / "skills"
    / "openclaw-imports"
    / "custom-learning-audiobook"
)
DISABLED_MARKER = "DISABLED: canonical skill required"
CANONICAL_ROUTE = "/Users/dfakkeldy/.hermes/skills/custom-learning-audiobook"
EXTERNAL_SKILL_STUB = f"""---
name: custom-learning-audiobook
description: Disabled duplicate. Load the canonical shared custom-learning-audiobook skill.
---

# Disabled Duplicate

## {DISABLED_MARKER}

Stop. Do not execute any workflow from this directory.
Load `{CANONICAL_ROUTE}` and follow that canonical skill.
"""
EXTERNAL_PACKAGE_STUB = f"""# {DISABLED_MARKER}

Stop. This duplicate package reference is not executable.
Load `{CANONICAL_ROUTE}` and follow that canonical skill.
"""


class InstalledCustomLearningSkillContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.tmp = Path(self.temporary.name)
        self.candidate = self.tmp / "candidate"
        self.canonical = self.tmp / "canonical"
        self.external = self.tmp / "external"
        self.links = [self.tmp / f"agent-{index}" for index in range(4)]
        self.hermes = self.tmp / "hermes"
        for root in (self.candidate, self.canonical, self.external):
            (root / "references").mkdir(parents=True)
            (root / "scripts").mkdir()
        for link in self.links:
            link.symlink_to(self.canonical, target_is_directory=True)
        self.write_skill(self.candidate, "candidate")
        self.write_skill(self.canonical, "old canonical")
        self.write_disabled_external()
        self.write_hermes_discovery("custom-learning-audiobook | local | enabled")

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
        (self.external / "SKILL.md").write_text(
            EXTERNAL_SKILL_STUB,
            encoding="utf-8",
        )
        (self.external / "references" / "package-and-qc.md").write_text(
            EXTERNAL_PACKAGE_STUB,
            encoding="utf-8",
        )

    def write_hermes_discovery(self, output: str) -> None:
        self.hermes.write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            "[[ ${1:-} == skills && ${2:-} == list && ${3:-} == --source "
            "&& ${4:-} == local ]]\n"
            f"printf '%s\\n' {output!r}\n",
            encoding="utf-8",
        )
        self.hermes.chmod(self.hermes.stat().st_mode | stat.S_IXUSR)

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
            "--hermes-command",
            str(self.hermes),
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

    def test_rejects_active_alternate_with_marker_and_route_later(self) -> None:
        (self.external / "SKILL.md").write_text(
            "# Active alternate\n\nRun this independent workflow first.\n\n"
            f"{DISABLED_MARKER}\n{CANONICAL_ROUTE}\n",
            encoding="utf-8",
        )
        result = self.run_validator()
        self.assertEqual(1, result.returncode)
        self.assertIn("not the exact disabled stub", result.stderr)

    def test_rejects_when_hermes_discovers_openclaw_alternate(self) -> None:
        self.write_hermes_discovery(
            "custom-learning-audiobook | openclaw-imports | local | enabled"
        )
        result = self.run_validator()
        self.assertEqual(1, result.returncode)
        self.assertIn(
            "Hermes discovery did not select the canonical skill", result.stderr
        )

    @unittest.skipUnless(LIVE_HERMES_IMPORT.exists(), "live Hermes import is absent")
    def test_live_independent_hermes_import_is_disabled_and_canonical_routed(
        self,
    ) -> None:
        for path in (
            (LIVE_HERMES_IMPORT / "SKILL.md", EXTERNAL_SKILL_STUB),
            (
                LIVE_HERMES_IMPORT / "references" / "package-and-qc.md",
                EXTERNAL_PACKAGE_STUB,
            ),
        ):
            live_path, expected = path
            self.assertEqual(expected, live_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
