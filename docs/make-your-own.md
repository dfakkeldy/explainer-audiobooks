# Make your own

The whole pipeline is a [Claude Code](https://claude.com/claude-code) skill, bundled in [`skill/`](../skill/). With it installed, you make a book by asking — in plain English — for one.

## Install

Copy the skill into your Claude Code skills directory:

```bash
cp -R skill ~/.claude/skills/explainer-audiobook
```

(Or drop it into a project's `.claude/skills/`.) It needs Python 3 and, for cover rasterizing, either `rsvg-convert` (from librsvg) or ImageMagick — both optional; without them the build just skips the cover.

## Ask for a book

Then say something like:

> Make me a ~4‑hour beginner audiobook on **WebSockets**, taught through **my `chatterbox` repo**. Warm, spoken, no code read aloud.

The skill will walk the process in [`skill/SKILL.md`](../skill/SKILL.md):

1. **Pin the brief** — it confirms the subject, the real worked example to ground everything in, the target length, and the voice.
2. **Propose an outline** — and wait for your yes before writing 45,000 words against the wrong structure.
3. **Build fact packs** — it reads the real docs/source of your worked example so the prose stays true to it.
4. **Fan out** — one writer agent per chapter, in parallel.
5. **QC + assemble** — a code-leak sweep, then a chaptered EPUB (with cover) and a combined Markdown.
6. **Deliver** — the finished `.epub` lands in `~/Downloads/book-inbox/`.

## The two ingredients that matter

- **A real worked example you (or the model) can read.** The grounding is everything. A book taught through an actual codebase, product, or system will be accurate and concrete; one taught from thin air will be generic and prone to drift.
- **An honest length.** ~45,000 words is about four hours at 1.25× speed. The skill has a runtime table; pick the listen you actually want.

## Authorship

By default the EPUB author is the human curator, and the **model that wrote the book is recorded as a contributor** — so you can always tell which model produced which book. Change either in the build command; see `skill/SKILL.md`.

## It's not magic

Read the [honest disclosure](../README.md#honest-disclosure) first. The method keeps the prose *grounded*, not *infallible* — spot-check before you publish anything under your name.
