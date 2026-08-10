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

## Run lanes

The governed wrapper accepts only these exact run lanes:

```text
ECHO_RUN_LANE=audiobook          -> .build/custom-learning-audiobooks/<slug>/
ECHO_RUN_LANE=fiction-audiobook  -> .build/fiction-audiobooks/<slug>/
unset ECHO_RUN_LANE              -> audiobook (backward compatible)
```

For a fiction audiobook, set the lane and use the matching exact run root:

```bash
export ECHO_RUN_LANE=fiction-audiobook
export RUN_ROOT="$PIPELINE_ROOT/.build/fiction-audiobooks/$SLUG"
```

Any other lane value, including a path-like value, fails closed before
narration. The lane and run root are sealed into the immutable input receipt;
a fiction run must resume with `ECHO_RUN_LANE=fiction-audiobook`. Fiction uses
the source-bound block procedure below; do not invoke a bare wrapper or
`--chapter-voice` mapping for a fiction character cast.

## Voice and invocation

Invoke the wrapper only through its public entry point. Do not bypass the
wrapper with a direct CLI command. This is installed renderer work, never
narration-time build work. The generic default/chapter examples in this section
do not apply to a fiction character cast; use `Source-bound block voices`
below for that case. Stop immediately on any failure:

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

## Source-bound block voices

Use this block-mode procedure, not the chapter-voice mapping above, for either
a Nonfiction semantic cast or a Fiction character cast. Each mode starts from
an authored, frozen EPUB source and sends its validated plan to the same
installed Echo resolver and governed wrapper. Do not calculate a plan hash or
identity outside Echo.

### Select and validate the cast mode

- **Nonfiction semantic cast:** Follow
  `skill/references/semantic-voice-casting.md`, then load its validated argv0
  vector with `load_semantic_voice_arguments`. Its
  `semantic_voice_cast.py validate-cast` handoff binds the semantic cast,
  inventory, authored plan, and frozen EPUB before the wrapper.
- **Fiction character cast:** Follow `express-fiction-craft.md`. Before it
  starts, that workflow records each blank-line source paragraph's intended
  speaker and freezes the final EPUB. Load
  `fiction_voice_preferences.py validate-cast` argv0 with
  `load_fiction_voice_arguments` below. Do not infer a character speaker from
  quotation marks, attribution, prose, model output, or an Echo block.

Neither validator infers speakers, expands ranges, or computes resolved
identity. Echo alone decides block existence, speakability, range expansion,
resolved identity, canonical plan bytes, and the resolution receipt. Before
every first, resume, or partial block invocation, load the selected validator's
NUL-delimited vector again. It must be --voice-plan plus the canonical authored
plan; pass that exact vector unchanged to the wrapper.

### Export the installed-Echo inventory

Set `EPUB` to the absolute frozen EPUB and derive `EPUB_SHA256` from those
unchanged bytes. Store the private inventory only at:

```text
$RUN_ROOT/research/echo-block-inventory-$EPUB_SHA256.json
```

Resolve the installed renderer for this new inventory with the shared resolver:
`resolve-new --source-sha APPROVED_ECHO_PRONUNCIATION_SHA --format env0`.
The shared `echo_pronunciation_resolve_installed_renderer 0` below invokes
that exact `echo_installed_renderer.py` command, accepts only its fixed env0
record exactly once, and rejects incomplete, duplicate, or unknown keys without
interpreting shell text. It sets `CLI`, `ECHO_RESOURCE_DIR`, and
`ECHO_RENDERER_BUILD_ROOT`; validate and live-attest that installed package
before the leased inventory command:

```bash
EPUB="$RUN_ROOT/dist/$SLUG.epub"
EPUB_SHA256=$(/usr/bin/shasum -a 256 "$EPUB" | awk '{print $1}')
INVENTORY="$RUN_ROOT/research/echo-block-inventory-$EPUB_SHA256.json"
source "$EXPLAINER_ROOT/skills/echo-narration/scripts/echo_pronunciation_preflight.sh"
# Internally: echo_installed_renderer.py resolve-new \
#   --source-sha "$APPROVED_ECHO_PRONUNCIATION_SHA" --format env0
echo_pronunciation_resolve_installed_renderer 0
echo_pronunciation_validate_renderer_paths
echo_pronunciation_attest_renderer
```

Derive `CANONICAL_LEASE_ROOT` with the same effective-account helper as the
governed wrapper, not an arbitrary project lock directory. Lease the selected
`ECHO_RENDERER_BUILD_ROOT` and set `ECHO_RESOURCE_DIR` explicitly in the child:

```bash
CANONICAL_LEASE_ROOT=$(echo_pronunciation_canonical_lease_root)
LEASE_HELPER="$EXPLAINER_ROOT/skills/echo-narration/scripts/echo_pronunciation_lease.py"
"$LEASE_HELPER" --lock-root "$CANONICAL_LEASE_ROOT" \
  --resource "$ECHO_RENDERER_BUILD_ROOT" -- \
  /usr/bin/env "ECHO_RESOURCE_DIR=$ECHO_RESOURCE_DIR" \
  "$CLI" export-blocks --epub "$EPUB" --out "$INVENTORY"
```

This is exactly the installed command `echo-cli export-blocks --epub
ABSOLUTE_FROZEN_EPUB --out ABSOLUTE_PRIVATE_INVENTORY_JSON`. It receives no
voice plan and emits only Echo inventory version 2 `{blocks, source, version}`.
Its source is exactly `{epub, epubSHA256}`: `epub` is the frozen regular EPUB
filename and `epubSHA256` is the lowercase SHA-256 of its exact bytes. An
expanded directory may report a null digest but is intentionally invalid for
semantic narration; do not substitute it for a frozen EPUB. `export-blocks`
rejects PDFs, containers, symlinks, and nonregular inputs; this handoff must
therefore preserve the direct regular frozen EPUB boundary. The inventory has
no speaker field and makes no assignment. Never substitute a checkout or
PATH-selected CLI.

### Author, validate, and resolve the fiction plan

The nonfiction semantic reference owns its distinct cast and prevalidation;
continue there for its authoring inputs and use the shared inventory, resolver,
wrapper, and evidence flow here. Do not use the fiction schema-2 cast or local
preferences for a semantic role cast.

Set `VOICE_CAST="$RUN_ROOT/_production/narration/voice-cast.json"` and
`VOICE_PLAN="$RUN_ROOT/_production/narration/echo-voice-plan.json"`. From the
installed inventory, write the schema-2 cast with three-to-five stable,
nonblacklisted voices and the exact sibling schema-1 Echo plan. The lead writer
assigns every block intentionally. Local validation checks the cast and
preferences; it does not infer dialogue or decide which blocks exist:

```bash
/usr/local/bin/python3 \
  skills/fiction-audiobook/scripts/fiction_voice_preferences.py \
  validate-cast --cast "$VOICE_CAST" --voice-plan "$VOICE_PLAN" \
  --preferences "$PREFERENCES" --format argv0
```

The governed wrapper then runs the leased installed `resolve-voice-plan` gate
before it narrates. Require success. Echo alone decides block existence,
speakability, range expansion, resolved identity, canonical plan bytes, and the
five-field resolution receipt (`blockCount`, `defaultVoice`,
`sourceEPUBSHA256`, `voicePlanID`, and `voicePlanSHA256`). A local plan is
never an operational identity until that resolution succeeds.

Forward the validator's NUL-delimited result without shell interpretation or lossy
reconstruction. `validate-cast` accepts `VOICE_PLAN` only when it is the
canonical absolute authored-plan path. Use this status-preserving private
scratch handoff immediately before every block-mode wrapper invocation; it
never exports voice state:

```bash
load_fiction_voice_arguments() {
  local argv0 status token
  argv0=$(mktemp "${TMPDIR:-/tmp}/echo-fiction-voice-arguments.XXXXXX") || return $?
  trap 'rm -f -- "$argv0"' RETURN

  if /usr/local/bin/python3 \
    skills/fiction-audiobook/scripts/fiction_voice_preferences.py \
    validate-cast --cast "$VOICE_CAST" --voice-plan "$VOICE_PLAN" \
    --preferences "$PREFERENCES" --format argv0 >"$argv0"; then
    :
  else
    status=$?
    return "$status"
  fi

  VOICE_ARGUMENTS=()
  while IFS= read -r -d '' token; do
    VOICE_ARGUMENTS+=("$token")
  done <"$argv0"

  if [[ ${#VOICE_ARGUMENTS[@]} -ne 2 ||
        "${VOICE_ARGUMENTS[0]}" != "--voice-plan" ||
        "${VOICE_ARGUMENTS[1]}" != "$VOICE_PLAN" ]]; then
    printf '%s\n' 'fiction block voice handoff must be --voice-plan plus the canonical authored plan' >&2
    return 64
  fi
}

load_fiction_voice_arguments || exit $?
"$NARRATION_SCRIPT" "${VOICE_ARGUMENTS[@]}"
```

For block mode, do not export `VOICE`; the wrapper resolves the default from
the sealed plan. Revalidate the identical token vector before a resume, then
pass it with the canonical resume-state path:

The `load_fiction_voice_arguments` calls below are the fiction form of the
shared commands. For nonfiction, call `load_semantic_voice_arguments` at the
same positions and pass its resulting `VOICE_ARGUMENTS` unchanged; do not
substitute a bare wrapper call.

```bash
load_fiction_voice_arguments || exit $?
"$NARRATION_SCRIPT" "${VOICE_ARGUMENTS[@]}" \
  --resume --resume-state "$RUN_ROOT/research/echo-resume-state-$RUN_ID.json"
```

If the resolved identity changes, start a new run. Never copy captures,
receipts, a work directory, database, or resume state into it.

### Block-mode resume and partial renders

These commands apply only to a source-bound `--voice-plan` render. Keep the exact
validated argv0 vector on every invocation; a bare resume or partial command
silently drops the authored plan. For an accepted partial attempt, read the
canonical resume-state path for its current `RUN_ID`, revalidate the vector,
then use:

```bash
load_fiction_voice_arguments || exit $?
"$NARRATION_SCRIPT" "${VOICE_ARGUMENTS[@]}" \
  --resume --resume-state "$RUN_ROOT/research/echo-resume-state-$RUN_ID.json"
```

For a deliberately one-block/chapter probe, preserve that same vector on both
the first partial call and its continuation:

```bash
load_fiction_voice_arguments || exit $?
set +e
"$NARRATION_SCRIPT" "${VOICE_ARGUMENTS[@]}" --max-chapters 1
rc=$?
set -e
[[ "$rc" == 2 ]]

load_fiction_voice_arguments || exit $?
set +e
"$NARRATION_SCRIPT" "${VOICE_ARGUMENTS[@]}" \
  --resume --resume-state "$RUN_ROOT/research/echo-resume-state-$RUN_ID.json" \
  --max-chapters 1
rc=$?
set -e
[[ "$rc" == 2 ]]
```

If a plan edit resolves to a different identity, do not resume: let the
wrapper create the new run and retain the earlier chain without reusing any
captures or state.

### Block-mode evidence

For a completed block run, require schema-2 captures, a schema-4 success
receipt, and a schema-7 pronunciation audit tied to the same resolved plan.
Keep captures and the pronunciation reel under private
`_production/narration/` evidence; they are never title-root media or public
package files. A completed selector resolves one M4B and one delivered
alignment sidecar. Automated block/audit checks do not complete human reading
or listening.

## Chapter-mode resuming and partial renders

This entire section is for the default/chapter-voice procedure only.
Source-bound block renders use the preceding argv0-vector commands and never borrow the
bare examples below.

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

### Block-mode verification

For a completed source-bound block run, derive the mode, sealed internal reel path,
resolved-plan SHA-256, and block count from the accepted schema-4 success/input
receipt chain. They are not shell variables exported by the wrapper's child
process. The state reader below rejects a non-current selector, a non-block
success receipt, duplicate/altered receipt JSON, mismatched input bytes, or
plan evidence that does not bind the input receipt.

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
INPUT_RECEIPT="$RUN_ROOT/research/$INPUT_RECEIPT_NAME"
SUCCESS_RECEIPT="$RUN_ROOT/research/$SUCCESS_RECEIPT_NAME"
STATE_RECEIPT="$RUN_ROOT/research/$STATE_RECEIPT_NAME"

BLOCK_EVIDENCE=$(mktemp /tmp/echo-block-delivery.XXXXXX)
trap 'rm -f -- "$BLOCK_EVIDENCE"' EXIT
/usr/local/bin/python3 "$STATE_HELPER" \
  block-delivery-evidence \
  --attempt "$ATTEMPT_RECEIPT" \
  --selector "$CURRENT_SELECTOR" \
  --receipt "$SUCCESS_RECEIPT" \
  --input-receipt "$INPUT_RECEIPT" \
  --format env0 >"$BLOCK_EVIDENCE"

VOICE_PLAN_MODE= REEL_RELATIVE_PATH= VOICE_PLAN_SHA256=
VOICE_PLAN_BLOCK_COUNT= SEALED_VOICE=
mode_count=0 reel_count=0 sha_count=0 count_count=0 voice_count=0
while IFS='=' read -r -d '' key value; do
  case "$key" in
    voice_plan_mode) VOICE_PLAN_MODE=$value; (( mode_count += 1 )) ;;
    reel_relative_path) REEL_RELATIVE_PATH=$value; (( reel_count += 1 )) ;;
    voice_plan_sha256) VOICE_PLAN_SHA256=$value; (( sha_count += 1 )) ;;
    voice_plan_block_count) VOICE_PLAN_BLOCK_COUNT=$value; (( count_count += 1 )) ;;
    voice) SEALED_VOICE=$value; (( voice_count += 1 )) ;;
    *) printf 'unknown block delivery evidence key: %s\n' "$key" >&2; exit 65 ;;
  esac
done <"$BLOCK_EVIDENCE"
rm -f -- "$BLOCK_EVIDENCE"
trap - EXIT
[[ $mode_count == 1 && $reel_count == 1 && $sha_count == 1 ]]
[[ $count_count == 1 && $voice_count == 1 && $VOICE_PLAN_MODE == block ]]
[[ "$VOICE_PLAN_BLOCK_COUNT" =~ ^[1-9][0-9]*$ ]]
ARTIFACT_ROOT="$DIST/$ARTIFACT_RELATIVE_PATH"
AUDIOBOOK="$ARTIFACT_ROOT/$SLUG.m4b"
SIDECAR="$ARTIFACT_ROOT/$SLUG.alignment.json"
AUDIT="$ARTIFACT_ROOT/$SLUG.pronunciation-audit.json"
REEL="$RUN_ROOT/research/$REEL_RELATIVE_PATH"

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
"$CLI" verify-sidecar \
  --epub "$DIST/$SLUG.epub" \
  --audio "$AUDIOBOOK" \
  --sidecar "$SIDECAR"

/usr/local/bin/python3 "$EXPLAINER_ROOT/skills/echo-narration/scripts/validate_pronunciation_audit.py" \
  "$AUDIT" \
  --audiobook "$AUDIOBOOK" \
  --reel "$REEL" \
  --voice-plan-sha256 "$VOICE_PLAN_SHA256" \
  --block-count "$VOICE_PLAN_BLOCK_COUNT"
```

Require `SIDECAR_OK` and `pronunciation_audit: clean` before `record-use`.
The block reader owns the meaning of `SEALED_VOICE`; do not export or replace
it with a caller-controlled `VOICE`.

### Chapter-mode verification

The following default/chapter-voice procedure is chapter mode only. Do not use
it for a source-bound `--voice-plan` render; use the receipt-derived block
procedure above instead. After a chapter-mode render completes, resolve the
accepted artifacts from the current selector, then verify them before treating
the render as done:

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
schema version is `6`; schemas `2` through `5` remain accepted for earlier
governed renders. Require `coverage=complete`, render version 12 or newer, a
known Echo English voice or `mixed`, complete valid `chapterVoices` provenance
for schemas `3` through `6`, schema-valid decision objects and timing ranges,
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
