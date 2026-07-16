#!/usr/bin/env bash

set -euo pipefail

# PILOT ONLY: this path creates comprehension evidence, never a book package.

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
# shellcheck disable=SC1091
source "$SCRIPT_DIR/echo_pronunciation_preflight.sh"

usage() {
  printf '%s\n' \
    'usage: echo_learning_pilot_narrate.sh' >&2
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

ECHO_REPO=${ECHO_REPO:-/Users/dfakkeldy/Developer/Echo}
BUILD_RESOURCE="$ECHO_REPO/.build/cli"
ECHO_PRONUNCIATION_LEASE_ROOT=$(echo_pronunciation_canonical_lease_root) \
  || exit $?
export ECHO_REPO BUILD_RESOURCE ECHO_PRONUNCIATION_LEASE_ROOT

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
  if ! "${command[@]}"; then
    printf 'internal pilot mode requires an inherited FD-backed lease capability\n' >&2
    return 70
  fi
}

pilot_preflight() {
  local original_pwd=$PWD
  local explainer_root=${EXPLAINER_ROOT:-$(cd -- "$SCRIPT_DIR/../../.." && pwd -P)}
  local build_gate=${ECHO_BUILD_GATE:-$HOME/.claude/bin/xcode-build-gate.sh}
  local approved_input=${APPROVED_ECHO_PRONUNCIATION_SHA:-}

  ECHO_REPO=$(cd -- "$ECHO_REPO" 2>/dev/null && pwd -P) || {
    printf 'cannot resolve Echo repository: %s\n' "$ECHO_REPO" >&2
    return 66
  }
  EXPLAINER_ROOT=$(cd -- "$explainer_root" 2>/dev/null && pwd -P) || {
    printf 'cannot resolve explainer-audiobooks repository: %s\n' \
      "$explainer_root" >&2
    return 66
  }
  BUILD_RESOURCE="$ECHO_REPO/.build/cli"
  assert_leases "$BUILD_RESOURCE"

  if [[ -z "$approved_input" ]]; then
    printf '%s\n' \
      'APPROVED_ECHO_PRONUNCIATION_SHA is required;' \
      'record the reviewed Echo commit boundary before rendering' >&2
    return 64
  fi
  require_git_commit_sha APPROVED_ECHO_PRONUNCIATION_SHA "$approved_input"
  if [[ ! ${SLUG:-} =~ ^[a-z0-9][a-z0-9-]*$ ]]; then
    printf 'SLUG must use lowercase letters, digits, and internal hyphens only\n' >&2
    return 64
  fi
  if [[ -z ${TITLE:-} || "$TITLE" == *$'\n'* || "$TITLE" == *$'\r'* ]]; then
    printf 'TITLE must be nonempty and single-line\n' >&2
    return 64
  fi
  if [[ -z ${RUN_ROOT:-} || "$RUN_ROOT" != /* ]]; then
    printf 'RUN_ROOT must be a nonempty absolute explainer-audiobooks run path\n' >&2
    return 64
  fi

  local expected_run_root="$EXPLAINER_ROOT/.build/custom-learning-audiobooks/$SLUG"
  local canonical_run_root
  canonical_run_root=$(cd -- "$RUN_ROOT" 2>/dev/null && pwd -P) \
    || canonical_run_root=
  if [[ "$canonical_run_root" != "$expected_run_root" ]]; then
    printf 'RUN_ROOT must equal the canonical run path: %s\n' \
      "$expected_run_root" >&2
    return 64
  fi

  PILOT_ROOT="$RUN_ROOT/pilot"
  PILOT_DIST="$PILOT_ROOT/dist"
  EPUB="$PILOT_DIST/$SLUG-pilot.epub"
  PRONUNCIATION_PLAN="$RUN_ROOT/research/pronunciation-plan.json"
  for governed_path in \
    "$RUN_ROOT" "$RUN_ROOT/research" "$PILOT_ROOT" "$PILOT_DIST" \
    "$EPUB" "$PRONUNCIATION_PLAN"; do
    if [[ -L "$governed_path" ]]; then
      printf 'governed pilot path must not be a symlink: %s\n' \
        "$governed_path" >&2
      return 65
    fi
  done
  if [[ ! -f "$EPUB" ]]; then
    printf 'pilot EPUB is missing: %s\n' "$EPUB" >&2
    return 66
  fi
  if [[ ! -f "$PRONUNCIATION_PLAN" ]]; then
    printf 'pronunciation plan is missing: %s\n' "$PRONUNCIATION_PLAN" >&2
    return 66
  fi
  if [[ ! -x "$build_gate" ]]; then
    printf 'Echo build gate is missing or not executable: %s\n' "$build_gate" >&2
    return 66
  fi

  APPROVED_ECHO_PRONUNCIATION_SHA=$(
    git -C "$ECHO_REPO" rev-parse --verify "${approved_input}^{commit}"
  ) || {
    printf 'approved Echo pronunciation revision is not a commit: %s\n' \
      "$approved_input" >&2
    return 65
  }
  ECHO_SOURCE_SHA=$(git -C "$ECHO_REPO" rev-parse HEAD) || return 65
  local echo_status
  echo_status=$(git -C "$ECHO_REPO" status --porcelain --untracked-files=all)
  if [[ -n "$echo_status" ]]; then
    printf 'Echo working tree is not clean; source SHA would not identify the built renderer\n' >&2
    return 65
  fi
  if [[ "$APPROVED_ECHO_PRONUNCIATION_SHA" != "$ECHO_SOURCE_SHA" ]]; then
    printf 'approved Echo pronunciation revision %s must exactly equal Echo source HEAD %s\n' \
      "$APPROVED_ECHO_PRONUNCIATION_SHA" "$ECHO_SOURCE_SHA" >&2
    return 65
  fi

  "$build_gate" --wait
  make -C "$ECHO_REPO" echo-cli

  CLI="$ECHO_REPO/.build/cli/Build/Products/Release/echo-cli"
  if [[ -L "$CLI" || ! -x "$CLI" ]]; then
    printf 'missing or unsafe Release echo-cli: %s\n' "$CLI" >&2
    return 66
  fi
  ECHO_RESOURCE_DIR="$(dirname -- "$CLI")/EchoNarrationResources"
  if [[ -L "$ECHO_RESOURCE_DIR" || ! -d "$ECHO_RESOURCE_DIR" ]]; then
    printf 'missing or unsafe Release EchoNarrationResources: %s\n' \
      "$ECHO_RESOURCE_DIR" >&2
    return 66
  fi
  ECHO_RESOURCES_SHA256=$(
    /usr/local/bin/python3 "$SCRIPT_DIR/echo_pronunciation_state.py" \
      hash-tree "$ECHO_RESOURCE_DIR"
  )
  require_sha256 ECHO_RESOURCES_SHA256 "$ECHO_RESOURCES_SHA256"
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

  /usr/local/bin/python3 \
    "$SCRIPT_DIR/../../../skill/scripts/pronunciation_plan_qc.py" \
    --run-root "$RUN_ROOT" \
    --phase planning >/dev/null

  EPUB_SHA256=$(shasum -a 256 "$EPUB" | awk '{print $1}')
  PRONUNCIATION_PLAN_SHA256=$(shasum -a 256 "$PRONUNCIATION_PLAN" | awk '{print $1}')
  ECHO_CLI_SHA256=$(shasum -a 256 "$CLI" | awk '{print $1}')
  WRAPPER_SHA256=$(shasum -a 256 "$SCRIPT_DIR/echo_learning_pilot_narrate.sh" | awk '{print $1}')
  require_sha256 EPUB_SHA256 "$EPUB_SHA256"
  require_sha256 PRONUNCIATION_PLAN_SHA256 "$PRONUNCIATION_PLAN_SHA256"
  require_sha256 ECHO_CLI_SHA256 "$ECHO_CLI_SHA256"
  require_sha256 WRAPPER_SHA256 "$WRAPPER_SHA256"

  VOICE=${VOICE:-am_michael}
  case "$VOICE" in
    am_michael | am_puck) ;;
    *)
      printf 'VOICE must be am_michael or am_puck, got: %s\n' "$VOICE" >&2
      return 64
      ;;
  esac

  RUN_ID="${EPUB_SHA256:0:12}-${ECHO_CLI_SHA256:0:12}-${ECHO_RESOURCES_SHA256:0:12}-${APPROVED_ECHO_PRONUNCIATION_SHA}-$VOICE-pilot"
  ATTEMPT_ID=$(/usr/local/bin/python3 -c 'import secrets; print(secrets.token_hex(32))')
  WORK="$PILOT_ROOT/audio-work-$RUN_ID-$ATTEMPT_ID"
  DB="$PILOT_ROOT/narration-$RUN_ID-$ATTEMPT_ID.sqlite"
  OUTPUT="$PILOT_DIST/$SLUG-pilot.m4b"
  SIDECAR="$PILOT_DIST/$SLUG-pilot.alignment.json"
  AUDIT="$PILOT_DIST/$SLUG-pilot.pronunciation-audit.json"
  REEL="$PILOT_DIST/$SLUG-pilot.pronunciation-reel.m4b"
  RECEIPT="$RUN_ROOT/research/comprehension-pilot-render.json"
  INPUT_RECEIPT="$RUN_ROOT/research/echo-pilot-render-inputs-$RUN_ID-$ATTEMPT_ID.env"

  local receipt_text
  receipt_text=$(printf '%s\n' \
    'package_status=pilot-only' \
    "attempt_id=$ATTEMPT_ID" \
    "approved_echo_pronunciation_sha=$APPROVED_ECHO_PRONUNCIATION_SHA" \
    "echo_source_sha=$ECHO_SOURCE_SHA" \
    "epub_path=$EPUB" \
    "epub_sha256=$EPUB_SHA256" \
    "pronunciation_plan_path=$PRONUNCIATION_PLAN" \
    "pronunciation_plan_sha256=$PRONUNCIATION_PLAN_SHA256" \
    "echo_cli_path=$CLI" \
    "echo_cli_sha256=$ECHO_CLI_SHA256" \
    "echo_resource_dir=$ECHO_RESOURCE_DIR" \
    "echo_resources_sha256=$ECHO_RESOURCES_SHA256" \
    "wrapper_sha256=$WRAPPER_SHA256" \
    "render_version=$ECHO_RENDER_VERSION" \
    "voice=$VOICE" \
    "title=$TITLE" \
    "run_id=$RUN_ID" \
    "work_dir=$WORK" \
    "narration_db=$DB")
  if [[ -e "$INPUT_RECEIPT" || -L "$INPUT_RECEIPT" \
    || -e "$WORK" || -L "$WORK" || -e "$DB" || -L "$DB" ]]; then
    printf 'fresh pilot attempt paths are not empty: %s\n' "$ATTEMPT_ID" >&2
    return 65
  fi
  if ! printf '%s\n' "$receipt_text" \
    | /usr/local/bin/python3 "$SCRIPT_DIR/echo_pronunciation_state.py" \
      immutable-file "$INPUT_RECEIPT"; then
    printf 'could not create immutable pilot input receipt: %s\n' \
      "$INPUT_RECEIPT" >&2
    return 65
  fi
  INPUT_RECEIPT_SHA256=$(shasum -a 256 "$INPUT_RECEIPT" | awk '{print $1}')
  require_sha256 INPUT_RECEIPT_SHA256 "$INPUT_RECEIPT_SHA256"

  if [[ "$PWD" != "$original_pwd" ]]; then
    printf 'pilot preflight changed cwd from %s to %s\n' \
      "$original_pwd" "$PWD" >&2
    return 70
  fi

  export ECHO_REPO EXPLAINER_ROOT BUILD_RESOURCE RUN_ROOT SLUG TITLE
  export APPROVED_ECHO_PRONUNCIATION_SHA ECHO_SOURCE_SHA
  export PILOT_ROOT PILOT_DIST EPUB EPUB_SHA256 PRONUNCIATION_PLAN
  export PRONUNCIATION_PLAN_SHA256 CLI ECHO_CLI_SHA256 ECHO_RESOURCE_DIR
  export ECHO_RESOURCES_SHA256 WRAPPER_SHA256 ECHO_RENDER_VERSION VOICE
  export RUN_ID ATTEMPT_ID
  export WORK DB OUTPUT SIDECAR AUDIT REEL RECEIPT INPUT_RECEIPT
  export INPUT_RECEIPT_SHA256
}

pilot_attest_inputs() {
  assert_leases "$BUILD_RESOURCE" "$WORK" "$DB" "$OUTPUT" "$SIDECAR" \
    "$AUDIT" "$REEL" "$RECEIPT" "$INPUT_RECEIPT"

  local current_source current_status current_epub_sha current_plan_sha
  local current_cli_sha current_resources_sha current_render_version
  local current_input_receipt_sha current_wrapper_sha
  current_source=$(git -C "$ECHO_REPO" rev-parse HEAD) || return 65
  current_status=$(git -C "$ECHO_REPO" status --porcelain --untracked-files=all)
  if [[ -n "$current_status" \
    || "$current_source" != "$ECHO_SOURCE_SHA" \
    || "$current_source" != "$APPROVED_ECHO_PRONUNCIATION_SHA" ]]; then
    printf 'approved Echo source changed while the pilot lease was held\n' >&2
    return 65
  fi
  if [[ -L "$EPUB" || ! -f "$EPUB" \
    || -L "$PRONUNCIATION_PLAN" || ! -f "$PRONUNCIATION_PLAN" \
    || -L "$CLI" || ! -x "$CLI" \
    || -L "$ECHO_RESOURCE_DIR" || ! -d "$ECHO_RESOURCE_DIR" \
    || -L "$INPUT_RECEIPT" || ! -f "$INPUT_RECEIPT" ]]; then
    printf 'pilot input changed or became unsafe while the lease was held\n' >&2
    return 65
  fi
  current_epub_sha=$(shasum -a 256 "$EPUB" | awk '{print $1}')
  current_plan_sha=$(shasum -a 256 "$PRONUNCIATION_PLAN" | awk '{print $1}')
  current_cli_sha=$(shasum -a 256 "$CLI" | awk '{print $1}')
  current_wrapper_sha=$(
    shasum -a 256 "$SCRIPT_DIR/echo_learning_pilot_narrate.sh" | awk '{print $1}'
  )
  current_input_receipt_sha=$(shasum -a 256 "$INPUT_RECEIPT" | awk '{print $1}')
  current_resources_sha=$(
    /usr/local/bin/python3 "$SCRIPT_DIR/echo_pronunciation_state.py" \
      hash-tree "$ECHO_RESOURCE_DIR"
  )
  if [[ "$current_epub_sha" != "$EPUB_SHA256" \
    || "$current_plan_sha" != "$PRONUNCIATION_PLAN_SHA256" \
    || "$current_cli_sha" != "$ECHO_CLI_SHA256" \
    || "$current_resources_sha" != "$ECHO_RESOURCES_SHA256" \
    || "$current_wrapper_sha" != "$WRAPPER_SHA256" ]]; then
    printf 'pilot source, plan, renderer, or resources changed while the lease was held\n' >&2
    return 65
  fi
  if [[ "$current_input_receipt_sha" != "$INPUT_RECEIPT_SHA256" ]]; then
    printf 'pilot input receipt changed while the lease was held\n' >&2
    return 65
  fi
  current_render_version=$(
    ECHO_RESOURCE_DIR="$ECHO_RESOURCE_DIR" "$CLI" --version \
      | while IFS= read -r line; do
          echo_pronunciation_release_render_version "$line"
        done
  ) || {
    printf 'pilot renderer is no longer an approved Release build\n' >&2
    return 65
  }
  if [[ "$current_render_version" != "$ECHO_RENDER_VERSION" ]]; then
    printf 'pilot render version changed while the lease was held\n' >&2
    return 65
  fi
  /usr/local/bin/python3 \
    "$SCRIPT_DIR/../../../skill/scripts/pronunciation_plan_qc.py" \
    --run-root "$RUN_ROOT" \
    --phase planning >/dev/null
}

if [[ -z "$INTERNAL_MODE" ]]; then
  exec "$SCRIPT_DIR/echo_pronunciation_lease.py" \
    --lock-root "$ECHO_PRONUNCIATION_LEASE_ROOT" \
    --resource "$BUILD_RESOURCE" \
    -- \
    "$0" --leased-preflight
fi

if [[ "$INTERNAL_MODE" == preflight ]]; then
  assert_leases "$BUILD_RESOURCE"
  pilot_preflight
  exec "$SCRIPT_DIR/echo_pronunciation_lease.py" \
    --lock-root "$ECHO_PRONUNCIATION_LEASE_ROOT" \
    --resource "$WORK" \
    --resource "$DB" \
    --resource "$OUTPUT" \
    --resource "$SIDECAR" \
    --resource "$AUDIT" \
    --resource "$REEL" \
    --resource "$RECEIPT" \
    --resource "$INPUT_RECEIPT" \
    -- \
    "$0" --leased-run
fi

if [[ "$INTERNAL_MODE" != run ]]; then
  printf 'invalid internal pilot mode\n' >&2
  exit 70
fi

assert_leases "$BUILD_RESOURCE"
pilot_attest_inputs

for final_output in "$OUTPUT" "$SIDECAR" "$AUDIT" "$REEL" "$RECEIPT"; do
  if [[ -e "$final_output" || -L "$final_output" ]]; then
    printf 'pilot output already exists; preserve it as evidence: %s\n' \
      "$final_output" >&2
    exit 65
  fi
done

STAGE=$(mktemp -d "$PILOT_ROOT/.echo-pilot-output-$RUN_ID-$ATTEMPT_ID.XXXXXX")
STAGE_CREATED=1
NARRATE_PID=

cleanup() {
  if [[ -n "$NARRATE_PID" ]] && kill -0 "$NARRATE_PID" 2>/dev/null; then
    kill "$NARRATE_PID" 2>/dev/null || true
    wait "$NARRATE_PID" 2>/dev/null || true
  fi
  if (( STAGE_CREATED )) && [[ -d "$STAGE" && ! -L "$STAGE" ]]; then
    rm -rf -- "$STAGE"
  fi
}

handle_signal() {
  local exit_status=${1:?exit status is required}
  cleanup
  exit "$exit_status"
}

trap cleanup EXIT
trap 'handle_signal 129' HUP
trap 'handle_signal 130' INT
trap 'handle_signal 143' TERM

STAGE_OUTPUT="$STAGE/$SLUG-pilot.m4b"
STAGE_SIDECAR="$STAGE/$SLUG-pilot.alignment.json"
STAGE_AUDIT="$STAGE/$SLUG-pilot.pronunciation-audit.json"
STAGE_REEL="$STAGE/$SLUG-pilot.pronunciation-reel.m4b"
STAGE_RECEIPT="$STAGE/comprehension-pilot-render.json"

narrate_command=(
  /usr/bin/env "ECHO_RESOURCE_DIR=$ECHO_RESOURCE_DIR"
  "$CLI" narrate
  --epub "$EPUB"
  --out "$STAGE_OUTPUT"
  --sidecar "$STAGE_SIDECAR"
  --voice "$VOICE"
  --title "$TITLE — Learning Pilot"
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
/usr/local/bin/python3 "$SCRIPT_DIR/validate_pronunciation_audit.py" \
  "$STAGE_AUDIT"
pilot_attest_inputs

AUDIO_SHA256=$(shasum -a 256 "$STAGE_OUTPUT" | awk '{print $1}')
SIDECAR_SHA256=$(shasum -a 256 "$STAGE_SIDECAR" | awk '{print $1}')
AUDIT_SHA256=$(shasum -a 256 "$STAGE_AUDIT" | awk '{print $1}')
for hash_name in AUDIO_SHA256 SIDECAR_SHA256 AUDIT_SHA256 INPUT_RECEIPT_SHA256; do
  require_sha256 "$hash_name" "${!hash_name}"
done

/usr/local/bin/python3 - \
  "$STAGE_RECEIPT" "$ATTEMPT_ID" "$RUN_ID" "$ECHO_SOURCE_SHA" \
  "$EPUB_SHA256" "$PRONUNCIATION_PLAN_SHA256" "$ECHO_CLI_SHA256" \
  "$ECHO_RESOURCES_SHA256" "$WRAPPER_SHA256" "$ECHO_RENDER_VERSION" "$VOICE" \
  "$INPUT_RECEIPT" "$INPUT_RECEIPT_SHA256" "$AUDIO_SHA256" \
  "$SIDECAR_SHA256" "$AUDIT_SHA256" <<'PY'
import json
import sys
from pathlib import Path

(
    output,
    attempt_id,
    run_id,
    echo_source_sha,
    epub_sha,
    plan_sha,
    cli_sha,
    resources_sha,
    wrapper_sha,
    render_version,
    voice,
    input_receipt,
    input_receipt_sha,
    audio_sha,
    sidecar_sha,
    audit_sha,
) = sys.argv[1:]
payload = {
    "schemaVersion": 1,
    "status": "pass",
    "packageStatus": "pilot-only",
    "attemptID": attempt_id,
    "runID": run_id,
    "echoSourceSHA": echo_source_sha,
    "epubSHA256": epub_sha,
    "pronunciationPlanSHA256": plan_sha,
    "echoCLISHA256": cli_sha,
    "echoResourcesSHA256": resources_sha,
    "wrapperSHA256": wrapper_sha,
    "renderVersion": int(render_version),
    "voice": voice,
    "inputReceiptFileName": Path(input_receipt).name,
    "inputReceiptSHA256": input_receipt_sha,
    "audioSHA256": audio_sha,
    "sidecarSHA256": sidecar_sha,
    "pronunciationAuditSHA256": audit_sha,
    "humanListening": "pending",
}
Path(output).write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY

for final_output in "$OUTPUT" "$SIDECAR" "$AUDIT" "$REEL" "$RECEIPT"; do
  if [[ -e "$final_output" || -L "$final_output" ]]; then
    printf 'pilot output appeared before publish: %s\n' "$final_output" >&2
    exit 65
  fi
done
mv -- "$STAGE_OUTPUT" "$OUTPUT"
mv -- "$STAGE_SIDECAR" "$SIDECAR"
mv -- "$STAGE_AUDIT" "$AUDIT"
if [[ -f "$STAGE_REEL" && ! -L "$STAGE_REEL" ]]; then
  mv -- "$STAGE_REEL" "$REEL"
fi
mv -- "$STAGE_RECEIPT" "$RECEIPT"
rmdir -- "$STAGE"
STAGE_CREATED=0

ECHO_RESOURCE_DIR="$ECHO_RESOURCE_DIR" "$CLI" verify-sidecar \
  --epub "$EPUB" \
  --audio "$OUTPUT" \
  --sidecar "$SIDECAR"
/usr/local/bin/python3 "$SCRIPT_DIR/validate_pronunciation_audit.py" "$AUDIT"
pilot_attest_inputs

printf 'PILOT ONLY: native Echo comprehension audio rendered\n'
printf 'audio=%s\nsidecar=%s\nreceipt=%s\n' \
  "$OUTPUT" "$SIDECAR" "$RECEIPT"
