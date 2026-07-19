from __future__ import annotations

import hashlib
import importlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
SCRIPTS = ROOT / "skill" / "scripts"
sys.path.insert(0, str(SCRIPTS))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PronunciationPlanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.chapters = self.root / "chapters"
        self.research = self.root / "research"
        self.chapters.mkdir()
        self.research.mkdir()
        (self.chapters / "ch01.md").write_text(
            "## Training choices\n\nA hyperparameter is selected before training. "
            "Several hyperparameters shape the run.\n",
            encoding="utf-8",
        )
        (self.research / "learning-outline.json").write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "chapters": [
                        {
                            "file": "ch01.md",
                            "purpose": "Introduce training choices.",
                            "prerequisites": [],
                        }
                    ],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        self.write_plan(self.valid_plan())

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def module(self):
        return importlib.import_module("pronunciation_plan_qc")

    def valid_plan(self) -> dict[str, object]:
        return {
            "schemaVersion": 1,
            "terms": [
                {
                    "term": "hyperparameter",
                    "variants": ["hyperparameters"],
                    "source": "listener",
                    "reason": "The listener requested pronunciation verification.",
                    "expectedChapters": ["ch01.md"],
                    "required": True,
                    "status": "planned",
                    "decision": None,
                    "evidence": None,
                }
            ],
        }

    def write_plan(self, plan: dict[str, object]) -> None:
        (self.research / "pronunciation-plan.json").write_text(
            json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    def accept_plan(self) -> Path:
        reel_path = self.research / "pronunciation-probe-reel.m4b"
        reel_path.write_bytes(b"governed pronunciation reel")
        evidence_path = self.research / "pronunciation-probe-evidence.json"
        evidence_path.write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "reelFileName": reel_path.name,
                    "reelSHA256": sha256(reel_path),
                    "clips": [
                        {
                            "term": "hyperparameter",
                            "variantHeard": "hyperparameter",
                        },
                        {
                            "term": "hyperparameter",
                            "variantHeard": "hyperparameters",
                        },
                    ],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        plan = self.valid_plan()
        entry = plan["terms"][0]
        entry["status"] = "accepted"
        entry["decision"] = {
            "acceptedBy": "Dan Fakkeldy",
            "acceptedAt": "2026-07-14T19:00:00-03:00",
        }
        entry["evidence"] = {
            "path": "research/pronunciation-probe-evidence.json",
            "sha256": sha256(evidence_path),
        }
        self.write_plan(plan)
        return evidence_path

    def probe_unattended_plan(self) -> Path:
        reel_path = self.research / "pronunciation-probe-reel.m4b"
        reel_path.write_bytes(b"governed unattended pronunciation reel")
        evidence_path = self.research / "pronunciation-probe-evidence.json"
        evidence_path.write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "reelFileName": reel_path.name,
                    "reelSHA256": sha256(reel_path),
                    "clips": [
                        {
                            "term": "hyperparameter",
                            "variantHeard": "hyperparameter",
                        },
                        {
                            "term": "hyperparameter",
                            "variantHeard": "hyperparameters",
                        },
                    ],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        plan = self.valid_plan()
        plan["assuranceLevel"] = "unattended-first-listen"
        entry = plan["terms"][0]
        entry["status"] = "probed"
        entry["decision"] = None
        entry["evidence"] = {
            "path": "research/pronunciation-probe-evidence.json",
            "sha256": sha256(evidence_path),
        }
        self.write_plan(plan)
        return evidence_path

    def test_planning_accepts_required_term_and_variants_in_named_chapter(self) -> None:
        result = self.module().validate_plan(self.root, "planning")
        self.assertEqual(["hyperparameter"], result["requiredTerms"])

    def test_planning_is_prospective_and_does_not_require_drafted_chapters(self) -> None:
        (self.chapters / "ch01.md").unlink()

        result = self.module().validate_plan(self.root, "planning")

        self.assertEqual(["ch01.md"], result["plannedChapters"])
        self.assertEqual({}, result["chapterSHA256"])

    def test_fiction_planning_uses_hash_bound_fiction_receipt_without_learning_outline(self) -> None:
        (self.research / "learning-outline.json").unlink()
        continuity = self.root / "continuity"
        revisions = self.root / "revisions"
        continuity.mkdir()
        revisions.mkdir()
        artifacts = {
            "authorization": self.research / "unattended-decisions.json",
            "storyBible": self.root / "story-bible.md",
            "continuity": continuity / "final.md",
            "revisionReview": revisions / "review.md",
            "proseQC": revisions / "prose-qc.md",
        }
        for path in artifacts.values():
            path.write_text("Verified.\n", encoding="utf-8")
        (self.research / "fiction-production-receipt.json").write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "status": "first-listen",
                    "productionMode": "unattended-first-listen",
                    "privacy": "private",
                    "permissionToPublish": False,
                    "humanReadingStatus": "pending",
                    "canonicalChapterSHA256": {
                        "ch01.md": sha256(self.chapters / "ch01.md")
                    },
                    "artifacts": {
                        name: {
                            "path": str(path.relative_to(self.root)),
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

        result = self.module().validate_plan(self.root, "planning")

        self.assertEqual(["ch01.md"], result["plannedChapters"])
        self.assertEqual({}, result["chapterSHA256"])

    def test_listener_term_must_exist_in_each_expected_chapter(self) -> None:
        plan = self.valid_plan()
        plan["terms"][0]["expectedChapters"] = ["ch02.md"]
        self.write_plan(plan)

        with self.assertRaisesRegex(ValueError, "unknown expected chapter"):
            self.module().validate_plan(self.root, "planning")

    def test_duplicate_normalized_term_fails(self) -> None:
        plan = self.valid_plan()
        duplicate = dict(plan["terms"][0])
        duplicate["term"] = "Hyperparameter"
        plan["terms"].append(duplicate)
        self.write_plan(plan)

        with self.assertRaisesRegex(ValueError, "duplicate pronunciation term"):
            self.module().validate_plan(self.root, "planning")

    def test_full_render_requires_accepted_human_evidence(self) -> None:
        with self.assertRaisesRegex(ValueError, "accepted human evidence"):
            self.module().validate_plan(self.root, "full-render")

    def test_listener_can_waive_pronunciation_listening_without_acceptance(self) -> None:
        evidence_path = self.accept_plan()
        plan = json.loads(
            (self.research / "pronunciation-plan.json").read_text(encoding="utf-8")
        )
        entry = plan["terms"][0]
        entry["status"] = "waived-by-listener"
        entry["decision"] = {
            "waivedBy": "Dan Fakkeldy",
            "waivedAt": "2026-07-16T15:30:00-03:00",
            "reason": "The listener asked production to continue without another gate.",
            "validationBoundary": (
                "The governed reel exists, but human pronunciation listening "
                "was not collected."
            ),
        }
        self.write_plan(plan)
        receipt_path = self.research / "pronunciation-plan-receipt.json"

        receipt = self.module().write_receipt(self.root, receipt_path)

        self.assertEqual("pass-with-listener-waiver", receipt["status"])
        self.assertEqual(
            "not-collected-listener-waived", receipt["humanListening"]
        )
        self.assertEqual(
            "not-collected-listener-waived",
            receipt["listeningAuthority"]["evidenceStatus"],
        )
        self.assertTrue(
            receipt["listeningAuthority"]["waiverDoesNotCertifyPronunciation"]
        )
        self.assertEqual(sha256(evidence_path), receipt["evidenceSHA256"])

    def test_pronunciation_waiver_requires_an_explicit_validation_boundary(self) -> None:
        self.accept_plan()
        plan = json.loads(
            (self.research / "pronunciation-plan.json").read_text(encoding="utf-8")
        )
        entry = plan["terms"][0]
        entry["status"] = "waived-by-listener"
        entry["decision"] = {
            "waivedBy": "Dan Fakkeldy",
            "waivedAt": "2026-07-16T15:30:00-03:00",
            "reason": "The listener asked production to continue.",
        }
        self.write_plan(plan)

        with self.assertRaisesRegex(ValueError, "validationBoundary"):
            self.module().validate_plan(self.root, "full-render")

    def test_unattended_full_render_uses_probe_without_fabricating_acceptance(self) -> None:
        evidence_path = self.probe_unattended_plan()
        receipt_path = self.research / "pronunciation-plan-receipt.json"

        receipt = self.module().write_receipt(self.root, receipt_path)

        self.assertEqual("first-listen", receipt["status"])
        self.assertEqual("unattended-first-listen", receipt["assuranceLevel"])
        self.assertEqual("pending", receipt["humanListening"])
        self.assertEqual(sha256(evidence_path), receipt["evidenceSHA256"])
        plan = json.loads(
            (self.research / "pronunciation-plan.json").read_text(encoding="utf-8")
        )
        self.assertIsNone(plan["terms"][0]["decision"])

    def test_unattended_probe_still_requires_every_variant(self) -> None:
        evidence_path = self.probe_unattended_plan()
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        evidence["clips"].pop()
        evidence_path.write_text(
            json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        plan = json.loads(
            (self.research / "pronunciation-plan.json").read_text(encoding="utf-8")
        )
        plan["terms"][0]["evidence"]["sha256"] = sha256(evidence_path)
        self.write_plan(plan)

        with self.assertRaisesRegex(ValueError, "missing heard variants"):
            self.module().validate_plan(self.root, "full-render")

    def test_full_render_requires_a_clip_for_every_variant(self) -> None:
        evidence_path = self.accept_plan()
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        evidence["clips"].pop()
        evidence_path.write_text(
            json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        plan = json.loads(
            (self.research / "pronunciation-plan.json").read_text(encoding="utf-8")
        )
        plan["terms"][0]["evidence"]["sha256"] = sha256(evidence_path)
        self.write_plan(plan)

        with self.assertRaisesRegex(ValueError, "missing heard variants"):
            self.module().validate_plan(self.root, "full-render")

    def test_full_render_rejects_stale_evidence_hash(self) -> None:
        evidence_path = self.accept_plan()
        evidence_path.write_text("{}\n", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "evidence SHA-256"):
            self.module().validate_plan(self.root, "full-render")

    def test_full_render_rejects_a_replaced_pronunciation_reel(self) -> None:
        self.accept_plan()
        (self.research / "pronunciation-probe-reel.m4b").write_bytes(b"replacement")

        with self.assertRaisesRegex(ValueError, "reel SHA-256"):
            self.module().validate_plan(self.root, "full-render")

    def test_receipt_binds_plan_evidence_and_chapters(self) -> None:
        evidence_path = self.accept_plan()
        receipt_path = self.research / "pronunciation-plan-receipt.json"
        receipt = self.module().write_receipt(self.root, receipt_path)

        self.assertEqual("pass", receipt["status"])
        self.assertEqual(sha256(self.research / "pronunciation-plan.json"), receipt["planSHA256"])
        self.assertEqual(sha256(evidence_path), receipt["evidenceSHA256"])
        self.assertEqual({"ch01.md": sha256(self.chapters / "ch01.md")}, receipt["chapterSHA256"])


if __name__ == "__main__":
    unittest.main()
