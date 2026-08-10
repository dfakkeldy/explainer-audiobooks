#!/usr/bin/env python3
"""Validate Echo's media-bound pronunciation acceptance manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import stat
import subprocess
import sys
import tempfile
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
SCHEMA_7_REQUIRED_FIELDS = {
    "schemaVersion",
    "renderVersion",
    "voice",
    "chapterVoices",
    "voicePlanSHA256",
    "blockVoices",
    "coverage",
    "legacyChapterIndexes",
    "audiobookFileName",
    "audiobookSHA256",
    "watchCounts",
    "decisions",
    "diagnostics",
}
SCHEMA_7_REEL_FIELDS = {"listeningReelFileName", "listeningReelSHA256"}
BLOCK_ID_PATTERN = re.compile(r"s[0-9]+-b[0-9]+\Z")
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


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    payload: dict[str, object] = {}
    for key, value in pairs:
        require(key not in payload, f"duplicate JSON key: {key}")
        payload[key] = value
    return payload


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


class StableMediaSnapshot:
    """A private copy whose bytes, hash, size, and duration stay bound together."""

    def __init__(self, path: Path, sha256: str, byte_count: int) -> None:
        self.path = path
        self.sha256 = sha256
        self.byte_count = byte_count


def require_canonical_explicit_path(path: Path, label: str) -> None:
    require(path.is_absolute(), f"--{label} must be an absolute path")
    try:
        resolved = path.resolve(strict=True)
    except OSError as error:
        raise AuditValidationError(
            f"explicit {label} is missing, a symlink, or not a file"
        ) from error
    require(
        resolved == path,
        f"explicit {label} must have canonical symlink-free ancestry",
    )
    ancestor = path.parent
    while ancestor != ancestor.parent:
        require(
            not ancestor.is_symlink(),
            f"explicit {label} must have canonical symlink-free ancestry",
        )
        ancestor = ancestor.parent


def open_regular_descriptor(path: Path, label: str) -> int:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise AuditValidationError(
            f"explicit {label} is missing, a symlink, or not a file"
        ) from error
    if not stat.S_ISREG(os.fstat(descriptor).st_mode):
        os.close(descriptor)
        raise AuditValidationError(
            f"explicit {label} is missing, a symlink, or not a file"
        )
    return descriptor


def stable_explicit_media_snapshot(path: Path, label: str) -> StableMediaSnapshot:
    """Copy one no-follow descriptor so ffprobe sees the exact hashed bytes.

    `ffprobe` consumes a pathname and cannot attest the descriptor it opens.  A
    private `mkstemp` copy is therefore the stable byte boundary: hashing and
    byte counting happen while copying the original descriptor, and duration is
    read only from that completed private copy.
    """

    require_canonical_explicit_path(path, label)
    descriptor = open_regular_descriptor(path, label)
    temporary_descriptor = -1
    temporary_path: Path | None = None
    try:
        temporary_descriptor, temporary_name = tempfile.mkstemp(
            prefix="echo-pronunciation-audit-",
            suffix=path.suffix or ".media",
        )
        temporary_path = Path(temporary_name)
        os.fchmod(temporary_descriptor, 0o600)
        digest = hashlib.sha256()
        byte_count = 0
        with os.fdopen(descriptor, "rb", closefd=True) as source:
            descriptor = -1
            with os.fdopen(temporary_descriptor, "wb", closefd=True) as destination:
                temporary_descriptor = -1
                while chunk := source.read(1_048_576):
                    digest.update(chunk)
                    byte_count += len(chunk)
                    destination.write(chunk)
                destination.flush()
                os.fsync(destination.fileno())
        require_canonical_explicit_path(path, label)
        return StableMediaSnapshot(temporary_path, digest.hexdigest(), byte_count)
    except Exception:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if temporary_descriptor >= 0:
            os.close(temporary_descriptor)


def require_explicit_media(path: Path | None, label: str) -> Path:
    require(path is not None, f"schema 7 requires --{label}")
    require_canonical_explicit_path(path, label)
    return path


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


def validate(
    audit_path: Path,
    *,
    audiobook: Path | None = None,
    reel: Path | None = None,
    voice_plan_sha256: str | None = None,
    block_count: int | None = None,
) -> None:
    try:
        raw_manifest = audit_path.read_text(encoding="utf-8")
        payload = json.loads(raw_manifest)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise AuditValidationError("manifest is not valid UTF-8 JSON") from error
    require(isinstance(payload, dict), "manifest root must be an object")
    schema_version = payload.get("schemaVersion")
    if schema_version == 7:
        try:
            payload = json.loads(
                raw_manifest,
                object_pairs_hook=reject_duplicate_keys,
            )
        except json.JSONDecodeError as error:
            raise AuditValidationError("manifest is not valid UTF-8 JSON") from error
        require(isinstance(payload, dict), "manifest root must be an object")
        schema_version = payload.get("schemaVersion")
    require(
        type(schema_version) is int and 2 <= schema_version <= 7,
        "schemaVersion must be between 2 and 7",
    )
    schema_7 = schema_version == 7
    if schema_7:
        exact_fields = SCHEMA_7_REQUIRED_FIELDS | (
            set(payload) & SCHEMA_7_REEL_FIELDS
        )
        require(
            set(payload) == exact_fields,
            "schema 7 manifest has unexpected top-level keys",
        )
        missing = sorted(SCHEMA_7_REQUIRED_FIELDS - payload.keys())
        require(not missing, f"schema 7 manifest missing fields: {missing}")
        require(
            ("listeningReelFileName" in payload)
            == ("listeningReelSHA256" in payload),
            "listeningReelFileName and listeningReelSHA256 must appear together",
        )
        audiobook_path = require_explicit_media(audiobook, "audiobook")
        require(
            voice_plan_sha256 is not None,
            "schema 7 requires --voice-plan-sha256",
        )
        require(
            block_count is not None,
            "schema 7 requires --block-count",
        )
        supplied_plan_sha = require_sha256(
            voice_plan_sha256, "--voice-plan-sha256"
        )
        require(
            type(block_count) is int and block_count > 0,
            "--block-count must be a positive integer",
        )
    else:
        missing = sorted(REQUIRED_FIELDS - payload.keys())
        require(not missing, f"manifest missing fields: {missing}")
        require(
            voice_plan_sha256 is None and block_count is None,
            "--voice-plan-sha256 and --block-count require schema 7",
        )
        require(
            audiobook is None and reel is None,
            "explicit media paths require schema 7",
        )
        audiobook_path = None
        supplied_plan_sha = None

    render_version = require_nonnegative_int(payload["renderVersion"], "renderVersion")
    require(render_version >= 12, "renderVersion must be at least 12")
    voice = require_nonempty_string(payload["voice"], "voice")
    chapter_voices: dict[str, str] = {}
    block_voices: dict[str, str] = {}
    if schema_version == 2:
        require(
            voice in {"am_michael", "am_puck"},
            "schema 2 voice must be am_michael or am_puck",
        )
    elif schema_7:
        require(payload["chapterVoices"] == {}, "schema 7 chapterVoices must be empty")
        require(
            payload["voicePlanSHA256"] == supplied_plan_sha,
            "schema 7 voicePlanSHA256 differs from --voice-plan-sha256",
        )
        raw_block_voices = payload["blockVoices"]
        require(isinstance(raw_block_voices, dict), "schema 7 blockVoices must be an object")
        require(
            len(raw_block_voices) == block_count,
            "schema 7 blockVoices count differs from --block-count",
        )
        for block_id, block_voice in raw_block_voices.items():
            require(
                isinstance(block_id, str)
                and BLOCK_ID_PATTERN.fullmatch(block_id) is not None,
                "schema 7 blockVoices keys must be canonical block IDs",
            )
            require(
                isinstance(block_voice, str) and block_voice in ALLOWED_VOICES,
                f"blockVoices.{block_id} is not a known Echo voice",
            )
            block_voices[block_id] = block_voice
        distinct_voices = set(block_voices.values())
        if len(distinct_voices) == 1:
            require(
                voice == next(iter(distinct_voices)),
                "schema 7 uniform voice disagrees with blockVoices",
            )
        else:
            require(
                voice == "mixed",
                "schema 7 multiple block voices require voice mixed",
            )
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
    if audiobook_path is None:
        audiobook_path = audit_path.parent / f"{stem}.m4b"
        require(
            audiobook_path.is_file() and not audiobook_path.is_symlink(),
            "listed audiobook is missing, a symlink, or not a file",
        )
        audiobook_binding = "exact sibling audiobook bytes"
    else:
        require(
            audiobook_path.name == payload["audiobookFileName"],
            "explicit audiobook filename does not match the audit manifest",
        )
        audiobook_binding = "exact explicit audiobook bytes"
    audiobook_sha256 = require_sha256(payload["audiobookSHA256"], "audiobookSHA256")
    if schema_7:
        audiobook_snapshot = stable_explicit_media_snapshot(
            audiobook_path, "audiobook"
        )
        try:
            require(
                audiobook_snapshot.sha256 == audiobook_sha256,
                f"audiobookSHA256 does not match {audiobook_binding}",
            )
            audiobook_duration = media_duration(audiobook_snapshot.path)
        finally:
            audiobook_snapshot.path.unlink(missing_ok=True)
    else:
        require(
            file_sha256(audiobook_path) == audiobook_sha256,
            f"audiobookSHA256 does not match {audiobook_binding}",
        )
        audiobook_duration = media_duration(audiobook_path)

    decisions = [
        validate_decision(decision, index)
        for index, decision in enumerate(payload["decisions"])
    ]
    if schema_7:
        for index, decision in enumerate(decisions):
            portable_block_id = BLOCK_ID_PATTERN.search(decision["blockID"])
            require(
                portable_block_id is not None
                and portable_block_id.group(0) in block_voices,
                f"decisions[{index}].blockID is absent from blockVoices",
            )
    elif schema_version >= 3:
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
    if schema_7:
        require(
            (reel is None) == (reel_name is None),
            "schema 7 --reel must appear exactly when the manifest lists a listening reel",
        )
        reel_path = require_explicit_media(reel, "reel") if reel_name is not None else None
        if reel_path is not None:
            require(
                reel_path.name == reel_name,
                "explicit reel filename does not match the audit manifest",
            )
    else:
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
        if not schema_7:
            require(
                not reel_path.exists() and not reel_path.is_symlink(),
                "unlisted listening reel is present",
            )
    else:
        require(reel_path is not None, "listed listening reel is missing")
        if not schema_7:
            require(
                reel_path.is_file() and not reel_path.is_symlink(),
                "listed listening reel is missing, a symlink, or not a file",
            )
        expected_reel_sha256 = require_sha256(reel_sha256, "listeningReelSHA256")
        if schema_7:
            reel_snapshot = stable_explicit_media_snapshot(reel_path, "reel")
            try:
                require(
                    reel_snapshot.sha256 == expected_reel_sha256,
                    "listeningReelSHA256 does not match exact explicit reel bytes",
                )
                media_duration(reel_snapshot.path)
            finally:
                reel_snapshot.path.unlink(missing_ok=True)
        else:
            require(
                file_sha256(reel_path) == expected_reel_sha256,
                "listeningReelSHA256 does not match exact sibling reel bytes",
            )
            media_duration(reel_path)
        require(
            any(
                decision.get("chapterRelativeAudioRange") is not None
                and decision.get("bookRelativeAudioRange") is not None
                and decision.get("timingPrecision") is not None
                for decision in decisions
            ),
            "listed listening reel requires an eligible timed pronunciation decision",
        )


def main(arguments: list[str]) -> int:
    parser = argparse.ArgumentParser(
        usage=(
            "validate_pronunciation_audit.py AUDIT_JSON "
            "[--audiobook ABSOLUTE_PATH [--reel ABSOLUTE_PATH] "
            "--voice-plan-sha256 SHA256 --block-count N]"
        )
    )
    parser.add_argument("audit_json", type=Path)
    parser.add_argument("--audiobook", type=Path)
    parser.add_argument("--reel", type=Path)
    parser.add_argument("--voice-plan-sha256")
    parser.add_argument("--block-count", type=int)
    try:
        options = parser.parse_args(arguments)
    except SystemExit as error:
        return int(error.code)
    try:
        validate(
            options.audit_json,
            audiobook=options.audiobook,
            reel=options.reel,
            voice_plan_sha256=options.voice_plan_sha256,
            block_count=options.block_count,
        )
    except (AuditValidationError, json.JSONDecodeError, OSError) as error:
        print(f"pronunciation_audit: {error}", file=sys.stderr)
        return 1
    print("pronunciation_audit: clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
