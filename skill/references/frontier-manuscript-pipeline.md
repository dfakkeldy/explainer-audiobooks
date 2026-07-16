# Frontier Manuscript Pipeline

Use this production split when the book's prose should be authored by a frontier
model, while lower-cost workers handle evidence, diagnostics, and packaging. The
point is not to make every task expensive. It is to protect the two things that
make a book feel authored: the explanation choices and the continuity of its
voice.

Long-form quality is a pipeline problem, not a prompt problem. Research,
argument design, prose drafting, and revision are different jobs whose
instructions compete when they share one long generation. Run them as separate
calls with explicit artifacts. Each phase consumes the accepted artifact from
the phase before it.

Follow `learning-design.md`. The frontier author owns the learning architecture,
but current packaging requires grounded `evidence-notes.json`, structured
`chapter-plans.json`, `revision-passes.json`, `learning-review.json`, and the
final hash-bound learning-design receipt.

## Role Contract

| Role | Owns | Must not do |
|---|---|---|
| Frontier lead author | Learning architecture, outline choices, explanatory depth, examples, canonical Markdown chapters, and accepted substantive revisions | Delegate chapters to independent prose writers or accept unsupported facts |
| Cheap research worker | Source extraction, citations, fact-pack drafts, terminology lists, and conflict flags | Decide what the listener needs to learn or invent facts |
| Cheap editorial reviewer | Evidence-backed findings: repetition candidates, confusing leaps, shallow explanations, jargon, voice tics, and missing examples | Rewrite a chapter in a competing voice or decide a structural repair |
| Cheap production worker | Markdown lint, EPUB/M4B build, metadata, cover rendering, file validation, and manifest | Change manuscript meaning |

A cheap worker may make a bounded mechanical correction only when it cannot alter
meaning, pedagogy, or a factual claim. Examples: a duplicate word, a malformed
heading, a broken Markdown image path, or a typo verified against the fact pack.
Everything else goes back to the frontier author as a precise repair request.

## Canonical Markdown Flow

1. **Cheap workers prepare grounded evidence.** Build `evidence-notes.md` and
   `evidence-notes.json` with stable claim IDs, citations, precise locators,
   contradictions, and uncertainty labels. Set the claim policy to
   `traceable-only`. Give the frontier author the evidence, not a cheaper
   worker's prose draft to imitate. A claim absent from the notes is unavailable
   to the outline and manuscript.

2. **Turn an approved private source into a craft profile.** When the user names
   a local book or audiobook as a voice source, analyze its high-level craft:
   opening moves, evidence-to-example movement, plain-language explanations,
   direct address, humor boundary, uncertainty, rhythm, and practical landings.
   Save those observations in `voice-source-profile.md`. Persist the rule
   "craft features, not pastiche." Do not commit raw source excerpts or source
   files. A later
   project-authored first section becomes the actual voice exemplar.

3. **The frontier author builds an argument-level outline.** Approve the table of
   contents, the two to four genuine throughlines, and
   `research/coverage-ledger.md`. For every section, record its job, argument,
   specific claims by evidence ID, throughline advance, narrative or metaphor
   payoff, landing beat, and what it must not repeat. The ledger maps each core
   concept to its first explanation, later retrieval or deepening, a concrete
   example, a boundary/counterexample where useful, and a listener outcome.
   Record the result in `learning-outline.json`, `chapter-plans.json`, and
   `coverage-ledger.json` before prose.

4. **Stop at the outline human checkpoint.** The intended human reviews the
   argument, progression, promised payoffs, road-book teaching infrastructure,
   and exclusions. Topic-list approval is insufficient. Record approval before
   the first section is drafted.

5. **Draft and curate the first section.** Give the frontier author the full
   outline, grounded evidence, voice-source craft profile, the section job, and
   its must-not-repeat list. Revise this section until the human accepts both its
   teaching and voice. Preserve it as `voice-exemplar.md`, then use it in the
   narrated comprehension pilot. Do not draft the remaining book before this
   human checkpoint and pilot pass.

6. **Draft section by section with forward context.** Each call receives the
   full outline, relevant evidence IDs, coverage rows, approved voice exemplar,
   the previous section's actual text or a faithful running summary, the current
   section job, and what it must not repeat. Write sections in order; never
   generate the whole book in one call or distribute adjacent prose to
   independent voices. The prose in `chapters/` is canonical; EPUB, audio, and
   covers are derivatives.

7. **Update continuity after every section.** Write the corresponding
   `continuity.json` draft context and checkpoint before the next call. Record
   terms already defined, analogies and scenes already used, examples,
   deliberate callbacks, active promises, unresolved questions, retrievals,
   listener load, the running summary, and the no-repeat list. This prevents
   drift and repetitive re-introductions without asking one generation to hold
   the entire manuscript.

8. **Cheap workers inspect, never redraft.** Run `skill/scripts/prose_qc.py`, source
   validation, narration lint, and independent learning reviews. Each report
   must cite the source paragraph and explain why a change would improve learning.

9. **Run narrow revision calls.** "Make it better" is not a revision job. Record
   each required single-job pass in `revision-passes.json`: claim-traceability,
   tightening, de-listification, sentence-rhythm, and ear-pass. The frontier
   author accepts, rejects, or repairs each substantive finding. Render the
   ear-pass through Echo, Kokoro, or the governed narrator and record every
   stumble or lost thread. Local findings earn local patches, not regeneration.
   Rerun structure and blind beginner review after final voice edits and bind all
   final records to the canonical chapter hashes.

10. **Humanize without changing authorship.** After substantive repairs, load the
   `humanizer` skill and follow `references/humanizer-pass.md`. It may remove
   AI-writing tics and improve spoken rhythm, but it must not invent anecdotes,
   claims, sources, first-person experience, or a competing voice. The frontier
   author reviews every non-mechanical edit; rerun factual, ledger, and narration
   checks afterward.

   Follow `references/declaudification.md`: run an independent phrase-family
   inventory before edits, repair accepted findings, rerun the whole-manuscript
   density gate, and create a receipt containing before/after counts, accepted
   and rejected decisions, rerun checks, and chapter hashes.

11. **Cheap workers package and validate.** Render EPUB/M4B, build covers, check
   files and metadata, and write the manifest. They must not “improve” the prose
   while packaging.

## Coverage-Ledger Test

Every core concept should have an explanation path, not just a definition:

1. **What** is it, in plain language?
2. **Why** does it exist — what problem or decision does it address?
3. **How** does it work at the level the listener needs?
4. **Where** does the listener see it in the worked example or a concrete case?
5. **When does it not apply?** Name a boundary, tradeoff, misconception, or
   counterexample when that would prevent a bad mental model.

Do not force all five into one paragraph or every minor term. The ledger makes
sure the book, taken as a whole, supplies the missing rung before moving on.

## Cheap Editorial Report Format

Require a compact, citation-first report. A useful finding is actionable without
asking the frontier author to rediscover the problem:

```markdown
## Finding 07 — redundant re-explanation
- **Location:** `chapters/ch04.md`, paragraph beginning “A cache is…”
- **Evidence:** This restates the definition from `ch02`, paragraph beginning
  “Think of a cache…” without adding mechanism, application, or contrast.
- **Listener cost:** A listener gets the same fact twice but still does not know
  when caching is the wrong choice.
- **Repair request:** Replace this restatement with one short callback, then add
  a concrete “when not to cache” case.
- **Category:** redundancy | depth gap | unclear mechanism | jargon | voice tic |
  factual conflict | weak example | missing boundary
```

A reviewer may return **no findings**. Do not make it manufacture criticism to
fill a quota. The author, not the reviewer, decides whether a reported issue is
real and writes all non-mechanical prose changes.

## Completion Gates

- [ ] One named frontier model authored every substantive Markdown passage.
- [ ] `evidence-notes.md` and `evidence-notes.json` bind every manuscript claim
      to a verified source and locator.
- [ ] A private source, when used, produced a bounded craft profile without raw
      excerpts or a pastiche request.
- [ ] The argument-level outline gives every section a job, claim IDs,
      throughline advance, payoff, landing beat, and no-repeat list.
- [ ] The human accepted the outline and first-section voice exemplar before the
      remaining section-by-section draft.
- [ ] `coverage-ledger.md` gives every planned recurrence a learning purpose.
- [ ] `chapter-plans.json` gives every chapter a purpose, prerequisites,
      knowledge delta, grounded example, concepts, and varied beats.
- [ ] `continuity.md` records prior terms, analogies, examples, and promises.
- [ ] `revision-passes.json` records separate passing single-job passes and a
      rendered ear-pass for the final chapter hashes.
- [ ] `learning-review.json` carries passing independent structure and
      beginner-reader verdicts for the final chapter hashes.
- [ ] Cheap review reports cite exact locations and recommend repairs rather than
  supplying a replacement voice.
- [ ] The frontier author accepted/rejected substantive findings before packaging.
- [ ] The bounded humanizer pass was reviewed by the frontier author, or its
      explicit skip was recorded.
- [ ] The de-Claudification family gate passes and its receipt matches the final
      chapter hashes.
- [ ] The published EPUB/M4B was derived from the reviewed Markdown, with no
  downstream prose rewriting.
