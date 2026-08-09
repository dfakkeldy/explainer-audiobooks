#!/usr/bin/env python3
"""Strict identities and attestation for one installed Echo renderer package."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import platform
import pwd
import re
import stat
import subprocess
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import BinaryIO, Iterator, Mapping, Sequence

from echo_pronunciation_state import read_installed_renderer_identity


ACCEPTED_INSTALLER_SOURCE_SHA = "8cb1e09de81feeb820e23b151b3a5b40efa4c1c5"
ACCEPTED_INSTALLER_SOURCE_SHAS = frozenset(
    {
        "2f23aceedb1b9f25b7ea4410756eea32a59af8cd",
        "d7f27b02f5a6046988d14c7e147e99904f66464b",
        ACCEPTED_INSTALLER_SOURCE_SHA,
    }
)

_EXECUTABLE_NAME = "echo-cli"
_RESOURCES_NAME = "EchoNarrationResources"
_MANIFEST_NAME = "renderer-manifest.json"
_TOP_LEVEL_NAMES = {_EXECUTABLE_NAME, _RESOURCES_NAME, _MANIFEST_NAME}
_COMMIT_SHA_PATTERN = re.compile(r"[0-9a-f]{40}\Z")
_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}\Z")
_ARCHITECTURE_PATTERN = re.compile(r"[A-Za-z0-9_]+\Z")
_VERSION_PATTERN = re.compile(r"ONNX rv([0-9]+) \(Release\)\n?\Z")
_VERSION_NUMBER_PATTERN = re.compile(r"[0-9]+(?:\.[0-9]+){1,2}\Z")
_ACCEPTED_SUBCOMMAND_CAPABILITIES = (
    "export-blocks",
    "resolve-voice-plan",
    "verify-sidecar",
)
_SELECTOR_NAME = "approved-renderer.json"
_ENV0_KEYS = (
    "ECHO_RENDERER_ROOT",
    "ECHO_RENDERER_BUILD_ROOT",
    "ECHO_RENDERER_MANIFEST",
    "ECHO_RENDERER_MANIFEST_SHA256",
    "APPROVED_ECHO_INSTALLER_SHA",
    "ECHO_SOURCE_SHA",
    "CLI",
    "ECHO_CLI_SHA256",
    "ECHO_RESOURCE_DIR",
    "ECHO_RESOURCES_SHA256",
    "ECHO_RENDER_VERSION",
    "ECHO_MODEL_REVISION",
    "ECHO_MODEL_EXPECTED_BYTES",
    "ECHO_MODEL_BYTES_ATTESTED",
)


@dataclass(frozen=True)
class FileIdentity:
    sha256: str
    byte_count: int


@dataclass(frozen=True)
class ResourceTreeIdentity:
    sha256: str
    regular_file_count: int


@dataclass(frozen=True)
class RendererState:
    renderer_root: Path
    source_sha: str
    manifest_sha: str
    build_root: Path
    manifest_path: Path
    executable: Path
    resources: Path
    installer_source_sha: str
    executable_sha256: str
    resources_sha256: str
    render_version: int
    architectures: Sequence[str]
    minimum_macos_version: str
    capabilities: Sequence[str]
    model_revision: str
    model_expected_byte_count: int
    model_delivery_mode: str
    model_bytes_attested: bool


def canonical_renderer_root(value: str | None) -> Path:
    """Return one canonical, absolute, link-free installed-renderer root."""
    if value is None:
        root = (
            _effective_account_home()
            / "Library"
            / "Application Support"
            / "Echo"
            / "Renderers"
        )
    else:
        root = Path(value)
    if not root.is_absolute():
        raise ValueError("renderer root must be absolute")
    _require_directory(root, "renderer root")
    return root


def resolve_new_renderer(renderer_root: Path, source_sha: str) -> RendererState:
    """Lease and consume the strict selector for one new renderer run."""
    _validate_commit_sha(source_sha, "source SHA")
    _require_directory(renderer_root, "renderer root")
    source_root = renderer_root / source_sha
    _require_directory(source_root, "renderer source directory")
    selector = source_root / _SELECTOR_NAME
    with _leased_selector(selector):
        payload = strict_json_object(selector, "renderer selector")
        _require_exact_keys(
            payload,
            {"schemaVersion", "echoSourceSHA", "manifestSHA256"},
            "renderer selector",
        )
        if _require_integer(payload["schemaVersion"], "schemaVersion") != 1:
            raise ValueError("renderer selector schemaVersion must be 1")
        selected_source_sha = _require_string(
            payload["echoSourceSHA"], "echoSourceSHA"
        )
        _validate_commit_sha(selected_source_sha, "echoSourceSHA")
        if selected_source_sha != source_sha:
            raise ValueError("renderer selector source SHA does not match the request")
        manifest_sha = _require_sha256(
            payload["manifestSHA256"], "manifestSHA256"
        )
        return parse_manifest(
            source_root / manifest_sha / _MANIFEST_NAME,
            source_sha,
            manifest_sha,
        )


def resolve_resume_renderer(
    renderer_root: Path,
    source_sha: str,
    resume_state_path: Path,
) -> RendererState:
    """Resolve an installed build only from an exact sealed resume receipt."""
    _validate_commit_sha(source_sha, "source SHA")
    _require_directory(renderer_root, "renderer root")
    _require_canonical_absolute_file(resume_state_path, "resume-state receipt")
    sealed_source_sha, manifest_sha = read_installed_renderer_identity(
        resume_state_path
    )
    if sealed_source_sha != source_sha:
        raise ValueError("resume-state Echo source SHA does not match the request")
    return parse_manifest(
        renderer_root / sealed_source_sha / manifest_sha / _MANIFEST_NAME,
        sealed_source_sha,
        manifest_sha,
    )


def emit_env0(state: RendererState, output: BinaryIO) -> None:
    """Emit the fixed installed-renderer environment as alternating NUL records."""
    values = {
        "ECHO_RENDERER_ROOT": str(state.renderer_root),
        "ECHO_RENDERER_BUILD_ROOT": str(state.build_root),
        "ECHO_RENDERER_MANIFEST": str(state.manifest_path),
        "ECHO_RENDERER_MANIFEST_SHA256": state.manifest_sha,
        "APPROVED_ECHO_INSTALLER_SHA": state.installer_source_sha,
        "ECHO_SOURCE_SHA": state.source_sha,
        "CLI": str(state.executable),
        "ECHO_CLI_SHA256": state.executable_sha256,
        "ECHO_RESOURCE_DIR": str(state.resources),
        "ECHO_RESOURCES_SHA256": state.resources_sha256,
        "ECHO_RENDER_VERSION": str(state.render_version),
        "ECHO_MODEL_REVISION": state.model_revision,
        "ECHO_MODEL_EXPECTED_BYTES": str(state.model_expected_byte_count),
        "ECHO_MODEL_BYTES_ATTESTED": "true" if state.model_bytes_attested else "false",
    }
    for key in _ENV0_KEYS:
        output.write(key.encode("ascii") + b"\0")
        output.write(values[key].encode("utf-8") + b"\0")


def strict_json_object(path: Path, label: str) -> dict[str, object]:
    """Read one regular UTF-8 JSON file and reject duplicate keys at every depth."""

    def reject_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"{label} contains duplicate JSON key: {key}")
            result[key] = value
        return result

    data = _read_regular_file(path, label)
    try:
        payload = json.loads(
            data.decode("utf-8"), object_pairs_hook=reject_duplicates
        )
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ValueError(f"{label} is invalid JSON") from error
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must contain a JSON object")
    return payload


def identify_regular_file(path: Path) -> FileIdentity:
    """Return the SHA-256 and byte count of one regular non-link file."""
    try:
        metadata = path.lstat()
    except OSError as error:
        raise ValueError(f"cannot inspect regular file: {path}") from error
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise ValueError(f"expected a regular non-link file: {path}")

    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    file_descriptor = -1
    try:
        file_descriptor = os.open(path, flags)
        opened = os.fstat(file_descriptor)
        current = os.stat(path, follow_symlinks=False)
        if not stat.S_ISREG(opened.st_mode):
            raise ValueError(f"expected a regular file: {path}")
        if opened.st_dev != current.st_dev or opened.st_ino != current.st_ino:
            raise ValueError(f"regular file changed while opening: {path}")

        digest = hashlib.sha256()
        byte_count = 0
        with os.fdopen(file_descriptor, "rb") as handle:
            file_descriptor = -1
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
                byte_count += len(chunk)
        return FileIdentity(sha256=digest.hexdigest(), byte_count=byte_count)
    except OSError as error:
        raise ValueError(f"cannot read regular file: {path}") from error
    finally:
        if file_descriptor >= 0:
            os.close(file_descriptor)


def identify_resource_tree(root: Path) -> ResourceTreeIdentity:
    """Identify a link-free tree using the frozen resource-tree-v1 framing."""
    _require_directory(root, "resource root")
    regular_files: list[tuple[str, Path]] = []

    def visit(directory: Path, relative_parts: tuple[str, ...]) -> None:
        try:
            entries = list(os.scandir(directory))
        except OSError as error:
            raise ValueError(f"cannot read resource directory: {directory}") from error
        for entry in entries:
            entry_path = Path(entry.path)
            try:
                metadata = entry.stat(follow_symlinks=False)
            except OSError as error:
                raise ValueError(f"cannot inspect resource entry: {entry_path}") from error
            if stat.S_ISLNK(metadata.st_mode):
                raise ValueError(f"resource links are not allowed: {entry_path}")

            parts = (*relative_parts, entry.name)
            relative_path = "/".join(parts)
            _validate_relative_path(relative_path, "resource entry path")
            if stat.S_ISDIR(metadata.st_mode):
                visit(entry_path, parts)
            elif stat.S_ISREG(metadata.st_mode):
                regular_files.append((relative_path, entry_path))
            else:
                raise ValueError(f"special resource files are not allowed: {entry_path}")

    visit(root, ())
    tree_digest = hashlib.sha256()
    for relative_path, path in sorted(regular_files, key=lambda item: item[0]):
        try:
            path_bytes = relative_path.encode("utf-8")
        except UnicodeEncodeError as error:
            raise ValueError(f"resource path is not valid UTF-8: {relative_path!r}") from error
        file_identity = identify_regular_file(path)
        tree_digest.update(len(path_bytes).to_bytes(8, "big", signed=False))
        tree_digest.update(path_bytes)
        tree_digest.update(bytes.fromhex(file_identity.sha256))
    return ResourceTreeIdentity(
        sha256=tree_digest.hexdigest(),
        regular_file_count=len(regular_files),
    )


def parse_manifest(path: Path, source_sha: str, manifest_sha: str) -> RendererState:
    """Strictly consume and byte-attest one canonical renderer manifest."""
    _validate_commit_sha(source_sha, "source SHA")
    _validate_sha256(manifest_sha, "manifest SHA")
    if path.name != _MANIFEST_NAME:
        raise ValueError("renderer manifest must use the exact manifest file name")

    build_root = path.parent
    source_root = build_root.parent
    renderer_root = source_root.parent
    _require_directory(renderer_root, "renderer root")
    _require_directory(source_root, "renderer source directory")
    _require_directory(build_root, "renderer build directory")
    if source_root.name != source_sha:
        raise ValueError("renderer source directory does not match the source SHA")
    if build_root.name != manifest_sha:
        raise ValueError("renderer build directory does not match the manifest SHA")

    try:
        entries = list(os.scandir(build_root))
    except OSError as error:
        raise ValueError(f"cannot inspect renderer package: {build_root}") from error
    names = {entry.name for entry in entries}
    if len(entries) != len(_TOP_LEVEL_NAMES) or names != _TOP_LEVEL_NAMES:
        raise ValueError("renderer package has unexpected top-level entries")

    manifest_data = _read_regular_file(path, "renderer manifest")
    if hashlib.sha256(manifest_data).hexdigest() != manifest_sha:
        raise ValueError("renderer manifest bytes do not match the expected manifest SHA")
    payload = strict_json_object(path, "renderer manifest")
    if manifest_data != _canonical_json_bytes(payload):
        raise ValueError("renderer manifest is not canonically encoded")

    _require_exact_keys(
        payload,
        {
            "schemaVersion",
            "echoSourceSHA",
            "installerSourceSHA",
            "executablePath",
            "executable",
            "resourcesPath",
            "resources",
            "renderVersion",
            "buildConfiguration",
            "architectures",
            "minimumMacOSVersion",
            "modelPolicy",
            "capabilities",
        },
        "renderer manifest",
    )
    if _require_integer(payload["schemaVersion"], "schemaVersion") != 1:
        raise ValueError("schemaVersion must be 1")

    manifest_source_sha = _require_string(payload["echoSourceSHA"], "echoSourceSHA")
    _validate_commit_sha(manifest_source_sha, "echoSourceSHA")
    if manifest_source_sha != source_sha:
        raise ValueError("renderer manifest source SHA does not match its directory")
    installer_source_sha = _require_string(
        payload["installerSourceSHA"], "installerSourceSHA"
    )
    _validate_commit_sha(installer_source_sha, "installerSourceSHA")
    if installer_source_sha not in ACCEPTED_INSTALLER_SOURCE_SHAS:
        raise ValueError("renderer manifest installer identity is not accepted")

    executable_path = _require_string(payload["executablePath"], "executablePath")
    resources_path = _require_string(payload["resourcesPath"], "resourcesPath")
    _validate_relative_path(executable_path, "executablePath")
    _validate_relative_path(resources_path, "resourcesPath")
    if executable_path != _EXECUTABLE_NAME or resources_path != _RESOURCES_NAME:
        raise ValueError("renderer manifest paths do not match the package layout")

    executable_payload = _require_object(payload["executable"], "executable")
    _require_exact_keys(executable_payload, {"sha256", "byteCount"}, "executable")
    executable_identity = FileIdentity(
        sha256=_require_sha256(executable_payload["sha256"], "executable.sha256"),
        byte_count=_require_nonnegative_integer(
            executable_payload["byteCount"], "executable.byteCount"
        ),
    )
    resources_payload = _require_object(payload["resources"], "resources")
    _require_exact_keys(
        resources_payload, {"sha256", "regularFileCount"}, "resources"
    )
    resources_identity = ResourceTreeIdentity(
        sha256=_require_sha256(resources_payload["sha256"], "resources.sha256"),
        regular_file_count=_require_nonnegative_integer(
            resources_payload["regularFileCount"], "resources.regularFileCount"
        ),
    )

    render_version = _require_positive_integer(payload["renderVersion"], "renderVersion")
    build_configuration = _require_nonempty_string(
        payload["buildConfiguration"], "buildConfiguration"
    )
    if build_configuration != "Release":
        raise ValueError("buildConfiguration must be Release")

    architectures = _require_nonempty_unique_string_list(
        payload["architectures"], "architectures"
    )
    if any(_ARCHITECTURE_PATTERN.fullmatch(value) is None for value in architectures):
        raise ValueError("architectures contains an invalid architecture")
    host_architecture = platform.machine()
    if not host_architecture or host_architecture not in architectures:
        raise ValueError("renderer does not support the current host architecture")

    minimum_macos_version = _require_nonempty_string(
        payload["minimumMacOSVersion"], "minimumMacOSVersion"
    )
    minimum_version = _version_tuple(minimum_macos_version)
    host_macos_version = platform.mac_ver()[0]
    if not host_macos_version:
        raise ValueError("cannot determine the current host macOS version")
    if minimum_version > _version_tuple(host_macos_version):
        raise ValueError("renderer requires a newer macOS version than this host")

    capabilities = _require_nonempty_unique_string_list(
        payload["capabilities"], "capabilities"
    )
    model_payload = _require_object(payload["modelPolicy"], "modelPolicy")
    _require_exact_keys(
        model_payload,
        {"revision", "expectedByteCount", "deliveryMode", "modelBytesAttested"},
        "modelPolicy",
    )
    model_revision = _require_nonempty_string(
        model_payload["revision"], "modelPolicy.revision"
    )
    model_expected_byte_count = _require_nonnegative_integer(
        model_payload["expectedByteCount"], "modelPolicy.expectedByteCount"
    )
    model_delivery_mode = _require_string(
        model_payload["deliveryMode"], "modelPolicy.deliveryMode"
    )
    if model_delivery_mode != "sharedEchoCache":
        raise ValueError("modelPolicy.deliveryMode must be sharedEchoCache")
    model_bytes_attested = model_payload["modelBytesAttested"]
    if model_bytes_attested is not False:
        raise ValueError("modelPolicy.modelBytesAttested must be false")

    executable = build_root / executable_path
    resources = build_root / resources_path
    if identify_regular_file(executable) != executable_identity:
        raise ValueError("renderer executable identity does not match the manifest")
    if identify_resource_tree(resources) != resources_identity:
        raise ValueError("renderer resource identity does not match the manifest")

    return RendererState(
        renderer_root=renderer_root,
        source_sha=source_sha,
        manifest_sha=manifest_sha,
        build_root=build_root,
        manifest_path=path,
        executable=executable,
        resources=resources,
        installer_source_sha=installer_source_sha,
        executable_sha256=executable_identity.sha256,
        resources_sha256=resources_identity.sha256,
        render_version=render_version,
        architectures=architectures,
        minimum_macos_version=minimum_macos_version,
        capabilities=capabilities,
        model_revision=model_revision,
        model_expected_byte_count=model_expected_byte_count,
        model_delivery_mode=model_delivery_mode,
        model_bytes_attested=False,
    )


def attest_renderer(state: RendererState) -> None:
    """Re-attest package bytes and the live Release CLI contract."""
    observed = parse_manifest(state.manifest_path, state.source_sha, state.manifest_sha)
    if observed != state:
        raise ValueError("renderer state does not match its installed package")

    account_home = Path(pwd.getpwuid(os.geteuid()).pw_dir).resolve(strict=True)
    environment = {
        "ECHO_RESOURCE_DIR": str(state.resources),
        "HOME": str(account_home),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
    }
    version_output = _run_probe(
        [str(state.executable), "--version"], environment=environment
    )
    match = _VERSION_PATTERN.fullmatch(version_output)
    if match is None or int(match.group(1)) != state.render_version:
        raise ValueError("live render version does not match the manifest")

    narrate_help = _run_probe(
        [str(state.executable), "narrate", "--help"], environment=environment
    )
    narrate_capabilities = tuple(
        capability for capability in state.capabilities if capability.startswith("--")
    )
    subcommand_capabilities = tuple(
        capability for capability in state.capabilities if not capability.startswith("--")
    )
    unexpected_subcommands = [
        capability
        for capability in subcommand_capabilities
        if capability not in _ACCEPTED_SUBCOMMAND_CAPABILITIES
    ]
    if unexpected_subcommands:
        raise ValueError(
            "renderer manifest has unsupported subcommand capabilities: "
            f"{unexpected_subcommands}"
        )
    missing = [
        capability
        for capability in narrate_capabilities
        if not _capability_present(capability, narrate_help)
    ]
    if missing:
        raise ValueError(f"live capabilities do not match the manifest: {missing}")

    for capability in subcommand_capabilities:
        subcommand_help = _run_probe(
            [str(state.executable), capability, "--help"],
            environment=environment,
        )
        if not _capability_present(capability, subcommand_help):
            raise ValueError(
                f"live capabilities do not match the manifest: {capability}"
            )


def _read_regular_file(path: Path, label: str) -> bytes:
    try:
        metadata = path.lstat()
    except OSError as error:
        raise ValueError(f"cannot inspect {label}: {path}") from error
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise ValueError(f"{label} must be a regular non-link file: {path}")
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    file_descriptor = -1
    try:
        file_descriptor = os.open(path, flags)
        opened = os.fstat(file_descriptor)
        current = os.stat(path, follow_symlinks=False)
        if not stat.S_ISREG(opened.st_mode):
            raise ValueError(f"{label} must be a regular file: {path}")
        if opened.st_dev != current.st_dev or opened.st_ino != current.st_ino:
            raise ValueError(f"{label} changed while opening: {path}")
        with os.fdopen(file_descriptor, "rb") as handle:
            file_descriptor = -1
            return handle.read()
    except OSError as error:
        raise ValueError(f"cannot read {label}: {path}") from error
    finally:
        if file_descriptor >= 0:
            os.close(file_descriptor)


def _require_directory(path: Path, label: str) -> None:
    try:
        metadata = path.lstat()
        resolved = path.resolve(strict=True)
    except OSError as error:
        raise ValueError(f"cannot inspect {label}: {path}") from error
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
        raise ValueError(f"{label} must be a regular non-link directory: {path}")
    if path != resolved:
        raise ValueError(f"{label} must be a canonical path without symlink components")


def _require_canonical_absolute_file(path: Path, label: str) -> None:
    if not path.is_absolute():
        raise ValueError(f"{label} must be absolute")
    try:
        metadata = path.lstat()
        resolved = path.resolve(strict=True)
    except OSError as error:
        raise ValueError(f"cannot inspect {label}: {path}") from error
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise ValueError(f"{label} must be a regular non-link file: {path}")
    if path != resolved:
        raise ValueError(f"{label} must be canonical without symlink components")


def _effective_account_home() -> Path:
    try:
        account_home = Path(pwd.getpwuid(os.geteuid()).pw_dir).resolve(strict=True)
    except (KeyError, OSError) as error:
        raise ValueError("cannot resolve the effective account home") from error
    _require_directory(account_home, "effective account home")
    return account_home


@contextmanager
def _leased_selector(selector: Path) -> Iterator[None]:
    """Hold the shared nonblocking selector lease for one resolution."""
    lock_root = (
        _effective_account_home()
        / ".cache"
        / "explainer-audiobooks"
        / "echo-pronunciation-leases"
    )
    try:
        lock_root.mkdir(mode=0o700, parents=True, exist_ok=True)
    except OSError as error:
        raise ValueError("cannot create the renderer selector lease root") from error
    _require_directory(lock_root, "renderer selector lease root")
    resource = str(selector.resolve(strict=False))
    lock_name = hashlib.sha256(resource.encode("utf-8")).hexdigest() + ".lock"
    lock_path = lock_root / lock_name
    flags = os.O_RDWR | os.O_CREAT
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = -1
    try:
        descriptor = os.open(lock_path, flags, 0o600)
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise ValueError("renderer selector lease is not a regular file")
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ValueError("active renderer selector lease blocks resolution") from error
        yield
    except OSError as error:
        raise ValueError("cannot acquire the renderer selector lease") from error
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _canonical_json_bytes(payload: Mapping[str, object]) -> bytes:
    return (
        json.dumps(
            dict(payload),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        + b"\n"
    )


def _validate_relative_path(value: str, field: str) -> None:
    if not value or value in (".", "..") or "\\" in value:
        raise ValueError(f"{field} must be a nonempty POSIX-relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or path.as_posix() != value:
        raise ValueError(f"{field} must be a normalized POSIX-relative path")
    if any(part in ("", ".", "..") for part in path.parts):
        raise ValueError(f"{field} contains an unsafe path component")


def _require_exact_keys(
    payload: Mapping[str, object], expected: set[str], field: str
) -> None:
    actual = set(payload)
    if actual != expected:
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        raise ValueError(
            f"{field} keys do not match schema; missing={missing}, unknown={unknown}"
        )


def _require_object(value: object, field: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be an object")
    return value


def _require_string(value: object, field: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string")
    return value


def _require_nonempty_string(value: object, field: str) -> str:
    result = _require_string(value, field)
    if not result:
        raise ValueError(f"{field} must not be empty")
    return result


def _require_integer(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{field} must be an integer")
    return value


def _require_nonnegative_integer(value: object, field: str) -> int:
    result = _require_integer(value, field)
    if result < 0:
        raise ValueError(f"{field} must not be negative")
    return result


def _require_positive_integer(value: object, field: str) -> int:
    result = _require_integer(value, field)
    if result <= 0:
        raise ValueError(f"{field} must be a positive integer")
    return result


def _require_sha256(value: object, field: str) -> str:
    result = _require_string(value, field)
    _validate_sha256(result, field)
    return result


def _require_nonempty_unique_string_list(
    value: object, field: str
) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field} must be a nonempty array")
    result = tuple(
        _require_nonempty_string(item, f"{field} item") for item in value
    )
    if len(set(result)) != len(result):
        raise ValueError(f"{field} must not contain duplicates")
    return result


def _validate_commit_sha(value: str, field: str) -> None:
    if _COMMIT_SHA_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{field} must be 40 lowercase hexadecimal characters")


def _validate_sha256(value: str, field: str) -> None:
    if _SHA256_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{field} must be 64 lowercase hexadecimal characters")


def _version_tuple(value: str) -> tuple[int, int, int]:
    if _VERSION_NUMBER_PATTERN.fullmatch(value) is None:
        raise ValueError(f"invalid macOS version: {value}")
    components = [int(component, 10) for component in value.split(".")]
    return tuple((components + [0, 0])[:3])


def _run_probe(arguments: list[str], *, environment: dict[str, str]) -> str:
    try:
        completed = subprocess.run(
            arguments,
            check=True,
            capture_output=True,
            text=True,
            env=environment,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise ValueError(f"renderer probe failed: {arguments[0]}") from error
    if not isinstance(completed.stdout, str):
        raise ValueError(f"renderer probe returned invalid output: {arguments[0]}")
    return completed.stdout


def _capability_present(capability: str, help_output: str) -> bool:
    return (
        re.search(
            rf"(?<![A-Za-z0-9_-]){re.escape(capability)}(?![A-Za-z0-9_-])",
            help_output,
        )
        is not None
    )


class _UsageError(ValueError):
    pass


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise _UsageError(message)


def _argument_parser() -> argparse.ArgumentParser:
    parser = _ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("resolve-new", "resolve-resume"):
        command = commands.add_parser(name)
        command.add_argument("--source-sha", required=True)
        command.add_argument("--renderer-root")
        command.add_argument("--format", choices=("env0",), required=True)
        if name == "resolve-resume":
            command.add_argument("--resume-state", type=Path, required=True)
    attest = commands.add_parser("attest")
    attest.add_argument("--source-sha", required=True)
    attest.add_argument("--manifest-sha", required=True)
    attest.add_argument("--renderer-root")
    return parser


def _operator_install_recovery(source_sha: str) -> str:
    return (
        "operator-only recovery command:\n"
        "PYTHONPATH=Scripts python3 -m echo_renderer.cli install \\\n"
        "  --installer-worktree <clean-reviewed-installer-worktree> \\\n"
        f"  --installer-sha {ACCEPTED_INSTALLER_SOURCE_SHA} \\\n"
        "  --source-worktree <clean-source-worktree-at-SHA> \\\n"
        f"  --source-sha {source_sha} \\\n"
        "  --promote"
    )


def main(argv: Sequence[str] | None = None) -> int:
    try:
        options = _argument_parser().parse_args(argv)
    except _UsageError as error:
        print(f"echo_installed_renderer: usage error: {error}", file=sys.stderr)
        return 64

    try:
        renderer_root = canonical_renderer_root(options.renderer_root)
        if options.command == "resolve-new":
            state = resolve_new_renderer(renderer_root, options.source_sha)
            emit_env0(state, sys.stdout.buffer)
        elif options.command == "resolve-resume":
            state = resolve_resume_renderer(
                renderer_root,
                options.source_sha,
                options.resume_state,
            )
            emit_env0(state, sys.stdout.buffer)
        else:
            _validate_commit_sha(options.source_sha, "source SHA")
            _validate_sha256(options.manifest_sha, "manifest SHA")
            state = parse_manifest(
                renderer_root
                / options.source_sha
                / options.manifest_sha
                / _MANIFEST_NAME,
                options.source_sha,
                options.manifest_sha,
            )
            attest_renderer(state)
        return 0
    except (OSError, ValueError) as error:
        print(f"echo_installed_renderer: {error}", file=sys.stderr)
        if options.command in ("resolve-new", "resolve-resume") and (
            _COMMIT_SHA_PATTERN.fullmatch(options.source_sha) is not None
        ):
            print(_operator_install_recovery(options.source_sha), file=sys.stderr)
        return 65


if __name__ == "__main__":
    raise SystemExit(main())
