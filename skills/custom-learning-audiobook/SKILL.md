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
  - `../../skill/references/cover-art.md` for cover concepts, visual quality,
    and the signature accent-colour rule.
  - `../../skill/scripts/build_book.py` for EPUB and combined Markdown.
  - `../../skill/scripts/make_cover.py` for cover rendering.
- If the request came from `longform-book-development`, read its handoff packet
  first and preserve approved outline, source, and figure decisions unless the
  user changes them.

## Defaults

| Decision | Default |
|---|---|
| Length | Standard beta book: about 2 hours, roughly 18,000-22,000 words |
| Deep mode | About 4 hours, roughly 40,000-45,000 words |
| Sampler | 45-75 minutes when the topic is vague or commitment is light |
| Audience | Curious beginner unless the request says otherwise |
| Narrator | `am_michael`; fallback `am_puck`; do not default to `af_heart` |
| Audio renderer | Native Echo/Kokoro through `echo-cli narrate`; no Apple/system-voice substitute |
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

6. **Plan any interior pictures.** If the user wants pictures, or a handoff
   packet includes a figure plan, gather only usable images: user-supplied,
   generated, self-created, public-domain, permissively licensed, or explicitly
   permissioned. Save them under `chapters/images/`, keep a provenance note in
   `research/visuals.md`, and plan chapter placement with alt text and captions.
   Treat unclear web images as visual references, not package assets.

7. **Write with one lead author.** Do not fan out chapter writing by default.
   Subagents may help with research or QC only when subagent use is allowed, but
   one lead writer owns the manuscript voice and continuity. If chapter fan-out
   is ever used for speed, run a lead-author continuity rewrite before delivery.

8. **Save chapter files.** Write `chapters/ch01.md`, `chapters/ch02.md`, and so
   on. Keep chapter headings clean and spoken-friendly. Avoid repeated openings,
   generic AI enthusiasm, and repeated disclaimers. Add approved figures as
   standalone Markdown image paragraphs, for example
   `![Alt text](images/example.png "Caption")`.

9. **Build the book.** Generate or choose a cover, then run the existing
   `build_book.py` script. The EPUB/Markdown outputs are always required. For
   generated covers, make 2-3 genuinely different beautiful candidates with a
   strong subject image and one intentional signature accent colour. Use that
   accent in the SVG art and pass the same hex value to `make_cover.py --accent`
   so the final cover clearly sells the colour Echo will derive from it. Include
   a bright/high-key background candidate when the topic would benefit from a
   friendly, modern audiobook-store look. `build_book.py` embeds standalone
   Markdown images as EPUB figures and copies them beside the combined Markdown.

10. **Render native Echo audio.** Use Echo's `echo-cli narrate` path from
   `references/package-and-qc.md` with `--voice am_michael` first and `am_puck`
   only as an Echo voice fallback. Echo audio is part of the delivery contract:
   do not impose your own time limit, deadline, or "too slow" threshold just
   because synthesis may take hours. Let long renders run, resume partial
   renders, or report the exact live blocker. Do not replace Echo/Kokoro with
   macOS `say`, Apple system voices, AVSpeechSynthesizer, audiobook-app TTS, or
   any other non-Echo renderer unless the user explicitly asks for that
   non-Echo preview/fallback after you name the tradeoff. Produce `<slug>.m4b`
   and `<slug>.alignment.json` whenever the CLI can run. If native Echo audio is
   blocked and the user has not approved a non-Echo substitute, deliver
   EPUB/Markdown and report the blocker instead of shipping substitute audio.

11. **QC before copying.** Validate EPUB, parse alignment JSON, inspect M4B
    duration with `ffprobe`, run narration/prose sweeps, and record missing QC
    steps honestly. For books with pictures, verify every figure appears in the
    EPUB, every image has alt text and a caption, and the provenance/licensing
    note is complete.

12. **Package and copy.** Write `README.md` or `manifest.json` in `dist/`.
    Public-safe packages copy to the iCloud Books folder and a repo
    `books/<slug>/` folder. Private packages stay out of the public repo and
    copy to iCloud only when the user explicitly wants that private reading
    copy.

13. **Report plainly.** Include title, slug, privacy status, research mode,
    source-confidence label, word count, runtime, narrator, output paths, and
    which QC gates passed or were skipped. If the book includes pictures, report
    figure count and any image rights/privacy caveats.

## Hard Rules

- Do not make the requester look up sources.
- Do not turn medical, legal, financial, safety-critical, workplace-private,
  customer, confidential, or professional-advice topics into advice books.
- Do not publish or commit a requester book unless it is public-safe and the
  user has permission to add it to the public learning library.
- Do not copy private generated artifacts into the public repo or public KB.
- Do not use `af_heart` as the default narrator.
- Do not invent a timebox for audio rendering. A multi-hour Echo/Kokoro render
  is allowed work, not a reason to downgrade the package.
- Do not use Apple/macOS/system narration as a fallback for Echo audio unless
  the user explicitly asks for a non-Echo preview or substitute.
- Do not include pictures in a public package unless their rights and privacy
  status are clear. Keep private, client, workplace, and personally sensitive
  images out of public repo and KB surfaces.
- Do not include decorative images without a learning, evidence, reference, or
  orientation purpose.
- Do not ship a generic title-on-colour cover when generating a cover yourself:
  make a real image-led cover, and make the derived accent colour visible enough
  to work as the book's library identity.
- Do not default every candidate to a dark background; bright covers are allowed
  and should be offered when they better sell the book.
