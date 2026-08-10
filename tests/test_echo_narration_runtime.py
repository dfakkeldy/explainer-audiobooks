from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import platform
import pwd
import re
import runpy
import shlex
import signal
import socket
import stat
import subprocess
import sys
import tempfile
import time
import unittest
import zipfile
from collections.abc import Callable
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).parents[1]
# These tests spawn real narration wrappers and wait on their side effects. The
# machine routinely runs concurrent Echo renders that saturate the CPU, so a tight
# deadline reports load as a lease bug. Raise ECHO_TEST_WAIT_TIMEOUT on a busy host;
# it bounds a failure path, so a generous value costs nothing when tests pass.
WAIT_TIMEOUT = float(os.environ.get("ECHO_TEST_WAIT_TIMEOUT", "60"))
PREFLIGHT = (
    ROOT
    / "skills"
    / "echo-narration"
    / "scripts"
    / "echo_pronunciation_preflight.sh"
)
AUDIT_VALIDATOR = (
    ROOT
    / "skills"
    / "echo-narration"
    / "scripts"
    / "validate_pronunciation_audit.py"
)
NARRATE_WRAPPER = (
    ROOT
    / "skills"
    / "echo-narration"
    / "scripts"
    / "echo_pronunciation_narrate.sh"
)
LEASE_HELPER = (
    ROOT
    / "skills"
    / "echo-narration"
    / "scripts"
    / "echo_pronunciation_lease.py"
)
STATE_HELPER = (
    ROOT
    / "skills"
    / "echo-narration"
    / "scripts"
    / "echo_pronunciation_state.py"
)
INSTALLED_RENDERER = (
    ROOT
    / "skills"
    / "echo-narration"
    / "scripts"
    / "echo_installed_renderer.py"
)

ACCEPTED_INSTALLER_SHA = "2f23aceedb1b9f25b7ea4410756eea32a59af8cd"
ACCEPTED_SOURCE_SHA = "81a635df84f75f2e391706e071878b379e6fe0a0"
REQUIRED_CAPABILITIES = (
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
    "verify-sidecar",
)
LEGACY_FIXTURE_WATCH_WORDS = (
    "able",
    "arithmetic",
    "available",
    "campbell",
    "comfortable",
    "content",
    "deepmind",
    "deepmind's",
    "fakkeldy",
    "filesystem",
    "lifecycle",
    "live",
    "lives",
    "pictou",
    "possible",
    "re",
    "read",
    "readme",
    "record",
    "reliable",
    "resume",
    "resumes",
    "résumé",
    "résumés",
    "stable",
    "startable",
    "super",
    "supercomputer",
    "supercomputers",
    "superforecasters",
    "superhuman",
    "superimposed",
    "superintelligence",
    "supernatural",
    "superposition",
    "supervised",
    "supervising",
    "table",
    "timeframe",
    "unsupervised",
    "validator",
    "validators",
    "verified",
    "xcassets",
    "xcode",
)


def canonical_json(payload: dict[str, object]) -> bytes:
    return (
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        .encode("utf-8")
        + b"\n"
    )


def resource_tree_identity(root: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    files = sorted(path for path in root.rglob("*") if path.is_file())
    for path in files:
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big", signed=False))
        digest.update(relative)
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest(), len(files)

# Backstop against a hang, never an assertion about speed: every wait below returns
# as soon as its condition holds, so this only costs wall time when something is
# genuinely stuck. It must clear the narration pipeline's spawn-and-hash work on a
# loaded machine -- at load average ~30 the median time-to-ready measured 5.8s and
# the peak 14s, so the former 5s budget failed about half the time.
WAIT_TIMEOUT = float(os.environ.get("ECHO_TEST_WAIT_TIMEOUT", "60"))


def load_audit_validator_module():
    specification = importlib.util.spec_from_file_location(
        "custom_learning_pronunciation_audit_validator",
        AUDIT_VALIDATOR,
    )
    if specification is None or specification.loader is None:
        raise RuntimeError(f"cannot import {AUDIT_VALIDATOR}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


AUDIT_VALIDATOR_MODULE = load_audit_validator_module()


class EchoPronunciationPreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.tmp = Path(self.temporary.name).resolve()
        self.echo = self.tmp / "Echo"
        self.explainer = self.tmp / "explainer-audiobooks"
        self.home = self.tmp / "home"
        self.fake_bin = self.home / "bin"
        self.installed_probe_log = self.tmp / "installed-probe-environment.log"
        self.run_root = (
            self.explainer / ".build" / "custom-learning-audiobooks" / "fixture"
        )
        self.uninstalled_cli_fixture = (
            self.echo / ".build" / "cli" / "Build" / "Products" / "Release" / "echo-cli"
        )
        self.uninstalled_resources_fixture = (
            self.uninstalled_cli_fixture.parent / "EchoNarrationResources"
        )
        self.renderer_root = (self.tmp / "installed-renderers").resolve()
        self.source_sha = ACCEPTED_SOURCE_SHA
        self.installer_source_sha = ACCEPTED_INSTALLER_SHA
        self.model_policy_revision = "kokoro-fixture-revision"
        self.model_expected_byte_count = 163234740
        self.fake_voice_plan_sha = self.tmp / "fake-voice-plan-sha"
        self.fake_resolve_lease_probe = self.tmp / "fake-resolve-lease-probe"
        self.fake_resolve_lease_log = self.tmp / "fake-resolve-lease.log"
        # Mirrors echo_pronunciation_canonical_lease_root (echo_pronunciation_preflight.sh),
        # which derives this root from the passwd database and so ignores both $HOME and
        # $ECHO_PRONUNCIATION_LEASE_ROOT — the wrappers overwrite that variable with the
        # canonical value rather than reading it, so the lease namespace cannot be forked
        # (see test_alternate_lock_root_cannot_fork_the_build_lease_namespace). Redirecting
        # this at a tmp dir would not move where the scripts lease; it would only desync the
        # harness from them, so --assert-held fails and every leased test returns 70.
        self.lease_root = (
            Path(pwd.getpwuid(os.geteuid()).pw_dir)
            / ".cache"
            / "explainer-audiobooks"
            / "echo-pronunciation-leases"
        )

        self.echo.mkdir(parents=True)
        self.renderer_root.mkdir()
        self.explainer.mkdir()
        (self.echo / "Makefile").write_text(
            "echo-cli:\n\t@test -x .build/cli/Build/Products/Release/echo-cli\n",
            encoding="utf-8",
        )
        (self.echo / ".gitignore").write_text(".build/\n", encoding="utf-8")
        self.uninstalled_cli_fixture.parent.mkdir(parents=True)
        self.uninstalled_resources_fixture.mkdir()
        self.write_cli(
            include_review_flag=True,
            cli=self.uninstalled_cli_fixture,
            resources=self.uninstalled_resources_fixture,
        )

        staging_root = self.renderer_root / self.source_sha / ("f" * 64)
        self.cli = staging_root / "echo-cli"
        self.resources = staging_root / "EchoNarrationResources"
        self.resources.mkdir(parents=True)
        self.write_cli(include_review_flag=True)
        resource_sha, resource_count = resource_tree_identity(self.resources)
        manifest_payload = {
            "schemaVersion": 1,
            "echoSourceSHA": self.source_sha,
            "installerSourceSHA": self.installer_source_sha,
            "executablePath": "echo-cli",
            "executable": {
                "sha256": hashlib.sha256(self.cli.read_bytes()).hexdigest(),
                "byteCount": self.cli.stat().st_size,
            },
            "resourcesPath": "EchoNarrationResources",
            "resources": {
                "sha256": resource_sha,
                "regularFileCount": resource_count,
            },
            "renderVersion": 12,
            "buildConfiguration": "Release",
            "architectures": [platform.machine() or "arm64"],
            "minimumMacOSVersion": "10.15",
            "modelPolicy": {
                "revision": self.model_policy_revision,
                "expectedByteCount": self.model_expected_byte_count,
                "deliveryMode": "sharedEchoCache",
                "modelBytesAttested": False,
            },
            "capabilities": list(REQUIRED_CAPABILITIES),
        }
        self.manifest_payload = copy.deepcopy(manifest_payload)
        manifest_data = canonical_json(manifest_payload)
        self.renderer_manifest_sha = hashlib.sha256(manifest_data).hexdigest()
        (staging_root / "renderer-manifest.json").write_bytes(manifest_data)
        self.renderer_build_root = (
            self.renderer_root / self.source_sha / self.renderer_manifest_sha
        )
        staging_root.rename(self.renderer_build_root)
        self.cli = self.renderer_build_root / "echo-cli"
        self.resources = self.renderer_build_root / "EchoNarrationResources"
        (self.renderer_root / self.source_sha / "approved-renderer.json").write_bytes(
            canonical_json(
                {
                    "schemaVersion": 1,
                    "echoSourceSHA": self.source_sha,
                    "manifestSHA256": self.renderer_manifest_sha,
                }
            )
        )

        self.fake_bin.mkdir(parents=True)
        ffprobe = self.fake_bin / "ffprobe"
        ffprobe.write_text(
            "#!/usr/bin/env bash\nprintf '%s\\n' "
            '\'{"format":{"duration":"5.0"}}\'\n',
            encoding="utf-8",
        )
        ffprobe.chmod(ffprobe.stat().st_mode | stat.S_IXUSR)

        gate = self.home / ".claude" / "bin" / "xcode-build-gate.sh"
        gate.parent.mkdir(parents=True)
        gate.write_text(
            "#!/usr/bin/env bash\nset -euo pipefail\n[[ ${1:-} == --wait ]]\n",
            encoding="utf-8",
        )
        gate.chmod(gate.stat().st_mode | stat.S_IXUSR)

        dist = self.run_root / "dist"
        self.pair = dist / "candidate-1"
        self.pair.mkdir(parents=True)
        self.portrait = self.pair / "cover.png"
        self.square = self.pair / "m4b-cover.png"
        Image.new("RGB", (1600, 2560), "#243447").save(self.portrait, "PNG")
        Image.new("RGB", (2400, 2400), "#375a7f").save(self.square, "PNG")
        sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
        filler = "a" * 64
        self.cover_selection_payload = {
            "schema_version": 2,
            "book_slug": "fixture",
            "edition_id": "fixture-private-v1",
            "candidate": {"id": "fixture-pair", "direction_name": "Fixture Pair"},
            "source_art_sha256": filler,
            "variants": {
                "portrait": {
                    "specification_sha256": filler,
                    "render_receipt_sha256": filler,
                    "cover_sha256": sha(self.portrait),
                    "dimensions": [1600, 2560],
                    "thumbnail_sha256": filler,
                    "subtitle_included": True,
                },
                "square": {
                    "specification_sha256": filler,
                    "render_receipt_sha256": filler,
                    "cover_sha256": sha(self.square),
                    "dimensions": [2400, 2400],
                    "thumbnail_sha256": filler,
                    "subtitle_included": False,
                },
            },
            "font_manifest_sha256": filler,
            "selection_source": "user",
            "selected_at": "2026-07-14T00:00:00+00:00",
            "privacy": {"classification": "private", "permission_to_publish": False},
        }
        chapters = self.run_root / "chapters"
        research = self.run_root / "research"
        chapters.mkdir()
        research.mkdir()
        (chapters / "ch01.md").write_text(
            "# Fixture chapter\n\nThis fixture exercises the governed narration path.\n",
            encoding="utf-8",
        )
        (research / "learning-outline.json").write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "chapters": [
                        {
                            "file": "ch01.md",
                            "purpose": "Exercise the governed narration path.",
                            "prerequisites": [],
                        }
                    ],
                },
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        with zipfile.ZipFile(dist / "fixture.epub", "w") as archive:
            archive.writestr(
                "META-INF/container.xml",
                """<?xml version="1.0"?>
<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
  <rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>""",
            )
            archive.writestr(
                "OEBPS/content.opf",
                """<?xml version="1.0"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><meta name="cover" content="cover-image"/></metadata>
  <manifest><item id="cover-image" href="cover.png" media-type="image/png" properties="cover-image"/></manifest>
</package>""",
            )
            archive.writestr("OEBPS/cover.png", self.portrait.read_bytes())

        self.git("init", "-q")
        self.git("config", "user.email", "fixture@example.com")
        self.git("config", "user.name", "Fixture")
        self.git("add", "Makefile", ".gitignore")
        self.git("commit", "-qm", "first")
        self.first_sha = self.git("rev-parse", "HEAD").stdout.strip()
        (self.echo / "revision.txt").write_text("second\n", encoding="utf-8")
        self.git("add", "revision.txt")
        self.git("commit", "-qm", "second")
        self.second_sha = self.git("rev-parse", "HEAD").stdout.strip()

    def git(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(self.echo), *arguments],
            check=True,
            capture_output=True,
            text=True,
        )

    def write_cli(
        self,
        *,
        include_review_flag: bool,
        render_version: int = 12,
        cli: Path | None = None,
        resources: Path | None = None,
    ) -> None:
        cli = cli or self.cli
        resources = resources or self.resources
        probe_block_control = self.tmp / "probe-block-control"
        probe_block_count = self.tmp / "probe-block-count"
        probe_block_ready = self.tmp / "probe-block-ready"
        probe_block_release = self.tmp / "probe-block-release"
        help_text = " ".join(REQUIRED_CAPABILITIES[:-1]) if include_review_flag else "--voice"
        (resources / "pronunciations.json").write_text(
            json.dumps({"renderVersion": render_version}) + "\n", encoding="utf-8"
        )
        emitter = resources / "fake_echo_emit.py"
        emitter_source = """#!/usr/bin/env python3
import hashlib, json, os, pathlib, sys

epub, out, sidecar, work, db = map(pathlib.Path, sys.argv[1:6])
voice = sys.argv[6]
voice_plan = pathlib.Path(sys.argv[7]) if len(sys.argv) == 8 else None
resolved_plan = None
out.parent.mkdir(parents=True, exist_ok=True)
work.mkdir(parents=True, exist_ok=True)
db.write_bytes(b"fixture database")
audio = work / "chapter-0.m4a"
audio.write_bytes(b"fixture chapter audio")
def frame(value):
    data = value.encode()
    return str(len(data)).encode() + b":" + data
raw = epub.read_bytes()
source = hashlib.sha256(frame("source-kind=epub") + frame(f"bytes={len(raw)}") + raw).hexdigest()
payload = {"duration": 1.0, "anchors": [], "pronunciationEvidence": {"decisions": [], "diagnostics": []}}
payload_bytes = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
identity = {
    "schemaVersion": 1, "captureSetID": "c" * 64, "sourceFingerprint": source,
    "voice": voice, "renderVersion": __RENDER_VERSION__, "rendererIdentity": "fixture-renderer",
    "normalizationMode": "spoken", "chapterIndex": 0,
    "chapterContentSignature": "d" * 16, "audioFileName": audio.name,
    "audioFileByteCount": audio.stat().st_size,
    "audioSHA256": hashlib.sha256(audio.read_bytes()).hexdigest(),
    "payloadSHA256": hashlib.sha256(payload_bytes).hexdigest(),
}
if voice_plan is not None:
    resolution = voice_plan.with_name(
        "echo-voice-plan-resolution-"
        + voice_plan.name.removeprefix("echo-voice-plan-")
    )
    resolved_plan = json.loads(resolution.read_text(encoding="utf-8"))
    identity.update(
        {
            "schemaVersion": 2,
            "voicePlanSHA256": resolved_plan["voicePlanSHA256"],
            "chapterVoicePlanSHA256": "e" * 64,
        }
    )
marker = dict(payload)
marker["identity"] = identity
(work / ".anchors-ch0.json").write_text(json.dumps(marker, sort_keys=True, separators=(",", ":")))
out.write_bytes(b"fixture audiobook bytes")
words = ("able", "arithmetic", "available", "campbell", "comfortable", "content", "deepmind", "deepmind's", "fakkeldy", "filesystem", "lifecycle", "live", "lives", "pictou", "possible", "re", "read", "readme", "record", "reliable", "resume", "resumes", "résumé", "résumés", "stable", "startable", "super", "supercomputer", "supercomputers", "superforecasters", "superhuman", "superimposed", "superintelligence", "supernatural", "superposition", "supervised", "supervising", "table", "timeframe", "unsupervised", "validator", "validators", "verified", "xcassets", "xcode")
if resolved_plan is None:
    sidecar.write_text("{}\\n")
    audit = {
        "schemaVersion": 6, "renderVersion": __RENDER_VERSION__, "voice": voice,
        "chapterVoices": {"0": voice}, "coverage": "complete",
        "watchCounts": {word: 0 for word in words}, "decisions": [], "diagnostics": [],
        "legacyChapterIndexes": [], "audiobookFileName": out.name,
        "audiobookSHA256": hashlib.sha256(out.read_bytes()).hexdigest(),
    }
else:
    sidecar.write_text('[{"blockId":"s2-b3","timestamp":0}]\\n')
    block_count = int(resolved_plan["blockCount"])
    block_voices = {
        "s2-b3": "bf_emma",
        "s2-b4": "am_michael",
        "s2-b5": "bm_george",
    }
    block_voices = dict(list(block_voices.items())[:block_count])
    audit = {
        "schemaVersion": 7, "renderVersion": __RENDER_VERSION__, "voice": "mixed",
        "chapterVoices": {}, "voicePlanSHA256": resolved_plan["voicePlanSHA256"],
        "blockVoices": block_voices,
        "coverage": "complete", "watchCounts": {word: 0 for word in words},
        "decisions": [], "diagnostics": [], "legacyChapterIndexes": [],
        "audiobookFileName": out.name,
        "audiobookSHA256": hashlib.sha256(out.read_bytes()).hexdigest(),
    }
if os.environ.get("FAKE_EMIT_REEL"):
    reel = out.with_suffix(".pronunciation-reel.m4b")
    reel.write_bytes(b"fixture listening reel")
    audit["listeningReelFileName"] = reel.name
    audit["listeningReelSHA256"] = hashlib.sha256(reel.read_bytes()).hexdigest()
    audit["watchCounts"]["read"] = 1
    audit["decisions"] = [{
        "blockID": "s2-b3" if resolved_plan is not None else "block-1", "wordStart": 0, "wordEnd": 4,
        "normalizedWord": "read", "sourceWord": "read",
        "sourceContext": "read the fixture", "selectedIPA": "read",
        "kokoroTokenIDs": [1], "source": "monitoredLexicon",
        "ruleID": "fixture-read", "rationale": "fixture listening sample",
        "chapterIndex": 0,
        "chapterRelativeAudioRange": {"start": 0.1, "end": 0.5},
        "bookRelativeAudioRange": {"start": 0.1, "end": 0.5},
        "timingPrecision": "exactSynthesisWord",
    }]
if not os.environ.get("FAKE_SKIP_AUDIT"):
    out.with_suffix(".pronunciation-audit.json").write_text(json.dumps(audit))
"""
        emitter.write_text(
            emitter_source.replace("__RENDER_VERSION__", str(render_version)),
            encoding="utf-8",
        )
        emitter.chmod(emitter.stat().st_mode | stat.S_IXUSR)
        cli.write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            'script_dir=$(cd -- "$(dirname -- "$0")" && pwd -P)\n'
            f"printf 'CALL=%s:%s ECHO_RESOURCE_DIR=%s\\n' "
            '"${1:-}" "${2:-}" "${ECHO_RESOURCE_DIR-<unset>}" '
            f">>{shlex.quote(str(self.installed_probe_log))}\n"
            "if [[ -n ${FAKE_ECHO_ENV_LOG:-} ]]; then\n"
            "  printf 'CALL=%s:%s ECHO_RESOURCE_DIR=%s\\n' "
            '"${1:-}" "${2:-}" "${ECHO_RESOURCE_DIR-<unset>}" '
            '>>"$FAKE_ECHO_ENV_LOG"\n'
            "fi\n"
            'if [[ ${1:-} == verify-sidecar && ${2:-} == --help '
            f'  && -f {shlex.quote(str(probe_block_control))} ]]; then\n'
            f'  probe_target=$(<{shlex.quote(str(probe_block_control))})\n'
            "  probe_count=0\n"
            f'  [[ ! -f {shlex.quote(str(probe_block_count))} ]] '
            f'|| read -r probe_count <{shlex.quote(str(probe_block_count))}\n'
            "  (( probe_count += 1 ))\n"
            f'  printf "%s\\n" "$probe_count" >{shlex.quote(str(probe_block_count))}\n'
            '  if [[ $probe_count == "$probe_target" ]]; then\n'
            f'    touch {shlex.quote(str(probe_block_ready))}\n'
            f'    while [[ ! -e {shlex.quote(str(probe_block_release))} ]]; '
            'do sleep 0.05; done\n'
            "  fi\n"
            "fi\n"
            "if [[ ${1:-} == --version ]]; then\n"
            f"  echo 'ONNX rv{render_version} (Release)'\n"
            "elif [[ ${1:-} == narrate && ${2:-} == --help ]]; then\n"
            f"  echo '{help_text}'\n"
            "elif [[ ${1:-} == resolve-voice-plan && ${2:-} == --help ]]; then\n"
            "  echo 'resolve-voice-plan --epub --voice-plan'\n"
            "elif [[ ${1:-} == export-blocks && ${2:-} == --help ]]; then\n"
            "  echo 'export-blocks --epub'\n"
            "elif [[ ${1:-} == export-blocks ]]; then\n"
            "  epub= out=\n"
            "  shift\n"
            "  while (( $# )); do\n"
            "    case \"$1\" in\n"
            "      --epub) epub=$2; shift 2 ;;\n"
            "      --out) out=$2; shift 2 ;;\n"
            "      *) exit 64 ;;\n"
            "    esac\n"
            "  done\n"
            "  [[ -n $epub && -n $out ]] || exit 64\n"
            "  source_sha=$(/usr/bin/shasum -a 256 \"$epub\" | awk '{print $1}')\n"
            "  source_name=${epub##*/}\n"
            "  printf '{\\\"blocks\\\":[{\\\"id\\\":\\\"s2-b3\\\"},{\\\"id\\\":\\\"s2-b4\\\"},{\\\"id\\\":\\\"s2-b5\\\"}],\\\"source\\\":{\\\"epub\\\":\\\"%s\\\",\\\"epubSHA256\\\":\\\"%s\\\"},\\\"version\\\":2}\\n' \"$source_name\" \"$source_sha\" >\"$out\"\n"
            "elif [[ ${1:-} == resolve-voice-plan ]]; then\n"
            "  epub= plan=\n"
            "  shift\n"
            "  while (( $# )); do\n"
            "    case \"$1\" in\n"
            "      --epub) epub=$2; shift 2 ;;\n"
            "      --voice-plan) plan=$2; shift 2 ;;\n"
            "      *) exit 64 ;;\n"
            "    esac\n"
            "  done\n"
            "  [[ -n $epub && -n $plan ]] || exit 64\n"
            "  if [[ -n ${FAKE_RESOLVE_LOG:-} ]]; then printf 'PLAN=%s\\n' \"$plan\" >>\"$FAKE_RESOLVE_LOG\"; fi\n"
            f"  if [[ -e {shlex.quote(str(self.fake_resolve_lease_probe))} ]]; then\n"
            "    lease_status=0\n"
            f"    if /usr/local/bin/python3 {shlex.quote(str(LEASE_HELPER))} "
            f"--lock-root {shlex.quote(str(self.lease_root))} --resource \"$script_dir\" "
            "-- /usr/bin/true >/dev/null 2>&1; then\n"
            "      lease_status=0\n"
            "    else\n"
            "      lease_status=$?\n"
            "    fi\n"
            f"    printf 'LEASE_STATUS=%s RESOURCE=%s\\n' \"$lease_status\" \"$script_dir\" >>{shlex.quote(str(self.fake_resolve_lease_log))}\n"
            "  fi\n"
            "  source_sha=$(/usr/bin/shasum -a 256 \"$epub\" | awk '{print $1}')\n"
            f"  if [[ -s {shlex.quote(str(self.fake_voice_plan_sha))} ]]; then\n"
            f"    IFS= read -r plan_sha <{shlex.quote(str(self.fake_voice_plan_sha))}\n"
            "  else\n"
            "    plan_sha=$(printf '%064d' 0 | tr 0 b)\n"
            "  fi\n"
            "  block_count=2\n"
            "  /usr/bin/grep -q '\"range\"' \"$plan\" && block_count=3\n"
            "  printf '{\\\"blockCount\\\":%s,\\\"defaultVoice\\\":\\\"am_michael\\\",\\\"sourceEPUBSHA256\\\":\\\"%s\\\",\\\"voicePlanID\\\":\\\"plan-%s\\\",\\\"voicePlanSHA256\\\":\\\"%s\\\"}\\n' \"$block_count\" \"$source_sha\" \"${plan_sha:0:12}\" \"$plan_sha\"\n"
            "elif [[ ${1:-} == verify-sidecar ]]; then\n"
            "  if [[ ${2:-} == --help ]]; then echo 'verify-sidecar'; exit 0; fi\n"
            "  if [[ -n ${FAKE_TAMPER_RESUME_STATE_ON_VERIFY:-} ]]; then\n"
            "    tamper_marker=$RUN_ROOT/research/fake-resume-tamper-fired\n"
            "    if [[ ! -e $tamper_marker ]]; then\n"
            "      printf 'changed after state seal' >\"$RUN_ROOT\"/narration-*.sqlite\n"
            '      touch "$tamper_marker"\n'
            "    fi\n"
            "  fi\n"
            "  exit 0\n"
            "elif [[ ${1:-} == narrate ]]; then\n"
            "  shift\n"
            "  if [[ -n ${FAKE_NARRATE_LOG:-} ]]; then\n"
            '    printf \'BEGIN=%s\\n\' "$BASHPID" >>"$FAKE_NARRATE_LOG"\n'
            '    printf \'ARG=%s\\n\' "$@" >>"$FAKE_NARRATE_LOG"\n'
            '    printf \'ENV=RUN_ID=%s INPUT_RECEIPT=%s STATE_RECEIPT=%s ARTIFACT_ROOT=%s VOICE=%s\\n\' '
            '"${RUN_ID-<unset>}" "${ECHO_RENDER_INPUT_RECEIPT-<unset>}" '
            '"${STATE_RECEIPT-<unset>}" "${ARTIFACT_ROOT-<unset>}" "${VOICE-<unset>}" >>"$FAKE_NARRATE_LOG"\n'
            "  fi\n"
            "  work= db= out= sidecar= epub= voice= chapter_voice= voice_plan=\n"
            "  while (( $# )); do\n"
            '    case "$1" in\n'
            "      --work-dir) work=$2; shift 2 ;;\n"
            "      --db) db=$2; shift 2 ;;\n"
            "      --out) out=$2; shift 2 ;;\n"
            "      --sidecar) sidecar=$2; shift 2 ;;\n"
            "      --epub) epub=$2; shift 2 ;;\n"
            "      --voice) voice=$2; shift 2 ;;\n"
            "      --voice-plan) voice_plan=$2; voice=am_michael; shift 2 ;;\n"
            "      --chapter-voice) chapter_voice=$2; shift 2 ;;\n"
            "      --resume) shift ;;\n"
            "      *) shift ;;\n"
            "    esac\n"
            "  done\n"
            '  [[ $chapter_voice != 1=* ]] || voice=${chapter_voice#1=}\n'
            '  [[ -z ${FAKE_NARRATE_READY:-} ]] || touch "$FAKE_NARRATE_READY"\n'
            "  if [[ -n ${FAKE_NARRATE_RELEASE:-} ]]; then\n"
            "    while [[ ! -e $FAKE_NARRATE_RELEASE ]]; do sleep 0.05; done\n"
            "  fi\n"
            "  if [[ -z ${FAKE_SKIP_CAPTURE:-} ]]; then\n"
            '    if [[ -n $voice_plan ]]; then\n'
            '      "$script_dir/EchoNarrationResources/fake_echo_emit.py" "$epub" "$out" "$sidecar" "$work" "$db" "$voice" "$voice_plan"\n'
            "    else\n"
            '      "$script_dir/EchoNarrationResources/fake_echo_emit.py" "$epub" "$out" "$sidecar" "$work" "$db" "$voice"\n'
            "    fi\n"
            "  fi\n"
            '  exit "${FAKE_NARRATE_EXIT:-0}"\n'
            "else\n"
            "  exit 64\n"
            "fi\n",
            encoding="utf-8",
        )
        cli.chmod(cli.stat().st_mode | stat.S_IXUSR)

    def environment(self) -> dict[str, str]:
        environment = os.environ.copy()
        environment.update(
            {
                "HOME": str(self.home),
                "ECHO_REPO": str(self.echo),
                "APPROVED_ECHO_PRONUNCIATION_SHA": self.source_sha,
                "ECHO_SOURCE_SHA": self.source_sha,
                "EXPLAINER_ROOT": str(self.explainer),
                "SLUG": "fixture",
                "RUN_ROOT": str(self.run_root),
                "VOICE": "am_michael",
                "TITLE": "Fixture Book",
                "COVER": str(self.run_root / "dist" / "candidate-1" / "cover.png"),
                "M4B_COVER": str(
                    self.run_root / "dist" / "candidate-1" / "m4b-cover.png"
                ),
                "ECHO_RENDERER_ROOT": str(self.renderer_root),
                "ECHO_RENDERER_BUILD_ROOT": str(self.renderer_build_root),
                "ECHO_RENDERER_MANIFEST": str(
                    self.renderer_build_root / "renderer-manifest.json"
                ),
                "ECHO_RENDERER_MANIFEST_SHA256": self.renderer_manifest_sha,
                "APPROVED_ECHO_INSTALLER_SHA": self.installer_source_sha,
                "CLI": str(self.cli),
                "ECHO_CLI_SHA256": hashlib.sha256(self.cli.read_bytes()).hexdigest(),
                "ECHO_RESOURCE_DIR": str(self.resources),
                "ECHO_RESOURCES_SHA256": resource_tree_identity(self.resources)[0],
                "ECHO_RENDER_VERSION": "12",
                "ECHO_MODEL_REVISION": self.model_policy_revision,
                "ECHO_MODEL_EXPECTED_BYTES": str(self.model_expected_byte_count),
                "ECHO_MODEL_BYTES_ATTESTED": "false",
                "ECHO_PRONUNCIATION_LEASE_ROOT": str(self.lease_root),
            }
        )
        environment["PATH"] = f"{self.fake_bin}:{environment['PATH']}"
        return environment

    def write_block_voice_plan(
        self,
        filename: str,
        *,
        sorted_keys: bool = False,
        add_unused_speaker: bool = False,
    ) -> Path:
        """Write one valid authored document; formatting is deliberately caller-owned."""
        plan = self.tmp / filename
        payload = {
            "schemaVersion": 1,
            "source": {
                "epubSHA256": hashlib.sha256(
                    (self.run_root / "dist" / "fixture.epub").read_bytes()
                ).hexdigest()
            },
            "defaultSpeakerID": "narrator",
            "speakers": [{"id": "narrator", "voiceID": "am_michael"}],
            "assignments": [],
        }
        if add_unused_speaker:
            payload["speakers"].append(
                {"id": "analyst", "voiceID": "af_heart"}
            )
        if sorted_keys:
            plan.write_text(
                json.dumps(payload, indent=4, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        else:
            plan.write_text(
                json.dumps(payload, separators=(",", ":")) + "\n",
                encoding="utf-8",
            )
        return plan

    @staticmethod
    def receipt_fields(receipt: Path) -> dict[str, str]:
        return dict(
            line.split("=", 1)
            for line in receipt.read_text(encoding="utf-8").splitlines()
        )

    @staticmethod
    def renderer_identity_from_receipt(payload: dict[str, object]) -> dict[str, object]:
        return {
            key: payload[key]
            for key in (
                "rendererSchemaVersion",
                "rendererRoot",
                "rendererBuildRoot",
                "installerSourceSHA",
                "echoSourceSHA",
                "rendererManifestSHA256",
                "echoCLI_SHA256",
                "echoResourcesSHA256",
                "echoRenderVersion",
                "modelPolicyRevision",
                "modelExpectedByteCount",
                "modelBytesAttested",
            )
        }

    @staticmethod
    def state_namespace() -> dict[str, object]:
        script_directory = str(STATE_HELPER.parent)
        sys.path.insert(0, script_directory)
        try:
            return runpy.run_path(str(STATE_HELPER))
        finally:
            sys.path.remove(script_directory)

    def completed_block_delivery_paths(self, fixture: str) -> dict[str, Path]:
        """Create one governed block chain backed by the installed fake renderer."""

        plan = self.write_block_voice_plan(f"{fixture}.json")
        environment = self.environment()
        environment["FAKE_EMIT_REEL"] = "1"
        rendered = self.run_narrate("--voice-plan", str(plan), environment=environment)
        self.assertEqual(0, rendered.returncode, rendered.stderr)

        research = self.run_root / "research"
        selector = research / "echo-render-current-accepted.json"
        accepted = json.loads(selector.read_text(encoding="utf-8"))
        receipt = research / str(accepted["successReceiptFileName"])
        success = json.loads(receipt.read_text(encoding="utf-8"))
        artifact_root = self.run_root / "dist" / str(accepted["artifactRelativePath"])
        return {
            "attempt": research / "echo-render-current-attempt.json",
            "selector": selector,
            "receipt": receipt,
            "input_receipt": research / str(accepted["inputReceiptFileName"]),
            "state_receipt": research / f"echo-resume-state-{accepted['runID']}.json",
            "epub": self.run_root / "dist" / "fixture.epub",
            "audiobook": artifact_root / "fixture.m4b",
            "sidecar": artifact_root / "fixture.alignment.json",
            "audit": artifact_root / "fixture.pronunciation-audit.json",
            "reel": research / str(success["reelRelativePath"]),
        }

    @staticmethod
    def write_canonical_receipt(path: Path, payload: dict[str, object]) -> None:
        path.write_bytes(
            (
                json.dumps(
                    payload,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=False,
                )
                + "\n"
            ).encode("utf-8")
        )

    def rebind_block_attempt_chain(
        self,
        paths: dict[str, Path],
        mutate: Callable[[dict[str, object]], None],
    ) -> None:
        """Rebind the mutable current chain so schema validation is the gate."""

        attempt = json.loads(paths["attempt"].read_text(encoding="utf-8"))
        mutate(attempt)
        self.write_canonical_receipt(paths["attempt"], attempt)
        attempt_hash = hashlib.sha256(paths["attempt"].read_bytes()).hexdigest()

        success = json.loads(paths["receipt"].read_text(encoding="utf-8"))
        success["attemptReceiptSHA256"] = attempt_hash
        self.write_canonical_receipt(paths["receipt"], success)
        success_hash = hashlib.sha256(paths["receipt"].read_bytes()).hexdigest()

        selector = json.loads(paths["selector"].read_text(encoding="utf-8"))
        selector["attemptReceiptSHA256"] = attempt_hash
        selector["successReceiptSHA256"] = success_hash
        self.write_canonical_receipt(paths["selector"], selector)

    @staticmethod
    def block_delivery_evidence_command(paths: dict[str, Path]) -> list[str]:
        return [
            "/usr/local/bin/python3",
            str(STATE_HELPER),
            "block-delivery-evidence",
            "--attempt",
            str(paths["attempt"]),
            "--selector",
            str(paths["selector"]),
            "--receipt",
            str(paths["receipt"]),
            "--input-receipt",
            str(paths["input_receipt"]),
            "--format",
            "env0",
        ]

    def delivery_fallback_command(
        self,
        paths: dict[str, Path],
        *,
        renderer_arguments: tuple[str, ...] = (),
        voice: str | None = None,
    ) -> list[str]:
        command = [
            "/usr/local/bin/python3",
            str(STATE_HELPER),
            "verify-delivery",
            *renderer_arguments,
        ]
        if voice is not None:
            command.extend(("--voice", voice))
        command.extend(
            (
                "--attempt",
                str(paths["attempt"]),
                "--selector",
                str(paths["selector"]),
                "--receipt",
                str(paths["receipt"]),
                "--input-receipt",
                str(paths["input_receipt"]),
                "--state-receipt",
                str(paths["state_receipt"]),
                "--epub",
                str(paths["epub"]),
                "--audiobook",
                str(paths["audiobook"]),
                "--sidecar",
                str(paths["sidecar"]),
                "--audit",
                str(paths["audit"]),
                "--reel",
                str(paths["reel"]),
            )
        )
        return command

    def verify_state_command(
        self,
        state: Path,
        input_receipt: Path,
        *,
        block: bool,
        extra: tuple[str, ...] = (),
    ) -> subprocess.CompletedProcess[str]:
        payload = json.loads(state.read_text(encoding="utf-8"))
        fields = self.receipt_fields(input_receipt)
        command = [
            "/usr/local/bin/python3",
            str(STATE_HELPER),
            "verify-state",
            *self.renderer_state_arguments(
                self.renderer_identity_from_receipt(payload)
            ),
            "--work",
            fields["work_dir"],
            "--db",
            fields["narration_db"],
            "--receipt",
            str(state),
            "--epub",
            str(self.run_root / "dist" / "fixture.epub"),
            "--source-sha",
            self.source_sha,
            "--voice",
            fields["voice"],
            "--voice-plan-sha256",
            fields["voice_plan_sha256"],
            "--render-version",
            fields["render_version"],
            "--input-receipt",
            str(input_receipt),
        ]
        if block:
            command.extend(
                (
                    "--voice-plan",
                    fields["voice_plan_canonical_path"],
                    "--voice-plan-id",
                    fields["voice_plan_id"],
                    "--voice-plan-block-count",
                    fields["voice_plan_block_count"],
                    "--voice-plan-resolution",
                    fields["voice_plan_resolution_path"],
                )
            )
        command.extend(extra)
        return subprocess.run(command, capture_output=True, text=True)

    def expected_legacy_input_receipt(
        self,
        *,
        chapter_voices: str,
        voice_plan_sha: str,
        voice_plan_id: str,
    ) -> tuple[str, bytes]:
        """Hand-written snapshot of the unchanged legacy wrapper receipt contract."""
        epub = self.run_root / "dist" / "fixture.epub"
        epub_sha = hashlib.sha256(epub.read_bytes()).hexdigest()
        cover_sha = hashlib.sha256(self.portrait.read_bytes()).hexdigest()
        m4b_cover_sha = hashlib.sha256(self.square.read_bytes()).hexdigest()
        package_sha = hashlib.sha256(
            (
                f"epub={epub_sha}\n"
                "cover_selection=receipt-free-private\n"
                f"portrait_cover={cover_sha}\n"
                f"square_cover={m4b_cover_sha}\n"
            ).encode("utf-8")
        ).hexdigest()
        cli_sha = hashlib.sha256(self.cli.read_bytes()).hexdigest()
        resources_sha, _ = resource_tree_identity(self.resources)
        run_id = (
            f"{epub_sha[:12]}-{cli_sha[:12]}-{resources_sha[:12]}-"
            f"{self.renderer_manifest_sha[:12]}-{self.source_sha}-{voice_plan_id}"
        )
        receipt = (
            "renderer_schema_version=1\n"
            f"renderer_root={self.renderer_root}\n"
            f"renderer_build_root={self.renderer_build_root}\n"
            f"installer_source_sha={self.installer_source_sha}\n"
            f"approved_echo_pronunciation_sha={self.source_sha}\n"
            f"echo_source_sha={self.source_sha}\n"
            f"renderer_manifest_sha256={self.renderer_manifest_sha}\n"
            f"echo_cli_sha256={cli_sha}\n"
            f"echo_cli_path={self.cli}\n"
            f"echo_resources_sha256={resources_sha}\n"
            f"echo_resource_dir={self.resources}\n"
            "render_version=12\n"
            f"model_policy_revision={self.model_policy_revision}\n"
            f"model_expected_byte_count={self.model_expected_byte_count}\n"
            "model_bytes_attested=false\n"
            "voice=am_michael\n"
            f"chapter_voices={chapter_voices}\n"
            f"voice_plan_sha256={voice_plan_sha}\n"
            f"voice_plan_id={voice_plan_id}\n"
            f"epub_sha256={epub_sha}\n"
            "cover_binding_mode=receipt-free-private\n"
            "cover_selection_path=\n"
            "cover_selection_sha256=\n"
            f"portrait_cover_path={self.portrait}\n"
            f"portrait_cover_sha256={cover_sha}\n"
            f"m4b_cover_path={self.square}\n"
            f"m4b_cover_sha256={m4b_cover_sha}\n"
            "run_lane=audiobook\n"
            f"run_root={self.run_root}\n"
            f"package_sha256={package_sha}\n"
            f"run_id={run_id}\n"
            f"work_dir={self.run_root / f'audio-work-{run_id}'}\n"
            f"narration_db={self.run_root / f'narration-{run_id}.sqlite'}\n"
        ).encode("utf-8")
        return run_id, receipt

    def expected_legacy_state_and_success_receipts(
        self,
        *,
        run_id: str,
        input_receipt: bytes,
        voice_plan_sha: str,
        chapter_voices: dict[str, str],
        capture_voice: str,
        attempt_id: str,
    ) -> tuple[bytes, bytes]:
        """Hand-built schema-3 goldens for the unchanged legacy wire format."""
        epub = self.run_root / "dist" / "fixture.epub"
        epub_bytes = epub.read_bytes()
        source_epub_sha = hashlib.sha256(epub_bytes).hexdigest()

        def frame(value: str) -> bytes:
            encoded = value.encode("utf-8")
            return str(len(encoded)).encode("ascii") + b":" + encoded

        source_fingerprint = hashlib.sha256(
            frame("source-kind=epub")
            + frame(f"bytes={len(epub_bytes)}")
            + epub_bytes
        ).hexdigest()
        cli_sha = hashlib.sha256(self.cli.read_bytes()).hexdigest()
        resources_sha, _ = resource_tree_identity(self.resources)
        renderer_identity = {
            "rendererSchemaVersion": 1,
            "rendererRoot": str(self.renderer_root),
            "rendererBuildRoot": str(self.renderer_build_root),
            "installerSourceSHA": self.installer_source_sha,
            "echoSourceSHA": self.source_sha,
            "rendererManifestSHA256": self.renderer_manifest_sha,
            "echoCLI_SHA256": cli_sha,
            "echoResourcesSHA256": resources_sha,
            "echoRenderVersion": 12,
            "modelPolicyRevision": self.model_policy_revision,
            "modelExpectedByteCount": self.model_expected_byte_count,
            "modelBytesAttested": False,
        }
        capture_payload = {
            "duration": 1.0,
            "anchors": [],
            "pronunciationEvidence": {"decisions": [], "diagnostics": []},
        }
        capture_payload_bytes = json.dumps(
            capture_payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        capture_audio = b"fixture chapter audio"
        marker_payload = {
            **capture_payload,
            "identity": {
                "schemaVersion": 1,
                "captureSetID": "c" * 64,
                "sourceFingerprint": source_fingerprint,
                "voice": capture_voice,
                "renderVersion": 12,
                "rendererIdentity": "fixture-renderer",
                "normalizationMode": "spoken",
                "chapterIndex": 0,
                "chapterContentSignature": "d" * 16,
                "audioFileName": "chapter-0.m4a",
                "audioFileByteCount": len(capture_audio),
                "audioSHA256": hashlib.sha256(capture_audio).hexdigest(),
                "payloadSHA256": hashlib.sha256(capture_payload_bytes).hexdigest(),
            },
        }
        marker_bytes = json.dumps(
            marker_payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        state_payload = {
            "schemaVersion": 3,
            **renderer_identity,
            "sourceFingerprint": source_fingerprint,
            "voice": "am_michael",
            "chapterVoices": chapter_voices,
            "voicePlanSHA256": voice_plan_sha,
            "renderVersion": 12,
            "captureSetID": "c" * 64,
            "inputReceiptSHA256": hashlib.sha256(input_receipt).hexdigest(),
            "databaseSHA256": hashlib.sha256(b"fixture database").hexdigest(),
            "databaseByteCount": len(b"fixture database"),
            "captures": [
                {
                    "chapterIndex": 0,
                    "markerFileName": ".anchors-ch0.json",
                    "markerSHA256": hashlib.sha256(marker_bytes).hexdigest(),
                    "audioFileName": "chapter-0.m4a",
                    "audioSHA256": hashlib.sha256(capture_audio).hexdigest(),
                    "payloadSHA256": hashlib.sha256(capture_payload_bytes).hexdigest(),
                }
            ],
        }
        state_bytes = canonical_json(state_payload)
        attempt_payload = {
            "schemaVersion": 2,
            "attemptID": attempt_id,
            "runID": run_id,
            "inputReceiptFileName": f"echo-render-inputs-{run_id}.env",
            "inputReceiptSHA256": hashlib.sha256(input_receipt).hexdigest(),
            "sourceEPUBFileName": epub.name,
            "sourceEPUBSHA256": source_epub_sha,
            "artifactRelativePath": f"echo-renders/{run_id}/{attempt_id}",
            **renderer_identity,
        }
        attempt_bytes = canonical_json(attempt_payload)
        audiobook = b"fixture audiobook bytes"
        sidecar = b"{}\n"
        audit_payload = {
            "schemaVersion": 6,
            "renderVersion": 12,
            "voice": capture_voice,
            "chapterVoices": {"0": capture_voice},
            "coverage": "complete",
            "watchCounts": {
                word: 0 for word in LEGACY_FIXTURE_WATCH_WORDS
            },
            "decisions": [],
            "diagnostics": [],
            "legacyChapterIndexes": [],
            "audiobookFileName": "fixture.m4b",
            "audiobookSHA256": hashlib.sha256(audiobook).hexdigest(),
        }
        audit = json.dumps(audit_payload).encode("utf-8")
        success_payload = {
            "schemaVersion": 3,
            **renderer_identity,
            "attemptID": attempt_id,
            "runID": run_id,
            "attemptReceiptSHA256": hashlib.sha256(attempt_bytes).hexdigest(),
            "inputReceiptFileName": f"echo-render-inputs-{run_id}.env",
            "inputReceiptSHA256": hashlib.sha256(input_receipt).hexdigest(),
            "sourceEPUBFileName": epub.name,
            "sourceEPUBSHA256": source_epub_sha,
            "artifactRelativePath": f"echo-renders/{run_id}/{attempt_id}",
            "resumeStateFileName": f"echo-resume-state-{run_id}.json",
            "resumeStateSHA256": hashlib.sha256(state_bytes).hexdigest(),
            "audiobookFileName": "fixture.m4b",
            "audiobookSHA256": hashlib.sha256(audiobook).hexdigest(),
            "sidecarFileName": "fixture.alignment.json",
            "sidecarSHA256": hashlib.sha256(sidecar).hexdigest(),
            "auditFileName": "fixture.pronunciation-audit.json",
            "auditSHA256": hashlib.sha256(audit).hexdigest(),
        }
        return state_bytes, canonical_json(success_payload)

    def use_run_lane(self, folder: str) -> None:
        destination = self.explainer / ".build" / folder / "fixture"
        destination.parent.mkdir(parents=True, exist_ok=True)
        self.run_root.rename(destination)
        self.run_root = destination

    def run_preflight(
        self,
        *,
        environment: dict[str, str] | None = None,
        body: str = "echo_pronunciation_preflight",
    ) -> subprocess.CompletedProcess[str]:
        command = (
            "set -euo pipefail\n" f"source {shlex.quote(str(PREFLIGHT))}\n" f"{body}\n"
        )
        return subprocess.run(
            [
                str(LEASE_HELPER),
                "--lock-root",
                str(self.lease_root),
                "--resource",
                str(self.renderer_build_root),
                "--",
                "bash",
                "-c",
                command,
            ],
            cwd=self.explainer,
            env=environment or self.environment(),
            capture_output=True,
            text=True,
        )

    def run_narrate(
        self,
        *arguments: str,
        environment: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(NARRATE_WRAPPER), *arguments],
            cwd=self.explainer,
            env=environment or self.environment(),
            capture_output=True,
            text=True,
        )

    def run_narrate_with_resolver_payload(
        self, payload: bytes
    ) -> tuple[subprocess.CompletedProcess[str], Path]:
        scripts = self.tmp / f"resolver-payload-{len(list(self.tmp.glob('resolver-payload-*')))}"
        scripts.mkdir()
        wrapper = scripts / NARRATE_WRAPPER.name
        wrapper.write_bytes(NARRATE_WRAPPER.read_bytes())
        wrapper.chmod(wrapper.stat().st_mode | stat.S_IXUSR)
        (scripts / PREFLIGHT.name).write_bytes(PREFLIGHT.read_bytes())
        (scripts / "echo_installed_renderer.py").write_text(
            "import sys\n" f"sys.stdout.buffer.write({payload!r})\n",
            encoding="utf-8",
        )
        lease_marker = scripts / "lease-invoked"
        lease = scripts / "echo_pronunciation_lease.py"
        lease.write_text(
            "#!/usr/bin/env bash\n"
            f"touch {shlex.quote(str(lease_marker))}\n"
            "exit 99\n",
            encoding="utf-8",
        )
        lease.chmod(lease.stat().st_mode | stat.S_IXUSR)
        environment = self.environment()
        return (
            subprocess.run(
                [str(wrapper)],
                cwd=self.explainer,
                env=environment,
                capture_output=True,
                text=True,
            ),
            lease_marker,
        )

    @staticmethod
    def valid_renderer_env0() -> bytes:
        values = {
            "ECHO_RENDERER_ROOT": "/installed",
            "ECHO_RENDERER_BUILD_ROOT": "/installed/build",
            "ECHO_RENDERER_MANIFEST": "/installed/build/renderer-manifest.json",
            "ECHO_RENDERER_MANIFEST_SHA256": "1" * 64,
            "APPROVED_ECHO_INSTALLER_SHA": "2" * 40,
            "ECHO_SOURCE_SHA": ACCEPTED_SOURCE_SHA,
            "CLI": "/installed/build/echo-cli",
            "ECHO_CLI_SHA256": "3" * 64,
            "ECHO_RESOURCE_DIR": "/installed/build/EchoNarrationResources",
            "ECHO_RESOURCES_SHA256": "4" * 64,
            "ECHO_RENDER_VERSION": "12",
            "ECHO_MODEL_REVISION": "fixture",
            "ECHO_MODEL_EXPECTED_BYTES": "1",
            "ECHO_MODEL_BYTES_ATTESTED": "false",
        }
        return b"".join(
            key.encode() + b"\0" + value.encode() + b"\0"
            for key, value in values.items()
        )

    def select_manifest_variant(
        self,
        mutate: Callable[[dict[str, object]], None],
        *,
        render_version: int = 12,
        include_review_flag: bool = True,
    ) -> tuple[Path, str]:
        staging = self.renderer_root / self.source_sha / ("e" * 64)
        cli = staging / "echo-cli"
        resources = staging / "EchoNarrationResources"
        resources.mkdir(parents=True)
        self.write_cli(
            include_review_flag=include_review_flag,
            render_version=render_version,
            cli=cli,
            resources=resources,
        )
        payload = copy.deepcopy(self.manifest_payload)
        payload["executable"] = {
            "sha256": hashlib.sha256(cli.read_bytes()).hexdigest(),
            "byteCount": cli.stat().st_size,
        }
        resources_sha, resources_count = resource_tree_identity(resources)
        payload["resources"] = {
            "sha256": resources_sha,
            "regularFileCount": resources_count,
        }
        mutate(payload)
        manifest_data = canonical_json(payload)
        manifest_sha = hashlib.sha256(manifest_data).hexdigest()
        (staging / "renderer-manifest.json").write_bytes(manifest_data)
        build_root = self.renderer_root / self.source_sha / manifest_sha
        staging.rename(build_root)
        (self.renderer_root / self.source_sha / "approved-renderer.json").write_bytes(
            canonical_json(
                {
                    "schemaVersion": 1,
                    "echoSourceSHA": self.source_sha,
                    "manifestSHA256": manifest_sha,
                }
            )
        )
        return build_root, manifest_sha

    def resume_arguments(self) -> tuple[str, str, str]:
        state = next(
            (self.run_root / "research").glob("echo-resume-state-*.json")
        )
        return ("--resume", "--resume-state", str(state))

    def write_public_pair_receipt(self) -> Path:
        receipt = self.pair / "cover-selection.json"
        payload = copy.deepcopy(self.cover_selection_payload)
        payload["privacy"] = {
            "classification": "public-safe",
            "permission_to_publish": True,
        }
        receipt.write_text(
            json.dumps(payload, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return receipt

    def test_ordinary_wrapper_observes_no_build_or_checkout_descendants(self) -> None:
        forbidden_log = self.tmp / "forbidden-descendants.log"
        for command in ("make", "git", "xcodebuild", "xcode-build-gate.sh"):
            sentinel = self.fake_bin / command
            sentinel.write_text(
                "#!/usr/bin/env bash\n"
                f"printf '%s\\n' {shlex.quote(command)} >>"
                f"{shlex.quote(str(forbidden_log))}\n"
                "exit 97\n",
                encoding="utf-8",
            )
            sentinel.chmod(sentinel.stat().st_mode | stat.S_IXUSR)

        result = self.run_narrate()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertFalse(forbidden_log.exists(), forbidden_log.read_text() if forbidden_log.exists() else "")

    def test_missing_installed_version_is_actionable_and_does_not_build(self) -> None:
        missing_source = "a" * 40
        environment = self.environment()
        environment["ECHO_SOURCE_SHA"] = missing_source
        environment["APPROVED_ECHO_PRONUNCIATION_SHA"] = missing_source

        result = self.run_narrate(environment=environment)

        self.assertEqual(65, result.returncode)
        self.assertIn("install the approved Echo renderer", result.stderr)
        self.assertIn(missing_source, result.stderr)

    def test_invalid_selector_reports_the_selector_failure(self) -> None:
        selector = self.renderer_root / self.source_sha / "approved-renderer.json"
        selector.write_text('{"schemaVersion":1}\n', encoding="utf-8")
        result = self.run_narrate()
        self.assertEqual(65, result.returncode)
        self.assertIn("renderer selector", result.stderr)

    def test_corrupt_manifest_reports_manifest_bytes(self) -> None:
        manifest = self.renderer_build_root / "renderer-manifest.json"
        manifest.write_bytes(manifest.read_bytes() + b" ")
        result = self.run_narrate()
        self.assertEqual(65, result.returncode)
        self.assertIn("manifest bytes", result.stderr)

    def test_changed_executable_reports_executable_identity(self) -> None:
        self.cli.write_bytes(self.cli.read_bytes() + b"# changed\n")
        result = self.run_narrate()
        self.assertEqual(65, result.returncode)
        self.assertIn("executable identity", result.stderr)

    def test_changed_resources_report_resource_identity(self) -> None:
        (self.resources / "changed.bin").write_bytes(b"changed")
        result = self.run_narrate()
        self.assertEqual(65, result.returncode)
        self.assertIn("resource identity", result.stderr)

    def test_incompatible_nonrelease_manifest_is_distinct(self) -> None:
        self.select_manifest_variant(
            lambda payload: payload.__setitem__("buildConfiguration", "Debug")
        )
        result = self.run_narrate()
        self.assertEqual(65, result.returncode)
        self.assertIn("buildConfiguration must be Release", result.stderr)

    def test_incompatible_live_version_is_distinct(self) -> None:
        self.select_manifest_variant(
            lambda payload: payload.__setitem__("renderVersion", 13),
            render_version=12,
        )
        result = self.run_narrate()
        self.assertEqual(65, result.returncode)
        self.assertIn("live render version", result.stderr)

    def test_incompatible_architecture_is_distinct(self) -> None:
        other = "x86_64" if (platform.machine() or "arm64") != "x86_64" else "arm64"
        self.select_manifest_variant(
            lambda payload: payload.__setitem__("architectures", [other])
        )
        result = self.run_narrate()
        self.assertEqual(65, result.returncode)
        self.assertIn("current host architecture", result.stderr)

    def test_incompatible_macos_floor_is_distinct(self) -> None:
        self.select_manifest_variant(
            lambda payload: payload.__setitem__("minimumMacOSVersion", "999.0")
        )
        result = self.run_narrate()
        self.assertEqual(65, result.returncode)
        self.assertIn("newer macOS", result.stderr)

    def test_incompatible_capabilities_are_distinct(self) -> None:
        self.select_manifest_variant(
            lambda payload: payload["capabilities"].append("--impossible")
        )
        result = self.run_narrate()
        self.assertEqual(65, result.returncode)
        self.assertIn("live capabilities", result.stderr)

    @staticmethod
    def renderer_state_arguments(identity: dict[str, object]) -> tuple[str, ...]:
        return (
            "--renderer-schema-version",
            str(identity["rendererSchemaVersion"]),
            "--renderer-root",
            str(identity["rendererRoot"]),
            "--renderer-build-root",
            str(identity["rendererBuildRoot"]),
            "--installer-source-sha",
            str(identity["installerSourceSHA"]),
            "--echo-source-sha",
            str(identity["echoSourceSHA"]),
            "--renderer-manifest-sha256",
            str(identity["rendererManifestSHA256"]),
            "--echo-cli-sha256",
            str(identity["echoCLI_SHA256"]),
            "--echo-resources-sha256",
            str(identity["echoResourcesSHA256"]),
            "--echo-render-version",
            str(identity["echoRenderVersion"]),
            "--model-policy-revision",
            str(identity["modelPolicyRevision"]),
            "--model-expected-byte-count",
            str(identity["modelExpectedByteCount"]),
            "--model-bytes-attested",
            "false" if identity["modelBytesAttested"] is False else "true",
        )

    def test_does_not_publish_after_resource_mutation(self) -> None:
        ready = self.tmp / "narrate-ready"
        release = self.tmp / "narrate-release"
        environment = self.environment()
        environment.update(
            {
                "FAKE_NARRATE_READY": str(ready),
                "FAKE_NARRATE_RELEASE": str(release),
            }
        )
        process = subprocess.Popen(
            [str(NARRATE_WRAPPER)],
            cwd=self.explainer,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.addCleanup(lambda: process.poll() is None and process.kill())
        self.wait_for_path(ready, process)
        (self.resources / "pronunciations.json").write_text(
            '{"renderVersion":13}\n', encoding="utf-8"
        )
        release.touch()

        stdout, stderr = process.communicate(timeout=WAIT_TIMEOUT)

        self.assertEqual(65, process.returncode, f"{stdout}\n{stderr}")
        self.assertIn("installed renderer attestation failed", stderr)
        self.assertFalse(list((self.run_root / "dist").glob("echo-renders/**/*")))
        self.assertFalse(list(self.run_root.glob(".echo-output-*")))

    def test_rejects_executable_and_resource_mutation_before_cli_launch(
        self,
    ) -> None:
        control = self.tmp / "probe-block-control"
        ready = self.tmp / "probe-block-ready"
        release = self.tmp / "probe-block-release"
        narrate_log = self.tmp / "prelaunch-narrate.log"
        control.write_text("2\n", encoding="utf-8")
        environment = self.environment()
        environment.update(
            {
                "FAKE_NARRATE_LOG": str(narrate_log),
            }
        )
        process = subprocess.Popen(
            [str(NARRATE_WRAPPER)],
            cwd=self.explainer,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.addCleanup(lambda: process.poll() is None and process.kill())
        self.wait_for_path(ready, process)

        (self.resources / "pronunciations.json").write_text(
            '{"renderVersion":13}\n', encoding="utf-8"
        )
        with self.cli.open("a", encoding="utf-8") as executable:
            executable.write("\n# mutated before narration launch\n")
        release.touch()
        stdout, stderr = process.communicate(timeout=WAIT_TIMEOUT)

        self.assertEqual(65, process.returncode, f"{stdout}\n{stderr}")
        narrate_calls = (
            narrate_log.read_text(encoding="utf-8").count("BEGIN=")
            if narrate_log.exists()
            else 0
        )
        self.assertEqual(0, narrate_calls, "mutated package reached CLI narration")
        self.assertFalse(list((self.run_root / "dist").glob("echo-renders/**/*")))
        self.assertFalse(list(self.run_root.glob(".echo-output-*")))

    def test_full_wrapper_holds_the_exact_build_root_lease_through_narration(
        self,
    ) -> None:
        ready = self.tmp / "full-build-lease-ready"
        release = self.tmp / "full-build-lease-release"
        environment = self.environment()
        environment.update(
            {
                "FAKE_NARRATE_READY": str(ready),
                "FAKE_NARRATE_RELEASE": str(release),
            }
        )
        process = subprocess.Popen(
            [str(NARRATE_WRAPPER)],
            cwd=self.explainer,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.addCleanup(lambda: process.poll() is None and process.kill())
        self.wait_for_path(ready, process)

        contender = subprocess.run(
            [
                str(LEASE_HELPER),
                "--lock-root",
                str(self.lease_root),
                "--resource",
                str(self.renderer_build_root),
                "--",
                "/usr/bin/true",
            ],
            cwd=self.explainer,
            env=self.environment(),
            capture_output=True,
            text=True,
        )
        self.assertEqual(75, contender.returncode, contender.stderr)
        self.assertIn(
            f"active narration lease owns shared resource: {self.renderer_build_root}",
            contender.stderr,
        )

        release.touch()
        stdout, stderr = process.communicate(timeout=WAIT_TIMEOUT)
        self.assertEqual(0, process.returncode, f"{stdout}\n{stderr}")

    def preflight_fields(self) -> dict[str, str]:
        names = (
            "EXPLAINER_ROOT",
            "APPROVED_ECHO_PRONUNCIATION_SHA",
            "ECHO_SOURCE_SHA",
            "EPUB",
            "EPUB_SHA256",
            "COVER_BINDING_MODE",
            "COVER_SELECTION",
            "COVER_SELECTION_SHA256",
            "COVER",
            "COVER_SHA256",
            "M4B_COVER",
            "M4B_COVER_SHA256",
            "PACKAGE_SHA256",
            "CLI",
            "ECHO_CLI_SHA256",
            "ECHO_RESOURCE_DIR",
            "ECHO_RESOURCES_SHA256",
            "ECHO_RENDER_VERSION",
            "ECHO_RENDERER_ROOT",
            "ECHO_RENDERER_BUILD_ROOT",
            "ECHO_RENDERER_MANIFEST",
            "ECHO_RENDERER_MANIFEST_SHA256",
            "APPROVED_ECHO_INSTALLER_SHA",
            "ECHO_MODEL_REVISION",
            "ECHO_MODEL_EXPECTED_BYTES",
            "ECHO_MODEL_BYTES_ATTESTED",
            "VOICE",
            "CHAPTER_VOICES_CANONICAL",
            "VOICE_PLAN_SHA256",
            "VOICE_PLAN_ID",
            "RUN_ID",
            "WORK",
            "DB",
            "ECHO_RENDER_INPUT_RECEIPT",
        )
        body_lines = ["echo_pronunciation_preflight"]
        for name in names:
            body_lines.append(f'printf "{name}=%s\\n" "${{{name}}}"')
        body = "\n".join(body_lines)
        result = self.run_preflight(body=body)
        self.assertEqual(0, result.returncode, result.stderr)
        return dict(
            line.split("=", 1)
            for line in result.stdout.splitlines()
            if line.split("=", 1)[0] in names
        )

    def test_private_pair_preflight_is_receipt_free_and_hash_bound(self) -> None:
        root_receipt = self.run_root / "dist" / "cover-selection.json"

        fields = self.preflight_fields()

        self.assertEqual("receipt-free-private", fields["COVER_BINDING_MODE"])
        self.assertEqual("", fields["COVER_SELECTION"])
        self.assertEqual("", fields["COVER_SELECTION_SHA256"])
        self.assertFalse(root_receipt.exists())
        self.assertEqual(
            hashlib.sha256(Path(fields["EPUB"]).read_bytes()).hexdigest(),
            fields["EPUB_SHA256"],
        )
        self.assertEqual(
            hashlib.sha256(Path(fields["COVER"]).read_bytes()).hexdigest(),
            fields["COVER_SHA256"],
        )
        self.assertEqual(
            hashlib.sha256(Path(fields["M4B_COVER"]).read_bytes()).hexdigest(),
            fields["M4B_COVER_SHA256"],
        )

        Path(fields["M4B_COVER"]).write_bytes(b"changed after preflight")
        result = self.run_direct_leased(fields)
        self.assertEqual(65, result.returncode)
        self.assertIn(
            "selected cover package changed while narration lease was held",
            result.stderr,
        )

    def test_public_pair_preflight_infers_receipt_beside_selected_pair(self) -> None:
        root_receipt = self.run_root / "dist" / "cover-selection.json"
        pair_receipt = self.write_public_pair_receipt()

        fields = self.preflight_fields()

        self.assertEqual("paired-receipt", fields["COVER_BINDING_MODE"])
        self.assertEqual(str(pair_receipt), fields["COVER_SELECTION"])
        self.assertEqual(
            hashlib.sha256(pair_receipt.read_bytes()).hexdigest(),
            fields["COVER_SELECTION_SHA256"],
        )
        self.assertFalse(root_receipt.exists())

    def test_state_helper_accepts_current_run_id_and_rejects_legacy_shape(self) -> None:
        current = "-".join(
            ["1" * 12, "2" * 12, "3" * 12, "4" * 12, "5" * 40, "am_michael"]
        )
        legacy = "-".join(
            ["1" * 12, "2" * 12, "3" * 12, "5" * 40, "am_michael"]
        )

        accepted = subprocess.run(
            ["/usr/local/bin/python3", str(STATE_HELPER), "validate-run-id", current],
            capture_output=True,
            text=True,
        )
        rejected = subprocess.run(
            ["/usr/local/bin/python3", str(STATE_HELPER), "validate-run-id", legacy],
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, accepted.returncode, accepted.stderr)
        self.assertNotEqual(0, rejected.returncode)

    def run_direct_leased(
        self,
        fields: dict[str, str],
        *,
        environment: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        direct_environment = environment or self.environment()
        direct_environment.update(fields)
        dist = self.run_root / "dist"
        output = dist / "fixture.m4b"
        sidecar = dist / "fixture.alignment.json"
        audit = dist / "fixture.pronunciation-audit.json"
        reel = dist / "fixture.pronunciation-reel.m4b"
        direct_environment.update(
            {
                "OUTPUT": str(output),
                "SIDECAR": str(sidecar),
                "AUDIT": str(audit),
                "REEL": str(reel),
                "DIST": str(dist),
                "OWNER_FILE": str(
                    self.run_root / "research" / "echo-render-output.owner.env"
                ),
                "STATE_RECEIPT": str(
                    self.run_root
                    / "research"
                    / f"echo-resume-state-{fields['RUN_ID']}.json"
                ),
                "SUCCESS_RECEIPT": str(
                    self.run_root
                    / "research"
                    / f"echo-render-success-{fields['RUN_ID']}.json"
                ),
                "STAGE": str(self.run_root / ".untrusted-stage"),
            }
        )
        command = [
            str(LEASE_HELPER),
            "--lock-root",
            str(self.lease_root),
        ]
        for resource in (
            self.renderer_build_root,
            output,
            sidecar,
            audit,
            reel,
            Path(fields["WORK"]),
            Path(fields["DB"]),
        ):
            command.extend(("--resource", str(resource)))
        command.extend(("--", str(NARRATE_WRAPPER), "--leased-run"))
        return subprocess.run(
            command,
            cwd=self.explainer,
            env=direct_environment,
            capture_output=True,
            text=True,
        )

    @staticmethod
    def wait_for_path(path: Path, process: subprocess.Popen[str]) -> None:
        deadline = time.monotonic() + WAIT_TIMEOUT
        while time.monotonic() < deadline:
            if path.exists():
                return
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                raise AssertionError(
                    f"process exited before {path} appeared: {stdout=} {stderr=}"
                )
            time.sleep(0.05)
        raise AssertionError(f"timed out waiting for {path} after {WAIT_TIMEOUT}s")

    def test_valid_preflight_preserves_cwd_and_records_provenance(self) -> None:
        result = self.run_preflight(
            body=(
                'before="$PWD"\n'
                "echo_pronunciation_preflight\n"
                'printf "before=%s\\nafter=%s\\nrun_id=%s\\nreceipt=%s\\n" '
                '"$before" "$PWD" "$RUN_ID" "$ECHO_RENDER_INPUT_RECEIPT"'
            )
        )
        self.assertEqual(0, result.returncode, result.stderr)
        resolved_explainer = self.explainer.resolve()
        self.assertIn(f"before={resolved_explainer}", result.stdout)
        self.assertIn(f"after={resolved_explainer}", result.stdout)
        self.assertRegex(result.stdout, r"run_id=[0-9a-f-]+-am_michael")

        receipt_match = re.search(r"receipt=(.+)", result.stdout)
        self.assertIsNotNone(receipt_match)
        receipt = Path(receipt_match.group(1))
        fields = dict(
            line.split("=", 1)
            for line in receipt.read_text(encoding="utf-8").splitlines()
        )
        self.assertEqual(self.source_sha, fields["approved_echo_pronunciation_sha"])
        self.assertEqual(self.source_sha, fields["echo_source_sha"])
        self.assertRegex(fields["epub_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(fields["echo_cli_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(fields["echo_resources_sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(str(self.resources.resolve()), fields["echo_resource_dir"])
        self.assertEqual("12", fields["render_version"])

    def test_preflight_accepts_and_binds_newer_release_render_version(self) -> None:
        _, manifest_sha = self.select_manifest_variant(
            lambda payload: payload.__setitem__("renderVersion", 13),
            render_version=13,
        )
        result = self.run_narrate()
        self.assertEqual(0, result.returncode, result.stderr)
        receipt = next((self.run_root / "research").glob("echo-render-inputs-*.env"))
        fields = dict(
            line.split("=", 1)
            for line in receipt.read_text(encoding="utf-8").splitlines()
        )
        self.assertEqual("13", fields["render_version"])
        self.assertEqual(manifest_sha, fields["renderer_manifest_sha256"])

    def test_standalone_preflight_rejects_without_renderer_lease(self) -> None:
        command = f"source {shlex.quote(str(PREFLIGHT))}; echo_pronunciation_preflight"
        result = subprocess.run(
            ["bash", "-c", command],
            cwd=self.explainer,
            env=self.environment(),
            capture_output=True,
            text=True,
        )
        self.assertEqual(70, result.returncode)
        self.assertIn("requires the inherited renderer lease", result.stderr)

    def test_preflight_requires_the_exact_reviewed_echo_source(self) -> None:
        environment = self.environment()
        environment["APPROVED_ECHO_PRONUNCIATION_SHA"] = "a" * 40
        result = self.run_preflight(environment=environment)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("must exactly equal installed source", result.stderr)

    def test_preflight_rejects_mismatched_receipt_or_unreceipted_capture(self) -> None:
        result = self.run_preflight(
            body=(
                "echo_pronunciation_preflight\n"
                'printf "work=%s\\nreceipt=%s\\n" '
                '"$WORK" "$ECHO_RENDER_INPUT_RECEIPT"'
            )
        )
        self.assertEqual(0, result.returncode, result.stderr)
        fields = dict(
            line.split("=", 1)
            for line in result.stdout.splitlines()
            if line.startswith(("work=", "receipt="))
        )
        receipt = Path(fields["receipt"])
        receipt.write_text("approved_echo_pronunciation_sha=wrong\n", encoding="utf-8")

        mismatch = self.run_preflight()
        self.assertNotEqual(0, mismatch.returncode)
        self.assertIn("existing render-input receipt does not match", mismatch.stderr)

        receipt.unlink()
        Path(fields["work"]).mkdir(parents=True)
        unreceipted = self.run_preflight()
        self.assertNotEqual(0, unreceipted.returncode)
        self.assertIn(
            "pre-existing WORK or DB requires a matching receipt", unreceipted.stderr
        )

    def test_preflight_accepts_matching_receipt_for_resume_paths(self) -> None:
        result = self.run_preflight(
            body=(
                "echo_pronunciation_preflight\n"
                'printf "receipt=%s\\n" "$ECHO_RENDER_INPUT_RECEIPT"'
            )
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("receipt=", result.stdout)

    def test_preflight_rejects_a_missing_approval(self) -> None:
        environment = self.environment()
        environment.pop("APPROVED_ECHO_PRONUNCIATION_SHA")
        result = self.run_preflight(environment=environment)
        self.assertEqual(64, result.returncode)
        self.assertIn("APPROVED_ECHO_PRONUNCIATION_SHA is required", result.stderr)

    def test_new_and_resume_require_an_explicit_approval(self) -> None:
        missing_new = self.environment()
        missing_new.pop("APPROVED_ECHO_PRONUNCIATION_SHA")
        new_result = self.run_narrate(environment=missing_new)
        self.assertEqual(64, new_result.returncode)
        self.assertIn("APPROVED_ECHO_PRONUNCIATION_SHA is required", new_result.stderr)

        initial = self.run_narrate()
        self.assertEqual(0, initial.returncode, initial.stderr)
        missing_resume = self.environment()
        missing_resume.pop("APPROVED_ECHO_PRONUNCIATION_SHA")
        resume_result = self.run_narrate(
            *self.resume_arguments(), environment=missing_resume
        )
        self.assertEqual(64, resume_result.returncode)
        self.assertIn(
            "APPROVED_ECHO_PRONUNCIATION_SHA is required", resume_result.stderr
        )

    def test_env0_rejects_partial_and_odd_trailing_records(self) -> None:
        valid = self.valid_renderer_env0()
        for suffix in (b"EXTRA_UNTERMINATED", b"EXTRA_WITHOUT_VALUE\0"):
            with self.subTest(suffix=suffix):
                result, lease_marker = self.run_narrate_with_resolver_payload(
                    valid + suffix
                )
                self.assertEqual(65, result.returncode)
                self.assertIn("incomplete installed renderer env0 record", result.stderr)
                self.assertFalse(lease_marker.exists())

    def test_preflight_does_not_consult_an_echo_checkout(self) -> None:
        (self.echo / "dirty-marker.txt").write_text("uncommitted\n", encoding="utf-8")
        result = self.run_narrate()
        self.assertEqual(0, result.returncode, result.stderr)

    def test_installed_source_pin_is_independent_of_checkout_dirt(self) -> None:
        environment = self.environment()
        (self.echo / "dirty-marker.txt").write_text("uncommitted\n", encoding="utf-8")
        result = self.run_narrate(environment=environment)
        self.assertEqual(0, result.returncode, result.stderr)

    def test_preflight_rejects_symbolic_approval(self) -> None:
        environment = self.environment()
        environment["APPROVED_ECHO_PRONUNCIATION_SHA"] = "HEAD"
        result = self.run_preflight(environment=environment)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("40 lowercase hexadecimal", result.stderr)

    def test_preflight_rejects_unapproved_source_revision(self) -> None:
        environment = self.environment()
        environment["APPROVED_ECHO_PRONUNCIATION_SHA"] = "a" * 40
        environment["ECHO_SOURCE_SHA"] = "a" * 40
        result = self.run_narrate(environment=environment)
        self.assertEqual(65, result.returncode)
        self.assertIn("renderer source directory", result.stderr)

    def test_preflight_rejects_unsafe_slug_and_run_root(self) -> None:
        for slug in ("../escape", "Fixture", "fixture/other"):
            with self.subTest(slug=slug):
                environment = self.environment()
                environment["SLUG"] = slug
                result = self.run_preflight(environment=environment)
                self.assertNotEqual(0, result.returncode)
                self.assertIn("SLUG", result.stderr)

        environment = self.environment()
        environment["RUN_ROOT"] = str(self.tmp / "outside" / "fixture")
        result = self.run_preflight(environment=environment)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("canonical run path", result.stderr)

    def test_internal_modes_reject_a_forged_environment_capability(self) -> None:
        environment = self.environment()
        environment["ECHO_PRONUNCIATION_LEASE_HELD"] = "1"
        result = self.run_narrate("--leased-run", environment=environment)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("inherited FD-backed lease capability", result.stderr)

        environment["ECHO_PRONUNCIATION_LEASE_CAPABILITY"] = json.dumps(
            {str(self.renderer_build_root): 1}
        )
        forged_fd = self.run_narrate("--leased-preflight", environment=environment)
        self.assertNotEqual(0, forged_fd.returncode)
        self.assertIn("inherited FD-backed lease capability", forged_fd.stderr)

    def test_direct_leased_run_rechecks_exact_approval_and_release_version(
        self,
    ) -> None:
        fields = self.preflight_fields()
        receipt = Path(fields["ECHO_RENDER_INPUT_RECEIPT"])
        receipt_text = receipt.read_text(encoding="utf-8")
        wrong_source = "a" * 40
        fields["APPROVED_ECHO_PRONUNCIATION_SHA"] = wrong_source
        receipt.write_text(
            receipt_text.replace(self.source_sha, wrong_source, 1),
            encoding="utf-8",
        )
        unapproved = self.run_direct_leased(fields)
        self.assertNotEqual(0, unapproved.returncode)
        self.assertIn("does not match installed source", unapproved.stderr)

    def test_preflight_ignores_dirty_echo_source(self) -> None:
        (self.echo / "revision.txt").write_text("uncommitted\n", encoding="utf-8")
        result = self.run_preflight()
        self.assertEqual(0, result.returncode, result.stderr)

    def test_preflight_rejects_missing_or_invalid_sha256_output(self) -> None:
        environment = self.environment()
        environment["ECHO_CLI_SHA256"] = "not-a-sha"
        result = self.run_preflight(environment=environment)
        self.assertEqual(64, result.returncode)
        self.assertIn("64 lowercase hexadecimal", result.stderr)

    def test_preflight_rejects_cli_without_review_flag(self) -> None:
        self.select_manifest_variant(lambda payload: None, include_review_flag=False)
        result = self.run_narrate()
        self.assertEqual(65, result.returncode)
        self.assertIn("live capabilities", result.stderr)

    def test_preflight_rejects_pre_v12_release_cli(self) -> None:
        self.select_manifest_variant(
            lambda payload: payload.__setitem__("renderVersion", 11),
            render_version=11,
        )
        result = self.run_narrate()
        self.assertEqual(64, result.returncode)
        self.assertIn("at least 12", result.stderr)

    def test_narration_wrapper_uses_exact_content_addressed_paths(self) -> None:
        log = self.tmp / "narrate.log"
        environment = self.environment()
        environment["FAKE_NARRATE_LOG"] = str(log)

        result = self.run_narrate(environment=environment)

        self.assertEqual(0, result.returncode, result.stderr)
        arguments = [
            line.removeprefix("ARG=")
            for line in log.read_text(encoding="utf-8").splitlines()
            if line.startswith("ARG=")
        ]
        staged_output = next(
            argument
            for index, argument in enumerate(arguments)
            if arguments[index - 1] == "--out"
        )
        staged_sidecar = next(
            argument
            for index, argument in enumerate(arguments)
            if arguments[index - 1] == "--sidecar"
        )
        self.assertRegex(
            staged_output,
            rf"^{re.escape(str(self.run_root))}/\.echo-output-.+/fixture\.m4b$",
        )
        self.assertEqual(
            str(Path(staged_output).parent / "fixture.alignment.json"), staged_sidecar
        )
        self.assertEqual(
            [
                "--epub",
                str(self.run_root / "dist" / "fixture.epub"),
                "--out",
                staged_output,
                "--sidecar",
                staged_sidecar,
                "--voice",
                "am_michael",
                "--title",
                "Fixture Book",
                "--author",
                "Dan Fakkeldy",
                "--cover",
                str(self.run_root / "dist" / "candidate-1" / "m4b-cover.png"),
                "--work-dir",
                next(
                    argument
                    for index, argument in enumerate(arguments)
                    if arguments[index - 1] == "--work-dir"
                ),
                "--db",
                next(
                    argument
                    for index, argument in enumerate(arguments)
                    if arguments[index - 1] == "--db"
                ),
                "--jobs",
                "1",
                "--threads",
                "2",
            ],
            arguments,
        )
        work = Path(arguments[arguments.index("--work-dir") + 1])
        database = Path(arguments[arguments.index("--db") + 1])
        self.assertEqual(self.run_root, work.parent)
        self.assertEqual(self.run_root, database.parent)
        run_id = work.name.removeprefix("audio-work-")
        self.assertEqual(f"narration-{run_id}.sqlite", database.name)
        self.assertFalse(
            (self.run_root / "research" / "echo-render-output.owner.env").exists()
        )

    def test_bounded_partial_render_is_sealed_but_not_published(self) -> None:
        log = self.tmp / "narrate-partial.log"
        environment = self.environment()
        environment.update(
            {
                "FAKE_NARRATE_LOG": str(log),
                "FAKE_NARRATE_EXIT": "2",
            }
        )

        result = self.run_narrate(
            "--max-chapters", "1", environment=environment
        )

        self.assertEqual(2, result.returncode, result.stderr)
        arguments = [
            line.removeprefix("ARG=")
            for line in log.read_text(encoding="utf-8").splitlines()
            if line.startswith("ARG=")
        ]
        self.assertIn("--max-chapters", arguments)
        max_index = arguments.index("--max-chapters")
        self.assertEqual("1", arguments[max_index + 1])
        self.assertEqual(1, len(list(self.run_root.glob("audio-work-*/.anchors-ch0.json"))))
        self.assertEqual(1, len(list(self.run_root.glob("narration-*.sqlite"))))
        self.assertEqual(
            1, len(list((self.run_root / "research").glob("echo-resume-state-*.json")))
        )
        self.assertTrue(
            (self.run_root / "research" / "echo-render-current-attempt.json").is_file()
        )
        self.assertFalse(
            (self.run_root / "research" / "echo-render-current-accepted.json").exists()
        )
        self.assertFalse(list((self.run_root / "dist").glob("echo-renders/**/*")))
        self.assertFalse(list(self.run_root.glob(".echo-output-*")))

    def test_max_chapters_requires_a_positive_integer(self) -> None:
        for arguments in (
            ("--max-chapters",),
            ("--max-chapters", "0"),
            ("--max-chapters", "-1"),
            ("--max-chapters", "one"),
        ):
            with self.subTest(arguments=arguments):
                result = self.run_narrate(*arguments)
                self.assertEqual(64, result.returncode)
                self.assertIn("positive integer", result.stderr)

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
        for lane in ("", "fiction", "../fiction", "Fiction"):
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

    def test_resume_requires_the_canonical_absolute_state_path(self) -> None:
        bare = self.run_narrate("--resume")
        self.assertEqual(64, bare.returncode)
        self.assertIn("--resume-state ABSOLUTE_PATH", bare.stderr)

        relative = self.run_narrate(
            "--resume", "--resume-state", "research/echo-resume-state.json"
        )
        self.assertEqual(64, relative.returncode)
        self.assertIn("absolute", relative.stderr)

        state_without_resume = self.run_narrate(
            "--resume-state", str(self.run_root / "research" / "state.json")
        )
        self.assertEqual(64, state_without_resume.returncode)
        self.assertIn("requires --resume", state_without_resume.stderr)

        self.use_run_lane("fiction-audiobooks")
        fiction_environment = self.environment()
        fiction_environment["ECHO_RUN_LANE"] = "fiction-audiobook"
        initial = self.run_narrate(environment=fiction_environment)
        self.assertEqual(0, initial.returncode, initial.stderr)
        mismatched = self.run_narrate(
            "--resume",
            "--resume-state",
            str(self.run_root / "research" / "echo-resume-state-wrong.json"),
            environment=fiction_environment,
        )
        self.assertEqual(64, mismatched.returncode)
        self.assertIn("canonical", mismatched.stderr)

        fiction_state = next(
            (self.run_root / "research").glob("echo-resume-state-*.json")
        )

        dropped_lane = self.run_narrate(
            "--resume", "--resume-state", str(fiction_state)
        )
        self.assertEqual(64, dropped_lane.returncode)
        self.assertIn("canonical", dropped_lane.stderr)

        changed_lane_environment = self.environment()
        changed_lane_environment["ECHO_RUN_LANE"] = "audiobook"
        changed_lane = self.run_narrate(
            "--resume",
            "--resume-state",
            str(fiction_state),
            environment=changed_lane_environment,
        )
        self.assertEqual(64, changed_lane.returncode)
        self.assertIn("canonical", changed_lane.stderr)

        fiction_resume = self.run_narrate(
            "--resume",
            "--resume-state",
            str(fiction_state),
            environment=fiction_environment,
        )
        self.assertEqual(0, fiction_resume.returncode, fiction_resume.stderr)

    def test_success_publishes_run_scoped_media_and_current_selector(self) -> None:
        result = self.run_narrate()
        self.assertEqual(0, result.returncode, result.stderr)

        attempt_path = self.run_root / "research" / "echo-render-current-attempt.json"
        selector_path = self.run_root / "research" / "echo-render-current-accepted.json"
        self.assertTrue(attempt_path.is_file())
        self.assertTrue(selector_path.is_file())
        attempt = json.loads(attempt_path.read_text(encoding="utf-8"))
        selector = json.loads(selector_path.read_text(encoding="utf-8"))
        self.assertEqual(attempt["attemptID"], selector["attemptID"])
        artifact_root = self.run_root / "dist" / selector["artifactRelativePath"]
        self.assertTrue(
            artifact_root.is_relative_to(self.run_root / "dist" / "echo-renders")
        )
        self.assertEqual(selector["runID"], artifact_root.parent.name)
        self.assertEqual(selector["attemptID"], artifact_root.name)
        self.assertTrue((artifact_root / "fixture.m4b").is_file())
        self.assertFalse((self.run_root / "dist" / "fixture.m4b").exists())

    def test_preserves_optional_pronunciation_reel(self) -> None:
        """Port of test_learning_pilot_preserves_optional_pronunciation_reel,
        deleted from this file in commit a092860 along with the pilot
        wrapper it exercised (originally added in commit 9b86658). The full
        wrapper stages and publishes the reel exactly like the pilot wrapper
        did (`mv -- "$STAGE_REEL" "$REEL"` in echo_pronunciation_narrate.sh),
        under the full wrapper's dist/echo-renders/<run>/<attempt> layout
        rather than the pilot's flat dist directory. This is the only test
        in the suite that sets FAKE_EMIT_REEL; without it the reel
        staging/publish path and the reelFileName/reelSHA256 success-receipt
        fields go uncovered.
        """
        environment = self.environment()
        environment["FAKE_EMIT_REEL"] = "1"

        result = self.run_narrate(environment=environment)

        self.assertEqual(0, result.returncode, result.stderr)
        selector = json.loads(
            (self.run_root / "research" / "echo-render-current-accepted.json")
            .read_text(encoding="utf-8")
        )
        artifact_root = self.run_root / "dist" / selector["artifactRelativePath"]
        self.assertTrue(
            artifact_root.is_relative_to(self.run_root / "dist" / "echo-renders")
        )
        reel = artifact_root / "fixture.pronunciation-reel.m4b"
        self.assertEqual(b"fixture listening reel", reel.read_bytes())

        success = json.loads(
            next(
                (self.run_root / "research").glob("echo-render-success-*.json")
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(reel.name, success["reelFileName"])
        self.assertEqual(
            hashlib.sha256(reel.read_bytes()).hexdigest(), success["reelSHA256"]
        )

    def test_block_narration_contains_review_media_outside_the_attempt(self) -> None:
        """Block-plan output publishes only delivery media into an attempt."""
        plan = self.write_block_voice_plan("contained-review-plan.json")
        narrate_log = self.tmp / "contained-review-narrate.log"
        environment = self.environment()
        environment.update(
            {
                "FAKE_EMIT_REEL": "1",
                "FAKE_NARRATE_LOG": str(narrate_log),
            }
        )

        result = self.run_narrate("--voice-plan", str(plan), environment=environment)

        self.assertEqual(0, result.returncode, result.stderr)
        research = self.run_root / "research"
        selector = json.loads(
            (research / "echo-render-current-accepted.json").read_text(
                encoding="utf-8"
            )
        )
        attempt = json.loads(
            (research / "echo-render-current-attempt.json").read_text(
                encoding="utf-8"
            )
        )
        artifact_root = self.run_root / "dist" / selector["artifactRelativePath"]
        self.assertEqual(
            {
                "fixture.m4b",
                "fixture.alignment.json",
                "fixture.pronunciation-audit.json",
            },
            {path.name for path in artifact_root.iterdir()},
        )
        run_id = selector["runID"]
        attempt_id = selector["attemptID"]
        reel = (
            research
            / "listening"
            / run_id
            / attempt_id
            / "fixture.pronunciation-reel.m4b"
        )
        self.assertEqual(b"fixture listening reel", reel.read_bytes())
        self.assertEqual(
            [
                Path(self.receipt_fields(
                    next(research.glob("echo-render-inputs-*.env"))
                )["work_dir"])
                / "chapter-0.m4a"
            ],
            sorted(self.run_root.rglob("*.m4a")),
        )
        success = json.loads(
            next(research.glob("echo-render-success-*.json")).read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            "listening/"
            + run_id
            + "/"
            + attempt_id
            + "/fixture.pronunciation-reel.m4b",
            success["reelRelativePath"],
        )
        self.assertEqual(reel.name, success["reelFileName"])
        self.assertEqual(hashlib.sha256(reel.read_bytes()).hexdigest(), success["reelSHA256"])
        self.assertEqual(
            {
                "schemaVersion",
                "attemptID",
                "runID",
                "inputReceiptFileName",
                "inputReceiptSHA256",
                "sourceEPUBFileName",
                "sourceEPUBSHA256",
                "artifactRelativePath",
                "rendererSchemaVersion",
                "rendererRoot",
                "rendererBuildRoot",
                "installerSourceSHA",
                "echoSourceSHA",
                "rendererManifestSHA256",
                "echoCLI_SHA256",
                "echoResourcesSHA256",
                "echoRenderVersion",
                "modelPolicyRevision",
                "modelExpectedByteCount",
                "modelBytesAttested",
            },
            set(attempt),
        )
        arguments = [
            line.removeprefix("ARG=")
            for line in narrate_log.read_text(encoding="utf-8").splitlines()
            if line.startswith("ARG=")
        ]
        fields = self.receipt_fields(next(research.glob("echo-render-inputs-*.env")))
        self.assertEqual(
            fields["voice_plan_canonical_path"],
            arguments[arguments.index("--voice-plan") + 1],
        )
        self.assertNotIn("--voice", arguments)
        self.assertNotIn("--chapter-voice", arguments)

        delivery_command = [
            "/usr/local/bin/python3",
            str(STATE_HELPER),
            "verify-delivery",
            *self.renderer_state_arguments(
                self.renderer_identity_from_receipt(attempt)
            ),
            "--voice",
            fields["voice"],
            "--attempt",
            str(research / "echo-render-current-attempt.json"),
            "--selector",
            str(research / "echo-render-current-accepted.json"),
            "--receipt",
            str(next(research.glob("echo-render-success-*.json"))),
            "--input-receipt",
            str(next(research.glob("echo-render-inputs-*.env"))),
            "--state-receipt",
            str(next(research.glob("echo-resume-state-*.json"))),
            "--epub",
            str(self.run_root / "dist" / "fixture.epub"),
            "--audiobook",
            str(artifact_root / "fixture.m4b"),
            "--sidecar",
            str(artifact_root / "fixture.alignment.json"),
            "--audit",
            str(artifact_root / "fixture.pronunciation-audit.json"),
            "--reel",
            str(reel),
        ]
        delivered = subprocess.run(delivery_command, capture_output=True, text=True)
        self.assertEqual(0, delivered.returncode, delivered.stderr)
        for leaked_name in (
            "leaked.m4a",
            "leaked.wav",
            "leaked.pcm",
            ".anchors-ch9.json",
            "leaked.pronunciation-reel.m4b",
        ):
            with self.subTest(leaked_name=leaked_name):
                leaked = artifact_root / leaked_name
                leaked.write_bytes(b"forbidden attempt media")
                rejected = subprocess.run(
                    delivery_command, capture_output=True, text=True
                )
                self.assertNotEqual(0, rejected.returncode)
                self.assertIn("block attempt contains", rejected.stderr)
                leaked.unlink()

    def test_block_delivery_evidence_comes_from_accepted_receipts_not_voice_env(
        self,
    ) -> None:
        """The post-render reader must surface sealed block facts as env0."""
        plan = self.write_block_voice_plan("delivery-evidence-plan.json")
        environment = self.environment()
        environment.pop("VOICE")
        narrate_log = self.tmp / "delivery-evidence-narrate.log"
        environment.update(
            {"FAKE_EMIT_REEL": "1", "FAKE_NARRATE_LOG": str(narrate_log)}
        )
        self.assertNotIn("VOICE", environment)

        rendered = self.run_narrate("--voice-plan", str(plan), environment=environment)
        self.assertEqual(0, rendered.returncode, rendered.stderr)
        self.assertIn(
            "VOICE=am_michael",
            next(
                line
                for line in narrate_log.read_text(encoding="utf-8").splitlines()
                if line.startswith("ENV=")
            ),
        )
        inherited_voice = self.environment()
        inherited_voice["VOICE"] = "af_heart"
        rejected = self.run_narrate(
            "--voice-plan", str(plan), environment=inherited_voice
        )
        self.assertEqual(64, rejected.returncode, rejected.stderr)
        self.assertIn("block-plan default voice", rejected.stderr)

        research = self.run_root / "research"
        selector = research / "echo-render-current-accepted.json"
        accepted = json.loads(selector.read_text(encoding="utf-8"))
        receipt = research / accepted["successReceiptFileName"]
        input_receipt = research / accepted["inputReceiptFileName"]
        command = [
            "/usr/local/bin/python3",
            str(STATE_HELPER),
            "block-delivery-evidence",
            "--attempt",
            str(research / "echo-render-current-attempt.json"),
            "--selector",
            str(selector),
            "--receipt",
            str(receipt),
            "--input-receipt",
            str(input_receipt),
            "--format",
            "env0",
        ]
        derived = subprocess.run(command, capture_output=True, check=False)
        self.assertEqual(0, derived.returncode, derived.stderr.decode())
        fields = dict(
            token.decode("utf-8").split("=", 1)
            for token in derived.stdout.split(b"\0")
            if token
        )
        success = json.loads(receipt.read_text(encoding="utf-8"))
        self.assertEqual("block", fields["voice_plan_mode"])
        self.assertEqual(success["reelRelativePath"], fields["reel_relative_path"])
        self.assertEqual(success["voicePlanSHA256"], fields["voice_plan_sha256"])
        self.assertEqual(
            str(success["voicePlanBlockCount"]), fields["voice_plan_block_count"]
        )
        self.assertEqual("am_michael", fields["voice"])

        artifact_root = self.run_root / "dist" / accepted["artifactRelativePath"]
        reel = research / fields["reel_relative_path"]
        delivered = subprocess.run(
            [
                "/usr/local/bin/python3",
                str(STATE_HELPER),
                "verify-delivery",
                "--attempt",
                str(research / "echo-render-current-attempt.json"),
                "--selector",
                str(selector),
                "--receipt",
                str(receipt),
                "--input-receipt",
                str(input_receipt),
                "--state-receipt",
                str(research / f"echo-resume-state-{accepted['runID']}.json"),
                "--epub",
                str(self.run_root / "dist" / "fixture.epub"),
                "--audiobook",
                str(artifact_root / "fixture.m4b"),
                "--sidecar",
                str(artifact_root / "fixture.alignment.json"),
                "--audit",
                str(artifact_root / "fixture.pronunciation-audit.json"),
                "--reel",
                str(reel),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, delivered.returncode, delivered.stderr)
        audited = subprocess.run(
            [
                "/usr/local/bin/python3",
                str(AUDIT_VALIDATOR),
                str(artifact_root / "fixture.pronunciation-audit.json"),
                "--audiobook",
                str(artifact_root / "fixture.m4b"),
                "--reel",
                str(reel),
                "--voice-plan-sha256",
                fields["voice_plan_sha256"],
                "--block-count",
                fields["voice_plan_block_count"],
            ],
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, audited.returncode, audited.stderr)

    def test_block_delivery_evidence_requires_the_exact_current_attempt_schema(
        self,
    ) -> None:
        """A rehashed mutable chain still cannot add or remove attempt fields."""

        paths = self.completed_block_delivery_paths("exact-attempt-schema")
        original = {
            name: paths[name].read_bytes()
            for name in ("attempt", "selector", "receipt")
        }
        mutations: tuple[tuple[str, Callable[[dict[str, object]], None]], ...] = (
            (
                "extra",
                lambda payload: payload.__setitem__("unexpected", "drift"),
            ),
            (
                "missing",
                lambda payload: payload.pop("modelPolicyRevision"),
            ),
        )
        for name, mutate in mutations:
            with self.subTest(mutation=name):
                try:
                    self.rebind_block_attempt_chain(paths, mutate)
                    rejected = subprocess.run(
                        self.block_delivery_evidence_command(paths),
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(65, rejected.returncode, rejected.stderr)
                    self.assertIn(
                        "not the exact current attempt schema", rejected.stderr
                    )
                    self.assertEqual("", rejected.stdout)
                finally:
                    for path_name, content in original.items():
                        paths[path_name].write_bytes(content)

    def test_governed_receipt_consumers_preserve_input_diagnostics(self) -> None:
        """The one-open boundary keeps all established unsafe-input messages."""

        paths = self.completed_block_delivery_paths("symlinked-delivery-evidence")
        labels = {
            "attempt": "current-attempt receipt",
            "selector": "current-accepted selector",
            "receipt": "render-success receipt",
            "input_receipt": "render-input receipt",
        }
        diagnostics = (
            ("missing", "is missing"),
            ("symlink", "must not be a symlink"),
            ("directory", "must be a regular file"),
        )
        for consumer in ("block-delivery-evidence", "verify-delivery"):
            for name, label in labels.items():
                for kind, diagnostic in diagnostics:
                    with self.subTest(
                        consumer=consumer,
                        receipt=name,
                        input_kind=kind,
                    ):
                        invalid_paths = dict(paths)
                        invalid_path = self.tmp / f"{consumer}-{name}-{kind}"
                        if kind == "symlink":
                            invalid_path.symlink_to(paths[name])
                        elif kind == "directory":
                            invalid_path.mkdir()
                        invalid_paths[name] = invalid_path
                        command = (
                            self.block_delivery_evidence_command(invalid_paths)
                            if consumer == "block-delivery-evidence"
                            else self.delivery_fallback_command(invalid_paths)
                        )
                        rejected = subprocess.run(
                            command,
                            capture_output=True,
                            text=True,
                        )
                        self.assertEqual(65, rejected.returncode, rejected.stderr)
                        self.assertEqual("", rejected.stdout)
                        self.assertEqual(
                            "echo_pronunciation_state: "
                            f"{label} {diagnostic}: {invalid_path}\n",
                            rejected.stderr,
                        )

    def test_verify_delivery_fallback_cross_checks_explicit_voice_and_renderer(
        self,
    ) -> None:
        """Receipt-derived fallback never permits conflicting caller overrides."""

        paths = self.completed_block_delivery_paths("fallback-cross-checks")
        attempt = json.loads(paths["attempt"].read_text(encoding="utf-8"))
        mismatched_renderer = self.renderer_identity_from_receipt(attempt)
        mismatched_renderer["echoCLI_SHA256"] = "0" * 64
        cases = (
            ("voice", (), "af_heart"),
            (
                "renderer",
                self.renderer_state_arguments(mismatched_renderer),
                None,
            ),
        )
        for name, renderer_arguments, voice in cases:
            with self.subTest(mismatch=name):
                rejected = subprocess.run(
                    self.delivery_fallback_command(
                        paths,
                        renderer_arguments=renderer_arguments,
                        voice=voice,
                    ),
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(65, rejected.returncode, rejected.stderr)
                self.assertEqual("", rejected.stdout)

    def test_governed_receipt_replacement_fails_closed_for_block_evidence_and_fallback(
        self,
    ) -> None:
        """No post-render consumer may mix data across atomic receipt replaces."""

        paths = self.completed_block_delivery_paths("atomic-replacement")
        consumers = ("block_delivery_evidence", "verify_delivery_receipt")
        for consumer in consumers:
            for name in ("attempt", "selector", "receipt", "input_receipt"):
                with self.subTest(consumer=consumer, receipt=name):
                    namespace = self.state_namespace()
                    target = paths[name]
                    replacement = self.tmp / f"{consumer}-{name}-replacement"
                    replacement.write_bytes(target.read_bytes())
                    runtime_globals = namespace["snapshot_regular_file"].__globals__
                    original_open_regular = runtime_globals["open_regular"]
                    replaced = False
                    open_count = 0

                    def replace_after_open(path: Path, label: str) -> int:
                        nonlocal open_count, replaced
                        descriptor = original_open_regular(path, label)
                        if path == target:
                            open_count += 1
                            if not replaced:
                                os.replace(replacement, target)
                                replaced = True
                        return descriptor

                    runtime_globals["open_regular"] = replace_after_open
                    state_error = namespace["StateError"]
                    try:
                        with self.assertRaises(state_error):
                            if consumer == "block_delivery_evidence":
                                namespace["block_delivery_evidence"](
                                    paths["attempt"],
                                    paths["selector"],
                                    paths["receipt"],
                                    paths["input_receipt"],
                                )
                            else:
                                namespace["verify_delivery_receipt"](
                                    paths["attempt"],
                                    paths["selector"],
                                    paths["receipt"],
                                    paths["input_receipt"],
                                    paths["state_receipt"],
                                    paths["epub"],
                                    paths["audiobook"],
                                    paths["sidecar"],
                                    paths["audit"],
                                    paths["reel"],
                                    None,
                                    None,
                                )
                    finally:
                        runtime_globals["open_regular"] = original_open_regular
                    self.assertTrue(replaced)
                    self.assertEqual(1, open_count)

    def test_block_resume_reuses_only_the_same_resolved_plan_identity(self) -> None:
        compact = self.write_block_voice_plan("resume-compact-plan.json")
        pretty = self.write_block_voice_plan("resume-pretty-plan.json", sorted_keys=True)
        environment = self.environment()
        environment["FAKE_NARRATE_EXIT"] = "2"

        partial = self.run_narrate("--voice-plan", str(compact), environment=environment)

        self.assertEqual(2, partial.returncode, partial.stderr)
        research = self.run_root / "research"
        state = next(research.glob("echo-resume-state-*.json"))
        first_fields = self.receipt_fields(next(research.glob("echo-render-inputs-*.env")))
        marker = next(self.run_root.glob("audio-work-*/.anchors-ch0.json"))
        self.assertEqual(2, json.loads(marker.read_text(encoding="utf-8"))["identity"]["schemaVersion"])

        resumed_environment = self.environment()
        resumed = self.run_narrate(
            "--resume",
            "--resume-state",
            str(state),
            "--voice-plan",
            str(pretty),
            environment=resumed_environment,
        )

        self.assertEqual(0, resumed.returncode, resumed.stderr)
        same_receipt = next(research.glob("echo-render-inputs-*.env"))
        self.assertEqual(first_fields["run_id"], self.receipt_fields(same_receipt)["run_id"])

        self.fake_voice_plan_sha.write_text("c" * 64 + "\n", encoding="utf-8")
        changed = self.run_narrate(
            "--resume",
            "--resume-state",
            str(state),
            "--voice-plan",
            str(compact),
            environment=self.environment(),
        )

        self.assertEqual(64, changed.returncode, changed.stderr)
        changed_receipt = next(
            path
            for path in research.glob("echo-render-inputs-*.env")
            if self.receipt_fields(path)["voice_plan_sha256"] == "c" * 64
        )
        self.assertNotEqual(
            first_fields["run_id"], self.receipt_fields(changed_receipt)["run_id"]
        )
        self.assertFalse(
            (self.run_root / f"audio-work-{self.receipt_fields(changed_receipt)['run_id']}").exists()
        )

    def test_wrapper_replaces_inherited_echo_resource_dir_for_every_cli_call(
        self,
    ) -> None:
        environment = self.environment()
        environment["ECHO_RESOURCE_DIR"] = "/stale/debug/resources"

        result = self.run_narrate(environment=environment)

        self.assertEqual(0, result.returncode, result.stderr)
        calls = self.installed_probe_log.read_text(encoding="utf-8").splitlines()
        sealed_suffix = f" ECHO_RESOURCE_DIR={self.resources.resolve()}"
        self.assertGreater(len(calls), 0)
        self.assertTrue(all(call.endswith(sealed_suffix) for call in calls), calls)
        for required_call in (
            "CALL=--version:",
            "CALL=narrate:--help",
            "CALL=verify-sidecar:--help",
            "CALL=narrate:--epub",
            "CALL=verify-sidecar:--epub",
        ):
            with self.subTest(required_call=required_call):
                self.assertTrue(
                    any(call.startswith(required_call) for call in calls), calls
                )

    def test_concurrent_owner_fails_before_narrate_then_resume_is_allowed(self) -> None:
        log = self.tmp / "narrate.log"
        ready = self.tmp / "ready"
        release = self.tmp / "release"
        environment = self.environment()
        environment.update(
            {
                "FAKE_NARRATE_LOG": str(log),
                "FAKE_NARRATE_READY": str(ready),
                "FAKE_NARRATE_RELEASE": str(release),
            }
        )
        first = subprocess.Popen(
            [str(NARRATE_WRAPPER)],
            cwd=self.explainer,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.addCleanup(lambda: first.poll() is None and first.kill())
        self.wait_for_path(ready, first)
        owner = self.run_root / "research" / "echo-render-output.owner.env"
        self.assertTrue(owner.is_file())

        contender_environment = environment.copy()
        contender = self.run_narrate(environment=contender_environment)

        self.assertEqual(75, contender.returncode, contender.stderr)
        self.assertIn("active narration lease", contender.stderr)
        self.assertEqual(
            1,
            log.read_text(encoding="utf-8").count("BEGIN="),
            "contender reached echo-cli narrate",
        )

        release.touch()
        first_stdout, first_stderr = first.communicate(timeout=WAIT_TIMEOUT)
        self.assertEqual(0, first.returncode, f"{first_stdout}\n{first_stderr}")
        self.assertFalse(owner.exists())

        resumed_environment = self.environment()
        resumed_environment["FAKE_NARRATE_LOG"] = str(log)
        resume_state = next(
            (self.run_root / "research").glob("echo-resume-state-*.json")
        )
        resumed = self.run_narrate(
            "--resume",
            "--resume-state",
            str(resume_state),
            environment=resumed_environment,
        )
        self.assertEqual(0, resumed.returncode, resumed.stderr)
        log_lines = log.read_text(encoding="utf-8").splitlines()
        self.assertEqual(2, sum(line.startswith("BEGIN=") for line in log_lines))
        self.assertIn("ARG=--resume", log_lines)
        self.assertFalse(owner.exists())

    def test_alternate_lock_root_cannot_fork_the_build_lease_namespace(self) -> None:
        log = self.tmp / "alternate-root.log"
        ready = self.tmp / "alternate-root-ready"
        release = self.tmp / "alternate-root-release"
        first_environment = self.environment()
        first_environment.update(
            {
                "ECHO_PRONUNCIATION_LEASE_ROOT": str(self.tmp / "attacker-a"),
                "FAKE_NARRATE_LOG": str(log),
                "FAKE_NARRATE_READY": str(ready),
                "FAKE_NARRATE_RELEASE": str(release),
            }
        )
        first = subprocess.Popen(
            [str(NARRATE_WRAPPER)],
            cwd=self.explainer,
            env=first_environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.addCleanup(lambda: first.poll() is None and first.kill())
        self.wait_for_path(ready, first)

        second_slug = "fixture-two"
        second_run_root = (
            self.explainer / ".build" / "custom-learning-audiobooks" / second_slug
        )
        (second_run_root / "dist").mkdir(parents=True)
        (second_run_root / "dist" / f"{second_slug}.epub").write_bytes(
            b"second fixture epub"
        )
        second_environment = self.environment()
        second_environment.update(
            {
                "ECHO_PRONUNCIATION_LEASE_ROOT": str(self.tmp / "attacker-b"),
                "FAKE_NARRATE_LOG": str(log),
                "SLUG": second_slug,
                "RUN_ROOT": str(second_run_root),
                "TITLE": "Second Fixture Book",
            }
        )
        contender = self.run_narrate(environment=second_environment)

        release.touch()
        first_stdout, first_stderr = first.communicate(timeout=WAIT_TIMEOUT)
        self.assertEqual(75, contender.returncode, contender.stderr)
        self.assertIn("active narration lease", contender.stderr)
        self.assertEqual(1, log.read_text(encoding="utf-8").count("BEGIN="))
        self.assertEqual(0, first.returncode, f"{first_stdout}\n{first_stderr}")
        self.assertFalse((self.tmp / "attacker-a").exists())
        self.assertFalse((self.tmp / "attacker-b").exists())

    def test_stale_lock_recovery_is_local_explicit_and_exact(self) -> None:
        preflight = self.run_preflight(
            body=(
                "echo_pronunciation_preflight\n"
                'printf "run_id=%s\\nwork=%s\\ndb=%s\\n" "$RUN_ID" "$WORK" "$DB"'
            )
        )
        self.assertEqual(0, preflight.returncode, preflight.stderr)
        fields = dict(
            line.split("=", 1)
            for line in preflight.stdout.splitlines()
            if line.startswith(("run_id=", "work=", "db="))
        )
        owner = self.run_root / "research" / "echo-render-output.owner.env"

        def write_owner(
            hostname: str = socket.gethostname(),
            run_id: str = fields["run_id"],
        ) -> None:
            attempt_id = "e" * 64
            artifact_root = (
                self.run_root / "dist" / "echo-renders" / run_id / attempt_id
            )
            owner.write_text(
                "\n".join(
                    (
                        "lock_schema=2",
                        f"owner_token={'a' * 64}",
                        "owner_pid=99999999",
                        f"owner_host={hostname}",
                        "owner_start=Mon Jan  1 00:00:00 2001",
                        f"run_id={run_id}",
                        f"attempt_id={attempt_id}",
                        f"work_dir={self.run_root / f'audio-work-{run_id}'}",
                        f"narration_db={self.run_root / f'narration-{run_id}.sqlite'}",
                        f"output_m4b={artifact_root / 'fixture.m4b'}",
                        f"output_sidecar={artifact_root / 'fixture.alignment.json'}",
                        f"output_audit={artifact_root / 'fixture.pronunciation-audit.json'}",
                        f"output_reel={artifact_root / 'fixture.pronunciation-reel.m4b'}",
                    )
                )
                + "\n",
                encoding="utf-8",
            )

        write_owner()
        ordinary = self.run_narrate()
        self.assertEqual(0, ordinary.returncode, ordinary.stderr)
        self.assertIn("recovered stale local narration owner", ordinary.stderr)
        self.assertFalse(owner.exists())

        write_owner("remote.example")
        remote = self.run_narrate("--recover-stale-lock")
        self.assertEqual(75, remote.returncode)
        self.assertIn("remote narration lock", remote.stderr)
        self.assertTrue(owner.exists())

        write_owner()
        malformed_text = owner.read_text(encoding="utf-8").replace(
            "owner_pid=99999999\n", ""
        )
        owner.write_text(malformed_text, encoding="utf-8")
        malformed = self.run_narrate("--recover-stale-lock")
        self.assertEqual(75, malformed.returncode)
        self.assertIn("malformed narration lock", malformed.stderr)
        self.assertTrue(owner.exists())

        write_owner()
        recovered = self.run_narrate("--recover-stale-lock")
        self.assertEqual(0, recovered.returncode, recovered.stderr)
        self.assertIn("stale narration lock recovered", recovered.stdout)
        self.assertFalse(owner.exists())

        old_run_id = f"{'a' * 12}-{'b' * 12}-{'c' * 12}-{'d' * 40}-am_michael"
        write_owner(run_id=old_run_id)
        old_recovered = self.run_narrate("--recover-stale-lock")
        self.assertEqual(75, old_recovered.returncode, old_recovered.stderr)
        self.assertIn("malformed narration lock", old_recovered.stderr)
        self.assertTrue(owner.exists())
        owner.unlink()

        fresh = self.run_narrate()
        self.assertEqual(0, fresh.returncode, fresh.stderr)
        self.assertFalse(owner.exists())

    def test_narration_lock_releases_on_cli_failure_and_signal(self) -> None:
        failed_environment = self.environment()
        failed_environment["FAKE_NARRATE_EXIT"] = "42"
        failed = self.run_narrate(environment=failed_environment)
        self.assertEqual(42, failed.returncode)
        owner = self.run_root / "research" / "echo-render-output.owner.env"
        self.assertFalse(owner.exists())

        ready = self.tmp / "signal-ready"
        release = self.tmp / "never-release"
        signaled_environment = self.environment()
        signaled_environment.update(
            {
                "FAKE_NARRATE_READY": str(ready),
                "FAKE_NARRATE_RELEASE": str(release),
            }
        )
        process = subprocess.Popen(
            [str(NARRATE_WRAPPER)],
            cwd=self.explainer,
            env=signaled_environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.addCleanup(lambda: process.poll() is None and process.kill())
        self.wait_for_path(ready, process)
        process.send_signal(signal.SIGTERM)
        process.communicate(timeout=WAIT_TIMEOUT)
        self.assertEqual(143, process.returncode)
        self.assertFalse(owner.exists())

    def test_locked_postcheck_rejects_epub_changed_during_narration(self) -> None:
        ready = self.tmp / "hash-ready"
        release = self.tmp / "hash-release"
        environment = self.environment()
        environment.update(
            {
                "FAKE_NARRATE_READY": str(ready),
                "FAKE_NARRATE_RELEASE": str(release),
            }
        )
        process = subprocess.Popen(
            [str(NARRATE_WRAPPER)],
            cwd=self.explainer,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.addCleanup(lambda: process.poll() is None and process.kill())
        self.wait_for_path(ready, process)
        (self.run_root / "dist" / "fixture.epub").write_bytes(b"changed")
        release.touch()
        stdout, stderr = process.communicate(timeout=WAIT_TIMEOUT)
        self.assertEqual(65, process.returncode, f"{stdout}\n{stderr}")
        self.assertIn("EPUB changed while narration lease was held", stderr)
        owner = self.run_root / "research" / "echo-render-output.owner.env"
        self.assertFalse(owner.exists())

    def test_locked_postcheck_rejects_receipt_changed_during_narration(self) -> None:
        ready = self.tmp / "receipt-ready"
        release = self.tmp / "receipt-release"
        environment = self.environment()
        environment.update(
            {
                "FAKE_NARRATE_READY": str(ready),
                "FAKE_NARRATE_RELEASE": str(release),
            }
        )
        process = subprocess.Popen(
            [str(NARRATE_WRAPPER)],
            cwd=self.explainer,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.addCleanup(lambda: process.poll() is None and process.kill())
        self.wait_for_path(ready, process)
        receipts = list((self.run_root / "research").glob("echo-render-inputs-*.env"))
        self.assertEqual(1, len(receipts))
        receipts[0].write_text("tampered=true\n", encoding="utf-8")
        release.touch()
        stdout, stderr = process.communicate(timeout=WAIT_TIMEOUT)
        self.assertEqual(65, process.returncode, f"{stdout}\n{stderr}")
        self.assertIn("receipt changed while narration lease was held", stderr)
        owner = self.run_root / "research" / "echo-render-output.owner.env"
        self.assertFalse(owner.exists())

    def test_locked_postcheck_rejects_resource_bundle_changed_during_narration(
        self,
    ) -> None:
        ready = self.tmp / "resource-ready"
        release = self.tmp / "resource-release"
        environment = self.environment()
        environment.update(
            {
                "FAKE_NARRATE_READY": str(ready),
                "FAKE_NARRATE_RELEASE": str(release),
            }
        )
        process = subprocess.Popen(
            [str(NARRATE_WRAPPER)],
            cwd=self.explainer,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.addCleanup(lambda: process.poll() is None and process.kill())
        self.wait_for_path(ready, process)
        (self.resources / "pronunciations.json").write_text(
            '{"renderVersion":13}\n', encoding="utf-8"
        )
        release.touch()
        stdout, stderr = process.communicate(timeout=WAIT_TIMEOUT)
        self.assertEqual(65, process.returncode, f"{stdout}\n{stderr}")
        self.assertIn("resource identity", stderr)

    def test_resume_requires_hash_bound_current_render_version_capture_state(self) -> None:
        initial = self.run_narrate()
        self.assertEqual(0, initial.returncode, initial.stderr)
        marker = next(self.run_root.glob("audio-work-*/.anchors-ch0.json"))
        marker_payload = json.loads(marker.read_text(encoding="utf-8"))
        marker_payload["identity"]["renderVersion"] = True
        marker.write_text(json.dumps(marker_payload), encoding="utf-8")

        resumed = self.run_narrate(*self.resume_arguments())
        self.assertNotEqual(0, resumed.returncode)
        self.assertIn("resume state", resumed.stderr)

    def test_resume_keeps_the_sealed_renderer_after_a_new_promotion(
        self,
    ) -> None:
        selector_path = self.renderer_root / self.source_sha / "approved-renderer.json"
        original_selector = selector_path.read_bytes()
        _, sealed_manifest = self.select_manifest_variant(
            lambda payload: payload.__setitem__("renderVersion", 13),
            render_version=13,
        )
        initial = self.run_narrate()
        self.assertEqual(0, initial.returncode, initial.stderr)
        marker = next(self.run_root.glob("audio-work-*/.anchors-ch0.json"))
        marker_payload = json.loads(marker.read_text(encoding="utf-8"))
        self.assertEqual(13, marker_payload["identity"]["renderVersion"])
        selector_path.write_bytes(original_selector)

        resumed = self.run_narrate(*self.resume_arguments())

        self.assertEqual(0, resumed.returncode, resumed.stderr)
        accepted = json.loads(
            (self.run_root / "research" / "echo-render-current-accepted.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(sealed_manifest, accepted["rendererManifestSHA256"])
        self.assertEqual(13, accepted["echoRenderVersion"])

    def test_resume_rejects_database_mutation(self) -> None:
        initial = self.run_narrate()
        self.assertEqual(0, initial.returncode, initial.stderr)
        database = next(self.run_root.glob("narration-*.sqlite"))
        database.write_bytes(b"substituted database")
        changed_database = self.run_narrate(*self.resume_arguments())
        self.assertNotEqual(0, changed_database.returncode)
        self.assertIn("resume state", changed_database.stderr)

    def test_resume_rejects_identity_free_legacy_capture(self) -> None:
        initial = self.run_narrate()
        self.assertEqual(0, initial.returncode, initial.stderr)
        marker = next(self.run_root.glob("audio-work-*/.anchors-ch0.json"))
        payload = json.loads(marker.read_text(encoding="utf-8"))
        payload["identity"] = None
        marker.write_text(json.dumps(payload), encoding="utf-8")
        resumed = self.run_narrate(*self.resume_arguments())
        self.assertNotEqual(0, resumed.returncode)
        self.assertIn("sealed Echo identity", resumed.stderr)

    def test_success_rechecks_live_resume_state_after_the_final_seal(self) -> None:
        environment = self.environment()
        environment["FAKE_TAMPER_RESUME_STATE_ON_VERIFY"] = "1"

        result = self.run_narrate(environment=environment)

        self.assertEqual(65, result.returncode, result.stderr)
        self.assertIn("resume state receipt does not match", result.stderr)
        self.assertFalse(
            list((self.run_root / "research").glob("echo-render-success-*.json"))
        )
        self.assertFalse(
            (self.run_root / "research" / "echo-render-current-accepted.json").exists()
        )

    def test_success_exit_without_complete_outputs_is_not_published(self) -> None:
        environment = self.environment()
        environment["FAKE_SKIP_AUDIT"] = "1"
        result = self.run_narrate(environment=environment)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("did not produce required output", result.stderr)
        self.assertFalse((self.run_root / "dist" / "fixture.m4b").exists())
        self.assertFalse(
            list((self.run_root / "research").glob("echo-render-success-*.json"))
        )

    def test_output_symlink_is_rejected_without_clobbering_its_target(self) -> None:
        target = self.tmp / "outside-output"
        target.mkdir()
        marker = target / "marker"
        marker.write_bytes(b"do not replace")
        output_root = self.run_root / "dist" / "echo-renders"
        output_root.symlink_to(target, target_is_directory=True)
        result = self.run_narrate()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("governed artifact directory is unsafe", result.stderr)
        self.assertEqual(b"do not replace", marker.read_bytes())
        self.assertTrue(output_root.is_symlink())

    def test_success_receipt_binds_final_media_and_audit(self) -> None:
        result = self.run_narrate()
        self.assertEqual(0, result.returncode, result.stderr)
        receipts = list((self.run_root / "research").glob("echo-render-success-*.json"))
        self.assertEqual(1, len(receipts))
        receipt = json.loads(receipts[0].read_text(encoding="utf-8"))
        self.assertEqual(3, receipt["schemaVersion"])
        state_receipt = next(
            (self.run_root / "research").glob("echo-resume-state-*.json")
        )
        self.assertIn("resumeStateFileName", receipt)
        self.assertEqual(state_receipt.name, receipt["resumeStateFileName"])
        self.assertEqual(
            hashlib.sha256(state_receipt.read_bytes()).hexdigest(),
            receipt["resumeStateSHA256"],
        )
        for field in ("audiobookSHA256", "sidecarSHA256", "auditSHA256"):
            self.assertRegex(receipt[field], r"^[0-9a-f]{64}$")

        identity = {
            "rendererSchemaVersion": 1,
            "rendererRoot": str(self.renderer_root),
            "rendererBuildRoot": str(self.renderer_build_root),
            "installerSourceSHA": self.installer_source_sha,
            "echoSourceSHA": self.source_sha,
            "rendererManifestSHA256": self.renderer_manifest_sha,
            "echoCLI_SHA256": hashlib.sha256(self.cli.read_bytes()).hexdigest(),
            "echoResourcesSHA256": receipt["echoResourcesSHA256"],
            "echoRenderVersion": 12,
            "modelPolicyRevision": self.model_policy_revision,
            "modelExpectedByteCount": self.model_expected_byte_count,
            "modelBytesAttested": False,
        }
        for path in (
            state_receipt,
            self.run_root / "research" / "echo-render-current-attempt.json",
            receipts[0],
            self.run_root / "research" / "echo-render-current-accepted.json",
        ):
            with self.subTest(receipt=path.name):
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(identity, {key: payload[key] for key in identity})
                self.assertIs(payload["modelBytesAttested"], False)

        run_id = receipt["runID"]
        self.assertRegex(
            run_id,
            rf"^[0-9a-f]{{12}}-[0-9a-f]{{12}}-[0-9a-f]{{12}}-"
            rf"{self.renderer_manifest_sha[:12]}-{self.source_sha}-am_michael$",
        )

        input_receipt = next(
            (self.run_root / "research").glob("echo-render-inputs-*.env")
        )
        input_fields = dict(
            line.split("=", 1)
            for line in input_receipt.read_text(encoding="utf-8").splitlines()
        )
        unleased_record = subprocess.run(
            [
                "/usr/local/bin/python3",
                str(STATE_HELPER),
                "record-state",
                *self.renderer_state_arguments(identity),
                "--work",
                input_fields["work_dir"],
                "--db",
                input_fields["narration_db"],
                "--receipt",
                str(self.run_root / "research" / "forged-resume-state.json"),
                "--epub",
                str(self.run_root / "dist" / "fixture.epub"),
                "--source-sha",
                self.source_sha,
                "--voice",
                "am_michael",
                "--render-version",
                input_fields["render_version"],
                "--input-receipt",
                str(input_receipt),
                "--lock-root",
                str(self.lease_root),
            ],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(0, unleased_record.returncode)
        self.assertIn(
            "missing inherited FD-backed lease capability", unleased_record.stderr
        )

        attempt = self.run_root / "research" / "echo-render-current-attempt.json"
        selector = self.run_root / "research" / "echo-render-current-accepted.json"
        selector_payload = json.loads(selector.read_text(encoding="utf-8"))
        artifact_root = (
            self.run_root / "dist" / selector_payload["artifactRelativePath"]
        )
        selection_resource = self.run_root / "research" / "echo-render-selection"
        forged_success = self.run_root / "research" / "forged-success.json"
        partially_leased_command = [
            str(LEASE_HELPER),
            "--lock-root",
            str(self.lease_root),
        ]
        for resource in (
            artifact_root / "fixture.m4b",
            artifact_root / "fixture.alignment.json",
            artifact_root / "fixture.pronunciation-audit.json",
            artifact_root / "fixture.pronunciation-reel.m4b",
            selection_resource,
        ):
            partially_leased_command.extend(("--resource", str(resource)))
        partially_leased_command.extend(
            (
                "--",
                "/usr/local/bin/python3",
                str(STATE_HELPER),
                "write-success",
                *self.renderer_state_arguments(identity),
                "--attempt-id",
                selector_payload["attemptID"],
                "--run-id",
                selector_payload["runID"],
                "--receipt",
                str(forged_success),
                "--attempt-receipt",
                str(attempt),
                "--input-receipt",
                str(input_receipt),
                "--epub",
                str(self.run_root / "dist" / "fixture.epub"),
                "--artifact-relative-path",
                selector_payload["artifactRelativePath"],
                "--state-receipt",
                str(state_receipt),
                "--work",
                input_fields["work_dir"],
                "--db",
                input_fields["narration_db"],
                "--source-sha",
                self.source_sha,
                "--voice",
                "am_michael",
                "--render-version",
                input_fields["render_version"],
                "--audiobook",
                str(artifact_root / "fixture.m4b"),
                "--sidecar",
                str(artifact_root / "fixture.alignment.json"),
                "--audit",
                str(artifact_root / "fixture.pronunciation-audit.json"),
                "--reel",
                str(artifact_root / "fixture.pronunciation-reel.m4b"),
                "--selection-resource",
                str(selection_resource),
                "--lock-root",
                str(self.lease_root),
            )
        )
        partially_leased = subprocess.run(
            partially_leased_command, capture_output=True, text=True
        )
        self.assertNotEqual(0, partially_leased.returncode)
        self.assertIn("does not cover", partially_leased.stderr)
        self.assertTrue(
            input_fields["work_dir"] in partially_leased.stderr
            or input_fields["narration_db"] in partially_leased.stderr
        )
        self.assertFalse(forged_success.exists())

        command = [
            "/usr/local/bin/python3",
            str(STATE_HELPER),
            "verify-delivery",
            *self.renderer_state_arguments(identity),
            "--voice",
            "am_michael",
            "--attempt",
            str(attempt),
            "--selector",
            str(selector),
            "--receipt",
            str(receipts[0]),
            "--input-receipt",
            str(input_receipt),
            "--state-receipt",
            str(state_receipt),
            "--epub",
            str(self.run_root / "dist" / "fixture.epub"),
            "--audiobook",
            str(artifact_root / "fixture.m4b"),
            "--sidecar",
            str(artifact_root / "fixture.alignment.json"),
            "--audit",
            str(artifact_root / "fixture.pronunciation-audit.json"),
            "--reel",
            str(artifact_root / "fixture.pronunciation-reel.m4b"),
        ]
        verified = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(0, verified.returncode, verified.stderr)

        original_state = state_receipt.read_bytes()
        state_receipt.write_bytes(b"X" * len(original_state))
        tampered_state = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(0, tampered_state.returncode)
        self.assertIn("resume-state receipt SHA-256 differs", tampered_state.stderr)
        state_receipt.unlink()
        missing_state = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(0, missing_state.returncode)
        self.assertIn("resume-state receipt is missing", missing_state.stderr)
        saved_state = self.tmp / state_receipt.name
        saved_state.write_bytes(original_state)
        state_receipt.symlink_to(saved_state)
        symlinked_state = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(0, symlinked_state.returncode)
        self.assertIn(
            "resume-state receipt must not be a symlink", symlinked_state.stderr
        )
        state_receipt.unlink()
        state_receipt.write_bytes(original_state)

        (artifact_root / "fixture.alignment.json").write_text(
            '{"tampered":true}\n', encoding="utf-8"
        )
        tampered = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(0, tampered.returncode)
        self.assertIn("SHA-256 differs", tampered.stderr)

    def test_chapter_voice_plan_is_forwarded_and_bound_to_run_and_resume(
        self,
    ) -> None:
        narrate_log = self.tmp / "mixed-voice-narrate.log"
        environment = self.environment()
        environment["FAKE_NARRATE_LOG"] = str(narrate_log)
        result = self.run_narrate(
            "--chapter-voice",
            "1=af_heart",
            environment=environment,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        arguments = narrate_log.read_text(encoding="utf-8")
        self.assertIn("ARG=--chapter-voice\nARG=1=af_heart", arguments)

        research = self.run_root / "research"
        input_receipt = next(research.glob("echo-render-inputs-*.env"))
        input_fields = dict(
            line.split("=", 1)
            for line in input_receipt.read_text(encoding="utf-8").splitlines()
        )
        self.assertEqual("1=af_heart", input_fields["chapter_voices"])
        self.assertRegex(input_fields["voice_plan_sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(
            f"plan-{input_fields['voice_plan_sha256'][:12]}",
            input_fields["voice_plan_id"],
        )
        self.assertTrue(
            input_fields["run_id"].endswith(f"-{input_fields['voice_plan_id']}")
        )

        state_path = next(research.glob("echo-resume-state-*.json"))
        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(3, state["schemaVersion"])
        self.assertEqual({"1": "af_heart"}, state["chapterVoices"])
        self.assertEqual(
            input_fields["voice_plan_sha256"], state["voicePlanSHA256"]
        )

        changed = self.run_narrate(
            "--resume",
            "--resume-state",
            str(state_path),
            "--chapter-voice",
            "1=af_bella",
            environment=environment,
        )
        self.assertNotEqual(0, changed.returncode)
        self.assertIn("canonical current-run receipt", changed.stderr)

    def test_block_voice_plan_is_sealed_and_bound_to_the_run(self) -> None:
        plan = self.tmp / "authored-voice-plan.json"
        epub = self.run_root / "dist" / "fixture.epub"
        plan.write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "source": {"epubSHA256": hashlib.sha256(epub.read_bytes()).hexdigest()},
                    "defaultSpeakerID": "narrator",
                    "speakers": [{"id": "narrator", "voiceID": "am_michael"}],
                    "assignments": [],
                }
            ),
            encoding="utf-8",
        )
        environment = self.environment()
        environment["VOICE_PLAN_SOURCE"] = str(plan)
        result = self.run_preflight(environment=environment)
        self.assertEqual(0, result.returncode, result.stderr)
        fields = dict(
            line.split("=", 1)
            for line in next((self.run_root / "research").glob("echo-render-inputs-*.env"))
            .read_text(encoding="utf-8")
            .splitlines()
        )
        self.assertEqual("block", fields["voice_plan_mode"])
        self.assertEqual("", fields["chapter_voices"])
        self.assertTrue(Path(fields["voice_plan_canonical_path"]).is_file())
        self.assertTrue(Path(fields["voice_plan_resolution_path"]).is_file())

    def test_block_capture_schema_2_seals_schema_4_state_and_success_receipts(
        self,
    ) -> None:
        """Schema-2 Echo captures carry opaque block-plan evidence into receipts."""
        plan = self.write_block_voice_plan("schema-2-capture-plan.json")
        # The legacy state implementation derives this chapter-mode hash before
        # it reaches its schema-1 marker guard. Keep the resolved fixture equal
        # to that legacy value so this RED test proves the intended boundary.
        self.fake_voice_plan_sha.write_text(
            hashlib.sha256(b"default=am_michael\n").hexdigest() + "\n",
            encoding="utf-8",
        )

        result = self.run_narrate("--voice-plan", str(plan))

        self.assertEqual(0, result.returncode, result.stderr)
        research = self.run_root / "research"
        input_receipt = next(research.glob("echo-render-inputs-*.env"))
        fields = self.receipt_fields(input_receipt)
        marker = next(self.run_root.glob("audio-work-*/.anchors-ch0.json"))
        marker_payload = json.loads(marker.read_text(encoding="utf-8"))
        identity = marker_payload["identity"]
        self.assertEqual(2, identity["schemaVersion"])
        self.assertEqual(fields["voice_plan_sha256"], identity["voicePlanSHA256"])
        self.assertRegex(identity["chapterVoicePlanSHA256"], r"^[0-9a-f]{64}$")

        state = json.loads(
            next(research.glob("echo-resume-state-*.json")).read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(4, state["schemaVersion"])
        self.assertEqual(
            {
                "schemaVersion",
                "rendererSchemaVersion",
                "rendererRoot",
                "rendererBuildRoot",
                "installerSourceSHA",
                "echoSourceSHA",
                "rendererManifestSHA256",
                "echoCLI_SHA256",
                "echoResourcesSHA256",
                "echoRenderVersion",
                "modelPolicyRevision",
                "modelExpectedByteCount",
                "modelBytesAttested",
                "sourceFingerprint",
                "voice",
                "voicePlanMode",
                "voicePlanID",
                "voicePlanSHA256",
                "voicePlanBlockCount",
                "voicePlanCanonicalFileName",
                "voicePlanCanonicalSHA256",
                "voicePlanResolutionFileName",
                "voicePlanResolutionSHA256",
                "renderVersion",
                "captureSetID",
                "inputReceiptSHA256",
                "databaseSHA256",
                "databaseByteCount",
                "captures",
            },
            set(state),
        )
        self.assertEqual(1, len(state["captures"]))
        self.assertEqual(
            {
                "chapterIndex",
                "markerFileName",
                "markerSHA256",
                "audioFileName",
                "audioSHA256",
                "payloadSHA256",
            },
            set(state["captures"][0]),
        )

        success = json.loads(
            next(research.glob("echo-render-success-*.json")).read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(4, success["schemaVersion"])
        self.assertEqual(
            {
                "schemaVersion",
                "rendererSchemaVersion",
                "rendererRoot",
                "rendererBuildRoot",
                "installerSourceSHA",
                "echoSourceSHA",
                "rendererManifestSHA256",
                "echoCLI_SHA256",
                "echoResourcesSHA256",
                "echoRenderVersion",
                "modelPolicyRevision",
                "modelExpectedByteCount",
                "modelBytesAttested",
                "attemptID",
                "runID",
                "attemptReceiptSHA256",
                "inputReceiptFileName",
                "inputReceiptSHA256",
                "sourceEPUBFileName",
                "sourceEPUBSHA256",
                "artifactRelativePath",
                "resumeStateFileName",
                "resumeStateSHA256",
                "audiobookFileName",
                "audiobookSHA256",
                "sidecarFileName",
                "sidecarSHA256",
                "auditFileName",
                "auditSHA256",
                "voicePlanMode",
                "voicePlanID",
                "voicePlanSHA256",
                "voicePlanBlockCount",
                "voicePlanCanonicalFileName",
                "voicePlanCanonicalSHA256",
                "voicePlanResolutionFileName",
                "voicePlanResolutionSHA256",
            },
            set(success),
        )

    def test_block_state_rejects_capture_identity_and_content_drift(self) -> None:
        """Each schema-2 marker field protects resume independently."""
        plan = self.write_block_voice_plan("capture-drift-plan.json")
        initial = self.run_narrate("--voice-plan", str(plan))
        self.assertEqual(0, initial.returncode, initial.stderr)
        research = self.run_root / "research"
        state = next(research.glob("echo-resume-state-*.json"))
        input_receipt = next(research.glob("echo-render-inputs-*.env"))
        work = Path(self.receipt_fields(input_receipt)["work_dir"])
        marker = work / ".anchors-ch0.json"
        audio = work / "chapter-0.m4a"
        original_marker = marker.read_bytes()
        original_audio = audio.read_bytes()

        def mutate_schema_one(payload: dict[str, object]) -> None:
            payload["identity"]["schemaVersion"] = 1

        def mutate_wrong_plan_hash(payload: dict[str, object]) -> None:
            payload["identity"]["voicePlanSHA256"] = "f" * 64

        def mutate_missing_plan_hash(payload: dict[str, object]) -> None:
            payload["identity"].pop("voicePlanSHA256")

        def mutate_chapter_digest(payload: dict[str, object]) -> None:
            payload["identity"]["chapterVoicePlanSHA256"] = "not-a-digest"

        def mutate_byte_count(payload: dict[str, object]) -> None:
            payload["identity"]["audioFileByteCount"] += 1

        cases = (
            ("schema-1-in-block", mutate_schema_one, "capture schema 2"),
            ("wrong-plan-hash", mutate_wrong_plan_hash, "voice-plan SHA-256 differs"),
            ("missing-plan-hash", mutate_missing_plan_hash, "voice-plan SHA-256 differs"),
            ("malformed-chapter-digest", mutate_chapter_digest, "chapterVoicePlanSHA256"),
            ("wrong-audio-byte-count", mutate_byte_count, "audio size differs"),
        )
        for name, mutate, expected in cases:
            with self.subTest(name=name):
                payload = json.loads(original_marker)
                mutate(payload)
                marker.write_text(json.dumps(payload), encoding="utf-8")
                result = self.verify_state_command(state, input_receipt, block=True)
                self.assertNotEqual(0, result.returncode)
                self.assertIn(expected, result.stderr)
                marker.write_bytes(original_marker)

        payload = json.loads(original_marker)
        payload["unboundMarkerMutation"] = True
        marker.write_text(json.dumps(payload), encoding="utf-8")
        marker_drift = self.verify_state_command(state, input_receipt, block=True)
        self.assertNotEqual(0, marker_drift.returncode)
        self.assertIn("resume state receipt does not match", marker_drift.stderr)
        marker.write_bytes(original_marker)

        audio.write_bytes(b"X" * len(original_audio))
        audio_drift = self.verify_state_command(state, input_receipt, block=True)
        self.assertNotEqual(0, audio_drift.returncode)
        self.assertIn("audio SHA-256 differs", audio_drift.stderr)
        audio.write_bytes(original_audio)

        duplicate = json.loads(original_marker)
        duplicate_audio = work / "chapter-1.m4a"
        duplicate_audio.write_bytes(original_audio)
        duplicate["identity"].update(
            {
                "chapterIndex": 1,
                "captureSetID": "a" * 64,
                "audioFileName": duplicate_audio.name,
                "audioSHA256": hashlib.sha256(duplicate_audio.read_bytes()).hexdigest(),
            }
        )
        duplicate_marker = work / ".anchors-ch1.json"
        duplicate_marker.write_text(json.dumps(duplicate), encoding="utf-8")
        capture_set_drift = self.verify_state_command(state, input_receipt, block=True)
        self.assertNotEqual(0, capture_set_drift.returncode)
        self.assertIn("different capture sets", capture_set_drift.stderr)

    def test_block_capture_snapshots_keep_marker_and_database_bytes_stable(self) -> None:
        """One descriptor must bind each marker/database hash and byte count."""
        plan = self.write_block_voice_plan("stable-capture-plan.json")
        initial = self.run_narrate("--voice-plan", str(plan))
        self.assertEqual(0, initial.returncode, initial.stderr)
        research = self.run_root / "research"
        state = json.loads(
            next(research.glob("echo-resume-state-*.json")).read_text(
                encoding="utf-8"
            )
        )
        input_receipt = next(research.glob("echo-render-inputs-*.env"))
        fields = self.receipt_fields(input_receipt)
        work = Path(fields["work_dir"])
        database = Path(fields["narration_db"])
        marker = work / ".anchors-ch0.json"
        namespace = self.state_namespace()
        capture_snapshot = namespace["capture_snapshot"]
        function_globals = capture_snapshot.__globals__
        original_open_regular = function_globals["open_regular"]
        identity = self.renderer_identity_from_receipt(state)
        block_plan = {
            key: state[key]
            for key in (
                "voicePlanMode",
                "voicePlanID",
                "voicePlanSHA256",
                "voicePlanBlockCount",
                "voicePlanCanonicalFileName",
                "voicePlanCanonicalSHA256",
                "voicePlanResolutionFileName",
                "voicePlanResolutionSHA256",
            )
        }

        def snapshot() -> dict[str, object]:
            return capture_snapshot(
                work,
                database,
                self.run_root / "dist" / "fixture.epub",
                self.source_sha,
                fields["voice"],
                [],
                fields["voice_plan_sha256"],
                int(fields["render_version"]),
                input_receipt,
                identity,
                block_plan,
            )

        original_marker = marker.read_bytes()
        replacement_marker = self.tmp / "replacement-marker.json"
        replacement_marker.write_bytes(original_marker + b" \n")
        marker_swapped = False

        def swap_marker_after_open(path: Path, label: str) -> int:
            nonlocal marker_swapped
            descriptor = original_open_regular(path, label)
            if path == marker and label == "capture marker" and not marker_swapped:
                marker_swapped = True
                os.replace(replacement_marker, marker)
            return descriptor

        function_globals["open_regular"] = swap_marker_after_open
        marker_snapshot = snapshot()
        self.assertTrue(marker_swapped, "marker swap hook did not run")
        self.assertEqual(
            hashlib.sha256(original_marker).hexdigest(),
            marker_snapshot["captures"][0]["markerSHA256"],
        )

        marker.write_bytes(original_marker)
        original_database = database.read_bytes()
        replacement_database = self.tmp / "replacement-database.sqlite"
        replacement_database.write_bytes(b"replacement database with different size")
        database_swapped = False

        def swap_database_after_open(path: Path, label: str) -> int:
            nonlocal database_swapped
            descriptor = original_open_regular(path, label)
            if path == database and not database_swapped:
                database_swapped = True
                os.replace(replacement_database, database)
            return descriptor

        function_globals["open_regular"] = swap_database_after_open
        database_snapshot = snapshot()
        self.assertTrue(database_swapped, "database swap hook did not run")
        self.assertEqual(
            hashlib.sha256(original_database).hexdigest(),
            database_snapshot["databaseSHA256"],
        )
        self.assertEqual(len(original_database), database_snapshot["databaseByteCount"])

        database.write_bytes(original_database)
        audio = work / "chapter-0.m4a"
        original_audio = audio.read_bytes()
        replacement_audio = self.tmp / "replacement-audio.m4a"
        replacement_audio.write_bytes(b"replacement audio bytes")
        audio_stat_seen = False
        audio_swapped = False
        original_path_stat = Path.stat

        def observe_audio_stat(path: Path, *args: object, **kwargs: object) -> os.stat_result:
            nonlocal audio_stat_seen
            result = original_path_stat(path, *args, **kwargs)
            if path == audio:
                audio_stat_seen = True
            return result

        def swap_audio_around_open(path: Path, label: str) -> int:
            nonlocal audio_swapped
            if path == audio and audio_stat_seen:
                os.replace(replacement_audio, audio)
                audio_swapped = True
                return original_open_regular(path, label)
            descriptor = original_open_regular(path, label)
            if path == audio and not audio_swapped:
                os.replace(replacement_audio, audio)
                audio_swapped = True
            return descriptor

        function_globals["open_regular"] = swap_audio_around_open
        Path.stat = observe_audio_stat
        try:
            audio_snapshot = snapshot()
        finally:
            Path.stat = original_path_stat
        self.assertTrue(audio_swapped, "audio swap hook did not run")
        self.assertEqual(
            hashlib.sha256(original_audio).hexdigest(),
            audio_snapshot["captures"][0]["audioSHA256"],
        )

    def test_block_receipt_readers_reject_duplicate_keys_before_cross_checks(self) -> None:
        """The governed attempt, state, success, and selector are closed JSON objects."""
        plan = self.write_block_voice_plan("duplicate-receipt-plan.json")
        initial = self.run_narrate("--voice-plan", str(plan), environment=self.environment())
        self.assertEqual(0, initial.returncode, initial.stderr)
        research = self.run_root / "research"
        paths = (
            (research / "echo-render-current-attempt.json", "current-attempt receipt", "schemaVersion"),
            (next(research.glob("echo-resume-state-*.json")), "resume-state receipt", "voicePlanSHA256"),
            (next(research.glob("echo-render-success-*.json")), "render-success receipt", "voicePlanSHA256"),
            (research / "echo-render-current-accepted.json", "current-accepted selector", "schemaVersion"),
        )
        namespace = self.state_namespace()
        json_object = namespace["json_object"]
        state_error = namespace["StateError"]
        for path, label, key in paths:
            with self.subTest(label=label):
                raw = path.read_text(encoding="utf-8")
                duplicate = raw.replace(
                    f'"{key}":', f'"{key}":', 1
                )
                value_start = duplicate.index(f'"{key}":')
                value_end = duplicate.find(",", value_start)
                if value_end == -1:
                    value_end = duplicate.find("}", value_start)
                duplicate = (
                    duplicate[:value_end]
                    + ","
                    + duplicate[value_start:value_end]
                    + duplicate[value_end:]
                )
                path.write_text(duplicate, encoding="utf-8")
                with self.assertRaises(state_error) as raised:
                    json_object(path, label)
                self.assertIn("duplicates key", str(raised.exception))

    def test_block_state_rejects_input_or_canonical_plan_evidence_drift(self) -> None:
        plan = self.write_block_voice_plan("plan-evidence-drift.json")
        initial = self.run_narrate("--voice-plan", str(plan))
        self.assertEqual(0, initial.returncode, initial.stderr)
        research = self.run_root / "research"
        state = next(research.glob("echo-resume-state-*.json"))
        input_receipt = next(research.glob("echo-render-inputs-*.env"))
        original_receipt = input_receipt.read_bytes()
        fields = self.receipt_fields(input_receipt)
        canonical_plan = Path(fields["voice_plan_canonical_path"])
        original_plan = canonical_plan.read_bytes()

        input_receipt.write_text(
            input_receipt.read_text(encoding="utf-8").replace(
                f"voice_plan_canonical_sha256={fields['voice_plan_canonical_sha256']}",
                "voice_plan_canonical_sha256=" + "0" * 64,
            ),
            encoding="utf-8",
        )
        input_drift = self.verify_state_command(state, input_receipt, block=True)
        self.assertNotEqual(0, input_drift.returncode)
        self.assertIn("voice_plan_canonical_sha256", input_drift.stderr)
        input_receipt.write_bytes(original_receipt)

        canonical_plan.write_bytes(b"{}\n")
        canonical_drift = self.verify_state_command(state, input_receipt, block=True)
        self.assertNotEqual(0, canonical_drift.returncode)
        self.assertIn("voice_plan_canonical_sha256", canonical_drift.stderr)
        canonical_plan.write_bytes(original_plan)

    def test_legacy_state_rejects_a_schema_2_capture(self) -> None:
        initial = self.run_narrate()
        self.assertEqual(0, initial.returncode, initial.stderr)
        research = self.run_root / "research"
        state = next(research.glob("echo-resume-state-*.json"))
        input_receipt = next(research.glob("echo-render-inputs-*.env"))
        marker = next(self.run_root.glob("audio-work-*/.anchors-ch0.json"))
        payload = json.loads(marker.read_text(encoding="utf-8"))
        payload["identity"].update(
            {
                "schemaVersion": 2,
                "voicePlanSHA256": "b" * 64,
                "chapterVoicePlanSHA256": "c" * 64,
            }
        )
        marker.write_text(json.dumps(payload), encoding="utf-8")

        result = self.verify_state_command(state, input_receipt, block=False)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("capture schema 1", result.stderr)

    def test_rejected_block_plan_cleans_all_preflight_scratch_files(self) -> None:
        """A rejected caller voice cannot leave sealed-looking plan residue behind."""
        plan = self.tmp / "authored-voice-plan.json"
        epub = self.run_root / "dist" / "fixture.epub"
        plan.write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "source": {"epubSHA256": hashlib.sha256(epub.read_bytes()).hexdigest()},
                    "defaultSpeakerID": "narrator",
                    "speakers": [{"id": "narrator", "voiceID": "am_michael"}],
                    "assignments": [],
                }
            ),
            encoding="utf-8",
        )
        environment = self.environment()
        environment.update({"VOICE_PLAN_SOURCE": str(plan), "VOICE": "af_heart"})
        result = self.run_preflight(environment=environment)
        self.assertEqual(64, result.returncode, result.stderr)
        research = self.run_root / "research"
        self.assertEqual([], list(research.glob(".echo-voice-plan*")))
        self.assertEqual([], list(research.glob("echo-render-inputs-*.env")))

    def test_outer_block_option_rejects_chapter_and_unsafe_plan_paths_without_mutation(self) -> None:
        plan = self.tmp / "voice-plan.json"
        plan.write_text("{}", encoding="utf-8")
        link = self.tmp / "voice-plan-link.json"
        link.symlink_to(plan)
        directory = self.tmp / "voice-plan-directory"
        directory.mkdir()
        cases = (
            (64, ("--voice-plan", str(plan), "--chapter-voice", "1=af_heart")),
            (64, ("--voice-plan", "relative.json")),
            (66, ("--voice-plan", str(self.tmp / "missing.json"))),
            (66, ("--voice-plan", str(directory))),
            (66, ("--voice-plan", str(link))),
        )
        for expected, arguments in cases:
            with self.subTest(arguments=arguments):
                result = self.run_narrate(*arguments)
                self.assertEqual(expected, result.returncode, result.stderr)
                research = self.run_root / "research"
                self.assertEqual([], list(research.glob("echo-render-inputs-*.env")))
                self.assertEqual([], list(research.glob(".echo-voice-plan*")))
                self.assertEqual([], list(self.run_root.glob("audio-work-*")))
                self.assertEqual([], list(self.run_root.glob("narration-*.sqlite")))

    def test_block_resolver_only_runs_while_exact_installed_build_root_is_leased(
        self,
    ) -> None:
        """A competing lease acquisition must fail at every fake resolver call."""
        plan = self.write_block_voice_plan("leased-resolver-plan.json")
        self.fake_resolve_lease_probe.touch()
        environment = self.environment()
        environment.update(
            {
                "FAKE_SKIP_CAPTURE": "1",
                "FAKE_NARRATE_EXIT": "42",
            }
        )

        result = self.run_narrate("--voice-plan", str(plan), environment=environment)

        self.assertEqual(42, result.returncode, result.stderr)
        lines = self.fake_resolve_lease_log.read_text(encoding="utf-8").splitlines()
        self.assertGreaterEqual(len(lines), 2)
        self.assertEqual(
            {f"LEASE_STATUS=75 RESOURCE={self.renderer_build_root}"}, set(lines)
        )

    def test_block_narration_uses_only_the_sealed_canonical_plan_argv(self) -> None:
        """The renderer must never receive a caller-controlled plan path or --voice."""
        plan = self.write_block_voice_plan("mutable-caller-plan.json")
        narrate_log = self.tmp / "block-narrate-arguments.log"
        environment = self.environment()
        environment.update(
            {
                "FAKE_NARRATE_LOG": str(narrate_log),
                "FAKE_SKIP_CAPTURE": "1",
                "FAKE_NARRATE_EXIT": "42",
            }
        )

        result = self.run_narrate("--voice-plan", str(plan), environment=environment)

        self.assertEqual(42, result.returncode, result.stderr)
        arguments = [
            line.removeprefix("ARG=")
            for line in narrate_log.read_text(encoding="utf-8").splitlines()
            if line.startswith("ARG=")
        ]
        receipt = next((self.run_root / "research").glob("echo-render-inputs-*.env"))
        fields = self.receipt_fields(receipt)
        canonical_plan = Path(fields["voice_plan_canonical_path"])
        self.assertNotEqual(plan, canonical_plan)
        self.assertIn("--voice-plan", arguments)
        self.assertEqual(
            str(canonical_plan), arguments[arguments.index("--voice-plan") + 1]
        )
        self.assertNotIn("--voice", arguments)
        self.assertNotIn(str(plan), arguments)

    def test_changed_block_resolver_hash_fans_out_to_every_run_scoped_path(
        self,
    ) -> None:
        """A new Echo receipt identity must select a wholly new governed run."""
        plan = self.write_block_voice_plan("hash-fanout-plan.json")
        research = self.run_root / "research"

        def render_for(resolved_sha: str) -> tuple[dict[str, str], Path, Path, Path]:
            self.fake_voice_plan_sha.write_text(resolved_sha + "\n", encoding="utf-8")
            narrate_log = self.tmp / f"hash-fanout-{resolved_sha[-1]}.log"
            environment = self.environment()
            environment.update(
                {
                    "FAKE_NARRATE_LOG": str(narrate_log),
                    "FAKE_SKIP_CAPTURE": "1",
                    "FAKE_NARRATE_EXIT": "42",
                }
            )
            result = self.run_narrate(
                "--voice-plan", str(plan), environment=environment
            )
            self.assertEqual(42, result.returncode, result.stderr)
            receipt = next(
                path
                for path in research.glob("echo-render-inputs-*.env")
                if self.receipt_fields(path)["voice_plan_sha256"] == resolved_sha
            )
            fields = self.receipt_fields(receipt)
            narrate_environment = dict(
                pair.split("=", 1)
                for pair in next(
                    line.removeprefix("ENV=")
                    for line in narrate_log.read_text(encoding="utf-8").splitlines()
                    if line.startswith("ENV=")
                ).split()
            )
            self.assertEqual(fields["run_id"], narrate_environment["RUN_ID"])
            self.assertEqual(
                str(receipt), narrate_environment["INPUT_RECEIPT"]
            )
            state = Path(narrate_environment["STATE_RECEIPT"])
            artifact_root = Path(narrate_environment["ARTIFACT_ROOT"])
            return fields, receipt, state, artifact_root

        shared_prefix = "0123456789ab"
        first = render_for(shared_prefix + "b" * 52)
        second = render_for(shared_prefix + "c" * 52)
        first_fields, first_receipt, first_state, first_artifact_root = first
        second_fields, second_receipt, second_state, second_artifact_root = second

        self.assertNotEqual(
            first_fields["voice_plan_sha256"], second_fields["voice_plan_sha256"]
        )
        self.assertEqual(
            first_fields["voice_plan_id"], second_fields["voice_plan_id"]
        )
        for field in (
            "run_id",
            "work_dir",
            "narration_db",
            "voice_plan_canonical_path",
            "voice_plan_resolution_path",
        ):
            with self.subTest(field=field):
                self.assertNotEqual(first_fields[field], second_fields[field])
        self.assertNotEqual(first_receipt, second_receipt)
        self.assertNotEqual(first_state, second_state)
        self.assertNotEqual(first_artifact_root, second_artifact_root)
        self.assertEqual(
            self.run_root / "dist" / "echo-renders" / first_fields["run_id"],
            first_artifact_root.parent,
        )
        self.assertEqual(
            self.run_root / "dist" / "echo-renders" / second_fields["run_id"],
            second_artifact_root.parent,
        )
        self.assertTrue(first_receipt.is_file())
        self.assertTrue(second_receipt.is_file())
        self.assertEqual(
            research / f"echo-resume-state-{first_fields['run_id']}.json", first_state
        )
        self.assertEqual(
            research / f"echo-resume-state-{second_fields['run_id']}.json", second_state
        )

    def test_equivalent_authored_block_plan_syntax_reuses_the_sealed_run(self) -> None:
        """Different authored documents reuse a run when Echo resolves them alike."""
        compact = self.write_block_voice_plan("compact-authored-plan.json")
        pretty = self.write_block_voice_plan(
            "pretty-authored-plan.json",
            sorted_keys=True,
            add_unused_speaker=True,
        )
        self.assertNotEqual(compact.read_bytes(), pretty.read_bytes())
        self.assertNotEqual(
            json.loads(compact.read_text(encoding="utf-8")),
            json.loads(pretty.read_text(encoding="utf-8")),
        )
        environment = self.environment()
        environment["VOICE_PLAN_SOURCE"] = str(compact)
        first_result = self.run_preflight(environment=environment)
        self.assertEqual(0, first_result.returncode, first_result.stderr)
        research = self.run_root / "research"
        first_receipt = next(research.glob("echo-render-inputs-*.env"))
        first_fields = self.receipt_fields(first_receipt)
        canonical_plan = Path(first_fields["voice_plan_canonical_path"])
        resolution = Path(first_fields["voice_plan_resolution_path"])
        sealed_plan_bytes = canonical_plan.read_bytes()
        sealed_resolution_bytes = resolution.read_bytes()

        environment["VOICE_PLAN_SOURCE"] = str(pretty)
        second_result = self.run_preflight(environment=environment)

        self.assertEqual(0, second_result.returncode, second_result.stderr)
        second_receipt = next(research.glob("echo-render-inputs-*.env"))
        second_fields = self.receipt_fields(second_receipt)
        self.assertEqual(first_fields, second_fields)
        self.assertEqual(canonical_plan, Path(second_fields["voice_plan_canonical_path"]))
        self.assertEqual(resolution, Path(second_fields["voice_plan_resolution_path"]))
        self.assertEqual(sealed_plan_bytes, canonical_plan.read_bytes())
        self.assertEqual(sealed_resolution_bytes, resolution.read_bytes())
        self.assertEqual(
            [canonical_plan], list(research.glob(f"{canonical_plan.name}"))
        )
        self.assertEqual([resolution], list(research.glob(f"{resolution.name}")))

    def test_block_narration_rejects_plan_or_resolution_mutation_after_render(
        self,
    ) -> None:
        """Post-render re-attestation must fail closed on either sealed byte drift."""
        for label, field, replacement in (
            ("plan", "voice_plan_canonical_path", b"{\"tampered\":true}\n"),
            (
                "resolution",
                "voice_plan_resolution_path",
                b"{\"tampered\":true}\n",
            ),
        ):
            with self.subTest(label=label):
                plan = self.write_block_voice_plan(f"{label}-drift-plan.json")
                resolved_sha = ("d" if label == "plan" else "e") * 64
                self.fake_voice_plan_sha.write_text(
                    resolved_sha + "\n",
                    encoding="utf-8",
                )
                ready = self.tmp / f"{label}-drift-ready"
                release = self.tmp / f"{label}-drift-release"
                environment = self.environment()
                environment.update(
                    {
                        "FAKE_NARRATE_READY": str(ready),
                        "FAKE_NARRATE_RELEASE": str(release),
                        "FAKE_SKIP_CAPTURE": "1",
                        "FAKE_NARRATE_EXIT": "42",
                    }
                )
                process = subprocess.Popen(
                    [str(NARRATE_WRAPPER), "--voice-plan", str(plan)],
                    cwd=self.explainer,
                    env=environment,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                self.addCleanup(lambda: process.poll() is None and process.kill())
                self.wait_for_path(ready, process)
                receipt = next(
                    path
                    for path in (self.run_root / "research").glob(
                        "echo-render-inputs-*.env"
                    )
                    if self.receipt_fields(path)["voice_plan_sha256"] == resolved_sha
                )
                Path(self.receipt_fields(receipt)[field]).write_bytes(replacement)
                release.touch()
                stdout, stderr = process.communicate(timeout=WAIT_TIMEOUT)

                self.assertEqual(65, process.returncode, f"{stdout}\n{stderr}")
                self.assertIn(
                    "sealed block voice-plan bytes changed while narration lease was held",
                    stderr,
                )
                self.assertFalse(list((self.run_root / "dist").glob("echo-renders/**/*")))

    def test_legacy_wrapper_run_ids_and_input_receipts_are_byte_for_byte_unchanged(
        self,
    ) -> None:
        """Uniform and chapter wrapper receipts remain the pre-block-mode bytes."""
        uniform_sha = hashlib.sha256(b"default=am_michael\n").hexdigest()
        uniform_run_id, uniform_bytes = self.expected_legacy_input_receipt(
            chapter_voices="",
            voice_plan_sha=uniform_sha,
            voice_plan_id="am_michael",
        )

        uniform = self.run_narrate()

        self.assertEqual(0, uniform.returncode, uniform.stderr)
        uniform_receipt = (
            self.run_root / "research" / f"echo-render-inputs-{uniform_run_id}.env"
        )
        self.assertEqual(uniform_bytes, uniform_receipt.read_bytes())

        chapter_sha = hashlib.sha256(
            b"default=am_michael\n1=af_heart\n"
        ).hexdigest()
        chapter_id = f"plan-{chapter_sha[:12]}"
        chapter_run_id, chapter_bytes = self.expected_legacy_input_receipt(
            chapter_voices="1=af_heart",
            voice_plan_sha=chapter_sha,
            voice_plan_id=chapter_id,
        )

        chapter = self.run_narrate("--chapter-voice", "1=af_heart")

        self.assertEqual(0, chapter.returncode, chapter.stderr)
        chapter_receipt = (
            self.run_root / "research" / f"echo-render-inputs-{chapter_run_id}.env"
        )
        self.assertNotEqual(uniform_run_id, chapter_run_id)
        self.assertEqual(chapter_bytes, chapter_receipt.read_bytes())

    def test_legacy_schema_3_resume_and_success_receipts_are_byte_goldens(self) -> None:
        """Task-3 block evidence cannot alter either legacy schema-3 wire receipt."""
        uniform_sha = hashlib.sha256(b"default=am_michael\n").hexdigest()
        chapter_sha = hashlib.sha256(
            b"default=am_michael\n1=af_heart\n"
        ).hexdigest()
        cases = (
            (
                (),
                "",
                uniform_sha,
                "am_michael",
                {},
                "am_michael",
            ),
            (
                ("--chapter-voice", "1=af_heart"),
                "1=af_heart",
                chapter_sha,
                f"plan-{chapter_sha[:12]}",
                {"1": "af_heart"},
                "af_heart",
            ),
        )
        for (
            arguments,
            chapter_voice_text,
            plan_sha,
            plan_id,
            chapter_voices,
            capture_voice,
        ) in cases:
            with self.subTest(arguments=arguments):
                run_id, input_bytes = self.expected_legacy_input_receipt(
                    chapter_voices=chapter_voice_text,
                    voice_plan_sha=plan_sha,
                    voice_plan_id=plan_id,
                )
                result = self.run_narrate(*arguments)
                self.assertEqual(0, result.returncode, result.stderr)
                research = self.run_root / "research"
                input_receipt = research / f"echo-render-inputs-{run_id}.env"
                self.assertEqual(input_bytes, input_receipt.read_bytes())
                attempt = json.loads(
                    (research / "echo-render-current-attempt.json").read_text(
                        encoding="utf-8"
                    )
                )
                state_bytes, success_bytes = self.expected_legacy_state_and_success_receipts(
                    run_id=run_id,
                    input_receipt=input_bytes,
                    voice_plan_sha=plan_sha,
                    chapter_voices=chapter_voices,
                    capture_voice=capture_voice,
                    attempt_id=attempt["attemptID"],
                )
                state = research / f"echo-resume-state-{run_id}.json"
                success = research / (
                    f"echo-render-success-{run_id}-{attempt['attemptID']}.json"
                )
                self.assertEqual(state_bytes, state.read_bytes())
                self.assertEqual(success_bytes, success.read_bytes())

    def test_renderer_identity_changes_prevent_resume_and_delivery_reuse(self) -> None:
        result = self.run_narrate()
        self.assertEqual(0, result.returncode, result.stderr)
        research = self.run_root / "research"
        state = next(research.glob("echo-resume-state-*.json"))
        attempt = research / "echo-render-current-attempt.json"
        selector = research / "echo-render-current-accepted.json"
        accepted = json.loads(selector.read_text(encoding="utf-8"))
        success = research / accepted["successReceiptFileName"]
        identity_keys = (
            "rendererSchemaVersion",
            "rendererRoot",
            "rendererBuildRoot",
            "installerSourceSHA",
            "echoSourceSHA",
            "rendererManifestSHA256",
            "echoCLI_SHA256",
            "echoResourcesSHA256",
            "echoRenderVersion",
            "modelPolicyRevision",
            "modelExpectedByteCount",
            "modelBytesAttested",
        )
        identity = {key: accepted[key] for key in identity_keys}
        input_receipt = research / accepted["inputReceiptFileName"]
        input_fields = dict(
            line.split("=", 1)
            for line in input_receipt.read_text(encoding="utf-8").splitlines()
        )
        artifact_root = self.run_root / "dist" / accepted["artifactRelativePath"]

        state_base = [
            "/usr/local/bin/python3",
            str(STATE_HELPER),
            "verify-state",
            "--work",
            input_fields["work_dir"],
            "--db",
            input_fields["narration_db"],
            "--receipt",
            str(state),
            "--epub",
            str(self.run_root / "dist" / "fixture.epub"),
            "--source-sha",
            self.source_sha,
            "--voice",
            "am_michael",
            "--render-version",
            input_fields["render_version"],
            "--input-receipt",
            str(input_receipt),
        ]
        delivery_base = [
            "/usr/local/bin/python3",
            str(STATE_HELPER),
            "verify-delivery",
            "--voice",
            "am_michael",
            "--attempt",
            str(attempt),
            "--selector",
            str(selector),
            "--receipt",
            str(success),
            "--input-receipt",
            str(input_receipt),
            "--state-receipt",
            str(state),
            "--epub",
            str(self.run_root / "dist" / "fixture.epub"),
            "--audiobook",
            str(artifact_root / "fixture.m4b"),
            "--sidecar",
            str(artifact_root / "fixture.alignment.json"),
            "--audit",
            str(artifact_root / "fixture.pronunciation-audit.json"),
            "--reel",
            str(artifact_root / "fixture.pronunciation-reel.m4b"),
        ]
        mutations = {
            "installerSourceSHA": "8" * 40,
            "rendererManifestSHA256": "8" * 64,
            "echoCLI_SHA256": "8" * 64,
            "echoResourcesSHA256": "8" * 64,
            "modelPolicyRevision": "different-policy-revision",
            "modelExpectedByteCount": self.model_expected_byte_count + 1,
            "echoSourceSHA": "a" * 40,
            "voice": "am_puck",
        }
        for field, changed in mutations.items():
            with self.subTest(field=field):
                changed_identity = dict(identity)
                if field == "voice":
                    state_command = [
                        "am_puck" if argument == "am_michael" else argument
                        for argument in state_base
                    ]
                else:
                    changed_identity[field] = changed
                    state_command = list(state_base)
                    if field == "echoSourceSHA":
                        state_command[state_command.index(self.source_sha)] = "a" * 40
                resume = subprocess.run(
                    [*state_command, *self.renderer_state_arguments(changed_identity)],
                    capture_output=True,
                    text=True,
                )
                self.assertNotEqual(0, resume.returncode, resume.stderr)
                delivery_command = [
                    "am_puck" if field == "voice" and argument == "am_michael" else argument
                    for argument in delivery_base
                ]
                delivery = subprocess.run(
                    [*delivery_command, *self.renderer_state_arguments(changed_identity)],
                    capture_output=True,
                    text=True,
                )
                self.assertNotEqual(0, delivery.returncode, delivery.stderr)

    def test_failed_newer_source_attempt_invalidates_old_delivery_acceptance(
        self,
    ) -> None:
        initial = self.run_narrate()
        self.assertEqual(0, initial.returncode, initial.stderr)
        research = self.run_root / "research"
        attempt_path = research / "echo-render-current-attempt.json"
        selector_path = research / "echo-render-current-accepted.json"
        first_attempt = json.loads(attempt_path.read_text(encoding="utf-8"))
        first_selector = json.loads(selector_path.read_text(encoding="utf-8"))
        first_artifacts = (
            self.run_root / "dist" / first_selector["artifactRelativePath"]
        )
        first_success = research / first_selector["successReceiptFileName"]

        epub = self.run_root / "dist" / "fixture.epub"
        with zipfile.ZipFile(epub, "a") as archive:
            archive.writestr("OEBPS/newer-source.txt", "newer source epub")
        failed_environment = self.environment()
        failed_environment["FAKE_NARRATE_EXIT"] = "42"
        failed = self.run_narrate(environment=failed_environment)
        self.assertEqual(42, failed.returncode, failed.stderr)

        newest_attempt = json.loads(attempt_path.read_text(encoding="utf-8"))
        self.assertNotEqual(first_attempt["attemptID"], newest_attempt["attemptID"])
        self.assertTrue((first_artifacts / "fixture.m4b").is_file())
        verify = subprocess.run(
            [
                "/usr/local/bin/python3",
                str(STATE_HELPER),
                "verify-delivery",
                *self.renderer_state_arguments(
                    {key: first_selector[key] for key in (
                        "rendererSchemaVersion",
                        "rendererRoot",
                        "rendererBuildRoot",
                        "installerSourceSHA",
                        "echoSourceSHA",
                        "rendererManifestSHA256",
                        "echoCLI_SHA256",
                        "echoResourcesSHA256",
                        "echoRenderVersion",
                        "modelPolicyRevision",
                        "modelExpectedByteCount",
                        "modelBytesAttested",
                    )}
                ),
                "--voice",
                "am_michael",
                "--attempt",
                str(attempt_path),
                "--selector",
                str(selector_path),
                "--receipt",
                str(first_success),
                "--input-receipt",
                str(research / first_selector["inputReceiptFileName"]),
                "--state-receipt",
                str(research / f"echo-resume-state-{first_selector['runID']}.json"),
                "--epub",
                str(epub),
                "--audiobook",
                str(first_artifacts / "fixture.m4b"),
                "--sidecar",
                str(first_artifacts / "fixture.alignment.json"),
                "--audit",
                str(first_artifacts / "fixture.pronunciation-audit.json"),
                "--reel",
                str(first_artifacts / "fixture.pronunciation-reel.m4b"),
            ],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(0, verify.returncode)
        self.assertIn("current attempt", verify.stderr)

    def test_lease_hashes_each_canonical_shared_resource_identity(self) -> None:
        log = self.tmp / "resources.log"
        environment = self.environment()
        environment["FAKE_NARRATE_LOG"] = str(log)
        result = self.run_narrate(environment=environment)
        self.assertEqual(0, result.returncode, result.stderr)
        arguments = [
            line.removeprefix("ARG=")
            for line in log.read_text(encoding="utf-8").splitlines()
            if line.startswith("ARG=")
        ]
        resources = (
            self.renderer_build_root,
            Path(arguments[arguments.index("--work-dir") + 1]),
            Path(arguments[arguments.index("--db") + 1]),
        )
        selector = json.loads(
            (
                self.run_root / "research" / "echo-render-current-accepted.json"
            ).read_text(encoding="utf-8")
        )
        artifact_root = self.run_root / "dist" / selector["artifactRelativePath"]
        resources += (
            artifact_root / "fixture.m4b",
            artifact_root / "fixture.alignment.json",
            artifact_root / "fixture.pronunciation-audit.json",
            artifact_root / "fixture.pronunciation-reel.m4b",
            self.run_root / "research" / "echo-render-selection",
        )
        expected = {
            hashlib.sha256(str(path.resolve()).encode("utf-8")).hexdigest() + ".lock"
            for path in resources
        }
        observed = {path.name for path in self.lease_root.glob("*.lock")}
        self.assertTrue(expected.issubset(observed))

    def test_fd_lease_survives_guardian_sigkill_until_child_exits(self) -> None:
        log = self.tmp / "sigkill.log"
        ready = self.tmp / "sigkill-ready"
        release = self.tmp / "sigkill-release"
        environment = self.environment()
        environment.update(
            {
                "FAKE_NARRATE_LOG": str(log),
                "FAKE_NARRATE_READY": str(ready),
                "FAKE_NARRATE_RELEASE": str(release),
            }
        )
        guardian = subprocess.Popen(
            [str(NARRATE_WRAPPER)],
            cwd=self.explainer,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.addCleanup(lambda: guardian.poll() is None and guardian.kill())
        self.wait_for_path(ready, guardian)
        owner = self.run_root / "research" / "echo-render-output.owner.env"
        self.assertTrue(owner.is_file())

        guardian.kill()
        guardian.wait(timeout=WAIT_TIMEOUT)
        self.assertEqual(-signal.SIGKILL, guardian.returncode)
        contender = self.run_narrate(environment=environment)
        self.assertEqual(75, contender.returncode, contender.stderr)
        self.assertIn("active narration lease", contender.stderr)
        self.assertEqual(1, log.read_text(encoding="utf-8").count("BEGIN="))

        release.touch()
        deadline = time.monotonic() + WAIT_TIMEOUT
        while owner.exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        self.assertFalse(
            owner.exists(), "orphaned child did not release owner metadata"
        )
        if guardian.stdout is not None:
            guardian.stdout.close()
        if guardian.stderr is not None:
            guardian.stderr.close()

        resumed_environment = self.environment()
        resumed_environment["FAKE_NARRATE_LOG"] = str(log)
        resumed = self.run_narrate(
            *self.resume_arguments(), environment=resumed_environment
        )
        self.assertEqual(0, resumed.returncode, resumed.stderr)


class EchoPronunciationStateCompatibilityTests(unittest.TestCase):
    def test_installed_renderer_reader_accepts_only_exact_schemas_two_through_four(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            renderer_root = root / "renderer-root"
            renderer_build_root = renderer_root / "build"
            renderer_build_root.mkdir(parents=True)
            identity = {
                "rendererSchemaVersion": 1,
                "rendererRoot": str(renderer_root),
                "rendererBuildRoot": str(renderer_build_root),
                "installerSourceSHA": "1" * 40,
                "echoSourceSHA": "2" * 40,
                "rendererManifestSHA256": "3" * 64,
                "echoCLI_SHA256": "4" * 64,
                "echoResourcesSHA256": "5" * 64,
                "echoRenderVersion": 12,
                "modelPolicyRevision": "fixture-policy",
                "modelExpectedByteCount": 1,
                "modelBytesAttested": False,
            }
            common = {
                **identity,
                "sourceFingerprint": "6" * 64,
                "voice": "am_michael",
                "renderVersion": 12,
                "captureSetID": "7" * 64,
                "inputReceiptSHA256": "8" * 64,
                "databaseSHA256": "9" * 64,
                "databaseByteCount": 0,
                "captures": [],
            }
            script_directory = str(STATE_HELPER.parent)
            sys.path.insert(0, script_directory)
            try:
                specification = importlib.util.spec_from_file_location(
                    "echo_pronunciation_state_reader_fixture", STATE_HELPER
                )
                self.assertIsNotNone(specification)
                self.assertIsNotNone(specification.loader)
                module = importlib.util.module_from_spec(specification)
                specification.loader.exec_module(module)
            finally:
                sys.path.remove(script_directory)

            payloads = {
                2: {"schemaVersion": 2, **common},
                3: {
                    "schemaVersion": 3,
                    **common,
                    "chapterVoices": {"0": "am_michael"},
                    "voicePlanSHA256": "a" * 64,
                },
                4: {
                    "schemaVersion": 4,
                    **common,
                    "voicePlanMode": "block",
                    "voicePlanID": "plan-aaaaaaaaaaaa",
                    "voicePlanSHA256": "a" * 64,
                    "voicePlanBlockCount": 2,
                    "voicePlanCanonicalFileName": "echo-voice-plan-plan-" + "a" * 64 + ".json",
                    "voicePlanCanonicalSHA256": "b" * 64,
                    "voicePlanResolutionFileName": "echo-voice-plan-resolution-plan-" + "a" * 64 + ".json",
                    "voicePlanResolutionSHA256": "c" * 64,
                },
            }
            receipt = root / "echo-resume-state.json"
            for schema_version, payload in payloads.items():
                with self.subTest(schema_version=schema_version):
                    receipt.write_bytes(canonical_json(payload))
                    self.assertEqual(
                        (identity["echoSourceSHA"], identity["rendererManifestSHA256"]),
                        module.read_installed_renderer_identity(receipt),
                    )
                    receipt.write_bytes(
                        canonical_json({**payload, "unexpected": True})
                    )
                    with self.assertRaises(ValueError):
                        module.read_installed_renderer_identity(receipt)

    def test_run_id_patterns_separate_operational_and_historical_receipts(self) -> None:
        script = """
import runpy
import sys
from pathlib import Path

helper = Path(sys.argv[1])
sys.path.insert(0, str(helper.parent))
namespace = runpy.run_path(str(helper))
pattern = namespace["RUN_ID_PATTERN"]
legacy_pattern = namespace["LEGACY_RUN_ID_PATTERN"]
commit = "d" * 40
current = f"{'a' * 12}-{'b' * 12}-{'c' * 12}-{'e' * 12}-{commit}-am_michael"
legacy = f"{'a' * 12}-{'b' * 12}-{'c' * 12}-{commit}-am_michael"
assert pattern.fullmatch(current)
assert pattern.fullmatch(legacy) is None
assert legacy_pattern.fullmatch(legacy)
assert legacy_pattern.fullmatch(current)

block = f"{'a' * 12}-{'b' * 12}-{'c' * 12}-{'e' * 12}-{commit}-plan-{'f' * 64}"
assert pattern.fullmatch(block)

dirty = f"{'a' * 12}-{'b' * 12}-{'c' * 12}-{commit}-dirty-{'9' * 8}-am_michael"
assert pattern.fullmatch(dirty) is None
assert legacy_pattern.fullmatch(dirty)
assert pattern.fullmatch(
    f"{'a' * 12}-{'b' * 12}-{'c' * 12}-unpinned-am_michael"
) is None
"""
        result = subprocess.run(
            [sys.executable, "-c", script, str(STATE_HELPER)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)

    def test_verify_delivery_remains_read_only_compatible_with_legacy_chain(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            research = root / "research"
            research.mkdir()
            run_id = (
                f"{'a' * 12}-{'b' * 12}-{'c' * 12}-{'d' * 40}-am_michael"
            )
            attempt_id = "e" * 64
            artifact_relative_path = f"echo-renders/{run_id}/{attempt_id}"
            artifacts = root / artifact_relative_path
            artifacts.mkdir(parents=True)
            input_receipt = research / f"echo-render-inputs-{run_id}.env"
            state_receipt = research / f"echo-resume-state-{run_id}.json"
            epub = root / "fixture.epub"
            audiobook = artifacts / "fixture.m4b"
            sidecar = artifacts / "fixture.alignment.json"
            audit = artifacts / "fixture.pronunciation-audit.json"
            reel = artifacts / "fixture.pronunciation-reel.m4b"
            input_receipt.write_text("legacy=true\n", encoding="utf-8")
            state_receipt.write_text('{"schemaVersion":1}\n', encoding="utf-8")
            epub.write_bytes(b"legacy epub")
            audiobook.write_bytes(b"legacy audiobook")
            sidecar.write_text("{}\n", encoding="utf-8")
            audit.write_text("{}\n", encoding="utf-8")

            digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
            attempt_payload = {
                "schemaVersion": 1,
                "attemptID": attempt_id,
                "runID": run_id,
                "inputReceiptFileName": input_receipt.name,
                "inputReceiptSHA256": digest(input_receipt),
                "sourceEPUBFileName": epub.name,
                "sourceEPUBSHA256": digest(epub),
                "artifactRelativePath": artifact_relative_path,
            }
            attempt = research / "echo-render-current-attempt.json"
            attempt.write_text(
                json.dumps(attempt_payload, sort_keys=True, separators=(",", ":"))
                + "\n",
                encoding="utf-8",
            )
            success_payload = {
                "schemaVersion": 2,
                **{key: attempt_payload[key] for key in (
                    "attemptID",
                    "runID",
                    "inputReceiptFileName",
                    "inputReceiptSHA256",
                    "sourceEPUBFileName",
                    "sourceEPUBSHA256",
                    "artifactRelativePath",
                )},
                "attemptReceiptSHA256": digest(attempt),
                "resumeStateFileName": state_receipt.name,
                "resumeStateSHA256": digest(state_receipt),
                "audiobookFileName": audiobook.name,
                "audiobookSHA256": digest(audiobook),
                "sidecarFileName": sidecar.name,
                "sidecarSHA256": digest(sidecar),
                "auditFileName": audit.name,
                "auditSHA256": digest(audit),
            }
            success = research / f"echo-render-success-{run_id}-{attempt_id}.json"
            success.write_text(
                json.dumps(success_payload, sort_keys=True, separators=(",", ":"))
                + "\n",
                encoding="utf-8",
            )
            selector_payload = {
                "schemaVersion": 1,
                **{key: attempt_payload[key] for key in (
                    "attemptID",
                    "runID",
                    "inputReceiptFileName",
                    "inputReceiptSHA256",
                    "sourceEPUBFileName",
                    "sourceEPUBSHA256",
                    "artifactRelativePath",
                )},
                "attemptReceiptSHA256": digest(attempt),
                "successReceiptFileName": success.name,
                "successReceiptSHA256": digest(success),
            }
            selector = research / "echo-render-current-accepted.json"
            selector.write_text(
                json.dumps(selector_payload, sort_keys=True, separators=(",", ":"))
                + "\n",
                encoding="utf-8",
            )

            command = [
                "/usr/local/bin/python3",
                str(STATE_HELPER),
                "verify-delivery",
                "--attempt",
                str(attempt),
                "--selector",
                str(selector),
                "--receipt",
                str(success),
                "--input-receipt",
                str(input_receipt),
                "--state-receipt",
                str(state_receipt),
                "--epub",
                str(epub),
                "--audiobook",
                str(audiobook),
                "--sidecar",
                str(sidecar),
                "--audit",
                str(audit),
                "--reel",
                str(reel),
            ]
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)

            governed_receipts = {
                "--attempt": ("current-attempt receipt", attempt),
                "--selector": ("current-accepted selector", selector),
                "--receipt": ("render-success receipt", success),
                "--input-receipt": ("render-input receipt", input_receipt),
            }
            diagnostics = (
                ("missing", "is missing"),
                ("symlink", "must not be a symlink"),
                ("directory", "must be a regular file"),
            )
            for option, (label, receipt) in governed_receipts.items():
                for kind, diagnostic in diagnostics:
                    with self.subTest(receipt=option, input_kind=kind):
                        invalid = root / f"legacy-{option.removeprefix('--')}-{kind}"
                        if kind == "symlink":
                            invalid.symlink_to(receipt)
                        elif kind == "directory":
                            invalid.mkdir()
                        rejected_command = list(command)
                        rejected_command[rejected_command.index(option) + 1] = str(invalid)
                        rejected = subprocess.run(
                            rejected_command,
                            capture_output=True,
                            text=True,
                        )
                        self.assertEqual(65, rejected.returncode, rejected.stderr)
                        self.assertEqual("", rejected.stdout)
                        self.assertEqual(
                            "echo_pronunciation_state: "
                            f"{label} {diagnostic}: {invalid}\n",
                            rejected.stderr,
                        )


class PronunciationAuditValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.tmp = Path(self.temporary.name).resolve()
        self.audit = self.tmp / "fixture.pronunciation-audit.json"
        self.audiobook = self.tmp / "fixture.m4b"
        self.audiobook.write_bytes(b"fixture audiobook bytes")
        self.fake_bin = self.tmp / "bin"
        self.fake_bin.mkdir()
        ffprobe = self.fake_bin / "ffprobe"
        ffprobe.write_text(
            '#!/usr/bin/env bash\nprintf \'%s\\n\' \'{"format":{"duration":"5.0"}}\'\n',
            encoding="utf-8",
        )
        ffprobe.chmod(ffprobe.stat().st_mode | stat.S_IXUSR)
        self.payload = {
            "schemaVersion": 2,
            "renderVersion": 12,
            "voice": "am_michael",
            "coverage": "complete",
            "watchCounts": {word: 0 for word in AUDIT_VALIDATOR_MODULE.WATCH_WORDS},
            "decisions": [],
            "diagnostics": [],
            "legacyChapterIndexes": [],
            "audiobookFileName": "fixture.m4b",
            "audiobookSHA256": hashlib.sha256(self.audiobook.read_bytes()).hexdigest(),
        }

    @staticmethod
    def valid_decision() -> dict[str, object]:
        return {
            "blockID": "fixture-s0-b1",
            "wordStart": 1,
            "wordEnd": 1,
            "normalizedWord": "filesystem",
            "sourceWord": "filesystem",
            "sourceContext": "The filesystem stores the result.",
            "selectedIPA": "fˈIl sˌɪstəm",
            "kokoroTokenIDs": [48, 156, 25, 54],
            "source": "builtInOverride",
            "ruleID": "override.built-in.filesystem",
            "rationale": "Built-in override matched filesystem.",
            "chapterIndex": 0,
            "chapterRelativeAudioRange": {"start": 1.25, "end": 1.75},
            "bookRelativeAudioRange": {"start": 1.25, "end": 1.75},
            "timingPrecision": "exactSynthesisWord",
        }

    def run_validator(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        self.audit.write_text(json.dumps(self.payload), encoding="utf-8")
        return self.run_validator_bytes(self.audit.read_bytes(), *arguments)

    def run_validator_bytes(
        self,
        payload: bytes,
        *arguments: str,
        extra_environment: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        self.audit.write_bytes(payload)
        environment = os.environ.copy()
        environment["PATH"] = f"{self.fake_bin}:{environment['PATH']}"
        if extra_environment is not None:
            environment.update(extra_environment)
        return subprocess.run(
            [
                "/usr/local/bin/python3",
                str(AUDIT_VALIDATOR),
                str(self.audit),
                *arguments,
            ],
            env=environment,
            capture_output=True,
            text=True,
        )

    def schema_7_payload(self) -> dict[str, object]:
        return {
            "schemaVersion": 7,
            "renderVersion": 12,
            "voice": "mixed",
            "chapterVoices": {},
            "voicePlanSHA256": "b" * 64,
            "blockVoices": {"s2-b3": "bf_emma", "s2-b4": "am_michael"},
            "coverage": "complete",
            "legacyChapterIndexes": [],
            "audiobookFileName": self.audiobook.name,
            "audiobookSHA256": hashlib.sha256(self.audiobook.read_bytes()).hexdigest(),
            "watchCounts": {
                word: 0 for word in AUDIT_VALIDATOR_MODULE.WATCH_WORDS
            },
            "decisions": [],
            "diagnostics": [],
        }

    def schema_7_arguments(self, *, reel: Path | None = None) -> tuple[str, ...]:
        arguments = (
            "--audiobook",
            str(self.audiobook),
            "--voice-plan-sha256",
            "b" * 64,
            "--block-count",
            "2",
        )
        if reel is not None:
            arguments += ("--reel", str(reel))
        return arguments

    def test_accepts_complete_schema_v2_fixture_with_zero_watch_counts(self) -> None:
        result = self.run_validator()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("pronunciation_audit: clean", result.stdout)

    def test_accepts_schema_7_block_voice_audit_with_explicit_plan_and_media(
        self,
    ) -> None:
        self.payload = self.schema_7_payload()

        result = self.run_validator(*self.schema_7_arguments())

        self.assertEqual(0, result.returncode, result.stderr)

    def test_schema_7_accepts_imported_decision_block_id_with_planned_suffix(
        self,
    ) -> None:
        self.payload = self.schema_7_payload()
        decision = self.valid_decision()
        decision["blockID"] = (
            "epub-runner-the-human-exception-ch09-multivoice-acceptance-"
            "the-human-exception-ch09-multivoice-acceptance.epub-s2-b3"
        )
        self.payload["decisions"] = [decision]
        self.payload["watchCounts"]["filesystem"] = 1
        reel = self.tmp / "fixture.pronunciation-reel.m4b"
        reel.write_bytes(b"fixture listening reel")
        self.payload["listeningReelFileName"] = reel.name
        self.payload["listeningReelSHA256"] = hashlib.sha256(reel.read_bytes()).hexdigest()

        result = self.run_validator(*self.schema_7_arguments(reel=reel))

        self.assertEqual(0, result.returncode, result.stderr)

    def test_schema_7_rejects_imported_decision_block_id_with_unplanned_suffix(
        self,
    ) -> None:
        self.payload = self.schema_7_payload()
        decision = self.valid_decision()
        decision["blockID"] = (
            "epub-runner-the-human-exception-ch09-multivoice-acceptance-"
            "the-human-exception-ch09-multivoice-acceptance.epub-s2-b99"
        )
        self.payload["decisions"] = [decision]
        self.payload["watchCounts"]["filesystem"] = 1
        reel = self.tmp / "fixture.pronunciation-reel.m4b"
        reel.write_bytes(b"fixture listening reel")
        self.payload["listeningReelFileName"] = reel.name
        self.payload["listeningReelSHA256"] = hashlib.sha256(reel.read_bytes()).hexdigest()

        result = self.run_validator(*self.schema_7_arguments(reel=reel))

        self.assertNotEqual(0, result.returncode)
        self.assertIn(
            "decisions[0].blockID is absent from blockVoices",
            result.stderr,
        )

    def test_schema_7_rejects_imported_decision_block_id_with_trailing_newline(
        self,
    ) -> None:
        self.payload = self.schema_7_payload()
        decision = self.valid_decision()
        decision["blockID"] = (
            "epub-runner-the-human-exception-ch09-multivoice-acceptance-"
            "the-human-exception-ch09-multivoice-acceptance.epub-s2-b3\n"
        )
        self.payload["decisions"] = [decision]
        self.payload["watchCounts"]["filesystem"] = 1
        reel = self.tmp / "fixture.pronunciation-reel.m4b"
        reel.write_bytes(b"fixture listening reel")
        self.payload["listeningReelFileName"] = reel.name
        self.payload["listeningReelSHA256"] = hashlib.sha256(reel.read_bytes()).hexdigest()

        result = self.run_validator(*self.schema_7_arguments(reel=reel))

        self.assertNotEqual(0, result.returncode)
        self.assertIn(
            "decisions[0].blockID is absent from blockVoices",
            result.stderr,
        )

    def test_schema_7_rejects_unbound_block_provenance(self) -> None:
        cases: list[tuple[str, Callable[[dict[str, object]], None], tuple[str, ...]]] = []

        def wrong_plan_hash(payload: dict[str, object]) -> None:
            payload["voicePlanSHA256"] = "c" * 64

        cases.append(("wrong plan hash", wrong_plan_hash, self.schema_7_arguments()))

        def wrong_block_count(payload: dict[str, object]) -> None:
            payload["blockVoices"] = {"s2-b3": "bf_emma"}

        cases.append(("wrong block count", wrong_block_count, self.schema_7_arguments()))

        def nonempty_chapter_voices(payload: dict[str, object]) -> None:
            payload["chapterVoices"] = {"0": "am_michael"}

        cases.append(
            ("chapter voices", nonempty_chapter_voices, self.schema_7_arguments())
        )

        def unknown_voice(payload: dict[str, object]) -> None:
            payload["blockVoices"] = {"s2-b3": "not_a_voice", "s2-b4": "am_michael"}

        cases.append(("unknown voice", unknown_voice, self.schema_7_arguments()))

        def invalid_block_id(payload: dict[str, object]) -> None:
            payload["blockVoices"] = {"invalid": "bf_emma", "s2-b4": "am_michael"}

        cases.append(("invalid block ID", invalid_block_id, self.schema_7_arguments()))

        def missing_decision_block(payload: dict[str, object]) -> None:
            decision = self.valid_decision()
            decision["blockID"] = "s9-b1"
            for field in (
                "chapterIndex",
                "chapterRelativeAudioRange",
                "bookRelativeAudioRange",
                "timingPrecision",
            ):
                decision.pop(field)
            payload["decisions"] = [decision]
            payload["watchCounts"]["filesystem"] = 1

        cases.append(
            ("missing decision block", missing_decision_block, self.schema_7_arguments())
        )

        for name, mutate, arguments in cases:
            with self.subTest(name=name):
                self.payload = self.schema_7_payload()
                mutate(self.payload)
                result = self.run_validator(*arguments)
                self.assertNotEqual(0, result.returncode)

    def test_schema_7_rejects_duplicate_top_level_json_keys(self) -> None:
        self.payload = self.schema_7_payload()
        encoded = json.dumps(self.payload, separators=(",", ":"))
        self.audit.write_text(
            encoded.replace('"schemaVersion":7', '"schemaVersion":7,"schemaVersion":7', 1),
            encoding="utf-8",
        )
        environment = os.environ.copy()
        environment["PATH"] = f"{self.fake_bin}:{environment['PATH']}"

        result = subprocess.run(
            [
                "/usr/local/bin/python3",
                str(AUDIT_VALIDATOR),
                str(self.audit),
                *self.schema_7_arguments(),
            ],
            env=environment,
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("duplicate JSON key", result.stderr)

    def test_schemas_two_through_six_preserve_last_key_wins_json_parsing(self) -> None:
        """Schema 7 is strict; historical audits keep Python JSON's old semantics."""
        for schema_version in range(2, 7):
            with self.subTest(schema_version=schema_version):
                payload = copy.deepcopy(self.payload)
                payload["schemaVersion"] = schema_version
                if schema_version >= 3:
                    payload["chapterVoices"] = {"0": "am_michael"}
                encoded = json.dumps(payload, separators=(",", ":"))
                duplicate_voice = encoded.replace(
                    '"voice":"am_michael"',
                    '"voice":"not_a_voice","voice":"am_michael"',
                    1,
                ).encode("utf-8")
                result = self.run_validator_bytes(duplicate_voice)
                self.assertEqual(0, result.returncode, result.stderr)

    def test_schema_7_rejects_extra_top_level_key_and_accepts_a_sole_voice(self) -> None:
        self.payload = self.schema_7_payload()
        self.payload["voice"] = "am_michael"
        self.payload["blockVoices"] = {
            "s2-b3": "am_michael",
            "s2-b4": "am_michael",
        }
        sole_voice = self.run_validator(*self.schema_7_arguments())
        self.assertEqual(0, sole_voice.returncode, sole_voice.stderr)

        self.payload["unexpected"] = True
        unexpected = self.run_validator(*self.schema_7_arguments())
        self.assertNotEqual(0, unexpected.returncode)
        self.assertIn("unexpected top-level keys", unexpected.stderr)

    def test_schema_7_requires_exact_plan_and_conditional_reel_options(self) -> None:
        self.payload = self.schema_7_payload()
        for arguments in (
            (),
            ("--audiobook", str(self.audiobook)),
            (
                "--audiobook",
                str(self.audiobook),
                "--voice-plan-sha256",
                "b" * 64,
            ),
            (
                "--audiobook",
                str(self.audiobook),
                "--block-count",
                "2",
            ),
        ):
            with self.subTest(arguments=arguments):
                result = self.run_validator(*arguments)
                self.assertNotEqual(0, result.returncode)

        extra_reel = self.tmp / "unexpected.pronunciation-reel.m4b"
        extra_reel.write_bytes(b"unexpected reel")
        supplied_without_manifest = self.run_validator(
            *self.schema_7_arguments(reel=extra_reel)
        )
        self.assertNotEqual(0, supplied_without_manifest.returncode)

        self.payload["listeningReelFileName"] = extra_reel.name
        self.payload["listeningReelSHA256"] = hashlib.sha256(
            extra_reel.read_bytes()
        ).hexdigest()
        missing_when_manifested = self.run_validator(*self.schema_7_arguments())
        self.assertNotEqual(0, missing_when_manifested.returncode)

        self.payload = {
            **copy.deepcopy(self.payload),
            "schemaVersion": 6,
            "voice": "am_michael",
            "chapterVoices": {"0": "am_michael"},
        }
        self.payload.pop("voicePlanSHA256", None)
        self.payload.pop("blockVoices", None)
        self.payload.pop("listeningReelFileName", None)
        self.payload.pop("listeningReelSHA256", None)
        for arguments in (
            ("--voice-plan-sha256", "b" * 64),
            ("--block-count", "2"),
            ("--voice-plan-sha256", "b" * 64, "--block-count", "2"),
        ):
            with self.subTest(legacy_arguments=arguments):
                forbidden_for_legacy = self.run_validator(*arguments)
                self.assertNotEqual(0, forbidden_for_legacy.returncode)
                self.assertIn("require schema 7", forbidden_for_legacy.stderr)

    def test_schema_7_explicit_media_uses_one_stable_snapshot_and_canonical_ancestry(
        self,
    ) -> None:
        self.payload = self.schema_7_payload()
        decision = self.valid_decision()
        decision["blockID"] = "s2-b3"
        self.payload["decisions"] = [decision]
        self.payload["watchCounts"]["filesystem"] = 1
        reel = self.tmp / "fixture.pronunciation-reel.m4b"
        reel.write_bytes(b"fixture listening reel")
        self.payload["listeningReelFileName"] = reel.name
        self.payload["listeningReelSHA256"] = hashlib.sha256(reel.read_bytes()).hexdigest()
        replacement = self.tmp / "replacement.m4b"
        replacement.write_bytes(b"replacement bytes")
        ffprobe = self.fake_bin / "ffprobe"
        ffprobe.write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            'target=${SWAP_TARGET:?}\n'
            'replacement=${SWAP_REPLACEMENT:?}\n'
            'media=${!#}\n'
            'if [[ -e $replacement ]]; then mv -- "$replacement" "$target"; fi\n'
            'if [[ $(<"$media") == "fixture audiobook bytes" ]]; then\n'
            "  printf '%s\\n' '{\"format\":{\"duration\":\"5.0\"}}'\n"
            "else\n"
            "  printf '%s\\n' '{\"format\":{\"duration\":\"1.0\"}}'\n"
            "fi\n",
            encoding="utf-8",
        )
        ffprobe.chmod(ffprobe.stat().st_mode | stat.S_IXUSR)
        result = self.run_validator_bytes(
            json.dumps(self.payload).encode("utf-8"),
            *self.schema_7_arguments(reel=reel),
            extra_environment={
                "SWAP_TARGET": str(self.audiobook),
                "SWAP_REPLACEMENT": str(replacement),
            },
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(b"replacement bytes", self.audiobook.read_bytes())

        actual = self.tmp / "actual-media"
        actual.mkdir()
        sibling = actual / self.audiobook.name
        sibling.write_bytes(b"fixture audiobook bytes")
        linked_parent = self.tmp / "linked-media"
        linked_parent.symlink_to(actual, target_is_directory=True)
        self.audiobook = linked_parent / self.audiobook.name
        self.payload = self.schema_7_payload()
        symlinked_ancestry = self.run_validator(*self.schema_7_arguments())
        self.assertNotEqual(0, symlinked_ancestry.returncode)

    def test_schema_7_binds_an_explicit_reel_outside_the_artifact_directory(
        self,
    ) -> None:
        self.payload = self.schema_7_payload()
        reel = self.tmp / "listening" / "run" / "attempt" / "fixture.pronunciation-reel.m4b"
        reel.parent.mkdir(parents=True)
        reel.write_bytes(b"external listening reel")
        self.payload["listeningReelFileName"] = reel.name
        self.payload["listeningReelSHA256"] = hashlib.sha256(reel.read_bytes()).hexdigest()
        decision = self.valid_decision()
        decision["blockID"] = "s2-b3"
        self.payload["decisions"] = [decision]
        self.payload["watchCounts"]["filesystem"] = 1

        result = self.run_validator(*self.schema_7_arguments(reel=reel))

        self.assertEqual(0, result.returncode, result.stderr)

        reel.write_bytes(b"tampered external reel")
        tampered = self.run_validator(*self.schema_7_arguments(reel=reel))
        self.assertNotEqual(0, tampered.returncode)
        self.assertIn("listeningReelSHA256 does not match", tampered.stderr)

    def test_schemas_two_through_six_keep_sibling_media_behavior(self) -> None:
        for schema_version in range(2, 7):
            with self.subTest(schema_version=schema_version):
                self.payload = {
                    **copy.deepcopy(self.payload),
                    "schemaVersion": schema_version,
                    "voice": "am_michael",
                }
                if schema_version >= 3:
                    self.payload["chapterVoices"] = {"0": "am_michael"}
                else:
                    self.payload.pop("chapterVoices", None)
                result = self.run_validator()
                self.assertEqual(0, result.returncode, result.stderr)

    def test_rejects_unsupported_manifest_schema(self) -> None:
        self.payload["schemaVersion"] = 1
        result = self.run_validator()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("schemaVersion must be between 2 and 7", result.stderr)

    def test_accepts_schema_v6_with_current_governed_decision_sources(self) -> None:
        supplemental = self.valid_decision()
        supplemental.update(
            {
                "source": "supplementalLexicon",
                "ruleID": "g2p.supplemental.filesystem",
                "rationale": "Supplemental lexicon selected filesystem.",
            }
        )
        derived = self.valid_decision()
        derived.update(
            {
                "normalizedWord": "available",
                "sourceWord": "available",
                "sourceContext": "Every available record remained searchable.",
                "source": "derivedMorphology",
                "ruleID": "g2p.derived.available",
                "rationale": "Derived morphology selected available.",
            }
        )
        for decision in (supplemental, derived):
            decision.pop("chapterRelativeAudioRange")
            decision.pop("bookRelativeAudioRange")
            decision.pop("timingPrecision")
        self.payload.update(
            {
                "schemaVersion": 6,
                "chapterVoices": {"0": "am_michael"},
                "decisions": [supplemental, derived],
            }
        )
        self.payload["watchCounts"]["filesystem"] = 1
        self.payload["watchCounts"]["available"] = 1

        result = self.run_validator()

        self.assertEqual(0, result.returncode, result.stderr)

    def test_watch_vocabulary_matches_current_echo_schema_v6_contract(self) -> None:
        expected = {
            "able",
            "arithmetic",
            "available",
            "campbell",
            "comfortable",
            "content",
            "deepmind",
            "deepmind's",
            "fakkeldy",
            "filesystem",
            "lifecycle",
            "live",
            "lives",
            "pictou",
            "possible",
            "re",
            "read",
            "readme",
            "record",
            "reliable",
            "resume",
            "resumes",
            "résumé",
            "résumés",
            "stable",
            "startable",
            "super",
            "supercomputer",
            "supercomputers",
            "superforecasters",
            "superhuman",
            "superimposed",
            "superintelligence",
            "supernatural",
            "superposition",
            "supervised",
            "supervising",
            "table",
            "timeframe",
            "unsupervised",
            "validator",
            "validators",
            "verified",
            "xcassets",
            "xcode",
        }
        self.assertEqual(expected, set(AUDIT_VALIDATOR_MODULE.WATCH_WORDS))

    def test_accepts_schema_v3_mixed_voice_with_complete_chapter_provenance(
        self,
    ) -> None:
        self.payload.update(
            {
                "schemaVersion": 3,
                "voice": "mixed",
                "chapterVoices": {
                    "0": "af_heart",
                    "2": "bf_emma",
                    "5": "bm_fable",
                },
            }
        )
        result = self.run_validator()
        self.assertEqual(0, result.returncode, result.stderr)

    def test_rejects_schema_v3_incomplete_or_inconsistent_voice_provenance(
        self,
    ) -> None:
        cases = (
            ("missing", None),
            ("unknown", {"0": "not_a_voice"}),
            ("mixed-but-uniform", {"0": "af_heart", "2": "af_heart"}),
        )
        for name, chapter_voices in cases:
            with self.subTest(name=name):
                self.payload["schemaVersion"] = 3
                self.payload["voice"] = "mixed"
                if chapter_voices is None:
                    self.payload.pop("chapterVoices", None)
                else:
                    self.payload["chapterVoices"] = chapter_voices
                result = self.run_validator()
                self.assertNotEqual(0, result.returncode)

    def test_accepts_full_schema_decision_and_matching_watch_count(self) -> None:
        self.payload["decisions"] = [self.valid_decision()]
        self.payload["watchCounts"]["filesystem"] = 1
        reel = self.tmp / "fixture.pronunciation-reel.m4b"
        reel.write_bytes(b"fixture reel")
        self.payload["listeningReelFileName"] = reel.name
        self.payload["listeningReelSHA256"] = hashlib.sha256(
            reel.read_bytes()
        ).hexdigest()
        result = self.run_validator()
        self.assertEqual(0, result.returncode, result.stderr)

    def test_rejects_null_manifest_scalars_and_null_decision(self) -> None:
        cases = {
            "renderVersion=null": ("renderVersion", None),
            "renderVersion=bool": ("renderVersion", True),
            "renderVersion=string": ("renderVersion", "11"),
            "voice=null": ("voice", None),
            "voice=empty": ("voice", ""),
            "voice=number": ("voice", 11),
            "decisions=[null]": ("decisions", [None]),
        }
        for name, (field, value) in cases.items():
            with self.subTest(name=name):
                original = self.payload[field]
                self.payload[field] = value
                result = self.run_validator()
                self.assertNotEqual(0, result.returncode)
                self.payload[field] = original

    def test_rejects_disallowed_voice_or_pre_v12_render(self) -> None:
        for field, value, message in (
            ("voice", "af_heart", "schema 2 voice must be am_michael or am_puck"),
            ("renderVersion", 11, "renderVersion must be at least 12"),
        ):
            with self.subTest(field=field):
                original = self.payload[field]
                self.payload[field] = value
                result = self.run_validator()
                self.assertNotEqual(0, result.returncode)
                self.assertIn(message, result.stderr)
                self.payload[field] = original

    def test_timed_decisions_require_a_reel_and_in_media_ranges(self) -> None:
        self.payload["decisions"] = [self.valid_decision()]
        self.payload["watchCounts"]["filesystem"] = 1
        missing_reel = self.run_validator()
        self.assertNotEqual(0, missing_reel.returncode)
        self.assertIn(
            "timed pronunciation decisions require a listening reel",
            missing_reel.stderr,
        )

        reel = self.tmp / "fixture.pronunciation-reel.m4b"
        reel.write_bytes(b"fixture reel")
        self.payload["listeningReelFileName"] = reel.name
        self.payload["listeningReelSHA256"] = hashlib.sha256(
            reel.read_bytes()
        ).hexdigest()
        self.payload["decisions"][0]["bookRelativeAudioRange"] = {
            "start": 4.5,
            "end": 9999.0,
        }
        outside = self.run_validator()
        self.assertNotEqual(0, outside.returncode)
        self.assertIn("exceeds audiobook duration", outside.stderr)

    def test_rejects_decision_word_missing_from_watch_counts(self) -> None:
        decision = self.valid_decision()
        decision["normalizedWord"] = "not-watched"
        self.payload["decisions"] = [decision]
        result = self.run_validator()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("is absent from watchCounts", result.stderr)

    def test_rejects_schema_invalid_decision_fields_and_ranges(self) -> None:
        valid = self.valid_decision()
        invalid_decisions: dict[str, object] = {}

        missing_block = copy.deepcopy(valid)
        missing_block.pop("blockID")
        invalid_decisions["missing required field"] = missing_block

        reversed_words = copy.deepcopy(valid)
        reversed_words["wordEnd"] = 0
        invalid_decisions["reversed word range"] = reversed_words

        boundary_token = copy.deepcopy(valid)
        boundary_token["kokoroTokenIDs"] = [0]
        invalid_decisions["synthetic boundary token"] = boundary_token

        oversized_token = copy.deepcopy(valid)
        oversized_token["kokoroTokenIDs"] = [2**31]
        invalid_decisions["out-of-range token"] = oversized_token

        invalid_source = copy.deepcopy(valid)
        invalid_source["source"] = "madeUpSource"
        invalid_decisions["unknown source"] = invalid_source

        invalid_source_type = copy.deepcopy(valid)
        invalid_source_type["source"] = []
        invalid_decisions["non-string source"] = invalid_source_type

        reversed_audio = copy.deepcopy(valid)
        reversed_audio["chapterRelativeAudioRange"] = {"start": 2.0, "end": 1.0}
        invalid_decisions["reversed audio range"] = reversed_audio

        invalid_precision = copy.deepcopy(valid)
        invalid_precision["timingPrecision"] = "estimated"
        invalid_decisions["unknown timing precision"] = invalid_precision

        missing_chapter_range = copy.deepcopy(valid)
        missing_chapter_range.pop("chapterRelativeAudioRange")
        invalid_decisions["book timing without chapter timing"] = missing_chapter_range

        negative_chapter = copy.deepcopy(valid)
        negative_chapter["chapterIndex"] = -1
        invalid_decisions["negative chapter index"] = negative_chapter

        for name, decision in invalid_decisions.items():
            with self.subTest(name=name):
                self.payload["decisions"] = [decision]
                self.payload["watchCounts"]["filesystem"] = 1
                result = self.run_validator()
                self.assertNotEqual(0, result.returncode)

    def test_rejects_watch_count_inconsistency_across_full_vocabulary(self) -> None:
        self.payload["watchCounts"]["arithmetic"] = 1
        result = self.run_validator()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("does not match decisions", result.stderr)

    def test_rejects_deletion_of_every_zero_count_watch_word(self) -> None:
        for word in AUDIT_VALIDATOR_MODULE.WATCH_WORDS:
            with self.subTest(word=word):
                watch_counts = self.payload["watchCounts"]
                removed = watch_counts.pop(word)
                result = self.run_validator()
                self.assertNotEqual(0, result.returncode)
                self.assertIn(f"watchCounts is missing {word}", result.stderr)
                watch_counts[word] = removed

    def test_rejects_echo_integer_values_outside_signed_64_bit_bounds(self) -> None:
        cases = []
        huge = 10**100

        def render_version(value: int) -> None:
            self.payload["renderVersion"] = value

        cases.append(("renderVersion", render_version))

        def watch_count(value: int) -> None:
            self.payload["watchCounts"]["arithmetic"] = value

        cases.append(("watchCount", watch_count))

        for name, mutate in cases:
            for value in (huge, -huge):
                with self.subTest(field=name, value=value):
                    original = copy.deepcopy(self.payload)
                    try:
                        mutate(value)
                        result = self.run_validator()
                        self.assertNotEqual(0, result.returncode)
                        self.assertIn("signed 64-bit", result.stderr)
                    finally:
                        self.payload = original

        decision_integer_fields = ("wordStart", "wordEnd", "chapterIndex")
        for field in decision_integer_fields:
            for value in (huge, -huge):
                with self.subTest(field=field, value=value):
                    original = copy.deepcopy(self.payload)
                    try:
                        decision = self.valid_decision()
                        decision[field] = value
                        self.payload["decisions"] = [decision]
                        self.payload["watchCounts"]["filesystem"] = 1
                        result = self.run_validator()
                        self.assertNotEqual(0, result.returncode)
                        self.assertIn("signed 64-bit", result.stderr)
                    finally:
                        self.payload = original

    def test_watch_vocabulary_matches_real_echo_acceptance_artifact(self) -> None:
        artifact = Path(
            "/Users/dfakkeldy/Developer/echo-overnight/"
            "pronunciation-acceptance-20260713-superseded-f3852939/"
            "pronunciation-regression-acceptance-20260713.pronunciation-audit.json"
        )
        if not artifact.is_file():
            self.skipTest("real Echo pronunciation acceptance artifact is unavailable")
        payload = json.loads(artifact.read_text(encoding="utf-8"))
        self.assertEqual(
            set(payload["watchCounts"]),
            set(AUDIT_VALIDATOR_MODULE.WATCH_WORDS),
        )

    def test_real_media_bound_echo_acceptance_artifact_validates(self) -> None:
        artifact = Path(
            "/Users/dfakkeldy/Developer/echo-overnight/"
            "pronunciation-acceptance-20260713-superseded-f3852939/"
            "pronunciation-regression-acceptance-20260713.pronunciation-audit.json"
        )
        if not artifact.is_file():
            self.skipTest("real Echo pronunciation acceptance artifact is unavailable")
        payload = json.loads(artifact.read_text(encoding="utf-8"))
        if payload.get("schemaVersion") != 2 or "audiobookSHA256" not in payload:
            self.skipTest("real Echo artifact predates bound media hashes")
        result = subprocess.run(
            ["/usr/local/bin/python3", str(AUDIT_VALIDATOR), str(artifact)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)

    def test_reel_filename_and_file_presence_must_agree(self) -> None:
        reel_name = "fixture.pronunciation-reel.m4b"
        self.payload["listeningReelFileName"] = reel_name
        reel_bytes = b"fixture reel"
        self.payload["listeningReelSHA256"] = hashlib.sha256(reel_bytes).hexdigest()
        missing = self.run_validator()
        self.assertNotEqual(0, missing.returncode)

        (self.tmp / reel_name).write_bytes(reel_bytes)
        no_sample = self.run_validator()
        self.assertNotEqual(0, no_sample.returncode)
        self.assertIn("eligible timed pronunciation decision", no_sample.stderr)

        untimed = self.valid_decision()
        for field in (
            "chapterIndex",
            "chapterRelativeAudioRange",
            "bookRelativeAudioRange",
            "timingPrecision",
        ):
            untimed.pop(field, None)
        self.payload["decisions"] = [untimed]
        self.payload["watchCounts"]["filesystem"] = 1
        no_timed_sample = self.run_validator()
        self.assertNotEqual(0, no_timed_sample.returncode)
        self.assertIn("eligible timed pronunciation decision", no_timed_sample.stderr)

        self.payload["decisions"] = [self.valid_decision()]
        present = self.run_validator()
        self.assertEqual(0, present.returncode, present.stderr)

        self.payload.pop("listeningReelFileName")
        self.payload.pop("listeningReelSHA256")
        unlisted = self.run_validator()
        self.assertNotEqual(0, unlisted.returncode)
        self.assertIn(
            "timed pronunciation decisions require a listening reel", unlisted.stderr
        )

    def test_audiobook_hash_binds_exact_sibling_bytes(self) -> None:
        accepted = self.run_validator()
        self.assertEqual(0, accepted.returncode, accepted.stderr)

        original = self.audiobook.read_bytes()
        self.audiobook.write_bytes(b"X" * len(original))
        mutated = self.run_validator()
        self.assertNotEqual(0, mutated.returncode)
        self.assertIn("audiobookSHA256 does not match", mutated.stderr)

        self.audiobook.write_bytes(original)
        self.payload["audiobookSHA256"] = self.payload["audiobookSHA256"].upper()
        uppercase = self.run_validator()
        self.assertNotEqual(0, uppercase.returncode)
        self.assertIn("64 lowercase hexadecimal", uppercase.stderr)

    def test_reel_hash_is_paired_and_binds_exact_sibling_bytes(self) -> None:
        reel = self.tmp / "fixture.pronunciation-reel.m4b"
        reel_bytes = b"paired reel bytes"
        reel.write_bytes(reel_bytes)
        self.payload["decisions"] = [self.valid_decision()]
        self.payload["watchCounts"]["filesystem"] = 1
        self.payload["listeningReelFileName"] = reel.name

        missing_hash = self.run_validator()
        self.assertNotEqual(0, missing_hash.returncode)
        self.assertIn("must appear together", missing_hash.stderr)

        self.payload["listeningReelSHA256"] = hashlib.sha256(reel_bytes).hexdigest()
        accepted = self.run_validator()
        self.assertEqual(0, accepted.returncode, accepted.stderr)

        reel.write_bytes(b"Z" * len(reel_bytes))
        mutated = self.run_validator()
        self.assertNotEqual(0, mutated.returncode)
        self.assertIn("listeningReelSHA256 does not match", mutated.stderr)

        self.payload["listeningReelFileName"] = None
        hash_without_name = self.run_validator()
        self.assertNotEqual(0, hash_without_name.returncode)
        self.assertIn("must appear together", hash_without_name.stderr)


if __name__ == "__main__":
    unittest.main()
