#!/usr/bin/env python3
"""Canonicalize and validate governed Echo chapter-voice assignments."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path


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


RESOLVER_KEYS = frozenset(
    {
        "blockCount",
        "defaultVoice",
        "sourceEPUBSHA256",
        "voicePlanID",
        "voicePlanSHA256",
    }
)


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise VoicePlanError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def require_regular_canonical(path: Path, label: str, *, executable: bool = False) -> None:
    if not path.is_absolute():
        raise VoicePlanError(f"{label} must be an absolute path: {path}")
    if path.is_symlink() or path.resolve(strict=False) != path:
        raise VoicePlanError(f"{label} must be canonical and not a symlink: {path}")
    try:
        mode = path.stat().st_mode
    except FileNotFoundError as error:
        raise VoicePlanError(f"{label} is missing: {path}") from error
    if not stat.S_ISREG(mode):
        raise VoicePlanError(f"{label} must be a regular file: {path}")
    if executable and not os.access(path, os.X_OK):
        raise VoicePlanError(f"{label} is not executable: {path}")


def read_authored_plan(plan: Path) -> bytes:
    require_regular_canonical(plan, "voice plan")
    try:
        payload = json.loads(plan.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise VoicePlanError(f"voice plan is not valid UTF-8 JSON: {plan}") from error
    if not isinstance(payload, dict):
        raise VoicePlanError("voice plan JSON root must be an object")
    return (json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def safe_environment() -> dict[str, str]:
    environment = {"PATH": os.environ.get("PATH", "/usr/bin:/bin")}
    if "ECHO_RESOURCE_DIR" in os.environ:
        environment["ECHO_RESOURCE_DIR"] = os.environ["ECHO_RESOURCE_DIR"]
    return environment


def validate_resolver_receipt(raw: bytes, epub: Path) -> dict[str, object]:
    if len(raw) > 64 * 1024:
        raise VoicePlanError("Echo voice-plan resolver stdout exceeds 64 KiB")
    try:
        payload = json.loads(raw.decode("utf-8"), object_pairs_hook=reject_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError, VoicePlanError) as error:
        raise VoicePlanError("Echo voice-plan resolver returned invalid JSON") from error
    if not isinstance(payload, dict) or set(payload) != RESOLVER_KEYS:
        raise VoicePlanError("Echo voice-plan resolver receipt has unexpected keys")
    if type(payload["blockCount"]) is not int or payload["blockCount"] <= 0:
        raise VoicePlanError("Echo voice-plan resolver blockCount must be positive")
    default_voice = payload["defaultVoice"]
    if not isinstance(default_voice, str) or default_voice not in VOICE_IDS:
        raise VoicePlanError("Echo voice-plan resolver returned an unknown default voice")
    source = payload["sourceEPUBSHA256"]
    plan_sha = payload["voicePlanSHA256"]
    plan_id = payload["voicePlanID"]
    if not isinstance(source, str) or re.fullmatch(r"[0-9a-f]{64}", source) is None:
        raise VoicePlanError("Echo voice-plan resolver source EPUB SHA-256 is invalid")
    if source != hashlib.sha256(epub.read_bytes()).hexdigest():
        raise VoicePlanError("Echo voice-plan resolver source EPUB SHA-256 differs")
    if not isinstance(plan_sha, str) or re.fullmatch(r"[0-9a-f]{64}", plan_sha) is None:
        raise VoicePlanError("Echo voice-plan resolver SHA-256 is invalid")
    if not isinstance(plan_id, str) or re.fullmatch(r"plan-[0-9a-f]{12}", plan_id) is None:
        raise VoicePlanError("Echo voice-plan resolver ID is invalid")
    if plan_id != f"plan-{plan_sha[:12]}":
        raise VoicePlanError("Echo voice-plan resolver ID does not bind its SHA-256")
    compact = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    normalized = raw[:-1] if raw.endswith(b"\n") else raw
    if normalized != compact:
        raise VoicePlanError("Echo voice-plan resolver receipt is not compact canonical JSON")
    return payload


def resolve_block_plan_bytes(echo_cli: Path, epub: Path, plan: Path) -> tuple[dict[str, object], bytes]:
    """Resolve through Echo and retain its exact receipt bytes for sealing."""
    require_regular_canonical(echo_cli, "Echo CLI", executable=True)
    require_regular_canonical(epub, "EPUB")
    require_regular_canonical(plan, "voice plan")
    result = subprocess.run(
        [str(echo_cli), "resolve-voice-plan", "--epub", str(epub), "--voice-plan", str(plan)],
        check=False,
        capture_output=True,
        text=False,
        env=safe_environment(),
    )
    if result.returncode != 0:
        raise VoicePlanError(f"Echo voice-plan resolver failed with status {result.returncode}")
    if result.stderr:
        raise VoicePlanError("Echo voice-plan resolver wrote stderr on success")
    return validate_resolver_receipt(result.stdout, epub), result.stdout


def resolve_block_plan(echo_cli: Path, epub: Path, plan: Path) -> dict[str, object]:
    """Ask the installed Echo CLI to validate and resolve one authored block plan."""
    return resolve_block_plan_bytes(echo_cli, epub, plan)[0]


def immutable_write(path: Path, content: bytes) -> None:
    if not path.is_absolute() or path.parent.is_symlink() or not path.parent.is_dir():
        raise VoicePlanError(f"immutable destination parent is unsafe: {path}")
    if path.is_symlink():
        raise VoicePlanError(f"immutable destination must not be a symlink: {path}")
    helper = Path(__file__).with_name("echo_pronunciation_state.py")
    result = subprocess.run(
        [sys.executable, str(helper), "immutable-file", str(path)],
        input=content,
        check=False,
        capture_output=True,
        text=False,
        env=safe_environment(),
    )
    if result.returncode != 0:
        raise VoicePlanError(f"could not immutably write: {path}")


def seal_block_plan(
    echo_cli: Path, epub: Path, plan: Path, canonical_plan: Path, resolution: Path
) -> dict[str, object]:
    canonical = read_authored_plan(plan)
    initial, _ = resolve_block_plan_bytes(echo_cli, epub, plan)
    if canonical_plan.exists():
        require_regular_canonical(canonical_plan, "canonical voice plan")
        sealed, sealed_bytes = resolve_block_plan_bytes(echo_cli, epub, canonical_plan)
        if sealed != initial:
            raise VoicePlanError("existing canonical voice plan resolves differently")
    else:
        immutable_write(canonical_plan, canonical)
        sealed, sealed_bytes = resolve_block_plan_bytes(echo_cli, epub, canonical_plan)
        if sealed != initial:
            raise VoicePlanError("sealed canonical voice plan resolves differently")
    resolution_bytes = sealed_bytes.rstrip(b"\n") + b"\n"
    immutable_write(resolution, resolution_bytes)
    return {
        **sealed,
        "canonicalPlanPath": str(canonical_plan),
        "canonicalPlanSHA256": hashlib.sha256(canonical_plan.read_bytes()).hexdigest(),
        "resolutionPath": str(resolution),
        "resolutionSHA256": hashlib.sha256(resolution.read_bytes()).hexdigest(),
    }


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
    root.add_argument("--default-voice")
    root.add_argument("--chapter-voice", action="append", default=[])
    root.add_argument("--echo-cli", type=Path)
    root.add_argument("--epub", type=Path)
    root.add_argument("--voice-plan", type=Path)
    root.add_argument("--canonical-plan", type=Path)
    root.add_argument("--resolution", type=Path)
    root.add_argument("--format", choices=("env0", "lines"), default="lines")
    return root


def main(arguments: list[str]) -> int:
    options = parser().parse_args(arguments)
    try:
        block_options = (
            options.echo_cli,
            options.epub,
            options.voice_plan,
            options.canonical_plan,
            options.resolution,
        )
        if any(value is not None for value in block_options):
            if not all(value is not None for value in block_options) or options.default_voice is not None or options.chapter_voice:
                raise VoicePlanError("block mode requires exactly Echo, EPUB, plan, canonical, and resolution paths")
            plan = seal_block_plan(*block_options)
            records = (
                ("VOICE", plan["defaultVoice"]),
                ("CHAPTER_VOICES_CANONICAL", ""),
                ("VOICE_PLAN_MODE", "block"),
                ("VOICE_PLAN_SHA256", plan["voicePlanSHA256"]),
                ("VOICE_PLAN_ID", plan["voicePlanID"]),
                ("VOICE_PLAN_BLOCK_COUNT", str(plan["blockCount"])),
                ("VOICE_PLAN_CANONICAL_PATH", plan["canonicalPlanPath"]),
                ("VOICE_PLAN_CANONICAL_SHA256", plan["canonicalPlanSHA256"]),
                ("VOICE_PLAN_RESOLUTION_PATH", plan["resolutionPath"]),
                ("VOICE_PLAN_RESOLUTION_SHA256", plan["resolutionSHA256"]),
            )
        else:
            if options.default_voice is None:
                raise VoicePlanError("--default-voice is required in chapter mode")
            plan = voice_plan(options.default_voice, options.chapter_voice)
            records = (
                ("VOICE", plan["defaultVoice"]),
                ("CHAPTER_VOICES_CANONICAL", ",".join(plan["canonicalAssignments"])),
                ("VOICE_PLAN_SHA256", plan["voicePlanSHA256"]),
                ("VOICE_PLAN_ID", plan["voicePlanID"]),
            )
    except VoicePlanError as error:
        print(f"echo_voice_plan: {error}", file=sys.stderr)
        return 64
    if options.format == "env0":
        sys.stdout.write("\0".join(component for record in records for component in record))
        sys.stdout.write("\0")
    else:
        sys.stdout.write("\n".join(f"{key}={value}" for key, value in records))
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
