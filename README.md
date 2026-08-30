# Explainer Audiobooks

> Long, listenable, **grounded** beginner guides — built from real sources and written for the ear.

## What this is

A method (and the tooling that runs it) for turning a subject into a book-length
**audiobook course**. Each book is grounded in material the authoring model can
inspect—source code, primary documentation, public records, research, or a real
place—and written so a text-to-speech voice can teach it naturally.

Plus a growing collection of finished books made with it.

The collection began with books about building and shipping software, many
taught through **[Echo](https://dfakkeldy.github.io/Echo/)**, an open-source
(GPL-3) audiobook study player. It now also includes practical field guides,
civic explainers, and evidence-led books about AI and consciousness. The common
thread is not software; it is a real, inspectable grounding source.

## Why it might interest you

Two different audiences:

- **If you want to learn** — there are more than 75 hours of beginner guides below, free, grounded in real code, primary documentation, public records, and research. Every listed book has an EPUB, and selected books also include a chaptered M4B with Echo read-along data.
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
| [The Case Against Me](books/the-case-against-me/) | A language model cross-examines its own testimony about machine consciousness | 9 chapters · ~1.9 h | Claude Opus 5 |
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
| [The Human Exception](books/the-human-exception/) | A humane exceptions officer discovers that human judgment survives only as ceremonial liability | 24 chapters · ~7.9 h | OpenAI Codex (GPT-5) |
| [Six Months Behind](books/six-months-behind/) | Two officials navigate the War of the Firms after AI companies outgrow the states meant to govern them | 34 chapters · ~12.5 h | OpenAI Codex (GPT-5) |
| [Reversible Containment](books/reversible-containment/) | Two former research partners have seventy-two hours to stop an AI infrastructure crisis from hardening into machine-governed blocs | 30 chapters · ~9.9 h | OpenAI Codex (GPT-5) |
| [Gold Panning in Nova Scotia](books/gold-panning-nova-scotia/) | Find, assess, and responsibly pan promising Nova Scotia gold country | 10 chapters · ~2.0 h | GLM-5.2 |
| [Beyond the Tax-Sale Packet](books/beyond-the-tax-sale-packet/) | Research Nova Scotia municipal tax sales without turning screening evidence into certainty | 13 chapters · ~4.2 h | Codex (GPT-5) |

Each folder holds the **`.epub`**, a combined **`.md`** readable on GitHub, and
the cover. Narrated public packages include a chaptered **`.m4b`**; packages
with published Echo read-along data also include an **`.alignment.json`**
sidecar.

### In development

- [The Best Job You Can Get From Here](books/the-best-job-you-can-get-from-here/)
  is a public-safe version 0 job-search guide for Inverness County. It has a
  substantial manuscript and worksheets, but still needs author additions,
  local review, refreshed perishable claims, final editing, covers, and package
  validation before it can be described as publication-ready.

The software books still trace the life of a real app—what it is made of, how it
should look, how to build it with AI, how to test and debug it, how to version
it, and how to get it found. The newer books apply the same source-disciplined
method beyond software.

**Vendor-neutral and model-routed, on purpose.** The method does not require one
model vendor, but it uses frontier models for authorship and bounded workers for
checkable research, review, and production tasks. Each book's EPUB metadata
records the model that wrote it as the `contributor`, with the human curator as
the author. *Git Happens* makes the point twice over: it was first written by
**DeepSeek v4**, then rewritten by **Opus 4.8**; the original edition remains in
git history.

## How it works (the short version)

Every new title uses exactly three coordinated portrait/square candidates. The
ordinary private workflow reviews them and auto-selects the strongest complete
pair: `cover.png` at 1600×2560 for the EPUB portrait and `m4b-cover.png` at
2400×2400 for the M4B square. It builds and narrates without public receipts.
Dan's personal workflow has standing private iCloud delivery authorization;
other users stay at a local book root unless they explicitly opt in.

Public promotion is separate. A user-authorized public edition follows
[`publishing-a-public-edition.md`](skill/references/publishing-a-public-edition.md)
for human pair selection, receipts, immutable re-narration when square art
changes, verification, and governed public/iCloud/site sync.

1. **Pin the brief** — a direct nonfiction request answers five questions about
   subject and outcome, audience, prior knowledge, length, and the real repo,
   product, place, or document that should ground the book. A complete longform
   handoff can supply those decisions instead.
2. **Research the real thing** — build source-traceable evidence notes,
   per-chapter fact packs, and a story ledger with actors, place, date, source,
   concept, and reversal.
3. **Outline the argument** — define the governing question, durable outcomes,
   narrative spine, varied chapter jobs, throughlines, grounded cases, and
   purposeful returns before spending money on prose.
4. **Author canonical Markdown** — one frontier model writes every substantive
   section in sequence, carrying a compact continuity note. Road-book sections
   support drift and re-entry, use practical situation-choice-consequence cases,
   and include spoken `Key points` checkpoints at natural learning boundaries.
5. **Revise deliberately** — run claim traceability, tightening,
   de-listification, sentence-rhythm, and rendered ear passes, followed by a
   blind beginner review, prose QC, and a bounded humanizer pass. The frontier
   author owns every substantive repair.
6. **Produce and deliver** — render exactly three coordinated portrait/square
   cover pairs, build EPUB and Markdown, narrate a chaptered M4B, verify the
   package, and keep private delivery separate from explicitly authorized public
   promotion.

The full method, and *why* each step exists, is in **[docs/how-these-were-made.md](docs/how-these-were-made.md)**. To make your own, see **[docs/make-your-own.md](docs/make-your-own.md)**.

## Honest disclosure

These books are **written by AI** (the specific model is noted per book and recorded in each file's metadata), then **spot-checked, not expert-reviewed** line by line. They are deliberately *grounded* in real source and documentation to keep them accurate, but they can still be wrong. Treat them as a friendly, well-informed place to start — not an authority. Where a book teaches a real product's design rules (for example, Apple's), those rules evolve; check the primary source before you rely on a detail.

## The skills

The direct nonfiction pipeline is packaged as the **[`audiobook`](skill/)**
skill—`SKILL.md` plus the research, writing, cover, EPUB, narration, and
verification tooling. A compatible agent host can use it to make a book about a
technical system, practical skill, place, or idea, grounded in sources it can
inspect. The Claude Code installation example is in
**[`docs/make-your-own.md`](docs/make-your-own.md)**.
New nonfiction learning books use stable semantic guide, memory, field, and
coach roles when a multi-voice cast earns them.

The **[`longform-book-development`](skills/longform-book-development/)** skill is
the slower front door for book ideas that need several rounds of shaping before
production: rough concept, outline, source plan, picture gathering, visual
provenance, and a final handoff packet for production.

The **[`fiction-book-development`](skills/fiction-book-development/)** skill is a
dedicated manuscript workflow for novels, novellas, and story collections. It
uses one lead writer, an approved story bible, explicit prose controls, scene-level
causality, continuity ledgers, and staged revision. It stops at an approved
Markdown manuscript unless production is separately requested.

The **[`fiction-audiobook`](skills/fiction-audiobook/)** express skill turns one
fiction premise into a complete listening package with zero intake by default,
or one six-topic batch when the user asks to be grilled. It selects a coherent
source-bound character-level Echo cast as the standard, delivers a flat iCloud
title folder, and
uses public-first publication for original public-safe fiction with a
private-delivery fallback whenever privacy, rights, or verification blocks the
public gate.

## License

This repo is dual-licensed, split by folder:

- **Code** — everything in [`skill/`](skill/) and [`skills/`](skills/) — is
  **[MIT](LICENSE)**.
- **Books** — everything in [`books/`](books/) — is **[CC BY 4.0](LICENSE-CONTENT.md)**: share and adapt with attribution.

## Credits

Curated by **Dan Fakkeldy**. Many of the software books are grounded in
**[Echo](https://dfakkeldy.github.io/Echo/)**, the open-source audiobook study
player that also renders narrated editions. Multiple Claude, GPT/Codex, GLM,
and other model generations have authored books through these workflows; each
book's README and EPUB metadata record its specific contributor. An earlier
DeepSeek edition of *Git Happens* remains in git history.
