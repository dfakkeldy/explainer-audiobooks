# High-Key Cover Slate Design

Date: 2026-08-15
Status: Approved design, pending written-spec review
Branch: `codex/cover-high-key-bias`

## Problem

The current cover workflow permits bright covers but rewards several cues that
push image generation toward dark compositions: cinematic contrast, isolated
hero objects, vivid accents, engineered objects, and dramatic negative space.
The three candidates must vary in palette, but they do not have to vary in
overall value structure. Three differently coloured dark candidates therefore
satisfy the current contract.

An earlier change made `bright` the default for the legacy `make_cover.py`
flags. New books no longer use those legacy flags, so that default does not
govern schema-driven source art or candidate selection.

The flat-graphic guarantee is also weaker than intended. It currently permits
either a Designed flat graphic or a type-led direction. A typographic graphic
system can satisfy the rule without producing a flat illustration, and the
rule is not reflected in the candidate-selection summary in `skill/SKILL.md`.

The focused baseline test also exposes two stale phrase contracts in
`docs/how-these-were-made.md`. The prose remains semantically close to the
intended behavior, but it no longer contains the exact canonical anchors for
governed synchronization and Echo cover embedding.

## Goals

- Bias new cover slates toward high-key art without banning dark covers.
- Guarantee one genuine Designed flat graphic candidate in every slate.
- Preserve three meaningfully distinct complete portrait/square pairs.
- Let an exceptional, subject-appropriate dark candidate still win.
- Pin the new behavior with focused contract tests.
- Repair the two pre-existing public-method documentation contracts without
  changing narration or publication behavior.

## Non-goals

- No changes to existing cover images or finished book packages.
- No fourth candidate and no mandatory dark candidate.
- No pixel-luminance analyzer, automatic exposure correction, or numeric
  brightness threshold.
- No renderer, schema, receipt, narration, packaging, or publication changes.
- No broad rewrite of `docs/how-these-were-made.md`.

## Candidate Slate

Every new book still receives exactly three coordinated portrait/square pairs.
The candidate contract becomes:

1. At least two of the three complete pairs must be intentionally high-key.
2. One of those high-key pairs must use the Designed flat graphic direction.
   A Typographic graphic system remains an available direction but no longer
   satisfies the flat-graphic requirement.
3. The third pair is tonally unrestricted. It may be dark, high-key, or
   intermediate according to the subject and central metaphor. The workflow
   does not manufacture a dark candidate merely to fill a slot.

The three directions must still differ in metaphor, composition, palette,
material language, and title strategy. Tonal intent becomes an additional
declared dimension, not a substitute for the existing differentiation rules.

## High-Key Definition and Review

High-key means that the overall impression is luminous and open, built mainly
from middle and high values. It may use saturated colour, firm typography,
strong silhouettes, and dark accents. It does not mean white-only, pastel,
washed out, low-contrast, or visually timid.

Each art-and-type brief declares `high-key` or `tonally unrestricted` before
art is made. A pair counts as high-key only when both its portrait and square
renders retain that luminous value structure at full size and thumbnail size.
If a planned high-key direction resolves into a predominantly dark render, it
is revised or regenerated before selection rather than relabeled after the
fact.

The existing quality rubric remains primary. High-key treatment is the
tie-breaker between similarly strong complete pairs. A dark or intermediate
candidate may still be selected when it is clearly stronger on subject
specificity, thumbnail legibility, title hierarchy, pair coherence, absence of
defects, and distinctiveness. When that happens, the reported selection reason
must identify why the darker direction earned the choice.

## Instruction Changes

`skill/references/cover-art.md` will:

- replace the flat-graphic-or-type-led slot with a genuine Designed flat
  graphic requirement;
- define the two-high-key-plus-one-unrestricted slate;
- define high-key independently from pastel or low contrast;
- require tonal intent in candidate briefs and review both variants;
- add an explicit tonal-intent field to the image-generation prompt: high-key
  candidates request luminous fields and natural high-key treatments, while
  the unrestricted candidate follows its own brief without inheriting that
  request;
- require revision or regeneration when a declared high-key candidate renders
  dark; and
- add the high-key tie-break and the earned-dark selection rationale.

`skill/SKILL.md` will summarize the same slate and selection behavior so the
top-level production instruction cannot omit the bias when delegating to the
reference.

## Contract Repair

`docs/how-these-were-made.md` will receive two narrow wording corrections:

- state that the `governed Echo wrapper embeds` the selected square cover; and
- use the canonical `public/iCloud/site sync` phrase for verified public
  synchronization.

These are documentation-contract repairs only. They do not authorize delivery
or publication, alter the Echo command, or change any artifact.

## Tests and Verification

Extend `tests/test_skill_cover_contract.py` with flattened-text assertions that
pin:

- at least two high-key candidates;
- a genuine Designed flat graphic candidate rather than the old
  flat-graphic-or-type-led alternative;
- one tonally unrestricted candidate;
- the non-pastel definition of high-key;
- regeneration of a declared high-key candidate that renders dark; and
- high-key as a tie-breaker while allowing an earned dark selection.

The existing two failing public-method assertions must pass after the narrow
documentation repair. Verification will run the focused cover-contract tests,
the full unittest suite, `tools/validate_skills.py`, and `git diff --check`.

## Acceptance Criteria

1. A fresh skill invocation creates three complete pairs, at least two of which
   are recognizably high-key in both portrait and square form.
2. One high-key pair is a genuine Designed flat graphic; a type-led candidate
   cannot consume that slot.
3. The unrestricted candidate may be dark, and a clearly superior dark pair
   can still be selected with an explicit editorial reason.
4. A high-key label cannot be applied retroactively to a predominantly dark
   render.
5. No existing cover or production artifact changes.
6. The focused cover contract and repository verification commands pass,
   including the two pre-existing public-method documentation assertions.
