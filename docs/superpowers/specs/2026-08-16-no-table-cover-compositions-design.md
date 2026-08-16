# No-Table Cover Compositions Design

Date: 2026-08-16
Status: Approved design, pending written-spec review
Branch: `codex/cover-surface-exception`

## Problem

The cover workflow repeatedly produces desks, tables, workbenches, flat lays,
and books or documents spread across horizontal surfaces. The pattern is not an
accident outside the instructions: `skill/references/cover-art.md` positively
offers both a **Documentary still life** direction and `WIDE STILL LIFE` as a
prompt composition. When the brief asks for a physical object, artifact,
document, book, tool, or specimen, the image model uses a tabletop as its
generic stage.

The current anti-brief only rejects `laptop-on-desk`. It does not prevent other
desk arrangements, overhead flat lays, or documents and books staged on tables.

## Decision

Generic horizontal-surface staging is forbidden. A table-like surface may
appear only when either:

1. the surface is itself part of the book's subject, such as a book about
   tables; or
2. the surface is indispensable to the candidate's central visual thesis and
   the thesis cannot be represented honestly without it.

The exception must be declared in the candidate brief before art is created.
An accidental table, desk, workbench, counter, or flat lay cannot be justified
after rendering.

Convenience, realism, available negative space, “people work at desks,” and a
desire to arrange several props are not valid exceptions.

## Goals

- Stop tables, desks, workbenches, counters, tabletops, flat lays, and overhead
  prop arrangements from serving as generic cover composition.
- Stop books, papers, dossiers, maps, and documents from being casually spread
  across a horizontal surface.
- Replace the workflow's positive still-life cues with useful surface-free
  composition recipes.
- Preserve a narrow, declared exception when a table-like surface is genuinely
  load-bearing to the subject or central metaphor.
- Pin the behavior in focused tests and the repository skill validator.

## Non-goals

- No retroactive changes to existing covers or finished packages.
- No absolute ban on a table when a declared subject-driven exception applies.
- No computer-vision classifier, automated object detection, or renderer
  changes.
- No changes to the three-pair, high-key, flat-graphic, typography, receipt,
  narration, delivery, or publication contracts.
- No new dependency or schema version.

## Positive Composition Recipe

The current **Documentary still life** direction becomes **Environmental
documentary detail**. It shows the subject encountered in context: held,
carried, mounted, installed, suspended, worn, operated, or otherwise in use.
The direction retains grain, imperfect natural light, physical specificity,
and an editorial-film sensibility, but removes staged horizontal surfaces as
its default setting.

The image-generation prompt removes `WIDE STILL LIFE` from its composition
menu. Its replacement choices emphasize a single subject and environmental
relationship:

- close crop;
- environmental detail;
- hand-held subject;
- full-frame artifact;
- single figure; or
- diagonal action.

An institutional artifact may still be a document, map, archival card,
blueprint, label, lab plate, schematic, or dossier. It must be treated as a
full-frame graphic object, held, mounted, installed, or integrated into its
environment—not laid out as a prop on furniture.

## Candidate Brief Contract

Every candidate brief adds one required field:

```text
Surface exception: none
```

or:

```text
Surface exception: [one sentence naming why the book's subject or indispensable
central visual thesis requires this exact table-like surface]
```

`none` is the normal value. When an exception is present, the generation prompt
must name the permitted surface and its semantic role in the central metaphor.
The exception does not authorize unrelated desk props, a flat lay, or several
documents arranged for atmosphere.

## Prompt and Review Contract

The generated-art prompt will positively request the declared surface-free
composition. It will also explicitly reject a table, desk, workbench, counter,
tabletop, desktop, flat lay, overhead arrangement, or books/documents/papers
spread on a surface when `Surface exception` is `none`.

During full-size and thumbnail review, any undeclared table-like staging causes
the complete candidate pair to be discarded and regenerated. The reviewer may
not relabel the render or invent an exception after seeing it. A declared
exception is reviewed narrowly: the named surface must visibly carry the
subject or central metaphor rather than merely holding props.

## Instruction Changes

`skill/references/cover-art.md` will:

- replace **Documentary still life** with **Environmental documentary detail**;
- tighten **Institutional artifact** against tabletop document staging;
- add the required `Surface exception` field to every candidate brief;
- replace `WIDE STILL LIFE` with the surface-free composition menu;
- add both the positive surface-free recipe and the explicit negative list to
  the copy-ready prompt;
- require regeneration when an undeclared surface appears; and
- add undeclared table-like staging to the Award-Worthy Acceptance Bar.

The top-level `skill/SKILL.md` already delegates all cover design to this
reference and does not carry conflicting composition advice, so it does not
need duplicate wording.

## Test-First Verification

Before changing the skill, record the current failure in two ways:

1. add focused contract assertions for the new direction, brief field, prompt
   composition, explicit rejection list, review rule, and acceptance-bar rule;
   verify they fail against merged `main`; and
2. run a fresh cover-direction pressure scenario against the unmodified skill
   that asks for a document-, artifact-, or tool-centered cover and record
   whether the resulting brief chooses tabletop staging.

After the instruction change, rerun the focused contract tests and the same
pressure scenario. The revised response must choose a surface-free composition
unless the scenario itself supplies a valid subject-driven exception.

`tools/validate_skills.py` will require stable markers for:

- `Environmental documentary detail`;
- `Surface exception: none`;
- the absence of `WIDE STILL LIFE`;
- the no-table prompt contract; and
- rejection and regeneration of an undeclared surface.

Final verification runs the focused cover-contract tests, full unittest
discovery, `tools/validate_skills.py`, and `git diff --check`.

## Acceptance Criteria

1. A normal cover brief declares `Surface exception: none`.
2. No direction or prompt option positively asks for a still life, tabletop,
   desk, workbench, counter, flat lay, or overhead prop arrangement.
3. Documents and books may appear without being staged across furniture.
4. A table-like surface is permitted only when the pre-generation brief names
   a subject-driven or indispensable-metaphor exception.
5. An undeclared surface causes discard and regeneration; it cannot be
   justified after rendering.
6. Existing high-key, flat-graphic, paired-cover, rendering, narration, and
   publication contracts remain unchanged.
7. Focused tests, full tests, skill validation, and patch-integrity checks pass.
