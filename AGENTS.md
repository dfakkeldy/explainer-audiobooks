# Explainer Audiobooks Agent Guide

Use the business knowledge base at
`/Users/dfakkeldy/Developer/knowledge-base` as operating context for this repo.

Before planning, changing, or answering anything non-trivial here, read:

1. `/Users/dfakkeldy/Developer/knowledge-base/AGENTS.md`
2. `/Users/dfakkeldy/Developer/knowledge-base/bundle/index.md`
3. Relevant KB pages, especially:
   - `/projects/explainer-audiobooks.md`
   - `/topics/echo-workplace-beta-recruitment.md`
   - `/status/2026-07-06-custom-learning-audiobook-skill-design.md`

Then verify the live repo state before making current claims:

- `git status --short --branch`
- current branch/upstream
- relevant open PRs/issues when publishing work
- local generated/private artifacts before deciding what belongs in Git

## Repo Rules

- Keep private/generated book artifacts out of the public repo unless the book is
  explicitly public-safe.
- Do not commit private source notes, raw build research, private client/prospect
  books, local narration scratch, or non-public-domain source material.
- Public-safe finished books may live under `books/<slug>/` following existing
  repo conventions.
- Copy public-safe finished packages to:
  `/Users/dfakkeldy/Library/Mobile Documents/com~apple~CloudDocs/Books`
- For private books, keep delivery artifacts in the private project folder; only
  copy to iCloud Books when the user explicitly wants a private reading copy.
- `skill/` is the canonical shared skill source for both Claude and Codex.
- Preserve unrelated local edits and generated artifacts. If cleanup is needed,
  inspect first and move private/generated scratch out of the repo rather than
  bulk deleting it.
