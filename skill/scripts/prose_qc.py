#!/usr/bin/env python3
"""Report likely prose repetition in Markdown audiobook chapters.

This is a candidate generator, not an automatic rewriter. It deliberately
reports repeated phrases and similar paragraphs for human/editorial judgment:
planned vocabulary retrieval may be useful, while an unplanned restatement is
usually padding.
"""

from __future__ import annotations

import argparse
import re
from collections import Counter
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Iterable

WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")
PARAGRAPH_SPLIT_RE = re.compile(r"\n\s*\n")
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "from",
    "in", "into", "is", "it", "its", "of", "on", "or", "that", "the", "this",
    "to", "was", "we", "with", "you", "your",
}


@dataclass(frozen=True)
class Paragraph:
    chapter: str
    number: int
    text: str
    words: tuple[str, ...]

    @property
    def location(self) -> str:
        return f"{self.chapter} ¶{self.number}"

    @property
    def excerpt(self) -> str:
        text = re.sub(r"\s+", " ", self.text).strip()
        return text[:180] + ("…" if len(text) > 180 else "")


def words(text: str) -> tuple[str, ...]:
    return tuple(word.lower() for word in WORD_RE.findall(text))


def chapters(chapters_dir: Path) -> Iterable[Path]:
    yield from sorted(chapters_dir.glob("ch*.md"))


def extract_paragraphs(path: Path) -> list[Paragraph]:
    raw = path.read_text(encoding="utf-8")
    result: list[Paragraph] = []
    for block in PARAGRAPH_SPLIT_RE.split(raw):
        stripped = block.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("!["):
            continue
        tokenized = words(stripped)
        if len(tokenized) >= 20:
            result.append(Paragraph(path.name, len(result) + 1, stripped, tokenized))
    return result


def repeated_phrases(paragraphs: list[Paragraph], n: int, limit: int) -> list[tuple[tuple[str, ...], int]]:
    counts: Counter[tuple[str, ...]] = Counter()
    for paragraph in paragraphs:
        seen_in_paragraph: set[tuple[str, ...]] = set()
        for index in range(len(paragraph.words) - n + 1):
            phrase = paragraph.words[index : index + n]
            if sum(word not in STOPWORDS for word in phrase) < max(2, n // 2):
                continue
            seen_in_paragraph.add(phrase)
        counts.update(seen_in_paragraph)
    return [(phrase, count) for phrase, count in counts.most_common(limit) if count >= 2]


def similar_paragraphs(paragraphs: list[Paragraph], threshold: float, limit: int) -> list[tuple[float, Paragraph, Paragraph]]:
    findings: list[tuple[float, Paragraph, Paragraph]] = []
    for index, left in enumerate(paragraphs):
        left_terms = {word for word in left.words if len(word) >= 5 and word not in STOPWORDS}
        if len(left_terms) < 8:
            continue
        for right in paragraphs[index + 1 :]:
            right_terms = {word for word in right.words if len(word) >= 5 and word not in STOPWORDS}
            union = left_terms | right_terms
            if len(right_terms) < 8 or not union:
                continue
            jaccard = len(left_terms & right_terms) / len(union)
            sequence = SequenceMatcher(None, " ".join(left.words), " ".join(right.words)).ratio()
            score = max(jaccard, sequence)
            if score >= threshold:
                findings.append((score, left, right))
    findings.sort(key=lambda item: item[0], reverse=True)
    return findings[:limit]


def formulaic_starts(paragraphs: list[Paragraph], position: str, limit: int) -> list[tuple[float, Paragraph, Paragraph]]:
    grouped: dict[str, list[Paragraph]] = {}
    for paragraph in paragraphs:
        grouped.setdefault(paragraph.chapter, []).append(paragraph)
    candidates: list[Paragraph] = []
    for chapter_paragraphs in grouped.values():
        candidates.append(chapter_paragraphs[0] if position == "opening" else chapter_paragraphs[-1])

    findings: list[tuple[float, Paragraph, Paragraph]] = []
    for index, left in enumerate(candidates):
        left_text = " ".join(left.words[:45] if position == "opening" else left.words[-45:])
        for right in candidates[index + 1 :]:
            right_text = " ".join(right.words[:45] if position == "opening" else right.words[-45:])
            score = SequenceMatcher(None, left_text, right_text).ratio()
            if score >= 0.42:
                findings.append((score, left, right))
    findings.sort(key=lambda item: item[0], reverse=True)
    return findings[:limit]


def report(paragraphs: list[Paragraph], phrase_size: int, threshold: float, limit: int) -> str:
    lines = ["# Prose QC Candidate Report", "", "> This report flags candidates; verify against the coverage ledger before editing. Intentional retrieval practice is not padding.", ""]
    chapter_counts = Counter(paragraph.chapter for paragraph in paragraphs)
    lines += ["## Input", "", f"- Chapters: {len(chapter_counts)}", f"- Analysed prose paragraphs: {len(paragraphs)}", ""]

    phrases = repeated_phrases(paragraphs, phrase_size, limit)
    lines += ["## Repeated phrases", ""]
    if phrases:
        for phrase, count in phrases:
            lines.append(f"- **{count}×**: “{' '.join(phrase)}”")
    else:
        lines.append("- No repeated phrase candidates at this threshold.")
    lines.append("")

    similar = similar_paragraphs(paragraphs, threshold, limit)
    lines += ["## Similar paragraphs", ""]
    if similar:
        for score, left, right in similar:
            lines += [f"- **{score:.0%}** — {left.location} ↔ {right.location}", f"  - {left.excerpt}", f"  - {right.excerpt}"]
    else:
        lines.append("- No similar paragraph candidates at this threshold.")
    lines.append("")

    for position, heading in (("opening", "Formulaic chapter openings"), ("closing", "Formulaic chapter closings")):
        findings = formulaic_starts(paragraphs, position, limit)
        lines += [f"## {heading}", ""]
        if findings:
            for score, left, right in findings:
                lines.append(f"- **{score:.0%}** — {left.chapter} ↔ {right.chapter}")
        else:
            lines.append("- No similar chapter-pattern candidates at this threshold.")
        lines.append("")

    lines += ["## Editorial decision", "", "For every candidate, mark it as **keep** (intentional retrieval with a named learning purpose), **tighten**, **deepen**, **replace with an example/boundary**, or **remove**. Only the frontier author makes substantive prose changes.", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chapters-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, help="Write the Markdown report here instead of stdout.")
    parser.add_argument("--phrase-size", type=int, default=6)
    parser.add_argument("--similarity-threshold", type=float, default=0.68)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    if args.phrase_size < 3:
        parser.error("--phrase-size must be at least 3")
    if not 0 < args.similarity_threshold <= 1:
        parser.error("--similarity-threshold must be between 0 and 1")
    if not args.chapters_dir.is_dir():
        parser.error(f"not a directory: {args.chapters_dir}")

    source_files = list(chapters(args.chapters_dir))
    if not source_files:
        parser.error(f"no ch*.md files in: {args.chapters_dir}")
    paragraphs = [paragraph for path in source_files for paragraph in extract_paragraphs(path)]
    output = report(paragraphs, args.phrase_size, args.similarity_threshold, args.limit)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
