#!/usr/bin/env python3
"""Validate and persist private ensemble voice preferences for fiction audiobooks."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator


ECHO_VOICE_PLAN_DIRECTORY = (
    Path(__file__).resolve().parents[2] / "echo-narration" / "scripts"
)
if str(ECHO_VOICE_PLAN_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(ECHO_VOICE_PLAN_DIRECTORY))

from echo_pronunciation_state import (
    RENDERER_IDENTITY_KEYS,
    RUN_ID_PATTERN,
)
from echo_voice_plan import VOICE_IDS, voice_plan


DEFAULT_PATH = (
    Path.home()
    / "Library/Application Support/Explainer Audiobooks/fiction-voice-preferences.json"
)
INITIAL_TIMESTAMP = "1970-01-01T00:00:00+00:00"
SHA256_LENGTH = 64
INPUT_RECEIPT_KEY_PATTERN = re.compile(r"[a-z][a-z0-9_]*\Z")
ECHO_SUCCESS_FIELDS = {
    "schemaVersion",
    *RENDERER_IDENTITY_KEYS,
    "attemptID",
    "runID",
    "attemptReceiptSHA256",
    "inputReceiptFileName",
    "inputReceiptSHA256",
    "sourceEPUBFileName",
    "sourceEPUBSHA256",
    "artifactRelativePath",
    "resumeStateFileName",
    "resumeStateSHA256",
    "audiobookFileName",
    "audiobookSHA256",
    "sidecarFileName",
    "sidecarSHA256",
    "auditFileName",
    "auditSHA256",
}


def resolve_voice(value: str) -> str:
    """Resolve an exact Echo ID or a unique human-friendly name."""
    if not isinstance(value, str):
        raise ValueError("unknown or ambiguous Echo voice: value is not text")
    normalized = value.strip().casefold().replace(" ", "_")
    if normalized in VOICE_IDS:
        return normalized
    matches = sorted(
        voice for voice in VOICE_IDS if voice.split("_", 1)[1] == normalized
    )
    if len(matches) != 1:
        raise ValueError(f"unknown or ambiguous Echo voice: {value}")
    return matches[0]


def initial_preferences() -> dict[str, object]:
    """Return the v1 preference state without creating a private file."""
    return {
        "schemaVersion": 1,
        "blacklist": {
            "af_heart": {
                "updatedAt": INITIAL_TIMESTAMP,
                "reason": "standing audiobook preference",
            }
        },
        "verdicts": {},
        "uses": [],
        "updatedAt": INITIAL_TIMESTAMP,
    }


def _json_object(path: Path, label: str) -> dict[str, Any]:
    _refuse_symlink(path, label)
    try:
        with path.open(encoding="utf-8") as source:
            value = json.load(source, object_pairs_hook=_unique_object)
    except json.JSONDecodeError as error:
        raise ValueError(f"{label} is not valid JSON: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _refuse_symlink(path: Path, label: str) -> None:
    current = path
    while True:
        if current.is_symlink():
            raise ValueError(f"{label} must not use a symlink ancestor: {current}")
        parent = current.parent
        if parent == current:
            return
        current = parent


def _timestamp(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be an ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{label} must be an ISO-8601 timestamp") from error
    if parsed.tzinfo is None:
        raise ValueError(f"{label} must be an ISO-8601 timestamp with an offset")
    return value


def _sha256(value: object, label: str) -> str:
    if not isinstance(value, str) or len(value) != SHA256_LENGTH:
        raise ValueError(f"{label} must be a lowercase SHA-256")
    if any(character not in "0123456789abcdef" for character in value):
        raise ValueError(f"{label} must be a lowercase SHA-256")
    return value


def _known_voice(value: object, label: str) -> str:
    if not isinstance(value, str) or value not in VOICE_IDS:
        raise ValueError(f"{label} is an unknown Echo voice: {value}")
    return value


def _require_dict(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def _require_list(value: object, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    return value


def _validate_preferences(preferences: dict[str, Any]) -> dict[str, Any]:
    schema_version = preferences.get("schemaVersion")
    if type(schema_version) is not int or schema_version != 1:
        raise ValueError("preferences schemaVersion must be 1")
    blacklist = _require_dict(preferences.get("blacklist"), "preferences blacklist")
    verdicts = _require_dict(preferences.get("verdicts"), "preferences verdicts")
    uses = _require_list(preferences.get("uses"), "preferences uses")
    _timestamp(preferences.get("updatedAt"), "preferences updatedAt")

    for voice, record in blacklist.items():
        _known_voice(voice, "blacklist voice")
        data = _require_dict(record, f"blacklist record for {voice}")
        _timestamp(data.get("updatedAt"), f"blacklist timestamp for {voice}")
        if "reason" in data and not isinstance(data["reason"], str):
            raise ValueError(f"blacklist reason for {voice} must be text")
    heart = blacklist.get("af_heart")
    if not isinstance(heart, dict):
        raise ValueError("preferences must retain the standing af_heart blacklist")
    _timestamp(heart.get("updatedAt"), "standing af_heart blacklist timestamp")
    if not isinstance(heart.get("reason"), str):
        raise ValueError("standing af_heart blacklist reason must be text")

    for voice, record in verdicts.items():
        _known_voice(voice, "verdict voice")
        data = _require_dict(record, f"verdict record for {voice}")
        if data.get("verdict") not in {"liked", "disliked", "blacklisted"}:
            raise ValueError(f"verdict for {voice} is invalid")
        _timestamp(data.get("updatedAt"), f"verdict timestamp for {voice}")
        if "reason" in data and not isinstance(data["reason"], str):
            raise ValueError(f"verdict reason for {voice} must be text")

    for index, use in enumerate(uses):
        data = _require_dict(use, f"use {index}")
        if not isinstance(data.get("slug"), str) or not data["slug"]:
            raise ValueError(f"use {index} slug must be non-empty text")
        _timestamp(data.get("recordedAt"), f"use {index} recordedAt")
        for field in (
            "sourceEPUBSHA256",
            "audiobookSHA256",
            "sidecarSHA256",
            "voicePlanSHA256",
        ):
            _sha256(data.get(field), f"use {index} {field}")
        _sha256(data.get("successReceiptSHA256"), f"use {index} successReceiptSHA256")
        chapters = _require_list(data.get("chapters"), f"use {index} chapters")
        for row in chapters:
            chapter = _require_dict(row, f"use {index} chapter")
            if type(chapter.get("chapter")) is not int or chapter["chapter"] < 1:
                raise ValueError(f"use {index} chapter number must be positive")
            _known_voice(chapter.get("voice"), f"use {index} chapter voice")
    return preferences


def load_preferences(path: Path = DEFAULT_PATH) -> dict[str, object]:
    """Read validated preferences, or supply the durable defaults without writing."""
    path = Path(path)
    _refuse_symlink(path, "preferences store")
    if not path.exists():
        return initial_preferences()
    return _validate_preferences(_json_object(path, "preferences store"))


def _atomic_json(path: Path, payload: object, label: str) -> None:
    path = Path(path)
    _refuse_symlink(path, label)
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    _refuse_symlink(path, label)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as destination:
            json.dump(payload, destination, sort_keys=True, indent=2)
            destination.write("\n")
            destination.flush()
            os.fsync(destination.fileno())
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    except BaseException:
        if temporary.exists():
            temporary.unlink()
        raise


@contextmanager
def _preferences_lock(path: Path) -> Iterator[None]:
    """Serialize one preference-store read/modify/replace transaction."""
    path = Path(path)
    _refuse_symlink(path, "preferences store")
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    _refuse_symlink(path, "preferences store")
    lock_path = path.with_name(f".{path.name}.lock")
    _refuse_symlink(lock_path, "preferences lock")
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise ValueError("preferences lock cannot be opened fail-closed")
    try:
        parent_before = os.stat(path.parent, follow_symlinks=False)
    except OSError as error:
        raise ValueError("preferences lock directory is unavailable") from error
    if not stat.S_ISDIR(parent_before.st_mode):
        raise ValueError("preferences lock parent must be a real directory")
    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    if hasattr(os, "O_CLOEXEC"):
        directory_flags |= os.O_CLOEXEC
    try:
        parent_descriptor = os.open(path.parent, directory_flags)
    except OSError as error:
        raise ValueError("preferences lock parent must be a stable directory") from error
    lock_descriptor: int | None = None
    try:
        parent_opened = os.fstat(parent_descriptor)
        parent_identity = (parent_opened.st_dev, parent_opened.st_ino)
        if parent_identity != (parent_before.st_dev, parent_before.st_ino):
            raise ValueError("preferences lock parent directory changed while opening")
        lock_flags = os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW
        if hasattr(os, "O_CLOEXEC"):
            lock_flags |= os.O_CLOEXEC
        try:
            lock_descriptor = os.open(
                lock_path,
                lock_flags,
                0o600,
            )
        except OSError as error:
            raise ValueError(
                "preferences lock must be a regular non-symlink file"
            ) from error
        if not stat.S_ISREG(os.fstat(lock_descriptor).st_mode):
            raise ValueError("preferences lock must be a regular non-symlink file")
        os.fchmod(lock_descriptor, 0o600)
        lock_opened = os.fstat(lock_descriptor)
        lock_at_path = os.stat(
            lock_path.name, dir_fd=parent_descriptor, follow_symlinks=False
        )
        if (
            not stat.S_ISREG(lock_at_path.st_mode)
            or (lock_at_path.st_dev, lock_at_path.st_ino)
            != (lock_opened.st_dev, lock_opened.st_ino)
        ):
            raise ValueError("preferences lock path changed while opening")
        fcntl.flock(lock_descriptor, fcntl.LOCK_EX)
        try:
            lock_after_acquire = os.stat(
                lock_path.name, dir_fd=parent_descriptor, follow_symlinks=False
            )
        except OSError as error:
            raise ValueError("preferences lock path changed while waiting") from error
        if (
            not stat.S_ISREG(lock_after_acquire.st_mode)
            or (lock_after_acquire.st_dev, lock_after_acquire.st_ino)
            != (lock_opened.st_dev, lock_opened.st_ino)
        ):
            raise ValueError("preferences lock path changed while waiting")
        parent_at_path = os.stat(path.parent, follow_symlinks=False)
        if (parent_at_path.st_dev, parent_at_path.st_ino) != parent_identity:
            raise ValueError("preferences lock parent directory changed")
        _refuse_symlink(path, "preferences store")
        yield
    finally:
        if lock_descriptor is not None:
            fcntl.flock(lock_descriptor, fcntl.LOCK_UN)
            os.close(lock_descriptor)
        os.close(parent_descriptor)


def _used_voices(preferences: dict[str, Any]) -> set[str]:
    return {
        row["voice"]
        for use in preferences["uses"]
        for row in use["chapters"]
    }


def _validate_cast_contract(
    cast: dict[str, Any], *, require_unverified: bool
) -> tuple[dict[str, object], list[dict[str, Any]]]:
    schema_version = cast.get("schemaVersion")
    if type(schema_version) is not int or schema_version != 1:
        raise ValueError("cast schemaVersion must be 1")
    if not isinstance(cast.get("slug"), str) or not cast["slug"]:
        raise ValueError("cast slug must be non-empty text")
    chapter_count = cast.get("chapterCount")
    if type(chapter_count) is not int or chapter_count < 1:
        raise ValueError("cast chapterCount must be a positive integer")
    default_voice = _known_voice(cast.get("defaultVoice"), "cast default voice")
    chapters = _require_list(cast.get("chapters"), "cast chapters")
    if len(chapters) != chapter_count:
        raise ValueError("cast must assign every chapter exactly once")

    roles: dict[str, str] = {}
    voices: set[str] = set()
    experimental_rows: list[dict[str, Any]] = []
    chapter_numbers: set[int] = set()
    canonical_rows: list[str] = []
    for row in chapters:
        data = _require_dict(row, "cast chapter")
        chapter = data.get("chapter")
        if type(chapter) is not int or chapter < 1:
            raise ValueError("cast chapter number must be positive")
        chapter_numbers.add(chapter)
        role = data.get("role")
        if not isinstance(role, str) or not role:
            raise ValueError("cast role must be non-empty text")
        voice = _known_voice(data.get("voice"), "cast voice")
        experimental = data.get("experimental")
        if type(experimental) is not bool:
            raise ValueError("cast experimental must be a real boolean")
        previous = roles.setdefault(role, voice)
        if previous != voice:
            raise ValueError(f"recurring role must keep one voice: {role}")
        voices.add(voice)
        canonical_rows.append(f"{chapter}={voice}")
        if experimental:
            experimental_rows.append(data)
    if chapter_numbers != set(range(1, chapter_count + 1)):
        raise ValueError("cast must assign every chapter from 1 through chapterCount")
    if not 3 <= len(voices) <= 5:
        raise ValueError("cast requires three to five distinct voices")
    if len(experimental_rows) > 2:
        raise ValueError("cast allows at most two experimental rows")

    plan = voice_plan(default_voice, canonical_rows)
    if cast.get("voicePlanSHA256") != plan["voicePlanSHA256"]:
        raise ValueError("cast voice-plan hash does not match Echo canonical plan")
    if cast.get("voicePlanID") != plan["voicePlanID"]:
        raise ValueError("cast voice-plan identity does not match Echo canonical plan")
    if require_unverified and cast.get("verifiedArtifacts") is not None:
        raise ValueError("cast verifiedArtifacts must be null before narration")
    if "verifiedArtifacts" not in cast:
        raise ValueError("cast verifiedArtifacts must be null before narration")
    return plan, experimental_rows


def _validate_cast(
    cast: dict[str, Any], preferences: dict[str, Any], *, require_unverified: bool
) -> dict[str, object]:
    blacklist = preferences["blacklist"]
    default_voice = cast.get("defaultVoice")
    if isinstance(default_voice, str) and default_voice in blacklist:
        raise ValueError(f"cast default voice is blacklisted: {default_voice}")
    chapter_rows = cast.get("chapters")
    if isinstance(chapter_rows, list):
        for row in chapter_rows:
            if isinstance(row, dict):
                voice = row.get("voice")
                if isinstance(voice, str) and voice in blacklist:
                    raise ValueError(f"cast voice is blacklisted: {voice}")
    plan, experimental_rows = _validate_cast_contract(
        cast, require_unverified=require_unverified
    )
    used_voices = _used_voices(preferences)
    for row in experimental_rows:
        if row["voice"] in used_voices:
            raise ValueError(f"experimental voice was already used: {row['voice']}")
    return plan


def validate_cast(cast: dict[str, object], preferences: dict[str, object]) -> dict[str, object]:
    """Reject invalid casts and return Echo's canonical chapter-voice plan."""
    return _validate_cast(
        _require_dict(cast, "cast"),
        _validate_preferences(_require_dict(preferences, "preferences")),
        require_unverified=True,
    )


def validate_completed_cast(cast: dict[str, object]) -> dict[str, object]:
    """Validate immutable cast structure and plan without mutable preferences."""
    data = _require_dict(cast, "cast")
    plan, _ = _validate_cast_contract(data, require_unverified=False)
    if not isinstance(data.get("verifiedArtifacts"), dict):
        raise ValueError("cast verifiedArtifacts must be completed")
    return plan


def _regular_digest(path: Path, label: str) -> str:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{label} must be a regular non-symlink file")
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _stable_regular_bytes(path: Path, label: str) -> bytes:
    """Read one non-symlink file through a stable descriptor and path identity."""
    path = Path(path)
    if path.is_symlink():
        raise ValueError(f"{label} must be a regular non-symlink sibling file")
    _refuse_symlink(path, label)
    try:
        before = os.stat(path, follow_symlinks=False)
    except OSError as error:
        raise ValueError(f"{label} must be a readable sibling file") from error
    if not stat.S_ISREG(before.st_mode):
        raise ValueError(f"{label} must be a regular non-symlink sibling file")
    flags = os.O_RDONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if not hasattr(os, "O_NOFOLLOW"):
        raise ValueError(f"{label} cannot be opened fail-closed on this platform")
    flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise ValueError(f"{label} must be a regular non-symlink sibling file") from error
    try:
        opened = os.fstat(descriptor)
        identity = (opened.st_dev, opened.st_ino)
        stable = (
            opened.st_mode,
            opened.st_size,
            opened.st_mtime_ns,
            opened.st_ctime_ns,
        )
        if identity != (before.st_dev, before.st_ino):
            raise ValueError(f"{label} path changed before it was opened")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after_descriptor = os.fstat(descriptor)
        try:
            after_path = os.stat(path, follow_symlinks=False)
        except OSError as error:
            raise ValueError(f"{label} path changed while it was read") from error
        if (
            not stat.S_ISREG(after_descriptor.st_mode)
            or (after_descriptor.st_dev, after_descriptor.st_ino) != identity
            or (
                after_descriptor.st_mode,
                after_descriptor.st_size,
                after_descriptor.st_mtime_ns,
                after_descriptor.st_ctime_ns,
            )
            != stable
            or (after_path.st_dev, after_path.st_ino) != identity
            or (
                after_path.st_mode,
                after_path.st_size,
                after_path.st_mtime_ns,
                after_path.st_ctime_ns,
            )
            != stable
        ):
            raise ValueError(f"{label} path or bytes changed while it was read")
        _refuse_symlink(path, label)
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def validate_echo_success_receipt(
    receipt: dict[str, object], receipt_path: Path, cast: dict[str, object]
) -> None:
    """Validate real Echo v3 provenance and bind its run to a canonical cast."""
    expected_fields = set(ECHO_SUCCESS_FIELDS)
    has_reel = "reelFileName" in receipt or "reelSHA256" in receipt
    if has_reel:
        expected_fields.update({"reelFileName", "reelSHA256"})
    if set(receipt) != expected_fields:
        raise ValueError(
            "Echo success receipt must contain exact governed provenance fields"
        )
    if type(receipt.get("schemaVersion")) is not int or receipt["schemaVersion"] != 3:
        raise ValueError("Echo success receipt schemaVersion must be integer 3")
    if (
        type(receipt.get("rendererSchemaVersion")) is not int
        or receipt["rendererSchemaVersion"] != 1
    ):
        raise ValueError("Echo rendererSchemaVersion must be integer 1")
    for field in ("rendererRoot", "rendererBuildRoot"):
        value = receipt.get(field)
        if not isinstance(value, str) or not Path(value).is_absolute():
            raise ValueError(f"Echo success receipt {field} must be an absolute path")
    for field in ("installerSourceSHA", "echoSourceSHA"):
        value = receipt.get(field)
        if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{40}", value) is None:
            raise ValueError(f"Echo success receipt {field} must be a lowercase Git SHA")
    for field in (
        "rendererManifestSHA256",
        "echoCLI_SHA256",
        "echoResourcesSHA256",
    ):
        _sha256(receipt.get(field), f"Echo success receipt {field}")
    if (
        type(receipt.get("echoRenderVersion")) is not int
        or receipt["echoRenderVersion"] < 12
    ):
        raise ValueError("Echo render version must be an integer of at least 12")
    policy = receipt.get("modelPolicyRevision")
    if (
        not isinstance(policy, str)
        or not policy
        or "\n" in policy
        or "\r" in policy
    ):
        raise ValueError("Echo modelPolicyRevision must be nonempty and single-line")
    if (
        type(receipt.get("modelExpectedByteCount")) is not int
        or receipt["modelExpectedByteCount"] < 1
    ):
        raise ValueError("Echo modelExpectedByteCount must be a positive integer")
    if receipt.get("modelBytesAttested") is not False:
        raise ValueError("Echo modelBytesAttested must be false")
    attempt_id = _sha256(receipt.get("attemptID"), "Echo attemptID")
    run_id = receipt.get("runID")
    if not isinstance(run_id, str) or RUN_ID_PATTERN.fullmatch(run_id) is None:
        raise ValueError("Echo success receipt runID is invalid")
    plan_id = cast.get("voicePlanID")
    if not isinstance(plan_id, str):
        raise ValueError("cast voice-plan identity is invalid")
    expected_run_id = (
        f"{_sha256(receipt.get('sourceEPUBSHA256'), 'Echo source EPUB SHA-256')[:12]}-"
        f"{receipt['echoCLI_SHA256'][:12]}-"
        f"{receipt['echoResourcesSHA256'][:12]}-"
        f"{receipt['rendererManifestSHA256'][:12]}-"
        f"{receipt['echoSourceSHA']}-{plan_id}"
    )
    if run_id != expected_run_id:
        raise ValueError(
            "Echo success receipt runID does not match source EPUB, renderer provenance, and cast voice plan"
        )
    receipt_path = Path(receipt_path)
    if receipt_path.name != f"echo-render-success-{run_id}-{attempt_id}.json":
        raise ValueError("Echo success receipt filename is not derived from runID")
    if receipt.get("artifactRelativePath") != f"echo-renders/{run_id}/{attempt_id}":
        raise ValueError("Echo artifact path is not derived from runID and attemptID")
    if receipt.get("inputReceiptFileName") != f"echo-render-inputs-{run_id}.env":
        raise ValueError("Echo input receipt filename is not derived from runID")
    input_receipt = receipt_path.parent / str(receipt["inputReceiptFileName"])
    input_bytes = _stable_regular_bytes(input_receipt, "Echo input receipt")
    expected_input_hash = _sha256(
        receipt.get("inputReceiptSHA256"), "Echo success receipt inputReceiptSHA256"
    )
    if hashlib.sha256(input_bytes).hexdigest() != expected_input_hash:
        raise ValueError("Echo input receipt bytes differ from success receipt")
    try:
        input_text = input_bytes.decode("utf-8")
    except UnicodeError as error:
        raise ValueError("Echo input receipt must be strict UTF-8 key=value lines") from error
    if (
        not input_text.endswith("\n")
        or "\r" in input_text
        or "\0" in input_text
    ):
        raise ValueError("Echo input receipt must be newline-terminated key=value lines")
    input_fields: dict[str, str] = {}
    for line in input_text[:-1].split("\n"):
        if not line or "=" not in line:
            raise ValueError("Echo input receipt contains a malformed key=value line")
        key, value = line.split("=", 1)
        if INPUT_RECEIPT_KEY_PATTERN.fullmatch(key) is None:
            raise ValueError(f"Echo input receipt contains an invalid key: {key}")
        if key in input_fields:
            raise ValueError(f"duplicate Echo input receipt key: {key}")
        input_fields[key] = value
    plan, _ = _validate_cast_contract(
        _require_dict(cast, "cast"), require_unverified=False
    )
    expected_input_fields = {
        "voice": str(plan["defaultVoice"]),
        "chapter_voices": ",".join(plan["canonicalAssignments"]),
        "voice_plan_sha256": str(cast["voicePlanSHA256"]),
        "voice_plan_id": str(cast["voicePlanID"]),
    }
    input_labels = {
        "voice": "default voice",
        "chapter_voices": "canonical chapter mappings",
        "voice_plan_sha256": "full voice-plan hash",
        "voice_plan_id": "voice-plan identity",
    }
    for key, expected in expected_input_fields.items():
        if input_fields.get(key) != expected:
            raise ValueError(
                f"Echo input receipt {input_labels[key]} does not match cast"
            )
    if receipt.get("resumeStateFileName") != f"echo-resume-state-{run_id}.json":
        raise ValueError("Echo resume-state filename is not derived from runID")
    for field in (
        "attemptReceiptSHA256",
        "inputReceiptSHA256",
        "resumeStateSHA256",
        "audiobookSHA256",
        "sidecarSHA256",
        "auditSHA256",
    ):
        _sha256(receipt.get(field), f"Echo success receipt {field}")
    if has_reel:
        _sha256(receipt.get("reelSHA256"), "Echo success receipt reelSHA256")
    for field in ("auditFileName", "reelFileName"):
        if field in receipt:
            filename = receipt[field]
            if (
                not isinstance(filename, str)
                or not filename
                or Path(filename).name != filename
            ):
                raise ValueError(f"Echo success receipt {field} must be a filename")


def _receipt_artifacts(
    cast: dict[str, Any], epub: Path, m4b: Path, sidecar: Path, success_receipt: Path
) -> dict[str, str]:
    receipt = _json_object(success_receipt, "Echo success receipt")
    validate_echo_success_receipt(receipt, success_receipt, cast)
    artifacts = (
        (epub, "sourceEPUBFileName", "sourceEPUBSHA256", "EPUB"),
        (m4b, "audiobookFileName", "audiobookSHA256", "M4B"),
        (sidecar, "sidecarFileName", "sidecarSHA256", "sidecar"),
    )
    verified: dict[str, str] = {}
    for path, name_field, hash_field, label in artifacts:
        actual = _regular_digest(path, label)
        if receipt.get(name_field) != path.name:
            raise ValueError(f"{label} filename differs from success receipt")
        if receipt.get(hash_field) != actual:
            raise ValueError(f"{label} differs from success receipt")
        verified[hash_field] = actual
    plan_hash = cast["voicePlanSHA256"]
    verified["voicePlanSHA256"] = plan_hash
    return verified


def _load_cast(path: Path) -> dict[str, Any]:
    return _json_object(Path(path), "voice cast")


def record_use(
    cast_path: Path,
    epub: Path,
    m4b: Path,
    sidecar: Path,
    success_receipt: Path,
    at: str,
    preferences_path: Path = DEFAULT_PATH,
) -> dict[str, object]:
    """Seal a verified cast, then append its completed use to private history."""
    _timestamp(at, "recordedAt")
    preferences_path = Path(preferences_path)
    with _preferences_lock(preferences_path):
        preferences = load_preferences(preferences_path)
        cast_path = Path(cast_path)
        cast = _load_cast(cast_path)
        _validate_cast(cast, preferences, require_unverified=False)
        verified = _receipt_artifacts(
            cast, Path(epub), Path(m4b), Path(sidecar), Path(success_receipt)
        )
        existing_verified = cast.get("verifiedArtifacts")
        if existing_verified is None:
            cast["verifiedArtifacts"] = verified
            _atomic_json(cast_path, cast, "voice cast")
        elif existing_verified != verified:
            raise ValueError(
                "cast verifiedArtifacts differ from the supplied governed artifacts"
            )

        use_key = (
            cast["slug"],
            verified["audiobookSHA256"],
            verified["voicePlanSHA256"],
        )
        for use in preferences["uses"]:
            if (
                use["slug"],
                use["audiobookSHA256"],
                use["voicePlanSHA256"],
            ) == use_key:
                return preferences
        preferences["uses"].append(
            {
                "slug": cast["slug"],
                "recordedAt": at,
                "sourceEPUBSHA256": verified["sourceEPUBSHA256"],
                "audiobookSHA256": verified["audiobookSHA256"],
                "sidecarSHA256": verified["sidecarSHA256"],
                "voicePlanSHA256": verified["voicePlanSHA256"],
                "successReceiptSHA256": _regular_digest(
                    Path(success_receipt), "Echo success receipt"
                ),
                "chapters": [
                    {"chapter": row["chapter"], "voice": row["voice"]}
                    for row in cast["chapters"]
                ],
            }
        )
        preferences["updatedAt"] = at
        _atomic_json(preferences_path, preferences, "preferences store")
        return preferences


def set_verdict(
    path: Path,
    voice: str,
    verdict: str,
    reason: str,
    at: str,
) -> dict[str, object]:
    """Persist a listener verdict and any matching blacklist effect."""
    if verdict not in {"liked", "disliked", "blacklisted", "clear"}:
        raise ValueError("verdict must be liked, disliked, blacklisted, or clear")
    if not isinstance(reason, str):
        raise ValueError("reason must be text")
    _timestamp(at, "verdict timestamp")
    resolved_voice = resolve_voice(voice)
    path = Path(path)
    with _preferences_lock(path):
        preferences = load_preferences(path)
        if verdict == "clear":
            preferences["verdicts"].pop(resolved_voice, None)
            if resolved_voice != "af_heart":
                preferences["blacklist"].pop(resolved_voice, None)
        else:
            record = {"verdict": verdict, "updatedAt": at}
            if reason:
                record["reason"] = reason
            preferences["verdicts"][resolved_voice] = record
            if verdict == "blacklisted":
                blacklist_record = {"updatedAt": at}
                if reason:
                    blacklist_record["reason"] = reason
                elif resolved_voice == "af_heart":
                    blacklist_record["reason"] = preferences["blacklist"]["af_heart"][
                        "reason"
                    ]
                preferences["blacklist"][resolved_voice] = blacklist_record
        preferences["updatedAt"] = at
        _atomic_json(path, preferences, "preferences store")
        return preferences


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate-cast")
    validate.add_argument("--cast", type=Path, required=True)
    validate.add_argument("--preferences", type=Path, default=DEFAULT_PATH)
    record = commands.add_parser("record-use")
    record.add_argument("--cast", type=Path, required=True)
    record.add_argument("--epub", type=Path, required=True)
    record.add_argument("--m4b", type=Path, required=True)
    record.add_argument("--sidecar", type=Path, required=True)
    record.add_argument("--success-receipt", type=Path, required=True)
    record.add_argument("--at", required=True)
    record.add_argument("--preferences", type=Path, default=DEFAULT_PATH)
    verdict = commands.add_parser("set-verdict")
    verdict.add_argument("--voice", required=True)
    verdict.add_argument("--verdict", choices=("liked", "disliked", "blacklisted", "clear"), required=True)
    verdict.add_argument("--at", required=True)
    verdict.add_argument("--reason", default="")
    verdict.add_argument("--preferences", type=Path, default=DEFAULT_PATH)
    return parser


def main(arguments: list[str]) -> int:
    options = _parser().parse_args(arguments)
    try:
        if options.command == "validate-cast":
            cast = _load_cast(options.cast)
            plan = validate_cast(cast, load_preferences(options.preferences))
            result: object = [
                token
                for assignment in plan["canonicalAssignments"]
                for token in ("--chapter-voice", assignment)
            ]
        elif options.command == "record-use":
            result = record_use(
                options.cast, options.epub, options.m4b, options.sidecar,
                options.success_receipt, options.at, options.preferences,
            )
        else:
            result = set_verdict(
                options.preferences, options.voice, options.verdict,
                options.reason, options.at,
            )
    except ValueError as error:
        print(f"fiction_voice_preferences: {error}", file=sys.stderr)
        return 64
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
