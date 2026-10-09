"""Chapter 9 figures (spec: design/figure-style.md; plan: design/chapter-plan.md, Chapter 9).

    .venv/bin/python figures/ch09_figures.py

Every label below is taken from the original figure (figure-26, -27, -28, -29), its alt text, or
the manuscript lines the chapter plan cites (md:1051-1163); review/claims/ch09.md maps each one.
Bar lengths in fig-09-fifty-thirtyfive-thirtyone, fig-09-inverness-ratio-distribution and panel a
of fig-09-build-backward are proportional to the printed counts and amounts; the cost stack and
panel b of the build-backward figure are not to scale and say so.
"""
from pathlib import Path

from svgkit import C, DASH, Canvas

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src/assets/figures"


def hatch(c, x, y, w, h, color, step=7):
    """Diagonal hatch clipped to a rectangle (drawn as short segments, no clipPath needed)."""
    segs = []
    k = -h
    while k < w:
        # line from (x+k, y+h) to (x+k+h, y), clipped to the box
        ax, ay = x + k, y + h
        bx, by = x + k + h, y
        if ax < x:
            ay -= (x - ax)
            ax = x
        if bx > x + w:
            by += (bx - (x + w))
            bx = x + w
        if ay > by:
            segs.append(f"M{ax:.1f},{ay:.1f} L{bx:.1f},{by:.1f}")
        k += step
    c.path(" ".join(segs), stroke=color, sw=0.75)


def bottom_line(c, y, text, w=672):
    c.line(16, y - 18, w - 16, y - 18, C.rule, 0.75)
    c.text(16, y, text, 12, 400, C.ink2)


# ------------------------------------------------------------------ figure-27 redraw
def fifty_thirtyfive_thirtyone():
    c = Canvas(672, 300, "Do not collapse three official counts",
               "Inverness County, May 2025: 50 advertised, 35 reported sold, 15 removed, "
               "31 published result rows, 4-row gap unresolved.")
    x0, unit, bh = 16, 12.8, 38
    c.text(x0, 22, "Inverness County, May 2025 sale · bar lengths proportional to the counts",
           11, 400, C.ink2)

    # row 1: advertised
    y1 = 34
    c.rect(x0, y1, 50 * unit, bh, fill=C.municipal)
    c.text(x0 + 12, y1 + 26, "50", 18, 700, C.white)
    c.text(x0 + 44, y1 + 24, "advertised properties", 12, 400, C.white)

    # row 2: sold + removed
    y2 = 112
    w35, w15 = 35 * unit, 15 * unit
    c.line(x0 + 1, y1 + bh, x0 + 1, y2, C.accent, 1.5)
    c.line(x0 + 50 * unit - 1, y1 + bh, x0 + 50 * unit - 1, y2, C.granite, 1.5)
    c.rect(x0, y2, w35, bh, fill=C.accent)
    c.text(x0 + 12, y2 + 26, "35", 18, 700, C.white)
    c.text(x0 + 44, y2 + 24, "reported sold in council minutes", 12, 400, C.white)
    c.rect(x0 + w35 + 3, y2, w15 - 3, bh, fill=C.paper2, stroke=C.granite, sw=1.5)
    c.text(x0 + w35 + 15, y2 + 26, "15", 18, 700, C.ink)
    c.text(x0 + w35 + 47, y2 + 24, "removed before sale", 12, 400, C.ink)
    c.text(x0 + w35 + 15, y2 + bh + 16, "after collection or legal advice", 11, 400, C.ink2)

    # row 3: published rows + gap
    y3 = 206
    w31, w4 = 31 * unit, 4 * unit
    c.line(x0 + 1, y2 + bh, x0 + 1, y3, C.accent, 1.5)
    c.line(x0 + w35 - 1, y2 + bh, x0 + w35 - 1, y3, C.accent, 1.5)
    c.rect(x0, y3, w31, bh, fill=C.accent_tint, stroke=C.accent, sw=1.5)
    c.text(x0 + 12, y3 + 26, "31", 18, 700, C.ink)
    c.text(x0 + 44, y3 + 24, "published result rows", 12, 400, C.ink)
    gx = x0 + w31 + 3
    hatch(c, gx, y3, w4 - 3, bh, C.unresolved)
    c.rect(gx, y3, w4 - 3, bh, fill="none", stroke=C.unresolved, sw=1.5, dash=DASH)
    c.rect(gx + 12, y3 + 8, 22, 22, fill=C.white)
    c.text(gx + (w4 - 3) / 2, y3 + 26, "4", 18, 700, C.unresolved, anchor="middle")
    c.glyph("question", gx + w4 + 12, y3 + 19, C.unresolved)
    c.text(gx + w4 + 26, y3 + 17, "sold-row gap left unresolved", 12, 700, C.unresolved)
    c.text(gx + w4 + 26, y3 + 32, "minutes 35 vs result sheet 31", 11, 400, C.ink2)

    bottom_line(c, 286, "Advertised, sold and published-result counts answer different questions.")
    c.save(OUT / "fig-09-fifty-thirtyfive-thirtyone.svg")


# ------------------------------------------------------------------ figure-26 redraw
def inverness_ratio_distribution():
    c = Canvas(672, 340, "Thirty-one published rows, bounded",
               "Inverness May 2025 published rows by bid as a multiple of the recovery amount: "
               "7 under 2x, 9 from 2x to under 5x, 8 from 5x to under 10x, 7 at 10x or more.")
    bands = [("under 2×", 7, C.white), ("2× to under 5×", 9, C.accent_tint),
             ("5× to under 10×", 8, C.accent_mid), ("10× or more", 7, C.accent)]
    x0, cell, gap, bh = 16, 18, 2, 34
    slot = cell + gap            # 31 cells, 3 extra band gaps
    bandgap = 10
    y = 112
    c.text(x0, 22, "Inverness County, May 2025 · winning bid ÷ advertised recovery amount",
           11, 400, C.ink2)
    c.text(x0, 40, "One block = one published row, grouped by band", 11, 400, C.ink2)

    # cumulative brackets above the bar: at least 2x / 5x / 10x
    x = x0
    starts = []
    for _, n, _ in bands:
        starts.append(x)
        x += n * slot + bandgap
    end = x - bandgap - gap
    brackets = [("24 at least twice the recovery amount", starts[1], 58),
                ("15 at least five times", starts[2], 76),
                ("7 at least ten times", starts[3], 94)]
    for label, bx, by in brackets:
        c.path(f"M{bx},{by + 8} L{bx},{by} L{end},{by} L{end},{by + 8}", stroke=C.accent, sw=1.25)
        c.text(bx + 6, by - 3, label, 11, 400, C.ink)

    # the blocks
    for i, (label, n, fill) in enumerate(bands):
        sx = starts[i]
        for k in range(n):
            c.rect(sx + k * slot, y, cell, bh, fill=fill,
                   stroke=C.accent if fill != C.accent else C.accent, sw=1)
        w = n * slot - gap
        c.text(sx + w / 2, y + bh + 22, str(n), 18, 700, C.ink, anchor="middle")
        c.text(sx + w / 2, y + bh + 40, label, 12, 700, C.ink, anchor="middle")

    # summary line
    sy = 232
    c.text(x0, sy, "31 published rows · median 4.53× · range 1.00× to 21.62×", 13, 700, C.ink)
    c.text(x0, sy + 20, "31 published rows of 35 reported sales; the recovery amount is not value.",
           12, 400, C.ink)
    c.text(x0, sy + 38, "Threshold grouping uses exact reported counts; blocks do not represent "
           "exact row positions.", 11, 400, C.ink2)

    bottom_line(c, 324, "In the 31 published rows, competition often carried bids above the "
                "recovery amount.")
    c.save(OUT / "fig-09-inverness-ratio-distribution.svg")


# ------------------------------------------------------------------ figure-28 redraw
def municipal_result_comparison():
    c = Canvas(672, 362, "Definitions travel with the numbers",
               "Three dated municipal result sets, each with its row count, ratio denominator "
               "and completeness limit.")
    panels = [
        ("Inverness 2025", "May 2025 public result sheet",
         [("Rows", "31 published rows; 35 reported sold"),
          ("Denominator", "advertised recovery amount"),
          ("Median", "bid/recovery 4.53×"),
          ("Range", "approximately the recovery amount to more than 21×"),
          ("Limit", "4-row gap left unresolved")]),
        ("CBRM March 2026", "official result sheet",
         [("Rows", "24 recorded sales with both a minimum and a winning bid"),
          ("Denominator", "minimum bid"),
          ("Median", "winning/minimum 3.17×"),
          ("Range", "exactly the minimum to more than 42×"),
          ("Spread", "8 at the minimum; 9 at 5× or more")]),
        ("Richmond June 2026", "published table",
         [("Rows", "3 sold rows"),
          ("Denominator", "listed taxes, interest and charges"),
          ("Ratios", "about 1.33×, 6.59× and 6.28×"),
          ("Limit", "far too few to support a municipal price rule")]),
    ]
    pw, gx, top, ph = 208, 16, 10, 300
    for i, (head, src, rows) in enumerate(panels):
        x = 8 + i * (pw + gx)
        c.box(x, top, pw, ph, fill=C.white, stroke=C.municipal, sw=1.5, tab=C.municipal)
        tx, tw = x + 18, pw - 28
        c.text(tx, top + 26, head, 13, 700, C.municipal)
        c.text(tx, top + 44, src, 11, 400, C.ink2)
        yy = top + 72
        for lab, val in rows:
            c.text(tx, yy, lab, 11, 700, C.ink2)
            yy = c.text_block(tx, yy + 16, tw, val, 12, 400, C.ink) + 8
    bottom_line(c, 348, "Cross-municipal numbers are useful only when procedure, sample and "
                "denominator travel with them.")
    c.save(OUT / "fig-09-municipal-result-comparison.svg")


# ------------------------------------------------------------------ figure-29 redraw
def all_in_cost_stack():
    layers = [
        ("Bid", "The amount called or tendered."),
        ("Tax", "Applicable tax and deed-transfer questions."),
        ("Legal + registry", "Advice, searches and registration."),
        ("Survey", "Boundary and access work when needed."),
        ("Insurance", "Coverage attempts and conditions."),
        ("Carrying", "New taxes, security and time."),
        ("Repair / remediation", "Unknown until appropriately investigated."),
        ("Possession", "A separate lawful process if occupied."),
        ("Uncertainty reserve", "A buffer, not hidden optimism."),
    ]
    c = Canvas(672, 470, "The bid is only the first layer",
               "The bid sits above a waterline; tax, legal and registry, survey, insurance, "
               "carrying, repair and remediation, possession and the uncertainty reserve sit "
               "below it.")
    x, w, lh, g = 16, 420, 34, 4
    y = 30
    wl = None
    for i, (head, body) in enumerate(layers):
        if i == 1:
            wl = y + 8
            y += 22
        fill = C.accent_tint if i == 0 else C.white
        c.box(x, y, w, lh, fill=fill, stroke=C.accent, sw=1.5)
        c.text(x + 12, y + 22, head, 13, 700, C.accent)
        c.text(x + 168, y + 22, body, 12, 400, C.ink)
        y += lh + g
    # waterline across the stack
    c.path(f"M8,{wl} " + " ".join(
        f"Q{12 + k * 24},{wl - 4} {20 + k * 24},{wl} T{32 + k * 24},{wl}" for k in range(19)),
        stroke=C.accent_mid, sw=1.5)
    # right-hand annotations
    ax = 456
    c.text(ax, 44, "Visible: the winning bid", 12, 700, C.ink)
    c.text_block(ax, 60, 200, "the visible tip", 11, 400, C.ink2)
    c.path(f"M{ax - 8},{wl + 22} L{ax - 8},{y - g}", stroke=C.accent, sw=1.5)
    c.text(ax, wl + 36, "Below the surface", 12, 700, C.ink)
    ny = c.text_block(ax, wl + 54, 200, "Known costs should be researched and estimated, not "
                      "treated as a mysterious mass.", 12, 400, C.ink)
    c.text_block(ax, ny + 10, 200, "Not to scale: the submerged proportion is not fixed.",
                 11, 400, C.ink2)
    bottom_line(c, y + 30, "The winning bid is one layer in the acquisition's uncertainty budget.")
    c.h = int(y + 42)
    c.save(OUT / "fig-09-all-in-cost-stack.svg")


# ------------------------------------------------------------------ new: build backward
def build_backward():
    c = Canvas(672, 420, "Exposure and the maximum, kept apart",
               "Panel a: $30,000 bid + $40,000 known non-bid costs + $20,000 uncertainty reserve "
               "= $90,000 all-in exposure. Panel b: supported value boundary minus known "
               "non-bid costs and reserve leaves what can become the maximum bid.")
    x0 = 16
    # panel a
    c.text(x0, 24, "a  All-in exposure (worked example, fictional file)", 13, 700, C.accent)
    unit = 640 / 90000
    segs = [("$30,000", "bid", 30000, C.accent, C.white),
            ("$40,000", "known non-bid costs", 40000, C.accent_mid, C.ink),
            ("$20,000", "uncertainty reserve", 20000, C.white, C.ink)]
    x, y, bh = x0, 40, 40
    for amt, lab, v, fill, tc in segs:
        w = v * unit
        dash = DASH if lab == "uncertainty reserve" else None
        c.rect(x, y, w - 3, bh, fill=fill, stroke=C.accent, sw=1.5, dash=dash)
        c.text(x + 10, y + 18, amt, 13, 700, tc)
        c.text(x + 10, y + 33, lab, 12, 400, tc)
        x += w
    c.path(f"M{x0},{y + bh + 8} L{x0},{y + bh + 14} L{x0 + 637},{y + bh + 14} "
           f"L{x0 + 637},{y + bh + 8}", stroke=C.ink, sw=1.25)
    c.text(x0 + 320, y + bh + 32, "$90,000 all-in exposure", 13, 700, C.ink, anchor="middle")
    c.text(x0 + 320, y + bh + 48, "Keep the structure, not the total: bid, known costs, reserve.",
           11, 400, C.ink2, anchor="middle")

    c.line(x0, 158, 672 - x0, 158, C.rule, 0.75)

    # panel b
    c.text(x0, 184, "b  The maximum, built backward (no amounts; not to scale)", 13, 700, C.accent)
    y = 198
    c.rect(x0, y, 640, bh, fill=C.white, stroke=C.verified, sw=1.5)
    c.text(x0 + 10, y + 18, "Supported value boundary", 13, 700, C.verified)
    c.text(x0 + 10, y + 33, "highest all-in amount defensible for the stated use, from "
           "property-specific valuation evidence", 11, 400, C.ink)
    y2 = y + bh + 30
    c.arrow(x0 + 320, y + bh + 4, x0 + 320, y2 - 2, C.accent)
    c.text(x0 + 330, y + bh + 20, "subtract from the right", 11, 400, C.ink2)
    wr, wk, wu = 240, 240, 160
    c.rect(x0, y2, wr - 3, bh, fill=C.accent_tint, stroke=C.accent, sw=2.25)
    c.text(x0 + 10, y2 + 18, "What remains", 13, 700, C.accent)
    c.text(x0 + 10, y2 + 33, "can become the maximum bid", 12, 400, C.ink)
    c.rect(x0 + wr, y2, wk - 3, bh, fill=C.accent_mid, stroke=C.accent, sw=1.5)
    c.text(x0 + wr + 10, y2 + 18, "Known non-bid costs", 13, 700, C.ink)
    c.rect(x0 + wr + wk, y2, wu - 3, bh, fill=C.white, stroke=C.accent, sw=1.5, dash=DASH)
    c.text(x0 + wr + wk + 10, y2 + 18, "Uncertainty reserve", 13, 700, C.ink)

    y3 = y2 + bh + 26
    c.glyph("check", x0 + 8, y3 - 4, C.complete)
    c.text_block(x0 + 22, y3, 600, "Only if every essential legal, eligibility, payment and "
                 "no-go condition is satisfied, and the amount is fundable.", 12, 400, C.ink)
    y4 = y3 + 44
    c.rect(x0, y4 - 22, 640, 34, fill=C.caution_tint, stroke=C.nogo, sw=3)
    c.glyph("bar", x0 + 18, y4 - 5, C.nogo)
    c.text(x0 + 34, y4, "If costs and reserve consume the whole boundary, nothing remains: "
           "a no-bid result.", 12, 700, C.ink)
    c.h = y4 + 24
    c.save(OUT / "fig-09-build-backward.svg")


# ------------------------------------------------------------------ new: tax branches
def tax_eligibility_branches():
    c = Canvas(672, 470, "Four branches before the ceiling",
               "Four tax and eligibility questions, each with its dated fact, as of July 2026.")
    branches = [
        ("1  Municipal deed transfer tax",
         "Does the municipal tax-sale-deed exemption apply to this deed?",
         "The Municipal Government Act exempts a deed given pursuant to a tax sale from "
         "municipal deed transfer tax. Registration charges, HST, the provincial non-resident "
         "tax, income-tax consequences and advice remain."),
        ("2  Provincial non-resident tax",
         "Could the provincial non-resident tax apply to this buyer and property?",
         "For qualifying transfers after March 2025: a 10% rate based on the non-resident "
         "interest and the higher of purchase price or assessed value, subject to definitions "
         "and exemptions (one concerns moving to Nova Scotia within six months)."),
        ("3  HST",
         "What is the HST treatment of this particular transaction?",
         "CBRM's current event instructions: HST applies to vacant land and commercially "
         "assessed property. That is a CBRM rule, not a universal one. Canada Revenue Agency "
         "guidance: treatment can depend on the seller, prior use, property, transaction and "
         "purchaser's registration status."),
        ("4  Eligibility",
         "Is the buyer eligible under current federal, provincial, and municipal law?",
         "Eligibility comes before price. The federal prohibition on certain purchases of "
         "residential property by non-Canadians is currently scheduled through January 1, 2027."),
    ]
    bw, bh, gx, gy = 320, 186, 16, 14
    for i, (head, q, fact) in enumerate(branches):
        x = 8 + (i % 2) * (bw + gx)
        y = 10 + (i // 2) * (bh + gy)
        c.box(x, y, bw, bh, fill=C.white, stroke=C.unresolved, sw=1.5, dash=DASH)
        c.text(x + 12, y + 24, head, 13, 700, C.unresolved)
        c.glyph("question", x + bw - 18, y + 19, C.unresolved)
        ny = c.text_block(x + 12, y + 46, bw - 24, q, 12, 700, C.ink)
        c.line(x + 12, ny - 6, x + bw - 12, ny - 6, C.rule, 0.75)
        c.text_block(x + 12, ny + 12, bw - 24, fact, 12, 400, C.ink)
    fy = 10 + 2 * (bh + gy) + 6
    c.rect(8, fy, 656, 46, fill=C.accent_tint)
    c.text(20, fy + 19, "An unanswered branch does not automatically mean no bid.", 12, 700, C.ink)
    c.text(20, fy + 36, "The file is not ready until the effect is confirmed, bounded, or treated "
           "as a stop condition.", 12, 400, C.ink)
    c.h = fy + 56
    c.save(OUT / "fig-09-tax-eligibility-branches.svg")


if __name__ == "__main__":
    fifty_thirtyfive_thirtyone()
    inverness_ratio_distribution()
    municipal_result_comparison()
    all_in_cost_stack()
    build_backward()
    tax_eligibility_branches()
