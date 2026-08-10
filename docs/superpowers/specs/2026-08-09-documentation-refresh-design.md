# Documentation Refresh Design

## Goal

Make the repository's public documentation describe the workflows and book
catalog that exist on `main` as of 2026-08-09, while preserving dated production
evidence as historical records.

## Chosen approach

Use a targeted refresh rather than reorganizing `docs/` or rewriting production
records. The current guides and catalog will state current behavior. A new
`docs/README.md` will distinguish current guides from development packets,
historical design records, and generated evidence. Superseded tax-sale handoff
and listening files will receive short archival banners; their original evidence
will remain unchanged below those banners.

This is preferable to either a guide-only edit, which would leave the `docs/`
landing page and historical status files misleading, or a wholesale archive
move, which would churn paths and risk breaking durable evidence links.

## Changes

### Root README

- Broaden the project description from code-only technical books to grounded
  learning audiobooks built from real sources.
- Add the finished public packages for *Beyond the Tax-Sale Packet*, *Gold
  Panning in Nova Scotia*, and *The Case Against Me* to the collection.
- Replace the obsolete tax-sale development entry with the current job-guide
  development entry.
- Keep unfinished or artifact-only directories out of the finished catalog.
- Align the short workflow description with the current argument outline,
  story ledger, road-book writing, revision, and private/public cover lanes.

### Current guides

- Update `docs/make-your-own.md` to describe the repository checkout, required
  Pillow-enabled interpreter, mandatory paired-cover production, five-question
  nonfiction intake, longform handoff, and available nonfiction and fiction
  entry points.
- Update `docs/how-these-were-made.md` to replace the retired
  concept-coverage-ledger description with the current outline, story-ledger,
  fact-pack, continuity, revision, blind-review, drift-and-re-entry, and spoken
  checkpoint contracts.
- Separate ordinary private cover auto-selection from explicitly authorized
  public promotion and its selection receipts.

### Documentation index and historical records

- Add `docs/README.md` as the GitHub landing page for current guides,
  development packets, dated operational evidence, and historical Superpowers
  plans/specifications.
- Reconcile the current status prose in the tax-sale packet README with the
  governed-final 54-figure publication receipt.
- Add a superseded-record banner to the tax-sale handoff packet and full-audio
  acceptance checklist. Do not alter their original dated evidence.
- Repair the one known broken relative link in the 2026-07-11 historical cover
  refresh plan.

## Boundaries

- Do not change audiobook artifacts, receipts, hashes, manuscript text, cover
  art, or production tooling.
- Do not rewrite historical plans, specifications, handoff content, or checklist
  evidence beyond an archival banner and the broken-link correction.
- Do not claim that unfinished or listening-pending packages have completed
  human acceptance.
- Preserve unrelated work in the canonical checkout.

## Verification

- Check every local Markdown link in `README.md` and `docs/**/*.md`.
- Run the repository unit-test suite and `tools/validate_skills.py`.
- Run `git diff --check` and inspect the final diff and working-tree status.
