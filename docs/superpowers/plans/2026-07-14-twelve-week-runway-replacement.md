# The Twelve-Week Runway Replacement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the incorrectly duplicated twelve-week introduction with a distinct, verified private audiobook titled *The Twelve-Week Runway* while preserving both existing *Before the Blueprint* packages.

**Architecture:** The longform workspace remains the private series canon, while a new `.build/custom-learning-audiobooks/the-twelve-week-runway/` run owns research, learning-design evidence, canonical Markdown, covers, package derivatives, and Echo receipts. Manuscript acceptance, cover selection, EPUB assembly, Echo narration, and delivery are separate fail-closed gates so a later change cannot inherit stale approval evidence.

**Tech Stack:** Markdown and JSON planning records, Anthropic and SGridworks primary/community sources, repository Python tooling, paired raster-cover specifications, EPUB 3, native Echo/Kokoro narration, `ffprobe`, `unzip`, SHA-256 receipts, iCloud Drive, Git, and GitHub CLI.

## Global Constraints

- Title: *The Twelve-Week Runway*.
- Subtitle: *How to Use the Claude Architect's Workshop*.
- Series position: Volume 0 of *The Claude Architect's Workshop*.
- Target runtime: 45–55 minutes.
- Target manuscript range: 6,700–8,300 canonical words, with 7,500 words as the planning target.
- Privacy classification: `private`; permission to publish: `not-requested`.
- Narrator: native Echo/Kokoro `am_michael`, with `am_puck` only as the documented Echo-resource fallback.
- The earlier four-week-series package at `/Users/dfakkeldy/Documents/Codex/custom-learning-audiobooks/before-the-blueprint/` is immutable historical material.
- The incorrect twelve-week *Before the Blueprint* package remains recoverable until the replacement is fully verified, then moves to a private superseded archive without deletion.
- Private manuscript, research, audio, alignment, and receipt artifacts do not enter Git or the public knowledge base.
- The replacement uses exactly three coordinated portrait/square raster cover candidates and pauses for Dan's explicit selection.
- Do not mutate, retag, or replace the cover of an audited M4B after Echo narration.
- Human listening remains `pending` until Dan or another person actually hears the reel or matching final passages.

---

### Task 1: Refresh live state and preserve the two source editions

**Files:**
- Inspect: `/Users/dfakkeldy/Documents/Codex/custom-learning-audiobooks/before-the-blueprint/manifest.json`
- Inspect: `/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/Before the Blueprint/README.md`
- Inspect: `/Users/dfakkeldy/.codex/worktrees/2776/explainer-audiobooks/.build/custom-learning-audiobooks/before-the-blueprint/research/echo-render-current-accepted.json`
- Create: `/Users/dfakkeldy/.codex/worktrees/2776/explainer-audiobooks/.build/custom-learning-audiobooks/the-twelve-week-runway/research/preservation-inventory.md`

**Interfaces:**
- Consumes: the design spec and both existing package trees.
- Produces: a path, title, chapter, media-hash, and role inventory that later archive and delivery steps must match.

- [ ] **Step 1: Confirm the repository and concurrent-render state**

  Run:

  ```bash
  git status --short --branch
  git log -1 --oneline
  ps aux | rg '[e]cho-cli|[e]cho_pronunciation_narrate' || true
  ```

  Expected: the tracked worktree contains only planned agent changes, and any active Echo process is identified before package files are moved.

- [ ] **Step 2: Record both editions without changing either package**

  Use `jq`, `shasum -a 256`, `ffprobe`, and chapter-heading extraction to record:

  - the older four-week-series package role and exact location;
  - the incorrect twelve-week package role and exact location;
  - M4B, EPUB, and alignment hashes when present;
  - chapter titles and runtime;
  - the current accepted Echo run and source revision.

  Save the evidence in `research/preservation-inventory.md` using `apply_patch`.

- [ ] **Step 3: Verify the inventory is complete**

  Run:

  ```bash
  rg -n 'four-week|twelve-week|M4B SHA-256|EPUB SHA-256|accepted Echo run|do not delete' \
    .build/custom-learning-audiobooks/the-twelve-week-runway/research/preservation-inventory.md
  ```

  Expected: every required label appears once with a nonempty value or an explicit `not present` observation.

### Task 2: Update the private thirteen-volume series canon

**Files:**
- Modify: `.build/longform-book-development/claude-certified-architect-series/brief.md`
- Modify: `.build/longform-book-development/claude-certified-architect-series/outline.md`
- Modify: `.build/longform-book-development/claude-certified-architect-series/conversation-log.md`
- Modify: `.build/longform-book-development/claude-certified-architect-series/handoff/handoff-packet.md`
- Modify: `.build/longform-book-development/claude-certified-architect-series/implementation-plan.md`
- Modify: `.build/longform-book-development/claude-certified-architect-series/visuals/manifest.md`

**Interfaces:**
- Consumes: the approved replacement design and preservation inventory.
- Produces: one consistent series canon in which *Before the Blueprint* belongs only to the earlier four-week sequence and Volume 0 is *The Twelve-Week Runway*.

- [ ] **Step 1: Replace Volume 0's identity and learning job**

  Use `apply_patch` to update every private series file. Preserve the twelve weekly titles, but change Volume 0 to:

  ```text
  The Twelve-Week Runway
  How to Use the Claude Architect's Workshop
  ```

  Define its job as the twelve-week operating system: baseline, weekly loop, evidence trail, recovery rules, readiness, and Week 1 handoff.

- [ ] **Step 2: Record the collision and correction in the conversation log**

  Add the approved 2026-07-14 decision: the previous title collided with the earlier four-week introduction, the overlap was substantive, and Dan approved full differentiation rather than a jacket-only rename.

- [ ] **Step 3: Verify canon consistency**

  Run:

  ```bash
  SERIES=.build/longform-book-development/claude-certified-architect-series
  rg -n 'The Twelve-Week Runway|the-twelve-week-runway' "$SERIES"
  rg -n 'Before the Blueprint' "$SERIES"
  ```

  Expected: the new title and slug appear in the active Volume 0 instructions; remaining old-title mentions describe the historical four-week book or the correction only.

### Task 3: Build the source-led learning design before drafting

**Files:**
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/research/brief.md`
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/research/learning-brief.json`
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/research/sources.md`
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/research/fact-pack.md`
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/research/outline.md`
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/research/learning-outline.json`
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/research/chapter-plans.json`
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/research/coverage-ledger.md`
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/research/coverage-ledger.json`
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/research/continuity.md`
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/research/continuity.json`
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/research/visuals.md`

**Interfaces:**
- Consumes: the updated handoff packet, live SGridworks repositories, linked primary Anthropic sources, and the older/newer manuscript comparison.
- Produces: an authorized seven-chapter learning progression and complete explanation paths before canonical prose begins.

- [ ] **Step 1: Refresh drift-prone sources**

  Browse the live SGridworks twelve-week and four-week repositories and follow their links to primary Anthropic documentation, Academy material, credential announcements, API/Agent SDK/MCP documentation, and current certification information. Record retrieval date `2026-07-14`, source class, confidence, and conflicts in `sources.md`; community repositories are curriculum maps, not exam authorities.

- [ ] **Step 2: Write the learner contract**

  Set these exact values in `learning-brief.json`:

  ```json
  {
    "schemaVersion": 1,
    "learnerOutcome": "Run the twelve-week Claude Architect's Workshop as a sustainable listen, retrieve, build, explain, and record-evidence practice system.",
    "priorKnowledge": "Experienced directing coding agents and shipping software; gaps in raw Claude API, Agent SDK, MCP, and current certification mechanics are explained rather than assumed.",
    "openingOrientation": {
      "context": "A four-week certification sprint compresses exposure but leaves little room for retrieval, deliberate practice, failure analysis, and recovery.",
      "promise": "The listener will know how to use the slower twelve-week sequence and how to recognize evidence of growing architecture skill.",
      "route": "Establish the reason for twelve weeks, map the baseline, install the weekly loop, preview the twelve volumes, collect evidence, recover from disruption, and begin Week 1."
    },
    "originalTargetWords": 7500,
    "currentTargetWords": 7500,
    "minimumAcceptedWords": 6700,
    "maximumAcceptedWords": 8300,
    "draftingStarted": false,
    "scopeHistory": []
  }
  ```

- [ ] **Step 3: Encode the approved seven-chapter progression**

  Create `learning-outline.json` and `chapter-plans.json` for these files and jobs:

  1. `ch01.md` — Why Twelve Weeks
  2. `ch02.md` — Set the Baseline
  3. `ch03.md` — The Weekly Operating Loop
  4. `ch04.md` — The Twelve-Volume Map
  5. `ch05.md` — Build an Evidence Trail
  6. `ch06.md` — When Real Life Breaks the Schedule
  7. `ch07.md` — Readiness and the Week 1 Handoff

  Authorization must use `status: approved`, `source: user`, and evidence `Dan approved the written replacement design on 2026-07-14.` Throughlines are sustainable pace, recognition versus demonstrated ability, and artifacts as evidence.

- [ ] **Step 4: Complete explanation paths and visual decision**

  Add full definition, reason, mechanism, concrete case, boundary, misconception, expected ability, and chapter-use records for: baseline gap map, weekly operating loop, retrieval, minimum viable week, evidence trail, recovery rule, consolidation week, and readiness. Record `figure count: 0`; the introduction must work entirely by ear.

- [ ] **Step 5: Validate structured learning files before drafting**

  Run:

  ```bash
  RUN_ROOT=.build/custom-learning-audiobooks/the-twelve-week-runway
  python3 -m json.tool "$RUN_ROOT/research/learning-brief.json" >/dev/null
  python3 -m json.tool "$RUN_ROOT/research/learning-outline.json" >/dev/null
  python3 -m json.tool "$RUN_ROOT/research/chapter-plans.json" >/dev/null
  python3 -m json.tool "$RUN_ROOT/research/coverage-ledger.json" >/dev/null
  python3 -m json.tool "$RUN_ROOT/research/continuity.json" >/dev/null
  ```

  Expected: every command exits zero, and `draftingStarted` is still `false`.

### Task 4: Draft and accept the canonical seven-chapter manuscript

**Files:**
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/chapters/ch01.md`
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/chapters/ch02.md`
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/chapters/ch03.md`
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/chapters/ch04.md`
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/chapters/ch05.md`
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/chapters/ch06.md`
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/chapters/ch07.md`
- Modify after every chapter: `.build/custom-learning-audiobooks/the-twelve-week-runway/research/continuity.md`
- Modify after every chapter: `.build/custom-learning-audiobooks/the-twelve-week-runway/research/continuity.json`
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/research/editorial-review.md`
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/research/learning-review.json`
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/research/humanizer-decisions.json`
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/research/prose-qc-before.md`
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/research/prose-qc-after.md`
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/research/prose-style-receipt.json`
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/research/learning-design-receipt.json`

**Interfaces:**
- Consumes: the approved structured learning design and cited fact pack.
- Produces: final canonical Markdown whose chapter hashes are accepted independently for pedagogy and prose style.

- [ ] **Step 1: Mark drafting as started and write chapters sequentially**

  Change `draftingStarted` to `true`, then write one chapter at a time with the same frontier author. Each file has exactly one H1 title and flowing spoken prose without internal headings, tables, bullet lists, code blocks, leaked test questions, or unsourced technical claims.

- [ ] **Step 2: Update continuity immediately after each chapter**

  After `ch01.md` through `ch07.md`, append one structured checkpoint with `afterChapter`, `termsDefined`, `examplesUsed`, `callbacks`, `promises`, and `unresolvedQuestions`. The next chapter is not drafted until the prior checkpoint exists.

- [ ] **Step 3: Run the first narration and style inventory**

  Run:

  ```bash
  RUN_ROOT=.build/custom-learning-audiobooks/the-twelve-week-runway
  wc -w "$RUN_ROOT"/chapters/ch*.md
  python3 skill/scripts/prose_qc.py \
    --chapters-dir "$RUN_ROOT/chapters" \
    --out "$RUN_ROOT/research/prose-qc-before.md" \
    --fail-on-style
  rg -n '`|```|[A-Za-z]+_[A-Za-z_]+|->|[{}]|\b[A-Za-z]+\(\)' "$RUN_ROOT/chapters" || true
  rg -ni 'tattoo|burn (this|it) into|the single most important|the whole point|let that land|hold on to this|sit with that' "$RUN_ROOT/chapters" || true
  ```

  Expected: total canonical word count is 6,700–8,300; prohibited prose and narration patterns have no unresolved matches.

- [ ] **Step 4: Perform independent structural and beginner-reader reviews**

  Record exact-location findings in `learning-review.json` and `editorial-review.md`. The frontier author accepts or rejects every finding and writes all substantive repairs. Rerun both reviews after the bounded humanizer pass; both final verdicts must be `pass` and bind every final chapter SHA-256.

- [ ] **Step 5: Create final independent receipts**

  Run:

  ```bash
  RUN_ROOT=.build/custom-learning-audiobooks/the-twelve-week-runway
  python3 skill/scripts/learning_design_qc.py \
    --run-root "$RUN_ROOT" \
    --receipt-out "$RUN_ROOT/research/learning-design-receipt.json"
  python3 skill/scripts/prose_qc.py \
    --chapters-dir "$RUN_ROOT/chapters" \
    --out "$RUN_ROOT/research/prose-qc-after.md" \
    --fail-on-style \
    --decisions "$RUN_ROOT/research/humanizer-decisions.json" \
    --style-receipt-out "$RUN_ROOT/research/prose-style-receipt.json"
  ```

  Expected: both commands exit zero and both receipts contain the same seven final chapter hashes.

### Task 5: Generate exactly three paired cover candidates and pause for selection

**Files:**
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/dist/candidate-1/source-art.png`
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/dist/candidate-1/cover-spec.json`
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/dist/candidate-1/m4b-cover-spec.json`
- Create matching pair artifacts under: `candidate-1/`, `candidate-2/`, and `candidate-3/`
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/research/cover-briefs.md`
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/dist/cover-contact-sheet.png`

**Interfaces:**
- Consumes: the accepted title, subtitle, editorial promise, and three cover directions.
- Produces: three complete portrait/square pairs for explicit human selection; it does not produce `cover-selection.json` yet.

- [ ] **Step 1: Write three genuinely different art-and-type briefs**

  Use these directions as starting points, sharpening each anti-brief before generation:

  - **Runway Lights:** a high-key overhead physical runway with twelve discrete markers, warm paper-white and safety orange, no airplane, arrow, ladder, dashboard, or blueprint.
  - **Twelve Field Cards:** tactile letterpress cards arranged as a measured working sequence, cobalt and acid yellow, no checklist UI, calendar grid, certification seal, or generic productivity system.
  - **Calibration Bench:** a documentary/editorial still life of twelve precisely spaced calibration weights leading to one active workpiece, charcoal and electric cyan, no laptop, robot, code rain, glowing brain, or architectural blueprint.

- [ ] **Step 2: Generate text-free raster art and render paired specifications**

  Use the image-generation tool for all three source images. Create schema-v2 portrait and square specifications, then call `render_cover_pair` once for each candidate so every directory contains portrait/square PNGs, thumbnails, and render receipts.

- [ ] **Step 3: Inspect full-size images and thumbnails**

  Verify dimensions:

  ```bash
  RUN_ROOT=.build/custom-learning-audiobooks/the-twelve-week-runway
  for n in 1 2 3; do
    sips -g pixelWidth -g pixelHeight "$RUN_ROOT/dist/candidate-$n/cover.png"
    sips -g pixelWidth -g pixelHeight "$RUN_ROOT/dist/candidate-$n/m4b-cover.png"
    test -s "$RUN_ROOT/dist/candidate-$n/cover-render.json"
    test -s "$RUN_ROOT/dist/candidate-$n/m4b-cover-render.json"
  done
  ```

  Expected: portrait covers are 1600×2560, square covers are 2400×2400, all thumbnails remain legible at 160 pixels, and no candidate is a recolour of another.

- [ ] **Step 4: Present all three pairs and stop**

  Show the contact sheet plus individual portrait/square pairs, summarize each visual thesis and any warnings, and ask Dan to choose `1`, `2`, `3`, or request a mix. Do not create a selection receipt, EPUB, or M4B before that response.

### Task 6: Build the governed EPUB and combined Markdown after cover selection

**Files:**
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/dist/cover-selection.json`
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/dist/the-twelve-week-runway.epub`
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/dist/the-twelve-week-runway.md`

**Interfaces:**
- Consumes: the selected paired-cover receipts and both final manuscript receipts.
- Produces: immutable source EPUB and Markdown derivatives for Echo narration.

- [ ] **Step 1: Create the paired user-selection receipt**

  Set `SLUG=the-twelve-week-runway`, a new edition ID, `selection_source=user`, `privacy_classification=private`, and `permission_to_publish=not-requested`. Copy the receipt into the selected candidate directory.

- [ ] **Step 2: Build from the final canonical chapter hashes**

  Run `skill/scripts/build_book.py` with the selected portrait and square cover, the paired selection receipt, `learning-design-receipt.json`, and `prose-style-receipt.json`. Contributor metadata records the frontier author used in this session.

- [ ] **Step 3: Verify EPUB structure and metadata**

  Run:

  ```bash
  RUN_ROOT=.build/custom-learning-audiobooks/the-twelve-week-runway
  unzip -t "$RUN_ROOT/dist/the-twelve-week-runway.epub"
  python3 -c "import zipfile; p='$RUN_ROOT/dist/the-twelve-week-runway.epub'; z=zipfile.ZipFile(p); i=z.infolist()[0]; print(i.filename, i.compress_type)"
  rg -n '^# ' "$RUN_ROOT/dist/the-twelve-week-runway.md"
  ```

  Expected: archive test passes, first ZIP entry reports `mimetype 0`, title metadata is *The Twelve-Week Runway*, and seven chapters appear in order.

### Task 7: Render and verify a fresh native Echo audiobook

**Files:**
- Create through governed wrapper: `.build/custom-learning-audiobooks/the-twelve-week-runway/research/echo-render-inputs-<run-id>.env`
- Create through governed wrapper: `.build/custom-learning-audiobooks/the-twelve-week-runway/research/echo-resume-state-<run-id>.json`
- Create through governed wrapper: `.build/custom-learning-audiobooks/the-twelve-week-runway/research/echo-render-current-attempt.json`
- Create through governed wrapper: `.build/custom-learning-audiobooks/the-twelve-week-runway/research/echo-render-current-accepted.json`
- Create through governed wrapper: `.build/custom-learning-audiobooks/the-twelve-week-runway/research/echo-render-success-<run-id>-<attempt-id>.json`
- Create through governed wrapper under `dist/echo-renders/<run-id>/<attempt-id>/`: M4B, alignment sidecar, pronunciation audit, and optional reel

**Interfaces:**
- Consumes: the immutable selected-cover EPUB, selected portrait/square cover pair, and an explicitly reviewed clean Echo revision.
- Produces: one accepted run/attempt chain whose receipts bind the source EPUB, Echo binary/resources, cover pair, M4B, sidecar, and pronunciation evidence.

- [ ] **Step 1: Reverify Echo source and select the approved pronunciation revision**

  Run in `/Users/dfakkeldy/Developer/Echo`:

  ```bash
  git status --short --branch
  git rev-parse HEAD
  git log -5 --oneline
  ```

  Review the current pronunciation and cover-binding changes. Set `APPROVED_ECHO_PRONUNCIATION_SHA` to that exact clean `HEAD`; do not infer approval from ancestry.

- [ ] **Step 2: Run the governed wrapper without an external timeout**

  Export `RUN_ROOT`, `DIST`, `SLUG`, `TITLE`, `VOICE=am_michael`, `COVER`, `M4B_COVER`, and `APPROVED_ECHO_PRONUNCIATION_SHA`, then run:

  ```bash
  skills/custom-learning-audiobook/scripts/echo_pronunciation_narrate.sh
  ```

  Let a progressing render finish. Use `--resume` only when the content-addressed inputs and sealed state remain identical.

- [ ] **Step 3: Verify the accepted selector chain and media**

  Run the complete `echo_pronunciation_state.py verify-delivery` flow from `references/package-and-qc.md`, then:

  ```bash
  ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$AUDIOBOOK"
  python3 -m json.tool "$SIDECAR" >/dev/null
  "$CLI" verify-sidecar --epub "$DIST/$SLUG.epub" --audio "$AUDIOBOOK" --sidecar "$SIDECAR"
  skills/custom-learning-audiobook/scripts/validate_pronunciation_audit.py "$AUDIT"
  /usr/local/bin/python3 skill/scripts/cover_receipts.py verify \
    --selection "$DIST/cover-selection.json" \
    --cover "$PAIR/cover.png" \
    --m4b-cover "$PAIR/m4b-cover.png" \
    --epub "$DIST/$SLUG.epub" \
    --m4b "$AUDIOBOOK" \
    --receipt "$DIST/cover-selection.json"
  ```

  Expected: `SIDECAR_OK`, valid schema-v2 pronunciation audit with complete coverage, positive duration, exact square-cover match, and matching accepted-selector hashes.

- [ ] **Step 4: Record listening status honestly**

  If the reel or final passages are not heard in this session, record `human listening: pending`; automated pronunciation checks do not convert that status to passed.

### Task 8: Deliver the private replacement and archive the incorrect edition safely

**Files:**
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/dist/README.md`
- Create: `.build/custom-learning-audiobooks/the-twelve-week-runway/dist/delivery-manifest.json`
- Create durable private package: `/Users/dfakkeldy/Documents/Codex/custom-learning-audiobooks/the-twelve-week-runway/`
- Create authorized reading copy: `/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/The Twelve-Week Runway/`
- Move after verification only: `/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/Before the Blueprint/`
- Archive destination: `/Users/dfakkeldy/Documents/Codex/custom-learning-audiobooks/superseded/before-the-blueprint-twelve-week-edition-2026-07-14/`

**Interfaces:**
- Consumes: the verified current accepted run and preservation inventory.
- Produces: one durable private package, one iCloud listening copy, and one recoverable superseded package; the four-week historical package remains untouched.

- [ ] **Step 1: Write package metadata**

  Record title, subtitle, slug, private status, publication permission, word count, runtime, chapter count, narrator, source-confidence label, frontier author, figure count zero, selected candidate, all current Echo/EPUB/CLI/resource hashes and receipt paths, QC results, and human listening status.

- [ ] **Step 2: Dry-run then apply governed private delivery**

  Use `sync_selected_cover.py` with the selected pair, `--intent reuse`, and `--paired-artifact-dir` first without and then with `--apply` for the Documents/Codex destination. Copy the remaining verified sidecars and receipts without overwriting the governed files.

- [ ] **Step 3: Dry-run then apply the explicitly authorized iCloud reading copy**

  Repeat the governed sequence for `/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/The Twelve-Week Runway/`. Verify the copied EPUB, M4B, sidecar, audit, cover receipt, and accepted Echo chain from the destination path.

- [ ] **Step 4: Archive the incorrect twelve-week delivery**

  Recompare its hashes with `preservation-inventory.md`, confirm no active render owns it, create the `superseded/` parent if absent, and move the whole iCloud `Before the Blueprint` directory to the exact archive destination. Stop if the destination already exists or any hash has changed since Task 1; never merge directories or overwrite the four-week package.

- [ ] **Step 5: Verify all three outcomes**

  Run:

  ```bash
  test -f '/Users/dfakkeldy/Documents/Codex/custom-learning-audiobooks/before-the-blueprint/before-the-blueprint.m4b'
  test -f '/Users/dfakkeldy/Documents/Codex/custom-learning-audiobooks/the-twelve-week-runway/the-twelve-week-runway.m4b'
  test -f '/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/The Twelve-Week Runway/the-twelve-week-runway.m4b'
  test -f '/Users/dfakkeldy/Documents/Codex/custom-learning-audiobooks/superseded/before-the-blueprint-twelve-week-edition-2026-07-14/before-the-blueprint.m4b'
  ```

  Expected: all four checks pass; `brctl status com.apple.CloudDocs` shows no incomplete item for the new iCloud package before delivery is reported complete.

### Task 9: Correct the durable business record without leaking private content

**Files:**
- Modify in a clean KB worktree: `/Users/dfakkeldy/Developer/knowledge-base/bundle/projects/explainer-audiobooks.md`
- Create or supersede in a clean KB worktree: `/Users/dfakkeldy/Developer/knowledge-base/bundle/status/2026-07-14-claude-architect-audiobook-series.md`
- Modify in a clean KB worktree: `/Users/dfakkeldy/Developer/knowledge-base/bundle/status/index.md`
- Modify in a clean KB worktree: `/Users/dfakkeldy/Developer/knowledge-base/bundle/log.md`

**Interfaces:**
- Consumes: the verified delivery manifest and existing incorrect KB receipt.
- Produces: a narrow operational record naming the corrected title, private paths, verification status, and historical distinction without copying manuscript or research text.

- [ ] **Step 1: Create a clean KB worktree and reread its instructions**

  Fetch `origin/main`, create a `codex/twelve-week-runway-receipt` worktree from current main, and reread `AGENTS.md`, `bundle/index.md`, the project page, and the existing series status page before editing.

- [ ] **Step 2: Correct the current title and package status**

  Mark the earlier twelve-week *Before the Blueprint* receipt as superseded or update the active status page according to KB retention rules. State that the older same-title four-week book remains separate. Include only durable folder paths, runtime/word count, QC gates, human-listening status, and the public/private decision.

- [ ] **Step 3: Lint, commit, push, and open the KB PR**

  Run:

  ```bash
  python3 tools/kb_lint.py
  git diff --check
  git status --short --branch
  ```

  Expected: KB lint and diff check pass. Commit with `docs: correct Claude architect audiobook title`, push, open a ready PR to `main`, and inspect hosted CI.

### Task 10: Publish the public process documentation and final verification

**Files:**
- Verify: `docs/superpowers/specs/2026-07-14-twelve-week-runway-replacement-design.md`
- Verify: `docs/superpowers/plans/2026-07-14-twelve-week-runway-replacement.md`

**Interfaces:**
- Consumes: completed private production and KB receipt status.
- Produces: a ready Explainer Audiobooks PR containing process documentation only, with no private media or manuscript artifacts.

- [ ] **Step 1: Confirm the public diff contains no private artifacts**

  Run:

  ```bash
  git status --short --branch
  git diff --name-only origin/main...HEAD
  git diff --check origin/main...HEAD
  git ls-files '.build/**'
  ```

  Expected: the diff contains only the design and implementation-plan documents; `.build` returns no tracked private files.

- [ ] **Step 2: Push and open a ready PR to `main`**

  Push `codex/twelve-week-runway`, open a normal ready-for-review PR to `main`, and describe the title-collision correction, privacy boundary, and governed replacement design. Do not attach private manuscript, source notes, covers, or audio.

- [ ] **Step 3: Check hosted state and final worktree cleanliness**

  Verify GitHub reports the PR open and mergeable and inspect any hosted checks. Run `git status --short --branch` in the Explainer Audiobooks worktree, Echo checkout, and KB worktree. Report exact remaining dirty state and preserve unrelated user changes.
