# Claude Platform Public Audiobook Series Design

Date: 2026-07-18
Status: approved in conversation; written-spec review pending
Related curriculum: `2026-07-14-claude-platform-audiobook-series-design.md`

## Purpose

Publish the first two completed Claude Platform documentation audiobooks as a
real series in the public Explainer Audiobooks library and make that series a
first-class part of the KinNoKi Labs Listening Room at `/listen`.

The work also permanently relaxes one over-restrictive production rule. A
public-safe audiobook with explicit publication authorization may be published
as a **public first-listen edition** before the creator completes a full human
listen, provided all non-human publication gates pass and the public status is
described honestly. Human listening remains valuable evidence, and a later
negative verdict supersedes the public-first-listen edition, but listening is
no longer a prerequisite for publication.

## Authorization Evidence

Dan made the following decisions in conversation on 2026-07-17 and 2026-07-18:

- publish both completed Claude Platform volumes now;
- make the first-listen publication rule a permanent workflow change rather
  than a one-series exception;
- use a first-class catalog series model rather than title/slug inference or a
  separate series microsite;
- publish Volume 1 under the clean public slug
  `claude-platform-01-the-message`, leaving its private package untouched;
- retain the existing `/listen?book=<slug>` player route;
- feature the Claude Platform series in the Listening Room;
- keep only published volumes playable and avoid empty future-volume cards;
- retain public-safety, rights, media, cover, alignment, and disclosure gates;
- create no new iCloud copy as part of publication.

## Current State

Two governed private packages already exist:

1. **The Message: Conversations, Content Blocks, and the Messages API**
   - 12 chapters;
   - native Echo `am_michael` M4B;
   - paired portrait and square cover;
   - valid EPUB, alignment sidecar, pronunciation audit, and governed render
     receipts;
   - human listening completed through Chapter 2, with the remainder pending.
2. **Making Claude Think and Respond Reliably: Reasoning, Multimodal Inputs,
   Structured Output, and Streaming**
   - 13 chapters;
   - native Echo `am_michael` M4B;
   - user-selected Candidate 3, *Event by Event*, as the paired cover;
   - valid EPUB, alignment sidecar, pronunciation audit, and governed render
     receipts;
   - full human listening pending.

The public Explainer Audiobooks repository already hosts complete playable
books. KinNoKi Labs consumes that repository through a transactional catalog
builder that creates `Resources/listen/books.json`, staged cover derivatives,
read-along blocks, and alignment files. Public audio URLs are pinned to an
exact merged Explainer Audiobooks commit.

The current Listening Room catalog is flat. It has no series schema, and the
client renders every non-selected title under one “Also in the library” list.

## Goals

- Publish clean public packages for Volumes 1 and 2 without mutating either
  private master package.
- Preserve the exact accepted M4B and sidecar bytes unless verification proves
  they cannot be reused.
- Add a general, versioned series model that can support the remaining approved
  Claude Platform volumes and unrelated future series.
- Make Volume 1 the default Listening Room selection while preserving explicit
  `?book=` deep links.
- Show series identity, volume order, availability, and previous/next
  navigation without creating placeholder books.
- Keep public-first-listen status plain, accurate, and data-driven.
- Fail closed before either repository exposes broken or unmerged media.
- Update the shared audiobook skill so future explicitly authorized public
  first-listen releases follow the same policy.

## Non-Goals

- Do not rewrite or re-record either manuscript merely to publish it.
- Do not rerender audio unless the existing governed media fails exact package
  verification.
- Do not copy private research folders, environment receipts, raw render state,
  local filesystem paths, or internal listening evidence into Git.
- Do not create a separate `/listen/series/<slug>/` application or duplicate
  the player.
- Do not infer series membership from titles or slug prefixes.
- Do not display Volumes 3–9 as empty, disabled, or “coming soon” cards.
- Do not redesign the whole Listening Room or add a top-level navigation item.
- Do not create a new iCloud reading copy.
- Do not claim expert review, human-approved learning transfer, or completed
  human pronunciation acceptance while those states remain pending.

## Publication Policy

### New state: public first listen

The audiobook workflows gain a durable `public-first-listen` publication
state. It is allowed when all of the following are true:

1. the book is classified `public-safe`;
2. the user explicitly grants publication permission;
3. manuscript, source, privacy, rights, and sensitive-content checks pass;
4. the governed EPUB, M4B, sidecar, pronunciation audit, and paired-cover chain
   pass their current validators;
5. the package contains no private paths or internal-only artifacts;
6. the README and public catalog expose that human listening is still pending.

The public edition must not use `final`, `human-approved`,
`learning-validated`, or `pronunciation-accepted` for a pending human state.
Recommended public wording is:

> This edition has passed package and audio checks. The creator’s full
> listening review is still underway.

### What remains fail-closed

Relaxing the listening prerequisite does not relax:

- public-safety classification;
- explicit permission to publish;
- source and image rights;
- private-material scanning;
- canonical manuscript and receipt freshness;
- EPUB integrity;
- M4B, chapter, alignment, and pronunciation-audit integrity;
- paired portrait/square cover identity;
- public destination classification;
- merged and fetchable public media;
- truthful status and AI-authorship disclosure.

### Later listening evidence

A later `continue` verdict promotes confidence without requiring a package
change. A later `revise` verdict or substantive factual problem supersedes the
public-first-listen edition. The correction workflow may replace or temporarily
withdraw the affected public package, but it must preserve the earlier edition’s
provenance rather than silently relabeling it.

## Public Book Packages

The Explainer Audiobooks repository receives:

```text
books/claude-platform-01-the-message/
books/claude-platform-02-thinking-and-reliable-responses/
```

Each public folder contains only reader-facing or public-verification material:

- `<slug>.md`;
- `<slug>.epub`;
- `<slug>.m4b`;
- `<slug>.alignment.json`;
- `cover.png` and `m4b-cover.png`;
- the selected cover’s public-safe specifications, render receipts,
  thumbnails, source art, and `cover-selection.json`;
- `README.md` with source date, AI-authorship disclosure, first-listen status,
  formats, and verification summary;
- a public-safe source map when one exists and contains no private path or
  internal note.

Pronunciation reels, raw pronunciation audits, renderer input receipts,
resume-state receipts, success selectors, narration databases, and internal
learning/research records do not belong in the public folders. Their private
source package remains the provenance authority.

### Volume 1 public slug

Volume 1’s private slug ends in `road-book-v2`. The public package uses
`claude-platform-01-the-message`. The files may be renamed only after byte and
sidecar compatibility checks. The displayed title and embedded media metadata
remain *The Message*; the private edition is not moved or altered.

### Cover and publication receipt

Both public packages reuse the exact user-selected paired cover art. A fresh
public selection receipt records:

- the clean public slug;
- `selection_source: user`;
- `privacy_classification: public-safe`;
- explicit publication permission;
- a public-first-listen edition identifier.

The receipt must verify against the portrait source, square source, EPUB, and
the unchanged governed M4B before public sync. A receipt failure is repaired at
the source and never by rewriting the audited M4B after narration.

## Catalog Architecture

`Resources/listen/books.json` advances from schema version 1 to version 2. It
adds a top-level `series` array while retaining the existing `books` array.

```json
{
  "version": 2,
  "series": [
    {
      "id": "claude-platform",
      "title": "Claude Platform Documentation",
      "description": "A mechanism-first guide to building on the Claude Platform.",
      "plannedVolumeCount": 9,
      "volumes": [
        { "number": 1, "book": "claude-platform-01-the-message" },
        {
          "number": 2,
          "book": "claude-platform-02-thinking-and-reliable-responses"
        }
      ]
    }
  ],
  "books": []
}
```

The canonical approved curriculum currently contains nine volumes after the
addition of *The Managed Agent*. The Listening Room therefore reports
“2 of 9 planned volumes available,” correcting the earlier conversational
example that said eight.

Series identity is explicit and normalized at the catalog level. The client
derives a book’s series and volume by resolving its slug against the series’
ordered `volumes` array. It does not duplicate series title or ordering inside
each book record.

### Catalog-builder validation

The transactional builder must reject:

- a catalog version other than the supported version;
- duplicate or invalid series IDs;
- blank titles or descriptions;
- non-positive or duplicate volume numbers;
- volume numbers outside `plannedVolumeCount`;
- series volumes not sorted by number;
- a series reference to an absent or unpublished book;
- a book appearing in more than one series;
- a featured series whose first published volume is not playable;
- missing M4B, EPUB, cover, sidecar, or read-along blocks for either new book;
- absolute filesystem or `file://` paths;
- a public audio URL not pinned to the exact source commit.

The builder’s existing two-gate publication model remains: the text package
allow-list controls public visibility, and `AUDIO_EXPECTED` controls which
books must carry complete playable media. Both new slugs enter both gates.

## Listening Room Experience

### Default and deep links

With no `?book=` parameter, the player opens
`claude-platform-01-the-message`. Existing valid `?book=<slug>` links continue
to open their selected title. Invalid slugs retain the current explicit error
or fallback behavior.

### Selected-book series context

When the selected book belongs to a series, the player shows:

- `Claude Platform Documentation · Volume N` above the title;
- `2 of 9 planned volumes available`;
- links to the immediately previous and next **published** volumes when they
  exist;
- the catalog-driven public-first-listen disclosure near the byline.

No disabled navigation is shown for unpublished volumes.

### Library structure

The secondary library becomes two semantic sections:

1. **Series** — one shelf per series, with its title, description, availability
   count, and ordered published-volume cards;
2. **More books** — all standalone public titles.

The active book is not duplicated as a normal card, but its series shelf keeps
the active position visible as an `aria-current` item so the series still makes
sense. Standalone titles retain their existing Listen, EPUB, and Read actions.

### Visual and accessibility direction

The feature extends the existing dark metal-and-gold Listening Room rather than
introducing a new visual system. Square player artwork remains the main series
signal. Volume numbers carry real sequence meaning and may therefore appear as
structural labels.

- Desktop uses an ordered grid or shelf that fits the current card language.
- Mobile stacks cards naturally; it does not require a carousel or horizontal
  drag gesture.
- Keyboard focus, visible selected state, reduced motion, intrinsic cover
  dimensions, and existing light/OpenDyslexic modes remain intact.
- The status disclosure is visible text, not a tooltip or hover-only detail.
- Client rendering uses text nodes and DOM construction rather than inserting
  catalog strings through raw HTML.

## Error Handling and Transaction Boundaries

The public books merge before the site catalog is generated. The site then pins
its audio URLs to that exact merged Explainer Audiobooks commit. This prevents
the live site from referencing branch-only or nonexistent media.

The catalog builder continues to stage the complete candidate bundle in a
transaction directory. It validates catalog JSON, assets, covers, blocks,
sidecars, figures, and series relationships before atomically replacing
`Resources/listen`. Any failure leaves the previous known-good Listening Room
resources unchanged.

The browser remains tolerant of older or standalone content:

- books with no series resolve as standalone;
- an empty series array renders no series section;
- catalog fetch failure retains the current visible retry status;
- audio failure retains EPUB and readable Markdown fallbacks;
- a malformed series reference should be prevented by build-time validation,
  but the client must not crash if a hand-edited catalog reaches it.

## Verification Strategy

### Explainer Audiobooks

Add or extend tests for:

- explicit publication authorization allowing a verified first-listen package;
- pending human listening remaining visible and non-final;
- negative human evidence retaining supersession authority;
- public destination sync requiring public-safe classification and permission;
- public slug/filename normalization for Volume 1;
- privacy and absolute-path exclusion;
- exact EPUB, M4B, sidecar, and paired-cover verification;
- expected public package file sets for both volumes;
- no mutation of the private source packages.

Run the relevant skill validators, package tests, Python compilation, archive
inspection, `ffprobe`, sidecar verification, pronunciation-audit validation,
cover-receipt verification, and `git diff --check`.

### KinNoKi Labs site

Add or extend tests for:

- schema version 2 and the exact Claude Platform series object;
- nine planned volumes and two published volumes;
- unique, sorted, resolvable volume references;
- both new slugs in the public and playable allow-lists;
- exact chapter and alignment counts from the merged packages;
- default selection of Volume 1;
- `?book=` deep links for both volumes;
- series context and previous/next published-volume navigation;
- active-volume state without duplicate book cards;
- standalone titles remaining under More books;
- public-first-listen disclosure;
- no private titles or local paths;
- square cover dimensions and staged-byte parity;
- keyboard, accessible-name, focus, and reduced-motion behavior;
- responsive layouts without horizontal overflow;
- generated `Output/listen` parity.

Run `make generate`, the complete listening-room Node tests, `swift build`,
`git diff --check`, a local preview, console/error inspection, and the existing
static/generated-route checks.

### Hosted proof

After the Explainer Audiobooks merge:

- verify public folder, EPUB, Markdown, cover, M4B, and sidecar URLs;
- require HTTP `206` from byte-range requests to both M4Bs;
- confirm the site catalog pins the exact merged commit.

After the KinNoKi site merge:

- verify production `/listen/` loads;
- open both deep links;
- play, seek, change chapter, and observe read-along captions;
- check previous/next series navigation;
- confirm both M4B requests return HTTP `206`;
- verify the public-first-listen disclosure and absence of private paths;
- distinguish Cloudflare deployment success from actual production playback.

## Release Sequence

1. Update the shared audiobook publication policy and its tests.
2. Promote and verify both public book packages in a clean Explainer Audiobooks
   branch.
3. Open the Explainer Audiobooks PR, verify it, and merge it.
4. Confirm the merged public media is fetchable, including range requests.
5. Implement schema-v2 series support on a clean KinNoKiLabsSite branch based
   on the latest `origin/main`.
6. Regenerate the transactional catalog against the exact merged book commit.
7. Verify source, generated output, tests, Swift build, and local browser
   behavior.
8. Open the site PR and verify its Cloudflare preview.
9. Merge the site PR and verify production `/listen` behavior.
10. File a sanitized business-KB receipt that separates book-package merge,
    site merge, deployment, HTTP range proof, and human-listening status.

## Success Criteria

The work is complete only when:

- both books are present in the public Explainer Audiobooks repository;
- both public packages pass the governed media and public-safety checks;
- no private master or internal receipt was committed;
- the shared skill permits explicitly authorized public-first-listen editions
  and tests the honest pending-human boundary;
- `kinnokilabs.com/listen` displays the Claude Platform series as an ordered
  first-class series;
- Volume 1 is the default player selection;
- both volumes stream, seek, expose chapters, and drive read-along captions;
- public URLs and M4B byte-range requests work from production;
- existing standalone books still render and play correctly;
- the public page states that full creator listening review is underway;
- no iCloud copy was created by this release;
- the KB records only public-safe operational proof.
