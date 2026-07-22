# Beyond the Tax-Sale Packet — full-audio acceptance checklist

This checklist is for the private governed audiobook candidate. The approved
EPUB manuscript and *The Packet Lifts* cover are frozen. Listening may identify
audio repairs; it does not authorize a text or cover revision.

The candidate package contains the chaptered M4B, portable alignment sidecar,
pronunciation audit, short pronunciation reel, selected square cover, and
machine-readable candidate receipt. Verify exact filenames and SHA-256 values
against `research/audiobook-candidate-receipt.json` before listening.

## Quick gate: pronunciation reel

The first candidate is rejected: Dan heard **Pictou** as “picktoau” and requires
**“PICK-toe.”** This checklist now applies only to the replacement M4B at
SHA-256 `f675ba1fde72aed5f7885931289f2d0dbb1b94e361f063012ab5bacbaeb1d4b8`
and replacement probe reel at SHA-256
`910a98daf19e6a3265794fbee46e52d577d31d7759cfd99fa1d2efdf4d0aaf27`.
Do not use the earlier listening folder for this verdict.

Listen to the short pronunciation reel first. Record the exact term and clip if
anything needs repair.

- [ ] Inverness
- [ ] Pictou — must end like **toe**, not “taow” or “toau”
- [ ] AAN and “Assessment Account Number”
- [ ] PID and “Parcel Identification Number”
- [ ] NSPRD and “Nova Scotia Property Records Database”
- [ ] CBRM and “Cape Breton Regional Municipality”
- [ ] HST
- [ ] Municipal Government Act

Pronunciation status remains **pending** until this listening is complete. The
automated audit proves coverage and alignment; it does not prove that a human
accepts the readings.

## Full-book gate

- [ ] All 13 chapter titles appear in order.
- [ ] Every chapter begins and ends cleanly, without a skipped or repeated
  passage.
- [ ] The `am_michael` voice, level, pace, and tone remain comfortable and
  consistent.
- [ ] Acronyms, place names, legal terms, numbers, and punctuation-driven pauses
  sound natural.
- [ ] No word is clipped, doubled, swallowed, or replaced.
- [ ] Long pauses and chapter transitions feel intentional.
- [ ] Seeking among chapter markers works in the chosen listening app.
- [ ] Pause and resume preserve the expected listening position in that app.
- [ ] The displayed artwork is Candidate 1, *The Packet Lifts*.
- [ ] The book continues to teach the source-bounded method:
  **notice → parcel → context → unknowns → handoff**.
- [ ] Nothing in the narration turns map screening into proof of access, title,
  condition, value, permission, possession, or buildability.
- [ ] No Property Online or other private-source material is present.

For a repair, record `chapter`, `time`, `heard`, and `expected`. A timestamped
negative finding overrides the machine receipts and blocks publication.

## Explicit verdict required

Choose one only after the pronunciation reel and the entire M4B have been heard:

- **ACCEPT FULL AUDIO** — the exact candidate may advance to a separately
  authorized publication gate.
- **REVISE AUDIO** — provide chapter/time findings for a controlled audio-only
  repair and a new hash-bound candidate.
- **REJECT AUDIO** — stop audiobook production and state the reason.

No verdict is inferred from opening the file, completing a spot check, or
accepting the earlier pilot. The full-audio verdict remains pending. Dan
separately authorized a `public-first-listen` deployment on 2026-07-22. That
publication permission does not count as full-audio acceptance, and any later
negative listening verdict supersedes the public-first-listen edition.

## Separate gates not covered here

- completed full-audio human acceptance;
- second-device proof of the public edition;
- final figure promotion; and
- video-edition production.
