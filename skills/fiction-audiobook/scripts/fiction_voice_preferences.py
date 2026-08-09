#!/usr/bin/env python3
"""Validate and persist private ensemble voice preferences for fiction audiobooks."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import io
import json
import os
import re
import secrets
import stat
import sys
import tempfile
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterator


ECHO_VOICE_PLAN_DIRECTORY = (
    Path(__file__).resolve().parents[2] / "echo-narration" / "scripts"
)
if str(ECHO_VOICE_PLAN_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(ECHO_VOICE_PLAN_DIRECTORY))

from echo_pronunciation_state import (
    RENDERER_IDENTITY_KEYS,
    RUN_ID_PATTERN,
    StateError,
    require_block_success_receipt,
)
from echo_voice_plan import (
    RESOLVER_KEYS,
    VOICE_IDS,
    VoicePlanError,
    validate_resolver_receipt,
    voice_plan,
)


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
BLOCK_CAST_FIELDS = {
    "schemaVersion",
    "slug",
    "narrationMode",
    "sourceEPUBSHA256",
    "defaultSpeakerID",
    "speakers",
    "authoredVoicePlan",
    "resolvedVoicePlan",
    "verifiedArtifacts",
}
BLOCK_SPEAKER_FIELDS = {"speakerID", "role", "voiceID", "experimental"}
AUTHORED_VOICE_PLAN_FIELDS = {
    "schemaVersion",
    "source",
    "defaultSpeakerID",
    "speakers",
    "assignments",
}
AUTHORED_VOICE_PLAN_SOURCE_FIELDS = {"epubSHA256"}
AUTHORED_VOICE_PLAN_SPEAKER_FIELDS = {"id", "voiceID"}
BLOCK_USE_FIELDS = {
    "slug",
    "recordedAt",
    "sourceEPUBSHA256",
    "audiobookSHA256",
    "sidecarSHA256",
    "voicePlanSHA256",
    "successReceiptSHA256",
    "narrationMode",
    "speakers",
}
BLOCK_USE_SPEAKER_FIELDS = {"speakerID", "voice"}
VERIFIED_ARTIFACT_FIELDS = {
    "sourceEPUBSHA256",
    "audiobookSHA256",
    "sidecarSHA256",
    "voicePlanSHA256",
}


@dataclass(frozen=True)
class _StableFileSnapshot:
    path: Path
    label: str
    device: int
    inode: int
    mode: int
    size: int
    mtime_ns: int
    ctime_ns: int
    content: bytes
    sha256: str


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


def _reject_nonfinite_json_number(value: str) -> None:
    raise ValueError(f"non-finite JSON number: {value}")


def _strict_json_object_bytes(content: bytes, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(
            content.decode("utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_nonfinite_json_number,
        )
    except (UnicodeError, json.JSONDecodeError, ValueError) as error:
        raise ValueError(f"{label} is not valid UTF-8 JSON") from error
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must be a JSON object")
    return payload


def _same_json_value(left: object, right: object) -> bool:
    """Compare decoded JSON without assigning meaning to opaque assignments."""
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return (
            isinstance(right, dict)
            and left.keys() == right.keys()
            and all(_same_json_value(value, right[key]) for key, value in left.items())
        )
    if isinstance(left, list):
        return isinstance(right, list) and len(left) == len(right) and all(
            _same_json_value(value, right[index])
            for index, value in enumerate(left)
        )
    return left == right


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


def _filename(value: object, label: str) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value in {".", ".."}
        or any(character in value for character in ("\0", "\n", "\r"))
        or "/" in value
        or "\\" in value
        or Path(value).name != value
    ):
        raise ValueError(f"{label} must be a safe filename")
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
        has_chapters = "chapters" in data
        has_speakers = "speakers" in data
        if has_chapters and has_speakers:
            raise ValueError(f"use {index} contains both chapters and speakers")
        if not has_chapters and not has_speakers:
            raise ValueError(f"use {index} contains neither chapters nor speakers")
        if has_chapters:
            chapters = _require_list(data.get("chapters"), f"use {index} chapters")
            for row in chapters:
                chapter = _require_dict(row, f"use {index} chapter")
                if type(chapter.get("chapter")) is not int or chapter["chapter"] < 1:
                    raise ValueError(f"use {index} chapter number must be positive")
                _known_voice(chapter.get("voice"), f"use {index} chapter voice")
            continue
        if set(data) != BLOCK_USE_FIELDS:
            raise ValueError(f"use {index} block record must contain exact schema-1 fields")
        if data.get("narrationMode") != "block":
            raise ValueError(f"use {index} narrationMode must be block")
        speaker_ids: set[str] = set()
        speakers = _require_list(data.get("speakers"), f"use {index} speakers")
        for row in speakers:
            speaker = _require_dict(row, f"use {index} speaker")
            if set(speaker) != BLOCK_USE_SPEAKER_FIELDS:
                raise ValueError(f"use {index} speaker must contain exact speakerID and voice")
            speaker_id = speaker.get("speakerID")
            if not isinstance(speaker_id, str) or not speaker_id:
                raise ValueError(f"use {index} speakerID must be non-empty text")
            if speaker_id in speaker_ids:
                raise ValueError(f"use {index} speakerID is not unique: {speaker_id}")
            speaker_ids.add(speaker_id)
            _known_voice(speaker.get("voice"), f"use {index} speaker voice")
    return preferences


class _PreferenceTransaction:
    """One preference mutation pinned to its locked parent directory."""

    def __init__(
        self,
        path: Path,
        parent_descriptor: int,
        parent_identity: tuple[int, int],
        lock_descriptor: int,
        lock_identity: tuple[int, int],
        lock_name: str,
    ) -> None:
        self.path = Path(path)
        self.parent_descriptor = parent_descriptor
        self.parent_identity = parent_identity
        self.lock_descriptor = lock_descriptor
        self.lock_identity = lock_identity
        self.lock_name = lock_name
        self.committed_descriptor: int | None = None
        self.committed_identity: tuple[int, int] | None = None
        self.committed_bytes: bytes | None = None
        self.committed_sha256: str | None = None

    def matches(self, path: Path) -> bool:
        return Path(path) == self.path

    def attest(self) -> None:
        parent_opened = os.fstat(self.parent_descriptor)
        if (
            not stat.S_ISDIR(parent_opened.st_mode)
            or (parent_opened.st_dev, parent_opened.st_ino) != self.parent_identity
        ):
            raise ValueError("preferences lock parent descriptor changed")
        try:
            parent_at_path = os.stat(self.path.parent, follow_symlinks=False)
        except OSError as error:
            raise ValueError("preferences lock parent directory changed") from error
        if (
            not stat.S_ISDIR(parent_at_path.st_mode)
            or (parent_at_path.st_dev, parent_at_path.st_ino) != self.parent_identity
        ):
            raise ValueError("preferences lock parent directory changed")

        lock_opened = os.fstat(self.lock_descriptor)
        try:
            lock_at_path = os.stat(
                self.lock_name,
                dir_fd=self.parent_descriptor,
                follow_symlinks=False,
            )
        except OSError as error:
            raise ValueError("preferences lock path changed") from error
        if (
            not stat.S_ISREG(lock_opened.st_mode)
            or not stat.S_ISREG(lock_at_path.st_mode)
            or (lock_opened.st_dev, lock_opened.st_ino) != self.lock_identity
            or (lock_at_path.st_dev, lock_at_path.st_ino) != self.lock_identity
        ):
            raise ValueError("preferences lock path changed")
        self._attest_committed()

    def _attest_committed(self) -> None:
        if self.committed_descriptor is None:
            return
        assert self.committed_identity is not None
        assert self.committed_bytes is not None
        assert self.committed_sha256 is not None
        bound = os.fstat(self.committed_descriptor)
        if (
            not stat.S_ISREG(bound.st_mode)
            or (bound.st_dev, bound.st_ino) != self.committed_identity
            or stat.S_IMODE(bound.st_mode) != 0o600
            or bound.st_size != len(self.committed_bytes)
        ):
            raise ValueError("preferences store committed file changed")
        flags = os.O_RDONLY | os.O_NOFOLLOW
        if hasattr(os, "O_CLOEXEC"):
            flags |= os.O_CLOEXEC
        try:
            descriptor = os.open(
                self.path.name,
                flags,
                dir_fd=self.parent_descriptor,
            )
        except OSError as error:
            raise ValueError("preferences store committed path changed") from error
        try:
            opened = os.fstat(descriptor)
            stable = (
                opened.st_mode,
                opened.st_size,
                opened.st_mtime_ns,
                opened.st_ctime_ns,
            )
            chunks: list[bytes] = []
            while True:
                chunk = os.read(descriptor, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
            after_descriptor = os.fstat(descriptor)
            try:
                after_path = os.stat(
                    self.path.name,
                    dir_fd=self.parent_descriptor,
                    follow_symlinks=False,
                )
            except OSError as error:
                raise ValueError("preferences store committed path changed") from error
            actual_bytes = b"".join(chunks)
            if (
                not stat.S_ISREG(opened.st_mode)
                or (opened.st_dev, opened.st_ino) != self.committed_identity
                or (
                    after_descriptor.st_mode,
                    after_descriptor.st_size,
                    after_descriptor.st_mtime_ns,
                    after_descriptor.st_ctime_ns,
                )
                != stable
                or (after_path.st_dev, after_path.st_ino) != self.committed_identity
                or (
                    after_path.st_mode,
                    after_path.st_size,
                    after_path.st_mtime_ns,
                    after_path.st_ctime_ns,
                )
                != stable
                or stat.S_IMODE(opened.st_mode) != 0o600
                or actual_bytes != self.committed_bytes
                or hashlib.sha256(actual_bytes).hexdigest()
                != self.committed_sha256
            ):
                raise ValueError("preferences store committed bytes changed")
        finally:
            os.close(descriptor)

    def close(self) -> None:
        if self.committed_descriptor is not None:
            os.close(self.committed_descriptor)
            self.committed_descriptor = None

    def load(self) -> dict[str, object]:
        self.attest()
        flags = os.O_RDONLY | os.O_NOFOLLOW
        if hasattr(os, "O_CLOEXEC"):
            flags |= os.O_CLOEXEC
        try:
            descriptor = os.open(
                self.path.name,
                flags,
                dir_fd=self.parent_descriptor,
            )
        except FileNotFoundError:
            self.attest()
            return initial_preferences()
        except OSError as error:
            raise ValueError("preferences store must be a regular non-symlink file") from error
        try:
            opened = os.fstat(descriptor)
            if not stat.S_ISREG(opened.st_mode):
                raise ValueError("preferences store must be a regular non-symlink file")
            identity = (opened.st_dev, opened.st_ino)
            stable = (
                opened.st_mode,
                opened.st_size,
                opened.st_mtime_ns,
                opened.st_ctime_ns,
            )
            chunks: list[bytes] = []
            while True:
                chunk = os.read(descriptor, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
            after_descriptor = os.fstat(descriptor)
            try:
                after_path = os.stat(
                    self.path.name,
                    dir_fd=self.parent_descriptor,
                    follow_symlinks=False,
                )
            except OSError as error:
                raise ValueError("preferences store changed while it was read") from error
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
                raise ValueError("preferences store changed while it was read")
        finally:
            os.close(descriptor)
        self.attest()
        try:
            value = json.loads(
                b"".join(chunks).decode("utf-8"),
                object_pairs_hook=_unique_object,
            )
        except (UnicodeError, json.JSONDecodeError) as error:
            raise ValueError(f"preferences store is not valid JSON: {error}") from error
        if not isinstance(value, dict):
            raise ValueError("preferences store must be a JSON object")
        return _validate_preferences(value)

    def write(self, payload: object) -> None:
        self.attest()
        flags = os.O_CREAT | os.O_EXCL | os.O_RDWR | os.O_NOFOLLOW
        if hasattr(os, "O_CLOEXEC"):
            flags |= os.O_CLOEXEC
        temporary_name: str | None = None
        descriptor: int | None = None
        for _attempt in range(100):
            candidate = f".{self.path.name}.{secrets.token_hex(16)}.tmp"
            try:
                descriptor = os.open(
                    candidate,
                    flags,
                    0o600,
                    dir_fd=self.parent_descriptor,
                )
            except FileExistsError:
                continue
            temporary_name = candidate
            break
        if descriptor is None or temporary_name is None:
            raise ValueError("preferences store could not create an atomic temporary file")
        try:
            os.fchmod(descriptor, 0o600)
            serialized = io.StringIO()
            json.dump(payload, serialized, sort_keys=True, indent=2)
            expected_bytes = (serialized.getvalue() + "\n").encode("utf-8")
            remaining = memoryview(expected_bytes)
            while remaining:
                written = os.write(descriptor, remaining)
                if written < 1:
                    raise OSError("preferences store atomic write made no progress")
                remaining = remaining[written:]
            os.fsync(descriptor)
            temporary_opened = os.fstat(descriptor)
            os.lseek(descriptor, 0, os.SEEK_SET)
            chunks: list[bytes] = []
            while True:
                chunk = os.read(descriptor, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
            temporary_after = os.fstat(descriptor)
            temporary_at_path = os.stat(
                temporary_name,
                dir_fd=self.parent_descriptor,
                follow_symlinks=False,
            )
            temporary_identity = (
                temporary_opened.st_dev,
                temporary_opened.st_ino,
            )
            actual_bytes = b"".join(chunks)
            if (
                not stat.S_ISREG(temporary_opened.st_mode)
                or stat.S_IMODE(temporary_opened.st_mode) != 0o600
                or (temporary_after.st_dev, temporary_after.st_ino)
                != temporary_identity
                or (temporary_at_path.st_dev, temporary_at_path.st_ino)
                != temporary_identity
                or temporary_after.st_size != len(expected_bytes)
                or temporary_at_path.st_size != len(expected_bytes)
                or actual_bytes != expected_bytes
            ):
                raise ValueError("preferences store atomic temporary file changed")
            self.attest()
            os.replace(
                temporary_name,
                self.path.name,
                src_dir_fd=self.parent_descriptor,
                dst_dir_fd=self.parent_descriptor,
            )
            temporary_name = None
            previous_descriptor = self.committed_descriptor
            self.committed_descriptor = descriptor
            self.committed_identity = temporary_identity
            self.committed_bytes = expected_bytes
            self.committed_sha256 = hashlib.sha256(expected_bytes).hexdigest()
            descriptor = None
            if previous_descriptor is not None:
                os.close(previous_descriptor)
            self.attest()
        finally:
            if descriptor is not None:
                os.close(descriptor)
            if temporary_name is not None:
                try:
                    os.unlink(temporary_name, dir_fd=self.parent_descriptor)
                except FileNotFoundError:
                    pass


_ACTIVE_PREFERENCE_TRANSACTION: ContextVar[_PreferenceTransaction | None] = (
    ContextVar("active_fiction_voice_preference_transaction", default=None)
)


def load_preferences(path: Path = DEFAULT_PATH) -> dict[str, object]:
    """Read validated preferences, or supply the durable defaults without writing."""
    path = Path(path)
    transaction = _ACTIVE_PREFERENCE_TRANSACTION.get()
    if transaction is not None and transaction.matches(path):
        return transaction.load()
    _refuse_symlink(path, "preferences store")
    if not path.exists():
        return initial_preferences()
    return _validate_preferences(_json_object(path, "preferences store"))


def _atomic_json(path: Path, payload: object, label: str) -> None:
    path = Path(path)
    transaction = _ACTIVE_PREFERENCE_TRANSACTION.get()
    if transaction is not None and transaction.matches(path):
        transaction.write(payload)
        return
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
    directory_locked = False
    transaction_token = None
    transaction: _PreferenceTransaction | None = None
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
        fcntl.flock(parent_descriptor, fcntl.LOCK_EX)
        directory_locked = True
        transaction = _PreferenceTransaction(
            path,
            parent_descriptor,
            parent_identity,
            lock_descriptor,
            (lock_opened.st_dev, lock_opened.st_ino),
            lock_path.name,
        )
        transaction.attest()
        transaction_token = _ACTIVE_PREFERENCE_TRANSACTION.set(transaction)
        yield
        transaction.attest()
    finally:
        if transaction_token is not None:
            _ACTIVE_PREFERENCE_TRANSACTION.reset(transaction_token)
        if transaction is not None:
            transaction.close()
        if directory_locked:
            fcntl.flock(parent_descriptor, fcntl.LOCK_UN)
        if lock_descriptor is not None:
            fcntl.flock(lock_descriptor, fcntl.LOCK_UN)
            os.close(lock_descriptor)
        os.close(parent_descriptor)


def _used_voices(preferences: dict[str, Any]) -> set[str]:
    voices: set[str] = set()
    for use in preferences["uses"]:
        has_chapters = "chapters" in use
        has_speakers = "speakers" in use
        if has_chapters and has_speakers:
            raise ValueError("preference use contains both chapters and speakers")
        if not has_chapters and not has_speakers:
            raise ValueError("preference use contains neither chapters nor speakers")
        rows = use["chapters"] if has_chapters else use["speakers"]
        voices.update(row["voice"] for row in rows)
    return voices


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


def _authored_block_plan(
    cast: dict[str, Any], voice_plan_path: Path, *, content: bytes | None = None
) -> tuple[dict[str, Any], bytes]:
    authored = _require_dict(cast.get("authoredVoicePlan"), "authored voice plan")
    if set(authored) != {"fileName", "sha256"}:
        raise ValueError("authored voice plan must contain exact fileName and sha256")
    filename = _filename(authored.get("fileName"), "authored voice plan filename")
    expected_hash = _sha256(authored.get("sha256"), "authored voice-plan hash")
    path = Path(voice_plan_path)
    if not path.is_absolute() or path.resolve(strict=False) != path:
        raise ValueError("authored voice plan must be a canonical absolute path")
    if path.name != filename:
        raise ValueError("authored voice plan filename differs from voice cast")
    if content is None:
        content = _stable_regular_bytes(path, "authored voice plan")
    if hashlib.sha256(content).hexdigest() != expected_hash:
        raise ValueError("authored voice-plan hash differs from voice cast")
    payload = _strict_json_object_bytes(content, "authored voice plan")
    if set(payload) != AUTHORED_VOICE_PLAN_FIELDS:
        raise ValueError("authored voice plan must contain exact Echo schema-1 fields")
    if type(payload.get("schemaVersion")) is not int or payload["schemaVersion"] != 1:
        raise ValueError("authored voice plan schemaVersion must be integer 1")
    source = _require_dict(payload.get("source"), "authored voice plan source")
    if set(source) != AUTHORED_VOICE_PLAN_SOURCE_FIELDS:
        raise ValueError("authored voice plan source must contain exact epubSHA256")
    if source.get("epubSHA256") != cast.get("sourceEPUBSHA256"):
        raise ValueError("authored voice plan source EPUB differs from voice cast")
    if payload.get("defaultSpeakerID") != cast.get("defaultSpeakerID"):
        raise ValueError("authored voice plan default speaker differs from voice cast")
    plan_speakers = _require_list(payload.get("speakers"), "authored voice plan speakers")
    expected_speakers = [
        {"id": row["speakerID"], "voiceID": row["voiceID"]}
        for row in cast["speakers"]
    ]
    for row in plan_speakers:
        data = _require_dict(row, "authored voice plan speaker")
        if set(data) != AUTHORED_VOICE_PLAN_SPEAKER_FIELDS:
            raise ValueError("authored voice plan speakers must contain exact id and voiceID")
    if plan_speakers != expected_speakers:
        raise ValueError("authored voice plan speakers differ from voice cast")
    _require_list(payload.get("assignments"), "authored voice plan assignments")
    return payload, content


def _validate_block_cast_contract(
    cast: dict[str, Any],
    voice_plan_path: Path,
    *,
    require_unverified: bool,
    authored_plan_content: bytes | None = None,
) -> dict[str, Any]:
    if set(cast) != BLOCK_CAST_FIELDS:
        raise ValueError("block voice cast must contain exact schema-2 fields")
    if type(cast.get("schemaVersion")) is not int or cast["schemaVersion"] != 2:
        raise ValueError("block cast schemaVersion must be integer 2")
    if not isinstance(cast.get("slug"), str) or not cast["slug"]:
        raise ValueError("block cast slug must be non-empty text")
    if cast.get("narrationMode") != "block":
        raise ValueError("block cast narrationMode must be block")
    _sha256(cast.get("sourceEPUBSHA256"), "block cast source EPUB SHA-256")
    default_speaker = cast.get("defaultSpeakerID")
    if not isinstance(default_speaker, str) or not default_speaker:
        raise ValueError("block cast default speaker must be non-empty text")
    speakers = _require_list(cast.get("speakers"), "block cast speakers")
    speaker_ids: set[str] = set()
    roles: set[str] = set()
    voices: set[str] = set()
    experimental_rows: list[dict[str, Any]] = []
    for row in speakers:
        data = _require_dict(row, "block cast speaker")
        if set(data) != BLOCK_SPEAKER_FIELDS:
            raise ValueError("block cast speaker must contain exact schema-2 fields")
        speaker_id = data.get("speakerID")
        role = data.get("role")
        if not isinstance(speaker_id, str) or not speaker_id:
            raise ValueError("block cast speakerID must be non-empty text")
        if not isinstance(role, str) or not role:
            raise ValueError("block cast role must be non-empty text")
        if speaker_id in speaker_ids:
            raise ValueError(f"block cast speakerID is not unique: {speaker_id}")
        if role in roles:
            raise ValueError(f"block cast role is not unique: {role}")
        speaker_ids.add(speaker_id)
        roles.add(role)
        voices.add(_known_voice(data.get("voiceID"), "block cast voiceID"))
        if type(data.get("experimental")) is not bool:
            raise ValueError("block cast experimental must be a real boolean")
        if data["experimental"]:
            experimental_rows.append(data)
    if default_speaker not in speaker_ids:
        raise ValueError("block cast default speaker must match a speakerID")
    if not 3 <= len(voices) <= 5:
        raise ValueError("block cast requires three to five distinct voices")
    if len(experimental_rows) > 2:
        raise ValueError("block cast allows at most two experimental speakers")
    _authored_block_plan(cast, voice_plan_path, content=authored_plan_content)
    if require_unverified and cast.get("resolvedVoicePlan") is not None:
        raise ValueError("block cast resolvedVoicePlan must be null before narration")
    if require_unverified and cast.get("verifiedArtifacts") is not None:
        raise ValueError("block cast verifiedArtifacts must be null before narration")
    return cast


def _validate_block_preferences(
    cast: dict[str, Any], preferences: dict[str, Any], *, check_used_voices: bool = True
) -> None:
    blacklist = preferences["blacklist"]
    assert isinstance(blacklist, dict)
    for row in cast["speakers"]:
        voice = row["voiceID"]
        if voice in blacklist:
            raise ValueError(f"block cast voice is blacklisted: {voice}")
    if not check_used_voices:
        return
    used_voices = _used_voices(preferences)
    for row in cast["speakers"]:
        if row["experimental"] and row["voiceID"] in used_voices:
            raise ValueError(f"experimental voice was already used: {row['voiceID']}")


def validate_block_cast(
    cast: dict[str, object],
    voice_plan_path: Path,
    preferences: dict[str, object],
) -> dict[str, object]:
    """Validate source-bound block cast inputs without resolving Echo assignments."""
    data = _validate_block_cast_contract(
        _require_dict(cast, "cast"), Path(voice_plan_path), require_unverified=True
    )
    checked_preferences = _validate_preferences(
        _require_dict(preferences, "preferences")
    )
    _validate_block_preferences(data, checked_preferences)
    return data


def validate_cast(cast: dict[str, object], preferences: dict[str, object]) -> dict[str, object]:
    """Reject invalid casts and return Echo's canonical chapter-voice plan."""
    return _validate_cast(
        _require_dict(cast, "cast"),
        _validate_preferences(_require_dict(preferences, "preferences")),
        require_unverified=True,
    )


def _block_sibling_plan_path(cast: dict[str, Any], cast_path: Path) -> Path:
    path = Path(cast_path)
    if not path.is_absolute() or path.resolve(strict=False) != path:
        raise ValueError("block voice cast path must be canonical and absolute")
    _refuse_symlink(path, "block voice cast")
    authored = _require_dict(cast.get("authoredVoicePlan"), "authored voice plan")
    filename = _filename(authored.get("fileName"), "authored voice plan filename")
    return path.parent / filename


def _validate_completed_block_cast(
    cast: dict[str, Any], cast_path: Path | None
) -> dict[str, object]:
    if cast_path is None:
        raise ValueError("completed block cast requires its voice-cast path")
    plan_path = _block_sibling_plan_path(cast, cast_path)
    _validate_block_cast_contract(cast, plan_path, require_unverified=False)
    resolved = _require_dict(cast.get("resolvedVoicePlan"), "block resolved voice plan")
    if set(resolved) != RESOLVER_KEYS:
        raise ValueError("block resolved voice plan must contain exact Echo receipt fields")
    if type(resolved.get("blockCount")) is not int or resolved["blockCount"] < 1:
        raise ValueError("block resolved voice plan blockCount must be positive")
    default_voice = _known_voice(
        resolved.get("defaultVoice"), "block resolved voice plan default voice"
    )
    source = _sha256(
        resolved.get("sourceEPUBSHA256"), "block resolved voice plan source EPUB SHA-256"
    )
    plan_hash = _sha256(
        resolved.get("voicePlanSHA256"), "block resolved voice-plan hash"
    )
    plan_id = resolved.get("voicePlanID")
    if not isinstance(plan_id, str) or plan_id != f"plan-{plan_hash[:12]}":
        raise ValueError("block resolved voice-plan identity does not bind its hash")
    if source != cast["sourceEPUBSHA256"]:
        raise ValueError("block resolved voice plan source EPUB differs from voice cast")
    cast_default_voice = next(
        row["voiceID"]
        for row in cast["speakers"]
        if row["speakerID"] == cast["defaultSpeakerID"]
    )
    if default_voice != cast_default_voice:
        raise ValueError("block resolved voice plan default voice differs from voice cast")
    verified = _require_dict(cast.get("verifiedArtifacts"), "block cast verifiedArtifacts")
    if set(verified) != VERIFIED_ARTIFACT_FIELDS:
        raise ValueError("block cast verifiedArtifacts must contain exact governed hashes")
    for field in VERIFIED_ARTIFACT_FIELDS:
        _sha256(verified.get(field), f"block cast verifiedArtifacts {field}")
    if verified["sourceEPUBSHA256"] != source:
        raise ValueError("block cast verified source EPUB differs from resolved voice plan")
    if verified["voicePlanSHA256"] != plan_hash:
        raise ValueError("block cast verified voice-plan hash differs from resolved voice plan")
    return resolved


def validate_completed_cast(
    cast: dict[str, object], *, cast_path: Path | None = None
) -> dict[str, object]:
    """Validate a completed chapter or source-bound block cast."""
    data = _require_dict(cast, "cast")
    if type(data.get("schemaVersion")) is int and data["schemaVersion"] == 2:
        return _validate_completed_block_cast(data, cast_path)
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


def _read_stable_regular_file(
    path: Path, label: str
) -> tuple[bytes, tuple[int, int, int, int, int, int]]:
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
        return b"".join(chunks), (
            opened.st_dev,
            opened.st_ino,
            opened.st_mode,
            opened.st_size,
            opened.st_mtime_ns,
            opened.st_ctime_ns,
        )
    finally:
        os.close(descriptor)


def _stable_regular_bytes(path: Path, label: str) -> bytes:
    return _read_stable_regular_file(path, label)[0]


def _stable_regular_snapshot(path: Path, label: str) -> _StableFileSnapshot:
    content, identity = _read_stable_regular_file(path, label)
    return _StableFileSnapshot(
        path=Path(path),
        label=label,
        device=identity[0],
        inode=identity[1],
        mode=identity[2],
        size=identity[3],
        mtime_ns=identity[4],
        ctime_ns=identity[5],
        content=content,
        sha256=hashlib.sha256(content).hexdigest(),
    )


def _require_stable_snapshots_unchanged(
    snapshots: tuple[_StableFileSnapshot, ...]
) -> None:
    for snapshot in snapshots:
        current = _stable_regular_snapshot(snapshot.path, snapshot.label)
        if (
            current.content != snapshot.content
            or current.sha256 != snapshot.sha256
            or (
                current.device,
                current.inode,
                current.mode,
                current.size,
                current.mtime_ns,
                current.ctime_ns,
            )
            != (
                snapshot.device,
                snapshot.inode,
                snapshot.mode,
                snapshot.size,
                snapshot.mtime_ns,
                snapshot.ctime_ns,
            )
        ):
            raise ValueError(f"{snapshot.label} changed after validation")


def _input_receipt_fields(input_bytes: bytes) -> dict[str, str]:
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
    return input_fields


def _relocated_block_evidence_path(
    value: object, expected_name: str, label: str
) -> Path:
    path = Path(value) if isinstance(value, str) else None
    if (
        path is None
        or not path.is_absolute()
        or str(path) != value
        or any(part in {".", ".."} for part in path.parts)
        or path.name != expected_name
    ):
        raise ValueError(
            f"Echo input receipt {label} is not a canonical plan filename"
        )
    return path


def _validate_relocated_block_evidence_paths(
    fields: dict[str, str], canonical_path: Path, resolution_path: Path, receipt_path: Path
) -> None:
    """Bind relocated source paths as one sibling set, not independent names."""
    historical_canonical = _relocated_block_evidence_path(
        fields.get("voice_plan_canonical_path"),
        canonical_path.name,
        "canonical voice-plan path",
    )
    historical_resolution = _relocated_block_evidence_path(
        fields.get("voice_plan_resolution_path"),
        resolution_path.name,
        "voice-plan resolution path",
    )
    captured_parent = receipt_path.parent
    if (
        historical_canonical.parent != historical_resolution.parent
        or canonical_path.parent != captured_parent
        or resolution_path.parent != captured_parent
    ):
        raise ValueError(
            "Echo relocated block evidence must map one sibling parent to the captured success-receipt directory"
        )
    original_parent = historical_canonical.parent
    expected_mapping = {
        original_parent / canonical_path.name: captured_parent / canonical_path.name,
        original_parent / resolution_path.name: captured_parent / resolution_path.name,
    }
    actual_mapping = {
        historical_canonical: canonical_path,
        historical_resolution: resolution_path,
    }
    if actual_mapping != expected_mapping:
        raise ValueError(
            "Echo relocated block evidence does not map the original sibling set to the captured success-receipt directory"
        )


def validate_block_echo_success_receipt(
    receipt: dict[str, object],
    receipt_path: Path,
    cast: dict[str, Any],
    epub: Path,
    *,
    authored_plan_path: Path | None = None,
    authored_plan_bytes: bytes | None = None,
    input_receipt_loader: Callable[[Path, str], bytes] | None = None,
    canonical_plan_loader: Callable[[Path, str], bytes] | None = None,
    resolution_loader: Callable[[Path, str], bytes] | None = None,
    allow_relocated_evidence: bool = False,
) -> dict[str, object]:
    """Bind an Echo schema-4 block receipt without resolving assignments in Python.

    A copied private evidence set may retain the source run's absolute plan paths.
    Callers that set ``allow_relocated_evidence`` still bind the names and hashes to
    the captured sibling files, while the production recorder keeps exact paths.
    """
    if type(receipt.get("schemaVersion")) is not int or receipt["schemaVersion"] != 4:
        raise ValueError("Echo success receipt schemaVersion must be integer 4")
    try:
        require_block_success_receipt(receipt, "Echo success receipt")
    except StateError as error:
        raise ValueError(str(error)) from error
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
    plan_hash = _sha256(receipt.get("voicePlanSHA256"), "Echo voice-plan hash")
    plan_id = receipt.get("voicePlanID")
    if not isinstance(plan_id, str) or plan_id != f"plan-{plan_hash[:12]}":
        raise ValueError("Echo voice-plan identity does not bind its hash")
    receipt_path = Path(receipt_path)
    authored = _require_dict(cast.get("authoredVoicePlan"), "authored voice plan")
    authored_filename = _filename(
        authored.get("fileName"), "authored voice plan filename"
    )
    authored_path = (
        Path(authored_plan_path)
        if authored_plan_path is not None
        else receipt_path.parent / authored_filename
    )
    authored_payload, _ = _authored_block_plan(
        cast, authored_path, content=authored_plan_bytes
    )
    if receipt_path.name != f"echo-render-success-{run_id}-{attempt_id}.json":
        raise ValueError("Echo success receipt filename is not derived from runID")
    if receipt.get("artifactRelativePath") != f"echo-renders/{run_id}/{attempt_id}":
        raise ValueError("Echo artifact path is not derived from runID and attemptID")
    if receipt.get("inputReceiptFileName") != f"echo-render-inputs-{run_id}.env":
        raise ValueError("Echo input receipt filename is not derived from runID")
    input_loader = input_receipt_loader or _stable_regular_bytes
    input_path = receipt_path.parent / str(receipt["inputReceiptFileName"])
    input_bytes = input_loader(input_path, "Echo input receipt")
    if hashlib.sha256(input_bytes).hexdigest() != _sha256(
        receipt.get("inputReceiptSHA256"), "Echo success receipt inputReceiptSHA256"
    ):
        raise ValueError("Echo input receipt bytes differ from success receipt")
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
    for field in ("auditFileName", "reelFileName"):
        if field in receipt:
            _filename(receipt[field], f"Echo success receipt {field}")

    canonical_path = receipt_path.parent / str(receipt["voicePlanCanonicalFileName"])
    canonical_bytes = (canonical_plan_loader or _stable_regular_bytes)(
        canonical_path, "Echo canonical voice plan"
    )
    if hashlib.sha256(canonical_bytes).hexdigest() != _sha256(
        receipt.get("voicePlanCanonicalSHA256"),
        "Echo success receipt voicePlanCanonicalSHA256",
    ):
        raise ValueError("Echo canonical voice-plan bytes differ from success receipt")
    canonical_payload = _strict_json_object_bytes(
        canonical_bytes, "Echo canonical voice plan"
    )
    if canonical_bytes != (
        json.dumps(
            canonical_payload,
            sort_keys=True,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8"):
        raise ValueError("Echo canonical voice plan is not canonical JSON")
    if not _same_json_value(canonical_payload, authored_payload):
        raise ValueError("Echo canonical voice plan differs from authored voice plan")

    resolution_path = receipt_path.parent / str(receipt["voicePlanResolutionFileName"])
    resolution_bytes = (resolution_loader or _stable_regular_bytes)(
        resolution_path, "Echo voice-plan resolution"
    )
    if hashlib.sha256(resolution_bytes).hexdigest() != _sha256(
        receipt.get("voicePlanResolutionSHA256"),
        "Echo success receipt voicePlanResolutionSHA256",
    ):
        raise ValueError("Echo voice-plan resolution bytes differ from success receipt")
    try:
        resolved = validate_resolver_receipt(resolution_bytes, Path(epub))
    except VoicePlanError as error:
        raise ValueError(f"Echo voice-plan resolution is invalid: {error}") from error
    if resolved["sourceEPUBSHA256"] != cast["sourceEPUBSHA256"]:
        raise ValueError("Echo resolved source EPUB differs from voice cast")
    default_voice = next(
        row["voiceID"]
        for row in cast["speakers"]
        if row["speakerID"] == cast["defaultSpeakerID"]
    )
    if resolved["defaultVoice"] != default_voice:
        raise ValueError("Echo resolved default voice differs from voice cast")
    for receipt_field, resolved_field in (
        ("voicePlanID", "voicePlanID"),
        ("voicePlanSHA256", "voicePlanSHA256"),
        ("voicePlanBlockCount", "blockCount"),
    ):
        if receipt[receipt_field] != resolved[resolved_field]:
            raise ValueError(
                f"Echo success receipt {receipt_field} differs from sealed resolution"
            )
    fields = _input_receipt_fields(input_bytes)
    expected_input = {
        "voice": str(resolved["defaultVoice"]),
        "chapter_voices": "",
        "voice_plan_mode": "block",
        "voice_plan_sha256": str(resolved["voicePlanSHA256"]),
        "voice_plan_id": str(resolved["voicePlanID"]),
        "voice_plan_block_count": str(resolved["blockCount"]),
        "voice_plan_canonical_path": str(canonical_path),
        "voice_plan_canonical_sha256": str(receipt["voicePlanCanonicalSHA256"]),
        "voice_plan_resolution_path": str(resolution_path),
        "voice_plan_resolution_sha256": str(receipt["voicePlanResolutionSHA256"]),
    }
    input_labels = {
        "voice": "default voice",
        "chapter_voices": "chapter voices",
        "voice_plan_mode": "voice-plan mode",
        "voice_plan_sha256": "voice-plan hash",
        "voice_plan_id": "voice-plan identity",
        "voice_plan_block_count": "block count",
        "voice_plan_canonical_path": "canonical voice-plan path",
        "voice_plan_canonical_sha256": "canonical voice-plan hash",
        "voice_plan_resolution_path": "voice-plan resolution path",
        "voice_plan_resolution_sha256": "voice-plan resolution hash",
    }
    for key, value in expected_input.items():
        if allow_relocated_evidence and key in {
            "voice_plan_canonical_path",
            "voice_plan_resolution_path",
        }:
            continue
        if fields.get(key) != value:
            raise ValueError(
                f"Echo input receipt {input_labels[key]} differs from sealed block evidence"
            )
    # Block runs intentionally use Echo's collision-free operational component:
    # ``plan-<full resolved SHA-256>``.  ``voicePlanID`` remains the short,
    # human-facing display identity and must not reconstruct a block RUN_ID.
    run_voice_identity = f"plan-{resolved['voicePlanSHA256']}"
    source_hash = _sha256(
        receipt.get("sourceEPUBSHA256"), "Echo source EPUB SHA-256"
    )
    expected_run_id = (
        f"{source_hash[:12]}-{receipt['echoCLI_SHA256'][:12]}-"
        f"{receipt['echoResourcesSHA256'][:12]}-"
        f"{receipt['rendererManifestSHA256'][:12]}-"
        f"{receipt['echoSourceSHA']}-{run_voice_identity}"
    )
    if run_id != expected_run_id:
        raise ValueError(
            "Echo success receipt runID does not match source EPUB, renderer provenance, and resolved voice plan"
        )
    if allow_relocated_evidence:
        _validate_relocated_block_evidence_paths(
            fields, canonical_path, resolution_path, receipt_path
        )
    return resolved


def validate_echo_success_receipt(
    receipt: dict[str, object],
    receipt_path: Path,
    cast: dict[str, object],
    *,
    input_receipt_loader: Callable[[Path, str], bytes] | None = None,
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
    loader = input_receipt_loader or _stable_regular_bytes
    input_bytes = loader(input_receipt, "Echo input receipt")
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


def _block_receipt_artifacts(
    cast: dict[str, Any],
    epub: Path,
    m4b: Path,
    sidecar: Path,
    success_receipt: Path,
    authored_plan_snapshot: _StableFileSnapshot,
) -> tuple[
    dict[str, str],
    dict[str, object],
    str,
    tuple[_StableFileSnapshot, ...],
]:
    success_snapshot = _stable_regular_snapshot(
        success_receipt, "Echo success receipt"
    )
    receipt = _strict_json_object_bytes(
        success_snapshot.content, "Echo success receipt"
    )
    input_receipt_snapshots: list[_StableFileSnapshot] = []
    canonical_plan_snapshots: list[_StableFileSnapshot] = []
    resolution_snapshots: list[_StableFileSnapshot] = []

    def capture_input_receipt(path: Path, label: str) -> bytes:
        snapshot = _stable_regular_snapshot(path, label)
        input_receipt_snapshots.append(snapshot)
        return snapshot.content

    def capture_canonical_plan(path: Path, label: str) -> bytes:
        snapshot = _stable_regular_snapshot(path, label)
        canonical_plan_snapshots.append(snapshot)
        return snapshot.content

    def capture_resolution(path: Path, label: str) -> bytes:
        snapshot = _stable_regular_snapshot(path, label)
        resolution_snapshots.append(snapshot)
        return snapshot.content

    resolved = validate_block_echo_success_receipt(
        receipt,
        success_receipt,
        cast,
        epub,
        authored_plan_path=authored_plan_snapshot.path,
        authored_plan_bytes=authored_plan_snapshot.content,
        input_receipt_loader=capture_input_receipt,
        canonical_plan_loader=capture_canonical_plan,
        resolution_loader=capture_resolution,
    )
    if len(input_receipt_snapshots) != 1:
        raise ValueError("Echo input receipt was not captured exactly once")
    if len(canonical_plan_snapshots) != 1:
        raise ValueError("Echo canonical voice plan was not captured exactly once")
    if len(resolution_snapshots) != 1:
        raise ValueError("Echo voice-plan resolution was not captured exactly once")
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
    if verified["sourceEPUBSHA256"] != cast["sourceEPUBSHA256"]:
        raise ValueError("block cast source EPUB differs from supplied EPUB")
    verified["voicePlanSHA256"] = str(resolved["voicePlanSHA256"])
    return (
        verified,
        resolved,
        success_snapshot.sha256,
        (
            authored_plan_snapshot,
            success_snapshot,
            input_receipt_snapshots[0],
            canonical_plan_snapshots[0],
            resolution_snapshots[0],
        ),
    )


def _load_cast(path: Path) -> dict[str, Any]:
    return _json_object(Path(path), "voice cast")


def _record_block_use(
    cast: dict[str, Any],
    cast_path: Path,
    epub: Path,
    m4b: Path,
    sidecar: Path,
    success_receipt: Path,
    at: str,
    preferences: dict[str, Any],
    preferences_path: Path,
) -> dict[str, object]:
    plan_path = _block_sibling_plan_path(cast, cast_path)
    authored_plan_snapshot = _stable_regular_snapshot(plan_path, "authored voice plan")
    _validate_block_cast_contract(
        cast,
        plan_path,
        require_unverified=False,
        authored_plan_content=authored_plan_snapshot.content,
    )
    _validate_block_preferences(cast, preferences, check_used_voices=False)
    verified, resolved, success_receipt_sha256, governed_snapshots = (
        _block_receipt_artifacts(
            cast,
            epub,
            m4b,
            sidecar,
            success_receipt,
            authored_plan_snapshot,
        )
    )
    proposed_cast = dict(cast)
    changed_cast = False
    existing_resolved = proposed_cast.get("resolvedVoicePlan")
    if existing_resolved is None:
        proposed_cast["resolvedVoicePlan"] = resolved
        changed_cast = True
    elif existing_resolved != resolved:
        raise ValueError(
            "block cast resolvedVoicePlan differs from the supplied sealed resolution"
        )
    existing_verified = proposed_cast.get("verifiedArtifacts")
    if existing_verified is None:
        proposed_cast["verifiedArtifacts"] = verified
        changed_cast = True
    elif existing_verified != verified:
        raise ValueError(
            "block cast verifiedArtifacts differ from the supplied governed artifacts"
        )

    use_key = (
        proposed_cast["slug"],
        verified["audiobookSHA256"],
        verified["voicePlanSHA256"],
    )
    existing_use = any(
        (
            use["slug"],
            use["audiobookSHA256"],
            use["voicePlanSHA256"],
        )
        == use_key
        for use in preferences["uses"]
    )
    proposed_preferences = preferences
    if not existing_use:
        _validate_block_preferences(proposed_cast, preferences)
        proposed_preferences = dict(preferences)
        proposed_preferences["uses"] = [
            *preferences["uses"],
            {
                "slug": proposed_cast["slug"],
                "recordedAt": at,
                "sourceEPUBSHA256": verified["sourceEPUBSHA256"],
                "audiobookSHA256": verified["audiobookSHA256"],
                "sidecarSHA256": verified["sidecarSHA256"],
                "voicePlanSHA256": verified["voicePlanSHA256"],
                "successReceiptSHA256": success_receipt_sha256,
                "narrationMode": "block",
                "speakers": [
                    {"speakerID": row["speakerID"], "voice": row["voiceID"]}
                    for row in proposed_cast["speakers"]
                ],
            },
        ]
        proposed_preferences["updatedAt"] = at
        _validate_preferences(proposed_preferences)
    _require_stable_snapshots_unchanged(governed_snapshots)
    if changed_cast:
        _atomic_json(cast_path, proposed_cast, "voice cast")
    if existing_use:
        return preferences
    _atomic_json(preferences_path, proposed_preferences, "preferences store")
    return proposed_preferences


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
        if type(cast.get("schemaVersion")) is int and cast["schemaVersion"] == 2:
            return _record_block_use(
                cast,
                cast_path,
                Path(epub),
                Path(m4b),
                Path(sidecar),
                Path(success_receipt),
                at,
                preferences,
                preferences_path,
            )
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
    validate.add_argument("--voice-plan", type=Path)
    validate.add_argument("--preferences", type=Path, default=DEFAULT_PATH)
    validate.add_argument("--format", choices=("json", "argv0"), default="json")
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
            if type(cast.get("schemaVersion")) is int and cast["schemaVersion"] == 2:
                if options.voice_plan is None:
                    raise ValueError("block cast validate-cast requires --voice-plan")
                cast_path = Path(options.cast)
                voice_plan_path = Path(options.voice_plan)
                if (
                    not cast_path.is_absolute()
                    or cast_path.resolve(strict=False) != cast_path
                    or voice_plan_path.parent != cast_path.parent
                ):
                    raise ValueError("block cast voice plan must be a sibling of voice cast")
                validate_block_cast(
                    cast, voice_plan_path, load_preferences(options.preferences)
                )
                result: object = ["--voice-plan", str(voice_plan_path)]
            else:
                if options.voice_plan is not None:
                    raise ValueError("chapter cast validate-cast does not accept --voice-plan")
                plan = validate_cast(cast, load_preferences(options.preferences))
                result = [
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
    if options.command == "validate-cast" and options.format == "argv0":
        assert isinstance(result, list)
        sys.stdout.buffer.write(
            b"".join(
                str(token).encode("utf-8") + b"\0" for token in result
            )
        )
        return 0
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
