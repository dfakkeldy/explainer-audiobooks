# Public Audiobook Cover Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace all eleven public audiobook covers with autonomously selected, premium raster-AI artwork, update every embedded EPUB cover and matching public iCloud package, and publish a provenance manifest plus collection contact sheet.

**Architecture:** Creative work lives under `.build/public-cover-refresh-2026-07/`, with three generated raster candidates per title and one selected artwork passed through the existing `make_cover.py` compositor. Two small tested utilities handle the deterministic edges: replacing the OPF-declared EPUB cover without rebuilding prose, and assembling the final contact sheet. Only selected covers, legacy covers, refreshed EPUBs, README corrections, the manifest, contact sheet, utilities, and tests enter Git.

**Tech Stack:** Built-in `image_gen`, Python 3 standard library, Pillow, existing `skill/scripts/make_cover.py`, `unittest`, EPUB/OPF XML, `unzip`, `ffprobe`, Git/GitHub CLI.

## Global Constraints

- Scope is exactly the eleven tracked public book directories listed in the approved design; private, ignored, build-only, and untracked books are excluded.
- Generate at least three genuinely different raster candidates per title with the built-in image-generation tool; do not fall back to SVG or CLI/API image generation without explicit user approval.
- Generated art contains no lettering, title, subtitle, author, logos, watermarks, UI, dashboards, mockup frames, or imitation of named covers/designers.
- Bright or high-key treatment is the collection default. Select a dark cover only when it is materially stronger and the subject genuinely benefits; regenerate a bright direction when no award-worthy bright option exists.
- Because `make_cover.py` places titles in the lower third, title-safe space is the lower 25–35%. Carry visual energy through the top and middle; reject and regenerate covers with a dead or vacant upper field.
- Composite final covers at exactly 1600 by 2560 pixels with `skill/scripts/make_cover.py`.
- Preserve every prior public `cover.png` as `cover-legacy.png` before replacement.
- Update existing EPUB cover assets in place; never rebuild public books from combined Markdown.
- Preserve the EPUB `mimetype` entry first and uncompressed and leave all non-cover entries unchanged.
- Do not modify private iCloud folders, M4B audio, alignment sidecars, `.echoplaylist.json`, playback state, or unrelated delivery files.
- Keep all 33 candidate images and review scratch under `.build/public-cover-refresh-2026-07/`; commit only selected/derived public artifacts and documented provenance.
- Use one coherent branch based on current `origin/main`, commit at the task checkpoints below, push, and open a ready pull request against `main`.

---

## File Map

- Create `skill/scripts/refresh_epub_cover.py`: discover an EPUB's OPF-declared cover-image item and replace only that archive member while preserving EPUB invariants.
- Create `tests/test_refresh_epub_cover.py`: fixture-based tests for OPF discovery, replacement, archive preservation, and fail-closed behavior.
- Create `skill/scripts/make_cover_contact_sheet.py`: validate eleven cover PNGs and render a labelled collection sheet.
- Create `tests/test_make_cover_contact_sheet.py`: dimension, label, order, and invalid-input tests.
- Create `.build/public-cover-refresh-2026-07/manifest.json`: untracked production ledger for 33+ generations and selection/QC state.
- Create `docs/cover-refresh-2026-07/manifest.md`: committed human-readable provenance and selection record.
- Create `docs/cover-refresh-2026-07/contact-sheet.png`: committed labelled final collection review.
- Modify each tracked `books/*/cover.png`: selected new cover.
- Create each tracked `books/*/cover-legacy.png`: exact previous cover bytes.
- Modify each tracked public `books/*/*.epub`: replace only its declared embedded cover asset.
- Modify book README files only when their cover provenance/description becomes inaccurate.

---

### Task 1: Tested EPUB Cover Replacement Utility

**Files:**
- Create: `skill/scripts/refresh_epub_cover.py`
- Create: `tests/test_refresh_epub_cover.py`

**Interfaces:**
- Consumes: `replace_epub_cover(epub_path: Path, cover_path: Path, output_path: Path) -> CoverReplacement`
- Produces: `CoverReplacement(opf_path: str, cover_member: str, width: int, height: int, sha256: str)` and CLI `--epub`, `--cover`, `--out`.

- [ ] **Step 1: Write a failing round-trip test**

Create an EPUB fixture in the test with `mimetype` first/stored, `META-INF/container.xml`, `OEBPS/content.opf`, `OEBPS/cover-old.png`, and one untouched chapter. Assert the result preserves member names and chapter bytes, keeps `mimetype` first and uncompressed, replaces only `OEBPS/cover-old.png`, and reports `1600x2560`.

```python
def test_replaces_declared_cover_and_preserves_epub(tmp_path):
    source = make_epub_fixture(tmp_path, cover_href="cover-old.png")
    new_cover = make_png(tmp_path / "new.png", (1600, 2560), "#D62828")
    result = refresh_epub_cover.replace_epub_cover(
        source, new_cover, tmp_path / "out.epub"
    )
    assert result.cover_member == "OEBPS/cover-old.png"
    assert (result.width, result.height) == (1600, 2560)
    assert_epub_invariants(tmp_path / "out.epub", source)
```

- [ ] **Step 2: Run the test and confirm the missing-module failure**

Run:

```bash
python3 -m unittest tests.test_refresh_epub_cover -v
```

Expected: `ModuleNotFoundError` or import failure for `refresh_epub_cover`.

- [ ] **Step 3: Implement OPF discovery and fail-closed replacement**

Implement these exact responsibilities:

```python
@dataclass(frozen=True)
class CoverReplacement:
    opf_path: str
    cover_member: str
    width: int
    height: int
    sha256: str

def discover_opf_member(archive: zipfile.ZipFile) -> str: ...
def discover_cover_member(archive: zipfile.ZipFile, opf_member: str) -> str: ...
def png_dimensions(data: bytes) -> tuple[int, int]: ...
def replace_epub_cover(
    epub_path: Path, cover_path: Path, output_path: Path
) -> CoverReplacement: ...
```

Resolve `META-INF/container.xml` rootfile paths with `ElementTree`; identify the cover using `properties="cover-image"`, falling back to `<meta name="cover" content="ID">`; resolve the href relative to the OPF member. Reject missing, external, ambiguous, non-PNG, or non-1600x2560 covers. Rebuild to a temporary file, writing `mimetype` first with `ZIP_STORED`, then atomically replace `output_path` only after validation.

- [ ] **Step 4: Add fail-closed tests**

Add tests asserting clear `ValueError` messages for zero cover items, two cover-image items, path traversal (`../` escaping the EPUB root), a JPEG candidate, and a PNG with the wrong dimensions. Add a test for the legacy `<meta name="cover">` lookup.

- [ ] **Step 5: Run the focused and existing suites**

Run:

```bash
python3 -m unittest tests.test_refresh_epub_cover -v
python3 -m unittest discover -s tests -v
```

Expected: all tests pass.

- [ ] **Step 6: Commit the utility**

```bash
git add skill/scripts/refresh_epub_cover.py tests/test_refresh_epub_cover.py
git commit -m "feat: add safe EPUB cover replacement"
```

---

### Task 2: Tested Collection Contact-Sheet Utility

**Files:**
- Create: `skill/scripts/make_cover_contact_sheet.py`
- Create: `tests/test_make_cover_contact_sheet.py`

**Interfaces:**
- Consumes: ordered JSON array `[{"title": str, "cover": str}]` plus `--out`.
- Produces: RGB PNG contact sheet with fixed three-column grid, equal cover cells, and labels below each cover.

- [ ] **Step 1: Write failing tests for layout and validation**

```python
def test_builds_three_column_contact_sheet_in_manifest_order(tmp_path):
    entries = make_entries(tmp_path, count=11, size=(1600, 2560))
    result = make_cover_contact_sheet.render(entries, tmp_path / "sheet.png")
    assert result.cover_count == 11
    assert result.columns == 3
    assert Image.open(result.path).mode == "RGB"

def test_rejects_wrong_cover_dimensions(tmp_path):
    entries = make_entries(tmp_path, count=1, size=(800, 1280))
    with self.assertRaisesRegex(ValueError, "1600x2560"):
        make_cover_contact_sheet.render(entries, tmp_path / "sheet.png")
```

- [ ] **Step 2: Run tests and confirm failure**

```bash
python3 -m unittest tests.test_make_cover_contact_sheet -v
```

Expected: import failure for the missing utility.

- [ ] **Step 3: Implement the minimal renderer**

Use Pillow with 320x512 cover thumbnails, 24-pixel gutters, 52-pixel label bands, white background, and `ImageFont.load_default()` unless a bundled repository font is already used by `make_cover.py`. Preserve manifest order. Return:

```python
@dataclass(frozen=True)
class ContactSheetResult:
    path: Path
    cover_count: int
    columns: int
    rows: int
```

- [ ] **Step 4: Add tests for missing files, duplicate titles, empty input, and labels**

Assert errors identify the offending entry. Verify a label band contains non-white pixels for every cell.

- [ ] **Step 5: Run tests and commit**

```bash
python3 -m unittest tests.test_make_cover_contact_sheet -v
python3 -m unittest discover -s tests -v
git add skill/scripts/make_cover_contact_sheet.py tests/test_make_cover_contact_sheet.py
git commit -m "feat: add audiobook cover contact sheet"
```

---

### Task 3: Inventory, Metadata, and Production Ledger

**Files:**
- Create: `.build/public-cover-refresh-2026-07/manifest.json` (untracked)
- Create: `.build/public-cover-refresh-2026-07/briefs/*.md` (untracked)

**Interfaces:**
- Consumes: the eleven tracked `books/*/README.md`, current `cover.png`, EPUB metadata, and `skill/references/cover-art.md`.
- Produces: a manifest entry per title with `slug`, `title`, `subtitle`, `author`, `accent`, `tone`, `layout`, `candidates`, `selected_candidate`, `inspection`, and `icloud_match`.

- [ ] **Step 1: Confirm the exact tracked scope**

Run:

```bash
git ls-tree -d --name-only HEAD:books | sort
```

Expected: exactly the eleven slugs from the approved design and no ignored/private title.

- [ ] **Step 2: Extract title/subtitle/author and EPUB cover paths**

For each book, read its README and OPF metadata. Record exact compositor strings; do not infer a subtitle when the package has none. Use a read-only Python snippet that imports `discover_opf_member` and `discover_cover_member` and records the result for every `books/*/*.epub` file.

- [ ] **Step 3: Preserve legacy cover bytes before creative work**

```bash
for d in books/*; do
  test -f "$d/cover.png" || continue
  test ! -e "$d/cover-legacy.png" || { echo "legacy exists: $d"; exit 1; }
  cp "$d/cover.png" "$d/cover-legacy.png"
done
```

Verify `shasum -a 256 books/*/cover.png books/*/cover-legacy.png` pairs match before any replacement.

- [ ] **Step 4: Write the three briefs per title**

Use these direction sets as fixed starting decisions; each brief expands them into audience promise, central metaphor, composition, material/palette/accent, and anti-brief:

| Title | Candidate A | Candidate B | Candidate C |
|---|---|---|---|
| Chicken Predators | single feather caught in a humane live-trap threshold, documentary dawn | cut-paper predator tracks circling an intact egg, bright tactile collage | weathered coop latch lit like a forensic artifact, deep teal and safety orange |
| Echo, From the Inside | exploded physical music box revealing a calm inner machine | translucent layered book pages becoming an app-shaped listening chamber | hand-built bridge from rough sketches to polished glass, bright editorial realism |
| Findable | one luminous book spine found inside a city-scale shelf | brass search compass aligning with a tiny storefront doorway | signal flare reflected in a field of quiet app-like tiles without UI or logos |
| Git Happens | branching red thread repaired with one deliberate knot | geological strata of paper commits with one clean fault line | battered field case containing a pristine branching specimen |
| Rodents in the Walls | house wall cutaway with one telltale trail of dust and whisker shadow | oversized gnawed wooden threshold as forensic still life | bright field-guide collage of tracks, nesting fibre, and sealed gap |
| Tests First | porcelain mechanism protected by a ring of precise gauges | bright row of dominoes stopped by one transparent safety block | repaired parachute stitching inspected under a work lamp |
| The Bug Is a Clue | single beetle casting the shadow of a magnifying glass | detective evidence board reduced to one red thread and one broken component | dark machine room with one warm diagnostic light revealing the real fault |
| The New Deal | rural mailbox rebuilt from layered contract paper and route twine | weathered postal satchel balanced between old road and new measured grid | bright Cape Breton route map folded into a handshake-shaped landscape, no logos |
| The Voice in the Machine | paper sentence entering a small acoustic machine and leaving as a waveform ribbon | intimate microphone still life containing layered phonetic textures | glass voice box glowing inside a closed phone-sized object without UI |
| Why It Feels Right | three tactile controls where only one invites the hand correctly | elegant teapot silhouette transformed into a spatial design grid | bright layered glass, paper, and type-sized blocks settling into visual balance without text |
| You Are the Architect | human hand placing the final keystone into an AI-built structure | blueprint becoming a real workshop with verification tools in the foreground | conductor's baton directing modular construction pieces, no robots or glowing brains |

- [ ] **Step 5: Initialize manifest state and verify completeness**

Every title starts with exactly three candidate objects containing `id`, `direction_name`, `brief_path`, `prompt`, `generation_path: null`, `generation_status: "pending"`, and `inspection: null`. Validate with:

```bash
python3 - <<'PY'
import json
from pathlib import Path
p = Path('.build/public-cover-refresh-2026-07/manifest.json')
d = json.loads(p.read_text())
assert len(d['books']) == 11
assert sum(len(book['candidates']) for book in d['books']) == 33
assert all(len(book['candidates']) == 3 for book in d['books'])
print('MANIFEST_OK 11 books 33 candidates')
PY
```

Expected: `MANIFEST_OK 11 books 33 candidates`.

Do not commit `.build` artifacts. Commit the eleven `cover-legacy.png` files only after all checksum pairs are confirmed:

```bash
git add books/*/cover-legacy.png
git commit -m "chore: preserve legacy public audiobook covers"
```

---

### Task 4: Generate and Select Covers for Field, Discovery, and Version-Control Titles

**Files:**
- Create untracked candidates under `.build/public-cover-refresh-2026-07/{chicken-predators,findable,git-happens,rodents-in-the-walls}/`
- Modify untracked `.build/public-cover-refresh-2026-07/manifest.json`
- Modify selected cover files for the four named public book directories.

**Interfaces:**
- Consumes: four titles' three approved briefs and the copy-ready raster prompt in `skill/references/cover-art.md`.
- Produces: twelve recorded generations and four selected/composited covers.

- [ ] **Step 1: Generate three candidates for Chicken Predators**

Issue one built-in `image_gen` call per manifest prompt. Copy each returned raster file into the title build directory as `candidate-a-art.png`, `candidate-b-art.png`, and `candidate-c-art.png`. Record the exact final prompt, tool path `built-in image_gen`, generated source path, copied path, and status.

- [ ] **Step 2: Repeat for Findable, Git Happens, and Rodents in the Walls**

Use separate calls for all nine remaining candidates. Never combine distinct prompts into one request and never use SVG stand-ins.

- [ ] **Step 3: Inspect all twelve at full size and 160-pixel thumbnail scale**

Create temporary thumbnails with Pillow. Record `pass` or a concrete rejection reason for metaphor specificity, accidental text/logos, focal clarity, title-safe space, artifacts, and cross-title distinctness. Regenerate any rejection with one targeted prompt correction and retain the full generation count in the ledger.

- [ ] **Step 4: Select and composite four covers**

For each title, run the compositor from its exact manifest metadata using this
manifest-driven command so no title, subtitle, candidate, or colour is inferred:

```python
import json, subprocess
from pathlib import Path

data = json.loads(Path('.build/public-cover-refresh-2026-07/manifest.json').read_text())
batch = {'chicken-predators', 'findable', 'git-happens', 'rodents-in-the-walls'}
for book in data['books']:
    if book['slug'] not in batch:
        continue
    chosen = next(c for c in book['candidates'] if c['id'] == book['selected_candidate'])
    command = [
        'python3', 'skill/scripts/make_cover.py',
        '--title', book['title'], '--author', book['author'],
        '--label', 'AUDIOBOOK', '--art', chosen['generation_path'],
        '--accent', book['accent'], '--tone', book['tone'],
        '--layout', book['layout'], '--out', f"books/{book['slug']}/cover.png",
    ]
    if book.get('subtitle'):
        command[4:4] = ['--subtitle', book['subtitle']]
    subprocess.run(command, check=True)
```

If the existing package credits a different author string, use the package value recorded in Task 3.

- [ ] **Step 5: Validate the four selected covers**

```bash
python3 - <<'PY'
from PIL import Image
from pathlib import Path
slugs = ['chicken-predators','findable','git-happens','rodents-in-the-walls']
for slug in slugs:
    p = Path('books') / slug / 'cover.png'
    with Image.open(p) as im:
        assert im.format == 'PNG' and im.size == (1600, 2560)
print('BATCH1_COVERS_OK')
PY
```

Expected: `BATCH1_COVERS_OK`. Do not commit yet; selected covers remain subject to collection-wide review.

---

### Task 5: Generate and Select Covers for Echo and Software-Craft Titles

**Files:**
- Create untracked candidates under `.build/public-cover-refresh-2026-07/{echo-from-the-inside,tests-first,the-bug-is-a-clue,the-voice-in-the-machine}/`
- Modify untracked manifest and four selected `cover.png` files.

**Interfaces:**
- Consumes: the four titles' briefs from Task 3.
- Produces: twelve recorded generations and four selected/composited covers.

- [ ] **Step 1: Generate three candidates per title with twelve separate built-in calls**

Use the same save-path and ledger contract as Task 4 for *Echo, From the Inside*, *Tests First*, *The Bug Is a Clue*, and *The Voice in the Machine*.

- [ ] **Step 2: Inspect full-size and thumbnail outputs**

Reject generic glowing technology, UI-like panels, robot imagery, meaningless code texture, accidental letters, and weak title fields. Regenerate only the failing direction with a targeted correction.

- [ ] **Step 3: Select and composite four covers**

Use exact Task 3 metadata and `make_cover.py`. Ensure none repeats Task 4's selected dominant palette, central object, or composition.

- [ ] **Step 4: Validate dimensions and manifest completion**

```bash
python3 - <<'PY'
from PIL import Image
from pathlib import Path
slugs = ['echo-from-the-inside','tests-first','the-bug-is-a-clue','the-voice-in-the-machine']
for slug in slugs:
    with Image.open(Path('books') / slug / 'cover.png') as im:
        assert im.format == 'PNG' and im.size == (1600, 2560)
print('BATCH2_COVERS_OK')
PY
```

Expected: `BATCH2_COVERS_OK`.

---

### Task 6: Generate and Select Covers for Design, Agency, and Labour Titles

**Files:**
- Create untracked candidates under `.build/public-cover-refresh-2026-07/{the-new-deal,why-it-feels-right,you-are-the-architect}/`
- Modify untracked manifest and three selected `cover.png` files.

**Interfaces:**
- Consumes: the final three titles' briefs.
- Produces: nine recorded generations and three selected/composited covers, completing the 33-candidate minimum.

- [ ] **Step 1: Generate three candidates per title with nine separate built-in calls**

Use exact manifest prompts and persist all requested deliverables under the build directory.

- [ ] **Step 2: Inspect and reject known failure modes**

For *The New Deal*, reject corporate logos, literal Canada Post branding, generic mailbox clip art, faux maps with readable false labels, and political propaganda aesthetics. For *Why It Feels Right*, reject generic app UI or Apple logos. For *You Are the Architect*, reject hard hats, robots, glowing brains, and generic blueprint stock art.

- [ ] **Step 3: Select and composite three covers**

Use exact metadata and ensure the three selections are distinct from the eight already selected.

- [ ] **Step 4: Validate the complete candidate ledger and selected cover set**

```bash
python3 - <<'PY'
import json
from pathlib import Path
from PIL import Image
root = Path('.build/public-cover-refresh-2026-07')
d = json.loads((root / 'manifest.json').read_text())
assert len(d['books']) == 11
assert sum(len(b['candidates']) for b in d['books']) == 33
assert all(sum(c['generation_status'] == 'complete' for c in b['candidates']) == 3 for b in d['books'])
assert all(b['selected_candidate'] for b in d['books'])
for b in d['books']:
    with Image.open(Path('books') / b['slug'] / 'cover.png') as im:
        assert im.size == (1600, 2560)
print('ALL_COVERS_OK 11 selected 33 candidates')
PY
```

Expected: `ALL_COVERS_OK 11 selected 33 candidates`.

---

### Task 7: Collection Contact Sheet and Cross-Title Art Direction Review

**Files:**
- Create: `docs/cover-refresh-2026-07/contact-sheet.png`
- Modify selected covers if targeted regeneration is required.

**Interfaces:**
- Consumes: the eleven selected public `cover.png` files and ordered title/cover JSON.
- Produces: final collection contact sheet and a completed collection-review section in the build ledger.

- [ ] **Step 1: Render the labelled contact sheet**

```bash
mkdir -p docs/cover-refresh-2026-07
python3 skill/scripts/make_cover_contact_sheet.py \
  --manifest .build/public-cover-refresh-2026-07/contact-sheet-input.json \
  --out docs/cover-refresh-2026-07/contact-sheet.png
```

Expected: `CONTACT_SHEET_OK 11 covers 3 columns 4 rows`.

- [ ] **Step 2: Inspect the sheet at full size and thumbnail scale**

Record evidence for all six approved review questions: readability, palette clustering, repeated metaphor, brightness balance, title hierarchy, and weakest member. Name each title explicitly in the review ledger.

- [ ] **Step 3: Regenerate any collection-level outlier**

If one cover repeats another or falls below the group, issue one new built-in call using the rejected candidate's strongest brief with one targeted change. Re-composite, revalidate, update the selection history without erasing the previous generation, and rerender the sheet.

- [ ] **Step 4: Freeze final selected cover checksums**

```bash
shasum -a 256 books/*/cover.png > .build/public-cover-refresh-2026-07/final-cover-sha256.txt
```

Confirm there are eleven unique hashes.

---

### Task 8: Refresh Embedded EPUB Covers and Package Documentation

**Files:**
- Modify: the eleven tracked public EPUB files.
- Modify: only README files with stale cover provenance/selection text.

**Interfaces:**
- Consumes: eleven selected covers and `refresh_epub_cover.py`.
- Produces: eleven valid EPUBs whose declared cover-image bytes match the selected repo cover.

- [ ] **Step 1: Replace each EPUB cover through a temporary output**

For each title, locate its one EPUB and run this exact manifest-driven script:

```python
import json, shutil, subprocess
from pathlib import Path

data = json.loads(Path('.build/public-cover-refresh-2026-07/manifest.json').read_text())
for book in data['books']:
    source = next((Path('books') / book['slug']).glob('*.epub'))
    output = Path('.build/public-cover-refresh-2026-07') / book['slug'] / source.name
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        'python3', 'skill/scripts/refresh_epub_cover.py',
        '--epub', str(source), '--cover', f"books/{book['slug']}/cover.png",
        '--out', str(output),
    ], check=True)
    shutil.move(output, source)
```

Expected output names the OPF path, cover member, `1600x2560`, and SHA-256.

- [ ] **Step 2: Verify archive integrity and embedded cover equality**

Run `unzip -t` for all eleven EPUBs. Add a read-only Python verification that discovers each cover member, extracts its bytes, and asserts its SHA-256 equals the `cover.png` beside that EPUB.

- [ ] **Step 3: Verify EPUB member preservation**

Compare each refreshed EPUB against a clean `origin/main` copy: allow only the declared cover member's CRC, compressed size, and uncompressed size to differ. Assert the member name set, OPF, navigation, chapters, CSS, metadata, and other assets have identical hashes.

- [ ] **Step 4: Update stale README cover statements**

Replace statements claiming SVG, old candidate names, or old provenance. Use this factual structure:

```markdown
## Cover

Refreshed in July 2026 with original raster artwork generated through the built-in image-generation tool, then composed with the repository cover tool. The previous public cover is preserved as `cover-legacy.png`; generation prompt and selection evidence are recorded in the collection [cover-refresh manifest](../../docs/cover-refresh-2026-07/manifest.md).
```

Do not add this section to README files that already link cleanly to the central manifest without making a stale claim.

- [ ] **Step 5: Run package verification**

```bash
for epub in books/*/*.epub; do unzip -t "$epub" >/dev/null || exit 1; done
python3 -m unittest discover -s tests -v
git diff --check
```

Expected: all EPUBs valid, all tests pass, no whitespace errors.

---

### Task 9: Publish Provenance Manifest

**Files:**
- Create: `docs/cover-refresh-2026-07/manifest.md`
- Modify: `README.md` only if a collection-level cover-refresh link materially improves discoverability.

**Interfaces:**
- Consumes: build ledger, exact prompts, selected covers, inspection notes, final hashes, and contact sheet.
- Produces: public-safe provenance record with no local private paths or discarded image binaries.

- [ ] **Step 1: Write the manifest header and collection contract**

Document date, built-in image-generation path, three-candidate rule, autonomous-selection approval, compositor, 1600x2560 output, no-lettering rule, rights status, and the contact-sheet link.

- [ ] **Step 2: Write one complete section per title**

Each section contains exact title/slug, all three direction names and one-sentence theses, selected direction, exact generation prompt for the selected art, accent, tone, layout, generated-art filename, final cover filename, legacy filename, EPUB cover member, full-size result, thumbnail result, and SHA-256. Do not claim model/version metadata the built-in tool did not return.

- [ ] **Step 3: Add collection-review outcome and limitations**

State which covers were regenerated after the contact-sheet pass, if any. State that generated visual art is illustrative and that the typography was applied deterministically after generation.

- [ ] **Step 4: Validate manifest completeness**

```bash
for slug in chicken-predators echo-from-the-inside findable git-happens rodents-in-the-walls tests-first the-bug-is-a-clue the-new-deal the-voice-in-the-machine why-it-feels-right you-are-the-architect; do
  rg -q "^## .*${slug//-/.*}" docs/cover-refresh-2026-07/manifest.md || exit 1
done
```

If title headings do not contain slugs, use a deterministic Python check for eleven `Slug: \`...\`` fields instead.

- [ ] **Step 5: Commit the repo refresh**

```bash
git add README.md docs/cover-refresh-2026-07 books/*/cover.png books/*/cover-legacy.png books/*/*.epub books/*/README.md
git diff --cached --check
git commit -m "feat: refresh public audiobook cover collection"
```

Stage only files that actually changed; omit unchanged README files.

---

### Task 10: Synchronize Matching Public iCloud Packages

**Files:**
- Modify only positively matched public delivery folders under `/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/`.
- Create untracked `.build/public-cover-refresh-2026-07/icloud-sync.json`.

**Interfaces:**
- Consumes: repo title, exact EPUB basename/metadata, selected cover, refreshed EPUB, and explicit public-package evidence.
- Produces: checksum-matched public iCloud copies or a documented `no_match` result.

- [ ] **Step 1: Build a read-only delivery inventory**

List candidate folders and files. A folder matches only when its README/manifest title or EPUB OPF title equals the repo book title and its package is public-safe. Title similarity alone is insufficient.

- [ ] **Step 2: Record the sync decision before copying**

For every title write `matched_public`, `no_match`, or `ambiguous` plus evidence into `icloud-sync.json`. Do not touch `ambiguous` or `no_match` folders.

- [ ] **Step 3: Copy only cover and refreshed EPUB for positive matches**

Use the delivery package's existing filenames. Preserve M4B, alignment, `.echoplaylist.json`, README, manifests, and playback state.

- [ ] **Step 4: Verify checksums and untouched files**

Assert destination cover and EPUB hashes equal repo sources. For each matched folder, compare a pre/post inventory and assert no other file hash or modification time changed.

- [ ] **Step 5: Record final sync results in the public manifest**

Report only title and `updated`/`no matching public package`; do not publish private paths or playback data.

---

### Task 11: Final Verification, Review, and Publication

**Files:**
- Modify only artifacts that fail final verification.

**Interfaces:**
- Consumes: completed repo refresh and iCloud sync evidence.
- Produces: ready pull request and exact hosted-check status.

- [ ] **Step 1: Run the complete local gate**

```bash
python3 tools/validate_skills.py
python3 -m unittest discover -s tests -v
for epub in books/*/*.epub; do unzip -t "$epub" >/dev/null || exit 1; done
git diff --check
git status --short --branch
```

Expected: validator clean, all tests pass, all EPUBs valid, no whitespace errors, and only intentional committed changes.

- [ ] **Step 2: Perform the final visual gate**

Open `docs/cover-refresh-2026-07/contact-sheet.png` and each full-size final cover. Confirm all eleven labels/covers, no accidental generated text/logos, no clipped metadata, readable thumbnail titles, balanced brightness, and no remaining weak outlier.

- [ ] **Step 3: Rebase onto current `origin/main` if necessary**

```bash
git fetch origin
git rebase origin/main
```

If conflicts touch book packages or cover files, stop and resolve by evidence; never accept an EPUB binary side blindly.

- [ ] **Step 4: Rerun the full gate after rebase**

Repeat Step 1 and confirm the contact sheet still reflects current `cover.png` hashes.

- [ ] **Step 5: Push and open a ready pull request**

```bash
git push -u origin codex/public-cover-refresh
gh pr create --base main --head codex/public-cover-refresh \
  --title "Refresh the public audiobook cover collection" \
  --body-file .build/public-cover-refresh-2026-07/pr-body.md
```

The PR body lists eleven books, 33 minimum generations, regeneration count, test results, EPUB invariants, iCloud sync summary, and embeds/links the contact sheet.

- [ ] **Step 6: Check hosted CI and file the KB receipt**

Run `PR=$(gh pr view --json number -q .number)` followed by `gh pr checks "$PR"`. If a required check fails, inspect its logs and fix the concrete failure. After the repo PR is ready, update the smallest Explainer Audiobooks KB status/project surfaces with the PR URL, public-safe provenance, validation result, and unchanged Master Plan impact; lint, commit, push, and open the normal KB PR.

- [ ] **Step 7: Final worktree-state audit**

Run `git status --short --branch` in the implementation worktree, original Explainer Audiobooks checkout, KB worktree, and original KB checkout. Preserve and report pre-existing unrelated dirt; leave agent-authored work committed, pushed, and represented by PRs.
