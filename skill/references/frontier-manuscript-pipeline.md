# Frontier Manuscript Pipeline

Use this production split when the book's prose should be authored by a frontier
model, while lower-cost workers handle evidence, diagnostics, and packaging. The
point is not to make every task expensive. It is to protect the two things that
make a book feel authored: the explanation choices and the continuity of its
voice.

## Role Contract

| Role | Owns | Must not do |
|---|---|---|
| Frontier lead author | Learning architecture, outline choices, explanatory depth, examples, canonical Markdown chapters, and accepted substantive revisions | Delegate chapters to independent prose writers or accept unsupported facts |
| Cheap research worker | Source extraction, citations, fact-pack drafts, terminology lists, and conflict flags | Decide what the listener needs to learn or invent facts |
| Cheap editorial reviewer | Evidence-backed findings: repetition candidates, confusing leaps, shallow explanations, jargon, voice tics, and missing examples | Rewrite a chapter in a competing voice or decide a structural repair |
| Cheap production worker | Markdown lint, EPUB/M4B build, metadata, cover rendering, file validation, and manifest | Change manuscript meaning |

A cheap worker may make a bounded mechanical correction only when it cannot alter
meaning, pedagogy, or a factual claim. Examples: a duplicate word, a malformed
heading, a broken Markdown image path, or a typo verified against the fact pack.
Everything else goes back to the frontier author as a precise repair request.

## Canonical Markdown Flow

1. **Cheap workers prepare evidence.** Create source notes and chapter fact packs
   with citations, terminology, contradictions, and uncertainty labels. Give the
   frontier author the evidence, not a cheaper worker's prose draft to imitate.

2. **The frontier author creates the book bible.** It approves the table of
   contents, the 2-4 genuine throughlines, and `research/coverage-ledger.md`.
   The ledger maps each core concept to its first explanation, later retrieval or
   deepening, a concrete example, a boundary/counterexample where useful, and a
   listener outcome. If a return to an idea has no named purpose, remove it.

3. **The frontier author writes the Markdown manuscript.** Write `chNN.md`
   files in chapter order. For a book too large for one context, use sequential
   runs rather than parallel chapter drafting. Each run receives the book bible,
   relevant fact pack, coverage-ledger rows, and the latest continuity record.
   The prose in `chapters/` is canonical; EPUB, audio, and covers are derivatives.

4. **Update continuity after each chapter.** Record only the facts the next
   chapter needs: terms already fully defined, analogies and scenes already used,
   examples, deliberate callbacks, active promises, and unresolved questions.
   This prevents repetitive re-introductions without forcing the author to reread
   an entire long manuscript on every call.

5. **Cheap workers inspect, never redraft.** Run `scripts/prose_qc.py`, source
   validation, narration lint, and a short reader review. Each report must point
   to the source paragraph and explain why a change would improve learning.

6. **The frontier author performs a targeted repair pass.** It accepts, rejects,
   or revises each substantive finding. A report with only local issues earns a
   local patch pass, not a costly full regeneration.

7. **Cheap workers package and validate.** Render EPUB/M4B, build covers, check
   files and metadata, and write the manifest. They must not “improve” the prose
   while packaging.

## Coverage-Ledger Test

Every core concept should have an explanation path, not just a definition:

1. **What** is it, in plain language?
2. **Why** does it exist — what problem or decision does it address?
3. **How** does it work at the level the listener needs?
4. **Where** does the listener see it in the worked example or a concrete case?
5. **When does it not apply?** Name a boundary, tradeoff, misconception, or
   counterexample when that would prevent a bad mental model.

Do not force all five into one paragraph or every minor term. The ledger makes
sure the book, taken as a whole, supplies the missing rung before moving on.

## Cheap Editorial Report Format

Require a compact, citation-first report. A useful finding is actionable without
asking the frontier author to rediscover the problem:

```markdown
## Finding 07 — redundant re-explanation
- **Location:** `chapters/ch04.md`, paragraph beginning “A cache is…”
- **Evidence:** This restates the definition from `ch02`, paragraph beginning
  “Think of a cache…” without adding mechanism, application, or contrast.
- **Listener cost:** A listener gets the same fact twice but still does not know
  when caching is the wrong choice.
- **Repair request:** Replace this restatement with one short callback, then add
  a concrete “when not to cache” case.
- **Category:** redundancy | depth gap | unclear mechanism | jargon | voice tic |
  factual conflict | weak example | missing boundary
```

A reviewer may return **no findings**. Do not make it manufacture criticism to
fill a quota. The author, not the reviewer, decides whether a reported issue is
real and writes all non-mechanical prose changes.

## Completion Gates

- [ ] One named frontier model authored every substantive Markdown passage.
- [ ] `coverage-ledger.md` gives every planned recurrence a learning purpose.
- [ ] `continuity.md` records prior terms, analogies, examples, and promises.
- [ ] Cheap review reports cite exact locations and recommend repairs rather than
  supplying a replacement voice.
- [ ] The frontier author accepted/rejected substantive findings before packaging.
- [ ] The published EPUB/M4B was derived from the reviewed Markdown, with no
  downstream prose rewriting.
