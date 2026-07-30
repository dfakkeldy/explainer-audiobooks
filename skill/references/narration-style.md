# Narration style bible

Contents: Voice & rules (verbatim block for the frontier lead author) · Why
these rules matter · Length and runtime math · The fact-pack discipline · The
story ledger · QC checklist · EPUB validity.

This is the craft layer of the audiobook skill. The whole product is
*heard*, never read on a page, so every rule below exists to serve the ear. Give
the "Voice & rules" block to the frontier lead author verbatim. Cheap workers may
review against it, but they must not replace its prose with a different voice.
Read `road-book-mode.md` first. Unless the brief explicitly selects
`focused-study`, assume the listener is driving and delivering mail, with eyes
unavailable and attention shared with safe work.

## Voice & rules (give this block to the frontier lead author verbatim)

THIS WILL BE NARRATED ALOUD as an audiobook. Write 100% for the EAR.

ROAD-BOOK LOAD — protect a one-pass listener:
- Let a governing question, human situation, history, people, and varied
  real-world applications create the need for each mechanism. These are teaching
  infrastructure, not decorative interludes.
- Introduce no more than two or three genuinely new core terms in a chapter.
  Give the listener-visible problem before the name.
- A brief spoken calculation carries at most three temporary values and three
  symbolic steps, then returns to a concrete case. Move anything that needs
  visual persistence, replay, or a longer chain into optional study material or
  an explicitly short focused lesson.

CODE ALOUD — at most ONE short line at a time:
- Never a code block, multi-line snippet, or two code lines back to back. Code the
  listener can't follow by ear is packaging, not teaching.
- A single short command or line IS allowed — and, for command-driven subjects
  like git, encouraged — when every token speaks naturally: "git status", "git
  commit", "swift build". Say it once, slowly, in spoken form, then immediately
  unpack what each part does. Explanation always goes between lines.
- If a line can't be spoken cleanly, describe it instead. Don't spell out
  operators or multi-token identifiers: no camelCase read letter by letter, no
  snake_case (it narrates as "underscore"), no spoken "open brace", "arrow",
  "colon", "equals", no empty "open paren close paren".
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
- Terms are learned by repetition, not introduction. After the first full gloss,
  re-use each key term and command in later chapters with a half-breath reminder
  ("git rebase — the rewrite-history command") until it plainly needs none. The
  core vocabulary should be heard several times, in context, before the book
  ends — one mention teaches recognition; several teach recall.

NOVELTY AND DEPTH — every paragraph earns its place:
- Give each paragraph one dominant job: introduce, explain a mechanism, work
  through an example, contrast an alternative, expose a failure mode, apply the
  idea, or retrieve it briefly. Do not say the same claim again with different
  metaphors unless the new paragraph adds a different job.
- A return to a core concept must perform a named learning function: retrieve it
  after a gap, deepen its mechanism, apply it in a new situation, compare it to
  an alternative, or correct a likely misconception. A bare redefinition is
  padding, even if it is elegantly phrased.
- Teach important concepts in layers across the book: what it is, why it exists,
  how it works, a concrete case, and the boundary where the simple story breaks.
  Do not make every minor term carry all five layers, but do not call a concept
  explained after one vague definition either.
- Prefer a specific observation, decision, failure, or worked example to a
  generic claim about what "matters." Frame a practical example as a situation,
  a choice or action, and a consequence. A clearly signaled hypothetical can
  rehearse application, but it must not carry unsupported facts.
- When using an analogy, make its working relationship and correspondences
  clear, then name where it stops matching. Make it a short, reusable retrieval
  handle; do not parade a succession of new metaphors past the same idea. A
  comparison that supplies only atmosphere does not teach.
- Do not inflate a chapter to hit a uniform word count. End a chapter when its
  promised knowledge delta is complete; deeper concepts may need more space,
  while orientation and transition chapters may be shorter.

KEY-POINTS CHECKPOINTS — make understanding testable:
- At the natural learning boundaries named in the outline, use the recognizable
  spoken cue "Key points." Give two to four short, flowing sentences that
  retrieve the idea, reconnect it to a concrete decision, or rehearse the next
  useful action. One may ask a brief question and then answer it.
- Add no new fact, term, example, or analogy in the checkpoint. Do not inventory
  every detail, turn it into a visual bullet list, or attach the same recap to
  every minor section. A narrative bridge may need no checkpoint.

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

FIGURES (only if your prompt lists figures for this chapter):
- Insert each listed figure exactly once, as its own paragraph, at the beat where
  it fits: `![alt text](images/filename.png "A caption that stands alone")`.
- The listener probably can't see it — they may be driving and review the images
  only afterwards. So the prose must work with eyes closed: describe the thing
  fully in words as if the figure weren't there. Never say "as you can see",
  "shown below", "see the figure", "pictured here".
- The caption is read *later*, out of context, so it names what the image shows
  and why it matters in one self-contained sentence.

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

VOICE SOURCE: when the user supplies private books or audio as an enjoyable
technical-writing reference, analyze them into `voice-source-profile.md`. Carry
forward high-level craft—question or ordinary-situation openings,
evidence-to-example movement, plain-language mechanisms, restrained humor,
precise uncertainty, varied rhythm, and practical landings. Do not copy source
passages or request a pastiche. Once the human accepts the project-authored first
section, use `voice-exemplar.md` as the concrete style input for every later
section call.

SECTION INPUT: draft section by section. Every call receives the full
argument-level outline, grounded claim IDs, the approved voice exemplar, the
previous section text, this section's job, and what it must not repeat. A
summary hands the author facts and strips cadence — always pass the actual
previous section text. A prose prompt without those artifacts is incomplete.

DE-CLAUDIFICATION — the listener's named AI-writing patterns to avoid are hard
bans during drafting, not just a QC finding. State the fact directly instead
of managing the listener's reaction. Do not synonym-cycle through hold,
carry, keep, sit with, notice, pause, resist, or let-that-land instructions; do
not use repeated `let me`, `not X but Y`, announced transitions, or honesty
announcements such as `honestly` and `the honest answer` as a voice. Put
epistemic precision and uncertainty in the claim itself. `declaudification.md`
runs the full density review at QC time, once before the humanizer and again
after.

BUDGETS — caps you write toward, not gates that fail a build:
- At most three genuinely new core terms per chapter.
- Six to ten durable book outcomes across the whole book.
- At most three temporary values and three symbolic steps in any spoken
  calculation.
- At least one real, sourced story anchor per chapter — see
  `research/story-ledger.md` — or a recorded exemption.
- Arithmetic language stays inside the brief's declared tier.
- No coordinated list of four or more items. Name the one that carries the
  point; the rest belongs in the reference appendix, not the narration.
- Vary sentence and paragraph length deliberately. Uniform rhythm is the most
  reliable signature of assembled prose — more reliable than any phrase.

MODAL CONVERSION: statutory and API sources arrive in *may* and *must*.
Convert them into people doing things: "The holder may collect rent" becomes
"The rent cheques start coming to you." Where a modal must survive because the
condition genuinely matters, name who is bound by it.

SHAPE of each chapter: give the chapter a distinct job in the book — perhaps a
scene, a mechanism, a guided walkthrough, a comparison, a failure analysis, or
an application — rather than running every chapter through the same hook →
concept → tradeoff → recap mould. Open with a concrete scene, question, or
problem when it serves the chapter; never use a generic "In this chapter" opener.
Teach the concept plainly and ground it in the real, named worked-example
component. Where the design genuinely gave up one thing to get another, name that
tradeoff once and cleanly, then move on — only where the cost is real, never as a
reflex, and never the same cost restated several ways. Close with the natural
last beat for this chapter: a planned `Key points` checkpoint, a consequence, a
mini-application, or the next useful question. Do not bolt on the same generic
recap or "you can now" line every time. A core term may be re-named at the close
only when it helps recall or advances the next chapter.

## Why these rules matter (so you can adapt, not just obey)

- **One line of code at a time, at most.** A block of symbols read by a
  text-to-speech voice ("open paren, var, equals") is pure misery. But a single
  speakable command — said slowly, then unpacked — is how a listener actually
  learns the commands they'll type later; banning code outright taught concepts
  while leaving the listener unable to *do* anything. The line count is the rule:
  one line, then talk.
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

Use these as book-level planning ranges, not a quota to divide equally among
chapters. A natural narration runs roughly 150 words per minute at 1.0x, ~187 at
1.25x. Let a chapter be as short as the listener's knowledge delta allows and as
long as a worked explanation needs; uniform three-thousand-word chapters are a
reliable way to manufacture filler. Estimate chapter lengths in the outline and
report the real final total. Falling outside the estimate is a planning signal,
not a reason to add or remove material after the learning job is complete.

| Target listen | ~Words | Suggested chapters |
|---|---|---|
| ~2 hours (1.25x) | ~22,000 | 8-10 |
| ~3 hours (1.25x) | ~34,000 | 12-14 |
| ~4 hours (1.25x) | ~45,000 | 15-17 |
| ~5 hours (1.25x) | ~56,000 | 17-19 |

A dense technical chapter may need 2,500-3,500 words, while an orientation,
bridge, or application chapter may be much shorter. If the book runs long, first
remove redundant explanations and decorative transitions; do not cut the only
worked example or boundary that makes a difficult concept understandable.

## The fact-pack discipline (this is what keeps it accurate)

The model writing a chapter must not invent technical specifics. For each
chapter, assemble a concise **fact pack** — accurate, sourced details about the
worked example — by actually reading its real docs and/or code first. **Include the
real names** the listener should come away knowing: the actual files, tools,
commands, and components this chapter touches, each with a one-line plain-English
gloss. Embed the fact pack in that chapter's frontier-author prompt with an instruction
like: "Ground everything in these real facts. Name these real things out loud and
gloss them; use them; simplify for a beginner; translate code-like *syntax* into
spoken English, but keep the real *names*; never contradict the facts and never
invent technical specifics beyond them." For command-driven subjects (git, the
shell, build tools), the fact pack should also mark the handful of commands the
listener must come away knowing cold — the frontier author voices each of those at
least twice in the chapter, once introduced and once in passing. Grounding beats trusting model memory
every time, and it is the difference between a guide the user can trust and
plausible-sounding fiction.

## The story ledger (this is what keeps a book from coming out storyless)

Books come out storyless for a specific reason: the fact pack collects
statutes and API surfaces, so at drafting time the author has no narrative
material on hand and invents a hypothetical. Fix it at the source, during
research, before the outline freezes — add a story-ledger section to
`source/research.md`.

Each entry records:

- what happened, in one line;
- named actors, place, and date;
- a source citation;
- which concept the entry carries;
- **the reversal** — what a reasonable person would have expected instead. No
  reversal means it is an example, not a story, and it does not count.

Sources are documented and institutional only: published decisions, papers,
post-mortems, news reports, real repository history, and named public figures
acting in public roles. Never private individuals.

Every chapter plan names a ledger entry it uses, or records an exemption with
a reason. An exemption is a recorded decision, not a silent gap.

## QC checklist (run after generation, before assembling)

This craft checklist complements the chapter teaching plans and blind beginner
review in `learning-design.md`. It does not replace either.

Tool-backed checks and cheap editorial review catch the things that ruin a
narration without letting a lower-cost model take over the author's voice. Run
them over the chapter files:

- **Real word counts:** `wc -w chapters/ch*.md`. Investigate a chapter that
  misses its outline estimate; do not automatically top it up. The question is
  whether its promised knowledge delta is incomplete, not whether it matches a
  uniform quota.
- **Code-leak sweep** — narration killers that slipped past the rules:
  - backticks / code fences: `grep -l '`' chapters/ch*.md`
  - snake_case tokens (narrate terribly): `grep -oE '[A-Za-z]+_[A-Za-z_]+' chapters/ch*.md | sort | uniq -c | sort -rn`
  - arrows / braces / empty calls: `grep -nE -- '->|[{}]|\b[a-zA-Z]+\(\)' chapters/ch*.md`
    (also eyeball for stray camelCase identifiers like viewDidLoad — they're too
    entangled with legitimate brand names like iPhone, iOS, macOS to grep cleanly)
  - Plain dotted *filenames* spoken naturally (settings.json, CLAUDE.md) are
    fine and wanted — do NOT scrub those. The same goes for a deliberate
    single-line spoken command ("git commit", "swift build"). Scrub only
    multi-line blocks, raw operators, and multi-token identifiers — and confirm
    no two code lines sit back to back without explanation between.
- **Cliché / over-emphasis sweep** — the voice tics this skill is prone to:
  - dead phrases: `grep -rniE 'tattoo|burn (this\|it) into|sear (this\|it)|etch (this\|it)|carve (this\|it)|the one rule, if you|if you remember nothing else' chapters/ch*.md` — should return nothing; rewrite any hit. (Bare `sear`/`etch` are deliberately avoided — they match "search" and "sketch".)
  - emphasis-inflation density: `grep -ronE 'the (single )?most important|the heart of|the whole point|the real (magic|secret|power)|matters more than anything' chapters/ch*.md | cut -d: -f1 | sort | uniq -c | sort -rn` — a chapter with many hits is overselling; send it back to flatten the register.
  - tradeoff drone: `grep -roniE 'trade[- ]?off|the cost of|every (choice|decision)|comes at a (cost|price)|nothing is free' chapters/ch*.md | cut -d: -f1 | sort | uniq -c | sort -rn` — more than two or three in one chapter usually means the tradeoff throughline has become a tic; thin it to the moments that are real.
  - honesty-announcement density: the governed `prose_qc.py` family catches
    `honestly`, `the honest answer`, `to be honest`, `in all honesty`, and close
    variants such as `let's be honest`, `truth be told`, `frankly`, and
    `candidly`. Replace announcements with the exact evidence, uncertainty, or
    boundary.
- **Repetition and depth review:** run
  `/usr/local/bin/python3 skill/scripts/prose_qc.py --chapters-dir chapters --out research/prose-qc.md`.
  Inspect its repeated-phrase, similar-paragraph, and opening/closing candidates
  against the outline and chapter plan: retain a repeat only when it retrieves,
  deepens, applies, compares, or corrects a concept. Give a cheap reviewer the
  report and research, then require a citation-first finding for every genuine
  issue: location, evidence, listener cost, and repair type. It reports; the
  frontier author writes substantive fixes.
- **Explanation-stack check:** for each core chapter-plan concept, verify the book gives
  the listener the promised definition, reason, mechanism, concrete case, and
  useful boundary/counterexample where applicable. Flag a shallow claim with its
  exact location rather than asking a cheaper model to expand it generically,
  and rerun blind beginner review after any accepted repair.
- **Key-points checkpoint review:** verify each planned checkpoint is at a
  meaningful learning boundary, contains two to four speakable recall or action
  points, and introduces no new material. Flag repeated boilerplate and any
  checkpoint that reads like an on-page list. Judge the rendered version in the
  ear-pass; silent readability does not prove the cue works while driving.
- **Vocabulary check (codebase-grounded books):** for each chapter, confirm the real
  file/tool/command names from its fact pack actually appear *by name* in the prose
  (not paraphrased into "the settings file"). If the listener couldn't search for
  the thing afterwards, the chapter generalised too far — send it back to name it.
  Also check *reinforcement*: grep a few core terms and commands across all of
  chapters/ch*.md — the vocabulary the book most wants to teach should recur in
  later chapters, not appear exactly once and vanish.
- **Figure check (if figures were used):** every `![...]` line references a file
  that actually exists in `chapters/images/` (build_book.py drops missing ones
  with a warning — don't ship a book that warned), each has alt text and a
  standalone caption, and the prose never leans on the image:
  `grep -rniE 'as you can see|shown below|see the (figure|image)|pictured' chapters/ch*.md`
  should return nothing.
- **Heading consistency:** confirm every file's first line is a single heading in
  the same format (e.g. `## Chapter N - Title`), so the EPUB's table of contents
  comes out clean.

## EPUB validity (the builder handles this, but know why)

`skill/scripts/build_book.py` writes a valid EPUB 3 with both a nav document and an
NCX table of contents. The one fragile rule: the `mimetype` entry must be the
first thing in the zip and stored uncompressed. Verify after building:
`/usr/local/bin/python3 -c "import zipfile;z=zipfile.ZipFile('OUT.epub');i=z.infolist()[0];print(i.filename, i.compress_type)"`
should report `mimetype 0`. Including both TOC formats is deliberate — it makes
the book import cleanly into the widest range of readers and audiobook apps.
