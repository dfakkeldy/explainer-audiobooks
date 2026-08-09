# Fiction Audiobook Express Skill Design

Date: 2026-08-08
Status: accepted conversational design; implementation pending written-spec review

## Purpose

Create a standalone `fiction-audiobook` skill that turns a one-sentence fiction
premise into a complete, privately delivered and normally public first-listen
audiobook without invoking the long `fiction-book-development` workflow.

The skill owns the express path from premise through story planning, canonical
prose, revision, covers, chapter-level multi-voice Echo narration, Echo-clean
iCloud delivery, and public GitHub staging. It reuses the repository's existing
builders, receipt gates, cover tooling, and governed Echo renderer.

## Goals

- Make a plain request such as “make me a fiction audiobook about a lighthouse
  that only appears during storms” sufficient to start production.
- Allow one optional, explicitly requested grilling session at the beginning.
- Choose the book's length from the premise instead of imposing one default.
- Preserve enough story planning and revision to produce coherent fiction
  without the long workflow's approval pauses and artifact volume.
- Use a coherent three-to-five-voice chapter ensemble and gradually explore
  Echo's English voice catalogue.
- Learn durable liked, tried, and blacklisted voice preferences from listening
  feedback.
- Keep the iCloud book root easy for Echo to load by exposing only the finished
  M4B, EPUB, alignment sidecar, cover, and one production subdirectory.
- Treat original fiction as public-safe and publication-authorized by default,
  subject to a fail-closed automated public-fiction gate.
- Report iCloud delivery, GitHub publication, merge, and human listening as
  separate states.

## Non-goals

- Do not replace or simplify `fiction-book-development`; it remains the
  collaborative lane for premise exploration, vertical slices, detailed story
  bibles, scene cards, approval checkpoints, and staged editorial development.
- Do not invoke `fiction-book-development` from the express skill.
- Do not add character-by-character or dialogue-line voice switching to Echo.
  Version one uses Echo's existing per-chapter voice mappings.
- Do not reorganize the existing iCloud Books library.
- Do not place pronunciation reels, chapter captures, alternate covers, or
  production receipts beside the loadable book files.
- Do not use Apple, macOS, AVSpeechSynthesizer, or another substitute narrator
  when governed Echo narration is interrupted or blocked.
- Do not claim that a public first-listen edition has been human-read or
  human-listened.
- Do not auto-merge the public-book pull request.
- Do not automatically rerender old books when a voice is later blacklisted.

## Selected Architecture

Add a new `skills/fiction-audiobook/` skill. Keep it independent from the long
fiction-development skill while reusing proven production components directly.

```text
skills/fiction-audiobook/
  SKILL.md
  agents/openai.yaml
  references/
    express-fiction-craft.md
    public-fiction-gate.md
  scripts/
    fiction_voice_preferences.py
    stage_echo_delivery.py
```

The skill instructions own intake, story decisions, drafting, revision,
orchestration, and state reporting. `express-fiction-craft.md` contains only the
fiction-specific craft contract needed by the autonomous lane.
`public-fiction-gate.md` owns public-safety and first-listen publication
criteria. The two new scripts handle deterministic state that should not be
left to prose instructions: voice preferences and the delivery-root allowlist.

Reuse these existing components rather than copying them:

- `skill/scripts/build_book.py` for EPUB and combined Markdown assembly;
- `skill/scripts/fiction_production_qc.py` and the existing
  `--fiction-receipt` build gate;
- the paired-cover rendering and selection tooling;
- `skills/echo-narration/scripts/echo_pronunciation_narrate.sh` and its
  installed-renderer, resume, sidecar, audit, and immutable-artifact checks;
- `skills/echo-narration/scripts/echo_voice_plan.py` for canonical chapter
  voice-plan validation;
- existing public-package and cover-selection verification where their
  contracts fit the public fiction edition.

### Rejected alternatives

1. Adding an express mode to `fiction-book-development` would keep the large
   skill loaded and make it too easy for agents to perform its ten-step process
   despite the express request.
2. Refactoring both workflows around a new shared fiction-core skill would
   create a broader migration before the express workflow provides value.

## Trigger And Intake

The skill triggers on requests for a complete fictional listening copy, for
example:

- “Make me a fiction audiobook about ...”
- “Turn this premise into a novel I can listen to.”
- “Make this story idea into an Echo-ready audiobook.”

A request only to plan, draft, revise, or continue fiction without producing a
listening package remains in `fiction-book-development`.

### Ordinary express request

For a plain premise, ask no questions and pause for no approval. Infer
reversible creative choices, record them in the run brief and autonomous
decision record, state a one-line plan, and continue.

The one-line plan contains the working title, dramatic angle, selected form,
chapter count, estimated word count, and estimated runtime.

### Opt-in grilling

Only language such as “grill me,” “interview me first,” or “ask me about the
story first” enables intake. Use the host's available batched-input mechanism
once. The single batch covers:

1. genre, mood, and desired listener experience;
2. characters, setting, or story elements that must appear;
3. content boundaries and elements to avoid;
4. POV or narrative-distance preferences;
5. ending shape or emotional destination; and
6. any voice, accent, or casting preference.

Do not ask follow-up questions after the batch. Resolve remaining reversible
choices editorially and record them.

## Length Selection

Choose the shortest form that fully pays off the premise. Length is an
editorial result, not an intake default.

Use these planning bands as estimates rather than quotas:

| Story demand | Likely form | Approximate words | Approximate audio |
|---|---|---:|---:|
| One central pressure, narrow cast, one decisive turn | short novella | 18k–30k | 2–3 h |
| Developed central arc, several reversals, limited subplots | novella | 30k–45k | 3–5 h |
| Multiple acts, meaningful subplots, or several POVs | novel | 50k–80k | 6–9 h |
| Premise genuinely requires a broad ensemble or long transformation | long novel | 80k–110k | 9–13 h |

Do not lengthen a slight premise to meet a band. Do not compress a premise until
its promised reversal, relationship change, or ending lacks causal support.
Record the chosen band and a one-sentence rationale in `brief.md`.

## Express Story Workflow

Use `.build/fiction-audiobooks/<slug>/` as the private run root. It remains the
active production workspace until a verified edition is staged.

```text
.build/fiction-audiobooks/<slug>/
  brief.md
  story-bible.md
  outline.md
  chapters/
  continuity/
    rolling.md
    final.md
  research/
    unattended-decisions.json
    fiction-production-receipt.json
  revisions/
    full-manuscript-review.md
    full-prose-qc.md
  dist/
```

### 1. Set the story contract

Write a concise `brief.md` and `story-bible.md`. Together they settle:

- dramatic premise and genre promise;
- intended audience and listener experience;
- protagonist desire, opposition, stakes, and change;
- principal characters as choice-making pressures;
- setting and only the world rules that constrain action;
- POV, tense, narrative distance, and prose controls;
- ending direction and deliberate ambiguity, if any;
- content exclusions and public-safety boundaries;
- selected length, chapter range, and runtime estimate;
- author `Dan Fakkeldy` and the generating model as contributor; and
- standing iCloud-delivery and conditional-publication authorization.

This is a compact story bible, not a wiki. It must be sufficient to draft the
opening and support the ending, but it does not require user approval.

### 2. Outline chapter turns

Write `outline.md` as causal turns rather than chapter summaries. Every chapter
has a dramatic job, changed story state, consequence, and exit pressure. The
outline also identifies recurring POV or chapter roles for voice casting.

The outline must support three to five genuine recurring voice roles. Prefer
multiple POVs, framed narration, letters, reports, or interludes only when they
strengthen the premise. Never rotate voices arbitrarily within one recurring
POV merely to reach the ensemble count; each voice needs a stable, listener-
recognizable story role.

Do not create a vertical slice, a scene-card directory, or a user checkpoint.

### 3. Draft sequentially

One lead writer owns the story bible, all canonical chapters, and all
substantive repairs. Draft chapters in order. Maintain one short rolling
continuity record containing current timeline, location, knowledge, injuries,
objects, relationships, promises, mysteries, and payoffs.

Each accepted chapter must change available choices, information,
relationships, risk, or emotional state. Discoveries may update the concise
bible and downstream outline, but they do not trigger routine approval.

### 4. Run three combined revision passes

Run the passes in this order:

1. **Story pass:** premise delivery, structure, causality, escalation, pacing,
   reversals, crisis, climax, and aftermath.
2. **Character and continuity pass:** motive, relationship change, POV
   knowledge, timeline, world logic, planted promises, and payoffs.
3. **Ear and prose pass:** dialogue distinction, narrative distance, sentence
   movement, image system, repeated AI-shaped phrasing, read-aloud flow, and
   final prose QC.

Record accepted findings and repairs in `full-manuscript-review.md`; record the
final mechanical and style result in `full-prose-qc.md`. Reconcile
`continuity/final.md` to the final chapter bytes.

### 5. Bind the fiction production receipt

Reuse the existing hash-bound fiction production gate. Bind the final chapter
hashes plus:

- `research/unattended-decisions.json` as authorization;
- `story-bible.md` as the compact story-bible evidence;
- `continuity/final.md` as final continuity evidence;
- `revisions/full-manuscript-review.md` as whole-book revision evidence; and
- `revisions/full-prose-qc.md` as prose-QC evidence.

The receipt remains `first-listen`, keeps `humanReadingStatus: pending`, grants
no publication by itself, and cannot survive a changed chapter or evidence
artifact. The separate public-fiction gate supplies publication authority.

## Chapter Voice Ensemble

Version one uses Echo's existing chapter-level voice plan. It does not parse or
render individual dialogue speakers.

### Casting rules

- Use three to five distinct voices in every book.
- Assign voices only after the final chapter order and EPUB bytes are frozen.
- Keep recurring POVs or recurring chapter roles on the same voice.
- Select voices for tonal, accent, and character fit before novelty.
- Reserve one or two suitable shorter chapters for voices with no listening
  history when doing so does not break POV consistency.
- Never select a blacklisted voice.
- Start with `af_heart` blacklisted, preserving the existing audiobook
  preference.
- Use one default voice plus complete repeatable `--chapter-voice N=voice_id`
  mappings so every narratable chapter has explicit provenance.

Write the exact cast to `_production/narration/voice-cast.json`. Validate the
plan through `echo_voice_plan.py` and bind it into the Echo run ID, resume state,
input receipt, pronunciation audit, and fiction production record.

### Durable voice preferences

Store private operational preferences at:

```text
~/Library/Application Support/Explainer Audiobooks/fiction-voice-preferences.json
```

Use a versioned record containing:

- blacklisted voice IDs with date and optional reason;
- explicit liked or disliked verdicts;
- use history by book and chapter; and
- the last-updated timestamp.

`fiction_voice_preferences.py` validates known VoiceCatalog IDs, prevents a
blacklisted voice from entering a new cast, records completed uses only after a
verified M4B exists, and supports explicit feedback such as “blacklist Bella.”
A new blacklist affects future books. Rerender an existing book only when the
user explicitly requests a recast.

If a selected voice resource is unavailable, recast it to a non-blacklisted
voice and generate a new immutable plan. Never change a sealed plan in place.

## Covers And Narration

Use the existing paired-cover workflow. Produce and evaluate three original
fiction-appropriate portrait/square pairs, select the strongest pair
automatically, embed the portrait in the EPUB, and provide the selected square
to Echo for the M4B.

Run only the governed installed Echo narration wrapper. Preserve its resource
leases, pronunciation review, content-addressed run identity, resume state,
sidecar verification, audit validation, and immutable final M4B contract.

Changing a chapter voice creates a new voice plan and governed narration run.
It does not require rebuilding unchanged prose or cover art, but the complete
new M4B and sidecar must pass verification before replacement.

## Echo-clean iCloud Delivery

Deliver each current edition to the flat iCloud Books root:

```text
~/Library/Mobile Documents/com~apple~CloudDocs/Books/<Title>/
  <slug>.m4b
  <slug>.epub
  <slug>.alignment.json
  cover.png
  _production/
    source/
    checks/
    narration/
    covers/
    publication/
    previous/
```

The root allowlist is exact:

1. one `<slug>.m4b`;
2. one `<slug>.epub`;
3. one `<slug>.alignment.json`;
4. one `cover.png`; and
5. one `_production/` directory.

The M4B, EPUB, and sidecar must share the same stem. Pronunciation reels,
chapter captures, alternate audio, audits, manifests, Markdown manuscripts,
alternate covers, thumbnails, receipts, logs, and checksums must live below
`_production/`.

`stage_echo_delivery.py` stages into a sibling temporary directory, verifies
the allowlist and hashes, then promotes the four current files and production
directory as one edition. It must not expose a partial new edition. On a redo,
incorporate the previously generated current set into the new staged
`_production/previous/` before promotion. Promotion must use a rename or an
equivalent rollback-safe exchange so the destination resolves to either the
complete old edition or the complete new edition, never a mixture.

Never overwrite or silently move an unexpected user-owned root item. Stop the
promotion, keep the verified staging directory, and report the conflicting
path. Cleanup or reorganization of existing book folders is separate work.

## Public-first Publication

An ordinary fiction-audiobook request carries standing authorization to
publish an original, public-safe first-listen edition. “Keep it private,” a
private source, a failed public-fiction gate, or unresolved rights uncertainty
overrides that default.

### Automated public-fiction gate

Publication requires all of the following:

- original characters and fictional world rather than unlicensed franchise or
  fan-fiction material;
- no private source material, confidential facts, or recognizable private-life
  details;
- no real living person used as an identifiable fictional target without
  explicit authorization;
- no request to imitate a living author's voice; craft references must be
  translated into observable style attributes;
- original, generated, public-domain, permissively licensed, or explicitly
  permissioned cover assets;
- final chapter, cover, EPUB, M4B, sidecar, voice-plan, and receipt hashes agree;
- accurate author, model-contributor, AI-generation, CC BY 4.0, and first-listen
  disclosure; and
- `humanReadingStatus` and `humanListeningStatus` remain `pending` until real
  human verdicts exist.

A failed gate does not block private listening. Deliver the verified iCloud
package, record the failure under `_production/publication/`, and skip all
GitHub mutations.

### Public repository package

Stage the public book under `books/<slug>/` with:

```text
books/<slug>/
  README.md
  <slug>.md
  <slug>.epub
  <slug>.alignment.json
  cover.png
  publication.json
```

Update the root catalogue. Do not commit the M4B to ordinary Git history. Push
the book commit on a public task branch, open a ready pull request, and upload
the exact verified M4B as a public GitHub Release asset targeting that same
commit. Label both the PR and release as a public first-listen whose human
listening verdict is pending.

This makes the edition publicly accessible without an additional approval
pause while keeping merge into the main catalogue separate. Do not auto-merge.
After merge, a later repository workflow may retarget or supersede the public
release without changing the verified M4B bytes.

If GitHub publication fails after iCloud delivery succeeds, report
`icloud-delivered` and `github-publication-failed` separately. Preserve the
staged repository package and release metadata so the publication operation is
safe to retry without regenerating the book.

## Failure Contract

| Failure | Required behavior |
|---|---|
| Story, continuity, or prose gate fails | Repair autonomously and rerun the affected pass before production. |
| Final manuscript cannot pass | Stop before covers, narration, delivery, or publication; preserve the run root and report the failed gate. |
| Voice is invalid, blacklisted, or unavailable | Recast explicitly, create a new plan identity, and restart governed narration for that plan. |
| Echo narration is interrupted | Preserve sealed resume state and resume the identical run; never downgrade to another TTS system. |
| M4B, EPUB, sidecar, cover, or receipt verification fails | Publish and deliver nothing from that candidate. |
| iCloud destination has an unexpected root item | Preserve staging, stop promotion, and report the exact conflict. |
| Public-fiction gate fails | Deliver the verified private iCloud edition and skip GitHub publication. |
| GitHub operation fails | Preserve successful iCloud delivery and idempotent publication staging; report the distinct state. |
| User dislikes a voice after delivery | Record the feedback for future casts; rerender this edition only on an explicit recast request. |

## Redo And Feedback Loop

Locate the book by informal or partial title, then read the brief, compact
bible, outline, final continuity record, current chapter bytes, voice cast, and
feedback log below `_production/source/`.

Preserve named strengths before revision. Make the narrowest requested change:

- story feedback changes the affected chapters and all causally downstream
  material, then reruns the three passes as needed;
- a voice-only complaint leaves prose and covers unchanged, writes a new voice
  plan, and performs a fresh governed narration;
- a cover-only complaint reruns cover selection, rebuilds the EPUB, and
  rerenders the M4B because audited Echo audio is immutable; and
- a blacklist command updates durable preferences without changing existing
  books unless the user also requests a recast.

Archive only the previous generated edition beneath `_production/previous/`.
Append the user's feedback, the exact change, and the resulting delivery and
publication states.

## Verification Strategy

### Skill contracts

Add tests proving that:

- plain premise requests trigger `fiction-audiobook` and skip intake;
- only explicit grilling language enables one batched intake;
- the express skill never invokes `fiction-book-development`;
- length is selected from the premise and recorded with a rationale;
- publication defaults to public-safe first-listen with a private fallback;
- human reading/listening is never inferred from automated checks; and
- the skill links every required reference and script.

### Voice preferences and casting

Test that:

- only known Echo English voice IDs are accepted;
- casts use three to five distinct non-blacklisted voices;
- every narratable chapter receives a valid effective voice;
- recurring POV or chapter roles remain consistent;
- untried voices are eligible for one or two suitable experimental chapters;
- `af_heart` is initially excluded;
- completed usage is recorded only after verified narration; and
- a plan change produces a different canonical voice-plan identity.

### Delivery staging

Using temporary directories, prove that:

- the final root has exactly the four loadable files and `_production/`;
- all other audio and production artifacts are below `_production/`;
- stem mismatches, missing sidecars, extra root audio, and hash mismatches fail;
- partial staging is never promoted;
- an unexpected user-owned destination item is preserved and blocks promotion;
- a redo archives exactly one previous generated edition; and
- rerunning an already-completed promotion is idempotent.

### Production integration

Use a small fixture story and fake renderer to exercise:

- compact story evidence and the existing fiction production receipt;
- EPUB and combined Markdown assembly;
- paired-cover selection;
- mixed chapter-voice forwarding and audit provenance;
- one final M4B plus a verified sidecar;
- Echo-clean staging; and
- public-package staging with the M4B excluded from Git history.

Run the focused tests first, then the full repository test suite,
`tools/validate_skills.py`, and `git diff --check`. Forward-test the completed
skill with fresh-agent requests covering ordinary express, opt-in grilling,
private fallback, unavailable voice, and Echo-root contamination scenarios.

## Acceptance Criteria

The implementation is accepted when all of the following are true:

- “make me a fiction audiobook about X” can proceed from premise to verified
  package without routine approval pauses;
- “grill me” produces exactly one batched intake before autonomous work;
- the skill chooses and records a premise-appropriate length;
- one lead writer owns all canonical prose and repairs;
- compact story evidence satisfies the unchanged fiction production gate;
- each book has a verified three-to-five-voice chapter ensemble with durable
  preference and blacklist handling;
- the iCloud book root contains no competing audio or production artifacts;
- Echo verifies the delivered sidecar against the exact delivered EPUB and M4B;
- a passing public-safe edition is exposed through a public branch, ready PR,
  and GitHub Release without a second approval pause;
- a failed public-fiction gate produces only a private iCloud edition;
- every delivery, publication, merge, and human-listening state is reported
  accurately; and
- focused, full-suite, skill-validation, diff, and forward-test checks pass.
