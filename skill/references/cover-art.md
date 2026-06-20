# Designing the cover

The cover should look like a **bestseller and show what the book is about through
an image** — not a generic template with the title on a colour. There is no
text-to-image tool here, so the illustration is authored as **bespoke vector art
(an SVG file) tailored to this book**, and `scripts/make_cover.py` drops it into a
premium layout.

## The flow: offer a couple of candidates, let the user pick

Don't auto-pick one cover. **Design 2-3 distinct candidates, render them, and let
the user choose** — cover taste is subjective and a render is cheap.

1. Come up with 2-3 *different* visual concepts for the subject (different central
   metaphor, not the same image recoloured). Optionally vary the layout too.
2. Author each as its own SVG art file (see the contract below).
3. Render each: `python3 scripts/make_cover.py --title ... --subtitle ... --author "Dan Fakkeldy" --art conceptN.svg --layout bleed --out <build>/dist/cover-N.png`
4. Send them all with `SendUserFile` and ask which they want (or to mix).
5. Assemble the EPUB with the chosen one via `build_book.py --cover`.

Default layout is **bleed** (full illustration + a gradient scrim carrying the
title — the trade-paperback look). `--layout hero` frames the illustration in a
panel over the book's signature hue; offer it as one of the candidates when a
quieter, more classic feel suits the subject.

## What makes the art good

- **One strong central metaphor** for the subject, the way a poster works. For a
  book on building apps with an AI assistant: an app under construction — a crane
  lowering a glowing piece into place, half the screen still a wireframe. For App
  Store Optimization: a single app icon found in a sea of grey ones. Pick the one
  image a reader would *get* at a glance.
- **Iconographic, not fussy.** Clean geometric shapes read at thumbnail size; fine
  detail turns to mud. Fewer, bigger elements win.
- **Limited, confident palette.** A dark backdrop, light line-work, and **one warm
  accent** reserved for the "alive"/important element (the glowing block, the found
  icon). Restraint is what reads as premium.
- **No text in the art.** The title, subtitle, badge, and author are added by the
  layout. Don't bake words into the illustration.
- **Legible small.** Squint at it — if the subject still reads, it works.

## The technical contract (so make_cover.py can place it)

- A complete `<svg viewBox="0 0 1200 1400"> ... </svg>` (that tall-ish ratio suits
  the cover). Any viewBox works; the script reads it.
- **Self-contained:** paint your own backdrop (a dark gradient `rect` covering the
  whole viewBox) so the art reads on any cover, rather than relying on transparency.
- **Keep key content centred** with margin. The `bleed` layout fills the cover by
  *slicing* (cropping the art's edges), so anything important near an edge can be
  cut. The `hero` layout fits the whole art inside a panel.
- **Namespace your ids** (gradients, patterns, filters) — e.g. `aaBg`, `aaGlow` —
  so they don't collide with the cover's own ids.
- Stick to plain SVG shapes, gradients, and patterns (no external fonts/images).
  `feGaussianBlur` works; a radial-gradient "glow" is the reliable way to make an
  element look lit.

A complete, working example ships beside this file: **`cover-art-example.svg`** (the
"app under construction" blueprint used for *You Are the Architect*). Read it as a
starting point, then design something specific to the book in front of you.
