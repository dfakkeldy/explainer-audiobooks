---
name: longform-book-development
description: >-
  Use when developing a long-term book or audiobook project over multiple turns:
  rough ideas, back-and-forth concept shaping, outline approval, source and
  picture gathering, visual/figure planning, and final handoff to
  custom-learning-audiobook for manuscript synthesis, EPUB building, and
  narration.
---

# Longform Book Development

## Production mode comes first

Read `../../skill/references/unattended-production.md` before asking development
questions. This skill remains conversational for an explicitly exploratory
request. An overnight, ready-to-listen, delegated, or multi-book request selects
`unattended-first-listen`: make reversible editorial decisions, record them in
`research/unattended-decisions.json`, complete the handoff, and invoke
`custom-learning-audiobook` without another approval pause. Human checkpoint
language below applies to `governed-final`; unattended mode follows the shared
editorial checkpoint and package-or-blocker contract.

Shape a durable book project before synthesis. This skill owns the messy
creative conversation: turning scattered ideas into an approved brief, outline,
source plan, picture plan, and handoff packet for `custom-learning-audiobook`.

Do not use this skill for a simple "make me a book about X" request that is ready
for one-pass production. Use `custom-learning-audiobook` directly for that.
Do not use it for novels, novellas, or short-story collections; route fiction to
`fiction-book-development`, which owns story bibles, canonical prose, continuity,
and fiction-specific revision.

## Required Reference

- Read `references/handoff-packet.md` before preparing the final handoff.
- Read `../../skill/references/unattended-production.md` before intake and mode
  selection.
- Read `../../skill/references/road-book-mode.md` before shaping an audiobook.
  Default to road-book mode for driving and delivering mail unless the listener
  explicitly wants focused study.
- Read `../../skill/references/learning-design.md` before shaping the curriculum
  or declaring a handoff production-ready.
- Read `../../skill/references/frontier-manuscript-pipeline.md` before defining
  research, outline, voice-calibration, section-drafting, or revision handoffs.
- Read `../../skill/references/curriculum-patterns.md` before proposing book
  structures or recording the selected progression.
- Read `../../skill/references/humanizer-pass.md` when shaping voice notes or
  preparing the production handoff. The final prose pass is bounded: it removes
  AI tics without inventing personality, anecdotes, sources, or claims.
- Read `../../skill/references/declaudification.md` and capture the listener's
  **AI-writing patterns to avoid**, disliked phrase families, and any positive
  voice sample before preparing the production handoff.

## Workflow

1. **Create a project workspace.** Use
   `.build/longform-book-development/<slug>/` unless the user gives another
   path. Create `brief.md`, `outline.md`, `conversation-log.md`,
   `visuals/manifest.md`, and `handoff/handoff-packet.md` as the project
   matures. Keep private or speculative material out of public book folders.

2. **Clarify in small batches.** In governed-final, ask no more than 2-3
   questions at a time. In unattended-first-listen, use and record documented
   defaults rather than asking about routine preferences.
   Favor useful prompts over interrogation: audience, outcome, tone, what to
   include or avoid, source material, privacy, and whether the final product is a
   book, audiobook, illustrated EPUB, or all of those.
   Establish actual prior knowledge, the outcome the listener wants, and the
   opening orientation: context, promise, and route through the subject. For an
   audiobook, confirm whether the listener expects the usual road-book context:
   driving and delivering mail, with eyes unavailable and interruptions likely.

3. **Maintain the evolving brief.** After each meaningful turn, update the
   working brief with confirmed decisions, assumptions, open questions, title
   candidates, audience promise, length target, voice, privacy status, and
   source-confidence needs. Record `new-book` or `first-edition-plus`; when an
   earlier edition taught successfully, preserve its governing question,
   narrative spine, examples, and chapter jobs. Preserve the original word-count
   estimate and target history; never reduce scope after drafting to make an
   undersized result appear planned, and never add material merely to reach the
   estimate.

4. **Separate grounded research from voice analysis.** Plan
   `research/evidence-notes.md` and hash-bound `research/evidence-notes.json`
   before the outline. Every usable claim needs a stable ID, verified source,
   precise locator, uncertainty, and `traceable-only` status. The research phase
   does not decide the learning arc or draft prose.

   When the user names private books or audio as a writing reference, plan a
   private `research/voice-source-profile.md`. Capture high-level craft—opening
   move, evidence-to-example movement, plain-language mechanism, humor boundary,
   uncertainty, rhythm, practical landing, and visual-to-audio adaptations.
   Preserve craft features, not copied passages or pastiche. The eventual
   project-authored first section becomes the voice exemplar.

5. **Build the argument-level outline as a conversation.** Offer 2-3 plausible structures when
   the shape is still fuzzy. Once the direction settles, produce a chapter table
   with chapter purpose, core beats, source needs, and any planned figure or
   image moments. Add each chapter's prerequisites, knowledge delta, grounded
   example, and concepts with complete explanation paths. For a beginner
   road-book, enforce a six-to-ten outcome concept budget, two or three new core
   terms per chapter, problem before name, an audio working-memory budget,
   people/history and narrative anchors, varied real-world applications,
   analogy contracts, retrieval after a gap, and an optional-study layer for
   derivations and specialist terminology. Governed-final pauses for human
   road-book approval before pilot synthesis; unattended-first-listen records
   editorial authorization and continues. Record the
   selected pattern, why it fits the learner and subject, and the approval
   evidence. Every planned section records its job, argument, specific
   evidence-note claim IDs, throughline advance, narrative or metaphor payoff,
   intellectual or emotional landing beat, and what it must not repeat. Obtain a
   human checkpoint on this argument-level outline and preserve it through
   handoff unless the user changes it.

6. **Gather and plan pictures deliberately.** Use pictures as teaching assets,
   evidence, examples, diagrams, mood references, or cover references. Track each
   image in `visuals/manifest.md` with file path, intended use, alt text,
   caption, source/provenance, license/permission status, and whether it is safe
   for public distribution. Found web images are references unless their license
   clearly allows inclusion. Prefer user-owned, generated, public-domain,
   permissively licensed, or self-created images for packaged books.

7. **Prepare the synthesis handoff.** When governed-final approval exists, or
   when unattended-first-listen editorial acceptance passes, write
   `handoff/handoff-packet.md` using `references/handoff-packet.md`. Include the
   final brief, outline, throughlines, source plan, figure plan, asset paths, and
   unresolved choices. Include the desired humanizing level, voice sample or
   style notes, AI-writing patterns to avoid, and the instruction to preserve
   facts, citations, technical names, and intentional teaching repetition. The
   packet must name listener-requested and author-anticipated pronunciation
   risks for `research/pronunciation-plan.json`; include every spoken variant
   that needs to be heard before full narration.
   Add a narrated-pilot plan for `research/comprehension-pilot.json`: 10 to 15
   minutes containing the opening and first technical passage, followed by one
   lightweight `continue` or `revise` decision against the exact audio hash and
   optional listener notes. Do not require comprehension questions. The packet can
   authorize pilot production, but never full canonical drafting before the
   listener accepts the first section as `research/voice-exemplar.md` and
   records `verdict: continue`. This lightweight verdict preserves human comprehension
   authority without turning listening into homework.
   Define the later production loop explicitly: draft section by section with
   the full outline, grounded evidence, voice exemplar, previous-section text or
   running summary, section job, and must-not-repeat list. Require
   `research/revision-passes.json` with separate single-job
   claim-traceability, tightening, de-listification, sentence-rhythm, and
   rendered ear-pass lanes.
   Preserve these decisions so the handoff is complete enough that a fresh agent can run
   `custom-learning-audiobook` without re-litigating the concept.

   If listening mode, revision mode, opening orientation, prior knowledge,
   target history, grounded evidence artifact, argument-level section jobs,
   concept budget, chapter prerequisites, knowledge deltas,
   working-memory limits, problem-before-name evidence, teaching beats,
   throughlines, explanation paths, blind sequential review instructions,
   voice-source profile, voice-exemplar checkpoint, section forward-context
   inputs, revision-pass plan, narrated pilot plan, or approval evidence are missing, label the packet a
   **development draft**. It cannot start pilot or canonical production.

8. **Invoke the audiobook skill for production.** Hand the packet to
   `custom-learning-audiobook` for research finalization, manuscript writing,
   cover generation, EPUB/Markdown building, Echo M4B/alignment rendering, QC,
   and delivery. This skill may draft sample passages or chapter beats, but it
   should not own the final manuscript build unless the user explicitly asks.
   Governed-final retains human outline, first-section, and comprehension gates.
   Unattended-first-listen follows the shared editorial checkpoints, completes a
   private first-listen package, and keeps human comprehension pending.

## Picture Rules

- Do not copy random copyrighted web images into public packages.
- Do not use private, client, workplace, or personally sensitive images in public
  books without explicit permission.
- For every included picture, provide meaningful alt text and a caption.
- Prefer a small number of purposeful figures over decorative image stuffing.
- If a picture is only a visual reference for cover art or generated diagrams,
  label it as a reference and keep it out of the final package unless permitted.

## Completion Criteria

The book-development phase is complete when these exist and the user approves
them, or explicitly asks to proceed without another gate:

- working title or title candidates,
- final brief and audience promise,
- learner prior knowledge and opening orientation,
- road-book or focused-study listening context, including driving and delivering
  mail when road-book is selected,
- revision mode and first-edition-plus preservation evidence when applicable,
- original target plus approved target history,
- grounded `evidence-notes.json` plan with traceable-only claim IDs,
- bounded voice-source profile when private exemplars were named,
- six-to-ten durable outcomes and per-chapter concept/working-memory budgets,
- listener pronunciation risks for `pronunciation-plan.json`,
- argument-level chapter and section outline with learning arc, prerequisites,
  knowledge delta, teaching beats, grounded examples, specific claims,
  throughline advance, payoff, landing beat, and must-not-repeat constraints,
- complete core-concept explanation paths,
- problem-before-name, real-world application, analogy, and retrieval plans,
- narrated-pilot design for `comprehension-pilot.json`, with full drafting still
  blocked until human outline approval, first-section voice-exemplar acceptance,
  and human listening acceptance,
- section-by-section forward-context contract and a final
  `revision-passes.json` plan of separate single-job passes including ear-pass,
- source/research plan,
- figure/image plan with provenance,
- handoff packet ready for `custom-learning-audiobook`.

The handoff also records whether the bounded `humanizer` pass is required,
optional, or explicitly skipped, plus any voice constraints the production
author must preserve.
For audiobook production, the de-Claudification gate is required even when a
general humanizer pass is optional: drafting prevention, whole-manuscript family
density review, accepted/rejected decisions, and a final hash-bound receipt.
