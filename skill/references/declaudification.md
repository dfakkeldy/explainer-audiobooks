# De-Claudification Contract for Audiobook Prose

This file is the **QC-time density review** — read it when checking a
finished draft, not while writing one. `voice-design.md` is the drafting-time
instruction: freeze its control panel and required project sample sentences
before the first section, and hand it to the lead author with the fact pack.

Run this contract once as an independent inventory before the humanizer, and
again during final editorial review. A post-draft cleanup alone is not enough:
a four-hour audiobook can become irritating through accumulated habits even
when every individual sentence is grammatical and defensible.

## Drafting Rule

State the fact directly. Do not manage the listener's reaction to it unless the
listener must perform a real exercise or thought experiment. In ordinary
explanation, remove reader-management instructions such as telling the listener
to hold, carry, keep, notice, pause over, sit with, stay with, resist, or let an
idea land. Explain why the idea matters instead of commanding attention.

Epistemic honesty appears through precise claims, stated evidence, named
uncertainty, and clear boundaries. Do not repeatedly announce the narrator's
honesty as a substitute for doing that work.

Avoid these phrase families:

- reader-management imperatives: `hold on to this`, `sit with that`, `carry it
  forward`, `keep this close`, `pause on that`, `notice what happened`, `let
  that land`, and synonym-cycled variants;
- author interventions and throat-clearing: repeated `let me`, `I want you to`,
  `I need you to`, `here is the thing`, and `here is what matters`;
- announced transitions: `one more thing`, `which brings us`, `before we move
  on`, and chapter endings that advertise the next chapter instead of ending;
- reflexive contrast frames: repeated `not X but Y`, `not because X but because
  Y`, the single-clause pivot `is not X — it is Y` (`The history is not just
  colourful background — it is a map`), and miniature reversals used only to
  make a sentence sound polished;
- intensifier tics: `genuinely`, `precisely`, `quietly`, `remarkably`, and
  nearby discourse adverbs used to manufacture sincerity or weight the claim
  has not earned. Each has legitimate literal uses (`precisely calibrated`,
  `quietly closed the door`); the tic is the free-floating intensity marker
  (`genuinely surprising`, `quietly radical`);
- fragment drumbeats: consecutive clipped sentences deployed as manufactured
  emphasis — `Not once. Not ever.` — and matched sets like `No waste. No
  guessing. No restarts.` A single short sentence after a long one is
  deliberate emphasis and is welcome; fragments arriving in formation are the
  tell;
- honesty announcement language: repeated `honestly`, `the honest answer`, `to
  be honest`, `if I'm being honest`, `in all honesty`, `the honest truth`,
  `let's be honest`, `truth be told`, `to tell you the truth`, `frankly`,
  `candidly`, and nearby variants. Put the qualification or uncertainty in the
  claim itself;
- faux gravity: `the heart of`, `the whole point`, `the real magic`, universal
  superlatives, moralizing symmetry, and tidy three-part conclusions that add no
  information.

The exact phrases named as disliked by the listener are a hard failure. The
broader phrase family is a density review: an occasional necessary transition
can survive, but synonym cycling does not evade the gate.

Fixed AI-vocabulary lists age by model generation — the `delve`/`tapestry` era
markers are already extinct in this pipeline, and the residual tics it actually
produces (`genuinely`, `precisely`, `quietly`) appear on no generic list. So the
named intensifier words are a starting inventory, not the check itself. The
durable check is per-book: list the manuscript's own most-repeated discourse
adverbs and evaluative words from the repeated-phrases report, and treat any
word doing sincerity work in every chapter as a candidate family.

## Better Repairs

- Delete the instruction and state the consequence.
- Replace an abstract importance claim with the mechanism, example, or boundary
  that makes it important.
- Replace `Let me explain inference` with `Inference is what happens when...`.
- Replace `Notice that the weights did not change` with `The weights did not
  change.`
- Replace `The honest answer is that researchers do not know` with `Researchers
  do not know.` Add the evidence boundary or competing interpretations when they
  matter.
- Replace `Honestly, this result is uncertain` with the precise uncertainty:
  `The result comes from one small study and has not yet been replicated.`
- Delete the free-floating intensifier and state what earns the intensity:
  replace `The result is genuinely surprising` with the expectation the result
  broke. If nothing earns it, the adverb was doing all the work.
- Fold a fragment run back into one sentence and keep at most one clipped
  sentence where the emphasis is real. `Not once. Not ever.` becomes `Not once
  across ninety-six runs.` The shape-metrics block of the prose report lists
  every run of consecutive short sentences for this review.
- Keep an imperative only when the listener must actually picture, calculate,
  compare, recall, or do something for the lesson to work.
- Let paragraphs end when their explanatory job is complete. Do not add a
  polished moral, slogan, or teaser merely to create a landing.

## Two-Level Gate

Run the prose checker once before the humanizer as an independent inventory,
then again after accepted repairs. Review chapter by chapter and across the
whole manuscript. The whole-manuscript pass catches synonym cycling that is
invisible when each chapter is judged alone.

```bash
python3 skill/scripts/prose_qc.py \
  --chapters-dir "$RUN_ROOT/chapters" \
  --out "$RUN_ROOT/research/prose-qc-before.md" \
  --fail-on-style
```

Hard-banned language makes the command fail immediately. Other families use a
per-10,000-word density budget. Treat every match as a candidate, not an
automatic deletion; the frontier author records accepted and rejected findings
and gives a reason for any rejected hard-looking case.

After the humanizer and frontier-author repair, rerun factual, narration, and
prose checks. Review accepted and rejected findings and the reason for each
decision, then run the final whole-manuscript gate:

```bash
python3 skill/scripts/prose_qc.py \
  --chapters-dir "$RUN_ROOT/chapters" \
  --out "$RUN_ROOT/research/prose-qc-after.md" \
  --fail-on-style
```

## Human Judgment

This contract is not a ban on voice, rhythm, emphasis, or second person. It is a
ban on substituting familiar rhetorical gestures for explanation. Preserve a
specific voice sample the listener likes, along with their AI-writing patterns to
avoid, but do not invent personality or flatten every sentence into the same
minimal cadence.
