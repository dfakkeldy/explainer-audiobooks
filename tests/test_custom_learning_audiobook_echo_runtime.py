from __future__ import annotations

import copy
import hashlib
import json
import os
import pwd
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
LEASE_HELPER = (
    ROOT
    / "skills"
    / "custom-learning-audiobook"
    / "scripts"
    / "echo_pronunciation_lease.py"
)
STATE_HELPER = (
    ROOT
    / "skills"
    / "custom-learning-audiobook"
    / "scripts"
    / "echo_pronunciation_state.py"
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
        self.fake_bin = self.home / "bin"
        self.run_root = (
            self.explainer / ".build" / "custom-learning-audiobooks" / "fixture"
        )
        self.cli = (
            self.echo / ".build" / "cli" / "Build" / "Products" / "Release" / "echo-cli"
        )
        self.resources = self.cli.parent / "EchoNarrationResources"
        self.lease_root = (
            Path(pwd.getpwuid(os.geteuid()).pw_dir)
            / ".cache"
            / "explainer-audiobooks"
            / "echo-pronunciation-leases"
        )

        self.echo.mkdir(parents=True)
        self.explainer.mkdir()
        (self.echo / "Makefile").write_text(
            "echo-cli:\n\t@test -x .build/cli/Build/Products/Release/echo-cli\n",
            encoding="utf-8",
        )
        (self.echo / ".gitignore").write_text(".build/\n", encoding="utf-8")
        self.cli.parent.mkdir(parents=True)
        self.resources.mkdir()
        (self.resources / "pronunciations.json").write_text(
            '{"renderVersion":12}\n', encoding="utf-8"
        )
        self.write_cli(include_review_flag=True)

        self.fake_bin.mkdir(parents=True)
        ffprobe = self.fake_bin / "ffprobe"
        ffprobe.write_text(
            "#!/usr/bin/env bash\nprintf '%s\\n' "
            '\'{"format":{"duration":"5.0"}}\'\n',
            encoding="utf-8",
        )
        ffprobe.chmod(ffprobe.stat().st_mode | stat.S_IXUSR)

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

    def write_cli(self, *, include_review_flag: bool, render_version: int = 12) -> None:
        help_text = "--no-pronunciation-review" if include_review_flag else "--voice"
        (self.resources / "pronunciations.json").write_text(
            json.dumps({"renderVersion": render_version}) + "\n", encoding="utf-8"
        )
        emitter = self.cli.parent / "fake_echo_emit.py"
        emitter_source = """#!/usr/bin/env python3
import hashlib, json, os, pathlib, sys

epub, out, sidecar, work, db = map(pathlib.Path, sys.argv[1:6])
voice = sys.argv[6]
out.parent.mkdir(parents=True, exist_ok=True)
work.mkdir(parents=True, exist_ok=True)
db.write_bytes(b"fixture database")
audio = work / "chapter-0.m4a"
audio.write_bytes(b"fixture chapter audio")
def frame(value):
    data = value.encode()
    return str(len(data)).encode() + b":" + data
raw = epub.read_bytes()
source = hashlib.sha256(frame("source-kind=epub") + frame(f"bytes={len(raw)}") + raw).hexdigest()
payload = {"duration": 1.0, "anchors": [], "pronunciationEvidence": {"decisions": [], "diagnostics": []}}
payload_bytes = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
identity = {
    "schemaVersion": 1, "captureSetID": "c" * 64, "sourceFingerprint": source,
    "voice": voice, "renderVersion": __RENDER_VERSION__, "rendererIdentity": "fixture-renderer",
    "normalizationMode": "spoken", "chapterIndex": 0,
    "chapterContentSignature": "d" * 16, "audioFileName": audio.name,
    "audioFileByteCount": audio.stat().st_size,
    "audioSHA256": hashlib.sha256(audio.read_bytes()).hexdigest(),
    "payloadSHA256": hashlib.sha256(payload_bytes).hexdigest(),
}
marker = dict(payload)
marker["identity"] = identity
(work / ".anchors-ch0.json").write_text(json.dumps(marker, sort_keys=True, separators=(",", ":")))
out.write_bytes(b"fixture audiobook bytes")
sidecar.write_text("{}\\n")
words = ("arithmetic", "campbell", "content", "fakkeldy", "filesystem", "live", "lives", "re", "read", "readme", "record", "resume", "resumes", "résumé", "résumés", "startable", "timeframe", "verified", "xcassets", "xcode")
audit = {
    "schemaVersion": 2, "renderVersion": __RENDER_VERSION__, "voice": voice, "coverage": "complete",
    "watchCounts": {word: 0 for word in words}, "decisions": [], "diagnostics": [],
    "legacyChapterIndexes": [], "audiobookFileName": out.name,
    "audiobookSHA256": hashlib.sha256(out.read_bytes()).hexdigest(),
}
if not os.environ.get("FAKE_SKIP_AUDIT"):
    out.with_suffix(".pronunciation-audit.json").write_text(json.dumps(audit))
"""
        emitter.write_text(
            emitter_source.replace("__RENDER_VERSION__", str(render_version)),
            encoding="utf-8",
        )
        emitter.chmod(emitter.stat().st_mode | stat.S_IXUSR)
        self.cli.write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            "if [[ -n ${FAKE_ECHO_ENV_LOG:-} ]]; then\n"
            "  printf 'CALL=%s:%s ECHO_RESOURCE_DIR=%s\\n' "
            '"${1:-}" "${2:-}" "${ECHO_RESOURCE_DIR-<unset>}" '
            '>>"$FAKE_ECHO_ENV_LOG"\n'
            "fi\n"
            "if [[ ${1:-} == --version ]]; then\n"
            f"  echo 'echo-cli fixture rv{render_version} (Release)'\n"
            "elif [[ ${1:-} == narrate && ${2:-} == --help ]]; then\n"
            f"  echo '{help_text}'\n"
            "elif [[ ${1:-} == verify-sidecar ]]; then\n"
            "  if [[ -n ${FAKE_TAMPER_RESUME_STATE_ON_VERIFY:-} ]]; then\n"
            "    tamper_marker=$RUN_ROOT/research/fake-resume-tamper-fired\n"
            "    if [[ ! -e $tamper_marker ]]; then\n"
            "      printf 'changed after state seal' >\"$RUN_ROOT\"/narration-*.sqlite\n"
            '      touch "$tamper_marker"\n'
            "    fi\n"
            "  fi\n"
            "  exit 0\n"
            "elif [[ ${1:-} == narrate ]]; then\n"
            "  shift\n"
            "  if [[ -n ${FAKE_NARRATE_LOG:-} ]]; then\n"
            '    printf \'BEGIN=%s\\n\' "$BASHPID" >>"$FAKE_NARRATE_LOG"\n'
            '    printf \'ARG=%s\\n\' "$@" >>"$FAKE_NARRATE_LOG"\n'
            "  fi\n"
            "  work= db= out= sidecar= epub= voice=\n"
            "  while (( $# )); do\n"
            '    case "$1" in\n'
            "      --work-dir) work=$2; shift 2 ;;\n"
            "      --db) db=$2; shift 2 ;;\n"
            "      --out) out=$2; shift 2 ;;\n"
            "      --sidecar) sidecar=$2; shift 2 ;;\n"
            "      --epub) epub=$2; shift 2 ;;\n"
            "      --voice) voice=$2; shift 2 ;;\n"
            "      --resume) shift ;;\n"
            "      *) shift ;;\n"
            "    esac\n"
            "  done\n"
            '  [[ -z ${FAKE_NARRATE_READY:-} ]] || touch "$FAKE_NARRATE_READY"\n'
            "  if [[ -n ${FAKE_NARRATE_RELEASE:-} ]]; then\n"
            "    while [[ ! -e $FAKE_NARRATE_RELEASE ]]; do sleep 0.05; done\n"
            "  fi\n"
            f'  "{emitter}" "$epub" "$out" "$sidecar" "$work" "$db" "$voice"\n'
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
                "APPROVED_ECHO_PRONUNCIATION_SHA": self.second_sha,
                "EXPLAINER_ROOT": str(self.explainer),
                "SLUG": "fixture",
                "RUN_ROOT": str(self.run_root),
                "VOICE": "am_michael",
                "TITLE": "Fixture Book",
                "ECHO_PRONUNCIATION_LEASE_ROOT": str(self.lease_root),
            }
        )
        environment["PATH"] = f"{self.fake_bin}:{environment['PATH']}"
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
            [
                str(LEASE_HELPER),
                "--lock-root",
                str(self.lease_root),
                "--resource",
                str(self.echo / ".build" / "cli"),
                "--",
                "bash",
                "-c",
                command,
            ],
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

    def preflight_fields(self) -> dict[str, str]:
        names = (
            "ECHO_REPO",
            "EXPLAINER_ROOT",
            "APPROVED_ECHO_PRONUNCIATION_SHA",
            "ECHO_SOURCE_SHA",
            "EPUB",
            "EPUB_SHA256",
            "CLI",
            "ECHO_CLI_SHA256",
            "ECHO_RESOURCE_DIR",
            "ECHO_RESOURCES_SHA256",
            "ECHO_RENDER_VERSION",
            "VOICE",
            "RUN_ID",
            "WORK",
            "DB",
            "ECHO_RENDER_INPUT_RECEIPT",
        )
        body_lines = ["echo_pronunciation_preflight"]
        for name in names:
            body_lines.append(f'printf "{name}=%s\\n" "${{{name}}}"')
        body = "\n".join(body_lines)
        result = self.run_preflight(body=body)
        self.assertEqual(0, result.returncode, result.stderr)
        return dict(
            line.split("=", 1)
            for line in result.stdout.splitlines()
            if line.split("=", 1)[0] in names
        )

    def run_direct_leased(
        self,
        fields: dict[str, str],
        *,
        environment: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        direct_environment = environment or self.environment()
        direct_environment.update(fields)
        dist = self.run_root / "dist"
        output = dist / "fixture.m4b"
        sidecar = dist / "fixture.alignment.json"
        audit = dist / "fixture.pronunciation-audit.json"
        reel = dist / "fixture.pronunciation-reel.m4b"
        direct_environment.update(
            {
                "OUTPUT": str(output),
                "SIDECAR": str(sidecar),
                "AUDIT": str(audit),
                "REEL": str(reel),
                "DIST": str(dist),
                "OWNER_FILE": str(
                    self.run_root / "research" / "echo-render-output.owner.env"
                ),
                "STATE_RECEIPT": str(
                    self.run_root
                    / "research"
                    / f"echo-resume-state-{fields['RUN_ID']}.json"
                ),
                "SUCCESS_RECEIPT": str(
                    self.run_root
                    / "research"
                    / f"echo-render-success-{fields['RUN_ID']}.json"
                ),
                "STAGE": str(self.run_root / ".untrusted-stage"),
            }
        )
        command = [
            str(LEASE_HELPER),
            "--lock-root",
            str(self.lease_root),
        ]
        for resource in (
            self.echo / ".build" / "cli",
            output,
            sidecar,
            audit,
            reel,
            Path(fields["WORK"]),
            Path(fields["DB"]),
        ):
            command.extend(("--resource", str(resource)))
        command.extend(("--", str(NARRATE_WRAPPER), "--leased-run"))
        return subprocess.run(
            command,
            cwd=self.explainer,
            env=direct_environment,
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
        self.assertEqual(self.second_sha, fields["approved_echo_pronunciation_sha"])
        self.assertEqual(self.second_sha, fields["echo_source_sha"])
        self.assertRegex(fields["epub_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(fields["echo_cli_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(fields["echo_resources_sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(str(self.resources.resolve()), fields["echo_resource_dir"])
        self.assertEqual("12", fields["render_version"])

    def test_preflight_accepts_and_binds_newer_release_render_version(self) -> None:
        self.write_cli(include_review_flag=True, render_version=13)

        result = self.run_preflight(
            body=(
                "echo_pronunciation_preflight\n"
                'printf "render_version=%s\\nreceipt=%s\\n" '
                '"$ECHO_RENDER_VERSION" "$ECHO_RENDER_INPUT_RECEIPT"'
            )
        )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("render_version=13", result.stdout)
        receipt_match = re.search(r"receipt=(.+)", result.stdout)
        self.assertIsNotNone(receipt_match)
        receipt = Path(receipt_match.group(1))
        fields = dict(
            line.split("=", 1)
            for line in receipt.read_text(encoding="utf-8").splitlines()
        )
        self.assertEqual("13", fields["render_version"])

    def test_standalone_preflight_rejects_make_without_build_lease(self) -> None:
        command = f"source {shlex.quote(str(PREFLIGHT))}; echo_pronunciation_preflight"
        result = subprocess.run(
            ["bash", "-c", command],
            cwd=self.explainer,
            env=self.environment(),
            capture_output=True,
            text=True,
        )
        self.assertEqual(70, result.returncode)
        self.assertIn("requires the inherited build lease", result.stderr)

    def test_preflight_requires_the_exact_reviewed_echo_source(self) -> None:
        environment = self.environment()
        environment["APPROVED_ECHO_PRONUNCIATION_SHA"] = self.first_sha
        result = self.run_preflight(environment=environment)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("must exactly equal Echo source HEAD", result.stderr)

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
        self.assertIn("must exactly equal Echo source HEAD", result.stderr)

    def test_preflight_rejects_unsafe_slug_and_run_root(self) -> None:
        for slug in ("../escape", "Fixture", "fixture/other"):
            with self.subTest(slug=slug):
                environment = self.environment()
                environment["SLUG"] = slug
                result = self.run_preflight(environment=environment)
                self.assertNotEqual(0, result.returncode)
                self.assertIn("SLUG", result.stderr)

        environment = self.environment()
        environment["RUN_ROOT"] = str(self.tmp / "outside" / "fixture")
        result = self.run_preflight(environment=environment)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("canonical run path", result.stderr)

    def test_internal_modes_reject_a_forged_environment_capability(self) -> None:
        environment = self.environment()
        environment["ECHO_PRONUNCIATION_LEASE_HELD"] = "1"
        result = self.run_narrate("--leased-run", environment=environment)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("inherited FD-backed lease capability", result.stderr)

        environment["ECHO_PRONUNCIATION_LEASE_CAPABILITY"] = json.dumps(
            {str((self.echo / ".build" / "cli").resolve()): 1}
        )
        forged_fd = self.run_narrate("--leased-preflight", environment=environment)
        self.assertNotEqual(0, forged_fd.returncode)
        self.assertIn("inherited FD-backed lease capability", forged_fd.stderr)

    def test_direct_leased_run_rechecks_exact_approval_and_release_version(
        self,
    ) -> None:
        fields = self.preflight_fields()
        receipt = Path(fields["ECHO_RENDER_INPUT_RECEIPT"])
        receipt_text = receipt.read_text(encoding="utf-8")
        fields["APPROVED_ECHO_PRONUNCIATION_SHA"] = self.first_sha
        receipt.write_text(
            receipt_text.replace(self.second_sha, self.first_sha, 1),
            encoding="utf-8",
        )
        unapproved = self.run_direct_leased(fields)
        self.assertNotEqual(0, unapproved.returncode)
        self.assertIn("must exactly equal Echo source HEAD", unapproved.stderr)

        receipt.write_text(receipt_text, encoding="utf-8")
        fields = self.preflight_fields()
        receipt = Path(fields["ECHO_RENDER_INPUT_RECEIPT"])
        self.cli.write_text(
            self.cli.read_text(encoding="utf-8").replace(
                "fixture rv12 (Release)", "fixture rv11 (Release)"
            ),
            encoding="utf-8",
        )
        cli_sha = hashlib.sha256(self.cli.read_bytes()).hexdigest()
        fields["ECHO_CLI_SHA256"] = cli_sha
        receipt.write_text(
            re.sub(
                r"(?m)^echo_cli_sha256=.*$",
                f"echo_cli_sha256={cli_sha}",
                receipt.read_text(encoding="utf-8"),
            ),
            encoding="utf-8",
        )
        stale_cli = self.run_direct_leased(fields)
        self.assertNotEqual(0, stale_cli.returncode)
        self.assertIn("pre-v12", stale_cli.stderr)

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

    def test_preflight_rejects_pre_v12_release_cli(self) -> None:
        cli_text = self.cli.read_text(encoding="utf-8").replace(
            "fixture rv12 (Release)", "fixture rv11 (Release)"
        )
        self.cli.write_text(cli_text, encoding="utf-8")
        result = self.run_preflight()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("pre-v12", result.stderr)

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
        staged_output = next(
            argument
            for index, argument in enumerate(arguments)
            if arguments[index - 1] == "--out"
        )
        staged_sidecar = next(
            argument
            for index, argument in enumerate(arguments)
            if arguments[index - 1] == "--sidecar"
        )
        self.assertRegex(
            staged_output,
            rf"^{re.escape(str(self.run_root))}/\.echo-output-.+/fixture\.m4b$",
        )
        self.assertEqual(
            str(Path(staged_output).parent / "fixture.alignment.json"), staged_sidecar
        )
        self.assertEqual(
            [
                "--epub",
                str(self.run_root / "dist" / "fixture.epub"),
                "--out",
                staged_output,
                "--sidecar",
                staged_sidecar,
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
        self.assertGreaterEqual(len(list(self.lease_root.glob("*.lock"))), 7)
        self.assertFalse(
            (self.run_root / "research" / "echo-render-output.owner.env").exists()
        )

    def test_bounded_partial_render_is_sealed_but_not_published(self) -> None:
        log = self.tmp / "narrate-partial.log"
        environment = self.environment()
        environment.update(
            {
                "FAKE_NARRATE_LOG": str(log),
                "FAKE_NARRATE_EXIT": "2",
            }
        )

        result = self.run_narrate(
            "--max-chapters", "1", environment=environment
        )

        self.assertEqual(2, result.returncode, result.stderr)
        arguments = [
            line.removeprefix("ARG=")
            for line in log.read_text(encoding="utf-8").splitlines()
            if line.startswith("ARG=")
        ]
        self.assertIn("--max-chapters", arguments)
        max_index = arguments.index("--max-chapters")
        self.assertEqual("1", arguments[max_index + 1])
        self.assertEqual(1, len(list(self.run_root.glob("audio-work-*/.anchors-ch0.json"))))
        self.assertEqual(1, len(list(self.run_root.glob("narration-*.sqlite"))))
        self.assertEqual(
            1, len(list((self.run_root / "research").glob("echo-resume-state-*.json")))
        )
        self.assertTrue(
            (self.run_root / "research" / "echo-render-current-attempt.json").is_file()
        )
        self.assertFalse(
            (self.run_root / "research" / "echo-render-current-accepted.json").exists()
        )
        self.assertFalse(list((self.run_root / "dist").glob("echo-renders/**/*")))
        self.assertFalse(list(self.run_root.glob(".echo-output-*")))

    def test_max_chapters_requires_a_positive_integer(self) -> None:
        for arguments in (
            ("--max-chapters",),
            ("--max-chapters", "0"),
            ("--max-chapters", "-1"),
            ("--max-chapters", "one"),
        ):
            with self.subTest(arguments=arguments):
                result = self.run_narrate(*arguments)
                self.assertEqual(64, result.returncode)
                self.assertIn("positive integer", result.stderr)

    def test_success_publishes_run_scoped_media_and_current_selector(self) -> None:
        result = self.run_narrate()
        self.assertEqual(0, result.returncode, result.stderr)

        attempt_path = self.run_root / "research" / "echo-render-current-attempt.json"
        selector_path = self.run_root / "research" / "echo-render-current-accepted.json"
        self.assertTrue(attempt_path.is_file())
        self.assertTrue(selector_path.is_file())
        attempt = json.loads(attempt_path.read_text(encoding="utf-8"))
        selector = json.loads(selector_path.read_text(encoding="utf-8"))
        self.assertEqual(attempt["attemptID"], selector["attemptID"])
        artifact_root = self.run_root / "dist" / selector["artifactRelativePath"]
        self.assertTrue(
            artifact_root.is_relative_to(self.run_root / "dist" / "echo-renders")
        )
        self.assertEqual(selector["runID"], artifact_root.parent.name)
        self.assertEqual(selector["attemptID"], artifact_root.name)
        self.assertTrue((artifact_root / "fixture.m4b").is_file())
        self.assertFalse((self.run_root / "dist" / "fixture.m4b").exists())

    def test_wrapper_replaces_inherited_echo_resource_dir_for_every_cli_call(
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
                f"CALL=--version: ECHO_RESOURCE_DIR={self.resources.resolve()}",
                f"CALL=narrate:--help ECHO_RESOURCE_DIR={self.resources.resolve()}",
                f"CALL=--version: ECHO_RESOURCE_DIR={self.resources.resolve()}",
                f"CALL=narrate:--help ECHO_RESOURCE_DIR={self.resources.resolve()}",
                f"CALL=--version: ECHO_RESOURCE_DIR={self.resources.resolve()}",
                f"CALL=narrate:--help ECHO_RESOURCE_DIR={self.resources.resolve()}",
                f"CALL=narrate:--epub ECHO_RESOURCE_DIR={self.resources.resolve()}",
                f"CALL=--version: ECHO_RESOURCE_DIR={self.resources.resolve()}",
                f"CALL=narrate:--help ECHO_RESOURCE_DIR={self.resources.resolve()}",
                f"CALL=verify-sidecar:--epub ECHO_RESOURCE_DIR={self.resources.resolve()}",
                f"CALL=--version: ECHO_RESOURCE_DIR={self.resources.resolve()}",
                f"CALL=narrate:--help ECHO_RESOURCE_DIR={self.resources.resolve()}",
                f"CALL=verify-sidecar:--epub ECHO_RESOURCE_DIR={self.resources.resolve()}",
                f"CALL=--version: ECHO_RESOURCE_DIR={self.resources.resolve()}",
                f"CALL=narrate:--help ECHO_RESOURCE_DIR={self.resources.resolve()}",
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

    def test_alternate_lock_root_cannot_fork_the_build_lease_namespace(self) -> None:
        log = self.tmp / "alternate-root.log"
        ready = self.tmp / "alternate-root-ready"
        release = self.tmp / "alternate-root-release"
        first_environment = self.environment()
        first_environment.update(
            {
                "ECHO_PRONUNCIATION_LEASE_ROOT": str(self.tmp / "attacker-a"),
                "FAKE_NARRATE_LOG": str(log),
                "FAKE_NARRATE_READY": str(ready),
                "FAKE_NARRATE_RELEASE": str(release),
            }
        )
        first = subprocess.Popen(
            [str(NARRATE_WRAPPER)],
            cwd=self.explainer,
            env=first_environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.addCleanup(lambda: first.poll() is None and first.kill())
        self.wait_for_path(ready, first)

        second_slug = "fixture-two"
        second_run_root = (
            self.explainer / ".build" / "custom-learning-audiobooks" / second_slug
        )
        (second_run_root / "dist").mkdir(parents=True)
        (second_run_root / "dist" / f"{second_slug}.epub").write_bytes(
            b"second fixture epub"
        )
        second_environment = self.environment()
        second_environment.update(
            {
                "ECHO_PRONUNCIATION_LEASE_ROOT": str(self.tmp / "attacker-b"),
                "FAKE_NARRATE_LOG": str(log),
                "SLUG": second_slug,
                "RUN_ROOT": str(second_run_root),
                "TITLE": "Second Fixture Book",
            }
        )
        contender = self.run_narrate(environment=second_environment)

        release.touch()
        first_stdout, first_stderr = first.communicate(timeout=5)
        self.assertEqual(75, contender.returncode, contender.stderr)
        self.assertIn("active narration lease", contender.stderr)
        self.assertEqual(1, log.read_text(encoding="utf-8").count("BEGIN="))
        self.assertEqual(0, first.returncode, f"{first_stdout}\n{first_stderr}")
        self.assertFalse((self.tmp / "attacker-a").exists())
        self.assertFalse((self.tmp / "attacker-b").exists())

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

        def write_owner(
            hostname: str = socket.gethostname(),
            run_id: str = fields["run_id"],
        ) -> None:
            attempt_id = "e" * 64
            artifact_root = (
                self.run_root / "dist" / "echo-renders" / run_id / attempt_id
            )
            owner.write_text(
                "\n".join(
                    (
                        "lock_schema=2",
                        f"owner_token={'a' * 64}",
                        "owner_pid=99999999",
                        f"owner_host={hostname}",
                        "owner_start=Mon Jan  1 00:00:00 2001",
                        f"run_id={run_id}",
                        f"attempt_id={attempt_id}",
                        f"work_dir={self.run_root / f'audio-work-{run_id}'}",
                        f"narration_db={self.run_root / f'narration-{run_id}.sqlite'}",
                        f"output_m4b={artifact_root / 'fixture.m4b'}",
                        f"output_sidecar={artifact_root / 'fixture.alignment.json'}",
                        f"output_audit={artifact_root / 'fixture.pronunciation-audit.json'}",
                        f"output_reel={artifact_root / 'fixture.pronunciation-reel.m4b'}",
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

        old_run_id = f"{'a' * 12}-{'b' * 12}-{'c' * 12}-{'d' * 40}-am_michael"
        write_owner(run_id=old_run_id)
        old_recovered = self.run_narrate("--recover-stale-lock")
        self.assertEqual(0, old_recovered.returncode, old_recovered.stderr)
        self.assertIn("stale narration lock recovered", old_recovered.stdout)
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

    def test_locked_postcheck_rejects_resource_bundle_changed_during_narration(
        self,
    ) -> None:
        ready = self.tmp / "resource-ready"
        release = self.tmp / "resource-release"
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
        (self.resources / "pronunciations.json").write_text(
            '{"renderVersion":13}\n', encoding="utf-8"
        )
        release.touch()
        stdout, stderr = process.communicate(timeout=5)
        self.assertEqual(65, process.returncode, f"{stdout}\n{stderr}")
        self.assertIn("Echo resources changed while narration lease was held", stderr)

    def test_resume_requires_hash_bound_current_render_version_capture_state(self) -> None:
        initial = self.run_narrate()
        self.assertEqual(0, initial.returncode, initial.stderr)
        marker = next(self.run_root.glob("audio-work-*/.anchors-ch0.json"))
        marker_payload = json.loads(marker.read_text(encoding="utf-8"))
        marker_payload["identity"]["renderVersion"] = True
        marker.write_text(json.dumps(marker_payload), encoding="utf-8")

        resumed = self.run_narrate("--resume")
        self.assertNotEqual(0, resumed.returncode)
        self.assertIn("resume state", resumed.stderr)

    def test_resume_rejects_capture_from_a_different_release_render_version(
        self,
    ) -> None:
        self.write_cli(include_review_flag=True, render_version=13)
        initial = self.run_narrate()
        self.assertEqual(0, initial.returncode, initial.stderr)
        marker = next(self.run_root.glob("audio-work-*/.anchors-ch0.json"))
        marker_payload = json.loads(marker.read_text(encoding="utf-8"))
        self.assertEqual(13, marker_payload["identity"]["renderVersion"])
        marker_payload["identity"]["renderVersion"] = 12
        marker.write_text(json.dumps(marker_payload), encoding="utf-8")

        resumed = self.run_narrate("--resume")

        self.assertNotEqual(0, resumed.returncode)
        self.assertIn("render version 13", resumed.stderr)

    def test_resume_rejects_database_mutation(self) -> None:
        initial = self.run_narrate()
        self.assertEqual(0, initial.returncode, initial.stderr)
        database = next(self.run_root.glob("narration-*.sqlite"))
        database.write_bytes(b"substituted database")
        changed_database = self.run_narrate("--resume")
        self.assertNotEqual(0, changed_database.returncode)
        self.assertIn("resume state", changed_database.stderr)

    def test_resume_rejects_identity_free_legacy_capture(self) -> None:
        initial = self.run_narrate()
        self.assertEqual(0, initial.returncode, initial.stderr)
        marker = next(self.run_root.glob("audio-work-*/.anchors-ch0.json"))
        payload = json.loads(marker.read_text(encoding="utf-8"))
        payload["identity"] = None
        marker.write_text(json.dumps(payload), encoding="utf-8")
        resumed = self.run_narrate("--resume")
        self.assertNotEqual(0, resumed.returncode)
        self.assertIn("sealed Echo identity", resumed.stderr)

    def test_success_rechecks_live_resume_state_after_the_final_seal(self) -> None:
        environment = self.environment()
        environment["FAKE_TAMPER_RESUME_STATE_ON_VERIFY"] = "1"

        result = self.run_narrate(environment=environment)

        self.assertEqual(65, result.returncode, result.stderr)
        self.assertIn("resume state receipt does not match", result.stderr)
        self.assertFalse(
            list((self.run_root / "research").glob("echo-render-success-*.json"))
        )
        self.assertFalse(
            (self.run_root / "research" / "echo-render-current-accepted.json").exists()
        )

    def test_success_exit_without_complete_outputs_is_not_published(self) -> None:
        environment = self.environment()
        environment["FAKE_SKIP_AUDIT"] = "1"
        result = self.run_narrate(environment=environment)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("did not produce required output", result.stderr)
        self.assertFalse((self.run_root / "dist" / "fixture.m4b").exists())
        self.assertFalse(
            list((self.run_root / "research").glob("echo-render-success-*.json"))
        )

    def test_output_symlink_is_rejected_without_clobbering_its_target(self) -> None:
        target = self.tmp / "outside-output"
        target.mkdir()
        marker = target / "marker"
        marker.write_bytes(b"do not replace")
        output_root = self.run_root / "dist" / "echo-renders"
        output_root.symlink_to(target, target_is_directory=True)
        result = self.run_narrate()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("governed artifact directory is unsafe", result.stderr)
        self.assertEqual(b"do not replace", marker.read_bytes())
        self.assertTrue(output_root.is_symlink())

    def test_success_receipt_binds_final_media_and_audit(self) -> None:
        result = self.run_narrate()
        self.assertEqual(0, result.returncode, result.stderr)
        receipts = list((self.run_root / "research").glob("echo-render-success-*.json"))
        self.assertEqual(1, len(receipts))
        receipt = json.loads(receipts[0].read_text(encoding="utf-8"))
        self.assertEqual(2, receipt["schemaVersion"])
        state_receipt = next(
            (self.run_root / "research").glob("echo-resume-state-*.json")
        )
        self.assertIn("resumeStateFileName", receipt)
        self.assertEqual(state_receipt.name, receipt["resumeStateFileName"])
        self.assertEqual(
            hashlib.sha256(state_receipt.read_bytes()).hexdigest(),
            receipt["resumeStateSHA256"],
        )
        for field in ("audiobookSHA256", "sidecarSHA256", "auditSHA256"):
            self.assertRegex(receipt[field], r"^[0-9a-f]{64}$")

        input_receipt = next(
            (self.run_root / "research").glob("echo-render-inputs-*.env")
        )
        input_fields = dict(
            line.split("=", 1)
            for line in input_receipt.read_text(encoding="utf-8").splitlines()
        )
        unleased_record = subprocess.run(
            [
                "/usr/local/bin/python3",
                str(STATE_HELPER),
                "record-state",
                "--work",
                input_fields["work_dir"],
                "--db",
                input_fields["narration_db"],
                "--receipt",
                str(self.run_root / "research" / "forged-resume-state.json"),
                "--epub",
                str(self.run_root / "dist" / "fixture.epub"),
                "--source-sha",
                self.second_sha,
                "--voice",
                "am_michael",
                "--render-version",
                input_fields["render_version"],
                "--input-receipt",
                str(input_receipt),
                "--lock-root",
                str(self.lease_root),
            ],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(0, unleased_record.returncode)
        self.assertIn(
            "missing inherited FD-backed lease capability", unleased_record.stderr
        )

        attempt = self.run_root / "research" / "echo-render-current-attempt.json"
        selector = self.run_root / "research" / "echo-render-current-accepted.json"
        selector_payload = json.loads(selector.read_text(encoding="utf-8"))
        artifact_root = (
            self.run_root / "dist" / selector_payload["artifactRelativePath"]
        )
        selection_resource = self.run_root / "research" / "echo-render-selection"
        forged_success = self.run_root / "research" / "forged-success.json"
        partially_leased_command = [
            str(LEASE_HELPER),
            "--lock-root",
            str(self.lease_root),
        ]
        for resource in (
            artifact_root / "fixture.m4b",
            artifact_root / "fixture.alignment.json",
            artifact_root / "fixture.pronunciation-audit.json",
            artifact_root / "fixture.pronunciation-reel.m4b",
            selection_resource,
        ):
            partially_leased_command.extend(("--resource", str(resource)))
        partially_leased_command.extend(
            (
                "--",
                "/usr/local/bin/python3",
                str(STATE_HELPER),
                "write-success",
                "--attempt-id",
                selector_payload["attemptID"],
                "--run-id",
                selector_payload["runID"],
                "--receipt",
                str(forged_success),
                "--attempt-receipt",
                str(attempt),
                "--input-receipt",
                str(input_receipt),
                "--epub",
                str(self.run_root / "dist" / "fixture.epub"),
                "--artifact-relative-path",
                selector_payload["artifactRelativePath"],
                "--state-receipt",
                str(state_receipt),
                "--work",
                input_fields["work_dir"],
                "--db",
                input_fields["narration_db"],
                "--source-sha",
                self.second_sha,
                "--voice",
                "am_michael",
                "--render-version",
                input_fields["render_version"],
                "--audiobook",
                str(artifact_root / "fixture.m4b"),
                "--sidecar",
                str(artifact_root / "fixture.alignment.json"),
                "--audit",
                str(artifact_root / "fixture.pronunciation-audit.json"),
                "--reel",
                str(artifact_root / "fixture.pronunciation-reel.m4b"),
                "--selection-resource",
                str(selection_resource),
                "--lock-root",
                str(self.lease_root),
            )
        )
        partially_leased = subprocess.run(
            partially_leased_command, capture_output=True, text=True
        )
        self.assertNotEqual(0, partially_leased.returncode)
        self.assertIn("does not cover", partially_leased.stderr)
        self.assertTrue(
            input_fields["work_dir"] in partially_leased.stderr
            or input_fields["narration_db"] in partially_leased.stderr
        )
        self.assertFalse(forged_success.exists())

        command = [
            "/usr/local/bin/python3",
            str(STATE_HELPER),
            "verify-delivery",
            "--attempt",
            str(attempt),
            "--selector",
            str(selector),
            "--receipt",
            str(receipts[0]),
            "--input-receipt",
            str(input_receipt),
            "--state-receipt",
            str(state_receipt),
            "--epub",
            str(self.run_root / "dist" / "fixture.epub"),
            "--audiobook",
            str(artifact_root / "fixture.m4b"),
            "--sidecar",
            str(artifact_root / "fixture.alignment.json"),
            "--audit",
            str(artifact_root / "fixture.pronunciation-audit.json"),
            "--reel",
            str(artifact_root / "fixture.pronunciation-reel.m4b"),
        ]
        verified = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(0, verified.returncode, verified.stderr)

        original_state = state_receipt.read_bytes()
        state_receipt.write_bytes(b"X" * len(original_state))
        tampered_state = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(0, tampered_state.returncode)
        self.assertIn("resume-state receipt SHA-256 differs", tampered_state.stderr)
        state_receipt.unlink()
        missing_state = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(0, missing_state.returncode)
        self.assertIn("resume-state receipt is missing", missing_state.stderr)
        saved_state = self.tmp / state_receipt.name
        saved_state.write_bytes(original_state)
        state_receipt.symlink_to(saved_state)
        symlinked_state = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(0, symlinked_state.returncode)
        self.assertIn(
            "resume-state receipt must not be a symlink", symlinked_state.stderr
        )
        state_receipt.unlink()
        state_receipt.write_bytes(original_state)

        (artifact_root / "fixture.alignment.json").write_text(
            '{"tampered":true}\n', encoding="utf-8"
        )
        tampered = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(0, tampered.returncode)
        self.assertIn("SHA-256 differs", tampered.stderr)

    def test_failed_newer_source_attempt_invalidates_old_delivery_acceptance(
        self,
    ) -> None:
        initial = self.run_narrate()
        self.assertEqual(0, initial.returncode, initial.stderr)
        research = self.run_root / "research"
        attempt_path = research / "echo-render-current-attempt.json"
        selector_path = research / "echo-render-current-accepted.json"
        first_attempt = json.loads(attempt_path.read_text(encoding="utf-8"))
        first_selector = json.loads(selector_path.read_text(encoding="utf-8"))
        first_artifacts = (
            self.run_root / "dist" / first_selector["artifactRelativePath"]
        )
        first_success = research / first_selector["successReceiptFileName"]

        epub = self.run_root / "dist" / "fixture.epub"
        epub.write_bytes(b"newer source epub")
        failed_environment = self.environment()
        failed_environment["FAKE_NARRATE_EXIT"] = "42"
        failed = self.run_narrate(environment=failed_environment)
        self.assertEqual(42, failed.returncode, failed.stderr)

        newest_attempt = json.loads(attempt_path.read_text(encoding="utf-8"))
        self.assertNotEqual(first_attempt["attemptID"], newest_attempt["attemptID"])
        self.assertTrue((first_artifacts / "fixture.m4b").is_file())
        verify = subprocess.run(
            [
                "/usr/local/bin/python3",
                str(STATE_HELPER),
                "verify-delivery",
                "--attempt",
                str(attempt_path),
                "--selector",
                str(selector_path),
                "--receipt",
                str(first_success),
                "--input-receipt",
                str(research / first_selector["inputReceiptFileName"]),
                "--state-receipt",
                str(research / f"echo-resume-state-{first_selector['runID']}.json"),
                "--epub",
                str(epub),
                "--audiobook",
                str(first_artifacts / "fixture.m4b"),
                "--sidecar",
                str(first_artifacts / "fixture.alignment.json"),
                "--audit",
                str(first_artifacts / "fixture.pronunciation-audit.json"),
                "--reel",
                str(first_artifacts / "fixture.pronunciation-reel.m4b"),
            ],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(0, verify.returncode)
        self.assertIn("current attempt", verify.stderr)

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
            self.echo / ".build" / "cli",
            Path(arguments[arguments.index("--work-dir") + 1]),
            Path(arguments[arguments.index("--db") + 1]),
        )
        selector = json.loads(
            (
                self.run_root / "research" / "echo-render-current-accepted.json"
            ).read_text(encoding="utf-8")
        )
        artifact_root = self.run_root / "dist" / selector["artifactRelativePath"]
        resources += (
            artifact_root / "fixture.m4b",
            artifact_root / "fixture.alignment.json",
            artifact_root / "fixture.pronunciation-audit.json",
            artifact_root / "fixture.pronunciation-reel.m4b",
            self.run_root / "research" / "echo-render-selection",
        )
        expected = {
            hashlib.sha256(str(path.resolve()).encode("utf-8")).hexdigest() + ".lock"
            for path in resources
        }
        observed = {path.name for path in self.lease_root.glob("*.lock")}
        self.assertTrue(expected.issubset(observed))

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
        self.fake_bin = self.tmp / "bin"
        self.fake_bin.mkdir()
        ffprobe = self.fake_bin / "ffprobe"
        ffprobe.write_text(
            '#!/usr/bin/env bash\nprintf \'%s\\n\' \'{"format":{"duration":"5.0"}}\'\n',
            encoding="utf-8",
        )
        ffprobe.chmod(ffprobe.stat().st_mode | stat.S_IXUSR)
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
        environment = os.environ.copy()
        environment["PATH"] = f"{self.fake_bin}:{environment['PATH']}"
        return subprocess.run(
            ["/usr/local/bin/python3", str(AUDIT_VALIDATOR), str(self.audit)],
            env=environment,
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
        reel = self.tmp / "fixture.pronunciation-reel.m4b"
        reel.write_bytes(b"fixture reel")
        self.payload["listeningReelFileName"] = reel.name
        self.payload["listeningReelSHA256"] = hashlib.sha256(
            reel.read_bytes()
        ).hexdigest()
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

    def test_rejects_disallowed_voice_or_pre_v12_render(self) -> None:
        for field, value, message in (
            ("voice", "af_heart", "voice must be am_michael or am_puck"),
            ("renderVersion", 11, "renderVersion must be at least 12"),
        ):
            with self.subTest(field=field):
                original = self.payload[field]
                self.payload[field] = value
                result = self.run_validator()
                self.assertNotEqual(0, result.returncode)
                self.assertIn(message, result.stderr)
                self.payload[field] = original

    def test_timed_decisions_require_a_reel_and_in_media_ranges(self) -> None:
        self.payload["decisions"] = [self.valid_decision()]
        self.payload["watchCounts"]["filesystem"] = 1
        missing_reel = self.run_validator()
        self.assertNotEqual(0, missing_reel.returncode)
        self.assertIn(
            "timed pronunciation decisions require a listening reel",
            missing_reel.stderr,
        )

        reel = self.tmp / "fixture.pronunciation-reel.m4b"
        reel.write_bytes(b"fixture reel")
        self.payload["listeningReelFileName"] = reel.name
        self.payload["listeningReelSHA256"] = hashlib.sha256(
            reel.read_bytes()
        ).hexdigest()
        self.payload["decisions"][0]["bookRelativeAudioRange"] = {
            "start": 4.5,
            "end": 9999.0,
        }
        outside = self.run_validator()
        self.assertNotEqual(0, outside.returncode)
        self.assertIn("exceeds audiobook duration", outside.stderr)

    def test_rejects_decision_word_missing_from_watch_counts(self) -> None:
        decision = self.valid_decision()
        decision["normalizedWord"] = "not-watched"
        self.payload["decisions"] = [decision]
        result = self.run_validator()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("is absent from watchCounts", result.stderr)

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
        self.assertIn(
            "timed pronunciation decisions require a listening reel", unlisted.stderr
        )

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
