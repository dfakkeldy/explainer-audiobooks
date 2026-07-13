from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
SKILL = ROOT / "skills" / "custom-learning-audiobook" / "SKILL.md"
PACKAGE = (
    ROOT
    / "skills"
    / "custom-learning-audiobook"
    / "references"
    / "package-and-qc.md"
)


class CustomLearningAudiobookEchoContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.skill = SKILL.read_text(encoding="utf-8")
        self.package = PACKAGE.read_text(encoding="utf-8")

    @staticmethod
    def normalized(text: str) -> str:
        return " ".join(text.split())

    def test_builds_and_preflights_the_exact_release_cli(self) -> None:
        for marker in (
            "cd /Users/dfakkeldy/Developer/Echo",
            '"$HOME/.claude/bin/xcode-build-gate.sh" --wait && make echo-cli',
            'CLI="/Users/dfakkeldy/Developer/Echo/.build/cli/Build/Products/Release/echo-cli"',
            '"$CLI" --version',
            "(Release)",
            '"$CLI" narrate --help',
            "--no-pronunciation-review",
            "Stop immediately",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.package)

        for stale_debug_discovery in ("xcodebuild build", "TARGET_BUILD_DIR"):
            with self.subTest(stale=stale_debug_discovery):
                self.assertNotIn(stale_debug_discovery, self.package)

    def test_pronunciation_review_defaults_on_with_bounded_render_concurrency(self) -> None:
        for text in (self.skill, self.package):
            with self.subTest(document="skill" if text == self.skill else "package"):
                normalized = self.normalized(text)
                self.assertIn("Pronunciation review is on by default", normalized)
                self.assertIn("Do not pass `--no-pronunciation-review`", normalized)

        self.assertIn("--jobs 1", self.package)
        self.assertIn("--threads 2", self.package)

    def test_resume_requires_an_immutable_source_renderer_and_capture_set(self) -> None:
        normalized = self.normalized(self.package)
        for marker in (
            "fresh `--work-dir` and `--db`",
            "source EPUB changes",
            "Release CLI binary changes",
            "same immutable source EPUB, Release CLI binary, and capture set",
            "SHA-256",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, normalized)

    def test_review_artifacts_are_automatic_and_part_of_package_qc(self) -> None:
        normalized = self.normalized(self.package)
        for marker in (
            "<slug>.pronunciation-audit.json",
            "<slug>.pronunciation-reel.m4b",
            '"$CLI" verify-sidecar',
            '--epub "$DIST/$SLUG.epub"',
            '--audio "$DIST/$SLUG.m4b"',
            '--sidecar "$DIST/$SLUG.alignment.json"',
            "schema version is `1`",
            "coverage",
            "watch counts",
            "including zero counts",
            "human listening remains explicitly pending",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, normalized)

        for marker in (
            "pronunciation audit",
            "pronunciation reel",
            "human listening",
        ):
            with self.subTest(report_marker=marker):
                self.assertIn(marker, self.skill.casefold())


if __name__ == "__main__":
    unittest.main()
