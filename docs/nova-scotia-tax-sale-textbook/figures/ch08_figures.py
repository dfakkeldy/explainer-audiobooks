"""Chapter 8 figures (spec: design/figure-style.md; plan: design/chapter-plan.md, Chapter 8).

    .venv/bin/python figures/ch08_figures.py

Every label below is taken from the original figure (figure-19, -21, -24, -25), its alt text, or
the manuscript lines the chapter plan cites (md:945-1049); review/claims/ch08.md maps each one.
The Case B plates reuse the Chapter 7 plate base (figures/ch07_figures.py) so all five Case B
plates share one geometry. Case plates are schematic, fictional geometry with no provincial base map.
"""
from pathlib import Path

from svgkit import C, DASH, DOT, Canvas, width
from ch07_figures import (CW, CX, MH, MX, MY, STATE, card, case_b_base, dotted, label_bg,
                          parcel_b, plate_end, ring)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src/assets/figures"
COMPOSITE = "Composite — not a real property; not a survey."
HATCH = ('<defs><pattern id="hatch-zone-b" width="8" height="8" patternUnits="userSpaceOnUse" '
         'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="8" '
         f'stroke="{C.verified}" stroke-width="1" stroke-opacity="0.35"/></pattern></defs>')


def state_box(c, x, y, w, h, state, fill=C.white):
    col, sw, dash, _, glyph = STATE[state]
    c.box(x, y, w, h, fill=fill, stroke=col, sw=sw, dash=dash,
          tab=C.municipal if state == "municipal" else None)
    if state == "screening":
        dotted(c)
    return col, glyph


def rail3(c, cards):
    gap, ch = 10, (MH - 20) / 3
    for i, (head, body, st) in enumerate(cards):
        card(c, CX, MY + i * (ch + gap), CW, ch, st, head, body)


# --------------------------------------------------------------------------- figure-24
def title_encumbrance_possession():
    """REDRAW figure-24: three questions, not three synonyms."""
    W, H = 672, 176
    c = Canvas(W, H, "Three questions, not three synonyms",
               "Title, rights and burdens, and possession as three separate columns.")
    cols = [("Title", "Ownership interest", "What ownership interest is recorded?"),
            ("Rights and burdens", "Rights and burdens",
             "What easements, liens or continuing interests may matter?"),
            ("Possession", "People or property on site", "Who or what is actually on the land?")]
    bw, gap, top, bh = 192, 48, 8, 160
    for i, (head, sub, q) in enumerate(cols):
        x = 8 + i * (bw + gap)
        c.box(x, top, bw, bh, fill=C.white, stroke=C.accent, sw=1.5)
        c.rect(x, top, bw, 6, fill=C.accent)
        c.text(x + 14, top + 34, head, 13, 700, C.accent)
        y = top + 34
        if sub != head:
            c.text(x + 14, top + 52, sub, 11, 400, C.ink2)
            y = top + 52
        c.line(x + 14, y + 12, x + bw - 14, y + 12, C.rule, 0.75)
        c.text_block(x + 14, y + 34, bw - 28, q, 12)
        # dotted joiner (two dotted bars: related, but not an equals sign)
        if i < 2:
            jx = x + bw + 8
            for dy in (-5, 5):
                c.line(jx, top + bh / 2 + dy, jx + gap - 16, top + bh / 2 + dy, C.granite, 2.25,
                       dash="0.5 5", cap="round")
    c.save(OUT / "fig-08-title-encumbrance-possession.svg")


# --------------------------------------------------------------------------- deed effect (NEW)
def deed_effect():
    """NEW: what the tax deed changes for the fictional Foundry Street (md:953-957, 969, 975, 981)."""
    W, H = 672, 494
    c = Canvas(W, H, "What the deed changes for Foundry Street",
               "Register entries before the deed and the three outcome lanes after it.")
    c.text(8, 20, "Fictional Foundry Street · " + COMPOSITE, 12, 700, C.ink)
    # column 1: the older parcel register
    rx, ry, rw, rh = 8, 40, 176, 304
    c.box(rx, ry, rw, rh, fill=C.paper2, stroke=C.granite, sw=1.5)
    c.text(rx + 12, ry + 24, "Older parcel register", 13, 700, C.ink)
    c.text(rx + 12, ry + 40, "before the deed", 11, 400, C.ink2)
    for name, y in (("Mortgage", 118), ("Judgment", 188)):
        c.box(rx + 10, y - 22, rw - 20, 44, fill=C.white, stroke=C.municipal, sw=1.5,
              tab=C.municipal)
        c.text(rx + 24, y + 4, name, 12, 700)
    c.box(rx + 10, 236, rw - 20, 56, fill=C.white, stroke=C.municipal, sw=1.5, tab=C.municipal)
    c.text(rx + 24, 258, "Registered right-of-way", 12, 700)
    c.text(rx + 24, 278, "serving the house behind", 11, 400, C.ink2)
    # column 2: the deed
    dx, dw = 214, 112
    c.box(dx, ry, dw, rh, fill=C.accent, stroke=C.accent, sw=1.5)
    c.text(dx + dw / 2, ry + 28, "Tax deed", 18, 700, C.white, "middle")
    c.text(dx + dw / 2, ry + 46, "registered", 12, 400, C.white, "middle")
    yb = ry + 80
    for s_ in ["Vests the land", "in fee simple,", "free and", "discharged from", "all encumbrances"]:
        c.text(dx + dw / 2, yb, s_, 12, 700, C.white, "middle")
        yb += 16
    c.text_block(dx + 12, 282, dw - 24,
                 "Read with the statute, any court order, the deed and the property record.",
                 11, 400, C.white)
    # column 3: outcome lanes
    lx, lw = 356, 308
    lanes = [
        (40, 98, "unresolved", "Interests the statute discharges",
         "Counsel confirms which. Mortgage and judgment sit here, not drawn as erased."),
        (150, 98, "verified", "Easements and rights-of-way",
         "A benefit passes with the land; a burden continues as the Act specifies."),
        (260, 84, "unresolved", "If a court order exists",
         "Its exceptions, exclusions or partial interests apply."),
    ]
    for y, h, st, head, body in lanes:
        col, glyph = state_box(c, lx, y, lw, h, st)
        c.text(lx + 12, y + 22, head, 13, 700, C.ink)
        if glyph:
            c.glyph(glyph, lx + lw - 16, y + 18, col)
        c.text_block(lx + 12, y + 42, lw - 24, body, 12)
    # arrows: mortgage and judgment into the deed, then to the counsel-confirms lane
    c.arrow(rx + rw - 10, 118, dx, 118, C.ink, 1.5)
    c.arrow(rx + rw - 10, 188, dx, 172, C.ink, 1.5)
    c.arrow(dx + dw, 130, lx, 100, C.ink, 1.5)
    # the right-of-way may continue (md:981): one heavy line through the deed
    c.line(rx + rw - 10, 250, dx, 250, C.verified, 2.25)
    c.line(dx, 250, dx + dw, 250, C.white, 2.25, dash="2 3")
    c.text(dx + dw / 2, 240, "may continue", 11, 700, C.white, "middle")
    c.arrow(dx + dw, 250, lx, 222, C.verified, 2.25)
    # court order: a conditional branch
    c.arrow(dx + dw, 300, lx, 300, C.unresolved, 1.5, dash=DASH)
    # bottom: the money route, outside the land
    sy = 370
    c.line(8, sy - 10, 664, sy - 10, C.rule, 0.75)
    c.text(8, sy + 8, "Outside the title file", 11, 700, C.ink2)
    c.box(8, sy + 18, 656, 72, fill=C.white, stroke=C.granite, sw=1.5, dash=DASH)
    c.text(22, sy + 42, "Possible claim to surplus proceeds", 13, 700, C.ink)
    c.text_block(22, sy + 62, 600,
                 "A former interest holder's separate statutory route to money: not automatically a "
                 "continuing burden on the land (Chapter 12).", 12)
    c.text(8, sy + 114, "Each result comes from its governing source.", 12, 700, C.accent)
    c.save(OUT / "fig-08-deed-effect.svg")


# --------------------------------------------------------------------------- figure-19
def case_b_identity():
    """REDRAW figure-19 (Case B map 2), moved from Chapter 7."""
    W, H = 672, 340
    c = Canvas(W, H, "Case B: land and structures may diverge",
               "Parcel B outline with a building footprint and a separate manufactured-home question.")
    case_b_base(c)
    parcel_b(c)
    c.text(218, 214, "building footprint", 12, 400, C.ink, "middle")
    # fictional identifiers pointing to the parcel (masked)
    bx, by, bw, bh = 22, 40, 100, 58
    c.box(bx, by, bw, bh, fill=C.white, stroke=C.verified, sw=1.5)
    for i, s in enumerate(("Lien ••••", "AAN ••••", "PID ••••")):
        c.text(bx + 10, by + 17 + i * 16, s, 12, 700, C.ink)
    c.line(bx + bw, by + bh - 6, 154, 140, C.verified, 1.25)
    # a separate manufactured-home question, tied to different records
    ring(c, 218, 175, 27, "unresolved")
    c.glyph("question", 246, 150, C.unresolved)
    hx, hy, hw, hh = 290, 44, 132, 58
    c.box(hx, hy, hw, hh, fill=C.white, stroke=C.unresolved, sw=1.5, dash=DASH)
    c.text(hx + 10, hy + 18, "Home record ••••", 12, 700, C.ink)
    c.text_block(hx + 10, hy + 34, hw - 20, "different fictional records", 11, 400, C.ink2)
    c.line(hx + 20, hy + hh, 246, 150, C.unresolved, 1.25, dash=DASH)
    plate_end(c)
    rail3(c, [("Lien / AAN / PID", "Fictional Case B identifiers point to one research target.",
               "verified"),
              ("Boundary", "The graphical outline is not a survey or title opinion.", "screening"),
              ("Manufactured home?", "A separate question tied to different fictional records.",
               "unresolved")])
    c.save(OUT / "fig-08-case-b-identity.svg")


# --------------------------------------------------------------------------- figure-21
def case_b_planning():
    """REDRAW figure-21 (Case B map 4), moved within Chapter 8 to the occupied-building section."""
    W, H = 672, 340
    c = Canvas(W, H, "Case B: occupation proves neither use nor services",
               "Parcel B with zones, water and sewer lines, a use-confirmation icon and an "
               "occupancy warning.")
    c.raw(HATCH)
    case_b_base(c)
    # zones (inside the map clip opened by case_b_base)
    c.path(f"M{MX},{MY} L120,{MY} L120,{MY + MH} L{MX},{MY + MH} Z", fill="url(#hatch-zone-b)",
           stroke=C.verified, sw=1.5)
    c.path(f"M318,{MY} L{MX + 424},{MY} L{MX + 424},{MY + MH} L318,{MY + MH} Z", fill="none",
           stroke=C.unresolved, sw=1.5, dash=DASH)
    # water and sewer lines along the east-west street
    import math
    x1, y1, x2, y2 = 8, 290, 444, 150
    L = math.hypot(x2 - x1, y2 - y1)
    nx, ny = (y1 - y2) / L, (x2 - x1) / L          # unit normal (points down-right)
    for off, col in ((-12, C.accent), (13, C.ink2)):
        c.line(x1 + nx * off, y1 + ny * off, x2 + nx * off, y2 + ny * off, col, 2)
    for t in (0.1, 0.62, 0.86):
        c.circle(x1 + (x2 - x1) * t + nx * 13, y1 + (y2 - y1) * t + ny * 13, 3.5,
                 fill=C.white, stroke=C.ink2, sw=1.5)
    parcel_b(c, label=False)
    plate_end(c)
    c.rect(MX + 4, MY + 6, 52, 20, fill=C.white)
    c.text(MX + 10, MY + 21, "Zone A", 12, 700, C.verified)
    c.rect(322, MY + 6, 54, 20, fill=C.white)
    c.text(328, MY + 21, "Zone ?", 12, 700, C.unresolved)
    label_bg(c, 150, 254, "Parcel B", 13, 700, C.accent)
    label_bg(c, 18, 262, "water line", 11, 700, C.accent)
    label_bg(c, 150, 306, "sewer line", 11, 700, C.ink2)
    # use-confirmation icon
    c.glyph("question", 270, 140, C.verified)
    label_bg(c, 230, 112, "use: confirm in writing", 11, 700, C.verified, "middle")
    # separate occupancy warning
    ox, oy, ow, oh = 300, 196, 120, 72
    c.box(ox, oy, ow, oh, fill=C.white, stroke=C.unresolved, sw=1.5, dash=DASH)
    c.text(ox + 10, oy + 18, "Occupancy", 12, 700, C.unresolved)
    c.text_block(ox + 10, oy + 34, ow - 20, "Existing occupation does not prove vacant possession.",
                 11, 400, C.ink)
    c.line(ox, oy + 20, 252, 190, C.unresolved, 1.25, dash=DASH)
    rail3(c, [("Zone", "Confirm the current rule and intended use in writing.", "verified"),
              ("Frontage", "Mapped contact is not a survey measurement.", "screening"),
              ("Services", "Well, septic, water and sewer require separate evidence.",
               "unresolved")])
    c.save(OUT / "fig-08-case-b-planning.svg")


# --------------------------------------------------------------------------- manufactured home (NEW)
def manufactured_home_records():
    """NEW: four separate records for the fictional Harbour Park listing (md:1017-1021, 1031)."""
    W, H = 672, 482
    c = Canvas(W, H, "One listing, four separate records",
               "The home, the land, the space and security interests are separate questions.")
    bw, bh = 272, 118
    boxes = [
        (8, 8, "The home", "Mobile-home tax-sale regulations and prescribed forms",
         "The notice uses a mobile home identifier."),
        (392, 8, "The land under it", "Land records",
         "The map selects the underlying land PID."),
        (8, 250, "The right to keep the home on the space",
         "Land-lease community: the Residential Tenancies framework",
         "Rules about the space, the tenancy and the sale of a home that remains there."),
        (392, 250, "Security interests in the home", "Personal Property Registry",
         "Not the land registry. A clean-looking PID search does not answer it."),
    ]
    for x, y, head, system, body in boxes:
        h_ = 112 if y < 100 else 124
        c.box(x, y, bw, h_, fill=C.white, stroke=C.accent, sw=1.5)
        c.rect(x, y, bw, 6, fill=C.accent)
        yy = c.text_block(x + 12, y + 28, bw - 24, head, 13, 700, C.accent)
        yy = c.text_block(x + 12, yy, bw - 24, system, 12, 700, C.ink)
        c.text_block(x + 12, yy + 2, bw - 24, body, 12, 400, C.ink2)
    # centre: the listing (no lines join it to the four records)
    cx, cy, cw, ch = 214, 130, 244, 110
    c.box(cx, cy, cw, ch, fill=C.accent_tint, stroke=C.unresolved, sw=1.5, dash=DASH)
    c.glyph("question", cx + cw - 16, cy + 16, C.unresolved)
    c.text(cx + cw / 2, cy + 24, "Fictional Harbour Park listing", 13, 700, C.ink, "middle")
    c.text(cx + cw / 2, cy + 40, "Composite — not a real property", 11, 400, C.ink2, "middle")
    c.text(cx + cw / 2, cy + 66, "Asset identity unresolved", 13, 700, C.unresolved, "middle")
    c.text(cx + cw / 2, cy + 84, "No PID-only conclusion", 12, 700, C.ink, "middle")
    c.text_block(cx + 14, cy + 104, cw - 28, "Roadside view: a home on a serviced pad.",
                 11, 400, C.ink2)
    # bottom strip: what none of the visible facts establishes
    sy = 386
    c.rect(8, sy, 656, 88, fill=C.paper2)
    c.text(20, sy + 22, "None of the notice, the map or the roadside view establishes that:", 12,
           700, C.ink)
    items = ["the home and land share an owner", "the home is affixed to the land",
             "the pad agreement transfers", "a personal-property lien is absent",
             "the home can remain after a sale"]
    xs, ys = (20, 236, 452), (sy + 46, sy + 70)
    for i, s in enumerate(items):
        x, y = xs[i % 3], ys[i // 3]
        c.text(x, y, "–", 12, 700, C.unresolved)
        c.text(x + 12, y, s, 12)
    c.save(OUT / "fig-08-manufactured-home-records.svg")


# --------------------------------------------------------------------------- figure-25
def occupied_property_handoff():
    """REDRAW figure-25: observation stops before self-help."""
    W, H = 672, 262
    c = Canvas(W, H, "Observation stops before self-help",
               "Lawful exterior observation, public records, then lawyer or tenancy advice; a stop "
               "card for self-help.")
    bw, gap, top, bh = 200, 28, 8, 118
    steps = [("screening", "Lawful exterior observation",
              "Remain off the parcel and avoid confrontation."),
             ("verified", "Public records", "Preserve only bounded, source-backed facts."),
             ("unresolved", "Lawyer / tenancy advice",
              "Establish the lawful route before contact or entry.")]
    for i, (st, head, body) in enumerate(steps):
        x = 8 + i * (bw + gap)
        col, glyph = state_box(c, x, top, bw, bh, st)
        c.text(x + 12, top + 22, f"{i + 1}", 13, 700, C.ink2)
        yy = c.text_block(x + 30, top + 22, bw - 58, head, 13, 700,
                          STATE[st][3] if st != "screening" else C.ink)
        if glyph:
            c.glyph(glyph, x + bw - 16, top + 18, col)
        c.text_block(x + 12, yy + 10, bw - 24, body, 12)
        if i < 2:
            c.arrow(x + bw + 2, top + bh / 2, x + bw + gap - 2, top + bh / 2, C.ink, 1.5)
    # stop card
    sy = top + bh + 24
    c.box(8, sy, 656, 96, fill=C.caution_tint, stroke=C.nogo, sw=3)
    c.glyph("bar", 30, sy + 30, C.nogo)
    c.text(46, sy + 35, "Stop", 18, 700, C.caution)
    c.text_block(110, sy + 34, 530,
                 "No lock change, entry, rent demand or goods handling without authority.", 13, 700)
    c.text_block(110, sy + 60, 530,
                 "Occupancy questions move from observation to legal advice, not to self-help.",
                 12, 400, C.ink)
    c.save(OUT / "fig-08-occupied-property-handoff.svg")


if __name__ == "__main__":
    title_encumbrance_possession()
    deed_effect()
    case_b_identity()
    case_b_planning()
    manufactured_home_records()
    occupied_property_handoff()
