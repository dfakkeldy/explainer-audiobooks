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
        (self.research / "evidence-notes.md").write_text(
            "# Evidence notes\n\n"
            "## EV-001\n\n"
            "Postal recognition supplied an early practical setting for neural networks.\n",
            encoding="utf-8",
        )
        (self.research / "voice-exemplar.md").write_text(
            "# Accepted voice exemplar\n\n"
            "A postal worker does not begin with a tensor. The day begins with an envelope.\n",
            encoding="utf-8",
        )
        (self.research / "voice-source-profile.md").write_text(
            "# Voice-source craft profile\n\n"
            "Open with a concrete question, move from evidence to a plain-language "
            "mechanism, use restrained humor, and finish with a practical choice.\n",
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

    def enable_unattended_first_listen(self) -> None:
        decisions_path = self.research / "unattended-decisions.json"
        self.write_json(
            "unattended-decisions.json",
            {
                "schemaVersion": 1,
                "productionMode": "unattended-first-listen",
                "requestEvidence": "User requested a private book ready to listen to overnight.",
                "privacy": "private",
                "permissionToPublish": False,
                "deliveryIntent": "private-project-only",
                "humanListeningStatus": "pending",
                "decisions": [
                    {
                        "field": "audience",
                        "choice": "curious beginner",
                        "reason": "The request did not name a narrower audience.",
                        "source": "documented-default",
                    }
                ],
            },
        )
        brief = self.read_json("learning-brief.json")
        brief["productionMode"] = {
            "name": "unattended-first-listen",
            "requestEvidence": "User requested a private book ready to listen to overnight.",
            "decisionsPath": "research/unattended-decisions.json",
            "decisionsSHA256": sha256(decisions_path),
        }
        self.write_json("learning-brief.json", brief)

        outline = self.read_json("learning-outline.json")
        outline["authorization"] = {
            "status": "approved",
            "source": "explicit-autonomous-run",
            "evidence": "The overnight request delegated reversible outline decisions.",
        }
        self.write_json("learning-outline.json", outline)

        pilot = self.read_json("comprehension-pilot.json")
        voice_source = pilot["humanCheckpoints"]["voiceSource"]
        pilot.pop("humanCheckpoints")
        pilot["status"] = "first-listen"
        pilot["listener"] = "human-listener-pending"
        pilot["listeningContext"] = "Editorial pilot review; representative road listening pending"
        pilot["editorialCheckpoints"] = {
            "voiceSource": voice_source,
            "outline": {
                "status": "editorially-approved",
                "reviewer": "independent-outline-reviewer",
                "evidence": "The outline passed the road-book and evidence checks.",
                "recordedBeforePilotDraft": True,
            },
            "firstSection": {
                "status": "editorially-accepted",
                "reviewer": "independent-voice-reviewer",
                "evidence": "The first section passed voice and teaching diagnostics.",
                "recordedBeforeRemainingDraft": True,
                "voiceExemplarPath": "research/voice-exemplar.md",
                "voiceExemplarSHA256": sha256(self.research / "voice-exemplar.md"),
            },
        }
        pilot["decision"] = {
            "verdict": "continue",
            "authority": "editorial-review",
            "evidence": "The rendered pilot passed transcript, structure, and ear-pass review.",
            "recordedBeforeFullDraft": True,
        }
        self.write_json("comprehension-pilot.json", pilot)

    def chapter_hashes(self) -> dict[str, str]:
        return {path.name: sha256(path) for path in sorted(self.chapters.glob("ch*.md"))}

    def write_valid_records(self) -> None:
        actual_words = sum(
            len(path.read_text(encoding="utf-8").split())
            for path in sorted(self.chapters.glob("ch*.md"))
        )
        self.write_json(
            "evidence-notes.json",
            {
                "schemaVersion": 2,
                "notesPath": "research/evidence-notes.md",
                "notesSHA256": sha256(self.research / "evidence-notes.md"),
                "claimPolicy": "traceable-only",
                "claims": [
                    {
                        "id": "EV-001",
                        "claim": "Postal recognition supplied an early practical setting for neural networks.",
                        "source": "Primary-source postal recognition paper",
                        "locator": "Introduction and application description",
                        "verificationStatus": "verified",
                    }
                ],
                "unresolvedConflicts": [],
            },
        )
        self.write_json(
            "learning-brief.json",
            {
                "schemaVersion": 2,
                "learnerOutcome": "Explain how a small neural network is trained and used.",
                "priorKnowledge": "Curious beginner; knows that AI learns from examples.",
                "audienceLevel": "beginner",
                "listeningMode": {
                    "name": "road-book",
                    "primaryContext": "Driving and delivering mail",
                    "attentionConstraints": [
                        "eyes unavailable",
                        "single-pass listening",
                        "real interruptions",
                    ],
                },
                "revisionMode": {
                    "name": "new-book",
                    "priorEditionExists": False,
                    "sourceEdition": "",
                    "preserve": {
                        "governingQuestion": "",
                        "narrativeSpine": "",
                        "successfulExamples": [],
                        "chapterJobs": [],
                    },
                },
                "openingOrientation": {
                    "context": "Why neural networks are useful question machines.",
                    "promise": "Build one mental model from inputs to inference.",
                    "route": "Network, training, inference, then limitations.",
                },
                "originalTargetWords": actual_words,
                "currentTargetWords": actual_words,
                "estimatedMinimumWords": actual_words - 2,
                "estimatedMaximumWords": actual_words + 2,
                "draftingStarted": True,
                "scopeHistory": [],
            },
        )
        self.write_json(
            "learning-outline.json",
            {
                "schemaVersion": 2,
                "authorization": {
                    "status": "approved",
                    "source": "user",
                    "evidence": "Dan approved the chapter progression on 2026-07-14.",
                },
                "curriculumPattern": {
                    "name": "question-led-narrative",
                    "reason": "A human problem gives the mechanism a reason to exist.",
                    "fitEvidence": "The listener learns best through questions, people, and uses.",
                },
                "throughlines": ["parameters store learning", "training differs from use"],
                "durableOutcomes": [
                    "Explain how learned parameters turn an input into an output.",
                    "Distinguish training from inference in a fresh situation.",
                    "Recognize why a network needs examples.",
                    "Connect neural networks to postal recognition.",
                    "Explain one useful boundary of the simple network story.",
                    "Use the safe-and-combination analogy without stretching it.",
                ],
                "roadBookDesign": {
                    "governingQuestion": "How does a machine learn a useful distinction?",
                    "narrativeSpine": "Follow a postal worker from handwritten mail to a trained classifier.",
                    "peopleAndHistory": [
                        "Yann LeCun and handwritten ZIP-code recognition",
                        "postal workers sorting real mail",
                    ],
                    "chapterJobVariety": ["scene", "mechanism", "history", "application"],
                    "realWorldApplications": [
                        "handwritten ZIP-code recognition",
                        "cheque processing",
                    ],
                    "optionalStudyBoundary": "Multi-step derivations and specialist variants stay out of the main listen.",
                },
                "referenceLayer": {
                    "items": ["multi-step derivations", "specialist architecture variants"],
                    "formats": ["EPUB figure", "optional appendix", "short focused lesson"],
                },
                "chapters": [
                    {
                        "file": "ch01.md",
                        "purpose": "Establish the network as a calculable mapping.",
                        "prerequisites": ["ordinary arithmetic"],
                        "sections": [
                            {
                                "id": "ch01-s01",
                                "job": "Make the recognition problem concrete before naming the mechanism.",
                                "argument": "Learning matters because fixed handwritten rules fail on human variation.",
                                "specificClaims": ["EV-001"],
                                "throughlineAdvance": "Introduce parameters as stored adjustments.",
                                "payoff": "The postal scene earns the first technical explanation.",
                                "landingBeat": "The listener sees why the adjustable mechanism has to exist.",
                                "mustNotRepeat": [],
                            }
                        ],
                    },
                    {
                        "file": "ch02.md",
                        "purpose": "Separate training from inference.",
                        "prerequisites": ["network mapping", "parameters"],
                        "sections": [
                            {
                                "id": "ch02-s01",
                                "job": "Contrast changing the sorter with using the finished sorter.",
                                "argument": "Training and inference are different operations even when they use the same network.",
                                "specificClaims": ["EV-001"],
                                "throughlineAdvance": "Show when parameters change and when they stay fixed.",
                                "payoff": "Tomorrow's envelope resolves the training-versus-use question.",
                                "landingBeat": "The listener can classify a fresh operation as training or inference.",
                                "mustNotRepeat": ["Do not redefine parameters from scratch."],
                            }
                        ],
                    },
                ],
            },
        )
        self.write_json(
            "chapter-plans.json",
            {
                "schemaVersion": 2,
                "chapters": [
                    {
                        "file": "ch01.md",
                        "purpose": "Build the first working mental model.",
                        "prerequisites": ["ordinary arithmetic"],
                        "knowledgeDelta": "Calculate one small network output by hand.",
                        "groundedExample": "An email urgency score from two inputs.",
                        "concepts": ["neural network", "parameter"],
                        "beats": ["orient", "define", "calculate", "test a boundary"],
                        "newCoreTerms": [
                            {
                                "term": "neural network",
                                "problemBeforeName": "A postal system needs to recognize many forms of the same handwritten digit.",
                            },
                            {
                                "term": "parameter",
                                "problemBeforeName": "The recognizer needs adjustable settings that examples can change.",
                            },
                        ],
                        "audioLoad": {
                            "temporaryValues": 2,
                            "symbolicChainSteps": 2,
                            "calculationTreatment": "brief-spoken",
                            "focusedLessonMinutes": 0,
                            "concreteReset": "Return to a handwritten seven after the two-step intuition.",
                        },
                        "teachingInfrastructure": {
                            "narrativeConnection": "A postal worker meets an unusually written seven.",
                            "realWorldApplication": "Automated ZIP-code recognition",
                        },
                    },
                    {
                        "file": "ch02.md",
                        "purpose": "Distinguish learning from use.",
                        "prerequisites": ["neural network", "parameter"],
                        "knowledgeDelta": "Explain training and inference without conflating them.",
                        "groundedExample": "Update an email classifier, then score a new message.",
                        "concepts": ["training", "inference"],
                        "beats": ["retrieve", "compare", "walk through", "correct misconception"],
                        "newCoreTerms": [
                            {
                                "term": "training",
                                "problemBeforeName": "The system must improve after seeing labelled examples.",
                            },
                            {
                                "term": "inference",
                                "problemBeforeName": "A finished recognizer must handle one newly arrived item without relearning.",
                            },
                        ],
                        "audioLoad": {
                            "temporaryValues": 0,
                            "symbolicChainSteps": 0,
                            "calculationTreatment": "none",
                            "focusedLessonMinutes": 0,
                            "concreteReset": "Compare learning yesterday with sorting one envelope today.",
                        },
                        "teachingInfrastructure": {
                            "narrativeConnection": "The trained sorter encounters tomorrow's mail.",
                            "realWorldApplication": "Cheque and mail sorting after training",
                        },
                    },
                ],
            },
        )
        self.write_json(
            "coverage-ledger.json",
            {
                "schemaVersion": 2,
                "concepts": [
                    {
                        "name": "parameter",
                        "durableOutcome": "Explain how learned parameters turn an input into an output.",
                        "definition": "An adjustable part of a network that training changes.",
                        "reason": "A recognizer needs settings that examples can improve.",
                        "mechanism": "Training nudges parameters so useful outputs become more likely.",
                        "concreteCase": "Improve recognition of a handwritten seven.",
                        "problemBeforeName": "The recognizer gets the seven wrong and needs something adjustable.",
                        "realWorldApplications": [
                            "handwritten ZIP-code recognition",
                            "cheque processing",
                        ],
                        "analogy": {
                            "name": "safe and combination",
                            "relationship": "Capacity is different from learned access.",
                            "correspondence": [
                                "the safe is the network's representational capacity",
                                "the combination is the learned parameter setting",
                            ],
                            "limit": "A network does not literally search combinations like a person opening a safe.",
                        },
                        "analogyNotApplicableReason": "",
                        "boundary": "A parameter stores an adjustment, not a human-readable rule.",
                        "boundaryNotApplicableReason": "",
                        "misconception": "A parameter is not a complete memory or a written instruction.",
                        "expectedAbility": "Explain why training changes parameters and later use can leave them fixed.",
                        "chapterUses": [
                            {"chapter": "ch01.md", "function": "introduce"},
                            {"chapter": "ch02.md", "function": "retrieve"},
                        ],
                        "retrievals": [
                            {
                                "chapter": "ch02.md",
                                "afterGapFrom": "ch01.md",
                                "freshSituation": "A trained mail sorter handles tomorrow's envelope.",
                                "listenerTask": "Identify what stays fixed during inference.",
                                "answerPlacement": "The next paragraph answers with parameters.",
                            }
                        ],
                    }
                ],
            },
        )
        self.write_json(
            "continuity.json",
            {
                "schemaVersion": 2,
                "draftContexts": [
                    {
                        "section": "ch01-s01",
                        "fullOutlinePath": "research/learning-outline.json",
                        "evidenceNotesPath": "research/evidence-notes.md",
                        "styleGuidePath": "research/voice-source-profile.md",
                        "previousSectionTextOrSummary": "Opening section; there is no previous section.",
                        "sectionJob": "Make the recognition problem concrete before naming the mechanism.",
                        "mustNotRepeat": [],
                    },
                    {
                        "section": "ch02-s01",
                        "fullOutlinePath": "research/learning-outline.json",
                        "evidenceNotesPath": "research/evidence-notes.md",
                        "styleGuidePath": "research/voice-source-profile.md",
                        "previousSectionTextOrSummary": "Parameters are adjustable settings learned from varied handwriting.",
                        "sectionJob": "Contrast changing the sorter with using the finished sorter.",
                        "mustNotRepeat": ["Do not redefine parameters from scratch."],
                    },
                ],
                "checkpoints": [
                    {
                        "afterChapter": "ch01.md",
                        "termsDefined": ["neural network", "parameter"],
                        "examplesUsed": ["email urgency score"],
                        "callbacks": [],
                        "promises": ["separate training from inference"],
                        "unresolvedQuestions": ["how parameters change"],
                        "retrievalsCompleted": [],
                        "listenerLoadNotes": "Two new core terms and one brief two-step calculation.",
                        "priorSectionSummary": "No prior section; this opens with the postal recognition problem.",
                        "doNotRepeat": [],
                    },
                    {
                        "afterChapter": "ch02.md",
                        "termsDefined": ["training", "inference"],
                        "examplesUsed": ["new email score"],
                        "callbacks": ["email urgency score"],
                        "promises": [],
                        "unresolvedQuestions": [],
                        "retrievalsCompleted": ["parameter in a new-envelope situation"],
                        "listenerLoadNotes": "Two new terms separated by a concrete mail-sorting reset.",
                        "priorSectionSummary": "The listener now treats parameters as adjustable settings learned from examples.",
                        "doNotRepeat": ["Do not replay the full safe-and-combination analogy."],
                    },
                ],
            },
        )
        hashes = self.chapter_hashes()
        self.write_json(
            "learning-review.json",
            {
                "schemaVersion": 2,
                "reviewedChapterSHA256": hashes,
                "structure": {
                    "reviewer": "independent-structure-reviewer",
                    "verdict": "pass",
                    "findings": [],
                },
                "blindSequentialBeginner": {
                    "reviewer": "independent-blind-beginner-listener",
                    "verdict": "pass",
                    "reviewMode": "manuscript-only-sequential",
                    "intentionMaterialsWithheld": True,
                    "chapterAssessments": [
                        {
                            "afterChapter": "ch01.md",
                            "plausibleMentalModel": "Parameters are adjustable parts learned from examples.",
                            "confusions": [],
                            "unstableTerms": ["neural network"],
                            "lostAt": [],
                        },
                        {
                            "afterChapter": "ch02.md",
                            "plausibleMentalModel": "Training changes parameters; inference uses them.",
                            "confusions": [],
                            "unstableTerms": [],
                            "lostAt": [],
                        },
                    ],
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
        self.write_json(
            "comprehension-pilot.json",
            {
                "schemaVersion": 2,
                "status": "accepted",
                "listener": "Dan Fakkeldy",
                "listeningContext": "Driving and delivering mail",
                "representativeMinutes": 12,
                "includesFirstTechnicalPassage": True,
                "audioPath": "dist/pilot.m4b",
                "audioSHA256": "a" * 64,
                "centralIdeaInOwnWords": "Training changes adjustable parameters; inference uses them on a new case.",
                "freshExampleResponse": "Teaching a sorter is training; sorting tomorrow's envelope is inference.",
                "lostAt": [],
                "humanCheckpoints": {
                    "voiceSource": {
                        "mode": "private-source-craft-analysis",
                        "profilePath": "research/voice-source-profile.md",
                        "profileSHA256": sha256(self.research / "voice-source-profile.md"),
                        "useBoundary": "craft-features-not-pastiche",
                        "rawSourceExcerptsCommitted": False,
                    },
                    "outline": {
                        "status": "approved",
                        "reviewer": "Dan Fakkeldy",
                        "evidence": "Dan approved the argument-level outline before pilot drafting.",
                        "recordedBeforePilotDraft": True,
                    },
                    "firstSection": {
                        "status": "accepted",
                        "reviewer": "Dan Fakkeldy",
                        "evidence": "Dan accepted the repaired first section as the voice target.",
                        "recordedBeforeRemainingDraft": True,
                        "voiceExemplarPath": "research/voice-exemplar.md",
                        "voiceExemplarSHA256": sha256(self.research / "voice-exemplar.md"),
                    },
                },
                "decision": {
                    "verdict": "continue",
                    "authority": "listener",
                    "evidence": "Dan explained the distinction after one road listen.",
                    "recordedBeforeFullDraft": True,
                },
            },
        )
        self.write_json(
            "revision-passes.json",
            {
                "schemaVersion": 2,
                "reviewedChapterSHA256": hashes,
                "passes": [
                    {
                        "name": "claim-traceability",
                        "job": "Check every factual claim against evidence-notes.json and evidence-notes.md.",
                        "scope": "single-job",
                        "reviewer": "evidence-reviewer",
                        "status": "pass",
                        "findings": [],
                    },
                    {
                        "name": "tightening",
                        "job": "Cut avoidable repetition and filler without changing teaching depth.",
                        "scope": "single-job",
                        "reviewer": "frontier-author",
                        "status": "pass",
                        "findings": [],
                    },
                    {
                        "name": "de-listification",
                        "job": "Replace unearned list rhythm with connected spoken prose.",
                        "scope": "single-job",
                        "reviewer": "frontier-author",
                        "status": "pass",
                        "findings": [],
                    },
                    {
                        "name": "sentence-rhythm",
                        "job": "Vary sentence and paragraph shape while preserving the approved voice.",
                        "scope": "single-job",
                        "reviewer": "frontier-author",
                        "status": "pass",
                        "findings": [],
                    },
                    {
                        "name": "ear-pass",
                        "job": "Listen to rendered prose and repair every stumble or lost thread.",
                        "scope": "single-job",
                        "reviewer": "Dan Fakkeldy",
                        "status": "pass",
                        "findings": [],
                        "renderer": "Echo",
                        "listeningContext": "Driving and delivering mail",
                        "stumbles": [],
                        "lostThreadAt": [],
                    },
                ],
            },
        )


class LearningDesignGateTests(LearningDesignFixture):
    def module(self):
        return importlib.import_module("learning_design_qc")

    def test_valid_run_writes_hash_bound_receipt(self) -> None:
        module = self.module()
        receipt_path = self.research / "learning-design-receipt.json"
        receipt = module.write_receipt(self.root, receipt_path)

        self.assertEqual(2, receipt["schemaVersion"])
        self.assertEqual("pass", receipt["status"])
        self.assertEqual(self.chapter_hashes(), receipt["chapterSHA256"])
        self.assertTrue(receipt["learningAuthority"]["negativeVerdictOverridesReceipt"])
        self.assertTrue(receipt["learningAuthority"]["receiptDoesNotCertifyTransfer"])
        self.assertEqual(receipt, module.verify_learning_receipt(self.chapters, receipt_path))

    def test_listener_can_waive_pilot_listening_without_creating_evidence(self) -> None:
        pilot = self.read_json("comprehension-pilot.json")
        pilot["status"] = "waived-by-listener"
        pilot.pop("centralIdeaInOwnWords", None)
        pilot.pop("freshExampleResponse", None)
        pilot["comprehensionEvidence"] = {
            "status": "not-collected-listener-waived",
            "waivedBy": "Dan Fakkeldy",
            "waivedAt": "2026-07-16T09:30:00-03:00",
            "reason": "The listener asked production to continue without another gate.",
        }
        pilot["validationBoundary"] = (
            "Production may continue, but this record does not claim that pilot "
            "comprehension or learning transfer was demonstrated."
        )
        pilot["decision"]["evidence"] = (
            "Dan explicitly declined another structured checkpoint and said continue."
        )
        self.write_json("comprehension-pilot.json", pilot)
        receipt_path = self.research / "learning-design-receipt.json"

        receipt = self.module().write_receipt(self.root, receipt_path)

        self.assertEqual("pass-with-listener-waiver", receipt["status"])
        self.assertEqual(
            "waived-by-listener", receipt["gates"]["humanComprehensionPilot"]
        )
        self.assertEqual(
            "not-collected-listener-waived",
            receipt["learningAuthority"]["comprehensionEvidenceStatus"],
        )
        self.assertTrue(
            receipt["learningAuthority"]["listenerWaiverDoesNotCertifyComprehension"]
        )
        self.assertEqual(
            receipt,
            self.module().verify_learning_receipt(self.chapters, receipt_path),
        )

    def test_listener_pilot_waiver_requires_an_explicit_validation_boundary(self) -> None:
        pilot = self.read_json("comprehension-pilot.json")
        pilot["status"] = "waived-by-listener"
        pilot["comprehensionEvidence"] = {
            "status": "not-collected-listener-waived",
            "waivedBy": "Dan Fakkeldy",
            "waivedAt": "2026-07-16T09:30:00-03:00",
            "reason": "The listener asked production to continue.",
        }
        self.write_json("comprehension-pilot.json", pilot)

        with self.assertRaisesRegex(ValueError, "validationBoundary"):
            self.module().validate_run(self.root)

    def test_unattended_first_listen_preserves_pending_human_authority(self) -> None:
        self.enable_unattended_first_listen()
        module = self.module()
        receipt_path = self.research / "learning-design-receipt.json"

        receipt = module.write_receipt(self.root, receipt_path)

        self.assertEqual("first-listen", receipt["status"])
        self.assertEqual("unattended-first-listen", receipt["productionMode"])
        self.assertEqual("pending", receipt["gates"]["humanComprehensionPilot"])
        self.assertEqual("human-listener-pending", receipt["learningAuthority"]["holder"])
        self.assertTrue(receipt["learningAuthority"]["negativeVerdictOverridesReceipt"])
        self.assertTrue(receipt["learningAuthority"]["receiptDoesNotCertifyTransfer"])
        self.assertEqual(receipt, module.verify_learning_receipt(self.chapters, receipt_path))

    def test_explicitly_authorized_public_first_listen_keeps_human_authority_pending(self) -> None:
        self.enable_unattended_first_listen()
        decisions_path = self.research / "unattended-decisions.json"
        decisions = self.read_json("unattended-decisions.json")
        decisions.update(
            {
                "privacy": "public-safe",
                "permissionToPublish": True,
                "deliveryIntent": "public-repository-and-listening-room-no-icloud",
                "publicationAuthorization": {
                    "status": "granted",
                    "authorizedBy": "Dan Fakkeldy",
                    "authorizedAt": "2026-07-18T12:00:00-03:00",
                    "evidence": "User explicitly authorized public publication after every non-human gate passes.",
                    "publicationStatus": "public-first-listen",
                    "disclosure": (
                        "This edition has passed package and audio checks. "
                        "The creator's full listening review is still underway."
                    ),
                },
            }
        )
        self.write_json("unattended-decisions.json", decisions)
        brief = self.read_json("learning-brief.json")
        brief["productionMode"]["decisionsSHA256"] = sha256(decisions_path)
        self.write_json("learning-brief.json", brief)

        module = self.module()
        receipt_path = self.research / "learning-design-receipt.json"
        receipt = module.write_receipt(self.root, receipt_path)

        self.assertEqual("first-listen", receipt["status"])
        self.assertEqual("pending", receipt["gates"]["humanComprehensionPilot"])
        self.assertEqual(
            "human-listener-pending", receipt["learningAuthority"]["holder"]
        )
        self.assertEqual(
            "public-first-listen", receipt["publicationAuthorization"]["status"]
        )

    def test_unattended_first_listen_requires_bound_decisions_receipt(self) -> None:
        self.enable_unattended_first_listen()
        brief = self.read_json("learning-brief.json")
        brief["productionMode"]["decisionsSHA256"] = "0" * 64
        self.write_json("learning-brief.json", brief)

        with self.assertRaisesRegex(ValueError, "decisionsSHA256"):
            self.module().validate_run(self.root)

    def test_unattended_receipt_cannot_claim_human_pilot_passed(self) -> None:
        self.enable_unattended_first_listen()
        module = self.module()
        receipt_path = self.research / "learning-design-receipt.json"
        receipt = module.write_receipt(self.root, receipt_path)
        receipt["gates"]["humanComprehensionPilot"] = "pass"
        receipt_path.write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

        with self.assertRaisesRegex(ValueError, "humanComprehensionPilot"):
            module.verify_learning_receipt(self.chapters, receipt_path)

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

        self.write_valid_records()
        outline = self.read_json("learning-outline.json")
        outline["authorization"]["source"] = "explicit-autonomous-run"
        self.write_json("learning-outline.json", outline)
        with self.assertRaisesRegex(ValueError, "human outline approval"):
            self.module().validate_run(self.root)

    def test_outline_requires_a_supported_curriculum_pattern(self) -> None:
        outline = self.read_json("learning-outline.json")
        outline.pop("curriculumPattern")
        self.write_json("learning-outline.json", outline)

        with self.assertRaisesRegex(ValueError, "outline.curriculumPattern"):
            self.module().validate_run(self.root)

    def test_evidence_notes_are_hash_bound_and_claims_are_verified(self) -> None:
        evidence = self.read_json("evidence-notes.json")
        evidence["notesSHA256"] = "0" * 64
        self.write_json("evidence-notes.json", evidence)

        with self.assertRaisesRegex(ValueError, "notesSHA256"):
            self.module().validate_run(self.root)

        self.write_valid_records()
        evidence = self.read_json("evidence-notes.json")
        evidence["claims"][0]["verificationStatus"] = "unverified"
        self.write_json("evidence-notes.json", evidence)
        with self.assertRaisesRegex(ValueError, "verificationStatus"):
            self.module().validate_run(self.root)

    def test_structured_unresolved_conflict_preserves_claim_traceability(self) -> None:
        evidence = self.read_json("evidence-notes.json")
        evidence["unresolvedConflicts"] = [
            {
                "id": "CF-01",
                "question": "Does access evidence establish experience?",
                "claimIds": ["EV-001"],
                "conflict": (
                    "The evidence supports access while competing theories "
                    "disagree about phenomenality."
                ),
                "status": "Unresolved; preserve the distinction in prose.",
            }
        ]
        self.write_json("evidence-notes.json", evidence)

        receipt = self.module().validate_run(self.root)

        self.assertEqual("pass", receipt["status"])

    def test_structured_unresolved_conflict_rejects_unknown_claim(self) -> None:
        evidence = self.read_json("evidence-notes.json")
        evidence["unresolvedConflicts"] = [
            {
                "id": "CF-01",
                "question": "Does access evidence establish experience?",
                "claimIds": ["EV-999"],
                "conflict": "The competing readings depend on an unverified claim.",
                "status": "Unresolved.",
            }
        ]
        self.write_json("evidence-notes.json", evidence)

        with self.assertRaisesRegex(ValueError, "unknown claim"):
            self.module().validate_run(self.root)

    def test_argument_outline_requires_section_jobs_claims_payoffs_and_no_repeat(self) -> None:
        outline = self.read_json("learning-outline.json")
        outline["chapters"][0]["sections"][0]["argument"] = ""
        self.write_json("learning-outline.json", outline)

        with self.assertRaisesRegex(ValueError, "argument"):
            self.module().validate_run(self.root)

        self.write_valid_records()
        outline = self.read_json("learning-outline.json")
        outline["chapters"][1]["sections"][0]["specificClaims"] = ["EV-999"]
        self.write_json("learning-outline.json", outline)
        with self.assertRaisesRegex(ValueError, "specificClaims"):
            self.module().validate_run(self.root)

    def test_road_book_requires_six_to_ten_durable_outcomes(self) -> None:
        outline = self.read_json("learning-outline.json")
        outline["durableOutcomes"] = outline["durableOutcomes"][:5]
        self.write_json("learning-outline.json", outline)

        with self.assertRaisesRegex(ValueError, "durableOutcomes"):
            self.module().validate_run(self.root)

    def test_first_edition_plus_requires_preservation_evidence(self) -> None:
        brief = self.read_json("learning-brief.json")
        brief["revisionMode"]["name"] = "first-edition-plus"
        brief["revisionMode"]["priorEditionExists"] = True
        self.write_json("learning-brief.json", brief)

        with self.assertRaisesRegex(ValueError, "revisionMode"):
            self.module().validate_run(self.root)

    def test_missing_prior_edition_exists_errors(self) -> None:
        brief = self.read_json("learning-brief.json")
        del brief["revisionMode"]["priorEditionExists"]
        self.write_json("learning-brief.json", brief)

        with self.assertRaisesRegex(ValueError, "priorEditionExists"):
            self.module().validate_run(self.root)

    def test_prior_edition_exists_true_with_new_book_name_errors(self) -> None:
        brief = self.read_json("learning-brief.json")
        brief["revisionMode"]["priorEditionExists"] = True
        brief["revisionMode"]["name"] = "new-book"
        self.write_json("learning-brief.json", brief)

        with self.assertRaisesRegex(ValueError, "previous spine"):
            self.module().validate_run(self.root)

    def test_reduced_target_requires_user_approved_scope_history(self) -> None:
        brief = self.read_json("learning-brief.json")
        old_target = brief["originalTargetWords"]
        new_target = old_target - 5
        brief["currentTargetWords"] = new_target
        brief["estimatedMinimumWords"] = new_target - 2
        brief["estimatedMaximumWords"] = new_target + 2
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

    def test_word_range_is_an_estimate_not_a_packaging_floor(self) -> None:
        brief = self.read_json("learning-brief.json")
        actual = brief["currentTargetWords"]
        brief["originalTargetWords"] = actual + 100
        brief["currentTargetWords"] = actual + 100
        brief["estimatedMinimumWords"] = actual + 90
        brief["estimatedMaximumWords"] = actual + 110
        self.write_json("learning-brief.json", brief)

        receipt = self.module().validate_run(self.root)

        self.assertFalse(receipt["wordCount"]["withinEstimatedRange"])

    def test_road_book_caps_new_core_terms_per_chapter(self) -> None:
        plans = self.read_json("chapter-plans.json")
        plans["chapters"][0]["newCoreTerms"].extend(
            [
                {"term": "weight", "problemBeforeName": "A connection needs adjustable influence."},
                {"term": "bias", "problemBeforeName": "The output needs a starting tendency."},
            ]
        )
        self.write_json("chapter-plans.json", plans)

        with self.assertRaisesRegex(ValueError, "newCoreTerms"):
            self.module().validate_run(self.root)

    def test_road_book_caps_spoken_temporary_values(self) -> None:
        plans = self.read_json("chapter-plans.json")
        plans["chapters"][0]["audioLoad"]["temporaryValues"] = 4
        self.write_json("chapter-plans.json", plans)

        with self.assertRaisesRegex(ValueError, "temporaryValues"):
            self.module().validate_run(self.root)

    def test_road_book_caps_spoken_symbolic_chains(self) -> None:
        plans = self.read_json("chapter-plans.json")
        plans["chapters"][0]["audioLoad"]["symbolicChainSteps"] = 4
        self.write_json("chapter-plans.json", plans)

        with self.assertRaisesRegex(ValueError, "symbolicChainSteps"):
            self.module().validate_run(self.root)

    def test_problem_before_name_and_real_world_grounding_are_required(self) -> None:
        coverage = self.read_json("coverage-ledger.json")
        coverage["concepts"][0]["problemBeforeName"] = ""
        self.write_json("coverage-ledger.json", coverage)

        with self.assertRaisesRegex(ValueError, "problemBeforeName"):
            self.module().validate_run(self.root)

        self.write_valid_records()
        coverage = self.read_json("coverage-ledger.json")
        coverage["concepts"][0]["realWorldApplications"] = []
        self.write_json("coverage-ledger.json", coverage)
        with self.assertRaisesRegex(ValueError, "realWorldApplications"):
            self.module().validate_run(self.root)

    def test_analogy_contract_and_retrieval_are_required(self) -> None:
        coverage = self.read_json("coverage-ledger.json")
        coverage["concepts"][0]["analogy"]["limit"] = ""
        self.write_json("coverage-ledger.json", coverage)

        with self.assertRaisesRegex(ValueError, "analogy"):
            self.module().validate_run(self.root)

        self.write_valid_records()
        coverage = self.read_json("coverage-ledger.json")
        coverage["concepts"][0]["retrievals"] = []
        self.write_json("coverage-ledger.json", coverage)
        with self.assertRaisesRegex(ValueError, "retrievals"):
            self.module().validate_run(self.root)

    def test_blind_review_is_manuscript_only_and_sequential(self) -> None:
        review = self.read_json("learning-review.json")
        review["blindSequentialBeginner"]["intentionMaterialsWithheld"] = False
        self.write_json("learning-review.json", review)

        with self.assertRaisesRegex(ValueError, "intentionMaterialsWithheld"):
            self.module().validate_run(self.root)

        self.write_valid_records()
        review = self.read_json("learning-review.json")
        review["blindSequentialBeginner"]["chapterAssessments"] = review[
            "blindSequentialBeginner"
        ]["chapterAssessments"][:1]
        self.write_json("learning-review.json", review)
        with self.assertRaisesRegex(ValueError, "chapterAssessments"):
            self.module().validate_run(self.root)

    def test_pilot_requires_road_length_and_listener_authority(self) -> None:
        pilot = self.read_json("comprehension-pilot.json")
        pilot["representativeMinutes"] = 9
        self.write_json("comprehension-pilot.json", pilot)

        with self.assertRaisesRegex(ValueError, "representativeMinutes"):
            self.module().validate_run(self.root)

        self.write_valid_records()
        pilot = self.read_json("comprehension-pilot.json")
        pilot["decision"]["authority"] = "agent"
        self.write_json("comprehension-pilot.json", pilot)
        with self.assertRaisesRegex(ValueError, "authority"):
            self.module().validate_run(self.root)

    def test_pilot_accepts_listener_verdict_without_questionnaire(self) -> None:
        pilot = self.read_json("comprehension-pilot.json")
        pilot.pop("centralIdeaInOwnWords")
        pilot.pop("freshExampleResponse")
        pilot.pop("lostAt")
        pilot["listenerNotes"] = "The pilot was clear; continue."
        self.write_json("comprehension-pilot.json", pilot)

        result = self.module().validate_run(self.root)

        self.assertIsInstance(result, dict)

    def test_a_text_package_does_not_require_rendered_pilot_audio(self) -> None:
        """The EPUB is a text artifact. Requiring pilot audio before it could be
        built made every text package depend on a full Echo build and a speech
        synthesis run."""
        pilot = self.read_json("comprehension-pilot.json")
        pilot["audioRendered"] = False
        pilot["audioPath"] = ""
        pilot["audioSHA256"] = ""
        pilot["audioNotRenderedReason"] = "Text package; narration has not run yet."
        self.write_json("comprehension-pilot.json", pilot)

        result = self.module().validate_run(self.root)

        self.assertIsInstance(result, dict)

    def test_a_not_rendered_pilot_must_not_also_claim_audio(self) -> None:
        """Relaxing the requirement must not let a record claim an audio hash it
        does not have."""
        pilot = self.read_json("comprehension-pilot.json")
        pilot["audioRendered"] = False
        pilot["audioPath"] = ""
        pilot["audioSHA256"] = "a" * 64
        pilot["audioNotRenderedReason"] = "Text package."
        self.write_json("comprehension-pilot.json", pilot)
        with self.assertRaisesRegex(ValueError, "audioSHA256 must be empty"):
            self.module().validate_run(self.root)

        self.write_valid_records()
        pilot = self.read_json("comprehension-pilot.json")
        pilot["audioRendered"] = False
        pilot["audioNotRenderedReason"] = "Text package."
        self.write_json("comprehension-pilot.json", pilot)
        with self.assertRaisesRegex(ValueError, "audioPath must be empty"):
            self.module().validate_run(self.root)

        self.write_valid_records()
        pilot = self.read_json("comprehension-pilot.json")
        pilot["audioRendered"] = False
        pilot["audioPath"] = ""
        pilot["audioSHA256"] = ""
        self.write_json("comprehension-pilot.json", pilot)
        with self.assertRaisesRegex(ValueError, "audioNotRenderedReason"):
            self.module().validate_run(self.root)

    def test_a_claimed_audio_hash_is_still_checked(self) -> None:
        """When a pilot does claim audio, the claim is validated exactly as
        before."""
        pilot = self.read_json("comprehension-pilot.json")
        pilot["audioSHA256"] = "not-a-digest"
        self.write_json("comprehension-pilot.json", pilot)
        with self.assertRaisesRegex(ValueError, "audioSHA256"):
            self.module().validate_run(self.root)

    def test_human_checkpoints_freeze_outline_and_first_section_exemplar(self) -> None:
        pilot = self.read_json("comprehension-pilot.json")
        pilot["humanCheckpoints"]["outline"]["recordedBeforePilotDraft"] = False
        self.write_json("comprehension-pilot.json", pilot)

        with self.assertRaisesRegex(ValueError, "recordedBeforePilotDraft"):
            self.module().validate_run(self.root)

        self.write_valid_records()
        pilot = self.read_json("comprehension-pilot.json")
        pilot["humanCheckpoints"]["firstSection"]["voiceExemplarSHA256"] = "0" * 64
        self.write_json("comprehension-pilot.json", pilot)
        with self.assertRaisesRegex(ValueError, "voiceExemplarSHA256"):
            self.module().validate_run(self.root)

    def test_private_voice_source_is_profiled_without_committing_excerpts(self) -> None:
        pilot = self.read_json("comprehension-pilot.json")
        pilot["humanCheckpoints"]["voiceSource"]["rawSourceExcerptsCommitted"] = True
        self.write_json("comprehension-pilot.json", pilot)

        with self.assertRaisesRegex(ValueError, "rawSourceExcerptsCommitted"):
            self.module().validate_run(self.root)

        self.write_valid_records()
        pilot = self.read_json("comprehension-pilot.json")
        pilot["humanCheckpoints"]["voiceSource"]["profileSHA256"] = "0" * 64
        self.write_json("comprehension-pilot.json", pilot)
        with self.assertRaisesRegex(ValueError, "profileSHA256"):
            self.module().validate_run(self.root)

    def test_revision_passes_are_hash_bound_and_each_has_one_job(self) -> None:
        revisions = self.read_json("revision-passes.json")
        revisions["passes"] = [
            item for item in revisions["passes"] if item["name"] != "ear-pass"
        ]
        self.write_json("revision-passes.json", revisions)

        with self.assertRaisesRegex(ValueError, "ear-pass"):
            self.module().validate_run(self.root)

        self.write_valid_records()
        revisions = self.read_json("revision-passes.json")
        revisions["passes"][0]["scope"] = "make-it-better"
        self.write_json("revision-passes.json", revisions)
        with self.assertRaisesRegex(ValueError, "single-job"):
            self.module().validate_run(self.root)

    def test_ear_pass_records_renderer_stumbles_and_lost_thread_locations(self) -> None:
        revisions = self.read_json("revision-passes.json")
        ear_pass = next(item for item in revisions["passes"] if item["name"] == "ear-pass")
        ear_pass.pop("renderer")
        self.write_json("revision-passes.json", revisions)

        with self.assertRaisesRegex(ValueError, "renderer"):
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

    def test_every_section_draft_context_carries_forward_context_and_no_repeat(self) -> None:
        continuity = self.read_json("continuity.json")
        continuity["draftContexts"][1]["previousSectionTextOrSummary"] = ""
        self.write_json("continuity.json", continuity)

        with self.assertRaisesRegex(ValueError, "previousSectionTextOrSummary"):
            self.module().validate_run(self.root)

        self.write_valid_records()
        continuity = self.read_json("continuity.json")
        continuity["draftContexts"] = continuity["draftContexts"][:1]
        self.write_json("continuity.json", continuity)
        with self.assertRaisesRegex(ValueError, "draftContexts"):
            self.module().validate_run(self.root)

    def test_listener_authorized_chapter_batch_can_cover_outline_sections(self) -> None:
        authorization = self.research / "fast-track-authorization.md"
        authorization.write_text(
            "# Fast-track authorization\n\n"
            "The listener explicitly authorized chapter-sized drafting batches.\n",
            encoding="utf-8",
        )
        continuity = self.read_json("continuity.json")
        continuity["draftContexts"] = [
            {
                "section": "ch01-batch",
                "batchSections": ["ch01-s01"],
                "fullOutlinePath": "research/learning-outline.json",
                "evidenceNotesPath": "research/evidence-notes.md",
                "styleGuidePath": "research/voice-source-profile.md",
                "previousSectionTextOrSummary": (
                    "Opening section; there is no previous section."
                ),
                "sectionJobs": [
                    "Make the recognition problem concrete before naming the mechanism."
                ],
                "mustNotRepeat": [],
                "fastTrackAuthorizationPath": "research/fast-track-authorization.md",
            },
            {
                "section": "ch02-batch",
                "batchSections": ["ch02-s01"],
                "fullOutlinePath": "research/learning-outline.json",
                "evidenceNotesPath": "research/evidence-notes.md",
                "styleGuidePath": "research/voice-source-profile.md",
                "previousSectionTextOrSummary": (
                    "Parameters are adjustable settings learned from varied handwriting."
                ),
                "sectionJobs": [
                    "Contrast changing the sorter with using the finished sorter."
                ],
                "mustNotRepeat": ["Do not redefine parameters from scratch."],
                "fastTrackAuthorizationPath": "research/fast-track-authorization.md",
            },
        ]
        self.write_json("continuity.json", continuity)

        receipt = self.module().validate_run(self.root)

        self.assertEqual("pass", receipt["status"])

    def test_chapter_batch_requires_an_in_run_authorization_artifact(self) -> None:
        continuity = self.read_json("continuity.json")
        first = continuity["draftContexts"][0]
        first["section"] = "ch01-batch"
        first["batchSections"] = ["ch01-s01"]
        first["sectionJobs"] = [first.pop("sectionJob")]
        first["fastTrackAuthorizationPath"] = "research/missing-authorization.md"
        self.write_json("continuity.json", continuity)

        with self.assertRaisesRegex(ValueError, "fastTrackAuthorizationPath"):
            self.module().validate_run(self.root)

    def test_chapter_batch_cannot_cross_chapter_boundaries(self) -> None:
        authorization = self.research / "fast-track-authorization.md"
        authorization.write_text(
            "# Fast-track authorization\n\n"
            "The listener authorized one chapter-sized batch at a time.\n",
            encoding="utf-8",
        )
        continuity = self.read_json("continuity.json")
        continuity["draftContexts"] = [
            {
                "section": "ch01-batch",
                "batchSections": ["ch01-s01", "ch02-s01"],
                "fullOutlinePath": "research/learning-outline.json",
                "evidenceNotesPath": "research/evidence-notes.md",
                "styleGuidePath": "research/voice-source-profile.md",
                "previousSectionTextOrSummary": "Opening batch.",
                "sectionJobs": [
                    "Introduce the recognition problem.",
                    "Separate training from inference.",
                ],
                "mustNotRepeat": [],
                "fastTrackAuthorizationPath": "research/fast-track-authorization.md",
            }
        ]
        self.write_json("continuity.json", continuity)

        with self.assertRaisesRegex(ValueError, "within one chapter"):
            self.module().validate_run(self.root)

    def test_core_concept_requires_a_complete_explanation_path(self) -> None:
        coverage = self.read_json("coverage-ledger.json")
        coverage["concepts"][0]["mechanism"] = ""
        self.write_json("coverage-ledger.json", coverage)

        with self.assertRaisesRegex(ValueError, "mechanism"):
            self.module().validate_run(self.root)

    def test_reviews_must_pass_and_match_final_chapter_hashes(self) -> None:
        review = self.read_json("learning-review.json")
        review["blindSequentialBeginner"]["verdict"] = "fail"
        self.write_json("learning-review.json", review)
        with self.assertRaisesRegex(ValueError, "blindSequentialBeginner"):
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


class PatchRevisionPreservationTests(LearningDesignFixture):
    def module(self):
        return importlib.import_module("learning_design_qc")

    def test_patch_revision_passes_when_unnamed_chapters_are_unchanged(self) -> None:
        previous_hashes = self.chapter_hashes()
        (self.chapters / "ch02.md").write_text(
            "## Chapter 2 - Training and Inference (revised)\n\n"
            "Training changes parameters. Inference uses those parameters on new input.\n",
            encoding="utf-8",
        )

        current = self.module().verify_patch_revision_preserved_chapters(
            self.chapters, previous_hashes, ["ch02.md"]
        )

        self.assertEqual(previous_hashes["ch01.md"], current["ch01.md"])
        self.assertNotEqual(previous_hashes["ch02.md"], current["ch02.md"])

    def test_patch_revision_fails_when_unnamed_chapter_mutates(self) -> None:
        previous_hashes = self.chapter_hashes()
        (self.chapters / "ch01.md").write_text(
            "## Chapter 1 - What a Network Does (silently changed)\n\n"
            "A neural network maps input values to an output through learned parameters.\n",
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ValueError, "ch01.md"):
            self.module().verify_patch_revision_preserved_chapters(
                self.chapters, previous_hashes, ["ch02.md"]
            )

    def test_patch_revision_fails_when_unnamed_chapter_is_deleted(self) -> None:
        previous_hashes = self.chapter_hashes()
        (self.chapters / "ch01.md").unlink()

        with self.assertRaisesRegex(ValueError, "removed chapter ch01.md"):
            self.module().verify_patch_revision_preserved_chapters(
                self.chapters, previous_hashes, ["ch02.md"]
            )

    def test_patch_revision_rejects_unknown_chapter_in_change_list(self) -> None:
        previous_hashes = self.chapter_hashes()

        with self.assertRaisesRegex(ValueError, "unknown chapter"):
            self.module().verify_patch_revision_preserved_chapters(
                self.chapters, previous_hashes, ["ch99.md"]
            )

    def test_patch_revision_does_not_evaluate_named_chapter_prose(self) -> None:
        previous_hashes = self.chapter_hashes()
        (self.chapters / "ch02.md").write_text("lowercase, no punctuation, terrible prose", encoding="utf-8")

        current = self.module().verify_patch_revision_preserved_chapters(
            self.chapters, previous_hashes, ["ch02.md"]
        )

        self.assertIn("ch02.md", current)


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

    def test_cli_builds_an_explicit_nonpackage_learning_pilot(self) -> None:
        output = self.root / "pilot"
        command = self.cli_base(output)
        command[command.index("--slug") + 1] = "learning-gate-fixture-pilot"

        result = subprocess.run(
            command + ["--learning-pilot"], capture_output=True, text=True, check=False
        )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("PILOT ONLY", result.stdout)
        self.assertTrue((output / "learning-gate-fixture-pilot.epub").is_file())

    def test_cli_rejects_a_pilot_slug_that_could_be_mistaken_for_a_book(self) -> None:
        output = self.root / "ambiguous-pilot"

        result = subprocess.run(
            self.cli_base(output) + ["--learning-pilot"],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("pilot builds require --slug ending in -pilot", result.stderr)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
