#!/usr/bin/env python3
"""Report whether installed custom-learning skill links expose this candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANONICAL = Path(
    "/Users/dfakkeldy/Developer/explainer-audiobooks/skills/custom-learning-audiobook"
)
DEFAULT_EXTERNAL = (
    Path.home() / ".hermes/skills/openclaw-imports/custom-learning-audiobook"
)
DEFAULT_HERMES_SOURCE_ROOT = Path.home() / ".hermes/hermes-agent"
DEFAULT_HERMES_PYTHON = DEFAULT_HERMES_SOURCE_ROOT / "venv/bin/python"
DEFAULT_LINKS = tuple(
    Path.home() / base / "skills/custom-learning-audiobook"
    for base in (".codex", ".agents", ".claude", ".hermes")
)


@dataclass(frozen=True)
class ManifestEntry:
    kind: str
    mode: int
    sha256: str | None = None


SKILL_MANIFEST = {
    Path("SKILL.md"): ManifestEntry(
        "file", 0o644, "7f8c6ffda7ed0334e042bc98061e874ca9fd01f4af94ccebfd0ae355951116dc"
    ),
    Path("agents"): ManifestEntry("directory", 0o755),
    Path("agents/openai.yaml"): ManifestEntry(
        "file", 0o644, "4f43f8f0c40a41d674e3caf46c624ae5cd33504693f2b71af295e3d14bee01f4"
    ),
    Path("references"): ManifestEntry("directory", 0o755),
    Path("references/echo-renderer-v1"): ManifestEntry("directory", 0o755),
    Path("references/echo-renderer-v1/canonical-manifest-v1.json"): ManifestEntry(
        "file", 0o644, "30f857f3ac890b21775f2e7773ff70faae1e1e85e0cf05af49c4ee4d7bb92c15"
    ),
    Path("references/echo-renderer-v1/lease-identities-v1.json"): ManifestEntry(
        "file", 0o644, "bcde098b8b1dc902236d5f0ee383ce9a2d70f6462eb79e8a6be70059b8a806ac"
    ),
    Path("references/echo-renderer-v1/resource-tree-v1.json"): ManifestEntry(
        "file", 0o644, "c025db26fec03bbf897849898c74d134c18eef7a64dfdf097827170fee5a5132"
    ),
    Path("references/echo-renderer-v1/vector-provenance.json"): ManifestEntry(
        "file", 0o644, "078b73e92e5069ecb369f9ac02481a05014ed5ea988781eb0c840eee7896d484"
    ),
    Path("references/intake-and-research.md"): ManifestEntry(
        "file", 0o644, "27c00cb8ececc8d6c158000ef84edbe40ee09202a9acb660f0785f21911f40f2"
    ),
    Path("references/package-and-qc.md"): ManifestEntry(
        "file", 0o644, "9d43b684cee3586ef2c7f5c43fe107c34bd0eea487283105cdc5862b662d282d"
    ),
    Path("scripts"): ManifestEntry("directory", 0o755),
    Path("scripts/echo_installed_renderer.py"): ManifestEntry(
        "file", 0o755, "7d0a70e1e690932667bf51c5b039cfdcfbd1b46eb7bf3c6b0fa86b2e4e845086"
    ),
    Path("scripts/echo_pronunciation_preflight.sh"): ManifestEntry(
        "file", 0o755, "5de16dc1b2b7b724b33858a17b0ab1158f033c06a5ba44099f038e66e13035be"
    ),
    Path("scripts/echo_learning_pilot_narrate.sh"): ManifestEntry(
        "file", 0o755, "20f259d29ea43f35f292b13d807a58a8bab29a55b05ef85cce742aae3c621388"
    ),
    Path("scripts/echo_pronunciation_narrate.sh"): ManifestEntry(
        "file", 0o755, "9af4f1e32d528ae1eb393c0468c6e52503f771206b7a96d33c1c6b48faf4d2f4"
    ),
    Path("scripts/echo_pronunciation_lease.py"): ManifestEntry(
        "file", 0o755, "f36136112ce1f40f47c8312d9687cbaf77ce9dfafcfdf353aa477ec5e5a6271b"
    ),
    Path("scripts/echo_pronunciation_state.py"): ManifestEntry(
        "file", 0o755, "08f42329fcb7f9fe3e034043c5556f62b72fd2b65327115194237302d8c885b7"
    ),
    Path("scripts/validate_pronunciation_audit.py"): ManifestEntry(
        "file", 0o755, "e349c02b7a396f847e6f1cac88d2508f377b9aa22b4a9080e9d0c9aa30d288c2"
    ),
}
IGNORED_TRANSIENT_NAMES = frozenset({".DS_Store", "__pycache__"})
EXTERNAL_DISCOVERABLE_SKILL = Path("SKILL.md")
EXTERNAL_TOMBSTONE = Path("SKILL.disabled.md")
EXTERNAL_GUARD_FILES = (EXTERNAL_TOMBSTONE, Path("references/package-and-qc.md"))
DISABLED_MARKER = "DISABLED: canonical skill required"
CANONICAL_ROUTE = "/Users/dfakkeldy/.hermes/skills/custom-learning-audiobook"
EXTERNAL_SKILL_TOMBSTONE = f"""---
name: custom-learning-audiobook
description: Disabled duplicate. Load the canonical shared custom-learning-audiobook skill.
---

# Disabled Duplicate

## {DISABLED_MARKER}

Stop. Do not execute any workflow from this directory.
Load `{CANONICAL_ROUTE}` and follow that canonical skill.
"""
EXTERNAL_PACKAGE_STUB = f"""# {DISABLED_MARKER}

Stop. This duplicate package reference is not executable.
Load `{CANONICAL_ROUTE}` and follow that canonical skill.
"""
EXTERNAL_STUBS = {
    EXTERNAL_TOMBSTONE: EXTERNAL_SKILL_TOMBSTONE,
    Path("references/package-and-qc.md"): EXTERNAL_PACKAGE_STUB,
}


def fail(message: str) -> int:
    print(f"installed_skill_parity: error: {message}", file=sys.stderr)
    return 1


def pending(candidate_root: Path, canonical_root: Path) -> int:
    print("installed_skill_parity: pending-integration")
    print(f"candidate={candidate_root}")
    print(f"installed_canonical={canonical_root}")
    return 2


def is_ignored_transient(relative_path: Path) -> bool:
    return any(part in IGNORED_TRANSIENT_NAMES for part in relative_path.parts)


def skill_inventory(root: Path) -> dict[Path, ManifestEntry]:
    if root.is_symlink() or not root.is_dir():
        raise ValueError(f"skill root is not a real directory: {root}")
    inventory: dict[Path, ManifestEntry] = {}
    for path in sorted(root.rglob("*")):
        relative_path = path.relative_to(root)
        if is_ignored_transient(relative_path):
            continue
        mode = path.lstat().st_mode
        if stat.S_ISREG(mode):
            kind = "file"
        elif stat.S_ISDIR(mode):
            kind = "directory"
        elif stat.S_ISLNK(mode):
            kind = "symlink"
        else:
            kind = "other"
        inventory[relative_path] = ManifestEntry(kind, stat.S_IMODE(mode))
    return inventory


def candidate_manifest_error(candidate_root: Path) -> str | None:
    try:
        actual = skill_inventory(candidate_root)
    except (OSError, ValueError) as error:
        return str(error)
    missing = sorted(set(SKILL_MANIFEST) - set(actual))
    unexpected = sorted(set(actual) - set(SKILL_MANIFEST))
    if missing:
        return "candidate manifest is missing: " + ", ".join(map(str, missing))
    if unexpected:
        return "candidate manifest has unexpected entries: " + ", ".join(
            map(str, unexpected)
        )
    for relative_path, expected in SKILL_MANIFEST.items():
        observed = actual[relative_path]
        if observed.kind != expected.kind:
            return (
                f"candidate manifest type differs for {relative_path}: "
                f"{observed.kind} != {expected.kind}"
            )
        if observed.mode != expected.mode:
            return (
                f"candidate manifest mode differs for {relative_path}: "
                f"{observed.mode:o} != {expected.mode:o}"
            )
        if expected.sha256 is not None:
            observed_hash = hashlib.sha256(
                (candidate_root / relative_path).read_bytes()
            ).hexdigest()
            if observed_hash != expected.sha256:
                return (
                    f"candidate manifest hash differs for {relative_path}: "
                    f"{observed_hash} != {expected.sha256}"
                )
    return None


def installed_manifest_matches(candidate_root: Path, canonical_root: Path) -> bool:
    try:
        candidate = skill_inventory(candidate_root)
        canonical = skill_inventory(canonical_root)
    except (OSError, ValueError):
        return False
    if candidate != canonical:
        return False
    for relative_path, entry in SKILL_MANIFEST.items():
        if entry.kind != "file":
            continue
        if (candidate_root / relative_path).read_bytes() != (
            canonical_root / relative_path
        ).read_bytes():
            return False
    return True


def parse_arguments(arguments: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--candidate-root",
        type=Path,
        default=ROOT / "skills/custom-learning-audiobook",
    )
    parser.add_argument("--canonical-root", type=Path, default=DEFAULT_CANONICAL)
    parser.add_argument("--external-root", type=Path, default=DEFAULT_EXTERNAL)
    parser.add_argument("--hermes-command", type=Path, default=Path("hermes"))
    parser.add_argument("--hermes-python", type=Path, default=DEFAULT_HERMES_PYTHON)
    parser.add_argument(
        "--hermes-source-root", type=Path, default=DEFAULT_HERMES_SOURCE_ROOT
    )
    parser.add_argument("--link", action="append", type=Path)
    return parser.parse_args(arguments)


def main(arguments: list[str]) -> int:
    options = parse_arguments(arguments)
    links = tuple(options.link or DEFAULT_LINKS)
    canonical = options.canonical_root.resolve()

    manifest_error = candidate_manifest_error(options.candidate_root)
    if manifest_error is not None:
        return fail(manifest_error)

    for link in links:
        if not link.is_symlink():
            return fail(f"not a symlink: {link}")
        if link.resolve() != canonical:
            return fail(f"wrong target: {link} -> {link.resolve()}")

    discoverable_external = tuple(
        path
        for path in options.external_root.rglob(EXTERNAL_DISCOVERABLE_SKILL.name)
        if path.name == EXTERNAL_DISCOVERABLE_SKILL.name
    )
    if discoverable_external:
        return fail(
            "discoverable independent Hermes skill must be absent: "
            + ", ".join(str(path) for path in discoverable_external)
        )

    for relative_path in EXTERNAL_GUARD_FILES:
        external_path = options.external_root / relative_path
        if not external_path.is_file():
            return fail(f"missing independent Hermes guard: {external_path}")
        external_text = external_path.read_text(encoding="utf-8")
        if external_text != EXTERNAL_STUBS[relative_path]:
            return fail(
                f"independent Hermes import is not the exact disabled stub: {external_path}"
            )

    try:
        discovery = subprocess.run(
            [str(options.hermes_command), "skills", "list", "--source", "local"],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as error:
        return fail(f"cannot run Hermes discovery: {error}")
    if discovery.returncode != 0:
        return fail(f"Hermes discovery failed: {discovery.stderr.strip()}")
    discovery_rows = [
        line
        for line in discovery.stdout.splitlines()
        if "custom-learning-audiobook" in line
    ]
    if len(discovery_rows) != 1 or "openclaw-imports" in discovery_rows[0]:
        return fail("Hermes discovery did not select the canonical skill exactly once")

    skill_view_code = (
        "from tools.skills_tool import skill_view\n"
        "print(skill_view('custom-learning-audiobook', preprocess=False))\n"
    )
    try:
        bare_view = subprocess.run(
            [str(options.hermes_python), "-c", skill_view_code],
            cwd=options.hermes_source_root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as error:
        return fail(f"cannot run Hermes bare skill_view: {error}")
    if bare_view.returncode != 0:
        return fail(f"Hermes bare skill_view failed: {bare_view.stderr.strip()}")
    try:
        view_payload = json.loads(bare_view.stdout)
    except json.JSONDecodeError as error:
        return fail(f"Hermes bare skill_view returned invalid JSON: {error}")
    if not isinstance(view_payload, dict) or view_payload.get("success") is not True:
        return fail(f"Hermes bare skill_view was not successful: {view_payload}")
    skill_dir_value = view_payload.get("skill_dir")
    if not isinstance(skill_dir_value, str) or not skill_dir_value:
        return fail("Hermes bare skill_view omitted skill_dir")
    loaded_skill_dir = Path(skill_dir_value)
    loaded_skill_file = loaded_skill_dir / "SKILL.md"
    canonical_skill_file = options.canonical_root / "SKILL.md"
    if (
        loaded_skill_dir.name != "custom-learning-audiobook"
        or loaded_skill_dir.resolve() != canonical
        or not loaded_skill_file.is_file()
        or loaded_skill_file.resolve() != canonical_skill_file.resolve()
    ):
        return fail(
            "Hermes bare skill_view did not load canonical skill: "
            f"{loaded_skill_file}"
        )
    try:
        canonical_content = canonical_skill_file.read_text(encoding="utf-8")
    except OSError as error:
        return fail(f"cannot read canonical skill content: {error}")
    if view_payload.get("content") != canonical_content:
        return fail("Hermes bare skill_view content does not equal canonical SKILL.md")

    if not installed_manifest_matches(options.candidate_root, options.canonical_root):
        return pending(options.candidate_root, options.canonical_root)

    print("installed_skill_parity: current")
    print(f"installed_canonical={options.canonical_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
