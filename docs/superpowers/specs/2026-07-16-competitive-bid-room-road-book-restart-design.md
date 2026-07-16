# The Competitive Bid Room Road-Book Restart Design

Date: 2026-07-16

## Decision

Restart *The Competitive Bid Room* as a new public-safe learning audiobook under
the current road-book, evidence-traceability, comprehension-pilot, revision, and
paired-cover contracts.

This specification supersedes the production direction in
`2026-07-15-competitive-bid-room-audiobook-design.md` and its implementation
plan. The earlier files and ignored build remain historical evidence; they are
not accepted learning architecture, manuscript, cover, or receipt inputs for the
restart. The earlier manuscript was never accepted through a narrated human
pilot, so this run uses `revisionMode.name: new-book`, not
`first-edition-plus`.

## Publication Identity

- Title: *The Competitive Bid Room*
- Subtitle: *Automating Heavy-Civil Tenders Without Automating Judgment*
- Public slug: `the-competitive-bid-room`
- Author metadata: `Dan Fakkeldy`
- Format: public-safe custom learning audiobook
- Listening mode: `road-book`
- Primary listening context: driving and delivery work, with eyes unavailable
  and attention shared with safe work
- Estimated length: 18,000 to 22,000 words, approximately two hours at 1.25x
- Preferred narrator: native Echo/Kokoro `am_michael`
- Echo fallback narrator: `am_puck`
- Research mode: deep public research
- Source-confidence label: deep
- Interior figures: none in the main production unless later research identifies
  a genuine learning need and rights-safe provenance

The internal edition and run identifiers must distinguish this restart from the
2026-07-15 ignored build. Public-facing title and slug remain unchanged unless a
later publication collision requires an explicit supersession decision.

## Audience

The listener already works with mid-sized heavy-civil and public-infrastructure
tenders. They understand drawings, specifications, addenda, quantity sheets,
bid security, supplier and subcontractor quotes, estimate spreadsheets,
deadlines, approvals, and electronic submission. Likely roles include estimator,
bid coordinator, project manager, and operations leader at a small-to-mid-sized
Atlantic Canadian contractor.

The listener is not treated as a beginner in tendering. The learning gap is how
to design an automation system that improves visibility, completeness, speed,
and learning while keeping confidential information, commercial judgment,
communications, price approval, and submission under named human authority.

The book begins inside the bid room. It contains no introduction to artificial
intelligence, generic prompting tutorial, product catalogue, or spoken technical
derivation.

## Governing Question

> How can a bid room use automation to see more, miss less, and make better
> decisions without surrendering commercial judgment?

The book answers that question by following one fictional tender from arrival
through post-bid learning. The tender develops rather than resetting between
chapters, so each automation capability appears only when a real workflow need
creates the reason for it.

## Learner Outcomes

After one forward-moving listen, the listener should be able to:

1. Describe a bid as one changing decision system rather than a folder of files.
2. Separate deterministic automation, probabilistic assistance, and human
   authority.
3. Specify the minimum contents of a traceable living bid record.
4. Turn tender sources into cited obligations, scope, assumptions, and
   unresolved questions without mistaking extraction for compliance.
5. Connect quantities, estimate logic, quotes, exclusions, and changes without
   automating final price ownership.
6. Explain why confidential data, untrusted documents, broad tool permissions,
   and outbound authority require separate controls.
7. Design a human-controlled closing, price-lock, and submission ritual.
8. Select a narrow ninety-day automation pilot with one primary success measure
   and explicit guardrails.

The learning records may express these as six to eight durable outcomes where
schema constraints reward consolidation, but they must preserve every ability
above.

## Curriculum Pattern

Use `end-to-end-trace`.

Reason: the listener needs to follow one tender state from discovery through
qualification, document control, estimating, quote coverage, change, closing,
submission, and learning. Each later capability modifies or verifies the same
bid, making dependencies and authority boundaries audible without a terminology
syllabus.

The rejected primary alternatives are:

- `problem-progression`: vivid but liable to become a catalogue of failures;
  selected failures remain chapter-level teaching devices.
- a ninety-day transformation narrative: useful for the conclusion but too
  narrow to teach the full tender lifecycle.

## Narrative Spine and Fiction Boundary

The worked case is an independently invented Atlantic bridge replacement and
approach-roadworks tender with earthworks, aggregate, drainage, structural
concrete, traffic control, environmental obligations, specialty subcontract
work, bid security, and electronic submission.

Its complications include:

- a buried mandatory requirement;
- a revised quantity;
- an addendum that changes an environmental obligation;
- an RFI answer that clarifies responsibility;
- incomplete quote coverage;
- a deceptively low subcontractor quote with a material exclusion;
- a late quote or controlled allowance change;
- a fixed electronic-submission deadline.

The fictional team is defined by roles: lead estimator, bid coordinator,
operations reviewer, and authorized submitter. The prose may give them restrained
fictional characterization only where it improves continuity or exposes a
decision. It must not encode or disguise any real contractor, employee, owner,
client, supplier, project, project number, date, location, price, production
rate, crew, internal form, or private anecdote.

## Teaching Infrastructure

The road-book must use history, people, applications, and failures as learning
infrastructure rather than decoration.

Two historical or institutional anchors are required:

1. The move from physical plan rooms, paper sets, and manual addendum circulation
   to electronic procurement and submission. The point is not nostalgia; it
   establishes why version identity and current state became harder, not easier.
2. The development of public award information, bidder debriefing, and
   estimate-versus-actual learning as ways to prevent every tender from becoming
   an isolated event.

Real-world applications must vary beyond the fictional tender. Suitable public
examples include procurement discovery, electronic submission controls,
privacy/data minimization, untrusted-document handling, access separation,
debriefing, and award-data limitations. No invented toy example may become the
book's only evidence that a mechanism matters.

Analogies are optional. When used, each must identify the relationship it
explains, at least two correspondences, and where it stops matching. Operational
examples are preferred when they can carry the explanation directly.

## Throughlines

Use these four throughlines only when they perform a named learning job:

1. **One changing bid state:** every source, requirement, assumption, quote,
   change, decision, and approval belongs to one traceable bid identity.
2. **Automation prepares; people authorize:** software may collect, compare,
   calculate, flag, draft, and explain, but named people own commitments,
   assumptions, price, and submission.
3. **Evidence before confidence:** consequential outputs point to their sources,
   and uncertainty remains visible.
4. **Every bid improves the next:** outcomes, debriefing, actuals, and decision
   quality become reusable evidence rather than forgotten history.

Every recurrence must retrieve, deepen, apply, compare, or correct an idea.
Bare restatement is not a throughline use.

## Chapter Architecture

Chapter lengths are estimates rather than quotas. Each chapter introduces no
more than two or three genuinely new core terms, gives the listener-visible
problem before the name, and finishes when its promised knowledge delta is
complete.

### Chapter 1: The Clock Starts — opening scene and reframing

The fictional tender arrives. Establish the deadline, document state, competing
demands, authority boundaries, governing question, and book route. Define
competitiveness as selection, completeness, decision speed, defensible pricing,
and learning rather than simply the lowest number.

Knowledge delta: the listener can describe the bid room as a changing decision
system.

### Chapter 2: From Plan Room to Living Bid — history and system construction

Use the first historical anchor, then construct the living bid record: identity,
current sources, versions, owners, deadlines, assumptions, decisions,
permissions, unresolved items, and audit history.

Knowledge delta: the listener can specify the minimum state every later
automation must read or update.

### Chapter 3: The Bid You Should Not Chase — decision comparison

Build a repeatable qualification packet around capability, geography, capacity,
schedule, risk, commercial fit, and strategic value. Automation prepares
evidence; people own the pursuit decision. Historical results inform questions
but do not become an automatic rejection rule.

Knowledge delta: the listener can distinguish consistent preparation from
automated bid/no-bid authority.

### Chapter 4: Turn Documents into Obligations — guided walkthrough

Convert specifications, drawings, forms, bonding requirements, insurance,
questions, deadlines, addenda, and submission rules into a cited obligation map.
Use the buried requirement and revised source to show why extraction is evidence
gathering, not proof of compliance.

Knowledge delta: the listener can design an obligation and compliance workflow
that preserves source, version, owner, state, and verification.

### Chapter 5: An Estimate That Can Explain Itself — mechanism

Connect quantities, assemblies, productivity assumptions, labour, equipment,
material, indirects, escalation, risk, and contingency to sources and owners.
Separate deterministic arithmetic from probabilistic extraction and
interpretation. Keep unresolved assumptions audible without turning the chapter
into a spoken spreadsheet.

Knowledge delta: the listener can place assistance around an estimate while
preserving calculation integrity and commercial ownership.

### Chapter 6: The Quote That Wasn't Cheap — failure analysis

Use the materially excluded low quote to teach request preparation, coverage,
normalization, inclusions, exclusions, approved follow-ups, late changes, and
discrepancy reporting. No message is sent and no supplier is selected without
human approval.

Knowledge delta: the listener can design quote automation that improves
comparability without creating accidental commitments.

### Chapter 7: Give the Machine Less Authority — threat and boundary analysis

Cover data classification, minimization, retention, untrusted tender documents,
prompt injection, least privilege, audit, vendor boundaries, and outbound tool
authority. A system allowed to read broadly must not automatically gain broad
sending, editing, or submission power.

Knowledge delta: the listener can outline a safe authority architecture and the
questions to answer before confidential bid data enters an AI service.

### Chapter 8: Closing the Bid — adversarial review

Red-team scope, assumptions, quote coverage, addenda, forms, bonds, arithmetic,
schedule, resource constraints, portal readiness, approvals, price lock, and
submission state. Automated checks report evidence and exceptions; they do not
declare the bid safe.

Knowledge delta: the listener can design a human-controlled closing and
submission ritual.

### Chapter 9: The Bid After the Bid — consequence and application

Use the second historical/institutional anchor. Connect public award
information, debriefing, estimate-versus-actual results, supplier behaviour,
risk outcomes, reusable assemblies, and decision quality. End with a narrow
ninety-day pilot, baseline, one primary measure, guardrails, and stop conditions.

Knowledge delta: the listener can choose a bounded pilot that improves the bid
room without attempting an autonomous estimating system.

## Optional Reference Layer

The main listen must stand alone. Put material requiring visual persistence,
backtracking, specialist catalogues, or implementation syntax into a
non-narrated appendix or separate study artifact. Candidate items include:

- a sample living-bid field map;
- an obligation/compliance matrix schema;
- a quote comparison and exclusion checklist;
- a change/discrepancy report schema;
- a closing authority matrix;
- a ninety-day pilot scorecard;
- current official source links and jurisdiction caveats.

These are reference aids, not proof that the audiobook taught the concepts.

## Evidence Contract

Research precedes outlining. Create `evidence-notes.md` and a hash-bound
schema-v2 `evidence-notes.json` with `claimPolicy: traceable-only`. Each usable
claim requires a stable ID, supported wording, official source, precise locator,
retrieval date, verification status, and uncertainty or conflict note.

The source shelf should begin with current primary material from:

- Nova Scotia procurement and electronic tendering guidance;
- CanadaBuys opportunity and supplier guidance;
- public construction-contract, debriefing, and award-information guidance;
- the Office of the Privacy Commissioner of Canada;
- the Canadian Centre for Cyber Security;
- a second authoritative cybersecurity source only where Canadian material
  does not adequately explain untrusted-document authority separation.

Research workers may extract and reconcile evidence. They may not choose the
curriculum or write manuscript prose. A claim absent from the accepted evidence
notes is unavailable to the outline and author. Jurisdiction-specific legal,
engineering, bonding, insurance, portal, and commercial details remain bounded
and educational rather than advisory.

## Voice Contract

The voice is an experienced peer reasoning through a live tender: direct,
concrete, restrained, and slightly wry. It assumes ordinary bid-room vocabulary
and explains only the automation or governance meaning that is new.

The prose must:

- be written for one forward-moving listen;
- use second person naturally without managing the listener's reaction;
- favour scenes, decisions, mechanisms, and consequences over lists;
- avoid consultant language, product hype, motivational emphasis, artificial
  suspense, repeated recaps, and reflexive `not X but Y` constructions;
- preserve exact names such as addendum, RFI, bid bond, CanadaBuys, source of
  truth, least privilege, and prompt injection when the listener needs the real
  vocabulary;
- keep calculations below the road-book working-memory limits and move visual
  chains to the reference layer;
- give every chapter a distinct job, opening move, and natural final beat.

No private external book is required as a voice source. The project-authored
first section becomes the concrete `voice-exemplar.md` after human acceptance.

## Human Approval Gates

### Gate 1: argument-level outline

After grounded evidence exists, produce schema-v2 `learning-outline.json`,
`chapter-plans.json`, and `coverage-ledger.json`. Every planned section records
its job, argument, specific evidence IDs, throughline advance, payoff, landing
beat, and must-not-repeat list. Dan approves that progression before pilot prose.

### Gate 2: first-section teaching and voice

Draft only the first section using the accepted evidence and outline. Revise it
until Dan accepts its teaching and voice. Preserve the accepted project prose as
`research/voice-exemplar.md`. Do not draft the rest of the book.

### Gate 3: narrated learning pilot

Build a nonpackage pilot with a mandatory `-pilot` slug. It contains 10 to 15
representative minutes, including the opening and first technical passage, no
more than three durable terms, at least two applications or consequences, and
one retrieval in a fresh situation.

Render it through `scripts/echo_learning_pilot_narrate.sh` with native Echo. Dan
hears the exact hash-bound audio and returns one lightweight verdict:
`continue` or `revise`. Notes are optional; no questionnaire or written
explanation is required. Record the verdict, audio hash, listening context, and
evidence in `comprehension-pilot.json` before full drafting.

A `revise` verdict returns to the first section, pilot material, or outline as
the evidence requires. An autonomous-run request, valid receipt, or agent review
cannot waive or override this gate.

## Canonical Drafting and Continuity

After a `continue` pilot verdict, one frontier lead author drafts every
substantive passage section by section in listening order. No parallel chapter
authors and no whole-book generation are allowed.

Before every section call, `continuity.json.draftContexts` supplies:

- the full approved argument outline;
- relevant evidence IDs and fact pack;
- applicable coverage-ledger rows;
- accepted voice exemplar;
- previous section text or a faithful running summary;
- the current section's single job;
- its must-not-repeat list.

After each section and chapter, continuity records terms defined, examples and
analogies used, deliberate callbacks, active promises, unresolved questions,
retrievals, listener load, prior-section summary, and do-not-repeat constraints.
Markdown under `chapters/` is canonical. EPUB, M4B, and combined Markdown are
downstream renderings only.

## Review and Revision

Review jobs remain independent:

1. claim traceability;
2. structure and progression;
3. blind manuscript-only sequential review at the actual audience level:
   experienced bidder, new to automation architecture and AI governance;
4. tightening;
5. de-listification;
6. sentence rhythm;
7. rendered ear-pass;
8. bounded humanizer and de-Claudification pass.

Reviewers cite exact locations, listener cost, and repair type. They do not
supply replacement chapters. The frontier author accepts, rejects, or repairs
every substantive finding. Local findings produce local repairs rather than
regeneration.

After accepted voice edits, rerun structure and blind sequential review on the
final chapter hashes. `learning-design-receipt.json` and
`prose-style-receipt.json` must bind the same canonical hashes. The learning
receipt proves the required process and accepted pilot, not learning transfer;
later negative listening evidence overrides it.

## Pronunciation Contract

Create `pronunciation-plan.json` before narration. Include every relevant spoken
variant discovered in the ledger and manuscript. Likely risks include:

- addendum and addenda;
- Ariba if current evidence makes it relevant;
- CanadaBuys;
- e-bond and e-bonding;
- RFI and RFIs;
- RFQ and RFQs;
- deterministic and probabilistic;
- discrepancy and discrepancies;
- prompt injection.

Terms begin pending. A governed partial probe and pronunciation reel provide
hash-bound human listening evidence before full narration. Do not waive
pronunciation review.

## Cover Contract

Cover work starts fresh after the manuscript direction is stable. Create exactly
three complete, rights-safe, generated-raster art-and-type directions. Each must
have a different metaphor, composition, palette, material language, title
strategy, and coordinated portrait/square treatment. Include one credible
bright/high-key direction.

Render each pair through the schema-v2 paired-cover tools at 1600 by 2560 for
EPUB and 2400 by 2400 for M4B, plus 160-pixel thumbnails and receipts. Inspect
every full-size render and thumbnail. Dan chooses one pair or requests a
specific mix. Do not create `cover-selection.json`, build the governed EPUB, or
start full narration before explicit selection and final manuscript acceptance.

The earlier three covers are not accepted candidates for this restart. A later
direction may independently recover a useful physical metaphor only if it is
re-derived from the new evidence and argument and presented as a new candidate.

## Packaging and Delivery

After final manuscript, learning, prose, pronunciation, and cover gates pass:

1. create the paired cover-selection receipt;
2. build the EPUB and combined Markdown with the hash-bound learning and prose
   receipts;
3. render native Echo/Kokoro audio through the governed wrapper using
   `am_michael`, with `am_puck` only as the Echo fallback;
4. verify the selected portrait cover in EPUB and square cover in M4B;
5. verify the render-success receipt, pronunciation audit, M4B duration,
   alignment JSON, sidecar, and EPUB structure;
6. dry-run and then apply governed delivery sync;
7. copy the verified public-safe package to iCloud Books;
8. prepare the governed public `books/the-competitive-bid-room/` package and
   collection metadata without publishing raw research or scratch artifacts.

The final package contains the combined Markdown, EPUB, M4B, alignment sidecar,
selected covers and receipts, pronunciation evidence, source appendix, and a
concise public-safe README. Delivery is incomplete until the actual destination
copy matches the verified source artifacts.

## Public and Private Boundary

The finished book may be public. The following remain outside public book
folders and public KB content:

- raw research captures and drafting scratch;
- generated databases, chapter captures, caches, and partial renders;
- private company, client, supplier, employee, or project information;
- real pricing, quantities, productivity rates, internal forms, or workflows;
- reviewer chain-of-thought or private source passages;
- any artifact whose rights or provenance is unclear.

The KB may receive a narrow operational receipt after durable milestones, but
not raw manuscript research or private material.

## Success Criteria

The restart succeeds only when:

- current official evidence is traceable through stable claim IDs;
- Dan approves the argument-level outline;
- Dan accepts the first-section teaching and voice;
- the exact narrated pilot receives `continue` before full drafting;
- one frontier author writes the canonical manuscript section by section;
- every chapter stays within the road-book concept and working-memory budgets;
- structure, blind sequential, revision, ear, humanizer, and prose gates pass on
  the final chapter hashes;
- Dan explicitly chooses one of exactly three new coordinated cover pairs or an
  approved requested mix;
- pronunciation evidence, EPUB, M4B, alignment, cover, render, and delivery
  receipts verify;
- the iCloud Books copy exists and matches the governed artifacts;
- any public repository package contains only approved public-safe outputs.

Technical receipts do not overrule a negative listening verdict at any stage.

