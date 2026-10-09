# Open questions for Dan

Planning phase 1, 9 October 2026. Nobody was available to ask, so each question has a default
decision that the next phases will follow unless Dan changes it. Flagged factual concerns are in
`review/flagged-claims.md` (F-ids); this file holds decisions about form, scope and wording.

| # | Question | Default decision | Why |
|---|---|---|---|
| Q1 | Keep the original chapter titles or retitle for a textbook? | New descriptive titles ("Reading the Notice", "Title and Possession"…), with the original title kept as each chapter's kicker ("Chapter 8 · Title is not possession"). Same 13 chapters, same order. | Textbook readers scan the contents for topics; the kicker keeps continuity with the audiobook. |
| Q2 | Credit line. The original says "By Dan Fakkeldy. Written, researched, reviewed and produced with OpenAI Codex (GPT-5)". | Cover: "Dan Fakkeldy". About page: "Textbook edition rewritten and designed with Claude (Anthropic) from the 2026 governed-final edition, which was written, researched, reviewed and produced with OpenAI Codex (GPT-5), using official Nova Scotia and municipal sources." | Accurate about both tools; keeps the original credit verbatim. |
| Q3 | Cover art: reuse *The Packet Lifts*? | Reuse the selected portrait cover art unchanged as the engine's cover band (cover art is frozen; no edits, no crop beyond the band's aspect if the engine requires one — if it does, ask). Kicker "Textbook edition". | Continuity, and cover art is frozen. |
| Q4 | The facts are dated July 2026; the August 11, 2026 Inverness sale has since happened. Refresh? | No refresh in this edition. Cover: "Facts as of July 22, 2026." Present-tense event statements are framed "as of July 22, 2026". A separate refresh project can follow. | The rule is to preserve every claim; a refresh means new research and new claims. |
| Q5 | The Case A/B/C plates do not line up neatly with the named cases: figure-17 (Parcel A, screening) sits in the Breakwater Lane chapter; figure-19 (manufactured-home question) sits in Ch 7; figure-22 (former-use registry clue) sits in Ch 8. | Keep every plate's content and "Parcel A/B/C" labels. Move figure-19 to Ch 8 (Harbour Park) and figure-22 to Ch 7 (registry search); move figure-21 within Ch 8 to the occupied-building section; keep figure-17 in Ch 7 captioned "Case A, plate 5: the screening layers used for the Breakwater Lane discussion". Captions never rename a parcel. | Each plate then sits beside the text it teaches; no figure content changes. |
| Q6 | Figure-12's five labels vs the text's four destinations (F-10). | Keep both. Caption figure-12 as labels for the strength of an observation (its own caption's words); the new four-destinations figure handles unknowns. | Both are the original's; the captions stop readers conflating them. |
| Q7 | Use the clean source art for figure-01 and figure-09 (no slide tag or baked caption)? | Yes, if the source art matches the published artwork; otherwise use the published PNG. | The baked "FIGURE-01" tag would clash with the book's numbering. |
| Q8 | Figure-02 is not a geographic map (F-01). What boundary data for the redraw? | An open-licence Nova Scotia municipal-boundary dataset, credited in the caption (preferably the Province's open data under the Open Government Licence – Nova Scotia, which the original packet already credits). Same seven labels. | Alt text promises a map of Nova Scotia; readers will look for their county. |
| Q9 | Add the older-arrears fork to the redrawn two-clocks figure (figure-03)? | Yes, as a dashed branch labelled "older-arrears route: no six-month redemption" (`md:201`, `md:259`). | Makes the figure consistent with Ch 2–3 text; the fact is the original's. |
| Q10 | Figure-51's original alt text names "Soapstone Mine Road", a real road with a current-notice parcel. | Keep the original alt text; do not repeat the name in captions or prose. | It is the original's own published text; no additional exposure. |
| Q11 | Index of statutes and sources: page numbers or section references? | Chapter and section references ("5.3"); page numbers later only if the engine gains automatic page references for arbitrary anchors. | The engine fills page numbers only for card targets today. |
| Q12 | Correct figure-11's alt text ("two-column" for a three-column image, F-11)? | Yes: "Three-column stack comparing…", otherwise unchanged. Record the original alt in the ledger. | Alt text should describe the image a blind reader is told about. |
| Q13 | NS Marks The Spot is the author's own project (repo `dfakkeldy/ns-marks-the-spot`, hosted at kinnokilabs.com). The original does not say so. Disclose? | Yes, one neutral sentence on the About page: "NS Marks The Spot, the public map used in Chapter 5, is the author's own project." No promotion. | Credibility rule: a textbook should disclose an author's interest in a tool it demonstrates. Needs Dan's approval because it is a statement the original does not make. |
| Q14 | Glossary entries the original never defines or expands: HST, PDF, FAQ expansions; "easement", "mineral tenure", "Mineral Resources Act" (named only in sources.md). | Include them, with definitions built only from the original's own statements (comments in `src/glossary-draft.yaml` mark them). The footer check requires every abbreviation to be expanded. | Required by the engine; kept minimal. |
| Q15 | May source notes carry details from the evidence notes that the running text omits (section numbers; "Nova Scotia Supreme Court"; Touquoy predating the 2016 Act; the s. 144 $5,000 penalty)? | Section numbers, source titles and dates: yes (that is what source notes are for). Substantive facts not in the running text: no — except identifying the court in the surplus source note as "Nova Scotia Supreme Court (evidence note LAW-014)" and noting the Touquoy evidence boundary, both because they prevent a misreading (F-05, F-12). The $5,000 penalty is not added. | Keeps the text's claims unchanged while making sources precise. |
| Q16 | The 14 screenshots are 2560 × 1440 and their panel text is tiny at 7 in wide. | Print each full width with pixels untouched; add one or two magnified insets cropped from the same PNG, outside the screenshot frame, and repeat the Province attribution in the caption. | Legibility without altering the original images. |
| Q17 | Answers to "Check your understanding": end of chapter or appendix? | Appendix A, linked from each question. | Requested in the brief; keeps chapters clean. |
| Q18 | Licence for the textbook. | Same as the original: Creative Commons Attribution 4.0 (repository content licence); fonts under the SIL Open Font License; Province attribution where required. | Consistency with the original package. |
| Q19 | Per-page glossary footers do not exist in an EPUB. | EPUB expands each abbreviation at first use per chapter and links terms to the glossary; the EPUB engine agent decides the mechanism. No EPUB-only text. | Same source, same claims. |
| Q20 | Length. | About 40,000–46,000 words of text (the original's 33,000 plus objectives, case boxes, summaries, questions, answers and source notes), roughly 170–200 letter pages with 78 figures. | Planning estimate for scheduling; not a target to pad toward. |
| Q21 | The author's first-person gold-panning story (`md:623`) in an otherwise third-person textbook. | Keep it in Dan's first person, in a "From the author" aside; brook unnamed. | It is approved, personal and location-free; recasting it would change its meaning. |
| Q22 | Audio "interruption/recovery" passages (`md:221–231`, `543–547`, `665`, `929`, `983`, `1035`, `1113`, `1215`). | Turn them into "Quick recall" boxes with the same questions and answers; delete only the audio framing ("road listener", "after an interruption"). | Their content is method; their framing is audio-only. |
| Q23 | Spelled-out numbers ("forty-five", "July twentieth"). | Numerals per the style guide; the ledger records both forms. | Print convention; values unchanged. |
| Q24 | Ch 8 flashes forward to a deeded case before Ch 9's pre-bid economics. Reorder? | No. Keep the original order and its explicit flash-forward framing (`md:949`, `md:1375`). | The order is part of the approved argument and the coverage ledger. |
| Q25 | Offer figure-38 (known / unresolved / professional) as a blank worksheet in an appendix? | Yes, a blank version with the same headings and no example content. | Useful to readers; adds no claims. |
| Q26 | Glossary terms that overlap ("redemption" inside "redemption marker"; "zoning" vs "zoning-confirmation letter"; "tax deed" vs "deed transfer tax"). | Keep both; check in the build phase how the engine resolves overlapping matches and narrow regexes if footers show the wrong sense. | The engine's lessons flag wrong-sense footers as a recurring review finding. |
| Q27 | Figure numbering. | "Figure 5.3" by chapter, assigned at build; ids stay `fig-05-…`. Cross-references always by link. | Standard textbook practice. |
| Q28 | Use the engine's card component (rating meters) for the composite cases? | No. Case boxes have no ratings, scores or meters. | A meter beside a parcel reads as a score, which the original forbids. |
| Q29 | Should the textbook include more of the packet's analysis (e.g. Inverness August 2026 total $342,793.85, median $3,412.09; CBRM illustrative pairs; Inverness mean 6.64×)? | No. Only claims the manuscript makes. | The task is a rewrite of the book, not a new edition of the research. |
| Q30 | Where the original repeats a rule across chapters by design (e.g. "the current municipal notice controls"). | Keep one full statement per chapter where the original has one; later repeats may shorten to a cross-reference. Never drop a chapter's only statement. | Chapters must stand alone for readers who dip in; the ledger records merges. |

## Orchestrator rulings (9 October 2026, overnight run)

- Q13: **Do not add** the NS Marks The Spot ownership sentence in this draft. It is a statement the original does not make; it is listed in the PR for Dan to decide.
- Q14: Standard expansions of common abbreviations (HST, PDF, FAQ) are allowed in the glossary; substantive new legal definitions are not.
- Q8: If an open-licence boundary dataset is not readily downloadable, draw figure-02 as a clearly labelled schematic ("not to scale") instead.
- All other defaults stand.

## Chapter 1 writer's decisions (9 October 2026)

- Q8 applied: the boundary data was readily downloadable, so figure-02 is redrawn on a true outline:
  Province of Nova Scotia, Municipality Boundaries (open data `7bqh-hssn`, Nova Scotia Open
  Government Licence), downloaded 2026-10-09, simplified by `figures/prep_ns_boundaries.py` into
  `figures/data/ns-municipal-units.json` (the 72 MB download is not kept). Boundaries are current
  as of the download, not July 2026; Sable Island is left out of the drawing. The caption credits
  the dataset. Kings keeps a solid dot with its own label "auction record" (legend: "auction (Kings:
  auction record)").
- Q7 applied: figure-01 uses the clean source art (`figures/source-art/figure-01-auction-morning-landscape-source.png`,
  identical artwork without the slide band), copied to `src/assets/figures/kept/fig-01-auction-morning.png`.
  Its baked title and caption moved into the textbook caption.
- Section 4 is titled "Halifax: a similar sequence under a different statute" (plan: "same sequence"),
  because `md:97` says only "recognizably similar".
- Figure-02's footer "Review candidate" is a production-status label and is not printed; "Verify
  sources • not a recommendation" moves into the caption.
- `design/figure-style.md`, `figures/svgkit.py` (embeds font subsets so SVGs render identically as
  `<img>` in Chrome and in EPUBs; preview fonts via `figures/fonts.conf`) and
  `review/tools/check_ledger.py` were created with Chapter 1 for later chapters to reuse.
- Answer anchors link to section ids (`#sec-01-…`) set on the chapter's `##` headings.

## Chapter 3 writer's decisions (9 October 2026)

- The four stage questions (`md:283–287`) are a Quick recall box whose answers are the leaking-roof
  answers from `md:287`, labelled "For the Harbour Road roof"; the protective questions of `md:275`
  became a list inside the case box.
- The certificate holder's powers and their boundaries (`md:269–271`) are a two-column table. The
  lead-in says "Each power or duty arrives with a boundary"; the two duty rows carry "—" (no
  boundary invented) and the insurance row points to the Careful panel.
- "(Chapter 11 returns to it)" added as a navigation pointer after the accounting-habit paragraph
  (`md:279`); the redemption-marker reference links to `#sec-02-redemption-marker`.
- figure-07's label "Treasurer issues and registers certificate" kept verbatim (F-23); no
  certificate drawn for Quarry Lane in the new figure (F-24).
- Figure-08's four question boxes are drawn in the unresolved style (dashed + "?"), per the plan;
  the original gave each a different colour without a meaning. The plan's label "Immediate deed
  describes timing, not readiness." is added beside the shorthand box.
- The §3.1 source note names the Intact Insurance pages (sources.md no. 31) with the limit
  sources.md records; the running text does not mention them (Q15).
- Tool issue: `review/tools/check_ledger.py NN` takes the first `NN-*.md`, which for 01, 02 and 03
  can be the engine's sample chapters (`01-writing.md`, `02-cards.md`, `03-checks.md`). Chapter 3
  was checked with a copy that selects the textbook chapter. Suggest removing the sample chapters
  from `src/chapters/` or making the tool exclude them.

## Chapter 2 writer's decisions (9 October 2026)

- fig-02-packet-anatomy keeps figure-04's own fictional values ($4,200 recovery, $68,000 assessment,
  lien 12) and masks only the eight-digit placeholders (F-23); the plan's "$4,000 / ••••• 421"
  variant was not used because it would change figure values and attach new facts to Harbour Road.
  The four callouts are the original's questions (Identity, Money, Legal route, Limits) rather than
  the plan's five-word field legend, which would have been new wording.
- fig-02-identifier-ladder keeps figure-05's structure (seven cards, then five struck conclusions for
  the whole chain) rather than pairing a conclusion with each card (F-24). Card labels keep
  "Location" as in the original (the plan said "civic address").
- Figure-04/05 colour coding is simplified: every field on a municipal sheet is drawn as a municipal
  record (navy tab), so no evidence-state colour appears without its meaning. Figure-06's three
  status cells keep amber with a dotted outline (screening state) as in the original.
- Figure order in the chapter: packet anatomy (2.1), two catalogue keys (2.2), identifier ladder
  (2.3), reconcile the packet (2.4), source-state labels (2.5).
- The Harbour Road routing sheet (md:175) is a two-column table (field → what it identifies); the
  "question beside it" in the plan is printed once as the lead sentence, since the original gives one
  question set for all fields.
- `review/tools/check_ledger.py` now takes the chapter file named in the ledger header, because the
  engine sample `src/chapters/02-cards.md` shares the `02-` prefix (Chapter 1's check is unchanged).
  The engine sample chapters (01-writing, 02-cards, 03-checks, 90-team-notes) still sit in
  `src/chapters/` and will need removing in the build phase.

## Chapter 4 writer's decisions (9 October 2026)

- Q12 applied: fig-04-beyond-the-packet's alt text says "Three-column stack…", otherwise the
  original's wording, followed by the three columns' labels. The original alt is in the Ch 4
  ledger (ch04-009).
- Q7 applied: fig-04-evidence-desk uses the clean source art
  (`figures/source-art/figure-09-evidence-desk-landscape-source.png`, same artwork as the published
  PNG without the slide band), copied to `src/assets/figures/kept/`. Its baked title "Build a
  traceable evidence file" became the caption title. Its alt text keeps "folders marked known,
  unresolved and professional" although the folder tabs are blank (flag F-25).
- fig-04-source-authority-ladder is drawn as a staircase with the original's state colours
  (imagery and map layers: screening, dotted; municipal record: municipal tab; registry / survey:
  dashed, as in the original's magenta; governing law: solid teal). The alt text's "question icons"
  are drawn as a small "?" beside each card's question.
- fig-04-four-destinations: priceable uncertainty has no colour in the evidence-state palette, so it
  is drawn in the accent teal with a heavier solid outline and a bounded-range glyph (|—|). Suggest
  adding this cue to `design/figure-style.md` if later chapters draw priceable items (Ch 9, Ch 13).
- The plan's source list for Ch 4 includes sources.md no. 49 (Open Government Licence). The
  attribution rule in Ch 4 comes from the Restricted Geographic Services License (GIS-001/002),
  which has no sources.md number, so no. 49 is not cited in Ch 4. Appendix B may need an entry for
  the Restricted licence under evidence notes GIS-001/GIS-002.
- The summary/detail discrepancy at `md:369` is cross-referenced to Chapter 1 (`#sec-01-packet`)
  instead of repeating Chapter 1's lien number.

## Chapter 6 writer's decisions (9 October 2026)

- The four Case A plates draw the marks their original alt texts name (communities, contours, a
  legal-access "?", masked identifiers "Lien / AAN / PID ••••", frontage dimension, well and septic
  icons, planner callout), although the published PNGs show almost none of them (flag F-06a). The
  alt's "scale" is drawn as "Not to scale" because a numbered scale bar would invent a distance;
  the textbook alt says so and the original alt is in the Ch 6 ledger (ch06-176).
- Plate geometry follows `md:695` (sliver behind two roadside lots, track crossing one lot), not
  the original plates' road through the parcel (flag F-06b). The base is `figures/case_a_plate.py`,
  for Chapter 7's fig-07-case-a-screening to reuse.
- Original card colours mapped to evidence states: amber → screening (dotted), magenta →
  unresolved (dashed + "?"), teal → verified (solid). The red "Limit" card on figure-13 is drawn as
  a neutral granite card, because buoy red means no-go only (figure-style §4).
- In figure-16 the parcel stays outside both zones, as in the original; "Zone ?" is dashed
  (unresolved).
- File Notes: the access note (`md:741`) is split into Observation / Limitation / Next authority
  rows with its text verbatim, keeping its own lead words "Required next evidence:". The planning
  call and the rational no have no six-part structure, so they are File Notes with one paragraph
  each, tabbed "Maple Ridge · planning call" and "Maple Ridge · a rational no". The manuscript's
  inline "> " hard-wrap artifacts are removed.
- "(Chapter 7)" added as a navigation pointer to md:783's "next inquiry".
- Flag IDs use a chapter prefix (F-06a–c) because chapters are being written in parallel and
  `flagged-claims.md` already has two duplicate IDs (F-23, F-24 appear twice).
- The §6.2 source note says the no-warranty sentence (`md:789`) is not traced to an evidence note
  (F-06c); no source was invented for it.

## Chapter 5 writer's decisions (9 October 2026)

- Q16 applied: each screenshot is copied byte for byte to `src/assets/figures/kept/<fig-id>.png`
  (SHA-256 checked by `figures/ch05_insets.py`). For the eight screenshots the plan gives an inset,
  the script also builds `<fig-id>-inset.png`: the untouched screenshot, numbered brackets drawn
  outside its frame (under the bottom edge and in a right-hand gutter), and below it one or two
  magnified pure crops tagged with the same numbers. The chapter references the `-inset.png`
  composites; the figure id stays `fig-05-<slug>` (so id ≠ file stem for these eight). Composites
  are 2650 px wide and 4–5 MB each; the build phase may want to recompress them losslessly.
- Insets were cropped to avoid magnifying any civic address or eight-digit identifier other than the
  five permitted (F-28). For figures 50 and 54 the record's status line and its amount rows are two
  separate crops because the rows between them carry an address and an assessment number.
- File Notes: the Birch Point Road notes (md:561, md:683) carry no part labels in the original, so
  they are printed as unlabelled `.filenote` blocks, verbatim; only the River Denys note (md:605) has
  labelled parts.
- The md:543 and md:665 "interruption" passages became a Quick recall box (four questions) and an
  "In practice" rail (name the record family before repeating an amount).
- Source notes name "CBC" (sources.md no. 53) and "DDV Gold"; "ME 84" appears in a source title.
  The glossary has no entries for CBC (Canadian Broadcasting Corporation) or DDV, and the footer
  check may flag them; not added here because `src/glossary-draft.yaml` is shared. Suggest adding
  CBC and putting DDV in `checks.not_acronyms`.
- The evidence-note IDs in source notes (MAP-001, MIN-003, …) follow the Chapter 4 practice.

## Chapter 7 writer's decisions (9 October 2026)

- fig-07-case-a-screening is drawn on the shared Case A base (`figures/case_a_plate.py`, from the
  Chapter 6 writer), so Parcel A keeps one geometry across Chapters 6 and 7 rather than figure-17's
  road-through-parcel layout. The Case B plates (fig-07-case-b-orientation, -access, -screening) use
  the same frame, stamp and "Not to scale" note; a Chapter 8 writer drawing figure-19 and figure-21
  may want to reuse `parcel_b()` / `case_b_base()` from `figures/ch07_figures.py` for continuity.
- Cards the originals drew in red but which are not no-go states ("No result" in figure-17/-22,
  "Limit" in figure-18) are drawn in granite, because the book reserves buoy red for no-go. The error
  column of fig-07-result-states uses the unresolved style (dashed + "?"), not no-go.
- The three result-state notes (`md:923–927`) are a two-column table plus fig-07-result-states,
  not three File Notes: they are generic rules, not a case's file entries. All other block quotes
  are File Notes with lead words added and the text verbatim.
- The Quick recall box keeps the original's five questions without answers (`md:929` gives none);
  writing answers would add text the original does not have.
- Check your understanding has 6 questions (plan: 5); within the design brief's 4–6.
- "roughly fifty metres" printed as "roughly 50 metres" (style-guide numerals rule); F-07 unchanged.
- figure-19 (placed at `md:845` in the original) is left to Chapter 8 per the plan; figure-22 arrives
  from Chapter 8. Both are recorded in the Ch 7 ledger (ch07-053 moved; "Arrived" A-1).
- New flag F-29 (alt texts that describe more than their images show).

## Chapter 9 writer's decisions (9 October 2026)

- Figure order follows the text: the tax-branches figure (9.5) comes before build-backward (9.6),
  because the original's tax branches (md:1137–1149) come before the maximum bid (md:1151–1155).
- fig-09-municipal-result-comparison labels each panel with its source document ("public result
  sheet", "official result sheet", "published table"), not with the original alt's "auction type",
  because the chapter text does not state every event's sale format. Each panel adds the
  denominator, range and limit from md:1059–1085, as the plan asks.
- fig-09-inverness-ratio-distribution draws 31 blocks in four bands (7 / 9 / 8 / 7) with brackets
  for the stated cumulative counts (24, 15, 7); no median position is drawn (flag F-09c).
- fig-09-all-in-cost-stack draws equal layers under a waterline, marked "Not to scale", so it does
  not suggest proportions (md:1103's limit). No layer carries an evidence-state style, because the
  original's card colours had no state meaning.
- md:1095 "route the listener" → "route the researcher"; md:1163 "protects the listener" →
  "protects the bidder" (style guide §2). Recorded in the ledger.
- The Quick recall answers (md:1113 gives only questions) restate claims from the same chapter; the
  ledger lists their supporting claims.
- `review/tools/check_ledger.py 09` passes.

## Chapter 8 writer's decisions (9 October 2026)

- Case B plates fig-08-case-b-identity (figure-19, Case B plate 2) and fig-08-case-b-planning
  (figure-21, plate 4) reuse `case_b_base()` / `parcel_b()` from `figures/ch07_figures.py`
  (imported by `figures/ch08_figures.py`), so Parcel B keeps one geometry across Chapters 7 and 8.
  Marks the alt texts name but the PNGs lack are drawn from the alts' words (flags F-08b, F-08c).
- figure-24's original colours (navy, magenta, amber) had no evidence-state meaning, so the redraw
  draws all three columns in the accent teal; figure-25's cards map to states (amber → screening,
  teal → verified, magenta → professional verification, red → no-go).
- fig-08-case-b-planning sits in the occupied-building section (plan); its caption says "Case B,
  plate 4, used here for the occupied Foundry Street discussion" without renaming Parcel B (Q5).
- Both recovery exercises (md:983, md:1035) are Quick recall boxes with the original questions and
  short bold answers restating this chapter's claims (as Chapters 6 and 9 do; Chapter 7 chose to
  print its questions without answers).
- md:979 "the land the listener thought" → "the land the bidder thought"; md:1007 "For a pre-bid
  listener" → "For a bidder still before the auction" (style guide §2). "(Chapter 9)" added as a
  navigation pointer to md:949's "returns to pre-bid valuation". Recorded in the ledger.
- The md:987 Foundry Street scene opens §8.2 as a case box (the original closes §8.1 with it); the
  transition "One question still sits outside the title file." is kept before it.
- The §8.2 source note cites LAW-008 (MGA s. 151; HRMC s. 166) for the certificate-holder powers the
  text recalls from Chapter 3.
- `review/tools/check_ledger.py 08` passes.
- New flags F-08a (clear-title warning not traced), F-08b and F-08c (alt texts describe marks the
  images lack), F-08d (Foundry Street's building type).

## Chapter 10 writer's decisions (9 October 2026)

- fig-10-auction-versus-tender keeps figure-30's own label "card rises only below the limit" (the
  plan paraphrased it as "card stays down above the limit") and draws the original alt's "parallel
  timelines" as two lanes of three steps ending in one shared box. "Same written walk-away rule"
  inside that box comes from the original alt. Lanes are drawn in accent teal, not figure-30's
  navy/teal/magenta, because those colours had no evidence-state meaning.
- fig-10-payment-readiness-clock: the three break boxes are dashed granite (branches, not no-go;
  buoy red is reserved for no-go) with a one-line timing note from md:1247, 1253, 1257 and a dash
  legend. Figure-39's source string and footer moved into the caption verbatim.
- fig-10-sale-state-changes (NEW) uses "paid, removed or otherwise changed" (md:1207) for
  withdrawal rather than the plan's "paid, removed or deferred". The tender and schedule-change boxes
  sit beside the last two spine states without connectors. No "Not to scale" mark: no time spans are
  drawn.
- Present-tense CBRM statements are dated in the text: "CBRM's current result legend (as checked in
  July 2026)" and "CBRM's current instructions (July 2026)" (credibility rule 3; F-06 practice).
- md:1215's "Chapter 9 retrieval under noise" became a Quick recall box ("the Chapter 9 test,
  applied under noise", Q22); md:1273's "returns the listener" → "returns the reader".
- The statute's $5,000 penalty (LAW-016) is not added (Q15); the text keeps "a penalty".
- Four Maya case boxes are labelled "Composite case — not a real property; Maya is a fictional
  bidder." The md:1239 scenario is boxed as "A different fictional parcel", as the original says.
- "Chapter 9" links to `#sec-09-build-backward`; "(Chapter 11)" is plain text (no anchor known yet).
- `review/tools/check_ledger.py 10` passes. New flags F-10a, F-10b (note) and F-10c (open).

## Chapter 11 writer's decisions (9 October 2026)

- F-16 applied: figure-31's month 1 card "Register certificate; organize evidence and insurance
  attempts." is redrawn verbatim; the caption points to F-16 ("the treasurer registers the
  certificate"). Month 6 (magenta in the original) is drawn in the unresolved style (dashed + "?").
- The original alt names marks the image does not draw (F-11b); following the F-29 / F-08b practice,
  the redraw adds small tags worded from the alt. The textbook alt lists the six cards.
- "Current Canadian insurer materials" (md:1307) is dated "(checked July 2026)" from sources.md
  no. 31 (F-11a).
- md:1339's "It is not a substitute for Chapter 9's all-in analysis" is printed as "The 10 percent
  line is not a substitute…", reading "It" as the paragraph's subject; recorded in the ledger for
  the reviewer.
- fig-11-redemption-ledger aligns each purchaser-repayment row with its redemption-amount row; the
  blank cells carry no legal meaning beyond md:1349's two lists, and the figure says "Not
  necessarily the same line-by-line list."
- Source notes cite CBRM (no. 7) and Residential Tenancies (no. 33) for OCC-001, which the plan
  lists by evidence ID only. "(Chapter 12)" added as a navigation pointer after the deed request
  (md:1367).

## Chapter 12 writer's decisions (9 October 2026)

- fig-12-deed-is-a-beginning draws the central "Tax deed" box and six arrows that figure-32's alt
  names but its PNG lacks (flag F-12a), like the Chapter 6–8 plates. The six cards keep their
  labels verbatim; the original colours had no evidence-state meaning, so all are accent teal.
- fig-12-surplus-proceeds-route draws figure-40's red band ("No automatic payout…") on the accent
  tint, because buoy red means no-go only; "twenty years" printed as "20 years" (style guide).
- fig-12-three-clocks prints md:1393's full list ("not auction day, not the end of redemption, not
  deed delivery, not first entry"); the plan's shorter note omitted "the end of redemption".
- "As of July 2026" added to md:1385, 1405 and 1429 and "(July 2026)" to md:1389 (dated official
  statements; style guide §3). md:1381 "explained earlier" → "explained in Chapter 8".
- md:1395's "That distinction blocks a dangerous shortcut." is a transition and was dropped; its
  content is the Careful panel. md:1391's "Registration starts another legal clock." is a subhead
  and is merged in the ledger (ch12-025).
- Five Foundry Street case boxes plus one Elena box: the plan names only the Elena box, but the
  style guide puts case narrative in boxes and rules in running text.
- `zoning-confirmation letter`, `municipal-clearance letter`, `taxable assessed value` and `Capped
  Assessment Program` are bolded at their defining use here (the glossary cites md:1429–1437).
- New flags F-12a, F-12b (Capped Assessment Program not traced), F-12c (deed fee, prescribed deed
  and delivery not itemized). `review/tools/check_ledger.py 12` passes.

## Chapter 13 writer's decisions (9 October 2026)

- The Case C plates use their own geometry in `figures/ch13_figures.py` (`CPlate`), built on the
  Case A layout constants and card styles from `figures/case_a_plate.py`: map 424 × 300, rail
  cards at x 448, stamp, north arrow, "Not to scale". Parcel C sits beside the mapped road
  (`md:1533`), not crossed by roads as in figures 33–37 (F-13b).
- Marks the alt texts name but the PNGs lack are drawn from the alts' words (F-13b). The planning
  plate's three written questions are worded only from `md:1557` ("exact frontage, lot,
  intended-use and approval"): "Exact frontage?", "Lot status?", "Intended use and its approval?".
- figure-33's green "evidence-file label" uses the process-complete state (green, check glyph);
  the red "Limit" card is granite (figure-style §9); figure-37's "No result" card is granite.
- fig-13-known-unresolved-professional: Known = verified (solid teal, check), Unresolved =
  unresolved (dashed, "?"), Professional = accent teal with an arrow glyph (a handoff, not an
  evidence state), Decision = ink 2.25 box. The original's amber for "Unresolved" was not kept
  because amber means screening in this book. Ruled rows make it a worksheet (Q25); the blank
  Appendix C copy can be made by dropping the two body sentences.
- fig-13-three-endings marks both stops in the no-go style and Meadow Line's decision point in the
  process-complete style with "not a recommendation".
- The four-part analyses (`md:1509`, `md:1529`) are two-column tables; the four-part instruction
  (`md:1507`) is an "In practice" rail. Key terms list existing glossary terms only ("none new" in
  the plan); "stage record" is explained in a table and not bolded, because it has no glossary
  entry (suggest adding one in the build phase: "a dated line stating the controlling document,
  the power or duty it creates, its boundary, the next authorized action and the event that will
  end that stage", `md:1597`).
- Cross-references link to `#sec-09-build-backward`, `#sec-10-finish-line` and (question 3)
  `#sec-04-four-destinations`; link text names the chapter, not a section number.
- `review/tools/check_ledger.py 13` passes. New flags F-13a (note), F-13b (open), F-13c (note),
  F-13d (open).
