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
  Y`, and miniature reversals used only to make a sentence sound polished;
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

After the humanizer and frontier-author repair, create
`research/humanizer-decisions.json` with the reviewer, model, skill version,
`humanizer_applied: true`, accepted and rejected finding lists, and the factual,
coverage-ledger, narration, and prose checks rerun. Then produce the hash-bound
receipt:

```bash
python3 skill/scripts/prose_qc.py \
  --chapters-dir "$RUN_ROOT/chapters" \
  --out "$RUN_ROOT/research/prose-qc-after.md" \
  --fail-on-style \
  --decisions "$RUN_ROOT/research/humanizer-decisions.json" \
  --style-receipt-out "$RUN_ROOT/research/prose-style-receipt.json"
```

Pass that receipt to `build_book.py --prose-receipt`. Packaging verifies the
chapter hashes before writing EPUB or combined Markdown output, so a later edit
cannot inherit an earlier draft's prose approval.

## Human Judgment

This contract is not a ban on voice, rhythm, emphasis, or second person. It is a
ban on substituting familiar rhetorical gestures for explanation. Preserve a
specific voice sample the listener likes, along with their AI-writing patterns to
avoid, but do not invent personality or flatten every sentence into the same
minimal cadence.
