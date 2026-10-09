"""Chapter 3 figures (spec: design/figure-style.md; plan: design/chapter-plan.md, Chapter 3).

    .venv/bin/python figures/ch03_figures.py

Every label below is taken from the original figure (figure-07, figure-08), its alt text, or the
manuscript lines the chapter plan cites; review/claims/ch03.md maps each one.
"""
from pathlib import Path

from svgkit import C, DASH, Canvas, wrap

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src/assets/figures"


def centred(c, cx, y, maxw, s, size=12, weight=400, color=C.ink, lh=1.3):
    """Centred wrapped text; y is the first baseline. Returns the next free baseline."""
    lines = wrap(s, size, maxw, weight)
    for i, ln in enumerate(lines):
        c.text(cx, y + i * size * lh, ln, size, weight, color, "middle")
    return y + len(lines) * size * lh


# --------------------------------------------------------------------------- redeemable route
def redeemable_route():
    """REDRAW of figure-07 (labels verbatim); six-month bracket and discharge ending added
    (md:259, 309, 315, 329)."""
    W, H = 672, 408
    c = Canvas(W, H, "The ordinary redeemable route",
               "Full payment, certificate holder, six months, then redemption or the deed stage.")

    # six-month bracket over the top row
    bx0, bx1, by = 12, 660, 30
    c.line(bx0, by, bx1, by, C.unresolved, 1.5, DASH)
    c.line(bx0, by - 8, bx0, by + 8, C.unresolved, 2.25)
    c.line(bx1, by - 8, bx1, by + 8, C.unresolved, 2.25)
    lab = "Six months after the sale"
    from svgkit import width
    lw = width(lab, 12, 700) + 16
    c.rect(W / 2 - lw / 2, by - 11, lw, 22, fill=C.white)
    c.text(W / 2, by + 4, lab, 12, 700, C.unresolved, "middle")
    c.text(bx0, by - 14, "Sale", 11, 400, C.ink2)

    # top row
    top, bh, bw, gap = 56, 104, 196, 34
    xs = [8, 8 + bw + gap, 8 + 2 * (bw + gap)]
    # 1 full payment: municipal fact (solid tab)
    c.box(xs[0], top, bw, bh, fill=C.white, stroke=C.municipal, tab=C.municipal)
    c.text(xs[0] + 18, top + 26, "Full payment", 13, 700, C.municipal)
    c.text_block(xs[0] + 18, top + 48, bw - 30, "Treasurer issues and registers certificate", 12)
    # 2 certificate holder: verified record (solid outline)
    c.box(xs[1], top, bw, bh, fill=C.white, stroke=C.verified, sw=1.5)
    c.text(xs[1] + 14, top + 26, "Certificate holder", 13, 700, C.verified)
    c.text_block(xs[1] + 14, top + 48, bw - 26,
                 "Protect land • insure insurable buildings • keep records", 12)
    # 3 six months: unresolved (dashed + ?)
    c.box(xs[2], top, bw, bh, fill=C.white, stroke=C.unresolved, dash=DASH)
    c.text(xs[2] + 14, top + 26, "Six months", 13, 700, C.unresolved)
    c.glyph("question", xs[2] + bw - 18, top + 21, C.unresolved)
    c.text_block(xs[2] + 14, top + 48, bw - 26,
                 "Qualifying interests may redeem through the treasurer", 12)
    for i in range(2):
        c.arrow(xs[i] + bw, top + bh / 2, xs[i + 1], top + bh / 2, C.accent)

    # fork
    fy0 = top + bh
    fy = fy0 + 26
    lo_y = fy + 30
    lw_, rw_ = 316, 316
    lx, rx = 8, W - 8 - rw_
    lcx, rcx = lx + lw_ / 2, rx + rw_ / 2
    sx = xs[2] + bw / 2
    c.line(sx, fy0, sx, fy, C.accent, 1.5)
    c.line(lcx, fy, sx, fy, C.accent, 1.5)
    c.circle(sx, fy, 4, fill=C.accent)
    c.arrow(lcx, fy, lcx, lo_y, C.complete)
    c.arrow(rcx, fy, rcx, lo_y, C.verified)

    oh = 134
    # if redeemed
    c.box(lx, lo_y, lw_, oh, fill=C.white, stroke=C.complete, sw=1.5)
    c.glyph("check", lx + 22, lo_y + 21, C.complete)
    c.text(lx + 38, lo_y + 26, "If redeemed", 13, 700, C.complete)
    c.text_block(lx + 16, lo_y + 50, lw_ - 32,
                 "Purchaser is repaid under the statutory formula. Certificate-holder rights end.", 12)
    c.line(lx + 16, lo_y + oh - 42, lx + lw_ - 16, lo_y + oh - 42, C.rule, 0.75)
    c.text(lx + 16, lo_y + oh - 18, "Ends in repayment and discharge", 12, 700, C.ink)
    # if not redeemed
    c.box(rx, lo_y, rw_, oh, fill=C.white, stroke=C.verified, sw=1.5)
    c.text(rx + 16, lo_y + 26, "If not redeemed", 13, 700, C.verified)
    c.text_block(rx + 16, lo_y + 50, rw_ - 32,
                 "After the applicable wait, purchaser may request and pay for the municipal deed.", 12)
    c.line(rx + 16, lo_y + oh - 42, rx + rw_ - 16, lo_y + oh - 42, C.rule, 0.75)
    c.text(rx + 16, lo_y + oh - 18, "Tax deed if no redemption occurs", 12, 700, C.ink)

    # band
    by2 = H - 44
    c.rect(8, by2, 656, 34, fill=C.paper2)
    c.text(W / 2, by2 + 22,
           "Certificate holder is a legal stage with powers, duties and limits — not ordinary ownership yet.",
           12, 400, C.ink, "middle")
    c.save(OUT / "fig-03-redeemable-route.svg")


# --------------------------------------------------------------------------- non-redeemable route
def nonredeemable_route():
    """REDRAW of figure-08 (labels verbatim); questions in the unresolved style; timing note
    from md:321."""
    W, H = 672, 352
    c = Canvas(W, H, "No redemption period does not mean no uncertainty",
               "Older-arrears route to the deed stage beside four questions that remain.")
    top, bh = 12, 112
    bw, gap = 156, 26
    xs = [8, 8 + bw + gap, 8 + 2 * (bw + gap)]
    heads = [("Older arrears", "Taxes were already in arrears for more than six years at sale", C.municipal),
             ("Statutory exception", "No six-month redemption right under the ordinary route", C.unresolved),
             ("Deed stage", "Purchaser may request and pay for the municipal deed", C.verified)]
    for i, (h, b, col) in enumerate(heads):
        x = xs[i]
        if i == 0:
            c.box(x, top, bw, bh, fill=C.white, stroke=col, tab=col)
            tx = x + 18
        else:
            c.box(x, top, bw, bh, fill=C.white, stroke=col, sw=1.5)
            tx = x + 14
        c.text(tx, top + 26, h, 13, 700, col)
        c.text_block(tx, top + 48, bw - (tx - x) - 10, b, 12)
    for i in range(2):
        c.arrow(xs[i] + bw, top + bh / 2, xs[i + 1], top + bh / 2, C.accent)
    # "immediate deed" shorthand box
    dx = xs[2] + bw + 14
    dw = W - 8 - dx
    c.rect(dx, top, dw, bh, fill=C.municipal, rx=3)
    c.text(dx + dw / 2, top + 30, "“Immediate", 16, 700, C.white, "middle")
    c.text(dx + dw / 2, top + 50, "deed”", 16, 700, C.white, "middle")
    c.text(dx + dw / 2, top + 74, "municipal", 12, 400, C.white, "middle")
    c.text(dx + dw / 2, top + 90, "shorthand", 12, 400, C.white, "middle")

    # timing note
    ny = top + bh + 24
    c.text(W - 8, ny, "Immediate deed describes timing, not readiness.", 12, 700, C.municipal, "end")

    # questions
    qy = ny + 30
    c.text(8, qy, "The deed route changes. These questions do not disappear:", 13, 700, C.ink)
    qtop = qy + 14
    qw = (656 - 3 * 14) / 4
    qh = 96
    qs = [("Possession", "Who is lawfully on site?"),
          ("Access", "What legal rights reach it?"),
          ("Title review", "What property-specific issues remain?"),
          ("Intended use", "Do planning and site facts support it?")]
    for i, (h, q) in enumerate(qs):
        x = 8 + i * (qw + 14)
        c.box(x, qtop, qw, qh, fill=C.white, stroke=C.unresolved, dash=DASH)
        c.glyph("question", x + 20, qtop + 21, C.unresolved)
        c.text(x + 34, qtop + 26, h, 13, 700, C.unresolved)
        c.text_block(x + 14, qtop + 52, qw - 26, q, 12)

    # band
    by = qtop + qh + 18
    c.rect(8, by, 656, 36, fill=C.caution_tint, stroke=C.caution, sw=1.5)
    c.text(W / 2, by + 23,
           "Not instant possession. Not access proof. Not a title opinion. Not development approval.",
           13, 700, C.caution, "middle")
    assert by + 36 <= H - 8, by
    c.save(OUT / "fig-03-nonredeemable-route.svg")


# --------------------------------------------------------------------------- two parcels
def two_parcels_two_endings():
    """NEW. md:331-335, 341 (with 255, 309 for the document names)."""
    W, H = 672, 494
    c = Canvas(W, H, "Two parcels, two endings",
               "Two fictional parcels sold at the same auction end in a discharge and a registered deed.")

    c.text(W - 8, 20, "Composite cases — not real properties", 11, 400, C.granite, "end")

    # start node spanning both lanes
    sx, sw_ = 8, 82
    L1, L2 = 48, 222            # lane tops
    lh1, lh2 = 128, 196
    c.rect(sx, L1, sw_, L2 + lh2 - L1, fill=C.accent, rx=3)
    cy = (L1 + L2 + lh2) / 2
    c.text(sx + sw_ / 2, cy - 20, "One", 13, 700, C.white, "middle")
    c.text(sx + sw_ / 2, cy - 4, "auction", 13, 700, C.white, "middle")
    centred(c, sx + sw_ / 2, cy + 20, sw_ - 14, "Both purchasers pay in full", 12, 400, C.white)

    cols = [108, 250, 392, 534]
    cw = 124
    # lane titles
    c.text(cols[0], L1 - 12, "Harbour Road · marked redeemable", 13, 700, C.verified)
    c.text(cols[0], L2 - 12, "Quarry Lane · older-arrears category", 13, 700, C.municipal)

    def step(x, y, h, head, body, stroke, sw=1.5, dash=None, glyph=None, hcol=None):
        c.box(x, y, cw, h, fill=C.white, stroke=stroke, sw=sw, dash=dash)
        hx = x + 12
        if glyph:
            c.glyph(glyph, x + 18, y + 19, stroke)
            hx = x + 32
        end = c.text_block(hx, y + 24, cw - (hx - x) - 8, head, 13, 700, hcol or stroke)
        c.text_block(x + 12, end + 4, cw - 22, body, 12)

    # lane 1
    l1 = [("Paid in full", "Full payment produces a certificate of sale.", C.accent, None),
          ("Certificate holder", "Six-month redemption right still live.", C.verified, None),
          ("Month 4: redeemed", "Purchaser supplies records for the statutory accounting.",
           C.verified, None),
          ("Discharged", "Repaid through the process; rights in the land end.", C.complete, "check")]
    for i, (h, b, col, g) in enumerate(l1):
        step(cols[i], L1, lh1, h, b, col, glyph=g)
    for i in range(3):
        c.arrow(cols[i] + cw, L1 + lh1 / 2, cols[i + 1], L1 + lh1 / 2, C.accent)
    c.arrow(sx + sw_, L1 + lh1 / 2, cols[0], L1 + lh1 / 2, C.accent)

    # lane 2
    l2 = [("Paid in full", "No normal six-month redemption right.", C.accent, None),
          ("Deed requested", "The purchaser requests the deed and registers it.", C.verified, None),
          ("Deed registered", "The ownership document for that stage.", C.complete, "check")]
    for i, (h, b, col, g) in enumerate(l2):
        step(cols[i], L2, 116, h, b, col, glyph=g)
    for i in range(2):
        c.arrow(cols[i] + cw, L2 + 58, cols[i + 1], L2 + 58, C.accent)
    c.arrow(sx + sw_, L2 + 58, cols[0], L2 + 58, C.accent)
    # unanswered questions
    qx = cols[3]
    c.text(qx, L2 + 8, "It does not answer:", 12, 700, C.unresolved)
    qh = 84
    qa = L2 + 18
    qb = qa + qh + 10
    for y, q in ((qa, "Is the apparent driveway a legal right-of-way?"),
                 (qb, "Does someone occupy a building?")):
        c.box(qx, y, cw, qh, fill=C.white, stroke=C.unresolved, dash=DASH)
        c.glyph("question", qx + 16, y + 18, C.unresolved)
        c.text_block(qx + 12, y + 40, cw - 22, q, 12)
    c.arrow(cols[2] + cw, L2 + 58, qx, qa + qh / 2, C.unresolved, dash=DASH)

    # endings band
    by = L2 + lh2 + 16
    c.rect(8, by, 656, H - 8 - by, fill=C.paper2)
    c.text(20, by + 22, "Harbour Road leaves through discharge: the first purchaser’s rights have ended.",
           12, 400, C.ink)
    c.text(20, by + 40, "Quarry Lane leaves through a registered deed: the second purchaser’s ownership work has begun.",
           12, 400, C.ink)
    c.save(OUT / "fig-03-two-parcels-two-endings.svg")


if __name__ == "__main__":
    redeemable_route()
    nonredeemable_route()
    two_parcels_two_endings()
