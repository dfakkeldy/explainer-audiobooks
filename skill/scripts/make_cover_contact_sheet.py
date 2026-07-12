#!/usr/bin/env python3
"""Render an ordered JSON cover manifest as a three-column contact sheet."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError


COVER_SIZE = (1600, 2560)
THUMBNAIL_SIZE = (320, 512)
COLUMNS = 3
GUTTER = 24
LABEL_HEIGHT = 52
LABEL_FONT_SIZE = 18
LABEL_FONT_PATH = (
    Path(__file__).resolve().parents[1]
    / "assets"
    / "fonts"
    / "SpaceGrotesk-Variable.ttf"
)
BACKGROUND = "white"
TEXT_COLOR = "black"


@dataclass(frozen=True)
class ContactSheetResult:
    path: Path
    cover_count: int
    columns: int
    rows: int


def _load_label_font() -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(str(LABEL_FONT_PATH), LABEL_FONT_SIZE)
    except OSError as error:
        raise ValueError(
            f"could not load bundled contact-sheet font {LABEL_FONT_PATH}: {error}"
        ) from error


def _validated_entries(entries: Sequence[dict[str, str]]) -> list[tuple[str, Path]]:
    if not entries:
        raise ValueError("contact sheet requires at least one entry")

    validated: list[tuple[str, Path]] = []
    titles: set[str] = set()
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            raise ValueError(f"entry {index}: expected an object")
        title = entry.get("title")
        cover_value = entry.get("cover")
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"entry {index}: title must be a non-empty string")
        if title in titles:
            raise ValueError(f"entry {index}: duplicate title {title!r}")
        if not isinstance(cover_value, str) or not cover_value:
            raise ValueError(f"entry {index} ({title}): cover must be a path string")

        cover = Path(cover_value)
        if not cover.is_file():
            raise ValueError(f"entry {index} ({title}): cover file not found: {cover}")
        try:
            with Image.open(cover) as image:
                dimensions = image.size
                image_format = image.format
                image_mode = image.mode
                image.verify()
        except (OSError, UnidentifiedImageError) as error:
            raise ValueError(f"entry {index} ({title}): invalid cover image: {cover}") from error
        if dimensions != COVER_SIZE:
            raise ValueError(
                f"entry {index} ({title}): cover must be 1600x2560; "
                f"found {dimensions[0]}x{dimensions[1]}"
            )
        if image_format != "PNG":
            raise ValueError(
                f"entry {index} ({title}): cover must use PNG format; "
                f"found {image_format or 'unknown'}"
            )
        if image_mode != "RGB":
            raise ValueError(
                f"entry {index} ({title}): cover must use RGB mode; found {image_mode}"
            )

        titles.add(title)
        validated.append((title, cover))
    return validated


def _ellipsize(
    text: str,
    draw: ImageDraw.ImageDraw,
    font: ImageFont.ImageFont,
    width: int,
) -> str:
    ellipsis = "..."
    candidate = text.rstrip()
    while candidate and draw.textlength(candidate + ellipsis, font=font) > width:
        candidate = candidate[:-1].rstrip()
    return candidate + ellipsis


def _wrapped_label(
    title: str,
    draw: ImageDraw.ImageDraw,
    font: ImageFont.ImageFont,
) -> str:
    """Wrap a title deterministically within the drawable label rectangle."""
    max_width = THUMBNAIL_SIZE[0] - 12
    line_height = draw.textbbox((0, 0), "Ag", font=font)[3]
    max_lines = max(1, (LABEL_HEIGHT - 12) // line_height)
    words = title.split()
    lines: list[str] = []

    while words and len(lines) < max_lines:
        line = words.pop(0)
        if draw.textlength(line, font=font) > max_width:
            line = _ellipsize(line, draw, font, max_width)
        while words:
            candidate = f"{line} {words[0]}"
            if draw.textlength(candidate, font=font) > max_width:
                break
            line = candidate
            words.pop(0)
        lines.append(line)

    if words:
        lines[-1] = _ellipsize(f"{lines[-1]} {' '.join(words)}", draw, font, max_width)
    return "\n".join(lines)


def render(entries: Sequence[dict[str, str]], out: str | Path) -> ContactSheetResult:
    """Render entries in their given order and return details of the PNG output."""
    validated = _validated_entries(entries)
    rows = (len(validated) + COLUMNS - 1) // COLUMNS
    cell_width = THUMBNAIL_SIZE[0]
    cell_height = THUMBNAIL_SIZE[1] + LABEL_HEIGHT
    sheet_width = COLUMNS * cell_width + (COLUMNS - 1) * GUTTER
    sheet_height = rows * cell_height + (rows - 1) * GUTTER
    sheet = Image.new("RGB", (sheet_width, sheet_height), BACKGROUND)
    draw = ImageDraw.Draw(sheet)
    font = _load_label_font()

    for index, (title, cover) in enumerate(validated):
        column = index % COLUMNS
        row = index // COLUMNS
        x = column * (cell_width + GUTTER)
        y = row * (cell_height + GUTTER)
        with Image.open(cover) as image:
            thumbnail = image.convert("RGB").resize(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
            sheet.paste(thumbnail, (x, y))
        label = Image.new("RGB", (cell_width, LABEL_HEIGHT), BACKGROUND)
        label_draw = ImageDraw.Draw(label)
        label_draw.multiline_text(
            (6, 6),
            _wrapped_label(title, label_draw, font),
            fill=TEXT_COLOR,
            font=font,
            spacing=0,
        )
        sheet.paste(label, (x, y + THUMBNAIL_SIZE[1]))

    output = Path(out)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, format="PNG")
    return ContactSheetResult(output, len(validated), COLUMNS, rows)


def _load_manifest(path: Path) -> list[dict[str, str]]:
    try:
        payload: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"could not read JSON manifest {path}: {error}") from error
    if not isinstance(payload, list):
        raise ValueError("manifest must be a JSON array")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        required=True,
        help="ordered JSON array of title/cover entries",
    )
    parser.add_argument("--out", type=Path, required=True, help="output PNG path")
    args = parser.parse_args()
    try:
        render(_load_manifest(args.manifest), args.out)
    except ValueError as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
