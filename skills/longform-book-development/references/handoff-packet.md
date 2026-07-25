# Handoff Packet

Use this shape when handing a developed longform book project to
`$custom-learning-audiobook`.

## Packet Sections

```markdown
# <Working Title> Handoff Packet

## Production Request

Use `$custom-learning-audiobook` to turn this approved book plan into a complete
learning audiobook package. Include the approved interior pictures as EPUB
figures, build EPUB and combined Markdown, render Echo audio when available, and
report any blockers honestly.

## Status

- Privacy:
- Permission to publish:
- Length target:
- Original target:
- Target history and approval evidence:
- Audience:
- Prior knowledge:
- Listening mode: road-book / focused-study
- Primary listening context: driving and delivering mail / other
- Attention constraints:
- Revision mode: new-book / first-edition-plus
- Source edition and preserved governing question, narrative spine, successful
  examples, and chapter jobs:
- Voice/tone:
- Voice-source profile path/hash and use boundary (craft features, not pastiche):
- Source-confidence target:
- User approval status:

## Core Promise

What the listener should understand, feel, or be able to do after finishing.

## Opening Orientation

- Context: why the subject or problem exists.
- Promise: what this book will make understandable or doable.
- Route: the learning path the listener will follow.

## Boundaries

What to include, avoid, simplify, keep private, or treat as educational-only.

## Approved Learning Outline

Read `../../../skill/references/curriculum-patterns.md` (path relative to this
file; from the skill root it is `../../skill/references/`), then record:

- Curriculum pattern:
- Selection reason:
- Learner-and-subject fit evidence:
- Pattern-change approval evidence, if changed after approval:
- Durable learner outcomes (six to ten for a beginner road-book):
- Governing question:
- Narrative spine:
- People and history anchors:
- Varied real-world applications:
- Chapter-job variety:
- Optional-study boundary for calculations, symbolic chains, and specialist
  terminology:

| Ch | Working title | Purpose | Prerequisites | Knowledge delta | New core terms and problem before name | Audio working-memory budget | Narrative/real application | Core beats | Sources | Figures |
|---|---|---|---|---|---|---|---|---|---|---|

Record who approved the progression, whether approval came from the user or an
explicit autonomous-run request, and the evidence for that authorization.

### Argument-level section map

For every section, record the section ID, job, argument, specific claim IDs from
`research/evidence-notes.json`, throughline advance, narrative or metaphor
payoff, intellectual or emotional landing beat, and what it must not repeat.

| Section | Job | Argument | Claim IDs | Throughline advance | Payoff | Landing beat | Must not repeat |
|---|---|---|---|---|---|---|---|

## Throughlines

Recurring ideas, metaphors, or tensions that should tie chapters together.

## Concept Explanation Paths

For every core concept, record its definition, reason, mechanism, concrete case,
useful boundary or not-applicable reason, likely misconception, expected listener
ability, durable outcome, problem before name, varied real-world applications,
analogy relationship/correspondences/limit (or omission reason), planned chapter
uses, and retrieval after a chapter gap. Exposure or reuse alone is not an
explanation path.

## Road-Book Review And Pilot

- Blind sequential beginner review: manuscript only, in order; withhold outline,
  ledger, expected abilities, and author rationale.
- Per-chapter review output: plausible mental model, confusions, unstable terms,
  and exact lost points.
- Narrated pilot length: 10 to 15 minutes.
- Pilot content: opening orientation plus the first technical passage, no more
  than three durable terms, varied real applications, and a fresh-example
  retrieval.
- Pilot listening context: driving and delivering mail when safe and
  representative, or the listener's stated equivalent.
- `research/comprehension-pilot.json`: exact audio path/hash, one lightweight
  human `continue` or `revise` verdict, optional listener notes, and decision
  evidence recorded before full drafting; do not require comprehension questions.
- Human checkpoint: approve the argument-level outline before pilot drafting.
- First-section checkpoint: accept the project-authored first section as
  `research/voice-exemplar.md` before drafting the remainder.

An autonomous-run request can authorize preparation up to the checkpoint. It
cannot replace human outline approval, first-section acceptance, or comprehension
evidence, and it cannot authorize the full canonical manuscript before the pilot
is accepted.

## Source Plan

User-provided files, live research needs, Open Notebook corpora, primary sources,
or source-quality constraints. Include retrieval dates for live web sources.

Plan `research/evidence-notes.md` and `research/evidence-notes.json` as the
research-phase artifact. Each allowed claim gets a stable ID, verified source,
precise locator, uncertainty/limits, and `verificationStatus: verified` under a
`traceable-only` policy. Research extraction may not become a substitute draft.

## Voice-Source Profile

When the user names a private book or audiobook, analyze it locally into
`research/voice-source-profile.md`: opening move, evidence-to-example movement,
plain-language mechanism, direct address, humor boundary, uncertainty, rhythm,
practical landing, and visual habits that need audio adaptation. Keep raw source
excerpts and files out of Git. The production request is for high-level craft
features, not pastiche; the accepted first section becomes the reusable voice
exemplar.

## Section Drafting Contract

Draft section by section. Every call receives the full outline, grounded
evidence IDs, approved voice exemplar, previous section text or a faithful
running summary, the current section job, and its must-not-repeat list. Production
records these inputs in `research/continuity.json.draftContexts` before each call.

## Narrow Revision Contract

Complete `research/revision-passes.json` as separate single-job passes for
claim-traceability, tightening, de-listification, sentence-rhythm, and ear-pass.
Render the ear-pass with Echo or Kokoro and record narration stumbles and every
place the listener loses the thread. A vague "make it better" pass is not valid.

## Pronunciation Plan

List the terms the listener explicitly wants checked, plus technical names and
variants the author expects to be risky. Production records these in
`research/pronunciation-plan.json`, makes a governed partial-render reel, and
requires the listener's accepted human listening evidence before full audio.

| Term | Spoken variants | Source | Why it matters | Expected chapters |
|---|---|---|---|---|

## Figure Plan

| ID | File path | Placement | Alt text | Caption | Provenance/license | Public-safe? |
|---|---|---|---|---|---|---|

Put final package images under `chapters/images/` before running
`build_book.py`. Insert them as standalone Markdown paragraphs:

```markdown
![Useful alt text](images/example.png "Caption shown under the figure")
```

Image paths resolve relative to the chapters directory. Supported formats are
PNG, JPEG, GIF, SVG, and WebP. Do not include pictures whose rights or privacy
status are unclear in a public package.

## Style Notes

Preferred voice, pacing, examples, jokes, repeated language to avoid, vocabulary
to introduce, and any sample passage the user liked. Record the humanizer
decision here:

- Humanizer pass: required / optional / skipped
- De-Claudification gate: required
- AI-writing patterns to avoid:
- Disliked phrase families:
- Honesty announcements to avoid (`honestly`, `the honest answer`, `to be
  honest`, and variants); express epistemic honesty through precise claims and
  uncertainty instead:
- Voice-design control panel: the ten `voice-design.md` dial settings recorded
  for this project (narrator stance, sentence movement, diction, evidence
  handling, concession, humour, exposition, story density, emphasis, direct
  address):
- Positive voice sample: 3-5 project-specific sample sentences from
  `voice-design.md`, required rather than optional — a handoff carrying only
  prohibitions reproduces the flattened-prose problem downstream:
- Voice constraints and things that must not be invented or copied:
- Voice sample path, if any:

## Open Questions

Only questions that must be answered before production. If none, say so.

This is the authoritative required-field checklist for the packet (the skill
body deliberately keeps no second copy). If prior knowledge, listening/revision
mode, opening orientation, target history,
approval evidence, grounded evidence notes, voice-source profile, argument-level
section map, durable outcomes, concept/working-memory budgets, chapter
prerequisites, knowledge delta, complete concept explanation paths,
problem-before-name evidence, teaching beats,
throughlines, analogy/retrieval paths, listener pronunciation risks, section
draft contexts, narrow revision
passes, blind review instructions, or first-section/narrated pilot design are
incomplete, mark this packet **development draft — not
authorized for pilot or canonical production**.

## Acceptance Criteria

What counts as done: EPUB/Markdown, cover, audio, alignment sidecar, README,
visual provenance, copied locations, or public repo package.
```
