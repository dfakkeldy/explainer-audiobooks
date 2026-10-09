"""Chapter 12 figures (spec: design/figure-style.md; plan: design/chapter-plan.md, Chapter 12).

    .venv/bin/python figures/ch12_figures.py

Every label below is taken from the original figure (figure-32, figure-40), its alt text, or the
manuscript lines the chapter plan cites (md:1377, 1391-1393, 1461, 1471-1477);
review/claims/ch12.md maps each one.
"""
from pathlib import Path

from svgkit import C, DASH, Canvas, wrap

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src/assets/figures"


def band(c, y, s, h=34, bold=False):
    c.rect(8, y, c.w - 16, h, fill=C.accent_tint)
    c.text(c.w / 2, y + h / 2 + 4.5, s, 12, 700 if bold else 400, C.ink, "middle")


def card(c, x, y, w, h, head, body, stroke=C.accent, dash=None, fill=C.white, head_color=None,
         centre=False):
    """Box with a 13/700 heading and a wrapped 12/400 body."""
    c.box(x, y, w, h, fill=fill, stroke=stroke, dash=dash)
    if centre:
        c.text(x + w / 2, y + 24, head, 13, 700, head_color or stroke, "middle")
        lines = wrap(body, 12, w - 28)
        for i, ln in enumerate(lines):
            c.text(x + w / 2, y + 46 + i * 15.6, ln, 12, 400, C.ink, "middle")
    else:
        c.text(x + 12, y + 23, head, 13, 700, head_color or stroke)
        c.text_block(x + 12, y + 43, w - 24, body, 12)


# --------------------------------------------------------------------------- NEW
def three_clocks():
    """Two anchors, three clocks (md:1377, 1391-1393, 1471-1473, 1477). Not to scale."""
    W, H = 672, 432
    c = Canvas(W, H, "Three clocks, two starting points",
               "The redemption period and the 20-year surplus limit are counted from the sale date; the "
               "six-year Marketable Titles Act period runs from deed registration.")
    x_sale, x_red_end, x_end = 40, 170, 652

    # ---- row 1: from the sale date
    c.text(8, 20, "Clocks that start on the sale date", 13, 700, C.accent)
    c.line(x_sale, 30, x_sale, 182, C.ink, 2.25)
    c.text(x_sale + 6, 42, "Sale date", 12, 700, C.ink)
    y1 = 52
    c.rect(x_sale, y1, x_red_end - x_sale, 28, fill=C.accent, stroke=C.accent)
    c.text((x_sale + x_red_end) / 2, y1 + 18.5, "Six months", 12, 700, C.white, "middle")
    c.text(x_red_end + 12, y1 + 12, "Redemption period (redeemable property)", 12, 700, C.ink)
    c.text(x_red_end + 12, y1 + 27, "If unredeemed, the purchaser may request the deed after "
           "six months.", 12)
    y1b = y1 + 40
    c.rect(x_sale, y1b, x_red_end - x_sale, 28, fill=C.white, stroke=C.ink2, dash=DASH)
    c.text((x_sale + x_red_end) / 2, y1b + 18.5, "No six-month period", 12, 400, C.ink,
           "middle")
    c.text(x_red_end + 12, y1b + 12, "Older-arrears route (taxes unpaid for more than six "
           "years at sale)", 12, 700, C.ink)
    c.text(x_red_end + 12, y1b + 27, "The purchaser may request the deed after the sale.", 12)

    y2 = 140
    bx = x_end - 26
    c.rect(x_red_end, y2, bx - x_red_end, 28, fill=C.accent_tint, stroke=C.accent)
    c.path(f"M{bx + 2},{y2 - 5} L{bx + 9},{y2 + 33}", stroke=C.ink2, sw=1.5)
    c.path(f"M{bx + 10},{y2 - 5} L{bx + 17},{y2 + 33}", stroke=C.ink2, sw=1.5)
    c.line(x_end, y2 - 6, x_end, y2 + 34, C.ink, 2.25)
    c.text(x_red_end + 12, y2 + 18.5, "Surplus window: application to the Supreme Court", 12, 700, C.ink)
    c.text_block(x_red_end, y2 + 46, 300, "A person claiming an interest may apply after the "
                 "redemption period.", 12)
    c.text(x_end, y2 + 46, "Closes: 20 years from the sale", 12, 700, C.ink, "end")

    c.line(8, 214, W - 8, 214, C.rule, 0.75)

    # ---- row 2: from the deed-registration date
    c.text(8, 238, "The clock that starts on deed registration", 13, 700, C.accent)
    x_reg, x_six = 212, 452
    c.line(x_reg, 250, x_reg, 316, C.ink, 2.25)
    c.text(x_reg + 6, 262, "Deed-registration date", 12, 700, C.ink)
    y3 = 272
    c.rect(x_reg, y3, x_six - x_reg, 28, fill=C.accent, stroke=C.accent)
    c.text((x_reg + x_six) / 2, y3 + 18.5, "Six years (Marketable Titles Act)", 12, 700,
           C.white, "middle")
    c.line(x_six, y3 - 6, x_six, y3 + 34, C.ink, 2.25)
    c.text(x_reg + 6, y3 + 46, "A tax deed generally may be set aside only in this period.", 12)
    c.text_block(x_six + 12, y3 + 4, W - 8 - x_six - 12,
                 "After it: strong binding and conclusive effect, subject to:", 12, 700)
    bx0, by0 = x_reg, 336
    bw, bh = W - 8 - x_reg, 68
    c.box(bx0, by0, bw, bh, fill=C.white, stroke=C.accent)
    items = ["the land-exclusion rule, where its statutory conditions are met",
             "the current owner's fraud or breach of trust",
             "a preserved damages claim for wrongful tax sale"]
    for i, s_ in enumerate(items):
        yy = by0 + 22 + i * 17
        c.circle(bx0 + 14, yy - 4, 2.5, fill=C.accent)
        c.text(bx0 + 24, yy, s_, 12)
    c.arrow(W - 60, y3 + 38, W - 60, by0, C.accent)

    nx, ny, nw, nh = 8, 254, 186, 100
    c.box(nx, ny, nw, nh, fill=C.paper2, stroke=C.granite, sw=1)
    c.text_block(nx + 12, ny + 24, nw - 24,
                 "Not auction day, not the end of redemption, not deed delivery, not first "
                 "entry: the six years start at registration.", 12, 700)
    c.text(8, H - 14, "Not to scale", 11, 400,
           C.ink2)
    c.save(OUT / "fig-12-three-clocks.svg")


# --------------------------------------------------------------------------- figure-32 redraw
def deed_is_a_beginning():
    """Tax deed at the centre, six arrows to six workstreams (figure-32 labels and alt)."""
    W, H = 672, 330
    c = Canvas(W, H, "A deed moves the questions",
               "Tax deed at the centre sends arrows to six workstreams.")
    streams = [("Title review", "Lawyer"), ("Possession", "Lawful process"),
               ("Planning", "Written municipal answers"), ("Survey", "Boundary and access"),
               ("Condition", "Inspection and environmental review"),
               ("Insurance", "Actual underwriting")]
    bw, bh = 196, 68
    ys = [12, 104, 196]
    cx0, cy0, cw, ch = 256, 112, 160, 88
    c.box(cx0, cy0, cw, ch, fill=C.accent, stroke=C.accent)
    c.text(cx0 + cw / 2, cy0 + 50, "Tax deed", 18, 700, C.white, "middle")
    for i, (head, body) in enumerate(streams):
        left = i % 2 == 0
        row = i // 2
        x = 8 if left else W - 8 - bw
        y = ys[row]
        card(c, x, y, bw, bh, head, body)
        # arrow from the centre box edge to the card edge
        sx = cx0 if left else cx0 + cw
        sy = cy0 + ch / 2 + (row - 1) * 26
        tx = x + bw if left else x
        ty = y + bh / 2
        c.arrow(sx, sy, tx, ty, C.accent)
    band(c, H - 48, "A tax deed changes the file's legal stage; it does not finish the property "
         "work.", h=40)
    c.save(OUT / "fig-12-deed-is-a-beginning.svg")


# --------------------------------------------------------------------------- figure-40 redraw
def surplus_proceeds_route():
    """Proceeds route with two branches (figure-40 labels; md:1461, 1471, 1337)."""
    W, H = 672, 300
    c = Canvas(W, H, "Surplus follows a statutory route",
               "Purchase money, statutory applications, balance to the surplus account, then "
               "two branches.")
    bw, bh, gap = 200, 76, 28
    y = 12
    top = [("Purchase money", "Amount received at the tax sale"),
           ("Statutory applications", "Taxes, interest, sale expenses and specified municipal "
            "amounts"),
           ("Balance to surplus", "Held in the tax-sale surplus account")]
    for i, (h, b) in enumerate(top):
        x = 8 + i * (bw + gap)
        card(c, x, y, bw, bh, h, b)
        if i < 2:
            c.arrow(x + bw, y + bh / 2, x + bw + gap, y + bh / 2, C.accent)
    # branch connector from the surplus box
    sx = 8 + 2 * (bw + gap) + bw / 2
    jy = y + bh + 26
    c.line(sx, y + bh, sx, jy, C.accent)
    lw, lh = 300, 82
    lx, rx = 8, W - 8 - lw
    ly = jy + 24
    c.line(lx + lw / 2, jy, sx, jy, C.accent)
    c.arrow(lx + lw / 2, jy, lx + lw / 2, ly, C.accent)
    c.arrow(rx + lw / 2, jy, rx + lw / 2, ly, C.accent)
    card(c, lx, ly, lw, lh, "If redeemed",
         "The balance reduces the redemption amount under the statutory formula.",
         fill=C.accent_tint, centre=True, head_color=C.accent)
    card(c, rx, ly, lw, lh, "After redemption expires",
         "A prior interest holder may apply to Supreme Court for a proportional payment "
         "before 20 years pass.", fill=C.accent_tint, centre=True, head_color=C.accent)
    band(c, H - 48, "No automatic payout · no purchaser windfall · court route and deadlines "
         "matter", h=40, bold=True)
    c.save(OUT / "fig-12-surplus-proceeds-route.svg")


if __name__ == "__main__":
    three_clocks()
    deed_is_a_beginning()
    surplus_proceeds_route()
