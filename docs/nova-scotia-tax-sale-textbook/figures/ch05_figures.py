"""Chapter 5 figures (spec: design/figure-style.md; plan: design/chapter-plan.md, Chapter 5).

    .venv/bin/python figures/ch05_figures.py

Three NEW figures. Every label is taken from the manuscript lines the chapter plan cites
(md:481-485, 493, 603-607, 645, 653-655, 665-671); review/claims/ch05.md maps each one.
The 14 screenshot figures are KEEP figures, handled by figures/ch05_insets.py.
"""
from pathlib import Path

from svgkit import C, DASH, Canvas, wrap

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src/assets/figures"


def h(s, size, w, weight=400, lh=1.3):
    return len(wrap(s, size, w, weight)) * size * lh


# --------------------------------------------------------------------------- current vs historical
def current_vs_historical():
    W = 672
    colw, gap, x0 = 318, 20, 8
    cols = [
        dict(head="Current notice", fill=C.municipal, text=C.white,
             rows=[
                 "What a municipality presently says it intends to sell.",
                 "The municipality's current notice or direct confirmation controls whether the "
                 "sale is live or a parcel remains listed.",
                 "A copied PDF, screenshot, browser tab or map catalogue can become stale.",
             ],
             ex_head="Example",
             ex=["Inverness, August 11, 2026 event. Snapshot checked July 22, 2026: 40 advertised, "
                 "5 withdrawn, 40 active PIDs."]),
        dict(head="Historical record", fill=C.white, text=C.ink,
             rows=[
                 "Dated results from completed events. Off by default.",
                 "Can hold a recent event whose outcome remains unknown while official results "
                 "are pending.",
                 "An opening or winning amount from an older event does not become a present "
                 "valuation.",
             ],
             ex_head="Examples",
             ex=["Halifax PID 00542589, March 8, 2022 event.",
                 "CBRM PID 15234636, July 21, 2026 event: “Awaiting official results.”"]),
    ]
    tw = colw - 32
    # layout height from the taller column
    def col_height(col):
        y = 44 + 14
        for r in col["rows"]:
            y += h(r, 12, tw) + 10
        y += 10 + 18
        for e in col["ex"]:
            y += h(e, 12, tw) + 4
        return y + 10
    body_h = max(col_height(c) for c in cols)
    H = int(8 + body_h + 16 + 40 + 8)
    c = Canvas(W, H, "Current notice or historical record",
               "Two kinds of evidence: current notices and historical records.")
    for i, col in enumerate(cols):
        x = x0 + i * (colw + gap)
        c.rect(x, 8, colw, body_h, fill=C.white, stroke=C.municipal if i == 0 else C.granite,
               sw=1.5, rx=3)
        if i == 0:
            c.rect(x, 8, colw, 36, fill=C.municipal, rx=3)
            c.rect(x, 30, colw, 14, fill=C.municipal)
        else:
            c.rect(x, 8, colw, 36, fill=C.paper2, stroke=C.granite, sw=1.5, rx=3)
        c.text(x + 16, 32, col["head"], 13, 700, col["text"])
        y = 44 + 14 + 12
        for r in col["rows"]:
            c.rect(x + 16, y - 9, 5, 5, fill=C.municipal if i == 0 else C.granite)
            c.text_block(x + 28, y, tw - 12, r, 12)
            y += h(r, 12, tw - 12) + 10
        c.line(x + 16, y - 4, x + colw - 16, y - 4, C.rule, 0.75)
        y += 14
        c.text(x + 16, y, col["ex_head"], 11, 700, C.ink2)
        y += 17
        for e in col["ex"]:
            c.text_block(x + 16, y, tw, e, 12)
            y += h(e, 12, tw) + 4
    # bottom band
    by = 8 + body_h + 16
    c.rect(x0, by, W - 16, 40, fill=C.accent)
    c.text(W / 2, by + 25, "Name the record family before repeating any amount.", 13, 700,
           C.white, anchor="middle")
    c.save(OUT / "fig-05-current-vs-historical.svg")


# --------------------------------------------------------------------------- six-part note
def six_part_note():
    W = 672
    parts = [
        ("Source", "current provincial road and water services in the checked production build."),
        ("Date", "July 20, 2026 capture."),
        ("Observation", "the service returned River Denys water intersections and no mapped road "
                        "or trail intersection for the selected polygon; transportation remained "
                        "visible nearby."),
        ("Limitation", "both source geometry and parcel geometry are screening data."),
        ("Unknown", "legal access, ground conditions, water constraints, and current service "
                    "completeness."),
        ("Next authority", "land records and a lawyer for access; survey and current municipal or "
                           "environmental sources for the physical and regulatory questions."),
    ]
    cx, cw = 8, 430          # card
    lw = 104                 # label column
    tw = cw - lw - 28
    top = 8 + 30             # below the tab
    rows = []
    y = top + 14
    for lab, txt in parts:
        rh = max(h(txt, 12, tw), 15.6) + 14
        rows.append((lab, txt, y, rh))
        y += rh
    card_h = y - top + 6
    H = int(top + card_h + 8)
    c = Canvas(W, H, "Anatomy of a research note",
               "The River Denys note in six labelled parts, with what is lost if a part is dropped.")
    # index-card tab and card
    c.rect(cx + 12, 8, 150, 30, fill=C.accent_tint, stroke=C.rule, sw=0.75, rx=3)
    c.text(cx + 24, 28, "River Denys · File note", 12, 700, C.accent)
    c.rect(cx, top, cw, card_h, fill=C.accent_tint, stroke=C.rule, sw=0.75)
    c.line(cx, top, cx + cw, top, C.accent, 2.25)
    ys = {}
    for i, (lab, txt, ry, rh) in enumerate(rows):
        if i:
            c.line(cx + 12, ry - 2, cx + cw - 12, ry - 2, C.rule, 0.75)
        c.text(cx + 14, ry + 14, lab, 12, 700, C.accent)
        c.text_block(cx + lw + 14, ry + 14, tw, txt, 12)
        ys[lab] = (ry - 2, ry - 2 + rh)
    # three "if lost" warnings, each bracketed to the part(s) it depends on
    wx = cx + cw + 34
    ww = W - 8 - wx
    warns = [
        (["Limitation"], "Lose the limitation", "The result becomes too strong."),
        (["Observation"], "Lose the observation", "The note becomes a generic disclaimer."),
        (["Unknown", "Next authority"], "Lose the unknown and handoff",
         "The note creates caution without progress."),
    ]
    for keys, head, body in warns:
        y0 = ys[keys[0]][0] + 7
        y1 = ys[keys[-1]][1] - 7
        bx = cx + cw + 10
        c.path(f"M{bx},{y0} L{bx + 8},{y0} L{bx + 8},{y1} L{bx},{y1}", stroke=C.caution, sw=1.5)
        mid = (y0 + y1) / 2
        c.line(bx + 8, mid, wx - 6, mid, C.caution, 1.5)
        bh = 14 + h(head, 12, ww - 12, 700) + h(body, 12, ww - 12)
        by = mid - bh / 2 + 6
        c.text_block(wx + 4, by, ww - 12, head, 12, 700, C.caution)
        c.text_block(wx + 4, by + h(head, 12, ww - 12, 700) + 2, ww - 12, body, 12)
    c.save(OUT / "fig-05-six-part-note.svg")


# --------------------------------------------------------------------------- research chain
def research_chain():
    W = 672
    links = [
        ("Notice", "Choose the record family, municipality, event, date and direct official "
                   "source."),
        ("Parcel", "Establish the exact PID or authoritative civic-point containment and keep "
                   "mapped geometry bounded."),
        ("Context", "Ask one source-sized question through one layer or service."),
        ("Unknowns", "Write what the result cannot establish and distinguish empty from error."),
        ("Handoff", "Name the next record, authority or qualified professional."),
    ]
    n, gap = 5, 22
    bw = (W - 16 - gap * (n - 1)) / n
    tw = bw - 20
    body_h = max(h(t, 12, tw) for _, t in links) + 22
    tab_h = 32
    H = int(8 + tab_h + body_h + 22 + 20 + 8)
    c = Canvas(W, H, "The research chain",
               "Notice, parcel, context, unknowns, handoff, each with its one-line job.")
    for i, (head, txt) in enumerate(links):
        x = 8 + i * (bw + gap)
        c.rect(x, 8, bw, tab_h, fill=C.accent, rx=3)
        c.rect(x, 8 + tab_h - 4, bw, 4, fill=C.accent)
        c.text(x + 10, 8 + 21, f"{i + 1}  {head}", 13, 700, C.white)
        c.rect(x, 8 + tab_h, bw, body_h, fill=C.accent_tint, stroke=C.accent, sw=1.5)
        c.text_block(x + 10, 8 + tab_h + 19, tw, txt, 12)
        if i < n - 1:
            ay = 8 + tab_h / 2
            c.arrow(x + bw + 3, ay, x + bw + gap - 1, ay, C.accent, 2.25)
    # footer: the chain ends in a handoff, not a score
    fy = 8 + tab_h + body_h + 22
    c.line(8, fy - 8, W - 8, fy - 8, C.rule, 0.75)
    c.text(W / 2, fy + 12, "The method does not end with a score.", 13, 700, C.ink,
           anchor="middle")
    c.save(OUT / "fig-05-research-chain.svg")


if __name__ == "__main__":
    current_vs_historical()
    six_part_note()
    research_chain()
