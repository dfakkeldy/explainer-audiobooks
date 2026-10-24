# Infographic brief

The textbook edition of *Beyond the Tax-Sale Packet* needs many good infographics that each get
one point across. Dan's words: "let's make sure there are lots of good infographics to get some
points across." The old edition's 54 figures were 16:9 slides, and about 40 of them were the same
grid of small labelled boxes. Don't repeat that.

## What makes one good here

- **One point per figure.** Know the sentence the figure proves before drawing. The caption in
  `figures.yaml` states it.
- **Carry data or process.** A timeline with real durations, a decision tree with the real rule, a
  chart of real numbers, a plan-view drawing, a worksheet someone could copy. Not a grid of boxes
  with a heading and a sentence each.
- **Say what things are and do.** No "not proof / not access / not a survey" lists, crossed-out
  words or "does not" labels; that over-qualifying tone is exactly what this edition removes.
  Show where each answer comes from instead (a record, an authority, a professional).
- **Few words.** Labels, not paragraphs. Most text runs under 12 words.
- **No title inside the figure.** The book prints the caption under it. A small kicker or legend
  is fine.
- **Dated facts carry their date** in the figure or the source line.
- **Privacy:** no owner names, no street addresses of real tax-sale properties, no Property Online
  material. Composite cases (Harbour Road, Case A/B/C) are fictional; label them so once.

## The kit (use it; don't invent a new look)

- `design/infographics/kit.css`: fonts (Fig Sans = Atkinson Hyperlegible Next, Fig Serif = Source
  Serif 4, Fig Display for big numbers), colour tokens, `.panel`, `.card`, `.tag`, `.chip`-style
  pills, `.edge-*` card edges, `.src` source line, helpers.
- Colour meaning, used consistently across the book:
  - `--blue` the municipality, the process before the sale, official records;
  - `--aqua` the purchaser's side, after the sale, things confirmed;
  - `--orange` stop, flag, conflict, a real risk (sparingly);
  - `--yellow` open question or unknown (always with a text label: it is light);
  - `--navy` / `--ink` structure and text; `--ink2` secondary text; `--panel` cream grounds.
  Text is always ink, never a series colour (white text inside a dark fill is fine).
  These four were validated together for colour-blind separation; don't add new hues. Tints
  (`--blue-tint` etc.) for grounds.
- Size: `#fig` is 672 px wide (the printed text width). Height up to 690 px. Every label at least
  11 px. Design at actual print size; the renderer makes the 3x PNG.
- Charts: thin marks (bars <= 24 px thick, 4 px rounded data end, square at the baseline), 1 px
  hairline grid in `--hair`, direct labels on the marks that matter, a legend when there are two
  or more series, a log axis where values span orders of magnitude (label it plainly). Inline
  SVG is fine for charts and drawings; SVG `<text>` uses the kit fonts.
- A `.src` line at the bottom: the official source and date, in a few words.
- Data that drives a chart is embedded in the HTML (a small array in a `<script>`), with a comment
  naming the file and commit it came from.

## Files and commands

- Write `design/infographics/<id>.html`. Start from an exemplar:
  `fig-process-timeline.html` (process, two lanes) and `fig-inverness-reconcile.html` (data
  grid + tally). Both are approved.
- Render: `node design/infographics/render.js <id> [<id> ...]` from the project folder. It writes
  `src/assets/figures/<id>.png` (3x) and a 1x preview in `design/infographics/out/`. It fails on
  width, height > 690, overflow, text under 11 px, or fonts not loading.
- **Look at every preview PNG** (Read the file) and fix collisions, cramped text, awkward wraps,
  orphan words, and anything that reads as boxes-with-sentences. Iterate until it would look good
  in a printed book.
- Facts come from `figures.yaml` (`draw:` and `caption:`), `../nova-scotia-tax-sale-book/research/evidence-notes.md` and
  the data files named there. If the spec and the evidence disagree, follow the evidence and say
  so in your reply. Don't add facts that aren't in those sources.
- The old slides are in
  `books/beyond-the-tax-sale-packet/images/` (repository root)
  if you want to see what a figure replaces (improve on them; don't copy their layout).
