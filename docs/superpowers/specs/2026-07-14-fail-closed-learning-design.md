# Fail-Closed Learning Design for Audiobook Skills

Date: 2026-07-14
Status: approved for implementation by Dan's instruction to apply the previously
presented recommendations

## Problem

The audiobook workflows currently describe good learning practices but do not
make them prerequisites for packaging. *The Question Machine, Second Edition*
demonstrated the failure: prose style checks passed while the manuscript lacked
orientation, a usable learning arc, chapter teaching plans, complete explanation
stacks, maintained continuity, and an independent beginner-reader verdict. The
run also reduced its word target after an undersized draft already existed.

A successful style, factual, cover, audio, or packaging check must never imply
that a book is structurally coherent or teachable.

## Considered Approaches

### 1. Strengthen prose instructions only

Add stronger reminders to the three skills. This is inexpensive, but repeats the
existing failure mode: an agent can skip the reminders and still build a book.

### 2. Add one editorial checklist

Require a final learning report before packaging. This improves review but still
allows planning omissions to be rationalized after the manuscript exists.

### 3. Add staged structured evidence plus a hash-bound packaging gate

Require structured development records before drafting, update them during
sequential drafting, require independent structural and beginner-reader review
against the final chapter hashes, and generate a learning-design receipt that
the EPUB builder verifies. This is the selected approach because it makes the
right artifacts part of the build dependency graph.

## Selected Architecture

### Shared learning-design reference

Add `skill/references/learning-design.md` as the canonical contract used by
`explainer-audiobook`, `custom-learning-audiobook`, and
`longform-book-development`. It defines five separate acceptance lanes:

1. curriculum and learner orientation;
2. chapter teaching plans and explanation depth;
3. final-manuscript structural and beginner-reader review;
4. prose style and de-Claudification;
5. packaging and acoustic verification.

No lane substitutes for another.

### Structured source records

Each production run will carry these machine-readable records under `research/`:

- `learning-brief.json`: learner outcome, prior knowledge, opening orientation,
  original/current target, and approved scope-change history;
- `learning-outline.json`: approval evidence, chapter progression, prerequisites,
  and two to four genuine throughlines;
- `chapter-plans.json`: one record per canonical chapter with purpose,
  prerequisite, knowledge delta, grounded example, concepts, and varied beats;
- `coverage-ledger.json`: one record per core concept with definition, reason,
  mechanism, concrete case, useful boundary or explicit not-applicable reason,
  misconception, expected ability, and chapter uses;
- `continuity.json`: an entry after every drafted chapter recording definitions,
  examples, callbacks, promises, and unresolved questions;
- `learning-review.json`: independent structural and beginner-reader verdicts,
  cited findings and frontier-author decisions, bound to the final chapter
  hashes.

Human-readable Markdown may accompany these files, but it cannot replace the
structured evidence used by the gate.

### Deterministic validator and receipt

Add `skill/scripts/learning_design_qc.py`. It will:

- reject missing, empty, malformed, or incomplete records;
- reject an outline without explicit user approval or an explicit autonomous-run
  authorization;
- reject unapproved target reductions;
- require one chapter plan and continuity checkpoint per chapter;
- require complete explanation paths for every core concept;
- require passing structural and beginner-reader verdicts over the final chapter
  hashes;
- reject unresolved review findings;
- write `research/learning-design-receipt.json` containing input hashes, chapter
  hashes, word-count comparison, and separate gate results.

The validator checks evidence shape and binding, not literary quality. Human and
frontier-author judgment still supplies the substantive verdict.

### Packaging enforcement

Add `--learning-receipt` to `build_book.py`. New CLI builds require it and verify
that every final chapter hash matches the receipt. A clearly named legacy escape
hatch remains only for reproducing an older package; all three current skills
will forbid using it for new or revised manuscripts.

The build commands in both audiobook production skills will pass both
`--learning-receipt` and `--prose-receipt`. A passing prose receipt cannot satisfy
the learning receipt requirement.

### Humanizer boundary

Update the shared `humanizer` skill to state that it certifies local voice edits
only. When the manuscript has missing orientation, chapter order problems,
unexplained concepts, or shallow mechanisms, the humanizer records a structural
blocker and returns the manuscript to the learning-design/editorial stage. It
must not cosmetically smooth those defects or claim whole-book acceptance.

### Longform handoff

Extend the longform handoff contract so production receives learner starting
state, opening orientation, approved target and change history, chapter
prerequisites, knowledge deltas, teaching beats, throughlines, explanation-stack
expectations, and acceptance criteria. A handoff without those items remains a
development draft and cannot start canonical manuscript production.

## Workflow

1. Capture learner outcome, prior knowledge, and target.
2. Design orientation, learning arc, throughlines, chapter plans, and concept
   explanation paths.
3. Obtain outline approval or record explicit autonomous authorization.
4. Draft sequentially, updating continuity after each chapter.
5. Run structural and beginner-reader review against final hashes; the frontier
   author resolves accepted findings.
6. Generate the learning-design receipt.
7. Run the separate humanizer/de-Claudification gate and prose receipt.
8. Build only when both receipts match the canonical chapters.
9. Continue with cover, Echo narration, package verification, and delivery.

## Failure Handling

- Missing planning evidence stops drafting or packaging; it is not reconstructed
  after the fact merely to satisfy the gate.
- A scope or word-target reduction after drafting requires explicit learner
  approval recorded with the old value, new value, reason, and evidence.
- A failed structural or beginner-reader verdict returns to frontier-author
  revision and must be rerun on the revised hashes.
- A stale receipt fails after any chapter edit.
- `legacy-without-learning-receipt` may reproduce an old artifact but may not be
  used for a new edition, revision, or claim of current workflow compliance.

## Testing

Add regression tests that first demonstrate the current builder and skills allow
missing learning evidence. Then verify:

- valid structured evidence produces a receipt;
- missing orientation, chapter plans, explanation rungs, continuity checkpoints,
  approval, or reader verdicts fail with specific messages;
- retroactive unapproved target reduction fails;
- stale chapter hashes fail at receipt generation and packaging;
- build CLI requires a learning receipt unless the explicit legacy flag is used;
- all three audiobook skills and the humanizer contain the separate-gate and
  no-retroactive-normalization contracts.

Run focused tests, the complete repository test suite, skill validation, and
`git diff --check` before publishing.

## Scope

This change repairs reusable skill contracts and deterministic packaging gates.
It does not rewrite *The Question Machine*, render audio, alter private book
artifacts, or declare any existing manuscript pedagogically accepted.
