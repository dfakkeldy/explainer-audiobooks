# Adaptive Audiobook Cover Specification Design

**Date:** 2026-07-12
**Status:** Approved by Dan on 2026-07-12; implementation planned in
`docs/superpowers/plans/2026-07-12-adaptive-cover-specification.md`

## Objective

Replace the single house title template with a reproducible, art-directed cover
system. Every cover candidate must combine its own artwork, title treatment,
palette, crop, and metadata hierarchy. The renderer should be flexible enough to
produce expressive covers such as the approved *Rodents in the Walls* B1 study,
but structured enough to render the same result again, validate it, package it,
and prove which cover reached each delivery surface.

The intended outcome is publisher-level confidence without forcing every book
into the same font, title zone, colour field, or art style.

## Problem Statement

The current workflow generates potentially strong artwork, then passes it through
`skill/scripts/make_cover.py`. That compositor currently hard-codes:

- centred Georgia title text;
- a centred italic Georgia subtitle;
- a centred Helvetica author line;
- one lower-third title treatment for `bleed`;
- one framed image panel and lower title treatment for `hero`.

That contract makes different artwork sound like the same cover. It can also
shrink an excellent portrait composition into a decorative panel, as happened
with the selected *Rodents in the Walls* artwork. A later public cover refresh
and a later custom-learning package also wrote different covers to the public
repo and iCloud package at different times. The files were internally valid, but
there was no durable selected-cover identity shared across pipelines.

The problem is therefore not merely a limited font menu. The visual candidate
and its typography are currently designed in separate systems, and the packaging
flow does not preserve one canonical cover decision for an edition.

## Approved Creative Direction

The selected approach is an **adaptive, art-directed cover specification**.

Every candidate is a complete editorial lock-up with:

- one book-specific visual thesis;
- original text-free artwork or rights-cleared source art;
- an intentional art crop and title field;
- a title face, line breaks, scale, alignment, position, and colour treatment;
- optional controlled outline, shadow, rotation, and baseline adjustments;
- subordinate subtitle, author, and `AUDIOBOOK` metadata;
- a two-to-four-colour palette with one visible signature accent.

The *Rodents in the Walls* B1 mockup is the expressive quality benchmark. The
production system does not need to copy that layout, but it must be capable of
reproducing the same class of deliberate word- or glyph-level composition from
validated data.

The visual references discussed during design included *Kill It with Fire*, the
*Emotional Design* audiobook, *Beyond Vibe Coding*, *The Pragmatic Programmer*,
and *The Adult ADHD Tool Kit*. They are principle references only. The workflow
must not trace, imitate, or reproduce their artwork, lettering, brand marks, or
publisher systems.

## Design Principles

1. **Art and title are one decision.** The image prompt and the typography plan
   are written together before art generation.
2. **Generated art contains no lettering.** The image model creates the visual
   world; the deterministic renderer adds accurate metadata.
3. **The title is structural.** It may occupy a third to half of the useful
   visual field when the concept calls for it. It is not automatically a caption
   below the art.
4. **Negative space must be active.** Empty space may carry type, tension, or a
   focal relationship. Vacant space created only to satisfy a template fails.
5. **A band or panel is an option, not the identity.** A saturated title band can
   be excellent when it belongs to the art palette. The same footer repeated on
   every book is not acceptable.
6. **Family identity stays quiet.** Canvas dimensions, safe margins, metadata
   accuracy, a small `AUDIOBOOK` marker, and the quality bar identify the
   collection. Font and title placement do not.
7. **No silent aesthetic fallback.** An invalid specification fails with a clear
   diagnostic. It never becomes centred Georgia on a generated gradient.
8. **Thumbnail judgment is first-class.** Every candidate is reviewed at full
   size, 160 pixels wide, and beside the current collection.

## System Architecture

The system has five bounded parts.

### 1. Candidate Brief

The existing five-line candidate brief gains a typography section. Before art is
generated, each candidate records:

- audience promise;
- central metaphor;
- composition, crop, and intended title field;
- material language and two-to-four-colour palette;
- anti-brief;
- title archetype;
- planned line breaks and hierarchy;
- title anchor, alignment, and approximate occupied area;
- intended relationship between title and art;
- supporting metadata placement.

The three candidates must differ in visual metaphor, composition, palette,
material language, **and title strategy**. A valid comparison set should normally
include at least one title-forward graphic or illustrated direction and one
art-forward editorial direction. A high-key direction remains required unless
the subject genuinely makes it inappropriate.

### 2. Cover Specification

Each rendered candidate has a versioned JSON file. The JSON is data, not raw
SVG, CSS, HTML, Python, or shell. It uses a small set of validated primitives:

- canvas;
- art placement;
- solid or gradient field;
- scrim;
- line or border;
- text layer;
- grouped title runs.

Canonical file locations are:

- `skill/schemas/cover-spec-v1.schema.json`: documented v1 contract;
- `skill/assets/fonts/manifest.json`: stable font identifiers and licence
  receipts;
- `.build/custom-learning-audiobooks/<slug>/dist/cover-spec-1.json`,
  `cover-spec-2.json`, and `cover-spec-3.json`: rendered candidate inputs;
- `.build/custom-learning-audiobooks/<slug>/dist/cover-selection.json`: selected
  candidate receipt;
- `books/<slug>/cover-selection.json`: canonical receipt for a published public
  book;
- `/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/<Title>/cover-selection.json`:
  delivered receipt beside the final package.

The Python validator is authoritative at runtime. The checked-in schema is the
reviewable contract and fixture source; implementation does not require adding a
third-party JSON Schema dependency.

A conceptual example:

```json
{
  "schema_version": 1,
  "metadata": {
    "title": "Rodents in the Walls",
    "subtitle": "A Western Cape Breton Guide to Finding and Fixing the Problem",
    "author": "Dan Fakkeldy",
    "label": "AUDIOBOOK"
  },
  "canvas": { "width": 1600, "height": 2560, "background": "#132238" },
  "art": {
    "path": "cover-art.png",
    "mode": "bleed",
    "anchor": "center-bottom"
  },
  "layers": [
    {
      "kind": "text",
      "role": "title",
      "text": "RODENTS",
      "font_id": "display-condensed",
      "box": [104, 250, 1392, 330],
      "size": 255,
      "colour": "#EF5735",
      "align": "left"
    },
    {
      "kind": "text",
      "role": "title",
      "text": "IN THE WALLS",
      "font_id": "editorial-serif",
      "box": [250, 560, 1200, 410],
      "size": 210,
      "colour": "#F6EDDA",
      "align": "left"
    }
  ]
}
```

Exact coordinates are in final-cover pixels. Normalized coordinates may be
accepted as authoring sugar, but validation resolves them to pixels before
rendering so the receipt is unambiguous.

Text layers support controlled properties only:

- repository-managed `font_id`;
- size, line height, tracking, alignment, and case transformation;
- fill, opacity, outline, and bounded shadow;
- rotation and baseline shift;
- optional per-word or per-glyph overrides for one focal title treatment.

Per-glyph overrides are allowed because they make a B1-class composition
reproducible. They remain data and are limited to the canonical title. The
specification cannot execute arbitrary drawing code.

### 3. Font Library And Resolution

The renderer uses a repository-managed font manifest rather than unverified
system font names. Each entry records:

- stable `font_id`;
- bundled file path;
- family and style;
- supported roles such as display condensed, geometric sans, editorial serif,
  slab, or technical mono;
- licence name and source receipt;
- supported glyph coverage.

Only redistributable fonts with a repository-compatible licence may be bundled.
The initial implementation should stay small: enough contrasting roles to make
three genuinely different candidates, not a catalogue of decorative fonts.
Missing fonts are validation failures. The renderer does not substitute Georgia,
Helvetica, or another local font silently.

### 4. Deterministic Renderer

`skill/scripts/make_cover.py` gains a specification-driven path. The preferred
interface is:

```bash
python3 skill/scripts/make_cover.py \
  --spec <candidate>/cover-spec.json \
  --out <candidate>/cover.png
```

The renderer:

1. loads and validates the specification;
2. verifies canonical metadata and font availability;
3. resolves the art path and placement;
4. constructs the ordered visual layers;
5. renders exactly 1600 by 2560 pixels;
6. writes a 160-pixel thumbnail;
7. writes a machine-readable render receipt.

The renderer may continue using an SVG composition internally, but the public
input is the restricted JSON contract. Existing command-line flags remain as a
legacy compatibility adapter during migration. Updated skills and new books use
`--spec`. Invalid new specifications never fall through to the legacy preset.

### 5. Selection And Package Receipt

The chosen candidate produces `cover-selection.json` containing:

- book slug and edition identifier;
- selected candidate name;
- specification schema version;
- specification SHA-256;
- source-art SHA-256;
- rendered-cover SHA-256;
- font-manifest version;
- dimensions and colour mode;
- selection timestamp;
- selection source, such as explicit user choice;
- public, private, and permission-to-publish status.

For a public book already tracked in `books/<slug>/`, the committed selection
receipt is canonical. A later audiobook build may reuse it. It may replace it
only through a newly recorded selection, so a routine package copy cannot
silently overwrite a separately approved public cover.

For a new or private book, the finalized build run owns the canonical receipt.
If the book later becomes public, the receipt is promoted with the approved
public package.

## Data Flow

```text
book metadata + research
        |
        v
three art-and-type briefs
        |
        v
three text-free artworks + three cover-spec.json files
        |
        v
validate -> render full size + 160 px -> compare/contact sheet
        |
        v
explicit selection or requested mix
        |
        v
cover.png + cover-selection.json
        |
        +--> EPUB cover member
        +--> M4B attached artwork
        +--> public repo package, when allowed
        +--> iCloud delivery package
```

A requested mix creates a new candidate specification and render. It is not an
unrecorded manual edit of an already selected PNG.

## Validation And Failure Handling

Specification validation rejects:

- unknown schema versions or layer kinds;
- missing or unlicensed font identifiers;
- missing art or unsupported art formats;
- non-1600-by-2560 final canvases;
- text, fields, or required metadata outside safe bounds;
- title runs that omit, duplicate, or alter canonical title tokens;
- invalid colours, unreasonable rotations, or unbounded shadows;
- empty title fields or title text too small for the declared hierarchy;
- a band, panel, or scrim with no declared compositional purpose;
- output paths that escape the intended run folder.

Render-time failures are loud and candidate-specific. If art lacks the planned
title space, the candidate is recomposed or regenerated. The renderer must not
shrink the image into a generic framed panel simply to make room.

Automated contrast checks are advisory over complex art. A failed advisory
requires a stronger field, scrim, outline, crop, or colour choice followed by a
fresh render. Human full-size and thumbnail review remains the final legibility
gate.

If image generation is unavailable, retain the existing policy: stop and report
the blocker unless the user approves an alternative. Do not use a deterministic
cover renderer as an excuse to replace original artwork with generic programmatic
graphics.

## Packaging And Stale-Cover Protection

The selected render is the only cover input to downstream packaging.

- The standalone `cover.png` and EPUB declared cover-image member must be
  byte-identical.
- Extracted M4B artwork must match the selected cover after normalization to the
  same RGB pixel buffer; raw PNG hashes may differ after container re-encoding.
- Repo and iCloud standalone covers must byte-match the selected render.
- Repo and iCloud EPUB files must embed the selected render.
- The destination receipt must match the selected receipt after delivery.

A delivery command encountering a different existing receipt must classify the
operation as an intentional new selection, a reuse of the existing canonical
cover, or a conflict. It must not overwrite on title similarity alone. Public
books prefer the committed public receipt unless the current run contains a
newer explicit user selection.

## Review Surface

Every candidate review includes:

- the three full-size covers;
- three 160-pixel thumbnails;
- a one-line art-direction name and rationale;
- the art-and-type brief;
- the palette and font roles;
- any validation warnings.

For collection work, a labelled contact sheet checks for:

- repeated title archetypes or font roles;
- repeated palettes, crops, metaphors, or material languages;
- excessive photorealism or excessive flat vector treatment;
- weak covers that only pass in isolation;
- title legibility and hierarchy at equal thumbnail size.

The collection should feel curated, not uniform. A small family marker and a
consistent quality bar are sufficient shared identity.

## Testing Strategy

### Unit Tests

- schema-version and required-field validation;
- safe path resolution;
- font-manifest lookup and missing-font failure;
- canonical title reconstruction from runs;
- line breaking, alignment, tracking, baseline shifts, and rotation bounds;
- per-word and per-glyph override validation;
- colour parsing and contrast advisory behavior;
- safe-bound calculations;
- legacy CLI compatibility without silent new-spec fallback.

### Renderer Tests

- exact 1600-by-2560 RGB/RGBA output contract;
- stable rendering from the same specification, assets, and font manifest;
- full-bleed title-forward fixture;
- integrated colour-band fixture;
- expressive multi-run fixture modeled on the Rodents B1 class of composition;
- thumbnail generation;
- invalid specification produces no final cover.

### Package Integration Tests

- EPUB discovery uses the declared OPF cover item;
- standalone and EPUB cover bytes match;
- EPUB `mimetype` remains first and uncompressed;
- M4B artwork normalized pixels match the selected cover;
- repo and iCloud receipt conflicts are reported rather than overwritten;
- a new explicit selection can supersede an older receipt;
- private packages never become public through cover synchronization.

### Human Review Gates

- full-size inspection;
- 160-pixel inspection;
- three-candidate comparison;
- collection contact-sheet inspection when multiple books change;
- explicit user selection or requested mix before final packaging.

## Implementation Scope

The first implementation slice includes:

1. versioned cover-spec validation;
2. the restricted layer renderer;
3. a small licensed font manifest;
4. render and selection receipts;
5. updated `skill/SKILL.md`, `skills/custom-learning-audiobook/SKILL.md`,
   cover-art, and package/QC instructions;
6. unit and integration tests;
7. a *Rodents in the Walls* pilot using the existing approved raw artwork to
   prove title-forward, colour-band, and expressive-run fixtures;
8. verified propagation of the selected pilot cover into its public package and
   delivery copies after explicit selection.

The pilot should present final rendered candidates before changing the public
book or iCloud package.

## Out Of Scope

- regenerating every existing public cover in this implementation slice;
- changing manuscript, narration, alignment, or interior figures;
- generating title lettering inside image-model artwork;
- copying any named reference cover, publisher system, or designer style;
- introducing a graphical cover editor;
- arbitrary SVG, CSS, HTML, or executable hooks in cover specifications;
- automatically selecting the first valid candidate.

Existing covers remain valid until deliberately replaced. Future books use the
new specification path by default after the pilot passes.

## Acceptance Criteria

The design is implemented successfully when:

- a candidate's artwork and typography are both defined before rendering;
- three candidates can differ in title architecture as well as artwork;
- the renderer reproduces title-forward, integrated-band, and expressive-run
  covers from JSON without manual post-render edits;
- no new-spec failure silently produces the legacy Georgia template;
- bundled font resolution is deterministic and licence receipts are present;
- every selected cover has a selection receipt and verifiable provenance;
- standalone, EPUB, M4B, repo, and iCloud cover identities are checked using the
  appropriate byte or normalized-pixel comparison;
- the Rodents pilot retains the strong original artwork at useful scale and
  presents title treatments comparable to the approved C studies;
- all automated tests, package checks, full-size review, thumbnail review, and
  relevant repository validators pass;
- implementation is committed, pushed, and represented by a ready pull request.

## Master Plan Impact

This raises the presentation and repeatability bar for the existing Explainer
Audiobooks and Echo-learning workflow. It does not change portfolio priority,
pricing, launch order, narration policy, privacy rules, or publication consent.

## Source Notes

- Dan Fakkeldy cover-direction conversation with Codex, 2026-07-11 and
  2026-07-12.
- Existing compositor: `skill/scripts/make_cover.py`.
- Existing cover policy: `skill/references/cover-art.md`.
- Existing package policy:
  `skills/custom-learning-audiobook/references/package-and-qc.md`.
- Prior collection refresh design:
  `docs/superpowers/specs/2026-07-11-public-cover-refresh-design.md`.
- O'Reilly, “A short history of the O'Reilly animals”:
  <https://www.oreilly.com/content/a-short-history-of-the-oreilly-animals/>.
- O'Reilly, *Beyond Vibe Coding*:
  <https://www.oreilly.com/library/view/beyond-vibe-coding/9798341634749/>.
- No Starch Press, *Kill It with Fire*:
  <https://nostarch.com/kill-it-fire>.
- Hachette Basic Books, *Emotional Design*:
  <https://www.hachettebookgroup.com/titles/don-norman/emotional-design/9780465004171/>.
- Pragmatic Bookshelf, *The Pragmatic Programmer, 20th Anniversary Edition*:
  <https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/>.
