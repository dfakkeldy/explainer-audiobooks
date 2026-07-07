#!/usr/bin/env python3
"""Validate repo skill contracts without external dependencies."""

from pathlib import Path
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
    for line in markdown[4:end].splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip()
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


def main() -> int:
    validate_skill("skill", "explainer-audiobook")
    validate_skill("skills/custom-learning-audiobook", "custom-learning-audiobook")
    validate_skill("skills/longform-book-development", "longform-book-development")

    contains(
        "skill/SKILL.md",
        "am_michael",
        "am_puck",
        "do not use `af_heart` as the default",
    )
    contains(
        "skills/custom-learning-audiobook/SKILL.md",
        "one lead writer",
        "source-confidence label",
        "public-safe",
        "interior pictures",
        "M4B/alignment",
        "Do not use `af_heart` as the default narrator.",
    )
    contains(
        "skills/custom-learning-audiobook/references/intake-and-research.md",
        "Open Notebook",
        "public-safe",
        "Sensitive/high-stakes",
    )
    contains(
        "skills/custom-learning-audiobook/references/package-and-qc.md",
        "echo-cli",
        "--voice am_michael",
        "<slug>.alignment.json",
        "ffprobe",
        "Interior Figures",
    )
    contains(
        "skills/custom-learning-audiobook/agents/openai.yaml",
        "$custom-learning-audiobook",
    )
    contains(
        "skills/longform-book-development/SKILL.md",
        "handoff packet",
        "picture plan",
        "custom-learning-audiobook",
    )
    contains(
        "skills/longform-book-development/references/handoff-packet.md",
        "Figure Plan",
        "chapters/images/",
        "$custom-learning-audiobook",
    )
    contains(
        "skills/longform-book-development/agents/openai.yaml",
        "$longform-book-development",
    )

    print("validate_skills: clean")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as error:
        print(f"validate_skills: {error}", file=sys.stderr)
        raise SystemExit(1)
