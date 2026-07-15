#!/usr/bin/env python3
"""Report likely prose repetition in Markdown audiobook chapters.

This is a candidate generator, not an automatic rewriter. It deliberately
reports repeated phrases and similar paragraphs for human/editorial judgment:
planned vocabulary retrieval may be useful, while an unplanned restatement is
usually padding.
"""

from __future__ import annotations

import argparse
import hashlib
import json
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

HARD_BANNED_PATTERNS = (
    re.compile(r"\bhold on to (?:this|that)\b", re.IGNORECASE),
    re.compile(r"\b(?:sit|stay) with (?:this|that)\b", re.IGNORECASE),
    re.compile(r"\blet (?:this|that|it) (?:land|sink in)\b", re.IGNORECASE),
    re.compile(r"\bif you remember nothing else\b", re.IGNORECASE),
    re.compile(r"\b(?:tattoo|burn|sear|etch|carve) (?:this|that|it)\b", re.IGNORECASE),
)

STYLE_FAMILIES = {
    "reader_management": re.compile(
        r"\b(?:hold(?: on to)? (?:this|that|it|the (?:thought|idea|image|shape|question|trend|standard|qualifier))"
        r"|(?:sit|stay) with (?:this|that|it)"
        r"|carry (?:(?:this|that|it)(?: (?:thought|idea|image|shape|question|trend|thread|number))?|the (?:thought|idea|image|shape|question|trend|thread|number)) (?:forward|with you|out of [a-z -]+)"
        r"|keep (?:this|that|it|the (?:thought|idea|image|shape|question|trend|thread)) (?:close|open|in mind|with you)"
        r"|let (?:this|that|it) (?:land|sink in)"
        r"|pause on (?:this|that|it|the [a-z -]+)"
        r"|resist (?:this|that|it))\b",
        re.IGNORECASE,
    ),
    "author_intervention": re.compile(
        r"\b(?:let me|i want you|i need you|notice (?:what|how|that|the)|here(?:'s| is) (?:the|what|where))\b",
        re.IGNORECASE,
    ),
    "announced_transition": re.compile(
        r"\b(?:one last thing|one more thing|which brings us|that brings us|before we move(?: on)?)\b",
        re.IGNORECASE,
    ),
    "contrast_frame": re.compile(
        r"\bnot because\b.{0,180}?\bbut because\b|\bthis is not\b.{0,120}?\bthis is\b",
        re.IGNORECASE,
    ),
    "honesty_announcement": re.compile(
        r"\b(?:honestly|candidly|frankly|truthfully"
        r"|to be (?:perfectly |completely |entirely )?honest"
        r"|in all honesty|let(?:'s| us) be honest|truth be told"
        r"|to tell (?:you )?the truth"
        r"|if (?:i am|i'm|we are|we're)(?: being)? honest"
        r"|the (?:only |most |plain )?honest (?:answer|truth|assessment|view|thing)(?: is)?)\b",
        re.IGNORECASE,
    ),
    "faux_gravity": re.compile(
        r"\b(?:the whole point|the heart of|the real (?:magic|secret|power)|it changes everything|the kind thing)\b",
        re.IGNORECASE,
    ),
}

DEFAULT_DENSITY_LIMITS = {
    "reader_management": 2.0,
    "author_intervention": 4.0,
    "announced_transition": 2.0,
    "contrast_frame": 4.0,
    "honesty_announcement": 0.5,
    "faux_gravity": 1.0,
}

REQUIRED_RERUN_CHECKS = {"factual", "coverage-ledger", "narration", "prose"}


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


def _style_matches(paragraphs: list[Paragraph], pattern: re.Pattern[str]) -> list[dict[str, object]]:
    matches: list[dict[str, object]] = []
    for paragraph in paragraphs:
        for match in pattern.finditer(paragraph.text):
            matches.append({
                "location": paragraph.location,
                "text": match.group(0),
                "excerpt": paragraph.excerpt,
            })
    return matches


def analyse_style(
    paragraphs: list[Paragraph],
    density_limits: dict[str, float] | None = None,
) -> dict[str, object]:
    limits = {**DEFAULT_DENSITY_LIMITS, **(density_limits or {})}
    total_words = sum(len(paragraph.words) for paragraph in paragraphs)
    hard_matches = [
        match
        for pattern in HARD_BANNED_PATTERNS
        for match in _style_matches(paragraphs, pattern)
    ]
    families: dict[str, dict[str, object]] = {}
    for name, pattern in STYLE_FAMILIES.items():
        matches = _style_matches(paragraphs, pattern)
        density = (len(matches) * 10_000 / total_words) if total_words else 0.0
        limit = limits[name]
        families[name] = {
            "count": len(matches),
            "density_per_10000_words": round(density, 2),
            "limit_per_10000_words": limit,
            "over_budget": density > limit,
            "matches": matches,
        }
    failed = bool(hard_matches) or any(
        bool(family["over_budget"]) for family in families.values()
    )
    return {
        "schema_version": 1,
        "status": "fail" if failed else "pass",
        "total_words": total_words,
        "hard_banned_count": len(hard_matches),
        "hard_banned_matches": hard_matches,
        "families": families,
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _chapter_hashes(chapters_dir: Path) -> dict[str, str]:
    return {path.name: _sha256(path) for path in chapters(chapters_dir)}


def write_style_receipt(
    chapters_dir: Path,
    receipt_path: Path,
    analysis: dict[str, object],
    decisions: dict[str, object],
) -> dict[str, object]:
    required_fields = {
        "reviewer", "model", "skill_version", "humanizer_applied",
        "accepted", "rejected", "checks_rerun",
    }
    missing = required_fields - decisions.keys()
    if missing:
        raise ValueError("decisions missing fields: " + ", ".join(sorted(missing)))
    if decisions["humanizer_applied"] is not True:
        raise ValueError("humanizer_applied must be true")
    rerun = set(decisions["checks_rerun"] if isinstance(decisions["checks_rerun"], list) else [])
    if not REQUIRED_RERUN_CHECKS <= rerun:
        missing_checks = REQUIRED_RERUN_CHECKS - rerun
        raise ValueError("checks_rerun missing: " + ", ".join(sorted(missing_checks)))
    if not isinstance(decisions["accepted"], list) or not isinstance(decisions["rejected"], list):
        raise ValueError("accepted and rejected must be lists")

    receipt = {
        "schema_version": 1,
        "status": analysis.get("status", "fail"),
        "chapter_sha256": _chapter_hashes(Path(chapters_dir)),
        "analysis": analysis,
        "decisions": decisions,
    }
    receipt_path = Path(receipt_path)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def verify_style_receipt(chapters_dir: Path, receipt_path: Path) -> dict[str, object]:
    receipt = json.loads(Path(receipt_path).read_text(encoding="utf-8"))
    if receipt.get("schema_version") != 1:
        raise ValueError("unsupported prose receipt schema")
    if receipt.get("status") != "pass":
        raise ValueError("prose receipt status is not pass")
    expected = receipt.get("chapter_sha256")
    actual = _chapter_hashes(Path(chapters_dir))
    if expected != actual:
        raise ValueError("prose receipt chapter hash mismatch")
    return receipt


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

    style = analyse_style(paragraphs)
    lines += [
        "## Rhetorical family gate",
        "",
        f"- Status: **{style['status']}**",
        f"- Hard-banned matches: **{style['hard_banned_count']}**",
    ]
    for name, family in style["families"].items():
        lines.append(
            f"- `{name}`: **{family['count']}** matches; "
            f"{family['density_per_10000_words']} per 10,000 words "
            f"(limit {family['limit_per_10000_words']})"
        )
        for match in family["matches"][:limit]:
            lines.append(f"  - {match['location']}: “{match['text']}”")
    for match in style["hard_banned_matches"][:limit]:
        lines.append(f"- Hard ban at {match['location']}: “{match['text']}”")
    lines.append("")

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
    parser.add_argument("--style-receipt-out", type=Path,
                        help="Write a hash-bound prose/humanizer receipt as JSON")
    parser.add_argument("--decisions", type=Path,
                        help="JSON humanizer decisions required by --style-receipt-out")
    parser.add_argument("--fail-on-style", action="store_true",
                        help="Exit 1 when hard bans or family density budgets fail")
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
    style = analyse_style(paragraphs)
    output = report(paragraphs, args.phrase_size, args.similarity_threshold, args.limit)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
    else:
        print(output)
    if args.style_receipt_out:
        if not args.decisions:
            parser.error("--style-receipt-out requires --decisions")
        decisions = json.loads(args.decisions.read_text(encoding="utf-8"))
        write_style_receipt(args.chapters_dir, args.style_receipt_out, style, decisions)
    return 1 if args.fail_on_style and style["status"] != "pass" else 0


if __name__ == "__main__":
    raise SystemExit(main())
