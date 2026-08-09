#!/usr/bin/env python3
"""Validate repo skill contracts without external dependencies."""

import importlib.util
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def frontmatter(markdown: str) -> dict[str, str]:
    if not markdown.startswith("---\n"):
        raise AssertionError("missing YAML frontmatter")
    end = markdown.find("\n---\n", 4)
    if end == -1:
        raise AssertionError("unterminated YAML frontmatter")
    result: dict[str, str] = {}
    block_key: str | None = None
    for line in markdown[4:end].splitlines():
        if not line.strip():
            continue
        if line[0].isspace() and block_key is not None:
            result[block_key] = " ".join(
                part for part in (result[block_key], line.strip()) if part
            )
            continue
        if ":" not in line:
            raise AssertionError("invalid YAML frontmatter")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        require(bool(key), "invalid YAML frontmatter key")
        if value in {">", ">-", "|", "|-"}:
            result[key] = ""
            block_key = key
        else:
            result[key] = value
            block_key = None
    return result


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def contains(path: str, *needles: str) -> None:
    text = read(path)
    for needle in needles:
        require(needle in text, f"{path} missing {needle!r}")


def validate_skill(path: str, name: str) -> None:
    text = read(f"{path}/SKILL.md")
    meta = frontmatter(text)
    require(meta.get("name") == name, f"{path}/SKILL.md has wrong name")
    description = meta.get("description", "")
    require(description, f"{path}/SKILL.md missing description")
    require(len(description) <= 1024, f"{path}/SKILL.md description too long")
    require("TODO" not in text, f"{path}/SKILL.md still has TODO text")


def validate_python_helper(path: str) -> None:
    script = ROOT / path
    module_name = f"validate_skills_{script.stem}"
    spec = importlib.util.spec_from_file_location(module_name, script)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    previous = sys.modules.get(module_name)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        if previous is None:
            sys.modules.pop(module_name, None)
        else:
            sys.modules[module_name] = previous
    result = subprocess.run(
        [sys.executable, str(script), "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    require(result.returncode == 0, f"{path} --help failed: {result.stderr.strip()}")
    require("usage:" in result.stdout, f"{path} --help did not print usage")


def main() -> int:
    validate_skill("skill", "audiobook")
    validate_skill("skills/longform-book-development", "longform-book-development")
    validate_skill("skills/fiction-book-development", "fiction-book-development")
    validate_skill("skills/fiction-audiobook", "fiction-audiobook")

    fiction_support = (
        "skills/fiction-audiobook/SKILL.md",
        "skills/fiction-audiobook/agents/openai.yaml",
        "skills/fiction-audiobook/references/express-fiction-craft.md",
        "skills/fiction-audiobook/references/public-fiction-gate.md",
        "skills/fiction-audiobook/scripts/fiction_voice_preferences.py",
        "skills/fiction-audiobook/scripts/stage_echo_delivery.py",
    )
    for path in fiction_support:
        require((ROOT / path).is_file(), f"missing fiction-audiobook support path: {path}")
    contains("skills/fiction-audiobook/agents/openai.yaml", "$fiction-audiobook")
    for path in fiction_support[-2:]:
        validate_python_helper(path)

    paired_contract = (
        "exactly three", "1600×2560", "cover.png", "2400×2400", "m4b-cover.png",
    )
    for path in (
        "skill/SKILL.md", "skill/references/cover-art.md",
        "README.md", "docs/how-these-were-made.md", "docs/make-your-own.md",
    ):
        contains(path, *paired_contract)

    # Receipt and sync commands are isolated in the rare public-publishing lane.
    complete_paired = (
        "render_cover_pair(", "portrait_spec=", "square_spec=",
        "portrait_output=", "square_output=", "portrait_thumbnail=",
        "square_thumbnail=", "portrait_receipt=", "square_receipt=",
        "--portrait-render-receipt", "--square-render-receipt",
        "--selection-source user", "--privacy-classification",
        "--out \"$PAIR/cover-selection.json\"",
        "--selection \"$PAIR/cover-selection.json\"",
        "--m4b-cover \"$PAIR/m4b-cover.png\"",
        "echo_pronunciation_narrate.sh",
        "--paired-artifact-dir \"$PAIR\"", "--public-destination",
        "--intent reuse", "--apply",
    )
    contains(
        "skill/references/publishing-a-public-edition.md",
        *complete_paired,
    )

    publishing = "skill/references/publishing-a-public-edition.md"
    contains(publishing, "Never mutate a narrated M4B", "replace_m4b_cover.py")
    require(
        "--portrait-cover \"$PAIR/cover.png\"" not in read(publishing),
        f"{publishing} teaches the retired post-narration cover mutation flow",
    )

    contains(
        "skill/SKILL.md",
        "am_michael",
        "am_puck",
        "never `af_heart`",
        "Dan Fakkeldy",
        "--contributor",
        "AI-writing patterns to avoid",
        "`humanizer`",
        "must not invent anecdotes",
    )
    contains(
        "skills/longform-book-development/SKILL.md",
        "humanizer-pass.md",
        "desired humanizing level",
        "bounded `humanizer` pass",
    )
    contains(
        "skill/references/humanizer-pass.md",
        "bounded voice pass",
        "Do not invent anecdotes",
        "targeted edits with a short reason",
    )
    contains(
        "skill/references/cover-art.md",
        "Copy-ready image-generation prompt",
        "No title, no subtitle, no author name",
        "generic infographic",
        "stronger art direction",
    )
    contains(
        "skills/echo-narration/references/narrating.md",
        "echo-cli",
        "--voice am_michael",
        "<slug>.alignment.json",
        "ffprobe",
    )
    contains(
        "skills/longform-book-development/SKILL.md",
        "handoff packet",
        "picture plan",
        "audiobook",
    )
    contains(
        "skills/longform-book-development/references/handoff-packet.md",
        "Figure Plan",
        "chapters/images/",
        "$audiobook",
    )
    contains(
        "skills/longform-book-development/agents/openai.yaml",
        "$longform-book-development",
    )
    contains(
        "skills/fiction-book-development/SKILL.md",
        "One manuscript owner",
        "Causality over chronology",
        "Style by observable choices",
        "Continuity is active",
        "Revision is staged",
        "Production is opt-in",
        "templates/fiction-project.md",
    )
    contains(
        "skills/fiction-book-development/references/story-bible-and-continuity.md",
        "Character engine",
        "Knowledge and secrets",
        "Promises and payoffs",
        "Research and representation ledger",
    )
    contains(
        "skills/fiction-book-development/references/style-and-scene-craft.md",
        "Style control panel",
        "Do not imitate a living author",
        "Scene engine",
        "Read-aloud test",
    )
    contains(
        "skills/fiction-book-development/references/revision-passes.md",
        "Pass 1: Premise and structure",
        "Pass 8: Read-aloud and final canon",
        "Reader feedback triage",
    )
    contains(
        "skills/fiction-book-development/agents/openai.yaml",
        "$fiction-book-development",
    )

    print("validate_skills: clean")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as error:
        print(f"validate_skills: {error}", file=sys.stderr)
        raise SystemExit(1)
