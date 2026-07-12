from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

DEFAULT_MANIFEST = Path(__file__).parents[1] / "assets" / "fonts" / "manifest.json"


class CoverFontError(ValueError):
    pass


@dataclass(frozen=True)
class FontRecord:
    font_id: str
    family: str
    style: str
    roles: tuple[str, ...]
    path: Path
    sha256: str
    license: str
    license_path: Path
    license_sha256: str
    source_url: str
    glyph_coverage: tuple[str, ...]
    width_factor: float
    axes: dict[str, tuple[float, float]]


@dataclass(frozen=True)
class FontManifest:
    version: int
    source_commit: str
    path: Path
    sha256: str
    fonts: dict[str, FontRecord]

    def require(self, font_id: str, *, role: str) -> FontRecord:
        if font_id not in self.fonts:
            raise CoverFontError(f"unknown font_id: {font_id}")
        record = self.fonts[font_id]
        if role not in record.roles:
            raise CoverFontError(f"font_id {font_id} does not support role {role}")
        return record


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _safe_asset(root: Path, value: str) -> Path:
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as error:
        raise CoverFontError(f"asset path escapes font directory: {value}") from error
    return candidate


def load_font_manifest(path: Path = DEFAULT_MANIFEST) -> FontManifest:
    manifest_path = Path(path).resolve()
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CoverFontError(f"invalid font manifest: {manifest_path}") from error
    if payload.get("manifest_version") != 1:
        raise CoverFontError("font manifest_version must be 1")
    records: dict[str, FontRecord] = {}
    for raw in payload.get("fonts", []):
        font_id = raw.get("font_id", "")
        if not font_id or font_id in records:
            raise CoverFontError(f"duplicate or empty font_id: {font_id}")
        font_path = _safe_asset(manifest_path.parent, raw.get("path", ""))
        licence_path = _safe_asset(manifest_path.parent, raw.get("license_path", ""))
        if not font_path.is_file() or _digest(font_path) != raw.get("sha256"):
            raise CoverFontError(f"font hash mismatch: {font_id}")
        if not licence_path.is_file() or _digest(licence_path) != raw.get("license_sha256"):
            raise CoverFontError(f"license hash mismatch: {font_id}")
        width_factor = float(raw.get("width_factor", 0))
        if not 0.25 <= width_factor <= 1.0:
            raise CoverFontError(f"invalid width_factor: {font_id}")
        axes = {
            name: (float(bounds[0]), float(bounds[1]))
            for name, bounds in raw.get("axes", {}).items()
        }
        records[font_id] = FontRecord(
            font_id=font_id,
            family=str(raw.get("family", "")),
            style=str(raw.get("style", "")),
            roles=tuple(raw.get("roles", [])),
            path=font_path,
            sha256=str(raw.get("sha256", "")),
            license=str(raw.get("license", "")),
            license_path=licence_path,
            license_sha256=str(raw.get("license_sha256", "")),
            source_url=str(raw.get("source_url", "")),
            glyph_coverage=tuple(raw.get("glyph_coverage", [])),
            width_factor=width_factor,
            axes=axes,
        )
    if not records:
        raise CoverFontError("font manifest contains no fonts")
    return FontManifest(
        version=1,
        source_commit=str(payload.get("source_commit", "")),
        path=manifest_path,
        sha256=_digest(manifest_path),
        fonts=records,
    )
