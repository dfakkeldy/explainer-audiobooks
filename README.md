# Explainer Audiobooks

> Long, listenable, **grounded** beginner guides — generated from real source code, written for the ear.

## What this is

A method (and the tooling that runs it) for turning a technical subject into a book-length **audiobook course** — taught through a real, open-source codebase, and written so a text-to-speech voice can read it aloud without a single line of code being spoken.

Plus a growing collection of finished books made with it.

The books teach how to **build and ship software**, and most are taught through one real app: **[Echo](https://dfakkeldy.github.io/Echo/)**, an open-source (GPL‑3) audiobook study player. So instead of a toy "hello world," you learn from a real, shipping app — what it's made of, how it's designed, how it's built, how it's debugged, and how it's versioned. (One book steps back from Echo to teach App Store Optimization for *any* small app, grounded in a real launch's real data.)

## Why it might interest you

Two different audiences:

- **If you want to learn** — there are more than 42 hours of beginner guides below, free, mostly grounded in real code and public technical sources. Every book has an EPUB, and selected books also include a chaptered M4B with Echo read-along data.
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
| [Chicken Predators](books/chicken-predators/) | Identify and prevent poultry predation in Cape Breton | 16 chapters · ~3.1 h | GLM-5.2 |
| [Rodents in the Walls](books/rodents-in-the-walls/) | Identify, exclude, and clean up after house-invading rodents | 9 chapters · ~2.0 h | GPT-5.6 Sol |
| [The New Deal](books/the-new-deal/) | Canada Post, CUPW, and the future of rural mail | 9 chapters · ~1.9 h | GLM-5.2 |

Each folder holds the **`.epub`**, a combined **`.md`** readable on GitHub, and the cover. Narrated public packages also include a chaptered **`.m4b`** and Echo **`.alignment.json`** read-along sidecar.

Together they trace the life of a real app — *what it's made of* → *how it should look* → *how to build it with AI* → *how to test it* → *how to debug it* → *how to version it* → *how to get it found* — mostly through the same real codebase.

**Model-agnostic, on purpose.** The method doesn't care which model runs it; each book's EPUB metadata records the model that wrote it (as the `contributor`), with the human curator as the author. *Git Happens* makes the point twice over: it was first written by **DeepSeek v4**, then rewritten by **Opus 4.8** (the original DeepSeek edition is preserved in this repo's git history).

## How it works (the short version)

1. **Pin the brief** — subject, the real worked example, target length, voice.
2. **Outline** — one chapter per concept, in teaching order, each grounded in one real piece of the example.
3. **Fact packs + coverage ledger** — before prose is written, distill *accurate*
   facts from the real docs and source into each chapter's evidence, then map each
   core concept to a real example, a knowledge delta, and a purposeful later
   retrieval. This keeps tens of thousands of AI-written words accurate and
   prevents definition-shaped padding.
4. **Frontier-author Markdown** — one frontier model writes every substantive
   chapter in sequence, using a continuity record to preserve the book's voice,
   examples, and promises. Cheaper workers research, diagnose, render, and
   package; they do not replace chapters.
5. **QC + assemble** — prose diagnostics and citation-first reader reports flag
   exact repair candidates, then build a chaptered EPUB (with a generated cover)
   and a combined Markdown file from the reviewed manuscript.

The full method, and *why* each step exists, is in **[docs/how-these-were-made.md](docs/how-these-were-made.md)**. To make your own, see **[docs/make-your-own.md](docs/make-your-own.md)**.

## Honest disclosure

These books are **written by AI** (the specific model is noted per book and recorded in each file's metadata), then **spot-checked, not expert-reviewed** line by line. They are deliberately *grounded* in real source and documentation to keep them accurate, but they can still be wrong. Treat them as a friendly, well-informed place to start — not an authority. Where a book teaches a real product's design rules (for example, Apple's), those rules evolve; check the primary source before you rely on a detail.

## The skills

The long technical explainer pipeline is packaged as a Claude Code skill in
**[`skill/`](skill/)** — `SKILL.md` plus a cover generator, an EPUB builder, and
the narration style guide. Point Claude Code at it and ask for a book on any
subject, grounded in any codebase you can read.

The separate **[`custom-learning-audiobook`](skills/custom-learning-audiobook/)**
skill is for short, listener-specific Echo beta books from plain topic requests:
"I want to learn X." It defaults to roughly two hours, uses one lead writer for
continuity, routes public/private books explicitly, supports approved interior
pictures as EPUB figures, and renders Echo-ready audio with `am_michael` when
the Echo CLI is available. It does not substitute Apple/macOS system narration
for native Echo/Kokoro audio unless the requester explicitly asks for a
non-Echo preview. Finished packages are copied to a complete iCloud Drive
`Books/<Title>/` folder by default so they are easy to find.

The **[`longform-book-development`](skills/longform-book-development/)** skill is
the slower front door for book ideas that need several rounds of shaping before
production: rough concept, outline, source plan, picture gathering, visual
provenance, and a final handoff packet for `custom-learning-audiobook`.

## License

This repo is dual-licensed, split by folder:

- **Code** — everything in [`skill/`](skill/) and [`skills/`](skills/) — is
  **[MIT](LICENSE)**.
- **Books** — everything in [`books/`](books/) — is **[CC BY 4.0](LICENSE-CONTENT.md)**: share and adapt with attribution.

## Credits

Curated by **Dan Fakkeldy**. The worked example throughout is **[Echo](https://dfakkeldy.github.io/Echo/)**, an open-source audiobook study player. Books written by **Claude (Opus 4.8 and Fable 5)** and **GPT-5 Codex** via the `explainer-audiobook` and `custom-learning-audiobook` skills (with an earlier edition of *Git Happens* by **DeepSeek v4**, kept in git history); each book's own README and EPUB metadata record its model.
