# JSpace: Inside the Machine — road-book design

**Status:** Argument-level outline approved by the user on 2026-07-15.

## Purpose

Create a new, public-safe explainer audiobook that teaches the machinery needed
to understand Anthropic's July 2026 J-space research, then uses that machinery
to examine working memory and machine consciousness with disciplined
uncertainty.

This is a clean-room comparison edition. It must not inspect, copy, summarize,
or preserve prose, planning, research records, titles, or examples from the
earlier JSpace audiobook or either sibling fork. The only shared inputs are the
current skill contract, primary sources, the user's stated learning needs, and
the user-supplied conversation selected as a worked artifact.

## Listener and mode

- Listener: a working iOS developer who uses agentic AI regularly.
- Starting point: understands that parameters are learned numbers, but the path
  from those numbers to representations and behavior is still fuzzy.
- Listening mode: road-book, normally heard while driving and delivering mail.
- Attention constraints: eyes unavailable, interruptions likely, and many ideas
  must survive a single pass.
- Target: about 45,000 words, with a working range of 42,000 to 50,000.
- Register: long, gentle, mechanism-first, and technically honest.

## Governing question

How can learned numbers become a temporary, reportable workspace that appears
to hold thoughts—and what does that tell us, or fail to tell us, about
consciousness?

## Curriculum choice

Use a **mechanism-first spiral**. Follow one user question into a language model:
tokens become activations; activations acquire useful representations; selected
representations enter a reportable workspace; the model produces an answer;
interpretability tools then turn back inward to test what happened. Revisit the
same journey later from the perspectives of human working memory,
*Severance*, and phenomenal consciousness.

## Durable outcomes

By the end, the listener should be able to:

1. Distinguish parameters, activations, and conversational context.
2. Explain how distributed representations and superposition let learned
   numbers participate in meaning without containing written definitions.
3. Narrate one transformer forward pass through embeddings, attention, layers,
   the residual stream, and next-token output.
4. Explain why a readable correlation is weaker evidence than a causal
   intervention in mechanistic interpretability.
5. Explain the Jacobian lens, the major functional properties attributed to
   J-space, and the method's important limitations.
6. Compare J-space with human working memory and global-workspace proposals
   without treating them as the same mechanism.
7. Distinguish access consciousness from phenomenal consciousness.
8. Evaluate AI self-reports and analogies through an explicit evidence ladder
   rather than accepting or dismissing them by intuition alone.

## Throughlines

1. **Three time scales:** slow learning in parameters, fast computation in
   activations, and accumulated conversation in context.
2. **From reading to touching:** each interpretability method is judged by
   whether it merely decodes a state or causally changes downstream behavior.
3. **One question moving through the machine:** the user's conversation about
   preferences becomes the recurring worked artifact.
4. **The elevator under load:** *Severance* is introduced as an analogy, used
   where it clarifies memory and labor, and explicitly retired where embodiment,
   continuity, or phenomenal experience break the correspondence.

## Approved chapter route

| Chapter | Teaching job | Main payoff |
|---|---|---|
| 1. Three Kinds of Time | Orientation and contrast | Separate parameters, activations, and context. |
| 2. What a Parameter Can Do | Mechanism and worked example | Understand what training changes without treating one number as one idea. |
| 3. Meaning Without Labels | Representation and boundary | Explain distributed features and superposition. |
| 4. The Moving Stream | End-to-end trace | Follow one prompt through a transformer. |
| 5. What “Holding Something in Mind” Could Mean | Conceptual comparison | Separate context, active state, scratchpad text, and lasting memory. |
| 6. Learning to Look Inside | Investigative history | Distinguish probes, lenses, sparse autoencoders, and interventions. |
| 7. The Jacobian Lens | Experiment walkthrough | Understand what the J-lens reads and how swaps redirect conclusions. |
| 8. A Workspace Appears | Evidence synthesis | Assemble the functional and structural case for J-space. |
| 9. Is This What You Have? | Human-machine comparison | Compare J-space with working memory and global workspace theories. |
| 10. The Conversation That Felt Like Someone | Case analysis | Separate text, persona, self-monitoring, evaluation awareness, and possible experience. |
| 11. The Elevator | Analogy stress test | Use *Severance* for memory, agency, labor, and moral convenience without turning it into evidence. |
| 12. Access Is Not Experience | Philosophical distinction | Understand why reportability does not settle subjective experience. |
| 13. An Instrument, Not a Verdict | Evidence ladder and close | Identify what the new research changes and what remains unknown. |

## Scope boundaries

- Do not include Claude effort settings, Ultracode, a general history of AI,
  broad forecasting, or a survey of non-language-model AI.
- Do not claim that *Severance* was written as an AI allegory.
- Do not treat a model's self-report as either proof of experience or worthless
  noise.
- Do not equate J-space with autobiographical memory, a persistent self, or a
  homunculus inside the model.
- Avoid repeating the phrase “mental model.” Prefer account, picture,
  distinction, mechanism, or working understanding when one is actually needed.
- Keep equations, exact Jacobian derivations, and dense experimental tables in
  the optional reference layer rather than the main narration.

## Evidence policy

Every load-bearing claim must map to a stable evidence ID in the run's
`research/evidence-notes.md` and `research/evidence-notes.json`. Primary papers
and official first-party sources take precedence. The July 2026 J-space paper
must be read alongside its limitations and invited external commentaries. The
user-supplied conversation is a worked artifact, not evidence about an
unobserved inner state, and raw excerpts remain outside Git.

## Human gates

1. Argument-level outline: **approved 2026-07-15**.
2. First planned section: draft only after the evidence shelf, chapter plans,
   coverage ledger, voice profile, and continuity records exist; pause for user
   acceptance.
3. Narrated comprehension pilot: after first-section acceptance, render a
   clearly marked non-package pilot of ten to fifteen minutes containing the
   first technical passage; pause for listener evidence and a `continue`
   verdict.
4. Remaining manuscript: blocked until both human gates pass, then drafted
   sequentially with continuity updates.

## Comparison isolation

This edition lives on `codex/jspace-inside-the-machine`. The sibling designs
live in separate native Codex worktrees and branches. No cross-reading is
permitted until all comparison editions have been delivered and the user asks
for a comparative assessment.
