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

# Kept for the still-checkout-backed learning pilot until its Task 5 migration.
require_git_commit_sha() {
  local name=${1:?revision name is required}
  local value=${2:-}
  if [[ ! "$value" =~ ^([0-9a-f]{40}|[0-9a-f]{64})$ ]]; then
    printf '%s is not a canonical commit SHA\n' "$name" >&2
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

# The learning-pilot wrapper still sources this shared format validator. Its
# checkout-backed renderer migration is deliberately owned by Task 5.
echo_pronunciation_release_render_version() {
  local cli_version=${1:-}
  local render_version
  if [[ "$cli_version" =~ (^|[[:space:]])rv([0-9]+)[[:space:]]+\(Release\)($|[[:space:]]) ]]; then
    render_version=${BASH_REMATCH[2]}
  else
    return 1
  fi
  render_version=$((10#$render_version))
  if (( render_version < 12 )); then
    return 1
  fi
  printf '%s\n' "$render_version"
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

echo_pronunciation_receipt_text() {
  printf '%s\n' \
    'renderer_schema_version=1' \
    "renderer_root=$ECHO_RENDERER_ROOT" \
    "renderer_build_root=$ECHO_RENDERER_BUILD_ROOT" \
    "installer_source_sha=$APPROVED_ECHO_INSTALLER_SHA" \
    "approved_echo_pronunciation_sha=$APPROVED_ECHO_PRONUNCIATION_SHA" \
    "echo_source_sha=$ECHO_SOURCE_SHA" \
    "renderer_manifest_sha256=$ECHO_RENDERER_MANIFEST_SHA256" \
    "epub_sha256=$EPUB_SHA256" \
    "cover_selection_path=$COVER_SELECTION" \
    "cover_selection_sha256=$COVER_SELECTION_SHA256" \
    "portrait_cover_path=$COVER" \
    "portrait_cover_sha256=$COVER_SHA256" \
    "m4b_cover_path=$M4B_COVER" \
    "m4b_cover_sha256=$M4B_COVER_SHA256" \
    "package_sha256=$PACKAGE_SHA256" \
    "echo_cli_sha256=$ECHO_CLI_SHA256" \
    "echo_cli_path=$CLI" \
    "echo_resources_sha256=$ECHO_RESOURCES_SHA256" \
    "echo_resource_dir=$ECHO_RESOURCE_DIR" \
    "render_version=$ECHO_RENDER_VERSION" \
    "model_policy_revision=$ECHO_MODEL_REVISION" \
    "model_expected_byte_count=$ECHO_MODEL_EXPECTED_BYTES" \
    'model_bytes_attested=false' \
    "voice=$VOICE" \
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
  COVER_SELECTION="$RUN_ROOT/dist/cover-selection.json"
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
  local cover_input
  for cover_input in "$COVER_SELECTION" "$COVER" "$M4B_COVER"; do
    if [[ -L "$cover_input" || ! -f "$cover_input" ]]; then
      printf 'governed paired-cover input is missing or unsafe: %s\n' \
        "$cover_input" >&2
      return 66
    fi
  done
  if ! /usr/local/bin/python3 "$cover_helper" verify \
    --selection "$COVER_SELECTION" --cover "$COVER" \
    --m4b-cover "$M4B_COVER" --epub "$EPUB" >/dev/null; then
    printf 'selected cover pair does not match its receipt or EPUB\n' >&2
    return 65
  fi

  EPUB_SHA256=$(/usr/bin/shasum -a 256 "$EPUB" | awk '{print $1}')
  COVER_SELECTION_SHA256=$(/usr/bin/shasum -a 256 "$COVER_SELECTION" | awk '{print $1}')
  COVER_SHA256=$(/usr/bin/shasum -a 256 "$COVER" | awk '{print $1}')
  M4B_COVER_SHA256=$(/usr/bin/shasum -a 256 "$M4B_COVER" | awk '{print $1}')
  local hash_name
  for hash_name in \
    EPUB_SHA256 COVER_SELECTION_SHA256 COVER_SHA256 M4B_COVER_SHA256; do
    require_sha256 "$hash_name" "${!hash_name}" || return $?
  done
  PACKAGE_SHA256=$(printf '%s\n' \
    "epub=$EPUB_SHA256" \
    "cover_selection=$COVER_SELECTION_SHA256" \
    "portrait_cover=$COVER_SHA256" \
    "square_cover=$M4B_COVER_SHA256" \
    | /usr/bin/shasum -a 256 | awk '{print $1}')
  require_sha256 PACKAGE_SHA256 "$PACKAGE_SHA256" || return $?

  VOICE=${VOICE:-am_michael}
  case "$VOICE" in
    am_michael | am_puck) ;;
    *)
      printf 'VOICE must be am_michael or am_puck, got: %s\n' "$VOICE" >&2
      return 64
      ;;
  esac
  local echo_source_id
  echo_source_id=$(echo_pronunciation_source_id "$ECHO_SOURCE_SHA")
  RUN_ID=$(echo_pronunciation_run_id \
    "$EPUB_SHA256" "$ECHO_CLI_SHA256" "$ECHO_RESOURCES_SHA256" \
    "$ECHO_RENDERER_MANIFEST_SHA256" "$echo_source_id" "$VOICE")
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
  export COVER_SELECTION COVER_SELECTION_SHA256 COVER COVER_SHA256
  export M4B_COVER M4B_COVER_SHA256 PACKAGE_SHA256
  export CLI ECHO_CLI_SHA256 ECHO_RESOURCE_DIR ECHO_RESOURCES_SHA256
  export ECHO_RENDERER_ROOT ECHO_RENDERER_BUILD_ROOT ECHO_RENDERER_MANIFEST
  export ECHO_RENDERER_MANIFEST_SHA256 APPROVED_ECHO_INSTALLER_SHA
  export ECHO_MODEL_REVISION ECHO_MODEL_EXPECTED_BYTES ECHO_MODEL_BYTES_ATTESTED
  export ECHO_RENDER_VERSION VOICE RUN_ID WORK DB ECHO_RENDER_INPUT_RECEIPT
}

echo_pronunciation_attest_inputs() {
  local script_dir lease_helper cover_helper lease_root required
  script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
  lease_helper="$script_dir/echo_pronunciation_lease.py"
  cover_helper="$script_dir/../../../skill/scripts/cover_receipts.py"
  lease_root=$(echo_pronunciation_canonical_lease_root) || return $?
  for required in \
    EXPLAINER_ROOT SLUG RUN_ROOT APPROVED_ECHO_PRONUNCIATION_SHA \
    ECHO_SOURCE_SHA EPUB EPUB_SHA256 COVER_SELECTION COVER_SELECTION_SHA256 \
    COVER COVER_SHA256 M4B_COVER M4B_COVER_SHA256 PACKAGE_SHA256 \
    CLI ECHO_CLI_SHA256 ECHO_RESOURCE_DIR ECHO_RESOURCES_SHA256 \
    ECHO_RENDER_VERSION ECHO_RENDERER_ROOT ECHO_RENDERER_BUILD_ROOT \
    ECHO_RENDERER_MANIFEST ECHO_RENDERER_MANIFEST_SHA256 \
    APPROVED_ECHO_INSTALLER_SHA ECHO_MODEL_REVISION \
    ECHO_MODEL_EXPECTED_BYTES ECHO_MODEL_BYTES_ATTESTED VOICE RUN_ID WORK DB \
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
  case "$VOICE" in
    am_michael | am_puck) ;;
    *)
      printf 'VOICE must be am_michael or am_puck, got: %s\n' "$VOICE" >&2
      return 64
      ;;
  esac

  local expected_epub expected_cover_selection selected_pair_dir cover_input
  expected_epub="$RUN_ROOT/dist/$SLUG.epub"
  expected_cover_selection="$RUN_ROOT/dist/cover-selection.json"
  selected_pair_dir=${COVER%/*}
  if [[ "$EPUB" != "$expected_epub" || -L "$EPUB" || ! -f "$EPUB" \
    || "$COVER_SELECTION" != "$expected_cover_selection" \
    || "$COVER" != "$selected_pair_dir/cover.png" \
    || "$M4B_COVER" != "$selected_pair_dir/m4b-cover.png" \
    || ! "$selected_pair_dir" =~ ^$RUN_ROOT/dist/candidate-[123]$ ]]; then
    printf 'governed source paths changed while narration lease was held\n' >&2
    return 65
  fi
  for cover_input in "$COVER_SELECTION" "$COVER" "$M4B_COVER"; do
    if [[ -L "$cover_input" || ! -f "$cover_input" ]]; then
      printf 'selected cover input changed while narration lease was held: %s\n' \
        "$cover_input" >&2
      return 65
    fi
  done

  local current_epub_sha current_cover_selection_sha current_cover_sha
  local current_m4b_cover_sha current_package_sha
  current_epub_sha=$(/usr/bin/shasum -a 256 "$EPUB" | awk '{print $1}')
  current_cover_selection_sha=$(/usr/bin/shasum -a 256 "$COVER_SELECTION" | awk '{print $1}')
  current_cover_sha=$(/usr/bin/shasum -a 256 "$COVER" | awk '{print $1}')
  current_m4b_cover_sha=$(/usr/bin/shasum -a 256 "$M4B_COVER" | awk '{print $1}')
  current_package_sha=$(printf '%s\n' \
    "epub=$current_epub_sha" \
    "cover_selection=$current_cover_selection_sha" \
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
  if ! /usr/local/bin/python3 "$cover_helper" verify \
    --selection "$COVER_SELECTION" --cover "$COVER" \
    --m4b-cover "$M4B_COVER" --epub "$EPUB" >/dev/null; then
    printf 'selected cover pair changed while narration lease was held\n' >&2
    return 65
  fi

  local expected_source_id expected_run_id expected_receipt
  expected_source_id=$(echo_pronunciation_source_id "$ECHO_SOURCE_SHA")
  expected_run_id=$(echo_pronunciation_run_id \
    "$EPUB_SHA256" "$ECHO_CLI_SHA256" "$ECHO_RESOURCES_SHA256" \
    "$ECHO_RENDERER_MANIFEST_SHA256" "$expected_source_id" "$VOICE")
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
