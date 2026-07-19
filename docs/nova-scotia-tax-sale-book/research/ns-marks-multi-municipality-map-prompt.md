# Copy-paste prompt: expand the NS Marks tax-sale map beyond Inverness

Use this prompt in the `ns-marks-the-spot` repository. It is intentionally
strict about event dates, owner privacy and the difference between an upcoming
listing and a historical result.

---

You are working in the NS Marks The Spot repository. Expand the existing online
tax-sale map from its single Inverness County event into a multi-municipality,
multi-event tax-sale catalog using only official municipal sources and the live
NSPRD PID lookup already used by the app.

First inspect the repository instructions, `git status --short --branch`, live
GitHub state, and the existing implementation at exact source commit
`92f1261e50dc05c8b2b2a6c38807d11d0f17cc98`. Preserve its Province licence
gate, relative/subpath-safe build, browser-local location behaviour, existing
Inverness data and tests. If the current checkout is the already-merged
`codex/inverness-tax-sale-web` branch, start a fresh feature branch from the
repository's current integration base rather than stacking new work on a stale
merged branch.

Read these Explainer Audiobooks research files before implementation:

- `docs/nova-scotia-tax-sale-book/research/municipal-map-source-register.json`
- `docs/nova-scotia-tax-sale-book/research/municipality-comparison.md`
- `docs/nova-scotia-tax-sale-book/research/sources.md`

They are available in [Explainer Audiobooks PR
#62](https://github.com/dfakkeldy/explainer-audiobooks/pull/62). If both
repositories are checked out locally, locate the Explainer repository from the
workspace rather than embedding a machine-specific path in source or receipts.

Treat the official municipal sources below as authority if a research note and
the live source differ.

## Scope and implementation order

### Phase 1 — current CBRM event

Add the Cape Breton Regional Municipality July 21, 2026 public auction as the
next upcoming event.

- Landing page:
  `https://cbrm.ns.ca/business/property-sales-management/tax-sales/`
- Official property list:
  `https://cbrm.ns.ca/wp-content/uploads/2026/06/JULY-21-2026-2nd-Ad.pdf`
- Official maps and descriptions:
  `https://cbrm.ns.ca/wp-content/uploads/2026/06/1.-List-of-Maps-and-Descriptions36.pdf`
- Expected source reconciliation: 67 lien rows and 68 unique PIDs. One lien has
  two PIDs.
- Public fields only: lien, AAN, PID list, address/description, location,
  minimum bid, and the municipality's redemption category.
- The PDF contains assessed-owner names. Never write those names to a source
  file, fixture, test, snapshot, build output, console log or UI.

### Phase 2 — historical comparison layers

Add these layers behind a clearly labelled **Historical 2026 events** control,
off by default. They must never look like available properties.

1. Pictou County tender 2026-01:
   `https://munpict.ca/assets/Tax-Sale-2026-01-Final-Advertisement-Posted-revised-April-10.pdf`
   - Closed April 10, 2026.
   - Expected 19 advertised rows/PIDs; three rows are visibly marked no longer
     part of the sale, leaving 16 in the revised list.
   - Preserve withdrawn rows with `listingStatus: "withdrawn"`; do not delete
     them or count them as active.
   - PDF text extraction drops leading zeroes from at least two PIDs. Visually
     inspect the rendered PDF and store every PID as an eight-character string.
   - Omit owner names.

2. Richmond County June 12, 2026 results:
   `https://www.richmondcounty.ca/tax-sales.html`
   - Expected three sold-result rows and three PIDs.
   - Store them as historical results, including official recovery and winning
     bid amounts if useful, but omit assessed-owner and successful-bidder names.
   - Never label them available, upcoming or recommended.

Do not add parcel records yet for:

- Annapolis County: its March and June 2026 result tables are currently embedded
  as images and require a separate visually verified extraction pass:
  `https://annapoliscounty.ca/tax-finance/tax-sale`
- Kings County: the current page confirms the March 24, 2026 event but exposes
  no parcel table:
  `https://www.countyofkings.ca/business/sales.aspx`
- Chester: the municipality explicitly says it is not holding a 2026 sale:
  `https://chester.ca/government/property-taxes-and-rates/tax-sales`

Represent the last three in an optional municipality-status/source register if
that fits the UI, but invent no parcels or coordinates.

## Data model

Generalize `web/src/data/invernessTaxSale.ts` without breaking the existing
Inverness receipt. Prefer an event-aware model similar to:

```ts
type TaxSaleEvent = {
  id: string;
  municipalityId: string;
  municipality: string;
  eventType: "public-auction" | "sealed-tender";
  eventStatus: "upcoming" | "historical";
  saleStartsAt?: string;
  closedAt?: string;
  venue?: string;
  sourceUrl: string;
  secondarySourceUrl?: string;
  retrievedOn: string;
  listings: TaxSaleListing[];
};

type TaxSaleListing = {
  eventId: string;
  recordId: string;
  lien?: string;
  aan?: string;
  pids: string[];
  location: string;
  minimumBidCents?: number;
  recoveryAmountCents?: number;
  successfulBidCents?: number;
  redemptionCategory: "six-month" | "immediate-deed" | "not-redeemable" | "unknown";
  listingStatus: "advertised" | "withdrawn" | "sold" | "unsold";
};
```

Adjust the exact shape to local conventions. Preserve money as integer cents,
PIDs and AANs as strings, and municipality wording as source data rather than a
cross-province legal conclusion. “Immediate deed” is a municipal category; the
UI must not imply immediate possession, guaranteed access, clear title or
buildability.

## UI behaviour

- Add municipality/event controls rather than one hard-coded Inverness toggle.
- Upcoming events are distinct from historical events. Historical is off by
  default and visibly dated.
- Keep the Province restricted-services licence acceptance in front of all
  NSPRD geometry requests.
- Query exact PIDs against live NSPRD; do not commit raw NSPRD geometry or tile
  caches.
- A selected parcel shows municipality, event date/status, official location,
  municipal financial field, redemption category, listing/result status,
  retrieval date and direct official-source link.
- Continue saying “listed in official notice” for upcoming records because
  properties can be paid, removed or deferred before sale.
- Add a historical-result label that cannot be mistaken for availability.
- Do not add scoring, ranking, bid ceilings, profit estimates or property
  recommendations.

## Required verification

Write tests before or alongside the model change that prove:

- Inverness remains 45 listings/47 PIDs with its current anomaly receipts.
- CBRM is 67 listings/68 unique PIDs.
- Pictou is 19 historical rows, three withdrawn, 16 remaining and 19 visually
  verified eight-character PIDs.
- Richmond is three historical sold rows/three PIDs.
- every public listing contains only the allowed owner-free fields;
- no source or built artifact contains the discarded assessed-owner or bidder
  fields;
- upcoming and historical filters cannot mix their counts or labels;
- exact-PID selection works across municipality boundaries;
- NSPRD failures remain visible and do not manufacture geometry; and
- production build output remains subpath-safe for the KinNoKi deployment.

Run the existing web tests, lint, production build, public-safety scan and live
NSPRD PID-match validation. Inspect desktop and phone layouts, exercise each
event filter, select at least one PID per municipality, and check the browser
console. Update `web/README.md` with source URLs, retrieval dates, expected
counts, anomalies, privacy exclusions and the distinction between source commit,
NS Marks deployment and the separately pinned KinNoKi production copy.

Commit the coherent NS Marks work and follow the repository's normal feature-PR
workflow. Do not change the KinNoKi site pin or claim production deployment as
part of this repository-only task.

---

The first useful cut is CBRM plus the generalized event model. If Pictou's two
leading-zero PID corrections or any row count cannot be proven visually, ship
CBRM alone and record Pictou as a fail-closed follow-up rather than guessing.
