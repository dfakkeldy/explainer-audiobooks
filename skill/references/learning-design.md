# Fail-Closed Learning Design

Use this schema-v2 contract before canonical drafting and again before packaging
a nonfiction learning audiobook. Read `road-book-mode.md` first. The default
mode assumes the book is heard while driving and delivering mail; select
`focused-study` explicitly when pause, rewind, or visual inspection is part of
the lesson.

The receipt is deliberately narrow. It proves process evidence and an accepted
human pilot. It does not certify learning transfer, and a negative human
listening verdict overrides it.

## Independent verdicts

1. **Curriculum and orientation:** the book starts at the listener's actual
   prior knowledge, names the listening context, preserves a successful earlier
   edition when appropriate, and follows a coherent curiosity-led route.
2. **Chapter teaching:** each chapter has a purpose, prerequisites, knowledge
   delta, problem-before-name terms, an audio working-memory budget, varied
   teaching beats, narrative connection, and real-world grounding.
3. **Blind sequential beginner review:** an independent reviewer hears or reads
   only the manuscript in order, without the outline, ledger, expected
   abilities, or author rationale.
4. **Human comprehension pilot:** the intended listener accepts a hash-bound
   10-to-15-minute narrated pilot before full drafting.
5. **Prose style:** the separate humanizer and de-Claudification pass checks
   voice, rhythm, and model tics without changing the learning architecture.
6. **Packaging and acoustic verification:** EPUB, covers, M4B, sidecar,
   pronunciation, and delivery receipts prove artifact integrity and audio
   behavior.

These verdicts cannot substitute for one another. Factual accuracy, a prose
receipt, or valid media cannot establish comprehension. Human listening remains
the acceptance authority.

## Structured evidence

Maintain these records under `$RUN_ROOT/research/` while the project develops.
Do not reconstruct them after a failed manuscript merely to unlock packaging.
Every record uses `schemaVersion: 2`.

### `evidence-notes.json` and `evidence-notes.md`

Research is its own phase and call. Write a grounded `evidence-notes.md` before
outlining, then bind it with `evidence-notes.json`. Each usable claim has a stable
ID, supported wording, verified source, precise locator, and verification status.
Set `claimPolicy` to `traceable-only`: the outline and manuscript may make only
claims traceable to these notes. Unresolved conflicts remain visible rather than
being silently averaged away.

The JSON record carries `notesPath`, `notesSHA256`, `claims`, and
`unresolvedConflicts`. Source gathering does not decide the curriculum and must
not produce prose for the author to polish.

### `learning-brief.json`

```json
{
  "schemaVersion": 2,
  "learnerOutcome": "What the listener can explain or do",
  "priorKnowledge": "Actual exposure, known terms, and likely gaps",
  "audienceLevel": "beginner",
  "listeningMode": {
    "name": "road-book",
    "primaryContext": "Driving and delivering mail",
    "attentionConstraints": ["eyes unavailable", "single-pass listening"]
  },
  "revisionMode": {
    "name": "new-book",
    "sourceEdition": "",
    "preserve": {
      "governingQuestion": "",
      "narrativeSpine": "",
      "successfulExamples": [],
      "chapterJobs": []
    }
  },
  "openingOrientation": {
    "context": "Why this subject and problem exist",
    "promise": "What this book will make understandable",
    "route": "The mental route through the book"
  },
  "originalTargetWords": 22000,
  "currentTargetWords": 22000,
  "estimatedMinimumWords": 18000,
  "estimatedMaximumWords": 24000,
  "draftingStarted": false,
  "scopeHistory": []
}
```

Use `first-edition-plus` when an earlier edition taught successfully. Record the
source edition and the governing question, narrative spine, successful examples,
and varied chapter jobs to preserve.

Word targets are estimates. Record target changes with old/new values, reason,
approval status, `approvalSource`, and evidence. A reduction after drafting
starts still requires explicit user approval; retroactive normalization fails.
The final word count may fall outside the estimate without failing the learning
gate.

### `learning-outline.json`

Record an approved `authorization`, two to four throughlines, and six to ten
`durableOutcomes` for a beginner road-book. Read `curriculum-patterns.md` and
record `curriculumPattern.name`, `reason`, and `fitEvidence`. Allowed patterns
are `question-led-narrative`, `mechanism-first-spiral`, `end-to-end-trace`, and
`problem-progression`.

For road-book mode, `authorization.source` is `user`. An
`explicit-autonomous-run` may prepare evidence and a proposed outline, but it
cannot stand in for the human outline checkpoint before pilot drafting.

For road-book mode, add `roadBookDesign` with a governing question, narrative
spine, at least two people/history anchors, at least four distinct chapter jobs,
at least two varied real-world applications, and the optional-study boundary.
Add `referenceLayer.items` and `referenceLayer.formats` for material intentionally
kept out of the main listen.

This is an argument-level outline, not a topic list. Record every canonical
chapter filename, purpose, and prerequisites, then divide it into named sections.
Every section records its `job`, `argument`, evidence-note IDs in
`specificClaims`, `throughlineAdvance`, narrative or metaphor `payoff`,
intellectual or emotional `landingBeat`, and `mustNotRepeat`. Outline approval
applies to this learning progression and occurs at a human checkpoint before the
pilot section is drafted.

### `chapter-plans.json`

Each chapter records the existing purpose, prerequisites, `knowledgeDelta`,
`groundedExample`, `concepts`, and at least three distinct beats. It also records:

```json
{
  "newCoreTerms": [
    {
      "term": "inference",
      "problemBeforeName": "A trained sorter must handle tomorrow's envelope."
    }
  ],
  "audioLoad": {
    "temporaryValues": 0,
    "symbolicChainSteps": 0,
    "calculationTreatment": "none",
    "focusedLessonMinutes": 0,
    "concreteReset": "Return to one newly arrived envelope."
  },
  "teachingInfrastructure": {
    "narrativeConnection": "The sorter meets tomorrow's mail.",
    "realWorldApplication": "Postal recognition after training"
  }
}
```

A road-book chapter introduces no more than three new core terms. A
`brief-spoken` calculation carries at most three temporary values and three
symbolic steps. `focused-lesson` is one to five minutes and still capped at five
values/steps. `none` and `optional-study` mean those chains do not appear in the
canonical main listen.

### `coverage-ledger.json`

Every core concept names one `durableOutcome` from the outline and records:

- `definition`, `reason`, `mechanism`, and `concreteCase`;
- `problemBeforeName`;
- one or more `realWorldApplications`;
- `boundary` or `boundaryNotApplicableReason`;
- `misconception` and `expectedAbility`;
- `chapterUses`;
- an `analogy` with `name`, `relationship`, at least two `correspondence`
  mappings, and `limit`, or an `analogyNotApplicableReason`;
- one or more `retrievals` after a chapter gap, each with `freshSituation`,
  `listenerTask`, and `answerPlacement`.

Terminology exposure is not learning evidence. Definitions beside a toy example
are not problem-before-name evidence. Repeating the same invented toy is not
varied real-world grounding.

### `continuity.json`

Draft section by section, never as one whole-book generation. Before each section
call, write one `draftContexts` entry. It must supply the full outline path,
grounded evidence-notes path, style-guide path, the previous section's actual
text or a faithful running summary, this section's job, and its `mustNotRepeat`
list. The draft call consumes those artifacts; it does not recreate them.

After every chapter, append `afterChapter`, `termsDefined`, `examplesUsed`,
`callbacks`, `promises`, `unresolvedQuestions`, `retrievalsCompleted`, and
`listenerLoadNotes`, plus `priorSectionSummary` and `doNotRepeat`. Update the
record before drafting the next section. This is where cumulative terminology,
working-memory load, and repetition risk become visible rather than being
rediscovered after a full draft.

### `comprehension-pilot.json`

Before full drafting, render 10 to 15 representative minutes including the first
technical passage. Record the listener, representative listening context, audio
path and SHA-256, whether the technical passage is included, and one lightweight
human verdict: `continue` or `revise`. Record optional listener notes when the
listener volunteers them; do not require a comprehension questionnaire.

The `humanCheckpoints` object freezes three earlier decisions:

- `voiceSource` binds `voice-source-profile.md`, whether it came from a project
  brief or a private source craft analysis. The persisted profile records craft
  features, not pastiche; `rawSourceExcerptsCommitted` is false.
- `outline` records human approval before the pilot draft.
- `firstSection` records human acceptance before the remaining draft and binds
  the accepted `voice-exemplar.md`. This project-authored section, not copied
  source prose, becomes the concrete voice exemplar for later calls.

`status` must be `accepted`. To authorize full drafting, the `decision` must
carry `verdict: continue`, `authority: listener`, non-empty evidence, and
`recordedBeforeFullDraft: true`. Outline approval, text review, or an agent's
assessment cannot stand in for this record.

### `revision-passes.json`

Revision is a sequence of narrow calls, not one request to "make it better."
Bind `revision-passes.json` to the final canonical chapter hashes. Every pass has
`scope: single-job`, a named reviewer, a passing status, and citation-first
findings with decisions. Required passes are:

- `claim-traceability`: compare every factual claim with the grounded notes;
- `tightening`: remove avoidable repetition and filler without cutting teaching;
- `de-listification`: repair mechanical list rhythm and false symmetry;
- `sentence-rhythm`: vary sentence and paragraph shape without changing voice;
- `ear-pass`: render with Echo, Kokoro, or the governed local narrator and record
  every stumble and every point where the listener loses the thread.

Do not combine these jobs. A clean rhythm pass cannot excuse a factual miss, and
a passing claim check cannot excuse prose that fails in the ear.

### `learning-review.json`

Run two independent final-hash reviews:

- `structure`: orientation, progression, prerequisites, chapter purpose,
  throughlines, and resolved promises;
- `blindSequentialBeginner`: `reviewMode` is `manuscript-only-sequential`,
  `intentionMaterialsWithheld` is true, and `chapterAssessments` cover every
  chapter in order.

Each blind assessment records `plausibleMentalModel`, `confusions`,
`unstableTerms`, and `lostAt`. Each review lane records a distinct reviewer,
`verdict: pass`, and citation-first findings with final decisions. Set
`reviewedChapterSHA256` to the canonical chapter hashes after accepted repairs.

## Gate order

1. Complete the brief and select road-book or focused-study mode.
2. Produce hash-bound grounded evidence notes with a traceable-only claim policy.
3. Preserve a successful earlier edition through first-edition-plus when
   applicable.
4. Build and obtain human approval for the argument-level outline and
   road-book/reference-layer design.
5. Complete chapter plans and coverage paths before the affected pilot prose.
6. Draft the first section, curate it into the voice exemplar, render the
   narrated pilot, and obtain listener comprehension evidence.
7. Only after both first-section and pilot acceptance, draft section by section
   with a complete `draftContexts` input and update continuity after each call.
8. Run structure and blind sequential beginner review; the frontier author
   resolves accepted findings.
9. Run each required single-job revision and complete `revision-passes.json`.
10. Run the bounded humanizer/de-Claudification pass.
11. Rerun both learning reviews on the final chapter hashes.
12. Generate the learning receipt:

```bash
python3 skill/scripts/learning_design_qc.py \
  --run-root "$RUN_ROOT" \
  --receipt-out "$RUN_ROOT/research/learning-design-receipt.json"
```

13. Generate the separate `prose-style-receipt.json` from the same hashes.
14. Pass both receipts to `build_book.py`.

For a readable, non-narrated study appendix, keep it outside `chapters/` and use
`--non-narrated-appendix`. Never name it `ch*.md`.

## Packaging rule and proof boundary

Every new or revised learning book passes both `--learning-receipt` and
`--prose-receipt`. `--legacy-without-learning-receipt` is old-artifact
reproduction only.

The schema-v2 receipt records `learningAuthority.holder: human-listener`,
`negativeVerdictOverridesReceipt: true`, and
`receiptDoesNotCertifyTransfer: true`. Any later negative listening evidence
invalidates the learning acceptance claim even when hashes and artifacts remain
technically valid.

## Red flags

Stop and return to development when:

- the outline is a terminology inventory;
- research, outlining, drafting, and revision are collapsed into one call;
- a section argument cites a claim absent from `evidence-notes.json`;
- a draft call lacks the full outline, previous-section context, or no-repeat list;
- raw private source excerpts are committed or the author is asked for a pastiche;
- "deeper" expands vocabulary, derivations, or variants instead of applications,
  consequences, comparisons, failure cases, and retrieval;
- a chapter exceeds three new core terms;
- spoken arithmetic needs more than three temporary values or symbolic steps;
- the repeated toy is the only real-world grounding;
- the beginner reviewer receives the ledger or expected abilities;
- someone proposes full drafting before the narrated pilot;
- revision is one vague "make it better" pass;
- the ear-pass is inferred from text inspection instead of rendered listening;
- word count is used to force more exposition;
- a receipt, style score, or valid M4B is offered as proof of comprehension.
