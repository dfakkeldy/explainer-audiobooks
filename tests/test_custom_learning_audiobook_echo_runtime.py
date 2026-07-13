from __future__ import annotations

import copy
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
            "set -euo pipefail\n" f"source {shlex.quote(str(PREFLIGHT))}\n" f"{body}\n"
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
                "filesystem": 0,
                "verified": 0,
                "live": 0,
                "lives": 0,
                "record": 0,
            },
            "decisions": [],
            "diagnostics": [],
            "legacyChapterIndexes": [],
            "audiobookFileName": "fixture.m4b",
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

    def test_accepts_complete_schema_v1_fixture_with_zero_watch_counts(self) -> None:
        result = self.run_validator()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("pronunciation_audit: clean", result.stdout)

    def test_rejects_non_v1_manifest(self) -> None:
        self.payload["schemaVersion"] = 2
        result = self.run_validator()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("schemaVersion must be 1", result.stderr)

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

    def test_reel_filename_and_file_presence_must_agree(self) -> None:
        reel_name = "fixture.pronunciation-reel.m4b"
        self.payload["listeningReelFileName"] = reel_name
        missing = self.run_validator()
        self.assertNotEqual(0, missing.returncode)

        (self.tmp / reel_name).write_bytes(b"fixture reel")
        present = self.run_validator()
        self.assertEqual(0, present.returncode, present.stderr)

        self.payload.pop("listeningReelFileName")
        unlisted = self.run_validator()
        self.assertNotEqual(0, unlisted.returncode)
        self.assertIn("unlisted listening reel", unlisted.stderr)


if __name__ == "__main__":
    unittest.main()
