# Slideshow figure production

This directory holds editable, deterministic source for the Nova Scotia
tax-sale book's 16:9 diagrams. The rendered PNGs live under
`../chapters/images/`, where the governed EPUB build will eventually consume
them.

The current batch covers figures 03 through 08 plus figures 39 and 40: the
legal/process and record-research sequence for Chapters 1–3, the Chapter 9
payment-performance clock and the Chapter 11 surplus-proceeds route. They are
**review candidates**, not accepted
book figures. They use no owner information, live property recommendation,
Property Online reproduction, raw provincial geometry or cached aerial tiles.

Render with the repository's Pillow-capable Python:

```bash
/usr/local/bin/python3 \
  docs/nova-scotia-tax-sale-book/figures/render_slideshow_figures.py
```

The renderer creates eight 2560×1440 sRGB PNGs, a large contact sheet, a
640×360-per-frame phone-stage contact sheet and a hash-bound render receipt. The
machine-readable `figure-specs.json` records each figure's teaching job,
caption, alt text, evidence claim IDs, legal locators, rights status and current
review state.

Before any candidate becomes accepted:

1. Re-check its factual labels against the cited official source.
2. Inspect the full-size PNG plus both contact sheets.
3. Test the figure in Echo at phone and desktop sizes.
4. Watch the short Karaoke/Simple export proof with the eventual caption and
   narration cue.
5. Change its manifest status only after that review.

These diagrams are educational process summaries, not legal advice. Current
law and the municipality's event-specific terms must be checked at the time of
use.
