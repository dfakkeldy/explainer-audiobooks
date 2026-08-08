#!/usr/bin/env python3
"""Verify a private first-listen fiction production receipt."""

from __future__ import annotations

import json
import hashlib
import os
import re
import tempfile
from pathlib import Path
from typing import Any


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REQUIRED_ARTIFACTS = {
    "authorization",
    "storyBible",
    "continuity",
    "revisionReview",
    "proseQC",
}
REQUIRED_GATES = {
    "manuscriptClosed",
    "storyBibleReconciled",
    "continuityReconciled",
    "revisionPassesCompleted",
    "proseQCPassed",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _verified_relative_artifact(
    run_root: Path, record: object, label: str
) -> tuple[Path, str]:
    if not isinstance(record, dict) or set(record) != {"path", "sha256"}:
        raise ValueError(f"{label} must contain exactly path and sha256")
    relative = Path(str(record.get("path", "")))
    if relative.is_absolute():
        raise ValueError(f"{label} path must be relative to the run root")
    artifact = (run_root / relative).resolve()
    try:
        artifact.relative_to(run_root)
    except ValueError as error:
        raise ValueError(f"{label} escapes the run root") from error
    expected = record.get("sha256")
    if not artifact.is_file():
        raise ValueError(f"missing {label}: {artifact}")
    if not isinstance(expected, str) or not SHA256_RE.fullmatch(expected):
        raise ValueError(f"{label} has an invalid SHA-256")
    if _sha256(artifact) != expected:
        raise ValueError(f"{label} hash mismatch")
    return artifact, expected


def verify_fiction_receipt(
    chapters_dir: Path,
    receipt_path: Path,
    *,
    verify_build_outputs: bool = True,
) -> dict[str, Any]:
    try:
        receipt = json.loads(Path(receipt_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"invalid fiction production receipt: {receipt_path}: {error}") from error
    if not isinstance(receipt, dict):
        raise ValueError("fiction production receipt must be an object")
    if type(receipt.get("schemaVersion")) is not int or receipt["schemaVersion"] != 1:
        raise ValueError("fiction production receipt schemaVersion must be 1")
    if receipt.get("status") != "first-listen":
        raise ValueError("fiction production receipt status must be first-listen")
    if receipt.get("productionMode") != "unattended-first-listen":
        raise ValueError(
            "fiction production receipt productionMode must be unattended-first-listen"
        )
    if receipt.get("privacy") != "private":
        raise ValueError("private first-listen fiction receipt privacy must be private")
    actual = {
        chapter.name: _sha256(chapter)
        for chapter in sorted(Path(chapters_dir).glob("ch*.md"))
    }
    if receipt.get("canonicalChapterSHA256") != actual:
        raise ValueError("fiction production receipt chapter hash mismatch")
    if receipt.get("permissionToPublish") is not False:
        raise ValueError("private first-listen fiction receipt cannot grant publication")
    if receipt.get("humanReadingStatus") != "pending":
        raise ValueError("private first-listen fiction receipt humanReadingStatus must be pending")
    if receipt.get("negativeHumanVerdictOverrides") is not True:
        raise ValueError("fiction production receipt must preserve negative human authority")
    if receipt.get("receiptDoesNotCertifyHumanAcceptance") is not True:
        raise ValueError("fiction production receipt must not certify human acceptance")
    artifacts = receipt.get("artifacts")
    if not isinstance(artifacts, dict):
        raise ValueError("fiction production receipt artifacts must be an object")
    missing = sorted(REQUIRED_ARTIFACTS - artifacts.keys())
    if missing:
        raise ValueError("fiction production receipt missing artifact: " + missing[0])
    run_root = Path(receipt_path).parent.parent.resolve()
    for name, record in artifacts.items():
        _verified_relative_artifact(
            run_root, record, f"fiction production artifact {name}"
        )
    gates = receipt.get("gates")
    if not isinstance(gates, dict):
        raise ValueError("fiction production receipt gates must be an object")
    for name in sorted(REQUIRED_GATES):
        if gates.get(name) != "pass":
            raise ValueError(f"fiction production gate {name} must be pass")
    build_outputs = receipt.get("buildOutputs")
    if build_outputs is not None and verify_build_outputs:
        if not isinstance(build_outputs, dict) or set(build_outputs) != {
            "slug",
            "manuscript",
            "epub",
        }:
            raise ValueError(
                "fiction buildOutputs must contain exactly slug, manuscript, and epub"
            )
        slug = build_outputs.get("slug")
        if not isinstance(slug, str) or not slug:
            raise ValueError("fiction buildOutputs slug must be non-empty text")
        _verified_relative_artifact(
            run_root, build_outputs.get("manuscript"), "fiction build manuscript"
        )
        _verified_relative_artifact(
            run_root, build_outputs.get("epub"), "fiction build EPUB"
        )
    return receipt


def record_fiction_build_outputs(
    chapters_dir: Path,
    receipt_path: Path,
    output_dir: Path,
    slug: str,
) -> dict[str, Any]:
    """Atomically bind builder-created Markdown and EPUB to a fiction receipt."""
    receipt_path = Path(receipt_path)
    output_dir = Path(output_dir)
    receipt = verify_fiction_receipt(
        Path(chapters_dir), receipt_path, verify_build_outputs=False
    )
    run_root = receipt_path.parent.parent.resolve()
    outputs: dict[str, dict[str, str] | str] = {"slug": slug}
    for name, suffix in (("manuscript", ".md"), ("epub", ".epub")):
        path = (output_dir / f"{slug}{suffix}").resolve()
        try:
            relative = path.relative_to(run_root)
        except ValueError as error:
            raise ValueError(f"fiction build {name} escapes the run root") from error
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"fiction build {name} must be a regular non-symlink file")
        outputs[name] = {"path": str(relative), "sha256": _sha256(path)}
    receipt["buildOutputs"] = outputs

    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{receipt_path.name}.", suffix=".tmp", dir=receipt_path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as destination:
            json.dump(receipt, destination, sort_keys=True, indent=2)
            destination.write("\n")
            destination.flush()
            os.fsync(destination.fileno())
        os.replace(temporary, receipt_path)
    except BaseException:
        if temporary.exists():
            temporary.unlink()
        raise
    return receipt
