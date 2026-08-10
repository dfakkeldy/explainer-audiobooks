# Make your own

The repository has four book-making entry points. The direct
[`audiobook`](../skill/) skill researches, writes, revises, packages, narrates,
and delivers one grounded nonfiction audiobook. Three companion skills handle
longform nonfiction development and fiction.

## Install

Keep a checkout of this repository available: the main skill uses supporting
references, scripts, and Echo narration tooling elsewhere in the checkout. For
Claude Code, link the direct audiobook skill into your personal skills folder:

```bash
mkdir -p ~/.claude/skills
ln -s "$(pwd)/skill" ~/.claude/skills/audiobook
```

You can link the development and fiction skills the same way when you want
their triggers:

```bash
ln -s "$(pwd)/skills/longform-book-development" ~/.claude/skills/longform-book-development
ln -s "$(pwd)/skills/fiction-book-development" ~/.claude/skills/fiction-book-development
ln -s "$(pwd)/skills/fiction-audiobook" ~/.claude/skills/fiction-audiobook
```

The current repository workflow runs its scripts with
`/usr/local/bin/python3`, which must have Pillow installed. Cover production is
mandatory: every new book uses coordinated portrait and square art. The paired
renderer requires ImageMagick for normalized PNG output and artwork comparison;
it can also use `rsvg-convert` from librsvg for SVG rasterization. A missing
interpreter or renderer is a setup problem to fix, not a reason to publish a
coverless edition.

Narration uses the repository's governed Echo support under
[`skills/echo-narration/`](../skills/echo-narration/). Its setup and accepted
artifact checks are documented in
[`narrating.md`](../skills/echo-narration/references/narrating.md).

## Choose the right entry point

- **[`audiobook`](../skill/)** — make one grounded nonfiction book now.
- **[`longform-book-development`](../skills/longform-book-development/)** —
  shape a nonfiction idea over several sessions, including its sources,
  outline, figures, reviews, and complete production handoff.
- **[`fiction-book-development`](../skills/fiction-book-development/)** — plan,
  draft, continue, or revise a novel, novella, or story collection through an
  accepted Markdown manuscript.
- **[`fiction-audiobook`](../skills/fiction-audiobook/)** — turn a fiction
  premise or approved manuscript into a complete Echo listening package.

## Ask for a nonfiction book

Say something like:

> Make me a ~4-hour beginner audiobook on **WebSockets**, taught through **my `chatterbox` repo**. Warm, spoken, no code read aloud.

A direct request settles five things in one intake:

1. the subject and what the listener should be able to do afterward;
2. the audience;
3. what the audience already knows;
4. the approximate length; and
5. the real repo, product, place, or document that should ground the book.

A complete handoff from `longform-book-development` supplies those decisions
instead, so the production skill does not repeat the intake. After either
route, it states the title, angle, chapter count, and estimated runtime, then
starts without another approval pause.

## What the nonfiction workflow does

1. **Research** — write source-traceable evidence notes, a fact pack for every
   chapter, and a story ledger whose real stories have actors, place, date,
   source, concept, and reversal.
2. **Outline** — build a question-led argument with durable outcomes, a
   narrative spine, varied chapter jobs, throughlines, grounded cases, and
   purposeful returns.
3. **Draft** — one frontier model authors every canonical section in sequence
   and carries a compact continuity note. Bounded workers may research, verify,
   render, assemble, and report; they do not replace chapters.
4. **Write for listening** — define terms plainly, name the real things the
   listener should remember, support drift and re-entry, use practical
   situation-choice-consequence examples, and add spoken `Key points`
   checkpoints at natural learning boundaries.
5. **Revise** — run separate claim-traceability, tightening,
   de-listification, sentence-rhythm, and rendered ear passes. A blind beginner
   then reports the mental model formed and the exact point where it breaks.
   Prose QC and a bounded humanizer pass follow; the frontier author owns every
   substantive repair.
6. **Produce** — render exactly three coordinated portrait/square cover pairs,
   select the strongest complete pair, build the EPUB and combined Markdown,
   narrate the chaptered M4B, and verify the finished package.
7. **Deliver** — Dan's personal workflow has standing authorization for a
   private iCloud Books copy with editable source. Every other user remains at
   an absolute local book root unless they explicitly opt into iCloud delivery.

## Private books and public editions

An ordinary book is private. The workflow reviews the three full-size cover
pairs and thumbnails, auto-selects the strongest complete pair on its rubric,
and reports the choice. It uses `cover.png` at 1600×2560 for the EPUB portrait
and `m4b-cover.png` at 2400×2400 for the M4B square. The user does not operate a
public receipt or publishing workflow.

Public promotion is a separate, explicitly authorized action. Follow
[`publishing-a-public-edition.md`](../skill/references/publishing-a-public-edition.md)
for pair selection, publication permission, immutable re-narration when square
art changes, package verification, and governed public, iCloud, or site sync.
Private delivery permission is never public-publishing permission.

## The two ingredients that matter

- **A real grounding source the model can inspect.** A book taught through an
  actual codebase, product, place, document, or body of primary sources can be
  accurate and concrete. One written from thin air will be generic and prone to
  drift.
- **An honest length.** About 45,000 words is roughly four hours at 1.25x
  playback. Pick the listen you actually want rather than padding to a round
  number.

## Authorship and limits

By default the EPUB author is the human curator and the model that wrote the
book is recorded as a contributor. See [`skill/SKILL.md`](../skill/SKILL.md)
for the current contract.

Read the [honest disclosure](../README.md#honest-disclosure) before publishing.
The method makes a book more grounded, coherent, and inspectable; it does not
make every claim infallible. Check current primary sources and obtain the
reviews appropriate to the subject.
