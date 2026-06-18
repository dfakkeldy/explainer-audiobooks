---
name: explainer-audiobook
description: >-
  Generate a long, narration-ready beginner's audiobook that teaches a technical
  or specialized subject through one concrete worked example, delivered as a
  chaptered EPUB plus a combined Markdown file, written entirely for the ear (no
  code or symbols read aloud). Use this whenever the user wants an audiobook,
  narrated guide, spoken course, listening course, or "beginner's guide" on a
  topic they intend to LISTEN to — for example "make me a 45k-word audiobook
  about GitHub", "a narrated guide to App Store Optimization", "turn the way our
  app works into a spoken beginner's course", "an audiobook explaining how X
  works, taught through our codebase", or "write me ~4 hours of audio teaching
  Xcode debugging". Especially reach for this skill when the request should be
  taught through a real example app, codebase, product, or system AND run to a
  target length (tens of thousands of words / multiple hours of listening). It
  also covers planning the chapter outline, writing the narration-friendly prose,
  and assembling the final EPUB. Prefer this skill even when the user says
  "guide" or "course" rather than literally "audiobook", as long as they mean to
  listen to it.
---

# Explainer Audiobook

Produce a book-length, *listenable* explainer that teaches a subject by touring a
real worked example — the actual app, codebase, product, or system the user
points you at — and explaining each part: what it does, how it works, why it was
chosen, and what was traded away. The output is a chaptered EPUB (importable into
any audiobook/reader app, including on-device text-to-speech narration) plus a
combined Markdown copy.

The whole thing is *heard*, so it is written for the ear: warm second-person
prose, every term defined in plain English, and **not one line of code or symbol
read aloud**. That single constraint shapes everything.

## What makes this hard (and where this skill earns its keep)

Three failure modes sink a project like this, and the process below exists to
beat each one:
1. **It sounds like code read aloud.** Solved by the narration style bible and a
   post-generation code-leak sweep.
2. **It hallucinates the worked example.** Solved by per-chapter *fact packs*
   built from the example's real docs/code, embedded in every writer's prompt.
3. **It's a slog to generate 45,000 good words.** Solved by fanning out one
   writer agent per chapter, in parallel, each writing its own file to disk.

## Process

Work through these steps in order. Use a TodoWrite list to track them.

### 1. Pin down the brief

Confirm these before writing anything. If the user hasn't specified them, ask
(an `AskUserQuestion` with a few options works well) — but offer sensible
defaults so it stays a quick yes/no, not an interrogation:

- **Subject** — what the book teaches (e.g. "iOS development", "GitHub & version
  control", "App Store Optimization").
- **Worked example** — the real thing every explanation is grounded in (e.g.
  "our app Echo", "this repo", "a generic example project"). This is what keeps
  it concrete and accurate. If there's a real codebase/product, you will read its
  docs/code for the fact packs.
- **Audience level** — default: a curious near-beginner who can muddle through
  with AI help but wants the *why*. Other options: total newcomer, or someone
  experienced in an adjacent area.
- **Target length** — default ~45,000 words (~4 hours at 1.25x). See the runtime
  table in `references/narration-style.md`.
- **Voice** — default: warm mentor, second person, spoken. (Confirm if they want
  drier/funnier/more formal.)
- **Title / author** — for the EPUB metadata.

A key clarification worth surfacing early: "don't read code aloud" is the rule,
which is *not* the same as "don't read code for accuracy." You should read
whatever docs and source you need to get the facts right; you just never narrate
syntax.

### 2. Design the chapter outline, and get approval before generating

This is the spec. Generating 45,000 words against the wrong outline is the
expensive mistake, so present the outline and get a yes first.

Build a table of contents in *pedagogical* order (foundations first, advanced
last). Each chapter pairs **one concept** with **one real component** of the
worked example, and promises the why + the tradeoff. Also pick **2-4
throughlines** — recurring ideas that give the long listen a spine (see
`references/narration-style.md` for why these matter and an example set).

Present the outline as a short table (chapter, concept taught, grounded-in) plus
the throughlines, and ask the user to approve, reorder, or adjust. Tell them the
honest projected length and runtime.

### 3. Write the fact packs and beat sheets

For each chapter, assemble:
- a **fact pack**: concise, accurate, sourced details about the worked example —
  read its real docs/code to get these right. This is the accuracy backbone; the
  writers must not invent beyond it.
- a **beat sheet**: 6-7 beats, each roughly 450-600 words, that walk the hook →
  concept → grounding → tradeoff → takeaway shape.

The fact-pack discipline is explained in `references/narration-style.md` — read
that section before writing the packs.

### 4. Fan out: one writer agent per chapter, in parallel

Pre-create a build directory with a `chapters/` subfolder. Then dispatch the
writers concurrently — each gets the style bible + throughlines + full TOC + its
own beats + its own fact pack, and each writes its own `chNN.md` file to disk
(large prose belongs on disk, not round-tripped through your context).

Follow `references/fanout-template.md`. It gives two ways to run the fan-out:
- **Default (anywhere):** parallel `Agent` tool calls, in batches.
- **When the user has opted into multi-agent orchestration** (e.g. an
  "ultracode" session, or they asked for a workflow): the `Workflow` script in
  that file gives nicer progress and concurrency control. Only use the Workflow
  tool under that opt-in.

### 5. QC sweep (cheap shell checks, before assembling)

Run the checklist in `references/narration-style.md`:
- real word counts with `wc -w` (top up any chapter under its floor — never trust
  self-reported counts);
- a code-leak grep sweep (backticks, snake_case, arrows, braces, spoken file
  extensions) — scrub anything that would sound wrong narrated;
- heading-consistency check so the TOC comes out clean.

Spot-read the tone-setting first chapter and the most technical chapter to
confirm voice and that nothing was hallucinated.

### 6. Make a cover, then assemble the EPUB + Markdown

**Authorship — the author is the human owner: "Dan Fakkeldy".** Set the
author to the human owner of the book (for this user, **Dan Fakkeldy**). The
EPUB author (`dc:creator`) and the cover by-line both use the human name, because
the user's book-ingestion workflow keys on a stable human author — a model name
in the author field breaks it. Still record which model wrote the book, but put
it in the *contributor* field (`--contributor`), a separate metadata slot
ingestion scripts ignore: pass your own model's human-friendly name there (the
model running this skill right now, e.g. "Opus 4.8", "Sonnet 4.6", "Fable 5" —
not the raw model id, not a guess). So: author = the human everywhere; model =
contributor in metadata only.

First generate a cover image. A cover makes the book look real in any library
(and in Echo), so always make one unless the user supplies their own:

```bash
python3 scripts/make_cover.py \
  --title "<Book Title>" \
  --subtitle "<one-line subtitle>" \
  --author "Dan Fakkeldy" \
  --label "AUDIOBOOK" \
  --out <build>/dist/cover.png
```

`make_cover.py` builds a clean typographic cover as an SVG (no image library
needed) and rasterizes it to a 1600×2560 PNG using whatever is installed
(`rsvg-convert`, then ImageMagick). The background hue is derived from the title,
so every book gets its own color. If no rasterizer is found it writes a `.svg`
beside the path and exits non-zero — in that case either install `librsvg`
(`rsvg-convert`) or ImageMagick, or proceed without a cover. If the user gave you
their own cover image, skip this and pass their file as `--cover` below.

Then assemble, passing the cover with `--cover`:

```bash
python3 scripts/build_book.py \
  --chapters-dir <build>/chapters \
  --out-dir <build>/dist \
  --title "<Book Title>" \
  --author "Dan Fakkeldy" \
  --contributor "<your model name, e.g. Opus 4.8>" \
  --subtitle "<one-line subtitle>" \
  --slug <Output-Filename-Base> \
  --cover <build>/dist/cover.png
```

It writes a valid EPUB 3 (with both a nav and an NCX table of contents, and the
cover embedded as both the library thumbnail and a full-bleed first page) plus a
combined Markdown file, and prints per-chapter word counts and an estimated
runtime. The EPUB author (`dc:creator`) is the human; the generating model is
recorded as a `dc:contributor`. `--cover` and `--contributor` are optional.
Verify the EPUB is valid (the `mimetype` check in `references/narration-style.md`).

### 7. Deliver

Always save the finished `.epub` to the user's book inbox so it's where they
expect it, then surface it in chat:

```bash
mkdir -p ~/Downloads/book-inbox
cp <build>/dist/<Output-Filename-Base>.epub ~/Downloads/book-inbox/
```

Then send the `.epub` (and the `.md`, which is handy for reading/editing) with
`SendUserFile`. Report the real total word count and the honest runtime estimate.
If it ran long, offer to trim by tightening prose across all chapters (preserving
the arc) rather than cutting chapters. Offer to regenerate any single chapter,
adjust the voice or cover, or change length.

If the user produced this from a real codebase that has living docs, consider
whether anything is worth noting — but this skill creates a *deliverable*, not a
code change, so it normally needs no repo-doc updates.

## Bundled resources

- `scripts/build_book.py` — assembles `chNN.md` chapter files into an EPUB +
  combined Markdown. Title/author/subtitle/slug are arguments, plus an optional
  `--cover`. Run it; don't reimplement EPUB zipping by hand.
- `scripts/make_cover.py` — generates a clean typographic cover PNG (title,
  subtitle, author, hue derived from the title) via SVG + a rasterizer. Run it
  before `build_book.py`; pass the result with `--cover`.
- `references/narration-style.md` — the voice & rules block to give every writer
  verbatim, the reasoning behind them, the length/runtime table, the fact-pack
  discipline, and the QC checklist. Read before writing fact packs.
- `references/fanout-template.md` — the parallel chapter-writing pattern, both the
  Agent-tool default and the Workflow option, with the exact writer-prompt
  template.
