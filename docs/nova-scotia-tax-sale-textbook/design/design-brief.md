# Design brief: Beyond the Tax-Sale Packet — Textbook Edition

9 October 2026 (planning phase 1). A calm, beautifully set textbook edition (PDF and EPUB) of Dan
Fakkeldy's *Beyond the Tax-Sale Packet: How Nova Scotia Municipal Auctions Really Work*, rewritten
for the page from the governed-final audio-first manuscript. Readers will use it to understand
how a Nova Scotia property reaches a municipal tax sale, what each record in a sale packet can
and cannot establish, what a purchaser takes on at each legal stage, and when a question belongs
to a lawyer, surveyor, planner, insurer, tax adviser or other professional.

The source of every fact is the canonical manuscript
`books/beyond-the-tax-sale-packet/beyond-the-tax-sale-packet.md` (cited in these plans as
`md:LINE`) and its development packet `docs/nova-scotia-tax-sale-book/` (official-source register
`research/sources.md`, claim IDs in `research/evidence-notes.md`). Both are frozen and are read,
never edited. Nothing in the textbook may add, change or drop a factual, legal, numeric or dated
claim; doubts go to `review/flagged-claims.md`, not into silent fixes.

## Readers and editions

- **Primary readers:** Nova Scotians who are curious about, or are considering taking part in, a
  municipal tax sale. They know ordinary real-estate listings but not tax-sale law, land records
  or auction procedure (the original's stated beginner, `research/brief.md`).
- **Secondary readers:** students, researchers, journalists, municipal staff and advisers who
  want a source-disciplined account of the process and a model of careful record research.
- **Reading situation:** printed at home on letter paper and read with a pencil; read as a PDF on
  a laptop or tablet; read as an EPUB on a phone or e-reader. Many will dip into one chapter
  (for example, the certificate-holder months) rather than read straight through, so every
  chapter must stand on its own, and every page explains its own abbreviations.
- **What readers should be able to do afterwards** (restating the original's learner outcome and
  coverage ledger):
  1. Trace the path from unpaid taxes to a tax deed, naming each legal stage and the document
     that marks it.
  2. Read a sale notice field by field and route each identifier (lien number, AAN, PID, address,
     assessment, recovery amount, redemption marker) to the record system it belongs to.
  3. Keep a dated source ledger that preserves disagreements between official records.
  4. Use a public map as a question machine: notice → parcel → context → unknowns → handoff,
     writing bounded notes that keep source, date, observation, limitation, unknown and next
     authority together.
  5. Classify each unknown as verified, professionally verifiable, priceable or no-go, and
     explain why one no-go governs a file.
  6. Separate visible access from legal access, frontage, zoning and approval; title from
     possession; a negative search from a clean bill of health.
  7. Build an all-in cost and a written maximum bid backward from a defined use, and check
     payment readiness before the event.
  8. Operate the certificate-holder months lawfully, keep a redemption-ready ledger, and know what
     changes (and what does not) when a deed is registered.
- **Editions:** one public edition only, in two formats (PDF via the textbook engine, and EPUB).
  There is no private edition: the original is public-safe and this edition draws on nothing
  else. The engine's `editions` block in book.yaml will define a single `public` edition with a
  forbid list (below); no `private_mark`, no `.only` blocks.
- **What the edition must leave out, and why:** everything the original deliberately left out
  (development packet README, "What is deliberately absent"):
  - assessed-owner names, occupant details, owner-bearing municipal extracts;
  - any PID, AAN, address or coordinate of a live property beyond those the original itself
    prints (PIDs `50292390`, `50308311`, `00542589`, `15234636`; AAN `00616672`; the
    municipal location "Southside River Denys Road, Valley Mills"; and the place names visible
    inside the kept screenshots and their original alt text);
  - the location of the author's recreational gold-panning brook (anonymous, location-free by
    Dan's explicit approval: no brook, home location, PID or coordinates);
  - Property Online screens, plans, registry documents or subscription-derived extracts;
  - live-property scores, rankings, maximum bids or recommendations;
  - internal pricing, possible-service planning notes, and private renderer artifacts.
  - Proposed forbid list (regexes) for book.yaml, added in the build phase:
    - `"\\b(?!50292390\\b|50308311\\b|00542589\\b|15234636\\b|00616672\\b)\\d{8}\\b"`: any
      eight-digit identifier other than the five the original prints;
    - `"(?i)brigend"`: the mine-record name on a development-packet atlas card, which the
      original book never prints;
    - `"(?i)11064 highway"`: the civic address visible inside a kept screenshot, which the
      original's text never prints and the textbook must not add;
    - `"(?i)assessed owner:\\s*[A-Z]"`: guards against an owner name after a field label.
    The PID pattern is checked against legitimate numbers in the build phase (none are expected:
    money is printed with `$` and commas, dates with words).

## Credibility rules (from the original's verification boundary and disclaimer)

These are binding on text, figures, captions, questions and answers.

1. **Educational only.** Print the original's disclaimer verbatim in "About this book": "The
   material is educational only. It is not legal, tax, investment, title, surveying, appraisal,
   access, environmental, insurance, planning, tenancy or construction advice. Municipal lists and
   procedures change. Always verify the current municipal notice, statute and event terms, and use
   qualified professionals for a live property decision."
2. **Screening is not proof.** The original's verification boundary: its status "does not convert
   map screening evidence into proof of access, title, condition, value, permission or
   buildability." No caption, objective, summary or answer may say otherwise.
3. **Date every fact.** The legal and event research was refreshed 19–22 July 2026 (core law and
   Inverness event 19 July; chapters 6–12 sources 20 July; mineral sources and screenshots 22 July).
   The cover reads "Facts as of July 22, 2026." Event-specific facts (Inverness 11 August 2026,
   CBRM 21 July 2026, Pictou April 2026, Chester's 2026 statement, foreign-buyer rule dates) are
   framed as dated examples, never as timeless rules.
4. **Provincial law versus local practice.** The Municipal Government Act frame (outside Halifax)
   and the Halifax Regional Municipality Charter are never blended; one municipality's
   instructions (CBRM's HST rule, CBRM's ID and bidding cards, Inverness's $200 registration
   amount, Halifax's fee categories) are never generalized.
5. **No recommendations, scores or valuations** of any parcel, real or fictional. Card rating
   meters from the engine are **not used** in this book: a meter beside a parcel would read as a
   score.
6. **Composite cases are labelled.** Every fictional parcel or person is identified as a
   composite at first appearance in each chapter and in every case box and figure caption.
7. **Never speak for people outside the room.** Owners, occupants, heirs and interest holders are
   treated as people with rights; no self-help, no eviction how-to, no portrayal of redemption as
   defeat.
8. **Preserve disagreements.** Where official sources disagree (45 vs 44 sheets; two recovery
   amounts; 50/35/31 counts; $608,693.21 surplus vs row arithmetic), show both and say the
   municipality answers.
9. **Formal references live in source notes.** Section numbers and document IDs appear only in
   `::: source` notes, taken from `research/evidence-notes.md` and `research/sources.md`, never
   invented. The running text names statutes and bodies as the original does.
10. **Province licence attribution survives.** Every kept screenshot that shows NS Aerial or NSPRD
    views keeps its in-image attribution, and the caption repeats: "Contains information obtained
    under license from the Province of Nova Scotia which is provided without warranty or
    liability for errors or omissions."

## Direction: "Harbour ledger"

A calm, trustworthy civic textbook, closer to a good field guide or a provincial
records-office handbook than to an investment manual. Evidence first, no shouting, generous white
space. Nova Scotia in the materials, not in clip art: the palette is drawn from a Cape Breton
harbour on an overcast morning (deep sea-teal water, spruce, granite, buoy red, tartan gold), and
the figures borrow the quiet linework of survey plans and registry index cards.

**The one memorable thing: the File Note.** The original's bounded research notes (the block
quotes at `md:561`, `605`, `683`, `741`, `777`, `799`, `831–833`, `849`, `859`, `899`, `923–927`,
`933`, `973`, `1031`) become a signature component styled like a registry index card: a small
tab on top with the case name and "File note", a thin teal top rule, and labelled rows in the rail
style — **Source · Date · Observation · Limitation · Unknown · Next authority** (the six parts the
original teaches at `md:603–607`). Where the original note does not use all six parts, only the
parts it contains are printed (no invented content). Its companion is the **research-chain
strip**: five linked tabs, *notice → parcel → context → unknowns → handoff* (`md:667–669`), printed
small on every chapter opening with the link(s) that chapter develops filled in.

- White paper (prints cleanly at home), near-black ink, one accent colour (harbour teal), one
  caution colour (buoy red). Everything reads in greyscale: evidence states carry a shape or line
  style as well as a colour.
- No gradients, no emoji, no drop shadows, no rounded "cards with a coloured left border", no
  photographs of real properties, no stock imagery of gavels or dollar signs.

## Page grid

- US Letter, 8.5 × 11 in = 816 × 1056 px at 96 px/in, portrait (`page: {size: letter}`).
- Margins 72 px left and right; running head at 36 px, body from 92 px.
- Rail layout (`layout: {body: rail}`): 672 px content; 144 px side rail, 24 px gutter, 504 px main
  column (65–70 characters a line). Side heads, learning-objective and key-term labels hang in the
  rail. Tables, figures, case boxes, File Notes and the footer span the full width.
- The per-page glossary footer ("Words on this page") sits above the folio, computed per page; at
  least 20 px clear above it.
- Figures: drawn at 672 px (7 in) content width as SVG; heights chosen from a small set (1/3, 1/2,
  2/3 page) so pages keep rhythm. The 14 kept screenshots (16:9) print at full content width
  (7 × 3.94 in) with optional magnified insets (see chapter plan and open questions).

## Typography

- Serif for reading and display: **Source Serif 4** (static cuts at optical size 12 for text, 48 for
  display). Sans for everything small or functional, and for all figure labels: **Atkinson
  Hyperlegible Next** (Braille Institute; made for low-vision readers). Both are the engine's tested
  defaults and are under the SIL Open Font License; a civic book read by people of all ages benefits
  from the hyperlegible sans in tables, footers and diagrams.
- Scale (px at 96 px/in): chapter title 38 serif 600; section head 20 sans 700; subhead 17 sans 700;
  body 15.33 (11.5 pt) / 1.47, ragged right, no hyphenation; tables 14 sans / 1.38; footer 12.67
  (9.5 pt) / 1.36; labels, captions and running head 12 (9 pt); figure labels never below 11 px at
  print size (≈ 8.25 pt).
- No all-caps set in CSS (it would hide real abbreviations from the footer check). Small caps only
  for the File Note tab, typed in mixed case.

## Colour tokens

| Token | Hex | Use |
|---|---|---|
| ink | #1d1c1a | body text |
| ink2 | #4a4843 | secondary text (≥ 4.5:1 on white) |
| rule | #cfcac0 | hairlines, table rules, File Note card edge |
| accent (harbour teal) | #1f5560 | headings, side heads, chain strip, figure strokes |
| accent_tint | #e6eef0 | table heads, notes, File Note ground |
| accent_mid | #9db8bf | secondary figure fills, chain-strip empty links |
| caution (buoy red) | #a33b28 | careful panels, no-go state |
| caution_tint | #f6e8e3 | caution panels |
| granite | #6b6a66 | neutral figure elements, "not a survey" stamps |

Evidence-state palette for figures. It keeps the original figures' visual grammar
(`research/visuals.md`, "Visual grammar") so redraws mean the same thing, retuned for print and
paired with a non-colour cue:

| State (original colour) | Book hex | Greyscale cue |
|---|---|---|
| Municipal fact (navy) | #24395a | solid fill tab |
| Verified added public record (teal) | #1f6b6e | solid outline |
| Screening clue / visual interpretation (amber) | #b07d17 | dotted outline |
| Unresolved / professional verification (magenta) | #7a3e6e | dashed outline + "?" glyph |
| No-go until resolved (red) | #a33b28 | heavy outline + bar glyph |
| Process complete / reconciled (green) | #2f5e46 | check glyph |

Contrast of each text-bearing hex against white to be verified (≥ 4.5:1) when book.yaml is set.

## Components

Engine components used as they are (`references/authoring.md`): chapter openings with `label`,
`kicker`, `intro`; `##`/`###` headings; rail side heads; `note` and `careful` panels; `source` notes;
full-width tables; figures; `keep`; the glossary and footer.

New components to build in the design phase (each a fenced-div class in `Blocks.division`, with its
text covered by `check_source.py`; until built, each falls back to the existing mark shown):

| Component | Mark (planned) | Fallback now | Breaks |
|---|---|---|---|
| Learning objectives | `::: {.objectives}` list | `::: {.rail label="You will learn to"}` | atomic |
| Key terms | `::: {.keyterms}` list of terms | `::: {.rail label="Key terms"}` | atomic |
| Research-chain strip | `::: {.chain links="notice,parcel"}` | a one-line note | atomic, on opener |
| Worked case box | `::: {.case name="Harbour Road"}` | `::: {.note label="Composite case: Harbour Road"}` | container (splits between children) |
| File Note (signature) | `::: {.filenote case="Birch Point Road"}` with `**Source:**`-style lead words | blockquote | atomic if < 700 characters, else container |
| Quick recall | `::: {.recall}` | `::: {.note label="Quick recall"}` | atomic |
| Check your understanding | `::: {.check}` numbered list with links to answers | `## Check your understanding` + list | splits between items |
| Chapter summary | `::: {.summary}` | `## Summary` + list | splits between items |

- Chapter openings: big number, kicker carrying the original chapter title, the textbook title, a
  short grey introduction, the chain strip, objectives and key terms.
- Tables: sans 14 px, header row on the accent tint, rows split across pages with the header
  repeated.
- Case boxes: accent-tint ground, a small "Composite case — not a real property" line under the
  case name, never a meter or score.
- Figures: number ("Figure 5.3"), short title in bold sans, one-sentence caption stating what the
  figure shows and its limit, credit/attribution line; `{#fig-… alt="…"}` on every image.

## Textbook apparatus (what every chapter carries)

1. Opening: learning objectives (3–5), key terms, chain strip.
2. Side-head rails in the running text ("The idea", "Why it matters", "In practice", "Careful",
   "Quick recall").
3. Worked case boxes for the composite cases: Harbour Road (with Quarry Lane), Birch Point Road,
   Maple Ridge (Case A plates), Breakwater Lane and Foundry Street/Harbour Park (Case B plates),
   Cedar Street with Maya, Elena's surplus file, and Alder Crossing, Union Workshop and Meadow Line
   (Case C plates).
4. Source notes at the end of each section linking the section's claims to the original's official
   sources (sources.md entries and evidence-note IDs).
5. Chapter summary (5–8 bullets restating claims already in the chapter).
6. Check your understanding (4–6 questions), answers in Appendix A.
7. Back matter: Appendix A (answers), Appendix B (index of statutes and official sources, by
   provision and chapter), Appendix C (figure list and credits), glossary, Sources and credits.

## EPUB notes (for the engine's EPUB output, being added separately)

- Same Markdown source; no EPUB-only text. Rails become run-in labels before their block; File
  Notes and case boxes become `aside` blocks with the same labels.
- Per-page footers do not exist in an EPUB: abbreviations are expanded at first use in each chapter
  and the glossary is linked. (Engine question; see open questions.)
- Figures ship as SVG with a PNG fallback at 2× and the same alt text; screenshot insets ship as a
  second image, not as an overlay.

## What the book must never do

- Never invent or "correct" a fact, section number, date, amount or source; flag doubts instead.
- Never present a parcel (real or fictional) as a bargain, a recommendation or a score.
- Never describe a map, overlay, empty result, assessment or historical bid as proof of boundary,
  access, condition, safety, value, permission or buildability.
- Never describe self-help (locks, utilities, belongings, rent demands, entry) as an option.
- Never print an owner, occupant, or the location of the gold-panning brook; never add a live PID,
  AAN or address beyond those the original prints.
- Never generalize one municipality's event terms to the province, or Halifax's to the MGA frame.
- Never reproduce Property Online material.
