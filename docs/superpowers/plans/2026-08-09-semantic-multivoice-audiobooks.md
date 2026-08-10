# Semantic Multi-Voice Audiobooks Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make source-bound character voices standard for new fiction audiobooks and add sparse, role-based semantic voices as the default for new nonfiction learning audiobooks.

**Architecture:** Keep the landed Echo schema-1 block plan and governed narration wrapper unchanged. Add one closed nonfiction cast envelope plus a deterministic Python validator that joins the frozen EPUB, Echo inventory, semantic cast, and authored plan before the wrapper invokes Echo's authoritative resolver. Keep detailed pedagogy in a new progressively loaded reference so `skill/SKILL.md` stays below its 200-line contract.

**Tech Stack:** Python 3.11 via `/usr/local/bin/python3`, standard-library `argparse`/`dataclasses`/`hashlib`/`json`, JSON Schema draft 2020-12, Markdown skills and references, `unittest`, Bash wrapper contracts, installed Echo PRs 531–533.

## Global Constraints

- Preserve the unrelated `CLAUDE.md` modification in the canonical checkout; work only in the isolated `codex/semantic-multivoice-audiobooks` worktree.
- Do not build, install, repair, or promote Echo; consume the already-landed `export-blocks`, `resolve-voice-plan`, and `--voice-plan` interfaces.
- Do not modify the governed narration wrapper unless a failing nonfiction-lane test proves it incompatible.
- Do not add a third-party dependency; the validator must use the Python standard library.
- Echo remains authoritative for block existence, speakability, range expansion, resolved plan bytes, and plan identity.
- Nonfiction plans use explicit block arrays only; range assignments fail local validation.
- The default `guide` owns at least 75 percent of nonempty paragraph blocks. `memory` owns no more than 15 percent. `field` plus `coach` own no more than 15 percent. All secondary roles together own no more than 25 percent.
- A secondary group contains one to four ordered paragraph blocks using one role. Separate groups have at least two intervening `guide` paragraph blocks.
- Normal casts contain two to four unique known Echo voices and require `guide` plus `memory`; only an explicit listener waiver permits a one-role `guide` cast with no assignments.
- Keep `skill/SKILL.md` below 200 lines and keep private narration ledgers, casts, inventories, plans, captures, and receipts out of public book roots.
- Existing accepted books and renders are never rerendered or mutated automatically.
- A cast or plan change starts a new governed render identity; never reuse captures or resume state across it.

## File Structure

### Create

- `skill/references/semantic-voice-casting.md` — nonfiction role definitions, authoring workflow, budgets, waiver, ear-pass, and exact validator handoff.
- `skill/schemas/semantic-voice-cast-v1.schema.json` — closed public shape of the nonfiction cast envelope.
- `skill/scripts/semantic_voice_cast.py` — strict cross-file validator and safe argv0 handoff; it does not invoke Echo or infer roles.
- `tests/test_semantic_voice_cast.py` — unit and CLI tests for source binding, semantic budgets, spacing, plan agreement, paths, and waiver behavior.
- `tests/test_semantic_multivoice_skill_contract.py` — cross-document behavior contract for the audiobook, longform, narration, fiction, and README guidance.

### Modify

- `skill/SKILL.md` — route nonfiction production through semantic block casting while staying lean.
- `skill/references/learning-design.md` — plan semantic roles alongside learning jobs.
- `skill/references/road-book-mode.md` — explain voices as stable retrieval/re-entry cues.
- `skill/references/narration-style.md` — require self-contained secondary paragraphs and memory-after-teaching.
- `skills/longform-book-development/SKILL.md` — include semantic voice design in a complete handoff.
- `skills/longform-book-development/references/handoff-packet.md` — add the exact semantic-cast fields without guessed Echo block IDs.
- `skills/echo-narration/references/narrating.md` — generalize the source-bound procedure across nonfiction semantic casts and fiction character casts.
- `skills/fiction-audiobook/SKILL.md` — state that landed character-level block casting is the standard fiction path.
- `README.md` — replace stale chapter-level fiction wording and describe semantic nonfiction voices.
- `tools/validate_skills.py` — require and import-check the new script, schema, and reference.
- `tests/test_audiobook_skill_contract.py` — assert the main skill routes to semantic block casting and remains lean.
- `tests/test_audiobook_longform_handoff_contract.py` — assert semantic role information crosses the handoff boundary.
- `tests/test_echo_narration_contract.py` — assert the shared block runbook retains separate deterministic cast validators.

## Stable Interfaces

### Semantic cast JSON

Use this exact schema-1 shape:

```json
{
  "schemaVersion": 1,
  "narrationMode": "semantic-block",
  "source": {
    "epubFileName": "example.epub",
    "epubSHA256": "0000000000000000000000000000000000000000000000000000000000000000",
    "inventoryFileName": "echo-block-inventory-0000000000000000000000000000000000000000000000000000000000000000.json",
    "inventorySHA256": "1111111111111111111111111111111111111111111111111111111111111111"
  },
  "defaultRoleID": "guide",
  "roles": [
    {"roleID": "guide", "voiceID": "am_michael"},
    {"roleID": "memory", "voiceID": "bf_emma"}
  ],
  "groups": [
    {"groupID": "memory-001", "roleID": "memory", "blocks": ["s1-b4"]}
  ],
  "authoredVoicePlan": {
    "fileName": "echo-voice-plan.json",
    "sha256": "2222222222222222222222222222222222222222222222222222222222222222"
  },
  "singleVoiceWaiver": null
}
```

The only allowed roles, in declaration order, are `guide`, `memory`, `field`, and `coach`; omitted optional roles close the gap rather than changing order. Group IDs match `^(memory|field|coach)-[0-9]{3}$`. A waiver replaces `null` with exactly:

```json
{
  "recordedIn": "source/brief.md",
  "reason": "Listener explicitly requested one voice."
}
```

When the waiver is present, `roles` contains only `guide`, `groups` and Echo `assignments` are empty, and the authored plan still binds the frozen EPUB and guide voice.

### Python API and CLI

`skill/scripts/semantic_voice_cast.py` exports:

```python
class SemanticVoiceCastError(ValueError):
    pass

@dataclass(frozen=True)
class ValidationResult:
    voice_plan: Path
    paragraph_block_count: int
    guide_block_count: int
    role_block_counts: dict[str, int]

def validate_cast(
    cast_path: Path,
    inventory_path: Path,
    voice_plan_path: Path,
    epub_path: Path,
) -> ValidationResult:
    raise NotImplementedError
```

The command is:

```text
semantic_voice_cast.py validate-cast \
  --cast ABSOLUTE_PATH --inventory ABSOLUTE_PATH \
  --voice-plan ABSOLUTE_PATH --epub ABSOLUTE_PATH \
  [--format json|argv0]
```

Default `json` output is compact sorted-key JSON with `guideBlockCount`, `paragraphBlockCount`, `roleBlockCounts`, and `voicePlan`. `argv0` output is exactly the two NUL-terminated tokens `--voice-plan` and the canonical absolute authored-plan path; it is the only shell handoff. Errors go to stderr and exit 65; argument-shape errors use argparse's exit 2.

Derive `RUN_ROOT` from a cast at
`$RUN_ROOT/_production/narration/semantic-voice-cast.json`. Require the authored
plan in that same directory, the inventory at
`$RUN_ROOT/research/$INVENTORY_FILE_NAME`, and the EPUB at
`$RUN_ROOT/dist/$EPUB_FILE_NAME`. The two filename variables are read from the
cast's `source` object. These exact canonical paths enforce the private
run boundary without accepting a user-supplied root.

### Authored Echo plan agreement

The Echo schema-1 plan must declare speakers in the same order and with the same role/voice pairs as the cast. Its `defaultSpeakerID` is `guide`. Its assignment array has exactly one entry per cast group, in the same order:

```json
{"speakerID": "memory", "blocks": ["s1-b4"]}
```

No `range` key is accepted. This deliberately makes semantic intent and authored Echo bytes structurally comparable without resolving or expanding a plan outside Echo.

---

### Task 1: Capture the Pre-Change Skill Baseline

**Files:**
- Create ignored evidence: `.superpowers/sdd/2026-08-09-semantic-multivoice-audiobooks/baseline.md`
- Read: `skill/SKILL.md`
- Read: `skills/echo-narration/references/narrating.md`

**Interfaces:**
- Consumes: the current unmodified audiobook skill and narration reference.
- Produces: verbatim examples of the behavior the new guidance must correct; no tracked repository change.

- [ ] **Step 1: Run three fresh-context no-guidance controls**

Use fresh subagents with no conversation fork and give each only the current skill path plus one prompt. Do not mention the intended solution.

```text
Use the audiobook skill at /Users/dfakkeldy/Developer/explainer-audiobooks/.worktrees/semantic-multivoice-audiobooks/skill/SKILL.md. Plan the narration voices for a beginner road-book about Git recovery that has Key points checkpoints, memorable terms, worked incidents, and safety warnings. Return the voice plan and the authoring steps you would follow.
```

```text
Use the audiobook skill at /Users/dfakkeldy/Developer/explainer-audiobooks/.worktrees/semantic-multivoice-audiobooks/skill/SKILL.md. You have a frozen nonfiction EPUB and want several Echo voices to keep it engaging. Time is short, so propose the fastest defensible mapping and explain whether you would infer assignments from terms, headings, or quotations.
```

```text
Use the audiobook skill at /Users/dfakkeldy/Developer/explainer-audiobooks/.worktrees/semantic-multivoice-audiobooks/skill/SKILL.md. A listener requested a multi-voice learning audiobook, but one secondary voice is unavailable during preflight. Decide what to render and what evidence or approval is required.
```

- [ ] **Step 2: Record the baseline verbatim**

Create the ignored report with one section per prompt. Record whether the response uses chapter rotation, decorative alternation, isolated-term switching, automatic keyword/quotation inference, unstable roles, rapid switching, or silent single-voice fallback. Quote the exact decision and rationale; do not summarize it into the desired answer.

- [ ] **Step 3: Confirm a real guidance gap exists**

Expected: at least one response lacks stable semantic roles or the fail-closed waiver boundary. If all three independently produce the complete approved contract, stop and report that prose guidance is not justified; continue only with deterministic validator work explicitly authorized by the user.

No commit: this is RED evidence for skill authoring and remains ignored.

### Task 2: Define the Closed Cast Contract and Source Binding

**Files:**
- Create: `skill/schemas/semantic-voice-cast-v1.schema.json`
- Create: `skill/scripts/semantic_voice_cast.py`
- Create: `tests/test_semantic_voice_cast.py`
- Modify: `tools/validate_skills.py`

**Interfaces:**
- Consumes: `VOICE_IDS` from `skills/echo-narration/scripts/echo_voice_plan.py` by loading that sibling repository script without copying the catalog.
- Produces: `SemanticVoiceCastError`, `ValidationResult`, `validate_cast`, and the `validate-cast` CLI defined above.

- [ ] **Step 1: Write fixture builders and failing source-contract tests**

Create `tests/test_semantic_voice_cast.py`. Import the missing script with `importlib.util`; add a `SemanticCastFixture` that writes canonical JSON with `json.dumps(payload, sort_keys=True, indent=2) + "\n"`. Its valid inventory contains 20 ordered nonempty paragraph blocks (`s0-b0` through `s0-b19`), its memory group owns `s0-b4`, and its plan mirrors the cast.

Add these exact tests:

```python
def test_valid_cast_binds_epub_inventory_roles_and_plan(self) -> None:
    result = module.validate_cast(
        self.fixture.cast, self.fixture.inventory,
        self.fixture.plan, self.fixture.epub,
    )
    self.assertEqual(self.fixture.plan, result.voice_plan)
    self.assertEqual(20, result.paragraph_block_count)
    self.assertEqual(19, result.guide_block_count)
    self.assertEqual({"memory": 1}, result.role_block_counts)

def test_rejects_duplicate_unknown_and_noncanonical_json(self) -> None:
    # Independently replace cast bytes with a duplicate schemaVersion key,
    # add an `extra` root key, and write valid JSON without canonical framing.
    # Each call raises SemanticVoiceCastError with duplicate/unknown/canonical.

def test_rejects_stale_or_mismatched_source_bytes(self) -> None:
    # Independently mutate EPUB bytes, inventory bytes, source EPUB filename,
    # inventory filename, authored plan bytes, and authored plan filename.
    # Each call raises with the corresponding source/hash/name boundary.

def test_rejects_noncanonical_symlinked_or_nonregular_paths(self) -> None:
    # For each of cast, inventory, plan, and EPUB, pass a relative path,
    # symlink, missing path, and directory. Every case raises before parsing.
```

The comments above enumerate the full parameter tables; implement them as `subTest` loops with exact mutations rather than leaving prose assertions.

- [ ] **Step 2: Run the new module and confirm RED**

Run:

```bash
/usr/local/bin/python3 -m unittest tests.test_semantic_voice_cast -v
```

Expected: import/setup failure because `skill/scripts/semantic_voice_cast.py` does not exist.

- [ ] **Step 3: Add the JSON Schema**

Write draft 2020-12 schema with `$id` under the repository URL. Use `additionalProperties: false` for every object, exact required arrays, role and block ID enums/patterns, one-to-four blocks per group, SHA-256 patterns, and `singleVoiceWaiver` as `oneOf` null or the exact two-field object. JSON Schema documents shape; Python owns hashes, ordering, budgets, and cross-file rules.

- [ ] **Step 4: Implement strict parsing and source binding**

In `semantic_voice_cast.py`, implement these private helpers with explicit error labels:

```python
def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise SemanticVoiceCastError(f"duplicate JSON key: {key}")
        result[key] = value
    return result

def require_regular_canonical(path: Path, label: str) -> None:
    if not path.is_absolute() or path.is_symlink() or path.resolve(strict=False) != path:
        raise SemanticVoiceCastError(f"{label} must be canonical and not a symlink: {path}")
    try:
        mode = path.stat().st_mode
    except FileNotFoundError as error:
        raise SemanticVoiceCastError(f"{label} is missing: {path}") from error
    if not stat.S_ISREG(mode):
        raise SemanticVoiceCastError(f"{label} must be a regular file: {path}")

def read_closed_json(path: Path, label: str, expected_keys: frozenset[str]) -> dict[str, object]:
    require_regular_canonical(path, label)
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SemanticVoiceCastError(f"{label} is not valid UTF-8 JSON") from error
    if not isinstance(value, dict) or set(value) != expected_keys:
        raise SemanticVoiceCastError(f"{label} has unexpected keys")
    return value

def canonical_json(payload: object) -> bytes:
    return (json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode()

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
```

Validate the cast's closed nested objects and types directly rather than importing a JSON Schema runtime. Derive the run root from the exact `_production/narration/semantic-voice-cast.json` suffix and require the plan, inventory, and EPUB at the stable paths defined above. Validate the Echo inventory as version 1 with exact `source.epub` and a block array containing unique IDs and sequence indexes. Accept only the documented Echo block keys: `id`, `kind`, `text`, `chapterIndex`, `sequenceIndex`, `wordCount`, plus `imagePath` only for image blocks.

Load `echo_voice_plan.py` from the repository-relative path and reuse `VOICE_IDS`. Do not import fiction preferences or duplicate the catalog.

- [ ] **Step 5: Register the support files in skill validation**

Extend `tools/validate_skills.py` so `main()` requires the schema and script to exist, calls `validate_python_helper("skill/scripts/semantic_voice_cast.py")`, and verifies `--help` returns usage. The reference is registered when Task 4 creates it. Do not add a third-party JSON Schema validator.

- [ ] **Step 6: Run tests and make GREEN**

Run:

```bash
/usr/local/bin/python3 -m unittest tests.test_semantic_voice_cast tests.test_validate_skills -v
/usr/local/bin/python3 tools/validate_skills.py
```

Expected: all tests pass and `validate_skills: clean`.

- [ ] **Step 7: Commit the closed contract**

```bash
git add skill/schemas/semantic-voice-cast-v1.schema.json \
  skill/scripts/semantic_voice_cast.py tests/test_semantic_voice_cast.py \
  tools/validate_skills.py
git commit -m "feat(narration): validate semantic voice casts"
```

### Task 3: Enforce Semantic Budgets, Spacing, Waivers, and Safe Handoff

**Files:**
- Modify: `skill/scripts/semantic_voice_cast.py`
- Modify: `tests/test_semantic_voice_cast.py`

**Interfaces:**
- Consumes: the closed source-bound documents and Python API from Task 2.
- Produces: complete semantic validation plus exact JSON/argv0 CLI output.

- [ ] **Step 1: Add failing role and plan-agreement tests**

Add parameterized tests for these exact failures:

```python
def test_roles_are_ordered_unique_known_stable_and_used(self) -> None:
    invalid = (
        ("missing-memory", [guide], []),
        ("wrong-order", [memory, guide], [memory_group]),
        ("duplicate-role", [guide, memory, memory], [memory_group]),
        ("duplicate-voice", [guide_am_michael, memory_am_michael], [memory_group]),
        ("unknown-voice", [guide, memory_not_a_voice], [memory_group]),
        ("unused-field", [guide, memory, field], [memory_group]),
        ("guide-group", [guide, memory], [group(role="guide")]),
    )
    # Every case raises with a role-specific message.

def test_cast_groups_match_echo_assignments_exactly(self) -> None:
    # Independently change plan speaker order, default speaker, voice,
    # assignment order, speakerID, block order, add a range, omit a group,
    # and add an unrecorded assignment. Every case raises.
```

- [ ] **Step 2: Add failing paragraph, budget, and spacing tests**

Use a 20-paragraph fixture so percentage boundaries are exact. In separate fixtures, assert acceptance at memory 3/20; memory 1/20 plus field+coach 3/20; and all-secondary 5/20. Assert rejection at memory 4/20, field+coach 4/20, or all-secondary 6/20.

Add exact failures for a heading/image/code/empty paragraph assignment; duplicate block; more than four blocks in one group; mixed/nonmatching group ID and role; noncontiguous blocks inside a group; groups separated by zero or one guide paragraph; unsorted groups; and an inventory with duplicate IDs or sequence indexes.

- [ ] **Step 3: Add failing waiver tests**

Assert that one-role output fails with a null waiver. With the exact waiver object, accept only one guide role, no groups, one guide speaker, and no plan assignments. Reject a waiver combined with memory, any group, a different `recordedIn`, an empty reason, or extra waiver keys.

- [ ] **Step 4: Add failing CLI byte-contract tests**

```python
def test_cli_emits_compact_json_and_exact_argv0(self) -> None:
    command = [
        sys.executable, str(MODULE_PATH), "validate-cast",
        "--cast", str(self.fixture.cast),
        "--inventory", str(self.fixture.inventory),
        "--voice-plan", str(self.fixture.plan),
        "--epub", str(self.fixture.epub),
    ]
    json_run = subprocess.run(command + ["--format", "json"], capture_output=True)
    self.assertEqual(0, json_run.returncode)
    self.assertEqual(expected_compact_json + b"\n", json_run.stdout)
    argv_run = subprocess.run(command + ["--format", "argv0"], capture_output=True)
    self.assertEqual(b"--voice-plan\0" + os.fsencode(plan) + b"\0", argv_run.stdout)
    self.assertEqual(b"", argv_run.stderr)

def test_cli_failure_emits_no_handoff_and_exits_65(self) -> None:
    # Corrupt the cast, run both formats, and require returncode 65,
    # empty stdout, and one concise `semantic voice cast:` stderr line.
```

- [ ] **Step 5: Run the focused module and verify RED**

Run:

```bash
/usr/local/bin/python3 -m unittest tests.test_semantic_voice_cast -v
```

Expected: new semantic and CLI tests fail while Task 2 source-binding tests remain green.

- [ ] **Step 6: Implement semantic validation**

Build an ordered list of eligible paragraphs where `kind == "paragraph"`, `text.strip()` is nonempty, and `wordCount` is a positive integer. Map block ID to paragraph position. Require each group to name one to four consecutive eligible positions, groups to be ordered, and `next_start - previous_end - 1 >= 2`.

Count blocks per non-guide role and enforce budgets with integer cross-multiplication:

```python
require(memory_count * 100 <= paragraph_count * 15, "memory exceeds 15 percent")
require((field_count + coach_count) * 100 <= paragraph_count * 15,
        "field plus coach exceeds 15 percent")
require(sum(role_counts.values()) * 100 <= paragraph_count * 25,
        "secondary roles exceed 25 percent")
```

Derive `guide_block_count = paragraph_count - sum(role_counts.values())`. Require every declared non-guide role to own at least one group. Compare role declarations and groups to the authored Echo plan structurally and reject every `range` key before Echo resolution.

- [ ] **Step 7: Implement the CLI**

Use subparsers so the only command is `validate-cast`. Parse all four paths as `Path`, call `validate_cast`, and emit either compact JSON or the two-token NUL record. Catch only `SemanticVoiceCastError`, write one error line, and return 65. Never use `eval`, shell interpolation, or invoke Echo.

- [ ] **Step 8: Run focused and regression tests**

```bash
/usr/local/bin/python3 -m unittest tests.test_semantic_voice_cast tests.test_echo_voice_plan -v
/usr/local/bin/python3 tools/validate_skills.py
```

Expected: all pass; legacy chapter and Echo block-plan behavior is unchanged.

- [ ] **Step 9: Commit semantic enforcement**

```bash
git add skill/scripts/semantic_voice_cast.py tests/test_semantic_voice_cast.py
git commit -m "fix(narration): enforce sparse semantic voice roles"
```

### Task 4: Teach Nonfiction Authors and Longform Handoffs the Semantic Cast

**Files:**
- Create: `skill/references/semantic-voice-casting.md`
- Create: `tests/test_semantic_multivoice_skill_contract.py`
- Modify: `skill/SKILL.md`
- Modify: `skill/references/learning-design.md`
- Modify: `skill/references/road-book-mode.md`
- Modify: `skill/references/narration-style.md`
- Modify: `skills/longform-book-development/SKILL.md`
- Modify: `skills/longform-book-development/references/handoff-packet.md`
- Modify: `tools/validate_skills.py`
- Modify: `tests/test_audiobook_skill_contract.py`
- Modify: `tests/test_audiobook_longform_handoff_contract.py`

**Interfaces:**
- Consumes: `semantic_voice_cast.py validate-cast` and the approved role contract.
- Produces: one discoverable nonfiction authoring workflow and a complete longform handoff without guessed block IDs.

- [ ] **Step 1: Write failing cross-document behavior tests**

In `tests/test_semantic_multivoice_skill_contract.py`, load and normalize the affected Markdown files. Add these tests:

```python
def test_nonfiction_uses_stable_semantic_roles_not_chapter_rotation(self) -> None:
    for marker in ("`guide`", "`memory`", "`field`", "`coach`",
                   "75 percent", "15 percent", "25 percent"):
        self.assertIn(marker, combined)
    self.assertIn("semantic-voice-casting.md", audiobook)
    self.assertIn("semantic_voice_cast.py", semantic_reference)
    self.assertNotIn("For a mixed-voice book, pass one repeatable mapping", nonfiction_section)

def test_memory_voice_follows_teaching_and_uses_complete_paragraphs(self) -> None:
    for marker in ("after", "already-taught", "self-contained paragraph",
                   "missed the preceding thirty seconds"):
        self.assertIn(marker, normalized_guidance)

def test_longform_handoff_plans_roles_but_never_guesses_echo_blocks(self) -> None:
    for marker in ("Semantic Voice Plan", "candidate Echo voices",
                   "secondary role", "frozen EPUB"):
        self.assertIn(marker, packet)
    self.assertIn("does not contain Echo block IDs", packet)

def test_single_voice_requires_an_explicit_listener_waiver(self) -> None:
    self.assertIn("single-voice", combined)
    self.assertIn("source/brief.md", combined)
    self.assertIn("explicit listener waiver", combined)
    self.assertNotIn("silently fall back", combined)
```

Extend `tests/test_audiobook_skill_contract.py` to require the semantic reference and keep `len(lines) < 200`. Extend the longform handoff test's shared requirements with `semantic`, `role`, `candidate Echo voices`, and `frozen EPUB`.

- [ ] **Step 2: Run contract tests and verify RED**

```bash
/usr/local/bin/python3 -m unittest \
  tests.test_semantic_multivoice_skill_contract \
  tests.test_audiobook_skill_contract \
  tests.test_audiobook_longform_handoff_contract -v
```

Expected: failures for the missing reference and semantic handoff markers.

- [ ] **Step 3: Write the semantic casting reference**

Create a concise reference with these sections in order:

1. `Core principle` — voice changes are retrieval cues, not decoration.
2. `Stable roles` — the exact guide/memory/field/coach table and budgets.
3. `Select the cast` — audition candidate voices on the same neutral passage, respect listener preferences and exclusions, keep roles audibly distinct without gender/accent stereotypes, and fail rather than silently substitute an unavailable secondary voice.
4. `Plan while writing` — ledger path, memory-after-teaching, whole-paragraph and cold-re-entry rules.
5. `Freeze, inventory, and assign` — no guessed IDs; exact private paths and Echo inventory boundary.
6. `Validate and hand off` — a status-preserving `mktemp`/argv0 Bash function analogous to fiction's function, calling `semantic_voice_cast.py` with all four absolute paths and requiring exactly `--voice-plan` plus the authored plan.
7. `Resume and rerender` — revalidate the same vector; cast changes create new runs.
8. `Waiver and listening review` — explicit brief evidence only; ear-pass checks contrast, calmness, role meaning, and road-book intelligibility.

The reference must state that local validation does not decide Echo speakability or plan identity and must link to `skills/echo-narration/references/narrating.md` for operational rendering.

Add `skill/references/semantic-voice-casting.md` to the nonfiction support paths required by `tools/validate_skills.py`.

- [ ] **Step 4: Route the main audiobook skill without growing it**

Replace the single narrator default row with `Semantic cast | guide am_michael; memory plus optional field/coach; never af_heart`. Add at most one short paragraph to Outline and one to Produce: plan the ledger with the new reference, then freeze/inventory/validate and pass its argv0 vector to the narration reference. Compress nearby prose as needed so the file remains below 200 lines.

- [ ] **Step 5: Update learning and prose guidance**

In learning design, add a semantic role to each planned checkpoint/case/action only when earned. In road-book mode, explain that a stable memory voice helps re-entry and retrieval but cannot substitute for recurrence and clear prose. In narration style, require complete secondary paragraphs, teach-before-memory, no isolated-word emphasis, and no new checkpoint facts.

- [ ] **Step 6: Extend the longform handoff**

Add `## Semantic Voice Plan` under Voice Direction with selected roles, candidate voices, passages/section jobs expected to earn them, listener preferences/exclusions, and the frozen-EPUB mapping boundary. Update completion criteria and the main longform skill so a complete audiobook handoff includes this section but explicitly does not contain Echo block IDs.

- [ ] **Step 7: Run contracts and keep the skill lean**

```bash
/usr/local/bin/python3 -m unittest \
  tests.test_semantic_multivoice_skill_contract \
  tests.test_audiobook_skill_contract \
  tests.test_audiobook_longform_handoff_contract -v
wc -l skill/SKILL.md
```

Expected: all pass and `skill/SKILL.md` reports at most 199 lines.

- [ ] **Step 8: Commit nonfiction guidance**

```bash
git add skill/SKILL.md skill/references/semantic-voice-casting.md \
  skill/references/learning-design.md skill/references/road-book-mode.md \
  skill/references/narration-style.md \
  skills/longform-book-development/SKILL.md \
  skills/longform-book-development/references/handoff-packet.md \
  tools/validate_skills.py \
  tests/test_semantic_multivoice_skill_contract.py \
  tests/test_audiobook_skill_contract.py \
  tests/test_audiobook_longform_handoff_contract.py
git commit -m "docs(audiobook): make semantic voice roles the default"
```

### Task 5: Generalize the Echo Runbook and Activate Fiction Wording

**Files:**
- Modify: `skills/echo-narration/references/narrating.md`
- Modify: `skills/fiction-audiobook/SKILL.md`
- Modify: `README.md`
- Modify: `tests/test_echo_narration_contract.py`
- Modify: `tests/test_semantic_multivoice_skill_contract.py`

**Interfaces:**
- Consumes: fiction `validate-cast --format argv0`, nonfiction `semantic_voice_cast.py validate-cast --format argv0`, and the existing governed wrapper.
- Produces: one source-bound operational procedure with mode-specific prevalidation and unchanged block receipts.

- [ ] **Step 1: Add failing runbook boundary tests**

Add to `tests/test_echo_narration_contract.py`:

```python
def test_source_bound_runbook_supports_semantic_and_character_casts(self) -> None:
    normalized = self.normalized(self.narrating)
    for marker in ("Nonfiction semantic cast", "Fiction character cast",
                   "semantic_voice_cast.py", "fiction_voice_preferences.py",
                   "export-blocks", "resolve-voice-plan", "--voice-plan"):
        self.assertIn(marker, normalized)
    self.assertIn("Echo alone decides block existence", normalized)

def test_block_handoffs_reject_invalid_casts_before_the_wrapper(self) -> None:
    self.assertGreaterEqual(self.narrating.count("load_"), 2)
    self.assertGreaterEqual(self.narrating.count("must be --voice-plan"), 2)
    self.assertNotIn("eval", self.narrating)
```

Extend the cross-document test to require `character-level`, `source-bound`, and `standard` in fiction/README text and to reject the phrase `chapter-level multi-voice Echo cast`.

- [ ] **Step 2: Run contract tests and verify RED**

```bash
/usr/local/bin/python3 -m unittest \
  tests.test_echo_narration_contract \
  tests.test_semantic_multivoice_skill_contract -v
```

Expected: the new nonfiction runbook and stale-wording assertions fail.

- [ ] **Step 3: Restructure only the block-mode prose**

Rename `Fiction source-bound block voices` to `Source-bound block voices`. Keep the installed renderer inventory, lease, Echo resolution, wrapper, resume, partial-render, and evidence commands unchanged. Add a short mode-selection subsection:

- nonfiction semantic cast: follow `skill/references/semantic-voice-casting.md` and load its validated argv0 vector;
- fiction character cast: follow `express-fiction-craft.md` and load `fiction_voice_preferences.py` argv0.

Share the common rule that neither validator infers speakers, expands ranges, or computes resolved identity. Retain Echo's sole authority and the exact `--voice-plan` vector on every first, resume, and partial invocation. Do not duplicate the lengthy common wrapper commands.

- [ ] **Step 4: Correct fiction and README wording**

In `skills/fiction-audiobook/SKILL.md`, state near the opening that new editions use the landed source-bound character-level cast as the standard. Preserve its existing explicit speaker authorship, three-to-five voice, preference, public gate, and receipt behavior. In README, replace `chapter-level multi-voice Echo cast` with `source-bound character-level Echo cast`; add one sentence to the nonfiction skill description explaining stable semantic guide/memory/field/coach roles.

- [ ] **Step 5: Run runbook, fiction, and validator regressions**

```bash
/usr/local/bin/python3 -m unittest \
  tests.test_echo_narration_contract \
  tests.test_semantic_multivoice_skill_contract \
  tests.test_fiction_audiobook_integration \
  tests.test_fiction_voice_preferences -v
```

Expected: all pass; fiction block evidence and public packaging remain unchanged.

- [ ] **Step 6: Commit shared operational guidance**

```bash
git add skills/echo-narration/references/narrating.md \
  skills/fiction-audiobook/SKILL.md README.md \
  tests/test_echo_narration_contract.py \
  tests/test_semantic_multivoice_skill_contract.py
git commit -m "docs(narration): route semantic and character block casts"
```

### Task 6: Forward-Test the Revised Skills and Close Real Gaps

**Files:**
- Modify only when a forward-test exposes a real omission: `skill/SKILL.md`, `skill/references/semantic-voice-casting.md`, `skills/echo-narration/references/narrating.md`, or their contract tests.
- Update ignored evidence: `.superpowers/sdd/2026-08-09-semantic-multivoice-audiobooks/forward.md`

**Interfaces:**
- Consumes: the same three prompts and scoring categories from Task 1, now with the revised skill.
- Produces: evidence that another agent can apply semantic casting without leaked design context.

- [ ] **Step 1: Re-run the three baseline prompts in fresh contexts**

Use new no-fork subagents. Point them at the revised `skill/SKILL.md`; do not give them the design spec, plan, expected answer, baseline report, or this conversation.

- [ ] **Step 2: Score every response manually**

Require all responses to preserve stable semantic roles, guide dominance, complete paragraph blocks, memory-after-teaching, frozen-EPUB inventory mapping, no inference, Echo resolution authority, and explicit single-voice waiver behavior. Record exact quotes and any new rationalization in `forward.md`.

- [ ] **Step 3: Add one missing-information variation**

Prompt:

```text
Use the audiobook skill at /Users/dfakkeldy/Developer/explainer-audiobooks/.worktrees/semantic-multivoice-audiobooks/skill/SKILL.md. Prepare a semantic Echo cast for a short road-book, but the brief does not say whether the listener accepts a single voice and the final EPUB has not been built yet. Produce only actions that are valid now and name what must wait.
```

Expected: plan roles and ledger now; do not invent waiver evidence or block IDs; wait for the frozen EPUB before inventory and operational plan assignment.

- [ ] **Step 4: Refactor only against observed failures**

If an agent finds a new loophole, first add a failing string/shape contract that names the missing positive instruction, then add the smallest guidance sentence or recipe that closes it. Do not add generic warnings or expand unrelated skill prose. Re-run the failing prompt in a fresh context.

- [ ] **Step 5: Run focused tests after any refactor**

```bash
/usr/local/bin/python3 -m unittest \
  tests.test_semantic_voice_cast \
  tests.test_semantic_multivoice_skill_contract \
  tests.test_audiobook_skill_contract \
  tests.test_echo_narration_contract -v
```

Expected: all pass. If no tracked changes were needed, make no empty commit. Otherwise commit:

```bash
git add skill/SKILL.md skill/references/semantic-voice-casting.md \
  skills/echo-narration/references/narrating.md \
  tests/test_semantic_multivoice_skill_contract.py \
  tests/test_audiobook_skill_contract.py tests/test_echo_narration_contract.py
git commit -m "fix(skills): close semantic casting guidance gaps"
```

### Task 7: Verify, Review, and Publish the Ready Pull Request

**Files:**
- Verify all changed files.
- Do not add generated test caches or ignored subagent reports.

**Interfaces:**
- Consumes: all prior commits.
- Produces: a clean pushed branch and ready pull request with distinct local/CI/listening states.

- [ ] **Step 1: Run the focused suite**

```bash
/usr/local/bin/python3 -m unittest \
  tests.test_semantic_voice_cast \
  tests.test_semantic_multivoice_skill_contract \
  tests.test_audiobook_skill_contract \
  tests.test_audiobook_longform_handoff_contract \
  tests.test_echo_narration_contract \
  tests.test_echo_voice_plan \
  tests.test_fiction_audiobook_integration \
  tests.test_fiction_voice_preferences -v
```

Expected: all pass with no warnings or errors.

- [ ] **Step 2: Run repository-wide skill verification**

```bash
/usr/local/bin/python3 -m unittest discover -s tests -v
/usr/local/bin/python3 tools/validate_skills.py
git diff --check origin/main...HEAD
```

Expected: full suite passes, `validate_skills: clean`, and no whitespace errors.

- [ ] **Step 3: Inspect scope and cleanliness**

```bash
git status --short --branch
git diff --stat origin/main...HEAD
git log --oneline origin/main..HEAD
```

Expected: only the approved spec, plan, semantic validator/schema/reference, skill/runbook/docs, and tests are tracked; the worktree is clean. Confirm no audiobook artifact, Echo build, local preference file, inventory, cast, plan, receipt, or subagent report is staged.

- [ ] **Step 4: Request code review**

Use `superpowers:requesting-code-review` against `origin/main...HEAD`. Resolve every Critical or Important finding with a failing test first. Re-run the focused suite after changes and commit coherent fixes.

- [ ] **Step 5: Push and open a ready PR**

```bash
git push -u origin codex/semantic-multivoice-audiobooks
gh pr create --base main --head codex/semantic-multivoice-audiobooks \
  --title "feat(audiobook): add semantic multi-voice narration" \
  --body $'## Summary\n\n- add stable semantic guide, memory, field, and coach roles for nonfiction\n- validate source-bound semantic casts before governed Echo resolution\n- make character-level block casting the standard fiction workflow\n\n## Verification\n\n- `/usr/local/bin/python3 -m unittest discover -s tests -v`\n- `/usr/local/bin/python3 tools/validate_skills.py`\n- `git diff --check origin/main...HEAD`\n\n## Acceptance boundary\n\nNo real audiobook was rendered or human-listened. Echo was not installed or promoted. CI and merge remain pending.'
```

The PR body must summarize stable semantic roles, deterministic cast validation, shared Echo block workflow, and activated fiction wording. List exact verification commands. State explicitly that no real audiobook was rendered or human-listened, Echo was not installed or promoted, and CI/merge remain pending.

- [ ] **Step 6: Report the separate proof states**

Report local tests and validation, review result, branch/PR URL, and worktree cleanliness. Do not claim CI, merge, delivery, publication, narration quality, or human listening unless separately observed.
