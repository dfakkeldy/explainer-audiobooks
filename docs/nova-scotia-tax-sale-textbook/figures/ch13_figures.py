"""Chapter 13 figures (spec: design/figure-style.md; plan: design/chapter-plan.md, Chapter 13).

    .venv/bin/python figures/ch13_figures.py

The five Case C plates redraw figure-33 to figure-37 on one fictional geometry (layout as the
Case A plates in case_a_plate.py: map panel left, rail of cards right). Card headings and texts are
the original figures' own words (sentence case); the map marks are the ones each original alt text
names (flag F-13b). Parcel C sits *beside* a mapped road (md:1533: "the graphical outline beside a
mapped road"), not crossed by two roads as in the original plates.
fig-13-known-unresolved-professional redraws figure-38 as a worksheet; fig-13-three-endings is new
and uses only md:1505-1579. review/claims/ch13.md maps every label.
"""
from pathlib import Path

from svgkit import C, DASH, DOT, Canvas, wrap
from case_a_plate import CARD, LAND, MH, MW, MX, MY, RW, RX, SCREEN_TINT, WATER, poly, polyline

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src/assets/figures"
H = 340

WATER_X = 368


def road_y(x):
    """Centre line of the mapped public road (gently rising to the east)."""
    return 262 - 0.08 * (x - MX)


EDGE = 3.5                                   # half road width + gap: parcel's south edge
P_SOUTH = [(150, road_y(150) - EDGE), (300, road_y(300) - EDGE)]
PARCEL = [P_SOUTH[0], P_SOUTH[1], (318, 150), (262, 104), (168, 120)]
PCX, PCY = 236, 180                           # label point


class CPlate:
    def __init__(self, c, stamp=True, communities=True, nslabel=(94, 64)):
        self.c = c
        c.raw('<defs><clipPath id="mapclip">'
              f'<rect x="{MX}" y="{MY}" width="{MW}" height="{MH}"/></clipPath>'
              '<pattern id="hatch-zone" width="8" height="8" patternUnits="userSpaceOnUse" '
              'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="8" '
              f'stroke="{C.verified}" stroke-width="1" stroke-opacity="0.35"/></pattern></defs>')
        c.raw('<g clip-path="url(#mapclip)">')
        c.rect(MX, MY, MW, MH, fill=LAND)
        shore = [(WATER_X, MY), (WATER_X + 12, 76), (WATER_X - 2, 128), (WATER_X + 10, 184),
                 (WATER_X - 4, 240), (WATER_X + 6, MY + MH)]
        c.path(poly(shore + [(MX + MW, MY + MH), (MX + MW, MY)]), fill=WATER, stroke="none")
        c.path(polyline(shore), stroke=C.accent_mid, sw=1)
        # second public road (north-south, west side) and main mapped public road
        c.path(polyline([(72, MY), (78, 170), (86, MY + MH)]), stroke=C.ink2, sw=4.5)
        x1 = WATER_X - 1
        c.line(MX, road_y(MX), x1, road_y(x1), C.ink2, 5)
        if communities:
            for (cx, cy) in [(26, 66), (42, 76), (22, 88), (36, 96)]:
                c.rect(cx, cy, 8, 8, fill=C.granite)
        c.raw("</g>")
        c.rect(MX, MY, MW, MH, stroke=C.rule, sw=1)
        lx = 98
        c.text(lx + 4, road_y(lx) + 18, "public road", 11, 400, C.ink2)
        c.text(*nslabel, "public road", 11, 400, C.ink2)
        c.text(394, 222, "water", 11, 400, C.accent)
        nx, ny = 404, 48
        c.path(f"M{nx},{ny - 12} L{nx + 6},{ny + 6} L{nx},{ny + 2} L{nx - 6},{ny + 6} Z",
               fill=C.ink, stroke=C.ink, sw=1)
        c.text(nx, ny + 20, "N", 11, 700, C.ink, anchor="middle")
        c.text(MX + MW - 6, MY + MH - 8, "Not to scale", 11, 400, C.ink2, anchor="end")
        if stamp:
            c.text(MX, 19, "Composite — not a real property; not a survey.", 12, 700, C.ink)

    def parcel(self, stroke=C.screening, sw=2.25, dash=None, fill=SCREEN_TINT, label=True,
               lx=PCX, ly=PCY):
        self.c.path(poly(PARCEL), fill=fill, stroke=stroke, sw=sw, dash=dash)
        if label:
            self.c.text(lx, ly, "Parcel C", 12, 700, C.ink, anchor="middle")

    def rail_cards(self, cards, top=MY, bottom=MY + MH, gap=10):
        c = self.c
        n = len(cards)
        h = (bottom - top - gap * (n - 1)) / n
        for i, (head, body, style) in enumerate(cards):
            y = top + i * (h + gap)
            col, sw, dash, hcol, glyph = CARD[style]
            c.box(RX, y, RW, h, fill=C.white, stroke=col, sw=sw, dash=dash)
            c.text(RX + 12, y + 22, head, 13, 700, hcol)
            if glyph:
                c.glyph(glyph, RX + RW - 18, y + 18, col)
            c.text_block(RX + 12, y + 42, RW - 24, body, 12, 400, C.ink)
            need = 42 + len(wrap(body, 12, RW - 24)) * 15.6
            assert need < h, (head, need, h)


def label_bg(c, x, y, s, size=11, weight=400, color=C.ink, anchor="start", pad=3):
    from svgkit import width
    w = width(s, size, weight)
    x0 = {"start": x, "middle": x - w / 2, "end": x - w}[anchor]
    c.rect(x0 - pad, y - size * 0.9, w + 2 * pad, size * 1.25, fill=C.white)
    c.text(x, y, s, size, weight, color, anchor)


# ---------------------------------------------------------------------------- plates

def orientation():
    c = Canvas(672, H, title="Case C is coherent, not recommended")
    p = CPlate(c)
    p.parcel()
    label_bg(c, 22, 116, "community services", 11, 400, C.ink2)
    # evidence-file label (process-complete green, check glyph) and "no bid score"
    bx, by, bw, bh = 184, 46, 150, 40
    c.box(bx, by, bw, bh, fill=C.white, stroke=C.complete, sw=1.5)
    c.glyph("check", bx + 16, by + 15, C.complete)
    c.text(bx + 30, by + 19, "Evidence file", 12, 700, C.complete)
    c.text(bx + 30, by + 33, "no bid score", 11, 400, C.ink2)
    c.line(bx + 60, by + bh, PCX - 4, 124, C.complete, 1.25)
    p.rail_cards([
        ("Place", "Locate fictional Case C among roads, communities and water.", "plain"),
        ("Limit", "Orientation does not prove access, title, condition or services.", "limit"),
    ])
    c.save(OUT / "fig-13-case-c-orientation.svg")


def identity():
    c = Canvas(672, H, title="Case C: consistent records reduce one unknown")
    p = CPlate(c, communities=False)
    p.parcel(stroke=C.verified, sw=3, lx=PCX + 20, ly=PCY + 20)
    # three matching identifier cards, joined to the parcel
    bx, by, bw, bh = 28, 92, 104, 24
    label_bg(c, bx, by - 8, "fictional identifiers", 11, 400, C.ink2)
    for i, s in enumerate(("Lien ••••", "AAN ••••", "PID ••••")):
        y = by + i * (bh + 6)
        c.box(bx, y, bw, bh, fill=C.white, stroke=C.verified, sw=1.5)
        c.text(bx + 10, y + 16, s, 12, 700, C.ink)
        c.glyph("check", bx + bw - 14, y + 12, C.verified)
        c.line(bx + bw, y + bh / 2, bx + bw + 14, y + bh / 2, C.verified, 1.25)
    c.line(bx + bw + 14, by + bh / 2, bx + bw + 14, by + 2 * (bh + 6) + bh / 2, C.verified, 1.25)
    c.arrow(bx + bw + 14, by + (bh + 6) + bh / 2, 190, by + (bh + 6) + bh / 2 + 30, C.verified,
            1.5)
    label_bg(c, bx, by + 3 * (bh + 6) + 12, "all three match", 11, 400, C.ink2)
    # prominent stamp
    sx, sy = 230, 40
    c.rect(sx, sy, 128, 30, fill=C.white, stroke=C.granite, sw=2.25)
    c.text(sx + 64, sy + 21, "Not a survey", 16, 700, C.granite, anchor="middle")
    p.rail_cards([
        ("Lien / AAN / PID", "Fictional Case C identifiers point to one research target.",
         "verified"),
        ("Boundary", "The graphical outline is not a survey or title opinion.", "screening"),
    ])
    c.save(OUT / "fig-13-case-c-identity.svg")


def access():
    c = Canvas(672, H, title="Case C: strong clues focus the legal question")
    p = CPlate(c, communities=False)
    # gentle contours: widely spaced, shallow curves across the north of the map
    import math
    for k, base in enumerate((74, 100, 128)):
        pts = [(x, base + 7 * math.sin((x - 100) / 70 + k * 0.6)) for x in range(96, 360, 6)]
        c.path(polyline(pts), stroke=C.granite, sw=0.9)
    label_bg(c, 250, 58, "gentle contours", 11, 400, C.ink2)
    p.parcel(lx=PCX + 10, ly=PCY - 34)
    # frontage where the parcel touches the mapped road
    (fx1, fy1), (fx2, fy2) = P_SOUTH
    c.line(fx1, fy1 - 3, fx2, fy2 - 3, C.unresolved, 2.25, dash=DASH)
    # visible track (screening, dotted) from the road into the parcel
    tr = [(196, road_y(196)), (204, 210), (214, 186)]
    c.path(polyline(tr), stroke=C.screening, sw=2.25, dash=DOT, extra=' stroke-linecap="round"')
    label_bg(c, 186, 204, "visible track?", 11, 700, C.ink, anchor="end")
    # lawyer-confirmation icon at the frontage
    gx, gy = 262, road_y(262) - 22
    c.glyph("question", gx, gy, C.unresolved)
    label_bg(c, gx + 11, gy - 3, "lawyer confirms", 11, 700, C.unresolved)
    label_bg(c, gx + 11, gy + 10, "legal access", 11, 400, C.unresolved)
    label_bg(c, 300, road_y(300) + 20, "mapped public road (frontage)", 11, 400, C.ink2,
             anchor="middle")
    p.rail_cards([
        ("Visible approach", "A road or track on a map is a screening clue.", "screening"),
        ("Legal access", "Registry and legal review must answer the right-of-way question.",
         "unresolved"),
        ("Terrain", "Contours and drainage change site questions, not legal rights.", "verified"),
    ])
    c.save(OUT / "fig-13-case-c-access.svg")


def planning():
    c = Canvas(672, H, title="Case C: name every confirmation")
    p = CPlate(c, communities=False, nslabel=(90, 150))
    c.raw('<g clip-path="url(#mapclip)">')
    za = [(MX, MY), (60, MY), (60, MY + MH), (MX, MY + MH)]
    c.path(poly(za), fill="url(#hatch-zone)", stroke=C.verified, sw=1.5)
    zq = [(352, MY), (MX + MW, MY), (MX + MW, MY + MH), (352, MY + MH)]
    c.path(poly(zq), fill="none", stroke=C.unresolved, sw=1.5, dash=DASH)
    c.raw("</g>")
    c.rect(MX + 4, MY + 6, 48, 20, fill=C.white)
    c.text(MX + 8, MY + 21, "Zone A", 12, 700, C.verified)
    c.rect(358, MY + 248, 54, 20, fill=C.white)
    c.text(364, MY + 263, "Zone ?", 12, 700, C.unresolved)
    p.parcel(lx=PCX - 20, ly=PCY - 10)
    # frontage dimension along the south edge, just inside the parcel
    (x1, y1), (x2, y2) = P_SOUTH
    y1, y2 = y1 - 12, y2 - 12
    c.line(x1 + 4, y1, x2 - 4, y2, C.screening, 1.5, dash=DOT, cap="round")
    for x, y in ((x1 + 4, y1), (x2 - 4, y2)):
        c.line(x, y - 6, x, y + 6, C.screening, 1.5)
    label_bg(c, (x1 + x2) / 2, (y1 + y2) / 2 + 4, "frontage?", 11, 700, C.ink, anchor="middle")
    # well and septic question icons
    for x, y, lab in ((236, 196, "well"), (282, 182, "septic")):
        c.glyph("question", x, y, C.unresolved)
        c.text(x + 10, y + 4, lab, 11, 400, C.ink)
    # three written questions for municipal planning staff (md:1557)
    bx, by, bw, bh = 72, 40, 224, 72
    c.box(bx, by, bw, bh, fill=C.white, stroke=C.accent, sw=1.5)
    c.text(bx + 10, by + 17, "Written questions for planning staff", 12, 700, C.accent)
    for i, q in enumerate(("1  Exact frontage?", "2  Lot status?",
                           "3  Intended use and its approval?")):
        c.text(bx + 10, by + 34 + i * 14, q, 11, 400, C.ink)
    c.arrow(bx + 150, by + bh, 230, 118, C.accent, 1.5)
    p.rail_cards([
        ("Zone", "Confirm the current rule and intended use in writing.", "verified"),
        ("Frontage", "Mapped contact is not a survey measurement.", "screening"),
        ("Services", "Well, septic, water and sewer require separate evidence.", "unresolved"),
    ])
    c.save(OUT / "fig-13-case-c-planning.svg")


def screening():
    c = Canvas(672, H, title="Case C: no mapped overlap is bounded")
    p = CPlate(c, communities=False, nslabel=(90, 222))
    p.parcel(lx=PCX, ly=PCY - 20)
    # mapped points from searched layers, all outside the parcel
    for (x, y, col, dash) in ((116, 128, C.verified, None), (300, 78, C.screening, DOT),
                              (340, 214, C.screening, DOT)):
        c.raw(f'<circle cx="{x}" cy="{y}" r="11" fill="none" stroke="{col}" stroke-width="2"'
              + (f' stroke-dasharray="{dash}" stroke-linecap="round"' if dash else "") + "/>")
    label_bg(c, 20, 168, "mapped points", 11, 400, C.ink2)
    label_bg(c, 20, 182, "outside the parcel", 11, 400, C.ink2)
    label_bg(c, PCX, PCY - 4, "no highlighted overlap", 11, 400, C.ink, anchor="middle")
    # searched layers list with coverage limit
    bx, by, bw, bh = 20, 40, 168, 64
    c.box(bx, by, bw, bh, fill=C.white, stroke=C.verified, sw=1.5)
    c.text(bx + 10, by + 17, "Layers searched", 12, 700, C.verified)
    c.text_block(bx + 10, by + 33, bw - 20, "environmental, well, sewage, coastal, mine", 11, 400,
                 C.ink)
    # inspection handoff
    hx, hy, hw, hh = 160, 268, 196, 44
    c.box(hx, hy, hw, hh, fill=C.white, stroke=C.unresolved, sw=1.5, dash=DASH)
    c.glyph("question", hx + 16, hy + 16, C.unresolved)
    c.text(hx + 30, hy + 20, "Inspection handoff", 12, 700, C.unresolved)
    c.text(hx + 30, hy + 35, "site professionals", 11, 400, C.ink)
    c.arrow(250, 236, 252, hy, C.unresolved, 1.5)
    p.rail_cards([
        ("Searched layers", "Coverage, date and category limits stay visible.", "verified"),
        ("Screening clue", "A mapped point or overlap starts another records question.",
         "screening"),
        ("No result", "No mapped overlap is not a clean bill of health.", "limit"),
    ])
    c.save(OUT / "fig-13-case-c-screening.svg")


# ---------------------------------------------------------------------------- worksheet

def worksheet():
    W, Hh = 672, 400
    c = Canvas(W, Hh, title="End with a file that knows its limits")
    cols = [
        ("Known", "Dated, cited facts and bounded observations.", C.verified, None, "check"),
        ("Unresolved", "Questions the current evidence cannot answer.", C.unresolved, DASH,
         "question"),
        ("Professional", "The person or authority qualified to answer next.", C.accent, None,
         "arrow"),
    ]
    gap, x0, top, ch = 12, 8, 8, 268
    cw = (W - 2 * x0 - 2 * gap) / 3
    for i, (head, body, col, dash, g) in enumerate(cols):
        x = x0 + i * (cw + gap)
        c.box(x, top, cw, ch, fill=C.white, stroke=col, sw=1.5, dash=dash)
        c.text(x + 14, top + 24, head, 13, 700, col)
        if g == "arrow":
            c.arrow(x + cw - 30, top + 19, x + cw - 10, top + 19, col, 2, gap=0)
        else:
            c.glyph(g, x + cw - 20, top + 19, col)
        yy = c.text_block(x + 14, top + 44, cw - 28, body, 12, 400, C.ink)
        for k in range(7):
            ly = yy + 18 + k * 26
            if ly < top + ch - 10:
                c.line(x + 14, ly, x + cw - 14, ly, C.rule, 0.75)
    dy, dh = top + ch + 14, 96
    c.box(x0, dy, W - 2 * x0, dh, fill=C.white, stroke=C.ink, sw=2.25)
    c.text(x0 + 14, dy + 24, "Decision", 13, 700, C.ink)
    c.text(x0 + 14, dy + 42, "The bidder owns the choice and its consequences.", 12, 400, C.ink)
    for k in range(2):
        ly = dy + 64 + k * 22
        c.line(x0 + 14, ly, W - x0 - 14, ly, C.rule, 0.75)
    c.save(OUT / "fig-13-known-unresolved-professional.svg")


# ---------------------------------------------------------------------------- three endings

ROWS = ["Verified fact", "Unresolved question", "Next authority", "Consequence"]
FILES = [
    ("Alder Crossing", [
        "One account with two PIDs; the civic point lies inside one parcel polygon.",
        "Which interest is sold, and how the PIDs, account, descriptions and building relate.",
        "The municipality's current notice or confirmation; counsel's land-record review.",
    ], ("Stop", "Unresolved parcel-identity conflict.", "nogo")),
    ("Union Workshop", [
        "Dated notice, exact PID and specific public-source returns.",
        "Possession, former use, condition, insurance and tax treatment.",
        "Counsel; environmental and building professionals; municipality; insurer; tax adviser.",
    ], ("Stop", "Not priceable in time; the bidder owns the decision to stop.", "nogo")),
    ("Meadow Line", [
        "Summary and detail agree; AAN and PID consistent; mapped road; zoning response.",
        "Access, frontage, lot, use and services.",
        "Lawyer; municipality; site professionals; surveyor if needed.",
    ], ("Decision point", "It belongs to the bidder; not a recommendation.", "complete")),
]


def three_endings():
    W = 672
    x0, lw, gap = 8, 112, 8
    cw = (W - 2 * x0 - lw - 3 * gap) / 3
    pad = 10
    tw = cw - 2 * pad
    # row heights from the longest cell
    heights = []
    for r in range(3):
        n = max(len(wrap(f[1][r], 12, tw)) for f in FILES)
        heights.append(max(n * 15.6 + 2 * pad, len(wrap(ROWS[r], 12, lw - 12, 700)) * 15.6 + 16))
    endh = max(len(wrap(f[2][1], 12, tw - 22)) for f in FILES) * 15.6 + 44
    heights.append(endh)
    head_h = 34
    Hh = int(8 + head_h + sum(heights) + gap * 4 + 8)
    c = Canvas(W, Hh, title="Three files, three endings")
    y = 8
    for i, (name, _, _) in enumerate(FILES):
        x = x0 + lw + gap + i * (cw + gap)
        c.rect(x, y, cw, head_h, fill=C.accent, rx=3)
        c.text(x + cw / 2, y + 22, name, 13, 700, C.white, anchor="middle")
    c.text(x0, y + 15, "Fictional files", 11, 400, C.ink2)
    c.text(x0, y + 29, "(composite cases)", 11, 400, C.ink2)
    y += head_h + gap
    for r in range(4):
        h = heights[r]
        c.text_block(x0, y + 18, lw - 12, ROWS[r], 12, 700, C.ink)
        for i, (name, cells, end) in enumerate(FILES):
            x = x0 + lw + gap + i * (cw + gap)
            if r < 3:
                style = {0: (C.verified, None), 1: (C.unresolved, DASH), 2: (C.accent, None)}[r]
                c.box(x, y, cw, h, fill=C.white, stroke=style[0], sw=1.5, dash=style[1])
                if r == 1:
                    c.glyph("question", x + cw - 12, y + 12, C.unresolved)
                    c.text_block(x + pad, y + pad + 12, tw - 10, cells[r], 12, 400, C.ink)
                else:
                    c.text_block(x + pad, y + pad + 12, tw, cells[r], 12, 400, C.ink)
            else:
                head, body, st = end
                if st == "nogo":
                    c.box(x, y, cw, h, fill=C.caution_tint, stroke=C.nogo, sw=3)
                    c.glyph("bar", x + pad + 8, y + 20, C.nogo)
                    hc = C.nogo
                else:
                    c.box(x, y, cw, h, fill=C.white, stroke=C.complete, sw=2.25)
                    c.glyph("check", x + pad + 7, y + 20, C.complete)
                    hc = C.complete
                c.text(x + pad + 22, y + 25, head, 13, 700, hc)
                c.text_block(x + pad, y + 46, tw, body, 12, 400, C.ink)
        y += h + gap
    c.save(OUT / "fig-13-three-endings.svg")


if __name__ == "__main__":
    orientation()
    identity()
    access()
    planning()
    screening()
    worksheet()
    three_endings()
