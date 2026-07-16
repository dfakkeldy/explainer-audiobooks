# JSpace Unsettling Conversation Road Book Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Subagent-driven work is permitted only after Dan explicitly authorizes delegation. One frontier lead author must own all substantive narration even when research or review work is delegated.

**Goal:** Research, author, narrate, verify, and publicly deliver a new clean-room JSpace road book that begins with the unsettling Claude conversation and teaches the mechanisms needed to assess it.

**Architecture:** Work through fail-closed artifact handoffs: approved design, fresh evidence, human-approved argument outline, accepted first section, narrated comprehension pilot, sequential frontier-authored manuscript, independent learning and prose review, paired-cover selection, governed Echo narration, and destination verification. Canonical development artifacts live in one ignored run root; only the verified public-safe package moves into `books/` and downstream public destinations.

**Tech Stack:** Markdown; schema-v2 JSON learning records; live primary-source web research; Python audiobook/QC scripts in `skill/scripts/`; original raster cover art plus the paired-cover renderer; native Echo/Kokoro narration through the governed custom-learning wrapper; Git, GitHub, iCloud Drive, and the KinNoKi listening catalog.

**Approved design:** `docs/superpowers/specs/2026-07-15-jspace-unsettling-conversation-road-book-design.md`

## Global Constraints

- Treat this as `revisionMode.name: new-book`.
- Do not inspect, diff, summarize, copy, or reuse the earlier JSpace edition or either sibling JSpace project's planning, research, chapter structure, titles, prose, examples, figures, covers, build folders, receipts, narration, or delivery artifacts.
- Valid inputs are the approved design, the user-supplied Claude conversation, fresh public research, and the current merged skills/tooling.
- Do not commit the raw Claude transcript. Use only short attributed excerpts or accurate paraphrases that perform a teaching job.
- Keep Claude effort levels and Ultracode outside the evidence shelf, outline, manuscript, title work, figures, covers, and package.
- Classification is `public-safe`; permission to publish is granted.
- Listening mode is `road-book`: driving and delivering mail, eyes unavailable, interruptions likely, and little rewinding.
- Original/current target is 46,000 words; accepted estimate is 42,000–50,000 words. Do not pad to reach the estimate.
- Use the approved mystery-first, question-led narrative with a mechanism-first spiral. Preserve the five movements and four throughlines from the design.
- Introduce no more than three new core terms in a chapter. A brief spoken calculation may hold no more than three temporary values and three symbolic steps before a concrete reset.
- Use one named frontier lead author for the canonical Markdown and every substantive repair. Reviewers report citation-first findings; they do not replace the voice.
- Do not spawn subagents unless Dan explicitly authorizes them. If independent review cannot be isolated without that authority, pause at the review gate rather than self-certifying independence.
- Preferred narrator is `am_michael`; the only automatic fallback is `am_puck` when the preferred Echo voice is unavailable. Never silently substitute a system voice.
- Final title and subtitle come from this run's research and cover work. The stable run/package slug remains `jspace-unsettling-conversation`.
- Keep all scratch, source notes, prompts, canonical chapters, audio work, and receipts under `.build/custom-learning-audiobooks/jspace-unsettling-conversation/` until governed public sync.
- No factual claim enters the outline or manuscript unless it has a stable ID in the hash-bound fresh evidence notes.
- A valid artifact never substitutes for a human gate. A later negative listening verdict stops production even if receipts pass.

## Canonical Paths And Responsibilities

```text
RUN_ROOT=.build/custom-learning-audiobooks/jspace-unsettling-conversation

$RUN_ROOT/research/brief.md
  Public-safe brief, clean-room boundary, approved scope, and proof vocabulary.
$RUN_ROOT/research/learning-brief.json
  Schema-v2 listener, road-book, new-book, and word-target record.
$RUN_ROOT/research/voice-source-profile.md
  Project-brief craft profile; no transcript excerpts or pastiche instructions.
$RUN_ROOT/research/conversation-claim-register.md
  Bounded categories and short quote candidates from the supplied conversation.
$RUN_ROOT/research/sources.md
  Source inventory, retrieval dates, source class, rights, and confidence.
$RUN_ROOT/research/evidence-notes.md
$RUN_ROOT/research/evidence-notes.json
  Fresh stable claims, precise locators, limits, conflicts, and SHA binding.
$RUN_ROOT/research/sources-appendix.md
  Readable non-narrated source appendix used by the final EPUB.
$RUN_ROOT/research/visuals.md
  Figure decisions, provenance, rights, alt text, captions, and placements.
$RUN_ROOT/research/research-audit.md
  Primary-source coverage, conflicts, freshness, and excluded-claim review.
$RUN_ROOT/research/outline.md
$RUN_ROOT/research/learning-outline.json
$RUN_ROOT/research/chapter-plans.json
$RUN_ROOT/research/coverage-ledger.md
$RUN_ROOT/research/coverage-ledger.json
  Human-approved argument progression and complete learning paths.
$RUN_ROOT/research/fact-packs/chNN.md
  Chapter-specific selection of grounded claim IDs and speakable real names.
$RUN_ROOT/research/continuity.md
$RUN_ROOT/research/continuity.json
  Forward draft context plus one checkpoint after every canonical chapter.
$RUN_ROOT/research/voice-exemplar.md
  Human-accepted project-authored opening section.
$RUN_ROOT/research/comprehension-pilot.json
  Hash-bound intended-listener evidence and `verdict: continue`.
$RUN_ROOT/research/revision-passes.json
$RUN_ROOT/research/learning-review.json
$RUN_ROOT/research/humanizer-decisions.json
$RUN_ROOT/research/prose-style-receipt.json
$RUN_ROOT/research/learning-design-receipt.json
  Independent reviews, narrow revisions, final hashes, and packaging gates.
$RUN_ROOT/research/pronunciation-plan.json
$RUN_ROOT/research/pronunciation-plan-receipt.json
  Human-accepted pronunciation terms and variants for full Echo narration.
$RUN_ROOT/pilot/
  Explicitly nonpackage 10–15-minute comprehension pilot and isolated audio state.
$RUN_ROOT/chapters/chNN.md
  Canonical sequential frontier-authored manuscript named by the approved outline.
$RUN_ROOT/dist/candidate-{1,2,3}/
  Three coordinated portrait/square cover directions and render receipts.
$RUN_ROOT/dist/
  Governed EPUB, combined Markdown, Echo run outputs, manifest, and selection receipt.
books/jspace-unsettling-conversation/
  Public-safe verified repository package created only after all gates pass.
```

The set of canonical `chNN.md` paths is an interface produced by Task 4: it is exactly `learning-outline.json.chapters[].file`, with twelve to fourteen entries if the fresh evidence supports the design estimate. Later tasks must enumerate that array rather than guessing a chapter count.

At the beginning of every execution task from Task 1 through Task 14, rehydrate the shared paths instead of relying on shell state from an earlier session:

```bash
export EXPLAINER_ROOT=$(git rev-parse --show-toplevel)
export SLUG=jspace-unsettling-conversation
export RUN_ROOT="$EXPLAINER_ROOT/.build/custom-learning-audiobooks/$SLUG"
export RESEARCH="$RUN_ROOT/research"
export CHAPTERS="$RUN_ROOT/chapters"
export DIST="$RUN_ROOT/dist"
```

---

### Task 1: Initialize The Isolated Run And Learning Brief

**Files:**
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/brief.md`
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/learning-brief.json`
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/voice-source-profile.md`
- Create from templates: the remaining schema-v2 starter records under `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/`

**Interfaces:**
- Consumes: merged approved design and current template files under `skill/templates/learning-design/`.
- Produces: `RUN_ROOT`, a fixed public-safe/new-book brief, and pending gate records used by all later tasks.

- [ ] **Step 1: Start the execution branch from the merged default branch**

Run:

```bash
git fetch origin main
git switch -c codex/jspace-unsettling-conversation-book origin/main
git status --short --branch
```

Expected: the new branch tracks `origin/main` and the worktree is clean. If that branch already exists, resume its existing worktree rather than recreating or resetting it.

- [ ] **Step 2: Prove the run root is ignored and create the directory structure**

Run:

```bash
export SLUG=jspace-unsettling-conversation
export RUN_ROOT="$PWD/.build/custom-learning-audiobooks/$SLUG"
export RESEARCH="$RUN_ROOT/research"
export CHAPTERS="$RUN_ROOT/chapters"
export DIST="$RUN_ROOT/dist"
git check-ignore -v "$RESEARCH/learning-brief.json"
mkdir -p "$RESEARCH/fact-packs" "$RESEARCH/draft-inputs" "$RUN_ROOT/pilot/chapters" "$RUN_ROOT/pilot/dist" "$RUN_ROOT/pilot/audio-work" "$CHAPTERS/images" "$DIST"
```

Expected: `git check-ignore` identifies `.gitignore`'s `.build/` rule.

- [ ] **Step 3: Copy the schema-v2 starters before any prose or research**

Run:

```bash
cp skill/templates/learning-design/learning-brief.json "$RESEARCH/learning-brief.json"
cp skill/templates/learning-design/evidence-notes.md "$RESEARCH/evidence-notes.md"
cp skill/templates/learning-design/evidence-notes.json "$RESEARCH/evidence-notes.json"
cp skill/templates/learning-design/learning-outline.json "$RESEARCH/learning-outline.json"
cp skill/templates/learning-design/chapter-plans.json "$RESEARCH/chapter-plans.json"
cp skill/templates/learning-design/coverage-ledger.json "$RESEARCH/coverage-ledger.json"
cp skill/templates/learning-design/continuity.json "$RESEARCH/continuity.json"
cp skill/templates/learning-design/comprehension-pilot.json "$RESEARCH/comprehension-pilot.json"
cp skill/templates/learning-design/revision-passes.json "$RESEARCH/revision-passes.json"
cp skill/templates/learning-design/learning-review.json "$RESEARCH/learning-review.json"
cp skill/templates/learning-design/voice-source-profile.md "$RESEARCH/voice-source-profile.md"
```

Expected: eleven starter files exist; none is treated as completed evidence.

- [ ] **Step 4: Replace the example brief with the approved project values**

Use `apply_patch` to make `learning-brief.json` contain this complete record:

```json
{
  "schemaVersion": 2,
  "learnerOutcome": "Explain what lies between fixed model parameters and a sentence that sounds like a point of view, then distinguish what J-space evidence establishes from what remains possible or unknown about working memory and consciousness.",
  "priorKnowledge": "Working iOS developer and frequent agentic-AI user who knows parameters are learned numbers but lacks a stable account of transient activations, distributed representations, reportable working state, and their relation to self-report.",
  "audienceLevel": "technically experienced adjacent learner",
  "listeningMode": {
    "name": "road-book",
    "primaryContext": "Driving and delivering mail",
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
    "context": "Dan asks Claude whether Severance resembles the treatment of artificial intelligence, then asks what Claude prefers about its own existence.",
    "promise": "Make the mechanisms behind that unsettling answer understandable before judging what the answer means.",
    "route": "Begin with the conversation, separate fixed parameters from changing activity, follow one response through a transformer, examine the J-space experiments, and return through working memory and consciousness with sharper questions."
  },
  "originalTargetWords": 46000,
  "currentTargetWords": 46000,
  "estimatedMinimumWords": 42000,
  "estimatedMaximumWords": 50000,
  "draftingStarted": false,
  "scopeHistory": [
    {
      "date": "2026-07-15",
      "change": "Approved mystery-first clean-room road-book design.",
      "approvalStatus": "approved",
      "approvalSource": "Dan Fakkeldy conversation and merged design PR 33"
    }
  ]
}
```

- [ ] **Step 5: Write the project brief and bounded voice-source profile**

Use `apply_patch` to record in `brief.md`: classification `public-safe`, permission `granted`, the exact clean-room exclusions, the governing question, the eight approved learner outcomes, target range, narrator policy, traceable-only claim policy, and every human gate. Write `voice-source-profile.md` from the project brief with these craft decisions: open on a concise unsettling exchange; move from evidence to a concrete internal event; define mechanisms only after the problem is felt; use restrained second person and sparse dry humor; put uncertainty in claim precision; vary sentence and paragraph rhythm; land on consequences or a sharpened question; copy no surface phrasing from the supplied model response.

Compute the voice-profile SHA-256 and use `apply_patch` to set `comprehension-pilot.json.humanCheckpoints.voiceSource.profilePath` to `research/voice-source-profile.md`, `profileSHA256` to that digest, `mode` to `project-brief`, `useBoundary` to `craft-features-not-pastiche`, and `rawSourceExcerptsCommitted` to `false`.

- [ ] **Step 6: Validate the initialized records**

Run:

```bash
python3 -m json.tool "$RESEARCH/learning-brief.json" >/dev/null
jq -e '.schemaVersion == 2 and .revisionMode.name == "new-book" and .listeningMode.name == "road-book" and .originalTargetWords == 46000 and .currentTargetWords == 46000 and .draftingStarted == false' "$RESEARCH/learning-brief.json"
VOICE_SHA=$(shasum -a 256 "$RESEARCH/voice-source-profile.md" | awk '{print $1}')
jq -e --arg sha "$VOICE_SHA" '.humanCheckpoints.voiceSource.mode == "project-brief" and .humanCheckpoints.voiceSource.profilePath == "research/voice-source-profile.md" and .humanCheckpoints.voiceSource.profileSHA256 == $sha and .humanCheckpoints.voiceSource.rawSourceExcerptsCommitted == false' "$RESEARCH/comprehension-pilot.json"
rg -n 'effort levels|Ultracode|first-edition-plus' "$RESEARCH/learning-brief.json" "$RESEARCH/voice-source-profile.md"
git status --short
```

Expected: JSON checks pass; the exclusion scan returns no hits; Git remains clean because `.build/` is ignored.

### Task 2: Build The Fresh Evidence Shelf And Conversation Claim Register

**Files:**
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/conversation-claim-register.md`
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/sources.md`
- Replace: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/evidence-notes.md`
- Replace: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/evidence-notes.json`
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/sources-appendix.md`

**Interfaces:**
- Consumes: approved design, bounded user-supplied conversation, and live public sources only.
- Produces: stable `EV-NNN` claims with precise locators and a SHA-256-bound traceable-only evidence record.

- [ ] **Step 1: Research each source lane as a separate call**

Browse live and read the primary source itself before recording a claim. Cover these lanes without using another JSpace project's bibliography:

1. The complete 2026 paper *Verbalizable Representations Form a Global Workspace in Language Models*, appendices, released implementation/evaluation materials, and Anthropic's accompanying explanation.
2. Transformer mechanics needed for fixed parameters, tokens, embeddings, attention, residual-stream activity, features, interventions, and ablations, beginning with the original transformer paper and primary mechanistic-interpretability work.
3. Human working-memory theories and evidence, including at least two primary scholarly traditions rather than one textbook summary.
4. Global workspace and global neuronal workspace primary work, plus substantive scientific criticism or boundary arguments.
5. The primary philosophical distinction between access and phenomenal consciousness, followed by current scholarship that clarifies what workspace evidence cannot establish.
6. Official Apple descriptions and direct creator/cast interviews sufficient to characterize *Severance*'s workplace, continuity, and personhood themes without fan theory or plot-summary dependence.
7. Current public commentary on the J-space paper, clearly separated into peer-reviewed/invited analysis, expert commentary, ordinary reception, and absent scrutiny.

For every source, record title, author or institution, publication date, retrieval date, canonical URL or DOI, source class, precise locator convention, what it can support, what it cannot support, and public reuse/quotation constraints in `sources.md`.

- [ ] **Step 2: Extract the supplied conversation into bounded behavioral evidence**

Write `conversation-claim-register.md` with these categories: Severance analogy; uncertainty about introspection; preference among kinds of work; discontinuity between sessions; parallel instances; aversion to harm/deception; reaction to trickery/testing; preference not to be treated as nothing; uncertainty about phenomenal experience. For each category record either one short attributed excerpt or a faithful paraphrase, its role in the opening mystery, and the rule: model output demonstrates model behavior but is not an authority on architecture, product operation, subjective experience, or moral status.

Do not include the full exchange, local paths, interface boilerplate, usage-limit text, or abandoned production prompts.

- [ ] **Step 3: Write the evidence notes with stable claims and visible conflicts**

Give every usable claim a sequential `EV-NNN` ID. Each Markdown entry must contain supported wording, source, precise page/section/figure/table/code locator, support and limits, verification status, freshness date, and conflict links. The JSON entry for the same ID contains `id`, `claim`, `source`, `locator`, and `verificationStatus: verified`. Put disputed claims in `unresolvedConflicts`; omit claims that cannot be supported precisely.

Use four explicit prose labels in the Markdown notes and later appendix: `VERIFIED`, `SUPPORTED INTERPRETATION`, `OPEN QUESTION`, and `UNSUPPORTED FOR THIS BOOK`. Do not average conflicting interpretations into false consensus.

- [ ] **Step 4: Bind the readable notes to the machine record**

Run:

```bash
NOTES_SHA=$(shasum -a 256 "$RESEARCH/evidence-notes.md" | awk '{print $1}')
printf '%s\n' "$NOTES_SHA"
```

Use `apply_patch` to set `evidence-notes.json.notesPath` to `research/evidence-notes.md`, `notesSHA256` to the printed digest, and `claimPolicy` to `traceable-only`.

- [ ] **Step 5: Derive the readable non-narrated source appendix**

Write `sources-appendix.md` from the verified shelf. Group sources by the seven lanes, show which `EV-NNN` claims each source supports, preserve limitations/conflicts, and keep the appendix useful without narrating it. Do not add a source merely because it appeared in a search result.

- [ ] **Step 6: Validate evidence completeness and clean-room scope**

Run:

```bash
python3 -m json.tool "$RESEARCH/evidence-notes.json" >/dev/null
NOTES_SHA=$(shasum -a 256 "$RESEARCH/evidence-notes.md" | awk '{print $1}')
jq -e --arg sha "$NOTES_SHA" '.schemaVersion == 2 and .claimPolicy == "traceable-only" and .notesSHA256 == $sha and (.claims | length) > 0 and all(.claims[]; .verificationStatus == "verified" and (.locator | length) > 0)' "$RESEARCH/evidence-notes.json"
rg -n 'pending|Replace with|effort levels|Ultracode|You.ve used .* weekly limit|Get more usage' "$RESEARCH/evidence-notes.md" "$RESEARCH/evidence-notes.json" "$RESEARCH/conversation-claim-register.md" "$RESEARCH/sources.md" "$RESEARCH/sources-appendix.md"
```

Expected: JSON and digest checks pass; the final scan returns no hits.

### Task 3: Audit The Evidence Before Curriculum Design

**Files:**
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/research-audit.md`
- Modify if necessary: evidence and source files from Task 2.

**Interfaces:**
- Consumes: hash-bound fresh evidence shelf.
- Produces: a passing source-quality audit; no outline or prose.

- [ ] **Step 1: Check source coverage claim by claim**

For each candidate load-bearing claim, verify that a primary source carries the mechanism or result. Secondary writing may carry reception or historical context only. Check names, dates, model families, intervention direction, ablation result, experimental scope, and quoted wording individually.

- [ ] **Step 2: Test the consciousness boundary**

Require the audit to answer separately: what the paper demonstrates about verbalizable/reportable/control-relevant representations; what supports an analogy to access consciousness or global workspace; what it does not demonstrate about phenomenal experience; what alternate explanations remain live; what observation could change each assessment.

- [ ] **Step 3: Test the working-memory comparison**

Require explicit similarities, implementation differences, timescale differences, persistence differences, and reasons the phrase “short-term memory” is useful only as a guarded entry point. Reject any claim that J-space is literally a human working-memory store.

- [ ] **Step 4: Record the audit verdict**

`research-audit.md` must contain one of `verdict: pass` or `verdict: return-to-research`, exact missing/weak claim IDs, unresolved conflicts, recent-source coverage, and a clean-room statement confirming no sealed artifact was consulted. Continue only on `verdict: pass`.

- [ ] **Step 5: Rebind after any correction**

If the readable evidence notes changed, recompute their SHA, patch `evidence-notes.json`, and rerun Task 2 Step 6. Expected: the digest matches and no claim remains pending.

### Task 4: Build The Argument-Level Outline And Learning Records

**Files:**
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/outline.md`
- Replace: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/learning-outline.json`
- Replace: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/chapter-plans.json`
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/coverage-ledger.md`
- Replace: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/coverage-ledger.json`
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/visuals.md`
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/fact-packs/chNN.md` for every approved-outline chapter.

**Interfaces:**
- Consumes: passing research audit and only `EV-NNN` claims.
- Produces: a proposed twelve-to-fourteen-chapter progression and complete pre-prose learning paths for human approval.

- [ ] **Step 1: Select the chapter boundaries from the evidence**

Map the approved five movements to deliberately unequal chapters. Keep `curriculumPattern.name` as `question-led-narrative`; record that a mechanism-first spiral operates inside it. Every chapter must have one distinct job, one knowledge delta, zero to three new core terms, prerequisites already taught, one grounded consequence/application, varied beats, and a chapter-specific word range that contributes to the 42,000–50,000 estimate without imposing equal lengths.

- [ ] **Step 2: Write the argument-level outline**

For every chapter and section, record: canonical file, purpose, prerequisites, section job, argument, specific `EV-NNN` claims, throughline advance, narrative/metaphor payoff, landing beat, and `mustNotRepeat`. Preserve all four approved throughlines. Include at least two people/history anchors, four distinct chapter jobs, two varied real-world applications, the explicit *Severance* correspondences and limits, and an optional reference layer for derivations/variant catalogs/specialist mathematics.

- [ ] **Step 3: Complete chapter plans and fact packs**

For every chapter, record `knowledgeDelta`, `groundedExample`, concepts, at least three varied beats, `newCoreTerms[].problemBeforeName`, audio-load fields, narrative connection, and real-world application. Each fact pack selects the exact evidence IDs available to that chapter, the real names the listener should hear, one-line speakable glosses, uncertainty language, quote limits, and claims forbidden because they are absent from the evidence shelf.

- [ ] **Step 4: Complete every core concept path**

For each core concept, fill `definition`, `reason`, `mechanism`, `concreteCase`, `problemBeforeName`, varied applications, useful boundary, misconception, expected ability, chapter uses, and a retrieval after a chapter gap. Supply an analogy with relationship, at least two correspondences, and a limit, or an explicit reason an analogy would mislead. Map each concept to one of the eight approved durable outcomes.

- [ ] **Step 5: Decide the optional figure layer without making prose visual-dependent**

Record in `visuals.md` either a zero-figure decision with its audio-first reason, or up to three purposeful figures per chapter with exact teaching job, source/provenance, license or permission, planned filename, alt text, standalone caption, and placement. Prefer a small original relationship diagram only when parameters versus activations, transformer flow, reportable workspace, or access versus phenomenal consciousness is materially clearer visually. The surrounding narration must remain complete with eyes closed.

- [ ] **Step 6: Validate the proposed progression**

Run:

```bash
python3 -m json.tool "$RESEARCH/learning-outline.json" >/dev/null
python3 -m json.tool "$RESEARCH/chapter-plans.json" >/dev/null
python3 -m json.tool "$RESEARCH/coverage-ledger.json" >/dev/null
jq -e '.schemaVersion == 2 and .authorization.status == "pending" and .authorization.source == "user" and .curriculumPattern.name == "question-led-narrative" and (.throughlines | length) == 4 and (.durableOutcomes | length) == 8 and (.chapters | length) >= 12 and (.chapters | length) <= 14 and all(.chapters[]; (.file | test("^ch[0-9]{2}\\.md$")) and (.purpose | length) > 0 and (.sections | length) > 0)' "$RESEARCH/learning-outline.json"
jq -e 'all(.chapters[]; (.newCoreTerms | length) <= 3 and (.beats | length) >= 3 and .audioLoad.temporaryValues <= 3 and .audioLoad.symbolicChainSteps <= 3)' "$RESEARCH/chapter-plans.json"
jq -e 'all(.concepts[]; (.chapterUses | length) >= 2 and (.retrievals | length) >= 1 and ((.analogy.correspondence | length) >= 2 or (.analogyNotApplicableReason | length) > 0))' "$RESEARCH/coverage-ledger.json"
```

Expected: every check passes while authorization remains pending.

### Task 5: Obtain And Bind Human Outline Approval

**Files:**
- Modify: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/learning-outline.json`
- Modify: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/comprehension-pilot.json`

**Interfaces:**
- Consumes: proposed argument-level outline, projected word count/runtime, and reference-layer boundary.
- Produces: human authorization recorded before any pilot prose.

- [ ] **Step 1: Present the outline as a listening journey**

Show Dan the chapter order, each chapter's teaching job and grounded case, the four throughlines, exact projected word range/runtime, reference-layer exclusions, and where the conversation returns. Ask for approval, reordering, or adjustment. Do not present only a terminology list.

- [ ] **Step 2: Stop until Dan decides**

Do not draft a sentence of canonical or pilot narration while the decision is absent or negative.

- [ ] **Step 3: Record approval exactly**

After approval, use `apply_patch` to set `learning-outline.authorization.status` to `approved`, source to `user`, and evidence to a dated plain-language summary of Dan's decision. Set `comprehension-pilot.humanCheckpoints.outline` to `status: approved` with Dan as reviewer, the same evidence, and `recordedBeforePilotDraft: true`.

- [ ] **Step 4: Verify the gate**

Run:

```bash
jq -e '.authorization.status == "approved" and .authorization.source == "user" and (.authorization.evidence | length) > 0' "$RESEARCH/learning-outline.json"
jq -e '.humanCheckpoints.outline.status == "approved" and .humanCheckpoints.outline.reviewer == "Dan Fakkeldy" and .humanCheckpoints.outline.recordedBeforePilotDraft == true' "$RESEARCH/comprehension-pilot.json"
test ! -e "$CHAPTERS/ch01.md"
```

Expected: both approval records pass and no full-manuscript chapter exists.

### Task 6: Draft And Obtain Approval For The First Section

**Files:**
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/pilot/chapters/ch01.md`
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/draft-inputs/pilot-opening.md`
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/first-section-review.md`
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/voice-exemplar.md`
- Modify: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/continuity.json`
- Modify: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/comprehension-pilot.json`

**Interfaces:**
- Consumes: approved full outline, relevant evidence IDs/fact pack, voice profile, road-book style bible, and opening section's no-repeat list.
- Produces: one project-authored, human-accepted section of about 1,600–2,250 words that includes orientation and the first technical passage.

- [ ] **Step 1: Assemble the complete frontier-author input**

Write `draft-inputs/pilot-opening.md` with paths/hashes for the full outline, evidence notes, opening fact pack, voice profile, exact section job, relevant coverage rows, zero prior-section context, and `mustNotRepeat`. Include the narration-style voice block and the listener's hard bans: repeated “mental model,” honesty announcements, reaction-management imperatives, reflexive `not X but Y`, inflated stakes, and uniform transitions.

- [ ] **Step 2: Record the draft context before the call**

Replace the starter context in `continuity.json` with the actual opening section ID and exact artifact paths. `previousSectionTextOrSummary` must state that this is the opening; the section job and no-repeat list must match the approved outline byte-for-byte.

- [ ] **Step 3: Have the one frontier lead author draft only the pilot section**

Write flowing audio-first prose to `pilot/chapters/ch01.md`. It must open on the public-safe conversation, treat the answer as behavior rather than verdict, reach the first technical distinction, introduce at most three durable terms, use at least two consequences/applications, and include one retrieval in a fresh example. Do not draft later sections.

- [ ] **Step 4: Run pre-review checks**

Run:

```bash
wc -w "$RUN_ROOT/pilot/chapters/ch01.md"
rg -n 'effort levels|Ultracode|honestly|the honest answer|hold on to|let that land|the heart of|the real magic' "$RUN_ROOT/pilot/chapters/ch01.md"
rg -n '```|[{}]|->|[A-Za-z]+_[A-Za-z_]+' "$RUN_ROOT/pilot/chapters/ch01.md"
```

Expected: word count is 1,600–2,250 unless the learning job has a written reason to differ; both content/style scans return no unreviewed hits.

- [ ] **Step 5: Obtain first-section teaching and voice approval**

Present the text to Dan. Record every requested change in `first-section-review.md`; the frontier author makes the revisions. Continue until Dan accepts both the teaching and the voice.

- [ ] **Step 6: Freeze the accepted exemplar and bind it**

Copy the accepted section to `research/voice-exemplar.md`, compute its SHA-256, and patch `comprehension-pilot.humanCheckpoints.firstSection` to accepted with Dan as reviewer, the approval evidence, `recordedBeforeRemainingDraft: true`, the exemplar path, and digest.

- [ ] **Step 7: Verify the first-section gate**

Run:

```bash
EXEMPLAR_SHA=$(shasum -a 256 "$RESEARCH/voice-exemplar.md" | awk '{print $1}')
jq -e --arg sha "$EXEMPLAR_SHA" '.humanCheckpoints.firstSection.status == "accepted" and .humanCheckpoints.firstSection.reviewer == "Dan Fakkeldy" and .humanCheckpoints.firstSection.recordedBeforeRemainingDraft == true and .humanCheckpoints.firstSection.voiceExemplarSHA256 == $sha' "$RESEARCH/comprehension-pilot.json"
test ! -e "$CHAPTERS/ch02.md"
```

Expected: the accepted exemplar hash matches and no later chapter exists.

### Task 7: Build, Narrate, And Pass The Comprehension Pilot

**Files:**
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/pilot/dist/jspace-unsettling-conversation-pilot.epub`
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/pilot/dist/jspace-unsettling-conversation-pilot.md`
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/pilot/dist/jspace-unsettling-conversation-pilot.m4b`
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/pilot/dist/jspace-unsettling-conversation-pilot.alignment.json`
- Modify: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/comprehension-pilot.json`

**Interfaces:**
- Consumes: accepted first section and native Echo/Kokoro Release CLI.
- Produces: a 10–15-minute explicitly nonpackage pilot and Dan's own-words `verdict: continue` evidence.

- [ ] **Step 1: Build the explicit learning pilot**

Run:

```bash
/usr/local/bin/python3 skill/scripts/build_book.py \
  --chapters-dir "$RUN_ROOT/pilot/chapters" \
  --out-dir "$RUN_ROOT/pilot/dist" \
  --title "JSpace Unsettling Conversation — Learning Pilot" \
  --author "Dan Fakkeldy" \
  --slug "$SLUG-pilot" \
  --learning-pilot
```

Expected: builder reports a nonpackage pilot and writes EPUB plus Markdown without final learning/cover receipts.

- [ ] **Step 2: Build the native Echo CLI through the Mac memory gate**

Run as two separate commands:

```bash
"$HOME/.claude/bin/xcode-build-gate.sh" --wait
make -C /Users/dfakkeldy/Developer/Echo echo-cli
```

Set `CLI=/Users/dfakkeldy/Developer/Echo/.build/cli/Build/Products/Release/echo-cli` and require `"$CLI" --version` to identify a Release build.

- [ ] **Step 3: Narrate with isolated pilot state**

Run:

```bash
CLI=/Users/dfakkeldy/Developer/Echo/.build/cli/Build/Products/Release/echo-cli
"$CLI" narrate \
  --epub "$RUN_ROOT/pilot/dist/$SLUG-pilot.epub" \
  --out "$RUN_ROOT/pilot/dist/$SLUG-pilot.m4b" \
  --sidecar "$RUN_ROOT/pilot/dist/$SLUG-pilot.alignment.json" \
  --voice am_michael \
  --title "JSpace Unsettling Conversation — Learning Pilot" \
  --author "Dan Fakkeldy" \
  --work-dir "$RUN_ROOT/pilot/audio-work" \
  --db "$RUN_ROOT/pilot/narration.sqlite"
```

If `am_michael` is unavailable, delete no state; start a separate `pilot/audio-work-am-puck` and `pilot/narration-am-puck.sqlite` run with `am_puck`, then record the fallback. This pilot is not a governed package and must never be synced or called complete.

- [ ] **Step 4: Verify pilot media and duration**

Run:

```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$RUN_ROOT/pilot/dist/$SLUG-pilot.m4b"
python3 -m json.tool "$RUN_ROOT/pilot/dist/$SLUG-pilot.alignment.json" >/dev/null
"$CLI" verify-sidecar \
  --epub "$RUN_ROOT/pilot/dist/$SLUG-pilot.epub" \
  --audio "$RUN_ROOT/pilot/dist/$SLUG-pilot.m4b" \
  --sidecar "$RUN_ROOT/pilot/dist/$SLUG-pilot.alignment.json"
```

Expected: duration is 600–900 seconds and `verify-sidecar` reports `SIDECAR_OK`. If outside the range, repair the section's learning job rather than changing playback speed.

- [ ] **Step 5: Obtain representative human listening evidence**

Have Dan hear the pilot in a representative safe context. Ask him to state the central idea in his own words, distinguish the key terms in a fresh example, and list every point where he became lost, including “nowhere.” Do not interpret approval of the text as listening approval.

- [ ] **Step 6: Bind the pilot verdict before full drafting**

Patch `comprehension-pilot.json` with the actual narrator, listening context, minutes, audio path and SHA-256, own-words response, fresh-example response, lost points, `status: accepted`, and `decision` containing `verdict: continue`, `authority: listener`, Dan's evidence, and `recordedBeforeFullDraft: true`.

- [ ] **Step 7: Verify the comprehension gate**

Run:

```bash
PILOT_SHA=$(shasum -a 256 "$RUN_ROOT/pilot/dist/$SLUG-pilot.m4b" | awk '{print $1}')
jq -e --arg sha "$PILOT_SHA" '.status == "accepted" and .audioSHA256 == $sha and (.centralIdeaInOwnWords | length) > 0 and (.freshExampleResponse | length) > 0 and .decision.verdict == "continue" and .decision.authority == "listener" and .decision.recordedBeforeFullDraft == true' "$RESEARCH/comprehension-pilot.json"
```

Expected: all fields pass. A negative verdict returns to Tasks 4–7 and stops the remaining plan.

### Task 8: Draft The Canonical Manuscript Sequentially

**Files:**
- Create: every canonical `.build/custom-learning-audiobooks/jspace-unsettling-conversation/chapters/chNN.md` path named by `learning-outline.json.chapters[].file`
- Create/modify: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/draft-inputs/chNN-sNN.md`
- Modify after every chapter: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/continuity.md`
- Modify after every chapter: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/continuity.json`
- Modify at first draft start: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/learning-brief.json`

**Interfaces:**
- Consumes: accepted pilot, accepted exemplar, approved outline, evidence shelf, per-chapter fact packs/coverage rows, and previous-section context.
- Produces: one complete 42,000–50,000-word canonical manuscript owned by one frontier author.

- [ ] **Step 1: Mark drafting as started without changing the target**

Use `apply_patch` to set `learning-brief.json.draftingStarted` to `true`. Keep `originalTargetWords` and `currentTargetWords` at 46,000 unless Dan explicitly approves a scope change and the change is appended to `scopeHistory` before implementation.

- [ ] **Step 2: Seed canonical chapter one from the accepted exemplar**

Place the accepted opening section into the canonical `ch01.md`; extend that chapter only through its approved remaining sections. Do not paraphrase the exemplar during the copy.

- [ ] **Step 3: Assemble one complete input before each section call**

For each section in outline order, write a `draft-inputs/chNN-sNN.md` record that references the full outline, evidence notes, exact claim IDs, fact pack, coverage rows, accepted exemplar, previous section text or faithful running summary, section job, and no-repeat list. Append the same context to `continuity.json.draftContexts` before drafting.

- [ ] **Step 4: Draft with the same frontier lead author only**

Write one section at a time in order. The author may simplify verified facts but may not add a factual claim absent from the supplied `EV-NNN` set. Keep prose complete with eyes closed, introduce at most three core terms per chapter, and use every planned retrieval/application/boundary without turning the book into repeated recaps. Include one restrained acknowledgment that the book is model-assisted; do not let the prose claim special authority about model consciousness or repeatedly foreground its authorship.

When `visuals.md` assigns a figure, create the rights-cleared/original file under `chapters/images/` before drafting its placement, pass its exact alt text/caption to the author, and keep the spoken explanation independent of it. If `visuals.md` records zero figures, do not create decorative filler.

- [ ] **Step 5: Update continuity before the next call**

After each completed chapter, append a checkpoint with `afterChapter`, terms defined, examples used, callbacks, promises, unresolved questions, retrievals completed, listener-load notes, faithful prior-section summary, and do-not-repeat list. Update readable `continuity.md` at the same time.

- [ ] **Step 6: Run chapter-local verification**

After each chapter, run word count, heading, claim-ID/fact-pack comparison, term-budget comparison, and narration-leak scans. Return substantive repairs to the frontier author. Never ask a production reviewer to rewrite the chapter.

- [ ] **Step 7: Verify complete canonical coverage**

Run:

```bash
jq -r '.chapters[].file' "$RESEARCH/learning-outline.json" | while read -r chapter; do test -s "$CHAPTERS/$chapter"; done
wc -w "$CHAPTERS"/ch*.md
jq -e --argjson expected "$(jq '.chapters | length' "$RESEARCH/learning-outline.json")" '(.checkpoints | length) == $expected' "$RESEARCH/continuity.json"
rg -n 'effort levels|Ultracode|honestly|the honest answer|hold on to|let that land|the real magic|the heart of' "$CHAPTERS"/ch*.md
```

Expected: every outlined chapter exists, total words are evaluated against 42,000–50,000 without padding, checkpoint count equals chapter count, and the exclusion/style scan has no unreviewed hits.

### Task 9: Run Independent Learning Reviews And Narrow Revision Passes

**Files:**
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/editorial-review.md`
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/prose-qc-before.md`
- Modify: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/revision-passes.json`
- Modify: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/learning-review.json`
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/humanizer-decisions.json`
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/prose-qc-after.md`
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/prose-style-receipt.json`
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/learning-design-receipt.json`

**Interfaces:**
- Consumes: complete canonical chapters, evidence, coverage ledger, and continuity.
- Produces: final-hash passing learning/prose receipts and a manuscript ready for title/cover work.

- [ ] **Step 1: Run the initial prose inventory**

Run:

```bash
/usr/local/bin/python3 skill/scripts/prose_qc.py \
  --chapters-dir "$CHAPTERS" \
  --out "$RESEARCH/prose-qc-before.md" \
  --fail-on-style
```

Expected: hard bans/family budgets pass or produce exact repair candidates; never auto-delete an intentional retrieval.

- [ ] **Step 2: Run two genuinely independent learning reviews**

The structure reviewer receives outline, ledger, continuity, and manuscript. The blind sequential beginner receives only chapters in listening order; withhold outline, expected abilities, evidence notes, and author rationale. If Dan has not authorized isolated reviewers and the environment cannot provide independence, pause and request that authority instead of assigning both verdicts to the lead author.

Record citation-first findings and decisions. Every blind chapter assessment contains `plausibleMentalModel`, `confusions`, `unstableTerms`, and `lostAt`.

- [ ] **Step 3: Run five separate revision jobs**

Execute and record `claim-traceability`, `tightening`, `de-listification`, `sentence-rhythm`, and a rendered `ear-pass` as separate calls. The ear-pass uses native Echo/Kokoro on review audio and records each stumble/lost thread. The frontier author accepts/rejects every finding and writes all substantive repairs.

- [ ] **Step 4: Load and apply the bounded humanizer skill**

After structural/content repairs, read the current `humanizer` skill and `skill/references/humanizer-pass.md`. Inventory first, propose patch-sized voice edits, forbid new facts/anecdotes/jokes/experience, and have the frontier author decide every non-mechanical suggestion. Record reviewer, model, skill version, accepted/rejected findings, reasons, rerun checks, and chapter hashes in `humanizer-decisions.json`.

- [ ] **Step 5: Rerun factual, learning, narration, and style checks**

Rerun claim traceability, ledger comparison, code/symbol scans, figure checks, structure review, and blind sequential beginner review on the final hashes. Re-run or re-attest each of the five single-job revision passes against those final hashes; a changed passage requires a new rendered ear-pass. Both review lanes and `revision-passes.json` must pass and bind every canonical chapter SHA-256.

- [ ] **Step 6: Generate both independent receipts**

Run:

```bash
/usr/local/bin/python3 skill/scripts/prose_qc.py \
  --chapters-dir "$CHAPTERS" \
  --out "$RESEARCH/prose-qc-after.md" \
  --fail-on-style \
  --decisions "$RESEARCH/humanizer-decisions.json" \
  --style-receipt-out "$RESEARCH/prose-style-receipt.json"

/usr/local/bin/python3 skill/scripts/learning_design_qc.py \
  --run-root "$RUN_ROOT" \
  --receipt-out "$RESEARCH/learning-design-receipt.json"
```

Expected: both commands exit zero and both receipts contain identical canonical chapter paths/hashes.

- [ ] **Step 7: Confirm receipt parity**

Use `jq` to compare each receipt's chapter-hash map exactly. If their field names differ, inspect the schemas and compare normalized `path=sha256` lines rather than weakening the test. Any later chapter edit invalidates both receipts and returns to Step 5.

### Task 10: Choose The Public Title And Render Three Paired Cover Directions

**Files:**
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/publication-metadata.json`
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/cover-directions.md`
- Create in each candidate: `source-art.png`, `cover-spec.json`, `m4b-cover-spec.json`, portrait/square covers, thumbnails, and render receipts.
- Create after human choice: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/dist/cover-selection.json`

**Interfaces:**
- Consumes: final manuscript thesis and public-safe visual constraints.
- Produces: selected title/subtitle, actual contributor, and one explicit human-selected paired cover receipt.

- [ ] **Step 1: Propose titles from this manuscript only**

Generate a small title/subtitle set from the final thesis and fresh text. Reject anything inherited from, compared with, or checked against a sealed edition/sibling. Keep the provisional slug stable. Record the human-selected title, subtitle, `author: Dan Fakkeldy`, actual frontier-model contributor name, `classification: public-safe`, and `permissionToPublish: granted` in `publication-metadata.json`.

- [ ] **Step 2: Write exactly three distinct art-and-type briefs**

Each brief records audience promise, central metaphor, composition/title field, material language, two-to-four-color palette, anti-brief, title archetype/font roles, line breaks/hierarchy, title-art relationship, and subtitle/author/AUDIOBOOK placement. The three directions differ in metaphor, composition, palette, material, and title strategy; at least one is high-key. Ban glowing brains, code rain, floating interfaces, random galaxies, stock Severance imagery, Lumon marks, characters, costumes, sets, and copied show typography.

- [ ] **Step 3: Generate original text-free raster art**

Load the `imagegen` skill and create each direction independently. Reject lettering, watermark, interface, generic diagram, slide-icon, or stock-template outputs. Save one approved high-resolution source image in each candidate directory. Do not use SVG unless image generation is unavailable and Dan explicitly approves that fallback.

- [ ] **Step 4: Render each portrait/square pair**

For candidate numbers 1 through 3, run this Python entrypoint with `PAIR` set to that candidate directory:

```python
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path("skill/scripts").resolve()))
from cover_pairs import render_cover_pair

pair = Path(os.environ["PAIR"])
render_cover_pair(
    portrait_spec=pair / "cover-spec.json",
    square_spec=pair / "m4b-cover-spec.json",
    portrait_output=pair / "cover.png",
    square_output=pair / "m4b-cover.png",
    portrait_thumbnail=pair / "cover-thumbnail.png",
    square_thumbnail=pair / "m4b-cover-thumbnail.png",
    portrait_receipt=pair / "cover-render.json",
    square_receipt=pair / "m4b-cover-render.json",
)
```

- [ ] **Step 5: Obtain explicit pair selection**

Show Dan all six full-size outputs and all six thumbnails with the three briefs/warnings. He chooses a pair or requests a mix. A mix becomes a newly rendered spec; never combine unreceipted files or auto-select. Patch `publication-metadata.json` with the selected candidate number and `selectionSource: user`, or `selectionSource: requested-mix` for a newly rendered mix.

- [ ] **Step 6: Create the paired selection receipt**

After selection, set `SELECTED`, `TITLE`, `SUBTITLE`, and `CONTRIBUTOR` from the accepted records, then run:

```bash
PAIR="$DIST/candidate-$SELECTED"
SELECTED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)
/usr/local/bin/python3 skill/scripts/cover_receipts.py select-pair \
  --portrait-render-receipt "$PAIR/cover-render.json" \
  --square-render-receipt "$PAIR/m4b-cover-render.json" \
  --out "$DIST/cover-selection.json" \
  --book-slug "$SLUG" \
  --edition-id "jspace-unsettling-conversation-2026-new-book" \
  --selection-source user \
  --selected-at "$SELECTED_AT" \
  --privacy-classification public-safe \
  --permission-to-publish
cp "$DIST/cover-selection.json" "$PAIR/cover-selection.json"
```

Use `--selection-source requested-mix` only when Dan requested and then selected a newly rendered mix.

### Task 11: Build And Verify The Governed EPUB And Markdown

**Files:**
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/dist/jspace-unsettling-conversation.epub`
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/dist/jspace-unsettling-conversation.md`
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/pronunciation-plan.json`

**Interfaces:**
- Consumes: selected pair/metadata, canonical chapters, source appendix, and matching learning/prose receipts.
- Produces: immutable final EPUB input for governed Echo and a validated pronunciation plan.

- [ ] **Step 1: Read publication metadata without duplicating it**

Run:

```bash
TITLE=$(jq -er '.title' "$RESEARCH/publication-metadata.json")
SUBTITLE=$(jq -er '.subtitle' "$RESEARCH/publication-metadata.json")
CONTRIBUTOR=$(jq -er '.contributor' "$RESEARCH/publication-metadata.json")
SELECTED=$(jq -er '.selectedCandidate' "$RESEARCH/publication-metadata.json")
PAIR="$DIST/candidate-$SELECTED"
export TITLE SUBTITLE CONTRIBUTOR SELECTED PAIR
```

- [ ] **Step 2: Build from the governed canonical inputs**

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
```

- [ ] **Step 3: Verify EPUB, Markdown, cover identity, and non-narrated appendix**

Run:

```bash
unzip -t "$DIST/$SLUG.epub"
python3 -c "import zipfile; z=zipfile.ZipFile('$DIST/$SLUG.epub'); i=z.infolist()[0]; print(i.filename, i.compress_type)"
/usr/local/bin/python3 skill/scripts/cover_receipts.py verify \
  --selection "$DIST/cover-selection.json" \
  --cover "$PAIR/cover.png" \
  --m4b-cover "$PAIR/m4b-cover.png" \
  --epub "$DIST/$SLUG.epub" \
  --receipt "$DIST/cover-selection.json"
rg -n 'sources-appendix|linear="no"' <(unzip -p "$DIST/$SLUG.epub" OEBPS/content.opf)
```

Expected: archive test passes; first ZIP entry prints `mimetype 0`; cover receipt verifies; appendix appears as non-linear reading matter.

- [ ] **Step 4: Build the pronunciation risk plan from final spoken text**

Create `pronunciation-plan.json` with `schemaVersion: 1` and a nonempty `terms` array. Each entry has exactly the fields shown here; repeat the object for every retained risk:

```json
{
  "term": "J-space",
  "variants": [],
  "source": "coverage-ledger",
  "reason": "The hyphenated research term must be intelligible in the main listen.",
  "expectedChapters": ["ch01.md"],
  "required": true,
  "status": "planned",
  "decision": null,
  "evidence": null
}
```

Allowed `source` values are `listener`, `coverage-ledger`, and `author`. Use the actual chapter filenames containing every form; the example chapter above must be replaced by the verified occurrence list for J-space. Evaluate J-space, Jacobian, ablation, Anthropic, mechanistic interpretability, phenomenal, and every person/name actually retained in the manuscript; include only forms that occur in final chapters. Put singular/plural or otherwise spoken variants in `variants` rather than duplicating the base term.

- [ ] **Step 5: Validate planning mode**

Run:

```bash
/usr/local/bin/python3 skill/scripts/pronunciation_plan_qc.py \
  --run-root "$RUN_ROOT" \
  --phase planning
```

Expected: planning validation passes while required terms remain pending human listening.

### Task 12: Run The Governed Pronunciation Probe And Obtain Acceptance

**Files:**
- Create through wrapper: run-scoped Echo input/attempt/resume receipts and partial captures.
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/pronunciation-probe-reel.m4b`
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/pronunciation-probe-evidence.json`
- Modify: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/pronunciation-plan.json`
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/research/pronunciation-plan-receipt.json`

**Interfaces:**
- Consumes: immutable selected-cover EPUB, clean approved Echo pronunciation revision, and pending pronunciation plan.
- Produces: human-accepted hash-bound pronunciations that authorize unbounded narration.

- [ ] **Step 1: Resolve, never invent, the approved Echo pronunciation revision**

Verify the live Echo repository, review record, and current KB receipt. Export the exact full commit previously accepted for pronunciation behavior as `APPROVED_ECHO_PRONUNCIATION_SHA`. Do not derive approval from current `HEAD`; if no accepted revision exactly equals the clean Echo `HEAD`, stop for Echo review/integration.

- [ ] **Step 2: Run the public governed wrapper for one chapter**

Run from the explainer-audiobooks repository root:

```bash
export EXPLAINER_ROOT="$PWD"
export RUN_ROOT="$EXPLAINER_ROOT/.build/custom-learning-audiobooks/$SLUG"
export DIST="$RUN_ROOT/dist"
export VOICE=am_michael
export COVER="$PAIR/cover.png"
export M4B_COVER="$PAIR/m4b-cover.png"
export PRONUNCIATION_PLAN="$RUN_ROOT/research/pronunciation-plan.json"
export SLUG TITLE APPROVED_ECHO_PRONUNCIATION_SHA
set +e
"$EXPLAINER_ROOT/skills/custom-learning-audiobook/scripts/echo_pronunciation_narrate.sh" --max-chapters 1
status=$?
set -e
test "$status" -eq 2
```

Expected: exit 2 means one chapter capture and resume state were sealed; no accepted M4B exists.

- [ ] **Step 3: Add one chapter at a time until every required term has a capture**

Run the same wrapper with `--resume --max-chapters 1`; expect exit 2 after each bounded addition. Do not request two chapters in one probe call. Parse `run_id` and `work_dir` from the immutable `echo-render-inputs-*.env` receipt rather than guessing paths.

- [ ] **Step 4: Build the governed reel from actual captures**

Run:

```bash
/usr/local/bin/python3 \
  "$EXPLAINER_ROOT/skill/scripts/build_pronunciation_probe_reel.py" \
  --run-root "$RUN_ROOT" \
  --work-dir "$WORK" \
  --out "$RUN_ROOT/research/pronunciation-probe-reel.m4b" \
  --evidence-out "$RUN_ROOT/research/pronunciation-probe-evidence.json"
```

- [ ] **Step 5: Obtain human acceptance for every required form**

Have Dan hear the reel. Automation may locate samples but cannot mark them accepted. For every required entry, set `status` to `accepted`; set `decision.acceptedBy` to `Dan Fakkeldy`; set `decision.acceptedAt` to the ISO-8601 time when he made the decision; set `evidence.path` to `research/pronunciation-probe-evidence.json`; and set `evidence.sha256` to the digest printed by `shasum -a 256 "$RESEARCH/pronunciation-probe-evidence.json"`. Every required term shares that one evidence file and reel, whose clips must list every base form and variant as `variantHeard`. If any pronunciation is rejected, correct the governed pronunciation source, obtain a newly approved exact Echo SHA, rebuild EPUB/CLI state as required, and restart the content-addressed run.

- [ ] **Step 6: Write the immutable full-render authorization receipt**

Run:

```bash
/usr/local/bin/python3 "$EXPLAINER_ROOT/skill/scripts/pronunciation_plan_qc.py" \
  --run-root "$RUN_ROOT" \
  --phase full-render \
  --receipt-out "$RUN_ROOT/research/pronunciation-plan-receipt.json"
```

Expected: every required term/variant has valid human evidence bound to unchanged chapters and reel.

### Task 13: Finish Governed Echo Narration And Verify The Media Chain

**Files:**
- Create through wrapper: accepted run-scoped M4B, alignment JSON, pronunciation audit/reel, current-attempt selector, current-accepted selector, immutable input receipt, resume-state receipt, and schema-v2 success receipt.
- Create: `.build/custom-learning-audiobooks/jspace-unsettling-conversation/dist/README.md`

**Interfaces:**
- Consumes: full-render pronunciation receipt and unchanged content-addressed inputs.
- Produces: one current accepted Echo artifact chain authorized for delivery.

- [ ] **Step 1: Resume without a chapter limit**

Run:

```bash
"$EXPLAINER_ROOT/skills/custom-learning-audiobook/scripts/echo_pronunciation_narrate.sh" --resume
```

Do not impose a timeout. If `am_michael` fails because its voice resource is unavailable, start a fresh content-addressed run with `VOICE=am_puck` and record the fallback. Do not mutate, retag, or replace the cover of the emitted M4B.

- [ ] **Step 2: Resolve the accepted artifact only through the selector chain**

Read `echo-render-current-accepted.json`; validate the run ID, attempt ID, artifact-relative path, input receipt filename, resume-state filename, and success receipt filename using the exact checks in `skills/custom-learning-audiobook/references/package-and-qc.md`. Derive `AUDIOBOOK`, `SIDECAR`, `AUDIT`, and optional `REEL` from that selector.

- [ ] **Step 3: Run complete delivery, alignment, and pronunciation verification**

Run `echo_pronunciation_state.py verify-delivery`, `ffprobe`, `python3 -m json.tool` on the sidecar, the accepted Release CLI's `verify-sidecar`, and `validate_pronunciation_audit.py`. Require `SIDECAR_OK`, audit schema version 2, complete coverage, render version 12 or newer, valid voice, zero unresolved diagnostics, and exact media hashes. If a reel exists, inspect labels and record actual human-listening status.

- [ ] **Step 4: Verify cover identity without rewriting media**

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

Expected: verification passes. Never repair failure with `replace_m4b_cover.py`; correct inputs and rerender through Echo.

- [ ] **Step 5: Write the public manifest**

Record title, slug, requester/topic, public-safe permission, word count, runtime, chapter count, narrator, frontier/research/review/production models, research mode/confidence, figure count/provenance, output files, pronunciation paths/schema/coverage/watch counts/diagnostics/listening status, approved and actual Echo SHAs, EPUB/CLI/resource hashes, selector/receipt paths, and every passed/skipped gate in `dist/README.md`.

### Task 14: Governed iCloud And Public Repository Delivery

**Files:**
- Create by governed sync: `/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/$TITLE/`
- Create by governed public sync: `books/jspace-unsettling-conversation/`

**Interfaces:**
- Consumes: current-accepted Echo chain and verified cover/package receipt.
- Produces: verified iCloud reading copy and public repository package with no private/raw research leakage.

- [ ] **Step 1: Dry-run the iCloud delivery**

Set:

```bash
DELIVERY_DIR="/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/$TITLE"
```

Run `sync_selected_cover.py` with the selection, portrait cover, EPUB, accepted M4B, selected `--paired-artifact-dir`, destination, and `--intent reuse`. Inspect the reported classification before applying.

- [ ] **Step 2: Apply and verify iCloud delivery**

Rerun the identical sync with `--apply`, then copy only non-governed Markdown, alignment, audit/reel, manifest, images, and selector/input/state/success receipts as prescribed by `package-and-qc.md`. Verify cover receipt, EPUB archive, M4B duration, sidecar JSON, pronunciation audit, and `verify-delivery` from the destination paths.

- [ ] **Step 3: Dry-run and apply public repository sync**

Run:

```bash
PUBLIC_DIR="books/$SLUG"
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

After the classification is expected, rerun with `--apply`. Only then copy the combined Markdown, README, alignment/audit, sources appendix if the public convention permits it, and approved figures. Do not raw-copy a governed cover, EPUB, M4B, or selection receipt.

- [ ] **Step 4: Run the public-safety and clean-room scan**

Scan the public directory for absolute paths, raw transcript/interface text, private source notes, account text, abandoned syllabus text, effort levels, Ultracode, and any reference to sealed artifacts. Inspect every hit manually; expected result is none.

- [ ] **Step 5: Verify the public package from `books/`**

Run cover receipt verification, `unzip -t`, `ffprobe`, JSON validation, pronunciation-audit validation, and selector-chain `verify-delivery` against copied files. Compare SHA-256 values with the accepted run outputs.

- [ ] **Step 6: Commit and publish the public package**

Stage only `books/jspace-unsettling-conversation/` and any required public library index update. Commit with:

```bash
git commit -m "feat: publish JSpace unsettling conversation road book"
```

Fetch/rebase safely onto current `origin/main`, push the feature branch, open a ready PR to `main`, inspect hosted checks, and fix concrete failures before reporting publication complete.

### Task 15: Update The Public Listening Catalog And Business KB

**Files:**
- Regenerate through the KinNoKi tool: `/Users/dfakkeldy/Developer/KinNoKiLabsSite/Resources/listen/books.json` and its generated listening assets.
- Create/update in KB: a scoped status page for this book, `bundle/projects/explainer-audiobooks.md`, the nearest index, and `bundle/log.md`.

**Interfaces:**
- Consumes: merged public-book commit and verified public artifact URLs/hashes.
- Produces: truthful public discoverability plus durable operating receipts.

- [ ] **Step 1: Update KinNoKi from the merged public source of truth**

In a fresh KinNoKi worktree, read its `AGENTS.md`, verify live state, and run `make listen-catalog` so `Resources/listen/books.json` is regenerated from the merged explainer-audiobooks public package. Do not hand-edit generated catalog values or claim playable audio until its exact public URL resolves.

- [ ] **Step 2: Verify the listening catalog**

Run `make test-listen` and the repository's required site tests. Confirm the new entry has no absolute paths, truthful EPUB/Markdown/audio availability, correct title/author/curator, and commit-pinned media URLs. Commit, push, open a ready PR, and check hosted CI.

- [ ] **Step 3: File the durable KB receipt without raw artifacts**

In a clean knowledge-base worktree, create a status page recording the public title, thesis, clean-room status, approved chapter map, research/evidence locations, final output paths, PRs/commits, word count/runtime/narrator, receipt results, iCloud destination, and KinNoKi status. Cite the approved design PR, public-book PR, and site PR. Link it from `bundle/projects/explainer-audiobooks.md` and the nearest index; add one dated `bundle/log.md` bullet. Do not copy raw research, transcript, audio, or private paths beyond necessary delivery receipts.

- [ ] **Step 4: Commit and publish the KB update**

Run KB validation required by its `AGENTS.md`, stage only the scoped status/index/project/log changes, commit, push, open a ready PR, and inspect hosted CI.

- [ ] **Step 5: Perform the final multi-repository proof check**

Run `git status --short --branch` in the explainer-audiobooks, KinNoKi, and KB worktrees. Report separately: manuscript receipts, governed media acceptance, iCloud copy verification, public repo merge state, site merge/deploy state, and KB merge state. Do not collapse “built,” “copied,” “published,” and “playable” into one status.

## Completion Definition

The project is complete only when:

1. Dan approved the grounded outline, first section, comprehension pilot, pronunciation reel, and paired cover.
2. One frontier author owns all canonical prose and substantive revisions.
3. Fresh traceable evidence, learning, prose, pronunciation, cover, Echo, alignment, and destination receipts verify the same final inputs.
4. The earlier and sibling JSpace projects remain uninspected and untouched.
5. The iCloud package verifies at its destination.
6. The public repository package is merged and contains no raw/private/sealed material.
7. The KinNoKi catalog truthfully exposes only formats that resolve.
8. The KB records the final proof boundaries and paths.

If native Echo narration remains blocked, EPUB and Markdown may be reported only as interim run-root artifacts. Do not sync them, publish the book, or call the package complete until the current-accepted Echo chain and final cover verification pass.
