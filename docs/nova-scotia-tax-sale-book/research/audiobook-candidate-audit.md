# Governed audiobook candidate audit

Date: 2026-07-21

## Decision

The existing 3:57:37 Echo ear-pass render is valid diagnostic evidence, but it
cannot be promoted byte-for-byte as the governed full-audiobook candidate. A
controlled rebuild is required from the frozen public EPUB through the governed
narration wrapper.

This decision does not reopen or change the approved manuscript. It also does
not authorize audiobook publication.

## Evidence retained from the ear pass

- Renderer: Echo rv15
- Voice: `am_michael`
- Chapters: 13
- Duration: 14,257.408 seconds (`3:57:37.408`)
- M4B SHA-256:
  `1eaa015503f2f389182c5d5358350921695eec8e0ecba993b677ab4e833df320`
- Alignment SHA-256:
  `0d1d9897552c2251286b66c02c7ce4cd91972d96572a0d08cc315efacaee6cc7`
- Pronunciation-audit SHA-256:
  `2f11a93eaf695ac39d54722ae809f4133fa649ba7c3b49244400f5ef07d3eaf0`
- Pronunciation-reel SHA-256:
  `25b80285dc805220abc3ede7bbec05391743dd1da497b30eccb72385763edb0b`
- Alignment: 612 anchors, including 324 verified word-timed anchors
- Acoustic scan: no silence event at least three seconds below -45 dB
- Full decode: passed
- Canonical chapter comparison: all 13 chapter files matched byte-for-byte

These findings remain useful as a baseline for the controlled rebuild. They do
not replace the new candidate's own alignment, pronunciation, cover, decoding,
integrity, and receipt checks.

## Why the existing M4B is not promotable

1. Its receipt classifies it as `learning-pilot-nonpackage` and leaves listener
   acceptance pending.
2. It is bound to source EPUB SHA-256
   `acf8842c09bf50d70b3582907430b0d67c44627da270a5ac595171a42b17568e`,
   not the frozen public EPUB SHA-256
   `40049b5e7bac13657d5b1417fc1dbac25f6c3d02587c3c484e2e49dc73003bd0`.
3. It has no accepted-current selector and no current governed delivery-receipt
   chain.
4. It does not bind the selected square *The Packet Lifts* cover into the M4B.
5. The committed pronunciation plan had drifted from the final manuscript: four
   planned forms no longer appeared in their declared chapters. The controlled
   run corrects that plan without changing manuscript bytes.

## Controlled-rebuild contract

- Source EPUB: the exact frozen public EPUB above
- Manuscript: 13 canonical chapters, 31,824 Markdown words, byte-for-byte frozen
- Narrator: `am_michael`
- Renderer: installed pinned Echo source
  `58cf8c2b8d02d883704413f9bb487a296ddddd63`, rv15
- Renderer CLI SHA-256:
  `5e68cf2ac67f20dd29dd07031421cf9ad5f782c0d02d29eb127eeb1cef0b9fb7`
- Renderer resources SHA-256:
  `7dc8c5f635f5fe451156a9ba842650d44e01acadf52a20cdfac5fecaed78777b`
- Selected square cover SHA-256:
  `350a78085825b8cadcf706d0be7355cc7020030b5cf86b90a5376aea3eeb707c`
- Assurance level: `unattended-first-listen`
- Human pronunciation listening: pending
- Human full-audio listening: pending
- Audiobook publication permission: not granted

The controlled run may produce a private listening candidate and its portable
receipts. It may not publish an audiobook, change the website, start the video
edition, promote figures, or claim second-device proof.

## Controlled-rebuild outcome

The rebuild completed through the governed wrapper on 2026-07-21 and advanced
to the full-audio human gate:

- M4B SHA-256:
  `f117bb2016b2b7bc58e900130a03b37d66452afff7e6a9ac0f81d1816dd706ec`
- Duration: 14,257.408 seconds (`3:57:37.408`)
- Chapter markers: 13, in canonical order
- Alignment: 612 anchors, 324 with verified word timings
- Automated pronunciation audit: complete coverage, 235 decisions, zero
  diagnostics
- Selected square-cover identity: pass
- Selector-bound schema-v3 delivery chain: pass
- Full audio decode: pass
- Silence scan: no event at least three seconds below -45 dB
- Copied private listening package: verified in place

The optional Echo database QA consumed the complete capture set but emitted no
report and became non-progressing after 11 minutes, so that optional process was
stopped and is recorded as inconclusive. It does not override the mandatory
passed gates, and it is not represented as a pass.

Human pronunciation listening and the entire-book listening verdict remain
pending. The candidate is not published.
