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
- Read `../../skill/references/learning-design.md` before shaping the curriculum
  or declaring a handoff production-ready.
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

2. **Clarify in small batches.** Ask no more than 2-3 questions at a time.
   Favor useful prompts over interrogation: audience, outcome, tone, what to
   include or avoid, source material, privacy, and whether the final product is a
   book, audiobook, illustrated EPUB, or all of those.
   Establish actual prior knowledge, the outcome the listener wants, and the
   opening orientation: context, promise, and route through the subject.

3. **Maintain the evolving brief.** After each meaningful turn, update the
   working brief with confirmed decisions, assumptions, open questions, title
   candidates, audience promise, length target, voice, privacy status, and
   source-confidence needs. Preserve the original target and a target history;
   never reduce scope after drafting to make an undersized result appear planned.

4. **Build the outline as a conversation.** Offer 2-3 plausible structures when
   the shape is still fuzzy. Once the direction settles, produce a chapter table
   with chapter purpose, core beats, source needs, and any planned figure or
   image moments. Add each chapter's prerequisites, knowledge delta, grounded
   example, and concepts with complete explanation paths. Get outline approval
   before final synthesis unless the user explicitly asks for an autonomous run.
   Record the selected pattern, why it fits the learner and subject, and the
   approval evidence. Preserve it through handoff unless the user changes it.

5. **Gather and plan pictures deliberately.** Use pictures as teaching assets,
   evidence, examples, diagrams, mood references, or cover references. Track each
   image in `visuals/manifest.md` with file path, intended use, alt text,
   caption, source/provenance, license/permission status, and whether it is safe
   for public distribution. Found web images are references unless their license
   clearly allows inclusion. Prefer user-owned, generated, public-domain,
   permissively licensed, or self-created images for packaged books.

6. **Prepare the synthesis handoff.** When the user approves the direction, write
   `handoff/handoff-packet.md` using `references/handoff-packet.md`. Include the
   final brief, outline, throughlines, source plan, figure plan, asset paths, and
   unresolved choices. Include the desired humanizing level, voice sample or
   style notes, AI-writing patterns to avoid, and the instruction to preserve
   facts, citations, technical names, and intentional teaching repetition. The
   packet must name listener-requested and author-anticipated pronunciation
   risks for `research/pronunciation-plan.json`; include every spoken variant
   that needs to be heard before full narration.
   Preserve these decisions so the handoff is complete enough that a fresh agent can run
   `custom-learning-audiobook` without re-litigating the concept.

   If opening orientation, prior knowledge, target history, chapter
   prerequisites, knowledge deltas, teaching beats, throughlines, explanation
   paths, or approval evidence are missing, label the packet a **development
   draft**. It cannot start canonical production.

7. **Invoke the audiobook skill for production.** Hand the packet to
   `custom-learning-audiobook` for research finalization, manuscript writing,
   cover generation, EPUB/Markdown building, Echo M4B/alignment rendering, QC,
   and delivery. This skill may draft sample passages or chapter beats, but it
   should not own the final manuscript build unless the user explicitly asks.

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
- original target plus approved target history,
- listener pronunciation risks for `pronunciation-plan.json`,
- chapter outline with learning arc, prerequisites, knowledge delta, teaching
  beats, and grounded examples,
- complete core-concept explanation paths,
- source/research plan,
- figure/image plan with provenance,
- handoff packet ready for `custom-learning-audiobook`.

The handoff also records whether the bounded `humanizer` pass is required,
optional, or explicitly skipped, plus any voice constraints the production
author must preserve.
For audiobook production, the de-Claudification gate is required even when a
general humanizer pass is optional: drafting prevention, whole-manuscript family
density review, accepted/rejected decisions, and a final hash-bound receipt.
