# Character-Level Multi-Voice Narration Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the governed Echo narration workflow and fiction skill to generate, seal, resume, audit, and deliver source-bound block voice plans without exposing intermediate clips or a pronunciation reel beside the final audiobook.

**Architecture:** Treat Echo's `resolve-voice-plan` output as the authority for EPUB block/range expansion and resolved identity. Governed shell/Python tooling binds that identity into run storage and receipts; the fiction skill generates an authored plan from explicit speaker assignments plus a separate local preference profile.

**Tech Stack:** Python 3 standard library, POSIX shell/Bash, `unittest`, installed Echo CLI contract, Markdown skill instructions.

## Global Constraints

- Implement only after the Echo branch supplies `echo-cli resolve-voice-plan`, `echo-cli narrate --voice-plan`, capture schema 2, and pronunciation-audit schema 7.
- Preserve existing uniform and repeatable `--chapter-voice` workflows.
- `--voice-plan` and `--chapter-voice` are mutually exclusive.
- The exact final EPUB must exist before a block voice plan is resolved.
- Automatic dialogue detection is outside Echo and outside this first workflow implementation.
- Local blacklists/preferences never enter Git or Echo configuration.
- Changed resolved plans allocate a new run ID, work directory, database, resume receipt, and delivery attempt.
- Chapter captures and pronunciation reels remain internal; fiction delivery contains exactly one M4B.
- Use only Python's standard library and existing repository tools.

## File Map

- Modify `skills/echo-narration/scripts/echo_voice_plan.py`: retain chapter mode and add strict authored-plan/installed-Echo resolution mode.
- Modify `tests/test_echo_voice_plan.py`: canonical resolution and failure tests.
- Modify `skills/echo-narration/scripts/echo_pronunciation_preflight.sh`: accept and seal plan files; derive run identity from Echo's resolved hash.
- Modify `skills/echo-narration/scripts/echo_pronunciation_narrate.sh`: pass plans to Echo, bind state, keep reel internal, and publish a single M4B.
- Modify `skills/echo-narration/scripts/echo_pronunciation_state.py`: schema-4 plan resume/success receipts and capture-schema-2 validation.
- Modify `skills/echo-narration/scripts/validate_pronunciation_audit.py`: validate Echo audit schema 7 and retain schemas 2–6.
- Modify `skills/echo-narration/scripts/echo_installed_renderer.py`: require/attest the resolver and narration capabilities in a new installed package.
- Modify `skills/echo-narration/references/narrating.md`: governed block-plan invocation, storage, resume, audit, and delivery contract.
- Modify `tests/test_echo_narration_runtime.py`: wrapper/state/audit/delivery behavior.
- Modify `tests/test_echo_narration_contract.py`: documented artifact and command contract.
- Modify `tests/test_echo_installed_renderer.py`: capability manifest coverage.
- Create `skills/fiction-book-development/scripts/fiction_voice_plan.py`: explicit assignment compiler and local preference reader.
- Create `tests/test_fiction_voice_plan.py`: casting, blacklist, and output contract.
- Modify `skills/fiction-book-development/SKILL.md`: final-EPUB segmentation and plan-generation gate.
- Modify `skills/fiction-book-development/templates/fiction-project.md`: durable speaker/voice assignment fields.

---

### Task 1: Governed Plan Resolution Adapter

**Files:**
- Modify: `skills/echo-narration/scripts/echo_voice_plan.py`
- Modify: `tests/test_echo_voice_plan.py`

**Interfaces:**
- Consumes: installed `echo-cli resolve-voice-plan --epub PATH --voice-plan PATH` compact JSON.
- Produces: `resolve_block_plan(echo_cli: Path, epub: Path, plan: Path) -> dict[str, object]`
  and CLI `--epub`, `--voice-plan`, `--echo-cli`, and `--canonical-plan`,
  preserving legacy `--default-voice`/`--chapter-voice` mode.

- [ ] **Step 1: Write subprocess and canonical-output tests**

Create a fake executable that emits the approved resolver object. Assert absolute regular-file inputs are required, output keys/types are exact, hash/ID/default voice are validated, and env0 records are:

```python
(
    "VOICE", "am_michael",
    "CHAPTER_VOICES_CANONICAL", "",
    "VOICE_PLAN_SHA256", "123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0",
    "VOICE_PLAN_ID", "plan-123456789abc",
    "VOICE_PLAN_CANONICAL_PATH", str(canonical_plan),
)
```

Also assert the existing chapter-plan API and its 28-voice catalog remain unchanged.

- [ ] **Step 2: Run focused tests and verify RED**

```sh
python3 -m unittest tests.test_echo_voice_plan -v
```

Expected: failure because block-plan CLI options and `resolve_block_plan` do not exist.

- [ ] **Step 3: Implement strict resolver invocation**

Use
`subprocess.run([str(echo_cli), "resolve-voice-plan", "--epub", str(epub), "--voice-plan", str(plan)], check=False, capture_output=True, text=True)`;
never use a shell. Reject nonzero status, stderr on success, duplicate JSON keys,
extra/missing keys, malformed SHA/ID, unknown default voice, mismatched ID prefix,
nonpositive block count, relative/symlink/non-file inputs, and output larger than
64 KiB.

Decode the authored plan with a duplicate-key-rejecting `object_pairs_hook`, then
write it to the caller-provided canonical destination using sorted-key,
two-space-indented JSON plus one terminal newline and atomic `os.replace`.
Re-run Echo's resolver against that canonical copy and require the same resolved
hash/ID before recording it. Do not reproduce EPUB range expansion in Python.

- [ ] **Step 4: Run tests and verify GREEN**

```sh
python3 -m unittest tests.test_echo_voice_plan -v
python3 -m compileall -q skills/echo-narration/scripts/echo_voice_plan.py
```

Expected: all voice-plan tests pass and compileall prints nothing.

- [ ] **Step 5: Commit the resolution adapter**

```sh
git add skills/echo-narration/scripts/echo_voice_plan.py tests/test_echo_voice_plan.py
git commit -m "feat(narration): resolve block voice plans with Echo"
```

### Task 2: Preflight, Run Identity, and Immutable Input Receipt

**Files:**
- Modify: `skills/echo-narration/scripts/echo_pronunciation_preflight.sh`
- Modify: `tests/test_echo_narration_runtime.py`
- Modify: `tests/test_echo_narration_contract.py`

**Interfaces:**
- Consumes: Task 1 env0 fields and Echo's resolved plan identity.
- Produces: wrapper option `--voice-plan ABSOLUTE_PATH`, canonical research copy `$RUN_ROOT/research/echo-voice-plan-$VOICE_PLAN_ID.json`, and input-receipt keys `voice_plan_source`, `voice_plan_canonical_path`, `voice_plan_sha256`, `voice_plan_id`, and `voice_plan_mode=block`.

- [ ] **Step 1: Write preflight contract tests**

Add runtime tests with fake installed Echo/package tooling. Assert plan mode derives:

```text
RUN_ID=<slug>-plan-<12>-<existing-input-digest>
WORK=$RUN_ROOT/audio-work-$RUN_ID
DB=$RUN_ROOT/narration-$RUN_ID.sqlite
ECHO_RENDER_INPUT_RECEIPT=$RUN_ROOT/research/echo-render-inputs-$RUN_ID.env
```

Assert plan/chapter coexistence exits 64, relative/symlinked/missing plans fail, changed resolved plan hash changes every run-scoped path, and invalid resolution creates no work/database/receipt. Assert legacy run IDs remain unchanged.

- [ ] **Step 2: Run focused runtime tests and verify RED**

```sh
python3 -m unittest \
  tests.test_echo_narration_runtime.EchoNarrationRuntimeTests \
  tests.test_echo_narration_contract -v
```

Expected: failure because the wrappers reject `--voice-plan`.

- [ ] **Step 3: Parse and seal plan mode before lease acquisition**

Add one `VOICE_PLAN_SOURCE` variable and reject duplicates. Before `echo_pronunciation_run_id`, call:

```sh
python3 "$SCRIPT_DIR/echo_voice_plan.py" \
  --echo-cli "$ECHO_CLI" \
  --epub "$EPUB" \
  --voice-plan "$VOICE_PLAN_SOURCE" \
  --canonical-plan "$RUN_ROOT/research/echo-voice-plan-pending.json" \
  --format env0
```

After reading the resolver output, atomically rename the pending copy to
`echo-voice-plan-$VOICE_PLAN_ID.json`. Re-attestation repeats Echo resolution and
requires the same hash/ID/default voice and exact canonical-plan bytes. Update
the input receipt with the fields above and retain all existing installed
renderer, source, pronunciation, manifest, and lease identities.

- [ ] **Step 4: Run focused tests and verify GREEN**

```sh
python3 -m unittest tests.test_echo_narration_runtime tests.test_echo_narration_contract -v
shellcheck skills/echo-narration/scripts/echo_pronunciation_preflight.sh
```

Expected: plan and legacy cases pass; shellcheck reports no new issue.

- [ ] **Step 5: Commit immutable preflight support**

```sh
git add skills/echo-narration/scripts/echo_pronunciation_preflight.sh tests/test_echo_narration_runtime.py tests/test_echo_narration_contract.py
git commit -m "feat(narration): bind block plans into run identity"
```

### Task 3: Plan-Aware Capture State and Resume

**Files:**
- Modify: `skills/echo-narration/scripts/echo_pronunciation_state.py`
- Modify: `tests/test_echo_narration_runtime.py`

**Interfaces:**
- Consumes: plan input receipt, Echo capture identity schema 2, `voicePlanSHA256`, and `chapterVoicePlanSHA256`.
- Produces: resume/success receipt schema 4 for block plans while continuing to read/write schema 3 for legacy current runs.

- [ ] **Step 1: Write schema-4 state tests**

Create marker fixtures with identity schema 2. Assert capture-state accepts exact plan hashes and chapter digests, records canonical plan path/hash/ID, and rejects schema 1 in block mode, schema 2 in legacy mode, missing plan fields, changed plan hash, malformed chapter digest, wrong capture set, wrong audio bytes/hash, or marker payload hash.

```python
self.assertEqual(4, state["schemaVersion"])
self.assertEqual("block", state["voicePlanMode"])
self.assertEqual(plan_sha, state["voicePlanSHA256"])
self.assertEqual(canonical_plan, state["voicePlanCanonicalPath"])
```

- [ ] **Step 2: Run state tests and verify RED**

```sh
python3 -m unittest tests.test_echo_narration_runtime -v
```

Expected: schema-2 capture fixtures fail the current identity-schema-1 check.

- [ ] **Step 3: Add mode-dependent capture and receipt validation**

Extend `capture_state_snapshot` and success/delivery snapshot commands with
`--voice-plan PATH`, mutually exclusive with chapter mappings. In block mode,
require marker schema 2, the exact 64-hex full plan hash, and a 64-hex chapter
digest. In legacy mode, retain exact current schema-1 behavior. Emit schema 4
only for block mode and require the canonical plan to remain a regular,
non-symlink file under `$RUN_ROOT/research`.

- [ ] **Step 4: Prove resume compatibility and invalidation**

Add a two-attempt fake-renderer test: first attempt captures one chapter and
returns partial; identical-plan resume reuses it; changed authored JSON that
resolves identically reuses it; changed resolved hash selects a different run
and cannot consume the old receipt. Keep the existing chapter-plan resume test.

- [ ] **Step 5: Run state tests and compile Python**

```sh
python3 -m unittest tests.test_echo_narration_runtime -v
python3 -m compileall -q skills/echo-narration/scripts/echo_pronunciation_state.py
```

Expected: all state and resume cases pass.

- [ ] **Step 6: Commit plan-aware resume state**

```sh
git add skills/echo-narration/scripts/echo_pronunciation_state.py tests/test_echo_narration_runtime.py
git commit -m "feat(narration): seal block plan resume state"
```

### Task 4: Narration, Audit Schema 7, and Single-M4B Delivery

**Files:**
- Modify: `skills/echo-narration/scripts/echo_pronunciation_narrate.sh`
- Modify: `skills/echo-narration/scripts/validate_pronunciation_audit.py`
- Modify: `tests/test_echo_narration_runtime.py`
- Modify: `tests/test_echo_narration_contract.py`

**Interfaces:**
- Consumes: Tasks 1–3 and Echo schema-7 audit.
- Produces: plan-aware Echo invocation, schema-7 audit validation, internal reel location, and a delivery directory containing one M4B.

- [ ] **Step 1: Write invocation, audit, and containment tests**

Assert the fake Echo receives exactly one `--voice-plan <canonical path>` and no `--chapter-voice`; state/success commands receive the same canonical plan. Validate schema 7 with exact `voicePlanSHA256`, complete `blockVoices`, known voices, and decision block coverage. Reject missing/extra mappings, unknown voices, wrong hash, nonempty `chapterVoices`, and decision block omissions while retaining schema 2–6 fixtures.

Assert the published attempt directory contains only:

```python
{
    "fixture.m4b",
    "fixture.alignment.json",
    "fixture.pronunciation-audit.json",
}
```

and that the optional reel remains under `$RUN_ROOT/research/listening/` rather than `dist/echo-renders`.

- [ ] **Step 2: Run narration/audit tests and verify RED**

```sh
python3 -m unittest tests.test_echo_narration_runtime tests.test_echo_narration_contract -v
```

Expected: plan invocation and schema-7 validation fail; current wrapper publishes the reel beside the final M4B.

- [ ] **Step 3: Wire plan arguments through the leased render**

Pass the sealed canonical plan to Echo, capture-state, success-state, and delivery-state commands. Keep `--work-dir "$WORK"` mandatory. Continue staging output atomically, but set:

```sh
REEL="$RUN_ROOT/research/listening/$RUN_ID/$ATTEMPT_ID/$SLUG.pronunciation-reel.m4b"
```

Create that private run-storage directory before rendering; never copy the reel
into `ARTIFACT_ROOT`. The pronunciation audit may name/hash the internal reel,
but delivery verification receives its explicit internal path.

- [ ] **Step 4: Validate audit schema 7**

Accept integer schemas 2 through 7. For schema 7 require exact keys
`voicePlanSHA256` and `blockVoices`, lowercase SHA, known voices, `voice` equal to
the sole mapped voice or `mixed`, empty `chapterVoices`, and every decision block
present. Do not weaken existing audiobook/reel byte-hash, timing-range, watch
count, or coverage validation.

- [ ] **Step 5: Verify one final M4B and no clip leakage**

Before success, recursively inspect the attempt delivery directory. Require one
`.m4b`, reject `.m4a`, `.wav`, `.pcm`, `.anchors-ch*.json`, and any filename
containing `pronunciation-reel`. Retain sidecar verification and exact final
M4B/audit hashes.

- [ ] **Step 6: Run focused tests and shell validation**

```sh
python3 -m unittest tests.test_echo_narration_runtime tests.test_echo_narration_contract -v
python3 -m compileall -q skills/echo-narration/scripts/validate_pronunciation_audit.py
shellcheck skills/echo-narration/scripts/echo_pronunciation_narrate.sh
```

Expected: block-plan and historical audit cases pass; no reel is published with the book.

- [ ] **Step 7: Commit governed rendering and delivery**

```sh
git add skills/echo-narration/scripts/echo_pronunciation_narrate.sh skills/echo-narration/scripts/validate_pronunciation_audit.py tests/test_echo_narration_runtime.py tests/test_echo_narration_contract.py
git commit -m "feat(narration): govern mixed-voice delivery"
```

### Task 5: Installed Renderer Capability and Documentation

**Files:**
- Modify: `skills/echo-narration/scripts/echo_installed_renderer.py`
- Modify: `skills/echo-narration/references/echo-renderer-v1/canonical-manifest-v1.json`
- Modify: `skills/echo-narration/references/echo-renderer-v1/resource-tree-v1.json`
- Modify: `skills/echo-narration/references/echo-renderer-v1/lease-identities-v1.json`
- Modify: `skills/echo-narration/references/narrating.md`
- Modify: `tests/test_echo_installed_renderer.py`
- Modify: `tests/test_echo_narration_contract.py`

**Interfaces:**
- Consumes: released/installed Echo binary from the Echo plan.
- Produces: attested `--voice-plan` and `resolve-voice-plan` capabilities and operator instructions.

- [ ] **Step 1: Write installed-capability tests**

Extend fake help output and manifest assertions so a package is accepted only
when `narrate --help` advertises `--voice-plan` and top-level help advertises
`resolve-voice-plan`. Assert old manifests remain historical evidence but cannot
be selected for block-plan runs.

- [ ] **Step 2: Run installed renderer tests and verify RED**

```sh
python3 -m unittest tests.test_echo_installed_renderer -v
```

Expected: the new capability assertions fail against the current manifest schema.

- [ ] **Step 3: Add explicit capability attestation**

Bump the installed renderer manifest schema only if required by its strict-key
validator; add capabilities `narrate.block_voice_plan.v1`,
`resolve_voice_plan.v1`, `capture.block_voice_plan.v2`, and
`pronunciation_audit.v7`. Regenerate canonical manifest/resource-tree/lease
identity values with the repository's existing installed-renderer command after
the new Echo binary is installed. Never hand-edit a digest.

- [ ] **Step 4: Document the operator contract**

In `narrating.md`, include the exact plan JSON, resolver command, narration
command, plan/chapter exclusivity, source freeze, run identity, schema-2 resume,
schema-7 audit, internal reel location, and one-M4B containment check. State
that semantic speaker markup is compiled upstream and Echo never infers prose.

- [ ] **Step 5: Run capability and documentation validation**

```sh
python3 -m unittest tests.test_echo_installed_renderer tests.test_echo_narration_contract -v
python3 tools/validate_skills.py
git diff --check
```

Expected: all tests and skill validation pass; diff check is empty.

- [ ] **Step 6: Commit renderer capability and docs**

```sh
git add skills/echo-narration/references skills/echo-narration/scripts/echo_installed_renderer.py tests/test_echo_installed_renderer.py tests/test_echo_narration_contract.py
git commit -m "docs(narration): attest block voice plan capability"
```

### Task 6: Fiction Segmentation, Casting Preferences, and Plan Generation

**Files:**
- Create: `skills/fiction-book-development/scripts/fiction_voice_plan.py`
- Create: `tests/test_fiction_voice_plan.py`
- Modify: `skills/fiction-book-development/SKILL.md`
- Modify: `skills/fiction-book-development/templates/fiction-project.md`

**Interfaces:**
- Consumes: an explicit JSON assignment input, final EPUB path, Echo voice catalog, and optional local preferences at `~/Library/Application Support/Explainer Audiobooks/fiction-voice-preferences.json`.
- Produces: an authored Echo schema-1 voice-plan JSON and
  `validate_delivery_set(directory: Path, slug: str) -> None`; it does not
  resolve ranges or synthesize audio.

- [ ] **Step 1: Write preference and plan-generation tests**

Define assignment input as:

```json
{
  "schemaVersion": 1,
  "defaultSpeakerID": "narrator",
  "speakers": [
    { "id": "narrator", "voiceID": "am_michael" },
    { "id": "mara", "voiceID": "bf_emma" }
  ],
  "assignments": [
    { "speakerID": "mara", "blocks": ["s2-b3"] }
  ]
}
```

Assert generation adds the exact EPUB SHA, writes sorted-key pretty JSON,
rejects blacklisted assigned voices, chooses the first available preferred
narrator only when the narrator voice is omitted, rejects unknown speakers,
voices, IDs, and duplicate assignments, and never reads a repo-local fallback
preference file. Assert `validate_delivery_set` accepts exactly
`<slug>.epub`, `<slug>.m4b`, `<slug>.alignment.json`, and one
`<slug>.cover.png|jpg|jpeg`; it rejects a second M4B, reel, M4A, WAV, PCM,
marker, audit, plan, receipt, missing role, or unrelated fifth file.

- [ ] **Step 2: Run fiction plan tests and verify RED**

```sh
python3 -m unittest tests.test_fiction_voice_plan -v
```

Expected: import failure because `fiction_voice_plan.py` does not exist.

- [ ] **Step 3: Implement the explicit compiler**

Expose:

Expose `load_preferences(path: Path | None) -> dict[str, object]`,
`build_voice_plan(epub: Path, assignment: dict[str, object], preferences: dict[str, object]) -> dict[str, object]`,
and `write_voice_plan(plan: dict[str, object], output: Path) -> None`.

CLI options are required `--epub`, `--assignments`, `--out`, optional
`--preferences`, and optional `--no-preferences`. Default preferences use the
approved Application Support path. Use `os.open`/`os.replace` for atomic output;
reject symlink EPUB/assignment/output parent and never mutate the EPUB. Add CLI
subcommand `verify-delivery --directory ABSOLUTE_PATH --slug SLUG` backed by the
same `validate_delivery_set` function used by tests.

- [ ] **Step 4: Add the fiction production gate**

Document that the accepted manuscript is transformed so each uninterrupted
narrator/POV/dialogue run is one block-level XHTML element before final EPUB
freeze. Dialogue plus attribution follows an explicit project decision; inline
`data-speaker` spans are not sufficient. The plan is generated after final EPUB,
then `echo-cli resolve-voice-plan` must succeed before narration.

Add template fields:

```markdown
- Dialogue attribution rule: character block | split narrator block
- Default narrator speaker ID:
- Explicit speaker-to-voice assignments:
- Local voice preference profile used: yes | no
- Final EPUB SHA-256:
- Resolved Echo voice plan ID:
```

Require the fiction delivery step to copy only the four approved files into a
new empty directory and run `fiction_voice_plan.py verify-delivery` before
reporting an Echo-ready set. Pronunciation audit, plan, receipts, and reel remain
under governed run research/storage and are not copied to that directory.

- [ ] **Step 5: Run fiction and skill validation**

```sh
python3 -m unittest tests.test_fiction_voice_plan -v
python3 tools/validate_skills.py
git diff --check
```

Expected: tests pass, skill validation passes, and diff check prints nothing.

- [ ] **Step 6: Commit fiction plan generation**

```sh
git add skills/fiction-book-development tests/test_fiction_voice_plan.py
git commit -m "feat(fiction): generate explicit Echo voice plans"
```

### Task 7: Full Workflow Verification and Review Handoff

**Files:**
- Modify only files already changed if verification exposes a defect.

**Interfaces:**
- Consumes: all prior tasks and the implemented Echo contract.
- Produces: a clean branch ready for GPT-5.6-sol review.

- [ ] **Step 1: Run all repository verification**

```sh
python3 -m unittest discover -s tests -v
python3 tools/validate_skills.py
python3 tools/validate_custom_learning_skill_install.py
git diff --check
```

Expected: all tests and validators pass with no diff whitespace errors.

- [ ] **Step 2: Run a public-safe synthetic contract fixture**

Generate a two-chapter EPUB fixture with narrator, POV, and dialogue blocks;
compile its authored plan; resolve it with installed Echo; execute one partial
render and one resume; verify schema-2 captures and schema-7 audit; verify the
delivery attempt contains exactly one M4B and no M4A/WAV/PCM/reel. Store the
fixture only under the test temporary directory and delete it through test
cleanup.

- [ ] **Step 3: Inspect branch cleanliness and commits**

```sh
git status --short --branch
git log --oneline origin/main..HEAD
```

Expected: no uncommitted files and coherent task commits only.

- [ ] **Step 4: Stop before publication**

Do not push or open a PR. Hand both repository commits and verification output
to a GPT-5.6-sol reviewer for spec compliance, implementation quality, security,
resume identity, audit integrity, artifact containment, and legacy compatibility.
