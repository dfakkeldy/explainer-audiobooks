#!/usr/bin/env python3
"""Pure prose measures for audiobook manuscripts.

Every function here is side-effect free and takes plain strings, so each
measure can be unit-tested without touching the filesystem or argparse.
`prose_qc.py` is the only caller that does I/O.

Design note: these measures describe *shape*, not vocabulary. The existing
phrase-family checks in prose_qc.py catch what the prose says; these catch
how uniformly it says it, which is the more reliable AI signature.
"""

from __future__ import annotations

import re
import statistics

SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def split_sentences(text: str) -> list[str]:
    """Split on sentence terminators followed by whitespace."""
    flat = re.sub(r"\s+", " ", text).strip()
    if not flat:
        return []
    return [part for part in SENTENCE_SPLIT_RE.split(flat) if part]


def _cv(values: list[int]) -> float:
    """Coefficient of variation: stdev / mean. Zero when undefined."""
    if len(values) < 2:
        return 0.0
    mean = statistics.mean(values)
    if mean == 0:
        return 0.0
    return statistics.pstdev(values) / mean


def rhythm(paragraph_texts: list[str]) -> dict[str, float]:
    """Variance in paragraph and sentence length.

    Uniformity is the signal. Human nonfiction puts one-sentence paragraphs
    next to nine-sentence ones; generated prose tends to a single length.
    """
    para_lengths = [len(p.split()) for p in paragraph_texts if p.strip()]
    sent_lengths: list[int] = []
    for paragraph in paragraph_texts:
        sent_lengths.extend(len(s.split()) for s in split_sentences(paragraph))
    return {
        "paragraph_cv": round(_cv(para_lengths), 4),
        "sentence_cv": round(_cv(sent_lengths), 4),
        "paragraph_mean": round(statistics.mean(para_lengths), 2) if para_lengths else 0.0,
        "sentence_mean": round(statistics.mean(sent_lengths), 2) if sent_lengths else 0.0,
        "paragraph_count": len(para_lengths),
        "sentence_count": len(sent_lengths),
    }
