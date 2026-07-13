#!/usr/bin/env python3
"""Validate Echo's schema-v1 pronunciation acceptance manifest."""

from __future__ import annotations

import json
import sys
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


class AuditValidationError(ValueError):
    """The manifest cannot prove a complete pronunciation review."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditValidationError(message)


def validate(audit_path: Path) -> None:
    payload = json.loads(audit_path.read_text(encoding="utf-8"))
    require(isinstance(payload, dict), "manifest root must be an object")
    missing = sorted(REQUIRED_FIELDS - payload.keys())
    require(not missing, f"manifest missing fields: {missing}")
    require(payload["schemaVersion"] == 1, "schemaVersion must be 1")
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
    require(audit_path.name.endswith(stem_suffix), f"audit filename must end with {stem_suffix}")
    stem = audit_path.name.removesuffix(stem_suffix)
    require(
        payload["audiobookFileName"] == f"{stem}.m4b",
        "audiobook filename is not relative or does not match the audit stem",
    )

    watch_counts = payload["watchCounts"]
    require(isinstance(watch_counts, dict), "watchCounts must be an object")
    for word in WATCH_WORDS:
        require(word in watch_counts, f"watchCounts is missing {word}")
        count = watch_counts[word]
        require(
            type(count) is int and count >= 0,
            f"watchCounts.{word} must be a nonnegative integer",
        )

    expected_reel_name = f"{stem}.pronunciation-reel.m4b"
    reel_name = payload.get("listeningReelFileName")
    require(
        reel_name is None or reel_name == expected_reel_name,
        "listening reel filename is not relative or does not match the audit stem",
    )
    reel_path = audit_path.parent / expected_reel_name
    require(
        reel_path.exists() == (reel_name is not None),
        "listening reel file and manifest filename disagree",
    )


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
