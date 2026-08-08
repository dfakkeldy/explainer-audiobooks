#!/usr/bin/env python3
"""Verify a sanitized, explicitly authorized public audiobook package."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import posixpath
import re
import stat
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

FICTION_VOICE_DIRECTORY = (
    Path(__file__).resolve().parents[2] / "skills" / "fiction-audiobook" / "scripts"
)
if str(FICTION_VOICE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(FICTION_VOICE_DIRECTORY))

from fiction_voice_preferences import (
    validate_completed_cast,
    validate_echo_success_receipt,
)

try:
    from .fiction_production_qc import verify_fiction_receipt
except ImportError:
    from fiction_production_qc import verify_fiction_receipt


DISCLOSURE = (
    "This edition has passed package and audio checks. The creator's full "
    "listening review is still underway."
)
GOVERNED_FINAL_DISCLOSURE = (
    "This edition has passed package and audio checks. The creator completed "
    "the full listening review and approved this edition for publication."
)
FICTION_DISCLOSURE = (
    "This original AI-generated fiction edition is published under CC BY 4.0 "
    "as a public first-listen. Automated package and audio checks passed; human "
    "reading and listening reviews remain pending."
)
_PUBLICATION_DISCLOSURES = {
    ("public-first-listen", "pending"): DISCLOSURE,
    ("governed-final", "accepted"): GOVERNED_FINAL_DISCLOSURE,
}

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_WINDOWS_ABSOLUTE = re.compile(r"^[A-Za-z]:[\\/]")
_FORBIDDEN_PATTERNS = (
    re.compile(r"^echo-render-", re.IGNORECASE),
    re.compile(r"pronunciation-audit", re.IGNORECASE),
    re.compile(r"pronunciation-reel", re.IGNORECASE),
    re.compile(r"resume-state", re.IGNORECASE),
)
_CANONICAL_ARTIFACTS = {
    "manuscript": lambda slug: f"{slug}.md",
    "epub": lambda slug: f"{slug}.epub",
    "m4b": lambda slug: f"{slug}.m4b",
    "alignment": lambda slug: f"{slug}.alignment.json",
    "portraitCover": lambda slug: "cover.png",
    "squareCover": lambda slug: "m4b-cover.png",
}
_FICTION_ARTIFACTS = {
    "manuscript": lambda slug: f"{slug}.md",
    "epub": lambda slug: f"{slug}.epub",
    "alignment": lambda slug: f"{slug}.alignment.json",
    "portraitCover": lambda slug: "cover.png",
}
_FICTION_PUBLIC_GATE_FIELDS = {
    "originalFiction",
    "noPrivateSource",
    "noLivingPersonTarget",
    "noLivingAuthorImitation",
    "coverRightsVerified",
}
_FICTION_RECEIPT_FIELDS = {
    "schemaVersion",
    "packageKind",
    "slug",
    "editionId",
    "publicationStatus",
    "humanReadingStatus",
    "humanListeningStatus",
    "classification",
    "permissionToPublish",
    "permissionGrantedAt",
    "author",
    "contributor",
    "aiGenerated",
    "contentLicense",
    "disclosure",
    "publicGate",
    "coverRights",
    "artifacts",
    "release",
    "privateEvidence",
}
_COVER_RIGHTS_BASES = {
    "original",
    "generated",
    "public-domain",
    "permissively-licensed",
    "explicit-permission",
}
_PROVENANCE_REQUIRED_BASES = {"permissively-licensed", "explicit-permission"}
_PRIVATE_EVIDENCE_FIELDS = {
    "fictionReceiptSHA256",
    "voiceCastSHA256",
    "voicePlanSHA256",
    "echoSuccessReceiptSHA256",
}
_CAST_VERIFIED_ARTIFACT_FIELDS = {
    "sourceEPUBSHA256",
    "audiobookSHA256",
    "sidecarSHA256",
    "voicePlanSHA256",
}
@dataclass(frozen=True)
class _FileSnapshot:
    path: Path
    device: int
    inode: int
    size: int
    mtime_ns: int
    sha256: str
    content: bytes | None = None


def _unique_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def _reject_nonfinite_json_number(value: str) -> None:
    raise ValueError(f"non-finite JSON number: {value}")


def _read_json(path: Path, label: str) -> object:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_unique_json_object,
            parse_constant=_reject_nonfinite_json_number,
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"{label} is not readable JSON") from error


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as error:
        raise ValueError(f"artifact is not readable: {path.name}") from error
    return digest.hexdigest()


def _snapshot_file(
    path: Path,
    label: str,
    *,
    capture: bool = False,
    copy_to: Path | None = None,
) -> _FileSnapshot:
    _reject_symlink_ancestors(path, label)
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise ValueError(f"{label} is not a readable regular file") from error
    chunks: list[bytes] | None = [] if capture else None
    digest = hashlib.sha256()
    copy_stream = None
    try:
        if copy_to is not None:
            copy_stream = copy_to.open("xb")
        before = os.fstat(descriptor)
        _require(stat.S_ISREG(before.st_mode), f"{label} must be a regular file")
        with os.fdopen(descriptor, "rb") as stream:
            descriptor = -1
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
                if chunks is not None:
                    chunks.append(chunk)
                if copy_stream is not None:
                    copy_stream.write(chunk)
            after = os.fstat(stream.fileno())
        if copy_stream is not None:
            copy_stream.flush()
            os.fsync(copy_stream.fileno())
            copy_stream.close()
            copy_stream = None
            os.chmod(copy_to, 0o400)
        current = os.lstat(path)
    except OSError as error:
        raise ValueError(f"{label} changed during verification") from error
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if copy_stream is not None:
            copy_stream.close()
    identity_before = (
        before.st_dev,
        before.st_ino,
        before.st_size,
        before.st_mtime_ns,
    )
    identity_after = (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
    )
    identity_current = (
        current.st_dev,
        current.st_ino,
        current.st_size,
        current.st_mtime_ns,
    )
    _require(
        identity_before == identity_after == identity_current
        and stat.S_ISREG(current.st_mode),
        f"{label} changed during verification",
    )
    return _FileSnapshot(
        path=path,
        device=before.st_dev,
        inode=before.st_ino,
        size=before.st_size,
        mtime_ns=before.st_mtime_ns,
        sha256=digest.hexdigest(),
        content=b"".join(chunks) if chunks is not None else None,
    )


def _require_snapshot_unchanged(snapshot: _FileSnapshot, label: str) -> None:
    current = _snapshot_file(snapshot.path, label)
    _require(
        (
            current.device,
            current.inode,
            current.size,
            current.mtime_ns,
            current.sha256,
        )
        == (
            snapshot.device,
            snapshot.inode,
            snapshot.size,
            snapshot.mtime_ns,
            snapshot.sha256,
        ),
        f"{label} changed during verification",
    )


def _json_from_snapshot(snapshot: _FileSnapshot, label: str) -> object:
    assert snapshot.content is not None
    try:
        return json.loads(
            snapshot.content.decode("utf-8"),
            object_pairs_hook=_unique_json_object,
            parse_constant=_reject_nonfinite_json_number,
        )
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"{label} is not readable JSON") from error


def _read_json_snapshot(path: Path, label: str) -> tuple[object, _FileSnapshot]:
    snapshot = _snapshot_file(path, label, capture=True)
    return _json_from_snapshot(snapshot, label), snapshot


def reject_private_values(value: object, location: str = "publication.json") -> None:
    """Reject absolute local references recursively from public JSON values."""
    if isinstance(value, str):
        if (
            value.startswith("/")
            or value.startswith("\\\\")
            or value.casefold().startswith("file://")
            or _WINDOWS_ABSOLUTE.match(value)
        ):
            raise ValueError(f"absolute path in {location}: {value}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            reject_private_values(item, f"{location}[{index}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            reject_private_values(key, f"{location} key")
            reject_private_values(item, f"{location}.{key}")


def load_receipt(book_dir: Path) -> dict[str, object]:
    receipt = _read_json(book_dir / "publication.json", "publication.json")
    if not isinstance(receipt, dict):
        raise ValueError("publication.json must be an object")
    reject_private_values(receipt)
    return receipt


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _require_contained_path(book_dir: Path, path: Path, label: str) -> None:
    _require(not path.is_symlink(), f"{label} must not be a symlink")
    try:
        path.resolve().relative_to(book_dir.resolve())
    except ValueError as error:
        raise ValueError(f"{label} escapes the book directory") from error


def _reject_symlinks(book_dir: Path) -> None:
    _require(not book_dir.is_symlink(), "book directory must not be a symlink")
    for path in book_dir.rglob("*"):
        _require(not path.is_symlink(), f"package must not contain symlink: {path.relative_to(book_dir)}")
        _require_contained_path(book_dir, path, f"package path {path.relative_to(book_dir)}")


def _verify_receipt_fields(receipt: dict[str, object]) -> str:
    _require(receipt.get("schemaVersion") == 1, "schemaVersion must be 1")
    slug = receipt.get("slug")
    _require(isinstance(slug, str) and _SLUG.fullmatch(slug) is not None, "slug is invalid")
    publication_state = (
        receipt.get("publicationStatus"),
        receipt.get("humanListeningStatus"),
    )
    _require(
        publication_state in _PUBLICATION_DISCLOSURES,
        "publicationStatus and humanListeningStatus must form an approved state",
    )
    _require(receipt.get("classification") == "public-safe", "classification must be public-safe")
    _require(receipt.get("permissionToPublish") is True, "permissionToPublish must be true")
    permission_date = receipt.get("permissionGrantedAt")
    _require(isinstance(permission_date, str) and permission_date, "permissionGrantedAt is required")
    _require(
        receipt.get("disclosure") == _PUBLICATION_DISCLOSURES[publication_state],
        "disclosure must match the approved text",
    )
    _require(isinstance(receipt.get("sourceArtIncluded"), bool), "sourceArtIncluded must be boolean")
    return slug


def verify_artifacts(book_dir: Path, receipt: dict[str, object]) -> None:
    """Require the canonical six artifacts and verify their streaming hashes."""
    slug = _verify_receipt_fields(receipt)
    artifacts = receipt.get("artifacts")
    _require(isinstance(artifacts, dict), "artifacts must be an object")
    _require(set(artifacts) == set(_CANONICAL_ARTIFACTS), "artifacts must contain exactly the six canonical artifacts")
    for name, filename_for_slug in _CANONICAL_ARTIFACTS.items():
        row = artifacts[name]
        _require(isinstance(row, dict), f"{name} artifact must be an object")
        expected_name = filename_for_slug(slug)
        _require(row.get("file") == expected_name, f"{name} filename must be {expected_name}")
        expected_hash = row.get("sha256")
        _require(isinstance(expected_hash, str) and _SHA256.fullmatch(expected_hash) is not None, f"{name} SHA-256 is invalid")
        path = book_dir / expected_name
        _require_contained_path(book_dir, path, f"{name} artifact")
        _require(path.is_file(), f"{name} artifact is missing: {expected_name}")
        _require(_sha256_file(path) == expected_hash, f"{name} SHA-256 does not match")


def _verify_media_and_alignment(book_dir: Path, slug: str) -> None:
    epub = book_dir / f"{slug}.epub"
    m4b = book_dir / f"{slug}.m4b"
    try:
        subprocess.run(["unzip", "-t", str(epub)], check=True, capture_output=True, text=True)
    except (OSError, subprocess.CalledProcessError) as error:
        raise ValueError("EPUB failed unzip -t") from error
    try:
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration:chapter=start_time,end_time", "-of", "json", str(m4b)],
            check=True,
            capture_output=True,
            text=True,
        )
        media = json.loads(probe.stdout)
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        raise ValueError("M4B failed ffprobe") from error
    try:
        _require(float(media["format"]["duration"]) > 0, "M4B duration must be positive")
        _require(isinstance(media["chapters"], list) and media["chapters"], "M4B chapters are required")
    except (KeyError, TypeError, ValueError) as error:
        if isinstance(error, ValueError) and str(error).startswith("M4B"):
            raise
        raise ValueError("M4B ffprobe output lacks duration or chapters") from error
    alignment = _read_json(book_dir / f"{slug}.alignment.json", "alignment")
    _require(isinstance(alignment, list) and alignment, "alignment must be a non-empty JSON array")


def _verify_source_art(book_dir: Path, receipt: dict[str, object]) -> None:
    render_path = book_dir / "cover-render.json"
    render = _read_json(render_path, "cover-render.json")
    _require(isinstance(render, dict), "cover-render.json must be an object")
    reject_private_values(render, "cover-render.json")
    source_art = render.get("source_art")
    _require(isinstance(source_art, str) and Path(source_art).name == source_art, "cover-render.json source art is invalid")
    declared_art = book_dir / source_art
    _require_contained_path(book_dir, declared_art, "declared source art")
    source_candidates = [
        path for path in book_dir.rglob("*")
        if path.is_file() and ("source-art" in path.name.lower() or "cover-source" in path.name.lower())
    ]
    if receipt["sourceArtIncluded"]:
        _require(declared_art.is_file(), "declared source art is missing")
    else:
        _require(not declared_art.exists() and not source_candidates, "source art is present despite sourceArtIncluded false")


def _verify_public_surface(
    book_dir: Path, receipt: dict[str, object]
) -> None:
    readme = book_dir / "README.md"
    try:
        readme_text = readme.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise ValueError("README is missing or unreadable") from error
    disclosure = receipt["disclosure"]
    assert isinstance(disclosure, str)
    _require(
        disclosure in readme_text,
        "README must include the approved disclosure",
    )
    for path in book_dir.rglob("*"):
        relative = path.relative_to(book_dir)
        parts = relative.parts
        _require("research" not in {part.lower() for part in parts}, f"forbidden internal file: {relative}")
        if path.is_file() and any(pattern.search(path.name) for pattern in _FORBIDDEN_PATTERNS):
            raise ValueError(f"forbidden internal file: {relative}")


def verify_public_package(book_dir: Path) -> None:
    book_dir = Path(book_dir)
    _require(book_dir.is_dir(), "book directory does not exist")
    _reject_symlinks(book_dir)
    receipt = load_receipt(book_dir)
    verify_artifacts(book_dir, receipt)
    slug = receipt["slug"]
    assert isinstance(slug, str)
    _verify_media_and_alignment(book_dir, slug)
    _verify_source_art(book_dir, receipt)
    _verify_public_surface(book_dir, receipt)


def _require_sha256(value: object, label: str) -> str:
    _require(
        isinstance(value, str) and _SHA256.fullmatch(value) is not None,
        f"{label} must be a lowercase SHA-256",
    )
    return value


def _require_regular_file(path: Path, label: str) -> None:
    _reject_symlink_ancestors(path, label)
    _require(path.is_file(), f"{label} must be a regular file")


def _require_regular_directory(path: Path, label: str) -> None:
    _reject_symlink_ancestors(path, label)
    _require(path.is_dir(), f"{label} must be a directory")
    for child in path.rglob("*"):
        _require(not child.is_symlink(), f"{label} must not contain a symlink: {child}")


def _reject_symlink_ancestors(path: Path, label: str) -> None:
    current = path
    while True:
        _require(
            not current.is_symlink(),
            f"{label} must not use a symlink ancestor: {current}",
        )
        parent = current.parent
        if parent == current:
            return
        current = parent


def _verify_fiction_public_root(book_dir: Path, slug: str) -> None:
    expected = {
        "README.md",
        "publication.json",
        *(filename(slug) for filename in _FICTION_ARTIFACTS.values()),
    }
    try:
        entries = list(book_dir.iterdir())
    except OSError as error:
        raise ValueError("fiction book directory is unreadable") from error
    actual = {path.name for path in entries}
    _require(
        actual == expected and len(entries) == len(expected),
        "fiction public root must contain exactly the six canonical files",
    )
    for path in entries:
        _require_regular_file(path, f"fiction public root item {path.name}")


def _verify_fiction_receipt_fields(receipt: dict[str, object]) -> str:
    _require(
        set(receipt) == _FICTION_RECEIPT_FIELDS,
        "fiction publication receipt must contain exactly the schema-v2 fields",
    )
    _require(
        type(receipt.get("schemaVersion")) is int
        and receipt["schemaVersion"] == 2,
        "fiction schemaVersion must be 2",
    )
    _require(
        receipt.get("packageKind") == "fiction-audiobook",
        "packageKind must be fiction-audiobook",
    )
    slug = receipt.get("slug")
    _require(
        isinstance(slug, str) and _SLUG.fullmatch(slug) is not None,
        "fiction slug is invalid",
    )
    edition_id = receipt.get("editionId")
    _require(
        isinstance(edition_id, str) and bool(edition_id.strip()),
        "editionId is required",
    )
    _require(
        receipt.get("publicationStatus") == "public-first-listen",
        "fiction publicationStatus must be public-first-listen",
    )
    for field in ("humanReadingStatus", "humanListeningStatus"):
        _require(receipt.get(field) == "pending", f"{field} must be pending")
    _require(
        receipt.get("classification") == "public-safe",
        "classification must be public-safe",
    )
    _require(
        receipt.get("permissionToPublish") is True,
        "permissionToPublish must be true",
    )
    permission_date = receipt.get("permissionGrantedAt")
    _require(
        isinstance(permission_date, str) and bool(permission_date.strip()),
        "permissionGrantedAt is required",
    )
    _require(receipt.get("author") == "Dan Fakkeldy", "author must be Dan Fakkeldy")
    contributor = receipt.get("contributor")
    _require(
        isinstance(contributor, str) and bool(contributor.strip()),
        "contributor must be non-empty text",
    )
    _require(receipt.get("aiGenerated") is True, "aiGenerated must be true")
    _require(
        receipt.get("contentLicense") == "CC-BY-4.0",
        "contentLicense must be CC-BY-4.0",
    )
    _require(
        receipt.get("disclosure") == FICTION_DISCLOSURE,
        "fiction disclosure must match the approved text",
    )

    public_gate = receipt.get("publicGate")
    _require(isinstance(public_gate, dict), "publicGate must be an object")
    _require(
        set(public_gate) == _FICTION_PUBLIC_GATE_FIELDS,
        "publicGate must contain exactly the five required fields",
    )
    for field in sorted(_FICTION_PUBLIC_GATE_FIELDS):
        _require(public_gate.get(field) is True, f"{field} must be true")

    cover_rights = receipt.get("coverRights")
    _require(isinstance(cover_rights, dict), "coverRights must be an object")
    basis = cover_rights.get("basis")
    _require(basis in _COVER_RIGHTS_BASES, "coverRights basis is invalid")
    expected_cover_fields = {"basis", "status", "coverSHA256"}
    if basis in _PROVENANCE_REQUIRED_BASES:
        expected_cover_fields.add("provenanceNote")
    _require(
        set(cover_rights) == expected_cover_fields,
        "coverRights provenance shape must contain exactly the fields required by its basis",
    )
    _require(
        cover_rights.get("status") == "verified",
        "coverRights status must be verified",
    )
    _require_sha256(cover_rights.get("coverSHA256"), "coverRights coverSHA256")
    if basis in _PROVENANCE_REQUIRED_BASES:
        note = cover_rights.get("provenanceNote")
        _require(
            isinstance(note, str) and bool(note.strip()),
            f"coverRights provenance note is required for {basis}",
        )
    return slug


def _verify_fiction_artifacts(
    book_dir: Path,
    receipt: dict[str, object],
    slug: str,
    epub_probe_copy: Path,
) -> tuple[dict[str, str], list[_FileSnapshot]]:
    artifacts = receipt.get("artifacts")
    _require(isinstance(artifacts, dict), "fiction artifacts must be an object")
    _require(
        set(artifacts) == set(_FICTION_ARTIFACTS),
        "fiction artifacts must contain exactly the four canonical artifacts",
    )
    verified: dict[str, str] = {}
    snapshots: list[_FileSnapshot] = []
    for name, filename_for_slug in _FICTION_ARTIFACTS.items():
        record = artifacts[name]
        _require(isinstance(record, dict), f"fiction {name} artifact must be an object")
        _require(
            set(record) == {"file", "sha256"},
            f"fiction {name} artifact must contain exactly file and sha256",
        )
        filename = filename_for_slug(slug)
        _require(
            record.get("file") == filename,
            f"fiction {name} filename must be {filename}",
        )
        expected_hash = _require_sha256(
            record.get("sha256"), f"fiction {name} SHA-256"
        )
        path = book_dir / filename
        _require_regular_file(path, f"fiction {name} artifact")
        snapshot = _snapshot_file(
            path,
            f"fiction {name} artifact",
            capture=name in {"manuscript", "alignment"},
            copy_to=epub_probe_copy if name == "epub" else None,
        )
        if name == "alignment":
            alignment = _json_from_snapshot(snapshot, "fiction alignment")
            reject_private_values(alignment, "fiction alignment")
            _require(
                isinstance(alignment, (list, dict)) and bool(alignment),
                "fiction alignment must be non-empty JSON",
            )
        actual_hash = snapshot.sha256
        _require(
            actual_hash == expected_hash,
            f"fiction {name} SHA-256 does not match",
        )
        verified[name] = actual_hash
        snapshots.append(snapshot)
    return verified, snapshots


def _probe_fiction_media(
    epub: Path,
    release_m4b: Path,
    epub_snapshot: _FileSnapshot,
    release_snapshot: _FileSnapshot,
    epub_probe_snapshot: _FileSnapshot,
    release_probe_snapshot: _FileSnapshot,
) -> None:
    try:
        subprocess.run(
            ["unzip", "-t", str(epub)],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise ValueError("fiction EPUB failed unzip -t") from error
    _require_snapshot_unchanged(epub_probe_snapshot, "immutable fiction EPUB")
    _require_snapshot_unchanged(epub_snapshot, "fiction EPUB")
    try:
        probe = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration:chapter=start_time,end_time",
                "-of",
                "json",
                str(release_m4b),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        media = json.loads(
            probe.stdout,
            object_pairs_hook=_unique_json_object,
            parse_constant=_reject_nonfinite_json_number,
        )
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        raise ValueError("fiction M4B failed ffprobe") from error
    _require_snapshot_unchanged(release_probe_snapshot, "immutable release M4B")
    _require_snapshot_unchanged(release_snapshot, "release M4B")
    _require(
        isinstance(media, dict) and set(media) == {"format", "chapters"},
        "fiction M4B ffprobe output must contain exactly format and chapters",
    )
    media_format = media["format"]
    _require(
        isinstance(media_format, dict) and set(media_format) == {"duration"},
        "fiction M4B ffprobe format must contain exactly duration",
    )
    duration_value = media_format["duration"]
    _require(
        isinstance(duration_value, str),
        "fiction M4B duration must be ffprobe text",
    )
    try:
        duration = float(duration_value)
    except ValueError as error:
        raise ValueError("fiction M4B duration must be numeric ffprobe text") from error
    _require(
        math.isfinite(duration) and duration > 0,
        "fiction M4B duration must be finite and positive",
    )
    chapters = media["chapters"]
    _require(
        isinstance(chapters, list) and bool(chapters),
        "fiction M4B chapters are required",
    )
    for index, chapter in enumerate(chapters):
        _require(
            isinstance(chapter, dict)
            and set(chapter) == {"start_time", "end_time"},
            f"fiction M4B chapter {index} must contain exact ffprobe times",
        )
        start_value = chapter["start_time"]
        end_value = chapter["end_time"]
        _require(
            isinstance(start_value, str) and isinstance(end_value, str),
            f"fiction M4B chapter {index} times must be ffprobe text",
        )
        try:
            start = float(start_value)
            end = float(end_value)
        except ValueError as error:
            raise ValueError(
                f"fiction M4B chapter {index} times must be numeric ffprobe text"
            ) from error
        _require(
            math.isfinite(start)
            and math.isfinite(end)
            and start >= 0
            and end > start,
            f"fiction M4B chapter {index} times must be finite and increasing",
        )


def _verify_release(
    receipt: dict[str, object],
    slug: str,
    release_m4b: Path,
    release_probe_copy: Path,
) -> tuple[str, _FileSnapshot]:
    release = receipt.get("release")
    _require(isinstance(release, dict), "release must be an object")
    _require(
        set(release) == {"tag", "assetFile", "assetSHA256"},
        "release must contain exactly tag, assetFile, and assetSHA256",
    )
    tag = release.get("tag")
    expected_tag = f"fiction-{slug}-{receipt['editionId']}"
    _require(tag == expected_tag, f"release tag must be {expected_tag}")
    expected_filename = f"{slug}.m4b"
    _require(
        release.get("assetFile") == expected_filename,
        f"release asset filename must be {expected_filename}",
    )
    _require(
        release_m4b.name == expected_filename,
        f"release M4B filename must be {expected_filename}",
    )
    expected_hash = _require_sha256(release.get("assetSHA256"), "release asset SHA-256")
    snapshot = _snapshot_file(
        release_m4b, "release M4B", copy_to=release_probe_copy
    )
    actual_hash = snapshot.sha256
    _require(actual_hash == expected_hash, "release M4B SHA-256 does not match")
    return actual_hash, snapshot


def _snapshot_fiction_inputs(
    chapters_dir: Path, fiction: dict[str, object]
) -> list[_FileSnapshot]:
    snapshots: list[_FileSnapshot] = []
    chapter_hashes = fiction.get("canonicalChapterSHA256")
    if isinstance(chapter_hashes, dict):
        for filename in chapter_hashes:
            if isinstance(filename, str) and Path(filename).name == filename:
                snapshots.append(
                    _snapshot_file(
                        chapters_dir / filename,
                        f"canonical fiction chapter {filename}",
                        capture=True,
                    )
                )
    run_root = chapters_dir.parent
    for section in (fiction.get("artifacts"),):
        if not isinstance(section, dict):
            continue
        for record in section.values():
            if not isinstance(record, dict):
                continue
            relative = record.get("path")
            if not isinstance(relative, str):
                continue
            candidate = run_root / relative
            try:
                candidate.resolve().relative_to(run_root.resolve())
            except ValueError:
                continue
            snapshots.append(_snapshot_file(candidate, f"fiction input {relative}"))
    return snapshots


def _verify_private_evidence(
    receipt: dict[str, object],
    slug: str,
    artifact_hashes: dict[str, str],
    release_hash: str,
    voice_cast: Path,
    fiction_receipt: Path,
    chapters_dir: Path,
    echo_success_receipt: Path,
) -> list[_FileSnapshot]:
    snapshots: list[_FileSnapshot] = []
    private = receipt.get("privateEvidence")
    _require(isinstance(private, dict), "privateEvidence must be an object")
    _require(
        set(private) == _PRIVATE_EVIDENCE_FIELDS,
        "privateEvidence must contain exactly the required hashes",
    )
    for field in _PRIVATE_EVIDENCE_FIELDS:
        _require_sha256(private.get(field), f"privateEvidence {field}")

    cast, cast_snapshot = _read_json_snapshot(voice_cast, "voice cast")
    _require(isinstance(cast, dict), "voice cast must be an object")
    _require(
        cast_snapshot.sha256 == private["voiceCastSHA256"],
        "voice cast SHA-256 does not match privateEvidence",
    )
    snapshots.append(cast_snapshot)
    canonical_plan = validate_completed_cast(cast)
    _require(cast.get("slug") == slug, "voice cast slug does not match publication")
    plan_hash = _require_sha256(cast.get("voicePlanSHA256"), "voice cast voicePlanSHA256")
    _require(
        canonical_plan["voicePlanSHA256"] == plan_hash,
        "voice cast voice-plan hash differs from its canonical plan",
    )
    _require(
        plan_hash == private["voicePlanSHA256"],
        "voice-plan hash does not match privateEvidence",
    )
    verified_artifacts = cast.get("verifiedArtifacts")
    _require(
        isinstance(verified_artifacts, dict),
        "voice cast verifiedArtifacts must be completed",
    )
    _require(
        set(verified_artifacts) == _CAST_VERIFIED_ARTIFACT_FIELDS,
        "voice cast verifiedArtifacts must contain exactly the governed hashes",
    )
    expected_verified = {
        "sourceEPUBSHA256": artifact_hashes["epub"],
        "audiobookSHA256": release_hash,
        "sidecarSHA256": artifact_hashes["alignment"],
        "voicePlanSHA256": plan_hash,
    }
    _require(
        verified_artifacts == expected_verified,
        "voice cast verifiedArtifacts differ from public and release artifacts",
    )

    success, success_snapshot = _read_json_snapshot(
        echo_success_receipt, "Echo success receipt"
    )
    _require(isinstance(success, dict), "Echo success receipt must be an object")
    _require(
        success_snapshot.sha256 == private["echoSuccessReceiptSHA256"],
        "Echo success receipt SHA-256 does not match privateEvidence",
    )
    snapshots.append(success_snapshot)
    validate_echo_success_receipt(success, echo_success_receipt, cast)
    expected_success = {
        "sourceEPUBFileName": f"{slug}.epub",
        "sourceEPUBSHA256": artifact_hashes["epub"],
        "audiobookFileName": f"{slug}.m4b",
        "audiobookSHA256": release_hash,
        "sidecarFileName": f"{slug}.alignment.json",
        "sidecarSHA256": artifact_hashes["alignment"],
    }
    for field, expected in expected_success.items():
        _require(
            success.get(field) == expected,
            f"Echo success receipt {field} does not match governed artifacts",
        )

    fiction, fiction_snapshot = _read_json_snapshot(
        fiction_receipt, "fiction production receipt"
    )
    _require(isinstance(fiction, dict), "fiction production receipt must be an object")
    _require(
        fiction_snapshot.sha256 == private["fictionReceiptSHA256"],
        "fiction receipt SHA-256 does not match privateEvidence",
    )
    snapshots.append(fiction_snapshot)
    fiction_inputs = _snapshot_fiction_inputs(chapters_dir, fiction)
    verify_fiction_receipt(chapters_dir, fiction_receipt)
    for snapshot in fiction_inputs:
        _require_snapshot_unchanged(snapshot, "fiction private input")
    snapshots.extend(fiction_inputs)
    return snapshots


def _chapter_markdown(
    content: bytes, filename: str, label: str
) -> tuple[str, tuple[str, ...]]:
    try:
        raw = content.decode("utf-8").strip()
    except UnicodeDecodeError as error:
        raise ValueError(f"{label} is not UTF-8") from error
    lines = raw.split("\n")
    title = Path(filename).stem
    body_start = 0
    for index, line in enumerate(lines):
        if line.strip().startswith("#"):
            title = re.sub(r"^#+\s*", "", line.strip())
            body_start = index + 1
            break
    _require(bool(title), f"{label} title is empty")
    body = "\n".join(lines[body_start:]).strip()
    paragraphs: list[str] = []
    for chunk in re.split(r"\n\s*\n", body):
        paragraph = re.sub(r"\s*\n\s*", " ", chunk.strip())
        if not paragraph:
            continue
        if paragraph.startswith("#"):
            paragraph = re.sub(r"^#+\s*", "", paragraph)
        _require(
            paragraph != "---",
            f"{label} contains an ambiguous story-section delimiter",
        )
        _require(
            re.fullmatch(r"!\[[^]]*\]\([^)]*\)", paragraph) is None,
            f"{label} contains unsupported public fiction image content",
        )
        paragraphs.append(paragraph)
    _require(bool(paragraphs), f"{label} story body is empty")
    return title, tuple(paragraphs)


def _canonical_story(
    chapters_dir: Path, snapshots: list[_FileSnapshot]
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    chapter_snapshots = sorted(
        (
            snapshot
            for snapshot in snapshots
            if snapshot.path.parent == chapters_dir
            and snapshot.path.name.startswith("ch")
            and snapshot.path.suffix == ".md"
        ),
        key=lambda snapshot: snapshot.path.name,
    )
    _require(bool(chapter_snapshots), "canonical fiction chapters are missing")
    story = []
    for snapshot in chapter_snapshots:
        assert snapshot.content is not None
        story.append(
            _chapter_markdown(
                snapshot.content,
                snapshot.path.name,
                f"canonical chapter {snapshot.path.name}",
            )
        )
    return tuple(story)


def _public_markdown_story(
    snapshot: _FileSnapshot,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    assert snapshot.content is not None
    try:
        text = snapshot.content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("public fiction Markdown is not UTF-8") from error
    lines = text.splitlines()
    try:
        first_delimiter = lines.index("---")
    except ValueError as error:
        raise ValueError(
            "public fiction Markdown story content lacks its section delimiter"
        ) from error
    story_lines = lines[first_delimiter + 1 :]
    sections: list[list[str]] = []
    current: list[str] = []
    for line in story_lines:
        if line == "---":
            _require(
                any(value.strip() for value in current),
                "public fiction Markdown contains an empty story section",
            )
            sections.append(current)
            current = []
        else:
            current.append(line)
    _require(
        not any(value.strip() for value in current),
        "public fiction Markdown has extra story content after its final section",
    )
    story = []
    for index, section in enumerate(sections, start=1):
        story.append(
            _chapter_markdown(
                "\n".join(section).encode("utf-8"),
                f"section-{index}.md",
                f"public fiction Markdown section {index}",
            )
        )
    return tuple(story)


def _safe_epub_path(value: str, label: str) -> str:
    _require(
        isinstance(value, str)
        and bool(value)
        and "\\" not in value
        and not value.startswith("/"),
        f"{label} is an unsafe EPUB path",
    )
    parts = PurePosixPath(value).parts
    _require(
        all(part not in {"", ".", ".."} for part in parts),
        f"{label} is an unsafe EPUB path",
    )
    return value


def _epub_href(opf_path: str, href: object, label: str) -> str:
    _require(
        isinstance(href, str) and "#" not in href and "?" not in href,
        f"{label} is invalid",
    )
    joined = posixpath.normpath(posixpath.join(posixpath.dirname(opf_path), href))
    return _safe_epub_path(joined, label)


def _epub_xml(
    archive: zipfile.ZipFile,
    entries: dict[str, zipfile.ZipInfo],
    name: str,
    label: str,
) -> ET.Element:
    _require(name in entries, f"{label} is missing from the EPUB")
    _require(entries[name].file_size <= 16 * 1024 * 1024, f"{label} is too large")
    try:
        return ET.fromstring(archive.read(name))
    except (ET.ParseError, UnicodeError, OSError, RuntimeError) as error:
        raise ValueError(f"{label} is invalid XML") from error


def _plain_inline_markdown(value: str) -> str:
    value = re.sub(r"\*\*(.+?)\*\*", r"\1", value)
    value = re.sub(r"__(.+?)__", r"\1", value)
    value = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\1", value)
    return re.sub(r"(?<!_)_(?!_)(.+?)(?<!_)_(?!_)", r"\1", value)


def _epub_story(
    epub: Path,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    try:
        archive = zipfile.ZipFile(epub)
    except (OSError, zipfile.BadZipFile) as error:
        raise ValueError("public fiction EPUB is not a valid zip archive") from error
    with archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        _require(len(names) == len(set(names)), "public fiction EPUB has duplicate files")
        entries: dict[str, zipfile.ZipInfo] = {}
        for info in infos:
            name = _safe_epub_path(info.filename, "EPUB member")
            mode = info.external_attr >> 16
            _require(not stat.S_ISLNK(mode), f"EPUB member is a symlink: {name}")
            entries[name] = info

        container = _epub_xml(
            archive, entries, "META-INF/container.xml", "EPUB container"
        )
        container_namespace = "urn:oasis:names:tc:opendocument:xmlns:container"
        rootfiles = container.findall(
            f".//{{{container_namespace}}}rootfile"
        )
        _require(len(rootfiles) == 1, "EPUB container must name exactly one package")
        opf_path = _safe_epub_path(
            rootfiles[0].get("full-path", ""), "EPUB package path"
        )
        package = _epub_xml(archive, entries, opf_path, "EPUB package")
        opf_namespace = "http://www.idpf.org/2007/opf"
        manifest = package.find(f"{{{opf_namespace}}}manifest")
        spine = package.find(f"{{{opf_namespace}}}spine")
        _require(manifest is not None and spine is not None, "EPUB lacks manifest or spine")

        items: dict[str, tuple[str, str]] = {}
        hrefs: set[str] = set()
        for item in list(manifest):
            _require(item.tag == f"{{{opf_namespace}}}item", "EPUB manifest is invalid")
            item_id = item.get("id")
            media_type = item.get("media-type")
            _require(
                isinstance(item_id, str)
                and bool(item_id)
                and item_id not in items
                and isinstance(media_type, str),
                "EPUB manifest item identity is invalid",
            )
            href = _epub_href(opf_path, item.get("href"), "EPUB manifest href")
            _require(href not in hrefs and href in entries, "EPUB manifest href is invalid")
            hrefs.add(href)
            items[item_id] = (href, media_type)

        xhtml_media = "application/xhtml+xml"
        declared_xhtml = {
            href for href, media_type in items.values() if media_type == xhtml_media
        }
        archived_xhtml = {name for name in entries if name.endswith(".xhtml")}
        _require(
            archived_xhtml == declared_xhtml,
            "public fiction EPUB has an unmanifested chapter-like XHTML file",
        )

        epub_type = "{http://www.idpf.org/2007/ops}type"
        documents: dict[str, tuple[str | None, ET.Element | None]] = {}
        for item_id, (href, media_type) in items.items():
            if media_type != xhtml_media:
                continue
            document = _epub_xml(archive, entries, href, f"EPUB document {href}")
            sections = document.findall(
                ".//{http://www.w3.org/1999/xhtml}section"
            )
            chapter_sections = [
                section
                for section in sections
                if "chapter" in section.get(epub_type, "").split()
            ]
            _require(
                len(chapter_sections) <= 1,
                f"EPUB document {href} has multiple chapter sections",
            )
            if chapter_sections:
                documents[item_id] = ("chapter", chapter_sections[0])
            else:
                section_type = sections[0].get(epub_type, "") if sections else None
                documents[item_id] = (section_type, sections[0] if sections else None)

        spine_ids: list[str] = []
        for itemref in list(spine):
            _require(itemref.tag == f"{{{opf_namespace}}}itemref", "EPUB spine is invalid")
            item_id = itemref.get("idref")
            _require(
                isinstance(item_id, str)
                and item_id in items
                and item_id not in spine_ids,
                "EPUB spine item identity is invalid",
            )
            spine_ids.append(item_id)
        chapter_ids = [
            item_id
            for item_id in spine_ids
            if documents.get(item_id, (None, None))[0] == "chapter"
        ]
        manifest_chapter_ids = {
            item_id for item_id, (kind, _section) in documents.items() if kind == "chapter"
        }
        _require(
            set(chapter_ids) == manifest_chapter_ids
            and len(chapter_ids) == len(manifest_chapter_ids),
            "public fiction EPUB contains an unspined chapter",
        )
        for item_id in spine_ids:
            if item_id in chapter_ids:
                continue
            kind = documents.get(item_id, (None, None))[0]
            _require(
                isinstance(kind, str)
                and bool({"cover", "titlepage"} & set(kind.split())),
                "public fiction EPUB spine contains a non-narrated document",
            )

        story = []
        xhtml_namespace = "http://www.w3.org/1999/xhtml"
        for item_id in chapter_ids:
            section = documents[item_id][1]
            assert section is not None
            children = list(section)
            _require(
                bool(children) and children[0].tag == f"{{{xhtml_namespace}}}h1",
                "public fiction EPUB chapter lacks its title",
            )
            title = "".join(children[0].itertext())
            paragraphs = []
            for child in children[1:]:
                _require(
                    child.tag == f"{{{xhtml_namespace}}}p",
                    "public fiction EPUB chapter has non-story content",
                )
                paragraphs.append("".join(child.itertext()))
            _require(bool(paragraphs), "public fiction EPUB chapter body is empty")
            story.append((title, tuple(paragraphs)))
        return tuple(story)


def _verify_public_story_content(
    manuscript: _FileSnapshot,
    epub: Path,
    chapters_dir: Path,
    private_snapshots: list[_FileSnapshot],
) -> None:
    canonical = _canonical_story(chapters_dir, private_snapshots)
    _require(
        _public_markdown_story(manuscript) == canonical,
        "public fiction Markdown story content differs from canonical chapters",
    )
    expected_epub = tuple(
        (title, tuple(_plain_inline_markdown(value) for value in paragraphs))
        for title, paragraphs in canonical
    )
    _require(
        _epub_story(epub) == expected_epub,
        "public fiction EPUB spine content differs from canonical chapters",
    )


def _verify_fiction_readme(book_dir: Path) -> _FileSnapshot:
    readme = book_dir / "README.md"
    try:
        snapshot = _snapshot_file(readme, "fiction README", capture=True)
        assert snapshot.content is not None
        text = snapshot.content.decode("utf-8")
    except UnicodeError as error:
        raise ValueError("fiction README is missing or unreadable") from error
    _require(
        FICTION_DISCLOSURE in text,
        "fiction README must include the approved disclosure",
    )
    return snapshot


def verify_public_fiction_package(
    book_dir: Path,
    release_m4b: Path,
    voice_cast: Path,
    fiction_receipt: Path,
    chapters_dir: Path,
    echo_success_receipt: Path,
) -> None:
    """Verify a release-backed schema-v2 fiction public package."""
    book_dir = Path(book_dir)
    release_m4b = Path(release_m4b)
    voice_cast = Path(voice_cast)
    fiction_receipt = Path(fiction_receipt)
    chapters_dir = Path(chapters_dir)
    echo_success_receipt = Path(echo_success_receipt)
    _require_regular_directory(book_dir, "fiction book directory")
    for path, label in (
        (release_m4b, "release M4B"),
        (voice_cast, "voice cast"),
        (fiction_receipt, "fiction receipt"),
        (echo_success_receipt, "Echo success receipt"),
    ):
        _require_regular_file(path, label)
    _require_regular_directory(chapters_dir, "chapters directory")

    receipt_value, receipt_snapshot = _read_json_snapshot(
        book_dir / "publication.json", "publication.json"
    )
    _require(isinstance(receipt_value, dict), "publication.json must be an object")
    receipt = receipt_value
    reject_private_values(receipt)
    slug = _verify_fiction_receipt_fields(receipt)
    _verify_fiction_public_root(book_dir, slug)
    with tempfile.TemporaryDirectory(prefix="fiction-public-probes-") as raw_probe_dir:
        probe_dir = Path(raw_probe_dir).resolve()
        epub_probe_copy = probe_dir / f"{slug}.epub"
        release_probe_copy = probe_dir / f"{slug}.m4b"
        artifact_hashes, artifact_snapshots = _verify_fiction_artifacts(
            book_dir, receipt, slug, epub_probe_copy
        )
        release_hash, release_snapshot = _verify_release(
            receipt, slug, release_m4b, release_probe_copy
        )
        epub_snapshot = next(
            snapshot
            for snapshot in artifact_snapshots
            if snapshot.path.name == f"{slug}.epub"
        )
        epub_probe_snapshot = _snapshot_file(
            epub_probe_copy, "immutable fiction EPUB"
        )
        release_probe_snapshot = _snapshot_file(
            release_probe_copy, "immutable release M4B"
        )
        _require(
            epub_probe_snapshot.sha256 == epub_snapshot.sha256,
            "immutable fiction EPUB copy differs from verified source",
        )
        _require(
            release_probe_snapshot.sha256 == release_snapshot.sha256,
            "immutable release M4B copy differs from verified source",
        )
        _probe_fiction_media(
            epub_probe_copy,
            release_probe_copy,
            epub_snapshot,
            release_snapshot,
            epub_probe_snapshot,
            release_probe_snapshot,
        )
        private_snapshots = _verify_private_evidence(
            receipt,
            slug,
            artifact_hashes,
            release_hash,
            voice_cast,
            fiction_receipt,
            chapters_dir,
            echo_success_receipt,
        )
        manuscript_snapshot = next(
            snapshot
            for snapshot in artifact_snapshots
            if snapshot.path.name == f"{slug}.md"
        )
        _verify_public_story_content(
            manuscript_snapshot,
            epub_probe_copy,
            chapters_dir,
            private_snapshots,
        )
        _require_snapshot_unchanged(epub_probe_snapshot, "immutable fiction EPUB")
    cover_rights = receipt["coverRights"]
    assert isinstance(cover_rights, dict)
    _require(
        cover_rights["coverSHA256"] == artifact_hashes["portraitCover"],
        "coverRights cover SHA-256 does not match the public cover",
    )
    readme_snapshot = _verify_fiction_readme(book_dir)
    _verify_fiction_public_root(book_dir, slug)
    all_snapshots = [
        receipt_snapshot,
        *artifact_snapshots,
        release_snapshot,
        *private_snapshots,
        readme_snapshot,
    ]
    for snapshot in all_snapshots:
        _require_snapshot_unchanged(snapshot, snapshot.path.name)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("book_directory", type=Path)
    parser.add_argument("--release-m4b", type=Path)
    parser.add_argument("--voice-cast", type=Path)
    parser.add_argument("--fiction-receipt", type=Path)
    parser.add_argument("--chapters-dir", type=Path)
    parser.add_argument("--echo-success-receipt", type=Path)
    args = parser.parse_args(argv)
    evidence = (
        args.release_m4b,
        args.voice_cast,
        args.fiction_receipt,
        args.chapters_dir,
        args.echo_success_receipt,
    )
    if any(value is not None for value in evidence) and not all(
        value is not None for value in evidence
    ):
        print(
            "public audiobook verification usage error: supply all five fiction evidence paths",
            file=sys.stderr,
        )
        return 64
    try:
        if all(value is not None for value in evidence):
            verify_public_fiction_package(
                args.book_directory,
                args.release_m4b,
                args.voice_cast,
                args.fiction_receipt,
                args.chapters_dir,
                args.echo_success_receipt,
            )
        else:
            verify_public_package(args.book_directory)
    except ValueError as error:
        print(f"public audiobook verification failed: {error}", file=sys.stderr)
        return 1
    print("public audiobook verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
