# Sources and Drift Notes

This appendix is written to be read, not narrated. It is deliberately excluded
from the audiobook spine and from the narrated word count.

## Source snapshot

Every claim in this volume was taken from the official Claude Platform
documentation as it stood on **2026-07-25**. Eighteen pages were captured and
hashed; the manifest lives with the production run. Volumes 1 through 3 of this
series were built against earlier snapshots, and at least one difference is
already visible: the server tools examples showed a different model name one week
earlier than they do here.

## How to read the dated material

Of the 100 recorded claims, 56 describe durable mechanisms, 42 are dated facts true at the snapshot, and 2 describe capabilities that were in beta.
Prices, quotas, model names, tool version strings, beta headers, and platform
availability are all in the dated category. Check the live page before relying on
any of them.

## Pages consulted

- <.../code-execution-tool> — 1 claims
- <.../programmatic-tool-calling> — 1 claims
- <.../web-fetch-tool> — 1 claims
- <https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool> — 11 claims
- <https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool> — 6 claims
- <https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool> — 7 claims
- <https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool> — 6 claims
- <https://platform.claude.com/docs/en/agents-and-tools/tool-use/fine-grained-tool-streaming> — 4 claims
- <https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool> — 7 claims
- <https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview> — 1 claims
- <https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling> — 8 claims
- <https://platform.claude.com/docs/en/agents-and-tools/tool-use/server-tools> — 15 claims
- <https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool> — 3 claims
- <https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference> — 5 claims
- <https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool> — 10 claims
- <https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool> — 9 claims
- <https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool> — 8 claims

## Recorded uncertainty

**UC-001 — What is the additional input-token cost of the current text editor tool version?**

The tool reference publishes a figure for the superseded text_editor_20250429 and none for the current text_editor_20250728.

Disposition: `unresolved-do-not-assert` (claims CP4-072, CP4-074)

**UC-002 — Which per-model additional-token figure should the narration quote for the Bash tool?**

The page gives 325 tokens for one model set and 244 for another; both are dated per-model values.

Disposition: `resolved-narrate-one-dated-example` (claims CP4-067)

**UC-003 — How long does an idle code execution container survive?**

The code execution page describes checkpointing after about five minutes with restoration inside thirty days; the programmatic tool calling page describes idle containers as reclaimed after about five minutes.

Disposition: `resolved-narrate-durable-shape` (claims CP4-038, CP4-088)

**UC-004 — Do the published advisor performance figures generalize beyond Anthropic's own tests?**

Every advisor figure comes from Anthropic internal testing at small sample sizes, and the page instructs readers to validate on their own workload.

Disposition: `resolved-attribute-never-generalize` (claims CP4-048, CP4-050, CP4-084)

**UC-005 — Which model appears in the server tools examples?**

The 2026-07-18 snapshot used for Volume 3 shows claude-opus-4-8 where the 2026-07-25 snapshot shows claude-opus-5.

Disposition: `resolved-usable-as-dated-illustration` (claims CP4-005, CP4-099)

## What this volume deliberately does not cover

Context windows, token counting, prompt caching, cache diagnostics, compaction,
context editing, mid-conversation system messages, the Files API, Skills, the MCP
connector, and cloud platform differences belong to Volume 5. Prompt engineering
and evaluation belong to Volume 6. Errors, rate limits, retries, and cost
optimization as disciplines belong to Volume 7. Managed Agents belong to Volume 9.
Where a tool in this volume genuinely depends on one of those subjects, the
narration names it and declines to teach it.

## Attribution

Anthropic's documentation and API reference are the primary sources. All
explanatory prose, analogies, worked examples, and the Project Desk case study are
original to this book. Performance figures attributed to Anthropic's own testing
are reported as such, with the sample caveats the source states.

