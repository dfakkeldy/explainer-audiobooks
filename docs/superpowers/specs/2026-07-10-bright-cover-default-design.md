# Bright Cover Default Design

## Goal

Make high-key, bright backgrounds the default for newly composed audiobook
covers. Keep the existing dark treatment as an explicit opt-in for a deliberate
cinematic direction.

## Context

`skill/scripts/make_cover.py` currently gives the `--tone` command-line option
a default value of `dark`. This implementation choice made most generated covers
dark even when a cover brief did not request that treatment. It is not a recorded
listener preference.

## Options Considered

1. Make `bright` the compositor default while preserving `--tone dark`.
   This changes the baseline without removing the cinematic option. Chosen.
2. Infer a tone from each artwork's colours.
   This is less predictable and would need a defined contrast-analysis contract.
3. Force every cover bright.
   This removes an intentional dark direction that remains useful for some books.

## Design

Change only the `argparse` default for `--tone` from `dark` to `bright`, and
update the option help and module documentation to describe the new baseline.
The existing `build_svg` and raster composition paths continue to accept both
`bright` and `dark` unchanged.

Add a command-line regression test that omits `--tone`, requests a cover with
no art, and asserts that the fallback SVG uses the bright-background palette.
The test will also preserve an explicit `--tone dark` assertion, so dark remains
available rather than becoming an accidental unsupported path.

## Scope and Non-Goals

- Future cover generation only; no existing cover files are changed.
- No changes to image-generation prompts, art selection, title layout, or
  library colour derivation.
- No automatic brightness analysis of supplied artwork.

## Verification

Run the focused cover tests, then the full Python unittest discovery suite and
the repository's skill validator. Inspect the generated SVG assertions rather
than relying only on a parsed command-line value.
