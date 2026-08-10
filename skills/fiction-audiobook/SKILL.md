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
   New editions use the landed source-bound character-level Echo cast as the
   standard narration path.
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
   one, and set `export PAIR="$RUN_ROOT/dist/candidate-N"`. The portrait cover
   must be embedded before the final EPUB is frozen.
6. Run the fiction source-bound block-voice pipeline in this order:

   1. Author explicit uninterrupted-speaker paragraphs and record the single
      dialogue-attribution rule from the craft reference. Do not infer speakers
      from dialogue or attribution.
   2. Build the final EPUB and combined Markdown with
      `skill/scripts/build_book.py --fiction-receipt`. Hash and freeze the final
      EPUB; it is the only source for inventory, casting, and narration.
   3. Follow the narration reference to export the private installed-Echo block
      inventory from the frozen EPUB. Echo owns block IDs and speakability; the
      inventory does not assign speakers.
   4. Run fresh `mkdir -p "$RUN_ROOT"/_production/{source,checks,narration,covers,publication,previous}`
      and require `previous` empty. Set
      `PREFERENCES="$HOME/Library/Application Support/Explainer Audiobooks/fiction-voice-preferences.json"`,
      `VOICE_CAST="$RUN_ROOT/_production/narration/voice-cast.json"`, and
      `VOICE_PLAN="$RUN_ROOT/_production/narration/echo-voice-plan.json"`.
      Write schema-2 `voice-cast.json` and the exact sibling authored Echo plan
      from the inventory with three-to-five stable, nonblacklisted voices. The
      lead writer assigns every intended speaker. A locally blacklisted voice is
      recast before Echo resolution; unavailable resources fail closed.
   5. Validate the cast and local preferences, then require installed Echo
      `resolve-voice-plan` success before narration:

      ```bash
      /usr/local/bin/python3 skills/fiction-audiobook/scripts/fiction_voice_preferences.py \
        validate-cast --cast "$VOICE_CAST" --voice-plan "$VOICE_PLAN" \
        --preferences "$PREFERENCES" --format argv0
      ```

   6. Invoke only the governed narration wrapper through the safe argv0 vector
      in the narration reference, with `--voice-plan`. In block mode do not
      export `VOICE`; the wrapper resolves it from the sealed Echo plan. Set
      `ECHO_RUN_LANE=fiction-audiobook`, use the exact fiction `RUN_ROOT`, and
      set `EPUB="$DIST/$SLUG.epub"` before the governed call.
   7. Verify schema-2 captures, schema-7 pronunciation audit, final M4B,
      alignment sidecar, and internal reel/capture path through the current
      selector and installed `verify-sidecar`.
   8. Set `COMPLETED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)` and record completed
      use only after schema-4 success:

      ```bash
      /usr/local/bin/python3 skills/fiction-audiobook/scripts/fiction_voice_preferences.py record-use \
        --cast "$VOICE_CAST" --epub "$EPUB" --m4b "$AUDIOBOOK" --sidecar "$SIDECAR" \
        --success-receipt "$SUCCESS_RECEIPT" --at "$COMPLETED_AT" --preferences "$PREFERENCES"
      ```

      Require non-null `verifiedArtifacts`.
   9. Set `EDITION_ID=$(date -u +%Y%m%dT%H%M%SZ)` and
      `ICLOUD_TITLE="$HOME/Library/Mobile Documents/com~apple~CloudDocs/Books/$TITLE"`.
      Decide the unchanged public/private gate first. Materialize the current `_production` evidence
      specified by the public reference **before** any delivery. Write the current `public-gate.json` in
      `_production/publication/`; for a public decision, verify and copy the
      unchanged schema-2 `publication.json` there before staging. A private
      request/source or failed gate records its nonempty reason and performs
      zero GitHub mutation.
   10. Stage only the existing root allowlist after that evidence is complete:

      ```bash
      /usr/local/bin/python3 skills/fiction-audiobook/scripts/stage_echo_delivery.py \
        --slug "$SLUG" --edition-id "$EDITION_ID" --m4b "$AUDIOBOOK" \
        --epub "$EPUB" --alignment "$SIDECAR" --cover "$PAIR/cover.png" \
        --production "$RUN_ROOT/_production" --destination "$ICLOUD_TITLE" --apply
      ```

      The iCloud title root is exactly M4B, EPUB, alignment JSON, `cover.png`,
      and `_production/`; it has no second M4B, capture, or reel.

       GitHub only after successful iCloud staging. Then, and only for a
       verified public decision, follow the public reference's six-file stage,
       push/ready-PR/release sequence; never merge. Report iCloud, push, PR,
       release, merge, human reading, and human listening as separate states.
7. Redo narrowly. Story changes repair causal prose and repeat affected
   passes/gates/receipt/build/narration; cover changes rebuild the EPUB/audio.
   Voice-only feedback changes the cast/plan and starts a new resolved run
   without rewriting prose or covers. Segmentation feedback changes chapter
   bytes, so rebuild the EPUB and invalidate the old source-bound plan; never
   copy captures into the new run. Every package change repeats verification,
   `record-use`, evidence, staging, and public/release reconciliation while
   preserving the complete prior chain. Append feedback, change, and resulting
   delivery/publication states to `_production/source/feedback.jsonl`. For
   listener feedback run:

    ```bash
    PREFERENCES="${HOME:?}/Library/Application Support/Explainer Audiobooks/fiction-voice-preferences.json"
    FEEDBACK_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ); FEEDBACK_REASON=${FEEDBACK_REASON-}
    /usr/local/bin/python3 skills/fiction-audiobook/scripts/fiction_voice_preferences.py set-verdict \
      --voice "$FEEDBACK_VOICE" --verdict "$VERDICT" --at "$FEEDBACK_AT" \
      --reason "$FEEDBACK_REASON" --preferences "$PREFERENCES"
    ```

    Feedback alone affects future casts; rerender only when recast is explicit.
    Preserve verified staging and name any unexpected iCloud item blocking promotion.
