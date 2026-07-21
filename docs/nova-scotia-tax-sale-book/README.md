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
  traceable evidence notes, fact pack, approved thirteen-chapter argument outline,
  structured learning records, Inverness dossier, municipal comparison,
  auction-result analysis, production-map research-chain plan and product
  feedback, accepted voice exemplar, pronunciation plan,
  conversation decision log, handoff packet, and approved-for-pilot 51-figure visual direction;
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
  and 40;
- `chapters/`: canonical Chapters 1–13, drafted sequentially from the accepted
  pilot and approved argument outline, including the major map-method rewrite
  and its access, intended-use, environmental, title, cost, auction, tender,
  payment, and failed-sale branches;
  and
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
- complete canonical manuscript, covers or governed full-book package; the
  ignored `.build` tree contains only the accepted nonpackage narrated pilot
  and its machine receipts, not a final audiobook or delivery package.

The interactive implementation remains in the
[NS Marks The Spot repository](https://github.com/dfakkeldy/ns-marks-the-spot)
and [live map](https://kinnokilabs.com/apps/nsmarksthespot/map/) rather than
being duplicated here. The 2026-07-20 screenshot receipt pins production source
commit `d3114b5cfc907d85f8b2c1f015d5476719b53586`. This repository owns the
book-development packet, its reproducible QGIS proofs and version-stamped
chapter screenshots.

## Current production gates

The project is in governed whole-manuscript review. Dan approved the prior
twelve-chapter outline and forty-figure visual direction on 2026-07-19, accepted
the exact three-card Inverness Packet Atlas direction with “I like them,” and
accepted the exact first-section teaching and voice with “Let’s go for the
voice.” On 2026-07-20 he authorized redesigning the map chapter and
review figures around the production workflow: notice → parcel → context →
unknowns → handoff, then explicitly approved that thirteen-chapter, 51-figure
direction for pilot development. Deep research,
structured chapter plans, coverage paths, two QGIS proofs, eight reproducible
diagram candidates and three accepted-direction atlas prototypes exist. The
actual Echo/video-stage atlas proof, atlas batch authorization, final hash-bound
learning review, rendered ear pass, accepted final figures, cover selection,
EPUB, Echo narration, public package verification and full listening all remain
pending. The bounded humanizer/tightening pass is complete and has a current
hash-bound prose receipt; any later ear-pass edit must regenerate that receipt.

The governed nonpackage pilot rendered on 2026-07-20 at 14:27 with verified
alignment and a clean pronunciation audit. Its exact SHA-256 is
`c94570d369b1c5f3842f111f151a9e4bb880db2d84ceeed86f3cfed44c974f1c`;
Dan accepted that exact pilot for continued drafting with “continue” at
2026-07-20T08:55:51-03:00. Canonical Chapters 1–13 now total 31,824 Markdown
words after the initial independent review and the bounded humanizer pass
recorded in `research/editorial-review.md` and
`research/humanizer-decisions.json`. Eight local style edits remove generic
chapter navigation, and three post-edit beginner-review repairs clarify the
parcel-register record, expand NSPRD at first use and preserve the treasurer as
the certificate-registration actor.
The chapters remain draft prose until the final hash-bound learning review and
rendered ear pass are complete. Final figures, full narration, packaging and
publication remain separate.

The three accepted-direction atlas prototypes remain development evidence, but
the remaining 42-card batch is paused. Review should first decide whether the
living map now performs most parcel-orientation work more accurately and
usefully than a static owner-free atlas.

## Safety and currency

This material is educational only. It is not legal, tax, investment, title,
surveying, appraisal, access, environmental, insurance, planning, tenancy, or
construction advice. Municipal lists and procedures change. The legal and
event research was refreshed against official sources on 2026-07-19, and the
Chapter 6–11 planning, access, environmental, title, occupancy, mobile-home,
auction-result, tax, eligibility, auction/tender, payment, failed-sale,
certificate, redemption, and insurance sources on 2026-07-20; readers must
consult the current statute, live municipal list, auction terms, and their own
qualified professionals before relying on a live-sale detail.

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
