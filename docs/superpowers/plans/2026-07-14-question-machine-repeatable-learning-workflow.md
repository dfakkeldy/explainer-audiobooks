# Repeatable Learning Audiobook Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make curriculum selection, prospective learning records, and listener-named pronunciation acceptance reusable and fail closed across the audiobook skills.

**Architecture:** Extend the shared learning contract instead of creating a parallel pedagogy system. Add curriculum guidance, public-safe templates, and a phase-aware pronunciation plan/reel tool; wire the Explainer, Custom Learning, and Longform entry points to those shared artifacts. Private book text never becomes a fixture.

**Tech Stack:** Python 3 standard library, shell, JSON receipts, `ffmpeg`, `ffprobe`, `unittest`, Markdown skills.

## Global Constraints

- `skill/` remains the canonical shared source.
- Add no third-party Python dependencies.
- Listener-named pronunciation terms require human listening evidence before an unbounded full render.
- Preserve governed partial-probe exit-2 semantics.
- Keep private manuscript, sources, captures, and delivery artifacts out of Git.
- Use TDD and commit each task separately.

---

### Task 1: Curriculum-pattern selection

**Files:**
- Create: `skill/references/curriculum-patterns.md`
- Modify: `skill/references/learning-design.md`
- Modify: `skill/SKILL.md`
- Modify: `skills/custom-learning-audiobook/SKILL.md`
- Modify: `skills/longform-book-development/SKILL.md`
- Modify: `skills/longform-book-development/references/handoff-packet.md`
- Test: `tests/test_skill_learning_contract.py`

**Interfaces:**
- Produces: `learning-outline.json.curriculumPattern` containing non-empty `name`, `reason`, and `fitEvidence`.
- Consumes: existing outline authorization, throughlines, and chapters.

- [ ] **Step 1: Write the failing contract test**

```python
def test_curriculum_pattern_is_selected_and_preserved(self) -> None:
    reference = self.read("skill/references/curriculum-patterns.md").lower()
    for phrase in (
        "mechanism-first spiral", "end-to-end trace", "problem progression",
        "terminology inventory", "curriculumPattern", "fitEvidence",
    ):
        self.assertIn(phrase.lower(), reference)
    for relative in (
        "skill/SKILL.md", "skills/custom-learning-audiobook/SKILL.md",
        "skills/longform-book-development/SKILL.md",
        "skills/longform-book-development/references/handoff-packet.md",
    ):
        self.assertIn("curriculum-patterns.md", self.read(relative))
```

- [ ] **Step 2: Verify RED**

Run: `/usr/local/bin/python3 -m unittest tests.test_skill_learning_contract -v`  
Expected: FAIL because the reference and routing do not exist.

- [ ] **Step 3: Implement the shared reference and routing**

Define selection criteria, useful shapes, and failure modes for all three patterns. Require this record before drafting:

```json
{
  "curriculumPattern": {
    "name": "mechanism-first-spiral",
    "reason": "The learner needs one stable mechanism before larger systems.",
    "fitEvidence": "Approved beginner profile and mechanism-first outcome."
  }
}
```

Longform handoffs preserve the selection unless the user approves a change.

- [ ] **Step 4: Verify GREEN and commit**

```bash
/usr/local/bin/python3 -m unittest tests.test_skill_learning_contract -v
git add skill/references/curriculum-patterns.md skill/references/learning-design.md \
  skill/SKILL.md skills/custom-learning-audiobook/SKILL.md \
  skills/longform-book-development/SKILL.md \
  skills/longform-book-development/references/handoff-packet.md \
  tests/test_skill_learning_contract.py
git commit -m "feat: add reusable audiobook curriculum patterns"
```

### Task 2: Prospective learning-record templates

**Files:**
- Create: `skill/templates/learning-design/{learning-brief,learning-outline,chapter-plans,coverage-ledger,continuity,learning-review}.json`
- Create: `skill/templates/learning-design/README.md`
- Modify: `tests/test_skill_learning_contract.py`

**Interfaces:**
- Produces: six schema-v1 starter objects containing every key used by `learning_design_qc.py`.

- [ ] **Step 1: Add a failing template test**

```python
def test_learning_templates_cover_every_required_record(self) -> None:
    root = ROOT / "skill" / "templates" / "learning-design"
    expected = {
        "learning-brief.json", "learning-outline.json", "chapter-plans.json",
        "coverage-ledger.json", "continuity.json", "learning-review.json",
    }
    self.assertEqual(expected, {path.name for path in root.glob("*.json")})
    for name in expected:
        payload = json.loads((root / name).read_text(encoding="utf-8"))
        self.assertEqual(1, payload["schemaVersion"])
```

- [ ] **Step 2: Verify RED**

Run: `/usr/local/bin/python3 -m unittest tests.test_skill_learning_contract -v`  
Expected: FAIL because the template directory is absent.

- [ ] **Step 3: Add templates and README**

Use a public-safe email-classifier example. Set the review template to `verdict: pending` with an empty hash map so it cannot be mistaken for acceptance. State that templates are copied and edited before drafting; they are never receipts.

- [ ] **Step 4: Verify GREEN and commit**

```bash
/usr/local/bin/python3 -m unittest tests.test_skill_learning_contract -v
git add skill/templates/learning-design tests/test_skill_learning_contract.py
git commit -m "feat: add prospective learning-design templates"
```

### Task 3: Pronunciation-plan validator

**Files:**
- Create: `skill/scripts/pronunciation_plan_qc.py`
- Create: `tests/test_pronunciation_plan_qc.py`

**Interfaces:**
- Produces: `validate_plan(run_root: Path, phase: str) -> dict[str, object]` and `write_receipt(run_root: Path, out: Path) -> dict[str, object]`.
- CLI: `--run-root PATH --phase planning|full-render [--receipt-out PATH]`.

- [ ] **Step 1: Write failing schema and phase tests**

Use this complete public-safe record:

```json
{
  "schemaVersion": 1,
  "terms": [{
    "term": "hyperparameter",
    "variants": ["hyperparameters"],
    "source": "listener",
    "reason": "The listener explicitly requested pronunciation verification.",
    "expectedChapters": ["ch01.md"],
    "required": true,
    "status": "planned",
    "decision": null,
    "evidence": null
  }]
}
```

Test duplicate normalized terms, missing expected occurrences, and full-render rejection without accepted human evidence.

- [ ] **Step 2: Verify RED**

Run: `/usr/local/bin/python3 -m unittest tests.test_pronunciation_plan_qc -v`  
Expected: ERROR importing `pronunciation_plan_qc`.

- [ ] **Step 3: Implement validation and receipts**

Accept sources `listener|coverage-ledger|author`. Planning permits `planned|probed|accepted`; full-render requires every required term to be `accepted`, with `acceptedBy`, `acceptedAt`, a regular evidence file, and matching lowercase SHA-256. Bind the receipt to plan SHA and chapter hashes.

- [ ] **Step 4: Verify GREEN and commit**

```bash
/usr/local/bin/python3 -m unittest tests.test_pronunciation_plan_qc -v
git add skill/scripts/pronunciation_plan_qc.py tests/test_pronunciation_plan_qc.py
git commit -m "feat: validate listener pronunciation plans"
```

### Task 4: Early evidence-bound pronunciation reel

**Files:**
- Create: `skill/scripts/build_pronunciation_probe_reel.py`
- Create: `tests/test_pronunciation_probe_reel.py`

**Interfaces:**
- CLI: `--run-root PATH --work-dir PATH --out FILE --evidence-out FILE`.
- Consumes: pronunciation plan, `.anchors-chN.json`, identity-named M4A files, word timings, and capture hashes.
- Produces: positive-duration M4B and evidence binding plan, captures, clips, and reel hashes.

- [ ] **Step 1: Write failing integrity and coverage tests**

Generate a one-second M4A with `ffmpeg`. Test rejection for mismatched `identity.audioSHA256`, absent exact word timing, and a required term absent from every capture.

- [ ] **Step 2: Verify RED**

Run: `/usr/local/bin/python3 -m unittest tests.test_pronunciation_probe_reel -v`  
Expected: ERROR importing `build_pronunciation_probe_reel`.

- [ ] **Step 3: Implement extraction**

Normalize punctuation, select the first exact occurrence of every required term or variant, add 1.25 seconds of bounded context, extract and concatenate with `ffmpeg`, then verify with `ffprobe`. Evidence records term, heard variant, chapter, capture hash, source/reel ranges, plan SHA, and reel SHA.

- [ ] **Step 4: Verify GREEN and commit**

```bash
/usr/local/bin/python3 -m unittest tests.test_pronunciation_probe_reel -v
git add skill/scripts/build_pronunciation_probe_reel.py tests/test_pronunciation_probe_reel.py
git commit -m "feat: build governed pronunciation probe reels"
```

### Task 5: Full-render wrapper gate and documentation

**Files:**
- Modify: `skills/custom-learning-audiobook/scripts/echo_pronunciation_narrate.sh`
- Modify: `skills/custom-learning-audiobook/references/package-and-qc.md`
- Modify: `skills/custom-learning-audiobook/references/intake-and-research.md`
- Modify: `skills/custom-learning-audiobook/SKILL.md`
- Test: `tests/test_echo_pronunciation_wrapper.py`
- Test: `tests/test_skill_learning_contract.py`

**Interfaces:**
- Partial render: validate `--phase planning` and retain exit 2.
- Unbounded render: require `PRONUNCIATION_PLAN`, validate `--phase full-render`, and write `research/pronunciation-plan-receipt.json` before Echo.

- [ ] **Step 1: Add failing wrapper assertions**

Assert that an unbounded invocation contains:

```bash
/usr/local/bin/python3 "$EXPLAINER_ROOT/skill/scripts/pronunciation_plan_qc.py" \
  --run-root "$RUN_ROOT" --phase full-render \
  --receipt-out "$RUN_ROOT/research/pronunciation-plan-receipt.json"
```

- [ ] **Step 2: Verify RED**

Run: `/usr/local/bin/python3 -m unittest tests.test_echo_pronunciation_wrapper tests.test_skill_learning_contract -v`  
Expected: FAIL because the gate is absent.

- [ ] **Step 3: Implement the gate and exact workflow documentation**

Document: plan during intake; governed partial renders through every required occurrence; build and listen to the reel; record decisions; validate full-render; resume without `--max-chapters`. Refuse missing or stale plans for new technical books.

- [ ] **Step 4: Verify GREEN and commit**

```bash
/usr/local/bin/python3 -m unittest tests.test_echo_pronunciation_wrapper tests.test_skill_learning_contract -v
git add skills/custom-learning-audiobook/scripts/echo_pronunciation_narrate.sh \
  skills/custom-learning-audiobook/references/package-and-qc.md \
  skills/custom-learning-audiobook/references/intake-and-research.md \
  skills/custom-learning-audiobook/SKILL.md \
  tests/test_echo_pronunciation_wrapper.py tests/test_skill_learning_contract.py
git commit -m "feat: gate full narration on pronunciation acceptance"
```

### Task 6: Full verification and ready PR

- [ ] **Step 1: Run all tests and validators**

```bash
/usr/local/bin/python3 -m unittest discover -s tests -v
/usr/local/bin/python3 tools/validate_skills.py
/usr/local/bin/python3 tools/validate_custom_learning_skill_install.py
git diff --check
```

Expected: all tests pass except documented pre-existing skips; skill validation is clean; installed-path validation is current or truthfully `pending-integration`; no whitespace errors.

- [ ] **Step 2: Push and open the ready PR**

```bash
git push -u origin codex/question-machine-learning-edition-design
gh pr create --base main \
  --title "feat: make technical learning audiobooks repeatable" \
  --body "Adds curriculum patterns, prospective learning templates, and a fail-closed listener pronunciation plan and early reel workflow."
```

Expected: ready PR targeting `main`; report its exact head and hosted-check state.
