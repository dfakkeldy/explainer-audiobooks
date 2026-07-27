# Humanizer Pass for Audiobook Manuscripts

Use the `humanizer` skill for a **light, bounded voice pass** after the frontier
author has written the canonical Markdown and after accepted content repairs have
been applied. The goal is prose that sounds like a thoughtful person explaining a
real subject aloud, not prose that has been cosmetically rewritten by another
model.

Read `declaudification.md` first. The humanizer is a two-pass check: an
independent inventory before edits, followed by frontier-author repairs and a
final run. Review chapter by chapter and then across the whole manuscript so
synonym-cycled habits are not hidden by chapter boundaries.

## Learning-design precondition

The humanizer cannot certify pedagogy or issue whole-book acceptance. Before
suggesting voice edits, check for missing orientation, chapter-order problems,
unexplained terms, shallow mechanisms, and missing worked examples. Each is a
structural blocker: record the exact location and return to learning review and
frontier-author repair.

The humanizer also cannot replace the revision sequence. Complete
claim-traceability, tightening, de-listification, sentence-rhythm, and rendered
ear-pass work as separate single-job passes. "Make it better" is not a valid
pass, and combining all five jobs in the humanizer hides which defect was
actually tested.

Do not smooth over a structural blocker with cleaner transitions, more polished
definitions, or added motivational prose. The humanizer starts only after the
learning architecture and substantive explanations are accepted. After a local
voice edit, rerun structure and beginner review over the affected material.

## What the pass should do

- Remove obvious AI tics: inflated significance, generic signposting, promotional
  adjectives, vague attributions, filler, synonym cycling, tidy rule-of-three
  lists, repetitive paragraph openings, empty conclusions, and repeated honesty
  announcements such as `honestly`, `the honest answer`, and `to be honest`.
- Vary sentence length and paragraph rhythm so narration does not sound assembled.
- Prefer concrete scenes, objects, decisions, constraints, and consequences that
  already exist in the fact pack or manuscript.
- Replace abstract claims with plain spoken language when the meaning is unchanged.
- Let the author sound interested, uncertain, amused, or practical when that tone
  is supported by the brief and the existing evidence.
- Keep the writing easy to hear: clear subjects, natural punctuation, short enough
  sentences, and no new code or visual dependence.
- Preserve road-book teaching infrastructure: history, people, narrative,
  real-world applications, useful analogies, and retrieval after a gap are not
  decorative material to cut for smoothness.

## What it must not do

- Do not invent anecdotes, interviews, feelings, opinions, quotations, sources,
  first-person experience, or claims about the author.
- Do not change facts, examples, citations, technical identifiers, commands,
  filenames, definitions, boundaries, or chapter order.
- Do not erase useful repetition that deliberately retrieves a concept for learning.
- Do not replace the manuscript wholesale or impose a generic "conversational"
  persona. Preserve the approved voice and the frontier author's choices.
- Do not add jokes, confessional language, fake uncertainty, or motivational
  endings just to make the prose seem human.
- Do not announce epistemic honesty. State the evidence, limitation, confidence,
  or uncertainty precisely in the claim itself.
- Do not touch Markdown image paths, captions, headings, metadata, or code samples
  except for a verified mechanical correction.

## Order of operations

1. Run the family-level independent inventory on the canonical
   `chapters/chNN.md` files, not on the EPUB, combined Markdown, or audio
   derivative. Save the before report.
2. Run the humanizer pass on those canonical files. Return targeted edits or a
   patch-sized change list first when the manuscript is large.
3. Have the frontier author review every finding, record accepted and rejected
   items with reasons, and make every accepted non-mechanical change.
4. Re-run factual/citation checks, narration checks, blind beginner review, and
   the whole-manuscript prose gate after accepted edits.
5. Review the before-and-after counts and preserve the accepted and rejected
   findings with their reasons in the editorial notes.

A cheaper worker may flag AI patterns and quote exact locations, but may not
rewrite the book in a competing voice. If humanization changes explanation,
structure, factual emphasis, or teaching depth, return that finding to the
frontier author instead.

## Prompt block

```text
Apply a light humanizing pass to these canonical audiobook chapters.

Remove AI-writing tells and make the prose sound naturally spoken: vary rhythm,
cut generic signposting and inflated claims, replace abstract filler with concrete
language already present in the manuscript, and keep the author's approved voice.
Preserve every fact, citation, technical name, filename, command, definition,
example, boundary, heading, image path, and intentional teaching repetition.

Do not invent anecdotes, feelings, opinions, quotations, sources, first-person
experience, jokes, or new claims. Do not rewrite the chapter wholesale. Return
only targeted edits with a short reason for each, and mark anything that needs the
frontier author's judgment. The frontier author will approve all substantive
changes before packaging.
```

## Final check

Read the revised passage aloud. It should sound less templated without becoming
sloppy, theatrical, over-familiar, or less precise. If the change makes the book
more entertaining but less true, reject it.
