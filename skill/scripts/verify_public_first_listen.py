#!/usr/bin/env python3
"""Verify a sanitized, explicitly authorized public audiobook package."""

from __future__ import annotations

import argparse
import hashlib
import html
import io
import json
import math
import os
import posixpath
import re
import stat
import struct
import subprocess
import sys
import tempfile
import uuid
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
    from .fiction_production_qc import (
        REQUIRED_ARTIFACTS as FICTION_REQUIRED_ARTIFACTS,
        REQUIRED_GATES as FICTION_REQUIRED_GATES,
        verify_fiction_receipt,
    )
except ImportError:
    from fiction_production_qc import (
        REQUIRED_ARTIFACTS as FICTION_REQUIRED_ARTIFACTS,
        REQUIRED_GATES as FICTION_REQUIRED_GATES,
        verify_fiction_receipt,
    )


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
_WINDOWS_DRIVE_PREFIX = re.compile(r"^[A-Za-z]:")
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
_PRIVATE_FICTION_RECEIPT_FIELDS = {
    "schemaVersion",
    "status",
    "productionMode",
    "privacy",
    "permissionToPublish",
    "humanReadingStatus",
    "canonicalChapterSHA256",
    "artifacts",
    "gates",
    "negativeHumanVerdictOverrides",
    "receiptDoesNotCertifyHumanAcceptance",
}
_MEDIA_PROBE_TIMEOUT_SECONDS = 30
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
    max_bytes: int | None = None,
) -> _FileSnapshot:
    _reject_symlink_ancestors(path, label)
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise ValueError(f"{label} is not a readable regular file") from error
    chunks: list[bytes] | None = None
    digest = hashlib.sha256()
    copy_stream = None
    try:
        before = os.fstat(descriptor)
        _require(stat.S_ISREG(before.st_mode), f"{label} must be a regular file")
        _require(
            max_bytes is None
            or (
                type(max_bytes) is int
                and max_bytes >= 0
                and before.st_size <= max_bytes
            ),
            f"{label} exceeds its snapshot size limit",
        )
        chunks = [] if capture else None
        if copy_to is not None:
            copy_stream = copy_to.open("xb")
        total_bytes = 0
        with os.fdopen(descriptor, "rb") as stream:
            descriptor = -1
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                total_bytes += len(chunk)
                _require(
                    max_bytes is None or total_bytes <= max_bytes,
                    f"{label} grew beyond its snapshot size limit",
                )
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


def _require_snapshot_unchanged(
    snapshot: _FileSnapshot,
    label: str,
    *,
    max_bytes: int | None = None,
) -> None:
    current = _snapshot_file(snapshot.path, label, max_bytes=max_bytes)
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
            capture=name in {"manuscript", "alignment", "portraitCover"},
            copy_to=epub_probe_copy if name == "epub" else None,
            max_bytes=_EPUB_MAX_COVER_BYTES if name == "portraitCover" else None,
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
            timeout=_MEDIA_PROBE_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as error:
        raise ValueError("fiction EPUB unzip -t timed out") from error
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
            timeout=_MEDIA_PROBE_TIMEOUT_SECONDS,
        )
        media = json.loads(
            probe.stdout,
            object_pairs_hook=_unique_json_object,
            parse_constant=_reject_nonfinite_json_number,
        )
    except subprocess.TimeoutExpired as error:
        raise ValueError("fiction M4B ffprobe timed out") from error
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


def _private_relative_path(value: object, label: str) -> str:
    _require(
        isinstance(value, str)
        and bool(value)
        and "\\" not in value
        and not value.startswith("/")
        and _WINDOWS_DRIVE_PREFIX.match(value) is None,
        f"{label} must be a nonempty relative POSIX-safe artifact path",
    )
    relative = PurePosixPath(value)
    _require(
        relative.as_posix() == value
        and not relative.is_absolute()
        and all(part not in {"", ".", ".."} for part in relative.parts),
        f"{label} must be a nonempty relative POSIX-safe artifact path",
    )
    return value


def _write_private_mirror_file(path: Path, content: bytes, label: str) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        with path.open("xb") as destination:
            destination.write(content)
            destination.flush()
            os.fsync(destination.fileno())
        os.chmod(path, 0o400)
    except OSError as error:
        raise ValueError(f"could not construct immutable {label}") from error


def _verify_fiction_receipt_mirror(
    fiction_snapshot: _FileSnapshot,
    chapter_snapshots: dict[str, _FileSnapshot],
    artifact_snapshots: dict[str, tuple[str, _FileSnapshot]],
) -> None:
    assert fiction_snapshot.content is not None
    payloads: dict[str, bytes] = {
        "research/fiction-production-receipt.json": fiction_snapshot.content,
    }
    for filename, snapshot in chapter_snapshots.items():
        assert snapshot.content is not None
        relative = f"chapters/{filename}"
        _require(
            relative not in payloads or payloads[relative] == snapshot.content,
            "private fiction mirror has conflicting chapter content",
        )
        payloads[relative] = snapshot.content
    for name, (relative, snapshot) in artifact_snapshots.items():
        assert snapshot.content is not None
        _require(
            relative not in payloads or payloads[relative] == snapshot.content,
            f"private fiction mirror has conflicting {name} content",
        )
        payloads[relative] = snapshot.content

    with tempfile.TemporaryDirectory(
        prefix="fiction-private-qc-mirror-"
    ) as raw_mirror_root:
        mirror_root = Path(raw_mirror_root).resolve()
        mirror_snapshots: list[_FileSnapshot] = []
        for relative, content in sorted(payloads.items()):
            mirror_path = mirror_root.joinpath(*PurePosixPath(relative).parts)
            _write_private_mirror_file(
                mirror_path, content, f"fiction QC mirror file {relative}"
            )
            mirror_snapshots.append(
                _snapshot_file(mirror_path, f"fiction QC mirror file {relative}")
            )
        mirror_receipt = mirror_root / "research/fiction-production-receipt.json"
        mirror_chapters = mirror_root / "chapters"
        verify_fiction_receipt(mirror_chapters, mirror_receipt)
        for snapshot in mirror_snapshots:
            _require_snapshot_unchanged(snapshot, "immutable fiction QC mirror file")


def _validate_private_fiction_receipt(
    chapters_dir: Path,
    fiction_receipt: Path,
    fiction: dict[str, object],
    fiction_snapshot: _FileSnapshot,
) -> list[_FileSnapshot]:
    _require(
        set(fiction) == _PRIVATE_FICTION_RECEIPT_FIELDS,
        "private fiction receipt must contain exactly the production fields",
    )
    _require(
        type(fiction.get("schemaVersion")) is int
        and fiction["schemaVersion"] == 1,
        "private fiction receipt schemaVersion must be integer 1",
    )
    for field, expected in (
        ("status", "first-listen"),
        ("productionMode", "unattended-first-listen"),
        ("privacy", "private"),
        ("humanReadingStatus", "pending"),
    ):
        _require(
            fiction.get(field) == expected,
            f"private fiction receipt {field} must be {expected}",
        )
    for field, expected in (
        ("permissionToPublish", False),
        ("negativeHumanVerdictOverrides", True),
        ("receiptDoesNotCertifyHumanAcceptance", True),
    ):
        _require(
            type(fiction.get(field)) is bool and fiction[field] is expected,
            f"private fiction receipt {field} must be boolean {str(expected).lower()}",
        )

    chapter_hashes = fiction.get("canonicalChapterSHA256")
    _require(
        isinstance(chapter_hashes, dict),
        "private fiction receipt canonicalChapterSHA256 must be an object",
    )
    try:
        current_chapters = sorted(
            (
                path
                for path in chapters_dir.iterdir()
                if path.name.startswith("ch") and path.suffix == ".md"
            ),
            key=lambda path: path.name,
        )
    except OSError as error:
        raise ValueError("canonical fiction chapter coverage is unreadable") from error
    current_names = [path.name for path in current_chapters]
    _require(
        bool(current_names)
        and set(chapter_hashes) == set(current_names)
        and len(chapter_hashes) == len(current_names),
        "private fiction receipt canonical chapter coverage is not exact",
    )
    chapter_snapshots: dict[str, _FileSnapshot] = {}
    for path in current_chapters:
        expected_hash = _require_sha256(
            chapter_hashes.get(path.name),
            f"private fiction receipt canonical chapter {path.name} SHA-256",
        )
        snapshot = _snapshot_file(
            path, f"canonical fiction chapter {path.name}", capture=True
        )
        _require(
            snapshot.sha256 == expected_hash,
            f"private fiction receipt canonical chapter hash mismatch: {path.name}",
        )
        chapter_snapshots[path.name] = snapshot

    artifacts = fiction.get("artifacts")
    _require(
        isinstance(artifacts, dict)
        and set(artifacts) == set(FICTION_REQUIRED_ARTIFACTS),
        "private fiction receipt artifacts must contain exactly the required artifacts",
    )
    run_root = fiction_receipt.parent.parent
    artifact_snapshots: dict[str, tuple[str, _FileSnapshot]] = {}
    for name in sorted(FICTION_REQUIRED_ARTIFACTS):
        record = artifacts[name]
        _require(
            isinstance(record, dict) and set(record) == {"path", "sha256"},
            f"private fiction receipt artifact {name} must contain exactly path and sha256",
        )
        relative = _private_relative_path(
            record.get("path"), f"private fiction receipt artifact {name} path"
        )
        expected_hash = _require_sha256(
            record.get("sha256"),
            f"private fiction receipt artifact {name} SHA-256",
        )
        path = run_root.joinpath(*PurePosixPath(relative).parts)
        snapshot = _snapshot_file(
            path, f"private fiction receipt artifact {name}", capture=True
        )
        _require(
            snapshot.sha256 == expected_hash,
            f"private fiction receipt artifact {name} hash mismatch",
        )
        artifact_snapshots[name] = (relative, snapshot)

    gates = fiction.get("gates")
    _require(
        isinstance(gates, dict) and set(gates) == set(FICTION_REQUIRED_GATES),
        "private fiction receipt gates must contain exactly the required gates",
    )
    for name in sorted(FICTION_REQUIRED_GATES):
        _require(
            gates[name] == "pass",
            f"private fiction receipt gate {name} must be pass",
        )

    _verify_fiction_receipt_mirror(
        fiction_snapshot, chapter_snapshots, artifact_snapshots
    )
    try:
        final_chapter_names = sorted(
            path.name
            for path in chapters_dir.iterdir()
            if path.name.startswith("ch") and path.suffix == ".md"
        )
    except OSError as error:
        raise ValueError("canonical fiction chapter coverage changed") from error
    _require(
        final_chapter_names == current_names,
        "canonical fiction chapter coverage changed during verification",
    )
    snapshots = [
        *chapter_snapshots.values(),
        *(snapshot for _relative, snapshot in artifact_snapshots.values()),
    ]
    for snapshot in snapshots:
        _require_snapshot_unchanged(snapshot, "fiction private input")
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
    fiction_inputs = _validate_private_fiction_receipt(
        chapters_dir,
        fiction_receipt,
        fiction,
        fiction_snapshot,
    )
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


def _builder_markdown_identity(
    snapshot: _FileSnapshot,
    canonical: tuple[tuple[str, tuple[str, ...]], ...],
    author: str,
) -> tuple[str, str]:
    assert snapshot.content is not None
    try:
        text = snapshot.content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("public fiction Markdown is not UTF-8") from error
    lines = text.splitlines()
    _require(
        bool(lines) and lines[0].startswith("# ") and bool(lines[0][2:]),
        "public fiction Markdown does not match the unchanged builder grammar",
    )
    title = lines[0][2:]
    subtitle = ""
    if len(lines) > 2 and lines[2].startswith("_") and lines[2].endswith("_"):
        subtitle = lines[2][1:-1]
        _require(
            bool(subtitle),
            "public fiction Markdown does not match the unchanged builder grammar",
        )

    total_words = sum(
        len(paragraph.split())
        for _chapter_title, paragraphs in canonical
        for paragraph in paragraphs
    )
    expected = [f"# {title}", ""]
    if subtitle:
        expected.extend([f"_{subtitle}_", ""])
    expected.extend(
        [f"by {author}", "", f"Roughly {total_words:,d} words.", "", "---", ""]
    )
    for chapter_title, paragraphs in canonical:
        expected.extend([f"## {chapter_title}", ""])
        for paragraph in paragraphs:
            expected.extend([paragraph, ""])
        expected.extend(["---", ""])
    _require(
        snapshot.content == "\n".join(expected).encode("utf-8"),
        "public fiction Markdown does not match the unchanged builder grammar and canonical story",
    )
    return title, subtitle


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
    content = _read_epub_member(
        archive,
        entries,
        name,
        label,
        _epub_member_limit(name),
    )
    try:
        _validate_epub_xml_lexical_identity(content, name, label)
        return ET.fromstring(content)
    except (ET.ParseError, UnicodeError, OSError, RuntimeError) as error:
        raise ValueError(f"{label} is invalid XML") from error


def _builder_inline_html(value: str) -> str:
    rendered = html.escape(value, quote=False)
    rendered = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", rendered)
    rendered = re.sub(r"__(.+?)__", r"<strong>\1</strong>", rendered)
    rendered = re.sub(
        r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", rendered
    )
    return re.sub(
        r"(?<!_)_(?!_)(.+?)(?<!_)_(?!_)", r"<em>\1</em>", rendered
    )


_XHTML_NAMESPACE = "http://www.w3.org/1999/xhtml"
_XHTML = f"{{{_XHTML_NAMESPACE}}}"
_EPUB_TYPE = "{http://www.idpf.org/2007/ops}type"
_OPF_NAMESPACE = "http://www.idpf.org/2007/opf"
_OPF = f"{{{_OPF_NAMESPACE}}}"
_DC_NAMESPACE = "http://purl.org/dc/elements/1.1/"
_DC = f"{{{_DC_NAMESPACE}}}"
_CONTAINER_NAMESPACE = "urn:oasis:names:tc:opendocument:xmlns:container"
_CONTAINER = f"{{{_CONTAINER_NAMESPACE}}}"
_NCX_NAMESPACE = "http://www.daisy.org/z3986/2005/ncx/"
_NCX = f"{{{_NCX_NAMESPACE}}}"
_EPUB_MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
_EPUB_MAX_MEMBERS = 64
_EPUB_MAX_CENTRAL_DIRECTORY_BYTES = 4 * 1024 * 1024
_EPUB_MAX_COMPRESSED_MEMBER_BYTES = 16 * 1024 * 1024
_EPUB_MAX_COMPRESSED_TOTAL_BYTES = 64 * 1024 * 1024
_EPUB_MAX_UNCOMPRESSED_TOTAL_BYTES = 64 * 1024 * 1024
_EPUB_MAX_COMPRESSION_RATIO = 100
_EPUB_MAX_XML_BYTES = 1024 * 1024
_EPUB_MAX_XHTML_BYTES = 4 * 1024 * 1024
_EPUB_MAX_CSS_BYTES = 64 * 1024
_EPUB_MAX_COVER_BYTES = 16 * 1024 * 1024
_ZIP_DOS_SPECIAL_FILE_MASK = 0x08 | 0x10 | 0x40
_BUILDER_EPUB_CSS = (
    "body{font-family:Georgia,'Times New Roman',serif;line-height:1.6;margin:5% 6%;}"
    "h1{font-size:1.5em;line-height:1.25;margin:0 0 1em;}"
    "p{margin:0 0 1em;text-align:justify;}"
    ".title-page{text-align:center;margin-top:25%;}.title-page h1{font-size:1.8em;}"
    ".title-page .author{font-size:1.1em;margin-top:1.5em;font-style:italic;}"
    ".title-page .sub{margin-top:2em;color:#444;}"
    "figure{margin:1.5em 0;text-align:center;}"
    "figure img{max-width:100%;height:auto;}"
    "figcaption{font-size:0.85em;color:#555;margin-top:0.5em;font-style:italic;text-align:center;}"
).encode("utf-8")


@dataclass(frozen=True)
class _ClassicZipEnd:
    member_count: int
    central_offset: int
    central_size: int
    eocd_offset: int


@dataclass(frozen=True)
class _ClassicZipRecord:
    name: str
    raw_name: bytes
    create_version: int
    extract_version: int
    flags: int
    method: int
    modified_time: int
    modified_date: int
    crc32: int
    compressed_size: int
    uncompressed_size: int
    internal_attributes: int
    external_attributes: int
    local_offset: int


def _validate_epub_xml_lexical_identity(
    content: bytes, name: str, label: str
) -> None:
    declaration = b'<?xml version="1.0" encoding="utf-8"?>'
    stripped = content.lstrip()
    _require(
        stripped.startswith(declaration),
        f"{label} must use the unchanged builder XML declaration",
    )
    after_declaration = stripped[len(declaration) :]
    _require(
        b"<!--" not in content and b"<?" not in after_declaration,
        f"{label} must not contain XML comments or processing instructions",
    )
    is_xhtml = name.endswith(".xhtml")
    if is_xhtml:
        _require(
            after_declaration.count(b"<!DOCTYPE") == 1
            and b"<!DOCTYPE html>" in after_declaration,
            f"{label} must contain exactly the unchanged builder HTML doctype",
        )
    else:
        _require(
            b"<!DOCTYPE" not in after_declaration,
            f"{label} must not contain a doctype",
        )
    try:
        namespaces = [
            namespace
            for _event, namespace in ET.iterparse(
                io.BytesIO(content), events=("start-ns",)
            )
        ]
    except (ET.ParseError, UnicodeError) as error:
        raise ValueError(f"{label} has invalid XML namespace declarations") from error
    if is_xhtml:
        expected_namespaces = [
            ("", _XHTML_NAMESPACE),
            ("epub", "http://www.idpf.org/2007/ops"),
        ]
    elif name == "OEBPS/content.opf":
        expected_namespaces = [("", _OPF_NAMESPACE), ("dc", _DC_NAMESPACE)]
    elif name == "META-INF/container.xml":
        expected_namespaces = [("", _CONTAINER_NAMESPACE)]
    elif name == "OEBPS/toc.ncx":
        expected_namespaces = [("", _NCX_NAMESPACE)]
    else:
        raise ValueError(f"{label} has an unknown XML role")
    _require(
        namespaces == expected_namespaces,
        f"{label} namespace declarations differ from the unchanged builder",
    )


def _epub_member_limit(name: str) -> int:
    if name == "mimetype":
        return 64
    if name.endswith(".css"):
        return _EPUB_MAX_CSS_BYTES
    if PurePosixPath(name).name in {"cover.png", "cover.jpg"}:
        return _EPUB_MAX_COVER_BYTES
    if name.endswith(".xhtml"):
        return _EPUB_MAX_XHTML_BYTES
    if name.endswith((".xml", ".opf", ".ncx")):
        return _EPUB_MAX_XML_BYTES
    return _EPUB_MAX_XHTML_BYTES


def _read_classic_zip_bytes(
    stream, offset: int, size: int, label: str
) -> bytes:
    _require(
        offset >= 0 and size >= 0,
        f"public fiction EPUB {label} is outside the classic ZIP envelope",
    )
    try:
        stream.seek(offset)
        value = stream.read(size)
    except OSError as error:
        raise ValueError(f"public fiction EPUB {label} is unreadable") from error
    _require(
        len(value) == size,
        f"public fiction EPUB {label} is truncated",
    )
    return value


def _classic_zip_end(stream, archive_size: int) -> _ClassicZipEnd:
    tail_size = min(archive_size, 65_535 + 22)
    tail = _read_classic_zip_bytes(
        stream,
        archive_size - tail_size,
        tail_size,
        "end record window",
    )
    eocd_index = tail.rfind(b"PK\x05\x06")
    _require(eocd_index >= 0, "public fiction EPUB lacks an end record")
    try:
        (
            signature,
            disk_number,
            central_disk,
            disk_entries,
            total_entries,
            central_size,
            central_offset,
            comment_size,
        ) = struct.unpack_from("<4s4H2IH", tail, eocd_index)
    except struct.error as error:
        raise ValueError("public fiction EPUB end record is truncated") from error
    _require(signature == b"PK\x05\x06", "public fiction EPUB end record is invalid")
    _require(
        disk_number == 0
        and central_disk == 0
        and disk_entries == total_entries
        and 0 < total_entries <= _EPUB_MAX_MEMBERS,
        "public fiction EPUB declared member count exceeds its resource limit",
    )
    _require(
        comment_size == 0 and eocd_index + 22 == len(tail),
        "public fiction EPUB archive comment or trailing bytes are not allowed",
    )
    eocd_offset = archive_size - tail_size + eocd_index
    _require(
        0 < central_size <= _EPUB_MAX_CENTRAL_DIRECTORY_BYTES
        and central_offset + central_size == eocd_offset,
        "public fiction EPUB central directory exceeds its resource limit",
    )
    _require(
        central_offset not in {0xFFFFFFFF}
        and central_size not in {0xFFFFFFFF}
        and total_entries != 0xFFFF
        and eocd_offset + 22 == archive_size,
        "public fiction EPUB must use one complete classic ZIP envelope",
    )
    return _ClassicZipEnd(
        member_count=total_entries,
        central_offset=central_offset,
        central_size=central_size,
        eocd_offset=eocd_offset,
    )


def _classic_zip_records(
    stream, end: _ClassicZipEnd
) -> list[_ClassicZipRecord]:
    cursor = end.central_offset
    central_end = end.central_offset + end.central_size
    records: list[_ClassicZipRecord] = []
    names: set[str] = set()
    local_offsets: set[int] = set()
    total_compressed = 0
    total_uncompressed = 0
    for index in range(end.member_count):
        fixed = _read_classic_zip_bytes(
            stream, cursor, 46, f"central record {index + 1}"
        )
        try:
            (
                signature,
                create_version,
                extract_version,
                flags,
                method,
                modified_time,
                modified_date,
                crc32,
                compressed_size,
                uncompressed_size,
                filename_size,
                extra_size,
                comment_size,
                disk_start,
                internal_attributes,
                external_attributes,
                local_offset,
            ) = struct.unpack("<4s6H3I5H2I", fixed)
        except struct.error as error:
            raise ValueError("public fiction EPUB central record is invalid") from error
        _require(
            signature == b"PK\x01\x02",
            "public fiction EPUB central directory has an invalid signature",
        )
        variable_size = filename_size + extra_size + comment_size
        _require(
            cursor + 46 + variable_size <= central_end,
            "public fiction EPUB central record exceeds its declared extent",
        )
        raw_name = _read_classic_zip_bytes(
            stream, cursor + 46, filename_size, f"central filename {index + 1}"
        )
        _require(
            extra_size == 0 and comment_size == 0,
            "public fiction EPUB central member extra data or comment is not allowed",
        )
        _require(
            disk_start == 0,
            "public fiction EPUB member must not span ZIP disks",
        )
        _require(
            flags == 0,
            "public fiction EPUB member has encryption, data descriptor, or unsupported flags",
        )
        _require(
            method in {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED},
            "public fiction EPUB member uses an unsupported compression method",
        )
        _require(
            extract_version <= 20,
            "public fiction EPUB ZIP64 or non-classic extract version is not allowed",
        )
        _require(
            compressed_size != 0xFFFFFFFF
            and uncompressed_size != 0xFFFFFFFF
            and local_offset != 0xFFFFFFFF,
            "public fiction EPUB ZIP64 member metadata is not allowed",
        )
        try:
            name = raw_name.decode("ascii")
        except UnicodeDecodeError as error:
            raise ValueError(
                "public fiction EPUB member filename is not unchanged-builder ASCII"
            ) from error
        name = _safe_epub_path(name, "EPUB central member")
        _require(
            raw_name == name.encode("ascii") and not name.endswith("/"),
            "public fiction EPUB member filename is not an exact regular-file path",
        )
        _require(name not in names, "public fiction EPUB has duplicate files")
        _require(
            local_offset not in local_offsets and local_offset < end.central_offset,
            "public fiction EPUB local header offsets overlap the central directory",
        )
        mode = external_attributes >> 16
        _require(
            stat.S_IFMT(mode) in {0, stat.S_IFREG}
            and not external_attributes & _ZIP_DOS_SPECIAL_FILE_MASK,
            f"EPUB member mode is not a regular file: {name}",
        )
        _require(
            compressed_size <= _EPUB_MAX_COMPRESSED_MEMBER_BYTES,
            f"EPUB member compressed size exceeds its resource limit: {name}",
        )
        _require(
            uncompressed_size <= _epub_member_limit(name),
            f"EPUB member uncompressed size exceeds its role resource limit: {name}",
        )
        if compressed_size == 0:
            _require(
                uncompressed_size == 0,
                f"EPUB member has a zero compressed size with nonempty content: {name}",
            )
        else:
            _require(
                uncompressed_size
                <= compressed_size * _EPUB_MAX_COMPRESSION_RATIO,
                f"EPUB member compression ratio exceeds its resource limit: {name}",
            )
        _require(
            method != zipfile.ZIP_STORED
            or compressed_size == uncompressed_size,
            f"EPUB stored member compressed and uncompressed sizes differ: {name}",
        )
        total_compressed += compressed_size
        total_uncompressed += uncompressed_size
        names.add(name)
        local_offsets.add(local_offset)
        records.append(
            _ClassicZipRecord(
                name=name,
                raw_name=raw_name,
                create_version=create_version,
                extract_version=extract_version,
                flags=flags,
                method=method,
                modified_time=modified_time,
                modified_date=modified_date,
                crc32=crc32,
                compressed_size=compressed_size,
                uncompressed_size=uncompressed_size,
                internal_attributes=internal_attributes,
                external_attributes=external_attributes,
                local_offset=local_offset,
            )
        )
        cursor += 46 + variable_size
    _require(
        cursor == central_end == end.eocd_offset,
        "public fiction EPUB central directory does not fill its exact extent",
    )
    _require(
        total_compressed <= _EPUB_MAX_COMPRESSED_TOTAL_BYTES,
        "public fiction EPUB total compressed size exceeds its aggregate limit",
    )
    _require(
        total_uncompressed <= _EPUB_MAX_UNCOMPRESSED_TOTAL_BYTES,
        "public fiction EPUB total uncompressed size exceeds its aggregate limit",
    )

    by_local_offset = sorted(records, key=lambda record: record.local_offset)
    _require(
        bool(by_local_offset) and by_local_offset[0].local_offset == 0,
        "public fiction EPUB has a preamble before its first local header",
    )
    for index, record in enumerate(by_local_offset):
        fixed = _read_classic_zip_bytes(
            stream,
            record.local_offset,
            30,
            f"local header for {record.name}",
        )
        try:
            (
                signature,
                extract_version,
                flags,
                method,
                modified_time,
                modified_date,
                crc32,
                compressed_size,
                uncompressed_size,
                filename_size,
                extra_size,
            ) = struct.unpack("<4s5H3I2H", fixed)
        except struct.error as error:
            raise ValueError("public fiction EPUB local header is invalid") from error
        _require(
            signature == b"PK\x03\x04",
            f"public fiction EPUB local signature is invalid: {record.name}",
        )
        _require(
            extra_size == 0,
            f"public fiction EPUB local extra data is not allowed: {record.name}",
        )
        local_name = _read_classic_zip_bytes(
            stream,
            record.local_offset + 30,
            filename_size,
            f"local filename for {record.name}",
        )
        _require(
            local_name == record.raw_name,
            f"public fiction EPUB local filename disagrees with central metadata: {record.name}",
        )
        _require(
            (
                extract_version,
                flags,
                method,
                modified_time,
                modified_date,
                crc32,
                compressed_size,
                uncompressed_size,
            )
            == (
                record.extract_version,
                record.flags,
                record.method,
                record.modified_time,
                record.modified_date,
                record.crc32,
                record.compressed_size,
                record.uncompressed_size,
            ),
            f"public fiction EPUB local header disagrees with central metadata: {record.name}",
        )
        data_start = record.local_offset + 30 + filename_size
        data_end = data_start + record.compressed_size
        next_offset = (
            by_local_offset[index + 1].local_offset
            if index + 1 < len(by_local_offset)
            else end.central_offset
        )
        _require(
            data_end == next_offset,
            f"public fiction EPUB has a gap or overlap after local member: {record.name}",
        )
    return records


def _inspect_epub_archive(
    epub: Path, *, public_cover_size: int
) -> tuple[list[zipfile.ZipInfo], dict[str, zipfile.ZipInfo]]:
    _reject_symlink_ancestors(epub, "immutable fiction EPUB")
    try:
        archive_size = epub.stat().st_size
    except OSError as error:
        raise ValueError("public fiction EPUB resource metadata is unreadable") from error
    _require(
        0 < archive_size <= _EPUB_MAX_ARCHIVE_BYTES,
        "public fiction EPUB compressed package size exceeds its resource limit",
    )
    try:
        with epub.open("rb") as stream:
            end = _classic_zip_end(stream, archive_size)
            raw_records = _classic_zip_records(stream, end)
    except OSError as error:
        raise ValueError("public fiction EPUB envelope is unreadable") from error
    try:
        with zipfile.ZipFile(epub) as archive:
            infos = archive.infolist()
    except (OSError, zipfile.BadZipFile, zipfile.LargeZipFile) as error:
        raise ValueError("public fiction EPUB is not a valid zip archive") from error
    _require(
        len(infos) == end.member_count == len(raw_records),
        "public fiction EPUB member count exceeds its resource limit",
    )
    entries: dict[str, zipfile.ZipInfo] = {}
    total_compressed = 0
    total_uncompressed = 0
    for info, raw_record in zip(infos, raw_records, strict=True):
        name = _safe_epub_path(info.filename, "EPUB member")
        _require(
            (
                name,
                info.create_version,
                info.extract_version,
                info.flag_bits,
                info.compress_type,
                info.CRC,
                info.compress_size,
                info.file_size,
                info.internal_attr,
                info.external_attr,
                info.header_offset,
            )
            == (
                raw_record.name,
                raw_record.create_version & 0xFF,
                raw_record.extract_version,
                raw_record.flags,
                raw_record.method,
                raw_record.crc32,
                raw_record.compressed_size,
                raw_record.uncompressed_size,
                raw_record.internal_attributes,
                raw_record.external_attributes,
                raw_record.local_offset,
            ),
            f"EPUB member central metadata is inconsistent: {name}",
        )
        _require(name not in entries, "public fiction EPUB has duplicate files")
        _require(
            info.comment == b"" and info.extra == b"",
            f"EPUB member comment or extra metadata is not allowed: {name}",
        )
        mode = info.external_attr >> 16
        _require(
            stat.S_IFMT(mode) in {0, stat.S_IFREG},
            f"EPUB member mode is not a regular file: {name}",
        )
        _require(
            not info.flag_bits & 0x1,
            f"EPUB member must not be encrypted: {name}",
        )
        _require(
            info.compress_type in {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED},
            f"EPUB member uses an unsupported compression method: {name}",
        )
        _require(
            0 <= info.compress_size <= _EPUB_MAX_COMPRESSED_MEMBER_BYTES,
            f"EPUB member compressed size exceeds its resource limit: {name}",
        )
        role_limit = _epub_member_limit(name)
        _require(
            0 <= info.file_size <= role_limit,
            f"EPUB member uncompressed size exceeds its role resource limit: {name}",
        )
        if info.compress_size == 0:
            _require(
                info.file_size == 0,
                f"EPUB member has a zero compressed size with nonempty content: {name}",
            )
        else:
            _require(
                info.file_size
                <= info.compress_size * _EPUB_MAX_COMPRESSION_RATIO,
                f"EPUB member compression ratio exceeds its resource limit: {name}",
            )
        total_compressed += info.compress_size
        total_uncompressed += info.file_size
        entries[name] = info
    _require(
        total_compressed <= _EPUB_MAX_COMPRESSED_TOTAL_BYTES,
        "public fiction EPUB total compressed size exceeds its aggregate limit",
    )
    _require(
        total_uncompressed <= _EPUB_MAX_UNCOMPRESSED_TOTAL_BYTES,
        "public fiction EPUB total uncompressed size exceeds its aggregate limit",
    )
    _require(
        "OEBPS/cover.png" in entries
        and entries["OEBPS/cover.png"].file_size == public_cover_size,
        "embedded EPUB cover size differs from the governed public cover",
    )
    return infos, entries


def _read_epub_member(
    archive: zipfile.ZipFile,
    entries: dict[str, zipfile.ZipInfo],
    name: str,
    label: str,
    maximum_bytes: int,
) -> bytes:
    _require(name in entries, f"{label} is missing from the EPUB")
    info = entries[name]
    _require(info.file_size <= maximum_bytes, f"{label} is too large")
    try:
        with archive.open(info, "r") as stream:
            content = stream.read(maximum_bytes + 1)
    except (OSError, RuntimeError, zipfile.BadZipFile) as error:
        raise ValueError(f"{label} is unreadable") from error
    _require(
        len(content) == info.file_size and len(content) <= maximum_bytes,
        f"{label} decompressed size differs from its bounded declaration",
    )
    return content


def _whitespace(value: str | None) -> bool:
    return value is None or not value.strip()


def _exact_children(
    element: ET.Element, tags: list[str], label: str
) -> list[ET.Element]:
    children = list(element)
    _require(
        [child.tag for child in children] == tags,
        f"{label} has invalid structure or extra content",
    )
    _require(_whitespace(element.text), f"{label} has visible direct text")
    _require(
        all(_whitespace(child.tail) for child in children),
        f"{label} has visible tail text",
    )
    return children


def _exact_text_leaf(
    element: ET.Element,
    tag: str,
    attributes: dict[str, str],
    text: str,
    label: str,
) -> None:
    _require(
        element.tag == tag
        and element.attrib == attributes
        and not list(element)
        and (element.text or "") == text,
        f"{label} has invalid structure or content",
    )


def _xhtml_shell(
    document: ET.Element, title: str, language: str, label: str
) -> tuple[ET.Element, ET.Element]:
    _require(
        document.tag == f"{_XHTML}html"
        and document.attrib == {"lang": language},
        f"{label} has invalid html identity",
    )
    head, body = _exact_children(
        document, [f"{_XHTML}head", f"{_XHTML}body"], label
    )
    _require(
        not head.attrib and not body.attrib,
        f"{label} head and body must not have attributes",
    )
    meta, title_element, link = _exact_children(
        head,
        [f"{_XHTML}meta", f"{_XHTML}title", f"{_XHTML}link"],
        f"{label} head",
    )
    _exact_text_leaf(
        meta, f"{_XHTML}meta", {"charset": "utf-8"}, "", f"{label} charset"
    )
    _exact_text_leaf(
        title_element, f"{_XHTML}title", {}, title, f"{label} title"
    )
    _exact_text_leaf(
        link,
        f"{_XHTML}link",
        {"rel": "stylesheet", "type": "text/css", "href": "style.css"},
        "",
        f"{label} stylesheet",
    )
    return head, body


def _element_identity(element: ET.Element, *, include_tail: bool) -> tuple[object, ...]:
    return (
        element.tag,
        tuple(sorted(element.attrib.items())),
        element.text,
        element.tail if include_tail else None,
        tuple(
            _element_identity(child, include_tail=True) for child in list(element)
        ),
    )


def _require_builder_inline_paragraph(
    paragraph: ET.Element, canonical_markdown: str, label: str
) -> None:
    expected_markup = (
        f'<p xmlns="{_XHTML_NAMESPACE}">'
        f"{_builder_inline_html(canonical_markdown)}</p>"
    )
    try:
        expected = ET.fromstring(expected_markup)
    except ET.ParseError as error:
        raise ValueError(f"{label} canonical inline Markdown is invalid") from error
    _require(
        _element_identity(paragraph, include_tail=False)
        == _element_identity(expected, include_tail=False),
        f"{label} inline structure differs from canonical Markdown",
    )


def _validate_chapter_xhtml(
    document: ET.Element,
    title: str,
    paragraphs: tuple[str, ...],
    language: str,
    label: str,
) -> None:
    _head, body = _xhtml_shell(document, title, language, label)
    (section,) = _exact_children(body, [f"{_XHTML}section"], f"{label} body")
    _require(
        section.attrib == {_EPUB_TYPE: "chapter"},
        f"{label} section has invalid role",
    )
    children = _exact_children(
        section,
        [f"{_XHTML}h1"] + [f"{_XHTML}p"] * len(paragraphs),
        f"{label} section",
    )
    _exact_text_leaf(children[0], f"{_XHTML}h1", {}, title, f"{label} heading")
    for index, (paragraph, expected) in enumerate(
        zip(children[1:], paragraphs, strict=True), start=1
    ):
        _require_builder_inline_paragraph(
            paragraph,
            expected,
            f"{label} paragraph {index}",
        )


def _validate_titlepage_xhtml(
    document: ET.Element,
    title: str,
    subtitle: str,
    author: str,
    language: str,
) -> None:
    _head, body = _xhtml_shell(document, title, language, "EPUB titlepage")
    (section,) = _exact_children(
        body, [f"{_XHTML}section"], "EPUB titlepage body"
    )
    _require(
        section.attrib == {_EPUB_TYPE: "titlepage", "class": "title-page"},
        "EPUB titlepage section has invalid role",
    )
    tags = [f"{_XHTML}h1", f"{_XHTML}p"]
    if subtitle:
        tags.append(f"{_XHTML}p")
    children = _exact_children(section, tags, "EPUB titlepage section")
    _exact_text_leaf(children[0], f"{_XHTML}h1", {}, title, "EPUB titlepage heading")
    _exact_text_leaf(
        children[1],
        f"{_XHTML}p",
        {"class": "author"},
        f"by {author}",
        "EPUB titlepage author",
    )
    if subtitle:
        _exact_text_leaf(
            children[2],
            f"{_XHTML}p",
            {"class": "sub"},
            subtitle,
            "EPUB titlepage subtitle",
        )


def _validate_nav_xhtml(
    document: ET.Element,
    canonical: tuple[tuple[str, tuple[str, ...]], ...],
    language: str,
) -> None:
    _head, body = _xhtml_shell(
        document, "Table of Contents", language, "EPUB navigation"
    )
    (navigation,) = _exact_children(
        body, [f"{_XHTML}nav"], "EPUB navigation body"
    )
    _require(
        navigation.attrib == {_EPUB_TYPE: "toc", "id": "toc"},
        "EPUB navigation has invalid role",
    )
    heading, ordered = _exact_children(
        navigation, [f"{_XHTML}h1", f"{_XHTML}ol"], "EPUB navigation"
    )
    _require(not ordered.attrib, "EPUB navigation list has invalid attributes")
    _exact_text_leaf(
        heading, f"{_XHTML}h1", {}, "Table of Contents", "EPUB navigation heading"
    )
    items = _exact_children(
        ordered, [f"{_XHTML}li"] * len(canonical), "EPUB navigation list"
    )
    for index, (item, (chapter_title, _paragraphs)) in enumerate(
        zip(items, canonical, strict=True)
    ):
        _require(not item.attrib, "EPUB navigation item has invalid attributes")
        (link,) = _exact_children(item, [f"{_XHTML}a"], "EPUB navigation item")
        _exact_text_leaf(
            link,
            f"{_XHTML}a",
            {"href": f"chap{index:02d}.xhtml"},
            chapter_title,
            f"EPUB navigation item {index + 1}",
        )


def _validate_cover_xhtml(
    document: ET.Element,
    title: str,
    language: str,
    cover_name: str,
) -> None:
    _require(
        document.tag == f"{_XHTML}html"
        and document.attrib == {"lang": language},
        "EPUB cover has invalid html identity",
    )
    head, body = _exact_children(
        document, [f"{_XHTML}head", f"{_XHTML}body"], "EPUB cover"
    )
    _require(
        not head.attrib and not body.attrib,
        "EPUB cover head and body must not have attributes",
    )
    meta, title_element, style = _exact_children(
        head,
        [f"{_XHTML}meta", f"{_XHTML}title", f"{_XHTML}style"],
        "EPUB cover head",
    )
    _exact_text_leaf(
        meta, f"{_XHTML}meta", {"charset": "utf-8"}, "", "EPUB cover charset"
    )
    _exact_text_leaf(
        title_element, f"{_XHTML}title", {}, "Cover", "EPUB cover title"
    )
    _exact_text_leaf(
        style,
        f"{_XHTML}style",
        {},
        "html,body{margin:0;padding:0;height:100%}img{display:block;width:100%;height:auto}",
        "EPUB cover style",
    )
    (section,) = _exact_children(body, [f"{_XHTML}section"], "EPUB cover body")
    _require(
        section.attrib == {_EPUB_TYPE: "cover"},
        "EPUB cover section has invalid role",
    )
    (cover_image,) = _exact_children(
        section, [f"{_XHTML}img"], "EPUB cover section"
    )
    _exact_text_leaf(
        cover_image,
        f"{_XHTML}img",
        {"src": cover_name, "alt": f"{title} cover"},
        "",
        "EPUB cover image",
    )


def _validate_ncx(
    root: ET.Element,
    uid: str,
    title: str,
    canonical: tuple[tuple[str, tuple[str, ...]], ...],
) -> None:
    _require(
        root.tag == f"{_NCX}ncx" and root.attrib == {"version": "2005-1"},
        "EPUB NCX has invalid identity",
    )
    head, doc_title, nav_map = _exact_children(
        root,
        [f"{_NCX}head", f"{_NCX}docTitle", f"{_NCX}navMap"],
        "EPUB NCX",
    )
    _require(
        not head.attrib and not doc_title.attrib and not nav_map.attrib,
        "EPUB NCX structural roles have invalid attributes",
    )
    (meta,) = _exact_children(head, [f"{_NCX}meta"], "EPUB NCX head")
    _exact_text_leaf(
        meta,
        f"{_NCX}meta",
        {"name": "dtb:uid", "content": uid},
        "",
        "EPUB NCX uid",
    )
    (title_text,) = _exact_children(
        doc_title, [f"{_NCX}text"], "EPUB NCX title"
    )
    _exact_text_leaf(
        title_text, f"{_NCX}text", {}, title, "EPUB NCX title text"
    )
    nav_points = _exact_children(
        nav_map, [f"{_NCX}navPoint"] * len(canonical), "EPUB NCX navigation"
    )
    for index, (point, (chapter_title, _paragraphs)) in enumerate(
        zip(nav_points, canonical, strict=True)
    ):
        _require(
            point.attrib == {"id": f"np{index}", "playOrder": str(index + 1)},
            f"EPUB NCX item {index + 1} has invalid identity",
        )
        label, content = _exact_children(
            point,
            [f"{_NCX}navLabel", f"{_NCX}content"],
            f"EPUB NCX item {index + 1}",
        )
        _require(
            not label.attrib,
            f"EPUB NCX item {index + 1} label has invalid attributes",
        )
        (text_element,) = _exact_children(
            label, [f"{_NCX}text"], f"EPUB NCX item {index + 1} label"
        )
        _exact_text_leaf(
            text_element,
            f"{_NCX}text",
            {},
            chapter_title,
            f"EPUB NCX item {index + 1} label",
        )
        _exact_text_leaf(
            content,
            f"{_NCX}content",
            {"src": f"chap{index:02d}.xhtml"},
            "",
            f"EPUB NCX item {index + 1} target",
        )


def _epub_story(
    epub: Path,
    canonical: tuple[tuple[str, tuple[str, ...]], ...],
    title: str,
    subtitle: str,
    author: str,
    contributor: str,
    public_cover: _FileSnapshot,
) -> None:
    infos, entries = _inspect_epub_archive(
        epub, public_cover_size=public_cover.size
    )
    try:
        archive = zipfile.ZipFile(epub)
    except (OSError, zipfile.BadZipFile) as error:
        raise ValueError("public fiction EPUB is not a valid zip archive") from error
    with archive:
        _require(
            bool(infos)
            and infos[0].filename == "mimetype"
            and infos[0].compress_type == zipfile.ZIP_STORED
            and _read_epub_member(
                archive, entries, "mimetype", "EPUB mimetype", 64
            )
            == b"application/epub+zip",
            "public fiction EPUB has an invalid mimetype entry",
        )

        container = _epub_xml(
            archive, entries, "META-INF/container.xml", "EPUB container"
        )
        _require(
            container.tag == f"{_CONTAINER}container"
            and container.attrib == {"version": "1.0"},
            "EPUB container has invalid identity",
        )
        (rootfiles,) = _exact_children(
            container, [f"{_CONTAINER}rootfiles"], "EPUB container"
        )
        _require(not rootfiles.attrib, "EPUB container rootfiles has attributes")
        (rootfile,) = _exact_children(
            rootfiles, [f"{_CONTAINER}rootfile"], "EPUB container rootfiles"
        )
        opf_path = _safe_epub_path(
            rootfile.get("full-path", ""), "EPUB package path"
        )
        _require(
            opf_path == "OEBPS/content.opf"
            and rootfile.attrib
            == {
                "full-path": "OEBPS/content.opf",
                "media-type": "application/oebps-package+xml",
            },
            "EPUB container does not match the unchanged builder structure",
        )
        _exact_text_leaf(
            rootfile,
            f"{_CONTAINER}rootfile",
            {
                "full-path": "OEBPS/content.opf",
                "media-type": "application/oebps-package+xml",
            },
            "",
            "EPUB container rootfile",
        )
        package = _epub_xml(archive, entries, opf_path, "EPUB package")
        _require(
            package.tag == f"{_OPF}package"
            and package.attrib == {"version": "3.0", "unique-identifier": "bookid"},
            "EPUB package identity is invalid",
        )
        metadata, manifest, spine = _exact_children(
            package,
            [f"{_OPF}metadata", f"{_OPF}manifest", f"{_OPF}spine"],
            "EPUB package",
        )
        _require(
            not metadata.attrib and not manifest.attrib,
            "EPUB metadata and manifest must not have attributes",
        )

        items: dict[str, tuple[str, str, str | None]] = {}
        hrefs: set[str] = set()
        manifest_items = _exact_children(
            manifest,
            [f"{_OPF}item"] * len(list(manifest)),
            "EPUB manifest",
        )
        for item in manifest_items:
            _require(item.tag == f"{_OPF}item", "EPUB manifest is invalid")
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
            allowed_keys = {"id", "href", "media-type"}
            if "properties" in item.attrib:
                allowed_keys.add("properties")
            _require(
                set(item.attrib) == allowed_keys
                and _whitespace(item.text)
                and not list(item),
                "EPUB manifest item has extra attributes or content",
            )
            items[item_id] = (href, media_type, item.get("properties"))

        chapter_ids = [f"chap{index:02d}" for index in range(len(canonical))]
        has_cover = "cover-image" in items or "coverpage" in items
        _require(
            has_cover and {"cover-image", "coverpage"} <= set(items),
            "EPUB must contain the governed public cover roles",
        )
        expected_items: dict[str, tuple[str, str, str | None]] = {
            "css": ("OEBPS/style.css", "text/css", None),
            "titlepage": (
                "OEBPS/titlepage.xhtml",
                "application/xhtml+xml",
                None,
            ),
            "nav": ("OEBPS/nav.xhtml", "application/xhtml+xml", "nav"),
            "ncx": ("OEBPS/toc.ncx", "application/x-dtbncx+xml", None),
        }
        expected_items.update(
            {
                chapter_id: (
                    f"OEBPS/{chapter_id}.xhtml",
                    "application/xhtml+xml",
                    None,
                )
                for chapter_id in chapter_ids
            }
        )
        cover_name = ""
        if has_cover:
            cover_path, cover_media, cover_properties = items["cover-image"]
            cover_name = PurePosixPath(cover_path).name
            _require(
                (cover_name, cover_media, cover_properties)
                == ("cover.png", "image/png", "cover-image"),
                "EPUB cover image manifest item is invalid",
            )
            expected_items["cover-image"] = (
                f"OEBPS/{cover_name}",
                cover_media,
                "cover-image",
            )
            expected_items["coverpage"] = (
                "OEBPS/cover.xhtml",
                "application/xhtml+xml",
                None,
            )
        _require(
            items == expected_items,
            "public fiction EPUB manifest differs from the unchanged builder roles",
        )
        expected_entries = {
            "mimetype",
            "META-INF/container.xml",
            opf_path,
            *(href for href, _media, _properties in expected_items.values()),
        }
        _require(
            set(entries) == expected_entries,
            "public fiction EPUB contains an extra or missing package file",
        )
        _require(
            _read_epub_member(
                archive,
                entries,
                "OEBPS/style.css",
                "EPUB stylesheet",
                _EPUB_MAX_CSS_BYTES,
            )
            == _BUILDER_EPUB_CSS,
            "public fiction EPUB stylesheet differs from the unchanged builder",
        )
        assert public_cover.content is not None
        embedded_cover = _read_epub_member(
            archive,
            entries,
            "OEBPS/cover.png",
            "embedded EPUB cover",
            _EPUB_MAX_COVER_BYTES,
        )
        _require(
            len(embedded_cover) == public_cover.size
            and hashlib.sha256(embedded_cover).hexdigest() == public_cover.sha256
            and embedded_cover == public_cover.content,
            "embedded EPUB cover bytes differ from the governed public cover",
        )

        _require(spine.attrib == {"toc": "ncx"}, "EPUB spine identity is invalid")
        spine_ids: list[str] = []
        spine_items = _exact_children(
            spine,
            [f"{_OPF}itemref"] * len(list(spine)),
            "EPUB spine",
        )
        for itemref in spine_items:
            _require(itemref.tag == f"{_OPF}itemref", "EPUB spine is invalid")
            item_id = itemref.get("idref")
            _require(
                isinstance(item_id, str)
                and item_id in items
                and item_id not in spine_ids,
                "EPUB spine item identity is invalid",
            )
            _require(
                itemref.attrib == {"idref": item_id}
                and not list(itemref)
                and _whitespace(itemref.text),
                "EPUB spine itemref has invalid attributes; narrated chapters cannot be linear=no",
            )
            spine_ids.append(item_id)
        expected_spine = (["coverpage"] if has_cover else []) + [
            "titlepage",
            *chapter_ids,
        ]
        _require(
            spine_ids == expected_spine,
            "public fiction EPUB spine differs from the complete narrated story",
        )

        metadata_tags = [
            f"{_DC}identifier",
            f"{_DC}title",
            f"{_DC}creator",
            f"{_DC}contributor",
            f"{_DC}language",
            f"{_OPF}meta",
        ]
        if subtitle:
            metadata_tags.append(f"{_OPF}meta")
        if has_cover:
            metadata_tags.append(f"{_OPF}meta")
        metadata_children = _exact_children(metadata, metadata_tags, "EPUB metadata")
        identifier, title_meta, creator, contributor_meta, language_meta = metadata_children[:5]
        uid = identifier.text or ""
        try:
            parsed_uid = uuid.UUID(uid.removeprefix("urn:uuid:"))
        except (ValueError, AttributeError) as error:
            raise ValueError("EPUB identifier must be a valid urn:uuid UUID") from error
        _require(
            uid == f"urn:uuid:{parsed_uid}",
            "EPUB identifier must be a canonical urn:uuid UUID",
        )
        _exact_text_leaf(
            identifier, f"{_DC}identifier", {"id": "bookid"}, uid, "EPUB identifier"
        )
        _exact_text_leaf(title_meta, f"{_DC}title", {}, title, "EPUB metadata title")
        _exact_text_leaf(creator, f"{_DC}creator", {}, author, "EPUB metadata author")
        _exact_text_leaf(
            contributor_meta,
            f"{_DC}contributor",
            {},
            contributor,
            "EPUB metadata contributor",
        )
        language = language_meta.text or ""
        _require(
            language == "en",
            "EPUB language must match the unchanged fiction builder language",
        )
        _exact_text_leaf(
            language_meta, f"{_DC}language", {}, language, "EPUB metadata language"
        )
        meta_index = 5
        _exact_text_leaf(
            metadata_children[meta_index],
            f"{_OPF}meta",
            {"property": "dcterms:modified"},
            "2026-01-01T00:00:00Z",
            "EPUB modified metadata",
        )
        meta_index += 1
        if subtitle:
            _exact_text_leaf(
                metadata_children[meta_index],
                f"{_OPF}meta",
                {"name": "calibre:subtitle", "content": subtitle},
                "",
                "EPUB subtitle metadata",
            )
            meta_index += 1
        if has_cover:
            _exact_text_leaf(
                metadata_children[meta_index],
                f"{_OPF}meta",
                {"name": "cover", "content": "cover-image"},
                "",
                "EPUB cover metadata",
            )

        _validate_titlepage_xhtml(
            _epub_xml(
                archive, entries, "OEBPS/titlepage.xhtml", "EPUB titlepage"
            ),
            title,
            subtitle,
            author,
            language,
        )
        _validate_nav_xhtml(
            _epub_xml(archive, entries, "OEBPS/nav.xhtml", "EPUB navigation"),
            canonical,
            language,
        )
        if has_cover:
            _validate_cover_xhtml(
                _epub_xml(archive, entries, "OEBPS/cover.xhtml", "EPUB cover"),
                title,
                language,
                cover_name,
            )
        for index, (chapter_title, paragraphs) in enumerate(canonical):
            path = f"OEBPS/chap{index:02d}.xhtml"
            _validate_chapter_xhtml(
                _epub_xml(archive, entries, path, f"EPUB chapter {index + 1}"),
                chapter_title,
                paragraphs,
                language,
                f"EPUB chapter {index + 1}",
            )
        _validate_ncx(
            _epub_xml(archive, entries, "OEBPS/toc.ncx", "EPUB NCX"),
            uid,
            title,
            canonical,
        )


def _verify_public_story_content(
    manuscript: _FileSnapshot,
    epub: Path,
    chapters_dir: Path,
    private_snapshots: list[_FileSnapshot],
    author: str,
    contributor: str,
    public_cover: _FileSnapshot,
) -> None:
    canonical = _canonical_story(chapters_dir, private_snapshots)
    title, subtitle = _builder_markdown_identity(manuscript, canonical, author)
    _epub_story(
        epub,
        canonical,
        title,
        subtitle,
        author,
        contributor,
        public_cover,
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


def _canonical_chapter_filenames(chapters_dir: Path) -> tuple[str, ...]:
    try:
        return tuple(
            sorted(
                path.name
                for path in chapters_dir.iterdir()
                if path.name.startswith("ch") and path.suffix == ".md"
            )
        )
    except OSError as error:
        raise ValueError("canonical fiction chapter coverage is unreadable") from error


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
    initial_chapter_filenames = _canonical_chapter_filenames(chapters_dir)
    _require(
        bool(initial_chapter_filenames),
        "canonical fiction chapter coverage is empty",
    )

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
        cover_snapshot = next(
            snapshot
            for snapshot in artifact_snapshots
            if snapshot.path.name == "cover.png"
        )
        _inspect_epub_archive(
            epub_probe_copy, public_cover_size=cover_snapshot.size
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
            receipt["author"],
            receipt["contributor"],
            cover_snapshot,
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
        _require_snapshot_unchanged(
            snapshot,
            snapshot.path.name,
            max_bytes=(
                _EPUB_MAX_COVER_BYTES if snapshot is cover_snapshot else None
            ),
        )
    _require(
        _canonical_chapter_filenames(chapters_dir) == initial_chapter_filenames,
        "canonical fiction chapter coverage changed during verification",
    )


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
