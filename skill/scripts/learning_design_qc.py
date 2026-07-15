#!/usr/bin/env python3
"""Validate audiobook learning-design evidence and bind it to final chapters."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
REQUIRED_RECORDS = {
    "brief": "learning-brief.json",
    "outline": "learning-outline.json",
    "plans": "chapter-plans.json",
    "coverage": "coverage-ledger.json",
    "continuity": "continuity.json",
    "review": "learning-review.json",
}
AUTHORIZATION_SOURCES = {"user", "explicit-autonomous-run"}
CURRICULUM_PATTERNS = {
    "mechanism-first-spiral",
    "end-to-end-trace",
    "problem-progression",
}
FINAL_FINDING_DECISIONS = {"accepted", "rejected", "resolved"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_record(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"missing {label} record: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"invalid {label} record: {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{label} record must be a JSON object")
    if value.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError(f"{label}.schemaVersion must be {SCHEMA_VERSION}")
    return value


def require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def require_bool(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field} must be a boolean")
    return value


def require_positive_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{field} must be a positive integer")
    return value


def require_list(value: Any, field: str, *, allow_empty: bool = False) -> list[Any]:
    if not isinstance(value, list) or (not allow_empty and not value):
        qualifier = "a list" if allow_empty else "a non-empty list"
        raise ValueError(f"{field} must be {qualifier}")
    return value


def require_string_list(value: Any, field: str, *, allow_empty: bool = False) -> list[str]:
    values = require_list(value, field, allow_empty=allow_empty)
    for index, item in enumerate(values):
        require_string(item, f"{field}[{index}]")
    return values


def chapter_paths(chapters_dir: Path) -> list[Path]:
    paths = sorted(chapters_dir.glob("ch*.md"))
    if not paths:
        raise ValueError(f"no canonical chapter files found in {chapters_dir}")
    return paths


def chapter_hashes(chapters_dir: Path) -> dict[str, str]:
    return {path.name: sha256_file(path) for path in chapter_paths(chapters_dir)}


def manuscript_word_count(chapters_dir: Path) -> int:
    return sum(len(path.read_text(encoding="utf-8").split()) for path in chapter_paths(chapters_dir))


def unique_records(items: Any, key: str, field: str) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(require_list(items, field)):
        if not isinstance(item, dict):
            raise ValueError(f"{field}[{index}] must be an object")
        identity = require_string(item.get(key), f"{field}[{index}].{key}")
        if identity in records:
            raise ValueError(f"duplicate {field} entry for {identity}")
        records[identity] = item
    return records


def validate_orientation(brief: dict[str, Any]) -> None:
    require_string(brief.get("learnerOutcome"), "brief.learnerOutcome")
    require_string(brief.get("priorKnowledge"), "brief.priorKnowledge")
    orientation = brief.get("openingOrientation")
    if not isinstance(orientation, dict):
        raise ValueError("brief.openingOrientation must be an object")
    for field in ("context", "promise", "route"):
        require_string(orientation.get(field), f"brief.openingOrientation.{field}")


def validate_target(brief: dict[str, Any], actual_words: int) -> dict[str, int]:
    original = require_positive_int(brief.get("originalTargetWords"), "brief.originalTargetWords")
    current = require_positive_int(brief.get("currentTargetWords"), "brief.currentTargetWords")
    minimum = require_positive_int(brief.get("minimumAcceptedWords"), "brief.minimumAcceptedWords")
    maximum = require_positive_int(brief.get("maximumAcceptedWords"), "brief.maximumAcceptedWords")
    if not minimum <= current <= maximum:
        raise ValueError("brief current target must fall inside its accepted word range")
    if minimum > maximum:
        raise ValueError("brief minimumAcceptedWords exceeds maximumAcceptedWords")

    drafting_started = require_bool(brief.get("draftingStarted"), "brief.draftingStarted")
    history = require_list(brief.get("scopeHistory"), "brief.scopeHistory", allow_empty=True)
    if drafting_started and current < original:
        approved_reduction = False
        for index, entry in enumerate(history):
            if not isinstance(entry, dict):
                raise ValueError(f"brief.scopeHistory[{index}] must be an object")
            if entry.get("oldTargetWords") == original and entry.get("newTargetWords") == current:
                approved_reduction = (
                    entry.get("approved") is True
                    and entry.get("approvalSource") == "user"
                    and isinstance(entry.get("reason"), str)
                    and bool(entry["reason"].strip())
                    and isinstance(entry.get("evidence"), str)
                    and bool(entry["evidence"].strip())
                )
                break
        if not approved_reduction:
            raise ValueError(
                "target reduction after drafting requires explicit user approval and evidence"
            )
    if not minimum <= actual_words <= maximum:
        raise ValueError(
            f"manuscript word count {actual_words} is outside accepted range {minimum}-{maximum}"
        )
    return {
        "originalTargetWords": original,
        "currentTargetWords": current,
        "minimumAcceptedWords": minimum,
        "maximumAcceptedWords": maximum,
        "actualWords": actual_words,
    }


def validate_outline(outline: dict[str, Any], chapter_names: set[str]) -> None:
    authorization = outline.get("authorization")
    if not isinstance(authorization, dict):
        raise ValueError("outline.authorization must be an object")
    if authorization.get("status") != "approved":
        raise ValueError("outline.authorization.status must be approved")
    if authorization.get("source") not in AUTHORIZATION_SOURCES:
        raise ValueError("outline.authorization.source must be user or explicit-autonomous-run")
    require_string(authorization.get("evidence"), "outline.authorization.evidence")

    curriculum_pattern = outline.get("curriculumPattern")
    if not isinstance(curriculum_pattern, dict):
        raise ValueError("outline.curriculumPattern must be an object")
    pattern_name = require_string(
        curriculum_pattern.get("name"), "outline.curriculumPattern.name"
    )
    if pattern_name not in CURRICULUM_PATTERNS:
        raise ValueError(
            "outline.curriculumPattern.name must be mechanism-first-spiral, "
            "end-to-end-trace, or problem-progression"
        )
    require_string(
        curriculum_pattern.get("reason"), "outline.curriculumPattern.reason"
    )
    require_string(
        curriculum_pattern.get("fitEvidence"),
        "outline.curriculumPattern.fitEvidence",
    )

    throughlines = require_string_list(outline.get("throughlines"), "outline.throughlines")
    if not 2 <= len(throughlines) <= 4:
        raise ValueError("outline.throughlines must contain two to four genuine throughlines")
    chapters = unique_records(outline.get("chapters"), "file", "outline.chapters")
    if set(chapters) != chapter_names:
        raise ValueError("outline chapters must match canonical chapter files exactly")
    for filename, chapter in chapters.items():
        require_string(chapter.get("purpose"), f"outline.chapters[{filename}].purpose")
        require_string_list(
            chapter.get("prerequisites"),
            f"outline.chapters[{filename}].prerequisites",
            allow_empty=True,
        )


def validate_chapter_plans(plans: dict[str, Any], chapter_names: set[str]) -> None:
    records = unique_records(plans.get("chapters"), "file", "chapter-plans.chapters")
    if set(records) != chapter_names:
        raise ValueError("one chapter plan is required for every canonical chapter")
    for filename, plan in records.items():
        prefix = f"chapter-plans[{filename}]"
        for field in ("purpose", "knowledgeDelta", "groundedExample"):
            require_string(plan.get(field), f"{prefix}.{field}")
        require_string_list(plan.get("prerequisites"), f"{prefix}.prerequisites", allow_empty=True)
        require_string_list(plan.get("concepts"), f"{prefix}.concepts")
        beats = require_string_list(plan.get("beats"), f"{prefix}.beats")
        if len(beats) < 3:
            raise ValueError(f"{prefix}.beats must contain at least three teaching jobs")


def validate_coverage(coverage: dict[str, Any], chapter_names: set[str]) -> None:
    concepts = unique_records(coverage.get("concepts"), "name", "coverage-ledger.concepts")
    for name, concept in concepts.items():
        prefix = f"coverage-ledger[{name}]"
        for field in (
            "definition",
            "reason",
            "mechanism",
            "concreteCase",
            "misconception",
            "expectedAbility",
        ):
            require_string(concept.get(field), f"{prefix}.{field}")
        boundary = concept.get("boundary")
        not_applicable = concept.get("boundaryNotApplicableReason")
        if not (
            isinstance(boundary, str)
            and boundary.strip()
            or isinstance(not_applicable, str)
            and not_applicable.strip()
        ):
            raise ValueError(f"{prefix} requires boundary or boundaryNotApplicableReason")
        uses = require_list(concept.get("chapterUses"), f"{prefix}.chapterUses")
        for index, use in enumerate(uses):
            if not isinstance(use, dict):
                raise ValueError(f"{prefix}.chapterUses[{index}] must be an object")
            chapter = require_string(use.get("chapter"), f"{prefix}.chapterUses[{index}].chapter")
            if chapter not in chapter_names:
                raise ValueError(f"{prefix}.chapterUses[{index}] names unknown chapter {chapter}")
            require_string(use.get("function"), f"{prefix}.chapterUses[{index}].function")


def validate_continuity(continuity: dict[str, Any], chapter_names: set[str]) -> None:
    checkpoints = unique_records(
        continuity.get("checkpoints"), "afterChapter", "continuity.checkpoints"
    )
    if set(checkpoints) != chapter_names:
        raise ValueError("one continuity checkpoint is required after every canonical chapter")
    for filename, checkpoint in checkpoints.items():
        prefix = f"continuity[{filename}]"
        for field in (
            "termsDefined",
            "examplesUsed",
            "callbacks",
            "promises",
            "unresolvedQuestions",
        ):
            require_string_list(checkpoint.get(field), f"{prefix}.{field}", allow_empty=True)


def validate_findings(findings: Any, field: str) -> None:
    for index, finding in enumerate(require_list(findings, field, allow_empty=True)):
        if not isinstance(finding, dict):
            raise ValueError(f"{field}[{index}] must be an object")
        prefix = f"{field}[{index}]"
        for name in ("id", "location", "category", "evidence"):
            require_string(finding.get(name), f"{prefix}.{name}")
        decision = finding.get("decision")
        if decision not in FINAL_FINDING_DECISIONS:
            raise ValueError(f"{prefix} has unresolved decision")
        require_string(finding.get("reason"), f"{prefix}.reason")


def validate_review(review: dict[str, Any], hashes: dict[str, str]) -> None:
    if review.get("reviewedChapterSHA256") != hashes:
        raise ValueError("review.reviewedChapterSHA256 does not match final canonical chapters")
    reviewers: list[str] = []
    for name in ("structure", "beginnerReader"):
        lane = review.get(name)
        if not isinstance(lane, dict):
            raise ValueError(f"review.{name} must be an object")
        reviewers.append(require_string(lane.get("reviewer"), f"review.{name}.reviewer"))
        if lane.get("verdict") != "pass":
            raise ValueError(f"review.{name}.verdict must be pass")
        validate_findings(lane.get("findings"), f"review.{name}.findings")
    if len(set(reviewers)) != len(reviewers):
        raise ValueError("structure and beginnerReader reviews require independent reviewers")


def validate_run(run_root: Path) -> dict[str, Any]:
    run_root = Path(run_root)
    chapters_dir = run_root / "chapters"
    research_dir = run_root / "research"
    paths = {name: research_dir / filename for name, filename in REQUIRED_RECORDS.items()}
    records = {name: load_record(path, name) for name, path in paths.items()}
    hashes = chapter_hashes(chapters_dir)
    names = set(hashes)
    actual_words = manuscript_word_count(chapters_dir)

    validate_orientation(records["brief"])
    word_count = validate_target(records["brief"], actual_words)
    validate_outline(records["outline"], names)
    validate_chapter_plans(records["plans"], names)
    validate_coverage(records["coverage"], names)
    validate_continuity(records["continuity"], names)
    validate_review(records["review"], hashes)

    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "pass",
        "chapterSHA256": hashes,
        "recordSHA256": {name: sha256_file(path) for name, path in paths.items()},
        "wordCount": word_count,
        "gates": {
            "learnerOrientation": "pass",
            "outlineAuthorization": "pass",
            "chapterTeachingPlans": "pass",
            "explanationPaths": "pass",
            "continuity": "pass",
            "structuralReview": "pass",
            "beginnerReaderReview": "pass",
        },
    }


def write_receipt(run_root: Path, output: Path) -> dict[str, Any]:
    receipt = validate_run(Path(run_root))
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def verify_learning_receipt(chapters_dir: Path, receipt_path: Path) -> dict[str, Any]:
    receipt_path = Path(receipt_path)
    receipt = load_record(receipt_path, "learning-design receipt")
    if receipt.get("status") != "pass":
        raise ValueError("learning-design receipt status must be pass")
    expected = chapter_hashes(Path(chapters_dir))
    if receipt.get("chapterSHA256") != expected:
        raise ValueError("learning-design receipt chapter hash mismatch")
    gates = receipt.get("gates")
    if not isinstance(gates, dict) or not gates or any(value != "pass" for value in gates.values()):
        raise ValueError("learning-design receipt contains a non-passing gate")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate audiobook learning design and bind it to final chapters."
    )
    parser.add_argument("--run-root", required=True, type=Path)
    parser.add_argument("--receipt-out", required=True, type=Path)
    args = parser.parse_args()
    receipt = write_receipt(args.run_root, args.receipt_out)
    print(f"learning design: {receipt['status']}")
    print(f"receipt: {args.receipt_out}")


if __name__ == "__main__":
    main()
