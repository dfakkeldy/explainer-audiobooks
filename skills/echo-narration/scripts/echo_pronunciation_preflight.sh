#!/usr/bin/env bash

set -euo pipefail

echo_pronunciation_canonical_lease_root() {
  local account_home
  account_home=$(/usr/local/bin/python3 - <<'PY'
import os
import pwd
from pathlib import Path

print(Path(pwd.getpwuid(os.geteuid()).pw_dir).resolve(strict=True))
PY
  ) || {
    printf 'cannot resolve the effective user account home for narration leases\n' >&2
    return 70
  }
  if [[ -z "$account_home" || "$account_home" != /* \
    || "$account_home" == *$'\n'* || "$account_home" == *$'\r'* ]]; then
    printf 'effective user account home is unsafe for narration leases\n' >&2
    return 70
  fi
  printf '%s/.cache/explainer-audiobooks/echo-pronunciation-leases\n' \
    "$account_home"
}

require_sha256() {
  local name=${1:?hash name is required}
  local value=${2:-}
  if [[ ! "$value" =~ ^[0-9a-f]{64}$ ]]; then
    printf '%s must be exactly 64 lowercase hexadecimal characters\n' "$name" >&2
    return 64
  fi
}

require_renderer_commit_sha() {
  local name=${1:?revision name is required}
  local value=${2:-}
  if [[ ! "$value" =~ ^[0-9a-f]{40}$ ]]; then
    printf '%s must be exactly 40 lowercase hexadecimal characters\n' \
      "$name" >&2
    return 64
  fi
}

echo_pronunciation_source_id() {
  local source_sha=${1:?source sha is required}
  require_renderer_commit_sha ECHO_SOURCE_SHA "$source_sha" || return $?
  printf '%s\n' "$source_sha"
}

echo_pronunciation_run_id() {
  local epub_sha=${1:?epub sha is required}
  local cli_sha=${2:?cli sha is required}
  local resources_sha=${3:?resources sha is required}
  local manifest_sha=${4:?manifest sha is required}
  local source_id=${5:?source id is required}
  local voice=${6:?voice is required}
  printf '%s-%s-%s-%s-%s-%s\n' \
    "${epub_sha:0:12}" "${cli_sha:0:12}" "${resources_sha:0:12}" \
    "${manifest_sha:0:12}" "$source_id" "$voice"
}

echo_pronunciation_renderer_required() {
  local required
  for required in \
    ECHO_RENDERER_ROOT ECHO_RENDERER_BUILD_ROOT ECHO_RENDERER_MANIFEST \
    ECHO_RENDERER_MANIFEST_SHA256 APPROVED_ECHO_INSTALLER_SHA ECHO_SOURCE_SHA \
    CLI ECHO_CLI_SHA256 ECHO_RESOURCE_DIR ECHO_RESOURCES_SHA256 \
    ECHO_RENDER_VERSION ECHO_MODEL_REVISION ECHO_MODEL_EXPECTED_BYTES \
    ECHO_MODEL_BYTES_ATTESTED; do
    if [[ -z ${!required:-} ]]; then
      printf 'installed renderer identity is missing: %s\n' "$required" >&2
      return 64
    fi
    if [[ ${!required} == *$'\n'* || ${!required} == *$'\r'* ]]; then
      printf 'installed renderer identity contains a line break: %s\n' \
        "$required" >&2
      return 64
    fi
  done
}

echo_pronunciation_resolve_installed_renderer() {
  local resume=${1:-0}
  local resume_state=${2:-}
  local requested_source_sha requested_renderer_root renderer_output
  local script_dir
  script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
  if [[ -z ${APPROVED_ECHO_PRONUNCIATION_SHA:-} ]]; then
    printf 'APPROVED_ECHO_PRONUNCIATION_SHA is required for operational narration\n' >&2
    return 64
  fi
  requested_source_sha=$APPROVED_ECHO_PRONUNCIATION_SHA
  require_renderer_commit_sha APPROVED_ECHO_PRONUNCIATION_SHA \
    "$requested_source_sha" || return $?
  if [[ -n ${ECHO_SOURCE_SHA:-} \
    && "$requested_source_sha" != "$ECHO_SOURCE_SHA" ]]; then
    printf 'approved and requested Echo source revisions disagree\n' >&2
    return 64
  fi
  requested_renderer_root=${ECHO_RENDERER_ROOT:-}
  renderer_output=$(mktemp "${TMPDIR:-/tmp}/echo-installed-renderer.XXXXXX") \
    || return 70

  local resolver_command=(
    /usr/local/bin/python3 "$script_dir/echo_installed_renderer.py"
  )
  if (( resume )); then
    resolver_command+=(
      resolve-resume
      --source-sha "$requested_source_sha"
      --resume-state "$resume_state"
    )
  else
    resolver_command+=(resolve-new --source-sha "$requested_source_sha")
  fi
  if [[ -n "$requested_renderer_root" ]]; then
    resolver_command+=(--renderer-root "$requested_renderer_root")
  fi
  resolver_command+=(--format env0)
  if ! "${resolver_command[@]}" >"$renderer_output"; then
    printf 'installed Echo renderer %s is unavailable; install the approved Echo renderer for this exact source, then retry\n' \
      "$requested_source_sha" >&2
    rm -f -- "$renderer_output"
    return 65
  fi

  unset ECHO_RENDERER_ROOT ECHO_RENDERER_BUILD_ROOT ECHO_RENDERER_MANIFEST
  unset ECHO_RENDERER_MANIFEST_SHA256 APPROVED_ECHO_INSTALLER_SHA
  unset ECHO_SOURCE_SHA CLI ECHO_CLI_SHA256 ECHO_RESOURCE_DIR
  unset ECHO_RESOURCES_SHA256 ECHO_RENDER_VERSION ECHO_MODEL_REVISION
  unset ECHO_MODEL_EXPECTED_BYTES ECHO_MODEL_BYTES_ATTESTED
  local renderer_count_root=0 renderer_count_build_root=0
  local renderer_count_manifest=0 renderer_count_manifest_sha=0
  local renderer_count_installer_sha=0 renderer_count_source_sha=0
  local renderer_count_cli=0 renderer_count_cli_sha=0
  local renderer_count_resources=0 renderer_count_resources_sha=0
  local renderer_count_version=0 renderer_count_model_revision=0
  local renderer_count_model_bytes=0 renderer_count_model_attested=0
  local renderer_key renderer_value
  while :; do
    renderer_key=
    if ! IFS= read -r -d '' renderer_key; then
      if [[ -n "$renderer_key" ]]; then
        printf 'incomplete installed renderer env0 record\n' >&2
        rm -f -- "$renderer_output"
        return 65
      fi
      break
    fi
    renderer_value=
    if ! IFS= read -r -d '' renderer_value; then
      printf 'incomplete installed renderer env0 record\n' >&2
      rm -f -- "$renderer_output"
      return 65
    fi
    if [[ "$renderer_value" == *$'\n'* || "$renderer_value" == *$'\r'* ]]; then
      printf 'installed renderer env0 contains a line break: %s\n' \
        "$renderer_key" >&2
      rm -f -- "$renderer_output"
      return 65
    fi
    case "$renderer_key" in
      ECHO_RENDERER_ROOT)
        (( renderer_count_root += 1 ))
        ECHO_RENDERER_ROOT=$renderer_value
        ;;
      ECHO_RENDERER_BUILD_ROOT)
        (( renderer_count_build_root += 1 ))
        ECHO_RENDERER_BUILD_ROOT=$renderer_value
        ;;
      ECHO_RENDERER_MANIFEST)
        (( renderer_count_manifest += 1 ))
        ECHO_RENDERER_MANIFEST=$renderer_value
        ;;
      ECHO_RENDERER_MANIFEST_SHA256)
        (( renderer_count_manifest_sha += 1 ))
        ECHO_RENDERER_MANIFEST_SHA256=$renderer_value
        ;;
      APPROVED_ECHO_INSTALLER_SHA)
        (( renderer_count_installer_sha += 1 ))
        APPROVED_ECHO_INSTALLER_SHA=$renderer_value
        ;;
      ECHO_SOURCE_SHA)
        (( renderer_count_source_sha += 1 ))
        ECHO_SOURCE_SHA=$renderer_value
        ;;
      CLI)
        (( renderer_count_cli += 1 ))
        CLI=$renderer_value
        ;;
      ECHO_CLI_SHA256)
        (( renderer_count_cli_sha += 1 ))
        ECHO_CLI_SHA256=$renderer_value
        ;;
      ECHO_RESOURCE_DIR)
        (( renderer_count_resources += 1 ))
        ECHO_RESOURCE_DIR=$renderer_value
        ;;
      ECHO_RESOURCES_SHA256)
        (( renderer_count_resources_sha += 1 ))
        ECHO_RESOURCES_SHA256=$renderer_value
        ;;
      ECHO_RENDER_VERSION)
        (( renderer_count_version += 1 ))
        ECHO_RENDER_VERSION=$renderer_value
        ;;
      ECHO_MODEL_REVISION)
        (( renderer_count_model_revision += 1 ))
        ECHO_MODEL_REVISION=$renderer_value
        ;;
      ECHO_MODEL_EXPECTED_BYTES)
        (( renderer_count_model_bytes += 1 ))
        ECHO_MODEL_EXPECTED_BYTES=$renderer_value
        ;;
      ECHO_MODEL_BYTES_ATTESTED)
        (( renderer_count_model_attested += 1 ))
        ECHO_MODEL_BYTES_ATTESTED=$renderer_value
        ;;
      *)
        printf 'installed renderer env0 contains an unknown key: %s\n' \
          "$renderer_key" >&2
        rm -f -- "$renderer_output"
        return 65
        ;;
    esac
  done <"$renderer_output"
  rm -f -- "$renderer_output"
  local renderer_count
  for renderer_count in \
    renderer_count_root renderer_count_build_root renderer_count_manifest \
    renderer_count_manifest_sha renderer_count_installer_sha \
    renderer_count_source_sha renderer_count_cli renderer_count_cli_sha \
    renderer_count_resources renderer_count_resources_sha \
    renderer_count_version renderer_count_model_revision \
    renderer_count_model_bytes renderer_count_model_attested; do
    if [[ ${!renderer_count} -ne 1 ]]; then
      printf 'installed renderer env0 key count is not exactly one: %s=%s\n' \
        "$renderer_count" "${!renderer_count}" >&2
      return 65
    fi
  done
  export ECHO_RENDERER_ROOT ECHO_RENDERER_BUILD_ROOT ECHO_RENDERER_MANIFEST
  export ECHO_RENDERER_MANIFEST_SHA256 APPROVED_ECHO_INSTALLER_SHA
  export ECHO_SOURCE_SHA CLI ECHO_CLI_SHA256 ECHO_RESOURCE_DIR
  export ECHO_RESOURCES_SHA256 ECHO_RENDER_VERSION ECHO_MODEL_REVISION
  export ECHO_MODEL_EXPECTED_BYTES ECHO_MODEL_BYTES_ATTESTED
}

echo_pronunciation_assert_leases() {
  local script_dir lease_root
  script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
  lease_root=$(echo_pronunciation_canonical_lease_root) || return $?
  local command=(
    "$script_dir/echo_pronunciation_lease.py"
    --assert-held
    --lock-root "$lease_root"
  )
  local resource
  for resource in "$@"; do
    command+=(--resource "$resource")
  done
  if ! "${command[@]}" >/dev/null; then
    printf 'internal narration mode requires an inherited FD-backed lease capability\n' >&2
    return 70
  fi
}

echo_pronunciation_validate_renderer_paths() {
  local renderer_path
  for renderer_path in "$ECHO_RENDERER_ROOT" "$ECHO_RENDERER_BUILD_ROOT"; do
    if [[ "$renderer_path" != /* || -L "$renderer_path" \
      || ! -d "$renderer_path" \
      || "$(cd -- "$renderer_path" && pwd -P)" != "$renderer_path" ]]; then
      printf 'installed renderer path is not canonical: %s\n' "$renderer_path" >&2
      return 64
    fi
  done
  if [[ "$ECHO_RENDERER_BUILD_ROOT" \
      != "$ECHO_RENDERER_ROOT/$ECHO_SOURCE_SHA/$ECHO_RENDERER_MANIFEST_SHA256" \
    || "$ECHO_RENDERER_MANIFEST" \
      != "$ECHO_RENDERER_BUILD_ROOT/renderer-manifest.json" \
    || "$CLI" != "$ECHO_RENDERER_BUILD_ROOT/echo-cli" \
    || "$ECHO_RESOURCE_DIR" \
      != "$ECHO_RENDERER_BUILD_ROOT/EchoNarrationResources" ]]; then
    printf 'installed renderer paths do not match the sealed package identity\n' >&2
    return 64
  fi
  if [[ -L "$ECHO_RENDERER_MANIFEST" || ! -f "$ECHO_RENDERER_MANIFEST" \
    || -L "$CLI" || ! -x "$CLI" \
    || -L "$ECHO_RESOURCE_DIR" || ! -d "$ECHO_RESOURCE_DIR" ]]; then
    printf 'installed renderer package paths are missing or unsafe\n' >&2
    return 65
  fi
  require_renderer_commit_sha APPROVED_ECHO_INSTALLER_SHA \
    "$APPROVED_ECHO_INSTALLER_SHA" || return $?
  require_renderer_commit_sha ECHO_SOURCE_SHA "$ECHO_SOURCE_SHA" || return $?
  require_sha256 ECHO_RENDERER_MANIFEST_SHA256 \
    "$ECHO_RENDERER_MANIFEST_SHA256" || return $?
  require_sha256 ECHO_CLI_SHA256 "$ECHO_CLI_SHA256" || return $?
  require_sha256 ECHO_RESOURCES_SHA256 "$ECHO_RESOURCES_SHA256" || return $?
  if [[ ! "$ECHO_RENDER_VERSION" =~ ^[1-9][0-9]*$ \
    || ! "$ECHO_MODEL_EXPECTED_BYTES" =~ ^[1-9][0-9]*$ \
    || "$ECHO_MODEL_BYTES_ATTESTED" != false ]]; then
    printf 'installed renderer version or model policy identity is invalid\n' >&2
    return 64
  fi
  if (( ECHO_RENDER_VERSION < 12 )); then
    printf 'installed renderer render version must be at least 12\n' >&2
    return 64
  fi
}

echo_pronunciation_attest_renderer() {
  local script_dir resolver
  script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
  resolver="$script_dir/echo_installed_renderer.py"
  if ! ECHO_RESOURCE_DIR="$ECHO_RESOURCE_DIR" \
    /usr/local/bin/python3 "$resolver" attest \
      --source-sha "$ECHO_SOURCE_SHA" \
      --manifest-sha "$ECHO_RENDERER_MANIFEST_SHA256" \
      --renderer-root "$ECHO_RENDERER_ROOT"; then
    printf 'installed renderer attestation failed for %s/%s\n' \
      "$ECHO_SOURCE_SHA" "$ECHO_RENDERER_MANIFEST_SHA256" >&2
    return 65
  fi
}

echo_pronunciation_renderer_receipt_text() {
  printf '%s\n' \
    'renderer_schema_version=1' \
    "renderer_root=$ECHO_RENDERER_ROOT" \
    "renderer_build_root=$ECHO_RENDERER_BUILD_ROOT" \
    "installer_source_sha=$APPROVED_ECHO_INSTALLER_SHA" \
    "approved_echo_pronunciation_sha=$APPROVED_ECHO_PRONUNCIATION_SHA" \
    "echo_source_sha=$ECHO_SOURCE_SHA" \
    "renderer_manifest_sha256=$ECHO_RENDERER_MANIFEST_SHA256" \
    "echo_cli_sha256=$ECHO_CLI_SHA256" \
    "echo_cli_path=$CLI" \
    "echo_resources_sha256=$ECHO_RESOURCES_SHA256" \
    "echo_resource_dir=$ECHO_RESOURCE_DIR" \
    "render_version=$ECHO_RENDER_VERSION" \
    "model_policy_revision=$ECHO_MODEL_REVISION" \
    "model_expected_byte_count=$ECHO_MODEL_EXPECTED_BYTES" \
    'model_bytes_attested=false' \
    "voice=$VOICE" \
    "chapter_voices=$CHAPTER_VOICES_CANONICAL" \
    "voice_plan_sha256=$VOICE_PLAN_SHA256" \
    "voice_plan_id=$VOICE_PLAN_ID"
}

echo_pronunciation_receipt_text() {
  echo_pronunciation_renderer_receipt_text
  printf '%s\n' \
    "epub_sha256=$EPUB_SHA256" \
    "cover_binding_mode=$COVER_BINDING_MODE" \
    "cover_selection_path=$COVER_SELECTION" \
    "cover_selection_sha256=$COVER_SELECTION_SHA256" \
    "portrait_cover_path=$COVER" \
    "portrait_cover_sha256=$COVER_SHA256" \
    "m4b_cover_path=$M4B_COVER" \
    "m4b_cover_sha256=$M4B_COVER_SHA256" \
    "package_sha256=$PACKAGE_SHA256" \
    "run_id=$RUN_ID" \
    "work_dir=$WORK" \
    "narration_db=$DB"
}

echo_pronunciation_preflight() {
  local original_pwd=$PWD
  local script_dir state_helper lease_helper cover_helper explainer_root lease_root
  script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
  state_helper="$script_dir/echo_pronunciation_state.py"
  lease_helper="$script_dir/echo_pronunciation_lease.py"
  cover_helper="$script_dir/../../../skill/scripts/cover_receipts.py"
  explainer_root=${EXPLAINER_ROOT:-$(cd -- "$script_dir/../../.." && pwd -P)}
  lease_root=$(echo_pronunciation_canonical_lease_root) || return $?
  explainer_root=$(cd -- "$explainer_root" 2>/dev/null && pwd -P) || {
    printf 'cannot resolve explainer-audiobooks repository: %s\n' \
      "$explainer_root" >&2
    return 66
  }

  echo_pronunciation_renderer_required || return $?
  echo_pronunciation_validate_renderer_paths || return $?
  if ! "$lease_helper" --assert-held --lock-root "$lease_root" \
    --resource "$ECHO_RENDERER_BUILD_ROOT" >/dev/null 2>&1; then
    printf 'Echo pronunciation preflight requires the inherited renderer lease\n' >&2
    return 70
  fi
  echo_pronunciation_attest_renderer || return $?

  local approved_input=${APPROVED_ECHO_PRONUNCIATION_SHA:-}
  if [[ -z "$approved_input" ]]; then
    printf 'APPROVED_ECHO_PRONUNCIATION_SHA is required for operational narration\n' >&2
    return 64
  fi
  require_renderer_commit_sha APPROVED_ECHO_PRONUNCIATION_SHA \
    "$approved_input" || return $?
  if [[ "$approved_input" != "$ECHO_SOURCE_SHA" ]]; then
    printf 'approved Echo pronunciation revision %s must exactly equal installed source %s\n' \
      "$approved_input" "$ECHO_SOURCE_SHA" >&2
    return 65
  fi
  APPROVED_ECHO_PRONUNCIATION_SHA=$approved_input

  if [[ ! ${SLUG:-} =~ ^[a-z0-9][a-z0-9-]*$ ]]; then
    printf 'SLUG must use lowercase letters, digits, and internal hyphens only\n' >&2
    return 64
  fi
  if [[ -z ${RUN_ROOT:-} || "$RUN_ROOT" != /* ]]; then
    printf 'RUN_ROOT must be a nonempty absolute explainer-audiobooks run path\n' >&2
    return 64
  fi
  local expected_run_root canonical_run_root
  expected_run_root="$explainer_root/.build/custom-learning-audiobooks/$SLUG"
  canonical_run_root=$(cd -- "$RUN_ROOT" 2>/dev/null && pwd -P) \
    || canonical_run_root=
  if [[ "$canonical_run_root" != "$expected_run_root" ]]; then
    printf 'RUN_ROOT must equal the canonical run path: %s\n' \
      "$expected_run_root" >&2
    return 64
  fi
  local governed_path
  for governed_path in \
    "$RUN_ROOT" "$RUN_ROOT/dist" "$RUN_ROOT/research" \
    "$RUN_ROOT/dist/$SLUG.epub"; do
    if [[ -L "$governed_path" ]]; then
      printf 'governed narration path must not be a symlink: %s\n' \
        "$governed_path" >&2
      return 65
    fi
  done

  EPUB="$RUN_ROOT/dist/$SLUG.epub"
  if [[ -L "$EPUB" || ! -f "$EPUB" ]]; then
    printf 'source EPUB is missing: %s\n' "$EPUB" >&2
    return 66
  fi
  if [[ -z ${COVER:-} || -z ${M4B_COVER:-} ]]; then
    printf 'COVER and M4B_COVER are required for governed paired-cover narration\n' >&2
    return 64
  fi
  local selected_pair_dir=${COVER%/*}
  if [[ "$COVER" != /* || "$M4B_COVER" != /* \
    || ! "$selected_pair_dir" =~ ^$RUN_ROOT/dist/candidate-[123]$ \
    || "$COVER" != "$selected_pair_dir/cover.png" \
    || "$M4B_COVER" != "$selected_pair_dir/m4b-cover.png" ]]; then
    printf 'COVER and M4B_COVER must identify one canonical candidate pair\n' >&2
    return 64
  fi
  COVER_SELECTION="$selected_pair_dir/cover-selection.json"
  if [[ -e "$COVER_SELECTION" || -L "$COVER_SELECTION" ]]; then
    COVER_BINDING_MODE=paired-receipt
  else
    COVER_BINDING_MODE=receipt-free-private
    COVER_SELECTION=
  fi
  local cover_input
  for cover_input in "$COVER" "$M4B_COVER"; do
    if [[ -L "$cover_input" || ! -f "$cover_input" ]]; then
      printf 'governed paired-cover input is missing or unsafe: %s\n' \
        "$cover_input" >&2
      return 66
    fi
  done
  if [[ "$COVER_BINDING_MODE" == paired-receipt ]]; then
    if [[ -L "$COVER_SELECTION" || ! -f "$COVER_SELECTION" ]]; then
      printf 'governed paired-cover input is missing or unsafe: %s\n' \
        "$COVER_SELECTION" >&2
      return 66
    fi
    if ! /usr/local/bin/python3 "$cover_helper" verify \
      --selection "$COVER_SELECTION" --cover "$COVER" \
      --m4b-cover "$M4B_COVER" --epub "$EPUB" >/dev/null; then
      printf 'selected cover pair does not match its receipt or EPUB\n' >&2
      return 65
    fi
  elif ! /usr/local/bin/python3 "$cover_helper" verify-receipt-free-pair \
    --cover "$COVER" --m4b-cover "$M4B_COVER" --epub "$EPUB" >/dev/null; then
    printf 'selected cover pair does not match its receipt or EPUB\n' >&2
    return 65
  fi

  EPUB_SHA256=$(/usr/bin/shasum -a 256 "$EPUB" | awk '{print $1}')
  COVER_SELECTION_SHA256=
  if [[ "$COVER_BINDING_MODE" == paired-receipt ]]; then
    COVER_SELECTION_SHA256=$(/usr/bin/shasum -a 256 "$COVER_SELECTION" | awk '{print $1}')
  fi
  COVER_SHA256=$(/usr/bin/shasum -a 256 "$COVER" | awk '{print $1}')
  M4B_COVER_SHA256=$(/usr/bin/shasum -a 256 "$M4B_COVER" | awk '{print $1}')
  local hash_name
  for hash_name in \
    EPUB_SHA256 COVER_SHA256 M4B_COVER_SHA256; do
    require_sha256 "$hash_name" "${!hash_name}" || return $?
  done
  if [[ "$COVER_BINDING_MODE" == paired-receipt ]]; then
    require_sha256 COVER_SELECTION_SHA256 "$COVER_SELECTION_SHA256" || return $?
  fi
  PACKAGE_SHA256=$(printf '%s\n' \
    "epub=$EPUB_SHA256" \
    "cover_selection=${COVER_SELECTION_SHA256:-receipt-free-private}" \
    "portrait_cover=$COVER_SHA256" \
    "square_cover=$M4B_COVER_SHA256" \
    | /usr/bin/shasum -a 256 | awk '{print $1}')
  require_sha256 PACKAGE_SHA256 "$PACKAGE_SHA256" || return $?

  VOICE=${VOICE:-am_michael}
  local voice_plan_helper voice_plan_output voice_plan_key voice_plan_value
  local voice_plan_count_voice=0 voice_plan_count_chapters=0
  local voice_plan_count_sha=0 voice_plan_count_id=0
  voice_plan_helper="$script_dir/echo_voice_plan.py"
  voice_plan_output=$(mktemp "${TMPDIR:-/tmp}/echo-voice-plan.XXXXXX") \
    || return 70
  local voice_plan_command=(
    /usr/local/bin/python3 "$voice_plan_helper"
    --default-voice "$VOICE"
    --format env0
  )
  local chapter_voice
  for chapter_voice in "${CHAPTER_VOICES[@]:-}"; do
    [[ -z "$chapter_voice" ]] || voice_plan_command+=(--chapter-voice "$chapter_voice")
  done
  if ! "${voice_plan_command[@]}" >"$voice_plan_output"; then
    rm -f -- "$voice_plan_output"
    return 64
  fi
  unset CHAPTER_VOICES_CANONICAL VOICE_PLAN_SHA256 VOICE_PLAN_ID
  while :; do
    voice_plan_key=
    if ! IFS= read -r -d '' voice_plan_key; then
      [[ -z "$voice_plan_key" ]] || {
        printf 'incomplete Echo voice-plan env0 record\n' >&2
        rm -f -- "$voice_plan_output"
        return 65
      }
      break
    fi
    voice_plan_value=
    if ! IFS= read -r -d '' voice_plan_value; then
      printf 'incomplete Echo voice-plan env0 record\n' >&2
      rm -f -- "$voice_plan_output"
      return 65
    fi
    case "$voice_plan_key" in
      VOICE)
        (( voice_plan_count_voice += 1 ))
        VOICE=$voice_plan_value
        ;;
      CHAPTER_VOICES_CANONICAL)
        (( voice_plan_count_chapters += 1 ))
        CHAPTER_VOICES_CANONICAL=$voice_plan_value
        ;;
      VOICE_PLAN_SHA256)
        (( voice_plan_count_sha += 1 ))
        VOICE_PLAN_SHA256=$voice_plan_value
        ;;
      VOICE_PLAN_ID)
        (( voice_plan_count_id += 1 ))
        VOICE_PLAN_ID=$voice_plan_value
        ;;
      *)
        printf 'unknown Echo voice-plan env0 key: %s\n' "$voice_plan_key" >&2
        rm -f -- "$voice_plan_output"
        return 65
        ;;
    esac
  done <"$voice_plan_output"
  rm -f -- "$voice_plan_output"
  if (( voice_plan_count_voice != 1 || voice_plan_count_chapters != 1 \
    || voice_plan_count_sha != 1 || voice_plan_count_id != 1 )); then
    printf 'Echo voice-plan env0 record is incomplete or duplicated\n' >&2
    return 65
  fi
  local echo_source_id
  echo_source_id=$(echo_pronunciation_source_id "$ECHO_SOURCE_SHA")
  RUN_ID=$(echo_pronunciation_run_id \
    "$EPUB_SHA256" "$ECHO_CLI_SHA256" "$ECHO_RESOURCES_SHA256" \
    "$ECHO_RENDERER_MANIFEST_SHA256" "$echo_source_id" "$VOICE_PLAN_ID")
  WORK="$RUN_ROOT/audio-work-$RUN_ID"
  DB="$RUN_ROOT/narration-$RUN_ID.sqlite"
  mkdir -p "$RUN_ROOT/research"
  ECHO_RENDER_INPUT_RECEIPT="$RUN_ROOT/research/echo-render-inputs-$RUN_ID.env"
  local receipt_text
  receipt_text=$(echo_pronunciation_receipt_text)
  if [[ -L "$ECHO_RENDER_INPUT_RECEIPT" ]]; then
    printf 'render-input receipt must not be a symlink: %s\n' \
      "$ECHO_RENDER_INPUT_RECEIPT" >&2
    return 65
  fi
  if [[ -e "$ECHO_RENDER_INPUT_RECEIPT" ]]; then
    local actual_receipt
    actual_receipt=$(<"$ECHO_RENDER_INPUT_RECEIPT")
    if [[ "$receipt_text" != "$actual_receipt" ]]; then
      printf 'existing render-input receipt does not match immutable inputs: %s\n' \
        "$ECHO_RENDER_INPUT_RECEIPT" >&2
      return 65
    fi
  else
    if [[ -e "$WORK" || -L "$WORK" || -e "$DB" || -L "$DB" ]]; then
      printf 'pre-existing WORK or DB requires a matching receipt: %s\n' \
        "$RUN_ID" >&2
      return 65
    fi
    if ! printf '%s\n' "$receipt_text" \
      | /usr/local/bin/python3 "$state_helper" immutable-file \
        "$ECHO_RENDER_INPUT_RECEIPT"; then
      printf 'could not create immutable render-input receipt: %s\n' \
        "$ECHO_RENDER_INPUT_RECEIPT" >&2
      return 65
    fi
  fi
  if [[ "$PWD" != "$original_pwd" ]]; then
    printf 'Echo preflight changed cwd from %s to %s\n' \
      "$original_pwd" "$PWD" >&2
    return 70
  fi

  EXPLAINER_ROOT=$explainer_root
  export EXPLAINER_ROOT APPROVED_ECHO_PRONUNCIATION_SHA
  export ECHO_SOURCE_SHA EPUB EPUB_SHA256
  export COVER_BINDING_MODE COVER_SELECTION COVER_SELECTION_SHA256 COVER COVER_SHA256
  export M4B_COVER M4B_COVER_SHA256 PACKAGE_SHA256
  export CLI ECHO_CLI_SHA256 ECHO_RESOURCE_DIR ECHO_RESOURCES_SHA256
  export ECHO_RENDERER_ROOT ECHO_RENDERER_BUILD_ROOT ECHO_RENDERER_MANIFEST
  export ECHO_RENDERER_MANIFEST_SHA256 APPROVED_ECHO_INSTALLER_SHA
  export ECHO_MODEL_REVISION ECHO_MODEL_EXPECTED_BYTES ECHO_MODEL_BYTES_ATTESTED
  export ECHO_RENDER_VERSION VOICE CHAPTER_VOICES_CANONICAL
  export VOICE_PLAN_SHA256 VOICE_PLAN_ID RUN_ID WORK DB ECHO_RENDER_INPUT_RECEIPT
}

echo_pronunciation_attest_inputs() {
  local script_dir lease_helper cover_helper lease_root required
  script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
  lease_helper="$script_dir/echo_pronunciation_lease.py"
  cover_helper="$script_dir/../../../skill/scripts/cover_receipts.py"
  lease_root=$(echo_pronunciation_canonical_lease_root) || return $?
  for required in \
    EXPLAINER_ROOT SLUG RUN_ROOT APPROVED_ECHO_PRONUNCIATION_SHA \
    ECHO_SOURCE_SHA EPUB EPUB_SHA256 COVER_BINDING_MODE \
    COVER COVER_SHA256 M4B_COVER M4B_COVER_SHA256 PACKAGE_SHA256 \
    CLI ECHO_CLI_SHA256 ECHO_RESOURCE_DIR ECHO_RESOURCES_SHA256 \
    ECHO_RENDER_VERSION ECHO_RENDERER_ROOT ECHO_RENDERER_BUILD_ROOT \
    ECHO_RENDERER_MANIFEST ECHO_RENDERER_MANIFEST_SHA256 \
    APPROVED_ECHO_INSTALLER_SHA ECHO_MODEL_REVISION \
    ECHO_MODEL_EXPECTED_BYTES ECHO_MODEL_BYTES_ATTESTED VOICE \
    VOICE_PLAN_SHA256 VOICE_PLAN_ID RUN_ID WORK DB \
    ECHO_RENDER_INPUT_RECEIPT; do
    if [[ -z ${!required:-} ]]; then
      printf 'sealed preflight state is missing: %s\n' "$required" >&2
      return 70
    fi
    if [[ ${!required} == *$'\n'* || ${!required} == *$'\r'* ]]; then
      printf 'sealed preflight state contains a line break: %s\n' "$required" >&2
      return 64
    fi
  done
  if [[ ${CHAPTER_VOICES_CANONICAL+x} != x ]]; then
    printf 'sealed preflight state is missing: CHAPTER_VOICES_CANONICAL\n' >&2
    return 70
  fi
  echo_pronunciation_validate_renderer_paths || return $?
  if ! "$lease_helper" --assert-held --lock-root "$lease_root" \
    --resource "$ECHO_RENDERER_BUILD_ROOT" >/dev/null 2>&1; then
    printf 'Echo input attestation requires the inherited renderer lease\n' >&2
    return 70
  fi
  echo_pronunciation_attest_renderer || return $?

  local canonical_explainer_root canonical_run_root
  canonical_explainer_root=$(cd -- "$EXPLAINER_ROOT" 2>/dev/null && pwd -P) \
    || canonical_explainer_root=
  canonical_run_root=$(cd -- "$RUN_ROOT" 2>/dev/null && pwd -P) \
    || canonical_run_root=
  if [[ "$canonical_explainer_root" != "$EXPLAINER_ROOT" \
    || ! "$SLUG" =~ ^[a-z0-9][a-z0-9-]*$ \
    || "$canonical_run_root" \
      != "$EXPLAINER_ROOT/.build/custom-learning-audiobooks/$SLUG" ]]; then
    printf 'RUN_ROOT and SLUG do not identify the canonical governed run\n' >&2
    return 64
  fi
  if [[ "$APPROVED_ECHO_PRONUNCIATION_SHA" != "$ECHO_SOURCE_SHA" ]]; then
    printf 'approved Echo pronunciation revision does not match installed source\n' >&2
    return 65
  fi
  local voice_plan_helper voice_plan_lines
  voice_plan_helper="$script_dir/echo_voice_plan.py"
  local voice_plan_command=(
    /usr/local/bin/python3 "$voice_plan_helper"
    --default-voice "$VOICE"
  )
  local chapter_voice
  for chapter_voice in "${CHAPTER_VOICES[@]:-}"; do
    [[ -z "$chapter_voice" ]] || voice_plan_command+=(--chapter-voice "$chapter_voice")
  done
  voice_plan_lines=$("${voice_plan_command[@]}") || return $?
  local expected_voice_plan_lines
  expected_voice_plan_lines=$(printf '%s\n' \
    "VOICE=$VOICE" \
    "CHAPTER_VOICES_CANONICAL=$CHAPTER_VOICES_CANONICAL" \
    "VOICE_PLAN_SHA256=$VOICE_PLAN_SHA256" \
    "VOICE_PLAN_ID=$VOICE_PLAN_ID")
  if [[ "$voice_plan_lines" != "$expected_voice_plan_lines" ]]; then
    printf 'sealed chapter-voice plan changed while narration lease was held\n' >&2
    return 65
  fi

  local expected_epub expected_cover_selection selected_pair_dir cover_input
  expected_epub="$RUN_ROOT/dist/$SLUG.epub"
  selected_pair_dir=${COVER%/*}
  expected_cover_selection="$selected_pair_dir/cover-selection.json"
  if [[ "$EPUB" != "$expected_epub" || -L "$EPUB" || ! -f "$EPUB" \
    || "$COVER" != "$selected_pair_dir/cover.png" \
    || "$M4B_COVER" != "$selected_pair_dir/m4b-cover.png" \
    || ! "$selected_pair_dir" =~ ^$RUN_ROOT/dist/candidate-[123]$ ]]; then
    printf 'governed source paths changed while narration lease was held\n' >&2
    return 65
  fi
  for cover_input in "$COVER" "$M4B_COVER"; do
    if [[ -L "$cover_input" || ! -f "$cover_input" ]]; then
      printf 'selected cover input changed while narration lease was held: %s\n' \
        "$cover_input" >&2
      return 65
    fi
  done
  case "$COVER_BINDING_MODE" in
    paired-receipt)
      if [[ "$COVER_SELECTION" != "$expected_cover_selection" \
        || -L "$COVER_SELECTION" || ! -f "$COVER_SELECTION" ]]; then
        printf 'selected cover receipt changed while narration lease was held\n' >&2
        return 65
      fi
      ;;
    receipt-free-private)
      if [[ -n "$COVER_SELECTION" || -n "$COVER_SELECTION_SHA256" ]]; then
        printf 'receipt-free private cover binding unexpectedly names a receipt\n' >&2
        return 65
      fi
      ;;
    *)
      printf 'unknown sealed cover binding mode: %s\n' "$COVER_BINDING_MODE" >&2
      return 65
      ;;
  esac

  local current_epub_sha current_cover_selection_sha current_cover_sha
  local current_m4b_cover_sha current_package_sha
  current_epub_sha=$(/usr/bin/shasum -a 256 "$EPUB" | awk '{print $1}')
  current_cover_selection_sha=
  if [[ "$COVER_BINDING_MODE" == paired-receipt ]]; then
    current_cover_selection_sha=$(/usr/bin/shasum -a 256 "$COVER_SELECTION" | awk '{print $1}')
  fi
  current_cover_sha=$(/usr/bin/shasum -a 256 "$COVER" | awk '{print $1}')
  current_m4b_cover_sha=$(/usr/bin/shasum -a 256 "$M4B_COVER" | awk '{print $1}')
  current_package_sha=$(printf '%s\n' \
    "epub=$current_epub_sha" \
    "cover_selection=${current_cover_selection_sha:-receipt-free-private}" \
    "portrait_cover=$current_cover_sha" \
    "square_cover=$current_m4b_cover_sha" \
    | /usr/bin/shasum -a 256 | awk '{print $1}')
  if [[ "$current_epub_sha" != "$EPUB_SHA256" ]]; then
    printf 'EPUB changed while narration lease was held: %s\n' "$EPUB" >&2
    return 65
  fi
  if [[ "$current_cover_selection_sha" != "$COVER_SELECTION_SHA256" \
    || "$current_cover_sha" != "$COVER_SHA256" \
    || "$current_m4b_cover_sha" != "$M4B_COVER_SHA256" \
    || "$current_package_sha" != "$PACKAGE_SHA256" ]]; then
    printf 'selected cover package changed while narration lease was held\n' >&2
    return 65
  fi
  local cover_verification_failed=0
  if [[ "$COVER_BINDING_MODE" == paired-receipt ]]; then
    /usr/local/bin/python3 "$cover_helper" verify \
      --selection "$COVER_SELECTION" --cover "$COVER" \
      --m4b-cover "$M4B_COVER" --epub "$EPUB" >/dev/null \
      || cover_verification_failed=1
  else
    /usr/local/bin/python3 "$cover_helper" verify-receipt-free-pair \
      --cover "$COVER" --m4b-cover "$M4B_COVER" --epub "$EPUB" >/dev/null \
      || cover_verification_failed=1
  fi
  if (( cover_verification_failed )); then
    printf 'selected cover pair changed while narration lease was held\n' >&2
    return 65
  fi

  local expected_source_id expected_run_id expected_receipt
  expected_source_id=$(echo_pronunciation_source_id "$ECHO_SOURCE_SHA")
  expected_run_id=$(echo_pronunciation_run_id \
    "$EPUB_SHA256" "$ECHO_CLI_SHA256" "$ECHO_RESOURCES_SHA256" \
    "$ECHO_RENDERER_MANIFEST_SHA256" "$expected_source_id" "$VOICE_PLAN_ID")
  expected_receipt="$RUN_ROOT/research/echo-render-inputs-$expected_run_id.env"
  if [[ "$RUN_ID" != "$expected_run_id" \
    || "$WORK" != "$RUN_ROOT/audio-work-$expected_run_id" \
    || "$DB" != "$RUN_ROOT/narration-$expected_run_id.sqlite" \
    || "$ECHO_RENDER_INPUT_RECEIPT" != "$expected_receipt" ]]; then
    printf 'sealed run paths are not derived from the attested inputs\n' >&2
    return 65
  fi
  if [[ -L "$ECHO_RENDER_INPUT_RECEIPT" \
    || ! -f "$ECHO_RENDER_INPUT_RECEIPT" ]]; then
    printf 'receipt changed while narration lease was held: %s\n' \
      "$ECHO_RENDER_INPUT_RECEIPT" >&2
    return 65
  fi
  if [[ $(/usr/bin/stat -f '%Lp' "$ECHO_RENDER_INPUT_RECEIPT") != 600 ]]; then
    printf 'canonical render-input receipt must have mode 600: %s\n' \
      "$ECHO_RENDER_INPUT_RECEIPT" >&2
    return 65
  fi
  local expected_receipt_text actual_receipt_text
  expected_receipt_text=$(echo_pronunciation_receipt_text)
  actual_receipt_text=$(<"$ECHO_RENDER_INPUT_RECEIPT")
  if [[ "$actual_receipt_text" != "$expected_receipt_text" ]]; then
    printf 'receipt changed while narration lease was held: %s\n' \
      "$ECHO_RENDER_INPUT_RECEIPT" >&2
    return 65
  fi
}

if [[ ${BASH_SOURCE[0]} == "$0" ]]; then
  echo_pronunciation_preflight
  printf 'echo_pronunciation_preflight: clean\n'
  printf 'run_id=%s\nreceipt=%s\n' "$RUN_ID" "$ECHO_RENDER_INPUT_RECEIPT"
fi
