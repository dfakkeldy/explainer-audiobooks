#!/usr/bin/env bash

set -euo pipefail

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

echo_pronunciation_preflight() {
  local original_pwd=$PWD
  local echo_repo=${ECHO_REPO:-/Users/dfakkeldy/Developer/Echo}
  local build_gate=${ECHO_BUILD_GATE:-$HOME/.claude/bin/xcode-build-gate.sh}
  local approved_input=${APPROVED_ECHO_PRONUNCIATION_SHA:-}

  if [[ -z "$approved_input" ]]; then
    printf '%s\n' \
      'APPROVED_ECHO_PRONUNCIATION_SHA is required;' \
      'record the reviewed Echo commit boundary before rendering' >&2
    return 64
  fi
  if [[ -z ${SLUG:-} ]]; then
    printf 'SLUG is required\n' >&2
    return 64
  fi
  if [[ -z ${RUN_ROOT:-} || "$RUN_ROOT" != /* ]]; then
    printf 'RUN_ROOT must be a nonempty absolute explainer-audiobooks run path\n' >&2
    return 64
  fi
  if [[ ! -x "$build_gate" ]]; then
    printf 'Echo build gate is missing or not executable: %s\n' "$build_gate" >&2
    return 66
  fi

  require_git_commit_sha APPROVED_ECHO_PRONUNCIATION_SHA "$approved_input"
  if ! APPROVED_ECHO_PRONUNCIATION_SHA=$(
    git -C "$echo_repo" rev-parse --verify "${approved_input}^{commit}"
  ); then
    printf 'approved Echo pronunciation revision is not a commit: %s\n' "$approved_input" >&2
    return 65
  fi
  if ! ECHO_SOURCE_SHA=$(git -C "$echo_repo" rev-parse HEAD); then
    printf 'cannot resolve Echo source revision at %s\n' "$echo_repo" >&2
    return 65
  fi
  local echo_status
  echo_status=$(git -C "$echo_repo" status --porcelain --untracked-files=all)
  if [[ -n "$echo_status" ]]; then
    printf 'Echo working tree is not clean; source SHA would not identify the built renderer\n' >&2
    return 65
  fi
  require_git_commit_sha APPROVED_ECHO_PRONUNCIATION_SHA "$APPROVED_ECHO_PRONUNCIATION_SHA"
  require_git_commit_sha ECHO_SOURCE_SHA "$ECHO_SOURCE_SHA"
  if ! git -C "$echo_repo" merge-base --is-ancestor \
    "$APPROVED_ECHO_PRONUNCIATION_SHA" "$ECHO_SOURCE_SHA"; then
    printf 'approved Echo pronunciation revision %s is not an ancestor of source %s\n' \
      "$APPROVED_ECHO_PRONUNCIATION_SHA" "$ECHO_SOURCE_SHA" >&2
    return 65
  fi

  "$build_gate" --wait
  make -C "$echo_repo" echo-cli

  CLI="$echo_repo/.build/cli/Build/Products/Release/echo-cli"
  if [[ ! -x "$CLI" ]]; then
    printf 'missing Release echo-cli: %s\n' "$CLI" >&2
    return 66
  fi
  local cli_version
  cli_version=$("$CLI" --version)
  if [[ "$cli_version" != *"(Release)"* ]]; then
    printf 'stale/non-Release echo-cli: %s\n' "$cli_version" >&2
    return 65
  fi
  if ! "$CLI" narrate --help \
    | rg --fixed-strings -- '--no-pronunciation-review' >/dev/null; then
    printf 'stale echo-cli: pronunciation review is unavailable\n' >&2
    return 65
  fi

  EPUB="$RUN_ROOT/dist/$SLUG.epub"
  if [[ ! -f "$EPUB" ]]; then
    printf 'source EPUB is missing: %s\n' "$EPUB" >&2
    return 66
  fi
  EPUB_SHA256=$(shasum -a 256 "$EPUB" | awk '{print $1}')
  ECHO_CLI_SHA256=$(shasum -a 256 "$CLI" | awk '{print $1}')
  require_sha256 EPUB_SHA256 "$EPUB_SHA256"
  require_sha256 ECHO_CLI_SHA256 "$ECHO_CLI_SHA256"

  VOICE=${VOICE:-am_michael}
  case "$VOICE" in
    am_michael | am_puck) ;;
    *)
      printf 'VOICE must be am_michael or am_puck, got: %s\n' "$VOICE" >&2
      return 64
      ;;
  esac

  RUN_ID="${EPUB_SHA256:0:12}-${ECHO_CLI_SHA256:0:12}-${ECHO_SOURCE_SHA:0:12}-$VOICE"
  WORK="$RUN_ROOT/audio-work-$RUN_ID"
  DB="$RUN_ROOT/narration-$RUN_ID.sqlite"
  mkdir -p "$RUN_ROOT/research"
  ECHO_RENDER_INPUT_RECEIPT="$RUN_ROOT/research/echo-render-inputs-$RUN_ID.env"
  local receipt_tmp="$ECHO_RENDER_INPUT_RECEIPT.tmp.$$"
  printf '%s\n' \
    "approved_echo_pronunciation_sha=$APPROVED_ECHO_PRONUNCIATION_SHA" \
    "echo_source_sha=$ECHO_SOURCE_SHA" \
    "epub_sha256=$EPUB_SHA256" \
    "echo_cli_sha256=$ECHO_CLI_SHA256" \
    "echo_cli_path=$CLI" \
    "voice=$VOICE" >"$receipt_tmp"
  mv "$receipt_tmp" "$ECHO_RENDER_INPUT_RECEIPT"

  if [[ "$PWD" != "$original_pwd" ]]; then
    printf 'Echo preflight changed cwd from %s to %s\n' "$original_pwd" "$PWD" >&2
    return 70
  fi

  export APPROVED_ECHO_PRONUNCIATION_SHA ECHO_SOURCE_SHA EPUB EPUB_SHA256
  export CLI ECHO_CLI_SHA256 VOICE RUN_ID WORK DB ECHO_RENDER_INPUT_RECEIPT
}

if [[ ${BASH_SOURCE[0]} == "$0" ]]; then
  echo_pronunciation_preflight
  printf 'echo_pronunciation_preflight: clean\n'
  printf 'run_id=%s\nreceipt=%s\n' "$RUN_ID" "$ECHO_RENDER_INPUT_RECEIPT"
fi
