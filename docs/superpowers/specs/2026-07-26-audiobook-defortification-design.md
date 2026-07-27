# Audiobook De-fortification

Date: 2026-07-26

Replace the two gated nonfiction production skills with one lean `audiobook`
skill. Ask for a book, answer five questions, get a finished narrated book in
the iCloud Books folder. Listen the next day. Say what is wrong. It gets redone.

## Why

The gate stack solves a publishing problem: proving a book is fit to go public
without a human having read it. Every receipt, pilot, probe reel, and
package-or-blocker report exists to substitute machine evidence for a missing
human listen.

The actual workflow has no publishing step. It is private, and the QA is the
next-day listen. The one thing gates cannot fake — a human ear on the finished
book — is already happening. So nearly every gate is insurance against a risk
already covered, paid for in build time and in ceremony at request time.

Two visible symptoms:

- The delivery folder carries the ceremony. `The Question Machine`,
  `The Question Machine - Rejected Preview`, and
  `The Question Machine - rv13 Real-World Acceptance` are three folders for one
  book, because the workflow had no concept of "the current version of this
  book" — every revision needed a new name.
- The workspace is not durable. Run roots live in `.build/`, which is gitignored
  and per-worktree, so a book built in one session can be invisible to the next.
  A next-day revision loop cannot stand on that.

## Scope

In scope: the private make-a-book workflow, end to end, and the tooling changes
required to run it without receipts.

Out of scope: `fiction-book-development` and `longform-book-development`, which
are different jobs and stay as they are. Only their production handoff pointer
changes to name the new skill. Public publishing keeps its tooling, parked.

## Decisions

| Decision | Choice |
|---|---|
| Structure | One skill replaces `explainer-audiobook` and `custom-learning-audiobook` |
| Skill name | `audiobook`, canonical source at `skill/` |
| Craft passes kept | Five named revision passes; blind beginner review |
| Craft passes cut | Coverage ledger |
| Book source location | Inside the book's own iCloud folder |
| Delivery authorization | Dan's original request is standing private iCloud authorization; no inheritance to other users |
| On redo | Replace in place; one prior version retained |
| Intake questions | Subject, audience, prior knowledge, length, real grounding |
| Check-in before drafting | State the plan in one line, do not wait |
| Public publishing tooling | Kept, parked, unused by the private lane |

## The skill

`skill/SKILL.md`, renamed to `audiobook`. Target length under 200 lines; the
current `explainer-audiobook` is 677 and `custom-learning-audiobook` is 557.

### 1. Intake

Ask five questions in a single batch, then state the plan in one line — title,
angle, chapter count, estimated runtime — and begin. Nothing blocks on a reply.

1. What is the book about, and what should the listener be able to do after it?
2. Who is it for?
3. What do they already know about the subject?
4. Roughly how long?
5. Should it be built around a specific real thing — a repo, product, place, or
   document?

Everything else is defaulted silently and written into `source/brief.md`:
road-book listening (driving and delivering mail), narrator `am_michael` with
`am_puck` as fallback, author `Dan Fakkeldy`, warm second-person spoken voice,
private, cover auto-selected from three rendered candidates.

### Standing delivery authorization

For Dan's named personal workflow, the original request to receive finished
books in iCloud Books is standing authorization for that private delivery.
Record it in `source/brief.md` and use the expanded iCloud Books title folder as
the absolute `BOOK_ROOT`. This ruling is identity- and context-scoped: another
user or a generic installation defaults to an absolute local `BOOK_ROOT` and
must explicitly opt in before any iCloud copy.

### 2. Research

Evidence notes with real sources and locators, a story ledger, and per-chapter
fact packs naming the real files, tools, and commands the listener should come
away knowing. Plain Markdown in `source/research.md`. No hash binding, no
schema validation, no separate JSON mirror.

The rule that survives is the one that matters: the manuscript may only assert
what the research supports. A citation-shaped memory is not evidence.

### 3. Outline

An argument-level, question-led progression — durable outcomes, a governing
question, a narrative spine, varied chapter jobs, and two to four throughlines.
Written to `source/outline.md`. No approval pause.

A terminology syllabus is not an outline.

### 4. Draft

One frontier author writes every section in order, carrying forward the outline,
the relevant fact pack, the previous section's text or a faithful summary, the
current section's job, and what it must not repeat. A running continuity note
tracks terms, examples, callbacks, and open promises.

Cheaper workers may extract sources, check citations, run diagnostics, assemble
files, render covers, and produce cited editorial reports. They do not write or
replace chapters.

### 5. Revise

In order, one job per pass:

1. `claim-traceability` against the research
2. `tightening` for avoidable repetition and filler
3. `de-listification` for mechanical list rhythm
4. `sentence-rhythm` for spoken variation
5. `ear-pass` against rendered audio

Then the blind beginner review: a reviewer reads the manuscript in listening
order with no outline, no rationale, no expected outcomes, and reports the
mental model a beginner would form and the exact point they get lost. The
frontier author resolves accepted findings.

Then `prose_qc.py --fail-on-style`, then the bounded `humanizer` pass, then
`prose_qc.py --fail-on-style` again.

The passes happen. No ledger records that they happened.

### 6. Produce and deliver

Render three coordinated cover pairs, auto-select the strongest on the existing
rubric — subject specificity, thumbnail legibility, title hierarchy,
portrait/square coherence, absence of defects, distinctiveness — and report the
choice. Build the EPUB and combined Markdown. Narrate the M4B through the Echo
wrapper. For Dan's authorized personal workflow, write the complete folder to
iCloud Books; otherwise retain it at the explicitly chosen local `BOOK_ROOT`.

The cover choice is reported, not requested. A cover you dislike is day-2
feedback like anything else.

## What a book is

```
Books/<Book Title>/
  <Book Title>.epub
  <Book Title>.m4b
  cover.png
  source/
    brief.md          intake answers and every default applied
    outline.md
    research.md       evidence notes and story ledger
    chapters/chNN.md  canonical manuscript
    feedback.md       dated log: what was said, what changed
  previous/           one prior version, overwritten each redo
```

The book carries its own source, so a cold session can find and revise it by
name without re-interviewing. This replaces the `.build/` run root as the
durable home. `.build/` may still be used as scratch during a run, but nothing
that must survive to the next day lives only there.

## The redo loop

1. Locate the book folder by name, tolerating partial and informal titles.
2. Read `source/brief.md`, `source/outline.md`, and the manuscript.
3. **Write down what is working and must not change**, before touching
   anything. See "Preserve on revision" below.
4. Make a targeted revision — the named chapters or the named problem. A full
   rewrite happens only when explicitly requested.
5. Re-run the craft passes over changed material and anything downstream of it.
6. Rebuild the EPUB, re-narrate the M4B, re-render the cover only if the cover
   was the complaint.
7. Move the current version to `previous/`, overwriting what is there. Write the
   new version in place under the same name.
8. Append to `source/feedback.md`: the date, what was said, what changed.

### Preserve on revision

Before revising, record what the current edition gets right and must survive:
its governing question, narrative spine, examples that landed, and chapter jobs
that worked. Revise against that list.

This is the rule from PR #82 (`revisionMode` bound to an explicit prior-edition
declaration), carried forward as practice rather than as a validated schema
field. It exists because *The Question Machine* lost its
Descartes-to-neural-nets spine when a revision did not know it was a revision.
Under the old workflow that was an edge case. Here every redo is a revision of a
book that was partly working, so the rule is load-bearing on the main path:
without it, "chapter 4 dragged" quietly costs chapter 7.

Recording this in `source/feedback.md` satisfies the rule. No gate enforces it.

### Recurring feedback

`source/feedback.md` accumulates per book. When the same note appears across
roughly three books, it is a standing preference, not a book-specific defect.
Offer to write it to memory so it shapes the next book's brief instead of being
corrected again after every build.

## Code changes

Two scripts hard-fail today and must change, or no book can be built:

- `skill/scripts/build_book.py:467` — the `--learning-receipt` requirement
  becomes optional. `--prose-receipt` stays optional as it already is. The
  `--legacy-without-learning-receipt` and `--learning-pilot` escape hatches are
  removed along with the requirement that made them necessary.
- `skills/custom-learning-audiobook/scripts/echo_pronunciation_narrate.sh:141`
  — drops the canonical-plan requirement, its QC invocation, and the
  `PRONUNCIATION_PLAN` variable entirely.

  **Corrected 2026-07-26.** This section originally kept the word list as an
  optional input, on the grounds that feeding Echo terms like `hyperparameter`
  improves the render — "an input wearing a gate's costume." That was wrong.
  `echo-cli narrate` takes only `--epub --out --sidecar --voice --title
  --author --cover --work-dir --db --jobs --threads --resume --max-chapters`.
  There is no lexicon flag and nothing in the repo passes the variable
  anywhere. The pronunciation plan was never an input to the renderer; it fed
  the QC gate and nothing else. It goes with the gate.

## Deletions

### Skill and references

- `skills/custom-learning-audiobook/` — SKILL.md and references deleted; the
  Echo scripts (`echo_pronunciation_narrate.sh`, `echo_installed_renderer.py`,
  `echo_pronunciation_lease.py`, `echo_pronunciation_state.py`,
  `echo_pronunciation_preflight.sh`, `validate_pronunciation_audit.py`,
  `echo_learning_pilot_narrate.sh`) move to `skill/scripts/echo/`, with the
  pilot narration script dropped.
- `skill/references/unattended-production.md` — the whole production-mode state
  machine goes.
- `skill/templates/learning-design/` — schema-v2 starter records.

### References trimmed, not deleted

- `learning-design.md` — keep argument-level outlining, chapter teaching plans,
  and the blind sequential review. Drop the schema-v2 JSON records, the
  comprehension pilot, receipts, waivers, and scope-history rules.
- `road-book-mode.md` — keep the listening-context craft and cognitive-load
  limits. Drop the pilot and human-comprehension-authority gate language.
- `cover-art.md` — keep design, rendering, and the selection rubric. Move the
  receipt and sync sections to the publishing reference.
- `frontier-manuscript-pipeline.md` — keep the role contract and review format.
  Drop the artifact-binding requirements.
- `narration-style.md`, `voice-design.md`, `curriculum-patterns.md`,
  `declaudification.md`, `humanizer-pass.md` — keep; strip references to
  deleted receipts.

### Scripts retired

`learning_design_qc.py`, `pronunciation_plan_qc.py`,
`build_pronunciation_probe_reel.py`.

### Scripts parked for publishing

`cover_receipts.py`, `sync_selected_cover.py`, `verify_public_first_listen.py`,
`replace_m4b_cover.py`. Unused by the private lane. Documented by a new
`skill/references/publishing-a-public-edition.md` covering the rare case of
promoting a finished private book into the public repo.

### Scripts kept and used

`build_book.py`, `make_cover.py`, `cover_pairs.py`, `cover_renderer.py`,
`cover_spec.py`, `cover_fonts.py`, `make_cover_contact_sheet.py`,
`prose_qc.py`, `prose_metrics.py`, `refresh_epub_cover.py`,
`public_audio_recovery.py`, `fiction_production_qc.py`.

### Tests deleted

Contract tests that pin gate language in prose that no longer exists:

- `test_skill_learning_contract.py`
- `test_skill_unattended_contract.py`
- `test_learning_design_gate.py`
- `test_custom_learning_audiobook_echo_contract.py`
- `test_custom_learning_audiobook_install_contract.py`
- `test_pronunciation_plan_qc.py`
- `test_pronunciation_probe_reel.py`

### Tests rewritten

- `test_skill_prose_contract.py` and `test_skill_cover_contract.py` — retarget
  to the new `skill/SKILL.md` and drop assertions about receipts.
- `test_custom_learning_audiobook_echo_runtime.py` — retarget to the new
  `skill/scripts/echo/` paths; it tests real script behaviour and stays.

### Tests kept and must still pass

`test_build_book_cover_receipt.py`, `test_build_book_non_narrated_appendix.py`,
`test_cover_*.py`, `test_make_cover*.py`, `test_prose_qc_metrics.py`,
`test_prose_metrics.py`, `test_prose_style_gate.py`,
`test_corpus_regression.py`, `test_refresh_epub_cover.py`,
`test_replace_m4b_cover.py`, `test_sync_selected_cover.py`,
`test_verify_public_first_listen.py`, `test_public_audio_recovery.py`,
`test_fiction_*.py`, `test_nova_scotia_*.py`, `test_tax_sale_*.py`,
`test_claude_platform_public_series.py`, `test_echo_installed_renderer.py`.

`test_build_book_cover_receipt.py` needs review: it may assert the receipt
requirement being removed. If so, it is updated rather than deleted, since it
also covers cover embedding that still matters.

## Migration

1. Rename `~/.claude/skills/explainer-audiobook` to
   `~/.claude/skills/audiobook` and `~/.agents/skills/explainer-audiobook` to
   `~/.agents/skills/audiobook`. Each already points at `skill/`, so no
   reinstall.
2. Delete `~/.claude/skills/custom-learning-audiobook` and
   `~/.agents/skills/custom-learning-audiobook`.
3. Update `longform-book-development` and `fiction-book-development` handoff
   pointers to name `audiobook`.
4. The Hermes copy of `custom-learning-audiobook` is a downstream consumer of
   the deleted skill and needs its own follow-up. Out of scope here; flagged so
   it is not discovered by breakage.
5. Existing books in `books/` and existing iCloud folders are left untouched.
   The new folder layout applies to new books and to any book revised through
   the redo loop.

## Verification

- `python3 -m unittest discover tests` passes. This repo uses `unittest`;
  `pytest` is not installed.
- `skill/SKILL.md` is under 200 lines.
- A real end-to-end run produces a book in the iCloud Books folder in the layout
  above, with no receipt files and no prompt for approval between intake and
  delivery.
- A redo against that book replaces it in place, populates `previous/`, and
  appends to `source/feedback.md`.

The end-to-end run is the acceptance test. Unit tests confirm the tooling still
works; only a real book confirms the workflow does.

## Risks

**Removing the outline gate can waste a full build on a wrong angle.** Accepted
deliberately: the plan is stated in one line before drafting, and a wrong angle
is interruptible and, failing that, correctable on day two.

**Removing the pronunciation gate can produce a book that mispronounces a term
throughout.** Accepted: Echo has no word-list input in this workflow, so a
mispronunciation is exactly the kind of thing the next-day listen catches.

**Losing the coverage ledger may allow padding to return.** The tightening pass
and `prose_qc.py` repeated-phrase sweep remain the defence. If padding recurs
across several books, revisit rather than restoring the full ledger.

**The redo loop degrading a book that was partly good** is the real risk, and it
has already happened once. The preserve-on-revision rule is the mitigation, and
it is unenforced by design.
