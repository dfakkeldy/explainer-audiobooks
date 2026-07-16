# Unattended Book Production

Use this contract before intake whenever a user asks for a finished book or
audiobook. It separates production autonomy from human acceptance so a private
book can be ready for a first listen without being misrepresented as final,
approved, or publishable.

## Choose the production mode

Use `unattended-first-listen` when the user requests completion and delegates
routine decisions. Strong signals include `overnight`, `wake up` to a book,
`ready to listen`, `use your judgment`, `go ahead`, or `start a few books`.
Also use it for a sufficiently specific request for a finished private book when
all missing preferences have safe reversible defaults.

Use `governed-final` when the user asks to collaborate on intermediate choices,
approve a public edition, or promote an existing first-listen package. Records
that predate this contract and omit `productionMode` remain `governed-final`.

An explicit user instruction overrides phrase detection. A request to make a
plan, outline, sample, or development packet is not a request for a finished
book. A request to have a book ready to listen to is authorization for private
production and, when stated, a private iCloud reading copy; it is never
permission to publish.

## Default instead of asking

In `unattended-first-listen`, do not ask about routine preferences. Choose and
record a safe reversible default:

| Decision | Default |
|---|---|
| Audience | Curious beginner, adjusted from evidence in the request |
| Listening context | `road-book`, normally driving and delivering mail |
| Length | Standard private book, about two hours; infer deep or sampler only from the request |
| Privacy | `private` |
| Publication | Not authorized |
| Narrator | `am_michael`, then `am_puck` if unavailable |
| Author metadata | `Dan Fakkeldy` |
| Voice | Warm, direct, mechanism-first, spoken for the ear |
| Worked example | The request's real example, otherwise the strongest research-grounded real example |
| Research | Current primary or official sources when facts may have changed |
| Cover | Exactly three candidates, then rubric-based editorial auto-selection |

Infer prior knowledge conservatively from the request and existing project
context. Do not invent personal facts. When a detail is unknown, state the
assumption in the run record and proceed.

Ask only when all three conditions are true:

1. no safe reversible default exists;
2. the choice materially changes safety, privacy, rights, spending, external
   communication, or irreversible publication; and
3. narrowing the scope or keeping the result private cannot resolve it.

Missing credentials, required source files, unavailable native Echo rendering,
unsafe high-stakes framing, and irreconcilable rights/privacy conflicts are
blockers. Cover taste, title wording, chapter order, ordinary depth, narrator
preference, and routine delivery naming are not blockers in unattended mode.

## Record the delegated decisions

Add this object to `research/learning-brief.json` for nonfiction:

```json
{
  "productionMode": {
    "name": "unattended-first-listen",
    "requestEvidence": "User asked for a book ready to listen to overnight.",
    "decisionsPath": "research/unattended-decisions.json",
    "decisionsSHA256": "<lowercase SHA-256>"
  }
}
```

Write the hash-bound `research/unattended-decisions.json` before outline
authorization:

```json
{
  "schemaVersion": 1,
  "productionMode": "unattended-first-listen",
  "requestEvidence": "User asked for a book ready to listen to overnight.",
  "privacy": "private",
  "permissionToPublish": false,
  "deliveryIntent": "private-project-and-requested-reading-copy",
  "humanListeningStatus": "pending",
  "decisions": [
    {
      "field": "audience",
      "choice": "curious beginner",
      "reason": "No narrower audience was specified.",
      "source": "documented-default"
    }
  ]
}
```

Every inferred choice gets its own non-empty `field`, `choice`, `reason`, and
`source`. Use `user-request`, `project-context`, `documented-default`, or
`editorial-judgment` as the source. Record delivery authorization from the
request; do not silently turn a general book request into an iCloud copy.

For fiction, store the same receipt beside the story bible and bind it from the
fiction brief. It may record delegated premise, genre, POV, tense, ending
direction, length, and production handoff decisions.

## Unattended checkpoints

Keep all non-human gates. Complete grounded evidence, argument or story design,
section-by-section drafting with one lead writer, continuity, separate revision
passes, blind review, de-Claudification, prose receipts, media checks, and
delivery verification.

For nonfiction, render the normal 10-to-15-minute pilot. An independent
editorial reviewer may authorize the outline, accept the project-authored voice
exemplar, and record continuation after reviewing the rendered pilot and its
transcript/diagnostics. Do not fabricate a listener verdict. The learning
receipt is `status: first-listen` with `humanComprehensionPilot: pending`,
`learningAuthority.holder: human-listener-pending`, and
`receiptDoesNotCertifyTransfer: true`.

For pronunciation, create the governed partial probe and evidence reel. Complete
automated form coverage before an unattended full render. The pronunciation
receipt is `status: first-listen` with `humanListening: pending`. Do not write a
human `acceptedBy` decision that did not happen.

Create and inspect exactly three complete paired covers. Select with the rubric
in `cover-art.md`: subject specificity, thumbnail legibility, title hierarchy,
portrait/square coherence, absence of rendering defects, and distinctiveness.
Record `selection_source: editorial-autoselection` in the paired receipt and the
reason in the unattended decisions receipt. This source is valid only with
`privacy: private` and `permission_to_publish: false`.

## Packaging and delivery

A verified unattended package is a **private first-listen edition**. Report:

- which research, learning, prose, EPUB, media, sidecar, cover, and delivery
  checks passed;
- which decisions were automated;
- the exact output and delivery paths;
- `human comprehension: pending` and `pronunciation listening: pending`;
- that a later negative human verdict overrides the automated receipts.

Never auto-publish. Never describe a first-listen package as human-approved,
learning-validated, pronunciation-accepted, final, or public-ready. Promotion to
`governed-final` reuses the existing artifacts but requires the applicable human
listening, cover/publication, and delivery decisions.

## Batch execution

Give every requested book an independent run root and decision receipt. Advance
research, design, drafting, and review independently. Queue native Echo renders
through their existing shared leases. A blocker in one book does not stop the
remaining books.

Enforce a `package-or-blocker` result for every batch item:

- **Package:** verified private first-listen files plus exact delivery path.
- **Blocker receipt:** completed artifacts, failed gate, evidence, whether the
  failure is transient, and the resumable next action.

Do not leave a run silently waiting for a routine preference or confirmation.
Continue every other safe batch item before reporting blockers.

## Safety boundary

Never auto-publish, spend money, send messages, expose private material, accept
legal terms, or issue personalized medical, legal, financial, or safety advice.
Prefer a safe educational overview with explicit limitations. If safe narrowing
is impossible, stop that book with a blocker receipt and continue the batch.

A negative human verdict always wins. Preserve the artifact and evidence, mark
the first-listen receipt superseded or rejected, and return the book to the
appropriate development stage.
