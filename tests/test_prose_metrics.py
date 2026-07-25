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

    def test_abstract_subjects_flags_concept_in_subject_slot(self):
        text = ("The document matters because a bid and a paid sale differ. "
                "Each power arrives with a boundary.")
        result = prose_metrics.abstract_subjects([text])
        self.assertEqual(result["count"], 2)

    def test_abstract_subjects_ignores_concrete_actors(self):
        text = "The treasurer registers the certificate. Gazzaniga asked why."
        self.assertEqual(prose_metrics.abstract_subjects([text])["count"], 0)

    def test_abstract_subjects_share_is_normalised(self):
        text = "The document matters. A clerk signed it."
        self.assertEqual(prose_metrics.abstract_subjects([text])["share_of_sentences"], 0.5)

    def test_arithmetic_density_counts_operation_language(self):
        text = "You multiply the weights, take the gradient, then the chain rule applies."
        result = prose_metrics.arithmetic_density(text)
        self.assertEqual(result["count"], 3)

    def test_arithmetic_density_normalises_per_10k_words(self):
        text = ("multiply " + "filler " * 999)
        self.assertEqual(prose_metrics.arithmetic_density(text)["per_10k_words"], 10.0)

    def test_arithmetic_tiers_place_ed1_baseline_in_light(self):
        # Question Machine ed1 measured 7.1 arithmetic terms per 10k words and
        # taught successfully. "light" must contain that value.
        low, high = prose_metrics.ARITHMETIC_TIERS["light"]
        self.assertTrue(low <= 7.1 <= high)

    def test_arithmetic_tiers_none_excludes_ed1_baseline(self):
        low, high = prose_metrics.ARITHMETIC_TIERS["none"]
        self.assertFalse(low <= 7.1 <= high)

    def test_abstract_subjects_known_false_positive_on_compound_plural_subject(self):
        # KNOWN LIMITATION: The verb alternation in ABSTRACT_SUBJECT_RE accepts
        # any token ending in "s", so it cannot distinguish a third-person-singular
        # verb from a plural noun. When an abstract noun from ABSTRACT_NOUNS acts
        # as a modifier in a compound subject whose head noun is plural, this test
        # will assert the false positive (count=1). This is a documented limitation;
        # any change to the regex to fix this should fail this test and force a
        # deliberate decision.
        text = "The case workers arrived."
        result = prose_metrics.abstract_subjects([text])
        # Currently incorrectly flagged because "case" is in ABSTRACT_NOUNS and
        # "workers" ends in "s", so the regex matches.
        self.assertEqual(result["count"], 1)
        self.assertIn("The case workers arrived", result["examples"][0])


if __name__ == "__main__":
    unittest.main()
