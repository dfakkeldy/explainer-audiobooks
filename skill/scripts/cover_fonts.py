from __future__ import annotations

import hashlib
import json
import struct
from dataclasses import dataclass
from functools import lru_cache
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


def _uint16(data: bytes, offset: int) -> int:
    if offset < 0 or offset + 2 > len(data):
        raise CoverFontError("truncated TTF cmap")
    return struct.unpack_from(">H", data, offset)[0]


def _uint32(data: bytes, offset: int) -> int:
    if offset < 0 or offset + 4 > len(data):
        raise CoverFontError("truncated TTF cmap")
    return struct.unpack_from(">I", data, offset)[0]


def _format_4_codepoints(table: bytes) -> set[int]:
    length = _uint16(table, 2)
    if length > len(table):
        raise CoverFontError("truncated TTF cmap format 4")
    table = table[:length]
    segment_count = _uint16(table, 6) // 2
    end_codes = 14
    start_codes = end_codes + segment_count * 2 + 2
    deltas = start_codes + segment_count * 2
    range_offsets = deltas + segment_count * 2
    codepoints: set[int] = set()
    for index in range(segment_count):
        start = _uint16(table, start_codes + index * 2)
        end = _uint16(table, end_codes + index * 2)
        delta = _uint16(table, deltas + index * 2)
        range_offset_position = range_offsets + index * 2
        range_offset = _uint16(table, range_offset_position)
        if start > end:
            raise CoverFontError("invalid TTF cmap format 4 segment")
        for codepoint in range(start, end + 1):
            if codepoint == 0xFFFF:
                continue
            if range_offset == 0:
                glyph = (codepoint + delta) & 0xFFFF
            else:
                glyph_position = range_offset_position + range_offset + (codepoint - start) * 2
                glyph = _uint16(table, glyph_position)
                if glyph:
                    glyph = (glyph + delta) & 0xFFFF
            if glyph:
                codepoints.add(codepoint)
    return codepoints


def _format_12_codepoints(table: bytes) -> set[int]:
    length = _uint32(table, 4)
    if length > len(table):
        raise CoverFontError("truncated TTF cmap format 12")
    group_count = _uint32(table, 12)
    codepoints: set[int] = set()
    for index in range(group_count):
        offset = 16 + index * 12
        start = _uint32(table, offset)
        end = _uint32(table, offset + 4)
        first_glyph = _uint32(table, offset + 8)
        if start > end or end > 0x10FFFF:
            raise CoverFontError("invalid TTF cmap format 12 group")
        for codepoint in range(start, end + 1):
            if first_glyph + codepoint - start:
                codepoints.add(codepoint)
    return codepoints


@lru_cache(maxsize=32)
def read_ttf_codepoints(path: Path) -> frozenset[int]:
    data = Path(path).read_bytes()
    table_count = _uint16(data, 4)
    cmap: bytes | None = None
    for index in range(table_count):
        entry = 12 + index * 16
        if entry + 16 > len(data):
            raise CoverFontError("truncated TTF table directory")
        if data[entry:entry + 4] == b"cmap":
            offset = _uint32(data, entry + 8)
            length = _uint32(data, entry + 12)
            if offset + length > len(data):
                raise CoverFontError("truncated TTF cmap table")
            cmap = data[offset:offset + length]
            break
    if cmap is None:
        raise CoverFontError("TTF has no cmap table")
    record_count = _uint16(cmap, 2)
    codepoints: set[int] = set()
    for index in range(record_count):
        record = 4 + index * 8
        platform = _uint16(cmap, record)
        encoding = _uint16(cmap, record + 2)
        if platform != 0 and (platform != 3 or encoding not in {1, 10}):
            continue
        offset = _uint32(cmap, record + 4)
        format_number = _uint16(cmap, offset)
        if format_number == 4:
            codepoints.update(_format_4_codepoints(cmap[offset:]))
        elif format_number == 12:
            codepoints.update(_format_12_codepoints(cmap[offset:]))
    if not codepoints:
        raise CoverFontError("TTF has no supported Unicode cmap format 4 or 12")
    return frozenset(codepoints)


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
