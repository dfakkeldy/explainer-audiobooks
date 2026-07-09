# How these were made

Each book here is beginner-friendly technical prose, written by a language model,
and meant to be *listened to*. That is harder than merely making a long document:
the listener needs a coherent mental model, concrete examples, and a voice that
does not turn into boilerplate halfway through.

## The three problems

1. **A long book can feel assembled instead of authored.** Independently drafted
   chapters often repeat the same definition, hook, transition, or tradeoff
   without adding a new layer of understanding.
2. **It can hallucinate.** Ask a model to “explain how this app handles audio”
   and it can invent plausible-sounding internals that are not real.
3. **It can sound like code read aloud.** Multi-line syntax and symbols turn into
   “open paren, underscore, arrow” in a text-to-speech voice — and the listener
   checks out.

## The production method

### 1. One frontier model authors the canonical Markdown

The book begins with a learner brief, a table of contents, and a
**concept-coverage ledger**. The ledger records what each core concept first
means, how it will be retrieved or deepened later, which real example will make
it concrete, and what new ability the listener should have afterward.

One frontier model then writes every substantive Markdown chapter in sequence.
For a long book, that is several focused passes rather than one enormous output:
the author receives the outline, the relevant fact pack, ledger rows, and a small
continuity record of prior terminology, analogies, examples, and unresolved
promises. The chapter Markdown is the source of truth; EPUB and audio are
renderings of it.

This is intentionally not a “one agent per chapter” assembly line. A repeated
idea is allowed only when it does a different learning job — retrieval, deeper
mechanism, application, comparison, or correction of a misconception. Otherwise
it is edited as padding.

### 2. Fact packs keep the author grounded

Before prose is written, lower-cost workers read the real source and build a
per-chapter **fact pack**: cited details about the worked example, the actual
names a listener should learn, likely uncertainty, and contradictions to avoid.
The frontier author receives the evidence, not a cheaper model’s draft to mimic.

That grounding beats trusting model memory. It is the difference between a guide
that is true to an actual codebase and one that is merely plausible.

### 3. Cheap workers review evidence; they do not take over the voice

Lower-cost workers are ideal for source extraction, citation checks, prose
linting, beginner-reader reports, cover generation, EPUB/M4B assembly, and file
validation. Their editorial reports cite the exact paragraph and say what kind of
repair is needed — for example, “this redefines a cache without adding an
application; replace it with a counterexample.” They do not redraft whole
chapters in a different voice.

A small standard-library tool,
[`skill/scripts/prose_qc.py`](../skill/scripts/prose_qc.py), reports candidates
for repeated phrases, similar paragraphs, and formulaic chapter openings or
closings. It is a prompt for judgment, not an automatic rewrite: deliberate
vocabulary retrieval can be pedagogically useful. The frontier author decides
which findings are real and makes only the necessary substantive repair pass.

### 4. Narration is designed for the ear

The narration guide ([`skill/references/narration-style.md`](../skill/references/narration-style.md)) keeps prose warm, second person, concrete, and plain-spoken.
A short, speakable command may appear once and be unpacked, but code blocks,
symbol-heavy syntax, and two code lines in a row do not belong in an audiobook.
The book still names real files, tools, and commands so a listener can find them
later.

The same guide requires a layered explanation for the important ideas: what it
is, why it exists, how it works, a real case, and the boundary where the simple
story breaks. That is how the books get deeper without getting longer merely by
repeating themselves.

## Assembly

A small Python builder ([`skill/scripts/build_book.py`](../skill/scripts/build_book.py)) turns the reviewed chapter files into a valid EPUB 3 — with both a modern navigation document and an old-style NCX table of contents — plus a combined Markdown copy. A second script ([`skill/scripts/make_cover.py`](../skill/scripts/make_cover.py)) composes original SVG or raster cover art into an image-led cover with an intentional accent colour. Every book gets three award-worthy, genre-distinct cover concepts by default; the user chooses or combines them. Echo can then render the EPUB into M4B audio and alignment data.

## Model-aware, not model-agnostic

The method does not require one specific vendor, but it is deliberately
**model-routed**: pay for a frontier model where judgment, explanation, and voice
matter; use cheaper models for bounded, checkable work. Each finished package
records the authoring model and the review/production roles used.

## What it is not

It is not a replacement for an expert author or a line-by-line expert review. The
method makes the work more grounded, coherent, and inspectable; it does not make
every claim infallible. Check primary sources before relying on a real product's
current rules or behavior, and keep the AI-authorship disclosure with any public
book.
