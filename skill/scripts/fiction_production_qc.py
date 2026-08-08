#!/usr/bin/env python3
"""Verify a private first-listen fiction production receipt."""

from __future__ import annotations

import json
import hashlib
import re
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


def verify_fiction_receipt(chapters_dir: Path, receipt_path: Path) -> dict[str, Any]:
    try:
        receipt = json.loads(Path(receipt_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"invalid fiction production receipt: {receipt_path}: {error}") from error
    if not isinstance(receipt, dict):
        raise ValueError("fiction production receipt must be an object")
    if receipt.get("schemaVersion") != 1:
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
        if not isinstance(record, dict):
            raise ValueError(f"fiction production artifact {name} must be an object")
        relative = Path(str(record.get("path", "")))
        artifact = (run_root / relative).resolve()
        try:
            artifact.relative_to(run_root)
        except ValueError as error:
            raise ValueError(f"fiction production artifact {name} escapes the run root") from error
        expected = record.get("sha256")
        if not artifact.is_file():
            raise ValueError(f"missing fiction production artifact: {artifact}")
        if not isinstance(expected, str) or not SHA256_RE.fullmatch(expected):
            raise ValueError(f"fiction production artifact {name} has an invalid SHA-256")
        if _sha256(artifact) != expected:
            raise ValueError(f"fiction production artifact {name} hash mismatch")
    gates = receipt.get("gates")
    if not isinstance(gates, dict):
        raise ValueError("fiction production receipt gates must be an object")
    for name in sorted(REQUIRED_GATES):
        if gates.get(name) != "pass":
            raise ValueError(f"fiction production gate {name} must be pass")
    return receipt
