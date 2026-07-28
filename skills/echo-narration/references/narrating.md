# Narrating

Echo owns the M4B, alignment, and pronunciation-review renderer. Narration is
an installed-package operation: it never builds, checks out, or repairs Echo.
Never invoke a DerivedData `Debug/echo-cli`, a raw direct `echo-cli narrate`, or
an older audiobook worktree command for a governed render; those paths bypass
the wrapper's installed-package provenance, resource leases, and locked
postchecks. The narration entry point is
`skills/echo-narration/scripts/echo_pronunciation_narrate.sh`.

## Installed renderer store and approvals

The local, content-addressed store is:

```text
~/Library/Application Support/Echo/Renderers/
  <40-hex source SHA>/
    approved-renderer.json
    <64-hex manifest SHA>/
      echo-cli
      EchoNarrationResources/
      renderer-manifest.json
```

`<40-hex source SHA>` is the reviewed Echo source revision and `<64-hex
manifest SHA>` names one immutable Release package. A source can have several
packages; `approved-renderer.json` selects only the package for a *new* run.
`APPROVED_ECHO_PRONUNCIATION_SHA` is required for every governed narration and
must be exactly 40 lowercase hexadecimal characters. It must exactly equal the
installed package's `ECHO_SOURCE_SHA`; a branch name, abbreviated SHA, current
checkout, or inferred revision is not approval. The separate installer review
is `APPROVED_ECHO_INSTALLER_SHA`, also an exact 40-character SHA. Record both
identities in the render-input receipt.

For a new render the wrapper uses `resolve-new`, which reads the selector while
leased and seals the selected manifest. For `--resume`, provide the canonical
absolute `research/echo-resume-state-$RUN_ID.json`; the wrapper uses
`resolve-resume` and the sealed resume-state receipt, never a possibly changed
selector. Do not copy captures, edit receipts, or turn a historical receipt
into an operational resume. Historical receipts are read-only verification
evidence; only the current installed-renderer schema and matching
manifest-bound receipts can resume, publish, or authorize delivery.

The wrapper records `ECHO_CLI_SHA256`, `ECHO_RESOURCES_SHA256`,
`ECHO_RENDERER_MANIFEST_SHA256`, the exact source/installer SHAs, and the
canonical `ECHO_RENDERER_BUILD_ROOT`. It passes the sealed
`ECHO_RESOURCE_DIR` explicitly to every probe, narration, and
`verify-sidecar` call, and re-attests the installed package before launch and
before publication. The model-policy fields are informational only:
`modelBytesAttested: false` means the shared cached model bytes are not
attested by this package. Do not claim that a package receipt verifies the
model cache.

## Operator-only install and recovery

Install, verification, promotion, and repair happen outside narration from a
clean, reviewed Echo installer worktree with separate clean installer and
source worktrees. Use the exact installer interface, not an improvised build:

```bash
PYTHONPATH=Scripts python3 -m echo_renderer.cli install \
  --installer-worktree <installer worktree> \
  --installer-sha <APPROVED_ECHO_INSTALLER_SHA> \
  --source-worktree <source worktree> \
  --source-sha <APPROVED_ECHO_PRONUNCIATION_SHA>

PYTHONPATH=Scripts python3 -m echo_renderer.cli verify \
  --source-sha <APPROVED_ECHO_PRONUNCIATION_SHA> \
  --manifest-sha <64-hex manifest SHA>

PYTHONPATH=Scripts python3 -m echo_renderer.cli promote \
  --source-sha <APPROVED_ECHO_PRONUNCIATION_SHA> \
  --manifest-sha <64-hex manifest SHA>

PYTHONPATH=Scripts python3 -m echo_renderer.cli repair \
  --installer-worktree <installer worktree> \
  --installer-sha <APPROVED_ECHO_INSTALLER_SHA> \
  --source-worktree <source worktree> \
  --source-sha <APPROVED_ECHO_PRONUNCIATION_SHA> \
  --manifest-sha <64-hex manifest SHA>
```

- **Missing version/selector**: install the exact approved source. Use
  `install --promote` only for a source with no selector; otherwise verify the
  new package and promote it explicitly after review.
- **Corrupt package or failed attestation**: run `verify` first. If it cannot
  verify, use `repair` for that exact source/manifest identity; repair
  quarantines bytes and never promotes a selector.
- **Incompatible package**: exit 69 means the Release package, capability,
  architecture, or deployment floor is incompatible with the host. Install a
  reviewed compatible renderer; do not weaken the narration wrapper.
- **Approval mismatch**: obtain the exact reviewed
  `APPROVED_ECHO_PRONUNCIATION_SHA` and select/install that identity. Do not
  substitute a descendant, branch, or local checkout.
- **Live lease (exit 75)**: wait for the holder and retry. Do not force a
  selector, repair, or narration past a live lease. The narration wrapper's
  `--recover-stale-lock` is only for its exact proven-local stale owner record;
  it does not build, repair, or narrate.

No automatic cleanup or update is permitted. Old packages and repair
quarantines are preserved until an operator makes a manual disposition. The
renderer store is local-only: it has no code-signing, notarization, or
cross-machine distribution authority.

## Voice and invocation

Invoke the wrapper only through its public entry point. Do not bypass the
wrapper with a direct CLI command. This is installed renderer work, never
narration-time build work. Stop immediately on any failure:

```bash
set -euo pipefail
: "${NARRATION_SCRIPT:?set the absolute installed echo_pronunciation_narrate.sh path}"
[[ "$NARRATION_SCRIPT" == /* && -x "$NARRATION_SCRIPT" ]]
NARRATION_SCRIPT_DIR=$(cd -- "$(dirname -- "$NARRATION_SCRIPT")" && pwd -P)
PIPELINE_ROOT=$(cd -- "$NARRATION_SCRIPT_DIR/../../.." && pwd -P)
[[ "$NARRATION_SCRIPT" == \
  "$PIPELINE_ROOT/skills/echo-narration/scripts/echo_pronunciation_narrate.sh" ]]
EXPLAINER_ROOT="$PIPELINE_ROOT"
export EXPLAINER_ROOT
export RUN_ROOT="$PIPELINE_ROOT/.build/custom-learning-audiobooks/$SLUG"
export DIST="$RUN_ROOT/dist"
export VOICE=am_michael
export SLUG TITLE
export COVER="$PAIR/cover.png"
export M4B_COVER="$PAIR/m4b-cover.png"
: "${APPROVED_ECHO_PRONUNCIATION_SHA:?set the exact reviewed 40-character source SHA}"
export APPROVED_ECHO_PRONUNCIATION_SHA

"$NARRATION_SCRIPT"
```

For a mixed-voice book, pass one repeatable mapping per narratable chapter.
Chapter numbers are one-based in the same order readers see in the EPUB. Echo's
full English `VoiceCatalog` is allowed:

```bash
"$NARRATION_SCRIPT" \
  --chapter-voice 1=af_heart \
  --chapter-voice 2=af_bella \
  --chapter-voice 3=am_fenrir
```

The wrapper validates and chapter-sorts the mappings, hashes the exact default
voice plus mapping plan into the `RUN_ID`, records the canonical plan and hash
in the immutable input receipt, and repeats the plan in the sealed resume-state
receipt. A resume must pass the identical `--chapter-voice` arguments. Changing,
adding, or removing one mapping selects a different `WORK`, database, and
receipt chain.

Pronunciation review is on by default; it applies approved rules before TTS
and emits review evidence automatically. Do not pass
`--no-pronunciation-review` for a governed render. The command uses the
default `--voice am_michael` through `VOICE` and keeps synthesis bounded at
one chapter job and two Kokoro threads.

If `am_michael` fails because the voice resource is unavailable, set and
export `VOICE=am_puck`, then rerun the wrapper. Its preflight derives a new
`RUN_ID`, `WORK`, `DB`, receipt, and resource leases. Record the fallback. Do
not silently use `af_heart`.

Do not add a self-imposed timeout around `echo-cli narrate`, kill a
progressing render because it may take several hours, or replace it with
Apple/macOS/system voice narration for convenience. Native Echo/Kokoro output
is the only accepted narrator; the only automatic fallback is from
`am_michael` to `am_puck` when the preferred Echo voice is unavailable.

## Resuming and partial renders

Use a fresh `--work-dir` and `--db` whenever the source EPUB changes or the
Release CLI binary or Echo source revision changes. Permit `--resume` only for
the same immutable source EPUB, exact approved/source revision, Release CLI
and resource-tree hashes, voice, and capture set. The wrapper requires
`research/echo-resume-state-$RUN_ID.json` to bind the current DB and every
capture-marker/audio hash. Every capture must carry a sealed schema-v1 Echo
identity for the exact Release render version recorded in the immutable input
receipt, the current EPUB fingerprint and voice, one consistent capture-set
ID, pronunciation evidence, and matching audio byte count and SHA-256. Legacy
identity-free captures are never blessed by this workflow. The wrapper's
success receipt binds the resume-state receipt's own derived filename and
hash as `resumeStateFileName` and `resumeStateSHA256`.

Only then rerun the wrapper with `--resume`; it must select the original
`WORK`/`DB` and acquire all resource leases before it invokes Echo:

```bash
ATTEMPT_RECEIPT="$RUN_ROOT/research/echo-render-current-attempt.json"
RUN_ID=$(/usr/local/bin/python3 -c \
  'import json,sys; print(json.load(open(sys.argv[1]))["runID"])' \
  "$ATTEMPT_RECEIPT")
RESUME_STATE="$RUN_ROOT/research/echo-resume-state-$RUN_ID.json"
[[ "$RESUME_STATE" == /* && -f "$RESUME_STATE" ]]
"$NARRATION_SCRIPT" --resume --resume-state "$RESUME_STATE"
```

Never copy old captures into a new run, edit a receipt, or resume after
editing the EPUB or rebuilding Echo; the content-addressed `RUN_ID` selects
fresh paths and the preflight rejects unreceipted or mismatched pre-existing
paths.

For an operator-led check of an exact local stale lock record, use:

```bash
"$EXPLAINER_ROOT/skills/echo-narration/scripts/echo_pronunciation_narrate.sh" --recover-stale-lock
```

Recovery does not narrate. Rerun the wrapper normally or with `--resume` after
a successful recovery.

For a partial, real-book pronunciation probe, the wrapper may render one new
chapter at a time while retaining the same source, approved renderer,
resource tree, `WORK`, and database. On a multi-chapter book, the first
command returns CLI **exit 2**, meaning that its chapter capture and resume
state were sealed but the book is still partial:

```bash
set +e
"$NARRATION_SCRIPT" \
  --max-chapters 1
rc=$?
set -e
[[ "$rc" == 2 ]]
```

To render exactly the next chapter, request one new chapter again — not two,
because the option counts uncaptured chapters in the current process:

```bash
set +e
ATTEMPT_RECEIPT="$RUN_ROOT/research/echo-render-current-attempt.json"
RUN_ID=$(/usr/local/bin/python3 -c \
  'import json,sys; print(json.load(open(sys.argv[1]))["runID"])' \
  "$ATTEMPT_RECEIPT")
RESUME_STATE="$RUN_ROOT/research/echo-resume-state-$RUN_ID.json"
[[ "$RESUME_STATE" == /* && -f "$RESUME_STATE" ]]
"$NARRATION_SCRIPT" \
  --resume --resume-state "$RESUME_STATE" --max-chapters 1
rc=$?
set -e
[[ "$rc" == 2 ]]
```

Each partial attempt updates `echo-render-current-attempt.json` and seals
`echo-resume-state-$RUN_ID.json`, but it has **no accepted M4B**, sidecar,
pronunciation audit, success receipt, or current-accepted selector. Partial
capture audio is listening evidence, not a deliverable package. Resume later
without `--max-chapters` only once the book is ready to complete.

## Alignment sidecar

Every render publishes `<slug>.alignment.json` beside `<slug>.m4b`,
`<slug>.pronunciation-audit.json`, and — when timed review samples exist —
`<slug>.pronunciation-reel.m4b`, at a run/attempt-scoped path under
`dist/echo-renders/<run-id>/<attempt-id>/`. The sidecar binds the audio to the
source EPUB text so a reading app, and later QC, can follow along. Parse it
with `python3 -m json.tool "$SIDECAR"` before trusting it downstream, and
treat `echo-cli verify-sidecar` as the authoritative consumer — it cross-checks
the sidecar against the exact EPUB and audio bytes and must report
`SIDECAR_OK`.

## Audio verification

After a render completes, resolve the accepted artifacts from the current
selector, then verify them before treating the render as done:

```bash
ATTEMPT_RECEIPT="$RUN_ROOT/research/echo-render-current-attempt.json"
CURRENT_SELECTOR="$RUN_ROOT/research/echo-render-current-accepted.json"
selector_value() {
  /usr/local/bin/python3 - "$CURRENT_SELECTOR" "$1" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as source:
    value = json.load(source).get(sys.argv[2])
if not isinstance(value, str) or not value:
    raise SystemExit(f"missing selector string: {sys.argv[2]}")
print(value)
PY
}
RUN_ID=$(selector_value runID)
ATTEMPT_ID=$(selector_value attemptID)
ARTIFACT_RELATIVE_PATH=$(selector_value artifactRelativePath)
INPUT_RECEIPT_NAME=$(selector_value inputReceiptFileName)
SUCCESS_RECEIPT_NAME=$(selector_value successReceiptFileName)
STATE_RECEIPT_NAME="echo-resume-state-$RUN_ID.json"
STATE_HELPER="$EXPLAINER_ROOT/skills/echo-narration/scripts/echo_pronunciation_state.py"
/usr/local/bin/python3 "$STATE_HELPER" validate-run-id "$RUN_ID"
[[ "$ATTEMPT_ID" =~ ^[0-9a-f]{64}$ ]]
[[ "$ARTIFACT_RELATIVE_PATH" == "echo-renders/$RUN_ID/$ATTEMPT_ID" ]]
[[ "$INPUT_RECEIPT_NAME" == "echo-render-inputs-$RUN_ID.env" ]]
[[ "$SUCCESS_RECEIPT_NAME" == "echo-render-success-$RUN_ID-$ATTEMPT_ID.json" ]]
[[ "$STATE_RECEIPT_NAME" == "echo-resume-state-$RUN_ID.json" ]]

ARTIFACT_ROOT="$DIST/$ARTIFACT_RELATIVE_PATH"
INPUT_RECEIPT="$RUN_ROOT/research/$INPUT_RECEIPT_NAME"
STATE_RECEIPT="$RUN_ROOT/research/$STATE_RECEIPT_NAME"
SUCCESS_RECEIPT="$RUN_ROOT/research/$SUCCESS_RECEIPT_NAME"
AUDIOBOOK="$ARTIFACT_ROOT/$SLUG.m4b"
SIDECAR="$ARTIFACT_ROOT/$SLUG.alignment.json"
AUDIT="$ARTIFACT_ROOT/$SLUG.pronunciation-audit.json"
REEL="$ARTIFACT_ROOT/$SLUG.pronunciation-reel.m4b"

/usr/local/bin/python3 "$STATE_HELPER" \
  verify-delivery \
  --attempt "$ATTEMPT_RECEIPT" \
  --selector "$CURRENT_SELECTOR" \
  --receipt "$SUCCESS_RECEIPT" \
  --input-receipt "$INPUT_RECEIPT" \
  --state-receipt "$STATE_RECEIPT" \
  --epub "$DIST/$SLUG.epub" \
  --audiobook "$AUDIOBOOK" \
  --sidecar "$SIDECAR" \
  --audit "$AUDIT" \
  --reel "$REEL"

CLI=$(awk -F= '$1 == "echo_cli_path" { print substr($0, index($0, "=") + 1) }' \
  "$INPUT_RECEIPT")
ECHO_RESOURCE_DIR=$(awk -F= '$1 == "echo_resource_dir" { print substr($0, index($0, "=") + 1) }' \
  "$INPUT_RECEIPT")
export ECHO_RESOURCE_DIR

ffprobe -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 "$AUDIOBOOK"

/usr/local/bin/python3 -m json.tool "$SIDECAR" >/dev/null

"$CLI" verify-sidecar \
  --epub "$DIST/$SLUG.epub" \
  --audio "$AUDIOBOOK" \
  --sidecar "$SIDECAR"

/usr/local/bin/python3 "$EXPLAINER_ROOT/skills/echo-narration/scripts/validate_pronunciation_audit.py" \
  "$AUDIT"
```

Require `SIDECAR_OK` from `verify-sidecar`. The current media-bound manifest
schema version is `3`; schema `2` remains accepted for earlier uniform governed
renders. Require `coverage=complete`, render version 12 or newer, a known Echo
English voice or `mixed`, complete valid `chapterVoices` provenance for schema
3, schema-valid decision objects and timing ranges,
and watch counts that match decisions across the complete emitted watch
vocabulary, including zero counts. Require `audiobookSHA256` to match the
exact raw sibling M4B bytes; when a reel is listed, require
`listeningReelSHA256` to match the exact raw sibling reel bytes. The audit
JSON is the pronunciation audit; an optional pronunciation reel accompanies
it when timed review samples exist. Automated checks do not substitute for
hearing the result: human listening remains explicitly pending until someone
actually listens, and the report must say so.

## Interior Figures

`skill/scripts/build_book.py` can embed pictures in the EPUB and copy them
beside the combined Markdown. Store package images under `chapters/images/`,
then insert each approved figure as its own Markdown paragraph:

```markdown
![Descriptive alt text](images/figure-01.png "Caption shown under the figure")
```

Image paths resolve relative to the chapters directory. Supported formats are
PNG, JPEG, GIF, SVG, and WebP. Keep `research/visuals.md` with each image's
source/provenance, license or permission status, intended placement, alt text,
caption, and public/private safety.

Rules:

- Use user-supplied, generated, self-created, public-domain, permissively
  licensed, or explicitly permissioned images.
- Treat found web images as references unless the rights allow inclusion.
- Do not copy private or sensitive images into public repo or KB outputs.
- Use meaningful alt text and captions; avoid decorative filler.
- Prefer a few purposeful figures that teach, orient, compare, or document.

## Cover immutability

Echo resolves the EPUB's OPF-declared cover before export and hashes the
exact resulting M4B into its pronunciation audit. Never run
`replace_m4b_cover.py` or otherwise mutate an audited Echo M4B after
narration — not to fix a cover, not to retag it, not for any reason. If
something is wrong with the package, correct the source and rerender so Echo
emits and hashes the final bytes itself.
