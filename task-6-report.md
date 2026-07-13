# Task 6 Report

## Outcome

Active skills and public workflow documentation now require one universal paired
cover process: exactly three coordinated portrait/square candidates, human pair
selection, a paired receipt, 1600×2560 EPUB portrait embedding, 2400×2400 M4B
square embedding, post-embed identity and media-preservation verification, and
governed public/iCloud/site synchronization.

Legacy single-cover commands are explicitly labelled verification-only
compatibility. The Rodents exclusion is scoped only to the five-book migration
and is not a future publishing exception.

## TDD and verification

- RED: `tests.test_skill_cover_contract` failed with 71 contract failures before
  the active instructions were updated.
- GREEN: 12 focused skill-cover contract tests pass.
- `tools/validate_skills.py`: clean.
- Full suite: 166 tests pass.
- `git diff --check`: clean.
- Installed-skill link boundary: read-only inspection confirmed both Claude and
  Codex links still target the main checkout; this worktree did not rewrite them.

## Review notes

The paired examples use the shipped Tasks 1–5 interfaces:
`cover_pairs.render_cover_pair`, `cover_receipts.py select-pair`,
`build_book.py --m4b-cover`, `replace_m4b_cover.py`, paired verification, and
`sync_selected_cover.py --paired-artifact-dir`.

No private/generated book artifact or knowledge-base file was changed.
