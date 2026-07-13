# Rodents C2 Cover Refinement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Render and verify a refined C2 *Rodents in the Walls* cover with a compact orange title ribbon above every rodent shadow and one intentional editorial subtitle/author lockup, then stop for explicit visual approval.

**Architecture:** Reuse the implemented adaptive JSON cover specification, pinned font manifest, deterministic renderer, and contact-sheet CLI. Reconstruct the lost ignored pilot from the still-live approved source art, preserve an original-C2 control, render the new C2A candidate into a separate ignored run, and enforce structural, deterministic, visual, and no-mutation gates before presentation.

**Tech Stack:** `/usr/local/bin/python3`, repository cover-spec validator, SVG/librsvg renderer, isolated Fontconfig/Pango font resolution, Pillow, ImageMagick, JSON render receipts, SHA-256 evidence.

## Global Constraints

- Work only in `/Users/dfakkeldy/.codex/worktrees/adaptive-cover-spec-implementation/explainer-audiobooks` on `codex/adaptive-cover-spec-implementation`.
- Approved source art is `/Users/dfakkeldy/Developer/explainer-audiobooks/.build/custom-learning-audiobooks/rodents-in-the-walls-v3/dist/cover-raster-art-1.png` with SHA-256 `cced16a14a0aaced901af7ffd0b140c4d6e13fdf88bd3da22a9724fb7bad9812`.
- Copy the approved art byte-for-byte. Do not regenerate, retouch, inpaint, recolour, or recrop it.
- Keep the exact 1600 × 2560 RGB canvas and palette: navy `#132238`, orange `#EF5735`, cream `#F6EDDA`, and footer navy `#07111F`.
- Revised candidate id is `c2a-compact-ribbon-editorial-footer`; direction name is `Compact Ribbon / Editorial Footer`.
- Keep the literal title, subtitle, author, and `AUDIOBOOK` label unchanged.
- No ribbon, binding rule, title glyph, outline, or effect may cover a rodent silhouette. Require at least 24 final-cover pixels of visually clear navy between the ribbon and first shadow.
- Use only repository-pinned fonts. A generic or system-font fallback fails the task.
- All pilot files stay ignored under `.build/custom-learning-audiobooks/rodents-in-the-walls-c2-refinement/`.
- Do not create `cover-selection.json` and do not modify the repository Rodents package, EPUB, M4B, public package, or iCloud package.
- The final step is a mandatory visual gate. Do not resume parent-plan package promotion until Dan explicitly approves the refined render.
- Preserve unrelated work. No commit is created for ignored pilot artifacts.

## File Responsibility Map

- `.build/custom-learning-audiobooks/rodents-in-the-walls-c2-refinement/verify_refinement.py`: executable structural, receipt, package-immutability, and selection-absence gate.
- `.build/custom-learning-audiobooks/rodents-in-the-walls-c2-refinement/evidence/protected-before.json`: pre-render SHA-256, size, and mtime snapshot for nine protected repository/iCloud files.
- `.build/custom-learning-audiobooks/rodents-in-the-walls-c2-refinement/dist/cover-source.png`: byte-identical pilot copy of approved art.
- `.build/custom-learning-audiobooks/rodents-in-the-walls-c2-refinement/dist/cover-spec-original.json`: exact original C2 control.
- `.build/custom-learning-audiobooks/rodents-in-the-walls-c2-refinement/dist/cover-spec-refined.json`: approved compact-ribbon/editorial-footer C2A specification.
- `.build/custom-learning-audiobooks/rodents-in-the-walls-c2-refinement/dist/cover-{original,refined}.png`: full-size comparison covers plus generated thumbnails and render receipts.
- `.build/custom-learning-audiobooks/rodents-in-the-walls-c2-refinement/dist/comparison-input.json`: ordered original/refined contact-sheet manifest.
- `.build/custom-learning-audiobooks/rodents-in-the-walls-c2-refinement/comparison.png`: ordinary-CLI comparison surface.
- `.build/custom-learning-audiobooks/rodents-in-the-walls-c2-refinement/title-zone-comparison.png`: full-resolution upper-cover crop comparison for shadow-clearance review.
- `.build/custom-learning-audiobooks/rodents-in-the-walls-c2-refinement/visual-review.md`: evidence-backed final visual checklist, written only after every listed observation passes.

---

### Task 1: Reconstruct the Pilot and Produce a Structurally Verified C2A Render

**Files:**
- Create ignored: `.build/custom-learning-audiobooks/rodents-in-the-walls-c2-refinement/verify_refinement.py`
- Create ignored: `.build/custom-learning-audiobooks/rodents-in-the-walls-c2-refinement/evidence/protected-before.json`
- Create ignored: `.build/custom-learning-audiobooks/rodents-in-the-walls-c2-refinement/dist/cover-source.png`
- Create ignored: `.build/custom-learning-audiobooks/rodents-in-the-walls-c2-refinement/dist/cover-spec-original.json`
- Create ignored: `.build/custom-learning-audiobooks/rodents-in-the-walls-c2-refinement/dist/cover-spec-refined.json`
- Create ignored: full-size covers, thumbnails, and render receipts beneath the same `dist/`
- Modify tracked files: none

**Interfaces:**
- Consumes: `make_cover.py --spec <Path> --out <Path>`, font manifest `skill/assets/fonts/manifest.json`, and approved source SHA-256.
- Produces: `cover-original.png` and `cover-refined.png`, their thumbnails and `.render.json` receipts, plus a passing `verify_refinement.py` gate for Task 2.

- [ ] **Step 1: Create the ignored run folders**

```bash
PILOT=.build/custom-learning-audiobooks/rodents-in-the-walls-c2-refinement
DIST="$PILOT/dist"
mkdir -p "$DIST" "$PILOT/evidence" "$PILOT/history"
```

Expected: the three directories exist and `git status --short` does not list them.

- [ ] **Step 2: Write the acceptance verifier before creating its inputs**

Use `apply_patch` to create `$PILOT/verify_refinement.py` with this complete content:

```python
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image


PILOT = Path(__file__).resolve().parent
DIST = PILOT / "dist"
BASELINE = PILOT / "evidence" / "protected-before.json"
SOURCE_SHA256 = "cced16a14a0aaced901af7ffd0b140c4d6e13fdf88bd3da22a9724fb7bad9812"
EXPECTED = {
    "original": ("c2-integrated-colour-band", "Integrated Colour Band"),
    "refined": (
        "c2a-compact-ribbon-editorial-footer",
        "Compact Ribbon / Editorial Footer",
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint(path: Path) -> dict[str, int | str]:
    stat = path.stat()
    return {
        "sha256": sha256(path),
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
    }


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"expected JSON object: {path}")
    return value


def image_identity(path: Path, size: tuple[int, int]) -> None:
    with Image.open(path) as image:
        image.load()
        assert image.format == "PNG", (path, image.format)
        assert image.mode == "RGB", (path, image.mode)
        assert image.size == size, (path, image.size)


def verify_protected_files() -> None:
    assert BASELINE.is_file(), f"missing protected baseline: {BASELINE}"
    baseline = load_json(BASELINE)
    for raw_path, expected in baseline.items():
        path = Path(raw_path)
        assert path.is_file(), f"protected file disappeared: {path}"
        assert fingerprint(path) == expected, f"protected file changed: {path}"


def verify_candidate(stem: str) -> None:
    expected_id, expected_name = EXPECTED[stem]
    spec_path = DIST / f"cover-spec-{stem}.json"
    cover = DIST / f"cover-{stem}.png"
    thumbnail = DIST / f"cover-{stem}-thumbnail.png"
    receipt_path = DIST / f"cover-{stem}.render.json"
    spec = load_json(spec_path)
    receipt = load_json(receipt_path)
    assert spec["candidate"] == {
        "id": expected_id,
        "direction_name": expected_name,
    }
    assert receipt["candidate"] == spec["candidate"]
    assert receipt["source_art_sha256"] == SOURCE_SHA256
    assert receipt["output_sha256"] == sha256(cover)
    assert receipt["thumbnail_sha256"] == sha256(thumbnail)
    assert receipt["dimensions"] == [1600, 2560]
    assert receipt["colour_mode"] == "RGB"
    assert receipt["warnings"] in (
        [],
        ["layer 6 advisory contrast ratio is 2.97:1"],
    ), receipt["warnings"]
    image_identity(cover, (1600, 2560))
    image_identity(thumbnail, (160, 256))


def verify_refined_geometry() -> None:
    spec = load_json(DIST / "cover-spec-refined.json")
    layers = spec["layers"]
    assert isinstance(layers, list)
    field = next(layer for layer in layers if layer.get("kind") == "field")
    assert field["box"] == [64, 120, 1472, 600]
    assert field["box"][1] + field["box"][3] == 720
    title_layers = [
        layer for layer in layers
        if layer.get("kind") == "text" and layer.get("role") in {"label", "title"}
    ]
    assert all(layer["box"][1] + layer["box"][3] <= 720 for layer in title_layers)
    subtitle = next(
        layer for layer in layers
        if layer.get("kind") == "text" and layer.get("role") == "subtitle"
    )
    author = next(
        layer for layer in layers
        if layer.get("kind") == "text" and layer.get("role") == "author"
    )
    assert subtitle["text"] == (
        "Squirrels and Other Houseguests\n"
        "in Western Cape Breton"
    )
    assert subtitle["font_id"] == "geometric-sans"
    assert author["text"] == "Dan Fakkeldy"
    assert author["font_id"] == "technical-mono"
    assert any(
        layer.get("kind") == "line"
        and layer.get("colour") == "#EF5735"
        and layer.get("start") == [96, 2105]
        and layer.get("end") == [470, 2105]
        for layer in layers
    )


def main() -> int:
    verify_protected_files()
    source = DIST / "cover-source.png"
    assert source.is_file(), f"missing source copy: {source}"
    assert sha256(source) == SOURCE_SHA256
    image_identity(source, (1024, 1536))
    for stem in EXPECTED:
        verify_candidate(stem)
    verify_refined_geometry()
    assert sha256(DIST / "cover-original.png") != sha256(DIST / "cover-refined.png")
    selections = list(PILOT.rglob("cover-selection.json"))
    assert not selections, f"selection receipt created before approval: {selections}"
    print("REFINEMENT_VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 3: Run the verifier and confirm the intended RED state**

```bash
/usr/local/bin/python3 "$PILOT/verify_refinement.py"
```

Expected: exit 1 with `AssertionError: missing protected baseline`. This proves the gate runs before implementation artifacts exist.

- [ ] **Step 4: Capture the nine protected files before rendering anything**

Run this exact read-only snapshot command:

```bash
/usr/local/bin/python3 - <<'PY'
from __future__ import annotations

import hashlib
import json
from pathlib import Path

pilot = Path('.build/custom-learning-audiobooks/rodents-in-the-walls-c2-refinement')
icloud = Path('/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/Rodents in the Walls')
paths = (
    Path('books/rodents-in-the-walls/cover.png'),
    Path('books/rodents-in-the-walls/rodents-in-the-walls.epub'),
    Path('books/rodents-in-the-walls/rodents-in-the-walls.m4b'),
    Path('books/rodents-in-the-walls/README.md'),
    icloud / 'cover.png',
    icloud / 'rodents-in-the-walls.epub',
    icloud / 'rodents-in-the-walls.m4b',
    icloud / 'README.md',
    icloud / 'SHA256SUMS',
)
baseline = {}
for path in paths:
    assert path.is_file(), f'missing protected file: {path}'
    stat = path.stat()
    baseline[str(path.resolve())] = {
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'size': stat.st_size,
        'mtime_ns': stat.st_mtime_ns,
    }
out = pilot / 'evidence' / 'protected-before.json'
out.write_text(json.dumps(baseline, indent=2, sort_keys=True) + '\n', encoding='utf-8')
print(f'PROTECTED_BASELINE {len(baseline)} {out}')
PY
```

Expected: `PROTECTED_BASELINE 9` and a JSON object with nine absolute-path keys.

- [ ] **Step 5: Copy and prove the approved art**

```bash
SOURCE='/Users/dfakkeldy/Developer/explainer-audiobooks/.build/custom-learning-audiobooks/rodents-in-the-walls-v3/dist/cover-raster-art-1.png'
cp "$SOURCE" "$DIST/cover-source.png"
test "$(shasum -a 256 "$DIST/cover-source.png" | awk '{print $1}')" = cced16a14a0aaced901af7ffd0b140c4d6e13fdf88bd3da22a9724fb7bad9812
file "$DIST/cover-source.png"
```

Expected: `PNG image data, 1024 x 1536, 8-bit/color RGB`; the hash assertion exits 0.

- [ ] **Step 6: Create the exact original-C2 control specification**

Use `apply_patch` to create `$DIST/cover-spec-original.json`:

```json
{
  "schema_version": 1,
  "candidate": {"id": "c2-integrated-colour-band", "direction_name": "Integrated Colour Band"},
  "metadata": {
    "title": "Rodents in the Walls",
    "subtitle": "Squirrels and Other Houseguests in Western Cape Breton",
    "author": "Dan Fakkeldy",
    "label": "AUDIOBOOK"
  },
  "canvas": {"width": 1600, "height": 2560, "background": "#132238", "safe_margin": 96},
  "art": {"path": "cover-source.png", "mode": "bleed", "anchor": "center", "box": [0, 0, 1600, 2560], "opacity": 1, "blend_mode": "normal"},
  "layers": [
    {"kind": "field", "box": [64, 130, 1472, 760], "fill": {"kind": "solid", "colour": "#EF5735"}, "opacity": 0.94, "blend_mode": "normal", "purpose": "turn the exposed plaster accent into a deliberate editorial title material"},
    {"kind": "line", "start": [96, 850], "end": [1504, 850], "colour": "#F6EDDA", "width": 6, "opacity": 0.82, "purpose": "bind the band to the pale exposed plaster around the wall opening"},
    {"kind": "text", "role": "label", "text": "AUDIOBOOK", "font_id": "technical-mono", "box": [110, 170, 900, 70], "size": 30, "line_height": 38, "tracking": 8, "align": "left", "colour": "#132238", "opacity": 1, "rotation": 0, "baseline_shift": 0, "contrast_against": "#EF5735"},
    {"kind": "text", "role": "title", "title_order": 1, "text": "RODENTS", "font_id": "editorial-serif", "font_variation": {"SOFT": 18, "WONK": 1, "opsz": 100, "wght": 850}, "box": [104, 275, 1392, 260], "size": 205, "line_height": 218, "tracking": 0, "align": "left", "colour": "#132238", "opacity": 1, "rotation": 0, "baseline_shift": 0, "contrast_against": "#EF5735"},
    {"kind": "text", "role": "title", "title_order": 2, "text": "IN THE", "font_id": "geometric-sans", "font_variation": {"wght": 650}, "box": [112, 520, 650, 115], "size": 72, "line_height": 82, "tracking": 7, "align": "left", "colour": "#132238", "opacity": 1, "rotation": 0, "baseline_shift": 0, "contrast_against": "#EF5735"},
    {"kind": "text", "role": "title", "title_order": 3, "text": "WALLS", "font_id": "display-condensed", "box": [104, 610, 1392, 250], "size": 220, "line_height": 230, "tracking": 2, "align": "left", "colour": "#F6EDDA", "opacity": 1, "rotation": 0, "baseline_shift": 0, "outline": {"colour": "#132238", "width": 3}, "contrast_against": "#EF5735"},
    {"kind": "scrim", "box": [0, 2020, 1600, 540], "fill": {"kind": "linear-gradient", "start": [0, 2020], "end": [0, 2560], "stops": [{"offset": 0, "colour": "#132238", "opacity": 0}, {"offset": 0.4, "colour": "#132238", "opacity": 0.7}, {"offset": 1, "colour": "#07111F", "opacity": 0.94}]}, "opacity": 1, "blend_mode": "normal", "purpose": "support secondary metadata over the baseboard without changing the main art crop"},
    {"kind": "text", "role": "subtitle", "text": "Squirrels and Other Houseguests in Western Cape Breton", "font_id": "geometric-sans", "font_variation": {"wght": 500}, "box": [96, 2150, 1408, 140], "size": 40, "line_height": 50, "tracking": 0, "align": "left", "colour": "#F6EDDA", "opacity": 1, "rotation": 0, "baseline_shift": 0, "contrast_against": "#132238"},
    {"kind": "text", "role": "author", "text": "Dan Fakkeldy", "font_id": "technical-mono", "box": [96, 2360, 1408, 85], "size": 36, "line_height": 44, "tracking": 2, "align": "left", "colour": "#EF5735", "opacity": 1, "rotation": 0, "baseline_shift": 0, "contrast_against": "#07111F"}
  ]
}
```

- [ ] **Step 7: Create the exact refined C2A specification**

Use `apply_patch` to create `$DIST/cover-spec-refined.json`:

```json
{
  "schema_version": 1,
  "candidate": {"id": "c2a-compact-ribbon-editorial-footer", "direction_name": "Compact Ribbon / Editorial Footer"},
  "metadata": {
    "title": "Rodents in the Walls",
    "subtitle": "Squirrels and Other Houseguests in Western Cape Breton",
    "author": "Dan Fakkeldy",
    "label": "AUDIOBOOK"
  },
  "canvas": {"width": 1600, "height": 2560, "background": "#132238", "safe_margin": 96},
  "art": {"path": "cover-source.png", "mode": "bleed", "anchor": "center", "box": [0, 0, 1600, 2560], "opacity": 1, "blend_mode": "normal"},
  "layers": [
    {"kind": "field", "box": [64, 120, 1472, 600], "fill": {"kind": "solid", "colour": "#EF5735"}, "opacity": 0.94, "blend_mode": "normal", "purpose": "retain the plaster-derived C2 title material while ending above every rodent shadow"},
    {"kind": "line", "start": [96, 690], "end": [1504, 690], "colour": "#F6EDDA", "width": 5, "opacity": 0.82, "purpose": "finish the compact ribbon without extending into the shadow field"},
    {"kind": "text", "role": "label", "text": "AUDIOBOOK", "font_id": "technical-mono", "box": [110, 150, 900, 60], "size": 28, "line_height": 36, "tracking": 8, "align": "left", "colour": "#132238", "opacity": 1, "rotation": 0, "baseline_shift": 0, "contrast_against": "#EF5735"},
    {"kind": "text", "role": "title", "title_order": 1, "text": "RODENTS", "font_id": "editorial-serif", "font_variation": {"SOFT": 18, "WONK": 1, "opsz": 100, "wght": 850}, "box": [104, 225, 1392, 195], "size": 172, "line_height": 185, "tracking": 0, "align": "left", "colour": "#132238", "opacity": 1, "rotation": 0, "baseline_shift": 0, "contrast_against": "#EF5735"},
    {"kind": "text", "role": "title", "title_order": 2, "text": "IN THE", "font_id": "geometric-sans", "font_variation": {"wght": 650}, "box": [112, 425, 650, 90], "size": 72, "line_height": 72, "tracking": 7, "align": "left", "colour": "#132238", "opacity": 1, "rotation": 0, "baseline_shift": 0, "contrast_against": "#EF5735"},
    {"kind": "text", "role": "title", "title_order": 3, "text": "WALLS", "font_id": "display-condensed", "box": [104, 505, 1392, 185], "size": 166, "line_height": 176, "tracking": 2, "align": "left", "colour": "#F6EDDA", "opacity": 1, "rotation": 0, "baseline_shift": 0, "outline": {"colour": "#132238", "width": 3}, "contrast_against": "#EF5735"},
    {"kind": "scrim", "box": [0, 1995, 1600, 565], "fill": {"kind": "linear-gradient", "start": [0, 1995], "end": [0, 2560], "stops": [{"offset": 0, "colour": "#132238", "opacity": 0}, {"offset": 0.42, "colour": "#132238", "opacity": 0.66}, {"offset": 1, "colour": "#07111F", "opacity": 0.94}]}, "opacity": 1, "blend_mode": "normal", "purpose": "support one lower editorial lockup without creating a hard footer container"},
    {"kind": "line", "start": [96, 2105], "end": [470, 2105], "colour": "#EF5735", "width": 5, "opacity": 1, "purpose": "join subtitle and author into one left-aligned editorial signature"},
    {"kind": "text", "role": "subtitle", "text": "Squirrels and Other Houseguests\nin Western Cape Breton", "font_id": "geometric-sans", "font_variation": {"wght": 500}, "box": [96, 2140, 1000, 180], "size": 46, "line_height": 58, "tracking": 0, "align": "left", "colour": "#F6EDDA", "opacity": 1, "rotation": 0, "baseline_shift": 0, "contrast_against": "#132238"},
    {"kind": "text", "role": "author", "text": "Dan Fakkeldy", "font_id": "technical-mono", "box": [96, 2340, 900, 85], "size": 34, "line_height": 44, "tracking": 3, "align": "left", "colour": "#EF5735", "opacity": 1, "rotation": 0, "baseline_shift": 0, "contrast_against": "#07111F"}
  ]
}
```

- [ ] **Step 8: Render both candidates through the production path**

```bash
/usr/local/bin/python3 skill/scripts/make_cover.py \
  --spec "$DIST/cover-spec-original.json" \
  --out "$DIST/cover-original.png"
/usr/local/bin/python3 skill/scripts/make_cover.py \
  --spec "$DIST/cover-spec-refined.json" \
  --out "$DIST/cover-refined.png"
```

Expected: both commands exit 0 and create full covers, `-thumbnail.png` files, and `.render.json` receipts. The refined receipt may retain the known 2.97:1 cream-on-orange large-title advisory; no other warning is accepted.

- [ ] **Step 9: Run the structural gate and confirm GREEN**

```bash
/usr/local/bin/python3 "$PILOT/verify_refinement.py"
```

Expected: exit 0 with exactly `REFINEMENT_VERIFIED`.

- [ ] **Step 10: Verify repository status and close the task without a commit**

```bash
git status --short --branch
git diff --check
```

Expected: branch is `codex/adaptive-cover-spec-implementation`; no pilot file appears because the run is ignored; no tracked diff exists. Do not commit ignored pilot artifacts.

---

### Task 2: Prove Determinism, Review the Visual Result, and Stop at the Human Gate

**Files:**
- Create ignored: `.build/custom-learning-audiobooks/rodents-in-the-walls-c2-refinement/dist/comparison-input.json`
- Create ignored: `.build/custom-learning-audiobooks/rodents-in-the-walls-c2-refinement/comparison.png`
- Create ignored: `.build/custom-learning-audiobooks/rodents-in-the-walls-c2-refinement/title-zone-comparison.png`
- Create ignored: `.build/custom-learning-audiobooks/rodents-in-the-walls-c2-refinement/visual-review.md`
- Create ignored on failed round only: `.build/custom-learning-audiobooks/rodents-in-the-walls-c2-refinement/history/round-N/`
- Modify tracked/public/iCloud files: none

**Interfaces:**
- Consumes: structurally verified original/refined artifacts from Task 1.
- Produces: deterministic comparison surfaces, a passed visual-review receipt, and an explicit human approval request. It intentionally does not produce a selection receipt.

- [ ] **Step 1: Record first-render hashes, rerender, and compare byte-for-byte**

```bash
shasum -a 256 \
  "$DIST/cover-original.png" \
  "$DIST/cover-original-thumbnail.png" \
  "$DIST/cover-original.render.json" \
  "$DIST/cover-refined.png" \
  "$DIST/cover-refined-thumbnail.png" \
  "$DIST/cover-refined.render.json" \
  > "$PILOT/evidence/render-hashes-first.txt"
/usr/local/bin/python3 skill/scripts/make_cover.py \
  --spec "$DIST/cover-spec-original.json" \
  --out "$DIST/cover-original.png"
/usr/local/bin/python3 skill/scripts/make_cover.py \
  --spec "$DIST/cover-spec-refined.json" \
  --out "$DIST/cover-refined.png"
shasum -a 256 \
  "$DIST/cover-original.png" \
  "$DIST/cover-original-thumbnail.png" \
  "$DIST/cover-original.render.json" \
  "$DIST/cover-refined.png" \
  "$DIST/cover-refined-thumbnail.png" \
  "$DIST/cover-refined.render.json" \
  > "$PILOT/evidence/render-hashes-second.txt"
cmp "$PILOT/evidence/render-hashes-first.txt" "$PILOT/evidence/render-hashes-second.txt"
```

Expected: `cmp` exits 0; all six artifacts are byte-identical across runs.

- [ ] **Step 2: Create and render the exact ordered comparison manifest**

Use `apply_patch` to create `$DIST/comparison-input.json`:

```json
[
  {
    "title": "Original C2 — Integrated Colour Band",
    "cover": ".build/custom-learning-audiobooks/rodents-in-the-walls-c2-refinement/dist/cover-original.png"
  },
  {
    "title": "Refined C2A — Compact Ribbon / Editorial Footer",
    "cover": ".build/custom-learning-audiobooks/rodents-in-the-walls-c2-refinement/dist/cover-refined.png"
  }
]
```

Render twice through the ordinary CLI:

```bash
/usr/local/bin/python3 skill/scripts/make_cover_contact_sheet.py \
  --manifest "$DIST/comparison-input.json" \
  --out "$PILOT/comparison.png"
shasum -a 256 "$PILOT/comparison.png" > "$PILOT/evidence/comparison-hash-first.txt"
/usr/local/bin/python3 skill/scripts/make_cover_contact_sheet.py \
  --manifest "$DIST/comparison-input.json" \
  --out "$PILOT/comparison.png"
shasum -a 256 "$PILOT/comparison.png" > "$PILOT/evidence/comparison-hash-second.txt"
cmp "$PILOT/evidence/comparison-hash-first.txt" "$PILOT/evidence/comparison-hash-second.txt"
```

Expected: both runs exit 0, Unicode em dashes render, and `cmp` exits 0.

- [ ] **Step 3: Build a full-resolution title-zone comparison**

```bash
magick "$DIST/cover-original.png" -crop 1600x1100+0+0 +repage "$PILOT/evidence/original-title-zone.png"
magick "$DIST/cover-refined.png" -crop 1600x1100+0+0 +repage "$PILOT/evidence/refined-title-zone.png"
magick "$PILOT/evidence/original-title-zone.png" "$PILOT/evidence/refined-title-zone.png" +append "$PILOT/title-zone-comparison.png"
```

Expected: `title-zone-comparison.png` is 3200 × 1100 and preserves full-resolution shadow edges for inspection.

- [ ] **Step 4: Inspect every required visual surface**

Use the image viewer at original detail on these exact absolute paths:

```text
/Users/dfakkeldy/.codex/worktrees/adaptive-cover-spec-implementation/explainer-audiobooks/.build/custom-learning-audiobooks/rodents-in-the-walls-c2-refinement/comparison.png
/Users/dfakkeldy/.codex/worktrees/adaptive-cover-spec-implementation/explainer-audiobooks/.build/custom-learning-audiobooks/rodents-in-the-walls-c2-refinement/title-zone-comparison.png
/Users/dfakkeldy/.codex/worktrees/adaptive-cover-spec-implementation/explainer-audiobooks/.build/custom-learning-audiobooks/rodents-in-the-walls-c2-refinement/dist/cover-original.png
/Users/dfakkeldy/.codex/worktrees/adaptive-cover-spec-implementation/explainer-audiobooks/.build/custom-learning-audiobooks/rodents-in-the-walls-c2-refinement/dist/cover-refined.png
/Users/dfakkeldy/.codex/worktrees/adaptive-cover-spec-implementation/explainer-audiobooks/.build/custom-learning-audiobooks/rodents-in-the-walls-c2-refinement/dist/cover-original-thumbnail.png
/Users/dfakkeldy/.codex/worktrees/adaptive-cover-spec-implementation/explainer-audiobooks/.build/custom-learning-audiobooks/rodents-in-the-walls-c2-refinement/dist/cover-refined-thumbnail.png
```

Confirm all of these observations before proceeding:

- the refined orange ribbon ends above the first rodent silhouette with at least 24 pixels of visually clear navy;
- no title glyph, outline, field, or cream rule covers any shadow;
- `RODENTS / IN THE / WALLS` remains immediate and correctly ordered at 160 pixels;
- the central wall opening and complete branch-shadow composition remain the second read;
- the short orange footer rule, two-line cream subtitle, and orange author read as one left-aligned unit;
- the footer uses a soft gradient rather than a visible hard rectangle;
- title, subtitle, author, and label spelling are exact;
- no text or effect clips the 96-pixel safe margin;
- cream `WALLS` plus navy outline remains crisp at full size and 160 pixels despite the retained advisory;
- the refined cover is less template-like than original C2.

- [ ] **Step 5: If any visual observation fails, preserve the round and change one variable**

Do not proceed with a failed observation. Create the next numbered history folder and preserve the current refined inputs/outputs:

```bash
ROUND="$PILOT/history/round-1"
test ! -e "$ROUND"
mkdir -p "$ROUND"
cp "$DIST/cover-spec-refined.json" "$DIST/cover-refined.png" \
  "$DIST/cover-refined-thumbnail.png" "$DIST/cover-refined.render.json" \
  "$PILOT/comparison.png" "$PILOT/title-zone-comparison.png" "$ROUND/"
```

Then change exactly one failed property in `cover-spec-refined.json` with `apply_patch`:

- move the entire ribbon upward or reduce its height if shadow clearance fails;
- reduce only the affected title size/box if the compact stack clips;
- increase only the footer subtitle size or line spacing if the lockup is weak;
- switch only `WALLS` from cream to navy and remove its outline if the advisory is visually unacceptable.

Rerun Task 1 Steps 8–9 and Task 2 Steps 1–4. For a second failure use `history/round-2`, then increment monotonically. Never edit `cover-source.png`.

- [ ] **Step 6: Write the pass-only visual review receipt**

Only after every Step 4 observation is true, use `apply_patch` to create `$PILOT/visual-review.md` with this exact content:

```markdown
# Rodents C2A Visual Review

- PASS — the compact orange ribbon ends above every rodent silhouette with at least 24 pixels of clear navy.
- PASS — no title field, binding rule, glyph, outline, or effect covers a shadow.
- PASS — title hierarchy is immediate at full size and 160 pixels.
- PASS — the central opening and complete branch-shadow composition remain visually dominant.
- PASS — the short orange rule, two-line cream subtitle, and orange author form one editorial footer lockup.
- PASS — the lower support is a soft gradient, not a hard footer container.
- PASS — all metadata spelling is exact and all text remains inside the safe margin.
- PASS — the pinned Fraunces, Space Grotesk, Barlow Condensed, and IBM Plex Mono roles are visibly distinct.
- PASS — the refined result is less template-like than original C2.
- PASS — original/refined renders and the ordinary-CLI comparison are deterministic.
```

- [ ] **Step 7: Re-run the structural and no-mutation gates**

```bash
/usr/local/bin/python3 "$PILOT/verify_refinement.py"
test ! -e "$PILOT/cover-selection.json"
test -z "$(find "$PILOT" -name cover-selection.json -print -quit)"
/usr/local/bin/python3 tools/validate_skills.py
/usr/local/bin/python3 -m unittest discover -s tests -v
git diff --check
git status --short --branch
```

Expected: `REFINEMENT_VERIFIED`; both selection checks exit 0; `validate_skills: clean`; all 122 or more tests pass; no whitespace errors; tracked tree clean; branch remains `codex/adaptive-cover-spec-implementation`.

- [ ] **Step 8: Present the refined cover and stop**

Show Dan:

- `comparison.png`;
- `cover-refined.png`;
- `cover-refined-thumbnail.png`;
- `title-zone-comparison.png`;
- candidate id/name;
- cover, thumbnail, specification, source-art, and contact-sheet SHA-256 values;
- the retained 2.97:1 advisory if cream `WALLS` remains;
- confirmation that all nine protected package files are byte-, size-, and mtime-identical.

Ask for explicit approval of **C2A — Compact Ribbon / Editorial Footer** or one final requested change. Do not create a selection receipt, modify an EPUB/M4B, sync a public/iCloud package, commit pilot scratch, push, or open a PR. This human gate is successful completion of this plan, not a blocker.

## Post-Gate Handoff

After Dan explicitly approves C2A, return to Task 9 of
`docs/superpowers/plans/2026-07-12-adaptive-cover-specification.md`. Adapt its
selected candidate paths to this refinement run and execute its governed
selection, EPUB, M4B, public-package, and iCloud-package workflow. That package
promotion is intentionally outside this refinement plan's authorization.
