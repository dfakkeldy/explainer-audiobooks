#!/usr/bin/env python3
"""Generate a bestseller-style cover image (PNG) for an explainer audiobook.

The cover is composed as an SVG with the standard library only (full control, no
image library needed), then rasterized to PNG with whatever is installed —
rsvg-convert first, then ImageMagick (magick/convert).

What makes a cover "show what the book is about" is a bespoke illustration. There
is no text-to-image tool here, so the illustration is authored as vector art (an
SVG file) tailored to THIS book, and passed in with --art. This script places that
art into a premium layout and sets the title/subtitle/author/badge around it. The
background hue is still derived from a seed (default: the title) so each book keeps
its own identity even before the art loads.

Two layouts:
  --layout bleed   the illustration fills the cover; a gradient scrim across the
                   lower third carries the title (the classic trade-paperback look).
  --layout hero    the illustration sits in a framed panel up top; the title block
                   sits on the background below it.

If no --art is given, a restrained abstract motif is drawn so the script still
produces a usable cover.

If no rasterizer is found, the .svg is written next to the requested PNG path and
the script exits non-zero, so the caller can install a rasterizer or ship the SVG.

Example:
  python3 make_cover.py \
    --title "You Are the Architect" \
    --subtitle "Vibe-Coding Real iOS Apps with Claude Code" \
    --author "Dan Fakkeldy" --label "AUDIOBOOK" \
    --art ./art.svg --layout bleed \
    --out ./dist/cover.png
"""

import argparse
import colorsys
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from xml.sax.saxutils import escape

W, H = 1600, 2560
CX = W // 2
MARGIN = 140
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


def fit_title(title, sizes):
    """Pick the largest font size from `sizes` that wraps the title to <=3 lines."""
    for size in sizes:
        max_chars = max(6, int(USABLE / (0.55 * size)))
        lines = wrap(title, max_chars)
        if len(lines) <= 3:
            return size, lines
    size = sizes[-1]
    return size, wrap(title, max(6, int(USABLE / (0.55 * size))))[:3]


def load_art(path):
    """Return (viewBox, inner_xml) from an SVG illustration file."""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    m = re.search(r'viewBox="([^"]+)"', text)
    vb = m.group(1) if m else "0 0 1000 1000"
    inner = re.sub(r"^.*?<svg[^>]*>", "", text, count=1, flags=re.S)
    inner = re.sub(r"</svg>\s*$", "", inner, count=1, flags=re.S)
    return vb, inner


def embed_art(vb, inner, x, y, w, h, preserve="xMidYMid meet"):
    return (
        f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="{vb}" '
        f'preserveAspectRatio="{preserve}">{inner}</svg>'
    )


def default_motif(accent):
    """A restrained fallback when no bespoke art is supplied: soft concentric arcs."""
    p = [f'<svg x="0" y="0" width="{W}" height="1500" viewBox="0 0 {W} 1500" '
         'preserveAspectRatio="xMidYMid meet">']
    cx, cy = CX, 720
    for i in range(8):
        r = 120 + i * 150
        op = max(0.05, 0.45 - i * 0.05)
        p.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" '
                 f'stroke="{accent}" stroke-width="4" stroke-opacity="{op:.2f}"/>')
    p.append("</svg>")
    return "\n".join(p)


def badge(label, accent, ink, y):
    if not label:
        return ""
    return (
        f'<text x="{CX}" y="{y}" text-anchor="middle" fill="{accent}" '
        'font-family="Helvetica, Arial, sans-serif" font-size="40" '
        f'font-weight="700" letter-spacing="13">{escape(label.upper())}</text>'
        f'<line x1="{CX - 78}" y1="{y + 38}" x2="{CX + 78}" y2="{y + 38}" '
        f'stroke="{accent}" stroke-width="3" stroke-opacity="0.75"/>'
    )


def title_block(title, subtitle, author, ink, accent, top_y, sizes):
    parts = []
    size, lines = fit_title(title, sizes)
    line_h = int(size * 1.04)
    ty = top_y
    for ln in lines:
        parts.append(
            f'<text x="{CX}" y="{ty}" text-anchor="middle" fill="{ink}" '
            'font-family="Georgia, \'Times New Roman\', serif" '
            f'font-size="{size}" font-weight="700">{escape(ln)}</text>'
        )
        ty += line_h
    if subtitle:
        sy = ty + 24
        for ln in wrap(subtitle, 44)[:3]:
            parts.append(
                f'<text x="{CX}" y="{sy}" text-anchor="middle" fill="{ink}" '
                'font-family="Georgia, \'Times New Roman\', serif" font-size="50" '
                f'font-style="italic" fill-opacity="0.85">{escape(ln)}</text>'
            )
            sy += 66
        ty = sy
    if author:
        parts.append(
            f'<line x1="{CX - 130}" y1="2326" x2="{CX + 130}" y2="2326" '
            f'stroke="{ink}" stroke-width="2" stroke-opacity="0.45"/>'
            f'<text x="{CX}" y="2398" text-anchor="middle" fill="{ink}" '
            'font-family="Helvetica, Arial, sans-serif" font-size="44" '
            f'letter-spacing="3" fill-opacity="0.9">{escape("by " + author)}</text>'
        )
    return "\n".join(parts)


def build_svg(title, subtitle, author, label, seed, art_path, layout):
    hue = int(hashlib.sha256(seed.encode("utf-8")).hexdigest(), 16) % 360
    accent = hex_color((hue + 16) % 360, 0.62, 0.62)
    ink = "#F6F3EE"
    art = load_art(art_path) if art_path else None

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}">'
    ]

    if layout == "bleed":
        bg_top = hex_color(hue, 0.13, 0.45)
        bg_bot = hex_color(hue, 0.07, 0.5)
        parts.append(
            '<defs>'
            f'<linearGradient id="coverbg" x1="0" y1="0" x2="0.25" y2="1">'
            f'<stop offset="0" stop-color="{bg_top}"/>'
            f'<stop offset="1" stop-color="{bg_bot}"/></linearGradient>'
            f'<linearGradient id="scrim" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{bg_bot}" stop-opacity="0"/>'
            f'<stop offset="0.32" stop-color="{bg_bot}" stop-opacity="0.82"/>'
            f'<stop offset="0.55" stop-color="{bg_bot}" stop-opacity="1"/>'
            '</linearGradient></defs>'
        )
        parts.append(f'<rect width="{W}" height="{H}" fill="url(#coverbg)"/>')
        # Illustration fills the upper region, bleeding to the edges (slice = fill).
        if art:
            parts.append(embed_art(art[0], art[1], 0, 0, W, 1860,
                                   preserve="xMidYMid slice"))
        else:
            parts.append(default_motif(accent))
        # Scrim carries the title over the lower third.
        parts.append(f'<rect x="0" y="1500" width="{W}" height="{H - 1500}" fill="url(#scrim)"/>')
        parts.append(badge(label, accent, ink, 1760))
        parts.append(title_block(title, subtitle, author, ink, accent, 1940,
                                 sizes=(150, 132, 116, 100)))

    else:  # hero
        bg_top = hex_color(hue, 0.16, 0.5)
        bg_bot = hex_color(hue, 0.09, 0.55)
        panel = hex_color(hue, 0.11, 0.45)
        parts.append(
            '<defs>'
            f'<linearGradient id="coverbg" x1="0" y1="0" x2="0.3" y2="1">'
            f'<stop offset="0" stop-color="{bg_top}"/>'
            f'<stop offset="1" stop-color="{bg_bot}"/></linearGradient></defs>'
        )
        parts.append(f'<rect width="{W}" height="{H}" fill="url(#coverbg)"/>')
        parts.append(badge(label, accent, ink, 300))
        # Framed illustration panel.
        px, py, pw, ph = 130, 420, W - 260, 1180
        parts.append(
            f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="40" '
            f'fill="{panel}" stroke="{accent}" stroke-width="3" stroke-opacity="0.5"/>'
        )
        if art:
            pad = 70
            parts.append(embed_art(art[0], art[1], px + pad, py + pad,
                                   pw - 2 * pad, ph - 2 * pad))
        else:
            parts.append(default_motif(accent))
        parts.append(title_block(title, subtitle, author, ink, accent, 1830,
                                 sizes=(140, 124, 108, 94)))

    parts.append("</svg>")
    return "\n".join(parts)


def rasterize(svg_path, png_path):
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
    ap = argparse.ArgumentParser(description="Generate a bestseller-style audiobook cover PNG.")
    ap.add_argument("--title", required=True)
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--author", default="")
    ap.add_argument("--label", default="AUDIOBOOK")
    ap.add_argument("--seed", default="", help="Hue seed; defaults to the title")
    ap.add_argument("--art", default="", help="SVG illustration file for this book")
    ap.add_argument("--layout", default="bleed", choices=("bleed", "hero"))
    ap.add_argument("--out", required=True, help="Output PNG path")
    a = ap.parse_args()

    svg = build_svg(a.title, a.subtitle, a.author, a.label, a.seed or a.title,
                    a.art or None, a.layout)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)

    with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False, encoding="utf-8") as f:
        f.write(svg)
        svg_tmp = f.name

    try:
        if rasterize(svg_tmp, a.out):
            print("COVER:", a.out)
            return 0
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
