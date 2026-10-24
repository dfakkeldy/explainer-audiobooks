# Beyond the Tax-Sale Packet: illustrated textbook edition

A plain-language rewrite of the 2026 book, laid out as an illustrated PDF and EPUB with the
textbook-pdf engine. The finished files are copied to
[`books/beyond-the-tax-sale-packet/illustrated/`](../../books/beyond-the-tax-sale-packet/illustrated/).

Dan asked for it on 2026-10-23: the first edition "over-qualif[ied] every paragraph" ("x
doesn't mean y"), and the textbook should have "lots of good infographics to get some points
across". Tracked in dfakkeldy/grok-bots#668.

## What changed from the first edition

- **Text.** Each chapter was rewritten from the published first-edition manuscript
  (`design/original/chNN.md`, split from `books/beyond-the-tax-sale-packet/beyond-the-tax-sale-packet.md`)
  under `design/rewrite-brief.md`. Sentences carrying a negative construction fell from 555 of
  2,317 (23%) to 50 of 1,838 (3%) (`python3 design/hedge_count.py src/chapters/*.md`). Chapter 1
  was written first as the voice model; Chapters 2–13 were rewritten in parallel against it. Every chapter
  writer left notes in `design/rewrite-notes/NN.md`: dropped or merged facts, qualifiers with
  legal weight that were reworded (old and new wording), and suspected errors in the original.
- **Figures.** 31 new infographics drawn for print (`design/infographics/*.html`, specs and
  captions in `design/figures.yaml`), plus two illustrations and six map screenshots kept from
  the first edition. Charts of past results use official municipal results from NS Marks The
  Spot's catalogue at revision `43e40b0b8`.
- **Chapter titles.** Four titles that were themselves qualifiers were renamed (see the brief).

The first-edition package (EPUB, M4B audiobook, alignment) in `books/beyond-the-tax-sale-packet/`
is unchanged. The audiobook narrates the first-edition text.

Open statute and sourcing questions for Dan are in `design/open-questions.md`. The earlier
October 9 textbook draft in `../nova-scotia-tax-sale-textbook/` is superseded by this edition.

## Result (2026-10-23)

149 pages, 13.3 MB PDF; 12.9 MB EPUB. `build/check_all.sh`: ALL CHECKS PASSED (footers, integrity,
source, breaks, leaks, EPUB with EPUBCheck 5.4.0: 0 fatal, 0 errors, 0 warnings). `pdffonts`:
TrueType only.

## Rebuild

```bash
cd docs/nova-scotia-tax-sale-illustrated
# one-time setup (venv, puppeteer-core, fonts): see the textbook-pdf skill's new_project.sh
node design/infographics/render.js            # infographics -> src/assets/figures/*.png
.venv/bin/python design/place_figures.py               # markers/captions from design/figures.yaml
.venv/bin/python build/build.py               # PDF + EPUB
EPUBCHECK_JAR=/path/to/epubcheck.jar build/check_all.sh
```

`check_all.sh` runs the engine's six checks: footers, integrity, source, breaks, leaks and the
EPUB (EPUBCheck 5.4.0).

## Layout

- `book.yaml` — title, cover, theme, edition, contents.
- `src/chapters/` — the text, one file per chapter, Pandoc Markdown with the engine's marks.
- `src/glossary.yaml` — every abbreviation and new term the page footers explain.
- `src/pronunciations.yaml`, `pronunciation-plan.md` — EPUB-only pronunciation markup (Pictou).
- `src/assets/` — cover band (cropped from the selected "Packet Lifts" art) and figures.
- `design/` — the rewrite brief, original chapters, rewrite notes, figure plan, infographic kit.
- `build/` — the textbook-pdf engine (one local change: hyphenated compounds stay whole in the
  cover title).
