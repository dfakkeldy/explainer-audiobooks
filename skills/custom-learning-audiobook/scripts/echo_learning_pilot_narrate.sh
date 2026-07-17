#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
# Resolved from this script's absolute directory.
# shellcheck disable=SC1091
source "$SCRIPT_DIR/echo_pronunciation_preflight.sh"

usage() {
  printf '%s\n' 'usage: echo_learning_pilot_narrate.sh' >&2
}

INTERNAL_MODE=
while (( $# )); do
  case "$1" in
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

ECHO_PRONUNCIATION_LEASE_ROOT=$(echo_pronunciation_canonical_lease_root) \
  || exit $?
ECHO_REPO=${ECHO_REPO:-/Users/dfakkeldy/Developer/Echo}
BUILD_RESOURCE="$ECHO_REPO/.build/cli"
export ECHO_PRONUNCIATION_LEASE_ROOT ECHO_REPO BUILD_RESOURCE

assert_leases() {
  local command=(
    "$SCRIPT_DIR/echo_pronunciation_lease.py"
    --assert-held
    --lock-root "$ECHO_PRONUNCIATION_LEASE_ROOT"
  )
  local resource
  for resource in "$@"; do
    command+=(--resource "$resource")
  done
  if ! "${command[@]}" >/dev/null; then
    printf 'learning-pilot narration requires inherited FD-backed leases\n' >&2
    return 70
  fi
}

if [[ -z "$INTERNAL_MODE" ]]; then
  exec "$SCRIPT_DIR/echo_pronunciation_lease.py" \
    --lock-root "$ECHO_PRONUNCIATION_LEASE_ROOT" \
    --resource "$BUILD_RESOURCE" \
    -- "$0" --leased-preflight
fi

pilot_receipt_text() {
  printf '%s\n' \
    'schema=1' \
    'kind=learning-pilot-nonpackage' \
    "attempt_id=$ATTEMPT_ID" \
    "approved_echo_pronunciation_sha=$APPROVED_ECHO_PRONUNCIATION_SHA" \
    "echo_source_sha=$ECHO_SOURCE_SHA" \
    "epub_path=$EPUB" \
    "epub_sha256=$EPUB_SHA256" \
    "echo_cli_path=$CLI" \
    "echo_cli_sha256=$ECHO_CLI_SHA256" \
    "echo_resource_dir=$ECHO_RESOURCE_DIR" \
    "echo_resources_sha256=$ECHO_RESOURCES_SHA256" \
    "render_version=$ECHO_RENDER_VERSION" \
    "voice=$VOICE" \
    "title=$TITLE" \
    "pilot_input_sha256=$PILOT_INPUT_SHA256" \
    "work_dir=$WORK" \
    "narration_db=$DB"
}

pilot_preflight() {
  local original_pwd=$PWD
  local echo_repo=${ECHO_REPO:-/Users/dfakkeldy/Developer/Echo}
  local explainer_root=${EXPLAINER_ROOT:-$(cd -- "$SCRIPT_DIR/../../.." && pwd -P)}
  local build_gate=${ECHO_BUILD_GATE:-$HOME/.claude/bin/xcode-build-gate.sh}
  local approved_input=${APPROVED_ECHO_PRONUNCIATION_SHA:-}

  assert_leases "$BUILD_RESOURCE"
  echo_repo=$(cd -- "$echo_repo" 2>/dev/null && pwd -P) || {
    printf 'cannot resolve Echo repository: %s\n' "$echo_repo" >&2
    return 66
  }
  explainer_root=$(cd -- "$explainer_root" 2>/dev/null && pwd -P) || {
    printf 'cannot resolve explainer-audiobooks repository: %s\n' \
      "$explainer_root" >&2
    return 66
  }
  if [[ -z "$approved_input" ]]; then
    printf '%s\n' \
      'APPROVED_ECHO_PRONUNCIATION_SHA is required;' \
      'record the reviewed Echo commit boundary before rendering' >&2
    return 64
  fi
  require_git_commit_sha APPROVED_ECHO_PRONUNCIATION_SHA "$approved_input"
  if [[ ! ${SLUG:-} =~ ^[a-z0-9][a-z0-9-]*$ || "$SLUG" == *-pilot ]]; then
    printf 'SLUG must be the lowercase base-book slug without a -pilot suffix\n' >&2
    return 64
  fi
  if [[ -z ${RUN_ROOT:-} || "$RUN_ROOT" != /* ]]; then
    printf 'RUN_ROOT must be the absolute canonical base-book run path\n' >&2
    return 64
  fi
  local canonical_run_root expected_run_root
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
    am_michael | am_puck | af_heart) ;;
    *)
      printf 'VOICE must be am_michael, am_puck, or af_heart, got: %s\n' "$VOICE" >&2
      return 64
      ;;
  esac
  if [[ ! -x "$build_gate" ]]; then
    printf 'Echo build gate is missing or not executable: %s\n' \
      "$build_gate" >&2
    return 66
  fi

  APPROVED_ECHO_PRONUNCIATION_SHA=$(
    git -C "$echo_repo" rev-parse --verify "${approved_input}^{commit}"
  ) || {
    printf 'approved Echo pronunciation revision is not a commit: %s\n' \
      "$approved_input" >&2
    return 65
  }
  ECHO_SOURCE_SHA=$(git -C "$echo_repo" rev-parse HEAD) || return 65
  local echo_status
  echo_status=$(git -C "$echo_repo" status --porcelain --untracked-files=all)
  if [[ -n "$echo_status" ]]; then
    printf 'Echo working tree is not clean; renderer attestation failed\n' >&2
    return 65
  fi
  if [[ "$APPROVED_ECHO_PRONUNCIATION_SHA" != "$ECHO_SOURCE_SHA" ]]; then
    printf 'approved Echo pronunciation revision %s must exactly equal Echo source HEAD %s\n' \
      "$APPROVED_ECHO_PRONUNCIATION_SHA" "$ECHO_SOURCE_SHA" >&2
    return 65
  fi

  "$build_gate" --wait
  make -C "$echo_repo" echo-cli
  CLI="$echo_repo/.build/cli/Build/Products/Release/echo-cli"
  ECHO_RESOURCE_DIR="$(dirname -- "$CLI")/EchoNarrationResources"
  if [[ -L "$CLI" || ! -x "$CLI" ]]; then
    printf 'missing or unsafe Release echo-cli: %s\n' "$CLI" >&2
    return 66
  fi
  if [[ -L "$ECHO_RESOURCE_DIR" || ! -d "$ECHO_RESOURCE_DIR" ]]; then
    printf 'missing or unsafe Release EchoNarrationResources: %s\n' \
      "$ECHO_RESOURCE_DIR" >&2
    return 66
  fi
  local cli_version cli_help
  cli_version=$(ECHO_RESOURCE_DIR="$ECHO_RESOURCE_DIR" "$CLI" --version)
  ECHO_RENDER_VERSION=$(
    echo_pronunciation_release_render_version "$cli_version"
  ) || {
    printf 'stale, pre-v12, or non-Release echo-cli: %s\n' "$cli_version" >&2
    return 65
  }
  cli_help=$(ECHO_RESOURCE_DIR="$ECHO_RESOURCE_DIR" "$CLI" narrate --help)
  if [[ "$cli_help" != *"--no-pronunciation-review"* ]]; then
    printf 'stale echo-cli: pronunciation review is unavailable\n' >&2
    return 65
  fi

  EPUB_SHA256=$(/usr/bin/shasum -a 256 "$EPUB" | awk '{print $1}')
  ECHO_CLI_SHA256=$(/usr/bin/shasum -a 256 "$CLI" | awk '{print $1}')
  ECHO_RESOURCES_SHA256=$(
    /usr/local/bin/python3 "$SCRIPT_DIR/echo_pronunciation_state.py" \
      hash-tree "$ECHO_RESOURCE_DIR"
  )
  require_sha256 EPUB_SHA256 "$EPUB_SHA256"
  require_sha256 ECHO_CLI_SHA256 "$ECHO_CLI_SHA256"
  require_sha256 ECHO_RESOURCES_SHA256 "$ECHO_RESOURCES_SHA256"
  PILOT_INPUT_SHA256=$(printf '%s\n' \
    "epub=$EPUB_SHA256" \
    "echo_cli=$ECHO_CLI_SHA256" \
    "echo_resources=$ECHO_RESOURCES_SHA256" \
    "approved_source=$APPROVED_ECHO_PRONUNCIATION_SHA" \
    "render_version=$ECHO_RENDER_VERSION" \
    "voice=$VOICE" \
    "title=$TITLE" \
    | /usr/bin/shasum -a 256 | awk '{print $1}')
  require_sha256 PILOT_INPUT_SHA256 "$PILOT_INPUT_SHA256"

  ATTEMPT_ID=$(/usr/local/bin/python3 -c 'import secrets; print(secrets.token_hex(32))')
  WORK="$PILOT_ROOT/audio-work-${PILOT_INPUT_SHA256:0:12}-$ATTEMPT_ID"
  DB="$PILOT_ROOT/narration-${PILOT_INPUT_SHA256:0:12}-$ATTEMPT_ID.sqlite"
  OUTPUT="$PILOT_DIST/$PILOT_SLUG.m4b"
  SIDECAR="$PILOT_DIST/$PILOT_SLUG.alignment.json"
  AUDIT="$PILOT_DIST/$PILOT_SLUG.pronunciation-audit.json"
  REEL="$PILOT_DIST/$PILOT_SLUG.pronunciation-reel.m4b"
  mkdir -p -- "$PILOT_RESEARCH"
  if [[ -L "$PILOT_RESEARCH" || ! -d "$PILOT_RESEARCH" ]]; then
    printf 'pilot research path is unsafe: %s\n' "$PILOT_RESEARCH" >&2
    return 65
  fi
  INPUT_RECEIPT="$PILOT_RESEARCH/echo-pilot-inputs-$ATTEMPT_ID.env"
  SUCCESS_RECEIPT="$PILOT_RESEARCH/echo-pilot-success-$ATTEMPT_ID.env"
  for governed_output in \
    "$WORK" "$DB" "$OUTPUT" "$SIDECAR" "$AUDIT" "$REEL" \
    "$INPUT_RECEIPT" "$SUCCESS_RECEIPT"; do
    if [[ -L "$governed_output" ]]; then
      printf 'governed pilot output must not be a symlink: %s\n' \
        "$governed_output" >&2
      return 65
    fi
  done
  if [[ -e "$WORK" || -e "$DB" || -e "$INPUT_RECEIPT" \
    || -e "$SUCCESS_RECEIPT" ]]; then
    printf 'fresh pilot attempt paths unexpectedly already exist\n' >&2
    return 65
  fi
  local receipt_text
  receipt_text=$(pilot_receipt_text)
  if ! printf '%s\n' "$receipt_text" \
    | /usr/local/bin/python3 "$SCRIPT_DIR/echo_pronunciation_state.py" \
      immutable-file "$INPUT_RECEIPT"; then
    printf 'could not create immutable pilot-input receipt: %s\n' \
      "$INPUT_RECEIPT" >&2
    return 65
  fi
  if [[ "$PWD" != "$original_pwd" ]]; then
    printf 'pilot preflight changed cwd from %s to %s\n' \
      "$original_pwd" "$PWD" >&2
    return 70
  fi

  ECHO_REPO=$echo_repo
  EXPLAINER_ROOT=$explainer_root
  export ECHO_REPO EXPLAINER_ROOT RUN_ROOT SLUG TITLE VOICE
  export PILOT_SLUG PILOT_ROOT PILOT_DIST PILOT_RESEARCH
  export APPROVED_ECHO_PRONUNCIATION_SHA ECHO_SOURCE_SHA
  export EPUB EPUB_SHA256 CLI ECHO_CLI_SHA256
  export ECHO_RESOURCE_DIR ECHO_RESOURCES_SHA256 ECHO_RENDER_VERSION
  export PILOT_INPUT_SHA256 ATTEMPT_ID WORK DB OUTPUT SIDECAR AUDIT REEL
  export INPUT_RECEIPT SUCCESS_RECEIPT
}

pilot_attest_inputs() {
  local required
  for required in \
    ECHO_REPO EXPLAINER_ROOT RUN_ROOT SLUG TITLE VOICE \
    PILOT_SLUG PILOT_ROOT PILOT_DIST PILOT_RESEARCH \
    APPROVED_ECHO_PRONUNCIATION_SHA ECHO_SOURCE_SHA \
    EPUB EPUB_SHA256 CLI ECHO_CLI_SHA256 ECHO_RESOURCE_DIR \
    ECHO_RESOURCES_SHA256 ECHO_RENDER_VERSION PILOT_INPUT_SHA256 \
    ATTEMPT_ID WORK DB OUTPUT SIDECAR AUDIT REEL \
    INPUT_RECEIPT SUCCESS_RECEIPT; do
    if [[ -z ${!required:-} || ${!required} == *$'\n'* \
      || ${!required} == *$'\r'* ]]; then
      printf 'sealed pilot preflight state is missing or unsafe: %s\n' \
        "$required" >&2
      return 70
    fi
  done
  require_git_commit_sha APPROVED_ECHO_PRONUNCIATION_SHA \
    "$APPROVED_ECHO_PRONUNCIATION_SHA"
  require_git_commit_sha ECHO_SOURCE_SHA "$ECHO_SOURCE_SHA"
  require_sha256 EPUB_SHA256 "$EPUB_SHA256"
  require_sha256 ECHO_CLI_SHA256 "$ECHO_CLI_SHA256"
  require_sha256 ECHO_RESOURCES_SHA256 "$ECHO_RESOURCES_SHA256"
  require_sha256 PILOT_INPUT_SHA256 "$PILOT_INPUT_SHA256"
  if [[ ! "$ATTEMPT_ID" =~ ^[0-9a-f]{64}$ ]]; then
    printf 'sealed pilot attempt ID is invalid\n' >&2
    return 70
  fi
  case "$VOICE" in
    am_michael | am_puck | af_heart) ;;
    *)
      printf 'sealed pilot voice is unsupported: %s\n' "$VOICE" >&2
      return 64
      ;;
  esac

  local canonical_echo canonical_explainer canonical_run canonical_pilot
  canonical_echo=$(cd -- "$ECHO_REPO" 2>/dev/null && pwd -P) \
    || canonical_echo=
  canonical_explainer=$(cd -- "$EXPLAINER_ROOT" 2>/dev/null && pwd -P) \
    || canonical_explainer=
  canonical_run=$(cd -- "$RUN_ROOT" 2>/dev/null && pwd -P) \
    || canonical_run=
  canonical_pilot=$(cd -- "$PILOT_ROOT" 2>/dev/null && pwd -P) \
    || canonical_pilot=
  if [[ "$canonical_echo" != "$ECHO_REPO" \
    || "$canonical_explainer" != "$EXPLAINER_ROOT" \
    || "$canonical_run" != "$EXPLAINER_ROOT/.build/custom-learning-audiobooks/$SLUG" \
    || "$canonical_pilot" != "$RUN_ROOT/pilot" \
    || "$PILOT_SLUG" != "$SLUG-pilot" \
    || "$PILOT_DIST" != "$PILOT_ROOT/dist" \
    || "$PILOT_RESEARCH" != "$PILOT_ROOT/research" \
    || "$EPUB" != "$PILOT_DIST/$PILOT_SLUG.epub" \
    || "$OUTPUT" != "$PILOT_DIST/$PILOT_SLUG.m4b" \
    || "$SIDECAR" != "$PILOT_DIST/$PILOT_SLUG.alignment.json" \
    || "$AUDIT" != "$PILOT_DIST/$PILOT_SLUG.pronunciation-audit.json" \
    || "$REEL" != "$PILOT_DIST/$PILOT_SLUG.pronunciation-reel.m4b" \
    || "$WORK" != "$PILOT_ROOT/audio-work-${PILOT_INPUT_SHA256:0:12}-$ATTEMPT_ID" \
    || "$DB" != "$PILOT_ROOT/narration-${PILOT_INPUT_SHA256:0:12}-$ATTEMPT_ID.sqlite" \
    || "$INPUT_RECEIPT" != "$PILOT_RESEARCH/echo-pilot-inputs-$ATTEMPT_ID.env" \
    || "$SUCCESS_RECEIPT" != "$PILOT_RESEARCH/echo-pilot-success-$ATTEMPT_ID.env" ]]; then
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
  assert_leases \
    "$BUILD_RESOURCE" "$WORK" "$DB" "$OUTPUT" "$SIDECAR" "$AUDIT" "$REEL" \
    "$INPUT_RECEIPT" "$SUCCESS_RECEIPT"

  local current_source source_status resolved_approved
  current_source=$(/usr/bin/git -C "$ECHO_REPO" rev-parse HEAD) || return 65
  source_status=$(/usr/bin/git -C "$ECHO_REPO" status --porcelain \
    --untracked-files=all)
  resolved_approved=$(/usr/bin/git -C "$ECHO_REPO" rev-parse --verify \
    "${APPROVED_ECHO_PRONUNCIATION_SHA}^{commit}") || return 65
  if [[ -n "$source_status" || "$current_source" != "$ECHO_SOURCE_SHA" \
    || "$resolved_approved" != "$APPROVED_ECHO_PRONUNCIATION_SHA" \
    || "$current_source" != "$APPROVED_ECHO_PRONUNCIATION_SHA" ]]; then
    printf 'approved Echo source changed while pilot lease was held\n' >&2
    return 65
  fi
  local expected_cli expected_resources release_component
  expected_cli="$ECHO_REPO/.build/cli/Build/Products/Release/echo-cli"
  expected_resources="$(dirname -- "$expected_cli")/EchoNarrationResources"
  for release_component in \
    "$ECHO_REPO/.build" "$ECHO_REPO/.build/cli" \
    "$ECHO_REPO/.build/cli/Build" "$ECHO_REPO/.build/cli/Build/Products" \
    "$ECHO_REPO/.build/cli/Build/Products/Release"; do
    if [[ -L "$release_component" ]]; then
      printf 'canonical Release path contains a symlink: %s\n' \
        "$release_component" >&2
      return 65
    fi
  done
  if [[ "$CLI" != "$expected_cli" || ! -x "$CLI" \
    || "$ECHO_RESOURCE_DIR" != "$expected_resources" \
    || ! -d "$ECHO_RESOURCE_DIR" || ! -f "$EPUB" ]]; then
    printf 'canonical pilot renderer inputs are missing or changed\n' >&2
    return 65
  fi

  local current_epub_sha current_cli_sha current_resources_sha
  local cli_version current_render_version cli_help current_input_sha
  current_epub_sha=$(/usr/bin/shasum -a 256 "$EPUB" | awk '{print $1}')
  current_cli_sha=$(/usr/bin/shasum -a 256 "$CLI" | awk '{print $1}')
  current_resources_sha=$(
    /usr/local/bin/python3 "$SCRIPT_DIR/echo_pronunciation_state.py" \
      hash-tree "$ECHO_RESOURCE_DIR"
  )
  cli_version=$(ECHO_RESOURCE_DIR="$ECHO_RESOURCE_DIR" "$CLI" --version)
  current_render_version=$(
    echo_pronunciation_release_render_version "$cli_version"
  ) || {
    printf 'stale, pre-v12, or non-Release echo-cli: %s\n' "$cli_version" >&2
    return 65
  }
  cli_help=$(ECHO_RESOURCE_DIR="$ECHO_RESOURCE_DIR" "$CLI" narrate --help)
  current_input_sha=$(printf '%s\n' \
    "epub=$current_epub_sha" \
    "echo_cli=$current_cli_sha" \
    "echo_resources=$current_resources_sha" \
    "approved_source=$APPROVED_ECHO_PRONUNCIATION_SHA" \
    "render_version=$current_render_version" \
    "voice=$VOICE" \
    "title=$TITLE" \
    | /usr/bin/shasum -a 256 | awk '{print $1}')
  if [[ "$current_epub_sha" != "$EPUB_SHA256" \
    || "$current_cli_sha" != "$ECHO_CLI_SHA256" \
    || "$current_resources_sha" != "$ECHO_RESOURCES_SHA256" \
    || "$current_render_version" != "$ECHO_RENDER_VERSION" \
    || "$current_input_sha" != "$PILOT_INPUT_SHA256" \
    || "$cli_help" != *"--no-pronunciation-review"* ]]; then
    printf 'learning-pilot renderer inputs changed while leases were held\n' >&2
    return 65
  fi
  if [[ ! -f "$INPUT_RECEIPT" \
    || $(/usr/bin/stat -f '%Lp' "$INPUT_RECEIPT") != 600 ]]; then
    printf 'pilot-input receipt is missing or has an unsafe mode\n' >&2
    return 65
  fi
  local expected_receipt actual_receipt
  expected_receipt=$(pilot_receipt_text)
  actual_receipt=$(<"$INPUT_RECEIPT")
  if [[ "$actual_receipt" != "$expected_receipt" ]]; then
    printf 'pilot-input receipt changed while leases were held\n' >&2
    return 65
  fi
}

if [[ "$INTERNAL_MODE" == preflight ]]; then
  pilot_preflight
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
    --resource "$SUCCESS_RECEIPT"
    --
    "$0"
    --leased-run
  )
  exec "${lease_command[@]}"
fi

pilot_attest_inputs

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
"${narrate_command[@]}" &
NARRATE_PID=$!
set +e
wait "$NARRATE_PID"
narrate_status=$?
set -e
NARRATE_PID=
pilot_attest_inputs
if (( narrate_status != 0 )); then
  exit "$narrate_status"
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

AUDIO_SHA256=$(/usr/bin/shasum -a 256 "$OUTPUT" | awk '{print $1}')
SIDECAR_SHA256=$(/usr/bin/shasum -a 256 "$SIDECAR" | awk '{print $1}')
AUDIT_SHA256=$(/usr/bin/shasum -a 256 "$AUDIT" | awk '{print $1}')
INPUT_RECEIPT_SHA256=$(/usr/bin/shasum -a 256 "$INPUT_RECEIPT" | awk '{print $1}')
require_sha256 AUDIO_SHA256 "$AUDIO_SHA256"
require_sha256 SIDECAR_SHA256 "$SIDECAR_SHA256"
require_sha256 AUDIT_SHA256 "$AUDIT_SHA256"
require_sha256 INPUT_RECEIPT_SHA256 "$INPUT_RECEIPT_SHA256"
REEL_PATH=
REEL_SHA256=
if [[ -f "$REEL" && ! -L "$REEL" ]]; then
  REEL_PATH=$REEL
  REEL_SHA256=$(/usr/bin/shasum -a 256 "$REEL" | awk '{print $1}')
  require_sha256 REEL_SHA256 "$REEL_SHA256"
fi
success_text=$(printf '%s\n' \
  'schema=1' \
  'kind=learning-pilot-nonpackage' \
  'listener_acceptance=pending' \
  "attempt_id=$ATTEMPT_ID" \
  "pilot_input_sha256=$PILOT_INPUT_SHA256" \
  "input_receipt_path=$INPUT_RECEIPT" \
  "input_receipt_sha256=$INPUT_RECEIPT_SHA256" \
  "audio_path=$OUTPUT" \
  "audio_sha256=$AUDIO_SHA256" \
  "sidecar_path=$SIDECAR" \
  "sidecar_sha256=$SIDECAR_SHA256" \
  "audit_path=$AUDIT" \
  "audit_sha256=$AUDIT_SHA256" \
  "reel_path=$REEL_PATH" \
  "reel_sha256=$REEL_SHA256")
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
