# Make your own

The audiobook pipeline is one [Claude Code](https://claude.com/claude-code)
skill, bundled in [`skill/`](../skill/). With it installed, you make a book by
asking — in plain English — for one.

## Install

Copy the skill into your Claude Code skills directory:

```bash
mkdir -p ~/.claude/skills
ln -s "$(pwd)/skill" ~/.claude/skills/audiobook
```

(Or drop it into a project's `.claude/skills/`.) It needs Python 3 and, for cover rasterizing, either `rsvg-convert` (from librsvg) or ImageMagick — both optional; without them the build just skips the cover.

## Ask for a book

New books use exactly three coordinated portrait/square candidates. The human
makes the explicit pair selection after thumbnail review, and the paired receipt
binds `cover.png` at 1600×2560 to the EPUB portrait and `m4b-cover.png` at
2400×2400 to the M4B square. Post-embed verification checks both and preserves
media before governed public/iCloud/site sync. Public-safe packages may use
approved public destinations; private packages stay private. Legacy single-cover
receipts are verification-only compatibility.

Order: research → three source directions → portrait/square render pairs →
thumbnail review → explicit pair selection → paired receipt → EPUB portrait +
M4B square embedding → post-embed verification → governed public/iCloud/site
sync. The current *Rodents in the Walls* exclusion is only for the five-book
migration and is not a universal future rule.

Then say something like:

> Make me a ~4‑hour beginner audiobook on **WebSockets**, taught through **my `chatterbox` repo**. Warm, spoken, no code read aloud.

The skill will walk the process in [`skill/SKILL.md`](../skill/SKILL.md):

1. **Pin the brief** — it confirms the subject, the real worked example to ground everything in, the target length, and the voice.
2. **Write an argument-level outline** — it maps the governing question,
   chapter jobs, throughlines, grounded cases, and purposeful returns before
   spending money on prose.
3. **Build fact packs** — lower-cost workers read the real docs/source of your
   worked example so the frontier author stays true to it.
4. **Author canonical Markdown** — one frontier model writes the chapters in
   sequence, carrying a continuity record instead of fanning out competing voices.
5. **Review + assemble** — cheap diagnostics and reader reports identify exact
   repair candidates; the frontier author handles substantive fixes, then EPUB,
   cover, audio, and Markdown are rendered from the reviewed chapters.
6. **Deliver** — an explicitly requested private reading copy lands with its
   editable source under iCloud Books.

## The two ingredients that matter

- **A real worked example you (or the model) can read.** The grounding is everything. A book taught through an actual codebase, product, or system will be accurate and concrete; one taught from thin air will be generic and prone to drift.
- **An honest length.** ~45,000 words is about four hours at 1.25× speed. The skill has a runtime table; pick the listen you actually want.

## Authorship

By default the EPUB author is the human curator, and the **model that wrote the book is recorded as a contributor** — so you can always tell which model produced which book. Change either in the build command; see `skill/SKILL.md`.

## It's not magic

Read the [honest disclosure](../README.md#honest-disclosure) first. The method keeps the prose *grounded*, not *infallible* — spot-check before you publish anything under your name.
