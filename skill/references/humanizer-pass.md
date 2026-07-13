# Humanizer Pass for Audiobook Manuscripts

Use the `humanizer` skill for a **light, bounded voice pass** after the frontier
author has written the canonical Markdown and after accepted content repairs have
been applied. The goal is prose that sounds like a thoughtful person explaining a
real subject aloud, not prose that has been cosmetically rewritten by another
model.

Read `declaudification.md` first. The humanizer is a two-pass gate: an
independent inventory before edits, followed by frontier-author repairs and a
final verified run. Review chapter by chapter and then across the whole manuscript
so synonym-cycled habits are not hidden by chapter boundaries.

## What the pass should do

- Remove obvious AI tics: inflated significance, generic signposting, promotional
  adjectives, vague attributions, filler, synonym cycling, tidy rule-of-three
  lists, repetitive paragraph openings, and empty conclusions.
- Vary sentence length and paragraph rhythm so narration does not sound assembled.
- Prefer concrete scenes, objects, decisions, constraints, and consequences that
  already exist in the fact pack or manuscript.
- Replace abstract claims with plain spoken language when the meaning is unchanged.
- Let the author sound interested, uncertain, amused, or practical when that tone
  is supported by the brief and the existing evidence.
- Keep the writing easy to hear: clear subjects, natural punctuation, short enough
  sentences, and no new code or visual dependence.

## What it must not do

- Do not invent anecdotes, interviews, feelings, opinions, quotations, sources,
  first-person experience, or claims about the author.
- Do not change facts, examples, citations, technical identifiers, commands,
  filenames, definitions, boundaries, chapter order, or the coverage ledger.
- Do not erase useful repetition that deliberately retrieves a concept for learning.
- Do not replace the manuscript wholesale or impose a generic "conversational"
  persona. Preserve the approved voice and the frontier author's choices.
- Do not add jokes, confessional language, fake uncertainty, or motivational
  endings just to make the prose seem human.
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
4. Re-run factual/citation checks, the coverage-ledger comparison, narration
   checks, and the whole-manuscript prose gate after accepted edits.
5. Record counts before and after plus the reviewer/model/skill version,
   accepted and rejected findings, rerun checks, and chapter hashes in the final
   `prose-style-receipt.json`. Packaging must verify the receipt against the
   canonical chapters.

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
