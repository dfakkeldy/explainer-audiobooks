from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import shlex
import signal
import socket
import stat
import subprocess
import tempfile
import time
import unittest
import importlib.util
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
NARRATE_WRAPPER = (
    ROOT
    / "skills"
    / "custom-learning-audiobook"
    / "scripts"
    / "echo_pronunciation_narrate.sh"
)


def load_audit_validator_module():
    specification = importlib.util.spec_from_file_location(
        "custom_learning_pronunciation_audit_validator",
        AUDIT_VALIDATOR,
    )
    if specification is None or specification.loader is None:
        raise RuntimeError(f"cannot import {AUDIT_VALIDATOR}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


AUDIT_VALIDATOR_MODULE = load_audit_validator_module()


class EchoPronunciationPreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.tmp = Path(self.temporary.name)
        self.echo = self.tmp / "Echo"
        self.explainer = self.tmp / "explainer-audiobooks"
        self.home = self.tmp / "home"
        self.run_root = (
            self.explainer / ".build" / "custom-learning-audiobooks" / "fixture"
        )
        self.cli = (
            self.echo / ".build" / "cli" / "Build" / "Products" / "Release" / "echo-cli"
        )

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
            "if [[ -n ${FAKE_ECHO_ENV_LOG:-} ]]; then\n"
            "  printf 'CALL=%s:%s ECHO_RESOURCE_DIR=%s\\n' "
            '"${1:-}" "${2:-}" "${ECHO_RESOURCE_DIR-<unset>}" '
            '>>"$FAKE_ECHO_ENV_LOG"\n'
            "fi\n"
            "if [[ ${1:-} == --version ]]; then\n"
            "  echo 'echo-cli fixture (Release)'\n"
            "elif [[ ${1:-} == narrate && ${2:-} == --help ]]; then\n"
            f"  echo '{help_text}'\n"
            "elif [[ ${1:-} == narrate ]]; then\n"
            "  shift\n"
            "  if [[ -n ${FAKE_NARRATE_LOG:-} ]]; then\n"
            '    printf \'BEGIN=%s\\n\' "$BASHPID" >>"$FAKE_NARRATE_LOG"\n'
            '    printf \'ARG=%s\\n\' "$@" >>"$FAKE_NARRATE_LOG"\n'
            "  fi\n"
            "  work= db= out=\n"
            "  while (( $# )); do\n"
            '    case "$1" in\n'
            "      --work-dir) work=$2; shift 2 ;;\n"
            "      --db) db=$2; shift 2 ;;\n"
            "      --out) out=$2; shift 2 ;;\n"
            "      --resume) shift ;;\n"
            "      *) shift ;;\n"
            "    esac\n"
            "  done\n"
            '  [[ -z ${FAKE_NARRATE_READY:-} ]] || touch "$FAKE_NARRATE_READY"\n'
            "  if [[ -n ${FAKE_NARRATE_RELEASE:-} ]]; then\n"
            "    while [[ ! -e $FAKE_NARRATE_RELEASE ]]; do sleep 0.05; done\n"
            "  fi\n"
            '  [[ -z $work ]] || mkdir -p "$work"\n'
            '  [[ -z $db ]] || touch "$db"\n'
            '  [[ -z $out ]] || touch "$out"\n'
            '  exit "${FAKE_NARRATE_EXIT:-0}"\n'
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
                "TITLE": "Fixture Book",
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
            "set -euo pipefail\n" f"source {shlex.quote(str(PREFLIGHT))}\n" f"{body}\n"
        )
        return subprocess.run(
            ["bash", "-c", command],
            cwd=self.explainer,
            env=environment or self.environment(),
            capture_output=True,
            text=True,
        )

    def run_narrate(
        self,
        *arguments: str,
        environment: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(NARRATE_WRAPPER), *arguments],
            cwd=self.explainer,
            env=environment or self.environment(),
            capture_output=True,
            text=True,
        )

    @staticmethod
    def wait_for_path(path: Path, process: subprocess.Popen[str]) -> None:
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if path.exists():
                return
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                raise AssertionError(
                    f"process exited before {path} appeared: {stdout=} {stderr=}"
                )
            time.sleep(0.05)
        raise AssertionError(f"timed out waiting for {path}")

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

    def test_approved_revision_is_part_of_every_render_identity(self) -> None:
        def run_with_approval(approved_sha: str) -> dict[str, str]:
            environment = self.environment()
            environment["APPROVED_ECHO_PRONUNCIATION_SHA"] = approved_sha
            result = self.run_preflight(
                environment=environment,
                body=(
                    "echo_pronunciation_preflight\n"
                    'printf "run_id=%s\\nwork=%s\\ndb=%s\\nreceipt=%s\\n" '
                    '"$RUN_ID" "$WORK" "$DB" "$ECHO_RENDER_INPUT_RECEIPT"'
                ),
            )
            self.assertEqual(0, result.returncode, result.stderr)
            return dict(
                line.split("=", 1)
                for line in result.stdout.splitlines()
                if line.startswith(("run_id=", "work=", "db=", "receipt="))
            )

        first = run_with_approval(self.first_sha)
        second = run_with_approval(self.second_sha)

        for field in ("run_id", "work", "db", "receipt"):
            with self.subTest(field=field):
                self.assertNotEqual(first[field], second[field])
        self.assertIn(self.first_sha, first["run_id"])
        self.assertIn(self.second_sha, second["run_id"])
        self.assertEqual(
            self.first_sha,
            dict(
                line.split("=", 1)
                for line in Path(first["receipt"])
                .read_text(encoding="utf-8")
                .splitlines()
            )["approved_echo_pronunciation_sha"],
        )
        self.assertEqual(
            self.second_sha,
            dict(
                line.split("=", 1)
                for line in Path(second["receipt"])
                .read_text(encoding="utf-8")
                .splitlines()
            )["approved_echo_pronunciation_sha"],
        )

    def test_preflight_rejects_mismatched_receipt_or_unreceipted_capture(self) -> None:
        result = self.run_preflight(
            body=(
                "echo_pronunciation_preflight\n"
                'printf "work=%s\\nreceipt=%s\\n" '
                '"$WORK" "$ECHO_RENDER_INPUT_RECEIPT"'
            )
        )
        self.assertEqual(0, result.returncode, result.stderr)
        fields = dict(
            line.split("=", 1)
            for line in result.stdout.splitlines()
            if line.startswith(("work=", "receipt="))
        )
        receipt = Path(fields["receipt"])
        receipt.write_text("approved_echo_pronunciation_sha=wrong\n", encoding="utf-8")

        mismatch = self.run_preflight()
        self.assertNotEqual(0, mismatch.returncode)
        self.assertIn("existing render-input receipt does not match", mismatch.stderr)

        receipt.unlink()
        Path(fields["work"]).mkdir(parents=True)
        unreceipted = self.run_preflight()
        self.assertNotEqual(0, unreceipted.returncode)
        self.assertIn(
            "pre-existing WORK or DB requires a matching receipt", unreceipted.stderr
        )

    def test_preflight_accepts_matching_receipt_for_resume_paths(self) -> None:
        result = self.run_preflight(
            body=(
                "echo_pronunciation_preflight\n"
                'mkdir -p "$WORK"\n'
                'touch "$DB"\n'
                "echo_pronunciation_preflight\n"
                'printf "receipt=%s\\n" "$ECHO_RENDER_INPUT_RECEIPT"'
            )
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("receipt=", result.stdout)

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

    def test_narration_wrapper_uses_exact_content_addressed_paths(self) -> None:
        log = self.tmp / "narrate.log"
        environment = self.environment()
        environment["FAKE_NARRATE_LOG"] = str(log)

        result = self.run_narrate(environment=environment)

        self.assertEqual(0, result.returncode, result.stderr)
        arguments = [
            line.removeprefix("ARG=")
            for line in log.read_text(encoding="utf-8").splitlines()
            if line.startswith("ARG=")
        ]
        self.assertEqual(
            [
                "--epub",
                str(self.run_root / "dist" / "fixture.epub"),
                "--out",
                str(self.run_root / "dist" / "fixture.m4b"),
                "--sidecar",
                str(self.run_root / "dist" / "fixture.alignment.json"),
                "--voice",
                "am_michael",
                "--title",
                "Fixture Book",
                "--author",
                "Dan Fakkeldy",
                "--work-dir",
                next(
                    argument
                    for index, argument in enumerate(arguments)
                    if arguments[index - 1] == "--work-dir"
                ),
                "--db",
                next(
                    argument
                    for index, argument in enumerate(arguments)
                    if arguments[index - 1] == "--db"
                ),
                "--jobs",
                "1",
                "--threads",
                "2",
            ],
            arguments,
        )
        work = Path(arguments[arguments.index("--work-dir") + 1])
        database = Path(arguments[arguments.index("--db") + 1])
        self.assertEqual(self.run_root, work.parent)
        self.assertEqual(self.run_root, database.parent)
        run_id = work.name.removeprefix("audio-work-")
        self.assertEqual(f"narration-{run_id}.sqlite", database.name)
        lease_root = (
            self.home / ".cache" / "explainer-audiobooks" / "echo-pronunciation-leases"
        )
        self.assertEqual(6, len(list(lease_root.glob("*.lock"))))
        self.assertFalse(
            (self.run_root / "research" / "echo-render-output.owner.env").exists()
        )

    def test_wrapper_clears_inherited_echo_resource_dir_for_every_cli_call(
        self,
    ) -> None:
        environment_log = self.tmp / "echo-environment.log"
        environment = self.environment()
        environment["ECHO_RESOURCE_DIR"] = "/stale/debug/resources"
        environment["FAKE_ECHO_ENV_LOG"] = str(environment_log)

        result = self.run_narrate(environment=environment)

        self.assertEqual(0, result.returncode, result.stderr)
        calls = environment_log.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            [
                "CALL=--version: ECHO_RESOURCE_DIR=<unset>",
                "CALL=narrate:--help ECHO_RESOURCE_DIR=<unset>",
                "CALL=narrate:--epub ECHO_RESOURCE_DIR=<unset>",
            ],
            calls,
        )

    def test_concurrent_owner_fails_before_narrate_then_resume_is_allowed(self) -> None:
        log = self.tmp / "narrate.log"
        ready = self.tmp / "ready"
        release = self.tmp / "release"
        environment = self.environment()
        environment.update(
            {
                "FAKE_NARRATE_LOG": str(log),
                "FAKE_NARRATE_READY": str(ready),
                "FAKE_NARRATE_RELEASE": str(release),
            }
        )
        first = subprocess.Popen(
            [str(NARRATE_WRAPPER)],
            cwd=self.explainer,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.addCleanup(lambda: first.poll() is None and first.kill())
        self.wait_for_path(ready, first)
        owner = self.run_root / "research" / "echo-render-output.owner.env"
        self.assertTrue(owner.is_file())

        contender_environment = environment.copy()
        contender_environment["APPROVED_ECHO_PRONUNCIATION_SHA"] = self.second_sha
        contender = self.run_narrate(environment=contender_environment)

        self.assertEqual(75, contender.returncode, contender.stderr)
        self.assertIn("active narration lease", contender.stderr)
        self.assertEqual(
            1,
            log.read_text(encoding="utf-8").count("BEGIN="),
            "contender reached echo-cli narrate",
        )

        release.touch()
        first_stdout, first_stderr = first.communicate(timeout=5)
        self.assertEqual(0, first.returncode, f"{first_stdout}\n{first_stderr}")
        self.assertFalse(owner.exists())

        resumed_environment = self.environment()
        resumed_environment["FAKE_NARRATE_LOG"] = str(log)
        resumed = self.run_narrate("--resume", environment=resumed_environment)
        self.assertEqual(0, resumed.returncode, resumed.stderr)
        log_lines = log.read_text(encoding="utf-8").splitlines()
        self.assertEqual(2, sum(line.startswith("BEGIN=") for line in log_lines))
        self.assertIn("ARG=--resume", log_lines)
        self.assertFalse(owner.exists())

    def test_stale_lock_recovery_is_local_explicit_and_exact(self) -> None:
        preflight = self.run_preflight(
            body=(
                "echo_pronunciation_preflight\n"
                'printf "run_id=%s\\nwork=%s\\ndb=%s\\n" "$RUN_ID" "$WORK" "$DB"'
            )
        )
        self.assertEqual(0, preflight.returncode, preflight.stderr)
        fields = dict(
            line.split("=", 1)
            for line in preflight.stdout.splitlines()
            if line.startswith(("run_id=", "work=", "db="))
        )
        owner = self.run_root / "research" / "echo-render-output.owner.env"

        def write_owner(hostname: str = socket.gethostname()) -> None:
            owner.write_text(
                "\n".join(
                    (
                        "lock_schema=2",
                        f"owner_token={'a' * 64}",
                        "owner_pid=99999999",
                        f"owner_host={hostname}",
                        "owner_start=Mon Jan  1 00:00:00 2001",
                        f"run_id={fields['run_id']}",
                        f"work_dir={fields['work']}",
                        f"narration_db={fields['db']}",
                        f"output_m4b={self.run_root / 'dist' / 'fixture.m4b'}",
                        f"output_sidecar={self.run_root / 'dist' / 'fixture.alignment.json'}",
                        f"output_audit={self.run_root / 'dist' / 'fixture.pronunciation-audit.json'}",
                        f"output_reel={self.run_root / 'dist' / 'fixture.pronunciation-reel.m4b'}",
                    )
                )
                + "\n",
                encoding="utf-8",
            )

        write_owner()
        ordinary = self.run_narrate()
        self.assertEqual(0, ordinary.returncode, ordinary.stderr)
        self.assertIn("recovered stale local narration owner", ordinary.stderr)
        self.assertFalse(owner.exists())

        write_owner("remote.example")
        remote = self.run_narrate("--recover-stale-lock")
        self.assertEqual(75, remote.returncode)
        self.assertIn("remote narration lock", remote.stderr)
        self.assertTrue(owner.exists())

        write_owner()
        malformed_text = owner.read_text(encoding="utf-8").replace(
            "owner_pid=99999999\n", ""
        )
        owner.write_text(malformed_text, encoding="utf-8")
        malformed = self.run_narrate("--recover-stale-lock")
        self.assertEqual(75, malformed.returncode)
        self.assertIn("malformed narration lock", malformed.stderr)
        self.assertTrue(owner.exists())

        write_owner()
        recovered = self.run_narrate("--recover-stale-lock")
        self.assertEqual(0, recovered.returncode, recovered.stderr)
        self.assertIn("stale narration lock recovered", recovered.stdout)
        self.assertFalse(owner.exists())

        fresh = self.run_narrate()
        self.assertEqual(0, fresh.returncode, fresh.stderr)
        self.assertFalse(owner.exists())

    def test_narration_lock_releases_on_cli_failure_and_signal(self) -> None:
        failed_environment = self.environment()
        failed_environment["FAKE_NARRATE_EXIT"] = "42"
        failed = self.run_narrate(environment=failed_environment)
        self.assertEqual(42, failed.returncode)
        owner = self.run_root / "research" / "echo-render-output.owner.env"
        self.assertFalse(owner.exists())

        ready = self.tmp / "signal-ready"
        release = self.tmp / "never-release"
        signaled_environment = self.environment()
        signaled_environment.update(
            {
                "FAKE_NARRATE_READY": str(ready),
                "FAKE_NARRATE_RELEASE": str(release),
            }
        )
        process = subprocess.Popen(
            [str(NARRATE_WRAPPER)],
            cwd=self.explainer,
            env=signaled_environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.addCleanup(lambda: process.poll() is None and process.kill())
        self.wait_for_path(ready, process)
        process.send_signal(signal.SIGTERM)
        process.communicate(timeout=5)
        self.assertEqual(143, process.returncode)
        self.assertFalse(owner.exists())

    def test_locked_postcheck_rejects_epub_changed_during_narration(self) -> None:
        ready = self.tmp / "hash-ready"
        release = self.tmp / "hash-release"
        environment = self.environment()
        environment.update(
            {
                "FAKE_NARRATE_READY": str(ready),
                "FAKE_NARRATE_RELEASE": str(release),
            }
        )
        process = subprocess.Popen(
            [str(NARRATE_WRAPPER)],
            cwd=self.explainer,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.addCleanup(lambda: process.poll() is None and process.kill())
        self.wait_for_path(ready, process)
        (self.run_root / "dist" / "fixture.epub").write_bytes(b"changed")
        release.touch()
        stdout, stderr = process.communicate(timeout=5)
        self.assertEqual(65, process.returncode, f"{stdout}\n{stderr}")
        self.assertIn("EPUB changed while narration lease was held", stderr)
        owner = self.run_root / "research" / "echo-render-output.owner.env"
        self.assertFalse(owner.exists())

    def test_locked_postcheck_rejects_receipt_changed_during_narration(self) -> None:
        ready = self.tmp / "receipt-ready"
        release = self.tmp / "receipt-release"
        environment = self.environment()
        environment.update(
            {
                "FAKE_NARRATE_READY": str(ready),
                "FAKE_NARRATE_RELEASE": str(release),
            }
        )
        process = subprocess.Popen(
            [str(NARRATE_WRAPPER)],
            cwd=self.explainer,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.addCleanup(lambda: process.poll() is None and process.kill())
        self.wait_for_path(ready, process)
        receipts = list((self.run_root / "research").glob("echo-render-inputs-*.env"))
        self.assertEqual(1, len(receipts))
        receipts[0].write_text("tampered=true\n", encoding="utf-8")
        release.touch()
        stdout, stderr = process.communicate(timeout=5)
        self.assertEqual(65, process.returncode, f"{stdout}\n{stderr}")
        self.assertIn("receipt changed while narration lease was held", stderr)
        owner = self.run_root / "research" / "echo-render-output.owner.env"
        self.assertFalse(owner.exists())

    def test_lease_hashes_each_canonical_shared_resource_identity(self) -> None:
        log = self.tmp / "resources.log"
        environment = self.environment()
        environment["FAKE_NARRATE_LOG"] = str(log)
        result = self.run_narrate(environment=environment)
        self.assertEqual(0, result.returncode, result.stderr)
        arguments = [
            line.removeprefix("ARG=")
            for line in log.read_text(encoding="utf-8").splitlines()
            if line.startswith("ARG=")
        ]
        resources = (
            self.run_root / "dist" / "fixture.m4b",
            self.run_root / "dist" / "fixture.alignment.json",
            self.run_root / "dist" / "fixture.pronunciation-audit.json",
            self.run_root / "dist" / "fixture.pronunciation-reel.m4b",
            Path(arguments[arguments.index("--work-dir") + 1]),
            Path(arguments[arguments.index("--db") + 1]),
        )
        expected = {
            hashlib.sha256(str(path.resolve()).encode("utf-8")).hexdigest() + ".lock"
            for path in resources
        }
        lease_root = (
            self.home / ".cache" / "explainer-audiobooks" / "echo-pronunciation-leases"
        )
        self.assertEqual(expected, {path.name for path in lease_root.glob("*.lock")})

    def test_fd_lease_survives_guardian_sigkill_until_child_exits(self) -> None:
        log = self.tmp / "sigkill.log"
        ready = self.tmp / "sigkill-ready"
        release = self.tmp / "sigkill-release"
        environment = self.environment()
        environment.update(
            {
                "FAKE_NARRATE_LOG": str(log),
                "FAKE_NARRATE_READY": str(ready),
                "FAKE_NARRATE_RELEASE": str(release),
            }
        )
        guardian = subprocess.Popen(
            [str(NARRATE_WRAPPER)],
            cwd=self.explainer,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.addCleanup(lambda: guardian.poll() is None and guardian.kill())
        self.wait_for_path(ready, guardian)
        owner = self.run_root / "research" / "echo-render-output.owner.env"
        self.assertTrue(owner.is_file())

        guardian.kill()
        guardian.wait(timeout=5)
        self.assertEqual(-signal.SIGKILL, guardian.returncode)
        contender = self.run_narrate(environment=environment)
        self.assertEqual(75, contender.returncode, contender.stderr)
        self.assertIn("active narration lease", contender.stderr)
        self.assertEqual(1, log.read_text(encoding="utf-8").count("BEGIN="))

        release.touch()
        deadline = time.monotonic() + 5
        while owner.exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        self.assertFalse(
            owner.exists(), "orphaned child did not release owner metadata"
        )
        if guardian.stdout is not None:
            guardian.stdout.close()
        if guardian.stderr is not None:
            guardian.stderr.close()

        resumed_environment = self.environment()
        resumed_environment["FAKE_NARRATE_LOG"] = str(log)
        resumed = self.run_narrate("--resume", environment=resumed_environment)
        self.assertEqual(0, resumed.returncode, resumed.stderr)


class PronunciationAuditValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.tmp = Path(self.temporary.name)
        self.audit = self.tmp / "fixture.pronunciation-audit.json"
        self.audiobook = self.tmp / "fixture.m4b"
        self.audiobook.write_bytes(b"fixture audiobook bytes")
        self.payload = {
            "schemaVersion": 2,
            "renderVersion": 12,
            "voice": "am_michael",
            "coverage": "complete",
            "watchCounts": {word: 0 for word in AUDIT_VALIDATOR_MODULE.WATCH_WORDS},
            "decisions": [],
            "diagnostics": [],
            "legacyChapterIndexes": [],
            "audiobookFileName": "fixture.m4b",
            "audiobookSHA256": hashlib.sha256(self.audiobook.read_bytes()).hexdigest(),
        }

    @staticmethod
    def valid_decision() -> dict[str, object]:
        return {
            "blockID": "fixture-s0-b1",
            "wordStart": 1,
            "wordEnd": 1,
            "normalizedWord": "filesystem",
            "sourceWord": "filesystem",
            "sourceContext": "The filesystem stores the result.",
            "selectedIPA": "fˈIl sˌɪstəm",
            "kokoroTokenIDs": [48, 156, 25, 54],
            "source": "builtInOverride",
            "ruleID": "override.built-in.filesystem",
            "rationale": "Built-in override matched filesystem.",
            "chapterIndex": 0,
            "chapterRelativeAudioRange": {"start": 1.25, "end": 1.75},
            "bookRelativeAudioRange": {"start": 1.25, "end": 1.75},
            "timingPrecision": "exactSynthesisWord",
        }

    def run_validator(self) -> subprocess.CompletedProcess[str]:
        self.audit.write_text(json.dumps(self.payload), encoding="utf-8")
        return subprocess.run(
            ["/usr/local/bin/python3", str(AUDIT_VALIDATOR), str(self.audit)],
            capture_output=True,
            text=True,
        )

    def test_accepts_complete_schema_v2_fixture_with_zero_watch_counts(self) -> None:
        result = self.run_validator()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("pronunciation_audit: clean", result.stdout)

    def test_rejects_non_v2_manifest(self) -> None:
        self.payload["schemaVersion"] = 1
        result = self.run_validator()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("schemaVersion must be 2", result.stderr)

    def test_accepts_full_schema_decision_and_matching_watch_count(self) -> None:
        self.payload["decisions"] = [self.valid_decision()]
        self.payload["watchCounts"]["filesystem"] = 1
        result = self.run_validator()
        self.assertEqual(0, result.returncode, result.stderr)

    def test_rejects_null_manifest_scalars_and_null_decision(self) -> None:
        cases = {
            "renderVersion=null": ("renderVersion", None),
            "renderVersion=bool": ("renderVersion", True),
            "renderVersion=string": ("renderVersion", "11"),
            "voice=null": ("voice", None),
            "voice=empty": ("voice", ""),
            "voice=number": ("voice", 11),
            "decisions=[null]": ("decisions", [None]),
        }
        for name, (field, value) in cases.items():
            with self.subTest(name=name):
                original = self.payload[field]
                self.payload[field] = value
                result = self.run_validator()
                self.assertNotEqual(0, result.returncode)
                self.payload[field] = original

    def test_rejects_schema_invalid_decision_fields_and_ranges(self) -> None:
        valid = self.valid_decision()
        invalid_decisions: dict[str, object] = {}

        missing_block = copy.deepcopy(valid)
        missing_block.pop("blockID")
        invalid_decisions["missing required field"] = missing_block

        reversed_words = copy.deepcopy(valid)
        reversed_words["wordEnd"] = 0
        invalid_decisions["reversed word range"] = reversed_words

        boundary_token = copy.deepcopy(valid)
        boundary_token["kokoroTokenIDs"] = [0]
        invalid_decisions["synthetic boundary token"] = boundary_token

        oversized_token = copy.deepcopy(valid)
        oversized_token["kokoroTokenIDs"] = [2**31]
        invalid_decisions["out-of-range token"] = oversized_token

        invalid_source = copy.deepcopy(valid)
        invalid_source["source"] = "madeUpSource"
        invalid_decisions["unknown source"] = invalid_source

        invalid_source_type = copy.deepcopy(valid)
        invalid_source_type["source"] = []
        invalid_decisions["non-string source"] = invalid_source_type

        reversed_audio = copy.deepcopy(valid)
        reversed_audio["chapterRelativeAudioRange"] = {"start": 2.0, "end": 1.0}
        invalid_decisions["reversed audio range"] = reversed_audio

        invalid_precision = copy.deepcopy(valid)
        invalid_precision["timingPrecision"] = "estimated"
        invalid_decisions["unknown timing precision"] = invalid_precision

        missing_chapter_range = copy.deepcopy(valid)
        missing_chapter_range.pop("chapterRelativeAudioRange")
        invalid_decisions["book timing without chapter timing"] = missing_chapter_range

        negative_chapter = copy.deepcopy(valid)
        negative_chapter["chapterIndex"] = -1
        invalid_decisions["negative chapter index"] = negative_chapter

        for name, decision in invalid_decisions.items():
            with self.subTest(name=name):
                self.payload["decisions"] = [decision]
                self.payload["watchCounts"]["filesystem"] = 1
                result = self.run_validator()
                self.assertNotEqual(0, result.returncode)

    def test_rejects_watch_count_inconsistency_across_full_vocabulary(self) -> None:
        self.payload["watchCounts"]["arithmetic"] = 1
        result = self.run_validator()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("does not match decisions", result.stderr)

    def test_rejects_deletion_of_every_zero_count_watch_word(self) -> None:
        for word in AUDIT_VALIDATOR_MODULE.WATCH_WORDS:
            with self.subTest(word=word):
                watch_counts = self.payload["watchCounts"]
                removed = watch_counts.pop(word)
                result = self.run_validator()
                self.assertNotEqual(0, result.returncode)
                self.assertIn(f"watchCounts is missing {word}", result.stderr)
                watch_counts[word] = removed

    def test_rejects_echo_integer_values_outside_signed_64_bit_bounds(self) -> None:
        cases = []
        huge = 10**100

        def render_version(value: int) -> None:
            self.payload["renderVersion"] = value

        cases.append(("renderVersion", render_version))

        def watch_count(value: int) -> None:
            self.payload["watchCounts"]["arithmetic"] = value

        cases.append(("watchCount", watch_count))

        for name, mutate in cases:
            for value in (huge, -huge):
                with self.subTest(field=name, value=value):
                    original = copy.deepcopy(self.payload)
                    try:
                        mutate(value)
                        result = self.run_validator()
                        self.assertNotEqual(0, result.returncode)
                        self.assertIn("signed 64-bit", result.stderr)
                    finally:
                        self.payload = original

        decision_integer_fields = ("wordStart", "wordEnd", "chapterIndex")
        for field in decision_integer_fields:
            for value in (huge, -huge):
                with self.subTest(field=field, value=value):
                    original = copy.deepcopy(self.payload)
                    try:
                        decision = self.valid_decision()
                        decision[field] = value
                        self.payload["decisions"] = [decision]
                        self.payload["watchCounts"]["filesystem"] = 1
                        result = self.run_validator()
                        self.assertNotEqual(0, result.returncode)
                        self.assertIn("signed 64-bit", result.stderr)
                    finally:
                        self.payload = original

    def test_watch_vocabulary_matches_real_echo_acceptance_artifact(self) -> None:
        artifact = Path(
            "/Users/dfakkeldy/Developer/echo-overnight/"
            "pronunciation-acceptance-20260713-superseded-f3852939/"
            "pronunciation-regression-acceptance-20260713.pronunciation-audit.json"
        )
        if not artifact.is_file():
            self.skipTest("real Echo pronunciation acceptance artifact is unavailable")
        payload = json.loads(artifact.read_text(encoding="utf-8"))
        self.assertEqual(
            set(payload["watchCounts"]),
            set(AUDIT_VALIDATOR_MODULE.WATCH_WORDS),
        )

    def test_real_media_bound_echo_acceptance_artifact_validates(self) -> None:
        artifact = Path(
            "/Users/dfakkeldy/Developer/echo-overnight/"
            "pronunciation-acceptance-20260713-superseded-f3852939/"
            "pronunciation-regression-acceptance-20260713.pronunciation-audit.json"
        )
        if not artifact.is_file():
            self.skipTest("real Echo pronunciation acceptance artifact is unavailable")
        payload = json.loads(artifact.read_text(encoding="utf-8"))
        if payload.get("schemaVersion") != 2 or "audiobookSHA256" not in payload:
            self.skipTest("real Echo artifact predates bound media hashes")
        result = subprocess.run(
            ["/usr/local/bin/python3", str(AUDIT_VALIDATOR), str(artifact)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)

    def test_reel_filename_and_file_presence_must_agree(self) -> None:
        reel_name = "fixture.pronunciation-reel.m4b"
        self.payload["listeningReelFileName"] = reel_name
        reel_bytes = b"fixture reel"
        self.payload["listeningReelSHA256"] = hashlib.sha256(reel_bytes).hexdigest()
        missing = self.run_validator()
        self.assertNotEqual(0, missing.returncode)

        (self.tmp / reel_name).write_bytes(reel_bytes)
        no_sample = self.run_validator()
        self.assertNotEqual(0, no_sample.returncode)
        self.assertIn("eligible timed pronunciation decision", no_sample.stderr)

        untimed = self.valid_decision()
        for field in (
            "chapterIndex",
            "chapterRelativeAudioRange",
            "bookRelativeAudioRange",
            "timingPrecision",
        ):
            untimed.pop(field, None)
        self.payload["decisions"] = [untimed]
        self.payload["watchCounts"]["filesystem"] = 1
        no_timed_sample = self.run_validator()
        self.assertNotEqual(0, no_timed_sample.returncode)
        self.assertIn("eligible timed pronunciation decision", no_timed_sample.stderr)

        self.payload["decisions"] = [self.valid_decision()]
        present = self.run_validator()
        self.assertEqual(0, present.returncode, present.stderr)

        self.payload.pop("listeningReelFileName")
        self.payload.pop("listeningReelSHA256")
        unlisted = self.run_validator()
        self.assertNotEqual(0, unlisted.returncode)
        self.assertIn("unlisted listening reel", unlisted.stderr)

    def test_audiobook_hash_binds_exact_sibling_bytes(self) -> None:
        accepted = self.run_validator()
        self.assertEqual(0, accepted.returncode, accepted.stderr)

        original = self.audiobook.read_bytes()
        self.audiobook.write_bytes(b"X" * len(original))
        mutated = self.run_validator()
        self.assertNotEqual(0, mutated.returncode)
        self.assertIn("audiobookSHA256 does not match", mutated.stderr)

        self.audiobook.write_bytes(original)
        self.payload["audiobookSHA256"] = self.payload["audiobookSHA256"].upper()
        uppercase = self.run_validator()
        self.assertNotEqual(0, uppercase.returncode)
        self.assertIn("64 lowercase hexadecimal", uppercase.stderr)

    def test_reel_hash_is_paired_and_binds_exact_sibling_bytes(self) -> None:
        reel = self.tmp / "fixture.pronunciation-reel.m4b"
        reel_bytes = b"paired reel bytes"
        reel.write_bytes(reel_bytes)
        self.payload["decisions"] = [self.valid_decision()]
        self.payload["watchCounts"]["filesystem"] = 1
        self.payload["listeningReelFileName"] = reel.name

        missing_hash = self.run_validator()
        self.assertNotEqual(0, missing_hash.returncode)
        self.assertIn("must appear together", missing_hash.stderr)

        self.payload["listeningReelSHA256"] = hashlib.sha256(reel_bytes).hexdigest()
        accepted = self.run_validator()
        self.assertEqual(0, accepted.returncode, accepted.stderr)

        reel.write_bytes(b"Z" * len(reel_bytes))
        mutated = self.run_validator()
        self.assertNotEqual(0, mutated.returncode)
        self.assertIn("listeningReelSHA256 does not match", mutated.stderr)

        self.payload["listeningReelFileName"] = None
        hash_without_name = self.run_validator()
        self.assertNotEqual(0, hash_without_name.returncode)
        self.assertIn("must appear together", hash_without_name.stderr)


if __name__ == "__main__":
    unittest.main()
