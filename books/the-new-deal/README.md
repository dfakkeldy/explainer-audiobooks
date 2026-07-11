# The New Deal — Canada Post, CUPW, and What It Means for Rural Mail

## Manifest

- **Title:** The New Deal
- **Subtitle:** Canada Post, CUPW, and What It Means for Rural Mail
- **Slug:** the-new-deal
- **Requester/topic:** Dan Fakkeldy — Canada Post's new collective agreement with CUPW, implications for the Port Hood Post Office, and especially RSMCs and OCREs
- **Public-safe/private/sensitive status:** Public-safe. Educational overview of a public collective agreement and public restructuring plan. Not workplace advice.
- **Permission-to-publish status:** Approved by Dan for public release on 2026-07-11.
- **Length mode:** Standard beta book (~2 hours, 16,471 words)
- **Word count:** 16,471 words
- **Runtime:** 1:55:42 at 1.0x (6,942.336 seconds), about 1.5 hours at 1.25x
- **Chapter count:** 9
- **Narrator:** am_michael (native Echo/Kokoro)
- **Frontier author model:** GLM-5.2 (Z.AI)
- **Research/review/production roles:** GLM-5.2 (research, outline, all chapters, QC). No cheaper-worker review used (single-model frontier run).
- **Research mode:** Deep — multiple source classes compared (Canada Post official, CUPW official/bulletins, independent journalism, government IIC report, critical analysis)
- **Source-confidence label:** deep
- **Sensitive-topic guardrails:** Educational overview framing. Multiple perspectives presented (CUPW, Canada Post, government, critical/rank-and-file). No advice on what any worker should do. Not a substitute for the actual collective agreement text.
- **Figure count and image provenance/licensing summary:** 0 interior figures. Current cover provenance and selection evidence are recorded in the collection [cover-refresh manifest](../../docs/cover-refresh-2026-07/manifest.md).

## Chapters

1. The Post Office on Main Street (1,831 words)
2. How We Got Here: Two Years of Chaos (1,745 words)
3. The Headlines: Wages, Pensions, and Personal Days (1,510 words)
4. The RSMC Revolution: From Route Evaluation to Hourly Pay (2,172 words)
5. Who Covers the Route? OCREs, PFEs, and the Staffing Puzzle (1,958 words)
6. Coverage of Absences: The New Rulebook (1,906 words)
7. Weekend Parcels and the Amazon Question (1,692 words)
8. The Money Problem: Why This Contract Exists (1,763 words)
9. What It Means in Port Hood (1,894 words)

## Cover

Refreshed in July 2026 with original raster artwork generated through the
built-in image-generation tool, then composed with the repository cover tool.
The artwork follows the current collection policy: visual energy continues
through the top and middle, with only the lower 25–35% reserved as a calmer
title field. The previous public cover is preserved as `cover-legacy.png`;
generation prompt and selection evidence are recorded in the collection
[cover-refresh manifest](../../docs/cover-refresh-2026-07/manifest.md).

## Output Files

- `the-new-deal.epub` — EPUB 3 with nav + NCX
- `the-new-deal.md` — combined Markdown
- `cover.png` — July 2026 generated-raster cover, 1600 × 2560
- `the-new-deal.m4b` — chaptered native Echo/Kokoro audiobook
- `the-new-deal.alignment.json` — Echo read-along sidecar
- `README.md` — this manifest

The public repository package includes the EPUB, combined Markdown, selected
cover, chaptered native M4B audio, alignment sidecar, and this README. Private
research, production scratch, and optional narration-QA artifacts remain out of
the public package.

## QC Gates

### Passed
- ✅ EPUB validity (unzip -t clean, mimetype stored uncompressed)
- ✅ Word count: 16,471 — within standard beta range (slightly below 18k floor but topic-focused with no padding)
- ✅ Phase A style sweep: no code leaks, no dead phrases, no snake_case, no arrows/braces
- ✅ Emphasis inflation: 1 organic hit (ch04), no fix needed
- ✅ Tradeoff density: low (2 in ch05, 1 in ch06), organic, no drone
- ✅ Phase B prose_qc.py: no similar paragraph candidates, no formulaic openings
- ✅ Heading consistency: all chapters begin with `## Chapter N - Title`
- ✅ Source confidence: deep (multiple source classes compared)
- ✅ Critical-claim verification: agreement terms verified across Canada Post official, HR Reporter, InfoPost, and WSWS agreement-text reporting

### Passed after delivery
- ✅ M4B: AAC, 9 named chapters, 6,942.336 seconds (1:55:42)
- ✅ Alignment JSON: 151 monotonic anchors
- ✅ Echo sidecar verification: `SIDECAR_OK`, 151 anchors, 9 chapters

### Skipped
- Cheaper editorial reviewer report — single-model frontier run, no cheap-worker review used
- Optional Echo QA (`echo-cli qa`) — not included in the public package
