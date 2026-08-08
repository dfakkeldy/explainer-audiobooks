#!/usr/bin/env python3
"""Verify a sanitized, explicitly authorized public audiobook package."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
from pathlib import Path

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


def reject_private_values(value: object, location: str = "publication.json") -> None:
    """Reject absolute local references recursively from public JSON values."""
    if isinstance(value, str):
        if value.startswith("/") or value.casefold().startswith("file://") or _WINDOWS_ABSOLUTE.match(value):
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
    _require(not path.is_symlink(), f"{label} must not be a symlink")
    _require(path.is_file(), f"{label} must be a regular file")


def _require_regular_directory(path: Path, label: str) -> None:
    _require(not path.is_symlink(), f"{label} must not be a symlink")
    _require(path.is_dir(), f"{label} must be a directory")
    for child in path.rglob("*"):
        _require(not child.is_symlink(), f"{label} must not contain a symlink: {child}")


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
) -> dict[str, str]:
    artifacts = receipt.get("artifacts")
    _require(isinstance(artifacts, dict), "fiction artifacts must be an object")
    _require(
        set(artifacts) == set(_FICTION_ARTIFACTS),
        "fiction artifacts must contain exactly the four canonical artifacts",
    )
    verified: dict[str, str] = {}
    for name, filename_for_slug in _FICTION_ARTIFACTS.items():
        record = artifacts[name]
        _require(isinstance(record, dict), f"fiction {name} artifact must be an object")
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
        if name == "alignment":
            alignment = _read_json(path, "fiction alignment")
            reject_private_values(alignment, "fiction alignment")
            _require(
                isinstance(alignment, (list, dict)) and bool(alignment),
                "fiction alignment must be non-empty JSON",
            )
        actual_hash = _sha256_file(path)
        _require(
            actual_hash == expected_hash,
            f"fiction {name} SHA-256 does not match",
        )
        verified[name] = actual_hash
    return verified


def _probe_fiction_media(epub: Path, release_m4b: Path) -> None:
    try:
        subprocess.run(
            ["unzip", "-t", str(epub)],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise ValueError("fiction EPUB failed unzip -t") from error
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
    try:
        duration = float(media["format"]["duration"])
        _require(
            math.isfinite(duration) and duration > 0,
            "fiction M4B duration must be finite and positive",
        )
        _require(
            isinstance(media["chapters"], list) and bool(media["chapters"]),
            "fiction M4B chapters are required",
        )
    except (KeyError, TypeError, ValueError) as error:
        if isinstance(error, ValueError) and str(error).startswith("fiction M4B"):
            raise
        raise ValueError("fiction M4B ffprobe output lacks duration or chapters") from error


def _verify_release(
    receipt: dict[str, object], slug: str, release_m4b: Path
) -> str:
    release = receipt.get("release")
    _require(isinstance(release, dict), "release must be an object")
    tag = release.get("tag")
    _require(isinstance(tag, str) and bool(tag.strip()), "release tag is required")
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
    actual_hash = _sha256_file(release_m4b)
    _require(actual_hash == expected_hash, "release M4B SHA-256 does not match")
    return actual_hash


def _verify_private_evidence(
    receipt: dict[str, object],
    slug: str,
    artifact_hashes: dict[str, str],
    release_hash: str,
    voice_cast: Path,
    fiction_receipt: Path,
    chapters_dir: Path,
    echo_success_receipt: Path,
) -> None:
    private = receipt.get("privateEvidence")
    _require(isinstance(private, dict), "privateEvidence must be an object")
    _require(
        set(private) == _PRIVATE_EVIDENCE_FIELDS,
        "privateEvidence must contain exactly the required hashes",
    )
    for field in _PRIVATE_EVIDENCE_FIELDS:
        _require_sha256(private.get(field), f"privateEvidence {field}")

    cast = _read_json(voice_cast, "voice cast")
    _require(isinstance(cast, dict), "voice cast must be an object")
    _require(
        _sha256_file(voice_cast) == private["voiceCastSHA256"],
        "voice cast SHA-256 does not match privateEvidence",
    )
    _require(cast.get("schemaVersion") == 1, "voice cast schemaVersion must be 1")
    _require(cast.get("slug") == slug, "voice cast slug does not match publication")
    plan_hash = _require_sha256(cast.get("voicePlanSHA256"), "voice cast voicePlanSHA256")
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

    success = _read_json(echo_success_receipt, "Echo success receipt")
    _require(isinstance(success, dict), "Echo success receipt must be an object")
    _require(
        _sha256_file(echo_success_receipt) == private["echoSuccessReceiptSHA256"],
        "Echo success receipt SHA-256 does not match privateEvidence",
    )
    expected_success = {
        "sourceEPUBFileName": f"{slug}.epub",
        "sourceEPUBSHA256": artifact_hashes["epub"],
        "audiobookFileName": f"{slug}.m4b",
        "audiobookSHA256": release_hash,
        "sidecarFileName": f"{slug}.alignment.json",
        "sidecarSHA256": artifact_hashes["alignment"],
        "voicePlanSHA256": plan_hash,
    }
    for field, expected in expected_success.items():
        _require(
            success.get(field) == expected,
            f"Echo success receipt {field} does not match governed artifacts",
        )

    _read_json(fiction_receipt, "fiction production receipt")
    _require(
        _sha256_file(fiction_receipt) == private["fictionReceiptSHA256"],
        "fiction receipt SHA-256 does not match privateEvidence",
    )
    verify_fiction_receipt(chapters_dir, fiction_receipt)


def _verify_fiction_readme(book_dir: Path) -> None:
    readme = book_dir / "README.md"
    try:
        text = readme.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise ValueError("fiction README is missing or unreadable") from error
    _require(
        FICTION_DISCLOSURE in text,
        "fiction README must include the approved disclosure",
    )


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

    receipt = load_receipt(book_dir)
    slug = _verify_fiction_receipt_fields(receipt)
    _verify_fiction_public_root(book_dir, slug)
    artifact_hashes = _verify_fiction_artifacts(book_dir, receipt, slug)
    release_hash = _verify_release(receipt, slug, release_m4b)
    _probe_fiction_media(
        book_dir / f"{slug}.epub",
        release_m4b,
    )
    _verify_private_evidence(
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
    _verify_fiction_readme(book_dir)


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
