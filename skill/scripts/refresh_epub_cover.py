#!/usr/bin/env python3
"""Safely replace the cover image declared by an EPUB package document."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import posixpath
import struct
import tempfile
import zipfile
from copy import copy
from dataclasses import asdict, dataclass
from io import BytesIO
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

from PIL import Image, UnidentifiedImageError


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
EXPECTED_DIMENSIONS = (1600, 2560)


def _zipinfo_metadata(info: zipfile.ZipInfo) -> tuple[object, ...]:
    """Return member metadata that must survive a payload-preserving rewrite."""
    return (
        info.date_time,
        info.compress_type,
        info.comment,
        info.extra,
        info.create_system,
        info.create_version,
        info.extract_version,
        info.reserved,
        info.flag_bits,
        info.volume,
        info.internal_attr,
        info.external_attr,
    )


@dataclass(frozen=True)
class CoverReplacement:
    opf_path: str
    cover_member: str
    width: int
    height: int
    sha256: str


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _safe_member(path: str, *, base: str = "", label: str) -> str:
    parsed = urlsplit(path)
    if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment:
        raise ValueError(f"{label} must be an internal EPUB path")
    decoded = unquote(parsed.path)
    if not decoded or decoded.startswith("/") or "\\" in decoded:
        raise ValueError(f"{label} must be an internal EPUB path")
    combined = posixpath.join(base, decoded) if base else decoded
    normalized = posixpath.normpath(combined)
    if normalized in ("", ".", "..") or normalized.startswith("../"):
        raise ValueError(f"{label} escapes EPUB root")
    return normalized


def discover_opf_member(archive: zipfile.ZipFile) -> str:
    try:
        container_data = archive.read("META-INF/container.xml")
    except KeyError as error:
        raise ValueError("EPUB is missing META-INF/container.xml") from error
    try:
        container = ElementTree.fromstring(container_data)
    except ElementTree.ParseError as error:
        raise ValueError("EPUB container.xml is invalid XML") from error
    paths = [
        element.get("full-path", "")
        for element in container.iter()
        if _local_name(element.tag) == "rootfile"
    ]
    if not paths:
        raise ValueError("EPUB container declares no OPF rootfile")
    if len(paths) != 1:
        raise ValueError("EPUB container declares ambiguous OPF rootfiles")
    opf_member = _safe_member(paths[0], label="OPF rootfile")
    if archive.namelist().count(opf_member) != 1:
        raise ValueError(f"declared OPF member is missing or ambiguous: {opf_member}")
    return opf_member


def discover_cover_member(archive: zipfile.ZipFile, opf_member: str) -> str:
    try:
        package = ElementTree.fromstring(archive.read(opf_member))
    except KeyError as error:
        raise ValueError(f"EPUB is missing declared OPF member: {opf_member}") from error
    except ElementTree.ParseError as error:
        raise ValueError("EPUB OPF is invalid XML") from error

    items = [element for element in package.iter() if _local_name(element.tag) == "item"]
    modern = [
        item
        for item in items
        if "cover-image" in item.get("properties", "").split()
    ]
    if len(modern) > 1:
        raise ValueError("ambiguous cover image: multiple cover-image items")

    candidates = modern
    if not candidates:
        cover_ids = [
            element.get("content", "")
            for element in package.iter()
            if _local_name(element.tag) == "meta" and element.get("name") == "cover"
        ]
        cover_ids = [cover_id for cover_id in cover_ids if cover_id]
        if len(cover_ids) > 1:
            raise ValueError("ambiguous cover image: multiple legacy cover metadata entries")
        if cover_ids:
            candidates = [item for item in items if item.get("id") == cover_ids[0]]
            if len(candidates) > 1:
                raise ValueError("ambiguous cover image: duplicate legacy cover item ID")

    if not candidates:
        raise ValueError("no cover image declared in OPF")
    item = candidates[0]
    href = item.get("href", "")
    media_type = item.get("media-type", "")
    if media_type != "image/png" or not urlsplit(href).path.lower().endswith(".png"):
        raise ValueError("declared cover must be PNG")

    cover_member = _safe_member(
        href,
        base=posixpath.dirname(opf_member),
        label="cover href",
    )
    if archive.namelist().count(cover_member) != 1:
        raise ValueError(f"declared cover member is missing or ambiguous: {cover_member}")
    return cover_member


def png_dimensions(data: bytes) -> tuple[int, int]:
    if data[:8] != PNG_SIGNATURE:
        raise ValueError("cover must be PNG")
    _validate_png_critical_chunks(data)
    try:
        with Image.open(BytesIO(data)) as image:
            if image.format != "PNG":
                raise ValueError("cover must be PNG")
            dimensions = image.size
            image.verify()
        with Image.open(BytesIO(data)) as image:
            if image.format != "PNG" or image.size != dimensions:
                raise ValueError("invalid PNG: inconsistent image metadata")
            image.load()
    except (OSError, SyntaxError, UnidentifiedImageError) as error:
        raise ValueError("invalid PNG: image cannot be decoded") from error
    return dimensions


def _validate_png_critical_chunks(data: bytes) -> None:
    offset = len(PNG_SIGNATURE)
    chunks: list[tuple[bytes, bytes]] = []
    while offset < len(data):
        if len(data) - offset < 12:
            raise ValueError("invalid PNG: truncated chunk")
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        end = offset + 12 + length
        if end > len(data):
            raise ValueError("invalid PNG: truncated chunk data")
        kind = data[offset + 4 : offset + 8]
        chunks.append((kind, data[offset + 8 : offset + 8 + length]))
        offset = end

    kinds = [kind for kind, _ in chunks]
    if not chunks or kinds[0] != b"IHDR" or kinds[-1] != b"IEND":
        raise ValueError("invalid PNG: critical chunks are out of order")
    if kinds.count(b"IHDR") != 1 or kinds.count(b"IEND") != 1:
        raise ValueError("invalid PNG: duplicate critical chunk")
    if len(chunks[0][1]) != 13 or chunks[-1][1]:
        raise ValueError("invalid PNG: malformed IHDR or IEND")
    if not any(kind == b"IDAT" for kind in kinds):
        raise ValueError("invalid PNG: missing image data")

    known_critical = {b"IHDR", b"PLTE", b"IDAT", b"IEND"}
    if any(kind[0] & 0x20 == 0 and kind not in known_critical for kind in kinds):
        raise ValueError("invalid PNG: unknown critical chunk")
    first_idat = kinds.index(b"IDAT")
    last_idat = len(kinds) - 1 - kinds[::-1].index(b"IDAT")
    if any(kind != b"IDAT" for kind in kinds[first_idat : last_idat + 1]):
        raise ValueError("invalid PNG: IDAT chunks must be consecutive")
    if b"PLTE" in kinds and (kinds.count(b"PLTE") != 1 or kinds.index(b"PLTE") > first_idat):
        raise ValueError("invalid PNG: PLTE chunk is out of order")

    color_type = chunks[0][1][9]
    if color_type == 3 and b"PLTE" not in kinds:
        raise ValueError("invalid PNG: indexed color requires PLTE")


def _validate_rebuilt_epub(
    source: zipfile.ZipFile,
    rebuilt: zipfile.ZipFile,
    cover_member: str,
    cover_data: bytes,
) -> None:
    source_names = source.namelist()
    rebuilt_names = rebuilt.namelist()
    if rebuilt_names != source_names:
        raise ValueError("rebuilt EPUB member names or order changed")
    first = rebuilt.infolist()[0]
    if first.filename != "mimetype" or first.compress_type != zipfile.ZIP_STORED:
        raise ValueError("rebuilt EPUB does not preserve stored-first mimetype")
    expected_mimetype = copy(source.getinfo("mimetype"))
    expected_mimetype.compress_type = zipfile.ZIP_STORED
    if _zipinfo_metadata(first) != _zipinfo_metadata(expected_mimetype):
        raise ValueError("rebuilt EPUB mimetype metadata changed")
    for name in source_names:
        actual = rebuilt.read(name)
        if name == cover_member:
            if actual != cover_data:
                raise ValueError("rebuilt EPUB cover bytes do not match input")
        elif actual != source.read(name):
            raise ValueError(f"rebuilt EPUB non-cover payload changed: {name}")
    if png_dimensions(rebuilt.read(cover_member)) != EXPECTED_DIMENSIONS:
        raise ValueError("rebuilt EPUB cover validation failed")


def replace_epub_cover(
    epub_path: Path, cover_path: Path, output_path: Path
) -> CoverReplacement:
    epub_path = Path(epub_path)
    cover_path = Path(cover_path)
    output_path = Path(output_path)
    cover_data = cover_path.read_bytes()
    dimensions = png_dimensions(cover_data)
    if dimensions != EXPECTED_DIMENSIONS:
        raise ValueError(
            f"cover dimensions must be 1600x2560, got {dimensions[0]}x{dimensions[1]}"
        )

    temporary_path: Path | None = None
    try:
        with zipfile.ZipFile(epub_path, "r") as source:
            if source.namelist().count("mimetype") != 1:
                raise ValueError("EPUB must contain exactly one mimetype member")
            opf_member = discover_opf_member(source)
            cover_member = discover_cover_member(source, opf_member)

            output_path.parent.mkdir(parents=True, exist_ok=True)
            descriptor, raw_path = tempfile.mkstemp(
                prefix=f".{output_path.name}.", suffix=".tmp", dir=output_path.parent
            )
            os.close(descriptor)
            temporary_path = Path(raw_path)
            with zipfile.ZipFile(temporary_path, "w") as destination:
                mimetype_info = copy(source.getinfo("mimetype"))
                mimetype_info.compress_type = zipfile.ZIP_STORED
                destination.writestr(mimetype_info, source.read("mimetype"))
                for info in source.infolist():
                    if info.filename == "mimetype":
                        continue
                    payload = cover_data if info.filename == cover_member else source.read(info)
                    destination.writestr(info, payload)

        with zipfile.ZipFile(epub_path, "r") as source, zipfile.ZipFile(
            temporary_path, "r"
        ) as rebuilt:
            _validate_rebuilt_epub(source, rebuilt, cover_member, cover_data)

        os.replace(temporary_path, output_path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    return CoverReplacement(
        opf_path=opf_member,
        cover_member=cover_member,
        width=dimensions[0],
        height=dimensions[1],
        sha256=hashlib.sha256(cover_data).hexdigest(),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epub", required=True, type=Path)
    parser.add_argument("--cover", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    arguments = parser.parse_args()
    result = replace_epub_cover(arguments.epub, arguments.cover, arguments.out)
    print(json.dumps(asdict(result), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
