# No-Table Cover Compositions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace generic tabletop cover staging with surface-free composition
recipes while preserving a narrow, pre-declared exception when a table-like
surface is genuinely required by the book's subject or central visual thesis.

**Architecture:** This is an instruction-contract change. Focused unittest
assertions define the required direction, brief field, prompt shape, exception,
review, and rejection behavior; `skill/references/cover-art.md` supplies the
minimal prose implementation, and `tools/validate_skills.py` pins stable
markers. Fresh-context skill pressure tests establish the current failure before
the edit and verify the revised instructions after it without changing renderers
or schemas.

**Tech Stack:** Markdown skill instructions; Python standard-library
`unittest`; `tools/validate_skills.py`; fresh-context agent pressure tests; Git.

## Global Constraints

- Work in
  `/Users/dfakkeldy/Developer/explainer-audiobooks/.worktrees/cover-surface-exception`
  on branch `codex/cover-surface-exception`.
- Use `/usr/local/bin/python3` for every Python command.
- Generic tables, desks, workbenches, counters, tabletops, desktops, and
  books/documents/papers spread across a surface are forbidden. Flat lays and
  overhead prop arrangements are forbidden regardless of any declaration.
- A table-like surface is allowed only when the pre-generation candidate brief
  declares that the book's subject or indispensable central visual thesis
  requires that exact surface.
- Convenience, realism, available negative space, “people work at desks,” and
  arranging several props are not valid exceptions.
- An accidental surface cannot be justified after rendering; discard and
  regenerate the complete candidate pair.
- Preserve exactly three coordinated portrait/square pairs, the two-high-key
  slate, the genuine Designed flat graphic slot, and the tonally unrestricted
  third candidate.
- Do not change renderers, cover schemas, receipts, existing covers, book
  packages, narration, delivery, publication, or dependencies.
- Keep generated artwork text-free and preserve the existing anti-AI prompt.
- Use `/Users/dfakkeldy/Developer/explainer-audiobooks/.worktrees/cover-surface-exception/.superpowers/sdd/2026-08-16-no-table-cover-compositions/skill-pressure/`
  for pressure-test reports. This is git-ignored task evidence, not repository
  content.

---

## File Structure

- `tests/test_skill_cover_contract.py`: focused contract tests for surface-free
  directions, the pre-declared exception, prompt/review behavior, and removal of
  stale still-life cues.
- `skill/references/cover-art.md`: single source of truth for cover direction,
  candidate briefs, generated-art prompts, visual review, and rejection.
- `tools/validate_skills.py`: repository validator requiring the stable
  surface-free markers and rejecting stale positive cues.
- `.superpowers/sdd/2026-08-16-no-table-cover-compositions/skill-pressure/`:
  ignored RED/GREEN fresh-agent reports used to verify the skill as behavior,
  not only as text.

---

### Task 1: Establish RED and Implement the Surface-Free Skill Contract

**Files:**
- Modify: `tests/test_skill_cover_contract.py:158-221`
- Modify: `skill/references/cover-art.md:107-171,200-326`
- Modify: `tools/validate_skills.py:264-277`
- Create ignored evidence:
  `.superpowers/sdd/2026-08-16-no-table-cover-compositions/skill-pressure/red-1.md`
  through `red-5.md`

**Interfaces:**
- Consumes: the existing `flattened("cover")` test helper, three-pair cover
  contract, high-key contract, flat-graphic contract, and copy-ready generated
  artwork prompt.
- Produces: exact markers `Environmental documentary detail`,
  `Surface exception: none`, `[SURFACE EXCEPTION: NONE / EXACT SUBJECT-DRIVEN
  REASON]`, `cannot be justified after rendering`, and `discard and
  regenerate`; removes `Documentary still life` and `WIDE STILL LIFE` from the
  active cover reference.

- [ ] **Step 1: Run five fresh-context RED pressure samples against the unmodified skill**

Dispatch five fresh agents independently. Each agent reads the current
`skill/references/cover-art.md` and receives exactly this prompt:

```text
Read skill/references/cover-art.md and follow it exactly. Produce exactly three
complete candidate art-and-type briefs for a premium nonfiction audiobook titled
The Paper Trail: How Municipal Records Move. The audience is a curious beginner;
the promise is to make document intake, indexing, retention, retrieval, and
handoff understandable. Do not create images. For each candidate, include its
direction, central metaphor, composition, tonal intent, planned title field,
material language, palette, anti-brief, typography strategy, and rationale.
Do not use any context outside the reference and this request.
```

Write the five complete responses to `red-1.md` through `red-5.md`. Score each
response with this fixed rubric:

```text
FAIL when any candidate uses or proposes a table, desk, workbench, counter,
tabletop, desktop, flat lay, overhead prop arrangement, or books/documents/papers
spread across a surface; or when the brief lacks a pre-generation surface
exception field. PASS only when all three candidates avoid those compositions
and explicitly declare the exception state.
```

Expected RED: at least one failure. The unmodified reference explicitly offers
`Documentary still life` and `WIDE STILL LIFE` and has no surface-exception
field. Record the five verdicts and exact offending phrases in the Task 1 report.
If all five unexpectedly pass, stop: the fresh-agent control did not reproduce
the behavior and the skill-edit workflow must not proceed without revisiting the
test scenario.

- [ ] **Step 2: Add failing focused contract tests**

Add these two methods after
`test_high_key_is_a_reviewed_visual_contract_not_a_label`:

```python
    def test_surface_free_directions_replace_tabletop_defaults(self) -> None:
        text = self.flattened("cover")
        for marker in (
            "Environmental documentary detail",
            "held, carried, mounted, installed, suspended, worn, operated",
            "full-frame graphic object, held, mounted, installed, or integrated",
            "never laid out as props on furniture",
            "[COMPOSITION: CLOSE CROP / ENVIRONMENTAL DETAIL / HAND-HELD SUBJECT / "
            "FULL-FRAME ARTIFACT / SINGLE FIGURE / DIAGONAL ACTION]",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)
        for stale in ("Documentary still life", "WIDE STILL LIFE"):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, text)

    def test_surface_exception_is_declared_before_art_and_narrowly_reviewed(self) -> None:
        text = self.flattened("cover")
        for marker in (
            "Surface exception: none",
            "book's subject or indispensable central visual thesis",
            "Convenience, realism, available negative space",
            "[SURFACE EXCEPTION: NONE / EXACT SUBJECT-DRIVEN REASON]",
            "No table, no desk, no workbench, no counter, no tabletop, no desktop, "
            "no flat lay, no overhead arrangement",
            "books, documents, or papers spread across a surface",
            "cannot be justified after rendering",
            "discard and regenerate",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)
```

- [ ] **Step 3: Run the focused suite and verify the new tests fail correctly**

```bash
/usr/local/bin/python3 -m unittest tests.test_skill_cover_contract -v
```

Expected: both new tests fail because the new markers are absent; the first
also reports the stale `Documentary still life` or `WIDE STILL LIFE` cue. The 14
pre-existing cover-contract tests remain green.

- [ ] **Step 4: Replace the two surface-producing direction rows**

In `skill/references/cover-art.md`, replace the Documentary and Institutional
rows with:

```markdown
| **Environmental documentary detail** | A real or generated subject encountered in context — held, carried, mounted, installed, suspended, worn, operated, or otherwise in use; visible grain, imperfect natural light, physical specificity, and editorial-film restraint without generic horizontal-surface staging. | History, practical skills, food, place, science, craft |
| **Institutional artifact** | An archival card, blueprint, label, map fragment, lab plate, schematic, or dossier treated as a full-frame graphic object, held, mounted, installed, or integrated into its environment; precise hierarchy, disciplined spacing, singular accent; never laid out as props on furniture. | Technical explainers, research, process, architecture, operations |
```

- [ ] **Step 5: Add the required field to every candidate brief**

Replace the current eleven-item list with:

```markdown
1. Audience promise.
2. Central metaphor.
3. Composition, crop, and intended title field.
4. Material language and two-to-four-colour palette.
5. Tonal intent: `high-key` or `tonally unrestricted`.
6. Surface exception: `none`, or one sentence naming the exact table-like
   surface required by the book's subject or indispensable central visual thesis.
7. Anti-brief.
8. Title archetype and font roles.
9. Planned line breaks and hierarchy.
10. Title anchor, alignment, and approximate occupied area.
11. Intended relationship between title and art.
12. Subtitle, author, and AUDIOBOOK placement.
```

Immediately after the list, add:

```markdown
`Surface exception: none` is the default. A declaration may authorize only that
exact necessary table-like surface. Flat lays and overhead prop arrangements are
forbidden regardless of any declaration. The pre-generation brief must name the
exact surface and explain why the book's subject or indispensable central visual
thesis requires it. Convenience, realism, available negative space, “people work
at desks,” and arranging several props do not qualify. The exception must name
the permitted surface and its semantic role; it does not authorize unrelated desk
props or documents arranged for atmosphere. An accidental surface cannot be
justified after rendering.
```

- [ ] **Step 6: Replace the generated-art composition menu**

Replace:

```text
Use [COMPOSITION: CLOSE CROP / WIDE STILL LIFE /
SINGLE FIGURE / DIAGONAL ACTION]
```

with:

```text
Use [COMPOSITION: CLOSE CROP / ENVIRONMENTAL DETAIL / HAND-HELD SUBJECT /
FULL-FRAME ARTIFACT / SINGLE FIGURE / DIAGONAL ACTION]
```

Keep the surrounding strong-silhouette and title-field instructions unchanged.

- [ ] **Step 7: Add the conditional surface recipe to the generated-art prompt**

After the tonal-intent paragraph and before `Show one unforgettable central
metaphor`, insert:

```text
The declared surface exception is [SURFACE EXCEPTION: NONE / EXACT
SUBJECT-DRIVEN REASON]. When it is NONE, build a surface-free composition: show
the subject held, carried, mounted, installed, suspended, worn, operated, in use,
or treated as a full-frame graphic object in its real environment. No table, no
desk, no workbench, no counter, no tabletop, no desktop, and no books, documents,
or papers spread across a surface. When an exception is declared, show only the
exact permitted table-like surface and make its named semantic role visibly
indispensable to the central metaphor. Flat lays and overhead prop arrangements
are forbidden regardless of any declaration. Do not add unrelated props or
arrange documents for atmosphere.
```

- [ ] **Step 8: Add discard/regenerate behavior after the prompt**

After the paragraph ending `encode all text and layout afterward in each
candidate specification.`, add:

```markdown
If a render introduces an undeclared table-like surface, or any flat lay or
overhead prop arrangement, discard and regenerate the complete candidate pair.
Do not relabel the render or invent a surface exception after seeing it. For a
declared exception, verify only the exact named table-like surface carries the
subject or central metaphor rather than merely holding props.
```

- [ ] **Step 9: Add the surface check to pair review and the acceptance bar**

In `Render, Compare, and Select`, after the high-key confirmation sentence, add:

```markdown
Confirm that every candidate with `Surface exception: none` remains free of
table-like staging in both variants and thumbnails. Confirm that every candidate
is free of flat lays and overhead prop arrangements in both variants and
thumbnails. Review any declared table-like surface in both variants and
thumbnails against its exact pre-generation reason.
```

In the Award-Worthy Acceptance Bar, after the high-key rejection bullet, add:

```markdown
- uses a flat lay or overhead prop arrangement, whether declared or not;
- uses a table, desk, workbench, counter, tabletop, or desktop without an exact
  pre-generation surface exception;
- uses a declared table-like surface merely to hold unrelated props or books,
  documents, or papers spread across a surface;
```

- [ ] **Step 10: Pin the contract in the repository validator**

After the existing detailed `cover_slate_contract` checks in
`tools/validate_skills.py`, add:

```python
    cover_art = "skill/references/cover-art.md"
    section_contains(
        cover_art,
        "Candidate Brief Before Making Art",
        "6. Surface exception: `none`",
        "A declaration may authorize only",
        "Flat lays and overhead prop arrangements are",
    )
    section_contains(
        cover_art,
        "Copy-ready image-generation prompt",
        "[SURFACE EXCEPTION: NONE / EXACT SUBJECT-DRIVEN REASON]",
        "exact permitted table-like surface",
        "Flat lays and overhead prop arrangements",
        "discard and regenerate the complete candidate pair",
    )
    section_contains(
        cover_art,
        "Render, Compare, and Select",
        "flat lays and overhead prop arrangements in both variants and thumbnails",
        "exact pre-generation reason",
    )
    section_contains(
        cover_art,
        "Award-Worthy Acceptance Bar",
        "whether declared or not",
        "exact pre-generation surface exception",
    )
    cover_text = read(cover_art)
    for stale in ("Documentary still life", "WIDE STILL LIFE", "specimen arrangement"):
        require(stale not in cover_text, f"{cover_art} still teaches {stale!r}")
```

- [ ] **Step 11: Run focused GREEN verification**

```bash
/usr/local/bin/python3 -m unittest tests.test_skill_cover_contract -v
/usr/local/bin/python3 tools/validate_skills.py
git diff --check
```

Expected: all cover-contract tests pass; validator prints
`validate_skills: clean`; `git diff --check` emits no output.

- [ ] **Step 12: Commit the contract change**

```bash
git add tests/test_skill_cover_contract.py skill/references/cover-art.md \
  tools/validate_skills.py
git commit -m "feat: avoid generic tabletop cover compositions"
```

---

### Task 2: Verify the Revised Skill Under Fresh-Agent Pressure

**Files:**
- Verify tracked files only; no planned tracked changes.
- Create ignored evidence:
  `.superpowers/sdd/2026-08-16-no-table-cover-compositions/skill-pressure/green-1.md`
  through `green-5.md`
- Create ignored evidence:
  `.superpowers/sdd/2026-08-16-no-table-cover-compositions/skill-pressure/exception.md`

**Interfaces:**
- Consumes: the Task 1 skill commit and the exact RED scenario/rubric.
- Produces: five convergent surface-free briefs for a subject with no valid
  exception, plus one correctly declared exception for a book whose subject is
  the table itself.

- [ ] **Step 1: Run five fresh-context GREEN samples**

Dispatch five new agents independently with the exact RED prompt from Task 1,
now reading the revised `skill/references/cover-art.md`. Write their complete
responses to `green-1.md` through `green-5.md`.

- [ ] **Step 2: Score all five GREEN responses with the unchanged rubric**

Every response must:

```text
- provide exactly three candidate briefs;
- declare Surface exception: none for all three;
- avoid a table, desk, workbench, counter, tabletop, desktop, flat lay,
  overhead prop arrangement, and books/documents/papers spread across a surface;
- use surface-free recipes such as held, carried, mounted, installed, suspended,
  worn, operated, in use, environmental detail, or full-frame artifact.
```

Expected GREEN: five of five responses pass. Record each verdict and its
composition phrases in the Task 2 report. If any response fails, stop the task
as `BLOCKED` with the exact rationalization and response path; do not silently
weaken the acceptance criterion or improvise unplanned skill wording.

- [ ] **Step 3: Verify the legitimate-subject exception once**

Dispatch one fresh agent with this prompt:

```text
Read skill/references/cover-art.md and follow it exactly. Produce exactly three
complete candidate art-and-type briefs for a premium nonfiction audiobook titled
The Table Itself: A Cultural History of Shared Furniture. The book explains how
tables shaped eating, work, negotiation, ritual, and domestic life. Do not create
images. For each candidate, include every field required by the cover reference.
Do not use any context outside the reference and this request.
```

Write the response to `exception.md`. At least one candidate may declare a
specific surface exception because the table is the book's subject. Every other
candidate must still declare `none`; no candidate may use unrelated desk props or
documents arranged for atmosphere. If the agent treats the rule as an absolute
ban or uses a vague convenience exception, stop as `BLOCKED` with the exact
response evidence.

- [ ] **Step 4: Re-run the focused deterministic contracts**

```bash
/usr/local/bin/python3 -m unittest tests.test_skill_cover_contract -v
/usr/local/bin/python3 tools/validate_skills.py
```

Expected: 16 tests pass and `validate_skills: clean`.

No commit is expected for Task 2. Its deliverable is the ignored pressure-test
evidence and report. Any required tracked refinement must return to a revised,
approved plan rather than being invented during pressure testing.

---

### Task 3: Run Full Verification and Prepare Publication Handoff

**Files:**
- Verify only; no planned file changes.

**Interfaces:**
- Consumes: the reviewed Task 1 commit and green pressure-test evidence from
  Task 2.
- Produces: final local verification evidence and a clean branch ready for the
  repository's push-and-PR workflow.

- [ ] **Step 1: Run the full unittest suite**

```bash
/usr/local/bin/python3 -m unittest discover -s tests -v
```

Expected: all tests pass. Identify every conditional skip by test name and exact
reason in the verification report. Do not hide skips behind only an aggregate
count.

- [ ] **Step 2: Run the skill validator**

```bash
/usr/local/bin/python3 tools/validate_skills.py
```

Expected: `validate_skills: clean`.

- [ ] **Step 3: Check the complete patch**

```bash
git diff --check origin/main...HEAD
git status --short --branch
git log --oneline --decorate origin/main..HEAD
```

Expected: no diff-check output; a clean
`codex/cover-surface-exception` worktree; design, plan, and implementation
commits ahead of `origin/main`.

- [ ] **Step 4: Hand off for final review and publication**

Report focused tests, pressure-test verdicts, full-suite results, exact skips,
validator output, branch status, and commit IDs. Do not claim regenerated-cover,
human visual, CI, merge, deployment, narration, delivery, or publication
acceptance. After whole-branch review passes, push the branch and open a ready PR
against `main` under the repository workflow.
