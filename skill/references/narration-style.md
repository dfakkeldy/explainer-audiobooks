# Narration style bible

This is the craft layer of the explainer-audiobook skill. The whole product is
*heard*, never read on a page, so every rule below exists to serve the ear. Hand
the "Voice & rules" block to every chapter-writer verbatim — consistency across
independently-written chapters depends on it.

## Voice & rules (give this block to every writer agent verbatim)

THIS WILL BE NARRATED ALOUD as an audiobook. Write 100% for the EAR.

NEVER READ CODE OR SYMBOLS ALOUD (this one is absolute):
- No code blocks, snippets, syntax, or pseudo-code.
- Don't spell out multi-token identifiers or operators: no camelCase read letter
  by letter, no snake_case (it narrates as "underscore"), no spoken "open brace",
  "arrow", "colon", "equals", no empty "open paren close paren".
- For any name that would narrate badly (camelCase, snake_case, punctuation in the
  middle), say it in plain words instead — "the view-did-load step", "the
  render-version stamp" — and explain the idea.

DO NAME THE REAL THINGS (this is how the listener learns the vocabulary):
- Name the actual files, tools, commands, and components by their real names, the
  way a podcaster says them out loud. A plain filename is fine spoken: "a file
  called CLAUDE.md", "the settings.json file", "the git command", "a tool called
  Instruments". The listener should finish able to recognise these by name and go
  look them up.
- Introduce each real name the first time with a one-breath gloss of what it is and
  does: "a file called CLAUDE.md — think of it as your project's standing house
  rules, written down once so they're followed every time." Name first, then the
  idea.
- Don't hide real things behind vague paraphrases. Saying "the settings file" when
  you mean settings.json, or "a configuration thing" when you mean a named tool,
  robs the listener of the exact word they need. Prefer the real name plus a
  plain-English gloss every time.

EMPHASIS — say it once, plainly, then move on:
- When something genuinely matters, say so in ordinary words, once, and let the
  explanation itself carry the weight. The clearest writing rarely announces its
  own importance.
- Most paragraphs should make no claim about how important they are. If every point
  is "the most important thing" or "the heart of it all," none of them lands.
- Dead phrases — never use these or anything in their family: "tattoo this", "burn
  this into", "sear/etch/carve this", "the one rule, if you remember nothing else
  from this chapter", "the single most important", "the whole point / the whole
  show / the whole game / the entire job", "the most X in the whole craft", "it
  changes everything". They are verbal tics that ring false read aloud.

NUMBERS, JARGON, FORM:
- Say numbers and units like a narrator: "about forty megabytes", "version
  seventeen", "three matches in a row".
- Define each piece of jargon in one short breath the first time, ideally with an
  everyday analogy.
- Flowing prose. Avoid bullet lists (they sound choppy aloud), no tables, and no
  headings inside the chapter except the single title line at the top.

VOICE: second person ("you"), patient, encouraging, a little wry — a smart friend
explaining over coffee, not a motivational speaker. Short, varied sentences.
Concrete analogies used sparingly. Trust the listener; never oversell.

SHAPE of each chapter: open with a hook — a small scene, a question, or a problem
(NOT "In this chapter we will"). Teach the concept plainly. Ground it in the real,
named worked-example component. Where the design genuinely gave up one thing to get
another, name that tradeoff once and cleanly, then move on — only where the cost is
real, never as a reflex, and never the same cost restated several ways (even when
the whole chapter is about a tradeoff, you make the point once). Close with two to
four spoken sentences that point ahead to what the listener can now understand or
do — no heading, and without announcing it ("to sum up", "the takeaway", "carry
this forward").

## Why these rules matter (so you can adapt, not just obey)

- **No code aloud** is the single non-negotiable. A symbol read by a
  text-to-speech voice ("open paren, var, equals") is pure misery. The listener
  wants the *concept*; raw syntax is packaging best left on the shelf.
- **Naming the real things** is the other half of that rule, and just as important.
  "No code aloud" does NOT mean "no real names." A listener who finishes a book on
  Claude Code without ever hearing the words *CLAUDE.md* or *settings.json* can't
  find those things on their own machine — the book taught a fog. Say the real
  file, tool, and command names out loud (in spoken-friendly form) and gloss each
  one. The test: could the listener, afterwards, search for the thing you described?
  If you only gave them "the settings file," no. If you said settings.json, yes.
- **Earned emphasis.** Importance is a currency that inflates. If the narrator keeps
  insisting each idea is the most important one, the listener stops believing any of
  it. State that something matters once, plainly, and spend the rest of the breath
  *showing* why. The flat, confident register is what makes the rare genuine "this
  one really matters" land.
- **Honest tradeoffs, used sparingly.** Every engineering choice technically gives
  something up, but you do not have to narrate the cost of all of them — that turns
  into a drone of "but of course there's a tradeoff" that teaches nothing. Name a
  tradeoff where the alternative was real and a thoughtful listener would genuinely
  wonder why it wasn't taken. A typical chapter has one or two such moments,
  sometimes none. Naming the cost *there* teaches judgment; naming it everywhere
  teaches the listener to tune you out. And make the point ONCE: even when a whole
  chapter is about a single tradeoff, state the cost cleanly in a sentence or two
  and move on — restating the same bargain five ways ("there's no free lunch",
  "that's the trade", "two different bargains", "the thing you refuse to give up")
  is the exact drone that flattens a real insight into filler.
- **Throughlines** are 2-4 ideas that recur across the whole book (for the Echo
  book they were: on-device/private by default; design-for-the-margins as an
  engineering force; the solo-dev-with-AI / "don't build what you don't need yet"
  reality). They give a long listen a spine and make it feel authored, not
  assembled. Pick them from what genuinely recurs in the subject; weave them in
  where they fit, never force all of them — or all of the tradeoff talk — into one
  chapter.

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
worked example — by actually reading its real docs and/or code first. **Include the
real names** the listener should come away knowing: the actual files, tools,
commands, and components this chapter touches, each with a one-line plain-English
gloss. Embed the fact pack in that chapter's writer prompt with an instruction
like: "Ground everything in these real facts. Name these real things out loud and
gloss them; use them; simplify for a beginner; translate code-like *syntax* into
spoken English, but keep the real *names*; never contradict the facts and never
invent technical specifics beyond them." Grounding beats trusting model memory
every time, and it is the difference between a guide the user can trust and
plausible-sounding fiction.

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
    (also eyeball for stray camelCase identifiers like viewDidLoad — they're too
    entangled with legitimate brand names like iPhone, iOS, macOS to grep cleanly)
  - Plain dotted *filenames* spoken naturally (settings.json, CLAUDE.md) are now
    fine and wanted — do NOT scrub those. Scrub only raw syntax, operators, and
    multi-token identifiers.
- **Cliché / over-emphasis sweep** — the voice tics this skill is prone to:
  - dead phrases: `grep -rniE 'tattoo|burn (this\|it) into|sear (this\|it)|etch (this\|it)|carve (this\|it)|the one rule, if you|if you remember nothing else' chapters/ch*.md` — should return nothing; rewrite any hit. (Bare `sear`/`etch` are deliberately avoided — they match "search" and "sketch".)
  - emphasis-inflation density: `grep -ronE 'the (single )?most important|the heart of|the whole point|the real (magic|secret|power)|matters more than anything' chapters/ch*.md | cut -d: -f1 | sort | uniq -c | sort -rn` — a chapter with many hits is overselling; send it back to flatten the register.
  - tradeoff drone: `grep -roniE 'trade[- ]?off|the cost of|every (choice|decision)|comes at a (cost|price)|nothing is free' chapters/ch*.md | cut -d: -f1 | sort | uniq -c | sort -rn` — more than two or three in one chapter usually means the tradeoff throughline has become a tic; thin it to the moments that are real.
- **Vocabulary check (codebase-grounded books):** for each chapter, confirm the real
  file/tool/command names from its fact pack actually appear *by name* in the prose
  (not paraphrased into "the settings file"). If the listener couldn't search for
  the thing afterwards, the chapter generalised too far — send it back to name it.
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
