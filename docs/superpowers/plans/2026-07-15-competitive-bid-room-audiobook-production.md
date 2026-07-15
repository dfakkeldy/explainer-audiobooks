# The Competitive Bid Room Audiobook Production Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Research, write, review, narrate, verify, publicly publish, and deliver the approved 18,000–24,000-word *The Competitive Bid Room* learning audiobook.

**Architecture:** Build one sequential frontier-authored manuscript around a fictional Atlantic heavy-civil tender, with current official procurement and AI-governance evidence. Maintain prospective learning and pronunciation records under the ignored run root, require two independent final-hash learning reviews and a bounded prose pass, then build only from the user-selected paired cover and governed Echo artifacts. Publish the verified package to both `books/the-competitive-bid-room/` and iCloud Books; keep raw research, review scratch, and render state out of Git.

**Tech Stack:** Markdown, JSON learning/prose/pronunciation/cover receipts, primary-source web research, repository Python 3.11 tooling, original raster image generation, EPUB 3, Echo/Kokoro `am_michael`, FFmpeg/FFprobe, GitHub CLI, iCloud Drive, and the private business knowledge base.

## Global Constraints

- Title: *The Competitive Bid Room*.
- Subtitle: *Automating Heavy-Civil Tenders Without Automating Judgment*.
- Slug: `the-competitive-bid-room`.
- Author metadata: `Dan Fakkeldy`; contributor metadata: `GPT-5 Codex`.
- Narrated target: 22,000 words; accepted range: 18,000–24,000 words; never reduce the target after drafting begins without explicit user approval recorded in `scopeHistory`.
- Audience: experienced heavy-civil bid-room staff who need automation architecture, not an introduction to AI or tendering.
- Curriculum: `end-to-end-trace`, ten narrated chapters, one fictional composite bridge-and-roadworks tender, and one non-narrated sources appendix.
- Privacy: `public-safe`; permission to publish is granted. No real company, prospect, employee, customer, bid, private price, internal workflow, route, address, or disguised private anecdote may appear.
- Authority: automation may locate, extract, cite, compare, draft, calculate deterministically, and surface decisions; people retain bid/no-bid, communications, quantities, assumptions, contingency, price, supplier selection, compliance acknowledgement, and submission authority.
- Evidence: current portal, procurement, privacy, security, and software claims require live verification; prefer official Nova Scotia, CanadaBuys, Canadian privacy, and Canadian cybersecurity sources.
- One frontier lead author owns the outline, every canonical chapter, and every substantive repair. Research and review workers produce evidence or findings, never competing manuscript prose.
- No interior figures. The text must work completely for someone listening while driving or working.
- Exactly three coordinated cover pairs are required. Each pair has original text-free raster art, a 1600×2560 portrait, a 2400×2400 square, thumbnails, specs, and render receipts. The user selects one pair explicitly.
- Learning and prose receipts must bind identical final chapter hashes before EPUB construction.
- Native Echo/Kokoro narration is mandatory. Use `am_michael`, with `am_puck` only when the preferred Echo voice is genuinely unavailable. Do not use a system voice or raw `echo-cli narrate`.
- A full Echo render requires hash-bound human listening evidence for every required pronunciation term.
- Public publication and iCloud delivery occur only after selector-bound cover, Echo, sidecar, audit, and receipt verification passes.
- This repository has no nightly/weekly promotion ladder. Rebase the feature branch onto `origin/main`, then open a ready PR against `main`.

## Working Paths

```bash
export EXPLAINER_ROOT=/Users/dfakkeldy/.codex/worktrees/competitive-bid-room/explainer-audiobooks
export RUN_ROOT="$EXPLAINER_ROOT/.build/custom-learning-audiobooks/the-competitive-bid-room"
export DIST="$RUN_ROOT/dist"
export SLUG=the-competitive-bid-room
export TITLE="The Competitive Bid Room"
export SUBTITLE="Automating Heavy-Civil Tenders Without Automating Judgment"
export CONTRIBUTOR="GPT-5 Codex"
export CLASSIFICATION=public-safe
export DELIVERY_DIR="/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/$TITLE"
export PUBLIC_DIR="$EXPLAINER_ROOT/books/$SLUG"
export PYTHON=/usr/local/bin/python3
```

## File Responsibility Map

- `$RUN_ROOT/research/brief.md`: readable request, assumptions, public-safety boundary, and production status.
- `$RUN_ROOT/research/learning-brief.json`: learner orientation and immutable word-range contract.
- `$RUN_ROOT/research/sources.md`: non-narrated, chapter-mapped public bibliography passed into the EPUB.
- `$RUN_ROOT/research/fact-pack.md`: claim-level evidence the author may use.
- `$RUN_ROOT/research/uncertainties.md`: conflicts, gaps, time-sensitive claims, and excluded unsupported claims.
- `$RUN_ROOT/research/learning-outline.json`: user-authorized ten-chapter progression and throughlines.
- `$RUN_ROOT/research/chapter-plans.json`: exact purpose, prerequisites, knowledge delta, example, concepts, and varied beats for every chapter.
- `$RUN_ROOT/research/coverage-ledger.{md,json}`: complete explanation paths and purposeful chapter uses for every core concept.
- `$RUN_ROOT/research/continuity.{md,json}`: sequential state appended immediately after each chapter.
- `$RUN_ROOT/research/pronunciation-plan.json`: prospective technical-term and variant listening requirements.
- `$RUN_ROOT/chapters/ch01.md` through `ch10.md`: canonical narrated manuscript; no other location may contain authoritative prose.
- `$RUN_ROOT/research/{structure-review.md,beginner-reader-review.md,learning-review.json}`: two independent citation-first learning reviews and final decisions.
- `$RUN_ROOT/research/{prose-qc-before.md,humanizer-decisions.json,prose-qc-after.md,prose-style-receipt.json}`: bounded voice review and final hash receipt.
- `$RUN_ROOT/research/learning-design-receipt.json`: final learning gate bound to the canonical chapters.
- `$DIST/candidate-{1,2,3}/`: each complete coordinated cover pair and provenance.
- `$DIST/cover-selection.json`: explicit user selection binding the portrait and square pair.
- `$DIST/$SLUG.{epub,md}`: governed readable derivatives of the canonical manuscript.
- `$DIST/echo-renders/...`: immutable run-scoped M4B, alignment, pronunciation audit, and optional reel selected through the accepted receipt chain.
- `$DIST/README.md`: publication manifest with objective QC, provenance, hashes, and listening status.
- `books/$SLUG/`: governed public package only; never raw research, chapter drafts, databases, captures, or review scratch.
- `README.md`: public collection row and updated total runtime after final media verification.
- `/Users/dfakkeldy/Developer/knowledge-base/bundle/...`: narrow public-safe business receipt, index link, and dated log entry; never manuscript or private research text.

---

### Task 1: Bootstrap the ignored run and bind the approved scope

**Files:**
- Create transiently: `$RUN_ROOT/{research,chapters,dist}/`
- Create transiently: `$RUN_ROOT/research/{brief.md,learning-brief.json}`
- Copy transiently: the remaining `skill/templates/learning-design/*.json` files into `$RUN_ROOT/research/`

**Interfaces:**
- Consumes: design commit `bc4d18e` and the user's approvals of the two-hour mode, design, and written specification.
- Produces: immutable learner/word/publication constraints for research and planning.

- [ ] **Step 1: Create the run structure from the repository templates**

```bash
set -euo pipefail
mkdir -p "$RUN_ROOT"/{research,chapters,dist}
cp "$EXPLAINER_ROOT"/skill/templates/learning-design/*.json "$RUN_ROOT/research/"
git check-ignore -q "$RUN_ROOT"
```

Expected: the directories exist and `git check-ignore` exits zero.

- [ ] **Step 2: Write `learning-brief.json` with the approved contract**

Use this exact semantic content:

```json
{
  "schemaVersion": 1,
  "learnerOutcome": "Map a heavy-civil tender as one controlled flow, place deterministic automation, AI assistance, and human authority correctly, and select a measurable ninety-day bid-room pilot.",
  "priorKnowledge": "Experienced bid-room worker familiar with tender documents, drawings, specifications, addenda, bonds, quotes, estimates, deadlines, and electronic submission, but not assumed to know AI governance or automation architecture.",
  "openingOrientation": {
    "context": "A fictional bridge-and-roadworks tender arrives in a busy Atlantic contractor's bid room with a changing document set and a fixed deadline.",
    "promise": "Show how one living bid system can reduce omissions and decision latency without delegating commercial judgment or submission authority.",
    "route": "Establish the bid record, qualify the opportunity, turn documents into obligations and scope, connect quotes and assumptions to a living estimate, red-team the submission, and convert outcomes into reusable intelligence."
  },
  "originalTargetWords": 22000,
  "currentTargetWords": 22000,
  "minimumAcceptedWords": 18000,
  "maximumAcceptedWords": 24000,
  "draftingStarted": false,
  "scopeHistory": []
}
```

- [ ] **Step 3: Write the readable brief**

Record the title, subtitle, slug, public-safe classification, publication permission, contributor, ten approved chapter ranges, no-interior-figures decision, composite-tender rule, prohibited private material, authority boundary, research mode `deep`, confidence label `deep`, and approval evidence: “User approved the presented design and then instructed: Write the plan.”

- [ ] **Step 4: Verify the clean public/private boundary**

```bash
git status --short --branch
rg -n -i 'zutphen|allsteel|prospect|mail route|private estimate|real customer' "$RUN_ROOT/research" || true
```

Expected: no run-root file appears in Git status and the sensitive-name scan has no match.

### Task 2: Build the deep official-source fact pack

**Files:**
- Create transiently: `$RUN_ROOT/research/{sources.md,fact-pack.md,uncertainties.md}`

**Interfaces:**
- Consumes: approved evidence policy and live official sources.
- Produces: chapter-tagged facts and uncertainty boundaries; canonical drafting may use no unsupported operational claim.

- [ ] **Step 1: Verify the source shelf live**

Open and record retrieval date `2026-07-15`, publisher, title, URL, source class, changing/stable status, and intended chapters for:

1. Nova Scotia Procurement overview.
2. Nova Scotia e-procurement and the current Supplier's Guide to eBidding.
3. Nova Scotia Construction Contract Guidelines.
4. Nova Scotia Bidder Debriefing Protocol.
5. Nova Scotia Awarded Public Tenders metadata and limitations.
6. CanadaBuys Tender Opportunities and current supplier getting-started guidance.
7. Office of the Privacy Commissioner of Canada generative-AI principles and business guidance.
8. Canadian Centre for Cyber Security AI security actions.
9. UK NCSC prompt-injection guidance only if the Canadian source does not adequately explain untrusted-content authority separation.

- [ ] **Step 2: Extract claim-level evidence by chapter**

For each usable claim, record: claim, supporting source, exact section/page when available, chapter, confidence, expiry/recheck concern, and manuscript-safe wording. Cover portal/submission rules, addenda, bid security, debriefing, award-data limits, privacy necessity/proportionality, accountability, data minimization, traceability, prompt injection, least privilege, and human authorization.

- [ ] **Step 3: Design the fictional tender independently**

Create a clearly labelled fictional case with these stable teaching facts:

- Atlantic municipal bridge replacement plus approach roadworks.
- Earthworks, aggregate, drainage, structural concrete, traffic control, environmental controls, specialty subcontract work, bid security, and electronic submission.
- One addendum revises a quantity and environmental obligation.
- One RFI answer clarifies responsibility without changing every related quantity.
- One low supplier quote excludes a material scope item.
- One late quote changes a controlled allowance and requires a discrepancy report.
- No real location, owner, contractor, supplier, project number, date, price, crew, production rate, or internal form is reused.

- [ ] **Step 4: Reconcile conflicts and remove unsupported scope**

Write `uncertainties.md` with separate sections for changing portal behaviour, incomplete award data, jurisdiction-specific legal/commercial obligations, vendor AI terms, engineering judgment, and claims intentionally excluded. Do not resolve a gap from model memory.

- [ ] **Step 5: Complete the non-narrated bibliography**

Write `sources.md` as readable Markdown with `# Sources`, a short public-safety/method note, and sources grouped under Chapters 1–10. Do not put it under `chapters/`; it will be passed to `build_book.py --non-narrated-appendix`.

### Task 3: Complete prospective learning and pronunciation architecture

**Files:**
- Create/replace transiently: `$RUN_ROOT/research/{learning-outline.json,chapter-plans.json,coverage-ledger.md,coverage-ledger.json,continuity.md,continuity.json,pronunciation-plan.json}`

**Interfaces:**
- Consumes: Tasks 1–2 and approved ten-chapter design.
- Produces: complete pre-draft teaching and pronunciation contracts.

- [ ] **Step 1: Authorize the structured outline**

Set `curriculumPattern.name` to `end-to-end-trace`. Its reason is that the listener must follow one tender state from arrival through outcome. Its fit evidence is that each later capability modifies or verifies the same composite bid. Record authorization `status: approved`, `source: user`, and evidence pointing to the design approval and commit `bc4d18e`. Record the four approved throughlines and exactly `ch01.md` through `ch10.md` with purposes and prerequisites from the design.

- [ ] **Step 2: Write all ten chapter plans before drafting**

Each entry must include its approved purpose, prerequisites, knowledge delta, composite-tender beat, concepts, and at least three distinct teaching jobs. Use these chapter jobs:

1. orientation and reframing;
2. system-state construction;
3. decision comparison;
4. document-extraction walkthrough and failure check;
5. estimate mechanism and boundary analysis;
6. quote-exclusion failure analysis;
7. change simulation and discrepancy reconstruction;
8. adversarial pre-submission review;
9. authority/security threat analysis;
10. outcome learning and pilot design.

- [ ] **Step 3: Complete the coverage ledger**

Create complete explanation paths for these core concepts: competitiveness, living bid record, source of truth, provenance, bid/no-bid packet, compliance matrix, addendum control, evidence versus confidence, deterministic calculation, probabilistic extraction, assumption register, unresolved-assumption state, quote coverage, quote normalization, exclusion, discrepancy report, change propagation, price lock, submission authority, data classification, least privilege, prompt injection, raw/working/sanitized data separation, audit trail, bidder debriefing, estimate-versus-actual feedback, and ninety-day pilot metric.

Every JSON row includes definition, reason, mechanism, fictional concrete case, boundary, misconception, expected ability, and named chapter uses with one of `introduce`, `retrieve`, `deepen`, `apply`, `compare`, or `correct`. The Markdown ledger mirrors the same teaching decisions for human review.

- [ ] **Step 4: Initialize continuity prospectively**

Set `continuity.json` to schema version 1 with an empty `checkpoints` list. Write `continuity.md` with headings for terms defined, examples used, callbacks, active promises, and unresolved questions; keep each empty until Chapter 1 is drafted.

- [ ] **Step 5: Create the pronunciation plan**

Use schema version 1. Require human listening for these entries and variants, mapped to chapters where the exact forms will appear:

- `addendum` / `addenda` — Chapters 4 and 7.
- `Ariba` — Chapters 4 and 8.
- `CanadaBuys` — Chapters 3 and 10.
- `e-bond` / `e-bonding` — Chapters 4 and 8.
- `RFI` / `RFIs` — Chapters 4 and 7.
- `RFQ` / `RFQs` — Chapter 6.
- `deterministic` — Chapters 5 and 9.
- `probabilistic` — Chapters 5 and 9.
- `discrepancy` / `discrepancies` — Chapter 7.
- `prompt injection` — Chapter 9.

Set each source to `coverage-ledger`, status to `planned`, `required` to `true`, and decision/evidence to `null`.

- [ ] **Step 6: Validate prospective records**

```bash
"$PYTHON" "$EXPLAINER_ROOT/skill/scripts/pronunciation_plan_qc.py" \
  --run-root "$RUN_ROOT" --phase planning
"$PYTHON" -m json.tool "$RUN_ROOT/research/learning-outline.json" >/dev/null
"$PYTHON" -m json.tool "$RUN_ROOT/research/chapter-plans.json" >/dev/null
"$PYTHON" -m json.tool "$RUN_ROOT/research/coverage-ledger.json" >/dev/null
git status --short --branch
```

Expected: pronunciation planning passes, JSON parses, and only the already committed plan/spec affect the branch.

### Task 4: Draft Chapters 1–5 sequentially

**Files:**
- Create transiently: `$RUN_ROOT/chapters/ch01.md` through `ch05.md`
- Update transiently after every chapter: `$RUN_ROOT/research/{continuity.md,continuity.json}`
- Modify transiently before first prose: `$RUN_ROOT/research/learning-brief.json`

**Interfaces:**
- Consumes: fact pack, chapter plans, affected ledger rows, narration-style rules, de-Claudification rules, and latest continuity checkpoint.
- Produces: the first half of the canonical manuscript with prospective continuity evidence.

- [ ] **Step 1: Lock the word contract before prose**

Set `draftingStarted` to `true`. Leave all word targets and `scopeHistory` unchanged.

- [ ] **Step 2: Draft Chapter 1, then append its continuity checkpoint**

Write 1,400–1,600 words. Begin inside the fictional bid arrival, establish context/promise/route, define competitiveness without reducing it to low price, and name the human authority boundary. Then append the complete checkpoint before drafting Chapter 2.

- [ ] **Step 3: Draft Chapter 2, then append its continuity checkpoint**

Write 1,900–2,100 words. Construct the living bid record and early data/permission boundaries. Reuse Chapter 1 only to deepen the changing-decision-system model.

- [ ] **Step 4: Draft Chapter 3, then append its continuity checkpoint**

Write 1,800–2,000 words. Build a repeatable qualification packet and show the boundary between prepared evidence and pursuit authority.

- [ ] **Step 5: Draft Chapter 4, then append its continuity checkpoint**

Write 2,400–2,800 words. Walk through the cited compliance matrix, addenda, bonds, questions, and submission rules. Include the exact planned pronunciation forms.

- [ ] **Step 6: Draft Chapter 5, then append its continuity checkpoint**

Write 2,700–3,100 words. Separate deterministic calculations from probabilistic extraction, make assumptions and unresolved state visible, and forbid AI-generated numbers from becoming an approved price.

- [ ] **Step 7: Run the midpoint diagnostic without issuing receipts**

```bash
"$PYTHON" "$EXPLAINER_ROOT/skill/scripts/prose_qc.py" \
  --chapters-dir "$RUN_ROOT/chapters" \
  --out "$RUN_ROOT/research/prose-qc-midpoint.md"
wc -w "$RUN_ROOT"/chapters/ch0{1,2,3,4,5}.md
```

Expected: no hard-banned prose; each chapter is within its range or has a written learning-based reason for a variance. Do not create final receipts.

### Task 5: Draft Chapters 6–10 sequentially and finish the source appendix

**Files:**
- Create transiently: `$RUN_ROOT/chapters/ch06.md` through `ch10.md`
- Update transiently after every chapter: continuity records
- Finalize transiently: `$RUN_ROOT/research/sources.md`

**Interfaces:**
- Consumes: Task 4 canonical prose and continuity.
- Produces: complete 18,000–24,000-word narrated manuscript plus readable non-narrated bibliography.

- [ ] **Step 1: Draft Chapter 6 and append continuity**

Write 2,400–2,800 words. Use the excluded-scope supplier quote to teach RFQ drafting, coverage, normalization, exclusions, follow-up, comparison, and communication authority.

- [ ] **Step 2: Draft Chapter 7 and append continuity**

Write 2,300–2,700 words. Apply the addendum, RFI, revised quantity, and late quote through one discrepancy report whose prior state, new evidence, delta, uncertainty, affected work, and required decision are audible.

- [ ] **Step 3: Draft Chapter 8 and append continuity**

Write 2,100–2,500 words. Red-team scope, forms, bonds, assumptions, schedule, arithmetic, portal readiness, price lock, and submission authority without allowing an automated “safe” verdict.

- [ ] **Step 4: Draft Chapter 9 and append continuity**

Write 2,000–2,400 words. Deepen privacy, retention, least privilege, audit, prompt injection, and untrusted-content authority separation. Keep legal and cybersecurity claims educational rather than advisory.

- [ ] **Step 5: Draft Chapter 10 and append the final continuity checkpoint**

Write 1,700–2,000 words. Use award results, debriefing, estimate-versus-actuals, supplier behaviour, and risk outcomes to define a bounded ninety-day pilot with baseline metrics.

- [ ] **Step 6: Verify manuscript shape and planned pronunciation forms**

```bash
wc -w "$RUN_ROOT"/chapters/ch*.md
for term in addendum addenda Ariba CanadaBuys e-bond e-bonding RFI RFIs RFQ RFQs deterministic probabilistic discrepancy discrepancies 'prompt injection'; do
  rg -n -i --fixed-strings "$term" "$RUN_ROOT/chapters" >/dev/null || {
    echo "missing pronunciation form: $term" >&2
    exit 1
  }
done
```

Expected: total 18,000–24,000 words and every planned form exists in its named chapter set. Deepen incomplete explanation paths if short; do not lower the target or pad complete chapters.

- [ ] **Step 7: Finish the non-narrated appendix**

Ensure every factual chapter has a source section, each source supports a real manuscript claim, changing sources carry the retrieval date, and no raw private/KB path or company-specific context appears.

### Task 6: Run independent learning reviews and substantive repair

**Files:**
- Create transiently: `$RUN_ROOT/research/{structure-review.md,beginner-reader-review.md,learning-review.json}`
- Modify transiently: canonical chapters only for accepted repairs
- Update transiently: continuity and coverage records when a repair changes their evidence

**Interfaces:**
- Consumes: complete canonical manuscript, fact pack, outline, plans, ledger, and continuity.
- Produces: provisional passing learning structure before the voice pass.

- [ ] **Step 1: Run the independent structure review**

Use a reviewer that did not author the chapters. Require citation-first findings for orientation, progression, prerequisites, the end-to-end tender trace, throughline purpose, unresolved promises, duplicated teaching jobs, and chapter knowledge deltas. Each finding records ID, exact location, category, evidence, listener cost, and repair type; it supplies no replacement prose.

- [ ] **Step 2: Run the independent `beginnerReader` lane at the correct audience level**

Use a distinct reviewer identity. Treat the listener as experienced in bidding but new to AI governance and automation architecture. Check unexplained automation/security terms, shallow mechanisms, missing evidence boundaries, visual dependencies, false certainty, weak examples, and whether the expected abilities are plausible.

- [ ] **Step 3: Have the frontier author decide and repair**

Record each finding as accepted, rejected, or resolved with a reason. Apply every accepted substantive, factual, structural, depth, or voice repair in the canonical chapter files; reviewers do not write replacement passages.

- [ ] **Step 4: Rerun both lanes to provisional pass**

Require no unresolved findings. Do not set final `reviewedChapterSHA256` yet because the bounded humanizer may still make accepted edits.

### Task 7: Humanize, de-Claudify, and create final learning/prose receipts

**Files:**
- Create transiently: `$RUN_ROOT/research/{prose-qc-before.md,humanizer-decisions.json,prose-qc-after.md,prose-style-receipt.json,learning-design-receipt.json}`
- Finalize transiently: `$RUN_ROOT/research/learning-review.json`
- Modify transiently: canonical chapters only for accepted patch-sized voice repairs

**Interfaces:**
- Consumes: provisionally accepted manuscript from Task 6.
- Produces: immutable final canonical hashes accepted by both independent gates.

- [ ] **Step 1: Load and apply the `humanizer` skill contract**

Run the independent inventory first:

```bash
"$PYTHON" "$EXPLAINER_ROOT/skill/scripts/prose_qc.py" \
  --chapters-dir "$RUN_ROOT/chapters" \
  --out "$RUN_ROOT/research/prose-qc-before.md" \
  --fail-on-style
```

- [ ] **Step 2: Make only frontier-approved local voice repairs**

Remove AI tics, generic signposting, inflated claims, repetitive rhythm, and formulaic openings/closings while preserving facts, citations, procurement vocabulary, explanation paths, examples, boundaries, and intentional retrieval. Record every accepted and rejected candidate with location, original, proposed change, decision, and reason. Invent no anecdote, opinion, joke, source, or claim.

- [ ] **Step 3: Run factual, privacy, narration, and range checks**

```bash
rg -n -i 'zutphen|allsteel|prospect|mail route|real customer|private estimate' "$RUN_ROOT/chapters" "$RUN_ROOT/research/sources.md" && exit 1 || true
rg -n '`|->|[{}]|[A-Za-z]+_[A-Za-z_]+' "$RUN_ROOT/chapters" && exit 1 || true
wc -w "$RUN_ROOT"/chapters/ch*.md
```

Expected: no private-name or narration-code leak and total remains 18,000–24,000 words.

- [ ] **Step 4: Generate the final prose receipt**

```bash
"$PYTHON" "$EXPLAINER_ROOT/skill/scripts/prose_qc.py" \
  --chapters-dir "$RUN_ROOT/chapters" \
  --out "$RUN_ROOT/research/prose-qc-after.md" \
  --fail-on-style \
  --decisions "$RUN_ROOT/research/humanizer-decisions.json" \
  --style-receipt-out "$RUN_ROOT/research/prose-style-receipt.json"
```

- [ ] **Step 5: Rerun both learning reviews against final hashes**

Set distinct reviewer names, final passing verdicts, citation-first decisions, and an exact `reviewedChapterSHA256` map in `learning-review.json`. Any chapter edit after this step invalidates both reviews and the prose receipt.

- [ ] **Step 6: Generate and cross-check the learning receipt**

```bash
"$PYTHON" "$EXPLAINER_ROOT/skill/scripts/learning_design_qc.py" \
  --run-root "$RUN_ROOT" \
  --receipt-out "$RUN_ROOT/research/learning-design-receipt.json"
"$PYTHON" - "$RUN_ROOT/research/prose-style-receipt.json" "$RUN_ROOT/research/learning-design-receipt.json" <<'PY'
import json, sys
prose = json.load(open(sys.argv[1], encoding="utf-8"))["chapterSHA256"]
learning = json.load(open(sys.argv[2], encoding="utf-8"))["chapterSHA256"]
assert prose == learning, "learning/prose chapter hashes differ"
print("FINAL_CHAPTER_HASHES_MATCH")
PY
```

Expected: learning design passes and prints `FINAL_CHAPTER_HASHES_MATCH`.

### Task 8: Create exactly three paired covers and obtain user selection

**Files:**
- Create transiently: `$DIST/candidate-{1,2,3}/{art-direction.md,source-art.png,cover-spec.json,m4b-cover-spec.json,cover.png,m4b-cover.png,cover-thumbnail.png,m4b-cover-thumbnail.png,cover-render.json,m4b-cover-render.json}`

**Interfaces:**
- Consumes: final research vocabulary and approved publication identity.
- Produces: three complete reviewed portrait/square pairs; packaging remains blocked pending user choice.

- [ ] **Step 1: Write three complete art-and-type briefs**

Use these distinct territories while allowing the research to sharpen physical details:

1. **The Controlled Markup:** one oversized, tactile bid sheet whose coloured revision marks converge on a single verified decision; editorial hero object, warm paper/graphite/vermillion, asymmetric title field.
2. **Layers into Structure:** physical layers of aggregate, concrete, paper, and tracing film resolving into one precise bridge section; bright high-key cut-paper/editorial still life, mineral grey/cream/cobalt/citrus, large typographic side field.
3. **The Change Ledger:** a metal measuring rule and stacked bid tabs altered by one vivid inserted strip, showing controlled change rather than a dashboard; institutional artifact, deep navy/steel/white/safety orange, compact top title block.

Each brief records audience promise, metaphor, composition, title field, material language, 2–4-colour palette, visible accent hex, anti-brief, font roles, line breaks, hierarchy, title/art relationship, subtitle, author, and AUDIOBOOK placement. Avoid dashboards, laptops, glowing brains, robots, arrows, handshakes, chess pieces, generic blueprint wallpaper, and copied cover styles.

- [ ] **Step 2: Generate original text-free raster art**

Use the built-in image generator for each direction. Reject lettering, logos, watermarks, interface elements, stock-photo composition, clutter, weak title space, or visual similarity across candidates.

- [ ] **Step 3: Author schema-v2 portrait and square specs and render each pair**

For candidate numbers 1–3, call `render_cover_pair(...)` from `skill/scripts/cover_pairs.py` with both final sizes, both thumbnails, and both receipts. Typography, line breaks, and composition must be candidate-specific.

- [ ] **Step 4: Inspect all twelve visual outputs**

Inspect portrait and square renders at full size plus both 160-pixel thumbnails per candidate. Record warnings, palette/font notes, thumbnail verdict, pair coordination, and rejection/regeneration decisions in each `art-direction.md`.

- [ ] **Step 5: Present the three complete pairs and pause**

Show all three portrait/square pairs together with concise rationales. Ask the user to choose candidate 1, 2, 3, or request a mix. Do not create `cover-selection.json`, build the EPUB, or start Echo before explicit selection.

### Task 9: Create the selection receipt and build governed EPUB/Markdown

**Files:**
- Create transiently: `$DIST/{cover-selection.json,$SLUG.epub,$SLUG.md}`
- Copy transiently: `$DIST/candidate-$SELECTED/cover-selection.json`

**Interfaces:**
- Consumes: final chapter receipts and explicit cover-pair choice.
- Produces: exact EPUB/Markdown bytes that Echo will narrate.

- [ ] **Step 1: Create the paired public-safe selection receipt**

```bash
: "${SELECTED:?set SELECTED to 1, 2, or 3 from the explicit user response}"
case "$SELECTED" in 1|2|3) ;; *) echo "invalid selected candidate" >&2; exit 1 ;; esac
export PAIR="$DIST/candidate-$SELECTED"
export EDITION_ID=public-v1
export SELECTED_AT=$("$PYTHON" -c 'from datetime import datetime; print(datetime.now().astimezone().isoformat(timespec="seconds"))')
"$PYTHON" "$EXPLAINER_ROOT/skill/scripts/cover_receipts.py" select-pair \
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

Set `SELECTED` only from the actual user decision; the command derives the current offset-aware selection timestamp.

- [ ] **Step 2: Build from both final receipts and the non-narrated appendix**

```bash
"$PYTHON" "$EXPLAINER_ROOT/skill/scripts/build_book.py" \
  --chapters-dir "$RUN_ROOT/chapters" \
  --out-dir "$DIST" \
  --title "$TITLE" \
  --subtitle "$SUBTITLE" \
  --author "Dan Fakkeldy" \
  --contributor "$CONTRIBUTOR" \
  --slug "$SLUG" \
  --cover "$PAIR/cover.png" \
  --m4b-cover "$PAIR/m4b-cover.png" \
  --cover-selection "$DIST/cover-selection.json" \
  --learning-receipt "$RUN_ROOT/research/learning-design-receipt.json" \
  --prose-receipt "$RUN_ROOT/research/prose-style-receipt.json" \
  --non-narrated-appendix "$RUN_ROOT/research/sources.md"
```

- [ ] **Step 3: Verify readable artifacts before narration**

```bash
unzip -t "$DIST/$SLUG.epub"
"$PYTHON" - "$DIST/$SLUG.epub" <<'PY'
import sys, zipfile
with zipfile.ZipFile(sys.argv[1]) as archive:
    first = archive.infolist()[0]
    assert (first.filename, first.compress_type) == ("mimetype", 0)
    assert "OEBPS/appendix.xhtml" in archive.namelist()
print("EPUB_AND_APPENDIX_OK")
PY
```

Expected: the archive validates and prints `EPUB_AND_APPENDIX_OK`.

### Task 10: Render governed pronunciation probes and obtain listening acceptance

**Files:**
- Create transiently: content-addressed partial Echo work/database/captures and resume receipts
- Create transiently: `$RUN_ROOT/research/{pronunciation-probe-reel.m4b,pronunciation-probe-evidence.json,pronunciation-plan-receipt.json}`
- Modify transiently: `$RUN_ROOT/research/pronunciation-plan.json` only with actual human decisions

**Interfaces:**
- Consumes: exact Task 9 EPUB, selected square cover, clean reviewed Echo SHA, and prospective pronunciation plan.
- Produces: hash-bound accepted human evidence authorizing an unbounded full render.

- [ ] **Step 1: Verify and export immutable Echo inputs**

Check the live Echo checkout is clean, its approved pronunciation revision has been reviewed, and its Release CLI/resources pass the wrapper preflight. Then export:

```bash
export VOICE=am_michael
export COVER="$PAIR/cover.png"
export M4B_COVER="$PAIR/m4b-cover.png"
export PRONUNCIATION_PLAN="$RUN_ROOT/research/pronunciation-plan.json"
export ECHO_REPO=/Users/dfakkeldy/Developer/Echo
test -z "$(git -C "$ECHO_REPO" status --porcelain)"
export APPROVED_ECHO_PRONUNCIATION_SHA=$(git -C "$ECHO_REPO" rev-parse HEAD)
[[ "$APPROVED_ECHO_PRONUNCIATION_SHA" =~ ^[0-9a-f]{40}$ ]]
export RUN_ROOT DIST SLUG TITLE VOICE COVER M4B_COVER PRONUNCIATION_PLAN APPROVED_ECHO_PRONUNCIATION_SHA
```

Use the actual forty-character Echo commit SHA; do not use a branch name or symbolic ref.

- [ ] **Step 2: Render one new chapter at a time through the governed wrapper**

Run the first partial command and require exit 2:

```bash
set +e
"$EXPLAINER_ROOT/skills/custom-learning-audiobook/scripts/echo_pronunciation_narrate.sh" --max-chapters 1
status=$?
set -e
[[ "$status" == 2 ]]
```

Then repeat this exact command until every chapter named in the pronunciation plan has a sealed capture:

```bash
set +e
"$EXPLAINER_ROOT/skills/custom-learning-audiobook/scripts/echo_pronunciation_narrate.sh" --resume --max-chapters 1
status=$?
set -e
[[ "$status" == 2 ]]
```

Do not skip chapters by copying captures or editing resume state.

- [ ] **Step 3: Build the governed pronunciation reel**

Resolve `WORK` from the immutable input receipt, then run:

```bash
"$PYTHON" "$EXPLAINER_ROOT/skill/scripts/build_pronunciation_probe_reel.py" \
  --run-root "$RUN_ROOT" \
  --work-dir "$WORK" \
  --out "$RUN_ROOT/research/pronunciation-probe-reel.m4b" \
  --evidence-out "$RUN_ROOT/research/pronunciation-probe-evidence.json"
```

- [ ] **Step 4: Pause for actual human listening**

Present the reel and the required term/variant checklist. The user must explicitly accept or reject every heard form. For a rejection, repair the actual Echo pronunciation input, obtain/review the new clean Echo SHA, and rerender affected captures. Automation may not mark a term accepted.

- [ ] **Step 5: Record accepted decisions and issue the pronunciation receipt**

For every required term, set status `accepted`, record `acceptedBy`, `acceptedAt`, evidence path `research/pronunciation-probe-evidence.json`, and the exact evidence SHA-256. Then run:

```bash
"$PYTHON" "$EXPLAINER_ROOT/skill/scripts/pronunciation_plan_qc.py" \
  --run-root "$RUN_ROOT" \
  --phase full-render \
  --receipt-out "$RUN_ROOT/research/pronunciation-plan-receipt.json"
```

Expected: full-render pronunciation planning passes only after all variants have accepted clips.

### Task 11: Complete the native Echo render and verify the accepted package

**Files:**
- Create transiently: accepted run-scoped M4B, alignment, audit, optional reel, current-attempt/current-accepted/input/state/success receipts, and `$DIST/README.md`

**Interfaces:**
- Consumes: pronunciation receipt and unchanged Task 9 EPUB.
- Produces: complete selector-bound package authorized for delivery.

- [ ] **Step 1: Resume the governed render without a chapter bound**

```bash
"$EXPLAINER_ROOT/skills/custom-learning-audiobook/scripts/echo_pronunciation_narrate.sh" --resume
```

Expected: zero exit, a schema-v2 success receipt, current-accepted selector, non-empty M4B, alignment JSON, and pronunciation audit. Let a progressing render run for as long as required.

- [ ] **Step 2: Resolve only the current accepted artifact chain**

Read `echo-render-current-accepted.json` to derive `RUN_ID`, `ATTEMPT_ID`, artifact path, input receipt, resume-state receipt, and success receipt. Set `AUDIOBOOK`, `SIDECAR`, `AUDIT`, and optional `REEL` only from those verified values. Never select a historical run by filename.

- [ ] **Step 3: Run complete media, sidecar, audit, and cover verification**

Run `echo_pronunciation_state.py verify-delivery` with the current attempt, accepted selector, success receipt, input receipt, resume-state receipt, EPUB, M4B, sidecar, audit, and reel. Then run:

```bash
ffprobe -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 "$AUDIOBOOK"
"$PYTHON" -m json.tool "$SIDECAR" >/dev/null
"$CLI" verify-sidecar \
  --epub "$DIST/$SLUG.epub" \
  --audio "$AUDIOBOOK" \
  --sidecar "$SIDECAR"
"$EXPLAINER_ROOT/skills/custom-learning-audiobook/scripts/validate_pronunciation_audit.py" "$AUDIT"
"$PYTHON" "$EXPLAINER_ROOT/skill/scripts/cover_receipts.py" verify \
  --selection "$DIST/cover-selection.json" \
  --cover "$PAIR/cover.png" \
  --m4b-cover "$PAIR/m4b-cover.png" \
  --epub "$DIST/$SLUG.epub" \
  --m4b "$AUDIOBOOK" \
  --receipt "$DIST/cover-selection.json"
```

Expected: sidecar, audit, selector chain, cover binding, and exact media bytes pass. Never mutate the accepted M4B to repair a failure.

- [ ] **Step 4: Write the publication manifest**

Record title, slug, public-safe status, publication permission, length mode, final narrated word count, runtime at 1.0x and 1.25x, chapter count, narrator, frontier model, distinct research/review/production roles, deep source confidence, no-interior-figures decision, authority/safety guardrails, selected cover pair, output files, pronunciation audit schema/coverage/watch counts, pronunciation reel, human pronunciation status, human full-book listening status `pending`, approved/actual Echo SHAs, EPUB/CLI/resource-tree hashes, all receipt paths, and every QC gate.

### Task 12: Governed public/iCloud sync, repository publication, and KB receipt

**Files:**
- Create tracked: `books/the-competitive-bid-room/` governed package and README
- Modify tracked: `README.md`
- Create in a clean KB worktree: `bundle/status/2026-07-15-competitive-bid-room-audiobook.md`
- Modify in that KB worktree: `bundle/projects/explainer-audiobooks.md`, `bundle/status/index.md`, and `bundle/log.md`
- Create transiently: `$RUN_ROOT/research/pr-body.md`

**Interfaces:**
- Consumes: complete verified package from Task 11.
- Produces: durable listening copy, public library entry, ready PR, and narrow operating-context receipt.

- [ ] **Step 1: Dry-run and apply the iCloud selected-cover sync**

```bash
"$PYTHON" "$EXPLAINER_ROOT/skill/scripts/sync_selected_cover.py" \
  --selection "$DIST/cover-selection.json" \
  --cover "$PAIR/cover.png" \
  --epub "$DIST/$SLUG.epub" \
  --m4b "$AUDIOBOOK" \
  --paired-artifact-dir "$PAIR" \
  --destination "$DELIVERY_DIR" \
  --intent reuse
```

Inspect the reported classification. If it is the expected new/reuse state, rerun the same command with `--apply`. Then copy non-governed Markdown, README, sidecar, audit, optional reel, and the current attempt/accepted/input/state/success receipts without overwriting governed files.

- [ ] **Step 2: Verify actual iCloud destination bytes**

Repeat cover-receipt verification, `unzip -t`, FFprobe duration, JSON parsing, pronunciation-audit validation, sidecar verification, and `verify-delivery` against files inside `$DELIVERY_DIR`. Check CloudDocs status only after the files exist there.

- [ ] **Step 3: Dry-run and apply the governed public sync**

```bash
"$PYTHON" "$EXPLAINER_ROOT/skill/scripts/sync_selected_cover.py" \
  --selection "$DIST/cover-selection.json" \
  --cover "$PAIR/cover.png" \
  --epub "$DIST/$SLUG.epub" \
  --m4b "$AUDIOBOOK" \
  --paired-artifact-dir "$PAIR" \
  --destination "$PUBLIC_DIR" \
  --intent reuse \
  --public-destination
```

Require `public-safe` plus granted permission, then rerun with `--apply`. Copy only the public Markdown, README, alignment sidecar, pronunciation audit, optional reel, and current delivery receipts. Do not copy research notes, chapter sources, captures, databases, or raw review files.

- [ ] **Step 4: Update the public collection index**

Add one `README.md` collection row with the verified title, subject, chapter count, 1.0x runtime, and frontier model. Increase the collection's claimed total hours using the verified duration rather than the planned two-hour estimate. Preserve the honest-disclosure language.

- [ ] **Step 5: Run repository verification**

```bash
"/Users/dfakkeldy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3" \
  -m unittest discover -s tests -v
git diff --check
git status --short --branch
```

Expected: 305 or more tests pass with only documented historical-artifact skips; all intended public files are visible and no `.build` artifact is staged.

- [ ] **Step 6: Commit, rebase, push, and open the ready PR**

```bash
git add README.md "books/$SLUG"
git commit -m "feat: publish the competitive bid room audiobook"
git fetch origin
git rebase origin/main
git push -u origin codex/competitive-bid-room-design
if gh pr view codex/competitive-bid-room-design >/dev/null 2>&1; then
  gh pr edit codex/competitive-bid-room-design \
    --title "Publish The Competitive Bid Room audiobook" \
    --body-file "$RUN_ROOT/research/pr-body.md"
else
  gh pr create \
    --base main \
    --head codex/competitive-bid-room-design \
    --title "Publish The Competitive Bid Room audiobook" \
    --body-file "$RUN_ROOT/research/pr-body.md"
fi
```

The PR body reports public-safety review, word count, runtime, narrator, cover selection, receipt hashes, objective QC, iCloud delivery, and human full-book listening status. Check hosted CI and fix concrete failures before reporting completion.

- [ ] **Step 7: File the narrow business KB receipt in a fresh KB worktree**

Record that a new generic public-safe heavy-civil bid-room automation book was published, its public PR/commit, exact iCloud folder, objective QC, and pending full-book human listening. Reconcile the Explainer Audiobooks project page and master-plan impact. Add the nearest index link and newest-first `2026-07-15` `bundle/log.md` bullet. Do not reproduce manuscript text, private business context, or raw research.

- [ ] **Step 8: Lint and publish the KB change**

```bash
export KB_ROOT=/Users/dfakkeldy/Developer/knowledge-base
export KB_WORKTREE=/Users/dfakkeldy/.codex/worktrees/competitive-bid-room-kb/knowledge-base
export KB_BRANCH=codex/competitive-bid-room-audiobook-receipt
git -C "$KB_ROOT" fetch origin --prune
git -C "$KB_ROOT" worktree add "$KB_WORKTREE" -b "$KB_BRANCH" origin/main
cd "$KB_WORKTREE"
python3 tools/kb_lint.py
git diff --check
git status --short --branch
git add \
  bundle/projects/explainer-audiobooks.md \
  bundle/status/2026-07-15-competitive-bid-room-audiobook.md \
  bundle/status/index.md \
  bundle/log.md
git commit -m "docs: record competitive bid room audiobook"
git push -u origin "$KB_BRANCH"
gh pr create --base main --head "$KB_BRANCH" \
  --title "Record Competitive Bid Room audiobook" \
  --body "Records the public-safe audiobook delivery and verification receipt."
```

If the named KB branch or worktree path already exists, inspect and resume it rather than creating a duplicate. Never stage unrelated KB changes. Confirm the Tier-1 PR's CI and auto-merge state.

- [ ] **Step 9: Final hygiene and report**

Run `git status --short --branch` in the explainer worktree, original explainer checkout, KB worktree, and original KB checkout. Report title, slug, classification, research mode, confidence, word count, runtime, narrator, model roles, public repo path, iCloud path, selected-cover receipt class, pronunciation evidence/audit/watch counts, approved/source Echo revisions, EPUB/CLI/resource hashes, CI state, PR links, and human full-book listening status. No agent-authored tracked change may remain uncommitted or unpushed.
