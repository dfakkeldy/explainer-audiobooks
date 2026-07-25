# Audiobook Writing Quality — Gate Consolidation and Prose Craft

Date: 2026-07-25
Branch: `claude/audiobook-writing-quality-86c4f7`
Scope: `explainer-audiobook`, `custom-learning-audiobook`,
`longform-book-development`, `fiction-book-development`
Status: design approved, implementation plan pending

## Problem

Books produced by the four book skills read as formulaic. Dan's assessment: the
prose "covers all the points and is so methodological it just feels like a
formula," carries too many conditional statements, spends words announcing that
something matters instead of showing it, and lacks the stories that make
nonfiction memorable.

Two prior corrections already shipped and did not fix this. PR #23 added the
de-Claudification linter; PR #28 added an independent learning gate; PR #32
added the road-book contract. All three are merged and live.

## Evidence

### Measured across the shipped corpus

| Book | Verdict | paraCV | sentCV | 4+ item lists /1k sents | arith terms /10k words |
|---|---|---|---|---|---|
| The Question Machine ed1 | taught well | 0.37 | 0.72 | 0 | 7.1 |
| Is There Anyone in Here? | good | 0.43 | 0.65 | 0 | 5.4 |
| NS tax-sale book | weak | 0.30 | 0.51 | 12 | 6.2 |

`paraCV` / `sentCV` are standard deviation over mean of paragraph and sentence
word counts — rhythm variance.

Two measures separate good from weak: **sentence variance** (0.65–0.72 good,
0.51 weak) and **coordinate lists** (0 good, 12 weak). Arithmetic density does
*not* separate — ed1 scores highest because it is a book about AI. Any
arithmetic budget must be relative to the brief's approved level, never a
universal cap.

### Forensic evidence from the KB

`bundle/questions/audiobook-learning-comprehension-gate.md` records three
Question Machine editions:

| | ed1 (worked) | ed2 | ed3 "deep" |
|---|---|---|---|
| narrated words | 39,900 | 11,300 | 40,200 |
| tracked technical terms | 40 | 91 | 98 |
| terms introduced in ch1 | — | 41 (first two ch) | 35 |
| arithmetic-language rate | baseline | — | ~9× ed1 |

The KB's verdict on the gate system:

> The system therefore failed closed on length and record completeness while
> failing open on overload.

Ed3 **passed** the structured learning gate and was unlistenable.

## Root causes

1. **The verification schema leaked into generation.** `learning-design.md`
   defines a five-layer explanation stack (what it is, why it exists, how it
   works, a concrete case, the boundary) and the QC check verifies those five
   per chapter. The author writes five paragraphs, one per layer, every chapter.
   The reader hears a form being filled in.

2. **Every gate is a receipt; almost none is a budget.** 6 independent verdicts,
   14 ordered gate steps, 18 artifacts, 5 builder receipt flags, ~1,640 lines of
   QC script. All post-hoc verification. Every *actual* failure was a budget
   failure — 98 terms, 35 in chapter one, 9× arithmetic — and each was answered
   with another checker rather than a cap the author writes toward.

3. **Ban-list voice control produces defensive prose.** `declaudification.md` is
   106 lines of prohibition and grows with each failure. Forty "don'ts" define a
   large acceptable space with no gradient toward any point in it, so the author
   lands on the safe centroid: flat and uniform. The counterexample is in this
   repo — `fiction-book-development` uses a positive control panel with named
   ranges plus project-specific sample sentences, and prohibitions as a footnote.

4. **Research collects facts, never narratives.** The fact pack gathers statutes,
   docs, and code. With no story material on hand the author invents
   hypotheticals — "the fictional bidder," "consider a modest fictional building
   on Harbour Road." A hypothetical is not a story.

5. **Revision substitutes instead of adding.** `revisionMode` defaults to
   `new-book` with an empty `preserve` block containing a field literally named
   `narrativeSpine`. Gate 3 applies `first-edition-plus` "when applicable" with
   no trigger deciding when. Feedback of the form "I didn't learn what a neural
   net is" therefore read as a fresh brief, and the Descartes spine — which was
   the explanation, not decoration — was dropped. With the lineage gone, the only
   remaining way to say what a neural net is was the notation.

## Decisions taken

| Decision | Choice |
|---|---|
| Coverage vs memorability | Split the surfaces. Coverage ledger and gates stay; narrated chapters become selective; exhaustive detail moves to the existing non-narrated appendix. |
| Story sources | Documented and institutional only — published decisions, papers, post-mortems, news, real repo history, named public figures in public roles. No private individuals. |
| Rollout shape | Port fiction's control-panel pattern to the nonfiction skills; share the metrics as a genre-neutral script. Fiction stays structurally independent and opts in via profile. |
| Gate work | All four moves, sequenced first. |

## Design

### PR 1 — Measurement

Merge `prose_qc.py` (381 lines) and `learning_design_qc.py` (1,255 lines) into a
single `book_qc.py` with `--profile learning|fiction`, producing one report and
one receipt with per-axis verdicts.

New measures, all computable from a draft in seconds:

| Measure | Type |
|---|---|
| paragraph CV, sentence CV | rhythm variance |
| 4+ item coordinated series per 1k sentences | exhaustive-list detector |
| abstract-noun sentence subjects | advisory, reports locations |
| new core terms introduced per chapter | concept load |
| arithmetic-language density vs brief's approved level | ratio, not absolute |

Existing checks carry over unchanged. Fiction gains its first automated prose
gate via `--profile fiction` (rhythm + coordinate lists, no nonfiction style
families).

### PR 2 — Budgets and verdict collapse

Promote the forensic numbers to generation-time budgets, present in the author's
prompt and checked after **each chapter**, not at gate 11:

| Budget | Cap | Enforcement | Source |
|---|---|---|---|
| new core terms / chapter | ≤3 | advisory | ed3 introduced 35 in ch1 |
| durable book outcomes | 6–10 | blocking | KB contract item 2 |
| arithmetic density | ≤ tier band (below) | advisory | ed3 ran ~9× ed1 |
| values / symbolic steps per spoken calculation | ≤3 / ≤3 | blocking | exists in `narration-style.md`, unenforced |
| real sourced story anchors / chapter | ≥1 or recorded exemption | blocking | new |
| sentence CV | ≥0.60 | blocking *iff* corpus split holds | ed1 0.72, consciousness 0.65, tax-sale 0.51 |
| 4+ item lists / 1k sentences | ≤3 | blocking | ed1 and consciousness both 0 |

Paragraph CV is measured and reported but is **not** a budget: it separates the
corpus too narrowly (0.37 / 0.43 good vs 0.30 weak) to carry a threshold.

"Arithmetic density ≤ tier band" requires the brief to record a named arithmetic
tier — `none`, `light` (ed1's level, ~7 arithmetic terms per 10k words),
`quantitative`, or `symbolic`. The check compares measured density against that
tier's band, calibrated from ed1 for `light`. Absolute caps are rejected: ed1
scored the corpus maximum and taught successfully.

Collapse 6 independent verdicts to 3. Curriculum, chapter teaching, blind
beginner review, and comprehension pilot all measure one question — does a
beginner learn — and become **Teaching**. Prose style and narration become
**Craft**. EPUB, covers, M4B, sidecar, acoustic become **Package**. The human
listening verdict remains supreme and unchanged.

Add **prerequisite-before-use** to the Teaching verdict as a mechanical check:
for every core concept, each declared prerequisite must be taught, in narratable
form, before first substantive use. Chapter plans already carry `prerequisites`;
nothing verifies delivery order.

Retire on evidence. For each remaining gate, name a real defect it caught that
the next gate would not have. Recorded precedent: the de-Claudification linter
found 2 hard bans and 87 family matches in a shipped book — it stays. The
learning receipt as constituted passed ed3 — it does not survive in its current
form.

### PR 3 — Revision protection

- **Preserve on by default.** Any brief referencing an existing book sets
  `revisionMode: first-edition-plus` and blocks until `preserve` is populated.
  The flag stops being something the user must know exists.
- **Gap feedback is an ADD instruction.** "I didn't learn X" means insert X's
  foundation into the existing spine. It never authorises re-planning the book
  around X. The skill must show where new material inserts **and name what
  stays**.
- **Math routes to the appendix.** Narrated chapters carry intuition and lineage;
  symbols, derivations, and worked arithmetic go to the existing
  `--non-narrated-appendix`. A math-density sweep over `chapters/` runs alongside
  the code-leak sweep.

### PR 4 — Prose craft

- **Voice control panel** (`skill/references/voice-design.md`), modeled on
  `fiction-book-development/references/style-and-scene-craft.md`: ten dials with
  observable ranges (narrator stance, sentence movement, diction, evidence
  handling, concession, humour, exposition, story density, emphasis, direct
  address), plus 3–5 positive sample sentences written for the project. Set at
  intake, frozen before drafting. `declaudification.md` survives unchanged but is
  read at QC, not at drafting.
- **Narrative spine, then story ledger.** The spine is book-level and ordered;
  chapters are stations on it. `research/story-ledger.md` + `.json` holds
  per-chapter cases, each recording what happened, named actors/place/date,
  source citation, the concept it carries, and **the reversal** — what a
  reasonable person would have expected instead. No reversal means it is an
  example, not a story, and does not count. Chapter plans name a ledger entry or
  record "no story available" with a reason, surfacing dry chapters at planning
  time.
- **Surface split.** `coverage-ledger` gains a `narration | reference` column.
  The explanation-stack check moves from per-chapter to book-wide. Coordinate-list
  and rhythm checks run strict over `chapters/`, off over the appendix.
- **Two small kills.** Delete "or running summary" from `narration-style.md:133`
  — previous section text, always. Add a modal-conversion rule: every statutory or
  API `may`/`must` becomes an actor doing something, or names who is bound.

## Validation

The corpus is the regression suite. Correct thresholds must reproduce these
verdicts:

| Book | Location | Expected |
|---|---|---|
| QM ed1 | `build/the-question-machine/` (this worktree, gitignored) | pass rhythm, pass lists |
| Is There Anyone in Here? | `.build/custom-learning-audiobooks/` | pass rhythm, pass lists |
| NS tax-sale | `docs/nova-scotia-tax-sale-book/` | **fail** rhythm, **fail** lists |

If the thresholds do not split the corpus that way, the thresholds are wrong.

**Known gap:** QM ed2 and ed3 are gone — the codex worktree
`~/.codex/worktrees/question-machine-learning-edition-design` no longer exists,
despite the KB instruction to "keep the rejected private package as failure
evidence." Their forensic numbers survive in the KB but the text does not, so the
term-load and arithmetic budgets cannot be re-validated against the manuscripts
that motivated them. Those two budgets ship advisory until a future book
exercises them.

Rhythm floors also rest on three books. They ship advisory in PR 1 and become
blocking in PR 2 only if the corpus split holds.

## Risks

- **Book-wide explanation-stack check weakens technical books.** A concept could
  lose a layer entirely rather than have it relocated. Mitigation: the coverage
  ledger's new column makes the intended surface explicit per row, and the
  Teaching verdict checks the union.
- **Gate consolidation reverses part of the 2026-07-15 contract.** That contract
  was Dan's own response to a real failure. Reversal must be argued in the KB, not
  performed silently.
- **Rhythm floors could reward padding.** Long sentences are not good sentences.
  Mitigation: advisory first, and CV is a variance measure — uniformly long prose
  scores as badly as uniformly short.

## Obligations

- **KB page required.** This reverses part of the 07-15 operating contract, so it
  needs a `bundle/questions/` page reconciling with
  `audiobook-learning-comprehension-gate.md` and
  `audiobook-prose-declaudification.md`, in its own KB PR per the KB's own rules.
- **Docs update.** Coverage-ledger schema change, two new artifacts, and the
  surface split affect `docs/how-these-were-made.md` and
  `skills/longform-book-development/references/handoff-packet.md`. Same branch.
- **Open question for Dan.** The KB carries a live condition: "Do not produce
  another full Question Machine edition until this contract is implemented and a
  short pilot passes human comprehension." PR #32 is merged, so the contract is
  implemented; whether the comprehension pilot ever ran is not recorded in the
  repo.
