# Nova Scotia tax-sale audiobook development packet

## Beyond the Tax-Sale Packet

**Status:** public-safe research and visual-development work in progress. This
is not a completed book or audiobook.

This packet develops a long, spoken-first educational book about Nova Scotia
municipal tax sales: terminology, the statutory process, municipal variation,
property research, auction behaviour, purchaser responsibilities, and the
questions that remain for qualified professionals. Inverness County's August
11, 2026 auction is the principal current case, with other Nova Scotia
municipalities used to distinguish provincial law from local procedure.

The intended final book is public. Its purpose is civic explanation and a
demonstration of careful research—not investment promotion, a live-property
ranking, or an advertisement disguised as education.

## What is here

- `research/`: the public-safe research brief, official-source register,
  traceable evidence notes, fact pack, proposed thirteen-chapter argument outline,
  structured learning records, Inverness dossier, municipal comparison,
  auction-result analysis, accepted voice exemplar, pronunciation plan,
  conversation decision log, handoff packet, and proposed 51-figure visual plan;
- `maps/data/`: an owner-free snapshot of the municipality-published August
  2026 listing facts;
- `maps/qgis/`: the editable QGIS 4.0.2 project used for the current proofs;
- `maps/exports/`: two attributed 2560-by-1440 development renders;
- `maps/atlas-prototypes/`: three owner-free QGIS 4 evidence-card prototypes
  plus full/phone contact sheets, specs, render receipt and hash-bound human
  visual-approval receipt;
- `maps/scripts/`: a reproducible local NSPRD/AMO source build and QGIS 4 render
  workflow;
- `figures/`: the deterministic diagram renderer, teaching/provenance
  specifications, contact sheets and hash-bound receipt for figures 03–08, 39
  and 40; and
- `chapters/images/`: eight legal/process candidates plus eleven
  2560-by-1440 NS Marks The Spot walkthrough screenshots; none is yet accepted
  or embedded in a manuscript.

![Inverness County auction orientation proof](maps/exports/inverness-all-properties-orientation.png)

![Lien 1 aerial and parcel-context proof](maps/exports/inverness-lien-01-aerial.png)

![Three-card Inverness Packet Atlas phone-stage review](maps/atlas-prototypes/atlas-prototype-phone-contact-sheet.png)

The schedule has 45 liens and 47 unique PIDs. NSPRD returned 53 polygon
features because four PIDs are represented by multiple mapped pieces. The map
project includes every listed PID; the county-scale proof uses large cyan and
orange halo markers over an OpenStreetMap orientation basemap and suppresses
individual lien labels at that scale. NS Aerial remains the detail basemap.

## What is deliberately absent

- assessed-owner names and owner-bearing municipal source extraction;
- raw municipal PDF/text snapshots;
- raw NSPRD geometry and aerial tile caches;
- Property Online plans, registry documents, or subscription-derived material;
- live-property scores, rankings, maximum bids, or recommendations;
- internal pricing and possible-service planning notes; and
- manuscript chapters, covers, EPUB, M4B, read-along data, or any claim of
  human listening acceptance.

The interactive website implementation remains in [NS Marks The Spot pull
request 89](https://github.com/dfakkeldy/ns-marks-the-spot/pull/89) and the
[live map](https://kinnokilabs.com/apps/nsmarksthespot/map/) rather than being
duplicated here. This repository owns the book development packet, its
reproducible QGIS proofs and the version-stamped chapter screenshots.

## Current production gates

The project is in `governed-final` pilot development. Dan approved the prior
twelve-chapter outline and forty-figure visual direction on 2026-07-19, accepted
the exact three-card Inverness Packet Atlas direction with “I like them,” and
accepted the exact first-section teaching and voice with “Let’s go for the
voice.” The current update proposes a thirteenth map-method chapter and a
replacement eleven-frame walkthrough, so the expanded thirteen-chapter,
51-figure scope still requires a new outline/figure verdict. Deep research,
structured chapter plans, coverage paths, two QGIS proofs, eight reproducible
diagram candidates and three accepted-direction atlas prototypes exist. The
narrated comprehension-pilot verdict, actual Echo/video-stage atlas proof,
atlas batch authorization, full manuscript, independent learning and prose
review, accepted final figures, cover selection, EPUB, Echo narration, public package
verification, and full listening all remain pending.

## Safety and currency

This material is educational only. It is not legal, tax, investment, title,
surveying, appraisal, access, environmental, insurance, planning, tenancy, or
construction advice. Municipal lists and procedures change. The legal and
event research was refreshed against official sources on 2026-07-19; readers
must consult the current statute, live municipal list, auction terms, and their
own qualified professionals before relying on a live-sale detail.

Principal current sources include the [Nova Scotia Municipal Government
Act](https://nslegislature.ca/sites/default/files/legc/statutes/municipal%20government.pdf),
the [Inverness County tax-sale page](https://invernesscounty.ca/services/finance-taxation/tax-sales/),
the [August 11, 2026 municipal packet](https://invernesscounty.ca/wp-content/uploads/2026/07/Tax-Sale_August-11.pdf),
the [NSPRD parcel service](https://nsgiwa2.novascotia.ca/arcgis/rest/services/PLAN/PLAN_NSPRD_WM84/MapServer/0),
and the [NS Aerial service](https://nsgiwa.novascotia.ca/arcgis/rest/services/BASE/BASE_NSODB_10k_WM84/MapServer).
The Lien 8 prototype additionally uses the Province's [DP ME 10 Version 9
Abandoned Mine Openings product](https://novascotia.ca/natr/meb/download/dp010.asp)
under the Nova Scotia Open Government Licence.

Rendered provincial-service views carry the required attribution inside each
image. See [the map workspace](maps/README.md) for the exact licence boundary
and reproduction steps.
