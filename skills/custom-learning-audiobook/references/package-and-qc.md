# Package And QC

## Universal paired-cover gate

New packages require exactly three paired candidates. Each has a 1600×2560
`cover.png` EPUB portrait and a 2400×2400 `m4b-cover.png` M4B square, generated
with `render_cover_pair` from `skill/scripts/cover_pairs.py`. After thumbnail
review and explicit pair selection, create a paired receipt with
`cover_receipts.py select-pair`. Pass both files to `build_book.py` using
`--cover`, `--m4b-cover`, and `--cover-selection`; after narration run
`replace_m4b_cover.py --m4b ... --cover ... --out ... --cover-selection ...
--portrait-cover ...`. Run `cover_receipts.py verify --cover ... --m4b-cover ...
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
  --privacy-classification "$CLASSIFICATION" \
  --permission-to-publish
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
  --prose-receipt "$RUN_ROOT/research/prose-style-receipt.json"

/usr/local/bin/python3 skill/scripts/replace_m4b_cover.py \
  --m4b "$DIST/$SLUG.m4b" \
  --cover "$PAIR/m4b-cover.png" \
  --out "$DIST/$SLUG.covered.m4b" \
  --cover-selection "$DIST/cover-selection.json" \
  --portrait-cover "$PAIR/cover.png"
mv "$DIST/$SLUG.covered.m4b" "$DIST/$SLUG.m4b"

/usr/local/bin/python3 skill/scripts/cover_receipts.py verify \
  --selection "$DIST/cover-selection.json" \
  --cover "$PAIR/cover.png" \
  --m4b-cover "$PAIR/m4b-cover.png" \
  --epub "$DIST/$SLUG.epub" \
  --m4b "$DIST/$SLUG.m4b" \
  --receipt "$DIST/cover-selection.json"

/usr/local/bin/python3 skill/scripts/sync_selected_cover.py \
  --selection "$DIST/cover-selection.json" \
  --cover "$PAIR/cover.png" \
  --epub "$DIST/$SLUG.epub" \
  --m4b "$DIST/$SLUG.m4b" \
  --paired-artifact-dir "$PAIR" \
  --destination "$DELIVERY_DIR" \
  --intent reuse

/usr/local/bin/python3 skill/scripts/sync_selected_cover.py \
  --selection "$DIST/cover-selection.json" \
  --cover "$PAIR/cover.png" \
  --epub "$DIST/$SLUG.epub" \
  --m4b "$DIST/$SLUG.m4b" \
  --paired-artifact-dir "$PAIR" \
  --destination "$DELIVERY_DIR" \
  --intent reuse \
  --apply
```


Use this reference before building, narrating, copying, or reporting a custom
learning audiobook package.

## Build Layout

Use this run layout:

```text
.build/custom-learning-audiobooks/<slug>/
  research/
    coverage-ledger.md
    continuity.md
    prose-qc.md
    editorial-review.md
    visuals.md
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
    <slug>.m4b
    <slug>.alignment.json
    README.md or manifest.json
```

Repeat that directory for `candidate-2/` and `candidate-3/`. After selection,
copy the paired receipt into the selected candidate directory before governed
sync so it contains the nine canonical pair/provenance artifacts.
`cover-selection.json` appears only after the user chooses or requests a mix.

The canonical transient build output stays under `.build/`. A public-safe
package defaults to a durable iCloud Drive delivery copy under:

```text
/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/<Title>/
```

Private or sensitive packages stay in the agreed private project folder and
receive an iCloud Books reading copy only on an explicit user request. Public-safe
final packages may also publish to `books/<slug>/` only through the governed
public sync described below.

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
  prose,
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

Echo owns the M4B/alignment renderer. Build `echo-cli` from the Echo repo when
needed:

```bash
cd /Users/dfakkeldy/Developer/Echo
"$HOME/.claude/bin/xcode-build-gate.sh" --wait && \
  xcodebuild build \
    -project Echo.xcodeproj \
    -scheme echo-cli \
    -destination 'platform=macOS' \
    -parallelizeTargets NO \
    CODE_SIGNING_ALLOWED=NO
```

Find the built binary:

```bash
CLI_DIR=$(xcodebuild -project /Users/dfakkeldy/Developer/Echo/Echo.xcodeproj \
  -scheme echo-cli \
  -destination 'platform=macOS' \
  -showBuildSettings 2>/dev/null \
  | awk -F= '/ TARGET_BUILD_DIR / {gsub(/^ +| +$/, "", $2); print $2; exit}')
CLI="$CLI_DIR/echo-cli"
```

Render with the custom-learning defaults:

```bash
DIST=".build/custom-learning-audiobooks/$SLUG/dist"
WORK=".build/custom-learning-audiobooks/$SLUG/audio-work"
DB=".build/custom-learning-audiobooks/$SLUG/narration.sqlite"

"$CLI" narrate \
  --epub "$DIST/$SLUG.epub" \
  --out "$DIST/$SLUG.m4b" \
  --sidecar "$DIST/$SLUG.alignment.json" \
  --voice am_michael \
  --title "$TITLE" \
  --author "Dan Fakkeldy" \
  --work-dir "$WORK" \
  --db "$DB"
```

If `am_michael` fails because the voice resource is unavailable, retry with
`--voice am_puck` and record the fallback. Do not silently use `af_heart`.

If the command exits partial, rerun with `--resume`. Keep the same `--work-dir`
and `--db`.

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

Run what is available and record anything skipped:

```bash
ffprobe -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 "$DIST/$SLUG.m4b"

python3 -m json.tool "$DIST/$SLUG.alignment.json" >/dev/null
```

Optional Echo QA after narration:

```bash
AUDIOBOOK_ID=$(sqlite3 "$DB" "select id from audiobook order by rowid desc limit 1;")
"$CLI" qa \
  --db "$DB" \
  --audiobook-id "$AUDIOBOOK_ID" \
  --work-dir "$WORK" \
  --report "$DIST/<slug>.narration-qa.json"
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
  --m4b "$DIST/$SLUG.m4b" \
  --receipt "$DIST/cover-selection.json"
```

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
- QC gates passed/skipped.

## Copy Rules

The final cover receipt verification above must pass before any copy. For a
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
  --m4b "$DIST/$SLUG.m4b" \
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
  --m4b "$DIST/$SLUG.m4b" \
  --destination "$DELIVERY_DIR" \
  --intent reuse \
  --apply
```

After the explicit apply succeeds, copy the rest of `dist/` without overwriting
the governed files:

```bash
rsync -a \
  --exclude "cover.png" \
  --exclude "cover-selection.json" \
  --exclude "$SLUG.epub" \
  --exclude "$SLUG.m4b" \
  "$DIST/" "$DELIVERY_DIR/"
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
  --m4b "$DIST/$SLUG.m4b" \
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
  --m4b "$DIST/$SLUG.m4b" \
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
