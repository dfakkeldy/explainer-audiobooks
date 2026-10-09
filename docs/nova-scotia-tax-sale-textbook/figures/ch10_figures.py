"""Chapter 10 figures (spec: design/figure-style.md; plan: design/chapter-plan.md, Chapter 10).

    .venv/bin/python figures/ch10_figures.py

Every label below is taken from the original figure (figure-30, figure-39), its alt text, or the
manuscript lines the chapter plan cites (md:1173-1185, 1217-1229, 1245-1273);
review/claims/ch10.md maps each one.
"""
from pathlib import Path

from svgkit import C, DASH, Canvas, wrap

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src/assets/figures"


def band(c, y, s, h=34):
    c.rect(8, y, c.w - 16, h, fill=C.accent_tint)
    c.text(c.w / 2, y + h / 2 + 4.5, s, 12, 400, C.ink, "middle")


def step(c, x, y, w, h, head, body, stroke=C.accent, dash=None, head_color=None, glyph=None):
    """Box with a 13/700 heading and a wrapped 12/400 body."""
    c.box(x, y, w, h, fill=C.white, stroke=stroke, dash=dash)
    hx = x + 12
    if glyph:
        c.glyph(glyph, x + 18, y + 19, stroke)
        hx = x + 32
    c.text(hx, y + 23, head, 13, 700, head_color or stroke)
    c.text_block(x + 12, y + 43, w - 24, body, 12)


def body_h(s, w, size=12):
    return len(wrap(s, size, w - 24)) * size * 1.3


# --------------------------------------------------------------------------- figure-30 redraw
def auction_versus_tender():
    """Two lanes ending at one evidence file (figure-30 labels, alt text md:1189)."""
    W, H = 672, 262
    c = Canvas(W, H, "Two formats, one written limit",
               "Open auction and sealed tender lanes both end at the same evidence file.")
    lanes = [("Open auction", ["Register", "Hear live calls", "Card rises only below the limit"]),
             ("Sealed tender", ["Choose once", "Submit by deadline", "No live adjustment"])]
    sw_, sg, x0 = 122, 22, 8
    bh = 58
    ys = [30, 132]
    for (name, steps), y in zip(lanes, ys):
        c.text(x0, y - 10, name, 13, 700, C.accent)
        for i, s in enumerate(steps):
            x = x0 + i * (sw_ + sg)
            c.box(x, y, sw_, bh, fill=C.accent_tint if i == 2 else C.white, stroke=C.accent)
            lines = wrap(s, 12, sw_ - 20, 700 if i == 2 else 400)
            ty = y + bh / 2 - (len(lines) - 1) * 7.8 + 4
            for k, ln in enumerate(lines):
                c.text(x + sw_ / 2, ty + k * 15.6, ln, 12, 700 if i == 2 else 400, C.ink, "middle")
            if i < 2:
                c.arrow(x + sw_, y + bh / 2, x + sw_ + sg, y + bh / 2, C.accent)
    # shared destination
    fx = x0 + 3 * sw_ + 2 * sg + 44
    fw = W - 8 - fx
    fy, fh = ys[0], ys[1] + bh - ys[0]
    c.box(fx, fy, fw, fh, fill=C.white, stroke=C.verified, sw=2.25)
    c.text(fx + 16, fy + 30, "Same evidence file", 13, 700, C.verified)
    c.text_block(fx + 16, fy + 56, fw - 32,
                 "Eligibility, authority, event terms and walk-away rule do not change.", 12)
    c.line(fx + 16, fy + fh - 52, fx + fw - 16, fy + fh - 52, C.rule, 0.75)
    c.text_block(fx + 16, fy + fh - 30, fw - 32, "Same written walk-away rule", 12, 700, C.ink)
    lx = x0 + 3 * sw_ + 2 * sg
    for y in ys:
        c.arrow(lx, y + bh / 2, fx, y + bh / 2, C.accent)
    band(c, H - 44, "Open bidding reveals competitors; a tender hides them, but both reward a "
         "prewritten limit.")
    c.save(OUT / "fig-10-auction-versus-tender.svg")


# --------------------------------------------------------------------------- figure-39 redraw
def payment_readiness_clock():
    """Readiness path and the three break branches (figure-39 labels; md:1217-1229, 1247-1257)."""
    W, H = 672, 308
    c = Canvas(W, H, "Payment readiness extends beyond the hammer",
               "Authorized, funds ready, immediate payment, then three business days; three "
               "branches when the expected path breaks.")
    path = [("Authorized", "Identity, authority and conflict check"),
            ("Funds ready", "Event-accepted forms in hand"),
            ("Immediate", "Price or recovery deposit; Inverness registration amount"),
            ("3 business days", "Any remaining purchase balance")]
    bw, gap, top, bh = 146, 24, 10, 86
    for i, (h, b) in enumerate(path):
        x = 8 + i * (bw + gap)
        step(c, x, top, bw, bh, h, b, stroke=C.accent)
        if i < 3:
            c.arrow(x + bw, top + bh / 2, x + bw + gap, top + bh / 2, C.accent)

    hy = top + bh + 34
    c.text(8, hy, "When the expected path breaks", 13, 700, C.ink)
    c.text(W - 8, hy, "Dashed: a branch, not the expected path", 11, 400, C.ink2, "end")
    breaks = [("No sufficient bid", "Before there is a purchaser",
               "Municipality may buy for the recovery amount — or advertise again for auction "
               "or tender."),
              ("No immediate payment", "Immediately after a high bid",
               "Treasurer puts the land up for sale again immediately."),
              ("Balance missed", "Not paid within 3 business days",
               "Re-advertise and resell; resale expenses come out of the deposit.")]
    bw2, gap2 = 208, 16
    by, bh2 = hy + 12, 104
    for i, (h, when, b) in enumerate(breaks):
        x = 8 + i * (bw2 + gap2)
        c.box(x, by, bw2, bh2, fill=C.white, stroke=C.granite, dash=DASH)
        c.text(x + 12, by + 23, h, 13, 700, C.ink)
        c.text(x + 12, by + 40, when, 11, 400, C.ink2)
        c.text_block(x + 12, by + 62, bw2 - 24, b, 12)
    band(c, H - 42, "The hammer finds a leading bid. Prepared payment completes the sale step.")
    c.save(OUT / "fig-10-payment-readiness-clock.svg")


# --------------------------------------------------------------------------- new state diagram
def sale_state_changes():
    """NEW: states of a listed property at a sale (md:1245-1273)."""
    W = 672
    spine = [("Advertised", "Before the event"),
             ("Called", "During the event"),
             ("Leading offer", "Highest acceptable bid"),
             ("Immediate amount paid", "Price or recovery amount"),
             ("Balance paid", "Within 3 business days"),
             ("Certificate of sale", "Redeemable branch")]
    branches = [
        ("Withdrawn", "Paid, removed or otherwise changed. Check the current municipal source; "
         "research cannot turn it into a private offer."),
        ("No sufficient bid", "Treasurer may buy for the municipality, or the municipality may "
         "advertise again and later sell at auction or by highest tender, subject to any "
         "acceptable minimum directed by council. Unsold is not privately available (CBRM "
         "legend: only at a future tax sale)."),
        ("Immediate payment fails", "Land is put up for sale again at once. The next person "
         "does not automatically inherit the winning amount."),
        ("Balance not paid", "Land is re-advertised and sold. Resale expenses are deducted from "
         "the deposit; the remainder is refunded after the resale."),
        None, None]
    sides = [("Tender", "The accepted tenderer has three business days after notification to "
              "pay. Failure sends the land back toward advertisement and sale."),
             ("Schedule change", "An old advertisement cannot prove the changed event. Return to "
              "the municipal page and current notice.")]
    sx, sw_, sh = 8, 206, 46
    bx = 262
    bw = W - 8 - bx
    gap = 14
    heights = [max(sh, 40 + body_h(b[1], bw)) if b else sh for b in branches]
    hw = (bw - 14) / 2
    sides_h = 40 + max(body_h(b, hw) for _, b in sides)
    # rows 5-6 hold the side boxes in the right column
    ys, y = [], 10
    for i, hgt in enumerate(heights):
        ys.append(y)
        y += hgt + gap
    side_y = ys[4]
    H = max(y - gap, side_y + sides_h) + 10
    c = Canvas(W, int(H), "What can happen to a listed property at a sale",
               "A spine of states from advertised to certificate of sale, with a dashed branch "
               "at each point where the expected sale can stop.")
    centres = []
    for i, ((name, sub), hgt, y) in enumerate(zip(spine, heights, ys)):
        sy = y + (hgt - sh) / 2
        last = i == 5
        col = C.complete if last else C.accent
        c.box(sx, sy, sw_, sh, fill=C.white if last else C.accent_tint, stroke=col,
              sw=2.25 if last else 1.5)
        tx = sx + 12
        if last:
            c.glyph("check", sx + 17, sy + 17, C.complete)
            tx = sx + 30
        c.text(tx, sy + 21, name, 13, 700, C.complete if last else C.ink)
        c.text(sx + 12, sy + 37, sub, 11, 400, C.ink2)
        centres.append((sy, sh))
        if branches[i]:
            h, b = branches[i]
            c.box(bx, y, bw, hgt, fill=C.white, stroke=C.granite, dash=DASH)
            c.text(bx + 12, y + 21, h, 13, 700, C.ink)
            c.text_block(bx + 12, y + 39, bw - 24, b, 12)
            c.arrow(sx + sw_, sy + sh / 2, bx, sy + sh / 2, C.granite, dash=DASH)
    for i in range(5):
        (ay, ah), (by_, _) = centres[i], centres[i + 1]
        c.arrow(sx + sw_ / 2, ay + ah, sx + sw_ / 2, by_, C.accent)
    for k, (h, b) in enumerate(sides):
        x = bx + k * (hw + 14)
        c.box(x, side_y, hw, sides_h, fill=C.white, stroke=C.granite, dash=DASH)
        c.text(x + 12, side_y + 21, h, 13, 700, C.ink)
        c.text_block(x + 12, side_y + 39, hw - 24, b, 12)
    c.save(OUT / "fig-10-sale-state-changes.svg")


if __name__ == "__main__":
    auction_versus_tender()
    payment_readiness_clock()
    sale_state_changes()
