#!/usr/bin/env python3
"""Build a listening reel from hash-bound governed partial chapter captures."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import math
import re
import sqlite3
import subprocess
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
CONTEXT_SECONDS = 1.25
SOURCE_NEIGHBOR_WORDS = 2
MAX_INFERRED_GAP_SECONDS = 5.0
MAX_UNALIGNED_SPAN_SECONDS = 60.0


def sha256_file(path: Path) -> str:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"missing {label}: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"invalid {label}: {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def normalized_word(value: str) -> str:
    return re.sub(r"^[^\w]+|[^\w]+$", "", value, flags=re.UNICODE).casefold()


def source_words(value: str) -> list[str]:
    return [
        normalized_word(word)
        for word in re.findall(r"\w+(?:[-’'][\w]+)*", value, flags=re.UNICODE)
    ]


def require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def require_time(value: Any, field: str) -> float:
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError(f"{field} word timing must be finite and nonnegative")
    return float(value)


def media_duration(path: Path) -> float:
    process = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if process.returncode != 0:
        raise ValueError(f"ffprobe could not read media: {path}")
    try:
        duration = float(process.stdout.strip())
    except ValueError as error:
        raise ValueError(f"ffprobe returned invalid duration for {path}") from error
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError(f"media duration must be positive: {path}")
    return duration


def planned_forms(plan: dict[str, Any]) -> list[tuple[str, str]]:
    if plan.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError(f"pronunciation plan schemaVersion must be {SCHEMA_VERSION}")
    terms = plan.get("terms")
    if not isinstance(terms, list) or not terms:
        raise ValueError("pronunciation plan terms must be a non-empty list")
    result: list[tuple[str, str]] = []
    for index, entry in enumerate(terms):
        if not isinstance(entry, dict):
            raise ValueError(f"terms[{index}] must be an object")
        if entry.get("required") is not True:
            continue
        term = require_string(entry.get("term"), f"terms[{index}].term")
        result.append((term, term))
        variants = entry.get("variants")
        if not isinstance(variants, list):
            raise ValueError(f"terms[{index}].variants must be a list")
        for variant_index, variant in enumerate(variants):
            result.append(
                (term, require_string(variant, f"terms[{index}].variants[{variant_index}]"))
            )
    if not result:
        raise ValueError("pronunciation plan contains no required terms")
    return result


def expected_chapter_indexes(plan: dict[str, Any]) -> dict[str, set[int]]:
    result: dict[str, set[int]] = {}
    for entry in plan.get("terms", []):
        if not isinstance(entry, dict) or entry.get("required") is not True:
            continue
        term = require_string(entry.get("term"), "term")
        indexes: set[int] = set()
        for chapter in entry.get("expectedChapters", []):
            if not isinstance(chapter, str):
                continue
            match = re.fullmatch(r"ch(\d+)\.md", chapter)
            if match is not None:
                indexes.add(int(match.group(1)) - 1)
        result[normalized_word(term)] = indexes
    return result


def load_chapter_sources(run_root: Path) -> dict[int, list[str]]:
    result: dict[int, list[str]] = {}
    for chapter in sorted((run_root / "chapters").glob("ch*.md")):
        match = re.fullmatch(r"ch(\d+)\.md", chapter.name)
        if match is not None:
            result[int(match.group(1)) - 1] = source_words(
                chapter.read_text(encoding="utf-8")
            )
    return result


def source_neighbor_timing(
    form: str,
    capture: dict[str, Any],
    chapter_source: list[str],
) -> dict[str, Any] | None:
    wanted = source_words(form)
    if not wanted:
        return None
    timed_words = capture["words"]
    timed = [normalized_word(str(word.get("word", ""))) for word in timed_words]
    candidates: list[tuple[float, dict[str, Any]]] = []
    for source_index in range(len(chapter_source) - len(wanted) + 1):
        if chapter_source[source_index : source_index + len(wanted)] != wanted:
            continue
        left = chapter_source[max(0, source_index - SOURCE_NEIGHBOR_WORDS) : source_index]
        right_start = source_index + len(wanted)
        right = chapter_source[right_start : right_start + SOURCE_NEIGHBOR_WORDS]
        if not left or not right:
            continue
        for timed_index in range(len(timed) - len(left) - len(right) + 1):
            left_end = timed_index + len(left)
            right_end = left_end + len(right)
            if timed[timed_index:left_end] != left or timed[left_end:right_end] != right:
                continue
            left_word = timed_words[left_end - 1]
            right_word = timed_words[left_end]
            start = require_time(left_word.get("end"), f"{form}.neighborStart")
            end = require_time(right_word.get("start"), f"{form}.neighborEnd")
            gap = end - start
            if gap <= 0 or gap > MAX_INFERRED_GAP_SECONDS:
                continue
            candidates.append(
                (
                    gap,
                    {
                        "start": start,
                        "end": end,
                        "leftContextWords": left,
                        "rightContextWords": right,
                    },
                )
            )
    if not candidates:
        return None
    return min(candidates, key=lambda candidate: candidate[0])[1]


def source_span_timing(
    form: str,
    capture: dict[str, Any],
    chapter_source: list[str],
) -> dict[str, Any] | None:
    wanted = source_words(form)
    if not wanted:
        return None
    timed_words = capture["words"]
    timed = [normalized_word(str(word.get("word", ""))) for word in timed_words]
    candidates: list[tuple[float, dict[str, Any]]] = []
    opcodes = difflib.SequenceMatcher(
        None,
        chapter_source,
        timed,
        autojunk=False,
    ).get_opcodes()
    for tag, source_start, source_end, timed_start, timed_end in opcodes:
        if tag != "delete" or timed_start != timed_end:
            continue
        if source_start == 0 or source_end >= len(chapter_source):
            continue
        if timed_start == 0 or timed_start >= len(timed_words):
            continue
        deleted = chapter_source[source_start:source_end]
        if not any(
            deleted[index : index + len(wanted)] == wanted
            for index in range(len(deleted) - len(wanted) + 1)
        ):
            continue
        left_source = chapter_source[source_start - 1]
        right_source = chapter_source[source_end]
        if timed[timed_start - 1] != left_source or timed[timed_start] != right_source:
            continue
        left_word = timed_words[timed_start - 1]
        right_word = timed_words[timed_start]
        start = require_time(left_word.get("end"), f"{form}.spanStart")
        end = require_time(right_word.get("start"), f"{form}.spanEnd")
        gap = end - start
        if gap <= 0 or gap > MAX_UNALIGNED_SPAN_SECONDS:
            continue
        candidates.append(
            (
                gap,
                {
                    "start": start,
                    "end": end,
                    "leftContextWords": [left_source],
                    "rightContextWords": [right_source],
                    "unalignedSourceWordCount": source_end - source_start,
                },
            )
        )
    if not candidates:
        return None
    return min(candidates, key=lambda candidate: candidate[0])[1]


def load_captures(work_dir: Path) -> list[dict[str, Any]]:
    captures: list[dict[str, Any]] = []
    for anchor_path in sorted(work_dir.glob(".anchors-ch*.json")):
        payload = load_json(anchor_path, "chapter anchor capture")
        identity = payload.get("identity")
        if not isinstance(identity, dict):
            raise ValueError(f"anchor identity must be an object: {anchor_path}")
        audio_name = require_string(identity.get("audioFileName"), "identity.audioFileName")
        if Path(audio_name).name != audio_name:
            raise ValueError("identity.audioFileName must be a basename")
        audio_path = work_dir / audio_name
        if not audio_path.is_file():
            raise ValueError(f"capture audio is missing: {audio_path}")
        expected_sha = require_string(identity.get("audioSHA256"), "identity.audioSHA256")
        actual_sha = sha256_file(audio_path)
        if expected_sha != actual_sha:
            raise ValueError(f"capture SHA-256 does not match identity: {audio_path}")
        chapter_index = identity.get("chapterIndex")
        if type(chapter_index) is not int or chapter_index < 0:
            raise ValueError("identity.chapterIndex must be a nonnegative integer")
        declared_duration = payload.get("duration")
        if type(declared_duration) not in (int, float) or declared_duration <= 0:
            raise ValueError(f"capture duration must be positive: {anchor_path}")
        duration = media_duration(audio_path)
        words: list[dict[str, Any]] = []
        anchors = payload.get("anchors")
        if not isinstance(anchors, list):
            raise ValueError(f"anchors must be a list: {anchor_path}")
        anchor_suffixes: list[str] = []
        for anchor in anchors:
            if not isinstance(anchor, dict):
                continue
            suffix = anchor.get("suffix")
            if isinstance(suffix, str) and suffix:
                anchor_suffixes.append(suffix)
            if isinstance(anchor.get("words"), list):
                words.extend(word for word in anchor["words"] if isinstance(word, dict))
        pronunciation_evidence = payload.get("pronunciationEvidence")
        decisions: list[dict[str, Any]] = []
        if isinstance(pronunciation_evidence, dict) and isinstance(
            pronunciation_evidence.get("decisions"), list
        ):
            decisions = [
                decision
                for decision in pronunciation_evidence["decisions"]
                if isinstance(decision, dict)
            ]
        captures.append(
            {
                "anchorPath": anchor_path,
                "audioPath": audio_path,
                "audioSHA256": actual_sha,
                "chapterIndex": chapter_index,
                "duration": duration,
                "words": words,
                "anchorSuffixes": anchor_suffixes,
                "pronunciationDecisions": decisions,
            }
        )
    if not captures:
        raise ValueError(f"no governed partial chapter captures found in {work_dir}")
    return sorted(captures, key=lambda capture: capture["chapterIndex"])


def add_database_words(captures: list[dict[str, Any]], timing_db: Path) -> str:
    if not timing_db.is_file():
        raise ValueError(f"missing narration timing database: {timing_db}")
    suffix_to_capture = {
        suffix: capture
        for capture in captures
        for suffix in capture["anchorSuffixes"]
    }
    snapshot: list[dict[str, Any]] = []
    try:
        with sqlite3.connect(f"file:{timing_db.resolve()}?mode=ro", uri=True) as database:
            rows = database.execute(
                """
                SELECT e.id, w.word_index, w.word, w.audio_start_time,
                       w.audio_end_time, w.source
                FROM word_timing AS w
                JOIN epub_block AS e ON e.id = w.epub_block_id
                WHERE w.source IN ('synthesis', 'synthesized')
                ORDER BY e.spine_index, e.block_index, w.word_index
                """
            )
            for block_id, word_index, word, start, end, source in rows:
                match = re.search(r"(s[0-9]+-b[0-9]+)$", str(block_id))
                if match is None:
                    continue
                capture = suffix_to_capture.get(match.group(1))
                if capture is None:
                    continue
                timing = {
                    "word": word,
                    "start": start,
                    "end": end,
                    "_timingSource": "narrationDatabaseWord",
                }
                capture["words"].append(timing)
                snapshot.append(
                    {
                        "suffix": match.group(1),
                        "wordIndex": word_index,
                        "word": word,
                        "start": start,
                        "end": end,
                        "source": source,
                    }
                )
    except sqlite3.Error as error:
        raise ValueError(f"invalid narration timing database: {timing_db}: {error}") from error
    if not snapshot:
        raise ValueError(f"narration timing database has no words for captured blocks: {timing_db}")
    encoded = json.dumps(snapshot, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def find_clips(
    forms: list[tuple[str, str]],
    captures: list[dict[str, Any]],
    chapter_sources: dict[int, list[str]],
    expected_indexes: dict[str, set[int]],
) -> list[dict[str, Any]]:
    clips: list[dict[str, Any]] = []
    reel_cursor = 0.0
    for term, form in forms:
        wanted = [normalized_word(part) for part in form.split()]
        match: tuple[dict[str, Any], dict[str, Any], dict[str, Any], str] | None = None
        for capture in captures:
            words = capture["words"]
            for index in range(len(words) - len(wanted) + 1):
                actual = [
                    normalized_word(str(word.get("word", "")))
                    for word in words[index : index + len(wanted)]
                ]
                if actual == wanted:
                    timing_source = str(words[index].get("_timingSource", "exactWord"))
                    if any(
                        str(word.get("_timingSource", "exactWord")) != timing_source
                        for word in words[index : index + len(wanted)]
                    ):
                        timing_source = "exactWord"
                    match = (
                        capture,
                        words[index],
                        words[index + len(wanted) - 1],
                        timing_source,
                    )
                    break
            if match is not None:
                break
        if match is None:
            for capture in captures:
                for decision in capture["pronunciationDecisions"]:
                    decision_word = decision.get("normalizedWord") or decision.get("sourceWord")
                    if normalized_word(str(decision_word or "")) == normalized_word(form):
                        match = (capture, decision, decision, "pronunciationDecision")
                        break
                if match is not None:
                    break
        if match is None:
            allowed = expected_indexes.get(normalized_word(term), set())
            for capture in captures:
                chapter_index = capture["chapterIndex"]
                if chapter_index not in allowed or chapter_index not in chapter_sources:
                    continue
                inferred = source_neighbor_timing(
                    form,
                    capture,
                    chapter_sources[chapter_index],
                )
                if inferred is not None:
                    match = (
                        capture,
                        inferred,
                        inferred,
                        "sourceNeighborInference",
                    )
                    break
        if match is None:
            allowed = expected_indexes.get(normalized_word(term), set())
            for capture in captures:
                chapter_index = capture["chapterIndex"]
                if chapter_index not in allowed or chapter_index not in chapter_sources:
                    continue
                inferred = source_span_timing(
                    form,
                    capture,
                    chapter_sources[chapter_index],
                )
                if inferred is not None:
                    match = (
                        capture,
                        inferred,
                        inferred,
                        "sourceSpanInference",
                    )
                    break
        if match is None:
            raise ValueError(f"missing timed pronunciation form: {form}")
        capture, first_timing, last_timing, timing_source = match
        if timing_source in {
            "exactWord",
            "narrationDatabaseWord",
            "sourceNeighborInference",
            "sourceSpanInference",
        }:
            start = require_time(first_timing.get("start"), f"{form}.start")
            end = require_time(last_timing.get("end"), f"{form}.end")
        else:
            audio_range = first_timing.get("chapterRelativeAudioRange")
            if not isinstance(audio_range, dict):
                raise ValueError(f"invalid pronunciation decision timing for {form}")
            start = require_time(audio_range.get("start"), f"{form}.start")
            end = require_time(audio_range.get("end"), f"{form}.end")
        if end <= start or end > capture["duration"]:
            raise ValueError(f"invalid word timing for {form}")
        clip_start = max(0.0, start - CONTEXT_SECONDS)
        clip_end = min(capture["duration"], end + CONTEXT_SECONDS)
        clip_duration = clip_end - clip_start
        clips.append(
            {
                "term": term,
                "variantHeard": form,
                "chapterIndex": capture["chapterIndex"],
                "captureFileName": capture["audioPath"].name,
                "captureSHA256": capture["audioSHA256"],
                "sourceStart": clip_start,
                "sourceEnd": clip_end,
                "reelStart": reel_cursor,
                "reelEnd": reel_cursor + clip_duration,
                "timingSource": timing_source,
                "_audioPath": capture["audioPath"],
            }
        )
        if timing_source == "pronunciationDecision":
            clips[-1]["timingPrecision"] = first_timing.get("timingPrecision")
            clips[-1]["ruleID"] = first_timing.get("ruleID")
        elif timing_source == "sourceNeighborInference":
            clips[-1]["timingPrecision"] = "adjacentSourceNeighbors"
            clips[-1]["leftContextWords"] = first_timing["leftContextWords"]
            clips[-1]["rightContextWords"] = first_timing["rightContextWords"]
        elif timing_source == "sourceSpanInference":
            clips[-1]["timingPrecision"] = "unalignedSourceSpan"
            clips[-1]["leftContextWords"] = first_timing["leftContextWords"]
            clips[-1]["rightContextWords"] = first_timing["rightContextWords"]
            clips[-1]["unalignedSourceWordCount"] = first_timing[
                "unalignedSourceWordCount"
            ]
        reel_cursor += clip_duration
    return clips


def render_reel(clips: list[dict[str, Any]], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    command = ["ffmpeg", "-v", "error", "-y"]
    for clip in clips:
        command.extend(["-i", str(clip["_audioPath"])])
    filters: list[str] = []
    labels: list[str] = []
    for index, clip in enumerate(clips):
        label = f"clip{index}"
        labels.append(f"[{label}]")
        filters.append(
            f"[{index}:a]atrim=start={clip['sourceStart']:.6f}:end={clip['sourceEnd']:.6f},"
            f"asetpts=PTS-STARTPTS[{label}]"
        )
    filters.append("".join(labels) + f"concat=n={len(clips)}:v=0:a=1[outa]")
    command.extend(
        [
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[outa]",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-f",
            "mp4",
            str(out),
        ]
    )
    process = subprocess.run(command, check=False, capture_output=True, text=True)
    if process.returncode != 0:
        raise ValueError(f"ffmpeg could not build pronunciation reel: {process.stderr.strip()}")
    media_duration(out)


def build_reel(
    run_root: Path,
    work_dir: Path,
    out: Path,
    evidence_out: Path,
    *,
    timing_db: Path | None = None,
) -> dict[str, Any]:
    run_root = run_root.resolve()
    work_dir = work_dir.resolve()
    plan_path = run_root / "research" / "pronunciation-plan.json"
    plan = load_json(plan_path, "pronunciation plan")
    forms = planned_forms(plan)
    expected_indexes = expected_chapter_indexes(plan)
    chapter_sources = load_chapter_sources(run_root)
    captures = load_captures(work_dir)
    timing_snapshot_sha256 = add_database_words(captures, timing_db) if timing_db else None
    clips = find_clips(forms, captures, chapter_sources, expected_indexes)
    render_reel(clips, out)
    public_clips = [{key: value for key, value in clip.items() if not key.startswith("_")} for clip in clips]
    unique_captures = {
        clip["captureFileName"]: clip["captureSHA256"] for clip in public_clips
    }
    evidence: dict[str, Any] = {
        "schemaVersion": SCHEMA_VERSION,
        "planSHA256": sha256_file(plan_path),
        "reelFileName": out.name,
        "reelSHA256": sha256_file(out),
        "captures": unique_captures,
        "clips": public_clips,
    }
    if timing_snapshot_sha256 is not None:
        evidence["timingSnapshotSHA256"] = timing_snapshot_sha256
    evidence_out.parent.mkdir(parents=True, exist_ok=True)
    temporary = evidence_out.with_suffix(evidence_out.suffix + ".tmp")
    temporary.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(evidence_out)
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--evidence-out", type=Path, required=True)
    parser.add_argument(
        "--timing-db",
        type=Path,
        help="Fallback Echo narration database when captures omit word arrays.",
    )
    args = parser.parse_args()
    evidence = build_reel(
        args.run_root,
        args.work_dir,
        args.out,
        args.evidence_out,
        timing_db=args.timing_db,
    )
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
