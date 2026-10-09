"""Chapter 11 figures (spec: design/figure-style.md; plan: design/chapter-plan.md, Chapter 11).

    .venv/bin/python figures/ch11_figures.py

Every label below is taken from the original figure (figure-31), its alt text, or the manuscript
lines the chapter plan cites (md:1295-1303, 1315-1321, 1335-1357); review/claims/ch11.md maps
each one.
"""
from pathlib import Path

from svgkit import C, DASH, Canvas, wrap

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src/assets/figures"


def band(c, y, s, h=34, fill=C.accent_tint, weight=400):
    c.rect(8, y, c.w - 16, h, fill=fill)
    lines = wrap(s, 12, c.w - 48, weight)
    y0 = y + h / 2 + 4.5 - (len(lines) - 1) * 7.8
    for i, ln in enumerate(lines):
        c.text(c.w / 2, y0 + i * 15.6, ln, 12, weight, C.ink, "middle")


def tag(c, x, y, s, color, dash=None):
    """Small outlined tag (11/400) with its text in ink."""
    from svgkit import width
    w = width(s, 11) + 14
    c.rect(x, y, w, 18, fill=C.white, stroke=color, sw=1.2, dash=dash, rx=2)
    c.text(x + 7, y + 12.5, s, 11, 400, C.ink2)
    return x + w + 6


# --------------------------------------------------------------------------- figure-31 redraw
def certificate_holder_calendar():
    W, H = 672, 322
    c = Canvas(W, H, "The certificate-holder months are active",
               "Six month cards with recurring tasks; month 6 is unresolved.")
    months = [
        ("Month 1", "Register certificate; organize evidence and insurance attempts.",
         ["record-keeping", "insurance"]),
        ("Month 2", "Track new taxes, notices and protective-work records.",
         ["new-tax marker"]),
        ("Month 3", "Maintain lawful protection; preserve every receipt.",
         ["protective-work limit"]),
        ("Month 4", "Refresh status and keep the redemption route open.", ["record-keeping"]),
        ("Month 5", "Prepare questions without assuming the outcome.", ["record-keeping"]),
        ("Month 6", "Redemption may close the file; otherwise deed work begins.",
         ["possible redemption event"]),
    ]
    cw, gx, ch, gy = 208, 16, 118, 14
    x0, y0 = 8, 10
    for i, (head, body, tags) in enumerate(months):
        col, row = i % 3, i // 3
        x, y = x0 + col * (cw + gx), y0 + row * (ch + gy)
        last = i == 5
        if last:
            c.box(x, y, cw, ch, fill=C.white, stroke=C.unresolved, dash=DASH)
            c.glyph("question", x + cw - 20, y + 20, C.unresolved)
            hc = C.unresolved
        else:
            c.box(x, y, cw, ch, fill=C.white, stroke=C.accent)
            c.rect(x, y, cw, 5, fill=C.accent)
            hc = C.accent
        c.text(x + 12, y + 28, head, 13, 700, hc)
        c.text_block(x + 12, y + 48, cw - 24, body, 12)
        tx = x + 12
        for t in tags:
            tx = tag(c, tx, y + ch - 28, t, C.unresolved if last else C.accent_mid,
                     dash=DASH if last else None)
    band(c, H - 48, "The certificate-holder months are an operations period, not dead time.",
         h=40, weight=700)
    c.save(OUT / "fig-11-certificate-holder-calendar.svg")


# --------------------------------------------------------------------------- new: repair chain
def approved_repair_chain():
    W, H = 672, 384
    c = Canvas(W, H, "The chain behind a reimbursable repair",
               "Five links from observed risk to a documented, paid, approved repair.")
    c.text(8, 22, "Composite case: the fictional Cedar Street file", 12, 700, C.ink)
    c.text(W - 8, 22, "Not a real property", 11, 400, C.granite, "end")
    links = [
        ("1 Observed risk", "A qualified exterior assessment finds a loose roof covering.", None),
        ("2 Defined scope", "Maya sends the treasurer a defined scope, supporting assessment and cost.",
         None),
        ("3 Written approval", "The treasurer approves that scope in writing.", C.municipal),
        ("4 Lawful work", "The contractor does only that scope, through lawful and safe access.",
         None),
        ("5 Paid and recorded", "Invoice, proof of payment and dated completion record, kept together.",
         None),
    ]
    bw, gap, bh, y = 118, 16.5, 150, 40
    for i, (head, body, tabc) in enumerate(links):
        x = 8 + i * (bw + gap)
        c.box(x, y, bw, bh, fill=C.white, stroke=C.verified, sw=1.5, tab=tabc)
        hx = x + (14 if tabc else 10)
        lines = wrap(head, 13, bw - 20, 700)
        for k, ln in enumerate(lines):
            c.text(hx, y + 22 + k * 16, ln, 13, 700, C.verified)
        c.text_block(hx, y + 26 + len(lines) * 16, bw - (hx - x) - 8, body, 12)
        if i < 4:
            c.arrow(x + bw, y + bh / 2, x + bw + gap, y + bh / 2, C.accent)
    # broken-link variant
    y2 = 224
    c.text(8, y2, "Remove any one link", 13, 700, C.unresolved)
    sw_, sg = 72, 10
    xs = 8
    for i in range(5):
        x = xs + i * (sw_ + sg)
        if i == 2:
            c.box(x, y2 + 12, sw_, 34, fill=C.white, stroke=C.unresolved, dash=DASH)
            c.glyph("question", x + sw_ / 2, y2 + 29, C.unresolved)
        else:
            c.box(x, y2 + 12, sw_, 34, fill=C.accent_tint, stroke=C.verified, sw=1)
            c.text(x + sw_ / 2, y2 + 33, str(i + 1), 12, 700, C.ink, "middle")
    c.text_block(8, y2 + 70, 396,
                 "The reimbursement claim becomes a different question. Good intentions cannot "
                 "reconstruct missing authority after redemption begins.", 12)
    # side note: larger defect
    nx, nw = 440, W - 8 - 440
    c.box(nx, y2 - 14, nw, 116, fill=C.white, stroke=C.unresolved, dash=DASH)
    c.glyph("question", nx + 18, y2 + 6, C.unresolved)
    c.text(nx + 32, y2 + 10, "A larger defect", 13, 700, C.unresolved)
    c.text_block(nx + 12, y2 + 32, nw - 24,
                 "Work does not silently expand. The new condition returns through the same "
                 "authority, professional and insurance channels.", 12)
    band(c, H - 48, "The approved repair receipt becomes the concrete centre of the file.", h=40,
         weight=700)
    c.save(OUT / "fig-11-approved-repair-chain.svg")


# --------------------------------------------------------------------------- new: two ledgers
def redemption_ledger():
    W = 672
    rows = [
        ("+", "The sum the purchaser paid", "Purchase sum"),
        ("+", "Interest at 10% a year on the total paid, from sale date to redemption date",
         "Interest"),
        ("+", "Certain older unpaid taxes the purchase payment did not cover", None),
        ("+", "Taxes levied after the sale, and related interest", None),
        ("+", "The fee to record the discharge", None),
        ("+", "Qualifying fire-insurance premiums", "Fire-insurance premiums"),
        ("+", "Necessary repairs paid with the treasurer's written approval", "Approved repairs"),
        ("−", "Less: any balance in the tax-sale surplus account for the property", None),
        ("−", "Less: rent or other income earned by the purchaser from the land",
         "Less: rent or other property income"),
    ]
    lx, lw = 8, 400
    rx, rw = 432, W - 8 - 432
    rh = 36
    top = 78
    H = top + len(rows) * rh + 10 + 84
    c = Canvas(W, H, "Two ledgers for one redemption",
               "Categories of the redemption amount and of the purchaser repayment.")
    # headers
    c.rect(lx, 8, lw, 62, fill=C.municipal)
    c.text(lx + 12, 32, "Redemption amount", 13, 700, C.white)
    c.text(lx + 12, 52, "The treasurer determines it through the statutory process.", 12, 400,
           C.white)
    c.rect(rx, 8, rw, 62, fill=C.accent)
    c.text(rx + 12, 32, "Purchaser repayment", 13, 700, C.white)
    c.text(rx + 12, 52, "The statute's repayment section", 12, 400, C.white)
    for i, (sign, left, right) in enumerate(rows):
        y = top + i * rh
        offset = sign != "+"
        if offset:
            c.rect(lx, y, lw, rh, fill=C.paper2)
        c.line(lx, y + rh, lx + lw, y + rh, C.rule, 0.75)
        c.text(lx + 16, y + rh / 2 + 5, sign, 13, 700, C.ink, "middle")
        lines = wrap(left, 12, lw - 44)
        ty = y + rh / 2 + 4.5 - (len(lines) - 1) * 7.8
        for k, ln in enumerate(lines):
            c.text(lx + 32, ty + k * 15.6, ln, 12)
        c.line(rx, y + rh, rx + rw, y + rh, C.rule, 0.75)
        if right:
            if offset:
                c.rect(rx, y, rw, rh, fill=C.paper2)
            c.text(rx + 16, y + rh / 2 + 5, sign, 13, 700, C.ink, "middle")
            c.text(rx + 32, y + rh / 2 + 4.5, right, 12)
            c.line(lx + lw + 4, y + rh / 2, rx - 4, y + rh / 2, C.accent_mid, 1, dash="2 3")
    c.line(lx, top, lx + lw, top, C.ink, 1)
    c.line(rx, top, rx + rw, top, C.ink, 1)
    fy = top + len(rows) * rh + 10
    c.text(rx, fy + 4, "Not necessarily the same", 11, 400, C.ink2)
    c.text(rx, fy + 18, "line-by-line list.", 11, 400, C.ink2)
    band(c, H - 56, "From the time the full redemption amount is paid to the treasurer, the "
         "purchaser ceases to have a right to the land.", h=48, fill=C.accent_tint, weight=700)
    c.save(OUT / "fig-11-redemption-ledger.svg")


if __name__ == "__main__":
    certificate_holder_calendar()
    approved_repair_chain()
    redemption_ledger()
