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
COORDINATE_LIST_RE = re.compile(
    r"(?:[\w'-]+(?:\s+[\w'-]+){0,3},\s+){3,}(?:and|or)\s+[\w'-]+",
    re.IGNORECASE,
)

ABSTRACT_NOUNS = frozenset({
    "document", "power", "duty", "protection", "obligation", "requirement",
    "boundary", "distinction", "mechanism", "process", "approach", "concept",
    "principle", "framework", "structure", "pattern", "relationship",
    "uncertainty", "ambiguity", "tension", "tradeoff", "trade-off",
    "difference", "similarity", "importance", "significance", "value",
    "question", "answer", "point", "issue", "problem", "solution",
    "insurance", "redemption", "use", "rent", "notice", "certificate",
    "statute", "provision", "rule", "law", "right", "interest", "position",
    "stage", "state", "step", "phase", "case", "result", "effect", "cause",
    "reason", "purpose", "goal", "benefit", "cost", "risk", "consequence",
})

ABSTRACT_SUBJECT_RE = re.compile(
    r"^(?:The|A|An|Each|Every|This|That)\s+([\w'-]+)\s+(?:\w+s|is|are|was|were|has|have|can|may|must|does|do)\b",
    re.IGNORECASE,
)

ARITHMETIC_RE = re.compile(
    r"\b(?:multiply|multiplied|divide[ds]?|subtract(?:ed)?|sum of|product of"
    r"|square(?:d|s|\s+root)?|derivative|gradient|slope|chain rule|matrix"
    r"|matrices|vector|dot product|weighted sum|partial derivative"
    r"|logarithm|exponent(?:ial)?|coefficient)\b",
    re.IGNORECASE,
)

# Bands are arithmetic terms per 10,000 words. Calibrated from The Question
# Machine ed1 (7.1/10k), which taught successfully and scored the corpus
# maximum. An absolute cap would have failed the book we are reproducing,
# so density is always judged against the brief's declared tier.
ARITHMETIC_TIERS: dict[str, tuple[float, float]] = {
    "none": (0.0, 2.0),
    "light": (2.0, 12.0),
    "quantitative": (12.0, 30.0),
    "symbolic": (30.0, 1000.0),
}


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


def coordinate_lists(paragraph_texts: list[str]) -> dict[str, object]:
    """Count exhaustive coordinated series of four or more items.

    Four-plus item lists are the prose signature of completeness-seeking:
    the writer enumerates the whole category instead of choosing the one
    item that carries the point. Three items is ordinary English and is
    deliberately not flagged.
    """
    examples: list[str] = []
    sentence_total = 0
    for paragraph in paragraph_texts:
        sentence_total += len(split_sentences(paragraph))
        for match in COORDINATE_LIST_RE.finditer(paragraph):
            examples.append(re.sub(r"\s+", " ", match.group(0)).strip())
    per_1k = round(len(examples) / sentence_total * 1000, 2) if sentence_total else 0.0
    return {
        "count": len(examples),
        "per_1k_sentences": per_1k,
        "examples": examples[:20],
    }


def abstract_subjects(paragraph_texts: list[str]) -> dict[str, object]:
    """Count sentences whose grammatical subject is an abstract noun.

    Advisory only. Real writers put people and things in the subject slot
    and concepts in the predicate; "The document matters" is the inversion.
    The noun list is curated rather than exhaustive, so this reports
    candidates for a human, never a verdict.
    """
    examples: list[str] = []
    sentences: list[str] = []
    for paragraph in paragraph_texts:
        sentences.extend(split_sentences(paragraph))
    for sentence in sentences:
        match = ABSTRACT_SUBJECT_RE.match(sentence.strip())
        if match and match.group(1).lower() in ABSTRACT_NOUNS:
            examples.append(sentence.strip()[:160])
    share = round(len(examples) / len(sentences), 4) if sentences else 0.0
    return {
        "count": len(examples),
        "share_of_sentences": share,
        "examples": examples[:20],
    }


def arithmetic_density(text: str) -> dict[str, float]:
    """Rate of arithmetic-operation language per 10,000 words."""
    total_words = len(text.split())
    count = len(ARITHMETIC_RE.findall(text))
    per_10k = round(count / total_words * 10000, 2) if total_words else 0.0
    return {"count": count, "per_10k_words": per_10k}


def arithmetic_tier_verdict(per_10k: float, tier: str) -> dict[str, object]:
    """Compare measured density against the brief's declared tier band."""
    if tier not in ARITHMETIC_TIERS:
        return {"tier": tier, "known": False, "within_band": True}
    low, high = ARITHMETIC_TIERS[tier]
    return {
        "tier": tier,
        "known": True,
        "band": [low, high],
        "measured": per_10k,
        "within_band": low <= per_10k <= high,
    }
