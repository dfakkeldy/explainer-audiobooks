# Chicken Predators — Delivery Manifest

## Title
Chicken Predators: Identify, prevent, trap, and release — a Cape Breton field guide

## Slug
`chicken-predators`

## Requester / topic
Backyard flock owner in Western Cape Breton, Nova Scotia. Topic: how to identify
what's killing your chickens, how to prevent them, how to trap them, how to
release them.

## Public-safe / private / sensitive status
**Public-safe.** General educational content on poultry-predator identification,
prevention, and legally-constrained trapping. No private people, clients,
workplaces, or sensitive material.

## Permission-to-publish
Granted by user (public-safe, share in the library).

## Length mode
Deep (~4 hours target). **Actual: 3:05:40 at 1.0x, about 2.5 hours at 1.25x.**
30,798 words across 16 chapters. Came in shorter than the 45k deep-mode target;
chapters were ended when their knowledge delta was complete rather than padded
to hit a word quota (per narration-style.md: "uniform three-thousand-word
chapters are a reliable way to manufacture filler").

## Word count
30,798 words (build script total)

## Runtime
3:05:40 at 1.0x (verified with `ffprobe`)

## Chapter count
16

## Narrator
`am_michael` (native Echo/Kokoro render)

## Frontier author model
**GLM-5.2** (zai) — authored outline, all 16 Markdown chapters, and substantive
repairs. Owns voice, explanation choices, and continuity.

## Lower-cost roles used
- Research extraction: delegated subagent (fact-pack gathering, cited)
- Prose QC: `prose_qc.py` script + sweep greps
- Editorial review: cheap-reviewer report (3 findings, all accepted by frontier
  author and repaired)
- Packaging: `build_book.py`, `make_cover.py`

## Research mode
Deep, mixed (Nova Scotia government sources + extension poultry references +
trapping literature + regional naturalist knowledge). Source-confidence label:
**mixed** — the core identification, prevention, and trapping material is
well-established across many sources; the Cape-Breton-specific fauna claims
(raccoon absence, eagle density, regional mustelid pressure) rest on fewer
region-specific sources and are stated with appropriate hedging in the prose.

## Sensitive-topic guardrails
This is practical livestock-protection content, not professional pest-control
advice or legal instruction. Legal specifics (trapping seasons, protected
species, relocation law, firearms discharge bylaws) vary and change; the book
teaches concepts and questions, and points to Nova Scotia's Department of
Natural Resources and Renewables (NRR) and licensed Nuisance Wildlife Control
Operators (NWCOs) as the authorities. Raptors are federally protected and the
book states this is non-negotiable — no trapping or dispatch of raptors. The
book does not instruct on killing protected species.

## Figure count and image provenance
**0 interior figures.** The book is prose-only (no pictures requested or
required). Cover provenance and selection evidence are recorded in the
collection [cover-refresh manifest](../../docs/cover-refresh-2026-07/manifest.md).

## Cover

Refreshed in July 2026 with the approved **Night at the Fence** paired identity.
`cover.png` is the 1600 × 2560 EPUB/library cover and `m4b-cover.png` is the
independently composed 2400 × 2400 audiobook artwork. The governed
`cover-selection.json` binds both to the same source and public edition. The
immediately previous portrait is `cover-pre-paired.png`; the earlier historical
cover remains `cover-legacy.png`. Full evidence is in the [paired rollout
manifest](../../docs/cover-pilots/public-paired-cover-rollout-2026-07/manifest.md).

## Public files
- `chicken-predators.epub` — validated EPUB 3 with nav + NCX TOC
- `chicken-predators.md` — combined Markdown
- `cover.png` — paired portrait cover, 1600 × 2560
- `m4b-cover.png` — paired square audiobook artwork, 2400 × 2400
- `cover-selection.json` — governed paired selection receipt
- `chicken-predators.m4b` — chaptered Echo/Kokoro audiobook
- `chicken-predators.alignment.json` — 231-anchor Echo read-along sidecar
- `README.md` — this manifest

## QC gates passed
- ✅ EPUB validity (`unzip -t`, mimetype stored uncompressed)
- ✅ EPUB TOC (16 chapters, both nav and NCX)
- ✅ Word count verified (30,798)
- ✅ Heading consistency (all 16 chapters, single `## Chapter N - Title` format)
- ✅ Code-leak sweep (no backticks, no snake_case, no arrows/braces)
- ✅ Dead-phrase sweep (no tattoo/burn/sear/etch family)
- ✅ Emphasis-inflation sweep (2 hits, both reviewed — 1 repaired, 1 kept as earned)
- ✅ Tradeoff-drone sweep (reviewed — varied constructions, no drone)
- ✅ `prose_qc.py` — 3 repetition/voice findings, all accepted and repaired by frontier author
- ✅ Editorial review (citation-first, 3/3 findings resolved)
- ✅ Coverage-ledger spot-check (all core concepts delivered)
- ✅ Frontier-author repair pass complete
- ✅ Cover refreshed under the generated-raster and lower-title-field policy

## Audio verification
- M4B duration: 11,140.181 seconds (3:05:40), AAC, 16 named chapters.
- Alignment JSON: 231 monotonic anchors.
- Echo sidecar verification: `SIDECAR_OK`, 231 anchors, 16 chapters.

## iCloud Drive delivery folder
`/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/Chicken Predators/`

## Public repo copy
`books/chicken-predators/` — public-safe EPUB, Markdown, cover, M4B, alignment sidecar, and README.
