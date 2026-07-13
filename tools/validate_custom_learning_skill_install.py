#!/usr/bin/env python3
"""Report whether installed custom-learning skill links expose this candidate."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANONICAL = Path(
    "/Users/dfakkeldy/Developer/explainer-audiobooks/skills/custom-learning-audiobook"
)
DEFAULT_EXTERNAL = (
    Path.home() / ".hermes/skills/openclaw-imports/custom-learning-audiobook"
)
DEFAULT_LINKS = tuple(
    Path.home() / base / "skills/custom-learning-audiobook"
    for base in (".codex", ".agents", ".claude", ".hermes")
)
CONTRACT_FILES = (
    Path("SKILL.md"),
    Path("references/package-and-qc.md"),
    Path("scripts/echo_pronunciation_preflight.sh"),
    Path("scripts/validate_pronunciation_audit.py"),
)
EXTERNAL_GUARD_FILES = (Path("SKILL.md"), Path("references/package-and-qc.md"))
DISABLED_MARKER = "DISABLED: canonical skill required"
CANONICAL_ROUTE = "/Users/dfakkeldy/.hermes/skills/custom-learning-audiobook"
EXTERNAL_SKILL_STUB = f"""---
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
    Path("SKILL.md"): EXTERNAL_SKILL_STUB,
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
    parser.add_argument("--link", action="append", type=Path)
    return parser.parse_args(arguments)


def main(arguments: list[str]) -> int:
    options = parse_arguments(arguments)
    links = tuple(options.link or DEFAULT_LINKS)
    canonical = options.canonical_root.resolve()

    for link in links:
        if not link.is_symlink():
            return fail(f"not a symlink: {link}")
        if link.resolve() != canonical:
            return fail(f"wrong target: {link} -> {link.resolve()}")

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

    for relative_path in CONTRACT_FILES:
        candidate_path = options.candidate_root / relative_path
        canonical_path = options.canonical_root / relative_path
        if not candidate_path.is_file():
            return fail(f"candidate is missing contract file: {relative_path}")
        if not canonical_path.is_file():
            return pending(options.candidate_root, options.canonical_root)
        if candidate_path.read_bytes() != canonical_path.read_bytes():
            return pending(options.candidate_root, options.canonical_root)

    print("installed_skill_parity: current")
    print(f"installed_canonical={options.canonical_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
