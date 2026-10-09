"""Chapter 7 figures (spec: design/figure-style.md; plan: design/chapter-plan.md, Chapter 7).

    .venv/bin/python figures/ch07_figures.py

Every label below is taken from the original figure (figure-17, -18, -20, -22, -23), its alt text
or research/visuals.md entry, or the manuscript lines the chapter plan cites (md:807-941, md:593);
review/claims/ch07.md maps each one. The case plates are schematic, fictional geometry with no
provincial base map.
"""
import math
from pathlib import Path

from svgkit import C, DASH, DOT, Canvas, wrap

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src/assets/figures"

WATER = C.accent_tint
COMPOSITE = "Composite — not a real property; not a survey."


def dotted(c):
    """Round caps make the last-drawn dotted line read as dots."""
    c.items[-1] = c.items[-1].replace("/>", ' stroke-linecap="round"/>')


# evidence-state card styles: (stroke, width, dash, heading colour, glyph)
STATE = {
    "verified": (C.verified, 1.5, None, C.verified, None),
    "screening": (C.screening, 1.75, DOT, C.ink, None),
    "unresolved": (C.unresolved, 1.5, DASH, C.unresolved, "question"),
    "neutral": (C.granite, 1.5, None, C.ink, None),
    "accent": (C.accent, 1.5, None, C.accent, None),
    "municipal": (C.municipal, 1.5, None, C.municipal, None),
    "nogo": (C.nogo, 3, None, C.nogo, "bar"),
}


def card(c, x, y, w, h, state, head, body, symbol=None, size=12):
    col, sw, dash, hcol, glyph = STATE[state]
    c.box(x, y, w, h, fill=C.white, stroke=col, sw=sw, dash=dash,
          tab=C.municipal if state == "municipal" else None)
    if state == "screening":
        dotted(c)
    tx = x + (18 if state == "municipal" else 12)
    if symbol:
        symbol(x + 20, y + 20)
        tx = x + 36
    c.text(tx, y + 25, head, 13, 700, hcol)
    if glyph:
        c.glyph(glyph, x + w - 16, y + 20, col)
    c.text_block(x + 12, y + 46, w - 24, body, size)


def ring(c, x, y, r, state):
    col, sw, dash, _, _ = STATE[state]
    c.circle(x, y, r, fill="none", stroke=col, sw=2.25 if state != "screening" else 2.5)
    if dash:
        c.items[-1] = c.items[-1].replace("/>", f' stroke-dasharray="{dash}"/>')
        if state == "screening":
            dotted(c)


def road(c, pts, w=9):
    d = "M" + " L".join(f"{x},{y}" for x, y in pts)
    c.path(d, stroke=C.granite, sw=w + 2)
    c.path(d, stroke=C.white, sw=w)


def map_frame(c, x, y, w, h):
    c.rect(x, y, w, h, fill=C.paper2, stroke=C.rule, sw=0.75)


def stamp(c, x, y):
    c.rect(x - 6, y - 13, 6 + 268 + 6, 19, fill=C.white, stroke=C.rule, sw=0.75)
    c.text(x, y, COMPOSITE, 11, 400, C.granite)


def water(c, d):
    c.path(d, fill=WATER, stroke=C.accent_mid, sw=1.5)


def label_bg(c, x, y, s, size=12, weight=700, color=C.ink, anchor="start"):
    from svgkit import width
    w = width(s, size, weight)
    x0 = {"start": x, "middle": x - w / 2, "end": x - w}[anchor]
    c.rect(x0 - 3, y - size * 0.85, w + 6, size * 1.15, fill=C.white, rx=2)
    c.text(x, y, s, size, weight, color, anchor)


# --------------------------------------------------------------------------- plates
MX, MY, MW, MH = 8, 30, 424, 300      # map area of every case plate (as figures/case_a_plate.py)
CX, CW = 448, 216                     # card column


def plate_base(c, coast):
    map_frame(c, MX, MY, MW, MH)
    c.raw(f'<clipPath id="mapclip"><rect x="{MX}" y="{MY}" width="{MW}" height="{MH}"/></clipPath>'
          '<g clip-path="url(#mapclip)">')
    water(c, coast)


def plate_end(c):
    c.raw("</g>")
    c.rect(MX, MY, MW, MH, stroke=C.rule, sw=0.75)
    label_bg(c, MX + MW - 6, MY + MH - 8, "Not to scale", 11, 400, C.ink2, "end")
    c.text(MX, 19, COMPOSITE, 12, 700, C.ink)


def case_a_screening():
    """REDRAW figure-17 (Case A map 5), on the shared Case A base (figures/case_a_plate.py)."""
    import case_a_plate as A
    W, H = 672, 340
    c = Canvas(W, H, "Case A: screening starts harder questions",
               "Parcel A with wet-ground, coastal, geology and mine-opening screening layers.")
    p = A.Plate(c)
    p.parcel()
    # coastal screening band along the shore (dotted: screening)
    c.path(A.polyline([(A.WATER_X - 14, A.MY + 40), (A.WATER_X - 22, 130), (A.WATER_X - 12, 190),
                       (A.WATER_X - 6, 250)]), stroke=C.screening, sw=2.5, dash=DOT)
    dotted(c)
    label_bg(c, A.WATER_X - 28, 164, "coastal", 12, 400, C.ink, "end")
    ring(c, 52, 196, 16, "verified")
    c.text(52, 228, "geology", 12, 400, C.ink, "middle")
    ring(c, 196, 150, 16, "screening")
    label_bg(c, 218, 154, "wet ground", 12, 400)
    ring(c, 256, 106, 16, "unresolved")
    c.glyph("question", 256, 106, C.unresolved)
    label_bg(c, 256, 80, "mine opening", 12, 400, C.ink, "middle")
    c.text(664, 19, "Dashed ring with ?: unresolved evidence", 11, 400, C.ink2, "end")
    p.rail_cards([("Searched layers", "Coverage, date and category limits stay visible.", "verified"),
                  ("Screening clue", "A mapped point or overlap starts another records question.",
                   "screening"),
                  ("No result", "No mapped overlap is not a clean bill of health.", "limit")])
    c.save(OUT / "fig-07-case-a-screening.svg")


def parcel_b(c, label=True):
    c.path("M150,128 L278,122 L288,226 L158,236 Z", fill=C.white, stroke=C.accent, sw=2.25)
    c.rect(186, 156, 64, 38, fill=C.municipal)
    if label:
        label_bg(c, 156, 254, "Parcel B", 13, 700, C.accent)


def case_b_base(c):
    plate_base(c, "M372,8 L444,8 L444,332 L376,332 L392,262 L366,220 L392,170 L360,120 L386,66 Z")
    road(c, [(78, 8), (300, 332)])
    road(c, [(8, 290), (444, 150)])


def case_b_orientation():
    """REDRAW figure-18 (Case B map 1)."""
    W, H = 672, 340
    c = Canvas(W, H, "Case B begins with occupancy clues",
               "Fictional Parcel B in a serviced community with a building footprint and nearby streets.")
    case_b_base(c)
    parcel_b(c)
    c.text(218, 214, "building footprint", 12, 400, C.ink, "middle")
    c.text(414, 300, "water", 12, 400, C.accent, "middle")
    label_bg(c, 120, 84, "street", 11, 400, C.ink2, "middle")
    label_bg(c, 70, 262, "street", 11, 400, C.ink2, "middle")
    plate_end(c)
    gap, ch = 12, (MH - 12) / 2
    card(c, CX, MY, CW, ch, "accent", "Place",
         "Locate fictional Case B among roads, communities and water.")
    card(c, CX, MY + ch + gap, CW, ch, "neutral", "Limit",
         "Orientation does not prove access, title, condition or services.")
    c.save(OUT / "fig-07-case-b-orientation.svg")


def case_b_access():
    """REDRAW figure-20 (Case B map 3)."""
    W, H = 672, 340
    c = Canvas(W, H, "Case B: observe without trespass",
               "Parcel B with a driveway, drainage path and public observation points outside the boundary.")
    case_b_base(c)
    # contours (terrain)
    for i, off in enumerate((0, 22, 44)):
        c.path(f"M{300+off},{8} C{290+off},{90} {330+off},{150} {318+off},{240} S{340+off},{320} {336+off},{332}",
               stroke=C.granite, sw=0.75)
    label_bg(c, 350, 52, "contours", 11, 400, C.ink2)
    parcel_b(c)
    # visible track / driveway from the road to the building (screening, dotted)
    c.path("M60,272 L186,190", stroke=C.screening, sw=3, dash="1.5 5")
    dotted(c)
    label_bg(c, 26, 244, "Visible track?", 12, 700, C.ink)
    # drainage path toward the water
    c.arrow_path("M288,206 C318,214 330,236 350,250 S372,266 384,264", C.accent, 2.25, "6 4")
    label_bg(c, 300, 284, "drainage path", 12, 400, C.ink)
    # public observation points on the public road, outside the boundary
    for (x, y) in ((122, 248), (330, 180)):
        c.circle(x, y, 6, fill=C.white, stroke=C.ink, sw=2)
        c.circle(x, y, 2, fill=C.ink)
    c.circle(30, 312, 6, fill=C.white, stroke=C.ink, sw=2)
    c.circle(30, 312, 2, fill=C.ink)
    label_bg(c, 42, 316, "public observation point (outside the parcel)", 11, 400, C.ink2)
    plate_end(c)
    gap, ch = 10, (MH - 20) / 3
    card(c, CX, MY, CW, ch, "screening", "Visible approach",
         "A road or track on a map is a screening clue.")
    card(c, CX, MY + ch + gap, CW, ch, "unresolved", "Legal access",
         "Registry and legal review must answer the right-of-way question.")
    card(c, CX, MY + 2 * (ch + gap), CW, ch, "verified", "Terrain",
         "Contours and drainage change site questions, not legal rights.")
    c.save(OUT / "fig-07-case-b-access.svg")


def case_b_screening():
    """REDRAW figure-22 (Case B map 5), moved from Chapter 8."""
    W, H = 672, 340
    c = Canvas(W, H, "Case B: a historical clue is not a finding",
               "Parcel B with a former-use symbol, a nearby registry point and arrows to questions.")
    case_b_base(c)
    parcel_b(c, label=False)
    label_bg(c, 146, 254, "Parcel B", 13, 700, C.accent)
    # former-use symbol on the building (screening clue: dotted ring)
    ring(c, 218, 175, 30, "screening")
    c.line(140, 162, 186, 170, C.ink, 0.75)
    label_bg(c, 84, 166, "former-use symbol", 12, 700, C.ink, "middle")
    # nearby registry point (verified added public record: solid teal square)
    c.rect(318, 186, 14, 14, fill=C.verified)
    label_bg(c, 340, 214, "registry point", 12, 700, C.ink)
    # arrows to the two questions
    q1 = (246, 50, 172, 42)
    q2 = (146, 266, 272, 42)
    for (x, y, w, h), text in ((q1, "Records question"), (q2, "Environmental-professional question")):
        c.box(x, y, w, h, fill=C.white, stroke=C.unresolved, sw=1.5, dash=DASH)
        c.glyph("question", x + 16, y + h / 2, C.unresolved)
        c.text(x + 30, y + h / 2 + 4, text, 12, 700, C.ink)
    c.arrow(234, 150, 282, 92, C.ink, 1.5)
    c.arrow(325, 186, 340, 92, C.ink, 1.5)
    c.arrow(222, 205, 236, 266, C.ink, 1.5)
    c.arrow(322, 220, 318, 266, C.ink, 1.5)
    plate_end(c)
    gap, ch = 10, (MH - 20) / 3
    sym = lambda st: (lambda x, y: ring(c, x, y, 7, st))
    card(c, CX, MY, CW, ch, "verified", "Searched layers",
         "Coverage, date and category limits stay visible.")
    card(c, CX, MY + ch + gap, CW, ch, "screening", "Screening clue",
         "A mapped point or overlap starts another records question.", sym("screening"))
    card(c, CX, MY + 2 * (ch + gap), CW, ch, "neutral", "No result",
         "No mapped overlap is not a clean bill of health.")
    c.save(OUT / "fig-07-case-b-screening.svg")


# --------------------------------------------------------------------------- three records
def three_records():
    """NEW: four records beneath one fictional yard (md:821, 827, 839-841, 853, 861, 871)."""
    W, H = 672, 464
    c = Canvas(W, H, "Three records beneath one yard",
               "Four records under one fictional yard, each with its result type and limit.")
    # ground scene
    gy = 112
    c.rect(8, 8, 656, gy - 8, fill=C.white)
    c.rect(8, gy, 656, 18, fill=C.paper2, stroke="none")
    c.line(8, gy, 664, gy, C.granite, 1.5)
    # building (former workshop)
    c.path(f"M110,{gy} L110,{gy-46} L160,{gy-70} L210,{gy-46} L210,{gy} Z",
           fill=C.white, stroke=C.ink, sw=1.5)
    c.text(160, gy - 14, "building", 12, 400, C.ink, "middle")
    c.text(486, 24, "Fictional Breakwater Lane yard", 11, 700, C.ink2)
    c.text(486, 40, "Composite — not a real property", 11, 400, C.ink2)
    c.text(486, 56, "Pre-bid records only; no entry", 11, 400, C.ink2)
    # tank-area hint and well point
    c.circle(418, gy - 6, 5, fill="none", stroke=C.unresolved, sw=2)
    c.text(418, gy - 18, "well point (estimated)", 11, 400, C.ink2, "middle")
    # four records
    cols = [
        ("screening", "Former-use history", "Positive clue",
         "Expands environmental inquiry: fuel, solvents, waste handling, fill, prior spills.",
         "Does not establish a spill, contaminant, tank location or present condition."),
        ("neutral", "Contaminated-site search", "Bounded negative",
         "No parcel-specific record located under the recorded search method and date.",
         "Reporting and search limits: not a clean site or a complete reporting history."),
        ("unresolved", "Well log", "Positive record",
         "One estimated point near the parcel; the log describes depth and a reported yield.",
         "Parcel association, geolocation and present condition are uncertain."),
        ("neutral", "On-site sewage search", "Negative result",
         "No older on-site sewage record returned.",
         "Retention boundary is central: a record is unlikely for a property more than seven years old."),
    ]
    bw, gap, top = 152, 15.33, gy + 40
    bh = 228
    for i, (st, head, kind, body, limit) in enumerate(cols):
        x = 8 + i * (bw + gap)
        col = STATE[st][0]
        card_h = bh
        c.box(x, top, bw, card_h, fill=C.white, stroke=col, sw=STATE[st][1], dash=STATE[st][2])
        if st == "screening":
            dotted(c)
        if STATE[st][4]:
            c.glyph(STATE[st][4], x + bw - 14, top + 16, col)
        y = c.text_block(x + 10, top + 22, bw - 34, head, 13, 700, C.ink)
        c.text(x + 10, y + 2, kind, 12, 700, STATE[st][3] if st != "screening" else C.ink)
        y = c.text_block(x + 10, y + 22, bw - 20, body, 12)
        c.line(x + 10, y - 4, x + bw - 10, y - 4, C.rule, 0.75)
        c.text(x + 10, y + 12, "Limit", 11, 700, C.ink2)
        c.text_block(x + 10, y + 28, bw - 20, limit, 12)
    # misleading symmetry strip
    sy = top + bh + 18
    c.rect(8, sy, 656, 56, fill=C.caution_tint, stroke="none")
    c.text(24, sy + 34, "No · yes · no", 18, 700, C.caution)
    from svgkit import width
    wv = width("No · yes · no", 18, 700)
    c.line(20, sy + 28, 28 + wv, sy + 28, C.caution, 2.25)
    c.text_block(52 + wv, sy + 24, 600 - wv - 40,
                 "Flattening the records this way creates misleading symmetry. Classify each "
                 "result with its limit instead.", 12, 400, C.ink)
    c.save(OUT / "fig-07-three-records-one-yard.svg")


# --------------------------------------------------------------------------- coastal scenario
def coastal_scenario():
    """NEW: how to read a coastal hazard scenario (md:893-895; md:593)."""
    W, H = 672, 420
    c = Canvas(W, H, "Reading a coastal hazard scenario",
               "The 2100 worst case and what its colour does and does not report.")
    # left: selector and the stack
    lx, lw = 8, 300
    c.text(lx, 24, "Scenario selector", 13, 700, C.accent)
    sel = ["Current", "2050", "2100"]
    sw_ = 92
    for i, s in enumerate(sel):
        x = lx + i * (sw_ + 4)
        on = s == "2100"
        c.rect(x, 34, sw_, 28, fill=C.accent if on else C.white, stroke=C.accent, sw=1.5, rx=3)
        c.text(x + sw_ / 2, 53, s, 12, 700, C.white if on else C.accent, "middle")
    c.text_block(lx, 82, lw - 8, "The years are sea-level scenarios, not extra probabilities.",
                 11, 400, C.ink2)
    c.text(lx, 120, "2100 worst-case coastal flooding scenario", 13, 700, C.ink)
    layers = [("Projected sea-level rise", C.accent_mid),
              ("A one-in-one-hundred-year storm surge", C.accent_tint),
              ("The highest high tide", C.white)]
    y = 132
    for i, (s, fill) in enumerate(layers):
        c.rect(lx + 22, y, lw - 30, 40, fill=fill, stroke=C.accent, sw=1.5)
        c.text(lx + 34, y + 25, s, 12, 400 if i else 700, C.ink)
        if i < 2:
            c.text(lx + 10, y + 46, "+", 18, 700, C.accent, "middle")
        y += 44
    c.text_block(lx + 22, y + 16, lw - 30,
                 "Combined, these make one future combination visible across a large area: "
                 "a planning view.", 12, 400, C.ink)
    # inset: river studies
    iy = 340
    c.rect(lx, iy, lw - 8, 72, fill=C.paper2, stroke=C.rule, sw=0.75)
    c.text(lx + 10, iy + 20, "Published river-study layers are different", 12, 700, C.ink)
    c.text_block(lx + 10, iy + 38, lw - 28,
                 "A one-percent or five-percent annual-exceedance probability describes the event "
                 "mapped by that study (see Chapter 5).", 11, 400, C.ink2)
    # right: two panels
    rx, rw = 336, 328
    c.box(rx, 8, rw, 184, fill=C.white, stroke=C.verified, sw=1.5)
    c.text(rx + 14, 32, "What the colour means", 13, 700, C.verified)
    yy = 54
    for s in ["The selected scenario", "Current data", "The model", "The resolution",
              "The map guidance"]:
        c.glyph("check", rx + 22, yy - 4, C.complete)
        c.text(rx + 38, yy, s, 12)
        yy += 22
    c.text_block(rx + 14, yy + 6, rw - 28, "Search by community, address or PID.",
                 11, 400, C.ink2)
    c.box(rx, 204, rw, 208, fill=C.white, stroke=C.unresolved, sw=1.5, dash=DASH)
    c.text(rx + 14, 228, "What it does not report", 13, 700, C.unresolved)
    c.glyph("question", rx + rw - 18, 224, C.unresolved)
    yy = 252
    for s in ["The elevation of a surveyed building floor",
              "The condition of a shoreline protection structure",
              "The route floodwater would take through a culvert",
              "The damage a particular storm will cause"]:
        c.text(rx + 18, yy, "–", 12, 700, C.unresolved)
        yy = c.text_block(rx + 32, yy, rw - 46, s, 12) + 4
    c.line(rx + 14, yy - 4, rx + rw - 14, yy - 4, C.rule, 0.75)
    c.text_block(rx + 14, yy + 14, rw - 28,
                 "Not an engineering design, an insurance decision or a municipal development "
                 "approval.", 12, 700, C.ink)
    c.save(OUT / "fig-07-coastal-scenario.svg")


# --------------------------------------------------------------------------- positional uncertainty
def positional_uncertainty():
    """NEW: abandoned-mine-opening point with roughly 50 m positional uncertainty (md:903-907)."""
    W, H = 672, 400
    c = Canvas(W, H, "A point with a position quality",
               "A mine-opening symbol just outside a fictional parcel, with a circle of about 50 m.")
    # scale: 50 m = 80 units
    m50 = 80
    map_frame(c, 8, 8, 420, 384)
    # road
    road(c, [(8, 300), (428, 248)], 10)
    c.text(24, 286, "road", 12, 400, C.ink2)
    # parcel
    c.path("M80,60 L270,52 L282,226 L94,244 Z", fill=C.white, stroke=C.accent, sw=2.25)
    c.text(96, 82, "Fictional parcel", 13, 700, C.accent)
    c.text(96, 98, "(graphical line)", 11, 400, C.ink2)
    # building site
    c.rect(150, 150, 50, 34, fill="none", stroke=C.ink, sw=1.5, dash="4 3")
    c.text(175, 202, "building site", 12, 400, C.ink, "middle")
    # mine opening symbol just outside the line
    px, py = 316, 204
    c.circle(px, py, m50, fill=C.unresolved, stroke="none")
    c.items[-1] = c.items[-1].replace('fill="#7a3e6e"', 'fill="#7a3e6e" fill-opacity="0.08"')
    c.circle(px, py, m50, fill="none", stroke=C.unresolved, sw=1.75)
    c.items[-1] = c.items[-1].replace("/>", f' stroke-dasharray="{DASH}"/>')
    # symbol: crossed-hammers-free neutral mark: filled square rotated
    c.path(f"M{px},{py-8} L{px+8},{py} L{px},{py+8} L{px-8},{py} Z", fill=C.ink, stroke=C.ink, sw=1)
    c.line(px + 10, py, px + m50, py, C.unresolved, 1.25)
    label_bg(c, px + m50 / 2 + 6, py - 8, "roughly 50 m", 11, 700, C.unresolved, "middle")
    label_bg(c, px + 12, py + 24, "inventory point", 12, 700, C.ink)
    # scale bar
    sx, sy = 24, 360
    c.rect(sx, sy, m50, 6, fill=C.ink)
    c.line(sx, sy - 4, sx, sy + 10, C.ink, 1.25)
    c.line(sx + m50, sy - 4, sx + m50, sy + 10, C.ink, 1.25)
    c.text(sx + m50 + 8, sy + 8, "50 m (fictional plate)", 11, 400, C.ink2)
    c.text(24, 30, COMPOSITE, 11, 400, C.granite)
    # right-hand notes
    rx, rw = 444, 220
    c.box(rx, 8, rw, 176, fill=C.white, stroke=C.unresolved, sw=1.5, dash=DASH)
    c.text(rx + 12, 32, "Position quality", 13, 700, C.unresolved)
    c.glyph("question", rx + rw - 16, 28, C.unresolved)
    c.text_block(rx + 12, 54, rw - 24,
                 "2024 inventory: positions on private land can have lower confidence and may be "
                 "inaccurate by roughly 50 metres. That distance can cross a road, parcel line, "
                 "building site or shoreline on a rural map.", 12)
    c.box(rx, 196, rw, 196, fill=C.white, stroke=C.granite, sw=1.5)
    c.text(rx + 12, 220, "Coverage limits", 13, 700, C.ink)
    yy = 244
    for s in ["The inventory is incomplete.", "Undocumented openings exist.",
              "It excludes surface expressions of subsidence.",
              "Site conditions may change."]:
        c.text(rx + 12, yy, "–", 12, 700, C.ink)
        yy = c.text_block(rx + 24, yy, rw - 36, s, 12) + 6
    c.save(OUT / "fig-07-positional-uncertainty.svg")


# --------------------------------------------------------------------------- beam
def negative_search_beam():
    """REDRAW figure-23, with the beam the original alt text describes."""
    W, H = 672, 412
    c = Canvas(W, H, "A negative search has a beam",
               "A flashlight beam covers part of a dark field; hazards outside it remain unknown.")
    fx, fy, fw, fh = 8, 8, 656, 220
    c.rect(fx, fy, fw, fh, fill=C.ink, stroke="none")
    # flashlight at left
    c.rect(22, 106, 46, 24, fill=C.granite, stroke=C.white, sw=1, rx=3)
    c.path("M68,102 L80,96 L80,140 L68,134 Z", fill=C.granite, stroke=C.white, sw=1)
    # beam
    c.path("M80,98 L470,30 L470,206 L80,138 Z", fill=C.white, stroke="none")
    c.items[-1] = c.items[-1].replace('fill="#ffffff"', 'fill="#ffffff" fill-opacity="0.92"')
    c.text(270, 104, "The source's coverage", 13, 700, C.ink, "middle")
    c.text_block(200, 124, 180, "It can reveal a post, a stair or clear floor in the area it illuminates.", 12, 400, C.ink)
    # field labels inside the beam
    c.text(462, 172, "time · location · record type", 11, 400, C.ink2, "end")
    # outside the beam
    for (x, y) in ((540, 70), (600, 150), (520, 190), (130, 56), (240, 200)):
        c.circle(x, y, 9, fill="none", stroke=C.white, sw=1.5)
        c.items[-1] = c.items[-1].replace("/>", ' stroke-dasharray="3 2.5"/>')
        c.text(x, y + 4, "?", 12, 700, C.white, "middle")
    c.text_block(500, 104, 150, "Outside the beam: hazards remain unknown.", 12, 700, C.white)
    # four coverage cards
    cards = [("Time", "Was the relevant period included?"),
             ("Place", "Was the parcel inside the source's mapped coverage?"),
             ("Record type", "Would this source contain the event or condition?"),
             ("Match rule", "Could spelling, geometry or identifiers hide a record?")]
    bw, gap, top, bh = 155, 12, 244, 100
    for i, (h, q) in enumerate(cards):
        x = 8 + i * (bw + gap)
        c.box(x, top, bw, bh, fill=C.accent_tint, stroke=C.accent, sw=1.5)
        c.text(x + 12, top + 24, h, 13, 700, C.accent)
        c.text_block(x + 12, top + 46, bw - 24, q, 12)
    c.text_block(8, top + bh + 26, 656,
                 "No result means only that this search, in this source, found no matching record.",
                 13, 700, C.ink)
    c.text_block(8, top + bh + 50, 656,
                 "Limit of the picture: a public database's beam is not random, and different "
                 "sources are not equally weak.", 12, 400, C.ink2)
    c.save(OUT / "fig-07-negative-search-beam.svg")


# --------------------------------------------------------------------------- result states
def result_states():
    """NEW: positive, negative and error states (md:919-927; md:633)."""
    W, H = 672, 360
    c = Canvas(W, H, "Three result states",
               "Positive, negative and error results and what each note preserves.")
    cols = [
        ("verified", "Positive", "Feature returned",
         "The service returned a feature or scenario under the recorded conditions.",
         ["source", "date", "geometry", "attributes", "coverage limits", "positional quality",
          "next question"], None),
        ("neutral", "Negative", "Query completed with no returned feature",
         "The query completed and returned no feature under those conditions.",
         ["source", "date", "settings", "completeness limits",
          "the exact narrow concern the result did not confirm"], None),
        ("unresolved", "Error", "No reliable result obtained",
         "The researcher does not have a completed result.",
         ["the failure"],
         "Draw no negative conclusion."),
    ]
    bw, gap, top = 210, 13, 66
    bh = H - top - 8
    # banner above error column
    ex = 8 + 2 * (bw + gap)
    c.rect(ex, 8, bw, 48, fill=C.paper2)
    c.text_block(ex + 10, 26, bw - 20,
                 "A failed service, loading timeout, hidden layer or incorrect selection is not "
                 "“nothing found”.", 11, 400, C.ink)
    for i, (st, head, sub, meaning, keep, stop) in enumerate(cols):
        x = 8 + i * (bw + gap)
        col, sw, dash, hcol, glyph = STATE[st]
        c.box(x, top, bw, bh, fill=C.white, stroke=col, sw=sw, dash=dash)
        if st == "verified":
            c.glyph("check", x + bw - 18, top + 20, C.verified)
        if glyph:
            c.glyph(glyph, x + bw - 18, top + 20, col)
        if st == "neutral":
            c.circle(x + bw - 18, top + 20, 7, fill="none", stroke=C.granite, sw=1.5)
            c.line(x + bw - 23, top + 25, x + bw - 13, top + 15, C.granite, 1.5)
        c.text(x + 12, top + 26, head, 13, 700, hcol)
        y = c.text_block(x + 12, top + 46, bw - 24, sub, 12, 700)
        y = c.text_block(x + 12, y + 4, bw - 24, meaning, 12, 400, C.ink2)
        c.line(x + 12, y - 2, x + bw - 12, y - 2, C.rule, 0.75)
        c.text(x + 12, y + 16, "Preserve", 11, 700, C.ink2)
        y += 34
        for k in keep:
            c.text(x + 14, y, "–", 12, 700, col)
            y = c.text_block(x + 26, y, bw - 38, k, 12) + 2
        if stop:
            y = c.text_block(x + 12, y + 14, bw - 24,
                             "Then retry, or use the authoritative source directly.", 12)
            c.rect(x + 10, y + 4, bw - 20, 30, fill=C.caution_tint)
            c.text(x + 18, y + 24, stop, 12, 700, C.caution)
    c.save(OUT / "fig-07-result-states.svg")


if __name__ == "__main__":
    case_a_screening()
    case_b_screening()
    case_b_orientation()
    three_records()
    case_b_access()
    coastal_scenario()
    positional_uncertainty()
    negative_search_beam()
    result_states()
