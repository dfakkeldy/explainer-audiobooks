from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "skill" / "scripts" / "prose_qc.py"

# prose_qc.py has no PIL dependency (unlike build_book.py, which pulls it in
# transitively via cover_receipts -> refresh_epub_cover), so it can be
# imported directly here even in environments where Pillow is not
# installed. Do NOT import build_book from this module.
sys.path.insert(0, str(SCRIPT.parent))
import prose_qc  # noqa: E402


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


class ProseQcMetricsCallPathParityTests(unittest.TestCase):
    """Pin: every call path to `report()` must agree on shape metrics.

    Before this fix, report()'s no-`metrics` fallback recomputed shape
    metrics from the >=20-word-filtered `paragraphs` list, while the CLI
    (main()) always precomputed metrics from the unfiltered paragraph
    population and passed them in -- two call paths, two different answers
    for the same chapter set. `_write_chapters`'s fixture is deliberately
    built so this matters: its coordinate list lives in a 12-word paragraph,
    which the >=20-word filter drops. Under the old bug the direct-call path
    would report `coordinate_lists.count == 0`; the CLI path would report
    `1`. This test locks both paths to the same answer.
    """

    def test_cli_and_direct_report_call_agree_on_coordinate_lists(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            chapters = _write_chapters(root / "chapters")

            # Path A: the CLI (main()), which precomputes metrics from the
            # unfiltered population and threads it into report().
            cli_out = root / "cli-report.md"
            subprocess.run(
                [sys.executable, str(SCRIPT), "--chapters-dir", str(chapters), "--out", str(cli_out)],
                check=True, cwd=REPO,
            )
            cli_match = re.search(r"coordinate_lists: (\d+)", cli_out.read_text(encoding="utf-8"))
            self.assertIsNotNone(cli_match, "CLI report is missing the coordinate_lists line")
            cli_count = int(cli_match.group(1))

            # Path B: call report() directly with no precomputed `metrics`,
            # exercising its internal fallback -- it must land on the same
            # unfiltered population the CLI used, not the filtered one.
            source_files = list(prose_qc.chapters(chapters))
            paragraphs = [p for path in source_files for p in prose_qc.extract_paragraphs(path)]
            paragraph_texts = [t for path in source_files for t in prose_qc.extract_paragraph_texts(path)]
            direct_text = prose_qc.report(paragraphs, 6, 0.68, 20, paragraph_texts)
            direct_match = re.search(r"coordinate_lists: (\d+)", direct_text)
            self.assertIsNotNone(direct_match, "direct report() call is missing the coordinate_lists line")
            direct_count = int(direct_match.group(1))

            self.assertEqual(1, cli_count, "fixture is expected to contain exactly one coordinate list")
            self.assertEqual(cli_count, direct_count)


class ProseQcReceiptBackwardCompatibilityTests(unittest.TestCase):
    """A receipt written before the `metrics` key existed must still verify.

    build_book.py's --prose-receipt gate calls verify_style_receipt() before
    writing EPUB/Markdown output, so this is the highest-risk invariant in
    the metrics change: old receipts must not suddenly fail verification.
    This module only imports prose_qc (see the module-level comment above),
    never build_book, so it runs in this Pillow-less environment even
    though tests/test_prose_style_gate.py -- which would otherwise be the
    natural home for a receipt round-trip test -- cannot.
    """

    def test_receipt_with_no_metrics_key_still_verifies(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            chapters = _write_chapters(root / "chapters")

            # verify_style_receipt only inspects schema_version, status, and
            # chapter_sha256 (read from prose_qc.py directly to confirm).
            # This is exactly the receipt shape write_style_receipt produced
            # before the `metrics` key was added: no "metrics" entry at all.
            chapter_sha256 = {
                path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(chapters.glob("ch*.md"))
            }
            pre_metrics_receipt = {
                "schema_version": 1,
                "status": "pass",
                "chapter_sha256": chapter_sha256,
            }
            self.assertNotIn("metrics", pre_metrics_receipt)

            receipt_path = root / "receipt.json"
            receipt_path.write_text(
                json.dumps(pre_metrics_receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )

            verified = prose_qc.verify_style_receipt(chapters, receipt_path)

            self.assertEqual("pass", verified["status"])
            self.assertNotIn("metrics", verified)


if __name__ == "__main__":
    unittest.main()
