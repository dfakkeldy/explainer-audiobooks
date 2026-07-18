# Claude Platform Public Series Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task.

**Goal:** Publish the first two Claude Platform documentation audiobooks as a verified public-first-listen series and make that series first-class at `https://kinnokilabs.com/listen`.

**Architecture:** The Explainer Audiobooks repository remains the immutable source of public book packages. Each package carries a sanitized, machine-readable publication receipt and exact copies of its accepted EPUB, M4B, alignment, and cover artifacts. After those packages merge, the KinNoKi Labs site’s transactional catalog builder consumes the merged commit, validates a normalized series definition, and generates catalog version 2 plus the existing read-along assets. The browser resolves series membership from the catalog, not from slugs or titles.

**Tech Stack:** Python 3 `unittest`; Bash; `jq`; `ffprobe`; `unzip`; Echo `echo-cli`; Node.js built-in test runner; vanilla JavaScript; HTML/CSS; SwiftPM Publish; GitHub CLI; Cloudflare Pages.

**Global Constraints:** Keep both private master folders byte-for-byte untouched. Do not copy anything to iCloud. Preserve accepted M4B and alignment bytes unless verification fails. Never commit internal narration receipts, pronunciation reels/audits, research scratch, listener notes, absolute local paths, or private-only source maps. Use `am_michael` metadata already embedded in the accepted M4Bs. Publish status as `public-first-listen` with `humanListeningStatus: pending` and the exact approved disclosure. Use nine planned volumes. Keep `?book=<slug>` deep links. No future-volume placeholders. Use PRs to `main` because neither repository has the promotion ladder. Merge the book PR before generating the site catalog. Do not edit generated `Output/` by hand.

## Fixed Paths and Identities

```text
Private Volume 1 master:
/Users/dfakkeldy/Documents/Codex/custom-learning-audiobooks/claude-platform-01-the-message-road-book-v2

Private Volume 2 master:
/Users/dfakkeldy/Documents/Codex/custom-learning-audiobooks/claude-platform-02-thinking-and-reliable-responses

Explainer implementation worktree:
/Users/dfakkeldy/.codex/worktrees/claude-platform-public-series

Site implementation worktree:
/Users/dfakkeldy/.codex/worktrees/kinnoki-claude-platform-series

Public Volume 1 slug:
claude-platform-01-the-message

Public Volume 2 slug:
claude-platform-02-thinking-and-reliable-responses

Series ID:
claude-platform
```

The accepted source facts to preserve are:

| Volume | Chapters | Duration | Alignment anchors | Embedded title | Embedded artist |
|---|---:|---:|---:|---|---|
| 1 | 12 | 7409.450667 s | 571 | The Message | Dan Fakkeldy |
| 2 | 13 | 5316.266667 s | 346 | Making Claude Think and Respond Reliably | Dan Fakkeldy |

## Files in Scope

### Explainer Audiobooks

- Modify: `skill/references/unattended-production.md`
- Modify: `skills/custom-learning-audiobook/SKILL.md`
- Modify: `skills/custom-learning-audiobook/references/package-and-qc.md`
- Modify: `tests/test_skill_unattended_contract.py`
- Create: `skill/scripts/verify_public_first_listen.py`
- Create: `tests/test_verify_public_first_listen.py`
- Create: `tests/test_claude_platform_public_series.py`
- Create: `books/claude-platform-01-the-message/*`
- Create: `books/claude-platform-02-thinking-and-reliable-responses/*`
- Modify: `README.md`

### KinNoKi Labs Site

- Create: `Tools/listen-series.json`
- Modify: `Tools/build-listen-catalog.sh`
- Modify: `Resources/listen/books.json`
- Modify: `Resources/listen/listen-core.js`
- Modify: `Resources/listen/listen.js`
- Modify: `Resources/listen/index.html`
- Modify: `Resources/listen/listen.css`
- Modify: `Tests/listen/catalog.test.mjs`
- Modify: `Tests/listen/catalog-transaction.test.mjs`
- Modify: `Tests/listen/listen-core.test.mjs`
- Modify: `Tests/listen/player-dom.test.mjs`
- Modify only through generation: `Output/listen/*`

### Business Knowledge Base

- Modify: `/Users/dfakkeldy/Developer/knowledge-base/projects/explainer-audiobooks.md`
- Create: `/Users/dfakkeldy/Developer/knowledge-base/status/2026-07-18-claude-platform-public-series.md`
- Update the relevant KB index/log required by its local instructions.

## Task 1: Create Clean Implementation Worktrees

**Files:** None yet.

1. Fetch both repositories and confirm their live base branches:

```bash
git -C /Users/dfakkeldy/Developer/explainer-audiobooks fetch origin
git -C /Users/dfakkeldy/Developer/KinNoKiLabsSite fetch origin
git -C /Users/dfakkeldy/Developer/explainer-audiobooks branch -r --list 'origin/nightly' 'origin/weekly'
git -C /Users/dfakkeldy/Developer/KinNoKiLabsSite branch -r --list 'origin/nightly' 'origin/weekly'
```

Expected: neither repository reports `nightly` or `weekly`; both changes target `main`.

2. Create clean named worktrees from the latest `origin/main`:

```bash
git -C /Users/dfakkeldy/Developer/explainer-audiobooks worktree add \
  -b codex/claude-platform-public-series \
  /Users/dfakkeldy/.codex/worktrees/claude-platform-public-series origin/main

git -C /Users/dfakkeldy/Developer/KinNoKiLabsSite worktree add \
  -b codex/kinnoki-claude-platform-series \
  /Users/dfakkeldy/.codex/worktrees/kinnoki-claude-platform-series origin/main
```

3. Copy the approved design and this plan onto the Explainer implementation branch by cherry-picking the design commit and the planning branch tip, then confirm both worktrees are clean:

```bash
git -C /Users/dfakkeldy/.codex/worktrees/claude-platform-public-series cherry-pick \
  c69406e codex/claude-platform-public-series-design
git -C /Users/dfakkeldy/.codex/worktrees/claude-platform-public-series status --short --branch
git -C /Users/dfakkeldy/.codex/worktrees/kinnoki-claude-platform-series status --short --branch
```

Expected: both branches have no uncommitted files before implementation begins.

4. Use the bundled Python runtime that includes Pillow, rather than the bare system Python that cannot import the cover tooling:

```bash
export PYTHON='/Users/dfakkeldy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3'
"$PYTHON" -c 'from PIL import Image; print("PIL_OK")'
```

Expected: `PIL_OK`.

## Task 2: Encode the Permanent Public-First-Listen Policy

**Files:**

- Modify: `skill/references/unattended-production.md`
- Modify: `skills/custom-learning-audiobook/SKILL.md`
- Modify: `skills/custom-learning-audiobook/references/package-and-qc.md`
- Modify: `tests/test_skill_unattended_contract.py`

1. Add a failing policy test next to the existing “never auto-publish” test:

```python
def test_explicit_authorization_can_promote_a_verified_first_listen(self) -> None:
    contract = self.read("skill/references/unattended-production.md")
    for marker in (
        "public-first-listen",
        "explicit publication authorization",
        "humanlisteningstatus: pending",
        "full listening review is still underway",
        "negative human verdict supersedes",
        "never auto-publish",
    ):
        with self.subTest(marker=marker):
            self.assertIn(marker, contract)
```

2. Run the focused test and verify RED:

```bash
"$PYTHON" -m unittest tests.test_skill_unattended_contract -v
```

Expected: the new test fails because `public-first-listen` is not yet in the contract.

3. Add a `Public first listen` subsection to the shared contract. It must say:

```text
Unattended production never auto-publishes. After the package exists, explicit
publication authorization may promote a verified public-safe package to
public-first-listen while humanListeningStatus: pending. The public package and
catalog must say: “This edition has passed package and audio checks. The
creator’s full listening review is still underway.” A negative human verdict
supersedes the public-first-listen edition.
```

4. Route the custom-learning skill and package checklist to the same state. Preserve the current `continue`/`revise` listener contract, and explicitly distinguish:

```text
unattended-first-listen -> private package, never automatically published
public-first-listen     -> explicitly authorized, public-safe, mechanically verified, human listen pending
governed-final          -> existing higher-confidence state with completed required human gates
```

5. Run the focused and related contract tests:

```bash
"$PYTHON" -m unittest \
  tests.test_skill_unattended_contract \
  tests.test_skill_cover_contract \
  tests.test_sync_selected_cover -v
```

Expected: all tests pass; the old `never auto-publish` markers remain intact.

6. Commit:

```bash
git add skill/references/unattended-production.md \
  skills/custom-learning-audiobook/SKILL.md \
  skills/custom-learning-audiobook/references/package-and-qc.md \
  tests/test_skill_unattended_contract.py
git commit -m "feat: define public first-listen publication"
```

## Task 3: Add a Machine-Verifiable Public Publication Receipt

**Files:**

- Create: `skill/scripts/verify_public_first_listen.py`
- Create: `tests/test_verify_public_first_listen.py`

1. Write tests first for a generic public package receipt. Build its artifact rows from real fixture bytes so every hash is meaningful:

```python
def artifact(root: Path, name: str, payload: bytes) -> dict[str, str]:
    path = root / name
    path.write_bytes(payload)
    return {"file": name, "sha256": hashlib.sha256(payload).hexdigest()}

receipt = {
    "schemaVersion": 1,
    "slug": "fixture-book",
    "editionId": "public-first-listen-2026-07-18",
    "publicationStatus": "public-first-listen",
    "humanListeningStatus": "pending",
    "classification": "public-safe",
    "permissionToPublish": True,
    "permissionGrantedAt": "2026-07-18",
    "disclosure": DISCLOSURE,
    "sourceArtIncluded": True,
    "artifacts": {
        "manuscript": artifact(root, "fixture-book.md", b"# Fixture\n"),
        "epub": artifact(root, "fixture-book.epub", b"epub-fixture"),
        "m4b": artifact(root, "fixture-book.m4b", b"m4b-fixture"),
        "alignment": artifact(
            root,
            "fixture-book.alignment.json",
            b'[{"blockId":"b1","timestamp":0}]\n',
        ),
        "portraitCover": artifact(root, "cover.png", b"portrait"),
        "squareCover": artifact(root, "m4b-cover.png", b"square"),
    },
}
```

Patch the external `unzip` and `ffprobe` probes in unit fixtures; real package acceptance tests exercise the actual commands.

Cover these failures:

- wrong publication or listening status;
- private classification or missing permission;
- wrong disclosure text;
- slug/filename mismatch;
- missing file or SHA mismatch;
- absolute path or `file://` value anywhere in JSON;
- a README that omits the disclosure;
- forbidden internal file patterns such as `echo-render-*`, `*pronunciation-audit*`, `*pronunciation-reel*`, `*resume-state*`, or `research/`;
- `sourceArtIncluded: true` without the source-art basename named by `cover-render.json`;
- `sourceArtIncluded: false` while a stale or fabricated source-art file is present.

The last pair handles the verified live discrepancy in Volume 1: its render receipt records source-art SHA `9c05f120931365179dee4f108371ee40f574b61268614f0fe4bd729f9a6b2d7c`, but the original source raster is not present in the private delivery folder or recovered source roots. The verifier must preserve that truth rather than fabricate replacement provenance. Volume 2 does include the selected Candidate 3 raster and therefore sets `sourceArtIncluded: true`.

2. Run the new tests and verify RED:

```bash
"$PYTHON" -m unittest tests.test_verify_public_first_listen -v
```

Expected: import failure because the verifier does not exist.

3. Implement this exact CLI contract:

```text
"$PYTHON" skill/scripts/verify_public_first_listen.py BOOK_DIRECTORY
```

The module should define the exact `DISCLOSURE` constant above and expose testable `load_receipt(book_dir: Path)`, `reject_private_values(value: object, location: str = "publication.json")`, `verify_artifacts(book_dir: Path, receipt: dict[str, object])`, and `verify_public_package(book_dir: Path)` functions.

Hash files by streaming chunks, require the six canonical artifacts, call `unzip -t` for the EPUB, call `ffprobe` for M4B duration and chapters, parse alignment as a nonempty JSON array, and exit nonzero with a specific diagnostic on failure. Do not modify the package.

4. Run the tests and verify GREEN:

```bash
"$PYTHON" -m unittest tests.test_verify_public_first_listen -v
```

5. Commit:

```bash
git add skill/scripts/verify_public_first_listen.py tests/test_verify_public_first_listen.py
git commit -m "feat: verify public first-listen packages"
```

## Task 4: Build and Verify the Public Volume 1 Package

**Files:**

- Create: `books/claude-platform-01-the-message/README.md`
- Create: `books/claude-platform-01-the-message/publication.json`
- Create: `books/claude-platform-01-the-message/claude-platform-01-the-message.md`
- Create: `books/claude-platform-01-the-message/claude-platform-01-the-message.epub`
- Create: `books/claude-platform-01-the-message/claude-platform-01-the-message.m4b`
- Create: `books/claude-platform-01-the-message/claude-platform-01-the-message.alignment.json`
- Create: the nine governed paired-cover artifacts (`cover.png`, `m4b-cover.png`, both specs, both render receipts, both thumbnails, and `cover-selection.json`)

1. Establish immutable inputs and a clean staging directory outside Git:

```bash
V1_PRIVATE='/Users/dfakkeldy/Documents/Codex/custom-learning-audiobooks/claude-platform-01-the-message-road-book-v2'
V1_PRIVATE_SLUG='claude-platform-01-the-message-road-book-v2'
V1_PUBLIC_SLUG='claude-platform-01-the-message'
V1_STAGE='/Users/dfakkeldy/Documents/Codex/publication-staging/claude-platform-01-the-message'
V1_INPUTS="$V1_STAGE/inputs"
V1_PAIR="$V1_STAGE/paired"
V1_DEST='/Users/dfakkeldy/.codex/worktrees/claude-platform-public-series/books/claude-platform-01-the-message'

rm -rf "$V1_STAGE"
mkdir -p "$V1_INPUTS" "$V1_PAIR"
test ! -e "$V1_DEST"
```

The staging directory is generated scratch outside Git. Removing it is allowed; never remove or mutate `$V1_PRIVATE`.

2. Verify the private master before copying:

```bash
unzip -t "$V1_PRIVATE/$V1_PRIVATE_SLUG.epub"
ffprobe -v error -show_entries format=duration:chapter=start_time,end_time \
  -of json "$V1_PRIVATE/$V1_PRIVATE_SLUG.m4b" | \
  jq -e '(.chapters | length) == 12 and ((.format.duration | tonumber) > 7409 and (.format.duration | tonumber) < 7410)'
jq -e 'type == "array" and length == 571' "$V1_PRIVATE/$V1_PRIVATE_SLUG.alignment.json"
```

Derive the approved Echo CLI and `ECHO_RESOURCE_DIR` from the immutable `echo-render-inputs-*.env` receipt, then run:

```bash
echo-cli verify-sidecar \
  "$V1_PRIVATE/$V1_PRIVATE_SLUG.m4b" \
  "$V1_PRIVATE/$V1_PRIVATE_SLUG.alignment.json"
"$PYTHON" skill/scripts/validate_pronunciation_audit.py \
  "$V1_PRIVATE/$V1_PRIVATE_SLUG.pronunciation-audit.json"
```

Expected: `SIDECAR_OK`; pronunciation validation passes.

3. Copy the four accepted reader artifacts to the private staging input directory under the clean public slug. Use `cp -p` only into staging, then prove byte identity:

```bash
for ext in md epub m4b alignment.json; do
  cp -p "$V1_PRIVATE/$V1_PRIVATE_SLUG.$ext" "$V1_INPUTS/$V1_PUBLIC_SLUG.$ext"
  test "$(shasum -a 256 "$V1_PRIVATE/$V1_PRIVATE_SLUG.$ext" | awk '{print $1}')" = \
       "$(shasum -a 256 "$V1_INPUTS/$V1_PUBLIC_SLUG.$ext" | awk '{print $1}')"
done
```

4. Generate a fresh schema-v2 public cover selection receipt from the accepted portrait and square render receipts, with:

```text
book_slug: claude-platform-01-the-message
edition_id: public-first-listen-2026-07-18
selection_source: user
privacy.classification: public-safe
privacy.permission_to_publish: true
```

Run the exact governed cover commands:

```bash
for name in cover.png m4b-cover.png cover-thumbnail.png m4b-cover-thumbnail.png \
  cover-spec.json m4b-cover-spec.json cover-render.json m4b-cover-render.json; do
  install -m 0644 "$V1_PRIVATE/$name" "$V1_PAIR/$name"
done
SELECTED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

"$PYTHON" skill/scripts/cover_receipts.py select-pair \
  --portrait-render-receipt "$V1_PRIVATE/cover-render.json" \
  --square-render-receipt "$V1_PRIVATE/m4b-cover-render.json" \
  --out "$V1_PAIR/cover-selection.json" \
  --book-slug "$V1_PUBLIC_SLUG" \
  --edition-id public-first-listen-2026-07-18 \
  --selection-source user \
  --selected-at "$SELECTED_AT" \
  --privacy-classification public-safe \
  --permission-to-publish

"$PYTHON" skill/scripts/cover_receipts.py verify \
  --selection "$V1_PAIR/cover-selection.json" \
  --cover "$V1_PRIVATE/cover.png" \
  --m4b-cover "$V1_PRIVATE/m4b-cover.png" \
  --epub "$V1_INPUTS/$V1_PUBLIC_SLUG.epub" \
  --m4b "$V1_INPUTS/$V1_PUBLIC_SLUG.m4b"

"$PYTHON" skill/scripts/sync_selected_cover.py \
  --selection "$V1_PAIR/cover-selection.json" \
  --cover "$V1_PAIR/cover.png" \
  --epub "$V1_INPUTS/$V1_PUBLIC_SLUG.epub" \
  --m4b "$V1_INPUTS/$V1_PUBLIC_SLUG.m4b" \
  --paired-artifact-dir "$V1_PAIR" \
  --destination "$V1_DEST" \
  --intent reuse \
  --public-destination \
  --apply

install -m 0644 "$V1_INPUTS/$V1_PUBLIC_SLUG.md" "$V1_DEST/$V1_PUBLIC_SLUG.md"
install -m 0644 "$V1_INPUTS/$V1_PUBLIC_SLUG.alignment.json" \
  "$V1_DEST/$V1_PUBLIC_SLUG.alignment.json"
```

Do not copy the private selection receipt. The governed sync destination is deliberately absent before the command so it is classified as a new public package, not an unreceipted overwrite.

5. Because the original Volume 1 source raster is absent, set `sourceArtIncluded: false`. Keep the truthful governed render/spec receipts, including their recorded source-art SHA, but do not fabricate `cover-source.png`.

6. Create `README.md` with:

- title, subtitle, author/contributor disclosure;
- Claude Platform documentation source date;
- `am_michael`, 12 chapters, 7409.450667 seconds;
- explicit public-safe classification and permission date;
- `public-first-listen` and human listening pending;
- the exact approved disclosure;
- lightweight listener contract: reply `continue` or `revise`;
- artifact hashes and verification summary;
- note that original cover source raster is not included, while selected covers and governed receipts are preserved;
- CC BY 4.0 link.

7. Generate `publication.json` with the exact hashes from `$V1_DEST`. Write the README and publication receipt with `apply_patch`; never generate them with shell redirection. Do not use a recursive raw package copy.

8. Verify:

```bash
"$PYTHON" skill/scripts/verify_public_first_listen.py "$V1_DEST"
find "$V1_DEST" -type f -print0 | xargs -0 rg -n \
  '/Users/|file://|Documents/Codex|echo-render-inputs|resume-state|pronunciation-reel|pronunciation-audit' || true
```

Expected: verifier succeeds; privacy scan prints no matches except the README’s intentional statement that private receipts are excluded, which should avoid literal local path names.

9. Commit Volume 1:

```bash
git add books/claude-platform-01-the-message
git commit -m "feat: publish The Message first-listen edition"
```

## Task 5: Build and Verify the Public Volume 2 Package

**Files:**

- Create: `books/claude-platform-02-thinking-and-reliable-responses/README.md`
- Create: `books/claude-platform-02-thinking-and-reliable-responses/publication.json`
- Create: the canonical MD, EPUB, M4B, alignment, paired-cover, and safe source files.

1. Repeat the Task 4 workflow with:

```bash
V2_PRIVATE='/Users/dfakkeldy/Documents/Codex/custom-learning-audiobooks/claude-platform-02-thinking-and-reliable-responses'
V2_SLUG='claude-platform-02-thinking-and-reliable-responses'
V2_STAGE='/Users/dfakkeldy/Documents/Codex/publication-staging/claude-platform-02-thinking-and-reliable-responses'
V2_DEST='/Users/dfakkeldy/.codex/worktrees/claude-platform-public-series/books/claude-platform-02-thinking-and-reliable-responses'
```

2. The source assertions are:

```bash
unzip -t "$V2_PRIVATE/$V2_SLUG.epub"
ffprobe -v error -show_entries format=duration:chapter=start_time,end_time \
  -of json "$V2_PRIVATE/$V2_SLUG.m4b" | \
  jq -e '(.chapters | length) == 13 and ((.format.duration | tonumber) > 5316 and (.format.duration | tonumber) < 5317)'
jq -e 'type == "array" and length == 346' "$V2_PRIVATE/$V2_SLUG.alignment.json"
```

3. Use Candidate 3, `Event by Event`, as the public cover source. Generate a fresh public selection receipt with the same status and permission fields as Volume 1. Copy `candidate-3/source-art.png` to `cover-source.png`, and set `sourceArtIncluded: true`. If the governed render receipt names `source-art.png`, retain that basename instead and keep the receipt internally consistent; do not rewrite receipt paths merely for cosmetic naming.

4. Copy `sources.md` only after a scan proves it contains no absolute paths, private notes, or unpublished research. If it fails, omit it; the readable manuscript/EPUB source appendix remains sufficient. Do not copy `reader-reference.md`, `receipts/`, the pronunciation artifacts, or the candidate directories.

5. Create the public README and `publication.json` with 13 chapters, 5316.266667 seconds, `am_michael`, public-first-listen status, the exact disclosure, `continue`/`revise`, source date, AI contribution disclosure, hashes, and CC BY 4.0.

6. Verify and commit:

```bash
"$PYTHON" skill/scripts/verify_public_first_listen.py "$V2_DEST"
git add books/claude-platform-02-thinking-and-reliable-responses
git commit -m "feat: publish reliable responses first-listen edition"
```

## Task 6: Add Repository-Level Acceptance Tests and Library Entries

**Files:**

- Create: `tests/test_claude_platform_public_series.py`
- Modify: `README.md`

1. Write an acceptance test that opens both real public packages and asserts:

```python
CASES = {
    "claude-platform-01-the-message": {
        "chapters": 12,
        "anchors": 571,
        "duration": (7409, 7410),
        "title": "The Message",
    },
    "claude-platform-02-thinking-and-reliable-responses": {
        "chapters": 13,
        "anchors": 346,
        "duration": (5316, 5317),
        "title": "Making Claude Think and Respond Reliably",
    },
}
```

For each package, invoke `verify_public_package`, confirm M4B and alignment SHA parity against the named private master without writing to it, confirm embedded artist `Dan Fakkeldy`, and confirm the public directory contains no forbidden files. The test may read the private masters only when they exist; CI must still validate the public package independently and skip only the private parity assertion.

2. Run the test before editing `README.md`:

```bash
"$PYTHON" -m unittest tests.test_claude_platform_public_series -v
```

Expected: package tests pass.

3. Add the two books contiguously at the top of the public book table, with `Claude Platform Documentation, Volume 1` and `Volume 2` in their descriptions and the established contributor attribution.

4. Run the full Explainer test suite and scans:

```bash
"$PYTHON" -m unittest discover -s tests -v
git diff --check
rg -n '/Users/|file://' books/claude-platform-01-the-message books/claude-platform-02-thinking-and-reliable-responses
git status --short --branch
```

Expected: all tests pass, `git diff --check` is clean, path scan has no hits, and only intended files are changed.

5. Commit:

```bash
git add README.md tests/test_claude_platform_public_series.py
git commit -m "test: lock Claude Platform public packages"
```

## Task 7: Publish and Prove the Explainer Packages

**Files:** No new source files.

1. Rebase onto the latest `origin/main`, rerun the full suite, and push:

```bash
git fetch origin
git rebase origin/main
"$PYTHON" -m unittest discover -s tests -v
git push -u origin codex/claude-platform-public-series
```

2. Open a ready PR to `main`. The body must state:

- explicit publication authorization is recorded;
- both editions are `public-first-listen`, not human-final;
- private masters were not changed;
- no iCloud copy was made;
- exact package tests and media verification performed;
- site publication is intentionally waiting for the merged SHA.

```bash
gh pr create --base main --head codex/claude-platform-public-series \
  --title "Publish Claude Platform audiobook series" \
  --body-file /tmp/claude-platform-explainer-pr.md
```

3. Watch required checks. If green, merge because the user explicitly authorized publication:

```bash
gh pr checks --watch
gh pr merge --squash --delete-branch
git fetch origin
BOOKS_SHA="$(git rev-parse origin/main)"
```

4. Verify each public media object supports range requests at the merged SHA:

```bash
for slug in claude-platform-01-the-message claude-platform-02-thinking-and-reliable-responses; do
  curl -fsSI -H 'Range: bytes=0-1023' \
    "https://raw.githubusercontent.com/dfakkeldy/explainer-audiobooks/$BOOKS_SHA/books/$slug/$slug.m4b" | \
    rg -i '^HTTP/|^content-range:|^content-length:'
done
```

Expected: final response is HTTP `206 Partial Content` for each M4B and includes a valid `Content-Range`.

Do not begin the site catalog generation until this succeeds.

## Task 8: Define and Validate Catalog Version 2 Series Data

**Files:**

- Create: `Tools/listen-series.json`
- Modify: `Tools/build-listen-catalog.sh`
- Modify: `Tests/listen/catalog.test.mjs`
- Modify: `Tests/listen/catalog-transaction.test.mjs`

1. Create the curated builder input:

```json
{
  "series": [
    {
      "id": "claude-platform",
      "title": "Claude Platform Documentation",
      "description": "A mechanism-first guide to building on the Claude Platform.",
      "plannedVolumeCount": 9,
      "featured": true,
      "volumes": [
        {"number": 1, "book": "claude-platform-01-the-message"},
        {"number": 2, "book": "claude-platform-02-thinking-and-reliable-responses"}
      ]
    }
  ]
}
```

2. Add failing catalog tests for:

```javascript
assert.equal(catalog.version, 2);
assert.deepEqual(catalog.series, seriesSource.series);
assert.equal(catalog.series.filter((series) => series.featured).length, 1);
assert.equal(catalog.series[0].plannedVolumeCount, 9);
assert.deepEqual(
  catalog.series[0].volumes.map((volume) => volume.book),
  ['claude-platform-01-the-message', 'claude-platform-02-thinking-and-reliable-responses'],
);
```

Update `expectedBooks`, `expectedPlayable`, `expectedAnchorCounts`, and `squareCovers` with both slugs and counts 571/346. Add both books’ `edition` assertions:

```javascript
assert.deepEqual(book.edition, {
  status: 'public-first-listen',
  humanListeningStatus: 'pending',
  disclosure: FIRST_LISTEN_DISCLOSURE,
});
```

3. Run tests and verify RED:

```bash
make test-listen
```

4. Update the builder allow-list and audio gate:

```text
claude-platform-01-the-message|The Message|Conversations, Content Blocks, and the Messages API|Codex (GPT-5)
claude-platform-02-thinking-and-reliable-responses|Making Claude Think and Respond Reliably|Reasoning, Multimodal Inputs, Structured Output, and Streaming|Codex (GPT-5)
```

Add both slugs to `AUDIO_EXPECTED`; change `EXPECTED_BOOK_COUNT` from 14 to 16.

5. Before staging a playable book, require and validate its `publication.json` with the Explainer verifier. Emit the public fields as:

```jq
edition: {
  status: $publication.publicationStatus,
  humanListeningStatus: $publication.humanListeningStatus,
  disclosure: $publication.disclosure
}
```

For older books without `publication.json`, emit `edition: null`; do not retroactively invent their human-listening state.

6. Add a shell `validate_series` function that uses `jq -e` to require:

- schema version 2;
- valid unique kebab-case IDs;
- nonblank title/description;
- one featured series;
- positive `plannedVolumeCount`;
- sorted, unique positive volume numbers no greater than the planned count;
- every referenced slug exists exactly once in the staged book catalog;
- no book belongs to more than one series;
- the featured series’ first volume is playable;
- no absolute path or file URL appears in series input or final catalog.

7. Change final catalog assembly to:

```jq
{
  version: 2,
  generated: $generated,
  source: {repo: "dfakkeldy/explainer-audiobooks", commit: $commit},
  series: $series[0].series,
  books: $books
}
```

where books are slurped from the staged per-book JSON files and series comes from `Tools/listen-series.json`. Validate the complete staged bundle before the transactional install.

8. Extend transaction tests with invalid series fixtures: duplicate ID, unsorted numbers, missing book, duplicate membership, and an absolute path. Each must fail without altering the existing installed catalog or assets.

9. Run tests. They should still fail only because generated catalog/assets have not been rebuilt:

```bash
make test-listen
```

10. Commit the builder and tests:

```bash
git add Tools/listen-series.json Tools/build-listen-catalog.sh \
  Tests/listen/catalog.test.mjs Tests/listen/catalog-transaction.test.mjs
git commit -m "feat: add versioned listening series catalog"
```

## Task 9: Implement Pure Series Resolution Logic

**Files:**

- Modify: `Resources/listen/listen-core.js`
- Modify: `Tests/listen/listen-core.test.mjs`

1. Add failing unit tests for these exported functions:

```javascript
const context = core.seriesContext(catalog, 'claude-platform-02-thinking-and-reliable-responses');
assert.equal(context.series.id, 'claude-platform');
assert.equal(context.volume.number, 2);
assert.equal(context.availableCount, 2);
assert.equal(context.plannedCount, 9);
assert.equal(context.previous.book, 'claude-platform-01-the-message');
assert.equal(context.next, null);

assert.equal(core.defaultBookSlug(catalog), 'claude-platform-01-the-message');
assert.deepEqual(core.librarySections(catalog, 'claude-platform-01-the-message'), {
  series: [{
    id: 'claude-platform',
    books: [
      'claude-platform-01-the-message',
      'claude-platform-02-thinking-and-reliable-responses',
    ],
  }],
  moreBooks: ['standalone-book'],
});
```

Also test a standalone book, malformed catalog input, and a series whose unpublished future volumes are absent. No function may synthesize Volume 3–9 cards.

2. Run RED:

```bash
node --test Tests/listen/listen-core.test.mjs
```

3. Implement and export `seriesContext(catalog, slug)`, `defaultBookSlug(catalog)`, and `librarySections(catalog, selectedSlug)`.

`seriesContext` resolves membership exclusively by scanning `series[].volumes[].book`. Previous/next are adjacent published entries in that ordered array. `defaultBookSlug` uses the first playable volume of the featured series, then falls back to the first playable book. `librarySections` returns every normalized series shelf with published books only, plus standalone books under `moreBooks`. It preserves the active book in its ordered series shelf so the UI can mark it `aria-current`, but never duplicates a series book under More books.

4. Run GREEN and commit:

```bash
node --test Tests/listen/listen-core.test.mjs
git add Resources/listen/listen-core.js Tests/listen/listen-core.test.mjs
git commit -m "feat: resolve listening series context"
```

## Task 10: Render Series Context, Navigation, and Grouped Library

**Files:**

- Modify: `Resources/listen/index.html`
- Modify: `Resources/listen/listen.js`
- Modify: `Resources/listen/listen.css`
- Modify: `Tests/listen/player-dom.test.mjs`
- Modify: `Tests/listen/contrast.test.mjs` only if a new color token is introduced.

1. Add failing DOM/source tests requiring these IDs and behaviors:

```text
bookSeries
seriesProgress
seriesPrevious
seriesNext
editionStatus
seriesShelves
seriesLibrary
moreBooksShelf
library
```

Require visible text for the pending review; navigation must be real links with book query parameters; inactive sections must use `hidden`; cover alt text and heading order remain valid.

2. Run RED:

```bash
node --test Tests/listen/player-dom.test.mjs Tests/listen/contrast.test.mjs
```

3. Add semantic player markup directly above the existing title:

```html
<p id="bookSeries" class="book-series" hidden></p>
<p id="seriesProgress" class="series-progress" hidden></p>
<nav class="series-navigation" aria-label="Published volumes in this series" hidden>
  <a id="seriesPrevious" class="series-link" hidden></a>
  <a id="seriesNext" class="series-link" hidden></a>
</nav>
<p id="editionStatus" class="edition-status" hidden></p>
```

4. Replace the single flat library heading with a series-shelf container and a standalone shelf:

```html
<section id="seriesShelves" class="room-library" aria-labelledby="seriesLibraryTitle" hidden>
  <h2 id="seriesLibraryTitle">Series</h2>
  <div id="seriesLibrary"></div>
</section>
<section id="moreBooksShelf" class="room-library" aria-labelledby="moreBooksTitle">
  <h2 id="moreBooksTitle">More books</h2>
  <ul id="library"></ul>
</section>
```

5. In `listen.js`:

- retain valid explicit `?book=` selection and the current invalid-slug error;
- replace `available[0]` fallback with `core.defaultBookSlug(catalog)`;
- render series title as `Claude Platform Documentation · Volume N`;
- render `2 of 9 planned volumes available`;
- render previous/next only when an adjacent published volume exists;
- render the exact `edition.disclosure` for public-first-listen books;
- split library cards with `core.librarySections`;
- render one ordered shelf per series with title, description, availability count, and published-volume cards;
- keep the selected book in its series position as `aria-current="page"` without a redundant Listen action;
- keep all series books out of More books, which contains standalone titles only;
- keep all existing player, transcript, speed, and deep-link behavior.

6. Style within the existing dark metal/gold system. On wide screens, previous/next may share one row. On narrow screens, stack them and both shelves vertically. Do not add a carousel or horizontal scroll. Use existing color variables wherever possible, retain visible keyboard focus, and meet WCAG AA contrast.

7. Run the focused and full browser logic suites:

```bash
node --test Tests/listen/player-dom.test.mjs Tests/listen/listen-core.test.mjs Tests/listen/contrast.test.mjs
make test-listen
```

8. Commit:

```bash
git add Resources/listen/index.html Resources/listen/listen.js \
  Resources/listen/listen.css Tests/listen/player-dom.test.mjs \
  Tests/listen/contrast.test.mjs
git commit -m "feat: present audiobook series in listening room"
```

## Task 11: Generate the Catalog from the Merged Book Commit

**Files:**

- Modify by tool: `Resources/listen/books.json`
- Create by tool: `Resources/listen/books/claude-platform-01-the-message/*`
- Create by tool: `Resources/listen/books/claude-platform-02-thinking-and-reliable-responses/*`
- Modify by tool: paired cover provenance if required by the existing cover-sync workflow.

1. Update the clean Explainer checkout used by the builder to the exact merged `origin/main` commit proven in Task 7:

```bash
git -C /Users/dfakkeldy/Developer/explainer-audiobooks fetch origin
git -C /Users/dfakkeldy/Developer/explainer-audiobooks worktree add --detach \
  /Users/dfakkeldy/.codex/worktrees/explainer-public-catalog-source origin/main
BOOKS_SHA="$(git -C /Users/dfakkeldy/.codex/worktrees/explainer-public-catalog-source rev-parse HEAD)"
```

2. Derive the approved Echo CLI/resources from either public book’s immutable input receipt in its private master. Set the exact command in `ECHO_CLI`; do not use an arbitrary installed Echo binary.

3. Run the transactional builder:

```bash
BOOKS_REPO=/Users/dfakkeldy/.codex/worktrees/explainer-public-catalog-source \
ECHO_CLI="$ECHO_CLI" \
Tools/build-listen-catalog.sh
```

Expected:

- catalog version 2;
- 16 books;
- 8 playable books;
- both new read-along bundles installed;
- source commit equals `$BOOKS_SHA`;
- no warning that HEAD is unmerged;
- transaction completes without partial installation.

4. Run the existing paired-cover synchronization so both Claude books use the square `m4b-cover.png` in player cards, with exact provenance and dimensions:

```bash
BOOKS_REPO=/Users/dfakkeldy/.codex/worktrees/explainer-public-catalog-source \
Tools/sync-paired-cover-assets.sh
```

5. Run catalog tests:

```bash
make test-listen
```

Expected: all Node tests pass, including exact anchor counts and version 2 series assertions.

6. Commit generated Resources:

```bash
git add Resources/listen Tools/listen-series.json Tools/build-listen-catalog.sh Tests/listen
git commit -m "chore: publish Claude Platform listening catalog"
```

## Task 12: Generate and Inspect the Static Site

**Files:**

- Modify only through generation: `Output/listen/*`

1. Build and test the site:

```bash
swift build
make test
make generate
```

Expected: Swift build succeeds, all listening/game tests pass, and Publish regenerates `Output/`.

2. Prove source/output parity:

```bash
cmp Resources/listen/books.json Output/listen/books.json
cmp Resources/listen/listen-core.js Output/listen/listen-core.js
cmp Resources/listen/listen.js Output/listen/listen.js
cmp Resources/listen/listen.css Output/listen/listen.css
```

3. Serve the generated site locally:

```bash
"$PYTHON" -m http.server 8000 --directory Output
```

Inspect at both viewport widths:

- `http://localhost:8000/listen/`
- `http://localhost:8000/listen/?book=claude-platform-02-thinking-and-reliable-responses`
- desktop around 1440 px;
- mobile around 390 px.

Verify:

- Volume 1 is the default;
- direct Volume 2 link works;
- series title and `2 of 9 planned volumes available` are visible;
- Volume 2 has a Previous link and no invented Next link;
- pending first-listen disclosure is visible;
- Series and More books shelves are stacked and readable;
- play, seek, chapters, transcript highlighting, and speed controls still work;
- keyboard focus, cover alt text, and heading hierarchy remain usable.

4. Commit generated output without using `make publish`:

```bash
git add Output
git commit -m "chore: regenerate listening room"
```

5. Final repository verification:

```bash
make test
git diff origin/main...HEAD --check
git status --short --branch
```

Expected: all tests pass and worktree is clean.

## Task 13: Publish and Verify KinNoKi Labs

**Files:** No new source files.

1. Rebase, rerun, push, and open a ready PR:

```bash
git fetch origin
git rebase origin/main
make test
git push -u origin codex/kinnoki-claude-platform-series
gh pr create --base main --head codex/kinnoki-claude-platform-series \
  --title "Add Claude Platform series to Listening Room" \
  --body-file /tmp/claude-platform-site-pr.md
```

The PR body must name the exact merged Explainer commit pinned in `books.json`, the catalog schema migration, the two new playable books, mobile/accessibility verification, and the first-listen disclosure.

2. Watch CI, then merge under the user’s explicit publish authorization:

```bash
gh pr checks --watch
gh pr merge --squash --delete-branch
```

3. Wait for Cloudflare Pages to deploy the merged site commit. Verify production:

```bash
curl -fsS https://kinnokilabs.com/listen/books.json | jq -e '
  .version == 2 and
  (.series[] | select(.id == "claude-platform") | .plannedVolumeCount == 9) and
  ([.books[].slug] | index("claude-platform-01-the-message") != null) and
  ([.books[].slug] | index("claude-platform-02-thinking-and-reliable-responses") != null)
'
```

Then range-test the production catalog’s actual audio URLs:

```bash
for slug in claude-platform-01-the-message claude-platform-02-thinking-and-reliable-responses; do
  url="$(curl -fsS https://kinnokilabs.com/listen/books.json | jq -r --arg slug "$slug" '.books[] | select(.slug == $slug) | .audio.url')"
  curl -fsSI -H 'Range: bytes=0-1023' "$url" | rg -i '^HTTP/|^content-range:'
done
```

Expected: both return HTTP 206.

4. Open production in a browser and verify the same default/deep-link/player/series/disclosure checks from Task 12. Automated playback proves browser delivery, not a completed human road listen; keep that proof boundary explicit.

## Task 14: Record the Durable Business Receipt

**Files:**

- Modify: `/Users/dfakkeldy/Developer/knowledge-base/projects/explainer-audiobooks.md`
- Create: `/Users/dfakkeldy/Developer/knowledge-base/status/2026-07-18-claude-platform-public-series.md`
- Modify: KB indexes/logs required by its `AGENTS.md`.

1. Use a clean KB worktree and follow its local instructions. Record only public-safe facts:

- both public slugs and live URLs;
- series ID, title, and planned count 9;
- Explainer PR, merge commit, and package verification;
- site PR, merge commit, and Cloudflare deployment proof;
- raw and production HTTP 206 proof;
- status `public-first-listen` and human road listen pending;
- no iCloud copy was made;
- private masters remain outside Git and are not linked by local path in public material;
- a later `revise` verdict supersedes the public edition.

2. Do not copy private listening notes, raw source maps, narration receipts, or local package paths into the public-safe receipt.

3. Run KB validation, commit, push, and open/merge its scoped PR according to the KB’s current tier rules.

## Final Verification Matrix

| Layer | Required proof |
|---|---|
| Private masters | Read-only hashes and governed media checks pass; no mutations |
| Public packages | Verifier passes, EPUB valid, exact M4B/sidecar parity, safe receipt, no private artifacts |
| Explainer Git | PR merged to `main`; both public M4Bs return HTTP 206 at merged SHA |
| Catalog | Version 2, normalized series, 9 planned, both books playable, exact merged source SHA |
| Listening UI | Default Volume 1, deep links preserved, series context/navigation, grouped shelves, visible pending disclosure |
| Generated site | `Resources/` and `Output/` parity; tests green; mobile and keyboard checks pass |
| Production | `kinnokilabs.com/listen` serves schema 2 and both audio URLs return HTTP 206 |
| Human evidence | Explicitly still pending; automated playback is not represented as a human road listen |
| iCloud | No new copy made |
| Knowledge base | Sanitized publication receipt committed after live verification |

## Plan Self-Review Checklist

Before implementation begins, confirm:

- every approved design requirement maps to at least one task above;
- all nine canonical planned volumes are represented only by the planned count, with no placeholder cards;
- the public Volume 1 slug never includes `road-book-v2`;
- `public-first-listen` never aliases `final`, `human-approved`, `learning-validated`, or `pronunciation-accepted`;
- the exact disclosure string is identical in skill policy, publication receipts, catalog, tests, and UI;
- catalog type names use `series[].volumes[].book` consistently;
- no step recursively copies a private master into Git;
- no step writes to iCloud;
- no site build occurs before the Explainer merge SHA is public and range-fetchable;
- no generated `Output/` file is manually edited;
- placeholder scan is clean:

```bash
rg -n 'TODO|TBD|FIXME|<slug>|<sha>|example\.com|coming soon' \
  docs/superpowers/plans/2026-07-18-claude-platform-public-series.md
```

The expected hits are only explanatory examples in this plan, never unresolved implementation values.
