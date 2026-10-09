"""Chapter 2 figures (spec: design/figure-style.md; plan: design/chapter-plan.md, Chapter 2).

    .venv/bin/python figures/ch02_figures.py

Every label below is taken from the original figure (figure-04, figure-05, figure-06), its alt
text, or the manuscript lines the chapter plan cites; review/claims/ch02.md maps each one.
"""
from pathlib import Path

from svgkit import C, DASH, DOT, Canvas, width, wrap

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src/assets/figures"


def centred_block(c, cx, y, maxw, s, size=12, weight=400, color=C.ink, lh=1.3):
    lines = wrap(s, size, maxw, weight)
    for i, ln in enumerate(lines):
        c.text(cx, y + i * size * lh, ln, size, weight, color, "middle")
    return y + len(lines) * size * lh


# --------------------------------------------------------------------------- packet anatomy
def packet_anatomy():
    """REDRAW figure-04. md:115, md:119 (alt), md:23."""
    W, H = 672, 410
    c = Canvas(W, H, "A parcel sheet is a set of claims to verify",
               "Annotated fictional tax-sale parcel sheet.")
    SX, SW = 160, 352                     # the sheet
    c.rect(SX, 10, SW, 390, fill=C.white, stroke=C.rule, sw=1.5, rx=3)
    c.rect(SX, 10, SW, 34, fill=C.municipal, rx=0)
    c.text(SX + 12, 32, "Fictional tax-sale parcel sheet", 13, 700, C.white)
    bw = width("Not a real parcel", 11, 700) + 16
    c.rect(SX + SW - 10 - bw, 17, bw, 20, fill=C.caution, rx=3)
    c.text(SX + SW - 10 - bw / 2, 31, "Not a real parcel", 11, 700, C.white, "middle")

    CW = 158
    X1, X2 = SX + 12, SX + 12 + CW + 12
    rows = [56, 128, 200]
    RH = 62

    def field(x, y, value, job):
        c.box(x, y, CW, RH, fill=C.white, stroke=C.municipal, sw=1.25, tab=C.municipal)
        c.text(x + 14, y + 21, value, 13, 700, C.ink)
        c.text_block(x + 14, y + 39, CW - 20, job, 11, 400, C.ink2)

    field(X1, rows[0], "Lien 12", "Auction-list key")
    field(X1, rows[1], "AAN ••••4567", "Assessment account")
    field(X1, rows[2], "PID ••••9999", "Mapped parcel identifier")
    field(X2, rows[0], "Recovery $4,200", "Taxes, interest and sale costs")
    field(X2, rows[1], "Assessment $68,000", "Assessment record — not sale value")
    field(X2, rows[2], "Redeemable: yes", "Ordinary six-month route shown")

    # legal description area (left) and orientation map (right)
    LY, LH = 274, 114
    c.box(X1, LY, CW, LH, fill=C.paper2, stroke=C.municipal, sw=1.25, tab=C.municipal)
    c.text(X1 + 14, LY + 22, "Legal description area", 12, 700, C.ink)
    c.text_block(X1 + 14, LY + 42, CW - 22,
                 "Read the record. Do not treat it as a survey or a site inspection.", 12)
    c.box(X2, LY, CW, LH, fill=C.white, stroke=C.municipal, sw=1.25, tab=C.municipal)
    mx, my, mw, mh = X2 + 16, LY + 12, CW - 26, 68
    c.rect(mx, my, mw, mh, fill=C.accent_tint, stroke=C.accent, sw=1)
    c.path(f"M{mx + 8},{my + mh - 8} L{mx + 46},{my + 22} L{mx + 76},{my + 46} "
           f"L{mx + 100},{my + 16} L{mx + mw - 8},{my + mh - 8} Z",
           fill=C.accent_mid, stroke="none", sw=0)
    c.text(X2 + 14 + (CW - 14) / 2, LY + 100, "Orientation map", 12, 700, C.ink, "middle")

    # callouts
    def callout(x, y, head, body):
        w = 136
        h = 30 + c.block_height(body, 12, w - 20)
        c.box(x, y, w, h, fill=C.white, stroke=C.accent, sw=1.5)
        c.text(x + 10, y + 20, head, 13, 700, C.accent)
        c.text_block(x + 10, y + 38, w - 20, body, 12)
        return h

    # left: identity -> bracket over lien, AAN, PID
    h = callout(8, 130, "Identity", "Which record are we following?")
    bx = X1 - 6
    c.path(f"M{bx + 4},{rows[0]} L{bx},{rows[0]} L{bx},{rows[2] + RH} L{bx + 4},{rows[2] + RH}",
           stroke=C.accent, sw=1.5)
    c.arrow(144, 130 + h / 2, bx, 130 + h / 2)
    # left: limits -> legal description
    h = callout(8, 290, "Limits", "What does this sheet not establish?")
    c.arrow(144, 290 + h / 2, X1, 290 + h / 2)
    # right: money -> recovery, legal route -> redeemable
    RX = 528
    h = callout(RX, 56, "Money", "What amount is advertised for recovery?")
    c.arrow(RX, rows[0] + RH / 2, X2 + CW, rows[0] + RH / 2)
    h = callout(RX, 196, "Legal route", "Is a six-month redemption period shown?")
    c.arrow(RX, rows[2] + RH / 2, X2 + CW, rows[2] + RH / 2)
    c.save(OUT / "fig-02-packet-anatomy.svg")


# --------------------------------------------------------------------------- identifier ladder
def identifier_ladder():
    """REDRAW figure-05. md:133, 137, 149-155; md:31; figure-05 labels and footer."""
    W, H = 672, 280
    c = Canvas(W, H, "Identifiers help records meet",
               "Seven record cards and five conclusions they do not prove.")
    cards = [("Lien", "auction list"), ("AAN", "tax account"), ("PID", "mapped parcel"),
             ("Location", "place clue"), ("Assessment", "assessment record"),
             ("Map", "graphical clue"), ("Legal description", "registry wording")]
    n, gap = 7, 10
    cw = (W - 16 - gap * (n - 1)) / n
    y0, ch = 10, 116
    for i, (head, sub) in enumerate(cards):
        x = 8 + i * (cw + gap)
        cx = x + cw / 2
        c.box(x, y0, cw, ch, fill=C.white, stroke=C.municipal, sw=1.5)
        c.circle(cx, y0 + 22, 12, fill=C.municipal)
        c.text(cx, y0 + 27, str(i + 1), 13, 700, C.white, "middle")
        yy = centred_block(c, cx, y0 + 56, cw - 8, head, 13, 700)
        centred_block(c, cx, max(yy + 2, y0 + 78), cw - 8, sub, 11, 400, C.ink2)
        if i < n - 1:
            ax = x + cw + 1
            c.path(f"M{ax},{y0 + ch / 2 - 5} L{ax + gap - 2},{y0 + ch / 2} L{ax},{y0 + ch / 2 + 5} Z",
                   fill=C.accent_mid, stroke="none", sw=0)

    c.text(8, 158, "The chain helps records meet. It does not prove:", 13, 700, C.ink)
    nots = ["exact boundary", "legal access", "site condition", "market value", "buildability"]
    m, g2 = 5, 10
    bw = (W - 16 - g2 * (m - 1)) / m
    for i, s in enumerate(nots):
        x = 8 + i * (bw + g2)
        c.box(x, 172, bw, 44, fill=C.caution_tint, stroke=C.caution, sw=1.5)
        tw = width(s, 12, 700)
        nw = width("not", 11, 700)
        tx = x + (bw - (nw + 6 + tw)) / 2
        c.text(tx, 199, "not", 11, 700, C.caution)
        c.text(tx + nw + 6, 199, s, 12, 700, C.ink)
        c.line(tx + nw + 3, 195, tx + nw + 9 + tw, 195, C.caution, 1.25)

    c.rect(8, 232, W - 16, 40, fill=C.accent_tint, rx=3)
    c.text(W / 2, 257, "Each field narrows a question. Authority comes from the source qualified "
           "to answer it.", 13, 400, C.ink, "middle")
    c.save(OUT / "fig-02-identifier-ladder.svg")


# --------------------------------------------------------------------------- two catalogue keys
def _key(c, x, y, color):
    """A plain key glyph, bow centred at (x, y), shaft to the right."""
    c.circle(x, y, 11, fill=C.white, stroke=color, sw=3)
    c.line(x + 11, y, x + 46, y, color, 3)
    c.line(x + 36, y, x + 36, y + 9, color, 3)
    c.line(x + 44, y, x + 44, y + 7, color, 3)


def _pin(c, x, y, color):
    c.path(f"M{x},{y + 16} C{x - 4},{y + 8} {x - 11},{y + 2} {x - 11},{y - 5} "
           f"A11,11 0 1,1 {x + 11},{y - 5} C{x + 11},{y + 2} {x + 4},{y + 8} {x},{y + 16} Z",
           fill=C.white, stroke=color, sw=3)
    c.circle(x, y - 5, 3.5, fill=color)


def two_catalogue_keys():
    """NEW. md:131-139, md:149-151, md:159."""
    W, H = 672, 424
    c = Canvas(W, H, "Two catalogue keys and a pointer",
               "AAN and PID open different records; a civic address points to a place.")
    colw, gap = 208, 16
    cols = [8, 8 + colw + gap, 8 + 2 * (colw + gap)]
    data = [
        ("key", "AAN", "Assessment Account Number", "Assessment account",
         "Assessed value, classification and other taxation information.",
         "The legal boundary, road access, ownership quality or an approved use."),
        ("key", "PID", "Parcel Identification Number", "Mapped land parcel",
         "Routes toward parcel mapping and registry information.",
         "A survey of every boundary on the ground, access, permitted use, physical condition, "
         "or freedom from competing interests."),
        ("pin", "Civic address", "or location field", "A place",
         "Points toward a building or civic point. Helps find the area.",
         "The mapped land parcel. Related to the PID but not interchangeable."),
    ]
    top = 10
    for x, (icon, name, full, drawer, holds, nots) in zip(cols, data):
        cx = x + colw / 2
        # key / pin row
        if icon == "key":
            _key(c, x + 22, top + 26, C.accent)
            c.text(x + 80, top + 26, name, 18, 700, C.accent)
        else:
            _pin(c, x + 22, top + 28, C.accent)
            c.text(x + 44, top + 26, name, 18, 700, C.accent)
        c.text(x + (80 if icon == "key" else 44), top + 44, full, 11, 400, C.ink2)
        c.arrow(cx, top + 56, cx, top + 86)
        # drawer (or place)
        dy, dh = top + 88, 112
        if icon == "key":
            c.box(x, dy, colw, dh, fill=C.accent_tint, stroke=C.accent, sw=1.5)
            c.rect(cx - 22, dy + 8, 44, 8, fill=C.white, stroke=C.accent, sw=1.5, rx=3)
            c.text(x + 12, dy + 38, drawer, 13, 700, C.ink)
            c.text_block(x + 12, dy + 58, colw - 24, holds, 12)
        else:
            c.box(x, dy, colw, dh, fill=C.white, stroke=C.accent, sw=1.5, dash=DASH)
            c.text(x + 12, dy + 38, drawer, 13, 700, C.ink)
            c.text_block(x + 12, dy + 58, colw - 24, holds, 12)
        # does not establish
        ny = dy + dh + 14
        c.box(x, ny, colw, 104, fill=C.white, stroke=C.rule, sw=1)
        c.text(x + 12, ny + 20, "Does not establish", 12, 700, C.caution)
        c.text_block(x + 12, ny + 40, colw - 24, nots, 12)

    # footnote: Property Online and the analogy's limit
    fy = 10 + 88 + 112 + 14 + 104 + 16
    c.line(8, fy, W - 8, fy, C.rule, 0.75)
    c.text_block(8, fy + 20, W - 16,
                 "Property Online, Nova Scotia’s subscription system, supports searches using "
                 "PID, owner, AAN and civic address.", 12, 400, C.ink)
    c.text_block(8, fy + 44, W - 16,
                 "Where the analogy ends: land records do more than describe an object on a shelf, "
                 "and legal interests cannot be reduced to a library entry. Its value is that "
                 "choosing the wrong key opens the wrong catalogue.", 11, 400, C.ink2)
    c.save(OUT / "fig-02-two-catalogue-keys.svg")


# --------------------------------------------------------------------------- reconcile the packet
def reconcile_the_packet():
    """REDRAW figure-06. md:37, 163, 197, 1059-1061; figure-06 labels and footer."""
    W, H = 672, 316
    c = Canvas(W, H, "Preserve disagreement between sources",
               "Six sources kept separately feed a comparison table.")
    srcs = ["Summary list", "Detail sheet", "Live webpage", "Registry", "Result sheet",
            "Council record"]
    n, gap = 6, 8
    bw = (W - 16 - gap * (n - 1)) / n
    for i, s in enumerate(srcs):
        x = 8 + i * (bw + gap)
        c.box(x, 10, bw, 48, fill=C.white, stroke=C.municipal, sw=1.5)
        c.text(x + bw / 2, 30, s, 12, 700, C.ink, "middle")
        c.text(x + bw / 2, 47, "keep separately", 11, 400, C.ink2, "middle")
        c.arrow(x + bw / 2, 60, x + bw / 2, 86, C.granite)

    cols = [(8, "Question"), (190, "Source A"), (350, "Source B"), (510, "File status")]
    ty, hh, rh = 86, 30, 40
    c.rect(8, ty, W - 16, hh, fill=C.municipal)
    for x, s in cols:
        c.text(x + 12, ty + 20, s, 12, 700, C.white)
    rows = [("Lien 6 detail", "listed", "detail missing", "Unresolved"),
            ("Recovery amount", "summary amount", "detail amount differs", "Ask municipality"),
            ("May 2025 outcome", "35 reported sold", "31 result rows", "Keep both counts")]
    for r, row in enumerate(rows):
        y = ty + hh + r * rh
        c.rect(8, y, W - 16, rh, fill=C.paper2 if r % 2 == 0 else C.white)
        for k, ((x, _), s) in enumerate(zip(cols, row)):
            if k == 3:
                sw_ = width(s, 12, 700)
                c.rect(x + 6, y + 8, sw_ + 14, 24, fill=C.white, stroke=C.screening, sw=1.75,
                       dash=DOT, rx=3, extra=' stroke-linecap="round"')
                c.text(x + 13, y + 25, s, 12, 700, C.ink)
            else:
                c.text(x + 12, y + 25, s, 12, 700 if k == 0 else 400, C.ink)
    tb = ty + hh + 3 * rh
    c.rect(8, ty, W - 16, tb - ty, stroke=C.rule, sw=1)

    c.rect(8, tb + 18, W - 16, 44, fill=C.white, stroke=C.screening, sw=1.75, dash=DOT, rx=3,
           extra=' stroke-linecap="round"')
    c.text(W / 2, tb + 45, "A discrepancy is a research finding — not permission to choose "
           "the convenient version.", 13, 400, C.ink, "middle")
    c.save(OUT / "fig-02-reconcile-the-packet.svg")


# --------------------------------------------------------------------------- source-state labels
def source_state_labels():
    """NEW. md:235, 237, 241."""
    W, H = 672, 380
    c = Canvas(W, H, "A dated research file",
               "Harbour Road's file card and three dated source states.")
    # index card
    CX, CY, CWd, CH = 116, 30, 440, 118
    c.rect(CX, CY - 20, 230, 22, fill=C.accent, rx=3)
    c.text(CX + 10, CY - 4, "Harbour Road · research file", 12, 700, C.white)
    c.rect(CX, CY, CWd, CH, fill=C.white, stroke=C.rule, sw=1.5)
    c.line(CX, CY, CX + CWd, CY, C.accent, 3)
    c.text(CX + CWd - 10, CY - 6, "Composite — not a real property", 11, 400, C.granite, "end")
    rows = [("Packet retrieved", "date"), ("Last event-status check", "date"),
            ("Beside every amount and marker", "a source page and date")]
    for i, (k, v) in enumerate(rows):
        y = CY + 30 + i * 36
        c.text(CX + 14, y, k, 12, 700, C.ink)
        c.line(CX + 220, y + 4, CX + CWd - 14, y + 4, C.rule, 0.75)
        c.text(CX + 224, y, v, 12, 400, C.ink2)
        if i < 2:
            c.line(CX + 8, y + 16, CX + CWd - 8, y + 16, C.rule, 0.75)

    # timeline of source states
    TY = 210
    c.text(8, TY - 26, "Source-state labels", 13, 700, C.accent)
    c.text(W - 8, TY - 26, "Not to scale", 11, 400, C.granite, "end")
    c.line(20, TY, 560, TY, C.accent, 2.25)
    c.line(560, TY, 652, TY, C.accent, 2.25, DASH)
    xs = [112, 336, 560]
    states = [
        ("Packet retrieved July 20", "Describes one snapshot.", False),
        ("Municipal page checked August 10", "Describes a later state.", False),
        ("Treasurer confirmed withdrawn August 11",
         "Would describe an event-day fact, only if that confirmation actually occurred.", True),
    ]
    cw = 200
    for x, (head, body, cond) in zip(xs, states):
        if cond:
            c.circle(x, TY, 7, fill=C.white, stroke=C.accent, sw=2.25)
        else:
            c.circle(x, TY, 7, fill=C.accent)
        bx = min(max(x - cw / 2, 8), W - 8 - cw)
        c.line(x, TY + 7, x, TY + 20, C.accent, 1.5, DASH if cond else None)
        hh = c.block_height(head, 12, cw - 24, 700) + c.block_height(body, 12, cw - 24) + 26
        c.box(bx, TY + 20, cw, hh, fill=C.white if cond else C.accent_tint, stroke=C.accent,
              sw=1.5, dash=DASH if cond else None)
        yy = c.text_block(bx + 12, TY + 40, cw - 24, head, 12, 700)
        c.text_block(bx + 12, yy + 2, cw - 24, body, 12)
    c.text(W / 2, H - 14, "The dates preserve change instead of forcing one document to erase "
           "another.", 12, 400, C.ink2, "middle")
    c.save(OUT / "fig-02-source-state-labels.svg")


if __name__ == "__main__":
    packet_anatomy()
    identifier_ladder()
    two_catalogue_keys()
    reconcile_the_packet()
    source_state_labels()
