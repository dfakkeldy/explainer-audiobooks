# Explainer Audiobooks

> Long, listenable, **grounded** beginner guides — generated from real source code, written for the ear.

## What this is

A method (and the tooling that runs it) for turning a technical subject into a book-length **audiobook course** — taught through a real, open-source codebase, and written so a text-to-speech voice can read it aloud without a single line of code being spoken.

Plus a growing collection of finished books made with it.

The books teach how to **build and ship software**, and most are taught through one real app: **[Echo](https://dfakkeldy.github.io/Echo/)**, an open-source (GPL‑3) audiobook study player. So instead of a toy "hello world," you learn from a real, shipping app — what it's made of, how it's designed, how it's built, how it's debugged, and how it's versioned. (One book steps back from Echo to teach App Store Optimization for *any* small app, grounded in a real launch's real data.)

## Why it might interest you

Two different audiences:

- **If you want to learn** — there are ~40 hours of narration-ready beginner guides below, free, mostly grounded in real code and public technical sources. Drop an `.epub` into any audiobook or reader app and listen.
- **If you build with AI agents** — the genuinely interesting part is the *method*: how to make a language model write 50,000 accurate words it *won't* hallucinate, by grounding every chapter in real source and fanning the work across one agent per chapter. That's in **[docs/how-these-were-made.md](docs/how-these-were-made.md)**.

## The collection

| Book | Teaches | Length | Written by |
|---|---|---|---|
| [Echo, From the Inside](books/echo-from-the-inside/) | What an iOS app actually is | 17 chapters · ~5.4 h | Opus 4.8 |
| [Why It Feels Right](books/why-it-feels-right/) | Apple's Human Interface Guidelines | 18 chapters · ~5.0 h | Fable 5 |
| [You Are the Architect](books/you-are-the-architect/) | Vibe‑coding real iOS apps with Claude Code | 20 chapters · ~5.1 h | Fable 5 |
| [The Bug Is a Clue](books/the-bug-is-a-clue/) | Debugging in Xcode | 17 chapters · ~5.9 h | Opus 4.8 |
| [Tests First](books/tests-first/) | Testing & TDD in Swift | 9 chapters · ~2.5 h | Opus 4.8 |
| [Git Happens](books/git-happens/) | Git & GitHub, end to end (incl. the nightly→weekly→main release ladder) | 16 chapters · ~4.6 h | Opus 4.8 |
| [Findable](books/findable/) | App Store Optimization for a small app | 8 chapters · ~3.0 h | Opus 4.8 |
| [The Voice in the Machine](books/the-voice-in-the-machine/) | How on‑device AI narration works (Kokoro on ONNX Runtime) | 11 chapters · ~3.6 h | Opus 4.8 |
| [The Long Route](books/the-long-route/) | Whether the indie road is the right career direction — evidence, not affirmation | 13 chapters · ~4.0 h | Fable 5 + Opus 4.8 |
| [The Living Knowledge Base](books/the-living-knowledge-base/) | LLM wikis, research notebooks, embeddings, and company memory | 15 chapters · ~1.6 h | GPT-5 Codex |

Each folder holds the **`.epub`** (for any audiobook/reader app, including on‑device text‑to‑speech), a combined **`.md`** (readable right here on GitHub), and the cover.

Together they trace the life of a real app — *what it's made of* → *how it should look* → *how to build it with AI* → *how to test it* → *how to debug it* → *how to version it* → *how to get it found* — mostly through the same real codebase. Two books step outside the app stack: *The Long Route* turns the same evidence-first method on a career question, while *The Living Knowledge Base* applies it to LLM-maintained wikis, research notebooks, and public-safe company-memory patterns.

**Model-agnostic, on purpose.** The method doesn't care which model runs it; each book's EPUB metadata records the model that wrote it (as the `contributor`), with the human curator as the author. *Git Happens* makes the point twice over: it was first written by **DeepSeek v4**, then rewritten by **Opus 4.8** (the original DeepSeek edition is preserved in this repo's git history).

## How it works (the short version)

1. **Pin the brief** — subject, the real worked example, target length, voice.
2. **Outline** — one chapter per concept, in teaching order, each grounded in one real piece of the example.
3. **Fact packs** — before any prose is written, distill *accurate* facts from the real docs and source into each chapter's prompt, with a hard "don't invent beyond this" rule. This is what keeps tens of thousands of AI-written words from drifting into confident fiction.
4. **Fan out** — one agent writes each chapter, in parallel, grounded in its fact pack and a shared style guide: warm, second person, and **no code read aloud, ever**.
5. **QC + assemble** — sweep for anything that would sound wrong narrated, then build a chaptered EPUB (with a generated cover) and a combined Markdown file.

The full method, and *why* each step exists, is in **[docs/how-these-were-made.md](docs/how-these-were-made.md)**. To make your own, see **[docs/make-your-own.md](docs/make-your-own.md)**.

## Honest disclosure

These books are **written by AI** (the specific model is noted per book and recorded in each file's metadata), then **spot-checked, not expert-reviewed** line by line. They are deliberately *grounded* in real source and documentation to keep them accurate, but they can still be wrong. Treat them as a friendly, well-informed place to start — not an authority. Where a book teaches a real product's design rules (for example, Apple's), those rules evolve; check the primary source before you rely on a detail.

## The skill

The whole pipeline is packaged as a Claude Code skill in **[`skill/`](skill/)** — `SKILL.md` plus a cover generator, an EPUB builder, and the narration style guide. Point Claude Code at it and ask for a book on any subject, grounded in any codebase you can read.

## License

This repo is dual-licensed, split by folder:

- **Code** — everything in [`skill/`](skill/) — is **[MIT](LICENSE)**.
- **Books** — everything in [`books/`](books/) — is **[CC BY 4.0](LICENSE-CONTENT.md)**: share and adapt with attribution.

## Credits

Curated by **Dan Fakkeldy**. The worked example throughout is **[Echo](https://dfakkeldy.github.io/Echo/)**, an open-source audiobook study player. Books written by **Claude (Opus 4.8 and Fable 5)** and **GPT-5 Codex** via the `explainer-audiobook` and `custom-learning-audiobook` skills (with an earlier edition of *Git Happens* by **DeepSeek v4**, kept in git history); each book's own README and EPUB metadata record its model.
