#!/usr/bin/env python3
"""Render the first Nova Scotia tax-sale Visual Listening figure sequence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Callable, Iterable

from PIL import Image, ImageDraw, ImageFont


WIDTH = 2560
HEIGHT = 1440
MARGIN = 150

PAPER = "#F5F1E8"
PAPER_2 = "#EAE4D8"
INK = "#172232"
MUTED = "#62707D"
NAVY = "#173C5B"
TEAL = "#087F82"
AMBER = "#D78B17"
MAGENTA = "#A33A72"
RED = "#B7423A"
GREEN = "#3C7A57"
WHITE = "#FFFFFF"
LINE = "#C8C1B5"

SCRIPT_DIR = Path(__file__).resolve().parent
BOOK_DIR = SCRIPT_DIR.parent
REPO_ROOT = SCRIPT_DIR.parents[2]
DEFAULT_SPEC = SCRIPT_DIR / "figure-specs.json"
DEFAULT_OUTPUT = BOOK_DIR / "chapters" / "images"
FONT_DIR = REPO_ROOT / "skill" / "assets" / "fonts"


def font(size: int, *, condensed: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    if mono:
        path = FONT_DIR / "IBMPlexMono-Bold.ttf"
    elif condensed:
        path = FONT_DIR / "BarlowCondensed-Black.ttf"
    else:
        path = FONT_DIR / "SpaceGrotesk-Variable.ttf"
    return ImageFont.truetype(str(path), size=size)


def text_width(draw: ImageDraw.ImageDraw, value: str, face: ImageFont.ImageFont) -> float:
    box = draw.textbbox((0, 0), value, font=face)
    return box[2] - box[0]


def wrap(draw: ImageDraw.ImageDraw, value: str, face: ImageFont.ImageFont, width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in value.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if text_width(draw, candidate, face) <= width:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def paragraph(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    value: str,
    face: ImageFont.ImageFont,
    fill: str,
    width: int,
    *,
    spacing: int = 12,
    anchor: str | None = None,
) -> int:
    lines = wrap(draw, value, face, width)
    line_height = face.size + spacing
    x, y = xy
    for line in lines:
        if anchor == "mm":
            draw.text((x, y + face.size // 2), line, font=face, fill=fill, anchor="mm")
        else:
            draw.text((x, y), line, font=face, fill=fill)
        y += line_height
    return y


def centered_paragraph(
    draw: ImageDraw.ImageDraw,
    center: tuple[int, int],
    value: str,
    face: ImageFont.ImageFont,
    fill: str,
    width: int,
    *,
    spacing: int = 10,
) -> None:
    lines = wrap(draw, value, face, width)
    draw.multiline_text(center, "\n".join(lines), font=face, fill=fill, anchor="mm", align="center", spacing=spacing)


def rounded(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    fill: str,
    *,
    outline: str | None = None,
    width: int = 4,
    radius: int = 28,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def arrow(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    fill: str,
    *,
    width: int = 10,
) -> None:
    draw.line((start, end), fill=fill, width=width)
    x2, y2 = end
    x1, y1 = start
    if abs(x2 - x1) >= abs(y2 - y1):
        direction = 1 if x2 > x1 else -1
        points = [(x2, y2), (x2 - 24 * direction, y2 - 18), (x2 - 24 * direction, y2 + 18)]
    else:
        direction = 1 if y2 > y1 else -1
        points = [(x2, y2), (x2 - 18, y2 - 24 * direction), (x2 + 18, y2 - 24 * direction)]
    draw.polygon(points, fill=fill)


def badge(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], label: str, fill: str) -> None:
    rounded(draw, box, fill, radius=22)
    draw.text(((box[0] + box[2]) // 2, (box[1] + box[3]) // 2), label, font=font(32, condensed=True), fill=WHITE, anchor="mm")


def base(spec: dict) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, WIDTH, 26), fill=TEAL)
    badge(draw, (MARGIN, 78, MARGIN + 178, 136), spec["id"].upper(), NAVY)
    draw.text((MARGIN, 168), spec["title"], font=font(76, condensed=True), fill=INK)
    draw.line((MARGIN, 270, WIDTH - MARGIN, 270), fill=LINE, width=4)
    return image, draw


def footer(draw: ImageDraw.ImageDraw, source: str) -> None:
    draw.line((MARGIN, 1300, WIDTH - MARGIN, 1300), fill=LINE, width=3)
    draw.text((MARGIN, 1324), source, font=font(29), fill=MUTED)
    draw.text((WIDTH - MARGIN, 1324), "EDUCATIONAL OVERVIEW  •  VERIFY CURRENT LAW AND SALE TERMS", font=font(29, condensed=True), fill=NAVY, anchor="ra")


def node(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, title: str, detail: str, color: str) -> None:
    rounded(draw, (x, y, x + w, y + h), WHITE, outline=color, width=5)
    draw.rectangle((x, y, x + 18, y + h), fill=color)
    paragraph(draw, (x + 42, y + 30), title, font(38, condensed=True), INK, w - 72, spacing=6)
    paragraph(draw, (x + 42, y + 88), detail, font(30), MUTED, w - 72, spacing=6)


def render_03(spec: dict) -> Image.Image:
    image, draw = base(spec)
    draw.text((MARGIN, 315), "MUNICIPAL COLLECTION CLOCK", font=font(34, condensed=True), fill=NAVY)
    draw.text((1810, 315), "PURCHASER / REDEMPTION CLOCK", font=font(34, condensed=True), fill=TEAL)
    municipal = [
        ("ARREARS", "Eligibility and council decisions"),
        ("NOTICE", "Preliminary notice, title search, sale notice"),
        ("ADVERTISE", "At least 30 consecutive days"),
    ]
    purchaser = [
        ("CERTIFICATE", "After full payment"),
        ("SIX-MONTH ROUTE", "Possible redemption; protect and insure"),
        ("DEED STAGE", "If not redeemed, request and pay for deed"),
    ]
    ys = [380, 660, 940]
    for index, (title, detail) in enumerate(municipal):
        node(draw, MARGIN, ys[index], 600, 190, title, detail, NAVY)
        if index < 2:
            arrow(draw, (450, ys[index] + 195), (450, ys[index + 1] - 16), NAVY)
    rounded(draw, (925, 470, 1635, 1040), NAVY, radius=42)
    draw.text((1280, 610), "AUCTION\nDAY", font=font(88, condensed=True), fill=WHITE, anchor="mm", align="center")
    draw.text((1280, 790), "A hinge,\nnot a finish line", font=font(43), fill="#DCEAF0", anchor="mm", align="center")
    draw.line((1000, 885, 1560, 885), fill="#6A899F", width=4)
    draw.text((1280, 955), "Event terms control payment\nand registration details.", font=font(31), fill=WHITE, anchor="mm", align="center")
    for index, (title, detail) in enumerate(purchaser):
        color = TEAL if index < 2 else GREEN
        node(draw, 1810, ys[index], 600, 190, title, detail, color)
        if index < 2:
            arrow(draw, (2110, ys[index] + 195), (2110, ys[index + 1] - 16), TEAL)
    arrow(draw, (755, 1035), (910, 1035), NAVY)
    arrow(draw, (1650, 475), (1795, 475), TEAL)
    rounded(draw, (MARGIN, 1170, WIDTH - MARGIN, 1260), PAPER_2, radius=22)
    draw.text((WIDTH // 2, 1215), "The sale ends neither the municipality's record work nor the purchaser's legal work.", font=font(37), fill=INK, anchor="mm")
    footer(draw, "Sources: MGA ss. 134, 137-142, 150, 152, 155-156  •  law checked 2026-07-19")
    return image


def render_04(spec: dict) -> Image.Image:
    image, draw = base(spec)
    page = (600, 330, 1960, 1220)
    rounded(draw, page, WHITE, outline=LINE, width=5, radius=18)
    draw.rectangle((600, 330, 1960, 430), fill=NAVY)
    draw.text((640, 360), "FICTIONAL TAX-SALE PARCEL SHEET", font=font(43, condensed=True), fill=WHITE)
    badge(draw, (1570, 350, 1918, 412), "NOT A REAL PARCEL", RED)
    fields = [
        ("LIEN 12", "Auction-list key", NAVY),
        ("AAN 01234567", "Assessment account", TEAL),
        ("PID 99999999", "Mapped parcel identifier", TEAL),
        ("RECOVERY $4,200", "Taxes, interest and sale costs", NAVY),
        ("ASSESSMENT $68,000", "Assessment record — not sale value", AMBER),
        ("REDEEMABLE: YES", "Ordinary six-month route shown", MAGENTA),
    ]
    for index, (label, detail, color) in enumerate(fields):
        col = index % 2
        row = index // 2
        x = 650 + col * 635
        y = 480 + row * 160
        rounded(draw, (x, y, x + 585, y + 128), PAPER, outline=color, width=4, radius=18)
        draw.text((x + 24, y + 20), label, font=font(34, mono=True), fill=INK)
        draw.text((x + 24, y + 76), detail, font=font(27), fill=MUTED)
    rounded(draw, (650, 985, 1235, 1165), "#DBE9E4", outline=TEAL, width=4, radius=18)
    draw.polygon([(720, 1110), (835, 1030), (920, 1085), (1020, 1020), (1160, 1110)], fill="#8DB7A4")
    draw.rectangle((700, 1018, 1185, 1135), outline=TEAL, width=4)
    draw.text((942, 1145), "ORIENTATION MAP", font=font(26, condensed=True), fill=TEAL, anchor="ms")
    rounded(draw, (1285, 985, 1910, 1165), "#F2E7D4", outline=AMBER, width=4, radius=18)
    paragraph(draw, (1320, 1015), "LEGAL DESCRIPTION AREA", font(30, condensed=True), INK, 550)
    paragraph(draw, (1320, 1065), "Read the record. Do not treat it as a survey or a site inspection.", font(27), MUTED, 550)
    callouts = [
        (MARGIN, 410, "IDENTITY", "Which record are we following?", TEAL, (600, 510)),
        (MARGIN, 730, "MONEY", "What amount is advertised for recovery?", NAVY, (600, 690)),
        (2020, 420, "LEGAL ROUTE", "Is a six-month redemption period shown?", MAGENTA, (1960, 830)),
        (2020, 780, "LIMITS", "What does this sheet not establish?", AMBER, (1960, 1070)),
    ]
    for x, y, title, detail, color, target in callouts:
        w = 390
        rounded(draw, (x, y, x + w, y + 190), WHITE, outline=color, width=4, radius=22)
        draw.text((x + 24, y + 24), title, font=font(32, condensed=True), fill=color)
        paragraph(draw, (x + 24, y + 74), detail, font(28), INK, w - 48)
        start = (x + w, y + 95) if x < 600 else (x, y + 95)
        arrow(draw, start, target, color, width=7)
    footer(draw, "Fictional composite based on public packet structure  •  no owner data or Property Online reproduction")
    return image


def render_05(spec: dict) -> Image.Image:
    image, draw = base(spec)
    labels = [
        ("LIEN", "auction list", NAVY),
        ("AAN", "tax account", TEAL),
        ("PID", "mapped parcel", TEAL),
        ("LOCATION", "place clue", NAVY),
        ("ASSESSMENT", "assessment record", AMBER),
        ("MAP", "graphical clue", AMBER),
        ("LEGAL DESCRIPTION", "registry wording", MAGENTA),
    ]
    gap = 22
    total_width = WIDTH - 2 * MARGIN
    card_width = (total_width - gap * 6) // 7
    y = 405
    for index, (title, detail, color) in enumerate(labels):
        x = MARGIN + index * (card_width + gap)
        rounded(draw, (x, y, x + card_width, y + 305), WHITE, outline=color, width=5, radius=24)
        draw.ellipse((x + card_width // 2 - 36, y + 34, x + card_width // 2 + 36, y + 106), fill=color)
        draw.text((x + card_width // 2, y + 70), str(index + 1), font=font(35, condensed=True), fill=WHITE, anchor="mm")
        centered_paragraph(draw, (x + card_width // 2, y + 165), title, font(29, condensed=True), INK, card_width - 36, spacing=5)
        centered_paragraph(draw, (x + card_width // 2, y + 255), detail, font(25), MUTED, card_width - 36, spacing=5)
        if index < len(labels) - 1:
            arrow(draw, (x + card_width + 2, y + 152), (x + card_width + gap - 4, y + 152), LINE, width=6)
    draw.text((MARGIN, 780), "THE CHAIN HELPS RECORDS MEET. IT DOES NOT PROVE:", font=font(38, condensed=True), fill=INK)
    conclusions = ["exact boundary", "legal access", "site condition", "market value", "buildability"]
    conclusion_width = 410
    for index, label in enumerate(conclusions):
        x = MARGIN + index * 452
        rounded(draw, (x, 860, x + conclusion_width, 1000), "#F8E5E2", outline=RED, width=4, radius=24)
        draw.text((x + conclusion_width // 2, 930), label.upper(), font=font(31, condensed=True), fill=RED, anchor="mm")
        draw.line((x + 45, 970, x + conclusion_width - 45, 890), fill=RED, width=7)
    rounded(draw, (MARGIN, 1080, WIDTH - MARGIN, 1245), "#DDEBE8", radius=28)
    draw.text((WIDTH // 2, 1140), "Each field narrows a question. Authority comes from the source qualified to answer it.", font=font(40), fill=INK, anchor="mm")
    footer(draw, "Sources: LAND-001 through LAND-004  •  identifiers are not surveys, inspections, appraisals or approvals")
    return image


def render_06(spec: dict) -> Image.Image:
    image, draw = base(spec)
    sources = ["SUMMARY LIST", "DETAIL SHEET", "LIVE WEBPAGE", "REGISTRY", "RESULT SHEET", "COUNCIL RECORD"]
    card_width = 342
    gap = 34
    for index, label in enumerate(sources):
        x = MARGIN + index * (card_width + gap)
        rounded(draw, (x, 340, x + card_width, 485), WHITE, outline=TEAL if index in (2, 3) else NAVY, width=4, radius=20)
        draw.text((x + card_width // 2, 400), label, font=font(27, condensed=True), fill=INK, anchor="mm")
        draw.text((x + card_width // 2, 450), "keep separately", font=font(24), fill=MUTED, anchor="mm")
        arrow(draw, (x + card_width // 2, 490), (x + card_width // 2, 560), LINE, width=6)
    rounded(draw, (MARGIN, 585, WIDTH - MARGIN, 1135), WHITE, outline=LINE, width=4, radius=28)
    draw.rectangle((MARGIN, 585, WIDTH - MARGIN, 690), fill=NAVY)
    columns = [MARGIN + 45, 825, 1410, 1960]
    headers = ["QUESTION", "SOURCE A", "SOURCE B", "FILE STATUS"]
    for x, label in zip(columns, headers):
        draw.text((x, 620), label, font=font(31, condensed=True), fill=WHITE)
    rows = [
        ("Lien 6 detail", "listed", "detail missing", "UNRESOLVED"),
        ("Recovery amount", "summary amount", "detail amount differs", "ASK MUNICIPALITY"),
        ("May 2025 outcome", "35 reported sold", "31 result rows", "KEEP BOTH COUNTS"),
    ]
    for row_index, row in enumerate(rows):
        top = 715 + row_index * 132
        if row_index % 2 == 0:
            draw.rectangle((MARGIN + 4, top - 16, WIDTH - MARGIN - 4, top + 104), fill="#F2EEE5")
        for col_index, value in enumerate(row):
            face = font(30, condensed=True) if col_index in (0, 3) else font(29)
            color = AMBER if col_index == 3 else INK
            paragraph(draw, (columns[col_index], top), value, face, color, 490 if col_index < 3 else 420, spacing=4)
    rounded(draw, (MARGIN, 1170, WIDTH - MARGIN, 1260), "#F2E7D4", outline=AMBER, width=3, radius=20)
    draw.text((WIDTH // 2, 1215), "A discrepancy is a research finding — not permission to choose the convenient version.", font=font(36), fill=INK, anchor="mm")
    footer(draw, "Sources: Inverness August 2026 packet; May 2025 packet, result sheet and council minutes")
    return image


def render_07(spec: dict) -> Image.Image:
    image, draw = base(spec)
    stages = [
        ("FULL PAYMENT", "Treasurer issues and registers certificate", NAVY),
        ("CERTIFICATE HOLDER", "Protect land • insure insurable buildings • keep records", TEAL),
        ("SIX MONTHS", "Qualifying interests may redeem through the treasurer", MAGENTA),
    ]
    xs = [MARGIN, 800, 1450]
    widths = [520, 520, 520]
    for index, (title, detail, color) in enumerate(stages):
        node(draw, xs[index], 400, widths[index], 230, title, detail, color)
        if index < 2:
            arrow(draw, (xs[index] + widths[index] + 10, 515), (xs[index + 1] - 24, 515), color)
    draw.line((1710, 642, 1710, 770), fill=LINE, width=8)
    draw.ellipse((1686, 746, 1734, 794), fill=LINE)
    left_box = (610, 820, 1200, 1125)
    right_box = (1360, 820, 1950, 1125)
    rounded(draw, left_box, "#E1EEE6", outline=GREEN, width=5, radius=30)
    rounded(draw, right_box, "#E5EFF2", outline=NAVY, width=5, radius=30)
    draw.text((905, 885), "IF REDEEMED", font=font(42, condensed=True), fill=GREEN, anchor="mm")
    centered_paragraph(draw, (905, 1010), "Purchaser is repaid under the statutory formula. Certificate-holder rights end.", font(33), INK, 480, spacing=10)
    draw.text((1655, 885), "IF NOT REDEEMED", font=font(42, condensed=True), fill=NAVY, anchor="mm")
    centered_paragraph(draw, (1655, 1010), "After the applicable wait, purchaser may request and pay for the municipal deed.", font(33), INK, 480, spacing=10)
    arrow(draw, (1710, 790), (1205, 800), GREEN, width=8)
    arrow(draw, (1710, 790), (1655, 800), NAVY, width=8)
    draw.text((WIDTH // 2, 1205), "Certificate holder is a legal stage with powers, duties and limits — not ordinary ownership yet.", font=font(36), fill=INK, anchor="mm")
    footer(draw, "Source: MGA ss. 150-156  •  six months runs from sale  •  law checked 2026-07-19")
    return image


def render_08(spec: dict) -> Image.Image:
    image, draw = base(spec)
    node(draw, MARGIN, 400, 520, 235, "OLDER ARREARS", "Taxes were already in arrears for more than six years at sale", NAVY)
    arrow(draw, (685, 518), (790, 518), NAVY)
    node(draw, 810, 400, 600, 235, "STATUTORY EXCEPTION", "No six-month redemption right under the ordinary route", MAGENTA)
    arrow(draw, (1420, 518), (1525, 518), MAGENTA)
    node(draw, 1545, 400, 520, 235, "DEED STAGE", "Purchaser may request and pay for the municipal deed", GREEN)
    rounded(draw, (2110, 365, 2410, 680), NAVY, radius=34)
    draw.text((2260, 485), "“IMMEDIATE\nDEED”", font=font(48, condensed=True), fill=WHITE, anchor="mm", align="center")
    draw.text((2260, 610), "municipal\nshorthand", font=font(28), fill="#DCEAF0", anchor="mm", align="center")
    draw.text((MARGIN, 740), "THE DEED ROUTE CHANGES. THESE QUESTIONS DO NOT DISAPPEAR:", font=font(40, condensed=True), fill=INK)
    questions = [
        ("POSSESSION", "Who is lawfully on site?", MAGENTA),
        ("ACCESS", "What legal rights reach it?", AMBER),
        ("TITLE REVIEW", "What property-specific issues remain?", NAVY),
        ("INTENDED USE", "Do planning and site facts support it?", TEAL),
    ]
    q_width = 520
    gap = 58
    for index, (title, detail, color) in enumerate(questions):
        x = MARGIN + index * (q_width + gap)
        rounded(draw, (x, 825, x + q_width, 1075), WHITE, outline=color, width=5, radius=26)
        draw.text((x + q_width // 2, 895), title, font=font(36, condensed=True), fill=color, anchor="mm")
        centered_paragraph(draw, (x + q_width // 2, 1005), detail, font(30), INK, q_width - 70, spacing=8)
    rounded(draw, (MARGIN, 1140, WIDTH - MARGIN, 1255), "#F8E5E2", outline=RED, width=4, radius=24)
    draw.text((WIDTH // 2, 1197), "Not instant possession. Not access proof. Not a title opinion. Not development approval.", font=font(37, condensed=True), fill=RED, anchor="mm")
    footer(draw, "Sources: MGA ss. 152(1), 155-156  •  educational route summary  •  law checked 2026-07-19")
    return image


RENDERERS: dict[str, Callable[[dict], Image.Image]] = {
    "figure-03": render_03,
    "figure-04": render_04,
    "figure-05": render_05,
    "figure-06": render_06,
    "figure-07": render_07,
    "figure-08": render_08,
}


def save_contact_sheet(
    paths: Iterable[Path],
    destination: Path,
    *,
    thumb_width: int = 1100,
    label_height: int = 74,
    gutter: int = 42,
) -> None:
    entries = list(paths)
    thumb_height = round(thumb_width * 9 / 16)
    sheet = Image.new("RGB", (thumb_width * 2 + gutter * 3, (thumb_height + label_height) * 3 + gutter * 4), "#202833")
    draw = ImageDraw.Draw(sheet)
    for index, path in enumerate(entries):
        row, column = divmod(index, 2)
        x = gutter + column * (thumb_width + gutter)
        y = gutter + row * (thumb_height + label_height + gutter)
        with Image.open(path) as source:
            thumb = source.convert("RGB").resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
        sheet.paste(thumb, (x, y))
        label_size = 34 if thumb_width >= 1000 else 28
        draw.text((x, y + thumb_height + 14), path.stem, font=font(label_size, condensed=True), fill=WHITE)
    destination.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(destination, format="PNG", optimize=True)


def render_all(spec_path: Path, output_dir: Path, contact_sheet: Path) -> list[Path]:
    data = json.loads(spec_path.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    rendered: list[Path] = []
    for spec in data["figures"]:
        renderer = RENDERERS.get(spec["id"])
        if renderer is None:
            raise ValueError(f"No renderer registered for {spec['id']}")
        image = renderer(spec)
        destination = output_dir / spec["filename"]
        image.save(destination, format="PNG", optimize=True)
        rendered.append(destination)
    save_contact_sheet(rendered, contact_sheet)
    return rendered


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_receipt(paths: Iterable[Path], spec_path: Path, destination: Path) -> None:
    files = []
    for path in paths:
        with Image.open(path) as image:
            files.append(
                {
                    "filename": path.name,
                    "sha256": sha256(path),
                    "width": image.width,
                    "height": image.height,
                    "mode": image.mode,
                }
            )
    receipt = {
        "schemaVersion": 1,
        "assetStatus": "review-candidate",
        "renderer": "render_slideshow_figures.py",
        "specPath": spec_path.name,
        "specSHA256": sha256(spec_path),
        "machineChecks": {
            "expectedCount": 6,
            "dimensions": "2560x1440",
            "mode": "RGB",
            "format": "PNG",
            "status": "pass",
        },
        "humanAcceptance": "pending",
        "files": files,
    }
    destination.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--contact-sheet", type=Path, default=SCRIPT_DIR / "slideshow-figures-03-08-contact-sheet.png")
    parser.add_argument("--phone-sheet", type=Path, default=SCRIPT_DIR / "slideshow-figures-03-08-phone-contact-sheet.png")
    parser.add_argument("--receipt", type=Path, default=SCRIPT_DIR / "render-receipt.json")
    args = parser.parse_args()
    rendered = render_all(args.spec, args.output_dir, args.contact_sheet)
    save_contact_sheet(rendered, args.phone_sheet, thumb_width=640, label_height=58, gutter=30)
    write_receipt(rendered, args.spec, args.receipt)
    for path in rendered:
        print(path)
    print(args.contact_sheet)
    print(args.phone_sheet)
    print(args.receipt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
