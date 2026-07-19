from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "skill" / "scripts"))

import build_book


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FictionProductionGateTests(unittest.TestCase):
    def test_build_accepts_hash_bound_private_first_listen_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            chapters = root / "chapters"
            research = root / "research"
            continuity = root / "continuity"
            revisions = root / "revisions"
            out = root / "dist"
            for directory in (chapters, research, continuity, revisions):
                directory.mkdir()

            chapter = chapters / "ch01.md"
            chapter.write_text("## Chapter One\n\nThe storm arrived before the appeal.\n", encoding="utf-8")
            artifacts = {
                "authorization": research / "unattended-decisions.json",
                "storyBible": root / "story-bible.md",
                "continuity": continuity / "final.md",
                "revisionReview": revisions / "full-manuscript-review.md",
                "proseQC": revisions / "full-prose-qc.md",
            }
            for name, path in artifacts.items():
                path.write_text(f"# {name}\n\nVerified.\n", encoding="utf-8")

            receipt = research / "fiction-production-receipt.json"
            receipt.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "status": "first-listen",
                        "productionMode": "unattended-first-listen",
                        "privacy": "private",
                        "permissionToPublish": False,
                        "humanReadingStatus": "pending",
                        "canonicalChapterSHA256": {chapter.name: sha256(chapter)},
                        "artifacts": {
                            name: {
                                "path": str(path.relative_to(root)),
                                "sha256": sha256(path),
                            }
                            for name, path in artifacts.items()
                        },
                        "gates": {
                            "manuscriptClosed": "pass",
                            "storyBibleReconciled": "pass",
                            "continuityReconciled": "pass",
                            "revisionPassesCompleted": "pass",
                            "proseQCPassed": "pass",
                        },
                        "negativeHumanVerdictOverrides": True,
                        "receiptDoesNotCertifyHumanAcceptance": True,
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )

            build_book.build(
                chapters,
                out,
                "Fixture Thriller",
                "Dan Fakkeldy",
                "",
                "fixture-thriller",
                fiction_receipt=receipt,
            )

            self.assertTrue((out / "fixture-thriller.epub").is_file())
            self.assertTrue((out / "fixture-thriller.md").is_file())

            invalid = json.loads(receipt.read_text(encoding="utf-8"))
            invalid["status"] = "pass"
            receipt.write_text(json.dumps(invalid), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "status must be first-listen"):
                build_book.build(
                    chapters,
                    root / "second-dist",
                    "Fixture Thriller",
                    "Dan Fakkeldy",
                    "",
                    "fixture-thriller",
                    fiction_receipt=receipt,
                )

            valid = json.loads(receipt.read_text(encoding="utf-8"))
            valid["status"] = "first-listen"
            boundary_cases = (
                ("schemaVersion", 2, "schemaVersion must be 1"),
                ("productionMode", "governed-final", "productionMode must be unattended-first-listen"),
                ("privacy", "public-safe", "privacy must be private"),
                ("negativeHumanVerdictOverrides", False, "preserve negative human authority"),
                ("receiptDoesNotCertifyHumanAcceptance", False, "must not certify human acceptance"),
            )
            for field, value, message in boundary_cases:
                with self.subTest(field=field):
                    changed = dict(valid)
                    changed[field] = value
                    receipt.write_text(json.dumps(changed), encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, message):
                        build_book.build(
                            chapters,
                            root / f"invalid-{field}",
                            "Fixture Thriller",
                            "Dan Fakkeldy",
                            "",
                            "fixture-thriller",
                            fiction_receipt=receipt,
                        )

    def test_build_rejects_receipt_after_canonical_chapter_changes(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            chapters = root / "chapters"
            research = root / "research"
            chapters.mkdir()
            research.mkdir()
            chapter = chapters / "ch01.md"
            chapter.write_text("## One\n\nAccepted text.\n", encoding="utf-8")
            receipt = research / "fiction-production-receipt.json"
            receipt.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "status": "first-listen",
                        "productionMode": "unattended-first-listen",
                        "privacy": "private",
                        "permissionToPublish": False,
                        "humanReadingStatus": "pending",
                        "canonicalChapterSHA256": {chapter.name: sha256(chapter)},
                        "negativeHumanVerdictOverrides": True,
                        "receiptDoesNotCertifyHumanAcceptance": True,
                    }
                ),
                encoding="utf-8",
            )
            chapter.write_text("## One\n\nChanged after approval.\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "chapter hash mismatch"):
                build_book.build(
                    chapters,
                    root / "dist",
                    "Fixture",
                    "Dan Fakkeldy",
                    "",
                    "fixture",
                    fiction_receipt=receipt,
                )

    def test_private_first_listen_receipt_cannot_grant_publication(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            chapters = root / "chapters"
            research = root / "research"
            chapters.mkdir()
            research.mkdir()
            chapter = chapters / "ch01.md"
            chapter.write_text("## One\n\nPrivate story.\n", encoding="utf-8")
            receipt = research / "fiction-production-receipt.json"
            receipt.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "status": "first-listen",
                        "productionMode": "unattended-first-listen",
                        "privacy": "private",
                        "permissionToPublish": True,
                        "humanReadingStatus": "pending",
                        "canonicalChapterSHA256": {chapter.name: sha256(chapter)},
                        "negativeHumanVerdictOverrides": True,
                        "receiptDoesNotCertifyHumanAcceptance": True,
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "cannot grant publication"):
                build_book.build(
                    chapters,
                    root / "dist",
                    "Fixture",
                    "Dan Fakkeldy",
                    "",
                    "fixture",
                    fiction_receipt=receipt,
                )

    def test_private_first_listen_receipt_cannot_claim_human_acceptance(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            chapters = root / "chapters"
            research = root / "research"
            chapters.mkdir()
            research.mkdir()
            chapter = chapters / "ch01.md"
            chapter.write_text("## One\n\nPrivate story.\n", encoding="utf-8")
            receipt = research / "fiction-production-receipt.json"
            receipt.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "status": "first-listen",
                        "productionMode": "unattended-first-listen",
                        "privacy": "private",
                        "permissionToPublish": False,
                        "humanReadingStatus": "accepted",
                        "canonicalChapterSHA256": {chapter.name: sha256(chapter)},
                        "negativeHumanVerdictOverrides": True,
                        "receiptDoesNotCertifyHumanAcceptance": True,
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "humanReadingStatus must be pending"):
                build_book.build(
                    chapters,
                    root / "dist",
                    "Fixture",
                    "Dan Fakkeldy",
                    "",
                    "fixture",
                    fiction_receipt=receipt,
                )

    def test_build_rejects_receipt_without_required_story_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            chapters = root / "chapters"
            research = root / "research"
            chapters.mkdir()
            research.mkdir()
            chapter = chapters / "ch01.md"
            chapter.write_text("## One\n\nAccepted story.\n", encoding="utf-8")
            receipt = research / "fiction-production-receipt.json"
            receipt.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "status": "first-listen",
                        "productionMode": "unattended-first-listen",
                        "privacy": "private",
                        "permissionToPublish": False,
                        "humanReadingStatus": "pending",
                        "canonicalChapterSHA256": {chapter.name: sha256(chapter)},
                        "artifacts": {},
                        "gates": {},
                        "negativeHumanVerdictOverrides": True,
                        "receiptDoesNotCertifyHumanAcceptance": True,
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "missing artifact"):
                build_book.build(
                    chapters,
                    root / "dist",
                    "Fixture",
                    "Dan Fakkeldy",
                    "",
                    "fixture",
                    fiction_receipt=receipt,
                )

    def test_build_rejects_nonpassing_fiction_gate(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            chapters = root / "chapters"
            research = root / "research"
            continuity = root / "continuity"
            revisions = root / "revisions"
            for directory in (chapters, research, continuity, revisions):
                directory.mkdir()
            chapter = chapters / "ch01.md"
            chapter.write_text("## One\n\nAccepted story.\n", encoding="utf-8")
            artifacts = {
                "authorization": research / "unattended-decisions.json",
                "storyBible": root / "story-bible.md",
                "continuity": continuity / "final.md",
                "revisionReview": revisions / "review.md",
                "proseQC": revisions / "prose-qc.md",
            }
            for path in artifacts.values():
                path.write_text("Verified.\n", encoding="utf-8")
            receipt = research / "fiction-production-receipt.json"
            receipt.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "status": "first-listen",
                        "productionMode": "unattended-first-listen",
                        "privacy": "private",
                        "permissionToPublish": False,
                        "humanReadingStatus": "pending",
                        "canonicalChapterSHA256": {chapter.name: sha256(chapter)},
                        "artifacts": {
                            name: {
                                "path": str(path.relative_to(root)),
                                "sha256": sha256(path),
                            }
                            for name, path in artifacts.items()
                        },
                        "gates": {
                            "manuscriptClosed": "pass",
                            "storyBibleReconciled": "pass",
                            "continuityReconciled": "pass",
                            "revisionPassesCompleted": "fail",
                            "proseQCPassed": "pass",
                        },
                        "negativeHumanVerdictOverrides": True,
                        "receiptDoesNotCertifyHumanAcceptance": True,
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "revisionPassesCompleted must be pass"):
                build_book.build(
                    chapters,
                    root / "dist",
                    "Fixture",
                    "Dan Fakkeldy",
                    "",
                    "fixture",
                    fiction_receipt=receipt,
                )


if __name__ == "__main__":
    unittest.main()
