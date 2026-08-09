---
name: fiction-audiobook
description: >-
  Use when the user asks to make a fiction audiobook from a premise, wants a novel or novella they can listen to, or asks for an Echo-ready fictional book.
---

# Fiction Audiobook

Own the package autonomously. Read `references/express-fiction-craft.md`,
`skill/references/cover-art.md`, `skills/echo-narration/references/narrating.md`,
then `references/public-fiction-gate.md` at its gate.

1. Complete fictional listening packages use this; manuscript-only work uses
   `fiction-book-development`.
2. Ask nothing unless grilling/interview is explicit; then one batch only:
   genre/mood; must-haves; exclusions; POV/distance; ending; casting. Never
   follow up.
3. Choose shortest sufficient: short novella 18k–30k, novella
   30k–45k, novel 50k–80k, or long novel 80k–110k. Announce title, angle, form,
   chapters, words, runtime; record rationale in
   `.build/fiction-audiobooks/<slug>/brief.md`.
4. Follow craft reference: compact bible/causal outline, one lead writer,
   sequential chapters, only `continuity/rolling.md`, three passes, final
   checks, and the unchanged schema-v1 private receipt.
5. Generate three paired covers in `$RUN_ROOT/dist/candidate-{1,2,3}`, select
   one, set `export PAIR="$RUN_ROOT/dist/candidate-N"`, then build EPUB and
   combined Markdown with `skill/scripts/build_book.py --fiction-receipt`.
6. After EPUB freezes, run
   `mkdir -p "$RUN_ROOT"/_production/{source,checks,narration,covers,publication,previous}`;
   require `previous` empty. Set
   `PREFERENCES="$HOME/Library/Application Support/Explainer Audiobooks/fiction-voice-preferences.json"`
   and `VOICE_CAST="$RUN_ROOT/_production/narration/voice-cast.json"`. Write its
   immutable JSON: schema 1,
   slug, integer chapter count, default voice, every integer chapter with stable
   role/voice and boolean experimental, canonical full plan hash/ID, and
   `verifiedArtifacts: null`. Choose from the premise: fit POV, role, character,
   tone, and accent first; novelty second. Use three-to-five voices, stable
   recurring roles, zero-to-two suitable untried short chapters, and no blacklist.
7. Export `VOICE` from the cast. Run `echo_voice_plan.py` with its default and
   every mapping, then `/usr/local/bin/python3 skills/fiction-audiobook/scripts/fiction_voice_preferences.py
   validate-cast --cast "$VOICE_CAST" --preferences "$PREFERENCES"`. Its JSON is a true argv token
   vector; decode without `eval` and pass every token unchanged to every
   `"$NARRATION_SCRIPT"` call. Follow the narration reference with
   `ECHO_RUN_LANE=fiction-audiobook`, fiction `$RUN_ROOT`, selected `$PAIR`, and
   `$EPUB="$DIST/$SLUG.epub"`. Unavailable resources fail closed; recast into a
   new plan/run.
8. Run selector `verify-delivery --epub`, installed `verify-sidecar`, audit,
   JSON, and `ffprobe`; then seal use:

   ```bash
   /usr/local/bin/python3 skills/fiction-audiobook/scripts/fiction_voice_preferences.py record-use \
     --cast "$VOICE_CAST" --epub "$EPUB" --m4b "$AUDIOBOOK" --sidecar "$SIDECAR" \
     --success-receipt "$SUCCESS_RECEIPT" --at "$COMPLETED_AT" --preferences "$PREFERENCES"
   ```

   Require non-null `verifiedArtifacts`.
9. Validate those six production directories; only the stager populates empty
   `previous`. Set nonempty `$EDITION_ID` and
   `ICLOUD_TITLE="$HOME/Library/Mobile Documents/com~apple~CloudDocs/Books/$TITLE"`,
   then run:

   ```bash
   /usr/local/bin/python3 skills/fiction-audiobook/scripts/stage_echo_delivery.py \
     --slug "$SLUG" --edition-id "$EDITION_ID" --m4b "$AUDIOBOOK" \
     --epub "$EPUB" --alignment "$SIDECAR" --cover "$PAIR/cover.png" \
     --production "$RUN_ROOT/_production" --destination "$ICLOUD_TITLE" --apply
   ```

   Its root is exactly M4B, EPUB, alignment JSON, `cover.png`, `_production/`.
10. Apply the public gate. Pass: six M4B-free Git files, verifier, push, ready
    PR, release. Fail/private source/private request: record why; zero GitHub
    mutation. Normal original public-safe triggers authorize; the private
    receipt does not. Never merge.
11. Report iCloud/push/PR/release/merge/human reading/listening separately.
    Never infer acceptance.
12. Redo narrowly. Story changes repair causal downstream prose and repeat
    affected passes/final gates/receipt/build/narration. Recast means a new
    plan/run; cover changes rebuild EPUB/audio. For liked, disliked,
    blacklisted, or clear feedback run:

    ```bash
    : "${FEEDBACK_REASON:=}"
    /usr/local/bin/python3 skills/fiction-audiobook/scripts/fiction_voice_preferences.py set-verdict \
      --voice "$FEEDBACK_VOICE" --verdict "$VERDICT" --at "$FEEDBACK_AT" \
      --reason "$FEEDBACK_REASON" --preferences "$PREFERENCES"
    ```

    Feedback alone affects future casts; rerender only when recast is explicit.
    Preserve verified staging and name any unexpected iCloud item blocking promotion.
