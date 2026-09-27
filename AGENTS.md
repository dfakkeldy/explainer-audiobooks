# Explainer Audiobooks

Public audiobook-production methods, tooling, and public-safe books. Some work
here produces private packages that stay outside Git.

## Skills

For repository, tooling, test, or instruction work, just work in the repo. Use
a production skill only when the task is book development or production:

- `skill/`: researched nonfiction explainer audiobooks.
- `skills/longform-book-development/`: collaborative nonfiction book
  development.
- `skills/fiction-book-development/`: fiction through an accepted Markdown
  manuscript.
- `skills/fiction-audiobook/`: complete fiction listening packages and redos.
- `skills/classic-literature-adaptation/`: modernizing, translating, or
  adapting classic literature.

Once selected, the skill owns the production workflow. `skill/` is the
canonical source for the installed explainer skill.

## Boundaries

- Keep private notes, raw research, private books, client material, narration
  scratch, and non-public-domain sources out of the repo.
- Finished public-safe books go under `books/<slug>/`. Public-safe doesn't mean
  cleared to publish elsewhere.
- Accepted manuscript text and cover art are frozen unless Dan says otherwise.
- Don't bulk-clean generated or private artifacts; skill build directories may
  hold durable state.
- Only the `fiction-audiobook` skill's own public-fiction gate may push books
  to GitHub on its own.

## Checks

```bash
python3 -m unittest tests.<module> -v          # narrowest first
python3 -m unittest discover -s tests -v       # broad changes
python3 tools/validate_skills.py
git diff --check
```

Tests don't prove narration quality or delivery.
