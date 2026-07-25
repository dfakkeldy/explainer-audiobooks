import importlib.util
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "prose_metrics",
    Path(__file__).resolve().parents[1] / "skill" / "scripts" / "prose_metrics.py",
)
prose_metrics = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prose_metrics)


class TestProseMetrics(unittest.TestCase):
    def test_split_sentences_handles_terminators_and_abbreviations(self):
        text = "One two three. Four five! Six seven? Eight."
        self.assertEqual(prose_metrics.split_sentences(text), [
            "One two three.", "Four five!", "Six seven?", "Eight.",
        ])

    def test_rhythm_uniform_paragraphs_score_zero_cv(self):
        # Three identical paragraphs of identical sentences -> no variance at all.
        para = "aa bb cc dd ee. ff gg hh ii jj."
        result = prose_metrics.rhythm([para, para, para])
        self.assertEqual(result["paragraph_cv"], 0.0)
        self.assertEqual(result["sentence_cv"], 0.0)
        self.assertEqual(result["paragraph_count"], 3)
        self.assertEqual(result["sentence_count"], 6)

    def test_rhythm_varied_paragraphs_score_positive_cv(self):
        short = "aa bb."
        long = " ".join(["word"] * 60) + ". " + " ".join(["word"] * 5) + "."
        result = prose_metrics.rhythm([short, long])
        self.assertGreater(result["paragraph_cv"], 0.5)
        self.assertGreater(result["sentence_cv"], 0.5)

    def test_rhythm_empty_input_is_safe(self):
        result = prose_metrics.rhythm([])
        self.assertEqual(result["paragraph_cv"], 0.0)
        self.assertEqual(result["sentence_cv"], 0.0)
        self.assertEqual(result["paragraph_count"], 0)


if __name__ == "__main__":
    unittest.main()
