# Semantic Multi-Voice Audiobooks Design

Date: 2026-08-09
Status: approved for implementation

## Purpose

Make Echo block-level multi-voice narration the standard production path for
new fiction and nonfiction audiobooks. Fiction uses stable character voices.
Nonfiction uses stable semantic voices as retrieval cues: a voice change tells
the listener what kind of attention a passage deserves instead of adding
decorative variety.

Echo pull requests 531 through 533 landed the source-bound block-plan,
installed-renderer attestation, and real multi-voice pronunciation-audit
support. The repository's governed narration wrapper already consumes that
contract in both the `audiobook` and `fiction-audiobook` lanes. This change
activates the landed capability in the production skills and adds deterministic
nonfiction casting validation. It does not redesign Echo or the wrapper.

## Goals

- Make character-level block casting the documented default for new fiction.
- Make semantic block casting the default for new nonfiction learning books.
- Use voice changes to reinforce retrieval, concrete application, and action.
- Keep one primary narrator dominant so books remain coherent and calm.
- Preserve deliberate human or lead-author assignment of every secondary block.
- Keep Echo authoritative for EPUB block existence, speakability, range
  expansion, canonical plan bytes, and resolved plan identity.
- Fail before narration when a semantic cast is stale, noisy, ambiguous, or
  inconsistent with its frozen EPUB and authored Echo plan.
- Preserve accepted runs and avoid automatic rerenders of existing books.

## Non-goals

- Do not switch voices for isolated words, headings, attribution fragments, or
  decorative quotations.
- Do not infer roles from keywords, quotation marks, HTML metadata, accents,
  gender, or personality stereotypes.
- Do not add invisible speaker markup to the EPUB.
- Do not replace semantic block casting with chapter rotation.
- Do not introduce new material inside a memory checkpoint.
- Do not build, install, repair, or promote Echo as part of this repository
  change.
- Do not weaken the installed-renderer, receipt, resume, audit, delivery, or
  publication gates.

## Selected Approach

Use a stable semantic cast for nonfiction and the existing stable character
cast for fiction. Both workflows freeze the EPUB, export Echo's block inventory,
author an Echo schema-1 source-bound plan, require `resolve-voice-plan`, and
invoke the governed wrapper with `--voice-plan`.

Rejected alternatives:

1. Chapter rotation is easy to author but gives a voice change little learning
   meaning.
2. Term-level switching is disruptive, technically mismatched to Echo's block
   model, and likely to sound gimmicky.
3. Automatic post-build classification can drift from author intent and makes
   a model or heuristic, rather than the lead author, responsible for casting.

## Nonfiction Semantic Roles

Every semantic cast contains two to four roles with one stable Echo voice per
role for the entire book. An explicit listener waiver may instead declare only
the `guide` role and an empty assignment set.

| Role | Requirement | Job |
|---|---|---|
| `guide` | Required default | Explanation, transitions, narrative spine, and most runtime |
| `memory` | Required | `Key points`, retrieval questions and answers, and occasional term-memory blocks |
| `field` | Optional | Selected real cases, sourced stories, and worked applications |
| `coach` | Optional | Action rehearsals, safety warnings, and next-action prompts |

The `guide` owns at least 75 percent of narratable blocks. `memory` normally
owns 5 to 15 percent. `field` and `coach` together own no more than 15 percent.
Secondary roles may be sparser when the material does not earn them.

A term receives the `memory` voice only after the `guide` has taught the
problem, name, and meaning. The memory passage is a complete, independently
understandable paragraph, for example: “The term to remember is idempotency. It
means repeating the operation does not change the result after the first
successful application.” The same role may retrieve that term later.

Represent secondary passages as groups of one to four ordered paragraph blocks.
Every block in a group uses the same role. Between groups, require at least two
intervening default-guide paragraph blocks. This makes the consecutive-checkpoint
exception explicit and prevents rapid switching. Every secondary block must
support cold re-entry after the listener missed the preceding thirty seconds.

## Authoring Artifacts

Keep the manuscript as natural Markdown. Store private casting intent outside
the loadable book:

```text
<BOOK_ROOT>/source/narration-role-ledger.md
<RUN_ROOT>/_production/narration/semantic-voice-cast.json
<RUN_ROOT>/_production/narration/echo-voice-plan.json
```

`narration-role-ledger.md` records each planned secondary passage, its semantic
role, its learning job, and the source location before packaging. It is the
editorial explanation, not an operational plan.

`semantic-voice-cast.json` is the deterministic nonfiction cast envelope. Its
schema records:

- schema version and cast mode `semantic`;
- frozen source EPUB filename and SHA-256;
- default role `guide`;
- two to four role records with unique known Echo voice IDs, or one `guide`
  record when an explicit listener waiver is present;
- ordered secondary groups containing a group ID, semantic role, and one to
  four explicit Echo block IDs;
- the authored Echo plan filename and SHA-256;
- the exact Echo inventory filename and SHA-256 used during assignment;
- a listener waiver only when an explicit request permits single-voice output.

The exact JSON schema is implementation detail, but it must be closed: unknown
keys, duplicate keys, malformed types, unsafe paths, and noncanonical JSON fail.
The validator compares the semantic groups with the exact explicit block lists
in the authored Echo plan; neither file may contain an unrecorded secondary
assignment.

`echo-voice-plan.json` remains Echo schema 1. Speaker IDs are the semantic role
IDs. The default speaker is `guide`. Nonfiction assignments use explicit block
lists only; range assignments fail local validation so sparse-role and switching
rules remain inspectable without reimplementing Echo's range semantics.

## Production Flow

1. During outlining, identify only the checkpoints, retrieval prompts, concrete
   cases, and action passages that earn a secondary role. Record them in the
   narration role ledger.
2. Draft and revise natural prose. Treat every planned secondary passage as one
   uninterrupted, self-contained paragraph.
3. Freeze the accepted EPUB and compute its SHA-256.
4. Use the attested installed Echo selected for the approved source revision to
   export the frozen EPUB's private block inventory.
5. The lead author maps the ledger's planned passages to exact inventory block
   IDs and writes the semantic cast plus Echo schema-1 plan. Do not infer roles
   or copy identifiers from a different EPUB.
6. Run the semantic-cast validator. It validates the envelope, known voices,
   role stability, hashes, explicit assignments, paragraph-only groups,
   budgets, spacing, and cast/plan agreement.
7. Invoke the governed wrapper with the validated absolute `--voice-plan`
   vector. The wrapper asks installed Echo to resolve and seal the plan before
   narration.
8. Use the existing block-mode run, resume, pronunciation-audit, sidecar,
   delivery, and publication evidence chain.

Fiction follows the existing explicit character-cast flow. Its instructions
and public descriptions must call block-level character voices the standard
path rather than the earlier chapter-level version-one behavior.

## Longform Handoff

A complete nonfiction handoff includes a semantic voice section containing:

- selected roles and candidate Echo voices;
- the passages or section jobs expected to earn each secondary role;
- any listener casting preferences or exclusions;
- confirmation that the final block mapping waits for the frozen EPUB.

The handoff does not contain guessed Echo block IDs. The production skill owns
inventory export, final assignment, validation, resolution, and rendering.

## Validation and Failure Behavior

The semantic validator fails before wrapper invocation when:

- fewer than two or more than four roles are present without an explicit
  single-voice listener waiver;
- `guide` is missing or is not the default;
- roles or voice IDs are duplicated, unknown, or unstable;
- a declared non-guide role owns no secondary group;
- the cast, inventory, plan, or frozen EPUB hashes disagree;
- the plan uses unknown speaker IDs or range assignments;
- secondary groups exceed 25 percent of the inventory's nonempty paragraph
  blocks;
- `memory` exceeds 15 percent of those blocks, or `field` plus `coach` exceeds
  15 percent;
- a secondary group contains more than four blocks, mixes roles, names a
  non-paragraph block, or is separated from the next group by fewer than two
  default-guide paragraph blocks;
- paths are noncanonical, symlinked, outside the run boundary, or stale.

The validator cannot prove prose quality. The ear pass and blind beginner
review confirm that memory passages contain already-taught material, role
changes sound useful rather than theatrical, and the cast remains intelligible
in road-book conditions.

Echo remains the final operational gate. A missing or unspeakable block, stale
source binding, unavailable voice resource, or failed plan resolution stops the
run. Any accepted cast or plan edit produces a new resolved identity, work
directory, database, receipt chain, and render. Do not reuse captures or resume
state across it.

A single-voice fallback is not automatic. It requires an explicit listener
waiver recorded in `source/brief.md` and the semantic cast. Existing accepted
books are never rerendered automatically.

## Implementation Surface

Expected repository changes:

- `skill/SKILL.md`: make semantic block casting the nonfiction default.
- `skill/references/learning-design.md`, `road-book-mode.md`, and narration
  guidance: define semantic-role planning and listening-quality review.
- `skills/longform-book-development/`: add semantic cast duties to the handoff.
- `skills/fiction-audiobook/` and public-facing descriptions: replace stale
  chapter-level wording with the landed character-level standard.
- `skills/echo-narration/references/narrating.md`: describe the shared
  source-bound block procedure and mode-specific cast validation.
- One small deterministic validator and schema for semantic casts.
- Contract, unit, and integration tests for the new default and failure paths.

Do not modify the governed wrapper unless a failing test proves a nonfiction
lane incompatibility. Current inspection shows that it already accepts and
seals block plans in both lanes.

## Verification

Follow test-driven skill development:

1. Run fresh-agent baseline scenarios without the new guidance and capture
   chapter rotation, decorative switching, term-level switching, automatic
   inference, or silent single-voice fallback when they occur.
2. Add failing contract and validator tests for the approved behavior.
3. Implement the minimal skill, reference, validator, and schema changes.
4. Re-run the same agent scenarios with the revised skill and verify semantic
   role selection and fail-closed handoff.
5. Run targeted validator, audiobook-skill, longform-handoff, Echo narration,
   and fiction integration tests.
6. Run the full unit-test suite, `tools/validate_skills.py`, and
   `git diff --check`.

Local tests prove repository behavior, not real narration quality. An actual
Echo render, human ear pass, delivery, publication, and human listening remain
separate acceptance states.
