from __future__ import annotations

import json
import os
import re
import shlex
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
PREFLIGHT = (
    ROOT
    / "skills"
    / "custom-learning-audiobook"
    / "scripts"
    / "echo_pronunciation_preflight.sh"
)
AUDIT_VALIDATOR = (
    ROOT
    / "skills"
    / "custom-learning-audiobook"
    / "scripts"
    / "validate_pronunciation_audit.py"
)


class EchoPronunciationPreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.tmp = Path(self.temporary.name)
        self.echo = self.tmp / "Echo"
        self.explainer = self.tmp / "explainer-audiobooks"
        self.home = self.tmp / "home"
        self.run_root = self.explainer / ".build" / "custom-learning-audiobooks" / "fixture"
        self.cli = self.echo / ".build" / "cli" / "Build" / "Products" / "Release" / "echo-cli"

        self.echo.mkdir(parents=True)
        self.explainer.mkdir()
        (self.echo / "Makefile").write_text(
            "echo-cli:\n\t@test -x .build/cli/Build/Products/Release/echo-cli\n",
            encoding="utf-8",
        )
        (self.echo / ".gitignore").write_text(".build/\n", encoding="utf-8")
        self.cli.parent.mkdir(parents=True)
        self.write_cli(include_review_flag=True)

        gate = self.home / ".claude" / "bin" / "xcode-build-gate.sh"
        gate.parent.mkdir(parents=True)
        gate.write_text(
            "#!/usr/bin/env bash\nset -euo pipefail\n[[ ${1:-} == --wait ]]\n",
            encoding="utf-8",
        )
        gate.chmod(gate.stat().st_mode | stat.S_IXUSR)

        (self.run_root / "dist").mkdir(parents=True)
        (self.run_root / "dist" / "fixture.epub").write_bytes(b"fixture epub")

        self.git("init", "-q")
        self.git("config", "user.email", "fixture@example.com")
        self.git("config", "user.name", "Fixture")
        self.git("add", "Makefile", ".gitignore")
        self.git("commit", "-qm", "first")
        self.first_sha = self.git("rev-parse", "HEAD").stdout.strip()
        (self.echo / "revision.txt").write_text("second\n", encoding="utf-8")
        self.git("add", "revision.txt")
        self.git("commit", "-qm", "second")
        self.second_sha = self.git("rev-parse", "HEAD").stdout.strip()

    def git(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(self.echo), *arguments],
            check=True,
            capture_output=True,
            text=True,
        )

    def write_cli(self, *, include_review_flag: bool) -> None:
        help_text = "--no-pronunciation-review" if include_review_flag else "--voice"
        self.cli.write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            "if [[ ${1:-} == --version ]]; then\n"
            "  echo 'echo-cli fixture (Release)'\n"
            "elif [[ ${1:-} == narrate && ${2:-} == --help ]]; then\n"
            f"  echo '{help_text}'\n"
            "else\n"
            "  exit 64\n"
            "fi\n",
            encoding="utf-8",
        )
        self.cli.chmod(self.cli.stat().st_mode | stat.S_IXUSR)

    def environment(self) -> dict[str, str]:
        environment = os.environ.copy()
        environment.update(
            {
                "HOME": str(self.home),
                "ECHO_REPO": str(self.echo),
                "APPROVED_ECHO_PRONUNCIATION_SHA": self.first_sha,
                "SLUG": "fixture",
                "RUN_ROOT": str(self.run_root),
                "VOICE": "am_michael",
            }
        )
        return environment

    def run_preflight(
        self,
        *,
        environment: dict[str, str] | None = None,
        body: str = "echo_pronunciation_preflight",
    ) -> subprocess.CompletedProcess[str]:
        command = (
            "set -euo pipefail\n"
            f"source {shlex.quote(str(PREFLIGHT))}\n"
            f"{body}\n"
        )
        return subprocess.run(
            ["bash", "-c", command],
            cwd=self.explainer,
            env=environment or self.environment(),
            capture_output=True,
            text=True,
        )

    def test_valid_preflight_preserves_cwd_and_records_provenance(self) -> None:
        result = self.run_preflight(
            body=(
                'before="$PWD"\n'
                "echo_pronunciation_preflight\n"
                'printf "before=%s\\nafter=%s\\nrun_id=%s\\nreceipt=%s\\n" '
                '"$before" "$PWD" "$RUN_ID" "$ECHO_RENDER_INPUT_RECEIPT"'
            )
        )
        self.assertEqual(0, result.returncode, result.stderr)
        resolved_explainer = self.explainer.resolve()
        self.assertIn(f"before={resolved_explainer}", result.stdout)
        self.assertIn(f"after={resolved_explainer}", result.stdout)
        self.assertRegex(result.stdout, r"run_id=[0-9a-f-]+-am_michael")

        receipt_match = re.search(r"receipt=(.+)", result.stdout)
        self.assertIsNotNone(receipt_match)
        receipt = Path(receipt_match.group(1))
        fields = dict(
            line.split("=", 1)
            for line in receipt.read_text(encoding="utf-8").splitlines()
        )
        self.assertEqual(self.first_sha, fields["approved_echo_pronunciation_sha"])
        self.assertEqual(self.second_sha, fields["echo_source_sha"])
        self.assertRegex(fields["epub_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(fields["echo_cli_sha256"], r"^[0-9a-f]{64}$")

    def test_preflight_rejects_missing_approval(self) -> None:
        environment = self.environment()
        environment.pop("APPROVED_ECHO_PRONUNCIATION_SHA")
        result = self.run_preflight(environment=environment)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("APPROVED_ECHO_PRONUNCIATION_SHA", result.stderr)

    def test_preflight_rejects_symbolic_approval(self) -> None:
        environment = self.environment()
        environment["APPROVED_ECHO_PRONUNCIATION_SHA"] = "HEAD"
        result = self.run_preflight(environment=environment)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("canonical Git commit SHA", result.stderr)

    def test_preflight_rejects_unapproved_source_revision(self) -> None:
        self.git("checkout", "-q", "--detach", self.first_sha)
        environment = self.environment()
        environment["APPROVED_ECHO_PRONUNCIATION_SHA"] = self.second_sha
        result = self.run_preflight(environment=environment)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("not an ancestor", result.stderr)

    def test_preflight_rejects_dirty_echo_source(self) -> None:
        (self.echo / "revision.txt").write_text("uncommitted\n", encoding="utf-8")
        result = self.run_preflight()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("working tree is not clean", result.stderr)

    def test_preflight_rejects_missing_or_invalid_sha256_output(self) -> None:
        for fake_output in ("", "not-a-sha"):
            with self.subTest(fake_output=fake_output):
                fake_bin = self.tmp / f"fake-{fake_output or 'missing'}"
                fake_bin.mkdir()
                shasum = fake_bin / "shasum"
                shasum.write_text(
                    f"#!/usr/bin/env bash\nprintf '%s\\n' {shlex.quote(fake_output)}\n",
                    encoding="utf-8",
                )
                shasum.chmod(shasum.stat().st_mode | stat.S_IXUSR)
                environment = self.environment()
                environment["PATH"] = f"{fake_bin}:{environment['PATH']}"
                result = self.run_preflight(environment=environment)
                self.assertNotEqual(0, result.returncode)
                self.assertIn("64 lowercase hexadecimal", result.stderr)

    def test_preflight_rejects_cli_without_review_flag(self) -> None:
        self.write_cli(include_review_flag=False)
        result = self.run_preflight()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("pronunciation review is unavailable", result.stderr)


class PronunciationAuditValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.tmp = Path(self.temporary.name)
        self.audit = self.tmp / "fixture.pronunciation-audit.json"
        self.payload = {
            "schemaVersion": 1,
            "renderVersion": 12,
            "voice": "am_michael",
            "coverage": "complete",
            "watchCounts": {
                "startable": 0,
                "filesystem": 1,
                "verified": 0,
                "live": 1,
                "lives": 1,
                "record": 1,
            },
            "decisions": [],
            "diagnostics": [],
            "legacyChapterIndexes": [],
            "audiobookFileName": "fixture.m4b",
        }

    def run_validator(self) -> subprocess.CompletedProcess[str]:
        self.audit.write_text(json.dumps(self.payload), encoding="utf-8")
        return subprocess.run(
            ["/usr/local/bin/python3", str(AUDIT_VALIDATOR), str(self.audit)],
            capture_output=True,
            text=True,
        )

    def test_accepts_complete_schema_v1_fixture_with_zero_watch_counts(self) -> None:
        result = self.run_validator()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("pronunciation_audit: clean", result.stdout)

    def test_rejects_non_v1_manifest(self) -> None:
        self.payload["schemaVersion"] = 2
        result = self.run_validator()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("schemaVersion must be 1", result.stderr)


if __name__ == "__main__":
    unittest.main()
