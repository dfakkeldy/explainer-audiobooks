# Listening Room Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish all thirteen public learning books as narrated, read-along titles at `/listen/`, with square player covers tied to the exact public Explainer Audiobooks package commit and an unambiguous playable count.

**Architecture:** Keep the existing two-gate catalog builder and transactional cover sync, but expand both from five playable books to the full thirteen-book public allow-list. The source manifest pins portrait, square, and receipt hashes at one public package SHA; the sync tool derives all player thumbnails from canonical square covers while retaining the existing eight-title `/learn` portrait set. The player derives its narrated count from catalog data so hiding the selected title from the secondary grid cannot make the collection look one book short.

**Tech Stack:** Bash, jq, ffprobe, Echo Release `echo-cli`, Node's built-in test runner, vanilla JavaScript/DOM, Swift Package Manager, Publish, `sips`, Cloudflare Pages.

## Global Constraints

- Execute in a clean KinNoKiLabsSite feature worktree based on current `origin/main`; do not modify the user's existing checkout.
- Consume the exact pushed public package SHA produced by `2026-07-17-public-audio-recovery.md`.
- Public catalog order remains the existing thirteen-title `ALLOW_LIST` order.
- `AUDIO_EXPECTED` must equal all thirteen public slugs in that same order.
- Every playable title requires M4B, sidecar, exported blocks, chapters, a staged square cover, and 100% anchor resolution.
- Audio URLs remain immutable raw-GitHub URLs pinned to the package SHA; no M4B is copied into the site repository.
- All thirteen player covers are 768 × 768 JPEG derivatives of canonical 2400 × 2400 `m4b-cover.png` files.
- The existing eight portrait covers published under `/learn` remain the `/learn` set; the five additional player-only cover pairs do not silently change `/learn` content.
- Generated `Output/` is changed only through `make generate`; never edit it directly.
- The selected book remains absent from the secondary library grid.
- The page must state the catalog-derived playable total, “13 narrated books”.
- No absolute filesystem path may appear in catalog or generated JSON assets.
- Run Swift builds through `$HOME/.claude/bin/xcode-build-gate.sh --wait`.
- Do not create the site PR until the package commit is publicly reachable and Dan explicitly acknowledges that the site PR is ready to exist.

---

## File Map

**Modify tests first**

- `Tests/listen/catalog.test.mjs` — thirteen playable packages, exact anchor counts, all square covers.
- `Tests/listen/player-dom.test.mjs` — catalog-derived “13 narrated books” label and selected-book omission.
- `Tests/site/paired-cover-assets.test.mjs` — thirteen square player derivatives and unchanged eight portrait `/learn` assets.
- `Tests/site/paired-cover-sync.test.mjs` — schema-2 source manifest, normal and legacy-pair receipts, fail-closed transactional sync.

**Modify implementation**

- `Tools/build-listen-catalog.sh` — expand `AUDIO_EXPECTED` to all thirteen.
- `Tools/sync-paired-cover-assets.sh` — source slugs from the pinned manifest/catalog, support both receipt contracts, and derive thirteen square player covers.
- `Resources/listen/index.html` — add the narrated-count output and update sample-only metadata/copy.
- `Resources/listen/listen.js` — render the playable count from catalog data.
- `Resources/learn/paired-cover-source-manifest.json` — pin all thirteen cover pairs and the exact package commit.

**Regenerate**

- `Resources/listen/books.json`.
- `Resources/listen/books/<slug>/alignment.json`, `blocks.json`, `cover.jpg`, and any referenced figure files.
- `Resources/learn/paired-cover-provenance.json` and the existing eight portrait `/learn` cover assets.
- All corresponding `Output/` files through `make generate`.

---

### Task 1: Thirteen-Book Audio Approval Gate

**Files:**

- Modify: `Tests/listen/catalog.test.mjs`
- Modify: `Tools/build-listen-catalog.sh`

**Interfaces:**

- Consumes: a clean Explainer Audiobooks checkout at `$BOOKS_REPO`, checked out to the exact public package SHA.
- Produces: a builder whose explicit audio approval list equals all thirteen allowed books; generated data remains unchanged until Task 2 can update catalog and cover assets atomically.

- [ ] **Step 1: Add a failing builder-source contract**

Add this helper and test without changing the current published-catalog expectations:

```javascript
function audioExpectedFromBuilder(source) {
  const match = source.match(/AUDIO_EXPECTED="([\s\S]*?)"\n\nEXPECTED_BOOK_COUNT=/);
  assert.ok(match, 'AUDIO_EXPECTED is a literal reviewed gate');
  return match[1].split('\n').filter(Boolean);
}

test('builder approves every public catalog book for audio in catalog order', () => {
  assert.deepEqual(audioExpectedFromBuilder(builderSource), expectedBooks);
});
```

- [ ] **Step 2: Run the catalog test red**

```bash
node --test Tests/listen/catalog.test.mjs
```

Expected: FAIL showing that `AUDIO_EXPECTED` contains only five slugs.

- [ ] **Step 3: Expand the exact audio approval gate**

Replace `AUDIO_EXPECTED` with this exact order:

```bash
AUDIO_EXPECTED="an-unsettling-conversation
jspace-inside-the-machine
echo-from-the-inside
why-it-feels-right
you-are-the-architect
the-bug-is-a-clue
tests-first
git-happens
findable
the-voice-in-the-machine
chicken-predators
rodents-in-the-walls
the-new-deal"
```

Do not change `ALLOW_LIST`, `EXPECTED_BOOK_COUNT=13`, the rejection of media outside `AUDIO_EXPECTED`, or the transactional validation path.

- [ ] **Step 4: Re-run the static catalog contract**

```bash
node --test Tests/listen/catalog.test.mjs
```

Expected: PASS. The existing five-book catalog still matches its unchanged expectations, while the builder's future generation gate now approves thirteen.

- [ ] **Step 5: Commit only the approval gate**

```bash
git add Tools/build-listen-catalog.sh Tests/listen/catalog.test.mjs
git commit -m "feat: approve public catalog audio"
```

---

### Task 2: Thirteen Governed Square Player Covers

**Files:**

- Modify: `Resources/learn/paired-cover-source-manifest.json`
- Modify: `Tools/sync-paired-cover-assets.sh`
- Modify: `Tests/site/paired-cover-assets.test.mjs`
- Modify: `Tests/site/paired-cover-sync.test.mjs`
- Regenerate: `Resources/learn/paired-cover-provenance.json`
- Regenerate: `Resources/listen/books/*/cover.jpg`

**Interfaces:**

- Consumes: package `sourceCommit`, thirteen `m4b-cover.png` files, seven schema-2 `cover-selection.json` receipts, and six `legacy-cover-pair.json` receipts.
- Produces: thirteen 768 × 768 player derivatives plus eight unchanged `/learn` portrait assets.

- [ ] **Step 1: Write the failing catalog and asset assertions**

In `catalog.test.mjs`, set `expectedPlayable` and `squareCovers` to `expectedBooks`, rename the playable test to `catalog publishes exactly thirteen playable books with complete read-along assets`, and replace the anchor map with:

```javascript
const expectedAnchorCounts = new Map([
  ['an-unsettling-conversation', 963],
  ['jspace-inside-the-machine', 755],
  ['echo-from-the-inside', 547],
  ['why-it-feels-right', 400],
  ['you-are-the-architect', 444],
  ['the-bug-is-a-clue', 525],
  ['tests-first', 223],
  ['git-happens', 461],
  ['findable', 263],
  ['the-voice-in-the-machine', 535],
  ['chicken-predators', 231],
  ['rodents-in-the-walls', 245],
  ['the-new-deal', 151],
]);
```

Every asset directory must now contain `alignment.json`, `blocks.json`, `cover.jpg`, and optional `figures` only when referenced; remove the links-only branch expectation.

In `paired-cover-assets.test.mjs`, define:

```javascript
const playerSlugs = catalog.books.map((book) => book.slug);
const learnPortraitSlugs = [
  'an-unsettling-conversation', 'jspace-inside-the-machine',
  'echo-from-the-inside', 'why-it-feels-right', 'findable',
  'rodents-in-the-walls', 'chicken-predators', 'the-new-deal',
];
```

Assert every `playerSlugs` entry has a 768 × 768 staged JPEG, `coverSourceSha256`, `coverDerivativeSha256`, and matching provenance square hashes. Assert `Resources/learn/covers` and portrait provenance still cover exactly `learnPortraitSlugs`.

Run:

```bash
node --test Tests/listen/catalog.test.mjs Tests/site/paired-cover-assets.test.mjs
```

Expected: FAIL because generated data still contains five playable books and four governed square player derivatives.

- [ ] **Step 2: Update transactional fixture tests red**

Build the fixture from all thirteen catalog slugs. Its source manifest must be schema 2:

```javascript
{
  schemaVersion: 2,
  sourceCommit: fixtureCommit,
  books: {
    [slug]: {
      publishPortraitToLearn: learnPortraitSlugs.includes(slug),
      receiptPath: legacyPairSlugs.includes(slug)
        ? 'legacy-cover-pair.json'
        : 'cover-selection.json',
      receiptSha256,
      candidateId,
      portrait: { sha256, specSha256 },
      square: { sha256, specSha256 }
    }
  }
}
```

Keep negative tests for substituted receipt, wrong slug, locally edited source, wrong dimensions, refused publication, candidate mismatch, and rollback after forced rename failure. Run:

```bash
node --test Tests/site/paired-cover-assets.test.mjs Tests/site/paired-cover-sync.test.mjs
```

Expected: FAIL because the current sync script hard-codes eight portraits, four square players, and a special portrait-only Rodents branch.

- [ ] **Step 3: Write the exact source manifest**

Update `paired-cover-source-manifest.json` to schema 2 with all thirteen books. Set `sourceCommit` to the exact public package SHA. For each book, compute and record:

- `publishPortraitToLearn` (`true` only for the existing eight-title set);
- repository-relative `receiptPath`;
- receipt SHA-256 and candidate/direction ID;
- portrait cover/spec SHA-256;
- square cover/spec SHA-256.

The manifest must contain no absolute paths and its book keys must match catalog order when read from `Resources/listen/books.json`.

- [ ] **Step 4: Remove hard-coded player subsets from the sync tool**

Implement these data sources:

```bash
SOURCE_SLUGS="$(jq -r '.books | keys[]' "$SOURCE_MANIFEST_PATH" | LC_ALL=C sort)"
PLAYER_SLUGS="$(jq -r '.books[] | select(.audio.status == "available") | .slug' "$CATALOG_PATH")"
LEARN_SLUGS="$(jq -r '.books | to_entries[] | select(.value.publishPortraitToLearn == true) | .key' "$SOURCE_MANIFEST_PATH")"
```

Require `SOURCE_SLUGS` and sorted `PLAYER_SLUGS` to contain the same thirteen slugs. Require `LEARN_SLUGS` to contain the exact existing eight. Resolve each receipt from the manifest's `receiptPath`, require it to be tracked and clean, and verify its hash before interpreting it.

For `cover-selection.json`, retain schema-2 candidate/privacy/variant checks. For `legacy-cover-pair.json`, require schema 1, matching `book_slug`, `selection_source == "user-approved-derivation"`, public-safe publication permission, matching direction name/candidate, and exact portrait/square hashes from the manifest. Delete the Rodents-only exception.

For every `PLAYER_SLUGS` entry, derive `cover.jpg` from `m4b-cover.png` with:

```bash
sips -s format jpeg -s formatOptions 86 -z 768 768 "$square" \
  --out "$work/player/$slug.jpg" >/dev/null
```

Only `LEARN_SLUGS` entries are copied into `Resources/learn/covers`.

- [ ] **Step 5: Run the sync transaction**

```bash
ECHO_CLI=/Users/dfakkeldy/Developer/Echo/.build/cli/Build/Products/Release/echo-cli
test -n "${BOOKS_REPO:?set BOOKS_REPO to the clean package worktree at the approved public SHA}"
PACKAGE_SHA="$(git -C "$BOOKS_REPO" rev-parse HEAD)"
test "$PACKAGE_SHA" = "$(jq -r '.sourceCommit' Resources/learn/paired-cover-source-manifest.json)"
BOOKS_REPO="$BOOKS_REPO" ECHO_CLI="$ECHO_CLI" Tools/build-listen-catalog.sh
BOOKS_REPO="$BOOKS_REPO" Tools/sync-paired-cover-assets.sh
```

Expected: thirteen complete read-along packages, then the final line `Verified and installed eight portrait covers and thirteen square player derivatives from $PACKAGE_SHA.`

- [ ] **Step 6: Run cover tests green**

```bash
node --test Tests/site/paired-cover-assets.test.mjs Tests/site/paired-cover-sync.test.mjs
node --test Tests/listen/catalog.test.mjs
```

Expected: PASS; all thirteen catalog cover dimensions are 768 × 768.

- [ ] **Step 7: Commit cover governance**

Stage the builder-generated thirteen-book catalog/assets, manifest, sync tool, tests, provenance JSON, thirteen player JPEGs, books.json hash/dimension updates, and only the existing eight `/learn` portrait assets. Commit:

```bash
git commit -m "feat: publish thirteen governed narrated books"
```

---

### Task 3: Catalog-Derived Narrated Count

**Files:**

- Modify: `Resources/listen/index.html`
- Modify: `Resources/listen/listen.js`
- Modify: `Tests/listen/player-dom.test.mjs`

**Interfaces:**

- Produces: `renderPlayableCount(catalog: Catalog) -> void` in browser JavaScript.
- DOM contract: element ID `playableCount` contains `13 narrated books` for the published catalog.

- [ ] **Step 1: Write the failing DOM test**

Add `playableCount` to `bootPlayer()`'s fake ID list. After startup, assert:

```javascript
assert.equal(elements.get('playableCount').textContent, '13 narrated books');
assert.equal(
  descendants(elements.get('library'), (node) => node.tagName === 'LI').length,
  12,
  'selected book remains omitted from the secondary grid',
);
```

Add a cloned-catalog test with two available books and one links-only book; expect `2 narrated books`. This prevents a hard-coded marketing count.

- [ ] **Step 2: Run the DOM test red**

```bash
node --test Tests/listen/player-dom.test.mjs
```

Expected: FAIL because `playableCount` is absent and never rendered.

- [ ] **Step 3: Add accessible count markup and current metadata**

Change the page description from “a sample learning audiobook” to “free learning audiobooks”. Under the library heading add:

```html
<p class="room-library-count"><strong id="playableCount">Loading narrated books…</strong></p>
```

Keep the existing explanatory subtitle immediately after it.

- [ ] **Step 4: Render the count from catalog data**

Add `playableCount: $('playableCount')` to `els`, then add:

```javascript
function renderPlayableCount(catalog) {
  var count = catalog.books.filter(function (candidate) {
    return candidate.audio.status === 'available';
  }).length;
  els.playableCount.textContent = count + ' narrated ' + (count === 1 ? 'book' : 'books');
}
```

Call `renderPlayableCount(catalog)` before selecting the active book, so the count also renders in the empty-player path.

- [ ] **Step 5: Run DOM, accessibility, and contrast tests**

```bash
node --test Tests/listen/player-dom.test.mjs Tests/listen/contrast.test.mjs
```

Expected: PASS.

- [ ] **Step 6: Commit the count behavior**

```bash
git add Resources/listen/index.html Resources/listen/listen.js Tests/listen/player-dom.test.mjs
git commit -m "feat: show the narrated library total"
```

---

### Task 4: Regeneration and Complete Local Verification

**Files:**

- Regenerate: committed `Resources/` data touched by the catalog/cover tools.
- Regenerate: all corresponding `Output/` files.

**Interfaces:**

- Consumes: the exact public package SHA.
- Produces: a clean, locally verified site HEAD ready for Dan's PR-existence acknowledgement.

- [ ] **Step 1: Re-run both source-data generators from clean inputs**

```bash
BOOKS_REPO="$BOOKS_REPO" ECHO_CLI="$ECHO_CLI" Tools/build-listen-catalog.sh
BOOKS_REPO="$BOOKS_REPO" Tools/sync-paired-cover-assets.sh
```

Run `git diff --exit-code` over generated source data after a second identical pass; expected: no changes from the second pass except the catalog's documented generation timestamp if the builder intentionally refreshes it. If the timestamp changes, compare all non-timestamp JSON and binary hashes.

- [ ] **Step 2: Run the full Node suite**

```bash
node --test Tests/listen/*.test.mjs Tests/site/*.test.mjs
```

Expected: PASS, including transactional rollback, absolute-path guards, accessibility, contrast, core player, catalog, and paired-cover tests.

- [ ] **Step 3: Regenerate the site**

```bash
make generate
```

Expected: success and updated committed `Output/listen/` plus paired-cover provenance/output assets. Never patch `Output/` manually.

- [ ] **Step 4: Build through the machine gate**

```bash
"$HOME/.claude/bin/xcode-build-gate.sh" --wait && swift build
```

Expected: `Build complete!` with a zero exit status.

- [ ] **Step 5: Verify generated parity and local HTTP behavior**

Serve `Output/` over localhost. For every catalog audio URL, run a byte-range request and require HTTP `206` plus non-empty bytes:

```bash
curl --fail --silent --show-error --range 0-1023 --output /dev/null \
  --write-out '%{http_code}\n' "$audio_url"
```

Open `/listen/` in the browser and verify:

- the visible count says “13 narrated books”;
- the grid shows twelve because the selected book is intentionally omitted;
- selecting each of the thirteen books updates title, square cover, chapters, URL, and read-along data;
- play initiates for each title;
- one chapter seek and one caption progression work for each title;
- the EPUB and Markdown links remain present.

- [ ] **Step 6: Commit generated output**

Stage only expected `Resources/`, `Output/`, and test changes. Commit:

```bash
git commit -m "build: regenerate thirteen-book listening room"
```

- [ ] **Step 7: Run the final clean gate**

```bash
node --test Tests/listen/*.test.mjs Tests/site/*.test.mjs
"$HOME/.claude/bin/xcode-build-gate.sh" --wait && swift build
git diff --check
git status --short --branch
git log --oneline --decorate origin/main..HEAD
```

Expected: all tests/builds PASS and the worktree is clean.

- [ ] **Step 8: Stop at the site PR gate**

Present the exact package SHA, exact site HEAD, thirteen `206` results, local browser results, and full test/build status. Request Dan's explicit acknowledgement that the site PR is ready to exist. Do not push, create the PR, or trigger public deployment before that acknowledgement.

---

## Post-Authorization Publication Checks

After explicit acknowledgement only: push the feature branch, open a ready PR against `main`, inspect hosted CI, and stop for merge authorization. After merge, verify Cloudflare Pages and `https://kinnokilabs.com/listen/` independently: 13 catalog entries, 13 available audio records, square cover dimensions, range-capable audio URLs, visible narrated count, and opening playback for every title.
