# Frontier Manuscript Pipeline

Use this split when a frontier model should author the prose while lower-cost
workers handle evidence, diagnostics, rendering, and packaging. The aim is to
protect the explanation choices and continuity that make a book feel authored.

Research, argument design, drafting, and revision are different jobs, and
they usually go better as separate calls, each consuming the accepted Markdown
from the phase before. How many passes a book needs, and in what order, is the
author's call.

## Role contract

| Role | Owns | Must not do |
|---|---|---|
| Frontier author | Learning architecture, outline, explanatory depth, examples, canonical chapters, substantive repairs | Delegate chapters to independent prose writers or accept unsupported facts |
| Research worker | Source extraction, citations, fact packs, terminology, conflicts | Decide the learning arc or invent facts |
| Editorial reviewer | Citation-first findings about repetition, leaps, shallow mechanisms, jargon, and missing examples | Rewrite a chapter in a competing voice |
| Production worker | Markdown checks, EPUB/M4B assembly, metadata, covers, file validation | Change manuscript meaning |

A worker may make a mechanical correction only when it cannot alter meaning,
teaching, or a factual claim. Everything else returns to the frontier author as
a precise repair request.

## A flow that has worked

1. **Ground the evidence.** Write source notes with precise locators,
   contradictions, and uncertainty. A claim absent from the notes is
   unavailable to the manuscript.
2. **Build the argument-level outline.** Give every section a job and a
   landing, and note what it must not repeat.
3. **Draft section by section.** Each call receives the outline, the relevant
   research, and the previous section's actual text. Never distribute adjacent
   prose to independent voices.
4. **Keep a short continuity note** of terms defined, examples used, callbacks,
   and open promises.
5. **Review and revise.** Workers may check sources, sweep for narration
   hazards, and do a blind listening-order read, quoting exact locations. The
   frontier author decides each substantive repair.
6. **Package downstream.** Build EPUB, M4B, covers, and manifests from the
   reviewed Markdown without rewriting prose.

## Citation-first report format

```markdown
## Finding 07 — redundant re-explanation
- **Location:** `chapters/ch04.md`, paragraph beginning "A cache is..."
- **Evidence:** This repeats the definition from chapter two without adding a
  mechanism, application, or contrast.
- **Listener cost:** The listener hears the same fact twice but still does not
  know when caching is the wrong choice.
- **Repair request:** Use one short callback, then add a concrete boundary case.
- **Category:** redundancy | depth gap | unclear mechanism | jargon |
  factual conflict | weak example | missing boundary
```

A reviewer may return no findings. The frontier author, not the reviewer,
decides whether an issue is real and writes all non-mechanical changes.

## Before packaging

- One frontier author owns every substantive Markdown passage.
- Every manuscript claim traces to a verified source.
- The delivered formats derive from reviewed Markdown with no downstream prose
  rewriting.
