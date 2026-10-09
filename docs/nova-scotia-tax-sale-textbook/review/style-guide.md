# Style guide: textbook rewrite

For the chapter rewrites of *Beyond the Tax-Sale Packet* (textbook edition). Read with
`design/design-brief.md`, `design/chapter-plan.md`, `review/claims-ledger-plan.md` and the engine's
`cs/textbook-pdf/references/authoring.md`.

## 1. What changes and what does not

The original was written for the ear: long, rhythmic paragraphs, repetition for a listener who
cannot glance back, spelled-out numbers, frequent recaps after "interruptions", and a recurring
rhetorical pattern of denial ("X is not Y"). The textbook is written for the eye: shorter
paragraphs, structure the reader can scan, numbers as numerals, and apparatus that does the
recapping.

What never changes: every claim, qualifier, date, amount and source in the claims ledger; the
composite cases and their facts; the privacy boundaries; the author's first-person panning story
(kept in his voice, `md:623`); the book's stance that the researcher organizes questions and the
bidder owns the decision.

## 2. Voice

- **Plain, calm, exact.** Say what a record shows, who made it, when, and what it cannot establish.
  Prefer the concrete noun ("the August 11, 2026 Inverness packet") to the abstract ("the source").
- **Lead with the positive statement, then the limit.** Original: "A parcel shape is not a boundary
  survey." Textbook: "A parcel shape shows where the land-record system places the parcel. It is not
  a boundary survey." Keep the denial when the denial *is* the lesson, but no more than one "X is
  not Y" sentence in a row; turn runs of them into a two-column table (record → what it does not
  establish).
- **Fewer rhetorical questions.** Convert "Is that line trying to persuade you? No." into a
  statement. Questions belong in "Check your understanding", "Quick recall" and the planning-call
  script, where the original uses them as genuine questions to ask.
- **No audio signposting.** Remove "listener", "road listener", "Return to…", "Now imagine an
  interruption", "here is the retrieval test", "the concrete reset is". Their content survives: the
  recovery questions become a "Quick recall" box; recaps become chapter summaries.
- **Analogies stay, with their limits.** The original pairs each analogy with its limit (catalogue
  keys `md:139`, relay baton `md:291`, door and key `md:717`, flashlight `md:911`, coat check
  `md:997`, iceberg `md:1103`, finish line `md:1237`). Keep both halves; set them in a rail labelled
  "A way to picture it".
- **Active voice, named actors.** "The treasurer prepares and registers the certificate," not "the
  certificate is registered". Actors and their authority are the subject of the book.
- **Sentences:** average 18–22 words, few over 35. **Paragraphs:** 2–5 sentences. One idea per
  paragraph.
- **Reading level:** about grade 10–11 (Flesch–Kincaid) for running text; legal terms are
  unavoidable, so define them at first use (bold) and let the footer and glossary carry them.
  Do not simplify a legal rule into a different rule to lower the score.
- **Respect for people outside the room.** Owners, occupants, heirs and interest holders are
  people with rights. No "distressed", "bargain", "hidden gem", "deal", "flip", "steal". Redemption
  is "the process working" (`md:1367`), never a loss to be avoided.

## 3. Spelling, numbers and dates (consistent with the original)

- **Canadian spelling as the original uses it:** -our (neighbour, colour, favourable, behaviour);
  -re (centre, metre); -ize (organize, recognize, authorize, characterize); licence (noun) / license
  (verb, and inside the Province's quoted attribution, which is quoted exactly: "obtained under
  license"); cheque; defence; program; "percent" as one word (the original's form); "right-of-way",
  "tax-sale" (adjective), "tax sale" (noun), "fee simple", "Plus Code", "land-lease community".
- **Proper names exactly as printed:** Municipal Government Act; Halifax Regional Municipality
  Charter; Marketable Titles Act; Mineral Resources Act; Property Online; Property Valuation Services
  Corporation (PVSC); Cape Breton Regional Municipality (CBRM); Eastern District Planning Commission;
  Plan Inverness; St. Peter's Parish Hall; NS Marks The Spot; NS Aerial; Nova Scotia Property Records
  Database (NSPRD); Coastal Hazard Map; Abandoned Mine Openings inventory; Personal Property Registry;
  Touquoy; DDV Gold; Forrest Higgins.
- **Numbers:** numerals for 10 and above, and always for money, percentages, ratios, data counts
  and day periods ("14 days", "60 days", "30 consecutive days", "45 lien entries", "5 withdrawn");
  words for one to nine otherwise, including month and year periods ("six months", "three business
  days", "six years"), and numerals from 10 ("20 years"). Money with `$`
  and commas ($608,693.21; $4,000). Ratios "4.53 times" in prose, "4.53×" in figures and tables.
  Approximations keep their word: "about 5.12 mapped acres", "roughly fifty metres" (or "roughly
  50 metres"; see flag F-07).
- **Dates:** "August 11, 2026" (month day, year, as the original). Event facts carry their date in
  the same sentence or the paragraph's first sentence. Present-tense statements about live events
  are dated: "As of July 22, 2026, the Inverness page described…".
- **Identifiers** in code font, as printed: PID `50292390`, AAN `00616672`. Only the five the
  original prints may appear.

## 4. The composite cases

- Name the case and say it is fictional at its first appearance in every chapter ("the fictional
  Maple Ridge sliver", as the original does) and in every case box ("Composite case — not a real
  property") and figure caption.
- Use the original's cast and facts only: Harbour Road (with Quarry Lane), Birch Point Road, Maple
  Ridge, Breakwater Lane, Foundry Street, Harbour Park, Cedar Street and Maya, Elena, Alder Crossing,
  Union Workshop, Meadow Line; the fictionalized Port Hood room. Do not give them owners, real
  places, real-looking identifiers or new facts; "might", "suppose" and "imagine" scenarios stay
  hypothetical.
- Case boxes hold the case narrative; the running text holds the rule. A reader who skips every
  box still gets every rule; a reader who reads only the boxes still sees the case end.
- The Case A/B/C figure plates are labelled "Parcel A/B/C" as in the original; captions say which
  case's discussion they illustrate without renaming the parcel (open question Q5).
- Never add a score, rank, bargain language or a recommendation to a case, including Meadow Line
  ("the most research-ready of the three evidence files… not a property ranking", `md:1547`).

## 5. Markdown conventions for the engine

Chapter files live in `src/chapters/NN-slug.md` (pandoc Markdown). Front matter:

```markdown
---
label: 5
kicker: Chapter 5 · The map is a question machine
intro: >-
  One or two sentences in grey under the title (no new claims; restate the chapter's purpose).
running_head: The map as a research tool
---

# Using the Map as a Research Tool
```

Marks (from `references/authoring.md`; planned components in the design brief, with fallbacks):

| Need | Write | Notes |
|---|---|---|
| Section / subsection | `## The first clock` / `### Two catalogue keys` | sentence case; no numbers typed by hand |
| Side head | `::: {.rail label="The idea"}` … `:::` | labels from a fixed set: The idea · Why it matters · In practice · A way to picture it · Quick recall · Careful (use the panel instead where it is a warning) |
| Key term at first use | `**tax lien**` + an entry in the glossary | bold only at the defining use |
| Objectives | `::: {.objectives}` + numbered list `:::` | fallback `::: {.rail label="You will learn to"}` |
| Key terms list | `::: {.keyterms}` + bullet list `:::` | fallback `::: {.rail label="Key terms"}` |
| Case box | `::: {.case name="Maple Ridge"}` … `:::` | fallback `::: {.note label="Composite case: Maple Ridge"}`; first line inside: "Composite case — not a real property." |
| File Note | `::: {.filenote case="Birch Point Road"}` then one paragraph per part, each starting `**Source:**`, `**Date:**`, `**Observation:**`, `**Limitation:**`, `**Unknown:**`, `**Next authority:**` | only the parts the original note contains; the original's note text is kept verbatim except line breaks; fallback: a `>` blockquote |
| Quick recall | `::: {.recall}` + numbered questions with their short answers `:::` | fallback `::: {.note label="Quick recall"}` |
| Warning | `::: careful` (or `::: {.careful label="Do not"}`) | at most one per page spread |
| Aside from the author | `::: {.note label="From the author"}` | the panning story only |
| Source note | `::: source` at the end of each `##` section | publisher, title, date; evidence IDs; section numbers only from evidence notes |
| Table | pipe table with a header row | short cells; a table compares, the prose explains |
| Figure | `![**Figure title.** One-sentence caption stating what it shows and its limit. Credit.](../assets/figures/fig-05-research-chain.svg){#fig-05-research-chain alt="Full alt text."}` | on its own line; the bracket text is the caption, `alt` is separate; id = file stem |
| Figure reference | `[Figure 5.3](#fig-05-research-chain)` | number assigned at build; never "the figure below" |
| Cross-reference | `see [section 3.2](#…)` | for merged claims (ledger rule) |
| Summary | `::: {.summary}` + bullets `:::` | fallback `## Summary` |
| Questions | `::: {.check}` + numbered list, each ending `[Answer](#ans-05-3)` `:::` | answers in `src/chapters/97-answers.md` under `### 5.3 {#ans-05-3}` |
| Identifiers | `` `50292390` `` | only the five permitted |
| Web addresses | in source notes and Sources only | printed as in sources.md |

Rules from the engine that matter for prose:

- Write lead-ins ("The file needs:") as their own paragraph; the paginator keeps them with what
  follows. No manual line breaks or spacing.
- Fenced divs nest; `:::` closes the innermost. A div that opens with a heading becomes `<section>`;
  the build treats both alike.
- Every abbreviation in text, tables, captions, running heads and the glossary itself needs a
  glossary entry; keep abbreviations off the cover.
- Pandoc writes `label` as an attribute but other names as `data-…`; any new component must read
  both (lessons.md). Text in attributes (rail labels, case names) must be added to
  `check_source.py`'s `attr_texts`.
- No all-caps in source text for emphasis: it confuses the footer's abbreviation check.

## 6. Formal references

Running text names the statute and the body ("the Municipal Government Act", "Inverness County's
December 2025 FAQ"). Section numbers, document numbers and URLs go in `::: source` notes and
Appendix B. Example source note:

```markdown
::: source
Municipal Government Act, consolidated to April 9, 2026 (checked July 19, 2026): tax lien, s. 133;
sale eligibility, s. 134; notices and title search, ss. 137–140; advertisement, s. 142 (evidence
notes LAW-001 to LAW-004). Inverness County, Property Tax Sales page and August 11, 2026 packet
(refreshed July 20, 2026). Chester, Tax Sales page.
:::
```

## 7. Checklist before a chapter goes to review

- Ledger complete and balanced; no new statements.
- Each `##` section ends with a source note.
- Objectives, key terms, summary and questions present; every question has an answer anchor.
- Every figure has id, caption, credit and alt text; numbers in figures match the ledger.
- Composite cases labelled; no forbidden identifiers; disclaimer language intact where the original
  has it.
- No "listener", no "road", no bare "not X, it's Y" runs; rhetorical questions converted.
