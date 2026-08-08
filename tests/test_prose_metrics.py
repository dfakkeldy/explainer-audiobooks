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

    def test_fragment_chains_counts_consecutive_short_sentences(self):
        text = ("The model answered every probe the same way across many runs. "
                "Not once. Not ever. Ninety-seven, seventy-four, seventy-one. "
                "The full explanation takes several more clauses to state properly.")
        result = prose_metrics.fragment_chains([text])
        self.assertEqual(result["chain_count"], 1)
        self.assertEqual(result["longest_chain"], 3)
        self.assertIn("Not once. Not ever.", result["examples"][0])

    def test_fragment_chains_ignores_a_single_clipped_sentence(self):
        # One short sentence after a long one is deliberate emphasis,
        # not the drumbeat. Only runs of two or more are reported.
        text = ("The parameters stay frozen while inference runs the calculation "
                "they define. It bends. The gold settles through the gravel until "
                "bedrock finally stops it somewhere out of sight.")
        result = prose_metrics.fragment_chains([text])
        self.assertEqual(result["chain_count"], 0)
        self.assertGreater(result["short_sentence_share"], 0.0)

    def test_fragment_chains_reset_at_paragraph_boundaries(self):
        # A short closer and a short opener in adjacent paragraphs are not
        # one chain; the rhythm reads differently across a paragraph break.
        first = "The claim map loads slowly over a weak connection. It bends."
        second = "Gold sinks. Every crack in the bedrock catches a little more of it."
        result = prose_metrics.fragment_chains([first, second])
        self.assertEqual(result["chain_count"], 0)

    def test_fragment_chains_empty_input_is_safe(self):
        result = prose_metrics.fragment_chains([])
        self.assertEqual(result["chain_count"], 0)
        self.assertEqual(result["short_sentence_share"], 0.0)

    def test_arithmetic_density_counts_operation_language(self):
        text = "You multiply the weights, take the gradient, then the chain rule applies."
        result = prose_metrics.arithmetic_density(text)
        self.assertEqual(result["count"], 3)

    def test_arithmetic_density_normalises_per_10k_words(self):
        text = ("multiply " + "filler " * 999)
        self.assertEqual(prose_metrics.arithmetic_density(text)["per_10k_words"], 10.0)

    def test_arithmetic_tiers_place_ed1_baseline_in_light(self):
        # The Question Machine ed1, measured with the shipped ARITHMETIC_RE
        # (not the earlier exploratory regex that double-counted "times",
        # "plus", "minus" as ordinary English), is 1.97 arithmetic terms per
        # 10k words, and it taught successfully. "light" must contain that
        # value -- that's the whole point of the tier system.
        low, high = prose_metrics.ARITHMETIC_TIERS["light"]
        self.assertTrue(low <= 1.97 <= high)

    def test_arithmetic_tiers_none_excludes_ed1_baseline(self):
        low, high = prose_metrics.ARITHMETIC_TIERS["none"]
        self.assertFalse(low <= 1.97 <= high)

    def test_arithmetic_tier_verdict_within_band_is_true(self):
        result = prose_metrics.arithmetic_tier_verdict(1.97, "light")
        self.assertTrue(result["known"])
        self.assertTrue(result["within_band"])
        self.assertEqual(result["measured"], 1.97)
        self.assertEqual(result["band"], [0.5, 5.0])

    def test_arithmetic_tier_verdict_outside_band_is_false(self):
        result = prose_metrics.arithmetic_tier_verdict(20.0, "none")
        self.assertTrue(result["known"])
        self.assertFalse(result["within_band"])

    def test_arithmetic_tier_verdict_unknown_tier_reads_as_compliant(self):
        # An unrecognized tier name (a typo, a stale brief) must never
        # manufacture a failure: within_band is always True when known is
        # False. This is a deliberate tradeoff -- a typo'd tier silently
        # reads as compliant rather than blocking, so any caller must check
        # `known` before trusting `within_band`.
        result = prose_metrics.arithmetic_tier_verdict(1.97, "extra-spicy")
        self.assertFalse(result["known"])
        self.assertTrue(result["within_band"])

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
