# Inverness Packet Atlas — three-card prototype

Status: three QGIS 4 **accepted prototype-direction frames**, not final appendix
frames and not part of the forty canonical book figures. Dan authorized
prototype development with “let's do it” and accepted the exact rendered set
with “I like them.” on 2026-07-19. That acceptance does not authorize the
remaining 42 lien cards, canonical insertion, narration or publication.

## What this gate tests

- `atlas-lien-01-community-roadside.png` tests apparent road context without
  claiming legal access, frontage, condition or possession.
- `atlas-lien-08-mine-screening.png` tests an official geoscience overlay where
  the visual subject could easily outrun the evidence. It shows the four 2024
  Brigend Brook (Soapstone Mine) AMO records, two of which are nearly
  co-located. QGIS measures the nearest displayed record approximately 1,939
  metres from the NSPRD graphic.
- `atlas-lien-11-three-pid-group.png` keeps one municipal lien and its three
  PIDs together while displaying their three graphical parcel features.

Every frame separates the dated municipal facts, bounded public-map screening
observations, what the map does not prove and questions for appropriate
professional review. No owner name, property score, ranking, maximum bid or
recommendation appears.

## Reproduce

From the book map workspace:

```bash
python3 scripts/build_map_assets.py
scripts/render_qgis4_macos.sh
```

The first command validates and rebuilds the ignored owner-free NSPRD working
geometry and downloads the official DP ME 10 Version 9 AMO archive. The wrapper
uses QGIS 4.0.2 to rebuild the existing proofs and these three atlas cards.
`atlas-prototype-specs.json` is the teaching and safety input;
`render-receipt.json` binds it to the listing data, source archive and rendered
PNG hashes. `human-visual-approval.json` binds Dan's dated verbatim approval to
that exact receipt and asset set.

## Rights and evidence boundary

- NS Aerial and NSPRD are rendered under the Province restricted map-services
  licence and carry its exact attribution in every frame.
- DP ME 10 Version 9 is published under the Nova Scotia Open Government Licence;
  its mine-screening frame carries open-data attribution.
- The full AMO archive and raw NSPRD geometry remain ignored local build inputs.
- Property Online was not used. No screenshot, plan, registry document, owner
  information or subscription-derived extract enters these frames.
- The AMO inventory is incomplete, excludes surface expressions of subsidence,
  and warns that private-land positions may be inaccurate by up to about 50
  metres. A point is a screening record, not a hazard boundary.

## Visual inspection — 2026-07-19

The full-size cards and 640-by-360-per-card contact sheet were inspected. The
first pass was revised to tighten the Lien 11 extent and combine the labels for
two nearly co-located Soapstone records. The map, evidence-band headings and
primary teaching contrast remain distinguishable at phone stage. Detailed
source footers are intended for full-screen, EPUB and paused-video inspection;
they are not expected to serve as phone-size teaching copy.

Human acceptance of the exact three-card visual direction is recorded. Actual
Echo phone/desktop and video-stage proof remains pending. Any re-render changes
the bound hashes and requires fresh review; this acceptance does not authorize
batch rendering.
