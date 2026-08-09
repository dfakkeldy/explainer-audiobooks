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
from echo_voice_plan import (
    VOICE_IDS,
    VoicePlanError,
    effective_voice,
    read_authored_plan,
    validate_resolver_receipt,
    voice_plan,
)


SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
CHAPTER_CONTENT_SIGNATURE_PATTERN = re.compile(r"[0-9a-f]{16}")
MARKER_PATTERN = re.compile(r"\.anchors-ch([0-9]+)\.json")
# epub-cli-resources-manifest-source-voice-plan.
VOICE_ID_PATTERN = "|".join(re.escape(voice) for voice in sorted(VOICE_IDS))
RUN_ID_PATTERN = re.compile(
    r"[0-9a-f]{12}-[0-9a-f]{12}-[0-9a-f]{12}-"
    r"[0-9a-f]{12}-[0-9a-f]{40}"
    rf"-(?:{VOICE_ID_PATTERN}|plan-[0-9a-f]{{12}}|plan-[0-9a-f]{{64}})"
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
BLOCK_PLAN_RECEIPT_KEYS = frozenset(
    {
        "voicePlanMode",
        "voicePlanID",
        "voicePlanSHA256",
        "voicePlanBlockCount",
        "voicePlanCanonicalFileName",
        "voicePlanCanonicalSHA256",
        "voicePlanResolutionFileName",
        "voicePlanResolutionSHA256",
    }
)
BLOCK_REEL_RECEIPT_KEYS = frozenset(
    {"reelFileName", "reelRelativePath", "reelSHA256"}
)
STATE_RECEIPT_COMMON_KEYS = frozenset(
    {
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
    }
) | frozenset(RENDERER_IDENTITY_KEYS)
SUCCESS_RECEIPT_COMMON_KEYS = frozenset(
    {
        "schemaVersion",
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
) | frozenset(RENDERER_IDENTITY_KEYS)


class StateError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise StateError(message)


def require_block_plan_receipt_evidence(
    payload: dict[str, object], label: str
) -> None:
    """Validate stored plan facts without attempting Echo's chapter digest."""

    require(
        payload.get("voicePlanMode") == "block",
        f"{label} is not a block voice-plan receipt",
    )
    plan_id = payload.get("voicePlanID")
    plan_sha = payload.get("voicePlanSHA256")
    block_count = payload.get("voicePlanBlockCount")
    require(
        isinstance(plan_id, str)
        and re.fullmatch(r"plan-[0-9a-f]{12}", plan_id) is not None,
        f"{label} has an invalid voicePlanID",
    )
    require(
        isinstance(plan_sha, str) and SHA256_PATTERN.fullmatch(plan_sha) is not None,
        f"{label} has an invalid voicePlanSHA256",
    )
    require(
        plan_id == f"plan-{plan_sha[:12]}",
        f"{label} voicePlanID does not bind voicePlanSHA256",
    )
    require(
        type(block_count) is int and block_count > 0,
        f"{label} has an invalid voicePlanBlockCount",
    )
    canonical_name = payload.get("voicePlanCanonicalFileName")
    resolution_name = payload.get("voicePlanResolutionFileName")
    require(
        canonical_name == f"echo-voice-plan-plan-{plan_sha}.json",
        f"{label} has an invalid voicePlanCanonicalFileName",
    )
    require(
        resolution_name == f"echo-voice-plan-resolution-plan-{plan_sha}.json",
        f"{label} has an invalid voicePlanResolutionFileName",
    )
    for field in ("voicePlanCanonicalSHA256", "voicePlanResolutionSHA256"):
        require(
            isinstance(payload.get(field), str)
            and SHA256_PATTERN.fullmatch(payload[field]) is not None,
            f"{label} has an invalid {field}",
        )


def require_block_state_receipt(payload: dict[str, object], label: str) -> None:
    require(
        set(payload) == STATE_RECEIPT_COMMON_KEYS | BLOCK_PLAN_RECEIPT_KEYS,
        f"{label} is not the exact block resume schema 4",
    )
    require(
        payload.get("schemaVersion") == 4,
        f"{label} schemaVersion must be 4 for a block receipt",
    )
    require_block_plan_receipt_evidence(payload, label)


def require_block_success_receipt(payload: dict[str, object], label: str) -> None:
    reel_keys = set(payload) & BLOCK_REEL_RECEIPT_KEYS
    require(
        reel_keys in (set(), set(BLOCK_REEL_RECEIPT_KEYS)),
        f"{label} block reel fields must be all present or all absent",
    )
    expected_keys = SUCCESS_RECEIPT_COMMON_KEYS | BLOCK_PLAN_RECEIPT_KEYS | reel_keys
    require(
        set(payload) == expected_keys,
        f"{label} is not the exact block success schema 4",
    )
    require(
        payload.get("schemaVersion") == 4,
        f"{label} schemaVersion must be 4 for a block receipt",
    )
    require_block_plan_receipt_evidence(payload, label)
    if reel_keys:
        reel_name = payload.get("reelFileName")
        run_id = payload.get("runID")
        attempt_id = payload.get("attemptID")
        require(
            isinstance(reel_name, str)
            and bool(reel_name)
            and Path(reel_name).name == reel_name,
            f"{label} has an invalid reelFileName",
        )
        require(
            isinstance(run_id, str) and isinstance(attempt_id, str),
            f"{label} lacks the run identity for its listening reel",
        )
        require(
            payload.get("reelRelativePath")
            == f"listening/{run_id}/{attempt_id}/{reel_name}",
            f"{label} has an invalid reelRelativePath",
        )
        require(
            isinstance(payload.get("reelSHA256"), str)
            and SHA256_PATTERN.fullmatch(payload["reelSHA256"]) is not None,
            f"{label} has an invalid reelSHA256",
        )


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


class RegularFileSnapshot:
    """One descriptor's exact bytes and the facts derived from those bytes."""

    def __init__(
        self, content: bytes | None, sha256: str, byte_count: int
    ) -> None:
        self.content = content
        self.sha256 = sha256
        self.byte_count = byte_count


def snapshot_regular_file(
    path: Path, label: str, *, retain_content: bool = False
) -> RegularFileSnapshot:
    """Read/hash/count one no-follow descriptor without reopening its pathname."""

    descriptor = open_regular(path, label)
    digest = hashlib.sha256()
    byte_count = 0
    chunks: list[bytes] | None = [] if retain_content else None
    with os.fdopen(descriptor, "rb", closefd=True) as input_file:
        while chunk := input_file.read(1_048_576):
            digest.update(chunk)
            byte_count += len(chunk)
            if chunks is not None:
                chunks.append(chunk)
    return RegularFileSnapshot(
        b"".join(chunks) if chunks is not None else None,
        digest.hexdigest(),
        byte_count,
    )


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
    """Read the installed-renderer identity from a sealed resume receipt."""

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
    schema_version = payload.get("schemaVersion")
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
    if schema_version == 3:
        expected_keys |= {"chapterVoices", "voicePlanSHA256"}
    elif schema_version == 4:
        expected_keys |= {
            "voicePlanMode",
            "voicePlanID",
            "voicePlanSHA256",
            "voicePlanBlockCount",
            "voicePlanCanonicalFileName",
            "voicePlanCanonicalSHA256",
            "voicePlanResolutionFileName",
            "voicePlanResolutionSHA256",
        }
    require(
        set(payload) == expected_keys,
        "resume-state receipt is not the exact installed-renderer schema",
    )
    require(
        type(schema_version) is int and schema_version in {2, 3, 4},
        "resume-state receipt is not installed-renderer schema 2, 3, or 4",
    )
    if schema_version == 4:
        require_block_state_receipt(payload, "resume-state receipt")
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
    return snapshot_regular_file(path, "hashed file").sha256


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
        # Full Echo plan digests intentionally appear in block run paths.  Do
        # not repeat an already near-limit receipt basename in a private temp
        # name, or the atomic writer itself exceeds NAME_MAX.
        prefix=".echo-receipt-", suffix=".tmp", dir=path.parent
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


def receipt_lines(input_receipt: Path) -> list[str]:
    regular_file(input_receipt, "render-input receipt")
    try:
        return read_regular_bytes(input_receipt, "render-input receipt").decode(
            "utf-8"
        ).splitlines()
    except UnicodeDecodeError as error:
        raise StateError("render-input receipt is not UTF-8") from error


def require_receipt_value(
    lines: list[str], key: str, value: object, label: str
) -> None:
    require(
        [line for line in lines if line.startswith(f"{key}=")]
        == [f"{key}={value}"],
        f"{label} differs from render-input receipt: {key}",
    )


def block_plan_evidence(
    voice_plan_path: Path,
    voice_plan_id: str,
    voice_plan_sha256: str,
    voice_plan_block_count: int,
    voice_plan_resolution: Path,
    epub: Path,
    input_receipt: Path,
    voice: str,
) -> dict[str, object]:
    """Validate Echo-sealed plan evidence without deriving Echo block digests."""

    require(
        isinstance(voice_plan_id, str)
        and re.fullmatch(r"plan-[0-9a-f]{12}", voice_plan_id) is not None,
        "block voice-plan ID is invalid",
    )
    require(
        isinstance(voice_plan_sha256, str)
        and SHA256_PATTERN.fullmatch(voice_plan_sha256) is not None,
        "block voice-plan SHA-256 is invalid",
    )
    require(
        voice_plan_id == f"plan-{voice_plan_sha256[:12]}",
        "block voice-plan ID does not bind its SHA-256",
    )
    require(
        type(voice_plan_block_count) is int and voice_plan_block_count > 0,
        "block voice-plan block count must be positive",
    )
    for path, label in (
        (voice_plan_path, "canonical block voice plan"),
        (voice_plan_resolution, "block voice-plan resolution"),
    ):
        require(path.is_absolute(), f"{label} must be absolute")
        require(path.resolve(strict=False) == path, f"{label} must be canonical")
        regular_file(path, label)
    require(
        voice_plan_path.name == f"echo-voice-plan-plan-{voice_plan_sha256}.json",
        "canonical block voice-plan filename is invalid",
    )
    require(
        voice_plan_resolution.name
        == f"echo-voice-plan-resolution-plan-{voice_plan_sha256}.json",
        "block voice-plan resolution filename is invalid",
    )
    canonical_bytes = read_regular_bytes(voice_plan_path, "canonical block voice plan")
    resolution_bytes = read_regular_bytes(
        voice_plan_resolution, "block voice-plan resolution"
    )
    try:
        require(
            read_authored_plan(voice_plan_path) == canonical_bytes,
            "canonical block voice plan is not canonical JSON",
        )
        resolved = validate_resolver_receipt(resolution_bytes, epub)
    except VoicePlanError as error:
        raise StateError(f"sealed block voice-plan evidence is invalid: {error}") from error
    require(
        resolved["voicePlanID"] == voice_plan_id,
        "block voice-plan ID differs from sealed resolution",
    )
    require(
        resolved["voicePlanSHA256"] == voice_plan_sha256,
        "block voice-plan SHA-256 differs from sealed resolution",
    )
    require(
        resolved["blockCount"] == voice_plan_block_count,
        "block voice-plan count differs from sealed resolution",
    )
    require(
        resolved["defaultVoice"] == voice,
        "block voice-plan default voice differs from the selected voice",
    )
    lines = receipt_lines(input_receipt)
    values = {
        "voice_plan_mode": "block",
        "voice_plan_sha256": voice_plan_sha256,
        "voice_plan_id": voice_plan_id,
        "voice_plan_block_count": voice_plan_block_count,
        "voice_plan_canonical_path": voice_plan_path,
        "voice_plan_canonical_sha256": hashlib.sha256(canonical_bytes).hexdigest(),
        "voice_plan_resolution_path": voice_plan_resolution,
        "voice_plan_resolution_sha256": hashlib.sha256(resolution_bytes).hexdigest(),
    }
    for key, value in values.items():
        require_receipt_value(lines, key, value, "block voice-plan evidence")
    require_receipt_value(lines, "chapter_voices", "", "block voice-plan evidence")
    return {
        "voicePlanMode": "block",
        "voicePlanID": voice_plan_id,
        "voicePlanSHA256": voice_plan_sha256,
        "voicePlanBlockCount": voice_plan_block_count,
        "voicePlanCanonicalFileName": voice_plan_path.name,
        "voicePlanCanonicalSHA256": values["voice_plan_canonical_sha256"],
        "voicePlanResolutionFileName": voice_plan_resolution.name,
        "voicePlanResolutionSHA256": values["voice_plan_resolution_sha256"],
    }


def block_plan_evidence_from_options(
    options: argparse.Namespace,
) -> dict[str, object] | None:
    structural_names = (
        "voice_plan",
        "voice_plan_id",
        "voice_plan_block_count",
        "voice_plan_resolution",
    )
    structural_values = [getattr(options, name) for name in structural_names]
    if all(value is None for value in structural_values):
        return None
    require(
        all(value is not None for value in structural_values)
        and options.voice_plan_sha256 is not None,
        "block voice-plan options must be supplied as one complete set",
    )
    require(
        not options.chapter_voice,
        "block voice-plan options cannot be combined with chapter voices",
    )
    return block_plan_evidence(
        options.voice_plan,
        options.voice_plan_id,
        options.voice_plan_sha256,
        options.voice_plan_block_count,
        options.voice_plan_resolution,
        options.epub,
        options.input_receipt,
        options.voice,
    )


def capture_snapshot(
    work: Path,
    database: Path,
    epub: Path,
    source_sha: str,
    voice: str,
    chapter_voice_values: list[str],
    voice_plan_sha256: str | None,
    render_version: int,
    input_receipt: Path,
    installed_renderer: dict[str, object],
    block_plan: dict[str, object] | None = None,
) -> dict[str, object]:
    require(
        SHA256_PATTERN.fullmatch(source_sha) is not None
        or re.fullmatch(r"[0-9a-f]{40}", source_sha) is not None,
        "source SHA is invalid",
    )
    plan: dict[str, object] | None = None
    if block_plan is None:
        plan = voice_plan(voice, chapter_voice_values)
        voice_plan_sha256 = voice_plan_sha256 or plan["voicePlanSHA256"]
        require(
            plan["voicePlanSHA256"] == voice_plan_sha256,
            "resume voice-plan SHA-256 is invalid",
        )
    else:
        require(
            voice_plan_sha256 == block_plan["voicePlanSHA256"],
            "resume block voice-plan SHA-256 is invalid",
        )
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
    database_snapshot = snapshot_regular_file(database, "resume database")
    input_receipt_snapshot = snapshot_regular_file(
        input_receipt, "render-input receipt", retain_content=True
    )
    require(
        input_receipt_snapshot.content is not None,
        "render-input receipt could not be read",
    )
    try:
        lines = input_receipt_snapshot.content.decode("utf-8").splitlines()
    except UnicodeDecodeError as error:
        raise StateError("render-input receipt is not UTF-8") from error
    require_receipt_value(lines, "render_version", render_version, "resume render version")
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
        "chapter_voices": ""
        if block_plan is not None
        else ",".join(plan["canonicalAssignments"]),
        "voice_plan_sha256": voice_plan_sha256,
        "voice_plan_id": (
            block_plan["voicePlanID"] if block_plan is not None else plan["voicePlanID"]
        ),
    }
    for key, value in expected_receipt_identity.items():
        require_receipt_value(lines, key, value, "render-input receipt renderer identity")
    expected_source = epub_fingerprint(epub)
    captures: list[dict[str, object]] = []
    capture_set_id: str | None = None
    indexes: set[int] = set()
    marker_paths = sorted(
        work.glob(".anchors-ch*.json"),
        key=lambda path: int(MARKER_PATTERN.fullmatch(path.name).group(1))
        if MARKER_PATTERN.fullmatch(path.name)
        else -1,
    )
    require(marker_paths, "resume state has no completed capture markers")
    for display_chapter, marker in enumerate(marker_paths, start=1):
        match = MARKER_PATTERN.fullmatch(marker.name)
        require(match is not None, f"malformed capture marker name: {marker.name}")
        filename_index = int(match.group(1))
        require(filename_index not in indexes, "duplicate capture chapter index")
        indexes.add(filename_index)
        marker_snapshot = snapshot_regular_file(
            marker, "capture marker", retain_content=True
        )
        require(
            marker_snapshot.content is not None,
            f"capture marker could not be read: {marker.name}",
        )
        try:
            payload = json.loads(marker_snapshot.content.decode("utf-8"))
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
        if block_plan is None:
            require(
                type(identity.get("schemaVersion")) is int
                and identity["schemaVersion"] == 1,
                f"resume state requires capture schema 1: {marker.name}",
            )
        else:
            require(
                type(identity.get("schemaVersion")) is int
                and identity["schemaVersion"] == 2,
                f"resume state requires capture schema 2: {marker.name}",
            )
            require(
                identity.get("voicePlanSHA256") == block_plan["voicePlanSHA256"],
                f"resume state voice-plan SHA-256 differs: {marker.name}",
            )
            require(
                isinstance(identity.get("chapterVoicePlanSHA256"), str)
                and SHA256_PATTERN.fullmatch(identity["chapterVoicePlanSHA256"])
                is not None,
                f"resume state has invalid chapterVoicePlanSHA256: {marker.name}",
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
        if block_plan is None:
            require(plan is not None, "legacy resume state lacks a chapter voice plan")
            expected_voice = effective_voice(
                voice, plan["chapterVoices"], display_chapter
            )
            require(
                identity.get("voice") == expected_voice,
                f"resume state voice differs: {marker.name}",
            )
        else:
            require(
                identity.get("voice") in VOICE_IDS,
                f"resume state has an unknown block voice: {marker.name}",
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
        audio_snapshot = snapshot_regular_file(audio, "capture audio")
        require(
            type(identity.get("audioFileByteCount")) is int
            and identity["audioFileByteCount"] >= 0
            and identity["audioFileByteCount"] == audio_snapshot.byte_count,
            f"resume capture audio size differs: {audio_name}",
        )
        audio_hash = audio_snapshot.sha256
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
                "markerSHA256": marker_snapshot.sha256,
                "audioFileName": audio_name,
                "audioSHA256": audio_hash,
                "payloadSHA256": identity["payloadSHA256"],
            }
        )
    if block_plan is not None:
        return {
            "schemaVersion": 4,
            **installed_renderer,
            "sourceFingerprint": expected_source,
            "voice": voice,
            **block_plan,
            "renderVersion": render_version,
            "captureSetID": capture_set_id,
            "inputReceiptSHA256": input_receipt_snapshot.sha256,
            "databaseSHA256": database_snapshot.sha256,
            "databaseByteCount": database_snapshot.byte_count,
            "captures": captures,
        }
    require(plan is not None, "legacy resume state lacks a chapter voice plan")
    return {
        "schemaVersion": 3,
        **installed_renderer,
        "sourceFingerprint": expected_source,
        "voice": voice,
        "chapterVoices": {
            str(chapter): chapter_voice
            for chapter, chapter_voice in plan["chapterVoices"].items()
        },
        "voicePlanSHA256": voice_plan_sha256,
        "renderVersion": render_version,
        "captureSetID": capture_set_id,
        "inputReceiptSHA256": input_receipt_snapshot.sha256,
        "databaseSHA256": database_snapshot.sha256,
        "databaseByteCount": database_snapshot.byte_count,
        "captures": captures,
    }


def block_attempt_root(
    attempt_receipt: Path, artifact_relative_path: str
) -> Path:
    require(
        attempt_receipt.is_absolute(),
        "block attempt receipt path must be absolute",
    )
    path_parts = artifact_relative_path.split("/")
    require(
        len(path_parts) == 3
        and path_parts[0] == "echo-renders"
        and all(path_parts[1:]),
        "block attempt artifact path is malformed",
    )
    return attempt_receipt.parent.parent / "dist" / artifact_relative_path


def require_block_attempt_contents(
    attempt_receipt: Path,
    artifact_relative_path: str,
    audiobook: Path,
    sidecar: Path,
    audit: Path,
) -> None:
    """Allow only final delivery media beneath a schema-4 attempt root."""

    artifact_root = block_attempt_root(attempt_receipt, artifact_relative_path)
    require(
        audiobook.parent == artifact_root
        and sidecar.parent == artifact_root
        and audit.parent == artifact_root,
        "block attempt media paths are not derived from the current attempt",
    )
    require(
        not artifact_root.is_symlink() and artifact_root.is_dir(),
        f"block attempt contains an unsafe artifact root: {artifact_root}",
    )
    expected = {audiobook.name, sidecar.name, audit.name}
    require(
        len(expected) == 3,
        "block attempt delivery media filenames must be distinct",
    )
    for path, expected_suffix in (
        (audiobook, ".m4b"),
        (sidecar, ".alignment.json"),
        (audit, ".pronunciation-audit.json"),
    ):
        require(
            path.name.endswith(expected_suffix),
            f"block attempt contains an invalid delivery filename: {path.name}",
        )
    actual: set[str] = set()
    for directory, directory_names, file_names in os.walk(
        artifact_root, followlinks=False
    ):
        directory_path = Path(directory)
        for name in directory_names:
            raise StateError(
                f"block attempt contains a nested or symlinked directory: "
                f"{(directory_path / name).relative_to(artifact_root)}"
            )
        for name in file_names:
            path = directory_path / name
            relative = path.relative_to(artifact_root).as_posix()
            if path.is_symlink() or not path.is_file():
                raise StateError(f"block attempt contains unsafe entry: {relative}")
            if (
                name.endswith((".m4a", ".wav", ".pcm"))
                or re.fullmatch(r"\.anchors-ch[0-9]+\.json", name) is not None
                or name.endswith(".pronunciation-reel.m4b")
            ):
                raise StateError(
                    f"block attempt contains prohibited review media: {relative}"
                )
            if relative not in expected:
                raise StateError(f"block attempt contains unexpected entry: {relative}")
            actual.add(relative)
    require(
        actual == expected,
        "block attempt contains an incomplete delivery media set",
    )


def block_reel_path(
    state_receipt: Path, run_id: str, attempt_id: str, audiobook: Path
) -> Path:
    require(state_receipt.is_absolute(), "block state receipt path must be absolute")
    return (
        state_receipt.parent
        / "listening"
        / run_id
        / attempt_id
        / f"{audiobook.stem}.pronunciation-reel.m4b"
    )


def require_block_reel_path(
    reel: Path,
    state_receipt: Path,
    run_id: str,
    attempt_id: str,
    audiobook: Path,
    label: str,
) -> None:
    expected = block_reel_path(state_receipt, run_id, attempt_id, audiobook)
    require(
        reel == expected,
        f"{label} reel path is not the current internal listening path",
    )


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
    chapter_voice_values: list[str],
    voice_plan_sha256: str | None,
    render_version: int,
    audiobook: Path,
    sidecar: Path,
    audit: Path,
    reel: Path,
    installed_renderer: dict[str, object],
    block_plan: dict[str, object] | None = None,
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
            chapter_voice_values,
            voice_plan_sha256,
            render_version,
            input_receipt,
            installed_renderer,
            block_plan,
        )
    )
    require(
        read_regular_bytes(state_receipt, "resume-state receipt") == expected_state,
        "resume state receipt does not match final WORK, DB, or captures",
    )
    require(audiobook.stat().st_size > 0, "audiobook is empty")
    if block_plan is not None:
        require_block_attempt_contents(
            attempt_receipt,
            artifact_relative_path,
            audiobook,
            sidecar,
            audit,
        )
        require_block_reel_path(
            reel,
            state_receipt,
            run_id,
            attempt_id,
            audiobook,
            "render-success receipt",
        )
    payload: dict[str, object] = {
        "schemaVersion": 4 if block_plan is not None else 3,
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
    if block_plan is not None:
        payload.update(block_plan)
    if reel.exists() or reel.is_symlink():
        regular_file(reel, "pronunciation reel")
        payload["reelFileName"] = reel.name
        if block_plan is not None:
            payload["reelRelativePath"] = (
                f"listening/{run_id}/{attempt_id}/{reel.name}"
            )
        payload["reelSHA256"] = sha256(reel)
    if block_plan is not None:
        require_block_success_receipt(payload, "render-success receipt")
    return payload


def canonical_json(payload: dict[str, object]) -> bytes:
    return (
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def json_object(path: Path, label: str) -> dict[str, object]:
    regular_file(path, label)

    def reject_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
        payload: dict[str, object] = {}
        for key, value in pairs:
            require(key not in payload, f"{label} duplicates key: {key}")
            payload[key] = value
        return payload

    try:
        payload = json.loads(
            read_regular_bytes(path, label).decode("utf-8"),
            object_pairs_hook=reject_duplicates,
        )
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise StateError(f"{label} is not valid JSON") from error
    require(isinstance(payload, dict), f"{label} root must be an object")
    return payload


def required_string(payload: dict[str, object], field: str, label: str) -> str:
    value = payload.get(field)
    require(isinstance(value, str) and bool(value), f"{label} has invalid {field}")
    return value


def input_receipt_value(path: Path, key: str) -> str:
    regular_file(path, "render-input receipt")
    try:
        lines = read_regular_bytes(path, "render-input receipt").decode(
            "utf-8"
        ).splitlines()
    except UnicodeDecodeError as error:
        raise StateError("render-input receipt is not UTF-8") from error
    values = [
        line.removeprefix(f"{key}=")
        for line in lines
        if line.startswith(f"{key}=")
    ]
    require(
        len(values) == 1 and bool(values[0]),
        f"render-input receipt has invalid {key}",
    )
    return values[0]


def current_run_voice_identity(input_receipt: Path) -> str:
    """Return the collision-free block component without changing legacy IDs."""

    lines = receipt_lines(input_receipt)
    modes = [
        line.removeprefix("voice_plan_mode=")
        for line in lines
        if line.startswith("voice_plan_mode=")
    ]
    if not modes:
        return input_receipt_value(input_receipt, "voice_plan_id")
    require(
        modes == ["block"],
        "render-input receipt has invalid voice_plan_mode",
    )
    plan_sha = input_receipt_value(input_receipt, "voice_plan_sha256")
    require(
        SHA256_PATTERN.fullmatch(plan_sha) is not None,
        "render-input receipt has invalid voice_plan_sha256",
    )
    return f"plan-{plan_sha}"


def require_block_plan_matches_input_receipt(
    payload: dict[str, object], input_receipt: Path, label: str
) -> None:
    require_block_plan_receipt_evidence(payload, label)
    for receipt_key, payload_key in (
        ("voice_plan_mode", "voicePlanMode"),
        ("voice_plan_sha256", "voicePlanSHA256"),
        ("voice_plan_id", "voicePlanID"),
        ("voice_plan_block_count", "voicePlanBlockCount"),
        ("voice_plan_canonical_sha256", "voicePlanCanonicalSHA256"),
        ("voice_plan_resolution_sha256", "voicePlanResolutionSHA256"),
    ):
        require(
            input_receipt_value(input_receipt, receipt_key)
            == str(payload[payload_key]),
            f"{label} {payload_key} differs from render-input receipt",
        )
    for receipt_key, payload_key in (
        ("voice_plan_canonical_path", "voicePlanCanonicalFileName"),
        ("voice_plan_resolution_path", "voicePlanResolutionFileName"),
    ):
        require(
            Path(input_receipt_value(input_receipt, receipt_key)).name
            == payload[payload_key],
            f"{label} {payload_key} differs from render-input receipt",
        )


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
        run_voice_identity = current_run_voice_identity(input_receipt)
        expected_run_id = (
            f"{sha256(epub)[:12]}-{installed_renderer['echoCLI_SHA256'][:12]}-"
            f"{installed_renderer['echoResourcesSHA256'][:12]}-"
            f"{installed_renderer['rendererManifestSHA256'][:12]}-"
            f"{installed_renderer['echoSourceSHA']}-{run_voice_identity}"
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
    if historical:
        require(
            success.get("schemaVersion") == 2,
            "render-success schema must be 2 for a historical receipt chain",
        )
    else:
        require(
            success.get("schemaVersion") in {3, 4},
            "render-success schema must be 3 or 4 for a current receipt chain",
        )
        if success.get("schemaVersion") == 4:
            require_block_success_receipt(success, "render-success receipt")
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
        historical or schemas in {(2, 2, 3), (2, 2, 4)},
        "receipt chain does not use a supported historical or current schema",
    )
    block_delivery = not historical and payload.get("schemaVersion") == 4
    if block_delivery:
        require_block_success_receipt(payload, "render-success receipt")
    # A post-render operator has the accepted receipt chain, not the child
    # wrapper environment.  For a current chain, safely derive the renderer
    # identity and selected default voice from those sealed inputs when callers
    # do not explicitly supply them.  Explicit values remain cross-checked
    # below, so this does not relax the governed boundary.
    if not historical and installed_renderer is None:
        installed_renderer = renderer_identity_from_payload(
            payload, "render-success receipt"
        )
    if not historical and voice is None:
        voice = input_receipt_value(input_receipt, "voice")
    require(
        historical or installed_renderer is not None,
        "current delivery verification requires installed renderer identity",
    )
    require(
        historical or voice in VOICE_IDS,
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
        require(
            voice == input_receipt_value(input_receipt, "voice"),
            "current delivery voice differs from render-input receipt",
        )
        run_voice_identity = current_run_voice_identity(input_receipt)
        expected_run_id = (
            f"{sha256(epub)[:12]}-{installed_renderer['echoCLI_SHA256'][:12]}-"
            f"{installed_renderer['echoResourcesSHA256'][:12]}-"
            f"{installed_renderer['rendererManifestSHA256'][:12]}-"
            f"{installed_renderer['echoSourceSHA']}-{run_voice_identity}"
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
    if block_delivery:
        state_payload = json_object(state_receipt, "resume-state receipt")
        require_block_state_receipt(state_payload, "resume-state receipt")
        require_block_plan_matches_input_receipt(
            state_payload, input_receipt, "resume-state receipt"
        )
        require_block_plan_matches_input_receipt(
            payload, input_receipt, "render-success receipt"
        )
        for field in BLOCK_PLAN_RECEIPT_KEYS:
            require(
                payload.get(field) == state_payload.get(field),
                f"render-success receipt {field} differs from resume-state receipt",
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
    if block_delivery:
        require_block_attempt_contents(
            attempt_receipt,
            artifact_relative_path,
            audiobook,
            sidecar,
            audit,
        )
        require_block_reel_path(
            reel,
            state_receipt,
            run_id,
            attempt_id,
            audiobook,
            "render-success receipt",
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


def block_delivery_evidence(
    attempt_receipt: Path,
    selector: Path,
    receipt: Path,
    input_receipt: Path,
) -> dict[str, str]:
    """Read post-render block facts from the accepted, sealed receipt chain.

    This intentionally emits only facts that the runbook needs to locate and
    validate a completed block delivery.  It does not consult the wrapper's
    already-exited environment or reconstruct a plan from its short display ID.
    """

    attempt = json_object(attempt_receipt, "current-attempt receipt")
    accepted = json_object(selector, "current-accepted selector")
    success = json_object(receipt, "render-success receipt")
    require(
        attempt.get("schemaVersion") == 2,
        "current-attempt receipt schema must be 2 for block delivery",
    )
    require_block_success_receipt(success, "render-success receipt")
    renderer = renderer_identity_from_payload(success, "render-success receipt")
    require(
        canonical_json(accepted)
        == canonical_json(
            accepted_selector_snapshot(attempt_receipt, receipt, renderer)
        ),
        "current-accepted selector does not match current attempt and render success",
    )
    regular_file(input_receipt, "render-input receipt")
    require(
        input_receipt.name == success.get("inputReceiptFileName"),
        "render-input receipt filename differs from render-success receipt",
    )
    require(
        sha256(input_receipt) == success.get("inputReceiptSHA256"),
        "render-input receipt SHA-256 differs from render-success receipt",
    )
    require_block_plan_matches_input_receipt(
        success, input_receipt, "render-success receipt"
    )
    voice = input_receipt_value(input_receipt, "voice")
    require(voice in VOICE_IDS, "render-input receipt has an unapproved voice")
    plan_sha = required_string(
        success, "voicePlanSHA256", "render-success receipt"
    )
    require(
        current_run_voice_identity(input_receipt) == f"plan-{plan_sha}",
        "render-input receipt does not use the current block run identity",
    )
    reel_relative_path = required_string(
        success, "reelRelativePath", "render-success receipt"
    )
    block_count = success.get("voicePlanBlockCount")
    require(
        type(block_count) is int and block_count > 0,
        "render-success receipt has an invalid voicePlanBlockCount",
    )
    return {
        "voice_plan_mode": "block",
        "reel_relative_path": reel_relative_path,
        "voice_plan_sha256": plan_sha,
        "voice_plan_block_count": str(block_count),
        "voice": voice,
    }


def write_env0(values: dict[str, str]) -> None:
    """Write a small fixed key/value record without shell evaluation."""

    for key in (
        "voice_plan_mode",
        "reel_relative_path",
        "voice_plan_sha256",
        "voice_plan_block_count",
        "voice",
    ):
        value = values[key]
        require("\0" not in key and "\0" not in value, "env0 value contains NUL")
        sys.stdout.buffer.write(f"{key}={value}".encode("utf-8") + b"\0")


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
        command.add_argument("--chapter-voice", action="append", default=[])
        command.add_argument("--voice-plan-sha256")
        command.add_argument("--voice-plan", type=Path)
        command.add_argument("--voice-plan-id")
        command.add_argument("--voice-plan-block-count", type=int)
        command.add_argument("--voice-plan-resolution", type=Path)
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
        command.add_argument("--chapter-voice", action="append", default=[])
        command.add_argument("--voice-plan-sha256")
        command.add_argument("--voice-plan", type=Path)
        command.add_argument("--voice-plan-id")
        command.add_argument("--voice-plan-block-count", type=int)
        command.add_argument("--voice-plan-resolution", type=Path)
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
    block_evidence = commands.add_parser("block-delivery-evidence")
    block_evidence.add_argument("--attempt", type=Path, required=True)
    block_evidence.add_argument("--selector", type=Path, required=True)
    block_evidence.add_argument("--receipt", type=Path, required=True)
    block_evidence.add_argument("--input-receipt", type=Path, required=True)
    block_evidence.add_argument("--format", choices=("env0",), required=True)
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
            block_plan = block_plan_evidence_from_options(options)
            payload = capture_snapshot(
                options.work,
                options.db,
                options.epub,
                options.source_sha,
                options.voice,
                options.chapter_voice,
                options.voice_plan_sha256,
                options.render_version,
                options.input_receipt,
                installed_renderer,
                block_plan,
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
            block_plan = block_plan_evidence_from_options(options)
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
                options.chapter_voice,
                options.voice_plan_sha256,
                options.render_version,
                options.audiobook,
                options.sidecar,
                options.audit,
                options.reel,
                installed_renderer,
                block_plan,
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
        elif options.command == "block-delivery-evidence":
            write_env0(
                block_delivery_evidence(
                    options.attempt,
                    options.selector,
                    options.receipt,
                    options.input_receipt,
                )
            )
        return 0
    except (OSError, StateError, json.JSONDecodeError) as error:
        print(f"echo_pronunciation_state: {error}", file=sys.stderr)
        return 65


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
