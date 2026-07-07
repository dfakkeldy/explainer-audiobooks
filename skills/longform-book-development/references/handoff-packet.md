# Handoff Packet

Use this shape when handing a developed longform book project to
`$custom-learning-audiobook`.

## Packet Sections

```markdown
# <Working Title> Handoff Packet

## Production Request

Use `$custom-learning-audiobook` to turn this approved book plan into a complete
learning audiobook package. Include the approved interior pictures as EPUB
figures, build EPUB and combined Markdown, render Echo audio when available, and
report any blockers honestly.

## Status

- Privacy:
- Permission to publish:
- Length target:
- Audience:
- Voice/tone:
- Source-confidence target:
- User approval status:

## Core Promise

What the listener should understand, feel, or be able to do after finishing.

## Boundaries

What to include, avoid, simplify, keep private, or treat as educational-only.

## Outline

| Ch | Working title | Purpose | Core beats | Sources needed | Figures |
|---|---|---|---|---|---|

## Throughlines

Recurring ideas, metaphors, or tensions that should tie chapters together.

## Source Plan

User-provided files, live research needs, Open Notebook corpora, primary sources,
or source-quality constraints. Include retrieval dates for live web sources.

## Figure Plan

| ID | File path | Placement | Alt text | Caption | Provenance/license | Public-safe? |
|---|---|---|---|---|---|---|

Put final package images under `chapters/images/` before running
`build_book.py`. Insert them as standalone Markdown paragraphs:

```markdown
![Useful alt text](images/example.png "Caption shown under the figure")
```

Image paths resolve relative to the chapters directory. Supported formats are
PNG, JPEG, GIF, SVG, and WebP. Do not include pictures whose rights or privacy
status are unclear in a public package.

## Style Notes

Preferred voice, pacing, examples, jokes, repeated language to avoid, vocabulary
to introduce, and any sample passage the user liked.

## Open Questions

Only questions that must be answered before production. If none, say so.

## Acceptance Criteria

What counts as done: EPUB/Markdown, cover, audio, alignment sidecar, README,
visual provenance, copied locations, or public repo package.
```
