#!/usr/bin/env python3
"""Validate repo skill contracts without external dependencies."""

import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
_YAML_KEY = re.compile(r"[A-Za-z_][A-Za-z0-9_-]*")
_YAML_NON_STRING = re.compile(
    r"(?:null|~|true|false|yes|no|on|off|"
    r"[-+]?(?:0b[01_]+|0o[0-7_]+|0x[0-9a-f_]+|[0-9][0-9_]*"
    r"(?:\.[0-9_]*)?(?:[eE][-+]?[0-9]+)?|\.[0-9_]+"
    r"(?:[eE][-+]?[0-9]+)?|\.inf|\.nan)|"
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}(?:[Tt ]"
    r"[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?"
    r"(?:Z|[-+][0-9]{1,2}(?::?[0-9]{2})?)?)?)\Z",
    re.IGNORECASE,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _quoted_yaml_string(value: str, label: str) -> str:
    if value.startswith('"'):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as error:
            raise AssertionError(f"{label} has malformed double quotes") from error
        require(isinstance(parsed, str), f"{label} must be a string")
        return parsed
    require(value.endswith("'") and len(value) >= 2, f"{label} has unterminated quotes")
    inner = value[1:-1]
    index = 0
    result: list[str] = []
    while index < len(inner):
        if inner[index] != "'":
            result.append(inner[index])
            index += 1
            continue
        require(
            index + 1 < len(inner) and inner[index + 1] == "'",
            f"{label} has malformed single quotes",
        )
        result.append("'")
        index += 2
    return "".join(result)


def _yaml_string(value: str, label: str) -> str:
    require(value and "\t" not in value, f"{label} must be a string")
    if value[0] in {'"', "'"}:
        return _quoted_yaml_string(value, label)
    require(
        value[0] not in "#[{&*!|>@`" and not value.startswith(("- ", "? ", ": ")),
        f"{label} must be a scalar string",
    )
    require(
        not value.endswith(("]", "}")) and ": " not in value and " #" not in value,
        f"{label} must be a scalar string",
    )
    require(_YAML_NON_STRING.fullmatch(value) is None, f"{label} must be a string")
    return value


def _fold_block(lines: list[str | None], marker: str) -> str:
    if marker.startswith("|"):
        value = "\n".join("" if line is None else line for line in lines)
    else:
        paragraphs: list[str] = []
        words: list[str] = []
        for line in lines:
            if line is None:
                if words:
                    paragraphs.append(" ".join(words))
                    words = []
                elif paragraphs:
                    paragraphs.append("")
            else:
                words.append(line)
        if words:
            paragraphs.append(" ".join(words))
        value = "\n".join(paragraphs)
    return value if marker.endswith("-") else value + "\n"


def _flat_yaml_strings(source: str, label: str) -> dict[str, str]:
    result: dict[str, str] = {}
    lines = source.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line:
            index += 1
            continue
        require("\t" not in line, f"{label} contains a tab")
        require(not line[0].isspace(), f"{label} has malformed indentation")
        require(":" in line, f"{label} has an invalid mapping entry")
        key, value = line.split(":", 1)
        require(_YAML_KEY.fullmatch(key) is not None, f"{label} has an invalid key")
        require(key not in result, f"{label} has duplicate key: {key}")
        require(not value.startswith("\t"), f"{label} contains a tab")
        value = value.strip()
        if value in {">", ">-", "|", "|-"}:
            block_lines: list[str | None] = []
            block_indent: int | None = None
            index += 1
            while index < len(lines):
                continuation = lines[index]
                require("\t" not in continuation, f"{label} contains a tab")
                if not continuation:
                    block_lines.append(None)
                    index += 1
                    continue
                indent = len(continuation) - len(continuation.lstrip(" "))
                if indent == 0:
                    break
                if block_indent is None:
                    block_indent = indent
                require(
                    indent == block_indent,
                    f"{label} has malformed block indentation",
                )
                block_lines.append(continuation[indent:])
                index += 1
            require(block_indent is not None, f"{label} has an empty block scalar")
            result[key] = _fold_block(block_lines, value)
        else:
            require(value, f"{label} does not support nested values")
            result[key] = _yaml_string(value, f"{label} {key}")
            index += 1
    return result


def frontmatter(markdown: str) -> dict[str, str]:
    require(markdown.startswith("---\n"), "missing YAML frontmatter")
    end = markdown.find("\n---\n", 4)
    require(end != -1, "unterminated YAML frontmatter")
    return _flat_yaml_strings(markdown[4:end], "YAML frontmatter")


def parse_agent_metadata(source: str, skill_name: str) -> dict[str, str]:
    lines = source.splitlines()
    require(lines and lines[0] == "interface:", "agent metadata must contain interface")
    nested: list[str] = []
    for line in lines[1:]:
        if not line:
            continue
        require("\t" not in line, "agent metadata contains a tab")
        indent = len(line) - len(line.lstrip(" "))
        require(indent == 2, "agent metadata has malformed indentation")
        nested.append(line[2:])
    interface = _flat_yaml_strings("\n".join(nested), "agent interface")
    require(
        set(interface) == {"display_name", "short_description", "default_prompt"},
        "agent interface must contain exactly the three supported fields",
    )
    for key, value in interface.items():
        require(bool(value), f"agent interface {key} must be nonempty")
    require(
        re.search(
            rf"(?<![A-Za-z0-9_-])\${re.escape(skill_name)}(?![A-Za-z0-9_-])",
            interface["default_prompt"],
        )
        is not None,
        f"agent default_prompt must name ${skill_name}",
    )
    return interface


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
    parse_agent_metadata(
        read("skills/fiction-audiobook/agents/openai.yaml"), "fiction-audiobook"
    )
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
