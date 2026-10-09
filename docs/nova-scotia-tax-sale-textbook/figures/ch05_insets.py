"""Chapter 5 screenshot figures (plan: design/chapter-plan.md, Chapter 5; open question Q16).

    python3 figures/ch05_insets.py          # needs Pillow (system python3 has it)

The 14 NS Marks The Spot screenshots (figure-41 to figure-54, 2560 x 1440, captured July 22, 2026)
are KEEP figures. Each is first copied, byte for byte, into src/assets/figures/kept/ under its
textbook id. Where the plan asks for a magnified inset, a second file `<id>-inset.png` is built:

- the untouched screenshot on top (pixels unchanged; no callout is drawn over it);
- outside its frame, a numbered bracket under the bottom edge (the inset's horizontal range) and a
  numbered bracket in a right-hand gutter (its vertical range);
- below, the inset(s): pure crops of the same PNG, scaled up with one uniform factor, framed by a
  thin teal rule and tagged with the same number.

Privacy (design brief, "What the edition must leave out"): crops are chosen so that no inset
magnifies a civic address or an eight-digit identifier other than the five the original prints.
The screenshots themselves are unchanged and keep the Province attribution in their footer.
"""
from pathlib import Path
import hashlib
import shutil

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parent.parent
SRC = REPO / "docs/nova-scotia-tax-sale-book/chapters/images"
OUT = ROOT / "src/assets/figures/kept"
FONT = ImageFont.truetype(str(ROOT / "fonts/static/sans-700-latin.ttf"), 46)

ACCENT = (31, 85, 96)
WHITE = (255, 255, 255)
RULE = (207, 202, 192)

# textbook id -> (original file, [crop boxes in original pixels: x0, y0, x1, y1])
FIGS = {
    "fig-05-map-layer-overview": ("figure-41-map-layer-overview.png",
                                  [(8, 355, 300, 655), (8, 680, 300, 980)]),
    "fig-05-province-data-licence": ("figure-42-province-data-licence.png",
                                     [(1000, 390, 1560, 790), (1000, 790, 1560, 1050)]),
    "fig-05-current-parcel-browser": ("figure-43-current-parcel-browser.png",
                                      [(8, 645, 300, 900), (8, 925, 300, 1160)]),
    "fig-05-civic-address-search": ("figure-44-civic-address-search.png", []),
    "fig-05-current-parcel-evidence": ("figure-45-current-parcel-evidence.png", []),
    "fig-05-aerial-and-property-boundaries": ("figure-46-aerial-and-property-boundaries.png", []),
    "fig-05-buildings-assessment": ("figure-52-buildings-assessment.png",
                                    [(2160, 100, 2510, 500), (2160, 515, 2510, 905)]),
    "fig-05-roads-water-context": ("figure-47-roads-water-context.png",
                                   [(2165, 960, 2510, 1185)]),
    "fig-05-flood-hazard-evidence": ("figure-53-flood-hazard-evidence.png",
                                     [(2170, 675, 2510, 940), (2170, 940, 2510, 1095)]),
    "fig-05-geology-resources": ("figure-48-geology-resources.png", []),
    "fig-05-historical-outcomes-overview": ("figure-49-historical-outcomes-overview.png", []),
    "fig-05-historical-outcome-sheet": ("figure-50-historical-outcome-sheet.png",
                                        [(2180, 372, 2510, 425), (2180, 625, 2510, 935)]),
    "fig-05-cbrm-outcome-unknown": ("figure-54-cbrm-outcome-unknown.png",
                                    [(2180, 405, 2510, 452), (2180, 656, 2510, 985)]),
    "fig-05-combined-parcel-research": ("figure-51-combined-parcel-research.png", []),
}

GUTTER = 90          # right-hand gutter for the vertical brackets
BELOW = 160          # band under the screenshot: brackets, then the insets' number tags
GAP = 60             # between insets
MAX_INSET_H = 1000   # composite pixels (about 260 px at 7 in print width)


def tag(d, x, y, n):
    d.rectangle([x, y, x + 58, y + 58], fill=ACCENT)
    d.text((x + 29, y + 30), str(n), font=FONT, fill=WHITE, anchor="mm")


def composite(src: Path, boxes, out: Path):
    shot = Image.open(src).convert("RGB")
    W, H = shot.size
    crops = [shot.crop(b) for b in boxes]
    avail = W + GUTTER - GAP * (len(crops) - 1) - 16
    scale = min(avail / sum(c.width for c in crops), MAX_INSET_H / max(c.height for c in crops))
    scaled = [c.resize((round(c.width * scale), round(c.height * scale)), Image.LANCZOS)
              for c in crops]
    inset_h = max(s.height for s in scaled)
    total = Image.new("RGB", (W + GUTTER, H + BELOW + inset_h + 16), WHITE)
    total.paste(shot, (0, 0))
    d = ImageDraw.Draw(total)
    d.rectangle([0, 0, W - 1, H - 1], outline=RULE, width=2)
    placed = []
    for i, (x0, y0, x1, y1) in enumerate(boxes, 1):
        # horizontal bracket under the frame; tags of brackets that share a range sit side by side
        by = H + 18
        d.line([x0, by, x1, by], fill=ACCENT, width=6)
        d.line([x0, H + 4, x0, by], fill=ACCENT, width=6)
        d.line([x1, H + 4, x1, by], fill=ACCENT, width=6)
        tx = min(max((x0 + x1) // 2 - 29, 0), W + GUTTER - 60)
        while any(abs(tx - p) < 66 for p in placed):
            tx += 66
        placed.append(tx)
        tag(d, tx, by + 8, i)
        # vertical bracket in the gutter
        gx = W + 18
        d.line([gx, y0, gx, y1], fill=ACCENT, width=6)
        d.line([W + 4, y0, gx, y0], fill=ACCENT, width=6)
        d.line([W + 4, y1, gx, y1], fill=ACCENT, width=6)
        tag(d, gx + 8, (y0 + y1) // 2 - 29, i)
    used = sum(s.width for s in scaled) + GAP * (len(scaled) - 1)
    x = (W + GUTTER - used) // 2
    top = H + BELOW
    for i, s in enumerate(scaled, 1):
        total.paste(s, (x, top))
        d.rectangle([x - 3, top - 3, x + s.width + 2, top + s.height + 2], outline=ACCENT, width=4)
        tag(d, x - 3, top - 64, i)   # above the inset, never over its pixels
        x += s.width + GAP
    total.save(out, optimize=True)
    return scale


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for fid, (name, boxes) in FIGS.items():
        src = SRC / name
        dst = OUT / f"{fid}.png"
        shutil.copyfile(src, dst)
        assert hashlib.sha256(src.read_bytes()).digest() == hashlib.sha256(dst.read_bytes()).digest()
        msg = f"copied {name} -> kept/{dst.name}"
        if boxes:
            s = composite(src, boxes, OUT / f"{fid}-inset.png")
            msg += f"; inset x{s:.2f}"
        print(msg)


if __name__ == "__main__":
    main()
