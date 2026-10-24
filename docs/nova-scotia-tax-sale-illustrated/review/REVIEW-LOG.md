# Review log

## 2026-10-23/24, build for Dan's review (Claude Opus 5.5)

- Rewrite: each chapter's writer checked its own hedge count (`design/hedge_count.py`) and wrote
  `design/rewrite-notes/NN.md`. Claude read Chapters 1, 3, 9 and 13 in full and spot-checked the
  rest, checked that substitutes ("rather than", "without", "stops short of") did not replace the
  removed negatives, and confirmed every composite name comes from the first edition.
- Figures: each designer rendered and inspected every figure at print size; Claude reviewed all 31
  on two contact sheets and corrected four captions or labels against the evidence notes
  (Annapolis, recovery-amount range, surplus-claim timing, the court's name).
- Engine checks (`build/check_all.sh`): footers, integrity, source, breaks, leaks and EPUB all
  pass; EPUBCheck 5.4.0 reports 0 fatal, 0 errors, 0 warnings. `pdffonts`: TrueType only.
- Looked at every page on contact sheets at 28 dpi, and at the cover, contents, About pages and four
  figure pages at 75–80 dpi. Fixed: a hyphen break in the cover title, a five-page contents
  (now one page), a split boundary panel, four stranded lead-ins and one near-empty page.
- Not done: the textbook-pdf skill's adversarial Codex review of the PDF, and the statute checks in
  `design/open-questions.md` (the Legislature and CanLII sites refused automated access).
