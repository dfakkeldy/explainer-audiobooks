# Fail-Closed Learning Design

Use this contract before canonical drafting and again before packaging a
nonfiction learning audiobook. It separates evidence that was previously easy
to collapse into one vague “QC passed” claim.

## Five independent verdicts

1. **Curriculum and orientation:** the book starts at the listener's real prior
   knowledge, explains why the subject is worth learning, promises a concrete
   outcome, and previews a coherent route.
2. **Chapter teaching:** every chapter has a purpose, prerequisites, a knowledge
   delta, a grounded example, varied teaching beats, and concepts with complete
   explanation paths.
3. **Structural and beginner-reader review:** independent reviewers examine the
   final manuscript for sequence, context, unexplained leaps, shallow mechanisms,
   jargon, missing examples, misconceptions, and boundaries.
4. **Prose style:** the separate humanizer and de-Claudification pass checks
   voice, rhythm, and model tics without changing the learning architecture.
5. **Packaging and acoustic verification:** EPUB, cover, M4B, sidecar,
   pronunciation, and delivery receipts prove artifact integrity and audio
   behavior.

These verdicts cannot substitute for one another. A factual manuscript with a
passing prose receipt can still fail to teach. A technically valid M4B can still
narrate a structurally failed book.

## Structured evidence

Maintain these records under `$RUN_ROOT/research/` as the project develops. Do
not reconstruct them after a failed draft merely to unlock packaging.

### `learning-brief.json`

```json
{
  "schemaVersion": 1,
  "learnerOutcome": "What the listener can explain or do after the book",
  "priorKnowledge": "Actual exposure, known terms, and likely gaps",
  "openingOrientation": {
    "context": "Why this subject and problem exist",
    "promise": "What this book will make understandable",
    "route": "The mental route through the book"
  },
  "originalTargetWords": 22000,
  "currentTargetWords": 22000,
  "minimumAcceptedWords": 18000,
  "maximumAcceptedWords": 24000,
  "draftingStarted": false,
  "scopeHistory": []
}
```

Record a target change with old and new values, reason, approval status,
`approvalSource`, and evidence. After drafting starts, any reduction requires
explicit user approval. Changing the target to match an undersized manuscript is
retroactive normalization and fails the gate.

### `learning-outline.json`

Record an `authorization` object with `status: approved`, `source: user` or
`explicit-autonomous-run`, and non-empty evidence. Record two to four genuine
`throughlines`. Record every canonical chapter filename, its purpose, and its
prerequisites. Approval applies to the learning progression, not merely a list
of topics.

### `chapter-plans.json`

Create one entry per canonical chapter:

```json
{
  "file": "ch03.md",
  "purpose": "Separate training from inference",
  "prerequisites": ["parameters", "forward calculation"],
  "knowledgeDelta": "Identify whether a model operation is training or inference",
  "groundedExample": "Train an email classifier, then score a new email",
  "concepts": ["training", "inference"],
  "beats": ["retrieve", "contrast", "walk through", "test misconception"]
}
```

The beats are distinct teaching jobs, not a uniform chapter template. Write
orientation before dense terminology. Do not let chapter one become an inventory
of terms the listener has no reason or framework to retain.

### `coverage-ledger.json`

Create one entry for every core concept. Each explanation path records:

- `definition`: what it is;
- `reason`: why it exists or what problem it solves;
- `mechanism`: how it works at the required depth;
- `concreteCase`: where the listener sees or uses it;
- `boundary`, or `boundaryNotApplicableReason` when a boundary would be
  artificial;
- `misconception`: the likely wrong mental model to prevent;
- `expectedAbility`: what the listener should be able to explain, distinguish,
  calculate, recognize, or do;
- `chapterUses`: each chapter and whether the use introduces, retrieves,
  deepens, applies, compares, or corrects the concept.

Terminology exposure is not learning evidence. A row that says only “defined in
chapter three, reused in chapter six” is incomplete.

### `continuity.json`

After every drafted chapter, append a checkpoint containing `afterChapter`,
`termsDefined`, `examplesUsed`, `callbacks`, `promises`, and
`unresolvedQuestions`. Update it before drafting the next chapter. A static note
written before all chapters does not prove sequential continuity.

### `learning-review.json`

Run two independent reviews after substantive revision:

- `structure`: orientation, progression, prerequisites, chapter purpose,
  throughlines, and resolved promises;
- `beginnerReader`: unexplained terms, leaps, weak mechanisms, absent examples,
  misconceptions, boundaries, and whether the expected abilities are plausible.

Each lane records a distinct reviewer, `verdict: pass`, and citation-first
findings. Every finding needs an ID, location, category, evidence, final decision,
and reason. The frontier author makes accepted repairs. Then rerun both reviews
and set `reviewedChapterSHA256` to the final canonical chapter hashes. An
unresolved finding or stale hash fails the gate.

## Gate order

1. Complete `learning-brief.json`, including priorKnowledge and
   openingOrientation.
2. Complete and authorize `learning-outline.json` before canonical drafting.
3. Complete `chapter-plans.json` and `coverage-ledger.json` before each affected
   chapter is drafted.
4. Draft in order and update `continuity.json` after each chapter.
5. Run structural and beginner-reader review, then have the frontier author make
   accepted substantive repairs.
6. Run the bounded humanizer/de-Claudification pass and finish all accepted
   voice edits.
7. Rerun the structural and beginner-reader reviews on those final chapters;
   record final decisions and hashes in `learning-review.json`.
8. Generate the learning receipt:

```bash
python3 skill/scripts/learning_design_qc.py \
  --run-root "$RUN_ROOT" \
  --receipt-out "$RUN_ROOT/research/learning-design-receipt.json"
```

9. Generate the separate final `prose-style-receipt.json` from the same chapter
   hashes.
10. Pass both receipts to `build_book.py`.

Any canonical chapter edit makes both hash-bound reviews stale. Rerun the
affected learning and prose reviews; never edit a receipt by hand.

## Packaging rule

Every new or revised learning book passes:

```bash
--learning-receipt "$RUN_ROOT/research/learning-design-receipt.json" \
--prose-receipt "$RUN_ROOT/research/prose-style-receipt.json"
```

`--legacy-without-learning-receipt` exists only to reproduce an old artifact.
It is forbidden for a new or revised manuscript, new edition, current-workflow
claim, or pedagogical acceptance claim.

## Red flags

Stop and return to development when any of these occurs:

- the opening starts teaching details before providing context, promise, and
  route;
- the outline is a terminology list rather than a learning progression;
- beat sheets or continuity checkpoints are missing and someone proposes
  creating them after the manuscript;
- a coverage ledger measures mentions instead of explanation paths and expected
  abilities;
- the target is reduced because the draft came out short;
- “zero style findings,” “factually correct,” or “audio verified” is offered as
  evidence that the listener can learn from the book.
