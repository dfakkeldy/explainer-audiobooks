# Handoff Packet

Use this shape when handing a developed nonfiction project to `$audiobook`.

## Packet

```markdown
# <Working Title> Handoff Packet

## Production Request

Use `$audiobook` to turn this settled plan into a complete audiobook. Build the
EPUB and combined Markdown, render Echo audio when available, preserve the
editable source with the book, and report blockers honestly.

## Status

- Privacy:
- Permission to publish:
- Length target:
- Audience:
- Prior knowledge:
- Listening mode: road-book / focused-study
- Primary listening context: driving and delivering mail / other
- Source-confidence target:
- Development decisions that are settled:
- Open choices that production may resolve:
- What a previous edition gets right and must preserve, if applicable:

## Core Promise

What the listener should understand or be able to do after finishing.

## Governing Question and Narrative Spine

- Governing question:
- Narrative spine:
- Two to four throughlines:
- Planned chapter jobs:

## Chapter and Section Outline

For each chapter, record its purpose, prerequisites, durable outcome, grounded
case, and distinct teaching beats. For each section, record:

- job;
- argument;
- exact source claims and locators;
- throughline advance;
- landing beat;
- what it must not repeat.

## Source Plan

- Authoritative sources and locators:
- Contradictions or uncertainty:
- Real files, tools, commands, records, people, and places to name:
- Story ledger entries with actor, place, date, source, concept, and reversal:
- Private-source boundary:

## Voice Direction

- Voice control panel:
- Positive voice sample: 3-5 project-specific sample sentences from
  project-owned text.
- Disliked phrase families:
- AI-writing patterns to avoid:
- Desired humanizing level:
- Facts, citations, technical names, and examples that must not change:
- De-Claudification gate: required

## Semantic Voice Plan

Choose exactly one mutually exclusive route; never write a reduced normal cast
as though it were a waiver.

### Normal cast

- Selected roles: `guide` plus `memory`, with `field` and `coach` only when
  their paragraph jobs are earned.
- Candidate Echo voices, audition passage, and selected role/voice pairs:
- Passages or section jobs expected to earn each secondary role:
- Listener preferences and exclusions:
- Editorial narration role ledger: `<BOOK_ROOT>/source/narration-role-ledger.md`,
  recording each planned secondary passage, role, learning job, and source location.
- Frozen EPUB mapping boundary: production creates the Echo inventory only after
  the EPUB freezes and maps the ledger to it; this handoff does not contain Echo block IDs.

### Guide-only waiver

- Explicit listener waiver cited from `source/brief.md`:
- Selected role: `guide` only.
- No `memory`, no secondary-role jobs, no groups, and no assignments.
- Candidate guide voice, audition passage, listener preferences/exclusions, and
  the same frozen EPUB mapping boundary; this handoff does not contain Echo block IDs.

## Figure Plan

For every figure:

- teaching job;
- source/provenance and rights status;
- planned file under `chapters/images/`;
- alt text;
- standalone caption;
- placement.

The narration must remain complete with eyes closed.

## Production Method

- One frontier author writes every section in order.
- Every section call receives the outline, fact pack, previous section text or
  faithful summary, current job, and must-not-repeat list.
- Cheaper workers extract, verify, assemble, render, and report with citations;
  they do not write or replace chapters.
- Run claim-traceability, tightening, de-listification, sentence-rhythm, and
  rendered ear-pass as separate jobs.
- Run the blind beginner review on the manuscript in listening order, without
  the outline or author rationale.
- Run `prose_qc.py --fail-on-style`, the bounded `humanizer` pass, and the final
  `prose_qc.py --fail-on-style`.

## Narration

- Preferred voice: `am_michael`
- Echo fallback: `am_puck`
- Listener-named pronunciation risks:
- Author-anticipated pronunciation risks and spoken variants:

## Delivery

- Author: Dan Fakkeldy
- Contributor model:
- Explicit private iCloud reading-copy request, if any:
- Other destination:
```

## Required-field check

A packet is production-ready when it includes:

- a settled audience, outcome, length, privacy boundary, and listening context;
- a real governing question, narrative spine, varied chapter jobs, and
  throughlines;
- chapter purposes and section-level argument jobs;
- source locators, story material, and the exact names production must preserve;
- a voice direction with positive examples and disliked patterns;
- a Semantic Voice Plan with roles, candidate Echo voices, earned secondary
  role jobs, listener preferences/exclusions, the
  `<BOOK_ROOT>/source/narration-role-ledger.md`, and the frozen EPUB boundary;
- a rights-aware picture plan, including a zero-figure decision when relevant;
- the preserve-on-revision notes for any existing edition;
- the five separate craft passes and blind beginner review;
- narration risks, author, contributor, and delivery boundary.

If any item is missing, label the packet a development draft and name the
remaining decision. Do not invent an approval or silently weaken the brief.
