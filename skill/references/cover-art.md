# Designing the cover

The cover should look like a **bestseller and show what the book is about through
an image** — not a generic template with the title on a colour. There is no
text-to-image tool here, so the illustration is authored as **bespoke vector art
(an SVG file) tailored to this book**, and `scripts/make_cover.py` drops it into a
premium layout.

Aim for a professional audiobook-store shelf, not an internal-doc thumbnail:
clear at small size, polished enough to sit beside commercial Audible-style
audiobooks, and specific enough that the listener can remember which book it is.
The cover should feel like a product people would choose, not merely a generated
artifact.

## The flow: offer a couple of candidates, let the user pick

Don't auto-pick one cover. **Design 2-3 distinct candidates, render them, and let
the user choose** — cover taste is subjective and a render is cheap.

1. Come up with 2-3 *different* visual concepts for the subject (different central
   metaphor, not the same image recoloured). Optionally vary the layout too.
2. Include at least one bright/high-key candidate when the subject allows it.
   Premium does not always mean dark; a bright shelf cover can feel more modern,
   friendly, and giftable.
3. Choose one **signature accent colour** for each concept. It should come from
   the cover idea itself — the glowing part, found object, route line, flower
   centre, alert mark, or other "alive" element — not from the title text.
4. Author each as its own SVG art file (see the contract below), using its
   signature accent as the most memorable colour in the art.
5. Render each: `python3 scripts/make_cover.py --title ... --subtitle ... --author "Dan Fakkeldy" --art conceptN.svg --accent "#2ee8b6" --tone bright --layout bleed --out <build>/dist/cover-N.png`
6. Send them all with `SendUserFile` and ask which they want (or to mix).
7. Assemble the EPUB with the chosen one via `build_book.py --cover`.

Default layout is **bleed** (full illustration + a gradient scrim carrying the
title — the trade-paperback look). `--layout hero` frames the illustration in a
panel over the book's signature hue; offer it as one of the candidates when a
quieter, more classic feel suits the subject. Use `--tone bright` for a high-key
cover and `--tone dark` for a cinematic cover; vary tone across candidates when
that gives the user a real choice.

## What makes the art good

- **One strong central metaphor** for the subject, the way a poster works. For a
  book on building apps with an AI assistant: an app under construction — a crane
  lowering a glowing piece into place, half the screen still a wireframe. For App
  Store Optimization: a single app icon found in a sea of grey ones. Pick the one
  image a reader would *get* at a glance.
- **Iconographic, not fussy.** Clean geometric shapes read at thumbnail size; fine
  detail turns to mud. Fewer, bigger elements win.
- **Professional audiobook hierarchy.** At 160px wide, the viewer should still
  read the title shape, understand the central image, and feel one emotional hook.
  Use scale, contrast, and negative space like a real store cover.
- **Limited, confident palette.** Use a controlled backdrop — either dark and
  cinematic or bright and high-key — with **one vivid signature accent** reserved
  for the "alive"/important element (the glowing block, the found icon, the
  route, the flower core). Restraint is what reads as premium.
- **Sell the derived accent colour.** Echo and library UIs may derive a colour
  from the cover image. Make that colour unmistakable: repeat the same accent in
  the art, badge, rule, glow, or edge treatment, with enough visible area to
  influence the thumbnail, but not so much that the cover becomes one flat colour.
- **No text in the art.** The title, subtitle, badge, and author are added by the
  layout. Don't bake words into the illustration.
- **Legible small.** Squint at it — if the subject still reads, it works.

## Cover acceptance bar

Before showing candidates, reject any render that fails one of these:

- It would not look credible beside professional audiobook marketplace covers.
- The art could be mistaken for a slide icon, diagram, logo, or placeholder.
- The title and central image do not read at thumbnail size.
- The accent colour is only a tiny trim detail, or the cover is dominated by a
  dull one-note background with no memorable accent.
- Every candidate is dark by default when the topic would benefit from a bright,
  inviting marketplace cover.
- The candidates are merely recolours of the same composition.

## The technical contract (so make_cover.py can place it)

- A complete `<svg viewBox="0 0 1200 1400"> ... </svg>` (that tall-ish ratio suits
  the cover). Any viewBox works; the script reads it.
- **Self-contained:** paint your own backdrop (a dark gradient `rect` covering the
  whole viewBox) so the art reads on any cover, rather than relying on transparency.
- **Accent-aware:** use the same hex accent in the SVG and in
  `make_cover.py --accent`. The layout will carry that colour into the badge,
  accent stripe, title rule, and glow so the final cover's derived colour is
  intentional.
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
