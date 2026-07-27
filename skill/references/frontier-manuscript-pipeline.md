# Frontier Manuscript Pipeline

Use this split when a frontier model should author the prose while lower-cost
workers handle evidence, diagnostics, rendering, and packaging. The aim is to
protect the explanation choices and continuity that make a book feel authored.

Long-form quality is a pipeline problem, not a prompt problem. Research,
argument design, drafting, and revision are different jobs. Run them as separate
calls, with each phase consuming the accepted Markdown from the phase before.

## Role contract

| Role | Owns | Must not do |
|---|---|---|
| Frontier author | Learning architecture, outline, explanatory depth, examples, canonical chapters, substantive repairs | Delegate chapters to independent prose writers or accept unsupported facts |
| Research worker | Source extraction, citations, fact packs, terminology, conflicts | Decide the learning arc or invent facts |
| Editorial reviewer | Citation-first findings about repetition, leaps, shallow mechanisms, jargon, voice tics, and missing examples | Rewrite a chapter in a competing voice |
| Production worker | Markdown checks, EPUB/M4B assembly, metadata, covers, file validation | Change manuscript meaning |

A worker may make a mechanical correction only when it cannot alter meaning,
teaching, or a factual claim. Everything else returns to the frontier author as
a precise repair request.

## Canonical Markdown flow

1. **Ground the evidence.** Write source notes with stable claim IDs, precise
   locators, contradictions, and uncertainty. A claim absent from the notes is
   unavailable to the outline and manuscript.
2. **Profile an approved voice source.** Capture opening moves,
   evidence-to-example movement, plain-language mechanism, humour boundary,
   uncertainty, rhythm, and practical landings. Keep craft features, not
   pastiche, and never commit raw source excerpts.
3. **Build the argument-level outline.** Give every section a job, supporting
   claims, throughline advance, landing beat, and must-not-repeat list.
4. **Draft section by section.** Each call receives the outline, fact pack,
   voice direction, previous section or faithful summary, current job, and
   no-repeat duty. Never generate the whole book in one call or distribute
   adjacent prose to independent voices.
5. **Update the continuity ledger.** After every section, record terms defined,
   examples and analogies used, callbacks, active promises, unresolved
   questions, listener load, running summary, and next no-repeat list.
6. **Inspect without redrafting.** Workers run source checks, narration lint,
   prose diagnostics, and blind beginner review. They quote exact locations and
   explain the listener cost.
7. **Run narrow revision calls.** Complete claim-traceability, tightening,
   de-listification, sentence-rhythm, and a rendered ear-pass as separate jobs.
   The frontier author decides each substantive repair.
8. **Humanize without changing authorship.** Apply targeted voice edits only.
   Do not invent facts, anecdotes, sources, first-person experience, jokes, or a
   competing voice.
9. **Package downstream.** Build EPUB, M4B, covers, and manifests from the
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
- **Category:** redundancy | depth gap | unclear mechanism | jargon | voice tic |
  factual conflict | weak example | missing boundary
```

A reviewer may return no findings. The frontier author, not the reviewer,
decides whether an issue is real and writes all non-mechanical changes.

## Completion check

- One frontier author owns every substantive Markdown passage.
- Every manuscript claim traces to a verified source and locator.
- The outline gives each section a job, evidence, landing, and no-repeat duty.
- The continuity ledger records prior terms, examples, callbacks, and promises.
- Cheap reports cite exact locations and request a kind of repair.
- The frontier author resolves substantive findings before packaging.
- The delivered formats derive from reviewed Markdown with no downstream prose
  rewriting.
