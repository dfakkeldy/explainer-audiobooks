#!/usr/bin/env python3
"""Verify public audiobook recovery evidence without exposing archive paths."""

from __future__ import annotations

import argparse
import json
import hashlib
import importlib
import math
import os
import re
import sys
import tempfile
import zipfile
from dataclasses import asdict
from pathlib import Path

from PIL import Image, UnidentifiedImageError


_WINDOWS_ABSOLUTE = re.compile(r"^[A-Za-z]:[\\/]")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_CANDIDATE_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

LEGACY_PAIR_FIELDS = {
    "schema_version",
    "book_slug",
    "edition_id",
    "candidate_id",
    "direction_name",
    "selection_source",
    "privacy",
    "portrait",
    "square",
}

RECOVERED_SLUGS = (
    "echo-from-the-inside",
    "why-it-feels-right",
    "you-are-the-architect",
    "the-bug-is-a-clue",
    "tests-first",
    "git-happens",
    "findable",
    "the-voice-in-the-machine",
)
REMUXED_SLUGS = RECOVERED_SLUGS + ("rodents-in-the-walls",)
LEGACY_PAIR_SLUGS = (
    "you-are-the-architect",
    "the-bug-is-a-clue",
    "tests-first",
    "git-happens",
    "the-voice-in-the-machine",
    "rodents-in-the-walls",
)
MAX_GIT_BLOB_BYTES = 100 * 1024 * 1024

COMMON_RECORD_FIELDS = {
    "slug",
    "source_m4b_sha256",
    "final_m4b_path",
    "final_m4b_sha256",
    "epub_path",
    "epub_sha256",
    "portrait_sha256",
    "square_sha256",
    "source_media_signature",
    "final_media_signature",
}
RECOVERED_RECORD_FIELDS = COMMON_RECORD_FIELDS | {
    "source_sidecar_sha256",
    "final_sidecar_path",
    "final_sidecar_sha256",
    "anchor_count",
    "exported_block_count",
    "resolved_anchor_count",
}


def validate_public_json(value: object) -> None:
    if isinstance(value, str):
        if value.startswith(("/", "file://")) or _WINDOWS_ABSOLUTE.match(value):
            raise ValueError(f"public JSON contains an absolute path: {value}")
        return
    if isinstance(value, list):
        for item in value:
            validate_public_json(item)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            validate_public_json(key)
            validate_public_json(item)


def _read_json(path: Path, label: str) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"{label} is not readable JSON: {path}") from error


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as error:
        raise ValueError(f"file is not readable: {path}") from error
    return digest.hexdigest()


def _image_dimensions(path: Path, label: str) -> tuple[int, int]:
    try:
        with Image.open(path) as image:
            image.load()
            if image.mode != "RGB":
                raise ValueError(f"{label} must use RGB colour mode")
            return image.size
    except (OSError, UnidentifiedImageError) as error:
        raise ValueError(f"{label} is not a readable image: {path}") from error


def _require_exact_fields(
    value: object, expected: set[str], label: str
) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    actual = set(value)
    if actual != expected:
        raise ValueError(
            f"{label} fields differ: missing={sorted(expected - actual)}, "
            f"unexpected={sorted(actual - expected)}"
        )
    return value


def _require_hash(value: object, label: str) -> str:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise ValueError(f"{label} must be a lowercase SHA-256")
    return value


def _resolve_named_file(book_dir: Path, value: object, expected: str, label: str) -> Path:
    if value != expected:
        raise ValueError(f"{label} path must be {expected}")
    path = book_dir / expected
    if not path.is_file():
        raise ValueError(f"{label} is missing: {path}")
    return path


def _epub_cover_sha256(epub_path: Path, member: str) -> str:
    try:
        with zipfile.ZipFile(epub_path) as archive:
            return hashlib.sha256(archive.read(member)).hexdigest()
    except (OSError, KeyError, zipfile.BadZipFile) as error:
        raise ValueError(f"EPUB cover is not readable: {epub_path}!/{member}") from error


def _write_json_atomic(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def _media_helpers() -> tuple[object, object, object]:
    scripts_directory = str(Path(__file__).resolve().parent)
    inserted = scripts_directory not in sys.path
    if inserted:
        sys.path.insert(0, scripts_directory)
    try:
        replacement = importlib.import_module("replace_m4b_cover")
        receipts = importlib.import_module("cover_receipts")
    finally:
        if inserted:
            sys.path.remove(scripts_directory)
    return (
        replacement.media_signature,
        receipts.normalized_image_sha256,
        receipts.normalized_m4b_art_sha256,
    )


def _signature_payload(signature: object) -> dict[str, object]:
    return json.loads(json.dumps(asdict(signature), sort_keys=True))


def _relative_file(repo_root: Path, path: Path, label: str) -> str:
    try:
        return path.resolve(strict=True).relative_to(repo_root.resolve(strict=True)).as_posix()
    except (OSError, RuntimeError, ValueError) as error:
        raise ValueError(f"{label} must be a file inside the repository") from error


def verify_block_parity(sidecar_path: Path, blocks_path: Path) -> tuple[int, int]:
    sidecar = _read_json(sidecar_path, "alignment sidecar")
    blocks_document = _read_json(blocks_path, "block export")
    if not isinstance(sidecar, list) or not sidecar:
        raise ValueError("alignment sidecar must be a non-empty list")
    if not isinstance(blocks_document, dict):
        raise ValueError("block export must be an object")
    blocks = blocks_document.get("blocks")
    if not isinstance(blocks, list) or not blocks:
        raise ValueError("block export blocks must be a non-empty list")

    block_ids = {
        block.get("id")
        for block in blocks
        if isinstance(block, dict) and isinstance(block.get("id"), str)
    }
    previous_timestamp = -math.inf
    resolved = 0
    for index, anchor in enumerate(sidecar):
        if not isinstance(anchor, dict):
            raise ValueError(f"alignment anchor {index} must be an object")
        block_id = anchor.get("blockId")
        timestamp = anchor.get("timestamp")
        if not isinstance(block_id, str) or not block_id:
            raise ValueError(f"alignment anchor {index} has an invalid blockId")
        if (
            isinstance(timestamp, bool)
            or not isinstance(timestamp, (int, float))
            or not math.isfinite(timestamp)
        ):
            raise ValueError(f"alignment anchor {index} has an invalid timestamp")
        if timestamp < previous_timestamp:
            raise ValueError("alignment timestamps must be monotonic")
        previous_timestamp = timestamp
        if block_id not in block_ids:
            raise ValueError(f"unresolved anchor {index}: {block_id}")
        resolved += 1
    return len(sidecar), resolved


def verify_legacy_cover_pair(book_dir: Path, receipt_path: Path) -> None:
    book_dir = book_dir.resolve()
    receipt_path = receipt_path.resolve()
    if receipt_path.parent != book_dir:
        raise ValueError("legacy pair receipt must be inside the book directory")
    payload = _require_exact_fields(
        _read_json(receipt_path, "legacy pair receipt"),
        LEGACY_PAIR_FIELDS,
        "legacy pair receipt",
    )
    validate_public_json(payload)
    if payload["schema_version"] != 1 or isinstance(payload["schema_version"], bool):
        raise ValueError("legacy pair schema_version must be integer 1")
    slug = book_dir.name
    if payload["book_slug"] != slug:
        raise ValueError(f"legacy pair receipt slug mismatch: expected {slug}")
    if payload["edition_id"] != "public-audio-recovery-2026-07":
        raise ValueError("legacy pair edition_id mismatch")
    candidate_id = payload["candidate_id"]
    if not isinstance(candidate_id, str) or not _CANDIDATE_ID.fullmatch(candidate_id):
        raise ValueError("legacy pair candidate_id is invalid")
    if not isinstance(payload["direction_name"], str) or not payload["direction_name"].strip():
        raise ValueError("legacy pair direction_name is invalid")
    if payload["selection_source"] != "user-approved-derivation":
        raise ValueError("legacy pair selection_source mismatch")
    privacy = _require_exact_fields(
        payload["privacy"],
        {"classification", "permission_to_publish"},
        "legacy pair privacy",
    )
    if privacy != {
        "classification": "public-safe",
        "permission_to_publish": True,
    }:
        raise ValueError("legacy pair is not approved for public publication")

    portrait = _require_exact_fields(
        payload["portrait"],
        {
            "path",
            "sha256",
            "dimensions",
            "epub_path",
            "epub_sha256",
            "epub_cover_member",
            "epub_cover_sha256",
        },
        "legacy pair portrait",
    )
    portrait_path = _resolve_named_file(book_dir, portrait["path"], "cover.png", "portrait")
    if portrait["dimensions"] != [1600, 2560] or _image_dimensions(
        portrait_path, "portrait"
    ) != (1600, 2560):
        raise ValueError("portrait dimensions must be 1600 by 2560")
    portrait_hash = _require_hash(portrait["sha256"], "portrait sha256")
    if sha256_file(portrait_path) != portrait_hash:
        raise ValueError("portrait hash mismatch")
    epub_name = f"{slug}.epub"
    epub_path = _resolve_named_file(book_dir, portrait["epub_path"], epub_name, "EPUB")
    if sha256_file(epub_path) != _require_hash(portrait["epub_sha256"], "EPUB sha256"):
        raise ValueError("EPUB hash mismatch")
    if portrait["epub_cover_member"] != "OEBPS/cover.png":
        raise ValueError("EPUB cover member must be OEBPS/cover.png")
    epub_cover_hash = _require_hash(
        portrait["epub_cover_sha256"], "EPUB cover sha256"
    )
    if _epub_cover_sha256(epub_path, "OEBPS/cover.png") != epub_cover_hash:
        raise ValueError("EPUB cover hash mismatch")
    if epub_cover_hash != portrait_hash:
        raise ValueError("EPUB cover and portrait hashes differ")

    square = _require_exact_fields(
        payload["square"],
        {
            "path",
            "sha256",
            "dimensions",
            "source_path",
            "source_sha256",
            "spec_path",
            "spec_sha256",
            "render_path",
            "render_sha256",
            "thumbnail_path",
            "thumbnail_sha256",
        },
        "legacy pair square",
    )
    square_files = {
        "square": ("path", "sha256", "m4b-cover.png"),
        "square source": ("source_path", "source_sha256", "m4b-cover-source.png"),
        "square specification": ("spec_path", "spec_sha256", "m4b-cover-spec.json"),
        "square render receipt": ("render_path", "render_sha256", "m4b-cover.render.json"),
        "square thumbnail": (
            "thumbnail_path",
            "thumbnail_sha256",
            "m4b-cover-thumbnail.png",
        ),
    }
    resolved: dict[str, Path] = {}
    for label, (path_key, hash_key, expected_name) in square_files.items():
        path = _resolve_named_file(book_dir, square[path_key], expected_name, label)
        if sha256_file(path) != _require_hash(square[hash_key], f"{label} sha256"):
            raise ValueError(f"{label} hash mismatch")
        resolved[label] = path
    if square["dimensions"] != [2400, 2400] or _image_dimensions(
        resolved["square"], "square"
    ) != (2400, 2400):
        raise ValueError("square dimensions must be 2400 by 2400")
    if _image_dimensions(resolved["square thumbnail"], "square thumbnail") != (
        240,
        240,
    ):
        raise ValueError("square thumbnail dimensions must be 240 by 240")


def write_legacy_cover_pair(
    book_dir: Path, candidate_id: str, direction_name: str
) -> Path:
    book_dir = book_dir.resolve()
    if not _CANDIDATE_ID.fullmatch(candidate_id):
        raise ValueError("candidate_id must be lowercase kebab-case")
    if not direction_name.strip():
        raise ValueError("direction_name must not be empty")
    slug = book_dir.name
    portrait = book_dir / "cover.png"
    epub = book_dir / f"{slug}.epub"
    square_paths = {
        "path": book_dir / "m4b-cover.png",
        "source_path": book_dir / "m4b-cover-source.png",
        "spec_path": book_dir / "m4b-cover-spec.json",
        "render_path": book_dir / "m4b-cover.render.json",
        "thumbnail_path": book_dir / "m4b-cover-thumbnail.png",
    }
    if _image_dimensions(portrait, "portrait") != (1600, 2560):
        raise ValueError("portrait dimensions must be 1600 by 2560")
    if _image_dimensions(square_paths["path"], "square") != (2400, 2400):
        raise ValueError("square dimensions must be 2400 by 2400")
    if _image_dimensions(square_paths["thumbnail_path"], "square thumbnail") != (
        240,
        240,
    ):
        raise ValueError("square thumbnail dimensions must be 240 by 240")
    portrait_hash = sha256_file(portrait)
    epub_cover_hash = _epub_cover_sha256(epub, "OEBPS/cover.png")
    if portrait_hash != epub_cover_hash:
        raise ValueError("EPUB cover and portrait hashes differ")
    payload: dict[str, object] = {
        "schema_version": 1,
        "book_slug": slug,
        "edition_id": "public-audio-recovery-2026-07",
        "candidate_id": candidate_id,
        "direction_name": direction_name.strip(),
        "selection_source": "user-approved-derivation",
        "privacy": {
            "classification": "public-safe",
            "permission_to_publish": True,
        },
        "portrait": {
            "path": "cover.png",
            "sha256": portrait_hash,
            "dimensions": [1600, 2560],
            "epub_path": f"{slug}.epub",
            "epub_sha256": sha256_file(epub),
            "epub_cover_member": "OEBPS/cover.png",
            "epub_cover_sha256": epub_cover_hash,
        },
        "square": {
            "path": "m4b-cover.png",
            "sha256": sha256_file(square_paths["path"]),
            "dimensions": [2400, 2400],
            "source_path": "m4b-cover-source.png",
            "source_sha256": sha256_file(square_paths["source_path"]),
            "spec_path": "m4b-cover-spec.json",
            "spec_sha256": sha256_file(square_paths["spec_path"]),
            "render_path": "m4b-cover.render.json",
            "render_sha256": sha256_file(square_paths["render_path"]),
            "thumbnail_path": "m4b-cover-thumbnail.png",
            "thumbnail_sha256": sha256_file(square_paths["thumbnail_path"]),
        },
    }
    validate_public_json(payload)
    receipt_path = book_dir / "legacy-cover-pair.json"
    _write_json_atomic(receipt_path, payload)
    verify_legacy_cover_pair(book_dir, receipt_path)
    return receipt_path


def build_recovery_manifest(
    repo_root: Path, source_map_path: Path, blocks_dir: Path
) -> dict[str, object]:
    source_map = _require_exact_fields(
        _read_json(source_map_path, "recovery source map"),
        {"schema_version", "books"},
        "recovery source map",
    )
    if source_map["schema_version"] != 1 or isinstance(
        source_map["schema_version"], bool
    ):
        raise ValueError("recovery source map schema_version must be integer 1")
    books = source_map["books"]
    if not isinstance(books, dict):
        raise ValueError("recovery source map books must be an object")
    if set(books) != set(REMUXED_SLUGS) or len(books) != len(REMUXED_SLUGS):
        raise ValueError(
            "source map slug set mismatch: expected " + ", ".join(REMUXED_SLUGS)
        )
    records: list[dict[str, object]] = []
    for slug in REMUXED_SLUGS:
        expected_fields = {"m4b", "sidecar"} if slug in RECOVERED_SLUGS else {"m4b"}
        source = _require_exact_fields(
            books[slug], expected_fields, f"source map entry {slug}"
        )
        m4b_value = source["m4b"]
        if not isinstance(m4b_value, str):
            raise ValueError(f"source M4B path must be a string: {slug}")
        source_m4b = Path(m4b_value).expanduser()
        source_sidecar: Path | None = None
        blocks_path: Path | None = None
        if slug in RECOVERED_SLUGS:
            sidecar_value = source["sidecar"]
            if not isinstance(sidecar_value, str):
                raise ValueError(f"source sidecar path must be a string: {slug}")
            source_sidecar = Path(sidecar_value).expanduser()
            blocks_path = blocks_dir / f"{slug}.json"
        records.append(
            build_recovery_record(
                repo_root,
                slug,
                source_m4b,
                source_sidecar,
                blocks_path,
            )
        )
    manifest: dict[str, object] = {
        "schema_version": 1,
        "edition_id": "public-audio-recovery-2026-07",
        "books": records,
    }
    validate_public_json(manifest)
    return manifest


def build_recovery_record(
    repo_root: Path,
    slug: str,
    source_m4b: Path,
    source_sidecar: Path | None,
    blocks_path: Path | None,
) -> dict[str, object]:
    repo_root = repo_root.resolve(strict=True)
    if slug not in REMUXED_SLUGS:
        raise ValueError(f"unsupported recovery slug: {slug}")
    source_m4b = source_m4b.resolve(strict=True)
    book_dir = repo_root / "books" / slug
    final_m4b = book_dir / f"{slug}.m4b"
    epub = book_dir / f"{slug}.epub"
    portrait = book_dir / "cover.png"
    square = book_dir / "m4b-cover.png"
    for path, label in (
        (final_m4b, "final M4B"),
        (epub, "EPUB"),
        (portrait, "portrait cover"),
        (square, "square cover"),
    ):
        if not path.is_file():
            raise ValueError(f"{label} is missing: {path}")
    if final_m4b.stat().st_size >= MAX_GIT_BLOB_BYTES:
        raise ValueError(f"final M4B reaches the ordinary Git size limit: {slug}")

    media_signature, normalized_image_sha256, normalized_m4b_art_sha256 = (
        _media_helpers()
    )
    source_signature = media_signature(source_m4b)
    final_signature = media_signature(final_m4b)
    if source_signature != final_signature:
        raise ValueError(f"media signature changed during artwork replacement: {slug}")
    source_payload = _signature_payload(source_signature)
    final_payload = _signature_payload(final_signature)
    if not source_payload.get("chapters"):
        raise ValueError(f"final M4B has no chapters: {slug}")
    if normalized_image_sha256(square) != normalized_m4b_art_sha256(final_m4b):
        raise ValueError(f"embedded M4B artwork does not match square cover: {slug}")

    record: dict[str, object] = {
        "slug": slug,
        "source_m4b_sha256": sha256_file(source_m4b),
        "final_m4b_path": _relative_file(repo_root, final_m4b, "final M4B"),
        "final_m4b_sha256": sha256_file(final_m4b),
        "epub_path": _relative_file(repo_root, epub, "EPUB"),
        "epub_sha256": sha256_file(epub),
        "portrait_sha256": sha256_file(portrait),
        "square_sha256": sha256_file(square),
        "source_media_signature": source_payload,
        "final_media_signature": final_payload,
    }
    if source_sidecar is not None:
        source_sidecar = source_sidecar.resolve(strict=True)
        final_sidecar = book_dir / f"{slug}.alignment.json"
        if not final_sidecar.is_file():
            raise ValueError(f"final sidecar is missing: {slug}")
        source_sidecar_hash = sha256_file(source_sidecar)
        final_sidecar_hash = sha256_file(final_sidecar)
        if source_sidecar_hash != final_sidecar_hash:
            raise ValueError(f"sidecar bytes changed during recovery: {slug}")
        if blocks_path is None:
            raise ValueError(f"block export is required for recovered sidecar: {slug}")
        anchor_count, resolved_count = verify_block_parity(
            final_sidecar, blocks_path.resolve(strict=True)
        )
        blocks_document = _read_json(blocks_path, "block export")
        assert isinstance(blocks_document, dict)
        blocks = blocks_document["blocks"]
        assert isinstance(blocks, list)
        record.update(
            {
                "source_sidecar_sha256": source_sidecar_hash,
                "final_sidecar_path": _relative_file(
                    repo_root, final_sidecar, "final sidecar"
                ),
                "final_sidecar_sha256": final_sidecar_hash,
                "anchor_count": anchor_count,
                "exported_block_count": len(blocks),
                "resolved_anchor_count": resolved_count,
            }
        )
    validate_public_json(record)
    return record


def verify_recovery_record(
    repo_root: Path, record: dict[str, object], blocks_path: Path | None
) -> None:
    repo_root = repo_root.resolve(strict=True)
    validate_public_json(record)
    slug = record.get("slug")
    if not isinstance(slug, str) or slug not in REMUXED_SLUGS:
        raise ValueError("recovery record has an unsupported slug")
    expected_fields = (
        RECOVERED_RECORD_FIELDS if slug in RECOVERED_SLUGS else COMMON_RECORD_FIELDS
    )
    _require_exact_fields(record, expected_fields, f"recovery record {slug}")
    book_dir = repo_root / "books" / slug
    expected_m4b_path = f"books/{slug}/{slug}.m4b"
    expected_epub_path = f"books/{slug}/{slug}.epub"
    if record["final_m4b_path"] != expected_m4b_path:
        raise ValueError(f"final M4B path mismatch: {slug}")
    if record["epub_path"] != expected_epub_path:
        raise ValueError(f"EPUB path mismatch: {slug}")
    final_m4b = repo_root / expected_m4b_path
    epub = repo_root / expected_epub_path
    portrait = book_dir / "cover.png"
    square = book_dir / "m4b-cover.png"
    for path, expected_hash, label in (
        (final_m4b, record["final_m4b_sha256"], "final M4B"),
        (epub, record["epub_sha256"], "EPUB"),
        (portrait, record["portrait_sha256"], "portrait"),
        (square, record["square_sha256"], "square"),
    ):
        expected = _require_hash(expected_hash, f"{label} sha256")
        if sha256_file(path) != expected:
            raise ValueError(f"{label} hash mismatch: {slug}")
    _require_hash(record["source_m4b_sha256"], "source M4B sha256")
    if final_m4b.stat().st_size >= MAX_GIT_BLOB_BYTES:
        raise ValueError(f"final M4B reaches the ordinary Git size limit: {slug}")
    if record["source_media_signature"] != record["final_media_signature"]:
        raise ValueError(f"recorded source/final media signatures differ: {slug}")
    media_signature, normalized_image_sha256, normalized_m4b_art_sha256 = (
        _media_helpers()
    )
    current_signature = _signature_payload(media_signature(final_m4b))
    if current_signature != record["final_media_signature"]:
        raise ValueError(f"current final media signature mismatch: {slug}")
    if not current_signature.get("chapters"):
        raise ValueError(f"final M4B has no chapters: {slug}")
    if normalized_image_sha256(square) != normalized_m4b_art_sha256(final_m4b):
        raise ValueError(f"embedded M4B artwork does not match square cover: {slug}")

    if slug in RECOVERED_SLUGS:
        expected_sidecar_path = f"books/{slug}/{slug}.alignment.json"
        if record["final_sidecar_path"] != expected_sidecar_path:
            raise ValueError(f"final sidecar path mismatch: {slug}")
        final_sidecar = repo_root / expected_sidecar_path
        final_sidecar_hash = _require_hash(
            record["final_sidecar_sha256"], "final sidecar sha256"
        )
        source_sidecar_hash = _require_hash(
            record["source_sidecar_sha256"], "source sidecar sha256"
        )
        if final_sidecar_hash != source_sidecar_hash:
            raise ValueError(f"recorded source/final sidecar hashes differ: {slug}")
        if sha256_file(final_sidecar) != final_sidecar_hash:
            raise ValueError(f"final sidecar hash mismatch: {slug}")
        if blocks_path is None:
            raise ValueError(f"block export is required for recovered sidecar: {slug}")
        anchor_count, resolved_count = verify_block_parity(final_sidecar, blocks_path)
        blocks_document = _read_json(blocks_path, "block export")
        assert isinstance(blocks_document, dict)
        blocks = blocks_document["blocks"]
        assert isinstance(blocks, list)
        if record["anchor_count"] != anchor_count:
            raise ValueError(f"anchor count mismatch: {slug}")
        if record["resolved_anchor_count"] != resolved_count:
            raise ValueError(f"resolved anchor count mismatch: {slug}")
        if record["exported_block_count"] != len(blocks):
            raise ValueError(f"exported block count mismatch: {slug}")


def verify_recovery_manifest(
    repo_root: Path, manifest_path: Path, blocks_dir: Path
) -> None:
    manifest = _require_exact_fields(
        _read_json(manifest_path, "public recovery manifest"),
        {"schema_version", "edition_id", "books"},
        "public recovery manifest",
    )
    validate_public_json(manifest)
    if manifest["schema_version"] != 1 or isinstance(
        manifest["schema_version"], bool
    ):
        raise ValueError("public recovery manifest schema_version must be integer 1")
    if manifest["edition_id"] != "public-audio-recovery-2026-07":
        raise ValueError("public recovery manifest edition_id mismatch")
    books = manifest["books"]
    if not isinstance(books, list):
        raise ValueError("public recovery manifest books must be a list")
    slugs = [record.get("slug") if isinstance(record, dict) else None for record in books]
    if tuple(slugs) != REMUXED_SLUGS:
        raise ValueError("manifest slug order mismatch")
    for record in books:
        assert isinstance(record, dict)
        slug = record["slug"]
        assert isinstance(slug, str)
        blocks_path = blocks_dir / f"{slug}.json" if slug in RECOVERED_SLUGS else None
        verify_recovery_record(repo_root, record, blocks_path)
    for slug in LEGACY_PAIR_SLUGS:
        book_dir = repo_root / "books" / slug
        verify_legacy_cover_pair(book_dir, book_dir / "legacy-cover-pair.json")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Record and verify public audiobook recovery evidence."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    record = commands.add_parser("record", help="build a public recovery manifest")
    record.add_argument("--repo", required=True, type=Path)
    record.add_argument("--sources", required=True, type=Path)
    record.add_argument("--blocks-dir", required=True, type=Path)
    record.add_argument("--out", required=True, type=Path)

    verify = commands.add_parser("verify", help="verify a public recovery manifest")
    verify.add_argument("--repo", required=True, type=Path)
    verify.add_argument("--manifest", required=True, type=Path)
    verify.add_argument("--blocks-dir", required=True, type=Path)

    cover = commands.add_parser(
        "record-cover", help="write one legacy square-companion receipt"
    )
    cover.add_argument("--book-dir", required=True, type=Path)
    cover.add_argument("--candidate-id", required=True)
    cover.add_argument("--direction-name", required=True)
    return parser


def main() -> int:
    arguments = _parser().parse_args()
    try:
        if arguments.command == "record":
            manifest = build_recovery_manifest(
                arguments.repo, arguments.sources, arguments.blocks_dir
            )
            _write_json_atomic(arguments.out, manifest)
            print(f"RECOVERY_MANIFEST: {arguments.out}")
            return 0
        if arguments.command == "verify":
            verify_recovery_manifest(
                arguments.repo, arguments.manifest, arguments.blocks_dir
            )
            print(f"VERIFIED_RECOVERY_BOOKS: {len(REMUXED_SLUGS)}")
            return 0
        receipt = write_legacy_cover_pair(
            arguments.book_dir, arguments.candidate_id, arguments.direction_name
        )
        print(f"LEGACY_COVER_PAIR: {receipt}")
        return 0
    except ValueError as error:
        parser = _parser()
        parser.error(str(error))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
