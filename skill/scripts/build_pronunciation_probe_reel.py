#!/usr/bin/env python3
"""Build a listening reel from hash-bound governed partial chapter captures."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
CONTEXT_SECONDS = 1.25


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
        for anchor in anchors:
            if isinstance(anchor, dict) and isinstance(anchor.get("words"), list):
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
                "pronunciationDecisions": decisions,
            }
        )
    if not captures:
        raise ValueError(f"no governed partial chapter captures found in {work_dir}")
    return sorted(captures, key=lambda capture: capture["chapterIndex"])


def find_clips(forms: list[tuple[str, str]], captures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    clips: list[dict[str, Any]] = []
    reel_cursor = 0.0
    for term, form in forms:
        wanted = normalized_word(form)
        match: tuple[dict[str, Any], dict[str, Any], str] | None = None
        for capture in captures:
            for word in capture["words"]:
                if normalized_word(str(word.get("word", ""))) == wanted:
                    match = (capture, word, "exactWord")
                    break
            if match is not None:
                break
        if match is None:
            for capture in captures:
                for decision in capture["pronunciationDecisions"]:
                    decision_word = decision.get("normalizedWord") or decision.get("sourceWord")
                    if normalized_word(str(decision_word or "")) == wanted:
                        match = (capture, decision, "pronunciationDecision")
                        break
                if match is not None:
                    break
        if match is None:
            raise ValueError(f"missing timed pronunciation form: {form}")
        capture, timing, timing_source = match
        if timing_source == "exactWord":
            start = require_time(timing.get("start"), f"{form}.start")
            end = require_time(timing.get("end"), f"{form}.end")
        else:
            audio_range = timing.get("chapterRelativeAudioRange")
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
            clips[-1]["timingPrecision"] = timing.get("timingPrecision")
            clips[-1]["ruleID"] = timing.get("ruleID")
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


def build_reel(run_root: Path, work_dir: Path, out: Path, evidence_out: Path) -> dict[str, Any]:
    run_root = run_root.resolve()
    work_dir = work_dir.resolve()
    plan_path = run_root / "research" / "pronunciation-plan.json"
    plan = load_json(plan_path, "pronunciation plan")
    forms = planned_forms(plan)
    captures = load_captures(work_dir)
    clips = find_clips(forms, captures)
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
    args = parser.parse_args()
    evidence = build_reel(args.run_root, args.work_dir, args.out, args.evidence_out)
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
