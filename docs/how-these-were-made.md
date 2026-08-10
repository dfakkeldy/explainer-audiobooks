# How these were made

Each book here is beginner-friendly prose written by a language model and meant
to be *listened to*. The subjects now range from software to practical skills,
civic processes, and questions about AI. The production problem is the same:
the listener needs a coherent mental model, concrete evidence, and a voice that
does not turn into boilerplate halfway through.

## The four problems

1. **A long book can feel assembled instead of authored.** Independently
   drafted chapters often repeat the same definition, hook, transition, or
   tradeoff without adding a new layer of understanding.
2. **It can hallucinate.** Ask a model to explain a system, place, or process
   from memory and it can invent plausible details that are not real.
3. **It can sound like code or notes read aloud.** Syntax, stacked lists, and
   unexplained names are hard to follow without a screen.
4. **Attention drifts.** A listener who is driving, working, or simply thinking
   about the last idea cannot scan backward to recover the subject.

## The production method

### 1. Begin with an argument, not a terminology syllabus

A direct nonfiction request settles the desired outcome, audience, prior
knowledge, length, and real grounding source. A longer development process can
supply the same decisions in a complete handoff.

Before prose, the lead author builds a question-led argument: one governing
question, six to ten durable outcomes where appropriate, a narrative spine,
varied chapter jobs, two to four throughlines, grounded cases, and purposeful
returns. Each section must change what the listener can explain, recognize, or
do. A table of contents that merely walks through vocabulary is not enough.

### 2. Fact packs and a story ledger keep it grounded

Research notes cite real sources with precise locators, contradictions, and
uncertainty. Every chapter receives a fact pack containing the supported facts
and the actual files, tools, commands, places, or documents the listener should
learn, each with a one-breath gloss.

The research also carries a story ledger. A real story records its actors,
place, date, source, concept, and reversal; without a reversal it is treated as
an illustration. This prevents a technically accurate book from becoming a
storyless inventory of rules and definitions.

That grounding beats trusting model memory. It is the difference between a
guide that is true to something inspectable and one that is merely plausible.

### 3. One frontier model owns the canonical manuscript

One frontier model writes every substantive section in sequence. Each writing
call receives the full outline, the relevant fact pack, the previous section or
a faithful summary, the current section's job, and a must-not-repeat list. A
compact continuity note tracks defined terms, examples, callbacks, and open
promises. Markdown chapters remain the source of truth; EPUB and audio are
renderings of that manuscript.

This is intentionally not a one-agent-per-chapter assembly line. Bounded
workers can extract sources, verify claims, run diagnostics, generate covers,
assemble EPUB/M4B files, and report exact findings. They do not replace a
chapter or silently take over the book's voice.

### 4. Write so a drifted listener can return

The narration guide
([`skill/references/narration-style.md`](../skill/references/narration-style.md))
keeps prose warm, concrete, plain-spoken, and complete without a screen. It
names real files, tools, commands, places, and documents, but speaks at most one
short line of code at a time before unpacking it.

Road-book sections reopen the subject explicitly so a listener can rejoin after
an interruption. Abstract ideas are grounded in practical
situation-choice-consequence examples. At natural learning boundaries, a
recognizable spoken `Key points` checkpoint gives two to four recall or action
points without introducing new facts.

Important ideas still receive depth: what the thing is, why it exists, how it
works, a real case, and the boundary where the simple story stops working.
Deliberate retrieval is useful; repeated definition-shaped padding is not.

### 5. Revise one problem at a time

The canonical manuscript receives five distinct craft passes, in order:

1. claim traceability;
2. tightening;
3. de-listification;
4. sentence rhythm; and
5. an ear pass against rendered audio.

A blind beginner then reads in listening order without the outline or expected
outcomes and reports the mental model they formed and the exact point where it
failed. The frontier author resolves accepted findings.

The standard-library tool
[`skill/scripts/prose_qc.py`](../skill/scripts/prose_qc.py) flags repeated
phrases, similar paragraphs, formulaic openings and closings, and other style
families for human judgment. A bounded humanizer pass may repair formulaic or
over-polished prose, but it cannot invent facts, anecdotes, opinions, jokes, or
a replacement voice. Prose QC runs again afterward.

## Assembly and delivery

Every new title uses exactly three coordinated cover pairs: `cover.png` at
1600×2560 for the EPUB portrait and `m4b-cover.png` at 2400×2400 for the M4B
square. The builder
([`skill/scripts/build_book.py`](../skill/scripts/build_book.py)) creates EPUB 3
and combined Markdown from the reviewed chapters. The governed Echo wrapper
narrates the selected square art into an immutable chaptered M4B and produces
alignment data for read-along playback.

There are two distinct lanes:

- **Ordinary private book:** the workflow reviews the full-size candidates and
  thumbnails, auto-selects the strongest coherent pair on its rubric, reports
  the choice, builds and narrates, and keeps the result local unless private
  iCloud delivery is authorized. The user does not operate public receipts.
- **Public promotion:** the user explicitly authorizes a named edition. The
  public runbook records a valid pair selection and publishing permission. If
  the square art changes, the M4B is re-narrated rather than patched. The EPUB,
  M4B, covers, alignment, and receipts are verified before governed public,
  iCloud, or site sync.

Private delivery permission never implies permission to publish. Legacy
single-cover receipts and `replace_m4b_cover.py` exist for compatibility with
old artifacts; neither is part of a new or revised render.

## Model-aware and vendor-neutral

The method does not require one vendor, but it is deliberately model-routed:
use a frontier model where explanation, judgment, continuity, and voice matter;
use cheaper or bounded workers for tasks whose outputs can be checked. Each
finished package records the authoring model and the review or production roles
used.

## What it is not

It is not a replacement for an expert author, a line-by-line expert review, or
current primary sources. The method makes the work more grounded, coherent, and
inspectable; it does not make every claim infallible. Keep the AI-authorship
disclosure with public books, and obtain the legal, medical, financial,
technical, cultural, or lived-experience review appropriate to the subject.
