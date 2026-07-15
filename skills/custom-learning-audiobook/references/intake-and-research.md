# Intake And Research

Use this reference before asking the requester questions or collecting sources.

## Intake Contract

The minimum viable request is a plain topic: "I want to learn small engine
repair." Do not require sources. If the topic is usable, proceed with sensible
defaults.

Ask only questions that materially improve the book:

- What should the listener be able to do or understand after finishing?
- Is the listener brand new, rusty, or already familiar?
- What has been confusing, too shallow, or too repetitive in other explanations?
- Is this practical, curiosity-driven, work-related, or hobby-related?
- Is there a specific situation the book should prepare them for?
- Will they usually hear it while driving and delivering mail, or can they stop,
  rewind, and inspect study material? Default to `road-book` for Dan/internal
  listening when no different context is given.
- Anything to include, avoid, simplify, or keep private?
- Has the listener named a private book or audiobook whose enjoyable technical
  craft should inform the project? If so, analyze it locally into high-level
  craft features; do not copy source passages into the repository or ask for a
  close pastiche.

For workplace/flyer beta requests, keep the tone casual and low-pressure. The
offer is a limited beta test, not an unlimited custom-book service.

## Public, Private, Sensitive

Classify the book before research:

| Status | Use when | Routing |
|---|---|---|
| Public-safe | General topic, no private person/client/workplace details, permission to share | May copy to `books/<slug>/` and public sample library |
| Private | Client/prospect book, private documents, personal strategy, or no permission to publish | Keep out of public repo and public KB |
| Sensitive/high-stakes | Medical, legal, financial, safety-critical, confidential, customer, workplace-private, or professional advice | Refuse, narrow, or frame as educational overview |

Public-safe wording for requester consent:

> With your permission, public-safe books may be added to the learning audiobook
> library so other people can use them too.

## Research Modes

| Mode | Use when | Output |
|---|---|---|
| Quick | Low-risk, simple, stable topic | Concise fact pack with source notes |
| Deep | Standard beta book or topic benefits from grounding | Broader source sweep, source-quality comparison, citations |
| Open Notebook | Reusable corpus, private/local docs, repeated topic family, or especially deep book | Stable source shelf plus cited fact pack |
| User-supplied | Requester gives documents/links | Use those first; label gaps |
| Mixed | Any combination above | Say which claims came from which source class |

For current facts, changing rules, recommendations, health/legal/financial, or
any topic where stale information could mislead the listener, browse live
sources and prefer primary/official references.

## Research Notes Shape

Save notes under `research/`:

- `brief.md` - request, assumptions, audience, length, public/private status.
- `learning-brief.json` - learner outcome, actual prior knowledge, audience
  level, road-book/focused-study context, first-edition-plus/new-book revision
  mode, opening orientation, original/current word estimate and estimated range,
  drafting status, and approved scope-change history.
- `sources.md` - links/files used, source-quality labels, retrieval date.
- `evidence-notes.md` - stable claim IDs, verified source and precise locator,
  supported wording, uncertainty, and conflicts. This is the grounded research
  artifact the outline and writer consume.
- `evidence-notes.json` - hash binding for the notes, `traceable-only` claim
  policy, verified claim records, and unresolved conflicts.
- `fact-pack.md` - chapter-specific selection from the grounded evidence notes.
- `voice-source-profile.md` - high-level craft analysis of a user-approved brief
  or private source. Record opening, evidence-to-example movement,
  plain-language mechanism, direct address, humor boundary, uncertainty,
  rhythm, practical landing, and visual-to-audio adaptations. Keep raw excerpts
  and source files out of Git.
- `outline.md` - chapter plan and learning throughlines.
- `learning-outline.json` - approved progression, durable outcomes, road-book
  governing question/narrative/people/history/real-world applications,
  optional-study boundary, approval evidence, chapter purposes/prerequisites,
  two to four throughlines, and an argument-level section map with jobs,
  arguments, specific claim IDs, throughline advances, payoffs, landing beats,
  and must-not-repeat constraints.
- `chapter-plans.json` - chapter purpose, prerequisites, knowledge delta,
  grounded example, concepts, problem-before-name terms, audio working-memory
  budget, narrative/real-world infrastructure, and varied teaching beats.
- `coverage-ledger.md` - each core concept's introduction, deliberate later use,
  example, explanation depth, expected listener ability, and reason for any
  repetition.
- `coverage-ledger.json` - complete explanation, analogy, application, and
  retrieval paths required by the shared learning-design gate.
- `continuity.md` - terms, analogies, examples, callbacks, open promises, and a
  faithful running summary the frontier author carries between sections.
- `continuity.json` - one forward-context input per planned section and one
  structured learning checkpoint after every drafted chapter. Every section
  input includes the full outline, evidence, style profile, previous section,
  job, and must-not-repeat list.
- `learning-review.json` - independent structure and blind sequential beginner
  verdicts bound to final chapter hashes.
- `comprehension-pilot.json` - the intended listener's accepted 10-to-15-minute
  narrated pilot, exact audio hash, representative context (normally driving and
  delivering mail), own-words explanation, fresh-example response, lost points,
  pre-full-draft decision, bound voice-source profile, human outline approval,
  and accepted first-section `voice-exemplar.md`.
- `revision-passes.json` - final-hash, separate single-job passes for claim
  traceability, tightening, de-listification, sentence rhythm, and a rendered
  ear-pass with stumbles and lost-thread locations.
- `pronunciation-plan.json` - listener-named, coverage-ledger, and author-found
  terms requiring an early spoken probe. Record singular/plural or other
  variants separately; for example, include both `hyperparameter` and
  `hyperparameters` when they occur. The plan starts pending and becomes
  accepted only through hash-bound human listening evidence.

Follow `../../skill/references/road-book-mode.md` and
`../../skill/references/learning-design.md`. Do not create these records
retroactively to normalize a failed manuscript; maintain them during planning,
pilot listening, section-by-section drafting, narrow revision, and final learning
review. Full drafting stops until the human accepts the outline, first-section
voice exemplar, and comprehension pilot.

Source-confidence labels:

- `quick` - enough for a friendly overview, not exhaustive.
- `deep` - multiple source classes compared.
- `open-notebook` - grounded in a curated corpus.
- `user-supplied` - mainly from requester material.
- `mixed` - combines public and private/user material.

## Sensitive Topic Handling

When a sensitive topic is still useful, narrow the scope:

- Replace "what should I do medically/legally/financially?" with "how to
  understand the basic concepts and questions to ask a professional."
- Replace workplace/customer specifics with a generalized scenario.
- Keep private source text out of public artifacts.
- Put an educational-only note in the README/manifest.

If a safe educational framing is not possible, refuse the book and offer safer
adjacent topics.
