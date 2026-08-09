---
name: fiction-audiobook
description: >-
  Use when the user asks to make or redo a fiction audiobook, wants a novel or novella they can listen to, requests an Echo-ready fictional book, or gives fiction narrator feedback.
---

# Fiction Audiobook

Read `references/express-fiction-craft.md` and
`skill/references/cover-art.md`; read
`skills/echo-narration/references/narrating.md` before narration and
`references/public-fiction-gate.md` before delivery.

1. Listening packages use this; `fiction-book-development` for manuscript-only
   work.
2. Ask nothing unless grilling/interview explicit; then one batch only:
   genre/mood; must-haves; exclusions; POV/distance; ending; casting. Never
   follow up.
3. Choose shortest sufficient: 18k–30k short novella, 30k–45k novella, 50k–80k
   novel, or 80k–110k long novel. Announce title, angle, form, chapters, words,
   runtime; record why in
   `.build/fiction-audiobooks/<slug>/brief.md`.
4. Follow craft reference: compact bible/causal outline, sequential lead writer,
   rolling continuity, three passes/final checks, unchanged private receipt.
5. Generate three paired covers in `$RUN_ROOT/dist/candidate-{1,2,3}`, select
   one, set `export PAIR="$RUN_ROOT/dist/candidate-N"`, then build EPUB and
   combined Markdown with `skill/scripts/build_book.py --fiction-receipt`.
6. After EPUB freezes, run fresh
   `mkdir -p "$RUN_ROOT"/_production/{source,checks,narration,covers,publication,previous}`;
   require `previous` empty. Set
   `PREFERENCES="$HOME/Library/Application Support/Explainer Audiobooks/fiction-voice-preferences.json"`
   and `VOICE_CAST="$RUN_ROOT/_production/narration/voice-cast.json"`. Write
   schema-1 immutable cast: slug, integer chapter count, default voice, every
   chapter's stable role/voice and boolean experimental, canonical plan hash/ID,
   `verifiedArtifacts: null`. Choose three-to-five nonblacklisted voices from the
   premise for POV/role/character/tone/accent fit, stable recurring roles, and
   zero-to-two suitable untried short chapters.
7. Export cast `VOICE`. Run `echo_voice_plan.py` with its default and mappings,
   then `/usr/local/bin/python3 skills/fiction-audiobook/scripts/fiction_voice_preferences.py
   validate-cast --cast "$VOICE_CAST" --preferences "$PREFERENCES"`. Decode its
   JSON argv vector without `eval`; pass tokens unchanged to every
   `"$NARRATION_SCRIPT"` call. Follow narration reference with
   `ECHO_RUN_LANE=fiction-audiobook`, fiction `$RUN_ROOT`, selected `$PAIR`, and
   `$EPUB="$DIST/$SLUG.epub"`. Unavailable resources fail closed; recast to new
   plan/run.
8. Run selector `verify-delivery --epub`, installed `verify-sidecar`, audit,
   JSON, `ffprobe`. Set
   `COMPLETED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)`, then seal use:

   ```bash
   /usr/local/bin/python3 skills/fiction-audiobook/scripts/fiction_voice_preferences.py record-use \
     --cast "$VOICE_CAST" --epub "$EPUB" --m4b "$AUDIOBOOK" --sidecar "$SIDECAR" \
     --success-receipt "$SUCCESS_RECEIPT" --at "$COMPLETED_AT" --preferences "$PREFERENCES"
   ```

   Require non-null `verifiedArtifacts`.
9. Set `EDITION_ID=$(date -u +%Y%m%dT%H%M%SZ)` and
   `ICLOUD_TITLE="$HOME/Library/Mobile Documents/com~apple~CloudDocs/Books/$TITLE"`.
   Materialize the public reference's exact evidence inventory and record its
   public/private decision before delivery, then run:

   ```bash
   /usr/local/bin/python3 skills/fiction-audiobook/scripts/stage_echo_delivery.py \
     --slug "$SLUG" --edition-id "$EDITION_ID" --m4b "$AUDIOBOOK" \
     --epub "$EPUB" --alignment "$SIDECAR" --cover "$PAIR/cover.png" \
     --production "$RUN_ROOT/_production" --destination "$ICLOUD_TITLE" --apply
   ```

   Its root is exactly M4B, EPUB, alignment JSON, `cover.png`, `_production/`.
10. After iCloud succeeds, a pass publishes six M4B-free Git files, ready PR,
    release. A private request/source or failure delivers iCloud with its reason
    and performs zero GitHub mutation. Original public-safe
    triggers authorize; the private receipt does not. Never merge.
11. Separately report iCloud/push/PR/release/merge/human reading/listening;
    never infer acceptance.
12. Redo narrowly. Story changes repair causal prose and repeat affected
    passes/gates/receipt/build/narration; recasts create a plan/run; cover changes
    rebuild EPUB/audio. Every package change repeats verification, `record-use`,
    evidence, staging, and public/release reconciliation while preserving the
    complete prior chain. Append feedback, change, and resulting delivery/publication
    states to `_production/source/feedback.jsonl`. For listener feedback run:

    ```bash
    PREFERENCES="${HOME:?}/Library/Application Support/Explainer Audiobooks/fiction-voice-preferences.json"
    FEEDBACK_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ); FEEDBACK_REASON=${FEEDBACK_REASON-}
    /usr/local/bin/python3 skills/fiction-audiobook/scripts/fiction_voice_preferences.py set-verdict \
      --voice "$FEEDBACK_VOICE" --verdict "$VERDICT" --at "$FEEDBACK_AT" \
      --reason "$FEEDBACK_REASON" --preferences "$PREFERENCES"
    ```

    Feedback alone affects future casts; rerender only when recast is explicit.
    Preserve verified staging and name any unexpected iCloud item blocking promotion.
