# Fan-out template: writing chapters in parallel

The chapters are independent prose, so write them concurrently — one agent per
chapter. Each writer gets the same style bible + throughlines + full table of
contents (for continuity) plus ITS OWN beat sheet and fact pack, and each writes
its own chapter file to disk. The text never has to round-trip through the
orchestrator's context — large prose belongs on disk, not in a tool result.

There are two ways to run the fan-out. Pick based on what's available.

## Option A — Agent tool (default, works anywhere)

Dispatch the chapter-writers as parallel `Agent` calls — multiple in a single
message run concurrently. With many chapters, send them in batches (e.g. 6-8 at
a time) to stay manageable. Each agent's prompt is built from the template at the
bottom of this file. Tell each agent to use the Write tool to save its chapter to
an exact absolute path (`<build-dir>/chapters/chNN.md`, zero-padded) and to
return a one-line status. Then run the QC checks yourself and assemble.

This path needs no special opt-in and is the reliable default.

## Option B — Workflow tool (when the user has opted into multi-agent orchestration)

If the Workflow tool is available and the user has opted into multi-agent
orchestration (e.g. an "ultracode"-style session, or they explicitly asked for a
workflow), a Workflow gives nicer live progress and built-in concurrency
control. Only reach for it under that opt-in — otherwise use Option A. The script
below is the proven shape; fill in CHAPTERS (each with `n`, `title`, `beats[]`,
`facts`), STYLE, SHAPE, TOC, and DIR.

```javascript
export const meta = {
  name: 'explainer-audiobook',
  description: 'Write a narration-ready beginner audiobook; one agent per chapter',
  phases: [{ title: 'Write', detail: 'One writer agent per chapter, each writes its own file' }],
}

const DIR = "/ABSOLUTE/PATH/TO/build/chapters"   // pre-create this directory
const pad = n => (n < 10 ? '0' : '') + n
const TOC = "0. ...\n1. ...\n..."                // full chapter list, for continuity
const STYLE = `...the Voice & rules block from narration-style.md, verbatim...`
const SHAPE = `...the SHAPE paragraph from narration-style.md...`
const THROUGHLINES = `1. ...\n2. ...\n3. ...`    // the 2-4 recurring ideas

const CHAPTERS = [
  { n: 0, title: "Why This Book Exists",
    beats: ["Beat 1 ...", "Beat 2 ...", "..."],   // 6-7 beats, ~450-600 words each
    facts: "Accurate, sourced facts about the worked example for THIS chapter." },
  // ... one object per chapter ...
]

const STATUS_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    n: { type: 'integer' }, title: { type: 'string' },
    approxWords: { type: 'integer' }, wroteFile: { type: 'boolean' },
    oneLineSummary: { type: 'string' },
  },
  required: ['n', 'title', 'approxWords', 'wroteFile'],
}

function buildPrompt(ch) {
  const path = DIR + "/ch" + pad(ch.n) + ".md"
  const beats = ch.beats.map((b, i) => "Beat " + (i + 1) + ": " + b).join("\n")
  return [
    'You are a warm, expert mentor writing ONE chapter of a beginner audiobook.',
    '', STYLE, '',
    'THREE/FOUR THROUGHLINES (weave in where they fit; never force all into one chapter):',
    THROUGHLINES, '',
    'THE WHOLE BOOK (so you know where your chapter sits; light transitions only, do NOT summarize the others):',
    TOC, '',
    'YOUR CHAPTER: Chapter ' + ch.n + ' - ' + ch.title, '',
    'WRITE TO THESE BEATS (each ~450-600 spoken words; expand vividly):', beats, '',
    'GROUND EVERYTHING IN THESE REAL FACTS (accurate; simplify for a beginner; translate code-like names to spoken English; never contradict; never invent beyond them):',
    ch.facts, '',
    SHAPE, '',
    'LENGTH: at least 2,800 words; aim 3,000-3,400. Earn the length with vivid explanation, analogy, and honest detail — do not pad with repetition.', '',
    'OUTPUT: 1) Write the chapter as plain spoken prose, beginning with exactly one heading line: "## Chapter ' + ch.n + ' - ' + ch.title + '". 2) Use the Write tool to save it to EXACTLY this absolute path (overwrite if present): ' + path + '. 3) Return the status object.', '',
    'Final reminder: this is SPOKEN ALOUD. If a sentence would sound like someone reading code or symbols, rewrite it as natural English. No code, ever.',
  ].join("\n")
}

phase('Write')
const results = await parallel(CHAPTERS.map(ch => () =>
  agent(buildPrompt(ch), {
    label: 'ch' + pad(ch.n) + ': ' + ch.title.slice(0, 22),
    phase: 'Write', schema: STATUS_SCHEMA,
  })
))
const ok = results.filter(Boolean)
return {
  filesWritten: ok.filter(r => r.wroteFile).length,
  approxTotalWords: ok.reduce((s, r) => s + (r.approxWords || 0), 0),
  perChapter: ok.map(r => ({ n: r.n, title: r.title, approxWords: r.approxWords })),
}
```

## Notes that save a re-run

- **Pre-create the chapters directory** before dispatching, or the agents' Write
  calls land nowhere.
- **Self-reported word counts are unreliable.** The agents return a guess; get
  the truth with `wc -w` afterward and top up any chapter that fell short.
- **One writer per chapter, not per beat.** Splitting finer fragments the voice
  and invites repetition across fragments.
- **Continuity over summary.** Giving every writer the full TOC lets them make
  light "remember the sandbox from earlier" transitions without re-explaining
  other chapters.
