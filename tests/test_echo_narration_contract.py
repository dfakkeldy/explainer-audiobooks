from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
NARRATING = ROOT / "skills" / "echo-narration" / "references" / "narrating.md"
SEMANTIC_REFERENCE = ROOT / "skill" / "references" / "semantic-voice-casting.md"
NARRATE_WRAPPER = (
    ROOT / "skills" / "echo-narration" / "scripts" / "echo_pronunciation_narrate.sh"
)
PREFLIGHT = (
    ROOT / "skills" / "echo-narration" / "scripts" / "echo_pronunciation_preflight.sh"
)
LEASE_HELPER = (
    ROOT / "skills" / "echo-narration" / "scripts" / "echo_pronunciation_lease.py"
)
COVER_ART = ROOT / "skill" / "references" / "cover-art.md"


class EchoNarrationContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.narrating = NARRATING.read_text(encoding="utf-8")
        self.narrate_wrapper = NARRATE_WRAPPER.read_text(encoding="utf-8")
        self.preflight = PREFLIGHT.read_text(encoding="utf-8")
        self.lease_helper = LEASE_HELPER.read_text(encoding="utf-8")
        self.cover_art = COVER_ART.read_text(encoding="utf-8")

    @staticmethod
    def normalized(text: str) -> str:
        return " ".join(text.split())

    def test_source_bound_runbook_supports_semantic_and_character_casts(self) -> None:
        normalized = self.normalized(self.narrating)
        for marker in (
            "Nonfiction semantic cast",
            "Fiction character cast",
            "semantic_voice_cast.py",
            "fiction_voice_preferences.py",
            "export-blocks",
            "resolve-voice-plan",
            "--voice-plan",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, normalized)
        self.assertIn("Echo alone decides block existence", normalized)

    def test_block_handoffs_reject_invalid_casts_before_the_wrapper(self) -> None:
        semantic_reference = SEMANTIC_REFERENCE.read_text(encoding="utf-8")
        self.assertIn("load_semantic_voice_arguments()", semantic_reference)
        self.assertIn("load_fiction_voice_arguments()", self.narrating)
        self.assertGreaterEqual(self.narrating.count("must be --voice-plan"), 2)
        self.assertIsNone(re.search(r"\beval\b", self.narrating))
        self.assertIsNone(re.search(r"\beval\b", semantic_reference))

    def test_semantic_block_handoff_stops_before_wrapper_on_invalid_cast(self) -> None:
        """A rejected semantic cast must not invoke the governed wrapper."""
        semantic_reference = SEMANTIC_REFERENCE.read_text(encoding="utf-8")
        marker = "Forward only the validator's NUL-delimited argv0 result."
        self.assertIn(marker, semantic_reference)
        handoff = semantic_reference.split(marker, 1)[1]
        handoff = handoff.split("```bash\n", 1)[1].split("```", 1)[0].strip()

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw).resolve()
            run_root = root / "run"
            narration = run_root / "_production" / "narration"
            research = run_root / "research"
            dist = run_root / "dist"
            for directory in (narration, research, dist):
                directory.mkdir(parents=True)
            epub = (dist / "fixture.epub").resolve()
            inventory = (research / "echo-block-inventory-fixture.json").resolve()
            voice_plan = (narration / "echo-voice-plan.json").resolve()
            voice_cast = (narration / "semantic-voice-cast.json").resolve()
            wrapper = (root / "fake-narration-wrapper.sh").resolve()
            wrapper_log = root / "wrapper-called.log"
            epub.write_bytes(b"frozen fixture EPUB")
            epub_hash = hashlib.sha256(epub.read_bytes()).hexdigest()
            inventory.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "source": {"epubSHA256": epub_hash},
                        "blocks": [
                            {
                                "id": "s0-b0",
                                "kind": [],
                                "text": "Malformed kind.",
                                "chapterIndex": 0,
                                "sequenceIndex": 0,
                                "wordCount": 2,
                            }
                        ],
                    },
                    sort_keys=True,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            voice_plan.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "source": {"epubSHA256": epub_hash},
                        "defaultSpeakerID": "guide",
                        "speakers": [
                            {"id": "guide", "voiceID": "am_michael"},
                            {"id": "memory", "voiceID": "bf_emma"},
                        ],
                        "assignments": [{"speakerID": "memory", "blocks": ["s0-b0"]}],
                    },
                    sort_keys=True,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            voice_cast.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "narrationMode": "semantic-block",
                        "source": {
                            "epubFileName": epub.name,
                            "epubSHA256": epub_hash,
                            "inventoryFileName": inventory.name,
                            "inventorySHA256": hashlib.sha256(inventory.read_bytes()).hexdigest(),
                        },
                        "defaultRoleID": "guide",
                        "roles": [
                            {"roleID": "guide", "voiceID": "am_michael"},
                            {"roleID": "memory", "voiceID": "bf_emma"},
                        ],
                        "groups": [
                            {"groupID": "memory-001", "roleID": "memory", "blocks": ["s0-b0"]}
                        ],
                        "authoredVoicePlan": {
                            "fileName": voice_plan.name,
                            "sha256": hashlib.sha256(voice_plan.read_bytes()).hexdigest(),
                        },
                        "singleVoiceWaiver": None,
                    },
                    sort_keys=True,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            wrapper.write_text(
                "#!/bin/bash\n"
                "set -euo pipefail\n"
                "printf '%s\\n' \"$@\" >\"$WRAPPER_LOG\"\n"
                "mkdir -p -- \"$RUN_ROOT/research\"\n"
                "touch -- \"$RUN_ROOT/research/echo-render-inputs-unexpected.env\"\n"
                "mkdir -p -- \"$RUN_ROOT/audio-work-unexpected\"\n"
                "touch -- \"$RUN_ROOT/narration-unexpected.sqlite\"\n",
                encoding="utf-8",
            )
            wrapper.chmod(0o700)

            environment = os.environ.copy()
            environment.update(
                {
                    "EXPLAINER_ROOT": str(ROOT),
                    "SEMANTIC_CAST": str(voice_cast),
                    "INVENTORY": str(inventory),
                    "VOICE_PLAN": str(voice_plan),
                    "EPUB": str(epub),
                    "NARRATION_SCRIPT": str(wrapper),
                    "RUN_ROOT": str(run_root),
                    "WRAPPER_LOG": str(wrapper_log),
                    "TMPDIR": str(root),
                }
            )
            result = subprocess.run(
                ["/bin/bash", "-c", "set -o pipefail\n" + handoff],
                cwd=ROOT,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(65, result.returncode, result.stderr)
            self.assertEqual(
                "semantic voice cast: inventory block 0 has an invalid kind\n",
                result.stderr,
            )
            self.assertFalse(wrapper_log.exists())
            self.assertFalse(
                (run_root / "research" / "echo-render-inputs-unexpected.env").exists()
            )
            self.assertFalse((run_root / "audio-work-unexpected").exists())
            self.assertFalse((run_root / "narration-unexpected.sqlite").exists())
            self.assertEqual([], list(root.glob("echo-semantic-voice-arguments.*")))

    def test_builds_and_preflights_the_exact_release_cli(self) -> None:
        combined = self.normalized(self.narrating + "\n" + self.preflight)
        for marker in (
            "APPROVED_ECHO_PRONUNCIATION_SHA",
            "ECHO_SOURCE_SHA",
            "ECHO_CLI_SHA256",
            "EPUB_SHA256",
            "RUN_ROOT",
            "--no-pronunciation-review",
            "Stop immediately",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, combined)

    def test_ordinary_narration_has_no_checkout_or_build_boundary(self) -> None:
        ordinary_source = self.preflight + self.narrate_wrapper
        forbidden = (
            "ECHO_REPO",
            ".build/cli",
            "xcode-build-gate.sh",
            "xcodebuild",
            "make",
            "git ",
            "/usr/bin/git",
        )
        for marker in forbidden:
            with self.subTest(marker=marker):
                self.assertNotIn(marker, ordinary_source)
        for required in (
            "echo_installed_renderer.py",
            "resolve-new",
            "resolve-resume",
            "ECHO_RENDERER_BUILD_ROOT",
            'case "$renderer_key" in',
            "installed renderer attestation failed",
        ):
            with self.subTest(required=required):
                self.assertIn(required, ordinary_source)
        self.assertNotIn("eval", ordinary_source)

    def test_renderer_identity_comes_from_the_installed_artifacts(self) -> None:
        """The immutable installed package is the operational fingerprint."""
        normalized_narrating = self.normalized(self.narrating)
        for marker in (
            "ECHO_CLI_SHA256",
            "ECHO_RESOURCES_SHA256",
            "ECHO_RENDERER_MANIFEST_SHA256",
            "APPROVED_ECHO_INSTALLER_SHA",
            "APPROVED_ECHO_PRONUNCIATION_SHA",
        ):
            with self.subTest(marker=marker, doc="narrating.md"):
                self.assertIn(marker, normalized_narrating)

        normalized_preflight = self.normalized(self.preflight)
        for marker in (
            "ECHO_RENDERER_BUILD_ROOT",
            "ECHO_RENDERER_MANIFEST_SHA256",
            "ECHO_CLI_SHA256",
            "ECHO_RESOURCES_SHA256",
        ):
            with self.subTest(marker=marker, doc="preflight"):
                self.assertIn(marker, normalized_preflight)

    def test_operational_narration_requires_an_explicit_approved_source(self) -> None:
        normalized_preflight = self.normalized(self.preflight)
        self.assertIn(
            "must exactly equal installed source",
            normalized_preflight,
        )
        self.assertIn(
            "APPROVED_ECHO_PRONUNCIATION_SHA is required",
            self.preflight,
        )
        self.assertNotIn("APPROVED_ECHO_PRONUNCIATION_SHA=unpinned", self.preflight)

    def test_run_id_is_derived_in_exactly_one_place(self) -> None:
        """The preflight and the attestation both need RUN_ID. Restating the
        formula in both let them drift the moment the source leg changed, which
        broke every render with 'sealed run paths are not derived from the
        attested inputs'. Both must call the shared helpers."""
        preflight = self.preflight
        self.assertIn("echo_pronunciation_source_id()", preflight)
        self.assertIn("echo_pronunciation_run_id()", preflight)
        # The literal formula must not appear anywhere: that is the duplication.
        self.assertNotIn("PACKAGE_SHA256:0:12", preflight)
        # Both call sites go through the helper.
        self.assertGreaterEqual(
            preflight.count("$(echo_pronunciation_run_id"), 2,
            "preflight and attestation must both derive RUN_ID via the helper",
        )
        self.assertGreaterEqual(
            preflight.count("$(echo_pronunciation_source_id"), 2,
            "preflight and attestation must both derive the source id via the helper",
        )

    def test_governed_receipts_bind_the_complete_installed_renderer_identity(self) -> None:
        for marker in (
            "renderer_schema_version",
            "renderer_root",
            "renderer_build_root",
            "installer_source_sha",
            "renderer_manifest_sha256",
            "model_policy_revision",
            "model_expected_byte_count",
            "model_bytes_attested=false",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.preflight)

        for marker in (
            "--renderer-root",
            "--renderer-build-root",
            "--installer-source-sha",
            "--echo-source-sha",
            "--renderer-manifest-sha256",
            "--echo-cli-sha256",
            "--echo-resources-sha256",
            "--echo-render-version",
            "--model-policy-revision",
            "--model-expected-byte-count",
            "--model-bytes-attested",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.narrate_wrapper)

    def test_attestation_fails_closed_on_mid_render_drift(self) -> None:
        """The immutable package is re-attested before and after rendering."""
        normalized_preflight = self.normalized(self.preflight)
        self.assertIn("echo_installed_renderer.py", normalized_preflight)
        self.assertIn('"$resolver" attest', normalized_preflight)
        self.assertIn('--source-sha "$ECHO_SOURCE_SHA"', normalized_preflight)
        self.assertIn("installed renderer attestation failed", normalized_preflight)

        self.assertIn("echo_pronunciation_preflight.sh", self.narrate_wrapper)
        self.assertIn('"$CLI" narrate', self.narrate_wrapper)
        self.assertIn('ECHO_RESOURCE_DIR="$ECHO_RESOURCE_DIR"', self.narrate_wrapper)
        self.assertNotIn('"$CLI" narrate', self.narrating)
        self.assertIn("Never invoke a DerivedData `Debug/echo-cli`", self.narrating)

        for stale_debug_discovery in ("xcodebuild build", "TARGET_BUILD_DIR"):
            with self.subTest(stale=stale_debug_discovery):
                self.assertNotIn(stale_debug_discovery, self.narrating)

        self.assertNotIn("cd /Users/dfakkeldy/Developer/Echo", self.narrating)

    def test_pronunciation_review_defaults_on_with_bounded_render_concurrency(
        self,
    ) -> None:
        normalized = self.normalized(self.narrating)
        self.assertIn("Pronunciation review is on by default", normalized)
        self.assertIn("Do not pass `--no-pronunciation-review`", normalized)

        self.assertIn("--jobs 1", self.narrate_wrapper)
        self.assertIn("--threads 2", self.narrate_wrapper)

    def test_wrapper_binds_selected_square_cover_to_immutable_render(self) -> None:
        for marker in (
            "M4B_COVER",
            "M4B_COVER_SHA256",
            "cover_receipts.py",
            "cover-selection.json",
            "receipt-free-private",
            "paired-receipt",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.preflight)

        self.assertIn('--cover "$M4B_COVER"', self.narrate_wrapper)
        self.assertIn("M4B_COVER_SHA256", self.preflight)

    def test_resume_examples_pass_the_exact_canonical_state_receipt(self) -> None:
        normalized = self.normalized(self.narrating)
        self.assertGreaterEqual(
            normalized.count('--resume --resume-state "$RESUME_STATE"'),
            2,
        )
        self.assertIn(
            'RESUME_STATE="$RUN_ROOT/research/echo-resume-state-$RUN_ID.json"',
            self.narrating,
        )
        self.assertNotIn(
            "echo_pronunciation_narrate.sh\" --resume\n",
            self.narrating,
        )

    def test_partial_resume_example_derives_every_variable_and_executes(self) -> None:
        section = self.narrating.split(
            "To render exactly the next chapter", 1
        )[1]
        block = section.split("```bash", 1)[1].split("```", 1)[0].strip()
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            run_root = root / "run"
            research = run_root / "research"
            research.mkdir(parents=True)
            run_id = "-".join(
                [
                    "1" * 12,
                    "2" * 12,
                    "3" * 12,
                    "4" * 12,
                    "5" * 40,
                    "am_michael",
                ]
            )
            (research / "echo-render-current-attempt.json").write_text(
                json.dumps({"runID": run_id}),
                encoding="utf-8",
            )
            (research / f"echo-resume-state-{run_id}.json").write_text(
                "{}\n",
                encoding="utf-8",
            )
            log = root / "arguments.log"
            wrapper = root / "narrate"
            wrapper.write_text(
                "#!/usr/bin/env bash\n"
                'printf "%s\\n" "$@" >"$ARGUMENT_LOG"\n'
                "exit 2\n",
                encoding="utf-8",
            )
            wrapper.chmod(0o755)
            environment = os.environ.copy()
            environment.update(
                {
                    "RUN_ROOT": str(run_root),
                    "NARRATION_SCRIPT": str(wrapper),
                    "ARGUMENT_LOG": str(log),
                }
            )

            result = subprocess.run(
                ["bash", "-c", f"set -u\n{block}"],
                env=environment,
                capture_output=True,
                text=True,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(
                [
                    "--resume",
                    "--resume-state",
                    str(research / f"echo-resume-state-{run_id}.json"),
                    "--max-chapters",
                    "1",
                ],
                log.read_text(encoding="utf-8").splitlines(),
            )

    def test_operating_commands_use_the_required_python_interpreter(self) -> None:
        validator = (
            '/usr/local/bin/python3 "$SCRIPT_DIR/validate_pronunciation_audit.py"'
        )
        self.assertEqual(2, self.narrate_wrapper.count(validator))
        self.assertIn(
            '/usr/local/bin/python3 "$EXPLAINER_ROOT/skills/echo-narration/'
            'scripts/validate_pronunciation_audit.py"',
            self.narrating,
        )
        self.assertIn(
            '/usr/local/bin/python3 "$STATE_HELPER" \\\n  verify-delivery',
            self.narrating,
        )
        self.assertNotIn(
            '"$EXPLAINER_ROOT/skills/echo-narration/scripts/'
            'echo_pronunciation_state.py" \\\n  verify-delivery',
            self.narrating,
        )

    def test_block_review_media_has_an_internal_path_and_exact_attempt_guard(
        self,
    ) -> None:
        """A block reel is governed review evidence, never delivery media."""
        for marker in (
            'REEL="$RUN_ROOT/research/listening/$RUN_ID/$ATTEMPT_ID/'
            '$SLUG.pronunciation-reel.m4b"',
            "LISTENING_ATTEMPT_ROOT",
            "assert_block_attempt_contents",
            "block attempt contains prohibited review media",
            '--audiobook "$OUTPUT"',
            '--reel "$REEL"',
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.narrate_wrapper)

    def test_reference_derives_pipeline_root_from_installed_narration_script(self) -> None:
        self.assertNotIn("git rev-parse --show-toplevel", self.narrating)
        for marker in (
            "NARRATION_SCRIPT",
            "NARRATION_SCRIPT_DIR",
            "PIPELINE_ROOT",
            'export RUN_ROOT="$PIPELINE_ROOT/.build/custom-learning-audiobooks/$SLUG"',
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.narrating)

    def test_wrapper_holds_fd_backed_resource_leases_through_narration(self) -> None:
        for marker in (
            "ECHO_PRONUNCIATION_LEASE_ROOT",
            "echo_pronunciation_canonical_lease_root",
            "echo_pronunciation_lease.py",
            "trap release_owner_metadata EXIT",
            "--recover-stale-lock",
            "active narration lock",
            "remote narration lock",
            "malformed narration lock",
            'wait "$NARRATE_PID"',
            "--leased-preflight",
            "ECHO_RENDERER_BUILD_ROOT",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.narrate_wrapper)
        self.assertIn("--assert-held", self.preflight)

        for marker in (
            "fcntl.flock",
            "fcntl.LOCK_EX | fcntl.LOCK_NB",
            "pass_fds=tuple(sorted(set(capability.values())))",
            "hashlib.sha256",
            "Path(resource).resolve()",
            "ECHO_PRONUNCIATION_LEASE_CAPABILITY",
            "validate_capability",
        ):
            self.assertIn(marker, self.lease_helper)

        self.assertIn("governed Echo narration wrapper", self.cover_art)
        self.assertIn(
            "Do not bypass the wrapper with a direct CLI command",
            self.normalized(self.narrating),
        )

    def test_resume_requires_an_immutable_source_renderer_and_capture_set(self) -> None:
        normalized = self.normalized(self.narrating)
        for marker in (
            "fresh `--work-dir` and `--db`",
            "source EPUB changes",
            "Release CLI binary or Echo source revision changes",
            "exact approved/source revision",
            "exact Release render version",
            "echo-resume-state-$RUN_ID.json",
            "SHA-256",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, normalized)

    def test_governed_partial_probe_is_resumable_but_not_publishable(self) -> None:
        normalized_narrating = self.normalized(self.narrating)

        for marker in (
            "--max-chapters 1",
            "exit 2",
            "partial",
            '--resume --resume-state "$RESUME_STATE" --max-chapters 1',
            "no accepted M4B",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, normalized_narrating)

        self.assertIn("real-book pronunciation probe", normalized_narrating)
        self.assertIn("--max-chapters", self.narrate_wrapper)

    def test_review_artifacts_are_automatic_and_part_of_package_qc(self) -> None:
        normalized = self.normalized(self.narrating)
        for marker in (
            "<slug>.pronunciation-audit.json",
            "<slug>.pronunciation-reel.m4b",
            '"$CLI" verify-sidecar',
            '--epub "$DIST/$SLUG.epub"',
            '--audio "$AUDIOBOOK"',
            '--sidecar "$SIDECAR"',
            "schema version is `6`",
            "coverage",
            "watch counts",
            "including zero counts",
            "human listening remains explicitly pending",
            "validate_pronunciation_audit.py",
            "echo-render-success-$RUN_ID-$ATTEMPT_ID.json",
            "echo-render-current-attempt.json",
            "echo-render-current-accepted.json",
            "echo-renders/$RUN_ID/$ATTEMPT_ID",
            "verify-delivery",
            "--state-receipt",
            "resumeStateFileName",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, normalized)

        self.assertNotIn('mv "$DIST/$SLUG.covered.m4b"', self.narrating)

        for marker in (
            "pronunciation audit",
            "pronunciation reel",
            "human listening",
        ):
            with self.subTest(report_marker=marker):
                self.assertIn(marker, self.narrating.casefold())

    def test_operating_docs_require_the_installed_renderer_contract(self) -> None:
        """The reference must send operators to the versioned store, not a checkout.

        These are deliberately documentation assertions: the shell wrappers
        already enforce the boundary, but an operator following stale prose can
        still choose an unsafe or non-reproducible recovery path.
        """
        normalized = self.normalized(self.narrating)
        for marker in (
            "~/Library/Application Support/Echo/Renderers/",
            "<40-hex source SHA>",
            "<64-hex manifest SHA>",
            "approved-renderer.json",
            "APPROVED_ECHO_INSTALLER_SHA",
            "APPROVED_ECHO_PRONUNCIATION_SHA",
            "exactly 40 lowercase hexadecimal characters",
            "resolve-new",
            "resolve-resume",
            "sealed resume-state receipt",
            "python3 -m echo_renderer.cli install",
            "python3 -m echo_renderer.cli verify",
            "python3 -m echo_renderer.cli promote",
            "python3 -m echo_renderer.cli repair",
            "ECHO_RESOURCE_DIR",
            "manifest-bound receipts",
            "modelBytesAttested: false",
            "Historical receipts are read-only",
            "No automatic cleanup",
            "local-only",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, normalized)

        for stale_marker in (
            "calls the memory gate",
            'make -C "$ECHO_REPO" echo-cli',
            "$ECHO_REPO/.build/cli/Build/Products/Release/echo-cli",
            "approved_echo_pronunciation_sha=unpinned",
        ):
            with self.subTest(stale_marker=stale_marker):
                self.assertNotIn(stale_marker, normalized)

    def test_fiction_block_runbook_names_executable_boundaries(self) -> None:
        """Keep only operator-visible command and artifact boundaries in prose."""
        heading = "## Source-bound block voices"
        self.assertIn(heading, self.narrating)
        if heading not in self.narrating:
            return
        section = self.narrating.split(heading, 1)[1]
        section = section.split("## Chapter-mode resuming and partial renders", 1)[0]
        for boundary in (
            'INVENTORY="$RUN_ROOT/research/echo-block-inventory-$EPUB_SHA256.json"',
            '"$LEASE_HELPER" --lock-root "$CANONICAL_LEASE_ROOT"',
            '--resource "$ECHO_RENDERER_BUILD_ROOT" --',
            '"ECHO_RESOURCE_DIR=$ECHO_RESOURCE_DIR"',
            '"$CLI" export-blocks --epub "$EPUB" --out "$INVENTORY"',
            '"$NARRATION_SCRIPT" "${VOICE_ARGUMENTS[@]}"',
        ):
            with self.subTest(boundary=boundary):
                self.assertIn(boundary, section)

        installed_resolver = (
            ROOT
            / "skills/echo-narration/scripts/echo_installed_renderer.py"
        ).read_text(encoding="utf-8")
        self.assertIn('"export-blocks"', installed_resolver)
        self.assertIn('"resolve-voice-plan"', installed_resolver)
        self.assertIn("--voice-plan", self.narrate_wrapper)
        self.assertIn(
            'REEL="$RUN_ROOT/research/listening/$RUN_ID/$ATTEMPT_ID/',
            self.narrate_wrapper,
        )

    def test_fiction_block_handoff_stops_before_wrapper_on_invalid_cast(self) -> None:
        """A rejected block cast must not fall through to legacy narration."""
        marker = "Forward the validator's NUL-delimited result"
        self.assertIn(marker, self.narrating)
        handoff = self.narrating.split(marker, 1)[1]
        handoff = handoff.split("```bash\n", 1)[1].split("```", 1)[0].strip()

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw).resolve()
            narration = root / "narration"
            narration.mkdir()
            voice_plan = (narration / "echo-voice-plan.json").resolve()
            voice_cast = (narration / "voice-cast.json").resolve()
            run_root = root / "run"
            wrapper = (root / "fake-narration-wrapper.sh").resolve()
            wrapper_log = root / "wrapper-called.log"

            speakers = [
                {"id": "narrator", "voiceID": "am_michael"},
                {"id": "mara", "voiceID": "bf_emma"},
                {"id": "ivo", "voiceID": "af_heart"},
            ]
            voice_plan.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "source": {"epubSHA256": "a" * 64},
                        "defaultSpeakerID": "narrator",
                        "speakers": speakers,
                        "assignments": [],
                    },
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            voice_cast.write_text(
                json.dumps(
                    {
                        "schemaVersion": 2,
                        "slug": "invalid-cast",
                        "narrationMode": "block",
                        "sourceEPUBSHA256": "a" * 64,
                        "defaultSpeakerID": "narrator",
                        "speakers": [
                            {
                                "speakerID": "narrator",
                                "role": "Narrator",
                                "voiceID": "am_michael",
                                "experimental": False,
                            },
                            {
                                "speakerID": "mara",
                                "role": "Mara",
                                "voiceID": "bf_emma",
                                "experimental": False,
                            },
                            {
                                "speakerID": "ivo",
                                "role": "Ivo",
                                "voiceID": "af_heart",
                                "experimental": False,
                            },
                        ],
                        "authoredVoicePlan": {
                            "fileName": voice_plan.name,
                            "sha256": hashlib.sha256(voice_plan.read_bytes()).hexdigest(),
                        },
                        "resolvedVoicePlan": None,
                        "verifiedArtifacts": None,
                    },
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            wrapper.write_text(
                "#!/bin/bash\n"
                "set -euo pipefail\n"
                "printf '%s\\n' \"$@\" >\"$WRAPPER_LOG\"\n"
                "mkdir -p -- \"$RUN_ROOT/research\"\n"
                "touch -- \"$RUN_ROOT/research/echo-render-inputs-unexpected.env\"\n"
                "mkdir -p -- \"$RUN_ROOT/audio-work-unexpected\"\n"
                "touch -- \"$RUN_ROOT/narration-unexpected.sqlite\"\n",
                encoding="utf-8",
            )
            wrapper.chmod(0o700)

            environment = os.environ.copy()
            environment.update(
                {
                    "VOICE_CAST": str(voice_cast),
                    "VOICE_PLAN": str(voice_plan),
                    "PREFERENCES": str(root / "preferences.json"),
                    "NARRATION_SCRIPT": str(wrapper),
                    "RUN_ROOT": str(run_root),
                    "WRAPPER_LOG": str(wrapper_log),
                    "TMPDIR": str(root),
                }
            )
            result = subprocess.run(
                # Do not let a surrounding `set -e` mask whether the fence
                # itself stops before calling the wrapper.
                ["/bin/bash", "-c", "set -o pipefail\n" + handoff],
                cwd=ROOT,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(64, result.returncode, result.stderr)
            self.assertIn("blacklisted", result.stderr)
            self.assertFalse(wrapper_log.exists())
            self.assertFalse(
                (run_root / "research" / "echo-render-inputs-unexpected.env").exists()
            )
            self.assertFalse((run_root / "audio-work-unexpected").exists())
            self.assertFalse((run_root / "narration-unexpected.sqlite").exists())
            self.assertEqual([], list(root.glob("echo-fiction-voice-arguments.*")))

    def test_block_runbook_uses_sealed_delivery_evidence_and_schema7_argv(self) -> None:
        """The operator command must not depend on a wrapper-child variable."""
        heading = "## Audio verification"
        self.assertIn(heading, self.narrating)
        section = self.narrating.split(heading, 1)[1]
        for boundary in (
            '"$STATE_HELPER" \\\n  block-delivery-evidence',
            "--format env0",
            'VOICE_PLAN_MODE',
            'REEL_RELATIVE_PATH',
            'VOICE_PLAN_SHA256',
            'VOICE_PLAN_BLOCK_COUNT',
            '--audiobook "$AUDIOBOOK"',
            '--reel "$REEL"',
            '--voice-plan-sha256 "$VOICE_PLAN_SHA256"',
            '--block-count "$VOICE_PLAN_BLOCK_COUNT"',
        ):
            with self.subTest(boundary=boundary):
                self.assertIn(boundary, section)
        self.assertNotIn('${VOICE_PLAN_MODE:-chapter}', section)

    def test_resume_and_delivery_steps_keep_block_vectors_and_gate_order(self) -> None:
        """Mode-specific command lines must not silently drop the block plan."""
        self.assertIn("## Chapter-mode resuming and partial renders", self.narrating)
        fiction = self.narrating.split("## Source-bound block voices", 1)[1]
        resume = fiction.split("## Chapter-mode resuming and partial renders", 1)[0]
        self.assertIn('"$NARRATION_SCRIPT" "${VOICE_ARGUMENTS[@]}"', resume)

        fiction_skill = (
            ROOT / "skills" / "fiction-audiobook" / "SKILL.md"
        ).read_text(encoding="utf-8")
        evidence = fiction_skill.index("Materialize the current `_production` evidence")
        staging = fiction_skill.index("stage_echo_delivery.py")
        github = fiction_skill.index("GitHub only after successful iCloud staging")
        self.assertLess(evidence, staging)
        self.assertLess(staging, github)

    def test_narrate_wrapper_uses_shared_preflight_functions_without_local_copies(
        self,
    ) -> None:
        """Guards the same class of drift as test_run_id_is_derived_in_exactly_one_place:
        two of the four tests dropped when the pilot wrapper was deleted were
        mixed-subject and also asserted that the narrate wrapper calls the
        shared preflight helpers instead of defining its own local copies.
        Duplicating a preflight helper locally in the wrapper once let the two
        definitions disagree and broke every render. This is not redundant with
        merely checking the shared helper is called: that only proves the
        wrapper reaches the shared code path, not that a shadowing local
        definition hasn't also been added alongside it.
        """
        for defined_function in (
            "echo_pronunciation_resolve_installed_renderer() {",
            "echo_pronunciation_assert_leases() {",
            "echo_pronunciation_attest_renderer() {",
            "echo_pronunciation_renderer_receipt_text() {",
        ):
            with self.subTest(defined_function=defined_function):
                self.assertIn(defined_function, self.preflight)

        self.assertIn(
            "echo_pronunciation_resolve_installed_renderer", self.narrate_wrapper
        )
        self.assertIn("echo_pronunciation_assert_leases", self.narrate_wrapper)

        self.assertNotIn("\nresolve_installed_renderer() {", self.narrate_wrapper)
        self.assertNotIn("\nassert_leases() {", self.narrate_wrapper)


if __name__ == "__main__":
    unittest.main()
