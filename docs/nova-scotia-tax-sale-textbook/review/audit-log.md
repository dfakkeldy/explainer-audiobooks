# Audit log

Phase: adversarial fact-preservation audit (prompt: /workspace/taxbook/promptB4.md).

Method: one reviewer per chapter, each reading the original chapter cold, then the textbook chapter,
its SVG figures and its answers fragment, using the claims ledger only as a cross-check. Per-chapter
findings and fixes are in `review/audit/chNN.md`; this log records progress and the summary.
Answer fixes are made in `src/appendix-answers/chNN.md` and merged into `97-answers.md` with
`review/tools/merge_answers.py`.

Severity: **high** = changes a legal, numeric or date meaning, or a privacy regression; **medium** =
drops or weakens a qualifier, or asserts something unsourced; **low** = wording drift, figure
labelling or cross-reference slips with no change of meaning.

## 2026-10-09 attempt 2
- Started. Attempt 1 received an empty prompt; no chapter had been audited.
- Wrote `review/tools/merge_answers.py` (reproduces the current `97-answers.md` exactly).
- Launched 13 chapter reviewers in parallel (brief: one per chapter, edits limited to that
  chapter's Markdown, SVG figures, figure script and answers fragment). A chapter is finished when
  `review/audit/chNN.md` ends with a `Summary:` line; a resumer should rerun only chapters without one.
- Ch 3 done: high=0 medium=1 low=1, 2 fixed (summary qualifiers restored), 0 flags. Report review/audit/ch03.md.
- Ch 2 done: high=0 medium=0 low=2, 1 fixed (summary 'about the arrears' restored), 0 flags. Report review/audit/ch02.md.
- Ch 4 done: high=0 medium=1 low=4, 2 fixed (answer 4.1 'purport' restored; 'the research file'), 0 flags. Report review/audit/ch04.md.
- Ch 6 done: high=0 medium=1 low=5, 3 fixed (CBRM scope sentence rejoined; unsourced lead-in replaced; answer 6.2), 0 new flags (F-06a-c already cover open points). Report review/audit/ch06.md.
- Ch 9 done: high=0 medium=2 low=7, 6 fixed (figure alt scope restored; summary bullet denials untangled; qualifiers), 0 new flags. Coordinator item: F-09b treatment text. Report review/audit/ch09.md.
  - F-09b treatment corrected: the source note cites TAX-003 only.
- Ch 7 done: high=0 medium=1 low=7, 6 fixed (figure alt 'retention boundary' meaning restored; modal and scope qualifiers), 0 new flags. Report review/audit/ch07.md.
- Ch 12 done: high=0 medium=0 low=4, 3 fixed (clocks figure: surplus window opens after redemption, 20-year limit counted from the sale — caption, alt, SVG desc, generator; table row 'Lawfulness of the proposed use'; LAW-012 note 'payment of the fee'), 0 new flags. Report review/audit/ch12.md.
- Ch 8 done: high=0 medium=4 low=6, 6 fixed (Foundry Street right-of-way 'may continue' restored in recall, figure label/SVG/generator, caption, alt; surplus 'possible'/'automatically'; court-order wording), 0 new flags. Report review/audit/ch08.md.
- Ch 10 done: high=0 medium=1 low=5, 4 fixed (payment source note no longer implies the packet lists Inverness's payment forms; wording restored), 1 proposed flag (F-NEW-10-a, merged at end). Report review/audit/ch10.md.
- Ch 11 done: high=0 medium=4 low=8, 8 fixed (repair rule back to 'treats … narrowly … when' in summary and answer 11.4; qualifiers 'when unsettled', 'exact', 'certain', 'qualifying' restored), 0 flags. Report review/audit/ch11.md.
  - Coordinator: "The concrete test" → "The concrete example" (chapter line 318, ledger ch11-122, changes note).
- Ch 1 done: high=0 medium=6 low=5, 8 fixed (summary no longer says who receives the preliminary notice; check question 6 no longer invents a "no dwelling" line; timeline label "Bidders enter / after notices" in SVG and generator; "to hold that priority"; answer 1.4 "tax-sale division"; methods-map caption cites OPS-005 for the July 20 refresh), 0 flags. Report review/audit/ch01.md.
  - Coordinator: ch01 ledger rows updated to the new timeline label.
- Ch 5 done: high=0 medium=0 low=4, 1 fixed (geology caption 'ownership of mineral rights'), 0 flags; coordinator items on F-28 and F-04. Report review/audit/ch05.md.
- Ch 13 done: high=0 medium=2 low=9, 6 fixed (Union Workshop 'cannot be responsibly investigated before the event' restored in alt and summary; 'or confirmation' in figure SVG and generator; unsourced lead-in removed; answer 13.3), 0 flags. Report review/audit/ch13.md.
- Coordinator items after all 13 chapters:
  - flagged-claims.md had duplicate IDs F-23/F-24 (Ch 2's packet-anatomy placeholders and ladder alt reused Ch 3's IDs); Ch 2's pair renumbered F-02a/F-02b, with the Ch 2 ledger updated.
  - F-NEW-10-a merged as F-10d. F-04 and F-28 treatment text corrected to what the textbook actually does (no combined count table; inset 2 shows the public venue's street address). F-09b corrected (above).
  - Ch 10 source-note wording smoothed: "accepted forms (the evidence notes do not itemize the list)".
  - Ch 13 ledger caption reference Appendix C → Appendix B.
- Regenerated the Ch 1, 8, 12 and 13 figures in a scratch copy: apart from the embedded font data URIs, every SVG is identical to the hand-edited file, so the generators carry the fixes. Repo SVGs left as they are.
- Merged answers (merge_answers.py). Ledger checks: ch04-021, ch06-023, ch12-108 rewrite quotes refreshed to the audited text; all 13 ledgers pass check_ledger.py. (Ledger SHA-256 lines and some apparatus rows predate the audit; the per-chapter audit reports are the current record.)
- Rebuilt (build.py) and ran check_all.sh with EPUBCheck 5.4.0: **ALL CHECKS PASSED**. 332 pages;
  66,168 words placed once and in order; 3,187 source blocks; footers, breaks, leaks pass; EPUBCheck
  0/0/0; EPUB text identical to the PDF flow. One nearly empty page reported (p. 135, 52 words).

## Summary (attempt 2, complete)

| | Count |
|---|---|
| Findings, high | 0 |
| Findings, medium | 23 |
| Findings, low | 67 |
| Fixed by chapter reviewers | 56 |
| Kept, with reasons | 34 |
| Coordinator fixes | 2 text (Ch 11 "concrete example"; Ch 10 source-note wording), 5 register/ledger corrections |
| New flagged claims | 1 (F-10d) |
| Flagged claims, final | 54 (22 open, 28 note, 4 perishable) |

There were no numeric, date, section-number or privacy regressions. The medium findings were all
dropped or hardened qualifiers ("may continue", "treats … narrowly … when", "cannot be responsibly
investigated", "subject to definitions and exemptions") or unsourced assertions in the apparatus
(summaries, recall answers, alt text, captions, source notes). Each has been restored to the
original's wording.
