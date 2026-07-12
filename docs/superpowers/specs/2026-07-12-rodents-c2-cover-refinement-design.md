# Rodents C2 Cover Refinement Design

**Date:** 2026-07-12

**Status:** Verbally approved; awaiting written-spec review

**Parent design:**
[`2026-07-12-adaptive-cover-specification-design.md`](2026-07-12-adaptive-cover-specification-design.md)

## Objective

Refine the C2 **Integrated Colour Band** candidate for *Rodents in the Walls*
without changing its approved artwork, crop, palette, or general title
direction. The revision must preserve C2's strong orange editorial identity
while revealing every rodent shadow and turning the subtitle and author into one
intentional footer lockup.

This is a requested mix/refinement, not a final package selection. The revised
candidate returns to Dan for visual approval before any selection receipt,
EPUB, M4B, public package, or iCloud package changes.

## Approved Inputs

- Source artwork:
  `/Users/dfakkeldy/Developer/explainer-audiobooks/.build/custom-learning-audiobooks/rodents-in-the-walls-v3/dist/cover-raster-art-1.png`
- Source-art SHA-256:
  `cced16a14a0aaced901af7ffd0b140c4d6e13fdf88bd3da22a9724fb7bad9812`
- Source properties: 1024 × 1536 RGB PNG.
- Canvas: 1600 × 2560 RGB.
- Palette:
  - navy `#132238`;
  - exposed-plaster orange `#EF5735`;
  - warm cream `#F6EDDA`;
  - deep footer navy `#07111F` where needed for the lower gradient.

The source artwork is copied byte-for-byte into an ignored pilot run. It is not
regenerated, retouched, inpainted, recoloured, or recropped.

## Approved Design

### Compact Title Ribbon

C2 keeps its orange title material, but the field becomes a shorter top ribbon.
It retains modest left and right insets rather than touching the canvas edges.
Its lower edge must stop above the first visible rodent silhouette, leaving a
clear navy gap between the ribbon and the shadows.

The renderer should begin from these proportions and adjust upward if the final
source crop reveals an earlier silhouette:

- ribbon top: approximately 4–5 percent of canvas height;
- ribbon height: approximately 23–25 percent of canvas height;
- left/right inset: approximately 4 percent of canvas width;
- minimum visual clearance above the first shadow: 24 final-cover pixels.

The final visual check, not the approximate coordinate, is authoritative. No
orange field, cream binding rule, title glyph, outline, or shadow effect may
cover a rodent silhouette.

The title hierarchy stays stacked and is tightened vertically to fit:

1. small technical-mono `AUDIOBOOK` label in navy;
2. `RODENTS` in the pinned Fraunces editorial serif, navy;
3. `IN THE` in the pinned Space Grotesk geometric sans, navy;
4. `WALLS` in the pinned Barlow Condensed display face, warm cream with a
   restrained navy outline.

A thin cream rule remains inside the ribbon near its lower edge. It binds the
colour field to the exposed plaster without extending into the shadow area.

### Editorial Footer Lockup

The former single-line subtitle and separated author treatment are replaced by
one left-aligned unit near the lower safe margin. The lockup contains:

1. a short orange rule, roughly one quarter of the usable cover width;
2. the subtitle in cream Space Grotesk, split deliberately across two lines:

   ```text
   Squirrels and Other Houseguests
   in Western Cape Breton
   ```

3. `Dan Fakkeldy` directly beneath in orange IBM Plex Mono with restrained
   tracking.

The literal metadata remains unchanged. The line break is presentation only;
capitalization and spelling remain canonical.

The footer uses a soft lower navy gradient for readability. It must not use a
hard rectangle, full-width rail, centred book-jacket ornament, or separate
author corner. The subtitle, rule, and author should read as one editorial
signature while leaving the wall opening as the focal point.

## Typography And Hierarchy

- The title remains the first thumbnail read.
- The central wall opening and branching shadows remain the second read.
- The subtitle should become comfortably readable above thumbnail scale and
  visibly structured at 160 pixels, even if its smallest words are not expected
  to be read at that width.
- The author should be clearly present at 160 pixels and comfortably readable
  at common audiobook-store detail sizes.
- Font resolution must use the repository-pinned files and isolated renderer
  environment already implemented by the parent adaptive-cover work.
- No system-font or generic fallback is acceptable.

The existing 2.97:1 cream-on-orange `WALLS` advisory may remain only if the
navy outline produces a crisp word shape at full size and 160 pixels. If it does
not, the renderer must use navy `WALLS` rather than weakening the artwork or
adding another container.

## Artifact Flow

The refinement uses a fresh ignored pilot directory so superseded fallback-font
or pre-refinement artifacts cannot be mistaken for the new candidate. The run
produces:

- the byte-identical approved source-art copy;
- one revised C2 JSON specification under a new candidate id;
- a 1600 × 2560 RGB cover;
- a 160 × 256 RGB thumbnail;
- a deterministic render receipt;
- a comparison sheet showing original C2 beside refined C2;
- a short visual-review report.

The revised candidate id is `c2a-compact-ribbon-editorial-footer`, with direction
name `Compact Ribbon / Editorial Footer`. This distinguishes the requested mix
from the earlier `c2-integrated-colour-band` render.

## Validation And Review

Before presentation, the run must prove:

- source-art SHA-256 matches the approved hash;
- specification validates with the canonical font manifest;
- output and thumbnail are RGB PNGs with exact dimensions;
- render receipt hashes match the files;
- two consecutive renders are byte-identical;
- title, subtitle, author, and label spelling are exact;
- no ribbon, rule, title treatment, or footer element clips or covers a rodent
  silhouette;
- the wall opening remains visually dominant;
- title is immediately legible at 160 pixels;
- subtitle and author form one coherent footer lockup;
- the result does not feel like artwork placed inside a generic template;
- the normal contact-sheet CLI renders the exact Unicode labels;
- no `cover-selection.json` exists;
- repository and iCloud Rodents package hashes, sizes, and mtimes remain
  unchanged.

If the shadow-clearance or footer-lockup checks fail, adjust the revised
specification only, preserve the failed ignored round as diagnostic history,
and rerender under the same revised candidate id.

## Mutation Boundary

This design authorizes only a new ignored pilot specification and its rendered
comparison artifacts. It does not authorize selection or package promotion.

After Dan approves the revised cover, a later explicit step may create the
selection receipt and update the governed EPUB, M4B artwork, public package,
and iCloud package. Those mutations must use the parent design's receipt,
verification, dry-run, apply, rollback, and final package-validation workflow.

## Out Of Scope

- Regenerating or editing the source artwork.
- Changing the book title, subtitle, author, or `AUDIOBOOK` label.
- Changing the approved navy/orange/cream palette.
- Revising C1 or B1.
- Replacing the adaptive renderer or cover-spec schema.
- Selecting or publishing a cover before the revised visual gate.
