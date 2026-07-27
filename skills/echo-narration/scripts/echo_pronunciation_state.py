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
CHAPTER_CONTENT_SIGNATURE_PATTERN = re.compile(r"[0-9a-f]{16}")
MARKER_PATTERN = re.compile(r"\.anchors-ch([0-9]+)\.json")
# epub-cli-resources-manifest-source-voice.
RUN_ID_PATTERN = re.compile(
    r"[0-9a-f]{12}-[0-9a-f]{12}-[0-9a-f]{12}-"
    r"[0-9a-f]{12}-[0-9a-f]{40}"
    r"-(?:am_michael|am_puck)"
)
LEGACY_RUN_ID_PATTERN = re.compile(
    r"[0-9a-f]{12}-[0-9a-f]{12}-[0-9a-f]{12}-"
    r"(?:[0-9a-f]{12}-)?"
    r"(?:[0-9a-f]{40}|[0-9a-f]{64})(?:-dirty-[0-9a-f]{8})?"
    r"-(?:am_michael|am_puck)"
)
RENDERER_IDENTITY_KEYS = (
    "rendererSchemaVersion",
    "rendererRoot",
    "rendererBuildRoot",
    "installerSourceSHA",
    "echoSourceSHA",
    "rendererManifestSHA256",
    "echoCLI_SHA256",
    "echoResourcesSHA256",
    "echoRenderVersion",
    "modelPolicyRevision",
    "modelExpectedByteCount",
    "modelBytesAttested",
)


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


def renderer_identity(
    renderer_schema_version: int,
    renderer_root: Path,
    renderer_build_root: Path,
    installer_source_sha: str,
    echo_source_sha: str,
    renderer_manifest_sha256: str,
    echo_cli_sha256: str,
    echo_resources_sha256: str,
    echo_render_version: int,
    model_policy_revision: str,
    model_expected_byte_count: int,
    model_bytes_attested: str | bool,
) -> dict[str, object]:
    require(
        type(renderer_schema_version) is int and renderer_schema_version == 1,
        "renderer schema version must be 1",
    )
    for value, label in (
        (renderer_root, "renderer root"),
        (renderer_build_root, "renderer build root"),
    ):
        require(value.is_absolute(), f"{label} must be absolute")
        require(not value.is_symlink() and value.is_dir(), f"{label} is unsafe")
        require(value.resolve() == value, f"{label} must be canonical")
    for value, label in (
        (installer_source_sha, "installer source SHA"),
        (echo_source_sha, "Echo source SHA"),
    ):
        require(
            isinstance(value, str)
            and re.fullmatch(r"[0-9a-f]{40}", value) is not None,
            f"{label} must be 40 lowercase hexadecimal characters",
        )
    for value, label in (
        (renderer_manifest_sha256, "renderer manifest SHA-256"),
        (echo_cli_sha256, "Echo CLI SHA-256"),
        (echo_resources_sha256, "Echo resources SHA-256"),
    ):
        require(
            isinstance(value, str) and SHA256_PATTERN.fullmatch(value) is not None,
            f"{label} must be 64 lowercase hexadecimal characters",
        )
    require(
        type(echo_render_version) is int and echo_render_version >= 12,
        "Echo render version must be an integer of at least 12",
    )
    require(
        isinstance(model_policy_revision, str)
        and bool(model_policy_revision)
        and "\n" not in model_policy_revision
        and "\r" not in model_policy_revision,
        "model policy revision must be nonempty and single-line",
    )
    require(
        type(model_expected_byte_count) is int and model_expected_byte_count > 0,
        "model expected byte count must be a positive integer",
    )
    if isinstance(model_bytes_attested, str):
        require(
            model_bytes_attested == "false",
            "model bytes attested must be boolean false",
        )
        attested = False
    else:
        require(
            model_bytes_attested is False,
            "model bytes attested must be boolean false",
        )
        attested = False
    return {
        "rendererSchemaVersion": 1,
        "rendererRoot": str(renderer_root),
        "rendererBuildRoot": str(renderer_build_root),
        "installerSourceSHA": installer_source_sha,
        "echoSourceSHA": echo_source_sha,
        "rendererManifestSHA256": renderer_manifest_sha256,
        "echoCLI_SHA256": echo_cli_sha256,
        "echoResourcesSHA256": echo_resources_sha256,
        "echoRenderVersion": echo_render_version,
        "modelPolicyRevision": model_policy_revision,
        "modelExpectedByteCount": model_expected_byte_count,
        "modelBytesAttested": attested,
    }


def renderer_identity_from_options(options: argparse.Namespace) -> dict[str, object]:
    return renderer_identity(
        options.renderer_schema_version,
        options.renderer_root,
        options.renderer_build_root,
        options.installer_source_sha,
        options.echo_source_sha,
        options.renderer_manifest_sha256,
        options.echo_cli_sha256,
        options.echo_resources_sha256,
        options.echo_render_version,
        options.model_policy_revision,
        options.model_expected_byte_count,
        options.model_bytes_attested,
    )


def renderer_identity_from_payload(
    payload: dict[str, object], label: str
) -> dict[str, object]:
    for key in ("rendererRoot", "rendererBuildRoot"):
        require(isinstance(payload.get(key), str), f"{label} has invalid {key}")
    return renderer_identity(
        payload.get("rendererSchemaVersion"),
        Path(payload["rendererRoot"]),
        Path(payload["rendererBuildRoot"]),
        payload.get("installerSourceSHA"),
        payload.get("echoSourceSHA"),
        payload.get("rendererManifestSHA256"),
        payload.get("echoCLI_SHA256"),
        payload.get("echoResourcesSHA256"),
        payload.get("echoRenderVersion"),
        payload.get("modelPolicyRevision"),
        payload.get("modelExpectedByteCount"),
        payload.get("modelBytesAttested"),
    )


def optional_renderer_identity_from_options(
    options: argparse.Namespace,
) -> dict[str, object] | None:
    names = (
        "renderer_schema_version",
        "renderer_root",
        "renderer_build_root",
        "installer_source_sha",
        "echo_source_sha",
        "renderer_manifest_sha256",
        "echo_cli_sha256",
        "echo_resources_sha256",
        "echo_render_version",
        "model_policy_revision",
        "model_expected_byte_count",
        "model_bytes_attested",
    )
    values = [getattr(options, name) for name in names]
    if all(value is None for value in values):
        return None
    require(
        all(value is not None for value in values),
        "renderer identity options must be supplied as one complete set",
    )
    return renderer_identity_from_options(options)


def require_receipt_renderer_identity(
    payload: dict[str, object],
    expected: dict[str, object],
    label: str,
) -> None:
    actual = {key: payload.get(key) for key in RENDERER_IDENTITY_KEYS}
    require(actual == expected, f"{label} renderer identity differs")


def read_installed_renderer_identity(path: Path) -> tuple[str, str]:
    """Read the exact installed-renderer identity from a schema-v2 resume receipt."""

    def reject_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
        payload: dict[str, object] = {}
        for key, value in pairs:
            require(key not in payload, f"resume-state receipt duplicates key: {key}")
            payload[key] = value
        return payload

    try:
        payload = json.loads(
            read_regular_bytes(path, "resume-state receipt").decode("utf-8"),
            object_pairs_hook=reject_duplicates,
        )
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise StateError("resume-state receipt is not valid UTF-8 JSON") from error
    require(isinstance(payload, dict), "resume-state receipt must be an object")
    expected_keys = {
        "schemaVersion",
        "echoSourceSHA",
        "rendererManifestSHA256",
        "sourceFingerprint",
        "voice",
        "renderVersion",
        "captureSetID",
        "inputReceiptSHA256",
        "databaseSHA256",
        "databaseByteCount",
        "captures",
    } | set(RENDERER_IDENTITY_KEYS)
    require(
        set(payload) == expected_keys,
        "resume-state receipt is not the exact installed-renderer schema",
    )
    require(
        type(payload["schemaVersion"]) is int and payload["schemaVersion"] == 2,
        "resume-state receipt is not installed-renderer schema 2",
    )
    identity = renderer_identity_from_payload(payload, "resume-state receipt")
    require_receipt_renderer_identity(payload, identity, "resume-state receipt")
    source_sha = payload["echoSourceSHA"]
    manifest_sha = payload["rendererManifestSHA256"]
    require(
        isinstance(source_sha, str)
        and re.fullmatch(r"[0-9a-f]{40}", source_sha) is not None,
        "resume-state receipt has an invalid echoSourceSHA",
    )
    require(
        isinstance(manifest_sha, str)
        and SHA256_PATTERN.fullmatch(manifest_sha) is not None,
        "resume-state receipt has an invalid rendererManifestSHA256",
    )
    return source_sha, manifest_sha


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
    render_version: int,
    input_receipt: Path,
    installed_renderer: dict[str, object],
) -> dict[str, object]:
    require(
        SHA256_PATTERN.fullmatch(source_sha) is not None
        or re.fullmatch(r"[0-9a-f]{40}", source_sha) is not None,
        "source SHA is invalid",
    )
    require(voice in {"am_michael", "am_puck"}, "resume voice is invalid")
    require(
        type(render_version) is int and render_version >= 12,
        "resume render version must be an integer of at least 12",
    )
    require(
        installed_renderer["echoSourceSHA"] == source_sha,
        "resume source SHA differs from installed renderer",
    )
    require(
        installed_renderer["echoRenderVersion"] == render_version,
        "resume render version differs from installed renderer",
    )
    require(
        not work.is_symlink() and work.is_dir(),
        f"resume work directory is unsafe: {work}",
    )
    regular_file(database, "resume database")
    regular_file(input_receipt, "render-input receipt")
    try:
        receipt_lines = read_regular_bytes(
            input_receipt, "render-input receipt"
        ).decode("utf-8").splitlines()
    except UnicodeDecodeError as error:
        raise StateError("render-input receipt is not UTF-8") from error
    render_version_lines = [
        line for line in receipt_lines if line.startswith("render_version=")
    ]
    require(
        render_version_lines == [f"render_version={render_version}"],
        "resume render version differs from render-input receipt",
    )
    expected_receipt_identity = {
        "renderer_schema_version": installed_renderer["rendererSchemaVersion"],
        "renderer_root": installed_renderer["rendererRoot"],
        "renderer_build_root": installed_renderer["rendererBuildRoot"],
        "installer_source_sha": installed_renderer["installerSourceSHA"],
        "echo_source_sha": installed_renderer["echoSourceSHA"],
        "renderer_manifest_sha256": installed_renderer[
            "rendererManifestSHA256"
        ],
        "echo_cli_sha256": installed_renderer["echoCLI_SHA256"],
        "echo_resources_sha256": installed_renderer["echoResourcesSHA256"],
        "render_version": installed_renderer["echoRenderVersion"],
        "model_policy_revision": installed_renderer["modelPolicyRevision"],
        "model_expected_byte_count": installed_renderer[
            "modelExpectedByteCount"
        ],
        "model_bytes_attested": "false",
        "voice": voice,
    }
    for key, value in expected_receipt_identity.items():
        require(
            [line for line in receipt_lines if line.startswith(f"{key}=")]
            == [f"{key}={value}"],
            f"render-input receipt renderer identity differs: {key}",
        )
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
            and identity["renderVersion"] == render_version,
            f"resume state requires Echo render version {render_version}: {marker.name}",
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
            "audioSHA256",
            "payloadSHA256",
        ):
            require(
                isinstance(identity.get(field), str)
                and SHA256_PATTERN.fullmatch(identity[field]) is not None,
                f"resume state identity has invalid {field}: {marker.name}",
            )
        require(
            isinstance(identity.get("chapterContentSignature"), str)
            and CHAPTER_CONTENT_SIGNATURE_PATTERN.fullmatch(
                identity["chapterContentSignature"]
            )
            is not None,
            f"resume state identity has invalid chapterContentSignature: {marker.name}",
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
        "schemaVersion": 2,
        **installed_renderer,
        "sourceFingerprint": expected_source,
        "voice": voice,
        "renderVersion": render_version,
        "captureSetID": capture_set_id,
        "inputReceiptSHA256": sha256(input_receipt),
        "databaseSHA256": sha256(database),
        "databaseByteCount": database.stat().st_size,
        "captures": captures,
    }


def success_snapshot(
    attempt_id: str,
    run_id: str,
    attempt_receipt: Path,
    input_receipt: Path,
    epub: Path,
    artifact_relative_path: str,
    state_receipt: Path,
    work: Path,
    database: Path,
    source_sha: str,
    voice: str,
    render_version: int,
    audiobook: Path,
    sidecar: Path,
    audit: Path,
    reel: Path,
    installed_renderer: dict[str, object],
) -> dict[str, object]:
    for path, label in (
        (input_receipt, "render-input receipt"),
        (attempt_receipt, "current-attempt receipt"),
        (epub, "source EPUB"),
        (state_receipt, "resume-state receipt"),
        (audiobook, "audiobook"),
        (sidecar, "alignment sidecar"),
        (audit, "pronunciation audit"),
    ):
        regular_file(path, label)
    validate_attempt(
        attempt_receipt,
        attempt_id,
        run_id,
        input_receipt,
        epub,
        artifact_relative_path,
        installed_renderer,
    )
    require(
        state_receipt.name == f"echo-resume-state-{run_id}.json",
        "resume-state receipt filename is not derived from the run ID",
    )
    expected_state = canonical_json(
        capture_snapshot(
            work,
            database,
            epub,
            source_sha,
            voice,
            render_version,
            input_receipt,
            installed_renderer,
        )
    )
    require(
        read_regular_bytes(state_receipt, "resume-state receipt") == expected_state,
        "resume state receipt does not match final WORK, DB, or captures",
    )
    require(audiobook.stat().st_size > 0, "audiobook is empty")
    payload: dict[str, object] = {
        "schemaVersion": 3,
        **installed_renderer,
        "attemptID": attempt_id,
        "runID": run_id,
        "attemptReceiptSHA256": sha256(attempt_receipt),
        "inputReceiptFileName": input_receipt.name,
        "inputReceiptSHA256": sha256(input_receipt),
        "sourceEPUBFileName": epub.name,
        "sourceEPUBSHA256": sha256(epub),
        "artifactRelativePath": artifact_relative_path,
        "resumeStateFileName": state_receipt.name,
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


def json_object(path: Path, label: str) -> dict[str, object]:
    regular_file(path, label)
    try:
        payload = json.loads(read_regular_bytes(path, label).decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise StateError(f"{label} is not valid JSON") from error
    require(isinstance(payload, dict), f"{label} root must be an object")
    return payload


def required_string(payload: dict[str, object], field: str, label: str) -> str:
    value = payload.get(field)
    require(isinstance(value, str) and bool(value), f"{label} has invalid {field}")
    return value


def attempt_snapshot(
    attempt_id: str,
    run_id: str,
    input_receipt: Path,
    epub: Path,
    artifact_relative_path: str,
    installed_renderer: dict[str, object] | None = None,
    *,
    historical: bool = False,
) -> dict[str, object]:
    require(
        SHA256_PATTERN.fullmatch(attempt_id) is not None,
        "attempt ID must be exactly 64 lowercase hexadecimal characters",
    )
    pattern = LEGACY_RUN_ID_PATTERN if historical else RUN_ID_PATTERN
    require(pattern.fullmatch(run_id) is not None, "run ID is invalid")
    require(
        historical or installed_renderer is not None,
        "current attempt requires installed renderer identity",
    )
    regular_file(input_receipt, "render-input receipt")
    regular_file(epub, "source EPUB")
    if not historical:
        require(
            installed_renderer is not None,
            "current attempt requires installed renderer identity",
        )
        voice = run_id.rsplit("-", 1)[-1]
        expected_run_id = (
            f"{sha256(epub)[:12]}-{installed_renderer['echoCLI_SHA256'][:12]}-"
            f"{installed_renderer['echoResourcesSHA256'][:12]}-"
            f"{installed_renderer['rendererManifestSHA256'][:12]}-"
            f"{installed_renderer['echoSourceSHA']}-{voice}"
        )
        require(
            run_id == expected_run_id,
            "run ID does not match the EPUB and installed renderer identity",
        )
    expected_artifact_path = f"echo-renders/{run_id}/{attempt_id}"
    require(
        artifact_relative_path == expected_artifact_path,
        "attempt artifact path is not derived from the run and attempt IDs",
    )
    payload: dict[str, object] = {
        "schemaVersion": 1 if historical else 2,
        "attemptID": attempt_id,
        "runID": run_id,
        "inputReceiptFileName": input_receipt.name,
        "inputReceiptSHA256": sha256(input_receipt),
        "sourceEPUBFileName": epub.name,
        "sourceEPUBSHA256": sha256(epub),
        "artifactRelativePath": artifact_relative_path,
    }
    if installed_renderer is not None:
        payload.update(installed_renderer)
    return payload


def validate_attempt(
    attempt_receipt: Path,
    attempt_id: str,
    run_id: str,
    input_receipt: Path,
    epub: Path,
    artifact_relative_path: str,
    installed_renderer: dict[str, object],
) -> dict[str, object]:
    expected = attempt_snapshot(
        attempt_id,
        run_id,
        input_receipt,
        epub,
        artifact_relative_path,
        installed_renderer,
    )
    actual = json_object(attempt_receipt, "current-attempt receipt")
    require(
        canonical_json(actual) == canonical_json(expected),
        "current-attempt receipt does not match current inputs",
    )
    return expected


def accepted_selector_snapshot(
    attempt_receipt: Path,
    success_receipt: Path,
    installed_renderer: dict[str, object] | None = None,
    *,
    historical: bool = False,
) -> dict[str, object]:
    attempt = json_object(attempt_receipt, "current-attempt receipt")
    success = json_object(success_receipt, "render-success receipt")
    require(
        attempt.get("schemaVersion") == (1 if historical else 2),
        f"current-attempt receipt schema must be {1 if historical else 2}",
    )
    require(
        success.get("schemaVersion") == (2 if historical else 3),
        f"render-success schema must be {2 if historical else 3}",
    )
    if not historical:
        require(installed_renderer is not None, "acceptance requires renderer identity")
        require_receipt_renderer_identity(
            attempt, installed_renderer, "current-attempt receipt"
        )
        require_receipt_renderer_identity(
            success, installed_renderer, "render-success receipt"
        )
    attempt_id = required_string(attempt, "attemptID", "current-attempt receipt")
    run_id = required_string(attempt, "runID", "current-attempt receipt")
    artifact_relative_path = required_string(
        attempt, "artifactRelativePath", "current-attempt receipt"
    )
    input_receipt_name = required_string(
        attempt, "inputReceiptFileName", "current-attempt receipt"
    )
    input_receipt_sha = required_string(
        attempt, "inputReceiptSHA256", "current-attempt receipt"
    )
    source_epub_name = required_string(
        attempt, "sourceEPUBFileName", "current-attempt receipt"
    )
    source_epub_sha = required_string(
        attempt, "sourceEPUBSHA256", "current-attempt receipt"
    )
    require(
        SHA256_PATTERN.fullmatch(attempt_id) is not None
        and (LEGACY_RUN_ID_PATTERN if historical else RUN_ID_PATTERN).fullmatch(run_id)
        is not None,
        "current-attempt receipt has invalid run or attempt ID",
    )
    require(
        SHA256_PATTERN.fullmatch(input_receipt_sha) is not None
        and SHA256_PATTERN.fullmatch(source_epub_sha) is not None,
        "current-attempt receipt has invalid input hashes",
    )
    require(
        input_receipt_name == f"echo-render-inputs-{run_id}.env",
        "current-attempt receipt has an invalid input receipt filename",
    )
    require(
        artifact_relative_path == f"echo-renders/{run_id}/{attempt_id}",
        "current-attempt receipt has an invalid artifact path",
    )
    require(
        success_receipt.name == f"echo-render-success-{run_id}-{attempt_id}.json",
        "render-success receipt filename is not derived from the current attempt",
    )
    for field in ("attemptID", "runID", "inputReceiptSHA256", "sourceEPUBSHA256"):
        require(
            success.get(field) == attempt.get(field),
            f"render-success receipt {field} differs from current attempt",
        )
    require(
        success.get("attemptReceiptSHA256") == sha256(attempt_receipt),
        "render-success receipt is not bound to the current attempt",
    )
    require(
        success.get("artifactRelativePath") == attempt.get("artifactRelativePath"),
        "render-success artifact path differs from current attempt",
    )
    for field in ("inputReceiptFileName", "sourceEPUBFileName"):
        require(
            success.get(field) == attempt.get(field),
            f"render-success receipt {field} differs from current attempt",
        )
    payload: dict[str, object] = {
        "schemaVersion": 1 if historical else 2,
        "attemptID": attempt_id,
        "runID": run_id,
        "attemptReceiptSHA256": sha256(attempt_receipt),
        "successReceiptFileName": success_receipt.name,
        "successReceiptSHA256": sha256(success_receipt),
        "inputReceiptFileName": input_receipt_name,
        "inputReceiptSHA256": input_receipt_sha,
        "sourceEPUBFileName": source_epub_name,
        "sourceEPUBSHA256": source_epub_sha,
        "artifactRelativePath": artifact_relative_path,
    }
    if installed_renderer is not None:
        payload.update(installed_renderer)
    return payload


def verify_delivery_receipt(
    attempt_receipt: Path,
    selector: Path,
    receipt: Path,
    input_receipt: Path,
    state_receipt: Path,
    epub: Path,
    audiobook: Path,
    sidecar: Path,
    audit: Path,
    reel: Path,
    installed_renderer: dict[str, object] | None,
    voice: str | None,
) -> None:
    attempt = json_object(attempt_receipt, "current-attempt receipt")
    accepted = json_object(selector, "current-accepted selector")
    payload = json_object(receipt, "render-success receipt")
    schemas = (
        attempt.get("schemaVersion"),
        accepted.get("schemaVersion"),
        payload.get("schemaVersion"),
    )
    historical = schemas == (1, 1, 2)
    require(
        historical or schemas == (2, 2, 3),
        "receipt chain does not use a supported historical or current schema",
    )
    require(
        historical or installed_renderer is not None,
        "current delivery verification requires installed renderer identity",
    )
    require(
        historical or voice in {"am_michael", "am_puck"},
        "current delivery verification requires an approved voice",
    )
    if installed_renderer is not None:
        for current_payload, label in (
            (attempt, "current-attempt receipt"),
            (accepted, "current-accepted selector"),
            (payload, "render-success receipt"),
        ):
            require_receipt_renderer_identity(
                current_payload, installed_renderer, label
            )
    attempt_id = required_string(attempt, "attemptID", "current-attempt receipt")
    run_id = required_string(attempt, "runID", "current-attempt receipt")
    if not historical:
        require(
            installed_renderer is not None,
            "current delivery verification requires installed renderer identity",
        )
        expected_run_id = (
            f"{sha256(epub)[:12]}-{installed_renderer['echoCLI_SHA256'][:12]}-"
            f"{installed_renderer['echoResourcesSHA256'][:12]}-"
            f"{installed_renderer['rendererManifestSHA256'][:12]}-"
            f"{installed_renderer['echoSourceSHA']}-{voice}"
        )
        require(
            run_id == expected_run_id,
            "current delivery run ID differs from renderer, source, or voice",
        )
    artifact_relative_path = required_string(
        attempt, "artifactRelativePath", "current-attempt receipt"
    )
    expected_attempt = attempt_snapshot(
        attempt_id,
        run_id,
        input_receipt,
        epub,
        artifact_relative_path,
        installed_renderer,
        historical=historical,
    )
    require(
        canonical_json(attempt) == canonical_json(expected_attempt),
        "current attempt receipt does not match the supplied source and input receipt",
    )
    require(
        accepted.get("attemptID") == attempt.get("attemptID")
        and accepted.get("attemptReceiptSHA256") == sha256(attempt_receipt),
        "current-accepted selector does not match the current attempt",
    )
    expected_selector = accepted_selector_snapshot(
        attempt_receipt,
        receipt,
        installed_renderer,
        historical=historical,
    )
    require(
        canonical_json(accepted) == canonical_json(expected_selector),
        "current-accepted selector does not match current attempt and success receipt",
    )
    for path, name_field, hash_field, label in (
        (
            input_receipt,
            "inputReceiptFileName",
            "inputReceiptSHA256",
            "render-input receipt",
        ),
        (epub, "sourceEPUBFileName", "sourceEPUBSHA256", "source EPUB"),
    ):
        regular_file(path, label)
        require(
            attempt.get(name_field) == path.name,
            f"{label} filename differs from current-attempt receipt",
        )
        require(
            attempt.get(hash_field) == sha256(path),
            f"{label} SHA-256 differs from current-attempt receipt",
        )
        require(
            payload.get(hash_field) == attempt.get(hash_field),
            f"{label} differs between current attempt and render success",
        )
    resume_state_name = required_string(
        payload, "resumeStateFileName", "render-success receipt"
    )
    resume_state_hash = required_string(
        payload, "resumeStateSHA256", "render-success receipt"
    )
    require(
        resume_state_name == f"echo-resume-state-{run_id}.json",
        "render-success receipt has an invalid resume-state filename",
    )
    require(
        SHA256_PATTERN.fullmatch(resume_state_hash) is not None,
        "render-success receipt has invalid resume-state SHA-256",
    )
    regular_file(state_receipt, "resume-state receipt")
    require(
        state_receipt.name == resume_state_name,
        "resume-state receipt filename differs from render-success receipt",
    )
    require(
        sha256(state_receipt) == resume_state_hash,
        "resume-state receipt SHA-256 differs from render-success receipt",
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


def add_renderer_arguments(
    command: argparse.ArgumentParser, *, required: bool
) -> None:
    command.add_argument("--renderer-schema-version", type=int, required=required)
    command.add_argument("--renderer-root", type=Path, required=required)
    command.add_argument("--renderer-build-root", type=Path, required=required)
    command.add_argument("--installer-source-sha", required=required)
    command.add_argument("--echo-source-sha", required=required)
    command.add_argument("--renderer-manifest-sha256", required=required)
    command.add_argument("--echo-cli-sha256", required=required)
    command.add_argument("--echo-resources-sha256", required=required)
    command.add_argument("--echo-render-version", type=int, required=required)
    command.add_argument("--model-policy-revision", required=required)
    command.add_argument("--model-expected-byte-count", type=int, required=required)
    command.add_argument("--model-bytes-attested", required=required)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    commands = root.add_subparsers(dest="command", required=True)
    hash_parser = commands.add_parser("hash-tree")
    hash_parser.add_argument("path", type=Path)
    immutable = commands.add_parser("immutable-file")
    immutable.add_argument("path", type=Path)
    validate_run_id = commands.add_parser("validate-run-id")
    validate_run_id.add_argument("run_id")
    for name in ("record-state", "verify-state"):
        command = commands.add_parser(name)
        add_renderer_arguments(command, required=True)
        command.add_argument("--work", type=Path, required=True)
        command.add_argument("--db", type=Path, required=True)
        command.add_argument("--receipt", type=Path, required=True)
        command.add_argument("--epub", type=Path, required=True)
        command.add_argument("--source-sha", required=True)
        command.add_argument("--voice", required=True)
        command.add_argument("--render-version", type=int, required=True)
        command.add_argument("--input-receipt", type=Path, required=True)
        command.add_argument("--lock-root", type=Path)
    reset = commands.add_parser("reset-state")
    reset.add_argument("--work", type=Path, required=True)
    reset.add_argument("--db", type=Path, required=True)
    reset.add_argument("--receipt", type=Path, required=True)
    reset.add_argument("--lock-root", type=Path, required=True)
    for name in ("write-attempt", "verify-attempt"):
        command = commands.add_parser(name)
        add_renderer_arguments(command, required=True)
        command.add_argument("--attempt-id", required=True)
        command.add_argument("--run-id", required=True)
        command.add_argument("--receipt", type=Path, required=True)
        command.add_argument("--input-receipt", type=Path, required=True)
        command.add_argument("--epub", type=Path, required=True)
        command.add_argument("--artifact-relative-path", required=True)
        command.add_argument("--selection-resource", type=Path)
        command.add_argument("--lock-root", type=Path)
    for name in ("write-success", "verify-success"):
        command = commands.add_parser(name)
        add_renderer_arguments(command, required=True)
        command.add_argument("--attempt-id", required=True)
        command.add_argument("--run-id", required=True)
        command.add_argument("--receipt", type=Path, required=True)
        command.add_argument("--attempt-receipt", type=Path, required=True)
        command.add_argument("--input-receipt", type=Path, required=True)
        command.add_argument("--epub", type=Path, required=True)
        command.add_argument("--artifact-relative-path", required=True)
        command.add_argument("--state-receipt", type=Path, required=True)
        command.add_argument("--work", type=Path, required=True)
        command.add_argument("--db", type=Path, required=True)
        command.add_argument("--source-sha", required=True)
        command.add_argument("--voice", required=True)
        command.add_argument("--render-version", type=int, required=True)
        command.add_argument("--audiobook", type=Path, required=True)
        command.add_argument("--sidecar", type=Path, required=True)
        command.add_argument("--audit", type=Path, required=True)
        command.add_argument("--reel", type=Path, required=True)
        command.add_argument("--selection-resource", type=Path)
        command.add_argument("--lock-root", type=Path)
    accepted = commands.add_parser("accept-attempt")
    add_renderer_arguments(accepted, required=True)
    accepted.add_argument("--attempt", type=Path, required=True)
    accepted.add_argument("--success", type=Path, required=True)
    accepted.add_argument("--selector", type=Path, required=True)
    accepted.add_argument("--selection-resource", type=Path, required=True)
    accepted.add_argument("--lock-root", type=Path, required=True)
    delivery = commands.add_parser("verify-delivery")
    add_renderer_arguments(delivery, required=False)
    delivery.add_argument("--attempt", type=Path, required=True)
    delivery.add_argument("--selector", type=Path, required=True)
    delivery.add_argument("--receipt", type=Path, required=True)
    delivery.add_argument("--input-receipt", type=Path, required=True)
    delivery.add_argument("--state-receipt", type=Path, required=True)
    delivery.add_argument("--epub", type=Path, required=True)
    delivery.add_argument("--audiobook", type=Path, required=True)
    delivery.add_argument("--sidecar", type=Path, required=True)
    delivery.add_argument("--audit", type=Path, required=True)
    delivery.add_argument("--reel", type=Path, required=True)
    delivery.add_argument("--voice")
    return root


def main(arguments: list[str]) -> int:
    options = parser().parse_args(arguments)
    try:
        if options.command == "hash-tree":
            print(hash_tree(options.path.resolve()))
        elif options.command == "immutable-file":
            safe_atomic_write(options.path, sys.stdin.buffer.read(), immutable=True)
        elif options.command == "validate-run-id":
            require(
                RUN_ID_PATTERN.fullmatch(options.run_id) is not None,
                "run ID is not a current governed narration run ID",
            )
        elif options.command in {"record-state", "verify-state"}:
            installed_renderer = renderer_identity_from_options(options)
            payload = capture_snapshot(
                options.work,
                options.db,
                options.epub,
                options.source_sha,
                options.voice,
                options.render_version,
                options.input_receipt,
                installed_renderer,
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
        elif options.command in {"write-attempt", "verify-attempt"}:
            installed_renderer = renderer_identity_from_options(options)
            payload = attempt_snapshot(
                options.attempt_id,
                options.run_id,
                options.input_receipt,
                options.epub,
                options.artifact_relative_path,
                installed_renderer,
            )
            content = canonical_json(payload)
            if options.command == "write-attempt":
                require(
                    options.lock_root is not None
                    and options.selection_resource is not None,
                    "write-attempt requires the selection lease",
                )
                require_mutation_leases(
                    options.lock_root, (options.selection_resource,)
                )
                safe_atomic_write(options.receipt, content, immutable=False)
            else:
                regular_file(options.receipt, "current-attempt receipt")
                require(
                    read_regular_bytes(options.receipt, "current-attempt receipt")
                    == content,
                    "current-attempt receipt does not match current inputs",
                )
        elif options.command in {"write-success", "verify-success"}:
            installed_renderer = renderer_identity_from_options(options)
            if options.command == "write-success":
                require(
                    options.lock_root is not None
                    and options.selection_resource is not None,
                    "write-success requires WORK, DB, output, and selection leases",
                )
                require_mutation_leases(
                    options.lock_root,
                    (
                        options.work,
                        options.db,
                        options.audiobook,
                        options.sidecar,
                        options.audit,
                        options.reel,
                        options.selection_resource,
                    ),
                )
            payload = success_snapshot(
                options.attempt_id,
                options.run_id,
                options.attempt_receipt,
                options.input_receipt,
                options.epub,
                options.artifact_relative_path,
                options.state_receipt,
                options.work,
                options.db,
                options.source_sha,
                options.voice,
                options.render_version,
                options.audiobook,
                options.sidecar,
                options.audit,
                options.reel,
                installed_renderer,
            )
            content = canonical_json(payload)
            if options.command == "write-success":
                safe_atomic_write(options.receipt, content, immutable=False)
            else:
                regular_file(options.receipt, "render-success receipt")
                require(
                    read_regular_bytes(options.receipt, "render-success receipt")
                    == content,
                    "render-success receipt does not match delivered media",
                )
        elif options.command == "accept-attempt":
            installed_renderer = renderer_identity_from_options(options)
            require_mutation_leases(options.lock_root, (options.selection_resource,))
            content = canonical_json(
                accepted_selector_snapshot(
                    options.attempt, options.success, installed_renderer
                )
            )
            safe_atomic_write(options.selector, content, immutable=False)
        elif options.command == "verify-delivery":
            installed_renderer = optional_renderer_identity_from_options(options)
            verify_delivery_receipt(
                options.attempt,
                options.selector,
                options.receipt,
                options.input_receipt,
                options.state_receipt,
                options.epub,
                options.audiobook,
                options.sidecar,
                options.audit,
                options.reel,
                installed_renderer,
                options.voice,
            )
        return 0
    except (OSError, StateError, json.JSONDecodeError) as error:
        print(f"echo_pronunciation_state: {error}", file=sys.stderr)
        return 65


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
