# The Question Machine: New Learning Edition — Design

Date: 2026-07-14  
Status: Approved in conversation  
Privacy: Private first-listen production; the specification is public-safe

## Purpose

Create a new manuscript of *The Question Machine* that genuinely teaches neural
networks and modern language models to a curious beginner. This is neither a
repair of the rejected second edition nor another narration of it. The new book
must supply orientation, a coherent learning progression, worked explanations,
retrieval and application, independent learning review, and separate prose and
audio acceptance.

The reader-facing edition label is **New Learning Edition**. Internal artifacts
use a fresh non-destructive edition identifier so the first edition, rejected
second edition, and its exact-text rerenders remain traceable and untouched.

## Approved listener profile and constraints

- The listener has no assumed machine-learning or programming background.
- Mathematics uses small worked examples based on arithmetic. Gradients and
  backpropagation are explained conceptually without requiring calculus.
- The manuscript contains no code listings and assumes no Python knowledge.
- The narrated target is 40,000–45,000 words. This target is fixed before
  drafting and may not be reduced after drafting begins without explicit user
  approval and evidence in the learning brief.
- The book is private. The accepted package is copied to the user's iCloud Books
  folder for a private first listen; it is not published to the public library.

## Learning promise

The opening supplies context before terminology: neural networks power familiar
systems, but common explanations skip from “learns from data” to transformers
without showing what changes during learning or what happens when a trained
model is used.

After finishing, the listener should be able to:

1. Explain what a neural network is in operational terms.
2. Follow a forward pass through a small network.
3. Distinguish parameters from hyperparameters.
4. Explain training, loss, gradients, backpropagation, and optimization.
5. Define inference and distinguish it from training and from a forward pass.
6. Explain tokens, embeddings, attention, transformers, and next-token
   generation.
7. Separate a model from the assistant product and surrounding software.
8. Explain the roles of fine-tuning, retrieval, tools, context, external memory,
   and agents.
9. Evaluate claims about intelligence, understanding, hallucination,
   consciousness, and risk without treating the machinery as magic.

## Curriculum approach

Use a mechanism-first spiral. Establish a small, stable mental model and revisit
it at increasing scale instead of presenting a terminology inventory.

Three throughlines hold the course together:

1. A tiny email-urgency network supplies the arithmetic and general
   neural-network concepts.
2. A tiny next-token model shows how those concepts become language modeling.
3. Every major stage asks: **What is fixed, what is changing, and where does the
   result come from?** This keeps training, inference, context, external memory,
   and product behavior distinct.

## Chapter progression and word allocation

The allocations are planning ranges, not identical containers. Their midpoint
totals approximately 44,300 narrated words.

### Part I — How a network learns

1. **Why Neural Networks Exist** — 1,900–2,500 words. Establish the problem,
   context, promise, route, and meaning of learning without a terminology dump.
2. **A Network You Can Calculate** — 3,100–3,700 words. Inputs, weights, bias,
   activation, neurons, layers, parameters, and a complete forward pass.
3. **An Answer, an Error, and a Loss** — 2,900–3,500 words. Examples, labels,
   predictions, loss functions, and the objective of training.
4. **Sending the Error Backward** — 3,500–4,100 words. Slopes and gradients
   without calculus prerequisites, conceptual chain rule, backpropagation,
   optimizers, and learning rates.
5. **Learning Without Memorizing** — 2,700–3,300 words. Datasets, batches,
   epochs, validation, overfitting, generalization, regularization, and
   hyperparameters.
6. **Inference: Using What Training Built** — 2,500–3,100 words. Frozen
   parameters, checkpoints, preprocessing, postprocessing, latency, throughput,
   batching, quantization, and inference versus a forward pass.

### Part II — From numbers to language

7. **How Language Becomes Numbers** — 2,900–3,500 words. Tokens,
   vocabularies, tokenization, vectors, embeddings, dimensions, similarity, and
   hidden states.
8. **Attention: Choosing Relevant Context** — 3,500–4,100 words. Queries, keys,
   values, scores, softmax, heads, masks, and a small worked attention example.
9. **Inside a Transformer Block** — 3,300–3,900 words. Residual stream,
   attention, feed-forward networks, normalization, stacked blocks, and context
   windows.
10. **Training a Language Model** — 2,700–3,300 words. Next-token prediction,
    pretraining data, objectives, compute, checkpoints, scaling, and what
    parameters absorb.
11. **How a Language Model Produces an Answer** — 2,700–3,300 words. Logits,
    probabilities, sampling, temperature, autoregression, KV caching, and
    repeated inference.

### Part III — From model to product

12. **How a Base Model Becomes an Assistant** — 3,000–3,600 words.
    Instruction tuning, preference training, system prompts, retrieval, RAG,
    tools, external memory, and agents.
13. **What the Result Means—and When It Fails** — 3,200–3,800 words.
    Evaluation, calibration, hallucination, distribution shift, contamination,
    interpretability, and model behavior versus product behavior.
14. **What the Machinery Does Not Settle** — 2,200–2,800 words. A compact,
    technically grounded treatment of understanding, consciousness, agency,
    moral status, and risk.

A non-narrated sources appendix follows the fourteen chapters.

## Teaching contract

Every core concept completes an explanation path:

- a plain definition;
- the problem it solves;
- its mechanism at the required depth;
- a concrete case;
- a useful boundary or explicit reason a boundary is not applicable;
- a likely misconception;
- an expected listener ability;
- deliberate chapter uses that introduce, retrieve, deepen, apply, compare, or
  correct the concept.

Teaching beats vary by chapter. Available jobs include worked arithmetic,
comparison, tracing one input through a system, prediction, misconception repair,
retrieval, and applying an earlier model at greater depth. The outline must not
turn these into a repeated chapter template.

Audio-first rules:

- Establish the need for a term before naming it.
- Keep numerical examples small enough to follow without a page.
- Restate relevant numbers before using them.
- Avoid long symbol sequences, tables that must be seen, and code listings.
- Use imperatives only for genuine recall, prediction, comparison, or thought
  experiments.
- End by integrating the new mental model, not with motivational prose,
  announced profundity, or a tidy rhetorical flourish.
- Treat the listener's named Claude-style phrases and their rhetorical families
  as hard bans.

## Research and authorship

Use deep research. Prior fact packs are leads, not automatically accepted
evidence. Verify manuscript claims against current primary sources, including
foundational papers, official technical documentation, and strong research
literature. Date changing claims and retain meaningful uncertainty.

One frontier author owns the approved outline, explanation choices, sequential
canonical Markdown chapters, and all substantive revisions. Research and review
workers may prepare cited evidence, uncertainty lists, diagnostics, and
production records; they do not write replacement chapters.

Maintain the fail-closed records during development rather than reconstructing
them afterward:

- `learning-brief.json`
- `learning-outline.json`
- `chapter-plans.json`
- `coverage-ledger.json`
- `continuity.json`
- `learning-review.json`

## Review and acceptance

Two independent learning lanes review the substantively revised manuscript:

1. **Structure:** orientation, progression, prerequisites, chapter purposes,
   throughlines, callbacks, and resolved promises.
2. **Beginner reader:** unexplained terms, conceptual leaps, shallow mechanisms,
   absent examples, misleading analogies, misconceptions, boundaries, and the
   plausibility of expected listener abilities.

The frontier author resolves accepted findings. A bounded humanizer and
de-Claudification pass occurs only after structural repairs. It may alter voice
locally but cannot certify teaching quality or replace the learning architecture.
After every accepted voice edit, rerun both learning reviews and the prose gate
against the final chapter hashes.

Packaging requires separate passing learning and prose receipts bound to the
same canonical Markdown hashes. Factual, prose, learning, cover, packaging, and
acoustic verdicts remain independent.

## Cover and edition identity

Keep the established title and amber series identity while developing exactly
three genuinely different coordinated portrait/square cover directions. At
least one direction should be bright or high-key. The user explicitly selects a
pair or requests a mix before the paired selection receipt and EPUB build exist.
The cover review does not overlap manuscript acceptance.

## Narration and pronunciation

Use governed native Echo/Kokoro narration with `am_michael` as the first voice.
Before full synthesis, render and inspect a technical-term pronunciation reel.
The mandatory probe matrix includes singular and plural forms where relevant,
especially:

- `hyperparameter` and `hyperparameters`;
- `inference`;
- `gradient` and `gradients`;
- `backpropagation`;
- `logit` and `logits`;
- `softmax`;
- `autoregression` and `autoregressive`;
- `quantization`.

Record exact approved Echo/source revisions and pronunciation decisions. Repair
recurring pronunciation inputs before the full render; do not patch an audited
M4B afterward. Human acoustic acceptance remains pending until the reel or
matching final passages are actually heard.

## Packaging and private delivery

After final learning and prose acceptance:

1. Bind the selected portrait/square cover pair.
2. Build EPUB and combined Markdown with both hash-bound receipts.
3. Render the governed Echo M4B and alignment sidecar.
4. Verify the pronunciation audit, render receipt, cover binding, EPUB,
   alignment JSON, M4B duration, and hashes.
5. Create a manifest stating which gates passed, failed, or remain pending.
6. Keep production artifacts out of the public repository and public KB.
7. Copy the verified private package to the user's iCloud Books folder for the
   approved first-listen delivery.

## Failure conditions

Stop and return to development if any of these occurs:

- the opening teaches details before context, promise, and route;
- a chapter becomes a terminology inventory;
- a core concept lacks any explanation-path component;
- continuity records are created retroactively;
- the word target is reduced to match an undersized draft;
- a style, factual, packaging, or audio result is offered as proof that the book
  teaches;
- learning or prose reviews refer to hashes other than the packaged chapters;
- a recurring technical pronunciation is known to be wrong before full render;
- private artifacts are proposed for the public repo or public KB.

## Completion criteria

The edition is complete only when the final manuscript is within the approved
40,000–45,000-word range; both learning reviewers pass the final hashes; the
prose and de-Claudification receipt passes those same hashes; a user-selected
cover pair is bound; Echo pronunciation, render, media, alignment, and cover
verification pass; and the private iCloud destination copy matches the governed
package. Human first-listen acceptance is reported separately and is never
inferred from automated QC.
