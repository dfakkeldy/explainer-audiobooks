#!/usr/bin/env python3
"""Seal Echo narration inputs, resume captures, and completed output bytes."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import tempfile
from pathlib import Path

from echo_pronunciation_lease import load_capability, validate_capability


SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
MARKER_PATTERN = re.compile(r"\.anchors-ch([0-9]+)\.json")


class StateError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise StateError(message)


def require_mutation_leases(lock_root: Path, resources: tuple[Path, ...]) -> None:
    capability = load_capability()
    validate_capability(
        lock_root,
        sorted(str(resource.resolve()) for resource in resources),
        capability,
    )


def regular_file(path: Path, label: str) -> None:
    require(not path.is_symlink(), f"{label} must not be a symlink: {path}")
    try:
        mode = path.stat().st_mode
    except FileNotFoundError as error:
        raise StateError(f"{label} is missing: {path}") from error
    require(stat.S_ISREG(mode), f"{label} must be a regular file: {path}")


def open_regular(path: Path, label: str) -> int:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise StateError(f"{label} is missing or unsafe: {path}") from error
    if not stat.S_ISREG(os.fstat(descriptor).st_mode):
        os.close(descriptor)
        raise StateError(f"{label} must be a regular file: {path}")
    return descriptor


def read_regular_bytes(path: Path, label: str) -> bytes:
    descriptor = open_regular(path, label)
    with os.fdopen(descriptor, "rb", closefd=True) as input_file:
        return input_file.read()


def sha256(path: Path) -> str:
    descriptor = open_regular(path, "hashed file")
    with os.fdopen(descriptor, "rb", closefd=True) as input_file:
        return hashlib.file_digest(input_file, "sha256").hexdigest()


def hash_tree(root: Path) -> str:
    require(root.is_absolute(), "resource tree must be absolute")
    require(
        not root.is_symlink() and root.is_dir(),
        "resource tree must be a real directory",
    )
    hasher = hashlib.sha256()
    files: list[Path] = []
    for directory, directory_names, file_names in os.walk(root, followlinks=False):
        directory_path = Path(directory)
        for name in directory_names:
            require(
                not (directory_path / name).is_symlink(),
                f"resource tree contains symlink directory: {name}",
            )
        for name in file_names:
            path = directory_path / name
            regular_file(path, "resource")
            files.append(path)
    require(files, "resource tree is empty")
    for path in sorted(
        files, key=lambda candidate: candidate.relative_to(root).as_posix()
    ):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        size = path.stat().st_size
        for value in (relative, str(size).encode("ascii")):
            hasher.update(str(len(value)).encode("ascii") + b":" + value)
        descriptor = open_regular(path, "resource")
        with os.fdopen(descriptor, "rb", closefd=True) as input_file:
            while chunk := input_file.read(1_048_576):
                hasher.update(chunk)
    return hasher.hexdigest()


def safe_atomic_write(path: Path, content: bytes, *, immutable: bool) -> None:
    require(path.is_absolute(), "receipt path must be absolute")
    require(
        not path.parent.is_symlink() and path.parent.is_dir(),
        "receipt parent is unsafe",
    )
    if path.is_symlink():
        raise StateError(f"receipt must not be a symlink: {path}")
    if immutable and path.exists():
        regular_file(path, "existing receipt")
        require(
            read_regular_bytes(path, "existing receipt") == content,
            f"existing immutable receipt differs: {path}",
        )
        return

    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "wb", closefd=True) as output_file:
            descriptor = -1
            output_file.write(content)
            output_file.flush()
            os.fsync(output_file.fileno())
        if immutable:
            try:
                os.link(temporary, path, follow_symlinks=False)
            except FileExistsError:
                require(not path.is_symlink(), f"receipt must not be a symlink: {path}")
                regular_file(path, "concurrent receipt")
                require(
                    read_regular_bytes(path, "concurrent receipt") == content,
                    f"concurrent immutable receipt differs: {path}",
                )
        else:
            require(not path.is_symlink(), f"receipt must not be a symlink: {path}")
            os.replace(temporary, path)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        temporary.unlink(missing_ok=True)


def framed(value: str) -> bytes:
    encoded = value.encode("utf-8")
    return str(len(encoded)).encode("ascii") + b":" + encoded


def epub_fingerprint(epub: Path) -> str:
    regular_file(epub, "EPUB")
    raw = read_regular_bytes(epub, "EPUB")
    return hashlib.sha256(
        framed("source-kind=epub") + framed(f"bytes={len(raw)}") + raw
    ).hexdigest()


def capture_snapshot(
    work: Path,
    database: Path,
    epub: Path,
    source_sha: str,
    voice: str,
    input_receipt: Path,
) -> dict[str, object]:
    require(
        SHA256_PATTERN.fullmatch(source_sha) is not None
        or re.fullmatch(r"[0-9a-f]{40}", source_sha) is not None,
        "source SHA is invalid",
    )
    require(voice in {"am_michael", "am_puck"}, "resume voice is invalid")
    require(
        not work.is_symlink() and work.is_dir(),
        f"resume work directory is unsafe: {work}",
    )
    regular_file(database, "resume database")
    regular_file(input_receipt, "render-input receipt")
    expected_source = epub_fingerprint(epub)
    captures: list[dict[str, object]] = []
    capture_set_id: str | None = None
    indexes: set[int] = set()
    marker_paths = sorted(work.glob(".anchors-ch*.json"), key=lambda path: path.name)
    require(marker_paths, "resume state has no completed capture markers")
    for marker in marker_paths:
        regular_file(marker, "capture marker")
        match = MARKER_PATTERN.fullmatch(marker.name)
        require(match is not None, f"malformed capture marker name: {marker.name}")
        filename_index = int(match.group(1))
        require(filename_index not in indexes, "duplicate capture chapter index")
        indexes.add(filename_index)
        try:
            payload = json.loads(
                read_regular_bytes(marker, "capture marker").decode("utf-8")
            )
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise StateError(
                f"capture marker is not valid JSON: {marker.name}"
            ) from error
        require(
            isinstance(payload, dict),
            f"capture marker root must be an object: {marker.name}",
        )
        identity = payload.get("identity")
        require(
            isinstance(identity, dict),
            f"resume state requires a sealed Echo identity: {marker.name}",
        )
        require(
            type(identity.get("schemaVersion")) is int
            and identity["schemaVersion"] == 1,
            f"resume state requires capture schema 1: {marker.name}",
        )
        require(
            type(identity.get("renderVersion")) is int
            and identity["renderVersion"] == 12,
            f"resume state requires Echo render version 12: {marker.name}",
        )
        require(
            identity.get("sourceFingerprint") == expected_source,
            f"resume state source fingerprint differs: {marker.name}",
        )
        require(
            identity.get("voice") == voice, f"resume state voice differs: {marker.name}"
        )
        require(
            type(identity.get("chapterIndex")) is int
            and identity["chapterIndex"] == filename_index,
            f"resume state chapter index differs: {marker.name}",
        )
        for field in ("rendererIdentity", "normalizationMode"):
            require(
                isinstance(identity.get(field), str) and bool(identity[field]),
                f"resume state identity lacks {field}: {marker.name}",
            )
        for field in (
            "captureSetID",
            "chapterContentSignature",
            "audioSHA256",
            "payloadSHA256",
        ):
            require(
                isinstance(identity.get(field), str)
                and SHA256_PATTERN.fullmatch(identity[field]) is not None,
                f"resume state identity has invalid {field}: {marker.name}",
            )
        if capture_set_id is None:
            capture_set_id = identity["captureSetID"]
        require(
            identity["captureSetID"] == capture_set_id,
            "resume captures belong to different capture sets",
        )
        audio_name = identity.get("audioFileName")
        require(
            isinstance(audio_name, str)
            and audio_name
            and Path(audio_name).name == audio_name,
            f"resume state has unsafe audio filename: {marker.name}",
        )
        audio = work / audio_name
        regular_file(audio, "capture audio")
        require(
            type(identity.get("audioFileByteCount")) is int
            and identity["audioFileByteCount"] >= 0
            and identity["audioFileByteCount"] == audio.stat().st_size,
            f"resume capture audio size differs: {audio_name}",
        )
        audio_hash = sha256(audio)
        require(
            identity["audioSHA256"] == audio_hash,
            f"resume capture audio SHA-256 differs: {audio_name}",
        )
        require(
            isinstance(payload.get("pronunciationEvidence"), dict),
            f"resume state lacks pronunciation evidence: {marker.name}",
        )
        captures.append(
            {
                "chapterIndex": filename_index,
                "markerFileName": marker.name,
                "markerSHA256": sha256(marker),
                "audioFileName": audio_name,
                "audioSHA256": audio_hash,
                "payloadSHA256": identity["payloadSHA256"],
            }
        )
    return {
        "schemaVersion": 1,
        "echoSourceSHA": source_sha,
        "sourceFingerprint": expected_source,
        "voice": voice,
        "captureSetID": capture_set_id,
        "inputReceiptSHA256": sha256(input_receipt),
        "databaseSHA256": sha256(database),
        "databaseByteCount": database.stat().st_size,
        "captures": captures,
    }


def success_snapshot(
    run_id: str,
    input_receipt: Path,
    state_receipt: Path,
    audiobook: Path,
    sidecar: Path,
    audit: Path,
    reel: Path,
) -> dict[str, object]:
    for path, label in (
        (input_receipt, "render-input receipt"),
        (state_receipt, "resume-state receipt"),
        (audiobook, "audiobook"),
        (sidecar, "alignment sidecar"),
        (audit, "pronunciation audit"),
    ):
        regular_file(path, label)
    require(audiobook.stat().st_size > 0, "audiobook is empty")
    payload: dict[str, object] = {
        "schemaVersion": 1,
        "runID": run_id,
        "inputReceiptSHA256": sha256(input_receipt),
        "resumeStateSHA256": sha256(state_receipt),
        "audiobookFileName": audiobook.name,
        "audiobookSHA256": sha256(audiobook),
        "sidecarFileName": sidecar.name,
        "sidecarSHA256": sha256(sidecar),
        "auditFileName": audit.name,
        "auditSHA256": sha256(audit),
    }
    if reel.exists() or reel.is_symlink():
        regular_file(reel, "pronunciation reel")
        payload["reelFileName"] = reel.name
        payload["reelSHA256"] = sha256(reel)
    return payload


def canonical_json(payload: dict[str, object]) -> bytes:
    return (
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def verify_delivery_receipt(
    receipt: Path,
    audiobook: Path,
    sidecar: Path,
    audit: Path,
    reel: Path,
) -> None:
    regular_file(receipt, "render-success receipt")
    try:
        payload = json.loads(
            read_regular_bytes(receipt, "render-success receipt").decode("utf-8")
        )
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise StateError("render-success receipt is not valid JSON") from error
    require(
        isinstance(payload, dict) and payload.get("schemaVersion") == 1,
        "render-success receipt schema must be 1",
    )
    for path, name_field, hash_field, label in (
        (audiobook, "audiobookFileName", "audiobookSHA256", "audiobook"),
        (sidecar, "sidecarFileName", "sidecarSHA256", "alignment sidecar"),
        (audit, "auditFileName", "auditSHA256", "pronunciation audit"),
    ):
        regular_file(path, label)
        require(
            payload.get(name_field) == path.name,
            f"{label} filename differs from render-success receipt",
        )
        require(
            payload.get(hash_field) == sha256(path),
            f"{label} SHA-256 differs from render-success receipt",
        )
    expected_reel = payload.get("reelFileName")
    if expected_reel is None:
        require(
            not reel.exists() and not reel.is_symlink(),
            "unreceipted pronunciation reel is present",
        )
    else:
        regular_file(reel, "pronunciation reel")
        require(
            expected_reel == reel.name,
            "pronunciation reel filename differs from render-success receipt",
        )
        require(
            payload.get("reelSHA256") == sha256(reel),
            "pronunciation reel SHA-256 differs from render-success receipt",
        )


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    commands = root.add_subparsers(dest="command", required=True)
    hash_parser = commands.add_parser("hash-tree")
    hash_parser.add_argument("path", type=Path)
    immutable = commands.add_parser("immutable-file")
    immutable.add_argument("path", type=Path)
    for name in ("record-state", "verify-state"):
        command = commands.add_parser(name)
        command.add_argument("--work", type=Path, required=True)
        command.add_argument("--db", type=Path, required=True)
        command.add_argument("--receipt", type=Path, required=True)
        command.add_argument("--epub", type=Path, required=True)
        command.add_argument("--source-sha", required=True)
        command.add_argument("--voice", required=True)
        command.add_argument("--input-receipt", type=Path, required=True)
        command.add_argument("--lock-root", type=Path)
    reset = commands.add_parser("reset-state")
    reset.add_argument("--work", type=Path, required=True)
    reset.add_argument("--db", type=Path, required=True)
    reset.add_argument("--receipt", type=Path, required=True)
    reset.add_argument("--lock-root", type=Path, required=True)
    for name in ("write-success", "verify-success"):
        command = commands.add_parser(name)
        command.add_argument("--run-id", required=True)
        command.add_argument("--receipt", type=Path, required=True)
        command.add_argument("--input-receipt", type=Path, required=True)
        command.add_argument("--state-receipt", type=Path, required=True)
        command.add_argument("--audiobook", type=Path, required=True)
        command.add_argument("--sidecar", type=Path, required=True)
        command.add_argument("--audit", type=Path, required=True)
        command.add_argument("--reel", type=Path, required=True)
        command.add_argument("--lock-root", type=Path)
    delivery = commands.add_parser("verify-delivery")
    delivery.add_argument("--receipt", type=Path, required=True)
    delivery.add_argument("--audiobook", type=Path, required=True)
    delivery.add_argument("--sidecar", type=Path, required=True)
    delivery.add_argument("--audit", type=Path, required=True)
    delivery.add_argument("--reel", type=Path, required=True)
    return root


def main(arguments: list[str]) -> int:
    options = parser().parse_args(arguments)
    try:
        if options.command == "hash-tree":
            print(hash_tree(options.path.resolve()))
        elif options.command == "immutable-file":
            safe_atomic_write(options.path, sys.stdin.buffer.read(), immutable=True)
        elif options.command in {"record-state", "verify-state"}:
            payload = capture_snapshot(
                options.work,
                options.db,
                options.epub,
                options.source_sha,
                options.voice,
                options.input_receipt,
            )
            content = canonical_json(payload)
            if options.command == "record-state":
                require(
                    options.lock_root is not None, "record-state requires a lease root"
                )
                require_mutation_leases(options.lock_root, (options.work, options.db))
                safe_atomic_write(options.receipt, content, immutable=False)
            else:
                regular_file(options.receipt, "resume-state receipt")
                require(
                    read_regular_bytes(options.receipt, "resume-state receipt")
                    == content,
                    "resume state receipt does not match WORK, DB, or captures",
                )
        elif options.command == "reset-state":
            require_mutation_leases(options.lock_root, (options.work, options.db))
            for path in (options.work, options.db, options.receipt):
                require(path.is_absolute(), f"unsafe reset path: {path}")
                require(
                    not path.is_symlink(), f"reset path must not be a symlink: {path}"
                )
            if options.work.exists():
                require(
                    options.work.is_dir(), f"WORK is not a directory: {options.work}"
                )
                shutil.rmtree(options.work)
            options.db.unlink(missing_ok=True)
            options.receipt.unlink(missing_ok=True)
        elif options.command in {"write-success", "verify-success"}:
            payload = success_snapshot(
                options.run_id,
                options.input_receipt,
                options.state_receipt,
                options.audiobook,
                options.sidecar,
                options.audit,
                options.reel,
            )
            content = canonical_json(payload)
            if options.command == "write-success":
                require(
                    options.lock_root is not None, "write-success requires a lease root"
                )
                require_mutation_leases(
                    options.lock_root,
                    (options.audiobook, options.sidecar, options.audit, options.reel),
                )
                safe_atomic_write(options.receipt, content, immutable=False)
            else:
                regular_file(options.receipt, "render-success receipt")
                require(
                    read_regular_bytes(options.receipt, "render-success receipt")
                    == content,
                    "render-success receipt does not match delivered media",
                )
        elif options.command == "verify-delivery":
            verify_delivery_receipt(
                options.receipt,
                options.audiobook,
                options.sidecar,
                options.audit,
                options.reel,
            )
        return 0
    except (OSError, StateError, json.JSONDecodeError) as error:
        print(f"echo_pronunciation_state: {error}", file=sys.stderr)
        return 65


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
