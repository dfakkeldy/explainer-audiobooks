# Custom Learning Audiobook Skill Design

Date: 2026-07-06

## Purpose

Create a new `custom-learning-audiobook` skill for listener-specific Echo beta
books. The skill starts from a low-friction topic request such as "I want to
learn small engine repair", asks a few helpful clarification questions when
needed, performs the research itself, and produces a complete Echo-ready delivery
folder.

This is separate from the existing `explainer-audiobook` skill. The existing
skill remains the technical/codebase-grounded explainer workflow. The new skill
is for custom learning requests from coworkers, friends, local testers, and
other beta users.

## Goals

- Make the requester feel helped, not assigned homework.
- Produce books that are listenable, grounded, and specific to the requester's
  goal.
- Default to a realistic beta-test length that people can finish.
- Use one lead writer for manuscript coherence.
- Use subagents for research, fact packs, critique, and QC.
- Produce artifacts that can be tested directly in Echo.
- Keep public/private handling explicit so private books do not leak into the
  repo or public folders.

## Non-Goals For V1

- Do not build `.echo` ZIP archives yet.
- Do not generate flashcards or study decks yet.
- Do not require Open Notebook for every request.
- Do not make the requester provide sources before the skill can proceed.
- Do not replace the existing `explainer-audiobook` skill.

## Skill Split

### New Skill: `custom-learning-audiobook`

Use this skill when the user asks to make a custom learning audiobook, beta-test
book, personalized audiobook, listenable guide, or Echo-ready learning package
from a topic request.

The skill should handle:

- frictionless intake,
- topic clarification,
- public/deep/Open Notebook research selection,
- source-quality labeling,
- one-lead-writer drafting,
- research and QC subagents,
- EPUB, Markdown, M4B, alignment, and cover outputs,
- delivery copies to iCloud Books and the repo when allowed.

### Existing Skill: `explainer-audiobook`

Keep the existing technical explainer skill for long, worked-example books
grounded in codebases, products, or specialized systems. Update its narrator
defaults:

- preferred narrator: `am_michael`
- fallback narrator: `am_puck`
- do not use `af_heart` as the default

## Intake Flow

The requester should only need to send a plain-language topic. Sources are
optional.

Ask 3-5 clarifying questions only when they materially improve the book:

- What should the listener be able to do after finishing?
- Is the listener brand new, rusty, or already familiar?
- Is this practical, curiosity-driven, work-related, or hobby-related?
- Is there a specific situation the book should prepare them for?
- Anything to include, avoid, or keep simple?

Avoid making the requester look things up. If sources are missing, the skill
researches.

## Length Defaults

- Standard beta book: about 2 hours, roughly 18,000-22,000 words.
- Deep book: about 4 hours, roughly 40,000-45,000 words.
- Sampler: 45-75 minutes when the topic is vague or the requester seems lightly
  committed.

For workplace beta recruitment, default to the standard beta book unless the
request is unusually detailed or the user explicitly asks for a deep treatment.

## Research Modes

### Quick Research

Use for simple, low-risk topics. Perform a public source scan, favoring official
or well-established sources, then build a concise fact pack.

### Deep Research

Use for standard beta books when the subject benefits from more grounding.
Perform a broader source sweep, compare source quality, and capture citations or
source notes for the fact pack.

### Open Notebook Research

Use Open Notebook when one of these is true:

- there is already a curated corpus for the topic,
- the topic is likely to recur,
- the book depends on private/local documents,
- the subject benefits from a stable source shelf,
- the user asks for an especially deep or source-grounded book.

Open Notebook is optional in V1, not a required dependency.

## Sensitive Topic Guardrails

For medical, legal, financial, safety-critical, workplace-private, customer,
confidential, or professional-advice topics:

- refuse topics that cannot be handled safely,
- narrow the scope when possible,
- frame the book as educational overview rather than advice,
- avoid copying sensitive source text into public artifacts,
- do not place private books in the public repo or public-facing folders.

## Writing Workflow

Use one lead writer for the manuscript. Do not fan out chapter writing by
default.

Subagents are appropriate for:

- research,
- source summaries,
- fact packs,
- outline critique,
- missing-source checks,
- repetition checks,
- hallucination checks,
- sensitive-topic/privacy review,
- narration QC.

If a future fast mode uses chapter fan-out, it must end with a lead-author
rewrite or continuity pass before delivery. That mode is not the V1 default.

## Voice And Narration

Narrator defaults:

- preferred narrator: `am_michael`
- fallback narrator: `am_puck`
- avoid defaulting to `af_heart`

Record the narrator used in the package manifest/readme. The writing voice
should stay warm, spoken, concrete, and useful. It should avoid generic AI
over-enthusiasm, repeated chapter openings, repeated disclaimers, and repeated
"this matters because" beats.

## Output Package

V1 produces a named delivery folder containing:

- `<slug>.epub`
- `<slug>.md`
- `<slug>.m4b`
- `<slug>.alignment.json`
- `cover.png`
- `README.md` or `manifest.json`

The README or manifest records:

- title,
- requester/topic,
- length mode,
- word count,
- runtime,
- chapter count,
- narrator,
- research mode,
- source-confidence label,
- sensitive-topic guardrails if any,
- whether the package is private or public-safe.

## Delivery Locations

Always keep the canonical build output in the skill's build/output directory for
the run.

If the book is public-safe:

1. Copy the finished package to:
   `/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books`
2. Add a copy to the repo in an appropriate public-safe location, such as
   `books/<slug>/`, following the existing repo conventions.

If the book is private:

1. Do not copy it into the public repo.
2. Do not copy private generated artifacts into public KB pages.
3. Keep it in the private project/delivery location chosen for that run.
4. Optionally copy it to the iCloud Books folder only if the user explicitly
   wants that private reading copy.

Examples of private books include client/prospect books, books with workplace
details, books based on private documents, or books containing non-public
strategy.

## QC Gates

Before delivery:

- EPUB validates.
- M4B metadata and duration are checked with `ffprobe`.
- Alignment JSON parses and has anchors.
- Runtime, chapter count, word count, and narrator are reported.
- Prose is scanned for repeated phrases, code-ish narration artifacts, and
  obvious privacy/safety issues.
- Source confidence is labeled as quick, deep, Open Notebook, user-supplied, or
  mixed.
- Private/public-safe status is recorded before copying to repo or iCloud Books.

## V2 Candidates

- `.echo` archive packaging.
- Generated Echo JSON study decks.
- Optional Anki/APKG export.
- Portable source anchors in generated deck cards.
- Open Notebook corpus creation helpers for recurring topic families.
- Intake form automation from `learn@kinnokilabs.com`.

## Implementation Notes

- Reuse existing `explainer-audiobook` scripts where possible:
  `build_book.py`, cover generation, EPUB assembly, and narration-style checks.
- Add only the new pieces that are genuinely different: intake, research-mode
  routing, single-lead-writing instructions, package copy rules, privacy status,
  and narrator defaults.
- Keep the new skill concise and route detailed reusable guidance into reference
  files rather than making `SKILL.md` too long.
