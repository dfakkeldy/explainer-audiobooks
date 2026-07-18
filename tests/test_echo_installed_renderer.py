from __future__ import annotations

import dataclasses
import hashlib
import importlib.util
import json
import os
import platform
import pwd
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).parents[1]
MODULE_PATH = (
    ROOT
    / "skills"
    / "custom-learning-audiobook"
    / "scripts"
    / "echo_installed_renderer.py"
)
LEASE_MODULE_PATH = (
    ROOT
    / "skills"
    / "custom-learning-audiobook"
    / "scripts"
    / "echo_pronunciation_lease.py"
)
VECTOR_ROOT = (
    ROOT
    / "skills"
    / "custom-learning-audiobook"
    / "references"
    / "echo-renderer-v1"
)

ACCEPTED_INSTALLER_SHA = "2f23aceedb1b9f25b7ea4410756eea32a59af8cd"
ACCEPTED_SOURCE_SHA = "81a635df84f75f2e391706e071878b379e6fe0a0"
ACCEPTED_MANIFEST_SHA = (
    "41bbb3c795b32c0e0273bec8847169bbd2bb9158d7b447255e9b90f587d4bdfd"
)
VECTOR_HASHES = {
    "canonical-manifest-v1.json": (
        "30f857f3ac890b21775f2e7773ff70faae1e1e85e0cf05af49c4ee4d7bb92c15"
    ),
    "lease-identities-v1.json": (
        "bcde098b8b1dc902236d5f0ee383ce9a2d70f6462eb79e8a6be70059b8a806ac"
    ),
    "resource-tree-v1.json": (
        "c025db26fec03bbf897849898c74d134c18eef7a64dfdf097827170fee5a5132"
    ),
}
REQUIRED_CAPABILITIES = (
    "--cover",
    "--sidecar",
    "--voice",
    "--db",
    "--work-dir",
    "--jobs",
    "--threads",
    "--resume",
    "--max-chapters",
    "--no-pronunciation-review",
    "verify-sidecar",
)


def load_module(name: str, path: Path):
    if not path.is_file():
        return None
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


RENDERER = load_module("custom_learning_echo_installed_renderer", MODULE_PATH)
LEASE = load_module("custom_learning_echo_pronunciation_lease", LEASE_MODULE_PATH)


def canonical_json(payload: dict[str, object]) -> bytes:
    return (
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        .encode("utf-8")
        + b"\n"
    )


def load_vector(name: str) -> dict[str, object]:
    payload = json.loads((VECTOR_ROOT / name).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"{name} must contain an object")
    return payload


def expected_resource_identity(files: dict[str, bytes]) -> tuple[str, int]:
    digest = hashlib.sha256()
    for relative_path, content in sorted(files.items()):
        path_bytes = relative_path.encode("utf-8")
        digest.update(len(path_bytes).to_bytes(8, "big", signed=False))
        digest.update(path_bytes)
        digest.update(hashlib.sha256(content).digest())
    return digest.hexdigest(), len(files)


class ModuleAvailabilityTests(unittest.TestCase):
    def test_installed_renderer_module_exists(self):
        self.assertIsNotNone(
            RENDERER,
            f"installed-renderer consumer is absent: {MODULE_PATH}",
        )


class FrozenVectorTests(unittest.TestCase):
    def test_vectors_have_the_independently_reviewed_byte_hashes(self):
        self.assertEqual(set(VECTOR_HASHES), {path.name for path in VECTOR_ROOT.glob("*-v1.json")})
        for name, expected_sha in VECTOR_HASHES.items():
            with self.subTest(name=name):
                self.assertEqual(
                    expected_sha,
                    hashlib.sha256((VECTOR_ROOT / name).read_bytes()).hexdigest(),
                )

    def test_provenance_records_each_exact_echo_source(self):
        provenance = load_vector("vector-provenance.json")
        self.assertEqual(1, provenance["schemaVersion"])
        vectors = provenance["vectors"]
        self.assertIsInstance(vectors, list)
        self.assertEqual(set(VECTOR_HASHES), {entry["fileName"] for entry in vectors})
        for entry in vectors:
            name = entry["fileName"]
            with self.subTest(name=name):
                self.assertEqual(
                    "https://github.com/dfakkeldy/Echo.git",
                    entry["sourceRepository"],
                )
                self.assertEqual(ACCEPTED_INSTALLER_SHA, entry["installerSourceSHA"])
                self.assertEqual(
                    f"Scripts/echo_renderer/test_vectors/{name}",
                    entry["echoRelativePath"],
                )
                self.assertEqual(VECTOR_HASHES[name], entry["sha256"])

    @unittest.skipIf(LEASE is None, "lease helper is absent")
    def test_lease_vector_matches_the_shared_cross_repository_protocol(self):
        vector = load_vector("lease-identities-v1.json")
        self.assertEqual(
            {
                "schemaVersion": 1,
                "canonicalResource": "resolved-absolute-path-utf8",
                "digest": "sha256",
                "suffix": ".lock",
            },
            {key: vector[key] for key in vector if key != "cases"},
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            lock_root = Path(temporary_directory).resolve()
            for case in vector["cases"]:
                with self.subTest(resource=case["resource"]):
                    self.assertEqual(
                        case["lockFileName"],
                        LEASE.lock_path(lock_root, case["resource"]).name,
                    )


@unittest.skipIf(RENDERER is None, "installed-renderer consumer is absent")
class IdentityTests(unittest.TestCase):
    def test_identifies_regular_file_bytes(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory).resolve() / "echo-cli"
            path.write_bytes(b"renderer bytes\n")
            self.assertEqual(
                RENDERER.FileIdentity(
                    sha256=hashlib.sha256(b"renderer bytes\n").hexdigest(),
                    byte_count=15,
                ),
                RENDERER.identify_regular_file(path),
            )

    def test_regular_file_rejects_links_directories_and_special_files(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve()
            regular = root / "regular"
            regular.write_bytes(b"bytes")
            link = root / "link"
            link.symlink_to(regular)
            fifo = root / "fifo"
            os.mkfifo(fifo)
            for path in (root, link, fifo):
                with self.subTest(path=path.name):
                    with self.assertRaises(ValueError):
                        RENDERER.identify_regular_file(path)

    def test_resource_tree_matches_every_frozen_case(self):
        vector = load_vector("resource-tree-v1.json")
        self.assertEqual(1, vector["schemaVersion"])
        self.assertEqual(
            {
                "fileDigest": "sha256-raw-32-bytes",
                "pathEncoding": "utf-8",
                "pathLength": "uint64-big-endian",
                "sort": "normalized-posix-relative-path",
            },
            vector["framing"],
        )
        for case in vector["cases"]:
            with self.subTest(case=case["name"]):
                with tempfile.TemporaryDirectory() as temporary_directory:
                    root = Path(temporary_directory).resolve()
                    for fixture in case["files"]:
                        path = root.joinpath(*fixture["path"].split("/"))
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_bytes(bytes.fromhex(fixture["contentHex"]))
                    self.assertEqual(
                        RENDERER.ResourceTreeIdentity(
                            sha256=case["expected"]["sha256"],
                            regular_file_count=case["expected"]["regularFileCount"],
                        ),
                        RENDERER.identify_resource_tree(root),
                    )

    def test_resource_tree_rejects_linked_and_special_entries(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            parent = Path(temporary_directory).resolve()
            root = parent / "resources"
            root.mkdir()
            regular = root / "voice.bin"
            regular.write_bytes(b"voice")
            root_link = parent / "resources-link"
            root_link.symlink_to(root, target_is_directory=True)
            with self.assertRaises(ValueError):
                RENDERER.identify_resource_tree(root_link)

            entry_link = root / "voice-link.bin"
            entry_link.symlink_to(regular)
            with self.assertRaises(ValueError):
                RENDERER.identify_resource_tree(root)
            entry_link.unlink()

            os.mkfifo(root / "voice.fifo")
            with self.assertRaises(ValueError):
                RENDERER.identify_resource_tree(root)


@unittest.skipIf(RENDERER is None, "installed-renderer consumer is absent")
class StrictJSONTests(unittest.TestCase):
    def test_rejects_duplicate_keys_at_any_depth(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory).resolve() / "payload.json"
            for data in (
                b'{"value":1,"value":2}\n',
                b'{"nested":{"value":1,"value":2}}\n',
            ):
                with self.subTest(data=data):
                    path.write_bytes(data)
                    with self.assertRaisesRegex(ValueError, "test payload"):
                        RENDERER.strict_json_object(path, "test payload")

    def test_rejects_invalid_utf8_and_non_objects(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory).resolve() / "payload.json"
            for data in (b"\xff", b"[]\n", b"null\n"):
                with self.subTest(data=data):
                    path.write_bytes(data)
                    with self.assertRaisesRegex(ValueError, "test payload"):
                        RENDERER.strict_json_object(path, "test payload")


@unittest.skipIf(RENDERER is None, "installed-renderer consumer is absent")
class ManifestAndAttestationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.renderer_root = self.root / "renderers"
        self.package_count = 0
        self.executable_bytes = b"#!/bin/sh\nexit 0\n"
        self.resource_files = {
            "voices/en/voice.bin": b"voice bytes",
            "caf\N{LATIN SMALL LETTER E WITH ACUTE}/\N{SNOW CAPPED MOUNTAIN}.txt": b"resource\n",
        }

    def payload(self) -> dict[str, object]:
        resources_sha, resources_count = expected_resource_identity(self.resource_files)
        return {
            "schemaVersion": 1,
            "echoSourceSHA": ACCEPTED_SOURCE_SHA,
            "installerSourceSHA": ACCEPTED_INSTALLER_SHA,
            "executablePath": "echo-cli",
            "executable": {
                "sha256": hashlib.sha256(self.executable_bytes).hexdigest(),
                "byteCount": len(self.executable_bytes),
            },
            "resourcesPath": "EchoNarrationResources",
            "resources": {
                "sha256": resources_sha,
                "regularFileCount": resources_count,
            },
            "renderVersion": 15,
            "buildConfiguration": "Release",
            "architectures": [platform.machine() or "arm64"],
            "minimumMacOSVersion": "10.15",
            "modelPolicy": {
                "revision": "kokoro-v1.0",
                "expectedByteCount": 325566778,
                "deliveryMode": "sharedEchoCache",
                "modelBytesAttested": False,
            },
            "capabilities": list(REQUIRED_CAPABILITIES),
        }

    def create_package(
        self,
        payload: dict[str, object] | None = None,
        *,
        manifest_data: bytes | None = None,
        source_directory_name: str = ACCEPTED_SOURCE_SHA,
        build_directory_name: str | None = None,
    ) -> tuple[Path, str]:
        selected_payload = payload or self.payload()
        data = manifest_data or canonical_json(selected_payload)
        manifest_sha = hashlib.sha256(data).hexdigest()
        build_name = build_directory_name or manifest_sha
        renderer_root = (
            self.renderer_root
            if self.package_count == 0
            else self.root / f"renderers-{self.package_count}"
        )
        self.package_count += 1
        build_root = renderer_root / source_directory_name / build_name
        resources = build_root / "EchoNarrationResources"
        resources.mkdir(parents=True)
        executable = build_root / "echo-cli"
        executable.write_bytes(self.executable_bytes)
        executable.chmod(0o755)
        for relative_path, content in self.resource_files.items():
            path = resources.joinpath(*relative_path.split("/"))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        (build_root / "renderer-manifest.json").write_bytes(data)
        return build_root, manifest_sha

    def parse_package(
        self, payload: dict[str, object] | None = None
    ):
        build_root, manifest_sha = self.create_package(payload)
        return RENDERER.parse_manifest(
            build_root / "renderer-manifest.json",
            ACCEPTED_SOURCE_SHA,
            manifest_sha,
        )

    def test_parses_every_closed_schema_v1_field_into_renderer_state(self):
        state = self.parse_package()
        self.assertEqual(self.renderer_root, state.renderer_root)
        self.assertEqual(ACCEPTED_SOURCE_SHA, state.source_sha)
        self.assertEqual(ACCEPTED_INSTALLER_SHA, state.installer_source_sha)
        self.assertEqual(state.manifest_sha, state.build_root.name)
        self.assertEqual(state.build_root / "renderer-manifest.json", state.manifest_path)
        self.assertEqual(state.build_root / "echo-cli", state.executable)
        self.assertEqual(state.build_root / "EchoNarrationResources", state.resources)
        self.assertEqual(hashlib.sha256(self.executable_bytes).hexdigest(), state.executable_sha256)
        self.assertEqual(expected_resource_identity(self.resource_files)[0], state.resources_sha256)
        self.assertEqual(15, state.render_version)
        self.assertEqual((platform.machine() or "arm64",), state.architectures)
        self.assertEqual(tuple(REQUIRED_CAPABILITIES), state.capabilities)
        self.assertEqual("10.15", state.minimum_macos_version)
        self.assertEqual("kokoro-v1.0", state.model_revision)
        self.assertEqual(325566778, state.model_expected_byte_count)
        self.assertEqual("sharedEchoCache", state.model_delivery_mode)
        self.assertIs(False, state.model_bytes_attested)

    def test_canonical_manifest_vector_has_the_reviewed_bytes_and_sha(self):
        vector = load_vector("canonical-manifest-v1.json")
        expected = vector["canonicalUTF8"].encode("utf-8")
        self.assertEqual(expected, canonical_json(vector["payload"]))
        self.assertEqual(vector["sha256"], hashlib.sha256(expected).hexdigest())

    def test_rejects_unknown_missing_and_duplicate_manifest_fields(self):
        for container in (None, "executable", "resources", "modelPolicy"):
            with self.subTest(container=container):
                payload = self.payload()
                target = payload if container is None else payload[container]
                target["unknown"] = True
                build_root, manifest_sha = self.create_package(payload)
                with self.assertRaises(ValueError):
                    RENDERER.parse_manifest(
                        build_root / "renderer-manifest.json",
                        ACCEPTED_SOURCE_SHA,
                        manifest_sha,
                    )

        payload = self.payload()
        del payload["capabilities"]
        build_root, manifest_sha = self.create_package(payload)
        with self.assertRaises(ValueError):
            RENDERER.parse_manifest(
                build_root / "renderer-manifest.json",
                ACCEPTED_SOURCE_SHA,
                manifest_sha,
            )

        data = canonical_json(self.payload())
        duplicate = data[:-2] + b',"schemaVersion":1}\n'
        build_root, manifest_sha = self.create_package(manifest_data=duplicate)
        with self.assertRaises(ValueError):
            RENDERER.parse_manifest(
                build_root / "renderer-manifest.json",
                ACCEPTED_SOURCE_SHA,
                manifest_sha,
            )

    def test_rejects_noncanonical_manifest_encoding(self):
        data = (json.dumps(self.payload(), indent=2, ensure_ascii=False) + "\n").encode()
        build_root, manifest_sha = self.create_package(manifest_data=data)
        with self.assertRaisesRegex(ValueError, "canonical"):
            RENDERER.parse_manifest(
                build_root / "renderer-manifest.json",
                ACCEPTED_SOURCE_SHA,
                manifest_sha,
            )

    def test_rejects_unsafe_or_inexact_layout_paths(self):
        unsafe_paths = (
            "/absolute/echo-cli",
            ".",
            "..",
            "./echo-cli",
            "bin/../echo-cli",
            "bin//echo-cli",
            "bin\\echo-cli",
            "echo-cli/",
        )
        for field in ("executablePath", "resourcesPath"):
            for unsafe_path in unsafe_paths:
                with self.subTest(field=field, path=unsafe_path):
                    payload = self.payload()
                    payload[field] = unsafe_path
                    build_root, manifest_sha = self.create_package(payload)
                    with self.assertRaises(ValueError):
                        RENDERER.parse_manifest(
                            build_root / "renderer-manifest.json",
                            ACCEPTED_SOURCE_SHA,
                            manifest_sha,
                        )

        for field, wrong in (
            ("executablePath", "bin/echo-cli"),
            ("resourcesPath", "resources"),
        ):
            with self.subTest(field=field):
                payload = self.payload()
                payload[field] = wrong
                build_root, manifest_sha = self.create_package(payload)
                with self.assertRaisesRegex(ValueError, "layout"):
                    RENDERER.parse_manifest(
                        build_root / "renderer-manifest.json",
                        ACCEPTED_SOURCE_SHA,
                        manifest_sha,
                    )

    def test_rejects_wrong_source_manifest_names_and_manifest_hash(self):
        build_root, manifest_sha = self.create_package(source_directory_name="a" * 40)
        with self.assertRaisesRegex(ValueError, "source directory"):
            RENDERER.parse_manifest(
                build_root / "renderer-manifest.json",
                ACCEPTED_SOURCE_SHA,
                manifest_sha,
            )

        build_root, manifest_sha = self.create_package(build_directory_name="b" * 64)
        with self.assertRaisesRegex(ValueError, "build directory"):
            RENDERER.parse_manifest(
                build_root / "renderer-manifest.json",
                ACCEPTED_SOURCE_SHA,
                manifest_sha,
            )

        build_root, manifest_sha = self.create_package()
        (build_root / "renderer-manifest.json").write_bytes(
            (build_root / "renderer-manifest.json").read_bytes() + b" "
        )
        with self.assertRaisesRegex(ValueError, "manifest bytes"):
            RENDERER.parse_manifest(
                build_root / "renderer-manifest.json",
                ACCEPTED_SOURCE_SHA,
                manifest_sha,
            )

    def test_rejects_wrong_source_and_installer_identities(self):
        payload = self.payload()
        payload["echoSourceSHA"] = "a" * 40
        build_root, manifest_sha = self.create_package(payload)
        with self.assertRaisesRegex(ValueError, "source SHA"):
            RENDERER.parse_manifest(
                build_root / "renderer-manifest.json",
                ACCEPTED_SOURCE_SHA,
                manifest_sha,
            )

        payload = self.payload()
        payload["installerSourceSHA"] = "b" * 40
        build_root, manifest_sha = self.create_package(payload)
        with self.assertRaisesRegex(ValueError, "installer"):
            RENDERER.parse_manifest(
                build_root / "renderer-manifest.json",
                ACCEPTED_SOURCE_SHA,
                manifest_sha,
            )

    def test_rejects_executable_and_resource_identity_changes(self):
        build_root, manifest_sha = self.create_package()
        (build_root / "echo-cli").write_bytes(b"changed executable")
        with self.assertRaisesRegex(ValueError, "executable identity"):
            RENDERER.parse_manifest(
                build_root / "renderer-manifest.json",
                ACCEPTED_SOURCE_SHA,
                manifest_sha,
            )

        build_root, manifest_sha = self.create_package()
        (build_root / "EchoNarrationResources" / "extra.bin").write_bytes(b"extra")
        with self.assertRaisesRegex(ValueError, "resource identity"):
            RENDERER.parse_manifest(
                build_root / "renderer-manifest.json",
                ACCEPTED_SOURCE_SHA,
                manifest_sha,
            )

    def test_rejects_links_special_files_and_unexpected_package_entries(self):
        build_root, manifest_sha = self.create_package()
        aliased_parent = self.root / "aliased-parent"
        aliased_parent.symlink_to(build_root.parents[2], target_is_directory=True)
        aliased_manifest = (
            aliased_parent
            / build_root.relative_to(build_root.parents[2])
            / "renderer-manifest.json"
        )
        with self.assertRaisesRegex(ValueError, "symlink components"):
            RENDERER.parse_manifest(
                aliased_manifest,
                ACCEPTED_SOURCE_SHA,
                manifest_sha,
            )

        build_root, manifest_sha = self.create_package()
        executable = build_root / "echo-cli"
        executable.unlink()
        executable.symlink_to(self.root / "outside")
        with self.assertRaises(ValueError):
            RENDERER.parse_manifest(
                build_root / "renderer-manifest.json",
                ACCEPTED_SOURCE_SHA,
                manifest_sha,
            )

        build_root, manifest_sha = self.create_package()
        resource = build_root / "EchoNarrationResources" / "linked"
        resource.symlink_to(self.root / "outside")
        with self.assertRaises(ValueError):
            RENDERER.parse_manifest(
                build_root / "renderer-manifest.json",
                ACCEPTED_SOURCE_SHA,
                manifest_sha,
            )

        build_root, manifest_sha = self.create_package()
        os.mkfifo(build_root / "EchoNarrationResources" / "special")
        with self.assertRaises(ValueError):
            RENDERER.parse_manifest(
                build_root / "renderer-manifest.json",
                ACCEPTED_SOURCE_SHA,
                manifest_sha,
            )

        build_root, manifest_sha = self.create_package()
        (build_root / "unexpected").write_text("unexpected", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "top-level"):
            RENDERER.parse_manifest(
                build_root / "renderer-manifest.json",
                ACCEPTED_SOURCE_SHA,
                manifest_sha,
            )

    def test_rejects_nonrelease_empty_or_malformed_host_contract_fields(self):
        invalid_cases = (
            ("buildConfiguration", "Debug"),
            ("architectures", []),
            ("architectures", ["arm64", "arm64"]),
            ("architectures", ["arm 64"]),
            ("capabilities", []),
            ("capabilities", ["--cover", "--cover"]),
            ("minimumMacOSVersion", "macOS 15"),
        )
        for field, value in invalid_cases:
            with self.subTest(field=field, value=value):
                payload = self.payload()
                payload[field] = value
                build_root, manifest_sha = self.create_package(payload)
                with self.assertRaises(ValueError):
                    RENDERER.parse_manifest(
                        build_root / "renderer-manifest.json",
                        ACCEPTED_SOURCE_SHA,
                        manifest_sha,
                    )

        payload = self.payload()
        payload["architectures"] = [
            "x86_64" if (platform.machine() or "arm64") != "x86_64" else "arm64"
        ]
        build_root, manifest_sha = self.create_package(payload)
        with self.assertRaisesRegex(ValueError, "host architecture"):
            RENDERER.parse_manifest(
                build_root / "renderer-manifest.json",
                ACCEPTED_SOURCE_SHA,
                manifest_sha,
            )

        payload = self.payload()
        payload["minimumMacOSVersion"] = "15.0"
        build_root, manifest_sha = self.create_package(payload)
        with mock.patch.object(RENDERER.platform, "mac_ver", return_value=("14.7", ("", "", ""), "")):
            with self.assertRaisesRegex(ValueError, "newer macOS"):
                RENDERER.parse_manifest(
                    build_root / "renderer-manifest.json",
                    ACCEPTED_SOURCE_SHA,
                    manifest_sha,
                )

    def test_rejects_invalid_scalar_and_model_policy_values(self):
        cases = (
            ("schemaVersion", 2),
            ("renderVersion", 0),
            ("renderVersion", True),
        )
        for field, value in cases:
            with self.subTest(field=field, value=value):
                payload = self.payload()
                payload[field] = value
                build_root, manifest_sha = self.create_package(payload)
                with self.assertRaises(ValueError):
                    RENDERER.parse_manifest(
                        build_root / "renderer-manifest.json",
                        ACCEPTED_SOURCE_SHA,
                        manifest_sha,
                    )

        for field, value in (
            ("revision", ""),
            ("expectedByteCount", -1),
            ("expectedByteCount", True),
            ("deliveryMode", "bundled"),
            ("modelBytesAttested", True),
            ("modelBytesAttested", 0),
        ):
            with self.subTest(field=field, value=value):
                payload = self.payload()
                payload["modelPolicy"][field] = value
                build_root, manifest_sha = self.create_package(payload)
                with self.assertRaises(ValueError):
                    RENDERER.parse_manifest(
                        build_root / "renderer-manifest.json",
                        ACCEPTED_SOURCE_SHA,
                        manifest_sha,
                    )

    def successful_probe(self, arguments, **kwargs):
        if arguments[-1] == "--version":
            stdout = "ONNX rv15 (Release)\n"
        elif arguments[-2:] == ["narrate", "--help"]:
            stdout = "\n".join(REQUIRED_CAPABILITIES[:-1]) + "\n"
        elif arguments[-2:] == ["verify-sidecar", "--help"]:
            stdout = "Usage: echo-cli verify-sidecar --help\n"
        else:
            raise AssertionError(f"unexpected probe: {arguments}")
        return subprocess.CompletedProcess(arguments, 0, stdout=stdout, stderr="")

    def test_attestation_recomputes_bytes_and_runs_safe_live_probes(self):
        state = self.parse_package()
        calls: list[tuple[list[str], dict[str, object]]] = []

        def runner(arguments, **kwargs):
            calls.append((arguments, kwargs))
            return self.successful_probe(arguments, **kwargs)

        with mock.patch.dict(os.environ, {"INJECTED": "unsafe", "PATH": "/unsafe"}, clear=True):
            with mock.patch.object(RENDERER.subprocess, "run", side_effect=runner):
                RENDERER.attest_renderer(state)

        self.assertEqual(3, len(calls))
        self.assertEqual(
            [
                [str(state.executable), "--version"],
                [str(state.executable), "narrate", "--help"],
                [str(state.executable), "verify-sidecar", "--help"],
            ],
            [arguments for arguments, _ in calls],
        )
        canonical_home = str(Path(pwd.getpwuid(os.geteuid()).pw_dir).resolve(strict=True))
        for _, kwargs in calls:
            self.assertTrue(kwargs["check"])
            self.assertTrue(kwargs["capture_output"])
            self.assertTrue(kwargs["text"])
            self.assertNotIn("INJECTED", kwargs["env"])
            self.assertEqual("/usr/bin:/bin:/usr/sbin:/sbin", kwargs["env"]["PATH"])
            self.assertEqual(canonical_home, kwargs["env"]["HOME"])
            self.assertEqual(str(state.resources), kwargs["env"]["ECHO_RESOURCE_DIR"])

    def test_attestation_rejects_changed_bytes_forged_state_and_live_contract(self):
        state = self.parse_package()
        state.executable.write_bytes(b"changed")
        with mock.patch.object(RENDERER.subprocess, "run") as runner:
            with self.assertRaises(ValueError):
                RENDERER.attest_renderer(state)
            runner.assert_not_called()

        state = self.parse_package()
        forged = dataclasses.replace(state, executable_sha256="f" * 64)
        with self.assertRaises(ValueError):
            RENDERER.attest_renderer(forged)

        state = self.parse_package()
        with mock.patch.object(
            RENDERER.subprocess,
            "run",
            return_value=subprocess.CompletedProcess([], 0, stdout="ONNX rv14 (Release)\n", stderr=""),
        ):
            with self.assertRaisesRegex(ValueError, "render version"):
                RENDERER.attest_renderer(state)

        outputs = iter(
            (
                subprocess.CompletedProcess([], 0, stdout="ONNX rv15 (Release)\n", stderr=""),
                subprocess.CompletedProcess([], 0, stdout="--cover\n", stderr=""),
            )
        )
        with mock.patch.object(RENDERER.subprocess, "run", side_effect=outputs):
            with self.assertRaisesRegex(ValueError, "capabilities"):
                RENDERER.attest_renderer(state)


if __name__ == "__main__":
    unittest.main()
