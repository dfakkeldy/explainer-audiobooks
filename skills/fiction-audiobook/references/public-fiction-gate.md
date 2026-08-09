# Public Fiction Gate And Runbook

Evaluate and record this gate before final iCloud staging; mutate GitHub only
after iCloud succeeds. An explicit private request, private source, rights
uncertainty, or failed condition means private-only: deliver the reason below
`_production/publication/` and perform zero GitHub mutation. Automated checks
never establish human reading or listening.

## Exact schema-v2 publication receipt

`publication.json` has exactly these fields and values/shapes:

```json
{
  "schemaVersion": 2,
  "packageKind": "fiction-audiobook",
  "slug": "<slug>",
  "editionId": "<nonempty-edition-id>",
  "publicationStatus": "public-first-listen",
  "humanReadingStatus": "pending",
  "humanListeningStatus": "pending",
  "classification": "public-safe",
  "permissionToPublish": true,
  "permissionGrantedAt": "<timestamp>",
  "author": "Dan Fakkeldy",
  "contributor": "<generating-model>",
  "aiGenerated": true,
  "contentLicense": "CC-BY-4.0",
  "disclosure": "This original AI-generated fiction edition is published under CC BY 4.0 as a public first-listen. Automated package and audio checks passed; human reading and listening reviews remain pending.",
  "publicGate": {
    "originalFiction": true,
    "noPrivateSource": true,
    "noLivingPersonTarget": true,
    "noLivingAuthorImitation": true,
    "coverRightsVerified": true
  },
  "coverRights": {
    "basis": "generated",
    "status": "verified",
    "coverSHA256": "<sha256>"
  },
  "artifacts": {
    "manuscript": {"file": "<slug>.md", "sha256": "<sha256>"},
    "epub": {"file": "<slug>.epub", "sha256": "<sha256>"},
    "alignment": {"file": "<slug>.alignment.json", "sha256": "<sha256>"},
    "portraitCover": {"file": "cover.png", "sha256": "<sha256>"}
  },
  "release": {
    "tag": "fiction-<slug>-<editionId>",
    "assetFile": "<slug>.m4b",
    "assetSHA256": "<sha256>"
  },
  "privateEvidence": {
    "fictionReceiptSHA256": "<sha256>",
    "voiceCastSHA256": "<sha256>",
    "voicePlanSHA256": "<sha256>",
    "echoSuccessReceiptSHA256": "<sha256>"
  }
}
```

The five `publicGate` booleans mean: original characters/world rather than
unlicensed fan fiction; no private/confidential/recognizable private-life
source; no identifiable living-person target without permission; no imitation
of a living author; and verified cover rights. Cover basis is exactly one of
`original`, `generated`, `public-domain`, `permissively-licensed`, or
`explicit-permission`; the last two also require a nonempty `provenanceNote`.
The cover may be original, generated, public-domain, permissively licensed, or
explicitly permissioned—never merely found online.

## Production evidence before delivery

Set `PRODUCTION="$RUN_ROOT/_production"`. Materialize one current, non-symlinked
evidence tree; `previous/` starts empty and only the stager fills it:

| Directory | Exact current-edition contents |
|---|---|
| `source/` | `brief.md`, `story-bible.md`, `outline.md`, `chapters/`, `continuity/`, `research/unattended-decisions.json`, unchanged `research/fiction-production-receipt.json`, `revisions/`, and `feedback.jsonl` (empty is valid) |
| `checks/` | schema-7 pronunciation audit plus captured successful `verify-delivery`, `verify-sidecar`, sidecar-JSON, audit-validator, and `ffprobe` results |
| `narration/` | completed schema-2 `voice-cast.json`; authored `echo-voice-plan.json`; sealed canonical plan; five-field resolution receipt; accepted input, attempt, resume, success, and selector receipts; delivered alignment sidecar; retained captures/reel only here |
| `covers/` | selected portrait/square pair, thumbnails, source art, specs, rights/provenance, render receipts, and selection receipt |
| `publication/` | `public-gate.json` and, on pass, the identical verified `publication.json`; on failure, the decision contains the nonempty reason |
| `previous/` | empty |

Copy canonical bytes from the run root; never summarize or edit receipts. Keep
all alternate audio, audits, logs, checksums, manuscripts, and alternate covers
below `_production`, never at the iCloud title root or in the public six-file
package. Do not add a seventh production directory. Write `public-gate.json`
with `decision` (`public` or `private`), timestamp, gate booleans, and reason.
Keep `publication.json` schema 2 and its current disclosure unchanged. A
private request/source or failed public gate performs zero GitHub mutation, and
automated block/audit checks do not set human reading or listening to complete.

## Stage and verify the public candidate

A private decision skips this section and proceeds to the skill's final iCloud
stager. A public decision derives all shell state under `set -u`:

```bash
PIPELINE_ROOT=$(git rev-parse --show-toplevel)
: "${RUN_ROOT:?}" "${SLUG:?}" "${EDITION_ID:?}"
[[ "$PIPELINE_ROOT" == /* ]]
[[ "$RUN_ROOT" == "$PIPELINE_ROOT/.build/fiction-audiobooks/$SLUG" ]]
PUBLIC_STAGE="$RUN_ROOT/public-stage-$EDITION_ID"
RELEASE_TAG="fiction-$SLUG-$EDITION_ID"
[[ "$PUBLIC_STAGE" != "$PIPELINE_ROOT/books/"* ]]
if [[ ! -e "$PUBLIC_STAGE" ]]; then mkdir "$PUBLIC_STAGE"; fi
[[ -d "$PUBLIC_STAGE" && ! -L "$PUBLIC_STAGE" ]]
```

Stage outside `books/`. `$PUBLIC_STAGE` must contain exactly `README.md`,
`publication.json`, `<slug>.md`, `<slug>.epub`,
`<slug>.alignment.json`, and `cover.png`. Keep the M4B and all private evidence
outside Git. `README.md` must include the exact disclosure from
`publication.json` and contain no private paths. Then run:

```bash
/usr/local/bin/python3 skill/scripts/verify_public_first_listen.py "$PUBLIC_STAGE" \
  --release-m4b "$AUDIOBOOK" \
  --voice-cast "$VOICE_CAST" \
  --fiction-receipt "$RUN_ROOT/research/fiction-production-receipt.json" \
  --chapters-dir "$RUN_ROOT/chapters" \
  --echo-success-receipt "$SUCCESS_RECEIPT"
```

After verifier success, copy `publication.json` unchanged into
`$PRODUCTION/publication/`; then run the skill's iCloud stager. Only after that
delivery succeeds, copy the six public files into `books/<slug>/`, update the
README catalogue, and publish in this order:

```bash
git add "books/$SLUG" README.md
git commit -m "book: publish $TITLE first listen"
git push -u origin HEAD
gh pr create --fill --head "$(git branch --show-current)"
PUBLIC_COMMIT=$(git rev-parse HEAD)
gh release create "$RELEASE_TAG" "$AUDIOBOOK#$SLUG.m4b" \
  --target "$PUBLIC_COMMIT" \
  --title "$TITLE — public first-listen" \
  --notes "This original AI-generated fiction edition is published under CC BY 4.0 as a public first-listen. Automated package and audio checks passed; human reading and listening reviews remain pending."
```

The release note is deliberately the exact disclosure already verified in the
public package. Do not upload a private notes file or interpolate private run
metadata into the public release body.

The PR must be ready: never pass `--draft` and never merge it. Verify the
release:

```bash
gh release view "$RELEASE_TAG" --json tagName,targetCommitish,assets,url
```

Compare tag, target commit, asset name, and—when GitHub supplies one—asset
digest. A GitHub failure does not undo successful iCloud delivery: preserve
the verified publication stage and report the GitHub state as retryable.
For a redo, reconcile the existing ready PR when one is open or create a new
ready PR, use the new derived release tag, verify the new asset, preserve prior
release bytes, and never merge.
