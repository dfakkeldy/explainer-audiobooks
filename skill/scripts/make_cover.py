#!/usr/bin/env python3
"""Generate a clean typographic cover image (PNG) for an explainer audiobook.

Builds the cover as an SVG with the standard library only (full control, no image
library needed), then rasterizes it to PNG using whatever is installed —
rsvg-convert first, then ImageMagick (magick/convert). The background color is
derived deterministically from a seed (default: the title), so each book gets its
own distinct hue while staying reproducible.

If no rasterizer is found, the script writes the .svg next to the requested PNG
path and exits non-zero with a clear message, so the caller can decide whether to
ship the SVG, install a rasterizer, or build the EPUB without a cover.

Example:
  python3 make_cover.py \
    --title "Why It Feels Right" \
    --subtitle "A Beginner's Guide to Apple's Human Interface Guidelines" \
    --author "Dan Fakkeldy" \
    --label "AUDIOBOOK" \
    --out ./dist/cover.png
"""

import argparse
import colorsys
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from xml.sax.saxutils import escape

W, H = 1600, 2560
CX = W // 2
MARGIN = 150
USABLE = W - 2 * MARGIN


def hex_color(h_deg, l, s):
    r, g, b = colorsys.hls_to_rgb((h_deg % 360) / 360.0, l, s)
    return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))


def wrap(text, max_chars):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if len(trial) <= max_chars or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_title(title):
    """Choose a font size and wrapped lines so the title fits nicely (<=3 lines)."""
    for size in (170, 150, 130, 112, 96):
        max_chars = max(6, int(USABLE / (0.56 * size)))
        lines = wrap(title, max_chars)
        if len(lines) <= 3:
            return size, lines
    return 96, wrap(title, max(6, int(USABLE / (0.56 * 96))))[:4]


def build_svg(title, subtitle, author, label, seed):
    hue = int(hashlib.sha256(seed.encode("utf-8")).hexdigest(), 16) % 360
    bg_top = hex_color(hue, 0.17, 0.50)
    bg_bot = hex_color(hue, 0.09, 0.55)
    accent = hex_color((hue + 18) % 360, 0.62, 0.62)
    ink = "#F6F3EE"

    parts = []
    parts.append(
        '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
        'viewBox="0 0 %d %d">' % (W, H, W, H)
    )
    parts.append(
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="0.3" y2="1">'
        '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/>'
        '</linearGradient></defs>' % (bg_top, bg_bot)
    )
    parts.append('<rect width="%d" height="%d" fill="url(#bg)"/>' % (W, H))

    # Echo ripples motif (concentric rings) — evokes sound radiating
    rcx, rcy = 1190, 720
    for i in range(7):
        r = 92 + i * 132
        op = max(0.05, 0.5 - i * 0.07)
        parts.append(
            '<circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" '
            'stroke-width="3" stroke-opacity="%.2f"/>' % (rcx, rcy, r, accent, op)
        )

    # Waveform footer motif (vertical bars of varied height)
    bar_w, gap, base_y = 14, 24, 2470
    heights = [40, 90, 150, 70, 200, 120, 240, 80, 160, 60, 110, 190, 50, 130, 210,
               90, 150, 70, 40, 100, 170, 60, 120, 30]
    n = (USABLE) // (bar_w + gap)
    x = MARGIN
    for i in range(int(n)):
        hgt = heights[i % len(heights)]
        parts.append(
            '<rect x="%d" y="%d" width="%d" height="%d" rx="6" fill="%s" '
            'fill-opacity="0.22"/>' % (x, base_y - hgt, bar_w, hgt, accent)
        )
        x += bar_w + gap

    # Top label
    if label:
        parts.append(
            '<text x="%d" y="380" text-anchor="middle" fill="%s" '
            'font-family="Helvetica, Arial, sans-serif" font-size="44" '
            'font-weight="700" letter-spacing="14">%s</text>'
            % (CX, accent, escape(label.upper()))
        )
        parts.append(
            '<line x1="%d" y1="440" x2="%d" y2="440" stroke="%s" '
            'stroke-width="3" stroke-opacity="0.7"/>' % (CX - 90, CX + 90, accent)
        )

    # Title
    size, lines = fit_title(title)
    line_h = int(size * 1.06)
    ty = 1080 if len(lines) <= 2 else 1000
    for ln in lines:
        parts.append(
            '<text x="%d" y="%d" text-anchor="middle" fill="%s" '
            'font-family="Georgia, \'Times New Roman\', serif" font-size="%d" '
            'font-weight="700">%s</text>' % (CX, ty, ink, size, escape(ln))
        )
        ty += line_h

    # Subtitle
    if subtitle:
        sub_lines = wrap(subtitle, 46)[:4]
        sy = ty + 90
        for ln in sub_lines:
            parts.append(
                '<text x="%d" y="%d" text-anchor="middle" fill="%s" '
                'font-family="Georgia, \'Times New Roman\', serif" font-size="52" '
                'font-style="italic" fill-opacity="0.82">%s</text>'
                % (CX, sy, ink, escape(ln))
            )
            sy += 70

    # Author
    if author:
        parts.append(
            '<line x1="%d" y1="2300" x2="%d" y2="2300" stroke="%s" '
            'stroke-width="2" stroke-opacity="0.5"/>' % (CX - 140, CX + 140, ink)
        )
        parts.append(
            '<text x="%d" y="2372" text-anchor="middle" fill="%s" '
            'font-family="Helvetica, Arial, sans-serif" font-size="46" '
            'letter-spacing="3" fill-opacity="0.88">%s</text>'
            % (CX, ink, escape("by " + author))
        )

    parts.append("</svg>")
    return "\n".join(parts)


def rasterize(svg_path, png_path):
    """Try available rasterizers in order. Return True on success."""
    if shutil.which("rsvg-convert"):
        r = subprocess.run(["rsvg-convert", "-w", str(W), "-h", str(H),
                            svg_path, "-o", png_path])
        if r.returncode == 0 and os.path.exists(png_path):
            return True
    for im in ("magick", "convert"):
        if shutil.which(im):
            r = subprocess.run([im, "-background", "none", svg_path,
                                "-resize", "%dx%d" % (W, H), png_path])
            if r.returncode == 0 and os.path.exists(png_path):
                return True
    return False


def main():
    ap = argparse.ArgumentParser(description="Generate a typographic audiobook cover PNG.")
    ap.add_argument("--title", required=True)
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--author", default="")
    ap.add_argument("--label", default="AUDIOBOOK")
    ap.add_argument("--seed", default="", help="Hue seed; defaults to the title")
    ap.add_argument("--out", required=True, help="Output PNG path")
    a = ap.parse_args()

    svg = build_svg(a.title, a.subtitle, a.author, a.label, a.seed or a.title)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)

    with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False, encoding="utf-8") as f:
        f.write(svg)
        svg_tmp = f.name

    try:
        if rasterize(svg_tmp, a.out):
            print("COVER:", a.out)
            return 0
        # No rasterizer — keep the SVG beside the requested path
        svg_out = os.path.splitext(a.out)[0] + ".svg"
        with open(svg_out, "w", encoding="utf-8") as f:
            f.write(svg)
        sys.stderr.write(
            "No rasterizer found (install librsvg's rsvg-convert or ImageMagick).\n"
            "Wrote SVG instead: " + svg_out + "\n")
        return 2
    finally:
        try:
            os.unlink(svg_tmp)
        except OSError:
            pass


if __name__ == "__main__":
    sys.exit(main())
