# Express Fiction Craft

## Private run artifacts

Keep only this compact evidence under `.build/fiction-audiobooks/<slug>/`:

```text
brief.md
story-bible.md
outline.md
chapters/ch*.md
continuity/rolling.md
continuity/final.md
research/unattended-decisions.json
research/fiction-production-receipt.json
revisions/full-manuscript-review.md
revisions/full-prose-qc.md
dist/
```

`brief.md` records premise, genre/listener promise, exclusions, working title,
form, chapter/word/runtime estimate, the one-sentence length rationale, author
`Dan Fakkeldy`, model contributor, iCloud authorization, privacy, and
conditional-publication state. `story-bible.md` contains only the characters,
world rules, POV/tense/distance, prose controls, ending direction, and public
safety needed to draft and close this book. `outline.md` gives every chapter a
dramatic job, changed state, consequence, exit pressure, and stable recurring
role for casting. Do not create approval gates, a vertical slice, scene cards,
or parallel chapter drafts.

## Craft contract

Treat each principal character as pressure: desire, leverage, contradiction,
limits, and choices must force or close options for others. Draft chapters in
order under one lead writer. Update `continuity/rolling.md` after each accepted
chapter with timeline, location, knowledge, injuries, objects, relationships,
promises, mysteries, and payoffs.

Specify prose through observable controls: narrative distance, sentence
movement, diction, image system, interiority, dialogue texture, humour, and
taboo habits. Never imitate a living author; translate references into those
controls.

Revise in three combined passes:

1. Story: promise, causality, escalation, pacing, reversals, crisis, climax,
   aftermath.
2. Character/continuity: motive, relationship change, POV knowledge, timeline,
   world logic, planted promises, payoffs.
3. Ear/prose: distinct dialogue, distance, rhythm, imagery, repeated
   AI-shaped phrasing, and read-aloud flow.

Record repairs in `full-manuscript-review.md`; record mechanical/style results
in `full-prose-qc.md`. Then read front to back without editing, repair accepted
whole-book findings, reconcile every promise/payoff or deliberate ambiguity,
perform the read-aloud check, and write `continuity/final.md` from final bytes.

## Source segmentation before EPUB freeze

Before EPUB build, one lead writer records the intended speaker for every
block. Treat each uninterrupted narrator, POV, quoted-character, letter,
report, or interlude run as one blank-line-delimited Markdown paragraph and
therefore one XHTML block.

Record one book-wide dialogue-attribution rule and use it consistently:

- The character owns the complete dialogue-and-attribution block; or
- The attribution is its own narrator block.

Never split a sentence merely to increase voice variety. Never encode a speaker
in invisible spans or expect Echo to read `data-speaker`. No model or Echo
inference fills unknown dialogue: revise the source paragraph or record the
speaker explicitly.

After final prose and the portrait cover are embedded, hash and freeze the
EPUB before inventory or casting. Any later EPUB byte change restarts inventory
and plan authoring.

## Private receipt

Create the unchanged schema-v1 receipt with `status: first-listen`,
`productionMode: unattended-first-listen`, `privacy: private`,
`permissionToPublish: false`, `humanReadingStatus: pending`,
`negativeHumanVerdictOverrides: true`, and
`receiptDoesNotCertifyHumanAcceptance: true`.

Bind every `chapters/ch*.md` hash. Bind these exact artifact names to relative
path plus SHA-256:

| Artifact | Evidence path |
|---|---|
| `authorization` | `research/unattended-decisions.json` |
| `storyBible` | `story-bible.md` |
| `continuity` | `continuity/final.md` |
| `revisionReview` | `revisions/full-manuscript-review.md` |
| `proseQC` | `revisions/full-prose-qc.md` |

Set exactly these gates to `pass`: `manuscriptClosed`,
`storyBibleReconciled`, `continuityReconciled`, `revisionPassesCompleted`, and
`proseQCPassed`.

Repair and rerun the affected pass when story, continuity, or prose fails. If
the final manuscript still cannot pass, preserve the run root and stop before
covers, narration, delivery, or publication.

For a story redo, retain unaffected prose only after causal review. Repair the
requested change and every downstream dependency; rerun affected portions of
all three passes, the final front-to-back read, promise/payoff reconciliation,
and read-aloud check. Rewrite final continuity and regenerate the schema-v1
receipt against current chapter and evidence hashes before rebuilding EPUB or
narration. Prior receipt, revision, QC, and package acceptance is stale.
