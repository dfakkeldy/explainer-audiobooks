# Explainer Audiobooks Agent Guide

This repository contains public audiobook-production methods and tooling plus
public-safe books. Work here may also produce private packages that remain
outside Git.

## Task Routing

- For repository, tooling, test, or instruction maintenance, work directly in
  the repository. Do not invoke a book-production skill unless the task calls
  for book development or production.
- Use `skill/` for long technical explainers.
- Use `skills/custom-learning-audiobook/` for ready-to-produce,
  listener-specific learning books.
- Use `skills/longform-book-development/` for collaborative nonfiction book
  development.
- Use `skills/fiction-book-development/` for fiction development through an
  accepted Markdown manuscript.
- Once selected, the relevant skill owns the detailed production workflow. This
  root guide does not activate a production workflow by itself.

## Context and Current State

- Consult `/Users/dfakkeldy/Developer/knowledge-base` only when the task depends
  on portfolio context, project history, prior decisions, or current business
  state. Self-contained repository, tooling, test, instruction, or artifact
  work does not trigger knowledge-base reading.
- When the knowledge base is relevant, read its `AGENTS.md`, its bundle index,
  and only the smallest relevant project, topic, or status pages.
- Verify current facts in the relevant live repository or service. Before
  editing, inspect the branch, upstream, and working tree, and preserve
  unrelated work.

## Privacy, Licensing, and Artifact Boundaries

- Keep private source notes, raw research, private books, private client or
  prospect material, local narration scratch, and non-public-domain source
  material out of the public repository.
- Public-safe finished books may live under `books/<slug>/` following existing
  conventions. Follow the repository's code and book-content license files.
- `skill/` is the canonical shared source for the installed explainer skill.
- Do not bulk-clean generated or private artifacts. Inspect the exact target
  first; durable project state may live in skill-defined build directories.
- Treat accepted manuscript text and cover art as frozen unless the user
  authorizes changes.
- The selected production skill governs delivery. Keep manuscript acceptance,
  package generation, narration, synchronization, pronunciation and human
  listening, iCloud delivery, repository publication, and website publication
  as separate states.
- Public-safe content is eligible for publication, but public safety alone is
  not authorization to publish or copy it elsewhere.
- Copy a package to iCloud Books only when the requested outcome or selected
  production workflow calls for that delivery step.

## Verification

- Start with the narrowest relevant test, for example:
  `python3 -m unittest tests.<relevant_module> -v`.
- For broad skill or tooling changes, run:
  `python3 -m unittest discover -s tests -v` and
  `python3 tools/validate_skills.py`.
- When the installed-skill or symlink contract changes, also run:
  `python3 tools/validate_custom_learning_skill_install.py`.
- Run `git diff --check` before committing.
- For book artifacts, also follow the selected skill's quality checks. Tool
  tests do not prove narration quality, human listening acceptance, delivery,
  or publication.
- Instruction-only edits do not require a book build or render.

## Repository Workflow

- Preserve unrelated edits and untracked files; do not adopt them as part of
  the task.
- Publish successful requested implementation work as a ready pull request when
  the repository supports that workflow. Diagnosis, read-only review, design,
  and planning do not trigger publication.
- Treat local verification, hosted CI, merge, deployment, delivery, and human
  acceptance as distinct states and report them accurately.
