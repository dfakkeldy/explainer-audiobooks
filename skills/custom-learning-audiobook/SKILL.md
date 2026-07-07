---
name: custom-learning-audiobook
description: Use when making a custom, personalized, beta-test, Echo-ready, or topic-request learning audiobook from a plain-language request such as "I want to learn X"; use for coworker/local tester books, sample learning books, public-safe library additions, or private learning packages.
---

# Custom Learning Audiobook

Make a listener-specific learning audiobook from a topic request. The requester
should feel helped, not assigned homework: ask only useful questions, do the
research, write one coherent manuscript, and package the result for Echo.

## Required References

- Read `references/intake-and-research.md` before intake, safety checks, or
  research.
- Read `references/package-and-qc.md` before building EPUB/Markdown, rendering
  M4B/alignment, copying packages, or reporting completion.
- Reuse the existing explainer tooling from this repo:
  - `../../skill/references/narration-style.md` for spoken style and QC sweeps.
  - `../../skill/references/cover-art.md` for cover concepts.
  - `../../skill/scripts/build_book.py` for EPUB and combined Markdown.
  - `../../skill/scripts/make_cover.py` for cover rendering.

## Defaults

| Decision | Default |
|---|---|
| Length | Standard beta book: about 2 hours, roughly 18,000-22,000 words |
| Deep mode | About 4 hours, roughly 40,000-45,000 words |
| Sampler | 45-75 minutes when the topic is vague or commitment is light |
| Audience | Curious beginner unless the request says otherwise |
| Narrator | `am_michael`; fallback `am_puck`; do not default to `af_heart` |
| Author metadata | `Dan Fakkeldy` |
| Writing model metadata | Record the generating model as contributor/source note |
| Build folder | `.build/custom-learning-audiobooks/<slug>/` |

## Workflow

1. **Create a run folder.** Use
   `.build/custom-learning-audiobooks/<slug>/` with `research/`, `chapters/`,
   and `dist/` subfolders. Keep source notes and scratch artifacts out of
   public book folders.

2. **Clarify only what matters.** If the request is broad, ask at most 3-5
   questions from `references/intake-and-research.md`. If the requester is not
   available, choose conservative defaults and state them in the manifest.

3. **Classify safety and public/private status before writing.** Decide whether
   the book is public-safe, private, or sensitive/high-stakes. Sensitive topics
   need narrowing, refusal, or educational-only framing. Private books never go
   into the public repo or public KB.

4. **Research for the listener.** Use quick, deep, Open Notebook, user-supplied,
   or mixed research mode. Label source confidence. The requester does not have
   to provide sources. Browse current or high-stakes topics when needed.

5. **Outline the book.** Build a short table of contents around what the
   listener wants to understand or do. For Dan/internal runs, get outline
   approval unless the user explicitly asked for a full autonomous run.

6. **Write with one lead author.** Do not fan out chapter writing by default.
   Subagents may help with research or QC only when subagent use is allowed, but
   one lead writer owns the manuscript voice and continuity. If chapter fan-out
   is ever used for speed, run a lead-author continuity rewrite before delivery.

7. **Save chapter files.** Write `chapters/ch01.md`, `chapters/ch02.md`, and so
   on. Keep chapter headings clean and spoken-friendly. Avoid repeated openings,
   generic AI enthusiasm, and repeated disclaimers.

8. **Build the book.** Generate or choose a cover, then run the existing
   `build_book.py` script. The EPUB/Markdown outputs are always required.

9. **Render Echo audio when available.** Use Echo's `echo-cli narrate` path from
   `references/package-and-qc.md` with `--voice am_michael` first and `am_puck`
   only as fallback. Produce `<slug>.m4b` and `<slug>.alignment.json` whenever
   the CLI can run. If audio rendering is blocked, deliver EPUB/Markdown and
   report the exact blocker.

10. **QC before copying.** Validate EPUB, parse alignment JSON, inspect M4B
    duration with `ffprobe`, run narration/prose sweeps, and record missing QC
    steps honestly.

11. **Package and copy.** Write `README.md` or `manifest.json` in `dist/`.
    Public-safe packages copy to the iCloud Books folder and a repo
    `books/<slug>/` folder. Private packages stay out of the public repo and
    copy to iCloud only when the user explicitly wants that private reading
    copy.

12. **Report plainly.** Include title, slug, privacy status, research mode,
    source-confidence label, word count, runtime, narrator, output paths, and
    which QC gates passed or were skipped.

## Hard Rules

- Do not make the requester look up sources.
- Do not turn medical, legal, financial, safety-critical, workplace-private,
  customer, confidential, or professional-advice topics into advice books.
- Do not publish or commit a requester book unless it is public-safe and the
  user has permission to add it to the public learning library.
- Do not copy private generated artifacts into the public repo or public KB.
- Do not use `af_heart` as the default narrator.
