"""Reduce the Province's Municipality Boundaries dataset to a small simplified file.

Input: GeoJSON export of Nova Scotia open data dataset 7bqh-hssn ("Municipality
Boundaries", Nova Scotia Open Government Licence), downloaded 2026-10-09 from
https://data.novascotia.ca/resource/7bqh-hssn.geojson (not committed; 72 MB).
Output: figures/data/ns-municipal-units.json, projected to a local plane
(x = lon * cos(45.2 deg), y = lat, in degrees), Douglas-Peucker simplified,
rings below a minimum area dropped. Used only for fig-01-municipal-methods-map.

Usage: python3 -I prep_ns_boundaries.py /path/to/muni.geojson
"""
import json
import math
import sys
from pathlib import Path

K = math.cos(math.radians(45.2))
TOL = 0.004          # simplification tolerance, projected degrees (~400 m)
MIN_AREA = 0.0012    # drop rings smaller than this (projected square degrees)


def dp(pts, tol):
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        ax, ay = pts[a]
        bx, by = pts[b]
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy) or 1e-12
        best, idx = -1.0, -1
        for i in range(a + 1, b):
            px, py = pts[i]
            d = abs(dy * px - dx * py + bx * ay - by * ax) / L
            if d > best:
                best, idx = d, i
        if best > tol:
            keep[idx] = True
            stack += [(a, idx), (idx, b)]
    return [p for p, k in zip(pts, keep) if k]


def area(r):
    return abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(r, r[1:] + r[:1]))) / 2


def main(src):
    data = json.loads(Path(src).read_text())
    out = []
    for f in data["features"]:
        p = f["properties"]
        polys = f["geometry"]["coordinates"]
        rings = []
        for poly in polys:
            outer = [(lon * K, lat) for lon, lat in poly[0]]
            if area(outer) < MIN_AREA:
                continue
            # a closed ring starts and ends on one point; split it at the farthest vertex
            far = max(range(len(outer)), key=lambda i: math.dist(outer[0], outer[i]))
            s = dp(outer[:far + 1], TOL)[:-1] + dp(outer[far:], TOL)
            if len(s) >= 4:
                rings.append([[round(x, 4), round(y, 4)] for x, y in s])
        if rings:
            out.append({"name": p.get("name"), "kind": p.get("featdesc"),
                        "full": p.get("fullname"), "rings": rings})
    dest = Path(__file__).parent / "data" / "ns-municipal-units.json"
    dest.write_text(json.dumps({
        "source": "Province of Nova Scotia, Municipality Boundaries (open data 7bqh-hssn), "
                  "Nova Scotia Open Government Licence; downloaded 2026-10-09; simplified.",
        "projection": "x = longitude * cos(45.2 deg), y = latitude",
        "units": out}, separators=(",", ":")))
    print(dest, sum(len(r) for u in out for r in u["rings"]), "points")


if __name__ == "__main__":
    main(sys.argv[1])
