# Narration style bible

This is the craft layer of the explainer-audiobook skill. The whole product is
*heard*, never read on a page, so every rule below exists to serve the ear. Hand
the "Voice & rules" block to every chapter-writer verbatim — consistency across
independently-written chapters depends on it.

## Voice & rules (give this block to every writer agent verbatim)

THIS WILL BE NARRATED ALOUD as an audiobook. Write 100% for the EAR.

ABSOLUTE RULES (breaking these ruins the audiobook):
- NEVER show code. No code blocks, no snippets, no syntax, no pseudo-code.
- NEVER read symbols aloud: no camelCase spelled out, no "dot", no "colon", no
  "slash", no curly braces, no angle brackets, no file extensions spoken oddly.
- When you must name a real component, say it as natural spoken words (for
  example: "the part called Player Model", or "a service named Audio Engine")
  and then explain the IDEA in plain English. Never spell an identifier letter
  by letter and never describe syntax.
- Say numbers and units the way a narrator would: "about forty megabytes",
  "version seventeen", "three consecutive matches".
- Define every piece of jargon in one short breath the first time it appears,
  ideally with an everyday analogy.
- Prefer flowing prose. Avoid bullet lists (they sound choppy read aloud). No
  tables. No headings inside the chapter except the single title line at the top.

VOICE: second person ("you"), patient, encouraging, a little wry. Imagine
sitting beside a smart friend learning this for the first time. Short, varied
sentences. Concrete analogies used sparingly and well.

SHAPE of each chapter: open with a hook — a small scene, a question, or a
problem (NOT "In this chapter we will"). Teach the concept plainly. Ground it in
the real worked-example component. Be honest about WHY that choice was made and
what was traded away. Close with a short passage that begins naturally with the
idea of what to carry forward — two to four spoken sentences, no heading.

## Why these rules matter (so you can adapt, not just obey)

- **No code aloud** is the single non-negotiable. A symbol read by a
  text-to-speech voice ("open paren, var, equals") is pure misery. The listener
  wants the *concept*; the syntax is packaging best left on the shelf. Translate
  every real identifier into spoken English the moment you introduce it.
- **Throughlines** are 2-4 ideas that recur across the whole book (for the Echo
  book they were: on-device/private by default; design-for-the-margins as an
  engineering force; the solo-dev-with-AI / "don't build what you don't need
  yet" reality). They give a long listen a spine and make it feel authored, not
  assembled. Pick them from what genuinely recurs in the subject; weave them in
  where they fit, never force all of them into one chapter.
- **Honest tradeoffs** are what separate a real explanation from marketing. Every
  engineering choice gives something up. Naming the cost teaches judgment, which
  is the actual goal — the listener should finish able to *reason*, not recite.

## Length and runtime math

A natural narration runs roughly 150 words per minute at 1.0x, ~187 at 1.25x.

| Target listen | ~Words | Suggested chapters |
|---|---|---|
| ~2 hours (1.25x) | ~22,000 | 8-10 |
| ~3 hours (1.25x) | ~34,000 | 12-14 |
| ~4 hours (1.25x) | ~45,000 | 15-17 |
| ~5 hours (1.25x) | ~56,000 | 17-19 |

Per chapter, aim for ~3,000 words (a 15-18 minute listen). Models reliably hit
this when each chapter has a 6-7 beat sheet with ~450-600 words per beat. They
tend to *overshoot* slightly when given beats — budget for landing 10-25% over
target and tell the user the real number. A few chapters long is fine for an
audiobook; you can offer to trim by tightening prose across all chapters rather
than cutting any single chapter, so the arc stays intact.

## The fact-pack discipline (this is what keeps it accurate)

The model writing a chapter must not invent technical specifics. For each
chapter, assemble a concise **fact pack** — accurate, sourced details about the
worked example — by actually reading its real docs and/or code first. Embed the
fact pack in that chapter's writer prompt with an instruction like: "Ground
everything in these real facts. Use them; simplify for a beginner; translate any
code-like names into spoken English; never contradict them and never invent
technical specifics beyond them." Grounding beats trusting model memory every
time, and it is the difference between a guide the user can trust and plausible-
sounding fiction.

## QC checklist (run after generation, before assembling)

Cheap shell checks catch the things that ruin a narration. Run them over the
chapter files:

- **Real word counts:** `wc -w chapters/ch*.md`. Top up any chapter under its
  floor with a targeted expansion agent. Never trust a model's self-reported
  count.
- **Code-leak sweep** — narration killers that slipped past the rules:
  - backticks / code fences: `grep -l '`' chapters/ch*.md`
  - snake_case tokens (narrate terribly): `grep -oE '[A-Za-z]+_[A-Za-z_]+' chapters/ch*.md | sort | uniq -c | sort -rn`
  - arrows / braces / empty calls: `grep -nE -- '->|[{}]|\b[a-zA-Z]+\(\)' chapters/ch*.md`
  - spoken file extensions: `grep -oE '\.(swift|md|json|py|js|ts|html|xml)\b' chapters/ch*.md | sort | uniq -c`
  If a chapter trips these, send it back to a scrub agent (or fix inline for a
  handful of hits).
- **Heading consistency:** confirm every file's first line is a single heading in
  the same format (e.g. `## Chapter N - Title`), so the EPUB's table of contents
  comes out clean.

## EPUB validity (the builder handles this, but know why)

`scripts/build_book.py` writes a valid EPUB 3 with both a nav document and an
NCX table of contents. The one fragile rule: the `mimetype` entry must be the
first thing in the zip and stored uncompressed. Verify after building:
`python3 -c "import zipfile;z=zipfile.ZipFile('OUT.epub');i=z.infolist()[0];print(i.filename, i.compress_type)"`
should report `mimetype 0`. Including both TOC formats is deliberate — it makes
the book import cleanly into the widest range of readers and audiobook apps.
