# How these were made

Each book here is roughly 45,000–75,000 words of beginner-friendly technical prose, written by a language model, and meant to be *listened to*. Three things make that hard, and most of the method is just three answers to them.

## The three problems

1. **Length is a slog.** Asking one model, in one pass, for a 50,000-word book gets you something that sags in the middle and quietly gives up on the back half.
2. **It hallucinates.** Ask a model to "explain how this app handles audio" and it will happily invent plausible-sounding internals that aren't real.
3. **It sounds like code read aloud.** The moment a technical writer reaches for `someFunction()` or `snake_case`, a text-to-speech voice turns it into misery — *"open paren close paren"* — and the listener checks out.

## The three answers

### 1. One agent per chapter, fanned out

The book is outlined first — one chapter per concept, in teaching order. Then **each chapter is written by its own agent, in parallel.** No single context has to hold the whole book, so chapter 14 is written with the same care as chapter 1. Each writer gets the full table of contents (so it can make light transitions) but only *its* chapter to write.

A short orchestration script ([`skill/references/fanout-template.md`](../skill/references/fanout-template.md)) dispatches the writers and each one saves its own chapter file straight to disk — the prose never round-trips through the orchestrator's context.

### 2. Fact packs — the anti-hallucination layer

This is the part that matters most. **Before any prose is written, the real source is read and distilled into a per-chapter "fact pack"** — a compact list of accurate, sourced details about the worked example. Each writer's prompt embeds its fact pack with a blunt instruction:

> Ground everything in these real facts. Simplify them for a beginner; translate any code-like names into plain spoken English; but never contradict them, and never invent technical specifics beyond them.

Grounding the model in real, retrieved facts beats trusting its memory every time. It's the difference between a guide that's true to the actual codebase and one that's merely plausible. The books about Echo were grounded in Echo's own architecture docs and source; the book about Apple's design guidelines was grounded in the current guidelines (Liquid Glass and all), not a model's stale recollection of them.

### 3. A narration style guide — written for the ear

Every writer gets the same style rules ([`skill/references/narration-style.md`](../skill/references/narration-style.md)), and the hard one is: **no code, ever.** No snippets, no symbols, no camelCase spelled out, no file extensions. When a real component has to be named, the writer says it in plain words ("the part called the Player Model") and then explains the *idea* in English. After generation, a cheap automated sweep greps every chapter for the things that slip through — backticks, `snake_case`, arrows, braces — and anything caught gets scrubbed before assembly.

The rest of the guide is voice: warm, second person, every piece of jargon defined in one breath the first time it appears, honest about the trade-offs behind each decision.

## Assembly

A small Python builder ([`skill/scripts/build_book.py`](../skill/scripts/build_book.py)) turns the chapter files into a valid EPUB 3 — with both a modern navigation document and an old-style NCX table of contents, so it imports cleanly into the widest range of readers — plus a combined Markdown copy. A second script ([`skill/scripts/make_cover.py`](../skill/scripts/make_cover.py)) turns bespoke SVG art into an image-led cover, carrying a deliberate cover-art accent colour when supplied, supporting bright or dark cover tones, and falling back to a title-derived colour otherwise. Neither script assumes much about the machine it runs on.

## Model-agnostic

The method is just orchestration plus grounding, so it doesn't depend on a particular model. One of the books in this collection (*Git Happens*) was written by **DeepSeek v4**; the others by **Opus 4.8**. Each book records the model that wrote it in its EPUB metadata. Swap the model, keep the method.

## What it is not

It is not a replacement for an expert author. The fact packs keep the prose honest about *what the code does*, but no one reviewed every sentence for pedagogical nuance. These are a fast, grounded, friendly first pass — and they're upfront about that. See the honest-disclosure note in the [README](../README.md).
