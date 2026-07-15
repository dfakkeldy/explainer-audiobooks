from __future__ import annotations

import inspect
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parents[1] / "skill" / "scripts"))
import build_book
import prose_qc


class ProseStyleGateContractTests(unittest.TestCase):
    def test_prose_qc_exposes_family_analysis_and_receipt_verification(self) -> None:
        self.assertTrue(callable(getattr(prose_qc, "analyse_style", None)))
        self.assertTrue(callable(getattr(prose_qc, "write_style_receipt", None)))
        self.assertTrue(callable(getattr(prose_qc, "verify_style_receipt", None)))

    def test_book_builder_accepts_a_prose_receipt_gate(self) -> None:
        parameters = inspect.signature(build_book.build).parameters
        self.assertIn("prose_receipt", parameters)


class ProseStyleAnalysisTests(unittest.TestCase):
    def paragraph(self, text: str) -> prose_qc.Paragraph:
        return prose_qc.Paragraph("ch01.md", 1, text, prose_qc.words(text))

    def test_groups_synonym_cycled_reader_management_and_hard_bans(self) -> None:
        text = (
            "Hold on to this. Sit with that for a moment. Carry that thought forward. "
            "Notice what happened next. The rest of this paragraph contains enough ordinary "
            "words to represent spoken audiobook prose without adding another rhetorical cue."
        )
        analysis = prose_qc.analyse_style([self.paragraph(text)])

        self.assertEqual("fail", analysis.get("status"))
        self.assertEqual(2, analysis.get("hard_banned_count"))
        families = analysis.get("families", {})
        self.assertEqual(3, families.get("reader_management", {}).get("count"))
        self.assertEqual(1, families.get("author_intervention", {}).get("count"))

    def test_density_budget_flags_repeated_meta_narration(self) -> None:
        text = " ".join(
            [
                "Let me explain the mechanism in ordinary language.",
                "Here is what the system does with the input.",
                "Let me show you the result before describing the calculation.",
                "The remaining words describe a small network processing values through layers "
                "and returning an output based on parameters learned during training.",
            ]
        )
        analysis = prose_qc.analyse_style(
            [self.paragraph(text)], density_limits={"author_intervention": 1.0}
        )

        intervention = analysis.get("families", {}).get("author_intervention", {})
        self.assertEqual(3, intervention.get("count"))
        self.assertTrue(intervention.get("over_budget"))
        self.assertEqual("fail", analysis.get("status"))

    def test_plain_explanatory_prose_passes(self) -> None:
        text = (
            "Inference is the stage when a trained neural network uses its learned parameters "
            "to calculate an output for new input. Training changes the parameters. Inference "
            "leaves them alone and runs the calculation they now define."
        )
        analysis = prose_qc.analyse_style([self.paragraph(text)])

        self.assertEqual("pass", analysis.get("status"))
        self.assertEqual(0, analysis.get("hard_banned_count"))

    def test_groups_repetitive_honesty_announcements(self) -> None:
        text = (
            "Honestly, the mechanism is simpler than it first appears. "
            "The honest answer is that the evidence remains incomplete. "
            "To be honest, nobody yet knows which interpretation is correct. "
            "In all honesty, the uncertainty belongs in the claim itself. "
            "The remaining words provide enough ordinary narration for a stable density result."
        )

        analysis = prose_qc.analyse_style([self.paragraph(text)])

        family = analysis.get("families", {}).get("honesty_announcement", {})
        self.assertEqual(4, family.get("count"))
        self.assertTrue(family.get("over_budget"))
        self.assertEqual("fail", analysis.get("status"))

    def test_groups_related_candor_announcements(self) -> None:
        text = (
            "Let's be honest: the evidence is incomplete. "
            "Truth be told, the trial was small. "
            "To tell you the truth, the result may not replicate. "
            "Candidly, the estimate is unstable. "
            "Frankly, nobody knows yet. "
            "If we're being honest, the mechanism still needs testing. "
            "The only honest assessment is that two explanations remain."
        )

        analysis = prose_qc.analyse_style([self.paragraph(text)])

        family = analysis.get("families", {}).get("honesty_announcement", {})
        self.assertEqual(7, family.get("count"))

    def test_markdown_report_surfaces_family_counts_and_locations(self) -> None:
        text = (
            "Hold on to this. The remaining sentence explains a trained network using its "
            "parameters to calculate a useful output from a new input during inference."
        )
        paragraph = self.paragraph(text)
        output = prose_qc.report([paragraph], 6, 0.68, 20)

        self.assertIn("## Rhetorical family gate", output)
        self.assertIn("reader_management", output)
        self.assertIn("ch01.md ¶1", output)


class ProseStyleReceiptTests(unittest.TestCase):
    def decisions(self) -> dict[str, object]:
        return {
            "reviewer": "frontier-author",
            "model": "GPT-5 Codex",
            "skill_version": "declaudification-v1",
            "humanizer_applied": True,
            "accepted": [],
            "rejected": [],
            "checks_rerun": ["factual", "coverage-ledger", "narration", "prose"],
        }

    def test_receipt_binds_passed_analysis_and_chapter_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            chapters = root / "chapters"
            chapters.mkdir()
            chapter = chapters / "ch01.md"
            chapter.write_text(
                "## Chapter 1 - Inference\n\n"
                "Inference runs a trained network on new input without changing its learned parameters.\n",
                encoding="utf-8",
            )
            paragraphs = prose_qc.extract_paragraphs(chapter)
            analysis = prose_qc.analyse_style(paragraphs)
            receipt_path = root / "prose-receipt.json"

            prose_qc.write_style_receipt(chapters, receipt_path, analysis, self.decisions())
            self.assertTrue(receipt_path.is_file())
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertEqual("pass", receipt["status"])
            self.assertIn("ch01.md", receipt["chapter_sha256"])
            self.assertEqual(receipt, prose_qc.verify_style_receipt(chapters, receipt_path))

            chapter.write_text(chapter.read_text(encoding="utf-8") + "Changed.\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "chapter hash"):
                prose_qc.verify_style_receipt(chapters, receipt_path)

    def test_receipt_requires_the_humanizer_and_rerun_checks(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            chapters = root / "chapters"
            chapters.mkdir()
            (chapters / "ch01.md").write_text(
                "## Chapter 1\n\nA plain explanation with enough words to be inspected correctly.\n",
                encoding="utf-8",
            )
            decisions = self.decisions()
            decisions["checks_rerun"] = ["prose"]

            with self.assertRaisesRegex(ValueError, "checks_rerun"):
                prose_qc.write_style_receipt(
                    chapters, root / "receipt.json", {"status": "pass"}, decisions
                )

    def test_book_builder_refuses_a_stale_prose_receipt_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            chapters = root / "chapters"
            chapters.mkdir()
            chapter = chapters / "ch01.md"
            chapter.write_text(
                "## Chapter 1 - Inference\n\n"
                "Inference runs a trained network on new input without changing its learned parameters.\n",
                encoding="utf-8",
            )
            analysis = prose_qc.analyse_style(prose_qc.extract_paragraphs(chapter))
            receipt = root / "receipt.json"
            prose_qc.write_style_receipt(chapters, receipt, analysis, self.decisions())
            chapter.write_text(chapter.read_text(encoding="utf-8") + "Changed.\n", encoding="utf-8")
            output = root / "dist"

            with self.assertRaisesRegex(ValueError, "chapter hash"):
                build_book.build(
                    str(chapters), str(output), "Fixture", "Dan Fakkeldy", "", "fixture",
                    prose_receipt=str(receipt),
                )
            self.assertFalse(output.exists())

    def test_cli_fails_closed_and_can_write_a_reviewed_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            chapters = root / "chapters"
            chapters.mkdir()
            chapter = chapters / "ch01.md"
            chapter.write_text(
                "## Chapter 1\n\nHold on to this. The rest of the paragraph explains how "
                "a trained network calculates outputs from inputs during inference without "
                "changing its learned parameters.\n",
                encoding="utf-8",
            )
            script = Path(prose_qc.__file__)
            failed = subprocess.run(
                [sys.executable, str(script), "--chapters-dir", str(chapters), "--fail-on-style"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(1, failed.returncode)
            self.assertIn("Rhetorical family gate", failed.stdout)

            chapter.write_text(
                "## Chapter 1\n\nInference uses a trained network to calculate an output "
                "from new input while leaving the learned parameters unchanged. This contrasts "
                "with training, which updates those parameters from examples.\n",
                encoding="utf-8",
            )
            decisions_path = root / "decisions.json"
            decisions_path.write_text(json.dumps(self.decisions()), encoding="utf-8")
            receipt_path = root / "receipt.json"
            passed = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--chapters-dir",
                    str(chapters),
                    "--fail-on-style",
                    "--style-receipt-out",
                    str(receipt_path),
                    "--decisions",
                    str(decisions_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, passed.returncode, passed.stderr)
            self.assertEqual("pass", json.loads(receipt_path.read_text(encoding="utf-8"))["status"])


if __name__ == "__main__":
    unittest.main()
