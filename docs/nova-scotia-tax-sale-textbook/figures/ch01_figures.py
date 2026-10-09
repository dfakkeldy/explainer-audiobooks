"""Chapter 1 figures (spec: design/figure-style.md; plan: design/chapter-plan.md, Chapter 1).

    .venv/bin/python figures/ch01_figures.py

Every label below is taken from the original figure (figure-02, figure-03), its alt text, or the
manuscript lines the chapter plan cites; review/claims/ch01.md maps each one.
"""
import json
from pathlib import Path

from svgkit import C, DASH, Canvas, width

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src/assets/figures"


# --------------------------------------------------------------------------- pre-sale timeline
def pre_sale_timeline():
    """NEW. md:59-61, 65, 71-75, 87, 97."""
    W, H = 672, 470
    c = Canvas(W, H, "From unpaid taxes to sale day",
               "Timeline, not to scale, of the steps before a tax sale outside Halifax.")

    # band: whose statute
    c.rect(8, 8, 656, 28, fill=C.accent_tint)
    c.text(18, 27, "Outside Halifax: Municipal Government Act", 13, 700, C.accent)
    c.text(654, 27, "Halifax: parallel framework under its Charter", 12, 400, C.ink2, "end")

    def station(x, y, head, body, w, anchor="start", hollow=False):
        if hollow:
            c.circle(x, y, 6, fill=C.white, stroke=C.municipal, sw=2.25)
        else:
            c.circle(x, y, 6, fill=C.municipal)
        tx = x - 6 if anchor == "start" else x
        c.text(tx, y + 28, head, 13, 700, C.ink, anchor)
        if anchor == "start":
            c.text_block(tx, y + 46, w, body, 12)
        else:
            from svgkit import wrap
            for i, ln in enumerate(wrap(body, 12, w)):
                c.text(tx, y + 46 + i * 15.6, ln, 12, 400, C.ink, anchor)

    # ---- row 1: arrears and eligibility
    A1 = 110
    c.text(18, 64, "1  Arrears and eligibility", 13, 700, C.municipal)
    c.line(20, A1, 640, A1, C.municipal, 2.25)
    c.arrow(630, A1, 654, A1, C.municipal, 2.25, gap=0)
    station(30, A1, "Taxes unpaid",
            "A tax lien attaches. It ranks ahead of other claims, liens and encumbrances and need not be registered.", 180)
    station(250, A1, "Earliest start",
            "For taxes unpaid from the immediately preceding taxation year: not before June 30 of the following year.",
            180, hollow=True)
    station(470, A1, "Backstop",
            "Must be put up for sale once taxes are unpaid for the three preceding fiscal years, subject to the "
            "Act\u2019s exceptions and a possible council deferral.", 180, hollow=True)
    # municipal practice inside the window
    px = 360
    c.line(px, A1 - 26, px, A1 - 4, C.ink2, 1.5, "2 2")
    c.text(px, A1 - 46, "Inverness and Chester: eligible", 11, 400, C.ink2, "middle")
    c.text(px, A1 - 32, "after two years (municipal practice)", 11, 400, C.ink2, "middle")

    # ---- row 2: notices and sale
    A2 = 340
    c.text(18, 252, "2  Notices and sale", 13, 700, C.municipal)
    c.line(20, A2, 548, A2, C.municipal, 2.25)
    c.arrow(540, A2, 562, A2, C.municipal, 2.25, gap=0)
    st = [(30, "Preliminary notice", "Sent by the municipality"),
          (160, "Title search", "Helps identify owner and interest holders; may order a survey"),
          (290, "Notice of intent", "To the owner and people with mortgages, liens or charges"),
          (420, "Public notice", "Qualifying newspaper or the municipal website")]
    for x, head, body in st:
        station(x, A2, head, body, 116)

    # sale
    sx, sw_ = 566, 98
    c.box(sx, A2 - 18, sw_, 36, fill=C.municipal, stroke=C.municipal)
    c.text(sx + sw_ / 2, A2 + 5, "Sale", 15, 700, C.white, "middle")
    c.text_block(sx, A2 + 46, sw_, "Public auction, or tender with council\u2019s consent", 12)
    c.text_block(sx, A2 + 100, sw_, "Bidders enter after notices", 12, 700, C.accent)

    def bracket(x0, x1, y, label):
        c.path(f"M{x0},{y + 7} L{x0},{y} L{x1},{y} L{x1},{y + 7}", stroke=C.accent, sw=1.5)
        c.text((x0 + x1) / 2, y - 6, label, 12, 700, C.accent, "middle")

    bracket(30, 160, A2 - 30, "at least 14 days to pay")
    bracket(290, sx, A2 - 68, "60 days to pay before the sale")
    bracket(420, sx, A2 - 30, "at least 30 consecutive days")

    c.text(18, H - 12, "Not to scale", 11, 700, C.granite)
    c.save(OUT / "fig-01-pre-sale-timeline.svg")


def _wrap_centered(s, size, maxw):
    from svgkit import wrap
    return wrap(s, size, maxw)


# --------------------------------------------------------------------------- two clocks
def two_clocks():
    """REDRAW of figure-03 (labels verbatim), plus the older-arrears fork (Q9; md:201)."""
    W, H = 672, 380
    c = Canvas(W, H, "Auction day connects two clocks",
               "Municipal collection clock before auction day; purchaser and redemption clock after it.")
    LX, LW = 8, 196
    RX, RW = 468, 196
    MX, MW = 244, 184
    top, bh, gap = 40, 74, 26
    ys = [top + i * (bh + gap) for i in range(3)]

    c.text(LX, 24, "Municipal collection clock", 13, 700, C.municipal)
    c.text(RX, 24, "Purchaser / redemption clock", 13, 700, C.verified)

    left = [("Arrears", "Eligibility and council decisions"),
            ("Notice", "Preliminary notice, title search, sale notice"),
            ("Advertise", "At least 30 consecutive days")]
    for y, (h, b) in zip(ys, left):
        c.box(LX, y, LW, bh, fill=C.white, stroke=C.municipal, tab=C.municipal)
        c.text(LX + 18, y + 24, h, 13, 700, C.municipal)
        c.text_block(LX + 18, y + 44, LW - 30, b, 12)
    for y in ys[:2]:
        c.arrow(LX + LW / 2, y + bh, LX + LW / 2, y + bh + gap, C.municipal)

    right = [("Certificate", "After full payment", C.verified),
             ("Six-month route", "Possible redemption; protect and insure", C.verified),
             ("Deed stage", "If not redeemed, request and pay for deed", C.complete)]
    for y, (h, b, col) in zip(ys, right):
        c.box(RX, y, RW, bh, fill=C.white, stroke=col, sw=2)
        c.text(RX + 14, y + 24, h, 13, 700, col)
        c.text_block(RX + 14, y + 44, RW - 26, b, 12)
    for y in ys[:2]:
        c.arrow(RX + RW / 2, y + bh, RX + RW / 2, y + bh + gap, C.verified)

    # hinge
    hy, hh = ys[0] + 30, 200
    c.rect(MX, hy, MW, hh, fill=C.accent, rx=3)
    c.text(MX + MW / 2, hy + 40, "Auction day", 18, 700, C.white, "middle")
    c.text(MX + MW / 2, hy + 68, "A hinge,", 13, 400, C.white, "middle")
    c.text(MX + MW / 2, hy + 85, "not a finish line", 13, 400, C.white, "middle")
    c.line(MX + 24, hy + 110, MX + MW - 24, hy + 110, C.accent_mid, 1)
    c.text(MX + MW / 2, hy + 136, "Event terms control", 12, 400, C.white, "middle")
    c.text(MX + MW / 2, hy + 152, "payment and", 12, 400, C.white, "middle")
    c.text(MX + MW / 2, hy + 168, "registration details.", 12, 400, C.white, "middle")

    # advertise -> hinge ; hinge -> certificate
    ay = ys[2] + bh / 2
    c.arrow_path(f"M{LX + LW},{ay} L{MX - 18},{ay} L{MX - 18},{hy + hh - 20} L{MX - 3},{hy + hh - 20}",
                 C.municipal)
    cy = ys[0] + bh / 2
    c.arrow_path(f"M{MX + MW},{hy + 20} L{MX + MW + 18},{hy + 20} L{MX + MW + 18},{cy} L{RX - 3},{cy}",
                 C.verified)

    # older-arrears fork: hinge -> deed stage, dashed
    dy = ys[2] + bh / 2 + 10
    fx = MX + MW - 40
    c.arrow_path(f"M{fx},{hy + hh} L{fx},{dy} L{RX - 3},{dy}", C.complete, dash=DASH)
    c.text_block(MX + 4, hy + hh + 20, fx - MX - 12,
                 "Older-arrears route: no six-month redemption", 11, color=C.ink2)

    # band
    by = H - 42
    c.rect(8, by, 656, 34, fill=C.paper2)
    c.text(W / 2, by + 22, "The sale ends neither the municipality’s record work nor the purchaser’s legal work.",
           12, 400, C.ink, "middle")
    c.save(OUT / "fig-01-two-clocks.svg")


# --------------------------------------------------------------------------- whose rules
def whose_rules():
    """NEW. md:65-67, 89, 97, 99-101."""
    W, H = 672, 352
    c = Canvas(W, H, "Whose rules answer which question",
               "Three tiers: provincial law, municipal practice, the current event notice.")
    LX, LW = 8, 150          # tier label column
    BX = 170                 # content column start
    BR = 520                 # content column right edge
    tiers = [
        (8, 104, "Provincial law", "Why a sale can occur"),
        (124, 100, "Municipal practice", "How a municipality operates inside that frame"),
        (236, 108, "Current event notice", "Whether this sale is happening, in what form, under which local instructions"),
    ]
    fills = [C.accent_tint, C.paper2, C.white]
    for (y, h, head, q), fill in zip(tiers, fills):
        c.rect(LX, y, BR - LX, h, fill=fill, stroke=C.rule, sw=0.75)
        c.text(LX + 12, y + 24, head, 13, 700, C.accent)
        c.text_block(LX + 12, y + 44, LW - 20, q, 12, color=C.ink)

    # tier 1 boxes
    y = 8 + 22
    bw = (BR - BX - 22) / 2
    for i, (h, b) in enumerate([("Municipal Government Act", "Outside Halifax"),
                                ("Halifax Regional Municipality Charter", "Halifax")]):
        x = BX + i * (bw + 10)
        c.box(x, y, bw, 76, fill=C.white, stroke=C.municipal, tab=C.municipal)
        ny = c.text_block(x + 16, y + 24, bw - 24, h, 12, 700, C.municipal)
        c.text(x + 16, ny + 2, b, 12, 400, C.ink)

    # tier 2 examples
    ex = [("Example", "Inverness and Chester describe accounts as eligible after two years."),
          ("Example", "Halifax lists possible sale-expense categories: an example, not a price list.")]
    yy = 124 + 26
    for h, b in ex:
        c.text(BX, yy, h + ":", 12, 700, C.ink)
        yy = c.text_block(BX + width("Example: ", 12, 700), yy, BR - BX - 70, b, 12) + 10

    # tier 3
    c.box(BX, 236 + 26, BR - BX - 12, 56, fill=C.white, stroke=C.accent, sw=2.25)
    c.text_block(BX + 14, 236 + 50, BR - BX - 40,
                 "The current notice of the municipality running the event", 12, 700, C.accent)

    # call-out: what controls a live event
    c.text_block(536, 258, 128, "For a live event, the current notice of the municipality running it controls.",
                 12, 700, C.accent)
    c.arrow(534, 290, BR - 12 + 2, 290, C.accent, 2.25)
    c.save(OUT / "fig-01-whose-rules.svg")


# --------------------------------------------------------------------------- municipal methods map
SYMBOL = {"auction": "dot", "tender": "square", "auction + tender": "half", "check current notice": "ring",
          "auction record": "dot"}
MAP_UNITS = {
    # full name in the dataset: (label, method, label dx, dy, anchor)
    "Municipality of the County of Inverness": ("Inverness", "auction", -70, -40, "end"),
    "Cape Breton Regional Municipality": ("CBRM", "auction", 12, -58, "middle"),
    "Municipality of the County of Richmond": ("Richmond", "auction", 34, 56, "start"),
    "Municipality of the County of Pictou": ("Pictou", "tender", -20, -58, "middle"),
    "Municipality of the County of Annapolis": ("Annapolis", "auction + tender", -40, 64, "end"),
    "Municipality of the County of Kings": ("Kings", "auction record", -26, -62, "end"),
    "Municipality of the District of Chester": ("Chester", "check current notice", 34, 66, "start"),
}


def municipal_methods_map():
    """REDRAW of figure-02 as a true outline (Q8). Labels and methods verbatim from figure-02."""
    data = json.loads((ROOT / "figures/data/ns-municipal-units.json").read_text())
    W, H = 672, 440
    c = Canvas(W, H, "One statute, different event methods",
               "Seven Nova Scotia municipal units with the sale method each used in dated examples.")
    for u in data["units"]:   # leave out Sable Island: far offshore, not part of the lesson
        u["rings"] = [r for r in u["rings"] if not all(p[1] < 44.2 and p[0] > -42.75 for p in r)]
    xs = [p[0] for u in data["units"] for r in u["rings"] for p in r]
    ys = [p[1] for u in data["units"] for r in u["rings"] for p in r]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    s = min((W - 140) / (x1 - x0), (H - 30) / (y1 - y0))
    ox = W - 12 - (x1 - x0) * s
    oy = 12

    def P(p):
        return ox + (p[0] - x0) * s, oy + (y1 - p[1]) * s

    def d_of(rings):
        out = []
        for r in rings:
            pts = [P(p) for p in r]
            out.append("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z")
        return " ".join(out)

    centroids = {}
    # base units first, highlighted units on top; towns are drawn last as plain base units
    order = sorted(data["units"], key=lambda u: (u["full"] in MAP_UNITS, u["kind"] == "Town"))
    for u in order:
        hl = u["full"] in MAP_UNITS
        c.path(d_of(u["rings"]), fill="#d7e5e8" if hl else C.paper2,
               stroke=C.accent if hl else C.rule, sw=1.1 if hl else 0.6)
        if hl:
            big = max(u["rings"], key=len)
            pts = [P(p) for p in big]
            A = cx = cy = 0
            for (xa, ya), (xb, yb) in zip(pts, pts[1:] + pts[:1]):
                cr = xa * yb - xb * ya
                A += cr
                cx += (xa + xb) * cr
                cy += (ya + yb) * cr
            centroids[u["full"]] = (cx / (3 * A), cy / (3 * A))

    for full, (label, method, dx, dy, anchor) in MAP_UNITS.items():
        x, y = centroids[full]
        if full.endswith("Richmond"):
            x, y = x - 6, y + 4
        lx, ly = x + dx, y + dy
        c.line(x, y, lx - (4 if anchor == "start" else -4 if anchor == "end" else 0), ly - 14 if dy > 0 else ly + 24,
               C.ink2, 0.75)
        _symbol(c, x, y, SYMBOL[method])
        c.text(lx, ly, label, 12, 700, C.ink, anchor)
        c.text(lx, ly + 14, method, 11, 400, C.ink2, anchor)

    # legend (top left, over the Gulf / New Brunswick side, where nothing is drawn)
    lx, ly = 12, 26
    c.text(lx, ly, "Sale method in the dated examples", 12, 700, C.ink)
    for i, (k, lab) in enumerate([("dot", "auction (Kings: auction record)"), ("square", "tender"),
                                  ("half", "auction + tender"), ("ring", "check current notice")]):
        yy = ly + 22 + i * 20
        _symbol(c, lx + 7, yy - 4, k)
        c.text(lx + 22, yy, lab, 11, 400, C.ink)
    c.text(lx, ly + 112, "Shaded: the seven municipal units named", 11, 400, C.ink2)

    c.text(W - 12, H - 30, "Dated procedural examples • refresh the event notice", 12, 700, C.accent, "end")
    c.text(W - 12, H - 14, "Boundaries simplified from Province of Nova Scotia open data", 11, 400, C.ink2, "end")
    c.save(OUT / "fig-01-municipal-methods-map.svg")


def _symbol(c, x, y, kind):
    col = C.municipal
    if kind == "dot":
        c.circle(x, y, 6, fill=col, stroke=C.white, sw=1.5)
    elif kind == "square":
        c.rect(x - 5.5, y - 5.5, 11, 11, fill=col, stroke=C.white, sw=1.5)
    elif kind == "half":
        c.circle(x, y, 6, fill=C.white, stroke=col, sw=2)
        c.path(f"M{x},{y - 6} A6,6 0 0,0 {x},{y + 6} Z", fill=col, stroke="none", sw=0)
    elif kind == "ring":
        c.circle(x, y, 6, fill=C.white, stroke=col, sw=2)


if __name__ == "__main__":
    pre_sale_timeline()
    two_clocks()
    whose_rules()
    municipal_methods_map()
