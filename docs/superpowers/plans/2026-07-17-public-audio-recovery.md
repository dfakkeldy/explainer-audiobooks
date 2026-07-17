# Public Audio Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Recover eight already-narrated public books, give every public M4B a governed square companion cover derived from its EPUB identity, and produce a verified public package commit without changing narration or EPUB bytes.

**Architecture:** Add one recovery-specific verifier and receipt format rather than weakening the normal paired-cover contract. Six legacy packages receive a `legacy-cover-pair.json` receipt that binds the unchanged portrait/EPUB to a newly rendered square cover; all nine remuxes (eight recovered books plus Rodents) use the existing media-signature-preserving artwork replacement path. A public manifest records safe hashes and counts, while absolute archive paths remain in an ignored local source map.

**Tech Stack:** Python 3.12, `unittest`, Pillow, ffmpeg/ffprobe, AtomicParsley, Echo Release `echo-cli`, JSON, EPUB ZIP inspection, existing governed cover renderer.

## Global Constraints

- Work from a clean feature worktree based on current `origin/main`; preserve unrelated files in the user's main checkout.
- Recovered slugs are exactly: `echo-from-the-inside`, `why-it-feels-right`, `you-are-the-architect`, `the-bug-is-a-clue`, `tests-first`, `git-happens`, `findable`, and `the-voice-in-the-machine`.
- New square companions are exactly: `you-are-the-architect`, `the-bug-is-a-clue`, `tests-first`, `git-happens`, `the-voice-in-the-machine`, and `rodents-in-the-walls`.
- Existing portrait `cover.png` files and all thirteen current EPUBs remain byte-identical.
- Existing governed square assets remain byte-identical for the other seven public books.
- M4B artwork must be 2400 × 2400; EPUB artwork must remain 1600 × 2560.
- The recovered sidecar bytes must equal the selected archive sidecar bytes.
- Before/after M4B decoded audio-packet SHA-256, duration, chapters, stream structure, and non-artwork tags must be identical.
- Every alignment anchor must resolve to a block exported from the current public EPUB and timestamps must be non-empty and monotonic.
- No individual committed file may reach GitHub's 100 MiB ordinary-Git limit.
- No absolute archive path, private narration scratch, or ignored recovery material may enter a tracked file.
- Do not push or create a PR until Dan explicitly acknowledges that the package PR is ready to exist.
- Use the bundled Python runtime:
  `/Users/dfakkeldy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3`.

---

## File Map

**Create**

- `skill/scripts/public_audio_recovery.py` — pure receipt/block validation plus `record` and `verify` CLI commands.
- `tests/test_public_audio_recovery.py` — unit and repository acceptance tests for the recovery contract.
- `docs/audio-recovery-2026-07/manifest.json` — safe public evidence for eight recoveries and the Rodents remux.
- `docs/audio-recovery-2026-07/square-companions.json` — ordered contact-sheet input.
- `docs/audio-recovery-2026-07/square-companions.png` — six-cover defect-review sheet.
- `books/<six-slugs>/m4b-cover-source.png` — approved square source art.
- `books/<six-slugs>/m4b-cover-spec.json` — deterministic square typography/layout spec.
- `books/<six-slugs>/m4b-cover.png` — canonical square M4B cover.
- `books/<six-slugs>/m4b-cover-thumbnail.png` — 240-pixel review thumbnail.
- `books/<six-slugs>/m4b-cover.render.json` — deterministic render receipt.
- `books/<six-slugs>/legacy-cover-pair.json` — recovery-specific binding of portrait, EPUB, square, and M4B artwork.
- `books/<eight-recovered-slugs>/<slug>.m4b` and `<slug>.alignment.json` — recovered public media.

**Modify**

- `.gitignore` — exclude `.recovery/`.
- `books/<eight-recovered-slugs>/README.md` — document browser audio and paired artwork.
- `books/rodents-in-the-walls/rodents-in-the-walls.m4b` — replace portrait artwork only.
- `books/rodents-in-the-walls/README.md` — document the square companion/remux receipt.

**Do not modify**

- Any `books/<slug>/cover.png`.
- Any `books/<slug>/<slug>.epub`.
- Any manuscript, pronunciation plan, or private delivery package.

---

### Task 1: Recovery Verifier and Legacy Pair Receipt

**Files:**

- Create: `skill/scripts/public_audio_recovery.py`
- Create: `tests/test_public_audio_recovery.py`
- Modify: `.gitignore`

**Interfaces:**

- Produces: `verify_block_parity(sidecar_path: Path, blocks_path: Path) -> tuple[int, int]`.
- Produces: `verify_legacy_cover_pair(book_dir: Path, receipt_path: Path) -> None`.
- Produces: `write_legacy_cover_pair(book_dir: Path, candidate_id: str, direction_name: str) -> Path`.
- Produces: `build_recovery_manifest(repo_root: Path, source_map_path: Path, blocks_dir: Path) -> dict[str, object]`.
- Produces: `verify_recovery_manifest(repo_root: Path, manifest_path: Path, blocks_dir: Path) -> None`.
- CLI: `public_audio_recovery.py record --repo ROOT --sources SOURCES --blocks-dir DIR --out FILE`.
- CLI: `public_audio_recovery.py verify --repo ROOT --manifest FILE --blocks-dir DIR`.
- CLI: `public_audio_recovery.py record-cover --book-dir DIR --candidate-id ID --direction-name NAME`.

- [ ] **Step 1: Add `.recovery/` to the ignore contract**

Append this exact line to `.gitignore` with `apply_patch`:

```gitignore
.recovery/
```

- [ ] **Step 2: Write focused failing unit tests**

Create tests that use temporary JSON/PNG/ZIP fixtures and assert these exact behaviors:

```python
def test_block_parity_requires_every_anchor_and_monotonic_time(self):
    self.write_json("sidecar.json", [
        {"blockId": "a", "timestamp": 0.0},
        {"blockId": "b", "timestamp": 1.5},
    ])
    self.write_json("blocks.json", {"blocks": [{"id": "a"}, {"id": "b"}]})
    self.assertEqual(verify_block_parity(self.path("sidecar.json"), self.path("blocks.json")), (2, 2))

def test_block_parity_rejects_unresolved_anchor(self):
    self.write_json("sidecar.json", [{"blockId": "missing", "timestamp": 0.0}])
    self.write_json("blocks.json", {"blocks": [{"id": "present"}]})
    with self.assertRaisesRegex(ValueError, "unresolved anchor"):
        verify_block_parity(self.path("sidecar.json"), self.path("blocks.json"))

def test_manifest_rejects_absolute_paths(self):
    with self.assertRaisesRegex(ValueError, "absolute path"):
        validate_public_json({"source": "/Users/example/archive/book.m4b"})
```

Run:

```bash
PY=/Users/dfakkeldy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
"$PY" -m unittest tests.test_public_audio_recovery -v
```

Expected: FAIL because `public_audio_recovery` does not exist.

- [ ] **Step 3: Implement the minimal pure validation core**

Use these constants and exact receipt fields:

```python
RECOVERED_SLUGS = (
    "echo-from-the-inside", "why-it-feels-right", "you-are-the-architect",
    "the-bug-is-a-clue", "tests-first", "git-happens", "findable",
    "the-voice-in-the-machine",
)
REMUXED_SLUGS = RECOVERED_SLUGS + ("rodents-in-the-walls",)
LEGACY_PAIR_SLUGS = (
    "you-are-the-architect", "the-bug-is-a-clue", "tests-first",
    "git-happens", "the-voice-in-the-machine", "rodents-in-the-walls",
)
MAX_GIT_BLOB_BYTES = 100 * 1024 * 1024

LEGACY_PAIR_FIELDS = {
    "schema_version", "book_slug", "edition_id", "candidate_id", "direction_name",
    "selection_source", "privacy", "portrait", "square",
}
```

`verify_block_parity` must require a non-empty sidecar list, numeric monotonic timestamps, non-empty string `blockId` values, a `{"blocks": [...]}` export, and 100% ID resolution. `validate_public_json` must recursively reject strings beginning with `/`, `file://`, or a Windows drive prefix.

`verify_legacy_cover_pair` must require:

```json
{
  "schema_version": 1,
  "book_slug": "the-bug-is-a-clue",
  "edition_id": "public-audio-recovery-2026-07",
  "candidate_id": "revealing-shadow",
  "direction_name": "Revealing Shadow",
  "selection_source": "user-approved-derivation",
  "privacy": {"classification": "public-safe", "permission_to_publish": true},
  "portrait": {
    "path": "cover.png",
    "sha256": "64 lowercase hex characters",
    "dimensions": [1600, 2560],
    "epub_path": "the-bug-is-a-clue.epub",
    "epub_sha256": "64 lowercase hex characters",
    "epub_cover_member": "OEBPS/cover.png",
    "epub_cover_sha256": "same hash as portrait.sha256"
  },
  "square": {
    "path": "m4b-cover.png",
    "sha256": "64 lowercase hex characters",
    "dimensions": [2400, 2400],
    "source_path": "m4b-cover-source.png",
    "source_sha256": "64 lowercase hex characters",
    "spec_path": "m4b-cover-spec.json",
    "spec_sha256": "64 lowercase hex characters",
    "render_path": "m4b-cover.render.json",
    "render_sha256": "64 lowercase hex characters",
    "thumbnail_path": "m4b-cover-thumbnail.png",
    "thumbnail_sha256": "64 lowercase hex characters"
  }
}
```

The verifier must recompute every hash and dimension, inspect the EPUB member with `zipfile.ZipFile`, and call `normalized_m4b_art_sha256()` when `<slug>.m4b` exists.

- [ ] **Step 4: Add manifest record/verify behavior**

The local source-map input is schema 1 and contains nine entries with absolute `m4b` paths and eight recovered `sidecar` paths. `build_recovery_manifest` must consume those paths but emit only relative public paths, hashes, counts, and serialized `MediaSignature` values. Each public record must have this shape:

```json
{
  "slug": "echo-from-the-inside",
  "source_m4b_sha256": "...",
  "source_sidecar_sha256": "...",
  "final_m4b_path": "books/echo-from-the-inside/echo-from-the-inside.m4b",
  "final_m4b_sha256": "...",
  "final_sidecar_path": "books/echo-from-the-inside/echo-from-the-inside.alignment.json",
  "final_sidecar_sha256": "...",
  "epub_path": "books/echo-from-the-inside/echo-from-the-inside.epub",
  "epub_sha256": "...",
  "anchor_count": 547,
  "exported_block_count": 0,
  "resolved_anchor_count": 547,
  "portrait_sha256": "...",
  "square_sha256": "...",
  "source_media_signature": {},
  "final_media_signature": {}
}
```

`exported_block_count` is computed live and must be positive; `0` above documents type only and is never accepted. The source and final media-signature dictionaries must compare exactly. Rodents has no `source_sidecar_sha256` field because its public sidecar is not being recovered; every other record requires it.

- [ ] **Step 5: Run focused tests green and commit**

Run:

```bash
"$PY" -m unittest tests.test_public_audio_recovery -v
"$PY" -m unittest tests.test_replace_m4b_cover tests.test_cover_receipts -v
git diff --check
```

Expected: all tests PASS.

Commit:

```bash
git add .gitignore skill/scripts/public_audio_recovery.py tests/test_public_audio_recovery.py
git commit -m "feat: add public audio recovery verifier"
```

---

### Task 2: Six Approved Square Cover Companions

**Files:**

- Create the six per-book `m4b-cover-*` assets and `legacy-cover-pair.json` files listed in the File Map.
- Create: `docs/audio-recovery-2026-07/square-companions.json`
- Create: `docs/audio-recovery-2026-07/square-companions.png`
- Modify: `tests/test_public_audio_recovery.py`

**Interfaces:**

- Consumes: `verify_legacy_cover_pair(book_dir: Path, receipt_path: Path) -> None`.
- Produces: six canonical `m4b-cover.png` files suitable for `replace_m4b_cover.py`.

- [ ] **Step 1: Write the failing repository cover-contract test**

Add a test that loops over `LEGACY_PAIR_SLUGS`, asserts that every listed square asset exists, calls `verify_legacy_cover_pair`, and separately records the SHA-256 of every `cover.png` and EPUB before any generation. Run it and confirm six missing-asset failures.

- [ ] **Step 2: Record immutable portrait and EPUB baselines**

Write the untracked baseline to `.recovery/portrait-epub-baseline.json` using a short Python command that records each public slug's `cover.png` and EPUB SHA-256. Do not stage this file. Verify `git check-ignore .recovery/portrait-epub-baseline.json` succeeds.

- [ ] **Step 3: Create one square source image per approved concept**

Use the `imagegen` skill in image-edit mode with each current `cover.png` as the reference. Preserve the visual thesis, materials, palette, and emotional tone; recompose for 1:1 with no typography, logo, badge, border, letterboxing, or blind center crop. Use exactly these identities:

| Slug | Candidate ID | Direction | Required thesis | Accent |
|---|---|---|---|
| `you-are-the-architect` | `directed-construction` | Directed Construction | conductor's baton directing modular construction pieces | `#E43D30` |
| `the-bug-is-a-clue` | `revealing-shadow` | Revealing Shadow | one beetle casting an unmistakable magnifying-glass shadow | `#F28C28` |
| `tests-first` | `safety-block` | Safety Block | falling cobalt dominoes stopped by one transparent safety block | `#2364FF` |
| `git-happens` | `the-deliberate-knot` | The Deliberate Knot | branching red thread repaired with one deliberate knot | `#D62828` |
| `the-voice-in-the-machine` | `sentence-to-sound` | Sentence to Sound | blank paper entering a physical acoustic machine and leaving as an amber sound ribbon | `#FF9F1C` |
| `rodents-in-the-walls` | `c2a-compact-ribbon-editorial-footer` | Compact Ribbon / Editorial Footer | the existing warm domestic rodent-shadow scene and orange/navy identity | `#EF5735` |

Save the accepted edit directly as `books/<slug>/m4b-cover-source.png`; this is a mismatch/defect check, not an alternative-selection round.

- [ ] **Step 4: Author deterministic 2400 × 2400 specs**

Create schema-version-2 square specs using the existing `cover-spec.json` schema and these exact text values:

| Slug | Title | Subtitle | Author |
|---|---|---|---|
| `you-are-the-architect` | You Are the Architect | From vibe coding to agentic engineering | Dan Fakkeldy |
| `the-bug-is-a-clue` | The Bug Is a Clue | A Beginner's Guide to Debugging in Xcode | Dan Fakkeldy |
| `tests-first` | Tests First | Test-Driven Development in Swift | Dan Fakkeldy |
| `git-happens` | Git Happens | Version Control for People Who Ship Software | Dan Fakkeldy |
| `the-voice-in-the-machine` | The Voice in the Machine | How a Phone Learned to Read Any Book Aloud | Dan Fakkeldy |
| `rodents-in-the-walls` | Rodents in the Walls | Squirrels and Other Houseguests in Western Cape Breton | Dan Fakkeldy |

Each spec must declare `"variant": "square"`, a 2400 × 2400 canvas, 120-pixel safe margin, its direction ID/name, the exact source path `m4b-cover-source.png`, and typography that remains legible on the generated 240-pixel thumbnail.

- [ ] **Step 5: Render all six governed covers**

For each slug run:

```bash
"$PY" skill/scripts/make_cover.py \
  --spec "books/$slug/m4b-cover-spec.json" \
  --out "books/$slug/m4b-cover.png"
```

Expected output names are `m4b-cover.png`, `m4b-cover-thumbnail.png`, and `m4b-cover.render.json`. Inspect each full-size cover and thumbnail; repair only defects such as clipped type, mismatched concept, accidental text in source art, or weak thumbnail contrast.

- [ ] **Step 6: Create the six legacy pair receipts**

Run `public_audio_recovery.py record-cover` once per row using the exact candidate ID and direction name in the table. The command writes `legacy-cover-pair.json` atomically after hashing and validating every referenced artifact. Every receipt must use `selection_source: user-approved-derivation`, `public-safe`, and `permission_to_publish: true`. Run the verifier before accepting the files.

- [ ] **Step 7: Build and inspect the ordered contact sheet**

Create `square-companions.json` as an ordered array of `{ "title", "cover" }` objects in the table order above, then run:

```bash
"$PY" skill/scripts/make_cover_contact_sheet.py \
  --manifest docs/audio-recovery-2026-07/square-companions.json \
  --out docs/audio-recovery-2026-07/square-companions.png
```

Inspect the sheet for six distinct titles, correct concept matching, square geometry, and no portrait stretching.

- [ ] **Step 8: Prove portrait/EPUB immutability and run tests**

Recompute all thirteen baseline hashes and compare to `.recovery/portrait-epub-baseline.json`; the comparison must produce no differences. Run:

```bash
"$PY" -m unittest tests.test_public_audio_recovery tests.test_cover_spec tests.test_cover_renderer -v
git diff --check
```

Expected: PASS.

- [ ] **Step 9: Commit the six companions**

Stage only the six book asset sets, the contact-sheet files, and the focused test change. Commit:

```bash
git commit -m "feat: add legacy square audiobook covers"
```

---

### Task 3: Recover, Remux, and Prove the Nine Public M4Bs

**Files:**

- Create: eight recovered M4Bs and eight recovered sidecars.
- Modify: `books/rodents-in-the-walls/rodents-in-the-walls.m4b`.
- Create: `docs/audio-recovery-2026-07/manifest.json`.
- Modify: `tests/test_public_audio_recovery.py`.

**Interfaces:**

- Consumes: the local schema-1 source map at `$RECOVERY_SOURCES_FILE`.
- Consumes: the Echo CLI at `$ECHO_CLI`.
- Consumes: `replace_m4b_cover.py` and the nine canonical `m4b-cover.png` files.
- Produces: a green `public_audio_recovery.py verify` result and the exact package commit consumed by the site plan.

- [ ] **Step 1: Build the failing package acceptance test**

Extend `tests/test_public_audio_recovery.py` to assert all eight recovered M4B/sidecar pairs exist, each file is below `MAX_GIT_BLOB_BYTES`, the manifest covers exactly `REMUXED_SLUGS`, anchor counts equal the accepted audit values below, and `verify_recovery_manifest` succeeds.

```python
EXPECTED_ANCHORS = {
    "echo-from-the-inside": 547,
    "why-it-feels-right": 400,
    "you-are-the-architect": 444,
    "the-bug-is-a-clue": 525,
    "tests-first": 223,
    "git-happens": 461,
    "findable": 263,
    "the-voice-in-the-machine": 535,
}
```

Run and confirm failure because the recovery manifest and eight public media pairs are absent.

- [ ] **Step 2: Prepare the ignored source map and staging tree**

Set `RECOVERY_SOURCES_FILE` to a local JSON file outside Git. Re-discover every candidate live, hash it, and choose the exact M4B/sidecar pairs whose counts match `EXPECTED_ANCHORS`. Copy the selected source bytes into `.recovery/source/<slug>/`; for Rodents, copy the current committed M4B there before replacing it. Run `git status --short` and confirm `.recovery/` is absent.

- [ ] **Step 3: Export current EPUB blocks**

Set:

```bash
ECHO_CLI=/Users/dfakkeldy/Developer/Echo/.build/cli/Build/Products/Release/echo-cli
test -x "$ECHO_CLI"
mkdir -p .recovery/blocks
```

For each recovered slug run:

```bash
"$ECHO_CLI" export-blocks \
  --epub "books/$slug/$slug.epub" \
  --out ".recovery/blocks/$slug.json"
```

Then call `verify_block_parity` for all eight sidecars. Expected totals are exactly the eight counts above with zero unresolved anchors.

- [ ] **Step 4: Copy the eight sidecars byte-for-byte**

Copy each selected sidecar to `books/<slug>/<slug>.alignment.json`. Verify its SHA-256 still equals the selected source sidecar SHA before proceeding.

- [ ] **Step 5: Remux only embedded artwork**

For each of the nine `REMUXED_SLUGS`, write to `.recovery/final/<slug>.m4b` first:

```bash
"$PY" skill/scripts/replace_m4b_cover.py \
  --m4b ".recovery/source/$slug/$slug.m4b" \
  --cover "books/$slug/m4b-cover.png" \
  --out ".recovery/final/$slug.m4b"
```

For schema-2 paired books also pass `--cover-selection books/$slug/cover-selection.json --portrait-cover books/$slug/cover.png`. For the six legacy-companion books, the recovery verifier supplies the equivalent binding through `legacy-cover-pair.json`; do not make `replace_m4b_cover.py` accept a weaker normal-package receipt.

- [ ] **Step 6: Promote the verified binaries**

Only after all nine replacement commands succeed, copy the eight recovered finals to their book directories and atomically replace the Rodents M4B. Check every final is below 100 MiB before staging.

- [ ] **Step 7: Record and verify the public manifest**

Run:

```bash
"$PY" skill/scripts/public_audio_recovery.py record \
  --repo . \
  --sources "$RECOVERY_SOURCES_FILE" \
  --blocks-dir .recovery/blocks \
  --out docs/audio-recovery-2026-07/manifest.json

"$PY" skill/scripts/public_audio_recovery.py verify \
  --repo . \
  --manifest docs/audio-recovery-2026-07/manifest.json \
  --blocks-dir .recovery/blocks
```

Expected: nine verified media signatures, eight complete sidecar/block joins, no absolute paths, and no errors.

- [ ] **Step 8: Perform full media verification**

For every final M4B:

```bash
ffprobe -v error -show_streams -show_chapters -show_format \
  -of json "books/$slug/$slug.m4b" > ".recovery/probes/$slug.json"
ffmpeg -v error -i "books/$slug/$slug.m4b" -map 0:a:0 -f null -
```

For every recovered EPUB run `unzip -t`. Compare source/final media signatures through the manifest verifier and compare normalized embedded artwork to `m4b-cover.png`.

- [ ] **Step 9: Run the focused and full suites**

```bash
"$PY" -m unittest tests.test_public_audio_recovery tests.test_replace_m4b_cover tests.test_cover_receipts -v
"$PY" -m unittest discover -s tests -v
"$PY" tools/validate_skills.py
git diff --check
```

Expected: PASS with no warnings treated as failures.

- [ ] **Step 10: Commit the recovery package**

Stage explicit book paths, the manifest, and the acceptance test only. Inspect `git diff --cached --stat` and `git status --short --branch`; no `.recovery` path may appear. Commit:

```bash
git commit -m "feat: recover public audiobook packages"
```

---

### Task 4: Package Documentation and Final Local Gate

**Files:**

- Modify: eight recovered book READMEs.
- Modify: `books/rodents-in-the-walls/README.md`.

**Interfaces:**

- Consumes: `docs/audio-recovery-2026-07/manifest.json`.
- Produces: the exact reviewed package HEAD handed to the dependent site plan.

- [ ] **Step 1: Update the nine READMEs**

For each recovered book, add the exact public filenames, anchor count, portrait-EPUB/square-M4B convention, and statement that browser playback is published through KinNoKi Labs. For Rodents, state that the narration and sidecar are unchanged and only embedded artwork was modernized.

- [ ] **Step 2: Re-run every immutability and package gate**

Run the Task 2 baseline comparison, Task 3 manifest verification, nine full decodes, eight `unzip -t` checks, full tests, skill validation, `git diff --check`, and `git status --short --branch`.

- [ ] **Step 3: Commit documentation**

```bash
git add books/*/README.md
git commit -m "docs: document recovered browser audiobooks"
```

Stage only the nine intended README files, not every matching directory.

- [ ] **Step 4: Capture the package handoff receipt**

Record:

```bash
git rev-parse HEAD
git status --short --branch
git log --oneline --decorate origin/main..HEAD
```

Expected: a clean feature worktree and a named exact HEAD. Present the contact sheet, manifest summary, file-size maximum, tests, and exact HEAD to Dan. Stop before push/PR and request the explicit package-PR acknowledgement required by the approved design.

---

## Package-to-Site Handoff

The site plan may begin test work locally, but its generated catalog must not be accepted until the package HEAD above is pushed and publicly reachable. The package SHA becomes `sourceCommit` in the site's paired-cover source manifest and `catalog.source.commit` in `Resources/listen/books.json`.
