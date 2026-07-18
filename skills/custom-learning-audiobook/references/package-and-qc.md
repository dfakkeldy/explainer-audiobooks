# Package And QC

Contents: Universal paired-cover gate (with the complete paired command
example) · Build Layout · Learning Design QC · Interior Figures · Prose QC ·
EPUB And Markdown (with legacy single-cover compatibility) · Echo M4B And
Alignment (with governed real-book pronunciation probes) · Audio And Alignment
QC · Final Cover Receipt Verification · README Or Manifest Fields · Copy Rules.

Read `../../skill/references/unattended-production.md` before applying human-only
gates. Governed-final uses explicit outline, pilot, pronunciation, and cover
acceptance. Unattended-first-listen uses hash-bound editorial decisions, labels
human listening pending, permits only private editorial cover auto-selection,
and still completes every non-human package and media check. A request to have a
book ready to listen to may authorize the recorded private reading-copy delivery
intent; it never authorizes publication. After a package is verified,
`public-first-listen` is available only with explicit publication authorization
for a public-safe package: it is mechanically verified with
`humanListeningStatus: pending`, not human accepted. The public package and
catalog must say: “This edition has passed package and audio checks. The
creator’s full listening review is still underway.” A negative human verdict
supersedes that edition.

Publication states remain distinct: `unattended-first-listen` means private
package, never automatically published; `public-first-listen` means explicitly
authorized, public-safe, mechanically verified, human listen pending; and
`governed-final` is the existing higher-confidence state with completed required
human gates. The governed pilot still requires its lightweight `continue` or
`revise` listener verdict; public-first-listen does not replace that contract.

## Universal paired-cover gate

New packages require exactly three paired candidates. Each has a 1600×2560
`cover.png` EPUB portrait and a 2400×2400 `m4b-cover.png` M4B square, generated
with `render_cover_pair` from `skill/scripts/cover_pairs.py`. After thumbnail
review and explicit pair selection under the selected production mode, create a paired receipt with
`cover_receipts.py select-pair`. Pass both files to `build_book.py` using
`--cover`, `--m4b-cover`, and `--cover-selection`. Echo resolves the EPUB's
OPF-declared cover before export and hashes the exact resulting M4B into its
pronunciation audit. Never run `replace_m4b_cover.py` or otherwise mutate an
audited Echo M4B after narration. Run `cover_receipts.py verify --cover ... --m4b-cover ...
--epub ... --m4b ...` for post-embed verification and media preservation. Sync
all nine pair/provenance artifacts using `sync_selected_cover.py
--paired-artifact-dir ...`, first dry and then with `--apply`.

Order: research → three source directions → portrait/square render pairs →
thumbnail review → explicit pair selection → paired receipt → EPUB portrait +
M4B square embedding → post-embed verification → governed public/iCloud/site
sync. Public/private boundaries below govern destinations. Legacy single-cover
selection is verification-only compatibility, not a new-package workflow.


### Complete paired command example

Create exactly three directories, `candidate-1/`, `candidate-2/`, and
`candidate-3/`. Each contains schema-v2 `cover-spec.json` and
`m4b-cover-spec.json`, shared source art, and portrait/square outputs,
thumbnails, and receipts. Repeat this call for candidates 1 through 3:

```python
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path("skill/scripts").resolve()))
from cover_pairs import render_cover_pair

PAIR = Path(os.environ["PAIR"])
render_cover_pair(
    portrait_spec=PAIR / "cover-spec.json",
    square_spec=PAIR / "m4b-cover-spec.json",
    portrait_output=PAIR / "cover.png",
    square_output=PAIR / "m4b-cover.png",
    portrait_thumbnail=PAIR / "cover-thumbnail.png",
    square_thumbnail=PAIR / "m4b-cover-thumbnail.png",
    portrait_receipt=PAIR / "cover-render.json",
    square_receipt=PAIR / "m4b-cover-render.json",
)
```

After human review selects one pair, run the complete governed sequence:

```bash
PAIR="$DIST/candidate-$SELECTED"
/usr/local/bin/python3 skill/scripts/cover_receipts.py select-pair \
  --portrait-render-receipt "$PAIR/cover-render.json" \
  --square-render-receipt "$PAIR/m4b-cover-render.json" \
  --out "$DIST/cover-selection.json" \
  --book-slug "$SLUG" \
  --edition-id "$EDITION_ID" \
  --selection-source user \
  --selected-at "$SELECTED_AT" \
  --privacy-classification "$CLASSIFICATION"
cp "$DIST/cover-selection.json" "$PAIR/cover-selection.json"

/usr/local/bin/python3 skill/scripts/build_book.py \
  --chapters-dir "$RUN_ROOT/chapters" \
  --out-dir "$DIST" \
  --title "$TITLE" \
  --author "Dan Fakkeldy" \
  --contributor "$CONTRIBUTOR" \
  --subtitle "$SUBTITLE" \
  --slug "$SLUG" \
  --cover "$PAIR/cover.png" \
  --m4b-cover "$PAIR/m4b-cover.png" \
  --cover-selection "$DIST/cover-selection.json" \
  --learning-receipt "$RUN_ROOT/research/learning-design-receipt.json" \
  --prose-receipt "$RUN_ROOT/research/prose-style-receipt.json"

# Run the governed Echo wrapper, then complete "Audio And Alignment QC" below.
# That verified selector flow sets AUDIOBOOK to the accepted run-scoped M4B.
: "${AUDIOBOOK:?set only from the verified current-accepted selector}"
/usr/local/bin/python3 skill/scripts/cover_receipts.py verify \
  --selection "$DIST/cover-selection.json" \
  --cover "$PAIR/cover.png" \
  --m4b-cover "$PAIR/m4b-cover.png" \
  --epub "$DIST/$SLUG.epub" \
  --m4b "$AUDIOBOOK" \
  --receipt "$DIST/cover-selection.json"

/usr/local/bin/python3 skill/scripts/sync_selected_cover.py \
  --selection "$DIST/cover-selection.json" \
  --cover "$PAIR/cover.png" \
  --epub "$DIST/$SLUG.epub" \
  --m4b "$AUDIOBOOK" \
  --paired-artifact-dir "$PAIR" \
  --destination "$DELIVERY_DIR" \
  --intent reuse

/usr/local/bin/python3 skill/scripts/sync_selected_cover.py \
  --selection "$DIST/cover-selection.json" \
  --cover "$PAIR/cover.png" \
  --epub "$DIST/$SLUG.epub" \
  --m4b "$AUDIOBOOK" \
  --paired-artifact-dir "$PAIR" \
  --destination "$DELIVERY_DIR" \
  --intent reuse \
  --apply
```

Publication permission is never implied by this sequence: append
`--permission-to-publish` to the `select-pair` call **only when the user has
explicitly granted publication for this book**. Omitting it records
`permission_to_publish: false`, the correct state for private, unattended, and
not-yet-approved books (and the state the unattended editorial-autoselection
validator requires).

Use this reference before building, narrating, copying, or reporting a custom
learning audiobook package.

## Build Layout

Use this run layout:

```text
.build/custom-learning-audiobooks/<slug>/
  research/
    brief.md
    sources.md
    fact-pack.md
    outline.md
    evidence-notes.md
    evidence-notes.json
    voice-source-profile.md
    voice-exemplar.md
    learning-brief.json
    learning-outline.json
    chapter-plans.json
    coverage-ledger.json
    continuity.json
    learning-review.json
    comprehension-pilot.json
    revision-passes.json
    learning-design-receipt.json
    coverage-ledger.md
    continuity.md
    prose-qc-before.md
    prose-qc.md
    prose-style-receipt.json
    editorial-review.md
    visuals.md
    pronunciation-plan.json
    pronunciation-plan-receipt.json
    pronunciation-probe-reel.m4b        # after a governed partial probe
    pronunciation-probe-evidence.json   # after a governed partial probe
    unattended-decisions.json           # unattended-first-listen runs only
    echo-render-inputs-<run-id>.env
    echo-resume-state-<run-id>.json
    echo-render-current-attempt.json
    echo-render-current-accepted.json
    echo-render-success-<run-id>-<attempt-id>.json
    echo-render-output.owner.env  # present only while governed narration runs
  pilot/
    research/
      echo-pilot-inputs-<attempt-id>.env
      echo-pilot-success-<attempt-id>.env
    chapters/
      ch01.md
    dist/
      <slug>-pilot.epub
      <slug>-pilot.md
      <slug>-pilot.m4b
      <slug>-pilot.alignment.json
      <slug>-pilot.pronunciation-audit.json
      <slug>-pilot.pronunciation-reel.m4b  # when review samples exist
  chapters/
    ch01.md
    ch02.md
    images/
      figure-01.png
  dist/
    candidate-1/
      source-art.png
      cover-spec.json
      m4b-cover-spec.json
      cover.png
      m4b-cover.png
      cover-thumbnail.png
      m4b-cover-thumbnail.png
      cover-render.json
      m4b-cover-render.json
    cover-selection.json
    <slug>.epub
    <slug>.md
    images/
    echo-renders/
      <run-id>/
        <attempt-id>/
          <slug>.m4b
          <slug>.alignment.json
          <slug>.pronunciation-audit.json
          <slug>.pronunciation-reel.m4b  # when review samples exist
    README.md or manifest.json
```

Repeat the `candidate-1/` directory shape for `candidate-2/` and
`candidate-3/`. After selection, copy the paired receipt into the selected
candidate directory before governed sync so it contains the nine canonical
pair/provenance artifacts. In governed-final, `cover-selection.json` appears
only after the user chooses or requests a mix. In unattended-first-listen, an
independent editorial review may select a private pair with
`selection_source=editorial-autoselection` and `permission_to_publish=false`.

The canonical transient build output stays under `.build/`. A public-safe
package defaults to a durable iCloud Drive delivery copy under:

```text
/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/<Title>/
```

Private or sensitive packages stay in the agreed private project folder and
receive an iCloud Books reading copy only on an explicit user request. Public-safe
final packages may also publish to `books/<slug>/` only through the governed
public sync described below.

## Learning Design QC

Read `../../skill/references/road-book-mode.md` and
`../../skill/references/learning-design.md`. Complete the listening/revision
brief, authorized outcome-limited outline, `chapter-plans.json`, problem-before-
name and auditory-load budgets, complete concept/analogy/application/retrieval
paths, per-chapter continuity checkpoints, and independent structure plus blind
sequential beginner review.

Research, outline, drafting, and revision are separate artifact handoffs. Require
hash-bound `evidence-notes.json` and the traceable-only grounded notes before the
argument-level outline. Require the human-approved outline and first section
bound as `voice-exemplar.md`; a private style source is represented only by the
bounded `voice-source-profile.md`, with no raw excerpts committed. Draft section
by section with the full outline, prior text or running summary, section job, and
must-not-repeat list in `continuity.json.draftContexts`.

Before full drafting, build only the 10-to-15-minute comprehension pilot:

```bash
/usr/local/bin/python3 skill/scripts/build_book.py \
  --chapters-dir "$RUN_ROOT/pilot/chapters" \
  --out-dir "$RUN_ROOT/pilot/dist" \
  --title "$TITLE — Learning Pilot" \
  --author "Dan Fakkeldy" \
  --slug "$SLUG-pilot" \
  --learning-pilot
```

Render this explicitly nonpackage pilot with native Echo/Kokoro, using isolated
pilot work/database/output paths. It is the only pre-receipt narration path and
cannot be synced, delivered, or called a governed package. Do not use an Apple
or system voice. The dedicated wrapper derives the mandatory `-pilot` EPUB and
all isolated paths from the canonical base-book run. It preserves the approved
Echo source, Release binary, resource-tree, lease, sidecar, and pronunciation-
audit checks without requiring the later paired-cover or accepted full-book
pronunciation-plan receipts:

```bash
EXPLAINER_ROOT=$(git rev-parse --show-toplevel)
export EXPLAINER_ROOT
export RUN_ROOT="$EXPLAINER_ROOT/.build/custom-learning-audiobooks/$SLUG"
export SLUG TITLE
export VOICE=am_michael
: "${APPROVED_ECHO_PRONUNCIATION_SHA:?set the exact reviewed 40-character source SHA}"
export APPROVED_ECHO_PRONUNCIATION_SHA

"$EXPLAINER_ROOT/skills/custom-learning-audiobook/scripts/echo_learning_pilot_narrate.sh"
```

The wrapper leaves `listener_acceptance=pending` in its immutable success
receipt. In `governed-final`, record the exact accepted audio hash and listener
evidence in `comprehension-pilot.json`; request only a lightweight `continue` or
`revise` verdict, with optional listener notes and no comprehension
questionnaire. Stop before full drafting unless the human decision is
`continue` and the first-section checkpoint is accepted. In
`unattended-first-listen`, record the shared editorial pilot decision and
`humanComprehensionPilot: pending`; continue only after the editorial
first-section checkpoint and pilot decision are recorded. The unattended lane
never rewrites the wrapper's pending listener acceptance or fabricates human
evidence.

If the intended listener explicitly waives the pilot decision and asks
production to continue, governed-final may instead record
`status: "waived-by-listener"`. Preserve the exact audio binding and add
`waivedBy`, `waivedAt`, `reason`, and a `validationBoundary` stating that
comprehension evidence was not collected. The resulting receipt is
`pass-with-listener-waiver`, with `humanComprehensionPilot:
waived-by-listener`; this is permission to continue, not evidence of learning.

Continuity contexts normally remain one per section. A small same-chapter batch
is allowed only when an explicit in-run fast-track authorization exists. Give
the context a `-batch` ID, enumerate the exact `batchSections`, provide one
matching `sectionJobs` record per section, and set `fastTrackAuthorizationPath`
to that existing authorization artifact. Cross-chapter batches, duplicate
coverage, unknown sections, and reused authorizations fail validation.

Before the final receipt, complete hash-bound `revision-passes.json` as separate
single-job claim-traceability, tightening, de-listification, sentence-rhythm,
and rendered ear-pass lanes. Echo or Kokoro must actually render the ear-pass;
record every stumble and lost-thread location rather than inferring listenability
from text.

After the humanizer and every accepted voice edit, rerun both learning reviews
against the final chapter hashes and write `learning-review.json`. Generate the
learning receipt before the governed final EPUB build:

```bash
python3 skill/scripts/learning_design_qc.py \
  --run-root "$RUN_ROOT" \
  --receipt-out "$RUN_ROOT/research/learning-design-receipt.json"
```

Do not reconstruct missing plans after drafting, reduce the target to match an
undersized manuscript, or add material to meet a word-count floor. A prose-style
pass cannot substitute for learning-design evidence, and the learning receipt
does not certify comprehension. Negative human listening evidence overrides it.

## Interior Figures

`skill/scripts/build_book.py` can embed pictures in the EPUB and copy them beside
the combined Markdown. Store package images under `chapters/images/`, then insert
each approved figure as its own Markdown paragraph:

```markdown
![Descriptive alt text](images/figure-01.png "Caption shown under the figure")
```

Image paths resolve relative to the chapters directory. Supported formats are
PNG, JPEG, GIF, SVG, and WebP. Keep `research/visuals.md` with each image's
source/provenance, license or permission status, intended placement, alt text,
caption, and public/private safety.

Rules:

- Use user-supplied, generated, self-created, public-domain, permissively
  licensed, or explicitly permissioned images.
- Treat found web images as references unless the rights allow inclusion.
- Do not copy private or sensitive images into public repo or KB outputs.
- Use meaningful alt text and captions; avoid decorative filler.
- Prefer a few purposeful figures that teach, orient, compare, or document.

## Prose QC

Complete prose QC, humanization, frontier-author acceptance, and every
substantive repair before building the EPUB or rendering Echo audio. Read
`../../skill/references/frontier-manuscript-pipeline.md`, the narration-style
checks in `../../skill/references/narration-style.md`, and
`../../skill/references/humanizer-pass.md`. Also follow
`../../skill/references/declaudification.md` for the independent inventory,
family-density gate, accepted/rejected decisions, and hash-bound receipt. The frontier-authored chapter
Markdown remains canonical throughout this step.

At minimum:

- verify `evidence-notes.json`, the argument-level outline, every section draft
  context, the accepted voice exemplar, and final `revision-passes.json`,
- word count matches the ledger's **chapter-specific** ranges or has a written
  reason to be outside them; do not pad a short chapter automatically,
- no raw code/symbol narration leaks,
- run `python3 skill/scripts/prose_qc.py --chapters-dir
  .build/custom-learning-audiobooks/<slug>/chapters --out
  .build/custom-learning-audiobooks/<slug>/research/prose-qc-before.md
  --fail-on-style` for the initial independent inventory,
- have a cheaper reviewer use that report and `coverage-ledger.md` to flag only
  exact locations for redundant ideas, formulaic openings/closings, unexplained
  leaps, shallow concepts, jargon without a concrete case, or missing
  boundaries/counterexamples; it recommends a repair **type**, not replacement
  prose, and saves its citation-first findings as
  `research/editorial-review.md`,
- the frontier author accepts/rejects findings and makes every substantive
  content edit in canonical Markdown,
- run the bounded humanizer pass, have the frontier author accept or reject each
  non-mechanical suggestion, then rerun factual, ledger, narration, and prose
  checks,
- save the decisions and rerun with `--fail-on-style`, `--decisions`, and
  `--style-receipt-out .../research/prose-style-receipt.json`; a failed family
  budget or stale chapter hash blocks packaging,
- complete the sensitive/private-term scan, first-chapter and technical-chapter
  spot reads, and source-confidence label,
- for illustrated books, every intended figure source exists and has alt text,
  caption, provenance, and permission before build; verify its `OEBPS/images/`
  entry after the governed EPUB is assembled.

## EPUB And Markdown

Render **exactly three award-worthy, complete art-and-type cover candidates**
before building the EPUB; this is the default, not an opt-in. Follow
`../../skill/references/cover-art.md`: research transferable visual principles,
write a complete brief for each candidate, render all three, and let the user
choose or request a mix. The three candidates must differ in metaphor,
composition, palette, material language, and title strategy. Font, line breaks,
scale, placement, and effects are part of the candidate—not a shared footer
applied afterward.

When an image-generation tool is available, generated raster art is mandatory;
keep it text-free, with no logos or watermarks. Do not substitute bespoke SVG,
programmatic vector art, diagrams, or icon compositions. Use SVG only when the
user explicitly requests vector art or approves it as a fallback after image
generation is confirmed unavailable. Rights-cleared raster art remains
acceptable; never copy or closely imitate a specific existing cover. Include a
bright/high-key option unless three dark directions are truly warranted, and
reject a generic template, slide icon, AI wallpaper, or recolour before the user
sees it.

Save shared art and two schema-v2 specifications in each candidate directory,
then use the complete `render_cover_pair(...)` call above for candidates 1
through 3. Human-review each full-size portrait and square render, generated
160-pixel thumbnail, art-and-type brief, font/palette note, and warning. The
renderer never selects a candidate automatically. Ask the user to choose or
request a mix; a mix becomes a new specification and render.

Only after that choice, assign `SLUG`, `EDITION_ID`, `SELECTED_AT`,
`CLASSIFICATION`, `PERMISSION_TO_PUBLISH`, `TITLE`, `SUBTITLE`, and `CONTRIBUTOR`
from the approved run metadata. `SELECTED_AT` is an ISO-8601 timestamp;
classification is `private`, `public-safe`, or `sensitive`; publication
permission is `denied`, `granted`, or `not-requested`. Use
`selection_source=user`; for a requested mix, substitute
`requested-mix` after rendering the new specification.

The following single-cover commands are verification-only compatibility for an
existing legacy package. Do not use them for a new package, which must follow
the paired gate above. Final receipt verification waits for the M4B:

```bash
SELECTED=1
DIST=".build/custom-learning-audiobooks/$SLUG/dist"
/usr/local/bin/python3 skill/scripts/cover_receipts.py select \
  --render-receipt "$DIST/cover-$SELECTED.render.json" \
  --out "$DIST/cover-selection.json" \
  --book-slug "$SLUG" \
  --edition-id "$EDITION_ID" \
  --selection-source explicit-user-choice \
  --selected-at "$SELECTED_AT" \
  --classification "$CLASSIFICATION" \
  --permission-to-publish "$PERMISSION_TO_PUBLISH"

/usr/local/bin/python3 skill/scripts/build_book.py \
  --chapters-dir ".build/custom-learning-audiobooks/$SLUG/chapters" \
  --out-dir "$DIST" \
  --title "$TITLE" \
  --author "Dan Fakkeldy" \
  --contributor "$CONTRIBUTOR" \
  --subtitle "$SUBTITLE" \
  --slug "$SLUG" \
  --cover "$DIST/cover-$SELECTED.png" \
  --cover-selection "$DIST/cover-selection.json" \
  --legacy-without-learning-receipt \
  --prose-receipt ".build/custom-learning-audiobooks/$SLUG/research/prose-style-receipt.json"
```

Validate:

```bash
unzip -t .build/custom-learning-audiobooks/<slug>/dist/<slug>.epub
wc -w .build/custom-learning-audiobooks/<slug>/chapters/ch*.md
test ! -d .build/custom-learning-audiobooks/<slug>/chapters/images || \
  unzip -l .build/custom-learning-audiobooks/<slug>/dist/<slug>.epub | rg 'OEBPS/images/'
```

## Echo M4B And Alignment

Echo owns the M4B, alignment, and pronunciation-review renderer. Narration is
an installed-package operation: it never builds, checks out, or repairs Echo.
Never invoke a DerivedData `Debug/echo-cli`, a raw direct `echo-cli narrate`, or
an older audiobook worktree command for a governed render; those paths bypass
the wrapper's installed-package provenance, resource leases, and locked
postchecks.

### Installed renderer store and approvals

The local, content-addressed store is:

```text
~/Library/Application Support/Echo/Renderers/
  <40-hex source SHA>/
    approved-renderer.json
    <64-hex manifest SHA>/
      echo-cli
      EchoNarrationResources/
      renderer-manifest.json
```

`<40-hex source SHA>` is the reviewed Echo source revision and `<64-hex
manifest SHA>` names one immutable Release package. A source can have several
packages; `approved-renderer.json` selects only the package for a *new* run.
`APPROVED_ECHO_PRONUNCIATION_SHA` is required for every governed narration and
must be exactly 40 lowercase hexadecimal characters. It must exactly equal the
installed package's `ECHO_SOURCE_SHA`; a branch name, abbreviated SHA, current
checkout, or inferred revision is not approval. The separate installer review
is `APPROVED_ECHO_INSTALLER_SHA`, also an exact 40-character SHA. Record both
identities in the render-input receipt.

For a new render the wrapper uses `resolve-new`, which reads the selector while
leased and seals the selected manifest. For `--resume`, provide the canonical
absolute `research/echo-resume-state-$RUN_ID.json`; the wrapper uses
`resolve-resume` and the sealed resume-state receipt, never a possibly changed
selector. Do not copy captures, edit receipts, or turn a historical receipt
into an operational resume. Historical receipts are read-only verification
evidence; only the current installed-renderer schema and matching
manifest-bound receipts can resume, publish, or authorize delivery.

The wrapper records `ECHO_CLI_SHA256`, `ECHO_RESOURCES_SHA256`,
`ECHO_RENDERER_MANIFEST_SHA256`, the exact source/installer SHAs, and the
canonical `ECHO_RENDERER_BUILD_ROOT`. It passes the sealed
`ECHO_RESOURCE_DIR` explicitly to every probe, narration, and
`verify-sidecar` call, and re-attests the installed package before launch and
before publication. The model-policy fields are informational only:
`modelBytesAttested: false` means the shared cached model bytes are not
attested by this package. Do not claim that a package receipt verifies the
model cache.

### Operator-only install and recovery

Install, verification, promotion, and repair happen outside narration from a
clean, reviewed Echo installer worktree with separate clean installer and
source worktrees. Use the exact installer interface, not an improvised build:

```bash
PYTHONPATH=Scripts python3 -m echo_renderer.cli install \
  --installer-worktree <installer worktree> \
  --installer-sha <APPROVED_ECHO_INSTALLER_SHA> \
  --source-worktree <source worktree> \
  --source-sha <APPROVED_ECHO_PRONUNCIATION_SHA>

PYTHONPATH=Scripts python3 -m echo_renderer.cli verify \
  --source-sha <APPROVED_ECHO_PRONUNCIATION_SHA> \
  --manifest-sha <64-hex manifest SHA>

PYTHONPATH=Scripts python3 -m echo_renderer.cli promote \
  --source-sha <APPROVED_ECHO_PRONUNCIATION_SHA> \
  --manifest-sha <64-hex manifest SHA>

PYTHONPATH=Scripts python3 -m echo_renderer.cli repair \
  --installer-worktree <installer worktree> \
  --installer-sha <APPROVED_ECHO_INSTALLER_SHA> \
  --source-worktree <source worktree> \
  --source-sha <APPROVED_ECHO_PRONUNCIATION_SHA> \
  --manifest-sha <64-hex manifest SHA>
```

- **Missing version/selector**: install the exact approved source. Use
  `install --promote` only for a source with no selector; otherwise verify the
  new package and promote it explicitly after review.
- **Corrupt package or failed attestation**: run `verify` first. If it cannot
  verify, use `repair` for that exact source/manifest identity; repair
  quarantines bytes and never promotes a selector.
- **Incompatible package**: exit 69 means the Release package, capability,
  architecture, or deployment floor is incompatible with the host. Install a
  reviewed compatible renderer; do not weaken the narration wrapper.
- **Approval mismatch**: obtain the exact reviewed
  `APPROVED_ECHO_PRONUNCIATION_SHA` and select/install that identity. Do not
  substitute a descendant, branch, or local checkout.
- **Live lease (exit 75)**: wait for the holder and retry. Do not force a
  selector, repair, or narration past a live lease. The narration wrapper's
  `--recover-stale-lock` is only for its exact proven-local stale owner record;
  it does not build, repair, or narrate.

No automatic cleanup or update is permitted. Old packages and repair
quarantines are preserved until an operator makes a manual disposition. The
renderer store is local-only: it has no code-signing, notarization, or
cross-machine distribution authority.

A feature-worktree edit does not update installed agents merely because their
paths are symlinks: those links resolve the canonical checkout at
`/Users/dfakkeldy/Developer/explainer-audiobooks`. Run
`tools/validate_custom_learning_skill_install.py` before claiming parity.
The validator also requires the independent OpenClaw import to have no
discoverable `SKILL.md`, preserves its exact `SKILL.disabled.md` tombstone, and
confirms both that `hermes skills list --source local` reports one canonical
skill and that Hermes' real bare `skill_view('custom-learning-audiobook')`
loads the canonical `SKILL.md` content.
`installed_skill_parity: pending-integration` means the branch is tested but the
installed canonical checkout is still old; do not report installed parity until
the tool says `current` after integration.

The public wrapper first derives one canonical lease namespace from the
effective operating-system user account, ignoring any caller-supplied
`ECHO_PRONUNCIATION_LEASE_ROOT`, then takes a kernel lease on the resolved
`ECHO_RENDERER_BUILD_ROOT`. Every hidden wrapper mode verifies the inherited
lock descriptors and their exact lock-file inodes; an environment variable by
itself is not a capability. A real inherited descriptor is necessary but not
sufficient: the hidden render stage independently re-attests the installed,
approved source/manifest identity, canonical Release CLI and resource paths,
the exact Release render version (`rv12` or newer) and help surface, complete
resource-tree and CLI hashes, selected portrait and square cover paths and
hashes, `M4B_COVER_SHA256`, the paired selection-receipt hash, the combined
package hash, canonical source/run/voice coordinates, and byte-exact
immutable-input receipt.
A directly constructed hidden invocation therefore receives no trust from its
caller and can proceed only when it independently satisfies the public
preflight contract. The preflight also requires `--version` to expose a
parseable `rvN (Release)` value where `N` is at least 12, requires
`narrate --help` to expose `--no-pronunciation-review` and `--cover`, validates
EPUB and CLI
SHA-256 values as exactly 64 lowercase hexadecimal characters, deterministically
hashes the complete sibling `EchoNarrationResources` tree, and records the
approved revision, source revision, `EPUB_SHA256`, `ECHO_CLI_SHA256`,
`ECHO_RESOURCES_SHA256`, exact resource path, and exact Release render version
in an immutable-input receipt.
The full exact approved revision is a component of `RUN_ID`. An
existing receipt for the same ID must match byte-for-byte, and pre-existing
`WORK` or `DB` data without that matching receipt fails closed before resume.
The narration wrapper then acquires nonblocking kernel leases for every
canonicalized shared resource: `WORK`, `DB`, the current-attempt selector state,
M4B, sidecar, audit, and reel. Each
resource identity is SHA-256-keyed independently, so different `RUN_ID` values
still conflict if any output path overlaps. The build and render lease file descriptors are
inherited by the governed shell and Echo child, remain held through all of
`echo-cli narrate`, and release automatically after process exit—even if the
outer helper is killed. The wrapper revalidates Echo source, EPUB, Release CLI,
the complete resource-tree hash, and the immutable receipt both before and after narration while those leases are
held. A mismatch exits nonzero; its artifacts are not accepted, validated, or
published. Stop immediately on any failure:

```bash
set -euo pipefail
EXPLAINER_ROOT=$(git rev-parse --show-toplevel)
export RUN_ROOT="$EXPLAINER_ROOT/.build/custom-learning-audiobooks/$SLUG"
export DIST="$RUN_ROOT/dist"
export VOICE=am_michael
export SLUG TITLE
export COVER="$PAIR/cover.png"
export M4B_COVER="$PAIR/m4b-cover.png"
export PRONUNCIATION_PLAN="$RUN_ROOT/research/pronunciation-plan.json"
: "${APPROVED_ECHO_PRONUNCIATION_SHA:?set the exact reviewed 40-character source SHA}"
export APPROVED_ECHO_PRONUNCIATION_SHA

"$EXPLAINER_ROOT/skills/custom-learning-audiobook/scripts/echo_pronunciation_narrate.sh"
```

Pronunciation review is on by default; it applies approved rules before TTS and
emits review evidence automatically. Do not pass
`--no-pronunciation-review` for a governed custom-learning render. The command
uses the custom-learning default `--voice am_michael` through `VOICE` and keeps
synthesis bounded at one chapter job and two Kokoro threads.

### Governed real-book pronunciation probes

Create `research/pronunciation-plan.json` before invoking Echo. It must include
listener-named risks such as `hyperparameter` and `hyperparameters`, every
spoken variant, the expected canonical chapters, and the reason each term needs
review. The wrapper validates this plan in `planning` mode for a bounded partial
render. When `assuranceLevel` is absent or `governed-final`, it refuses an
unbounded full render until every required term has accepted, hash-bound human
listening evidence or an explicit listener waiver bound to the same governed
reel evidence. When `assuranceLevel` is `unattended-first-listen`, it
requires every term to be `probed`, complete governed reel evidence for every
spoken variant, no fabricated human decision, and records `humanListening:
pending`. Export the canonical path:

```bash
export PRONUNCIATION_PLAN="$RUN_ROOT/research/pronunciation-plan.json"
/usr/local/bin/python3 "$EXPLAINER_ROOT/skill/scripts/pronunciation_plan_qc.py" \
  --run-root "$RUN_ROOT" \
  --phase planning
```

For a real-book pronunciation probe, the public wrapper may render one new
chapter at a time while retaining the same source, approved renderer, resource
tree, `WORK`, and database. On a multi-chapter book, the first command returns
CLI **exit 2**, meaning that its chapter capture and resume state were sealed
but the book is still partial:

```bash
set +e
"$EXPLAINER_ROOT/skills/custom-learning-audiobook/scripts/echo_pronunciation_narrate.sh" \
  --max-chapters 1
rc=$?
set -e
[[ "$rc" == 2 ]]
```

The wrapper derives its own work directory and narration database; recover
their canonical paths from the attempt's immutable input receipt before using
`$WORK` or `$DB` below:

```bash
ATTEMPT_RECEIPT="$RUN_ROOT/research/echo-render-current-attempt.json"
INPUT_RECEIPT="$RUN_ROOT/research/$(/usr/local/bin/python3 -c \
  'import json,sys; print(json.load(open(sys.argv[1]))["inputReceiptFileName"])' \
  "$ATTEMPT_RECEIPT")"
WORK=$(awk -F= '$1 == "work_dir" { print substr($0, index($0, "=") + 1) }' \
  "$INPUT_RECEIPT")
DB=$(awk -F= '$1 == "narration_db" { print substr($0, index($0, "=") + 1) }' \
  "$INPUT_RECEIPT")
```

Listen to and inspect the chapter-zero M4A named by
`$WORK/.anchors-ch0.json`. To render exactly the next chapter, request one new
chapter again—not two, because the option counts uncaptured chapters in the
current process:

```bash
set +e
"$EXPLAINER_ROOT/skills/custom-learning-audiobook/scripts/echo_pronunciation_narrate.sh" \
  --resume --max-chapters 1
rc=$?
set -e
[[ "$rc" == 2 ]]
```

This second probe adds `$WORK/.anchors-ch1.json` and its named chapter-one M4A.
Each partial attempt updates `echo-render-current-attempt.json` and seals
`echo-resume-state-$RUN_ID.json`, but it has **no accepted M4B**, sidecar,
pronunciation audit, success receipt, or current-accepted selector. Partial
capture audio is listening evidence, not a deliverable package. Resume later
without `--max-chapters` only after completing the acceptance sequence below.

Build one governed reel from the actual partial chapter captures and their Echo
word timings. The builder writes a JSON evidence file binding the plan, source
captures, extracted clips, and reel hashes:

```bash
/usr/local/bin/python3 \
  "$EXPLAINER_ROOT/skill/scripts/build_pronunciation_probe_reel.py" \
  --run-root "$RUN_ROOT" \
  --work-dir "$WORK" \
  --timing-db "$DB" \
  --out "$RUN_ROOT/research/pronunciation-probe-reel.m4b" \
  --evidence-out "$RUN_ROOT/research/pronunciation-probe-evidence.json"
```

`--timing-db` is a governed fallback for Echo captures whose marker omits word
arrays even though the same narration database contains synthesis timing rows.
The reel evidence records a deterministic hash of the timing snapshot used;
the source chapter audio remains bound by its sealed capture hash.

For governed-final, have the listener hear every required base form and variant.
Human listening is the decision gate: automation may locate and extract the
clips, but it may not mark them accepted. After the listener accepts the reel,
update each required plan entry to `status: "accepted"`, record `acceptedBy` and
`acceptedAt`, and point its evidence path and SHA-256 at the shared governed
evidence JSON.

If the listener explicitly says to continue without hearing the reel, keep the
same complete governed evidence but set each required entry to
`status: "waived-by-listener"`. Record `waivedBy`, `waivedAt`, `reason`, and a
`validationBoundary` stating that human listening was not collected. The
receipt becomes `pass-with-listener-waiver` and reports `humanListening:
not-collected-listener-waived`; it does not describe any term as accepted, and
later negative human evidence overrides the waiver.

For unattended-first-listen, set the plan-level `assuranceLevel`, update each
required entry to `status: "probed"`, keep `decision: null`, and point the
evidence path and SHA-256 at that same governed evidence JSON. The validator
checks every form and variant but writes `status: first-listen` and
`humanListening: pending`; it never invents acceptance. Then validate and write
the immutable full-render receipt:

```bash
/usr/local/bin/python3 "$EXPLAINER_ROOT/skill/scripts/pronunciation_plan_qc.py" \
  --run-root "$RUN_ROOT" \
  --phase full-render \
  --receipt-out "$RUN_ROOT/research/pronunciation-plan-receipt.json"
```

Only then resume without `--max-chapters` to finish and publish the governed
run, followed by the complete selector-bound QC below. The wrapper repeats the
full-render validation itself, so a stale plan, changed chapter, changed reel,
or missing acceptance fails before Echo starts.

Each attempt receives a cryptographically random `ATTEMPT_ID`. Its output stem
is `$DIST/echo-renders/$RUN_ID/$ATTEMPT_ID/$SLUG`, with a pronunciation audit on
every reviewed render and a pronunciation reel when review samples are
available. The audit JSON is required even when there are zero decisions; an
empty reel is not created.

Echo renders into a run-scoped staging directory. A zero CLI exit is not enough:
the wrapper requires a nonempty M4B, validates the sidecar and schema-v2 audit,
then publishes the staged files into the run/attempt-scoped directory. Under the
shared selector lease, it atomically writes
`research/echo-render-current-attempt.json` before rendering. A failure leaves
that newest attempt current, so an older success can no longer verify as the
current delivery. On success it writes the schema-v2
`research/echo-render-success-$RUN_ID-$ATTEMPT_ID.json`, binding the exact
attempt, source EPUB, input receipt, resume-state receipt, M4B, sidecar, audit,
and optional reel hashes. Only after that receipt verifies does it atomically
replace `research/echo-render-current-accepted.json`. Absence or mismatch of
the attempt, success, or accepted-selector chain means the render is not
deliverable. Old run-scoped artifacts may remain as history but are never
selected implicitly.
Do not edit, retag, replace the cover of, or otherwise mutate the published M4B.

If `am_michael` fails because the voice resource is unavailable, set and export
`VOICE=am_puck`, then rerun the wrapper. Its preflight derives a new `RUN_ID`,
`WORK`, `DB`, receipt, and resource leases. Record the fallback. Do not silently use
`af_heart`.

Use a fresh `--work-dir` and `--db` whenever the source EPUB changes or the
Release CLI binary or Echo source revision changes. Permit `--resume` only for
the same immutable source EPUB, exact approved/source revision, Release CLI and
resource-tree hashes, voice, and capture set. The wrapper requires
`research/echo-resume-state-$RUN_ID.json` to bind the current DB and every
capture-marker/audio hash. Every capture must carry a sealed schema-v1 Echo
identity for the exact Release render version recorded in the immutable input
receipt, the current EPUB fingerprint and voice, one
consistent capture-set ID, pronunciation evidence, and matching audio byte count
and SHA-256. Legacy identity-free captures are never blessed by this workflow.
State reset, capture receipt, and success receipt writes also require the live
inherited resource-lease descriptors; invoking the helper directly cannot bless
unleased files.
Immediately before success publication, while the `WORK` and `DB` leases are
still held, the wrapper re-derives the resume snapshot from the live database,
capture markers, and capture audio and requires it to match the sealed state
receipt. The success receipt binds both that receipt's derived filename and its
SHA-256 as `resumeStateFileName` and `resumeStateSHA256`.
Only then rerun the wrapper with `--resume`;
it must select the original `WORK`/`DB` and acquire all resource leases before it
invokes Echo:

```bash
"$EXPLAINER_ROOT/skills/custom-learning-audiobook/scripts/echo_pronunciation_narrate.sh" --resume
```

Never copy old captures into a new run, edit a receipt, or resume after editing
the EPUB or rebuilding Echo; the content-addressed `RUN_ID` selects fresh paths
and the preflight rejects unreceipted or mismatched pre-existing paths.

An active kernel lease fails closed before a second Echo process starts. Owner
metadata is diagnostic, not the lock itself. After acquiring all kernel leases,
the wrapper may remove exact local stale metadata only when its hostname, PID,
process-start identity, run, and all resource paths prove that the old owner is
gone. A structurally valid stale owner from an older content-addressed run can
be recovered after inputs change; its recorded `WORK` and `DB` must still derive
exactly from its own safe run ID. It never automatically removes remote-host or malformed metadata. For an
operator-led check of an exact local stale record, use:

```bash
"$EXPLAINER_ROOT/skills/custom-learning-audiobook/scripts/echo_pronunciation_narrate.sh" --recover-stale-lock
```

Recovery does not narrate. Rerun the wrapper normally or with `--resume` after a
successful recovery. Do not delete lease or owner files by hand.

Do not add a self-imposed timeout around `echo-cli narrate`, kill a progressing
render because it may take several hours, or replace it with Apple/macOS/system
voice narration for convenience. Native Echo/Kokoro output is the custom-learning
audio contract. The only automatic narrator fallback is from `am_michael` to the
Echo voice `am_puck` when the preferred Echo voice is unavailable.

If native Echo rendering is blocked, distinguish the cases clearly:

- **Slow but progressing**: let it run, use `--resume` if interrupted, and report
  the active render state if the session must hand off.
- **Blocked by resources/build/schema**: fix the Echo blocker when practical, or
  surface EPUB/Markdown from the run folder as clearly labelled interim files;
  do not sync or call the package complete.
- **User-approved non-Echo preview**: only if the user explicitly asks for it,
  create the preview with a loud `non_echo_audio` status. Do not call it
  Echo-ready, and do not let it replace the native Echo render unless the user
  cancels Echo audio.

## Audio And Alignment QC

Verify the final sidecar against the exact EPUB and audio, then validate the
automatic pronunciation audit. These are release gates, not optional QA:

```bash
ATTEMPT_RECEIPT="$RUN_ROOT/research/echo-render-current-attempt.json"
CURRENT_SELECTOR="$RUN_ROOT/research/echo-render-current-accepted.json"
selector_value() {
  /usr/local/bin/python3 - "$CURRENT_SELECTOR" "$1" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as source:
    value = json.load(source).get(sys.argv[2])
if not isinstance(value, str) or not value:
    raise SystemExit(f"missing selector string: {sys.argv[2]}")
print(value)
PY
}
RUN_ID=$(selector_value runID)
ATTEMPT_ID=$(selector_value attemptID)
ARTIFACT_RELATIVE_PATH=$(selector_value artifactRelativePath)
INPUT_RECEIPT_NAME=$(selector_value inputReceiptFileName)
SUCCESS_RECEIPT_NAME=$(selector_value successReceiptFileName)
STATE_RECEIPT_NAME="echo-resume-state-$RUN_ID.json"
[[ "$RUN_ID" =~ ^[0-9a-f]{12}-[0-9a-f]{12}-[0-9a-f]{12}-([0-9a-f]{40}|[0-9a-f]{64})-(am_michael|am_puck)$ ]]
[[ "$ATTEMPT_ID" =~ ^[0-9a-f]{64}$ ]]
[[ "$ARTIFACT_RELATIVE_PATH" == "echo-renders/$RUN_ID/$ATTEMPT_ID" ]]
[[ "$INPUT_RECEIPT_NAME" == "echo-render-inputs-$RUN_ID.env" ]]
[[ "$SUCCESS_RECEIPT_NAME" == "echo-render-success-$RUN_ID-$ATTEMPT_ID.json" ]]
[[ "$STATE_RECEIPT_NAME" == "echo-resume-state-$RUN_ID.json" ]]

ARTIFACT_ROOT="$DIST/$ARTIFACT_RELATIVE_PATH"
INPUT_RECEIPT="$RUN_ROOT/research/$INPUT_RECEIPT_NAME"
STATE_RECEIPT="$RUN_ROOT/research/$STATE_RECEIPT_NAME"
SUCCESS_RECEIPT="$RUN_ROOT/research/$SUCCESS_RECEIPT_NAME"
AUDIOBOOK="$ARTIFACT_ROOT/$SLUG.m4b"
SIDECAR="$ARTIFACT_ROOT/$SLUG.alignment.json"
AUDIT="$ARTIFACT_ROOT/$SLUG.pronunciation-audit.json"
REEL="$ARTIFACT_ROOT/$SLUG.pronunciation-reel.m4b"

"$EXPLAINER_ROOT/skills/custom-learning-audiobook/scripts/echo_pronunciation_state.py" \
  verify-delivery \
  --attempt "$ATTEMPT_RECEIPT" \
  --selector "$CURRENT_SELECTOR" \
  --receipt "$SUCCESS_RECEIPT" \
  --input-receipt "$INPUT_RECEIPT" \
  --state-receipt "$STATE_RECEIPT" \
  --epub "$DIST/$SLUG.epub" \
  --audiobook "$AUDIOBOOK" \
  --sidecar "$SIDECAR" \
  --audit "$AUDIT" \
  --reel "$REEL"

CLI=$(awk -F= '$1 == "echo_cli_path" { print substr($0, index($0, "=") + 1) }' \
  "$INPUT_RECEIPT")
ECHO_RESOURCE_DIR=$(awk -F= '$1 == "echo_resource_dir" { print substr($0, index($0, "=") + 1) }' \
  "$INPUT_RECEIPT")
export ECHO_RESOURCE_DIR

ffprobe -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 "$AUDIOBOOK"

python3 -m json.tool "$SIDECAR" >/dev/null

"$CLI" verify-sidecar \
  --epub "$DIST/$SLUG.epub" \
  --audio "$AUDIOBOOK" \
  --sidecar "$SIDECAR"

"$EXPLAINER_ROOT/skills/custom-learning-audiobook/scripts/validate_pronunciation_audit.py" \
  "$AUDIT"

test ! -f "$REEL" || ffprobe -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 "$REEL"
```

Require `SIDECAR_OK` from `verify-sidecar`. The media-bound manifest schema
version is `2`.
Require `coverage=complete`, render version 12 or newer, `am_michael` or
`am_puck`, schema-valid decision objects and timing ranges, and watch counts that
match decisions across the complete emitted watch vocabulary, including zero
counts. Require `audiobookSHA256` to match the exact raw sibling M4B bytes. When
a reel is listed, require `listeningReelSHA256` to match the exact raw sibling
reel bytes; reel filename and hash must be present or absent together. Reconcile
every diagnostic before delivery. A missing reel is valid
only when `listeningReelFileName` is absent or null and there are no timed review
samples. Every timed decision requires a listed reel, and every chapter/book
range must fit within the probed audiobook duration. A listed reel must exist,
probe as positive-duration media, and have at least one eligible pronunciation
decision with validated chapter- and book-relative timing.
When a reel exists, inspect its chapter labels and listen to its samples (or the
matching final-audiobook passages). Automated checks do not substitute for
hearing the result: human listening remains explicitly pending until someone
actually listens, and the report must say so.

Optional Echo QA after narration:

```bash
AUDIOBOOK_ID=$(sqlite3 "$DB" "select id from audiobook order by rowid desc limit 1;")
"$CLI" qa \
  --db "$DB" \
  --audiobook-id "$AUDIOBOOK_ID" \
  --work-dir "$WORK" \
  --report "$ARTIFACT_ROOT/$SLUG.narration-qa.json"
```

If the database schema differs, skip this optional QA and report why.

## Final Cover Receipt Verification

After Echo renders the M4B, verify the explicit selection across the selected
cover, governed EPUB, and M4B before any delivery or public publishing step:

```bash
/usr/local/bin/python3 skill/scripts/cover_receipts.py verify \
  --selection "$DIST/cover-selection.json" \
  --cover "$DIST/cover-$SELECTED.png" \
  --epub "$DIST/$SLUG.epub" \
  --m4b "$AUDIOBOOK" \
  --receipt "$DIST/cover-selection.json"
```

This is verification only. Never repair a failure by replacing the cover or
otherwise rewriting the audited M4B. Correct the source/selection and rerender
so Echo emits and hashes the final package bytes itself.

If native Echo rendering is blocked, EPUB/Markdown may be surfaced from the run
folder only as clearly labelled interim files. Do not call them a complete
governed package, and do not proceed to sync/copy until native Echo audio and
this final verification succeed.

## README Or Manifest Fields

Record:

- title,
- slug,
- requester/topic,
- public-safe/private/sensitive status,
- permission-to-publish status,
- length mode,
- word count,
- runtime,
- chapter count,
- narrator,
- frontier author model and model used for research/review/production (when used),
- research mode,
- source-confidence label,
- sensitive-topic guardrails,
- figure count and image provenance/licensing summary,
- output files,
- pronunciation audit path, schema version, coverage, watch counts, and
  diagnostic count,
- pronunciation reel path or the reason no reel was emitted,
- pronunciation human-listening status (`pending` until actually heard),
- approved Echo pronunciation SHA, actual Echo source SHA, EPUB SHA-256, CLI
  SHA-256, resource-tree SHA-256, and the current-attempt, current-accepted,
  input, resume-state, and schema-v2 render-success receipt paths,
- QC gates passed/skipped.

## Copy Rules

The final cover receipt verification above must pass before any copy. The Audio
And Alignment QC sequence must also pass `verify-delivery`; only the matching
current-attempt, current-accepted, schema-v2 success, input, resume-state,
source, and media chain authorizes copying. A historical success receipt alone
never authorizes a delivery. For a
public-safe package, the default delivery folder is iCloud Books:

```bash
DELIVERY_DIR="/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/$TITLE"
```

Private or sensitive packages stay in the agreed private project folder and
receive an iCloud Books reading copy only on an explicit user request. Set
`DELIVERY_DIR` to that agreed private folder first. If the user explicitly asks
for an iCloud reading copy, repeat the same governed delivery sequence with the
authorized iCloud path only after the private project copy is complete.

For every authorized delivery folder, run this dry run and inspect its reported
classification before applying or copying anything:

```bash
/usr/local/bin/python3 skill/scripts/sync_selected_cover.py \
  --selection "$DIST/cover-selection.json" \
  --cover "$DIST/cover-$SELECTED.png" \
  --epub "$DIST/$SLUG.epub" \
  --m4b "$AUDIOBOOK" \
  --destination "$DELIVERY_DIR" \
  --intent reuse
```

Use `--intent supersede` only for a newer explicit choice. If a destination has
cover-bearing files but no receipt, it is an `unreceipted` conflict unless the
operation is an explicit supersession. Only after the classification is expected,
rerun the same chosen intent with explicit apply:

```bash
/usr/local/bin/python3 skill/scripts/sync_selected_cover.py \
  --selection "$DIST/cover-selection.json" \
  --cover "$DIST/cover-$SELECTED.png" \
  --epub "$DIST/$SLUG.epub" \
  --m4b "$AUDIOBOOK" \
  --destination "$DELIVERY_DIR" \
  --intent reuse \
  --apply
```

After the explicit apply succeeds, copy the rest of `dist/` without overwriting
the governed files:

```bash
rsync -a \
  --exclude "echo-renders/" \
  --exclude "cover.png" \
  --exclude "cover-selection.json" \
  --exclude "$SLUG.epub" \
  --exclude "$SLUG.m4b" \
  "$DIST/" "$DELIVERY_DIR/"

cp "$SIDECAR" "$DELIVERY_DIR/$SLUG.alignment.json"
cp "$AUDIT" "$DELIVERY_DIR/$SLUG.pronunciation-audit.json"
test ! -f "$REEL" || \
  cp "$REEL" "$DELIVERY_DIR/$SLUG.pronunciation-reel.m4b"
cp "$ATTEMPT_RECEIPT" "$DELIVERY_DIR/$(basename "$ATTEMPT_RECEIPT")"
cp "$CURRENT_SELECTOR" "$DELIVERY_DIR/$(basename "$CURRENT_SELECTOR")"
cp "$INPUT_RECEIPT" "$DELIVERY_DIR/$(basename "$INPUT_RECEIPT")"
cp "$STATE_RECEIPT" "$DELIVERY_DIR/$(basename "$STATE_RECEIPT")"
cp "$SUCCESS_RECEIPT" "$DELIVERY_DIR/$(basename "$SUCCESS_RECEIPT")"
```

After copying, verify the copied package from the delivery path, not only from
`.build/`:

```bash
/usr/local/bin/python3 skill/scripts/cover_receipts.py verify \
  --selection "$DELIVERY_DIR/cover-selection.json" \
  --cover "$DELIVERY_DIR/cover.png" \
  --epub "$DELIVERY_DIR/$SLUG.epub" \
  --m4b "$DELIVERY_DIR/$SLUG.m4b" \
  --receipt "$DELIVERY_DIR/cover-selection.json"

unzip -t "$DELIVERY_DIR/$SLUG.epub"
ffprobe -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 "$DELIVERY_DIR/$SLUG.m4b"
test ! -f "$DELIVERY_DIR/$SLUG.alignment.json" || \
  python3 -m json.tool "$DELIVERY_DIR/$SLUG.alignment.json" >/dev/null
"$EXPLAINER_ROOT/skills/custom-learning-audiobook/scripts/validate_pronunciation_audit.py" \
  "$DELIVERY_DIR/$SLUG.pronunciation-audit.json"
test ! -f "$DELIVERY_DIR/$SLUG.pronunciation-reel.m4b" || \
  ffprobe -v error -show_entries format=duration \
    -of default=noprint_wrappers=1:nokey=1 \
    "$DELIVERY_DIR/$SLUG.pronunciation-reel.m4b"

"$EXPLAINER_ROOT/skills/custom-learning-audiobook/scripts/echo_pronunciation_state.py" \
  verify-delivery \
  --attempt "$DELIVERY_DIR/$(basename "$ATTEMPT_RECEIPT")" \
  --selector "$DELIVERY_DIR/$(basename "$CURRENT_SELECTOR")" \
  --receipt "$DELIVERY_DIR/$(basename "$SUCCESS_RECEIPT")" \
  --input-receipt "$DELIVERY_DIR/$(basename "$INPUT_RECEIPT")" \
  --state-receipt "$DELIVERY_DIR/$(basename "$STATE_RECEIPT")" \
  --epub "$DELIVERY_DIR/$SLUG.epub" \
  --audiobook "$DELIVERY_DIR/$SLUG.m4b" \
  --sidecar "$DELIVERY_DIR/$SLUG.alignment.json" \
  --audit "$DELIVERY_DIR/$SLUG.pronunciation-audit.json" \
  --reel "$DELIVERY_DIR/$SLUG.pronunciation-reel.m4b"
```

Public publishing is a separate governed destination. It requires
`classification=public-safe`, `permission_to_publish=granted`, and the
`--public-destination` check. Run the public dry run first:

```bash
PUBLIC_DIR="books/$SLUG"
/usr/local/bin/python3 skill/scripts/sync_selected_cover.py \
  --selection "$DIST/cover-selection.json" \
  --cover "$DIST/cover-$SELECTED.png" \
  --epub "$DIST/$SLUG.epub" \
  --m4b "$AUDIOBOOK" \
  --destination "$PUBLIC_DIR" \
  --intent reuse \
  --public-destination
```

Apply this public sync only when the repo policy permits all four governed
artifacts: `cover.png`, EPUB, M4B, and `cover-selection.json`. If M4B or another
governed artifact is not permitted, do not bypass classification with raw copy;
leave public publishing pending. When the classification and policy are both
expected, rerun with explicit apply:

```bash
/usr/local/bin/python3 skill/scripts/sync_selected_cover.py \
  --selection "$DIST/cover-selection.json" \
  --cover "$DIST/cover-$SELECTED.png" \
  --epub "$DIST/$SLUG.epub" \
  --m4b "$AUDIOBOOK" \
  --destination "$PUBLIC_DIR" \
  --intent reuse \
  --public-destination \
  --apply
```

Only after governed public apply may non-governed Markdown, README, and images be
copied; these commands do not replace any of the four governed files:

```bash
test ! -f "$DIST/$SLUG.md" || cp "$DIST/$SLUG.md" "$PUBLIC_DIR/$SLUG.md"
test ! -f "$DIST/README.md" || cp "$DIST/README.md" "$PUBLIC_DIR/README.md"
if [ -d "$DIST/images" ]; then
  cp -R "$DIST/images" "$PUBLIC_DIR/images"
fi
```

Private/sensitive artifacts never go to `books/` or the public KB.

`~/Downloads/book-inbox` is optional import staging only. Do not treat it as the
primary delivery surface, and do not report a package as done if the user would
have to hunt through `book-inbox` to find the approved public-safe iCloud folder
or the agreed private project folder.
