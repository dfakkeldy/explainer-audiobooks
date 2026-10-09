# Engine changes made for this book

The engine in `build/` started as the textbook-pdf template with EPUB output
(`/workspace/taxbook/cs/textbook-pdf`). These changes were made during assembly (9 October 2026).
Most are generally useful and are candidates to carry back into the skill; the book-specific ones
are marked.

## New components (`build.py` `Blocks.division`, CSS in `theme.py`, both PDF and EPUB)

| Mark | What it prints | Breaking |
|---|---|---|
| `::: {.objectives}` | A list with the rail label "You will learn to" | atomic |
| `::: {.keyterms}` | Terms as small chips, rail label "Key terms"; glossary marks abbreviations only (terms are defined where the chapter first uses them) | atomic |
| `::: {.chain links="a,b"}` | The research-chain strip: five tabs (notice, parcel, context, unknowns, handoff), the named links filled. The source sentence "Research chain: … handoff." becomes the strip, keeping its words in order; the rest of the paragraph follows as a grey line | atomic |
| `::: {.case name="…"}` | A worked-case box: kicker "Worked case", the name, the "Composite case — …" line in italics, then the text. File notes inside become cards | atomic under 350 characters; longer boxes split, the continuation headed "Name (continued)" |
| `::: {.filenote case="…"}` | The File Note index card: tab "File note · case", then a ruled row for each paragraph that opens with a bold `Label:` | atomic under 900 characters |
| `::: {.recall}` | A note panel headed "Quick recall" | atomic under 900 characters |
| `::: {.check}`, `::: {.summary}` | A ruled heading ("Check your understanding", "Chapter summary"), not in the contents, and the list | splits between items |

Labels are in `theme.DEFAULT_LABELS` (`objectives`, `keyterms`, `chain`, `case`, `filenote`,
`recall`, `check`, `summary`, `figure`) and can be renamed in `book.yaml` `labels:`.

## Build

- **Figure numbers:** `figure_numbers: true` puts "Figure 6.2" before each caption, numbered within
  the chapter from its `label`.
- **Heading ids:** a `## Heading {#id}` keeps its id, so cross-references (`[…](#sec-06-route)`)
  work in the PDF and the EPUB.
- **Abbreviations inside SVG figures:** their text is real text in the PDF, so the build reads each
  SVG and adds hidden term marks to the figure; the page footer then spells them out (removed in the
  EPUB, whose notes come from the text).
- **Glossary words inside links:** marked unless the link's visible text is a web address.
- **Explicit `deps:`** in a glossary entry now also apply to the short (reminder) form.
- **Chapter front matter `gloss: false | acronyms`:** no glossary marks, or abbreviations only (for
  reference pages: the cases table, the statutes index, the figure list, the sources). Contents rows
  are abbreviations-only.
- **Long lead-ins:** a paragraph ending with a colon is kept with what follows up to 600 characters
  (was 160).
- **Print copies of large rasters:** `images: {max_px, format, quality}` resizes wider images into
  `out/img/` with ImageMagick (sources untouched). Here: 1800 px JPEG at quality 88, 4:4:4. This took
  the PDF from 100 MB to 23 MB and the EPUB from 63 MB to 9 MB.
- **Poster cover:** `cover_mode: poster` (with `cover_ground`, `cover_ink`, `cover_accent`) shows
  finished cover art that already carries the title whole and uncropped, with the kicker and date
  beneath it and the title as hidden text. Used for the frozen 2026 cover.

## Paginator (`paginate.js`)

- **Floating figures:** a figure that does not fit on a page that already has text goes to the top
  of the next page while the following text fills the gap. It never floats past a section heading,
  a chapter opening or another figure. This removed about 15 pages of blank space.
- **Footer-held space:** after a split, the paginator tests whether more could have stayed; if the
  fuller copy fails only because the footer grows, the space is recorded as `data-held`, which
  `check_breaks.py` already allows for. If it fits, the fuller split is kept.
- **Lead-ins:** consecutive lead-ins (a component's head and sub-line, class `lead`) move together.
  A long lead-in closing a keep-with-next group may split, its last lines going over with what it
  introduces. A text split never ends a page on a line ending in a colon.

## Checks

- `check_integrity.py` compares figures as their own sequence (they may float), then the remaining
  words in order.
- `check_footers.py` accepts `checks.not_acronym_patterns` (regexes) for code families; here,
  evidence-note identifiers such as `LAND-003`.

## Book-specific

- `review/tools/make_backmatter.py` generates Appendix C (statute provisions, curated by hand inside
  the script, and official sources by chapter and section), Appendix D (the figure list) and the
  Sources chapter from the source notes and the packet's source register.
