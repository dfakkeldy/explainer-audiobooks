---
name: audiobook
description: "Create and deliver a researched nonfiction audiobook from a topic, source material, or repository."
---

# Audiobook

Write the best book you can. The angle, structure, chapter count, voice,
examples, length, and revision method are yours to choose. The references named
below record what has worked for this listener; use what helps and skip what
does not. No humanizer pass, AI-tell sweep, or prose-style gate is required.

## The finish line

The book is done only when this package is in
`~/Library/Mobile Documents/com~apple~CloudDocs/Books/<Book Title>/`:

- `<Book Title>.epub` with the portrait cover embedded and verified Echo
  pronunciation annotations authored into it;
- `<Book Title>.m4b`, the complete Echo narration with the square cover
  embedded;
- `<Book Title>.alignment.json`, the Echo sidecar bound to that EPUB and audio
  and checked with the installed renderer's `verify-sidecar`;
- `cover.png` (portrait) and `m4b-cover.png` (square);
- `source/` holding the canonical manuscript.

`../skills/echo-narration/references/complete-delivery.md` owns this contract:
the evidence to collect, and what to report when something blocks it. A local
build, a preview clip, or an EPUB alone is not a finished book.

## Interpreter

Run every script with `/usr/local/bin/python3`. The default `python3` lacks
Pillow and cannot import `build_book.py`.

## Intake

### Ordinary request

For a direct book request, use the host's available batched input mechanism
once for exactly these five questions:

1. What is the book about, and what should the listener be able to do after it?
2. Who is it for?
3. What do they already know about the subject?
4. Roughly how long?
5. Should it be built around a specific real thing — a repo, product, place, or
   document?

### Complete longform handoff

When `$longform-book-development` supplies a complete handoff packet,
skip the five-question intake. A handoff is complete enough when it settles the
audience, outcome, length, privacy and listening context; governing question,
narrative spine, chapter and section intentions; source locators and story
material; voice direction; figure and semantic voice plan; narration risks;
author, contributor, and delivery boundary. An incomplete packet follows the
ordinary-request route.

After either route, state the plan in one line — title, angle, chapter count,
estimated runtime — and start with no approval pause.

Apply silent defaults and write them to `source/brief.md`:

| Choice | Default |
|---|---|
| Listening | `road-book`, for driving and delivering mail |
| Semantic cast | guide am_michael; memory plus optional field/coach; never af_heart |
| Guide fallback | `am_puck` only when the guide voice is unavailable; record it; never `af_heart` |
| Credits | author `Dan Fakkeldy`; model name in `--contributor` |
| Privacy | private |
| Cover | strongest of three rendered pairs, selected on the rubric |
| Delivery | Dan-specific standing private iCloud authorization; otherwise local |

Use `.build/custom-learning-audiobooks/<slug>/` as the internal run root, with
`research/`, `chapters/`, and `dist/` scratch directories. Define absolute `BOOK_ROOT`
before writing durable work. Its source of truth is
`$BOOK_ROOT/source/brief.md`, `$BOOK_ROOT/source/outline.md`,
`$BOOK_ROOT/source/research.md`, `$BOOK_ROOT/source/chapters/`, and
`$BOOK_ROOT/source/feedback.md`; the run root remains disposable scratch.

## The listener

The default listener is driving and delivering mail: no screen, no rewinding,
attention shared with the road. That shapes the writing more than any rule.

- Write for the ear. Name the real files, tools, commands, places, and
  documents with a one-breath gloss instead of vague paraphrase, and speak at
  most one short line of code at a time before unpacking it.
- Attention drifts, so open each section so a drifted listener can join it
  cold, re-naming the running subject instead of leaning on the last close.
- Practical situation-choice-consequence examples ground abstract ideas.
  Analogies work best as short retrieval handles.
- A spoken `Key points` checkpoint of two to four recall or action points, with
  no new facts, has worked well at natural learning boundaries.

Optional craft notes: `references/road-book-mode.md`,
`references/narration-style.md`, `references/voice-design.md`,
`references/learning-design.md`, `references/curriculum-patterns.md`, and
`references/frontier-manuscript-pipeline.md`.

## Research

Work from real sources with precise locators, and keep the notes in
`source/research.md`. Name the actual files, tools, commands, places, and
documents the listener should come away knowing. Real stories — named actors,
a place, a date, and a turn nobody expected — teach better than hypotheticals;
gather them into a story ledger while researching.

Accuracy is the one writing rule that does not bend: the manuscript may only
assert what the research supports, and a citation-shaped memory is not
evidence.

## Write and revise

One frontier author writes every canonical chapter and makes every substantive
repair, so the book keeps one voice. Cheaper workers may research, check,
assemble, and render; they never write or replace chapters.

Draft and revise however serves the book. Before packaging, check every factual
claim against the research, and read the manuscript as a newcomer hearing it
once. A fresh-context reader working in listening order, without the outline,
is a good way to find where a listener would get lost.

## Produce and deliver

Follow `../skills/echo-narration/references/epub-pronunciation.md` before packaging:
review every content, record, and read occurrence in context and embed verified
IPA through Echo's supported contract before freezing the EPUB. Keep pending
renderer support and actual listening acceptance explicit.

Design exactly three coordinated cover pairs with
`references/cover-art.md`. At least two of the three complete pairs must be intentionally high-key, and one of those high-key pairs must be a Designed flat graphic. The third candidate is tonally unrestricted and may be dark when its subject and central metaphor earn that treatment. Render each with
`render_cover_pair(...)`: `cover.png` at 1600×2560 for the EPUB portrait and
`m4b-cover.png` at 2400×2400 for the M4B square.

Review full-size art and thumbnails and auto-select the best pair on subject specificity,
thumbnail legibility, title hierarchy, portrait/square coherence, absence of defects,
and distinctiveness. High-key treatment breaks a close tie; a clearly stronger darker
pair may win when the reported choice explains why. Report the choice rather than asking.

Run `skill/scripts/build_book.py` with the chapters, chosen covers, title,
author `Dan Fakkeldy`, and model in `--contributor`. Plan the semantic roles,
candidate Echo voices, listener exclusions, and frozen EPUB boundary with
`references/semantic-voice-casting.md`. Resolve the absolute
`NARRATION_SCRIPT` from this installed skill or its repository, then follow
`skills/echo-narration/references/narrating.md` for the mandatory invocation
and accepted-artifact verification contract. Freeze, inventory, validate the
semantic cast, and pass its argv0 vector to that reference; never derive the
pipeline root from the subject repository.

The request authorizes Dan's private iCloud delivery. Record it in
`$BOOK_ROOT/source/brief.md` and set `BOOK_ROOT` to the expanded
`~/Library/Mobile Documents/com~apple~CloudDocs/Books/<Book Title>/`.
Verify the complete delivered package before claiming completion; follow the
required-delivery reference for blockers and evidence. This authorization is
Dan-specific: for any other user or context, deliver locally unless that user
explicitly opts in to iCloud delivery.

## What a book is

```text
Books/<Book Title>/
  <Book Title>.epub
  <Book Title>.m4b
  <Book Title>.alignment.json
  m4b-cover.png
  cover.png
  source/
    brief.md          intake answers and every default applied
    outline.md
    research.md       evidence notes and story ledger
    chapters/chNN.md  canonical manuscript
    feedback.md       dated log: what was said, what changed
  previous/           one prior version, overwritten each redo
```

## The redo loop

1. Locate the book folder by name, tolerating partial and informal titles.
2. Read `source/brief.md`, `source/outline.md`, and the manuscript.
3. Write down what is working and must not change before touching anything:
   the governing question, narrative spine, examples that landed, and chapter
   jobs that worked.
4. Make the targeted revision. Rewrite the whole book only when asked.
5. Re-check facts and flow in the changed material and anything downstream.
6. Rebuild the EPUB with pronunciation reviewed for changed text, re-narrate
   the M4B, and re-render the cover only when the cover was the complaint.
7. Move the current version to `previous/`, overwriting it, then write the new
   version in place under the same name.
8. Append to `source/feedback.md`: date, what was said, and what changed.

When the same feedback appears across roughly three books, treat it as a
standing preference and offer to write it to memory for the next brief.
