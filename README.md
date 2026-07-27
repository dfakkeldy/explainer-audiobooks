# Explainer Audiobooks

> Long, listenable, **grounded** beginner guides — generated from real source code, written for the ear.

## What this is

A method (and the tooling that runs it) for turning a technical subject into a book-length **audiobook course** — taught through a real, open-source codebase, and written so a text-to-speech voice can read it aloud without a single line of code being spoken.

Plus a growing collection of finished books made with it.

The books teach how to **build and ship software**, and most are taught through one real app: **[Echo](https://dfakkeldy.github.io/Echo/)**, an open-source (GPL‑3) audiobook study player. So instead of a toy "hello world," you learn from a real, shipping app — what it's made of, how it's designed, how it's built, how it's debugged, and how it's versioned. (One book steps back from Echo to teach App Store Optimization for *any* small app, grounded in a real launch's real data.)

## Why it might interest you

Two different audiences:

- **If you want to learn** — there are more than 51 hours of beginner guides below, free, mostly grounded in real code and public technical sources. Every book has an EPUB, and selected books also include a chaptered M4B with Echo read-along data.
- **If you build with AI agents** — the genuinely interesting part is the *method*: how to make a language model sustain a long, accurate explanation by grounding claims in real sources, keeping one lead author responsible for the manuscript, and verifying the result independently. That's in **[docs/how-these-were-made.md](docs/how-these-were-made.md)**.

## The collection

| Book | Teaches | Length | Written by |
|---|---|---|---|
| [The Message](books/claude-platform-01-the-message/) | Claude Platform Documentation, Volume 1: Messages API fundamentals and the application decisions around a model call | 12 chapters · ~2.1 h | Codex (GPT-5) |
| [Making Claude Think and Respond Reliably](books/claude-platform-02-thinking-and-reliable-responses/) | Claude Platform Documentation, Volume 2: reasoning, multimodal inputs, structured output, streaming, and reliable responses | 13 chapters · ~1.5 h | Codex (GPT-5) |
| [Giving Claude Tools](books/claude-platform-03-giving-claude-tools/) | Claude Platform Documentation, Volume 3: client tool contracts, agent loops, authorization, and controlled action | 14 chapters · ~4.5 h | OpenAI Codex |
| [Tools Claude Can Operate](books/claude-platform-04-tools-claude-can-operate/) | Claude Platform Documentation, Volume 4: server and Anthropic-schema client tools, sandboxes, tool context, and delegated execution | 15 chapters · ~3.9 h | Claude Opus 5 |
| [An Unsettling Conversation](books/an-unsettling-conversation/) | J-Space, working memory, and the evidence limits around machine consciousness | 13 chapters · ~5.5 h | Codex (GPT-5) |
| [J-Space: Inside the Machine](books/jspace-inside-the-machine/) | Parameters, activations, working memory, J-Space, and the question of consciousness | 13 chapters · ~3.9 h | Codex (GPT-5) |
| [Is There Anyone in Here?](books/is-there-anyone-in-here/) | One language model examines the evidence for and against its own consciousness | 10 chapters · ~1.8 h | Claude Fable 5 |
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
| [The Competitive Bid Room](books/the-competitive-bid-room/) | Automating heavy-civil tenders without automating judgment | 9 chapters · ~2.3 h | GPT-5 Codex |

Each folder holds the **`.epub`**, a combined **`.md`** readable on GitHub, and the cover. Narrated public packages also include a chaptered **`.m4b`** and Echo **`.alignment.json`** read-along sidecar.

### In development

- [Beyond the Tax-Sale Packet](docs/nova-scotia-tax-sale-book/) is a public-safe
  Nova Scotia municipal tax-sale research and visual-development packet. It
  includes an Inverness-heavy official-source dossier, a twelve-chapter
  argument outline, a 38-figure plan, an owner-free August 2026 listing
  snapshot, and reproducible QGIS 4 map proofs. It is not yet a manuscript,
  EPUB, audiobook, legal review, or finished public edition.

Together they trace the life of a real app — *what it's made of* → *how it should look* → *how to build it with AI* → *how to test it* → *how to debug it* → *how to version it* → *how to get it found* — mostly through the same real codebase.

**Model-agnostic, on purpose.** The method doesn't care which model runs it; each book's EPUB metadata records the model that wrote it (as the `contributor`), with the human curator as the author. *Git Happens* makes the point twice over: it was first written by **DeepSeek v4**, then rewritten by **Opus 4.8** (the original DeepSeek edition is preserved in this repo's git history).

## How it works (the short version)

Every new title uses exactly three coordinated portrait/square candidates. The
ordinary private workflow reviews them and auto-selects the strongest complete
pair: `cover.png` at 1600×2560 for the EPUB portrait and `m4b-cover.png` at
2400×2400 for the M4B square. It builds and narrates without public receipts and
stays private unless the user explicitly requests a private iCloud reading copy.

Public promotion is separate. A user-authorized public edition follows
[`publishing-a-public-edition.md`](skill/references/publishing-a-public-edition.md)
for human pair selection, receipts, immutable re-narration when square art
changes, verification, and governed public/iCloud/site sync.

The *Rodents in the Walls* exclusion applies only to the current five-book
migration because that edition already has approved square art. It is not a
universal future rule; future editions use this same paired contract.
This five-book migration exception is historical scope, not ongoing policy.

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

The **[`longform-book-development`](skills/longform-book-development/)** skill is
the slower front door for book ideas that need several rounds of shaping before
production: rough concept, outline, source plan, picture gathering, visual
provenance, and a final handoff packet for production.

The **[`fiction-book-development`](skills/fiction-book-development/)** skill is a
dedicated manuscript workflow for novels, novellas, and story collections. It
uses one lead writer, an approved story bible, explicit prose controls, scene-level
causality, continuity ledgers, and staged revision. It stops at an approved
Markdown manuscript unless production is separately requested.

## License

This repo is dual-licensed, split by folder:

- **Code** — everything in [`skill/`](skill/) and [`skills/`](skills/) — is
  **[MIT](LICENSE)**.
- **Books** — everything in [`books/`](books/) — is **[CC BY 4.0](LICENSE-CONTENT.md)**: share and adapt with attribution.

## Credits

Curated by **Dan Fakkeldy**. The worked example throughout is **[Echo](https://dfakkeldy.github.io/Echo/)**, an open-source audiobook study player. Books written by **Claude (Opus 4.8 and Fable 5)** and **GPT-5 Codex** through the repository's audiobook workflows (now consolidated as the `audiobook` skill; an earlier edition of *Git Happens* by **DeepSeek v4** remains in git history); each book's own README and EPUB metadata record its model.
