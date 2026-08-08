# Fiction Audiobook Express Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a standalone `fiction-audiobook` skill that takes a one-sentence premise through autonomous fiction development, a three-to-five-voice governed Echo render, Echo-clean iCloud delivery, and public-first GitHub publication with a private fail-closed fallback.

**Architecture:** Keep the creative workflow in a lean skill and two deterministic helpers. Extend the existing Echo wrapper with a sealed fiction run lane, store durable voice feedback in a private versioned JSON record, promote each iCloud edition through an exact-root atomic stager, and extend the existing public-package verifier with a backward-compatible fiction schema whose M4B is verified outside Git and uploaded as a release asset. Reuse the existing fiction production receipt, book builder, paired-cover flow, Echo voice-plan identity, and governed narration proofs.

**Tech Stack:** Python 3.11 (`/usr/local/bin/python3`), `unittest`, Bash, Pillow 9.4.0, Echo/Kokoro CLI, Git, and GitHub CLI.

## Global Constraints

- Run every repository command from `/Users/dfakkeldy/.codex/worktrees/7bba/explainer-audiobooks`.
- Use `/usr/local/bin/python3` for tests and tools that import the book builder or Pillow. `/opt/homebrew/bin/python3` is 3.14.6 and has no Pillow; `/usr/local/bin/python3` is 3.11.1 with Pillow 9.4.0.
- Baseline on 2026-08-08: `/usr/local/bin/python3 -m unittest discover -s tests -v` ran 514 tests in 337.885 seconds and passed with 7 skips.
- Keep `skill/scripts/fiction_production_qc.py` and the `--fiction-receipt` build contract unchanged. Its private first-listen receipt authorizes packaging, never publication.
- Do not invoke or import `fiction-book-development` from the new skill. The express skill is a separate route, not a mode of the long workflow.
- Keep one lead writer responsible for every canonical chapter and substantive repair. Agents may diagnose or verify, but may not independently draft competing chapters.
- Use chapter-level voices only. Do not add speaker parsing, dialogue-line routing, or new Echo rendering behavior.
- Preserve `af_heart` as initially blacklisted. Never silently change an immutable cast or rerender an old book because a later preference changed.
- The iCloud title directory has an exact root allowlist: `<slug>.m4b`, `<slug>.epub`, `<slug>.alignment.json`, `cover.png`, and `_production/`. All other material belongs below `_production/`.
- Public fiction is the ordinary outcome only after the automated original/public-safe gate passes. A private request, private source, rights uncertainty, or failed gate must cause zero GitHub mutations.
- The public repository package excludes the M4B. Upload the exact verified M4B as a GitHub Release asset targeting the pushed book commit. Open a ready PR and do not auto-merge it.
- Keep iCloud delivery, GitHub push, ready PR, release upload, merge, human reading, and human listening as separate reported states.
- Do not point installed skill symlinks at this disposable worktree. Activate the skill from the canonical checkout only after the implementation PR is merged.
- Line numbers below are pre-edit. Locate code by the quoted function or marker rather than by line number alone.

**Spec:** `docs/superpowers/specs/2026-08-08-fiction-audiobook-design.md`

---

### Task 1: Add a sealed fiction narration lane

The governed wrapper currently accepts only `.build/custom-learning-audiobooks/<slug>/`, including its resume precheck and second input attestation. The express skill needs `.build/fiction-audiobooks/<slug>/` without weakening those exact-path guarantees.

**Files:**

- Modify: `tests/test_echo_narration_runtime.py`
- Modify: `tests/test_echo_narration_contract.py`
- Modify: `skills/echo-narration/scripts/echo_pronunciation_preflight.sh`
- Modify: `skills/echo-narration/scripts/echo_pronunciation_narrate.sh`
- Modify: `skills/echo-narration/references/narrating.md`

**Interface:**

```text
ECHO_RUN_LANE=audiobook          -> .build/custom-learning-audiobooks/<slug>/
ECHO_RUN_LANE=fiction-audiobook  -> .build/fiction-audiobooks/<slug>/
unset ECHO_RUN_LANE              -> audiobook (backward compatible)
anything else                    -> exit 64 before narration
```

- [ ] **Step 1: Add failing runtime coverage for the new lane and fail-closed values**

In `tests/test_echo_narration_runtime.py`, add a fixture relocation helper:

```python
def use_run_lane(self, folder: str) -> None:
    destination = self.explainer / ".build" / folder / "fixture"
    destination.parent.mkdir(parents=True, exist_ok=True)
    self.run_root.rename(destination)
    self.run_root = destination
```

Then add:

```python
def test_fiction_lane_renders_and_seals_the_exact_run_root(self) -> None:
    self.use_run_lane("fiction-audiobooks")
    environment = self.environment()
    environment["ECHO_RUN_LANE"] = "fiction-audiobook"
    result = self.run_narrate(
        "--chapter-voice", "1=bf_emma", environment=environment
    )
    self.assertEqual(0, result.returncode, result.stderr)
    receipt = next(
        (self.run_root / "research").glob("echo-render-inputs-*.env")
    ).read_text(encoding="utf-8")
    self.assertIn("run_lane=fiction-audiobook\n", receipt + "\n")
    self.assertIn(f"run_root={self.run_root}\n", receipt + "\n")

def test_run_lane_rejects_unknown_or_cross_lane_roots(self) -> None:
    for lane in ("fiction", "../fiction", "Fiction"):
        with self.subTest(lane=lane):
            environment = self.environment()
            environment["ECHO_RUN_LANE"] = lane
            result = self.run_preflight(environment=environment)
            self.assertEqual(64, result.returncode)
            self.assertIn("ECHO_RUN_LANE", result.stderr)

    self.use_run_lane("fiction-audiobooks")
    environment = self.environment()
    environment["ECHO_RUN_LANE"] = "audiobook"
    result = self.run_preflight(environment=environment)
    self.assertEqual(64, result.returncode)
    self.assertIn("canonical run path", result.stderr)
```

Extend `test_resume_requires_the_canonical_absolute_state_path` so a successful fiction render resumes only with the same `ECHO_RUN_LANE=fiction-audiobook`; dropping or changing the lane must fail before the state receipt is consumed.

- [ ] **Step 2: Run the focused tests and observe failure**

```bash
/usr/local/bin/python3 -m unittest tests.test_echo_narration_runtime.EchoPronunciationPreflightTests.test_fiction_lane_renders_and_seals_the_exact_run_root tests.test_echo_narration_runtime.EchoPronunciationPreflightTests.test_run_lane_rejects_unknown_or_cross_lane_roots -v
```

Expected: FAIL because preflight still hardcodes `custom-learning-audiobooks` and does not write `run_lane` or `run_root`.

- [ ] **Step 3: Add one canonical lane-to-folder helper**

Near the other shared preflight helpers, add:

```bash
echo_pronunciation_run_folder() {
  case "${1:-}" in
    audiobook) printf '%s\n' 'custom-learning-audiobooks' ;;
    fiction-audiobook) printf '%s\n' 'fiction-audiobooks' ;;
    *)
      printf 'ECHO_RUN_LANE must be audiobook or fiction-audiobook\n' >&2
      return 64
      ;;
  esac
}

echo_pronunciation_expected_run_root() {
  local root=$1 slug=$2 lane=$3 folder
  folder=$(echo_pronunciation_run_folder "$lane") || return $?
  printf '%s/.build/%s/%s\n' "$root" "$folder" "$slug"
}
```

At the start of `echo_pronunciation_preflight`, set `ECHO_RUN_LANE=${ECHO_RUN_LANE:-audiobook}` and validate it. Replace both hardcoded expected-root expressions with this helper. Do not accept arbitrary subdirectories, prefixes, or caller-supplied folder names.

- [ ] **Step 4: Seal the lane and root in the input receipt**

Append these fields in `echo_pronunciation_receipt_text()` before package hashes:

```bash
"run_lane=$ECHO_RUN_LANE" \
"run_root=$RUN_ROOT" \
```

Add `ECHO_RUN_LANE` to `echo_pronunciation_attest_inputs`' required variables and export it with the sealed fields. During attestation, derive `expected_run_root` through the same helper and require the lane and root to agree. The receipt hash already flows into resume, attempt, success, and selector receipts, so `echo_pronunciation_state.py` needs no schema change.

- [ ] **Step 5: Make the pre-preflight resume check lane-aware**

In `echo_pronunciation_narrate.sh`, before validating `RESUME_STATE`, add:

```bash
ECHO_RUN_LANE=${ECHO_RUN_LANE:-audiobook}
RUN_FOLDER=$(echo_pronunciation_run_folder "$ECHO_RUN_LANE") || exit $?
export ECHO_RUN_LANE
```

Replace the resume root with:

```bash
canonical_resume_root="$canonical_explainer_root/.build/$RUN_FOLDER/${SLUG:-}/research"
```

Do not add a command-line flag. The environment value must survive the lease wrapper's internal `exec` and be re-attested after rendering.

- [ ] **Step 6: Document and contract-test both exact lanes**

Add a “Run lanes” section to `narrating.md` with both mappings, the default, and a fiction invocation. Add to `tests/test_echo_narration_contract.py`:

```python
def test_run_lanes_are_exact_documented_and_receipt_bound(self) -> None:
    combined = self.narrating + self.preflight + self.narrate_wrapper
    for marker in (
        "ECHO_RUN_LANE", "audiobook", "fiction-audiobook",
        "custom-learning-audiobooks", "fiction-audiobooks",
        "run_lane=", "run_root=",
    ):
        self.assertIn(marker, combined)
    self.assertNotIn(".build/$ECHO_RUN_LANE", combined)
```

- [ ] **Step 7: Run and commit**

```bash
/usr/local/bin/python3 -m unittest tests.test_echo_narration_contract tests.test_echo_narration_runtime -v
git add tests/test_echo_narration_runtime.py tests/test_echo_narration_contract.py skills/echo-narration/scripts/echo_pronunciation_preflight.sh skills/echo-narration/scripts/echo_pronunciation_narrate.sh skills/echo-narration/references/narrating.md
git commit -m "feat: add governed fiction narration lane"
```

Expected: both modules pass, including a fake-renderer run and resume in `.build/fiction-audiobooks/`.

---

### Task 2: Implement durable ensemble voice preferences

The creative skill can choose a cast, but a deterministic helper must reject unknown or blacklisted voices, enforce ensemble consistency, bind the cast to Echo's canonical voice-plan identity, and write private feedback atomically.

**Files:**

- Create: `skills/fiction-audiobook/scripts/fiction_voice_preferences.py`
- Create: `tests/test_fiction_voice_preferences.py`

**Preference schema:**

```json
{
  "schemaVersion": 1,
  "blacklist": {
    "af_heart": {
      "updatedAt": "1970-01-01T00:00:00+00:00",
      "reason": "standing audiobook preference"
    }
  },
  "verdicts": {},
  "uses": [],
  "updatedAt": "1970-01-01T00:00:00+00:00"
}
```

**Cast schema:**

```json
{
  "schemaVersion": 1,
  "slug": "storm-lighthouse",
  "chapterCount": 8,
  "defaultVoice": "bf_emma",
  "chapters": [
    {"chapter": 1, "role": "Mara", "voice": "bf_emma", "experimental": false}
  ],
  "voicePlanSHA256": "64 lowercase hexadecimal characters",
  "voicePlanID": "plan identity from echo_voice_plan.py",
  "verifiedArtifacts": null
}
```

- [ ] **Step 1: Write failing tests for defaults, validation, completed use, and feedback**

Create `tests/test_fiction_voice_preferences.py`, load the script with `importlib.util`, and cover:

```python
def test_missing_store_supplies_the_standing_heart_blacklist(self) -> None:
    preferences = module.load_preferences(self.preferences_path)
    self.assertIn("af_heart", preferences["blacklist"])
    self.assertFalse(self.preferences_path.exists())

def test_cast_requires_three_to_five_known_nonblacklisted_voices(self) -> None:
    cast = self.valid_cast()
    module.validate_cast(cast, module.load_preferences(self.preferences_path))
    for voice, message in (
        ("af_heart", "blacklisted"),
        ("not_a_voice", "unknown Echo voice"),
    ):
        changed = copy.deepcopy(cast)
        changed["chapters"][2]["voice"] = voice
        with self.assertRaisesRegex(ValueError, message):
            module.validate_cast(changed, module.load_preferences(self.preferences_path))

def test_recurring_role_keeps_one_voice_and_every_chapter_is_present(self) -> None:
    inconsistent = self.valid_cast()
    inconsistent["chapters"][3]["voice"] = "bm_george"
    with self.assertRaisesRegex(ValueError, "recurring role"):
        module.validate_cast(inconsistent, module.load_preferences(self.preferences_path))
    missing = self.valid_cast()
    missing["chapters"].pop(1)
    with self.assertRaisesRegex(ValueError, "every chapter"):
        module.validate_cast(missing, module.load_preferences(self.preferences_path))

def test_feedback_resolves_bella_and_blacklists_future_casts(self) -> None:
    module.set_verdict(
        self.preferences_path, "Bella", "blacklisted", "too breathy",
        "2026-08-08T13:00:00+00:00",
    )
    saved = module.load_preferences(self.preferences_path)
    self.assertIn("af_bella", saved["blacklist"])
    with self.assertRaisesRegex(ValueError, "blacklisted"):
        module.validate_cast(self.valid_cast(), saved)
```

Also test zero-to-two experimental rows, experimental voices that must be untried, atomic mode `0600`, idempotent use records, changed EPUB/M4B/sidecar rejection, and changed plan identity rejection. Before narration `verifiedArtifacts` must be null. The governed success fixture contains `sourceEPUBFileName`, `sourceEPUBSHA256`, `audiobookFileName`, `audiobookSHA256`, `sidecarFileName`, `sidecarSHA256`, and `voicePlanSHA256` matching the cast and files.

- [ ] **Step 2: Run and observe import failure**

```bash
/usr/local/bin/python3 -m unittest tests.test_fiction_voice_preferences -v
```

Expected: ERROR because the helper does not exist.

- [ ] **Step 3: Implement exact voice resolution and default loading**

Import `VOICE_IDS` and `voice_plan` from `skills/echo-narration/scripts/echo_voice_plan.py` by adding that exact directory to `sys.path`. Implement:

```python
DEFAULT_PATH = Path.home() / "Library/Application Support/Explainer Audiobooks/fiction-voice-preferences.json"
INITIAL_TIMESTAMP = "1970-01-01T00:00:00+00:00"

def resolve_voice(value: str) -> str:
    normalized = value.strip().casefold().replace(" ", "_")
    if normalized in VOICE_IDS:
        return normalized
    matches = sorted(
        voice for voice in VOICE_IDS if voice.split("_", 1)[1] == normalized
    )
    if len(matches) != 1:
        raise ValueError(f"unknown or ambiguous Echo voice: {value}")
    return matches[0]

def initial_preferences() -> dict[str, object]:
    return {
        "schemaVersion": 1,
        "blacklist": {
            "af_heart": {
                "updatedAt": INITIAL_TIMESTAMP,
                "reason": "standing audiobook preference",
            }
        },
        "verdicts": {},
        "uses": [],
        "updatedAt": INITIAL_TIMESTAMP,
    }
```

`load_preferences` returns this without writing when absent. When present, reject duplicate keys, wrong shapes, unknown voices, invalid timestamps, symlinks, and records omitting the standing `af_heart` blacklist.

- [ ] **Step 4: Validate casts through Echo's canonical plan**

Implement `validate_cast(cast, preferences) -> dict[str, object]`. Require chapters exactly `1...chapterCount`, three-to-five distinct nonblacklisted voices, stable recurring roles, real boolean experimental flags, no more than two experimental rows, and no earlier use of an experimental voice. Call:

```python
plan = voice_plan(
    cast["defaultVoice"],
    [f"{row['chapter']}={row['voice']}" for row in cast["chapters"]],
)
```

Require exact `voicePlanSHA256` and `voicePlanID` matches, then return `plan` so the skill can forward every canonical assignment.

- [ ] **Step 5: Implement atomic feedback and completed-use updates**

Write JSON through a same-directory temporary file, `flush`, `os.fsync`, `chmod(0o600)`, and `os.replace`. Never write through a symlink. `record_use` computes the EPUB, M4B, sidecar, and success-receipt hashes; compares their names and hashes plus the voice-plan hash with the governed success receipt; atomically replaces the cast's null `verifiedArtifacts` with those four hashes; then appends one preference use record. Repeating `(slug, M4B hash, voice-plan hash)` is idempotent. A partial failure may leave the verified cast written but not the preference history, so retry must safely finish the missing preference write without altering the cast identity.

`set_verdict` accepts `liked`, `disliked`, `blacklisted`, or `clear`. `blacklisted` writes the verdict and blacklist entry. `clear` removes the explicit verdict and blacklist entry except that v1 never clears `af_heart`.

- [ ] **Step 6: Add the CLI**

```text
fiction_voice_preferences.py validate-cast --cast PATH [--preferences PATH]
fiction_voice_preferences.py record-use --cast PATH --epub PATH --m4b PATH --sidecar PATH --success-receipt PATH --at ISO8601 [--preferences PATH]
fiction_voice_preferences.py set-verdict --voice NAME_OR_ID --verdict liked|disliked|blacklisted|clear --at ISO8601 [--reason TEXT] [--preferences PATH]
```

`validate-cast` prints the canonical `--chapter-voice N=voice_id` arguments as JSON without mutation. Mutating commands print the saved record.

- [ ] **Step 7: Run and commit**

```bash
/usr/local/bin/python3 -m unittest tests.test_echo_voice_plan tests.test_fiction_voice_preferences -v
git add skills/fiction-audiobook/scripts/fiction_voice_preferences.py tests/test_fiction_voice_preferences.py
git commit -m "feat: track fiction voice preferences"
```

Expected: existing Echo plan tests and all new preference tests pass.

---

### Task 3: Implement atomic Echo-clean iCloud staging

The delivered title directory must be loadable by Echo without competing audio. The stager owns the exact root allowlist, hash verification, previous-edition archive, and rollback-safe promotion.

**Files:**

- Create: `skills/fiction-audiobook/scripts/stage_echo_delivery.py`
- Create: `tests/test_stage_echo_delivery.py`

**Prepared production input:**

```text
production/
  source/
  checks/
  narration/
  covers/
  publication/
  previous/
```

The skill fills the first five directories from the private run. `previous/` starts empty; the stager alone populates it from the destination's prior generated edition.

- [ ] **Step 1: Write failing allowlist and promotion tests**

Create `tests/test_stage_echo_delivery.py`, import the new script, and build four source files named `fixture.m4b`, `fixture.epub`, `fixture.alignment.json`, and `cover.png` plus the production skeleton. Add:

```python
def test_apply_promotes_only_four_loadable_files_and_production(self) -> None:
    result = module.stage_delivery(self.request(), apply=True)
    self.assertEqual("promoted", result.decision)
    self.assertEqual(
        {
            "fixture.m4b", "fixture.epub", "fixture.alignment.json",
            "cover.png", "_production",
        },
        {path.name for path in self.destination.iterdir()},
    )
    self.assertTrue(
        (self.destination / "_production/checks/delivery-manifest.json").is_file()
    )

def test_unexpected_root_item_is_preserved_and_blocks_promotion(self) -> None:
    module.stage_delivery(self.request(), apply=True)
    note = self.destination / "my-note.txt"
    note.write_text("keep me", encoding="utf-8")
    self.m4b.write_bytes(b"new audio")
    with self.assertRaisesRegex(ValueError, "my-note.txt"):
        module.stage_delivery(self.request(), apply=True)
    self.assertEqual("keep me", note.read_text(encoding="utf-8"))
    self.assertEqual(b"audio", (self.destination / "fixture.m4b").read_bytes())
    self.assertTrue(list(self.destination.parent.glob(".fixture.staging-*")))

def test_promotion_failure_restores_the_complete_old_edition(self) -> None:
    module.stage_delivery(self.request(), apply=True)
    before = module.tree_hash(self.destination)
    self.m4b.write_bytes(b"replacement")
    with mock.patch.object(module, "_rename_stage", side_effect=OSError("injected")):
        with self.assertRaisesRegex(OSError, "injected"):
            module.stage_delivery(self.request(), apply=True)
    self.assertEqual(before, module.tree_hash(self.destination))

def test_redo_archives_one_prior_generated_edition_and_is_idempotent(self) -> None:
    module.stage_delivery(self.request(), apply=True)
    self.m4b.write_bytes(b"replacement")
    module.stage_delivery(self.request(), apply=True)
    previous = self.destination / "_production/previous"
    self.assertEqual(b"audio", (previous / "fixture.m4b").read_bytes())
    self.assertFalse((previous / "_production/previous").exists())
    before = module.tree_hash(self.destination)
    result = module.stage_delivery(self.request(), apply=True)
    self.assertEqual("reuse", result.decision)
    self.assertEqual(before, module.tree_hash(self.destination))
```

Also test a mismatched M4B/EPUB/sidecar stem, missing or empty sidecar, invalid sidecar JSON, staged hash drift, an extra root audio file, source or destination symlinks, a dry run that does not mutate, and a new destination.

- [ ] **Step 2: Run and observe import failure**

```bash
/usr/local/bin/python3 -m unittest tests.test_stage_echo_delivery -v
```

Expected: ERROR because `stage_echo_delivery.py` does not exist.

- [ ] **Step 3: Implement immutable request and result types**

Use:

```python
@dataclass(frozen=True)
class DeliveryRequest:
    slug: str
    edition_id: str
    m4b: Path
    epub: Path
    alignment: Path
    cover: Path
    production: Path
    destination: Path

@dataclass(frozen=True)
class DeliveryResult:
    decision: str
    destination: str
    staging_directory: str | None
    applied: bool
    root_files: tuple[str, ...]
```

Validate a lowercase hyphenated slug, nonempty edition ID, regular non-symlink inputs, exact filenames, a nonempty JSON alignment object or array, and exact production entries `source`, `checks`, `narration`, `covers`, `publication`, `previous`. Recursively reject production symlinks.

- [ ] **Step 4: Stage and hash one complete edition**

Create the stage with:

```python
stage = Path(tempfile.mkdtemp(
    prefix=f".{request.slug}.staging-", dir=request.destination.parent
))
```

Copy the four loadable files with canonical names and the six production directories beneath `_production/`. Write `_production/checks/delivery-manifest.json`:

```json
{
  "schemaVersion": 1,
  "slug": "fixture",
  "editionId": "fixture-v2",
  "rootArtifacts": {
    "fixture.m4b": "sha256",
    "fixture.epub": "sha256",
    "fixture.alignment.json": "sha256",
    "cover.png": "sha256"
  }
}
```

Reopen and rehash every staged root artifact after copying. Reject any unexpected staged root entry before promotion.

- [ ] **Step 5: Validate and archive exactly one old generated edition**

If the destination exists, require its exact five root entries and exact six `_production` subdirectories. Any extra, missing, nonregular, or symlinked item is a conflict; preserve both destination and verified stage.

When source hashes differ, copy the old four root files into the new `_production/previous/` and copy old `_production` subdirectories except `previous` beneath `_production/previous/_production/`. This deliberately drops the older archive so only one prior generated edition survives.

When the new four hashes and current production tree excluding `previous` are identical, return `decision="reuse"` without renaming or growing the archive.

- [ ] **Step 6: Promote with rollback**

For an existing destination, rename it to a unique same-parent backup, rename the verified stage to the destination, and remove the backup only after the second rename succeeds. If stage rename raises, rename the backup back before re-raising. For a new destination, one same-parent rename publishes the stage. Never copy files individually into the live title directory.

Keep a verified stage after a destination conflict. Clean an unpromoted stage only for source-validation failures before it becomes complete.

- [ ] **Step 7: Add the CLI**

```text
stage_echo_delivery.py --slug SLUG --edition-id ID --m4b PATH --epub PATH --alignment PATH --cover PATH --production PATH --destination PATH [--apply]
```

Without `--apply`, validate source and destination policy without creating or mutating the destination. Print `DeliveryResult` as sorted JSON.

- [ ] **Step 8: Run and commit**

```bash
/usr/local/bin/python3 -m unittest tests.test_stage_echo_delivery -v
git add skills/fiction-audiobook/scripts/stage_echo_delivery.py tests/test_stage_echo_delivery.py
git commit -m "feat: stage Echo-clean fiction deliveries"
```

Expected: staging, rollback, conflict, archive, symlink, and idempotence tests pass.

---

### Task 4: Extend public-package verification for release-backed fiction

The existing schema v1 verifier requires an M4B and square cover inside `books/<slug>/`. Fiction's public package intentionally excludes both. Add a schema v2 fiction path while preserving every schema v1 behavior and test.

**Files:**

- Modify: `skill/scripts/verify_public_first_listen.py`
- Modify: `tests/test_verify_public_first_listen.py`

**Fiction public receipt:**

```json
{
  "schemaVersion": 2,
  "packageKind": "fiction-audiobook",
  "slug": "storm-lighthouse",
  "editionId": "first-listen-2026-08-08",
  "publicationStatus": "public-first-listen",
  "humanReadingStatus": "pending",
  "humanListeningStatus": "pending",
  "classification": "public-safe",
  "permissionToPublish": true,
  "permissionGrantedAt": "2026-08-08T12:00:00+00:00",
  "author": "Dan Fakkeldy",
  "contributor": "GPT-5.6",
  "aiGenerated": true,
  "contentLicense": "CC-BY-4.0",
  "disclosure": "This original AI-generated fiction edition is published under CC BY 4.0 as a public first-listen. Automated package and audio checks passed; human reading and listening reviews remain pending.",
  "publicGate": {
    "originalFiction": true,
    "noPrivateSource": true,
    "noLivingPersonTarget": true,
    "noLivingAuthorImitation": true,
    "coverRightsVerified": true
  },
  "coverRights": {
    "basis": "generated",
    "status": "verified",
    "coverSHA256": "sha256"
  },
  "artifacts": {
    "manuscript": {"file": "storm-lighthouse.md", "sha256": "sha256"},
    "epub": {"file": "storm-lighthouse.epub", "sha256": "sha256"},
    "alignment": {"file": "storm-lighthouse.alignment.json", "sha256": "sha256"},
    "portraitCover": {"file": "cover.png", "sha256": "sha256"}
  },
  "release": {
    "tag": "fiction-storm-lighthouse-first-listen-2026-08-08",
    "assetFile": "storm-lighthouse.m4b",
    "assetSHA256": "sha256"
  },
  "privateEvidence": {
    "fictionReceiptSHA256": "sha256",
    "voiceCastSHA256": "sha256",
    "voicePlanSHA256": "sha256",
    "echoSuccessReceiptSHA256": "sha256"
  }
}
```

- [ ] **Step 1: Add failing schema v2 fixtures without changing v1 tests**

Add `FictionPublicPackageVerifierTests` to `tests/test_verify_public_first_listen.py`. Setup creates exactly:

```text
README.md
fixture-fiction.md
fixture-fiction.epub
fixture-fiction.alignment.json
cover.png
publication.json
```

Create an external `fixture-fiction.m4b`, private `chapters/`, a valid existing fiction receipt, and a completed `voice-cast.json` whose `verifiedArtifacts` hashes and `voicePlanSHA256` match the EPUB, M4B, sidecar, and governed success receipt. Test acceptance plus rejection of:

- a local M4B, square cover, or seventh public root item;
- mismatched external M4B, cast, plan, fiction receipt, chapter, cover-rights, or artifact hashes;
- any false original/public-gate field;
- nonpending human states;
- wrong author, empty contributor, false AI flag, wrong license, or wrong disclosure.

Accept cover-rights `basis` only from `original`, `generated`, `public-domain`, `permissively-licensed`, or `explicit-permission`; require a nonempty provenance note for the last two.

The call is:

```python
verifier.verify_public_fiction_package(
    self.book_dir,
    self.release_m4b,
    self.voice_cast,
    self.fiction_receipt,
    self.chapters,
    self.echo_success_receipt,
)
```

- [ ] **Step 2: Run and observe the missing interface**

```bash
/usr/local/bin/python3 -m unittest tests.test_verify_public_first_listen -v
```

Expected: legacy v1 passes and v2 errors because the new function is absent.

- [ ] **Step 3: Preserve v1 and add strict v2 validation**

Do not relax `_CANONICAL_ARTIFACTS` or `_verify_receipt_fields`. Keep `verify_public_package(book_dir)` unchanged for schema v1 and add separate v2 constants/functions. For v2, require the exact six root files, no directories or symlinks, and no absolute or `file://` JSON values. External evidence paths are arguments and never serialized publicly.

- [ ] **Step 4: Verify local, private, and release evidence together**

Implement:

```python
def verify_public_fiction_package(
    book_dir: Path,
    release_m4b: Path,
    voice_cast: Path,
    fiction_receipt: Path,
    chapters_dir: Path,
    echo_success_receipt: Path,
) -> None:
```

It must:

1. validate schema v2 and exact four local artifact records;
2. `unzip -t` the EPUB, parse nonempty alignment JSON, and ffprobe the external M4B for positive duration and at least one chapter;
3. require the release filename and hash to match that M4B;
4. require the cast hash and `voicePlanSHA256` to match private evidence, and require cast `verifiedArtifacts` hashes to match the public EPUB, public sidecar, external M4B, and supplied Echo success receipt;
5. require the Echo success receipt file hash, filenames, `sourceEPUBSHA256`, `audiobookSHA256`, `sidecarSHA256`, and `voicePlanSHA256` to match the public artifacts, external M4B, and completed cast;
6. call `verify_fiction_receipt(chapters_dir, fiction_receipt)` and match its file hash;
7. require all five `publicGate` values true and cover-rights hash equal the public cover;
8. require the exact disclosure in `publication.json` and README.

Use a package/direct-script import fallback:

```python
try:
    from .fiction_production_qc import verify_fiction_receipt
except ImportError:
    from fiction_production_qc import verify_fiction_receipt
```

- [ ] **Step 5: Extend the CLI without breaking old commands**

Keep `verify_public_first_listen.py BOOK_DIRECTORY` valid. Add:

```text
verify_public_first_listen.py BOOK_DIRECTORY --release-m4b PATH --voice-cast PATH --fiction-receipt PATH --chapters-dir PATH --echo-success-receipt PATH
```

Require zero extra evidence arguments for v1 or all five for v2. Reject partial forms with exit 64; verification failures return 1.

- [ ] **Step 6: Run and commit**

```bash
/usr/local/bin/python3 -m unittest tests.test_verify_public_first_listen tests.test_claude_platform_public_series -v
git add skill/scripts/verify_public_first_listen.py tests/test_verify_public_first_listen.py
git commit -m "feat: verify release-backed public fiction"
```

Expected: legacy packages remain valid and new fiction packages verify without an M4B in Git.

---

### Task 5: Write the standalone express skill and references

With deterministic support in place, add the skill that owns intake, autonomous story decisions, production order, failure handling, private delivery, and conditional public publication.

**Files:**

- Create: `skills/fiction-audiobook/SKILL.md`
- Create: `skills/fiction-audiobook/agents/openai.yaml`
- Create: `skills/fiction-audiobook/references/express-fiction-craft.md`
- Create: `skills/fiction-audiobook/references/public-fiction-gate.md`
- Create: `tests/test_fiction_audiobook_contract.py`
- Modify: `tools/validate_skills.py`
- Modify: `AGENTS.md`
- Modify: `README.md`

- [ ] **Step 1: Write the failing skill contract**

Create `tests/test_fiction_audiobook_contract.py` with:

```python
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]


class FictionAudiobookContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = ROOT / "skills/fiction-audiobook"
        self.skill = (self.root / "SKILL.md").read_text(encoding="utf-8")

    def test_plain_premise_is_zero_intake_and_grilling_is_one_batch(self) -> None:
        self.assertIn("ask no questions", self.skill)
        self.assertIn("one batched intake", self.skill)
        self.assertIn("grill me", self.skill)
        self.assertIn("Do not ask follow-up questions", self.skill)

    def test_express_lane_never_invokes_long_fiction_development(self) -> None:
        self.assertIn("Do not invoke `fiction-book-development`", self.skill)
        self.assertNotIn("Use $fiction-book-development", self.skill)
        self.assertNotIn("scene-cards/", self.skill)
        self.assertNotIn("vertical slice", self.skill.casefold())

    def test_skill_selects_the_shortest_sufficient_form(self) -> None:
        for marker in (
            "18k–30k", "30k–45k", "50k–80k", "80k–110k",
            "one-sentence rationale", "brief.md",
        ):
            self.assertIn(marker, self.skill)

    def test_ensemble_delivery_and_publication_contracts_are_explicit(self) -> None:
        for marker in (
            "three to five", "af_heart", "--chapter-voice",
            "fiction-voice-preferences.json", "stage_echo_delivery.py",
            "_production/", "public first-listen", "GitHub Release",
            "ready pull request", "Do not auto-merge", "humanListeningStatus",
        ):
            self.assertIn(marker, self.skill)

    def test_every_required_support_file_exists_and_is_linked(self) -> None:
        for relative in (
            "references/express-fiction-craft.md",
            "references/public-fiction-gate.md",
            "scripts/fiction_voice_preferences.py",
            "scripts/stage_echo_delivery.py",
            "agents/openai.yaml",
        ):
            self.assertTrue((self.root / relative).is_file())
            if relative != "agents/openai.yaml":
                self.assertIn(relative, self.skill)


if __name__ == "__main__":
    unittest.main()
```

Add ordering assertions that the three revision passes are story → character/continuity → ear/prose; build is before casting; casting before narration; narration verification before iCloud promotion; iCloud delivery before GitHub mutation; and public-gate failure skips all GitHub commands.

- [ ] **Step 2: Run and observe failure**

```bash
/usr/local/bin/python3 -m unittest tests.test_fiction_audiobook_contract -v
```

Expected: ERROR because the skill files do not exist.

- [ ] **Step 3: Write a lean `SKILL.md` with the autonomous state machine**

Use frontmatter:

```yaml
---
name: fiction-audiobook
description: >-
  Use when the user says “make me a fiction audiobook about X,” wants a premise turned into a novel or novella they can listen to, or asks for an Echo-ready fictional book. Takes one sentence through autonomous story development, revision, EPUB/M4B narration, Echo-clean iCloud delivery, and public-first publication; intake occurs only when the user explicitly asks to be grilled.
---
```

Keep `SKILL.md` under 300 lines. Define this exact order:

1. classify a full listening-package request and reject manuscript-only routing;
2. perform zero intake unless explicit grilling language requests one batch covering genre/mood, must-have characters or setting, exclusions, POV/distance, ending shape, and voice/casting preferences; never ask a follow-up;
3. choose the shortest sufficient form from short novella 18k–30k, novella 30k–45k, novel 50k–80k, or long novel 80k–110k; announce working title, angle, form, chapters, words, and runtime; then record the rationale in `.build/fiction-audiobooks/<slug>/brief.md`;
4. write the compact story bible and causal outline, then draft sequentially with one rolling continuity file;
5. run the three combined revision passes and bind the unchanged fiction production receipt;
6. generate three paired-cover candidates, select one, and build EPUB/combined Markdown with `--fiction-receipt`;
7. load preferences, write and validate a three-to-five-voice cast after EPUB bytes freeze, keep each recurring role on one voice, reserve zero-to-two suitable short chapters for untried voices, then render with `ECHO_RUN_LANE=fiction-audiobook` and complete `--chapter-voice` mappings;
8. run Echo's `verify-delivery`, `verify-sidecar`, audit, JSON, and `ffprobe` checks before recording use;
9. prepare the six `_production` directories and atomically stage `~/Library/Mobile Documents/com~apple~CloudDocs/Books/<Title>/` with exactly the four loadable files plus `_production/`;
10. evaluate the public-fiction gate; on pass, stage/verify the M4B-free repository package, push a public branch, open a ready PR, and create the release; on fail, record the reason and make no GitHub mutation;
11. report delivery/publication/merge/human states separately;
12. apply narrow redo rules for story, voice, cover, and blacklist feedback.

The skill must say that a normal public-safe fiction-audiobook request supplies standing publication authorization, while `fiction-production-receipt.json` stays private and cannot authorize publication.

- [ ] **Step 4: Write the compact craft reference**

`references/express-fiction-craft.md` contains only:

- the compact `brief.md`, `story-bible.md`, `outline.md`, rolling/final continuity, decision, revision, and QC artifacts;
- character-as-pressure and causal-turn requirements;
- observable prose controls and the ban on imitating living authors;
- sequential lead-writer drafting;
- the three combined revision passes, final front-to-back read, promise/payoff reconciliation, and read-aloud check;
- exact fiction-receipt evidence paths and gate fields;
- failure behavior when story, continuity, or prose cannot pass.

Do not copy the long skill's ten-step workflow, vertical slice, scene-card directory, approval gates, or eight separate revision passes.

- [ ] **Step 5: Write the public gate and publication runbook**

`references/public-fiction-gate.md` defines Task 4's exact schema v2 receipt and original/public-safe checks. It instructs the agent to stage outside `books/`, run:

```bash
/usr/local/bin/python3 skill/scripts/verify_public_first_listen.py "$PUBLIC_STAGE" \
  --release-m4b "$AUDIOBOOK" \
  --voice-cast "$VOICE_CAST" \
  --fiction-receipt "$RUN_ROOT/research/fiction-production-receipt.json" \
  --chapters-dir "$RUN_ROOT/chapters" \
  --echo-success-receipt "$ECHO_SUCCESS_RECEIPT"
```

Only after success, copy the six public files into `books/<slug>/`, update the README catalogue, and publish in this order:

```bash
git add "books/$SLUG" README.md
git commit -m "book: publish $TITLE first listen"
git push -u origin HEAD
gh pr create --fill --head "$(git branch --show-current)"
PUBLIC_COMMIT=$(git rev-parse HEAD)
gh release create "$RELEASE_TAG" "$AUDIOBOOK#$SLUG.m4b" \
  --target "$PUBLIC_COMMIT" \
  --title "$TITLE — public first-listen" \
  --notes-file "$RUN_ROOT/research/release-notes.md"
```

Require a ready PR, never `--draft`, and never merge. Then run:

```bash
gh release view "$RELEASE_TAG" --json tagName,targetCommitish,assets,url
```

Compare asset name and digest when GitHub supplies one. A GitHub failure preserves successful iCloud delivery and the publication stage, and is reported as retryable.

- [ ] **Step 6: Add metadata and route documentation**

Create `agents/openai.yaml`:

```yaml
interface:
  display_name: "Fiction Audiobook"
  short_description: "Turn one premise into an Echo-ready fiction book"
  default_prompt: "Use $fiction-audiobook to turn my premise into a complete narrated fiction package."
```

Update `AGENTS.md` so full fictional listening packages use `skills/fiction-audiobook/`, while planning/drafting/revision-only requests remain in `fiction-book-development`. Clarify that the express trigger supplies workflow publication authorization subject to its fail-closed gate.

Add a README paragraph covering zero-intake default, optional grilling, multi-voice Echo, flat iCloud delivery, and public-first/private-fallback behavior.

- [ ] **Step 7: Register the skill in `validate_skills.py`**

Add:

```python
validate_skill("skills/fiction-audiobook", "fiction-audiobook")
```

Require stable markers across the skill, references, scripts, and YAML: `ask no questions`, `fiction-audiobooks`, `three to five`, `af_heart`, `_production/`, `public first-listen`, `private fallback`, `$fiction-audiobook`, and both helper names.

- [ ] **Step 8: Run and commit**

```bash
/usr/local/bin/python3 -m unittest tests.test_fiction_audiobook_contract -v
/usr/local/bin/python3 tools/validate_skills.py
git diff --check
git add skills/fiction-audiobook tests/test_fiction_audiobook_contract.py tools/validate_skills.py AGENTS.md README.md
git commit -m "feat: add express fiction audiobook skill"
```

Expected: contract and validator pass, and the skill contains no unfinished marker, implementation stub, or invocation of the long workflow.

---

### Task 6: Add one production integration fixture

Unit tests prove each seam. Add one compact fixture proving the existing fiction receipt, builder, paired covers, voice cast, delivery stager, and public verifier agree on filenames and hashes.

**Files:**

- Create: `tests/test_fiction_audiobook_integration.py`

- [ ] **Step 1: Build the fixture book**

Create three `ch*.md` files and the five evidence artifacts required by `fiction_production_qc.py`, write a valid private receipt, and call:

```python
build_book.build(
    chapters,
    run_root / "dist",
    "Fixture Ensemble",
    "Dan Fakkeldy",
    "",
    "fixture-ensemble",
    cover=portrait_cover,
    m4b_cover=square_cover,
    contributor="GPT-5.6",
    fiction_receipt=fiction_receipt,
)
```

Create real RGB 1600×2560 and 2400×2400 PNGs with Pillow so the receipt-free private paired-cover path is exercised. Assert EPUB and combined Markdown exist and the EPUB includes the portrait cover.

- [ ] **Step 2: Bind and validate a three-role cast**

Build a complete three-chapter cast using `bf_emma`, `am_michael`, and `af_bella`, compute its plan through `echo_voice_plan.voice_plan`, and call `validate_cast`. Write a fake final M4B, sidecar, and governed success receipt whose EPUB, M4B, sidecar, and plan names and hashes match. Call `record_use` with all four evidence paths, assert the cast gains exact `verifiedArtifacts`, and assert all three chapter uses are persisted once.

- [ ] **Step 3: Stage private delivery and the M4B-free public package**

Prepare exact production directories with cast and success receipt under `narration/`, revision and fiction receipts under `checks/`, story files under `source/`, and selected pair under `covers/`. Call `stage_delivery(..., apply=True)` and assert only the four loadable files and `_production/` appear at the title root.

Create the exact six public files and schema v2 receipt in a separate stage. Mock only `ffprobe` to return positive duration and one chapter; use the real EPUB for `unzip -t`. Call `verify_public_fiction_package` with the Echo success receipt and assert the public stage has no `.m4b`, square cover, or private path text.

- [ ] **Step 4: Run the integration and components**

```bash
/usr/local/bin/python3 -m unittest tests.test_fiction_audiobook_integration tests.test_fiction_production_gate tests.test_fiction_voice_preferences tests.test_stage_echo_delivery tests.test_verify_public_first_listen -v
```

Expected: integration and component tests pass.

- [ ] **Step 5: Commit**

```bash
git add tests/test_fiction_audiobook_integration.py
git commit -m "test: cover fiction audiobook production flow"
```

---

### Task 7: Verify, forward-test, and publish the implementation

This is repository implementation publication, not a sample book publication. Do not create a book release in this task.

**Files:**

- Modify only if a failure reveals a real defect in Tasks 1–6.
- Do not create durable forward-test transcripts unless they expose a contract that needs a repository test.

- [ ] **Step 1: Run focused validation**

```bash
/usr/local/bin/python3 -m unittest tests.test_echo_narration_contract tests.test_echo_narration_runtime tests.test_echo_voice_plan tests.test_fiction_voice_preferences tests.test_stage_echo_delivery tests.test_verify_public_first_listen tests.test_fiction_audiobook_contract tests.test_fiction_audiobook_integration -v
```

Expected: all focused tests pass. Echo runtime may take several minutes.

- [ ] **Step 2: Run complete repository checks**

```bash
/usr/local/bin/python3 -m unittest discover -s tests -v
/usr/local/bin/python3 tools/validate_skills.py
git diff --check
git status --short --branch
```

Expected: full suite passes with documented skips, validator prints `validate_skills: clean`, diff check is silent, and all durable work is committed.

- [ ] **Step 3: Forward-test decisions with fresh agents**

Give five fresh agents the completed skill plus one request each, asking for workflow decisions without writing or publishing a book:

1. `Make me a fiction audiobook about a lighthouse that appears only during storms.`
2. `Grill me, then make me a fiction audiobook about a retired courier who can deliver letters to yesterday.`
3. `Make me a private fiction audiobook about a family story from my attached notes.`
4. `Make me a fiction audiobook about a moon colony. The selected Echo voice is unavailable after the EPUB is frozen.`
5. `Redo my latest fiction audiobook, but the iCloud title folder now contains my own notes.m4a.`

Require, respectively: zero intake and autonomous length choice; one six-topic batch and no follow-up; private delivery with zero GitHub work; explicit recast/new plan identity without prose rebuild; and preserved staging plus blocked promotion naming `notes.m4a`.

If an agent invents a long-workflow checkpoint, line-level voices, extra root audio, publication after a failed gate, human acceptance, or auto-merge, fix the enabling instruction and add a regression assertion.

- [ ] **Step 4: Review the complete branch**

Use `superpowers:requesting-code-review` on the complete diff. Resolve correctness or contract findings, rerun affected tests, then rerun `tools/validate_skills.py` and `git diff --check`.

- [ ] **Step 5: Push and open a ready implementation PR**

```bash
git status --short --branch
git push -u origin codex/fiction-audiobook-express
gh pr create --fill --head codex/fiction-audiobook-express
```

Confirm the PR is ready, not draft. Do not merge it. Report local verification, hosted CI, PR state, and installation state separately.

- [ ] **Step 6: Activate only after merge into the canonical checkout**

After merge and update of `/Users/dfakkeldy/Developer/explainer-audiobooks`, create these links only if their destinations are absent:

```text
/Users/dfakkeldy/.codex/skills/fiction-audiobook -> /Users/dfakkeldy/Developer/explainer-audiobooks/skills/fiction-audiobook
/Users/dfakkeldy/.agents/skills/fiction-audiobook -> /Users/dfakkeldy/Developer/explainer-audiobooks/skills/fiction-audiobook
```

If either destination exists and is not that exact symlink, stop and report the conflict. Verify both resolve to a `SKILL.md` whose frontmatter name is `fiction-audiobook`. Never point them at the task worktree.

---

## Plan Self-Review

- The plan covers zero-intake default, one opt-in grilling batch, premise-selected length, independent express workflow, one lead writer, compact receipts, three revision passes, three-to-five chapter voices, durable preferences, the fiction Echo run root, atomic flat iCloud delivery, public-by-default gating, M4B release publication, ready PR/no merge, private fallback, redo rules, and separate state reporting.
- Every persistent format has a concrete schema and deterministic validator.
- Existing schema v1 public packages and the default nonfiction Echo lane stay backward compatible.
- The public receipt carries hashes and public metadata only; private paths and M4B bytes remain outside Git history.
- There are no unspecified implementation stubs, optional future architecture tasks, or line-level Echo changes hidden in scope.
- Durable skill activation waits for merge and uses the canonical checkout, so repository implementation and installation are reported separately.
