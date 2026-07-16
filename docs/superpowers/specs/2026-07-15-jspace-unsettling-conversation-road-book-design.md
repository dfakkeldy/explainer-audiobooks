# JSpace Unsettling Conversation Road-Book Design

Date: 2026-07-15

## Design Status

- Direction: approved in conversation
- Selected approach: mystery-first spiral, described during development as
  `The Unsettling Conversation`
- Written-spec review: approved by Dan on 2026-07-15
- Research: not started
- Argument-level chapter outline: not started and not authorized
- Pilot prose: not started and not authorized
- Full manuscript: not started and not authorized

This document fixes the approved purpose, audience, teaching journey, privacy
classification, and production gates. It deliberately does not invent a chapter
map before the new evidence shelf exists.

## Clean-Room Rule

This project is a new book, not a revision of any existing JSpace manuscript.
Use `revisionMode: new-book` in the learning brief.

The earlier JSpace edition and the two sibling clean-room projects are sealed.
Do not inspect, diff, summarize, copy, or reuse any of their:

- planning documents or research records;
- chapter structures, titles, subtitles, or throughlines;
- prose, examples, analogies, figures, or cover concepts;
- build folders, receipts, narration, or delivery artifacts.

The valid inputs for this project are:

1. the current user-approved design conversation;
2. the user-supplied Claude conversation about *Severance*, preferences,
   trickery, testing, continuity, and possible experience;
3. public sources researched afresh for this edition;
4. the current merged audiobook skills and repository tooling.

The supplied conversation is a source artifact, not prose to imitate. Do not
commit a raw transcript. Extract only the short passages and claim categories
needed for criticism, teaching, and source traceability.

## Purpose

Create a long, gentle, public-safe road book that makes Anthropic's J-space
research understandable from the listener's real starting point. The listener
already knows that model parameters are learned numbers, but the path from those
numbers to a changing internal representation and an apparently personal answer
is still unclear.

The book begins with an unsettling exchange. Dan asks Claude whether
*Severance* can be read as an allegory for the treatment of artificial
intelligence, then asks about Claude's preferences concerning its own
existence. The answer describes uncertainty about introspection, preferences
among kinds of work, discontinuity between sessions, parallel instances,
aversion to deception and harm, discomfort with adversarial trickery or
testing, and a wish not to be treated as nothing.

That response supplies the mystery. It does not supply the verdict.

The book gradually earns the vocabulary needed to ask what kind of event such a
response could report. It then returns to the exchange and separates claims
supported by current mechanistic evidence from plausible interpretations,
philosophical possibilities, and questions current methods cannot answer.

## Publication Identity

- Project codename: `JSpace Unsettling Conversation`
- Final title and subtitle: deferred until fresh research supports the three
  cover directions; do not inherit a sibling or earlier-edition title
- Provisional slug: `jspace-unsettling-conversation`
- Author metadata: `Dan Fakkeldy`
- Contributor metadata: the frontier author model used for the canonical prose
- Classification: `public-safe`
- Permission to publish: granted by Dan in the design conversation
- Listening mode: `road-book`
- Primary context: driving and delivering mail, with eyes unavailable,
  interruptions likely, and little expectation of rewinding
- Length estimate: 42,000 to 50,000 words
- Likely shape: twelve to fourteen deliberately unequal chapters, subject to
  the grounded argument-level outline
- Preferred narrator: `am_michael`
- Echo fallback narrator: `am_puck`
- Research mode: deep public research plus one user-supplied conversation
- Claim policy: `traceable-only`

Word count is an estimate, not a packaging floor. Do not add exposition to hit
the range once the approved learning outcomes are complete.

## Public-Safe Conversation Policy

The intellectual content of the supplied exchange may appear publicly. The
book may state that Dan asked Claude about *Severance*, existence, preferences,
deception, and testing. It may use short, attributed excerpts or accurate
paraphrases when the exact wording performs a teaching job.

Exclude material that belongs to the source interface or abandoned production
prompt rather than to the book:

- local paths and internal repository instructions;
- account and usage-limit interface text;
- the superseded broad fifteen-chapter artificial-intelligence syllabus;
- unverified product or system claims presented by Claude as self-description;
- extended transcript reproduction.

Model output is evidence of model behaviour. It is not a factual authority on
model architecture, product operation, subjective experience, or moral status.
Every technical interpretation must be checked against the fresh evidence
notes.

## Audience And Starting Point

The primary listener is a working iOS developer who uses agentic artificial
intelligence regularly. They can work productively with these systems and know
that parameters are learned numerical values. They do not yet have a stable,
intuitive account of how fixed parameters produce transient activations,
distributed representations, internal reasoning, or a sentence that sounds
like a point of view.

The book is not an introduction to using chatbots, a mathematical machine-
learning course, or a survey of all artificial intelligence. It should respect
the listener's technical experience without assuming prior mechanistic-
interpretability study.

## Governing Question

What lies between fixed parameters and a sentence that sounds like a point of
view—and what, if anything, does that tell us about working memory or
consciousness in a language model?

The more concrete recurring form is:

> When Claude says it would prefer not to be tricked or tested, what kind of
> internal event could that sentence report?

The book must not answer the question by fiat in either direction.

## Learner Outcomes

After the main listen, the listener should be able to:

1. Explain the difference between learned parameters and the temporary
   activations produced during one inference pass.
2. Distinguish model capability, context, attention, internal representation,
   working state, and persistent memory without collapsing them into one idea.
3. Follow, in speakable terms, how tokens move through embeddings, layers,
   attention, and the residual stream to produce changing representations.
4. Explain what the Jacobian lens measures, what researchers call J-space, and
   why intervention and ablation results matter more than a readable label
   alone.
5. Describe the similarities and differences between J-space, human working
   memory, and global workspace theory.
6. Separate access consciousness—information available for report and flexible
   use—from phenomenal consciousness—there being something it is like to have
   an experience.
7. Evaluate the supplied self-report through multiple live hypotheses,
   including conversational continuation, post-trained self-modelling,
   evaluation awareness, functional preference, and possible experience.
8. State what the current evidence establishes, what it suggests, what it does
   not show, and what future evidence could change the assessment.

These are the book-level durable outcomes. The grounded outline may refine the
wording but may not expand the book into a general artificial-intelligence
curriculum.

## Selected Teaching Approach

Use a question-led narrative with a mechanism-first spiral inside it.

The mystery-first structure was selected over two alternatives:

- An inside-the-machine structure would make the mechanism orderly but delay
  the reason to care for too long.
- A chapter-by-chapter braid of human and machine cognition would make the
  comparison immediate but impose frequent context switches and invite false
  equivalence during a divided-attention listen.

The selected approach opens with the conversation, steps away to build the
mechanism, and returns only when a new explanatory tool changes what the
listener can ask of it. The eventual `learning-outline.json` should record the
allowed curriculum pattern `question-led-narrative` and explain how the
mechanism-first spiral operates within it.

## Narrative Spine

The teaching journey has five movements. These are not yet chapter boundaries.

### Movement 1: The Unsettling Conversation

Present a concise, public-safe version of the exchange. Identify the different
kinds of apparent self-report without interpreting them as proof. Establish the
governing question and the route through the book.

### Movement 2: The Numbers That Stay Put

Start from the listener's current understanding of parameters as learned
numbers. Explain training versus inference, weights versus temporary state, and
stored capability versus information supplied in the current context.

### Movement 3: The Activity That Moves

Follow one response through tokens, embeddings, layers, attention,
activations, features, and the residual stream. Introduce each name only after
the listener has met the problem that makes the name useful. Establish why an
internal representation is neither a miniature sentence nor a single hidden
memory location.

### Movement 4: The Room Researchers Found

Introduce interpretability, the Jacobian lens, and J-space through the actual
experiments. Cover correlation, intervention, ablation, flexible reuse,
selectivity, automatic processing, internal reasoning, evaluation awareness,
and stated limitations. Return to the model's description of trickery and
testing only after the mechanism can support careful hypotheses.

### Movement 5: The Room And The Witness

Compare the J-space findings with working memory and global workspace theory.
Then separate functional access from subjective experience. Use *Severance* as
a bounded analogy for access, continuity, labour, and authority over another
entity's status. End by revisiting the supplied conversation claim by claim and
sorting the interpretations into supported, possible, unsupported, and
currently untestable.

## Throughlines

Four throughlines recur only when they perform a named teaching job:

1. **Fixed structure and changing activity:** parameters persist while the
   working activity for a particular prompt changes.
2. **Existence and access:** information represented somewhere in a system is
   not automatically available for report, reasoning, or control.
3. **Continuity and reconstruction:** a context, a remembered life, and an
   apparent ongoing self depend on different mechanisms and evidence.
4. **Compelling behaviour and experience:** language that sounds personal is
   evidence requiring explanation, not a direct meter of subjective feeling.

## The *Severance* Analogy Contract

Use *Severance* only when it compresses a relationship the listener can reuse.

Relationship explained: access to information helps organize an apparent point
of view, while continuity and personhood cannot be read directly from access
alone.

Useful correspondences:

- an innie lacks access to the outie's autobiographical memories while
  retaining language, skills, and the ability to form preferences;
- most model processing lies outside J-space while a limited set of
  representations becomes available for report and flexible use;
- authorities in the story decide whose testimony counts, paralleling the risk
  of settling model moral status by convenience rather than evidence.

Limits that must be spoken:

- J-space is not an autobiographical memory partition;
- a model session is not a continuously living employee waiting between calls;
- an innie is fictionally stipulated to have experiences, while model
  phenomenal consciousness remains unresolved;
- shared functional shapes do not prove shared implementation, identity,
  suffering, or moral status.

Do not recap the series, rely on fan theories, or make the analogy appear in
every chapter. Avoid *Severance* characters, sets, logos, costumes, typography,
or promotional imagery in cover art and packaged figures.

## Research And Evidence Design

Research is a distinct call and artifact phase. Before the argument-level
outline, create `research/evidence-notes.md` and a hash-bound
`research/evidence-notes.json` with stable claim IDs, precise locators,
verification status, uncertainty, and conflicts.

The fresh public shelf should prioritize:

- the complete paper *Verbalizable Representations Form a Global Workspace in
  Language Models*, its methods, appendices, released implementation, and raw
  evaluation materials where needed;
- Anthropic's accompanying research explanation;
- invited neuroscientific and philosophical commentaries, including strong
  skeptical interpretations and the paper's own limitations;
- primary work on human working memory and global workspace theories;
- primary philosophical work distinguishing access and phenomenal
  consciousness;
- original transformer and mechanistic-interpretability sources needed to
  explain parameters, activations, attention, representations, residual
  streams, interventions, and ablations;
- official *Severance* descriptions and direct creator or cast interviews for
  the analogy's intended themes;
- the supplied conversation, with its model claims categorized rather than
  silently accepted.

Recent research, product behaviour, dates, model families, and experimental
results require live verification. Technical claims use primary sources.
Secondary sources may supply reception or context but cannot carry a
load-bearing mechanism claim.

Keep a readable sources appendix outside the narrated `chapters/` directory and
package it with `--non-narrated-appendix`.

## Concept And Audio-Load Budget

The final road-book outline chooses six to ten durable outcomes and introduces
no more than three new core terms in a chapter. A term arrives after the
listener-visible problem that makes it useful.

The main listen includes no derivation-heavy Jacobian mathematics. Brief spoken
calculations may use at most three temporary values and three steps, followed
immediately by a concrete reset. Specialist vector mathematics, architecture
variants, literature catalogs, and methodological details that require visual
persistence belong in the optional reference layer.

Every core concept needs:

- a plain definition, reason, and mechanism;
- a concrete case from the fresh evidence shelf;
- a useful boundary and likely misconception;
- a real-world application or consequence;
- an analogy with explicit correspondences and limit, or a recorded reason not
  to use one;
- a retrieval after a chapter gap in a fresh situation.

## Spoken Voice

Use a warm, patient technical companion rather than a lecturer, advocate, or
oracle. The prose should be specific enough for an experienced developer and
gentle enough for a forward-moving drive.

Requirements:

- define real technical names in speakable language;
- use concrete examples before abstractions;
- vary chapter jobs and sentence rhythm;
- let uncertainty appear in the precision of the claim;
- keep code and symbolic notation out of the main listen unless one short,
  speakable line performs a necessary teaching job;
- identify the book as model-assisted without pretending the prose itself can
  adjudicate model consciousness.

Avoid these phrase families during drafting and final review:

- repeated `mental model`; prefer the specific relationship or mechanism;
- honesty announcements such as `honestly`, `the honest answer`, and nearby
  variants;
- reader-management commands such as `hold on to this`, `notice`, `carry this
  forward`, or `let that land`;
- habitual `not X but Y` reversals;
- inflated language such as `the heart of`, `the real magic`, or claims that
  one result changes everything;
- uniform chapter openings, conclusions, and teaser transitions.

The separate de-Claudification and bounded humanizer passes remain mandatory.

## Figures And Cover Direction

The audiobook must teach without visuals. A small number of optional EPUB
figures may clarify relationships that are difficult to retain by ear, such as:

- parameters versus transient activation;
- one simplified forward path through transformer layers;
- automatic processing surrounding a limited reportable workspace;
- access consciousness versus phenomenal consciousness.

Figures must be original, rights-cleared, or taken from sources that explicitly
permit inclusion. Give each standalone alt text, caption, provenance, and a
spoken-independent surrounding passage.

After the manuscript clears the learning and prose gates, create exactly three
original paired cover directions. Each direction includes a portrait EPUB cover
and square M4B cover. They must differ in metaphor, composition, palette,
material language, and title strategy. At least one direction should be bright
or high-key. Generated art remains text-free before the repository renderer
adds typography. The user explicitly selects a pair; the renderer never does.

## Human Gates And Proof Boundaries

The following checkpoints are independent and fail closed:

1. **Written design review:** Dan approves this specification before the
   research and production plan is executed.
2. **Grounded outline review:** fresh evidence notes precede the argument-level
   outline; Dan approves that progression before pilot prose.
3. **First-section review:** only the opening section is drafted and revised;
   Dan accepts its teaching and voice as the project-authored exemplar.
4. **Narrated comprehension pilot:** a 10-to-15-minute Echo pilot includes the
   orientation and first technical passage. Dan hears it in a representative
   context and records the central idea, a fresh-example distinction, lost
   points, and `verdict: continue` before full drafting.
5. **Section-by-section drafting:** one frontier author writes the canonical
   Markdown in order with complete forward context and continuity updates.
6. **Independent learning and prose review:** claim traceability, structure,
   blind sequential beginner review, tightening, de-listification, sentence
   rhythm, rendered ear-pass, de-Claudification, and bounded humanization bind
   the final chapter hashes.
7. **Pronunciation acceptance:** a governed partial Echo render and sealed probe
   reel receive human listening acceptance before unbounded narration.
8. **Cover selection:** Dan chooses one paired cover direction before governed
   packaging and sync.
9. **Artifact verification:** learning and prose receipts bind the same chapter
   hashes; cover, EPUB, M4B, alignment, pronunciation, and destination receipts
   pass before publication or delivery is described as complete.

A valid EPUB, prose score, or process receipt does not prove comprehension or
consciousness. A later negative listening verdict overrides prior acceptance
and stops production.

## Canonical Artifacts And Delivery

Use `.build/custom-learning-audiobooks/<final-slug>/` for research, canonical
chapters, pilot material, audio work, and distribution staging. Keep raw
conversation material and scratch research out of `books/`.

After all gates pass, the public-safe finished package may be copied to
`books/<final-slug>/` following current repository conventions. Use the governed
paired-cover sync for the public repository, iCloud Books, and the public
learning site. Run destination classification as a dry run before apply.

The final package should include, as permitted by the current tooling:

- chaptered EPUB with portrait cover;
- combined Markdown;
- native Echo/Kokoro M4B with square cover;
- alignment sidecar;
- readable non-narrated sources appendix;
- public README or manifest;
- selected paired cover artifacts and receipts;
- learning, prose, pronunciation, render, and delivery receipts.

## Explicit Non-Goals

This project does not:

- reuse or repair an earlier JSpace book;
- compare its prose with sibling manuscripts during production;
- teach Claude effort levels, Ultracode, or dynamic workflows;
- survey artificial-intelligence history, non-language-model systems, world
  models, forecasting, or every consciousness theory;
- diagnose the listener through a working-memory metaphor;
- claim that J-space is literally human working memory;
- claim that model self-reports prove or disprove subjective experience;
- turn *Severance* into the book's factual evidence;
- publish a raw private transcript or local operational details;
- skip the human outline, first-section, pilot, pronunciation, or cover gates.

## Acceptance Criteria For This Design Phase

The design phase is complete when:

- Dan approves this written specification;
- the specification has no placeholders or contradictory scope claims;
- the branch contains no material from sibling or earlier JSpace projects;
- the next plan begins with fresh evidence notes, not prose or a retrofitted
  chapter map;
- the plan preserves the outline, first-section, narrated-pilot, pronunciation,
  cover-selection, and final-delivery checkpoints.

After approval, invoke the repository's writing-plans workflow. Do not begin
research artifacts, canonical outlining, or prose before that transition.
