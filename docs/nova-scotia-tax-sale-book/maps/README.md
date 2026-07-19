# Inverness tax-sale map workspace

This workspace supports the public educational book and a possible interactive
companion. It is not a property recommendation, title opinion, survey,
appraisal, access opinion, environmental opinion or substitute for the live
municipal list.

## What is included

- `data/inverness-tax-sale-2026-08-11.json`: public-safe listing data derived
  from the municipality's August 11, 2026 schedule. Assessed-owner names are
  deliberately excluded.
- `working/inverness-tax-sale-parcels.geojson`: local build snapshot queried
  from the NSPRD service. It is ignored by Git; keep this raw geometry out of
  public distribution.
- `working/dp010v9sgkx_NS_Abandoned_Mines.zip`: ignored local copy of the
  openly licensed 2024 abandoned-mine-opening product used by one prototype.
- `qgis/inverness-tax-sale-2026-08-11.qgz`: editable QGIS project with an
  OpenStreetMap orientation layer, NS Aerial detail layer and the 2026 auction
  parcels, built and rendered with QGIS 4.0.2.
- `exports/`: 2560-by-1440 publication/video proofs.
- `atlas-prototypes/`: three attributed 2560-by-1440 evidence-card review
  candidates, full/phone contact sheets, teaching specs and a hash-bound QGIS 4
  receipt. These are outside the canonical forty-figure manifest.
- `scripts/`: repeatable data and QGIS-render steps.
- `build-metadata.json`: receipt for the checked-in proof render. A fresh fetch
  writes its current metadata beside the ignored GeoJSON under `working/`.

The checked-in QGIS project uses the relative source
`../working/inverness-tax-sale-parcels.geojson`. A fresh clone must rebuild that
local cache before the parcel layer will resolve.

## Reproduce locally

From this directory:

```bash
python3 scripts/build_map_assets.py
```

That command validates the owner-free listing JSON, queries the Province's
NSPRD service for every PID, writes the ignored working GeoJSON, and downloads
and validates the fixed-version DP ME 10 Version 9 source archive. It fails if
a listed PID is missing, the AMO shapefile members are absent or the public
input does not preserve the explicit owner-exclusion contract.

The proof renderer requires QGIS 4. On macOS, the checked-in wrapper reproduces
the producing environment:

```bash
scripts/render_qgis4_macos.sh
```

Set `QGIS4_APP` if QGIS is installed somewhere other than
`/Applications/QGIS-final-4_0_2.app`. Other platforms should launch both
`render_qgis_maps.py` and `render_atlas_prototypes.py` through their QGIS 4
Python environment. The checked-in project and render receipts identify QGIS
4.0.2 as the producing version.

## Source and licence boundary

Municipal schedule:
<https://invernesscounty.ca/wp-content/uploads/2026/07/Tax-Sale_August-11.pdf>

NSPRD property layer:
<https://nsgiwa2.novascotia.ca/arcgis/rest/services/PLAN/PLAN_NSPRD_WM84/MapServer/0>

NS Aerial basemap:
<https://nsgiwa.novascotia.ca/arcgis/rest/services/BASE/BASE_NSODB_10k_WM84/MapServer>

Abandoned Mine Openings DP ME 10 Version 9 and metadata:
<https://novascotia.ca/natr/meb/download/dp010.asp> and
<https://novascotia.ca/natr/meb/download/dp010md.asp>

Nova Scotia Open Government Licence:
<https://support.novascotia.ca/services/open-data-portal-licence>

OpenStreetMap orientation basemap:
<https://www.openstreetmap.org/copyright>

Province Restricted Map Services Licence used by this build:
<https://nsgiwa.novascotia.ca/documents/licenses/MapService/Restricted%20Map%20Services%20License%20-%20NSPRD%20v1.pdf>

Required statement on rendered views:

> Contains information obtained under license from the Province of Nova Scotia
> which is provided without warranty or liability for errors or omissions.

The restricted licence expressly supports viewing in any medium and requires an
application to link to the licence. It does not provide a broad raw-data
redistribution grant. Public map pages should therefore load aerial tiles and
query parcel geometry directly from the Province's services, carry the exact
attribution, and link the licence rather than publishing the local geometry
snapshot.

## Public interactive companion shape

A static web application can safely avoid a database for the first edition:

1. Publish the owner-free listing JSON.
2. On load, request the matching PIDs directly from the NSPRD ArcGIS query
   endpoint as GeoJSON.
3. Render NS Aerial tiles from the provincial cached MapServer as the optional
   basemap.
4. Show lien number, location, recovery amount, redemption marker and PID—never
   a property score, investment ranking or owner name.
5. Display snapshot date, live-list link, licence link, exact attribution and
   `not a survey or title opinion` language persistently.
6. Fail visibly if the provincial service is unavailable; do not serve a stale
   hidden parcel cache as though it were current.

The companion should open on the county overview. Selecting a lien can zoom to
its parcel or parcels and expose the municipal-source facts plus a separate
`research questions` panel. NS Aerial should be a user-controlled basemap rather
than the only view because county-scale aerial imagery makes overview labels
harder to read.

The publication orientation proof follows that same split: it uses one large
cyan circle or orange diamond per listed PID over OpenStreetMap, suppresses
individual lien labels at county scale and states the dated total in the
header. NS Aerial is reserved for close detail where parcel context is actually
legible. This avoids the coastline tile-gap artifacts and white polygon specks
seen in the first county-scale experiment.

The companion website itself is maintained in the separate [NS Marks The Spot
repository at `92f1261e5`](https://github.com/dfakkeldy/ns-marks-the-spot/tree/92f1261e5/web)
and is intentionally not duplicated in this book-development PR.
