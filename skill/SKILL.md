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

Five failure modes sink a project like this, and the process below exists to
beat each one:
1. **It sounds like code read aloud — or, overcorrecting, scrubs the real names
   away.** Solved by the narration style bible (which caps code at one speakable
   line at a time and *requires* naming the real files, tools, and commands) plus
   a post-generation code-leak and vocabulary sweep.
2. **It hallucinates the worked example.** Solved by per-chapter *fact packs*
   built from the example's real docs/code, embedded in the lead author's prompt.
3. **It feels padded, repetitive, or assembled.** Solved by a single frontier
   lead author, a concept-coverage ledger, deliberately varied chapter jobs,
   and an editorial pass that treats repetition as a defect unless it has a
   named learning purpose.
4. **The vocabulary washes over the listener without sticking.** Solved by the
   reinforcement rules in the style bible: key terms and commands recur across
   chapters with brief re-glosses, and each chapter's close re-names what it
   introduced.
5. **Expensive prose work gets wasted on mechanical production.** Solved by
   routing research extraction, fact checking, diagnostics, packaging, and
   rendering to cheaper workers while the frontier author owns only the prose
   and substantive editorial decisions.

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
  backbone; the author must not invent beyond it.
- a **beat sheet**: a short sequence of distinct jobs, such as a scene,
  mechanism, worked example, failure mode, comparison, or application. Do not
  force every chapter into the same 6-7-beat shape or a uniform word target;
  a short orienting chapter and a dense technical chapter should earn different
  lengths.
- a **concept-coverage ledger** in `research/coverage-ledger.md`: for every
  core concept, record its first introduction, planned later use, why any
  repetition helps (retrieve, deepen, apply, compare, or correct a
  misconception), its real example, and the listener's expected new ability.
  Every chapter needs a clear *knowledge delta* — what the listener can explain
  or do afterward that they could not before. This is the anti-padding spec.

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
shows) goes into that chapter's frontier-author prompt.

### 4. Use a frontier lead author; keep Markdown canonical

Pre-create a build directory with a `chapters/` subfolder. One frontier model
owns every chapter's narration and all substantive revisions. It may write the
book sequentially, chapter by chapter, to `chNN.md` when the whole manuscript
will not fit in one context, but do **not** fan out prose drafting to cheaper
models or independent chapter writers.

Give the frontier author the approved TOC, throughlines, voice bible,
concept-coverage ledger, the relevant fact pack and beat sheet, plus a compact
continuity record after each chapter. Store that record in
`research/continuity.md`: newly introduced terms, analogies already used,
examples, deliberate callbacks, unresolved promises, and facts that must remain
consistent. The chapter files are the canonical manuscript; EPUB, audio, and all
other formats are downstream renderings.

Cheaper workers may extract sources, build fact packs, check citations, run
diagnostics, simulate a beginner listener, assemble files, make covers, render
audio, and produce short editorial reports with exact quotations and locations.
They do **not** write or replace whole chapters. A bounded mechanical edit is
acceptable only when it cannot change meaning; return depth, structure,
explanation, and factual corrections to the frontier author. Follow
`references/frontier-manuscript-pipeline.md` for the role contract and review
format.

### 5. QC sweep and targeted editorial repair

Run the checklist in `references/narration-style.md`:
- real word counts with `wc -w` (investigate a chapter outside its ledger range;
  never trust a model's self-reported count or pad automatically);
- a code-leak grep sweep (backticks, snake_case, arrows, braces) — scrub raw
  syntax and multi-line blocks, but leave plainly-spoken filenames like
  settings.json and deliberate single-line spoken commands (git commit, swift
  build) alone;
- a cliché / over-emphasis sweep — the "tattoo this" tics, inflated-stakes density,
  and tradeoff drone this voice is prone to; flatten anything that oversells;
- a vocabulary check — the real file/tool names from each fact pack actually get
  named in the prose, not paraphrased into "the settings file";
- `python3 scripts/prose_qc.py --chapters-dir <build>/chapters` to surface
  repeated phrases, similar paragraphs, and formulaic openings/closings. Treat
  it as a candidate list, not a blind rewrite instruction: intentional
  vocabulary retrieval is allowed only when the coverage ledger explains it;
- a cheap-reader report that cites the exact paragraph for: redundant idea,
  unexplained leap, weak or missing mechanism, jargon without an example,
  generic phrasing, and a place that needs a counterexample, boundary, or
  concrete walkthrough. It should recommend the *type* of repair, not rewrite
  the manuscript in a different voice;
- heading-consistency check so the TOC comes out clean;
- figure check (if figures were used) — every `![...]` line points at a file that
  exists in `chapters/images/`, has alt text and a standalone caption, and the
  surrounding prose never leans on it (`grep -rniE 'as you can see|shown below|see the (figure|image)|pictured' chapters/ch*.md` should return nothing).

Spot-read the tone-setting first chapter and the most technical chapter to
confirm voice and that nothing was hallucinated. Have the frontier author make
one targeted editorial pass over accepted findings; do not pay for a wholesale
second draft if the report only finds local polish.

Then load the `humanizer` skill and follow `references/humanizer-pass.md` for a
light, bounded humanizing pass over the canonical Markdown. Remove AI tics,
generic signposting, inflated claims, and repetitive rhythm, while preserving
facts, citations, technical names, teaching structure, intentional retrieval,
and the frontier author's voice. The humanizer must not invent anecdotes,
opinions, first-person experience, sources, jokes, or new claims, and must not
rewrite the book wholesale. The frontier author reviews and accepts every
non-mechanical change before EPUB/audio packaging; rerun factual, ledger, and
narration checks afterward.

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
Echo), and it must look like a professional audiobook-store cover: specific,
thumbnail-legible, and built around an image with an editorial point of view —
not title text on a plain colour. Follow `references/cover-art.md` and make
**exactly three award-worthy, complete art-and-type candidates by default.** The
three candidates must differ in metaphor, composition, palette, material
language, and title strategy. Font, line breaks, scale, placement, and effects
are part of the candidate—not a shared footer applied afterward. Use the
reference's style menu and genre calibration to choose three appropriate
directions, write a complete art-and-type brief for each, and reject generic
genre clichés before rendering.

Use the strongest available image-generation tool directly for the art (for
example, `image_generate`), rather than asking a cheaper text model to draw a
generic SVG of icons, cards, arrows, or diagrams. Follow the copy-ready prompt in
`references/cover-art.md`: give the model one specific visual thesis, one large
central metaphor, an art-directed composition for that candidate's intended
title relationship, and an eye-catching two-to-four-colour palette with a vivid
signature accent. Keep generated art text-free: no lettering, logos, watermarks,
mockup frame, interface, infographic, stock-template look, or close imitation of
a named existing cover or designer. Reject weak outputs and regenerate; do not
ship the first technically valid image. Include at least one high-key/bright
candidate unless the subject genuinely demands three dark directions.

Save each art file beside a validated `cover-spec-N.json`. New books render the
whole composition from the specification:

```bash
SLUG="<Output-Filename-Base>"
RUN_ROOT=".build/custom-learning-audiobooks/$SLUG"
/usr/local/bin/python3 skill/scripts/make_cover.py \
  --spec "$RUN_ROOT/dist/cover-spec-1.json" \
  --out "$RUN_ROOT/dist/cover-1.png"
```

Repeat for candidates 2 and 3. Review every full-size render and generated
160-pixel thumbnail with its brief, font/palette note, and warnings. Send all
three complete candidates to the user and ask them to choose or request a mix;
a mix becomes a new specification and render. The renderer never selects a
candidate automatically.

Only after the human choice, create `cover-selection.json` with
`cover_receipts.py select`, using `selection_source=explicit-user-choice` (or
`requested-mix`) plus the approved edition and privacy metadata. Assign all
values from the approved run metadata, then select and build in that order:

```bash
SELECTED=1
SLUG="<Output-Filename-Base>"
TITLE="<Book Title>"
SUBTITLE="<one-line subtitle>"
CONTRIBUTOR="<your model name, e.g. Opus 4.8>"
EDITION_ID="<edition identifier>"
SELECTED_AT="<ISO-8601 timestamp with UTC offset>"
CLASSIFICATION="<private|public-safe|sensitive>"
PERMISSION_TO_PUBLISH="<denied|granted|not-requested>"
RUN_ROOT=".build/custom-learning-audiobooks/$SLUG"
DIST="$RUN_ROOT/dist"

/usr/local/bin/python3 skill/scripts/cover_receipts.py select \
  --render-receipt "$DIST/cover-$SELECTED.render.json" \
  --out "$DIST/cover-selection.json" \
  --book-slug "$SLUG" \
  --edition-id "$EDITION_ID" \
  --selection-source explicit-user-choice \
  --selected-at "$SELECTED_AT" \
  --classification "$CLASSIFICATION" \
  --permission-to-publish "$PERMISSION_TO_PUBLISH"

/usr/local/bin/python3 skill/scripts/build_book.py \
  --chapters-dir "$RUN_ROOT/chapters" \
  --out-dir "$DIST" \
  --title "$TITLE" \
  --author "Dan Fakkeldy" \
  --contributor "$CONTRIBUTOR" \
  --subtitle "$SUBTITLE" \
  --slug "$SLUG" \
  --cover "$DIST/cover-$SELECTED.png" \
  --cover-selection "$DIST/cover-selection.json"
```

It writes a valid EPUB 3 (with both a nav and an NCX table of contents, and the
cover embedded as both the library thumbnail and a full-bleed first page) plus a
combined Markdown file, and prints per-chapter word counts and an estimated
runtime. The EPUB author (`dc:creator`) is the human; the generating model is
recorded as a `dc:contributor`. `--cover` and `--contributor` are optional.
Verify the EPUB is valid (the `mimetype` check in `references/narration-style.md`).

### 7. Native Echo/Kokoro M4B and alignment

For a complete governed package, render native Echo/Kokoro audio only after the
governed EPUB exists. Follow the Echo build and CLI-discovery procedure in
`skills/custom-learning-audiobook/references/package-and-qc.md`, set `CLI` to the
built `echo-cli`, and keep the same work directory/database across resumes:

```bash
CLI="<path to the built echo-cli>"
WORK="$RUN_ROOT/audio-work"
DB="$RUN_ROOT/narration.sqlite"

"$CLI" narrate \
  --epub "$DIST/$SLUG.epub" \
  --out "$DIST/$SLUG.m4b" \
  --sidecar "$DIST/$SLUG.alignment.json" \
  --voice am_michael \
  --title "$TITLE" \
  --author "Dan Fakkeldy" \
  --work-dir "$WORK" \
  --db "$DB"
```

If `am_michael` is unavailable, retry with the Echo voice `am_puck` and record
the fallback. Do not impose a timeout on a progressing render, and do not silently
replace Echo/Kokoro with Apple/macOS/system narration. Resume a partial render
with the same command plus `--resume`.

After Echo writes the M4B and alignment sidecar, run the final receipt check
across the selected cover, governed EPUB, and M4B:

```bash
/usr/local/bin/python3 skill/scripts/cover_receipts.py verify \
  --selection "$DIST/cover-selection.json" \
  --cover "$DIST/cover-$SELECTED.png" \
  --epub "$DIST/$SLUG.epub" \
  --m4b "$DIST/$SLUG.m4b" \
  --receipt "$DIST/cover-selection.json"
```

If native Echo audio is blocked, the EPUB and Markdown may be surfaced directly
from `dist/` as clearly labelled **interim** files. They are not a complete
governed package, and the workflow does not proceed to package sync until native
Echo audio and the final M4B receipt verification succeed.

### 8. Governed delivery

Set `DELIVERY_DIR` to the approved delivery folder. Run the sync as a dry run
first; it reports `new`, `reuse`, `supersede`, or a conflict without writing:

```bash
DELIVERY_DIR="<approved delivery folder>"
/usr/local/bin/python3 skill/scripts/sync_selected_cover.py \
  --selection "$DIST/cover-selection.json" \
  --cover "$DIST/cover-$SELECTED.png" \
  --epub "$DIST/$SLUG.epub" \
  --m4b "$DIST/$SLUG.m4b" \
  --destination "$DELIVERY_DIR" \
  --intent reuse
```

Use `--intent supersede` only for a newer explicit choice. A cover-bearing
destination without a receipt is an `unreceipted` conflict unless the operation
is an explicit supersession. Only after the reported classification is expected,
rerun the same sync with explicit apply (and the same chosen intent):

```bash
/usr/local/bin/python3 skill/scripts/sync_selected_cover.py \
  --selection "$DIST/cover-selection.json" \
  --cover "$DIST/cover-$SELECTED.png" \
  --epub "$DIST/$SLUG.epub" \
  --m4b "$DIST/$SLUG.m4b" \
  --destination "$DELIVERY_DIR" \
  --intent reuse \
  --apply
```

After governed apply, copy only non-governed Markdown, alignment, manifest, and
image files as needed; never raw-copy the selected cover, EPUB, M4B, or selection
receipt around classification. Surface the delivered EPUB/Markdown in chat and
report the real total word count, runtime, narrator, receipt verification, and
destination classification. If it ran long, offer to trim by tightening prose
across all chapters (preserving the arc) rather than cutting chapters. Offer to
regenerate any single chapter, adjust the voice or cover, or change length.

If the user produced this from a real codebase that has living docs, consider
whether anything is worth noting — but this skill creates a *deliverable*, not a
code change, so it normally needs no repo-doc updates.

## Bundled resources

- `scripts/build_book.py` — assembles `chNN.md` chapter files into an EPUB +
  combined Markdown. Title/author/subtitle/slug are arguments, plus an optional
  `--cover`. New builds also pass `--cover-selection` so the selected cover is
  verified while the EPUB is assembled. Standalone Markdown image lines
  (`![alt](images/f.png "caption")`) become embedded figures automatically —
  images resolve relative to the chapters dir, land inside the EPUB, and are
  copied beside the .md. Missing images are dropped with a warning, so read the
  build output. Run it; don't reimplement EPUB zipping by hand.
- `scripts/make_cover.py` — validates a candidate specification, renders its
  complete art-and-type composition with bundled fonts, and writes a full-size
  cover, thumbnail, and render receipt. New books use `--spec`; the old title,
  art, accent, tone, and layout flags are compatibility-only for existing calls.
- `scripts/cover_receipts.py` — creates an explicit human selection receipt and
  verifies that receipt through the selected cover and packaged artifacts.
- `scripts/sync_selected_cover.py` — classifies a delivery destination in a dry
  run and applies the selected cover-bearing artifacts only after explicit
  approval.
- `references/narration-style.md` — the voice & rules block to give the frontier
  author verbatim, the reasoning behind them, the length/runtime table, the
  fact-pack discipline, and the QC checklist. Read before writing fact packs.
- `references/cover-art.md` — how to design, render, review, and explicitly
  select three complete art-and-type candidates; ships with
  `cover-art-example.svg` as a structural reference for an approved vector
  fallback.
- `references/frontier-manuscript-pipeline.md` — the frontier-author / cheaper-worker
  split, continuity protocol, and citation-first cheap-review format.
- `references/humanizer-pass.md` — the bounded `humanizer` pass for removing
  AI-writing tells without replacing the frontier author's voice or meaning.
