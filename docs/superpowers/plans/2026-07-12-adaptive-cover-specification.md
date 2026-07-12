# Adaptive Audiobook Cover Specification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic, art-directed cover-specification pipeline and prove it with three final *Rodents in the Walls* candidates, then propagate only the explicitly selected pilot cover through the public EPUB, M4B, repository package, and iCloud delivery folder.

**Architecture:** Keep `skill/scripts/make_cover.py` as the public CLI and legacy compatibility adapter, but move new behavior into focused modules: licensed-font resolution, specification validation, SVG rendering, selection/package receipts, M4B artwork replacement, and guarded delivery. Candidate specifications and source art live in the ignored build run until Dan selects a final render; only the selected public-safe art/spec/receipts and verified package changes are promoted into `books/rodents-in-the-walls/`.

**Tech Stack:** Python 3.11 at `/usr/local/bin/python3`, Python standard library, existing Pillow 9.4 runtime for EPUB/contact-sheet tests, SVG 1.1, `rsvg-convert`, ImageMagick, AtomicParsley, `ffmpeg`/`ffprobe`, `unittest`, EPUB/OPF XML, JSON, Git, and GitHub CLI.

## Global Constraints

- Final covers are exactly 1600×2560 pixels. Text safe margins are 96 pixels on every edge; art, fields, and intentional bleed shapes may extend to the canvas edge.
- Every candidate combines its own art crop, font choices, title runs, line breaks, scale, placement, palette, and effects. A candidate is never an image dropped into the legacy Georgia footer.
- Generated raster art remains text-free. The deterministic renderer owns the title, subtitle, author, and `AUDIOBOOK` label.
- Exactly three final pilot candidates are required: a full-bleed display treatment, an integrated colour-band treatment, and an expressive-run treatment that proves word/glyph-level composition.
- The Rodents pilot deliberately reuses the already approved text-free source art with SHA-256 `cced16a14a0aaced901af7ffd0b140c4d6e13fdf88bd3da22a9724fb7bad9812`. This isolates the typography/compositor proof. Future three-candidate sets must also differ in metaphor, art language, palette, and crop.
- The B1 shadow-branches study is the expressive quality benchmark; the selected C architecture is the repeatable system. Do not copy any named reference cover, publisher system, lettering, logo, or artwork.
- The checked-in JSON schema is the reviewable v1 contract; `cover_spec.py` is authoritative at runtime. Do not add a third-party JSON Schema dependency.
- Specification input is restricted data. Do not accept raw SVG, CSS, HTML, Python, shell, or executable hooks as specification layers.
- Bundle only the four pinned SIL Open Font License assets in Task 1. Missing files, hash mismatches, unsupported glyphs, or unknown `font_id` values are hard failures; no Georgia/Helvetica/system-font substitution is allowed on the new path.
- New-spec errors must leave no final cover, thumbnail, or render receipt and must never fall through to `--layout bleed` or `--layout hero`.
- Keep all existing legacy CLI flags and their current behavior until a later migration removes them deliberately.
- A final cover requires an explicit `explicit-user-choice` or `requested-mix` selection receipt. Never auto-select the first valid candidate.
- The standalone cover and EPUB-declared cover member must be byte-identical. M4B art must match after RGB pixel normalization. Repo and iCloud copies must match the selection receipt.
- Public-repo writes require `privacy.classification = "public-safe"` and `privacy.permission_to_publish = "granted"`. Private packages remain outside `books/` and the public KB.
- Do not change the current Rodents public cover, EPUB, M4B, README, or iCloud package before the three candidate renders are presented and Dan explicitly chooses one.
- Do not regenerate any other book cover in this slice. Do not change manuscript, narration audio packets, alignment data, interior figures, or unrelated delivery files.
- Use `/usr/local/bin/python3` for repository tests on this Mac; the Homebrew Python 3.14 currently first on `PATH` does not have Pillow.
- Base the implementation worktree on current `origin/main`; use a `codex/` feature branch, frequent Conventional Commits, a ready PR into `main`, and explicit hosted-check status.

---

## File Map

### Font and specification boundary

- Create `tools/fetch_cover_fonts.py`: fetch only the pinned font/license assets, verify SHA-256 before replacing destination files, and support an idempotent `--check` mode.
- Create `skill/assets/fonts/manifest.json`: stable font identifiers, roles, axes, source URLs/commit, asset hashes, licence paths/hashes, and width factors.
- Create `skill/assets/fonts/BarlowCondensed-Black.ttf`: `display-condensed` role.
- Create `skill/assets/fonts/Fraunces-Variable.ttf`: `editorial-serif` role.
- Create `skill/assets/fonts/SpaceGrotesk-Variable.ttf`: `geometric-sans` role.
- Create `skill/assets/fonts/IBMPlexMono-Bold.ttf`: `technical-mono` role.
- Create four licence receipts under `skill/assets/fonts/licenses/`.
- Create `skill/scripts/cover_fonts.py`: validated, hash-checked font-manifest loader.
- Create `skill/schemas/cover-spec-v1.schema.json`: checked-in v1 data contract.
- Create `skill/scripts/cover_spec.py`: authoritative runtime validation and normalized specification model.
- Create `tests/test_cover_fonts.py` and `tests/test_cover_spec.py`.

### Rendering and receipts

- Create `skill/scripts/cover_renderer.py`: deterministic SVG construction, rasterization, thumbnail output, and render receipts.
- Modify `skill/scripts/make_cover.py`: add mutually exclusive `--spec` behavior while preserving the existing legacy CLI.
- Extend `tests/test_make_cover.py`; create `tests/test_cover_renderer.py`.
- Create `skill/scripts/cover_receipts.py`: explicit selection receipt creation plus standalone/EPUB/M4B/receipt identity verification.
- Create `tests/test_cover_receipts.py`.

### Package propagation

- Create `skill/scripts/replace_m4b_cover.py`: AtomicParsley-based artwork replacement with unchanged audio-packet and chapter/stream verification.
- Create `tests/test_replace_m4b_cover.py`.
- Create `skill/scripts/sync_selected_cover.py`: classify destination receipts, fail on conflicts, copy cover-bearing artifacts transactionally, update an existing checksum manifest, and roll back on failure.
- Create `tests/test_sync_selected_cover.py`.
- Modify `skill/scripts/build_book.py`: optional `--cover-selection` verification for new builds, retaining legacy `--cover` compatibility.
- Create `tests/test_build_book_cover_receipt.py`.

### Workflow documentation and pilot

- Modify `skill/references/cover-art.md`, `skill/SKILL.md`, `skills/custom-learning-audiobook/SKILL.md`, `skills/custom-learning-audiobook/references/package-and-qc.md`, and `docs/how-these-were-made.md`.
- Create ignored pilot inputs and outputs under `.build/custom-learning-audiobooks/rodents-in-the-walls-cover-pilot/dist/`.
- After explicit selection only, create `books/rodents-in-the-walls/cover-source.png`, `cover-spec.json`, `cover-thumbnail.png`, `cover.render.json`, `cover-selection.json`, and `cover-pre-adaptive.png`; modify the selected `cover.png`, EPUB, M4B, and README.
- After explicit selection only, create `docs/cover-pilots/rodents-adaptive-2026-07/manifest.md` and `contact-sheet.png`.
- After explicit selection only, synchronize and verify the matching iCloud delivery package.

---

### Task 1: Pinned Licensed Font Library

**Files:**
- Create: `tools/fetch_cover_fonts.py`
- Create: `skill/scripts/cover_fonts.py`
- Create: `skill/assets/fonts/manifest.json`
- Create: `skill/assets/fonts/*.ttf`
- Create: `skill/assets/fonts/licenses/*.txt`
- Test: `tests/test_cover_fonts.py`

**Interfaces:**
- Consumes: `load_font_manifest(path: Path = DEFAULT_MANIFEST) -> FontManifest`.
- Produces: `FontRecord`, `FontManifest`, and an idempotent asset-fetch/check command.

- [ ] **Step 1: Write the failing manifest tests**

Create `tests/test_cover_fonts.py` with a temporary manifest so corruption and path-safety behavior do not depend on the checked-in binary assets:

```python
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "skill" / "scripts"))
from cover_fonts import CoverFontError, load_font_manifest


class CoverFontManifestTests(unittest.TestCase):
    def make_manifest(self, root: Path) -> Path:
        font = root / "Demo.ttf"
        licence = root / "demo-OFL.txt"
        font.write_bytes(b"font-bytes")
        licence.write_text("SIL OPEN FONT LICENSE Version 1.1", encoding="utf-8")
        payload = {
            "manifest_version": 1,
            "source_commit": "a" * 40,
            "fonts": [
                {
                    "font_id": "display-condensed",
                    "family": "Demo",
                    "style": "Black",
                    "roles": ["title", "label"],
                    "path": "Demo.ttf",
                    "sha256": hashlib.sha256(font.read_bytes()).hexdigest(),
                    "license": "OFL-1.1",
                    "license_path": "demo-OFL.txt",
                    "license_sha256": hashlib.sha256(licence.read_bytes()).hexdigest(),
                    "source_url": "https://example.invalid/Demo.ttf",
                    "glyph_coverage": ["latin", "latin-ext"],
                    "width_factor": 0.48,
                    "axes": {},
                }
            ],
        }
        manifest = root / "manifest.json"
        manifest.write_text(json.dumps(payload), encoding="utf-8")
        return manifest

    def test_loads_hash_checked_font_record(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = load_font_manifest(self.make_manifest(Path(raw)))
            record = manifest.require("display-condensed", role="title")
            self.assertEqual("Demo", record.family)
            self.assertEqual(0.48, record.width_factor)
            self.assertTrue(record.path.is_file())

    def test_rejects_tampered_font_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = self.make_manifest(Path(raw))
            (Path(raw) / "Demo.ttf").write_bytes(b"tampered")
            with self.assertRaisesRegex(CoverFontError, "font hash mismatch"):
                load_font_manifest(path)

    def test_rejects_unknown_role_and_unknown_identifier(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = load_font_manifest(self.make_manifest(Path(raw)))
            with self.assertRaisesRegex(CoverFontError, "does not support role author"):
                manifest.require("display-condensed", role="author")
            with self.assertRaisesRegex(CoverFontError, "unknown font_id"):
                manifest.require("missing", role="title")

    def test_rejects_asset_path_escape(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            manifest_path = self.make_manifest(root)
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            payload["fonts"][0]["path"] = "../outside.ttf"
            manifest_path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(CoverFontError, "escapes font directory"):
                load_font_manifest(manifest_path)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the focused test and confirm the missing-module failure**

Run:

```bash
/usr/local/bin/python3 -m unittest tests.test_cover_fonts -v
```

Expected: import failure for `cover_fonts`.

- [ ] **Step 3: Add the pinned fetcher and manifest**

Create `tools/fetch_cover_fonts.py` with this fixed asset list and atomic hash gate:

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import os
import tempfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).parents[1]
DESTINATION = REPO_ROOT / "skill" / "assets" / "fonts"
SOURCE_COMMIT = "ec0464b978de222073645d6d3366f3fdf03376d8"
BASE = f"https://raw.githubusercontent.com/google/fonts/{SOURCE_COMMIT}"


@dataclass(frozen=True)
class Asset:
    relative_url: str
    destination: str
    sha256: str


ASSETS = (
    Asset("ofl/barlowcondensed/BarlowCondensed-Black.ttf", "BarlowCondensed-Black.ttf", "e74b750df582c608f35db467b711b2b60d2217618e85e60b72b42dfd00446cab"),
    Asset("ofl/fraunces/Fraunces%5BSOFT%2CWONK%2Copsz%2Cwght%5D.ttf", "Fraunces-Variable.ttf", "177ff6c0f14e5550a3c624247cd1189611d4eb65d000b14944c63d967958abbb"),
    Asset("ofl/spacegrotesk/SpaceGrotesk%5Bwght%5D.ttf", "SpaceGrotesk-Variable.ttf", "acad6de1fc93436f5c0f1f4137751ef04f1aea3063e7036535970ffcfbd79f72"),
    Asset("ofl/ibmplexmono/IBMPlexMono-Bold.ttf", "IBMPlexMono-Bold.ttf", "ac27abd6450a64dd94467580a02fe6235156d5b92f2926ebbc8e7489df64e0be"),
    Asset("ofl/barlowcondensed/OFL.txt", "licenses/barlow-condensed-OFL.txt", "186d750eb496a4c17a76385f82be6aea2ac1cf2de074a811d63786cf374ea73f"),
    Asset("ofl/fraunces/OFL.txt", "licenses/fraunces-OFL.txt", "bdf4c22802eaf804f998195871c6b8938aac2ac14b2d78a8bd66a6f1eced833b"),
    Asset("ofl/spacegrotesk/OFL.txt", "licenses/space-grotesk-OFL.txt", "564ce565c371c5e5bbf286006565a7c9aa55a9f56e7ca58d56e05d649dd61a72"),
    Asset("ofl/ibmplexmono/OFL.txt", "licenses/ibm-plex-mono-OFL.txt", "7e6b2818edbd8f6a01ae80641cc8f16a51080d08fb4e532be3a0b6f74adb07da"),
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(asset: Asset, check_only: bool) -> None:
    target = DESTINATION / asset.destination
    if check_only:
        if not target.is_file() or digest(target.read_bytes()) != asset.sha256:
            raise SystemExit(f"FONT_ASSET_INVALID {asset.destination}")
        print(f"FONT_ASSET_OK {asset.destination}")
        return
    with urllib.request.urlopen(f"{BASE}/{asset.relative_url}", timeout=30) as response:
        data = response.read()
    if digest(data) != asset.sha256:
        raise SystemExit(f"FONT_DOWNLOAD_HASH_MISMATCH {asset.destination}")
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, raw = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
        os.replace(raw, target)
    finally:
        if os.path.exists(raw):
            os.unlink(raw)
    print(f"FONT_ASSET_INSTALLED {asset.destination}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    for asset in ASSETS:
        fetch(asset, arguments.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Create `skill/assets/fonts/manifest.json` with exactly these four stable identifiers:

```json
{
  "manifest_version": 1,
  "source_commit": "ec0464b978de222073645d6d3366f3fdf03376d8",
  "fonts": [
    {
      "font_id": "display-condensed",
      "family": "Barlow Condensed",
      "style": "Black",
      "roles": ["title", "label"],
      "path": "BarlowCondensed-Black.ttf",
      "sha256": "e74b750df582c608f35db467b711b2b60d2217618e85e60b72b42dfd00446cab",
      "license": "OFL-1.1",
      "license_path": "licenses/barlow-condensed-OFL.txt",
      "license_sha256": "186d750eb496a4c17a76385f82be6aea2ac1cf2de074a811d63786cf374ea73f",
      "source_url": "https://raw.githubusercontent.com/google/fonts/ec0464b978de222073645d6d3366f3fdf03376d8/ofl/barlowcondensed/BarlowCondensed-Black.ttf",
      "glyph_coverage": ["latin", "latin-ext"],
      "width_factor": 0.46,
      "axes": {}
    },
    {
      "font_id": "editorial-serif",
      "family": "Fraunces",
      "style": "Variable Roman",
      "roles": ["title", "subtitle", "author"],
      "path": "Fraunces-Variable.ttf",
      "sha256": "177ff6c0f14e5550a3c624247cd1189611d4eb65d000b14944c63d967958abbb",
      "license": "OFL-1.1",
      "license_path": "licenses/fraunces-OFL.txt",
      "license_sha256": "bdf4c22802eaf804f998195871c6b8938aac2ac14b2d78a8bd66a6f1eced833b",
      "source_url": "https://raw.githubusercontent.com/google/fonts/ec0464b978de222073645d6d3366f3fdf03376d8/ofl/fraunces/Fraunces%5BSOFT%2CWONK%2Copsz%2Cwght%5D.ttf",
      "glyph_coverage": ["latin", "latin-ext", "vietnamese"],
      "width_factor": 0.59,
      "axes": {"SOFT": [0, 100], "WONK": [0, 1], "opsz": [9, 144], "wght": [100, 900]}
    },
    {
      "font_id": "geometric-sans",
      "family": "Space Grotesk",
      "style": "Variable Roman",
      "roles": ["title", "subtitle", "author", "label"],
      "path": "SpaceGrotesk-Variable.ttf",
      "sha256": "acad6de1fc93436f5c0f1f4137751ef04f1aea3063e7036535970ffcfbd79f72",
      "license": "OFL-1.1",
      "license_path": "licenses/space-grotesk-OFL.txt",
      "license_sha256": "564ce565c371c5e5bbf286006565a7c9aa55a9f56e7ca58d56e05d649dd61a72",
      "source_url": "https://raw.githubusercontent.com/google/fonts/ec0464b978de222073645d6d3366f3fdf03376d8/ofl/spacegrotesk/SpaceGrotesk%5Bwght%5D.ttf",
      "glyph_coverage": ["latin", "latin-ext", "vietnamese"],
      "width_factor": 0.55,
      "axes": {"wght": [300, 700]}
    },
    {
      "font_id": "technical-mono",
      "family": "IBM Plex Mono",
      "style": "Bold",
      "roles": ["title", "subtitle", "author", "label"],
      "path": "IBMPlexMono-Bold.ttf",
      "sha256": "ac27abd6450a64dd94467580a02fe6235156d5b92f2926ebbc8e7489df64e0be",
      "license": "OFL-1.1",
      "license_path": "licenses/ibm-plex-mono-OFL.txt",
      "license_sha256": "7e6b2818edbd8f6a01ae80641cc8f16a51080d08fb4e532be3a0b6f74adb07da",
      "source_url": "https://raw.githubusercontent.com/google/fonts/ec0464b978de222073645d6d3366f3fdf03376d8/ofl/ibmplexmono/IBMPlexMono-Bold.ttf",
      "glyph_coverage": ["latin", "latin-ext"],
      "width_factor": 0.60,
      "axes": {}
    }
  ]
}
```

Run the fetcher, then immediately run its offline check:

```bash
/usr/local/bin/python3 tools/fetch_cover_fonts.py
/usr/local/bin/python3 tools/fetch_cover_fonts.py --check
```

Expected: eight `FONT_ASSET_INSTALLED` lines followed by eight `FONT_ASSET_OK` lines.

- [ ] **Step 4: Implement the manifest loader**

Create `skill/scripts/cover_fonts.py` with immutable records, safe relative resolution, duplicate detection, role checks, and byte verification:

```python
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

DEFAULT_MANIFEST = Path(__file__).parents[1] / "assets" / "fonts" / "manifest.json"


class CoverFontError(ValueError):
    pass


@dataclass(frozen=True)
class FontRecord:
    font_id: str
    family: str
    style: str
    roles: tuple[str, ...]
    path: Path
    sha256: str
    license: str
    license_path: Path
    license_sha256: str
    source_url: str
    glyph_coverage: tuple[str, ...]
    width_factor: float
    axes: dict[str, tuple[float, float]]


@dataclass(frozen=True)
class FontManifest:
    version: int
    source_commit: str
    path: Path
    sha256: str
    fonts: dict[str, FontRecord]

    def require(self, font_id: str, *, role: str) -> FontRecord:
        if font_id not in self.fonts:
            raise CoverFontError(f"unknown font_id: {font_id}")
        record = self.fonts[font_id]
        if role not in record.roles:
            raise CoverFontError(f"font_id {font_id} does not support role {role}")
        return record


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _safe_asset(root: Path, value: str) -> Path:
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as error:
        raise CoverFontError(f"asset path escapes font directory: {value}") from error
    return candidate


def load_font_manifest(path: Path = DEFAULT_MANIFEST) -> FontManifest:
    manifest_path = Path(path).resolve()
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CoverFontError(f"invalid font manifest: {manifest_path}") from error
    if payload.get("manifest_version") != 1:
        raise CoverFontError("font manifest_version must be 1")
    records: dict[str, FontRecord] = {}
    for raw in payload.get("fonts", []):
        font_id = raw.get("font_id", "")
        if not font_id or font_id in records:
            raise CoverFontError(f"duplicate or empty font_id: {font_id}")
        font_path = _safe_asset(manifest_path.parent, raw.get("path", ""))
        licence_path = _safe_asset(manifest_path.parent, raw.get("license_path", ""))
        if not font_path.is_file() or _digest(font_path) != raw.get("sha256"):
            raise CoverFontError(f"font hash mismatch: {font_id}")
        if not licence_path.is_file() or _digest(licence_path) != raw.get("license_sha256"):
            raise CoverFontError(f"license hash mismatch: {font_id}")
        width_factor = float(raw.get("width_factor", 0))
        if not 0.25 <= width_factor <= 1.0:
            raise CoverFontError(f"invalid width_factor: {font_id}")
        axes = {
            name: (float(bounds[0]), float(bounds[1]))
            for name, bounds in raw.get("axes", {}).items()
        }
        records[font_id] = FontRecord(
            font_id=font_id,
            family=str(raw.get("family", "")),
            style=str(raw.get("style", "")),
            roles=tuple(raw.get("roles", [])),
            path=font_path,
            sha256=str(raw.get("sha256", "")),
            license=str(raw.get("license", "")),
            license_path=licence_path,
            license_sha256=str(raw.get("license_sha256", "")),
            source_url=str(raw.get("source_url", "")),
            glyph_coverage=tuple(raw.get("glyph_coverage", [])),
            width_factor=width_factor,
            axes=axes,
        )
    if not records:
        raise CoverFontError("font manifest contains no fonts")
    return FontManifest(
        version=1,
        source_commit=str(payload.get("source_commit", "")),
        path=manifest_path,
        sha256=_digest(manifest_path),
        fonts=records,
    )
```

- [ ] **Step 5: Run focused and asset verification**

Run:

```bash
/usr/local/bin/python3 -m unittest tests.test_cover_fonts -v
/usr/local/bin/python3 tools/fetch_cover_fonts.py --check
```

Expected: four tests pass and all eight assets report `FONT_ASSET_OK`.

- [ ] **Step 6: Commit the licensed font boundary**

```bash
git add tools/fetch_cover_fonts.py skill/assets/fonts skill/scripts/cover_fonts.py tests/test_cover_fonts.py
git commit -m "feat: add licensed audiobook cover fonts"
```

---

### Task 2: Versioned Cover-Specification Validation

**Files:**
- Create: `skill/schemas/cover-spec-v1.schema.json`
- Create: `skill/scripts/cover_spec.py`
- Test: `tests/test_cover_spec.py`

**Interfaces:**
- Consumes: `load_cover_spec(path: Path, font_manifest_path: Path = DEFAULT_MANIFEST) -> ValidatedCoverSpec`.
- Produces: canonical specification/art hashes, normalized layer data, resolved font records, and advisory contrast warnings.

- [ ] **Step 1: Write failing happy-path and rejection tests**

Create `tests/test_cover_spec.py`. The helper writes a minimal source-art SVG and a complete valid specification; each negative test changes one contract dimension:

```python
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "skill" / "scripts"))
from cover_spec import CoverSpecError, load_cover_spec

FONT_MANIFEST = Path(__file__).parents[1] / "skill" / "assets" / "fonts" / "manifest.json"


def valid_payload() -> dict[str, object]:
    return {
        "schema_version": 1,
        "candidate": {"id": "candidate-a", "direction_name": "Full Bleed Display"},
        "metadata": {
            "title": "Rodents in the Walls",
            "subtitle": "Squirrels and Other Houseguests",
            "author": "Dan Fakkeldy",
            "label": "AUDIOBOOK",
        },
        "canvas": {
            "width": 1600,
            "height": 2560,
            "background": "#132238",
            "safe_margin": 96,
        },
        "art": {
            "path": "art.svg",
            "mode": "bleed",
            "anchor": "center",
            "box": [0, 0, 1600, 2560],
            "opacity": 1,
            "blend_mode": "normal",
        },
        "layers": [
            {
                "kind": "text",
                "role": "label",
                "text": "AUDIOBOOK",
                "font_id": "geometric-sans",
                "box": [96, 110, 900, 70],
                "size": 36,
                "line_height": 44,
                "tracking": 8,
                "align": "left",
                "colour": "#EF5735",
                "opacity": 1,
                "rotation": 0,
                "baseline_shift": 0,
                "contrast_against": "#132238",
            },
            {
                "kind": "text",
                "role": "title",
                "title_order": 1,
                "text": "RODENTS",
                "font_id": "display-condensed",
                "box": [96, 220, 1408, 300],
                "size": 250,
                "line_height": 260,
                "tracking": 1,
                "align": "left",
                "colour": "#EF5735",
                "opacity": 1,
                "rotation": 0,
                "baseline_shift": 0,
                "contrast_against": "#132238",
            },
            {
                "kind": "text",
                "role": "title",
                "title_order": 2,
                "text": "IN THE WALLS",
                "font_id": "editorial-serif",
                "font_variation": {"wght": 780, "opsz": 96, "SOFT": 30, "WONK": 1},
                "box": [96, 510, 1408, 310],
                "size": 188,
                "line_height": 200,
                "tracking": 0,
                "align": "left",
                "colour": "#F6EDDA",
                "opacity": 1,
                "rotation": 0,
                "baseline_shift": 0,
                "contrast_against": "#132238",
            },
            {
                "kind": "text",
                "role": "subtitle",
                "text": "Squirrels and Other Houseguests",
                "font_id": "geometric-sans",
                "box": [96, 2100, 1408, 130],
                "size": 48,
                "line_height": 58,
                "tracking": 0,
                "align": "left",
                "colour": "#F6EDDA",
                "opacity": 1,
                "rotation": 0,
                "baseline_shift": 0,
                "contrast_against": "#132238",
            },
            {
                "kind": "text",
                "role": "author",
                "text": "Dan Fakkeldy",
                "font_id": "geometric-sans",
                "box": [96, 2320, 1408, 90],
                "size": 42,
                "line_height": 50,
                "tracking": 2,
                "align": "left",
                "colour": "#F6EDDA",
                "opacity": 1,
                "rotation": 0,
                "baseline_shift": 0,
                "contrast_against": "#132238",
            },
        ],
    }


def write_fixture(root: Path, payload: dict[str, object]) -> Path:
    (root / "art.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 2560"><rect width="1600" height="2560" fill="#132238"/></svg>',
        encoding="utf-8",
    )
    path = root / "cover-spec.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


class CoverSpecValidationTests(unittest.TestCase):
    def test_loads_valid_spec_and_reconstructs_canonical_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            spec = load_cover_spec(write_fixture(Path(raw), valid_payload()), FONT_MANIFEST)
            self.assertEqual("Rodents in the Walls", spec.metadata["title"])
            self.assertEqual((1600, 2560), spec.dimensions)
            second = load_cover_spec(write_fixture(Path(raw), valid_payload()), FONT_MANIFEST)
            self.assertEqual(spec.spec_sha256, second.spec_sha256)
            self.assertEqual(64, len(spec.art_sha256))
            self.assertEqual(3, len(spec.fonts))

    def test_rejects_wrong_canvas_without_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            payload = valid_payload()
            payload["canvas"]["width"] = 1200
            with self.assertRaisesRegex(CoverSpecError, "canvas must be 1600x2560"):
                load_cover_spec(write_fixture(Path(raw), payload), FONT_MANIFEST)

    def test_rejects_title_token_omission(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            payload = valid_payload()
            payload["layers"][2]["text"] = "THE WALLS"
            with self.assertRaisesRegex(CoverSpecError, "title layers must reproduce canonical title"):
                load_cover_spec(write_fixture(Path(raw), payload), FONT_MANIFEST)

    def test_rejects_unknown_font_and_path_escape(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            payload = valid_payload()
            payload["layers"][1]["font_id"] = "system-georgia"
            with self.assertRaisesRegex(ValueError, "unknown font_id"):
                load_cover_spec(write_fixture(Path(raw), payload), FONT_MANIFEST)
            payload = valid_payload()
            payload["art"]["path"] = "../outside.png"
            with self.assertRaisesRegex(CoverSpecError, "art path escapes run folder"):
                load_cover_spec(write_fixture(Path(raw), payload), FONT_MANIFEST)

    def test_rejects_text_outside_safe_bounds_and_unbounded_effects(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            payload = valid_payload()
            payload["layers"][0]["box"] = [20, 110, 900, 70]
            with self.assertRaisesRegex(CoverSpecError, "outside 96px safe margin"):
                load_cover_spec(write_fixture(Path(raw), payload), FONT_MANIFEST)
            payload = valid_payload()
            payload["layers"][1]["shadow"] = {
                "colour": "#000000", "dx": 0, "dy": 80, "blur": 12, "opacity": 0.5
            }
            with self.assertRaisesRegex(CoverSpecError, "shadow dy must be between -48 and 48"):
                load_cover_spec(write_fixture(Path(raw), payload), FONT_MANIFEST)

    def test_rejects_run_text_or_axis_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            payload = valid_payload()
            payload["layers"][1]["runs"] = [{"text": "RODENT", "colour": "#EF5735"}]
            with self.assertRaisesRegex(CoverSpecError, "runs must concatenate to layer text"):
                load_cover_spec(write_fixture(Path(raw), payload), FONT_MANIFEST)
            payload = valid_payload()
            payload["layers"][2]["font_variation"]["wght"] = 950
            with self.assertRaisesRegex(CoverSpecError, "axis wght must be between 100 and 900"):
                load_cover_spec(write_fixture(Path(raw), payload), FONT_MANIFEST)

    def test_requires_declared_purpose_for_compositional_fields(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            payload = valid_payload()
            payload["layers"].insert(0, {
                "kind": "field",
                "box": [0, 0, 1600, 500],
                "fill": {"kind": "solid", "colour": "#EF5735"},
                "opacity": 1,
                "blend_mode": "normal"
            })
            with self.assertRaisesRegex(CoverSpecError, "field layer requires compositional purpose"):
                load_cover_spec(write_fixture(Path(raw), payload), FONT_MANIFEST)

    def test_rejects_unknown_layer_keys_and_unsupported_glyphs(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            payload = valid_payload()
            payload["layers"][1]["script"] = "alert(1)"
            with self.assertRaisesRegex(CoverSpecError, "unknown keys"):
                load_cover_spec(write_fixture(Path(raw), payload), FONT_MANIFEST)
            payload = valid_payload()
            payload["layers"][1]["text"] = "RODENTS☃"
            with self.assertRaisesRegex(CoverSpecError, "unsupported glyph"):
                load_cover_spec(write_fixture(Path(raw), payload), FONT_MANIFEST)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the focused test and confirm the missing-module failure**

```bash
/usr/local/bin/python3 -m unittest tests.test_cover_spec -v
```

Expected: import failure for `cover_spec`.

- [ ] **Step 3: Add the reviewable JSON contract**

Create `skill/schemas/cover-spec-v1.schema.json`. It is deliberately dependency-free documentation; the Python validator enforces the same bounds at runtime:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/dfakkeldy/explainer-audiobooks/skill/schemas/cover-spec-v1.schema.json",
  "title": "Explainer Audiobook Cover Specification v1",
  "type": "object",
  "additionalProperties": false,
  "required": ["schema_version", "candidate", "metadata", "canvas", "art", "layers"],
  "properties": {
    "schema_version": {"const": 1},
    "candidate": {
      "type": "object",
      "additionalProperties": false,
      "required": ["id", "direction_name"],
      "properties": {
        "id": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]*$"},
        "direction_name": {"type": "string", "minLength": 1}
      }
    },
    "metadata": {
      "type": "object",
      "additionalProperties": false,
      "required": ["title", "subtitle", "author", "label"],
      "properties": {
        "title": {"type": "string", "minLength": 1},
        "subtitle": {"type": "string"},
        "author": {"type": "string", "minLength": 1},
        "label": {"type": "string", "minLength": 1}
      }
    },
    "canvas": {
      "type": "object",
      "additionalProperties": false,
      "required": ["width", "height", "background", "safe_margin"],
      "properties": {
        "width": {"const": 1600},
        "height": {"const": 2560},
        "background": {"$ref": "#/$defs/colour"},
        "safe_margin": {"const": 96}
      }
    },
    "art": {
      "type": "object",
      "additionalProperties": false,
      "required": ["path", "mode", "anchor", "box", "opacity", "blend_mode"],
      "properties": {
        "path": {"type": "string", "minLength": 1},
        "mode": {"enum": ["bleed", "fit", "crop"]},
        "anchor": {"enum": ["center", "center-top", "center-bottom", "left", "right"]},
        "box": {"$ref": "#/$defs/box"},
        "opacity": {"type": "number", "minimum": 0, "maximum": 1},
        "blend_mode": {"$ref": "#/$defs/blend"},
        "mask": {"$ref": "#/$defs/mask"}
      }
    },
    "layers": {
      "type": "array",
      "minItems": 1,
      "items": {
        "oneOf": [
          {"$ref": "#/$defs/text_layer"},
          {"$ref": "#/$defs/field_layer"},
          {"$ref": "#/$defs/shape_layer"},
          {"$ref": "#/$defs/line_layer"}
        ]
      }
    }
  },
  "$defs": {
    "colour": {"type": "string", "pattern": "^#[0-9A-Fa-f]{6}$"},
    "box": {
      "type": "array", "prefixItems": [
        {"type": "number"}, {"type": "number"},
        {"type": "number", "exclusiveMinimum": 0},
        {"type": "number", "exclusiveMinimum": 0}
      ], "minItems": 4, "maxItems": 4
    },
    "point": {
      "type": "array", "prefixItems": [{"type": "number"}, {"type": "number"}],
      "minItems": 2, "maxItems": 2
    },
    "blend": {"enum": ["normal", "multiply", "screen", "overlay", "soft-light"]},
    "fill": {
      "oneOf": [
        {
          "type": "object", "additionalProperties": false,
          "required": ["kind", "colour"],
          "properties": {"kind": {"const": "solid"}, "colour": {"$ref": "#/$defs/colour"}}
        },
        {
          "type": "object", "additionalProperties": false,
          "required": ["kind", "start", "end", "stops"],
          "properties": {
            "kind": {"const": "linear-gradient"},
            "start": {"$ref": "#/$defs/point"},
            "end": {"$ref": "#/$defs/point"},
            "stops": {
              "type": "array", "minItems": 2,
              "items": {
                "type": "object", "additionalProperties": false,
                "required": ["offset", "colour", "opacity"],
                "properties": {
                  "offset": {"type": "number", "minimum": 0, "maximum": 1},
                  "colour": {"$ref": "#/$defs/colour"},
                  "opacity": {"type": "number", "minimum": 0, "maximum": 1}
                }
              }
            }
          }
        }
      ]
    },
    "mask": {
      "type": "object", "additionalProperties": false,
      "required": ["shape", "box"],
      "properties": {
        "shape": {"enum": ["rect", "ellipse"]},
        "box": {"$ref": "#/$defs/box"},
        "radius": {"type": "number", "minimum": 0, "maximum": 300}
      }
    },
    "run": {
      "type": "object", "additionalProperties": false, "required": ["text"],
      "properties": {
        "text": {"type": "string", "minLength": 1},
        "colour": {"$ref": "#/$defs/colour"},
        "size_scale": {"type": "number", "minimum": 0.5, "maximum": 1.5},
        "rotation": {"type": "number", "minimum": -12, "maximum": 12},
        "baseline_shift": {"type": "number", "minimum": -80, "maximum": 80},
        "dx": {"type": "number", "minimum": -80, "maximum": 80},
        "tracking": {"type": "number", "minimum": -8, "maximum": 40}
      }
    },
    "text_layer": {
      "type": "object", "additionalProperties": false,
      "required": ["kind", "role", "text", "font_id", "box", "size", "line_height", "tracking", "align", "colour", "opacity", "rotation", "baseline_shift"],
      "properties": {
        "kind": {"const": "text"},
        "role": {"enum": ["title", "subtitle", "author", "label"]},
        "title_order": {"type": "integer", "minimum": 1},
        "text": {"type": "string", "minLength": 1},
        "font_id": {"type": "string", "minLength": 1},
        "font_variation": {"type": "object", "additionalProperties": {"type": "number"}},
        "box": {"$ref": "#/$defs/box"},
        "size": {"type": "number", "minimum": 28, "maximum": 420},
        "line_height": {"type": "number", "minimum": 28, "maximum": 500},
        "tracking": {"type": "number", "minimum": -8, "maximum": 40},
        "align": {"enum": ["left", "center", "right"]},
        "colour": {"$ref": "#/$defs/colour"},
        "opacity": {"type": "number", "minimum": 0, "maximum": 1},
        "rotation": {"type": "number", "minimum": -12, "maximum": 12},
        "baseline_shift": {"type": "number", "minimum": -80, "maximum": 80},
        "outline": {
          "type": "object", "additionalProperties": false, "required": ["colour", "width"],
          "properties": {"colour": {"$ref": "#/$defs/colour"}, "width": {"type": "number", "minimum": 0, "maximum": 16}}
        },
        "shadow": {
          "type": "object", "additionalProperties": false, "required": ["colour", "dx", "dy", "blur", "opacity"],
          "properties": {
            "colour": {"$ref": "#/$defs/colour"},
            "dx": {"type": "number", "minimum": -48, "maximum": 48},
            "dy": {"type": "number", "minimum": -48, "maximum": 48},
            "blur": {"type": "number", "minimum": 0, "maximum": 48},
            "opacity": {"type": "number", "minimum": 0, "maximum": 1}
          }
        },
        "runs": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/run"}},
        "contrast_against": {"$ref": "#/$defs/colour"},
        "blend_mode": {"$ref": "#/$defs/blend"}
      }
    },
    "field_layer": {
      "type": "object", "additionalProperties": false,
      "required": ["kind", "box", "fill", "opacity", "blend_mode", "purpose"],
      "properties": {
        "kind": {"enum": ["field", "scrim"]},
        "box": {"$ref": "#/$defs/box"},
        "fill": {"$ref": "#/$defs/fill"},
        "opacity": {"type": "number", "minimum": 0, "maximum": 1},
        "blend_mode": {"$ref": "#/$defs/blend"},
        "purpose": {"type": "string", "minLength": 1}
      }
    },
    "shape_layer": {
      "type": "object", "additionalProperties": false,
      "required": ["kind", "shape", "box", "fill", "opacity", "rotation", "blend_mode", "purpose"],
      "properties": {
        "kind": {"const": "shape"},
        "shape": {"enum": ["rect", "ellipse"]},
        "box": {"$ref": "#/$defs/box"},
        "fill": {"$ref": "#/$defs/fill"},
        "stroke": {"$ref": "#/$defs/colour"},
        "stroke_width": {"type": "number", "minimum": 0, "maximum": 40},
        "radius": {"type": "number", "minimum": 0, "maximum": 300},
        "opacity": {"type": "number", "minimum": 0, "maximum": 1},
        "rotation": {"type": "number", "minimum": -180, "maximum": 180},
        "blend_mode": {"$ref": "#/$defs/blend"},
        "purpose": {"type": "string", "minLength": 1}
      }
    },
    "line_layer": {
      "type": "object", "additionalProperties": false,
      "required": ["kind", "start", "end", "colour", "width", "opacity", "purpose"],
      "properties": {
        "kind": {"const": "line"},
        "start": {"$ref": "#/$defs/point"},
        "end": {"$ref": "#/$defs/point"},
        "colour": {"$ref": "#/$defs/colour"},
        "width": {"type": "number", "minimum": 1, "maximum": 40},
        "opacity": {"type": "number", "minimum": 0, "maximum": 1},
        "purpose": {"type": "string", "minLength": 1}
      }
    }
  }
}
```

- [ ] **Step 4: Implement authoritative runtime validation**

Create `skill/scripts/cover_spec.py`. Keep the validated JSON available to the renderer, but resolve paths and fonts up front so rendering never performs aesthetic fallback:

```python
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cover_fonts import DEFAULT_MANIFEST, CoverFontError, FontManifest, FontRecord, load_font_manifest

WIDTH = 1600
HEIGHT = 2560
SAFE_MARGIN = 96
COLOUR = re.compile(r"^#[0-9A-Fa-f]{6}$")
TOKEN = re.compile(r"[0-9A-Za-z]+(?:['’][0-9A-Za-z]+)?")
BLENDS = {"normal", "multiply", "screen", "overlay", "soft-light"}
ART_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}
TEXT_KEYS = {"kind", "role", "title_order", "text", "font_id", "font_variation", "box", "size", "line_height", "tracking", "align", "colour", "opacity", "rotation", "baseline_shift", "outline", "shadow", "runs", "contrast_against", "blend_mode"}
FIELD_KEYS = {"kind", "box", "fill", "opacity", "blend_mode", "purpose"}
SHAPE_KEYS = {"kind", "shape", "box", "fill", "stroke", "stroke_width", "radius", "opacity", "rotation", "blend_mode", "purpose"}
LINE_KEYS = {"kind", "start", "end", "colour", "width", "opacity", "purpose"}
LATIN_PUNCTUATION = set("–—‘’“”…•·©®™")


class CoverSpecError(ValueError):
    pass


@dataclass(frozen=True)
class ValidatedCoverSpec:
    path: Path
    data: dict[str, Any]
    metadata: dict[str, str]
    dimensions: tuple[int, int]
    art_path: Path
    spec_sha256: str
    art_sha256: str
    font_manifest: FontManifest
    fonts: dict[str, FontRecord]
    warnings: tuple[str, ...]


def _canonical_digest(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _safe_child(root: Path, raw: str, label: str) -> Path:
    candidate = (root / raw).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as error:
        raise CoverSpecError(f"{label} path escapes run folder: {raw}") from error
    return candidate


def _number(value: object, low: float, high: float, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise CoverSpecError(f"{label} must be numeric")
    result = float(value)
    if not low <= result <= high:
        raise CoverSpecError(f"{label} must be between {low:g} and {high:g}")
    return result


def _box(value: object, label: str) -> tuple[float, float, float, float]:
    if not isinstance(value, list) or len(value) != 4:
        raise CoverSpecError(f"{label} must contain x, y, width, height")
    x = _number(value[0], -WIDTH, WIDTH * 2, f"{label} x")
    y = _number(value[1], -HEIGHT, HEIGHT * 2, f"{label} y")
    width = _number(value[2], 1, WIDTH * 2, f"{label} width")
    height = _number(value[3], 1, HEIGHT * 2, f"{label} height")
    return x, y, width, height


def _point(value: object, label: str) -> tuple[float, float]:
    if not isinstance(value, list) or len(value) != 2:
        raise CoverSpecError(f"{label} must contain x and y")
    return (
        _number(value[0], -WIDTH, WIDTH * 2, f"{label} x"),
        _number(value[1], -HEIGHT, HEIGHT * 2, f"{label} y"),
    )


def _colour(value: object, label: str) -> str:
    if not isinstance(value, str) or not COLOUR.fullmatch(value):
        raise CoverSpecError(f"{label} must be #RRGGBB")
    return value.upper()


def _tokens(value: str) -> list[str]:
    return [match.group(0).casefold().replace("’", "'") for match in TOKEN.finditer(value)]


def _validate_glyphs(value: str, font: FontRecord, label: str) -> None:
    for character in value:
        codepoint = ord(character)
        if character.isspace() or codepoint < 128 or character in LATIN_PUNCTUATION:
            continue
        if codepoint <= 0x024F and "latin-ext" in font.glyph_coverage:
            continue
        name = unicodedata.name(character, f"U+{codepoint:04X}")
        raise CoverSpecError(f"{label} contains unsupported glyph {name} for {font.font_id}")


def _luminance(value: str) -> float:
    components = [int(value[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [component / 12.92 if component <= 0.04045 else ((component + 0.055) / 1.055) ** 2.4 for component in components]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast(first: str, second: str) -> float:
    high, low = sorted((_luminance(first), _luminance(second)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def _validate_fill(fill: object, label: str) -> None:
    if not isinstance(fill, dict):
        raise CoverSpecError(f"{label} must be an object")
    if fill.get("kind") == "solid":
        if set(fill) != {"kind", "colour"}:
            raise CoverSpecError(f"{label} solid fill has unknown keys")
        _colour(fill.get("colour"), f"{label} colour")
        return
    if fill.get("kind") != "linear-gradient":
        raise CoverSpecError(f"{label} kind must be solid or linear-gradient")
    if set(fill) != {"kind", "start", "end", "stops"}:
        raise CoverSpecError(f"{label} gradient has unknown keys")
    _point(fill.get("start"), f"{label} start")
    _point(fill.get("end"), f"{label} end")
    stops = fill.get("stops")
    if not isinstance(stops, list) or len(stops) < 2:
        raise CoverSpecError(f"{label} requires at least two stops")
    previous = -1.0
    for index, stop in enumerate(stops):
        if not isinstance(stop, dict):
            raise CoverSpecError(f"{label} stop {index + 1} must be an object")
        if set(stop) != {"offset", "colour", "opacity"}:
            raise CoverSpecError(f"{label} stop {index + 1} has unknown keys")
        offset = _number(stop.get("offset"), 0, 1, f"{label} stop offset")
        if offset < previous:
            raise CoverSpecError(f"{label} stop offsets must be sorted")
        previous = offset
        _colour(stop.get("colour"), f"{label} stop colour")
        _number(stop.get("opacity"), 0, 1, f"{label} stop opacity")


def _validate_text(layer: dict[str, Any], index: int, manifest: FontManifest, warnings: list[str]) -> FontRecord:
    unknown = set(layer) - TEXT_KEYS
    if unknown:
        raise CoverSpecError(f"layer {index} has unknown keys: {sorted(unknown)}")
    role = layer.get("role")
    if role not in {"title", "subtitle", "author", "label"}:
        raise CoverSpecError(f"layer {index} has invalid text role")
    text = layer.get("text")
    if not isinstance(text, str) or not text.strip():
        raise CoverSpecError(f"layer {index} text is empty")
    if role == "title" and not isinstance(layer.get("title_order"), int):
        raise CoverSpecError(f"layer {index} title requires title_order")
    font = manifest.require(str(layer.get("font_id", "")), role=role)
    _validate_glyphs(text, font, f"layer {index}")
    x, y, width, height = _box(layer.get("box"), f"layer {index} box")
    if x < SAFE_MARGIN or y < SAFE_MARGIN or x + width > WIDTH - SAFE_MARGIN or y + height > HEIGHT - SAFE_MARGIN:
        raise CoverSpecError(f"layer {index} text is outside 96px safe margin")
    minimum = {"title": 72, "subtitle": 36, "author": 28, "label": 28}[role]
    size = _number(layer.get("size"), minimum, 420, f"layer {index} size")
    line_height = _number(layer.get("line_height"), minimum, 500, f"layer {index} line_height")
    _number(layer.get("tracking"), -8, 40, f"layer {index} tracking")
    _number(layer.get("opacity"), 0, 1, f"layer {index} opacity")
    _number(layer.get("rotation"), -12, 12, f"layer {index} rotation")
    _number(layer.get("baseline_shift"), -80, 80, f"layer {index} baseline_shift")
    if layer.get("align") not in {"left", "center", "right"}:
        raise CoverSpecError(f"layer {index} align must be left, center, or right")
    if layer.get("blend_mode", "normal") not in BLENDS:
        raise CoverSpecError(f"layer {index} has invalid blend_mode")
    colour = _colour(layer.get("colour"), f"layer {index} colour")
    lines = text.split("\n")
    if len(lines) * line_height > height:
        raise CoverSpecError(f"layer {index} text exceeds box height")
    longest = max(lines, key=len)
    estimated = len(longest) * size * font.width_factor + max(0, len(longest) - 1) * float(layer.get("tracking", 0))
    if estimated > width * 1.12:
        raise CoverSpecError(f"layer {index} text exceeds box width estimate")
    runs = layer.get("runs")
    if runs is not None:
        if "\n" in text or not isinstance(runs, list) or not runs:
            raise CoverSpecError(f"layer {index} runs require one non-empty line")
        if "".join(str(run.get("text", "")) for run in runs) != text:
            raise CoverSpecError(f"layer {index} runs must concatenate to layer text")
        for run_index, run in enumerate(runs):
            if not isinstance(run, dict) or not run.get("text"):
                raise CoverSpecError(f"layer {index} run {run_index + 1} is invalid")
            if set(run) - {"text", "colour", "size_scale", "rotation", "baseline_shift", "dx", "tracking"}:
                raise CoverSpecError(f"layer {index} run {run_index + 1} has unknown keys")
            if "colour" in run:
                _colour(run["colour"], f"layer {index} run colour")
            _number(run.get("size_scale", 1), 0.5, 1.5, f"layer {index} run size_scale")
            _number(run.get("rotation", 0), -12, 12, f"layer {index} run rotation")
            _number(run.get("baseline_shift", 0), -80, 80, f"layer {index} run baseline_shift")
            _number(run.get("dx", 0), -80, 80, f"layer {index} run dx")
            _number(run.get("tracking", layer.get("tracking", 0)), -8, 40, f"layer {index} run tracking")
    for axis, value in layer.get("font_variation", {}).items():
        if axis not in font.axes:
            raise CoverSpecError(f"font {font.font_id} does not support axis {axis}")
        low, high = font.axes[axis]
        if not low <= float(value) <= high:
            raise CoverSpecError(f"axis {axis} must be between {low:g} and {high:g}")
    outline = layer.get("outline")
    if outline is not None:
        _colour(outline.get("colour"), f"layer {index} outline colour")
        _number(outline.get("width"), 0, 16, f"layer {index} outline width")
    shadow = layer.get("shadow")
    if shadow is not None:
        _colour(shadow.get("colour"), f"layer {index} shadow colour")
        dx = _number(shadow.get("dx"), -48, 48, f"layer {index} shadow dx")
        dy = _number(shadow.get("dy"), -48, 48, f"layer {index} shadow dy")
        if not -48 <= dx <= 48 or not -48 <= dy <= 48:
            raise CoverSpecError("shadow offsets must be between -48 and 48")
        _number(shadow.get("blur"), 0, 48, f"layer {index} shadow blur")
        _number(shadow.get("opacity"), 0, 1, f"layer {index} shadow opacity")
    against = layer.get("contrast_against")
    if against is None:
        warnings.append(f"layer {index} contrast is unverified over complex art")
    else:
        background = _colour(against, f"layer {index} contrast_against")
        ratio = _contrast(colour, background)
        if ratio < 4.5:
            warnings.append(f"layer {index} advisory contrast ratio is {ratio:.2f}:1")
    return font


def load_cover_spec(path: Path, font_manifest_path: Path = DEFAULT_MANIFEST) -> ValidatedCoverSpec:
    spec_path = Path(path).resolve()
    try:
        payload = json.loads(spec_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CoverSpecError(f"invalid cover specification: {spec_path}") from error
    if payload.get("schema_version") != 1:
        raise CoverSpecError("schema_version must be 1")
    if set(payload) != {"schema_version", "candidate", "metadata", "canvas", "art", "layers"}:
        raise CoverSpecError("cover specification has missing or unknown top-level fields")
    candidate = payload.get("candidate")
    if not isinstance(candidate, dict) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", str(candidate.get("id", ""))) or not candidate.get("direction_name"):
        raise CoverSpecError("candidate requires a slug-like id and direction_name")
    if set(candidate) != {"id", "direction_name"}:
        raise CoverSpecError("candidate has missing or unknown fields")
    metadata = payload.get("metadata")
    if not isinstance(metadata, dict) or set(metadata) != {"title", "subtitle", "author", "label"}:
        raise CoverSpecError("metadata must contain title, subtitle, author, and label")
    if any(not isinstance(metadata[key], str) for key in metadata) or not metadata["title"] or not metadata["author"] or not metadata["label"]:
        raise CoverSpecError("canonical metadata strings are invalid")
    canvas = payload.get("canvas")
    if not isinstance(canvas, dict) or canvas.get("width") != WIDTH or canvas.get("height") != HEIGHT:
        raise CoverSpecError("canvas must be 1600x2560")
    if set(canvas) != {"width", "height", "background", "safe_margin"}:
        raise CoverSpecError("canvas has missing or unknown fields")
    if canvas.get("safe_margin") != SAFE_MARGIN:
        raise CoverSpecError("canvas safe_margin must be 96")
    _colour(canvas.get("background"), "canvas background")
    art = payload.get("art")
    if not isinstance(art, dict):
        raise CoverSpecError("art must be an object")
    if set(art) - {"path", "mode", "anchor", "box", "opacity", "blend_mode", "mask"}:
        raise CoverSpecError("art has unknown fields")
    art_path = _safe_child(spec_path.parent, str(art.get("path", "")), "art")
    if not art_path.is_file() or art_path.suffix.lower() not in ART_SUFFIXES:
        raise CoverSpecError("art must be an existing SVG, PNG, JPEG, WebP, or GIF")
    if art.get("mode") not in {"bleed", "fit", "crop"} or art.get("anchor") not in {"center", "center-top", "center-bottom", "left", "right"}:
        raise CoverSpecError("art mode or anchor is invalid")
    _box(art.get("box"), "art box")
    _number(art.get("opacity"), 0, 1, "art opacity")
    if art.get("blend_mode") not in BLENDS:
        raise CoverSpecError("art blend_mode is invalid")
    if "mask" in art:
        mask = art["mask"]
        if not isinstance(mask, dict) or mask.get("shape") not in {"rect", "ellipse"}:
            raise CoverSpecError("art mask must be rect or ellipse")
        if set(mask) - {"shape", "box", "radius"}:
            raise CoverSpecError("art mask has unknown fields")
        _box(mask.get("box"), "art mask box")
        _number(mask.get("radius", 0), 0, 300, "art mask radius")
    manifest = load_font_manifest(Path(font_manifest_path))
    layers = payload.get("layers")
    if not isinstance(layers, list) or not layers:
        raise CoverSpecError("layers must be a non-empty array")
    warnings: list[str] = []
    fonts: dict[str, FontRecord] = {}
    for index, layer in enumerate(layers, start=1):
        if not isinstance(layer, dict):
            raise CoverSpecError(f"layer {index} must be an object")
        kind = layer.get("kind")
        if kind == "text":
            font = _validate_text(layer, index, manifest, warnings)
            fonts[font.font_id] = font
        elif kind in {"field", "scrim"}:
            if set(layer) - FIELD_KEYS:
                raise CoverSpecError(f"layer {index} has unknown keys")
            _box(layer.get("box"), f"layer {index} box")
            _validate_fill(layer.get("fill"), f"layer {index} fill")
            _number(layer.get("opacity"), 0, 1, f"layer {index} opacity")
            if layer.get("blend_mode") not in BLENDS:
                raise CoverSpecError(f"layer {index} has invalid blend_mode")
            if not str(layer.get("purpose", "")).strip():
                raise CoverSpecError(f"{kind} layer requires compositional purpose")
        elif kind == "shape":
            if set(layer) - SHAPE_KEYS:
                raise CoverSpecError(f"layer {index} has unknown keys")
            if layer.get("shape") not in {"rect", "ellipse"}:
                raise CoverSpecError(f"layer {index} has invalid shape")
            _box(layer.get("box"), f"layer {index} box")
            _validate_fill(layer.get("fill"), f"layer {index} fill")
            _number(layer.get("opacity"), 0, 1, f"layer {index} opacity")
            _number(layer.get("rotation"), -180, 180, f"layer {index} rotation")
            _number(layer.get("stroke_width", 0), 0, 40, f"layer {index} stroke_width")
            if "stroke" in layer:
                _colour(layer["stroke"], f"layer {index} stroke")
            if layer.get("blend_mode") not in BLENDS or not str(layer.get("purpose", "")).strip():
                raise CoverSpecError(f"layer {index} shape requires valid blend_mode and purpose")
        elif kind == "line":
            if set(layer) - LINE_KEYS:
                raise CoverSpecError(f"layer {index} has unknown keys")
            _point(layer.get("start"), f"layer {index} start")
            _point(layer.get("end"), f"layer {index} end")
            _colour(layer.get("colour"), f"layer {index} colour")
            _number(layer.get("width"), 1, 40, f"layer {index} width")
            _number(layer.get("opacity"), 0, 1, f"layer {index} opacity")
            if not str(layer.get("purpose", "")).strip():
                raise CoverSpecError("line layer requires compositional purpose")
        else:
            raise CoverSpecError(f"unknown layer kind: {kind}")
    title_layers = sorted(
        (layer for layer in layers if layer.get("kind") == "text" and layer.get("role") == "title"),
        key=lambda layer: layer["title_order"],
    )
    if _tokens(" ".join(layer["text"] for layer in title_layers)) != _tokens(metadata["title"]):
        raise CoverSpecError("title layers must reproduce canonical title")
    for role in ("subtitle", "author", "label"):
        displayed = " ".join(layer["text"] for layer in layers if layer.get("kind") == "text" and layer.get("role") == role)
        if _tokens(displayed) != _tokens(metadata[role]):
            raise CoverSpecError(f"{role} layers must reproduce canonical metadata")
    return ValidatedCoverSpec(
        path=spec_path,
        data=payload,
        metadata={key: str(value) for key, value in metadata.items()},
        dimensions=(WIDTH, HEIGHT),
        art_path=art_path,
        spec_sha256=_canonical_digest(payload),
        art_sha256=hashlib.sha256(art_path.read_bytes()).hexdigest(),
        font_manifest=manifest,
        fonts=fonts,
        warnings=tuple(warnings),
    )
```

During implementation, factor repeated key-set checks into small helpers only if it makes the validator easier to audit; preserve every error string asserted above.

- [ ] **Step 5: Run the validator tests and contract parse**

```bash
/usr/local/bin/python3 -m unittest tests.test_cover_spec tests.test_cover_fonts -v
/usr/local/bin/python3 -m json.tool skill/schemas/cover-spec-v1.schema.json >/dev/null
```

Expected: all focused tests pass and the schema parses as JSON.

- [ ] **Step 6: Commit the specification boundary**

```bash
git add skill/schemas/cover-spec-v1.schema.json skill/scripts/cover_spec.py tests/test_cover_spec.py
git commit -m "feat: validate adaptive cover specifications"
```

---

### Task 3: Deterministic Renderer and `--spec` CLI

**Files:**
- Create: `skill/scripts/cover_renderer.py`
- Modify: `skill/scripts/make_cover.py`
- Modify: `tests/test_make_cover.py`
- Test: `tests/test_cover_renderer.py`

**Interfaces:**
- Consumes: `render_cover_spec(spec_path: Path, output_path: Path, font_manifest_path: Path = DEFAULT_MANIFEST) -> RenderResult`.
- Produces: RGB `cover.png`, `cover-thumbnail.png`, and deterministic `cover.render.json`.
- Preserves: the current legacy title/art/accent/tone/layout CLI when `--spec` is absent.

- [ ] **Step 1: Write failing renderer and CLI-separation tests**

Create `tests/test_cover_renderer.py` with a compact fixture builder. Render three variants by changing only validated data: plain full bleed, an integrated field, and per-run title offsets.

```python
from __future__ import annotations

import json
import shutil
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "skill" / "scripts"))
from cover_renderer import render_cover_spec

FONT_MANIFEST = Path(__file__).parents[1] / "skill" / "assets" / "fonts" / "manifest.json"


def base_spec() -> dict[str, object]:
    metadata = {"title": "Rodents in the Walls", "subtitle": "A Field Guide", "author": "Dan Fakkeldy", "label": "AUDIOBOOK"}
    def text(role: str, value: str, order: int, y: int, size: int, font_id: str, colour: str) -> dict[str, object]:
        layer: dict[str, object] = {
            "kind": "text", "role": role, "text": value, "font_id": font_id,
            "box": [96, y, 1408, size + 70], "size": size, "line_height": size + 10,
            "tracking": 0, "align": "left", "colour": colour, "opacity": 1,
            "rotation": 0, "baseline_shift": 0, "contrast_against": "#132238"
        }
        if role == "title":
            layer["title_order"] = order
        return layer
    return {
        "schema_version": 1,
        "candidate": {"id": "full-bleed", "direction_name": "Full Bleed"},
        "metadata": metadata,
        "canvas": {"width": 1600, "height": 2560, "background": "#132238", "safe_margin": 96},
        "art": {"path": "art.svg", "mode": "bleed", "anchor": "center", "box": [0, 0, 1600, 2560], "opacity": 1, "blend_mode": "normal"},
        "layers": [
            text("label", "AUDIOBOOK", 0, 120, 32, "geometric-sans", "#EF5735"),
            text("title", "RODENTS", 1, 240, 220, "display-condensed", "#EF5735"),
            text("title", "IN THE WALLS", 2, 500, 150, "editorial-serif", "#F6EDDA"),
            text("subtitle", "A Field Guide", 0, 2100, 46, "geometric-sans", "#F6EDDA"),
            text("author", "Dan Fakkeldy", 0, 2320, 38, "geometric-sans", "#F6EDDA")
        ]
    }


def write_spec(root: Path, payload: dict[str, object], name: str) -> Path:
    (root / "art.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 2560"><rect width="1600" height="2560" fill="#132238"/><circle cx="800" cy="1500" r="440" fill="#274664"/></svg>',
        encoding="utf-8"
    )
    path = root / f"{name}.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


@unittest.skipUnless(shutil.which("rsvg-convert") and shutil.which("magick"), "renderer tools required")
class CoverRendererTests(unittest.TestCase):
    def test_renders_full_bleed_band_and_expressive_runs(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            variants = []
            plain = base_spec()
            variants.append(("full", plain))
            band = base_spec()
            band["candidate"] = {"id": "band", "direction_name": "Integrated Band"}
            band["layers"].insert(0, {
                "kind": "field", "box": [0, 120, 1600, 650],
                "fill": {"kind": "solid", "colour": "#EF5735"},
                "opacity": 0.92, "blend_mode": "normal",
                "purpose": "carry the title using the plaster accent from the art"
            })
            variants.append(("band", band))
            expressive = base_spec()
            expressive["candidate"] = {"id": "expressive", "direction_name": "Shadow Branches"}
            expressive["layers"][1]["runs"] = [
                {"text": "R", "rotation": -4, "baseline_shift": 12, "colour": "#EF5735"},
                {"text": "O", "rotation": 2, "baseline_shift": -8, "colour": "#F6EDDA"},
                {"text": "DENTS", "rotation": -1, "baseline_shift": 0, "colour": "#EF5735"}
            ]
            variants.append(("expressive", expressive))
            for name, payload in variants:
                with self.subTest(name=name):
                    spec = write_spec(root, payload, name)
                    result = render_cover_spec(spec, root / f"{name}.png", FONT_MANIFEST)
                    header = result.output_path.read_bytes()[:29]
                    self.assertEqual(b"\x89PNG\r\n\x1a\n", header[:8])
                    self.assertEqual((1600, 2560), struct.unpack(">II", header[16:24]))
                    self.assertEqual(2, header[25])
                    self.assertTrue(result.thumbnail_path.is_file())
                    self.assertTrue(result.receipt_path.is_file())

    def test_same_inputs_produce_identical_cover_and_receipt_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            spec = write_spec(root, base_spec(), "stable")
            first = render_cover_spec(spec, root / "first.png", FONT_MANIFEST)
            second = render_cover_spec(spec, root / "second.png", FONT_MANIFEST)
            self.assertEqual(first.cover_sha256, second.cover_sha256)
            first_receipt = json.loads(first.receipt_path.read_text(encoding="utf-8"))
            second_receipt = json.loads(second.receipt_path.read_text(encoding="utf-8"))
            for receipt in (first_receipt, second_receipt):
                receipt["output"] = "cover.png"
                receipt["thumbnail"] = "cover-thumbnail.png"
            self.assertEqual(first_receipt, second_receipt)

    def test_invalid_spec_leaves_no_partial_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            payload = base_spec()
            payload["canvas"]["width"] = 1200
            spec = write_spec(root, payload, "invalid")
            output = root / "invalid.png"
            with self.assertRaisesRegex(ValueError, "1600x2560"):
                render_cover_spec(spec, output, FONT_MANIFEST)
            self.assertFalse(output.exists())
            self.assertFalse((root / "invalid-thumbnail.png").exists())
            self.assertFalse((root / "invalid.render.json").exists())

    def test_rejects_output_outside_the_specification_run_folder(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            spec = write_spec(root, base_spec(), "safe")
            escaped = root.parent / f"{root.name}-escaped.png"
            try:
                with self.assertRaisesRegex(ValueError, "output path escapes"):
                    render_cover_spec(spec, escaped, FONT_MANIFEST)
                self.assertFalse(escaped.exists())
            finally:
                escaped.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
```

Extend `tests/test_make_cover.py` with a CLI-level no-fallback test:

```python
def test_spec_mode_rejects_legacy_flags_instead_of_falling_back(self) -> None:
    with tempfile.TemporaryDirectory() as raw_dir, mock.patch.object(
        sys,
        "argv",
        [str(SCRIPT), "--spec", "candidate.json", "--title", "Wrong", "--out", str(Path(raw_dir) / "cover.png")],
    ), self.assertRaises(SystemExit) as raised:
        make_cover.main()
    self.assertEqual(2, raised.exception.code)
```

- [ ] **Step 2: Run focused tests and confirm the missing renderer failure**

```bash
/usr/local/bin/python3 -m unittest tests.test_cover_renderer tests.test_make_cover -v
```

Expected: import failure for `cover_renderer`; legacy tests remain discoverable.

- [ ] **Step 3: Implement SVG composition, normalization, and receipts**

Create `skill/scripts/cover_renderer.py`. Use deterministic layer IDs based on array position; embed exact font/art bytes as data URIs; rasterize full-size and thumbnail SVGs; normalize through ImageMagick to stripped RGB PNGs; write the receipt last.

```python
from __future__ import annotations

import base64
import hashlib
import json
import mimetypes
import os
import shutil
import struct
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from cover_fonts import DEFAULT_MANIFEST, FontRecord
from cover_spec import HEIGHT, WIDTH, ValidatedCoverSpec, load_cover_spec

RENDERER_VERSION = 1


class CoverRenderError(RuntimeError):
    pass


@dataclass(frozen=True)
class RenderResult:
    output_path: Path
    thumbnail_path: Path
    receipt_path: Path
    cover_sha256: str
    thumbnail_sha256: str


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    if path.suffix.lower() == ".svg":
        mime = "image/svg+xml"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def _font_css(fonts: dict[str, FontRecord]) -> str:
    rules = []
    for font_id in sorted(fonts):
        record = fonts[font_id]
        encoded = base64.b64encode(record.path.read_bytes()).decode("ascii")
        rules.append(
            f"@font-face{{font-family:'Cover-{font_id}';src:url(data:font/ttf;base64,{encoded}) format('truetype');}}"
        )
    return "".join(rules)


def _blend(value: str) -> str:
    return "normal" if value == "normal" else value


def _fill(fill: dict[str, Any], identity: str, definitions: list[str]) -> str:
    if fill["kind"] == "solid":
        return fill["colour"]
    x1, y1 = fill["start"]
    x2, y2 = fill["end"]
    stops = "".join(
        f'<stop offset="{stop["offset"] * 100:g}%" stop-color="{stop["colour"]}" stop-opacity="{stop["opacity"]:g}"/>'
        for stop in fill["stops"]
    )
    definitions.append(f'<linearGradient id="{identity}" x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" gradientUnits="userSpaceOnUse">{stops}</linearGradient>')
    return f"url(#{identity})"


def _art_markup(spec: ValidatedCoverSpec, definitions: list[str]) -> str:
    art = spec.data["art"]
    x, y, width, height = art["box"]
    anchor = {"center": "xMidYMid", "center-top": "xMidYMin", "center-bottom": "xMidYMax", "left": "xMinYMid", "right": "xMaxYMid"}[art["anchor"]]
    fit = "meet" if art["mode"] == "fit" else "slice"
    mask_attribute = ""
    if "mask" in art:
        mask = art["mask"]
        mx, my, mw, mh = mask["box"]
        if mask["shape"] == "ellipse":
            shape = f'<ellipse cx="{mx + mw / 2:g}" cy="{my + mh / 2:g}" rx="{mw / 2:g}" ry="{mh / 2:g}" fill="white"/>'
        else:
            shape = f'<rect x="{mx:g}" y="{my:g}" width="{mw:g}" height="{mh:g}" rx="{mask.get("radius", 0):g}" fill="white"/>'
        definitions.append(f'<mask id="art-mask">{shape}</mask>')
        mask_attribute = ' mask="url(#art-mask)"'
    return (
        f'<image href="{_data_uri(spec.art_path)}" x="{x:g}" y="{y:g}" width="{width:g}" height="{height:g}" '
        f'preserveAspectRatio="{anchor} {fit}" opacity="{art["opacity"]:g}" '
        f'style="mix-blend-mode:{_blend(art["blend_mode"])}"{mask_attribute}/>'
    )


def _text_markup(layer: dict[str, Any], index: int, definitions: list[str]) -> str:
    x, y, width, _height = layer["box"]
    anchor = {"left": "start", "center": "middle", "right": "end"}[layer["align"]]
    origin_x = {"left": x, "center": x + width / 2, "right": x + width}[layer["align"]]
    origin_y = y + layer["size"] + layer["baseline_shift"]
    style = [f"mix-blend-mode:{_blend(layer.get('blend_mode', 'normal'))}"]
    variations = layer.get("font_variation", {})
    if variations:
        axes = ",".join(f"'{name}' {value:g}" for name, value in sorted(variations.items()))
        style.append(f"font-variation-settings:{axes}")
    outline = layer.get("outline")
    stroke = ""
    if outline:
        stroke = f' stroke="{outline["colour"]}" stroke-width="{outline["width"]:g}" paint-order="stroke fill"'
    filter_attribute = ""
    shadow = layer.get("shadow")
    if shadow:
        identity = f"shadow-{index}"
        definitions.append(
            f'<filter id="{identity}" x="-30%" y="-30%" width="160%" height="160%">'
            f'<feDropShadow dx="{shadow["dx"]:g}" dy="{shadow["dy"]:g}" stdDeviation="{shadow["blur"] / 2:g}" '
            f'flood-color="{shadow["colour"]}" flood-opacity="{shadow["opacity"]:g}"/></filter>'
        )
        filter_attribute = f' filter="url(#{identity})"'
    transform = f"rotate({layer['rotation']:g} {origin_x:g} {origin_y:g})" if layer["rotation"] else ""
    common = (
        f'x="{origin_x:g}" y="{origin_y:g}" text-anchor="{anchor}" font-family="Cover-{layer["font_id"]}" '
        f'font-size="{layer["size"]:g}" letter-spacing="{layer["tracking"]:g}" fill="{layer["colour"]}" '
        f'fill-opacity="{layer["opacity"]:g}" style="{";".join(style)}"{stroke}{filter_attribute}'
    )
    if transform:
        common += f' transform="{transform}"'
    if layer.get("runs"):
        runs = []
        for run in layer["runs"]:
            attrs = [f'fill="{run.get("colour", layer["colour"])}"']
            attrs.append(f'font-size="{layer["size"] * run.get("size_scale", 1):g}"')
            attrs.append(f'letter-spacing="{run.get("tracking", layer["tracking"]):g}"')
            attrs.append(f'dx="{run.get("dx", 0):g}"')
            attrs.append(f'baseline-shift="{run.get("baseline_shift", 0):g}"')
            if run.get("rotation", 0):
                attrs.append(f'rotate="{run["rotation"]:g}"')
            runs.append(f'<tspan {" ".join(attrs)}>{escape(run["text"])}</tspan>')
        body = "".join(runs)
    else:
        lines = layer["text"].split("\n")
        body = "".join(
            f'<tspan x="{origin_x:g}" dy="{0 if line_index == 0 else layer["line_height"]:g}">{escape(line)}</tspan>'
            for line_index, line in enumerate(lines)
        )
    return f"<text {common}>{body}</text>"


def build_svg(spec: ValidatedCoverSpec) -> str:
    definitions: list[str] = []
    body = [f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{spec.data["canvas"]["background"]}"/>']
    body.append(_art_markup(spec, definitions))
    for index, layer in enumerate(spec.data["layers"], start=1):
        kind = layer["kind"]
        if kind in {"field", "scrim", "shape"}:
            x, y, width, height = layer["box"]
            fill = _fill(layer["fill"], f"fill-{index}", definitions)
            if kind == "shape" and layer["shape"] == "ellipse":
                element = f'<ellipse cx="{x + width / 2:g}" cy="{y + height / 2:g}" rx="{width / 2:g}" ry="{height / 2:g}"'
            else:
                element = f'<rect x="{x:g}" y="{y:g}" width="{width:g}" height="{height:g}" rx="{layer.get("radius", 0):g}"'
            stroke = f' stroke="{layer["stroke"]}" stroke-width="{layer.get("stroke_width", 0):g}"' if layer.get("stroke") else ""
            rotation = layer.get("rotation", 0)
            transform = f' transform="rotate({rotation:g} {x + width / 2:g} {y + height / 2:g})"' if rotation else ""
            body.append(f'{element} fill="{fill}" opacity="{layer["opacity"]:g}" style="mix-blend-mode:{_blend(layer["blend_mode"])}"{stroke}{transform}/>')
        elif kind == "line":
            body.append(f'<line x1="{layer["start"][0]:g}" y1="{layer["start"][1]:g}" x2="{layer["end"][0]:g}" y2="{layer["end"][1]:g}" stroke="{layer["colour"]}" stroke-width="{layer["width"]:g}" opacity="{layer["opacity"]:g}"/>')
        else:
            body.append(_text_markup(layer, index, definitions))
    defs = f'<defs><style>{_font_css(spec.fonts)}</style>{"".join(definitions)}</defs>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">{defs}{"".join(body)}</svg>'


def _render(svg_path: Path, destination: Path, width: int, height: int) -> None:
    raw = destination.with_name(f".{destination.name}.raw.png")
    normalized = destination.with_name(f".{destination.name}.normalized.png")
    try:
        if shutil.which("rsvg-convert"):
            command = ["rsvg-convert", "-w", str(width), "-h", str(height), str(svg_path), "-o", str(raw)]
        elif shutil.which("magick"):
            command = ["magick", "-background", "none", str(svg_path), "-resize", f"{width}x{height}!", str(raw)]
        else:
            raise CoverRenderError("no SVG rasterizer found")
        subprocess.run(command, check=True, capture_output=True)
        if not shutil.which("magick"):
            raise CoverRenderError("ImageMagick is required to normalize RGB PNG output")
        subprocess.run(["magick", str(raw), "-alpha", "off", "-colorspace", "sRGB", "-strip", f"PNG24:{normalized}"], check=True, capture_output=True)
        payload = normalized.read_bytes()
        if payload[:8] != b"\x89PNG\r\n\x1a\n" or struct.unpack(">II", payload[16:24]) != (width, height) or payload[25] != 2:
            raise CoverRenderError(f"renderer did not produce {width}x{height} RGB PNG")
        os.replace(normalized, destination)
    finally:
        raw.unlink(missing_ok=True)
        normalized.unlink(missing_ok=True)


def render_cover_spec(spec_path: Path, output_path: Path, font_manifest_path: Path = DEFAULT_MANIFEST) -> RenderResult:
    spec = load_cover_spec(Path(spec_path), Path(font_manifest_path))
    output = Path(output_path).resolve()
    try:
        output.relative_to(spec.path.parent)
    except ValueError as error:
        raise CoverRenderError("output path escapes specification run folder") from error
    thumbnail = output.with_name(f"{output.stem}-thumbnail.png")
    receipt = output.with_name(f"{output.stem}.render.json")
    for artifact in (output, thumbnail, receipt):
        artifact.unlink(missing_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    svg = build_svg(spec)
    with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False, encoding="utf-8") as handle:
        handle.write(svg)
        raw_svg = Path(handle.name)
    try:
        _render(raw_svg, output, WIDTH, HEIGHT)
        _render(raw_svg, thumbnail, 160, 256)
        payload = {
            "receipt_version": 1,
            "renderer_version": RENDERER_VERSION,
            "schema_version": 1,
            "candidate": spec.data["candidate"],
            "spec": spec.path.name,
            "spec_sha256": spec.spec_sha256,
            "source_art": spec.art_path.name,
            "source_art_sha256": spec.art_sha256,
            "font_manifest_version": spec.font_manifest.version,
            "font_manifest_sha256": spec.font_manifest.sha256,
            "fonts": {font_id: record.sha256 for font_id, record in sorted(spec.fonts.items())},
            "output": output.name,
            "output_sha256": _sha(output),
            "thumbnail": thumbnail.name,
            "thumbnail_sha256": _sha(thumbnail),
            "dimensions": [WIDTH, HEIGHT],
            "colour_mode": "RGB",
            "warnings": list(spec.warnings),
        }
        receipt.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return RenderResult(output, thumbnail, receipt, payload["output_sha256"], payload["thumbnail_sha256"])
    except Exception:
        for artifact in (output, thumbnail, receipt):
            artifact.unlink(missing_ok=True)
        raise
    finally:
        raw_svg.unlink(missing_ok=True)
```

- [ ] **Step 4: Wire spec mode into the existing CLI without changing legacy behavior**

In `skill/scripts/make_cover.py`, import the new renderer and change only argument parsing/dispatch:

```python
from pathlib import Path

from cover_renderer import CoverRenderError, render_cover_spec
from cover_spec import CoverSpecError
```

Replace `ap.add_argument("--title", required=True)` with these arguments:

```python
ap.add_argument("--spec", default="", help="Validated cover-specification JSON")
ap.add_argument("--title", default="")
```

Immediately after `a = ap.parse_args()`, dispatch spec mode before any legacy art/layout code:

```python
legacy_flags = {"--title", "--subtitle", "--author", "--label", "--seed", "--accent", "--art", "--tone", "--layout"}
provided = set(sys.argv[1:]) & legacy_flags
if a.spec:
    if provided:
        ap.error("--spec cannot be combined with legacy cover flags")
    try:
        result = render_cover_spec(Path(a.spec), Path(a.out))
    except (CoverSpecError, CoverRenderError, ValueError) as error:
        sys.stderr.write(f"COVER_SPEC_ERROR: {error}\n")
        return 2
    print("COVER:", result.output_path)
    print("THUMBNAIL:", result.thumbnail_path)
    print("RECEIPT:", result.receipt_path)
    return 0
if not a.title:
    ap.error("--title is required when --spec is not used")
```

Do not touch `build_svg`, `rasterize_raster_art_cover`, or legacy fallback behavior in this task.

- [ ] **Step 5: Run renderer, legacy, and full tests**

```bash
/usr/local/bin/python3 -m unittest tests.test_cover_renderer tests.test_make_cover -v
/usr/local/bin/python3 -m unittest discover -s tests -v
```

Expected: the three archetypes render as RGB PNGs, repeated renders match, invalid specs leave no outputs, all five pre-existing `test_make_cover` behaviors remain green, and the full suite passes.

- [ ] **Step 6: Commit the renderer**

```bash
git add skill/scripts/cover_renderer.py skill/scripts/make_cover.py tests/test_cover_renderer.py tests/test_make_cover.py
git commit -m "feat: render adaptive audiobook cover specs"
```

---

### Task 4: Explicit Selection and Package Identity Receipts

**Files:**
- Create: `skill/scripts/cover_receipts.py`
- Test: `tests/test_cover_receipts.py`

**Interfaces:**
- Produces: `create_selection(render_receipt_path, output_path, book_slug, edition_id, selection_source, selected_at, classification, permission_to_publish) -> SelectionReceipt`.
- Produces: `verify_package(selection_path, cover_path, epub_path=None, m4b_path=None, receipt_path=None) -> PackageVerification`.
- CLI subcommands: `select` and `verify`.

- [ ] **Step 1: Write failing selection and identity tests**

Create `tests/test_cover_receipts.py`. The fixture uses a real PNG and minimal OPF-declared EPUB; mock only the M4B extractor in this task.

```python
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from PIL import Image

sys.path.insert(0, str(Path(__file__).parents[1] / "skill" / "scripts"))
import cover_receipts


def make_cover(path: Path, colour: str = "#132238") -> Path:
    Image.new("RGB", (1600, 2560), colour).save(path)
    return path


def make_epub(path: Path, cover: bytes) -> Path:
    container = '<?xml version="1.0"?><container xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>'
    opf = '<package xmlns="http://www.idpf.org/2007/opf"><metadata/><manifest><item id="cover" href="cover.png" media-type="image/png" properties="cover-image"/></manifest><spine/></package>'
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        archive.writestr("META-INF/container.xml", container)
        archive.writestr("OEBPS/content.opf", opf)
        archive.writestr("OEBPS/cover.png", cover)
    return path


def make_render_receipt(root: Path, cover: Path) -> Path:
    payload = {
        "receipt_version": 1,
        "renderer_version": 1,
        "schema_version": 1,
        "candidate": {"id": "c1-full-bleed", "direction_name": "Full Bleed Display"},
        "spec": "cover-spec-1.json",
        "spec_sha256": "1" * 64,
        "source_art": "cover-source.png",
        "source_art_sha256": "2" * 64,
        "font_manifest_version": 1,
        "font_manifest_sha256": "3" * 64,
        "fonts": {"display-condensed": "4" * 64},
        "output": cover.name,
        "output_sha256": hashlib.sha256(cover.read_bytes()).hexdigest(),
        "thumbnail": "cover-thumbnail.png",
        "thumbnail_sha256": "5" * 64,
        "dimensions": [1600, 2560],
        "colour_mode": "RGB",
        "warnings": []
    }
    path = root / "cover.render.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


class CoverReceiptTests(unittest.TestCase):
    def test_creates_explicit_selection_from_verified_render(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            cover = make_cover(root / "cover.png")
            receipt = cover_receipts.create_selection(
                make_render_receipt(root, cover), root / "cover-selection.json",
                book_slug="rodents-in-the-walls", edition_id="corrected-v2",
                selection_source="explicit-user-choice", selected_at="2026-07-12T13:00:00-03:00",
                classification="public-safe", permission_to_publish="granted"
            )
            self.assertEqual(hashlib.sha256(cover.read_bytes()).hexdigest(), receipt.rendered_cover_sha256)
            self.assertEqual("c1-full-bleed", receipt.selected_candidate)
            self.assertTrue((root / "cover-selection.json").is_file())

    def test_rejects_automatic_or_tampered_selection(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            cover = make_cover(root / "cover.png")
            render = make_render_receipt(root, cover)
            with self.assertRaisesRegex(ValueError, "selection_source"):
                cover_receipts.create_selection(render, root / "selection.json", book_slug="rodents-in-the-walls", edition_id="v2", selection_source="first-valid", selected_at="2026-07-12T13:00:00-03:00", classification="public-safe", permission_to_publish="granted")
            cover.write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "rendered cover hash mismatch"):
                cover_receipts.create_selection(render, root / "selection.json", book_slug="rodents-in-the-walls", edition_id="v2", selection_source="explicit-user-choice", selected_at="2026-07-12T13:00:00-03:00", classification="public-safe", permission_to_publish="granted")

    def test_verifies_cover_epub_and_receipt_identity(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            cover = make_cover(root / "cover.png")
            selection_path = root / "cover-selection.json"
            cover_receipts.create_selection(make_render_receipt(root, cover), selection_path, book_slug="rodents-in-the-walls", edition_id="corrected-v2", selection_source="explicit-user-choice", selected_at="2026-07-12T13:00:00-03:00", classification="public-safe", permission_to_publish="granted")
            epub = make_epub(root / "book.epub", cover.read_bytes())
            result = cover_receipts.verify_package(selection_path, cover, epub_path=epub, receipt_path=selection_path)
            self.assertEqual(("standalone-bytes", "epub-cover-bytes", "receipt-identity"), result.checks)

    def test_rejects_stale_epub_and_normalizes_m4b_art(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            cover = make_cover(root / "cover.png")
            selection_path = root / "cover-selection.json"
            cover_receipts.create_selection(make_render_receipt(root, cover), selection_path, book_slug="rodents-in-the-walls", edition_id="corrected-v2", selection_source="explicit-user-choice", selected_at="2026-07-12T13:00:00-03:00", classification="public-safe", permission_to_publish="granted")
            stale = make_cover(root / "stale.png", "#FFFFFF")
            epub = make_epub(root / "stale.epub", stale.read_bytes())
            with self.assertRaisesRegex(ValueError, "EPUB cover bytes do not match"):
                cover_receipts.verify_package(selection_path, cover, epub_path=epub)
            m4b = root / "book.m4b"
            m4b.write_bytes(b"fixture")
            with mock.patch.object(cover_receipts, "normalized_image_sha256", return_value="a" * 64), mock.patch.object(cover_receipts, "normalized_m4b_art_sha256", return_value="a" * 64):
                result = cover_receipts.verify_package(selection_path, cover, m4b_path=m4b)
            self.assertIn("m4b-normalized-pixels", result.checks)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the focused test and confirm the missing-module failure**

```bash
/usr/local/bin/python3 -m unittest tests.test_cover_receipts -v
```

Expected: import failure for `cover_receipts`.

- [ ] **Step 3: Implement selection creation and package verification**

Create `skill/scripts/cover_receipts.py` with these immutable outputs and exact identity rules:

```python
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from refresh_epub_cover import discover_cover_member, discover_opf_member


@dataclass(frozen=True)
class SelectionReceipt:
    receipt_version: int
    book_slug: str
    edition_id: str
    selected_candidate: str
    direction_name: str
    schema_version: int
    spec_sha256: str
    source_art_sha256: str
    rendered_cover_sha256: str
    font_manifest_version: int
    font_manifest_sha256: str
    dimensions: tuple[int, int]
    colour_mode: str
    selected_at: str
    selection_source: str
    privacy: dict[str, str]


@dataclass(frozen=True)
class PackageVerification:
    book_slug: str
    edition_id: str
    rendered_cover_sha256: str
    checks: tuple[str, ...]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _read_json(path: Path) -> dict[str, object]:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"invalid receipt: {path}") from error


def _write_json(path: Path, payload: dict[str, object]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_selection(path: Path) -> SelectionReceipt:
    payload = _read_json(Path(path))
    if payload.get("receipt_version") != 1 or payload.get("selection_source") not in {"explicit-user-choice", "requested-mix"}:
        raise ValueError("invalid cover selection receipt")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", str(payload.get("book_slug", ""))) or not str(payload.get("edition_id", "")) or not str(payload.get("selected_candidate", "")):
        raise ValueError("invalid cover selection identity")
    for field in ("spec_sha256", "source_art_sha256", "rendered_cover_sha256", "font_manifest_sha256"):
        if not re.fullmatch(r"[0-9a-f]{64}", str(payload.get(field, ""))):
            raise ValueError(f"invalid selection hash: {field}")
    if payload.get("dimensions") != [1600, 2560] or payload.get("colour_mode") != "RGB":
        raise ValueError("selection cover must be 1600x2560 RGB")
    datetime.fromisoformat(str(payload["selected_at"]))
    privacy = payload.get("privacy")
    if not isinstance(privacy, dict) or set(privacy) != {"classification", "permission_to_publish"} or privacy.get("classification") not in {"public-safe", "private", "sensitive"} or privacy.get("permission_to_publish") not in {"granted", "denied", "not-requested"}:
        raise ValueError("invalid selection privacy classification")
    return SelectionReceipt(
        receipt_version=1,
        book_slug=str(payload["book_slug"]),
        edition_id=str(payload["edition_id"]),
        selected_candidate=str(payload["selected_candidate"]),
        direction_name=str(payload["direction_name"]),
        schema_version=int(payload["schema_version"]),
        spec_sha256=str(payload["spec_sha256"]),
        source_art_sha256=str(payload["source_art_sha256"]),
        rendered_cover_sha256=str(payload["rendered_cover_sha256"]),
        font_manifest_version=int(payload["font_manifest_version"]),
        font_manifest_sha256=str(payload["font_manifest_sha256"]),
        dimensions=tuple(payload["dimensions"]),
        colour_mode=str(payload["colour_mode"]),
        selected_at=str(payload["selected_at"]),
        selection_source=str(payload["selection_source"]),
        privacy={str(key): str(value) for key, value in privacy.items()},
    )


def create_selection(render_receipt_path: Path, output_path: Path, *, book_slug: str, edition_id: str, selection_source: str, selected_at: str, classification: str, permission_to_publish: str) -> SelectionReceipt:
    if selection_source not in {"explicit-user-choice", "requested-mix"}:
        raise ValueError("selection_source must be explicit-user-choice or requested-mix")
    datetime.fromisoformat(selected_at)
    if classification not in {"public-safe", "private", "sensitive"} or permission_to_publish not in {"granted", "denied", "not-requested"}:
        raise ValueError("invalid privacy selection")
    render_path = Path(render_receipt_path).resolve()
    render = _read_json(render_path)
    if render.get("receipt_version") != 1 or render.get("schema_version") != 1 or render.get("dimensions") != [1600, 2560] or render.get("colour_mode") != "RGB":
        raise ValueError("invalid render receipt contract")
    cover = render_path.parent / str(render["output"])
    if sha256_file(cover) != render.get("output_sha256"):
        raise ValueError("rendered cover hash mismatch")
    receipt = SelectionReceipt(
        receipt_version=1,
        book_slug=book_slug,
        edition_id=edition_id,
        selected_candidate=str(render["candidate"]["id"]),
        direction_name=str(render["candidate"]["direction_name"]),
        schema_version=int(render["schema_version"]),
        spec_sha256=str(render["spec_sha256"]),
        source_art_sha256=str(render["source_art_sha256"]),
        rendered_cover_sha256=str(render["output_sha256"]),
        font_manifest_version=int(render["font_manifest_version"]),
        font_manifest_sha256=str(render["font_manifest_sha256"]),
        dimensions=tuple(render["dimensions"]),
        colour_mode=str(render["colour_mode"]),
        selected_at=selected_at,
        selection_source=selection_source,
        privacy={"classification": classification, "permission_to_publish": permission_to_publish},
    )
    _write_json(Path(output_path), asdict(receipt))
    return receipt


def normalized_image_sha256(path: Path) -> str:
    if not shutil.which("magick"):
        raise ValueError("ImageMagick is required for normalized artwork comparison")
    result = subprocess.run(["magick", str(path), "-auto-orient", "-alpha", "off", "-colorspace", "sRGB", "-depth", "8", "RGB:-"], check=True, capture_output=True)
    return hashlib.sha256(result.stdout).hexdigest()


def normalized_m4b_art_sha256(path: Path) -> str:
    if not shutil.which("ffmpeg"):
        raise ValueError("ffmpeg is required for M4B artwork verification")
    with tempfile.TemporaryDirectory(prefix="cover-art-") as raw:
        extracted = Path(raw) / "art.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-map", "0:v:0", "-frames:v", "1", str(extracted)], check=True, capture_output=True)
        return normalized_image_sha256(extracted)


def verify_package(selection_path: Path, cover_path: Path, *, epub_path: Path | None = None, m4b_path: Path | None = None, receipt_path: Path | None = None) -> PackageVerification:
    selected = load_selection(selection_path)
    cover = Path(cover_path)
    if sha256_file(cover) != selected.rendered_cover_sha256:
        raise ValueError("standalone cover bytes do not match selection")
    checks = ["standalone-bytes"]
    if epub_path is not None:
        with zipfile.ZipFile(epub_path) as archive:
            opf = discover_opf_member(archive)
            member = discover_cover_member(archive, opf)
            if archive.read(member) != cover.read_bytes():
                raise ValueError("EPUB cover bytes do not match standalone cover")
        checks.append("epub-cover-bytes")
    if m4b_path is not None:
        if normalized_m4b_art_sha256(Path(m4b_path)) != normalized_image_sha256(cover):
            raise ValueError("M4B artwork pixels do not match selected cover")
        checks.append("m4b-normalized-pixels")
    if receipt_path is not None:
        delivered = load_selection(Path(receipt_path))
        if asdict(delivered) != asdict(selected):
            raise ValueError("destination selection receipt does not match source")
        checks.append("receipt-identity")
    return PackageVerification(selected.book_slug, selected.edition_id, selected.rendered_cover_sha256, tuple(checks))


def main() -> int:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    select = commands.add_parser("select")
    select.add_argument("--render-receipt", required=True, type=Path)
    select.add_argument("--out", required=True, type=Path)
    select.add_argument("--book-slug", required=True)
    select.add_argument("--edition-id", required=True)
    select.add_argument("--selection-source", required=True, choices=("explicit-user-choice", "requested-mix"))
    select.add_argument("--selected-at", required=True)
    select.add_argument("--classification", required=True, choices=("public-safe", "private", "sensitive"))
    select.add_argument("--permission-to-publish", required=True, choices=("granted", "denied", "not-requested"))
    verify = commands.add_parser("verify")
    verify.add_argument("--selection", required=True, type=Path)
    verify.add_argument("--cover", required=True, type=Path)
    verify.add_argument("--epub", type=Path)
    verify.add_argument("--m4b", type=Path)
    verify.add_argument("--receipt", type=Path)
    arguments = parser.parse_args()
    if arguments.command == "select":
        result = create_selection(
            arguments.render_receipt,
            arguments.out,
            book_slug=arguments.book_slug,
            edition_id=arguments.edition_id,
            selection_source=arguments.selection_source,
            selected_at=arguments.selected_at,
            classification=arguments.classification,
            permission_to_publish=arguments.permission_to_publish,
        )
    else:
        result = verify_package(
            arguments.selection,
            arguments.cover,
            epub_path=arguments.epub,
            m4b_path=arguments.m4b,
            receipt_path=arguments.receipt,
        )
    print(json.dumps(asdict(result), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run focused and renderer tests**

```bash
/usr/local/bin/python3 -m unittest tests.test_cover_receipts tests.test_cover_renderer -v
```

Expected: all selection/package tests pass and renderer receipts remain compatible.

- [ ] **Step 5: Commit the receipt boundary**

```bash
git add skill/scripts/cover_receipts.py tests/test_cover_receipts.py
git commit -m "feat: add cover selection and package receipts"
```

---

### Task 5: Lossless M4B Artwork Replacement

**Files:**
- Create: `skill/scripts/replace_m4b_cover.py`
- Test: `tests/test_replace_m4b_cover.py`

**Interfaces:**
- Consumes: `replace_m4b_cover(source: Path, cover: Path, output: Path) -> M4BCoverReplacement`.
- Produces: a validated M4B with one replacement artwork item and unchanged audio packets, stream codec/type sequence, duration, chapter boundaries/titles, and text metadata.

- [ ] **Step 1: Write a failing real-tool integration test**

The test creates a 0.25-second AAC `.m4b`, adds initial art, replaces it, and compares the immutable media signature:

```python
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parents[1] / "skill" / "scripts"))
from cover_receipts import normalized_image_sha256, normalized_m4b_art_sha256
from replace_m4b_cover import media_signature, replace_m4b_cover


@unittest.skipUnless(all(shutil.which(tool) for tool in ("AtomicParsley", "ffmpeg", "ffprobe", "magick")), "media tools required")
class ReplaceM4BCoverTests(unittest.TestCase):
    def test_replaces_only_artwork_and_preserves_media_signature(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            old_art = root / "old.png"
            new_art = root / "new.png"
            Image.new("RGB", (1600, 2560), "#132238").save(old_art)
            Image.new("RGB", (1600, 2560), "#EF5735").save(new_art)
            audio = root / "audio.m4b"
            tagged = root / "tagged.m4b"
            output = root / "output.m4b"
            subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", "0.25", "-c:a", "aac", "-metadata", "title=Fixture", str(audio)], check=True)
            subprocess.run(["AtomicParsley", str(audio), "--artwork", str(old_art), "--output", str(tagged)], check=True, capture_output=True)
            before = media_signature(tagged)
            result = replace_m4b_cover(tagged, new_art, output)
            self.assertEqual(before, media_signature(output))
            self.assertEqual(before.audio_packet_sha256, result.audio_packet_sha256)
            self.assertEqual(normalized_image_sha256(new_art), normalized_m4b_art_sha256(output))

    def test_failure_does_not_replace_existing_output(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            output = root / "output.m4b"
            output.write_bytes(b"keep-me")
            with self.assertRaisesRegex(ValueError, "AtomicParsley"):
                replace_m4b_cover(root / "missing.m4b", root / "missing.png", output)
            self.assertEqual(b"keep-me", output.read_bytes())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test and confirm the missing-module failure**

```bash
/usr/local/bin/python3 -m unittest tests.test_replace_m4b_cover -v
```

Expected: import failure for `replace_m4b_cover`.

- [ ] **Step 3: Implement AtomicParsley replacement with immutable-media checks**

Create `skill/scripts/replace_m4b_cover.py`. Do not use the naive ffmpeg remux path: on the real Rodents file it fails against the QuickTime chapter `bin_data` stream. AtomicParsley preserves the audio packet hash and the AAC/data/PNG stream structure.

```python
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

from cover_receipts import normalized_image_sha256, normalized_m4b_art_sha256


@dataclass(frozen=True)
class MediaSignature:
    audio_packet_sha256: str
    streams: tuple[tuple[str, str], ...]
    duration: str
    chapters: tuple[tuple[str, str, str], ...]
    format_tags: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class M4BCoverReplacement:
    output: str
    artwork_sha256: str
    normalized_artwork_sha256: str
    audio_packet_sha256: str
    chapter_count: int


def _run(command: list[str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(command, check=True, capture_output=True)


def media_signature(path: Path) -> MediaSignature:
    if not shutil.which("ffprobe") or not shutil.which("ffmpeg"):
        raise ValueError("ffmpeg and ffprobe are required")
    probe = _run(["ffprobe", "-v", "error", "-show_streams", "-show_chapters", "-show_format", "-of", "json", str(path)])
    payload = json.loads(probe.stdout)
    packet_stream = _run(["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:a:0", "-c", "copy", "-f", "data", "-"])
    chapters = tuple((str(chapter.get("start_time", "")), str(chapter.get("end_time", "")), str(chapter.get("tags", {}).get("title", ""))) for chapter in payload.get("chapters", []))
    streams = tuple((str(stream.get("codec_type", "")), str(stream.get("codec_name", ""))) for stream in payload.get("streams", []))
    tags = tuple(sorted((str(key), str(value)) for key, value in payload.get("format", {}).get("tags", {}).items()))
    return MediaSignature(hashlib.sha256(packet_stream.stdout).hexdigest(), streams, str(payload.get("format", {}).get("duration", "")), chapters, tags)


def replace_m4b_cover(source: Path, cover: Path, output: Path) -> M4BCoverReplacement:
    source = Path(source)
    cover = Path(cover)
    output = Path(output)
    if not shutil.which("AtomicParsley"):
        raise ValueError("AtomicParsley is required")
    if not source.is_file() or not cover.is_file():
        raise ValueError("AtomicParsley source M4B and cover must exist")
    before = media_signature(source)
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, raw = tempfile.mkstemp(prefix=f".{output.name}.", suffix=".m4b", dir=output.parent)
    os.close(descriptor)
    temporary = Path(raw)
    temporary.unlink()
    try:
        _run(["AtomicParsley", str(source), "--artwork", "REMOVE_ALL", "--artwork", str(cover), "--output", str(temporary)])
        after = media_signature(temporary)
        if after != before:
            raise ValueError("M4B media signature changed while replacing artwork")
        normalized = normalized_image_sha256(cover)
        if normalized_m4b_art_sha256(temporary) != normalized:
            raise ValueError("M4B replacement artwork does not match source cover")
        os.replace(temporary, output)
        return M4BCoverReplacement(str(output), hashlib.sha256(cover.read_bytes()).hexdigest(), normalized, after.audio_packet_sha256, len(after.chapters))
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--m4b", required=True, type=Path)
    parser.add_argument("--cover", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    arguments = parser.parse_args()
    print(json.dumps(asdict(replace_m4b_cover(arguments.m4b, arguments.cover, arguments.out)), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run focused test and one read-only real-file signature probe**

```bash
/usr/local/bin/python3 -m unittest tests.test_replace_m4b_cover -v
/usr/local/bin/python3 - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, str(Path('skill/scripts').resolve()))
from replace_m4b_cover import media_signature
signature = media_signature(Path('books/rodents-in-the-walls/rodents-in-the-walls.m4b'))
assert signature.streams == (("audio", "aac"), ("data", "bin_data"), ("video", "png"))
assert len(signature.chapters) == 9
print("RODENTS_M4B_SIGNATURE_OK", signature.audio_packet_sha256)
PY
```

Expected: integration tests pass; the real book reports three preserved stream types and nine chapters without changing the file.

- [ ] **Step 5: Commit the M4B artwork tool**

```bash
git add skill/scripts/replace_m4b_cover.py tests/test_replace_m4b_cover.py
git commit -m "feat: replace M4B artwork without changing audio"
```

---

### Task 6: Guarded Delivery and EPUB Build Integration

**Files:**
- Create: `skill/scripts/sync_selected_cover.py`
- Create: `tests/test_sync_selected_cover.py`
- Modify: `skill/scripts/build_book.py`
- Create: `tests/test_build_book_cover_receipt.py`

**Interfaces:**
- Produces: `classify_destination(source: SelectionReceipt, destination: SelectionReceipt | None, intent: str, destination_has_artifacts: bool = False) -> str` with `new`, `reuse`, `supersede`, `supersede-unreceipted`, or a hard conflict.
- Produces: `sync_selected_cover(selection_path: Path, cover_path: Path, epub_path: Path, m4b_path: Path, destination: Path, *, intent: str, apply: bool, checksum_manifest: Path | None = None, public_destination: bool = False, fail_after: int | None = None) -> SyncResult` with dry-run/apply behavior and rollback.
- Extends: `build(chapters_dir, out_dir, title, author, subtitle, slug, lang="en", cover=None, contributor="", cover_selection=None)` and CLI `--cover-selection`.

- [ ] **Step 1: Write failing destination classification and rollback tests**

Create `tests/test_sync_selected_cover.py`. Use mocks around `verify_package`; the filesystem assertions exercise the real transaction and checksum rewrite:

```python
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from dataclasses import asdict, replace
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parents[1] / "skill" / "scripts"))
from cover_receipts import SelectionReceipt
import sync_selected_cover


def receipt(selected_at: str = "2026-07-12T13:00:00-03:00", cover_hash: str = "a" * 64) -> SelectionReceipt:
    return SelectionReceipt(1, "rodents-in-the-walls", "corrected-v2", "c1", "Full Bleed", 1, "1" * 64, "2" * 64, cover_hash, 1, "3" * 64, (1600, 2560), "RGB", selected_at, "explicit-user-choice", {"classification": "public-safe", "permission_to_publish": "granted"})


def write_receipt(path: Path, value: SelectionReceipt) -> Path:
    path.write_text(json.dumps(asdict(value)), encoding="utf-8")
    return path


class SyncSelectedCoverTests(unittest.TestCase):
    def test_classifies_new_reuse_supersede_and_conflict(self) -> None:
        source = receipt()
        self.assertEqual("new", sync_selected_cover.classify_destination(source, None, "reuse"))
        self.assertEqual("supersede-unreceipted", sync_selected_cover.classify_destination(source, None, "supersede", destination_has_artifacts=True))
        with self.assertRaisesRegex(ValueError, "unreceipted cover artifacts"):
            sync_selected_cover.classify_destination(source, None, "reuse", destination_has_artifacts=True)
        self.assertEqual("reuse", sync_selected_cover.classify_destination(source, source, "reuse"))
        older = receipt("2026-07-11T13:00:00-03:00", "b" * 64)
        self.assertEqual("supersede", sync_selected_cover.classify_destination(source, older, "supersede"))
        with self.assertRaisesRegex(ValueError, "cover receipt conflict"):
            sync_selected_cover.classify_destination(source, older, "reuse")
        newer = receipt("2026-07-13T13:00:00-03:00", "b" * 64)
        with self.assertRaisesRegex(ValueError, "not newer"):
            sync_selected_cover.classify_destination(source, newer, "supersede")

    def test_public_destination_requires_public_safe_permission(self) -> None:
        private = replace(receipt(), privacy={"classification": "private", "permission_to_publish": "not-requested"})
        with self.assertRaisesRegex(ValueError, "public-safe and permissioned"):
            sync_selected_cover.require_public_permission(private)

    def test_apply_updates_only_cover_artifacts_receipt_and_existing_checksums(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = root / "source"
            destination = root / "destination"
            source.mkdir(); destination.mkdir()
            cover = source / "cover.png"; cover.write_bytes(b"new-cover")
            epub = source / "book.epub"; epub.write_bytes(b"new-epub")
            m4b = source / "book.m4b"; m4b.write_bytes(b"new-m4b")
            selection = write_receipt(source / "cover-selection.json", receipt(cover_hash=hashlib.sha256(cover.read_bytes()).hexdigest()))
            (destination / "cover.png").write_bytes(b"old-cover")
            (destination / "book.epub").write_bytes(b"old-epub")
            (destination / "book.m4b").write_bytes(b"old-m4b")
            write_receipt(destination / "cover-selection.json", receipt("2026-07-11T13:00:00-03:00", "b" * 64))
            untouched = destination / "alignment.json"; untouched.write_bytes(b"untouched")
            checksums = destination / "SHA256SUMS"
            checksums.write_text(f"{'0' * 64}  cover.png\n{'1' * 64}  alignment.json\n", encoding="utf-8")
            with mock.patch.object(sync_selected_cover, "verify_package"):
                result = sync_selected_cover.sync_selected_cover(selection, cover, epub, m4b, destination, intent="supersede", apply=True, checksum_manifest=checksums, public_destination=False)
            self.assertEqual("supersede", result.decision)
            self.assertEqual(b"new-cover", (destination / "cover.png").read_bytes())
            self.assertEqual(b"untouched", untouched.read_bytes())
            self.assertIn(hashlib.sha256(b"new-cover").hexdigest(), checksums.read_text(encoding="utf-8"))
            self.assertIn(f"{'1' * 64}  alignment.json", checksums.read_text(encoding="utf-8"))

    def test_failure_rolls_back_every_touched_file(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = root / "source"; destination = root / "destination"
            source.mkdir(); destination.mkdir()
            cover = source / "cover.png"; epub = source / "book.epub"; m4b = source / "book.m4b"
            cover.write_bytes(b"new-cover"); epub.write_bytes(b"new-epub"); m4b.write_bytes(b"new-m4b")
            selection = write_receipt(source / "cover-selection.json", receipt(cover_hash=hashlib.sha256(cover.read_bytes()).hexdigest()))
            originals = {"cover.png": b"old-cover", "book.epub": b"old-epub", "book.m4b": b"old-m4b"}
            for name, payload in originals.items():
                (destination / name).write_bytes(payload)
            with mock.patch.object(sync_selected_cover, "verify_package"), self.assertRaisesRegex(RuntimeError, "injected sync failure"):
                sync_selected_cover.sync_selected_cover(selection, cover, epub, m4b, destination, intent="supersede", apply=True, fail_after=2)
            for name, payload in originals.items():
                self.assertEqual(payload, (destination / name).read_bytes())
            self.assertFalse((destination / "cover-selection.json").exists())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the sync test and confirm the missing-module failure**

```bash
/usr/local/bin/python3 -m unittest tests.test_sync_selected_cover -v
```

Expected: import failure for `sync_selected_cover`.

- [ ] **Step 3: Implement destination classification and a rollback transaction**

Create `skill/scripts/sync_selected_cover.py`. Receipt comparison is exact for reuse; supersession requires the same book/edition and a strictly newer explicit selection.

```python
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from cover_receipts import SelectionReceipt, load_selection, verify_package


@dataclass(frozen=True)
class SyncResult:
    decision: str
    destination: str
    applied: bool
    files: tuple[str, ...]


def classify_destination(source: SelectionReceipt, destination: SelectionReceipt | None, intent: str, destination_has_artifacts: bool = False) -> str:
    if intent not in {"reuse", "supersede"}:
        raise ValueError("intent must be reuse or supersede")
    if destination is None:
        if destination_has_artifacts and intent != "supersede":
            raise ValueError("cover receipt conflict: destination has unreceipted cover artifacts")
        if destination_has_artifacts:
            return "supersede-unreceipted"
        return "new"
    if asdict(source) == asdict(destination):
        return "reuse"
    if source.book_slug != destination.book_slug or source.edition_id != destination.edition_id:
        raise ValueError("cover receipt conflict: book or edition differs")
    if intent != "supersede":
        raise ValueError("cover receipt conflict: explicit supersede intent required")
    if source.selection_source not in {"explicit-user-choice", "requested-mix"}:
        raise ValueError("cover receipt conflict: source selection is not explicit")
    if datetime.fromisoformat(source.selected_at) <= datetime.fromisoformat(destination.selected_at):
        raise ValueError("cover receipt conflict: source selection is not newer")
    return "supersede"


def require_public_permission(selection: SelectionReceipt) -> None:
    if selection.privacy != {"classification": "public-safe", "permission_to_publish": "granted"}:
        raise ValueError("public destination requires public-safe and permissioned selection")


def _update_checksums(path: Path, replacements: dict[str, Path]) -> None:
    rows: list[tuple[str, str]] = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            digest, name = line.split(None, 1)
            rows.append((digest, name.strip()))
    known = {name for _, name in rows}
    updated = []
    for digest, name in rows:
        source = replacements.get(name)
        updated.append((hashlib.sha256(source.read_bytes()).hexdigest(), name) if source else (digest, name))
    for name in sorted(set(replacements) - known):
        updated.append((hashlib.sha256(replacements[name].read_bytes()).hexdigest(), name))
    path.write_text("".join(f"{digest}  {name}\n" for digest, name in updated), encoding="utf-8")


def sync_selected_cover(selection_path: Path, cover_path: Path, epub_path: Path, m4b_path: Path, destination: Path, *, intent: str, apply: bool, checksum_manifest: Path | None = None, public_destination: bool = False, fail_after: int | None = None) -> SyncResult:
    selection_path = Path(selection_path)
    cover_path = Path(cover_path)
    epub_path = Path(epub_path)
    m4b_path = Path(m4b_path)
    destination = Path(destination)
    source = load_selection(selection_path)
    verify_package(selection_path, cover_path, epub_path=epub_path, m4b_path=m4b_path, receipt_path=selection_path)
    if public_destination:
        require_public_permission(source)
    destination_receipt_path = destination / "cover-selection.json"
    destination_receipt = load_selection(destination_receipt_path) if destination_receipt_path.exists() else None
    files = ("cover.png", epub_path.name, m4b_path.name, "cover-selection.json")
    destination_has_artifacts = any((destination / name).exists() for name in files[:-1])
    decision = classify_destination(source, destination_receipt, intent, destination_has_artifacts)
    if not apply:
        return SyncResult(decision, str(destination), False, files)
    destination.mkdir(parents=True, exist_ok=True)
    sources = {
        "cover.png": cover_path,
        epub_path.name: epub_path,
        m4b_path.name: m4b_path,
        "cover-selection.json": selection_path,
    }
    checksum_path = Path(checksum_manifest) if checksum_manifest is not None else None
    with tempfile.TemporaryDirectory(prefix="cover-sync-", dir=destination.parent) as raw_backup:
        backup = Path(raw_backup)
        existed: set[str] = set()
        touched: list[str] = []
        try:
            for name in files:
                target = destination / name
                if target.exists():
                    existed.add(name)
                    shutil.copy2(target, backup / name)
                incoming = destination / f".{name}.incoming"
                shutil.copy2(sources[name], incoming)
                os.replace(incoming, target)
                touched.append(name)
                if fail_after is not None and len(touched) == fail_after:
                    raise RuntimeError("injected sync failure")
            if checksum_path is not None:
                checksum_backup = backup / "SHA256SUMS"
                if checksum_path.exists():
                    shutil.copy2(checksum_path, checksum_backup)
                    existed.add("SHA256SUMS")
                _update_checksums(checksum_path, sources)
                touched.append("SHA256SUMS")
            verify_package(destination / "cover-selection.json", destination / "cover.png", epub_path=destination / epub_path.name, m4b_path=destination / m4b_path.name, receipt_path=destination / "cover-selection.json")
        except Exception:
            for name in reversed(touched):
                target = checksum_path if name == "SHA256SUMS" else destination / name
                backup_file = backup / name
                if name in existed:
                    shutil.copy2(backup_file, target)
                else:
                    target.unlink(missing_ok=True)
            for incoming in destination.glob(".*.incoming"):
                incoming.unlink(missing_ok=True)
            raise
    return SyncResult(decision, str(destination), True, files)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selection", required=True, type=Path)
    parser.add_argument("--cover", required=True, type=Path)
    parser.add_argument("--epub", required=True, type=Path)
    parser.add_argument("--m4b", required=True, type=Path)
    parser.add_argument("--destination", required=True, type=Path)
    parser.add_argument("--intent", required=True, choices=("reuse", "supersede"))
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--checksum-manifest", type=Path)
    parser.add_argument("--public-destination", action="store_true")
    arguments = parser.parse_args()
    result = sync_selected_cover(
        arguments.selection,
        arguments.cover,
        arguments.epub,
        arguments.m4b,
        arguments.destination,
        intent=arguments.intent,
        apply=arguments.apply,
        checksum_manifest=arguments.checksum_manifest,
        public_destination=arguments.public_destination,
    )
    print(json.dumps(asdict(result), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Without `--apply`, the command remains a read-only classification/verification operation.

- [ ] **Step 4: Write failing EPUB-build receipt tests**

Create `tests/test_build_book_cover_receipt.py`:

```python
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parents[1] / "skill" / "scripts"))
import build_book


def selection(path: Path, cover: Path, slug: str = "fixture-book") -> Path:
    payload = {
        "receipt_version": 1, "book_slug": slug, "edition_id": "v1",
        "selected_candidate": "c1", "direction_name": "Fixture", "schema_version": 1,
        "spec_sha256": "1" * 64, "source_art_sha256": "2" * 64,
        "rendered_cover_sha256": hashlib.sha256(cover.read_bytes()).hexdigest(),
        "font_manifest_version": 1, "font_manifest_sha256": "3" * 64,
        "dimensions": [1600, 2560], "colour_mode": "RGB",
        "selected_at": "2026-07-12T13:00:00-03:00",
        "selection_source": "explicit-user-choice",
        "privacy": {"classification": "public-safe", "permission_to_publish": "granted"}
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


class BuildBookCoverReceiptTests(unittest.TestCase):
    def test_build_verifies_receipt_before_and_after_embedding(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); chapters = root / "chapters"; out = root / "dist"
            chapters.mkdir(); (chapters / "ch01.md").write_text("# One\n\nA complete chapter.", encoding="utf-8")
            cover = root / "cover.png"; Image.new("RGB", (1600, 2560), "#132238").save(cover)
            receipt = selection(root / "cover-selection.json", cover)
            build_book.build(chapters, out, "Fixture", "Dan Fakkeldy", "", "fixture-book", cover=cover, cover_selection=receipt)
            with zipfile.ZipFile(out / "fixture-book.epub") as archive:
                self.assertEqual(cover.read_bytes(), archive.read("OEBPS/cover.png"))

    def test_build_rejects_stale_cover_or_wrong_slug(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); chapters = root / "chapters"; out = root / "dist"
            chapters.mkdir(); (chapters / "ch01.md").write_text("# One\n\nA complete chapter.", encoding="utf-8")
            cover = root / "cover.png"; Image.new("RGB", (1600, 2560), "#132238").save(cover)
            receipt = selection(root / "cover-selection.json", cover, slug="other-book")
            with self.assertRaisesRegex(ValueError, "selection book_slug"):
                build_book.build(chapters, out, "Fixture", "Dan Fakkeldy", "", "fixture-book", cover=cover, cover_selection=receipt)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 5: Extend `build_book.py` with optional receipt enforcement**

Add these imports:

```python
from pathlib import Path

from cover_receipts import load_selection, sha256_file, verify_package
```

Add `cover_selection=None` as the final `build()` parameter so existing positional callers remain compatible. Before reading `cover_bytes`, add:

```python
selection_path = Path(cover_selection) if cover_selection else None
if selection_path is not None:
    if not cover or not os.path.exists(cover):
        raise ValueError("--cover-selection requires an existing --cover")
    selected = load_selection(selection_path)
    if selected.book_slug != slug:
        raise ValueError(f"selection book_slug {selected.book_slug} does not match build slug {slug}")
    if sha256_file(Path(cover)) != selected.rendered_cover_sha256:
        raise ValueError("selected cover hash does not match --cover")
```

Immediately after closing the EPUB zip, add:

```python
if selection_path is not None:
    verify_package(selection_path, Path(cover), epub_path=Path(epub_path))
```

Add the CLI option and pass it as the final argument:

```python
ap.add_argument("--cover-selection", default=None, help="Selection receipt that must match --cover and the built EPUB")
```

```python
build(a.chapters_dir, a.out_dir, a.title, a.author, a.subtitle, a.slug, a.lang, a.cover, a.contributor, a.cover_selection)
```

- [ ] **Step 6: Run package-boundary and full tests**

```bash
/usr/local/bin/python3 -m unittest tests.test_sync_selected_cover tests.test_build_book_cover_receipt -v
/usr/local/bin/python3 -m unittest discover -s tests -v
```

Expected: classification, rollback, privacy, checksum, and build receipt tests pass; all earlier tests remain green.

- [ ] **Step 7: Commit guarded package propagation**

```bash
git add skill/scripts/sync_selected_cover.py skill/scripts/build_book.py tests/test_sync_selected_cover.py tests/test_build_book_cover_receipt.py
git commit -m "feat: guard selected covers through package delivery"
```

---

### Task 7: Make the Adaptive Path the Skill Default

**Files:**
- Modify: `skill/references/cover-art.md`
- Modify: `skill/SKILL.md`
- Modify: `skills/custom-learning-audiobook/SKILL.md`
- Modify: `skills/custom-learning-audiobook/references/package-and-qc.md`
- Modify: `docs/how-these-were-made.md`
- Create: `tests/test_skill_cover_contract.py`

**Interfaces:**
- Consumes: the spec/render/select/verify/build/sync CLIs from Tasks 1–6.
- Produces: one consistent new-book workflow for the canonical long and custom-learning skills.

- [ ] **Step 1: Write a failing documentation-contract test**

Create `tests/test_skill_cover_contract.py`:

```python
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
FILES = {
    "cover": ROOT / "skill" / "references" / "cover-art.md",
    "long": ROOT / "skill" / "SKILL.md",
    "custom": ROOT / "skills" / "custom-learning-audiobook" / "SKILL.md",
    "package": ROOT / "skills" / "custom-learning-audiobook" / "references" / "package-and-qc.md",
}


class SkillCoverContractTests(unittest.TestCase):
    def test_active_workflows_use_spec_selection_and_receipt_verification(self) -> None:
        text = "\n".join(path.read_text(encoding="utf-8") for path in FILES.values())
        for required in ("--spec", "cover-selection.json", "explicit-user-choice", "--cover-selection", "cover_receipts.py verify"):
            self.assertIn(required, text)

    def test_candidate_contract_varies_typography_as_well_as_art(self) -> None:
        for key in ("cover", "long", "custom", "package"):
            text = FILES[key].read_text(encoding="utf-8")
            self.assertIn("title strategy", text)
            self.assertIn("font", text)
            self.assertIn("line breaks", text)

    def test_active_commands_do_not_teach_the_legacy_template(self) -> None:
        for key in ("cover", "long", "custom", "package"):
            text = FILES[key].read_text(encoding="utf-8")
            self.assertNotIn("--layout bleed", text)
            self.assertNotIn("lower 25–35% reserved", text)
            self.assertNotIn("lower third carries the title", text)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test and confirm it fails against the legacy instructions**

```bash
/usr/local/bin/python3 -m unittest tests.test_skill_cover_contract -v
```

Expected: failures for missing `--spec`/receipt commands and legacy `--layout bleed` guidance.

- [ ] **Step 3: Rewrite the candidate brief and render sequence**

In `skill/references/cover-art.md`, preserve the research lens, genre calibration, image-generation prompt, rights rules, and human review bar. Replace the universal title-safe-zone and legacy render sections with this exact workflow:

````markdown
## Candidate Brief Before Making Art

Write one complete art-and-type brief per candidate before image generation:

1. Audience promise.
2. Central metaphor.
3. Composition, crop, and intended title field.
4. Material language and two-to-four-colour palette.
5. Anti-brief.
6. Title archetype and font roles.
7. Planned line breaks and hierarchy.
8. Title anchor, alignment, and approximate occupied area.
9. Intended relationship between title and art.
10. Subtitle, author, and AUDIOBOOK placement.

The three candidates must differ in metaphor, composition, palette, material
language, and title strategy. Font, line breaks, scale, placement, and effects
are part of the candidate—not a shared footer applied afterward.

## Render, Compare, and Select

Keep generated artwork text-free. Save each art file beside its validated
`cover-spec-N.json`, then render each complete composition:

```bash
RUN_ROOT=".build/custom-learning-audiobooks/$SLUG"
/usr/local/bin/python3 skill/scripts/make_cover.py \
  --spec "$RUN_ROOT/dist/cover-spec-1.json" \
  --out "$RUN_ROOT/dist/cover-1.png"
```

Repeat for candidates 2 and 3. Review every full-size render, generated
160-pixel thumbnail, art-and-type brief, font/palette note, and warning. Ask the
user to choose or request a mix. A mix becomes a new specification and render.

Only after the user chooses, create `cover-selection.json` with
`selection_source=explicit-user-choice` (or `requested-mix`). The renderer never
selects a candidate automatically. New books use `--spec`; the old
title/art/accent/tone/layout flags remain compatibility-only for existing calls.
````

Also remove claims that every image needs the same lower title area. Replace them with: `Generate art for the intended candidate composition; negative space may be top, bottom, side, central, interrupted, or supplied by an integrated band when the brief makes that relationship deliberate.`

- [ ] **Step 4: Update both skills and package commands**

In `skill/SKILL.md` and `skills/custom-learning-audiobook/SKILL.md`, replace legacy cover commands with the spec command above and require three complete title strategies. In `package-and-qc.md`, expand `dist/` to include:

```text
cover-source-1.png
cover-spec-1.json
cover-1.png
cover-1-thumbnail.png
cover-1.render.json
cover-selection.json
```

Before the post-choice commands, require the workflow to assign `SLUG`, `EDITION_ID`, `SELECTED_AT`, `CLASSIFICATION`, `PERMISSION_TO_PUBLISH`, `TITLE`, `SUBTITLE`, and `CONTRIBUTOR` from the approved run metadata. Then use these exact commands:

```bash
SELECTED=1
DIST=".build/custom-learning-audiobooks/$SLUG/dist"
/usr/local/bin/python3 skill/scripts/cover_receipts.py select \
  --render-receipt "$DIST/cover-$SELECTED.render.json" \
  --out "$DIST/cover-selection.json" \
  --book-slug "$SLUG" \
  --edition-id "$EDITION_ID" \
  --selection-source explicit-user-choice \
  --selected-at "$SELECTED_AT" \
  --classification "$CLASSIFICATION" \
  --permission-to-publish "$PERMISSION_TO_PUBLISH"

/usr/local/bin/python3 skill/scripts/build_book.py \
  --chapters-dir ".build/custom-learning-audiobooks/$SLUG/chapters" \
  --out-dir "$DIST" \
  --title "$TITLE" \
  --author "Dan Fakkeldy" \
  --contributor "$CONTRIBUTOR" \
  --subtitle "$SUBTITLE" \
  --slug "$SLUG" \
  --cover "$DIST/cover-$SELECTED.png" \
  --cover-selection "$DIST/cover-selection.json"

/usr/local/bin/python3 skill/scripts/cover_receipts.py verify \
  --selection "$DIST/cover-selection.json" \
  --cover "$DIST/cover-$SELECTED.png" \
  --epub "$DIST/$SLUG.epub" \
  --m4b "$DIST/$SLUG.m4b" \
  --receipt "$DIST/cover-selection.json"
```

For an existing delivery folder, document a mandatory dry run and explicit classification before apply:

```bash
/usr/local/bin/python3 skill/scripts/sync_selected_cover.py \
  --selection "$DIST/cover-selection.json" \
  --cover "$DIST/cover-$SELECTED.png" \
  --epub "$DIST/$SLUG.epub" \
  --m4b "$DIST/$SLUG.m4b" \
  --destination "$ICLOUD_DIR" \
  --intent reuse
```

Use `--intent supersede` only for a newer explicit choice. Add `--apply` only after the reported classification is expected. If a destination has cover-bearing files but no receipt, it is an `unreceipted` conflict unless the operation is an explicit supersession.

- [ ] **Step 5: Update the public method summary**

Change the one cover sentence in `docs/how-these-were-made.md` to state that `make_cover.py` renders a validated art-and-type specification using bundled fonts, the user selects among three complete candidates, and the resulting receipt is verified through EPUB/M4B/delivery.

- [ ] **Step 6: Run skill, documentation, and full validation**

```bash
/usr/local/bin/python3 -m unittest tests.test_skill_cover_contract -v
/usr/local/bin/python3 tools/validate_skills.py
/usr/local/bin/python3 -m unittest discover -s tests -v
git diff --check
```

Expected: documentation-contract tests pass, `validate_skills: clean`, the full suite passes, and no whitespace errors remain.

- [ ] **Step 7: Commit the workflow migration**

```bash
git add skill/SKILL.md skill/references/cover-art.md skills/custom-learning-audiobook/SKILL.md skills/custom-learning-audiobook/references/package-and-qc.md docs/how-these-were-made.md tests/test_skill_cover_contract.py
git commit -m "docs: make adaptive cover specs the default"
```

---

### Task 8: Render the Three Rodents Pilot Candidates and Stop for Selection

**Files:**
- Create ignored: `.build/custom-learning-audiobooks/rodents-in-the-walls-cover-pilot/dist/cover-source.png`
- Create ignored: `cover-spec-{1,2,3}.json`, `cover-{1,2,3}.png`, thumbnails, render receipts, `briefs.md`, and `contact-sheet-input.json` in the same `dist/`.
- Create ignored: `.build/custom-learning-audiobooks/rodents-in-the-walls-cover-pilot/contact-sheet.png`
- Modify public/repo/iCloud package files: none.

**Interfaces:**
- Consumes: source art SHA-256 `cced16a14a0aaced901af7ffd0b140c4d6e13fdf88bd3da22a9724fb7bad9812`.
- Produces: C1 full-bleed display, C2 integrated colour band, and B1-class expressive-run candidates for explicit user review.

- [ ] **Step 1: Copy and prove the exact approved source art**

```bash
PILOT=.build/custom-learning-audiobooks/rodents-in-the-walls-cover-pilot
DIST="$PILOT/dist"
SOURCE='/Users/dfakkeldy/Developer/explainer-audiobooks/.build/custom-learning-audiobooks/rodents-in-the-walls-v3/dist/cover-raster-art-1.png'
mkdir -p "$DIST"
cp "$SOURCE" "$DIST/cover-source.png"
test "$(shasum -a 256 "$DIST/cover-source.png" | awk '{print $1}')" = cced16a14a0aaced901af7ffd0b140c4d6e13fdf88bd3da22a9724fb7bad9812
file "$DIST/cover-source.png"
```

Expected: a 1024×1536 RGB PNG with the exact approved hash. Do not regenerate the art.

- [ ] **Step 2: Write the shared candidate metadata and three art-and-type briefs**

Use `apply_patch` to create `briefs.md`. Record the shared visual thesis—blue plaster wall, orange exposed plaster, branching rodent shadows, and a central broken opening—and these three distinct title strategies:

| ID | Direction | Title strategy | Palette | Relationship to art |
|---|---|---|---|---|
| `c1-full-bleed-display` | Full-Bleed Display | Large left-aligned condensed/serif hierarchy in the existing upper wall space | navy `#132238`, plaster orange `#EF5735`, warm cream `#F6EDDA` | Type occupies the negative wall without shrinking or framing the art |
| `c2-integrated-colour-band` | Integrated Colour Band | Editorial serif and condensed title locked into an orange plaster-derived band | orange `#EF5735`, navy `#132238`, cream `#F6EDDA` | The band behaves like a deliberate patch of material from the damaged wall |
| `b1-shadow-branches` | Shadow Branches | Staggered per-glyph `RODENTS` plus strong serif `WALLS` | navy, orange, cream | Letter rhythm echoes the branching shadows while preserving immediate reading order |

State explicitly that reusing one art file is a pilot exception to isolate renderer quality. Future candidate sets still vary art metaphor, material language, crop, palette, and title strategy.

- [ ] **Step 3: Create the three validated specifications**

Use `apply_patch` to create three JSON files. Every file has `schema_version: 1`; metadata exactly `Rodents in the Walls`, `Squirrels and Other Houseguests in Western Cape Breton`, `Dan Fakkeldy`, and `AUDIOBOOK`; canvas exactly `1600`, `2560`, `#132238`, and safe margin `96`; and art exactly `cover-source.png`, `bleed`, `center`, box `[0, 0, 1600, 2560]`, opacity `1`, and blend mode `normal`.

The three candidate objects are exactly:

```json
{"cover-spec-1.json":{"id":"c1-full-bleed-display","direction_name":"Full-Bleed Display"},"cover-spec-2.json":{"id":"c2-integrated-colour-band","direction_name":"Integrated Colour Band"},"cover-spec-3.json":{"id":"b1-shadow-branches","direction_name":"Shadow Branches"}}
```

For `cover-spec-1.json`, use this complete layer array:

```json
[
  {"kind":"scrim","box":[0,0,1600,1120],"fill":{"kind":"linear-gradient","start":[0,0],"end":[0,1120],"stops":[{"offset":0,"colour":"#132238","opacity":0.78},{"offset":0.72,"colour":"#132238","opacity":0.44},{"offset":1,"colour":"#132238","opacity":0}]},"opacity":1,"blend_mode":"normal","purpose":"quiet the upper plaster while retaining its texture and shadow detail"},
  {"kind":"text","role":"label","text":"AUDIOBOOK","font_id":"geometric-sans","font_variation":{"wght":650},"box":[96,112,650,70],"size":32,"line_height":40,"tracking":10,"align":"left","colour":"#EF5735","opacity":1,"rotation":0,"baseline_shift":0,"contrast_against":"#132238"},
  {"kind":"text","role":"title","title_order":1,"text":"RODENTS","font_id":"display-condensed","box":[96,215,1408,300],"size":250,"line_height":260,"tracking":1,"align":"left","colour":"#EF5735","opacity":1,"rotation":0,"baseline_shift":0,"shadow":{"colour":"#07111F","dx":10,"dy":16,"blur":18,"opacity":0.48},"contrast_against":"#132238"},
  {"kind":"text","role":"title","title_order":2,"text":"IN THE","font_id":"geometric-sans","font_variation":{"wght":650},"box":[104,500,650,130],"size":80,"line_height":92,"tracking":8,"align":"left","colour":"#F6EDDA","opacity":1,"rotation":0,"baseline_shift":0,"contrast_against":"#132238"},
  {"kind":"text","role":"title","title_order":3,"text":"WALLS","font_id":"editorial-serif","font_variation":{"SOFT":28,"WONK":1,"opsz":110,"wght":820},"box":[96,610,1408,315],"size":226,"line_height":238,"tracking":0,"align":"left","colour":"#F6EDDA","opacity":1,"rotation":0,"baseline_shift":0,"shadow":{"colour":"#07111F","dx":8,"dy":14,"blur":16,"opacity":0.4},"contrast_against":"#132238"},
  {"kind":"scrim","box":[0,2010,1600,550],"fill":{"kind":"linear-gradient","start":[0,2010],"end":[0,2560],"stops":[{"offset":0,"colour":"#132238","opacity":0},{"offset":0.38,"colour":"#132238","opacity":0.62},{"offset":1,"colour":"#07111F","opacity":0.92}]},"opacity":1,"blend_mode":"normal","purpose":"support subtitle and author without covering the wall opening"},
  {"kind":"text","role":"subtitle","text":"Squirrels and Other Houseguests in Western Cape Breton","font_id":"geometric-sans","font_variation":{"wght":500},"box":[96,2140,1408,140],"size":40,"line_height":50,"tracking":0,"align":"left","colour":"#F6EDDA","opacity":1,"rotation":0,"baseline_shift":0,"contrast_against":"#132238"},
  {"kind":"text","role":"author","text":"Dan Fakkeldy","font_id":"geometric-sans","font_variation":{"wght":650},"box":[96,2355,1408,90],"size":38,"line_height":48,"tracking":3,"align":"left","colour":"#EF5735","opacity":1,"rotation":0,"baseline_shift":0,"contrast_against":"#07111F"}
]
```

For `cover-spec-2.json`, set candidate id/name to `c2-integrated-colour-band` / `Integrated Colour Band` and use:

```json
[
  {"kind":"field","box":[64,130,1472,760],"fill":{"kind":"solid","colour":"#EF5735"},"opacity":0.94,"blend_mode":"normal","purpose":"turn the exposed plaster accent into a deliberate editorial title material"},
  {"kind":"line","start":[96,850],"end":[1504,850],"colour":"#F6EDDA","width":6,"opacity":0.82,"purpose":"bind the band to the pale exposed plaster around the wall opening"},
  {"kind":"text","role":"label","text":"AUDIOBOOK","font_id":"technical-mono","box":[110,170,900,70],"size":30,"line_height":38,"tracking":8,"align":"left","colour":"#132238","opacity":1,"rotation":0,"baseline_shift":0,"contrast_against":"#EF5735"},
  {"kind":"text","role":"title","title_order":1,"text":"RODENTS","font_id":"editorial-serif","font_variation":{"SOFT":18,"WONK":1,"opsz":100,"wght":850},"box":[104,275,1392,260],"size":205,"line_height":218,"tracking":0,"align":"left","colour":"#132238","opacity":1,"rotation":0,"baseline_shift":0,"contrast_against":"#EF5735"},
  {"kind":"text","role":"title","title_order":2,"text":"IN THE","font_id":"geometric-sans","font_variation":{"wght":650},"box":[112,520,650,115],"size":72,"line_height":82,"tracking":7,"align":"left","colour":"#132238","opacity":1,"rotation":0,"baseline_shift":0,"contrast_against":"#EF5735"},
  {"kind":"text","role":"title","title_order":3,"text":"WALLS","font_id":"display-condensed","box":[104,610,1392,250],"size":220,"line_height":230,"tracking":2,"align":"left","colour":"#F6EDDA","opacity":1,"rotation":0,"baseline_shift":0,"outline":{"colour":"#132238","width":3},"contrast_against":"#EF5735"},
  {"kind":"scrim","box":[0,2020,1600,540],"fill":{"kind":"linear-gradient","start":[0,2020],"end":[0,2560],"stops":[{"offset":0,"colour":"#132238","opacity":0},{"offset":0.4,"colour":"#132238","opacity":0.7},{"offset":1,"colour":"#07111F","opacity":0.94}]},"opacity":1,"blend_mode":"normal","purpose":"support secondary metadata over the baseboard without changing the main art crop"},
  {"kind":"text","role":"subtitle","text":"Squirrels and Other Houseguests in Western Cape Breton","font_id":"geometric-sans","font_variation":{"wght":500},"box":[96,2150,1408,140],"size":40,"line_height":50,"tracking":0,"align":"left","colour":"#F6EDDA","opacity":1,"rotation":0,"baseline_shift":0,"contrast_against":"#132238"},
  {"kind":"text","role":"author","text":"Dan Fakkeldy","font_id":"technical-mono","box":[96,2360,1408,85],"size":36,"line_height":44,"tracking":2,"align":"left","colour":"#EF5735","opacity":1,"rotation":0,"baseline_shift":0,"contrast_against":"#07111F"}
]
```

For `cover-spec-3.json`, set candidate id/name to `b1-shadow-branches` / `Shadow Branches` and use:

```json
[
  {"kind":"scrim","box":[0,0,1600,1110],"fill":{"kind":"linear-gradient","start":[0,0],"end":[0,1110],"stops":[{"offset":0,"colour":"#07111F","opacity":0.78},{"offset":0.68,"colour":"#132238","opacity":0.36},{"offset":1,"colour":"#132238","opacity":0}]},"opacity":1,"blend_mode":"multiply","purpose":"preserve the branch shadows while giving expressive title runs a stable field"},
  {"kind":"line","start":[245,500],"end":[470,790],"colour":"#EF5735","width":7,"opacity":0.66,"purpose":"echo one existing shadow branch without tracing the animal silhouette"},
  {"kind":"line","start":[870,505],"end":[1040,770],"colour":"#F6EDDA","width":5,"opacity":0.48,"purpose":"carry the title rhythm toward the central shadow structure"},
  {"kind":"text","role":"label","text":"AUDIOBOOK","font_id":"technical-mono","box":[104,112,700,70],"size":30,"line_height":38,"tracking":9,"align":"left","colour":"#F6EDDA","opacity":1,"rotation":0,"baseline_shift":0,"contrast_against":"#07111F"},
  {"kind":"text","role":"title","title_order":1,"text":"RODENTS","font_id":"display-condensed","box":[96,220,1408,315],"size":232,"line_height":245,"tracking":0,"align":"left","colour":"#EF5735","opacity":1,"rotation":0,"baseline_shift":0,"outline":{"colour":"#07111F","width":2},"shadow":{"colour":"#07111F","dx":12,"dy":18,"blur":20,"opacity":0.52},"runs":[{"text":"R","colour":"#EF5735","rotation":-5,"baseline_shift":14,"dx":0},{"text":"O","colour":"#F6EDDA","rotation":3,"baseline_shift":-10,"dx":5},{"text":"D","colour":"#EF5735","rotation":-2,"baseline_shift":8,"dx":-2},{"text":"E","colour":"#F6EDDA","rotation":4,"baseline_shift":-4,"dx":4},{"text":"N","colour":"#EF5735","rotation":-4,"baseline_shift":12,"dx":0},{"text":"T","colour":"#F6EDDA","rotation":2,"baseline_shift":-7,"dx":3},{"text":"S","colour":"#EF5735","rotation":-2,"baseline_shift":5,"dx":0}],"contrast_against":"#07111F"},
  {"kind":"text","role":"title","title_order":2,"text":"IN THE","font_id":"geometric-sans","font_variation":{"wght":650},"box":[118,525,680,125],"size":82,"line_height":94,"tracking":9,"align":"left","colour":"#F6EDDA","opacity":1,"rotation":-2,"baseline_shift":0,"contrast_against":"#132238"},
  {"kind":"text","role":"title","title_order":3,"text":"WALLS","font_id":"editorial-serif","font_variation":{"SOFT":42,"WONK":1,"opsz":110,"wght":850},"box":[400,625,1100,300],"size":220,"line_height":232,"tracking":0,"align":"right","colour":"#F6EDDA","opacity":1,"rotation":1,"baseline_shift":0,"shadow":{"colour":"#07111F","dx":8,"dy":14,"blur":18,"opacity":0.44},"contrast_against":"#132238"},
  {"kind":"scrim","box":[0,2015,1600,545],"fill":{"kind":"linear-gradient","start":[0,2015],"end":[0,2560],"stops":[{"offset":0,"colour":"#132238","opacity":0},{"offset":0.38,"colour":"#132238","opacity":0.68},{"offset":1,"colour":"#07111F","opacity":0.94}]},"opacity":1,"blend_mode":"normal","purpose":"keep secondary metadata separate from the expressive title"},
  {"kind":"text","role":"subtitle","text":"Squirrels and Other Houseguests in Western Cape Breton","font_id":"geometric-sans","font_variation":{"wght":500},"box":[96,2145,1408,140],"size":40,"line_height":50,"tracking":0,"align":"left","colour":"#F6EDDA","opacity":1,"rotation":0,"baseline_shift":0,"contrast_against":"#132238"},
  {"kind":"text","role":"author","text":"Dan Fakkeldy","font_id":"geometric-sans","font_variation":{"wght":650},"box":[96,2358,1408,88],"size":38,"line_height":46,"tracking":3,"align":"left","colour":"#EF5735","opacity":1,"rotation":0,"baseline_shift":0,"contrast_against":"#07111F"}
]
```

- [ ] **Step 4: Validate and render all three**

```bash
for number in 1 2 3; do
  /usr/local/bin/python3 skill/scripts/make_cover.py \
    --spec "$DIST/cover-spec-$number.json" \
    --out "$DIST/cover-$number.png" || exit 1
done
/usr/local/bin/python3 -m json.tool "$DIST/cover-1.render.json" >/dev/null
/usr/local/bin/python3 -m json.tool "$DIST/cover-2.render.json" >/dev/null
/usr/local/bin/python3 -m json.tool "$DIST/cover-3.render.json" >/dev/null
```

Expected: three 1600×2560 RGB covers, three 160×256 thumbnails, and three render receipts whose source-art hash is the approved hash. No `cover-selection.json` exists yet.

- [ ] **Step 5: Create the comparison surface**

Create `contact-sheet-input.json` as:

```json
[
  {"title":"C1 — Full-Bleed Display","cover":".build/custom-learning-audiobooks/rodents-in-the-walls-cover-pilot/dist/cover-1.png"},
  {"title":"C2 — Integrated Colour Band","cover":".build/custom-learning-audiobooks/rodents-in-the-walls-cover-pilot/dist/cover-2.png"},
  {"title":"B1 — Shadow Branches","cover":".build/custom-learning-audiobooks/rodents-in-the-walls-cover-pilot/dist/cover-3.png"}
]
```

Render it from the repo root:

```bash
/usr/local/bin/python3 skill/scripts/make_cover_contact_sheet.py \
  --manifest "$DIST/contact-sheet-input.json" \
  --out "$PILOT/contact-sheet.png"
```

- [ ] **Step 6: Perform full-size and thumbnail visual review**

Open the contact sheet, all three 1600×2560 covers, and all three generated thumbnails. Record pass/fail for exact title/subtitle/author spelling, title hierarchy, art retained at useful scale, shadows and hole still legible, colour relationship, no clipped metadata, 160-pixel readability, and whether any treatment feels templated. If a candidate fails, change its specification—not the source art—and rerender/review it under the same candidate id with the receipt history preserved in the ignored run folder.

- [ ] **Step 7: Present the three final candidates and stop**

Send Dan the three final covers, thumbnails, names, one-line rationales, font roles, palette, and warnings. Ask for exactly one candidate number or a requested mix. Do not create a selection receipt; do not change `books/rodents-in-the-walls/`; do not touch iCloud. This is a mandatory human gate, not an execution failure.

No commit is created for ignored pilot scratch in this task.

---

### Task 9: Promote the Chosen Rodents Cover Across Both Editions

**Files:**
- Create: `books/rodents-in-the-walls/cover-source.png`
- Create: `books/rodents-in-the-walls/cover-spec.json`
- Create: `books/rodents-in-the-walls/cover-thumbnail.png`
- Create: `books/rodents-in-the-walls/cover.render.json`
- Create: `books/rodents-in-the-walls/cover-selection.json`
- Create: `books/rodents-in-the-walls/cover-pre-adaptive.png`
- Modify: `books/rodents-in-the-walls/cover.png`
- Modify: `books/rodents-in-the-walls/rodents-in-the-walls.epub`
- Modify: `books/rodents-in-the-walls/rodents-in-the-walls.m4b`
- Modify: `books/rodents-in-the-walls/README.md`
- Create: `docs/cover-pilots/rodents-adaptive-2026-07/manifest.md`
- Create: `docs/cover-pilots/rodents-adaptive-2026-07/contact-sheet.png`
- Modify: only cover-bearing/cover-description/checksum files in the existing iCloud `Rodents in the Walls` delivery folder.

**Interfaces:**
- Consumes: Dan's explicit candidate number or requested mix from Task 8.
- Produces: a canonical `corrected-v2` public receipt and a separate `v3` iCloud receipt pointing to the same selected visual but preserving each edition's own EPUB/M4B content.

- [ ] **Step 1: Record immutable pre-change evidence for both editions**

The public repo and iCloud delivery currently contain different editions. Never copy the repo EPUB/M4B over iCloud: the public M4B is about 7377.963 seconds, while iCloud v3 is about 5464.661 seconds.

```bash
PILOT=.build/custom-learning-audiobooks/rodents-in-the-walls-cover-pilot
DIST="$PILOT/dist"
BOOK=books/rodents-in-the-walls
ICLOUD='/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/Rodents in the Walls'
mkdir -p "$PILOT/evidence"
/usr/local/bin/python3 - <<'PY'
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path('skill/scripts').resolve()))
from replace_m4b_cover import media_signature
paths = {
    'repo': Path('books/rodents-in-the-walls/rodents-in-the-walls.m4b'),
    'icloud-v3': Path('/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/Rodents in the Walls/rodents-in-the-walls.m4b')
}
payload = {name: media_signature(path).__dict__ for name, path in paths.items()}
Path('.build/custom-learning-audiobooks/rodents-in-the-walls-cover-pilot/evidence/m4b-before.json').write_text(json.dumps(payload, indent=2, default=list), encoding='utf-8')
print('M4B_EDITION_EVIDENCE_OK', payload['repo']['duration'], payload['icloud-v3']['duration'])
PY
```

Write a SHA-256 inventory of every iCloud file to ignored evidence. This inventory is used after sync to prove that alignment, QA, Markdown, images, and unrelated files stayed unchanged:

```bash
/usr/local/bin/python3 - <<'PY'
import hashlib, json
from pathlib import Path
root = Path('/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/Rodents in the Walls')
inventory = {
    str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
    for path in sorted(root.rglob('*')) if path.is_file()
}
out = Path('.build/custom-learning-audiobooks/rodents-in-the-walls-cover-pilot/evidence/icloud-before.json')
out.write_text(json.dumps(inventory, indent=2, sort_keys=True), encoding='utf-8')
print('ICLOUD_INVENTORY_OK', len(inventory))
PY
```

- [ ] **Step 2: Bind the explicit choice to a numeric candidate**

Set `SELECTED` to exactly `1`, `2`, or `3` from Dan's response. Map C1 to 1, C2 to 2, and B1 to 3. For a requested mix, create and render `cover-spec-4.json`, review it with Dan, then set `SELECTED=4`. Reject empty, automatic, or inferred values:

```bash
case "$SELECTED" in
  1|2|3|4) ;;
  *) echo 'SELECTED must come from the explicit user choice'; exit 1 ;;
esac
SELECTION_SOURCE=explicit-user-choice
test "$SELECTED" != 4 || SELECTION_SOURCE=requested-mix
```

- [ ] **Step 3: Promote and rerender the canonical public assets**

```bash
cp "$BOOK/cover.png" "$BOOK/cover-pre-adaptive.png"
cp "$DIST/cover-source.png" "$BOOK/cover-source.png"
cp "$DIST/cover-spec-$SELECTED.json" "$BOOK/cover-spec.json"
/usr/local/bin/python3 skill/scripts/make_cover.py \
  --spec "$BOOK/cover-spec.json" \
  --out "$BOOK/cover.png"
test "$(shasum -a 256 "$BOOK/cover.png" | awk '{print $1}')" = "$(shasum -a 256 "$DIST/cover-$SELECTED.png" | awk '{print $1}')"
```

Expected: canonical rerender creates `cover.png`, `cover-thumbnail.png`, and `cover.render.json`; its bytes equal the reviewed candidate.

Create the public selection receipt using the actual current offset timestamp:

```bash
SELECTED_AT=$(date -Iseconds)
/usr/local/bin/python3 skill/scripts/cover_receipts.py select \
  --render-receipt "$BOOK/cover.render.json" \
  --out "$BOOK/cover-selection.json" \
  --book-slug rodents-in-the-walls \
  --edition-id corrected-v2 \
  --selection-source "$SELECTION_SOURCE" \
  --selected-at "$SELECTED_AT" \
  --classification public-safe \
  --permission-to-publish granted
```

- [ ] **Step 4: Refresh only the public EPUB cover and M4B artwork**

```bash
/usr/local/bin/python3 skill/scripts/refresh_epub_cover.py \
  --epub "$BOOK/rodents-in-the-walls.epub" \
  --cover "$BOOK/cover.png" \
  --out "$PILOT/rodents-public.epub"
mv "$PILOT/rodents-public.epub" "$BOOK/rodents-in-the-walls.epub"

/usr/local/bin/python3 skill/scripts/replace_m4b_cover.py \
  --m4b "$BOOK/rodents-in-the-walls.m4b" \
  --cover "$BOOK/cover.png" \
  --out "$PILOT/rodents-public.m4b"
mv "$PILOT/rodents-public.m4b" "$BOOK/rodents-in-the-walls.m4b"

/usr/local/bin/python3 skill/scripts/cover_receipts.py verify \
  --selection "$BOOK/cover-selection.json" \
  --cover "$BOOK/cover.png" \
  --epub "$BOOK/rodents-in-the-walls.epub" \
  --m4b "$BOOK/rodents-in-the-walls.m4b" \
  --receipt "$BOOK/cover-selection.json"
```

Compare the post-change public `media_signature` with `m4b-before.json`; the audio packet hash, duration, three stream codec/type pairs, nine chapter boundaries/titles, and format tags must be unchanged:

```bash
/usr/local/bin/python3 - <<'PY'
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path('skill/scripts').resolve()))
from replace_m4b_cover import media_signature
before = json.loads(Path('.build/custom-learning-audiobooks/rodents-in-the-walls-cover-pilot/evidence/m4b-before.json').read_text())['repo']
after = media_signature(Path('books/rodents-in-the-walls/rodents-in-the-walls.m4b')).__dict__
normalized_after = {key: [list(value) for value in item] if key in {'streams', 'chapters', 'format_tags'} else value for key, value in after.items()}
assert normalized_after == before, (before, normalized_after)
print('PUBLIC_M4B_UNCHANGED')
PY
```

- [ ] **Step 5: Stage the same visual for iCloud v3 without replacing its edition**

```bash
DELIVERY_STAGE="$PILOT/icloud-v3"
mkdir -p "$DELIVERY_STAGE"
cp "$BOOK/cover.png" "$DELIVERY_STAGE/cover.png"

/usr/local/bin/python3 skill/scripts/refresh_epub_cover.py \
  --epub "$ICLOUD/rodents-in-the-walls.epub" \
  --cover "$DELIVERY_STAGE/cover.png" \
  --out "$DELIVERY_STAGE/rodents-in-the-walls.epub"

/usr/local/bin/python3 skill/scripts/replace_m4b_cover.py \
  --m4b "$ICLOUD/rodents-in-the-walls.m4b" \
  --cover "$DELIVERY_STAGE/cover.png" \
  --out "$DELIVERY_STAGE/rodents-in-the-walls.m4b"

/usr/local/bin/python3 skill/scripts/cover_receipts.py select \
  --render-receipt "$BOOK/cover.render.json" \
  --out "$DELIVERY_STAGE/cover-selection.json" \
  --book-slug rodents-in-the-walls \
  --edition-id v3 \
  --selection-source "$SELECTION_SOURCE" \
  --selected-at "$SELECTED_AT" \
  --classification public-safe \
  --permission-to-publish granted
```

Verify the staged v3 package against its v3 receipt before touching iCloud:

```bash
/usr/local/bin/python3 skill/scripts/cover_receipts.py verify \
  --selection "$DELIVERY_STAGE/cover-selection.json" \
  --cover "$DELIVERY_STAGE/cover.png" \
  --epub "$DELIVERY_STAGE/rodents-in-the-walls.epub" \
  --m4b "$DELIVERY_STAGE/rodents-in-the-walls.m4b" \
  --receipt "$DELIVERY_STAGE/cover-selection.json"
```

- [ ] **Step 6: Dry-run, apply, and verify the iCloud transaction**

```bash
/usr/local/bin/python3 skill/scripts/sync_selected_cover.py \
  --selection "$DELIVERY_STAGE/cover-selection.json" \
  --cover "$DELIVERY_STAGE/cover.png" \
  --epub "$DELIVERY_STAGE/rodents-in-the-walls.epub" \
  --m4b "$DELIVERY_STAGE/rodents-in-the-walls.m4b" \
  --destination "$ICLOUD" \
  --intent supersede \
  --checksum-manifest "$ICLOUD/SHA256SUMS"
```

Expected dry-run decision for the current unreceipted package: `supersede-unreceipted`, `applied=false`. Then repeat with `--apply`.

Use `apply_patch` to change only the iCloud README's cover-specific statements: package table `cover.png` row, edition-detail `Cover:` row, visual-provenance cover sentence, and cover verification row. Name the selected adaptive direction and `cover-selection.json`; leave v3 manuscript/audio/figure claims untouched. Recompute only the README entry in `SHA256SUMS`.

```bash
/usr/local/bin/python3 - <<'PY'
import hashlib
from pathlib import Path
root = Path('/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/Rodents in the Walls')
manifest = root / 'SHA256SUMS'
digest = hashlib.sha256((root / 'README.md').read_bytes()).hexdigest()
rows = []
for line in manifest.read_text(encoding='utf-8').splitlines():
    old, name = line.split(None, 1)
    rows.append((digest if name.strip() == 'README.md' else old, name.strip()))
manifest.write_text(''.join(f'{value}  {name}\n' for value, name in rows), encoding='utf-8')
PY
```

Verify afterward:

```bash
/usr/local/bin/python3 skill/scripts/cover_receipts.py verify \
  --selection "$ICLOUD/cover-selection.json" \
  --cover "$ICLOUD/cover.png" \
  --epub "$ICLOUD/rodents-in-the-walls.epub" \
  --m4b "$ICLOUD/rodents-in-the-walls.m4b" \
  --receipt "$ICLOUD/cover-selection.json"
```

Compare against the pre-change inventory. Allowed iCloud changes are exactly `cover.png`, `rodents-in-the-walls.epub`, `rodents-in-the-walls.m4b`, `cover-selection.json`, `README.md`, and `SHA256SUMS`. The v3 audio packet hash/duration/chapters remain unchanged; all alignment, QA, Markdown, figures, and unrelated files remain byte-identical:

```bash
/usr/local/bin/python3 - <<'PY'
import hashlib, json, sys
from pathlib import Path
sys.path.insert(0, str(Path('skill/scripts').resolve()))
from replace_m4b_cover import media_signature
root = Path('/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/Rodents in the Walls')
before = json.loads(Path('.build/custom-learning-audiobooks/rodents-in-the-walls-cover-pilot/evidence/icloud-before.json').read_text())
after = {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest() for path in root.rglob('*') if path.is_file()}
changed = {name for name in set(before) | set(after) if before.get(name) != after.get(name)}
allowed = {'cover.png', 'rodents-in-the-walls.epub', 'rodents-in-the-walls.m4b', 'cover-selection.json', 'README.md', 'SHA256SUMS'}
assert changed <= allowed, changed - allowed
m4b_before = json.loads(Path('.build/custom-learning-audiobooks/rodents-in-the-walls-cover-pilot/evidence/m4b-before.json').read_text())['icloud-v3']
m4b_after = media_signature(root / 'rodents-in-the-walls.m4b').__dict__
normalized_after = {key: [list(value) for value in item] if key in {'streams', 'chapters', 'format_tags'} else value for key, value in m4b_after.items()}
assert normalized_after == m4b_before, (m4b_before, normalized_after)
print('ICLOUD_V3_PRESERVED', sorted(changed))
PY
```

- [ ] **Step 7: Publish the pilot provenance and update the public README**

Create `docs/cover-pilots/rodents-adaptive-2026-07/manifest.md` with the approved design link, source-art hash/provenance, all three direction names/spec/render hashes, selected direction and timestamp/source, four font IDs/licences, full-size/thumbnail review results, public corrected-v2 verification, separate iCloud-v3 verification, unchanged audio packet hashes, and the explicit note that one source artwork was intentionally reused for this compositor pilot.

Copy the reviewed three-cover contact sheet from the ignored pilot folder to `docs/cover-pilots/rodents-adaptive-2026-07/contact-sheet.png`. Update the public book README's Cover and Verification sections to link the new manifest and describe the selected adaptive art/type composition and receipt checks. Preserve the historical July collection-refresh manifest/contact sheet as historical evidence; do not rewrite it to pretend PR #17 produced the new cover.

- [ ] **Step 8: Commit the selected public pilot only**

```bash
git add \
  books/rodents-in-the-walls/cover-source.png \
  books/rodents-in-the-walls/cover-spec.json \
  books/rodents-in-the-walls/cover.png \
  books/rodents-in-the-walls/cover-thumbnail.png \
  books/rodents-in-the-walls/cover.render.json \
  books/rodents-in-the-walls/cover-selection.json \
  books/rodents-in-the-walls/cover-pre-adaptive.png \
  books/rodents-in-the-walls/rodents-in-the-walls.epub \
  books/rodents-in-the-walls/rodents-in-the-walls.m4b \
  books/rodents-in-the-walls/README.md \
  docs/cover-pilots/rodents-adaptive-2026-07
git diff --cached --check
git commit -m "feat: publish adaptive Rodents cover pilot"
```

Do not commit unselected covers/specs or ignored run evidence.

---

### Task 10: Final Verification, Ready PR, and Durable Receipt

**Files:**
- Modify only files that fail the final gates.
- Update the smallest relevant Explainer Audiobooks KB project/status/log surfaces after the implementation PR exists.

**Interfaces:**
- Consumes: all committed infrastructure/docs and, after the human gate, the chosen Rodents public pilot.
- Produces: a clean ready PR into `main`, exact hosted-check status, verified installed-skill boundary, and a merged Tier-1 KB receipt.

- [ ] **Step 1: Run the complete local automated gate**

```bash
/usr/local/bin/python3 tools/fetch_cover_fonts.py --check
/usr/local/bin/python3 -m json.tool skill/schemas/cover-spec-v1.schema.json >/dev/null
/usr/local/bin/python3 tools/validate_skills.py
/usr/local/bin/python3 -m unittest discover -s tests -v
unzip -t books/rodents-in-the-walls/rodents-in-the-walls.epub >/dev/null
/usr/local/bin/python3 skill/scripts/cover_receipts.py verify \
  --selection books/rodents-in-the-walls/cover-selection.json \
  --cover books/rodents-in-the-walls/cover.png \
  --epub books/rodents-in-the-walls/rodents-in-the-walls.epub \
  --m4b books/rodents-in-the-walls/rodents-in-the-walls.m4b \
  --receipt books/rodents-in-the-walls/cover-selection.json
git diff --check
git status --short --branch
```

Expected: eight font assets valid, schema valid, skill validator clean, all tests pass, EPUB valid, all public cover identities pass, no whitespace errors, and only intentional committed work.

- [ ] **Step 2: Run the final visual and edition-preservation gate**

Open the selected public `cover.png`, its 160-pixel thumbnail, and the three-cover pilot contact sheet. Confirm exact metadata, thumbnail hierarchy, source art retained at full scale, no clipping, no generic footer, and the selected direction still matches what Dan chose.

Re-run the stored before/after media-signature and iCloud inventory comparisons. Public corrected-v2 and iCloud v3 must retain their own pre-change durations, audio packet hashes, streams, chapter markers, and non-cover files. A cover match alone is not sufficient if an edition was replaced.

- [ ] **Step 3: Rebase onto current `origin/main` and rerun the gate**

```bash
git fetch origin
git rebase origin/main
```

If a conflict touches a binary EPUB/M4B/cover or a receipt, stop and resolve it from hashes and edition evidence; never pick a binary side by branch name. Repeat Tasks 10.1 and 10.2 after a successful rebase.

- [ ] **Step 4: Push and open the ready implementation PR**

```bash
git push -u origin codex/adaptive-cover-spec-implementation
gh pr create \
  --base main \
  --head codex/adaptive-cover-spec-implementation \
  --title "Implement adaptive art-directed audiobook covers" \
  --body-file .build/custom-learning-audiobooks/rodents-in-the-walls-cover-pilot/pr-body.md
```

The PR body must distinguish infrastructure commits from the user-selected pilot; name the four bundled fonts/licences, test count, candidate review gate, selected direction, public corrected-v2 checks, separate iCloud-v3 checks, unchanged audio hashes/chapters, and privacy scope. If Task 9 is waiting on selection, do not open the final PR yet; the branch remains a progressing implementation, not a completed deliverable.

- [ ] **Step 5: Check hosted state from GitHub**

```bash
PR=$(gh pr view --json number -q .number)
gh pr view "$PR" --json state,isDraft,mergeStateStatus,headRefOid,baseRefName,statusCheckRollup,url
gh pr checks "$PR"
```

If no checks are configured, report `no hosted checks reported`; do not call that passing CI. If a required check fails, inspect its job log, fix the concrete failure, re-run the local gate, commit, and push.

- [ ] **Step 6: Verify the installed-skill boundary without repointing it**

```bash
for link in \
  "$HOME/.claude/skills/explainer-audiobook" \
  "$HOME/.agents/skills/explainer-audiobook" \
  "$HOME/.claude/skills/custom-learning-audiobook" \
  "$HOME/.agents/skills/custom-learning-audiobook" \
  "$HOME/.codex/skills/custom-learning-audiobook"; do
  printf '%s\t%s\n' "$link" "$(readlink "$link")"
done
```

Expected: every link resolves into `/Users/dfakkeldy/Developer/explainer-audiobooks/`. Do not repoint shared agent installations to an unmerged feature worktree. Report that installed Claude/Codex/shared-agent behavior remains on the merged original checkout until the implementation PR merges and that checkout is updated.

- [ ] **Step 7: File the durable KB implementation receipt**

In a clean KB worktree based on current `origin/main`, update the existing `2026-07-12 Adaptive Audiobook Cover Specification Design` status page rather than creating a duplicate. Record Dan's written approval, the implementation PR URL/exact head, automated and visual evidence, the chosen candidate, corrected-v2 versus iCloud-v3 preservation, hosted-check state, installed-skill boundary, and unchanged Master Plan impact. Update `bundle/projects/explainer-audiobooks.md`, `bundle/status/index.md` only if its summary is stale, and the top `2026-07-12` section of `bundle/log.md`.

```bash
/usr/local/bin/python3 tools/kb_lint.py
git diff --check
git add bundle/log.md bundle/projects/explainer-audiobooks.md bundle/status/index.md bundle/status/2026-07-12-adaptive-audiobook-cover-spec-design.md
git commit -m "docs: record adaptive cover implementation"
git fetch origin
git rebase origin/main
git push -u origin codex/adaptive-cover-spec-implementation-kb
gh pr create --base main --head codex/adaptive-cover-spec-implementation-kb --title "Record adaptive cover implementation" --body "Tier-1 receipt for the tested adaptive cover pipeline and selected Rodents pilot."
```

Check the KB PR's hosted lint/auto-merge run and confirm its final merged or blocked state.

- [ ] **Step 8: Audit every touched worktree**

Run `git status --short --branch` in the implementation worktree, original Explainer Audiobooks checkout, KB receipt worktree, and original KB checkout. Preserve and report the pre-existing untracked Gold Panning directory, `.worktrees/`, and modified KB sync log. Leave every agent-authored repository change committed, pushed, and represented by its PR.

---

## Execution Handoff

Plan execution begins from a fresh worktree/branch named `codex/adaptive-cover-spec-implementation` based on current `origin/main`. Task 8 pauses for Dan's visual selection; Task 9 cannot begin before that response.

Two supported execution modes:

1. **Subagent-Driven (recommended):** use `superpowers:subagent-driven-development`, dispatch a fresh worker per task, and run specification-compliance plus code-quality review between tasks.
2. **Inline Execution:** use `superpowers:executing-plans` in this session, execute in reviewed batches, and stop at the Task 8 selection gate.
