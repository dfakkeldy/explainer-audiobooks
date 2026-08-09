# Public Fiction Gate And Runbook

Private delivery completes before this gate. An explicit private request,
private source, rights uncertainty, or any failed condition means private-only:
record the reason below `_production/publication/` and perform zero GitHub
mutation. Automated checks never establish human reading or listening.

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

## Stage and verify

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
  --echo-success-receipt "$ECHO_SUCCESS_RECEIPT"
```

Only after success, copy the six public files into `books/<slug>/`, update the
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
  --notes-file "$RUN_ROOT/research/release-notes.md"
```

The PR must be ready: never pass `--draft` and never merge it. Verify the
release:

```bash
gh release view "$RELEASE_TAG" --json tagName,targetCommitish,assets,url
```

Compare tag, target commit, asset name, and—when GitHub supplies one—asset
digest. A GitHub failure does not undo successful iCloud delivery: preserve
the verified publication stage and report the GitHub state as retryable.
