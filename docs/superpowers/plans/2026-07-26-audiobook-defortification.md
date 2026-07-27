# Audiobook De-fortification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the two gated nonfiction production skills with one lean `audiobook` skill that takes a book request through five questions to a narrated EPUB + M4B in the iCloud Books folder, with a next-day feedback loop that revises in place.

**Architecture:** Two scripts currently hard-fail without receipts and must be unblocked first, because nothing can be built until they are. Then the retired gate scripts and their tests are deleted, the Echo narration tooling is renamed to reflect what it actually is, the new skill body is written, the craft references are trimmed, and the publishing tooling is parked behind one reference doc. Downstream pointers and the skill validator are updated last.

**Tech Stack:** Python 3.11 (`/usr/local/bin/python3`), `unittest`, Bash, Pillow 9.4.0, Echo/Kokoro CLI for narration.

## Global Constraints

- **Use `/usr/local/bin/python3` for every command in this plan.** The default `python3` on PATH is Homebrew 3.14.6 and **does not have Pillow**. `build_book.py` imports `cover_receipts` → `refresh_epub_cover` → `PIL` at module level, so it cannot even start under 3.14. `/usr/local/bin/python3` is 3.11.1 with Pillow 9.4.0. The Echo shell scripts already hardcode this interpreter.
- **Baseline before any change:** `/usr/local/bin/python3 -m unittest discover tests` → `Ran 583 tests` / `OK (skipped=6)`, about 5 minutes. Every task must end at a green suite; test-count drops from deliberate deletions are expected and are called out per task.
- This repo uses `unittest`. **`pytest` is not installed.** Never write a `pytest` command.
- Run every command from the repo root: `/Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3`. The Bash working directory persists between calls — always `cd` to the repo root in the same command.
- **Do not change the build run-root convention** `.build/custom-learning-audiobooks/<slug>/`. It is asserted by exact string equality in `echo_pronunciation_preflight.sh:587` and is woven through the lease, resume, and state receipts. It is internal build scratch the user never sees. Renaming it is out of scope.
- Author metadata is always the human owner, `Dan Fakkeldy`. The generating model goes in `--contributor`. Never put a model name in the author field.
- Preserve `--fiction-receipt`. `skills/fiction-book-development` is out of scope and still consumes it.
- Do not delete anything under `books/` or in the iCloud Books folder.

- **Line numbers in this plan are pre-edit.** They drift as tasks land. Always locate a block by the code content quoted in the step, not by line number alone.

**Spec:** `docs/superpowers/specs/2026-07-26-audiobook-defortification-design.md`

### Deliberate deviation from the spec

The spec says the Echo scripts move to `skill/scripts/echo/`. This plan instead renames `skills/custom-learning-audiobook/` to `skills/echo-narration/` (Task 3).

Reason: the scripts resolve the repo root as `$SCRIPT_DIR/../../../`, and `echo_pronunciation_preflight.sh:587` asserts the run root by exact string equality. Moving to `skill/scripts/echo/` changes the directory depth and would require rewriting those paths through the lease, resume, and state machinery — real risk for no user-visible benefit. A same-depth rename achieves the spec's intent (the directory stops claiming to be a skill) while leaving every relative path valid.

---

### Task 1: Unblock `build_book.py`

`build_book.py:467` refuses to build without `--learning-receipt`. It also imports `verify_learning_receipt` from `learning_design_qc`, which this plan deletes. Until this task lands, no book can be built at all.

**Files:**
- Create: `tests/test_build_book_lean.py`
- Modify: `skill/scripts/build_book.py:48`, `:97-101`, `:437-471`, `:475-476`
- Delete: `skill/scripts/learning_design_qc.py`, `tests/test_learning_design_gate.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `build_book.build(chapters_dir, out_dir, title, author, subtitle, slug, lang="en", cover=None, contributor="", cover_selection=None, m4b_cover=None, prose_receipt=None, fiction_receipt=None, non_narrated_appendix=None)` — note `learning_receipt` is **gone** from the signature and it is **positionally before** `fiction_receipt` today, so the positional call at line 475 must be updated. The CLI accepts no `--learning-receipt`, `--legacy-without-learning-receipt`, or `--learning-pilot`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_build_book_lean.py`:

```python
from __future__ import annotations

import io
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

REPO = Path(__file__).parents[1]
sys.path.insert(0, str(REPO / "skill" / "scripts"))
import build_book


class LeanBuildTests(unittest.TestCase):
    def _chapters(self, root: Path) -> Path:
        chapters = root / "chapters"
        chapters.mkdir()
        (chapters / "ch01.md").write_text(
            "# One\n\nThese four words are narrated.\n", encoding="utf-8"
        )
        return chapters

    def test_build_succeeds_with_no_receipt_arguments(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            chapters = self._chapters(root)
            out = root / "dist"

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                build_book.build(chapters, out, "Fixture", "Dan Fakkeldy", "", "fixture-book")

            self.assertIn("Chapters: 1", stdout.getvalue())
            self.assertTrue((out / "fixture-book.epub").is_file())
            self.assertTrue((out / "fixture-book.md").is_file())

    def test_cli_builds_without_any_receipt_flag(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            chapters = self._chapters(root)
            out = root / "dist"

            result = subprocess.run(
                [
                    "/usr/local/bin/python3",
                    str(REPO / "skill" / "scripts" / "build_book.py"),
                    "--chapters-dir", str(chapters),
                    "--out-dir", str(out),
                    "--title", "Fixture",
                    "--author", "Dan Fakkeldy",
                    "--slug", "fixture-book",
                ],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((out / "fixture-book.epub").is_file())

    def test_retired_gate_flags_are_gone(self) -> None:
        result = subprocess.run(
            ["/usr/local/bin/python3", str(REPO / "skill" / "scripts" / "build_book.py"), "--help"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("--learning-receipt", result.stdout)
        self.assertNotIn("--legacy-without-learning-receipt", result.stdout)
        self.assertNotIn("--learning-pilot", result.stdout)
        self.assertIn("--fiction-receipt", result.stdout)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && /usr/local/bin/python3 -m unittest tests.test_build_book_lean -v
```

Expected: FAIL. `test_build_succeeds_with_no_receipt_arguments` passes already (the `build()` function itself has no gate), but `test_cli_builds_without_any_receipt_flag` fails with a non-zero exit and stderr containing `current builds require --learning-receipt`, and `test_retired_gate_flags_are_gone` fails because `--learning-receipt` is still in `--help`.

- [ ] **Step 3: Remove the `learning_design_qc` import**

In `skill/scripts/build_book.py`, delete line 48:

```python
from learning_design_qc import verify_learning_receipt
```

Line 47 (`from fiction_production_qc import verify_fiction_receipt`) stays.

- [ ] **Step 4: Drop `learning_receipt` from `build()`**

Replace lines 97-101:

```python
def build(chapters_dir, out_dir, title, author, subtitle, slug, lang="en", cover=None,
          contributor="", cover_selection=None, m4b_cover=None, prose_receipt=None,
          learning_receipt=None, fiction_receipt=None, non_narrated_appendix=None):
    if learning_receipt is not None:
        verify_learning_receipt(Path(chapters_dir), Path(learning_receipt))
    if fiction_receipt is not None:
```

with:

```python
def build(chapters_dir, out_dir, title, author, subtitle, slug, lang="en", cover=None,
          contributor="", cover_selection=None, m4b_cover=None, prose_receipt=None,
          fiction_receipt=None, non_narrated_appendix=None):
    if fiction_receipt is not None:
```

- [ ] **Step 5: Replace the CLI gate with a plain optional argument**

Replace the whole `learning_gate` block and the error checks (lines 437-471 — from `learning_gate = ap.add_mutually_exclusive_group()` through the closing paren of the `print("PILOT ONLY: ...")` statement):

```python
    learning_gate = ap.add_mutually_exclusive_group()
    learning_gate.add_argument(
        "--learning-receipt",
        default=None,
        help="Passed learning-design receipt that must match the canonical chapters",
    )
    learning_gate.add_argument(
        "--fiction-receipt",
        default=None,
        help="Passed private first-listen fiction receipt matching the canonical chapters",
    )
    learning_gate.add_argument(
        "--legacy-without-learning-receipt",
        action="store_true",
        help="Reproduce a legacy artifact only; forbidden for new or revised books",
    )
    learning_gate.add_argument(
        "--learning-pilot",
        action="store_true",
        help="Build a nonpackage narrated-comprehension pilot before full drafting",
    )
    a = ap.parse_args()
    if a.learning_pilot and not a.slug.endswith("-pilot"):
        ap.error("pilot builds require --slug ending in -pilot")
    if (
        a.learning_receipt is None
        and a.fiction_receipt is None
        and not a.legacy_without_learning_receipt
        and not a.learning_pilot
    ):
        ap.error(
            "current builds require --learning-receipt; use "
            "--fiction-receipt for a private first-listen fiction package, "
            "--learning-pilot for a nonpackage pilot or "
            "--legacy-without-learning-receipt only to reproduce an old artifact"
        )
    if a.learning_pilot:
        print("PILOT ONLY: not a governed book package or learning-completion claim")
```

with:

```python
    ap.add_argument(
        "--fiction-receipt",
        default=None,
        help="Passed private first-listen fiction receipt matching the canonical chapters",
    )
    a = ap.parse_args()
```

- [ ] **Step 6: Fix the positional call to `build()`**

Replace lines 475-476:

```python
    build(a.chapters_dir, a.out_dir, a.title, a.author, a.subtitle, a.slug, a.lang, a.cover,
          a.contributor, a.cover_selection, a.m4b_cover, a.prose_receipt,
          a.learning_receipt, a.fiction_receipt, a.non_narrated_appendix)
```

with:

```python
    build(a.chapters_dir, a.out_dir, a.title, a.author, a.subtitle, a.slug, a.lang, a.cover,
          a.contributor, a.cover_selection, a.m4b_cover, a.prose_receipt,
          a.fiction_receipt, a.non_narrated_appendix)
```

- [ ] **Step 7: Delete the retired script and its test**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && git rm skill/scripts/learning_design_qc.py tests/test_learning_design_gate.py
```

- [ ] **Step 8: Run the new test to verify it passes**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && /usr/local/bin/python3 -m unittest tests.test_build_book_lean -v
```

Expected: `Ran 3 tests` / `OK`.

- [ ] **Step 9: Run the full suite**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && /usr/local/bin/python3 -m unittest discover tests 2>&1 | tail -20
```

Expected: `OK (skipped=6)`. Test count drops from 583 by the number of tests in the deleted `test_learning_design_gate.py`, plus 3 added. If anything else fails, it is a real regression — most likely another test importing `learning_design_qc` or calling `build()` with a positional `learning_receipt`. Fix it before committing; do not delete a failing test to make this step pass.

- [ ] **Step 10: Commit**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && git add -A && git commit -m "feat: build a book without a learning receipt

build_book.py refused every build that did not carry a learning-design
receipt, and imported the receipt verifier at module scope. The private
lane has no receipts, so nothing could be built.

Drop the gate, its two escape hatches, and learning_design_qc.py.
--fiction-receipt stays; fiction-book-development still consumes it.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 2: Unblock Echo narration

`echo_pronunciation_narrate.sh:141-160` refuses to render without a canonical `pronunciation-plan.json` that passes `pronunciation_plan_qc.py`. Remove the gate and the variable with it.

**Correction (2026-07-26, after review of the first attempt).** This task originally kept `PRONUNCIATION_PLAN` as an optional input, on the stated grounds that feeding Echo terms like `hyperparameter` improves the render. That was wrong. `echo-cli narrate` accepts only `--epub --out --sidecar --voice --title --author --cover --work-dir --db --jobs --threads --resume --max-chapters`; it has no lexicon or pronunciation flag, and nothing in the repo passes the variable anywhere. The pronunciation plan was never an input to the renderer — it existed solely to feed the QC gate this task deletes. Keeping the variable would leave a check whose only possible effect is to abort an otherwise-good render. Dan's call, 2026-07-26: remove it entirely.

**Files:**
- Create: `tests/test_echo_narration_lean.py`
- Modify: `skills/custom-learning-audiobook/scripts/echo_pronunciation_narrate.sh:141-160`
- Delete: `skill/scripts/pronunciation_plan_qc.py`, `skill/scripts/build_pronunciation_probe_reel.py`, `skills/custom-learning-audiobook/scripts/echo_learning_pilot_narrate.sh`, `tests/test_pronunciation_plan_qc.py`, `tests/test_pronunciation_probe_reel.py`

**Interfaces:**
- Consumes: nothing from Task 1.
- Produces: `echo_pronunciation_narrate.sh` has no `PRONUNCIATION_PLAN`
  interface at all. Task 3 renames the directory holding this script; Task 4's
  SKILL.md documents its invocation.

- [ ] **Step 1: Write the failing test**

Create `tests/test_echo_narration_lean.py`:

```python
from __future__ import annotations

import unittest
from pathlib import Path

REPO = Path(__file__).parents[1]
WRAPPER = REPO / "skills" / "custom-learning-audiobook" / "scripts" / "echo_pronunciation_narrate.sh"


class EchoNarrationLeanTests(unittest.TestCase):
    def setUp(self) -> None:
        if not WRAPPER.is_file():
            self.skipTest(f"wrapper not at {WRAPPER}; Task 3 moves it")
        self.text = WRAPPER.read_text(encoding="utf-8")

    def test_wrapper_does_not_require_a_pronunciation_plan(self) -> None:
        self.assertNotIn("PRONUNCIATION_PLAN is required", self.text)
        self.assertNotIn("PRONUNCIATION_PLAN must be the canonical run plan", self.text)

    def test_wrapper_does_not_invoke_the_deleted_qc_script(self) -> None:
        self.assertNotIn("pronunciation_plan_qc.py", self.text)

    def test_pronunciation_plan_variable_is_gone(self) -> None:
        self.assertNotIn("PRONUNCIATION_PLAN", self.text)

    def test_retired_scripts_are_gone(self) -> None:
        for retired in (
            REPO / "skill" / "scripts" / "pronunciation_plan_qc.py",
            REPO / "skill" / "scripts" / "build_pronunciation_probe_reel.py",
            REPO / "skills" / "custom-learning-audiobook" / "scripts" / "echo_learning_pilot_narrate.sh",
        ):
            self.assertFalse(retired.exists(), f"{retired} should be deleted")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && /usr/local/bin/python3 -m unittest tests.test_echo_narration_lean -v
```

Expected: 3 of 4 fail — `test_wrapper_does_not_require_a_pronunciation_plan`, `test_wrapper_does_not_invoke_the_deleted_qc_script`, and `test_retired_scripts_are_gone`.

- [ ] **Step 3: Remove the plan gate from the wrapper**

In `skills/custom-learning-audiobook/scripts/echo_pronunciation_narrate.sh`, replace this block (lines 141-160, inside `if (( ! RECOVER_STALE_LOCK )); then`):

```bash
    CANONICAL_PRONUNCIATION_PLAN="$RUN_ROOT/research/pronunciation-plan.json"
    if [[ -z ${PRONUNCIATION_PLAN:-} ]]; then
      printf 'PRONUNCIATION_PLAN is required; expected %s\n' \
        "$CANONICAL_PRONUNCIATION_PLAN" >&2
      exit 64
    fi
    if [[ "$PRONUNCIATION_PLAN" != "$CANONICAL_PRONUNCIATION_PLAN" ]]; then
      printf 'PRONUNCIATION_PLAN must be the canonical run plan: %s\n' \
        "$CANONICAL_PRONUNCIATION_PLAN" >&2
      exit 64
    fi
    if [[ -n "$MAX_CHAPTERS" ]]; then
      /usr/local/bin/python3 "$SCRIPT_DIR/../../../skill/scripts/pronunciation_plan_qc.py" \
        --run-root "$RUN_ROOT" \
        --phase planning
    else
      /usr/local/bin/python3 "$SCRIPT_DIR/../../../skill/scripts/pronunciation_plan_qc.py" \
        --run-root "$RUN_ROOT" \
        --phase full-render \
        --receipt-out "$RUN_ROOT/research/pronunciation-plan-receipt.json"
    fi
```

with nothing — delete the block outright, along with every other reference to `PRONUNCIATION_PLAN` in the wrapper. Nothing consumes the variable, so no replacement check is warranted.

Leave the surrounding `if (( ! RECOVER_STALE_LOCK )); then ... fi` intact. If removing the block leaves that conditional with an empty body, remove the now-empty conditional too rather than leaving a no-op branch.

Note that `tools/validate_custom_learning_skill_install.py` pins a SHA-256 of this wrapper and must be updated to the new hash. That file is deleted in Task 3, but it must pass until then.

- [ ] **Step 4: Delete the retired scripts and tests**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && git rm \
  skill/scripts/pronunciation_plan_qc.py \
  skill/scripts/build_pronunciation_probe_reel.py \
  skills/custom-learning-audiobook/scripts/echo_learning_pilot_narrate.sh \
  tests/test_pronunciation_plan_qc.py \
  tests/test_pronunciation_probe_reel.py
```

- [ ] **Step 5: Check for orphaned references**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && grep -rn "pronunciation_plan_qc\|build_pronunciation_probe_reel\|echo_learning_pilot_narrate" --include=*.py --include=*.sh . | grep -v __pycache__ | grep -v '^\./docs/'
```

Expected: no output. Any hit outside `docs/` is a live caller that must be fixed now. Hits inside `docs/` are historical plans and specs — leave them alone.

- [ ] **Step 6: Verify the wrapper is still valid Bash**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && bash -n skills/custom-learning-audiobook/scripts/echo_pronunciation_narrate.sh && echo "SYNTAX OK"
```

Expected: `SYNTAX OK`.

- [ ] **Step 7: Run the new test to verify it passes**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && /usr/local/bin/python3 -m unittest tests.test_echo_narration_lean -v
```

Expected: `Ran 4 tests` / `OK`.

- [ ] **Step 8: Run the full suite**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && /usr/local/bin/python3 -m unittest discover tests 2>&1 | tail -20
```

Expected: `OK (skipped=6)`. `tests/test_custom_learning_audiobook_echo_runtime.py` exercises the wrapper and must still pass; if it asserts on the plan gate, update those assertions rather than deleting the test — it covers real render behaviour that still matters.

- [ ] **Step 9: Commit**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && git add -A && git commit -m "feat: narrate without a validated pronunciation plan

The Echo wrapper refused to render unless a canonical pronunciation-plan
existed at an exact path and passed QC. The word list is genuinely useful
input for the renderer; the gate around it was not.

Remove `PRONUNCIATION_PLAN` entirely. Drop the plan QC, the probe reel builder,
and the pilot narration wrapper.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 3: Rename the Echo tooling directory

After Tasks 1-2 the directory `skills/custom-learning-audiobook/` holds no skill — only Echo narration tooling. `skills/echo-narration/` is the same directory depth, so every `$SCRIPT_DIR/../../../` in the shell scripts still resolves to the repo root unchanged.

**Files:**
- Rename: `skills/custom-learning-audiobook/` → `skills/echo-narration/`
- Delete: `skills/echo-narration/SKILL.md`, `skills/echo-narration/agents/`, `skills/echo-narration/references/intake-and-research.md`, `tools/validate_custom_learning_skill_install.py`, `tests/test_custom_learning_audiobook_install_contract.py`
- Modify (do NOT delete — see the correction below): `tests/test_custom_learning_audiobook_echo_contract.py`

**Correction (2026-07-26, after Task 2's review).** This task originally deleted `tests/test_custom_learning_audiobook_echo_contract.py` outright. That was wrong. Task 2's implementer deleted it early, and review established that only 4 of its 18 tests were obsolete; the other 14 are text contracts on files that **survive this rename** — `echo_pronunciation_narrate.sh`, `echo_pronunciation_preflight.sh`, `echo_pronunciation_lease.py`, and the operator docs. One of them, `test_run_id_is_derived_in_exactly_one_place`, is a named regression guard against a past production break. The 14 were restored in commit `e324b5f`. This task must **repoint their paths** to `skills/echo-narration/`, not delete them. Rename the file to `tests/test_echo_narration_contract.py` to match what it now tests.
- Create: `skills/echo-narration/references/narrating.md`
- Modify: `tests/test_custom_learning_audiobook_echo_runtime.py`, `tests/test_echo_installed_renderer.py`, `tests/test_echo_narration_lean.py`, `skill/references/cover-art.md:97,418`

**Interfaces:**
- Consumes: the unblocked wrapper from Task 2.
- Produces: the narration entry point at `skills/echo-narration/scripts/echo_pronunciation_narrate.sh`. Task 4's SKILL.md and Task 6's publishing reference both cite this exact path.

- [ ] **Step 1: Extract the Echo command reference before deleting anything**

`skills/custom-learning-audiobook/references/package-and-qc.md` mixes two things: real Echo/ffprobe commands that are still needed, and receipt/sync ceremony that is not. Read it in full, then write `skills/custom-learning-audiobook/references/narrating.md` containing only the still-live material:

- the `echo-cli` invocation and its `--voice am_michael` default with `am_puck` fallback;
- the `<slug>.alignment.json` sidecar and what consumes it;
- the `ffprobe` duration and chapter-marker check;
- the "Interior Figures" handling for EPUB images;
- the rule that a narrated Echo M4B is never mutated after export (so `replace_m4b_cover.py` is never run on one).

Exclude every receipt, selection-source, privacy-classification, permission-to-publish, probe-reel, and sync-classification instruction. Those either die here or move to Task 6's publishing reference.

- [ ] **Step 2: Delete the skill surface and its install validator**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && git rm -r \
  skills/custom-learning-audiobook/SKILL.md \
  skills/custom-learning-audiobook/agents \
  skills/custom-learning-audiobook/references/intake-and-research.md \
  skills/custom-learning-audiobook/references/package-and-qc.md \
  tools/validate_custom_learning_skill_install.py \
  tests/test_custom_learning_audiobook_install_contract.py
```

**Do not delete `tests/test_custom_learning_audiobook_echo_contract.py`.** Its 14 surviving tests cover files this task renames rather than removes. Rename it alongside them and repoint its paths:

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && git mv tests/test_custom_learning_audiobook_echo_contract.py tests/test_echo_narration_contract.py
```

Then update every `skills/custom-learning-audiobook` path inside it to `skills/echo-narration`. If one of the 14 asserts on text in `references/package-and-qc.md` (deleted in Step 2), repoint that assertion at the file the text moved to — `references/narrating.md` for Echo commands, or `skill/references/publishing-a-public-edition.md` for receipt and sync prose. Do not delete an assertion because its source file moved.

- [ ] **Step 3c: Restore six assertions lost with two mixed-subject tests**

Task 2's re-review found that two of the four tests deleted from this file were mixed-subject: they asserted on the deleted pilot wrapper *and* on files that survive. Their pilot half was correctly dropped; their surviving half is now guarded by nothing. Read the originals for the exact assertion text:

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && git show 9b86658:tests/test_custom_learning_audiobook_echo_contract.py | sed -n '225,320p'
```

Add one new test to the renamed file covering what is currently unguarded, with paths pointing at `skills/echo-narration/`:

1. The four shared shell functions are **defined** in `echo_pronunciation_preflight.sh` (they are, at roughly lines 84, 251, 315, 330).
2. `echo_pronunciation_narrate.sh` **uses** `echo_pronunciation_resolve_installed_renderer` and `echo_pronunciation_assert_leases` rather than defining local copies.
3. The anti-duplication negatives against the wrapper: `assertNotIn("\nresolve_installed_renderer() {", ...)` and `assertNotIn("\nassert_leases() {", ...)`.

Item 3 is the point of the exercise. It is the same class of guard as `test_run_id_is_derived_in_exactly_one_place`, which exists because duplicating a derivation between the preflight and the wrapper once broke every render in production. Do not skip it as redundant with item 2 — item 2 proves the shared function is called, item 3 proves a local copy has not been added alongside it.

`validate_custom_learning_skill_install.py` validated the install of a skill that no longer exists. Its Hermes consumer is a known downstream break, recorded in Task 8 Step 6.

- [ ] **Step 3: Rename the directory**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && git mv skills/custom-learning-audiobook skills/echo-narration && ls skills/echo-narration
```

Expected output: `references  scripts`.

- [ ] **Step 4: Update the test path constants**

In `tests/test_echo_narration_lean.py`, change the two path constants:

```python
WRAPPER = REPO / "skills" / "custom-learning-audiobook" / "scripts" / "echo_pronunciation_narrate.sh"
```

to:

```python
WRAPPER = REPO / "skills" / "echo-narration" / "scripts" / "echo_pronunciation_narrate.sh"
```

and in `test_retired_scripts_are_gone`:

```python
            REPO / "skills" / "custom-learning-audiobook" / "scripts" / "echo_learning_pilot_narrate.sh",
```

to:

```python
            REPO / "skills" / "echo-narration" / "scripts" / "echo_learning_pilot_narrate.sh",
```

Then update every `skills/custom-learning-audiobook` path in `tests/test_custom_learning_audiobook_echo_runtime.py` and `tests/test_echo_installed_renderer.py` to `skills/echo-narration`. Rename the runtime test file to match what it now tests:

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && git mv tests/test_custom_learning_audiobook_echo_runtime.py tests/test_echo_narration_runtime.py
```

- [ ] **Step 5: Update the two cover-art pointers**

In `skill/references/cover-art.md`, line 97 and line 418 both point at the deleted `skills/custom-learning-audiobook/references/package-and-qc.md`. Repoint both to `skill/references/publishing-a-public-edition.md` (created in Task 6). Leave the surrounding prose otherwise intact — Task 5 trims this file.

- [ ] **Step 5b: Fix the fiction contract test**

`tests/test_fiction_book_development_contract.py:101-113` reads the deleted `skills/custom-learning-audiobook/references/package-and-qc.md`. Its point — fiction uses `--fiction-receipt`, not a learning receipt — is still true and worth keeping; only the second source file is gone. Narrow it to the fiction skill body:

```python
    def test_authorized_private_production_uses_fiction_receipt_not_learning_receipt(self) -> None:
        skill = self.read("SKILL.md")
        self.assertIn("fiction-production-receipt.json", skill)
        self.assertIn("--fiction-receipt", skill)
        self.assertIn("Do not pretend fiction passed a learning-design gate", skill)
```

If the last assertion now fails because `skills/fiction-book-development/SKILL.md` phrases the learning-gate warning in terms that no longer exist, update that sentence in the fiction skill to say fiction carries its own receipt — do not delete the assertion. `--fiction-receipt` must keep working; the fiction skill is out of scope for every other change.

Note: `tests/test_corpus_regression.py` and `tests/test_claude_platform_public_series.py` match `custom-learning-audiobook**s**` — the plural run-root convention, which this plan does not touch. Leave both files alone.

- [ ] **Step 6: Verify no stale paths remain in live code**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && grep -rn "custom-learning-audiobook\b" tests tools skill skills README.md 2>/dev/null | grep -v __pycache__
```

Expected: no output. Two deliberate exclusions:

- The trailing `\b` matters. Without it the pattern also matches `custom-learning-audiobook**s**`, the plural run-root convention in `tests/test_corpus_regression.py` and `tests/test_claude_platform_public_series.py`, which this plan does not touch.
- `docs/` is excluded — it holds dated records of past work that should stay accurate about what was true then.

`README.md` currently matches and is handled in Task 8 Step 2; if it still matches here, fix it now instead.

- [ ] **Step 7: Run the full suite**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && /usr/local/bin/python3 -m unittest discover tests 2>&1 | tail -20
```

Expected: `OK (skipped=6)`. `tools/validate_skills.py` still references the deleted skill and will be rewritten in Task 7 — it is not run by the unittest suite, so it does not fail here.

- [ ] **Step 8: Commit**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && git add -A && git commit -m "refactor: rename custom-learning-audiobook to echo-narration

After the gates came out the directory holds no skill, only the Echo
narration tooling. Same directory depth, so the scripts' relative paths
to the repo root are unchanged.

Keep the live Echo commands as references/narrating.md; drop the intake,
packaging, and receipt prose along with the skill itself.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 4: Write the `audiobook` skill

The keystone deliverable: one skill body under 200 lines replacing 1,234 lines across two skills.

**Files:**
- Create: `tests/test_audiobook_skill_contract.py`
- Rewrite: `skill/SKILL.md`

**Interfaces:**
- Consumes: `build_book.py` without receipt flags (Task 1); `skills/echo-narration/scripts/echo_pronunciation_narrate.sh` (Tasks 2-3).
- Produces: a skill named `audiobook`. Task 7's `validate_skills.py` asserts that name; Task 8's symlink migration uses it.

- [ ] **Step 1: Write the failing contract test**

Create `tests/test_audiobook_skill_contract.py`:

```python
from __future__ import annotations

import unittest
from pathlib import Path

REPO = Path(__file__).parents[1]
SKILL = REPO / "skill" / "SKILL.md"


class AudiobookSkillContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = SKILL.read_text(encoding="utf-8")

    def test_skill_is_named_audiobook(self) -> None:
        self.assertTrue(self.text.startswith("---\n"))
        header = self.text.split("\n---\n", 1)[0]
        self.assertIn("name: audiobook", header)

    def test_skill_is_lean(self) -> None:
        lines = self.text.splitlines()
        self.assertLess(len(lines), 200, f"SKILL.md is {len(lines)} lines")

    def test_intake_asks_five_questions_then_starts(self) -> None:
        for needle in (
            "what should the listener be able to do",
            "Who is it for",
            "already know",
            "how long",
            "specific real thing",
        ):
            self.assertIn(needle, self.text)
        self.assertIn("state the plan in one line", self.text)

    def test_craft_passes_that_survive_are_named(self) -> None:
        for needle in (
            "claim-traceability",
            "tightening",
            "de-listification",
            "sentence-rhythm",
            "ear-pass",
            "blind beginner review",
            "--fail-on-style",
            "humanizer",
            "story ledger",
        ):
            self.assertIn(needle, self.text)

    def test_defaults_are_recorded(self) -> None:
        for needle in ("am_michael", "am_puck", "Dan Fakkeldy", "road-book"):
            self.assertIn(needle, self.text)
        self.assertIn("af_heart", self.text)

    def test_pillow_interpreter_is_documented(self) -> None:
        self.assertIn("/usr/local/bin/python3", self.text)

    def test_delivery_layout_is_specified(self) -> None:
        for needle in ("source/", "previous/", "feedback.md", "brief.md"):
            self.assertIn(needle, self.text)
        self.assertIn("com~apple~CloudDocs/Books", self.text)

    def test_preserve_on_revision_rule_survives(self) -> None:
        self.assertIn("what is working and must not change", self.text)

    def test_retired_gate_vocabulary_is_gone(self) -> None:
        for banned in (
            "learning receipt",
            "--learning-receipt",
            "prose-style-receipt",
            "unattended-first-listen",
            "governed-final",
            "public-first-listen",
            "permission-to-publish",
            "comprehension pilot",
            "probe reel",
            "package-or-blocker",
            "coverage ledger",
        ):
            self.assertNotIn(banned, self.text, f"retired gate vocabulary present: {banned!r}")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && /usr/local/bin/python3 -m unittest tests.test_audiobook_skill_contract -v
```

Expected: most tests FAIL. The current `skill/SKILL.md` is 677 lines, named `explainer-audiobook`, and is dense with the retired vocabulary.

- [ ] **Step 3: Rewrite `skill/SKILL.md`**

Replace the file entirely. Follow the spec's section 2 ("The run"), section 3 ("What a book is"), and section 4 ("The redo loop"). Required structure and content:

**Frontmatter** — `name: audiobook`, and a description that triggers on "make me a book about X", "I want to learn X", "turn this repo into an audiobook", "a book I can listen to while driving". Keep it under 1024 characters.

**Body sections, in order:**

1. **Interpreter note.** State plainly: run every script with `/usr/local/bin/python3`. The default `python3` lacks Pillow and cannot import `build_book.py`.
2. **Intake.** The five questions, asked once through the host's available
   batched input mechanism, followed by "state the plan in one line — title,
   angle, chapter count, estimated runtime — and start. Do not wait for a
   reply." Then the silent defaults table: road-book listening, `am_michael`
   then `am_puck`, never `af_heart`, author `Dan Fakkeldy`, model name to
   `--contributor`, warm second-person spoken voice, private, cover
   auto-selected.
3. **Research.** Evidence notes with real sources and locators, a story ledger (a story has a reversal; without one it is an illustration), per-chapter fact packs naming the real files, tools, and commands. Plain Markdown. The rule that survives: the manuscript may only assert what the research supports.
4. **Outline.** Argument-level and question-led — durable outcomes, a governing question, a narrative spine, varied chapter jobs, 2-4 throughlines. A terminology syllabus is not an outline. No approval pause.
5. **Draft.** One frontier author, every section in order, carrying the outline, fact pack, previous section's text or faithful summary, current section's job, and its must-not-repeat list. Cheaper workers may extract, verify, assemble, render, and report with citations; they never write or replace chapters.
6. **Revise.** The five named passes in order, then the blind beginner review, then `prose_qc.py --fail-on-style`, then the `humanizer` skill, then `prose_qc.py --fail-on-style` again. State explicitly that no ledger records the passes.
7. **Produce and deliver.** Three cover pairs rendered via `render_cover_pair(...)`, best auto-selected on the rubric, choice reported not requested. `build_book.py` with no receipt flags. Echo narration via `skills/echo-narration/scripts/echo_pronunciation_narrate.sh`. Copy the finished folder into `~/Library/Mobile Documents/com~apple~CloudDocs/Books/<Book Title>/` in the layout below.
8. **What a book is.** The folder layout from the spec, verbatim.
9. **The redo loop.** The eight numbered steps from the spec, including step 3 preserve-on-revision. Include the exact phrase `what is working and must not change`. Note that recurring feedback across ~3 books is a standing preference worth writing to memory.

Carry forward the narration constraints that make these books listenable: at most one short line of code spoken at a time; name the real files, tools, and commands rather than erasing them into "the settings file"; every term defined in plain English.

Point at the surviving references rather than restating them: `references/narration-style.md`, `references/voice-design.md`, `references/cover-art.md`, `references/curriculum-patterns.md`, `references/declaudification.md`, `references/humanizer-pass.md`, `references/frontier-manuscript-pipeline.md`, `references/road-book-mode.md`, `references/learning-design.md`.

- [ ] **Step 3b: Delete the two contract tests that pin the retired skill body**

`tests/test_skill_learning_contract.py` pins the learning-gate vocabulary in the old SKILL.md, and `tests/test_skill_unattended_contract.py` pins the production-mode contract that Task 5 deletes. Both describe behaviour this plan removes on purpose; neither covers live tooling.

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && git rm tests/test_skill_learning_contract.py tests/test_skill_unattended_contract.py
```

The replacement coverage is `tests/test_audiobook_skill_contract.py` from Step 1, whose `test_retired_gate_vocabulary_is_gone` asserts the opposite of what these two asserted.

- [ ] **Step 4: Run the contract test to verify it passes**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && /usr/local/bin/python3 -m unittest tests.test_audiobook_skill_contract -v
```

Expected: `Ran 9 tests` / `OK`. If `test_skill_is_lean` fails, cut prose — do not raise the limit.

- [ ] **Step 5: Run the full suite**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && /usr/local/bin/python3 -m unittest discover tests 2>&1 | tail -25
```

Expected: exactly two failing files — `tests/test_skill_prose_contract.py` and `tests/test_skill_cover_contract.py`, which pin phrases in the old SKILL.md. **Do not fix them here** — Task 7 retargets both. Every other test must pass. If a third file fails, it is a real regression: investigate before moving on.

- [ ] **Step 6: Commit**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && git add -A && git commit -m "feat: the audiobook skill

One skill replaces explainer-audiobook and custom-learning-audiobook:
five questions, a one-line plan, then a narrated book in the iCloud Books
folder with no approval pause anywhere in between.

Keeps the craft that makes prose better and drops the paperwork that
proved it happened. Carries the preserve-on-revision rule into the redo
loop, where it now sits on the main path.

Two skill contract tests fail until Task 7 retargets them.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 5: Trim the craft references

The references hold the writing craft worth keeping and the gate prose worth losing, interleaved.

**Files:**
- Delete: `skill/references/unattended-production.md`, `skill/templates/learning-design/`
- Modify: `skill/references/learning-design.md`, `skill/references/road-book-mode.md`, `skill/references/cover-art.md`, `skill/references/frontier-manuscript-pipeline.md`, `skill/references/narration-style.md`, `skill/references/voice-design.md`, `skill/references/curriculum-patterns.md`, `skill/references/declaudification.md`, `skill/references/humanizer-pass.md`
- Create: `tests/test_reference_trim.py`

**Interfaces:**
- Consumes: the reference list cited by Task 4's SKILL.md — every path named there must still exist after this task.
- Produces: trimmed references. Task 6 receives the receipt/sync prose lifted out of `cover-art.md`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_reference_trim.py`:

```python
from __future__ import annotations

import unittest
from pathlib import Path

REPO = Path(__file__).parents[1]
REFS = REPO / "skill" / "references"

SURVIVING = (
    "narration-style.md", "voice-design.md", "cover-art.md",
    "curriculum-patterns.md", "declaudification.md", "humanizer-pass.md",
    "frontier-manuscript-pipeline.md", "road-book-mode.md", "learning-design.md",
)

RETIRED_VOCABULARY = (
    "unattended-first-listen",
    "governed-final",
    "public-first-listen",
    "comprehension pilot",
    "learning receipt",
    "package-or-blocker",
)


class ReferenceTrimTests(unittest.TestCase):
    def test_surviving_references_exist(self) -> None:
        for name in SURVIVING:
            self.assertTrue((REFS / name).is_file(), f"missing reference: {name}")

    def test_retired_reference_and_templates_are_gone(self) -> None:
        self.assertFalse((REFS / "unattended-production.md").exists())
        self.assertFalse((REPO / "skill" / "templates" / "learning-design").exists())

    def test_surviving_references_drop_retired_vocabulary(self) -> None:
        for name in SURVIVING:
            text = (REFS / name).read_text(encoding="utf-8")
            for banned in RETIRED_VOCABULARY:
                self.assertNotIn(banned, text, f"{name} still teaches {banned!r}")

    def test_skill_only_cites_references_that_exist(self) -> None:
        skill = (REPO / "skill" / "SKILL.md").read_text(encoding="utf-8")
        for line in skill.splitlines():
            if "references/" in line and ".md" in line:
                for token in line.replace("`", " ").replace("(", " ").replace(")", " ").split():
                    if token.startswith("references/") and token.endswith(".md"):
                        self.assertTrue(
                            (REFS / token.split("/", 1)[1]).is_file(),
                            f"SKILL.md cites missing {token}",
                        )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && /usr/local/bin/python3 -m unittest tests.test_reference_trim -v
```

Expected: `test_retired_reference_and_templates_are_gone` and `test_surviving_references_drop_retired_vocabulary` FAIL.

- [ ] **Step 3: Delete the production-mode contract and schema starters**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && git rm -r skill/references/unattended-production.md skill/templates/learning-design
```

- [ ] **Step 4: Trim `learning-design.md`**

This is the heaviest trim: 376 lines down to roughly 120. **Keep** the argument-level outline definition, the chapter teaching-plan shape (durable outcome, definition, mechanism, concrete case, misconception, expected ability), and the blind sequential beginner review procedure. **Remove** every schema-v2 JSON record and its field list, the comprehension pilot and its `continue`/`revise` contract, the `waived-by-listener` status, all receipts and hash binding, the scope-history rule, and the `revisionMode` schema field.

The coverage ledger goes entirely — the spec drops it.

The `revisionMode` intent survives as the preserve-on-revision rule in SKILL.md's redo loop, not as a validated field here.

- [ ] **Step 5: Trim `road-book-mode.md`**

**Keep** the driving/delivery listening context, the concept and working-memory budgets, and the optional-study boundary. **Remove** the pilot, the human-comprehension-authority language, the `first-edition-plus` mode machinery, and the blind-review duplication now living in `learning-design.md`.

- [ ] **Step 6: Lift the publishing prose out of `cover-art.md`**

**Keep** the style menu, genre calibration, the copy-ready image-generation prompt, the art-and-type brief, `render_cover_pair(...)`, and the selection rubric. **Cut and set aside** — this text goes into Task 6's new file, so save it now — the `cover_receipts.py select-pair` commands, `--selection-source` values, `--privacy-classification`, `--permission-to-publish`, `cover_receipts.py verify`, and the whole `sync_selected_cover.py` dry-run/apply/supersede/unreceipted section.

Replace what you cut with one line pointing at `references/publishing-a-public-edition.md`, matching the pointers Task 3 Step 5 already put at lines 97 and 418.

- [ ] **Step 7: Trim the remaining six references**

`frontier-manuscript-pipeline.md` — keep the frontier-author / cheaper-worker role contract, the continuity ledger, and the citation-first review format; remove the artifact-binding and hash requirements.

`narration-style.md`, `voice-design.md`, `curriculum-patterns.md`, `declaudification.md`, `humanizer-pass.md` — keep the craft whole. Remove only sentences that require a deleted receipt or name a retired production mode. `declaudification.md` keeps the phrase families and density limits and keeps `prose_qc.py --fail-on-style`; it loses the hash-bound `research/prose-style-receipt.json` requirement.

- [ ] **Step 8: Run the trim test to verify it passes**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && /usr/local/bin/python3 -m unittest tests.test_reference_trim -v
```

Expected: `Ran 4 tests` / `OK`.

- [ ] **Step 9: Run the full suite**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && /usr/local/bin/python3 -m unittest discover tests 2>&1 | tail -25
```

Expected: still only `test_skill_prose_contract.py` and `test_skill_cover_contract.py` failing, retargeted in Task 7. If a cover or prose *tooling* test now fails, a trim went too far into a live command — restore that text.

- [ ] **Step 10: Commit**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && git add -A && git commit -m "refactor: trim the craft references to craft

Keep what makes the prose better: argument outlines, chapter teaching
plans, blind review, narration style, voice design, de-Claudification,
the humanizer.

Drop the schema-v2 records, the comprehension pilot, the coverage ledger,
the production-mode contract, and the receipt binding. Publishing prose
moves out of cover-art.md in the next commit.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 6: Park the publishing tooling

`cover_receipts.py`, `sync_selected_cover.py`, `verify_public_first_listen.py`, and `replace_m4b_cover.py` keep working and keep their tests. They get one reference doc and no place in the private lane.

**Files:**
- Create: `skill/references/publishing-a-public-edition.md`
- Create: `tests/test_publishing_reference.py`

**Interfaces:**
- Consumes: the receipt and sync prose set aside in Task 5 Step 6; the pointers written in Task 3 Step 5.
- Produces: `skill/references/publishing-a-public-edition.md`, cited by `cover-art.md:97` and `:418`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_publishing_reference.py`:

```python
from __future__ import annotations

import unittest
from pathlib import Path

REPO = Path(__file__).parents[1]
DOC = REPO / "skill" / "references" / "publishing-a-public-edition.md"
SCRIPTS = REPO / "skill" / "scripts"


class PublishingReferenceTests(unittest.TestCase):
    def test_parked_scripts_still_exist(self) -> None:
        for name in (
            "cover_receipts.py",
            "sync_selected_cover.py",
            "verify_public_first_listen.py",
            "replace_m4b_cover.py",
        ):
            self.assertTrue((SCRIPTS / name).is_file(), f"parked script missing: {name}")

    def test_reference_exists_and_covers_the_parked_flow(self) -> None:
        text = DOC.read_text(encoding="utf-8")
        for needle in (
            "cover_receipts.py",
            "select-pair",
            "--selection-source user",
            "--privacy-classification",
            "--permission-to-publish",
            "sync_selected_cover.py",
            "--intent reuse",
            "--apply",
            "verify_public_first_listen.py",
        ):
            self.assertIn(needle, text, f"publishing reference missing {needle!r}")

    def test_reference_states_it_is_not_the_private_lane(self) -> None:
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("not used when making a book for yourself", text)

    def test_cover_art_points_here(self) -> None:
        cover_art = (REPO / "skill" / "references" / "cover-art.md").read_text(encoding="utf-8")
        self.assertIn("publishing-a-public-edition.md", cover_art)

    def test_skill_does_not_route_the_private_lane_through_publishing(self) -> None:
        skill = (REPO / "skill" / "SKILL.md").read_text(encoding="utf-8")
        for banned in ("sync_selected_cover.py", "cover_receipts.py", "verify_public_first_listen.py"):
            self.assertNotIn(banned, skill, f"SKILL.md still routes through {banned}")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && /usr/local/bin/python3 -m unittest tests.test_publishing_reference -v
```

Expected: FAIL — the reference file does not exist yet.

- [ ] **Step 3: Write the publishing reference**

Create `skill/references/publishing-a-public-edition.md`. Open with a sentence stating this flow is **not used when making a book for yourself** — it applies only when promoting a finished private book into the public `books/` directory or the site.

Then reassemble, from the text set aside in Task 5 Step 6:

- the paired selection receipt: `cover_receipts.py select-pair` with `--selection-source user` (or `requested-mix`), `--privacy-classification`, and the rule for when `--permission-to-publish` may be passed;
- the post-embed check: `cover_receipts.py verify --cover ... --m4b-cover ... --epub ... --m4b ...`;
- the delivery sync: `sync_selected_cover.py --paired-artifact-dir ...` as a dry run first, reading the reported `new` / `reuse` / `supersede` / conflict classification, then the same command with `--intent reuse` and `--apply`; `--intent supersede` only for a newer explicit choice;
- `verify_public_first_listen.py` and what it checks;
- the rule that a narrated Echo M4B is never mutated after export, so `replace_m4b_cover.py` is legacy-artifact compatibility only.

Keep it short. It is a runbook for a rare task, not a governance document.

- [ ] **Step 4: Run the test to verify it passes**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && /usr/local/bin/python3 -m unittest tests.test_publishing_reference -v
```

Expected: `Ran 5 tests` / `OK`.

- [ ] **Step 5: Run the full suite**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && /usr/local/bin/python3 -m unittest discover tests 2>&1 | tail -25
```

Expected: still only the two skill contract tests failing. `test_sync_selected_cover.py`, `test_cover_receipts.py`, `test_verify_public_first_listen.py`, and `test_replace_m4b_cover.py` must all still pass — the scripts are parked, not changed.

- [ ] **Step 6: Commit**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && git add -A && git commit -m "docs: park the public-publishing runbook

The receipt and sync tooling stays working for the rare case of promoting
a finished book into the public repo. It moves into one reference and out
of the private lane, which never touches it.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 7: Rewrite the validator and retarget the remaining contract tests

`tools/validate_skills.py` is the master phrase-pinning validator. It still validates a deleted skill and pins retired vocabulary in `README.md` and `docs/`.

**Files:**
- Modify: `tools/validate_skills.py:53-56`, `:64-70`, `:88-96`, `:113-133`, `:161-186`
- Modify: `tests/test_skill_prose_contract.py`, `tests/test_skill_cover_contract.py`
- Modify: `skills/longform-book-development/SKILL.md` (lines 10, 23, 29, 32, 90, 188, 198, 251), `skills/longform-book-development/references/handoff-packet.md` (lines 4, 13), `docs/make-your-own.md` (lines 8, 20)

**Interfaces:**
- Consumes: the `audiobook` skill name (Task 4); `skills/echo-narration/` (Task 3); `publishing-a-public-edition.md` (Task 6).
- Produces: `validate_skills.py` exiting 0. Task 8 runs it as a release check.

- [ ] **Step 1: Run the validator to see the current failure**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && /usr/local/bin/python3 tools/validate_skills.py; echo "exit=$?"
```

Expected: non-zero exit with a message about `skills/custom-learning-audiobook/SKILL.md` — the file no longer exists.

- [ ] **Step 2: Update the skill roster**

In `tools/validate_skills.py`, replace lines 53-56:

```python
    validate_skill("skill", "explainer-audiobook")
    validate_skill("skills/custom-learning-audiobook", "custom-learning-audiobook")
    validate_skill("skills/longform-book-development", "longform-book-development")
    validate_skill("skills/fiction-book-development", "fiction-book-development")
```

with:

```python
    validate_skill("skill", "audiobook")
    validate_skill("skills/longform-book-development", "longform-book-development")
    validate_skill("skills/fiction-book-development", "fiction-book-development")
```

- [ ] **Step 3: Narrow the paired-cover contract to the publishing lane**

The paired-cover *rendering* survives — an M4B needs a square cover, which is mechanical necessity. The paired *receipt* is publishing-only.

Replace the `paired_contract` loop (lines 64-70) so it checks only the files that still teach cover rendering:

```python
    paired_contract = (
        "exactly three", "1600×2560", "cover.png", "2400×2400", "m4b-cover.png",
    )
    for path in (
        "skill/SKILL.md", "skill/references/cover-art.md",
        "README.md", "docs/how-these-were-made.md", "docs/make-your-own.md",
    ):
        contains(path, *paired_contract)
```

Then move the `complete_paired` command-shape block (lines 74-88) to check only `skill/references/publishing-a-public-edition.md`, and delete the `contains("skills/custom-learning-audiobook/SKILL.md", ...)` assertion at lines 92-96 along with the legacy-marker loop at lines 113-127.

If `README.md`, `docs/how-these-were-made.md`, or `docs/make-your-own.md` no longer carry a needle, update the doc rather than dropping the assertion — those files describe how the published books were actually made and should stay accurate.

- [ ] **Step 4: Replace the retired skill-body assertions**

Delete the `contains("skills/custom-learning-audiobook/SKILL.md", ...)` block (lines 138-150) and the two `contains("skills/custom-learning-audiobook/references/...", ...)` blocks (lines 161-172), plus the `agents/openai.yaml` assertion (lines 173-176).

Update the `contains("skill/SKILL.md", ...)` block (lines 128-137) to the vocabulary the new skill actually uses. Remove `"load the `humanizer` skill"` only if the new SKILL.md phrases it differently; otherwise keep every needle that still holds.

Add an assertion for the new narration reference:

```python
    contains(
        "skills/echo-narration/references/narrating.md",
        "echo-cli",
        "--voice am_michael",
        "<slug>.alignment.json",
        "ffprobe",
    )
```

- [ ] **Step 5: Update the longform handoff pointers**

In `skills/longform-book-development/SKILL.md`, replace every `custom-learning-audiobook` with `audiobook` at lines 10, 23, 29, 32, 188, 198, and 251. Line 90 references the run folder `.build/custom-learning-audiobooks/<slug>/` — **leave that path unchanged**, it is the run-root convention this plan does not touch, but update the surrounding sentence to say `audiobook` creates it.

In `skills/longform-book-development/references/handoff-packet.md`, replace `$custom-learning-audiobook` with `$audiobook` at lines 4 and 13.

Then update the validator's longform assertion at lines 177-186, changing the `"custom-learning-audiobook"` needle to `"audiobook"` and `"$custom-learning-audiobook"` to `"$audiobook"`.

- [ ] **Step 6: Update `docs/make-your-own.md`**

Line 8 links to the deleted skill; line 20 gives the install symlink command. Replace both so the doc describes one skill:

```bash
ln -s "$(pwd)/skill" ~/.claude/skills/audiobook
```

Remove the `custom-learning-audiobook` symlink line entirely.

- [ ] **Step 7: Retarget the two failing contract tests**

`tests/test_skill_prose_contract.py` and `tests/test_skill_cover_contract.py` assert phrases in the old skill bodies. For each: drop every assertion naming `skills/custom-learning-audiobook`, drop assertions about receipts and selection sources, and keep assertions about prose QC and cover *rendering* that still describe live behaviour. Where an assertion covers publishing, retarget it to `skill/references/publishing-a-public-edition.md`.

Do not delete either file. Both cover behaviour that still exists.

- [ ] **Step 8: Run the validator**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && /usr/local/bin/python3 tools/validate_skills.py; echo "exit=$?"
```

Expected: `validate_skills: clean` and `exit=0`.

- [ ] **Step 9: Run the full suite**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && /usr/local/bin/python3 -m unittest discover tests 2>&1 | tail -20
```

Expected: `OK (skipped=6)` — the first fully green suite since Task 4.

- [ ] **Step 10: Commit**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && git add -A && git commit -m "test: retarget the skill contracts to the audiobook skill

validate_skills.py validated a deleted skill and pinned retired
vocabulary. Narrow the paired-cover contract to rendering, move the
command-shape pins to the publishing reference, and repoint the longform
handoff at \`audiobook\`.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 8: Migrate the install and verify end to end

Unit tests confirm the tooling works. Only a real book confirms the workflow does.

**Files:**
- Modify after merge: `~/.claude/skills/` and `~/.agents/skills/` symlinks
  (outside the repo)
- Modify: `README.md` if it names the retired skills

**Interfaces:**
- Consumes: everything from Tasks 1-7.
- Produces: a working `audiobook` skill in both hosts and, when Dan's standing
  authorization is recorded, a real book in the iCloud Books folder.

- [ ] **Step 1: Confirm the full suite and validator are green**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && /usr/local/bin/python3 -m unittest discover tests 2>&1 | tail -5 && /usr/local/bin/python3 tools/validate_skills.py
```

Expected: `OK (skipped=6)` and `validate_skills: clean`. Do not proceed past a failure.

- [ ] **Step 2: Check `README.md` for retired skill names**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && grep -n "explainer-audiobook\|custom-learning-audiobook" README.md
```

If either name appears as a live instruction (an install command, a "use this skill" pointer), update it to `audiobook`. Leave prose describing how already-published books were made — that is a historical record and is accurate.

- [ ] **Step 3: Migrate the symlinks**

These live outside the repo and are not covered by any test.

After merge, inspect each exact retired path and its target. Remove only a
confirmed symlink, then create the new link; do not recursively delete anything:

```bash
for skill_host in "$HOME/.claude/skills" "$HOME/.agents/skills"; do
  test -d "$skill_host"
  for retired in explainer-audiobook custom-learning-audiobook; do
    retired_path="$skill_host/$retired"
    if test -L "$retired_path"; then
      readlink "$retired_path"
      unlink "$retired_path"
    elif test -e "$retired_path"; then
      printf 'refusing non-symlink path: %s\n' "$retired_path" >&2
      exit 1
    fi
  done
  test ! -e "$skill_host/audiobook" && test ! -L "$skill_host/audiobook"
  ln -s /Users/dfakkeldy/Developer/explainer-audiobooks/skill \
    "$skill_host/audiobook"
  ls -ld "$skill_host/audiobook"
done
```

Note the symlink targets the **main checkout**, not this worktree. Until this branch merges, the linked skill is still the old one — expected, and the reason Step 5's end-to-end run happens after merge.

- [ ] **Step 4: Commit the docs updates**

```bash
cd /Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/kind-pascal-8b42e3 && git add -A && git commit -m "docs: point the install at the audiobook skill

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

If Step 2 found nothing to change, skip this step rather than making an empty commit.

- [ ] **Step 5: End-to-end acceptance — make a real book**

After this branch merges to `main`, record
`delivery_authorization: standing-dan-private-workflow` in the brief before
using Dan's iCloud `BOOK_ROOT`, then ask for a short real book (target ~1 hour,
so the run is quick) and confirm every one of these:

1. Exactly five questions asked, in one batch.
2. A one-line plan stated, and the run continues **without waiting** for a reply.
3. No prompt for approval anywhere between intake and delivery.
4. `~/Library/Mobile Documents/com~apple~CloudDocs/Books/<Book Title>/` exists and contains `<Book Title>.epub`, `<Book Title>.m4b`, `cover.png`, and `source/` holding `brief.md`, `outline.md`, `research.md`, `chapters/`, and `feedback.md`.
5. No receipt files anywhere in the delivered folder — no `*-receipt.json`, no `cover-selection.json`, no `unattended-decisions.json`.
6. The EPUB opens and the M4B plays with chapter markers.

For any generic installation or other user, run this acceptance at an absolute
local `BOOK_ROOT`; do not copy to iCloud unless that user explicitly opts in.

- [ ] **Step 6: End-to-end acceptance — redo it**

Give one piece of feedback on the book from Step 5 ("chapter 2 dragged"), then confirm:

1. The book is found by name from a cold session, with no re-interviewing.
2. `source/feedback.md` records the date, what was said, and what changed.
3. The prior version is in `previous/`.
4. The current EPUB and M4B are replaced in place under the same name — no new folder, no `- Revised` suffix.
5. What was working elsewhere in the book survived the revision.

- [ ] **Step 7: Record the known downstream break**

`tools/validate_custom_learning_skill_install.py` was deleted in Task 3. The Hermes copy of `custom-learning-audiobook` is a downstream consumer of the skill this plan removes and needs its own follow-up. Report this to the user; it is out of scope here.

Also report that the KB section still owed for the prior-edition rule (`kb-prior-edition-rule-gap`) now describes a `revisionMode` schema field that no longer exists. It needs restating against the preserve-on-revision practice in the redo loop.

---

## Verification Summary

| Check | Command | Expected |
|---|---|---|
| Full suite | `/usr/local/bin/python3 -m unittest discover tests` | `OK (skipped=6)` |
| Skill validator | `/usr/local/bin/python3 tools/validate_skills.py` | `validate_skills: clean` |
| Skill is lean | `wc -l skill/SKILL.md` | under 200 |
| No stale paths | `grep -rn "custom-learning-audiobook\b" tests tools skill skills README.md` | no output |
| Real book | Task 8 Steps 5-6 | all criteria met |

The full suite and validator are necessary but not sufficient. The acceptance test is a book in the Books folder that was made without a single approval pause, and a redo that improved it without losing what worked.
