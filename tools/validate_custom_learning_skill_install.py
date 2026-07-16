#!/usr/bin/env python3
"""Report whether installed custom-learning skill links expose this candidate."""

from __future__ import annotations

import argparse
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


SKILL_MANIFEST = {
    Path("SKILL.md"): ManifestEntry("file", 0o644),
    Path("agents"): ManifestEntry("directory", 0o755),
    Path("agents/openai.yaml"): ManifestEntry("file", 0o644),
    Path("references"): ManifestEntry("directory", 0o755),
    Path("references/intake-and-research.md"): ManifestEntry("file", 0o644),
    Path("references/package-and-qc.md"): ManifestEntry("file", 0o644),
    Path("scripts"): ManifestEntry("directory", 0o755),
    Path("scripts/echo_pronunciation_preflight.sh"): ManifestEntry("file", 0o755),
    Path("scripts/echo_learning_pilot_narrate.sh"): ManifestEntry("file", 0o755),
    Path("scripts/echo_pronunciation_narrate.sh"): ManifestEntry("file", 0o755),
    Path("scripts/echo_pronunciation_lease.py"): ManifestEntry("file", 0o755),
    Path("scripts/echo_pronunciation_state.py"): ManifestEntry("file", 0o755),
    Path("scripts/validate_pronunciation_audit.py"): ManifestEntry("file", 0o755),
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
    return None


def installed_manifest_matches(candidate_root: Path, canonical_root: Path) -> bool:
    try:
        candidate = skill_inventory(candidate_root)
        canonical = skill_inventory(canonical_root)
    except (OSError, ValueError):
        return False
    if candidate != canonical or candidate != SKILL_MANIFEST:
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
