---
name: explainer-audiobook
description: >-
  Use when the user wants a long, narration-ready audiobook, spoken course,
  beginner guide, or listenable explainer on a technical or specialized topic,
  especially when it should be grounded in a real codebase, product, app, or
  system and delivered as a chaptered EPUB plus combined Markdown.
---

# Explainer Audiobook

Produce a book-length, *listenable* explainer that teaches a subject by touring a
real worked example — the actual app, codebase, product, or system the user
points you at — and explaining each part: what it does, how it works, why it was
chosen, and what was traded away. The output is a chaptered EPUB (importable into
any audiobook/reader app, including on-device text-to-speech narration) plus a
combined Markdown copy.

The whole thing is *heard*, so it is written for the ear: warm second-person
prose, every term defined in plain English, and **never more than one short line
of code at a time — spoken slowly, then unpacked**. That constraint shapes
everything.

## What makes this hard (and where this skill earns its keep)

Four failure modes sink a project like this, and the process below exists to
beat each one:
1. **It sounds like code read aloud — or, overcorrecting, scrubs the real names
   away.** Solved by the narration style bible (which caps code at one speakable
   line at a time and *requires* naming the real files, tools, and commands) plus
   a post-generation code-leak and vocabulary sweep.
2. **It hallucinates the worked example.** Solved by per-chapter *fact packs*
   built from the example's real docs/code, embedded in every writer's prompt.
3. **It's a slog to generate 45,000 good words.** Solved by fanning out one
   writer agent per chapter, in parallel, each writing its own file to disk.
4. **The vocabulary washes over the listener without sticking.** Solved by the
   reinforcement rules in the style bible: key terms and commands recur across
   chapters with brief re-glosses, and each chapter's close re-names what it
   introduced.

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
- **What the listener already knows** — don't stop at a level label. Ask two or
  three quick follow-up questions about their actual prior exposure: tools
  they've used, terms they already understand, where they tend to get lost
  (`AskUserQuestion` with concrete options works well — e.g. for a git book:
  "Have you used git at all? Never / I copy-paste commands / I commit but
  branching scares me"). The answers set the true starting level, which terms
  need a full definition versus a quick refresher, and which chapters to add or
  skip.
- **Target length** — default ~45,000 words (~4 hours at 1.25x). See the runtime
  table in `references/narration-style.md`.
- **Voice** — default: warm mentor, second person, spoken. (Confirm if they want
  drier/funnier/more formal.)
- **Narrator** — if the user also asks for rendered audio, default to
  `am_michael`, fall back to `am_puck`, and do not use `af_heart` as the default.
- **Title / author** — for the EPUB metadata.

A key clarification worth surfacing early: "at most one spoken line of code at a
time" is the rule, which is *not* the same as "don't read code for accuracy" —
and *not* the same as "don't name real things." Read whatever docs and source you
need to get the facts right. You never narrate blocks or unspeakable syntax, but
you *do* speak single commands and *do* name the real files, tools, and commands
out loud (in spoken-friendly form) so the listener finishes knowing the
vocabulary and could go find — and type — these things. Quietly erasing every real name into
"the settings file" is the failure to avoid — see `references/narration-style.md`.

### 2. Design the chapter outline, and get approval before generating

This is the spec. Generating 45,000 words against the wrong outline is the
expensive mistake, so present the outline and get a yes first.

Build a table of contents in *pedagogical* order (foundations first, advanced
last). Each chapter pairs **one concept** with **one real component** of the
worked example, and promises the why — and the honest tradeoff where there's a
real one (not every chapter needs one). Also pick **2-4 throughlines** — recurring
ideas that give the long listen a spine (see `references/narration-style.md` for
why these matter and an example set).

Present the outline as a short table (chapter, concept taught, grounded-in) plus
the throughlines, and ask the user to approve, reorder, or adjust. Tell them the
honest projected length and runtime.

### 3. Write the fact packs and beat sheets

For each chapter, assemble:
- a **fact pack**: concise, accurate, sourced details about the worked example —
  read its real docs/code (or, for non-software subjects, whatever authoritative
  sources the user points you at) to get these right. **Include the real names** the
  listener should come away knowing (the actual files, tools, commands, and
  components this chapter touches), each with a one-line gloss. This is the accuracy
  backbone; the writers must not invent beyond it.
- a **beat sheet**: 6-7 beats, each roughly 450-600 words, that walk the hook →
  concept → grounding → tradeoff → takeaway shape. The closing beat re-names the
  chapter's new terms and commands (the recap rule in the style bible).

The fact-pack discipline is explained in `references/narration-style.md` — read
that section before writing the packs.

Optionally, also assemble a **figure pack**: zero to three images per chapter,
saved to `<build>/chapters/images/` with speakable filenames. This is an
audiobook first — most listeners never see them — but EPUB readers show them,
and some audiobook apps surface the images you passed while listening (Echo's
pic review at the end of a drive), so figures are a free bonus wherever a
picture genuinely helps: UI patterns, hardware, the anatomy of a screen. Source
priority:

1. the worked example's own assets — screenshots, App Store images, repo art
   (best fit, no rights questions);
2. the subject's *official* documentation (e.g. Apple's HIG illustrations for a
   HIG book) — use a search engine to find the right page, then download the
   image from the official page itself, never a re-hosted copy from an image
   search (those are routinely watermarked, low-res, or wrongly licensed);
3. openly licensed sources (Wikimedia Commons and similar) for general subjects;
4. an SVG diagram you author yourself (same craft as the cover art) — often
   clearer than any found image.

Record each figure's source URL and give it a caption that stands alone. These
books are personal-library items, but still skip anything watermarked or
paywalled, and if the environment blocks image downloads, skip figures rather
than substituting junk. Each chapter's figure list (filename + caption + what it
shows) goes into that chapter's writer prompt.

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
- a code-leak grep sweep (backticks, snake_case, arrows, braces) — scrub raw
  syntax and multi-line blocks, but leave plainly-spoken filenames like
  settings.json and deliberate single-line spoken commands (git commit, swift
  build) alone;
- a cliché / over-emphasis sweep — the "tattoo this" tics, inflated-stakes density,
  and tradeoff drone this voice is prone to; flatten anything that oversells;
- a vocabulary check — the real file/tool names from each fact pack actually get
  named in the prose, not paraphrased into "the settings file";
- heading-consistency check so the TOC comes out clean;
- figure check (if figures were used) — every `![...]` line points at a file that
  exists in `chapters/images/`, has alt text and a standalone caption, and the
  surrounding prose never leans on it (`grep -rniE 'as you can see|shown below|see the (figure|image)|pictured' chapters/ch*.md` should return nothing).

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

Make the cover next. A cover makes the book look real in any library (and in
Echo), and it should look like a professional audiobook-store cover: beautiful,
thumbnail-legible, and specific to the book, with an image that **shows what the
book is about** — not the title on a plain colour. There is no text-to-image
tool, so you author the illustration as bespoke vector art per book. Follow
`references/cover-art.md`: design **2-3 distinct illustration concepts** for the
subject, choose a signature accent colour for each concept, use that colour in
the SVG art, and pass the same hex value to `make_cover.py --accent` so the final
cover sells the colour Echo/library UIs will derive from it. Include a
bright/high-key background candidate when the topic would benefit from a modern,
friendly audiobook-store look; not every professional cover should be dark. The
default layout is `bleed` (full illustration plus a scrim that carries the title):

```bash
python3 scripts/make_cover.py \
  --title "<Book Title>" \
  --subtitle "<one-line subtitle>" \
  --author "Dan Fakkeldy" \
  --label "AUDIOBOOK" \
  --art <build>/dist/cover-concept-1.svg \
  --accent "#2ee8b6" \
  --tone bright \
  --layout bleed \
  --out <build>/dist/cover-1.png
```

Then **send the candidates with `SendUserFile` and let the user pick** (or mix) —
cover taste is theirs, and each render is cheap. `make_cover.py` composes your art
into the layout and rasterizes a 1600×2560 PNG via `rsvg-convert`, then ImageMagick;
the background hue is derived from `--accent` when supplied, otherwise from the
title. Use `--tone bright` for high-key covers and `--tone dark` for cinematic
covers. `--layout hero` frames the art in a panel instead, for a quieter, more
classic option worth including as one of the candidates. A complete example
illustration ships at
`references/cover-art-example.svg`. If no rasterizer is found the script writes a
`.svg` beside the path and exits non-zero — install `librsvg`/ImageMagick or
proceed without a cover. If the user supplied their own cover image, skip all this
and pass their file as `--cover` below.

Then assemble, passing the chosen cover with `--cover`:

```bash
python3 scripts/build_book.py \
  --chapters-dir <build>/chapters \
  --out-dir <build>/dist \
  --title "<Book Title>" \
  --author "Dan Fakkeldy" \
  --contributor "<your model name, e.g. Opus 4.8>" \
  --subtitle "<one-line subtitle>" \
  --slug <Output-Filename-Base> \
  --cover <build>/dist/cover-<chosen>.png
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
  `--cover`. Standalone Markdown image lines (`![alt](images/f.png "caption")`)
  become embedded figures automatically — images resolve relative to the
  chapters dir, land inside the EPUB, and are copied beside the .md. Missing
  images are dropped with a warning, so read the build output. Run it; don't
  reimplement EPUB zipping by hand.
- `scripts/make_cover.py` — composes a bespoke per-book illustration (`--art`, an
  SVG you author for the book) into a bestseller-style cover PNG, in a `bleed`
  (default) or `hero` layout. Pass `--accent` with the art's signature colour so
  the finished cover strongly carries the library-derived accent. Use `--tone
  bright` or `--tone dark` deliberately. Render 2-3 concepts, let the user pick,
  then pass the chosen PNG to `build_book.py --cover`.
- `references/narration-style.md` — the voice & rules block to give every writer
  verbatim, the reasoning behind them, the length/runtime table, the fact-pack
  discipline, and the QC checklist. Read before writing fact packs.
- `references/cover-art.md` — how to design good per-book cover art and run the
  offer-a-few-candidates flow; ships with `cover-art-example.svg` as a starting
  point.
- `references/fanout-template.md` — the parallel chapter-writing pattern, both the
  Agent-tool default and the Workflow option, with the exact writer-prompt
  template.
