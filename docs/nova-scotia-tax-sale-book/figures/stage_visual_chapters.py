#!/usr/bin/env python3
"""Stage the current tax-sale review prose with review-only visual cue blocks."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


BOOK_ROOT = Path(__file__).resolve().parents[1]
CHAPTERS_ROOT = BOOK_ROOT / "chapters"
VISUALS_PATH = BOOK_ROOT / "research" / "visuals.md"
ANCHORS_PATH = Path(__file__).with_name("visual-placement-anchors.json")
FIGURE_BLOCK = re.compile(
    r"\n\n<!-- visual-figure-start:figure-\d{2} -->\n"
    r"\n!\[[^\n]*\]\(images/[^\n]+\)\n\n"
    r"<!-- visual-figure-end:figure-\d{2} -->"
)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def parse_visual_register() -> dict[str, dict[str, str | int]]:
    figures: dict[str, dict[str, str | int]] = {}
    row = re.compile(
        r"^\| `(?P<filename>figure-(?P<number>\d{2})-[^`]+\.png)` "
        r"\| (?P<chapter>\d+) \| (?P<job>.*?) \| (?P<source>.*?) "
        r"\| (?P<caption>.*?) \| (?P<alt>.*?) \|$"
    )
    for line in VISUALS_PATH.read_text().splitlines():
        match = row.match(line)
        if not match:
            continue
        data = match.groupdict()
        figure_id = f"figure-{data['number']}"
        figures[figure_id] = {
            "id": figure_id,
            "filename": data["filename"],
            "chapterNumber": int(data["chapter"]),
            "teachingJob": data["job"],
            "provenance": data["source"],
            "caption": data["caption"],
            "altText": data["alt"],
        }
    if len(figures) != 54:
        raise ValueError(f"Expected 54 figure rows in {VISUALS_PATH}, found {len(figures)}")
    return figures


def load_placements() -> list[dict[str, str | int]]:
    register = parse_visual_register()
    anchor_data = json.loads(ANCHORS_PATH.read_text())
    placements = []
    for anchor in anchor_data["placements"]:
        figure = register.get(anchor["id"])
        if figure is None:
            raise ValueError(f"Unknown figure ID in placement manifest: {anchor['id']}")
        expected_chapter = int(anchor["chapter"][2:4])
        if figure["chapterNumber"] != expected_chapter:
            raise ValueError(
                f"{anchor['id']} belongs to chapter {figure['chapterNumber']}, "
                f"not {expected_chapter}"
            )
        placements.append({**figure, **anchor})
    return placements


def figure_block(placement: dict[str, str | int]) -> str:
    caption = str(placement["caption"]).replace('"', "&quot;")
    return (
        f"\n\n<!-- visual-figure-start:{placement['id']} -->\n"
        f"\n![{placement['altText']}](images/{placement['filename']} \"{caption}\")\n\n"
        f"<!-- visual-figure-end:{placement['id']} -->"
    )


def insert_after_anchor(text: str, placement: dict[str, str | int]) -> str:
    anchor = str(placement["anchor"])
    if text.count(anchor) != 1:
        raise ValueError(
            f"{placement['id']} anchor must occur once in {placement['chapter']}; "
            f"found {text.count(anchor)}"
        )
    anchor_index = text.index(anchor)
    paragraph_end = text.find("\n\n", anchor_index)
    if paragraph_end == -1:
        paragraph_end = len(text.rstrip("\n"))
    return text[:paragraph_end] + figure_block(placement) + text[paragraph_end:]


def remove_figure_blocks(text: str) -> str:
    return FIGURE_BLOCK.sub("", text)


def stage_visual_chapters(destination: Path) -> dict[str, object]:
    destination.mkdir(parents=True, exist_ok=True)
    placements = load_placements()
    by_chapter: dict[str, list[dict[str, str | int]]] = {}
    for placement in placements:
        by_chapter.setdefault(str(placement["chapter"]), []).append(placement)

    chapter_receipts = []
    for source in sorted(CHAPTERS_ROOT.glob("ch*.md")):
        original = source.read_text()
        staged = original
        # Insert from the final cue backward so two figures anchored in the same
        # paragraph retain manifest order instead of being reversed.
        for placement in reversed(by_chapter.get(source.name, [])):
            staged = insert_after_anchor(staged, placement)
        if remove_figure_blocks(staged) != original:
            raise ValueError(f"Figure staging changed canonical prose in {source.name}")
        output = destination / source.name
        output.write_text(staged)
        chapter_receipts.append(
            {
                "chapter": source.name,
                "sourceSha256": sha256_text(original),
                "stagedSha256": sha256_text(staged),
                "figureIds": [
                    placement["id"] for placement in by_chapter.get(source.name, [])
                ],
            }
        )

    receipt = {
        "schemaVersion": 1,
        "status": "review-candidate",
        "figureCount": len(placements),
        "proseParity": "exact-after-removing-figures",
        "chapters": chapter_receipts,
    }
    (destination.parent / "visual-placement-receipt.json").write_text(
        json.dumps(receipt, indent=2) + "\n"
    )
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    receipt = stage_visual_chapters(args.destination)
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
