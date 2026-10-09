# Beyond the Tax-Sale Packet — Textbook Edition (DRAFT)

**Status: draft awaiting Dan's review. Not governed-final.** This is a textbook edition, for print and
e-readers, of Dan Fakkeldy's *Beyond the Tax-Sale Packet: How Nova Scotia Municipal Auctions Really
Work*. It was rewritten for the page and designed with Claude Opus 5.5 from the 2026 governed-final
audio-first edition. The published text-and-audio edition in `books/beyond-the-tax-sale-packet/` and
its development packet in `docs/nova-scotia-tax-sale-book/` are unchanged.

- `beyond-the-tax-sale-packet-textbook.pdf`: US Letter, 324 pages, 22.8 MB.
- `beyond-the-tax-sale-packet-textbook.epub`: EPUB 3, 8.9 MB.

Facts are as of July 22, 2026, the same as the 2026 edition; nothing was refreshed. The material is
educational only and is not legal or other professional advice (see About this book in the PDF).

## What's in it

- The same 13 chapters in the same order, with descriptive titles (the original titles are kept as
  kickers), written for reading rather than listening.
- Textbook apparatus: research-chain strip, learning objectives and key terms on each opening;
  worked-case boxes for the composite cases; File Notes; Careful panels; Quick recall boxes; a source
  note closing each section; chapter summaries; 70 questions answered in Appendix A.
- Front and back matter: About this book, The Cases in This Book, Appendix A answers, Appendix B
  blank worksheet, Appendix C index of statutes and official sources, Appendix D list of figures,
  glossary, Sources and Credits.
- **Figures: 78.** 16 kept from the 2026 edition (2 illustrations, 14 map screenshots with
  magnified insets), 38 redrawn as SVG, 24 new. The kept and redrawn figures cover all 54 figures of
  the 2026 edition.
- Every page of the PDF spells out the abbreviations on it, and defines new terms, in its footer.

`review/dehedge/` records the plain-language de-hedging pass (October 9, 2026). `review/DIFF-SUMMARY.md` summarizes what changed. `review/changes/` has the per-chapter notes,
`review/claims/` the claim ledgers, and `review/flagged-claims.md` the open questions about the
original's facts (kept as printed). `review/open-questions.md` lists the form and scope decisions
taken by default. `review/assembly-log.md` records the build phase.

## Rebuild

Needs Python 3, Node, pandoc, poppler (`pdftotext`, `pdftoppm`), ImageMagick (for the print copies of
the screenshots; without it the build uses the full-size PNGs) and Google Chrome (or set
`CHROME=/path/to/chrome`). EPUBCheck needs Java; use the current release from
github.com/w3c/epubcheck (Debian's packaged 4.2.6 is old).

```bash
python3 -m venv .venv && .venv/bin/pip install -r build/requirements.txt   # once
(cd build && npm install)                                                  # once
.venv/bin/python build/fonts.py        # only if fonts/ is missing or the fonts in book.yaml change
.venv/bin/python review/tools/make_backmatter.py   # after editing source notes or figures (Appendix C, D, Sources)
CHROME=/usr/bin/google-chrome .venv/bin/python build/build.py
EPUBCHECK_JAR=/path/to/epubcheck.jar build/check_all.sh
```

`fonts/` (0.9 MB, static cuts of Source Serif 4 and Atkinson Hyperlegible Next under the SIL Open
Font License) is kept so the book rebuilds without a network.

## Where things are

- `book.yaml`: title, poster cover (the frozen 2026 cover art, `src/assets/cover.png`, shown whole),
  colours, fonts, image print settings, the single public edition and its forbid list.
- `src/chapters/`: `00-about.md`, `00b-cases.md`, chapters `01`–`13`, `97-answers.md`,
  `98-worksheet.md`, the generated `98b-statutes-and-sources.md`, `98c-figures.md` and
  `99-sources.md`. `src/appendix-answers/` holds the per-chapter answer fragments merged into
  `97-answers.md`.
- `src/glossary.yaml`: the footer glossary. `src/assets/figures/`: SVG figures and, in `kept/`, the
  2026 edition's PNGs byte-for-byte.
- `figures/`: the scripts that drew the SVG figures. `design/`: design brief, chapter plan, figure
  style.
- **Sources:** each section's source note cites the 2026 edition's source register
  (`docs/nova-scotia-tax-sale-book/research/sources.md`, by number) and its evidence notes
  (`research/evidence-notes.md`, by identifier such as LAW-007). The Sources and Credits chapter lists
  the cited register entries with links.
- `build/`: the engine (template plus EPUB output, extended for this book; see
  `review/engine-changes.md`) and the checks.

## Check results (9 October 2026)

`build/check_all.sh` prints **ALL CHECKS PASSED**:

- Footers: every abbreviation on all 324 pages spelled out in that page's footer.
- Integrity: every one of 66,168 words placed once, in order (figures compared as their own sequence,
  since they may float to the next page).
- Source: all 3,187 source blocks present.
- Breaks: no stranded headings or lead-ins, no early splits, no overflow. One nearly empty page
  is reported (p. 135).
- Leaks: the 7 forbidden patterns (stray eight-digit identifiers, a mine-record name and civic
  address the original never prints, owner names after a field label, statements about the map's
  ownership, a real road name kept only in alt text, the map's source repository) absent from the PDF
  and EPUB.
- EPUB: **EPUBCheck v5.4.0, 0 fatal, 0 errors, 0 warnings**; text and marks identical to the PDF
  flow; all source blocks present.

The checks test layout and fidelity to the source files. They do not prove the facts; the
adversarial fact-preservation audit (`review/audit-log.md`, per-chapter reports in `review/audit/`)
found 0 high, 23 medium and 67 low findings; the medium ones (dropped or hardened qualifiers and
unsourced apparatus wording) are all fixed. `review/flagged-claims.md` holds 54 entries (22 open).

## Known limits and decisions

- The book is longer than planned (324 pages against an estimate of 170–200), because the text and
  apparatus came to about 66,000 words against an estimate of 40,000–46,000.
- The kept screenshots print from 1800 px JPEG copies (about 257 dpi at the 7 in column) made at
  build time. The source PNGs are unchanged; full-size PNGs pushed the PDF over 100 MB.
- No pronunciation lexicon: the packet's pronunciation plan holds only candidate respellings, none
  accepted, so no IPA was added.
- The About page does not describe who owns NS Marks The Spot (open question Q13 is overridden), and
  the Sources chapter does not print the map's repository link.
