---
name: fiction-audiobook
description: >-
  Use when the user asks to make a fiction audiobook from a premise, wants a novel or novella they can listen to, or asks for an Echo-ready fictional book.
---

# Fiction Audiobook

Own the package autonomously. Read `references/express-fiction-craft.md`
for story, `references/public-fiction-gate.md` for publication, and
`skills/echo-narration/references/narrating.md` before narration.

1. Full fictional listening packages use this express lane, never
   `fiction-book-development`; route manuscript-only planning, drafting,
   continuation, or revision there.
2. Ask nothing unless grilling/interview is explicit. Then ask one batch only:
   genre/mood; must-haves; exclusions; POV/distance; ending;
   casting. Never follow up.
3. Choose shortest sufficient form: short novella 18k–30k, novella 30k–45k,
   novel 50k–80k, or long novel 80k–110k. Announce title, angle, form, chapters,
   words, and runtime; record rationale in
   `.build/fiction-audiobooks/<slug>/brief.md`.
4. Write a compact bible/causal outline; one lead writer drafts sequentially
   with only `continuity/rolling.md`.
5. Run three craft passes plus final checks;
   bind the craft reference's unchanged schema-v1 private receipt.
6. Generate/select three cover pairs; build EPUB plus
   combined Markdown with `skill/scripts/build_book.py --fiction-receipt`.
7. After EPUB freezes, load preferences and write an immutable
   three-to-five-voice cast. Keep every recurring role on one voice; reserve
   zero-to-two short chapters for untried voices.
   Set `VOICE_CAST=$RUN_ROOT/_production/narration/voice-cast.json`; write
   `schemaVersion: 1`, `slug`, `chapterCount` (unquoted integer), `defaultVoice`, and
   `chapters` with integer `chapter`, text `role`/`voice`, boolean `experimental`;
   add canonical `voicePlanSHA256`,
   `voicePlanID: plan-<first-12-hash-characters>`, and
   `verifiedArtifacts: null`. Export its exact default with
   `export VOICE=$(/usr/local/bin/python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["defaultVoice"])' "$VOICE_CAST")`.
   Derive the plan fields only with
   `/usr/local/bin/python3 skills/echo-narration/scripts/echo_voice_plan.py --default-voice "$VOICE"`
   plus every cast `--chapter-voice N=voice`. Set `PREFERENCES` to expanded
   `~/Library/Application Support/Explainer Audiobooks/fiction-voice-preferences.json`,
   then run `/usr/local/bin/python3 skills/fiction-audiobook/scripts/fiction_voice_preferences.py validate-cast --cast
   "$VOICE_CAST" --preferences "$PREFERENCES"`.
8. Follow the narration reference exactly. Override its nonfiction
   `VOICE=am_michael` with the cast-derived `$VOICE`; adapt its lane/root, and
   pass mappings identical to the cast/helper. After it sets `$DIST`, run
   `export EPUB="$DIST/$SLUG.epub"; [[ -f "$EPUB" ]]`. Missing renderer/voice
   resources fail closed; recasting creates a new cast/plan/run. Run its
   selector-derived
   `$STATE_HELPER verify-delivery`, installed `$CLI verify-sidecar`, audit,
   JSON, and `ffprobe` commands. Only then seal use with
   `/usr/local/bin/python3 skills/fiction-audiobook/scripts/fiction_voice_preferences.py record-use --cast "$VOICE_CAST"
   --epub "$EPUB" --m4b "$AUDIOBOOK" --sidecar "$SIDECAR"
   --success-receipt "$SUCCESS_RECEIPT" --at "<ISO-8601 timestamp>" --preferences
   "$PREFERENCES"`; require `verifiedArtifacts` to become non-null before
   staging or public verification.
9. Prepare `_production/{source,checks,narration,covers,publication,previous}`;
   atomically stage
   `~/Library/Mobile Documents/com~apple~CloudDocs/Books/<Title>/` with
   `/usr/local/bin/python3 skills/fiction-audiobook/scripts/stage_echo_delivery.py`;
   root: exactly M4B, EPUB, alignment JSON, `cover.png`, and `_production/`.
10. Evaluate the public gate. Pass: stage outside `books/`, verify/copy six
    files, push, ready PR, release; keep M4B out of Git. Fail: record why; zero
    GitHub mutation. Normal public-safe triggers authorize; the private
    production receipt does not.
11. Separately report iCloud, push, ready PR, release, merge, human
    reading/listening. Never infer acceptance; never merge.
12. Redo narrowly. Story changes repair affected and causally downstream prose;
    rerun affected portions of all three passes plus final front-to-back,
    promise/payoff, and read-aloud gates; regenerate the unchanged fiction
    receipt against current chapter/evidence hashes; then rebuild EPUB and
    narration—never reuse stale acceptance. Voice changes preserve prose/covers
    but create a new cast/plan/run; cover changes rebuild EPUB/audio;
    blacklist-only feedback changes future preferences. Preserve verified
    staging and block promotion on any unexpected iCloud item, naming it.
