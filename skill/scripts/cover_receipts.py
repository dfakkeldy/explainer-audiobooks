#!/usr/bin/env python3
"""Create explicit cover selections and verify packaged cover identity."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from refresh_epub_cover import (
    discover_cover_member,
    discover_opf_member,
    png_dimensions,
)


EXPECTED_DIMENSIONS = (1600, 2560)
PAIRED_DIMENSIONS = {"portrait": (1600, 2560), "square": (2400, 2400)}
SELECTION_SOURCES = frozenset({"explicit-user-choice", "requested-mix"})
PAIRED_SELECTION_SOURCES = frozenset({"user", "requested-mix"})
CLASSIFICATIONS = frozenset({"public-safe", "private", "sensitive"})
PUBLICATION_PERMISSIONS = frozenset({"granted", "denied", "not-requested"})
SLUG = re.compile(r"[a-z0-9][a-z0-9-]*")
SHA256 = re.compile(r"[0-9a-f]{64}")

RENDER_FIELDS = frozenset(
    {
        "receipt_version",
        "renderer_version",
        "schema_version",
        "candidate",
        "spec",
        "spec_sha256",
        "source_art",
        "source_art_sha256",
        "font_manifest_version",
        "font_manifest_sha256",
        "fonts",
        "output",
        "output_sha256",
        "thumbnail",
        "thumbnail_sha256",
        "dimensions",
        "colour_mode",
        "warnings",
    }
)
PAIRED_RENDER_FIELDS = RENDER_FIELDS | {"variant", "thumbnail_dimensions"}
PAIRED_SELECTION_FIELDS = frozenset(
    {
        "schema_version",
        "book_slug",
        "edition_id",
        "candidate",
        "source_art_sha256",
        "variants",
        "font_manifest_sha256",
        "selection_source",
        "selected_at",
        "privacy",
    }
)
SELECTION_FIELDS = frozenset(
    {
        "receipt_version",
        "book_slug",
        "edition_id",
        "selected_candidate",
        "direction_name",
        "schema_version",
        "spec_sha256",
        "source_art_sha256",
        "rendered_cover_sha256",
        "font_manifest_version",
        "font_manifest_sha256",
        "dimensions",
        "colour_mode",
        "selected_at",
        "selection_source",
        "privacy",
    }
)


@dataclass(frozen=True)
class SelectionReceipt:
    receipt_version: int
    book_slug: str
    edition_id: str
    selected_candidate: str
    direction_name: str
    schema_version: int
    spec_sha256: str
    source_art_sha256: str
    rendered_cover_sha256: str
    font_manifest_version: int
    font_manifest_sha256: str
    dimensions: tuple[int, int]
    colour_mode: str
    selected_at: str
    selection_source: str
    privacy: dict[str, str]


@dataclass(frozen=True)
class SelectedCandidate:
    id: str
    direction_name: str


@dataclass(frozen=True)
class SelectedVariant:
    specification_sha256: str
    render_receipt_sha256: str
    cover_sha256: str
    dimensions: tuple[int, int]
    thumbnail_sha256: str
    subtitle_included: bool


@dataclass(frozen=True)
class PairedSelectionReceipt:
    schema_version: int
    book_slug: str
    edition_id: str
    candidate: SelectedCandidate
    source_art_sha256: str
    variants: dict[str, SelectedVariant]
    font_manifest_sha256: str
    selection_source: str
    selected_at: str
    privacy: dict[str, object]


@dataclass(frozen=True)
class PackageVerification:
    book_slug: str
    edition_id: str
    rendered_cover_sha256: str
    checks: tuple[str, ...]


class _DuplicateJSONKeyError(ValueError):
    pass


def _unique_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateJSONKeyError(f"duplicate key: {key}")
        result[key] = value
    return result


def _path(value: object, label: str) -> Path:
    try:
        return Path(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as error:
        raise ValueError(f"invalid {label} path") from error


def _read_json(path: Path, label: str) -> dict[str, object]:
    source = _path(path, label)
    try:
        payload = json.loads(
            source.read_text(encoding="utf-8"),
            object_pairs_hook=_unique_json_object,
        )
    except _DuplicateJSONKeyError as error:
        raise ValueError(f"invalid {label}: {error}") from error
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"invalid {label}: {source}") from error
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must be a JSON object")
    return payload


def _exact_fields(
    payload: dict[str, object],
    fields: frozenset[str],
    label: str,
) -> None:
    if set(payload) != fields:
        raise ValueError(f"{label} has missing or unknown fields")


def _version(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value != 1:
        raise ValueError(f"{label} must be integer 1")
    return value


def _slug(value: object, label: str) -> str:
    if not isinstance(value, str) or not SLUG.fullmatch(value):
        raise ValueError(f"{label} must be a lowercase slug")
    return value


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value


def _hash(value: object, label: str) -> str:
    if not isinstance(value, str) or not SHA256.fullmatch(value):
        raise ValueError(f"{label} must be a lowercase SHA-256")
    return value


def _choice(value: object, choices: frozenset[str], label: str) -> str:
    if not isinstance(value, str) or value not in choices:
        raise ValueError(f"invalid {label}")
    return value


def _timestamp(value: object, label: str = "selected_at") -> str:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a timezone-aware ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value)
        offset = parsed.utcoffset()
    except (OverflowError, TypeError, ValueError) as error:
        raise ValueError(
            f"{label} must be a timezone-aware ISO-8601 timestamp"
        ) from error
    if offset is None:
        raise ValueError(f"{label} must be timezone-aware")
    return value


def _dimensions(value: object, label: str) -> tuple[int, int]:
    if (
        not isinstance(value, list)
        or len(value) != 2
        or any(isinstance(item, bool) or not isinstance(item, int) for item in value)
        or tuple(value) != EXPECTED_DIMENSIONS
    ):
        raise ValueError(f"{label} must be 1600x2560 RGB")
    return EXPECTED_DIMENSIONS


def _file_name(value: object, label: str) -> str:
    text = _text(value, label)
    try:
        candidate = Path(text)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{label} must be a relative file name") from error
    if candidate.is_absolute() or len(candidate.parts) != 1 or text in {".", ".."}:
        raise ValueError(f"{label} must be a relative file name")
    return text


def _read_bytes(path: Path, label: str) -> bytes:
    try:
        if not path.is_file():
            raise OSError("not a file")
        return path.read_bytes()
    except (OSError, RuntimeError) as error:
        raise ValueError(f"{label} could not be read: {path}") from error


def _validate_cover_png(payload: bytes, label: str) -> None:
    try:
        dimensions = png_dimensions(payload)
    except (IndexError, TypeError, ValueError) as error:
        raise ValueError(f"{label} must be a valid 1600x2560 RGB PNG") from error
    if dimensions != EXPECTED_DIMENSIONS or len(payload) < 26 or payload[25] != 2:
        raise ValueError(f"{label} must be a valid 1600x2560 RGB PNG")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(_read_bytes(_path(path, "file"), "file")).hexdigest()


def _validate_render_receipt(payload: dict[str, object]) -> dict[str, object]:
    _exact_fields(payload, RENDER_FIELDS, "render receipt")
    _version(payload["receipt_version"], "render receipt_version")
    _version(payload["renderer_version"], "renderer_version")
    _version(payload["schema_version"], "schema_version")
    candidate = payload["candidate"]
    if not isinstance(candidate, dict) or set(candidate) != {"id", "direction_name"}:
        raise ValueError("render candidate has missing or unknown fields")
    _slug(candidate["id"], "render candidate id")
    _text(candidate["direction_name"], "render direction_name")
    _file_name(payload["spec"], "render spec")
    _hash(payload["spec_sha256"], "render spec_sha256")
    _file_name(payload["source_art"], "render source_art")
    _hash(payload["source_art_sha256"], "render source_art_sha256")
    _version(payload["font_manifest_version"], "font_manifest_version")
    _hash(payload["font_manifest_sha256"], "render font_manifest_sha256")
    fonts = payload["fonts"]
    if not isinstance(fonts, dict) or not fonts:
        raise ValueError("render fonts must be a non-empty object")
    for font_id, digest in fonts.items():
        _slug(font_id, "render font id")
        _hash(digest, f"render font hash for {font_id}")
    _file_name(payload["output"], "render output")
    _hash(payload["output_sha256"], "render output_sha256")
    _file_name(payload["thumbnail"], "render thumbnail")
    _hash(payload["thumbnail_sha256"], "render thumbnail_sha256")
    _dimensions(payload["dimensions"], "render cover")
    if payload["colour_mode"] != "RGB" or not isinstance(payload["colour_mode"], str):
        raise ValueError("render cover must be 1600x2560 RGB")
    warnings = payload["warnings"]
    if not isinstance(warnings, list) or any(
        not isinstance(warning, str) for warning in warnings
    ):
        raise ValueError("render warnings must be an array of strings")
    return payload


def _resolve_render_cover(render_path: Path, output: object) -> Path:
    name = _file_name(output, "render output")
    try:
        cover = (render_path.parent / name).resolve(strict=True)
        cover.relative_to(render_path.parent)
    except (OSError, RuntimeError, ValueError) as error:
        raise ValueError(
            "rendered cover output escapes receipt folder or is missing"
        ) from error
    if cover == render_path:
        raise ValueError("render output aliases render receipt")
    if not cover.is_file():
        raise ValueError("rendered cover is missing")
    return cover


def _resolved_output(path: Path) -> Path:
    output = _path(path, "selection output")
    try:
        return output.resolve()
    except (OSError, RuntimeError, ValueError) as error:
        raise ValueError("invalid selection output path") from error


def _aliases_any(path: Path, protected: tuple[Path, ...]) -> bool:
    try:
        return any(
            path == source or (path.exists() and os.path.samefile(path, source))
            for source in protected
        )
    except OSError as error:
        raise ValueError("invalid selection output path") from error


def _write_json_atomic(path: Path, payload: dict[str, object]) -> None:
    destination = _path(path, "selection output")
    temporary: Path | None = None
    descriptor: int | None = None
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        descriptor, raw_path = tempfile.mkstemp(
            prefix=f".{destination.name}.",
            suffix=".tmp",
            dir=destination.parent,
        )
        temporary = Path(raw_path)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            descriptor = None
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
        temporary = None
    except (OSError, TypeError, ValueError) as error:
        raise ValueError(
            f"selection receipt could not be written: {destination}"
        ) from error
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _load_legacy_selection(payload: dict[str, object]) -> SelectionReceipt:
    _exact_fields(payload, SELECTION_FIELDS, "cover selection receipt")
    receipt_version = _version(payload["receipt_version"], "receipt_version")
    book_slug = _slug(payload["book_slug"], "book_slug")
    edition_id = _slug(payload["edition_id"], "edition_id")
    selected_candidate = _slug(payload["selected_candidate"], "selected_candidate")
    direction_name = _text(payload["direction_name"], "direction_name")
    schema_version = _version(payload["schema_version"], "schema_version")
    spec_sha256 = _hash(payload["spec_sha256"], "spec_sha256")
    source_art_sha256 = _hash(payload["source_art_sha256"], "source_art_sha256")
    rendered_cover_sha256 = _hash(
        payload["rendered_cover_sha256"], "rendered_cover_sha256"
    )
    font_manifest_version = _version(
        payload["font_manifest_version"], "font_manifest_version"
    )
    font_manifest_sha256 = _hash(
        payload["font_manifest_sha256"], "font_manifest_sha256"
    )
    dimensions = _dimensions(payload["dimensions"], "selection cover")
    if payload["colour_mode"] != "RGB" or not isinstance(payload["colour_mode"], str):
        raise ValueError("selection cover must be 1600x2560 RGB")
    selected_at = _timestamp(payload["selected_at"])
    selection_source = _choice(
        payload["selection_source"], SELECTION_SOURCES, "selection_source"
    )
    privacy = payload["privacy"]
    if not isinstance(privacy, dict) or set(privacy) != {
        "classification",
        "permission_to_publish",
    }:
        raise ValueError("selection privacy has missing or unknown fields")
    classification = _choice(
        privacy["classification"], CLASSIFICATIONS, "privacy classification"
    )
    permission = _choice(
        privacy["permission_to_publish"],
        PUBLICATION_PERMISSIONS,
        "permission_to_publish",
    )
    return SelectionReceipt(
        receipt_version=receipt_version,
        book_slug=book_slug,
        edition_id=edition_id,
        selected_candidate=selected_candidate,
        direction_name=direction_name,
        schema_version=schema_version,
        spec_sha256=spec_sha256,
        source_art_sha256=source_art_sha256,
        rendered_cover_sha256=rendered_cover_sha256,
        font_manifest_version=font_manifest_version,
        font_manifest_sha256=font_manifest_sha256,
        dimensions=dimensions,
        colour_mode="RGB",
        selected_at=selected_at,
        selection_source=selection_source,
        privacy={
            "classification": classification,
            "permission_to_publish": permission,
        },
    )


def _paired_dimensions(value: object, variant: str) -> tuple[int, int]:
    expected = PAIRED_DIMENSIONS[variant]
    if (
        not isinstance(value, list)
        or len(value) != 2
        or any(isinstance(item, bool) or not isinstance(item, int) for item in value)
        or tuple(value) != expected
    ):
        raise ValueError(f"{variant} dimensions must be {expected[0]}x{expected[1]}")
    return expected


def _load_paired_selection(payload: dict[str, object]) -> PairedSelectionReceipt:
    _exact_fields(payload, PAIRED_SELECTION_FIELDS, "paired selection receipt")
    if payload["schema_version"] != 2 or isinstance(payload["schema_version"], bool):
        raise ValueError("paired schema_version must be integer 2")
    candidate = payload["candidate"]
    if not isinstance(candidate, dict):
        raise ValueError("paired candidate must be an object")
    _exact_fields(candidate, frozenset({"id", "direction_name"}), "paired candidate")
    variants = payload["variants"]
    if not isinstance(variants, dict) or set(variants) != set(PAIRED_DIMENSIONS):
        raise ValueError("paired variants must contain exactly portrait and square")
    parsed_variants: dict[str, SelectedVariant] = {}
    fields = frozenset(
        {
            "specification_sha256",
            "render_receipt_sha256",
            "cover_sha256",
            "dimensions",
            "thumbnail_sha256",
            "subtitle_included",
        }
    )
    for name in ("portrait", "square"):
        variant = variants[name]
        if not isinstance(variant, dict):
            raise ValueError(f"{name} variant must be an object")
        _exact_fields(variant, fields, f"{name} variant")
        included = variant["subtitle_included"]
        if not isinstance(included, bool):
            raise ValueError(f"{name} subtitle_included must be boolean")
        parsed_variants[name] = SelectedVariant(
            specification_sha256=_hash(
                variant["specification_sha256"], f"{name} specification_sha256"
            ),
            render_receipt_sha256=_hash(
                variant["render_receipt_sha256"], f"{name} render_receipt_sha256"
            ),
            cover_sha256=_hash(variant["cover_sha256"], f"{name} cover_sha256"),
            dimensions=_paired_dimensions(variant["dimensions"], name),
            thumbnail_sha256=_hash(
                variant["thumbnail_sha256"], f"{name} thumbnail_sha256"
            ),
            subtitle_included=included,
        )
    privacy = payload["privacy"]
    if not isinstance(privacy, dict):
        raise ValueError("paired privacy must be an object")
    _exact_fields(
        privacy,
        frozenset({"classification", "permission_to_publish"}),
        "paired privacy",
    )
    permission = privacy["permission_to_publish"]
    if not isinstance(permission, bool):
        raise ValueError("permission_to_publish must be boolean")
    return PairedSelectionReceipt(
        schema_version=2,
        book_slug=_slug(payload["book_slug"], "book_slug"),
        edition_id=_slug(payload["edition_id"], "edition_id"),
        candidate=SelectedCandidate(
            _slug(candidate["id"], "candidate id"),
            _text(candidate["direction_name"], "direction_name"),
        ),
        source_art_sha256=_hash(payload["source_art_sha256"], "source_art_sha256"),
        variants=parsed_variants,
        font_manifest_sha256=_hash(
            payload["font_manifest_sha256"], "font_manifest_sha256"
        ),
        selection_source=_choice(
            payload["selection_source"], PAIRED_SELECTION_SOURCES, "selection_source"
        ),
        selected_at=_timestamp(payload["selected_at"]),
        privacy={
            "classification": _choice(
                privacy["classification"], CLASSIFICATIONS, "privacy classification"
            ),
            "permission_to_publish": permission,
        },
    )


def load_selection(path: Path) -> SelectionReceipt | PairedSelectionReceipt:
    payload = _read_json(Path(path), "cover selection receipt")
    version = payload.get("schema_version")
    if version == 1 and not isinstance(version, bool):
        return _load_legacy_selection(payload)
    if version == 2 and not isinstance(version, bool):
        return _load_paired_selection(payload)
    raise ValueError("unsupported cover selection schema_version")


def create_selection(
    render_receipt_path: Path,
    output_path: Path,
    *,
    book_slug: str,
    edition_id: str,
    selection_source: str,
    selected_at: str,
    classification: str,
    permission_to_publish: str,
) -> SelectionReceipt:
    validated_slug = _slug(book_slug, "book_slug")
    validated_edition = _slug(edition_id, "edition_id")
    validated_source = _choice(selection_source, SELECTION_SOURCES, "selection_source")
    validated_time = _timestamp(selected_at)
    validated_classification = _choice(
        classification, CLASSIFICATIONS, "privacy classification"
    )
    validated_permission = _choice(
        permission_to_publish,
        PUBLICATION_PERMISSIONS,
        "permission_to_publish",
    )

    raw_render_path = _path(render_receipt_path, "render receipt")
    try:
        render_path = raw_render_path.resolve(strict=True)
    except (OSError, RuntimeError, ValueError) as error:
        raise ValueError(f"invalid render receipt: {raw_render_path}") from error
    render = _validate_render_receipt(_read_json(render_path, "render receipt"))
    cover = _resolve_render_cover(render_path, render["output"])
    cover_payload = _read_bytes(cover, "rendered cover")
    cover_hash = hashlib.sha256(cover_payload).hexdigest()
    if cover_hash != render["output_sha256"]:
        raise ValueError("rendered cover hash mismatch")
    _validate_cover_png(cover_payload, "rendered cover")

    output = _resolved_output(output_path)
    if _aliases_any(output, (render_path, cover)):
        raise ValueError("selection output aliases render receipt or rendered cover")

    candidate = render["candidate"]
    if not isinstance(candidate, dict):
        raise ValueError("invalid render candidate")
    receipt = SelectionReceipt(
        receipt_version=1,
        book_slug=validated_slug,
        edition_id=validated_edition,
        selected_candidate=str(candidate["id"]),
        direction_name=str(candidate["direction_name"]),
        schema_version=1,
        spec_sha256=str(render["spec_sha256"]),
        source_art_sha256=str(render["source_art_sha256"]),
        rendered_cover_sha256=cover_hash,
        font_manifest_version=1,
        font_manifest_sha256=str(render["font_manifest_sha256"]),
        dimensions=EXPECTED_DIMENSIONS,
        colour_mode="RGB",
        selected_at=validated_time,
        selection_source=validated_source,
        privacy={
            "classification": validated_classification,
            "permission_to_publish": validated_permission,
        },
    )
    _write_json_atomic(Path(output_path), asdict(receipt))
    return receipt


def _validated_paired_render(
    path: Path, expected_variant: str
) -> tuple[dict[str, object], Path, dict[str, str], str]:
    try:
        render_path = _path(path, f"{expected_variant} render receipt").resolve(
            strict=True
        )
    except (OSError, RuntimeError, ValueError) as error:
        raise ValueError(f"invalid {expected_variant} render receipt") from error
    render = _read_json(render_path, f"{expected_variant} render receipt")
    _exact_fields(render, PAIRED_RENDER_FIELDS, f"{expected_variant} render receipt")
    for field in (
        "receipt_version",
        "renderer_version",
        "schema_version",
        "font_manifest_version",
    ):
        _version(render[field], f"{expected_variant} {field}")
    if render["variant"] != expected_variant:
        raise ValueError(f"{expected_variant} render receipt has wrong variant")
    candidate = render["candidate"]
    if not isinstance(candidate, dict):
        raise ValueError(f"{expected_variant} candidate must be an object")
    _exact_fields(
        candidate, frozenset({"id", "direction_name"}), f"{expected_variant} candidate"
    )
    _slug(candidate["id"], f"{expected_variant} candidate id")
    _text(candidate["direction_name"], f"{expected_variant} direction_name")
    dimensions = _paired_dimensions(render["dimensions"], expected_variant)
    expected_thumbnail = (160, 256) if expected_variant == "portrait" else (160, 160)
    if render["thumbnail_dimensions"] != list(expected_thumbnail):
        raise ValueError(f"{expected_variant} thumbnail dimensions are invalid")
    for field in (
        "spec_sha256",
        "source_art_sha256",
        "font_manifest_sha256",
        "output_sha256",
        "thumbnail_sha256",
    ):
        _hash(render[field], f"{expected_variant} {field}")
    if render["colour_mode"] != "RGB":
        raise ValueError(f"{expected_variant} cover must be RGB")
    fonts = render["fonts"]
    if not isinstance(fonts, dict) or not fonts:
        raise ValueError(f"{expected_variant} fonts must be a non-empty object")
    for font_id, digest in fonts.items():
        _slug(font_id, f"{expected_variant} font id")
        _hash(digest, f"{expected_variant} font hash")
    warnings = render["warnings"]
    if not isinstance(warnings, list) or any(
        not isinstance(item, str) for item in warnings
    ):
        raise ValueError(f"{expected_variant} warnings must be strings")
    cover = _resolve_render_cover(render_path, render["output"])
    cover_bytes = _read_bytes(cover, f"{expected_variant} rendered cover")
    if hashlib.sha256(cover_bytes).hexdigest() != render["output_sha256"]:
        raise ValueError(f"{expected_variant} rendered cover hash mismatch")
    try:
        from PIL import Image

        with Image.open(cover) as image:
            if image.mode != "RGB" or image.size != dimensions:
                raise ValueError
    except Exception as error:
        raise ValueError(
            f"{expected_variant} rendered cover has invalid dimensions or colour mode"
        ) from error
    thumbnail = render_path.parent / _file_name(
        render["thumbnail"], f"{expected_variant} thumbnail"
    )
    if (
        hashlib.sha256(
            _read_bytes(thumbnail, f"{expected_variant} thumbnail")
        ).hexdigest()
        != render["thumbnail_sha256"]
    ):
        raise ValueError(f"{expected_variant} thumbnail hash mismatch")
    spec = render_path.parent / _file_name(render["spec"], f"{expected_variant} spec")
    spec_bytes = _read_bytes(spec, f"{expected_variant} specification")
    if hashlib.sha256(spec_bytes).hexdigest() != render["spec_sha256"]:
        raise ValueError(f"{expected_variant} specification hash mismatch")
    spec_payload = _read_json(spec, f"{expected_variant} specification")
    if spec_payload.get("variant") != expected_variant:
        raise ValueError(f"{expected_variant} specification has wrong variant")
    if spec_payload.get("candidate") != candidate:
        raise ValueError(
            f"{expected_variant} render candidate does not match specification"
        )
    metadata = spec_payload.get("metadata")
    if not isinstance(metadata, dict):
        raise ValueError(f"{expected_variant} specification metadata is invalid")
    parsed_metadata = {
        field: _text(metadata.get(field), f"{expected_variant} {field}")
        for field in ("title", "author")
    }
    subtitle = metadata.get("subtitle")
    if not isinstance(subtitle, str):
        raise ValueError(f"{expected_variant} subtitle must be a string")
    parsed_metadata["subtitle"] = subtitle
    return (
        render,
        cover,
        parsed_metadata,
        hashlib.sha256(
            _read_bytes(render_path, f"{expected_variant} render receipt")
        ).hexdigest(),
    )


def create_paired_selection(
    portrait_render: Path,
    square_render: Path,
    output: Path,
    book_slug: str,
    edition_id: str,
    selection_source: str,
    selected_at: str,
    privacy_classification: str,
    permission_to_publish: bool,
) -> PairedSelectionReceipt:
    validated_slug = _slug(book_slug, "book_slug")
    validated_edition = _slug(edition_id, "edition_id")
    validated_source = _choice(
        selection_source, PAIRED_SELECTION_SOURCES, "selection_source"
    )
    validated_time = _timestamp(selected_at)
    classification = _choice(
        privacy_classification, CLASSIFICATIONS, "privacy classification"
    )
    if not isinstance(permission_to_publish, bool):
        raise ValueError("permission_to_publish must be boolean")
    (
        portrait,
        portrait_cover,
        portrait_metadata,
        portrait_receipt_hash,
    ) = _validated_paired_render(portrait_render, "portrait")
    (
        square,
        square_cover,
        square_metadata,
        square_receipt_hash,
    ) = _validated_paired_render(square_render, "square")
    portrait_candidate = portrait["candidate"]
    square_candidate = square["candidate"]
    if portrait_candidate != square_candidate:
        raise ValueError("portrait and square candidate identities must match")
    if portrait["source_art_sha256"] != square["source_art_sha256"]:
        raise ValueError("portrait and square source hashes must match")
    if portrait["font_manifest_sha256"] != square["font_manifest_sha256"]:
        raise ValueError("portrait and square font manifests must match")
    for field in ("title", "author"):
        if portrait_metadata[field] != square_metadata[field]:
            raise ValueError(f"portrait and square {field} must match")
    if square_metadata["subtitle"] not in ("", portrait_metadata["subtitle"]):
        raise ValueError("square subtitle must match portrait or be omitted")
    resolved_output = _resolved_output(output)
    protected = tuple(
        Path(path).resolve()
        for path in (portrait_render, square_render, portrait_cover, square_cover)
    )
    if _aliases_any(resolved_output, protected):
        raise ValueError("selection output aliases paired render input")
    assert isinstance(portrait_candidate, dict)
    receipt = PairedSelectionReceipt(
        schema_version=2,
        book_slug=validated_slug,
        edition_id=validated_edition,
        candidate=SelectedCandidate(
            str(portrait_candidate["id"]), str(portrait_candidate["direction_name"])
        ),
        source_art_sha256=str(portrait["source_art_sha256"]),
        variants={
            "portrait": SelectedVariant(
                str(portrait["spec_sha256"]),
                portrait_receipt_hash,
                str(portrait["output_sha256"]),
                PAIRED_DIMENSIONS["portrait"],
                str(portrait["thumbnail_sha256"]),
                bool(portrait_metadata["subtitle"]),
            ),
            "square": SelectedVariant(
                str(square["spec_sha256"]),
                square_receipt_hash,
                str(square["output_sha256"]),
                PAIRED_DIMENSIONS["square"],
                str(square["thumbnail_sha256"]),
                bool(square_metadata["subtitle"]),
            ),
        },
        font_manifest_sha256=str(portrait["font_manifest_sha256"]),
        selection_source=validated_source,
        selected_at=validated_time,
        privacy={
            "classification": classification,
            "permission_to_publish": permission_to_publish,
        },
    )
    _write_json_atomic(output, asdict(receipt))
    return receipt


def _require_file(path: Path, label: str) -> Path:
    source = _path(path, label)
    try:
        if not source.is_file():
            raise OSError("not a file")
    except (OSError, RuntimeError) as error:
        raise ValueError(f"{label} is missing or invalid: {source}") from error
    return source


def _validate_ppm(payload: bytes) -> tuple[int, int]:
    match = re.match(rb"P6\n([1-9][0-9]*) ([1-9][0-9]*)\n255\n", payload)
    if match is None:
        raise ValueError("ImageMagick returned invalid normalized PPM data")
    width = int(match.group(1))
    height = int(match.group(2))
    if len(payload) - match.end() != width * height * 3:
        raise ValueError("ImageMagick returned incomplete normalized PPM data")
    return width, height


def normalized_image_sha256(path: Path) -> str:
    image = _require_file(path, "artwork image")
    if not shutil.which("magick"):
        raise ValueError("ImageMagick is required for normalized artwork comparison")
    command = [
        "magick",
        str(image),
        "-auto-orient",
        "-alpha",
        "off",
        "-colorspace",
        "sRGB",
        "-depth",
        "8",
        "PPM:-",
    ]
    try:
        result = subprocess.run(command, check=True, capture_output=True)
    except subprocess.CalledProcessError as error:
        detail = (error.stderr or b"").decode("utf-8", errors="replace").strip()
        suffix = f": {detail}" if detail else ""
        raise ValueError(f"ImageMagick artwork normalization failed{suffix}") from error
    except OSError as error:
        raise ValueError("ImageMagick artwork normalization failed") from error
    _validate_ppm(result.stdout)
    return hashlib.sha256(result.stdout).hexdigest()


def normalized_m4b_art_sha256(path: Path) -> str:
    m4b = _require_file(path, "M4B")
    if not shutil.which("ffmpeg"):
        raise ValueError("ffmpeg is required for M4B artwork verification")
    with tempfile.TemporaryDirectory(prefix="cover-art-") as raw:
        extracted = Path(raw) / "art.png"
        command = [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-i",
            str(m4b),
            "-map",
            "0:v:0",
            "-frames:v",
            "1",
            str(extracted),
        ]
        try:
            subprocess.run(command, check=True, capture_output=True)
        except subprocess.CalledProcessError as error:
            detail = (error.stderr or b"").decode("utf-8", errors="replace").strip()
            suffix = f": {detail}" if detail else ""
            raise ValueError(f"ffmpeg M4B artwork extraction failed{suffix}") from error
        except OSError as error:
            raise ValueError("ffmpeg M4B artwork extraction failed") from error
        if not extracted.is_file():
            raise ValueError("ffmpeg M4B artwork extraction produced no image")
        return normalized_image_sha256(extracted)


def verify_package(
    selection_path: Path,
    cover_path: Path,
    *,
    m4b_cover_path: Path | None = None,
    epub_path: Path | None = None,
    m4b_path: Path | None = None,
    receipt_path: Path | None = None,
) -> PackageVerification:
    selected = load_selection(selection_path)
    if isinstance(selected, PairedSelectionReceipt):
        portrait = _path(cover_path, "portrait standalone cover")
        portrait_payload = _read_bytes(portrait, "portrait standalone cover")
        if (
            hashlib.sha256(portrait_payload).hexdigest()
            != selected.variants["portrait"].cover_sha256
        ):
            raise ValueError("portrait standalone cover bytes do not match selection")
        if m4b_cover_path is None:
            raise ValueError("square standalone cover is required for paired selection")
        square = _path(m4b_cover_path, "square standalone cover")
        square_payload = _read_bytes(square, "square standalone cover")
        if (
            hashlib.sha256(square_payload).hexdigest()
            != selected.variants["square"].cover_sha256
        ):
            raise ValueError("square standalone cover bytes do not match selection")
        checks = ["portrait-standalone-bytes", "square-standalone-bytes"]
        if epub_path is not None:
            epub = _require_file(epub_path, "EPUB")
            try:
                with zipfile.ZipFile(epub, "r") as archive:
                    member = discover_cover_member(
                        archive, discover_opf_member(archive)
                    )
                    epub_cover = archive.read(member)
            except ValueError:
                raise
            except (KeyError, OSError, RuntimeError, zipfile.BadZipFile) as error:
                raise ValueError(f"invalid EPUB: {epub}") from error
            if epub_cover != portrait_payload:
                raise ValueError("EPUB portrait cover bytes do not match selection")
            checks.append("epub-portrait-bytes")
        if m4b_path is not None:
            if normalized_m4b_art_sha256(
                _require_file(m4b_path, "M4B")
            ) != normalized_image_sha256(square):
                raise ValueError(
                    "M4B artwork pixels do not match square selected cover"
                )
            checks.append("m4b-square-normalized-pixels")
        if receipt_path is not None:
            delivered = load_selection(receipt_path)
            if asdict(delivered) != asdict(selected):
                raise ValueError(
                    "destination paired selection receipt does not match source"
                )
            checks.append("paired-receipt-identity")
        return PackageVerification(
            selected.book_slug,
            selected.edition_id,
            selected.variants["portrait"].cover_sha256,
            tuple(checks),
        )

    cover = _path(cover_path, "standalone cover")
    cover_payload = _read_bytes(cover, "standalone cover")
    cover_hash = hashlib.sha256(cover_payload).hexdigest()
    if cover_hash != selected.rendered_cover_sha256:
        raise ValueError("standalone cover bytes do not match selection")
    _validate_cover_png(cover_payload, "standalone cover")
    checks = ["standalone-bytes"]

    if epub_path is not None:
        epub = _require_file(epub_path, "EPUB")
        try:
            with zipfile.ZipFile(epub, "r") as archive:
                opf = discover_opf_member(archive)
                member = discover_cover_member(archive, opf)
                epub_cover = archive.read(member)
        except ValueError:
            raise
        except (KeyError, OSError, RuntimeError, zipfile.BadZipFile) as error:
            raise ValueError(f"invalid EPUB: {epub}") from error
        if epub_cover != cover_payload:
            raise ValueError("EPUB cover bytes do not match standalone cover")
        checks.append("epub-cover-bytes")

    if m4b_path is not None:
        m4b = _require_file(m4b_path, "M4B")
        if normalized_m4b_art_sha256(m4b) != normalized_image_sha256(cover):
            raise ValueError("M4B artwork pixels do not match selected cover")
        checks.append("m4b-normalized-pixels")

    if receipt_path is not None:
        delivered = load_selection(receipt_path)
        if asdict(delivered) != asdict(selected):
            raise ValueError("destination selection receipt does not match source")
        checks.append("receipt-identity")

    return PackageVerification(
        book_slug=selected.book_slug,
        edition_id=selected.edition_id,
        rendered_cover_sha256=selected.rendered_cover_sha256,
        checks=tuple(checks),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    select = commands.add_parser("select")
    select.add_argument("--render-receipt", required=True, type=Path)
    select.add_argument("--out", required=True, type=Path)
    select.add_argument("--book-slug", required=True)
    select.add_argument("--edition-id", required=True)
    select.add_argument(
        "--selection-source",
        required=True,
        choices=tuple(sorted(SELECTION_SOURCES)),
    )
    select.add_argument("--selected-at", required=True)
    select.add_argument(
        "--classification",
        required=True,
        choices=tuple(sorted(CLASSIFICATIONS)),
    )
    select.add_argument(
        "--permission-to-publish",
        required=True,
        choices=tuple(sorted(PUBLICATION_PERMISSIONS)),
    )

    select_pair = commands.add_parser("select-pair")
    select_pair.add_argument("--portrait-render-receipt", required=True, type=Path)
    select_pair.add_argument("--square-render-receipt", required=True, type=Path)
    select_pair.add_argument("--out", required=True, type=Path)
    select_pair.add_argument("--book-slug", required=True)
    select_pair.add_argument("--edition-id", required=True)
    select_pair.add_argument(
        "--selection-source",
        required=True,
        choices=tuple(sorted(PAIRED_SELECTION_SOURCES)),
    )
    select_pair.add_argument("--selected-at", required=True)
    select_pair.add_argument(
        "--privacy-classification",
        required=True,
        choices=tuple(sorted(CLASSIFICATIONS)),
    )
    select_pair.add_argument("--permission-to-publish", action="store_true")

    verify = commands.add_parser("verify")
    verify.add_argument("--selection", required=True, type=Path)
    verify.add_argument("--cover", required=True, type=Path)
    verify.add_argument("--m4b-cover", type=Path)
    verify.add_argument("--epub", type=Path)
    verify.add_argument("--m4b", type=Path)
    verify.add_argument("--receipt", type=Path)

    arguments = parser.parse_args()
    if arguments.command == "select":
        result = create_selection(
            arguments.render_receipt,
            arguments.out,
            book_slug=arguments.book_slug,
            edition_id=arguments.edition_id,
            selection_source=arguments.selection_source,
            selected_at=arguments.selected_at,
            classification=arguments.classification,
            permission_to_publish=arguments.permission_to_publish,
        )
    elif arguments.command == "select-pair":
        result = create_paired_selection(
            arguments.portrait_render_receipt,
            arguments.square_render_receipt,
            arguments.out,
            arguments.book_slug,
            arguments.edition_id,
            arguments.selection_source,
            arguments.selected_at,
            arguments.privacy_classification,
            arguments.permission_to_publish,
        )
    else:
        result = verify_package(
            arguments.selection,
            arguments.cover,
            m4b_cover_path=arguments.m4b_cover,
            epub_path=arguments.epub,
            m4b_path=arguments.m4b,
            receipt_path=arguments.receipt,
        )
    print(json.dumps(asdict(result), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
