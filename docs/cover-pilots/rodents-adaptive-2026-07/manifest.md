# Rodents Adaptive Cover Pilot — July 2026

## Approval and design source

- Approved direction: **C2A — Compact Ribbon / Editorial Footer** (`c2a-compact-ribbon-editorial-footer`).
- Approval: Dan explicitly approved C2A on 2026-07-12 as a requested mix refining C2.
- Governed selection timestamp: `2026-07-13T00:07:44-03:00`; selection source: `requested-mix`.
- Design and implementation plan: [Adaptive Cover Specification](../../superpowers/plans/2026-07-12-adaptive-cover-specification.md).
- Source artwork: approved blue-plaster wall, orange exposed plaster, branching rodent shadows, and central broken opening; SHA-256 `cced16a14a0aaced901af7ffd0b140c4d6e13fdf88bd3da22a9724fb7bad9812`.
- Pilot exception: one source artwork was intentionally reused across all four directions to isolate compositor, typography, hierarchy, and material-language quality. This does not change the normal requirement for candidate sets to vary art metaphor, crop, palette, and title strategy.

## Reviewed directions

| Direction | Candidate ID | Specification SHA-256 | Render SHA-256 | Render receipt SHA-256 |
|---|---|---|---|---|
| C1 — Full-Bleed Display | `c1-full-bleed-display` | `29faf90137a3c36c72fb21464ec8a231a52391284cbef568b73f3549a3fa1ada` | `ead6f55c9aafbead95cc0a75d472dedea9d885a9a2cde25ea637f6d99affac2a` | `cb67fe06338bf3327e0866ac66d3ed199873c13bcf5bc4adc87a99246e39a2fc` |
| C2 — Integrated Colour Band | `c2-integrated-colour-band` | `d781b0a02bb9ed3a3b1e3072ea7f0008e09b12f04701e1569245d371a778d528` | `6d1b0cfc6f0437797219afdbaa0126075e6aa668274dc49fbbac2fcd0d5dd185` | `41778134655efd4cb84ae939f4f8f0956ab0913ccc007f6eaed55a0046d7c4ad` |
| B1 — Shadow Branches | `b1-shadow-branches` | `58817913120442c791308ac0bdf28daf794e346f8d1641a02da4264b57f65636` | `6f9e5e9e174c3b5384d45233a8e4d861ea631507ba4f2ded0f31675c34e5bf04` | `ff8ed9a73f6c11ed087effdf1a7b74b4d028c960a1ab1f273b6ffb2a0b1b6c1c` |
| C2A — Compact Ribbon / Editorial Footer | `c2a-compact-ribbon-editorial-footer` | `917f7f7b6866e668c3da8b144609ecf093d111112c0177d2d92a179678fc53e3` | `e1afe1fbcbd440927c8d4d62de475af3230afe0d8edbbb6a886c498fc21af2a2` | `5a1bf0a0da298cac6779479b073843deca8dd8503a92c52a498508e53f3d00ea` |

The committed four-direction [contact sheet](contact-sheet.png) has SHA-256 `0c030c9e99b234184ce14cb49438df91cc2b9aefdd902b04956fda898e943694`.

## Pinned font roles and licences

| Font ID | Family | Role in C2A | Licence |
|---|---|---|---|
| `editorial-serif` | Fraunces | `RODENTS` editorial display | OFL-1.1 |
| `geometric-sans` | Space Grotesk | `IN THE` and subtitle | OFL-1.1 |
| `display-condensed` | Barlow Condensed | `WALLS` | OFL-1.1 |
| `technical-mono` | IBM Plex Mono | label and author | OFL-1.1 |

The font manifest is hash-pinned; its SHA-256 is `5c905e1ab6642b14d341a450be01e12a54f541a775e0e63410765ae87e11947f`.

## Visual review

- Full size: PASS — the compact ribbon clears every silhouette, no title element covers a shadow, the central opening and complete branch composition remain the second read, and the editorial footer is a soft gradient-supported lockup rather than a hard container.
- 160 × 256 thumbnail: PASS — `RODENTS / IN THE / WALLS` is immediate and ordered; cream `WALLS` remains crisp with its navy outline despite the retained 2.97:1 advisory.
- Metadata and bounds: PASS — title, subtitle, author, and label spelling are exact; all effects remain inside the 96-pixel safe margin.
- Comparative result: PASS — C2A is less template-like than C2 while retaining the approved artwork at full scale.

## Edition-specific promotion verification

- Public `corrected-v2`: receipt SHA-256 `d1c87d54233960540be9baa5e82c7a816718c212d332ae8f8b3364b3b6643ea9`; standalone cover bytes, EPUB cover bytes, M4B normalized pixels, and receipt identity verified. The public M4B retained audio packet SHA-256 `76a4c4a8461de8251eaf81e62264ed0dc6573feadae524474b6c3b5a9e8dff10`, duration `7377.962667`, three stream codec/type pairs, nine chapter boundaries/titles, and all format tags.
- Separate iCloud `v3`: receipt SHA-256 `eb4e82681504d1477b87a80f297ca9b8395cd4cd42ef2852c4d0f829fbecbca9`; the same four cover/receipt checks passed. The v3 M4B retained audio packet SHA-256 `088c2891354d1790e784cbb8637eb6524307f48a6c72f100c20f34d353955f8f`, duration `5464.661333`, three stream codec/type pairs, nine chapter boundaries/titles, and all format tags.
- The editions were refreshed independently; no EPUB or M4B was copied between public corrected-v2 and iCloud v3.
- Governed iCloud sync returned `supersede-unreceipted` in dry-run and apply modes. Exactly `cover.png`, `rodents-in-the-walls.epub`, `rodents-in-the-walls.m4b`, `cover-selection.json`, `README.md`, and `SHA256SUMS` changed; alignment, QA, Markdown, figures, and all unrelated files remained byte-identical.
