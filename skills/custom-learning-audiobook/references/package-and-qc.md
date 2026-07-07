# Package And QC

Use this reference before building, narrating, copying, or reporting a custom
learning audiobook package.

## Build Layout

Use this run layout:

```text
.build/custom-learning-audiobooks/<slug>/
  research/
  chapters/
    ch01.md
    ch02.md
  dist/
    <slug>.epub
    <slug>.md
    <slug>.m4b
    <slug>.alignment.json
    cover.png
    README.md or manifest.json
```

The canonical transient build output stays under `.build/`. Public-safe final
packages may also be copied to `books/<slug>/`.

## EPUB And Markdown

From the repo root:

```bash
python3 skill/scripts/build_book.py \
  --chapters-dir .build/custom-learning-audiobooks/<slug>/chapters \
  --out-dir .build/custom-learning-audiobooks/<slug>/dist \
  --title "<Title>" \
  --author "Dan Fakkeldy" \
  --contributor "<model name>" \
  --subtitle "<subtitle>" \
  --slug <slug> \
  --cover .build/custom-learning-audiobooks/<slug>/dist/cover.png
```

Validate:

```bash
unzip -t .build/custom-learning-audiobooks/<slug>/dist/<slug>.epub
wc -w .build/custom-learning-audiobooks/<slug>/chapters/ch*.md
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

Run the narration-style checks from `../../skill/references/narration-style.md`.
At minimum:

- word count matches the chosen length mode,
- no raw code/symbol narration leaks,
- repeated phrase/opening sweep,
- sensitive/private-term scan,
- first chapter and most technical chapter spot-read,
- source-confidence label assigned.

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
- research mode,
- source-confidence label,
- sensitive-topic guardrails,
- output files,
- QC gates passed/skipped.

## Copy Rules

Public-safe, permissioned packages:

```bash
mkdir -p "/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/<Title>"
cp -R "$DIST"/. "/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books/<Title>/"

mkdir -p "books/<slug>"
cp "$DIST/<slug>.epub" "$DIST/<slug>.md" "$DIST/cover.png" "books/<slug>/"
test -f "$DIST/README.md" && cp "$DIST/README.md" "books/<slug>/README.md"
```

Commit only public-safe repo copies. Large `.m4b` and alignment sidecars should
stay out of the public repo unless the repo's current policy explicitly allows
that book and file size.

Private packages:

- Do not copy into `books/`.
- Do not copy into the public KB.
- Copy to iCloud Books only when the user explicitly wants a private reading
  copy.
- Keep private delivery folders under the agreed private path for that run.
