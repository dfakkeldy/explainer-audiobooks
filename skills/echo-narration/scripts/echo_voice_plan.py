#!/usr/bin/env python3
"""Canonicalize and validate governed Echo chapter-voice assignments."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from collections.abc import Sequence


VOICE_IDS = frozenset(
    {
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
)
ASSIGNMENT_PATTERN = re.compile(r"([1-9][0-9]*)=([a-z]+_[a-z]+)\Z")


class VoicePlanError(ValueError):
    """The requested chapter-voice plan is not canonical and safe."""


def parse_assignments(values: Sequence[str]) -> dict[int, str]:
    assignments: dict[int, str] = {}
    for value in values:
        match = ASSIGNMENT_PATTERN.fullmatch(value)
        if match is None:
            raise VoicePlanError(
                f"chapter voice must use N=voice_id with a positive chapter: {value}"
            )
        chapter = int(match.group(1))
        voice = match.group(2)
        if voice not in VOICE_IDS:
            raise VoicePlanError(f"unknown Echo voice: {voice}")
        if chapter in assignments:
            raise VoicePlanError(f"duplicate chapter voice assignment: {chapter}")
        assignments[chapter] = voice
    return assignments


def canonical_assignments(assignments: dict[int, str]) -> tuple[str, ...]:
    return tuple(
        f"{chapter}={assignments[chapter]}" for chapter in sorted(assignments)
    )


def voice_plan(default_voice: str, values: Sequence[str]) -> dict[str, object]:
    if default_voice not in VOICE_IDS:
        raise VoicePlanError(f"unknown Echo default voice: {default_voice}")
    assignments = parse_assignments(values)
    canonical = canonical_assignments(assignments)
    framed = "\n".join((f"default={default_voice}", *canonical)) + "\n"
    plan_hash = hashlib.sha256(framed.encode("utf-8")).hexdigest()
    plan_id = default_voice if not canonical else f"plan-{plan_hash[:12]}"
    return {
        "defaultVoice": default_voice,
        "chapterVoices": assignments,
        "canonicalAssignments": canonical,
        "voicePlanSHA256": plan_hash,
        "voicePlanID": plan_id,
    }


def effective_voice(
    default_voice: str, assignments: dict[int, str], display_chapter: int
) -> str:
    if display_chapter < 1:
        raise VoicePlanError("display chapter must be positive")
    return assignments.get(display_chapter, default_voice)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    root.add_argument("--default-voice", required=True)
    root.add_argument("--chapter-voice", action="append", default=[])
    root.add_argument("--format", choices=("env0", "lines"), default="lines")
    return root


def main(arguments: list[str]) -> int:
    options = parser().parse_args(arguments)
    try:
        plan = voice_plan(options.default_voice, options.chapter_voice)
    except VoicePlanError as error:
        print(f"echo_voice_plan: {error}", file=sys.stderr)
        return 64
    records = (
        ("VOICE", plan["defaultVoice"]),
        (
            "CHAPTER_VOICES_CANONICAL",
            ",".join(plan["canonicalAssignments"]),
        ),
        ("VOICE_PLAN_SHA256", plan["voicePlanSHA256"]),
        ("VOICE_PLAN_ID", plan["voicePlanID"]),
    )
    if options.format == "env0":
        sys.stdout.write("\0".join(component for record in records for component in record))
        sys.stdout.write("\0")
    else:
        sys.stdout.write("\n".join(f"{key}={value}" for key, value in records))
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
