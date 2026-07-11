# Public Audiobook Cover Refresh Design

**Date:** 2026-07-11
**Status:** Approved direction; implementation pending

## Objective

Refresh the complete public Explainer Audiobooks collection with premium,
image-led raster cover art. Every title receives three genuinely different
AI-generated concepts. The agent selects the strongest concept for each title,
then presents the eleven final covers together for a collection-wide review.

The refresh covers these public books on `main`:

1. *Chicken Predators*
2. *Echo, From the Inside*
3. *Findable*
4. *Git Happens*
5. *Rodents in the Walls*
6. *Tests First*
7. *The Bug Is a Clue*
8. *The New Deal*
9. *The Voice in the Machine*
10. *Why It Feels Right*
11. *You Are the Architect*

Private, ignored, build-only, and untracked books are out of scope.

## Creative System

Each book gets three five-line candidate briefs following
`skill/references/cover-art.md`. The candidates must differ in all four axes:

- central metaphor;
- composition and title-safe field;
- palette and visible signature accent;
- material or visual language.

All candidate art is generated with the built-in image-generation tool as
original raster artwork. Generated art contains no title, subtitle, author,
lettering, logos, watermarks, UI, dashboards, mockup frames, or close imitation
of an existing cover or named designer. Typography is added afterward with
`skill/scripts/make_cover.py` at 1600 by 2560 pixels.

The collection shares a restrained typographic hierarchy and metadata treatment,
not a repeated visual template. Each title must remain recognizable by its own
metaphor, colour identity, and silhouette. Bright or high-key treatment is the
collection default, not merely one candidate per title. Select a dark cover only
when it is materially stronger and the subject genuinely benefits from it; if a
title has no award-worthy bright option, regenerate one direction brighter
before selection.

## Autonomous Selection

The agent chooses one final cover per book without pausing after each generation.
Selection uses the existing award-worthy acceptance bar plus these checks:

- the metaphor is specific to the book rather than generic technology or
  self-improvement imagery;
- the artwork remains legible at a 160-pixel thumbnail;
- the title field has enough visual quiet for clean typography;
- generated artifacts, accidental lettering, logos, anatomy errors, and muddled
  focal points are absent;
- the selected cover does not duplicate another book's metaphor, dominant
  palette, crop, or material language;
- the visible accent colour in the artwork matches the compositor's `--accent`.

A technically valid but weak concept is rejected and regenerated. The three
concepts are a minimum comparison set, not permission to select a poor result.

## Files and Provenance

Work-in-progress briefs, prompts, generated candidates, thumbnails, and review
notes live under `.build/public-cover-refresh-2026-07/` and stay out of Git.
Each book's final committed package contains:

- `cover.png`: the new 1600 by 2560 composited cover;
- `cover-legacy.png`: the previous public cover preserved for comparison and
  rollback;
- the existing EPUB with its embedded cover updated to the new `cover.png`;
- the existing README updated only where its cover provenance or description is
  now inaccurate.

A committed `docs/cover-refresh-2026-07/manifest.md` records, per title, the
selected direction, visual thesis, generation prompt, accent, tone, layout,
tool path, inspection result, and source/output filenames. A labelled contact
sheet is committed beside the manifest so the complete collection can be judged
at once. Discarded candidate images remain build artifacts and are not committed.

## EPUB and Delivery Updates

Public folders contain combined Markdown rather than canonical chapter source,
so implementation must not rebuild prose from the combined file. Instead, it
updates the existing EPUB's declared cover-image asset in place while preserving
all other entries, metadata, navigation, and compression. The EPUB `mimetype`
entry remains first and uncompressed.

For each book:

1. Discover the cover-image item from the OPF package rather than assuming a
   fixed path.
2. Replace only that image with the new cover bytes.
3. Preserve every other archive member and its order where practical.
4. Validate the archive with `unzip -t` and verify the cover item dimensions.

Where a matching public iCloud Books delivery folder exists, copy the selected
cover and refreshed EPUB into it without altering M4B audio, alignment sidecars,
playback state, or unrelated files. Do not create or modify private delivery
folders based only on title similarity.

## Collection Review Surface

The contact sheet shows all eleven final covers at equal size with title labels.
It is reviewed for:

- thumbnail readability;
- accidental palette clustering;
- repeated metaphors or compositions;
- excessively uniform dark or bright treatment;
- title hierarchy consistency;
- whether any single cover falls visibly below the collection.

If the collection review exposes a weak or repetitive cover, regenerate only
that title's art and rebuild its derived outputs before publication.

## Verification

The implementation is complete only when:

- all 33 minimum candidate generations are recorded in the build manifest;
- all eleven selected covers are 1600 by 2560 raster PNG files;
- every selected cover passes full-size and thumbnail inspection;
- every old cover is preserved as `cover-legacy.png`;
- every public EPUB passes `unzip -t`, keeps first/uncompressed `mimetype`, and
  embeds the selected cover;
- README cover statements and the provenance manifest are accurate;
- the contact sheet contains all eleven current selected covers;
- matching public iCloud copies, when found, checksum-match the selected repo
  cover and refreshed EPUB;
- `git diff --check` and relevant repository validators pass;
- the branch is pushed and represented by a ready pull request.

## Failure Handling

If built-in image generation is unavailable, stop and report the blocker. Do not
fall back to SVG or a CLI/API image model without explicit user approval. If a
candidate contains unwanted text or visual defects, regenerate with one targeted
prompt correction. If EPUB cover discovery or replacement cannot be verified for
a title, leave that EPUB unchanged and report the exact package structure rather
than risking corruption.

## Master Plan Impact

This is a quality and public-proof improvement to the existing Explainer
Audiobooks and Echo-dogfooding lane. It does not change portfolio priority,
launch order, dates, pricing, positioning, or automation cadence.
