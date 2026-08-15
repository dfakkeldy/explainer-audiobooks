# High-Key Cover Slate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bias every new three-pair cover slate toward high-key art, guarantee
one genuine high-key Designed flat graphic, preserve an unrestricted candidate
that may be dark, and repair two pre-existing public-method documentation
contracts.

**Architecture:** This is an instruction-contract change, not a rendering-system
change. Focused unittest assertions define the required prose behavior;
`skill/references/cover-art.md` owns the detailed slate, prompt, rejection, and
selection rules, while `skill/SKILL.md` carries the concise production summary.
The repository validator pins the shared skill surfaces. A separate first task
repairs the two already-failing documentation anchors without changing behavior.

**Tech Stack:** Markdown skill instructions; Python standard-library
`unittest`; `tools/validate_skills.py`; Git.

## Global Constraints

- Work in
  `/Users/dfakkeldy/Developer/explainer-audiobooks/.worktrees/cover-high-key-bias`
  on branch `codex/cover-high-key-bias`.
- Use `/usr/local/bin/python3` for every Python command.
- Preserve exactly three coordinated portrait/square pairs: `cover.png` at
  1600×2560 and `m4b-cover.png` at 2400×2400.
- At least two complete pairs are intentionally high-key.
- One high-key pair is a genuine Designed flat graphic; a Typographic graphic
  system does not satisfy that slot.
- The third pair is tonally unrestricted and may be dark, high-key, or
  intermediate. Never manufacture a dark direction merely to fill a slot.
- High-key means luminous and open, not white-only, pastel, washed out,
  low-contrast, or timid.
- High-key is a tie-breaker, not a ban: a clearly stronger dark pair may win
  when the reported reason explains why it earned the choice.
- Do not change renderers, schemas, receipts, existing covers, book packages,
  narration commands, publication behavior, or dependencies.
- Preserve unrelated work and do not modify the canonical checkout's existing
  `CLAUDE.md` change.

---

## File Structure

- `docs/how-these-were-made.md`: public explanation only; restore two canonical
  contract phrases while retaining current semantics.
- `tests/test_skill_cover_contract.py`: focused behavioral prose contracts for
  the candidate slate, high-key definition, prompt, review, and dark-cover
  escape hatch.
- `skill/references/cover-art.md`: detailed source of truth for cover direction,
  prompt construction, rendering review, rejection, and selection.
- `skill/SKILL.md`: concise top-level production instruction that must expose
  the slate and selection bias before delegating to the reference.
- `tools/validate_skills.py`: repository-level guard that requires the core
  high-key slate markers in both shared skill surfaces.

---

### Task 1: Restore the Public-Method Documentation Contracts

**Files:**
- Modify: `docs/how-these-were-made.md:105-127`
- Test: `tests/test_skill_cover_contract.py:94-107,152-157`

**Interfaces:**
- Consumes: the existing exact-string assertions
  `public/iCloud/site sync` and `governed Echo wrapper embeds`.
- Produces: green baseline public-method contract tests; no production behavior
  or command changes.

- [ ] **Step 1: Reproduce the two known failures**

Run:

```bash
/usr/local/bin/python3 -m unittest \
  tests.test_skill_cover_contract.SkillCoverContractTests.test_docs_distinguish_private_default_from_public_promotion \
  tests.test_skill_cover_contract.SkillCoverContractTests.test_public_method_uses_wrapper_embedding_not_post_echo_replacement \
  -v
```

Expected: two failures. The first reports missing `public/iCloud/site sync`;
the second reports missing `governed Echo wrapper embeds`.

- [ ] **Step 2: Restore the Echo embedding phrase**

Replace:

```markdown
and combined Markdown from the reviewed chapters. The governed Echo wrapper
narrates the selected square art into an immutable chaptered M4B and produces
alignment data for read-along playback.
```

with:

```markdown
and combined Markdown from the reviewed chapters. The governed Echo wrapper embeds
the selected square art while narrating an immutable chaptered M4B and produces
alignment data for read-along playback.
```

- [ ] **Step 3: Restore the governed synchronization phrase**

Replace:

```markdown
  square art changes, the M4B is re-narrated rather than patched. The EPUB,
  M4B, covers, alignment, and receipts are verified before governed public,
  iCloud, or site sync.
```

with:

```markdown
  square art changes, the M4B is re-narrated rather than patched. The EPUB,
  M4B, covers, alignment, and receipts are verified before governed
  public/iCloud/site sync.
```

- [ ] **Step 4: Verify the repaired baseline tests**

Run the command from Step 1 again.

Expected: `Ran 2 tests` and `OK`.

- [ ] **Step 5: Commit the bounded repair**

```bash
git add docs/how-these-were-made.md
git commit -m "fix(docs): restore public cover workflow contracts"
```

---

### Task 2: Contract-Test and Implement the High-Key Candidate Slate

**Files:**
- Modify: `tests/test_skill_cover_contract.py:159-194`
- Modify: `skill/references/cover-art.md:95-251,282-300`
- Modify: `skill/SKILL.md:138-146`
- Modify: `tools/validate_skills.py:255-263,313-320`

**Interfaces:**
- Consumes: the existing three-pair rendering contract and qualitative
  selection rubric.
- Produces: the exact shared markers `At least two of the three complete pairs
  must be intentionally high-key`, `one of those high-key pairs must be a
  Designed flat graphic`, and `The third candidate is tonally unrestricted`.
  Detailed prompt and review behavior remains owned by `cover-art.md`.

- [ ] **Step 1: Replace the obsolete flat-or-type-led assertion and add failing slate tests**

In `test_route_parity_and_flat_graphic_slot`, replace:

```python
        for marker in (
            "Designed flat graphic",
            "route follows the direction",
            "flat graphic or type-led direction",
        ):
```

with:

```python
        for marker in (
            "Designed flat graphic",
            "route follows the direction",
        ):
```

Add `"flat graphic or type-led direction"` to that method's `stale` tuple.
Then add these methods after `test_route_parity_and_flat_graphic_slot`:

```python
    def test_candidate_slate_biases_high_key_and_requires_flat_graphic(self) -> None:
        for key in ("cover", "skill"):
            text = self.flattened(key)
            for marker in (
                "At least two of the three complete pairs must be intentionally high-key",
                "one of those high-key pairs must be a Designed flat graphic",
                "The third candidate is tonally unrestricted",
            ):
                with self.subTest(file=key, marker=marker):
                    self.assertIn(marker, text)

    def test_high_key_is_a_reviewed_visual_contract_not_a_label(self) -> None:
        text = self.flattened("cover")
        for marker in (
            "High-key means that the overall impression is luminous and open",
            "does not mean white-only, pastel, washed out, low-contrast",
            "`high-key` or `tonally unrestricted`",
            "both its portrait and square renders",
            "revised or regenerated",
            "[TONAL INTENT: HIGH-KEY / TONALLY UNRESTRICTED]",
            "High-key treatment is the tie-breaker",
            "darker direction earned the choice",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)
```

- [ ] **Step 2: Run the focused tests and verify the new contract is red**

Run:

```bash
/usr/local/bin/python3 -m unittest tests.test_skill_cover_contract -v
```

Expected: the two new high-key tests fail on missing markers, and the updated
route test fails because the old `flat graphic or type-led direction` wording
is still present. The two Task 1 public-method tests remain green.

- [ ] **Step 3: Replace the old candidate-slot paragraph in `cover-art.md`**

Replace:

```markdown
Choose the three most appropriate directions from this menu. Do not use a
weak/placeholder direction just to fill the count. At least one of the three
candidates must be a Designed flat graphic or type-led direction (Typographic
graphic system counts), so a designed, non-generated look is always offered.
```

with:

```markdown
Choose the three most appropriate directions from this menu. Do not use a
weak/placeholder direction just to fill the count. At least two of the three
complete pairs must be intentionally high-key, and one of those high-key pairs
must be a Designed flat graphic. A Typographic graphic system remains available
but does not satisfy the flat-graphic slot. The third candidate is tonally
unrestricted: it may be dark, high-key, or intermediate according to the subject
and central metaphor. Do not manufacture a dark candidate merely to fill a slot.
```

- [ ] **Step 4: Add tonal calibration before the candidate brief**

Immediately before `## Candidate Brief Before Making Art`, insert:

```markdown
### Tonal Calibration

High-key means that the overall impression is luminous and open, built mainly
from middle and high values. It may use saturated colour, firm typography,
strong silhouettes, and dark accents. It does not mean white-only, pastel,
washed out, low-contrast, or visually timid.

Declare each candidate's tonal intent as `high-key` or `tonally unrestricted`
before making art. A pair counts as high-key only when both its portrait and
square renders retain that luminous value structure at full size and thumbnail
size. If a planned high-key direction resolves into a predominantly dark render,
it is revised or regenerated before selection rather than relabeled after the
fact.
```

- [ ] **Step 5: Add tonal intent to the complete candidate brief**

Replace the current ten-item brief with:

```markdown
1. Audience promise.
2. Central metaphor.
3. Composition, crop, and intended title field.
4. Material language and two-to-four-colour palette.
5. Tonal intent: `high-key` or `tonally unrestricted`.
6. Anti-brief.
7. Title archetype and font roles.
8. Planned line breaks and hierarchy.
9. Title anchor, alignment, and approximate occupied area.
10. Intended relationship between title and art.
11. Subtitle, author, and AUDIOBOOK placement.
```

- [ ] **Step 6: Add tonal intent to the copy-ready image prompt**

After the prompt sentence ending in `[ONE SENTENCE VISUAL THESIS].`, add:

```text

The declared tonal intent is [TONAL INTENT: HIGH-KEY / TONALLY UNRESTRICTED].
For a high-key direction, make the overall value structure luminous and open,
using broad middle and high values with saturated colour, clear contrast, and
dark accents rather than a dominant dark field. High-key does not mean pale,
pastel, washed out, or low-contrast. For a tonally unrestricted direction,
follow the brief's intended value structure; a dark field is welcome when the
subject and central metaphor earn it.
```

- [ ] **Step 7: Extend render review and selection behavior**

Replace the final three sentences of `Render, Compare, and Select`:

```markdown
Score the complete pairs on subject specificity, thumbnail legibility, title
hierarchy, portrait/square coherence, absence of defects, and distinctiveness.
Select and report the strongest. A later request to mix directions becomes a new
specification and render.
```

with:

```markdown
Score the complete pairs on subject specificity, thumbnail legibility, title
hierarchy, portrait/square coherence, absence of defects, and distinctiveness.
Confirm that both declared high-key pairs remain high-key in their portrait and
square renders and thumbnails. High-key treatment is the tie-breaker between
similarly strong pairs. A clearly stronger dark or intermediate pair may still
win; when it does, report why the darker direction earned the choice. A later
request to mix directions becomes a new specification and render.
```

- [ ] **Step 8: Make a dark-rendered high-key candidate rejectable**

In the Award-Worthy Acceptance Bar, after the thumbnail-collapse bullet, add:

```markdown
- was declared high-key but resolves into a predominantly dark portrait or
  square render;
```

- [ ] **Step 9: Put the same slate contract in the top-level skill**

Replace `skill/SKILL.md` lines 140-146 with:

```markdown
Design exactly three coordinated cover pairs with
`references/cover-art.md`. At least two of the three complete pairs must be
intentionally high-key, and one of those high-key pairs must be a Designed flat
graphic. The third candidate is tonally unrestricted and may be dark when its
subject and central metaphor earn that treatment. Render each with
`render_cover_pair(...)`: `cover.png` at 1600×2560 for the EPUB portrait and
`m4b-cover.png` at 2400×2400 for the M4B square.

Review full-size art and thumbnails and auto-select the best pair on subject
specificity, thumbnail legibility, title hierarchy, portrait/square coherence,
absence of defects, and distinctiveness. High-key treatment breaks a close tie;
a clearly stronger darker pair may win when the reported choice explains why.
Report the choice rather than asking.
```

- [ ] **Step 10: Pin the core markers in the repository validator**

After the existing `paired_contract` loop in `tools/validate_skills.py`, add:

```python
    cover_slate_contract = (
        "At least two of the three complete pairs must be intentionally high-key",
        "one of those high-key pairs must be a Designed flat graphic",
        "The third candidate is tonally unrestricted",
    )
    for path in ("skill/SKILL.md", "skill/references/cover-art.md"):
        contains(path, *cover_slate_contract)
    contains(
        "skill/references/cover-art.md",
        "[TONAL INTENT: HIGH-KEY / TONALLY UNRESTRICTED]",
        "High-key treatment is the tie-breaker",
        "darker direction earned the choice",
    )
```

- [ ] **Step 11: Run the focused cover contracts and skill validator**

Run:

```bash
/usr/local/bin/python3 -m unittest tests.test_skill_cover_contract -v
/usr/local/bin/python3 tools/validate_skills.py
```

Expected: all cover-contract tests pass and the validator prints
`validate_skills: clean`.

- [ ] **Step 12: Commit the high-key candidate contract**

```bash
git add tests/test_skill_cover_contract.py skill/references/cover-art.md \
  skill/SKILL.md tools/validate_skills.py
git commit -m "feat: bias audiobook covers toward high-key art"
```

---

### Task 3: Run Repository Verification and Prepare Handoff

**Files:**
- Verify only; no planned file changes.

**Interfaces:**
- Consumes: the two implementation commits from Tasks 1 and 2.
- Produces: evidence that the repository's skill and Python contracts pass and
  that the task worktree contains no uncommitted agent-authored changes.

- [ ] **Step 1: Run the full unittest suite**

```bash
/usr/local/bin/python3 -m unittest discover -s tests -v
```

Expected: all tests pass. Do not normalize or ignore a failure. If a failure is
caused by the task, fix the smallest task-scoped defect and amend the Task 1 or
Task 2 commit as appropriate. If it is unrelated and newly introduced upstream,
stop and report the exact failure.

- [ ] **Step 2: Run skill validation**

```bash
/usr/local/bin/python3 tools/validate_skills.py
```

Expected: `validate_skills: clean`.

- [ ] **Step 3: Check whitespace and patch integrity**

```bash
git diff --check origin/main...HEAD
```

Expected: no output and exit status 0.

- [ ] **Step 4: Inspect the final branch and worktree state**

```bash
git status --short --branch
git log --oneline --decorate origin/main..HEAD
```

Expected: a clean `codex/cover-high-key-bias` worktree, with the design commit,
the public-method contract repair, and the high-key cover contract commits ahead
of `origin/main`.

- [ ] **Step 5: Hand off for the repository's publication workflow**

Report the exact verification results and commit IDs. Successful requested
implementation is then ready for push and a ready pull request; do not claim CI,
merge, deployment, book regeneration, delivery, or human cover acceptance.
