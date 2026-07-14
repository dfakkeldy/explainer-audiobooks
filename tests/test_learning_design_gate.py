from __future__ import annotations

import hashlib
import importlib
import inspect
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
SCRIPTS = ROOT / "skill" / "scripts"
sys.path.insert(0, str(SCRIPTS))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class LearningDesignFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.chapters = self.root / "chapters"
        self.research = self.root / "research"
        self.chapters.mkdir()
        self.research.mkdir()
        (self.chapters / "ch01.md").write_text(
            "## Chapter 1 - What a Network Does\n\n"
            "A neural network maps input values to an output through learned parameters.\n",
            encoding="utf-8",
        )
        (self.chapters / "ch02.md").write_text(
            "## Chapter 2 - Training and Inference\n\n"
            "Training changes parameters. Inference uses those parameters on new input.\n",
            encoding="utf-8",
        )
        self.write_valid_records()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_json(self, name: str, value: object) -> None:
        (self.research / name).write_text(
            json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    def read_json(self, name: str) -> dict[str, object]:
        return json.loads((self.research / name).read_text(encoding="utf-8"))

    def chapter_hashes(self) -> dict[str, str]:
        return {path.name: sha256(path) for path in sorted(self.chapters.glob("ch*.md"))}

    def write_valid_records(self) -> None:
        actual_words = sum(
            len(path.read_text(encoding="utf-8").split())
            for path in sorted(self.chapters.glob("ch*.md"))
        )
        self.write_json(
            "learning-brief.json",
            {
                "schemaVersion": 1,
                "learnerOutcome": "Explain how a small neural network is trained and used.",
                "priorKnowledge": "Curious beginner; knows that AI learns from examples.",
                "openingOrientation": {
                    "context": "Why neural networks are useful question machines.",
                    "promise": "Build one mental model from inputs to inference.",
                    "route": "Network, training, inference, then limitations.",
                },
                "originalTargetWords": actual_words,
                "currentTargetWords": actual_words,
                "minimumAcceptedWords": actual_words - 2,
                "maximumAcceptedWords": actual_words + 2,
                "draftingStarted": True,
                "scopeHistory": [],
            },
        )
        self.write_json(
            "learning-outline.json",
            {
                "schemaVersion": 1,
                "authorization": {
                    "status": "approved",
                    "source": "user",
                    "evidence": "Dan approved the chapter progression on 2026-07-14.",
                },
                "curriculumPattern": {
                    "name": "mechanism-first-spiral",
                    "reason": "The learner needs one stable mechanism before larger systems.",
                    "fitEvidence": "A beginner outcome centered on training and inference.",
                },
                "throughlines": ["parameters store learning", "training differs from use"],
                "chapters": [
                    {
                        "file": "ch01.md",
                        "purpose": "Establish the network as a calculable mapping.",
                        "prerequisites": ["ordinary arithmetic"],
                    },
                    {
                        "file": "ch02.md",
                        "purpose": "Separate training from inference.",
                        "prerequisites": ["network mapping", "parameters"],
                    },
                ],
            },
        )
        self.write_json(
            "chapter-plans.json",
            {
                "schemaVersion": 1,
                "chapters": [
                    {
                        "file": "ch01.md",
                        "purpose": "Build the first working mental model.",
                        "prerequisites": ["ordinary arithmetic"],
                        "knowledgeDelta": "Calculate one small network output by hand.",
                        "groundedExample": "An email urgency score from two inputs.",
                        "concepts": ["neural network", "parameter"],
                        "beats": ["orient", "define", "calculate", "test a boundary"],
                    },
                    {
                        "file": "ch02.md",
                        "purpose": "Distinguish learning from use.",
                        "prerequisites": ["neural network", "parameter"],
                        "knowledgeDelta": "Explain training and inference without conflating them.",
                        "groundedExample": "Update an email classifier, then score a new message.",
                        "concepts": ["training", "inference"],
                        "beats": ["retrieve", "compare", "walk through", "correct misconception"],
                    },
                ],
            },
        )
        self.write_json(
            "coverage-ledger.json",
            {
                "schemaVersion": 1,
                "concepts": [
                    {
                        "name": "inference",
                        "definition": "Using learned parameters to calculate an output for new input.",
                        "reason": "A trained model is useful only when it can process new cases.",
                        "mechanism": "Run inputs through the fixed weighted calculation.",
                        "concreteCase": "Score a newly arrived email.",
                        "boundary": "Inference does not update the learned parameters.",
                        "boundaryNotApplicableReason": "",
                        "misconception": "Inference is not another name for training.",
                        "expectedAbility": "Identify whether a described operation is training or inference.",
                        "chapterUses": [
                            {"chapter": "ch02.md", "function": "introduce"},
                            {"chapter": "ch02.md", "function": "apply"},
                        ],
                    }
                ],
            },
        )
        self.write_json(
            "continuity.json",
            {
                "schemaVersion": 1,
                "checkpoints": [
                    {
                        "afterChapter": "ch01.md",
                        "termsDefined": ["neural network", "parameter"],
                        "examplesUsed": ["email urgency score"],
                        "callbacks": [],
                        "promises": ["separate training from inference"],
                        "unresolvedQuestions": ["how parameters change"],
                    },
                    {
                        "afterChapter": "ch02.md",
                        "termsDefined": ["training", "inference"],
                        "examplesUsed": ["new email score"],
                        "callbacks": ["email urgency score"],
                        "promises": [],
                        "unresolvedQuestions": [],
                    },
                ],
            },
        )
        hashes = self.chapter_hashes()
        self.write_json(
            "learning-review.json",
            {
                "schemaVersion": 1,
                "reviewedChapterSHA256": hashes,
                "structure": {
                    "reviewer": "independent-structure-reviewer",
                    "verdict": "pass",
                    "findings": [],
                },
                "beginnerReader": {
                    "reviewer": "independent-beginner-reader",
                    "verdict": "pass",
                    "findings": [
                        {
                            "id": "BR-01",
                            "location": "ch02.md paragraph 1",
                            "category": "misconception",
                            "evidence": "The distinction is explicit.",
                            "decision": "rejected",
                            "reason": "No repair is needed after review.",
                        }
                    ],
                },
            },
        )


class LearningDesignGateTests(LearningDesignFixture):
    def module(self):
        return importlib.import_module("learning_design_qc")

    def test_valid_run_writes_hash_bound_receipt(self) -> None:
        module = self.module()
        receipt_path = self.research / "learning-design-receipt.json"
        receipt = module.write_receipt(self.root, receipt_path)

        self.assertEqual(1, receipt["schemaVersion"])
        self.assertEqual("pass", receipt["status"])
        self.assertEqual(self.chapter_hashes(), receipt["chapterSHA256"])
        self.assertEqual(receipt, module.verify_learning_receipt(self.chapters, receipt_path))

    def test_missing_opening_orientation_fails(self) -> None:
        brief = self.read_json("learning-brief.json")
        brief["openingOrientation"] = {}
        self.write_json("learning-brief.json", brief)

        with self.assertRaisesRegex(ValueError, "openingOrientation"):
            self.module().validate_run(self.root)

    def test_outline_requires_explicit_authorization(self) -> None:
        outline = self.read_json("learning-outline.json")
        outline["authorization"] = {"status": "pending", "source": "agent", "evidence": ""}
        self.write_json("learning-outline.json", outline)

        with self.assertRaisesRegex(ValueError, "authorization"):
            self.module().validate_run(self.root)

    def test_outline_requires_a_supported_curriculum_pattern(self) -> None:
        outline = self.read_json("learning-outline.json")
        outline.pop("curriculumPattern")
        self.write_json("learning-outline.json", outline)

        with self.assertRaisesRegex(ValueError, "outline.curriculumPattern"):
            self.module().validate_run(self.root)

    def test_reduced_target_requires_user_approved_scope_history(self) -> None:
        brief = self.read_json("learning-brief.json")
        old_target = brief["originalTargetWords"]
        new_target = old_target - 5
        brief["currentTargetWords"] = new_target
        brief["minimumAcceptedWords"] = new_target - 2
        brief["maximumAcceptedWords"] = new_target + 2
        brief["scopeHistory"] = [
            {
                "oldTargetWords": old_target,
                "newTargetWords": new_target,
                "reason": "The draft came out short.",
                "approved": False,
                "approvalSource": "agent",
                "evidence": "",
            }
        ]
        self.write_json("learning-brief.json", brief)

        with self.assertRaisesRegex(ValueError, "target reduction"):
            self.module().validate_run(self.root)

    def test_every_chapter_requires_a_plan_and_continuity_checkpoint(self) -> None:
        plans = self.read_json("chapter-plans.json")
        plans["chapters"] = plans["chapters"][:1]
        self.write_json("chapter-plans.json", plans)

        with self.assertRaisesRegex(ValueError, "chapter plan"):
            self.module().validate_run(self.root)

        self.write_valid_records()
        continuity = self.read_json("continuity.json")
        continuity["checkpoints"] = continuity["checkpoints"][:1]
        self.write_json("continuity.json", continuity)
        with self.assertRaisesRegex(ValueError, "continuity"):
            self.module().validate_run(self.root)

    def test_core_concept_requires_a_complete_explanation_path(self) -> None:
        coverage = self.read_json("coverage-ledger.json")
        coverage["concepts"][0]["mechanism"] = ""
        self.write_json("coverage-ledger.json", coverage)

        with self.assertRaisesRegex(ValueError, "mechanism"):
            self.module().validate_run(self.root)

    def test_reviews_must_pass_and_match_final_chapter_hashes(self) -> None:
        review = self.read_json("learning-review.json")
        review["beginnerReader"]["verdict"] = "fail"
        self.write_json("learning-review.json", review)
        with self.assertRaisesRegex(ValueError, "beginnerReader"):
            self.module().validate_run(self.root)

        self.write_valid_records()
        chapter = self.chapters / "ch02.md"
        chapter.write_text(chapter.read_text(encoding="utf-8") + "\nChanged.\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "reviewedChapterSHA256"):
            self.module().validate_run(self.root)

    def test_unresolved_review_finding_fails(self) -> None:
        review = self.read_json("learning-review.json")
        review["structure"]["findings"] = [
            {
                "id": "ST-01",
                "location": "ch01.md paragraph 1",
                "category": "orientation",
                "evidence": "The opening lacks context.",
                "decision": "unresolved",
                "reason": "",
            }
        ]
        self.write_json("learning-review.json", review)

        with self.assertRaisesRegex(ValueError, "unresolved"):
            self.module().validate_run(self.root)


class LearningDesignBuilderTests(LearningDesignFixture):
    def modules(self):
        learning = importlib.import_module("learning_design_qc")
        builder = importlib.import_module("build_book")
        return learning, builder

    def cli_base(self, out_dir: Path) -> list[str]:
        return [
            sys.executable,
            str(SCRIPTS / "build_book.py"),
            "--chapters-dir",
            str(self.chapters),
            "--out-dir",
            str(out_dir),
            "--title",
            "Learning Gate Fixture",
            "--author",
            "Dan Fakkeldy",
            "--slug",
            "learning-gate-fixture",
        ]

    def test_book_builder_accepts_and_verifies_a_learning_receipt(self) -> None:
        learning, builder = self.modules()
        self.assertIn("learning_receipt", inspect.signature(builder.build).parameters)
        receipt = self.research / "learning-design-receipt.json"
        learning.write_receipt(self.root, receipt)
        output = self.root / "dist"

        builder.build(
            self.chapters,
            output,
            "Learning Gate Fixture",
            "Dan Fakkeldy",
            "",
            "learning-gate-fixture",
            learning_receipt=receipt,
        )
        self.assertTrue((output / "learning-gate-fixture.epub").is_file())

    def test_stale_learning_receipt_fails_before_output(self) -> None:
        learning, builder = self.modules()
        receipt = self.research / "learning-design-receipt.json"
        learning.write_receipt(self.root, receipt)
        (self.chapters / "ch02.md").write_text("## Changed\n\nChanged.\n", encoding="utf-8")
        output = self.root / "dist"

        with self.assertRaisesRegex(ValueError, "chapter hash"):
            builder.build(
                self.chapters,
                output,
                "Learning Gate Fixture",
                "Dan Fakkeldy",
                "",
                "learning-gate-fixture",
                learning_receipt=receipt,
            )
        self.assertFalse(output.exists())

    def test_cli_requires_receipt_or_explicit_legacy_reproduction(self) -> None:
        no_gate_output = self.root / "no-gate"
        missing = subprocess.run(
            self.cli_base(no_gate_output), capture_output=True, text=True, check=False
        )
        self.assertNotEqual(0, missing.returncode)
        self.assertIn("--learning-receipt", missing.stderr)
        self.assertFalse(no_gate_output.exists())

        legacy_output = self.root / "legacy"
        legacy = subprocess.run(
            self.cli_base(legacy_output) + ["--legacy-without-learning-receipt"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, legacy.returncode, legacy.stderr)
        self.assertTrue((legacy_output / "learning-gate-fixture.epub").is_file())

    def test_cli_accepts_current_learning_receipt(self) -> None:
        learning, _ = self.modules()
        receipt = self.research / "learning-design-receipt.json"
        learning.write_receipt(self.root, receipt)
        output = self.root / "current"
        result = subprocess.run(
            self.cli_base(output) + ["--learning-receipt", str(receipt)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertTrue((output / "learning-gate-fixture.epub").is_file())


if __name__ == "__main__":
    unittest.main()
