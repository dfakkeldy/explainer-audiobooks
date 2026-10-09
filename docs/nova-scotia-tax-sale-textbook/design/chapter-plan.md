# Chapter plan: Beyond the Tax-Sale Packet — Textbook Edition

Planning phase 1, 9 October 2026. No chapter prose is written in this phase.

## Conventions used in this plan

- `md:N` or `md:N–M` = line numbers in the frozen canonical manuscript
  `books/beyond-the-tax-sale-packet/beyond-the-tax-sale-packet.md` (1,613 lines, 54 figures).
- `E:ID` = claim ID in `docs/nova-scotia-tax-sale-book/research/evidence-notes.md`;
  `S#` = entry number in `research/sources.md`. These feed the per-section source notes.
- Original figures are `figure-NN` (files in `books/beyond-the-tax-sale-packet/images/`).
- Textbook figures are `fig-CC-slug`, where `CC` is the textbook chapter. Printed numbers
  ("Figure 5.3") are assigned in chapter order at build time.
- **KEEP** = original raster used unchanged (pixels untouched; see the screenshot inset rule).
  **REDRAW** = the same teaching content drawn again as clean vector SVG in the book's palette;
  every label in the redraw must be traceable to the facts listed (from the original figure, its
  caption/alt text, and the cited manuscript lines); nothing is added that is not listed.
  **NEW** = a figure the original does not have; it may depict only facts already in the manuscript
  at the cited lines.
- Every figure carries: an id, `alt` text (below), a caption (title + one sentence + limit), and a
  credit/attribution line. Fictional plates carry "Composite — not a real property; not a survey."

## Totals

| Treatment | Count | Figures |
|---|---:|---|
| KEEP | 16 | figure-01, figure-09 (illustrations, from their clean source art), figure-41 to figure-54 (14 map screenshots) |
| REDRAW | 38 | figure-02 to -08, -10 to -40 (23 teaching diagrams and charts + 15 fictional case plates) |
| NEW | 24 | listed per chapter below |
| **Total in textbook** | **78** | every one of the 54 originals appears exactly once |

No original figure is dropped. Four originals move for topical fit (all recorded in the claims
ledger as moved): figure-19 (Ch 7 → Ch 8), figure-22 (Ch 8 → Ch 7), figure-21 (within Ch 8, to the
occupied-building section), figure-12 stays in Ch 4 but is captioned as observation labels (see
`review/open-questions.md` Q5–Q6).

### Rules that apply to every KEEP figure

- **Illustrations (figure-01, figure-09):** use the artwork from
  `docs/nova-scotia-tax-sale-book/figures/source-art/*-landscape-source.png`, which is the same
  artwork without the slide chrome ("FIGURE-01" tag and baked-in title/caption band); the slide tag
  would clash with the book's numbering. If the source art differs in content from the published
  image, use the published image instead (open question Q7).
- **Screenshots (figure-41 to -54):** printed full content width, pixels untouched, so the in-image
  Province attribution and "Boundaries are not a survey" footer stay legible in the image. Where the
  panel text matters, the figure is a composite: the untouched full screenshot on top, then one or
  two magnified insets (pure crops of the same PNG, scaled, with a thin rule and a number linking
  them to a small marker drawn *outside* the screenshot's frame). Insets never omit the attribution:
  the caption repeats it. No callouts are drawn over the screenshot's pixels.
- Captions for screenshots state the capture date (production build checked July 22, 2026, per
  `md:481` and the screenshot receipt), and "a dated interface state; not a recommendation."

### Rules that apply to every REDRAW figure

- SVG at 672 px content width, Atkinson Hyperlegible Next labels ≥ 11 px at print size, book
  palette with greyscale cues (design brief), white ground (the originals' cream ground is dropped).
- The originals' footer strings ("Sources: MGA ss. …", "law checked 2026-07-19", "Educational
  overview • verify current law and sale terms") move into the caption's credit line verbatim so no
  source citation is lost.
- The original's slide title (for example "Auction day connects two clocks") becomes the figure's
  printed title, unless noted.
- Case plates (figure-13 to -22, -33 to -37) are schematic, fictional geometry with no provincial
  basemap; they need no Province attribution, and each carries the "not a survey" stamp the
  original shows.

---

## Front matter

- `@cover`: title, subtitle, kicker "Textbook edition", blurb, "Facts as of July 22, 2026." No
  abbreviations on the cover. Cover art: the selected *The Packet Lifts* cover is frozen; whether
  the textbook reuses it is open question Q3 (default: reuse the portrait cover art as the cover
  band, unchanged).
- `00-about.md` (`toc: false`): what this book is (a textbook edition of the 2026 governed-final
  audiobook edition; same facts); the verbatim disclaimer; how facts are dated; composite cases and
  privacy; how to use the apparatus (objectives, rails, case boxes, File Notes, source notes,
  questions, answers); credits (open question Q2).
- `01-cases.md` ("The cases in this book", `toc: true`, no number): a table of every composite case
  — name, chapters, what it teaches, figure plates — so a reader who dips in can find Harbour Road
  or Maya. Every entry restates only what the chapters say.
- `@toc`.

## Back matter

- `97-answers.md`: Appendix A, answers to every "Check your understanding" question, each answer a
  restatement of claims in the chapter, with a "See section x.y" pointer.
- `98-statutes-and-sources.md`: Appendix B, an index of statutes and official sources: statute →
  provisions as recorded in evidence notes → topic → chapters/sections; then municipal, provincial
  and other sources by publisher → chapters. Chapter-and-section references, not page numbers
  (open question Q11).
- `98b-figures.md`: Appendix C, list of figures with credits, licence statements and, for redraws,
  "Redrawn from figure-NN of the 2026 edition".
- `@glossary`.
- `99-sources.md`: Sources and credits (the full sources.md register with URLs and retrieval
  dates; fonts; licence: CC BY 4.0 as the original).

---

## Chapter 1 — How a Property Reaches a Tax Sale

Kicker: "Chapter 1 · The last scene first". Source: `md:11–107`. Chain strip: **notice**.

**Learning objectives.** After this chapter you should be able to:
1. Explain why a municipality sells land for taxes, using the terms tax lien, notice of intent and
   tax sale (`md:59–61`, `73`, `103`).
2. Put the pre-sale steps in order with their minimum periods (14 days, 60 days, 30 consecutive
   days) and the eligibility window (`md:65`, `71`, `75`).
3. Distinguish the provincial legal frame, a municipality's practice inside it, and the current
   event notice, and say which governs a Halifax event (`md:65–67`, `87–89`, `97–101`).
4. Say what the Inverness packet establishes and what it cannot decide (`md:23`, `29–43`).

**Key terms.** tax lien · notice of intent · tax sale.

**Sections.**
1. `## The packet and the question it raises` (`md:13–55`): the fictionalized Port Hood room; what
   the Inverness August 2026 packet contains; Harbour Road introduced; what each part establishes;
   45 vs 44 entries, lien six, two amounts (`md:37–39`); the first skill (`md:41`); the route
   notice → parcel → context → unknowns → handoff and the portfolio of composite cases (`md:47`);
   researcher versus bidder (`md:49–51`).
   - Rails: "The idea" (records vs conclusions, `md:41`); "Careful" (a map line feels conclusive,
     `md:33`).
   - **Case box: Harbour Road** (`md:29–31`, `43`): what the municipal page gives it; the five
     "X is not Y" limits rewritten as a two-column table (record → what it does not establish).
2. `## The first clock` (`md:57–75`): tax lien; eligibility window and backstop; Inverness and
   Chester's two-year description; preliminary notice, title search, possible survey; notice of
   intent; advertisement.
   - Rails: "The idea" (lien), "In practice" (Inverness/Chester), "Why it matters" (people before
     the bidder, `md:69–73`).
3. `## Notice, not marketing` (`md:83–89`): the fictional website line; auction vs tender; council
   minimum; dated municipal examples (Inverness, Richmond, Pictou, Annapolis, Chester).
4. `## Halifax: same sequence, different statute` (`md:97–101`): HRM Charter; Halifax's sale-expense
   categories as an example only; the retrieval test as a **Quick recall** box.
5. `## What a tax sale is` (`md:103–105`): definition; back to the room.
- Summary; Check your understanding (5): order the pre-sale steps; what the backstop requires;
  why "notice, not marketing"; which source controls a Halifax event; what the 45/44 discrepancy
  does and does not show.
- Source notes: S1, S2, S10, S11, S13, S14, S36; E:LAW-001–005, OPS-004, OPS-005, OPS-007, DATA-002,
  DATA-005.

**Figures (5).**

- **fig-01-auction-morning — KEEP figure-01** (`md:17`). Placed at the opening. Alt (original):
  "Editorial illustration of a quiet Cape Breton community hall on an auction morning, with folders
  and bidder cards visible through the entrance." Caption: "A tax sale begins as municipal collection
  work, not a treasure hunt. Illustration; the room is a composite, not a depiction of a real venue."

- **fig-01-pre-sale-timeline — NEW.** A horizontal, not-to-scale timeline from unpaid taxes to the
  sale, with minimum periods printed on the spans and the two eligibility markers above the line. A
  thin band labelled "Outside Halifax: Municipal Government Act" spans the eligibility markers; a
  note at the right edge says Halifax runs a parallel sequence under its Charter. Stations in
  municipal-fact navy; the bidder appears only at the last station.
  Facts depicted: taxes unpaid → tax lien attaches, ranks ahead of other claims, need not be
  registered (`md:59–61`); proceedings may begin for taxes unpaid from the immediately preceding
  year, not before June 30 of the following year (`md:65`); backstop: must be put up for sale once
  taxes are unpaid for the three preceding fiscal years, subject to exceptions and possible council
  deferral (`md:65`); municipalities may use a shorter trigger, e.g. Inverness and Chester describe
  two years (`md:65`); preliminary notice, at least 14 days to pay (`md:71`); title search, may order
  a survey (`md:71`); notice of intent to owner and interest holders, 60 days to pay (`md:71–73`);
  at least 30 consecutive days of public notice by qualifying newspaper or municipal website
  (`md:75`); sale by public auction, or tender with council's consent (`md:87`).
  Alt: "Timeline, not to scale, from unpaid taxes to sale day. A tax lien attaches first. Sale
  proceedings may start no earlier than June 30 of the year after the unpaid tax year, and a sale is
  required once taxes are three years unpaid, subject to exceptions. Then come a preliminary notice
  with at least 14 days to pay, a title search and possible survey, a notice of intent with 60 days
  to pay, at least 30 consecutive days of public advertisement, and the auction or tender."

- **fig-01-two-clocks — REDRAW figure-03** (`md:79`). Same structure: left column "Municipal
  collection clock" (Arrears: eligibility and council decisions; Notice: preliminary notice, title
  search, sale notice; Advertise: at least 30 consecutive days), centre "Auction day — a hinge, not a
  finish line; event terms control payment and registration details", right column
  "Purchaser / redemption clock" (Certificate: after full payment; Six-month route: possible
  redemption, protect and insure; Deed stage: if not redeemed, request and pay for deed); band "The
  sale ends neither the municipality's record work nor the purchaser's legal work." Improvement:
  true timeline arrows, the redeemable branch drawn as a fork (a dashed line notes the older-arrears
  route skips the six-month stage, `md:201`) — only if the open question on adding that fork is
  accepted (Q9, default: add it, since `md:201` states it in this chapter's sibling text; the label
  reads "older-arrears route: no six-month redemption").
  Facts: figure-03 labels; `md:63–75`, `md:201`. Credit line: "Sources: MGA ss. 134, 137–142, 150,
  152, 155–156 • law checked 2026-07-19 (from the original figure)."
  Alt (original, kept): "Two horizontal timelines meet at auction day: arrears, notices and
  advertisement before it; certificate, possible redemption and deed after it."

- **fig-01-municipal-methods-map — REDRAW figure-02** (`md:93`). The original is an abstract
  polygon, not a geographic map, despite alt text that says "Map of Nova Scotia" (flagged). Redraw as
  a true simplified outline of Nova Scotia with the seven municipal units shaded, drawn from an
  open-licence boundary dataset credited in the caption (Q8). Symbols: open auction (solid gavel-free
  dot), tender (square), auction + tender (half-filled), check current notice / no 2026 sale (open
  ring). Labels exactly as the original figure: Inverness — auction; CBRM — auction; Richmond —
  auction; Pictou — tender; Annapolis — auction + tender; Kings — auction record; Chester — check
  current notice. Footer note: "Dated procedural examples • refresh the event notice."
  Facts: figure-02 labels; `md:87` (Inverness, Richmond auctions; Pictou sealed tender; Annapolis
  auction-to-tender; Chester no 2026 sale); `md:1177` (CBRM auction); Kings appears only in the
  original figure and alt text (source: `research/municipality-comparison.md`; flagged F-03).
  Alt: "Map of Nova Scotia highlighting Inverness, Cape Breton Regional Municipality, Richmond,
  Pictou, Annapolis, Kings and Chester, with symbols for auction, tender, both, or check the current
  notice. Dated examples only."

- **fig-01-whose-rules — NEW.** Three stacked tiers, each answering one question: top "Provincial
  law — why a sale can occur" with two side-by-side boxes (Municipal Government Act, outside
  Halifax; Halifax Regional Municipality Charter, Halifax); middle "Municipal practice — how a
  municipality operates inside that frame" (example: Inverness and Chester describe two-year
  eligibility; Halifax lists sale-expense categories, an example not a price list); bottom
  "Current event notice — whether this sale is happening, in what form, under which local
  instructions". A side arrow labelled "For a live event, the current notice of the municipality
  running it controls."
  Facts: `md:65–67`, `md:89`, `md:97`, `md:99–101`.
  Alt: "Three tiers of authority. Provincial law explains why a tax sale can occur: the Municipal
  Government Act outside Halifax and the Halifax Regional Municipality Charter in Halifax.
  Municipal practice explains how one municipality works within that law. The current event notice
  says whether a particular sale is happening and on what terms, and it controls for a live event."

---

## Chapter 2 — Reading the Notice

Kicker: "Chapter 2 · What the notice says—and does not say". Source: `md:109–247`. Chain strip:
**notice**, **parcel**.

**Learning objectives.**
1. Identify the six fields of a sale-schedule row and the record system each belongs to
   (`md:113–175`).
2. Explain the different jobs of the AAN and the PID, and why an address is related but not
   interchangeable (`md:131–151`).
3. Explain why the recovery amount is a collection figure, not an appraisal, and what a redemption
   marker does and does not tell you (`md:187–205`).
4. Keep a versioned file with source-state labels and treat withdrawal as narrow evidence
   (`md:207–245`).

**Key terms.** Assessment Account Number (AAN) · Parcel Identification Number (PID) · assessment ·
recovery amount (plus redemption marker as a defined phrase, glossary only).

**Sections.**
1. `## Six fields, six different jobs` (`md:111–181`).
   - `### The lien number and the assessed-owner field` (`md:125–129`).
   - `### Two catalogue keys: AAN and PID` (`md:131–147`), analogy and its limit kept.
   - `### Address, assessment and Property Online` (`md:149–161`), with the firm Property Online
     boundary as a **Careful** panel (`md:161`).
   - `### When the packet disagrees with itself` (`md:163–171`).
   - **Case box: Harbour Road's routing sheet** (`md:173–179`): the collapsed list at `md:175`
     becomes a proper table (field → what it identifies → question beside it).
2. `## The fields that pull hardest` (`md:183–245`).
   - `### The recovery amount` (`md:187–197`), with the $4,000 Harbour Road example (`md:193`).
   - `### The redemption marker` (`md:199–205`), with 27 redeemable / 18 non-redeemable (`md:205`).
   - `### A list that can shrink` (`md:207–219`), NS Marks The Spot's first appearance (`md:211–213`).
   - **Quick recall: four questions after an interruption** (`md:221–231`).
   - `### Dating the file` (`md:233–245`): source-state labels, withdrawal, historical results.
- Summary; Check your understanding (5): which number identifies the mapped parcel; what the
  recovery amount supports and does not; which source decides whether a lien is still in the sale;
  what a non-redeemable marker establishes; why the file needs two dates.
- Source notes: S10, S15, S16, S17, S36, S48; E:LAND-001–004, DATA-002, OPS-003, LAW-009, MAP-003.

**Figures (5).**

- **fig-02-packet-anatomy — REDRAW figure-04** (`md:119`). A fictional Inverness-style parcel
  sheet with numbered callouts to: lien number, AAN, PID, recovery amount, assessment (land and
  building), redemption marker, map area, legal-description area. Values are obviously fictional
  placeholders: identifiers are masked ("PID ••••• 421", echoing `md:83`'s fictional "parcel
  identifier ending four-two-one"); amounts reuse only Harbour Road's fictional $4,000 (`md:193`). A callout legend beside the sheet gives each field's job in five words. Facts:
  figure-04 alt; fields from `md:115`, `md:23`. Alt (original): "Annotated fictional tax-sale packet
  page pointing to lien number, AAN, PID, recovery amount, assessment, redemption marker, map and
  legal-description areas."

- **fig-02-identifier-ladder — REDRAW figure-05** (`md:143`). Seven record cards in a ladder from
  tax-sale lien to legal description (lien, AAN, PID, civic address, assessment, map, legal
  description), each paired with the conclusion it does not support, struck through. Improvement:
  the struck-through conclusions are listed in plain text with a strike line *and* the word "not"
  (greyscale-safe). Facts: figure-05 alt and caption; `md:133`, `137`, `149–155`; `md:31`.
  Alt (original): "Seven labelled record cards form a ladder from tax-sale lien to legal
  description, with the unsupported conclusions crossed out beside each card."

- **fig-02-two-catalogue-keys — NEW.** Two keys, each opening a drawer: "AAN → assessment account
  (assessed value, classification, other taxation information)" and "PID → mapped land parcel →
  parcel mapping and registry information"; a third pointer, "Civic address → orientation: finds the
  area", aimed at a place, not a drawer. Under each drawer, a "does not establish" line. A footnote
  states the analogy's limit. Facts: `md:131–139`, `md:149–151`, `md:159` (Property Online searches by
  PID, owner, AAN and civic address). Alt: "Two catalogue keys. The Assessment Account Number opens
  the assessment account: value, classification and other tax information. The Parcel Identification
  Number opens the mapped land parcel and leads to parcel mapping and registry records. A civic
  address only points to a place. None of them proves boundaries, access, title quality or a
  permitted use."

- **fig-02-reconcile-the-packet — REDRAW figure-06** (`md:169`). Six source boxes (summary list,
  detail sheet, live webpage, registry, result sheet, council record; "keep separately") feeding a
  table: Lien 6 detail — listed / detail missing — unresolved; Recovery amount — summary amount /
  detail amount differs — ask municipality; May 2025 outcome — 35 reported sold / 31 result rows —
  keep both counts. Band: "A discrepancy is a research finding — not permission to choose the
  convenient version." Improvement: amber highlight paired with a dotted outline; table set as a
  real table. Facts: figure-06; `md:37`, `md:163`, `md:197`, `md:1059–1061`. Credit: "Sources:
  Inverness August 2026 packet; May 2025 packet, result sheet and council minutes (from the original
  figure)." Alt (original): "Six source boxes feed a comparison table; mismatched amount, missing
  detail page and differing result counts are highlighted in amber."

- **fig-02-source-state-labels — NEW.** A dated strip for the fictional Harbour Road file with three
  labelled snapshots: "Packet retrieved July 20", "Municipal page checked August 10", and a dashed
  third card "Treasurer confirmed withdrawn August 11 — only if that confirmation actually occurred".
  Above it, the index card with its two required dates: packet retrieved; last event-status check.
  Facts: `md:235`, `md:241`; withdrawal as narrow evidence `md:237`. Alt: "A fictional research file
  for Harbour Road labelled with dated source states: packet retrieved July 20, municipal page checked
  August 10, and, only if it really happened, treasurer confirmed withdrawn August 11. The file card
  records two dates: when the packet was retrieved and when event status was last checked."

---

## Chapter 3 — Certificate, Redemption and Deed

Kicker: "Chapter 3 · The six-month door". Source: `md:249–343`. Chain strip: **unknowns**,
**handoff** (post-sale stages).

**Learning objectives.**
1. Distinguish a leading bid, completed payment, a registered certificate, a discharge and a tax
   deed (`md:255–257`, `329`).
2. State who may redeem, within what period, and the older-arrears exception (`md:259`).
3. List the certificate holder's powers and duties and the boundary on each (`md:269–277`).
4. Name the categories in a redemption calculation and why an evidence ledger matters
   (`md:299–307`).
5. Explain what "fee simple free of encumbrances" and "immediate deed" do and do not mean
   (`md:317–321`).

**Key terms.** certificate of sale · certificate holder · discharge · tax deed.

**Sections.**
1. `## The document between a bid and a deed` (`md:251–295`).
   - `### The middle state` (`md:253–261`).
   - `### Powers and duties` (`md:269–277`), with the insurance-duty limit as a **Careful** panel
     (`md:273`).
   - **Case box: Harbour Road's leaking roof** (`md:275–279`, `287`).
   - **Quick recall: four stage questions** (`md:283–289`), the collapsed list at `md:285` set as a
     numbered list.
   - The relay-baton analogy and its limit (`md:291`) as a short rail "A way to picture it".
2. `## Two endings, two documents` (`md:297–341`).
   - `### Redemption and the evidence ledger` (`md:299–313`).
   - `### The deed branch` (`md:315–321`).
   - `### The document sequence` (`md:329`).
   - **Case box: Harbour Road and Quarry Lane** (`md:331–337`, `341`).
- Summary; Check your understanding (5).
- Source notes: S1, S2; E:LAW-007–012, OCC-001.

**Figures (3).**

- **fig-03-redeemable-route — REDRAW figure-07** (`md:265`). Timeline: auction → certificate →
  insurance and record keeping → possible redemption → tax deed if no redemption occurs. Improvement:
  the six-month span drawn as a bracket labelled "six months after the sale"; the redemption exit as
  a branch ending in "repayment and discharge". Facts: figure-07; `md:259–261`, `269`, `309`, `315`.
  Alt (original): "Timeline from auction to certificate, insurance and record keeping, possible
  redemption, and tax deed if no redemption occurs."

- **fig-03-nonredeemable-route — REDRAW figure-08** (`md:325`). Short route auction → deed beside
  four unresolved branches: possession, access, title, intended use. Improvement: the branches drawn
  with the "unresolved" dashed style and a label "Immediate deed describes timing, not readiness."
  Facts: figure-08; `md:259`, `md:319–321`. Alt (original): "Short route from auction to deed beside
  four unresolved branches labelled possession, access, title and intended use."

- **fig-03-two-parcels-two-endings — NEW.** Two parallel lanes from the same fictional auction:
  Harbour Road (redeemable) — paid in full → certificate → month 4: redeemed → records supplied,
  repayment through the process, rights in the land end, certificate discharged; Quarry Lane
  (older-arrears category) — paid in full → deed requested and registered → "does not answer: is the
  driveway a right-of-way? is anyone occupying the building?". Facts: `md:331–335`, `md:341`.
  Alt: "Two fictional parcels sold at the same auction. Harbour Road is redeemable: after full
  payment its purchaser holds a certificate, the property is redeemed in month four, the purchaser
  is repaid through the process and the certificate is discharged. Quarry Lane is in the
  older-arrears category: its purchaser requests and registers a deed, which still does not answer
  questions about the driveway or occupancy."

---

## Chapter 4 — Building the Parcel File

Kicker: "Chapter 4 · Give the parcel a biography". Source: `md:345–465`. Chain strip: **parcel**,
**unknowns**, **handoff**.

**Learning objectives.**
1. Inventory what the municipal packet already provides before adding research (`md:349–351`).
2. Keep a source ledger in which each line has a source, retrieval date and limitation
   (`md:361`, `369`).
3. Distinguish the parcel register snapshot, the source instruments and their legal effect
   (`md:377–383`); the legal description from a civic address and a map (`md:385–389`).
4. Apply the Province's attribution and licence boundary to public map views (`md:391–393`).
5. Sort unknowns into four destinations and explain why one no-go governs (`md:425–461`).

**Key terms.** parcel register · legal description · title search (four destinations as a defined
list in the glossary: verified, professionally verifiable, priceable uncertainty, no-go).

**Sections.**
1. `## What the municipality has already done` (`md:347–421`).
   - `### The inventory and the source ledger` (`md:349–371`), **Case box: Birch Point Road**
     (`md:359–361`, `399`).
   - `### Two routes into the map` (`md:373`), pointing ahead to Chapter 5.
   - `### Property Online and the parcel register` (`md:375–383`), Property Online boundary as a
     **Careful** panel (`md:375`).
   - `### The legal description and the screening exhibit` (`md:385–389`).
   - `### Licence and attribution` (`md:391–393`), the attribution sentence set as a quotation.
   - `### Title search` (`md:395–397`).
   - `### Writing bounded observations` (`md:407–419`): the collapsed list at `md:409` set as a list;
     the verbs table "associates / returns / shows / contains" vs "owns / bounds / permits /
     guarantees" (`md:411`).
2. `## Four places an unknown can go` (`md:423–463`).
   - `### Verified, professionally verifiable, priceable, no-go` (`md:427–441`).
   - **Quick recall: the four questions** (`md:443`).
   - `### The handoff` (`md:445–451`).
   - `### Court-directed sales` (`md:453–455`).
   - **Case box: Birch Point Road in all four destinations** (`md:457–461`).
- Summary; Check your understanding (5).
- Source notes: S15, S16, S19, S36, S46, S47, S49; E:DATA-005, LAND-001, LAND-002, LAND-004, LAW-003,
  LAW-013, GIS-001, GIS-002, MAP-001, MAP-002.

**Figures (6).**

- **fig-04-beyond-the-packet — REDRAW figure-11** (`md:355`). Three columns (the original shows
  three, although its alt text says "two-column"; flagged F-11): Municipal packet (lien, AAN, PID,
  recovery amount, assessment, redemption marker, map and legal description); Research layer
  (reconciliation, planning, terrain, screening limits, dated observations and source log); Handoff
  layer (questions for lawyer, surveyor, planner, insurer, inspector and environmental
  professional). Title "Credit the packet; add the missing work." Facts: figure-11 labels; `md:23`,
  `md:349–351`. Alt (original wording adapted only to say three columns, if Q12 approves; default
  keeps the original alt): "Two-column stack comparing municipal packet contents with
  reconciliation, planning, terrain, environmental screening, uncertainty labels and professional
  handoffs."

- **fig-04-evidence-desk — KEEP figure-09** (`md:365`), from source art. Alt (original): "Overhead
  editorial illustration of a desk with a municipal packet, map layers, statute, source log and three
  folders marked known, unresolved and professional." Caption: "The researcher's product is a
  traceable evidence file, not a verdict. Illustration."

- **fig-04-source-authority-ladder — REDRAW figure-10** (`md:403`). Five source cards, each with the
  question it can answer: Imagery — what appeared visible on a dated image?; Map layers — where
  should another record search begin?; Municipal record — what did this event publish?; Registry /
  survey — what legally identifies the interest and boundary?; Governing law — what process and
  powers apply? Improvement: drawn as a ladder rising from screening to law, with a note that "a
  stronger source is one authorized to answer the particular question — not simply one that looks
  official." Facts: figure-10; `md:399`. Alt (original): "Stacked source cards rise from imagery and
  screening clues to municipal records, registry evidence and governing law, with different question
  icons beside them."

- **fig-04-five-evidence-labels — REDRAW figure-12** (`md:415`). Five labels with one-line examples:
  Verified record — directly supported by the cited source; Screening clue — a map result that starts
  a question; Visual interpretation — a dated observation, not a verified fact; Professional
  verification — the question has reached an authorized expert; No-go until resolved — the intended
  use cannot proceed on current evidence. Each drawn in its evidence-state style. Caption: "Labels for
  the strength of an observation. Good research labels the strength and authority of each
  observation." (Q6.) Facts: figure-12 labels. Alt (original): "Five colour-coded evidence cards
  progress from verified record to unresolved no-go, each with a one-sentence example."

- **fig-04-four-destinations — NEW.** A sorting diagram: an unknown enters at the top and passes
  four questions in order (What does the file actually establish? → verified; Does the gap belong to
  a named professional or source? → professionally verifiable; Can a documented amount or bounded
  range enter the budget? → priceable uncertainty; Can an essential gap be resolved or carried in
  time? if not → no-go: "do not proceed under these conditions"). Below, Birch Point Road's four
  items placed in their bins, and a balance-scale note: "Evidence is not a vote: one essential no-go
  governs." Facts: `md:427–439`, `md:443`, `md:457–459`. Alt: "Four destinations for an unknown.
  Verified: the file establishes it from a dated source. Professionally verifiable: a named
  professional or source can answer it. Priceable: a documented amount or range can enter the
  budget. No-go: an essential fact cannot be confirmed before the sale. For the fictional Birch Point
  Road, the PID-to-notice match is verified, a survey quote is priceable, access is professionally
  verifiable, and an essential site-condition question is no-go, which governs the file."

- **fig-04-handoff-matrix — NEW.** A table-figure with three rows (lawyer, surveyor, planner) and
  three columns: what the file sends; the question asked; what this professional does not decide.
  Facts: `md:419`, `md:445–449`. Alt: "Who answers which question. The lawyer receives the PID,
  dated record, instrument references, legal description, attributed map view and intended use, and
  is asked which registered rights give legal access; the lawyer does not locate boundaries on the
  ground. The surveyor is asked what evidence locates the boundary or plan relationship and whether
  that can be done before the deadline; the surveyor does not decide what a tax deed does to a
  registered interest. The planner receives the proposed use and identifiers and identifies planning,
  lot, frontage, servicing and permit questions; the planner does not confirm title or physical
  condition."

---

## Chapter 5 — Using the Map as a Research Tool

Kicker: "Chapter 5 · The map is a question machine". Source: `md:467–689`. Chain strip: all five
links (this chapter introduces the whole chain).

**Learning objectives.**
1. Choose the record family (current notice or historical result) before reading any parcel
   (`md:481–483`).
2. Establish parcel identity by exact PID or authoritative civic-point containment, and state what
   containment does not prove (`md:507–531`).
3. Read mapped area, building counts, assessment, Plus Codes, intersections and flood results as
   bounded records (`md:509–519`, `539–541`, `585–601`).
4. Write a six-part note: source, date, observation, limitation, unknown, next authority
   (`md:603–607`).
5. Explain why a mineral occurrence opens questions about tenure and surface rights, using the
   Mineral Resources Act and the Touquoy example (`md:617–631`).

**Key terms.** civic point · Plus Code · layer · mapped intersection.

**Sections.**
1. `## Start with the record family` (`md:469–567`).
   - `### Current notice or historical result` (`md:479–497`), the July 22, 2026 Inverness snapshot
     figures (40 advertised, 5 withdrawn, 40 active PIDs) printed with their date (`md:481`).
   - `### Parcel identity` (`md:505–541`): exact PID; mapped area; building count and PVSC
     assessment for demonstration PID `50292390` (`md:511–519`); civic address and containment;
     Plus Codes.
   - **Quick recall: four recovery questions** (`md:543–547`).
   - `### Boundary and imagery` (`md:549–557`).
   - **File Note: Birch Point Road map note** (`md:561`).
2. `## One question at a time` (`md:569–619`).
   - `### Layers` (`md:571–573`).
   - `### Road and water: a demonstration` (`md:575–591`), PID `50308311`, Southside River Denys Road,
     Valley Mills, about 5.12 mapped acres; "not a recommendation" kept with it.
   - `### Flood evidence` (`md:593–601`).
   - **File Note: the six-part road-and-water note** (`md:603–607`).
   - `### Geology and resources` (`md:609–619`).
3. `## A small find, and a larger property question` (`md:621–635`).
   - The author's panning story kept in the first person as a boxed aside ("From the author"),
     brook unnamed (`md:623`); Mineral Resources Act (`md:627`); Touquoy (`md:629`); empty views and
     handoffs (`md:633–635`).
4. `## Historical mode` (`md:637–665`): Halifax PID `00542589` (March 8, 2022), CBRM PID
   `15234636` (July 21, 2026, "Awaiting official results").
5. `## The whole method` (`md:667–687`): the five words; Birch Point Road's combined state; **File
   Note: final file entry** (`md:683`).
- Summary; Check your understanding (6).
- Source notes: S17, S22, S46–S54; E:MAP-001–008, GIS-001, GIS-002, LAND-004, DATA-002, DATA-005,
  MIN-001–004.

**Figures (17).** All screenshot captions add: "Production build of NS Marks The Spot, captured
July 22, 2026. A dated interface state, not a recommendation. Contains information obtained under
license from the Province of Nova Scotia which is provided without warranty or liability for errors
or omissions."

- **fig-05-map-layer-overview — KEEP figure-41** (`md:475`). Alt (original): "Production map with
  current and historical modes, current defaults and the available public layers visible." Inset:
  the left layer panel.
- **fig-05-current-vs-historical — NEW** (after `md:483`). Two columns, "Current notice" and
  "Historical record". Current: what a municipality presently says it intends to sell; the direct
  official source controls whether the sale and parcel are live; a snapshot can go stale; example:
  Inverness August 11 event, snapshot checked July 22, 2026 (40 advertised, 5 withdrawn, 40 active
  PIDs). Historical: dated results from completed events, off by default; may hold a recent event
  whose outcome is "unknown" while official results are pending; an old opening or winning amount
  does not become a present value; examples: Halifax PID `00542589`, March 8, 2022 event; CBRM PID
  `15234636`, July 21, 2026, "Awaiting official results". Bottom band: "Name the record family
  before repeating any amount." Facts: `md:481–485`, `md:493`, `md:645`, `md:653–655`, `md:665`.
  Alt: "Current notices and historical records are different kinds of evidence. A current notice
  says what a municipality presently intends to sell, and only the municipality's own current source
  confirms it is still live. A historical record reports a dated result, or that the result is still
  pending; its amounts are not a present value. Examples: the Inverness August 11, 2026 snapshot,
  a Halifax result from March 8, 2022, and a CBRM record from July 21, 2026 still awaiting official
  results."
- **fig-05-current-parcel-browser — KEEP figure-43** (`md:489`). Alt (original): "Inverness August 11
  view showing 40 advertised records, 5 withdrawn records, 40 active PIDs, redemption filters and the
  direct official source." Inset: the "Tax-sale notices" and "Redemption category" panel.
- **fig-05-province-data-licence — KEEP figure-42** (`md:501`). Alt (original): "Province-data notice
  in landscape and mobile layer-source metadata identify approximate boundaries, dated services and
  the licence boundary." Inset: the notice dialog.
- **fig-05-buildings-assessment — KEEP figure-52** (`md:515`). Alt (original): "Parcel inspector
  showing two mapped building features, PVSC AAN `00616672`, 2026 assessed and taxable values of
  $35,000, and the attached limitations." Inset: the inspector panel.
- **fig-05-civic-address-search — KEEP figure-44** (`md:525`). Alt (original): "Exact civic-address
  result and selected parcel shown together, with authoritative-result language visible." (The
  address visible in the image is not repeated in text or caption.)
- **fig-05-current-parcel-evidence — KEEP figure-45** (`md:535`). Alt (original): "Selected parcel
  with authoritative civic result, Plus Code, mapped context and explicit evidence limits."
- **fig-05-aerial-and-property-boundaries — KEEP figure-46** (`md:553`). Alt (original): "Selected
  civic parcel on NS Aerial with graphical property-boundary linework and source attribution."
- **fig-05-roads-water-context — KEEP figure-47** (`md:581`). Alt (original): "Southside River Denys
  parcel sheet showing current notice facts, River Denys intersections and no mapped road/trail
  intersection." Inset: the parcel sheet's road and water rows.
- **fig-05-six-part-note — NEW** (at `md:603–607`). The River Denys note set as a File Note card,
  each of the six parts bracketed and labelled; beside it three "if lost" warnings: lose the
  limitation → result too strong; lose the observation → generic disclaimer; lose the unknown and
  handoff → caution without progress. Facts: `md:605` (note text verbatim, re-lined), `md:607`.
  Alt: "Anatomy of a research note, using the River Denys example: source (current provincial road
  and water services), date (July 20, 2026 capture), observation (River Denys water intersections and
  no mapped road or trail intersection), limitation (both geometries are screening data), unknown
  (legal access, ground conditions, water constraints, service completeness) and next authority (land
  records and a lawyer for access; survey and current municipal or environmental sources for physical
  and regulatory questions). Dropping any part makes the note too strong, too vague, or cautious
  without progress."
- **fig-05-flood-hazard-evidence — KEEP figure-53** (`md:597`). Alt (original): "Flood evidence panel
  reports outside the four river-study extents and no current, 2050 or 2100 coastal pixel
  intersection, with the no-hazard caveat visible." Inset: the flood panel.
- **fig-05-geology-resources — KEEP figure-48** (`md:613`). Alt (original): "Selected parcel with
  geology and resource controls active and map symbols visible."
- **fig-05-historical-outcomes-overview — KEEP figure-49** (`md:641`). Alt (original): "Historical
  mode showing 154 records, 161 exact matched PIDs, municipality, year and outcome filters, and
  explicit outcome-unknown language."
- **fig-05-historical-outcome-sheet — KEEP figure-50** (`md:649`). Alt (original): "Halifax March 8,
  2022 result sheet with official notice/result links, difference/ratio fields and historical
  disclaimer." Inset: the result sheet.
- **fig-05-cbrm-outcome-unknown — KEEP figure-54** (`md:659`). Alt (original): "CBRM July 21, 2026
  record marked Outcome pending, with minimum bid, Awaiting official results, official links and
  dated-notice-only limitation." Inset: the record panel.
- **fig-05-research-chain — NEW** (at `md:667–669`; also the source of the chain strip motif). Five
  linked tabs with one-line definitions: Notice — choose the record family, municipality, event,
  date and direct official source; Parcel — establish the exact PID or authoritative civic-point
  containment and keep mapped geometry bounded; Context — ask one source-sized question through one
  layer or service; Unknowns — write what the result cannot establish and distinguish empty from
  error; Handoff — name the next record, authority or qualified professional. Footer: "The method
  does not end with a score." Facts: `md:667–671`. Alt: "The research chain in five links: notice,
  parcel, context, unknowns, handoff, each with its one-line job. The chain ends with a handoff to
  the next authority, not with a score."
- **fig-05-combined-parcel-research — KEEP figure-51** (`md:675`). Alt (original): "Soapstone Mine
  Road parcel sheet, civic results, Plus Codes, road/water observations and geology/resource layers
  together." (Q10: whether to keep the place name in alt text; default keep, as the original prints
  it.)

---

## Chapter 6 — Access and Intended Use

Kicker: "Chapter 6 · The driveway that may not be a right-of-way". Source: `md:691–805`. Chain
strip: **context**, **unknowns**, **handoff**.

**Learning objectives.**
1. Separate a visible route, a legal right of passage, and a route capable of serving a project
   (`md:747`).
2. Define right-of-way, road frontage and zoning, and say what each does not settle
   (`md:715`, `765`, `769–771`).
3. Frame a planning call around a named PID and use (`md:763`, `777`).
4. Explain why favourable answers do not merge into a permit, and write a rational no
   (`md:787`, `797–801`).

**Key terms.** right-of-way · road frontage · zoning.

**Sections.**
1. `## The route you can see` (`md:693–749`). **Case box: Maple Ridge (Case A)** opens the chapter
   (`md:695`); entry and CBRM's no-access guidance as a **Careful** panel (`md:711`); the door-and-key
   analogy with its limit (`md:717`); the changed-fact variations (`md:733–737`); **File Note:
   Maple Ridge access note** (`md:741`).
2. `## The use the parcel must support` (`md:751–803`). Frontage; zoning; Plan Inverness (effective
   September 11, 2025) and the Eastern District Planning Commission (`md:773`); **File Note: the
   bidder's call script** (`md:777`); permitted use vs approved project; services and setbacks;
   municipal boundary (`md:789`); Maple Ridge's two columns as a table (`md:791`); **File Note: a
   rational no** (`md:799`).
- Summary; Check your understanding (5).
- Source notes: S7, S15, S24, S25, S41; E:LAND-004–006, LAND-008, LAW-012, LAND-007.

**Figures (5).** Case A plates are redrawn as one consistent family: the same fictional sliver
geometry, scale bar and north arrow on every plate, a "Composite — not a real property; not a
survey" stamp, and the three side-cards of the original as a right-hand rail of labelled cards.

- **fig-06-case-a-orientation — REDRAW figure-13** (`md:699`). Wide orientation: fictional Parcel A
  (the long narrow sliver) among communities, public roads and water; scale and north arrow; side
  cards "Place" and "Limit" (orientation does not prove lawful access, title, condition or services).
  Facts: figure-13. Alt (original): "Wide map locating fictional Parcel A among communities, public
  roads and water, with scale and north arrow."
- **fig-06-case-a-access — REDRAW figure-15** (`md:721`). Parcel A, a nearby public road, a dashed
  visible track crossing an intervening lot, steep contours, and a question mark where legal access
  would need proof; side cards "Visible approach", "Legal access", "Terrain". Facts: figure-15;
  `md:695`, `md:711`. Alt (original): "Terrain map showing Parcel A, a nearby public road, a dashed
  visible track, steep contours and a question mark where legal access would need proof."
- **fig-06-case-a-identity — REDRAW figure-14** (`md:729`). Parcel A highlighted with three fictional
  record identifiers (lien, AAN, PID; fictional, styled "••••") and a prominent "Not a survey" stamp;
  side cards "Lien / AAN / PID" and "Boundary". Facts: figure-14. Alt (original): "Parcel A
  highlighted with three fictional record identifiers and a prominent not-a-survey warning."
- **fig-06-case-a-planning — REDRAW figure-16** (`md:759`). Zone shading (labelled "Zone A" and a
  second zone with "?"), a frontage dimension line, well and septic question icons, and a
  "planner confirms" callout; side cards "Zone", "Frontage", "Services". Facts: figure-16. Alt
  (original): "Map of fictional Parcel A with zoning colour, frontage dimension, well and septic
  question icons, and a planner-confirmation callout."
- **fig-06-independent-gates — NEW** (at `md:787–801`). Five gates in a row, each a separate
  question with its own authority: visible approach (map and imagery) → legal access (title
  instruments, lawyer, survey) → road frontage (applicable rules, planning authority) → zoning /
  permitted use (planner) → development approval and services (application, permits, qualified
  advice). Under them, Maple Ridge's state from the second half of the chapter: track visible; a
  registered passage right that appears to benefit the parcel, needing final legal and survey
  confirmation; frontage and lot status unanswered; a zone in which a dwelling may be permitted;
  building envelope, physical access, services and approvals unresolved → "rational no". A
  footnote: "None of these records grants permission to enter." Facts: `md:747`, `md:753`, `md:765`,
  `md:781`, `md:787`, `md:791–801`. Alt: "Five separate gates for the fictional Maple Ridge parcel:
  a visible approach, legal access, road frontage, zoning, and development approval with services.
  The track is visible; a registered passage right appears to benefit the parcel but needs legal and
  survey confirmation; frontage and lot status are unanswered; a dwelling may be a permitted use; the
  building envelope, physical access, services and approvals are unresolved, so the bidder decides
  not to bid. No record grants permission to enter."

---

## Chapter 7 — Physical and Environmental Records

Kicker: "Chapter 7 · The things a map cannot smell". Source: `md:807–943`. Chain strip:
**context**, **unknowns**.

**Learning objectives.**
1. Turn exterior clues into literal observations (`md:821`).
2. Explain what the Environmental Registry, the well-log database and the on-site sewage record
   service can and cannot show, including the seven-year sewage-record limit (`md:825–859`).
3. Read a coastal hazard scenario and an abandoned-mine inventory point with their stated limits
   (`md:889–909`).
4. Distinguish positive, negative and error results and write the note each requires
   (`md:919–927`).

**Key terms.** contaminated site · well log · hazard map.

**Sections.**
1. `## Three records beneath one yard` (`md:809–883`). **Case box: Breakwater Lane (composite)**
   (`md:811`); contaminated sites and the Environmental Registry; **File Notes** `md:831`, `833`;
   wells and well logs; **File Note** `md:849`; sewage records; **File Note** `md:859`; the four-way
   classification (`md:871`, collapsed list set as a list); no entry (`md:873`, **Careful**).
2. `## A future shore and an incomplete past` (`md:885–941`). Hazard maps; the Coastal Hazard Map
   and its 2100 scenario; **File Note** `md:899`; abandoned mine openings, incompleteness and
   positional uncertainty; the flashlight analogy and its limit (`md:911`); result states and
   **File Notes** `md:923–927`; **Quick recall** (`md:929`); **File Note: environmental summary**
   (`md:933`).
- Summary; Check your understanding (5).
- Source notes: S20–S23; E:ENV-001–005, LAND-007.

**Figures (9).**

- **fig-07-case-a-screening — REDRAW figure-17** (`md:815`). Case A's fifth plate: Parcel A with
  wet-ground, coastal, geology and mine-opening screening symbols; side cards "Searched layers",
  "Screening clue", "No result". Caption names it "Case A, plate 5" and says it previews the
  screening layers used for Breakwater Lane (it is not a Breakwater Lane map; Q5). Facts: figure-17.
  Alt (original): "Aerial-style map of Parcel A with wet-ground, coastal, geology and mine-opening
  screening layers and an unresolved-evidence legend."
- **fig-07-case-b-screening — REDRAW figure-22, moved from Ch 8** (to sit at `md:825–833`). Parcel B
  with a former-use symbol, a nearby registry point and arrows to records and
  environmental-professional questions; side cards as figure-17. Facts: figure-22. Alt (original):
  "Parcel B map with a former-use symbol, nearby registry point and arrows to records and
  environmental-professional questions."
- **fig-07-case-b-orientation — REDRAW figure-18** (`md:865`). Parcel B in a serviced community with
  a building footprint and nearby streets; side cards "Place", "Limit". Facts: figure-18. Alt
  (original): "Map locating fictional Parcel B in a serviced community with a building footprint and
  nearby streets."
- **fig-07-three-records-one-yard — NEW** (at `md:861–871`). One schematic yard with a building and
  four labelled records beneath it, each with its result type and limit: former-use history —
  positive clue that widens environmental inquiry; contaminated-site registry search — bounded
  negative (reporting and search limits); well log — positive record with uncertain parcel
  association, location and present condition; on-site sewage search — negative, read against the
  record service's limited retention (a record is unlikely for a property more than seven years
  old). A struck-through caption "no · yes · no" with "misleading symmetry". Facts: `md:821`,
  `md:827`, `md:839–841`, `md:853`, `md:861`, `md:871`. Alt: "Four records under one fictional
  yard. The former workshop use is a positive clue that widens environmental questions. The
  contaminated-site search found nothing, within its search and reporting limits. One estimated well
  log exists, but its link to this parcel and the well's present condition are unverified. The
  sewage search found no file, which means little because such records are unlikely to exist for a
  property more than seven years old. Reading these as 'no, yes, no' would mislead."
- **fig-07-case-b-access — REDRAW figure-20** (`md:877`). Parcel B with a driveway, a drainage path
  and public observation points outside the boundary; side cards "Visible approach", "Legal access",
  "Terrain". Facts: figure-20. Alt (original): "Street-and-terrain map of Parcel B showing a
  driveway, drainage path and public observation points outside the parcel boundary."
- **fig-07-coastal-scenario — NEW** (at `md:893–901`). Left: the 2100 worst-case coastal flooding
  scenario built as a stack of three components — highest high tide + a one-in-one-hundred-year
  storm surge + projected sea-level rise — with a selector showing current / 2050 / 2100 and a note
  that the years are sea-level scenarios, not extra probabilities. Right: "What the colour means"
  (the selected scenario, current data, model, resolution and map guidance) and "What it does not
  report" (surveyed floor elevation, shoreline-protection condition, floodwater route through a
  culvert, damage from a particular storm; not engineering, insurance or approval). A small inset
  repeats that a river-study 1% or 5% annual-exceedance probability describes the event mapped by
  that study. Facts: `md:593`, `md:893–895`. Alt: "How to read a coastal hazard scenario. The 2100
  worst case combines the highest high tide, a one-in-one-hundred-year storm surge and projected
  sea-level rise; current and 2050 are other scenarios, not added probabilities. The colour belongs
  to the selected scenario, data, model and resolution. It does not report a building's elevation,
  a shoreline structure's condition, how water would flow, or damage from a particular storm, and it
  is not an engineering, insurance or approval decision."
- **fig-07-positional-uncertainty — NEW** (at `md:903–909`). A fictional rural parcel edge, a road
  and a building site, with an abandoned-mine-opening symbol just outside the line and a circle of
  roughly 50 m radius drawn to the scale bar, crossing the parcel line and the road. Labels: "2024
  inventory: positions on private land can have lower confidence and may be inaccurate by roughly
  fifty metres"; "inventory is incomplete; excludes surface expressions of subsidence; site
  conditions may change". Facts: `md:903–907` (wording "roughly fifty metres" kept as the original
  prints it; flagged F-07 because the source says "up to approximately 50 metres"). Alt: "A mine
  opening symbol sits just outside a fictional parcel. A circle with a radius of about fifty metres
  shows how far the true position may be from the symbol on private land, enough to cross the parcel
  line and the road. The inventory is also incomplete and leaves out surface signs of subsidence."
- **fig-07-negative-search-beam — REDRAW figure-23** (`md:915`). The flashlight: a beam covers part
  of a dark field; four coverage dimensions as cards — Time (was the relevant period included?),
  Place (was the parcel inside the source's mapped coverage?), Record type (would this source contain
  the event or condition?), Match rule (could spelling, geometry or identifiers hide a record?);
  hazards outside the beam remain unknown. Improvement: draw the actual beam the alt text describes
  (the original renders only cards). Facts: figure-23 labels and alt; `md:911`. Alt (original): "A
  flashlight beam covers part of a dark field labelled by time, location and record type; hazards
  outside the beam remain unknown."
- **fig-07-result-states — NEW** (at `md:919–927`). Three columns: Positive — feature returned:
  preserve source, date, geometry, attributes, coverage limits, positional quality, next question;
  Negative — query completed with no returned feature: preserve source, date, settings, completeness
  limits and the narrow concern not confirmed; Error — no reliable result: preserve the failure,
  retry or use the authoritative source, draw no negative conclusion. Above the error column: "a
  failed service, loading timeout, hidden layer or wrong selection is not 'nothing found'." Facts:
  `md:633`, `md:919–927`. Alt: "Three result states. Positive: a feature was returned; keep its
  source, date, geometry, attributes, coverage and position limits and the next question. Negative:
  the query finished and returned nothing; keep the source, date, settings and completeness limits,
  and name the narrow concern it did not confirm. Error: no reliable result; record the failure,
  retry or go to the authoritative source, and conclude nothing."

---

## Chapter 8 — Title and Possession

Kicker: "Chapter 8 · Title is not possession". Source: `md:945–1049`. Chain strip: **unknowns**,
**handoff**. Opening note keeps the original's framing that this chapter steps forward to a deeded
case on purpose (`md:949`).

**Learning objectives.**
1. Explain what the tax deed conveys (fee simple, free of encumbrances) and the statute's treatment
   of easements and rights-of-way (`md:953–957`).
2. Identify the court-order branch and the separate surplus-money route (`md:969–975`).
3. Explain why "clear title" is an unsafe label (`md:977`).
4. Distinguish title from possession, and name the lawful-process boundary (`md:991–1007`).
5. Identify the separate records involved when a manufactured home is listed (`md:1009–1031`).

**Key terms.** fee simple · encumbrance · vacant possession.

**Sections.**
1. `## What the deed actually changes` (`md:947–987`). **Case box: Foundry Street (composite)**
   (`md:949`, `957`); the deed-effect rule; Foundry Street's right-of-way and the link back to
   Chapter 6 (`md:959`); **File Note: court-order check** (`md:973`); surplus as a money route
   (`md:975`); "clear title" (`md:977–985`); **Quick recall** (`md:983`).
2. `## The house does not empty on paper` (`md:989–1047`). Occupants (`md:991`); CBRM's guidance as a
   dated example (`md:993`); vacant possession; coat-check analogy and limit (`md:997`); actions not
   taken as a **Careful** panel (`md:999`, `1039`); certificate-period boundary (`md:1003`); goods
   left behind (`md:1005`); possession as a decision input (`md:1007`).
   - `### When the asset is a manufactured home` (`md:1009–1033`): **Case box: Harbour Park
     (composite)** (`md:1021`); **File Note** `md:1031`.
   - **Quick recall: four questions** (`md:1035`).
- Summary; Check your understanding (5).
- Source notes: S1, S2, S4, S5, S7, S33, S34, S35; E:LAW-012–014, OCC-001, MOB-001.

**Figures (6).**

- **fig-08-title-encumbrance-possession — REDRAW figure-24** (`md:965`). Three columns: Title —
  what ownership interest is recorded?; Rights and burdens — what easements, liens or continuing
  interests may matter?; Possession — who or what is actually on the land?; joined by dotted (not
  equal) signs. Facts: figure-24. Alt (original): "Three parallel columns labelled ownership
  interest, rights and burdens, and people or property on site, joined by dotted rather than equal
  signs."
- **fig-08-deed-effect — NEW** (at `md:953–981`). Foundry Street's register before the deed (a
  mortgage, a judgment, a registered right-of-way serving the house behind) and three outcome lanes
  after the deed: "Interests the statute discharges — counsel confirms which"; "Easements and
  rights-of-way: a benefit passes with the land; a burden continues as the Act specifies" (the
  right-of-way to the rear house drawn continuing); "If a court order exists: its exceptions,
  exclusions or partial interests apply". A separate side channel, not touching the land, for
  "possible claim to surplus proceeds — a money route, not a burden on the land". The mortgage and
  judgment are not drawn as erased; they sit in the "counsel confirms" lane. Facts: `md:953–957`,
  `md:969`, `md:975`, `md:981`. Alt: "What a tax deed changes for the fictional Foundry Street. The
  deed vests fee simple free of encumbrances, but a lawyer must confirm which registered interests,
  such as the mortgage and judgment, the statute discharges. Easements and rights-of-way continue as
  the Act specifies, so the right-of-way serving the house behind stays. A court order, if there is
  one, adds its own exceptions. A former interest holder's claim to surplus money follows a separate
  route and is not a burden on the land."
- **fig-08-case-b-planning — REDRAW figure-21, moved within Ch 8** (from `md:1025` to the occupied
  section, `md:991–1007`). Parcel B with zone shading, water and sewer lines, a use-confirmation icon
  and a separate occupancy warning; side cards "Zone", "Frontage", "Services". Facts: figure-21. Alt
  (original): "Planning map of Parcel B with zone, water and sewer lines, use-confirmation icon and a
  separate occupancy warning."
- **fig-08-case-b-identity — REDRAW figure-19, moved from Ch 7** (to `md:1017–1021`). Parcel B outline
  containing a building footprint and a separate manufactured-home question card tied to different
  fictional records. Facts: figure-19. Alt (original): "Parcel B outline contains a building
  footprint and a separate manufactured-home question card tied to different fictional records."
- **fig-08-manufactured-home-records — NEW** (at `md:1017–1031`). Four separate record boxes around
  the fictional Harbour Park listing, none joined: the home (mobile-home tax-sale regulations and
  prescribed forms; mobile home identifier); the land under it (land records; the PID the map
  selects); the right to keep the home on the space (land-lease community, Residential Tenancies
  framework); security interests in the home (Personal Property Registry — not the land registry).
  Centre label: "Asset identity unresolved — no PID-only conclusion." Facts: `md:1017–1021`,
  `md:1031`. Alt: "Four separate records for the fictional Harbour Park listing: the manufactured
  home itself, under Nova Scotia's mobile-home tax-sale rules; the land under it, in the land
  records; the right to keep the home on its space, under the residential-tenancy rules for
  land-lease communities; and any security interest in the home, in the Personal Property Registry.
  A search by PID alone cannot answer what is being sold."
- **fig-08-occupied-property-handoff — REDRAW figure-25** (`md:1043`). Flow: lawful exterior
  observation (remain off the parcel, avoid confrontation) → public records (preserve only bounded,
  source-backed facts) → lawyer / tenancy advice (establish the lawful route before contact or
  entry); a stop card: "No lock change, entry, rent demand or goods handling without authority."
  Facts: figure-25. Alt (original): "Flowchart starts with lawful exterior observation and records,
  then stops at lawyer or tenancy advice before contact, entry, lock changes or goods handling."

---

## Chapter 9 — Results, Costs and the Maximum Bid

Kicker: "Chapter 9 · The number you decide before the room". Source: `md:1051–1165`. Chain strip:
**unknowns**, **handoff**.

**Learning objectives.**
1. Read a result sheet with its completeness limits (50 advertised, 35 sold, 31 rows) (`md:1059–1061`).
2. Describe the Inverness 2025, CBRM March 2026 and Richmond June 2026 samples and why they cannot
   predict (`md:1069–1093`).
3. Build an all-in cost from a defined use, with an uncertainty reserve that does not bridge a
   missing right (`md:1101–1135`).
4. Identify the four tax and eligibility branches (`md:1137–1149`).
5. Derive a maximum bid backward from a supported value boundary, and check it is fundable
   (`md:1151–1157`).

**Key terms.** all-in cost · uncertainty reserve · maximum bid · supported value boundary.

**Sections.**
1. `## What a result sheet can tell you` (`md:1053–1115`): three counts; the Inverness ratios; the
   surplus figure; CBRM; Richmond; comparison discipline; the historical layer; assessment;
   **Case box: Cedar Street (composite)** (`md:1099`); all-in cost and the iceberg analogy with its
   limit (`md:1101–1103`); **Quick recall** (`md:1113`).
2. `## Build the number backward` (`md:1117–1163`): three cost groups; evidence states; uncertainty
   reserve; the worked arithmetic ($30,000 + $40,000 + $20,000 = $90,000) as a small table
   (`md:1133`); tax branches as a table (`md:1137–1147`); maximum bid; supported value boundary;
   payment within three business days (`md:1157`); **Case box: Cedar Street's worksheet and the card
   that stays down** (`md:1159–1163`).
- Summary; Check your understanding (6).
- Source notes: S9, S17, S26–S30, S38, S40, S42; E:DATA-001, DATA-003, DATA-004, LAND-003, TAX-001–003,
  ELIG-001, LAW-006, MAP-007.

**Figures (6).**

- **fig-09-fifty-thirtyfive-thirtyone — REDRAW figure-27** (`md:1065`). Count cards: 50 advertised
  properties; 35 reported sold in council minutes; 31 published result rows; 15 removed before sale;
  4 sold-row gap left unresolved. Improvement: drawn as a flow from 50 splitting into 35 sold and 15
  removed, with the 31 published rows as a subset of the 35 and the 4-row gap hatched "unresolved".
  Facts: figure-27; `md:1059–1061`. Alt (original): "Three large count cards show 50 advertised, 35
  reported sold and 31 published result rows, with 15 removals and a four-row unresolved gap."
- **fig-09-inverness-ratio-distribution — REDRAW figure-26** (`md:1073`). The original groups dots
  by threshold (16 under 5×, 8 at 5–10×, 7 at 10× or more) and says dots are not exact positions.
  Redraw as a horizontal stacked bar of the 31 published rows in four bands derived only from the
  counts the text states (`md:1069`): under 2× — 7 (31 − 24); 2× to under 5× — 9 (24 − 15); 5× to under
  10× — 8 (15 − 7); 10× or more — 7; with median 4.53× and range 1.00×–21.62× printed beside it, and
  "31 published rows of 35 reported sales; recovery amount is not value". No individual row
  positions are drawn. Facts: figure-26; `md:1069`, `md:1077`. Alt: "The 31 published bid rows from
  Inverness County's May 2025 sale, grouped by bid as a multiple of the recovery amount: 7 under
  twice, 9 from twice to under five times, 8 from five to under ten times, and 7 at ten times or more.
  Median 4.53 times; range 1.00 to 21.62 times. The rows are not all 35 reported sales."
  (Original alt, recorded in the ledger: "Dot plot of 31 bid-to-recovery ratios from 1.00 to 21.62,
  with the 4.53 median marked and a 31-row completeness caveat.")
- **fig-09-municipal-result-comparison — REDRAW figure-28** (`md:1089`). Three small panels:
  Inverness 2025 — 31 published rows, median bid/recovery 4.53×, 35 reported sold; CBRM March 2026 —
  24 recorded sales, median winning/minimum 3.17×, range to more than 42×, 8 at minimum, 9 at 5× or
  more; Richmond June 2026 — 3 sold rows, ratios about 1.33, 6.59 and 6.28 times listed taxes,
  interest and charges. Each panel labels format, row count and denominator; band "Definitions
  travel with the numbers." Facts: figure-28; `md:1069`, `md:1081`, `md:1085`, `md:1093`. Alt
  (original): "Three small charts compare dated municipal result sets, each labelled with auction
  type, number of rows and a warning against treating recovery as value."
- **fig-09-all-in-cost-stack — REDRAW figure-29** (`md:1107`). Layered stack: bid (the amount called
  or tendered); tax (applicable tax and deed-transfer questions); legal / registry; survey; insurance;
  carrying; repair / remediation; possession; uncertainty reserve. Improvement: drawn as a vertical
  stack with the bid as the small visible top layer and a waterline (the iceberg analogy, with its
  limit in the caption: layers are researched, not mysterious; proportions not fixed). No amounts.
  Facts: figure-29; `md:1101–1103`. Alt (original): "Layered stack begins with bid price and adds
  taxes, legal work, insurance, survey, carrying costs, repairs, remediation, possession and
  reserve."
- **fig-09-build-backward — NEW** (at `md:1133` and `md:1151–1155`). Two panels kept visibly
  separate. Panel a, "All-in exposure (worked example)": $30,000 bid + $40,000 known non-bid costs +
  $20,000 uncertainty reserve = $90,000. Panel b, "The maximum, built backward" (no numbers):
  supported value boundary − known non-bid costs − uncertainty reserve = what remains → maximum bid,
  only if every legal, eligibility, payment and no-go condition is satisfied; "if nothing remains:
  no bid". Facts: `md:1133`, `md:1153–1155`. Alt: "Two panels. First, the book's worked example of
  all-in exposure: a $30,000 bid plus $40,000 of known non-bid costs plus a $20,000 uncertainty
  reserve equals $90,000. Second, how a maximum bid is built backward: start from the supported
  value boundary, subtract known non-bid costs and the reserve, and what remains can become the
  maximum bid if every condition is met; if nothing remains, the result is no bid."
- **fig-09-tax-eligibility-branches — NEW** (at `md:1137–1149`). Four branches as a decision panel,
  each with its dated fact: (1) municipal deed transfer tax — a tax-sale deed is exempt under the
  Municipal Government Act; registration charges, HST, the non-resident tax, income tax and advice
  remain; (2) provincial non-resident deed transfer tax — for qualifying transfers after March 2025,
  10% based on the non-resident interest and the higher of purchase price or assessed value, subject
  to definitions and exemptions (one concerns moving to Nova Scotia within six months); (3) HST —
  CBRM's event instructions say it applies to vacant land and commercially assessed property;
  Canada Revenue Agency guidance makes treatment depend on the seller, prior use, property,
  transaction and purchaser's registration; (4) eligibility — the federal prohibition on certain
  purchases by non-Canadians is currently scheduled through January 1, 2027. Footer: "An unanswered
  branch means the file is not ready." Facts: `md:1137–1149`. Alt: "Four tax and eligibility
  questions to answer before bidding: whether the municipal deed-transfer-tax exemption for tax-sale
  deeds applies; whether the provincial non-resident deed transfer tax applies, at 10 percent on the
  higher of price or assessed value for qualifying transfers after March 2025; what the HST
  treatment of this transaction is, since CBRM's event rule is not a provincial rule; and whether
  the buyer is eligible under the federal non-Canadian purchase prohibition, scheduled through
  January 1, 2027. Any unanswered branch means the file is not ready."

---

## Chapter 10 — Auction Day, Tenders and Payment

Kicker: "Chapter 10 · When the card goes up". Source: `md:1167–1275`. Chain strip: **handoff**.

**Learning objectives.**
1. Compare an open-outcry auction and a public tender, and explain why the maximum enters both
   unchanged (`md:1173–1185`).
2. State who the Municipal Government Act prohibits from buying, and separate eligibility, authority
   and event compliance (`md:1195–1199`).
3. Prepare a payment sheet: statutory payment forms, the event's accepted forms, the immediate
   amount and the three-business-day balance (`md:1217–1233`).
4. Trace what happens when there is no sufficient bid, no immediate payment, a missed balance, a
   failed tender payment or a schedule change (`md:1245–1273`).

**Key terms.** open-outcry auction · public tender · deposit.

**Sections.**
1. `## Two formats, one decision` (`md:1169–1203`): Inverness's St. Peter's Parish Hall auction
   (`md:1173`); CBRM's dated mechanics (`md:1177`); tenders; Pictou April 2026; Annapolis 2026;
   **Case box: Maya's rehearsal** (`md:1193`); the prohibited buyers (`md:1195`); the three-question
   sheet as a table (`md:1199`).
2. `## The finish line beyond the hammer` (`md:1205–1241`): source refresh; the open-outcry
   sequence; payment forms; Inverness terms; deposit; two readiness tests; **Case box: Maya's payment
   sheet** (`md:1233`); Pictou's tender payment; analogy limit (`md:1237`); "ready means" as a
   five-item checklist (`md:1241`).
3. `## When the expected sale does not happen` (`md:1243–1273`): the three breaks; tender failure;
   state changes; schedule changes; the certificate as the next stage.
- Summary; Check your understanding (5).
- Source notes: S1, S2, S7, S8, S10, S12, S39, S43, S44; E:LAW-005, LAW-006, LAW-015, LAW-016,
  OPS-001–006.

**Figures (3).**

- **fig-10-auction-versus-tender — REDRAW figure-30** (`md:1189`). Two lanes: Open auction —
  register, hear live calls, card stays down above the limit; Sealed tender — choose once, submit by
  deadline, no live adjustment; both ending at "Same evidence file: eligibility, authority, event
  terms and walk-away rule do not change." Facts: figure-30; `md:1173–1185`. Alt (original):
  "Parallel timelines compare registration and live bidding with sealed submission and opening, both
  ending at the same written walk-away rule."
- **fig-10-payment-readiness-clock — REDRAW figure-39** (`md:1223`). Path: Authorized (identity,
  authority and conflict check) → Funds ready (event-accepted forms in hand) → Immediate (price or
  recovery deposit; Inverness registration amount) → 3 business days (any remaining purchase
  balance); "When the expected path breaks": No sufficient bid (municipality may buy for the
  recovery amount, or advertise again for auction or tender); No immediate payment (treasurer puts
  the land up for sale again immediately); Balance missed (re-advertise and resell; resale expenses
  come out of the deposit). Band: "The hammer finds a leading bid. Prepared payment completes the
  sale step." Facts: figure-39; `md:1217–1229`, `md:1247–1257`. Credit: "Sources: MGA ss. 143,
  148–149; HRMC ss. 158–159, 163–164 • verify current event terms (from the original figure)." Alt
  (original): "Horizontal readiness path from authorized registration to accepted funds, immediate
  recovery and registration payment, then the three-business-day balance, with branches for no
  sufficient bidder, immediate re-offer, re-advertisement and resale costs."
- **fig-10-sale-state-changes — NEW** (at `md:1263`). A state diagram: Advertised → (withdrawn: paid,
  removed or deferred; check the current source) or Called → (no sufficient bid → treasurer may bid
  and buy for the municipality, or the property may be advertised again and later sold at auction for
  the best obtainable price or by highest tender, subject to any council minimum; "unsold" is not
  privately available — CBRM's legend: only at a future tax sale) or Leading offer → (immediate
  payment fails → offered again at once; next bidder does not inherit the price) or Immediate payment
  made → (balance not paid within three business days → re-advertised and sold; resale expenses
  deducted from the deposit, remainder refunded after the resale) or Paid in full → certificate of
  sale (redeemable branch). A side box: Tender — pay within three business days after notification
  of acceptance; failure returns the land toward advertisement and sale. A second side box: Schedule
  change — return to the current notice. Facts: `md:1245–1273`. Alt: "What can happen to a listed
  property at a sale. It may be withdrawn before it is called. If called with no sufficient bid, the
  municipality may buy it or advertise it again; it is not then available privately. If the high
  bidder cannot pay immediately, the property is offered again at once. If the immediate amount is
  paid but the balance is not paid within three business days, it is advertised and sold again and
  resale expenses come out of the deposit. If paid in full, the treasurer gives a certificate of
  sale. For a tender, the accepted bidder has three business days after notification to pay. Any
  schedule change sends the bidder back to the current notice."

---

## Chapter 11 — The Certificate-Holder Months

Kicker: "Chapter 11 · The certificate-holder months". Source: `md:1277–1369`. Chain strip:
**handoff**.

**Learning objectives.**
1. Describe the certificate holder's operating lane: protect, collect rent, use without diminishing,
   do not cut trees or injure, insure insurable buildings (`md:1285–1289`).
2. Keep the first operating file and handle new tax bills (`md:1295`, `1303`).
3. Explain insurable interest and why one insurer's refusal is evidence, not a legal finding
   (`md:1305–1313`).
4. Follow a necessary repair through written treasurer approval (`md:1315–1321`).
5. Name the redemption formula's categories and offsets, and when the purchaser's rights end
   (`md:1335–1357`).

**Key terms.** insurable interest · necessary repairs.

**Sections.**
1. `## Responsibility before certainty` (`md:1279–1325`): **Case box: Maya and Cedar Street**
   (`md:1281–1283`); the lane; protective vs development work; no forced entry (**Careful**,
   `md:1291`); safety; the operating file; new tax bills; insurance (refusal, broker, quote vs
   policy); the approved repair; rent and income; "active restraint" summary (`md:1325`).
2. `## Closing the ledger when the property is redeemed` (`md:1327–1367`): month four; who may
   redeem; the human scene; the formula and offsets; the 10% line; the statement; redemption amount
   vs purchaser repayment; Halifax's Administrative Order 18 categories as a Halifax-only example
   (July 2026 snapshot); the legal moment rights cease; close-out record; final ledger list.
- Summary; Check your understanding (5).
- Source notes: S1, S2, S14, S31; E:LAW-007–011, INS-001, OPS-007, OCC-001.

**Figures (3).**

- **fig-11-certificate-holder-calendar — REDRAW figure-31** (`md:1299`). Six month cells with
  recurring tasks: month 1 — certificate; organize evidence and insurance attempts; month 2 — track
  new taxes, notices and protective-work records; month 3 — maintain lawful protection, preserve
  every receipt; month 4 — refresh status and keep the redemption route open; month 5 — prepare
  questions without assuming the outcome; month 6 — redemption may close the file, otherwise deed
  work begins. The original month-1 label reads "Register certificate"; registration
  is the treasurer's act (`md:255`, `md:1281`), so the label is flagged (F-16); it is redrawn verbatim
  unless Dan approves the suggested rewording in the flag. Facts: figure-31; `md:1295–1303`. Alt
  (original): "Six-month calendar with recurring record-keeping and insurance tasks, new-tax markers,
  protective-work limits and a possible redemption event."
- **fig-11-approved-repair-chain — NEW** (at `md:1315–1321`). Five links: observed risk (a qualified
  exterior assessment finds a loose roof covering) → defined scope and cost → the treasurer's written
  approval → lawful, safe performance of only that scope → invoice, proof of payment and dated
  completion record. A broken-link variant beneath: "remove any link and the reimbursement claim
  becomes a different question"; a side note: "a larger defect returns through the same channels."
  Facts: `md:1315–1321`. Alt: "The chain behind a reimbursable repair in the fictional Cedar Street
  file: a qualified assessment identifies the risk, Maya sends a defined scope and cost, the
  treasurer approves it in writing, the contractor does only that work through lawful and safe
  access, and Maya keeps the invoice, proof of payment and completion record. Without any link, the
  claim becomes a different question."
- **fig-11-redemption-ledger — NEW** (at `md:1335–1349`). Two ledgers side by side. Left, "Redemption
  amount (the treasurer determines it)": the sum the purchaser paid; interest at 10% a year on the
  total paid, from sale date to redemption date; certain older unpaid taxes the purchase did not
  cover; taxes levied after the sale, with interest; the fee to record the discharge; qualifying
  fire-insurance premiums; necessary repairs paid with the treasurer's written approval; less: any
  balance in the tax-sale surplus account for the property; less: rent or other income earned from
  the land. Right, "Purchaser repayment": purchase sum, interest, fire-insurance premiums, approved
  repairs, less rent or other property income. Footer: "From the time the full redemption amount is
  paid to the treasurer, the purchaser ceases to have a right to the land." Facts: `md:1335–1337`,
  `md:1341`, `md:1349`, `md:1357`. Alt: "Two ledgers for a redemption. The redemption amount, set by
  the treasurer, includes the purchase sum, 10 percent yearly interest from sale to redemption,
  certain unpaid older taxes, taxes levied after the sale with interest, the discharge recording fee,
  qualifying fire-insurance premiums and approved necessary repairs, minus any surplus balance and
  any rent or income the purchaser earned. The purchaser's repayment covers the purchase sum,
  interest, premiums and approved repairs, minus rent or income. The purchaser's right to the land
  ends when the full amount is paid to the treasurer."

---

## Chapter 12 — After the Deed

Kicker: "Chapter 12 · The deed is a beginning". Source: `md:1371–1495`. Chain strip: **handoff**.

**Learning objectives.**
1. Describe the two routes to a deed request and what to check in the delivered deed
   (`md:1377–1379`).
2. Explain deed registration, the Affidavit of Value and registry fees as dated requirements
   (`md:1383–1389`).
3. Distinguish the six-month, six-year and twenty-year clocks and what starts each
   (`md:1391–1393`, `1471–1473`).
4. Plan a second due-diligence wave without treating any one answer as the whole project
   (`md:1421–1455`).
5. Keep the ownership, surplus and challenge files separate (`md:1459–1489`).

**Key terms.** deed registration · post-deed due diligence · tax-sale surplus account.

**Sections.**
1. `## The document changes, the questions move` (`md:1373–1417`): the request; registration;
   Affidavit of Value; fees; the Marketable Titles Act clock; right-of-way and access revisited;
   insurance; possession (**Careful**, `md:1405`); first entry; three records (`md:1409`).
2. `## The second due-diligence wave` (`md:1419–1455`): definition; Foundry Street's plan; CBRM's
   zoning-confirmation and municipal-clearance letters; PVSC and the Capped Assessment Program;
   lawful access and professional findings; environmental evidence; revised plan; updated decision
   record.
3. `## The money and the challenge take different roads` (`md:1457–1493`): surplus account;
   **Case box: Elena (composite)** (`md:1469–1473`); challenges; the Marketable Titles Act
   qualifications; set-aside does not discharge the lien; three files as a table (`md:1485`).
- Summary; Check your understanding (5).
- Source notes: S1–S3, S17, S18, S20, S25, S26; E:LAW-012, LAW-014, LAW-017, LAW-018, TAX-001,
  LAND-003, LAND-006, OCC-001.

**Figures (3).**

- **fig-12-three-clocks — NEW** (at `md:1391–1393`, revisited at `md:1473`). A not-to-scale
  timeline with two anchors. From the sale date: six-month redemption period (no six-month period if
  taxes were more than six years in arrears at sale); the twenty-year surplus window (application
  after the redemption period and before twenty years from the sale). From the deed-registration
  date: the six-year Marketable Titles Act period, with its three qualifications listed (land
  exclusion under stated conditions; current owner's fraud or breach of trust; damages claim for
  wrongful tax sale preserved). A note: "Not auction day, not deed delivery, not first entry: the
  six years start at registration." Facts: `md:1377`, `md:1391–1393`, `md:1471–1473`, `md:1477`.
  Alt: "Three different legal clocks. The six-month redemption period and the twenty-year window to
  apply for surplus proceeds both run from the sale date. The six-year period in which a tax deed
  can generally be set aside runs from the deed's registration date, subject to a land-exclusion
  rule, a fraud or breach-of-trust exception, and a preserved claim for damages."
- **fig-12-deed-is-a-beginning — REDRAW figure-32** (`md:1413`). Tax deed at the centre sending six
  arrows to: title review (lawyer); possession (lawful process); planning (written municipal
  answers); survey (boundary and access); condition (inspection and environmental review); insurance
  (actual underwriting). Facts: figure-32. Alt (original): "Tax deed at the centre sends six arrows
  to lawyer, possession, planning, survey, condition and insurance workstreams."
- **fig-12-surplus-proceeds-route — REDRAW figure-40** (`md:1465`). Purchase money → statutory
  applications (taxes, interest, sale expenses and specified municipal amounts) → balance to the
  tax-sale surplus account; then two branches: if redeemed — the balance reduces the redemption
  amount under the statutory formula; after redemption expires — a prior interest holder may apply
  to the Supreme Court for a proportional payment before twenty years pass. Band: "No automatic
  payout • no purchaser windfall • court route and deadlines matter." Facts: figure-40; `md:1461`,
  `md:1471`, `md:1337`. Credit: "Sources: MGA ss. 146–147; HRMC ss. 161–162 • educational route
  summary (from the original figure)." Alt (original): "Sale proceeds first satisfy statutory
  municipal amounts, then enter a surplus account; after redemption expiry a prior interest holder
  may apply to Supreme Court before the twenty-year endpoint."

---

## Chapter 13 — Putting the Method Together

Kicker: "Chapter 13 · A file that knows its limits". Source: `md:1497–1613`. Chain strip: all five.

**Learning objectives.**
1. Run three fresh composite files through the method and state, for each, the verified fact, the
   unresolved question, the next authority and the decision consequence (`md:1507–1579`).
2. Explain why Alder Crossing stops, Union Workshop stays unresolved and Meadow Line reaches a
   decision point (`md:1579`).
3. Keep a stage record that survives withdrawal, payment, redemption and deed (`md:1585–1601`).
4. Describe what a public map should and should not supply, and the separate roles of researcher,
   professionals and bidder (`md:1603–1605`).

**Key terms.** none new; the chapter's glossary use is retrieval.

**Sections.**
1. `## Three parcels, three different endings` (`md:1499–1581`): three **Case boxes**: Alder
   Crossing (`md:1505–1513`), Union Workshop (`md:1515–1531`), Meadow Line (`md:1533–1577`); the
   four-part sentence as a rail exercise (`md:1507`).
2. `## The record that survives the event` (`md:1583–1611`): the stable core; the public-private
   boundary; stage records (five fields as a table, `md:1597`); outcomes; the deed's limit; a better
   public map (`md:1603`); roles (`md:1605`); closing.
- Summary; Check your understanding (6, cumulative).
- Source notes: S7, S10, S15, S17, S20, S25, S28, S38, S40; E:DATA-005, LAND-005, LAND-006, ENV-001,
  OCC-001, TAX-003, DATA-003.

**Figures (7).** Case C plates follow the Case A family style.

- **fig-13-three-endings — NEW** (at `md:1503`, recapped at `md:1579`). Three columns, one per
  composite file, each with the same four rows (verified fact; unresolved question; next authority;
  consequence): Alder Crossing — one account with two PIDs; civic point inside one polygon / which
  interest is sold and how the PIDs, account, descriptions and building relate / the municipality's
  current notice and counsel's land-record review / stop. Union Workshop — dated notice, exact PID,
  specific public-source returns / possession, former use, condition, insurance, tax treatment /
  counsel, environmental and building professionals, municipality, insurer, tax adviser / stop: not
  priceable in time. Meadow Line — summary and detail agree; AAN and PID consistent; mapped road;
  zoning response / access, frontage, lot, use, services / lawyer, municipality, site professionals,
  surveyor if needed / decision point for the bidder (no recommendation). Facts: `md:1505–1513`,
  `md:1515–1531`, `md:1533–1577`, `md:1579`. Alt: "Three fictional files, three endings. Alder
  Crossing stops because one account lists two parcels and the records do not say what is sold.
  Union Workshop stops because occupancy, former use, condition, insurance and tax questions cannot
  be answered before the sale. Meadow Line's records agree and its remaining questions have
  credible routes, so it reaches a decision point, which belongs to the bidder."
- **fig-13-case-c-orientation — REDRAW figure-33** (`md:1537`). Parcel C near a public road and
  community services, a green "evidence file" label and no bid score; side cards "Place", "Limit".
  Alt (original): "Regional map locates fictional Parcel C near a public road and community services
  with a green evidence-file label and no bid score."
- **fig-13-case-c-identity — REDRAW figure-34** (`md:1543`). Parcel C outline beside matching
  fictional lien, AAN and PID cards and a not-a-survey note. Alt (original): "Parcel C outline
  beside matching fictional lien, AAN and PID cards and a not-a-survey note."
- **fig-13-case-c-access — REDRAW figure-35** (`md:1553`). Parcel C touching a mapped public road,
  gentle contours, a lawyer-confirmation icon at the frontage; side cards "Visible approach", "Legal
  access", "Terrain". Alt (original): "Parcel C touches a mapped public road and gentle contours,
  with a lawyer-confirmation icon at the frontage."
- **fig-13-case-c-planning — REDRAW figure-36** (`md:1561`). Zone, frontage, well and septic
  assumptions, and three written questions for municipal planning staff. Alt (original): "Parcel C
  planning map shows zone, frontage, well and septic assumptions and three written questions for
  municipal planning staff." (The three questions are written only from `md:1557` — exact frontage,
  lot and intended-use/approval questions — not invented.)
- **fig-13-case-c-screening — REDRAW figure-37** (`md:1571`). Searched layers, no highlighted
  overlap, coverage limits and an inspection handoff; "No mapped overlap found is a bounded result."
  Alt (original): "Physical-screening map for Parcel C shows searched layers, no highlighted overlap,
  coverage limits and an inspection handoff."
- **fig-13-known-unresolved-professional — REDRAW figure-38** (`md:1591`). Columns: Known (dated,
  cited facts and bounded observations); Unresolved (questions the current evidence cannot answer);
  Professional (the person or authority qualified to answer next); separate box: Decision — the
  bidder owns the choice and its consequences. Designed to print as a reusable worksheet (it is the
  only figure also offered as a blank form in Appendix C; the blank form carries no new claims).
  Alt (original): "Final summary sheet with columns for known facts, unresolved questions and
  professional handoffs, plus a separate box stating that the bidder owns the decision."

---

## Figure index (original → textbook)

| Original | Textbook id | Treatment | Ch |
|---|---|---|---|
| figure-01 | fig-01-auction-morning | KEEP | 1 |
| figure-02 | fig-01-municipal-methods-map | REDRAW | 1 |
| figure-03 | fig-01-two-clocks | REDRAW | 1 |
| figure-04 | fig-02-packet-anatomy | REDRAW | 2 |
| figure-05 | fig-02-identifier-ladder | REDRAW | 2 |
| figure-06 | fig-02-reconcile-the-packet | REDRAW | 2 |
| figure-07 | fig-03-redeemable-route | REDRAW | 3 |
| figure-08 | fig-03-nonredeemable-route | REDRAW | 3 |
| figure-09 | fig-04-evidence-desk | KEEP | 4 |
| figure-10 | fig-04-source-authority-ladder | REDRAW | 4 |
| figure-11 | fig-04-beyond-the-packet | REDRAW | 4 |
| figure-12 | fig-04-five-evidence-labels | REDRAW | 4 |
| figure-13 | fig-06-case-a-orientation | REDRAW | 6 |
| figure-14 | fig-06-case-a-identity | REDRAW | 6 |
| figure-15 | fig-06-case-a-access | REDRAW | 6 |
| figure-16 | fig-06-case-a-planning | REDRAW | 6 |
| figure-17 | fig-07-case-a-screening | REDRAW | 7 |
| figure-18 | fig-07-case-b-orientation | REDRAW | 7 |
| figure-19 | fig-08-case-b-identity | REDRAW, moved 7→8 | 8 |
| figure-20 | fig-07-case-b-access | REDRAW | 7 |
| figure-21 | fig-08-case-b-planning | REDRAW, moved within 8 | 8 |
| figure-22 | fig-07-case-b-screening | REDRAW, moved 8→7 | 7 |
| figure-23 | fig-07-negative-search-beam | REDRAW | 7 |
| figure-24 | fig-08-title-encumbrance-possession | REDRAW | 8 |
| figure-25 | fig-08-occupied-property-handoff | REDRAW | 8 |
| figure-26 | fig-09-inverness-ratio-distribution | REDRAW | 9 |
| figure-27 | fig-09-fifty-thirtyfive-thirtyone | REDRAW | 9 |
| figure-28 | fig-09-municipal-result-comparison | REDRAW | 9 |
| figure-29 | fig-09-all-in-cost-stack | REDRAW | 9 |
| figure-30 | fig-10-auction-versus-tender | REDRAW | 10 |
| figure-31 | fig-11-certificate-holder-calendar | REDRAW | 11 |
| figure-32 | fig-12-deed-is-a-beginning | REDRAW | 12 |
| figure-33 | fig-13-case-c-orientation | REDRAW | 13 |
| figure-34 | fig-13-case-c-identity | REDRAW | 13 |
| figure-35 | fig-13-case-c-access | REDRAW | 13 |
| figure-36 | fig-13-case-c-planning | REDRAW | 13 |
| figure-37 | fig-13-case-c-screening | REDRAW | 13 |
| figure-38 | fig-13-known-unresolved-professional | REDRAW | 13 |
| figure-39 | fig-10-payment-readiness-clock | REDRAW | 10 |
| figure-40 | fig-12-surplus-proceeds-route | REDRAW | 12 |
| figure-41 | fig-05-map-layer-overview | KEEP | 5 |
| figure-42 | fig-05-province-data-licence | KEEP | 5 |
| figure-43 | fig-05-current-parcel-browser | KEEP | 5 |
| figure-44 | fig-05-civic-address-search | KEEP | 5 |
| figure-45 | fig-05-current-parcel-evidence | KEEP | 5 |
| figure-46 | fig-05-aerial-and-property-boundaries | KEEP | 5 |
| figure-47 | fig-05-roads-water-context | KEEP | 5 |
| figure-48 | fig-05-geology-resources | KEEP | 5 |
| figure-49 | fig-05-historical-outcomes-overview | KEEP | 5 |
| figure-50 | fig-05-historical-outcome-sheet | KEEP | 5 |
| figure-51 | fig-05-combined-parcel-research | KEEP | 5 |
| figure-52 | fig-05-buildings-assessment | KEEP | 5 |
| figure-53 | fig-05-flood-hazard-evidence | KEEP | 5 |
| figure-54 | fig-05-cbrm-outcome-unknown | KEEP | 5 |

New (24): fig-01-pre-sale-timeline, fig-01-whose-rules, fig-02-two-catalogue-keys,
fig-02-source-state-labels, fig-03-two-parcels-two-endings, fig-04-four-destinations,
fig-04-handoff-matrix, fig-05-current-vs-historical, fig-05-six-part-note, fig-05-research-chain,
fig-06-independent-gates, fig-07-three-records-one-yard, fig-07-coastal-scenario,
fig-07-positional-uncertainty, fig-07-result-states, fig-08-deed-effect,
fig-08-manufactured-home-records, fig-09-build-backward, fig-09-tax-eligibility-branches,
fig-10-sale-state-changes, fig-11-approved-repair-chain, fig-11-redemption-ledger,
fig-12-three-clocks, fig-13-three-endings.

Per chapter: Ch1 5 · Ch2 5 · Ch3 3 · Ch4 6 · Ch5 17 · Ch6 5 · Ch7 9 · Ch8 6 · Ch9 6 · Ch10 3 ·
Ch11 3 · Ch12 3 · Ch13 7 = 78.

## Figure review gate (applies in the drawing phase)

For each REDRAW and NEW figure, a reviewer checks: every label traces to the listed facts and lines;
no fictional value looks like a real PID/AAN; the original figure's source line is in the credit;
evidence-state colours have their greyscale cue; text ≥ 11 px at print size; alt text says what a
sighted reader learns, not what the picture looks like. Figure checks are part of the claims ledger
(see `review/claims-ledger-plan.md`, section F).
