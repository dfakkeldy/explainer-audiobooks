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

require_git_commit_sha() {
  local name=${1:?revision name is required}
  local value=${2:-}
  if [[ ! "$value" =~ ^([0-9a-f]{40}|[0-9a-f]{64})$ ]]; then
    printf '%s is not a canonical Git commit SHA\n' "$name" >&2
    return 64
  fi
}

# The renderer's identity leg of RUN_ID. Derived in exactly one place so the
# preflight and the attestation cannot drift apart: computing it twice is what
# let them disagree when the source leg changed.
echo_pronunciation_source_id() {
  local source_sha=${1:?source sha is required}
  local tree_state=${2:?tree state is required}
  local tree_diff=${3:-}
  if [[ "$tree_state" == clean ]]; then
    printf '%s\n' "$source_sha"
  else
    printf '%s-dirty-%s\n' "$source_sha" "${tree_diff:0:8}"
  fi
}

echo_pronunciation_run_id() {
  local package_sha=${1:?package sha is required}
  local cli_sha=${2:?cli sha is required}
  local resources_sha=${3:?resources sha is required}
  local source_id=${4:?source id is required}
  local voice=${5:?voice is required}
  printf '%s-%s-%s-%s-%s\n' \
    "${package_sha:0:12}" "${cli_sha:0:12}" "${resources_sha:0:12}" \
    "$source_id" "$voice"
}

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

echo_pronunciation_preflight() {
  local original_pwd=$PWD
  local echo_repo=${ECHO_REPO:-/Users/dfakkeldy/Developer/Echo}
  local script_dir
  script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
  local state_helper="$script_dir/echo_pronunciation_state.py"
  local lease_helper="$script_dir/echo_pronunciation_lease.py"
  local cover_helper="$script_dir/../../../skill/scripts/cover_receipts.py"
  local explainer_root=${EXPLAINER_ROOT:-$(cd -- "$script_dir/../../.." && pwd -P)}
  local build_gate=${ECHO_BUILD_GATE:-$HOME/.claude/bin/xcode-build-gate.sh}
  local lease_root
  lease_root=$(echo_pronunciation_canonical_lease_root) || return $?
  echo_repo=$(cd -- "$echo_repo" 2>/dev/null && pwd -P) || {
    printf 'cannot resolve Echo repository: %s\n' "$echo_repo" >&2
    return 66
  }
  explainer_root=$(cd -- "$explainer_root" 2>/dev/null && pwd -P) || {
    printf 'cannot resolve explainer-audiobooks repository: %s\n' \
      "$explainer_root" >&2
    return 66
  }
  local build_resource="$echo_repo/.build/cli"
  local approved_input=${APPROVED_ECHO_PRONUNCIATION_SHA:-}

  if ! "$lease_helper" --assert-held --lock-root "$lease_root" \
    --resource "$build_resource" >/dev/null 2>&1; then
    printf 'Echo pronunciation preflight requires the inherited build lease\n' >&2
    return 70
  fi

  if [[ ! ${SLUG:-} =~ ^[a-z0-9][a-z0-9-]*$ ]]; then
    printf 'SLUG must use lowercase letters, digits, and internal hyphens only\n' >&2
    return 64
  fi
  if [[ -z ${RUN_ROOT:-} || "$RUN_ROOT" != /* ]]; then
    printf 'RUN_ROOT must be a nonempty absolute explainer-audiobooks run path\n' >&2
    return 64
  fi
  local canonical_explainer_root expected_run_root
  canonical_explainer_root=$explainer_root
  expected_run_root="$canonical_explainer_root/.build/custom-learning-audiobooks/$SLUG"
  local canonical_run_root
  canonical_run_root=$(cd -- "$RUN_ROOT" 2>/dev/null && pwd -P) || canonical_run_root=
  if [[ "$canonical_run_root" != "$expected_run_root" ]]; then
    printf 'RUN_ROOT must equal the canonical run path: %s\n' "$expected_run_root" >&2
    return 64
  fi
  for governed_path in \
    "$RUN_ROOT" "$RUN_ROOT/dist" "$RUN_ROOT/research" \
    "$RUN_ROOT/dist/$SLUG.epub"; do
    if [[ -L "$governed_path" ]]; then
      printf 'governed narration path must not be a symlink: %s\n' "$governed_path" >&2
      return 65
    fi
  done
  if [[ ! -x "$build_gate" ]]; then
    printf 'Echo build gate is missing or not executable: %s\n' "$build_gate" >&2
    return 66
  fi

  # The authoritative identity of the renderer that produces the audio is
  # ECHO_CLI_SHA256 plus ECHO_RESOURCES_SHA256, computed below from the actual
  # built binary and its resource tree. The Git revision is a convenience label
  # for those, so it is recorded rather than gated on: a dirty tree is described
  # honestly instead of blocking the render.
  if ! ECHO_SOURCE_SHA=$(git -C "$echo_repo" rev-parse HEAD); then
    printf 'cannot resolve Echo source revision at %s\n' "$echo_repo" >&2
    return 65
  fi
  require_git_commit_sha ECHO_SOURCE_SHA "$ECHO_SOURCE_SHA"

  local echo_status
  echo_status=$(git -C "$echo_repo" status --porcelain --untracked-files=all)
  if [[ -z "$echo_status" ]]; then
    ECHO_TREE_STATE=clean
    ECHO_TREE_DIFF_SHA256=$(printf '' | /usr/bin/shasum -a 256 | cut -d' ' -f1)
  else
    ECHO_TREE_STATE=dirty
    # Fingerprint the exact deviation from HEAD so the receipt still identifies
    # the built renderer: tracked diff plus the porcelain status (which carries
    # untracked paths the diff cannot see).
    ECHO_TREE_DIFF_SHA256=$(
      {
        git -C "$echo_repo" diff HEAD
        printf '%s\n' "$echo_status"
      } | /usr/bin/shasum -a 256 | cut -d' ' -f1
    )
  fi
  require_sha256 ECHO_TREE_DIFF_SHA256 "$ECHO_TREE_DIFF_SHA256"

  # APPROVED_ECHO_PRONUNCIATION_SHA is optional. When set it still pins a
  # reviewed revision and is enforced exactly as before; when unset the render
  # proceeds and the receipt records that no revision was pinned.
  if [[ -n "$approved_input" ]]; then
    require_git_commit_sha APPROVED_ECHO_PRONUNCIATION_SHA "$approved_input"
    if ! APPROVED_ECHO_PRONUNCIATION_SHA=$(
      git -C "$echo_repo" rev-parse --verify "${approved_input}^{commit}"
    ); then
      printf 'approved Echo pronunciation revision is not a commit: %s\n' "$approved_input" >&2
      return 65
    fi
    require_git_commit_sha APPROVED_ECHO_PRONUNCIATION_SHA "$APPROVED_ECHO_PRONUNCIATION_SHA"
    if [[ "$APPROVED_ECHO_PRONUNCIATION_SHA" != "$ECHO_SOURCE_SHA" ]]; then
      printf 'approved Echo pronunciation revision %s must exactly equal Echo source HEAD %s\n' \
        "$APPROVED_ECHO_PRONUNCIATION_SHA" "$ECHO_SOURCE_SHA" >&2
      return 65
    fi
    if [[ "$ECHO_TREE_STATE" != clean ]]; then
      printf 'APPROVED_ECHO_PRONUNCIATION_SHA pins a revision but the Echo working tree is not clean; the pinned SHA would not identify the built renderer\n' >&2
      return 65
    fi
  else
    APPROVED_ECHO_PRONUNCIATION_SHA=unpinned
  fi

  "$build_gate" --wait
  make -C "$echo_repo" echo-cli

  CLI="$echo_repo/.build/cli/Build/Products/Release/echo-cli"
  if [[ ! -x "$CLI" ]]; then
    printf 'missing Release echo-cli: %s\n' "$CLI" >&2
    return 66
  fi
  ECHO_RESOURCE_DIR="$(dirname -- "$CLI")/EchoNarrationResources"
  if [[ -L "$ECHO_RESOURCE_DIR" || ! -d "$ECHO_RESOURCE_DIR" ]]; then
    printf 'missing or unsafe Release EchoNarrationResources: %s\n' \
      "$ECHO_RESOURCE_DIR" >&2
    return 66
  fi
  ECHO_RESOURCES_SHA256=$(
    /usr/local/bin/python3 "$state_helper" hash-tree "$ECHO_RESOURCE_DIR"
  )
  require_sha256 ECHO_RESOURCES_SHA256 "$ECHO_RESOURCES_SHA256"
  local cli_version cli_help
  cli_version=$(ECHO_RESOURCE_DIR="$ECHO_RESOURCE_DIR" "$CLI" --version)
  if ! ECHO_RENDER_VERSION=$(
    echo_pronunciation_release_render_version "$cli_version"
  ); then
    printf 'stale, pre-v12, or non-Release echo-cli: %s\n' "$cli_version" >&2
    return 65
  fi
  cli_help=$(ECHO_RESOURCE_DIR="$ECHO_RESOURCE_DIR" "$CLI" narrate --help)
  if [[ "$cli_help" != *"--no-pronunciation-review"* ]]; then
    printf 'stale echo-cli: pronunciation review is unavailable\n' >&2
    return 65
  fi
  if [[ "$cli_help" != *"--cover"* ]]; then
    printf 'stale echo-cli: explicit cover art is unavailable\n' >&2
    return 65
  fi

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
  for cover_input in "$COVER_SELECTION" "$COVER" "$M4B_COVER"; do
    if [[ -L "$cover_input" || ! -f "$cover_input" ]]; then
      printf 'governed paired-cover input is missing or unsafe: %s\n' \
        "$cover_input" >&2
      return 66
    fi
  done
  if ! /usr/local/bin/python3 \
    "$cover_helper" verify \
    --selection "$COVER_SELECTION" \
    --cover "$COVER" \
    --m4b-cover "$M4B_COVER" \
    --epub "$EPUB" >/dev/null; then
    printf 'selected cover pair does not match its receipt or EPUB\n' >&2
    return 65
  fi
  EPUB_SHA256=$(shasum -a 256 "$EPUB" | awk '{print $1}')
  COVER_SELECTION_SHA256=$(shasum -a 256 "$COVER_SELECTION" | awk '{print $1}')
  COVER_SHA256=$(shasum -a 256 "$COVER" | awk '{print $1}')
  M4B_COVER_SHA256=$(shasum -a 256 "$M4B_COVER" | awk '{print $1}')
  ECHO_CLI_SHA256=$(shasum -a 256 "$CLI" | awk '{print $1}')
  for hash_name in \
    EPUB_SHA256 COVER_SELECTION_SHA256 COVER_SHA256 M4B_COVER_SHA256; do
    require_sha256 "$hash_name" "${!hash_name}"
  done
  require_sha256 ECHO_CLI_SHA256 "$ECHO_CLI_SHA256"
  PACKAGE_SHA256=$(printf '%s\n' \
    "epub=$EPUB_SHA256" \
    "cover_selection=$COVER_SELECTION_SHA256" \
    "portrait_cover=$COVER_SHA256" \
    "square_cover=$M4B_COVER_SHA256" \
    | shasum -a 256 | awk '{print $1}')
  require_sha256 PACKAGE_SHA256 "$PACKAGE_SHA256"

  VOICE=${VOICE:-am_michael}
  case "$VOICE" in
    am_michael | am_puck) ;;
    *)
      printf 'VOICE must be am_michael or am_puck, got: %s\n' "$VOICE" >&2
      return 64
      ;;
  esac

  local echo_source_id
  echo_source_id=$(echo_pronunciation_source_id \
    "$ECHO_SOURCE_SHA" "$ECHO_TREE_STATE" "$ECHO_TREE_DIFF_SHA256")
  RUN_ID=$(echo_pronunciation_run_id \
    "$PACKAGE_SHA256" "$ECHO_CLI_SHA256" "$ECHO_RESOURCES_SHA256" \
    "$echo_source_id" "$VOICE")
  WORK="$RUN_ROOT/audio-work-$RUN_ID"
  DB="$RUN_ROOT/narration-$RUN_ID.sqlite"
  mkdir -p "$RUN_ROOT/research"
  ECHO_RENDER_INPUT_RECEIPT="$RUN_ROOT/research/echo-render-inputs-$RUN_ID.env"
  local receipt_text
  receipt_text=$(printf '%s\n' \
    "approved_echo_pronunciation_sha=$APPROVED_ECHO_PRONUNCIATION_SHA" \
    "echo_source_sha=$ECHO_SOURCE_SHA" \
    "echo_tree_state=$ECHO_TREE_STATE" \
    "echo_tree_diff_sha256=$ECHO_TREE_DIFF_SHA256" \
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
    "voice=$VOICE" \
    "run_id=$RUN_ID" \
    "work_dir=$WORK" \
    "narration_db=$DB")

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
      printf 'pre-existing WORK or DB requires a matching receipt: %s\n' "$RUN_ID" >&2
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
    printf 'Echo preflight changed cwd from %s to %s\n' "$original_pwd" "$PWD" >&2
    return 70
  fi

  ECHO_REPO=$echo_repo
  EXPLAINER_ROOT=$explainer_root
  export ECHO_REPO EXPLAINER_ROOT
  export APPROVED_ECHO_PRONUNCIATION_SHA ECHO_SOURCE_SHA EPUB EPUB_SHA256
  export ECHO_TREE_STATE ECHO_TREE_DIFF_SHA256
  export COVER_SELECTION COVER_SELECTION_SHA256 COVER COVER_SHA256
  export M4B_COVER M4B_COVER_SHA256 PACKAGE_SHA256
  export CLI ECHO_CLI_SHA256 ECHO_RESOURCE_DIR ECHO_RESOURCES_SHA256
  export ECHO_RENDER_VERSION VOICE RUN_ID WORK DB ECHO_RENDER_INPUT_RECEIPT
}

echo_pronunciation_attest_inputs() {
  local script_dir state_helper lease_helper cover_helper lease_root
  script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
  state_helper="$script_dir/echo_pronunciation_state.py"
  lease_helper="$script_dir/echo_pronunciation_lease.py"
  cover_helper="$script_dir/../../../skill/scripts/cover_receipts.py"
  lease_root=$(echo_pronunciation_canonical_lease_root) || return $?

  local required
  for required in \
    ECHO_REPO EXPLAINER_ROOT SLUG RUN_ROOT APPROVED_ECHO_PRONUNCIATION_SHA \
    ECHO_SOURCE_SHA ECHO_TREE_STATE ECHO_TREE_DIFF_SHA256 \
    EPUB EPUB_SHA256 COVER_SELECTION COVER_SELECTION_SHA256 \
    COVER COVER_SHA256 M4B_COVER M4B_COVER_SHA256 PACKAGE_SHA256 \
    CLI ECHO_CLI_SHA256 ECHO_RESOURCE_DIR \
    ECHO_RESOURCES_SHA256 ECHO_RENDER_VERSION VOICE RUN_ID WORK DB \
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

  if [[ "$ECHO_REPO" != /* || "$EXPLAINER_ROOT" != /* || "$RUN_ROOT" != /* ]]; then
    printf 'governed repository and run paths must be absolute\n' >&2
    return 64
  fi
  local canonical_echo_repo canonical_explainer_root canonical_run_root
  canonical_echo_repo=$(cd -- "$ECHO_REPO" 2>/dev/null && pwd -P) \
    || canonical_echo_repo=
  canonical_explainer_root=$(cd -- "$EXPLAINER_ROOT" 2>/dev/null && pwd -P) \
    || canonical_explainer_root=
  canonical_run_root=$(cd -- "$RUN_ROOT" 2>/dev/null && pwd -P) \
    || canonical_run_root=
  if [[ "$canonical_echo_repo" != "$ECHO_REPO" ]]; then
    printf 'ECHO_REPO must be a canonical real directory: %s\n' "$ECHO_REPO" >&2
    return 64
  fi
  if [[ "$canonical_explainer_root" != "$EXPLAINER_ROOT" ]]; then
    printf 'EXPLAINER_ROOT must be a canonical real directory: %s\n' \
      "$EXPLAINER_ROOT" >&2
    return 64
  fi
  if [[ ! "$SLUG" =~ ^[a-z0-9][a-z0-9-]*$ \
    || "$canonical_run_root" != "$EXPLAINER_ROOT/.build/custom-learning-audiobooks/$SLUG" ]]; then
    printf 'RUN_ROOT and SLUG do not identify the canonical governed run\n' >&2
    return 64
  fi
  case "$VOICE" in
    am_michael | am_puck) ;;
    *)
      printf 'VOICE must be am_michael or am_puck, got: %s\n' "$VOICE" >&2
      return 64
      ;;
  esac

  local build_resource="$ECHO_REPO/.build/cli"
  if ! "$lease_helper" --assert-held --lock-root "$lease_root" \
    --resource "$build_resource" >/dev/null 2>&1; then
    printf 'Echo input attestation requires the inherited build lease\n' >&2
    return 70
  fi
  require_git_commit_sha ECHO_SOURCE_SHA "$ECHO_SOURCE_SHA"
  require_sha256 ECHO_TREE_DIFF_SHA256 "${ECHO_TREE_DIFF_SHA256:-}"
  # The attestation's job is that the renderer did not change between preflight
  # and render. It compares against the state preflight actually recorded rather
  # than demanding a clean tree, so a dirty tree is attested rather than refused
  # — but any drift from that exact state still fails closed.
  local current_source source_status current_tree_state current_tree_diff
  current_source=$(/usr/bin/git -C "$ECHO_REPO" rev-parse HEAD) || return 65
  source_status=$(/usr/bin/git -C "$ECHO_REPO" status --porcelain \
    --untracked-files=all)
  if [[ -z "$source_status" ]]; then
    current_tree_state=clean
    current_tree_diff=$(printf '' | /usr/bin/shasum -a 256 | cut -d' ' -f1)
  else
    current_tree_state=dirty
    current_tree_diff=$(
      {
        /usr/bin/git -C "$ECHO_REPO" diff HEAD
        printf '%s\n' "$source_status"
      } | /usr/bin/shasum -a 256 | cut -d' ' -f1
    )
  fi
  if [[ "$current_source" != "$ECHO_SOURCE_SHA" ]]; then
    printf 'Echo source HEAD moved during the render: recorded %s, now %s\n' \
      "$ECHO_SOURCE_SHA" "$current_source" >&2
    return 65
  fi
  if [[ "$current_tree_state" != "${ECHO_TREE_STATE:-}" \
    || "$current_tree_diff" != "$ECHO_TREE_DIFF_SHA256" ]]; then
    printf 'Echo working tree changed during the render; renderer attestation failed\n' >&2
    return 65
  fi
  if [[ "$APPROVED_ECHO_PRONUNCIATION_SHA" != unpinned ]]; then
    require_git_commit_sha APPROVED_ECHO_PRONUNCIATION_SHA \
      "$APPROVED_ECHO_PRONUNCIATION_SHA"
    if [[ "$APPROVED_ECHO_PRONUNCIATION_SHA" != "$current_source" ]]; then
      printf 'approved Echo pronunciation revision %s must exactly equal Echo source HEAD %s\n' \
        "$APPROVED_ECHO_PRONUNCIATION_SHA" "$current_source" >&2
      return 65
    fi
  fi

  local expected_cli expected_resources expected_epub expected_cover_selection
  expected_cli="$ECHO_REPO/.build/cli/Build/Products/Release/echo-cli"
  expected_resources="$(dirname -- "$expected_cli")/EchoNarrationResources"
  expected_epub="$RUN_ROOT/dist/$SLUG.epub"
  expected_cover_selection="$RUN_ROOT/dist/cover-selection.json"
  local release_component
  for release_component in \
    "$ECHO_REPO/.build" \
    "$ECHO_REPO/.build/cli" \
    "$ECHO_REPO/.build/cli/Build" \
    "$ECHO_REPO/.build/cli/Build/Products" \
    "$ECHO_REPO/.build/cli/Build/Products/Release"; do
    if [[ -L "$release_component" ]]; then
      printf 'canonical Release path contains a symlink: %s\n' \
        "$release_component" >&2
      return 65
    fi
  done
  if [[ "$CLI" != "$expected_cli" || -L "$CLI" || ! -x "$CLI" ]]; then
    printf 'CLI is not the canonical Release echo-cli: %s\n' "$CLI" >&2
    return 65
  fi
  if [[ "$ECHO_RESOURCE_DIR" != "$expected_resources" \
    || -L "$ECHO_RESOURCE_DIR" || ! -d "$ECHO_RESOURCE_DIR" ]]; then
    printf 'Echo resources are not the canonical Release resource tree: %s\n' \
      "$ECHO_RESOURCE_DIR" >&2
    return 65
  fi
  if [[ "$EPUB" != "$expected_epub" || -L "$EPUB" || ! -f "$EPUB" ]]; then
    printf 'EPUB is not the canonical governed source: %s\n' "$EPUB" >&2
    return 65
  fi
  local selected_pair_dir=${COVER%/*}
  if [[ "$COVER_SELECTION" != "$expected_cover_selection" \
    || "$COVER" != "$selected_pair_dir/cover.png" \
    || "$M4B_COVER" != "$selected_pair_dir/m4b-cover.png" \
    || ! "$selected_pair_dir" =~ ^$RUN_ROOT/dist/candidate-[123]$ ]]; then
    printf 'selected cover paths changed while narration lease was held\n' >&2
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
  local current_m4b_cover_sha current_package_sha current_cli_sha
  local current_resources_sha cli_version cli_help
  local current_render_version
  current_epub_sha=$(/usr/bin/shasum -a 256 "$EPUB" | awk '{print $1}')
  current_cover_selection_sha=$(/usr/bin/shasum -a 256 "$COVER_SELECTION" | awk '{print $1}')
  current_cover_sha=$(/usr/bin/shasum -a 256 "$COVER" | awk '{print $1}')
  current_m4b_cover_sha=$(/usr/bin/shasum -a 256 "$M4B_COVER" | awk '{print $1}')
  current_package_sha=$(printf '%s\n' \
    "epub=$current_epub_sha" \
    "cover_selection=$current_cover_selection_sha" \
    "portrait_cover=$current_cover_sha" \
    "square_cover=$current_m4b_cover_sha" \
    | shasum -a 256 | awk '{print $1}')
  current_cli_sha=$(/usr/bin/shasum -a 256 "$CLI" | awk '{print $1}')
  current_resources_sha=$(/usr/local/bin/python3 "$state_helper" \
    hash-tree "$ECHO_RESOURCE_DIR")
  for required in \
    EPUB_SHA256 COVER_SELECTION_SHA256 COVER_SHA256 M4B_COVER_SHA256 \
    PACKAGE_SHA256 ECHO_CLI_SHA256 ECHO_RESOURCES_SHA256; do
    require_sha256 "$required" "${!required}"
  done
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
  if ! /usr/local/bin/python3 \
    "$cover_helper" verify \
    --selection "$COVER_SELECTION" \
    --cover "$COVER" \
    --m4b-cover "$M4B_COVER" \
    --epub "$EPUB" >/dev/null; then
    printf 'selected cover pair changed while narration lease was held\n' >&2
    return 65
  fi
  if [[ "$current_cli_sha" != "$ECHO_CLI_SHA256" ]]; then
    printf 'Echo CLI changed while narration lease was held: %s\n' "$CLI" >&2
    return 65
  fi
  if [[ "$current_resources_sha" != "$ECHO_RESOURCES_SHA256" ]]; then
    printf 'Echo resources changed while narration lease was held: %s\n' \
      "$ECHO_RESOURCE_DIR" >&2
    return 65
  fi
  cli_version=$(ECHO_RESOURCE_DIR="$ECHO_RESOURCE_DIR" "$CLI" --version)
  if ! current_render_version=$(
    echo_pronunciation_release_render_version "$cli_version"
  ); then
    printf 'stale, pre-v12, or non-Release echo-cli: %s\n' "$cli_version" >&2
    return 65
  fi
  if [[ "$current_render_version" != "$ECHO_RENDER_VERSION" ]]; then
    printf 'Echo render version changed while narration lease was held: %s\n' \
      "$cli_version" >&2
    return 65
  fi
  cli_help=$(ECHO_RESOURCE_DIR="$ECHO_RESOURCE_DIR" "$CLI" narrate --help)
  if [[ "$cli_help" != *"--no-pronunciation-review"* ]]; then
    printf 'stale echo-cli: pronunciation review is unavailable\n' >&2
    return 65
  fi
  if [[ "$cli_help" != *"--cover"* ]]; then
    printf 'stale echo-cli: explicit cover art is unavailable\n' >&2
    return 65
  fi

  local expected_run_id expected_work expected_db expected_receipt expected_source_id
  expected_source_id=$(echo_pronunciation_source_id \
    "$ECHO_SOURCE_SHA" "$ECHO_TREE_STATE" "$ECHO_TREE_DIFF_SHA256")
  expected_run_id=$(echo_pronunciation_run_id \
    "$PACKAGE_SHA256" "$ECHO_CLI_SHA256" "$ECHO_RESOURCES_SHA256" \
    "$expected_source_id" "$VOICE")
  expected_work="$RUN_ROOT/audio-work-$expected_run_id"
  expected_db="$RUN_ROOT/narration-$expected_run_id.sqlite"
  expected_receipt="$RUN_ROOT/research/echo-render-inputs-$expected_run_id.env"
  if [[ "$RUN_ID" != "$expected_run_id" || "$WORK" != "$expected_work" \
    || "$DB" != "$expected_db" \
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
  expected_receipt_text=$(printf '%s\n' \
    "approved_echo_pronunciation_sha=$APPROVED_ECHO_PRONUNCIATION_SHA" \
    "echo_source_sha=$ECHO_SOURCE_SHA" \
    "echo_tree_state=$ECHO_TREE_STATE" \
    "echo_tree_diff_sha256=$ECHO_TREE_DIFF_SHA256" \
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
    "voice=$VOICE" \
    "run_id=$RUN_ID" \
    "work_dir=$WORK" \
    "narration_db=$DB")
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
