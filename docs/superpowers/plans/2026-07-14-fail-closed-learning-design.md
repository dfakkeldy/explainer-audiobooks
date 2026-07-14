# Fail-Closed Learning Design Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent new audiobook packages from treating style, factual, or media checks as evidence that a manuscript has a coherent and independently reviewed learning design.

**Architecture:** Add one shared structured learning-design contract and a Python validator that emits a receipt bound to the final chapter hashes. Extend the EPUB builder to require that receipt for current CLI builds, while retaining an explicit legacy-reproduction escape hatch. Update all production and development skills so planning, review, prose, and media verdicts remain separate.

**Tech Stack:** Python 3 standard library, `unittest`, Markdown skill contracts, JSON receipts, SHA-256.

## Global Constraints

- Do not rewrite or repackage *The Question Machine* in this change.
- Do not allow a passing prose receipt to satisfy the learning-design gate.
- Require explicit user approval or explicit autonomous-run authorization before canonical drafting.
- Require explicit learner approval for any target reduction after drafting starts.
- Bind structural and beginner-reader verdicts to the final canonical chapter hashes.
- Keep the humanizer bounded to local voice edits; it cannot certify pedagogy.
- Preserve private/generated book artifacts and unrelated worktree changes.

---

### Task 1: Structured learning-design validator

**Files:**
- Create: `tests/test_learning_design_gate.py`
- Create: `skill/scripts/learning_design_qc.py`

**Interfaces:**
- Consumes: a run root containing `chapters/chNN.md` and the six structured JSON records named in the design specification.
- Produces: `validate_run(run_root: Path) -> dict[str, object]`, `write_receipt(run_root: Path, output: Path) -> dict[str, object]`, and `verify_learning_receipt(chapters_dir: Path, receipt_path: Path) -> dict[str, object]`.

- [ ] **Step 1: Write failing validator tests**

Create fixtures for two chapters and valid records. Assert that a valid run emits
`schemaVersion == 1`, `status == "pass"`, and exact chapter hashes. Add one test
per failure family: missing orientation; missing approval; unapproved target
reduction; missing chapter plan; incomplete explanation stack; missing continuity
checkpoint; failing or stale structural/beginner review; unresolved accepted
finding.

- [ ] **Step 2: Run tests and verify RED**

Run: `python3 -m unittest tests.test_learning_design_gate -v`

Expected: import failure because `learning_design_qc.py` does not exist.

- [ ] **Step 3: Implement the minimal validator**

Use only the standard library. Require these exact files:

```python
REQUIRED_RECORDS = {
    "brief": "learning-brief.json",
    "outline": "learning-outline.json",
    "plans": "chapter-plans.json",
    "coverage": "coverage-ledger.json",
    "continuity": "continuity.json",
    "review": "learning-review.json",
}
```

Validate non-empty strings with a shared `require_string`, non-empty lists with
`require_list`, and chapter identity with sorted `ch*.md` filenames. Hash every
source record and chapter with SHA-256. Require:

```python
brief["learnerOutcome"]
brief["priorKnowledge"]
brief["openingOrientation"]
brief["originalTargetWords"] > 0
brief["currentTargetWords"] > 0
outline["authorization"]["status"] == "approved"
outline["authorization"]["source"] in {"user", "explicit-autonomous-run"}
2 <= len(outline["throughlines"]) <= 4
```

For a reduced target after drafting, require a matching scope-history entry with
old/new values, reason, `approved == true`, `approvalSource == "user"`, and
non-empty evidence. Require exactly one plan and continuity entry per chapter.
Require every concept to have definition, reason, mechanism, concrete case,
misconception, expected ability, chapter uses, and either a useful boundary or a
non-empty boundary-not-applicable reason. Require `structure` and `beginnerReader`
review verdicts of `pass`, final chapter hashes, and no finding whose decision is
`unresolved`.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run: `python3 -m unittest tests.test_learning_design_gate -v`

Expected: all learning-design tests pass.

- [ ] **Step 5: Commit**

```bash
git add tests/test_learning_design_gate.py skill/scripts/learning_design_qc.py
git commit -m "feat: add hash-bound audiobook learning gate"
```

### Task 2: EPUB packaging enforcement

**Files:**
- Modify: `tests/test_learning_design_gate.py`
- Modify: `skill/scripts/build_book.py`

**Interfaces:**
- Consumes: `--learning-receipt <path>` for current CLI builds.
- Produces: builder verification before any output directory is created; `--legacy-without-learning-receipt` only for reproducing old artifacts.

- [ ] **Step 1: Write failing builder tests**

Assert that `build_book.build` exposes `learning_receipt`; a stale receipt fails
before output; CLI invocation without either learning receipt or legacy flag
returns non-zero; CLI with a valid learning receipt succeeds; and the legacy flag
cannot be combined with a receipt.

- [ ] **Step 2: Run tests and verify RED**

Run: `python3 -m unittest tests.test_learning_design_gate -v`

Expected: failures for the missing parameter and CLI gate.

- [ ] **Step 3: Implement builder verification**

Import `verify_learning_receipt`. Add `learning_receipt=None` to `build(...)` and
verify it before style or cover receipts. Add CLI arguments:

```python
gate = ap.add_mutually_exclusive_group()
gate.add_argument("--learning-receipt")
gate.add_argument("--legacy-without-learning-receipt", action="store_true")
```

After parsing, call `ap.error(...)` when neither is present. Pass
`a.learning_receipt` into `build(...)`. Name the escape hatch loudly and describe
it as old-artifact reproduction only.

- [ ] **Step 4: Run focused builder and existing receipt tests**

Run:
`python3 -m unittest tests.test_learning_design_gate tests.test_prose_style_gate tests.test_build_book_cover_receipt -v`

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add tests/test_learning_design_gate.py skill/scripts/build_book.py
git commit -m "feat: require learning receipt for current book builds"
```

### Task 3: Shared learning contract and audiobook skill integration

**Files:**
- Create: `tests/test_skill_learning_contract.py`
- Create: `skill/references/learning-design.md`
- Modify: `skill/SKILL.md`
- Modify: `skills/custom-learning-audiobook/SKILL.md`
- Modify: `skills/custom-learning-audiobook/references/intake-and-research.md`
- Modify: `skills/custom-learning-audiobook/references/package-and-qc.md`
- Modify: `skill/references/frontier-manuscript-pipeline.md`
- Modify: `skill/references/narration-style.md`

**Interfaces:**
- Consumes: the structured record names and validator command from Task 1.
- Produces: identical fail-closed learning requirements and build flags in both production skills.

- [ ] **Step 1: Write failing contract tests**

Assert that the shared reference names all six records, separates five verdict
lanes, forbids retroactive normalization, requires a full opening orientation,
and includes the validator command. Assert that both production skills read the
reference, run `learning_design_qc.py`, pass `--learning-receipt`, pass
`--prose-receipt`, and forbid the legacy escape hatch for new/revised books.

- [ ] **Step 2: Run tests and verify RED**

Run: `python3 -m unittest tests.test_skill_learning_contract -v`

Expected: failures for the missing reference and commands.

- [ ] **Step 3: Write the shared contract**

Define the five independent verdicts, exact record fields, workflow order,
review format, and command:

```bash
python3 skill/scripts/learning_design_qc.py \
  --run-root "$RUN_ROOT" \
  --receipt-out "$RUN_ROOT/research/learning-design-receipt.json"
```

State that records must be maintained during planning/drafting and cannot be
reconstructed after a failed draft merely to unlock packaging.

- [ ] **Step 4: Integrate production and supporting references**

Make the explainer and custom skills require orientation, structured chapter
plans, full explanation paths, continuity checkpoints, two independent review
verdicts, and the receipt before humanization/packaging. Add both receipt flags
to every current `build_book.py` command. Keep prose and learning receipts
separate. Update intake, frontier-author, narration, and package references to
use the same record names and command.

- [ ] **Step 5: Run contract and focused script tests**

Run:
`python3 -m unittest tests.test_skill_learning_contract tests.test_skill_prose_contract tests.test_learning_design_gate -v`

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add tests/test_skill_learning_contract.py skill skills/custom-learning-audiobook
git commit -m "feat: make audiobook learning design fail closed"
```

### Task 4: Longform handoff and humanizer boundary

**Files:**
- Modify: `tests/test_skill_learning_contract.py`
- Modify: `skills/longform-book-development/SKILL.md`
- Modify: `skills/longform-book-development/references/handoff-packet.md`
- Modify: `skill/references/humanizer-pass.md`
- Modify outside this repository: `/Users/dfakkeldy/.codex/skills/humanizer/SKILL.md`

**Interfaces:**
- Consumes: the shared learning-design record contract.
- Produces: a production-ready handoff with the learner starting state and teaching architecture, plus a humanizer that reports structural blockers without smoothing them.

- [ ] **Step 1: Extend failing contract tests**

Require the longform skill and handoff template to include opening orientation,
prior knowledge, target history, chapter prerequisites, knowledge deltas,
explanation stacks, approval evidence, and the “development draft” blocker.
Require the humanizer reference to state that it cannot certify pedagogy and must
return structural defects to learning review.

- [ ] **Step 2: Run tests and verify RED**

Run: `python3 -m unittest tests.test_skill_learning_contract -v`

Expected: failures for missing handoff and humanizer-boundary language.

- [ ] **Step 3: Update the longform contract**

Make the handoff completion criteria depend on approved learner orientation,
chapter progression, prerequisites, knowledge deltas, teaching beats,
throughlines, concept explanation paths, and target-change history. State that a
packet missing any of these stays in development and cannot start canonical
production.

- [ ] **Step 4: Update canonical and installed humanizer guidance**

Add a precondition before local style work: missing context, chapter-order
problems, unexplained terms, shallow mechanisms, or absent worked examples are
structural blockers. The humanizer records them and stops; it does not rearrange,
expand, or cosmetically smooth the manuscript and cannot issue whole-book or
pedagogical acceptance.

- [ ] **Step 5: Run contract tests and verify installed parity**

Run:
`python3 -m unittest tests.test_skill_learning_contract tests.test_skill_prose_contract -v`

Then compare the installed humanizer boundary with
`skill/references/humanizer-pass.md` using focused `rg` checks.

- [ ] **Step 6: Commit repository changes**

```bash
git add tests/test_skill_learning_contract.py skills/longform-book-development skill/references/humanizer-pass.md
git commit -m "docs: separate humanizing from learning acceptance"
```

### Task 5: Full verification, publication, and durable receipt

**Files:**
- Modify only if validation exposes a defect: files from Tasks 1-4.
- Update in a clean KB worktree: `bundle/projects/explainer-audiobooks.md`, `bundle/questions/audiobook-prose-declaudification.md`, and `bundle/log.md`.

**Interfaces:**
- Consumes: the completed implementation and exact Git SHA.
- Produces: ready Explainer Audiobooks PR with hosted status and a merged Tier-1 KB receipt.

- [ ] **Step 1: Run repository validation**

```bash
python3 -m unittest discover -s tests -v
python3 tools/validate_skills.py
python3 tools/validate_custom_learning_skill_install.py
git diff --check
```

Expected: all applicable checks pass; any environment-only installed-skill
warning is reported precisely rather than hidden.

- [ ] **Step 2: Review the final diff and repository state**

Run `git diff origin/main...HEAD --check`, inspect `git diff --stat`, and confirm
that only the design, plan, tests, validator, builder, and named skill/reference
files changed.

- [ ] **Step 3: Commit any final verification fixes**

Use a focused Conventional Commit message and stage only agent-authored files.

- [ ] **Step 4: Push and open a ready PR against `main`**

This repository has no `nightly` or `weekly` branches, so push the feature branch
and open the PR explicitly against `main`. Report the PR URL and exact head SHA.

- [ ] **Step 5: Check hosted CI**

Wait for required checks. Inspect concrete job logs and repair any failure before
claiming completion.

- [ ] **Step 6: File the KB receipt**

Record that the skill repair is implemented and under review or merged, cite the
PR and exact SHA, distinguish local tests from hosted CI, and state explicitly
that *The Question Machine* was not rewritten. Run `python3 tools/kb_lint.py`,
commit, push, and verify the Tier-1 PR auto-merges.
