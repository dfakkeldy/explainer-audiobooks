# Universal Paired Book Covers Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make coordinated portrait EPUB covers and square M4B/player covers the universal rule for new or refreshed audiobooks, then migrate the five non-Rodents public books listed on `kinnokilabs.com/learn`.

**Architecture:** Preserve the existing single-spec validator and renderer as focused primitives, extending them with an explicit `variant`. Add a pair orchestrator and paired receipt that bind two independently rendered layouts to one candidate and source-art identity, then make packaging and sync consume that receipt. Canonical assets remain in Explainer Audiobooks; KinNoKiLabsSite copies verified portrait and square derivatives by purpose.

**Tech Stack:** Python 3 standard library, JSON Schema 2020-12, CairoSVG/librsvg rendering, pinned OFL fonts, ffmpeg/ffprobe, AtomicParsley, EPUB ZIP tooling, Node test runner, Swift Package Manager site generator, Git/GitHub CLI.

## Global Constraints

- `cover.png` is RGB PNG at exactly 1600 × 2560; `m4b-cover.png` is RGB PNG at exactly 2400 × 2400.
- Each selected pair shares one candidate ID, one source-art hash, one palette, and one visual thesis; portrait and square may differ only in layout, crop, hierarchy, and recorded subtitle presence.
- Portrait requires exact title, subtitle, and author metadata. Square requires exact title and author; it may include the exact subtitle or omit it, but may never abbreviate or rewrite it.
- New or intentionally refreshed covers require a paired receipt. Legacy single-cover receipts remain readable and verifiable for unchanged packages.
- Render and promotion are atomic at pair scope. Failure may not leave one new canonical variant beside one old variant.
- EPUB embeds portrait bytes exactly. M4B embeds square artwork and must preserve audio packet bytes, streams, duration, chapters, and format tags exactly.
- Exactly three genuinely different candidate pairs are produced per migrated book. No automatic selection is permitted.
- Generated art contains no lettering, logos, watermarks, interface, dashboard, mockup, or close imitation of an existing cover or designer.
- Public and private/iCloud editions are staged from their own originals and verified independently. Never replace one edition with another.
- *Rodents in the Walls* is excluded and must remain byte-identical throughout implementation and rollout.
- Preserve unrelated work in the original Explainer Audiobooks and KinNoKiLabsSite checkouts. Use clean feature worktrees and ready PRs against each repository's configured base.
- Do not repoint installed shared skills to an unmerged worktree.

---

### Task 1: Add portrait and square variants to the specification contract

**Files:**
- Modify: `skill/schemas/cover-spec-v1.schema.json`
- Modify: `skill/scripts/cover_spec.py`
- Modify: `tests/test_cover_spec.py`

**Interfaces:**
- Consumes: existing `load_cover_spec(path, font_manifest_path)` validation entry point.
- Produces: `ValidatedCoverSpec.variant: str`, `ValidatedCoverSpec.width: int`, and `ValidatedCoverSpec.height: int`; exact variant/canvas rules used by rendering and receipts.

- [ ] **Step 1: Write failing variant tests**

Add tests that create otherwise-valid specifications with these cases:

```python
def test_accepts_exact_portrait_and_square_canvas(self):
    portrait = self.valid_spec()
    portrait["variant"] = "portrait"
    loaded = self.load_payload(portrait)
    self.assertEqual((loaded.variant, loaded.width, loaded.height), ("portrait", 1600, 2560))

    square = self.valid_spec()
    square["variant"] = "square"
    square["canvas"].update(width=2400, height=2400, safe_margin=120)
    loaded = self.load_payload(square)
    self.assertEqual((loaded.variant, loaded.width, loaded.height), ("square", 2400, 2400))

def test_rejects_unknown_variant_and_crossed_dimensions(self):
    for variant, width, height in [
        ("album", 2400, 2400),
        ("portrait", 2400, 2400),
        ("square", 1600, 2560),
    ]:
        payload = self.valid_spec()
        payload["variant"] = variant
        payload["canvas"].update(width=width, height=height)
        with self.assertRaises(CoverSpecError):
            self.load_payload(payload)
```

- [ ] **Step 2: Run the focused tests and confirm RED**

Run:

```bash
/usr/local/bin/python3 -m unittest \
  tests.test_cover_spec.CoverSpecValidationTests.test_accepts_exact_portrait_and_square_canvas \
  tests.test_cover_spec.CoverSpecValidationTests.test_rejects_unknown_variant_and_crossed_dimensions -v
```

Expected: failures because `variant` is unknown and `ValidatedCoverSpec` exposes no variant/dimensions.

- [ ] **Step 3: Extend the schema and runtime validator**

Require top-level `variant` with enum `portrait|square`. Replace fixed canvas constants with a schema `allOf` conditional:

```json
"variant": {"enum": ["portrait", "square"]}
```

```json
{
  "if": {"properties": {"variant": {"const": "portrait"}}, "required": ["variant"]},
  "then": {"properties": {"canvas": {"properties": {
    "width": {"const": 1600}, "height": {"const": 2560}, "safe_margin": {"const": 96}
  }}}},
  "else": {"properties": {"canvas": {"properties": {
    "width": {"const": 2400}, "height": {"const": 2400}, "safe_margin": {"const": 120}
  }}}}
}
```

In `cover_spec.py`, validate the exact tuple before layer geometry and carry the values in `ValidatedCoverSpec`. Replace hard-coded coordinate bounds with values derived from the validated canvas while retaining the same two-times-canvas effect allowance.

- [ ] **Step 4: Add metadata rules for square subtitle omission**

Represent omission as exact empty subtitle metadata plus no subtitle layer. Add tests proving:

```python
def test_square_may_omit_but_not_rewrite_subtitle(self):
    square = self.valid_square_spec()
    square["metadata"]["subtitle"] = ""
    square["layers"] = [layer for layer in square["layers"] if layer.get("role") != "subtitle"]
    self.load_payload(square)

    rewritten = self.valid_square_spec()
    rewritten["metadata"]["subtitle"] = "Shortened words"
    with self.assertRaisesRegex(CoverSpecError, "metadata subtitle"):
        self.load_payload(rewritten, canonical_subtitle="The exact canonical subtitle")
```

Extend `load_cover_spec` with optional canonical metadata arguments only where needed by pair validation; standalone structural validation must not invent a book catalogue dependency.

- [ ] **Step 5: Run specification tests and commit**

```bash
/usr/local/bin/python3 -m json.tool skill/schemas/cover-spec-v1.schema.json >/dev/null
/usr/local/bin/python3 -m unittest tests.test_cover_spec -v
git add skill/schemas/cover-spec-v1.schema.json skill/scripts/cover_spec.py tests/test_cover_spec.py
git commit -m "feat: add portrait and square cover variants"
```

Expected: schema parses and all specification tests pass.

---

### Task 2: Render square layouts and publish paired outputs atomically

**Files:**
- Modify: `skill/scripts/cover_renderer.py`
- Create: `skill/scripts/cover_pairs.py`
- Modify: `tests/test_cover_renderer.py`
- Create: `tests/test_cover_pairs.py`

**Interfaces:**
- Consumes: `render_cover_spec(spec_path, output_path, thumbnail_path, receipt_path, font_manifest_path)`.
- Produces: `render_cover_pair(portrait_spec: Path, square_spec: Path, portrait_output: Path, square_output: Path, portrait_thumbnail: Path, square_thumbnail: Path, portrait_receipt: Path, square_receipt: Path) -> CoverPairRenderResult`.

- [ ] **Step 1: Add failing square-render tests**

Add a square fixture and assertions:

```python
result = render_cover_spec(square_spec, cover, thumbnail, receipt)
with Image.open(cover) as image:
    self.assertEqual((image.mode, image.size), ("RGB", (2400, 2400)))
with Image.open(thumbnail) as image:
    self.assertEqual((image.mode, image.size), ("RGB", (160, 160)))
self.assertEqual(result.variant, "square")
```

Run `tests.test_cover_renderer` and confirm RED because thumbnail and result metadata assume portrait.

- [ ] **Step 2: Make rendering dimension-driven**

Use `ValidatedCoverSpec.width`, `.height`, and `.variant` everywhere SVG canvas, raster validation, thumbnail sizing, and render receipts are built. Render receipt fields must include:

```json
{
  "schema_version": 1,
  "variant": "square",
  "dimensions": [2400, 2400],
  "thumbnail_dimensions": [160, 160]
}
```

Keep the isolated pinned-font environment and current atomic single-render rollback unchanged.

- [ ] **Step 3: Write failing pair-orchestrator tests**

Cover these cases in `tests/test_cover_pairs.py`:

```python
def test_pair_requires_same_candidate_and_source_hash(self):
    square = self.write_square(candidate_id="different-candidate")
    with self.assertRaisesRegex(CoverRenderError, "candidate"):
        self.render_pair(self.portrait_spec, square)

def test_pair_publishes_both_variants_and_receipts(self):
    result = self.render_pair(self.portrait_spec, self.square_spec)
    self.assertEqual(result.candidate_id, "open-machine")
    self.assertEqual(self.image_size(self.portrait_output), (1600, 2560))
    self.assertEqual(self.image_size(self.square_output), (2400, 2400))

def test_second_render_failure_preserves_all_existing_pair_files(self):
    sentinels = self.install_existing_outputs()
    with self.assertRaises(CoverRenderError):
        self.render_pair(self.portrait_spec, self.invalid_square_spec)
    self.assert_outputs_equal(sentinels)

def test_publish_failure_restores_all_eight_existing_outputs(self):
    sentinels = self.install_existing_outputs()
    with mock.patch("cover_pairs._replace", side_effect=self.fail_on_sixth_replace):
        with self.assertRaises(OSError):
            self.render_pair(self.portrait_spec, self.square_spec)
    self.assert_outputs_equal(sentinels)

def test_pair_rejects_any_output_alias_or_hardlink(self):
    os.link(self.portrait_output, self.square_output)
    with self.assertRaisesRegex(CoverRenderError, "alias"):
        self.render_pair(self.portrait_spec, self.square_spec)
```

The test fixture must pre-create all canonical outputs with distinct sentinel bytes, force failure during the second render and during the sixth publish, then assert every sentinel is restored exactly.

- [ ] **Step 4: Implement `cover_pairs.py`**

Define:

```python
@dataclass(frozen=True)
class CoverPairRenderResult:
    candidate_id: str
    source_sha256: str
    portrait: RenderResult
    square: RenderResult

def render_cover_pair(
    portrait_spec: Path,
    square_spec: Path,
    portrait_output: Path,
    square_output: Path,
    portrait_thumbnail: Path,
    square_thumbnail: Path,
    portrait_receipt: Path,
    square_receipt: Path,
    font_manifest_path: Path = DEFAULT_MANIFEST,
) -> CoverPairRenderResult:
    """Validate one identity, stage both renders, and publish all outputs atomically."""
```

Validate before writing that variants are exactly `{portrait, square}`, candidate IDs match, source-art SHA-256 values match, metadata title/author match, square subtitle is exact or empty, and no input/output paths alias. Render into one staging directory, then publish the eight artifacts with the renderer's rollback discipline.

- [ ] **Step 5: Run focused tests and commit**

```bash
/usr/local/bin/python3 -m unittest tests.test_cover_renderer tests.test_cover_pairs -v
git add skill/scripts/cover_renderer.py skill/scripts/cover_pairs.py tests/test_cover_renderer.py tests/test_cover_pairs.py
git commit -m "feat: render coordinated cover pairs atomically"
```

---

### Task 3: Introduce paired selection receipts with legacy verification

**Files:**
- Modify: `skill/scripts/cover_receipts.py`
- Modify: `tests/test_cover_receipts.py`

**Interfaces:**
- Consumes: two validated render receipts from Task 2.
- Produces: `create_paired_selection(portrait_render: Path, square_render: Path, output: Path, book_slug: str, edition_id: str, selection_source: str, selected_at: str, privacy_classification: str, permission_to_publish: bool) -> PairedSelectionReceipt`, `load_selection(path: Path) -> SelectionReceipt | PairedSelectionReceipt`, and `verify_package(selection_path: Path, cover_path: Path, *, m4b_cover_path: Path | None = None, epub_path: Path | None = None, m4b_path: Path | None = None, receipt_path: Path | None = None) -> PackageVerification`.

- [ ] **Step 1: Add failing paired-receipt tests**

Add explicit cases for:

```python
def test_creates_one_selection_binding_both_variants(self):
    receipt = self.create_pair()
    self.assertEqual(set(receipt.variants), {"portrait", "square"})
    self.assertEqual(receipt.candidate.id, "open-machine")

def test_rejects_mixed_candidate_ids_or_source_hashes(self):
    square = self.square_render(candidate_id="other")
    with self.assertRaisesRegex(ValueError, "candidate"):
        self.create_pair(square_render=square)

def test_rejects_duplicate_nested_variant_fields(self):
    payload = self.valid_pair_json().replace('"cover_sha256":', '"cover_sha256":"' + "0" * 64 + '","cover_sha256":', 1)
    with self.assertRaisesRegex(ValueError, "duplicate"):
        self.load_raw(payload)

def test_rejects_stale_portrait_or_square_render(self):
    receipt = self.create_pair()
    self.square_cover.write_bytes(b"stale")
    with self.assertRaisesRegex(ValueError, "square"):
        self.verify_pair(receipt)

def test_rejects_rewritten_square_subtitle(self):
    square = self.square_render(subtitle="Shortened words")
    with self.assertRaisesRegex(ValueError, "subtitle"):
        self.create_pair(square_render=square)

def test_loads_and_verifies_legacy_single_cover_receipt(self):
    loaded = load_selection(self.legacy_selection)
    self.assertIsInstance(loaded, SelectionReceipt)
    self.assertIn("receipt-identity", self.verify_legacy(loaded).checks)

def test_cli_select_pair_requires_both_render_receipts(self):
    completed = self.run_cli("select-pair", "--portrait-render-receipt", str(self.portrait_render))
    self.assertNotEqual(completed.returncode, 0)
    self.assertIn("--square-render-receipt", completed.stderr)
```

The expected paired JSON shape is:

```json
{
  "schema_version": 2,
  "book_slug": "fixture-book",
  "edition_id": "public-v1",
  "candidate": {"id": "open-machine", "direction_name": "The Open Machine"},
  "source_art_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "variants": {
    "portrait": {"specification_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", "render_receipt_sha256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc", "cover_sha256": "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd", "dimensions": [1600, 2560], "thumbnail_sha256": "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee", "subtitle_included": true},
    "square": {"specification_sha256": "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "render_receipt_sha256": "1111111111111111111111111111111111111111111111111111111111111111", "cover_sha256": "2222222222222222222222222222222222222222222222222222222222222222", "dimensions": [2400, 2400], "thumbnail_sha256": "3333333333333333333333333333333333333333333333333333333333333333", "subtitle_included": false}
  },
  "font_manifest_sha256": "4444444444444444444444444444444444444444444444444444444444444444",
  "selection_source": "user",
  "selected_at": "2026-07-13T12:00:00-03:00",
  "privacy": {"classification": "public-safe", "permission_to_publish": true}
}
```

- [ ] **Step 2: Confirm RED**

```bash
/usr/local/bin/python3 -m unittest tests.test_cover_receipts -v
```

Expected: paired API and schema-version-2 support are absent.

- [ ] **Step 3: Implement strict paired parsing and creation**

Add frozen dataclasses for `SelectedVariant` and `PairedSelectionReceipt`. Preserve strict duplicate-key rejection and exact-field validation at every nesting level. Dispatch `load_selection` by integer schema version: version 1 follows the existing path unchanged; version 2 requires exactly `portrait` and `square`.

Expose CLI commands:

```bash
cover_receipts.py select-pair \
  --portrait-render-receipt portrait.render.json \
  --square-render-receipt square.render.json \
  --out cover-selection.json \
  --book-slug fixture-book --edition-id public-v1 \
  --selection-source user --selected-at 2026-07-13T12:00:00-03:00 \
  --privacy-classification public-safe --permission-to-publish
```

Keep the existing `select` command only for legacy fixtures and verification compatibility; documentation and active skills must never teach it for new work.

- [ ] **Step 4: Extend package verification**

For paired receipts require `--cover` and `--m4b-cover`. Return checks:

```python
("portrait-standalone-bytes", "square-standalone-bytes", "epub-portrait-bytes",
 "m4b-square-normalized-pixels", "paired-receipt-identity")
```

Legacy version-1 receipts retain the old check names and behavior.

- [ ] **Step 5: Run tests and commit**

```bash
/usr/local/bin/python3 -m unittest tests.test_cover_receipts -v
git add skill/scripts/cover_receipts.py tests/test_cover_receipts.py
git commit -m "feat: bind portrait and square cover selections"
```

---

### Task 4: Make book building and cover replacement pair-aware

**Files:**
- Modify: `skill/scripts/build_book.py`
- Modify: `skill/scripts/refresh_epub_cover.py`
- Modify: `skill/scripts/replace_m4b_cover.py`
- Modify: `tests/test_build_book_cover_receipt.py`
- Modify: `tests/test_refresh_epub_cover.py`
- Modify: `tests/test_replace_m4b_cover.py`

**Interfaces:**
- Consumes: paired selection receipt, portrait `cover.png`, square `m4b-cover.png`.
- Produces: EPUB containing byte-identical portrait art and M4B containing normalized-pixel-identical square art without media-signature drift.

- [ ] **Step 1: Write failing build and replacement tests**

Add tests proving a paired build refuses a missing/stale square cover before writing outputs, passes the portrait to EPUB construction, and passes the square to M4B replacement. Extend the M4B invariant test to use a 2400 × 2400 image and assert packet hash, duration, stream signature, chapters, and tags remain exact.

- [ ] **Step 2: Run focused tests and confirm RED**

```bash
/usr/local/bin/python3 -m unittest \
  tests.test_build_book_cover_receipt \
  tests.test_refresh_epub_cover \
  tests.test_replace_m4b_cover -v
```

- [ ] **Step 3: Thread paired assets through packaging**

Add `--m4b-cover` beside `--cover` in paired workflows. Verify the complete receipt before any EPUB/M4B output is staged and after both embeddings. Do not alter the low-level EPUB requirement that the `mimetype` member remains stored first with its original metadata, and do not relax any M4B media invariant.

- [ ] **Step 4: Test failure rollback**

Force post-EPUB and post-M4B verification failures separately. Assert existing outputs remain byte-identical and no `.incoming-*` or temporary artifacts remain.

- [ ] **Step 5: Run tests and commit**

```bash
/usr/local/bin/python3 -m unittest \
  tests.test_build_book_cover_receipt \
  tests.test_refresh_epub_cover \
  tests.test_replace_m4b_cover -v
git add skill/scripts/build_book.py skill/scripts/refresh_epub_cover.py skill/scripts/replace_m4b_cover.py \
  tests/test_build_book_cover_receipt.py tests/test_refresh_epub_cover.py tests/test_replace_m4b_cover.py
git commit -m "feat: package portrait EPUB and square M4B covers"
```

---

### Task 5: Publish complete pairs transactionally

**Files:**
- Modify: `skill/scripts/sync_selected_cover.py`
- Modify: `tests/test_sync_selected_cover.py`

**Interfaces:**
- Consumes: verified paired receipt and eight canonical cover artifacts.
- Produces: dry-run/apply decisions and atomic destination updates for both variants, both thumbnails, both specs, both render receipts, selection receipt, EPUB, M4B, and existing checksum manifest entries.

- [ ] **Step 1: Add failing transactional tests**

Add tests for exact paired changed sets, dry-run immutability, public permission, supersession, alias rejection, checksum updates, failure after portrait publish, failure after square publish, and complete rollback. Explicitly assert an unrelated file and a legacy Rodents fixture remain byte-identical.

- [ ] **Step 2: Confirm RED**

```bash
/usr/local/bin/python3 -m unittest tests.test_sync_selected_cover -v
```

- [ ] **Step 3: Generalize the artifact manifest**

Replace implicit single-cover arguments with an explicit ordered artifact map whose canonical names are validated against a fixed allow-list. The apply path stages every file, verifies the staged pair/package, publishes every file with unique same-directory incoming names, rewrites only pre-existing checksum entries plus new governed cover entries, and rolls back the entire set on any error.

- [ ] **Step 4: Run tests and commit**

```bash
/usr/local/bin/python3 -m unittest tests.test_sync_selected_cover -v
git add skill/scripts/sync_selected_cover.py tests/test_sync_selected_cover.py
git commit -m "feat: sync selected cover pairs transactionally"
```

---

### Task 6: Make the paired rule universal in active skills and documentation

**Files:**
- Modify: `skill/SKILL.md`
- Modify: `skills/custom-learning-audiobook/SKILL.md`
- Modify: `skill/references/cover-art.md`
- Modify: `skill/references/package-and-qc.md`
- Modify: `README.md`
- Modify: `docs/how-these-were-made.md`
- Modify: `docs/make-your-own.md`
- Modify: `tests/test_skill_cover_contract.py`
- Modify: `tools/validate_skills.py`

**Interfaces:**
- Consumes: paired commands and artifacts from Tasks 1–5.
- Produces: one universal, chronological workflow taught consistently to every installed skill consumer.

- [ ] **Step 1: Write failing contract tests**

Require every active skill to teach: exactly three paired candidates, portrait and square dimensions/names, human pair selection, EPUB portrait embedding, M4B square embedding, receipt verification, media preservation, and public/private delivery boundaries. Reject active instructions that teach a single selected cover for new work.

- [ ] **Step 2: Confirm RED**

```bash
/usr/local/bin/python3 -m unittest tests.test_skill_cover_contract -v
```

- [ ] **Step 3: Update active workflow documentation**

Document the governed order exactly:

```text
research → three source directions → portrait/square render pairs → thumbnail review
→ explicit pair selection → paired receipt → EPUB portrait + M4B square embedding
→ post-embed verification → governed public/iCloud/site sync
```

State that legacy single-cover receipts are verification-only compatibility and that Rodents is not retroactively changed by this rollout.

- [ ] **Step 4: Validate and commit**

```bash
/usr/local/bin/python3 tools/validate_skills.py
/usr/local/bin/python3 -m unittest tests.test_skill_cover_contract -v
git add skill/SKILL.md skills/custom-learning-audiobook/SKILL.md skill/references/cover-art.md \
  skill/references/package-and-qc.md README.md docs/how-these-were-made.md docs/make-your-own.md \
  tests/test_skill_cover_contract.py tools/validate_skills.py
git commit -m "docs: require paired covers for audiobook publishing"
```

---

### Task 7: Generate and render fifteen paired candidates

**Files:**
- Create ignored run tree: `.build/custom-learning-audiobooks/public-paired-cover-rollout/`
- Create: `.build/custom-learning-audiobooks/public-paired-cover-rollout/candidate-manifest.json`
- Create: source files beneath `.build/custom-learning-audiobooks/public-paired-cover-rollout/`, using the exact book slugs and fifteen exact candidate IDs enumerated in Step 2; each leaf is named `source.png`
- Create: paired specs, renders, thumbnails, receipts, and per-book contact sheets under the same ignored run tree

**Interfaces:**
- Consumes: the exact five-book direction names and metaphors in the approved design specification.
- Produces: three validated portrait/square candidate pairs and one paired contact sheet per book; no canonical book mutation.

- [ ] **Step 1: Record immutable pre-rollout baselines**

For each five-book public folder, hash every file, inspect EPUB member identity, and capture ffprobe media signatures when an M4B exists. Separately hash every Rodents file. Save JSON evidence beneath `evidence/before/` with absolute source paths and timestamps.

- [ ] **Step 2: Create the candidate manifest**

The manifest contains exactly these IDs:

```text
echo-from-the-inside: open-machine, rooms-inside-the-app, sound-made-physical
why-it-feels-right: impossible-teapot, invisible-alignment, shape-of-feedback
findable: one-spine-in-a-city, exact-phrase, signal-through-the-shelf
chicken-predators: tracks-around-the-henhouse, evidence-table, night-at-the-fence
the-new-deal: red-thread-route, weight-of-the-mailbag, route-rewritten
```

Each entry records title, canonical subtitle, author, audience promise, central metaphor, composition, 2–4-colour palette, visible accent, material language, anti-brief, and the complete text-free image-generation prompt. The prompt must explicitly prohibit lettering, logos, watermarks, UI, mockups, generic icon clouds, stock-photo appearance, and named-artist imitation.

- [ ] **Step 3: Generate source art with the image-generation tool**

Generate one high-resolution portrait source for every manifest entry. Reject and regenerate outputs containing text, weak generic wallpaper, multiple competing ideas, dead title space, or a metaphor that does not match its named brief. Save tool provenance and the exact prompt beside each source.

- [ ] **Step 4: Author and render paired specifications**

For each source, create a `portrait-spec.json` and `square-spec.json` with the same candidate/source identity. Give the square an intentional recomposition at 2400 × 2400; do not crop the rendered portrait. Run `cover_pairs.py` and assert byte-identical deterministic rerenders.

- [ ] **Step 5: Build five paired contact sheets**

Each sheet has three rows. Every row shows the 160 × 256 portrait thumbnail and 160 × 160 square thumbnail together, with the direction name outside the artwork. Also create an index HTML/Markdown page with links to full-size assets and briefs.

- [ ] **Step 6: Run the candidate gate**

Verify schema, pinned font hashes/glyphs, exact RGB dimensions, receipt identity, deterministic rerender, source-art equality within each pair, and zero changes to tracked book folders. Visually inspect every full-size render and every actual thumbnail.

- [ ] **Step 7: Stop for human selection**

Present all five contact sheets. Record one selected pair or requested mix per book. Do not create selection receipts, alter canonical covers, embed packages, change iCloud, or touch the website before explicit responses cover all five books.

---

### Task 8: Promote the five approved pairs into public book packages

**Files:**
- Modify selected cover/package/provenance files under:
  - `books/echo-from-the-inside/`
  - `books/why-it-feels-right/`
  - `books/findable/`
  - `books/chicken-predators/`
  - `books/the-new-deal/`
- Create: `docs/cover-pilots/public-paired-cover-rollout-2026-07/manifest.md`
- Create: `docs/cover-pilots/public-paired-cover-rollout-2026-07/contact-sheet.png`

**Interfaces:**
- Consumes: five explicit human selections from Task 7.
- Produces: five canonical selected pairs, paired receipts, portrait EPUB covers, and square M4B covers with edition-preservation evidence.

- [ ] **Step 1: Revalidate selections and fresh baselines**

Rerender every selected pair from recorded specs and require byte identity with reviewed outputs. Re-capture public file inventories and M4B signatures immediately before mutation. Compare Rodents against Task 7 hashes and stop on any difference.

- [ ] **Step 2: Create paired selection receipts**

Use `selection_source=user` or `requested-mix` exactly as applicable, current timezone-aware timestamps, public-safe classification, publication permission, and the actual public edition ID from each book package.

- [ ] **Step 3: Stage all five package updates independently**

For each book, preserve the prior portrait cover, publish the governed pair artifacts, replace only the EPUB cover member with portrait bytes, and replace only M4B artwork with square pixels when an M4B exists. A failure in one book does not publish a partial pair for that book and does not substitute files between books.

- [ ] **Step 4: Verify every public edition**

Require receipt verification, `unzip -t`, exact EPUB portrait identity, exact M4B square identity, exact pre/post audio packet hash, duration, streams, chapters, and format tags, plus unchanged non-cover file inventory. Confirm Rodents remains byte-identical.

- [ ] **Step 5: Sync exact-matching iCloud editions only**

Search the authorized iCloud Books collection for exact edition matches. For each match, stage from that iCloud edition, capture its own baseline, run governed dry-run then apply, verify checksums and media signatures, and report the exact changed set. Skip unmatched or ambiguous editions without creating a substitute.

- [ ] **Step 6: Commit the public rollout**

```bash
/usr/local/bin/python3 tools/validate_skills.py
/usr/local/bin/python3 -m unittest discover -s tests -v
git diff --check
git add books/echo-from-the-inside books/why-it-feels-right books/findable \
  books/chicken-predators books/the-new-deal docs/cover-pilots/public-paired-cover-rollout-2026-07
git commit -m "feat: publish paired covers for public learning books"
```

---

### Task 9: Show portrait covers on `/learn` and square covers in the player

**Files (KinNoKiLabsSite clean worktree):**
- Modify: `Sources/KinNoKiLabsSite/Theme/KinNoKiTheme.swift`
- Modify: `Tools/build-listen-catalog.sh`
- Modify: `Resources/listen/books.json`
- Modify: `Resources/listen/books/{echo-from-the-inside,why-it-feels-right,findable,chicken-predators,the-new-deal}/cover.jpg` for migrated slugs represented in the listening catalogue
- Create: `Resources/learn/covers/{echo-from-the-inside,why-it-feels-right,findable,rodents-in-the-walls,chicken-predators,the-new-deal}.png`; the Rodents file is a byte-derived website copy of its existing approved portrait, not a redesigned or republished book asset
- Modify generated outputs under `Output/` through the repository's normal publish command
- Modify: `Tests/site/learn-library.test.mjs`
- Create: `Tests/site/paired-cover-assets.test.mjs`

**Interfaces:**
- Consumes: verified canonical `cover.png`, `m4b-cover.png`, and paired receipt hashes from Task 8.
- Produces: responsive portrait cards on `/learn`, square listening artwork, and a build-time provenance map.

- [ ] **Step 1: Create a clean site worktree and capture baseline**

Read site `AGENTS.md`/`CLAUDE.md`, inspect deployment branch/configuration, run existing tests and build, and hash current audio/caption/book metadata. Preserve the original checkout exactly.

- [ ] **Step 2: Write failing site tests**

Assert each of the six `/learn` books appears once and has a portrait image with meaningful alt text. Rodents must use a hash-verified derivative of its existing approved portrait; the five migrated cards use their newly selected portraits. Listening entries for migrated books resolve to square assets, while Rodents retains its existing player asset. Validate actual dimensions with the site's available image inspection tool rather than filename assumptions.

- [ ] **Step 3: Add a verified asset-copy command**

Extend `build-listen-catalog.sh` or add a focused helper that reads paired receipts from the Explainer checkout and copies only hash-matching assets. Emit a generated provenance JSON mapping slug to portrait hash, square hash, and selection-receipt hash. Fail on missing receipt, wrong dimensions, stale source, unknown slug, or Rodents mutation.

- [ ] **Step 4: Render responsive `/learn` cards**

Add portrait `<img>` markup within all six cards using the site's existing semantic HTML and CSS conventions. Preserve title, runtime, description, and links. Use intrinsic width/height and `object-fit: cover` without distorting the 5:8 image. Rodents uses its existing approved portrait and is never sent through candidate generation or book-package promotion.

- [ ] **Step 5: Use square player artwork**

Generate player JPEG/WebP derivatives from each verified 2400 × 2400 source without changing audio, alignment, blocks, captions, title, author, or runtime metadata. The listening catalogue must identify the square source hash.

- [ ] **Step 6: Test, build, and visually verify**

```bash
node --test Tests/site/*.test.mjs
swift test
make publish
node --test Tests/site/*.test.mjs
git diff --check
```

Inspect `/learn` at phone and desktop widths and the player at a real small tile size. Confirm no title/author crop, layout shift, broken alt text, or cover/content mismatch.

- [ ] **Step 7: Commit the site rollout**

```bash
git add Sources Tools Resources Output Tests
git commit -m "feat: publish paired learning-library covers"
```

---

### Task 10: Final verification, PRs, and durable KB receipt

**Files:**
- Create ignored implementation and site PR bodies under each worktree's `.build/` evidence folder
- Modify existing adaptive-cover/Explainer Audiobooks KB project or status surfaces in a clean KB worktree
- Update: `bundle/log.md` in the KB worktree

**Interfaces:**
- Consumes: completed Explainer and site branches plus all baseline/receipt evidence.
- Produces: two ready implementation PRs, exact hosted-check status, and a merged Tier-1 KB receipt.

- [ ] **Step 1: Run the complete Explainer gate**

```bash
/usr/local/bin/python3 tools/fetch_cover_fonts.py --check
/usr/local/bin/python3 -m json.tool skill/schemas/cover-spec-v1.schema.json >/dev/null
/usr/local/bin/python3 tools/validate_skills.py
/usr/local/bin/python3 -m unittest discover -s tests -v
for epub in books/{echo-from-the-inside,why-it-feels-right,findable,chicken-predators,the-new-deal}/*.epub; do unzip -t "$epub" >/dev/null; done
git diff --check
git status --short --branch
```

Re-run all five paired receipts and media-signature comparisons, inspect ten selected full-size covers and ten real thumbnails, and confirm the complete Rodents hash inventory is unchanged.

- [ ] **Step 2: Run the complete site gate**

```bash
node --test Tests/site/*.test.mjs
swift test
make publish
git diff --check
git status --short --branch
```

Confirm generated output matches source, five portrait cards load, square player images load, and all audio/caption hashes remain baseline-identical.

- [ ] **Step 3: Rebase both branches and rerun their gates**

Fetch and rebase each branch onto its repository's current intended base. If any conflict touches a cover, EPUB, M4B, receipt, generated site asset, or audio/caption file, resolve from exact hashes and edition evidence; never choose a binary side by branch name. Rerun Steps 1–2 after successful rebases.

- [ ] **Step 4: Push and open ready PRs**

Open the Explainer PR against its configured base with infrastructure commits distinguished from the five-book creative rollout and with exact test/media evidence. Open the KinNoKi site PR separately with its asset provenance, responsive visual evidence, test/build results, and unchanged listening-content hashes. Do not use draft status unless a concrete unresolved blocker remains.

- [ ] **Step 5: Inspect hosted state**

For each PR record state, draft state, exact head SHA, base, merge status, and `statusCheckRollup`; run `gh pr checks`. Report `no hosted checks reported` when empty rather than calling it passing CI. Inspect and fix concrete failing logs before proceeding.

- [ ] **Step 6: Verify installed-skill boundary**

Confirm all Claude/Codex/shared-agent skill links still resolve into `/Users/dfakkeldy/Developer/explainer-audiobooks/`, not the feature worktree. Record that universal paired behavior becomes installed only after the Explainer PR merges and the original checkout updates.

- [ ] **Step 7: File the KB receipt**

In a clean KB worktree based on current `origin/main`, update the smallest existing Explainer/adaptive-cover status and project surfaces. Record Dan's approval, both PR URLs/exact heads, the universal rule, five selected pairs, Rodents exclusion proof, public/iCloud edition evidence, website state, hosted checks, installed-skill boundary, and unchanged Master Plan impact. Run `tools/kb_lint.py`, commit, rebase, push, open a Tier-1 PR, and verify its lint/auto-merge final state.

- [ ] **Step 8: Audit every touched worktree**

Run `git status --short --branch` in both feature worktrees, both original checkouts, the KB receipt worktree, and original KB checkout. Preserve and report all pre-existing unrelated files. Every agent-authored tracked change must be committed, pushed, and represented by its PR; generated scratch remains ignored and locally evidenced.

---

## Execution Handoff

Execute from the existing clean worktree and branch:

```text
/Users/dfakkeldy/.codex/worktrees/universal-paired-book-covers/explainer-audiobooks
codex/universal-paired-book-covers
```

Task 7 is a mandatory visual-selection gate. Task 8 cannot begin until Dan has explicitly selected or mixed one portrait/square pair for each of the five books. *Rodents in the Walls* remains outside the migration at every task.
