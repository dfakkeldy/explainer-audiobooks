from __future__ import annotations

import io
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

REPO = Path(__file__).parents[1]
sys.path.insert(0, str(REPO / "skill" / "scripts"))
import build_book


class LeanBuildTests(unittest.TestCase):
    def _chapters(self, root: Path) -> Path:
        chapters = root / "chapters"
        chapters.mkdir()
        (chapters / "ch01.md").write_text(
            "# One\n\nThese four words are narrated.\n", encoding="utf-8"
        )
        return chapters

    def test_build_succeeds_with_no_receipt_arguments(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            chapters = self._chapters(root)
            out = root / "dist"

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                build_book.build(chapters, out, "Fixture", "Dan Fakkeldy", "", "fixture-book")

            self.assertIn("Chapters: 1", stdout.getvalue())
            self.assertTrue((out / "fixture-book.epub").is_file())
            self.assertTrue((out / "fixture-book.md").is_file())

    def test_cli_builds_without_any_receipt_flag(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            chapters = self._chapters(root)
            out = root / "dist"

            result = subprocess.run(
                [
                    "/usr/local/bin/python3",
                    str(REPO / "skill" / "scripts" / "build_book.py"),
                    "--chapters-dir", str(chapters),
                    "--out-dir", str(out),
                    "--title", "Fixture",
                    "--author", "Dan Fakkeldy",
                    "--slug", "fixture-book",
                ],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((out / "fixture-book.epub").is_file())

    def test_retired_gate_flags_are_gone(self) -> None:
        result = subprocess.run(
            ["/usr/local/bin/python3", str(REPO / "skill" / "scripts" / "build_book.py"), "--help"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("--learning-receipt", result.stdout)
        self.assertNotIn("--legacy-without-learning-receipt", result.stdout)
        self.assertNotIn("--learning-pilot", result.stdout)
        self.assertIn("--fiction-receipt", result.stdout)


if __name__ == "__main__":
    unittest.main()
