"""Chapter 6 figures (spec: design/figure-style.md; plan: design/chapter-plan.md, Chapter 6).

    .venv/bin/python figures/ch06_figures.py

The four Case A plates redraw figure-13 to figure-16 on the shared base in case_a_plate.py; their
card headings and texts are the original figures' own words (sentence case), and the map marks are
the ones each original alt text names. fig-06-independent-gates is new and uses only md:747-801.
review/claims/ch06.md maps every label.
"""
from pathlib import Path

from svgkit import C, DASH, DOT, Canvas, wrap
from case_a_plate import (MX, MY, MW, MH, SLIVER_D, SLIVER_X, Plate, above_road, pt, road_y,
                          polyline)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src/assets/figures"
H = 340


def orientation():
    c = Canvas(672, H, title="Case A starts with location")
    p = Plate(c)
    p.parcel()
    p.rail_cards([
        ("Place", "Locate fictional Case A among roads, communities and water.", "plain"),
        ("Limit", "Orientation does not prove access, title, condition or services.", "limit"),
    ])
    c.save(OUT / "fig-06-case-a-orientation.svg")


def access():
    c = Canvas(672, H, title="Case A: a visible route is not a right")
    p = Plate(c)
    # steep contours across the rear of the sliver and beyond
    for k, d in enumerate((112, 124, 136, 148)):
        xs = range(250, 372, 6)
        pts = [(x, above_road(x, d) - 6 * ((x - 250) / 120) ** 2 * (1 + k * 0.4)) for x in xs]
        c.path(polyline(pts), stroke=C.granite, sw=0.9)
    c.text(258, above_road(258, 156) - 4, "steep contours", 11, 400, C.ink2)
    p.parcel()
    pts = p.track()
    c.text(214, above_road(214, 0) + 20, "visible track?", 12, 700, C.ink, anchor="end")
    # question mark where legal access would need proof: on the track inside the roadside lot
    qx, qy = pts[1]
    c.glyph("question", qx + 1, qy, C.unresolved)
    c.text(qx + 12, qy - 6, "legal access", 11, 700, C.unresolved)
    c.text(qx + 12, qy + 7, "needs proof", 11, 400, C.unresolved)
    p.rail_cards([
        ("Visible approach", "A road or track on a map is a screening clue.", "screening"),
        ("Legal access", "Registry and legal review must answer the right-of-way question.",
         "unresolved"),
        ("Terrain", "Contours and drainage change site questions, not legal rights.", "verified"),
    ])
    c.save(OUT / "fig-06-case-a-access.svg")


def identity():
    c = Canvas(672, H, title="Case A: identify the research target")
    p = Plate(c)
    p.parcel(stroke=C.verified, sw=3)
    # identifier card with a leader to the parcel
    bx, by, bw, bh = 128, 122, 112, 60
    c.path(polyline([(bx + bw / 2, by + bh), (bx + bw / 2 + 30, above_road(bx + 90, 90))]),
           stroke=C.verified, sw=1.25)
    c.box(bx, by, bw, bh, fill=C.white, stroke=C.verified, sw=1.5)
    for i, s in enumerate(("Lien ••••", "AAN ••••", "PID ••••")):
        c.text(bx + 10, by + 18 + i * 16, s, 12, 700, C.ink)
    c.text(bx, by - 6, "fictional identifiers", 11, 400, C.ink2)
    # prominent stamp
    sx, sy = 130, 42
    c.rect(sx, sy, 150, 34, fill=C.white, stroke=C.granite, sw=2.25)
    c.text(sx + 75, sy + 23, "Not a survey", 18, 700, C.granite, anchor="middle")
    p.rail_cards([
        ("Lien / AAN / PID", "Fictional Case A identifiers point to one research target.",
         "verified"),
        ("Boundary", "The graphical outline is not a survey or title opinion.", "screening"),
    ])
    c.save(OUT / "fig-06-case-a-identity.svg")


def planning():
    c = Canvas(672, H, title="Case A: planning and servicing separate")
    p = Plate(c)
    # zones: Zone A to the west (hatched, solid outline); an unconfirmed zone to the east (dashed)
    za = [(MX, MY), (88, MY), (88, MY + MH), (MX, MY + MH)]
    c.raw('<g clip-path="url(#mapclip)">')
    c.path("M" + " L".join(f"{x},{y}" for x, y in za) + " Z", fill="url(#hatch-zone)",
           stroke=C.verified, sw=1.5)
    zq = [(358, MY), (MX + MW, MY), (MX + MW, MY + MH), (358, MY + MH)]
    c.path("M" + " L".join(f"{x},{y}" for x, y in zq) + " Z", fill="none",
           stroke=C.unresolved, sw=1.5, dash=DASH)
    c.raw("</g>")
    c.rect(MX + 4, MY + 6, 52, 20, fill=C.white)
    c.text(MX + 10, MY + 21, "Zone A", 12, 700, C.verified)
    c.rect(362, MY + 60, 54, 20, fill=C.white)
    c.text(368, MY + 75, "Zone ?", 12, 700, C.unresolved)
    p.parcel(label=False)
    c.text(186, above_road(186, 84) + 4, "Parcel A", 12, 700, C.ink, anchor="middle")
    # frontage dimension line along the sliver's road-facing edge, offset into the lots
    a, b = SLIVER_X[0] + 10, SLIVER_X[0] + 120
    d = SLIVER_D[0] - 12
    (x1, y1), (x2, y2) = pt(a, d), pt(b, d)
    c.line(x1, y1, x2, y2, C.screening, 1.5, dash=DOT, cap="round")
    for x, y in ((x1, y1), (x2, y2)):
        c.line(x, y - 6, x, y + 6, C.screening, 1.5)
    c.rect((x1 + x2) / 2 - 26, (y1 + y2) / 2 - 9, 64, 15, fill=C.white)
    c.text((x1 + x2) / 2 + 6, (y1 + y2) / 2 + 2, "frontage?", 11, 700, C.ink, anchor="middle")
    # well and septic question icons inside the parcel
    for x, lab in ((262, "well"), (306, "septic")):
        y = above_road(x, 84)
        c.glyph("question", x, y, C.unresolved)
        c.text(x + 10, y + 4, lab, 11, 400, C.ink)
    # planner-confirmation callout
    bx, by, bw, bh = 160, 46, 128, 40
    c.box(bx, by, bw, bh, fill=C.white, stroke=C.accent, sw=1.5)
    c.text_block(bx + 10, by + 17, bw - 20, "planner confirms", 12, 700, C.accent)
    c.text(bx + 10, by + 32, "current zone and rule", 11, 400, C.ink)
    c.arrow(bx + 70, by + bh, 214, above_road(214, 100), C.accent, 1.5)
    p.rail_cards([
        ("Zone", "Confirm the current rule and intended use in writing.", "verified"),
        ("Frontage", "Mapped contact is not a survey measurement.", "screening"),
        ("Services", "Well, septic, water and sewer require separate evidence.", "unresolved"),
    ])
    c.save(OUT / "fig-06-case-a-planning.svg")


GATES = [
    # heading, who answers, Maple Ridge state, style
    ("Visible approach", "Map and imagery: a physical observation",
     "Track visible from the public road", "screening"),
    ("Legal access", "Title instruments and plans; lawyer and surveyor",
     "Registered passage right appears to benefit the parcel; needs final legal and survey "
     "confirmation", "unresolved"),
    ("Road frontage", "Applicable rules; the planning authority",
     "Frontage and lot-status answers still required", "unresolved"),
    ("Zoning", "Permitted use; the planner",
     "A zone in which a dwelling may be permitted", "verified"),
    ("Approval and services", "Application, permits and qualified advice",
     "Building envelope, physical access, services and approvals still required", "unresolved"),
]
STYLE = {
    "screening": (C.screening, 1.75, DOT, C.ink, None),
    "unresolved": (C.unresolved, 1.5, DASH, C.unresolved, "question"),
    "verified": (C.verified, 1.5, None, C.verified, "check"),
}


def gates():
    W, Hh = 672, 372
    c = Canvas(W, Hh, title="Five separate gates")
    n, gap, x0 = 5, 10, 8
    gw = (W - 2 * x0 - gap * (n - 1)) / n           # 123.2
    top, gh = 34, 92
    c.text(x0, 20, "Each gate is a separate question with its own authority", 13, 700, C.ink)
    stop = 150
    c.text(x0, stop - 6, "Fictional Maple Ridge, after the access research improves "
           "(composite case, not a real property)", 11, 400, C.ink2)
    for i, (head, who, state, style) in enumerate(GATES):
        x = x0 + i * (gw + gap)
        col, sw, dash, hcol, glyph = STYLE[style]
        # gate head: number + heading, solid accent
        c.box(x, top, gw, gh, fill=C.accent_tint, stroke=C.accent, sw=1.5)
        c.text(x + 10, top + 18, str(i + 1), 13, 700, C.accent)
        yy = c.text_block(x + 24, top + 18, gw - 30, head, 13, 700, C.ink)
        c.text_block(x + 10, max(yy, top + 40) + 4, gw - 18, who, 11, 400, C.ink2)
        if i < n - 1:
            c.arrow(x + gw + 1, top + gh / 2, x + gw + gap + 2, top + gh / 2, C.accent, 1.5, gap=1)
        # Maple Ridge state
        sy, sh = stop + 2, 118
        c.box(x, sy, gw, sh, fill=C.white, stroke=col, sw=sw, dash=dash)
        if glyph:
            c.glyph(glyph, x + gw - 14, sy + 14, col)
        c.text_block(x + 10, sy + 34, gw - 18, state, 12, 400, C.ink)
    # outcome bar
    oy = 286
    c.rect(x0, oy, W - 2 * x0, 44, fill=C.caution_tint, stroke=C.nogo, sw=3, rx=3)
    c.glyph("bar", x0 + 20, oy + 22, C.nogo)
    c.text(x0 + 38, oy + 19, "A rational no", 13, 700, C.nogo)
    c.text(x0 + 38, oy + 35, "“I will not bid on the assumption that they work out later.”",
           12, 400, C.ink)
    c.text(x0, Hh - 14, "None of these records grants permission to enter and inspect the land.",
           12, 700, C.ink)
    c.save(OUT / "fig-06-independent-gates.svg")


if __name__ == "__main__":
    orientation()
    access()
    identity()
    planning()
    gates()
