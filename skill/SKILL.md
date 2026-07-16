---
name: explainer-audiobook
description: >-
  Use when the user wants a long, narration-ready audiobook, spoken course,
  beginner guide, or listenable explainer on a technical or specialized topic —
  "turn this repo/app into an audiobook", "a book I can listen to while
  driving", "explain X as a spoken course" — especially when it should be
  grounded in a real codebase, product, app, or system and delivered as a
  chaptered EPUB plus combined Markdown, optionally with native Echo M4B audio.
---

# Explainer Audiobook

Produce a book-length, *listenable* explainer that teaches a subject by touring
a real worked example — the actual app, codebase, product, or system the user
points you at — and explaining each part: what it does, how it works, why it
was chosen, and what was traded away. The output is a chaptered EPUB
(importable into any audiobook/reader app, including on-device text-to-speech
narration) plus a combined Markdown copy. Run all commands from the
explainer-audiobooks repo root.

## Production mode comes first

Read `references/unattended-production.md` before intake. Requests such as
“overnight,” “wake up to a book,” “ready to listen,” or “start a few books” use
`unattended-first-listen`: apply documented defaults, record them in
`research/unattended-decisions.json`, and continue through a private verified
package without routine approval pauses. Treat the human approval language below
as `governed-final` behavior. Unattended mode follows the shared contract's
editorial outline, pilot, pronunciation, cover-selection, delivery, and
package-or-blocker rules. Never infer publication permission.

## Universal paired-cover publishing contract

Every new book creates exactly three source directions and renders each as a
coordinated pair: `cover.png` at 1600×2560 for the EPUB portrait and
`m4b-cover.png` at 2400×2400 for the M4B square. Use `render_cover_pair(...)`
from `skill/scripts/cover_pairs.py`, review both thumbnails, and require
explicit pair selection (human in governed-final, editorial in private
unattended-first-listen). Create the paired receipt (`cover-selection.json`)
with `cover_receipts.py select-pair --selection-source user` (or
`requested-mix`). Embed with
`build_book.py --cover ... --m4b-cover ... --cover-selection ...`. The governed
Echo narration wrapper embeds the square cover itself and binds the exact
resulting M4B bytes into the pronunciation audit.
Never run `replace_m4b_cover.py` or otherwise mutate a narrated M4B after Echo
emits it.
Run `cover_receipts.py verify --cover ... --m4b-cover ... --epub ... --m4b ...`
for post-embed verification. Finally dry-run and apply `sync_selected_cover.py
--paired-artifact-dir ...` for governed public/iCloud/site sync under the
public/private rules below.

Order: research → three source directions → portrait/square render pairs →
thumbnail review → explicit pair selection → paired receipt → EPUB portrait +
M4B square embedding → post-embed verification → governed public/iCloud/site
sync. Legacy single-cover selection commands are verification-only compatibility
and must not be used for new work.

Run the complete paired command sequence from the
"Complete paired command example" in `references/cover-art.md` — including its
rule for when `--permission-to-publish` may be passed — rather than retyping
it from memory.


For an explainer book, `build_book.py` additionally takes
`--non-narrated-appendix "$RUN_ROOT/research/sources.md"` for a readable
sources document that stays outside Echo narration and narrated word counts.

Read `references/declaudification.md` before outlining or drafting. Record the
listener's **AI-writing patterns to avoid**, prevent those phrase families in the
lead-author prompt, and require the family-density gate plus hash-bound prose
receipt before packaging.

Read `references/road-book-mode.md`, `references/learning-design.md`, and
`references/curriculum-patterns.md` before intake or outlining. Default to
road-book mode for listening while driving and delivering mail unless the
listener explicitly selects focused study. Curriculum, chapter teaching, blind
sequential beginner review, human comprehension, prose, and packaging verdicts
are independent. A passing style or media check cannot certify that the book
teaches.

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

Record these before writing anything. In `governed-final`, ask about a missing
decision when it materially improves the book. In `unattended-first-listen`, use
the defaults in `references/unattended-production.md`, record the assumption,
and continue unless the shared contract identifies a real blocker:

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
- **Listening mode** — default: `road-book`, heard while driving and delivering
  mail. Record the primary context and constraints. Use `focused-study` only
  when the listener expects to stop, rewind, or inspect visual material.
- **Revision mode** — use `first-edition-plus` when an earlier edition produced
  learning or curiosity. Preserve its governing question, narrative spine,
  successful examples, and varied chapter jobs. Otherwise record `new-book`.
- **Target length** — default ~45,000 words (~4 hours at 1.25x). See the runtime
  table in `references/narration-style.md`.
- **Voice** — default: warm mentor, second person, spoken. (Confirm if they want
  drier/funnier/more formal.)
- **Voice source** — when the user names private books or audio as an enjoyable
  technical-writing reference, record the local sources for private analysis.
  Derive a high-level craft profile; never commit the source or raw excerpts and
  never ask the author for a close pastiche.
- **Narrator** — if the user also asks for rendered audio, default to
  `am_michael`, fall back to `am_puck`, and do not use `af_heart` as the default.
- **Pronunciation risks** — ask for any terms the listener already knows need
  special attention. Record them and manuscript-derived risks in
  `research/pronunciation-plan.json`; listener-named forms take priority.
- **Title / author** — for the EPUB metadata.

Create the run folder now: `.build/custom-learning-audiobooks/<slug>/` with
`research/`, `chapters/`, and `dist/` subfolders (the governed Echo tooling
expects this shared run-root convention). Seed `research/` by copying the
starter records from `skill/templates/learning-design/` and reading its
`instructions.md` — fill in the schema-v2 starters rather than hand-building
each JSON record from the reference prose.

Create `research/learning-brief.json` now. Record the learner outcome, actual
prior knowledge, audience level, listening and revision modes, opening
orientation (context, promise, and route), original/current word estimates,
estimated range, drafting status, and scope history. Do not lower a target after
drafting begins without explicit user approval recorded as specified in
`references/learning-design.md`. Word count is an estimate, not a floor that can
force added exposition.

A key clarification worth surfacing early: "at most one spoken line of code at a
time" is the rule, which is *not* the same as "don't read code for accuracy" —
and *not* the same as "don't name real things." Read whatever docs and source you
need to get the facts right. You never narrate blocks or unspeakable syntax, but
you *do* speak single commands and *do* name the real files, tools, and commands
out loud (in spoken-friendly form) so the listener finishes knowing the
vocabulary and could go find — and type — these things. Quietly erasing every real name into
"the settings file" is the failure to avoid — see `references/narration-style.md`.

### 2. Ground the research and create the voice-source profile

Run research as its own call before outlining. Build `research/evidence-notes.md`
with stable claim IDs, verified sources, precise locators, contradictions, and
uncertainty. Bind it in `research/evidence-notes.json` with
`claimPolicy: traceable-only`. The outline and manuscript may use only claims
traceable to this artifact; a citation-shaped memory is not evidence.

When the user approved a private writing source, analyze its high-level craft in
`research/voice-source-profile.md`: opening move, evidence-to-example movement,
plain-language mechanism, direct address, humor boundary, uncertainty, rhythm,
practical landing, and visual habits that need translation for audio. Bind the
profile in `comprehension-pilot.json`. Store craft features, not copied prose or
pastiche. The source profile seeds the voice; the accepted project-authored
first section becomes the voice exemplar.

Research workers may extract and verify. They do not choose the learning arc or
write draft prose. Finish and hash these artifacts before the outline call.

### 3. Design the argument-level outline, and get approval before generating

This is the spec. In `governed-final`, present the outline and get a yes first.
In `unattended-first-listen`, require independent editorial authorization bound
to the unattended decisions receipt, then continue.

Build a question-led learning progression rather than a terminology syllabus.
For a beginner road-book, choose six to ten durable outcomes, a governing
question, a narrative spine, people/history anchors, varied real-world
applications, at least four distinct chapter jobs, and an optional-study layer.
Each chapter pairs a small concept set with real consequences and a real
component of the worked example. Name a tradeoff only where a genuine alternative
helps the listener understand the choice. Also pick **2-4 throughlines** —
recurring ideas that give the long listen a spine.

Present the outline as a short table (chapter, concept taught, grounded-in) plus
the throughlines, and ask the user to approve, reorder, or adjust. Tell them the
projected length and runtime as estimates.

Record the approved progression in `research/learning-outline.json`, including
the authorization evidence, two to four throughlines, every chapter's purpose,
its prerequisites, and the selected curriculum pattern with a non-empty reason
and learner-and-subject fit evidence. For every section, record its job,
argument, specific evidence-note claim IDs, throughline advance, narrative or
metaphor payoff, intellectual or emotional landing beat, and what it must not
repeat. A terminology inventory is not an outline. A governed-final road-book
pauses until the user approves this argument-level outline. An unattended
first-listen run records editorial authorization and continues under
`references/unattended-production.md`.

### 4. Write the chapter fact packs and teaching plans

For each chapter, derive from the grounded evidence notes:
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

Also maintain the machine-readable `research/chapter-plans.json` and
`research/coverage-ledger.json` defined in `references/learning-design.md`.
Every chapter records no more than three new core terms, the problem before each
name, its auditory load, a concrete reset, a narrative connection, and a real
application. Every core concept needs a durable outcome, definition, reason,
mechanism, concrete case, varied real-world grounding, useful boundary or
explicit not-applicable reason, misconception, expected ability, analogy
contract or reason to omit one, named chapter uses, and retrieval after a gap.
Mentions and reuses alone do not count as coverage.

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

### 5. Calibrate the first section and render the comprehension pilot

Draft only the first planned section. Give the frontier author the full approved
outline, grounded evidence notes, voice-source profile, that section's job, and
its must-not-repeat list. Revise it narrowly until the intended human accepts its
teaching and voice, then preserve the accepted project-authored text as
`research/voice-exemplar.md`. Record outline approval and first-section
acceptance as separate human checkpoints in `research/comprehension-pilot.json`.

Use that section to create only enough frontier-authored pilot prose for 10 to 15 representative
minutes. It includes the opening orientation and first technical passage, uses
no more than three durable terms, reaches at least two real applications or
consequences, and retrieves the central distinction in a fresh example.

Build an explicitly nonpackage pilot EPUB; the `-pilot` slug is mandatory:

```bash
python3 skill/scripts/build_book.py \
  --chapters-dir "$RUN_ROOT/pilot/chapters" \
  --out-dir "$RUN_ROOT/pilot/dist" \
  --title "$TITLE — Learning Pilot" \
  --author "Dan Fakkeldy" \
  --slug "$SLUG-pilot" \
  --learning-pilot
```

Render it through the governed Echo path. Have the intended listener hear it in
a representative context, then record the exact audio hash, listening context,
and one lightweight `continue` or `revise` decision. Accept optional listener
notes, but do not ask comprehension questions or require a written explanation.
Record the verdict in `research/comprehension-pilot.json`. Full drafting remains blocked until the
listener records `verdict: continue`. The first-section checkpoint and listening
pilot are both required. Outline approval, text review, or agent confidence
cannot substitute for this gate.

### 6. Draft section by section with a frontier lead author

Pre-create a build directory with a `chapters/` subfolder. One frontier model
owns every section's narration and all substantive revisions. Write in order to
`chNN.md`; do **not** fan out prose drafting to cheaper models or independent
chapter writers and never generate the whole book in one call.

Before every section call, write its entry in
`research/continuity.json.draftContexts`. Give the frontier author the full
argument-level outline, grounded evidence IDs, approved voice exemplar, relevant
coverage rows and fact pack, the previous section's actual text or faithful
running summary, the current section's job, and what it must not repeat. Update
the readable `research/continuity.md` and structured record after every section,
including terms, analogies, examples, callbacks, unresolved promises, retrievals,
listener load, and no-repeat constraints. A static note created before the
manuscript is not forward context. The chapter files are canonical; EPUB, audio,
and all other formats are downstream renderings.

Cheaper workers may extract sources, build fact packs, check citations, run
diagnostics, simulate a beginner listener, assemble files, make covers, render
audio, and produce short editorial reports with exact quotations and locations.
They do **not** write or replace whole chapters. A bounded mechanical edit is
acceptable only when it cannot change meaning; return depth, structure,
explanation, and factual corrections to the frontier author. Follow
`references/frontier-manuscript-pipeline.md` for the role contract and review
format.

### 7. Run separate single-job revision and review passes

Do not ask any model to "make it better." Run and record the required passes in
`research/revision-passes.json`, one call and one job at a time:

1. `claim-traceability` against the grounded evidence notes;
2. `tightening` for avoidable repetition and filler;
3. `de-listification` for mechanical list rhythm and false symmetry;
4. `sentence-rhythm` for spoken variation without a new voice;
5. `ear-pass` using rendered Echo or Kokoro audio, recording each stumble and
   each place the listener loses the thread.

Bind the completed pass ledger to the final chapter hashes. A pass may return no
findings; it may not borrow work from another lane to manufacture activity.

Then run the remaining QC and learning reviews:

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
- `python3 skill/scripts/prose_qc.py --chapters-dir <build>/chapters` to surface
  repeated phrases, similar paragraphs, and formulaic openings/closings. Treat
  it as a candidate list, not a blind rewrite instruction: intentional
  vocabulary retrieval is allowed only when the coverage ledger explains it;
- follow `references/declaudification.md` and run `prose_qc.py` with
  `--fail-on-style` before and after the humanizer. The initial run is an
  independent inventory; the final run records accepted and rejected decisions
  and writes `research/prose-style-receipt.json` bound to the canonical chapter
  hashes;
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
targeted patches for accepted findings; do not request a wholesale second draft
if the reports only find local issues.

Before the humanizer, run the independent structure review and the blind
sequential beginner review from `references/learning-design.md`. Give the blind
reviewer only the manuscript in listening order—never the outline, coverage
ledger, expected abilities, or author rationale. After each chapter it records
the mental model a beginner could plausibly form, unstable terms, confusions,
and the exact point where the listener may become lost. The frontier author
resolves accepted findings.

Then load the `humanizer` skill and follow `references/humanizer-pass.md` for a
light, bounded humanizing pass over the canonical Markdown. Remove AI tics,
generic signposting, inflated claims, and repetitive rhythm, while preserving
facts, citations, technical names, teaching structure, intentional retrieval,
and the frontier author's voice. The humanizer must not invent anecdotes,
opinions, first-person experience, sources, jokes, or new claims, and must not
rewrite the book wholesale. The frontier author reviews and accepts every
non-mechanical change before EPUB/audio packaging; rerun factual, ledger, and
narration checks afterward.

Rerun both learning reviews after every accepted voice edit and record their
passing final-hash verdicts in `research/learning-review.json`. Then generate the
separate learning receipt:

```bash
python3 skill/scripts/learning_design_qc.py \
  --run-root "$RUN_ROOT" \
  --receipt-out "$RUN_ROOT/research/learning-design-receipt.json"
```

The learning and prose receipts must bind the same canonical chapter hashes.
The learning receipt proves the schema-v2 process and accepted pilot; it does
not certify learning transfer. Any later negative human listening verdict
overrides both receipts and stops production.

### 8. Make a cover, then assemble the EPUB + Markdown

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

Save the shared art and two schema-v2 specifications in each candidate directory,
then use the complete `render_cover_pair(...)` call above for candidates 1, 2,
and 3. Review every full-size portrait and square render and generated
160-pixel thumbnail with its brief, font/palette note, and warnings. Send all
three complete candidates to the user and ask them to choose or request a mix;
a mix becomes a new specification and render. The renderer never selects a
candidate automatically.

Legacy single-cover receipts (created with `cover_receipts.py select` and
`--selection-source explicit-user-choice`) are verification-only compatibility
for pre-paired packages; the preserved legacy command shapes live in the
compatibility sections of `references/cover-art.md` and
`skills/custom-learning-audiobook/references/package-and-qc.md`. Never use
them for new work.

Assign `SLUG`, `TITLE`, `SUBTITLE`, `EDITION_ID`, `SELECTED_AT`,
`CLASSIFICATION`, and `CONTRIBUTOR` from the approved run metadata, then run
the paired `select-pair` and `build_book.py` commands from
`references/cover-art.md`. New builds pass `--learning-receipt` and
`--prose-receipt`; packaging stops if either receipt is missing, failed, or
stale. `build_book.py` writes a valid EPUB 3 (with both a nav and an NCX table of contents, and the
cover embedded as both the library thumbnail and a full-bleed first page) plus a
combined Markdown file, and prints per-chapter word counts and an estimated
runtime. The EPUB author (`dc:creator`) is the human; the generating model is
recorded as a `dc:contributor`. `--cover` and `--contributor` are optional.
`--non-narrated-appendix` is optional; use it for a readable sources document
that should remain outside Echo narration and narrated word counts. Its filename
must not start with `ch`.
Verify the EPUB is valid (the `mimetype` check in `references/narration-style.md`).

### 9. Native Echo/Kokoro M4B and alignment

For a complete governed package, render native Echo/Kokoro audio only after the
governed EPUB exists. Follow the complete wrapper and receipt procedure in
`skills/custom-learning-audiobook/references/package-and-qc.md`. Create
`research/pronunciation-plan.json`, including listener-named risks and every
spoken variant. Render bounded partial chapters first, use
`build_pronunciation_probe_reel.py`, and require accepted, hash-bound human
listening evidence before an unbounded render. Export the canonical plan path:

```bash
EXPLAINER_ROOT=$(git rev-parse --show-toplevel)
export EXPLAINER_ROOT
export RUN_ROOT="$EXPLAINER_ROOT/.build/custom-learning-audiobooks/$SLUG"
export PRONUNCIATION_PLAN="$RUN_ROOT/research/pronunciation-plan.json"
"$EXPLAINER_ROOT/skills/custom-learning-audiobook/scripts/echo_pronunciation_narrate.sh" \
  --max-chapters 1
```

If `am_michael` is unavailable, retry with the Echo voice `am_puck` and record
the fallback. Do not impose a timeout on a progressing render, and do not silently
replace Echo/Kokoro with Apple/macOS/system narration. Resume a partial render
through the governed wrapper. Never bypass its pronunciation-plan gate.

After Echo writes the M4B and alignment sidecar, complete the selector-bound
"Audio And Alignment QC" flow in
`skills/custom-learning-audiobook/references/package-and-qc.md` (it sets
`AUDIOBOOK` from the verified current-accepted selector), then run the paired
`cover_receipts.py verify` command from `references/cover-art.md` across the
selected pair, governed EPUB, and `$AUDIOBOOK`.

If native Echo audio is blocked, the EPUB and Markdown may be surfaced directly
from `dist/` as clearly labelled **interim** files. They are not a complete
governed package, and the workflow does not proceed to package sync until native
Echo audio and the final M4B receipt verification succeed.

### 10. Governed delivery

Set `DELIVERY_DIR` to the approved delivery folder, then run the paired
`sync_selected_cover.py` commands from `references/cover-art.md`: first as a
dry run — it reports `new`, `reuse`, `supersede`, or a conflict without
writing — and only after the reported classification is expected, rerun the
same command and intent with `--apply`. Use `--intent supersede` only for a
newer explicit choice. A cover-bearing destination without a receipt is an
`unreceipted` conflict unless the operation is an explicit supersession.

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

Never use `--legacy-without-learning-receipt` for a new or revised manuscript,
new edition, or current-workflow quality claim. It exists only to reproduce an
older artifact that predates the learning gate. Use `--learning-pilot` only for
the explicitly named nonpackage comprehension pilot; it cannot support a book
completion or delivery claim.

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
- `scripts/cover_pairs.py` — renders one candidate's coordinated portrait and
  square covers plus thumbnails and render receipts (`render_cover_pair(...)`).
- `scripts/make_cover_contact_sheet.py` — builds a review contact sheet from
  the rendered candidates.
- `scripts/prose_qc.py` — repeated-phrase/formula sweep plus the
  `--fail-on-style` de-Claudification gate and hash-bound prose receipt.
- `scripts/learning_design_qc.py` — validates the schema-v2 learning records
  and writes the hash-bound learning receipt.
- `scripts/pronunciation_plan_qc.py` — validates `pronunciation-plan.json` in
  `planning` and `full-render` phases and writes its receipt.
- `scripts/build_pronunciation_probe_reel.py` — builds the governed listening
  reel from partial chapter captures.
- `scripts/replace_m4b_cover.py` — legacy-artifact compatibility only; never
  run it on a narrated Echo M4B.
- `templates/learning-design/` — schema-v2 starter records to copy into a run's
  `research/` before pilot work; read its `instructions.md`.
- `schemas/cover-spec-v1.schema.json` — validates cover specs (schema versions
  1 and 2).
- `references/narration-style.md` — the voice & rules block to give the frontier
  author verbatim, the reasoning behind them, the length/runtime table, the
  fact-pack discipline, and the QC checklist. Read before writing fact packs.
- `references/cover-art.md` — how to design, render, review, and explicitly
  select three complete art-and-type candidates; ships with
  `cover-art-example.svg` as a structural reference for an approved vector
  fallback.
- `references/frontier-manuscript-pipeline.md` — the artifactized research,
  argument outline, section-drafting, voice-exemplar, single-job revision,
  frontier-author / cheaper-worker split, and citation-first review format.
- `references/humanizer-pass.md` — the bounded `humanizer` pass for removing
  AI-writing tells without replacing the frontier author's voice or meaning.
- `references/declaudification.md` — drafting prohibitions, rhetorical phrase
  families, density limits, the two-pass humanizer inventory, and the
  hash-bound prose receipt required for new packages.
- `references/road-book-mode.md` — the driving/delivery listening mode,
  first-edition-plus revision rule, narrative and real-world teaching
  infrastructure, concept/working-memory budgets, optional-study boundary,
  blind review, and human comprehension pilot.
- `references/learning-design.md` — grounded evidence notes, the structured
  learner orientation, argument-level outline, chapter plans, complete
  explanation paths, section forward-context checkpoints, revision-pass ledger,
  blind sequential review, comprehension-pilot record, scope-history rule, and hash-bound process
  receipt required before packaging.
- `references/curriculum-patterns.md` — the selectable learning progressions
  and the selection/fit evidence the outline must record.
- `references/unattended-production.md` — the shared
  governed-final/unattended-first-listen contract: mode triggers, documented
  defaults, editorial checkpoints, and package-or-blocker rules.
