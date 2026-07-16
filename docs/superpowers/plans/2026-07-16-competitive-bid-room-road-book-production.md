# The Competitive Bid Room Road-Book Production Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Subagent-driven execution is permitted only after Dan explicitly authorizes delegation. One frontier lead author must own the argument-level outline, every substantive canonical passage, and every substantive repair.

**Goal:** Research, author, narrate, verify, and publicly deliver a new road-book edition of *The Competitive Bid Room* that teaches experienced heavy-civil tender workers how to automate the bid room without automating commercial judgment.

**Architecture:** Use fail-closed artifact handoffs: fresh traceable evidence, human-approved argument outline, accepted first-section voice exemplar, hash-bound native Echo pilot, sequential frontier-authored manuscript, independent learning and prose review, explicit paired-cover selection, governed Echo narration, and destination verification. Canonical development records remain in an ignored run root in the fresh restart worktree; only the selected, verified public-safe package moves into `books/` and iCloud Books.

**Tech Stack:** Markdown; schema-v2 JSON learning records; live official web research; Python QC and packaging tools under `skill/scripts/`; original generated raster cover art plus paired-cover specifications; native Echo/Kokoro narration through the governed custom-learning wrappers; Git, GitHub, and iCloud Drive.

**Approved design:** `docs/superpowers/specs/2026-07-16-competitive-bid-room-road-book-restart-design.md`

## Global Constraints

- Public title: *The Competitive Bid Room*.
- Subtitle: *Automating Heavy-Civil Tenders Without Automating Judgment*.
- Canonical public and wrapper slug: `the-competitive-bid-room`.
- Edition ID: `the-competitive-bid-room-road-book-restart-2026-07-16`.
- Classification: `public-safe`; publication permission is granted.
- Revision mode: `new-book`. The earlier ignored run remains untouched and supplies no accepted prose, learning records, receipts, or cover candidates.
- Audience: experienced heavy-civil/public-infrastructure bid-room worker who is new to automation architecture and AI governance, not new to tendering.
- Listening mode: `road-book`, normally driving and delivery work with eyes unavailable, interruptions likely, and little rewinding.
- Estimated length: 18,000–22,000 words. Word count is a planning estimate, not a packaging floor; never pad a complete learning path.
- Curriculum pattern: `end-to-end-trace` through one independently invented Atlantic bridge-and-roadworks tender.
- Main listen: no AI primer, prompting tutorial, product catalogue, spoken spreadsheet, specialist schema recital, or implementation syntax.
- Introduce no more than three new core terms in any chapter. A brief spoken calculation carries no more than three temporary values and three symbolic steps before a concrete reset.
- Every factual manuscript claim must be traceable to a stable ID in the hash-bound fresh evidence notes.
- One frontier lead author owns the outline, canonical Markdown, and every substantive repair. Reviewers report citation-first findings and do not replace prose.
- Do not spawn subagents unless Dan explicitly authorizes delegation. If independent review cannot be isolated under the available authority, pause at that gate rather than self-certifying it.
- Preferred narrator is `am_michael`; the only automatic fallback is Echo/Kokoro `am_puck` when the preferred Echo voice is unavailable. Never silently substitute a system voice.
- Full drafting stops until Dan approves the argument-level outline, accepts the first-section teaching and voice, and returns `continue` against the exact native Echo pilot audio hash.
- The final package requires exactly three new coordinated portrait/square cover candidates and Dan's explicit selection or requested mix.
- Keep private/workplace/customer details, real pricing, production rates, internal forms, raw research captures, databases, partial renders, and unclear-rights assets out of Git, the public book package, and the KB.
- A valid receipt never substitutes for human listening. A later negative verdict stops production even when technical gates pass.

## Canonical Paths And Responsibilities

```text
RUN_ROOT=.build/custom-learning-audiobooks/the-competitive-bid-room

$RUN_ROOT/research/brief.md
  Public-safe scope, fiction boundary, metadata, gates, and status.
$RUN_ROOT/research/learning-brief.json
  Schema-v2 listener, road-book, new-book, and word-estimate record.
$RUN_ROOT/research/sources.md
  Live source inventory with retrieval dates, classes, and chapter use.
$RUN_ROOT/research/evidence-notes.md
$RUN_ROOT/research/evidence-notes.json
  Stable EV-NNN claims, precise locators, conflicts, limits, and SHA binding.
$RUN_ROOT/research/sources-appendix.md
  Readable non-narrated public bibliography for the EPUB.
$RUN_ROOT/research/voice-source-profile.md
  Project-brief craft profile; no pastiche or private source excerpts.
$RUN_ROOT/research/outline.md
$RUN_ROOT/research/learning-outline.json
$RUN_ROOT/research/chapter-plans.json
$RUN_ROOT/research/coverage-ledger.md
$RUN_ROOT/research/coverage-ledger.json
  Human-approved nine-chapter argument progression and learning paths.
$RUN_ROOT/research/fact-packs/chNN.md
  Chapter-specific claim IDs, exact terms, boundaries, and fictional beats.
$RUN_ROOT/research/continuity.md
$RUN_ROOT/research/continuity.json
  One forward draft context per section and one checkpoint per chapter.
$RUN_ROOT/research/voice-exemplar.md
  Dan-accepted project-authored first section.
$RUN_ROOT/research/comprehension-pilot.json
  Exact native Echo pilot hash and Dan's lightweight verdict.
$RUN_ROOT/research/pronunciation-plan.json
$RUN_ROOT/research/pronunciation-plan-receipt.json
  Planned and human-accepted spoken terms and variants.
$RUN_ROOT/research/revision-passes.json
$RUN_ROOT/research/learning-review.json
$RUN_ROOT/research/humanizer-decisions.json
$RUN_ROOT/research/prose-style-receipt.json
$RUN_ROOT/research/learning-design-receipt.json
  Final-hash review, revision, voice, and packaging gates.
$RUN_ROOT/pilot/
  Explicitly nonpackage 10–15-minute pilot and governed pilot evidence.
$RUN_ROOT/chapters/ch01.md ... ch09.md
  Canonical sequential frontier-authored manuscript.
$RUN_ROOT/dist/candidate-{1,2,3}/
  Three new coordinated portrait/square cover candidates and receipts.
$RUN_ROOT/dist/
  Governed EPUB, combined Markdown, Echo outputs, manifest, and selection receipt.
books/the-competitive-bid-room/
  Verified public-safe repository package created only after every gate passes.
```

At the start of every execution task, rehydrate paths explicitly:

```bash
export EXPLAINER_ROOT=$(git rev-parse --show-toplevel)
export SLUG=the-competitive-bid-room
export EDITION_ID=the-competitive-bid-room-road-book-restart-2026-07-16
export TITLE="The Competitive Bid Room"
export SUBTITLE="Automating Heavy-Civil Tenders Without Automating Judgment"
export CONTRIBUTOR="GPT-5 Codex"
export RUN_ROOT="$EXPLAINER_ROOT/.build/custom-learning-audiobooks/$SLUG"
export RESEARCH="$RUN_ROOT/research"
export CHAPTERS="$RUN_ROOT/chapters"
export DIST="$RUN_ROOT/dist"
```

---

### Task 1: Initialize The Fresh Canonical Run

**Files:**
- Create: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/brief.md`
- Create: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/learning-brief.json`
- Create from templates: remaining schema-v2 research starters under `.build/custom-learning-audiobooks/the-competitive-bid-room/research/`

**Interfaces:**
- Consumes: merged approved restart design and current `skill/templates/learning-design/` files.
- Produces: canonical ignored run root and immutable listener/publication constraints for every later task.

- [ ] **Step 1: Start the execution branch from merged `main`**

Run:

```bash
git fetch origin main
git switch -c codex/competitive-bid-room-road-book origin/main
git status --short --branch
```

Expected: a clean named branch based on the commit containing the approved design and plan. If the execution branch already exists, resume its existing worktree instead of resetting or recreating it.

- [ ] **Step 2: Prove the new run is isolated from the older worktree**

Run:

```bash
export SLUG=the-competitive-bid-room
export RUN_ROOT="$PWD/.build/custom-learning-audiobooks/$SLUG"
test "$PWD" = "/Users/dfakkeldy/.codex/worktrees/competitive-bid-room-restart/explainer-audiobooks"
git check-ignore -v "$RUN_ROOT/research/learning-brief.json"
test ! -e "$RUN_ROOT" || {
  printf 'Restart run already exists; inspect and resume rather than overwrite: %s\n' "$RUN_ROOT" >&2
  exit 1
}
```

Expected: `.build/` is ignored and the restart worktree has no pre-existing run. Never delete or modify the earlier run under `/Users/dfakkeldy/.codex/worktrees/competitive-bid-room/explainer-audiobooks/`.

- [ ] **Step 3: Create the canonical directory structure and copy schema starters**

Run:

```bash
export RESEARCH="$RUN_ROOT/research"
mkdir -p "$RESEARCH/fact-packs" "$RESEARCH/draft-inputs" \
  "$RUN_ROOT/pilot/chapters" "$RUN_ROOT/pilot/dist" \
  "$RUN_ROOT/chapters" "$RUN_ROOT/dist"
for file in skill/templates/learning-design/*; do
  cp "$file" "$RESEARCH/$(basename "$file")"
done
```

Expected: every current template exists under `research/`; none is treated as completed evidence.

- [ ] **Step 4: Replace the example learning brief with the approved record**

Use `apply_patch` so `learning-brief.json` is exactly:

```json
{
  "schemaVersion": 2,
  "learnerOutcome": "Map one heavy-civil tender as a changing decision system, place deterministic automation, probabilistic assistance, and human authority correctly, and choose a measurable ninety-day bid-room pilot.",
  "priorKnowledge": "Experienced heavy-civil and public-infrastructure bid-room worker familiar with tender documents, drawings, specifications, addenda, bid security, quote coverage, estimates, approvals, closing deadlines, and electronic submission; not assumed to know automation architecture or AI governance.",
  "audienceLevel": "experienced practitioner adjacent to automation",
  "listeningMode": {
    "name": "road-book",
    "primaryContext": "Driving and delivery work",
    "attentionConstraints": [
      "eyes unavailable",
      "single-pass listening",
      "real interruptions",
      "little expectation of rewinding"
    ]
  },
  "revisionMode": {
    "name": "new-book",
    "sourceEdition": "",
    "preserve": {
      "governingQuestion": "",
      "narrativeSpine": "",
      "successfulExamples": [],
      "chapterJobs": []
    }
  },
  "openingOrientation": {
    "context": "A fictional Atlantic bridge-and-roadworks tender arrives with a fixed deadline, a changing document set, and competing demands on estimator attention.",
    "promise": "Show how automation can reduce omissions and decision latency without owning commitments, assumptions, final price, or submission.",
    "route": "Follow one tender through qualification, document obligations, estimating, quote coverage, authority and security, closing, submission, and post-bid learning."
  },
  "originalTargetWords": 20000,
  "currentTargetWords": 20000,
  "estimatedMinimumWords": 18000,
  "estimatedMaximumWords": 22000,
  "draftingStarted": false,
  "scopeHistory": [
    {
      "date": "2026-07-16",
      "change": "Approved from-scratch road-book restart with an end-to-end tender trace.",
      "approvalStatus": "approved",
      "approvalSource": "Dan Fakkeldy conversation and approved restart specification"
    }
  ]
}
```

- [ ] **Step 5: Write the readable brief and project craft profile**

Use `apply_patch` to record in `brief.md`: title, subtitle, slug, edition ID, author/contributor, public-safe classification, publication permission, no-figures default, preferred/fallback narrator, nine approved chapter jobs, fictional-tender elements, prohibited real/private material, traceable-only claim policy, and all three human gates.

Replace `voice-source-profile.md` with these explicit craft decisions: open inside the active tender; make the operational problem felt before naming the automation concept; move from source evidence to a concrete decision; use experienced-peer second person, restrained dry humor, precise uncertainty, varied rhythm, and practical landings; avoid consultant language, motivational emphasis, artificial suspense, repeated recaps, reflexive contrast frames, and pastiche.

Compute its SHA and patch `comprehension-pilot.json.humanCheckpoints.voiceSource` to `mode: project-brief`, path `research/voice-source-profile.md`, the exact SHA, boundary `craft-features-not-pastiche`, and `rawSourceExcerptsCommitted: false`.

- [ ] **Step 6: Validate the initialized contract**

Run:

```bash
python3 -m json.tool "$RESEARCH/learning-brief.json" >/dev/null
jq -e '.schemaVersion == 2 and .revisionMode.name == "new-book" and .listeningMode.name == "road-book" and .originalTargetWords == 20000 and .estimatedMinimumWords == 18000 and .estimatedMaximumWords == 22000 and .draftingStarted == false' "$RESEARCH/learning-brief.json"
VOICE_SHA=$(shasum -a 256 "$RESEARCH/voice-source-profile.md" | awk '{print $1}')
jq -e --arg sha "$VOICE_SHA" '.humanCheckpoints.voiceSource.profileSHA256 == $sha and .humanCheckpoints.voiceSource.rawSourceExcerptsCommitted == false' "$RESEARCH/comprehension-pilot.json"
rg -n -i 'real customer|real contractor|real supplier|private estimate|real project number|private workflow' "$RESEARCH" && exit 1 || true
git status --short
```

Expected: JSON and SHA checks pass, the sensitive-name scan has no hits, and ignored run artifacts do not appear in Git status.

### Task 2: Build The Fresh Official Evidence Shelf

**Files:**
- Create: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/sources.md`
- Replace: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/evidence-notes.md`
- Replace: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/evidence-notes.json`
- Create: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/sources-appendix.md`
- Create: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/research-audit.md`

**Interfaces:**
- Consumes: approved design and live official public sources; consumes no earlier run research record.
- Produces: stable `EV-NNN` claims and a SHA-bound `traceable-only` evidence contract used by the outline and manuscript.

- [ ] **Step 1: Verify each source lane live as a separate research call**

Browse the primary pages and downloadable guidance directly. Record publisher, exact title, URL, retrieval date, source class, precise locator strategy, freshness risk, and proposed chapter use for:

1. Nova Scotia Procurement overview and current tender-opportunity workflow.
2. Current Nova Scotia electronic bidding guidance and Supplier's Guide to eBidding.
3. Current Nova Scotia construction contract guidance.
4. Nova Scotia bidder debriefing protocol.
5. Nova Scotia public award/open-tender data and its limitations.
6. CanadaBuys tender opportunities and current supplier guidance.
7. Office of the Privacy Commissioner of Canada generative-AI principles and business guidance.
8. Canadian Centre for Cyber Security guidance on AI security, access, data, and untrusted inputs.
9. UK NCSC prompt-injection guidance only if the Canadian source does not adequately explain why untrusted documents must be separated from tool authority.

Expected: current official sources replace remembered URLs or claims. News posts, vendor marketing, and generic AI summaries are not evidence authorities.

- [ ] **Step 2: Write stable claim records before curriculum decisions**

For each usable claim, add an `EV-NNN` section to `evidence-notes.md` with supported wording, source, precise page/section/table locator, verification date, confidence, jurisdiction/freshness boundary, conflict status, and allowed manuscript wording. Cover at minimum: opportunity discovery, electronic submission, document/addendum control, bid security, questions and deadlines, debriefing, award-data limits, privacy necessity/proportionality, accountability, data minimization, auditability, least privilege, prompt injection, and human authorization.

Do not write chapter prose in this task.

- [ ] **Step 3: Design the fictional tender without borrowing real details**

Add a clearly marked fictional-case section to `evidence-notes.md` that fixes only these teaching facts:

- Atlantic municipal bridge replacement plus approach roadworks.
- Earthworks, aggregate, drainage, structural concrete, traffic control, environmental controls, specialty subcontract work, bid security, and electronic submission.
- One buried mandatory requirement.
- One addendum revises a quantity and environmental obligation.
- One RFI answer clarifies responsibility.
- One low quote excludes a material scope item.
- One late quote or allowance change requires a discrepancy report.
- No real location, owner, contractor, supplier, employee, project number, date, price, crew, quantity, production rate, internal form, or anecdote is reused.

Label every fictional fact `illustrative`, not `verified`.

- [ ] **Step 4: Bind the evidence JSON**

Set `evidence-notes.json` to schema version 2, `notesPath: research/evidence-notes.md`, `claimPolicy: traceable-only`, one record for every `EV-NNN`, and an explicit `unresolvedConflicts` array. Compute the Markdown SHA-256 and set `notesSHA256` to the digest.

Run:

```bash
NOTES_SHA=$(shasum -a 256 "$RESEARCH/evidence-notes.md" | awk '{print $1}')
python3 -m json.tool "$RESEARCH/evidence-notes.json" >/dev/null
jq -e --arg sha "$NOTES_SHA" '.schemaVersion == 2 and .claimPolicy == "traceable-only" and .notesPath == "research/evidence-notes.md" and .notesSHA256 == $sha and (.claims | length) >= 24' "$RESEARCH/evidence-notes.json"
```

Expected: at least 24 bounded, precisely located claims exist; unresolved conflicts are retained rather than averaged away.

- [ ] **Step 5: Write the public source appendix and research audit**

Write `sources-appendix.md` with `# Sources`, a public-safety/method note, retrieval date, and sources grouped by Chapters 1–9. Write `research-audit.md` with official-source coverage, exact conflicts, time-sensitive claims, jurisdiction limits, excluded unsupported claims, and confirmation that no earlier run record supplied evidence.

- [ ] **Step 6: Verify the evidence boundary**

Run:

```bash
rg -n '^## EV-[0-9]{3}' "$RESEARCH/evidence-notes.md"
rg -n -i 'real customer|real contractor|real supplier|private estimate|real project number|private workflow' "$RESEARCH" && exit 1 || true
python3 -m json.tool "$RESEARCH/evidence-notes.json" >/dev/null
git status --short
```

Expected: claim IDs are unique and sequential enough to audit, private-name scan is empty, JSON parses, and Git remains clean.

### Task 3: Build The Argument-Level Learning Architecture And Pause

**Files:**
- Create: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/outline.md`
- Replace: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/learning-outline.json`
- Replace: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/chapter-plans.json`
- Create: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/coverage-ledger.md`
- Replace: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/coverage-ledger.json`
- Replace: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/continuity.json`
- Create: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/continuity.md`
- Create: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/fact-packs/ch01.md` through `ch09.md`

**Interfaces:**
- Consumes: Task 2 hash-bound evidence and the approved nine-chapter design.
- Produces: complete human-reviewable section arguments, chapter plans, concept paths, and claim-specific fact packs. No prose may start before Dan approves this deliverable.

- [ ] **Step 1: Write the complete nine-chapter argument map**

Use exactly `ch01.md` through `ch09.md` with the approved chapter titles and jobs. Split each chapter into two to four named sections. Every section must record: ID, single job, one-sentence argument, specific `EV-NNN` claims, throughline advance, fictional-tender or historical payoff, landing beat, and must-not-repeat list.

Set `curriculumPattern.name` to `end-to-end-trace`. Record the reason, fit evidence, four approved throughlines, the eight durable outcomes, governing question, fictional tender spine, two history/institution anchors, all nine chapter-job types, varied public applications, and the optional-reference boundary.

- [ ] **Step 2: Complete every chapter plan before pilot prose**

For each `chNN.md`, record purpose, prerequisites, knowledge delta, grounded example, concepts, at least three distinct beats, no more than three `newCoreTerms`, problem-before-name evidence for each term, audio-load budget, narrative connection, and real-world application.

Use these primary chapter jobs in order: opening scene/reframing; history/system construction; decision comparison; guided obligation walkthrough; estimate mechanism; quote failure analysis; threat/authority analysis; adversarial closing review; post-bid application and pilot design.

- [ ] **Step 3: Complete the concept coverage ledger**

Create complete paths for at least these concepts: competitiveness; changing bid state; living bid record; source/version identity; bid/no-bid packet; obligation map; extraction versus compliance; provenance; deterministic automation; probabilistic assistance; assumption register; unresolved state; quote coverage; normalization; exclusion; discrepancy report; change propagation; data classification; least privilege; prompt injection; communication authority; price lock; submission authority; debriefing; award-data limits; estimate-versus-actual learning; and ninety-day primary measure.

Every JSON row must contain one durable outcome, definition, reason, mechanism, fictional concrete case, problem before name, at least two varied applications where applicable, boundary, misconception, expected ability, analogy contract or explicit omission reason, named chapter uses, and at least one retrieval after a chapter gap.

- [ ] **Step 4: Build chapter fact packs and draft contexts**

For each chapter, create `fact-packs/chNN.md` listing only the specific evidence IDs it may use, precise source wording boundaries, speakable real terms, fictional beats, prohibited claims, and chapter knowledge delta.

Initialize `continuity.json` with one `draftContexts` entry for every planned section. Each entry names the full outline path, evidence path, style profile, the actual prior-section summary or the exact sentence `Opening section; there is no previous section.`, section job, and exact must-not-repeat list. Keep `checkpoints` empty before canonical drafting.

- [ ] **Step 5: Validate the prospective architecture**

Run:

```bash
python3 -m json.tool "$RESEARCH/learning-outline.json" >/dev/null
python3 -m json.tool "$RESEARCH/chapter-plans.json" >/dev/null
python3 -m json.tool "$RESEARCH/coverage-ledger.json" >/dev/null
python3 -m json.tool "$RESEARCH/continuity.json" >/dev/null
jq -e '.schemaVersion == 2 and .curriculumPattern.name == "end-to-end-trace" and (.chapters | length) == 9 and (.durableOutcomes | length) >= 6 and (.durableOutcomes | length) <= 10' "$RESEARCH/learning-outline.json"
jq -e '.schemaVersion == 2 and (.chapters | length) == 9 and all(.chapters[]; (.newCoreTerms | length) <= 3)' "$RESEARCH/chapter-plans.json"
jq -e '.schemaVersion == 2 and (.concepts | length) >= 24 and all(.concepts[]; (.retrievals | length) >= 1)' "$RESEARCH/coverage-ledger.json"
jq -e '.schemaVersion == 2 and (.checkpoints | length) == 0 and (.draftContexts | length) >= 18' "$RESEARCH/continuity.json"
```

Expected: all prospective records pass and there are at least two planned sections per chapter.

- [ ] **Step 6: Present the argument-level outline and pause**

Show Dan `outline.md` plus a concise table of each section's argument, evidence IDs, payoff, and no-repeat duty. Ask for one verdict: `approve` or `revise`.

On approval, patch `learning-outline.json.authorization` to `status: approved`, `source: user`, and exact approval evidence. Patch `comprehension-pilot.json.humanCheckpoints.outline` to approved with reviewer, evidence, and `recordedBeforePilotDraft: true`.

Stop here if the verdict is not explicit approval. Do not draft the first section.

### Task 4: Draft And Accept The First-Section Voice Exemplar

**Files:**
- Create: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/draft-inputs/ch01-s01.md`
- Create: `.build/custom-learning-audiobooks/the-competitive-bid-room/pilot/chapters/ch01.md`
- Create: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/voice-exemplar.md`
- Modify: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/comprehension-pilot.json`

**Interfaces:**
- Consumes: approved argument outline, Ch. 1 fact pack, coverage rows, project craft profile, narration rules, and de-Claudification rules.
- Produces: only the opening section and its human-accepted voice exemplar. No remaining section may be drafted.

- [ ] **Step 1: Materialize the exact frontier-author input**

Write `draft-inputs/ch01-s01.md` containing: full outline path and SHA; evidence-notes path and SHA; Ch. 1 fact-pack content; relevant coverage rows; project craft profile; narration-style voice block; de-Claudification drafting rules; current section job/argument/claims/payoff/landing; and its must-not-repeat list.

- [ ] **Step 2: Draft only the approved opening section**

The frontier lead author writes approximately 900–1,200 words into `pilot/chapters/ch01.md`. Begin when the fictional tender arrives. Establish the changing document set, fixed deadline, competing attention, governing question, and human authority boundary. Do not complete Chapter 1 or introduce more than three durable terms.

- [ ] **Step 3: Run first-section checks**

Run:

```bash
wc -w "$RUN_ROOT/pilot/chapters/ch01.md"
rg -n '```|`[^`]+`|\b[A-Za-z]+_[A-Za-z_]+\b|->|[{}]' "$RUN_ROOT/pilot/chapters/ch01.md" && exit 1 || true
mkdir -p "$RUN_ROOT/pilot/qc"
cp "$RUN_ROOT/pilot/chapters/ch01.md" "$RUN_ROOT/pilot/qc/ch01.md"
python3 skill/scripts/prose_qc.py \
  --chapters-dir "$RUN_ROOT/pilot/qc" \
  --out "$RESEARCH/prose-qc-first-section.md" \
  --fail-on-style
```

Expected: the section is within range, has no narration-killing syntax, and the style gate passes.

- [ ] **Step 4: Present the exact section and pause for teaching/voice acceptance**

Ask Dan for `accept` or `revise`, with optional notes. If revised, apply only local frontier-author changes, rerun Step 3, and present the new exact text.

On acceptance, copy the accepted text byte-for-byte to `research/voice-exemplar.md`, compute SHA-256, and patch `comprehension-pilot.json.humanCheckpoints.firstSection` with approved status, reviewer, evidence, `recordedBeforeRemainingDraft: true`, path `research/voice-exemplar.md`, and exact SHA.

Stop if the section is not explicitly accepted.

### Task 5: Build, Render, And Accept The Native Echo Learning Pilot

**Files:**
- Modify: `.build/custom-learning-audiobooks/the-competitive-bid-room/pilot/chapters/ch01.md`
- Create: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/pronunciation-plan.json`
- Create under pilot: EPUB, Markdown, M4B, alignment, audit, reel when applicable, and pilot render receipts
- Create: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/approved-echo-pronunciation-sha.txt`
- Modify: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/comprehension-pilot.json`

**Interfaces:**
- Consumes: accepted first section, approved outline, and clean reviewed Echo pronunciation source SHA.
- Produces: a 10–15-minute native Echo pilot and Dan's hash-bound `continue` or `revise` verdict.

- [ ] **Step 1: Extend only the pilot material to representative length**

The frontier author adds the first technical passage to the pilot chapter, preserving the accepted opening byte-for-byte. The pilot must contain no more than three durable terms, at least two applications or consequences, one retrieval in a fresh situation, and enough prose for 10–15 minutes. It remains pilot-only, not canonical full Chapter 1.

- [ ] **Step 2: Create and planning-validate the pronunciation plan**

Create schema-v1 `pronunciation-plan.json` with every exact pilot term and variant that needs review. Use one object per base term with `variants`, not duplicate objects for singular and plural. Include at minimum `addendum` with variant `addenda`, `RFI` with variant `RFIs`, and any portal/procurement name actually present. Every term object contains `source` (`listener`, `coverage-ledger`, or `author`), nonempty `reason`, canonical `expectedChapters`, Boolean `required`, `status: planned`, and null decision/evidence. The complete shape is:

```json
{
  "schemaVersion": 1,
  "terms": [
    {
      "term": "addendum",
      "variants": ["addenda"],
      "source": "coverage-ledger",
      "reason": "The base and plural forms recur in document-control and closing passages.",
      "expectedChapters": ["ch04.md", "ch08.md"],
      "required": true,
      "status": "planned",
      "decision": null,
      "evidence": null
    },
    {
      "term": "RFI",
      "variants": ["RFIs"],
      "source": "coverage-ledger",
      "reason": "The acronym and plural occur in the obligation walkthrough.",
      "expectedChapters": ["ch04.md"],
      "required": true,
      "status": "planned",
      "decision": null,
      "evidence": null
    }
  ]
}
```

Run:

```bash
/usr/local/bin/python3 skill/scripts/pronunciation_plan_qc.py \
  --run-root "$RUN_ROOT" \
  --phase planning
```

Expected: planning validation passes.

- [ ] **Step 3: Build the explicitly nonpackage pilot**

Run:

```bash
/usr/local/bin/python3 skill/scripts/build_book.py \
  --chapters-dir "$RUN_ROOT/pilot/chapters" \
  --out-dir "$RUN_ROOT/pilot/dist" \
  --title "$TITLE — Learning Pilot" \
  --author "Dan Fakkeldy" \
  --contributor "$CONTRIBUTOR" \
  --slug "$SLUG-pilot" \
  --learning-pilot
unzip -t "$RUN_ROOT/pilot/dist/$SLUG-pilot.epub"
```

Expected: EPUB and Markdown build successfully and are explicitly marked nonpackage pilot artifacts.

- [ ] **Step 4: Render through the dedicated native Echo pilot wrapper**

Identify and review the clean Echo source commit that owns accepted pronunciation behavior; do not infer approval from current `HEAD`. Use `apply_patch` to write only that exact hexadecimal commit plus a trailing newline to `research/approved-echo-pronunciation-sha.txt`. Then run:

```bash
read -r APPROVED_ECHO_PRONUNCIATION_SHA < "$RESEARCH/approved-echo-pronunciation-sha.txt"
: "${APPROVED_ECHO_PRONUNCIATION_SHA:?approved Echo SHA file is empty}"
export RUN_ROOT SLUG TITLE APPROVED_ECHO_PRONUNCIATION_SHA
"$EXPLAINER_ROOT/skills/custom-learning-audiobook/scripts/echo_learning_pilot_narrate.sh"
```

Expected: the wrapper emits the pilot M4B, alignment, pronunciation audit, optional reel, immutable inputs, and `comprehension-pilot-render.json`; no sync or public delivery occurs.

- [ ] **Step 5: Verify pilot media and bind the exact hash**

Run:

```bash
ffprobe -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 \
  "$RUN_ROOT/pilot/dist/$SLUG-pilot.m4b"
python3 -m json.tool "$RUN_ROOT/pilot/dist/$SLUG-pilot.alignment.json" >/dev/null
python3 -m json.tool "$RESEARCH/comprehension-pilot-render.json" >/dev/null
shasum -a 256 "$RUN_ROOT/pilot/dist/$SLUG-pilot.m4b"
```

Expected: runtime is 10–15 minutes, JSON parses, and the exact audio digest is available.

- [ ] **Step 6: Present the pilot and pause for the lightweight verdict**

Give Dan the exact M4B path and audio SHA. Ask only `continue` or `revise`; notes are optional and no comprehension questionnaire is required.

On `continue`, patch `comprehension-pilot.json` to `status: accepted`, listener `Dan Fakkeldy`, actual listening context, exact audio path/SHA, optional notes, and a decision with `verdict: continue`, `authority: listener`, `evidence` set to the exact quoted user message, and `recordedBeforeFullDraft: true`.

On `revise`, record the verdict and return to the outline, first section, or pilot passage as the evidence requires. Do not start Task 6.

### Task 6: Draft Canonical Chapters 1–3 Sequentially

**Files:**
- Create: `.build/custom-learning-audiobooks/the-competitive-bid-room/chapters/ch01.md` through `ch03.md`
- Create/update: one section input under `research/draft-inputs/` for every section
- Update after every section/chapter: `research/continuity.md` and `research/continuity.json`
- Modify before prose: `research/learning-brief.json`

**Interfaces:**
- Consumes: accepted pilot, approved voice exemplar, full argument outline, exact fact packs, coverage paths, and current continuity.
- Produces: first three canonical chapters with prospective section contexts and checkpoints.

- [ ] **Step 1: Lock canonical drafting state**

Patch `learning-brief.json.draftingStarted` to `true`. Do not change any word estimate or scope-history entry.

- [ ] **Step 2: Draft Chapter 1 section by section**

Before each frontier-author call, materialize its complete draft input from the corresponding `continuity.json.draftContexts` entry. Preserve the accepted voice-exemplar opening exactly where it belongs, then complete **The Clock Starts**. After each section, update the running summary and no-repeat state; after the chapter, append the complete Ch. 1 checkpoint.

- [ ] **Step 3: Draft Chapter 2 section by section**

Write **From Plan Room to Living Bid** using only its claim IDs and the current continuity. Complete the first history anchor and build the minimum living-bid state. Append continuity before beginning Chapter 3.

- [ ] **Step 4: Draft Chapter 3 section by section**

Write **The Bid You Should Not Chase** as a decision comparison. Keep automated evidence preparation distinct from pursuit authority. Append continuity.

- [ ] **Step 5: Run the first manuscript checkpoint**

Run:

```bash
wc -w "$CHAPTERS"/ch0{1,2,3}.md
python3 skill/scripts/prose_qc.py \
  --chapters-dir "$CHAPTERS" \
  --out "$RESEARCH/prose-qc-ch01-ch03.md"
jq -e '.checkpoints | length == 3' "$RESEARCH/continuity.json"
```

Expected: each chapter completes its knowledge delta without padding, continuity has three checkpoints, and no hard style bans appear.

### Task 7: Draft Canonical Chapters 4–6 Sequentially

**Files:**
- Create: `.build/custom-learning-audiobooks/the-competitive-bid-room/chapters/ch04.md` through `ch06.md`
- Update after every section/chapter: draft inputs and continuity records

**Interfaces:**
- Consumes: Tasks 1–6 and continuity through Ch. 3.
- Produces: obligation, estimate, and quote-room chapters grounded only in their evidence IDs.

- [ ] **Step 1: Draft Chapter 4**

Write **Turn Documents into Obligations** as a guided walkthrough. Use the buried requirement, addendum, bid-security, question, and submission evidence. Extraction gathers cited evidence and never declares compliance. Update continuity.

- [ ] **Step 2: Draft Chapter 5**

Write **An Estimate That Can Explain Itself** as a mechanism chapter. Separate deterministic calculation from probabilistic extraction/interpretation; connect assumptions and unresolved state to named human ownership; avoid a spoken spreadsheet. Update continuity.

- [ ] **Step 3: Draft Chapter 6**

Write **The Quote That Wasn't Cheap** as a failure analysis. Use the material exclusion to teach coverage, normalization, approved follow-ups, late change, and discrepancy reporting. No example communication may be send-ready or imply automatic supplier selection. Update continuity.

- [ ] **Step 4: Run the second manuscript checkpoint**

Run:

```bash
wc -w "$CHAPTERS"/ch0{4,5,6}.md
python3 skill/scripts/prose_qc.py \
  --chapters-dir "$CHAPTERS" \
  --out "$RESEARCH/prose-qc-ch01-ch06.md"
jq -e '.checkpoints | length == 6' "$RESEARCH/continuity.json"
rg -n -i 'send this email|ready to send|automatically select|final price chosen by' "$CHAPTERS/ch06.md" && exit 1 || true
```

Expected: continuity has six checkpoints and the communication/authority scan is empty.

### Task 8: Draft Canonical Chapters 7–9 Sequentially

**Files:**
- Create: `.build/custom-learning-audiobooks/the-competitive-bid-room/chapters/ch07.md` through `ch09.md`
- Update after every section/chapter: draft inputs and continuity records
- Finalize: `research/sources-appendix.md`

**Interfaces:**
- Consumes: Tasks 1–7 and continuity through Ch. 6.
- Produces: complete nine-chapter canonical manuscript and public source appendix.

- [ ] **Step 1: Draft Chapter 7**

Write **Give the Machine Less Authority** as threat/boundary analysis. Cover classification, minimization, retention, least privilege, audit, prompt injection, untrusted documents, vendor boundaries, and outbound authority without drifting into legal or cybersecurity advice. Update continuity.

- [ ] **Step 2: Draft Chapter 8**

Write **Closing the Bid** as adversarial review. Red-team scope, assumptions, quotes, addenda, bonds, arithmetic, schedule, portal readiness, approvals, price lock, and named submission authority. Automated checks report evidence and exceptions, not a safe verdict. Update continuity.

- [ ] **Step 3: Draft Chapter 9**

Write **The Bid After the Bid** as consequence/application. Complete the award/debriefing/history anchor, estimate-versus-actual learning, supplier behavior, and one bounded ninety-day pilot with a baseline, primary measure, guardrails, and stop conditions. Update continuity.

- [ ] **Step 4: Verify the complete manuscript shape**

Run:

```bash
wc -w "$CHAPTERS"/ch*.md
test "$(find "$CHAPTERS" -maxdepth 1 -name 'ch*.md' | wc -l | tr -d ' ')" = 9
jq -e '.checkpoints | length == 9' "$RESEARCH/continuity.json"
rg -n '```|\b[A-Za-z]+_[A-Za-z_]+\b|->|[{}]' "$CHAPTERS" && exit 1 || true
```

Expected: exactly nine canonical chapters, roughly 18,000–22,000 words unless a learning-based variance is documented, nine continuity checkpoints, and no narration-killing syntax.

- [ ] **Step 5: Finish the non-narrated source appendix**

Ensure every factual chapter has a source section, each source supports an actual manuscript claim, changing sources carry retrieval dates, and jurisdiction/privacy limitations are explicit. Keep it outside `chapters/`.

### Task 9: Run Independent Learning Reviews And Substantive Repair

**Files:**
- Create: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/structure-review.md`
- Create: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/blind-sequential-review.md`
- Replace: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/learning-review.json`
- Modify for accepted repairs: canonical chapters and affected learning records

**Interfaces:**
- Consumes: complete manuscript, evidence, outline, plans, ledger, and continuity.
- Produces: citation-first independent findings, frontier-author decisions, and provisionally passing learning structure.

- [ ] **Step 1: Run the structure review**

Use an independent reviewer identity that did not author the prose. Give it the manuscript plus planning records. Require exact-location findings for orientation, progression, prerequisites, the end-to-end tender trace, throughline purpose, history/application infrastructure, unresolved promises, duplicate teaching jobs, knowledge deltas, authority boundaries, and optional-reference separation. Findings supply repair types, not replacement prose.

- [ ] **Step 2: Run the blind sequential practitioner review**

Use a distinct reviewer. Give it only the manuscript in order, one chapter at a time; withhold outline, ledger, expected abilities, and author rationale. Treat the listener as an experienced bidder new to automation architecture and AI governance. After each chapter record plausible mental model, confusions, unstable terms, and exact lost point.

- [ ] **Step 3: Have the frontier author decide every finding**

For each finding, record `accepted`, `rejected`, or `already-satisfied` with evidence. The frontier author makes every accepted factual, structural, explanation-depth, example, boundary, or voice repair locally in canonical Markdown. Update continuity, coverage, outline, or evidence records when the repair changes their truth.

- [ ] **Step 4: Rerun both reviewers on repaired text**

Require `verdict: pass` in both lanes or repeat Step 3. Populate `learning-review.json` with distinct reviewer names, review modes, citation-first decisions, every chapter assessment, and current chapter SHA-256 map.

- [ ] **Step 5: Verify review independence and hash binding**

Run:

```bash
jq -e '.schemaVersion == 2 and .structure.verdict == "pass" and .blindSequentialBeginner.verdict == "pass" and .structure.reviewer != .blindSequentialBeginner.reviewer and .blindSequentialBeginner.reviewMode == "manuscript-only-sequential" and .blindSequentialBeginner.intentionMaterialsWithheld == true and (.blindSequentialBeginner.chapterAssessments | length) == 9' "$RESEARCH/learning-review.json"
```

Expected: both lanes pass with distinct reviewers and nine sequential assessments. If independent delegation is unavailable and Dan has not authorized it, pause rather than fabricate independence.

### Task 10: Complete Narrow Revision Passes And The Rendered Ear Pass

**Files:**
- Replace: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/revision-passes.json`
- Modify for accepted repairs: canonical chapters and affected learning records
- Create: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/ear-pass/`

**Interfaces:**
- Consumes: provisionally passing manuscript and evidence records.
- Produces: five separately evidenced, final-hash revision lanes.

- [ ] **Step 1: Run claim traceability as its own call**

Compare every factual paragraph against `EV-NNN` records. Record exact unsupported, overstated, stale, or mislocated claims. The frontier author repairs or removes accepted findings; rerun until pass.

- [ ] **Step 2: Run tightening as its own call**

Flag avoidable repetition and filler only when it does not perform retrieval, deepening, application, comparison, or misconception correction. The frontier author makes local accepted repairs; rerun until pass.

- [ ] **Step 3: Run de-listification as its own call**

Flag mechanical list rhythm, false symmetry, and enumerations that should become connected spoken reasoning. Preserve real checklists in the non-narrated reference layer. Repair and rerun until pass.

- [ ] **Step 4: Run sentence-rhythm as its own call**

Flag repetitive paragraph openings, uniform sentence lengths, and assembled cadence without changing the approved voice or facts. Repair and rerun until pass.

- [ ] **Step 5: Render and hear the ear pass**

Render the final working chapters through Echo/Kokoro using a non-delivery QC path that does not claim a governed package. Listen for stumbles, ambiguous punctuation, acronym collisions, visual dependencies, and lost threads. Record every location in `revision-passes.json.passes[name=ear-pass].stumbles` or `lostThreadAt`; repair locally and rerender affected passages until pass.

- [ ] **Step 6: Bind the revision ledger to current hashes**

Set all five passes to `scope: single-job`, distinct named reviewer/call identity, `status: pass`, decisions, renderer/listening context for ear-pass, and exact canonical chapter hashes.

Run:

```bash
jq -e '.schemaVersion == 2 and (.passes | length) == 5 and all(.passes[]; .scope == "single-job" and .status == "pass")' "$RESEARCH/revision-passes.json"
```

### Task 11: Humanize, Re-Review, And Generate Final Manuscript Receipts

**Files:**
- Create: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/prose-qc-before.md`
- Create: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/editorial-review.md`
- Create: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/humanizer-decisions.json`
- Create: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/prose-qc-after.md`
- Create: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/prose-style-receipt.json`
- Replace: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/learning-review.json`
- Create: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/learning-design-receipt.json`

**Interfaces:**
- Consumes: repaired manuscript and passing revision ledger.
- Produces: final canonical chapter hashes shared by prose and learning receipts.

- [ ] **Step 1: Run the independent phrase-family inventory**

Run:

```bash
python3 skill/scripts/prose_qc.py \
  --chapters-dir "$CHAPTERS" \
  --out "$RESEARCH/prose-qc-before.md" \
  --fail-on-style
```

If it fails, preserve the report and continue only through targeted frontier-author decisions; never regenerate the book.

- [ ] **Step 2: Run the bounded humanizer review**

Load the `humanizer` skill. Require targeted exact-location suggestions only for AI tics, generic signposting, inflated claims, filler, repetitive rhythm, formulaic openings/closings, and honesty announcements. Preserve facts, citations, exact terms, chapter order, examples, boundaries, intentional retrieval, and the accepted voice.

- [ ] **Step 3: Record frontier-author decisions and make accepted local edits**

Create `humanizer-decisions.json` with reviewer/model/skill version, `humanizer_applied: true`, accepted and rejected findings with reasons, touched chapters, and factual/ledger/narration/prose reruns. The frontier author makes all accepted non-mechanical changes.

- [ ] **Step 4: Generate the final prose receipt**

Run:

```bash
python3 skill/scripts/prose_qc.py \
  --chapters-dir "$CHAPTERS" \
  --out "$RESEARCH/prose-qc-after.md" \
  --fail-on-style \
  --decisions "$RESEARCH/humanizer-decisions.json" \
  --style-receipt-out "$RESEARCH/prose-style-receipt.json"
```

Expected: style gate passes and receipt binds every canonical chapter hash.

- [ ] **Step 5: Rerun both independent learning reviews on final hashes**

Repeat Task 9's structure and blind sequential lanes after all voice edits. Update `learning-review.json` to passing verdicts and final chapter hashes. Do not reuse a pre-humanizer hash map.

- [ ] **Step 6: Generate the learning receipt and compare hash sets**

Run:

```bash
python3 skill/scripts/learning_design_qc.py \
  --run-root "$RUN_ROOT" \
  --receipt-out "$RESEARCH/learning-design-receipt.json"
python3 - <<'PY'
import json
from pathlib import Path
root = Path('.build/custom-learning-audiobooks/the-competitive-bid-room/research')
learning = json.loads((root / 'learning-design-receipt.json').read_text())
prose = json.loads((root / 'prose-style-receipt.json').read_text())
lh = learning.get('chapterSHA256') or learning.get('reviewedChapterSHA256')
ph = prose.get('chapter_sha256') or prose.get('chapterSHA256')
assert lh == ph and isinstance(lh, dict) and len(lh) == 9
print('FINAL_RECEIPT_HASHES_MATCH')
PY
```

Expected: learning QC passes and both receipts bind the same nine chapter hashes.

### Task 12: Create Exactly Three New Cover Pairs And Pause For Selection

**Files:**
- Create: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/cover-research.md`
- Create under each `.build/custom-learning-audiobooks/the-competitive-bid-room/dist/candidate-{1,2,3}/`: `art-direction.md`, `source-art.png`, `cover-spec.json`, `m4b-cover-spec.json`, portrait/square outputs, thumbnails, and render receipts
- Create: portrait and square contact sheets

**Interfaces:**
- Consumes: final manuscript argument, audience promise, public-safety boundary, and current cover-art contract.
- Produces: exactly three complete coordinated cover pairs and Dan's explicit selection or requested mix. It does not yet produce `cover-selection.json`.

- [ ] **Step 1: Research transferable visual principles and write three briefs**

Each `art-direction.md` must specify audience promise, central metaphor, composition/crops/title fields, material language, distinct two-to-four-colour palette and visible accent hex, anti-brief, title archetype/font roles, line breaks/hierarchy, anchor/occupied area, art/type relationship, subtitle, author, and AUDIOBOOK placement.

The three candidates must differ in metaphor, composition, palette, material language, and title strategy. At least one is bright/high-key. Do not reuse the old candidates as accepted inputs or merely recolour them.

- [ ] **Step 2: Generate exactly three original text-free raster artworks**

Use the strongest available image-generation tool directly. Each prompt follows `skill/references/cover-art.md`, names one specific physical metaphor, preserves a deliberate title field, and prohibits lettering, logos, watermarks, interfaces, generic AI wallpaper, dashboards, mockups, borders, and close imitation.

Reject generic or weak outputs before rendering. Save provenance in `cover-research.md`.

- [ ] **Step 3: Create paired schema-v2 specifications and render each pair**

For candidates 1 through 3, save shared `source-art.png`, `cover-spec.json`, and `m4b-cover-spec.json`, then run:

```bash
for n in 1 2 3; do
  PAIR="$DIST/candidate-$n" /usr/local/bin/python3 - <<'PY'
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path('skill/scripts').resolve()))
from cover_pairs import render_cover_pair
pair = Path(os.environ['PAIR'])
render_cover_pair(
    portrait_spec=pair / 'cover-spec.json',
    square_spec=pair / 'm4b-cover-spec.json',
    portrait_output=pair / 'cover.png',
    square_output=pair / 'm4b-cover.png',
    portrait_thumbnail=pair / 'cover-thumbnail.png',
    square_thumbnail=pair / 'm4b-cover-thumbnail.png',
    portrait_receipt=pair / 'cover-render.json',
    square_receipt=pair / 'm4b-cover-render.json',
)
PY
done
```

- [ ] **Step 4: Inspect all twelve outputs**

Verify exactly three candidate directories and these dimensions: portrait 1600×2560, square 2400×2400, portrait thumbnail 160×256, square thumbnail 160×160. Inspect every full-size and thumbnail render; record type/palette notes, warnings, and acceptance in each brief. Build portrait and square contact sheets.

- [ ] **Step 5: Present all three pairs and pause**

Show the portrait and square comparisons together with one concise rationale per direction. Ask Dan to choose `1`, `2`, `3`, or request a specific mix.

Do not create `cover-selection.json`, build the governed EPUB, or begin full narration until the choice is explicit. A requested mix becomes a new specification and render, then returns to this gate.

### Task 13: Record The Cover Choice, Build The Governed EPUB, And Accept Pronunciations

**Files:**
- Create: `.build/custom-learning-audiobooks/the-competitive-bid-room/dist/cover-selection.json`
- Create: selected candidate's `cover-selection.json`
- Create: `.build/custom-learning-audiobooks/the-competitive-bid-room/dist/the-competitive-bid-room.epub`
- Create: `.build/custom-learning-audiobooks/the-competitive-bid-room/dist/the-competitive-bid-room.md`
- Finalize: pronunciation plan, probe reel/evidence, and receipt

**Interfaces:**
- Consumes: final-hash learning/prose receipts and explicit cover selection.
- Produces: governed EPUB/Markdown and human-accepted pronunciation evidence authorizing the full Echo render.

- [ ] **Step 1: Create the paired selection receipt**

Set `SELECTED`, `SELECTED_AT` to the real ISO-8601 choice time, and `PAIR="$DIST/candidate-$SELECTED"`. Run:

```bash
/usr/local/bin/python3 skill/scripts/cover_receipts.py select-pair \
  --portrait-render-receipt "$PAIR/cover-render.json" \
  --square-render-receipt "$PAIR/m4b-cover-render.json" \
  --out "$DIST/cover-selection.json" \
  --book-slug "$SLUG" \
  --edition-id "$EDITION_ID" \
  --selection-source user \
  --selected-at "$SELECTED_AT" \
  --privacy-classification public-safe \
  --permission-to-publish
cp "$DIST/cover-selection.json" "$PAIR/cover-selection.json"
```

For a requested mix, use `--selection-source requested-mix` after rendering the new pair.

- [ ] **Step 2: Build the governed EPUB and combined Markdown**

Run:

```bash
/usr/local/bin/python3 skill/scripts/build_book.py \
  --chapters-dir "$CHAPTERS" \
  --out-dir "$DIST" \
  --title "$TITLE" \
  --author "Dan Fakkeldy" \
  --contributor "$CONTRIBUTOR" \
  --subtitle "$SUBTITLE" \
  --slug "$SLUG" \
  --cover "$PAIR/cover.png" \
  --m4b-cover "$PAIR/m4b-cover.png" \
  --cover-selection "$DIST/cover-selection.json" \
  --learning-receipt "$RESEARCH/learning-design-receipt.json" \
  --prose-receipt "$RESEARCH/prose-style-receipt.json" \
  --non-narrated-appendix "$RESEARCH/sources-appendix.md"
unzip -t "$DIST/$SLUG.epub"
```

Expected: governed build succeeds with selected portrait cover and both final receipts.

- [ ] **Step 3: Finalize the full pronunciation plan**

Scan the final manuscript and ledger for every risky term and variant. Include at minimum when present: `addendum`/`addenda`, `Ariba`, `CanadaBuys`, `e-bond`/`e-bonding`, `RFI`/`RFIs`, `RFQ`/`RFQs`, `deterministic`, `probabilistic`, `discrepancy`/`discrepancies`, and `prompt injection`. Record exact canonical chapters and reasons.

Run planning validation:

```bash
/usr/local/bin/python3 skill/scripts/pronunciation_plan_qc.py \
  --run-root "$RUN_ROOT" \
  --phase planning
```

- [ ] **Step 4: Render bounded real-book probes**

Export selected covers, plan, preferred voice, and reviewed clean Echo SHA. Run one new chapter at a time:

```bash
export VOICE=am_michael
export COVER="$PAIR/cover.png"
export M4B_COVER="$PAIR/m4b-cover.png"
export PRONUNCIATION_PLAN="$RESEARCH/pronunciation-plan.json"
read -r APPROVED_ECHO_PRONUNCIATION_SHA < "$RESEARCH/approved-echo-pronunciation-sha.txt"
: "${APPROVED_ECHO_PRONUNCIATION_SHA:?approved Echo SHA file is empty}"
set +e
"$EXPLAINER_ROOT/skills/custom-learning-audiobook/scripts/echo_pronunciation_narrate.sh" --max-chapters 1
status=$?
set -e
test "$status" = 2
```

Repeat with `--resume --max-chapters 1` only as needed to capture every required term. Exit 2 is expected partial state and authorizes no deliverable.

- [ ] **Step 5: Build and hear the pronunciation reel**

Resolve `WORK` from the current attempt/input receipt, then run:

```bash
/usr/local/bin/python3 skill/scripts/build_pronunciation_probe_reel.py \
  --run-root "$RUN_ROOT" \
  --work-dir "$WORK" \
  --out "$RESEARCH/pronunciation-probe-reel.m4b" \
  --evidence-out "$RESEARCH/pronunciation-probe-evidence.json"
```

Dan hears every required base form and variant. Only after explicit acceptance, set each required entry to `status: accepted`, record acceptedBy/acceptedAt, and bind its evidence path/SHA.

- [ ] **Step 6: Generate the immutable full-render pronunciation receipt**

Run:

```bash
/usr/local/bin/python3 skill/scripts/pronunciation_plan_qc.py \
  --run-root "$RUN_ROOT" \
  --phase full-render \
  --receipt-out "$RESEARCH/pronunciation-plan-receipt.json"
```

Expected: full-render validation passes. Stop if Dan has not accepted the reel.

### Task 14: Complete Governed Echo Narration And Final Artifact Verification

**Files:**
- Create under `dist/echo-renders/$RUN_ID/$ATTEMPT_ID/`: final M4B, alignment, pronunciation audit, and optional reel
- Create under `research/`: current-attempt, current-accepted, input, resume-state, and schema-v2 success receipts
- Create: `.build/custom-learning-audiobooks/the-competitive-bid-room/dist/README.md`

**Interfaces:**
- Consumes: immutable EPUB, selected pair receipt, accepted pronunciation receipt, exact Echo SHA, and partial capture state.
- Produces: current selector-authorized native Echo package and manifest.

- [ ] **Step 1: Resume the governed render without a chapter limit**

Run with the exact same immutable inputs used by Task 13:

```bash
export RUN_ROOT SLUG TITLE VOICE COVER M4B_COVER PRONUNCIATION_PLAN APPROVED_ECHO_PRONUNCIATION_SHA
"$EXPLAINER_ROOT/skills/custom-learning-audiobook/scripts/echo_pronunciation_narrate.sh" --resume
```

Expected: the wrapper publishes a nonempty run-scoped M4B, sidecar, schema-v2 audit, success receipt, and current-accepted selector. Do not add a timeout or mutate the M4B afterward.

- [ ] **Step 2: Resolve the accepted artifact chain from the selector**

Parse `research/echo-render-current-accepted.json` to obtain `RUN_ID`, `ATTEMPT_ID`, artifact relative path, input receipt, and success receipt. Derive exact M4B, sidecar, audit, optional reel, and resume-state paths. Reject any mismatch between the attempt and accepted selectors.

- [ ] **Step 3: Run selector-bound delivery verification**

Run `echo_pronunciation_state.py verify-delivery` with the current-attempt selector, current-accepted selector, success receipt, input receipt, resume-state receipt, EPUB, M4B, sidecar, audit, and reel. Then run:

```bash
ffprobe -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 "$AUDIOBOOK"
python3 -m json.tool "$SIDECAR" >/dev/null
"$CLI" verify-sidecar \
  --epub "$DIST/$SLUG.epub" \
  --audio "$AUDIOBOOK" \
  --sidecar "$SIDECAR"
"$EXPLAINER_ROOT/skills/custom-learning-audiobook/scripts/validate_pronunciation_audit.py" "$AUDIT"
```

Expected: `SIDECAR_OK`, positive runtime, schema-valid alignment/audit, complete coverage, matching watch counts, and zero unresolved diagnostics.

- [ ] **Step 4: Verify the selected portrait and square covers across EPUB and M4B**

Run:

```bash
/usr/local/bin/python3 skill/scripts/cover_receipts.py verify \
  --selection "$DIST/cover-selection.json" \
  --cover "$PAIR/cover.png" \
  --m4b-cover "$PAIR/m4b-cover.png" \
  --epub "$DIST/$SLUG.epub" \
  --m4b "$AUDIOBOOK" \
  --receipt "$DIST/cover-selection.json"
```

Expected: selected portrait cover matches EPUB and selected square cover matches the exact audited M4B. Never repair failure by retagging or replacing M4B artwork; correct source and rerender.

- [ ] **Step 5: Write the final manifest**

Create `dist/README.md` with title, subtitle, slug, edition ID, requester/topic, public-safe status, publication permission, length mode, exact word count, runtime, chapter count, narrator, frontier author model, research/review/production roles, research mode/confidence, figure count zero, output files, all receipt paths/hashes, pronunciation audit/reel/watch counts, human listening states, approved/source Echo SHAs, EPUB/CLI/resource hashes, and passed/skipped QC gates.

### Task 15: Deliver, Publish, Update Documentation, And Close The Work

**Files:**
- Create/update governed public package: `books/the-competitive-bid-room/`
- Modify: `README.md`
- Create/update: narrow business KB status receipt, status index, and newest-first log
- Create transiently: `.build/custom-learning-audiobooks/the-competitive-bid-room/research/public-pr-body.md`

**Interfaces:**
- Consumes: selector-authorized final package and explicit public-safe permission.
- Produces: checksum-consistent iCloud Books copy, public repository package, collection metadata, KB receipt, and review-ready PR.

- [ ] **Step 1: Dry-run and apply iCloud Books sync**

Set:

```bash
export DELIVERY_DIR="/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/$TITLE"
```

Run `sync_selected_cover.py` first without `--apply`, using selection, selected portrait cover, EPUB, M4B, selected paired-artifact directory, destination, and `--intent reuse`. Inspect the destination classification. Only when expected, rerun with `--apply`.

- [ ] **Step 2: Copy non-governed delivery artifacts without overwriting governed files**

Copy combined Markdown, README, sidecar, audit, optional reel, and the exact current-attempt/current-accepted/input/resume/success receipts. Do not copy `echo-renders/` wholesale and do not overwrite cover, EPUB, M4B, or selection receipt after governed sync.

- [ ] **Step 3: Verify the actual iCloud destination**

From `DELIVERY_DIR`, rerun paired cover verification, `unzip -t`, `ffprobe`, JSON parsing, pronunciation-audit validation, `verify-sidecar`, and selector-bound `verify-delivery`. Compare SHA-256 hashes for EPUB, M4B, alignment, audit, README, and receipts with the accepted source package.

- [ ] **Step 4: Dry-run and apply the public repository sync**

Run:

```bash
export PUBLIC_DIR="$EXPLAINER_ROOT/books/$SLUG"
/usr/local/bin/python3 skill/scripts/sync_selected_cover.py \
  --selection "$DIST/cover-selection.json" \
  --cover "$PAIR/cover.png" \
  --epub "$DIST/$SLUG.epub" \
  --m4b "$AUDIOBOOK" \
  --paired-artifact-dir "$PAIR" \
  --destination "$PUBLIC_DIR" \
  --intent reuse \
  --public-destination
```

Inspect classification and repo artifact policy, then repeat with `--apply`. Only afterward copy combined Markdown and README. Never publish research, draft inputs, databases, captures, or private material.

- [ ] **Step 5: Update collection documentation and public metadata**

Add the verified book to the repository README using actual runtime and file names. Update any collection totals from the live package rather than estimates. Run repository tests and package validation relevant to public books.

- [ ] **Step 6: File the narrow KB completion receipt**

In a fresh KB worktree, record public title, verified runtime, chapter/word count, narrator, public-safe status, exact delivery/public paths, PR, and QC boundaries. Update the nearest project/status indexes and newest-first log. Do not copy manuscript research or private material. Run `python3 tools/kb_lint.py`, commit, push, and open the normal KB PR.

- [ ] **Step 7: Commit and publish the public package branch**

First use `apply_patch` to write `research/public-pr-body.md`. It must list exact package hashes, runtime, chapter/word count, cover choice, narrator, human pilot verdict, pronunciation status, receipt gates, iCloud verification, public/private boundary, and tests. If the repository has no hosted checks, say so explicitly.

Then run:

```bash
git status --short --branch
git diff --check
git add books/the-competitive-bid-room README.md
git commit -m "feat: publish The Competitive Bid Room road book"
git fetch origin main
git rebase origin/main
git push -u origin codex/competitive-bid-room-road-book
gh pr create --base main --head codex/competitive-bid-room-road-book \
  --title "Publish The Competitive Bid Room road book" \
  --body-file "$RESEARCH/public-pr-body.md"
```

- [ ] **Step 8: Verify final repository states and report proof boundaries**

Check `git status --short --branch` in the audiobook and KB worktrees. Re-query both PRs and hosted checks. Report separately: design approved; pilot accepted; manuscript final; package verified; iCloud copy verified; public repo PR open/merged; KB receipt open/merged; and human final-audiobook listening pending or complete.

Do not call the book delivered if native Echo narration, selector-bound verification, paired cover verification, or destination verification is incomplete.
