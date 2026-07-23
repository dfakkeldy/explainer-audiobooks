# Nova Scotia tax-sale audiobook development packet

## Beyond the Tax-Sale Packet

**Status:** the governed-final 54-figure EPUB and 4:12:50 audiobook have passed
package checks, completed Dan's full listening review and received explicit
publication authorization. The two Touquoy passages were accepted in context,
but their canonical pronunciation remains unverified. Portrait/landscape video
publication and second-device proof remain separate.

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
  conversation decision log, handoff packet, and approved-for-pilot 54-figure visual direction;
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
  specifications, paired contact sheets and hash-bound receipts, including 14
  production-map screens in both landscape and genuine mobile-browser profiles;
- `chapters/`: canonical Chapters 1–13, drafted sequentially from the accepted
  pilot and approved argument outline, including the major map-method rewrite
  and its access, intended-use, environmental, title, cost, auction, tender,
  payment, and failed-sale branches;
  and
- `chapters/images/`: the complete 54-figure landscape review set, including 14
  refreshed 2560-by-1440 NS Marks The Spot walkthrough screenshots; none is yet accepted
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
- private governed renderer scratch and pronunciation-review artifacts; the
  public package includes only the verified M4B and portable alignment sidecar.

The interactive implementation remains in the
[NS Marks The Spot repository](https://github.com/dfakkeldy/ns-marks-the-spot)
and [live map](https://kinnokilabs.com/apps/nsmarksthespot/map/) rather than
being duplicated here. The 2026-07-22 paired screenshot receipt pins production
source commit `a7ba7da9ad5f8a5dcc1c67c79888bb76b6bae108`. This repository owns the
book-development packet, its reproducible QGIS proofs and version-stamped
chapter screenshots.

## Current production gates

The approved text edition has completed governed whole-manuscript review. Dan
approved the prior
twelve-chapter outline and forty-figure visual direction on 2026-07-19, accepted
the exact three-card Inverness Packet Atlas direction with “I like them,” and
accepted the exact first-section teaching and voice with “Let’s go for the
voice.” On 2026-07-20 he authorized redesigning the map chapter and
review figures around the production workflow: notice → parcel → context →
unknowns → handoff, then explicitly approved that thirteen-chapter, 51-figure
direction for pilot development. On 2026-07-22 he approved expanding the same
direction to 54 figures with paired landscape and genuine mobile-browser map
captures. The current four-chapter wording refresh is an exact-hash review
candidate recorded in `research/review-revision-receipt.json`; it does not
inherit the earlier manuscript, narration, listening, figure, video or
publication approvals. Deep research,
structured chapter plans, coverage paths, two QGIS proofs, eight reproducible
diagram candidates and three accepted-direction atlas prototypes exist. The
actual Echo/video-stage atlas proof, atlas batch authorization, accepted final
figures and full-audio human acceptance all remain pending. The exact earlier
Pictou-fixed M4B is separately authorized for public-first-listen publication;
that authorization does not transfer to the revised 54-figure candidate.
The final-hash structure and blind sequential beginner reviews,
bounded humanizer/tightening pass, rendered ear-pass diagnostics and governed
text-only EPUB build are complete. The public reader package is under
`books/beyond-the-tax-sale-packet/`; the governed M4B is included, while no
video is claimed.

The governed nonpackage pilot rendered on 2026-07-20 at 14:27 with verified
alignment and a clean pronunciation audit. Its exact SHA-256 is
`c94570d369b1c5f3842f111f151a9e4bb880db2d84ceeed86f3cfed44c974f1c`;
Dan accepted that exact pilot for continued drafting with “continue” at
2026-07-20T08:55:51-03:00. Canonical Chapters 1–13 now total 32,189 Markdown
words after the initial independent review and the bounded humanizer pass
recorded in `research/editorial-review.md` and
`research/humanizer-decisions.json`. Eight local style edits remove generic
chapter navigation, and three post-edit beginner-review repairs clarify the
parcel-register record, expand NSPRD at first use and preserve the treasurer as
the certificate-registration actor.
Dan approved the exact thirteen-chapter EPUB manuscript text for public
publication on 2026-07-21 and requested the anonymous Chapter 5
mineral-occurrence revision on 2026-07-22. The approval is hash-bound in
research/publication-authorization.json; any chapter-byte change requires a new
manuscript verdict. Dan selected Candidate 1, *The Packet Lifts*, as the paired
EPUB/audiobook cover on 2026-07-21; `covers/cover-selection.json` binds the
portrait, square and source-art hashes. The remaining figure, ear-pass, package,
full-narration and video gates remain separate. The governed public EPUB embeds
the selected portrait cover byte-for-byte and is verified at SHA-256
`12a0822a8c89babc26b160f75d44128ea4056c1624707961dcd9c2061464b37a`.

The earlier 3:57:37 ear-pass render remains diagnostic evidence rather than a
promotable package. `research/audiobook-candidate-audit.md` records why a
controlled wrapper-only rebuild from the frozen public EPUB is required, and
`audiobook-acceptance-checklist.md` defines the next human gate. Neither file
claims pronunciation acceptance, full-audio acceptance, publication, website
deployment, video work, figure promotion, or second-device proof.

Dan rejected that first controlled candidate after hearing **Pictou** as
“picktoau” and specified **“PICK-toe.”** The exact negative verdict remains
bound in `research/audiobook-human-listening-verdicts.json`; it did not reopen
the approved text or cover.

A fresh wrapper-only replacement is now complete as a private first-listen
candidate: 13 chapters, 14,256.597333 seconds, exact M4B SHA-256
`f675ba1fde72aed5f7885931289f2d0dbb1b94e361f063012ab5bacbaeb1d4b8`.
Its complete automated audit proves all five Pictou occurrences use the
long-o `pˈɪktO` override and none use rejected `pˈɪktaʊ`. The selector-bound
delivery chain, 612-anchor sidecar, selected square-cover identity, archive
integrity, full decode and acoustic scan pass.
`research/audiobook-candidate-receipt.json` preserves those machine results
while leaving replacement pronunciation and full-book human listening
pending. The M4B and renderer work state remain outside the public repository.

The revised 54-figure edition now also has a fresh private first-listen M4B:
13 chapters, 15,170.090667 seconds (4:12:50.091), exact SHA-256
`f56220fea72c767a225a1538ad70c0e160763830bd15bb9bc2cb9f0fe474c505`.
It is bound to the current 54-figure EPUB at SHA-256
`b2399f3850e98050fe58e913ba1bd8cfd1cc5a86331b4b3a4f884959f82d666d`.
The selector-bound delivery chain, complete 248-decision pronunciation audit,
735-anchor alignment sidecar, 13 ordered chapter markers, selected cover,
archive integrity, full decode and acoustic scan pass. All five Pictou
occurrences use the accepted long-o override. The audit also exposes two
Touquoy occurrences produced by generic fallback; no authoritative
pronunciation guide was found during the unattended pass, so those samples are
explicit priority human checks rather than accepted pronunciations.
`research/audiobook-54-figure-first-listen-receipt.json` preserves the exact
machine evidence. Dan then reported “I listened, sounds good” and explicitly
authorized publication on the tax-sale page and in the Listening Room.
`research/audiobook-54-figure-publication-receipt.json` binds that verdict and
authorization to the exact M4B. The public package now carries the matching
54-figure EPUB, M4B and alignment. Private renderer work state remains outside
the repository. The rendered Touquoy passages are accepted for this edition,
but the receipt does not claim that their pronunciation is canonical.

The three accepted-direction atlas prototypes remain development evidence, but
the remaining 42-card batch is paused. Review should first decide whether the
living map now performs most parcel-orientation work more accurately and
usefully than a static owner-free atlas.

## Safety and currency

This material is educational only. It is not legal, tax, investment, title,
surveying, appraisal, access, environmental, insurance, planning, tenancy, or
construction advice. Municipal lists and procedures change. The legal and
event research was refreshed against official sources on 2026-07-19, the
Chapter 5 mineral-resource sources on 2026-07-22, and the Chapter 6–11
planning, access, environmental, title, occupancy, mobile-home,
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
