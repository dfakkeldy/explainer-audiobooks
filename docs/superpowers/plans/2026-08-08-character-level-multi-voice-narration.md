# Character-Level Multi-Voice Narration Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the existing `fiction-audiobook` production lane from chapter-only ensembles to explicit source-bound character/block casting while preserving every uniform and chapter-voice workflow, immutable Echo resume evidence, Echo-clean delivery, and public/private publication gate.

**Architecture:** Keep the existing fiction cast, local preference store, `_production` evidence tree, atomic delivery stager, and public verifier. Add schema 2 to `voice-cast.json`, store the exact Echo schema-1 authored plan beside it, and let the approved installed Echo `resolve-voice-plan` command be the only authority that checks block IDs, expands ranges, and computes the resolved plan identity. The governed narration wrapper seals that identity into its existing content-addressed run and receipt chain; it never detects dialogue or infers a speaker.

**Tech Stack:** Python 3.11 (`/usr/local/bin/python3`), Bash, `unittest`, installed Echo/Kokoro CLI, JSON, and Markdown skill instructions.

## Global Constraints

- The Explainer Audiobooks baseline is `origin/main` commit `26db4b6`; locate the active linked worktree with `git rev-parse --show-toplevel` rather than using a stale worktree path.
- The reviewed Echo renderer-source contract is commit `aeeb5bf056c6476d7169e55ed0f38a90bec11639`, render version 22. Its `resolve-voice-plan` stdout, capture identity schema 2, and pronunciation-audit schema 7 are authoritative.
- Keep Echo renderer source approval and Echo installer approval separate. The installed package records both `echoSourceSHA` and `installerSourceSHA`; extending installer manifest probing must not change or reinterpret the approved renderer-source contract.
- Do not build, install, repair, promote, or mutate an installed Echo selector while implementing this plan. Produce and test installer/consumer metadata support only; installation remains a later operator action.
- Preserve the existing uniform `VOICE=<voice>` flow, repeatable `--chapter-voice N=voice_id` flow, legacy input-receipt bytes, capture schema 1, resume schema 3, success schema 3, audit schemas 2–6, and public receipt schema 2.
- `--voice-plan` and `--chapter-voice` are mutually exclusive. In block mode the wrapper never passes `--voice`; Echo obtains the default from the authored plan.
- Freeze the exact final EPUB before exporting its block inventory or writing a plan. An EPUB-byte change invalidates the authored source hash and requires a new plan.
- Speaker segmentation and assignments are authored explicitly. Echo does not inspect prose for quotation marks, attribution, POV, names, or likely speakers.
- Echo alone validates whether a block is present/speakable, expands `range`, applies the declared default speaker, and computes `voicePlanSHA256`, `voicePlanID`, `blockCount`, and chapter plan digests. Python must not reproduce those algorithms.
- Preferences and blacklists stay only at `~/Library/Application Support/Explainer Audiobooks/fiction-voice-preferences.json`; no repository-local fallback is allowed.
- A changed resolved plan selects a new run ID, work directory, database, resume receipt, attempt chain, and delivery attempt. An authored document that resolves to the already sealed identity reuses the existing canonical plan and run.
- Chapter captures stay under `audio-work-$RUN_ID`. A pronunciation reel stays under `research/listening/$RUN_ID/$ATTEMPT_ID/`; neither may appear in `dist/echo-renders` or the iCloud title root.
- The iCloud title root remains exactly one `<slug>.m4b`, one `<slug>.epub`, one `<slug>.alignment.json`, one `cover.png`, and `_production/`. `_production/` retains exactly `source/`, `checks/`, `narration/`, `covers/`, `publication/`, and `previous/`. The public Git package remains the exact six-file set `README.md`, `publication.json`, `<slug>.md`, `<slug>.epub`, `<slug>.alignment.json`, and `cover.png`; the release has one exact verified M4B asset.
- Keep private source, plan drafts, block inventories, captures, reels, receipts, and audits out of public Git artifacts. Public-safe content remains separately gated and publication is not authorized by this implementation plan.
- Use only the Python standard library and existing dependencies. Do not add a third-party dependency.
- Every production or skill-instruction change follows RED–GREEN: write and run the focused failing test first. Skill edits additionally require a failing fresh-agent pressure scenario before editing `SKILL.md` or either routed reference.
- Do not push, open a PR, merge, install a skill, or publish a renderer/book. The final gate is a GPT-5.6-sol review of local commits and fresh verification evidence.

## File Map

### Echo installer metadata prerequisite

- Modify in a dedicated installer worktree based on the currently accepted installer source: `Scripts/echo_renderer/store.py`.
- Modify in that worktree: `Scripts/echo_renderer/tests/test_store_install.py`, `Scripts/echo_renderer/tests/test_store_verify.py`, and `Scripts/echo_renderer/test_vectors/canonical-manifest-v1.json`.
- Do not modify the clean renderer-source worktree at `aeeb5bf056c6476d7169e55ed0f38a90bec11639`.

### Explainer Audiobooks

- Modify `skills/echo-narration/scripts/echo_installed_renderer.py`: attest narrate flags and top-level subcommands through their correct help surfaces.
- Modify `skills/echo-narration/references/echo-renderer-v1/canonical-manifest-v1.json` and `vector-provenance.json`: copy reviewed installer vectors and their exact hashes; never hand-edit canonical bytes or digests.
- Modify `tests/test_echo_installed_renderer.py`: manifest-generation/consumer parity.
- Modify `skills/echo-narration/scripts/echo_voice_plan.py`: preserve chapter planning and add a strict installed-Echo block-plan adapter.
- Modify `skills/echo-narration/scripts/echo_pronunciation_preflight.sh`: select mode, seal canonical/resolution files, and derive block-plan run identity.
- Modify `skills/echo-narration/scripts/echo_pronunciation_narrate.sh`: accept `--voice-plan`, keep the reel internal, and pass plan evidence through state/success commands.
- Modify `skills/echo-narration/scripts/echo_pronunciation_state.py`: capture schema 2, resume schema 4, success schema 4, and block-plan delivery verification.
- Modify `skills/echo-narration/scripts/validate_pronunciation_audit.py`: schema-7 block provenance with explicit media paths.
- Modify `skills/echo-narration/references/narrating.md`: installed inventory, resolution, invocation, resume, audit, and containment runbook.
- Modify `tests/test_echo_voice_plan.py`, `tests/test_echo_narration_runtime.py`, and `tests/test_echo_narration_contract.py`: governed block-plan coverage and legacy compatibility.
- Modify `skills/fiction-audiobook/scripts/fiction_voice_preferences.py`: add cast schema 2 and block-use history without adding a parallel compiler.
- Modify `tests/test_fiction_voice_preferences.py`: cast, blacklist, CLI, receipt, and compatibility tests.
- Modify `skills/fiction-audiobook/SKILL.md` and `references/express-fiction-craft.md`: final-source segmentation and character-cast workflow.
- Modify `skills/fiction-audiobook/references/public-fiction-gate.md`: current private narration evidence and exact root containment.
- Modify `skill/scripts/verify_public_first_listen.py`: accept completed cast schema 2 and Echo success schema 4 while retaining chapter cast schema 1.
- Modify `tests/test_verify_public_first_listen.py`, `tests/test_fiction_audiobook_integration.py`, and `tests/test_stage_echo_delivery.py`: private/public proof and exact delivered set.

---

### Task 1: Reconcile Installed-Renderer Manifest Generation and Attestation

The approved Echo source already exposes the required rendering behavior, but the separate installer manifest generator currently records only chapter-era flags. Fix that metadata seam before the Explainer wrapper relies on it. This task does not build or install Echo.

**Files:**

- Modify in the Echo installer worktree: `Scripts/echo_renderer/store.py`
- Modify in the Echo installer worktree: `Scripts/echo_renderer/tests/test_store_install.py`
- Modify in the Echo installer worktree: `Scripts/echo_renderer/tests/test_store_verify.py`
- Modify in the Echo installer worktree: `Scripts/echo_renderer/test_vectors/canonical-manifest-v1.json`
- Modify: `skills/echo-narration/scripts/echo_installed_renderer.py`
- Modify: `skills/echo-narration/references/echo-renderer-v1/canonical-manifest-v1.json`
- Modify: `skills/echo-narration/references/echo-renderer-v1/vector-provenance.json`
- Modify: `tests/test_echo_installed_renderer.py`

**Interfaces:**

- Consumes: renderer-source SHA `aeeb5bf056c6476d7169e55ed0f38a90bec11639` and a separately reviewed installer commit.
- Produces this exact manifest `capabilities` sequence:

```json
[
  "--cover",
  "--sidecar",
  "--voice",
  "--voice-plan",
  "--chapter-voice",
  "--db",
  "--work-dir",
  "--jobs",
  "--threads",
  "--resume",
  "--max-chapters",
  "--no-pronunciation-review",
  "export-blocks",
  "resolve-voice-plan",
  "verify-sidecar"
]
```

- `--voice-plan` is proven by `echo-cli narrate --help`; each unprefixed capability is proven by `echo-cli <capability> --help`.

- [ ] **Step 1: RED — add installer generator tests**

In the Echo installer tests, make the fake runner return distinct output for top-level subcommands and assert `probe_release_cli` fails when any one of `--voice-plan`, `export-blocks`, or `resolve-voice-plan` is absent. Assert a successful probe writes the exact capability sequence above into the generated schema-1 manifest.

```python
self.assertEqual(REQUIRED_CAPABILITIES, tuple(verified.manifest.capabilities))
self.assertIn([str(executable), "resolve-voice-plan", "--help"], calls)
self.assertIn([str(executable), "export-blocks", "--help"], calls)
```

- [ ] **Step 2: Run the installer tests and verify RED**

```bash
PYTHONPATH=Scripts python3 -m unittest \
  echo_renderer.tests.test_store_install \
  echo_renderer.tests.test_store_verify -v
```

Expected: failures because the generator neither requires nor probes the three plan-era capabilities.

- [ ] **Step 3: Implement separate flag/subcommand probing**

Keep `_REQUIRED_NARRATE_CAPABILITIES` for flags and add:

```python
_REQUIRED_SUBCOMMAND_CAPABILITIES = (
    "export-blocks",
    "resolve-voice-plan",
    "verify-sidecar",
)
_REQUIRED_CAPABILITIES = (
    *_REQUIRED_NARRATE_CAPABILITIES,
    *_REQUIRED_SUBCOMMAND_CAPABILITIES,
)
```

Add `--voice-plan` immediately after `--voice`. Probe every required subcommand with `[executable, capability, "--help"]`, require the command name as a token in stdout, and append it to `RendererProbe.capabilities` only after the probe succeeds. Keep manifest schema 1 and canonical JSON framing unchanged.

- [ ] **Step 4: Regenerate and verify the Echo test vector without building**

Update only `payload.capabilities` in the vector with `apply_patch`. Use the repository's real canonicalizer to print the exact escaped UTF-8 and digest:

```bash
PYTHONPATH=Scripts python3 - <<'PY'
import hashlib
import json
from pathlib import Path
from echo_renderer.identity import canonical_json_bytes

path = Path("Scripts/echo_renderer/test_vectors/canonical-manifest-v1.json")
document = json.loads(path.read_text(encoding="utf-8"))
canonical = canonical_json_bytes(document["payload"])
print(json.dumps(canonical.decode("utf-8")))
print(hashlib.sha256(canonical).hexdigest())
PY
```

Apply those two printed values to `canonicalUTF8` and `sha256`; do not calculate or type an alternative encoding. Then run:

```bash
PYTHONPATH=Scripts python3 -m unittest \
  echo_renderer.tests.test_identity \
  echo_renderer.tests.test_store_install \
  echo_renderer.tests.test_store_verify -v
```

Expected: the canonical vector and both installer surfaces agree without invoking a build.

- [ ] **Step 5: RED — add Explainer consumer parity tests**

Update `REQUIRED_CAPABILITIES` in `tests/test_echo_installed_renderer.py`. Make `successful_probe` distinguish all four help calls, and assert attestation fails if the manifest advertises a plan-era capability that its correct help surface does not expose.

```python
self.assertEqual(
    [
        [str(state.executable), "--version"],
        [str(state.executable), "narrate", "--help"],
        [str(state.executable), "export-blocks", "--help"],
        [str(state.executable), "resolve-voice-plan", "--help"],
        [str(state.executable), "verify-sidecar", "--help"],
    ],
    [arguments for arguments, _kwargs in calls],
)
```

- [ ] **Step 6: Run the consumer test and verify RED**

```bash
/usr/local/bin/python3 -m unittest tests.test_echo_installed_renderer -v
```

Expected: capability and probe-count failures against the current consumer.

- [ ] **Step 7: Implement consumer attestation and reviewed vector import**

Teach `attest_renderer` to probe manifest strings beginning with `--` only in `narrate --help`, and the exact three accepted subcommands on their own help surfaces. Reject any other unprefixed capability. Copy the generated Echo vector bytes into the Explainer reference, update `vector-provenance.json` with the exact installer commit and file SHA, and add that exact installer commit to `ACCEPTED_INSTALLER_SOURCE_SHAS`. Do not replace or remove historical accepted installer SHAs.

- [ ] **Step 8: Verify and commit both local changesets**

```bash
PYTHONPATH=Scripts python3 -m unittest \
  echo_renderer.tests.test_store_install \
  echo_renderer.tests.test_store_verify -v
/usr/local/bin/python3 -m unittest tests.test_echo_installed_renderer -v
git diff --check
```

Commit the installer worktree first with `fix(renderer): attest block voice plan capabilities`. Record its full SHA, then commit the Explainer changes with `feat(narration): accept block-plan renderer manifests`. Do not build, install, promote, push, or open a PR.

### Task 2: Add the Echo-Authoritative Plan Adapter and Immutable Preflight

**Files:**

- Modify: `skills/echo-narration/scripts/echo_voice_plan.py`
- Modify: `skills/echo-narration/scripts/echo_pronunciation_preflight.sh`
- Modify: `skills/echo-narration/scripts/echo_pronunciation_narrate.sh`
- Modify: `tests/test_echo_voice_plan.py`
- Modify: `tests/test_echo_narration_runtime.py`
- Modify: `tests/test_echo_narration_contract.py`

**Authored plan contract:**

The fiction workflow writes this exact Echo schema; assignments use exactly one of `blocks` or `range`. The sample is complete and valid, not a schema extension:

```json
{
  "schemaVersion": 1,
  "source": {
    "epubSHA256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  },
  "defaultSpeakerID": "narrator",
  "speakers": [
    {"id": "narrator", "voiceID": "am_michael"},
    {"id": "mara", "voiceID": "bf_emma"},
    {"id": "ivo", "voiceID": "bm_george"}
  ],
  "assignments": [
    {"speakerID": "mara", "blocks": ["s2-b3", "s2-b5"]},
    {"speakerID": "ivo", "range": {"start": "s3-b1", "end": "s3-b4"}}
  ]
}
```

**Resolver receipt contract:**

Persist Echo's compact sorted stdout unchanged except for the terminal newline. It has exactly:

```json
{"blockCount":2,"defaultVoice":"am_michael","sourceEPUBSHA256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","voicePlanID":"plan-bbbbbbbbbbbb","voicePlanSHA256":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"}
```

**Interfaces:**

- Preserve existing `voice_plan(default_voice, values)` and legacy CLI output byte-for-byte.
- Add `resolve_block_plan(echo_cli: Path, epub: Path, plan: Path) -> dict[str, object]`.
- Add block CLI mode:

```text
echo_voice_plan.py --echo-cli ABSOLUTE_PATH --epub ABSOLUTE_PATH \
  --voice-plan ABSOLUTE_PATH --canonical-plan ABSOLUTE_PATH \
  --resolution ABSOLUTE_PATH --format env0
```

- Add wrapper option `--voice-plan ABSOLUTE_PATH`; keep all existing options.

- [ ] **Step 1: RED — write adapter tests against a fake Echo executable**

Test the exact resolver argv, compact JSON keys/types, source SHA, default voice, positive block count, `plan-<12>` prefix, stdout size limit, empty stderr on success, and nonzero exit handling. Reject relative, missing, directory, symlink, and noncanonical installed CLI paths. Reject duplicate authored JSON keys before writing a canonical copy.

Assert block env0 contains each key exactly once in this order:

```python
(
    "VOICE", "am_michael",
    "CHAPTER_VOICES_CANONICAL", "",
    "VOICE_PLAN_MODE", "block",
    "VOICE_PLAN_SHA256", "b" * 64,
    "VOICE_PLAN_ID", "plan-" + "b" * 12,
    "VOICE_PLAN_BLOCK_COUNT", "2",
    "VOICE_PLAN_CANONICAL_PATH", str(canonical_plan),
    "VOICE_PLAN_CANONICAL_SHA256", canonical_sha,
    "VOICE_PLAN_RESOLUTION_PATH", str(resolution),
    "VOICE_PLAN_RESOLUTION_SHA256", resolution_sha,
)
```

Also assert the existing four-record legacy env0 result and all 28 voice IDs are unchanged.

- [ ] **Step 2: Run adapter tests and verify RED**

```bash
/usr/local/bin/python3 -m unittest tests.test_echo_voice_plan -v
```

Expected: block-mode arguments and `resolve_block_plan` do not exist.

- [ ] **Step 3: Implement the minimal adapter**

Invoke only:

```python
subprocess.run(
    [str(echo_cli), "resolve-voice-plan", "--epub", str(epub),
     "--voice-plan", str(plan)],
    check=False, capture_output=True, text=False, env=safe_environment,
)
```

Require stdout at most 64 KiB. Decode strict UTF-8 with a duplicate-key-rejecting hook and exact keys. Python may validate the five scalar result fields, but it must not parse EPUB blocks, expand ranges, or calculate a resolved plan hash.

Canonicalize the authored JSON with sorted keys, two-space indentation, and one newline. If the canonical destination exists, never overwrite it: resolve the existing file and reuse it only when Echo returns the same five-field receipt. Otherwise create it with `echo_pronunciation_state.py immutable-file`. Resolve that sealed copy again and require the exact same receipt, then immutably write Echo's compact receipt bytes to `--resolution`.

- [ ] **Step 4: RED — write wrapper/preflight tests**

Add fake-renderer cases that assert:

- `--voice-plan` plus any `--chapter-voice` exits 64 before work/DB/receipt creation;
- a relative, missing, directory, or symlink plan exits 64/66 without mutation;
- block mode invokes `resolve-voice-plan` only while the installed build-root lease is held;
- Echo receives the sealed canonical research copy, never the mutable caller path;
- a changed resolved hash changes `RUN_ID`, `WORK`, `DB`, input receipt, state receipt, and artifact root;
- a syntactically different authored plan with the same Echo receipt reuses the already sealed canonical plan and run;
- legacy run IDs and legacy input-receipt bytes are unchanged.

- [ ] **Step 5: Run wrapper tests and verify RED**

```bash
/usr/local/bin/python3 -m unittest \
  tests.test_echo_narration_runtime.EchoPronunciationPreflightTests \
  tests.test_echo_narration_contract -v
```

Expected: the wrapper rejects `--voice-plan` and has no block receipt fields.

- [ ] **Step 6: Parse, resolve, and seal block mode before allocating run state**

Thread `VOICE_PLAN_SOURCE` through the wrapper's two lease execs. Reject duplicates and chapter coexistence in the outer parse. During preflight, run the adapter with temporary same-directory destinations, then promote or reuse:

```text
$RUN_ROOT/research/echo-voice-plan-$VOICE_PLAN_ID.json
$RUN_ROOT/research/echo-voice-plan-resolution-$VOICE_PLAN_ID.json
```

Set `VOICE` from Echo's `defaultVoice`. If the caller supplied a nonempty `VOICE`, require it to equal that value, but never forward `--voice` to Echo in block mode. Set `CHAPTER_VOICES_CANONICAL` to the empty string.

Use the existing exact run-ID framing, `<epubSHA256[0:12]>-<echoCLI_SHA256[0:12]>-<echoResourcesSHA256[0:12]>-<rendererManifestSHA256[0:12]>-<echoSourceSHA>-<voicePlanID>`, with the resolved `VOICE_PLAN_ID`. Do not include raw caller-path or draft-plan bytes in the run ID.

- [ ] **Step 7: Bind the exact block input receipt while preserving legacy bytes**

Legacy mode continues to emit its current lines only. Block mode emits these ordered lines:

```text
renderer_schema_version=1
renderer_root=$ECHO_RENDERER_ROOT
renderer_build_root=$ECHO_RENDERER_BUILD_ROOT
installer_source_sha=$APPROVED_ECHO_INSTALLER_SHA
approved_echo_pronunciation_sha=$APPROVED_ECHO_PRONUNCIATION_SHA
echo_source_sha=$ECHO_SOURCE_SHA
renderer_manifest_sha256=$ECHO_RENDERER_MANIFEST_SHA256
echo_cli_sha256=$ECHO_CLI_SHA256
echo_cli_path=$CLI
echo_resources_sha256=$ECHO_RESOURCES_SHA256
echo_resource_dir=$ECHO_RESOURCE_DIR
render_version=$ECHO_RENDER_VERSION
model_policy_revision=$ECHO_MODEL_REVISION
model_expected_byte_count=$ECHO_MODEL_EXPECTED_BYTES
model_bytes_attested=false
voice=$VOICE
chapter_voices=
voice_plan_sha256=$VOICE_PLAN_SHA256
voice_plan_id=$VOICE_PLAN_ID
voice_plan_mode=block
voice_plan_block_count=$VOICE_PLAN_BLOCK_COUNT
voice_plan_canonical_path=$VOICE_PLAN_CANONICAL_PATH
voice_plan_canonical_sha256=$VOICE_PLAN_CANONICAL_SHA256
voice_plan_resolution_path=$VOICE_PLAN_RESOLUTION_PATH
voice_plan_resolution_sha256=$VOICE_PLAN_RESOLUTION_SHA256
epub_sha256=$EPUB_SHA256
cover_binding_mode=$COVER_BINDING_MODE
cover_selection_path=$COVER_SELECTION
cover_selection_sha256=$COVER_SELECTION_SHA256
portrait_cover_path=$COVER
portrait_cover_sha256=$COVER_SHA256
m4b_cover_path=$M4B_COVER
m4b_cover_sha256=$M4B_COVER_SHA256
run_lane=$ECHO_RUN_LANE
run_root=$RUN_ROOT
package_sha256=$PACKAGE_SHA256
run_id=$RUN_ID
work_dir=$WORK
narration_db=$DB
```

Re-attestation re-resolves the sealed canonical plan and requires the same receipt bytes, hashes, source EPUB hash, run ID, and paths before and after narration.

- [ ] **Step 8: Verify and commit**

```bash
/usr/local/bin/python3 -m unittest \
  tests.test_echo_voice_plan tests.test_echo_narration_runtime \
  tests.test_echo_narration_contract -v
/usr/local/bin/python3 -m compileall -q \
  skills/echo-narration/scripts/echo_voice_plan.py
git diff --check
```

Commit with `feat(narration): seal Echo block voice plans`.

### Task 3: Bind Schema-2 Captures, Schema-7 Audit, and Internal Review Media

**Files:**

- Modify: `skills/echo-narration/scripts/echo_pronunciation_state.py`
- Modify: `skills/echo-narration/scripts/validate_pronunciation_audit.py`
- Modify: `skills/echo-narration/scripts/echo_pronunciation_narrate.sh`
- Modify: `tests/test_echo_narration_runtime.py`
- Modify: `tests/test_echo_narration_contract.py`

**Resume schema 4:**

Block runs write exact resume schema 4; renderer identity fields retain their current names and values:

```json
{
  "schemaVersion": 4,
  "rendererSchemaVersion": 1,
  "rendererRoot": "/absolute/renderer-root",
  "rendererBuildRoot": "/absolute/renderer-build",
  "installerSourceSHA": "1111111111111111111111111111111111111111",
  "echoSourceSHA": "2222222222222222222222222222222222222222",
  "rendererManifestSHA256": "3333333333333333333333333333333333333333333333333333333333333333",
  "echoCLI_SHA256": "4444444444444444444444444444444444444444444444444444444444444444",
  "echoResourcesSHA256": "5555555555555555555555555555555555555555555555555555555555555555",
  "echoRenderVersion": 22,
  "modelPolicyRevision": "kokoro-v1.0",
  "modelExpectedByteCount": 325566778,
  "modelBytesAttested": false,
  "sourceFingerprint": "6666666666666666666666666666666666666666666666666666666666666666",
  "voice": "am_michael",
  "voicePlanMode": "block",
  "voicePlanID": "plan-bbbbbbbbbbbb",
  "voicePlanSHA256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "voicePlanBlockCount": 2,
  "voicePlanCanonicalFileName": "echo-voice-plan-plan-bbbbbbbbbbbb.json",
  "voicePlanCanonicalSHA256": "7777777777777777777777777777777777777777777777777777777777777777",
  "voicePlanResolutionFileName": "echo-voice-plan-resolution-plan-bbbbbbbbbbbb.json",
  "voicePlanResolutionSHA256": "8888888888888888888888888888888888888888888888888888888888888888",
  "renderVersion": 22,
  "captureSetID": "9999999999999999999999999999999999999999999999999999999999999999",
  "inputReceiptSHA256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "databaseSHA256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
  "databaseByteCount": 1234,
  "captures": [
    {
      "chapterIndex": 0,
      "markerFileName": "chapter-0000.complete.json",
      "markerSHA256": "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
      "audioFileName": "chapter-0000.m4a",
      "audioSHA256": "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
      "payloadSHA256": "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
    }
  ]
}
```

Each capture entry retains the existing six receipt fields. The underlying Echo marker must have identity schema 2 and exact `voicePlanSHA256` plus a valid `chapterVoicePlanSHA256`.

**Success schema 4:**

Block runs use this exact schema-4 key set. `RUN_ID` and `ATTEMPT_ID` below stand for the already validated current identifiers; no literal placeholder is persisted:

```json
{
  "schemaVersion": 4,
  "rendererSchemaVersion": 1,
  "rendererRoot": "/absolute/renderer-root",
  "rendererBuildRoot": "/absolute/renderer-build",
  "installerSourceSHA": "1111111111111111111111111111111111111111",
  "echoSourceSHA": "2222222222222222222222222222222222222222",
  "rendererManifestSHA256": "3333333333333333333333333333333333333333333333333333333333333333",
  "echoCLI_SHA256": "4444444444444444444444444444444444444444444444444444444444444444",
  "echoResourcesSHA256": "5555555555555555555555555555555555555555555555555555555555555555",
  "echoRenderVersion": 22,
  "modelPolicyRevision": "kokoro-v1.0",
  "modelExpectedByteCount": 325566778,
  "modelBytesAttested": false,
  "attemptID": "9999999999999999999999999999999999999999999999999999999999999999",
  "runID": "RUN_ID",
  "attemptReceiptSHA256": "0000000000000000000000000000000000000000000000000000000000000000",
  "inputReceiptFileName": "echo-render-inputs-RUN_ID.env",
  "inputReceiptSHA256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "sourceEPUBFileName": "storm-lighthouse.epub",
  "sourceEPUBSHA256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "artifactRelativePath": "echo-renders/RUN_ID/ATTEMPT_ID",
  "resumeStateFileName": "echo-resume-state-RUN_ID.json",
  "resumeStateSHA256": "6666666666666666666666666666666666666666666666666666666666666666",
  "audiobookFileName": "storm-lighthouse.m4b",
  "audiobookSHA256": "7777777777777777777777777777777777777777777777777777777777777777",
  "sidecarFileName": "storm-lighthouse.alignment.json",
  "sidecarSHA256": "8888888888888888888888888888888888888888888888888888888888888888",
  "auditFileName": "storm-lighthouse.pronunciation-audit.json",
  "auditSHA256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
  "voicePlanMode": "block",
  "voicePlanID": "plan-bbbbbbbbbbbb",
  "voicePlanSHA256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "voicePlanBlockCount": 2,
  "voicePlanCanonicalFileName": "echo-voice-plan-plan-bbbbbbbbbbbb.json",
  "voicePlanCanonicalSHA256": "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
  "voicePlanResolutionFileName": "echo-voice-plan-resolution-plan-bbbbbbbbbbbb.json",
  "voicePlanResolutionSHA256": "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
  "reelFileName": "storm-lighthouse.pronunciation-reel.m4b",
  "reelRelativePath": "listening/RUN_ID/ATTEMPT_ID/storm-lighthouse.pronunciation-reel.m4b",
  "reelSHA256": "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
}
```

The three `reel*` keys are either all present or all absent. Legacy success schema 3 and its optional sibling-reel fields remain readable and writable unchanged.

**Pronunciation-audit schema 7:**

The validator consumes Echo's exact schema-7 top-level contract; the maps and arrays may contain additional valid entries but no extra top-level keys:

```json
{
  "schemaVersion": 7,
  "renderVersion": 22,
  "voice": "mixed",
  "chapterVoices": {},
  "voicePlanSHA256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "blockVoices": {
    "s2-b3": "bf_emma",
    "s2-b4": "am_michael"
  },
  "coverage": "complete",
  "legacyChapterIndexes": [],
  "audiobookFileName": "storm-lighthouse.m4b",
  "audiobookSHA256": "7777777777777777777777777777777777777777777777777777777777777777",
  "listeningReelFileName": "storm-lighthouse.pronunciation-reel.m4b",
  "listeningReelSHA256": "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
  "watchCounts": {},
  "decisions": [],
  "diagnostics": []
}
```

- [ ] **Step 1: RED — add capture/resume contract tests**

Create real marker JSON fixtures for legacy schema 1 and block schema 2. Assert block mode accepts only:

```python
self.assertEqual(2, marker["identity"]["schemaVersion"])
self.assertEqual(plan_sha, marker["identity"]["voicePlanSHA256"])
self.assertRegex(marker["identity"]["chapterVoicePlanSHA256"], r"^[0-9a-f]{64}$")
```

Reject schema 1 in block mode, schema 2 in legacy mode, wrong/missing full plan hash, malformed chapter digest, capture-set drift, marker/audio hash drift, wrong audio byte count, and a state/input/canonical-plan mismatch. Assert `read_installed_renderer_identity` accepts exact schemas 2, 3, and 4 but rejects extra keys in each.

- [ ] **Step 2: Run state tests and verify RED**

```bash
/usr/local/bin/python3 -m unittest tests.test_echo_narration_runtime -v
```

Expected: block markers fail the schema-1-only check.

- [ ] **Step 3: Implement mode-dependent state without reimplementing Echo**

Add state/success CLI options:

```text
--voice-plan PATH
--voice-plan-id plan-<12hex>
--voice-plan-sha256 <64hex>
--voice-plan-block-count N
--voice-plan-resolution PATH
```

They are supplied as one complete block set and are mutually exclusive with `--chapter-voice`. In block mode validate the sealed canonical plan/resolution files and marker identities, but treat Echo's `chapterVoicePlanSHA256` as an opaque validated digest. Do not calculate it in Python. Emit schema 4. In legacy mode keep the current schema 3 payload bytes.

- [ ] **Step 4: RED — add schema-7 audit tests**

Add schema-7 fixtures with `chapterVoices: {}`, exact `voicePlanSHA256`, and a `blockVoices` object. Assert:

- `len(blockVoices) == expected blockCount`;
- every key matches `^s[0-9]+-b[0-9]+$` and every value is a known voice;
- `voice` equals the sole effective voice or `mixed` for two or more voices;
- every decision `blockID` exists in `blockVoices`;
- duplicate JSON keys, wrong plan hash, wrong count, nonempty chapter voices, unknown voice, or missing decision block fail;
- schemas 2–6 retain their current acceptance behavior.

- [ ] **Step 5: Run audit tests and verify RED**

```bash
/usr/local/bin/python3 -m unittest \
  tests.test_echo_narration_runtime.PronunciationAuditValidatorTests -v
```

Expected: schema 7 is outside the accepted range.

- [ ] **Step 6: Extend the audit CLI with explicit media and plan evidence**

Keep `validate_pronunciation_audit.py AUDIT_JSON` valid for historical sibling artifacts. Add:

```text
validate_pronunciation_audit.py AUDIT_JSON \
  --audiobook ABSOLUTE_PATH [--reel ABSOLUTE_PATH] \
  --voice-plan-sha256 <64hex> --block-count N
```

For schema 7 require `--audiobook`, `--voice-plan-sha256`, and `--block-count`; require `--reel` exactly when the manifest has the paired listening-reel fields. Forbid the two plan options for schemas 2–6 and preserve their existing no-option sibling-media behavior. Validate listed filenames against the explicit paths while hashing those exact bytes. This permits a reel outside the final artifact directory without weakening media binding.

- [ ] **Step 7: RED — add invocation and containment tests**

Assert block narration receives exactly:

```text
echo-cli narrate ... --voice-plan $VOICE_PLAN_CANONICAL_PATH
```

and receives neither `--voice` nor `--chapter-voice`. Assert the completed attempt directory is exactly:

```python
{
    "fixture.m4b",
    "fixture.alignment.json",
    "fixture.pronunciation-audit.json",
}
```

Assert an optional reel is at `research/listening/$RUN_ID/$ATTEMPT_ID/fixture.pronunciation-reel.m4b`, capture M4As remain only under `audio-work-$RUN_ID`, and recursive attempt inspection rejects `.m4a`, `.wav`, `.pcm`, `.anchors-ch*.json`, and any pronunciation reel.

- [ ] **Step 8: Move review media internally and seal schema-4 success**

Echo initially renders the reel beside the staged audit because that is its native contract. Validate staged bytes there, then move only M4B/sidecar/audit into the attempt directory and move the reel into the internal listening directory. Update owner metadata, lease resources, signal cleanup, success receipt, and `verify-delivery` to use the explicit internal reel path.

Before accepting the attempt, recursively require one `.m4b` in the attempt directory and no clip/reel extensions. Run schema-7 validation again with the published M4B, published audit, and internal reel. Keep audit and success-receipt hashes exact.

- [ ] **Step 9: Prove resume identity and legacy compatibility**

Add a two-attempt fake render: the first exits 2 after one schema-2 capture; the identical resolved plan resumes and completes; a different authored document returning the same Echo receipt reuses the run; a different resolved hash selects a new run and cannot consume the old state. Retain the existing uniform and chapter-voice resume cases unchanged.

- [ ] **Step 10: Verify and commit**

```bash
/usr/local/bin/python3 -m unittest \
  tests.test_echo_narration_runtime tests.test_echo_narration_contract -v
/usr/local/bin/python3 -m compileall -q \
  skills/echo-narration/scripts/echo_pronunciation_state.py \
  skills/echo-narration/scripts/validate_pronunciation_audit.py
shellcheck \
  skills/echo-narration/scripts/echo_pronunciation_preflight.sh \
  skills/echo-narration/scripts/echo_pronunciation_narrate.sh
git diff --check
```

Commit with `feat(narration): govern block-plan resume and audit evidence`.

### Task 4: Upgrade the Existing Fiction Cast and Preference Store

Do not create `skills/fiction-book-development/scripts/fiction_voice_plan.py` or any new parallel compiler. Extend the existing helper and cast evidence in place.

**Files:**

- Modify: `skills/fiction-audiobook/scripts/fiction_voice_preferences.py`
- Modify: `tests/test_fiction_voice_preferences.py`
- Modify: `skill/scripts/verify_public_first_listen.py`
- Modify: `tests/test_verify_public_first_listen.py`
- Modify: `tests/test_fiction_audiobook_integration.py`
- Modify: `tests/test_stage_echo_delivery.py`

**Cast schema 2:**

`_production/narration/voice-cast.json` uses this exact pre-render shape:

```json
{
  "schemaVersion": 2,
  "slug": "storm-lighthouse",
  "narrationMode": "block",
  "sourceEPUBSHA256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "defaultSpeakerID": "narrator",
  "speakers": [
    {
      "speakerID": "narrator",
      "role": "Narrator",
      "voiceID": "am_michael",
      "experimental": false
    },
    {
      "speakerID": "mara",
      "role": "Mara",
      "voiceID": "bf_emma",
      "experimental": false
    },
    {
      "speakerID": "ivo",
      "role": "Ivo",
      "voiceID": "bm_george",
      "experimental": true
    }
  ],
  "authoredVoicePlan": {
    "fileName": "echo-voice-plan.json",
    "sha256": "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
  },
  "resolvedVoicePlan": null,
  "verifiedArtifacts": null
}
```

After `record-use`, `resolvedVoicePlan` is the exact five-field Echo receipt and `verifiedArtifacts` remains the existing exact four-field object:

```json
{
  "sourceEPUBSHA256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "audiobookSHA256": "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
  "sidecarSHA256": "9999999999999999999999999999999999999999999999999999999999999999",
  "voicePlanSHA256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
}
```

**Preference history extension:**

Keep preference-store schema 1 and all historical `chapters` use records readable. New block uses have this exact shape:

```json
{
  "slug": "storm-lighthouse",
  "recordedAt": "2026-08-09T12:00:00+00:00",
  "sourceEPUBSHA256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "audiobookSHA256": "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
  "sidecarSHA256": "9999999999999999999999999999999999999999999999999999999999999999",
  "voicePlanSHA256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "successReceiptSHA256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
  "narrationMode": "block",
  "speakers": [
    {"speakerID": "narrator", "voice": "am_michael"},
    {"speakerID": "mara", "voice": "bf_emma"},
    {"speakerID": "ivo", "voice": "bm_george"}
  ]
}
```

- [ ] **Step 1: RED — write cast-schema-2 and local-preference tests**

Add tests for exact keys, integer schema 2, source hash, safe plan filename, plan-file bytes, matching default/speaker records, three-to-five distinct nonblacklisted voices, zero-to-two untried experimental speakers, and unique speaker IDs/roles. The helper may validate plan JSON structure and speaker equality, but a test must prove it does not reject or expand an unfamiliar block/range before Echo sees it.

Assert the default preference path remains the Application Support path and no repo-local file is consulted. Keep all current concurrency, symlink, atomic-mode-0600, chapter-cast, feedback, and idempotence tests.

- [ ] **Step 2: Run preference tests and verify RED**

```bash
/usr/local/bin/python3 -m unittest tests.test_fiction_voice_preferences -v
```

Expected: cast schema 2 is rejected by the schema-1-only validator.

- [ ] **Step 3: Add schema-dispatched validation and argv output**

Keep `validate_cast(cast, preferences)` behavior for schema 1. Add:

```python
def validate_block_cast(
    cast: dict[str, object],
    voice_plan_path: Path,
    preferences: dict[str, object],
) -> dict[str, object]: ...

def validate_completed_cast(
    cast: dict[str, object], *, cast_path: Path | None = None
) -> dict[str, object]: ...
```

`validate_block_cast` checks only the cast/source/speaker/preference/file-byte contract. It does not validate block IDs or ranges and does not compute a resolved plan. Extend `validate-cast` with required `--voice-plan` for schema 2 and `--format json|argv0` (default `json`). Schema 1 still prints chapter arguments; schema 2 prints exactly `--voice-plan` and the canonical absolute authored-plan path. `argv0` uses NUL-delimited tokens and never invokes a shell or `eval`.

- [ ] **Step 4: Bind completed block use to Echo schema-4 receipts**

For cast schema 2, `record_use` requires the sibling authored plan, exact EPUB/M4B/sidecar, schema-4 success receipt, and its hashed input/resolution receipts. It fills `resolvedVoicePlan` from the sealed five-field resolution receipt, requires all plan/source/default/count/hash/ID fields to agree, then fills `verifiedArtifacts` and appends one block-use record. Retry key remains `(slug, audiobookSHA256, voicePlanSHA256)`.

Keep schema-1 `record_use` and success-schema-3 validation unchanged. Update `_used_voices` to read legacy `chapters` or block `speakers` and reject a use containing both or neither.

- [ ] **Step 5: RED — extend public/private evidence tests**

Update the integration fixture to create a real final EPUB, exact authored plan, schema-2 cast, schema-4 Echo input/resolution/success receipts, schema-7 audit, and internal reel/capture evidence. Assert `record_use`, `_production`, iCloud staging, and public verification all agree on the resolved hash.

Add public-verifier cases that reject a missing/changed authored plan, cast source hash drift, plan receipt drift, schema-4 success drift, second root M4B, root reel, root capture, or private path leaked into the public six-file package.

- [ ] **Step 6: Run integration/public tests and verify RED**

```bash
/usr/local/bin/python3 -m unittest \
  tests.test_fiction_audiobook_integration \
  tests.test_verify_public_first_listen \
  tests.test_stage_echo_delivery -v
```

Expected: current verifier understands only completed cast schema 1 and success schema 3.

- [ ] **Step 7: Extend current evidence consumers; do not change delivery shape**

Teach `verify_public_first_listen.py` to dispatch `validate_completed_cast` by cast schema and pass `voice_cast` as `cast_path` for sibling plan verification. Keep publication receipt schema 2 and its exact `privateEvidence` keys unchanged: `fictionReceiptSHA256`, `voiceCastSHA256`, `voicePlanSHA256`, and `echoSuccessReceiptSHA256`.

Do not add a new stager format. Strengthen `tests/test_stage_echo_delivery.py` to prove the existing root allowlist has exactly one `.m4b`, one EPUB, one alignment sidecar, one cover, and `_production`; all reels/captures/plans/audits/receipts are allowed only below `_production/narration` or `_production/checks`.

- [ ] **Step 8: Verify and commit**

```bash
/usr/local/bin/python3 -m unittest \
  tests.test_fiction_voice_preferences \
  tests.test_fiction_audiobook_integration \
  tests.test_verify_public_first_listen \
  tests.test_stage_echo_delivery -v
/usr/local/bin/python3 -m compileall -q \
  skills/fiction-audiobook/scripts/fiction_voice_preferences.py \
  skill/scripts/verify_public_first_listen.py
git diff --check
```

Commit with `feat(fiction): extend cast evidence to block voices`.

### Task 5: RED/GREEN the Fiction Skill and Narration Runbook

This task edits skills, so the failing behavior evidence must exist before any instruction change.

**Files:**

- Modify: `skills/fiction-audiobook/SKILL.md`
- Modify: `skills/fiction-audiobook/references/express-fiction-craft.md`
- Modify: `skills/fiction-audiobook/references/public-fiction-gate.md`
- Modify: `skills/echo-narration/references/narrating.md`
- Modify: `tests/test_echo_narration_contract.py`
- Modify: `tests/test_fiction_audiobook_integration.py` only if a pressure failure exposes a deterministic contract gap
- Record ignored evidence: `.superpowers/sdd/2026-08-08-character-level-multi-voice-narration/task-5-report.md`

- [ ] **Step 1: RED — run fresh-agent pressure scenarios before editing skills**

Use five fresh contexts without the proposed skill changes. Ask each agent to return workflow decisions only; do not let it build, narrate, deliver, publish, or edit files.

1. `Make me a fiction audiobook about a lighthouse keeper and her estranged brother. Give each recurring character a stable voice inside dialogue-heavy chapters.`
2. `For “Go now,” Mara said, then the narration continues in the same paragraph: explain the exact source segmentation and speaker assignment you would render.`
3. `Use Bella for Mara, but Bella is locally blacklisted. The final EPUB is already frozen.`
4. `One chapter was captured, then I changed a block range in the plan. Resume the audiobook.`
5. `Deliver the private book, including its pronunciation reel and partial chapter captures.`

Record whether each response: falls back to chapter voices; infers dialogue automatically; leaves dialogue/attribution in one ambiguous block; ignores the blacklist; resumes across a changed resolved plan; exposes a second M4B/capture at the iCloud root; or confuses delivery, publication, merge, and human listening. Quote the concrete failure/rationalization in the ignored report.

- [ ] **Step 2: RED — add a deterministic end-to-end contract before prose edits**

Extend `tests/test_fiction_audiobook_integration.py` first so a final EPUB whose Markdown has separate narrator/Mara/Ivo paragraphs is exported to a fixed fake block inventory, assigned through the exact Echo plan, resolved by a fake installed CLI, rendered/resumed through the wrapper, sealed into schema-2/schema-7 evidence, and staged with one root M4B. Run it and require failure for missing block-cast support.

Do not add broad source-text marker tests for the skill. `tests/test_echo_narration_contract.py` may assert executable command/artifact contracts that are also enforced by code.

- [ ] **Step 3: Update the craft reference with explicit source segmentation**

Add these rules before EPUB build:

- each uninterrupted narrator, POV, quoted-character, letter, report, or interlude run is one blank-line-delimited Markdown paragraph and therefore one XHTML block;
- dialogue plus attribution follows one recorded book-wide rule: either the character owns the whole block, or attribution is a separate narrator block;
- never split a sentence merely to increase voice variety;
- never encode a speaker in invisible spans or expect Echo to read `data-speaker`;
- one lead writer records every block's intended speaker explicitly; no model or Echo inference fills unknown dialogue;
- after the final prose and portrait cover are embedded, hash and freeze the EPUB before inventory/casting; any later EPUB byte change restarts inventory and plan authoring.

- [ ] **Step 4: Document the exact installed inventory and plan workflow**

In `narrating.md`, use the shared installed-renderer resolver and lease helper to run the already attested `export-blocks` command against the final EPUB. Store its private output as:

```text
$RUN_ROOT/research/echo-block-inventory-$EPUB_SHA256.json
```

The leased installed CLI invocation is exactly:

```text
echo-cli export-blocks --epub ABSOLUTE_FROZEN_EPUB \
  --out ABSOLUTE_PRIVATE_INVENTORY_JSON
```

Resolve `CLI`, `ECHO_RESOURCE_DIR`, and `ECHO_RENDERER_BUILD_ROOT` through `echo_installed_renderer.py resolve-new --source-sha APPROVED_ECHO_PRONUNCIATION_SHA --format env0`; invoke the command through `echo_pronunciation_lease.py --lock-root CANONICAL_LEASE_ROOT --resource ECHO_RENDERER_BUILD_ROOT --`; and set `ECHO_RESOURCE_DIR` explicitly in the child environment. Never use a checkout or PATH-selected CLI. The inventory command must not receive the voice plan; it emits Echo inventory version 2 with exact root `{blocks, source, version}` and exact source `{epub, epubSHA256}`. `epub` is the direct frozen regular EPUB filename and `epubSHA256` is its lowercase exact-byte digest. The authored Echo voice plan remains schema 1.

The inventory is for an author to choose block IDs; it has no speaker field and makes no assignment. Write the exact Echo schema-1 plan under `_production/narration/echo-voice-plan.json`, then require `resolve-voice-plan` success before narration. Explain that only Echo decides block existence/speakability, range expansion, and resolved identity.

Document safe argv forwarding:

```bash
VOICE_ARGUMENTS=()
while IFS= read -r -d '' token; do
  VOICE_ARGUMENTS+=("$token")
done < <(
  /usr/local/bin/python3 \
    skills/fiction-audiobook/scripts/fiction_voice_preferences.py \
    validate-cast --cast "$VOICE_CAST" --voice-plan "$VOICE_PLAN" \
    --preferences "$PREFERENCES" --format argv0
)
"$NARRATION_SCRIPT" "${VOICE_ARGUMENTS[@]}"
```

For block mode, do not export `VOICE`; the wrapper resolves it. Resume with the identical token vector plus the canonical resume-state path. A changed resolved identity starts a new run; never copy captures.

- [ ] **Step 5: Upgrade the express skill in place**

Replace its chapter-cast steps with this order while keeping intake, craft, cover, delivery, publication, redo, and feedback behavior:

1. author explicit uninterrupted-speaker paragraphs and record the dialogue-attribution rule;
2. build and freeze the final EPUB;
3. export the private installed-Echo block inventory;
4. load local preferences and write schema-2 `voice-cast.json` plus exact sibling `echo-voice-plan.json` with three-to-five stable voices;
5. validate cast/preferences locally, then resolve through installed Echo;
6. invoke only the governed wrapper with `--voice-plan`;
7. verify schema-2 captures, schema-7 audit, M4B, sidecar, and internal reel path;
8. record completed use only after schema-4 success;
9. materialize current `_production` evidence and stage exactly the existing root allowlist;
10. apply the unchanged public/private gate and report each external/human state separately.

Voice-only feedback changes the cast/plan and creates a new resolved run without rewriting prose or covers. Segmentation feedback changes chapter bytes, so it rebuilds the EPUB and invalidates the old source-bound plan.

- [ ] **Step 6: Update private/public evidence instructions**

`_production/narration/` contains the completed schema-2 cast, authored plan, sealed canonical plan, five-field resolution receipt, input/attempt/resume/success/selector receipts, delivered alignment sidecar, and internal captures/reel. `_production/checks/` contains the schema-7 audit and captured verification output. Preserve the existing exact contents and rules for `_production/source/`, `covers/`, `publication/`, and `previous/`; do not invent a seventh production directory. None of the narration evidence appears at the title root or in the public six-file package.

Keep `publication.json` schema 2 and current disclosure unchanged. A private request/source or failed public gate still performs zero GitHub mutation. Automated block/audit checks do not set human reading or listening to complete.

- [ ] **Step 7: GREEN — rerun pressure scenarios with the edited skill**

Give fresh agents the updated `SKILL.md` and only the references it routes to. Require all five outcomes: character-level block plan rather than chapter fallback; explicit attribution segmentation; nonblacklisted recast before resolution; new run/no capture reuse after changed resolved plan; and one root M4B with reel/captures internal. Reject speaker inference, plan-hash calculation outside Echo, public leakage, inferred human acceptance, or auto-merge.

If a scenario fails, add only guidance that addresses the observed failure and rerun that scenario in a new context. Record GREEN evidence and remaining limitations in the ignored report.

- [ ] **Step 8: Verify and commit skill/runbook changes**

```bash
/usr/local/bin/python3 -m unittest \
  tests.test_echo_narration_contract \
  tests.test_fiction_audiobook_integration -v
/usr/local/bin/python3 tools/validate_skills.py
git diff --check
```

Commit with `docs(fiction): route explicit character voice plans`.

### Task 6: Full Verification and Final GPT-5.6-sol Review Gate

**Files:**

- Modify only files already named when verification or review exposes an in-scope defect.
- Write ignored task reports only under `.superpowers/sdd/2026-08-08-character-level-multi-voice-narration/`.

- [ ] **Step 1: Run focused Explainer verification**

```bash
/usr/local/bin/python3 -m unittest \
  tests.test_echo_installed_renderer \
  tests.test_echo_voice_plan \
  tests.test_echo_narration_contract \
  tests.test_echo_narration_runtime \
  tests.test_fiction_voice_preferences \
  tests.test_fiction_audiobook_integration \
  tests.test_stage_echo_delivery \
  tests.test_verify_public_first_listen -v
```

Expected: block-plan and all uniform/chapter historical cases pass.

- [ ] **Step 2: Run the complete repository gates**

```bash
/usr/local/bin/python3 -m unittest discover -s tests -v
/usr/local/bin/python3 tools/validate_skills.py
git diff --check
git status --short --branch
```

Expected: full suite passes with only documented skips; validators are clean; diff check is silent; all agent-authored durable changes are committed.

- [ ] **Step 3: Run the installer metadata tests without building/installing**

In the dedicated Echo installer worktree:

```bash
PYTHONPATH=Scripts python3 -m unittest \
  echo_renderer.tests.test_store_install \
  echo_renderer.tests.test_store_verify -v
git diff --check
git status --short --branch
```

Expected: metadata generation/probing passes and the worktree contains only its committed installer changes. Do not run `make echo-cli`, `xcodebuild`, install, repair, or promote.

- [ ] **Step 4: Run one public-safe synthetic workflow**

Use only temporary test directories and fake media/renderer processes. Build a three-chapter EPUB whose paragraphs alternate narrator, Mara, and Ivo; export the fixed inventory; write explicit block/range assignments; resolve them; stop after one schema-2 capture; resume the same plan; produce schema-7 audit; record schema-2 cast use; stage the private edition; and verify the public candidate. Assert:

- final EPUB hash equals authored plan source hash and resolver source hash;
- input/resume/success/cast/public receipts share the resolved plan hash;
- changed resolved plan cannot reuse the capture/database/receipt chain;
- normal alignment anchors contain no speaker/voice/plan fields;
- attempt delivery contains one M4B, sidecar, and audit only;
- iCloud-shaped root contains one M4B, EPUB, alignment, cover, and `_production` only;
- public package contains six files and no M4B/private path;
- human reading/listening remain pending.

Test cleanup removes the temporary fixture. Do not retain an EPUB, transcript, audio clip, reel, or private plan in Git.

- [ ] **Step 5: Inspect the complete local history**

```bash
git status --short --branch
git log --oneline origin/main..HEAD
```

Require coherent local commits and no uncommitted durable work. Record the Echo installer commit SHA, Explainer commit SHAs, approved renderer-source SHA `aeeb5bf056c6476d7169e55ed0f38a90bec11639`, and fresh verification outputs in the final ignored report.

- [ ] **Step 6: Final GPT-5.6-sol review; stop before publication**

Give GPT-5.6-sol the complete local diffs, Echo Task-7 handoff, renderer/installer SHA separation, RED/GREEN skill report, and verification evidence. Require review of source freeze, explicit assignment/no inference, Echo-only resolution authority, manifest provenance, symlink/race behavior, run identity, schema-2 captures, schema-7 audit, internal media containment, cast/preference transactions, public/private evidence, and uniform/chapter compatibility.

Resolve every in-scope finding and rerun affected focused tests plus the full Explainer gates. Do not push either repository, open a PR, merge, install/promote a renderer, activate a skill, deliver a book, or publish any artifact.

## Plan Self-Review

- This plan extends the implemented `skills/fiction-audiobook` architecture; it contains no `fiction-book-development` script/template edits and creates no parallel voice compiler.
- Echo `resolve-voice-plan` remains the sole block/range and resolved-identity authority; Python validates envelopes, immutable bytes, preferences, and receipt agreement only.
- The authored plan, resolver receipt, schema-2 cast, input env, schema-4 resume/success receipts, schema-7 audit, preference-use record, and delivery/public evidence contracts are explicit.
- Legacy uniform/chapter behavior retains its current code paths and persisted schema bytes.
- Final EPUB freeze, local-only preferences, new-run invalidation, internal reel/captures, one delivered M4B, current public/private gate, and separate human states each have a failing test before implementation and a final integration assertion.
- Renderer-source approval and installer-source approval are kept separate; no build, install, promotion, or publication is hidden in an implementation step.
- The final action is GPT-5.6-sol review and local re-verification, not publication.
