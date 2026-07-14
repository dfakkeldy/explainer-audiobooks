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
- Anything to include, avoid, simplify, or keep private?

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
- `learning-brief.json` - learner outcome, actual prior knowledge, opening
  orientation, original/current target and accepted range, drafting status, and
  approved scope-change history.
- `sources.md` - links/files used, source-quality labels, retrieval date.
- `fact-pack.md` - facts the manuscript may rely on.
- `outline.md` - chapter plan and learning throughlines.
- `learning-outline.json` - approved progression, approval evidence, chapter
  purposes/prerequisites, and two to four throughlines.
- `chapter-plans.json` - chapter purpose, prerequisites, knowledge delta,
  grounded example, concepts, and varied teaching beats.
- `coverage-ledger.md` - each core concept's introduction, deliberate later use,
  example, explanation depth, expected listener ability, and reason for any
  repetition.
- `coverage-ledger.json` - complete explanation paths required by the shared
  learning-design gate.
- `continuity.md` - terms, analogies, examples, callbacks, and open promises the
  frontier author must carry forward between Markdown chapters.
- `continuity.json` - one structured checkpoint after every drafted chapter.
- `learning-review.json` - independent structure and beginner-reader verdicts
  bound to final chapter hashes.

Follow `../../skill/references/learning-design.md`. Do not create these records
retroactively to normalize a failed manuscript; maintain them during planning,
sequential drafting, revision, and final learning review.

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
