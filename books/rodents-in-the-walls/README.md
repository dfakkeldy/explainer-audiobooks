# Rodents in the Walls

## Squirrels and Other Houseguests in Western Cape Breton

A public-safe custom learning audiobook for identifying, excluding, repairing after, and safely cleaning up around squirrels and other rodents in Western Cape Breton, Nova Scotia.

This corrected edition treats American red squirrels as a leading daytime candidate and northern flying squirrels as a plausible nighttime candidate. It does not assume the noises occur at night, and it treats timing as one clue rather than a verdict.

## Package

| File | Purpose |
|---|---|
| `rodents-in-the-walls.md` | Canonical reading manuscript |
| `rodents-in-the-walls.epub` | EPUB edition with embedded cover and chapter navigation |
| `cover.png` | Selected cover, 1600 × 2560 |
| `rodents-in-the-walls.m4b` | Echo audiobook, `am_michael`, 9 chapters |
| `rodents-in-the-walls.alignment.json` | Echo read-along sidecar |
| `rodents-in-the-walls.qa.json` | Sanitized deterministic narration-QA report |

The public repository package contains the Markdown, EPUB, selected cover, chaptered M4B, alignment sidecar, and this README. The narration-QA report and delivery checksums remain in the private delivery package.

## Edition details

- Canonical word count: 16,826 build words
- Chapters: 9
- Narration: Echo `am_michael`, ONNX render version 10
- Audio duration: 2:02:57.963
- Alignment: 245 anchors; 9 chapters; `SIDECAR_OK`
- Frontier author and substantive editor: `gpt-5.6-sol`
- Evidence extraction, diagnostics, packaging, and rendering: supporting tools and deterministic scripts
- Final build date: 2026-07-11 ADT

## Learning emphasis

The book teaches an evidence-stack method:

1. Record timing without turning it into an identity.
2. Trace the route through roof edge, soffit, attic, wall, cladding, and interior openings.
3. Combine sightings, camera evidence, gnawing, nesting material, droppings, tracks, season, and weather.
4. Check for dependent young before exclusion or closure.
5. Verify current Nova Scotia species and legal requirements before trapping, moving, or killing wildlife.
6. Repair failed substrate and building function, then add durable chew-resistant protection.
7. Clean rodent contamination wet, following current Canadian public-health guidance.
8. Monitor after repair and maintain the house without treating the surrounding habitat as the enemy.

## Regional and safety boundaries

- American red squirrels and northern flying squirrels are both treated as locally relevant.
- Eastern grey squirrels are not presented as the default Western Cape Breton squirrel.
- A flying-squirrel possibility stops do-it-yourself capture until species and permit requirements are confirmed.
- Active squirrel openings are not sealed until occupants and dependent-young risk are assessed.
- Poison is not recommended as a squirrel solution.
- The book does not provide individualized legal, medical, pesticide, structural, electrical, chimney, or wildlife-removal advice.

## Principal sources

- Nova Scotia Department of Natural Resources, **Squirrels — Nuisance Wildlife**: <https://novascotia.ca/natr/wildlife/nuisance/squirrels.asp>
- Nova Scotia Department of Natural Resources, **Flying Squirrels**: <https://novascotia.ca/natr/wildlife/conserva/flying-squirrels.asp>
- Nova Scotia, **Fur Harvesting Regulations**: <https://novascotia.ca/just/regulations/regs/wifurhrv.htm>
- Nova Scotia, **General Wildlife Regulations**: <https://novascotia.ca/just/regulations/regs/wigeneral.htm>
- Nova Scotia, **Nuisance Wildlife Permit**: <https://novascotia.ca/sns/paal/dnr/paal119.asp>
- Public Health Agency of Canada, **Hantavirus: Spread, prevention and risks**: <https://www.canada.ca/en/public-health/services/diseases/hantaviruses/prevention-hantavirus-infection.html>
- Health Canada, rodenticide mitigation material: <https://www.canada.ca/en/health-canada/services/consumer-product-safety/reports-publications/pesticides-pest-management/fact-sheets-other-resources/rodenticides-agricultural-settings/questions-answers.html>

The live provincial consolidations, permit page, and 2026–27 annual hunting and fur-harvesting summary were checked on 2026-07-11. Wildlife rules change; verify the current text before taking action.

## Verification

- EPUB ZIP integrity: passed, no compressed-data errors.
- EPUB metadata: title, subtitle, author, contributor, embedded cover, and 9 chapter documents confirmed.
- Cover: 1600 × 2560; selected from three original, rights-safe SVG concepts.
- M4B: title/artist/album tags confirmed; 9 named chapters; duration confirmed by `ffprobe`.
- Sidecar: native Echo verifier returned `SIDECAR_OK` with 245 anchors and 9 chapters.
- Independent review: high-priority factual, legal, and safety findings were repaired before final delivery. The revision removes unsupported entry rankings and chewing times, separates red-squirrel hunting from fur-trapping dates, identifies the property-damage exception without treating it as method permission, states Nova Scotia's prohibition on poisoning wildlife except rats, requires DNR or licensed-operator confirmation before a flying-squirrel exclusion device is installed, limits building repair guidance to supported principles and trade decisions, and separates PHAC's public cleanup sequence from contractor-specific remediation practice.
- QA qualification: `rodents-in-the-walls.qa.json` is the 221-diagnostic full-book baseline produced immediately before the final chapter-7 legal correction; the other eight audio chapters are unchanged. A fresh full Echo QA attempt was blocked when its transcription-model download timed out. Final chapter 7 was therefore checked separately with local offline ASR: the hunting and fur-trapping dates, 2026–27 season wording, property-damage exception, stand-alone-permission warning, flying-squirrel permit warning, Wildlife Act poison prohibition, and federal label rule were all detected. This is focused ad-hoc verification, not a fresh full-suite QA result.
- Final SHA-256 checksums are recorded in the delivered package as `SHA256SUMS`.
