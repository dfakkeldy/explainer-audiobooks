#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
# Resolved from this script's absolute directory.
# shellcheck disable=SC1091
source "$SCRIPT_DIR/echo_pronunciation_preflight.sh"

usage() {
  printf '%s\n' \
    'usage: echo_pronunciation_narrate.sh [--resume | --recover-stale-lock]' >&2
}

RESUME=0
RECOVER_STALE_LOCK=0
INTERNAL_MODE=
while (( $# )); do
  case "$1" in
    --resume)
      RESUME=1
      ;;
    --recover-stale-lock)
      RECOVER_STALE_LOCK=1
      ;;
    --leased-run)
      INTERNAL_MODE=run
      ;;
    --leased-recover)
      INTERNAL_MODE=recover
      ;;
    --leased-preflight)
      INTERNAL_MODE=preflight
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
if (( RESUME && RECOVER_STALE_LOCK )) \
  || [[ "$INTERNAL_MODE" == recover && $RESUME == 1 ]]; then
  usage
  exit 64
fi

ECHO_PRONUNCIATION_LEASE_ROOT=${ECHO_PRONUNCIATION_LEASE_ROOT:-$HOME/.cache/explainer-audiobooks/echo-pronunciation-leases}
ECHO_REPO=${ECHO_REPO:-/Users/dfakkeldy/Developer/Echo}
BUILD_RESOURCE="$ECHO_REPO/.build/cli"
export ECHO_PRONUNCIATION_LEASE_ROOT ECHO_REPO BUILD_RESOURCE

assert_leases() {
  local resources=("$@")
  local command=(
    "$SCRIPT_DIR/echo_pronunciation_lease.py"
    --assert-held
    --lock-root "$ECHO_PRONUNCIATION_LEASE_ROOT"
  )
  local resource
  for resource in "${resources[@]}"; do
    command+=(--resource "$resource")
  done
  if ! "${command[@]}"; then
    printf 'internal narration mode requires an inherited FD-backed lease capability\n' >&2
    return 70
  fi
}

if [[ -z "$INTERNAL_MODE" ]]; then
  lease_command=(
    "$SCRIPT_DIR/echo_pronunciation_lease.py"
    --lock-root "$ECHO_PRONUNCIATION_LEASE_ROOT"
    --resource "$BUILD_RESOURCE"
    --
    "$0"
    --leased-preflight
  )
  if (( RECOVER_STALE_LOCK )); then
    lease_command+=(--recover-stale-lock)
  elif (( RESUME )); then
    lease_command+=(--resume)
  fi
  exec "${lease_command[@]}"
fi

if [[ "$INTERNAL_MODE" == preflight ]]; then
  assert_leases "$BUILD_RESOURCE"
  echo_pronunciation_preflight

  DIST="$RUN_ROOT/dist"
  OUTPUT="$DIST/$SLUG.m4b"
  SIDECAR="$DIST/$SLUG.alignment.json"
  AUDIT="$DIST/$SLUG.pronunciation-audit.json"
  REEL="$DIST/$SLUG.pronunciation-reel.m4b"
  OWNER_FILE="$RUN_ROOT/research/echo-render-output.owner.env"
  STATE_RECEIPT="$RUN_ROOT/research/echo-resume-state-$RUN_ID.json"
  SUCCESS_RECEIPT="$RUN_ROOT/research/echo-render-success-$RUN_ID.json"
  STAGE="$RUN_ROOT/.echo-output-$RUN_ID"
  TITLE=${TITLE:-}
  export RUN_ROOT SLUG TITLE DIST OUTPUT SIDECAR AUDIT REEL OWNER_FILE
  export STATE_RECEIPT SUCCESS_RECEIPT STAGE

  lease_command=(
    "$SCRIPT_DIR/echo_pronunciation_lease.py"
    --lock-root "$ECHO_PRONUNCIATION_LEASE_ROOT"
    --resource "$OUTPUT"
    --resource "$SIDECAR"
    --resource "$AUDIT"
    --resource "$REEL"
    --resource "$WORK"
    --resource "$DB"
    --
    "$0"
  )
  if (( RECOVER_STALE_LOCK )); then
    lease_command+=(--leased-recover)
  else
    if [[ -z "$TITLE" ]]; then
      printf 'TITLE is required\n' >&2
      exit 64
    fi
    lease_command+=(--leased-run)
    if (( RESUME )); then
      lease_command+=(--resume)
    fi
  fi
  exec "${lease_command[@]}"
fi

assert_leases "$BUILD_RESOURCE"
for required_internal_variable in OUTPUT SIDECAR AUDIT REEL WORK DB; do
  if [[ -z ${!required_internal_variable:-} ]]; then
    printf 'internal narration mode lacks sealed preflight state: %s\n' \
      "$required_internal_variable" >&2
    exit 70
  fi
done
assert_leases \
  "$BUILD_RESOURCE" "$OUTPUT" "$SIDECAR" "$AUDIT" "$REEL" "$WORK" "$DB"

LOCAL_HOST=$(/bin/hostname)
OWNER_CREATED=0
OWNER_TOKEN=
OWNER_PID=$BASHPID
NARRATE_PID=
LOCK_CLASSIFICATION=
STAGE_CREATED=0

process_start_for_pid() {
  local pid=${1:?pid is required}
  local process_start
  process_start=$(ps -p "$pid" -o lstart= 2>/dev/null || true)
  awk '{$1=$1; print}' <<<"$process_start"
}

owner_field() {
  local key=${1:?owner key is required}
  awk -F= -v key="$key" '
    $1 == key {
      sub(/^[^=]*=/, "")
      print
    }
  ' "$OWNER_FILE"
}

load_owner_metadata() {
  if [[ -L "$OWNER_FILE" || ! -f "$OWNER_FILE" ]]; then
    return 1
  fi

  local line_count
  line_count=$(wc -l <"$OWNER_FILE" | tr -d ' ')
  if [[ "$line_count" != 12 ]]; then
    return 1
  fi

  local key _value
  while IFS='=' read -r key _value; do
    case "$key" in
      lock_schema | owner_token | owner_pid | owner_host | owner_start | run_id | work_dir | narration_db | output_m4b | output_sidecar | output_audit | output_reel) ;;
      *) return 1 ;;
    esac
  done <"$OWNER_FILE"

  for key in lock_schema owner_token owner_pid owner_host owner_start run_id work_dir narration_db output_m4b output_sidecar output_audit output_reel; do
    if [[ $(awk -F= -v key="$key" '$1 == key { count += 1 } END { print count + 0 }' "$OWNER_FILE") != 1 ]]; then
      return 1
    fi
  done

  LOCK_SCHEMA=$(owner_field lock_schema)
  LOCK_OWNER_TOKEN=$(owner_field owner_token)
  LOCK_OWNER_PID=$(owner_field owner_pid)
  LOCK_OWNER_HOST=$(owner_field owner_host)
  LOCK_OWNER_START=$(owner_field owner_start)
  LOCK_RUN_ID=$(owner_field run_id)
  LOCK_WORK=$(owner_field work_dir)
  LOCK_DB=$(owner_field narration_db)
  LOCK_OUTPUT=$(owner_field output_m4b)
  LOCK_SIDECAR=$(owner_field output_sidecar)
  LOCK_AUDIT=$(owner_field output_audit)
  LOCK_REEL=$(owner_field output_reel)

  if [[ "$LOCK_SCHEMA" != 2 \
    || ! "$LOCK_OWNER_TOKEN" =~ ^[0-9a-f]{64}$ \
    || ! "$LOCK_OWNER_PID" =~ ^[1-9][0-9]*$ \
    || -z "$LOCK_OWNER_HOST" \
    || -z "$LOCK_OWNER_START" \
    || ! "$LOCK_RUN_ID" =~ ^[0-9a-f-]+-(am_michael|am_puck)$ \
    || "$LOCK_WORK" != "$RUN_ROOT/audio-work-$LOCK_RUN_ID" \
    || "$LOCK_DB" != "$RUN_ROOT/narration-$LOCK_RUN_ID.sqlite" \
    || "$LOCK_OUTPUT" != "$OUTPUT" \
    || "$LOCK_SIDECAR" != "$SIDECAR" \
    || "$LOCK_AUDIT" != "$AUDIT" \
    || "$LOCK_REEL" != "$REEL" ]]; then
    return 1
  fi
  LOCK_OWNER_FILE_SHA=$(shasum -a 256 "$OWNER_FILE" | awk '{print $1}')
  [[ "$LOCK_OWNER_FILE_SHA" =~ ^[0-9a-f]{64}$ ]]
}

classify_owner_metadata() {
  if ! load_owner_metadata; then
    LOCK_CLASSIFICATION=malformed
    return
  fi
  if [[ "$LOCK_OWNER_HOST" != "$LOCAL_HOST" ]]; then
    LOCK_CLASSIFICATION=remote
    return
  fi
  if kill -0 "$LOCK_OWNER_PID" 2>/dev/null; then
    local current_start
    current_start=$(process_start_for_pid "$LOCK_OWNER_PID")
    if [[ -z "$current_start" || "$current_start" == "$LOCK_OWNER_START" ]]; then
      LOCK_CLASSIFICATION=active
      return
    fi
  fi
  LOCK_CLASSIFICATION=stale
}

remove_unchanged_stale_owner() {
  local current_sha
  current_sha=$(shasum -a 256 "$OWNER_FILE" | awk '{print $1}')
  if [[ "$current_sha" != "$LOCK_OWNER_FILE_SHA" ]]; then
    printf 'narration owner metadata changed during stale recovery: %s\n' \
      "$OWNER_FILE" >&2
    return 75
  fi
  rm -- "$OWNER_FILE"
}

# Invoked by the EXIT trap.
# shellcheck disable=SC2329
release_owner_metadata() {
  if (( STAGE_CREATED )) && [[ -d "$STAGE" && ! -L "$STAGE" ]]; then
    rm -rf -- "$STAGE"
    STAGE_CREATED=0
  fi
  if (( ! OWNER_CREATED )); then
    return
  fi
  if [[ -f "$OWNER_FILE" && ! -L "$OWNER_FILE" ]]; then
    local token pid
    token=$(owner_field owner_token 2>/dev/null || true)
    pid=$(owner_field owner_pid 2>/dev/null || true)
    if [[ "$token" == "$OWNER_TOKEN" && "$pid" == "$OWNER_PID" ]]; then
      rm -f -- "$OWNER_FILE"
    fi
  fi
  OWNER_CREATED=0
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
  seal_resume_state >/dev/null 2>&1 || true
  exit "$exit_status"
}

recover_stale_owner() {
  if [[ ! -e "$OWNER_FILE" && ! -L "$OWNER_FILE" ]]; then
    printf 'no narration owner metadata exists to recover: %s\n' "$OWNER_FILE" >&2
    return 66
  fi
  classify_owner_metadata
  case "$LOCK_CLASSIFICATION" in
    active)
      printf 'active narration lock cannot be recovered: %s\n' "$OWNER_FILE" >&2
      return 75
      ;;
    remote)
      printf 'remote narration lock cannot be recovered automatically: %s\n' \
        "$OWNER_FILE" >&2
      return 75
      ;;
    malformed)
      printf 'malformed narration lock cannot be recovered automatically: %s\n' \
        "$OWNER_FILE" >&2
      return 75
      ;;
    stale)
      remove_unchanged_stale_owner
      printf 'stale narration lock recovered: %s\n' "$OWNER_FILE"
      ;;
  esac
}

if [[ "$INTERNAL_MODE" == recover ]]; then
  recover_stale_owner
  exit $?
fi

if [[ -e "$OWNER_FILE" || -L "$OWNER_FILE" ]]; then
  classify_owner_metadata
  case "$LOCK_CLASSIFICATION" in
    stale)
      remove_unchanged_stale_owner
      printf 'recovered stale local narration owner: %s\n' "$OWNER_FILE" >&2
      ;;
    active)
      printf 'active narration lock metadata blocks this render: %s\n' \
        "$OWNER_FILE" >&2
      exit 75
      ;;
    remote)
      printf 'remote narration lock metadata blocks this render: %s\n' \
        "$OWNER_FILE" >&2
      exit 75
      ;;
    malformed)
      printf 'malformed narration lock metadata blocks this render: %s\n' \
        "$OWNER_FILE" >&2
      exit 75
      ;;
  esac
fi

umask 077
OWNER_TOKEN=$(printf '%s' "$OWNER_PID:$RANDOM:$RANDOM:$RUN_ID" | shasum -a 256 | awk '{print $1}')
OWNER_START=$(process_start_for_pid "$OWNER_PID")
if [[ ! "$OWNER_TOKEN" =~ ^[0-9a-f]{64}$ || -z "$OWNER_START" ]]; then
  printf 'could not establish narration lease owner identity\n' >&2
  exit 70
fi
trap release_owner_metadata EXIT
trap 'handle_signal HUP 129' HUP
trap 'handle_signal INT 130' INT
trap 'handle_signal TERM 143' TERM
owner_text=$(printf '%s\n' \
  'lock_schema=2' \
  "owner_token=$OWNER_TOKEN" \
  "owner_pid=$OWNER_PID" \
  "owner_host=$LOCAL_HOST" \
  "owner_start=$OWNER_START" \
  "run_id=$RUN_ID" \
  "work_dir=$WORK" \
  "narration_db=$DB" \
  "output_m4b=$OUTPUT" \
  "output_sidecar=$SIDECAR" \
  "output_audit=$AUDIT" \
  "output_reel=$REEL")
if ! printf '%s\n' "$owner_text" \
  | /usr/local/bin/python3 "$SCRIPT_DIR/echo_pronunciation_state.py" \
    immutable-file "$OWNER_FILE"; then
  printf 'could not create narration owner metadata atomically: %s\n' \
    "$OWNER_FILE" >&2
  exit 75
fi
OWNER_CREATED=1

verify_locked_inputs() {
  local current_epub_sha current_cli_sha current_resources_sha current_source_sha source_status
  if ! current_epub_sha=$(shasum -a 256 "$EPUB" | awk '{print $1}') \
    || [[ "$current_epub_sha" != "$EPUB_SHA256" ]]; then
    printf 'EPUB changed while narration lease was held: %s\n' "$EPUB" >&2
    return 65
  fi
  if ! current_cli_sha=$(shasum -a 256 "$CLI" | awk '{print $1}') \
    || [[ "$current_cli_sha" != "$ECHO_CLI_SHA256" ]]; then
    printf 'Echo CLI changed while narration lease was held: %s\n' "$CLI" >&2
    return 65
  fi
  if ! current_resources_sha=$(
    /usr/local/bin/python3 "$SCRIPT_DIR/echo_pronunciation_state.py" \
      hash-tree "$ECHO_RESOURCE_DIR"
  ) || [[ "$current_resources_sha" != "$ECHO_RESOURCES_SHA256" ]]; then
    printf 'Echo resources changed while narration lease was held: %s\n' \
      "$ECHO_RESOURCE_DIR" >&2
    return 65
  fi
  current_source_sha=$(git -C "${ECHO_REPO:-/Users/dfakkeldy/Developer/Echo}" rev-parse HEAD)
  source_status=$(git -C "${ECHO_REPO:-/Users/dfakkeldy/Developer/Echo}" status --porcelain --untracked-files=all)
  if [[ "$current_source_sha" != "$ECHO_SOURCE_SHA" || -n "$source_status" ]]; then
    printf 'Echo source changed while narration lease was held\n' >&2
    return 65
  fi
  if [[ -L "$ECHO_RENDER_INPUT_RECEIPT" || ! -f "$ECHO_RENDER_INPUT_RECEIPT" ]]; then
    printf 'receipt changed while narration lease was held: %s\n' \
      "$ECHO_RENDER_INPUT_RECEIPT" >&2
    return 65
  fi
  local expected_receipt actual_receipt
  expected_receipt=$(printf '%s\n' \
    "approved_echo_pronunciation_sha=$APPROVED_ECHO_PRONUNCIATION_SHA" \
    "echo_source_sha=$ECHO_SOURCE_SHA" \
    "epub_sha256=$EPUB_SHA256" \
    "echo_cli_sha256=$ECHO_CLI_SHA256" \
    "echo_cli_path=$CLI" \
    "echo_resources_sha256=$ECHO_RESOURCES_SHA256" \
    "echo_resource_dir=$ECHO_RESOURCE_DIR" \
    "voice=$VOICE" \
    "run_id=$RUN_ID" \
    "work_dir=$WORK" \
    "narration_db=$DB")
  actual_receipt=$(<"$ECHO_RENDER_INPUT_RECEIPT")
  if [[ "$actual_receipt" != "$expected_receipt" ]]; then
    printf 'receipt changed while narration lease was held: %s\n' \
      "$ECHO_RENDER_INPUT_RECEIPT" >&2
    return 65
  fi
}

verify_locked_inputs

state_command=(
  --work "$WORK"
  --db "$DB"
  --receipt "$STATE_RECEIPT"
  --epub "$EPUB"
  --source-sha "$ECHO_SOURCE_SHA"
  --voice "$VOICE"
  --input-receipt "$ECHO_RENDER_INPUT_RECEIPT"
  --lock-root "$ECHO_PRONUNCIATION_LEASE_ROOT"
)

seal_resume_state() {
  /usr/local/bin/python3 "$SCRIPT_DIR/echo_pronunciation_state.py" \
    record-state "${state_command[@]}"
}

if (( RESUME )); then
  if ! /usr/local/bin/python3 "$SCRIPT_DIR/echo_pronunciation_state.py" \
    verify-state "${state_command[@]}"; then
    printf 'resume state is not bound to the current WORK, DB, and Echo v12 captures\n' >&2
    exit 65
  fi
else
  /usr/local/bin/python3 "$SCRIPT_DIR/echo_pronunciation_state.py" \
    reset-state --work "$WORK" --db "$DB" --receipt "$STATE_RECEIPT" \
    --lock-root "$ECHO_PRONUNCIATION_LEASE_ROOT"
fi

if [[ -L "$SUCCESS_RECEIPT" ]]; then
  printf 'render-success receipt must not be a symlink: %s\n' "$SUCCESS_RECEIPT" >&2
  exit 65
fi
rm -f -- "$SUCCESS_RECEIPT"
for final_output in "$OUTPUT" "$SIDECAR" "$AUDIT" "$REEL"; do
  if [[ -L "$final_output" ]]; then
    printf 'final narration output must not be a symlink: %s\n' "$final_output" >&2
    exit 65
  fi
done

STAGE=$(mktemp -d "$RUN_ROOT/.echo-output-$RUN_ID.XXXXXX")
STAGE_CREATED=1
STAGE_OUTPUT="$STAGE/$SLUG.m4b"
STAGE_SIDECAR="$STAGE/$SLUG.alignment.json"
STAGE_AUDIT="$STAGE/$SLUG.pronunciation-audit.json"
STAGE_REEL="$STAGE/$SLUG.pronunciation-reel.m4b"

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

"${narrate_command[@]}" &
NARRATE_PID=$!
set +e
wait "$NARRATE_PID"
narrate_status=$?
set -e
NARRATE_PID=
if ! verify_locked_inputs; then
  exit 65
fi
if [[ -d "$WORK" && -f "$DB" ]] \
  && compgen -G "$WORK/.anchors-ch*.json" >/dev/null; then
  if ! seal_resume_state; then
    printf 'could not seal resumable Echo v12 capture state\n' >&2
    exit 65
  fi
fi
if (( narrate_status != 0 )); then
  exit "$narrate_status"
fi
if [[ ! -f "$STATE_RECEIPT" || -L "$STATE_RECEIPT" ]]; then
  printf 'successful narration did not produce sealed Echo v12 capture state\n' >&2
  exit 65
fi

for required_output in "$STAGE_OUTPUT" "$STAGE_SIDECAR" "$STAGE_AUDIT"; do
  if [[ -L "$required_output" || ! -f "$required_output" ]]; then
    printf 'successful narration did not produce required output: %s\n' \
      "$required_output" >&2
    exit 65
  fi
done
if [[ ! -s "$STAGE_OUTPUT" ]]; then
  printf 'successful narration produced an empty audiobook\n' >&2
  exit 65
fi
ECHO_RESOURCE_DIR="$ECHO_RESOURCE_DIR" "$CLI" verify-sidecar \
  --epub "$EPUB" \
  --audio "$STAGE_OUTPUT" \
  --sidecar "$STAGE_SIDECAR"
"$SCRIPT_DIR/validate_pronunciation_audit.py" "$STAGE_AUDIT"

for final_output in "$OUTPUT" "$SIDECAR" "$AUDIT" "$REEL"; do
  if [[ -L "$final_output" ]]; then
    printf 'final narration output must not be a symlink: %s\n' "$final_output" >&2
    exit 65
  fi
done
mv -f -- "$STAGE_OUTPUT" "$OUTPUT"
mv -f -- "$STAGE_SIDECAR" "$SIDECAR"
mv -f -- "$STAGE_AUDIT" "$AUDIT"
if [[ -f "$STAGE_REEL" && ! -L "$STAGE_REEL" ]]; then
  mv -f -- "$STAGE_REEL" "$REEL"
else
  rm -f -- "$REEL"
fi
rmdir -- "$STAGE"
STAGE_CREATED=0

ECHO_RESOURCE_DIR="$ECHO_RESOURCE_DIR" "$CLI" verify-sidecar \
  --epub "$EPUB" \
  --audio "$OUTPUT" \
  --sidecar "$SIDECAR"
"$SCRIPT_DIR/validate_pronunciation_audit.py" "$AUDIT"
/usr/local/bin/python3 "$SCRIPT_DIR/echo_pronunciation_state.py" \
  write-success \
  --run-id "$RUN_ID" \
  --receipt "$SUCCESS_RECEIPT" \
  --input-receipt "$ECHO_RENDER_INPUT_RECEIPT" \
  --state-receipt "$STATE_RECEIPT" \
  --audiobook "$OUTPUT" \
  --sidecar "$SIDECAR" \
  --audit "$AUDIT" \
  --reel "$REEL" \
  --lock-root "$ECHO_PRONUNCIATION_LEASE_ROOT"
/usr/local/bin/python3 "$SCRIPT_DIR/echo_pronunciation_state.py" \
  verify-success \
  --run-id "$RUN_ID" \
  --receipt "$SUCCESS_RECEIPT" \
  --input-receipt "$ECHO_RENDER_INPUT_RECEIPT" \
  --state-receipt "$STATE_RECEIPT" \
  --audiobook "$OUTPUT" \
  --sidecar "$SIDECAR" \
  --audit "$AUDIT" \
  --reel "$REEL"
