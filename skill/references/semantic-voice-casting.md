# Semantic voice casting

Use this reference for a new nonfiction audiobook with Echo block voices. It
does not change an accepted book or rerender an existing production.

## Core principle

Voice changes are retrieval cues, not decoration. The guide is the continuous
main narrator; a secondary voice earns a brief, stable learning job. Never
rotate by chapter, switch for a term, heading, title fragment, quotation, or
accent, or infer a role from prose.

## Stable roles

| Role | Job | Limit |
|---|---|---|
| `guide` | Continuous explanation, transitions, and all unearned prose. | At least 75 percent of nonempty paragraph blocks. |
| `memory` | Revisit an already-taught idea after teaching. | At most 15 percent. |
| `field` | Ground a concrete sourced example, observation, or evidence. | With `coach`, at most 15 percent. |
| `coach` | Prompt a brief action or reflection. | With `field`, at most 15 percent. |

All secondary roles together own at most 25 percent. Use two to four audibly
distinct voices, with `guide` and `memory` required: `guide` defaults to
`am_michael`; never use `af_heart`. A secondary group is one role across one to
four ordered, complete paragraph blocks, with at least two `guide` paragraph
blocks before the next secondary group. Do not use headings, title fragments,
or isolated words as a group.

## Select the cast

Audition candidate Echo voices on the same neutral passage. Respect listener
preferences and exclusions, and make roles audibly distinct without gender or
accent stereotypes. If a selected secondary voice is unavailable during
preflight, stop and obtain a revised approved cast; do not silently substitute
or render a reduced cast.

The only exception is a single-voice listener request recorded as an explicit
listener waiver in `source/brief.md`. That waiver permits one `guide` voice and
no assignments; it is not a fallback for time, availability, or uncertainty.

## Plan while writing

Keep the private semantic ledger at
`$RUN_ROOT/_production/narration/semantic-voice-ledger.md`. While drafting,
mark only earned paragraph groups and their learning jobs; do not assign Echo
block IDs. `memory` comes after the guide has taught the idea, recalls it in a
self-contained paragraph, and must make sense to a listener who missed the
preceding thirty seconds. `field` adds concrete evidence only when the example
does work that guide prose cannot. `coach` asks for a short action or reflection
only when it strengthens the next decision.

Keep guide prose sufficient on its own: voices reinforce recurrence and
retrieval, rather than replacing clear explanation, cold re-entry, or
well-placed `Key points` checkpoints.

## Freeze, inventory, and assign

Freeze the EPUB before creating an Echo inventory. The cast is
`$RUN_ROOT/_production/narration/semantic-voice-cast.json`; its authored plan
is the sibling `$RUN_ROOT/_production/narration/echo-voice-plan.json`. Read the
inventory file name and EPUB file name only from the cast's `source` object,
then require the private paths
`$RUN_ROOT/research/$INVENTORY_FILE_NAME` and
`$RUN_ROOT/dist/$EPUB_FILE_NAME`. The cast binds the frozen EPUB and inventory
bytes by filename and SHA-256.

Echo's installed `export-blocks` creates the inventory; it is the boundary for
actual block IDs, paragraph status, and order. Map the already-authored ledger
to that frozen inventory as whole paragraph groups. Never guess IDs, construct
ranges, infer roles, or treat local validation as a decision about Echo
speakability or plan identity.

## Validate and hand off

Use `semantic_voice_cast.py validate-cast` immediately before every semantic
block-mode wrapper invocation. It validates the source binding, known Echo
voices, role order, paragraph budgets, group spacing, waiver exclusivity, and
the exact authored-plan agreement. Echo remains authoritative for block
existence, speakability, resolved plan bytes, and plan identity. Follow
`skills/echo-narration/references/narrating.md` for operational rendering.

Forward only the validator's NUL-delimited argv0 result. This private function
preserves a validation failure status and requires exactly `--voice-plan` plus
the canonical authored plan:

```bash
load_semantic_voice_arguments() {
  local argv0 status token
  argv0=$(mktemp "${TMPDIR:-/tmp}/echo-semantic-voice-arguments.XXXXXX") || return $?
  trap 'rm -f -- "$argv0"' RETURN

  if /usr/local/bin/python3 \
    "$EXPLAINER_ROOT/skill/scripts/semantic_voice_cast.py" \
    validate-cast --cast "$SEMANTIC_CAST" --inventory "$INVENTORY" \
    --voice-plan "$VOICE_PLAN" --epub "$EPUB" --format argv0 >"$argv0"; then
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
    printf '%s\n' 'semantic voice handoff must be --voice-plan plus the canonical authored plan' >&2
    return 64
  fi
}

load_semantic_voice_arguments || exit $?
"$NARRATION_SCRIPT" "${VOICE_ARGUMENTS[@]}"
```

## Resume and rerender

Revalidate the same argv0 vector before every resume or partial render. A cast
or plan change creates a new governed run: never reuse captures, receipts,
work, database, or resume state. Existing accepted books are not automatically
rerendered.

## Waiver and listening review

Keep waiver evidence only in the brief. For a normal cast, conduct an ear pass:
the listener should hear calm, useful contrast; recognize the role's meaning;
and remain oriented in road-book conditions. Confirm that guide continuity,
clear prose, recurrence, and cold re-entry still carry the learning if a
secondary paragraph is missed.
