#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
# Resolved from this script's absolute directory.
# shellcheck disable=SC1091
source "$SCRIPT_DIR/echo_pronunciation_preflight.sh"

usage() {
  printf '%s\n' \
    'usage: echo_learning_pilot_narrate.sh [--resume --resume-state ABSOLUTE_PATH]' >&2
}

RESUME=0
RESUME_STATE=
INTERNAL_MODE=
while (( $# )); do
  case "$1" in
    --resume)
      RESUME=1
      ;;
    --resume-state)
      if [[ -n "$RESUME_STATE" || -z ${2:-} ]]; then
        printf '%s\n' '--resume-state requires one absolute path' >&2
        usage
        exit 64
      fi
      RESUME_STATE=$2
      shift
      ;;
    --leased-preflight)
      INTERNAL_MODE=preflight
      ;;
    --leased-run)
      INTERNAL_MODE=run
      ;;
    -h | --help)
      usage
      exit 0
      ;;
    *)
      usage
      exit 64
      ;;
  esac
  shift
done
if (( RESUME )) && [[ -z "$RESUME_STATE" ]]; then
  printf '%s\n' '--resume requires --resume-state ABSOLUTE_PATH' >&2
  usage
  exit 64
fi
if [[ -n "$RESUME_STATE" && $RESUME -eq 0 ]]; then
  printf '%s\n' '--resume-state requires --resume' >&2
  usage
  exit 64
fi
if [[ -n "$RESUME_STATE" && "$RESUME_STATE" != /* ]]; then
  printf '%s\n' '--resume-state must be an absolute path' >&2
  usage
  exit 64
fi
if (( RESUME )); then
  canonical_explainer_root=$(cd -- "${EXPLAINER_ROOT:-$SCRIPT_DIR/../../..}" && pwd -P)
  canonical_resume_root="$canonical_explainer_root/.build/custom-learning-audiobooks/${SLUG:-}/pilot/research"
  resume_filename=${RESUME_STATE#"$canonical_resume_root/"}
  if [[ -z ${SLUG:-} || "$RESUME_STATE" == "$resume_filename" \
    || ! "$resume_filename" =~ ^echo-resume-state-[a-z0-9_-]+\.json$ \
    || -L "$RESUME_STATE" || ! -f "$RESUME_STATE" ]]; then
    printf 'resume state must be the canonical pilot receipt under: %s\n' \
      "$canonical_resume_root" >&2
    exit 64
  fi
fi

ECHO_PRONUNCIATION_LEASE_ROOT=$(echo_pronunciation_canonical_lease_root) \
  || exit $?
export ECHO_PRONUNCIATION_LEASE_ROOT

if [[ -z "$INTERNAL_MODE" ]]; then
  echo_pronunciation_resolve_installed_renderer "$RESUME" "$RESUME_STATE" \
    || exit $?
  lease_command=(
    "$SCRIPT_DIR/echo_pronunciation_lease.py"
    --lock-root "$ECHO_PRONUNCIATION_LEASE_ROOT"
    --resource "$ECHO_RENDERER_BUILD_ROOT"
    --
    "$0"
    --leased-preflight
  )
  if (( RESUME )); then
    lease_command+=(--resume --resume-state "$RESUME_STATE")
  fi
  exec "${lease_command[@]}"
fi

pilot_receipt_text() {
  printf '%s\n' \
    'schema=2' \
    'kind=learning-pilot-nonpackage'
  echo_pronunciation_renderer_receipt_text
  printf '%s\n' \
    "epub_path=$EPUB" \
    "epub_sha256=$EPUB_SHA256" \
    "title=$TITLE" \
    "pilot_input_sha256=$PILOT_INPUT_SHA256" \
    "run_id=$RUN_ID" \
    "work_dir=$WORK" \
    "narration_db=$DB"
}

pilot_preflight() {
  local original_pwd=$PWD
  local explainer_root=${EXPLAINER_ROOT:-$(cd -- "$SCRIPT_DIR/../../.." && pwd -P)}

  echo_pronunciation_assert_leases "$ECHO_RENDERER_BUILD_ROOT"
  echo_pronunciation_renderer_required || return $?
  echo_pronunciation_validate_renderer_paths || return $?
  echo_pronunciation_attest_renderer || return $?
  require_renderer_commit_sha APPROVED_ECHO_PRONUNCIATION_SHA \
    "${APPROVED_ECHO_PRONUNCIATION_SHA:-}" || return $?
  if [[ "$APPROVED_ECHO_PRONUNCIATION_SHA" != "$ECHO_SOURCE_SHA" ]]; then
    printf 'approved Echo pronunciation revision %s must exactly equal installed source %s\n' \
      "$APPROVED_ECHO_PRONUNCIATION_SHA" "$ECHO_SOURCE_SHA" >&2
    return 65
  fi
  explainer_root=$(cd -- "$explainer_root" 2>/dev/null && pwd -P) || {
    printf 'cannot resolve explainer-audiobooks repository: %s\n' \
      "$explainer_root" >&2
    return 66
  }
  if [[ ! ${SLUG:-} =~ ^[a-z0-9][a-z0-9-]*$ || "$SLUG" == *-pilot ]]; then
    printf 'SLUG must be the lowercase base-book slug without a -pilot suffix\n' >&2
    return 64
  fi
  if [[ -z ${RUN_ROOT:-} || "$RUN_ROOT" != /* ]]; then
    printf 'RUN_ROOT must be the absolute canonical base-book run path\n' >&2
    return 64
  fi
  local canonical_run_root expected_run_root governed_path
  canonical_run_root=$(cd -- "$RUN_ROOT" 2>/dev/null && pwd -P) \
    || canonical_run_root=
  expected_run_root="$explainer_root/.build/custom-learning-audiobooks/$SLUG"
  if [[ "$canonical_run_root" != "$expected_run_root" ]]; then
    printf 'RUN_ROOT must equal the canonical run path: %s\n' \
      "$expected_run_root" >&2
    return 64
  fi
  RUN_ROOT=$canonical_run_root
  PILOT_SLUG="$SLUG-pilot"
  PILOT_ROOT="$RUN_ROOT/pilot"
  PILOT_DIST="$PILOT_ROOT/dist"
  PILOT_RESEARCH="$PILOT_ROOT/research"
  EPUB="$PILOT_DIST/$PILOT_SLUG.epub"
  for governed_path in \
    "$RUN_ROOT" "$PILOT_ROOT" "$PILOT_DIST" "$EPUB"; do
    if [[ -L "$governed_path" ]]; then
      printf 'governed pilot path must not be a symlink: %s\n' \
        "$governed_path" >&2
      return 65
    fi
  done
  if [[ ! -d "$PILOT_DIST" || ! -f "$EPUB" ]]; then
    printf 'learning-pilot EPUB is missing: %s\n' "$EPUB" >&2
    return 66
  fi
  if [[ -z ${TITLE:-} || "$TITLE" == *$'\n'* || "$TITLE" == *$'\r'* ]]; then
    printf 'TITLE must be nonempty and single-line\n' >&2
    return 64
  fi
  VOICE=${VOICE:-am_michael}
  case "$VOICE" in
    am_michael | am_puck) ;;
    *)
      printf 'VOICE must be am_michael or am_puck, got: %s\n' "$VOICE" >&2
      return 64
      ;;
  esac

  EPUB_SHA256=$(/usr/bin/shasum -a 256 "$EPUB" | awk '{print $1}')
  require_sha256 EPUB_SHA256 "$EPUB_SHA256"
  local echo_source_id
  echo_source_id=$(echo_pronunciation_source_id "$ECHO_SOURCE_SHA")
  RUN_ID=$(echo_pronunciation_run_id \
    "$EPUB_SHA256" "$ECHO_CLI_SHA256" "$ECHO_RESOURCES_SHA256" \
    "$ECHO_RENDERER_MANIFEST_SHA256" "$echo_source_id" "$VOICE")
  PILOT_INPUT_SHA256=$(printf '%s\n' \
    "run_id=$RUN_ID" \
    "title=$TITLE" \
    | /usr/bin/shasum -a 256 | awk '{print $1}')
  require_sha256 PILOT_INPUT_SHA256 "$PILOT_INPUT_SHA256"

  WORK="$PILOT_ROOT/audio-work-$RUN_ID"
  DB="$PILOT_ROOT/narration-$RUN_ID.sqlite"
  OUTPUT="$PILOT_DIST/$PILOT_SLUG.m4b"
  SIDECAR="$PILOT_DIST/$PILOT_SLUG.alignment.json"
  AUDIT="$PILOT_DIST/$PILOT_SLUG.pronunciation-audit.json"
  REEL="$PILOT_DIST/$PILOT_SLUG.pronunciation-reel.m4b"
  mkdir -p -- "$PILOT_RESEARCH"
  if [[ -L "$PILOT_RESEARCH" || ! -d "$PILOT_RESEARCH" ]]; then
    printf 'pilot research path is unsafe: %s\n' "$PILOT_RESEARCH" >&2
    return 65
  fi
  INPUT_RECEIPT="$PILOT_RESEARCH/echo-pilot-inputs-$RUN_ID.env"
  STATE_RECEIPT="$PILOT_RESEARCH/echo-resume-state-$RUN_ID.json"
  ATTEMPT_ID=$(/usr/local/bin/python3 -c 'import secrets; print(secrets.token_hex(32))')
  SUCCESS_RECEIPT="$PILOT_RESEARCH/echo-pilot-success-$ATTEMPT_ID.env"
  local governed_output
  for governed_output in \
    "$WORK" "$DB" "$OUTPUT" "$SIDECAR" "$AUDIT" "$REEL" \
    "$INPUT_RECEIPT" "$STATE_RECEIPT" "$SUCCESS_RECEIPT"; do
    if [[ -L "$governed_output" ]]; then
      printf 'governed pilot output must not be a symlink: %s\n' \
        "$governed_output" >&2
      return 65
    fi
  done

  local receipt_text
  receipt_text=$(pilot_receipt_text)
  if [[ -e "$INPUT_RECEIPT" ]]; then
    if [[ "$(<"$INPUT_RECEIPT")" != "$receipt_text" ]]; then
      printf 'existing pilot-input receipt does not match immutable inputs: %s\n' \
        "$INPUT_RECEIPT" >&2
      return 65
    fi
  else
    if (( RESUME )) || [[ -e "$WORK" || -e "$DB" || -e "$STATE_RECEIPT" ]]; then
      printf 'pre-existing pilot state requires a matching input receipt\n' >&2
      return 65
    fi
    if ! printf '%s\n' "$receipt_text" \
      | /usr/local/bin/python3 "$SCRIPT_DIR/echo_pronunciation_state.py" \
        immutable-file "$INPUT_RECEIPT"; then
      printf 'could not create immutable pilot-input receipt: %s\n' \
        "$INPUT_RECEIPT" >&2
      return 65
    fi
  fi
  if (( RESUME )) && [[ "$RESUME_STATE" != "$STATE_RECEIPT" ]]; then
    printf 'resume state must be the canonical current-pilot receipt: %s\n' \
      "$STATE_RECEIPT" >&2
    return 64
  fi
  if [[ "$PWD" != "$original_pwd" ]]; then
    printf 'pilot preflight changed cwd from %s to %s\n' \
      "$original_pwd" "$PWD" >&2
    return 70
  fi

  EXPLAINER_ROOT=$explainer_root
  export EXPLAINER_ROOT RUN_ROOT SLUG TITLE VOICE
  export PILOT_SLUG PILOT_ROOT PILOT_DIST PILOT_RESEARCH
  export APPROVED_ECHO_PRONUNCIATION_SHA ECHO_SOURCE_SHA
  export ECHO_RENDERER_ROOT ECHO_RENDERER_BUILD_ROOT ECHO_RENDERER_MANIFEST
  export ECHO_RENDERER_MANIFEST_SHA256 APPROVED_ECHO_INSTALLER_SHA
  export EPUB EPUB_SHA256 CLI ECHO_CLI_SHA256
  export ECHO_RESOURCE_DIR ECHO_RESOURCES_SHA256 ECHO_RENDER_VERSION
  export ECHO_MODEL_REVISION ECHO_MODEL_EXPECTED_BYTES ECHO_MODEL_BYTES_ATTESTED
  export PILOT_INPUT_SHA256 RUN_ID ATTEMPT_ID WORK DB OUTPUT SIDECAR AUDIT REEL
  export INPUT_RECEIPT STATE_RECEIPT SUCCESS_RECEIPT
}

pilot_attest_inputs() {
  local required
  for required in \
    EXPLAINER_ROOT RUN_ROOT SLUG TITLE VOICE \
    PILOT_SLUG PILOT_ROOT PILOT_DIST PILOT_RESEARCH \
    APPROVED_ECHO_PRONUNCIATION_SHA ECHO_SOURCE_SHA \
    ECHO_RENDERER_ROOT ECHO_RENDERER_BUILD_ROOT ECHO_RENDERER_MANIFEST \
    ECHO_RENDERER_MANIFEST_SHA256 APPROVED_ECHO_INSTALLER_SHA \
    EPUB EPUB_SHA256 CLI ECHO_CLI_SHA256 ECHO_RESOURCE_DIR \
    ECHO_RESOURCES_SHA256 ECHO_RENDER_VERSION ECHO_MODEL_REVISION \
    ECHO_MODEL_EXPECTED_BYTES ECHO_MODEL_BYTES_ATTESTED PILOT_INPUT_SHA256 \
    RUN_ID ATTEMPT_ID WORK DB OUTPUT SIDECAR AUDIT REEL \
    INPUT_RECEIPT STATE_RECEIPT SUCCESS_RECEIPT; do
    if [[ -z ${!required:-} || ${!required} == *$'\n'* \
      || ${!required} == *$'\r'* ]]; then
      printf 'sealed pilot preflight state is missing or unsafe: %s\n' \
        "$required" >&2
      return 70
    fi
  done
  echo_pronunciation_renderer_required || return $?
  echo_pronunciation_validate_renderer_paths || return $?
  require_renderer_commit_sha APPROVED_ECHO_PRONUNCIATION_SHA \
    "$APPROVED_ECHO_PRONUNCIATION_SHA" || return $?
  require_renderer_commit_sha ECHO_SOURCE_SHA "$ECHO_SOURCE_SHA" || return $?
  require_sha256 EPUB_SHA256 "$EPUB_SHA256" || return $?
  require_sha256 ECHO_CLI_SHA256 "$ECHO_CLI_SHA256" || return $?
  require_sha256 ECHO_RESOURCES_SHA256 "$ECHO_RESOURCES_SHA256" || return $?
  require_sha256 ECHO_RENDERER_MANIFEST_SHA256 \
    "$ECHO_RENDERER_MANIFEST_SHA256" || return $?
  require_sha256 PILOT_INPUT_SHA256 "$PILOT_INPUT_SHA256" || return $?
  if [[ ! "$ATTEMPT_ID" =~ ^[0-9a-f]{64}$ ]]; then
    printf 'sealed pilot attempt ID is invalid\n' >&2
    return 70
  fi
  echo_pronunciation_assert_leases \
    "$ECHO_RENDERER_BUILD_ROOT" "$WORK" "$DB" "$OUTPUT" "$SIDECAR" \
    "$AUDIT" "$REEL" "$INPUT_RECEIPT" "$STATE_RECEIPT" "$SUCCESS_RECEIPT"
  echo_pronunciation_attest_renderer || return $?

  local canonical_explainer canonical_run canonical_pilot governed_path
  canonical_explainer=$(cd -- "$EXPLAINER_ROOT" 2>/dev/null && pwd -P) \
    || canonical_explainer=
  canonical_run=$(cd -- "$RUN_ROOT" 2>/dev/null && pwd -P) || canonical_run=
  canonical_pilot=$(cd -- "$PILOT_ROOT" 2>/dev/null && pwd -P) || canonical_pilot=
  if [[ "$canonical_explainer" != "$EXPLAINER_ROOT" \
    || "$canonical_run" != "$EXPLAINER_ROOT/.build/custom-learning-audiobooks/$SLUG" \
    || "$canonical_pilot" != "$RUN_ROOT/pilot" \
    || "$PILOT_SLUG" != "$SLUG-pilot" \
    || "$PILOT_DIST" != "$PILOT_ROOT/dist" \
    || "$PILOT_RESEARCH" != "$PILOT_ROOT/research" \
    || "$EPUB" != "$PILOT_DIST/$PILOT_SLUG.epub" \
    || "$OUTPUT" != "$PILOT_DIST/$PILOT_SLUG.m4b" \
    || "$SIDECAR" != "$PILOT_DIST/$PILOT_SLUG.alignment.json" \
    || "$AUDIT" != "$PILOT_DIST/$PILOT_SLUG.pronunciation-audit.json" \
    || "$REEL" != "$PILOT_DIST/$PILOT_SLUG.pronunciation-reel.m4b" ]]; then
    printf 'sealed pilot paths are not canonically derived\n' >&2
    return 65
  fi
  for governed_path in \
    "$RUN_ROOT" "$PILOT_ROOT" "$PILOT_DIST" "$PILOT_RESEARCH" \
    "$EPUB" "$CLI" "$ECHO_RESOURCE_DIR" "$INPUT_RECEIPT" \
    "$OUTPUT" "$SIDECAR" "$AUDIT" "$REEL"; do
    if [[ -L "$governed_path" ]]; then
      printf 'governed pilot path became a symlink: %s\n' "$governed_path" >&2
      return 65
    fi
  done
  if [[ "$APPROVED_ECHO_PRONUNCIATION_SHA" != "$ECHO_SOURCE_SHA" ]]; then
    printf 'approved Echo pronunciation revision does not match installed source\n' >&2
    return 65
  fi
  case "$VOICE" in
    am_michael | am_puck) ;;
    *)
      printf 'sealed pilot voice is unsupported: %s\n' "$VOICE" >&2
      return 64
      ;;
  esac
  local current_epub_sha expected_source_id expected_run_id expected_input_sha
  current_epub_sha=$(/usr/bin/shasum -a 256 "$EPUB" | awk '{print $1}')
  expected_source_id=$(echo_pronunciation_source_id "$ECHO_SOURCE_SHA")
  expected_run_id=$(echo_pronunciation_run_id \
    "$EPUB_SHA256" "$ECHO_CLI_SHA256" "$ECHO_RESOURCES_SHA256" \
    "$ECHO_RENDERER_MANIFEST_SHA256" "$expected_source_id" "$VOICE")
  expected_input_sha=$(printf '%s\n' \
    "run_id=$expected_run_id" \
    "title=$TITLE" \
    | /usr/bin/shasum -a 256 | awk '{print $1}')
  if [[ "$current_epub_sha" != "$EPUB_SHA256" ]]; then
    printf 'pilot EPUB changed while leases were held\n' >&2
    return 65
  fi
  if [[ "$RUN_ID" != "$expected_run_id" \
    || "$PILOT_INPUT_SHA256" != "$expected_input_sha" \
    || "$WORK" != "$PILOT_ROOT/audio-work-$RUN_ID" \
    || "$DB" != "$PILOT_ROOT/narration-$RUN_ID.sqlite" \
    || "$INPUT_RECEIPT" != "$PILOT_RESEARCH/echo-pilot-inputs-$RUN_ID.env" \
    || "$STATE_RECEIPT" != "$PILOT_RESEARCH/echo-resume-state-$RUN_ID.json" \
    || "$SUCCESS_RECEIPT" != "$PILOT_RESEARCH/echo-pilot-success-$ATTEMPT_ID.env" ]]; then
    printf 'sealed pilot run paths are not derived from attested inputs\n' >&2
    return 65
  fi
  if [[ ! -f "$INPUT_RECEIPT" \
    || $(/usr/bin/stat -f '%Lp' "$INPUT_RECEIPT") != 600 ]]; then
    printf 'pilot-input receipt is missing or has an unsafe mode\n' >&2
    return 65
  fi
  if [[ "$(<"$INPUT_RECEIPT")" != "$(pilot_receipt_text)" ]]; then
    printf 'pilot-input receipt changed while leases were held\n' >&2
    return 65
  fi
}

if [[ "$INTERNAL_MODE" == preflight ]]; then
  pilot_preflight
  if (( RESUME )) && [[ "$RESUME_STATE" != "$STATE_RECEIPT" ]]; then
    printf 'internal resume state is not the canonical current-pilot receipt\n' >&2
    exit 70
  fi
  lease_command=(
    "$SCRIPT_DIR/echo_pronunciation_lease.py"
    --lock-root "$ECHO_PRONUNCIATION_LEASE_ROOT"
    --resource "$WORK"
    --resource "$DB"
    --resource "$OUTPUT"
    --resource "$SIDECAR"
    --resource "$AUDIT"
    --resource "$REEL"
    --resource "$INPUT_RECEIPT"
    --resource "$STATE_RECEIPT"
    --resource "$SUCCESS_RECEIPT"
    --
    "$0"
    --leased-run
  )
  if (( RESUME )); then
    lease_command+=(--resume --resume-state "$RESUME_STATE")
  fi
  exec "${lease_command[@]}"
fi

pilot_attest_inputs

renderer_state_arguments=(
  --renderer-schema-version 1
  --renderer-root "$ECHO_RENDERER_ROOT"
  --renderer-build-root "$ECHO_RENDERER_BUILD_ROOT"
  --installer-source-sha "$APPROVED_ECHO_INSTALLER_SHA"
  --echo-source-sha "$ECHO_SOURCE_SHA"
  --renderer-manifest-sha256 "$ECHO_RENDERER_MANIFEST_SHA256"
  --echo-cli-sha256 "$ECHO_CLI_SHA256"
  --echo-resources-sha256 "$ECHO_RESOURCES_SHA256"
  --echo-render-version "$ECHO_RENDER_VERSION"
  --model-policy-revision "$ECHO_MODEL_REVISION"
  --model-expected-byte-count "$ECHO_MODEL_EXPECTED_BYTES"
  --model-bytes-attested "$ECHO_MODEL_BYTES_ATTESTED"
)
state_command=(
  "${renderer_state_arguments[@]}"
  --work "$WORK"
  --db "$DB"
  --receipt "$STATE_RECEIPT"
  --epub "$EPUB"
  --source-sha "$ECHO_SOURCE_SHA"
  --voice "$VOICE"
  --render-version "$ECHO_RENDER_VERSION"
  --input-receipt "$INPUT_RECEIPT"
  --lock-root "$ECHO_PRONUNCIATION_LEASE_ROOT"
)
if (( RESUME )); then
  if ! /usr/local/bin/python3 "$SCRIPT_DIR/echo_pronunciation_state.py" \
    verify-state "${state_command[@]}"; then
    printf 'pilot resume state is not bound to the current capture set\n' >&2
    exit 65
  fi
else
  /usr/local/bin/python3 "$SCRIPT_DIR/echo_pronunciation_state.py" \
    reset-state --work "$WORK" --db "$DB" --receipt "$STATE_RECEIPT" \
    --lock-root "$ECHO_PRONUNCIATION_LEASE_ROOT"
fi

STAGE=
NARRATE_PID=
cleanup() {
  if [[ -n "$STAGE" && -d "$STAGE" && ! -L "$STAGE" ]]; then
    rm -rf -- "$STAGE"
  fi
}
# Invoked by signal traps.
# shellcheck disable=SC2329
handle_signal() {
  local signal_name=${1:?signal name is required}
  local exit_status=${2:?exit status is required}
  if [[ -n "$NARRATE_PID" ]] && kill -0 "$NARRATE_PID" 2>/dev/null; then
    kill -"$signal_name" "$NARRATE_PID" 2>/dev/null || true
    wait "$NARRATE_PID" 2>/dev/null || true
  fi
  exit "$exit_status"
}
trap cleanup EXIT
trap 'handle_signal HUP 129' HUP
trap 'handle_signal INT 130' INT
trap 'handle_signal TERM 143' TERM

STAGE=$(mktemp -d "$PILOT_ROOT/.echo-pilot-output-$ATTEMPT_ID.XXXXXX")
STAGE_OUTPUT="$STAGE/$PILOT_SLUG.m4b"
STAGE_SIDECAR="$STAGE/$PILOT_SLUG.alignment.json"
STAGE_AUDIT="$STAGE/$PILOT_SLUG.pronunciation-audit.json"
STAGE_REEL="$STAGE/$PILOT_SLUG.pronunciation-reel.m4b"
narrate_command=(
  /usr/bin/env "ECHO_RESOURCE_DIR=$ECHO_RESOURCE_DIR"
  "$CLI" narrate
  --epub "$EPUB"
  --out "$STAGE_OUTPUT"
  --sidecar "$STAGE_SIDECAR"
  --voice "$VOICE"
  --title "$TITLE"
  --author "Dan Fakkeldy"
  --work-dir "$WORK"
  --db "$DB"
  --jobs 1
  --threads 2
)
if (( RESUME )); then
  narrate_command+=(--resume)
fi
pilot_attest_inputs
"${narrate_command[@]}" &
NARRATE_PID=$!
set +e
wait "$NARRATE_PID"
narrate_status=$?
set -e
NARRATE_PID=
pilot_attest_inputs
if [[ -d "$WORK" && -f "$DB" ]] \
  && compgen -G "$WORK/.anchors-ch*.json" >/dev/null; then
  /usr/local/bin/python3 "$SCRIPT_DIR/echo_pronunciation_state.py" \
    record-state "${state_command[@]}"
fi
if (( narrate_status != 0 )); then
  exit "$narrate_status"
fi
if [[ ! -f "$STATE_RECEIPT" || -L "$STATE_RECEIPT" ]]; then
  printf 'successful pilot narration did not produce sealed capture state\n' >&2
  exit 65
fi
for required_output in "$STAGE_OUTPUT" "$STAGE_SIDECAR" "$STAGE_AUDIT"; do
  if [[ -L "$required_output" || ! -f "$required_output" ]]; then
    printf 'successful pilot narration did not produce required output: %s\n' \
      "$required_output" >&2
    exit 65
  fi
done
if [[ ! -s "$STAGE_OUTPUT" ]]; then
  printf 'successful pilot narration produced an empty audiobook\n' >&2
  exit 65
fi
ECHO_RESOURCE_DIR="$ECHO_RESOURCE_DIR" "$CLI" verify-sidecar \
  --epub "$EPUB" \
  --audio "$STAGE_OUTPUT" \
  --sidecar "$STAGE_SIDECAR"
"$SCRIPT_DIR/validate_pronunciation_audit.py" "$STAGE_AUDIT"
pilot_attest_inputs

for final_output in "$OUTPUT" "$SIDECAR" "$AUDIT" "$REEL"; do
  if [[ -L "$final_output" ]]; then
    printf 'final pilot output must not be a symlink: %s\n' "$final_output" >&2
    exit 65
  fi
done
mv -f -- "$STAGE_OUTPUT" "$OUTPUT"
mv -f -- "$STAGE_SIDECAR" "$SIDECAR"
mv -f -- "$STAGE_AUDIT" "$AUDIT"
if [[ -e "$STAGE_REEL" || -L "$STAGE_REEL" ]]; then
  if [[ -L "$STAGE_REEL" || ! -f "$STAGE_REEL" ]]; then
    printf 'staged pronunciation reel is unsafe: %s\n' "$STAGE_REEL" >&2
    exit 65
  fi
  mv -f -- "$STAGE_REEL" "$REEL"
else
  rm -f -- "$REEL"
fi
ECHO_RESOURCE_DIR="$ECHO_RESOURCE_DIR" "$CLI" verify-sidecar \
  --epub "$EPUB" \
  --audio "$OUTPUT" \
  --sidecar "$SIDECAR"
"$SCRIPT_DIR/validate_pronunciation_audit.py" "$AUDIT"
pilot_attest_inputs
/usr/local/bin/python3 "$SCRIPT_DIR/echo_pronunciation_state.py" \
  verify-state "${state_command[@]}"

AUDIO_SHA256=$(/usr/bin/shasum -a 256 "$OUTPUT" | awk '{print $1}')
SIDECAR_SHA256=$(/usr/bin/shasum -a 256 "$SIDECAR" | awk '{print $1}')
AUDIT_SHA256=$(/usr/bin/shasum -a 256 "$AUDIT" | awk '{print $1}')
INPUT_RECEIPT_SHA256=$(/usr/bin/shasum -a 256 "$INPUT_RECEIPT" | awk '{print $1}')
STATE_RECEIPT_SHA256=$(/usr/bin/shasum -a 256 "$STATE_RECEIPT" | awk '{print $1}')
require_sha256 AUDIO_SHA256 "$AUDIO_SHA256"
require_sha256 SIDECAR_SHA256 "$SIDECAR_SHA256"
require_sha256 AUDIT_SHA256 "$AUDIT_SHA256"
require_sha256 INPUT_RECEIPT_SHA256 "$INPUT_RECEIPT_SHA256"
require_sha256 STATE_RECEIPT_SHA256 "$STATE_RECEIPT_SHA256"
REEL_PATH=
REEL_SHA256=
if [[ -f "$REEL" && ! -L "$REEL" ]]; then
  REEL_PATH=$REEL
  REEL_SHA256=$(/usr/bin/shasum -a 256 "$REEL" | awk '{print $1}')
  require_sha256 REEL_SHA256 "$REEL_SHA256"
fi
success_text=$(
  printf '%s\n' \
    'schema=2' \
    'kind=learning-pilot-nonpackage' \
    'listener_acceptance=pending'
  echo_pronunciation_renderer_receipt_text
  printf '%s\n' \
    "attempt_id=$ATTEMPT_ID" \
    "run_id=$RUN_ID" \
    "pilot_input_sha256=$PILOT_INPUT_SHA256" \
    "input_receipt_path=$INPUT_RECEIPT" \
    "input_receipt_sha256=$INPUT_RECEIPT_SHA256" \
    "state_receipt_path=$STATE_RECEIPT" \
    "state_receipt_sha256=$STATE_RECEIPT_SHA256" \
    "audio_path=$OUTPUT" \
    "audio_sha256=$AUDIO_SHA256" \
    "sidecar_path=$SIDECAR" \
    "sidecar_sha256=$SIDECAR_SHA256" \
    "audit_path=$AUDIT" \
    "audit_sha256=$AUDIT_SHA256" \
    "reel_path=$REEL_PATH" \
    "reel_sha256=$REEL_SHA256"
)
if ! printf '%s\n' "$success_text" \
  | /usr/local/bin/python3 "$SCRIPT_DIR/echo_pronunciation_state.py" \
    immutable-file "$SUCCESS_RECEIPT"; then
  printf 'could not create immutable pilot-success receipt: %s\n' \
    "$SUCCESS_RECEIPT" >&2
  exit 65
fi

printf '%s\n' \
  'echo_learning_pilot_narrate: complete' \
  "audio=$OUTPUT" \
  "audio_sha256=$AUDIO_SHA256" \
  "receipt=$SUCCESS_RECEIPT" \
  'listener_acceptance=pending'
