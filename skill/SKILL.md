---
name: audiobook
description: >-
  Use when the user says "make me a book about X", "I want to learn X",
  "turn this repo into an audiobook", or "a book I can listen to while
  driving". Research, write, revise, package, narrate, and deliver one grounded
  nonfiction audiobook, whether the subject is a technical system, a practical
  skill, a place, or an idea.
---

# Audiobook

Make the useful book, then make it easy to hear and easy to revise.

## Interpreter

Run every script with `/usr/local/bin/python3`. The default `python3` lacks
Pillow and cannot import `build_book.py`.

## Intake

### Ordinary request

For a direct book request, use one `AskUserQuestion` batch:

1. What is the book about, and what should the listener be able to do after it?
2. Who is it for?
3. What do they already know about the subject?
4. Roughly how long?
5. Should it be built around a specific real thing — a repo, product, place, or
   document?

### Complete longform handoff

When `$longform-book-development` supplies a complete handoff packet, skip the five-question intake.
A handoff is complete enough when it settles the audience,
outcome, length, privacy and listening context; governing question, narrative
spine, chapter and section jobs; source locators and story material; voice and
figure plan; five craft passes and blind beginner review; narration risks,
author, contributor, and delivery boundary. An incomplete packet follows the
ordinary-request route.

After either route, state the plan in one line — title, angle, chapter count,
estimated runtime — and start with no approval pause.

Apply silent defaults and write them to `source/brief.md`:

| Choice | Default |
|---|---|
| Listening | `road-book`, for driving and delivering mail |
| Narrator | `am_michael`, then `am_puck`; never `af_heart` |
| Credits | author `Dan Fakkeldy`; model name in `--contributor` |
| Voice | warm, second-person, spoken |
| Privacy | private |
| Cover | strongest of three rendered pairs, selected on the rubric |

Use `.build/custom-learning-audiobooks/<slug>/` as the internal run root, with
`research/`, `chapters/`, and `dist/` scratch directories. The book's delivered
`source/` folder is its durable source of truth.

## Research

Write plain Markdown evidence notes with real sources, precise locators,
contradictions, and uncertainty. Add a story ledger: each story has named
actors, place, date, source, concept carried, and a reversal. Without a reversal
it is an illustration, not a story.

Build a fact pack for every chapter from the real source material. Name the
actual files, tools, commands, places, and documents the listener should know,
each with a one-breath gloss. The manuscript may only assert what the research
supports; a citation-shaped memory is not evidence. Keep the research in
`source/research.md`.

## Outline

Write an argument-level, question-led progression to `source/outline.md`: six
to ten durable outcomes where appropriate, one governing question, a narrative
spine, varied chapter jobs, and two to four throughlines. A terminology syllabus
is not an outline. State the one-line plan and continue; there is no approval
pause.

Choose the learning shape with `references/curriculum-patterns.md`. Protect the
driving context with `references/road-book-mode.md`, and use the chapter
teaching plan and blind review in `references/learning-design.md`.

## Draft

One frontier author owns every canonical section and every substantive repair.
Draft in order. Each call receives the full outline, relevant fact pack,
previous section text or a faithful summary, current section job, and its
must-not-repeat list. Maintain a short continuity note of defined terms,
examples, callbacks, and open promises.

Cheaper workers may extract, verify, assemble, render, and report with citations.
They never write or replace chapters. Follow
`references/frontier-manuscript-pipeline.md`.

Write for the ear using `references/narration-style.md` and
`references/voice-design.md`: define every term in plain English, name the real
files, tools, and commands instead of erasing them into "the settings file",
and speak at most one short line of code at a time before unpacking it.

## Revise

Run one job per pass, in this order:

1. `claim-traceability`
2. `tightening`
3. `de-listification`
4. `sentence-rhythm`
5. `ear-pass` against rendered audio

The passes happen; no ledger records them. Next run the blind beginner review:
the reviewer reads in listening order without the outline, rationale, or
expected outcomes, then reports the mental model formed and the exact point
where the listener gets lost. The frontier author resolves accepted findings.

Run `skill/scripts/prose_qc.py --fail-on-style`, apply the bounded `humanizer`
skill using `references/humanizer-pass.md`, then run
`skill/scripts/prose_qc.py --fail-on-style` again. Use
`references/declaudification.md` for the listener's AI-writing patterns to avoid
and the family-density limits. The humanizer must not invent anecdotes, facts,
sources, opinions, first-person experience, jokes, or a replacement voice.

## Produce and deliver

Design exactly three coordinated cover pairs with
`references/cover-art.md`. Render each with `render_cover_pair(...)`:
`cover.png` at 1600×2560 for the EPUB portrait and `m4b-cover.png` at
2400×2400 for the M4B square. Review full-size art and thumbnails, auto-select
the best pair on subject specificity, thumbnail legibility, title hierarchy,
portrait/square coherence, absence of defects, and distinctiveness, then report
the choice rather than asking.

Run `skill/scripts/build_book.py` with the chapters, chosen covers, title,
author `Dan Fakkeldy`, and model in `--contributor`. Narrate with
`skills/echo-narration/scripts/echo_pronunciation_narrate.sh`.

Keep the private result in its run root unless the user explicitly requests a
private iCloud reading copy. On that request, copy the finished folder to
`~/Library/Mobile Documents/com~apple~CloudDocs/Books/<Book Title>/`, whose
expanded path contains `com~apple~CloudDocs/Books`.

## What a book is

```text
Books/<Book Title>/
  <Book Title>.epub
  <Book Title>.m4b
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
5. Re-run the craft passes over changed material and anything downstream.
6. Rebuild the EPUB, re-narrate the M4B, and re-render the cover only when the
   cover was the complaint.
7. Move the current version to `previous/`, overwriting it, then write the new
   version in place under the same name.
8. Append to `source/feedback.md`: date, what was said, and what changed.

When the same feedback appears across roughly three books, treat it as a
standing preference and offer to write it to memory for the next brief.
