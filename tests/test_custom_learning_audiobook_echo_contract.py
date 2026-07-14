from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
SKILL = ROOT / "skills" / "custom-learning-audiobook" / "SKILL.md"
PACKAGE = (
    ROOT / "skills" / "custom-learning-audiobook" / "references" / "package-and-qc.md"
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


class CustomLearningAudiobookEchoContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.skill = SKILL.read_text(encoding="utf-8")
        self.package = PACKAGE.read_text(encoding="utf-8")
        self.narrate_wrapper = NARRATE_WRAPPER.read_text(encoding="utf-8")
        self.lease_helper = LEASE_HELPER.read_text(encoding="utf-8")

    @staticmethod
    def normalized(text: str) -> str:
        return " ".join(text.split())

    def test_builds_and_preflights_the_exact_release_cli(self) -> None:
        for marker in (
            "APPROVED_ECHO_PRONUNCIATION_SHA",
            "approved source revision",
            "ECHO_SOURCE_SHA",
            "ECHO_CLI_SHA256",
            "EPUB_SHA256",
            "RUN_ROOT",
            "--no-pronunciation-review",
            "Stop immediately",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.normalized(self.package))

        self.assertIn("echo_pronunciation_preflight.sh", self.narrate_wrapper)
        self.assertIn('"$CLI" narrate', self.narrate_wrapper)
        self.assertIn('ECHO_RESOURCE_DIR="$ECHO_RESOURCE_DIR"', self.narrate_wrapper)
        self.assertNotIn('"$CLI" narrate', self.package)
        self.assertIn("Never invoke a DerivedData `Debug/echo-cli`", self.package)
        self.assertIn("Do not bypass the governed narration wrapper", self.skill)

        for stale_debug_discovery in ("xcodebuild build", "TARGET_BUILD_DIR"):
            with self.subTest(stale=stale_debug_discovery):
                self.assertNotIn(stale_debug_discovery, self.package)

        self.assertNotIn("cd /Users/dfakkeldy/Developer/Echo", self.package)

    def test_pronunciation_review_defaults_on_with_bounded_render_concurrency(
        self,
    ) -> None:
        for text in (self.skill, self.package):
            with self.subTest(document="skill" if text == self.skill else "package"):
                normalized = self.normalized(text)
                self.assertIn("Pronunciation review is on by default", normalized)
                self.assertIn("Do not pass `--no-pronunciation-review`", normalized)

        self.assertIn("--jobs 1", self.narrate_wrapper)
        self.assertIn("--threads 2", self.narrate_wrapper)

    def test_wrapper_holds_fd_backed_resource_leases_through_narration(self) -> None:
        for marker in (
            "ECHO_PRONUNCIATION_LEASE_ROOT",
            "echo_pronunciation_canonical_lease_root",
            "echo_pronunciation_lease.py",
            "trap release_owner_metadata EXIT",
            "--recover-stale-lock",
            "active narration lock",
            "remote narration lock",
            "malformed narration lock",
            'wait "$NARRATE_PID"',
            "--leased-preflight",
            "--assert-held",
            "BUILD_RESOURCE",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.narrate_wrapper)

        for marker in (
            "fcntl.flock",
            "fcntl.LOCK_EX | fcntl.LOCK_NB",
            "pass_fds=tuple(sorted(set(capability.values())))",
            "hashlib.sha256",
            "Path(resource).resolve()",
            "ECHO_PRONUNCIATION_LEASE_CAPABILITY",
            "validate_capability",
        ):
            self.assertIn(marker, self.lease_helper)

        for marker in (
            "governed Echo narration wrapper",
            "do not bypass the wrapper with a direct CLI command",
        ):
            self.assertIn(marker, self.skill)

    def test_resume_requires_an_immutable_source_renderer_and_capture_set(self) -> None:
        normalized = self.normalized(self.package)
        for marker in (
            "fresh `--work-dir` and `--db`",
            "source EPUB changes",
            "Release CLI binary or Echo source revision changes",
            "exact approved/source revision",
            "exact Release render version",
            "echo-resume-state-$RUN_ID.json",
            "SHA-256",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, normalized)

    def test_governed_partial_probe_is_resumable_but_not_publishable(self) -> None:
        normalized_skill = self.normalized(self.skill)
        normalized_package = self.normalized(self.package)

        for marker in (
            "--max-chapters 1",
            "exit 2",
            "partial",
            "--resume --max-chapters 1",
            "no accepted M4B",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, normalized_package)

        self.assertIn("real-book pronunciation probe", normalized_skill)
        self.assertIn("--max-chapters", self.narrate_wrapper)

    def test_review_artifacts_are_automatic_and_part_of_package_qc(self) -> None:
        normalized = self.normalized(self.package)
        for marker in (
            "<slug>.pronunciation-audit.json",
            "<slug>.pronunciation-reel.m4b",
            '"$CLI" verify-sidecar',
            '--epub "$DIST/$SLUG.epub"',
            '--audio "$AUDIOBOOK"',
            '--sidecar "$SIDECAR"',
            "schema version is `2`",
            "coverage",
            "watch counts",
            "including zero counts",
            "human listening remains explicitly pending",
            "validate_pronunciation_audit.py",
            "echo-render-success-$RUN_ID-$ATTEMPT_ID.json",
            "echo-render-current-attempt.json",
            "echo-render-current-accepted.json",
            "echo-renders/$RUN_ID/$ATTEMPT_ID",
            "verify-delivery",
            "--state-receipt",
            "resumeStateFileName",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, normalized)

        self.assertNotIn('mv "$DIST/$SLUG.covered.m4b"', self.skill)
        self.assertNotIn('mv "$DIST/$SLUG.covered.m4b"', self.package)
        self.assertIn('cp "$STATE_RECEIPT"', self.package)
        self.assertGreaterEqual(self.package.count("--state-receipt"), 2)

        for marker in (
            "pronunciation audit",
            "pronunciation reel",
            "human listening",
        ):
            with self.subTest(report_marker=marker):
                self.assertIn(marker, self.skill.casefold())


if __name__ == "__main__":
    unittest.main()
