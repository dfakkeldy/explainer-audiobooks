---
name: fiction-book-development
description: >-
  Use when planning, drafting, revising, or continuing a novel, novella, or short-story collection. Builds a coherent fiction manuscript with one lead writer, an approved story bible, deliberate prose style, scene-level causality, continuity ledgers, and separate structural-to-line revision passes. Stops at an approved Markdown manuscript unless production is explicitly requested.
---

# Fiction Book Development

Develop original fiction from premise to an approved Markdown manuscript. This
skill owns story architecture, characters, scenes, continuity, prose voice, and
revision. It does **not** own covers, EPUB/M4B rendering, narration, alignment,
packaging, or delivery.

## When to Use

Use for:

- novels, novellas, serial fiction, or linked short-story collections;
- a fiction vertical slice before committing to a full manuscript;
- continuing or repairing an existing fictional manuscript;
- story-bible, scene, character, POV, dialogue, pacing, or continuity work;
- choosing and applying a distinct fiction prose style.

Do not use for technical explainers, learning books, narrative nonfiction, or a
request that only concerns production. Route those to the corresponding book or
audiobook skill.

## Required References

- Read `references/story-bible-and-continuity.md` before outlining or continuing
  a manuscript.
- Read `references/style-and-scene-craft.md` before selecting a prose mode or
  drafting scenes.
- Read `references/revision-passes.md` before revising a chapter or manuscript.
- Start a new project from `templates/fiction-project.md`.

## Scope Gate

Restate the requested fiction outcome in one sentence. Classify it as premise,
vertical slice, outline, draft, continuation, or revision. Work only in that
lane. Never infer cover, narration, packaging, or publishing work from a fiction
request.

## Core Contract

1. **One manuscript owner.** One frontier model owns the story bible and all
   canonical prose. Workers may research, inspect, challenge, and report; they
   do not independently write competing chapters.
2. **Bible before volume.** Lock the premise, genre promise, audience, POV,
   tense, central characters, world rules, ending direction, and explicit
   exclusions before drafting at scale.
3. **Causality over chronology.** Every scene changes the available choices,
   information, relationships, risk, or emotional state. A scene that merely
   reports what happened next must be combined, transformed, or cut.
4. **Style by observable choices.** Define distance, syntax, diction, imagery,
   interiority, dialogue texture, humour, and taboo habits. Do not request an
   imitation of a living author. Translate references into craft attributes.
5. **Continuity is active.** Update timeline, location, knowledge, relationship,
   object, injury, promise, mystery, and foreshadow/payoff ledgers after every
   accepted chapter.
6. **Revision is staged.** Repair premise/structure before character, character
   before scene, scene before continuity/pacing, and all of those before line
   prose. Never polish scenes likely to be removed.
7. **Markdown is canonical.** Keep planning artifacts separate from manuscript
   chapters. Do not let notes, diagnostics, or alternate drafts silently replace
   accepted prose.
8. **Production is opt-in.** Completion here is an approved manuscript plus its
   current bible and ledgers. Hand off to a production skill only when the user
   explicitly asks.

## Workflow

### 1. Create the project

Create a private workspace unless the user explicitly approves public-safe
publication:

```text
.build/fiction/<slug>/
  brief.md
  story-bible.md
  outline.md
  scene-cards/
  chapters/
  continuity/
  research/
  revisions/
```

Copy the headings from `templates/fiction-project.md`. Record privacy and rights
status. **Done when:** the workspace exists and scope, audience, form, length,
and exclusions are explicit.

### 2. Develop the premise and genre promise

Write a one-sentence dramatic premise, the reader experience being promised,
the central source of opposition, the consequence of failure, and the change
that makes the ending possible. Offer at most three materially different
options when the direction is unclear. **Done when:** the user approves one
premise and genre promise, or explicitly delegates the choice.

### 3. Build the story bible

Define characters as pressure systems—not biographies. For each principal
character record desire, need, fear, contradiction, leverage, limits, voice,
relationships, and likely change. Define world rules only where they constrain
choices. Establish POV/tense rules, timeline, major turns, ending direction, and
content boundaries. Follow `story-bible-and-continuity.md`.

**Done when:** every major turn is supported by character motive and world rules,
and no unresolved foundational question blocks the opening chapters.

### 4. Validate a vertical slice

Unless the user supplies a mature manuscript plan or explicitly requests an
autonomous full draft, create:

1. a three-chapter outline;
2. scene cards for those chapters;
3. one complete representative chapter; and
4. one continuity and revision pass.

Evaluate whether the premise generates pressure, characters make consequential
choices, the style is sustainable, and the chapter creates forward pull.
**Done when:** the user approves the story contract or the autonomous brief's
acceptance criteria all pass.

### 5. Outline as turns, not summaries

Map setup, escalation, reversals, crisis, climax, and aftermath at the scale the
form needs. Each chapter must have a dramatic job and alter at least one story
state. Track planted promises and expected payoffs without making every turn
predictable. **Done when:** removing any planned chapter would create a named
causal, emotional, or thematic gap.

### 6. Prepare scene cards just in time

Before each chapter, create cards with viewpoint, location/time, immediate goal,
opposition, stakes, opening imbalance, turn, consequence, emotional movement,
revealed/withheld information, continuity dependencies, and exit pressure.
Cards are constraints, not prose templates. **Done when:** each scene has a turn
and its consequence forces or complicates what follows.

### 7. Draft sequentially

The lead writer drafts chapters in order using the current bible, accepted
chapters, continuity delta, and upcoming scene cards. Start scenes under
pressure; dramatize decisive moments; summarize connective tissue deliberately.
Do not explain an emotion already carried by action, image, or dialogue.

After each chapter:

- run a read-aloud pass;
- record continuity deltas and new promises;
- flag discoveries that require bible or outline changes;
- obtain approval when the workflow is collaborative.

**Done when:** the chapter satisfies its dramatic job, creates a changed state,
and the ledgers match the accepted text.

### 8. Revise in separate passes

Apply `revision-passes.md` in order: structure, character/causality, scene,
continuity/world logic, pacing, dialogue/POV, then prose. Record findings before
editing, and preserve intentional voice variation. A diagnostic worker reports;
the lead writer accepts or rejects and performs substantive rewrites.

Before structural revision, reverse-outline the manuscript actually written.
When consequential real-world behaviour, institutions, geography, history,
health, disability, trauma, or cultural practice appears, resolve the research
and representation ledger rather than smoothing uncertainty into confident
fiction. Use targeted readers when warranted; they inform rather than grant
permission or replace author responsibility.

**Done when:** each pass has an accepted/rejected findings record and no earlier
pass remains invalidated by a later change.

### 9. Close the manuscript

Read the manuscript front to back without editing, then record only whole-book
problems. Resolve open continuity items, verify planted promises have deliberate
payoffs or deliberate ambiguity, and reconcile the bible to final canon.

**Done when:** chapters, bible, continuity ledgers, revision record, and a clean
combined Markdown manuscript agree; unresolved creative choices are explicitly
listed rather than silently guessed.

## Common Pitfalls

1. **Wiki-first worldbuilding.** Build only rules that constrain action or create
   meaning; defer decorative lore until a scene requires it.
2. **Character dossiers without behaviour.** Convert traits into choices under
   pressure, competing wants, limits, and consequences.
3. **Outline obedience.** Preserve causality and promise, not obsolete beats. When
   drafting discovers a better truth, update the bible and downstream outline.
4. **Uniform scene rhythm.** Vary scene length, entry point, compression, silence,
   and aftermath while keeping each scene's dramatic turn clear.
5. **Explanatory dialogue.** Give speakers private aims, unequal knowledge, and
   reasons not to say exactly what they mean.
6. **POV leakage.** Track what the viewpoint character can perceive, infer, know,
   and misread at that moment.
7. **Style by adjective.** “Lyrical” or “gritty” is insufficient. Specify the
   observable prose controls in the style reference.
8. **Premature line editing.** Fix the highest-level failed pass first.
9. **Competing chapter authors.** Parallel prose generation produces voice and
   continuity drift. Parallelize research and diagnosis, not canonical drafting.
10. **Accidental production.** A finished manuscript does not authorize covers,
    narration, packaging, or publication.

## Verification Checklist

- [ ] Requested lane and privacy status are explicit.
- [ ] Premise and genre promise are approved.
- [ ] Story bible records POV, tense, character engines, world constraints, turns,
      ending direction, boundaries, and prose controls.
- [ ] Every accepted scene changes story state and has a consequence.
- [ ] One lead writer owns canonical prose.
- [ ] Continuity ledgers reflect every accepted chapter.
- [ ] Structural-to-line revision passes were completed in order.
- [ ] Dialogue voices remain distinguishable without dialogue tags.
- [ ] POV knowledge and world rules survive spot checks.
- [ ] Planted promises and payoffs are reconciled.
- [ ] Consequential factual uncertainties and representation risks have an
      explicit disposition.
- [ ] Final Markdown, bible, and ledgers agree.
- [ ] No production work occurred without explicit authorization.
