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
Deep (~4 hours target). **Actual: ~3.4 hours at 1.0x, ~2.7 hours at 1.25x.**
30,798 words across 16 chapters. Came in shorter than the 45k deep-mode target;
chapters were ended when their knowledge delta was complete rather than padded
to hit a word quota (per narration-style.md: "uniform three-thousand-word
chapters are a reliable way to manufacture filler").

## Word count
30,798 words (build script total)

## Runtime
~3.4 hours at 1.0x / ~2.7 hours at 1.25x (estimated at 150 wpm)

## Chapter count
16

## Narrator
`am_michael` (Echo/Kokoro). Fallback `am_puck` if am_michael unavailable.

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
required). Cover art is bespoke SVG, authored for this book — no external image
rights involved.

## Output files
- `chicken-predators.epub` — validated EPUB 3 with nav + NCX TOC
- `chicken-predators.md` — combined Markdown
- `cover.png` — selected cover (Concept 1: fortress coop at dusk, amber accent)
- `cover-1.png`, `cover-2.png`, `cover-3.png` — all three rendered candidates
- `cover-concept-1.svg`, `cover-concept-2.svg`, `cover-concept-3.svg` — source SVG art
- `chicken-predators.m4b` — Echo/Kokoro audio (render in progress at manifest time)
- `chicken-predators.alignment.json` — Echo alignment sidecar (render in progress)
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
- ✅ Cover rendered (3 candidates, 1 selected, accent colour visible)

## QC gates in progress / pending
- ⏳ M4B duration (`ffprobe`) — awaiting narration render completion
- ⏳ Alignment JSON parse — awaiting narration render completion
- ⏳ Optional Echo QA report — schema-dependent, may skip

## iCloud Drive delivery folder
`/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/Chicken Predators/`

## Public repo copy
`books/chicken-predators/` — public-safe EPUB, Markdown, cover, README.
