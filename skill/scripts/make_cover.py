#!/usr/bin/env python3
"""Generate a bestseller-style cover image (PNG) for an explainer audiobook.

The cover is composed as an SVG with the standard library only (full control, no
image library needed), then rasterized to PNG with whatever is installed —
rsvg-convert first, then ImageMagick (magick/convert).

What makes a cover "show what the book is about" is original, book-specific art.
Pass either a self-contained SVG illustration or high-resolution PNG/JPEG/WebP/GIF
art with `--art`; raster art is embedded as a data URI so the composed SVG remains
portable. This script places the art into a premium layout and sets the
title/subtitle/author/badge around it. The background hue is derived from --accent
when provided, otherwise from a seed (default: the title). Use --accent to carry
the cover art's signature colour into the final layout so library UIs have a
strong colour to derive from the cover.

Two layouts:
  --layout bleed   the illustration fills the cover; a gradient scrim across the
                   lower third carries the title (the classic trade-paperback look).
  --layout hero    the illustration sits in a framed panel up top; the title block
                   sits on the background below it.

Two tones:
  --tone bright    high-key, bright marketplace cover background (default).
  --tone dark      deep, cinematic cover background (explicit opt-in).

If no --art is given, a restrained abstract motif is drawn so the script still
produces a usable cover.

If no rasterizer is found, the .svg is written next to the requested PNG path and
the script exits non-zero, so the caller can install a rasterizer or ship the SVG.

Example:
  python3 make_cover.py \
    --title "You Are the Architect" \
    --subtitle "Vibe-Coding Real iOS Apps with Claude Code" \
    --author "Dan Fakkeldy" --label "AUDIOBOOK" \
    --art ./art.svg --accent "#2ee8b6" --tone bright --layout bleed \
    --out ./dist/cover.png
"""

import argparse
import base64
import colorsys
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape

from cover_renderer import CoverRenderError, render_cover_spec
from cover_spec import CoverSpecError

W, H = 1600, 2560
CX = W // 2
MARGIN = 140
USABLE = W - 2 * MARGIN


@dataclass(frozen=True)
class Art:
    """Self-contained vector or raster artwork suitable for embedding in the cover SVG."""

    kind: str
    viewbox: str
    content: str


RASTER_MIME_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
}


def hex_color(h_deg, l, s):
    r, g, b = colorsys.hls_to_rgb((h_deg % 360) / 360.0, l, s)
    return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))


def parse_hex_color(value):
    """Normalize #RRGGBB input for the deliberate cover accent."""
    if not value:
        return ""
    m = re.fullmatch(r"#?([0-9a-fA-F]{6})", value.strip())
    if not m:
        raise argparse.ArgumentTypeError("accent must be a hex RGB colour like #2ee8b6")
    return "#" + m.group(1).lower()


def hue_from_hex(value):
    r = int(value[1:3], 16) / 255.0
    g = int(value[3:5], 16) / 255.0
    b = int(value[5:7], 16) / 255.0
    h, _l, _s = colorsys.rgb_to_hls(r, g, b)
    return h * 360


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
    """Return self-contained SVG or raster artwork for placement on the cover.

    SVG preserves editable vector geometry. PNG/JPEG/WebP/GIF files are encoded as
    data URIs so the temporary composition SVG remains portable when rasterized.
    """
    suffix = os.path.splitext(os.fspath(path))[1].lower()
    if suffix in RASTER_MIME_TYPES:
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("ascii")
        return Art("raster", "", f"data:{RASTER_MIME_TYPES[suffix]};base64,{encoded}")

    if suffix and suffix != ".svg":
        raise ValueError("art must be SVG, PNG, JPEG, WebP, or GIF")
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    m = re.search(r'viewBox="([^"]+)"', text)
    vb = m.group(1) if m else "0 0 1000 1000"
    inner = re.sub(r"^.*?<svg[^>]*>", "", text, count=1, flags=re.S)
    inner = re.sub(r"</svg>\s*$", "", inner, count=1, flags=re.S)
    return Art("svg", vb, inner)


def embed_art(art, x, y, w, h, preserve="xMidYMid meet"):
    if art.kind == "raster":
        return (
            f'<image href="{art.content}" x="{x}" y="{y}" width="{w}" height="{h}" '
            f'preserveAspectRatio="{preserve}"/>'
        )
    return (
        f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="{art.viewbox}" '
        f'preserveAspectRatio="{preserve}">{art.content}</svg>'
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


def accent_signature(accent, layout):
    """Visible accent treatment so the cover's derived colour has real signal."""
    if layout == "bleed":
        return (
            f'<path d="M0 0 H{W} V30 H0 Z" fill="{accent}" opacity="0.95"/>'
            f'<path d="M0 0 H38 V{H} H0 Z" fill="{accent}" opacity="0.86"/>'
            f'<path d="M{W} 0 V620 L{W - 270} 0 Z" fill="{accent}" opacity="0.18"/>'
        )
    return (
        f'<path d="M0 0 H{W} V34 H0 Z" fill="{accent}" opacity="0.95"/>'
        f'<path d="M0 {H - 44} H{W} V{H} H0 Z" fill="{accent}" opacity="0.78"/>'
    )


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
    parts.append(
        f'<rect x="{CX - 112}" y="{top_y - 86}" width="224" height="8" rx="4" '
        f'fill="{accent}" fill-opacity="0.95"/>'
    )
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
        # Keep the classic position, but never let the rule strike through a
        # subtitle that wrapped to multiple lines.
        rule_y = max(2326, ty + 30)
        parts.append(
            f'<line x1="{CX - 130}" y1="{rule_y}" x2="{CX + 130}" y2="{rule_y}" '
            f'stroke="{ink}" stroke-width="2" stroke-opacity="0.45"/>'
            f'<text x="{CX}" y="{rule_y + 72}" text-anchor="middle" fill="{ink}" '
            'font-family="Helvetica, Arial, sans-serif" font-size="44" '
            f'letter-spacing="3" fill-opacity="0.9">{escape("by " + author)}</text>'
        )
    return "\n".join(parts)


def build_svg(
    title,
    subtitle,
    author,
    label,
    seed,
    accent_color,
    art_path,
    layout,
    tone,
    include_background=True,
    include_art=True,
    include_overlays=True,
):
    if accent_color:
        hue = (hue_from_hex(accent_color) - 18) % 360
        accent = accent_color
    else:
        hue = int(hashlib.sha256(seed.encode("utf-8")).hexdigest(), 16) % 360
        accent = hex_color((hue + 16) % 360, 0.62, 0.72)
    bright = tone == "bright"
    ink = "#17130F" if bright else "#F6F3EE"
    art = load_art(art_path) if art_path else None

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}">'
    ]

    if layout == "bleed":
        if bright:
            bg_top = hex_color(hue, 0.94, 0.36)
            bg_bot = hex_color(hue, 0.82, 0.42)
            scrim_opacity = "0.94"
            wash_opacity = "0.16"
        else:
            bg_top = hex_color(hue, 0.13, 0.45)
            bg_bot = hex_color(hue, 0.07, 0.5)
            scrim_opacity = "1"
            wash_opacity = "0.20"
        parts.append(
            '<defs>'
            f'<linearGradient id="coverbg" x1="0" y1="0" x2="0.25" y2="1">'
            f'<stop offset="0" stop-color="{bg_top}"/>'
            f'<stop offset="1" stop-color="{bg_bot}"/></linearGradient>'
            f'<linearGradient id="scrim" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{bg_bot}" stop-opacity="0"/>'
            f'<stop offset="0.32" stop-color="{bg_bot}" stop-opacity="0.82"/>'
            f'<stop offset="0.55" stop-color="{bg_bot}" stop-opacity="{scrim_opacity}"/></linearGradient>'
            f'<linearGradient id="accentwash" x1="0" y1="0" x2="1" y2="0.35">'
            f'<stop offset="0" stop-color="{accent}" stop-opacity="{wash_opacity}"/>'
            f'<stop offset="0.34" stop-color="{accent}" stop-opacity="0.07"/>'
            f'<stop offset="1" stop-color="{accent}" stop-opacity="0"/></linearGradient>'
            '</defs>'
        )
        if include_background:
            parts.append(f'<rect width="{W}" height="{H}" fill="url(#coverbg)"/>')
        # Illustration fills the upper region, bleeding to the edges (slice = fill).
        if include_art:
            if art:
                parts.append(embed_art(art, 0, 0, W, 1860,
                                       preserve="xMidYMid slice"))
            else:
                parts.append(default_motif(accent))
        if include_overlays:
            parts.append(f'<rect x="0" y="0" width="{W}" height="1860" fill="url(#accentwash)"/>')
            parts.append(accent_signature(accent, layout))
            # Scrim carries the title over the lower third.
            parts.append(f'<rect x="0" y="1500" width="{W}" height="{H - 1500}" fill="url(#scrim)"/>')
            parts.append(badge(label, accent, ink, 1760))
            parts.append(title_block(title, subtitle, author, ink, accent, 1940,
                                     sizes=(150, 132, 116, 100)))

    else:  # hero
        if bright:
            bg_top = hex_color(hue, 0.94, 0.36)
            bg_bot = hex_color(hue, 0.80, 0.42)
            panel = hex_color(hue, 0.90, 0.28)
            halo_opacity = "0.18"
        else:
            bg_top = hex_color(hue, 0.16, 0.5)
            bg_bot = hex_color(hue, 0.09, 0.55)
            panel = hex_color(hue, 0.11, 0.45)
            halo_opacity = "0.24"
        parts.append(
            '<defs>'
            f'<linearGradient id="coverbg" x1="0" y1="0" x2="0.3" y2="1">'
            f'<stop offset="0" stop-color="{bg_top}"/>'
            f'<stop offset="1" stop-color="{bg_bot}"/></linearGradient>'
            f'<radialGradient id="accenthalo" cx="50%" cy="32%" r="62%">'
            f'<stop offset="0" stop-color="{accent}" stop-opacity="{halo_opacity}"/>'
            f'<stop offset="0.48" stop-color="{accent}" stop-opacity="0.08"/>'
            f'<stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>'
            '</defs>'
        )
        if include_background:
            parts.append(f'<rect width="{W}" height="{H}" fill="url(#coverbg)"/>')
            parts.append(f'<rect width="{W}" height="{H}" fill="url(#accenthalo)"/>')
        if include_overlays and include_background:
            # Keep the original full-cover order: signature and badge sit before
            # the panel/motif, while the title remains the final foreground layer.
            parts.append(accent_signature(accent, layout))
            parts.append(badge(label, accent, ink, 300))
        if include_background:
            # Framed illustration panel.
            px, py, pw, ph = 130, 420, W - 260, 1180
            parts.append(
                f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="40" '
                f'fill="{panel}" stroke="{accent}" stroke-width="5" stroke-opacity="0.72"/>'
            )
        else:
            px, py, pw, ph = 130, 420, W - 260, 1180
        if include_art:
            if art:
                pad = 70
                parts.append(embed_art(art, px + pad, py + pad,
                                       pw - 2 * pad, ph - 2 * pad))
            else:
                parts.append(default_motif(accent))
        if include_overlays:
            if not include_background:
                parts.append(accent_signature(accent, layout))
                parts.append(badge(label, accent, ink, 300))
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


def rasterize_raster_art_cover(
    title,
    subtitle,
    author,
    label,
    seed,
    accent_color,
    art_path,
    layout,
    tone,
    png_path,
):
    """Compose raster art with SVG background/overlay layers through ImageMagick.

    ImageMagick's SVG decoder cannot reliably follow raster `data:` URIs. Render
    the simple vector layers separately, then place the source image between them.
    """
    tool = next((candidate for candidate in ("magick", "convert")
                 if shutil.which(candidate)), None)
    if not tool:
        return False

    def run(args):
        result = subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0

    with tempfile.TemporaryDirectory(prefix="audiobook-cover-") as raw_dir:
        tmp_dir = os.fspath(raw_dir)
        background_svg = os.path.join(tmp_dir, "background.svg")
        overlay_svg = os.path.join(tmp_dir, "overlay.svg")
        background_png = os.path.join(tmp_dir, "background.png")
        fitted_art = os.path.join(tmp_dir, "art.png")
        composed_png = os.path.join(tmp_dir, "composed.png")
        overlay_png = os.path.join(tmp_dir, "overlay.png")

        common = (title, subtitle, author, label, seed, accent_color, "", layout, tone)
        with open(background_svg, "w", encoding="utf-8") as f:
            f.write(build_svg(*common, include_background=True, include_art=False,
                              include_overlays=False))
        with open(overlay_svg, "w", encoding="utf-8") as f:
            f.write(build_svg(*common, include_background=False, include_art=False,
                              include_overlays=True))

        if not run([tool, "-background", "none", background_svg, "-resize",
                    f"{W}x{H}!", background_png]):
            return False
        if not run([tool, "-background", "none", overlay_svg, "-resize",
                    f"{W}x{H}!", overlay_png]):
            return False

        if layout == "bleed":
            art_w, art_h, art_x, art_y = W, 1860, 0, 0
            resize = f"{art_w}x{art_h}^"
        else:
            art_w, art_h, art_x, art_y = 1200, 1040, 200, 490
            resize = f"{art_w}x{art_h}"

        source = os.fspath(art_path) + "[0]"  # Animated GIF covers use the first frame.
        if not run([tool, source, "-auto-orient", "-resize", resize, "-gravity", "center",
                    "-background", "none", "-extent", f"{art_w}x{art_h}", fitted_art]):
            return False
        if not run([tool, background_png, fitted_art, "-geometry",
                    f"+{art_x}+{art_y}", "-composite", composed_png]):
            return False
        if not run([tool, composed_png, overlay_png, "-composite", png_path]):
            return False
        return os.path.exists(png_path) and os.path.getsize(png_path) > 0


def main():
    ap = argparse.ArgumentParser(description="Generate a bestseller-style audiobook cover PNG.")
    ap.add_argument("--spec", default="", help="Validated cover-specification JSON")
    ap.add_argument("--title", default="")
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--author", default="")
    ap.add_argument("--label", default="AUDIOBOOK")
    ap.add_argument("--seed", default="", help="Hue seed; defaults to the title")
    ap.add_argument("--accent", default="", type=parse_hex_color,
                    help="Signature cover-art accent as #RRGGBB; defaults to seed-derived")
    ap.add_argument("--art", default="", help="SVG, PNG, JPEG, WebP, or GIF art for this book")
    ap.add_argument("--tone", default="bright", choices=("dark", "bright"),
                    help="Cover background tone; defaults to bright; use dark for cinematic covers")
    ap.add_argument("--layout", default="bleed", choices=("bleed", "hero"))
    ap.add_argument("--out", required=True, help="Output PNG path")
    a = ap.parse_args()

    legacy_flags = {
        "--title",
        "--subtitle",
        "--author",
        "--label",
        "--seed",
        "--accent",
        "--art",
        "--tone",
        "--layout",
    }
    arguments = sys.argv[1:]
    provided = {
        flag
        for flag in legacy_flags
        if any(argument == flag or argument.startswith(f"{flag}=") for argument in arguments)
    }
    spec_requested = any(
        argument == "--spec" or argument.startswith("--spec=")
        for argument in arguments
    )
    if spec_requested:
        if provided:
            ap.error("--spec cannot be combined with legacy cover flags")
        if not a.spec:
            ap.error("--spec requires a non-empty path")
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

    os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)

    art_suffix = os.path.splitext(a.art)[1].lower() if a.art else ""
    if art_suffix in RASTER_MIME_TYPES:
        if rasterize_raster_art_cover(
            a.title,
            a.subtitle,
            a.author,
            a.label,
            a.seed or a.title,
            a.accent,
            a.art,
            a.layout,
            a.tone,
            a.out,
        ):
            print("COVER:", a.out)
            return 0

    svg = build_svg(a.title, a.subtitle, a.author, a.label, a.seed or a.title,
                    a.accent, a.art or None, a.layout, a.tone)

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
