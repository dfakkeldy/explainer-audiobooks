# Plain-language de-hedging pass (October 9, 2026)

Why: Dan's review note on the draft: AI over-hedges on obvious stuff, which makes the reading
tedious and insulting. This pass makes the book state settled law, procedure and plain facts
directly, and keeps a caveat only where something is genuinely uncertain or varies by
municipality, event or case, said once where it matters.

Method: Claude Opus 5.5 (Claude Code, headless), one session per chapter, two passes.

- Pass 1 (`chNN.md`, top part): reflexive softeners ("may", "can help", "should", "it is worth
  noting", repeated professional-advice asides) turned into direct statements where the original
  and the evidence notes support them. The About chapter keeps the single "educational only"
  disclaimer; nothing was removed there.
- Pass 2 (`## Pass 2` in each report): repeated limits. Each limit keeps its first, clearest
  statement (Careful panel, table or summary bullet); the reflexive echoes in running prose,
  captions and answers were cut, along with caption boilerplate tails ("Verify sources; not a
  recommendation.", "A dated interface state, not a recommendation.", "Educational overview •
  verify current law and sale terms.").

Rules held in both passes: no new factual claims; permissive statutory "may" (a power the Act
grants) kept as the rule it is; every qualifier the fact audit restored (`review/audit/`) kept, for
example Foundry Street's right-of-way "may continue"; flagged claims kept as printed; File Notes
word for word; SVG figures untouched (their printed text is unchanged).

Totals: 354 hedges removed or rewritten (pass 1: 150, pass 2: 204), about 200 deliberately kept
(listed per chapter under "Kept hedged"). Words placed in the PDF: 66,168 → 64,454.

Layout: the build afterwards reported four nearly empty pages, each a chapter's last
"Check your understanding" question spilling onto its own page (Chapters 4, 5, 6 and 11; the
reported p. 135 was Chapter 6's). The summaries and questions at those chapter ends were tightened
by a line or two each, with no change of meaning, until no nearly empty page remained. 324 pages.

Also in this change: source no. 48 (NS Marks The Spot) now prints its source-commit GitHub URL,
production source receipt and live-map URLs, as the 2026 source register does. The `dfakkeldy`
pattern was dropped from the `book.yaml` forbid list for that; the edition still says nothing about
who owns the map.

Checks after the rebuild: `build/check_all.sh` ALL CHECKS PASSED, EPUBCheck 5.4.0 0 fatal / 0
errors / 0 warnings.
