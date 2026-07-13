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
