# Figure style

Written 9 October 2026 with Chapter 1, the first chapter drawn. Binding on every REDRAW and NEW
figure; read with `design/design-brief.md` (palette, credibility rules) and the "Figure review
gate" at the end of `design/chapter-plan.md`. The helper `figures/svgkit.py` implements this spec;
use it unless a figure needs something it cannot do.

## 1. Files

- Source of record: `src/assets/figures/<fig-id>.svg`, one per figure, id = file stem
  (`fig-CC-slug`). Self-contained: no external references, no `<image>` links, no web fonts by URL.
- Generator scripts: `figures/<fig-id>.py` (or one script per chapter), run with the project venv
  (`.venv/bin/python figures/ch01_figures.py`) because the helper uses fontTools. Hand-written SVG
  is allowed; it must still meet this spec.
- Kept rasters: copied (never moved) into `src/assets/figures/kept/`, pixels untouched.
- Data a figure is drawn from (e.g. simplified boundaries) lives in `figures/data/` with its
  source, licence and download date recorded in the file and in the caption's credit line.

## 2. Canvas

SVG user units are CSS pixels at print size (96 px/in): a 672-unit-wide figure prints 7 in wide,
so every size below is the printed size.

| Format | viewBox width | Heights (pick one) | Use |
|---|---:|---|---|
| Full width | 672 | 224 (short strip) · 300 (1/3 page) · 420 (1/2 page) · 560 (2/3 page); ± about 60 when the content needs it (Chapter 1 uses 352–470) | default |
| Half width | 324 | 224 · 300 · 420 | side-by-side pairs (two halves + 24 gutter = 672) |

- Ground: a white rectangle under everything (so EPUB readers in dark mode and greyscale checks
  see the figure as printed). No frame around the whole figure.
- Inner margin: keep 8 units clear on every edge; nothing may touch the viewBox edge.
- Title, caption, figure number and credit are **not** drawn in the SVG; they come from the
  Markdown caption. The only text inside is labels, legends and short in-figure notes.

## 3. Type

- Family: `Atkinson Hyperlegible Next` (the static cuts in `fonts/static/sans-400-latin.ttf` and
  `sans-700-latin.ttf`), fallback `'Atkinson Hyperlegible', sans-serif`. The helper embeds a
  glyph subset of both weights as `@font-face` data URIs so the SVG renders identically in
  Chrome (`<img>` cannot load page fonts) and in EPUB readers. For `rsvg-convert` previews, point
  fontconfig at `fonts/static` (`figures/fonts.conf`).
- All text is real `<text>`; never outlined, never rotated except axis titles, never all caps.

| Role | Size | Weight | Colour |
|---|---:|---|---|
| Box / station heading | 13 | 700 | ink `#1d1c1a` or the state colour |
| Label, body of a box | 12 | 400 | ink |
| Secondary note, legend, "not to scale" | 11 | 400 | ink2 `#4a4843` |
| Large hinge word (one per figure at most) | 18 | 700 | white on accent or ink |

Minimum 11 units anywhere (≈ 8.25 pt). Line height 1.3 × size. Wrap with the helper's measured
wrapping; no line closer than 4 units to a box edge.

## 4. Colour

Book tokens (design brief):

| Token | Hex | Figure use |
|---|---|---|
| ink | `#1d1c1a` | text, neutral strokes |
| ink2 | `#4a4843` | secondary text |
| rule | `#cfcac0` | hairlines, base-map unit edges, grid |
| accent (harbour teal) | `#1f5560` | figure strokes, arrows, emphasis |
| accent_tint | `#e6eef0` | box grounds, highlighted map units |
| accent_mid | `#9db8bf` | secondary fills, empty links |
| caution (buoy red) | `#a33b28` | no-go only |
| caution_tint | `#f6e8e3` | no-go grounds |
| granite | `#6b6a66` | neutral elements, "not a survey" / "not to scale" stamps |
| paper2 | `#f3f1ec` | non-highlighted base-map units, neutral bands |

Evidence states (always with their greyscale cue):

| State | Hex | Cue |
|---|---|---|
| Municipal fact | `#24395a` | solid fill tab (a 6-unit filled bar on the box's left or top edge) |
| Verified added public record | `#1f6b6e` | solid 1.5 outline |
| Screening clue / visual interpretation | `#b07d17` | dotted outline (`1.5 2.5`, round caps) |
| Unresolved / professional verification | `#7a3e6e` | dashed outline (`6 4`) + "?" glyph |
| No-go until resolved | `#a33b28` | 3-unit outline + bar glyph |
| Process complete / reconciled | `#2f5e46` | check glyph |

Text colour on a tinted ground is ink; white text only on `#24395a`, `#1f5560` or `#1f6b6e`
fills (all ≥ 7:1). Amber `#b07d17` is never used for text (3.3:1); label it in ink beside the
mark.

## 5. Lines and marks

- Strokes: hairline 0.75 (`rule`); standard 1.5; emphasis 2.25; no-go 3. `stroke-linejoin: round`.
- Arrows: one marker, a filled 8 × 8 triangle (`refX` at the tip), coloured to match its line via
  per-colour markers (`arrow-<hex>`). Arrowheads stop 3 units short of the target box.
- Boxes: square corners or a 3-unit radius (no pill shapes, no drop shadows, no gradients, no
  coloured left-border "cards" except the municipal-fact tab, which is a state cue).
- **Uncertainty, conditions and alternatives are dashed** (`6 4`), always with a text label saying
  what is uncertain or conditional ("older-arrears route: no six-month redemption"). Solid means
  the default path or a stated fact. Never let dashing be the only carrier of meaning.
- Spans of time (minimum periods) are drawn as a bracket or bar with the period printed on it
  ("at least 14 days"), and the figure says "Not to scale" whenever spans are not proportional.
- Map symbols: solid dot r 6 (auction), square 11 × 11 (tender), half-filled dot (both), open
  ring r 6, stroke 2 (check the current notice). Labels 12/700 name + 11/400 method below.

## 6. Greyscale and contrast test

Before a figure is accepted, render it (`rsvg-convert -w 1400`), then render a greyscale copy
(`magick in.png -colorspace Gray out.png` or PIL `convert("L")`) and check that every state is
still distinguishable by its cue, every label is readable, and nothing relies on hue alone.

## 7. Content rules (from the plan; repeated because figures are where they slip)

- Every label traces to the original figure, its caption/alt text, or the manuscript lines cited
  in the chapter plan; the chapter's claims ledger lists them (type G).
- Composite plates carry "Composite — not a real property; not a survey."
- Dated facts carry their date inside the figure or in the caption.
- No scores, rankings, meters, bargain language, gavels, dollar signs, or real PIDs beyond the five
  the original prints.
- Alt text says what a sighted reader learns, not what the picture looks like.

## 8. Review loop

1. Generate SVG. 2. `rsvg-convert -w 1400` to `/tmp`, look at it at full size. 3. Fix overlaps,
clipping, crowding, contrast. 4. Greyscale check. 5. Run the helper's `check()` (text inside
viewBox, minimum size, no external references). Repeat until clean.

## 9. Case plates (added with Chapter 6)

The Case A plates (fig-06-case-a-*, and fig-07-case-a-screening) share `figures/case_a_plate.py`:
672 × 340, map panel 424 × 300 at (8, 30), right rail of 2–3 cards 216 wide at x 448; the
composite stamp "Composite — not a real property; not a survey." in 12/700 above the map; land
`paper2`, water `accent_tint` with an `accent_mid` shoreline; public roads `ink2` 4.5–5 wide;
lot lines `granite` 0.9; north arrow and "Not to scale" in every plate. The parcel itself is a
screening exhibit: dotted-state amber outline 2.25 on a pale amber tint `#f7efdc` (the one tint
added to the palette; text on it is ink). Zones: verified teal hatch with a solid edge for a named
zone; a dashed unresolved outline with "?" for an unconfirmed one. Rail card styles map the
original card colours to evidence states (amber → dotted, magenta → dashed + "?", teal → solid);
a neutral limit card is granite 2.25, never red. Case B and C plates can follow the same layout
with their own geometry module.
