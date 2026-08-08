#!/usr/bin/env python3
"""Verify a sanitized, explicitly authorized public audiobook package."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ECHO_SCRIPT_DIRECTORY = (
    Path(__file__).resolve().parents[2] / "skills" / "echo-narration" / "scripts"
)
if str(ECHO_SCRIPT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(ECHO_SCRIPT_DIRECTORY))

from echo_pronunciation_state import RENDERER_IDENTITY_KEYS, RUN_ID_PATTERN

FICTION_VOICE_DIRECTORY = (
    Path(__file__).resolve().parents[2] / "skills" / "fiction-audiobook" / "scripts"
)
if str(FICTION_VOICE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(FICTION_VOICE_DIRECTORY))

from fiction_voice_preferences import validate_completed_cast

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
_ECHO_SUCCESS_FIELDS = {
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


def _snapshot_file(path: Path, label: str, *, capture: bool = False) -> _FileSnapshot:
    _reject_symlink_ancestors(path, label)
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise ValueError(f"{label} is not a readable regular file") from error
    chunks: list[bytes] | None = [] if capture else None
    digest = hashlib.sha256()
    try:
        before = os.fstat(descriptor)
        _require(stat.S_ISREG(before.st_mode), f"{label} must be a regular file")
        with os.fdopen(descriptor, "rb") as stream:
            descriptor = -1
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
                if chunks is not None:
                    chunks.append(chunk)
            after = os.fstat(stream.fileno())
        current = os.lstat(path)
    except OSError as error:
        raise ValueError(f"{label} changed during verification") from error
    finally:
        if descriptor >= 0:
            os.close(descriptor)
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
    book_dir: Path, receipt: dict[str, object], slug: str
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
            path, f"fiction {name} artifact", capture=name == "alignment"
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
    receipt: dict[str, object], slug: str, release_m4b: Path
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
    snapshot = _snapshot_file(release_m4b, "release M4B")
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
                    )
                )
    run_root = chapters_dir.parent
    for section in (fiction.get("artifacts"), fiction.get("buildOutputs")):
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
    _verify_echo_success_provenance(success, echo_success_receipt, cast)
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
    verified_fiction = verify_fiction_receipt(chapters_dir, fiction_receipt)
    for snapshot in fiction_inputs:
        _require_snapshot_unchanged(snapshot, "fiction private input")
    snapshots.extend(fiction_inputs)
    build_outputs = verified_fiction.get("buildOutputs")
    _require(
        isinstance(build_outputs, dict),
        "fiction receipt must bind private build outputs",
    )
    _require(
        build_outputs.get("slug") == slug,
        "fiction private build slug does not match publication",
    )
    for name, artifact_name, label in (
        ("manuscript", "manuscript", "manuscript"),
        ("epub", "epub", "EPUB"),
    ):
        record = build_outputs.get(name)
        _require(isinstance(record, dict), f"fiction private build {label} is missing")
        _require(
            record.get("sha256") == artifact_hashes[artifact_name],
            f"fiction private build {label} differs from public {label}",
        )
    return snapshots


def _verify_echo_success_provenance(
    success: dict[str, object], receipt_path: Path, cast: dict[str, object]
) -> None:
    expected_fields = set(_ECHO_SUCCESS_FIELDS)
    has_reel = "reelFileName" in success or "reelSHA256" in success
    if has_reel:
        expected_fields.update({"reelFileName", "reelSHA256"})
    _require(
        set(success) == expected_fields,
        "Echo success receipt must contain exact governed provenance fields",
    )
    _require(
        type(success.get("schemaVersion")) is int
        and success["schemaVersion"] == 3,
        "Echo success receipt schemaVersion must be integer 3",
    )
    attempt_id = _require_sha256(success.get("attemptID"), "Echo attemptID")
    run_id = success.get("runID")
    _require(
        isinstance(run_id, str) and RUN_ID_PATTERN.fullmatch(run_id) is not None,
        "Echo success receipt runID is invalid",
    )
    plan_id = cast.get("voicePlanID")
    _require(
        isinstance(plan_id, str) and run_id.endswith(f"-{plan_id}"),
        "Echo runID does not bind the cast voicePlanID",
    )
    _require(
        receipt_path.name == f"echo-render-success-{run_id}-{attempt_id}.json",
        "Echo success receipt filename is not derived from run and attempt",
    )
    _require(
        success.get("artifactRelativePath")
        == f"echo-renders/{run_id}/{attempt_id}",
        "Echo artifactRelativePath is not derived from run and attempt",
    )
    _require(
        success.get("inputReceiptFileName") == f"echo-render-inputs-{run_id}.env",
        "Echo input receipt filename is not derived from runID",
    )
    _require(
        success.get("resumeStateFileName") == f"echo-resume-state-{run_id}.json",
        "Echo resume-state filename is not derived from runID",
    )
    for field in (
        "attemptReceiptSHA256",
        "inputReceiptSHA256",
        "sourceEPUBSHA256",
        "resumeStateSHA256",
        "audiobookSHA256",
        "sidecarSHA256",
        "auditSHA256",
    ):
        _require_sha256(success.get(field), f"Echo success receipt {field}")
    if has_reel:
        _require_sha256(success.get("reelSHA256"), "Echo success receipt reelSHA256")
    for field in ("auditFileName", "reelFileName"):
        if field in success:
            filename = success[field]
            _require(
                isinstance(filename, str)
                and bool(filename)
                and Path(filename).name == filename,
                f"Echo success receipt {field} must be a filename",
            )

    _require(
        type(success.get("rendererSchemaVersion")) is int
        and success["rendererSchemaVersion"] == 1,
        "Echo rendererSchemaVersion must be integer 1",
    )
    for field in ("rendererRoot", "rendererBuildRoot"):
        value = success.get(field)
        _require(
            isinstance(value, str) and Path(value).is_absolute(),
            f"Echo success receipt {field} must be an absolute path",
        )
    for field in ("installerSourceSHA", "echoSourceSHA"):
        value = success.get(field)
        _require(
            isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value) is not None,
            f"Echo success receipt {field} must be a lowercase Git SHA",
        )
    for field in (
        "rendererManifestSHA256",
        "echoCLI_SHA256",
        "echoResourcesSHA256",
    ):
        _require_sha256(success.get(field), f"Echo success receipt {field}")
    _require(
        type(success.get("echoRenderVersion")) is int
        and success["echoRenderVersion"] >= 12,
        "Echo render version must be an integer of at least 12",
    )
    policy = success.get("modelPolicyRevision")
    _require(
        isinstance(policy, str)
        and bool(policy)
        and "\n" not in policy
        and "\r" not in policy,
        "Echo modelPolicyRevision must be nonempty and single-line",
    )
    _require(
        type(success.get("modelExpectedByteCount")) is int
        and success["modelExpectedByteCount"] > 0,
        "Echo modelExpectedByteCount must be a positive integer",
    )
    _require(
        success.get("modelBytesAttested") is False,
        "Echo modelBytesAttested must be false",
    )
    expected_run_id = (
        f"{success['sourceEPUBSHA256'][:12]}-{success['echoCLI_SHA256'][:12]}-"
        f"{success['echoResourcesSHA256'][:12]}-"
        f"{success['rendererManifestSHA256'][:12]}-"
        f"{success['echoSourceSHA']}-{plan_id}"
    )
    _require(
        run_id == expected_run_id,
        "Echo success receipt runID does not match source EPUB and renderer provenance",
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
    artifact_hashes, artifact_snapshots = _verify_fiction_artifacts(
        book_dir, receipt, slug
    )
    release_hash, release_snapshot = _verify_release(receipt, slug, release_m4b)
    epub_snapshot = next(
        snapshot
        for snapshot in artifact_snapshots
        if snapshot.path.name == f"{slug}.epub"
    )
    _probe_fiction_media(
        book_dir / f"{slug}.epub",
        release_m4b,
        epub_snapshot,
        release_snapshot,
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
