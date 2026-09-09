# Required audiobook delivery

For Dan's audiobook requests, the finished outcome is the complete listening
package delivered to iCloud Books. This applies to nonfiction, fiction, and
classic adaptations, including requested audiobook redos. The request supplies
standing authorization for that private delivery; do not ask again whether to
narrate, create covers, include alignment, build the EPUB, or copy to iCloud.
Explicit manuscript-only or planning-only requests retain their narrower scope.
A later explicit instruction can change the outcome; inconvenience, missing
resources, or an unfinished renderer step cannot silently reduce it.

## Required artifacts

- A fully rendered M4B audiobook covering the requested manuscript.
- The matching Echo alignment sidecar JSON, bound to the delivered EPUB/audio
  and verified with the installed renderer's `verify-sidecar` workflow.
- The final EPUB with its portrait cover embedded and authored pronunciation
  instructions included through Echo PR #600’s verified contract. Follow
  [EPUB pronunciation](epub-pronunciation.md) for whole-manuscript coverage,
  inline decisions, linked lexicons, and plan-to-render reconciliation. This is
  required production work, not an optional polish pass.
- Both selected cover files: portrait `cover.png` and square `m4b-cover.png`.
  Embed the square cover in the M4B and retain both image files in delivery.
- The complete package in
  `~/Library/Mobile Documents/com~apple~CloudDocs/Books/<Book Title>/`.

Use the selected skill's established layout and staging workflow. Nonfiction
keeps the alignment sidecar and both cover files beside the EPUB and M4B. Fiction
and classic packages using fiction staging keep `cover.png` at the title root
and the selected pair under `_production/covers/`; preserve that root allowlist.
Retain source, pronunciation, casting, and validation evidence in the prescribed
source or production folders, not as competing final media files.

## Completion requires delivery evidence

Finish the normal manuscript, packaging, pronunciation, narration, media, and
alignment checks before staging. Verify the delivered files exist, are nonempty,
and match the accepted artifacts by hash. Check the staged package using the
selected workflow's delivery verifier when available. A working-directory build,
a preview clip, an EPUB-only copy, or a render queued for later is not completion.

If access, renderer support, or another required resource blocks completion,
continue independent work, preserve the resumable package, and report the exact
missing deliverable and blocker. Do not relabel a partial result as a finished
audiobook or make a required step optional. Keep prior accepted editions
recoverable while replacing a package through the supported delivery workflow.

Report the iCloud folder and final file paths, together with verification status
and any actual limitation. Local presence in the iCloud-managed folder proves
local delivery, not remote sync or arrival on the phone; report those separately
when verified. Human listening acceptance also remains a separate state and
must not be implied by automated checks. Private iCloud authorization does not
authorize GitHub publication or other destinations.
