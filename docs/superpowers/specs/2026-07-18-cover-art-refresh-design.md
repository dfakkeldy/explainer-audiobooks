# Cover Art Refresh: Flat-Graphic Direction + De-AI'd Raster — Design

Date: 2026-07-18
Status: Approved design, pending spec review
Branch: `claude/skill-cover-images-a52a59`

## Problem

Recent generated raster covers read as obviously AI-generated. Concrete tells on
the current shelf: the paper-cut layered landscape with a winding road
(*Claude Platform 01*), airbrushed radial glow (*Rodents in the Walls*),
hyper-smooth 3D product-render sheen (*Why It Feels Right*), and glossy AI
photorealism (*The New Deal*).

Two skill rules cause this:

1. `skill/references/cover-art.md` demotes bespoke vector art to an explicit
   fallback ("Never choose SVG merely because it is faster"), and its copy-ready
   prompt offers visual languages ("cinematic editorial photograph", "painterly
   realism", "surreal editorial illustration") that image models render with a
   recognizable AI sheen. Its anti-brief bans subject clichés but no render
   tells.
2. `skills/custom-learning-audiobook/references/package-and-qc.md` goes
   further: "When an image-generation tool is available, generated raster art is
   mandatory; … Do not substitute bespoke SVG, programmatic vector art,
   diagrams, or icon compositions."

The flat-graphic look the user wants to recur (the *Question Machine*
flat-lens cover — flat inks, one bold mark, mid-century poster sensibility) was
never encoded as a variant anywhere: "cartoon" appears in no skill file and no
git history. A remembered "cartoon variant used from time to time" therefore
never fired again — the rules above actively forbid it. Lesson: a style that is
not contract-tested does not exist.

## Goals

- The flat-graphic look becomes a first-class, recurring cover direction.
- Generated raster covers stop reading as AI at a glance.
- Both rules are pinned by contract tests so they cannot silently drift.

## Non-goals (explicit follow-ups, not this change)

- No mechanical print-treatment step (posterize/halftone/grain at compose
  time). Script + test work; revisit only if the prompt-level fix falls short.
- No cross-book series ledger. The guaranteed flat-graphic slot plus per-book
  user selection already varies the shelf.
- No pipeline, script, schema, or receipt changes. Paired covers, receipts, and
  command shapes stay exactly as `tests/test_skill_cover_contract.py` pins
  them.

## Change 1 — "Designed flat graphic" becomes a first-class direction

File: `skill/references/cover-art.md`

- Add a seventh row to the Non-Negotiable Default direction menu:
  **Designed flat graphic** — bold flat-ink illustration; one confident
  geometric or character mark; 2–4 flat colours; strong silhouette; mid-century
  poster sensibility; lively but not childish. Best fit: technology, ideas,
  learning journeys, playful explainers.
- Replace the SVG-demotion paragraph in "Making the Art" with a route-parity
  rule: **the render route follows the direction, not tool availability.**
  Flat-graphic and type-led candidates use compositor-native SVG or flat
  raster art; photographic, collage, and illustrative print directions use the
  image-generation tool. Neither route is a fallback for the other.
- Add the guarantee to Non-Negotiable Default, verbatim in both files: "At
  least one of the three candidates must be a designed flat graphic or
  type-led direction." The user still makes the explicit pair selection; this
  only guarantees the direction is always offered.

File: `skills/custom-learning-audiobook/references/package-and-qc.md`

- Replace the raster-mandatory paragraph ("generated raster art is mandatory
  … Do not substitute bespoke SVG …") with the same route-parity rule and the
  at-least-one-flat-candidate guarantee, phrased for that skill's packaging
  flow. The existing bright/high-key requirement and the no-copying rule stay.

## Change 2 — De-AI the raster route

File: `skill/references/cover-art.md`

- Visual-language menu in the copy-ready prompt: drop "cinematic editorial
  photograph" and "painterly realism"; offer print-native languages instead —
  refined screen print, risograph, woodcut/linocut, gouache poster
  illustration, halftone editorial illustration, tactile cut-paper collage
  (kept, but see anti-brief below). Documentary still life survives as a
  direction but must read as film photography — visible grain, imperfect
  natural light, real-world staging — never a glossy smooth 3D render.
- Negative-prompt block gains an explicit AI-tell anti-brief: no centered
  glowing object, no airbrushed radial glow, no perfectly smooth gradients, no
  paper-cut layered landscape with a winding road or river, no hyper-smooth 3D
  product render, no melted or smeared detail, no uniform digital sheen.
- Award-Worthy Acceptance Bar gains one rejection line: any candidate a
  stranger would clock as AI-generated at a glance (waxy smoothness, airbrush
  glow, trope composition) is discarded and regenerated.

## Change 3 — Pin the new rules with contract tests

File: `tests/test_skill_cover_contract.py`

New test method(s) asserting these anchor phrases exist:

| Anchor | Files |
|---|---|
| `Designed flat graphic` | cover-art.md, package-and-qc.md |
| `route follows the direction` | cover-art.md, package-and-qc.md |
| `flat graphic or type-led direction` (the at-least-one sentence) | cover-art.md, package-and-qc.md |
| `airbrushed radial glow` (anti-brief anchor) | cover-art.md |

Also assert the removed rules stay removed: `assertNotIn` for
"generated raster art is mandatory" (package-and-qc.md) and "Never choose SVG
merely because it is faster" (cover-art.md).

## Constraints

- Every existing pinned marker must survive, notably: "exactly three",
  "1600×2560", "2400×2400", "explicit pair selection", "paired receipt",
  "post-embed verification", "title strategy", "font", "line breaks",
  "Never run `replace_m4b_cover.py`", the complete paired command example, and
  the verification-only compatibility sections.
- The differentiation rule (three candidates differ in metaphor, composition,
  palette, material language, and title strategy) is unchanged and applies to
  flat-graphic candidates too.
- Keep generated artwork text-free; typography stays in the candidate
  specification.
- Unattended runs: the rubric reference in
  `skill/references/unattended-production.md` continues to point at
  cover-art.md and needs no change; the at-least-one rule applies to candidate
  *creation*, which unattended runs already do before rubric selection.

## Acceptance criteria

1. The full test suite passes, including the new contract markers.
2. `cover-art.md` and `package-and-qc.md` contain no sentence that makes
   raster mandatory or demotes vector art to a fallback.
3. A dry read of the two files as a fresh skill invocation would produce, for
   any book: three directions of which at least one is flat-graphic or
   type-led, raster prompts constrained to print-native languages with the
   AI-tell anti-brief, and the user's explicit pair selection unchanged.

## Execution note (2026-08-08)

Executed on `claude/raster-creation-codex-f7a423`; the original plan branch is
untouched and keeps its unrelated probe-fallback commit. The tree drifted
between design and execution:

- Commit `7fc34d5` (2026-07-26) deleted the custom-learning skill along with
  `package-and-qc.md` after the Echo gates came out, so Change 1's
  package-and-qc.md half — and the plan's later widening to both SKILL.md
  bodies — no longer had targets. The deleted surfaces took their
  raster-mandatory rules with them. Today's `skill/SKILL.md` delegates cover
  work to `cover-art.md` and carries no route language.
- Changes 1–3 therefore landed entirely in `skill/references/cover-art.md`
  and `tests/test_skill_cover_contract.py`. The new tests pin the markers in
  cover-art.md and assert the stale demotion phrases stay out of every surface
  in the contract's `FILES` dict.
- One edit beyond the plan: the Candidate Brief "not ready to render" sentence
  also demoted vector art ("without first using an available image-generation
  tool"), which acceptance criterion 2 forbids; it now binds to the
  route-follows-direction rule instead.
