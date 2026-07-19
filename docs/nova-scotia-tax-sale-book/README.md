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
  traceable evidence notes, fact pack, twelve-chapter argument outline,
  structured learning records, Inverness dossier, municipal comparison,
  auction-result analysis, and 38-figure visual plan;
- `maps/data/`: an owner-free snapshot of the municipality-published August
  2026 listing facts;
- `maps/qgis/`: the editable QGIS 4.0.2 project used for the current proofs;
- `maps/exports/`: two attributed 2560-by-1440 development renders; and
- `maps/scripts/`: a reproducible local NSPRD fetch and QGIS 4 render workflow.

![Inverness County auction orientation proof](maps/exports/inverness-all-properties-orientation.png)

![Lien 1 aerial and parcel-context proof](maps/exports/inverness-lien-01-aerial.png)

The schedule has 45 liens and 47 unique PIDs. NSPRD returned 53 polygon
features because four PIDs are represented by multiple mapped pieces. The map
project includes every listed PID; the county-scale proof suppresses some
colliding labels and still needs final cartographic refinement.

## What is deliberately absent

- assessed-owner names and owner-bearing municipal source extraction;
- raw municipal PDF/text snapshots;
- raw NSPRD geometry and aerial tile caches;
- Property Online plans, registry documents, or subscription-derived material;
- live-property scores, rankings, maximum bids, or recommendations;
- internal pricing and possible-service planning notes; and
- manuscript chapters, covers, EPUB, M4B, read-along data, or any claim of
  human listening acceptance.

The interactive website implementation remains in [NS Marks The Spot at
`92f1261e5`](https://github.com/dfakkeldy/ns-marks-the-spot/tree/92f1261e5/web)
rather than being duplicated here. This repository owns the book development
packet and its reproducible QGIS proofs.

## Current production gates

The project is in `governed-final` development. Deep research, the argument
outline, structured chapter plans, coverage ledger, figure manifest, and two
QGIS proofs exist. Human outline authorization, accepted first-section voice,
the narrated comprehension pilot, full manuscript, independent learning and
prose review, final figures, cover selection, EPUB, Echo narration, public
package verification, and full listening all remain pending.

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

Rendered provincial-service views carry the required attribution inside each
image. See [the map workspace](maps/README.md) for the exact licence boundary
and reproduction steps.
