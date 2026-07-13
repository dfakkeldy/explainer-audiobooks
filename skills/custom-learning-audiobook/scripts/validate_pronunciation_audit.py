#!/usr/bin/env python3
"""Validate Echo's schema-v1 pronunciation acceptance manifest."""

from __future__ import annotations

import json
import math
import sys
from collections import Counter
from pathlib import Path


WATCH_WORDS = ("startable", "filesystem", "verified", "live", "lives", "record")
REQUIRED_FIELDS = {
    "schemaVersion",
    "renderVersion",
    "voice",
    "coverage",
    "watchCounts",
    "decisions",
    "diagnostics",
    "legacyChapterIndexes",
    "audiobookFileName",
}
DECISION_REQUIRED_FIELDS = {
    "blockID",
    "wordStart",
    "wordEnd",
    "normalizedWord",
    "sourceWord",
    "sourceContext",
    "selectedIPA",
    "kokoroTokenIDs",
    "source",
    "ruleID",
    "rationale",
}
DECISION_STRING_FIELDS = (
    "blockID",
    "normalizedWord",
    "sourceWord",
    "sourceContext",
    "selectedIPA",
    "ruleID",
    "rationale",
)
DECISION_SOURCES = {
    "occurrenceOverride",
    "bookOverride",
    "globalOverride",
    "builtInOverride",
    "contextualHomograph",
    "monitoredLexicon",
    "fallback",
}
TIMING_PRECISIONS = {"exactSynthesisWord", "blockAnchorFallback"}
INT32_MAX = (2**31) - 1


class AuditValidationError(ValueError):
    """The manifest cannot prove a complete pronunciation review."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditValidationError(message)


def require_nonempty_string(value: object, field: str) -> str:
    require(
        isinstance(value, str) and bool(value.strip()),
        f"{field} must be a nonempty string",
    )
    return value


def require_nonnegative_int(value: object, field: str) -> int:
    require(type(value) is int and value >= 0, f"{field} must be a nonnegative integer")
    return value


def validate_audio_range(value: object, field: str) -> bool:
    if value is None:
        return False
    require(isinstance(value, dict), f"{field} must be an object or null")
    require("start" in value and "end" in value, f"{field} must contain start and end")
    start = value["start"]
    end = value["end"]
    for component, component_value in (("start", start), ("end", end)):
        require(
            type(component_value) in (int, float)
            and math.isfinite(component_value)
            and component_value >= 0,
            f"{field}.{component} must be a finite nonnegative number",
        )
    require(end > start, f"{field}.end must be greater than start")
    return True


def validate_decision(decision: object, index: int) -> dict[str, object]:
    label = f"decisions[{index}]"
    require(isinstance(decision, dict), f"{label} must be an object")
    missing = sorted(DECISION_REQUIRED_FIELDS - decision.keys())
    require(not missing, f"{label} missing fields: {missing}")

    for field in DECISION_STRING_FIELDS:
        require_nonempty_string(decision[field], f"{label}.{field}")

    word_start = require_nonnegative_int(decision["wordStart"], f"{label}.wordStart")
    word_end = require_nonnegative_int(decision["wordEnd"], f"{label}.wordEnd")
    require(word_end >= word_start, f"{label}.wordEnd must not precede wordStart")

    token_ids = decision["kokoroTokenIDs"]
    require(
        isinstance(token_ids, list) and bool(token_ids),
        f"{label}.kokoroTokenIDs must be nonempty",
    )
    for token_index, token_id in enumerate(token_ids):
        require(
            type(token_id) is int and 0 < token_id <= INT32_MAX,
            f"{label}.kokoroTokenIDs[{token_index}] must be a positive Int32 token ID",
        )

    source = decision["source"]
    require(
        isinstance(source, str) and source in DECISION_SOURCES,
        f"{label}.source is invalid",
    )
    chapter_index = decision.get("chapterIndex")
    if chapter_index is not None:
        require_nonnegative_int(chapter_index, f"{label}.chapterIndex")

    chapter_range = validate_audio_range(
        decision.get("chapterRelativeAudioRange"),
        f"{label}.chapterRelativeAudioRange",
    )
    book_range = validate_audio_range(
        decision.get("bookRelativeAudioRange"),
        f"{label}.bookRelativeAudioRange",
    )
    timing_precision = decision.get("timingPrecision")
    require(
        timing_precision is None
        or (
            isinstance(timing_precision, str) and timing_precision in TIMING_PRECISIONS
        ),
        f"{label}.timingPrecision is invalid",
    )
    require(
        not book_range or chapter_range, f"{label} book timing requires chapter timing"
    )
    require(
        not (chapter_range or book_range or timing_precision is not None)
        or chapter_index is not None,
        f"{label} timing requires chapterIndex",
    )
    require(
        chapter_range == (timing_precision is not None),
        f"{label} chapter timing and timingPrecision must appear together",
    )
    return decision


def validate(audit_path: Path) -> None:
    payload = json.loads(audit_path.read_text(encoding="utf-8"))
    require(isinstance(payload, dict), "manifest root must be an object")
    missing = sorted(REQUIRED_FIELDS - payload.keys())
    require(not missing, f"manifest missing fields: {missing}")
    require(
        type(payload["schemaVersion"]) is int and payload["schemaVersion"] == 1,
        "schemaVersion must be 1",
    )
    require(
        type(payload["renderVersion"]) is int and payload["renderVersion"] > 0,
        "renderVersion must be a positive integer",
    )
    require_nonempty_string(payload["voice"], "voice")
    require(payload["coverage"] == "complete", "coverage must be complete")
    require(isinstance(payload["decisions"], list), "decisions must be an array")
    require(isinstance(payload["diagnostics"], list), "diagnostics must be an array")
    require(not payload["diagnostics"], "complete coverage cannot contain diagnostics")
    require(
        isinstance(payload["legacyChapterIndexes"], list),
        "legacyChapterIndexes must be an array",
    )
    require(
        not payload["legacyChapterIndexes"],
        "complete coverage cannot contain legacy chapter indexes",
    )

    stem_suffix = ".pronunciation-audit.json"
    require(
        audit_path.name.endswith(stem_suffix),
        f"audit filename must end with {stem_suffix}",
    )
    stem = audit_path.name.removesuffix(stem_suffix)
    require(
        payload["audiobookFileName"] == f"{stem}.m4b",
        "audiobook filename is not relative or does not match the audit stem",
    )

    decisions = [
        validate_decision(decision, index)
        for index, decision in enumerate(payload["decisions"])
    ]

    watch_counts = payload["watchCounts"]
    require(isinstance(watch_counts, dict), "watchCounts must be an object")
    for word, count in watch_counts.items():
        require_nonempty_string(word, "watchCounts key")
        require_nonnegative_int(count, f"watchCounts.{word}")
    for word in WATCH_WORDS:
        require(word in watch_counts, f"watchCounts is missing {word}")
    decision_counts = Counter(decision["normalizedWord"] for decision in decisions)
    for word, count in watch_counts.items():
        require(
            count == decision_counts[word],
            f"watchCounts.{word} does not match decisions",
        )

    expected_reel_name = f"{stem}.pronunciation-reel.m4b"
    reel_name = payload.get("listeningReelFileName")
    require(
        reel_name is None or reel_name == expected_reel_name,
        "listening reel filename is not relative or does not match the audit stem",
    )
    reel_path = audit_path.parent / expected_reel_name
    if reel_name is None:
        require(
            not reel_path.exists() and not reel_path.is_symlink(),
            "unlisted listening reel is present",
        )
    else:
        require(reel_path.is_file(), "listed listening reel is missing or not a file")


def main(arguments: list[str]) -> int:
    if len(arguments) != 1:
        print("usage: validate_pronunciation_audit.py AUDIT_JSON", file=sys.stderr)
        return 64
    try:
        validate(Path(arguments[0]))
    except (AuditValidationError, json.JSONDecodeError, OSError) as error:
        print(f"pronunciation_audit: {error}", file=sys.stderr)
        return 1
    print("pronunciation_audit: clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
