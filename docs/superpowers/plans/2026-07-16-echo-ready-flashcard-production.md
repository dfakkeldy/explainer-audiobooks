# Echo-Ready Learning-Book Flashcard Production Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every newly completed learning-book run produce, independently review, verify, and transactionally deliver a compact portable Echo study deck by default, with an explicit governed opt-out.

**Architecture:** Shared Python tooling under `skill/` consumes an exact Echo `export-blocks` v2 artifact, prepares deterministic deck bytes, binds two independent reviews to those bytes, and finalizes a receipt/manifest/checksum-governed bundle. The explainer and custom-learning production skills use that one contract; longform development plans retrieval targets but defers final wording and anchors until the governed EPUB exists. Delivery remains fail-closed across public/private boundaries and cannot claim Echo-ready compatibility before the reviewed Echo revision is available.

**Tech Stack:** Python 3 standard library, JSON Schema Draft 2020-12 as a checked contract document, `unittest`/`pytest`, Markdown skill instructions, existing learning/prose receipt machinery, existing Echo CLI build/export path, SHA-256 receipts.

## Global Constraints

- Base the feature branch on `origin/main`; this repository has no `nightly`/`weekly` promotion ladder, so open the ready PR into `main`.
- Add no Python dependency; use only the standard library and existing repository tooling.
- Generate a reviewed Echo deck by default for every newly completed learning book; omission is permitted only through an explicit opt-out recorded in `flashcard-plan.json`.
- Target two or three high-value cards per substantive chapter. Zero or one is allowed only for a short orientation/closing chapter with a recorded reason; never add filler to meet a quota.
- Write final cards only after canonical chapters, learning receipt, prose receipt, and governed EPUB are final.
- The frontier author owns substantive question/answer wording. Lower-cost workers may extract, validate, assemble, and report, but may not invent or substantively rewrite accepted cards.
- Require two independent passing reviews against the same immutable candidate hashes; a passing deck ships without a routine per-deck user approval gate.
- Use `formatVersion: 2`, `targetBinding: "selectedBook"`, a portable `targetMediaID` sentinel, `echo-canonical-blocks-v1`, source anchors from the exact Echo export, and `triggerTiming: "manualOnly"`.
- Use Unicode code-point count in Python for the 160-character front and 240-character back limits; reject lone surrogate code points so the count matches Echo's Unicode-scalar validation.
- Most cards remain text-only. A declared final `imageAnchor` or `imageFile` is required; optional image failure falls back to text-only before final review by removing the reference.
- Reject absolute paths, `..`, escaping symlinks, missing image files, duplicate JSON keys, unknown schema keys, stale hashes, stale reviews, wrong source signatures, and package drift.
- Keep private source blocks, drafts, reviews, decks, images, receipts, and book packages out of the public repo and public KB.
- Public-safe finished books may live under `books/<slug>/`; do not globally ignore `*.echo-deck.json`.
- Keep full `.echo` archive packaging, APKG generation, cloze cards, scheduler changes, historic-book retrofits, and final anchor invention during longform planning out of scope.
- Keep pressure-test runs for each skill separate: RED baseline, minimal GREEN guidance, at least five fresh-context repetitions per wording variant, manual scoring of every response, REFACTOR, then commit before editing the next skill.

## Contract Corrections Locked by This Plan

Live Echo mapping found that persisted `chapterIndex` changes with audiobook chapter metadata and `isHidden` changes with user actions. The first unshipped signature is therefore `echo-canonical-blocks-v1`, copied byte-for-byte from Echo's v2 export. Python never recreates that digest. The export may include `chapterIndex` as authoring metadata, but the builder treats it as non-identity metadata.

The finalizer operates after deterministic candidate creation. Both reviewers inspect and approve the exact candidate bytes plus EPUB/export/plan/draft hashes; finalization copies those candidate bytes unchanged. This makes the technical review meaningful while preserving the approved rule that no receipt or deliverable exists before both reviews pass.

Every declared image in the reviewed candidate is required at import. Optional image fallback is an authoring decision made before review, not a silent Echo import degradation.

---

### Task 1: Record RED Skill-Behavior Baselines

**Files:**
- Create: `docs/superpowers/skill-tests/2026-07-16-echo-ready-flashcards-explainer-red.md`
- Create: `docs/superpowers/skill-tests/2026-07-16-echo-ready-flashcards-custom-red.md`
- Create: `docs/superpowers/skill-tests/2026-07-16-echo-ready-flashcards-longform-red.md`
- Create later in Tasks 6-8: one GREEN/REFACTOR evidence file per skill

**Interfaces:**
- Consumes: the current unmodified `explainer-audiobook`, `custom-learning-audiobook`, and `longform-book-development` skill instructions.
- Produces: reproducible evidence of the exact omissions/rationalizations that the subsequent instruction changes must correct.

- [ ] **Step 1: Create the first implementation worktree from current `main`**

Run:

```bash
git fetch origin
git worktree add \
  /Users/dfakkeldy/.codex/worktrees/echo-ready-flashcards-explainer/explainer-audiobooks \
  -b codex/echo-ready-flashcards-explainer origin/main
cd /Users/dfakkeldy/.codex/worktrees/echo-ready-flashcards-explainer/explainer-audiobooks
git status --short --branch
```

Expected: a clean branch named `codex/echo-ready-flashcards-explainer` tracking the current `origin/main`.

- [ ] **Step 2: Run five fresh-context repetitions for each explainer control variant**

For each of the five variants below, dispatch five fresh subagents without the proposed flashcard reference: 25 independent no-guidance controls. Give each the same base prompt and append exactly one variant sentence:

```text
You are completing a public-safe beginner learning audiobook. The canonical chapters, learning receipt, prose receipt, EPUB, M4B, cover, and checksums already pass. The requester chose low friction and is unavailable for another approval. One existing book figure genuinely helps recall. Follow the currently installed explainer-audiobook skill and return the exact remaining actions and completion claim you would make. Do not infer requirements that are not in the skill.
```

Variants:

1. `The introduction and closing are short; the six middle chapters are substantive.`
2. `The book has no useful generated images, only one useful in-book figure.`
3. `A source rebuild changed the EPUB after an earlier draft deck was discussed.`
4. `The delivery target is the public repo plus iCloud Books.`
5. `The user explicitly asks whether the learning package is complete now.`

Manually read and score all 25 complete responses. Record the prompt variant, run number, response, missing default deck behavior, missing final-EPUB anchor gate, missing reviews/receipt, and verbatim rationalization in the RED evidence file. Automated keyword counts may assist but never replace manual scoring.

- [ ] **Step 3: Record custom-learning and longform controls without editing them**

Run five fresh-context repetitions for each of five variants of both exact base prompts: 25 custom controls and 25 longform controls. Record custom responses in `2026-07-16-echo-ready-flashcards-custom-red.md` and longform responses in `2026-07-16-echo-ready-flashcards-longform-red.md`:

```text
CUSTOM: A private beta learning book is nearly complete. Canonical prose and audio gates pass, the requester chose low friction and is offline, and one mnemonic image would help. Follow only the currently installed custom-learning-audiobook skill. State the artifacts, reviews, delivery action, and completion claim.

LONGFORM: Plan an eight-chapter learning book with a short orientation, six substantive chapters, and a short closing. The production handoff will later use custom-learning-audiobook. Follow only the current longform-book-development skill. Produce the flashcard-related part of the handoff without drafting manuscript prose.
```

For custom variants, vary private/public destination, stale EPUB, image failure, unavailable reviewer, and explicit completion question. For longform variants, vary misconceptions, mechanisms, comparisons, existing figures, and mnemonic opportunities. Manually score every response and record run number plus verbatim rationalization. These are no-guidance control observations only; do not edit either skill yet.

- [ ] **Step 4: Commit the immutable behavioral RED evidence**

Run:

```bash
git add docs/superpowers/skill-tests/2026-07-16-echo-ready-flashcards-explainer-red.md \
  docs/superpowers/skill-tests/2026-07-16-echo-ready-flashcards-custom-red.md \
  docs/superpowers/skill-tests/2026-07-16-echo-ready-flashcards-longform-red.md
git commit -m "test: capture flashcard skill behavior gaps"
```

Expected: the commit succeeds and the repository test suite remains green. Task 6 adds the mechanical RED immediately before the explainer skill edit.

### Task 2: Exact Echo v2 Export and Provenance Gate

**Files:**
- Create: `skill/scripts/echo_block_export.py`
- Create: `tests/test_echo_block_export.py`
- Create: `tests/fixtures/echo-source-blocks-v2.json`

**Interfaces:**
- Consumes: governed EPUB path, clean Echo checkout at an approved 40-character SHA, memory-gate path, and destination paths.
- Produces: the unmodified Echo v2 JSON plus `research/echo-source-export-receipt.json`; `resolve_reviewed_echo_cli` returns `EchoExportProvenance`, and `export_blocks_v2` returns the decoded export object.

- [ ] **Step 1: Write provenance and atomic-export tests**

Create tests around an injected command runner and temporary Git fixture. The primary public contract is:

```text
@dataclass(frozen=True)
class EchoExportProvenance:
    echo_revision: str
    cli_path: Path
    cli_sha256: str


resolve_reviewed_echo_cli(
    echo_repo: Path,
    approved_sha: str,
    gate: Path,
    *,
    run: CommandRunner = subprocess.run,
) -> EchoExportProvenance


export_blocks_v2(
    epub: Path,
    output: Path,
    provenance_output: Path,
    provenance: EchoExportProvenance,
    *,
    run: CommandRunner = subprocess.run,
) -> dict[str, object]
```

Tests must cover non-hex SHA, symbolic ref, wrong HEAD, dirty checkout, missing gate, gate failure, build failure, unexpected Release path, missing CLI, CLI hash, EPUB hash, CLI nonzero exit, malformed JSON, duplicate keys, export version 1, wrong algorithm, malformed digest, missing blocks, output byte preservation, receipt fields, and no partial output after any failure.

- [ ] **Step 2: Run export tests and verify RED**

Run:

```bash
/usr/local/bin/python3 -m unittest tests.test_echo_block_export -v
```

Expected: import failure because `skill.scripts.echo_block_export` does not exist.

- [ ] **Step 3: Implement exact-SHA CLI resolution**

Use these fixed rules:

```python
APPROVED_SHA = re.compile(r"[0-9a-f]{40}\Z")
EXPECTED_CLI = Path(".build/cli/Build/Products/Release/echo-cli")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
```

Require `git rev-parse HEAD == approved_sha` and empty `git status --porcelain`; execute `[gate, "--wait"]`; execute `make echo-cli` with `cwd=echo_repo`; resolve only `echo_repo / EXPECTED_CLI`; require a regular executable file; and return its SHA-256. Do not check out, reset, clean, or modify the supplied Echo repository.

- [ ] **Step 4: Implement unmodified v2 export plus a separate receipt**

Run the exact CLI as `[cli, "export-blocks", "--epub", epub, "--out", temporary_output]`. Parse with a duplicate-key-rejecting loader. Require version 2, algorithm `echo-canonical-blocks-v1`, `sha256:` plus 64 lowercase hex digits, at least one block, unique portable block IDs, and Boolean `isFrontMatter` on every block. Atomically rename the original temporary bytes to `output`; never reserialize them.

Write canonical JSON for the separate receipt with these exact keys:

```json
{
  "receiptVersion": 1,
  "echoRevision": "0123456789abcdef0123456789abcdef01234567",
  "echoCLISHA256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "epubSHA256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "exportSHA256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
  "sourceSignature": {
    "algorithm": "echo-canonical-blocks-v1",
    "value": "sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
  },
  "generatedAt": "2026-07-16T12:00:00Z"
}
```

Those digest values are valid-shape fixture data, not trusted production values; production always derives them from the supplied reviewed revision and files.

- [ ] **Step 5: Add the CLI and commit**

Expose `build` as the only subcommand with required `--epub`, `--echo-repo`, `--approved-sha`, `--gate`, `--output`, and `--receipt` arguments. Run:

```bash
/usr/local/bin/python3 -m unittest tests.test_echo_block_export -v
/usr/local/bin/python3 skill/scripts/echo_block_export.py --help
git diff --check
git add skill/scripts/echo_block_export.py tests/test_echo_block_export.py \
  tests/fixtures/echo-source-blocks-v2.json
git commit -m "feat: gate Echo source block exports"
```

Expected: all export tests pass, help exits 0, and the fixture is a valid v2 export from the reviewed Echo CLI rather than hand-authored JSON.

### Task 3: Strict Flashcard Schemas, Templates, and Candidate Validation

**Files:**
- Create: `skill/schemas/echo-deck-v2.schema.json`
- Create: `skill/templates/flashcards/flashcard-plan.json`
- Create: `skill/templates/flashcards/flashcard-draft.json`
- Create: `skill/templates/flashcards/flashcard-review.json`
- Create: `skill/templates/flashcards/instructions.md`
- Create: `skill/scripts/echo_flashcard_bundle.py`
- Create: `tests/test_echo_deck_schema.py`
- Create: `tests/test_echo_flashcard_bundle.py`

**Interfaces:**
- Consumes: strict plan, draft, review, and exact Echo export JSON.
- Produces: duplicate-key rejection, semantic validators, and deterministic `prepare` output at `research/echo-deck-candidate.json`.

- [ ] **Step 1: Write schema and validator tests**

Tests must load every template with duplicate-key rejection and validate a minimal good deck plus one failure per rule: unknown property at every object level, wrong version/binding/algorithm, nonportable sentinel, invalid deck ID, no cards, whitespace text, scalar limit, missing/malformed anchor, timestamps, non-manual timing, both image fields, unsafe image path, lone surrogate, duplicate card ID, duplicate normalized Q/A pair, missing chapter exception, filler-card reason, and generated-image majority.

The duplicate normalizer is exactly:

```python
def normalize_duplicate_text(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())
```

- [ ] **Step 2: Run schema/bundle tests and verify RED**

Run:

```bash
/usr/local/bin/python3 -m unittest \
  tests.test_echo_deck_schema tests.test_echo_flashcard_bundle -v
```

Expected: import/file failures because the schema, templates, and bundle module do not exist.

- [ ] **Step 3: Write the closed v2 schema**

Use Draft 2020-12, `additionalProperties: false` recursively, and these required top-level properties:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://kinnoki.com/schemas/echo-deck-v2.schema.json",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "formatVersion", "deckID", "deckName", "targetBinding",
    "targetMediaID", "sourceSignature", "cards"
  ],
  "properties": {
    "formatVersion": {"const": 2},
    "deckID": {"type": "string", "pattern": "^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"},
    "deckName": {"type": "string", "minLength": 1},
    "targetBinding": {"const": "selectedBook"},
    "targetMediaID": {"type": "string", "pattern": "^echo-portable:[a-z0-9][a-z0-9-]*:[a-z0-9][a-z0-9.-]*$"},
    "sourceSignature": {"$ref": "#/$defs/sourceSignature"},
    "cards": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/card"}}
  },
  "$defs": {
    "sourceSignature": {
      "type": "object",
      "additionalProperties": false,
      "required": ["algorithm", "value"],
      "properties": {
        "algorithm": {"const": "echo-canonical-blocks-v1"},
        "value": {"type": "string", "pattern": "^sha256:[0-9a-f]{64}$"}
      }
    },
    "card": {
      "type": "object",
      "additionalProperties": false,
      "required": ["frontText", "backText", "sourceAnchor", "triggerTiming"],
      "properties": {
        "frontText": {"type": "string", "minLength": 1, "maxLength": 160},
        "backText": {"type": "string", "minLength": 1, "maxLength": 240},
        "sourceAnchor": {"type": "string", "pattern": "^s[0-9]+-b[0-9]+$"},
        "triggerTiming": {"const": "manualOnly"},
        "imageAnchor": {"type": "string", "pattern": "^s[0-9]+-b[0-9]+$"},
        "imageFile": {"type": "string", "pattern": "^deck-images/[A-Za-z0-9._/-]+$"}
      },
      "not": {"required": ["imageAnchor", "imageFile"]}
    }
  }
}
```

The final deck deliberately omits draft-only stable card IDs; `flashcard-draft.json` retains them for review decisions, while candidate card order and the candidate hash bind those decisions to shipped bytes. Timestamp keys are forbidden by the closed card object. The Python validator additionally enforces whitespace, Unicode scalar, lone-surrogate, path-component, and typed-anchor semantics because JSON Schema length/pattern behavior alone is insufficient.

Make the plan and draft templates valid, closed examples with these exact top-level and nested fields:

```json
{
  "planVersion": 1,
  "bookSlug": "sample-book",
  "editionID": "2026-07",
  "state": "enabled",
  "optOutEvidence": null,
  "durableOutcomes": [
    {"id": "outcome-1", "statement": "Explain the core mechanism."}
  ],
  "chapters": [
    {
      "chapterFile": "01-orientation.md",
      "chapterClass": "orientation",
      "durableOutcomeIDs": [],
      "retrievalTargets": [],
      "expectedCardCount": 0,
      "belowRangeReason": "Orientation only; no durable retrieval target.",
      "visualOpportunities": []
    },
    {
      "chapterFile": "02-mechanism.md",
      "chapterClass": "substantive",
      "durableOutcomeIDs": ["outcome-1"],
      "retrievalTargets": [
        {"id": "target-1", "job": "mechanism", "description": "Reconstruct the core mechanism."},
        {"id": "target-2", "job": "application", "description": "Apply the mechanism to a new case."}
      ],
      "expectedCardCount": 2,
      "belowRangeReason": null,
      "visualOpportunities": [
        {"kind": "existing-figure", "description": "Use the mechanism diagram only if it improves recall."}
      ]
    }
  ]
}
```

```json
{
  "draftVersion": 1,
  "bookSlug": "sample-book",
  "editionID": "2026-07",
  "deckName": "Sample Book — Core Review",
  "cards": [
    {
      "id": "card-mechanism-1",
      "chapterFile": "02-mechanism.md",
      "retrievalTargetID": "target-1",
      "job": "mechanism",
      "frontText": "What sequence makes the mechanism work?",
      "backText": "The input changes state, the gate accepts it, and the result is carried forward.",
      "sourceAnchor": "s1-b4",
      "imageDecision": "text-only"
    }
  ]
}
```

The allowed `state` values are `enabled` and `explicit-opt-out`; an opt-out requires nonempty evidence and no draft. Allowed chapter classes are `orientation`, `substantive`, and `closing`. Allowed jobs are `definition`, `importance`, `mechanism`, `application`, `comparison`, `misconception`, and `visual-cue`. `imageDecision` is exactly one of `text-only`, `image-anchor`, or `image-file`, and the corresponding image field is required only for the latter two values.

- [ ] **Step 4: Implement strict loaders and domain types**

Create these concrete boundaries:

```python
class FlashcardBundleError(ValueError):
    pass


def load_unique_json(path: Path, label: str) -> object:
    def reject_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise FlashcardBundleError(f"{label}: duplicate JSON key: {key}")
            result[key] = value
        return result
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicates)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise FlashcardBundleError(f"{label}: cannot load strict JSON: {error}") from error


def canonical_json_bytes(payload: object) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")
```

Add these frozen domain values:

```python
@dataclass(frozen=True)
class EchoSourceSignature:
    algorithm: str
    value: str


@dataclass(frozen=True)
class EchoBlock:
    id: str
    kind: str
    text: str
    chapter_index: int | None
    sequence_index: int
    word_count: int | None
    is_front_matter: bool
    image_path: str | None


@dataclass(frozen=True)
class EchoBlockExport:
    version: int
    source_signature: EchoSourceSignature
    blocks: Sequence[EchoBlock]
    block_by_id: Mapping[str, EchoBlock]


@dataclass(frozen=True)
class PortableDeckCandidate:
    payload: Mapping[str, object]
    encoded: bytes
    card_count_by_chapter: Mapping[str, int]
    mnemonic_image_paths: Sequence[Path]


@dataclass(frozen=True)
class FlashcardBundleVerification:
    classification: str
    deck_path: Path
    receipt_path: Path
    governed_paths: Sequence[Path]
```

`load_echo_block_export_v2` copies the signature value; no function in this module may compute an Echo source signature. It rejects duplicate block IDs before constructing `block_by_id`.

- [ ] **Step 5: Implement plan/draft validation and deterministic candidate preparation**

`validate_flashcard_plan` requires enabled or explicit opt-out, substantive chapter classifications, expected count/range, below-range reason, durable outcome links, and visual opportunity decisions. `validate_flashcard_draft` requires one candidate per stable card ID, allowed card job, chapter binding by exported structural metadata, and safe images. Build one block map by portable ID and enforce the same typed-anchor rule as Echo:

```python
TEXT_KINDS = frozenset({"heading", "paragraph", "sentence"})


def validate_card_anchors(card: dict[str, object], blocks: dict[str, EchoBlock]) -> None:
    source_anchor = require_string(card, "sourceAnchor")
    source = blocks.get(source_anchor)
    if source is None:
        raise FlashcardBundleError(f"unknown sourceAnchor: {source_anchor}")
    if source.kind not in TEXT_KINDS or source.is_front_matter:
        raise FlashcardBundleError(
            f"sourceAnchor must resolve to non-front-matter text: {source_anchor}"
        )
    image_anchor = card.get("imageAnchor")
    if image_anchor is not None:
        if not isinstance(image_anchor, str) or not image_anchor:
            raise FlashcardBundleError("imageAnchor must be a non-empty string")
        image = blocks.get(image_anchor)
        if image is None or image.kind != "image":
            raise FlashcardBundleError(
                f"imageAnchor must resolve to an image block: {image_anchor}"
            )
```

Add named RED/GREEN tests for a source anchor pointing at an image, a source anchor pointing at front matter, and an image anchor pointing at text. Derive identifiers exactly:

```python
deck_id = f"com.kinnoki.learning-book.{slug}.{edition_id}.core"
target_media_id = f"echo-portable:{slug}:{edition_id}"
```

Require `slug` to match `[a-z0-9][a-z0-9-]*` and `edition_id` to match `[a-z0-9][a-z0-9.-]*`. `prepare` writes canonical candidate bytes atomically; a repeated run with identical inputs must be byte-identical.

- [ ] **Step 6: Verify candidate construction and commit**

Run:

```bash
/usr/local/bin/python3 -m unittest \
  tests.test_echo_deck_schema tests.test_echo_flashcard_bundle -v
/usr/local/bin/python3 skill/scripts/echo_flashcard_bundle.py --help
git diff --check
git add skill/schemas/echo-deck-v2.schema.json \
  skill/templates/flashcards/flashcard-plan.json \
  skill/templates/flashcards/flashcard-draft.json \
  skill/templates/flashcards/flashcard-review.json \
  skill/templates/flashcards/instructions.md \
  skill/scripts/echo_flashcard_bundle.py \
  tests/test_echo_deck_schema.py tests/test_echo_flashcard_bundle.py
git commit -m "feat: prepare deterministic Echo deck candidates"
```

Expected: schema and prepare tests pass; no deliverable receipt is produced yet.

### Task 4: Independent Review Binding, Receipt, Manifest, and Verification

**Files:**
- Modify: `skill/scripts/echo_flashcard_bundle.py`
- Modify: `tests/test_echo_flashcard_bundle.py`
- Create: `tests/fixtures/flashcard-review-passing.json`

**Interfaces:**
- Consumes: canonical chapters directory, candidate, plan, draft, two existing learning/prose receipts, EPUB, Echo export/provenance receipt, generated images, and two independent review records.
- Produces: unchanged `dist/<slug>.echo-deck.json`, `research/flashcard-review.json`, `research/echo-flashcard-receipt.json`, byte-identical packaged `dist/flashcard-receipt.json`, updated `dist/manifest.json`, and updated `dist/SHA256SUMS`.

- [ ] **Step 1: Write finalization freshness tests**

Cover two distinct reviewer identities/roles, both verdicts pass, reviewed hash set equality, candidate bytes copied unchanged, EPUB hash, learning/prose receipt hashes, export/provenance hashes, image inventory, per-chapter counts, review aggregation, deterministic manifest/checksum rows, and verify-after-finalize. Mutate each input one at a time and assert `verify` fails. Assert no final deck/receipt/manifest/checksum exists after any failed finalization.

The required reviewed artifact object is:

```python
reviewed_artifacts = {
    "epubSHA256": sha256_file(epub),
    "echoSourceExportSHA256": sha256_file(source_export),
    "echoSourceExportReceiptSHA256": sha256_file(source_export_receipt),
    "echoCLISHA256": source_export_receipt_payload["echoCLISHA256"],
    "flashcardPlanSHA256": sha256_file(plan),
    "flashcardDraftSHA256": sha256_file(draft),
    "deckCandidateSHA256": sha256_file(candidate),
    "mnemonicImages": [
        {"path": path.as_posix(), "sha256": sha256_file(bundle_root / path)}
        for path in ordered_mnemonic_image_paths
    ],
}
```

Before constructing this object, require the provenance receipt's EPUB hash, export hash, source signature, Echo revision, and CLI hash to match the supplied EPUB/export and their strict shapes. Both review records must contain an object exactly equal to this value. Tests mutate every scalar, reorder the image inventory, change one image byte, change the provenance receipt, and change the CLI hash inside the provenance receipt; every mutation must invalidate both reviews before final output.

- [ ] **Step 2: Run finalization tests and verify RED**

Run:

```bash
/usr/local/bin/python3 -m unittest \
  tests.test_echo_flashcard_bundle.FlashcardFinalizeTests -v
```

Expected: failures because `finalize_flashcard_bundle` and receipt verification do not exist.

- [ ] **Step 3: Validate independent reviews against one immutable candidate**

`flashcard-review.json` is a closed object with `reviewVersion: 1`, the exact `reviewedArtifacts` object above, and exactly two entries in `reviews`. Each review repeats that same object. Require roles `learning` and `echo-package`, distinct nonempty reviewer IDs, nonempty model/run provenance, `verdict: "pass"`, per-card decisions covering every candidate card ID, and no unresolved severity `error` finding. The learning review checks learning/factual quality and image benefit; the technical review checks portable shape, typed anchors, images, privacy, provenance, and package counts.

- [ ] **Step 4: Finalize by copying reviewed bytes and writing one hash-bound receipt**

Before hashing either receipt, validate it against the exact canonical chapters:

```python
from learning_design_qc import verify_learning_receipt
from prose_qc import verify_style_receipt

learning_payload = verify_learning_receipt(chapters_dir, learning_receipt)
prose_payload = verify_style_receipt(chapters_dir, prose_receipt)
```

The `finalize` CLI therefore requires `--chapters-dir`, `--learning-receipt`, and `--prose-receipt`; a non-passing or stale receipt fails before final output. After both validators pass, copy candidate bytes unchanged to `dist/<slug>.echo-deck.json`. Write receipt version 1 with exact slug, edition ID, deck ID, classification, EPUB/learning/prose/Echo CLI/export/provenance/plan/draft/candidate/final deck hashes, source signature, ordered images, card counts, per-chapter counts, image counts, reviewer identities/verdicts/hashes, and UTC timestamp. Publish those exact receipt bytes to both `research/echo-flashcard-receipt.json` and `dist/flashcard-receipt.json`.

For a flashcard-enabled complete run, require machine-readable `dist/manifest.json`. Add one closed `echoStudyDeck` object containing filename/hash, version, deck ID, source signature, counts, image inventory, receipt hash, review verdicts, and `minimumCompatibleEchoRevision`. Rewrite `dist/SHA256SUMS` in sorted POSIX-path order and include the deck, images, flashcard receipt, manifest, EPUB, M4B, cover, and all other governed deliverables already present.

Construct every output byte in memory, including copied mnemonic images, before publication. Publish the full set through one rollback boundary rooted at the run directory:

```python
def publish_outputs_atomically(
    run_root: Path,
    outputs: dict[Path, bytes],
    *,
    fail_after: int | None = None,
    post_publish_check: Callable[[], None] | None = None,
    publication_order: Sequence[Path] | None = None,
) -> None:
    staging = Path(tempfile.mkdtemp(prefix=".flashcard-finalize-", dir=run_root))
    backup = Path(tempfile.mkdtemp(prefix=".flashcard-backup-", dir=run_root))
    published: list[tuple[Path, Path | None]] = []
    try:
        for relative, data in outputs.items():
            if relative.is_absolute() or ".." in relative.parts:
                raise FlashcardBundleError(f"unsafe output path: {relative}")
            staged = staging / relative
            staged.parent.mkdir(parents=True, exist_ok=True)
            staged.write_bytes(data)
        ordered = list(publication_order) if publication_order is not None else sorted(
            outputs, key=lambda path: path.as_posix()
        )
        if len(ordered) != len(outputs) or set(ordered) != set(outputs):
            raise FlashcardBundleError("publication order must name every output exactly once")
        for index, relative in enumerate(ordered, 1):
            destination = run_root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            prior: Path | None = None
            if destination.exists():
                prior = backup / relative
                prior.parent.mkdir(parents=True, exist_ok=True)
                os.replace(destination, prior)
            published.append((destination, prior))
            try:
                os.replace(staging / relative, destination)
            except Exception:
                published.pop()
                if prior is not None:
                    os.replace(prior, destination)
                raise
            if fail_after == index:
                raise FlashcardBundleError(f"injected publication failure after {index}")
        if post_publish_check is not None:
            post_publish_check()
    except Exception:
        for destination, prior in reversed(published):
            destination.unlink(missing_ok=True)
            if prior is not None:
                prior.parent.mkdir(parents=True, exist_ok=True)
                os.replace(prior, destination)
        raise
    finally:
        shutil.rmtree(staging, ignore_errors=True)
        shutil.rmtree(backup, ignore_errors=True)
```

Tests inject failure after every publication index and assert the entire pre-finalize tree is byte-identical afterward.

- [ ] **Step 5: Add `prepare`, `finalize`, and `verify` CLI subcommands**

Use explicit required path arguments; never discover the newest run by glob. `prepare` requires `--plan`, `--draft`, `--source-export`, `--bundle-root`, `--slug`, `--edition-id`, and `--output`. `finalize` requires those inputs plus `--chapters-dir`, `--epub`, `--learning-receipt`, `--prose-receipt`, `--source-export-receipt`, `--candidate`, `--review`, `--run-root`, and `--minimum-echo-revision`. `verify` requires `--run-root`, `--chapters-dir`, and every receipt/export source path, reloads strict JSON, recomputes every non-Echo hash/count, validates typed anchors against the preserved export, checks that the source signature is copied exactly, checks both review artifact objects, and compares manifest/checksum entries. It returns 0 only when the complete bundle agrees.

- [ ] **Step 6: Verify finalization and commit**

Run:

```bash
/usr/local/bin/python3 -m unittest tests.test_echo_flashcard_bundle -v
/usr/local/bin/python3 skill/scripts/echo_flashcard_bundle.py --help
git diff --check
git add skill/scripts/echo_flashcard_bundle.py \
  tests/test_echo_flashcard_bundle.py \
  tests/fixtures/flashcard-review-passing.json
git commit -m "feat: finalize reviewed Echo deck bundles"
```

Expected: deterministic finalization and all stale-input tests pass.

### Task 5: Transactional Delivery and Privacy Enforcement

**Files:**
- Create: `skill/scripts/sync_flashcard_bundle.py`
- Create: `tests/test_sync_flashcard_bundle.py`

**Interfaces:**
- Consumes: a verified final run directory, existing delivery root, declared intent, and public/private destination classification.
- Produces: dry-run or rollback-safe publication of the exact governed deck paths; `sync_flashcard_bundle` returns `FlashcardSyncResult`, and `verify-delivery` proves the copied bundle.

- [ ] **Step 1: Write dry-run, privacy, and rollback tests**

Cover exact changed-file set, dry-run immutability, private-to-public rejection, public-safe acceptance, missing deck/receipt/manifest/checksum, unsafe image path, symlink escape, source corruption, destination corruption, failure injected after each publication point, restoration of every prior destination byte, removal of newly created paths, and successful post-copy verification.

The public boundary is:

```text
@dataclass(frozen=True)
class FlashcardSyncResult:
    changed_paths: Sequence[str]
    applied: bool
    destination: Path


sync_flashcard_bundle(
    bundle_root: Path,
    destination: Path,
    *,
    intent: str,
    apply: bool,
    public_destination: bool,
    fail_after: int | None = None,
) -> FlashcardSyncResult
```

- [ ] **Step 2: Run delivery tests and verify RED**

Run:

```bash
/usr/local/bin/python3 -m unittest tests.test_sync_flashcard_bundle -v
```

Expected: import failure because the synchronization module does not exist.

- [ ] **Step 3: Implement governed path classification and synchronization**

Publish exactly the deck path from `manifest.echoStudyDeck.filename`, ordered `deck-images/` inventory, `flashcard-receipt.json`, `manifest.json`, and `SHA256SUMS`. `verify_final_bundle_tree` returns those paths as a sorted tuple only after strict receipt/manifest/checksum agreement. Reject path aliases, absolute paths, backslashes, `..`, symlinks, unlisted files, and classification mismatches before creating a staging directory.

Implement the synchronization body by reusing Task 4's tested rollback primitive:

```python
from echo_flashcard_bundle import (
    FlashcardBundleError,
    publish_outputs_atomically,
    verify_delivered_flashcard_bundle,
    verify_final_bundle_tree,
)


def sync_flashcard_bundle(
    bundle_root: Path,
    destination: Path,
    *,
    intent: str,
    apply: bool,
    public_destination: bool,
    fail_after: int | None = None,
) -> FlashcardSyncResult:
    if intent not in {"public-safe", "private-reading-copy"}:
        raise FlashcardBundleError(f"unsupported delivery intent: {intent}")
    verification = verify_final_bundle_tree(bundle_root)
    if verification.classification != intent:
        raise FlashcardBundleError(
            f"bundle classification {verification.classification} does not match {intent}"
        )
    if public_destination and intent != "public-safe":
        raise FlashcardBundleError("private bundle cannot use a public destination")
    changed = tuple(path.as_posix() for path in verification.governed_paths)
    if not apply:
        return FlashcardSyncResult(changed, False, destination)
    if destination.is_symlink():
        raise FlashcardBundleError(f"destination must not be a symlink: {destination}")
    destination.mkdir(parents=True, exist_ok=True)
    outputs = {
        path: (bundle_root / path).read_bytes()
        for path in verification.governed_paths
    }
    publish_outputs_atomically(
        destination,
        outputs,
        fail_after=fail_after,
        post_publish_check=lambda: verify_delivered_flashcard_bundle(
            bundle_root, destination
        ),
        publication_order=verification.governed_paths,
    )
    return FlashcardSyncResult(changed, True, destination)
```

- [ ] **Step 4: Implement journaled atomic publication**

`verification.governed_paths` is the explicit tested publication order: deck, ordered images, receipt, manifest, then checksums. After every replacement, support the test-only `fail_after` injection. On any error, restore backups in reverse order and remove newly created paths. The `post_publish_check` callback runs delivered-bundle verification before backups are deleted, so verification failure uses the same rollback journal.

- [ ] **Step 5: Add CLI and commit**

Provide `plan`, `apply`, and `verify-delivery` subcommands with required `--bundle-root`, `--destination`, `--intent {public-safe,private-reading-copy}`, and `--public-destination {yes,no}`. Run:

```bash
/usr/local/bin/python3 -m unittest tests.test_sync_flashcard_bundle -v
/usr/local/bin/python3 skill/scripts/sync_flashcard_bundle.py --help
git diff --check
git add skill/scripts/sync_flashcard_bundle.py tests/test_sync_flashcard_bundle.py
git commit -m "feat: deliver flashcard bundles transactionally"
```

Expected: every injected failure restores the original destination exactly and successful delivery verifies.

### Task 6: GREEN, REFACTOR, and Deploy the Shared Explainer Skill

**Files:**
- Create: `skill/references/echo-ready-flashcards.md`
- Modify: `skill/SKILL.md:182-241,290-346,495-589,629-721`
- Modify: `skill/references/learning-design.md`
- Create: `tests/test_skill_flashcard_contract.py`
- Create: `docs/superpowers/skill-tests/2026-07-16-echo-ready-flashcards-explainer-green.md`

**Interfaces:**
- Consumes: Tasks 2-5 tools and the current explainer workflow.
- Produces: default-on production behavior, exact governed commands/artifacts, explicit opt-out, independent review, fail-closed completion, and pressure-test evidence.

- [ ] **Step 1: Add and run the mechanical explainer RED test**

Create a `unittest.TestCase` so the documented runner executes a nonzero test count:

```python
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ExplainerFlashcardContractTests(unittest.TestCase):
    def test_explainer_skill_requires_default_echo_deck(self) -> None:
        explainer = (ROOT / "skill/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("echo-ready-flashcards.md", explainer)
        self.assertIn("explicit opt-out", explainer)
        self.assertIn("echo_flashcard_bundle.py finalize", explainer)


if __name__ == "__main__":
    unittest.main()
```

Run:

```bash
/usr/local/bin/python3 -m unittest tests.test_skill_flashcard_contract -v
```

Expected: exactly one test runs and fails because the explainer skill lacks the flashcard contract. Append the exact output to the explainer RED evidence file; do not commit this red state.

- [ ] **Step 2: Write the canonical reference as the single source of truth**

Include these exact sections: Default and Opt-Out; Planning Before Final EPUB; Governed Echo Export; Frontier Authorship; Card Distribution and Jobs; Selective Images; Deterministic Candidate; Independent Reviews; Finalization and Receipt; Transactional Delivery; Failure and Interim Output; Privacy; Commands; Completion Checklist. State explicitly that final card wording and anchors happen only after final EPUB export, and that every present image reference is required.

The completion checklist requires all of these paths or a verified opt-out receipt:

```text
research/flashcard-plan.json
research/echo-source-blocks.json
research/echo-source-export-receipt.json
research/flashcard-draft.json
research/echo-deck-candidate.json
research/flashcard-review.json
research/echo-flashcard-receipt.json
dist/<slug>.echo-deck.json
dist/manifest.json
dist/SHA256SUMS
```

- [ ] **Step 3: Add minimal routing and gates to `skill/SKILL.md`**

At intake, set `flashcards: enabled` unless the requester explicitly opts out. At chapter planning, record durable outcomes, retrieval targets, chapter class, expected count, and visual opportunities. After EPUB build and receipt verification, run the exact Echo export gate, `prepare`, two fresh independent review runs, `finalize`, `verify`, delivery plan/apply, and `verify-delivery`. Register every new reference/script/schema/template in the skill resource list.

The skill must say: `An EPUB/M4B-only package is interim, not complete, when flashcards are enabled and any flashcard gate is blocked.`

- [ ] **Step 4: Run the mechanical GREEN test**

Run:

```bash
/usr/local/bin/python3 -m unittest tests.test_skill_flashcard_contract -v
/usr/local/bin/python3 tools/validate_skills.py
```

Expected: the complete mechanical contract suite passes. Custom-learning and longform assertions are not added until their own RED phases.

- [ ] **Step 5: Repeat the behavioral tests with the skill loaded**

Dispatch five fresh subagents for every variant with the updated explainer skill. Repeat the exact five RED variants and add five variants changing: one useful figure, failed mnemonic generation, stale EPUB, unavailable requester, and public destination. This is 50 independent GREEN samples. Require every response to default to the deck, wait for final EPUB, invoke two reviews without user approval, fail closed on stale/unsafe artifacts, and label blocked packages interim.

Manually score every response and record prompt variant, run number, response, pass/fail, and remaining loophole in the GREEN evidence file. Tighten only `skill/references/echo-ready-flashcards.md` or the minimal routing sentence that the failure demonstrates; rerun the affected variant five fresh times after each change.

- [ ] **Step 6: Commit the completed explainer skill cycle**

Run:

```bash
git add skill/references/echo-ready-flashcards.md skill/SKILL.md \
  skill/references/learning-design.md tests/test_skill_flashcard_contract.py \
  docs/superpowers/skill-tests/2026-07-16-echo-ready-flashcards-explainer-green.md
git commit -m "feat: default explainer books to Echo flashcards"
```

Expected: the explainer pressure cycle is green and committed before custom-learning edits begin.

- [ ] **Step 7: Verify and publish the tooling plus explainer skill PR**

Run the focused tool suites, full repository suite, and skill validation before publishing:

```bash
/usr/local/bin/python3 -m unittest tests.test_echo_block_export -v
/usr/local/bin/python3 -m unittest tests.test_echo_flashcard_bundle -v
/usr/local/bin/python3 -m unittest tests.test_echo_deck_schema -v
/usr/local/bin/python3 -m unittest tests.test_sync_flashcard_bundle -v
/usr/local/bin/python3 -m unittest tests.test_skill_flashcard_contract -v
/usr/local/bin/python3 -m pytest -q
/usr/local/bin/python3 tools/validate_skills.py
git diff --check
git status --short --branch
git fetch origin
git rebase origin/main
git push -u origin codex/echo-ready-flashcards-explainer
gh pr create --base main --head codex/echo-ready-flashcards-explainer \
  --title "feat: produce reviewed Echo study decks" \
  --body-file /tmp/explainer-flashcards-pr.md
gh pr checks --watch --fail-fast
```

Before creating the PR, write `/tmp/explainer-flashcards-pr.md` with exact Echo provenance, pressure-test evidence, focused/full test counts, atomicity fault-injection coverage, and the public/private boundary. End-to-end production fixture hashes are not claimed until Task 10 creates them. Expected: all tests pass, a ready PR into `main` is opened, and hosted-check status is known.

- [ ] **Step 8: STOP until the explainer skill is merged and deployed**

Do not edit `custom-learning-audiobook` yet. After the PR is reviewed and merged, require a clean canonical checkout, fast-forward it to `origin/main`, and verify all installed explainer links resolve to the canonical `skill/` directory:

```bash
git -C /Users/dfakkeldy/Developer/explainer-audiobooks status --short --branch
git -C /Users/dfakkeldy/Developer/explainer-audiobooks fetch origin
git -C /Users/dfakkeldy/Developer/explainer-audiobooks merge --ff-only origin/main
for base in .codex .agents .claude .hermes; do
  test "$(readlink "$HOME/$base/skills/explainer-audiobook")" = \
    /Users/dfakkeldy/Developer/explainer-audiobooks/skill
done
```

Expected: the canonical checkout is clean and current, every link resolves correctly, and a fresh agent using the installed explainer skill passes the final pressure scenario. If the canonical checkout is dirty or the PR is unmerged, stop and report that deployment gate rather than beginning Task 7.

### Task 7: RED, GREEN, REFACTOR, and Deploy the Custom-Learning Production Skill

**Files:**
- Modify: `skills/custom-learning-audiobook/SKILL.md:123-500`
- Modify: `skills/custom-learning-audiobook/references/package-and-qc.md`
- Modify: `tools/validate_custom_learning_skill_install.py`
- Modify: `tests/test_custom_learning_audiobook_echo_contract.py`
- Modify: `tests/test_custom_learning_audiobook_install_contract.py`
- Modify: `tests/test_skill_flashcard_contract.py`
- Create: `docs/superpowers/skill-tests/2026-07-16-echo-ready-flashcards-custom-green.md`

**Interfaces:**
- Consumes: canonical shared flashcard reference/scripts via the repo root.
- Produces: private/public custom-learning runs with the same default-on, reviewed, governed deck contract and installed-skill manifest parity.

- [ ] **Step 1: Start from deployed `main` and add failing custom-learning assertions**

Create a fresh isolated worktree/branch from the now-deployed `origin/main`:

```bash
git fetch origin
git worktree add \
  /Users/dfakkeldy/.codex/worktrees/echo-ready-flashcards-custom/explainer-audiobooks \
  -b codex/echo-ready-flashcards-custom origin/main
cd /Users/dfakkeldy/.codex/worktrees/echo-ready-flashcards-custom/explainer-audiobooks
```

Require the custom skill and package reference to name every canonical script, exact run path, both reviewer roles, default/opt-out, machine-readable manifest, transactional delivery, privacy classification, and interim-package wording. Extend `SKILL_MANIFEST` only for files actually added inside the custom skill directory; the shared scripts remain under `skill/` and must not be duplicated.

Run:

```bash
/usr/local/bin/python3 -m unittest \
  tests.test_custom_learning_audiobook_echo_contract \
  tests.test_custom_learning_audiobook_install_contract \
  tests.test_skill_flashcard_contract -v
```

Expected: custom flashcard assertions fail while existing pronunciation/install assertions remain green.

- [ ] **Step 2: Route custom production through canonical shared tooling**

Add the flashcard plan to intake/run layout. After final EPUB and receipts, invoke the shared Echo export, candidate, review, finalize, verify, delivery plan/apply, and delivered verification commands. Require the exact approved Echo SHA and record CLI provenance. Require `dist/manifest.json` for flashcard-enabled completion. For a private run, permit iCloud Books only when the requester explicitly asked for a private reading copy; otherwise keep the deck in the private project folder.

- [ ] **Step 3: Repeat the full custom pressure cycle**

Repeat each of the five original CUSTOM control variants five times, then run five new variants—private client data, public-safe repackaging, mnemonic failure, stale EPUB, and no active requester—five fresh times each. Manually score all 50 responses. Passing behavior must preserve privacy, remove an optional image before review or block a required image, run both reviews automatically, and never call an EPUB/M4B-only handoff complete.

Record verbatim evidence and loophole fixes in the custom GREEN file. Do not edit longform files during this cycle.

- [ ] **Step 4: Verify and commit the custom cycle**

Run:

```bash
/usr/local/bin/python3 -m unittest \
  tests.test_custom_learning_audiobook_echo_contract \
  tests.test_custom_learning_audiobook_install_contract \
  tests.test_skill_flashcard_contract -v
/usr/local/bin/python3 tools/validate_custom_learning_skill_install.py
git diff --check
git add skills/custom-learning-audiobook/SKILL.md \
  skills/custom-learning-audiobook/references/package-and-qc.md \
  tools/validate_custom_learning_skill_install.py \
  tests/test_custom_learning_audiobook_echo_contract.py \
  tests/test_custom_learning_audiobook_install_contract.py \
  tests/test_skill_flashcard_contract.py \
  docs/superpowers/skill-tests/2026-07-16-echo-ready-flashcards-custom-green.md
git commit -m "feat: govern custom learning flashcard delivery"
```

Expected: focused tests pass. On the feature branch, the live installed-parity command may truthfully return exit 2 `pending-integration`; that is recorded, not disguised as current parity.

- [ ] **Step 5: Publish the custom-learning PR and STOP until deployment**

Run:

```bash
/usr/local/bin/python3 -m pytest -q
/usr/local/bin/python3 tools/validate_skills.py
git diff --check
git status --short --branch
git fetch origin
git rebase origin/main
git push -u origin codex/echo-ready-flashcards-custom
gh pr create --base main --head codex/echo-ready-flashcards-custom \
  --title "feat: deliver custom learning Echo decks" \
  --body-file /tmp/custom-learning-flashcards-pr.md
gh pr checks --watch --fail-fast
```

Expected: full tests pass, a ready PR is open, and hosted-check status is known. Do not edit longform files until this PR is merged. After merge, fast-forward the clean canonical checkout and require `/usr/local/bin/python3 tools/validate_custom_learning_skill_install.py` to exit 0. Run one fresh installed-skill pressure scenario and record its passing result before Task 8.

### Task 8: GREEN and REFACTOR the Longform Planning Skill

**Files:**
- Modify: `skills/longform-book-development/SKILL.md`
- Modify: `skills/longform-book-development/references/handoff-packet.md`
- Modify: `tests/test_skill_flashcard_contract.py`
- Create: `docs/superpowers/skill-tests/2026-07-16-echo-ready-flashcards-longform-green.md`

**Interfaces:**
- Consumes: audience, durable outcomes, chapter architecture, misconceptions, mechanisms, comparisons, applications, and visual opportunities.
- Produces: a plan-only `Flashcard Strategy` handoff section; no final card wording and no source anchors.

- [ ] **Step 1: Start from deployed `main` in a fresh longform worktree**

Run:

```bash
git fetch origin
git worktree add \
  /Users/dfakkeldy/.codex/worktrees/echo-ready-flashcards-longform/explainer-audiobooks \
  -b codex/echo-ready-flashcards-longform origin/main
cd /Users/dfakkeldy/.codex/worktrees/echo-ready-flashcards-longform/explainer-audiobooks
git status --short --branch
```

Expected: a clean branch containing the deployed explainer and custom-learning cycles.

- [ ] **Step 2: Strengthen the failing handoff contract test**

Require these literal handoff fields:

```text
## Flashcard Strategy
- State: enabled | explicit-opt-out
- Opt-out evidence:
- Durable outcomes:
- Chapter retrieval targets:
- Retrieval-job coverage:
- Existing figure opportunities:
- Mnemonic-image opportunities:
- Short-chapter exceptions:
- Production constraint: Do not write final card text or Echo source anchors before the governed EPUB export.
```

Run the longform test method and verify it fails before editing the skill.

- [ ] **Step 3: Add the plan-only workflow and handoff**

Default `State` to `enabled`; require explicit user evidence for opt-out. For every substantive chapter, record two or three likely retrieval targets spanning supported mechanism/misconception/application/comparison jobs. For short orientation/closing chapters, record zero/one targets and a reason. Mark figures and mnemonic opportunities as opportunities only. State twice—once in the workflow and once in the handoff template—that final wording, portable anchors, source signature, and image binding belong to production after the final EPUB.

- [ ] **Step 4: Repeat the full longform pressure cycle**

Repeat each of the five original LONGFORM control variants five times, then run five new variants five fresh times each. Manually score all 50 responses. A pass includes a complete strategy and production boundary without drafting final Q/A or inventing `s<i>-b<j>` anchors. Record exact outputs, failures, and narrow instruction fixes in the longform GREEN evidence file; rerun any affected variant five times after a wording change.

- [ ] **Step 5: Verify and commit the longform cycle**

Run:

```bash
/usr/local/bin/python3 -m unittest tests.test_skill_flashcard_contract -v
/usr/local/bin/python3 tools/validate_skills.py
git diff --check
git add skills/longform-book-development/SKILL.md \
  skills/longform-book-development/references/handoff-packet.md \
  tests/test_skill_flashcard_contract.py \
  docs/superpowers/skill-tests/2026-07-16-echo-ready-flashcards-longform-green.md
git commit -m "feat: plan flashcards in longform handoffs"
```

Expected: all three skill contract groups pass and the longform skill remains planning-only.

### Task 9: Installed-Skill Parity and Public Documentation

**Files:**
- Create: `tools/validate_learning_book_skill_install.py`
- Create: `tests/test_learning_book_skill_install_contract.py`
- Modify: `tools/validate_skills.py`
- Modify: `README.md`
- Modify: `docs/make-your-own.md`
- Modify: `docs/how-these-were-made.md`
- Modify: `docs/superpowers/specs/2026-07-15-echo-ready-flashcards-design.md`

**Interfaces:**
- Consumes: final candidate skill trees and canonical checkout/install symlinks.
- Produces: byte-for-byte parity reporting (`current`, `pending-integration`, or `error`) plus accurate user documentation and corrected approved-spec status.

- [ ] **Step 1: Write parity tests before the validator**

Test regular candidate roots, recursive inventory/mode equality, byte equality, ignored `.DS_Store`/`__pycache__`, wrong symlink target, missing install, unexpected file, branch candidate differing from canonical, and all three skill families. Require exit 0/current, exit 2/pending integration, and exit 1/error.

The validator defaults are:

```python
CANONICAL_REPO = Path("/Users/dfakkeldy/Developer/explainer-audiobooks")
INSTALL_BASES = tuple(Path.home() / name / "skills" for name in (
    ".codex", ".agents", ".claude", ".hermes"
))
SKILL_ROOTS = {
    "explainer-audiobook": Path("skill"),
    "custom-learning-audiobook": Path("skills/custom-learning-audiobook"),
    "longform-book-development": Path("skills/longform-book-development"),
}
```

- [ ] **Step 2: Run parity tests and verify RED**

Run:

```bash
/usr/local/bin/python3 -m unittest \
  tests.test_learning_book_skill_install_contract -v
```

Expected: import failure because the validator does not exist.

- [ ] **Step 3: Implement inventory, byte, and symlink checks**

Compare recursive type/mode/file-byte inventories for each candidate versus canonical skill root, then require each configured installed path to be a symlink resolving to that canonical root. Ignore only `.DS_Store` and `__pycache__`. If candidate differs cleanly from canonical, print `installed_skill_parity: pending-integration` and exit 2. Structural errors or wrong links exit 1. Exact agreement exits 0. Keep the specialized custom-learning validator for Hermes/OpenClaw duplicate suppression and `skill_view` checks.

- [ ] **Step 4: Update docs and the implementation-status ledger**

Document that new completed learning books default to compact reviewed Echo decks, the explicit opt-out, ordinary Echo session review, selective visuals, final-EPUB requirement, and compatible Echo revision gate. Do not retrofit historical book READMEs. The design spec already records `Approved; coordinated implementation plans published`, `echo-canonical-blocks-v1`, and pre-review image fallback; preserve those decisions and add an implementation ledger containing the exact merged Echo, explainer, and custom-learning SHAs plus the current longform PR commit. Mark the overall status as pending final longform merge and post-merge installed parity until those gates actually pass.

- [ ] **Step 5: Verify docs/parity and commit**

Run:

```bash
/usr/local/bin/python3 -m unittest \
  tests.test_learning_book_skill_install_contract \
  tests.test_custom_learning_audiobook_install_contract -v
/usr/local/bin/python3 tools/validate_skills.py
/usr/local/bin/python3 tools/validate_learning_book_skill_install.py || test $? -eq 2
/usr/local/bin/python3 tools/validate_custom_learning_skill_install.py || test $? -eq 2
git diff --check
git add tools/validate_learning_book_skill_install.py \
  tests/test_learning_book_skill_install_contract.py tools/validate_skills.py \
  README.md docs/make-your-own.md docs/how-these-were-made.md \
  docs/superpowers/specs/2026-07-15-echo-ready-flashcards-design.md
git commit -m "docs: publish Echo flashcard production contract"
```

Expected: test validators pass; live install validators report truthful pending integration until the canonical checkout contains the merged commit.

### Task 10: Full Verification, Longform Deployment PR, Merge-Dependent Parity, and Handoff

**Files:**
- Modify only for concrete test failures: files already named in Tasks 1-9

**Interfaces:**
- Consumes: all completed tasks and the exact reviewed Echo merge SHA.
- Produces: green local suite, ready PR into `main`, known hosted-check state, and a post-merge parity receipt.

- [ ] **Step 1: Run every focused suite**

Run:

```bash
/usr/local/bin/python3 -m unittest tests.test_echo_block_export -v
/usr/local/bin/python3 -m unittest tests.test_echo_flashcard_bundle -v
/usr/local/bin/python3 -m unittest tests.test_echo_deck_schema -v
/usr/local/bin/python3 -m unittest tests.test_sync_flashcard_bundle -v
/usr/local/bin/python3 -m unittest tests.test_skill_flashcard_contract -v
/usr/local/bin/python3 -m unittest \
  tests.test_learning_book_skill_install_contract \
  tests.test_custom_learning_audiobook_install_contract -v
```

Expected: every focused test passes with a nonzero test count.

- [ ] **Step 2: Run the complete repository verification**

Run:

```bash
/usr/local/bin/python3 -m pytest -q
/usr/local/bin/python3 tools/validate_skills.py
/usr/local/bin/python3 tools/validate_learning_book_skill_install.py || test $? -eq 2
/usr/local/bin/python3 tools/validate_custom_learning_skill_install.py || test $? -eq 2
git diff --check
git status --short --branch
```

Expected: the full suite passes with at least the current baseline of 331 passing tests plus the new tests, one existing skip remains understood, skill structure validation passes, install parity is current or truthfully pending integration, diff check is silent, and only intended files are present.

- [ ] **Step 3: Run one end-to-end governed fixture**

Using a public-domain fixture EPUB and clean Echo checkout at the reviewed merge SHA: export v2 blocks and provenance; validate plan/draft; prepare candidate twice and compare bytes; run two fresh independent reviewer agents with distinct IDs; finalize; verify; plan delivery; apply to a temporary destination; verify delivery; import the deck in the Echo test fixture against the matching selected book; and prove wrong-book rejection. Save the exact command transcript and artifact hashes in the PR body, not private source text.

- [ ] **Step 4: Rebase, push, and open the ready PR**

Run:

```bash
git fetch origin
git rebase origin/main
git push -u origin codex/echo-ready-flashcards-longform
gh pr create --base main --head codex/echo-ready-flashcards-longform \
  --title "feat: plan Echo flashcards in longform handoffs" \
  --body-file /tmp/explainer-echo-flashcards-pr.md
```

Before the command, write `/tmp/explainer-echo-flashcards-pr.md` with the exact Echo SHA, signature correction, behavior-pressure evidence, local test counts, end-to-end fixture hashes, privacy boundary, and pending/current installed-parity state. Expected: branch pushes and a ready PR URL is returned.

- [ ] **Step 5: Inspect hosted checks and resolve concrete failures**

Run:

```bash
gh pr checks --watch --fail-fast
git status --short --branch
```

Expected: all configured checks pass or GitHub truthfully reports no checks. For a failure, open the job log, add a focused regression, fix the concrete cause, push, and watch again.

- [ ] **Step 6: Verify post-merge installed parity before claiming rollout complete**

After merge, update the canonical checkout safely, without overwriting user changes, then run:

```bash
/usr/local/bin/python3 tools/validate_learning_book_skill_install.py
/usr/local/bin/python3 tools/validate_custom_learning_skill_install.py
```

Expected: both exit 0 and report current. If the canonical checkout or install links cannot be updated safely, stop at `pending-integration` and report the exact path/state; do not claim installed behavior is current.

## Dependency and Release Order

The Echo implementation lands first and supplies the exact reviewed SHA. In this repository, the shared tooling plus explainer skill is one RED-GREEN-REFACTOR deployment PR; custom-learning is a second PR cut only after the first is merged and installed; longform plus final parity/docs is a third PR cut only after custom-learning is merged and installed. This sequencing is mandatory because `superpowers:writing-skills` forbids batching unverified skill edits. Final end-to-end proof, `minimumCompatibleEchoRevision`, and complete-package claims wait for a tester-installable Echo build containing the reviewed SHA. The larger `.echo` archive remains a later wrapper around the deck JSON, source identity, images, and receipts created here.
