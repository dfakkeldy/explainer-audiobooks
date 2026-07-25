# Fail-Closed Learning Design

Contents: Independent verdicts · Structured evidence (per-record contracts for
`evidence-notes.json`, `learning-brief.json`, `learning-outline.json`,
`chapter-plans.json`, `coverage-ledger.json`, `continuity.json`,
`comprehension-pilot.json`, `revision-passes.json`, `learning-review.json`) ·
Gate order · Packaging rule and proof boundary · Red flags.

Use this schema-v2 contract before canonical drafting and again before packaging
a nonfiction learning audiobook. Read `road-book-mode.md` first. The default
mode assumes the book is heard while driving and delivering mail; select
`focused-study` explicitly when pause, rewind, or visual inspection is part of
the lesson.

The receipt is deliberately narrow. In `governed-final`, it proves process
evidence and an accepted human pilot. In `unattended-first-listen`, it proves the
same non-human process evidence while recording the human pilot as pending.
Either receipt status does not certify learning transfer, and a negative human
listening verdict overrides both. Read `unattended-production.md` before
choosing the lane.

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
4. **Comprehension pilot:** governed-final requires the intended listener to
   accept a hash-bound narrated pilot. Unattended-first-listen requires a
   hash-bound editorial pilot decision and keeps human comprehension pending.
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
`unresolvedConflicts`. A conflict may be a concise non-empty string. Prefer a
structured record when traceability matters: give it a unique `id`, the
`question`, one or more known `claimIds`, the competing readings in `conflict`,
and a `status` that preserves the safe wording boundary. Source gathering does
not decide the curriculum and must not produce prose for the author to polish.

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
    "priorEditionExists": false,
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

For unattended production, also add `productionMode` with
`name: unattended-first-listen`, the request evidence, and the relative path and
SHA-256 of `research/unattended-decisions.json`. The decisions receipt must keep
the run private, set publication permission false, record delivery intent and
every inferred choice, and set `humanListeningStatus: pending`. If
`productionMode` is absent, validation defaults to `governed-final`.

`revisionMode.priorEditionExists` is required and has no default: the mode is
an answered question, not a starting point, so a brief can never reach
`new-book` by simply omitting the question. When `priorEditionExists` is
`true`, `name` must be `first-edition-plus`; a brief that declares a prior
edition and still asks for `new-book` fails validation, because a revision
that discards a working narrative spine is how a working book gets worse. When
`priorEditionExists` is `false`, `new-book` is valid.

Use `first-edition-plus` when an earlier edition taught successfully. Record the
source edition and the governing question, narrative spine, successful examples,
and varied chapter jobs to preserve.

A listener saying "I didn't learn X" is an instruction to add X's missing
foundation into the existing spine. It never authorizes re-planning the book
around X. *The Question Machine*'s first edition traced Descartes through
McCulloch and Pitts to backpropagation and taught successfully; feedback that a
listener still hadn't grasped what a neural network is led the next edition to
delete that lineage and replace it with mathematics. The lineage was the
explanation, not decoration competing with the mechanism for word budget, and
removing it left a vacuum only notation filled — unfollowable to a listener who
is driving. A correct revision records where the new material inserts into the
spine and names what stays; it does not discard the spine to make room.

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

For governed-final road-book mode, `authorization.source` is `user`. For a
hash-bound unattended-first-listen run, use `explicit-autonomous-run` and record
the editorial evidence. This authorization permits a private first-listen
candidate, not a human learning-acceptance or publication claim.

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

Draft section by section by default, never as one whole-book generation. Before
each call, write one `draftContexts` entry. It must supply the full outline path,
grounded evidence-notes path, style-guide path, the previous section's actual
text or a faithful running summary, the current job, and its `mustNotRepeat`
list. The draft call consumes those artifacts; it does not recreate them.

If the listener explicitly authorizes a faster workflow, the same frontier
author may cover the remaining sections of one chapter in a single call. Record
a `section` ID ending in `-batch`, every covered outline ID in `batchSections`,
a one-for-one `sectionJobs` list, and an in-run
`fastTrackAuthorizationPath`. A batch may not cross chapters, duplicate a
section already covered by the calibrated first-section call, or expand into a
whole-book generation. The authorization changes call granularity; it does not
waive any section job, evidence boundary, or continuity input.

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

In governed-final, the normal `status` is `accepted`, the object uses
`humanCheckpoints`, and the decision carries `authority: listener`. If the
listener explicitly declines even the lightweight pilot listening checkpoint
and directs production to continue, `status` may instead be
`waived-by-listener`. Record `comprehensionEvidence.status` as
`not-collected-listener-waived`, with `waivedBy`, `waivedAt`, and `reason`, plus
a plain-language `validationBoundary`. The waiver authorizes production; it is
not evidence of comprehension or learning transfer.

In unattended-first-listen,
`status` is `first-listen`, the object uses `editorialCheckpoints`, outline and
first-section statuses are `editorially-approved` and
`editorially-accepted`, and the decision carries `authority: editorial-review`.
Both lanes require non-empty evidence and `recordedBeforeFullDraft: true`.
Editorial review never stands in for a later human acceptance claim.

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

## Patch revisions

The listener's ordinary workflow is asynchronous: request a book at night,
listen the next day, and return notes. Those notes name specific chapters with
specific problems, and the correct response is a patch, not a rewrite: only
the chapters named in the change list get redrafted, every other chapter is
preserved byte-for-byte, and only the redrafted chapters get re-narrated. The
change list decides which chapters move; it does not reopen the outline, the
narrative spine, or any chapter it does not name.

Because a fix in one chapter can leave a seam with its neighbor, re-check
continuity on the immediate neighbors of every changed chapter — the chapter
immediately before and immediately after — even though their text is
unchanged. A repaired chapter 4 can still break a callback, a promise, or a
`mustNotRepeat` boundary in chapter 5. Record that re-check in
`continuity.json` the same way any other continuity pass is recorded.

The safety property this protects — not a quality gate, and it never reads or
judges prose — is that every chapter absent from the change list keeps an
identical SHA-256 before and after the patch. `learning_design_qc.py` already
binds chapter hashes into every receipt (`chapter_hashes`, `chapterSHA256`);
`verify_patch_revision_preserved_chapters` reuses that same hashing rather than
inventing a parallel one:

```bash
python3 skill/scripts/learning_design_qc.py \
  --verify-patch-preservation \
  --run-root "$RUN_ROOT" \
  --previous-receipt "$RUN_ROOT/research/learning-design-receipt.json" \
  --changed-chapters ch04.md
```

A failure here means silent loss in a chapter the change list did not name —
not a prose defect. Do not resolve it by adding the chapter to the change list
after the fact; that requires the listener's sign-off, since it changes what
the patch claims to have touched.

## Gate order

1. Complete the brief and select road-book or focused-study mode.
2. Produce hash-bound grounded evidence notes with a traceable-only claim policy.
3. Preserve a successful earlier edition through first-edition-plus when
   applicable.
4. Build the argument-level outline and road-book/reference-layer design. Obtain
   human approval in governed-final or hash-bound editorial authorization in
   unattended-first-listen.
5. Complete chapter plans and coverage paths before the affected pilot prose.
6. Draft the first section, curate it into the voice exemplar, render the
   narrated pilot, and obtain the lane's human or editorial evidence or an
   explicit governed-final listener waiver.
7. Only after the first-section and pilot checkpoints, draft section by section
   with a complete `draftContexts` input and update continuity after each call.
   An explicitly authorized fast-track may use one chapter-sized batch at a time
   under the bounded contract above.
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
`--prose-receipt`. A `pass-with-listener-waiver` learning receipt is valid only
because it records that comprehension evidence was not collected; it does not
convert the waiver into learning evidence. `--legacy-without-learning-receipt` is old-artifact
reproduction only.

The governed-final schema-v2 receipt records `status: pass` and
`learningAuthority.holder: human-listener`. A governed listener waiver records
`status: pass-with-listener-waiver`,
`humanComprehensionPilot: waived-by-listener`, and
`comprehensionEvidenceStatus: not-collected-listener-waived`. The unattended receipt records
`status: first-listen`, `humanComprehensionPilot: pending`, and
`learningAuthority.holder: human-listener-pending`. Both record
`negativeVerdictOverridesReceipt: true` and
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
