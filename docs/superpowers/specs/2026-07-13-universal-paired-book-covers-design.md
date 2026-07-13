# Universal Paired Book Covers — Design Specification

**Date:** 2026-07-13  
**Status:** Proposed for implementation  
**Scope:** Shared audiobook-production contract plus the five public books listed on `kinnokilabs.com/learn`, excluding the already-approved *Rodents in the Walls* cover

## Goal

Every newly produced or intentionally refreshed audiobook uses two coordinated,
purpose-built cover compositions:

- a 1600 × 2560 portrait book jacket for EPUBs, public book folders, repository
  pages, and portrait website presentation; and
- a 2400 × 2400 square listening cover for M4B artwork and square player tiles.

The two assets express one approved cover identity. They share the same central
metaphor, source artwork, palette, and typographic family, but each has a layout
and hierarchy designed for its actual display shape. The square is never an
automatic centre crop of the portrait, and the portrait is never padded into a
square.

This becomes the universal forward-looking production rule. Existing legacy
packages remain valid until deliberately refreshed. Any new book, or any book
whose cover is intentionally changed after this contract lands, must publish
both variants together.

## First Migration

The first catalogue migration covers these five public books currently listed
on `https://kinnokilabs.com/learn`:

1. *Echo, From the Inside*
2. *Why It Feels Right*
3. *Findable*
4. *Chicken Predators*
5. *The New Deal*

*Rodents in the Walls* is explicitly excluded. Its approved C2A Compact Ribbon /
Editorial Footer portrait cover and existing package remain unchanged. It is a
quality benchmark during review, not a migration target.

## Collection Design System

The library is unified by rules rather than a repeated template:

- every title has a book-specific visual thesis;
- the title is an active compositional element, not text pasted into a generic
  footer;
- pinned, licensed display fonts provide expressive but reproducible type;
- title, subtitle, and author hierarchy remains readable at a 160-pixel
  portrait thumbnail and a 160-pixel square player tile;
- colour, metaphor, material language, crop, and layout vary by book;
- generated artwork contains no lettering, logos, interface screenshots,
  watermarks, or book mockups; and
- bright/high-key design remains the default unless the subject earns a darker
  direction.

The five-book art briefs approved in conversation are the controlling creative
briefs. Each book receives exactly three genuinely different candidate pairs.
The candidates differ in metaphor, composition, material language, and palette,
not merely crop or colour.

### Approved direction menu

#### Echo, From the Inside

- **The Open Machine:** an audiobook player opened like a mechanical watch.
- **Rooms Inside the App:** a tactile architectural cutaway of connected app
  systems.
- **Sound Made Physical:** narration moving through a precisely constructed
  transparent object.

#### Why It Feels Right

- **The Impossible Teapot:** a surreal physical lesson in affordances.
- **Invisible Alignment:** ordinary objects settling onto a designed grid.
- **The Shape of Feedback:** a responsive glass-and-paper object in use.

#### Findable

- **One Spine in a City:** one unmistakable spine within an immense shelf.
- **The Exact Phrase:** scattered letterforms converging into one path.
- **Signal Through the Shelf:** a narrow beacon crossing a crowded catalogue.

#### Chicken Predators

- **Tracks Around the Henhouse:** field-guide evidence around a coop threshold.
- **The Evidence Table:** a naturalist's investigative still life.
- **Night at the Fence:** predator silhouettes outside a protected enclosure.

#### The New Deal

- **The Red Thread Route:** a rural route map physically stitched together.
- **The Weight of the Mailbag:** a mailbag and agreement pages on a scale.
- **The Route Rewritten:** an archival route card changing measurement systems.

## Paired Candidate Contract

A candidate is one visual direction with two governed render specifications:

```text
candidate identity
├── shared source artwork and provenance
├── portrait specification → cover.png (1600 × 2560)
└── square specification   → m4b-cover.png (2400 × 2400)
```

Both specifications name the same candidate ID and source-art identity. They may
use different crops, layer positions, type sizes, line breaks, safe areas, and
effect bounds. They may not change the metaphor, substitute unrelated artwork,
or silently use different palettes.

The portrait contains the exact title, exact subtitle when the book has one,
and exact author metadata. The square always contains the exact title and exact
author. It includes the exact subtitle when it remains comfortably legible; it
may omit the subtitle but may never abbreviate or rewrite it. Omitting a subtitle
is an explicit square-layout choice recorded in the specification and receipt.

Exactly three paired candidates are rendered per book. A contact sheet presents
each candidate as a portrait/square pair. The human selects one complete pair or
requests a specific mix. The system never independently selects a portrait and
square from different candidates.

## Files and Naming

For governed public book folders:

- `cover.png` — selected 1600 × 2560 portrait cover;
- `m4b-cover.png` — selected 2400 × 2400 square listening cover;
- `cover-source.png` — approved source artwork;
- `cover-spec.json` — selected portrait specification;
- `m4b-cover-spec.json` — selected square specification;
- `cover-thumbnail.png` — real 160 × 256 portrait thumbnail;
- `m4b-cover-thumbnail.png` — real 160 × 160 square thumbnail;
- `cover.render.json` — portrait render receipt;
- `m4b-cover.render.json` — square render receipt; and
- `cover-selection.json` — one selection receipt binding the complete pair.

Historical covers are preserved using existing per-book conventions before the
new pair is promoted. Unselected candidates and source-generation scratch remain
ignored build artifacts, not public-repository content.

## Schema and Renderer

The declarative cover schema gains a required `variant` value of `portrait` or
`square`. Canvas dimensions are exact per variant. Safe-margin, text-bound,
font-role, effect-bound, metadata, glyph, and source-art rules apply to both.

The renderer remains deterministic and atomic. It renders each specification
independently, then publishes a pair only after both outputs and both render
receipts validate. If either render or publish fails, neither selected canonical
asset changes.

Square layout support is a real layout mode, not a post-render crop. Tests cover
square safe areas, metadata hierarchy, thumbnail creation, source identity,
output aliasing, deterministic rerendering, and two-asset rollback.

## Selection and Receipt Model

`cover-selection.json` evolves from a single-render selection into a paired
selection. It binds:

- candidate ID and human selection source;
- shared source-art hash and provenance;
- portrait specification, render, dimensions, thumbnail, and output hashes;
- square specification, render, dimensions, thumbnail, and output hashes;
- font-manifest identity;
- exact metadata and the square subtitle-presence decision;
- book slug, edition, privacy classification, and publication permission; and
- the selection timestamp.

Receipts reject mixed candidate IDs, mismatched source-art identities, stale
renders, wrong dimensions, unknown fields, duplicate JSON keys, automatic
selection, and output aliasing. Legacy single-cover receipts remain verifiable
for unchanged legacy packages, but the creation and sync commands require a
paired receipt for new or refreshed covers.

## EPUB and M4B Packaging

The EPUB embeds `cover.png` byte-for-byte and verifies that identity after
replacement.

The M4B embeds `m4b-cover.png`. Verification compares orientation-normalized
square artwork pixels and separately proves that audio packet bytes, streams,
duration, chapter boundaries and titles, and format tags remain unchanged.

Packaging succeeds only when both embedded identities match the selected pair.
Replacing cover art must never rebuild, transcode, shorten, or substitute an
edition. Public and private/iCloud editions are always staged and verified from
their own pre-change media.

## Website Behaviour

The KinNoKi site consumes both variants by purpose:

- `/learn` sample-book cards display the portrait `cover.png`;
- the listening catalogue and player use `m4b-cover.png` as their square
  artwork; and
- generated site assets record the source book and selected-pair hashes so a
  stale or mixed pair is detectable during the site build.

The site rollout must preserve existing book descriptions, links, audio,
captions, and player metadata. Only cover presentation and cover assets change.
Responsive tests confirm that portrait cards do not distort and square player
tiles do not crop title or author text.

## Five-Book Rollout Workflow

1. Capture fresh public EPUB/M4B/site baselines and media signatures for all five
   books.
2. Generate three approved art-direction sources per book with no baked text.
3. Create portrait and square specifications for each source and render 15
   paired candidates.
4. Validate full-size assets and true 160-pixel thumbnails, then present one
   paired contact sheet per book.
5. Pause for human selection. Selection can choose a pair or request a named
   mix, but cannot be inferred from silence.
6. Promote the five approved pairs atomically into their public book folders.
7. Replace only the EPUB cover member and M4B artwork for each public edition.
8. Update corresponding public iCloud packages only when an exact matching
   edition exists; never substitute a repo edition for a different private or
   corrected edition.
9. Update KinNoKi site portrait and square assets, build outputs, and tests.
10. Verify receipts, EPUB archives, M4B media signatures, site rendering,
    checksums, privacy boundaries, and changed-file inventories before PRs.

## Failure and Safety Behaviour

- No canonical book or site asset changes before human selection.
- A failed pair render or publish restores both previous assets and receipts.
- A failed EPUB or M4B verification preserves the existing package.
- Edition mismatch, absent baseline evidence, stale receipt, missing square
  cover, or changed audio is a hard stop.
- Public sync requires explicit public-safe status and publication permission.
- Generated art, prompts, and production scratch remain outside public book
  folders unless included in a scoped public provenance manifest.
- The untouched Rodents package is included in final changed-file checks so an
  accidental modification fails the rollout.

## Verification and Acceptance

The implementation is acceptable when:

- the shared skill universally requires paired covers for new/refreshed books;
- schema, renderer, receipts, EPUB/M4B tooling, sync, documentation, and tests
  agree on the paired contract;
- all five books have a human-approved portrait/square pair;
- every portrait is RGB PNG at 1600 × 2560 and every square is RGB PNG at
  2400 × 2400;
- both variants pass full-size and actual 160-pixel visual review;
- all five EPUB embedded covers match their selected portrait bytes;
- all available M4B artworks match their selected square pixels while their
  pre-change media signatures remain exact;
- KinNoKi `/learn` cards show the portrait covers and the player uses the square
  covers without changing listening content;
- public/private and edition boundaries remain intact;
- *Rodents in the Walls* remains byte-identical; and
- local and hosted verification state is reported precisely, including when a
  repository has no hosted checks configured.

## Compatibility and Rollout Boundary

This design does not force an immediate rewrite of every historical book in the
repository. “Universal” means every future creation or intentional cover refresh
uses a pair, and tooling refuses to create a new single-cover receipt. Legacy
single-cover receipts remain readable so untouched books are not invalidated.

The five `/learn` books are the first deliberate migration. Other public books
can follow in later batches using the same contract. Rodents is intentionally
grandfathered until Dan explicitly requests a square companion; this project
does not alter it.

## Master Plan Impact

No change to portfolio priority, launch order, pricing, or product positioning.
This raises the presentation and listening-player quality bar for the existing
public learning-library and Echo dogfooding strategy.
