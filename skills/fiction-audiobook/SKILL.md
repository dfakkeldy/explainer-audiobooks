---
name: fiction-audiobook
description: >-
  Use when the user asks to make a fiction audiobook from a premise, wants a novel or novella they can listen to, or asks for an Echo-ready fictional book.
---

# Fiction Audiobook

Own the complete listening package autonomously. Read
`references/express-fiction-craft.md` before story work and
`references/public-fiction-gate.md` before publication.

1. Classify a complete fictional listening-package request into this express
   lane. Never invoke `fiction-book-development`; manuscript-only planning,
   drafting, continuation, or revision belongs there.
2. Ask zero intake questions unless the user explicitly says “grill me,”
   “interview me first,” or equivalent. Then ask one batch covering only:
   genre/mood; must-have characters or setting; exclusions; POV/distance;
   ending shape; and voice/casting preferences. Never ask a follow-up.
3. Choose the shortest sufficient form: short novella 18k–30k, novella
   30k–45k, novel 50k–80k, or long novel 80k–110k. Announce working title,
   angle, form, chapters, words, and runtime; record the rationale in
   `.build/fiction-audiobooks/<slug>/brief.md`.
4. Write a compact story bible and causal outline, then have one lead writer
   draft sequentially while maintaining only `continuity/rolling.md`.
5. Run the story, character/continuity, and ear/prose revision passes. Complete
   the final checks, then bind the unchanged schema-v1 private fiction
   production receipt described in the craft reference.
6. Generate three paired-cover candidates, select one, and build EPUB plus
   combined Markdown with `skill/scripts/build_book.py --fiction-receipt`.
7. After EPUB bytes freeze, load preferences and write an immutable
   three-to-five-voice cast. Keep every recurring role on one chapter-level
   voice; reserve zero-to-two suitable short chapters for untried voices.
   Validate with `scripts/fiction_voice_preferences.py`, then render through
   `skills/echo-narration/scripts/echo_pronunciation_narrate.sh` using
   `ECHO_RUN_LANE=fiction-audiobook` and complete `--chapter-voice` mappings.
8. Before recording use, run Echo `verify-delivery`, `verify-sidecar`,
   pronunciation-audit validation, JSON validation, and `ffprobe` checks.
9. Prepare `_production/{source,checks,narration,covers,publication,previous}`.
   Atomically stage
   `~/Library/Mobile Documents/com~apple~CloudDocs/Books/<Title>/` with
   `scripts/stage_echo_delivery.py`; its root must contain exactly M4B, EPUB,
   alignment JSON, `cover.png`, and `_production/`.
10. Evaluate the public-fiction gate. On pass, stage outside `books/`, verify,
    copy the six public files, push a public branch, open a ready PR, and create
    the release. M4B stays out of Git. On failure, record why and make zero
    GitHub mutations. A normal public-safe trigger is standing publication
    authorization; `fiction-production-receipt.json` stays private and grants
    none.
11. Report iCloud delivery, GitHub push, ready PR, release, merge, human
    reading, and human listening separately. Never infer human acceptance or
    auto-merge.
12. Redo narrowly: story changes repair causal downstream prose; voice changes
    preserve frozen prose/covers and create a new immutable cast/plan and fresh
    governed run; cover changes rebuild EPUB and audio; blacklist-only feedback
    changes future preferences. Preserve verified staging and block promotion
    on any unexpected iCloud item, naming the conflict.
