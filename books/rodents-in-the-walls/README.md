# Rodents in the Walls

A Listener's Guide to Identifying, Removing, and Preventing Unwanted Houseguests

## About

An educational audiobook on rodents that get into the structure of a house — the
three species most likely to be responsible (house mouse, Norway rat, roof rat),
how they get in, why they stay, and the integrated approach to removal and
prevention. Grounded in CDC and EPA public-health guidance.

## Metadata

| Field | Value |
|---|---|
| Title | Rodents in the Walls |
| Subtitle | Identify, Remove, and Prevent Unwanted Houseguests |
| Slug | `rodents-in-the-walls` |
| Author | Dan Fakkeldy |
| Frontier author model | deepseek-reasoner |
| Research/review model | deepseek-reasoner |
| Length mode | Standard beta (~2 hours) |
| Word count | 19,394 |
| Chapters | 9 |
| Est. runtime | ~2.2 h at 1.0x, ~1.7 h at 1.25x |
| Narrator | am_michael (Echo native) |
| Research mode | Deep — live CDC, EPA primary sources verified |
| Source-confidence label | deep — multiple authoritative source classes |
| Public/private status | Public-safe |
| Permission to publish | Yes |
| Sensitive-topic guardrails | Educational overview only; disease risk framed as public-health guidance; cleanup protocol from CDC; poison guidance from EPA |

## Research notes

- **CDC — How to Clean Up After Rodents** (April 2024): 7-step safe cleanup, no-vacuum rule, bleach ratio 1:9, heavy-infestation HEPA respirator protocol. Verified live.
- **CDC — How to Seal Up to Prevent Rodents** (April 2024): inside/outside entry-point checklist, steel wool + caulk, denial of food/water/shelter. Verified live.
- **CDC — How to Trap Up to Remove Rodents** (April 2024): snap-trap recommendation, T-placement, peanut-butter bait, pre-baiting for rat neophobia; no glue traps. Verified live.
- **CDC — About Hantavirus / Hantavirus Prevention** (May 2024): deer mouse vector, 38% HPS case fatality, prevention through rodent control.
- **EPA — Rodenticides hub** (2025-2026): About Rats and Mice, options for dealing with infestations, safely using bait products, bait-station tiers 1-4, hiring a professional. Verified live.

## QC gates

| Gate | Status |
|---|---|
| Code-leak sweep (backticks, snake_case, arrows/braces/empty calls) | PASS |
| Dead-phrase sweep (tattoo, burn, sear, etch, the-one-rule, if-you-remember-nothing) | PASS |
| Emphasis inflation (most important, heart of, matters more than anything) | PASS (resolved 7 hits) |
| Tradeoff drone (trade-off, cost of, every choice/decision) | PASS (earned instances only) |
| Prose QC script (repeated phrases, similar paragraphs, formulaic openings/closings) | PASS (clean report) |
| EPUB validation (unzip -t) | PASS |
| Heading consistency (single ## per file) | PASS |
| No interior figures | N/A |

## Output files

| File | Description |
|---|---|
| `rodents-in-the-walls.epub` | EPUB 3 format |
| `rodents-in-the-walls.md` | Combined Markdown |
| `cover.png` | Cover art (Concept B — The Inspection) |
| `rodents-in-the-walls.m4b` | Echo-narrated audiobook (M4B) |
| `rodents-in-the-walls.alignment.json` | Chapter-level alignment data |

## iCloud delivery

Complete package copied to:
`/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/Rodents in the Walls/`
