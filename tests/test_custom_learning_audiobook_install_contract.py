from __future__ import annotations

import json
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
LIVE_HERMES_AGENT = Path.home() / ".hermes" / "hermes-agent"
LIVE_HERMES_PYTHON = LIVE_HERMES_AGENT / "venv" / "bin" / "python"
LIVE_CANONICAL_SKILL = Path.home() / ".hermes" / "skills" / "custom-learning-audiobook"
DISABLED_MARKER = "DISABLED: canonical skill required"
CANONICAL_ROUTE = "/Users/dfakkeldy/.hermes/skills/custom-learning-audiobook"
EXTERNAL_SKILL_TOMBSTONE = f"""---
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
SKILL_FILES = {
    "SKILL.md": 0o644,
    "agents/openai.yaml": 0o644,
    "references/intake-and-research.md": 0o644,
    "references/package-and-qc.md": 0o644,
    "scripts/echo_pronunciation_preflight.sh": 0o755,
    "scripts/echo_learning_pilot_narrate.sh": 0o755,
    "scripts/validate_pronunciation_audit.py": 0o755,
    "scripts/echo_pronunciation_narrate.sh": 0o755,
    "scripts/echo_pronunciation_lease.py": 0o755,
    "scripts/echo_pronunciation_state.py": 0o755,
}


class InstalledCustomLearningSkillContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.tmp = Path(self.temporary.name)
        self.candidate = self.tmp / "candidate"
        self.canonical = self.tmp / "installed" / "custom-learning-audiobook"
        self.external = self.tmp / "external"
        self.links = [self.tmp / f"agent-{index}" for index in range(4)]
        self.hermes = self.tmp / "hermes"
        self.hermes_agent = self.tmp / "hermes-agent"
        self.hermes_python = self.tmp / "hermes-python"
        for root in (self.candidate, self.canonical, self.external):
            (root / "agents").mkdir(parents=True)
            (root / "references").mkdir(parents=True)
            (root / "scripts").mkdir()
        for link in self.links:
            link.symlink_to(self.canonical, target_is_directory=True)
        self.write_skill(self.candidate, "candidate")
        self.write_skill(self.canonical, "old canonical")
        self.write_disabled_external()
        self.write_hermes_discovery("custom-learning-audiobook | local | enabled")
        self.hermes_agent.mkdir()
        self.write_hermes_view()

    @staticmethod
    def write_skill(root: Path, value: str) -> None:
        for relative, mode in SKILL_FILES.items():
            path = root / relative
            path.write_text(value, encoding="utf-8")
            path.chmod(mode)

    def integrate_candidate(self) -> None:
        for relative_path in SKILL_FILES:
            shutil.copy2(
                self.candidate / relative_path,
                self.canonical / relative_path,
            )

    def write_disabled_external(self) -> None:
        (self.external / "SKILL.disabled.md").write_text(
            EXTERNAL_SKILL_TOMBSTONE,
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

    def write_hermes_view(
        self,
        *,
        skill_dir: Path | None = None,
        success: bool = True,
    ) -> None:
        selected = skill_dir or self.canonical
        self.hermes_python.write_text(
            "#!/usr/local/bin/python3\n"
            "import json\n"
            "from pathlib import Path\n"
            f"skill_dir = Path({str(selected)!r})\n"
            "print(json.dumps({\n"
            f"    'success': {success!r},\n"
            "    'skill_dir': str(skill_dir),\n"
            "    'content': (skill_dir / 'SKILL.md').read_text(encoding='utf-8'),\n"
            "}))\n",
            encoding="utf-8",
        )
        self.hermes_python.chmod(self.hermes_python.stat().st_mode | stat.S_IXUSR)

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
            "--hermes-python",
            str(self.hermes_python),
            "--hermes-source-root",
            str(self.hermes_agent),
        ]
        for link in self.links:
            command.extend(("--link", str(link)))
        return subprocess.run(command, capture_output=True, text=True)

    def test_reports_pending_when_installed_canonical_content_is_old(self) -> None:
        result = self.run_validator()
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn("installed_skill_parity: pending-integration", result.stdout)

    def test_reports_current_after_candidate_is_integrated(self) -> None:
        self.integrate_candidate()
        result = self.run_validator()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("installed_skill_parity: current", result.stdout)

    def test_reports_pending_when_canonical_lacks_a_new_helper(self) -> None:
        self.integrate_candidate()
        (self.canonical / "scripts" / "echo_pronunciation_preflight.sh").unlink()
        result = self.run_validator()
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn("installed_skill_parity: pending-integration", result.stdout)

    def test_reports_pending_when_contract_file_mode_differs(self) -> None:
        self.integrate_candidate()
        helper = self.canonical / "scripts" / "echo_pronunciation_state.py"
        helper.chmod(0o700)
        result = self.run_validator()
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn("installed_skill_parity: pending-integration", result.stdout)

    def test_declared_manifest_covers_non_runtime_skill_files(self) -> None:
        self.integrate_candidate()
        (self.canonical / "agents" / "openai.yaml").write_text(
            "stale agent metadata", encoding="utf-8"
        )
        stale_agent = self.run_validator()
        self.assertEqual(2, stale_agent.returncode, stale_agent.stderr)

        shutil.copy2(
            self.candidate / "agents" / "openai.yaml",
            self.canonical / "agents" / "openai.yaml",
        )
        (self.canonical / "references" / "intake-and-research.md").unlink()
        missing_reference = self.run_validator()
        self.assertEqual(2, missing_reference.returncode, missing_reference.stderr)

    def test_declared_manifest_rejects_missing_unexpected_and_wrong_mode_candidate(
        self,
    ) -> None:
        missing = self.candidate / "agents" / "openai.yaml"
        original = missing.read_bytes()
        missing.unlink()
        missing_result = self.run_validator()
        self.assertEqual(1, missing_result.returncode)
        self.assertIn("candidate manifest", missing_result.stderr)

        missing.write_bytes(original)
        missing.chmod(0o644)
        unexpected = self.candidate / "scripts" / "shadow_runtime.py"
        unexpected.write_text("pass\n", encoding="utf-8")
        unexpected_result = self.run_validator()
        self.assertEqual(1, unexpected_result.returncode)
        self.assertIn("unexpected", unexpected_result.stderr)

        unexpected.unlink()
        helper = self.candidate / "scripts" / "echo_pronunciation_state.py"
        helper.chmod(0o644)
        wrong_mode = self.run_validator()
        self.assertEqual(1, wrong_mode.returncode)
        self.assertIn("mode", wrong_mode.stderr)

    def test_declared_manifest_rejects_unexpected_installed_entry(self) -> None:
        self.integrate_candidate()
        (self.canonical / "references" / "shadow.md").write_text(
            "stale", encoding="utf-8"
        )
        result = self.run_validator()
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn("pending-integration", result.stdout)

    def test_declared_manifest_ignores_only_explicit_transient_files(self) -> None:
        self.integrate_candidate()
        for root, value in ((self.candidate, b"candidate"), (self.canonical, b"old")):
            cache = root / "scripts" / "__pycache__"
            cache.mkdir()
            (cache / "helper.cpython-314.pyc").write_bytes(value)
            (root / ".DS_Store").write_bytes(value)
        result = self.run_validator()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("installed_skill_parity: current", result.stdout)

    def test_rejects_active_alternate_with_marker_and_route_later(self) -> None:
        (self.external / "SKILL.md").write_text(
            "# Active alternate\n\nRun this independent workflow first.\n\n"
            f"{DISABLED_MARKER}\n{CANONICAL_ROUTE}\n",
            encoding="utf-8",
        )
        result = self.run_validator()
        self.assertEqual(1, result.returncode)
        self.assertIn("discoverable independent Hermes skill", result.stderr)

    def test_rejects_nested_discoverable_alternate(self) -> None:
        nested = self.external / "historical" / "copy"
        nested.mkdir(parents=True)
        (nested / "SKILL.md").write_text("nested alternate", encoding="utf-8")
        result = self.run_validator()
        self.assertEqual(1, result.returncode)
        self.assertIn("discoverable independent Hermes skill", result.stderr)

    def test_rejects_when_hermes_discovers_openclaw_alternate(self) -> None:
        self.write_hermes_discovery(
            "custom-learning-audiobook | openclaw-imports | local | enabled"
        )
        result = self.run_validator()
        self.assertEqual(1, result.returncode)
        self.assertIn(
            "Hermes discovery did not select the canonical skill", result.stderr
        )

    def test_rejects_bare_hermes_view_resolving_noncanonical_skill(self) -> None:
        alternate = self.tmp / "alternate" / "custom-learning-audiobook"
        alternate.mkdir(parents=True)
        (alternate / "SKILL.md").write_text("alternate", encoding="utf-8")
        self.write_hermes_view(skill_dir=alternate)
        result = self.run_validator()
        self.assertEqual(1, result.returncode)
        self.assertIn("bare skill_view did not load canonical skill", result.stderr)

    @unittest.skipUnless(LIVE_HERMES_IMPORT.exists(), "live Hermes import is absent")
    def test_live_independent_hermes_import_is_disabled_and_canonical_routed(
        self,
    ) -> None:
        self.assertFalse((LIVE_HERMES_IMPORT / "SKILL.md").exists())
        for path in (
            (
                LIVE_HERMES_IMPORT / "SKILL.disabled.md",
                EXTERNAL_SKILL_TOMBSTONE,
            ),
            (
                LIVE_HERMES_IMPORT / "references" / "package-and-qc.md",
                EXTERNAL_PACKAGE_STUB,
            ),
        ):
            live_path, expected = path
            self.assertEqual(expected, live_path.read_text(encoding="utf-8"))

    @unittest.skipUnless(
        LIVE_HERMES_PYTHON.is_file() and LIVE_CANONICAL_SKILL.exists(),
        "live Hermes agent or canonical skill is absent",
    )
    def test_live_bare_skill_view_loads_only_canonical_content(self) -> None:
        code = (
            "from tools.skills_tool import skill_view\n"
            "print(skill_view('custom-learning-audiobook', preprocess=False))\n"
        )
        result = subprocess.run(
            [str(LIVE_HERMES_PYTHON), "-c", code],
            cwd=LIVE_HERMES_AGENT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload.get("success"), payload)
        skill_dir = Path(payload["skill_dir"])
        self.assertEqual(LIVE_CANONICAL_SKILL.resolve(), skill_dir.resolve())
        skill_file = skill_dir / "SKILL.md"
        self.assertEqual("custom-learning-audiobook", skill_file.parent.name)
        self.assertEqual(
            (LIVE_CANONICAL_SKILL / "SKILL.md").resolve(), skill_file.resolve()
        )
        self.assertEqual(
            (LIVE_CANONICAL_SKILL / "SKILL.md").read_text(encoding="utf-8"),
            payload["content"],
        )


if __name__ == "__main__":
    unittest.main()
