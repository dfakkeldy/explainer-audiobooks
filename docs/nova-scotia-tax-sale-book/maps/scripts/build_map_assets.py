#!/usr/bin/env python3
"""Build a local-only NSPRD working layer from owner-free public input.

The checked-in listing JSON deliberately excludes assessed-owner names. This
script validates that public boundary and uses the listed PIDs to reconstruct a
restricted-service geometry cache for local QGIS rendering. Public web maps
should query the Province service at runtime instead of redistributing the
cache.
"""

from __future__ import annotations

import json
import hashlib
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path


MAP_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DATA = MAP_ROOT / "data/inverness-tax-sale-2026-08-11.json"
WORKING_GEOJSON = MAP_ROOT / "working/inverness-tax-sale-parcels.geojson"
WORKING_METADATA = MAP_ROOT / "working/build-metadata.json"

MUNICIPAL_SOURCE = (
    "https://invernesscounty.ca/wp-content/uploads/2026/07/"
    "Tax-Sale_August-11.pdf"
)
NSPRD_LAYER = (
    "https://nsgiwa2.novascotia.ca/arcgis/rest/services/PLAN/"
    "PLAN_NSPRD_WM84/MapServer/0"
)
NSPRD_QUERY = f"{NSPRD_LAYER}/query"
LICENSE_URL = (
    "https://nsgiwa.novascotia.ca/documents/licenses/MapService/"
    "Restricted%20Map%20Services%20License%20-%20NSPRD%20v1.pdf"
)
ATTRIBUTION = (
    "Contains information obtained under license from the Province of Nova "
    "Scotia which is provided without warranty or liability for errors or "
    "omissions."
)


def load_public_listings() -> tuple[dict[str, object], list[dict[str, object]]]:
    public_record = json.loads(PUBLIC_DATA.read_text(encoding="utf-8"))
    if public_record.get("ownerNamesExcluded") is not True:
        raise RuntimeError("public listing must explicitly exclude owner names")

    listings = public_record.get("listings")
    if not isinstance(listings, list) or len(listings) != 45:
        raise RuntimeError("expected 45 owner-free listings")

    allowed_keys = {
        "lien",
        "aan",
        "location",
        "recoveryAmount",
        "redeemable",
        "pids",
    }
    seen_pids: set[str] = set()
    for listing in listings:
        if not isinstance(listing, dict) or set(listing) != allowed_keys:
            raise RuntimeError("listing fields do not match the public schema")
        pids = listing.get("pids")
        if not isinstance(pids, list) or not pids:
            raise RuntimeError(f"lien {listing.get('lien')} has no PIDs")
        for pid in pids:
            if not isinstance(pid, str) or not pid.isdigit():
                raise RuntimeError(f"invalid PID in lien {listing.get('lien')}")
            if pid in seen_pids:
                raise RuntimeError(f"PID appears in more than one lien: {pid}")
            seen_pids.add(pid)

    if len(seen_pids) != 47:
        raise RuntimeError(f"expected 47 unique PIDs, found {len(seen_pids)}")
    return public_record, listings


def fetch_parcels(listings: list[dict[str, object]]) -> dict[str, object]:
    pids = [pid for listing in listings for pid in listing["pids"]]
    where = "PID IN (" + ",".join(f"'{pid}'" for pid in pids) + ")"
    query = urllib.parse.urlencode(
        {
            "where": where,
            "outFields": "PID",
            "returnGeometry": "true",
            "outSR": "4326",
            "f": "geojson",
        }
    )
    request = urllib.request.Request(
        f"{NSPRD_QUERY}?{query}", headers={"User-Agent": "KinNoKiLabs-map-build/1"}
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        collection = json.load(response)

    listing_by_pid = {
        pid: listing for listing in listings for pid in listing["pids"]
    }
    found: set[str] = set()
    for feature in collection.get("features", []):
        pid = feature.get("properties", {}).get("PID")
        if pid not in listing_by_pid:
            continue
        found.add(pid)
        listing = listing_by_pid[pid]
        feature["properties"] = {
            "lien": listing["lien"],
            "aan": listing["aan"],
            "location": listing["location"],
            "recovery": listing["recoveryAmount"],
            "redeemable": "YES" if listing["redeemable"] else "NO",
            "pid": pid,
        }

    missing = sorted(set(pids) - found)
    if missing:
        raise RuntimeError(f"NSPRD query did not return PIDs: {', '.join(missing)}")
    return collection


def main() -> None:
    public_record, listings = load_public_listings()
    parcels = fetch_parcels(listings)
    WORKING_GEOJSON.parent.mkdir(parents=True, exist_ok=True)
    WORKING_GEOJSON.write_text(
        json.dumps(parcels, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    pids = {pid for listing in listings for pid in listing["pids"]}
    metadata = {
        "builtDate": date.today().isoformat(),
        "listingSnapshotDate": public_record.get("retrievedDate"),
        "listingDataSHA256": hashlib.sha256(PUBLIC_DATA.read_bytes()).hexdigest(),
        "municipalSource": MUNICIPAL_SOURCE,
        "nsprdLayer": NSPRD_LAYER,
        "license": LICENSE_URL,
        "attribution": ATTRIBUTION,
        "publicDistributionBoundary": (
            "Rendered views may be displayed with attribution. Keep this raw "
            "geometry snapshot local; a public web map should query the "
            "Province service directly at runtime."
        ),
        "listingCount": len(listings),
        "requestedPIDCount": len(pids),
        "returnedFeatureCount": len(parcels.get("features", [])),
    }
    WORKING_METADATA.write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
