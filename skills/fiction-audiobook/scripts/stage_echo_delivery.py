#!/usr/bin/env python3
"""Atomically stage one Echo-clean fiction audiobook edition."""

from __future__ import annotations

import argparse
import ctypes
import errno
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path


PRODUCTION_DIRECTORIES = (
    "source",
    "checks",
    "narration",
    "covers",
    "publication",
    "previous",
)
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass(frozen=True)
class DeliveryRequest:
    slug: str
    edition_id: str
    m4b: Path
    epub: Path
    alignment: Path
    cover: Path
    production: Path
    destination: Path


@dataclass(frozen=True)
class DeliveryResult:
    decision: str
    destination: str
    staging_directory: str | None
    applied: bool
    root_files: tuple[str, ...]


@dataclass(frozen=True)
class _DirectorySnapshot:
    device: int
    inode: int
    tree: dict[str, tuple[str, str]]


def _artifact_paths(request: DeliveryRequest) -> dict[str, Path]:
    return {
        f"{request.slug}.m4b": Path(request.m4b),
        f"{request.slug}.epub": Path(request.epub),
        f"{request.slug}.alignment.json": Path(request.alignment),
        "cover.png": Path(request.cover),
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _reject_symlink_components(path: Path, label: str) -> None:
    current = path
    while True:
        if current.is_symlink():
            raise ValueError(
                f"{label} must not be a symlink or use a symlink ancestor: {current}"
            )
        parent = current.parent
        if parent == current:
            return
        current = parent


def _require_regular_file(path: Path, label: str) -> None:
    _reject_symlink_components(path, label)
    if not path.is_file():
        raise ValueError(f"{label} must be an existing regular file: {path}")


def _difference_message(actual: set[str], expected: set[str]) -> str:
    differences = sorted(actual ^ expected)
    return ", ".join(differences) if differences else "entry type mismatch"


def _validate_tree(path: Path, label: str) -> None:
    _reject_symlink_components(path, label)
    if not path.is_dir():
        raise ValueError(f"{label} must be a directory: {path}")
    for entry in path.rglob("*"):
        if entry.is_symlink():
            raise ValueError(f"{label} must not contain a symlink: {entry}")
        if not entry.is_dir() and not entry.is_file():
            raise ValueError(f"{label} contains a nonregular item: {entry}")


def _manifest(request: DeliveryRequest, hashes: dict[str, str]) -> dict[str, object]:
    return {
        "schemaVersion": 1,
        "slug": request.slug,
        "editionId": request.edition_id,
        "rootArtifacts": hashes,
    }


def _json_bytes(payload: object) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _reject_json_constant(value: str) -> object:
    raise ValueError(f"nonstandard JSON constant: {value}")


def _unique_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _load_json(path: Path, label: str) -> object:
    try:
        text = path.read_text(encoding="utf-8")
        return json.loads(
            text,
            parse_constant=_reject_json_constant,
            object_pairs_hook=_unique_json_object,
        )
    except (UnicodeDecodeError, ValueError) as error:
        raise ValueError(f"{label} must be valid JSON: {error}") from error


def _validate_source(request: DeliveryRequest) -> tuple[dict[str, Path], dict[str, str]]:
    if not isinstance(request.slug, str) or not SLUG_PATTERN.fullmatch(request.slug):
        raise ValueError("slug must be lowercase words or digits separated by hyphens")
    if not isinstance(request.edition_id, str) or not request.edition_id.strip():
        raise ValueError("edition ID must be nonempty")

    artifacts = _artifact_paths(request)
    supplied = {
        "m4b": Path(request.m4b),
        "epub": Path(request.epub),
        "alignment": Path(request.alignment),
        "cover": Path(request.cover),
    }
    expected_names = {
        "m4b": f"{request.slug}.m4b",
        "epub": f"{request.slug}.epub",
        "alignment": f"{request.slug}.alignment.json",
        "cover": "cover.png",
    }
    for label, path in supplied.items():
        if path.name != expected_names[label]:
            raise ValueError(
                f"{label} for slug {request.slug} must be named {expected_names[label]}"
            )
        _require_regular_file(path, label)

    alignment = _load_json(Path(request.alignment), "alignment")
    if not isinstance(alignment, (dict, list)):
        raise ValueError("alignment JSON must be an object or array")
    if not alignment:
        raise ValueError("alignment JSON must be nonempty")

    production = Path(request.production)
    _validate_tree(production, "production")
    actual = {path.name for path in production.iterdir()}
    expected = set(PRODUCTION_DIRECTORIES)
    if actual != expected:
        raise ValueError(
            "production must contain exactly the six required directories; conflict: "
            + _difference_message(actual, expected)
        )
    for name in PRODUCTION_DIRECTORIES:
        directory = production / name
        if directory.is_symlink() or not directory.is_dir():
            raise ValueError(f"production {name} must be a non-symlink directory")
    if any((production / "previous").iterdir()):
        raise ValueError("production previous must start empty; only the stager may populate it")

    destination = Path(request.destination)
    _reject_symlink_components(destination.parent, "destination parent")
    if not destination.parent.is_dir():
        raise ValueError(f"destination parent must be an existing directory: {destination.parent}")

    hashes = {name: _sha256(path) for name, path in artifacts.items()}
    return artifacts, hashes


def _validate_destination(request: DeliveryRequest) -> None:
    destination = Path(request.destination)
    _reject_symlink_components(destination, "destination")
    if not destination.exists():
        return
    if not destination.is_dir():
        raise ValueError(f"destination must be a directory: {destination}")

    expected_root = set(_artifact_paths(request)) | {"_production"}
    actual_root = {path.name for path in destination.iterdir()}
    if actual_root != expected_root:
        raise ValueError(
            "destination root conflicts with the generated allowlist: "
            + _difference_message(actual_root, expected_root)
        )
    for name in _artifact_paths(request):
        _require_regular_file(destination / name, f"destination {name}")

    production = destination / "_production"
    _validate_tree(production, "destination _production")
    actual_production = {path.name for path in production.iterdir()}
    expected_production = set(PRODUCTION_DIRECTORIES)
    if actual_production != expected_production:
        raise ValueError(
            "destination _production conflicts with the generated allowlist: "
            + _difference_message(actual_production, expected_production)
        )
    for name in PRODUCTION_DIRECTORIES:
        path = production / name
        if path.is_symlink() or not path.is_dir():
            raise ValueError(f"destination _production/{name} must be a non-symlink directory")

    manifest_path = production / "checks/delivery-manifest.json"
    _require_regular_file(manifest_path, "destination delivery manifest")
    manifest = _load_json(manifest_path, "destination delivery manifest")
    if not isinstance(manifest, dict):
        raise ValueError("destination delivery manifest must be a JSON object")
    expected_fields = {"schemaVersion", "slug", "editionId", "rootArtifacts"}
    if set(manifest) != expected_fields:
        raise ValueError(
            "destination delivery manifest fields conflict: "
            + _difference_message(set(manifest), expected_fields)
        )
    if type(manifest["schemaVersion"]) is not int or manifest["schemaVersion"] != 1:
        raise ValueError("destination delivery manifest schemaVersion must be integer 1")
    if manifest["slug"] != request.slug:
        raise ValueError("destination delivery manifest slug does not match the title")
    edition_id = manifest["editionId"]
    if not isinstance(edition_id, str) or not edition_id.strip():
        raise ValueError("destination delivery manifest editionId must be nonempty")
    recorded_hashes = manifest["rootArtifacts"]
    expected_artifacts = _artifact_paths(request)
    if not isinstance(recorded_hashes, dict) or set(recorded_hashes) != set(
        expected_artifacts
    ):
        actual_names = (
            set(recorded_hashes) if isinstance(recorded_hashes, dict) else set()
        )
        raise ValueError(
            "destination delivery manifest root artifact names conflict: "
            + _difference_message(actual_names, set(expected_artifacts))
        )
    for name in expected_artifacts:
        if recorded_hashes[name] != _sha256(destination / name):
            raise ValueError(
                f"destination delivery manifest hash does not match live artifact: {name}"
            )


def _copy_root_artifact(source: Path, destination: Path) -> None:
    shutil.copy2(source, destination)


def _write_manifest(stage: Path, payload: object) -> None:
    path = stage / "_production/checks/delivery-manifest.json"
    path.write_bytes(_json_bytes(payload))


def _validate_stage(stage: Path, root_hashes: dict[str, str]) -> None:
    expected = set(root_hashes) | {"_production"}
    actual = {path.name for path in stage.iterdir()}
    if actual != expected:
        raise ValueError(
            "staged root conflicts with the generated allowlist: "
            + _difference_message(actual, expected)
        )
    for name, expected_hash in root_hashes.items():
        artifact = stage / name
        _require_regular_file(artifact, f"staged {name}")
        if _sha256(artifact) != expected_hash:
            raise ValueError(f"staged artifact hash drift: {name}")
    _validate_tree(stage / "_production", "staged _production")


def _build_stage(
    request: DeliveryRequest,
    artifacts: dict[str, Path],
    root_hashes: dict[str, str],
) -> Path:
    stage = Path(
        tempfile.mkdtemp(
            prefix=f".{request.slug}.staging-", dir=Path(request.destination).parent
        )
    )
    try:
        for name, source in artifacts.items():
            _copy_root_artifact(source, stage / name)
        staged_production = stage / "_production"
        staged_production.mkdir()
        for name in PRODUCTION_DIRECTORIES:
            shutil.copytree(Path(request.production) / name, staged_production / name)
        _write_manifest(stage, _manifest(request, root_hashes))
        _validate_stage(stage, root_hashes)
        return stage
    except BaseException:
        if stage.exists():
            shutil.rmtree(stage)
        raise


def _tree_snapshot(root: Path, *, omit_previous: bool = False) -> dict[str, tuple[str, str]]:
    snapshot: dict[str, tuple[str, str]] = {}
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if omit_previous and relative.parts and relative.parts[0] == "previous":
            continue
        key = relative.as_posix()
        if path.is_dir():
            snapshot[key] = ("directory", "")
        elif path.is_file() and not path.is_symlink():
            snapshot[key] = ("file", _sha256(path))
        else:
            snapshot[key] = ("invalid", "")
    return snapshot


def _directory_snapshot(root: Path, label: str) -> _DirectorySnapshot:
    """Capture one stable directory identity and all descendant bytes."""
    _reject_symlink_components(root, label)
    try:
        before = root.stat(follow_symlinks=False)
    except OSError as error:
        raise ValueError(f"{label} is unavailable") from error
    if not root.is_dir() or root.is_symlink():
        raise ValueError(f"{label} must be a non-symlink directory")
    tree = _tree_snapshot(root)
    try:
        after = root.stat(follow_symlinks=False)
    except OSError as error:
        raise ValueError(f"{label} changed while it was inspected") from error
    stable_fields = ("st_dev", "st_ino", "st_mtime_ns", "st_ctime_ns")
    if any(getattr(before, field) != getattr(after, field) for field in stable_fields):
        raise ValueError(f"{label} changed while it was inspected")
    return _DirectorySnapshot(before.st_dev, before.st_ino, tree)


def _require_snapshot(
    root: Path, expected: _DirectorySnapshot, label: str
) -> _DirectorySnapshot:
    actual = _directory_snapshot(root, label)
    if actual != expected:
        raise ValueError(f"{label} changed after validation")
    return actual


def _same_edition(stage: Path, destination: Path, root_files: tuple[str, ...]) -> bool:
    if any(
        _sha256(stage / name) != _sha256(destination / name) for name in root_files
    ):
        return False
    return _tree_snapshot(
        stage / "_production", omit_previous=True
    ) == _tree_snapshot(destination / "_production", omit_previous=True)


def _dry_run_matches(
    request: DeliveryRequest, root_hashes: dict[str, str], root_files: tuple[str, ...]
) -> bool:
    destination = Path(request.destination)
    if not destination.exists():
        return False
    if any(_sha256(destination / name) != root_hashes[name] for name in root_files):
        return False

    source_production = Path(request.production)
    destination_production = destination / "_production"
    for name in PRODUCTION_DIRECTORIES:
        if name == "previous":
            continue
        source_snapshot = _tree_snapshot(source_production / name)
        destination_snapshot = _tree_snapshot(destination_production / name)
        if name == "checks":
            source_snapshot.pop("delivery-manifest.json", None)
            destination_manifest = destination_production / "checks/delivery-manifest.json"
            destination_snapshot.pop("delivery-manifest.json", None)
            if (
                not destination_manifest.is_file()
                or destination_manifest.is_symlink()
                or destination_manifest.read_bytes()
                != _json_bytes(_manifest(request, root_hashes))
            ):
                return False
        if source_snapshot != destination_snapshot:
            return False
    return True


def _rename_with_kernel_guarantee(
    source: Path, destination: Path, *, exchange: bool
) -> None:
    """Atomically exchange paths or rename without replacing an existing path."""
    library = ctypes.CDLL(None, use_errno=True)
    source_bytes = os.fsencode(source)
    destination_bytes = os.fsencode(destination)
    if sys.platform == "darwin":
        rename = library.renamex_np
        rename.argtypes = (ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint)
        rename.restype = ctypes.c_int
        flags = 0x00000002 if exchange else 0x00000004
        result = rename(source_bytes, destination_bytes, flags)
    elif sys.platform.startswith("linux") and hasattr(library, "renameat2"):
        rename = library.renameat2
        rename.argtypes = (
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        )
        rename.restype = ctypes.c_int
        flags = 0x00000002 if exchange else 0x00000001
        result = rename(-100, source_bytes, -100, destination_bytes, flags)
    else:
        raise OSError(
            errno.ENOTSUP,
            "atomic no-replace directory promotion is unavailable",
            str(destination),
        )
    if result != 0:
        error_number = ctypes.get_errno()
        raise OSError(error_number, os.strerror(error_number), str(destination))


def _rename_exclusive(source: Path, destination: Path) -> None:
    _rename_with_kernel_guarantee(source, destination, exchange=False)


def _rename_exchange(source: Path, destination: Path) -> None:
    _rename_with_kernel_guarantee(source, destination, exchange=True)


def _rename_stage(stage: Path, destination: Path) -> None:
    try:
        _rename_exclusive(stage, destination)
    except FileExistsError as error:
        raise ValueError("destination appeared before exclusive promotion") from error


def _promote(
    stage: Path,
    destination: Path,
    expected_destination: _DirectorySnapshot | None,
) -> None:
    expected_stage = _directory_snapshot(stage, "staged delivery")
    if expected_destination is None:
        if destination.exists() or destination.is_symlink():
            raise ValueError("destination appeared after validation")
        _rename_stage(stage, destination)
        _require_snapshot(destination, expected_stage, "promoted delivery")
        return

    _require_snapshot(destination, expected_destination, "destination")
    _rename_exchange(stage, destination)
    prior = destination / "_production/previous"
    prior_moved = False
    try:
        _require_snapshot(destination, expected_stage, "promoted delivery")
        _require_snapshot(stage, expected_destination, "exchanged prior destination")
        prior.rmdir()
        try:
            _rename_exclusive(stage, prior)
        except FileExistsError as error:
            raise ValueError("production previous changed during promotion") from error
        prior_moved = True
        _require_snapshot(prior, expected_destination, "archived prior destination")
    except BaseException:
        if prior_moved and prior.exists():
            if stage.exists() or stage.is_symlink():
                raise ValueError(
                    "staging path appeared during rollback; prior edition remains preserved"
                )
            _rename_exclusive(prior, stage)
            prior.mkdir()
        if stage.exists() and destination.exists():
            _rename_exchange(stage, destination)
        raise


def stage_delivery(request: DeliveryRequest, *, apply: bool = False) -> DeliveryResult:
    """Validate, stage, and optionally atomically promote one generated edition."""
    if not isinstance(request, DeliveryRequest):
        raise TypeError("request must be a DeliveryRequest")
    artifacts, root_hashes = _validate_source(request)
    root_files = tuple(sorted(artifacts))
    destination = Path(request.destination)

    if not apply:
        _validate_destination(request)
        decision = (
            "reuse"
            if _dry_run_matches(request, root_hashes, root_files)
            else "promote"
        )
        return DeliveryResult(
            decision=decision,
            destination=str(destination),
            staging_directory=None,
            applied=False,
            root_files=root_files,
        )

    stage: Path | None = None
    verified = False
    try:
        stage = _build_stage(request, artifacts, root_hashes)
        verified = True
        _validate_destination(request)
        expected_destination = (
            _directory_snapshot(destination, "destination")
            if destination.exists()
            else None
        )
        if destination.exists() and _same_edition(stage, destination, root_files):
            assert expected_destination is not None
            _require_snapshot(destination, expected_destination, "destination")
            shutil.rmtree(stage)
            return DeliveryResult(
                decision="reuse",
                destination=str(destination),
                staging_directory=None,
                applied=True,
                root_files=root_files,
            )
        staging_directory = str(stage)
        _promote(stage, destination, expected_destination)
        return DeliveryResult(
            decision="promoted",
            destination=str(destination),
            staging_directory=staging_directory,
            applied=True,
            root_files=root_files,
        )
    except BaseException:
        if stage is not None and not verified and stage.exists():
            shutil.rmtree(stage)
        raise


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--edition-id", required=True)
    parser.add_argument("--m4b", required=True, type=Path)
    parser.add_argument("--epub", required=True, type=Path)
    parser.add_argument("--alignment", required=True, type=Path)
    parser.add_argument("--cover", required=True, type=Path)
    parser.add_argument("--production", required=True, type=Path)
    parser.add_argument("--destination", required=True, type=Path)
    parser.add_argument("--apply", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    request = DeliveryRequest(
        slug=arguments.slug,
        edition_id=arguments.edition_id,
        m4b=arguments.m4b,
        epub=arguments.epub,
        alignment=arguments.alignment,
        cover=arguments.cover,
        production=arguments.production,
        destination=arguments.destination,
    )
    result = stage_delivery(request, apply=arguments.apply)
    print(json.dumps(asdict(result), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
