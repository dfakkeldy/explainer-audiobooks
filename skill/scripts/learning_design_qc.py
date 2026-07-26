#!/usr/bin/env python3
"""Validate audiobook learning-design evidence and bind it to final chapters."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 2
REQUIRED_RECORDS = {
    "evidence": "evidence-notes.json",
    "brief": "learning-brief.json",
    "outline": "learning-outline.json",
    "plans": "chapter-plans.json",
    "coverage": "coverage-ledger.json",
    "continuity": "continuity.json",
    "review": "learning-review.json",
    "pilot": "comprehension-pilot.json",
    "revisions": "revision-passes.json",
}
AUTHORIZATION_SOURCES = {"user", "explicit-autonomous-run"}
CURRICULUM_PATTERNS = {
    "mechanism-first-spiral",
    "end-to-end-trace",
    "problem-progression",
    "question-led-narrative",
}
AUDIENCE_LEVELS = {"beginner", "intermediate", "advanced"}
LISTENING_MODES = {"road-book", "focused-study"}
REVISION_MODES = {"new-book", "first-edition-plus"}
PRODUCTION_MODES = {"governed-final", "unattended-first-listen"}
UNATTENDED_DECISION_SOURCES = {
    "user-request",
    "project-context",
    "documented-default",
    "editorial-judgment",
}
CALCULATION_TREATMENTS = {
    "none",
    "brief-spoken",
    "optional-study",
    "focused-lesson",
}
FINAL_FINDING_DECISIONS = {"accepted", "rejected", "resolved"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
VOICE_SOURCE_MODES = {
    "private-source-craft-analysis",
    "project-brief",
    "user-supplied-exemplar",
}
REQUIRED_REVISION_PASSES = {
    "claim-traceability",
    "tightening",
    "de-listification",
    "sentence-rhythm",
    "ear-pass",
}
PUBLIC_FIRST_LISTEN_DISCLOSURE = (
    "This edition has passed package and audio checks. The creator's full "
    "listening review is still underway."
)


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


def require_nonnegative_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
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


def validate_bound_artifact(
    run_root: Path,
    path_value: Any,
    hash_value: Any,
    field: str,
) -> Path:
    relative = Path(require_string(path_value, f"{field}Path"))
    if relative.is_absolute():
        raise ValueError(f"{field}Path must be relative to the run root")
    root = run_root.resolve()
    artifact = (root / relative).resolve()
    try:
        artifact.relative_to(root)
    except ValueError as error:
        raise ValueError(f"{field}Path must stay inside the run root") from error
    if not artifact.is_file():
        raise ValueError(f"missing {field} artifact: {artifact}")
    expected = require_string(hash_value, f"{field}SHA256")
    if not SHA256_RE.fullmatch(expected):
        raise ValueError(f"{field}SHA256 must be a lowercase SHA-256 digest")
    if sha256_file(artifact) != expected:
        raise ValueError(f"{field}SHA256 does not match {artifact}")
    return artifact


def validate_evidence(evidence: dict[str, Any], run_root: Path) -> set[str]:
    validate_bound_artifact(
        run_root,
        evidence.get("notesPath"),
        evidence.get("notesSHA256"),
        "evidence.notes",
    )
    if evidence.get("claimPolicy") != "traceable-only":
        raise ValueError("evidence.claimPolicy must be traceable-only")
    claims = unique_records(evidence.get("claims"), "id", "evidence.claims")
    for claim_id, claim in claims.items():
        prefix = f"evidence.claims[{claim_id}]"
        for field in ("claim", "source", "locator"):
            require_string(claim.get(field), f"{prefix}.{field}")
        if claim.get("verificationStatus") != "verified":
            raise ValueError(f"{prefix}.verificationStatus must be verified")
    conflicts = require_list(
        evidence.get("unresolvedConflicts"),
        "evidence.unresolvedConflicts",
        allow_empty=True,
    )
    conflict_ids: set[str] = set()
    for index, conflict in enumerate(conflicts):
        prefix = f"evidence.unresolvedConflicts[{index}]"
        if isinstance(conflict, str):
            require_string(conflict, prefix)
            continue
        if not isinstance(conflict, dict):
            raise ValueError(f"{prefix} must be a non-empty string or an object")
        conflict_id = require_string(conflict.get("id"), f"{prefix}.id")
        if conflict_id in conflict_ids:
            raise ValueError(f"duplicate evidence.unresolvedConflicts entry for {conflict_id}")
        conflict_ids.add(conflict_id)
        for field in ("question", "conflict", "status"):
            require_string(conflict.get(field), f"{prefix}.{field}")
        related_claims = require_string_list(
            conflict.get("claimIds"), f"{prefix}.claimIds"
        )
        unknown_claims = sorted(set(related_claims) - set(claims))
        if unknown_claims:
            raise ValueError(
                f"{prefix}.claimIds names unknown claim {unknown_claims[0]}"
            )
    return set(claims)


def validate_production_mode(
    brief: dict[str, Any], run_root: Path
) -> tuple[str, Path | None, dict[str, str] | None]:
    production = brief.get("productionMode")
    if production is None:
        return "governed-final", None, None
    if not isinstance(production, dict):
        raise ValueError("brief.productionMode must be an object")
    name = require_string(production.get("name"), "brief.productionMode.name")
    if name not in PRODUCTION_MODES:
        raise ValueError(
            "brief.productionMode.name must be governed-final or unattended-first-listen"
        )
    if name == "governed-final":
        return name, None, None

    request_evidence = require_string(
        production.get("requestEvidence"), "brief.productionMode.requestEvidence"
    )
    decisions_path = validate_bound_artifact(
        run_root,
        production.get("decisionsPath"),
        production.get("decisionsSHA256"),
        "brief.productionMode.decisions",
    )
    try:
        decisions = json.loads(decisions_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"invalid unattended decisions receipt: {decisions_path}") from error
    if not isinstance(decisions, dict):
        raise ValueError("unattended decisions receipt must be a JSON object")
    if decisions.get("schemaVersion") != 1:
        raise ValueError("unattended decisions schemaVersion must be 1")
    if decisions.get("productionMode") != "unattended-first-listen":
        raise ValueError("unattended decisions productionMode must be unattended-first-listen")
    if decisions.get("requestEvidence") != request_evidence:
        raise ValueError("unattended decisions requestEvidence must match the learning brief")
    privacy = decisions.get("privacy")
    permission_to_publish = decisions.get("permissionToPublish")
    publication_authorization: dict[str, str] | None = None
    if privacy == "private":
        if permission_to_publish is not False:
            raise ValueError(
                "private unattended decisions permissionToPublish must be false"
            )
        if decisions.get("publicationAuthorization") is not None:
            raise ValueError(
                "private unattended decisions must not claim publication authorization"
            )
    elif privacy == "public-safe":
        if permission_to_publish is not True:
            raise ValueError(
                "public-safe unattended decisions permissionToPublish must be true"
            )
        authorization = decisions.get("publicationAuthorization")
        if not isinstance(authorization, dict):
            raise ValueError(
                "public-safe unattended decisions require publicationAuthorization"
            )
        if authorization.get("status") != "granted":
            raise ValueError("publicationAuthorization.status must be granted")
        if authorization.get("publicationStatus") != "public-first-listen":
            raise ValueError(
                "publicationAuthorization.publicationStatus must be public-first-listen"
            )
        if authorization.get("disclosure") != PUBLIC_FIRST_LISTEN_DISCLOSURE:
            raise ValueError(
                "publicationAuthorization.disclosure must match the approved text"
            )
        authorized_by = require_string(
            authorization.get("authorizedBy"),
            "publicationAuthorization.authorizedBy",
        )
        authorized_at = require_string(
            authorization.get("authorizedAt"),
            "publicationAuthorization.authorizedAt",
        )
        try:
            parsed_authorized_at = datetime.fromisoformat(authorized_at)
        except ValueError as error:
            raise ValueError(
                "publicationAuthorization.authorizedAt must be timezone-aware ISO-8601"
            ) from error
        if parsed_authorized_at.utcoffset() is None:
            raise ValueError(
                "publicationAuthorization.authorizedAt must be timezone-aware ISO-8601"
            )
        evidence = require_string(
            authorization.get("evidence"), "publicationAuthorization.evidence"
        )
        publication_authorization = {
            "status": "public-first-listen",
            "permission": "granted",
            "authorizedBy": authorized_by,
            "authorizedAt": authorized_at,
            "evidence": evidence,
            "disclosure": PUBLIC_FIRST_LISTEN_DISCLOSURE,
        }
    else:
        raise ValueError(
            "unattended decisions privacy must be private or public-safe"
        )
    require_string(decisions.get("deliveryIntent"), "unattended decisions deliveryIntent")
    if decisions.get("humanListeningStatus") != "pending":
        raise ValueError("unattended decisions humanListeningStatus must be pending")
    entries = require_list(decisions.get("decisions"), "unattended decisions")
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValueError(f"unattended decisions[{index}] must be an object")
        for field in ("field", "choice", "reason"):
            require_string(entry.get(field), f"unattended decisions[{index}].{field}")
        source = require_string(
            entry.get("source"), f"unattended decisions[{index}].source"
        )
        if source not in UNATTENDED_DECISION_SOURCES:
            raise ValueError(f"unattended decisions[{index}].source is unsupported")
    return name, decisions_path, publication_authorization


def validate_brief(brief: dict[str, Any], run_root: Path) -> dict[str, Any]:
    require_string(brief.get("learnerOutcome"), "brief.learnerOutcome")
    require_string(brief.get("priorKnowledge"), "brief.priorKnowledge")
    audience_level = require_string(brief.get("audienceLevel"), "brief.audienceLevel")
    if audience_level not in AUDIENCE_LEVELS:
        raise ValueError("brief.audienceLevel must be beginner, intermediate, or advanced")

    listening = brief.get("listeningMode")
    if not isinstance(listening, dict):
        raise ValueError("brief.listeningMode must be an object")
    listening_mode = require_string(listening.get("name"), "brief.listeningMode.name")
    if listening_mode not in LISTENING_MODES:
        raise ValueError("brief.listeningMode.name must be road-book or focused-study")
    require_string(listening.get("primaryContext"), "brief.listeningMode.primaryContext")
    require_string_list(
        listening.get("attentionConstraints"),
        "brief.listeningMode.attentionConstraints",
    )

    revision = brief.get("revisionMode")
    if not isinstance(revision, dict):
        raise ValueError("brief.revisionMode must be an object")
    revision_mode = require_string(revision.get("name"), "brief.revisionMode.name")
    if revision_mode not in REVISION_MODES:
        raise ValueError("brief.revisionMode.name must be new-book or first-edition-plus")
    preserve = revision.get("preserve")
    if not isinstance(preserve, dict):
        raise ValueError("brief.revisionMode.preserve must be an object")
    # A run must state whether an earlier edition exists. Reaching new-book by
    # saying nothing is the failure this gate exists to prevent, so omission is
    # an error rather than a false default.
    if "priorEditionExists" not in revision:
        raise ValueError(
            "brief.revisionMode.priorEditionExists is required; new-book may not be "
            "reached by omitting any statement about a prior edition"
        )
    prior_edition_exists = require_bool(
        revision.get("priorEditionExists"), "brief.revisionMode.priorEditionExists"
    )
    if revision_mode == "first-edition-plus" and not prior_edition_exists:
        raise ValueError(
            "brief.revisionMode.priorEditionExists must be true for first-edition-plus"
        )
    # The prior edition is a fact about the subject; the mode is a deliberate
    # choice about it. When an earlier edition exists, new-book must document the
    # carryovers and non-carryovers exactly as first-edition-plus does.
    if prior_edition_exists:
        require_string(revision.get("sourceEdition"), "brief.revisionMode.sourceEdition")
        for field in ("governingQuestion", "narrativeSpine"):
            require_string(preserve.get(field), f"brief.revisionMode.preserve.{field}")
        for field in ("successfulExamples", "chapterJobs"):
            require_string_list(preserve.get(field), f"brief.revisionMode.preserve.{field}")

    orientation = brief.get("openingOrientation")
    if not isinstance(orientation, dict):
        raise ValueError("brief.openingOrientation must be an object")
    for field in ("context", "promise", "route"):
        require_string(orientation.get(field), f"brief.openingOrientation.{field}")
    production_mode, decisions_path, publication_authorization = (
        validate_production_mode(brief, run_root)
    )
    return {
        "audienceLevel": audience_level,
        "listeningMode": listening_mode,
        "productionMode": production_mode,
        "decisionsPath": decisions_path,
        "publicationAuthorization": publication_authorization,
    }


def validate_target(brief: dict[str, Any], actual_words: int) -> dict[str, int]:
    original = require_positive_int(brief.get("originalTargetWords"), "brief.originalTargetWords")
    current = require_positive_int(brief.get("currentTargetWords"), "brief.currentTargetWords")
    minimum = require_positive_int(brief.get("estimatedMinimumWords"), "brief.estimatedMinimumWords")
    maximum = require_positive_int(brief.get("estimatedMaximumWords"), "brief.estimatedMaximumWords")
    if minimum > maximum:
        raise ValueError("brief estimatedMinimumWords exceeds estimatedMaximumWords")
    if not minimum <= current <= maximum:
        raise ValueError("brief current target must fall inside its estimated word range")

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
    return {
        "originalTargetWords": original,
        "currentTargetWords": current,
        "estimatedMinimumWords": minimum,
        "estimatedMaximumWords": maximum,
        "actualWords": actual_words,
        "withinEstimatedRange": minimum <= actual_words <= maximum,
    }


def validate_outline(
    outline: dict[str, Any],
    chapter_names: set[str],
    listening_mode: str,
    evidence_claim_ids: set[str],
    production_mode: str,
) -> tuple[set[str], set[str]]:
    authorization = outline.get("authorization")
    if not isinstance(authorization, dict):
        raise ValueError("outline.authorization must be an object")
    if authorization.get("status") != "approved":
        raise ValueError("outline.authorization.status must be approved")
    authorization_source = authorization.get("source")
    if authorization_source not in AUTHORIZATION_SOURCES:
        raise ValueError("outline.authorization.source must be user or explicit-autonomous-run")
    if (
        listening_mode == "road-book"
        and authorization_source != "user"
        and production_mode != "unattended-first-listen"
    ):
        raise ValueError("road-book human outline approval requires authorization.source user")
    if (
        production_mode == "unattended-first-listen"
        and authorization_source != "explicit-autonomous-run"
    ):
        raise ValueError(
            "unattended first-listen outline requires explicit-autonomous-run authorization"
        )
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
            "end-to-end-trace, problem-progression, or question-led-narrative"
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
    durable_outcomes = require_string_list(
        outline.get("durableOutcomes"), "outline.durableOutcomes"
    )
    if listening_mode == "road-book" and not 6 <= len(durable_outcomes) <= 10:
        raise ValueError("outline.durableOutcomes must contain six to ten road-book outcomes")

    if listening_mode == "road-book":
        road_book = outline.get("roadBookDesign")
        if not isinstance(road_book, dict):
            raise ValueError("outline.roadBookDesign must be an object for road-book mode")
        for field in ("governingQuestion", "narrativeSpine", "optionalStudyBoundary"):
            require_string(road_book.get(field), f"outline.roadBookDesign.{field}")
        people = require_string_list(
            road_book.get("peopleAndHistory"), "outline.roadBookDesign.peopleAndHistory"
        )
        if len(people) < 2:
            raise ValueError("outline.roadBookDesign.peopleAndHistory needs at least two anchors")
        jobs = require_string_list(
            road_book.get("chapterJobVariety"), "outline.roadBookDesign.chapterJobVariety"
        )
        if len(set(jobs)) < 4:
            raise ValueError("outline.roadBookDesign.chapterJobVariety needs four distinct jobs")
        applications = require_string_list(
            road_book.get("realWorldApplications"),
            "outline.roadBookDesign.realWorldApplications",
        )
        if len(applications) < 2:
            raise ValueError(
                "outline.roadBookDesign.realWorldApplications needs at least two varied applications"
            )
        reference_layer = outline.get("referenceLayer")
        if not isinstance(reference_layer, dict):
            raise ValueError("outline.referenceLayer must be an object for road-book mode")
        require_string_list(reference_layer.get("items"), "outline.referenceLayer.items")
        require_string_list(reference_layer.get("formats"), "outline.referenceLayer.formats")

    chapters = unique_records(outline.get("chapters"), "file", "outline.chapters")
    if set(chapters) != chapter_names:
        raise ValueError("outline chapters must match canonical chapter files exactly")
    section_ids: set[str] = set()
    for filename, chapter in chapters.items():
        require_string(chapter.get("purpose"), f"outline.chapters[{filename}].purpose")
        require_string_list(
            chapter.get("prerequisites"),
            f"outline.chapters[{filename}].prerequisites",
            allow_empty=True,
        )
        sections = unique_records(
            chapter.get("sections"),
            "id",
            f"outline.chapters[{filename}].sections",
        )
        overlap = section_ids.intersection(sections)
        if overlap:
            raise ValueError(f"duplicate outline section id: {sorted(overlap)[0]}")
        section_ids.update(sections)
        for section_id, section in sections.items():
            prefix = f"outline.sections[{section_id}]"
            for field in (
                "job",
                "argument",
                "throughlineAdvance",
                "payoff",
                "landingBeat",
            ):
                require_string(section.get(field), f"{prefix}.{field}")
            claims = set(
                require_string_list(section.get("specificClaims"), f"{prefix}.specificClaims")
            )
            unknown_claims = claims - evidence_claim_ids
            if unknown_claims:
                raise ValueError(
                    f"{prefix}.specificClaims names unknown evidence id {sorted(unknown_claims)[0]}"
                )
            require_string_list(
                section.get("mustNotRepeat"),
                f"{prefix}.mustNotRepeat",
                allow_empty=True,
            )
    return set(durable_outcomes), section_ids


def validate_chapter_plans(
    plans: dict[str, Any], chapter_names: set[str], listening_mode: str
) -> None:
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

        terms = require_list(plan.get("newCoreTerms"), f"{prefix}.newCoreTerms", allow_empty=True)
        if listening_mode == "road-book" and len(terms) > 3:
            raise ValueError(f"{prefix}.newCoreTerms may contain at most three road-book terms")
        for index, term in enumerate(terms):
            if not isinstance(term, dict):
                raise ValueError(f"{prefix}.newCoreTerms[{index}] must be an object")
            require_string(term.get("term"), f"{prefix}.newCoreTerms[{index}].term")
            require_string(
                term.get("problemBeforeName"),
                f"{prefix}.newCoreTerms[{index}].problemBeforeName",
            )

        audio = plan.get("audioLoad")
        if not isinstance(audio, dict):
            raise ValueError(f"{prefix}.audioLoad must be an object")
        temporary_values = require_nonnegative_int(
            audio.get("temporaryValues"), f"{prefix}.audioLoad.temporaryValues"
        )
        symbolic_steps = require_nonnegative_int(
            audio.get("symbolicChainSteps"), f"{prefix}.audioLoad.symbolicChainSteps"
        )
        treatment = require_string(
            audio.get("calculationTreatment"), f"{prefix}.audioLoad.calculationTreatment"
        )
        if treatment not in CALCULATION_TREATMENTS:
            raise ValueError(f"{prefix}.audioLoad.calculationTreatment is unsupported")
        minutes = require_nonnegative_int(
            audio.get("focusedLessonMinutes"), f"{prefix}.audioLoad.focusedLessonMinutes"
        )
        require_string(audio.get("concreteReset"), f"{prefix}.audioLoad.concreteReset")

        if treatment in {"none", "optional-study"}:
            if temporary_values:
                raise ValueError(
                    f"{prefix}.audioLoad.temporaryValues must be zero when calculations are not in the main listen"
                )
            if symbolic_steps:
                raise ValueError(
                    f"{prefix}.audioLoad.symbolicChainSteps must be zero when calculations are not in the main listen"
                )
            if minutes:
                raise ValueError(f"{prefix}.audioLoad.focusedLessonMinutes must be zero")
        elif treatment == "brief-spoken":
            if temporary_values > 3:
                raise ValueError(
                    f"{prefix}.audioLoad.temporaryValues exceeds the road-book limit of three"
                )
            if symbolic_steps > 3:
                raise ValueError(
                    f"{prefix}.audioLoad.symbolicChainSteps exceeds the road-book limit of three"
                )
            if minutes:
                raise ValueError(f"{prefix}.audioLoad.focusedLessonMinutes must be zero")
        else:
            if not 1 <= minutes <= 5:
                raise ValueError(
                    f"{prefix}.audioLoad.focusedLessonMinutes must be one to five"
                )
            if temporary_values > 5:
                raise ValueError(f"{prefix}.audioLoad.temporaryValues exceeds focused-lesson limit")
            if symbolic_steps > 5:
                raise ValueError(f"{prefix}.audioLoad.symbolicChainSteps exceeds focused-lesson limit")

        if listening_mode == "road-book":
            infrastructure = plan.get("teachingInfrastructure")
            if not isinstance(infrastructure, dict):
                raise ValueError(f"{prefix}.teachingInfrastructure must be an object")
            require_string(
                infrastructure.get("narrativeConnection"),
                f"{prefix}.teachingInfrastructure.narrativeConnection",
            )
            require_string(
                infrastructure.get("realWorldApplication"),
                f"{prefix}.teachingInfrastructure.realWorldApplication",
            )


def validate_coverage(
    coverage: dict[str, Any], chapter_names: set[str], durable_outcomes: set[str]
) -> None:
    concepts = unique_records(coverage.get("concepts"), "name", "coverage-ledger.concepts")
    for name, concept in concepts.items():
        prefix = f"coverage-ledger[{name}]"
        durable_outcome = require_string(
            concept.get("durableOutcome"), f"{prefix}.durableOutcome"
        )
        if durable_outcome not in durable_outcomes:
            raise ValueError(f"{prefix}.durableOutcome must name an outline outcome")
        for field in (
            "definition",
            "reason",
            "mechanism",
            "concreteCase",
            "misconception",
            "expectedAbility",
        ):
            require_string(concept.get(field), f"{prefix}.{field}")
        require_string(concept.get("problemBeforeName"), f"{prefix}.problemBeforeName")
        require_string_list(
            concept.get("realWorldApplications"), f"{prefix}.realWorldApplications"
        )

        analogy = concept.get("analogy")
        analogy_reason = concept.get("analogyNotApplicableReason")
        if isinstance(analogy, dict) and analogy:
            for field in ("name", "relationship", "limit"):
                require_string(analogy.get(field), f"{prefix}.analogy.{field}")
            correspondence = require_string_list(
                analogy.get("correspondence"), f"{prefix}.analogy.correspondence"
            )
            if len(correspondence) < 2:
                raise ValueError(f"{prefix}.analogy.correspondence needs at least two mappings")
        elif not isinstance(analogy_reason, str) or not analogy_reason.strip():
            raise ValueError(f"{prefix} requires an analogy contract or analogyNotApplicableReason")
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

        retrievals = require_list(concept.get("retrievals"), f"{prefix}.retrievals")
        for index, retrieval in enumerate(retrievals):
            if not isinstance(retrieval, dict):
                raise ValueError(f"{prefix}.retrievals[{index}] must be an object")
            chapter = require_string(
                retrieval.get("chapter"), f"{prefix}.retrievals[{index}].chapter"
            )
            after_gap = require_string(
                retrieval.get("afterGapFrom"),
                f"{prefix}.retrievals[{index}].afterGapFrom",
            )
            if chapter not in chapter_names or after_gap not in chapter_names:
                raise ValueError(f"{prefix}.retrievals[{index}] names an unknown chapter")
            if chapter == after_gap:
                raise ValueError(f"{prefix}.retrievals[{index}] must occur after a chapter gap")
            for field in ("freshSituation", "listenerTask", "answerPlacement"):
                require_string(
                    retrieval.get(field), f"{prefix}.retrievals[{index}].{field}"
                )


def validate_continuity(
    continuity: dict[str, Any],
    chapter_names: set[str],
    section_ids: set[str],
    run_root: Path,
) -> None:
    draft_contexts = unique_records(
        continuity.get("draftContexts"), "section", "continuity.draftContexts"
    )
    covered_sections: set[str] = set()
    for context_id, context in draft_contexts.items():
        prefix = f"continuity.draftContexts[{context_id}]"
        for field in (
            "fullOutlinePath",
            "evidenceNotesPath",
            "styleGuidePath",
            "previousSectionTextOrSummary",
        ):
            require_string(context.get(field), f"{prefix}.{field}")
        require_string_list(
            context.get("mustNotRepeat"), f"{prefix}.mustNotRepeat", allow_empty=True
        )
        batch_sections = context.get("batchSections")
        if batch_sections is None:
            if context_id not in section_ids:
                raise ValueError(f"{prefix}.section names an unknown outline section")
            if context_id in covered_sections:
                raise ValueError(
                    f"{prefix}.section covers outline section {context_id} more than once"
                )
            require_string(context.get("sectionJob"), f"{prefix}.sectionJob")
            covered_sections.add(context_id)
            continue

        if not context_id.endswith("-batch"):
            raise ValueError(f"{prefix}.section must end in -batch")
        batch = require_string_list(batch_sections, f"{prefix}.batchSections")
        unknown_sections = sorted(set(batch) - section_ids)
        if unknown_sections:
            raise ValueError(
                f"{prefix}.batchSections names unknown outline section {unknown_sections[0]}"
            )
        if len(set(batch)) != len(batch):
            raise ValueError(f"{prefix}.batchSections covers a section more than once")
        already_covered = sorted(set(batch) & covered_sections)
        if already_covered:
            raise ValueError(
                f"{prefix}.batchSections covers outline section "
                f"{already_covered[0]} more than once"
            )
        chapter_prefix = context_id.removesuffix("-batch") + "-s"
        if any(not section.startswith(chapter_prefix) for section in batch):
            raise ValueError(f"{prefix}.batchSections must stay within one chapter")
        jobs = require_string_list(context.get("sectionJobs"), f"{prefix}.sectionJobs")
        if len(jobs) != len(batch):
            raise ValueError(f"{prefix}.sectionJobs must match batchSections one for one")
        authorization_value = require_string(
            context.get("fastTrackAuthorizationPath"),
            f"{prefix}.fastTrackAuthorizationPath",
        )
        authorization_relative = Path(authorization_value)
        if authorization_relative.is_absolute():
            raise ValueError(f"{prefix}.fastTrackAuthorizationPath must be relative")
        root = run_root.resolve()
        authorization = (root / authorization_relative).resolve()
        try:
            authorization.relative_to(root)
        except ValueError as error:
            raise ValueError(
                f"{prefix}.fastTrackAuthorizationPath must stay inside the run root"
            ) from error
        if not authorization.is_file():
            raise ValueError(f"{prefix}.fastTrackAuthorizationPath does not exist")
        covered_sections.update(batch)

    if covered_sections != section_ids:
        raise ValueError(
            "continuity.draftContexts must cover every argument-outline section"
        )

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
            "retrievalsCompleted",
        ):
            require_string_list(checkpoint.get(field), f"{prefix}.{field}", allow_empty=True)
        require_string(checkpoint.get("listenerLoadNotes"), f"{prefix}.listenerLoadNotes")
        require_string(checkpoint.get("priorSectionSummary"), f"{prefix}.priorSectionSummary")
        require_string_list(
            checkpoint.get("doNotRepeat"), f"{prefix}.doNotRepeat", allow_empty=True
        )


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
    for name in ("structure", "blindSequentialBeginner"):
        lane = review.get(name)
        if not isinstance(lane, dict):
            raise ValueError(f"review.{name} must be an object")
        reviewers.append(require_string(lane.get("reviewer"), f"review.{name}.reviewer"))
        if lane.get("verdict") != "pass":
            raise ValueError(f"review.{name}.verdict must be pass")
        validate_findings(lane.get("findings"), f"review.{name}.findings")
        if name == "blindSequentialBeginner":
            if lane.get("reviewMode") != "manuscript-only-sequential":
                raise ValueError(
                    "review.blindSequentialBeginner.reviewMode must be manuscript-only-sequential"
                )
            if lane.get("intentionMaterialsWithheld") is not True:
                raise ValueError(
                    "review.blindSequentialBeginner.intentionMaterialsWithheld must be true"
                )
            assessments = unique_records(
                lane.get("chapterAssessments"),
                "afterChapter",
                "review.blindSequentialBeginner.chapterAssessments",
            )
            if set(assessments) != set(hashes):
                raise ValueError(
                    "review.blindSequentialBeginner.chapterAssessments must cover every chapter"
                )
            for filename, assessment in assessments.items():
                prefix = f"review.blindSequentialBeginner.chapterAssessments[{filename}]"
                require_string(
                    assessment.get("plausibleMentalModel"),
                    f"{prefix}.plausibleMentalModel",
                )
                for field in ("confusions", "unstableTerms", "lostAt"):
                    require_string_list(
                        assessment.get(field), f"{prefix}.{field}", allow_empty=True
                    )
    if len(set(reviewers)) != len(reviewers):
        raise ValueError(
            "structure and blindSequentialBeginner reviews require independent reviewers"
        )


def validate_revision_passes(revisions: dict[str, Any], hashes: dict[str, str]) -> None:
    if revisions.get("reviewedChapterSHA256") != hashes:
        raise ValueError(
            "revision-passes.reviewedChapterSHA256 does not match final canonical chapters"
        )
    passes = unique_records(revisions.get("passes"), "name", "revision-passes.passes")
    missing = REQUIRED_REVISION_PASSES - set(passes)
    if missing:
        raise ValueError(
            f"revision-passes.passes is missing required pass: {sorted(missing)[0]}"
        )
    for name, revision_pass in passes.items():
        prefix = f"revision-passes[{name}]"
        require_string(revision_pass.get("job"), f"{prefix}.job")
        if revision_pass.get("scope") != "single-job":
            raise ValueError(f"{prefix}.scope must be single-job")
        require_string(revision_pass.get("reviewer"), f"{prefix}.reviewer")
        if revision_pass.get("status") != "pass":
            raise ValueError(f"{prefix}.status must be pass")
        validate_findings(revision_pass.get("findings"), f"{prefix}.findings")

    ear_pass = passes["ear-pass"]
    require_string(ear_pass.get("renderer"), "revision-passes[ear-pass].renderer")
    require_string(
        ear_pass.get("listeningContext"),
        "revision-passes[ear-pass].listeningContext",
    )
    require_string_list(
        ear_pass.get("stumbles"), "revision-passes[ear-pass].stumbles", allow_empty=True
    )
    require_string_list(
        ear_pass.get("lostThreadAt"),
        "revision-passes[ear-pass].lostThreadAt",
        allow_empty=True,
    )


def validate_pilot(
    pilot: dict[str, Any], run_root: Path, production_mode: str
) -> str:
    unattended = production_mode == "unattended-first-listen"
    status = pilot.get("status")
    if unattended:
        if status != "first-listen":
            raise ValueError("pilot.status must be first-listen before full drafting")
    elif status not in {"accepted", "waived-by-listener"}:
        raise ValueError(
            "pilot.status must be accepted or waived-by-listener before full drafting"
        )
    require_string(pilot.get("listener"), "pilot.listener")
    require_string(pilot.get("listeningContext"), "pilot.listeningContext")
    minutes = require_positive_int(
        pilot.get("representativeMinutes"), "pilot.representativeMinutes"
    )
    if not 10 <= minutes <= 15:
        raise ValueError("pilot.representativeMinutes must be between 10 and 15")
    if pilot.get("includesFirstTechnicalPassage") is not True:
        raise ValueError("pilot.includesFirstTechnicalPassage must be true")
    # The EPUB is a text artifact. Requiring a rendered pilot before it can be
    # built made every text package depend on a full Echo Release build and a
    # speech synthesis run. A pilot may therefore declare itself not-rendered;
    # when it claims audio, the claim is still checked exactly as before.
    if pilot.get("audioRendered") is False:
        if pilot.get("audioPath") not in (None, ""):
            raise ValueError("pilot.audioPath must be empty when audioRendered is false")
        if pilot.get("audioSHA256") not in (None, ""):
            raise ValueError("pilot.audioSHA256 must be empty when audioRendered is false")
        require_string(pilot.get("audioNotRenderedReason"), "pilot.audioNotRenderedReason")
    else:
        require_string(pilot.get("audioPath"), "pilot.audioPath")
        audio_hash = require_string(pilot.get("audioSHA256"), "pilot.audioSHA256")
        if not SHA256_RE.fullmatch(audio_hash):
            raise ValueError("pilot.audioSHA256 must be a lowercase SHA-256 digest")
    listener_notes = pilot.get("listenerNotes")
    if listener_notes is not None and not isinstance(listener_notes, str):
        raise ValueError("pilot.listenerNotes must be a string when present")
    if status == "waived-by-listener":
        evidence = pilot.get("comprehensionEvidence")
        if not isinstance(evidence, dict):
            raise ValueError(
                "pilot.comprehensionEvidence must be an object for a listener waiver"
            )
        if evidence.get("status") != "not-collected-listener-waived":
            raise ValueError(
                "pilot.comprehensionEvidence.status must be "
                "not-collected-listener-waived"
            )
        for field in ("waivedBy", "waivedAt", "reason"):
            require_string(evidence.get(field), f"pilot.comprehensionEvidence.{field}")
        require_string(pilot.get("validationBoundary"), "pilot.validationBoundary")
    checkpoint_key = "editorialCheckpoints" if unattended else "humanCheckpoints"
    checkpoint_label = f"pilot.{checkpoint_key}"
    checkpoints = pilot.get(checkpoint_key)
    if not isinstance(checkpoints, dict):
        raise ValueError(f"{checkpoint_label} must be an object")

    voice_source = checkpoints.get("voiceSource")
    if not isinstance(voice_source, dict):
        raise ValueError(f"{checkpoint_label}.voiceSource must be an object")
    mode = require_string(
        voice_source.get("mode"), f"{checkpoint_label}.voiceSource.mode"
    )
    if mode not in VOICE_SOURCE_MODES:
        raise ValueError(f"{checkpoint_label}.voiceSource.mode is unsupported")
    validate_bound_artifact(
        run_root,
        voice_source.get("profilePath"),
        voice_source.get("profileSHA256"),
        f"{checkpoint_label}.voiceSource.profile",
    )
    if voice_source.get("useBoundary") != "craft-features-not-pastiche":
        raise ValueError(
            f"{checkpoint_label}.voiceSource.useBoundary must be craft-features-not-pastiche"
        )
    if voice_source.get("rawSourceExcerptsCommitted") is not False:
        raise ValueError(
            f"{checkpoint_label}.voiceSource.rawSourceExcerptsCommitted must be false"
        )

    outline_checkpoint = checkpoints.get("outline")
    if not isinstance(outline_checkpoint, dict):
        raise ValueError(f"{checkpoint_label}.outline must be an object")
    outline_status = "editorially-approved" if unattended else "approved"
    if outline_checkpoint.get("status") != outline_status:
        raise ValueError(f"{checkpoint_label}.outline.status must be {outline_status}")
    for field in ("reviewer", "evidence"):
        require_string(
            outline_checkpoint.get(field), f"{checkpoint_label}.outline.{field}"
        )
    if outline_checkpoint.get("recordedBeforePilotDraft") is not True:
        raise ValueError(
            f"{checkpoint_label}.outline.recordedBeforePilotDraft must be true"
        )

    first_section = checkpoints.get("firstSection")
    if not isinstance(first_section, dict):
        raise ValueError(f"{checkpoint_label}.firstSection must be an object")
    section_status = "editorially-accepted" if unattended else "accepted"
    if first_section.get("status") != section_status:
        raise ValueError(f"{checkpoint_label}.firstSection.status must be {section_status}")
    for field in ("reviewer", "evidence"):
        require_string(
            first_section.get(field), f"{checkpoint_label}.firstSection.{field}"
        )
    if first_section.get("recordedBeforeRemainingDraft") is not True:
        raise ValueError(
            f"{checkpoint_label}.firstSection.recordedBeforeRemainingDraft must be true"
        )
    validate_bound_artifact(
        run_root,
        first_section.get("voiceExemplarPath"),
        first_section.get("voiceExemplarSHA256"),
        f"{checkpoint_label}.firstSection.voiceExemplar",
    )

    decision = pilot.get("decision")
    if not isinstance(decision, dict):
        raise ValueError("pilot.decision must be an object")
    if decision.get("verdict") != "continue":
        raise ValueError("pilot.decision.verdict must be continue")
    decision_authority = "editorial-review" if unattended else "listener"
    if decision.get("authority") != decision_authority:
        raise ValueError(f"pilot.decision.authority must be {decision_authority}")
    require_string(decision.get("evidence"), "pilot.decision.evidence")
    if decision.get("recordedBeforeFullDraft") is not True:
        raise ValueError("pilot.decision.recordedBeforeFullDraft must be true")
    return status


def validate_run(run_root: Path) -> dict[str, Any]:
    run_root = Path(run_root)
    chapters_dir = run_root / "chapters"
    research_dir = run_root / "research"
    paths = {name: research_dir / filename for name, filename in REQUIRED_RECORDS.items()}
    records = {name: load_record(path, name) for name, path in paths.items()}
    hashes = chapter_hashes(chapters_dir)
    names = set(hashes)
    actual_words = manuscript_word_count(chapters_dir)

    evidence_claim_ids = validate_evidence(records["evidence"], run_root)
    brief = validate_brief(records["brief"], run_root)
    word_count = validate_target(records["brief"], actual_words)
    durable_outcomes, section_ids = validate_outline(
        records["outline"],
        names,
        brief["listeningMode"],
        evidence_claim_ids,
        brief["productionMode"],
    )
    validate_chapter_plans(records["plans"], names, brief["listeningMode"])
    validate_coverage(records["coverage"], names, durable_outcomes)
    validate_continuity(records["continuity"], names, section_ids, run_root)
    pilot_status = validate_pilot(records["pilot"], run_root, brief["productionMode"])
    validate_revision_passes(records["revisions"], hashes)
    validate_review(records["review"], hashes)

    unattended = brief["productionMode"] == "unattended-first-listen"
    listener_waiver = pilot_status == "waived-by-listener"
    record_paths = dict(paths)
    if brief["decisionsPath"] is not None:
        record_paths["unattendedDecisions"] = brief["decisionsPath"]
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": (
            "first-listen"
            if unattended
            else "pass-with-listener-waiver" if listener_waiver else "pass"
        ),
        "productionMode": brief["productionMode"],
        **(
            {"publicationAuthorization": brief["publicationAuthorization"]}
            if brief["publicationAuthorization"] is not None
            else {}
        ),
        "chapterSHA256": hashes,
        "recordSHA256": {
            name: sha256_file(path) for name, path in record_paths.items()
        },
        "wordCount": word_count,
        "gates": {
            "learnerOrientation": "pass",
            "groundedEvidence": "pass",
            "outlineAuthorization": "pass",
            "argumentLevelOutline": "pass",
            "chapterTeachingPlans": "pass",
            "conceptBudget": "pass",
            "audioWorkingMemory": "pass",
            "problemBeforeName": "pass",
            "realWorldGrounding": "pass",
            "analogyContract": "pass",
            "retrieval": "pass",
            "explanationPaths": "pass",
            "continuity": "pass",
            "sectionDraftContexts": "pass",
            "voiceCalibration": "pass",
            "narrowRevisionPasses": "pass",
            "earPass": "pass",
            "structuralReview": "pass",
            "blindSequentialBeginnerReview": "pass",
            "humanComprehensionPilot": (
                "pending"
                if unattended
                else "waived-by-listener" if listener_waiver else "pass"
            ),
        },
        "learningAuthority": {
            "holder": "human-listener-pending" if unattended else "human-listener",
            "negativeVerdictOverridesReceipt": True,
            "receiptDoesNotCertifyTransfer": True,
            **(
                {
                    "comprehensionEvidenceStatus": "not-collected-listener-waived",
                    "listenerWaiverDoesNotCertifyComprehension": True,
                }
                if listener_waiver
                else {}
            ),
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
    status = receipt.get("status")
    if status not in {"pass", "pass-with-listener-waiver", "first-listen"}:
        raise ValueError(
            "learning-design receipt status must be pass, "
            "pass-with-listener-waiver, or first-listen"
        )
    expected = chapter_hashes(Path(chapters_dir))
    if receipt.get("chapterSHA256") != expected:
        raise ValueError("learning-design receipt chapter hash mismatch")
    gates = receipt.get("gates")
    if not isinstance(gates, dict) or not gates:
        raise ValueError("learning-design receipt contains invalid gates")
    production_mode = receipt.get("productionMode", "governed-final")
    if status == "pass":
        if production_mode != "governed-final" or any(
            value != "pass" for value in gates.values()
        ):
            raise ValueError("governed-final learning receipt contains a non-passing gate")
        expected_holder = "human-listener"
    elif status == "pass-with-listener-waiver":
        if production_mode != "governed-final":
            raise ValueError("listener-waiver receipt requires governed-final mode")
        for name, value in gates.items():
            expected = "waived-by-listener" if name == "humanComprehensionPilot" else "pass"
            if value != expected:
                raise ValueError(f"listener-waiver {name} gate must be {expected}")
        if "humanComprehensionPilot" not in gates:
            raise ValueError("listener-waiver receipt is missing humanComprehensionPilot")
        expected_holder = "human-listener"
    else:
        if production_mode != "unattended-first-listen":
            raise ValueError("first-listen receipt requires unattended-first-listen mode")
        for name, value in gates.items():
            expected = "pending" if name == "humanComprehensionPilot" else "pass"
            if value != expected:
                raise ValueError(
                    f"first-listen {name} gate must be {expected}"
                )
        if "humanComprehensionPilot" not in gates:
            raise ValueError("first-listen receipt is missing humanComprehensionPilot")
        expected_holder = "human-listener-pending"
    authority = receipt.get("learningAuthority")
    if not isinstance(authority, dict):
        raise ValueError("learning-design receipt is missing learningAuthority")
    if authority.get("holder") != expected_holder:
        raise ValueError(f"learning-design receipt holder must be {expected_holder}")
    if authority.get("negativeVerdictOverridesReceipt") is not True:
        raise ValueError("learning-design receipt must preserve negative listener authority")
    if authority.get("receiptDoesNotCertifyTransfer") is not True:
        raise ValueError("learning-design receipt must not claim to certify learning transfer")
    if status == "pass-with-listener-waiver":
        if (
            authority.get("comprehensionEvidenceStatus")
            != "not-collected-listener-waived"
        ):
            raise ValueError(
                "listener-waiver receipt must record uncollected comprehension evidence"
            )
        if authority.get("listenerWaiverDoesNotCertifyComprehension") is not True:
            raise ValueError(
                "listener-waiver receipt must not claim to certify comprehension"
            )
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate audiobook learning design and bind it to final chapters."
    )
    parser.add_argument("--run-root", required=True, type=Path)
    parser.add_argument("--receipt-out", required=True, type=Path)
    args = parser.parse_args()
    receipt = write_receipt(args.run_root, args.receipt_out)
    print(f"learning design process: {receipt['status']}")
    print(f"receipt: {args.receipt_out}")


if __name__ == "__main__":
    main()
