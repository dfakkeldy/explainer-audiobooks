# Package And QC

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
    cover-source-1.png
    cover-spec-1.json
    cover-1.png
    cover-1-thumbnail.png
    cover-1.render.json
    cover-selection.json
    <slug>.epub
    <slug>.md
    images/
    <slug>.m4b
    <slug>.alignment.json
    README.md or manifest.json
```

Repeat the numbered cover source/spec/render/thumbnail/receipt set for candidates
2 and 3. `cover-selection.json` appears only after the user chooses or requests a
mix.

The canonical transient build output stays under `.build/`. The durable local
delivery copy goes to iCloud Drive under:

```text
/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/<Title>/
```

Use that iCloud Drive folder as the findable delivery surface. Public-safe final
packages may also be copied to `books/<slug>/`.

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

Save each art file beside its validated specification. Assign `SLUG` from the run
metadata, then render candidate 1:

```bash
RUN_ROOT=".build/custom-learning-audiobooks/$SLUG"
/usr/local/bin/python3 skill/scripts/make_cover.py \
  --spec "$RUN_ROOT/dist/cover-spec-1.json" \
  --out "$RUN_ROOT/dist/cover-1.png"
```

Repeat for candidates 2 and 3. Human-review each full-size render, generated
160-pixel thumbnail, art-and-type brief, font/palette note, and warning. The
renderer never selects a candidate automatically. Ask the user to choose or
request a mix; a mix becomes a new specification and render.

Only after that choice, assign `SLUG`, `EDITION_ID`, `SELECTED_AT`,
`CLASSIFICATION`, `PERMISSION_TO_PUBLISH`, `TITLE`, `SUBTITLE`, and `CONTRIBUTOR`
from the approved run metadata. `SELECTED_AT` is an ISO-8601 timestamp;
classification is `private`, `public-safe`, or `sensitive`; publication
permission is `denied`, `granted`, or `not-requested`. Use
`selection_source=explicit-user-choice`; for a requested mix, substitute
`requested-mix` after rendering the new specification.

Run the selection and governed build commands now. Run the final verification
stanza after the native Echo step has produced the M4B and before any copy or
delivery:

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
  --cover-selection "$DIST/cover-selection.json"

/usr/local/bin/python3 skill/scripts/cover_receipts.py verify \
  --selection "$DIST/cover-selection.json" \
  --cover "$DIST/cover-$SELECTED.png" \
  --epub "$DIST/$SLUG.epub" \
  --m4b "$DIST/$SLUG.m4b" \
  --receipt "$DIST/cover-selection.json"
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
DIST=".build/custom-learning-audiobooks/<slug>/dist"
WORK=".build/custom-learning-audiobooks/<slug>/audio-work"
DB=".build/custom-learning-audiobooks/<slug>/narration.sqlite"

"$CLI" narrate \
  --epub "$DIST/<slug>.epub" \
  --out "$DIST/<slug>.m4b" \
  --sidecar "$DIST/<slug>.alignment.json" \
  --voice am_michael \
  --title "<Title>" \
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
  deliver EPUB/Markdown with audio marked blocked.
- **User-approved non-Echo preview**: only if the user explicitly asks for it,
  create the preview with a loud `non_echo_audio` status. Do not call it
  Echo-ready, and do not let it replace the native Echo render unless the user
  cancels Echo audio.

## Audio And Alignment QC

Run what is available and record anything skipped:

```bash
ffprobe -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 "$DIST/<slug>.m4b"

python3 -m json.tool "$DIST/<slug>.alignment.json" >/dev/null
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

## Prose QC

Read `../../skill/references/frontier-manuscript-pipeline.md` and run the
narration-style checks from `../../skill/references/narration-style.md`. The
frontier-authored chapter Markdown remains canonical throughout this step.

At minimum:

- word count matches the ledger's **chapter-specific** ranges or has a written
  reason to be outside them; do not pad a short chapter automatically,
- no raw code/symbol narration leaks,
- run `python3 skill/scripts/prose_qc.py --chapters-dir
  .build/custom-learning-audiobooks/<slug>/chapters --out
  .build/custom-learning-audiobooks/<slug>/research/prose-qc.md`,
- have a cheaper reviewer use that report and `coverage-ledger.md` to flag only
  exact locations for redundant ideas, formulaic openings/closings, unexplained
  leaps, shallow concepts, jargon without a concrete case, or missing
  boundaries/counterexamples; it recommends a repair **type**, not replacement
  prose,
- the frontier author accepts/rejects findings and makes every substantive
  content edit before packaging,
- sensitive/private-term scan,
- first chapter and most technical chapter spot-read,
- source-confidence label assigned,
- for illustrated books, every intended figure has alt text, caption, provenance,
  and an `OEBPS/images/` entry in the EPUB.

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

Always create a complete iCloud Drive delivery folder for finished packages
unless the user explicitly says not to copy to iCloud. Assign `ICLOUD_DIR` from
the approved title metadata:

```bash
ICLOUD_DIR="/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/$TITLE"
```

For an existing delivery folder, the following dry run and its reported
classification are mandatory before applying or copying anything:

```bash
/usr/local/bin/python3 skill/scripts/sync_selected_cover.py \
  --selection "$DIST/cover-selection.json" \
  --cover "$DIST/cover-$SELECTED.png" \
  --epub "$DIST/$SLUG.epub" \
  --m4b "$DIST/$SLUG.m4b" \
  --destination "$ICLOUD_DIR" \
  --intent reuse
```

Use `--intent supersede` only for a newer explicit choice. Add `--apply` only
after the reported classification is expected. If a destination has
cover-bearing files but no receipt, it is an `unreceipted` conflict unless the
operation is an explicit supersession. The same dry-run/apply path is safe for a
new destination; after it applies the governed cover, EPUB, M4B, and receipt,
copy the remaining non-cover package files without replacing those four
verified artifacts.

After the explicit apply succeeds, copy the rest of `dist/` without overwriting
the governed files:

```bash
rsync -a \
  --exclude "cover.png" \
  --exclude "cover-selection.json" \
  --exclude "$SLUG.epub" \
  --exclude "$SLUG.m4b" \
  "$DIST/" "$ICLOUD_DIR/"
```

After copying, verify the copied package from the iCloud path, not only from
`.build/`:

```bash
/usr/local/bin/python3 skill/scripts/cover_receipts.py verify \
  --selection "$ICLOUD_DIR/cover-selection.json" \
  --cover "$ICLOUD_DIR/cover.png" \
  --epub "$ICLOUD_DIR/$SLUG.epub" \
  --m4b "$ICLOUD_DIR/$SLUG.m4b" \
  --receipt "$ICLOUD_DIR/cover-selection.json"

unzip -t "$ICLOUD_DIR/$SLUG.epub"
ffprobe -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 "$ICLOUD_DIR/$SLUG.m4b"
test ! -f "$ICLOUD_DIR/$SLUG.alignment.json" || \
  python3 -m json.tool "$ICLOUD_DIR/$SLUG.alignment.json" >/dev/null
```

Public-safe, permissioned packages may also copy the public-facing files to the
repo. If `books/$SLUG/cover-selection.json` already exists, treat it as canonical:
do not replace a different receipt through a routine copy. A replacement needs
the newer explicit choice recorded above, and the package must still be
`public-safe` with `permission_to_publish=granted`.

```bash
mkdir -p "books/$SLUG"
cp "$DIST/$SLUG.epub" "$DIST/$SLUG.md" "books/$SLUG/"
cp "$DIST/cover-$SELECTED.png" "books/$SLUG/cover.png"
cp "$DIST/cover-selection.json" "books/$SLUG/cover-selection.json"
test -f "$DIST/README.md" && cp "$DIST/README.md" "books/$SLUG/README.md"
if [ -d "$DIST/images" ]; then
  cp -R "$DIST/images" "books/$SLUG/images"
fi
```

Commit only public-safe repo copies. Large `.m4b` and alignment sidecars should
stay out of the public repo unless the repo's current policy explicitly allows
that book and file size.

Private packages:

- Do not copy into `books/`.
- Do not copy into the public KB.
- Copy the complete package to the iCloud Drive `Books/<Title>/` delivery folder
  by default, because the user wants finished books to be findable there.
- Keep private delivery folders under the agreed private path for that run.

`~/Downloads/book-inbox` is optional import staging only. Do not treat it as the
primary delivery surface, and do not report a package as done if the user would
have to hunt through `book-inbox` to find the finished book.
