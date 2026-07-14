# The Question Machine: New Learning Edition Production Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Research, write, review, narrate, verify, and privately deliver the approved 40,000–45,000-word New Learning Edition.

**Architecture:** Use one sequential frontier-author manuscript over a deep primary-source fact pack. Maintain prospective learning records and continuity after every chapter, run independent final-hash learning and prose gates, then produce user-selected paired covers and governed Echo artifacts. Private content remains under the ignored run root.

**Tech Stack:** Markdown, JSON receipts, primary-source web research, repository Python tooling, image generation, EPUB, Echo/Kokoro `am_michael`, FFmpeg, iCloud Drive.

## Global Constraints

- Narrated target: 40,000–45,000 words; no post-draft reduction without explicit user approval.
- Audience: curious beginner; light arithmetic; no calculus, programming, or code prerequisite.
- Curriculum: approved mechanism-first spiral, fourteen narrated chapters, and a non-narrated sources appendix.
- One frontier author owns canonical prose and substantive revision.
- Private artifacts never enter Git or the public KB.
- Learning and prose receipts must bind the same final chapter hashes.
- Unbounded Echo rendering requires accepted human evidence for every planned pronunciation term.
- Deliver a verified private iCloud Books copy; public publication is not authorized.

## Private paths

```bash
export EXPLAINER_ROOT=/Users/dfakkeldy/.codex/worktrees/question-machine-learning-edition-design
export RUN_ROOT="$EXPLAINER_ROOT/.build/custom-learning-audiobooks/the-question-machine-new-learning-edition"
export DIST="$RUN_ROOT/dist"
export SLUG=the-question-machine-new-learning-edition
```

---

### Task 1: Bootstrap prospective evidence and record approval

**Files:**
- Create privately: `$RUN_ROOT/research/{brief.md,learning-brief.json,learning-outline.json,chapter-plans.json,coverage-ledger.json,pronunciation-plan.json,sources.md}`
- Create privately: `$RUN_ROOT/{chapters,dist,cover-candidates}/`

**Interfaces:**
- Consumes: approved design commit `176c8b0` and the user's recorded approvals.
- Produces: authorized evidence for research and sequential drafting.

- [ ] **Step 1: Create the ignored run structure and copy templates**

```bash
mkdir -p "$RUN_ROOT"/{research,chapters,dist,cover-candidates}
cp "$EXPLAINER_ROOT"/skill/templates/learning-design/*.json "$RUN_ROOT/research/"
```

- [ ] **Step 2: Populate the approved learning brief and outline**

Record `originalTargetWords: 40000`, `currentTargetWords: 40000`, `minimumAcceptedWords: 40000`, `maximumAcceptedWords: 45000`, `draftingStarted: false`, and empty scope history. Record beginner prior knowledge, opening context/promise/route, `mechanism-first-spiral`, its fit evidence, three approved throughlines, fourteen chapter files/purposes/prerequisites, and conversation/design-commit approval evidence.

- [ ] **Step 3: Populate chapter plans and complete concept paths**

Every chapter receives purpose, prerequisites, knowledge delta, grounded example, concepts, and at least three varied beats. Every core concept receives definition, reason, mechanism, concrete case, boundary, misconception, expected ability, and chapter uses before its first chapter is drafted.

- [ ] **Step 4: Create and validate the pronunciation plan**

Include `hyperparameter`, `hyperparameters`, `inference`, `gradient`, `gradients`, `backpropagation`, `logit`, `logits`, `softmax`, `autoregression`, `autoregressive`, and `quantization`. Mark the first two `source: listener`, map exact chapters, then run:

```bash
/usr/local/bin/python3 "$EXPLAINER_ROOT/skill/scripts/pronunciation_plan_qc.py" \
  --run-root "$RUN_ROOT" --phase planning
git status --short --branch
```

Expected: planning passes; all private paths remain ignored.

### Task 2: Deep primary-source research

**Files:**
- Create privately: `$RUN_ROOT/research/{fact-pack.md,uncertainties.md}`
- Update privately: `$RUN_ROOT/research/sources.md`

- [ ] **Step 1: Build a live source map**

Use primary sources for neural networks, backpropagation, generalization, word representations, attention/transformers, language-model training/scaling, instruction/preference tuning, retrieval/tools/agents, evaluation/calibration, hallucination, interpretability, and the final consciousness/risk boundaries. Record title, organization/authors, publication date, retrieval date, source class, URL, and supported chapters.

- [ ] **Step 2: Extract claim-level evidence and uncertainty**

Distinguish foundational mechanism from current implementation practice. Date changing claims and record disputes. Prior fact packs are leads only; recheck every reused claim.

- [ ] **Step 3: Reconcile evidence with the coverage ledger**

Each mechanism and boundary needs adequate support. Remove unsupported scope instead of filling gaps from model memory.

### Task 3: Sequentially draft Part I

**Files:**
- Create privately: `$RUN_ROOT/chapters/ch01.md` through `ch06.md`
- Create/update privately: `$RUN_ROOT/research/{continuity.json,continuity.md}`

- [ ] **Step 1: Mark drafting started without changing targets**

Set `learning-brief.json.draftingStarted` to `true` before canonical prose exists.

- [ ] **Step 2: Draft Chapters 1–6 in order with one frontier author**

Before each chapter, load the approved outline, chapter plan, fact pack, affected coverage rows, and latest continuity checkpoint. Stay within each approved chapter range. Do not draft chapters concurrently.

- [ ] **Step 3: Append continuity before beginning the next chapter**

Record `afterChapter`, `termsDefined`, `examplesUsed`, `callbacks`, `promises`, and `unresolvedQuestions` immediately after each chapter.

- [ ] **Step 4: Run the non-final Part I diagnostic**

```bash
/usr/local/bin/python3 "$EXPLAINER_ROOT/skill/scripts/prose_qc.py" \
  --chapters-dir "$RUN_ROOT/chapters" \
  --out "$RUN_ROOT/research/prose-qc-part1.md"
```

Verify that Chapter 1 supplies context/promise/route and that the email network is calculable using arithmetic alone. Do not issue final receipts.

### Task 4: Sequentially draft Parts II and III

**Files:**
- Create privately: `$RUN_ROOT/chapters/ch07.md` through `ch14.md`
- Create privately: `$RUN_ROOT/chapters/ch15-sources.md`
- Update privately: continuity records.

- [ ] **Step 1: Draft Chapters 7–11 sequentially**

Carry the fixed/changing/result throughline through tokens, embeddings, attention, transformer blocks, pretraining, and repeated inference. Include the approved worked attention case without a visual dependency.

- [ ] **Step 2: Draft Chapters 12–14 sequentially**

Separate model from product in Chapter 12, evaluate failure/evidence in Chapter 13, and keep consciousness, agency, moral status, and risk to the grounded compact closing.

- [ ] **Step 3: Write the non-narrated sources appendix**

Map sources by chapter. Keep citation apparatus out of spoken prose unless needed for comprehension.

- [ ] **Step 4: Verify range without changing the target**

```bash
find "$RUN_ROOT/chapters" -name 'ch*.md' ! -name '*sources*' -print0 | xargs -0 wc -w
```

Expected: 40,000–45,000 narrated words. If short, deepen incomplete explanation paths; never lower the approved range.

### Task 5: Independent learning review and repair

**Files:**
- Create privately: `$RUN_ROOT/research/{learning-review.json,structure-review.md,beginner-reader-review.md}`
- Modify privately: canonical chapters for accepted repairs.

- [ ] **Step 1: Run the structure review**

Record citation-first findings for orientation, progression, prerequisites, throughlines, callbacks, and resolved promises. The reviewer does not write replacement prose.

- [ ] **Step 2: Run the beginner-reader review**

Inventory unexplained terms, conceptual leaps, shallow mechanisms, absent examples, misleading analogies, misconceptions, boundaries, and implausible expected abilities with exact locations.

- [ ] **Step 3: Frontier-author repair and rerun**

Record accepted/rejected/resolved decisions and reasons. Apply accepted repairs only in canonical Markdown. Rerun both lanes to provisional pass, but defer final hashes until humanizing is complete.

### Task 6: Humanizer, de-Claudification, and final-hash review

**Files:**
- Create privately: `$RUN_ROOT/research/{humanizer-decisions.json,prose-qc.md,prose-style-receipt.json,learning-design-receipt.json}`
- Modify privately: accepted local voice repairs.

- [ ] **Step 1: Run the phrase-family inventory**

```bash
/usr/local/bin/python3 "$EXPLAINER_ROOT/skill/scripts/prose_qc.py" \
  --chapters-dir "$RUN_ROOT/chapters" \
  --out "$RUN_ROOT/research/prose-qc.md"
```

- [ ] **Step 2: Apply only accepted patch-sized humanizer edits**

Preserve facts, definitions, examples, technical terms, teaching order, retrieval, and uncertainty. Record location, original, proposal, decision, and reason. Treat the listener's named Claude-style rhetorical families as hard bans.

- [ ] **Step 3: Generate the final prose receipt**

Use the exact `declaudification.md` command with `--fail-on-style`, decisions, and final chapter hashes.

- [ ] **Step 4: Rerun both learning reviews on final hashes**

Set distinct passing reviewer identities and `reviewedChapterSHA256` only after all accepted voice edits.

- [ ] **Step 5: Generate the learning receipt**

```bash
/usr/local/bin/python3 "$EXPLAINER_ROOT/skill/scripts/learning_design_qc.py" \
  --run-root "$RUN_ROOT" \
  --receipt-out "$RUN_ROOT/research/learning-design-receipt.json"
```

Expected: PASS within 40,000–45,000 words; learning and prose receipts bind identical chapter hashes.

### Task 7: Three paired cover directions and user selection

**Files:**
- Create privately: `$RUN_ROOT/cover-candidates/candidate-{1,2,3}/` with art, specs, renders, thumbnails, and receipts.

- [ ] **Step 1: Write three distinct art-and-type briefs**

Retain the amber series identity while varying metaphor, composition, palette, material language, and title strategy. Include at least one high-key direction.

- [ ] **Step 2: Generate raster art and render all coordinated pairs**

Use original text-free image generation, then `render_cover_pair(...)` for 1600×2560 portrait and 2400×2400 square outputs.

- [ ] **Step 3: Inspect full-size renders and thumbnails**

Reject generic, artifacted, unreadable, or poorly coordinated candidates before presentation.

- [ ] **Step 4: Pause for explicit user selection**

Do not create `cover-selection.json` or package the book until the user selects a pair or requests a mix.

### Task 8: Governed EPUB and Markdown build

**Files:**
- Create privately: `$DIST/{cover-selection.json,$SLUG.epub,$SLUG.md}`

- [ ] **Step 1: Create the paired selection receipt**

Run `cover_receipts.py select-pair` against the selected candidate with private classification and user selection evidence. Create a stable `$RUN_ROOT/cover-candidates/selected` symlink only after receipt verification.

- [ ] **Step 2: Build with both final receipts**

```bash
/usr/local/bin/python3 "$EXPLAINER_ROOT/skill/scripts/build_book.py" \
  --chapters-dir "$RUN_ROOT/chapters" --out-dir "$DIST" \
  --title "The Question Machine" --subtitle "New Learning Edition" \
  --author "Dan Fakkeldy" --contributor "GPT-5 Codex" --slug "$SLUG" \
  --cover "$RUN_ROOT/cover-candidates/selected/cover.png" \
  --m4b-cover "$RUN_ROOT/cover-candidates/selected/m4b-cover.png" \
  --cover-selection "$DIST/cover-selection.json" \
  --learning-receipt "$RUN_ROOT/research/learning-design-receipt.json" \
  --prose-receipt "$RUN_ROOT/research/prose-style-receipt.json"
```

Expected: EPUB and Markdown exist; both receipts verify against packaged chapter hashes.

### Task 9: Partial Echo render and pronunciation approval

**Files:**
- Create privately: governed partial captures/anchors.
- Create privately: `$DIST/$SLUG-pronunciation-probe.m4b`
- Create privately: `$RUN_ROOT/research/pronunciation-probe-evidence.json`
- Update privately: pronunciation plan decisions.

- [ ] **Step 1: Export governed Echo inputs**

Set `EXPLAINER_ROOT`, `RUN_ROOT`, `DIST`, `SLUG`, `TITLE`, selected covers, `VOICE=am_michael`, `PRONUNCIATION_PLAN`, and a reviewed clean live Echo `HEAD` as `APPROVED_ECHO_PRONUNCIATION_SHA`.

- [ ] **Step 2: Render one new chapter at a time**

Call the public wrapper with `--max-chapters 1`, then `--resume --max-chapters 1`, requiring exit 2 and sealed state each time. Continue through the latest chapter containing a required planned term.

- [ ] **Step 3: Build the technical-term reel**

```bash
/usr/local/bin/python3 "$EXPLAINER_ROOT/skill/scripts/build_pronunciation_probe_reel.py" \
  --run-root "$RUN_ROOT" --work-dir "$WORK" \
  --out "$DIST/$SLUG-pronunciation-probe.m4b" \
  --evidence-out "$RUN_ROOT/research/pronunciation-probe-evidence.json"
```

- [ ] **Step 4: Pause for human listening decisions**

The user explicitly accepts or rejects every required term, including both forms of `hyperparameter`. Record decisions and evidence hashes. Repair Echo pronunciation inputs and rerender affected captures for any rejection.

- [ ] **Step 5: Generate the accepted pronunciation receipt**

```bash
/usr/local/bin/python3 "$EXPLAINER_ROOT/skill/scripts/pronunciation_plan_qc.py" \
  --run-root "$RUN_ROOT" --phase full-render \
  --receipt-out "$RUN_ROOT/research/pronunciation-plan-receipt.json"
```

Expected: PASS only after every required term has accepted human evidence.

### Task 10: Complete Echo render, verify, and privately deliver

**Files:**
- Create privately: accepted M4B, alignment, audit, Echo reel when emitted, success receipts, selector, and manifest.
- Copy privately: verified package to iCloud Books.

- [ ] **Step 1: Resume without a chapter bound**

```bash
"$EXPLAINER_ROOT/skills/custom-learning-audiobook/scripts/echo_pronunciation_narrate.sh" --resume
```

Expected: zero exit, success receipt, accepted selector, and non-empty M4B/sidecar/audit.

- [ ] **Step 2: Run complete selector-bound QC**

Follow `package-and-qc.md`: verify attempt/success/selector chain, pronunciation audit, watch counts, sidecar, duration, EPUB, cover hashes, and paired binding. Never mutate the accepted M4B.

- [ ] **Step 3: Write the private manifest**

Record word count, runtime, voice, research confidence, model roles, exact skill revision, every receipt/hash, human pronunciation status, human full-listen status `pending`, and private classification.

- [ ] **Step 4: Dry-run and apply iCloud sync**

Use `sync_selected_cover.py`, preserve earlier editions, inspect destination classification, and apply only after the dry run is correct.

- [ ] **Step 5: Verify actual destination bytes**

Repeat checksum, receipt, EPUB, M4B, sidecar, audit, and cover checks against the copied files. Report human first-listen acceptance as pending.

### Task 11: After-action skill audit and durable receipts

**Files:**
- Modify public skill files only for reusable gaps proven by the run.
- Update private after-action records.
- Update public-safe business KB project/topic/log pages.

- [ ] **Step 1: Compare design, evidence, and delivered output**

Check every promise and failure condition. Separate reusable workflow defects from book-specific editorial choices.

- [ ] **Step 2: Repair proven reusable gaps with TDD**

Follow the linked repeatable-workflow plan. Do not add speculative Humanizer bans or private examples.

- [ ] **Step 3: Publish and verify the ready skill PR**

Report exact head SHA, PR URL, hosted checks, and installed-path parity.

- [ ] **Step 4: File the public-safe KB receipt**

Record private delivery status, exact skill revision, objective QC, and pending human first-listen status without copying private content. Lint, commit, push, open the Tier-1 KB PR, and confirm auto-merge.

- [ ] **Step 5: Final hygiene**

Run `git status --short --branch` in every touched repo/worktree. All public changes must be committed/pushed/PR-backed; all private artifacts remain ignored.
