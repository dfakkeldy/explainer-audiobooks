#!/usr/bin/env python3
"""Validate Echo's media-bound pronunciation acceptance manifest."""

from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path


WATCH_WORDS = (
    "able",
    "arithmetic",
    "available",
    "campbell",
    "comfortable",
    "content",
    "deepmind",
    "deepmind's",
    "fakkeldy",
    "filesystem",
    "lifecycle",
    "live",
    "lives",
    "pictou",
    "possible",
    "re",
    "read",
    "readme",
    "record",
    "reliable",
    "resume",
    "resumes",
    "résumé",
    "résumés",
    "stable",
    "startable",
    "super",
    "supercomputer",
    "supercomputers",
    "superforecasters",
    "superhuman",
    "superimposed",
    "superintelligence",
    "supernatural",
    "superposition",
    "supervised",
    "supervising",
    "table",
    "timeframe",
    "unsupervised",
    "validator",
    "validators",
    "verified",
    "xcassets",
    "xcode",
)
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
    "audiobookSHA256",
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
    "supplementalLexicon",
    "derivedMorphology",
    "monitoredLexicon",
    "fallback",
}
TIMING_PRECISIONS = {"exactSynthesisWord", "blockAnchorFallback"}
INT32_MAX = (2**31) - 1
INT64_MAX = (2**63) - 1
ALLOWED_VOICES = {
    "af_heart",
    "af_bella",
    "af_nicole",
    "af_aoede",
    "af_kore",
    "af_sarah",
    "af_alloy",
    "af_nova",
    "af_sky",
    "af_jessica",
    "af_river",
    "am_fenrir",
    "am_michael",
    "am_puck",
    "am_echo",
    "am_eric",
    "am_liam",
    "am_onyx",
    "am_santa",
    "am_adam",
    "bf_emma",
    "bf_isabella",
    "bf_alice",
    "bf_lily",
    "bm_fable",
    "bm_george",
    "bm_lewis",
    "bm_daniel",
}


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
    require(
        type(value) is int and 0 <= value <= INT64_MAX,
        f"{field} must be a nonnegative signed 64-bit integer",
    )
    return value


def require_sha256(value: object, field: str) -> str:
    require(
        isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None,
        f"{field} must be exactly 64 lowercase hexadecimal characters",
    )
    return value


def file_sha256(path: Path) -> str:
    with path.open("rb") as input_file:
        return hashlib.file_digest(input_file, "sha256").hexdigest()


def media_duration(path: Path) -> float:
    process = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    require(
        process.returncode == 0, f"ffprobe could not read media duration: {path.name}"
    )
    try:
        payload = json.loads(process.stdout)
        duration = float(payload["format"]["duration"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        raise AuditValidationError(
            f"ffprobe returned an invalid media duration: {path.name}"
        ) from error
    require(
        math.isfinite(duration) and duration > 0,
        f"media duration must be positive: {path.name}",
    )
    return duration


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
    schema_version = payload["schemaVersion"]
    require(
        type(schema_version) is int and 2 <= schema_version <= 6,
        "schemaVersion must be between 2 and 6",
    )
    render_version = require_nonnegative_int(payload["renderVersion"], "renderVersion")
    require(render_version >= 12, "renderVersion must be at least 12")
    voice = require_nonempty_string(payload["voice"], "voice")
    if schema_version == 2:
        require(
            voice in {"am_michael", "am_puck"},
            "schema 2 voice must be am_michael or am_puck",
        )
        chapter_voices: dict[str, str] = {}
    else:
        require(
            "chapterVoices" in payload,
            f"schema {schema_version} manifest must contain chapterVoices",
        )
        raw_chapter_voices = payload["chapterVoices"]
        require(
            isinstance(raw_chapter_voices, dict) and bool(raw_chapter_voices),
            f"schema {schema_version} chapterVoices must be a nonempty object",
        )
        chapter_voices = {}
        for chapter_index, chapter_voice in raw_chapter_voices.items():
            require(
                isinstance(chapter_index, str)
                and re.fullmatch(r"0|[1-9][0-9]*", chapter_index) is not None,
                "chapterVoices keys must be canonical nonnegative chapter indexes",
            )
            require(
                isinstance(chapter_voice, str) and chapter_voice in ALLOWED_VOICES,
                f"chapterVoices.{chapter_index} is not a known Echo voice",
            )
            chapter_voices[chapter_index] = chapter_voice
        distinct_voices = set(chapter_voices.values())
        if voice == "mixed":
            require(
                len(distinct_voices) > 1,
                "mixed voice requires more than one distinct chapter voice",
            )
        else:
            require(voice in ALLOWED_VOICES, "voice is not a known Echo voice")
            require(
                distinct_voices == {voice},
                "uniform voice disagrees with chapterVoices",
            )
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
    audiobook_path = audit_path.parent / f"{stem}.m4b"
    require(
        audiobook_path.is_file() and not audiobook_path.is_symlink(),
        "listed audiobook is missing, a symlink, or not a file",
    )
    audiobook_sha256 = require_sha256(payload["audiobookSHA256"], "audiobookSHA256")
    require(
        file_sha256(audiobook_path) == audiobook_sha256,
        "audiobookSHA256 does not match exact sibling audiobook bytes",
    )
    audiobook_duration = media_duration(audiobook_path)

    decisions = [
        validate_decision(decision, index)
        for index, decision in enumerate(payload["decisions"])
    ]
    if schema_version >= 3:
        for index, decision in enumerate(decisions):
            chapter_index = decision.get("chapterIndex")
            if chapter_index is not None:
                require(
                    str(chapter_index) in chapter_voices,
                    f"decisions[{index}].chapterIndex is absent from chapterVoices",
                )

    watch_counts = payload["watchCounts"]
    require(isinstance(watch_counts, dict), "watchCounts must be an object")
    for word, count in watch_counts.items():
        require_nonempty_string(word, "watchCounts key")
        require_nonnegative_int(count, f"watchCounts.{word}")
    for word in WATCH_WORDS:
        require(word in watch_counts, f"watchCounts is missing {word}")
    decision_counts = Counter(decision["normalizedWord"] for decision in decisions)
    for word in decision_counts:
        require(
            word in watch_counts,
            f"decision normalizedWord {word} is absent from watchCounts",
        )
    for word, count in watch_counts.items():
        require(
            count == decision_counts[word],
            f"watchCounts.{word} does not match decisions",
        )

    expected_reel_name = f"{stem}.pronunciation-reel.m4b"
    reel_name = payload.get("listeningReelFileName")
    reel_sha256 = payload.get("listeningReelSHA256")
    require(
        (reel_name is None) == (reel_sha256 is None),
        "listeningReelFileName and listeningReelSHA256 must appear together",
    )
    require(
        reel_name is None or reel_name == expected_reel_name,
        "listening reel filename is not relative or does not match the audit stem",
    )
    reel_path = audit_path.parent / expected_reel_name
    timed_decisions = [
        decision
        for decision in decisions
        if decision.get("chapterRelativeAudioRange") is not None
        or decision.get("bookRelativeAudioRange") is not None
        or decision.get("timingPrecision") is not None
    ]
    require(
        not timed_decisions or reel_name is not None,
        "timed pronunciation decisions require a listening reel",
    )
    if timed_decisions:
        for index, decision in enumerate(decisions):
            for field in ("chapterRelativeAudioRange", "bookRelativeAudioRange"):
                audio_range = decision.get(field)
                if audio_range is not None:
                    require(
                        audio_range["end"] <= audiobook_duration,
                        f"decisions[{index}].{field} exceeds audiobook duration",
                    )
    if reel_name is None:
        require(
            not reel_path.exists() and not reel_path.is_symlink(),
            "unlisted listening reel is present",
        )
    else:
        require(
            reel_path.is_file() and not reel_path.is_symlink(),
            "listed listening reel is missing, a symlink, or not a file",
        )
        expected_reel_sha256 = require_sha256(reel_sha256, "listeningReelSHA256")
        require(
            file_sha256(reel_path) == expected_reel_sha256,
            "listeningReelSHA256 does not match exact sibling reel bytes",
        )
        require(
            any(
                decision.get("chapterRelativeAudioRange") is not None
                and decision.get("bookRelativeAudioRange") is not None
                and decision.get("timingPrecision") is not None
                for decision in decisions
            ),
            "listed listening reel requires an eligible timed pronunciation decision",
        )
        media_duration(reel_path)


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
