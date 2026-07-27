# Publishing a Public Edition

This flow is not used when making a book for yourself. Use it only to promote a
finished private book into the public `books/` directory or site.

The private lane stays outside `books/` and public publishing. Copy it into
iCloud Books only when the user explicitly requests it, a private iCloud
reading copy; that request is not public-publishing permission.

## Render or confirm the pair

If the public edition needs a new coordinated pair, follow `cover-art.md` and
render all three candidates before selecting one:

```python
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

## Select and verify

Create the paired selection record. Use `--selection-source user` for a direct
choice or `requested-mix` for a requested mix. Set
`--privacy-classification` truthfully. Pass `--permission-to-publish` only when
the user explicitly authorizes publication of this named edition.

```bash
/usr/local/bin/python3 skill/scripts/cover_receipts.py select-pair \
  --portrait-render-receipt "$PAIR/cover-render.json" \
  --square-render-receipt "$PAIR/m4b-cover-render.json" \
  --out "$PAIR/cover-selection.json" \
  --book-slug "$SLUG" \
  --edition-id "$EDITION_ID" \
  --selection-source user \
  --selected-at "$SELECTED_AT" \
  --privacy-classification "$CLASSIFICATION" \
  --permission-to-publish

/usr/local/bin/python3 skill/scripts/build_book.py \
  --chapters-dir "$RUN_ROOT/chapters" \
  --out-dir "$DIST" \
  --title "$TITLE" \
  --author "Dan Fakkeldy" \
  --contributor "$CONTRIBUTOR" \
  --slug "$SLUG" \
  --cover "$PAIR/cover.png" \
  --m4b-cover "$PAIR/m4b-cover.png" \
  --cover-selection "$PAIR/cover-selection.json"
```

## Narrate the selected square

If the selected square cover changed, the EPUB and M4B must both be rebuilt.
Do not reuse an M4B rendered with different square art, and never patch the new
cover into an old narration.

Set `EXPLAINER_ROOT`, `RUN_ROOT`, `DIST`, `SLUG`, `TITLE`, `VOICE`, `COVER`,
`M4B_COVER`, and the approved Echo source identity exactly as documented in
`skills/echo-narration/references/narrating.md`, then run the governed wrapper:

```bash
export COVER="$PAIR/cover.png"
export M4B_COVER="$PAIR/m4b-cover.png"
"$EXPLAINER_ROOT/skills/echo-narration/scripts/echo_pronunciation_narrate.sh"
```

Follow that reference's **Audio verification** block in full. It resolves
`AUDIOBOOK` only from the accepted selector at
`$RUN_ROOT/research/echo-render-current-accepted.json` and verifies the
immutable M4B, sidecar, audit, input receipt, and success receipt. If the square
did not change, still resolve the existing M4B through that accepted selector;
never point `AUDIOBOOK` at an arbitrary or historical file.

Only after that verification succeeds, verify the paired package:

```bash
/usr/local/bin/python3 skill/scripts/cover_receipts.py verify \
  --selection "$PAIR/cover-selection.json" \
  --cover "$PAIR/cover.png" \
  --m4b-cover "$PAIR/m4b-cover.png" \
  --epub "$DIST/$SLUG.epub" \
  --m4b "$AUDIOBOOK" \
  --receipt "$PAIR/cover-selection.json"
```

## Sync the selected artifacts

Dry-run first and read the reported `new`, `reuse`, `supersede`, or conflict
classification:

```bash
/usr/local/bin/python3 skill/scripts/sync_selected_cover.py \
  --selection "$PAIR/cover-selection.json" \
  --cover "$PAIR/cover.png" \
  --epub "$DIST/$SLUG.epub" \
  --m4b "$AUDIOBOOK" \
  --paired-artifact-dir "$PAIR" \
  --destination "$DELIVERY_DIR" \
  --intent reuse \
  --public-destination
```

When that classification is expected, repeat the same command with `--apply`:

```bash
/usr/local/bin/python3 skill/scripts/sync_selected_cover.py \
  --selection "$PAIR/cover-selection.json" \
  --cover "$PAIR/cover.png" \
  --epub "$DIST/$SLUG.epub" \
  --m4b "$AUDIOBOOK" \
  --paired-artifact-dir "$PAIR" \
  --destination "$DELIVERY_DIR" \
  --intent reuse \
  --public-destination \
  --apply
```

Use `--intent supersede` only for a newer explicit choice. Do not overwrite an
unreceipted or conflicting destination.

## Public package check

Run `verify_public_first_listen.py` on the staged public package. It checks the
authorization record, disclosure, manifest, required files, privacy boundary,
and the relationship between the staged package and public destination before
promotion.

Echo narration exports are immutable. Never mutate a narrated M4B after export.
`replace_m4b_cover.py` is compatibility tooling for legacy artifacts only.
