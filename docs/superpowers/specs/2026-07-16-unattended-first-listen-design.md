# Unattended First-Listen Book Production Design

## Problem

The current book workflows treat internal quality checks as conversational
approval gates. Intake, outline approval, first-section acceptance, the narrated
pilot, cover selection, pronunciation acceptance, and delivery can each stop a
run. That makes the workflows unsuitable for requests such as “start a few
books before bed and have them ready to listen to at work.”

## Outcome

Add two explicit assurance levels:

1. `unattended-first-listen` produces a private, listenable candidate without
   routine questions. It records assumptions and automated editorial decisions,
   completes all non-human research, teaching, prose, media, and package checks,
   and reports human listening as pending.
2. `governed-final` preserves the existing human outline, voice, comprehension,
   cover, pronunciation, publication, and negative-verdict authority.

The mode affects decision authority, not quality effort. Unattended books still
use grounded research, one canonical lead writer, section continuity, separate
revision passes, blind beginner review, de-Claudification, native Echo audio,
sidecar checks, and governed receipts.

## Mode Selection

Select `unattended-first-listen` when the user asks for a completed book and
signals autonomous execution with language such as “overnight,” “wake up to
it,” “ready to listen,” “use your judgment,” “go ahead,” or “start a few
books.” A plain, sufficiently specific request for a finished private book may
also use this mode when the missing decisions have documented defaults.

Select `governed-final` when the user explicitly asks to collaborate, review
intermediate work, approve a public edition, or promote a first-listen edition.
A negative listener verdict always stops or returns the book to development.

## Default Decisions

For unattended nonfiction, default to a curious beginner, road-book listening,
private status, a standard two-hour book unless the request implies another
depth, `am_michael` with `am_puck` fallback, Dan Fakkeldy as author metadata,
and current primary/official research where facts may have changed. Select a
real worked example from the request or the strongest research-grounded example.

Record defaults and inferred choices in a hash-bound
`research/unattended-decisions.json`. The receipt includes request evidence,
privacy, publication status, delivery intent, each decision and reason, and
human-listening status. Missing information becomes a question only when no safe
reversible default exists.

## Checkpoints and Proof Boundaries

In unattended mode, the frontier author or an independent editorial reviewer
may authorize the outline, first-section exemplar, and continuation after a
rendered pilot. The learning receipt is labelled `first-listen`, keeps
`humanComprehensionPilot: pending`, and states that human listening remains the
authority. It must never claim validated learning transfer.

The pronunciation plan may advance from a governed probe to full rendering with
automated evidence in unattended mode. Its receipt is labelled `first-listen`
and records `humanListening: pending`. Governed-final keeps hash-bound human
pronunciation acceptance.

An editorial cover choice is allowed only for a private unattended package with
publication permission false. The receipt records
`selection_source: editorial-autoselection`. Public-safe publication and later
promotion still require explicit human authorization.

## Batch and Failure Behavior

Each requested book gets an independent run folder and assumptions receipt.
Research, planning, drafting, and review may progress independently. Echo renders
respect the existing shared-build leases and queue safely. A blocker in one book
does not stop other books.

At handoff, every requested book must have either:

- a verified private first-listen package and exact delivery path; or
- an explicit blocker receipt naming the completed artifacts, failed gate, and
  resumable next action.

The workflow never leaves a run silently waiting for a routine preference.

## Safety and Publication Boundaries

Do not auto-publish, spend money, send messages, expose private material, or turn
high-stakes topics into personalized advice. Narrow sensitive topics to a safe
educational overview where possible; otherwise stop that book with a precise
reason and continue the remaining batch. Existing private/public repository and
delivery rules remain in force.

## Skill Coverage

- `explainer-audiobook` and `custom-learning-audiobook` perform unattended
  research through delivery.
- `longform-book-development` remains collaborative for exploratory shaping but
  routes overnight or ready-to-listen requests into unattended production
  without requiring a separate handoff approval.
- `fiction-book-development` may autonomously choose premise details and draft
  when explicitly delegated; ready-to-listen language is also explicit
  production authorization for a private first-listen handoff.

## Verification

Contract tests must prove mode selection language exists across all four skills,
the assumptions receipt and stop-question policy are documented, governed-final
behavior remains the default for legacy records, unattended learning and
pronunciation receipts preserve pending human authority, and automated cover
selection cannot authorize publication.
