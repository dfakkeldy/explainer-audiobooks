#!/usr/bin/env python3
"""Validate a source-bound semantic voice cast before Echo resolves it."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import stat
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence


CAST_KEYS = frozenset(
    {
        "schemaVersion",
        "narrationMode",
        "source",
        "defaultRoleID",
        "roles",
        "groups",
        "authoredVoicePlan",
        "singleVoiceWaiver",
    }
)
SOURCE_KEYS = frozenset(
    {"epubFileName", "epubSHA256", "inventoryFileName", "inventorySHA256"}
)
ROLE_KEYS = frozenset({"roleID", "voiceID"})
GROUP_KEYS = frozenset({"groupID", "roleID", "blocks"})
AUTHORED_PLAN_KEYS = frozenset({"fileName", "sha256"})
WAIVER_KEYS = frozenset({"recordedIn", "reason"})
INVENTORY_KEYS = frozenset({"version", "source", "blocks"})
INVENTORY_SOURCE_KEYS = frozenset({"epubSHA256"})
PLAN_KEYS = frozenset(
    {"schemaVersion", "source", "defaultSpeakerID", "speakers", "assignments"}
)
PLAN_SOURCE_KEYS = frozenset({"epubSHA256"})
PLAN_SPEAKER_KEYS = frozenset({"id", "voiceID"})
PLAN_ASSIGNMENT_KEYS = frozenset({"speakerID", "blocks"})
ROLES = ("guide", "memory", "field", "coach")
SECONDARY_ROLES = frozenset({"memory", "field", "coach"})
BLOCK_ID = re.compile(r"s[0-9]+-b[0-9]+\Z")
GROUP_ID = re.compile(r"(memory|field|coach)-[0-9]{3}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


class SemanticVoiceCastError(ValueError):
    """The semantic cast is not a closed, source-bound Echo handoff."""


@dataclass(frozen=True)
class ValidationResult:
    voice_plan: Path
    paragraph_block_count: int
    guide_block_count: int
    role_block_counts: dict[str, int]


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise SemanticVoiceCastError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def require_regular_canonical(path: Path, label: str) -> None:
    if not path.is_absolute() or path.is_symlink() or path.resolve(strict=False) != path:
        raise SemanticVoiceCastError(f"{label} must be canonical and not a symlink: {path}")
    try:
        mode = path.stat().st_mode
    except FileNotFoundError as error:
        raise SemanticVoiceCastError(f"{label} is missing: {path}") from error
    if not stat.S_ISREG(mode):
        raise SemanticVoiceCastError(f"{label} must be a regular file: {path}")


def read_closed_json(path: Path, label: str, expected_keys: frozenset[str]) -> dict[str, object]:
    require_regular_canonical(path, label)
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SemanticVoiceCastError(f"{label} is not valid UTF-8 JSON") from error
    if not isinstance(value, dict) or set(value) != expected_keys:
        raise SemanticVoiceCastError(f"{label} has unexpected keys")
    return value


def canonical_json(payload: object) -> bytes:
    return (json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_voice_ids() -> frozenset[str]:
    source = Path(__file__).resolve().parents[2] / "skills" / "echo-narration" / "scripts" / "echo_voice_plan.py"
    spec = importlib.util.spec_from_file_location("semantic_voice_cast_echo_voice_plan", source)
    if spec is None or spec.loader is None:
        raise SemanticVoiceCastError("could not load Echo voice catalog")
    echo_voice_plan = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(echo_voice_plan)
    voice_ids = getattr(echo_voice_plan, "VOICE_IDS", None)
    if not isinstance(voice_ids, frozenset) or not all(isinstance(value, str) for value in voice_ids):
        raise SemanticVoiceCastError("Echo voice catalog is invalid")
    return voice_ids


VOICE_IDS = _load_voice_ids()


def _require_object(value: object, label: str, expected_keys: frozenset[str]) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != expected_keys:
        raise SemanticVoiceCastError(f"{label} has unexpected keys")
    return value


def _require_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise SemanticVoiceCastError(f"{label} must be nonempty text")
    return value


def _require_filename(value: object, label: str) -> str:
    filename = _require_string(value, label)
    if filename in {".", ".."} or "/" in filename or "\\" in filename or "\0" in filename:
        raise SemanticVoiceCastError(f"{label} must be a safe filename")
    return filename


def _require_sha256(value: object, label: str) -> str:
    if not isinstance(value, str) or SHA256.fullmatch(value) is None:
        raise SemanticVoiceCastError(f"{label} must be a lowercase SHA-256")
    return value


def _run_root(cast_path: Path) -> Path:
    suffix = Path("_production") / "narration" / "semantic-voice-cast.json"
    if tuple(cast_path.parts[-3:]) != tuple(suffix.parts):
        raise SemanticVoiceCastError("cast path must end in _production/narration/semantic-voice-cast.json")
    run_root = cast_path.parents[2]
    if run_root / suffix != cast_path:
        raise SemanticVoiceCastError("cast path does not have the required run-root layout")
    return run_root


def _validate_cast(cast: dict[str, object]) -> tuple[dict[str, object], list[dict[str, object]]]:
    if type(cast["schemaVersion"]) is not int or cast["schemaVersion"] != 1:
        raise SemanticVoiceCastError("cast schemaVersion must be 1")
    if cast["narrationMode"] != "semantic-block":
        raise SemanticVoiceCastError("cast narrationMode must be semantic-block")
    source = _require_object(cast["source"], "cast source", SOURCE_KEYS)
    _require_filename(source["epubFileName"], "source EPUB filename")
    _require_sha256(source["epubSHA256"], "source EPUB hash")
    _require_filename(source["inventoryFileName"], "source inventory filename")
    _require_sha256(source["inventorySHA256"], "source inventory hash")
    if cast["defaultRoleID"] != "guide":
        raise SemanticVoiceCastError("cast defaultRoleID must be guide")

    roles = cast["roles"]
    if not isinstance(roles, list) or not 1 <= len(roles) <= len(ROLES):
        raise SemanticVoiceCastError("cast roles must contain one to four entries")
    for index, value in enumerate(roles):
        role = _require_object(value, f"cast role {index}", ROLE_KEYS)
        if role["roleID"] not in ROLES:
            raise SemanticVoiceCastError(f"cast role {index} has an unknown roleID")
        voice = _require_string(role["voiceID"], f"cast role {index} voiceID")
        if voice not in VOICE_IDS:
            raise SemanticVoiceCastError(f"cast role {index} has an unknown Echo voice")

    groups = cast["groups"]
    if not isinstance(groups, list):
        raise SemanticVoiceCastError("cast groups must be an array")
    checked_groups: list[dict[str, object]] = []
    for index, value in enumerate(groups):
        group = _require_object(value, f"cast group {index}", GROUP_KEYS)
        group_id = _require_string(group["groupID"], f"cast group {index} groupID")
        if GROUP_ID.fullmatch(group_id) is None:
            raise SemanticVoiceCastError(f"cast group {index} groupID is invalid")
        if group["roleID"] not in SECONDARY_ROLES:
            raise SemanticVoiceCastError(f"cast group {index} roleID is invalid")
        blocks = group["blocks"]
        if not isinstance(blocks, list) or not 1 <= len(blocks) <= 4:
            raise SemanticVoiceCastError(f"cast group {index} must contain one to four blocks")
        for block in blocks:
            if not isinstance(block, str) or BLOCK_ID.fullmatch(block) is None:
                raise SemanticVoiceCastError(f"cast group {index} block ID is invalid")
        checked_groups.append(group)

    authored = _require_object(cast["authoredVoicePlan"], "authored voice plan", AUTHORED_PLAN_KEYS)
    _require_filename(authored["fileName"], "authored voice-plan filename")
    _require_sha256(authored["sha256"], "authored voice-plan hash")
    waiver = cast["singleVoiceWaiver"]
    if waiver is not None:
        waiver_data = _require_object(waiver, "singleVoiceWaiver", WAIVER_KEYS)
        _require_string(waiver_data["recordedIn"], "singleVoiceWaiver recordedIn")
        _require_string(waiver_data["reason"], "singleVoiceWaiver reason")
    return source, checked_groups


def _validate_inventory(inventory: dict[str, object], epub_hash: str) -> set[str]:
    if type(inventory["version"]) is not int or inventory["version"] != 1:
        raise SemanticVoiceCastError("inventory version must be 1")
    source = _require_object(inventory["source"], "inventory source", INVENTORY_SOURCE_KEYS)
    if _require_sha256(source["epubSHA256"], "inventory source EPUB hash") != epub_hash:
        raise SemanticVoiceCastError("inventory source EPUB hash differs")
    blocks = inventory["blocks"]
    if not isinstance(blocks, list):
        raise SemanticVoiceCastError("inventory blocks must be an array")
    ids: set[str] = set()
    sequence_indexes: set[int] = set()
    for index, value in enumerate(blocks):
        if not isinstance(value, dict):
            raise SemanticVoiceCastError(f"inventory block {index} must be an object")
        kind = value.get("kind")
        expected = {"id", "kind", "text", "chapterIndex", "sequenceIndex", "wordCount"}
        if kind == "image":
            expected.add("imagePath")
        if set(value) != expected:
            raise SemanticVoiceCastError(f"inventory block {index} has unexpected keys")
        block_id = value["id"]
        if not isinstance(block_id, str) or BLOCK_ID.fullmatch(block_id) is None or block_id in ids:
            raise SemanticVoiceCastError(f"inventory block {index} has a duplicate or invalid ID")
        ids.add(block_id)
        if kind not in {"heading", "paragraph", "sentence", "image", "code"}:
            raise SemanticVoiceCastError(f"inventory block {index} has an invalid kind")
        if not isinstance(value["text"], str):
            raise SemanticVoiceCastError(f"inventory block {index} text must be text")
        chapter = value["chapterIndex"]
        if chapter is not None and (type(chapter) is not int or chapter < 0):
            raise SemanticVoiceCastError(f"inventory block {index} chapterIndex is invalid")
        sequence = value["sequenceIndex"]
        if type(sequence) is not int or sequence < 0 or sequence in sequence_indexes:
            raise SemanticVoiceCastError(f"inventory block {index} has a duplicate or invalid sequenceIndex")
        sequence_indexes.add(sequence)
        words = value["wordCount"]
        if words is not None and (type(words) is not int or words < 0):
            raise SemanticVoiceCastError(f"inventory block {index} wordCount is invalid")
        if kind == "image" and value["imagePath"] is not None and not isinstance(value["imagePath"], str):
            raise SemanticVoiceCastError(f"inventory block {index} imagePath is invalid")
    return ids


def _validate_authored_plan(plan: dict[str, object], epub_hash: str) -> None:
    if type(plan["schemaVersion"]) is not int or plan["schemaVersion"] != 1:
        raise SemanticVoiceCastError("authored voice plan schemaVersion must be 1")
    source = _require_object(plan["source"], "authored voice plan source", PLAN_SOURCE_KEYS)
    if _require_sha256(source["epubSHA256"], "authored voice plan source EPUB hash") != epub_hash:
        raise SemanticVoiceCastError("authored voice plan source EPUB hash differs")
    _require_string(plan["defaultSpeakerID"], "authored voice plan defaultSpeakerID")
    speakers = plan["speakers"]
    assignments = plan["assignments"]
    if not isinstance(speakers, list) or not isinstance(assignments, list):
        raise SemanticVoiceCastError("authored voice plan speakers and assignments must be arrays")
    for index, speaker in enumerate(speakers):
        value = _require_object(speaker, f"authored voice plan speaker {index}", PLAN_SPEAKER_KEYS)
        _require_string(value["id"], f"authored voice plan speaker {index} id")
        _require_string(value["voiceID"], f"authored voice plan speaker {index} voiceID")
    for index, assignment in enumerate(assignments):
        value = _require_object(assignment, f"authored voice plan assignment {index}", PLAN_ASSIGNMENT_KEYS)
        _require_string(value["speakerID"], f"authored voice plan assignment {index} speakerID")
        if not isinstance(value["blocks"], list):
            raise SemanticVoiceCastError(f"authored voice plan assignment {index} blocks must be an array")


def validate_cast(
    cast_path: Path,
    inventory_path: Path,
    voice_plan_path: Path,
    epub_path: Path,
) -> ValidationResult:
    """Validate one closed semantic cast and its bound Echo source artifacts."""
    cast_path = Path(cast_path)
    inventory_path = Path(inventory_path)
    voice_plan_path = Path(voice_plan_path)
    epub_path = Path(epub_path)
    for path, label in (
        (cast_path, "cast"),
        (inventory_path, "inventory"),
        (voice_plan_path, "authored voice plan"),
        (epub_path, "EPUB"),
    ):
        require_regular_canonical(path, label)
    cast = read_closed_json(cast_path, "cast", CAST_KEYS)
    if cast_path.read_bytes() != canonical_json(cast):
        raise SemanticVoiceCastError("cast is not canonical JSON")
    run_root = _run_root(cast_path)
    source, groups = _validate_cast(cast)
    epub_name = _require_filename(source["epubFileName"], "source EPUB filename")
    inventory_name = _require_filename(source["inventoryFileName"], "source inventory filename")
    plan_name = _require_filename(
        _require_object(cast["authoredVoicePlan"], "authored voice plan", AUTHORED_PLAN_KEYS)["fileName"],
        "authored voice-plan filename",
    )
    if epub_path != run_root / "dist" / epub_name:
        raise SemanticVoiceCastError("EPUB path does not match source EPUB filename")
    if inventory_path != run_root / "research" / inventory_name:
        raise SemanticVoiceCastError("inventory path does not match source inventory filename")
    if voice_plan_path != cast_path.parent / plan_name:
        raise SemanticVoiceCastError("authored voice-plan filename does not match path")
    epub_hash = _require_sha256(source["epubSHA256"], "source EPUB hash")
    if sha256(epub_path) != epub_hash:
        raise SemanticVoiceCastError("source EPUB hash differs")
    inventory_hash = _require_sha256(source["inventorySHA256"], "source inventory hash")
    if sha256(inventory_path) != inventory_hash:
        raise SemanticVoiceCastError("source inventory hash differs")
    authored = _require_object(cast["authoredVoicePlan"], "authored voice plan", AUTHORED_PLAN_KEYS)
    if sha256(voice_plan_path) != _require_sha256(authored["sha256"], "authored voice-plan hash"):
        raise SemanticVoiceCastError("authored voice-plan hash differs")
    inventory = read_closed_json(inventory_path, "inventory", INVENTORY_KEYS)
    _validate_inventory(inventory, epub_hash)
    plan = read_closed_json(voice_plan_path, "authored voice plan", PLAN_KEYS)
    _validate_authored_plan(plan, epub_hash)
    inventory_blocks = inventory["blocks"]
    assert isinstance(inventory_blocks, list)
    paragraph_ids = {
        value["id"]
        for value in inventory_blocks
        if isinstance(value, dict) and value["kind"] == "paragraph" and bool(value["text"].strip())
    }
    assigned_blocks = [block for group in groups for block in group["blocks"]]
    assigned = set(assigned_blocks)
    if not assigned <= paragraph_ids:
        raise SemanticVoiceCastError("cast group block is not a nonempty paragraph in inventory")
    role_counts: dict[str, int] = {}
    for group in groups:
        role = group["roleID"]
        blocks = group["blocks"]
        assert isinstance(role, str) and isinstance(blocks, list)
        role_counts[role] = role_counts.get(role, 0) + len(blocks)
    paragraph_count = len(paragraph_ids)
    return ValidationResult(
        voice_plan=voice_plan_path,
        paragraph_block_count=paragraph_count,
        guide_block_count=paragraph_count - len(assigned),
        role_block_counts=role_counts,
    )


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate-cast", help="validate one semantic cast")
    validate.add_argument("--cast", required=True, type=Path)
    validate.add_argument("--inventory", required=True, type=Path)
    validate.add_argument("--voice-plan", required=True, type=Path)
    validate.add_argument("--epub", required=True, type=Path)
    validate.add_argument("--format", choices=("json", "argv0"), default="json")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    options = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        result = validate_cast(options.cast, options.inventory, options.voice_plan, options.epub)
    except SemanticVoiceCastError as error:
        print(f"semantic_voice_cast: {error}", file=sys.stderr)
        return 65
    if options.format == "argv0":
        sys.stdout.buffer.write(b"--voice-plan\0" + str(result.voice_plan).encode("utf-8") + b"\0")
    else:
        print(json.dumps({
            "guideBlockCount": result.guide_block_count,
            "paragraphBlockCount": result.paragraph_block_count,
            "roleBlockCounts": result.role_block_counts,
            "voicePlan": str(result.voice_plan),
        }, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
