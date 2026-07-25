from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "skill" / "scripts" / "prose_qc.py"


def _write_chapters(chapters_dir: Path) -> Path:
    chapters_dir.mkdir()
    (chapters_dir / "ch01.md").write_text(
        "## Chapter 1 - Test\n\n"
        "A clerk signed the form. She waited.\n\n"
        "The treasurer registered it, filed it, stamped it, indexed it, and left.\n",
        encoding="utf-8",
    )
    return chapters_dir


class ProseQcMetricsReportTests(unittest.TestCase):
    def test_report_contains_metrics_section(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            chapters = _write_chapters(root / "chapters")
            out = root / "report.md"
            subprocess.run(
                [sys.executable, str(SCRIPT), "--chapters-dir", str(chapters), "--out", str(out)],
                check=True, cwd=REPO,
            )
            text = out.read_text(encoding="utf-8")
            self.assertIn("Shape metrics", text)
            self.assertIn("sentence_cv", text)


class ProseQcMetricsReceiptTests(unittest.TestCase):
    def test_receipt_contains_metrics_block(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            chapters = _write_chapters(root / "chapters")
            out = root / "report.md"
            decisions = root / "decisions.json"
            receipt = root / "receipt.json"
            decisions.write_text(json.dumps({
                "reviewer": "test", "model": "test", "skill_version": "test",
                "humanizer_applied": True, "accepted": [], "rejected": [],
                "checks_rerun": ["factual", "coverage-ledger", "narration", "prose"],
            }), encoding="utf-8")
            subprocess.run(
                [sys.executable, str(SCRIPT), "--chapters-dir", str(chapters),
                 "--out", str(out), "--decisions", str(decisions),
                 "--style-receipt-out", str(receipt)],
                check=True, cwd=REPO,
            )
            data = json.loads(receipt.read_text(encoding="utf-8"))
            self.assertIn("metrics", data)
            self.assertIn("rhythm", data["metrics"])
            self.assertEqual(data["metrics"]["coordinate_lists"]["count"], 1)


class ProseQcMetricsAdvisoryTests(unittest.TestCase):
    def test_metrics_never_fail_the_run(self) -> None:
        """Measures are advisory in this task; --fail-on-style must ignore them."""
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            chapters = root / "chapters"
            chapters.mkdir()
            (chapters / "ch01.md").write_text(
                "## Chapter 1\n\n" + ("Alpha, beta, gamma, delta, and epsilon follow. " * 10),
                encoding="utf-8",
            )
            out = root / "report.md"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--chapters-dir", str(chapters),
                 "--out", str(out), "--fail-on-style"],
                cwd=REPO,
            )
            self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
