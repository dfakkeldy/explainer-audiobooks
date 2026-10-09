"""Small helper for the textbook's figures (spec: design/figure-style.md).

Run with the project venv (it needs fontTools):  .venv/bin/python figures/<script>.py

    from svgkit import Canvas, C
    c = Canvas(672, 300)
    c.box(16, 16, 200, 60, fill=C.accent_tint, stroke=C.accent)
    c.text_block(28, 30, 176, "Preliminary notice: at least 14 days to pay", size=12)
    c.arrow(216, 46, 300, 46)
    c.save("src/assets/figures/fig-01-example.svg")

Text is measured with the real font metrics, so wrapping and the overlap check are exact enough
for layout. `save()` embeds a glyph subset of the two sans weights as data URIs and runs `check()`.
"""
from __future__ import annotations

import base64
import io
import math
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONT_FILES = {400: ROOT / "fonts/static/sans-400-latin.ttf",
              700: ROOT / "fonts/static/sans-700-latin.ttf"}
FAMILY = "Atkinson Hyperlegible Next"
FONT_STACK = f"'{FAMILY}', 'Atkinson Hyperlegible', sans-serif"
MIN_SIZE = 11


class C:
    ink = "#1d1c1a"
    ink2 = "#4a4843"
    rule = "#cfcac0"
    accent = "#1f5560"
    accent_tint = "#e6eef0"
    accent_mid = "#9db8bf"
    caution = "#a33b28"
    caution_tint = "#f6e8e3"
    granite = "#6b6a66"
    paper2 = "#f3f1ec"
    white = "#ffffff"
    # evidence states
    municipal = "#24395a"
    verified = "#1f6b6e"
    screening = "#b07d17"
    unresolved = "#7a3e6e"
    nogo = "#a33b28"
    complete = "#2f5e46"


DASH = "6 4"
DOT = "1.5 2.5"

_fonts: dict[int, TTFont] = {}


def _font(weight: int) -> TTFont:
    w = 700 if weight >= 600 else 400
    if w not in _fonts:
        _fonts[w] = TTFont(FONT_FILES[w])
    return _fonts[w]


def width(text: str, size: float, weight: int = 400) -> float:
    f = _font(weight)
    cmap = f.getBestCmap()
    hmtx = f["hmtx"]
    upm = f["head"].unitsPerEm
    total = 0
    for ch in text:
        g = cmap.get(ord(ch)) or cmap.get(ord("?"))
        total += hmtx[g][0]
    return total * size / upm


def wrap(text: str, size: float, maxw: float, weight: int = 400) -> list[str]:
    lines: list[str] = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split(" "):
            trial = f"{cur} {word}".strip()
            if cur and width(trial, size, weight) > maxw:
                lines.append(cur)
                cur = word
            else:
                cur = trial
        lines.append(cur)
    return lines


def _f(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".")


class Canvas:
    def __init__(self, w: int, h: int, title: str = "", desc: str = ""):
        self.w, self.h = w, h
        self.title, self.desc = title, desc
        self.items: list[str] = []
        self.texts: list[tuple] = []      # (x0, y0, x1, y1, size, text, tag)
        self.chars = {400: set(), 700: set()}
        self.markers: set[str] = set()

    # ---------------------------------------------------------------- shapes
    def raw(self, s: str):
        self.items.append(s)

    def rect(self, x, y, w, h, fill="none", stroke="none", sw=1.5, dash=None, rx=0, extra=""):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.items.append(
            f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" rx="{_f(rx)}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{_f(sw)}"{d}{extra}/>')

    def box(self, x, y, w, h, fill=C.white, stroke=C.accent, sw=1.5, dash=None, tab=None, rx=3):
        """A labelled box. tab=colour draws the municipal-fact solid tab on the left edge."""
        self.rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, dash=dash, rx=rx)
        if tab:
            self.rect(x, y, 6, h, fill=tab)

    def line(self, x1, y1, x2, y2, color=C.accent, sw=1.5, dash=None, cap="butt"):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.items.append(
            f'<line x1="{_f(x1)}" y1="{_f(y1)}" x2="{_f(x2)}" y2="{_f(y2)}" stroke="{color}" '
            f'stroke-width="{_f(sw)}" stroke-linecap="{cap}"{d}/>')

    def path(self, d, fill="none", stroke=C.accent, sw=1.5, dash=None, extra=""):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.items.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{_f(sw)}" '
                          f'stroke-linejoin="round"{da}{extra}/>')

    def circle(self, cx, cy, r, fill=C.accent, stroke="none", sw=1.5):
        self.items.append(f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r)}" fill="{fill}" '
                          f'stroke="{stroke}" stroke-width="{_f(sw)}"/>')

    def arrow(self, x1, y1, x2, y2, color=C.accent, sw=1.5, dash=None, gap=3):
        """Straight arrow; the head stops `gap` units before (x2, y2)."""
        L = math.hypot(x2 - x1, y2 - y1)
        ex, ey = x2 - (x2 - x1) / L * gap, y2 - (y2 - y1) / L * gap
        self.arrow_path(f"M{_f(x1)},{_f(y1)} L{_f(ex)},{_f(ey)}", color, sw, dash)

    def arrow_path(self, d, color=C.accent, sw=1.5, dash=None):
        mid = "arrow-" + color.lstrip("#")
        self.markers.add(color)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.items.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{_f(sw)}" '
                          f'stroke-linejoin="round"{da} marker-end="url(#{mid})"/>')

    # ---------------------------------------------------------------- glyphs
    def glyph(self, kind, x, y, color):
        """State glyphs, centred on (x, y), 12 units across: question, bar, check."""
        if kind == "question":
            self.circle(x, y, 7, fill=C.white, stroke=color, sw=1.5)
            self.text(x, y + 4, "?", size=11, weight=700, color=color, anchor="middle", tag="glyph")
        elif kind == "bar":
            self.rect(x - 7, y - 2, 14, 4, fill=color)
        elif kind == "check":
            self.path(f"M{x-5},{y} L{x-1.5},{y+4} L{x+5.5},{y-4}", stroke=color, sw=2.25)

    # ---------------------------------------------------------------- text
    def text(self, x, y, s, size=12, weight=400, color=C.ink, anchor="start", tag="", italic=False):
        if size < MIN_SIZE:
            raise ValueError(f"text below {MIN_SIZE}: {s!r}")
        w = width(s, size, weight)
        x0 = {"start": x, "middle": x - w / 2, "end": x - w}[anchor]
        self.texts.append((x0, y - size * 0.78, x0 + w, y + size * 0.22, size, s, tag))
        self.chars[700 if weight >= 600 else 400].update(s)
        st = ' font-style="italic"' if italic else ""
        self.items.append(
            f'<text x="{_f(x)}" y="{_f(y)}" font-size="{_f(size)}" font-weight="{weight}" '
            f'fill="{color}" text-anchor="{anchor}"{st}>{escape(s)}</text>')

    def text_block(self, x, y, maxw, s, size=12, weight=400, color=C.ink, anchor="start",
                   lh=1.3, tag=""):
        """Wrapped text; y is the first baseline. Returns the y of the next free baseline."""
        lines = wrap(s, size, maxw, weight)
        for i, ln in enumerate(lines):
            self.text(x, y + i * size * lh, ln, size, weight, color, anchor, tag)
        return y + len(lines) * size * lh

    def block_height(self, s, size, maxw, weight=400, lh=1.3):
        return len(wrap(s, size, maxw, weight)) * size * lh

    # ---------------------------------------------------------------- output
    def check(self, allow_overlap: set[tuple[str, str]] | None = None) -> list[str]:
        problems = []
        for (x0, y0, x1, y1, size, s, _) in self.texts:
            if x0 < 4 or y0 < 4 or x1 > self.w - 4 or y1 > self.h - 4:
                problems.append(f"near or outside the edge: {s!r} ({x0:.0f},{y0:.0f},{x1:.0f},{y1:.0f})")
        for i, a in enumerate(self.texts):
            for b in self.texts[i + 1:]:
                if a[0] < b[2] - 0.5 and b[0] < a[2] - 0.5 and a[1] < b[3] - 0.5 and b[1] < a[3] - 0.5:
                    problems.append(f"text overlap: {a[5]!r} / {b[5]!r}")
        return problems

    def _font_face(self) -> str:
        out = []
        for w, chars in self.chars.items():
            if not chars:
                continue
            opts = subset.Options()
            opts.flavor = "woff2"
            opts.layout_features = ["kern", "liga"]
            f = TTFont(FONT_FILES[w])
            sub = subset.Subsetter(opts)
            sub.populate(text="".join(sorted(chars | {" "})))
            sub.subset(f)
            buf = io.BytesIO()
            f.flavor = "woff2"
            f.save(buf)
            b64 = base64.b64encode(buf.getvalue()).decode()
            out.append(f"@font-face{{font-family:'{FAMILY}';font-weight:{w};"
                       f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}")
        return "".join(out)

    def svg(self) -> str:
        markers = "".join(
            f'<marker id="arrow-{c.lstrip("#")}" viewBox="0 0 8 8" refX="8" refY="4" '
            f'markerWidth="8" markerHeight="8" markerUnits="userSpaceOnUse" orient="auto">'
            f'<path d="M0,0 L8,4 L0,8 Z" fill="{c}"/></marker>' for c in sorted(self.markers))
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
                f'width="{self.w}" height="{self.h}" role="img" font-family="{FONT_STACK}">')
        meta = ""
        if self.title:
            meta += f"<title>{escape(self.title)}</title>"
        if self.desc:
            meta += f"<desc>{escape(self.desc)}</desc>"
        style = f"<style>{self._font_face()}</style>"
        ground = f'<rect width="{self.w}" height="{self.h}" fill="#ffffff"/>'
        return (head + meta + f"<defs>{style}{markers}</defs>" + ground + "\n".join(self.items)
                + "</svg>\n")

    def save(self, path, allow_problems=False):
        problems = self.check()
        for p in problems:
            print("  !", p)
        if problems and not allow_problems:
            raise SystemExit(f"{path}: {len(problems)} layout problem(s)")
        Path(path).write_text(self.svg())
        print("wrote", path)
