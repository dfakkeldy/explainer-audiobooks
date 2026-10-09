"""Chapter 4 figures (spec: design/figure-style.md; plan: design/chapter-plan.md, Chapter 4).

    .venv/bin/python figures/ch04_figures.py

Every label below is taken from the original figure (figure-10, figure-11, figure-12), its alt
text or visuals.md entry, or the manuscript lines the chapter plan cites (md:419-459);
review/claims/ch04.md maps each one.
"""
from pathlib import Path

from svgkit import C, DASH, DOT, Canvas, wrap

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src/assets/figures"

# evidence-state styles: (stroke colour, stroke width, dash, heading colour, glyph)
STATE = {
    "municipal": (C.municipal, 1.5, None, C.municipal, None),
    "verified": (C.verified, 1.5, None, C.verified, "check"),
    "screening": (C.screening, 1.75, DOT, C.ink, None),
    "professional": (C.unresolved, 1.5, DASH, C.unresolved, "question"),
    "nogo": (C.nogo, 3, None, C.nogo, "bar"),
    # no evidence state exists for a priced unknown: accent outline plus a bounded-range glyph
    "priceable": (C.accent, 2, None, C.accent, "range"),
}


def draw_glyph(c, kind, x, y, col):
    if kind == "range":   # |-| : a bounded range
        c.line(x - 7, y, x + 7, y, col, 1.75)
        c.line(x - 7, y - 5, x - 7, y + 5, col, 1.75)
        c.line(x + 7, y - 5, x + 7, y + 5, col, 1.75)
    else:
        c.glyph(kind, x, y, col)


def state_box(c, x, y, w, h, state, fill=C.white):
    col, sw, dash, _, _ = STATE[state]
    c.box(x, y, w, h, fill=fill, stroke=col, sw=sw, dash=dash,
          tab=C.municipal if state == "municipal" else None)
    if state == "screening":   # round caps make the dotted line read as dots
        c.items[-1] = c.items[-1].replace("/>", ' stroke-linecap="round"/>')


def lines_height(s, size, w, weight=400, lh=1.3):
    return len(wrap(s, size, w, weight)) * size * lh


# --------------------------------------------------------------------------- beyond the packet
def beyond_the_packet():
    """REDRAW of figure-11. Labels verbatim (sentence case)."""
    W, H = 672, 200
    c = Canvas(W, H, "Credit the packet; add the missing work",
               "Three columns: municipal packet, research layer, handoff layer.")
    cols = [
        ("municipal", "Municipal packet",
         "Lien, AAN, PID, recovery amount, assessment, redemption marker, map and legal description.",
         "Supplied by the municipality"),
        ("verified", "Research layer",
         "Reconciliation, planning, terrain, screening limits, dated observations and source log.",
         "Added by the researcher"),
        ("professional", "Handoff layer",
         "Questions for lawyer, surveyor, planner, insurer, inspector and environmental professional.",
         "Routed to professionals"),
    ]
    bw, gap, top, bh = 190, 43, 10, 124
    for i, (state, head, body, who) in enumerate(cols):
        x = 8 + i * (bw + gap)
        state_box(c, x, top, bw, bh, state)
        tx = x + (18 if state == "municipal" else 14)
        col = STATE[state][3]
        c.text(tx, top + 28, head, 13, 700, col)
        c.text_block(tx, top + 52, bw - (tx - x) - 12, body, 12)
        if state == "professional":
            c.glyph("question", x + bw - 18, top + 24, C.unresolved)
        if i < 2:
            c.arrow(x + bw + 6, top + bh / 2, x + bw + gap - 6, top + bh / 2, C.accent, 2.25)
    # bracket and line under all three
    by = top + bh + 24
    c.line(8, by, 664, by, C.rule, 0.75)
    c.text(8, by + 26, "The value-add begins after the municipality’s facts, map and legal description.",
           12, 700, C.accent)
    c.save(OUT / "fig-04-beyond-the-packet.svg")


# --------------------------------------------------------------------------- source authority
def source_authority_ladder():
    """REDRAW of figure-10 as a staircase rising from screening to law (plan)."""
    W, H = 672, 400
    c = Canvas(W, H, "Authority depends on the question",
               "Five source cards, each with the question it can answer.")
    rungs = [  # bottom to top
        ("screening", "Imagery", "What appeared visible on a dated image?"),
        ("screening", "Map layers", "Where should another record search begin?"),
        ("municipal", "Municipal record", "What did this event publish?"),
        ("professional", "Registry / survey", "What legally identifies the interest and boundary?"),
        ("verified", "Governing law", "What process and powers apply?"),
    ]
    bw, bh, step_x, step_y = 380, 56, 60, 68
    base_y = H - 16 - bh
    for i, (state, head, q) in enumerate(rungs):
        x = 8 + 16 + i * step_x
        y = base_y - i * step_y
        state_box(c, x, y, bw, bh, state)
        tx = x + (18 if state == "municipal" else 14)
        c.text(tx, y + 22, head, 13, 700, STATE[state][3])
        # question mark icon beside each card: the question this source can answer
        c.circle(tx + 7, y + 39, 7, fill=C.white, stroke=C.ink2, sw=1.25)
        c.text(tx + 7, y + 43, "?", 11, 700, C.ink2, "middle", tag="glyph")
        c.text(tx + 20, y + 43, q, 12, 400, C.ink)
    # rising arrow at the left
    x0 = 24 + bw + 16
    c.arrow(x0, base_y + bh, x0 + 3.8 * step_x, base_y + bh - 3.8 * step_y, C.accent, 1.5)
    c.text(x0 + 40, base_y + bh - 16, "From imagery and screening clues", 11, 400, C.ink2)
    c.text(x0 + 40, base_y + bh - 2, "to governing law", 11, 400, C.ink2)
    # note in the free top-left area
    c.text_block(8, 30, 240,
                 "A stronger source is one authorized to answer the particular question — "
                 "not simply one that looks official.", 12, 700, C.accent)
    c.save(OUT / "fig-04-source-authority-ladder.svg")


# --------------------------------------------------------------------------- five labels
def five_evidence_labels():
    """REDRAW of figure-12. Labels and examples verbatim (sentence case)."""
    labels = [
        ("verified", "Verified record", "Directly supported by the cited source."),
        ("screening", "Screening clue", "A map result that starts a question."),
        ("screening", "Visual interpretation", "A dated observation, not a verified fact."),
        ("professional", "Professional verification", "The question has reached an authorized expert."),
        ("nogo", "No-go until resolved", "The intended use cannot proceed on current evidence."),
    ]
    rh, gap = 46, 10
    W, H = 672, 16 + len(labels) * (rh + gap) + 36
    c = Canvas(W, H, "Five labels keep claims honest",
               "Five evidence labels, from verified record to no-go until resolved.")
    for i, (state, head, ex) in enumerate(labels):
        y = 12 + i * (rh + gap)
        state_box(c, 10, y, 236, rh, state)
        col, _, _, hcol, glyph = STATE[state]
        c.text(28, y + 28, head, 13, 700, hcol)
        if glyph:
            draw_glyph(c, glyph, 226, y + rh / 2, col)
        c.line(254, y + rh / 2, 272, y + rh / 2, C.rule, 1)
        c.text(282, y + 28, ex, 12, 400, C.ink)
    yb = 12 + len(labels) * (rh + gap) + 2
    c.line(10, yb, 662, yb, C.rule, 0.75)
    c.text(10, yb + 22, "Good research labels the strength and authority of each observation.",
           12, 700, C.accent)
    c.save(OUT / "fig-04-five-evidence-labels.svg")


# --------------------------------------------------------------------------- four destinations
def four_destinations():
    """NEW. md:427-439, 443, 457-459."""
    rows = [
        ("What does the file actually establish?", "verified", "Verified",
         "The file has the source, date and captured record.",
         "the exact PID-to-notice match"),
        ("Does the next gap belong to a named professional or source?", "professional",
         "Professionally verifiable",
         "A question, an evidence source and a competent route to an answer; not a promise "
         "of a favourable answer.",
         "the access question, by the lawyer and surveyor"),
        ("Can a documented answer enter the budget?", "priceable", "Priceable uncertainty",
         "A documented amount or bounded range, without inventing a number. Priceable does not "
         "mean trivial.",
         "a survey quote"),
        ("Can an essential gap be resolved or carried?", "nogo", "No-go if not",
         "“Do not proceed under these conditions.” Not a prediction that the land is bad.",
         "an essential site-condition question that cannot be answered lawfully before sale"),
    ]
    from svgkit import width
    W = 672
    QX, QW = 8, 196
    BX = 248
    BW = W - 8 - BX
    gap = 14
    top = 50
    lab = "Birch Point Road: "
    lw = width(lab, 12, 700)
    heights = []
    for q, state, dest, defn, bpr in rows:
        hb = 44 + lines_height(defn, 12, BW - 52) + 12 + lines_height(bpr, 12, BW - 28 - lw)
        hq = 42 + lines_height(q, 12, QW - 24, 700)
        heights.append(max(hb, hq) + 4)
    H = top + sum(heights) + gap * (len(rows) - 1) + 54
    c = Canvas(W, H, "Four places an unknown can go",
               "Four questions in order, each leading to a destination, with Birch Point Road's entries.")
    # entry
    c.box(QX, 8, QW, 30, fill=C.paper2, stroke=C.granite, sw=1)
    c.text(QX + QW / 2, 28, "An unknown in the file", 13, 700, C.ink, "middle")
    c.arrow(QX + QW / 2, 38, QX + QW / 2, top, C.accent)
    c.text(W - 8, 28, "Birch Point Road: composite \u2014 not a real property", 11, 400, C.ink2, "end")
    y = top
    for i, ((q, state, dest, defn, bpr), rh) in enumerate(zip(rows, heights)):
        # question box
        c.box(QX, y, QW, rh, fill=C.accent_tint, stroke=C.accent, sw=1.25)
        c.text(QX + 12, y + 22, f"Question {i + 1}", 11, 700, C.accent)
        c.text_block(QX + 12, y + 42, QW - 24, q, 12, 700, C.ink)
        if i < len(rows) - 1:
            c.arrow(QX + QW / 2, y + rh, QX + QW / 2, y + rh + gap, C.accent)
        c.arrow(QX + QW + 4, y + rh / 2, BX - 2, y + rh / 2, STATE[state][0], 2)
        # destination bin
        fill = C.caution_tint if state == "nogo" else C.white
        state_box(c, BX, y, BW, rh, state, fill=fill)
        col, _, _, hcol, glyph = STATE[state]
        c.text(BX + 14, y + 24, dest, 13, 700, hcol)
        if glyph:
            draw_glyph(c, glyph, BX + BW - 20, y + 19, col)
        ny = c.text_block(BX + 14, y + 44, BW - 52, defn, 12)
        c.line(BX + 14, ny - 6, BX + BW - 14, ny - 6, C.rule, 0.75)
        c.text(BX + 14, ny + 12, lab, 12, 700, C.ink2)
        c.text_block(BX + 14 + lw, ny + 12, BW - 28 - lw, bpr, 12, color=C.ink2)
        y += rh + gap
    yb = y - gap + 14
    c.rect(8, yb, W - 16, 32, fill=C.caution_tint)
    c.glyph("bar", 26, yb + 16, C.nogo)
    c.text(42, yb + 21, "Evidence is not a vote: one essential no-go governs the file.", 13, 700, C.nogo)
    c.save(OUT / "fig-04-four-destinations.svg")


# --------------------------------------------------------------------------- handoff matrix
def handoff_matrix():
    """NEW. md:419, 445-449."""
    cols = [("Professional", 92), ("What the file sends", 196), ("The question asked", 196),
            ("What this professional does not decide", 172)]
    rows = [
        ("Lawyer",
         "Exact PID; dated municipal record; relevant instrument references; legal description; "
         "captured public view with attribution; intended use.",
         "Which registered rights provide legal access, and what interests or documents must be "
         "reviewed?",
         "Where a monument lies on the ground."),
        ("Surveyor",
         "The mapped-boundary and description question, from the same file.",
         "What evidence is needed to locate the relevant boundary or plan relationship, and can "
         "that work be completed before the decision deadline?",
         "What a tax deed does to a registered interest."),
        ("Planner",
         "Proposed use; current municipal source; parcel identifiers.",
         "Which planning, lot, frontage, servicing or permit questions require confirmation?",
         "Title or physical condition."),
    ]
    W = 672
    pad = 10
    xs = [8]
    for _, w in cols:
        xs.append(xs[-1] + w)
    hh = 46
    heights = []
    for r in rows:
        hs = [lines_height(t, 12, cols[k + 1][1] - 2 * pad) for k, t in enumerate(r[1:])]
        heights.append(max(hs) + 26)
    H = 8 + hh + sum(heights) + 50
    c = Canvas(W, H, "Who answers which question",
               "Three handoffs from one file: lawyer, surveyor, planner.")
    # header
    c.rect(8, 8, xs[-1] - 8, hh, fill=C.accent_tint)
    for k, (head, w) in enumerate(cols):
        c.text_block(xs[k] + pad, 8 + 19, w - 2 * pad, head, 12, 700, C.accent)
    y = 8 + hh
    for r, rh in zip(rows, heights):
        c.line(8, y, xs[-1], y, C.rule, 0.75)
        c.text(xs[0] + pad, y + 22, r[0], 13, 700, C.ink)
        for k, t in enumerate(r[1:]):
            x = xs[k + 1]
            color = C.ink
            if k == 2:   # "does not decide" column on a caution tint
                c.rect(x + 4, y + 6, cols[k + 1][1] - 8, rh - 12, fill=C.paper2)
                color = C.ink
            c.text_block(x + pad, y + 22, cols[k + 1][1] - 2 * pad, t, 12, color=color)
        y += rh
    c.line(8, y, xs[-1], y, C.accent, 1.5)
    c.text(8, y + 24, "The roles overlap around the parcel without becoming substitutes.", 12, 700, C.accent)
    c.text(xs[-1], y + 40, "Birch Point Road: composite — not a real property", 11, 400, C.ink2, "end")
    c.save(OUT / "fig-04-handoff-matrix.svg")


if __name__ == "__main__":
    beyond_the_packet()
    source_authority_ladder()
    five_evidence_labels()
    four_destinations()
    handoff_matrix()
