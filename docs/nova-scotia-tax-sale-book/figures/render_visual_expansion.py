#!/usr/bin/env python3
"""Render paired review figures for the approved tax-sale visual expansion.

The two editorial scenes use original image-generation source art. Every map is
a fictional composite, and every remaining frame is a deterministic teaching
diagram. Outputs are review candidates, not governed publication figures.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import subprocess
import sys
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont, ImageOps


PAPER = "#F5F1E8"
PAPER_2 = "#E7E1D6"
INK = "#172232"
MUTED = "#61707C"
NAVY = "#173C5B"
TEAL = "#087F82"
AMBER = "#D78B17"
MAGENTA = "#A33A72"
RED = "#B7423A"
GREEN = "#3C7A57"
WHITE = "#FFFFFF"
LINE = "#C8C1B5"
WATER = "#9FC8D2"
LAND = "#D8DCCB"

SCRIPT_DIR = Path(__file__).resolve().parent
BOOK_DIR = SCRIPT_DIR.parent
REPO_ROOT = SCRIPT_DIR.parents[2]
FONT_DIR = REPO_ROOT / "skill" / "assets" / "fonts"

DEFAULT_PROFILE_SIZES = {
    "landscape": (2560, 1440),
    "mobile": (1080, 1920),
}

PLANNED_FIGURES = (
    "figure-01",
    "figure-02",
    *(f"figure-{number:02d}" for number in range(9, 39)),
)

MOBILE_SUPPORT_FIGURES = (
    "figure-03",
    "figure-04",
    "figure-05",
    "figure-06",
    "figure-07",
    "figure-08",
    "figure-39",
    "figure-40",
)


def entry(
    figure_id: str,
    filename: str,
    chapter: int,
    title: str,
    caption: str,
    kind: str,
    items: Iterable[tuple[str, str, str]] = (),
    **extra: str,
) -> dict:
    return {
        "id": figure_id,
        "filename": filename,
        "chapter": chapter,
        "title": title,
        "caption": caption,
        "kind": kind,
        "items": [
            {"label": label, "detail": detail, "color": color}
            for label, detail, color in items
        ],
        **extra,
    }


FIGURES = {
    "figure-01": entry(
        "figure-01", "figure-01-auction-morning.png", 1,
        "Auction morning is collection work",
        "A tax sale begins as municipal collection work, not a treasure hunt.",
        "scene",
    ),
    "figure-02": entry(
        "figure-02", "figure-02-nova-scotia-municipal-methods.png", 1,
        "One statute, different event methods",
        "Municipal procedure varies even though the provincial legal framework is shared.",
        "municipal-map",
    ),
    "figure-09": entry(
        "figure-09", "figure-09-evidence-desk.png", 4,
        "Build a traceable evidence file",
        "The researcher's product is a traceable evidence file, not a verdict.",
        "scene",
    ),
    "figure-10": entry(
        "figure-10", "figure-10-source-authority-ladder.png", 4,
        "Authority depends on the question",
        "A stronger source is one authorized to answer the particular question.",
        "ladder",
        (
            ("IMAGERY", "What appeared visible on a dated image?", AMBER),
            ("MAP LAYERS", "Where should another record search begin?", AMBER),
            ("MUNICIPAL RECORD", "What did this event publish?", NAVY),
            ("REGISTRY / SURVEY", "What legally identifies the interest and boundary?", MAGENTA),
            ("GOVERNING LAW", "What process and powers apply?", TEAL),
        ),
    ),
    "figure-11": entry(
        "figure-11", "figure-11-beyond-the-packet-delta.png", 4,
        "Credit the packet; add the missing work",
        "The value-add begins after the municipality's facts, map and legal description.",
        "columns",
        (
            ("MUNICIPAL PACKET", "Lien, AAN, PID, recovery amount, assessment, redemption marker, map and legal description.", NAVY),
            ("RESEARCH LAYER", "Reconciliation, planning, terrain, screening limits, dated observations and source log.", TEAL),
            ("HANDOFF LAYER", "Questions for lawyer, surveyor, planner, insurer, inspector and environmental professional.", MAGENTA),
        ),
    ),
    "figure-12": entry(
        "figure-12", "figure-12-five-evidence-labels.png", 4,
        "Five labels keep claims honest",
        "Good research labels the strength and authority of each observation.",
        "columns",
        (
            ("VERIFIED RECORD", "Directly supported by the cited source.", TEAL),
            ("SCREENING CLUE", "A map result that starts a question.", AMBER),
            ("VISUAL INTERPRETATION", "A dated observation, not a verified fact.", AMBER),
            ("PROFESSIONAL VERIFICATION", "The question has reached an authorized expert.", MAGENTA),
            ("NO-GO UNTIL RESOLVED", "The intended use cannot proceed on current evidence.", RED),
        ),
    ),
    "figure-23": entry(
        "figure-23", "figure-23-negative-search-beam.png", 7,
        "A negative search has a beam",
        "No result means only that this search, in this source, found no matching record.",
        "coverage",
        (
            ("TIME", "Was the relevant period included?", NAVY),
            ("PLACE", "Was the parcel inside the source's mapped coverage?", TEAL),
            ("RECORD TYPE", "Would this source contain the event or condition?", AMBER),
            ("MATCH RULE", "Could spelling, geometry or identifiers hide a record?", MAGENTA),
        ),
    ),
    "figure-24": entry(
        "figure-24", "figure-24-title-encumbrance-possession.png", 8,
        "Three questions, not three synonyms",
        "Title, encumbrances and possession are related, but none is a synonym for the others.",
        "columns",
        (
            ("TITLE", "What ownership interest is recorded?", NAVY),
            ("RIGHTS AND BURDENS", "What easements, liens or continuing interests may matter?", MAGENTA),
            ("POSSESSION", "Who or what is actually on the land?", AMBER),
        ),
    ),
    "figure-25": entry(
        "figure-25", "figure-25-occupied-property-handoff.png", 8,
        "Observation stops before self-help",
        "Occupancy questions move from observation to legal advice—not to self-help.",
        "flow",
        (
            ("LAWFUL EXTERIOR OBSERVATION", "Remain off the parcel and avoid confrontation.", AMBER),
            ("PUBLIC RECORDS", "Preserve only bounded, source-backed facts.", TEAL),
            ("LAWYER / TENANCY ADVICE", "Establish the lawful route before contact or entry.", MAGENTA),
            ("STOP", "No lock change, entry, rent demand or goods handling without authority.", RED),
        ),
    ),
    "figure-26": entry(
        "figure-26", "figure-26-inverness-ratio-distribution.png", 9,
        "Thirty-one published rows, bounded",
        "In the 31 published rows, competition often carried bids above the recovery amount.",
        "ratio-chart",
    ),
    "figure-27": entry(
        "figure-27", "figure-27-fifty-thirtyfive-thirtyone.png", 9,
        "Do not collapse three official counts",
        "Advertised, sold and published-result counts answer different questions.",
        "count-chart",
        (
            ("50", "advertised properties", NAVY),
            ("35", "reported sold in council minutes", TEAL),
            ("31", "published result rows", AMBER),
            ("15", "removed before sale", GREEN),
            ("4", "sold-row gap left unresolved", MAGENTA),
        ),
    ),
    "figure-28": entry(
        "figure-28", "figure-28-municipal-result-comparison.png", 9,
        "Definitions travel with the numbers",
        "Cross-municipal numbers are useful only when procedure, sample and denominator travel with them.",
        "columns",
        (
            ("INVERNESS 2025", "31 published rows • median bid/recovery 4.53× • 35 reported sold.", NAVY),
            ("CBRM MAR 2026", "24 recorded sales • median winning/minimum 3.17×.", TEAL),
            ("RICHMOND JUN 2026", "3 sold rows • ratios about 1.33×, 6.59× and 6.28×.", AMBER),
        ),
    ),
    "figure-29": entry(
        "figure-29", "figure-29-all-in-cost-stack.png", 9,
        "The bid is only the first layer",
        "The winning bid is one layer in the acquisition's uncertainty budget.",
        "stack",
        (
            ("BID", "The amount called or tendered.", NAVY),
            ("TAX", "Applicable tax and deed-transfer questions.", TEAL),
            ("LEGAL + REGISTRY", "Advice, searches and registration.", MAGENTA),
            ("SURVEY", "Boundary and access work when needed.", AMBER),
            ("INSURANCE", "Coverage attempts and conditions.", TEAL),
            ("CARRYING", "New taxes, security and time.", NAVY),
            ("REPAIR / REMEDIATION", "Unknown until appropriately investigated.", RED),
            ("POSSESSION", "A separate lawful process if occupied.", MAGENTA),
            ("UNCERTAINTY RESERVE", "A buffer, not hidden optimism.", AMBER),
        ),
    ),
    "figure-30": entry(
        "figure-30", "figure-30-auction-versus-tender.png", 10,
        "Two formats, one written limit",
        "Open bidding reveals competitors; a tender hides them, but both reward a prewritten limit.",
        "two-route",
        (
            ("OPEN AUCTION", "Register • hear live calls • card rises only below the limit.", NAVY),
            ("SEALED TENDER", "Choose once • submit by deadline • no live adjustment.", TEAL),
            ("SAME EVIDENCE FILE", "Eligibility, authority, event terms and walk-away rule do not change.", MAGENTA),
        ),
    ),
    "figure-31": entry(
        "figure-31", "figure-31-certificate-holder-calendar.png", 11,
        "The certificate-holder months are active",
        "The certificate-holder months are an operations period, not dead time.",
        "calendar",
        tuple(
            (f"MONTH {month}", detail, TEAL if month < 6 else MAGENTA)
            for month, detail in enumerate(
                (
                    "Register certificate; organize evidence and insurance attempts.",
                    "Track new taxes, notices and protective-work records.",
                    "Maintain lawful protection; preserve every receipt.",
                    "Refresh status and keep the redemption route open.",
                    "Prepare questions without assuming the outcome.",
                    "Redemption may close the file; otherwise deed work begins.",
                ),
                start=1,
            )
        ),
    ),
    "figure-32": entry(
        "figure-32", "figure-32-deed-is-a-beginning.png", 12,
        "A deed moves the questions",
        "A tax deed changes the file's legal stage; it does not finish the property work.",
        "radial",
        (
            ("TITLE REVIEW", "Lawyer", MAGENTA),
            ("POSSESSION", "Lawful process", RED),
            ("PLANNING", "Written municipal answers", TEAL),
            ("SURVEY", "Boundary and access", AMBER),
            ("CONDITION", "Inspection and environmental review", AMBER),
            ("INSURANCE", "Actual underwriting", NAVY),
        ),
    ),
    "figure-38": entry(
        "figure-38", "figure-38-known-unresolved-professional.png", 13,
        "End with a file that knows its limits",
        "A responsible file separates known facts, unresolved questions and authorized handoffs.",
        "columns",
        (
            ("KNOWN", "Dated, cited facts and bounded observations.", TEAL),
            ("UNRESOLVED", "Questions the current evidence cannot answer.", AMBER),
            ("PROFESSIONAL", "The person or authority qualified to answer next.", MAGENTA),
            ("DECISION", "The bidder owns the choice and its consequences.", NAVY),
        ),
    ),
}

FIGURES.update(
    {
        "figure-03": entry(
            "figure-03", "figure-03-two-clocks.png", 1,
            "Auction day connects two clocks",
            "The sale connects two legal clocks; it does not end either one instantly.",
            "flow",
            (
                ("ARREARS", "Eligibility, council decisions and collection work.", NAVY),
                ("NOTICE", "Title search, preliminary notice and sale notice.", NAVY),
                ("ADVERTISE", "The public event is advertised under the governing route.", NAVY),
                ("CERTIFICATE", "Full payment begins the purchaser's legal stage.", TEAL),
                ("REDEMPTION ROUTE", "Possible redemption, protection and record keeping.", MAGENTA),
                ("DEED STAGE", "If not redeemed, request and pay for the deed.", GREEN),
            ),
        ),
        "figure-04": entry(
            "figure-04", "figure-04-packet-anatomy.png", 2,
            "A parcel sheet is a set of claims",
            "Every field is an identifier or claim to verify, not a promise about the parcel.",
            "columns",
            (
                ("LIEN", "The auction-list key.", NAVY),
                ("AAN", "The assessment account number.", TEAL),
                ("PID", "The mapped parcel identifier.", TEAL),
                ("RECOVERY", "Taxes, interest and stated sale costs.", NAVY),
                ("ASSESSMENT", "An assessment record, not sale value.", AMBER),
                ("REDEMPTION MARKER", "The route shown for this event record.", MAGENTA),
            ),
        ),
        "figure-05": entry(
            "figure-05", "figure-05-identifiers-not-promises.png", 2,
            "Identifiers help records meet",
            "None alone proves boundary, access, condition, value or buildability.",
            "stack",
            (
                ("LIEN", "Auction-list reference.", NAVY),
                ("AAN", "Tax and assessment account.", TEAL),
                ("PID", "Mapped parcel reference.", TEAL),
                ("LOCATION", "A place clue.", NAVY),
                ("ASSESSMENT", "A dated assessment record.", AMBER),
                ("MAP", "A graphical clue, not a survey.", AMBER),
                ("LEGAL DESCRIPTION", "Registry wording requiring interpretation.", MAGENTA),
            ),
        ),
        "figure-06": entry(
            "figure-06", "figure-06-reconcile-the-packet.png", 2,
            "Preserve disagreement between sources",
            "A discrepancy is a research finding, not permission to choose the convenient version.",
            "columns",
            (
                ("SUMMARY LIST", "Keep the published row separately.", NAVY),
                ("DETAIL SHEET", "Record missing or different fields.", NAVY),
                ("LIVE WEBPAGE", "Refresh event status at decision time.", TEAL),
                ("REGISTRY", "Answer only registry-authorized questions.", MAGENTA),
                ("RESULT SHEET", "A dated outcome source, not current value.", AMBER),
                ("COUNCIL RECORD", "Preserve official counts even when they differ.", GREEN),
            ),
        ),
        "figure-07": entry(
            "figure-07", "figure-07-redeemable-route.png", 3,
            "The ordinary redeemable route",
            "A winning bid may begin a six-month certificate-holder period rather than immediate ownership.",
            "flow",
            (
                ("FULL PAYMENT", "The treasurer issues and registers a certificate.", NAVY),
                ("CERTIFICATE HOLDER", "Protect, seek insurance and keep records within legal limits.", TEAL),
                ("SIX MONTHS", "Qualifying interests may redeem through the treasurer.", MAGENTA),
                ("IF REDEEMED", "The statutory repayment route closes certificate-holder rights.", GREEN),
                ("IF NOT REDEEMED", "The purchaser may request and pay for the municipal deed.", NAVY),
            ),
        ),
        "figure-08": entry(
            "figure-08", "figure-08-nonredeemable-route.png", 3,
            "No redemption period is not no uncertainty",
            "Immediate deed changes the redemption route, not possession, access, title or buildability.",
            "flow",
            (
                ("OLDER ARREARS", "The statutory age condition changes the ordinary route.", NAVY),
                ("REDEMPTION EXCEPTION", "No ordinary six-month redemption period.", MAGENTA),
                ("DEED STAGE", "The purchaser may request and pay for the deed.", GREEN),
                ("POSSESSION", "Who is lawfully on site?", RED),
                ("ACCESS", "What legal rights reach the land?", AMBER),
                ("INTENDED USE", "What still requires written confirmation?", TEAL),
            ),
        ),
        "figure-39": entry(
            "figure-39", "figure-39-payment-readiness-clock.png", 10,
            "Payment readiness extends beyond the hammer",
            "The hammer identifies a leading bid; readiness and payment determine whether the sale completes.",
            "flow",
            (
                ("AUTHORIZED", "Identity, authority and conflict checks complete.", NAVY),
                ("FUNDS READY", "Event-accepted payment forms are in hand.", TEAL),
                ("IMMEDIATE PAYMENT", "Pay the amount required immediately by the event terms.", AMBER),
                ("BALANCE DEADLINE", "Meet the verified remaining-balance deadline.", GREEN),
                ("NO SUFFICIENT BID", "The municipality's statutory alternatives remain.", NAVY),
                ("PAYMENT NOT READY", "An immediate re-offer may follow.", RED),
                ("BALANCE MISSED", "Re-advertisement, resale and expenses may follow.", MAGENTA),
            ),
        ),
        "figure-40": entry(
            "figure-40", "figure-40-surplus-proceeds-route.png", 12,
            "Surplus follows a statutory route",
            "Surplus is held and claimed through a statutory route; it is not a purchaser windfall.",
            "flow",
            (
                ("PURCHASE MONEY", "The amount received at the tax sale.", NAVY),
                ("STATUTORY APPLICATIONS", "Taxes, interest, sale expenses and specified municipal amounts.", TEAL),
                ("BALANCE TO SURPLUS", "The remaining balance enters the statutory account.", AMBER),
                ("IF REDEEMED", "The balance affects the statutory redemption formula.", NAVY),
                ("AFTER EXPIRY", "A prior interest holder may need a court application before the endpoint.", MAGENTA),
            ),
        ),
    }
)


MAP_DEFINITIONS = (
    (13, 6, "A", "orientation", "Case A starts with location", "Case A begins with location, not a conclusion about access."),
    (14, 6, "A", "identity", "Case A: identify the research target", "The graphical outline identifies the target; it does not settle the legal boundary."),
    (15, 6, "A", "access", "Case A: a visible route is not a right", "A visible track can be a clue without being a legal right of access."),
    (16, 6, "A", "planning", "Case A: planning and servicing separate", "Planning controls and servicing are separate tests from parcel identity."),
    (17, 7, "A", "screening", "Case A: screening starts harder questions", "A screening map is not an environmental opinion."),
    (18, 7, "B", "orientation", "Case B begins with occupancy clues", "An occupied-looking building changes the question set before possession is discussed."),
    (19, 7, "B", "identity", "Case B: land and structures may diverge", "Land, buildings and a manufactured home may not share one simple record story."),
    (20, 7, "B", "access", "Case B: observe without trespass", "Exterior observation can narrow questions without entry, confrontation or trespass."),
    (21, 8, "B", "planning", "Case B: occupation proves neither use nor services", "Existing occupation does not prove lawful use, services or vacant possession."),
    (22, 8, "B", "screening", "Case B: a historical clue is not a finding", "A mapped historical clue is a lead for professional review, not a contamination finding."),
    (33, 13, "C", "orientation", "Case C is coherent, not recommended", "Case C is the strongest file, not a recommendation to buy."),
    (34, 13, "C", "identity", "Case C: consistent records reduce one unknown", "Consistent records reduce one uncertainty without eliminating the rest."),
    (35, 13, "C", "access", "Case C: strong clues focus the legal question", "Strong map evidence can support a focused legal question; it cannot answer it."),
    (36, 13, "C", "planning", "Case C: name every confirmation", "A coherent file names the confirmations still required before intended use is credible."),
    (37, 13, "C", "screening", "Case C: no mapped overlap is bounded", "No mapped overlap found is not a clean bill of health."),
)

for number, chapter, case, purpose, title, caption in MAP_DEFINITIONS:
    figure_id = f"figure-{number:02d}"
    FIGURES[figure_id] = entry(
        figure_id,
        f"{figure_id}-case-{case.lower()}-{purpose}.png",
        chapter,
        title,
        caption,
        "case-map",
        case=case,
        purpose=purpose,
    )


def face(size: int, *, condensed: bool = False) -> ImageFont.FreeTypeFont:
    font_name = "BarlowCondensed-Black.ttf" if condensed else "SpaceGrotesk-Variable.ttf"
    return ImageFont.truetype(str(FONT_DIR / font_name), max(9, size))


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if text_width(draw, candidate, font) <= width:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill: str,
    width: int,
    *,
    spacing: int,
    max_lines: int | None = None,
) -> int:
    lines = wrap(draw, text, font, width)
    if max_lines is not None:
        lines = lines[:max_lines]
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += font.size + spacing
    return y


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: str, *, outline: str | None = None, width: int = 3, radius: int = 24) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_header(draw: ImageDraw.ImageDraw, spec: dict, size: tuple[int, int]) -> tuple[int, int]:
    width, height = size
    margin = round(width * 0.065)
    header_bottom = round(height * 0.22)
    draw.rectangle((0, 0, width, max(8, round(height * 0.012))), fill=TEAL)
    badge_height = max(28, round(height * 0.045))
    badge_width = max(120, round(width * 0.18))
    rounded(draw, (margin, round(height * 0.045), margin + badge_width, round(height * 0.045) + badge_height), NAVY, radius=max(9, round(badge_height * 0.32)))
    draw.text((margin + badge_width // 2, round(height * 0.045) + badge_height // 2), spec["id"].upper(), font=face(round(badge_height * 0.52), condensed=True), fill=WHITE, anchor="mm")
    title_size = round(height * (0.042 if height > width else 0.055))
    draw_wrapped(draw, (margin, round(height * 0.105)), spec["title"], face(title_size, condensed=True), INK, width - margin * 2, spacing=max(2, title_size // 10), max_lines=2)
    draw.line((margin, header_bottom, width - margin, header_bottom), fill=LINE, width=max(2, round(height * 0.002)))
    return margin, header_bottom


def draw_footer(draw: ImageDraw.ImageDraw, spec: dict, size: tuple[int, int]) -> None:
    width, height = size
    margin = round(width * 0.065)
    top = round(height * 0.90)
    draw.line((margin, top, width - margin, top), fill=LINE, width=max(2, round(height * 0.002)))
    caption_size = round(height * (0.021 if height > width else 0.022))
    draw_wrapped(draw, (margin, top + round(height * 0.014)), spec["caption"], face(caption_size), INK, width - margin * 2, spacing=max(2, caption_size // 7), max_lines=2)
    draw.text((width - margin, height - round(height * 0.022)), "REVIEW CANDIDATE  •  VERIFY SOURCES  •  NOT A RECOMMENDATION", font=face(max(10, round(height * 0.014)), condensed=True), fill=MUTED, anchor="ra")


def card_layout(spec: dict, size: tuple[int, int]) -> dict:
    width, height = size
    margin = round(width * 0.065)
    content_top = round(height * 0.22)
    content_bottom = round(height * 0.875)
    items = spec["items"]
    portrait = height > width
    if spec["kind"] == "stack":
        columns = 1 if portrait else 3
    elif portrait:
        columns = 1 if len(items) <= 6 else 2
    else:
        columns = min(3, max(1, len(items)))
    rows = math.ceil(len(items) / columns)
    gap = max(8, round(min(width, height) * (0.012 if rows >= 7 else 0.025)))
    available_width = width - 2 * margin - gap * (columns - 1)
    available_height = content_bottom - content_top - round(height * 0.035) - gap * (rows - 1)
    card_width = available_width // columns
    card_height = available_height // rows
    label_size = min(
        max(11, round(height * (0.026 if portrait else 0.027))),
        max(11, round(card_height * 0.27)),
    )
    detail_size = min(
        max(10, round(height * (0.020 if portrait else 0.021))),
        max(10, round(card_height * 0.18)),
    )
    dense = card_height < round(height * 0.09)
    return {
        "margin": margin,
        "content_top": content_top,
        "content_bottom": content_bottom,
        "columns": columns,
        "rows": rows,
        "gap": gap,
        "card_width": card_width,
        "card_height": card_height,
        "start_y": content_top + round(height * 0.03),
        "label_size": label_size,
        "detail_size": detail_size,
        "label_max_lines": 1 if dense else 2,
        "detail_max_lines": 2 if dense else 4,
    }


def card_layout_overflows(spec: dict, size: tuple[int, int]) -> list[str]:
    layout = card_layout(spec, size)
    image = Image.new("RGB", (8, 8), WHITE)
    draw = ImageDraw.Draw(image)
    strip = max(8, round(layout["card_width"] * 0.025))
    text_width_available = layout["card_width"] - strip * 4
    failures = []
    for item in spec["items"]:
        label_font = face(layout["label_size"], condensed=True)
        detail_font = face(layout["detail_size"])
        label_lines = wrap(draw, item["label"], label_font, text_width_available)
        detail_lines = wrap(draw, item["detail"], detail_font, text_width_available)
        if len(label_lines) > layout["label_max_lines"] or len(detail_lines) > layout["detail_max_lines"]:
            failures.append(item["label"])
            continue
        label_spacing = max(2, layout["label_size"] // 8)
        detail_spacing = max(2, layout["detail_size"] // 7)
        used = round(layout["card_height"] * 0.13)
        used += len(label_lines) * (layout["label_size"] + label_spacing)
        used += round(layout["card_height"] * 0.05)
        used += len(detail_lines) * (layout["detail_size"] + detail_spacing)
        if used > round(layout["card_height"] * 0.92):
            failures.append(item["label"])
    image.close()
    return failures


def render_scene(spec: dict, source: Path, size: tuple[int, int]) -> Image.Image:
    with Image.open(source) as opened:
        image = ImageOps.fit(opened.convert("RGB"), size, method=Image.Resampling.LANCZOS)
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    width, height = size
    band = round(height * 0.13)
    draw.rectangle((0, 0, width, band), fill=(23, 60, 91, 220))
    margin = round(width * 0.06)
    draw.text((margin, round(height * 0.025)), spec["id"].upper(), font=face(round(height * 0.022), condensed=True), fill=WHITE)
    draw_wrapped(draw, (margin, round(height * 0.056)), spec["title"], face(round(height * 0.035), condensed=True), WHITE, width - 2 * margin, spacing=max(2, round(height * 0.004)), max_lines=2)
    footer_height = round(height * 0.115)
    draw.rectangle((0, height - footer_height, width, height), fill=(245, 241, 232, 235))
    draw_wrapped(draw, (margin, height - footer_height + round(height * 0.018)), spec["caption"], face(round(height * 0.024)), INK, width - 2 * margin, spacing=max(2, round(height * 0.003)), max_lines=2)
    return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")


def render_cards(spec: dict, size: tuple[int, int]) -> Image.Image:
    width, height = size
    image = Image.new("RGB", size, PAPER)
    draw = ImageDraw.Draw(image)
    margin, _ = draw_header(draw, spec, size)
    items = spec["items"]
    layout = card_layout(spec, size)
    columns = layout["columns"]
    gap = layout["gap"]
    card_width = layout["card_width"]
    card_height = layout["card_height"]
    start_y = layout["start_y"]
    for index, item in enumerate(items):
        row, column = divmod(index, columns)
        x = margin + column * (card_width + gap)
        y = start_y + row * (card_height + gap)
        color = item["color"]
        rounded(draw, (x, y, x + card_width, y + card_height), WHITE, outline=color, width=max(2, round(min(size) * 0.004)), radius=max(10, round(min(size) * 0.018)))
        strip = max(8, round(card_width * 0.025))
        draw.rounded_rectangle((x, y, x + strip * 2, y + card_height), radius=max(6, strip), fill=color)
        label_size = layout["label_size"]
        detail_size = layout["detail_size"]
        text_x = x + strip * 3
        text_width_available = card_width - strip * 4
        label_bottom = draw_wrapped(draw, (text_x, y + round(card_height * 0.13)), item["label"], face(label_size, condensed=True), color, text_width_available, spacing=max(2, label_size // 8), max_lines=layout["label_max_lines"])
        draw_wrapped(draw, (text_x, label_bottom + round(card_height * 0.05)), item["detail"], face(detail_size), INK, text_width_available, spacing=max(2, detail_size // 7), max_lines=layout["detail_max_lines"])
    draw_footer(draw, spec, size)
    return image


def render_ratio_chart(spec: dict, size: tuple[int, int]) -> Image.Image:
    width, height = size
    image = Image.new("RGB", size, PAPER)
    draw = ImageDraw.Draw(image)
    margin, content_top = draw_header(draw, spec, size)
    portrait = height > width
    chart_top = content_top + round(height * 0.05)
    chart_bottom = round(height * 0.77)
    rounded(draw, (margin, chart_top, width - margin, chart_bottom), WHITE, outline=LINE, width=max(2, round(height * 0.002)), radius=max(12, round(height * 0.018)))
    bands = [
        ("UNDER 5×", 16, NAVY),
        ("5× TO UNDER 10×", 8, AMBER),
        ("10× OR MORE", 7, MAGENTA),
    ]
    band_height = (chart_bottom - chart_top - round(height * 0.12)) // 3
    for index, (label, count, color) in enumerate(bands):
        y = chart_top + round(height * 0.08) + index * band_height
        draw.text((margin + round(width * 0.04), y), label, font=face(round(height * 0.024), condensed=True), fill=color)
        start_x = margin + round(width * (0.34 if portrait else 0.24))
        dot_radius = max(4, round(min(size) * 0.009))
        per_row = 8 if portrait else 16
        for dot in range(count):
            dot_row, dot_column = divmod(dot, per_row)
            x = start_x + dot_column * dot_radius * 3
            dot_y = y + dot_row * dot_radius * 3
            draw.ellipse((x - dot_radius, dot_y - dot_radius, x + dot_radius, dot_y + dot_radius), fill=color)
        draw.text((width - margin - round(width * 0.04), y), str(count), font=face(round(height * 0.031), condensed=True), fill=color, anchor="ra")
    draw.text((margin + round(width * 0.04), chart_bottom - round(height * 0.07)), "31 PUBLISHED ROWS  •  MEDIAN 4.53×  •  RANGE 1.00×–21.62×", font=face(round(height * 0.021), condensed=True), fill=INK)
    draw.text((margin + round(width * 0.04), chart_bottom - round(height * 0.035)), "Threshold grouping uses exact reported counts; dots do not represent exact row positions.", font=face(round(height * 0.016)), fill=MUTED)
    draw_footer(draw, spec, size)
    return image


def map_panel(draw: ImageDraw.ImageDraw, spec: dict, box: tuple[int, int, int, int], size: tuple[int, int]) -> None:
    left, top, right, bottom = box
    width = right - left
    height = bottom - top
    seed = int(spec["id"].split("-")[-1])
    randomizer = random.Random(seed)
    draw.rectangle(box, fill=LAND, outline=LINE, width=max(2, round(min(size) * 0.003)))
    for row in range(1, 7):
        y = top + row * height // 7
        draw.line((left, y, right, y), fill="#CFD4C6", width=1)
    for column in range(1, 7):
        x = left + column * width // 7
        draw.line((x, top, x, bottom), fill="#CFD4C6", width=1)
    water_edge = left + round(width * 0.78)
    water_points = [(right, top), (right, bottom), (water_edge, bottom)]
    for step in range(7, -1, -1):
        y = top + step * height // 7
        x = water_edge + randomizer.randint(-round(width * 0.05), round(width * 0.04))
        water_points.append((x, y))
    draw.polygon(water_points, fill=WATER)
    road_width = max(3, round(min(size) * 0.009))
    draw.line((left - road_width, bottom - round(height * 0.16), right, top + round(height * 0.28)), fill=WHITE, width=road_width * 2)
    draw.line((left - road_width, bottom - round(height * 0.16), right, top + round(height * 0.28)), fill="#A38D72", width=road_width)
    draw.line((left + round(width * 0.12), top, left + round(width * 0.58), bottom), fill=WHITE, width=max(3, road_width))
    case = spec["case"]
    if case == "A":
        parcel = [
            (left + round(width * 0.35), top + round(height * 0.25)),
            (left + round(width * 0.43), top + round(height * 0.22)),
            (left + round(width * 0.57), top + round(height * 0.75)),
            (left + round(width * 0.48), top + round(height * 0.79)),
        ]
    elif case == "B":
        parcel = [
            (left + round(width * 0.30), top + round(height * 0.31)),
            (left + round(width * 0.58), top + round(height * 0.29)),
            (left + round(width * 0.60), top + round(height * 0.68)),
            (left + round(width * 0.32), top + round(height * 0.71)),
        ]
    else:
        parcel = [
            (left + round(width * 0.28), top + round(height * 0.28)),
            (left + round(width * 0.62), top + round(height * 0.24)),
            (left + round(width * 0.67), top + round(height * 0.65)),
            (left + round(width * 0.42), top + round(height * 0.76)),
            (left + round(width * 0.25), top + round(height * 0.57)),
        ]
    draw.polygon(parcel, fill="#E9C66C", outline=AMBER)
    draw.line(parcel + [parcel[0]], fill=AMBER, width=max(3, round(min(size) * 0.008)), joint="curve")
    center_x = sum(point[0] for point in parcel) // len(parcel)
    center_y = sum(point[1] for point in parcel) // len(parcel)
    draw.text((center_x, center_y), f"CASE {case}", font=face(max(10, round(min(size) * 0.032)), condensed=True), fill=INK, anchor="mm")
    purpose = spec["purpose"]
    if purpose == "identity":
        draw.rectangle((center_x - road_width * 4, center_y - road_width * 3, center_x + road_width * 4, center_y + road_width * 3), outline=TEAL, width=road_width)
    elif purpose == "access":
        draw.line((left + round(width * 0.08), top + round(height * 0.78), center_x, center_y), fill=RED, width=max(3, road_width // 2))
        draw.text((left + round(width * 0.14), top + round(height * 0.72)), "VISIBLE TRACK?", font=face(max(10, round(min(size) * 0.021)), condensed=True), fill=RED)
    elif purpose == "planning":
        draw.rectangle((left, top, left + round(width * 0.28), bottom), fill="#D6E8E4")
        draw.rectangle((left + round(width * 0.67), top, right, bottom), fill="#EBDCC4")
        draw.line(parcel + [parcel[0]], fill=AMBER, width=max(3, road_width), joint="curve")
        draw.text((left + round(width * 0.08), top + round(height * 0.12)), "ZONE A", font=face(max(10, round(min(size) * 0.022)), condensed=True), fill=TEAL)
        draw.text((left + round(width * 0.76), top + round(height * 0.12)), "ZONE?", font=face(max(10, round(min(size) * 0.022)), condensed=True), fill=AMBER)
    elif purpose == "screening":
        radius = max(10, round(min(size) * 0.035))
        for offset_x, offset_y, color in ((0.20, 0.35, TEAL), (0.66, 0.52, MAGENTA), (0.50, 0.18, AMBER)):
            x = left + round(width * offset_x)
            y = top + round(height * offset_y)
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline=color, width=max(2, road_width // 2))
    if case == "B":
        house_w = round(width * 0.07)
        house_h = round(height * 0.07)
        draw.rectangle((center_x - house_w, center_y - house_h, center_x + house_w, center_y + house_h), fill=NAVY)
    draw.text((left + round(width * 0.025), top + round(height * 0.035)), "FICTIONAL COMPOSITE  •  NOT A SURVEY", font=face(max(9, round(min(size) * 0.018)), condensed=True), fill=NAVY)
    draw.text((right - round(width * 0.025), bottom - round(height * 0.035)), "N ↑", font=face(max(10, round(min(size) * 0.024)), condensed=True), fill=INK, anchor="ra")


def map_items(spec: dict) -> list[tuple[str, str, str]]:
    purpose = spec["purpose"]
    case = spec["case"]
    if purpose == "orientation":
        return [
            ("PLACE", f"Locate fictional Case {case} among roads, communities and water.", NAVY),
            ("LIMIT", "Orientation does not prove access, title, condition or services.", RED),
        ]
    if purpose == "identity":
        return [
            ("LIEN / AAN / PID", f"Fictional Case {case} identifiers point to one research target.", TEAL),
            ("BOUNDARY", "The graphical outline is not a survey or title opinion.", AMBER),
        ]
    if purpose == "access":
        return [
            ("VISIBLE APPROACH", "A road or track on a map is a screening clue.", AMBER),
            ("LEGAL ACCESS", "Registry and legal review must answer the right-of-way question.", MAGENTA),
            ("TERRAIN", "Contours and drainage change site questions, not legal rights.", TEAL),
        ]
    if purpose == "planning":
        return [
            ("ZONE", "Confirm the current rule and intended use in writing.", TEAL),
            ("FRONTAGE", "Mapped contact is not a survey measurement.", AMBER),
            ("SERVICES", "Well, septic, water and sewer require separate evidence.", MAGENTA),
        ]
    return [
        ("SEARCHED LAYERS", "Coverage, date and category limits stay visible.", TEAL),
        ("SCREENING CLUE", "A mapped point or overlap starts another records question.", AMBER),
        ("NO RESULT", "No mapped overlap is not a clean bill of health.", RED),
    ]


def render_case_map(spec: dict, size: tuple[int, int]) -> Image.Image:
    width, height = size
    image = Image.new("RGB", size, PAPER)
    draw = ImageDraw.Draw(image)
    margin, content_top = draw_header(draw, spec, size)
    portrait = height > width
    if portrait:
        map_box = (margin, content_top + round(height * 0.025), width - margin, round(height * 0.62))
        info_top = round(height * 0.65)
        info_bottom = round(height * 0.875)
        columns = 1
    else:
        map_box = (margin, content_top + round(height * 0.035), round(width * 0.67), round(height * 0.865))
        info_top = content_top + round(height * 0.035)
        info_bottom = round(height * 0.865)
        columns = 1
    map_panel(draw, spec, map_box, size)
    items = map_items(spec)
    if portrait:
        gap = round(height * 0.012)
        card_height = (info_bottom - info_top - gap * (len(items) - 1)) // len(items)
        card_left, card_right = margin, width - margin
    else:
        gap = round(height * 0.02)
        card_height = (info_bottom - info_top - gap * (len(items) - 1)) // len(items)
        card_left, card_right = round(width * 0.70), width - margin
    for index, (label, detail, color) in enumerate(items):
        top = info_top + index * (card_height + gap)
        rounded(draw, (card_left, top, card_right, top + card_height), WHITE, outline=color, width=max(2, round(min(size) * 0.004)), radius=max(10, round(min(size) * 0.018)))
        x = card_left + round((card_right - card_left) * 0.06)
        draw.text((x, top + round(card_height * 0.14)), label, font=face(round(height * 0.022), condensed=True), fill=color)
        draw_wrapped(draw, (x, top + round(card_height * 0.42)), detail, face(round(height * 0.017)), INK, round((card_right - card_left) * 0.86), spacing=max(2, round(height * 0.003)), max_lines=3)
    draw_footer(draw, spec, size)
    return image


def render_municipal_map(spec: dict, size: tuple[int, int]) -> Image.Image:
    width, height = size
    image = Image.new("RGB", size, PAPER)
    draw = ImageDraw.Draw(image)
    margin, content_top = draw_header(draw, spec, size)
    portrait = height > width
    map_left = margin
    map_top = content_top + round(height * 0.03)
    map_right = width - margin
    map_bottom = round(height * (0.70 if portrait else 0.82))
    rounded(draw, (map_left, map_top, map_right, map_bottom), "#DDE6E2", outline=LINE, width=max(2, round(height * 0.002)), radius=max(12, round(height * 0.018)))
    if portrait:
        silhouette = [
            (0.47, 0.05), (0.58, 0.12), (0.52, 0.28), (0.64, 0.39),
            (0.55, 0.55), (0.45, 0.67), (0.40, 0.91), (0.28, 0.78),
            (0.36, 0.58), (0.30, 0.42), (0.40, 0.28),
        ]
    else:
        silhouette = [
            (0.34, 0.08), (0.45, 0.15), (0.48, 0.30), (0.61, 0.40),
            (0.56, 0.56), (0.45, 0.70), (0.42, 0.92), (0.28, 0.78),
            (0.32, 0.56), (0.23, 0.42), (0.30, 0.26),
        ]
    polygon = [
        (map_left + round((map_right - map_left) * x), map_top + round((map_bottom - map_top) * y))
        for x, y in silhouette
    ]
    draw.polygon(polygon, fill="#BED0C3", outline=TEAL)
    methods = [
        ("INVERNESS", "auction", 0.35, 0.27, NAVY),
        ("CBRM", "auction", 0.56, 0.45, NAVY),
        ("RICHMOND", "auction", 0.53, 0.61, NAVY),
        ("PICTOU", "tender", 0.43, 0.47, MAGENTA),
        ("ANNAPOLIS", "auction + tender", 0.32, 0.69, AMBER),
        ("KINGS", "auction record", 0.28, 0.60, TEAL),
        ("CHESTER", "check current notice", 0.36, 0.53, RED),
    ]
    dot_radius = max(5, round(min(size) * 0.009))
    for name, method, x_ratio, y_ratio, color in methods:
        x = map_left + round((map_right - map_left) * x_ratio)
        y = map_top + round((map_bottom - map_top) * y_ratio)
        draw.ellipse((x - dot_radius, y - dot_radius, x + dot_radius, y + dot_radius), fill=color, outline=WHITE)
        label_x = x + dot_radius * 2
        draw.text((label_x, y - dot_radius), name, font=face(max(10, round(height * 0.018)), condensed=True), fill=INK)
        draw.text((label_x, y + dot_radius), method, font=face(max(9, round(height * 0.014))), fill=MUTED)
    draw.text((map_left + round((map_right - map_left) * 0.04), map_bottom - round(height * 0.045)), "DATED PROCEDURAL EXAMPLES  •  REFRESH THE EVENT NOTICE", font=face(round(height * 0.017), condensed=True), fill=NAVY)
    draw_footer(draw, spec, size)
    return image


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def save_contact_sheet(paths: list[Path], destination: Path, profile: str) -> None:
    thumb_size = (360, 202) if profile == "landscape" else (180, 320)
    columns = 4 if profile == "landscape" else 6
    rows = math.ceil(len(paths) / columns)
    gutter = 24
    label_height = 34
    sheet = Image.new("RGB", (columns * thumb_size[0] + (columns + 1) * gutter, rows * (thumb_size[1] + label_height) + (rows + 1) * gutter), "#202833")
    draw = ImageDraw.Draw(sheet)
    for index, path in enumerate(paths):
        row, column = divmod(index, columns)
        x = gutter + column * (thumb_size[0] + gutter)
        y = gutter + row * (thumb_size[1] + label_height + gutter)
        with Image.open(path) as source:
            thumb = ImageOps.fit(source.convert("RGB"), thumb_size, method=Image.Resampling.LANCZOS)
        sheet.paste(thumb, (x, y))
        draw.text((x, y + thumb_size[1] + 7), path.stem, font=face(18, condensed=True), fill=WHITE)
    destination.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(destination, format="PNG", optimize=True)
    sheet.close()


def render_review_set(
    output_root: Path,
    *,
    scene_sources: dict[str, dict[str, Path]],
    profile_sizes: dict[str, tuple[int, int]] | None = None,
    figure_ids: Iterable[str] | None = None,
) -> dict:
    sizes = profile_sizes or DEFAULT_PROFILE_SIZES
    selected = tuple(figure_ids or PLANNED_FIGURES)
    missing = set(selected) - set(FIGURES)
    if missing:
        raise ValueError(f"Missing figure specifications: {sorted(missing)}")
    receipt = {
        "schemaVersion": 1,
        "assetStatus": "review-candidate",
        "scope": "paired visual review figures: " + ", ".join(selected),
        "profiles": {},
        "figures": [],
        "boundaries": [
            "Fictional composite maps are teaching diagrams, not surveys or parcel evidence.",
            "Generated scenes are editorial illustrations, not documentary depictions.",
            "No figure is governed, accepted, syncable or publishable until human and device review pass.",
        ],
    }
    outputs_by_profile: dict[str, list[Path]] = {}
    figure_rows: dict[str, dict] = {}
    for profile, size in sizes.items():
        destination_dir = output_root / profile
        destination_dir.mkdir(parents=True, exist_ok=True)
        outputs_by_profile[profile] = []
        receipt["profiles"][profile] = {"width": size[0], "height": size[1]}
        for figure_id in selected:
            spec = FIGURES[figure_id]
            if spec["kind"] == "scene":
                try:
                    source = Path(scene_sources[figure_id][profile])
                except KeyError as error:
                    raise ValueError(f"Missing {profile} scene source for {figure_id}") from error
                image = render_scene(spec, source, size)
                source_hash = sha256(source)
            elif spec["kind"] == "case-map":
                image = render_case_map(spec, size)
                source_hash = None
            elif spec["kind"] == "municipal-map":
                image = render_municipal_map(spec, size)
                source_hash = None
            elif spec["kind"] == "ratio-chart":
                image = render_ratio_chart(spec, size)
                source_hash = None
            else:
                image = render_cards(spec, size)
                source_hash = None
            path = destination_dir / spec["filename"]
            image.save(path, format="PNG", optimize=True)
            image.close()
            outputs_by_profile[profile].append(path)
            row = figure_rows.setdefault(
                figure_id,
                {
                    "id": figure_id,
                    "filename": spec["filename"],
                    "chapter": spec["chapter"],
                    "title": spec["title"],
                    "caption": spec["caption"],
                    "kind": spec["kind"],
                    "renditions": {},
                },
            )
            rendition = {
                "path": str(path),
                "sha256": sha256(path),
                "width": size[0],
                "height": size[1],
            }
            if source_hash:
                rendition["sourceSHA256"] = source_hash
            row["renditions"][profile] = rendition
    for profile, paths in outputs_by_profile.items():
        save_contact_sheet(paths, output_root / f"visual-expansion-{profile}-contact-sheet.png", profile)
    receipt["figures"] = [figure_rows[figure_id] for figure_id in selected]
    return receipt


def merge_profile_receipts(partials: list[dict]) -> dict:
    if not partials:
        raise ValueError("At least one profile receipt is required")
    merged = {
        "schemaVersion": partials[0]["schemaVersion"],
        "assetStatus": partials[0]["assetStatus"],
        "scope": partials[0]["scope"],
        "profiles": {},
        "figures": [],
        "boundaries": list(partials[0].get("boundaries", [])),
    }
    rows: dict[str, dict] = {}
    order: list[str] = []
    for partial in partials:
        for key in ("schemaVersion", "assetStatus", "scope"):
            if partial[key] != merged[key]:
                raise ValueError(f"Profile receipts disagree on {key}")
        merged["profiles"].update(partial["profiles"])
        for boundary in partial.get("boundaries", []):
            if boundary not in merged["boundaries"]:
                merged["boundaries"].append(boundary)
        for figure in partial["figures"]:
            figure_id = figure["id"]
            if figure_id not in rows:
                order.append(figure_id)
                rows[figure_id] = {
                    key: value
                    for key, value in figure.items()
                    if key != "renditions"
                }
                rows[figure_id]["renditions"] = {}
            else:
                for key, value in figure.items():
                    if key != "renditions" and rows[figure_id][key] != value:
                        raise ValueError(f"Profile receipts disagree on {figure_id}.{key}")
            for profile, rendition in figure["renditions"].items():
                if profile in rows[figure_id]["renditions"]:
                    raise ValueError(f"Duplicate {profile} rendition for {figure_id}")
                rows[figure_id]["renditions"][profile] = rendition
    merged["figures"] = [rows[figure_id] for figure_id in order]
    return merged


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--scene-source-root", type=Path, required=True)
    parser.add_argument("--profile", choices=tuple(DEFAULT_PROFILE_SIZES))
    parser.add_argument("--figure-id", action="append")
    args = parser.parse_args()
    scene_sources = {
        "figure-01": {
            "landscape": args.scene_source_root / "figure-01-auction-morning-landscape-source.png",
            "mobile": args.scene_source_root / "figure-01-auction-morning-mobile-source.png",
        },
        "figure-09": {
            "landscape": args.scene_source_root / "figure-09-evidence-desk-landscape-source.png",
            "mobile": args.scene_source_root / "figure-09-evidence-desk-mobile-source.png",
        },
    }
    if args.profile:
        receipt = render_review_set(
            args.output_root,
            scene_sources=scene_sources,
            profile_sizes={args.profile: DEFAULT_PROFILE_SIZES[args.profile]},
            figure_ids=args.figure_id,
        )
        receipt_path = args.output_root / f"visual-expansion-render-receipt-{args.profile}.json"
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        print(f"rendered {len(receipt['figures'])} {args.profile} review figures")
        print(receipt_path)
        return 0

    args.output_root.mkdir(parents=True, exist_ok=True)
    partial_paths = []
    for profile in DEFAULT_PROFILE_SIZES:
        command = [
                sys.executable,
                str(Path(__file__).resolve()),
                "--output-root",
                str(args.output_root),
                "--scene-source-root",
                str(args.scene_source_root),
                "--profile",
                profile,
            ]
        for figure_id in args.figure_id or ():
            command.extend(("--figure-id", figure_id))
        subprocess.run(command, check=True)
        partial_paths.append(
            args.output_root / f"visual-expansion-render-receipt-{profile}.json"
        )
    receipt = merge_profile_receipts(
        [json.loads(path.read_text(encoding="utf-8")) for path in partial_paths]
    )
    receipt_path = args.output_root / "visual-expansion-render-receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"rendered {len(receipt['figures'])} paired review figures")
    print(receipt_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
