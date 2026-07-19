# Inverness Packet Atlas — proposed appendix and slideshow companion

Status: proposed public-safe development lane with three rendered review
candidates. This atlas is **outside the approved forty-figure manifest**. It
does not change the approved book outline,
the forty canonical figures or the first-section voice gate. Promotion into the
book, Echo slideshow or video package needs a separate content, rights,
live-event-status and human-legibility approval.

## What the atlas would add

The August 11, 2026 municipal packet contains 45 lien entries associated with
47 unique PIDs. The current owner-free map reconciliation resolves those PIDs
to 53 NSPRD polygon features because some identifiers have multipart geometry.
The proposed publication unit is one card per lien, not one card per polygon:
the three PIDs under Lien 11 stay together, and multipart features are explained
rather than made to look like additional sale entries.

The atlas should credit the unusually substantial work already done by the
Municipality of the County of Inverness. Its added value is not a repackaging of
the packet. It is a consistent, dated comparison layer that shows what each
public source can establish, what it can only suggest and what remains for a
lawyer, surveyor, planner, insurer, engineer, environmental professional or
lawful site inspection.

The likely slideshow package is 50 frames: one orientation and method frame,
45 lien cards, three cross-property dashboards and one source/limitations
retrieval aid. These are optional appendix frames rather than forty new claims
that every audiobook listener must absorb. Echo may display them as a browsable
appendix or export them as a companion video; the main narration must remain
complete without them.

## Repeating lien-card anatomy

Each card should answer the same questions in the same positions:

1. **Dated municipal facts.** Auction date, lien number, municipality-published
   location, AAN, PID or PIDs, recovery amount, redeemable marker, packet version
   and the current event-status label. No assessed-owner names appear anywhere.
2. **County locator.** A simple point or halo locates the lien within Inverness
   County and names the nearest mapped community. This is orientation, not a
   statement that the municipality still offers the property.
3. **Parcel-scale view.** A rendered NS Aerial view with the matching NSPRD
   graphical boundary, scale, north arrow, retrieval date and licence text.
   Multipart geometry is labelled directly.
4. **One question-specific overlay.** Depending on the parcel: terrain and
   relief, mapped roads and civic context, Plan Inverness zoning, hydrography
   and screening layers, Crown/protected-land context, or geology and abandoned
   mine records. A layer is omitted when it adds no legible teaching value.
5. **Three evidence bands.** Municipal facts; public-map screening observations;
   and unresolved questions or professional handoffs. Derived measurements
   state their method, units, CRS and date.
6. **Limits and provenance.** Every card says that mapped parcel geometry is not
   a survey, visible road or track proximity is not legal access, environmental
   screening is not a wetland determination, and the card is not a title opinion,
   appraisal, building inspection or recommendation to bid.

Short map observations should use bounded wording: “the mapped parcel boundary
intersects,” “the nearest mapped road is approximately,” or “no overlap was
found in the named layer as retrieved on this date.” They must not become
“accessible,” “buildable,” “dry,” “clean,” “vacant,” “insurable” or “worth.”

## Publishable source and layer matrix

Only a source with a documented public reuse path enters the rendered atlas.
Every layer keeps its publisher, title, URL or service endpoint, retrieval date,
licence, transformation notes and required attribution in a machine-readable
source record.

| Source or layer | What it can add | What it cannot establish |
|---|---|---|
| Inverness tax-sale notice, packet, live page and later results | Event-specific identifiers, amounts, redemption marker, packet fields, status changes and reported outcome | Current title, boundary, condition, access, value or a guarantee that the entry remains in the sale |
| NSPRD graphical parcels | Reconcile a published PID to mapped polygon features; show apparent adjacency and multipart geometry | A surveyed boundary, ownership, current registry state or a title opinion |
| NS Aerial rendered imagery | Dated visible context such as apparent buildings, clearing, water, roads and tracks | Occupancy, interior or structural condition, legal access, current site conditions or permission to enter |
| Plan Inverness land-use by-law and zoning map | Screen the mapped zone and identify exact questions for Eastern District Planning Commission | A development permit, lawful existing use, subdivision approval, frontage compliance or buildability |
| Nova Scotia Road Network, addressable roads and civic points | Measure mapped road and civic-address context and distinguish different public datasets | Legal frontage, a right-of-way, maintained access or permission to cross another parcel |
| LIDAR-derived elevation, contours and slope | Compare relief, low points and terrain questions consistently | Geotechnical stability, drainage performance, construction cost or safe access |
| Hydrography, wetlands, coastal and flood-screening layers | Identify mapped intersections and proximity that merit agency or professional review | A wetland determination, flood certificate, ordinary-high-water mark, setback decision or environmental clearance |
| Crown land, protected areas and forest inventory | Add surrounding public-land, protection and forest-cover context | Ownership of the sale parcel, permission to use adjacent land, timber value or harvest rights |
| Nova Scotia well logs | Show nearby logged wells and the database's temporal/geographic coverage | A well on the parcel, water quantity, potability, septic suitability or present serviceability |
| Environmental Registry request process | Identify the official address-based route for certain environmental and onsite-sewage records | A bulk “clean” result, complete site history, conditions outside the registry's record coverage or a substitute for assessment |
| Abandoned Mine Openings, mineral occurrences and geoscience layers | Show nearby recorded occurrences with their published completeness and positional caveats | Absence of mine hazards, subsidence risk, mineral ownership, economically recoverable material or land value |
| PVSC public assessment search and disclosure data | Add dated public assessment and property-class fields where the reuse terms and match are recorded | Market value, an appraisal, condition, title or a rational maximum bid |

The first source-and-rights ledger should include, at minimum:

- Plan Inverness MPS/LUB and zoning materials:
  <https://invernesscounty.ca/municipal-planning-strategy-land-use-bylaw-in-effect/>
- Nova Scotia Well Logs:
  <https://data.novascotia.ca/Mines-and-Minerals/Nova-Scotia-Well-Logs-Database/eqej-ag64>
- LIDAR Tiles:
  <https://data.novascotia.ca/dataset/LIDAR-Tiles/ahjc-7din>
- Civic Address File — addressable roads and civic points:
  <https://data.novascotia.ca/Roads-Driving-and-Transport/Nova-Scotia-Civic-Address-File-Addressable-Roads/xtdd-axm7>
  and <https://data.novascotia.ca/Municipalities/Nova-Scotia-Civic-Address-File-Civic-Points/tntn-er5g>
- Nova Scotia Road Network and topographic roads/trails:
  <https://data.novascotia.ca/datasets/pg9a-kkaq> and
  <https://data.novascotia.ca/Roads-Driving-and-Transport/Nova-Scotia-Topographic-DataBase-Roads-Trails-and-/gywn-246n>
- Protected Areas, Crown land and forest inventory:
  <https://data.novascotia.ca/Environment-and-Energy/The-Nova-Scotia-Protected-Areas-System/ticv-5du5>,
  <https://data.novascotia.ca/datasets/sqec-gjbw> and
  <https://data.novascotia.ca/Lands-Forests-and-Wildlife/Forest-Inventory/c8ai-fjbt>
- Mineral occurrences, downloadable geoscience layers and Abandoned Mine
  Openings:
  <https://data.novascotia.ca/Mines-and-Minerals/Nova-Scotia-Mineral-Occurrence-Database/4cr9-9vxn>,
  <https://novascotia.ca/natr/meb/download/gis-data-maps.asp> and
  <https://novascotia.ca/natr/meb/geoscience-online/about-database-amo.asp>
- Environmental Registry and its request process:
  <https://novascotia.ca/nse/dept/envregistry.asp>
- PVSC public assessment search:
  <https://www.pvsc.ca/find-assessment>
- Nova Scotia Open Government Licence:
  <https://support.novascotia.ca/services/open-data-portal-licence>

## Property Online is a private research boundary

Property Online is not an atlas source. It is subscriber access governed by a
signed user agreement, not an Open Data Portal layer. The public package must
not contain Property Online screenshots, plans, registry documents,
assessed-owner or registered-owner information, copied map views, or structured
extracts derived from the subscription. It must not use paraphrase to recreate
a restricted document in substance.

A private title lookup may tell the researcher that a question is important,
but the public card records only the boundary: “current registry and title
review required.” No Property Online fact should be silently laundered into a
public-map observation. If a future edition proposes reproducing anything from
the service, publication pauses until the precise material and intended reuse
have written authorization from the Province or another rights holder.

Official access and agreement references:

- <https://www.novascotia.ca/subscribe-property-online>
- <https://www.novascotia.ca/sign-property-online>
- <https://novascotia.ca/sns/pdf/ans-property-pol-query-agreement.pdf>

## Cross-property analysis that earns the word “deep dive”

The atlas should distill the set without turning distressed-property records
into a shopping list:

- **Packet reconciliation dashboard.** Preserve the 45-entry summary, missing
  or incomplete detail records, amount disagreements, live-page changes, later
  results and council records as distinct dated sources. Never silently choose
  the most convenient version.
- **Coverage matrix.** For every lien, show whether PID geometry, aerial tiles,
  planning, terrain, road/civic, environmental, geoscience and assessment checks
  were available, matched, ambiguous, unavailable or not attempted.
- **Geometry dashboard.** Count liens, unique PIDs and NSPRD features separately;
  flag multipart records and any unresolved geometry rather than inflating the
  apparent property count.
- **Descriptive charts.** Recovery-amount distribution; redeemable versus marked
  non-redeemable; packet dwelling and Land Registration System fields when
  explicitly present; assessment distribution and assessment-to-recovery ratio
  with a large warning that neither number establishes value; and record
  completeness. Denominators and missing fields travel with every chart.
- **Place-based clusters.** Compare mapped patterns around Margaree, Mabou,
  Whycocomagh, Port Hood and other communities only to explain geography,
  planning and layer coverage. Do not rank communities or liens.
- **Question frequency.** Count how often the public research raises access,
  multipart geometry, planning, terrain, water/wastewater, environmental,
  coastal or mine-record questions. This is a research-workload chart, not a
  risk score.
- **Temporal record.** Freeze the source packet and retrieval date, then append
  removals, adjournments, sale results, redemption/deed information only when an
  official public source later provides it. Historical and live status must
  never be visually conflated.

Each result carries one of four confidence labels: **verified public record**,
**mapped screening observation**, **professional determination required**, or
**unresolved/missing evidence**. There is no combined score, “best property,”
maximum bid, predicted return or implied recommendation.

## Public-safety and editorial rules

- No assessed-owner names, registered-owner names, personal contact details,
  live-occupancy narratives or speculation about an identifiable person's
  circumstances.
- No trespass, drone flight, private-road entry, interior image, street-level
  surveillance or instruction to confront an occupant. Any original field image
  needs a separate lawful-capture and dignity review.
- Maps use only the municipality-published identifiers necessary to teach the
  method. The publication is dated and states whether it depicts an advertised,
  removed, sold, unsold or unknown-status entry.
- Every derived observation names its source and limitation. “No record found”
  is bounded by the source, geography, categories and retrieval date searched.
- Every layer passes a separate rights check. An open-data licence for one layer
  does not authorize another service, and a rendered map is not permission to
  redistribute raw tiles or a reusable parcel database.
- The existing Lien 1 aerial remains a pre-gate development specimen. Its
  quality does not approve the remaining liens or override the separate live
  parcel, rights, dignity, caption and Echo-stage reviews.
- The appendix explains research method and uncertainty. It does not offer
  legal, surveying, engineering, environmental, insurance, investment or
  valuation advice.

## Production sequence

1. **Source and rights ledger.** Confirm current official URLs, licence text,
   redistribution form, attribution and temporal coverage for every layer.
2. **Owner-free enrichment.** Join only the municipal lien/AAN/PID facts to
   rights-cleared public layers; calculate geometry and proximity fields with
   reproducible QGIS 4 processing steps and retain nulls.
3. **Three-card prototype.** Render one community/roadside example, one rural or
   multipart example and one coastal or mine-screening example. These are
   selected for teaching contrast, not investment merit.
4. **Human gate.** Review privacy, dignity, legal wording, source rights,
   map-screening limits and phone-size legibility before batch rendering.
5. **Batch and audit.** Render all approved cards from the same template, compare
   the output against the coverage matrix and manually inspect every frame.
6. **Event refresh.** Immediately before public packaging, check the live
   municipal page and label removals, adjournments and results without erasing
   the dated research snapshot.
7. **Separate approval.** Decide whether the atlas is a downloadable appendix,
   an Echo-only visual appendix, a narrated companion video or some combination.
   None is implied by approving the twelve chapters and forty canonical figures.

## Proposed approval gates

The atlas can advance after four distinct decisions:

1. approve the 45-card structure and non-ranking editorial policy;
2. approve the source/rights ledger, including the exclusion of Property Online;
3. approve the three representative prototype cards after phone and video-stage
   review; and
4. approve the fully rendered, status-refreshed atlas for public release.

### Current gate record — 2026-07-19

Dan replied “let's do it” to the proposed next step of producing three
deliberately contrasting prototype cards. That authorizes prototype development
for Liens 1, 8 and 11. The cards have been rendered and machine-checked, but the
reply is not recorded as visual acceptance. Gate 3 therefore remains pending
Dan's review of the resulting full-size/phone cards and a later actual Echo
stage proof. Gates 1, 2 and 4 remain separate; the other 42 lien cards are not
authorized for batch rendering.
