# Claude Platform Audiobook Series Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce and deliver nine thoroughly sourced Claude Platform learning audiobooks covering Build, Evaluate and ship, Operate, and the approved Managed Agents curriculum from the official documentation.

**Architecture:** A shared source inventory maps every in-scope official page to one of nine independently governed volume runs. Each volume uses the existing fail-closed learning, frontier-author, paired-cover, Echo pronunciation, and delivery pipeline; a final series audit proves source coverage and cross-volume continuity.

**Tech Stack:** Official Claude Platform documentation, Markdown, JSON, Python 3, existing `skill/scripts` validators and builders, image generation plus schema-v2 paired-cover rendering, native Echo/Kokoro narration, EPUB 3, M4B, and alignment JSON.

## Global Constraints

- Omit the homepage's Get started section; begin with Build and continue through Evaluate and ship and Operate.
- Use Python as the primary spoken code anchor; explain HTTP behavior independently of SDK syntax.
- Use Project Desk as the progressive worked example across all nine volumes.
- Author metadata is `Dan Fakkeldy`; model attribution belongs in contributor metadata.
- Use one frontier lead author for all substantive canonical prose and sequential continuity updates.
- Never narrate more than one short line of code at a time or place two code lines back to back.
- Treat official Anthropic documentation as primary; date all volatile claims with a source snapshot.
- Treat Managed Agents beta headers, sessions and events, permissions, sandboxes, retention/ZDR eligibility, preview features, multiagent work, scheduled deployments, and migration as volatile until reverified for the active source snapshot.
- Series target and aggregate audit gate remain 315,000 to 405,000 words; every volume must also pass its unchanged accepted range. Both gates apply: the aggregate lower bound is independently stricter, the jointly feasible accepted interval is 315,000-402,000, and 405,000 remains the approved outer planning/audit ceiling. Do not reduce a target after drafting without explicit user approval.
- Every volume requires final-hash structural, beginner-reader, learning-design, and prose-style acceptance.
- Every volume requires exactly three coordinated portrait/square raster cover candidates and an explicit user selection.
- Portrait covers are 1600 by 2560; square M4B covers are 2400 by 2400.
- Narrate with native Echo/Kokoro `am_michael`; use `am_puck` only when the preferred Echo voice is unavailable.
- Do not impose a timeout on progressing Echo narration and do not substitute a system voice.
- Source material is public-safe, but public publication is not authorized by this plan. Deliver personal learning copies through governed iCloud sync; leave repo publication pending.
- Preserve all unrelated work and stage explicit files only.

---

## File Structure

### Tracked planning files

- `docs/superpowers/specs/2026-07-14-claude-platform-audiobook-series-design.md`: approved design and canonical curriculum.
- `docs/superpowers/plans/2026-07-14-claude-platform-audiobook-series.md`: this execution plan.

### Shared transient series records

- `.build/custom-learning-audiobooks/claude-platform-series/research/source-inventory.json`: URL-level source inventory and stability labels.
- `.build/custom-learning-audiobooks/claude-platform-series/research/source-coverage.json`: page-to-volume and page-to-chapter dispositions.
- `.build/custom-learning-audiobooks/claude-platform-series/research/series-brief.json`: shared learner, throughlines, worked example, scope, and target.
- `.build/custom-learning-audiobooks/claude-platform-series/research/series-continuity.json`: cross-volume definitions, callbacks, promises, and versioned facts.
- `.build/custom-learning-audiobooks/claude-platform-series/dist/series-index.json`: delivered volume order, checksums, durations, and source dates.
- `.build/custom-learning-audiobooks/claude-platform-series/dist/README.md`: human-readable series index and accuracy notice.

### Governed volume roots

| Volume | Slug | Target | Accepted range |
|---:|---|---:|---:|
| 1 | `claude-platform-01-the-message` | 36,000 | 31,000-41,000 |
| 2 | `claude-platform-02-thinking-and-reliable-responses` | 39,000 | 34,000-44,000 |
| 3 | `claude-platform-03-giving-claude-tools` | 39,000 | 34,000-44,000 |
| 4 | `claude-platform-04-tools-claude-can-operate` | 41,000 | 36,000-46,000 |
| 5 | `claude-platform-05-context-knowledge-integration` | 43,000 | 38,000-48,000 |
| 6 | `claude-platform-06-prompt-evaluate-improve` | 37,000 | 32,000-42,000 |
| 7 | `claude-platform-07-reliability-safety-economics` | 37,000 | 32,000-42,000 |
| 8 | `claude-platform-08-operating-the-platform` | 45,000 | 40,000-50,000 |
| 9 | `claude-platform-09-the-managed-agent` | 40,000 | 35,000-45,000 |

Each exact slug listed in the table uses its own directory under `.build/custom-learning-audiobooks/`, with the `research/`, `chapters/`, `dist/`, candidate, and governed Echo layout required by `skills/custom-learning-audiobook/references/package-and-qc.md`.

## Shared Interfaces

### Source inventory record

```json
{
  "url": "https://platform.claude.com/docs/en/build-with-claude/extended-thinking",
  "title": "Extended thinking",
  "documentationFamily": "build",
  "retrievedAt": "2026-07-14",
  "stability": "volatile",
  "status": "included"
}
```

Allowed `documentationFamily` values are `build`, `evaluate-and-ship`, `operate`, and `managed-agents`. The 26 approved Volume 9 pages, including the navigation-only migration page, use `managed-agents`. Allowed `stability` values are `durable`, `volatile`, `beta`, `preview`, `deprecated`, and `contractual`. Excluded Get started pages do not enter the inventory.

### Source coverage record

```json
{
  "url": "https://platform.claude.com/docs/en/build-with-claude/extended-thinking",
  "volume": 2,
  "chapter": "ch02.md",
  "disposition": "primary",
  "reason": "Defines extended thinking behavior, display, signatures, and preservation rules"
}
```

Allowed `disposition` values are `primary`, `supporting`, and `consolidated`. Every inventory URL appears at least once. A consolidated page names the chapter that absorbs it and gives a nonempty reason.

### Per-volume package contract

Every run produces the learning brief, approved outline, chapter plans, complete coverage ledger, sequential continuity, two-lane learning review, learning receipt, before/after prose reports, humanizer decisions, prose receipt, pronunciation plan, canonical `chNN.md` files, cited chapter fact packs under `research/fact-packs/chNN.md`, three paired cover directories, selection receipt, EPUB, Markdown, manifest, and governed Echo artifacts required by `package-and-qc.md`.

### Per-volume verification commands

Set `SLUG` to the task's exact slug and run after final voice edits:

```bash
set -euo pipefail
RUN_ROOT="$PWD/.build/custom-learning-audiobooks/$SLUG"
python3 skill/scripts/learning_design_qc.py \
  --run-root "$RUN_ROOT" \
  --receipt-out "$RUN_ROOT/research/learning-design-receipt.json"
python3 skill/scripts/prose_qc.py \
  --chapters-dir "$RUN_ROOT/chapters" \
  --out "$RUN_ROOT/research/prose-qc-after.md" \
  --fail-on-style \
  --decisions "$RUN_ROOT/research/humanizer-decisions.json" \
  --style-receipt-out "$RUN_ROOT/research/prose-style-receipt.json"
wc -w "$RUN_ROOT"/chapters/ch*.md
```

Before humanization, run the same `prose_qc.py` command without `--decisions` or `--style-receipt-out`, saving `prose-qc-before.md`. Preserve its findings, repair accepted items through the frontier author, then require the final command above to pass.

## Task 1: Freeze the live source inventory

**Files:**
- Create: `.build/custom-learning-audiobooks/claude-platform-series/research/source-inventory.json`
- Create: `.build/custom-learning-audiobooks/claude-platform-series/research/source-coverage.json`
- Create: `.build/custom-learning-audiobooks/claude-platform-series/research/source-notes.md`

**Interfaces:**
- Consumes: approved design curriculum
- Produces: complete URL inventory and chapter dispositions for all volumes

- [ ] **Step 1: Confirm the execution checkout**

Run `git status --short --branch`, `git rev-parse --show-toplevel`, and `git log -1 --oneline`. Expected: a named `codex/` branch in the explainer-audiobooks root with no unrelated changes.

- [ ] **Step 2: Re-open the official lifecycle root**

Open `https://platform.claude.com/docs/en/home`. Record the retrieval date and current Build, Evaluate and ship, Operate, and Managed Agents navigation in `source-notes.md`. Include the navigation-only Managed Agents migration page. Do not include Get started links.

- [ ] **Step 3: Enumerate the official pages**

Follow the Build, evaluation, administration, model-migration, and Managed Agents navigation. Add one canonical URL record per substantive page plus the navigation-only Managed Agents migration page. Resolve redirects. Mark pricing, model, limit, beta/preview, availability, data-handling, deprecation, Managed Agents session/event lifecycle, permissions, sandbox, retention/ZDR, memory/dreams preview, multiagent, scheduled deployment, and migration pages as non-durable where applicable.

- [ ] **Step 4: Map each URL to the approved curriculum**

Create at least one coverage record for every URL using the approved chapter titles and `chNN.md` names. Do not create a new chapter without a design revision.

- [ ] **Step 5: Validate completeness**

```bash
python3 - <<'PY'
import json
import re
from pathlib import Path
root = Path('.build/custom-learning-audiobooks/claude-platform-series/research')
inventory = json.loads((root / 'source-inventory.json').read_text())
coverage = json.loads((root / 'source-coverage.json').read_text())
urls = [item['url'] for item in inventory]
chapter_counts = {1: 12, 2: 13, 3: 14, 4: 15, 5: 16, 6: 15, 7: 15, 8: 19, 9: 14}
assert inventory and len(urls) == len(set(urls))
assert all(item['documentationFamily'] in {'build', 'evaluate-and-ship', 'operate', 'managed-agents'} for item in inventory)
assert all(item['stability'] in {'durable', 'volatile', 'beta', 'preview', 'deprecated', 'contractual'} for item in inventory)
assert all(item['status'] == 'included' for item in inventory)
covered = {item['url'] for item in coverage}
assert set(urls) == covered, (set(urls) - covered, covered - set(urls))
assert all(1 <= item['volume'] <= 9 for item in coverage)
for item in coverage:
    match = re.fullmatch(r'ch(\d{2})\.md', item['chapter'])
    assert match, item
    assert 1 <= int(match.group(1)) <= chapter_counts[item['volume']], item
assert all(item['disposition'] in {'primary', 'supporting', 'consolidated'} for item in coverage)
assert all(item['reason'].strip() for item in coverage)
managed_agent_urls = {item['url'] for item in inventory if item['documentationFamily'] == 'managed-agents'}
volume9_urls = {item['url'] for item in coverage if item['volume'] == 9}
assert len(managed_agent_urls) == 26, len(managed_agent_urls)
assert volume9_urls == managed_agent_urls, (volume9_urls - managed_agent_urls, managed_agent_urls - volume9_urls)
print(f'SOURCE_COVERAGE_OK pages={len(urls)} mappings={len(coverage)}')
PY
```

Expected: `SOURCE_COVERAGE_OK` with nonzero counts. Record both JSON SHA-256 values in `source-notes.md`; do not commit `.build/`.

## Task 2: Create the shared series bible

**Files:**
- Create: `.build/custom-learning-audiobooks/claude-platform-series/research/series-brief.json`
- Create: `.build/custom-learning-audiobooks/claude-platform-series/research/series-continuity.json`
- Create: `.build/custom-learning-audiobooks/claude-platform-series/research/series-continuity.md`

**Interfaces:**
- Consumes: Task 1 source hashes and approved design
- Produces: shared learner state, Project Desk state, throughlines, and promises

- [ ] **Step 1: Write the shared brief**

Record the approved learner, Python anchor, Project Desk, four throughlines, original/current target 315,000, minimum 315,000, maximum 405,000, and `draftingStarted: false`. Record that per-volume and aggregate gates both apply, the aggregate minimum is independently stricter, and their jointly feasible interval is 315,000-402,000 while 405,000 remains the approved outer planning/audit ceiling. In authorization and scope history, preserve the previously approved 280,000-360,000 range and record that Dan's 2026-07-14 approval of Managed Agents as Volume 9 changed the current range; do not erase the earlier range.

- [ ] **Step 2: Seed cross-volume continuity**

Create a pre-Volume-1 checkpoint with empty terms and examples plus four active promises: system ownership, context as working set, quality as evidence, and models as versioned dependencies.

- [ ] **Step 3: Validate the brief**

```bash
python3 - <<'PY'
import json
from pathlib import Path
brief = json.loads(Path('.build/custom-learning-audiobooks/claude-platform-series/research/series-brief.json').read_text())
assert brief['originalTargetWords'] == brief['currentTargetWords'] == 315000
assert brief['minimumAcceptedWords'] == 315000
assert brief['maximumAcceptedWords'] == 405000
assert any(item['minimumAcceptedWords'] == 280000 and item['maximumAcceptedWords'] == 360000 for item in brief['scopeHistory'])
assert brief['primaryCodeLanguage'] == 'Python'
assert brief['workedExample'] == 'Project Desk'
assert len(brief['throughlines']) == 4
print('SERIES_BRIEF_OK')
PY
```

Expected: `SERIES_BRIEF_OK`. Record user authorization as approved with evidence dated 2026-07-14. Set `draftingStarted` only immediately before canonical Volume 1 prose begins.

## Per-Volume Execution Contract

Every volume task below executes these actions in order:

- [ ] Create `learning-brief.json`, authorized `learning-outline.json`, `chapter-plans.json`, both coverage ledgers, empty continuity records, and cited fact packs before prose.
- [ ] Draft the canonical chapters sequentially through one frontier lead author, updating both continuity files after every chapter and series continuity after the volume.
- [ ] Run independent structural and beginner-reader reviews; have the frontier author resolve accepted findings.
- [ ] Run the pre-humanizer prose inventory, bounded humanizer, final factual/coverage/narration checks, and final-hash learning and prose receipts.
- [ ] Generate exactly three text-free raster art directions, paired schema-v2 specifications, full-size renders, thumbnails, receipts, and a contact sheet; stop for explicit user selection.
- [ ] Build EPUB and Markdown with the selected pair, both receipts, author `Dan Fakkeldy`, and the active frontier model as contributor.
- [ ] Create and validate a pronunciation plan, render bounded real-book probes, obtain human acceptance, and run the governed native Echo wrapper with `am_michael` or recorded `am_puck` fallback.
- [ ] Require selector-bound `verify-delivery`, `SIDECAR_OK`, pronunciation audit validation, positive M4B duration, EPUB archive validation, and paired cover verification.
- [ ] Dry-run and apply governed iCloud sync, then repeat all package verification from the destination path.
- [ ] Record final words, runtime, narrator, source snapshot, checksums, delivery path, and unresolved volatile facts in series continuity.

## Task 3: Produce Volume 1, The Message

**Files:** `.build/custom-learning-audiobooks/claude-platform-01-the-message/{research,chapters,dist}` with `ch01.md` through `ch12.md`.

**Interfaces:** Consumes Volume 1 mappings and series bible; produces the governed foundation volume and first cross-volume checkpoint.

- [ ] Execute the Per-Volume Contract with target 36,000 and accepted range 31,000-41,000.
- [ ] Use the twelve approved Volume 1 chapters; the capstone assembles Project Desk's message core without introducing tools early.
- [ ] Use title `The Message` and subtitle `Conversations, Content Blocks, and the Messages API`.
- [ ] Probe Claude, Anthropic, API, JSON, Messages API, content block, stop reason, and model IDs.
- [ ] Deliver to `/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/Building with Claude 01 - The Message`.
- [ ] Verify the destination package and write the cross-volume continuity checkpoint before Volume 2 research begins.

## Task 4: Produce Volume 2, Making Claude Think and Respond Reliably

**Files:** `.build/custom-learning-audiobooks/claude-platform-02-thinking-and-reliable-responses/{research,chapters,dist}` with `ch01.md` through `ch13.md`.

**Interfaces:** Consumes Volume 2 mappings and accepted Volume 1 continuity; produces the governed capabilities volume.

- [ ] Execute the Per-Volume Contract with target 39,000 and range 34,000-44,000.
- [ ] Cover all thirteen approved chapters and retrieve Volume 1's content-block model without reteaching it.
- [ ] Use title `Making Claude Think and Respond Reliably` and subtitle `Reasoning, Multimodal Inputs, Structured Output, and Streaming`.
- [ ] Probe adaptive thinking, extended thinking, Fable, Opus, Sonnet, schema, citation, server-sent events, multilingual, and embeddings.
- [ ] Reject generic glowing-brain and interface-card cover concepts.
- [ ] Deliver to `/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/Building with Claude 02 - Making Claude Think and Respond Reliably` and checkpoint continuity.

## Task 5: Produce Volume 3, Giving Claude Tools

**Files:** `.build/custom-learning-audiobooks/claude-platform-03-giving-claude-tools/{research,chapters,dist}` with `ch01.md` through `ch14.md`.

**Interfaces:** Consumes Volume 3 mappings and Volumes 1-2 continuity; produces the governed client-tool volume.

- [ ] Execute the Per-Volume Contract with target 39,000 and range 34,000-44,000.
- [ ] Build all fourteen approved chapters around one controlled Python tool loop and explicit side-effect ownership.
- [ ] Use title `Giving Claude Tools` and subtitle `Contracts, Agent Loops, and Controlled Action`.
- [ ] Probe tool use, tool result, JSON Schema, strict tool use, parallel tool use, Tool Runner, and prompt caching.
- [ ] Reject robot-hand, plug-icon, and generic workflow-diagram cover concepts.
- [ ] Deliver to `/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/Building with Claude 03 - Giving Claude Tools` and checkpoint continuity.

## Task 6: Produce Volume 4, Tools Claude Can Operate

**Files:** `.build/custom-learning-audiobooks/claude-platform-04-tools-claude-can-operate/{research,chapters,dist}` with `ch01.md` through `ch15.md`.

**Interfaces:** Consumes Volume 4 mappings and client-tool ownership model; produces the governed execution-tool volume.

- [ ] Execute the Per-Volume Contract with target 41,000 and range 36,000-46,000.
- [ ] For each approved tool chapter, state executor, permissions, state, data path, cost, failure modes, and oversight.
- [ ] Use title `Tools Claude Can Operate` and subtitle `Search, Execution, Memory, and Computer Use`.
- [ ] Probe web fetch, code execution, advisor, Bash, text editor, computer use, programmatic tool calling, and fine-grained streaming.
- [ ] Reject literal dashboards and generic robot-operator cover concepts.
- [ ] Deliver to `/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/Building with Claude 04 - Tools Claude Can Operate` and checkpoint continuity.

## Task 7: Produce Volume 5, Context, Knowledge, and Integration

**Files:** `.build/custom-learning-audiobooks/claude-platform-05-context-knowledge-integration/{research,chapters,dist}` with `ch01.md` through `ch16.md`.

**Interfaces:** Consumes Volume 5 mappings and accumulated Project Desk state; produces the governed information-architecture volume.

- [ ] Execute the Per-Volume Contract with target 43,000 and range 38,000-48,000.
- [ ] Use one Project Desk corpus to distinguish adding, retaining, caching, compacting, editing, and retrieving information.
- [ ] Use title `Context, Knowledge, and Integration` and subtitle `Caching, Files, Skills, MCP, and Cloud Platforms`.
- [ ] Probe cache breakpoint, compaction, context editing, Files API, Skills, Model Context Protocol, Amazon Bedrock, Google Cloud, and Microsoft Foundry.
- [ ] Reject generic cloud, database-cylinder, and puzzle-piece cover concepts.
- [ ] Deliver to `/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/Building with Claude 05 - Context, Knowledge, and Integration` and checkpoint continuity.

## Task 8: Produce Volume 6, Prompt, Evaluate, and Improve

**Files:** `.build/custom-learning-audiobooks/claude-platform-06-prompt-evaluate-improve/{research,chapters,dist}` with `ch01.md` through `ch15.md`.

**Interfaces:** Consumes Volume 6 mappings and Project Desk behavior; produces the governed evaluation volume.

- [ ] Execute the Per-Volume Contract with target 37,000 and range 32,000-42,000.
- [ ] Use one evaluation suite to distinguish exact, code, model, and human graders across all approved chapters.
- [ ] Use title `Prompt, Evaluate, and Improve` and subtitle `From Instructions to Measurable Quality`.
- [ ] Probe evaluation, grader, latency, Fable, Opus, Sonnet, Console, prompt chaining, and batch processing.
- [ ] Reject checkmark-cloud and generic chart cover concepts.
- [ ] Deliver to `/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/Building with Claude 06 - Prompt, Evaluate, and Improve` and checkpoint continuity.

## Task 9: Produce Volume 7, Reliability, Safety, and Economics

**Files:** `.build/custom-learning-audiobooks/claude-platform-07-reliability-safety-economics/{research,chapters,dist}` with `ch01.md` through `ch15.md`.

**Interfaces:** Consumes Volume 7 mappings and Volume 6 evidence; produces the governed production-control volume.

- [ ] Execute the Per-Volume Contract with target 37,000 and range 32,000-42,000.
- [ ] Tie every safeguard to a named failure and evidence source; never treat a prompt as a security boundary.
- [ ] Use title `Reliability, Safety, and Economics` and subtitle `Guardrails, Failures, Limits, and Cost`.
- [ ] Probe hallucination, jailbreak, prompt leak, idempotency, rate limit, exponential backoff, cache pricing, and spend limit.
- [ ] Date every price and numeric limit; reject shields, locks, dollar signs, and warning triangles as cover theses.
- [ ] Deliver to `/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/Building with Claude 07 - Reliability, Safety, and Economics` and checkpoint continuity.

## Task 10: Produce Volume 8, Operating the Claude Platform

**Files:** `.build/custom-learning-audiobooks/claude-platform-08-operating-the-platform/{research,chapters,dist}` with `ch01.md` through `ch19.md`.

**Interfaces:** Consumes Volume 8 mappings and full continuity; produces the governed operations volume and advances the series promises into the managed-agent capstone.

- [ ] Execute the Per-Volume Contract with target 45,000 and range 40,000-50,000.
- [ ] Keep contractual data-handling claims dated and separate application observability from platform administration.
- [ ] Use title `Operating the Claude Platform` and subtitle `Identity, Monitoring, Compliance, and Migration`.
- [ ] Probe workload identity federation, Admin API, Usage and Cost API, Analytics API, data residency, zero data retention, Access Transparency, Compliance API, deprecation, and migration.
- [ ] Advance all four series throughlines into Volume 9; reject skyline, handshake, and generic server-rack cover concepts.
- [ ] Deliver to `/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/Building with Claude 08 - Operating the Claude Platform` and checkpoint continuity for Volume 9.

## Task 11: Produce Volume 9, The Managed Agent

**Files:** `.build/custom-learning-audiobooks/claude-platform-09-the-managed-agent/{research,chapters,dist}` with `ch01.md` through `ch14.md`.

**Interfaces:** Consumes Volume 9 mappings and Volumes 1-8 continuity; produces the governed Managed Agents volume and resolves the series promises.

- [ ] Execute the Per-Volume Contract with target 40,000 and accepted range 35,000-45,000.
- [ ] Use all fourteen approved chapters: The Managed Harness; From Console Prototype to First Session; Defining an Agent; Tools and Permission Boundaries; MCP and Skills; Where Agents Run; Self-Hosted Sandboxes; Sessions, Steering, and State; Events, Streams, and Webhooks; Outcomes and Vaults; GitHub and Files as Working Context; Persistent Memory and Dreams; Multiagent and Scheduled Work; Limits, Events, and Production Reference.
- [ ] Use title `The Managed Agent` and subtitle `Sessions, Sandboxes, State, and Autonomous Work`.
- [ ] Probe beta headers, session and event lifecycle, permissions, Anthropic-hosted and self-hosted sandboxes, retention and Zero Data Retention ineligibility, memory and dreams preview, multiagent orchestration, scheduled deployments, and migration, including the navigation-only migration page.
- [ ] Probe the official terminology `MCP`, `webhooks`, `GitHub`, `multiagent`, `vaults`, and `server-sent events`/`SSE`; do not invent product terminology.
- [ ] Keep Anthropic-managed state distinct from application-owned policy, credential, monitoring, and retention ownership; resolve all four series throughlines.
- [ ] Deliver to `/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/Building with Claude 09 - The Managed Agent` and record final continuity.

## Task 12: Audit and deliver the complete series

**Files:**
- Create: `.build/custom-learning-audiobooks/claude-platform-series/dist/series-index.json`
- Create: `.build/custom-learning-audiobooks/claude-platform-series/dist/README.md`
- Modify: `/Users/dfakkeldy/Developer/knowledge-base/bundle/projects/explainer-audiobooks.md`
- Modify: `/Users/dfakkeldy/Developer/knowledge-base/bundle/projects/index.md` only if the existing entry is insufficient
- Modify: `/Users/dfakkeldy/Developer/knowledge-base/bundle/log.md`

**Interfaces:** Consumes all nine verified deliveries; produces the complete-series receipt and durable KB status.

- [ ] **Step 1: Re-run source coverage validation**

Repeat Task 1's validator and confirm every mapping points to an existing volume and chapter fact pack.

- [ ] **Step 2: Validate length and chapter count**

```bash
python3 - <<'PY'
from pathlib import Path
slugs = [
    'claude-platform-01-the-message',
    'claude-platform-02-thinking-and-reliable-responses',
    'claude-platform-03-giving-claude-tools',
    'claude-platform-04-tools-claude-can-operate',
    'claude-platform-05-context-knowledge-integration',
    'claude-platform-06-prompt-evaluate-improve',
    'claude-platform-07-reliability-safety-economics',
    'claude-platform-08-operating-the-platform',
    'claude-platform-09-the-managed-agent',
]
expected = [12, 13, 14, 15, 16, 15, 15, 19, 14]
accepted = [(31000, 41000), (34000, 44000), (34000, 44000), (36000, 46000), (38000, 48000), (32000, 42000), (32000, 42000), (40000, 50000), (35000, 45000)]
words = chapters = 0
for slug, count, (minimum, maximum) in zip(slugs, expected, accepted):
    paths = sorted(Path('.build/custom-learning-audiobooks', slug, 'chapters').glob('ch*.md'))
    assert len(paths) == count, (slug, len(paths), count)
    chapters += len(paths)
    volume_words = sum(len(path.read_text().split()) for path in paths)
    assert minimum <= volume_words <= maximum, (slug, volume_words, minimum, maximum)
    words += volume_words
assert chapters == 133
assert 315000 <= words <= 405000, words
print(f'SERIES_LENGTH_OK chapters={chapters} words={words}')
PY
```

Expected: `SERIES_LENGTH_OK chapters=133` with every volume inside its unchanged accepted range and aggregate words inside the approved 315,000-405,000 audit range. Because both gates apply, the jointly feasible aggregate interval is 315,000-402,000; the 405,000 outer cap remains the approved planning/audit ceiling.

- [ ] **Step 3: Verify every iCloud package**

From each destination, rerun paired cover verification, `unzip -t`, `ffprobe`, sidecar JSON parsing, Echo `verify-sidecar`, pronunciation audit validation, and selector-bound `verify-delivery`. Local `.build` success is insufficient.

- [ ] **Step 4: Write the series index**

Record each volume's number, title, subtitle, slug, chapters, words, runtime, narrator, source date, delivery path, EPUB/M4B/sidecar SHA-256, cover-selection SHA-256, and `supersessionStatus: current`. Include total words and runtime.

- [ ] **Step 5: Write the series README**

State audience, order, Project Desk arc, source snapshot, volatile-fact warning, AI disclosure, human-listening status, and exact iCloud paths. Do not claim public availability.

- [ ] **Step 6: File durable KB status**

Update the smallest Explainer Audiobooks project surface with the approved series, delivered artifacts, verification results, and source snapshot. Cite the design, plan, official docs, and delivery root. Add a newest-first 2026-07-14 log entry. Run `python3 tools/kb_lint.py`, commit on a clean `codex/` KB branch, push, open a ready PR, and verify hosted CI.

- [ ] **Step 7: Run repository checks**

Run `python3 -m unittest discover -s tests -v`, `git diff --check`, and `git status --short --branch`. Expected: tests pass, no whitespace errors, and only intentional tracked files remain.

- [ ] **Step 8: Publish repo work for review**

Rebase the feature branch onto current `origin/main`, push with `--force-with-lease` only if already published, and open a ready PR against `main`; this repo has no nightly/weekly branches. Report hosted CI. Do not place audiobook packages in `books/` without separate publication permission.
