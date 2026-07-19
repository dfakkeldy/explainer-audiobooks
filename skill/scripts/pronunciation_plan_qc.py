#!/usr/bin/env python3
"""Validate planned technical pronunciations before a governed full render."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from fiction_production_qc import verify_fiction_receipt


SCHEMA_VERSION = 1
PHASES = {"planning", "full-render"}
SOURCES = {"listener", "coverage-ledger", "author"}
STATUSES = {"planned", "probed", "accepted", "waived-by-listener"}
ASSURANCE_LEVELS = {"governed-final", "unattended-first-listen"}


def sha256_file(path: Path) -> str:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"missing {label}: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"invalid {label}: {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def normalized(value: str) -> str:
    return value.strip().casefold()


def contains_form(text: str, form: str) -> bool:
    pattern = rf"(?<![\w]){re.escape(form)}(?![\w])"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def chapter_hashes(chapters_dir: Path) -> dict[str, str]:
    chapters = sorted(chapters_dir.glob("ch*.md"))
    if not chapters:
        raise ValueError(f"no canonical chapter files found in {chapters_dir}")
    return {path.name: sha256_file(path) for path in chapters}


def resolved_run_file(run_root: Path, relative: str, label: str) -> Path:
    candidate = (run_root / relative).resolve()
    root = run_root.resolve()
    if not candidate.is_relative_to(root):
        raise ValueError(f"{label} must stay inside the run root")
    if not candidate.is_file():
        raise ValueError(f"{label} is missing: {candidate}")
    return candidate


def validate_plan(run_root: Path, phase: str) -> dict[str, object]:
    run_root = run_root.resolve()
    if phase not in PHASES:
        raise ValueError(f"phase must be one of {sorted(PHASES)}")
    plan_path = run_root / "research" / "pronunciation-plan.json"
    plan = load_json(plan_path, "pronunciation plan")
    if plan.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError(f"pronunciation plan schemaVersion must be {SCHEMA_VERSION}")
    assurance_level = plan.get("assuranceLevel", "governed-final")
    if assurance_level not in ASSURANCE_LEVELS:
        raise ValueError(
            "pronunciation plan assuranceLevel must be governed-final or "
            "unattended-first-listen"
        )
    terms = plan.get("terms")
    if not isinstance(terms, list) or not terms:
        raise ValueError("pronunciation plan terms must be a non-empty list")

    chapters_dir = run_root / "chapters"
    if phase == "planning":
        fiction_receipt_path = run_root / "research" / "fiction-production-receipt.json"
        if fiction_receipt_path.is_file():
            fiction_receipt = verify_fiction_receipt(chapters_dir, fiction_receipt_path)
            chapter_names = set(fiction_receipt["canonicalChapterSHA256"])
        else:
            outline = load_json(
                run_root / "research" / "learning-outline.json", "learning outline"
            )
            outline_chapters = outline.get("chapters")
            if not isinstance(outline_chapters, list) or not outline_chapters:
                raise ValueError("learning outline chapters must be a non-empty list")
            chapter_names = set()
            for index, chapter in enumerate(outline_chapters):
                if not isinstance(chapter, dict):
                    raise ValueError(f"learning outline chapters[{index}] must be an object")
                name = require_string(chapter.get("file"), f"learning outline chapters[{index}].file")
                if name in chapter_names:
                    raise ValueError(f"duplicate learning outline chapter: {name}")
                chapter_names.add(name)
        hashes: dict[str, str] = {}
        chapter_text: dict[str, str] = {}
    else:
        hashes = chapter_hashes(chapters_dir)
        chapter_names = set(hashes)
        chapter_text = {
            name: (chapters_dir / name).read_text(encoding="utf-8") for name in hashes
        }
    seen: set[str] = set()
    required_terms: list[str] = []
    waived_terms: list[str] = []
    evidence_paths: set[Path] = set()
    evidence_reel_paths: set[Path] = set()

    for index, entry in enumerate(terms):
        label = f"terms[{index}]"
        if not isinstance(entry, dict):
            raise ValueError(f"{label} must be an object")
        term = require_string(entry.get("term"), f"{label}.term")
        identity = normalized(term)
        if identity in seen:
            raise ValueError(f"duplicate pronunciation term: {term}")
        seen.add(identity)
        variants = entry.get("variants")
        if not isinstance(variants, list):
            raise ValueError(f"{label}.variants must be a list")
        forms = [term]
        for variant_index, variant in enumerate(variants):
            forms.append(require_string(variant, f"{label}.variants[{variant_index}]"))
        normalized_forms = [normalized(form) for form in forms]
        if len(set(normalized_forms)) != len(normalized_forms):
            raise ValueError(f"{label} contains a duplicate term or variant")
        if entry.get("source") not in SOURCES:
            raise ValueError(f"{label}.source must be listener, coverage-ledger, or author")
        require_string(entry.get("reason"), f"{label}.reason")
        expected = entry.get("expectedChapters")
        if not isinstance(expected, list) or not expected:
            raise ValueError(f"{label}.expectedChapters must be a non-empty list")
        expected_names = [
            require_string(name, f"{label}.expectedChapters[{position}]")
            for position, name in enumerate(expected)
        ]
        for name in expected_names:
            if name not in chapter_names:
                raise ValueError(f"{label} names unknown expected chapter {name}")
        if phase == "full-render":
            combined = "\n".join(chapter_text[name] for name in expected_names)
            missing_source_forms = [form for form in forms if not contains_form(combined, form)]
            if missing_source_forms:
                raise ValueError(
                    f"{label} forms are absent from expected chapters: {missing_source_forms}"
                )
        if not isinstance(entry.get("required"), bool):
            raise ValueError(f"{label}.required must be a boolean")
        status = entry.get("status")
        if status not in STATUSES:
            raise ValueError(
                f"{label}.status must be planned, probed, accepted, "
                "or waived-by-listener"
            )
        if entry["required"]:
            required_terms.append(term)

        if phase == "full-render" and entry["required"]:
            decision = entry.get("decision")
            evidence = entry.get("evidence")
            if assurance_level == "governed-final":
                if status not in {"accepted", "waived-by-listener"} \
                    or not isinstance(decision, dict) \
                    or not isinstance(evidence, dict):
                    raise ValueError(
                        f"{label} requires accepted human evidence or an explicit "
                        "listener waiver before full render"
                    )
                if status == "accepted":
                    require_string(
                        decision.get("acceptedBy"), f"{label}.decision.acceptedBy"
                    )
                    require_string(
                        decision.get("acceptedAt"), f"{label}.decision.acceptedAt"
                    )
                else:
                    for field in ("waivedBy", "waivedAt", "reason", "validationBoundary"):
                        require_string(decision.get(field), f"{label}.decision.{field}")
                    waived_terms.append(term)
            else:
                if status != "probed" or decision is not None or not isinstance(evidence, dict):
                    raise ValueError(
                        f"{label} requires probed evidence without a fabricated human "
                        "decision for unattended first-listen"
                    )
            relative_path = require_string(evidence.get("path"), f"{label}.evidence.path")
            evidence_path = resolved_run_file(run_root, relative_path, f"{label}.evidence.path")
            expected_sha = require_string(evidence.get("sha256"), f"{label}.evidence.sha256")
            actual_sha = sha256_file(evidence_path)
            if expected_sha != actual_sha:
                raise ValueError(f"{label} evidence SHA-256 does not match {evidence_path}")
            evidence_paths.add(evidence_path)
            evidence_payload = load_json(evidence_path, f"{label} pronunciation evidence")
            if evidence_payload.get("schemaVersion") != SCHEMA_VERSION:
                raise ValueError(
                    f"{label} pronunciation evidence schemaVersion must be {SCHEMA_VERSION}"
                )
            reel_name = require_string(
                evidence_payload.get("reelFileName"),
                f"{label} pronunciation evidence reelFileName",
            )
            if Path(reel_name).name != reel_name:
                raise ValueError(f"{label} pronunciation evidence reelFileName must be a basename")
            reel_path = (evidence_path.parent / reel_name).resolve()
            if not reel_path.is_relative_to(run_root) or not reel_path.is_file():
                raise ValueError(f"{label} pronunciation evidence reel is missing: {reel_path}")
            expected_reel_sha = require_string(
                evidence_payload.get("reelSHA256"),
                f"{label} pronunciation evidence reelSHA256",
            )
            if sha256_file(reel_path) != expected_reel_sha:
                raise ValueError(f"{label} pronunciation reel SHA-256 does not match {reel_path}")
            evidence_reel_paths.add(reel_path)
            clips = evidence_payload.get("clips")
            if not isinstance(clips, list):
                raise ValueError(f"{label} pronunciation evidence clips must be a list")
            heard = {
                normalized(clip.get("variantHeard", ""))
                for clip in clips
                if isinstance(clip, dict) and normalized(str(clip.get("term", ""))) == identity
            }
            missing_heard = sorted(set(normalized_forms) - heard)
            if missing_heard:
                raise ValueError(f"{label} missing heard variants: {missing_heard}")

    if phase == "full-render" and len(evidence_paths) != 1:
        raise ValueError("required pronunciation terms must share one governed reel evidence file")
    if phase == "full-render" and len(evidence_reel_paths) != 1:
        raise ValueError("required pronunciation terms must share one governed pronunciation reel")

    result: dict[str, object] = {
        "schemaVersion": SCHEMA_VERSION,
        "phase": phase,
        "assuranceLevel": assurance_level,
        "humanListening": (
            "pending"
            if assurance_level == "unattended-first-listen"
            else "not-collected-listener-waived" if waived_terms else "accepted"
        ),
        "planSHA256": sha256_file(plan_path),
        "chapterSHA256": hashes,
        "plannedChapters": sorted(chapter_names),
        "requiredTerms": required_terms,
    }
    if waived_terms:
        result["waivedTerms"] = waived_terms
        result["listeningAuthority"] = {
            "holder": "human-listener",
            "evidenceStatus": "not-collected-listener-waived",
            "waiverDoesNotCertifyPronunciation": True,
            "negativeVerdictOverridesReceipt": True,
        }
    if evidence_paths:
        evidence_path = next(iter(evidence_paths))
        result["evidencePath"] = str(evidence_path.relative_to(run_root))
        result["evidenceSHA256"] = sha256_file(evidence_path)
        reel_path = next(iter(evidence_reel_paths))
        result["reelPath"] = str(reel_path.relative_to(run_root))
        result["reelSHA256"] = sha256_file(reel_path)
    return result


def write_receipt(run_root: Path, out: Path) -> dict[str, object]:
    result = validate_plan(run_root, "full-render")
    receipt = {
        **result,
        "status": (
            "first-listen"
            if result["assuranceLevel"] == "unattended-first-listen"
            else "pass-with-listener-waiver" if result.get("waivedTerms") else "pass"
        ),
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    temporary = out.with_suffix(out.suffix + ".tmp")
    temporary.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(out)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--phase", choices=sorted(PHASES), required=True)
    parser.add_argument("--receipt-out", type=Path)
    args = parser.parse_args()
    if args.receipt_out is not None:
        if args.phase != "full-render":
            parser.error("--receipt-out requires --phase full-render")
        result = write_receipt(args.run_root, args.receipt_out)
    else:
        result = validate_plan(args.run_root, args.phase)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
