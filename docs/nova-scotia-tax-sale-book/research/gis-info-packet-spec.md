# GIS and Property Online information-packet design

## Product split

The safest and most useful design is two related products:

1. **Public companion packet:** a reusable method, QGIS project template, open-data and licensed-service catalogue, aggregate municipal examples and fictional/completed-sale demonstrations. Rendered NS Aerial and NSPRD views may be shared under the Province's Restricted Geographic Services License when its conditions are carried into the artifact.
2. **Private live-sale worksheet:** PID-specific Property Online research, registry documents, observations and decision notes for the current bidder. This is not distributed with the public book.

That separation avoids turning a public book into a live-property recommendation service and lets the public artifact remain useful after the August 2026 list changes. It is not a claim that the provincial map services are unshareable.

## Municipal baseline, not blank canvas

Inverness's August 2026 packet already contains a tabular parcel/account summary, aerial image with parcel overlay, Property Online parcel map and registry legal description for its detailed entries. A companion that merely recreates those pages would be duplicative. The defensible value-add begins with reconciliation and additional questions: current planning controls, terrain and water, apparent versus legal access, geology/minerals/mines, coastal and environmental screening, record limitations, and a source-traceable professional handoff.

## Public QGIS layer stack

Prefer datasets explicitly offered under the Nova Scotia Open Government Licence, with retrieval dates and attribution:

- municipal and community boundaries;
- roads, trails and rails;
- topography, contours and landforms;
- Crown land;
- mineral occurrences, bedrock and surficial geology;
- abandoned mine openings and drillholes;
- environmental registry points or linked records where a reusable spatial service exists;
- coastal-hazard screening layers whose scenario and scale are carried into the legend;
- current Inverness zoning, provided the municipality's reproduction terms permit inclusion; otherwise link to the official map.

Required attribution for open provincial data when no more specific statement is supplied: `Contains information licensed under the Open Government Licence – Nova Scotia.`

## Province restricted-service material that may be publicly displayed

- NS Marks The Spot already ships public display of the Nova Scotia Orthophotomap Database service and NSPRD property-boundary service under the Province of Nova Scotia Restricted Geographic Services License.
- That licence permits viewing the information in any medium, mode or format for a lawful purpose. A public packet may therefore contain properly attributed rendered map views from those services.
- Every such view must include the Province's required attribution and disclaimer: `Contains information obtained under license from the Province of Nova Scotia which is provided without warranty or liability for errors or omissions.`
- An application must link to the licence. For a PDF/EPUB companion, include the licence link or a bundled copy in the data-sources section and keep the non-endorsement, no-warranty and suitability boundaries visible.
- The licence does not authorize personal information, third-party rights, provincial logos or marks, or a suggestion of government endorsement.
- The safe grant is public **viewing**. Do not assume it also authorizes bulk redistribution of raw service data, a packaged tile cache or a reusable parcel database; those uses should follow the service's technical restrictions and any additional permission requirements.
- Registry plans and documents obtained through Property Online are distinct from the NSPRD map service. Their reproduction terms still need to be checked separately before public inclusion.
- Municipal zoning maps and other website materials need their own copyright check; a public link may be safer than embedding the image.

Sources: NS Marks The Spot's verified [public web implementation at
`92f1261e5`](https://github.com/dfakkeldy/ns-marks-the-spot/tree/92f1261e5/web),
native `Layers/LayerCatalog.swift`, and bundled
`Layers/ProvinceRestrictedGeographicServicesLicense.md`; [GeoNOVA property-data
product description](https://geonova.novascotia.ca/sites/default/files/resource-library/GeoData_NSPRD.pdf);
[Nova Scotia Open Government Licence](https://support.novascotia.ca/services/open-data-portal-licence);
and [Nova Scotia copyright policy](https://www.novascotia.ca/copyright).

## Five-map packet

For each worked parcel, the packet can contain:

1. **Orientation:** community, public roads, water, scale and north arrow.
2. **Identity:** AAN/PID reconciliation and a clearly labelled NSPRD graphical parcel outline, never called a survey, with the Province's restricted-service attribution.
3. **Access and terrain:** road classification, apparent approach, contours, watercourses and questions about legal frontage or rights-of-way.
4. **Planning and services:** current zone, relevant overlay, known service areas and the exact municipal confirmation still required.
5. **Physical-screening map:** attributed NS Aerial imagery with geology, mines, coastal and environmental indicators, each carrying its source limitation.

The packet should also include a one-page **delta from the municipal packet**: which municipal facts were reused, which new sources were added, which conflicts were found, and which questions remain outside the researcher's authority.

Every map should display map ID, PID or fictional parcel ID, retrieval date, source and licence, coordinate reference system, scale, a `not a survey or title opinion` statement and a short list of unresolved questions.

## Evidence table behind the maps

Each layer observation should be classified as one of:

- `verified record`: the source directly supports the statement;
- `map-screening clue`: location or overlap needs verification;
- `visual interpretation`: a feature appears in imagery but is not confirmed;
- `professional verification needed`: lawyer, surveyor, planner, engineer or environmental professional must answer it;
- `no-go until resolved`: the proposed use should not support a bid while the issue remains open.

The key principle is that spatial overlap is not causation, legal access, title, contamination or buildability.

## Implemented QGIS 4 proof and web-companion result

On 2026-07-18, the first live Inverness technical proof was completed locally
with QGIS 4.0.2. The municipality's 45 liens contain 47 unique PIDs. A live
NSPRD query resolved every PID and returned 53 polygon features; four PIDs are
represented by multiple polygons. The saved `.qgz` project reports QGIS
`4.0.2-Norrköping`, and both proof renders are 2560-by-1440 PNGs.

The public-safe auction dataset contains lien, AAN, PID, general location,
advertised recovery amount and redemption marker. It deliberately excludes
assessed-owner names. The raw NSPRD geometry snapshot remains local and is not
part of the proposed public distribution.

A static interactive companion is technically feasible without publishing a
parcel database. It should:

1. ship only the owner-free municipal listing JSON;
2. query matching PIDs from the provincial NSPRD ArcGIS endpoint at runtime;
3. offer NS Aerial as a user-controlled provincial tile basemap;
4. open on a legible county overview, then zoom to the selected lien;
5. persist the municipal snapshot date, live-list link, exact provincial
   attribution, licence link and `not a survey or title opinion` warning; and
6. fail visibly when a provincial service is unavailable instead of silently
   substituting a stale parcel cache.

This architecture lets the QGIS print proof and the website share one
owner-free listing source while keeping restricted-service geometry and imagery
at the Province's display boundary.
