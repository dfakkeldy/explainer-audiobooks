"""Shared base for the Case A plates (fictional Parcel A, the Maple Ridge discussion).

Used by figures/ch06_figures.py (fig-06-case-a-*) and available to Chapter 7
(fig-07-case-a-screening) so every Case A plate has the same fictional geometry, north arrow,
"not to scale" note and composite stamp (chapter plan, Chapter 6: "one consistent family").

Geometry follows the manuscript, not the original plates' layout: the long, narrow sliver lies
just behind two roadside lots, and a pale track leaves the public road, crosses one of those lots
and seems to continue into the sliver (md:695). The original plates (figure-13 to -16) drew a road
running through the parcel; see review/flagged-claims.md F-06b.

    from case_a_plate import Plate
    p = Plate(c)            # draws the base map in the left panel
    p.rail_card(0, "Place", "Locate fictional Case A among roads, communities and water.", "plain")
"""
from svgkit import C, DASH, DOT, wrap

# panel: the map occupies the left of a 672-wide canvas; the rail of side cards the right
MX, MY, MW, MH = 8, 30, 424, 300          # map frame
RX, RW = 448, 216                         # rail cards
WATER_X = 372                             # approximate shoreline
LAND = "#f3f1ec"                          # paper2
WATER = "#e6eef0"                         # accent_tint
SCREEN_TINT = "#f7efdc"                   # pale tint of screening amber (parcel highlight)

# card styles: (stroke, width, dash, heading colour, glyph)
CARD = {
    "plain": (C.accent, 1.5, None, C.accent, None),
    "limit": (C.granite, 2.25, None, C.ink, None),
    "verified": (C.verified, 1.5, None, C.verified, None),
    "screening": (C.screening, 1.75, DOT, C.ink, None),
    "unresolved": (C.unresolved, 1.5, DASH, C.unresolved, "question"),
}


def road_y(x):
    """Centre line of the main public road (gently sloping, west to east)."""
    return 300 - 0.066 * (x - MX)


def above_road(x, d):
    return road_y(x) - d


# parcel and lots, in offsets above the road centre line
LOT_X = (150, 240, 330)                   # two roadside lots: 150-240 and 240-330
LOT_D = (7, 70)                           # from road edge to rear lot line
SLIVER_X = (132, 352)
SLIVER_D = (70, 98)                       # sliver: just behind the lots
TRACK = [(218, 7), (223, 40), (229, 70), (238, 84)]   # x, offset above road (inside lot 1)


def pt(x, d):
    return x, above_road(x, d)


def poly(points):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in points) + " Z"


def polyline(points):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in points)


class Plate:
    def __init__(self, c, stamp=True, base_roads=True):
        self.c = c
        self._defs()
        self.base(stamp, base_roads)

    def _defs(self):
        self.c.raw(
            '<defs><clipPath id="mapclip">'
            f'<rect x="{MX}" y="{MY}" width="{MW}" height="{MH}"/></clipPath>'
            '<pattern id="hatch-zone" width="8" height="8" patternUnits="userSpaceOnUse" '
            'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="8" '
            f'stroke="{C.verified}" stroke-width="1" stroke-opacity="0.35"/></pattern></defs>')

    # ------------------------------------------------------------------ base map
    def base(self, stamp, base_roads):
        c = self.c
        c.raw('<g clip-path="url(#mapclip)">')
        c.rect(MX, MY, MW, MH, fill=LAND)
        shore = [(WATER_X, MY), (WATER_X - 10, 80), (WATER_X + 6, 130), (WATER_X - 4, 190),
                 (WATER_X + 10, 250), (WATER_X + 2, MY + MH)]
        c.path(poly(shore + [(MX + MW, MY + MH), (MX + MW, MY)]), fill=WATER, stroke="none")
        c.path(polyline(shore), stroke=C.accent_mid, sw=1)
        # second public road (north-south, west side)
        c.path(polyline([(96, MY), (102, 160), (112, MY + MH)]), stroke=C.ink2, sw=4.5)
        # main public road (stops at the shore)
        x1 = WATER_X - 2
        c.line(MX, road_y(MX), x1, road_y(x1), C.ink2, 5)
        # communities: small building clusters
        for (cx, cy) in [(30, 70), (46, 80), (24, 90), (290, 60), (304, 52), (310, 70)]:
            c.rect(cx, cy, 8, 8, fill=C.granite)
        # roadside lots
        for a, b in [(LOT_X[0], LOT_X[1]), (LOT_X[1], LOT_X[2])]:
            c.path(poly([pt(a, LOT_D[0]), pt(b, LOT_D[0]), pt(b, LOT_D[1]), pt(a, LOT_D[1])]),
                   fill="none", stroke=C.granite, sw=0.9)
        c.raw("</g>")
        c.rect(MX, MY, MW, MH, stroke=C.rule, sw=1)
        # labels
        c.text(18, 112, "community", 11, 400, C.ink2)
        c.text(288, 46, "community", 11, 400, C.ink2)
        c.text(394, 222, "water", 11, 400, C.accent)
        lx = 22
        c.text(lx, road_y(lx) - 8, "public road", 11, 400, C.ink2)
        c.text(116, 96, "public road", 11, 400, C.ink2)
        for a, b in [(LOT_X[0], LOT_X[1]), (LOT_X[1], LOT_X[2])]:
            m = (a + b) / 2 - (12 if a == LOT_X[0] else 0)
            c.text(m, above_road(m, 14), "roadside lot", 11, 400, C.ink2, anchor="middle")
        # north arrow and scale note
        nx, ny = 404, 48
        c.path(f"M{nx},{ny - 12} L{nx + 6},{ny + 6} L{nx},{ny + 2} L{nx - 6},{ny + 6} Z",
               fill=C.ink, stroke=C.ink, sw=1)
        c.text(nx, ny + 20, "N", 11, 700, C.ink, anchor="middle")
        c.text(MX + MW - 6, MY + MH - 8, "Not to scale", 11, 400, C.ink2, anchor="end")
        if stamp:
            c.text(MX, 19, "Composite — not a real property; not a survey.", 12, 700, C.ink)

    def parcel(self, stroke=C.screening, sw=2.25, dash=None, fill=SCREEN_TINT, label=True):
        a, b = SLIVER_X
        d0, d1 = SLIVER_D
        self.c.path(poly([pt(a, d0), pt(b, d0), pt(b, d1), pt(a, d1)]), fill=fill,
                    stroke=stroke, sw=sw, dash=dash)
        if label:
            self.c.text(286, above_road(286, 84) + 4, "Parcel A", 12, 700, C.ink, anchor="middle")

    def track(self, color=C.screening, sw=2.25, dash=DASH):
        pts = [pt(x, d) for x, d in TRACK]
        self.c.path(polyline(pts), stroke=color, sw=sw, dash=dash)
        return pts

    # ------------------------------------------------------------------ rail
    def rail_cards(self, cards, top=MY, bottom=MY + MH, gap=10):
        """cards: list of (heading, body, style). Heights split the rail evenly."""
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
