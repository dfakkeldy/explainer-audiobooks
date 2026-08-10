# Documentation Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring the public documentation and book catalog into agreement with the workflows and published artifacts on `main` as of 2026-08-09.

**Architecture:** Treat current guides, the catalog, historical evidence, and the `docs/` landing page as separate documentation roles. Rewrite only current guidance and status summaries; preserve dated evidence in place with explicit superseded banners.

**Tech Stack:** Markdown, Git, repository Python validation tools

## Global Constraints

- Do not change audiobook artifacts, receipts, hashes, manuscript text, cover art, or production tooling.
- Do not rewrite historical handoff or checklist evidence below their new superseded banners.
- Do not describe listening-pending packages as having completed human acceptance.
- Preserve unrelated work in the canonical checkout.

---

### Task 1: Refresh the public catalog and project summary

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: finished package metadata in `books/*/README.md` and the current workflow contract in `skill/SKILL.md`
- Produces: the repository's public catalog and short workflow overview

- [x] **Step 1: Update the project description**

Replace code-only language with a grounded-learning description that covers technical, practical, civic, and reflective books without claiming every title is based on a codebase.

- [x] **Step 2: Reconcile the collection table**

Add these finished public packages with their repository-recorded status and runtime:

```text
Beyond the Tax-Sale Packet — 13 chapters, ~4.2 h, Codex (GPT-5)
Gold Panning in Nova Scotia — 10 chapters, ~2.0 h, GLM-5.2
The Case Against Me — 9 chapters, ~1.9 h, Claude Opus 5
```

Do not add `everything-but-the-code`, because it is an artifact-only directory without a public package README. Do not add *The Best Job You Can Get From Here* to the finished table, because its README identifies it as version 0 requiring review.

- [x] **Step 3: Replace the obsolete development entry**

Remove the claim that *Beyond the Tax-Sale Packet* is an unfinished 12-chapter, 38-figure packet. Add *The Best Job You Can Get From Here* as the current public-safe development draft and preserve its not-publication-ready boundary.

- [x] **Step 4: Align the short workflow**

Describe the five-question nonfiction intake, argument-level outline, story ledger, fact packs, sequential frontier authorship, road-book re-entry/checkpoints, five revision passes, blind beginner review, and the distinct private/public cover lanes.

- [x] **Step 5: Review catalog claims against package READMEs**

Run:

```bash
rg -n "Edition|Status|Chapters|Runtime|listening|permission" \
  books/beyond-the-tax-sale-packet/README.md \
  books/gold-panning-nova-scotia/README.md \
  books/the-case-against-me/README.md \
  books/the-best-job-you-can-get-from-here/README.md
```

Expected: every new README claim has a corresponding source line and no unfinished package is described as final.

### Task 2: Refresh the current how-to and method guides

**Files:**
- Modify: `docs/make-your-own.md`
- Modify: `docs/how-these-were-made.md`

**Interfaces:**
- Consumes: `skill/SKILL.md`, `skills/longform-book-development/SKILL.md`, `skills/fiction-book-development/SKILL.md`, and `skills/fiction-audiobook/SKILL.md`
- Produces: current public setup, routing, production-method, and publication guidance

- [x] **Step 1: Rewrite setup and routing in `make-your-own.md`**

State that the repository checkout must remain available, `/usr/local/bin/python3` with Pillow is the current interpreter contract, paired covers are mandatory, and missing rendering dependencies are setup failures rather than a reason to skip the cover. Keep the Claude Code symlink example, then route users among:

```text
audiobook — direct grounded nonfiction production
longform-book-development — multi-session nonfiction development
fiction-book-development — fiction manuscript development
fiction-audiobook — complete fiction listening packages
```

- [x] **Step 2: Update the nonfiction request flow**

List the exact five intake topics from `skill/SKILL.md`, explain the complete-handoff exception, and summarize the current research, drafting, five-pass revision, blind beginner review, packaging, narration, and delivery behavior.

- [x] **Step 3: Replace retired method language in `how-these-were-made.md`**

Replace the concept-coverage-ledger description with the current question-led argument outline, durable outcomes, throughlines, story ledger, per-chapter fact packs, and continuity note.

- [x] **Step 4: Add current listening and revision contracts**

Explain drift-and-re-entry section openings, situation-choice-consequence examples, spoken `Key points` checkpoints, the five named revision passes, blind beginner review, prose QC, and the bounded humanizer pass.

- [x] **Step 5: Correct private/public assembly behavior**

State that ordinary private books auto-select the strongest of three cover pairs and remain receipt-free for the user. State separately that public promotion requires explicit authorization, a valid pair-selection record, immutable re-narration when the square changes, package verification, and governed sync.

### Task 3: Add navigation and reconcile tax-sale status

**Files:**
- Create: `docs/README.md`
- Modify: `docs/nova-scotia-tax-sale-book/README.md`
- Modify: `docs/nova-scotia-tax-sale-book/handoff-packet.md`
- Modify: `docs/nova-scotia-tax-sale-book/audiobook-acceptance-checklist.md`
- Modify: `docs/superpowers/plans/2026-07-11-public-cover-refresh.md`

**Interfaces:**
- Consumes: `docs/nova-scotia-tax-sale-book/research/audiobook-54-figure-publication-receipt.json`
- Produces: a navigable `docs/` landing page, a current tax-sale status summary, and clearly labelled historical records

- [x] **Step 1: Add `docs/README.md`**

Create four clearly separated groups:

```text
Current guides
Current development packets
Dated operational evidence
Historical plans and specifications
```

Explain that dated cover/audio folders and `docs/superpowers/` are evidence and design history, not current setup instructions.

- [x] **Step 2: Reconcile the tax-sale README**

Keep the governed-final opening. Change the intended-future wording to identify the finished public book, state that all 54 figures are embedded in the public EPUB, and replace the internally contradictory production-gate chronology with a concise current-status section plus a clearly labelled historical timeline.

- [x] **Step 3: Mark the handoff packet as superseded**

Insert this meaning directly below the title without changing later evidence:

```text
Historical record — superseded. This handoff captures the pre-publication state on 2026-07-20. The governed-final 54-figure edition was later published and accepted; see the packet README and final publication receipt for current status.
```

- [x] **Step 4: Mark the acceptance checklist as superseded**

Insert an equivalent banner identifying it as the 2026-07-22 replacement-candidate gate and linking to the governed-final publication receipt. Leave every checkbox and pending-status statement unchanged as historical evidence.

- [x] **Step 5: Repair the historical plan link**

Change the broken link target from:

```text
../../docs/cover-refresh-2026-07/manifest.md
```

to:

```text
../../cover-refresh-2026-07/manifest.md
```

### Task 4: Verify the complete documentation refresh

**Files:**
- Verify: `README.md`
- Verify: `docs/**/*.md`

**Interfaces:**
- Consumes: all edits from Tasks 1–3
- Produces: validation evidence suitable for commit and pull-request handoff

- [x] **Step 1: Check all local Markdown links**

Run the repository-root link scanner over `README.md` and every Markdown file under `docs/`. Expected: `missing_local_targets=0`.

- [x] **Step 2: Run repository validation**

Run the focused skill and publishing contracts plus the skill validator. The
full suite includes renderer-install tests that invoke an Apple build and must
not be started outside the repository's admitted build window for an
instruction-only change.

```bash
/usr/local/bin/python3 -m unittest \
  tests.test_audiobook_skill_contract \
  tests.test_audiobook_longform_handoff_contract \
  tests.test_fiction_book_development_contract \
  tests.test_fiction_audiobook_integration \
  tests.test_publishing_reference \
  tests.test_publishing_public_path -v
/usr/local/bin/python3 tools/validate_skills.py
```

Expected: 31 tests pass and `validate_skills: clean`.

- [x] **Step 3: Check formatting and scope**

Run:

```bash
git diff --check
git status --short --branch
git diff --stat origin/main...HEAD
git diff origin/main...HEAD -- README.md docs/
```

Expected: no whitespace errors; only the approved documentation files, design, and implementation plan are changed.

- [x] **Step 4: Commit and publish**

Stage only the approved paths, commit the implementation, push `codex/refresh-documentation`, and open one ready pull request against `main` using the repository's GitHub workflow.
