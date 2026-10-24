#!/usr/bin/env python3
"""Place figures in the chapters from design/figures.yaml.

A marker line `<!-- figure: ID -->`, or an image line already pointing at
../assets/figures/ID.(png|jpg), becomes `![caption](../assets/figures/ID.ext)`.
Rerun after changing a caption. Fails on unknown IDs, missing images, or a
figure placed twice or not at all.
"""
import pathlib, re, sys
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIGS = {f["id"]: f for f in yaml.safe_load((ROOT / "design/figures.yaml").read_text())}
ASSETS = ROOT / "src/assets/figures"
LINE = re.compile(r"^(?:<!-- figure: (?P<m>[\w-]+) -->|!\[[^\]]*\]\(\.\./assets/figures/(?P<i>[\w-]+)\.(?:png|jpg)\))\s*$")

def image(fid):
    for ext in ("png", "jpg"):
        if (ASSETS / f"{fid}.{ext}").exists():
            return f"{fid}.{ext}"
    return None

placed, errors = {}, []
for ch in sorted((ROOT / "src/chapters").glob("*.md")):
    out = []
    for n, line in enumerate(ch.read_text().splitlines(), 1):
        m = LINE.match(line)
        if not m:
            out.append(line); continue
        fid = m.group("m") or m.group("i")
        if fid not in FIGS:
            errors.append(f"{ch.name}:{n}: unknown figure {fid}"); out.append(line); continue
        if fid in placed:
            errors.append(f"{ch.name}:{n}: {fid} already placed in {placed[fid]}")
        placed[fid] = ch.name
        img = image(fid)
        if not img:
            errors.append(f"{ch.name}:{n}: no image for {fid} yet"); out.append(line); continue
        cap = " ".join(FIGS[fid]["caption"].split())
        out.append(f"![{cap}](../assets/figures/{img})")
    ch.write_text("\n".join(out) + "\n")

for fid in FIGS:
    if fid not in placed:
        errors.append(f"{fid}: not placed in any chapter")
print(f"placed {len(placed)} of {len(FIGS)} figures")
if errors:
    print("\n".join(errors)); sys.exit(1)
