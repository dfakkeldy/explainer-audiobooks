# Unattended First-Listen Book Production Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make overnight and ready-to-listen requests complete as private first-listen audiobook packages without routine user approval pauses.

**Architecture:** Add one shared unattended-production contract consumed by all book skills, then teach the existing learning, pronunciation, and cover receipt validators a second honest assurance level. Legacy records remain governed-final by default; unattended receipts are packageable but keep human listening pending and cannot authorize publication.

**Tech Stack:** Markdown skills and references, Python 3 standard library validators, `unittest`, native Echo/Kokoro wrapper contracts.

## Global Constraints

- Never auto-publish or infer permission to publish.
- Keep private/generated book artifacts out of the public repository and public KB.
- Preserve `governed-final` behavior for records that omit the new production-mode fields.
- An unattended receipt must state that human listening is pending and that a later negative verdict overrides it.
- Native Echo/Kokoro remains the complete-package renderer; do not substitute a system voice silently.
- Use one frontier author for canonical prose and retain every existing non-human learning, prose, research, and media gate.

---

### Task 1: Shared unattended-production contract

**Files:**
- Create: `skill/references/unattended-production.md`
- Modify: `skill/SKILL.md`
- Modify: `skills/custom-learning-audiobook/SKILL.md`
- Modify: `skills/custom-learning-audiobook/references/intake-and-research.md`
- Modify: `skills/custom-learning-audiobook/references/package-and-qc.md`
- Modify: `skills/longform-book-development/SKILL.md`
- Modify: `skills/fiction-book-development/SKILL.md`
- Test: `tests/test_skill_unattended_contract.py`

**Interfaces:**
- Consumes: user request language and existing skill routing.
- Produces: `productionMode.name`, `research/unattended-decisions.json`, mode-specific stop rules, batch completion rules, and promotion boundaries used by later tasks.

- [x] **Step 1: Write the failing contract tests**

  Add tests that require all four skills to reference `unattended-production.md`,
  require the shared reference to define `unattended-first-listen` and
  `governed-final`, assert that routine preferences use recorded defaults instead
  of questions, and require one package-or-blocker result per batch item.

- [x] **Step 2: Run the contract test and verify RED**

  Run: `python3 -m unittest tests.test_skill_unattended_contract -v`

  Expected: FAIL because the shared reference and skill markers do not exist.

- [x] **Step 3: Implement the minimal shared contract and skill routing**

  Define triggers, defaults, the assumptions-receipt schema, allowed blockers,
  first-listen proof wording, batch isolation, fiction handoff behavior, and
  governed-final promotion. Replace unconditional approval language with
  mode-specific behavior while retaining explicit publication and negative
  verdict gates.

- [x] **Step 4: Run the contract test and verify GREEN**

  Run: `python3 -m unittest tests.test_skill_unattended_contract -v`

  Expected: PASS.

### Task 2: Dual-assurance learning receipt

**Files:**
- Modify: `skill/scripts/learning_design_qc.py`
- Modify: `skill/references/learning-design.md`
- Test: `tests/test_learning_design_gate.py`

**Interfaces:**
- Consumes: optional `learning-brief.json.productionMode` and a hash-bound `research/unattended-decisions.json`.
- Produces: legacy `status: pass` receipts or `status: first-listen` receipts with `humanComprehensionPilot: pending` and `learningAuthority.holder: human-listener-pending`.

- [x] **Step 1: Write failing unattended learning tests**

  Extend the fixture with a helper that writes an unattended decisions receipt,
  switches outline authorization to `explicit-autonomous-run`, and converts the
  pilot checkpoints to editorial review. Assert that `validate_run` produces a
  first-listen receipt, `verify_learning_receipt` accepts it, a missing or stale
  assumptions hash fails, and governed road-book records still reject autonomous
  authorization.

- [x] **Step 2: Run focused tests and verify RED**

  Run: `python3 -m unittest tests.test_learning_design_gate.LearningDesignGateTests.test_unattended_first_listen_preserves_pending_human_authority -v`

  Expected: FAIL because the validator does not recognize the unattended mode.

- [x] **Step 3: Implement mode-aware validation**

  Parse the optional production mode, validate the bound decisions receipt,
  allow editorial outline/first-section/pilot continuation only in unattended
  mode, emit the honest pending-human receipt, and accept only the exact allowed
  pending gate when verifying it.

- [x] **Step 4: Run learning tests and verify GREEN**

  Run: `python3 -m unittest tests.test_learning_design_gate -v`

  Expected: PASS.

### Task 3: Unattended pronunciation evidence

**Files:**
- Modify: `skill/scripts/pronunciation_plan_qc.py`
- Modify: `skills/custom-learning-audiobook/references/package-and-qc.md`
- Test: `tests/test_pronunciation_plan_qc.py`
- Test: `tests/test_custom_learning_audiobook_echo_contract.py`

**Interfaces:**
- Consumes: optional `pronunciation-plan.json.assuranceLevel` with value `unattended-first-listen` and the existing governed reel evidence.
- Produces: `status: first-listen`, `humanListening: pending`, and full-render eligibility without fabricated human acceptance; governed-final remains unchanged.

- [x] **Step 1: Write failing pronunciation tests**

  Add a governed probe-evidence fixture without a human decision. Assert it can
  produce an unattended first-listen receipt, cannot claim `pass`, and does not
  weaken the existing governed-final failure.

- [x] **Step 2: Run focused tests and verify RED**

  Run: `python3 -m unittest tests.test_pronunciation_plan_qc -v`

  Expected: FAIL because required terms still demand accepted human evidence.

- [x] **Step 3: Implement assurance-aware pronunciation validation**

  Require `probed` terms and complete hash-bound clip/reel evidence for
  unattended mode, omit fabricated acceptance fields, and label the receipt and
  human-listening boundary explicitly.

- [x] **Step 4: Run pronunciation and Echo contract tests**

  Run: `python3 -m unittest tests.test_pronunciation_plan_qc tests.test_custom_learning_audiobook_echo_contract -v`

  Expected: PASS.

### Task 4: Private editorial cover selection

**Files:**
- Modify: `skill/scripts/cover_receipts.py`
- Modify: `skill/references/cover-art.md`
- Modify: `skill/SKILL.md`
- Modify: `skills/custom-learning-audiobook/SKILL.md`
- Test: `tests/test_cover_receipts.py`
- Test: `tests/test_skill_cover_contract.py`

**Interfaces:**
- Consumes: `selection_source=editorial-autoselection`, privacy classification, and publication permission.
- Produces: a normal paired selection receipt only when classification is `private` and permission is false.

- [x] **Step 1: Write failing cover-policy tests**

  Assert that private editorial auto-selection succeeds, while public-safe,
  sensitive, or publication-authorized attempts fail.

- [x] **Step 2: Run focused tests and verify RED**

  Run: `python3 -m unittest tests.test_cover_receipts -v`

  Expected: FAIL because the new selection source is unsupported.

- [x] **Step 3: Implement the narrow selection source**

  Add `editorial-autoselection` to paired receipts and enforce the private,
  non-publishing invariant before writing the receipt. Document the editorial
  rubric and require the automated decision in the assumptions receipt.

- [x] **Step 4: Run cover tests and verify GREEN**

  Run: `python3 -m unittest tests.test_cover_receipts tests.test_skill_cover_contract -v`

  Expected: PASS.

### Task 5: Full validation and durable operating context

**Files:**
- Modify: `/Users/dfakkeldy/Developer/knowledge-base/bundle/projects/explainer-audiobooks.md`
- Modify: `/Users/dfakkeldy/Developer/knowledge-base/bundle/log.md`
- Modify: nearest KB index only if a new page is required

**Interfaces:**
- Consumes: final repository diff and verification results.
- Produces: a durable KB note describing the new default and its proof boundary.

- [x] **Step 1: Run all repository tests**

  Run: `python3 -m unittest discover -s tests -v`

  Expected: PASS with no failures or errors.

- [x] **Step 2: Validate skill folders**

  Run the installed skill validator against `skill/`,
  `skills/custom-learning-audiobook/`, `skills/longform-book-development/`, and
  `skills/fiction-book-development/`.

  Expected: all four report valid skill structure.

- [x] **Step 3: Update and lint the KB**

  Record that ready-to-listen/overnight requests default to private
  unattended-first-listen packages, while publication and learning acceptance
  remain human-governed. Run `python3 tools/kb_lint.py` in the KB repository.

  Expected: PASS.

- [x] **Step 4: Commit and publish repository work**

  Commit coherent repository and KB changes separately, push the feature branch,
  open a ready PR against `main`, and report hosted CI status.
