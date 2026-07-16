# Echo-Ready Flashcards for Learning Books — Design Specification

**Date:** 2026-07-15

**Status:** Approved in conversation; awaiting written-spec review

**Scope:** `longform-book-development`, `custom-learning-audiobook`,
`explainer-audiobook`, shared Explainer Audiobooks tooling, and the narrow Echo
import seam required for portable decks

## Purpose

Every completed learning book should include a compact, reviewed set of
flashcards that can be imported into Echo on Mac, iPhone, or another tester's
device. The cards should reinforce the book's durable learning outcomes without
interrupting playback or burdening the requester with another approval step.

The deck is a governed learning artifact, not a chapter-summary dump. It is
derived from the accepted manuscript and the exact EPUB that Echo parses. It
uses Echo-owned portable source anchors, enters the ordinary Echo session/FSRS
review flow, and may selectively use book figures or mnemonic images when they
materially improve recall.

## Approved Product Decisions

- A reviewed Echo deck is a default output for every completed learning book.
- The user may explicitly opt out in the learning brief, but omission is never
  an unstated production shortcut.
- The normal target is two or three high-value cards per substantive chapter.
- Short orientation or closing chapters may have fewer cards when additional
  cards would be filler; the exception and reason are recorded.
- Most cards are text-only. Existing book figures and a small number of
  generated mnemonic images are used only when they improve recall.
- Imported cards use `triggerTiming: "manualOnly"`, so they never interrupt
  listening. They remain ordinary Echo flashcards eligible for session and FSRS
  review.
- Deck generation and two independent reviews run automatically. A passing deck
  ships without a separate user approval gate.
- Decks must be portable across devices and testers. They cannot embed a Mac
  home-directory path or another device's local audiobook identifier.
- Full `.echo` archive packaging remains a later wrapper around these same
  artifacts. It is not part of this implementation.

## Live Baseline

The design was checked against these live sources on 2026-07-15:

- Explainer Audiobooks `origin/main` at
  `728eb4736a3a85e8c83cc43d856a6629d65bc793`.
- Echo `origin/nightly` at
  `e6a78acb275b82994f7dd38c55abdde8b5528ed1`.

At that Echo revision:

- `echo-cli export-blocks` emits the visible EPUB block set with the same
  portable `s<i>-b<j>` anchors used by alignment sidecars.
- `FlashcardDeckImport` accepts `deckName`, `targetMediaID`, and cards with
  `frontText`, `backText`, optional times, `triggerTiming`, `sourceAnchor`, and
  optional mutually exclusive `imageAnchor` / `imageFile` fields.
- `DeckImportService.importDeckVNext` resolves source anchors against the
  deck's embedded `targetMediaID`.
- `StudyDeckFileExporter` writes importable JSON decks with portable anchors.
- `echo-cli deck` exists, but its deterministic fixture generator produces
  generic keyword cards. It is useful as a smoke-test surface, not as the
  learning-book authoring path.

The current blocker to true portability is `targetMediaID`: Echo book IDs are
device-local, commonly folder URL strings. A deck created for one filesystem
cannot safely carry that value to another device.

## Goals

1. Generate concise, source-backed retrieval cards from the final learning
   book by default.
2. Bind every card to the exact EPUB passage it teaches using Echo's canonical
   portable anchors.
3. Let one deck bind safely to the matching local book on different devices.
4. Keep cards in Echo's normal review flow without triggering during playback.
5. Support selective in-book figures and generated mnemonic images.
6. Fail closed on stale manuscripts, mismatched books, invalid anchors, failed
   reviews, unsafe image references, or package drift.
7. Preserve public/private boundaries and existing governed package receipts.
8. Keep the requester workflow low-friction.

## Non-Goals

- Building the `.echo` ZIP archive and its transactional multi-asset importer.
- Generating Anki `.apkg` files.
- Adding cloze cards or changing Echo's card scheduler.
- Automatically interrupting playback with imported cards.
- Replacing Echo's EPUB parser or estimating portable anchors in Python.
- Requiring every chapter to hit a numeric card quota when no useful card is
  available.
- Requiring user review of every deck or mnemonic image.
- Rewriting historical book packages unless they are deliberately rebuilt.

## Responsibilities Across Skills

### `longform-book-development`

The planning skill defines the deck strategy and carries it in the production
handoff. It records:

- whether the default deck is enabled;
- durable outcomes that deserve later retrieval;
- likely chapter-level retrieval targets;
- misconceptions, mechanisms, applications, and comparisons worth testing;
- existing figures that may help a card; and
- abstract concepts that might earn a mnemonic image.

It does not write final card text or source anchors. Those depend on the final
manuscript and the exact built EPUB.

### `custom-learning-audiobook` and `explainer-audiobook`

Both production skills:

1. inherit or create the flashcard strategy;
2. finish the canonical manuscript and pass prose/learning gates;
3. build the governed EPUB;
4. obtain canonical source blocks and source identity from Echo;
5. create and review the final deck;
6. package the deck, images, receipt evidence, and checksums; and
7. deliver the deck under the book's privacy/publication classification.

### Shared Explainer Audiobooks tooling

Shared references, templates, schemas, and scripts live under `skill/` so both
production skills follow one contract. The custom-learning skill references the
canonical shared files instead of maintaining a divergent implementation.

### Echo

Echo owns:

- EPUB parsing and portable block identity;
- the portable source-signature algorithm;
- target-book selection and device-local book binding;
- source-signature verification;
- anchor resolution and card persistence; and
- the session/FSRS review behavior of imported cards.

## Architecture

```text
longform planning or production intake
    -> flashcard strategy and retrieval targets
    -> accepted canonical manuscript
    -> governed EPUB
    -> Echo CLI export-blocks v2
         -> portable blocks
         -> Echo-owned source signature
    -> frontier-authored flashcard draft
    -> optional figure/mnemonic binding
    -> learning review + technical review
    -> deterministic deck builder + hash-bound receipt
    -> governed package and delivery
    -> Echo selected-book import
         -> local source-signature verification
         -> local audiobook-ID binding
         -> portable anchor resolution
         -> ordinary session/FSRS review
```

The architecture separates three identities:

- **Deck identity:** stable across re-imports of one book edition.
- **Source identity:** stable across devices for the same parsed EPUB content.
- **Local book identity:** assigned by Echo on each device.

No filesystem path is used as a portable identity.

## Run Artifacts

The canonical run remains `.build/custom-learning-audiobooks/<slug>/` where
that layout applies. The feature adds:

### Research and evidence

- `research/flashcard-plan.json` — planning strategy, enabled/opt-out decision,
  retrieval targets, chapter expectations, and visual opportunities.
- `research/echo-source-blocks.json` — exact `export-blocks` v2 output from the
  approved Echo CLI.
- `research/flashcard-draft.json` — unshipped candidate cards with reviewer
  stable IDs and source anchors.
- `research/flashcard-review.json` — both review verdicts, citation-first
  findings, decisions, and reviewed artifact hashes.
- `research/echo-flashcard-receipt.json` — final hash-bound acceptance receipt.

### Deliverables

- `dist/<slug>.echo-deck.json` — portable Echo deck.
- `dist/deck-images/` — generated mnemonic images referenced by `imageFile`.
  The directory is omitted when empty.

In-book figures are referenced by `imageAnchor` and are not duplicated into
`deck-images/`.

## Portable Deck v2

The deck extends the existing JSON shape additively:

```json
{
  "formatVersion": 2,
  "deckID": "com.kinnoki.learning-book.example.2026-07.core",
  "deckName": "Example Book — Core Review",
  "targetBinding": "selectedBook",
  "targetMediaID": "echo-portable:example:2026-07",
  "sourceSignature": {
    "algorithm": "echo-visible-blocks-v1",
    "value": "sha256:<lowercase-hex>"
  },
  "cards": [
    {
      "frontText": "Why does this mechanism fail when the input changes?",
      "backText": "Its cached assumption no longer matches the current input.",
      "sourceAnchor": "s3-b7",
      "triggerTiming": "manualOnly"
    },
    {
      "frontText": "What visual cue distinguishes these two states?",
      "backText": "The open gate represents an accepted transition.",
      "sourceAnchor": "s4-b5",
      "triggerTiming": "manualOnly",
      "imageFile": "deck-images/open-gate.png"
    }
  ]
}
```

### Field rules

- `formatVersion` is exactly `2` for portable generated decks.
- `deckID` is a stable ASCII identifier scoped to the book slug, edition, and
  core-deck role. Rebuilding the same edition preserves it; a new edition gets a
  new identifier.
- `targetBinding` is exactly `selectedBook`.
- `targetMediaID` remains present for backward decoding but contains a portable
  sentinel, never a local path. Echo v2 must not persist the sentinel.
- `sourceSignature` comes byte-for-byte from Echo's block export.
- `frontText` is non-empty and at most 160 characters.
- `backText` is non-empty and at most 240 characters.
- `sourceAnchor` is required and must name an exported visible text block.
- `startTime` and `endTime` are omitted. Source placement is authoritative.
- `triggerTiming` is exactly `manualOnly`.
- A card has at most one of `imageAnchor` and `imageFile`.
- `imageAnchor` names an exported image block in the same source.
- `imageFile` is a normalized relative path under `deck-images/`; absolute
  paths, `..`, symlinks escaping the bundle, and missing files fail validation.
- Portable v2 initially produces basic question/answer cards only.
- Unknown or duplicate JSON keys fail deterministic tooling validation even
  where the platform decoder would otherwise ignore them.

An old Echo version will decode the legacy fields but cannot resolve the
portable sentinel. Because portable cards omit timestamp fallbacks, import
fails before card persistence instead of silently attaching them to a fake
book. The package manifest records the minimum compatible Echo revision.

## Echo-Owned Source Signature

Portable anchors identify a location but do not identify the book. A source
signature prevents a deck for one book from being attached to structurally
similar anchors in another.

Echo adds one shared, deterministic `EchoSourceSignature` implementation used
by both `export-blocks` and deck import.

`echo-visible-blocks-v1` is calculated from visible blocks sorted by
`sequenceIndex`. Its canonical input contains:

- signature algorithm/version;
- total block count; and
- for each block, length-prefixed values for portable block ID, block kind,
  exact text, chapter index including an explicit null representation, sequence
  index, and word count including an explicit null representation.

The input excludes audiobook ID, filesystem paths, extraction directories,
timestamps, and other device-local values. It uses the exact stored UTF-8 text
without locale-dependent normalization. The result is a full SHA-256 digest
encoded as lowercase hexadecimal with the `sha256:` prefix.

`BlockExportDocument` advances to version 2 and includes the signature object.
Deck tooling copies the signature; it does not reimplement the algorithm.

The signature protects the textual/structural source identity. Image anchors
are additionally required to resolve to visible `image` blocks. Generated
mnemonic image bytes are governed separately by the flashcard receipt.

## Card Generation

### Timing

Final cards are written only after:

- canonical chapter files are final;
- learning and prose receipts pass and bind those files; and
- the governed EPUB has been built.

Any later manuscript or EPUB change makes the source export, deck, reviews, and
flashcard receipt stale.

### Authorship

The frontier author owns substantive card wording because a flashcard is
learning content, not mechanical packaging. Lower-cost workers may prepare
source extracts, assemble JSON, run validators, and report findings. They may
not invent or substantively rewrite accepted questions and answers.

### Inputs

The card author receives:

- the learner outcome and prior-knowledge brief;
- approved durable outcomes;
- chapter plans and coverage ledger;
- the flashcard strategy/handoff;
- final canonical chapter hashes; and
- exact final source blocks with allowed portable IDs.

### Card distribution

- Substantive chapters normally receive two or three cards.
- A short orientation or closing chapter may receive zero or one when its job
  does not create a durable retrieval target.
- Every below-range chapter records a reason in `flashcard-plan.json`.
- No card is added merely to reach a quota.
- The deck as a whole must cover the book's core durable outcomes; incidental
  details do not displace mechanisms or applications.

### Card jobs

The deck varies retrieval jobs where the manuscript supports them:

- explain a definition in plain language;
- recall why something matters;
- reconstruct a mechanism;
- apply an idea to a fresh situation;
- distinguish a useful boundary or comparison;
- correct a likely misconception; or
- identify a meaningful visual cue.

Each card tests one clear target. The question must require recall rather than
merely recognition, and the answer must be sufficient without copying a long
source passage. Trick wording, answer giveaways, vague chapter-summary prompts,
and duplicate paraphrases are defects.

## Images

Images are selective, not a quota.

Priority order:

1. Reference an existing useful in-book figure with `imageAnchor`.
2. Generate a mnemonic image when an abstract, high-value concept lacks a
   useful figure and a visual hook materially improves recall.
3. Keep the card text-only when an image would be decorative or redundant.

Generated mnemonic images:

- remain a small minority of the deck;
- use original, rights-safe art;
- contain no required answer text, private details, logos, watermarks, or
  imitation of named artists;
- remain understandable as an optional cue rather than the sole source of the
  answer;
- use speakable, safe filenames under `deck-images/`; and
- inherit the book's privacy and publication classification.

If optional image generation or import validation fails, the card may fall back
to text-only only when the learning reviewer confirms that the card remains
complete. An image that is required to understand the answer is not optional
and blocks acceptance.

## Independent Reviews

The workflow runs two distinct reviews against the same final draft hashes.

### Learning and factual review

For every card, the reviewer verifies:

- one clear retrieval target;
- factual support in the anchored source block and surrounding chapter;
- an accurate, concise, sufficient answer;
- an appropriate job for the learner's prior knowledge;
- useful coverage of durable outcomes;
- no duplicate, trick, giveaway, or long-quotation card; and
- a genuine recall benefit for any image.

Findings cite card ID, source anchor, and exact issue. The reviewer recommends
the type of repair; the frontier author makes substantive changes.

### Echo and package review

The second reviewer verifies:

- schema-v2 shape and duplicate-key rejection;
- stable deck identity and portable target binding;
- exact source-signature provenance;
- all source and image anchors against the block export;
- all relative image paths and image hashes;
- character limits and `manualOnly` timing;
- privacy/provenance classification;
- package manifest and checksum coverage; and
- receipt freshness against the final EPUB and review artifacts.

Both reviews must pass. Their reviewer identities, input hashes, findings,
accepted/rejected decisions, and final verdicts are recorded in
`flashcard-review.json`. They do not require routine user approval.

## Hash-Bound Flashcard Receipt

`echo-flashcard-receipt.json` records:

- schema and receipt version;
- book slug, edition ID, deck ID, and privacy classification;
- final EPUB SHA-256;
- learning- and prose-receipt SHA-256 values;
- Echo source revision and Echo CLI binary SHA-256;
- source-block export SHA-256 and source signature;
- flashcard plan and draft SHA-256 values;
- final deck SHA-256;
- ordered mnemonic image paths and SHA-256 values;
- card count, per-chapter counts, image-anchor count, and image-file count;
- both passing review verdicts and reviewed hashes; and
- generation timestamp.

The receipt fails when any input, output, review, image, source revision, or
count changes. It is generated only after both reviews pass.

## Echo Import Design

### Model additions

`FlashcardDeckImport` gains optional/additive portable-v2 fields:

- `formatVersion`;
- `deckID`;
- `targetBinding`; and
- `sourceSignature`.

Legacy decks without these fields retain current behavior.

### Import context

Echo adds a selected-book import path, conceptually:

```swift
importDeckVNext(
    from: deckURL,
    targetAudiobookID: selectedBookID,
    db: writer
)
```

For a portable v2 deck, the supplied local target is required and takes the
place of the sentinel `targetMediaID`. The sentinel is never inserted as an
audiobook ID. The legacy method remains as a wrapper for legacy decks and
continues using their embedded `targetMediaID`.

### Preflight and mutation boundary

Before deleting or inserting any deck/card rows, Echo:

1. decodes and validates the deck;
2. requires the selected-book context for portable v2;
3. loads that book's visible persisted blocks;
4. recomputes the Echo-owned source signature;
5. requires an exact signature match;
6. resolves every required source anchor;
7. resolves or safely degrades optional image references under existing image
   rules; and
8. constructs the complete write set.

A mismatch or unresolved required anchor returns an actionable error with zero
deck/card database mutation.

### Idempotent re-import

Portable v2 uses `deckID` as the persistent deck-table identity. Importing the
same edition again replaces that deck's cards after successful preflight rather
than creating duplicates. Legacy name-based behavior remains unchanged for
legacy decks.

### User surfaces

- iOS Book Settings adds **Import Study Deck for This Book**.
- macOS adds the equivalent active-book action.
- The existing global deck importer recognizes a portable v2 deck. If no book
  context is active, it asks the user to choose a library book before preflight.
- The result reports imported card count, anchored card count, image count, and
  warnings.

Selecting the file and, when necessary, the target book are the only routine
user steps. There is no per-card confirmation gate.

### Review behavior

Imported cards are persisted as ordinary enabled flashcards with the existing
new-card scheduling defaults. They appear in normal session/FSRS review.
`manualOnly` prevents playback-trigger insertion but does not exclude the card
from study sessions or play-in-context behavior.

## Failure Behavior

- Missing or stale learning/prose receipts: no deck generation.
- Failed governed EPUB build: no source export or deck generation.
- Missing, unapproved, or hash-mismatched Echo CLI: no Echo-ready claim.
- Source export without the required v2 signature: no portable deck.
- Missing or ambiguous source anchor: deck acceptance fails.
- Source-signature mismatch during import: import fails with zero card/deck
  database mutation.
- Character-limit, duplicate-card, or schema failure: affected cards return to
  targeted revision.
- Optional mnemonic failure: text-only fallback only after learning review.
- Required image failure: deck acceptance fails.
- EPUB or manuscript rebuild: all downstream deck evidence becomes stale.
- Failed review or stale flashcard receipt: package is not complete.
- Private artifact in a public destination: delivery fails.

An EPUB/M4B package may be surfaced as explicitly labelled interim output when
flashcards are blocked, but it is not reported as a complete learning package.

## Packaging and Delivery

The package manifest adds:

- deck filename and SHA-256;
- deck format version and stable deck ID;
- source-signature algorithm/value;
- total and per-chapter card counts;
- `imageAnchor` and `imageFile` counts;
- ordered mnemonic image inventory and hashes;
- flashcard receipt hash;
- review verdicts; and
- minimum compatible Echo revision.

The governed delivery operation treats the deck JSON, mnemonic image directory,
manifest/checksum entries, and receipt evidence as one deck bundle. A partial
deck-bundle copy cannot produce a successful package result.

Public-safe decks may accompany public-safe books in `books/<slug>/` and the
approved iCloud/public delivery surfaces. Private or sensitive decks, images,
and source evidence remain with the private book. Private artifacts never enter
the public repo or public KB.

## Verification Strategy

Implementation follows test-driven development in each repository.

### Explainer Audiobooks

Tests cover:

- deterministic deck and receipt generation;
- schema-v2 required fields and duplicate-key rejection;
- stable deck ID and portable target sentinel;
- source signature copied exactly from Echo output;
- anchors against the exact block export;
- front/back limits, required `manualOnly`, card distribution, and duplicate
  detection;
- `imageAnchor` / `imageFile` exclusivity and safe relative paths;
- missing files, stale hashes, stale reviews, and EPUB rebuild invalidation;
- both production skills requiring the default deck;
- longform handoff carrying the deck strategy;
- package manifest/checksum and privacy rules; and
- installed shared-skill parity after the canonical skill changes.

### Echo

Tests cover:

- legacy and portable-v2 JSON decoding;
- deterministic source signatures independent of local audiobook IDs and file
  paths;
- `export-blocks` v2 signature output;
- selected local target overriding the portable sentinel;
- source-signature mismatch causing zero database mutation;
- every required anchor resolving into the selected book;
- stable `deckID` re-import without duplication;
- image-anchor and image-file behavior under selected-book import;
- ordinary session/FSRS review eligibility with `manualOnly` playback timing;
- existing legacy import behavior remaining unchanged; and
- iOS/macOS target-book import presentation and result handling.

Swift builds and tests use the required memory-pressure gate. Echo hosted
`Build gate + tests` is followed to completion after its PR is opened.

## Rollout and Repository Boundaries

The work lands as coordinated, independently reviewable changes:

1. Echo feature branch based on `origin/nightly`, PR into `nightly`.
2. Explainer Audiobooks feature branch based on `origin/main`, PR into `main`.
3. Canonical skill installation/parity verification after the Explainer change.
4. Narrow business-KB update recording the implemented portable-deck layer and
   leaving `.echo` archives as a future wrapper.

The Explainer implementation records the exact reviewed Echo source revision.
Packages cannot claim portable-v2 compatibility until the required Echo import
behavior exists in a build available to the intended tester.

## Master Plan Impact

This work advances the existing Echo learning flywheel and beta-testing
direction. It does not change portfolio priority, launch order, pricing, or
automation cadence. It promotes a previously deferred V2 study-deck capability
into an approved implementation while keeping the larger `.echo` archive out of
scope.

## Acceptance Criteria

The feature is complete when:

- all three learning-book skills carry the approved flashcard responsibilities;
- every new completed production run defaults to a compact reviewed deck unless
  the brief records an explicit opt-out;
- the exact final EPUB is parsed by Echo's own export path;
- the deck carries only portable anchors and a portable source signature;
- no local filesystem path is used as the target identity;
- Echo can bind the same deck to matching local copies on Mac and iPhone;
- a wrong-book signature fails before database mutation;
- cards enter normal session/FSRS review without interrupting playback;
- stable deck IDs make same-edition re-import idempotent;
- figures and mnemonic images obey the selective visual and privacy rules;
- both independent reviews pass against final hashes;
- the flashcard receipt, package manifest, and checksums agree;
- public/private delivery boundaries remain intact;
- relevant local tests pass in both repositories;
- Echo hosted CI status is known; and
- the KB records the shipped boundary accurately.
