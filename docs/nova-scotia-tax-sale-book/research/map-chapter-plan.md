# Proposed Chapter 5 — The Map Is a Question Machine

Status: **outline and screenshot candidates for review**. This chapter expands
the previously approved twelve-chapter/forty-figure direction. It is not yet an
approved chapter, and the screenshots are not final publication assets.

## Chapter job

Teach a listener to use the public NS Marks The Spot map as a disciplined first
research pass for a Nova Scotia tax-sale parcel: select the right event, find one
PID, turn on one layer at a time, write down bounded observations, and route each
new question to the source or professional capable of answering it.

The chapter belongs after **Give the Parcel a Biography** and before the
access and environmental case studies. That placement lets the listener first
understand source hierarchy, then practise it in the map, then see where the map
fails in the landlocked and environmental cases.

Proposed length: approximately **3,400 words**. The revised book would contain
thirteen chapters and approximately 46,200 words before editorial compression.

## Learning delta

By the end, the listener should be able to:

1. verify the municipal event and notice snapshot before exploring parcels;
2. search an exact PID and distinguish notice facts from mapped context;
3. explain what each available layer can show and what it cannot establish;
4. compare apparent proximity with the map's exact intersection result without
   turning either result into a legal or environmental conclusion; and
5. leave a dated research note containing the observation, limitation, next
   authoritative source and professional handoff.

New core terms are limited to **layer** and **mapped intersection**. The
road-book reset is always one parcel, one toggle and one note.

## Throughline

The map is not a verdict machine. It is a question machine.

An overlap does not prove ownership, access, buildability, flooding or site
condition. An empty result does not prove the feature is absent. Each screen
state is a dated view of municipal notice data and provincial map services whose
coverage, scale, currency and legal authority differ.

## Argument and scene plan

### 1. Start with the notice, not the imagery

- Open the Province-data explanation before using restricted geographic
  services. Explain why licence, attribution and service limits belong inside
  the research record.
- Choose the correct municipality and sale date. Read the notice snapshot date,
  then open the direct official source to confirm that the sale and parcel are
  still current.
- Use the redemption filter only to organize the notice. It does not change or
  interpret the legal status of a parcel.

Landing beat: the map helps the listener find a municipal record; it does not
replace the municipality.

### 2. Find one PID and change one layer at a time

- Search the exact PID and read the parcel inspector before zooming into visual
  detail.
- Keep the modern map as orientation. Treat Fletcher historical mapping as
  unavailable while public-web display rights remain unresolved.
- Turn layers on one at a time. Say aloud what changed and what did not.
- Treat approximate mapped acreage as an NSPRD geometry calculation rather than
  a survey or deed area.
- Compare nearby linework with the exact intersection lists. A feature that
  appears nearby may not intersect the selected polygon; a returned intersection
  is a map-service result, not proof of legal access or physical condition.

Landing beat: visual confidence falls as the research note becomes more precise.

### 3. Turn pixels into a research record

For every useful observation, record:

| Field | What to write |
|---|---|
| Question | The parcel-specific uncertainty being investigated. |
| Source/layer | Exact layer or municipal notice used. |
| Observation | Neutral wording such as “mapped water feature intersects.” |
| Retrieval | Event snapshot date, access date and, for production, app version. |
| Limitation | Scale, currency, coverage or authority boundary. |
| Next source | Municipal notice, Property Online, survey, planning record or other authoritative record. |
| Handoff | Lawyer, surveyor, planner, environmental professional or other qualified reviewer when required. |

### Worked example: Southside River Denys

Use PID `50308311` only as a dated interface demonstration, not as a property
recommendation. In the captured build the parcel inspector reports approximately
5.12 mapped acres, returns mapped water-feature intersections including River
Denys, and returns no mapped road/trail intersection. The visible transportation
line nearby and the empty intersection result create an access question; they
do not establish either access or no access. The water result creates a physical
and environmental research question; it is not a wetland determination, flood
opinion or site inspection.

Before publication, refresh this example against the live municipal notice and
current map build. If the parcel leaves the sale or the service result changes,
replace it with a fictionalized or completed-sale example while preserving the
same research method.

## What each layer contributes

| Map control | Useful for | Must not be narrated as |
|---|---|---|
| Modern map | Community, road and place-name orientation. | Current legal access, boundary or official property fact. |
| Fletcher historical map | Historical context if rights become available. | Available for public use in the current build; it is intentionally disabled. |
| NS Aerial | Visible land-cover, building, shoreline and approach clues at the imagery date. | Current condition, lawful access, boundary, occupancy or inspection. |
| NS Property Boundaries | Locating the selected NSPRD geometry and comparing nearby mapped parcels. | A survey, legal description, title opinion or guaranteed area. |
| Crown Lands | Screening nearby mapped Crown-land context. | Proof that the selected parcel is Crown land or that public access exists. |
| Flood Risk Areas | Watershed-scale flood-risk screening where the service has coverage. | A parcel-specific flood certificate, insurance decision or future-condition guarantee. |
| Waterfalls | Regional landscape and named-feature orientation. | Core parcel due diligence or proof of water on the selected parcel. |
| Water features | Mapped rivers, lakes, wetlands and water linework; exact polygon intersections where returned. | A current wetland delineation, water quality result, setback decision or site condition. |
| Roads, trails & culverts | Mapped transportation classes, proximity and exact polygon intersections where returned. | Legal right-of-way, maintained frontage, passability, culvert condition or permission to enter. |

The current public build deliberately does not offer well or septic layers. The
available public records have different locations, dates and precision, so those
questions remain in the records-and-professionals part of the book.

## Screenshot sequence

The eleven 2560-by-1440 candidates live in `chapters/images/`. They were captured
from NS Marks The Spot source commit `1ee76d15b2466d40674e62113ac9f1e9044421c1`
on 2026-07-19 and are review evidence, not accepted final figures.

| Figure | Teaching job | Planned narration cue |
|---|---|---|
| 41 — map-layer overview | Establish the control panel and all available toggles in their off state. | “Before we add information, notice what the map is already claiming—and what it is not.” |
| 42 — Province-data licence | Explain the source/licence boundary before activating provincial services. | “The permission and disclaimer travel with the picture.” |
| 43 — tax-sale notice filter | Choose municipality/event and isolate the redeemable category. | “This filter organizes the notice; it does not decide the law.” |
| 44 — PID search and inspector | Search PID `50203256` and separate notice fields, mapped area and intersection results. | “Read the words before trusting the shape.” |
| 45 — aerial plus boundaries | Show how imagery and parcel linework answer different questions. | “Two layers can align beautifully and still not become a survey.” |
| 46 — roads, trails and culverts | Reveal transportation classes and the legend. | “A road-coloured line is a clue, not a right-of-way.” |
| 47 — water features | Reveal mapped hydrography and wetlands. | “Blue linework starts a water question; it does not finish one.” |
| 48 — Crown Lands | Show public-land context near the selected area. | “Neighbouring Crown context says nothing by itself about this parcel's ownership or access.” |
| 49 — flood-risk areas | Show watershed-scale screening and service coverage. | “The layer speaks at its own scale, not the scale of your hopes.” |
| 50 — waterfalls overview | Demonstrate a regional context layer and why not every layer belongs in every parcel file. | “Useful maps are selected by the question, not by novelty.” |
| 51 — combined River Denys research | Combine boundaries, water and transport with exact inspector results. | “Now write the discrepancy down: water intersects; mapped road does not.” |

## Screenshot production rules

- Keep all masters at 2560 by 1440 with the full app header, control panel,
  attribution footer and any open inspector visible.
- Add a small book-owned title card or callout only after the interface settles;
  do not cover source attribution or imply the book owns provincial data.
- Refresh every screen after the map implementation is declared stable and
  again immediately before publication.
- Preserve figure IDs 41–51 when replacing screenshots so chapter cues and Echo
  timelines remain stable.
- The narration must remain complete when the screen is unavailable. Do not
  recite every checkbox; teach the repeatable method and use the images as
  spatial reinforcement.

## Publication and safety gate

This proposal changes the approved outline from twelve chapters/forty figures
to thirteen chapters/fifty-one figures. Pilot drafting can continue only after
the revised outline and screenshot direction receive explicit approval. Final
screens require a fresh source/version receipt, public-safety scan, phone-size
legibility review and an Echo slideshow/video check.
