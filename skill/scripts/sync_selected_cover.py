#!/usr/bin/env python3
"""Safely propagate one explicitly selected cover through a delivery package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from cover_receipts import SelectionReceipt, load_selection, verify_package


@dataclass(frozen=True)
class SyncResult:
    decision: str
    destination: str
    applied: bool
    files: tuple[str, ...]


@dataclass(frozen=True)
class _Snapshot:
    kind: str
    value: Path | str | None = None


def classify_destination(
    source: SelectionReceipt,
    destination: SelectionReceipt | None,
    intent: str,
    destination_has_artifacts: bool = False,
) -> str:
    if intent not in {"reuse", "supersede"}:
        raise ValueError("intent must be reuse or supersede")
    if destination is None:
        if destination_has_artifacts and intent != "supersede":
            raise ValueError(
                "cover receipt conflict: destination has unreceipted cover artifacts"
            )
        if destination_has_artifacts:
            return "supersede-unreceipted"
        return "new"
    if asdict(source) == asdict(destination):
        return "reuse"
    if (
        source.book_slug != destination.book_slug
        or source.edition_id != destination.edition_id
    ):
        raise ValueError("cover receipt conflict: book or edition differs")
    if intent != "supersede":
        raise ValueError("cover receipt conflict: explicit supersede intent required")
    if source.selection_source not in {"explicit-user-choice", "requested-mix"}:
        raise ValueError("cover receipt conflict: source selection is not explicit")
    if datetime.fromisoformat(source.selected_at) <= datetime.fromisoformat(
        destination.selected_at
    ):
        raise ValueError("cover receipt conflict: source selection is not newer")
    return "supersede"


def require_public_permission(selection: SelectionReceipt) -> None:
    if selection.privacy != {
        "classification": "public-safe",
        "permission_to_publish": "granted",
    }:
        raise ValueError(
            "public destination requires public-safe and permissioned selection"
        )


def _lexists(path: Path) -> bool:
    return os.path.lexists(path)


def _resolved(path: Path, label: str) -> Path:
    try:
        return path.resolve(strict=False)
    except (OSError, RuntimeError, ValueError) as error:
        raise ValueError(f"invalid {label} path: {path}") from error


def _aliases(first: Path, second: Path) -> bool:
    if _resolved(first, "artifact") == _resolved(second, "artifact"):
        return True
    try:
        return first.exists() and second.exists() and os.path.samefile(first, second)
    except OSError as error:
        raise ValueError("invalid artifact path") from error


def _reject_aliases(
    labelled_paths: list[tuple[str, Path]],
    message: str,
) -> None:
    for index, (first_label, first) in enumerate(labelled_paths):
        for second_label, second in labelled_paths[index + 1 :]:
            if _aliases(first, second):
                raise ValueError(f"{message}: {first_label} and {second_label}")


def _validate_paths(
    sources: dict[str, Path],
    destination: Path,
    checksum_path: Path | None,
) -> tuple[tuple[str, ...], dict[str, Path]]:
    names = tuple(sources)
    if len(names) != len(set(names)):
        raise ValueError("artifact names collide")

    targets = {name: destination / name for name in names}
    labelled_targets = list(targets.items())
    if checksum_path is not None:
        if checksum_path.name in targets:
            raise ValueError("artifact names collide with checksum manifest")
        labelled_targets.append(("checksum manifest", checksum_path))
    _reject_aliases(labelled_targets, "artifact targets collide")

    _reject_aliases(list(sources.items()), "source artifacts alias")
    for source_label, source in sources.items():
        for target_label, target in labelled_targets:
            if _aliases(source, target):
                raise ValueError(
                    "source artifact aliases destination target: "
                    f"{source_label} and {target_label}"
                )

    if checksum_path is not None:
        if _resolved(checksum_path.parent, "checksum manifest parent") != _resolved(
            destination, "destination"
        ):
            raise ValueError("checksum manifest must be inside the destination")
        if not _lexists(checksum_path) or not checksum_path.is_file():
            raise ValueError("checksum manifest must be an existing file")

    for label, target in labelled_targets:
        if _lexists(target) and not target.is_symlink():
            try:
                mode = target.stat(follow_symlinks=False).st_mode
            except OSError as error:
                raise ValueError(f"destination {label} could not be inspected") from error
            if not stat.S_ISREG(mode):
                raise ValueError(f"destination {label} must be a file or symlink")

    return names, targets


_CHECKSUM_ROW = re.compile(
    r"^(?P<digest>[0-9a-fA-F]{64})(?P<rest>[ \t]+\*?(?P<name>[^\r\n]+))"
    r"(?P<ending>\r?\n)?$"
)


def _checksum_payload(path: Path, replacements: dict[str, Path]) -> bytes:
    try:
        original = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise ValueError(f"checksum manifest could not be read: {path}") from error

    digests: dict[str, str] = {}
    for name, source in replacements.items():
        try:
            digests[name] = hashlib.sha256(source.read_bytes()).hexdigest()
        except OSError as error:
            raise ValueError(f"artifact could not be checksummed: {source}") from error

    seen: set[str] = set()
    updated: list[str] = []
    for line in original.splitlines(keepends=True):
        match = _CHECKSUM_ROW.fullmatch(line)
        if match is None or match.group("name") not in digests:
            updated.append(line)
            continue
        name = match.group("name")
        updated.append(digests[name] + match.group("rest") + (match.group("ending") or ""))
        seen.add(name)

    missing = [name for name in replacements if name not in seen]
    if missing:
        if updated and not updated[-1].endswith(("\n", "\r")):
            updated[-1] += "\n"
        updated.extend(f"{digests[name]}  {name}\n" for name in missing)
    return "".join(updated).encode("utf-8")


def _incoming_path(target: Path) -> Path:
    descriptor, raw_path = tempfile.mkstemp(
        prefix=f".{target.name}.",
        suffix=".incoming",
        dir=target.parent,
    )
    os.close(descriptor)
    return Path(raw_path)


def _publish_copy(source: Path, target: Path) -> None:
    incoming = _incoming_path(target)
    try:
        shutil.copy2(source, incoming)
        os.replace(incoming, target)
    finally:
        incoming.unlink(missing_ok=True)


def _publish_bytes(payload: bytes, target: Path) -> None:
    incoming = _incoming_path(target)
    try:
        with incoming.open("wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(incoming, target)
    finally:
        incoming.unlink(missing_ok=True)


def _snapshot(target: Path, backup_dir: Path, index: int) -> _Snapshot:
    if target.is_symlink():
        return _Snapshot("symlink", os.readlink(target))
    if not target.exists():
        return _Snapshot("absent")
    backup = backup_dir / f"backup-{index}"
    shutil.copy2(target, backup)
    return _Snapshot("file", backup)


def _remove_file_or_symlink(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink(missing_ok=True)
    elif path.exists():
        raise OSError(f"cannot replace non-file destination during rollback: {path}")


def _restore(target: Path, snapshot: _Snapshot) -> None:
    if snapshot.kind == "absent":
        _remove_file_or_symlink(target)
        return
    if snapshot.kind == "symlink":
        _remove_file_or_symlink(target)
        os.symlink(snapshot.value, target)
        return
    if snapshot.kind == "file":
        backup = snapshot.value
        if not isinstance(backup, Path):
            raise RuntimeError("invalid file snapshot")
        os.replace(backup, target)
        return
    raise RuntimeError(f"unknown snapshot kind: {snapshot.kind}")


def _rollback(
    attempted: list[Path],
    snapshots: dict[Path, _Snapshot],
) -> list[str]:
    errors: list[str] = []
    restored: set[Path] = set()
    for target in reversed(attempted):
        if target in restored:
            continue
        restored.add(target)
        try:
            _restore(target, snapshots[target])
        except Exception as error:  # Continue so later artifacts still restore.
            errors.append(f"{target}: {error}")
    return errors


def sync_selected_cover(
    selection_path: Path,
    cover_path: Path,
    epub_path: Path,
    m4b_path: Path,
    destination: Path,
    *,
    intent: str,
    apply: bool,
    checksum_manifest: Path | None = None,
    public_destination: bool = False,
    fail_after: int | None = None,
) -> SyncResult:
    selection_path = Path(selection_path)
    cover_path = Path(cover_path)
    epub_path = Path(epub_path)
    m4b_path = Path(m4b_path)
    destination = Path(destination)
    checksum_path = Path(checksum_manifest) if checksum_manifest is not None else None
    if fail_after is not None and fail_after < 1:
        raise ValueError("fail_after must be positive")

    artifact_names = (
        "cover.png",
        epub_path.name,
        m4b_path.name,
        "cover-selection.json",
    )
    if len(artifact_names) != len(set(artifact_names)):
        raise ValueError("artifact names collide")
    sources = {
        "cover.png": cover_path,
        epub_path.name: epub_path,
        m4b_path.name: m4b_path,
        "cover-selection.json": selection_path,
    }
    files, targets = _validate_paths(sources, destination, checksum_path)

    source = load_selection(selection_path)
    verify_package(
        selection_path,
        cover_path,
        epub_path=epub_path,
        m4b_path=m4b_path,
        receipt_path=selection_path,
    )
    if public_destination:
        require_public_permission(source)

    destination_receipt_path = targets["cover-selection.json"]
    destination_receipt = (
        load_selection(destination_receipt_path)
        if _lexists(destination_receipt_path)
        else None
    )
    destination_has_artifacts = any(_lexists(targets[name]) for name in files[:-1])
    decision = classify_destination(
        source,
        destination_receipt,
        intent,
        destination_has_artifacts,
    )
    checksum_bytes = (
        _checksum_payload(checksum_path, sources)
        if checksum_path is not None
        else None
    )
    if not apply:
        return SyncResult(decision, str(destination), False, files)

    if _lexists(destination) and not destination.is_dir():
        raise ValueError("destination must be a directory")
    destination_existed = destination.is_dir()
    destination.mkdir(parents=True, exist_ok=True)

    apply_error: Exception | None = None
    rollback_errors: list[str] = []
    try:
        with tempfile.TemporaryDirectory(
            prefix=".cover-sync-backup-", dir=destination
        ) as raw_backup:
            backup_dir = Path(raw_backup)
            ordered_targets = [targets[name] for name in files]
            if checksum_path is not None:
                ordered_targets.append(checksum_path)
            snapshots = {
                target: _snapshot(target, backup_dir, index)
                for index, target in enumerate(ordered_targets)
            }
            attempted: list[Path] = []
            try:
                for name in files:
                    target = targets[name]
                    attempted.append(target)
                    _publish_copy(sources[name], target)
                    if fail_after is not None and len(attempted) == fail_after:
                        raise RuntimeError("injected sync failure")
                if checksum_path is not None:
                    if checksum_bytes is None:
                        raise RuntimeError("missing checksum update payload")
                    attempted.append(checksum_path)
                    _publish_bytes(checksum_bytes, checksum_path)
                verify_package(
                    destination_receipt_path,
                    targets["cover.png"],
                    epub_path=targets[epub_path.name],
                    m4b_path=targets[m4b_path.name],
                    receipt_path=destination_receipt_path,
                )
            except Exception as error:
                apply_error = error
                rollback_errors = _rollback(attempted, snapshots)
    except Exception as error:
        if apply_error is None:
            apply_error = error

    if apply_error is not None:
        if not destination_existed:
            try:
                destination.rmdir()
            except OSError as error:
                rollback_errors.append(f"{destination}: {error}")
        if rollback_errors:
            raise RuntimeError(
                "selected cover sync failed and rollback failed: "
                + "; ".join(rollback_errors)
            ) from apply_error
        raise apply_error

    return SyncResult(decision, str(destination), True, files)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", required=True, type=Path)
    parser.add_argument("--cover", required=True, type=Path)
    parser.add_argument("--epub", required=True, type=Path)
    parser.add_argument("--m4b", required=True, type=Path)
    parser.add_argument("--destination", required=True, type=Path)
    parser.add_argument("--intent", required=True, choices=("reuse", "supersede"))
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--checksum-manifest", type=Path)
    parser.add_argument("--public-destination", action="store_true")
    arguments = parser.parse_args()
    result = sync_selected_cover(
        arguments.selection,
        arguments.cover,
        arguments.epub,
        arguments.m4b,
        arguments.destination,
        intent=arguments.intent,
        apply=arguments.apply,
        checksum_manifest=arguments.checksum_manifest,
        public_destination=arguments.public_destination,
    )
    print(json.dumps(asdict(result), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
