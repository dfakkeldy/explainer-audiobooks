"""Empirical thresholds, validated against three real books.

Known verdicts, from the design spec:
  Question Machine ed1        taught well   sentence_cv 0.662, lists  9.3
  Is There Anyone in Here?    good          sentence_cv 0.656, lists 14.2
  NS tax-sale book            weak          sentence_cv 0.503, lists 62.6

Measured 2026-07-25 with this repo's own COORDINATE_LIST_RE and rhythm().
An earlier exploratory regex matched only single-word list items and gave
0/0/12; the shipped detector allows 1-4 words per item and gives the numbers
above. The relative ordering -- the weak book runs 4-7x the good books -- is
what carries the signal, and it holds under both detectors.

Actual values reproduced against SENTENCE_CV_FLOOR=0.60 and
COORDINATE_LIST_CEILING=25.0 below (209/126/558 qualifying paragraphs):
  qm_ed1        sentence_cv=0.6624  lists_per_1k=9.29   (build/, this worktree)
  consciousness sentence_cv=0.6563  lists_per_1k=14.25  (main checkout only --
                the .build/ corpus is not tracked in any worktree, so this
                subTest SKIPS here; verified by running the same _paragraphs/
                rhythm/coordinate_lists pipeline directly against
                /Users/dfakkeldy/Developer/explainer-audiobooks/.build/
                custom-learning-audiobooks/is-there-anyone-in-here/chapters)
  tax_sale      sentence_cv=0.5029  lists_per_1k=62.63  (docs/, this worktree)
qm_ed1 arithmetic_density=1.98 per_10k_words, within the "light" band [0.5, 5.0].

A threshold that does not reproduce this split is wrong. The corpora live
outside version control, so a missing corpus SKIPS rather than fails --
a fresh clone must stay green.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "skill" / "scripts"))
import prose_metrics

REPO = Path(__file__).resolve().parents[1]

SENTENCE_CV_FLOOR = 0.60
COORDINATE_LIST_CEILING = 25.0

GOOD_BOOKS = ("qm_ed1", "consciousness")

CORPORA = {
    "qm_ed1": REPO / "build" / "the-question-machine" / "chapters-narration",
    "consciousness": REPO / ".build" / "custom-learning-audiobooks"
                          / "is-there-anyone-in-here" / "chapters",
    "tax_sale": REPO / "docs" / "nova-scotia-tax-sale-book" / "chapters",
}


def _paragraphs(directory: Path) -> list[str]:
    texts: list[str] = []
    for path in sorted(directory.glob("ch*.md")):
        body = "\n".join(
            line for line in path.read_text(encoding="utf-8").splitlines()
            if not line.startswith("#")
        )
        texts.extend(
            block for block in body.split("\n\n") if len(block.split()) > 15
        )
    return texts


class CorpusRegressionTests(unittest.TestCase):
    def _load(self, name: str) -> list[str]:
        directory = CORPORA[name]
        if not directory.is_dir():
            self.skipTest(f"corpus {name} not present at {directory}")
        paragraphs = _paragraphs(directory)
        if not paragraphs:
            self.skipTest(f"corpus {name} has no chapters")
        return paragraphs

    def test_good_books_clear_the_sentence_cv_floor(self) -> None:
        for name in GOOD_BOOKS:
            with self.subTest(corpus=name):
                result = prose_metrics.rhythm(self._load(name))
                self.assertGreaterEqual(result["sentence_cv"], SENTENCE_CV_FLOOR)

    def test_weak_book_fails_the_sentence_cv_floor(self) -> None:
        result = prose_metrics.rhythm(self._load("tax_sale"))
        self.assertLess(result["sentence_cv"], SENTENCE_CV_FLOOR)

    def test_good_books_clear_the_coordinate_list_ceiling(self) -> None:
        for name in GOOD_BOOKS:
            with self.subTest(corpus=name):
                result = prose_metrics.coordinate_lists(self._load(name))
                self.assertLessEqual(
                    result["per_1k_sentences"], COORDINATE_LIST_CEILING
                )

    def test_weak_book_exceeds_the_coordinate_list_ceiling(self) -> None:
        result = prose_metrics.coordinate_lists(self._load("tax_sale"))
        self.assertGreater(result["per_1k_sentences"], COORDINATE_LIST_CEILING)

    def test_arithmetic_tier_does_not_penalise_the_book_that_taught(self) -> None:
        """Ed1 scored the corpus maximum for arithmetic and taught successfully."""
        joined = "\n\n".join(self._load("qm_ed1"))
        density = prose_metrics.arithmetic_density(joined)
        verdict = prose_metrics.arithmetic_tier_verdict(
            float(density["per_10k_words"]), "light"
        )
        self.assertTrue(verdict["within_band"])


if __name__ == "__main__":
    unittest.main()
