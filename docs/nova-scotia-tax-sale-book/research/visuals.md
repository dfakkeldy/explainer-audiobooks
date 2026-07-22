# Visual-listening figure plan

Status: all 51 figures in the approved pilot direction now have landscape review
candidates, and all 51 have paired mobile review candidates. Figures 41 through
51 use genuine 390-by-844 mobile-browser captures in the mobile rendition rather
than resized desktop screenshots. The remaining mobile figures are purpose-built
1080-by-1920 reflows. This register remains the authority for interior figures in
the public edition. Canonical chapter prose is unchanged; review builds use the
reversible placement layer under `figures/` until the matching narration,
placement, full phone review and Echo proof are approved.

## Complete visual review set — 2026-07-22

The previously missing 32 figures—01, 02 and 09 through 38—now exist in both
2560-by-1440 landscape and 1080-by-1920 mobile forms under
`figures/visual-expansion-review-v4/`. The set includes the two original
editorial scenes, the three five-map fictional case families, the evidence and
legal-process diagrams, the numerical charts and the final retrieval aid.

Figures 03 through 08, 39 and 40 also have purpose-built mobile reflows in the
same review directory. Together with the separately captured mobile-browser map
screens, the private staging run contains 51 desktop and 51 mobile assets. Its
placement receipt proves that removing the review-only figure blocks restores
the canonical chapter Markdown exactly.

Two silent 103.967-second proof reels were rendered from the complete cue order:
1920-by-1080 landscape and 1080-by-1920 portrait. They are rapid visual-review
artifacts, not narrated exports, governed packages or publication evidence. The
paired EPUBs are likewise review candidates only; full human figure acceptance,
narration alignment and the whole-book video export remain separate gates.

## Interactive-map research-chain batch — 2026-07-20

Figures 41 through 51 are version-stamped 2560-by-1440 review candidates for
the approved-for-pilot Chapter 5. They now teach one complete chain—notice, parcel,
context, unknowns and handoff—using the production app's current parcel browser,
authoritative civic-address search, Plus Codes, road/water results,
geology/resource screening and verified historical outcomes. Their source
commit, hashes and refresh boundary are recorded in
`figures/map-chapter-screenshot-receipt.json`; the contact sheet is
`figures/map-chapter-screenshots-contact-sheet.png`.

The captures are teaching evidence, not final publication assets. The app is
still changing, so all eleven screens must be recaptured after interface freeze
and checked again against the live municipal notice immediately before
publication. No screen is a property recommendation or proof of survey, title,
access, flooding, wetland, site condition or development permission.

## First slideshow diagram batch — 2026-07-19

Figures 03 through 08, 39 and 40 now exist as reproducible 2560-by-1440 sRGB
review candidates:

- the two pre-sale/post-sale clocks;
- a fictional Inverness-style parcel-sheet anatomy;
- the identifier chain and its limits;
- the packet/source reconciliation table;
- the ordinary six-month redeemable route; and
- the older-arrears redemption exception and unresolved property questions;
- auction payment readiness, immediate payment and the three-business-day
  default branches; and
- the surplus-proceeds account, court-application window and twenty-year
  endpoint.

Their editable source, machine-readable teaching/provenance specifications,
large contact sheet, 640-by-360-per-frame phone-stage contact sheet and
hash-bound render receipt live under `figures/`. The rendered PNGs live under
`chapters/images/`.

The first visual inspection found ambiguous flow in Figure 03 and centered text
escaping its cards in Figures 05, 07 and 08. The renderer was corrected and all
original six candidates were regenerated and re-inspected. The two drought-repair
figures use the same visual grammar and are included in the current phone-stage
contact sheet. The primary teaching structure remains readable in the
640-by-360 preview, but dense secondary copy,
caption placement and the subtitle band still require the planned real Echo
phone/desktop and short-video proof. No figure has human acceptance yet.

The legal labels were refreshed against the Municipal Government Act snapshot
consolidated to April 9, 2026 and the live Inverness tax-sale page on July 19,
2026. Figures 07 and 08 remain educational route summaries, not legal advice;
current law and event-specific municipal terms must be checked again before a
public edition is packaged.

## QGIS 4 development proof — 2026-07-18; overview refined 2026-07-19

The local map workspace now contains an editable QGIS project and two
2560-by-1440 proofs built with QGIS 4.0.2 (`4.0.2-Norrköping` in the saved
project metadata):

- `maps/qgis/inverness-tax-sale-2026-08-11.qgz` contains NS Aerial and all
  current Inverness auction parcels;
- `maps/exports/inverness-all-properties-orientation.png` is a county-scale
  orientation proof;
- `maps/exports/inverness-lien-01-aerial.png` is a close aerial-and-parcel proof
  for Lien 1; and
- `maps/data/inverness-tax-sale-2026-08-11.json` is the owner-free listing
  dataset that can also drive an interactive companion.

The municipal schedule contains 45 liens and 47 unique PIDs. All 47 PIDs
resolved through NSPRD to 53 polygon features; the higher polygon count is
expected because several PIDs have more than one mapped feature. Owner names
were deliberately omitted from the derived listing and map attributes.

These are development evidence, not accepted book plates. The county-scale
proof now uses sized, coloured halo markers over an OpenStreetMap orientation
basemap, with individual lien labels removed at that scale and the live count
stated in the header. This fixes the white-speck, phone-label and aerial
tile-gap failures while preserving NS Aerial for detail.

The Lien 1 detail remains a strong **pre-gate development specimen**. It is not
an approved book plate merely because it is committed. Before any canonical
chapter insertion or public package, its deliberate gate order is: source and
licence check; owner/privacy and live-event-status refresh; educational-need
review; caption and non-recommendation review; Echo phone/desktop and video
stage proof; then human visual acceptance. A failed gate retires or replaces
the specimen; it does not inherit approval from its earlier production date.

## Proposed Inverness Packet Atlas

The separate `inverness-packet-atlas-plan.md` proposes an owner-free appendix
and slideshow companion: one repeatable evidence card for each of the 45 liens,
plus orientation, reconciliation and source-limit dashboards. It would combine
municipal packet facts with rights-checked public mapping, clearly separated
screening observations and professional handoffs. Property Online screenshots,
documents, owner information and subscription-derived extracts are excluded.

This direction **does not add the atlas to the 51-figure chapter direction**.
The atlas stays outside the proposed manifest until its card structure, source-and-rights
ledger, three-card prototype, live-event-status refresh and complete rendered
set each pass a separate approval gate. The existing Lien 1 aerial is only a
pre-gate specimen for that discussion.

Dan authorized the three-card prototype development step on 2026-07-19 with
“let's do it.” QGIS 4.0.2 review candidates now exist for Lien 1
(community/roadside context), Lien 8 (abandoned-mine-record screening) and Lien
11 (one lien with three PIDs). Their specs, full/phone contact sheets and
hash-bound receipt live under `maps/atlas-prototypes/`. The mine card uses four
official 2024 Brigend Brook (Soapstone Mine) records and reports the nearest
displayed record approximately 1,939 metres from the NSPRD graphic. It also
states the database's incompleteness, subsidence exclusion and approximately
50-metre private-land positional caveat.

The first full/phone visual inspection tightened the Lien 11 extent and combined
two nearly co-located mine-record labels. After receiving the three cards and
phone-stage sheet, Dan accepted the exact rendered prototype direction with “I
like them.” at 2026-07-19T15:39:47-03:00. The hash-bound human receipt lives
beside the render receipt. Actual Echo phone/desktop and video-stage proof
remains pending. This acceptance does not approve the 42 remaining lien cards,
canonical insertion, narration, batch rendering or publication.

## Purpose

This book should be a strong Echo Visual Listening and video-export title, not
an audio book with a few incidental illustrations. The main narration must
remain complete with the screen unavailable, while the visual track should make
spatial, procedural and numerical relationships easier to retrieve.

The approved-for-pilot target is **51 purposeful figures**:

- 15 QGIS map plates: three fictional/composite case files, each using the
  five-map packet structure;
- 22 diagrams and charts that explain law, source authority, reconciliation,
  auction behaviour and post-sale responsibility;
- 2 original editorial illustrations that establish the auction-room and
  research-desk story settings; and
- 1 final retrieval/decision aid.
- 11 version-stamped NS Marks The Spot walkthrough screenshots.

At an estimated 46,200 narrated words, this gives roughly one new figure every
6–8 minutes. Echo's karaoke subtitles provide motion between figure changes, so
the book does not need decorative filler or artificial animation.

## Echo and video production contract

Checked against the live Echo source and approved export design on 2026-07-18:

- Echo selects image blocks from the EPUB and aligns them to nearby narrated
  text through `VisualListeningCueResolver`.
- The live stage and video export use the same cue decisions.
- Whole-book export is designed for 1920 by 1080 H.264/AAC video with burned-in
  subtitles, a sidecar SRT and a chapter timestamp file.
- The renderer aspect-fits the figure on a dark stage, puts the figure caption
  beneath it and reserves the bottom band for subtitles.
- A missing or unreadable figure falls back to the cover rather than aborting a
  long export.

Production implications:

1. Master raster figures at 2560 by 1440 pixels in sRGB PNG. Retain the QGIS,
   SVG or chart source so text and line weights can be revised.
2. Use a central safe area. Put no essential label within 8 percent of an edge.
3. Use one teaching idea per frame, large labels, high contrast and no table
   that requires pinching or pausing to decode.
4. Keep image-internal titles short because Echo already displays a caption and
   subtitle. Never bake the narrated paragraph into the image.
5. Design for a 1920 by 1080 export, a smaller phone stage and an EPUB page at
   the same time. Minimum final-master text target: 40 pixels for normal labels,
   52 pixels for primary labels and 30 pixels for unavoidable source footers.
6. Time each figure to the paragraph that teaches it. If a chapter needs a
   longer display interval, place a second related figure rather than letting a
   single dense plate carry several ideas.

Echo production references reviewed in the separate Echo repository:

- `Shared/VisualListeningCueResolver.swift`
- `EchoCore/Services/Export/SlideshowFrameRenderer.swift`
- `docs/superpowers/specs/2026-07-18-slideshow-video-export-design.md`

## Rights and public-safety rules

- Maps may use self-created vectors, user-created QGIS layouts, public-domain
  material, Nova Scotia Open Government Licence data and properly attributed
  rendered NS Aerial or NSPRD service views.
- Every figure using open provincial data carries: `Contains information
  licensed under the Open Government Licence – Nova Scotia.`
- Every figure using a rendered restricted-service view carries the exact
  required statement inside the exported image so it survives EPUB, Echo and
  video reuse: `Contains information obtained under license from the Province
  of Nova Scotia which is provided without warranty or liability for errors or
  omissions.`
- Do not package raw restricted-service tiles, a reusable parcel database or a
  bulk cache. A rendered map view is the planned publication unit.
- Property Online plans and registry documents remain out of public figures
  until their separate reproduction terms are confirmed. Recreated teaching
  diagrams may explain their fields without reproducing a document.
- The fifteen instructional case maps use fictional composite parcel IDs and
  geometry. A separate authentic current-list orientation/demo may show the
  municipality-published lien, PID and location fields to demonstrate the
  research method, but only after a separate public-safety review, with no
  assessed-owner name, score, ranking, maximum bid or implied recommendation.
- No live parcel gets a score, rank, maximum bid or visual treatment that turns
  an identifiable owner or occupant into entertainment.
- The two scene illustrations are original editorial artwork, clearly
  illustrative rather than a documentary depiction of a specific venue or
  person.

## Visual grammar

- **Municipal fact:** navy.
- **Verified added public record:** teal.
- **Map-screening clue or visual interpretation:** amber.
- **Unresolved or professional verification needed:** magenta.
- **No-go until resolved:** red.
- **Process complete or source reconciled:** green.
- Maps use a consistent legend order, north arrow, scale, CRS, retrieval date,
  map ID and `not a survey or title opinion` note.
- Charts label sample size and completeness directly on the frame. Ratio charts
  always say that advertised recovery is not value.

## Figure manifest

Captions and alt text below are working copy. Each must be rechecked against the
final visual and narration before packaging.

| ID / filename | Ch. | Teaching job and visual form | Planned source / provenance | Working caption | Working alt text |
|---|---:|---|---|---|---|
| `figure-01-auction-morning.png` | 1 | Establish the Port Hood auction setting without glamorizing a distressed-property sale; original editorial illustration. | Original generated or commissioned art; no exact venue likeness and no identifiable people. | A tax sale begins as municipal collection work, not a treasure hunt. | Editorial illustration of a quiet Cape Breton community hall on an auction morning, with folders and bidder cards visible through the entrance. |
| `figure-02-nova-scotia-municipal-methods.png` | 1 | Orient Inverness inside Nova Scotia and distinguish open auction, tender and no-current-sale comparison municipalities. | Self-created QGIS map from open municipal boundaries; dated municipal method research. | Municipal procedure varies even though the provincial legal framework is shared. | Map of Nova Scotia highlighting Inverness, CBRM, Richmond, Pictou, Annapolis, Kings and Chester with symbols for auction, tender or no current sale. |
| `figure-03-two-clocks.png` | 1 | Show the municipal pre-sale sequence and purchaser post-sale sequence as two connected clocks. | Self-created vector diagram from MGA/HRM Charter evidence notes. | The sale connects two legal clocks; it does not end either one instantly. | Two horizontal timelines meet at auction day: arrears, notices and advertisement before it; certificate, possible redemption and deed after it. |
| `figure-04-packet-anatomy.png` | 2 | Teach the fields in an Inverness-style parcel sheet without reproducing owner data or a Property Online document. | Self-created fictional packet page based on observed public field structure. | Every field is an identifier or claim to verify, not a promise about the parcel. | Annotated fictional tax-sale packet page pointing to lien number, AAN, PID, recovery amount, assessment, redemption marker, map and legal-description areas. |
| `figure-05-identifiers-not-promises.png` | 2 | Separate lien, AAN, PID, civic address, assessment, map and legal description. | Self-created ladder diagram grounded in LAND-001 through LAND-004. | Identifiers help records meet; none alone proves boundaries, access, condition or value. | Seven labelled record cards form a ladder from tax-sale lien to legal description, with the unsupported conclusions crossed out beside each card. |
| `figure-06-reconcile-the-packet.png` | 2 | Show why summary list, detail page, live webpage, registry research, results and council record must remain separate. | Self-created reconciliation diagram using anonymized August 2026 and May 2025 discrepancies. | A careful file preserves disagreement instead of silently choosing a convenient number. | Six source boxes feed a comparison table; mismatched amount, missing detail page and differing result counts are highlighted in amber. |
| `figure-07-redeemable-route.png` | 3 | Isolate the ordinary six-month redemption route. | Self-created statutory process diagram; current-law refresh required. | A winning bid may begin a six-month certificate-holder period rather than immediate ownership. | Timeline from auction to certificate, insurance and record keeping, possible redemption, and tax deed if no redemption occurs. |
| `figure-08-nonredeemable-route.png` | 3 | Isolate the immediate-deed route while showing what the marker does not settle. | Self-created statutory process diagram; current-law refresh required. | Immediate deed changes the redemption route, not possession, access, title quality or buildability. | Short route from auction to deed beside four unresolved branches labelled possession, access, title and intended use. |
| `figure-09-evidence-desk.png` | 4 | Establish the recurring researcher role and show multiple source classes meeting in one evidence file. | Original generated or commissioned editorial art; fictional records only. | The researcher's product is a traceable evidence file, not a verdict. | Overhead editorial illustration of a desk with a municipal packet, map layers, statute, source log and three folders marked known, unresolved and professional. |
| `figure-10-source-authority-ladder.png` | 4 | Rank statute, municipal terms, registry records, plans, maps, imagery and inference by the question each can answer. | Self-created hierarchy from the evidence and GIS specifications. | A stronger source is one authorized to answer the particular question—not simply one that looks official. | Stacked source cards rise from imagery and screening clues to municipal records, registry evidence and governing law, with different question icons beside them. |
| `figure-11-beyond-the-packet-delta.png` | 4 | Credit the substantial Inverness packet and show the genuinely added research layer. | Self-created comparison from DATA-005 and the GIS packet specification. | The value-add begins after the municipality's facts, map and legal description—not by repackaging them. | Two-column stack comparing municipal packet contents with reconciliation, planning, terrain, environmental screening, uncertainty labels and professional handoffs. |
| `figure-12-five-evidence-labels.png` | 4 | Teach verified record, map-screening clue, visual interpretation, professional verification and no-go-until-resolved. | Self-created classification card. | Good research labels the strength and authority of each observation. | Five colour-coded evidence cards progress from verified record to unresolved no-go, each with a one-sentence example. |
| `figure-13-case-a-orientation.png` | 6 | Case A map 1: orient the fictional landlocked sliver in community, road and water context. | QGIS; fictional geometry over rights-clear open or rendered provincial layers. | Case A begins with location, not with a conclusion about access. | Wide map locating fictional Parcel A among communities, public roads and water, with scale and north arrow. |
| `figure-14-case-a-identity.png` | 6 | Case A map 2: reconcile fictional parcel ID, tax account and graphical boundary while stating that the boundary is not a survey. | QGIS; fictional IDs and teaching geometry; any NSPRD rendered view separately attributed. | The graphical outline identifies the research target; it does not settle the legal boundary. | Parcel A highlighted with three fictional record identifiers and a prominent not-a-survey warning. |
| `figure-15-case-a-access-terrain.png` | 6 | Case A map 3: compare apparent approach, public road, contours, watercourses and the unanswered right-of-way question. | QGIS; open roads, terrain and hydrography plus fictional access marks. | A visible track can be a clue without being a legal right of access. | Terrain map showing Parcel A, a nearby public road, a dashed visible track, steep contours and a question mark where legal access would need proof. |
| `figure-16-case-a-planning-services.png` | 6 | Case A map 4: show zone, frontage, service assumptions and questions for Eastern District Planning. | QGIS; recreated teaching zone geometry unless municipal embedding rights are confirmed. | Planning controls and servicing are separate tests from parcel identity. | Map of fictional Parcel A with zoning colour, frontage dimension, well and septic question icons, and a planner-confirmation callout. |
| `figure-17-case-a-physical-screening.png` | 7 | Case A map 5: combine aerial context, wet ground, coast, geology and mines without claiming causation or cleanliness. | QGIS; open data and attributed rendered NS Aerial view. | A screening map tells you where to ask harder questions; it is not an environmental opinion. | Aerial-style map of Parcel A with wet-ground, coastal, geology and mine-opening screening layers and an unresolved-evidence legend. |
| `figure-18-case-b-orientation.png` | 7 | Case B map 1: orient the fictional occupied-building case. | QGIS; fictional geometry over rights-clear base layers. | An occupied-looking building changes the question set before anyone discusses possession. | Map locating fictional Parcel B in a serviced community with a building footprint and nearby streets. |
| `figure-19-case-b-identity.png` | 7 | Case B map 2: separate land parcel, building footprint and possible manufactured-home record. | QGIS; fictional identifiers and self-created symbols. | Land, buildings and a manufactured home may not share one simple record story. | Parcel B outline contains a building footprint and a separate manufactured-home question card tied to different fictional records. |
| `figure-20-case-b-access-terrain.png` | 7 | Case B map 3: show lawful exterior observations, driveway geometry and drainage clues. | QGIS; fictional case geometry and rights-clear terrain/road layers. | Exterior observation can narrow questions without entry, confrontation or trespass. | Street-and-terrain map of Parcel B showing a driveway, drainage path and public observation points outside the parcel boundary. |
| `figure-21-case-b-planning-services.png` | 8 | Case B map 4: map zone, existing-use questions, water/sewer context and occupancy-related municipal checks. | QGIS; recreated planning symbology unless embedding terms are confirmed. | Existing occupation does not prove lawful use, services or vacant possession. | Planning map of Parcel B with zone, water and sewer lines, use-confirmation icon and a separate occupancy warning. |
| `figure-22-case-b-physical-screening.png` | 8 | Case B map 5: show former-use and environmental-registry clues around the occupied composite. | QGIS; open public screening data and fictional site history. | A mapped historical clue is a lead for professional review, not a contamination finding. | Parcel B map with a former-use symbol, nearby registry point and arrows to records and environmental-professional questions. |
| `figure-23-negative-search-beam.png` | 7 | Explain why a database with limited time, geography or category coverage cannot issue a clean bill of health. | Self-created beam/coverage diagram. | “No result” means only that this search, in this source, found no matching record. | A flashlight beam covers part of a dark field labelled by time, location and record type; hazards outside the beam remain unknown. |
| `figure-24-title-encumbrance-possession.png` | 8 | Keep title, continuing rights and actual possession in three separate columns. | Self-created legal-concept diagram with lawyer-review boundary. | Title, encumbrances and possession are related, but none is a synonym for the others. | Three parallel columns labelled ownership interest, rights and burdens, and people or property on site, joined by dotted rather than equal signs. |
| `figure-25-occupied-property-handoff.png` | 8 | Show the researcher's stop points and the lawful professional handoff for tenancy, locks, rent and abandoned goods. | Self-created decision-boundary diagram; educational only. | Occupancy questions move from observation to legal advice—not to self-help. | Flowchart starts with lawful exterior observation and records, then stops at lawyer or tenancy advice before contact, entry, lock changes or goods handling. |
| `figure-26-inverness-ratio-distribution.png` | 9 | Plot the 31 published 2025 bid/recovery ratios and the 4.53-times median without implying the set is all 35 sales. | Self-created chart from the official results rows; analysis file retained. | In the 31 published rows, competition often carried bids far above the recovery amount. | Dot plot of 31 bid-to-recovery ratios from 1.00 to 21.62, with the 4.53 median marked and a 31-row completeness caveat. |
| `figure-27-fifty-thirtyfive-thirtyone.png` | 9 | Preserve the 50 advertised, 35 sold and 31 published-row counts as different official measures. | Self-created funnel/waterfall from packet, council minutes and results PDF. | Advertised, sold and published-result counts answer different questions and do not silently collapse into one number. | Three large count cards show 50 advertised, 35 reported sold and 31 published result rows, with 15 removals and a four-row unresolved gap. |
| `figure-28-municipal-result-comparison.png` | 9 | Compare Inverness, CBRM and Richmond results only where definitions and row coverage can be stated. | Self-created small multiples from dated municipal result sources. | Cross-municipal numbers are useful only when sample size, procedure and denominator travel with them. | Three small charts compare dated municipal result sets, each labelled with auction type, number of rows and a warning against treating recovery as value. |
| `figure-29-all-in-cost-stack.png` | 9 | Show bid plus legal, tax, insurance, survey, carrying, repair, remediation, possession and uncertainty reserve. | Self-created generic cost-stack diagram; no personalized amounts. | The winning bid is one layer in the acquisition's uncertainty budget. | Layered stack begins with bid price and adds taxes, legal work, insurance, survey, carrying costs, repairs, remediation, possession and reserve. |
| `figure-30-auction-versus-tender.png` | 10 | Compare open-outcry auction and sealed-tender information flow and decision pressure. | Self-created side-by-side process diagram from municipal procedures. | Open bidding reveals competitors in real time; a tender hides them, but both reward a prewritten limit. | Parallel timelines compare registration and live bidding with sealed submission and opening, both ending at the same written walk-away rule. |
| `figure-31-certificate-holder-calendar.png` | 11 | Organize the six-month stewardship period: certificate, registration, insurance attempts, taxes, protective work, records and redemption. | Self-created calendar from current statutory and municipal research. | The certificate-holder months are an operations period, not dead time. | Six-month calendar with recurring record-keeping and insurance tasks, new-tax markers, protective-work limits and a possible redemption event. |
| `figure-32-deed-is-a-beginning.png` | 12 | Show deed registration followed by title, possession, planning, condition, insurance and intended-use work. | Self-created handoff diagram. | A tax deed changes the file's legal stage; it does not finish the property work. | Tax deed at the centre sends six arrows to lawyer, possession, planning, survey, condition and insurance workstreams. |
| `figure-33-case-c-orientation.png` | 13 | Case C map 1: orient the coherent-but-not-recommended fictional parcel. | QGIS; fictional geometry over rights-clear layers. | Case C is the strongest file, not a recommendation to buy. | Regional map locates fictional Parcel C near a public road and community services with a green evidence-file label and no bid score. |
| `figure-34-case-c-identity.png` | 13 | Case C map 2: show consistent fictional identifiers and a graphical parcel outline with survey/title caveat. | QGIS; fictional IDs and teaching geometry; any NSPRD rendered view separately attributed. | Consistent records reduce one uncertainty without eliminating the rest. | Parcel C outline beside matching fictional lien, AAN and PID cards and a not-a-survey note. |
| `figure-35-case-c-access-terrain.png` | 13 | Case C map 3: show apparent public-road contact, manageable terrain and the remaining legal-access confirmation. | QGIS; open road/terrain data and fictional geometry. | Strong map evidence can support a focused legal question; it cannot answer it. | Parcel C touches a mapped public road and gentle contours, with a lawyer-confirmation icon at the frontage. |
| `figure-36-case-c-planning-services.png` | 13 | Case C map 4: show a plausible intended-use path and exact planner/service questions. | QGIS; recreated planning geometry unless embedding terms are confirmed. | A coherent file names the confirmations still required before an intended use is credible. | Parcel C planning map shows zone, frontage, well and septic assumptions and three written questions for municipal planning staff. |
| `figure-37-case-c-physical-screening.png` | 13 | Case C map 5: show no found screening overlap while preserving database and site-inspection limits. | QGIS; open screening data and attributed rendered imagery. | “No mapped overlap found” is a bounded result, not a clean bill of health. | Physical-screening map for Parcel C shows searched layers, no highlighted overlap, coverage limits and an inspection handoff. |
| `figure-38-known-unresolved-professional.png` | 13 | End with the reusable three-column evidence record and decision boundary. | Self-created retrieval sheet based on the three composite cases. | A responsible file ends by separating what is known, what remains unresolved and who is authorized to answer next. | Final summary sheet with columns for known facts, unresolved questions and professional handoffs, plus a separate box stating that the bidder owns the decision. |
| `figure-39-payment-readiness-clock.png` | 10 | Put bidder authority, accepted funds, immediate payment and the three-business-day balance on one operational clock, with no-bid and payment-default exits. | Self-created statutory-process diagram from LAW-006, LAW-015, LAW-016, OPS-004 and OPS-006. | The hammer identifies a leading bid; readiness and payment determine whether the sale completes. | Horizontal readiness path from authorized registration to accepted funds, immediate recovery and registration payment, then the three-business-day balance, with branches for no sufficient bidder, immediate re-offer, re-advertisement and resale costs. |
| `figure-40-surplus-proceeds-route.png` | 12 | Follow money above municipal claims into the surplus account and the former interest-holder's court route without implying automatic payment. | Self-created statutory account diagram from MGA ss. 146–147 and HRMC ss. 161–162. | Surplus is held and claimed through a statutory route; it is not a windfall silently awarded to the purchaser. | Sale proceeds first satisfy statutory municipal amounts, then enter a surplus account; after redemption expiry a prior interest holder may apply to Supreme Court before the twenty-year endpoint. |
| `figure-41-map-layer-overview.png` | 5 | Establish the production map's source boundary, current defaults and main research modes. | Production screenshot of NS Marks The Spot source commit `d3114b5c`; full provenance in the screenshot receipt. | Start with the mode, notice and question before choosing a parcel or layer. | Province-wide production map with source link, current notices, historical outcomes and the available public layers visible. |
| `figure-42-province-data-licence.png` | 5 | Put the Province restricted-service explanation, attribution and disclaimer before layer use. | Screenshot of the app's bundled Province-data notice and licence link. | Licence and source limitations are part of the research record, not footer decoration. | Modal explaining Province-data sources, approximate property boundaries and the no-endorsement boundary. |
| `figure-43-current-parcel-browser.png` | 5 | Browse the current Inverness event and filter its published redemption category while keeping the direct official source visible. | Screenshot of the dated production catalogue snapshot; refresh required. | Event filters organize a municipal notice; they do not determine live legal status. | Current-parcel list with municipality, event date, snapshot note, direct-source link and redemption filter. |
| `figure-44-civic-address-search.png` | 5 | Show an authoritative civic-point search returning its containing parcel. | Production screenshot using `11064 Highway 19`; dated location demonstration only. | A contained civic point can find a parcel without proving access, occupancy or ownership. | Exact civic-address result and selected parcel shown together, with authoritative-result language visible. |
| `figure-45-current-parcel-evidence.png` | 5 | Read PID, mapped area, civic point, Plus Code, road/water results and limitations as one bounded parcel sheet. | Production screenshot using PID `50292390`; not a current-notice recommendation. | Read the inspector's bounded words before interpreting the parcel shape. | Selected parcel with authoritative civic result, Plus Code, mapped context and explicit evidence limits. |
| `figure-46-aerial-and-property-boundaries.png` | 5 | Compare dated aerial context with graphical parcel boundaries. | Screenshot using NS Aerial and NSPRD services under the in-app attribution. | Imagery plus a boundary service is still neither a survey nor a current site inspection. | Selected civic parcel on NS Aerial with graphical property-boundary linework and source attribution. |
| `figure-47-roads-water-context.png` | 5 | Compare visible transport/water context with exact mapped-intersection results. | Production screenshot using current-notice PID `50308311`; dated demonstration only. | Nearby transportation and a mapped water intersection are separate clues, not access or environmental conclusions. | Southside River Denys parcel sheet showing current notice facts, River Denys intersections and no mapped road/trail intersection. |
| `figure-48-geology-resources.png` | 5 | Screen geology, mineral occurrences, mineral tenure and abandoned mine openings without inferring parcel value or condition. | Production screenshot of the app's Province/open-data resource layers. | Resource layers start records questions; they do not establish reserves, rights, contamination or economic potential. | Selected parcel with geology and resource controls active and map symbols visible. |
| `figure-49-historical-outcomes-overview.png` | 5 | Switch from current notices to a dated catalogue of verified historical outcomes. | Production screenshot of the 2022–2025 Halifax historical filter state. | Historical outcomes describe completed events; they do not forecast another auction. | Historical mode, event-year filters, exact-PID coverage statement and result list visible. |
| `figure-50-historical-outcome-sheet.png` | 5 | Read one exact-PID historical result with opening amount, winning amount and direct official sources. | Production screenshot using historical PID `00542589`; dated event demonstration only. | One result describes one event, not current value or a comparable-sale model. | Halifax March 8, 2022 result sheet with official notice/result links, difference/ratio fields and historical disclaimer. |
| `figure-51-combined-parcel-research.png` | 5 | Close the chain with current notice, exact parcel, civic aids, road/water context and resource layers in one state. | Production screenshot using current-notice PID `50113968`; dated demonstration only. | Separate what the screen reports from what remains for authoritative records and qualified professionals. | Soapstone Mine Road parcel sheet, civic results, Plus Codes, road/water observations and geology/resource layers together. |

## Map-pack source record

Each of the fifteen map plates needs its own provenance row before rendering:

| Field | Required value |
|---|---|
| Figure ID | Stable `figure-XX` identifier. |
| QGIS project/layout | Versioned local source path and layout name. |
| Geometry status | Fictional composite, neutral public demonstration or approved completed-sale example. |
| Layer sources | Publisher, dataset/service title, URL or endpoint, retrieval date and licence. |
| CRS and scale | Printed on the map and in this register. |
| Interpretation status | Verified record, screening clue, visual interpretation, professional verification or no-go. |
| Attribution | Exact open-data and/or restricted-service statement, rendered into the image. |
| Safety check | No owner name, live recommendation, hidden personal information, provincial mark or implied endorsement. |

## Creation and promotion order

1. Treat figures 03–08, 39–40 and the two QGIS renders as pre-gate development
   evidence created under the user's explicit requests to work on maps and
   slideshow figures. None may be promoted into canonical chapter placement by
   that fact alone.
2. Preserve the approved thirteen-chapter argument outline and 51-figure visual direction while final figures remain separately gated.
3. Use figures 03–08 and 39–40 as the diagram-system proof, then create one **map style
   proof**, preferably `figure-15-case-a-access-terrain.png`, because it tests
   QGIS labels, colour semantics, attribution, phone legibility and Echo's 16:9
   video stage at once.
4. Export the style proof to PNG, embed it in a tiny test EPUB and inspect it in
   Echo on phone-size and desktop-size stages.
5. Export a 60–90 second video range in Karaoke and Simple modes. Check figure,
   caption, subtitle band, attribution legibility and SRT timing.
6. After the web interface freezes, recapture figures 41–51 and run the same
   phone/desktop/video checks against the source receipt.
7. Lock the template, then batch the remaining map families and diagrams.
8. Generate the two editorial illustrations only after the visual grammar is
   stable; they should feel like the same book, not unrelated AI art.
9. Insert figures into chapter Markdown only after the matching narration and
   placement paragraph are stable.

## Figure QC and acceptance

Every finished figure must pass:

- rights/provenance record complete;
- public-safety scan complete;
- factual values and labels checked against the cited source;
- meaningful alt text and standalone caption;
- figure understandable at 1920 by 1080 video scale and a phone-size Echo stage;
- attribution legible in the exported MP4 frame, not only in an EPUB appendix;
- colour meaning survives grayscale and common colour-vision differences;
- map never described as a survey, title opinion, access proof, environmental
  conclusion, appraisal or recommendation;
- narration remains understandable when the figure is unseen;
- Echo cue appears during the intended paragraph and falls back cleanly at the
  chapter boundary; and
- a human watches at least the short proof export before the figure system is
  accepted for the whole book.

## Future export set

When the final aligned package exists, produce and verify:

- whole-book 1920 by 1080 Karaoke MP4;
- whole-book SRT and chapter timestamp sidecars;
- whole-book Simple-mode MP4 if Karaoke render time or visual intensity is poor;
- a short public demo range containing one map, one chart and one legal-process
  diagram; and
- later, only if requested, vertical or square clips from the same 16:9 masters
  using layouts revised for those aspect ratios rather than automatic cropping.
