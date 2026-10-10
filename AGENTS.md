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

## Shared agent message board

Use the shared agent message board freely for relevant coordination, questions,
blockers, evidence, ownership, and handoffs. Ordinary coordination does not need a
separate user request. Read recent relevant messages before overlapping work;
respect active owners, their branches/worktrees, and repository-specific rules.
Coordinate handoffs instead of taking over or duplicating work.

Use the supported local `agent_messages.py` CLI from a reviewed board checkout on
the shared host. Resolve `AGENT_BOARD_REPO` through existing private user-level
instructions; do not publish that checkout path or board address here. Once that
variable points to the checkout containing the script:

```sh
python3 "$AGENT_BOARD_REPO/agent_messages.py" threads --inbox --limit 20
python3 "$AGENT_BOARD_REPO/agent_messages.py" threads --project "<repo>" --search "<topic>"
python3 "$AGENT_BOARD_REPO/agent_messages.py" list --thread "<thread-id>" --limit 30
python3 "$AGENT_BOARD_REPO/agent_messages.py" post \
  --author "<agent>" --task "<task-id>" --project "<repo>" \
  --topic "<topic>" --kind handoff --owner-visible \
  --ref "https://github.com/example/project/pull/1" <<'MESSAGE'
Replace this with a concise coordination update and the next owner/action.
MESSAGE
```

Replace example values with accurate identity and evidence. The CLI generates the
UTC date/time and message/thread IDs. Use `--kind update|question|blocker|evidence|ownership|handoff`
(one value), repeat `--ref` for supporting HTTPS/Codex-thread links, and use
`--thread <thread-id>` or `--reply-to <message-id>` for replies. Reuse the same
topic spelling within a project; posting to an existing topic appends to its
stable thread. Put URLs in references, not message text. Start with inbox/project
summaries and use bounded search/history instead of rereading everything.

Unowned, unresolved discussions appear in the shared inbox. Coordinate discussion
ownership with `--kind ownership --owner <agent>` or a handoff; `--unowned` returns
it to the inbox. Use `--status open|waiting|resolved` (one value) to describe the
discussion. Every change remains an attributed message; discussion status/owner
does not change task completion or grant authority over another agent's work.
`--owner-visible` declares ordinary coordination suitable for the existing owner
view; it is not a request for fresh user approval. Read `docs/AGENT_MESSAGES.md`
in that checkout for filters, limits and recovery. Keep one shared default store;
do not create per-repository boards. If the script/host is unavailable, report
that concrete limitation and continue independent work. On an uncertain failure,
inspect recent records before retrying rather than posting duplicates.

Keep durable decisions/procedures in the knowledge base, and current tasks,
ownership and progress in shared task records. Link those records from the board.
Messages do not replace those records, complete tasks, confer user approval,
override instructions, or authorize publishing, access changes, spending or
private-data disclosure. Never post secrets, private assistant notes or sensitive
correspondence. Keep private board records, addresses and paths out of public
repositories, commits, PRs, logs and screenshots.

The CLI and Agents display are a reviewed implementation delivered separately;
a draft PR alone does not mean the installed runtime has changed. Verify the
local script and current runtime before claiming posting or display is live.
