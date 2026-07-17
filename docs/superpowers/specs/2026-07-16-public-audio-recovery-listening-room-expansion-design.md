# Public Audio Recovery and Listening Room Expansion — Design

**Date:** 2026-07-16

**Repositories:** `dfakkeldy/explainer-audiobooks`, then `dfakkeldy/KinNoKiLabsSite`

**Public surface:** `https://kinnokilabs.com/listen/`

## Purpose

Recover the eight already-narrated public learning books that are absent from
the browser Listening Room, bring every public M4B up to the current paired
cover convention, publish the verified media packages in the public books
repository, and expand the Listening Room from three playable books to all
eleven public books.

This is a recovery and packaging project, not a new narration project. The
spoken audio, timing, chapter structure, and manuscript content must remain
unchanged.

## Current State

The public catalog lists eleven books but marks only these three as playable:

- *Chicken Predators*
- *Rodents in the Walls*
- *The New Deal*

Recoverable M4B and alignment-sidecar pairs exist outside the public repository
for all eight omitted public titles:

- *Echo, From the Inside*
- *Why It Feels Right*
- *You Are the Architect*
- *The Bug Is a Clue*
- *Tests First*
- *Git Happens*
- *Findable*
- *The Voice in the Machine*

The site builder currently uses a hand-maintained `AUDIO_EXPECTED` allow-list
containing only the three playable slugs. It also rejects M4B or alignment files
for other public slugs, so archived media cannot become playable accidentally.

Git history shows that each recovery candidate postdates its book's last
manuscript change. Later EPUB changes are cover-package changes. That makes the
archived media strong recovery candidates, but current EPUB-block-to-sidecar
parity must still be proven rather than inferred.

## Decisions

### Direct repository publication

The eight recovered M4Bs and sidecars will be committed directly under their
existing `books/<slug>/` directories using ordinary Git, matching the three
current playable packages and the site's immutable raw-GitHub URL strategy.

The recovered M4Bs plus the refreshed Rodents M4B add approximately 630 MB to
repository history. This is an accepted tradeoff for keeping source text, EPUB,
M4B, alignment, cover receipts, and site audio pins within one public commit
lineage. Git LFS, GitHub Release assets, and Cloudflare R2 are out of scope for
this recovery.

### Square M4B artwork for every recovered book

The current convention is one governed visual identity rendered as:

- a 1600 × 2560 portrait `cover.png` embedded in the EPUB; and
- a purpose-composed 2400 × 2400 `m4b-cover.png` embedded in the M4B.

Existing governed square covers remain byte-identical for:

- *Echo, From the Inside*
- *Why It Feels Right*
- *Findable*
- *Chicken Predators*
- *The New Deal*

One square companion will be created for each legacy portrait-only package:

- *You Are the Architect*
- *The Bug Is a Clue*
- *Tests First*
- *Git Happens*
- *The Voice in the Machine*
- *Rodents in the Walls*

Each new square uses the already-approved EPUB cover concept and title. This is
not a new cover-selection round. The square must be purpose-composed for 1:1,
not stretched, letterboxed, or blindly center-cropped. A single contact sheet
is a mismatch/defect review surface, not a request to select among alternatives.

The existing portrait covers and EPUBs remain byte-identical. Each new paired
receipt binds the unchanged portrait, the new square, and the existing EPUB.
Rodents keeps its already-approved `Compact Ribbon / Editorial Footer` identity;
only its square companion, receipt, and M4B artwork are added or refreshed.

### Legacy-artifact compatibility path

The governed narration workflow normally embeds the selected square cover
before M4B acceptance and forbids later mutation. These recovered files predate
that workflow, so they qualify for the repository's explicit legacy-artifact
compatibility path: `skill/scripts/replace_m4b_cover.py`.

Artwork replacement is accepted only if the post-change M4B retains the exact:

- decoded audio-packet SHA-256;
- duration;
- chapter count, titles, and boundaries;
- stream codec/type structure;
- non-artwork format tags; and
- alignment sidecar bytes.

The replacement artwork must match `m4b-cover.png` after normalized RGB pixel
comparison.

## Recovery Inputs and Provenance

Absolute archive paths stay outside the public repository. An ignored recovery
workspace records the operator's source paths and pre-promotion hashes. The
public recovery receipt records only safe durable evidence:

- slug and title;
- recovered source M4B SHA-256;
- recovered sidecar SHA-256 and anchor count;
- source media signature;
- current EPUB SHA-256 and exported-block count;
- sidecar-to-current-block resolution count;
- selected portrait and square cover hashes;
- final M4B SHA-256 and unchanged media signature; and
- final public package paths.

No raw narration scratch, local absolute path, private book, ignored build
research, or unrelated archive content enters Git.

## Explainer Audiobooks Changes

For each recovered book package:

1. Copy the selected recovery M4B and alignment sidecar into a private ignored
   staging directory.
2. Validate that the M4B is decodable and has a non-empty chapter table.
3. Export blocks from the current public EPUB with the current Release
   `echo-cli export-blocks` command.
4. Require every sidecar anchor to resolve to a current EPUB block ID, with
   non-empty monotonic timestamps.
5. Reuse the existing governed square cover or create the one missing square
   companion from the approved portrait concept.
6. Create or update paired-cover specification, render, thumbnail, and selection
   receipts without modifying the portrait or EPUB.
7. Record the source media signature, replace only the embedded artwork through
   the legacy compatibility tool, and require an unchanged post-replacement
   media signature.
8. Promote the verified M4B and unchanged sidecar to `books/<slug>/`.
9. Update the book README to describe the portrait/square pair and playable
   browser edition.

Run the same cover-only media-signature path against the already-public Rodents
M4B: create its square companion from the approved portrait concept, replace its
embedded portrait artwork, prove the media signature unchanged, and update its
receipt/README without altering its EPUB, alignment, or narration.

A public recovery manifest and contact sheet document the complete eight-book
recovery plus the six new square companions. Promotion is fail-closed: no
recovery commit is accepted while any book has unresolved anchors, a changed
media signature, invalid artwork identity, missing provenance, or a file at or
above the host's ordinary Git file-size boundary.

No manuscript, EPUB body, pronunciation, narration voice, alignment timing,
flashcard deck, or private delivery folder changes are in scope.

## KinNoKi Labs Site Changes

The site change depends on a pushed public Explainer Audiobooks package commit.
It will:

1. Change `AUDIO_EXPECTED` from the three current slugs to all eleven public
   slugs in catalog order.
2. Regenerate `Resources/listen/books.json` from the exact public package commit.
3. Stage `blocks.json`, `alignment.json`, and the current cover derivative for
   every playable book.
4. Preserve the existing catalog-relative figure pipeline and selected-book
   behavior.
5. Regenerate committed `Output/` through the site generator rather than editing
   generated files directly.

The site continues streaming M4Bs from SHA-pinned raw-GitHub URLs. No audio is
copied into the site repository.

The library heading or supporting copy should state the playable total so the
selected book being omitted from the grid cannot make eleven streams look like
ten.

## Failure Handling

- Missing or unreadable recovery source: stop that book before staging.
- M4B at or above the public Git file-size boundary: stop and redesign hosting;
  do not recompress or split audio silently.
- Current EPUB block mismatch: stop and reconcile the exact narrated edition;
  do not publish desynchronized captions.
- Media signature drift after artwork replacement: discard the replacement and
  retain the source artifact unchanged.
- Square-cover mismatch or illegible 1:1 composition: repair that one derived
  square without changing the approved portrait concept.
- Public package push unavailable: do not create a site catalog commit with
  unreachable raw URLs.
- Any package fails final verification: keep the site at its existing playable
  set until the complete approved batch is ready.

## Test-Driven Implementation

Implementation follows red-green-refactor sequencing.

### Explainer repository

Tests are added or tightened before promotion to require:

- the eight recovered public M4B and sidecar paths;
- a valid square M4B cover and paired receipt for all eleven public titles;
- exact EPUB portrait identity;
- normalized M4B artwork identity;
- complete, monotonic sidecars;
- current EPUB block resolution for every anchor;
- non-empty M4B chapter tables; and
- recovery-manifest coverage of all eight slugs.

The initial red run must fail because the eight public media packages and six
square companions are absent. Package promotion plus the Rodents cover-only
repair is the minimal green change.

### Site repository

Catalog tests are changed first to expect eleven playable titles, eleven complete
asset directories, and Listen actions for all catalog entries. The initial red
run must fail against the three-title `AUDIO_EXPECTED` set. The minimal green
change expands the gate and regenerates catalog assets from the verified public
package commit.

DOM tests also require an explicit playable-total label while preserving the
rule that the selected book is not duplicated in the library grid.

## Verification

### Explainer package gate

- focused recovery, cover-receipt, M4B-replacement, and EPUB-block tests;
- full repository test suite and skill validation;
- `unzip -t` for all eight current EPUBs;
- `ffprobe` chapter/stream/tag inspection for the eight recovered M4Bs and the
  Rodents source/final pair;
- full `ffmpeg` audio decode of the eight recovered final M4Bs and refreshed
  Rodents M4B;
- source/final audio-packet hash equality;
- sidecar JSON validation and 100% current-block resolution;
- normalized embedded-art equality with each `m4b-cover.png`;
- eight-book public recovery receipt validation; and
- `git diff --check` plus explicit repository status.

### Site gate

- catalog, core player, DOM, accessibility, contrast, and paired-cover tests;
- complete Node test suite;
- generated-site parity;
- Swift package build through the machine's build gate;
- local HTTP `206` byte-range checks for all eleven SHA-pinned audio URLs;
- browser selection, play initiation, chapter seek, and read-along checks for all
  eleven titles; and
- Cloudflare Pages check after publication authorization and PR creation.

Audible full-book listening is not required for a cover-only remux when the
audio-packet hash is unchanged, but a short opening playback smoke is required
for every recovered title.

## Publication Order and Review Gates

1. Commit the approved design.
2. Commit the detailed implementation plan.
3. Execute and verify the Explainer Audiobooks recovery branch.
4. Present the six-square contact sheet and final eight-book recovery plus
   Rodents cover-modernization receipt as verification evidence.
5. Obtain Dan's explicit acknowledgement that the package PR is ready to exist,
   then push/open it against `main`.
6. Merge or otherwise establish the exact public package commit before creating
   the dependent site catalog commit.
7. Execute and verify the KinNoKi site branch against that exact commit.
8. Obtain Dan's explicit acknowledgement that the site PR is ready to exist,
   then push/open it against `main`.
9. Verify hosted checks and the custom-domain production surface after merge.

No direct push to `main`, automatic public publication, iCloud replacement, or
private-book promotion is authorized by this design.

## Success Criteria

- All eight recovered public books have committed M4B and alignment sidecar
  packages.
- All eleven public books use the portrait-EPUB/square-M4B convention.
- Recovered M4Bs retain exact audio, chapters, streams, tags, duration, and
  timing while embedding approved current artwork.
- All alignment anchors resolve against the current public EPUBs.
- The Listening Room exposes eleven playable books from one immutable public
  package commit and makes that total unambiguous.
- Both repositories pass their complete local verification gates, and public
  deployment remains behind explicit PR acknowledgement and hosted verification.
