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
  --out "$DIST/cover-selection.json" \
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
  --cover-selection "$DIST/cover-selection.json"

/usr/local/bin/python3 skill/scripts/cover_receipts.py verify \
  --selection "$DIST/cover-selection.json" \
  --cover "$PAIR/cover.png" \
  --m4b-cover "$PAIR/m4b-cover.png" \
  --epub "$DIST/$SLUG.epub" \
  --m4b "$AUDIOBOOK" \
  --receipt "$DIST/cover-selection.json"
```

## Sync the selected artifacts

Dry-run first and read the reported `new`, `reuse`, `supersede`, or conflict
classification:

```bash
/usr/local/bin/python3 skill/scripts/sync_selected_cover.py \
  --selection "$DIST/cover-selection.json" \
  --cover "$PAIR/cover.png" \
  --epub "$DIST/$SLUG.epub" \
  --m4b "$AUDIOBOOK" \
  --paired-artifact-dir "$PAIR" \
  --destination "$DELIVERY_DIR" \
  --intent reuse
```

When that classification is expected, repeat the same command with `--apply`:

```bash
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

Use `--intent supersede` only for a newer explicit choice. Do not overwrite an
unreceipted or conflicting destination.

## Public package check

Run `verify_public_first_listen.py` on the staged public package. It checks the
authorization record, disclosure, manifest, required files, privacy boundary,
and the relationship between the staged package and public destination before
promotion.

Echo narration exports are immutable. Never mutate a narrated M4B after export.
`replace_m4b_cover.py` is compatibility tooling for legacy artifacts only.
