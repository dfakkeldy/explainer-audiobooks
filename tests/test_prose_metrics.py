import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "skill" / "scripts"))
import prose_metrics


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

    def test_coordinate_lists_flags_four_item_series(self):
        text = ("Non-diminishing use does not erase planning law, tenancy, "
                "occupancy, safety, or the continuing redemption right.")
        result = prose_metrics.coordinate_lists([text])
        self.assertEqual(result["count"], 1)
        self.assertIn("planning law, tenancy", result["examples"][0])

    def test_coordinate_lists_ignores_three_item_series(self):
        # Three items is ordinary English; four or more is the tell.
        text = "He brought bread, cheese, and wine."
        self.assertEqual(prose_metrics.coordinate_lists([text])["count"], 0)

    def test_coordinate_lists_per_1k_sentences_is_normalised(self):
        listed = ("alpha, beta, gamma, delta, and epsilon follow. ") * 2
        plain = "Short one. " * 8
        result = prose_metrics.coordinate_lists([listed + plain])
        self.assertEqual(result["count"], 2)
        self.assertEqual(result["per_1k_sentences"], 200.0)


if __name__ == "__main__":
    unittest.main()
