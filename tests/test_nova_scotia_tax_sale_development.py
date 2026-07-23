import ast
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import unittest
import zipfile
import re


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKET_ROOT = REPO_ROOT / "docs/nova-scotia-tax-sale-book"
RESEARCH_ROOT = PACKET_ROOT / "research"
MAP_ROOT = PACKET_ROOT / "maps"
LISTING_PATH = MAP_ROOT / "data/inverness-tax-sale-2026-08-11.json"
METADATA_PATH = MAP_ROOT / "build-metadata.json"
PROJECT_PATH = MAP_ROOT / "qgis/inverness-tax-sale-2026-08-11.qgz"
ATLAS_ROOT = MAP_ROOT / "atlas-prototypes"
ATLAS_SPEC_PATH = ATLAS_ROOT / "atlas-prototype-specs.json"
ATLAS_RECEIPT_PATH = ATLAS_ROOT / "render-receipt.json"
ATLAS_APPROVAL_PATH = ATLAS_ROOT / "human-visual-approval.json"
MUNICIPAL_SOURCE_REGISTER = PACKET_ROOT / "research/municipal-map-source-register.json"
NS_MARKS_PROMPT = PACKET_ROOT / "research/ns-marks-multi-municipality-map-prompt.md"
ATTRIBUTION = (
    "Contains information obtained under license from the Province of Nova "
    "Scotia which is provided without warranty or liability for errors or "
    "omissions."
)
REVIEW_REVISION_PATH = RESEARCH_ROOT / "review-revision-receipt.json"


class NovaScotiaTaxSaleDevelopmentTests(unittest.TestCase):
    def assert_checkpoint_or_review_revision(
        self, chapter_path: Path, checkpoint_sha256: str
    ) -> None:
        actual_sha256 = hashlib.sha256(chapter_path.read_bytes()).hexdigest()
        if actual_sha256 == checkpoint_sha256:
            return

        revision = json.loads(REVIEW_REVISION_PATH.read_text(encoding="utf-8"))
        chapter = chapter_path.name
        self.assertEqual(
            revision["status"], "governed-final-publication-authorized"
        )
        self.assertEqual(
            revision["baseApprovedChapterSHA256"][chapter], checkpoint_sha256
        )
        self.assertEqual(
            revision["candidateChapterSHA256"][chapter], actual_sha256
        )
        self.assertIn(chapter, revision["changedChapters"])
        self.assertTrue(revision["gates"]["manuscriptTextApproved"])
        self.assertTrue(revision["gates"]["narrationAccepted"])

    def test_learning_evidence_matches_validator_contract(self) -> None:
        evidence_path = RESEARCH_ROOT / "evidence-notes.json"
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))

        self.assertEqual(
            evidence["notesSHA256"],
            hashlib.sha256(
                (RESEARCH_ROOT / "evidence-notes.md").read_bytes()
            ).hexdigest(),
        )
        self.assertTrue(evidence["claims"])
        for claim in evidence["claims"]:
            self.assertEqual(claim["verificationStatus"], "verified")
            self.assertTrue(claim["claim"])
            self.assertTrue(claim["verificationNote"])

    def test_scope_receipt_preserves_original_target_and_verbatim_quotes(self) -> None:
        brief = json.loads(
            (RESEARCH_ROOT / "learning-brief.json").read_text(encoding="utf-8")
        )

        self.assertEqual(brief["originalTargetWords"], 22000)
        self.assertEqual(brief["currentTargetWords"], 46200)
        self.assertTrue(brief["draftingStarted"])
        self.assertEqual(len(brief["scopeHistory"]), 11)
        for decision in brief["scopeHistory"]:
            self.assertRegex(decision["recordedAt"], r"^2026-07-(18|19|20|21)T")
            self.assertTrue(decision["verbatimQuote"])
            self.assertIn(decision["verbatimQuote"], decision["evidence"])

        self.assertIn(
            "51 figures direction",
            brief["scopeHistory"][-3]["verbatimQuote"],
        )
        self.assertEqual(
            brief["scopeHistory"][-2]["verbatimQuote"],
            "I meant the epub text was ready to publish.",
        )
        self.assertEqual(
            brief["scopeHistory"][-1]["verbatimQuote"],
            "i'm going to go with image 1",
        )

    def test_epub_text_approval_and_review_revision_are_separately_bound(self) -> None:
        authorization = json.loads(
            (RESEARCH_ROOT / "publication-authorization.json").read_text(
                encoding="utf-8"
            )
        )
        chapter_dir = PACKET_ROOT / "chapters"
        actual_hashes = {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(chapter_dir.glob("ch*.md"))
        }

        self.assertEqual(authorization["classification"], "public-safe")
        self.assertEqual(authorization["manuscriptTextApproval"]["status"], "approved")
        approved_hashes = authorization["manuscriptTextApproval"][
            "reviewedChapterSHA256"
        ]
        revision = json.loads(REVIEW_REVISION_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            revision["basePublicationAuthorizationSHA256"],
            hashlib.sha256(
                (RESEARCH_ROOT / "publication-authorization.json").read_bytes()
            ).hexdigest(),
        )
        self.assertEqual(revision["baseApprovedChapterSHA256"], approved_hashes)
        self.assertEqual(revision["candidateChapterSHA256"], actual_hashes)
        self.assertEqual(
            set(revision["changedChapters"]),
            {
                chapter
                for chapter, approved_sha256 in approved_hashes.items()
                if actual_hashes[chapter] != approved_sha256
            },
        )
        self.assertEqual(
            revision["status"], "governed-final-publication-authorized"
        )
        self.assertTrue(revision["gates"]["manuscriptTextApproved"])
        self.assertTrue(revision["gates"]["narrationAccepted"])
        self.assertTrue(revision["gates"]["figuresAccepted"])
        self.assertFalse(revision["gates"]["videoEditionAccepted"])
        self.assertTrue(revision["privacyBoundary"]["privateSourceExcluded"])
        self.assertTrue(revision["privacyBoundary"]["privateFactsExcluded"])
        self.assertTrue(
            authorization["publicationAuthorization"]["permissionToPublish"]
        )
        self.assertEqual(
            authorization["boundaries"]["coverSelection"],
            "candidate-1-packet-lifts-selected",
        )
        self.assertEqual(authorization["boundaries"]["audioListeningStatus"], "pending")

    def test_cover_review_has_three_complete_pairs_and_user_selection(self) -> None:
        covers_root = PACKET_ROOT / "covers"
        review = json.loads(
            (covers_root / "render-review.json").read_text(encoding="utf-8")
        )
        candidate_dirs = sorted(covers_root.glob("candidate-[1-3]"))

        self.assertEqual(len(candidate_dirs), 3)
        self.assertEqual(review["status"], "pair-selected")
        self.assertEqual(
            review["humanPairSelection"]["selectedCandidate"], "packet-lifts"
        )
        self.assertEqual(
            review["humanPairSelection"]["verbatimEvidence"],
            "i'm going to go with image 1",
        )

        selection = json.loads(
            (covers_root / "cover-selection.json").read_text(encoding="utf-8")
        )
        self.assertEqual(selection["candidate"]["id"], "packet-lifts")
        self.assertEqual(selection["selection_source"], "user")
        self.assertEqual(selection["privacy"]["classification"], "public-safe")
        self.assertTrue(selection["privacy"]["permission_to_publish"])

        reviewed = {item["id"]: item for item in review["candidates"]}
        self.assertEqual(
            set(reviewed),
            {"packet-lifts", "raised-card", "layers-of-uncertainty"},
        )
        for candidate_dir in candidate_dirs:
            portrait = json.loads(
                (candidate_dir / "cover-render.json").read_text(encoding="utf-8")
            )
            square = json.loads(
                (candidate_dir / "m4b-cover-render.json").read_text(encoding="utf-8")
            )
            candidate_id = portrait["candidate"]["id"]

            portrait_spec = json.loads(
                (candidate_dir / "cover-spec.json").read_text(encoding="utf-8")
            )
            square_spec = json.loads(
                (candidate_dir / "m4b-cover-spec.json").read_text(encoding="utf-8")
            )
            self.assertEqual(portrait_spec["schema_version"], 2)
            self.assertEqual(square_spec["schema_version"], 2)
            self.assertEqual(square["candidate"]["id"], candidate_id)
            self.assertEqual(portrait["source_art_sha256"], square["source_art_sha256"])
            self.assertEqual(portrait["dimensions"], [1600, 2560])
            self.assertEqual(square["dimensions"], [2400, 2400])
            self.assertEqual(
                reviewed[candidate_id]["sourceArtSHA256"],
                portrait["source_art_sha256"],
            )
            self.assertEqual(
                reviewed[candidate_id]["portraitSHA256"],
                portrait["output_sha256"],
            )
            self.assertEqual(
                reviewed[candidate_id]["squareSHA256"],
                square["output_sha256"],
            )
            self.assertTrue((candidate_dir / "brief.md").exists())

    def test_governed_final_package_tracks_current_text_figures_and_audio(self) -> None:
        public_root = REPO_ROOT / "books/beyond-the-tax-sale-packet"
        publication = json.loads(
            (public_root / "publication.json").read_text(encoding="utf-8")
        )
        learning_receipt = json.loads(
            (RESEARCH_ROOT / "learning-design-receipt.json").read_text(encoding="utf-8")
        )
        authorization = json.loads(
            (RESEARCH_ROOT / "publication-authorization.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(publication["publicationStatus"], "governed-final")
        self.assertEqual(publication["humanListeningStatus"], "accepted")
        self.assertTrue(publication["permissionToPublish"])
        self.assertEqual(
            publication["audioStatus"], "published-current-54-figure-edition"
        )
        self.assertTrue(publication["artifacts"]["m4b"]["manuscriptParity"])
        self.assertTrue(publication["artifacts"]["alignment"]["manuscriptParity"])
        self.assertEqual(publication["figureCount"], 54)
        self.assertEqual(
            publication["disclosure"],
            "This edition has passed package and audio checks. The creator "
            "completed the full listening review and approved this edition for "
            "publication.",
        )
        self.assertTrue((public_root / "beyond-the-tax-sale-packet.m4b").is_file())
        self.assertTrue(
            (public_root / "beyond-the-tax-sale-packet.alignment.json").is_file()
        )

        for artifact in publication["artifacts"].values():
            path = public_root / artifact["file"]
            self.assertTrue(path.is_file())
            self.assertEqual(
                artifact["sha256"], hashlib.sha256(path.read_bytes()).hexdigest()
            )

        self.assertEqual(learning_receipt["status"], "pass")
        self.assertEqual(
            learning_receipt["chapterSHA256"],
            authorization["manuscriptTextApproval"]["reviewedChapterSHA256"],
        )
        with zipfile.ZipFile(public_root / "beyond-the-tax-sale-packet.epub") as epub:
            self.assertEqual(
                hashlib.sha256(epub.read("OEBPS/cover.png")).hexdigest(),
                publication["artifacts"]["portraitCover"]["sha256"],
            )
            self.assertEqual(
                len(
                    [
                        name
                        for name in epub.namelist()
                        if name.startswith("OEBPS/images/")
                    ]
                ),
                54,
            )

    def test_outline_gate_records_map_revision_approval_for_pilot_only(self) -> None:
        outline = json.loads(
            (RESEARCH_ROOT / "learning-outline.json").read_text(encoding="utf-8")
        )
        pilot = json.loads(
            (RESEARCH_ROOT / "comprehension-pilot.json").read_text(encoding="utf-8")
        )
        approval_quote = (
            "I approve the revised twelve-chapter outline and forty-figure "
            "visual direction for pilot development."
        )

        approval = (
            "The new map warrants one major Chapter 5 rewrite plus targeted "
            "changes to Chapters 2, 4, 6, 7, 9, and 13—let’s work on that with "
            "the 51 figures direction."
        )

        self.assertEqual(outline["authorization"]["status"], "approved")
        self.assertEqual(outline["authorization"]["requestedBy"], "Dan Fakkeldy")
        self.assertEqual(outline["authorization"]["approvedBy"], "Dan Fakkeldy")
        self.assertEqual(outline["authorization"]["verbatimQuote"], approval)
        self.assertEqual(outline["authorization"]["evidence"], approval)
        self.assertEqual(outline["authorization"]["approvalScope"], "pilot-development")
        self.assertEqual(
            outline["authorization"]["scope"],
            "revised-thirteen-chapter-outline-and-fifty-one-figure-direction",
        )
        prior = outline["authorization"]["priorAuthorization"]
        self.assertEqual(prior["status"], "approved")
        self.assertEqual(prior["approvedBy"], "Dan Fakkeldy")
        self.assertRegex(
            prior["approvedAt"],
            r"^2026-07-19T\d{2}:\d{2}:\d{2}-03:00$",
        )
        self.assertEqual(prior["verbatimQuote"], approval_quote)
        self.assertEqual(prior["evidence"], approval_quote)
        self.assertEqual(prior["scope"], "pilot-development")
        excluded_actions = " ".join(outline["authorization"]["doesNotAuthorize"])
        self.assertIn("full manuscript", excluded_actions)
        self.assertIn("publication", excluded_actions)

        outline_checkpoint = pilot["humanCheckpoints"]["outline"]
        self.assertEqual(outline_checkpoint["status"], "approved")
        self.assertEqual(outline_checkpoint["reviewer"], "Dan Fakkeldy")
        self.assertEqual(outline_checkpoint["evidence"], approval)
        self.assertEqual(
            outline_checkpoint["priorApproval"]["evidence"], approval_quote
        )
        self.assertTrue(outline_checkpoint["recordedBeforePilotDraft"])

    def test_required_planning_handoff_artifacts_exist(self) -> None:
        conversation = (RESEARCH_ROOT / "conversation-log.md").read_text(
            encoding="utf-8"
        )
        handoff = (PACKET_ROOT / "handoff-packet.md").read_text(encoding="utf-8")
        pronunciation = json.loads(
            (RESEARCH_ROOT / "pronunciation-plan.json").read_text(encoding="utf-8")
        )

        terms = {entry["term"] for entry in pronunciation["terms"]}
        self.assertTrue(
            {
                "Inverness",
                "Pictou",
                "AAN",
                "PID",
                "NSPRD",
                "CBRM",
                "HST",
                "Municipal Government Act",
            }
            <= terms
        )
        self.assertIn("approved for pilot development", handoff)
        self.assertIn(
            "I approve the revised twelve-chapter outline and forty-figure",
            conversation,
        )
        self.assertIn("Let's add a chapter about using this resource", conversation)

    def test_pronunciation_plan_forms_exist_in_declared_chapters(self) -> None:
        pronunciation = json.loads(
            (RESEARCH_ROOT / "pronunciation-plan.json").read_text(encoding="utf-8")
        )

        for entry in pronunciation["terms"]:
            declared_text = "\n".join(
                (PACKET_ROOT / "chapters" / chapter).read_text(encoding="utf-8")
                for chapter in entry["expectedChapters"]
            ).casefold()
            for form in [entry["term"], *entry["variants"]]:
                self.assertIn(
                    form.casefold(),
                    declared_text,
                    f"{form!r} is absent from its declared pronunciation chapters",
                )

        pictou = next(item for item in pronunciation["terms"] if item["term"] == "Pictou")
        self.assertEqual(pictou["source"], "listener")
        self.assertEqual(pictou["variants"], [])
        self.assertEqual(
            pictou["spokenCandidates"],
            ["PICK-toe"],
        )

    def test_audiobook_acceptance_packet_preserves_separate_gates(self) -> None:
        audit = (RESEARCH_ROOT / "audiobook-candidate-audit.md").read_text(
            encoding="utf-8"
        )
        checklist = (PACKET_ROOT / "audiobook-acceptance-checklist.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("cannot be promoted byte-for-byte", audit)
        self.assertIn("does not reopen or change the approved manuscript", audit)
        self.assertIn(
            "40049b5e7bac13657d5b1417fc1dbac25f6c3d02587c3c484e2e49dc73003bd0",
            audit,
        )
        self.assertIn("unattended-first-listen", audit)
        self.assertIn("ACCEPT FULL AUDIO", checklist)
        self.assertIn("REVISE AUDIO", checklist)
        self.assertIn("REJECT AUDIO", checklist)
        self.assertIn("second-device proof of the public edition", checklist)
        self.assertIn("video-edition production", checklist)
        self.assertIn("public-first-listen", checklist)
        self.assertIn("notice → parcel → context → unknowns → handoff", checklist)
        self.assertIn("Property Online", checklist)

    def test_audiobook_candidate_receipt_binds_machine_and_human_boundaries(
        self,
    ) -> None:
        receipt = json.loads(
            (RESEARCH_ROOT / "audiobook-candidate-receipt.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(
            receipt["status"],
            "public-first-listen-authorized-full-audio-verdict-pending",
        )
        self.assertTrue(receipt["permissionToPublishAudiobook"])
        self.assertEqual(
            receipt["publicationAuthorization"]["status"], "public-first-listen"
        )
        self.assertEqual(
            receipt["source"]["epubSHA256"],
            "40049b5e7bac13657d5b1417fc1dbac25f6c3d02587c3c484e2e49dc73003bd0",
        )
        self.assertTrue(receipt["source"]["canonicalChaptersUnchanged"])
        self.assertFalse(receipt["source"]["propertyOnlineMaterialIncluded"])
        self.assertEqual(receipt["narration"]["voice"], "am_michael")
        self.assertEqual(
            (RESEARCH_ROOT / "approved-echo-pronunciation-sha.txt")
            .read_text(encoding="utf-8")
            .strip(),
            receipt["narration"]["echoSourceSHA"],
        )
        self.assertEqual(receipt["artifacts"]["audiobook"]["chapterCount"], 13)
        self.assertEqual(
            receipt["artifacts"]["audiobook"]["sha256"],
            "f675ba1fde72aed5f7885931289f2d0dbb1b94e361f063012ab5bacbaeb1d4b8",
        )
        self.assertEqual(receipt["artifacts"]["alignment"]["anchorCount"], 612)
        self.assertEqual(receipt["artifacts"]["alignment"]["wordTimedAnchorCount"], 324)
        self.assertEqual(
            receipt["artifacts"]["pronunciationAudit"]["diagnosticCount"], 0
        )
        self.assertEqual(
            receipt["artifacts"]["pronunciationAudit"]["pictouDecisionCount"], 5
        )
        self.assertEqual(
            receipt["artifacts"]["pronunciationAudit"]["pictouIPA"], "pˈɪktO"
        )
        self.assertEqual(
            receipt["artifacts"]["pronunciationAudit"]["rejectedPictouIPACount"],
            0,
        )
        self.assertEqual(receipt["checks"]["fullAudioDecode"], "pass")
        self.assertEqual(
            receipt["humanGates"]["fullAudioListening"],
            "pending-replacement-verdict",
        )
        self.assertEqual(
            receipt["humanGates"]["audiobookPublication"],
            "authorized-public-first-listen",
        )
        self.assertTrue(
            (
                REPO_ROOT
                / "books/beyond-the-tax-sale-packet/beyond-the-tax-sale-packet.m4b"
            ).is_file()
        )

    def test_54_figure_publication_receipt_binds_positive_listen_and_touquoy_boundary(
        self,
    ) -> None:
        receipt = json.loads(
            (
                RESEARCH_ROOT
                / "audiobook-54-figure-publication-receipt.json"
            ).read_text(encoding="utf-8")
        )

        self.assertEqual(
            receipt["status"], "governed-final-publication-authorized"
        )
        self.assertEqual(receipt["humanListeningVerdict"]["status"], "accepted")
        self.assertEqual(
            receipt["humanListeningVerdict"]["boundM4BSHA256"],
            "f56220fea72c767a225a1538ad70c0e160763830bd15bb9bc2cb9f0fe474c505",
        )
        self.assertEqual(receipt["publicationAuthorization"]["status"], "granted")
        self.assertIn(
            "kinnokilabs.com/taxsale",
            receipt["publicationAuthorization"]["destinations"],
        )
        self.assertEqual(
            receipt["touquoyBoundary"]["status"],
            "rendered-passage-accepted-in-context-canonical-pronunciation-unverified",
        )
        self.assertEqual(receipt["artifacts"]["epub"]["figureCount"], 54)
        self.assertEqual(receipt["checks"]["humanFullListen"], "accepted")

    def test_negative_pictou_verdict_blocks_exact_candidate_without_reopening_text(
        self,
    ) -> None:
        verdicts = json.loads(
            (RESEARCH_ROOT / "audiobook-human-listening-verdicts.json").read_text(
                encoding="utf-8"
            )
        )
        verdict = verdicts["verdicts"][-1]

        self.assertEqual(
            verdicts["status"],
            "public-first-listen-authorized-human-verdict-pending",
        )
        self.assertEqual(
            verdicts["publicationAuthorization"]["status"], "public-first-listen"
        )
        self.assertEqual(verdict["decision"], "revise-audio")
        self.assertEqual(verdict["finding"]["term"], "Pictou")
        self.assertEqual(verdict["finding"]["heard"], "picktoau")
        self.assertEqual(verdict["finding"]["expected"], "PICK-toe")
        self.assertEqual(verdict["finding"]["rejectedRendererIPA"], "pˈɪktaʊ")
        self.assertEqual(verdict["finding"]["targetRendererIPA"], "pˈɪktO")
        self.assertEqual(
            verdict["boundArtifacts"]["audiobookSHA256"],
            "f117bb2016b2b7bc58e900130a03b37d66452afff7e6a9ac0f81d1816dd706ec",
        )
        replacement = verdicts["replacementCandidate"]
        self.assertEqual(
            replacement["audiobookSHA256"],
            "f675ba1fde72aed5f7885931289f2d0dbb1b94e361f063012ab5bacbaeb1d4b8",
        )
        self.assertEqual(replacement["pictouEvidence"]["occurrenceCount"], 5)
        self.assertEqual(replacement["pictouEvidence"]["selectedIPA"], "pˈɪktO")
        self.assertEqual(replacement["pictouEvidence"]["rejectedIPACount"], 0)
        self.assertEqual(replacement["humanPronunciationVerdict"], "pending")
        self.assertFalse(
            verdicts["frozenInputs"]["canonicalManuscriptRevisionAuthorized"]
        )
        self.assertFalse(verdicts["frozenInputs"]["selectedCoverRevisionAuthorized"])

    def test_first_section_voice_acceptance_binds_exact_candidate(self) -> None:
        continuity = json.loads(
            (RESEARCH_ROOT / "continuity.json").read_text(encoding="utf-8")
        )
        pilot = json.loads(
            (RESEARCH_ROOT / "comprehension-pilot.json").read_text(encoding="utf-8")
        )
        pilot_readme = (PACKET_ROOT / "pilot/README.md").read_text(encoding="utf-8")
        candidate_path = PACKET_ROOT / "pilot/first-section-candidate.md"
        exemplar_path = RESEARCH_ROOT / "voice-exemplar.md"
        candidate = candidate_path.read_text(encoding="utf-8")

        self.assertEqual(len(continuity["checkpoints"]), 13)
        self.assertEqual(len(continuity["draftContexts"]), 28)
        context = next(
            item
            for item in continuity["draftContexts"]
            if item["section"] == "ch01-s01"
        )
        self.assertEqual(context["section"], "ch01-s01")
        self.assertEqual(context["specificClaims"], ["OPS-004", "DATA-002", "DATA-005"])
        self.assertEqual(context["status"], "accepted-and-promoted-to-canonical")

        checkpoint = pilot["humanCheckpoints"]["firstSection"]
        self.assertEqual(checkpoint["status"], "accepted")
        self.assertEqual(checkpoint["reviewer"], "Dan Fakkeldy")
        self.assertEqual(checkpoint["evidence"], "Let’s go for the voice.")
        self.assertTrue(checkpoint["recordedBeforeRemainingDraft"])
        self.assertEqual(candidate_path.read_bytes(), exemplar_path.read_bytes())
        self.assertEqual(
            checkpoint["voiceExemplarSHA256"],
            hashlib.sha256(exemplar_path.read_bytes()).hexdigest(),
        )

        self.assertIn("accepted", pilot_readme.lower())
        self.assertIn("14:27", pilot_readme)
        self.assertTrue(pilot["audioRendered"])
        self.assertEqual(
            pilot["audioSHA256"],
            "c94570d369b1c5f3842f111f151a9e4bb880db2d84ceeed86f3cfed44c974f1c",
        )
        self.assertGreaterEqual(pilot["actualDurationSeconds"], 600)
        self.assertLessEqual(pilot["actualDurationSeconds"], 900)
        self.assertEqual(pilot["render"]["pronunciationAuditStatus"], "clean")
        self.assertEqual(pilot["status"], "accepted")
        self.assertEqual(pilot["decision"]["verdict"], "continue")
        self.assertEqual(pilot["decision"]["evidence"], "continue")
        self.assertTrue(pilot["decision"]["recordedBeforeFullDraft"])
        self.assertEqual(pilot["decision"]["audioSHA256"], pilot["audioSHA256"])
        self.assertTrue(candidate.startswith("## Chapter 1 — The Last Scene First"))
        self.assertGreaterEqual(len(candidate.split()), 800)
        self.assertLessEqual(len(candidate.split()), 1500)
        self.assertNotIn("![", candidate)
        self.assertNotRegex(
            candidate.lower(),
            r"tattoo this|burn this into|let that land|the honest answer|the whole point",
        )

        technical = next(
            item
            for item in continuity["draftContexts"]
            if item["section"] == "ch01-s02"
        )
        technical_path = PACKET_ROOT / technical["draftPath"]
        self.assertEqual(
            technical["status"], "accepted-pilot-passage-promoted-to-canonical"
        )
        self.assertEqual(technical["wordCount"], 1042)
        self.assertEqual(
            technical["draftSHA256"],
            hashlib.sha256(technical_path.read_bytes()).hexdigest(),
        )
        self.assertEqual(
            technical["voiceExemplarSHA256"],
            checkpoint["voiceExemplarSHA256"],
        )

        canonical_path = PACKET_ROOT / "chapters/ch01.md"
        canonical = canonical_path.read_text(encoding="utf-8")
        expected = (
            candidate.rstrip("\n")
            + "\n\n"
            + technical_path.read_text(encoding="utf-8").rstrip("\n")
            + "\n"
        )
        self.assertNotEqual(canonical, expected)
        chapter_checkpoint = continuity["checkpoints"][0]
        self.assertEqual(chapter_checkpoint["chapter"], "ch01")
        self.assertFalse(chapter_checkpoint["sourceSectionsPromotedExactly"])
        self.assertTrue(chapter_checkpoint["acceptedSourceSectionsPreservedSeparately"])
        self.assertEqual(
            chapter_checkpoint["editorialReviewPath"], "research/editorial-review.md"
        )
        self.assert_checkpoint_or_review_revision(
            canonical_path, chapter_checkpoint["draftSHA256"]
        )

        chapter_two_path = PACKET_ROOT / "chapters/ch02.md"
        chapter_two_checkpoint = continuity["checkpoints"][1]
        self.assertEqual(chapter_two_checkpoint["chapter"], "ch02")
        self.assertEqual(chapter_two_checkpoint["wordCount"], 2977)
        self.assert_checkpoint_or_review_revision(
            chapter_two_path, chapter_two_checkpoint["draftSHA256"]
        )
        chapter_two_contexts = {
            item["section"]: item
            for item in continuity["draftContexts"]
            if item["section"].startswith("ch02-")
        }
        self.assertEqual(set(chapter_two_contexts), {"ch02-s01", "ch02-s02"})
        self.assertTrue(
            all(
                item["status"] == "canonical-section-drafted"
                and item["recordedBeforeDraft"]
                for item in chapter_two_contexts.values()
            )
        )

        chapter_three_path = PACKET_ROOT / "chapters/ch03.md"
        chapter_three_checkpoint = continuity["checkpoints"][2]
        self.assertEqual(chapter_three_checkpoint["chapter"], "ch03")
        self.assertEqual(chapter_three_checkpoint["wordCount"], 1929)
        self.assert_checkpoint_or_review_revision(
            chapter_three_path, chapter_three_checkpoint["draftSHA256"]
        )
        chapter_three_contexts = {
            item["section"]: item
            for item in continuity["draftContexts"]
            if item["section"].startswith("ch03-")
        }
        self.assertEqual(set(chapter_three_contexts), {"ch03-s01", "ch03-s02"})
        self.assertTrue(
            all(
                item["status"] == "canonical-section-drafted"
                and item["recordedBeforeDraft"]
                for item in chapter_three_contexts.values()
            )
        )

        chapter_four_path = PACKET_ROOT / "chapters/ch04.md"
        chapter_four_checkpoint = continuity["checkpoints"][3]
        self.assertEqual(chapter_four_checkpoint["chapter"], "ch04")
        self.assertEqual(chapter_four_checkpoint["wordCount"], 2427)
        self.assert_checkpoint_or_review_revision(
            chapter_four_path, chapter_four_checkpoint["draftSHA256"]
        )
        chapter_four_contexts = {
            item["section"]: item
            for item in continuity["draftContexts"]
            if item["section"].startswith("ch04-")
        }
        self.assertEqual(set(chapter_four_contexts), {"ch04-s01", "ch04-s02"})
        self.assertTrue(
            all(
                item["status"] == "canonical-section-drafted"
                and item["recordedBeforeDraft"]
                for item in chapter_four_contexts.values()
            )
        )

        chapter_five_path = PACKET_ROOT / "chapters/ch05.md"
        chapter_five = chapter_five_path.read_text(encoding="utf-8")
        chapter_five_checkpoint = continuity["checkpoints"][4]
        self.assertEqual(chapter_five_checkpoint["chapter"], "ch05")
        self.assertEqual(chapter_five_checkpoint["wordCount"], 3031)
        self.assert_checkpoint_or_review_revision(
            chapter_five_path, chapter_five_checkpoint["draftSHA256"]
        )
        chapter_five_contexts = {
            item["section"]: item
            for item in continuity["draftContexts"]
            if item["section"].startswith("ch05-")
        }
        self.assertEqual(set(chapter_five_contexts), {"ch05-s01", "ch05-s02"})
        self.assertTrue(
            all(
                item["status"] == "canonical-section-drafted"
                and item["recordedBeforeDraft"]
                for item in chapter_five_contexts.values()
            )
        )
        self.assertEqual(
            chapter_five_checkpoint["method"],
            ["notice", "parcel", "context", "unknowns", "handoff"],
        )
        self.assertIn("current or historical mode", chapter_five)
        self.assertIn("not a recommendation", chapter_five)
        self.assertIn("A Small Find, and a Larger Property Question", chapter_five)
        self.assertIn("found a little colour", chapter_five)
        self.assertIn("connected with or incidental to one", chapter_five)
        self.assertIn("Touquoy did later produce gold", chapter_five)
        self.assertIn("neither a bonus nor an automatic rejection", chapter_five)
        self.assertIn("leaving the brook unnamed", chapter_five)

        chapter_six_path = PACKET_ROOT / "chapters/ch06.md"
        chapter_six = chapter_six_path.read_text(encoding="utf-8")
        chapter_six_checkpoint = continuity["checkpoints"][5]
        self.assertEqual(chapter_six_checkpoint["chapter"], "ch06")
        self.assertEqual(chapter_six_checkpoint["wordCount"], 2355)
        self.assert_checkpoint_or_review_revision(
            chapter_six_path, chapter_six_checkpoint["draftSHA256"]
        )
        chapter_six_contexts = {
            item["section"]: item
            for item in continuity["draftContexts"]
            if item["section"].startswith("ch06-")
        }
        self.assertEqual(set(chapter_six_contexts), {"ch06-s01", "ch06-s02"})
        self.assertTrue(
            all(
                item["status"] == "canonical-section-drafted"
                and item["recordedBeforeDraft"]
                for item in chapter_six_contexts.values()
            )
        )
        self.assertIn("right-of-way", chapter_six)
        self.assertIn("road frontage", chapter_six)
        self.assertIn("zoning", chapter_six)
        self.assertIn("rational no", chapter_six)

        chapter_seven_path = PACKET_ROOT / "chapters/ch07.md"
        chapter_seven = chapter_seven_path.read_text(encoding="utf-8")
        chapter_seven_checkpoint = continuity["checkpoints"][6]
        self.assertEqual(chapter_seven_checkpoint["chapter"], "ch07")
        self.assertEqual(chapter_seven_checkpoint["wordCount"], 2436)
        self.assert_checkpoint_or_review_revision(
            chapter_seven_path, chapter_seven_checkpoint["draftSHA256"]
        )
        chapter_seven_contexts = {
            item["section"]: item
            for item in continuity["draftContexts"]
            if item["section"].startswith("ch07-")
        }
        self.assertEqual(set(chapter_seven_contexts), {"ch07-s01", "ch07-s02"})
        self.assertTrue(
            all(
                item["status"] == "canonical-section-drafted"
                and item["recordedBeforeDraft"]
                for item in chapter_seven_contexts.values()
            )
        )
        self.assertIn("contaminated site", chapter_seven)
        self.assertIn("well log", chapter_seven)
        self.assertIn("hazard map", chapter_seven)
        self.assertIn("positive, negative, and error states", chapter_seven)

        chapter_eight_path = PACKET_ROOT / "chapters/ch08.md"
        chapter_eight = chapter_eight_path.read_text(encoding="utf-8")
        chapter_eight_checkpoint = continuity["checkpoints"][7]
        self.assertEqual(chapter_eight_checkpoint["chapter"], "ch08")
        self.assertEqual(chapter_eight_checkpoint["wordCount"], 2226)
        self.assert_checkpoint_or_review_revision(
            chapter_eight_path, chapter_eight_checkpoint["draftSHA256"]
        )
        chapter_eight_contexts = {
            item["section"]: item
            for item in continuity["draftContexts"]
            if item["section"].startswith("ch08-")
        }
        self.assertEqual(set(chapter_eight_contexts), {"ch08-s01", "ch08-s02"})
        self.assertTrue(
            all(
                item["status"] == "canonical-section-drafted"
                and item["recordedBeforeDraft"]
                for item in chapter_eight_contexts.values()
            )
        )
        self.assertIn("fee simple", chapter_eight)
        self.assertIn("encumbrance", chapter_eight)
        self.assertIn("vacant possession", chapter_eight)
        self.assertIn("Personal Property Registry", chapter_eight)
        self.assertIn("No locks are changed", " ".join(chapter_eight.split()))

        chapter_nine_path = PACKET_ROOT / "chapters/ch09.md"
        chapter_nine = chapter_nine_path.read_text(encoding="utf-8")
        chapter_nine_checkpoint = continuity["checkpoints"][8]
        self.assertEqual(chapter_nine_checkpoint["chapter"], "ch09")
        self.assertEqual(chapter_nine_checkpoint["wordCount"], 2407)
        self.assert_checkpoint_or_review_revision(
            chapter_nine_path, chapter_nine_checkpoint["draftSHA256"]
        )
        chapter_nine_contexts = {
            item["section"]: item
            for item in continuity["draftContexts"]
            if item["section"].startswith("ch09-")
        }
        self.assertEqual(set(chapter_nine_contexts), {"ch09-s01", "ch09-s02"})
        self.assertTrue(
            all(
                item["status"] == "canonical-section-drafted"
                and item["recordedBeforeDraft"]
                for item in chapter_nine_contexts.values()
            )
        )
        self.assertIn("all-in cost", chapter_nine)
        self.assertIn("uncertainty reserve", chapter_nine)
        self.assertIn("maximum bid", chapter_nine)
        chapter_nine_flat = " ".join(chapter_nine.split())
        self.assertIn("fifty properties", chapter_nine_flat)
        self.assertIn("thirty-five sold", chapter_nine_flat)
        self.assertIn("thirty-one bid rows", chapter_nine_flat)
        self.assertIn("lowers the card", chapter_nine_flat)

        chapter_ten_path = PACKET_ROOT / "chapters/ch10.md"
        chapter_ten = chapter_ten_path.read_text(encoding="utf-8")
        chapter_ten_checkpoint = continuity["checkpoints"][9]
        self.assertEqual(chapter_ten_checkpoint["chapter"], "ch10")
        self.assertEqual(chapter_ten_checkpoint["wordCount"], 2638)
        self.assert_checkpoint_or_review_revision(
            chapter_ten_path, chapter_ten_checkpoint["draftSHA256"]
        )
        chapter_ten_contexts = {
            item["section"]: item
            for item in continuity["draftContexts"]
            if item["section"].startswith("ch10-")
        }
        self.assertEqual(
            set(chapter_ten_contexts), {"ch10-s01", "ch10-s02", "ch10-s03"}
        )
        self.assertTrue(
            all(
                item["status"] == "canonical-section-drafted"
                and item["recordedBeforeDraft"]
                for item in chapter_ten_contexts.values()
            )
        )
        self.assertIn("open-outcry auction", chapter_ten)
        self.assertIn("public tender", chapter_ten)
        self.assertIn("deposit", chapter_ten)
        chapter_ten_flat = " ".join(chapter_ten.split())
        self.assertIn("three business days", chapter_ten_flat)
        self.assertIn("put the land up for sale again forthwith", chapter_ten_flat)
        self.assertIn("current municipal source", chapter_ten_flat)

        chapter_eleven_path = PACKET_ROOT / "chapters/ch11.md"
        chapter_eleven = chapter_eleven_path.read_text(encoding="utf-8")
        chapter_eleven_checkpoint = continuity["checkpoints"][10]
        self.assertEqual(chapter_eleven_checkpoint["chapter"], "ch11")
        self.assertEqual(chapter_eleven_checkpoint["wordCount"], 2617)
        self.assert_checkpoint_or_review_revision(
            chapter_eleven_path, chapter_eleven_checkpoint["draftSHA256"]
        )
        chapter_eleven_contexts = {
            item["section"]: item
            for item in continuity["draftContexts"]
            if item["section"].startswith("ch11-")
        }
        self.assertEqual(set(chapter_eleven_contexts), {"ch11-s01", "ch11-s02"})
        self.assertTrue(
            all(
                item["status"] == "canonical-section-drafted"
                and item["recordedBeforeDraft"]
                for item in chapter_eleven_contexts.values()
            )
        )
        self.assertIn("insurable interest", chapter_eleven)
        self.assertIn("necessary repair", chapter_eleven)
        self.assertIn("municipality's official close-out record", chapter_eleven)
        chapter_eleven_flat = " ".join(chapter_eleven.split())
        self.assertIn("requested purchaser statement", chapter_eleven_flat)
        self.assertIn(
            "full redemption amount is paid to the treasurer", chapter_eleven_flat
        )
        self.assertIn("not a Nova Scotia tariff", chapter_eleven_flat)

        chapter_twelve_path = PACKET_ROOT / "chapters/ch12.md"
        chapter_twelve = chapter_twelve_path.read_text(encoding="utf-8")
        chapter_twelve_checkpoint = continuity["checkpoints"][11]
        self.assertEqual(chapter_twelve_checkpoint["chapter"], "ch12")
        self.assertEqual(chapter_twelve_checkpoint["wordCount"], 2825)
        self.assert_checkpoint_or_review_revision(
            chapter_twelve_path, chapter_twelve_checkpoint["draftSHA256"]
        )
        chapter_twelve_contexts = {
            item["section"]: item
            for item in continuity["draftContexts"]
            if item["section"].startswith("ch12-")
        }
        self.assertEqual(
            set(chapter_twelve_contexts),
            {"ch12-s01", "ch12-s02", "ch12-s03"},
        )
        self.assertTrue(
            all(
                item["status"] == "canonical-section-drafted"
                and item["recordedBeforeDraft"]
                for item in chapter_twelve_contexts.values()
            )
        )
        chapter_twelve_lower = chapter_twelve.lower()
        self.assertIn("deed registration", chapter_twelve_lower)
        self.assertIn("post-deed due diligence", chapter_twelve_lower)
        self.assertIn("tax-sale surplus account", chapter_twelve_lower)
        chapter_twelve_flat = " ".join(chapter_twelve.split())
        self.assertIn("six years following its registration", chapter_twelve_flat)
        self.assertIn(
            "before twenty years have passed from the sale", chapter_twelve_flat
        )
        self.assertIn(
            "assessed value is a dated mass-appraisal estimate", chapter_twelve_flat
        )

        chapter_thirteen_path = PACKET_ROOT / "chapters/ch13.md"
        chapter_thirteen = chapter_thirteen_path.read_text(encoding="utf-8")
        chapter_thirteen_checkpoint = continuity["checkpoints"][12]
        self.assertEqual(chapter_thirteen_checkpoint["chapter"], "ch13")
        self.assertEqual(chapter_thirteen_checkpoint["wordCount"], 2176)
        self.assert_checkpoint_or_review_revision(
            chapter_thirteen_path, chapter_thirteen_checkpoint["draftSHA256"]
        )
        chapter_thirteen_contexts = {
            item["section"]: item
            for item in continuity["draftContexts"]
            if item["section"].startswith("ch13-")
        }
        self.assertEqual(
            set(chapter_thirteen_contexts),
            {"ch13-s01", "ch13-s02"},
        )
        self.assertTrue(
            all(
                item["status"] == "canonical-section-drafted"
                and item["recordedBeforeDraft"]
                for item in chapter_thirteen_contexts.values()
            )
        )
        chapter_thirteen_flat = " ".join(chapter_thirteen.split())
        self.assertIn("Alder Crossing is a complete stop result", chapter_thirteen_flat)
        self.assertIn("It is not a property ranking", chapter_thirteen_flat)
        self.assertIn(
            "Payment readiness remains a separate gate", chapter_thirteen_flat
        )
        self.assertIn(
            "The public map remains owner-free and parcel-first", chapter_thirteen_flat
        )
        self.assertIn("without a sales pitch", chapter_thirteen_flat)

    def test_inverness_atlas_plan_is_separate_from_approved_figure_manifest(
        self,
    ) -> None:
        atlas = (RESEARCH_ROOT / "inverness-packet-atlas-plan.md").read_text(
            encoding="utf-8"
        )
        visuals = (RESEARCH_ROOT / "visuals.md").read_text(encoding="utf-8")
        handoff = (PACKET_ROOT / "handoff-packet.md").read_text(encoding="utf-8")
        conversation = (RESEARCH_ROOT / "conversation-log.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("45 lien entries", atlas)
        self.assertIn("47 unique PIDs", atlas)
        self.assertIn("53 NSPRD polygon features", atlas)
        self.assertIn(
            "outside both the previously approved forty-figure", atlas.lower()
        )
        self.assertIn("No assessed-owner names", atlas)
        self.assertIn("not legal access", atlas.lower())
        self.assertIn("not a wetland determination", atlas.lower())
        self.assertIn("not a title opinion", atlas.lower())
        self.assertIn("Property Online is a private research boundary", atlas)
        self.assertIn("no screenshots, plans", handoff.lower())
        self.assertIn(
            "I have access to a ns property online account, but I don't think",
            " ".join(conversation.split()),
        )
        self.assertIn("Inverness Packet Atlas", visuals)
        self.assertIn("does not add the atlas to the 54-figure", visuals)

    def test_inverness_atlas_visual_approval_binds_exact_prototype_set(self) -> None:
        receipt = json.loads(ATLAS_RECEIPT_PATH.read_text(encoding="utf-8"))
        approval = json.loads(ATLAS_APPROVAL_PATH.read_text(encoding="utf-8"))

        self.assertEqual(
            approval["renderReceiptSHA256"],
            hashlib.sha256(ATLAS_RECEIPT_PATH.read_bytes()).hexdigest(),
        )
        self.assertEqual(approval["status"], "accepted-prototype-direction")
        self.assertEqual(approval["acceptedBy"], "Dan Fakkeldy")
        self.assertEqual(approval["verbatimQuote"], "I like them.")
        self.assertRegex(
            approval["acceptedAt"], r"^2026-07-19T\d{2}:\d{2}:\d{2}-03:00$"
        )
        self.assertEqual(
            approval["acceptedFiles"],
            [item["filename"] for item in receipt["files"]],
        )
        for item in receipt["files"]:
            self.assertEqual(
                item["sha256"],
                hashlib.sha256(
                    (ATLAS_ROOT / item["filename"]).read_bytes()
                ).hexdigest(),
            )
        self.assertFalse(approval["scope"]["remainingCardsBatchAuthorized"])
        self.assertFalse(approval["scope"]["actualEchoStageProofCompleted"])
        self.assertFalse(approval["scope"]["publicationAuthorized"])

    def test_payment_and_stage_outcomes_are_distinct(self) -> None:
        ledger = json.loads(
            (RESEARCH_ROOT / "coverage-ledger.json").read_text(encoding="utf-8")
        )
        concepts = {item["name"]: item for item in ledger["concepts"]}
        self.assertNotEqual(
            concepts["payment performance"]["durableOutcome"],
            concepts["staged responsibility"]["durableOutcome"],
        )
        self.assertIn(
            "three-business-day", concepts["payment performance"]["durableOutcome"]
        )

    def test_research_closes_named_failure_path_gaps(self) -> None:
        evidence = json.loads(
            (RESEARCH_ROOT / "evidence-notes.json").read_text(encoding="utf-8")
        )
        claim_ids = {claim["id"] for claim in evidence["claims"]}
        self.assertTrue(
            {
                "LAW-015",
                "LAW-016",
                "LAW-017",
                "LAW-018",
                "OPS-006",
                "OPS-007",
                "INS-001",
            }
            <= claim_ids
        )
        comparison = (RESEARCH_ROOT / "municipality-comparison.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Halifax Regional Municipality", comparison)

    def test_visual_category_math_matches_the_proposed_fifty_four_row_manifest(
        self,
    ) -> None:
        visuals = (RESEARCH_ROOT / "visuals.md").read_text(encoding="utf-8")
        ids = {
            int(match.group(1))
            for match in re.finditer(r"^\| `figure-(\d{2})-", visuals, re.MULTILINE)
        }
        map_ids = set(range(13, 23)) | set(range(33, 38))
        editorial_ids = {1, 9}
        retrieval_ids = {38}
        screenshot_ids = set(range(41, 55))
        diagram_ids = ids - map_ids - editorial_ids - retrieval_ids - screenshot_ids

        self.assertEqual(ids, set(range(1, 55)))
        self.assertEqual(
            (
                len(map_ids),
                len(diagram_ids),
                len(editorial_ids),
                len(retrieval_ids),
                len(screenshot_ids),
            ),
            (15, 22, 2, 1, 14),
        )

    def test_map_chapter_plan_and_screenshot_receipt_are_review_only(self) -> None:
        plan = (RESEARCH_ROOT / "map-chapter-plan.md").read_text(encoding="utf-8")
        receipt = json.loads(
            (PACKET_ROOT / "figures/map-chapter-screenshot-receipt.json").read_text(
                encoding="utf-8"
            )
        )
        evidence = json.loads(
            (RESEARCH_ROOT / "evidence-notes.json").read_text(encoding="utf-8")
        )

        self.assertIn("The Map Is a Question Machine", plan)
        self.assertIn("one parcel, one toggle and one note", plan.lower())
        self.assertIn("not a verdict machine", plan.lower())
        self.assertEqual(receipt["status"], "paired-review-candidates")
        self.assertFalse(receipt["publicationBoundary"]["acceptedFinalFigures"])
        self.assertTrue(receipt["publicationBoundary"]["refreshBeforePublication"])
        self.assertEqual(receipt["schemaVersion"], 3)
        self.assertEqual(len(receipt["profiles"]), 2)
        self.assertEqual(
            {profile["name"]: len(profile["outputs"]) for profile in receipt["profiles"]},
            {"landscape": 14, "mobile": 14},
        )
        self.assertEqual(
            receipt["captureSource"]["sourceCommit"],
            "a7ba7da9ad5f8a5dcc1c67c79888bb76b6bae108",
        )
        self.assertEqual(
            {
                claim["id"]
                for claim in evidence["claims"]
                if claim["id"].startswith("MAP-")
            },
            {
                "MAP-001",
                "MAP-002",
                "MAP-003",
                "MAP-004",
                "MAP-005",
                "MAP-006",
                "MAP-007",
                "MAP-008",
            },
        )
        mineral_claims = {
            claim["id"] for claim in evidence["claims"] if claim["id"].startswith("MIN-")
        }
        self.assertEqual(mineral_claims, {"MIN-001", "MIN-002", "MIN-003", "MIN-004"})

        expected_dimensions = {"landscape": (2560, 1440), "mobile": (390, 844)}
        for profile in receipt["profiles"]:
            for output in profile["outputs"]:
                with self.subTest(profile=profile["name"], file=output["file"]):
                    path = PACKET_ROOT / output["file"]
                    self.assertTrue(path.is_file())
                    self.assertEqual(
                        hashlib.sha256(path.read_bytes()).hexdigest(), output["sha256"]
                    )
                    data = path.read_bytes()[:24]
                    self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
                    self.assertEqual(
                        struct.unpack(">II", data[16:24]),
                        expected_dimensions[profile["name"]],
                    )

    def test_public_listing_is_owner_free_and_complete(self) -> None:
        payload = json.loads(LISTING_PATH.read_text(encoding="utf-8"))

        self.assertIs(payload["ownerNamesExcluded"], True)
        self.assertEqual(payload["listingCount"], 45)
        self.assertEqual(payload["parcelIdentifierCount"], 47)
        self.assertEqual(len(payload["listings"]), 45)

        allowed_keys = {
            "aan",
            "lien",
            "location",
            "pids",
            "recoveryAmount",
            "redeemable",
        }
        pids: list[str] = []
        for listing in payload["listings"]:
            self.assertEqual(set(listing), allowed_keys)
            pids.extend(listing["pids"])

        self.assertEqual(len(pids), 47)
        self.assertEqual(len(set(pids)), 47)

    def test_map_receipt_binds_listing_and_expected_geometry_counts(self) -> None:
        metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
        listing_hash = hashlib.sha256(LISTING_PATH.read_bytes()).hexdigest()

        self.assertEqual(metadata["listingDataSHA256"], listing_hash)
        self.assertEqual(metadata["listingCount"], 45)
        self.assertEqual(metadata["requestedPIDCount"], 47)
        self.assertEqual(metadata["returnedFeatureCount"], 53)
        self.assertEqual(metadata["attribution"], ATTRIBUTION)
        self.assertIn(
            "Keep this raw geometry snapshot local",
            metadata["publicDistributionBoundary"],
        )

    def test_qgis_project_is_version_4_and_uses_only_relative_working_geometry(
        self,
    ) -> None:
        with zipfile.ZipFile(PROJECT_PATH) as archive:
            project_names = [
                name for name in archive.namelist() if name.endswith(".qgs")
            ]
            self.assertEqual(len(project_names), 1)
            project_xml = archive.read(project_names[0]).decode("utf-8")

        self.assertIn('version="4.0.2-Norrköping"', project_xml)
        self.assertIn("../working/inverness-tax-sale-parcels.geojson", project_xml)
        self.assertNotIn("/Users/", project_xml)
        self.assertNotIn("source-snapshots", project_xml)

    def test_raw_geometry_and_source_archives_are_not_tracked(self) -> None:
        geometry_path = MAP_ROOT / "working/inverness-tax-sale-parcels.geojson"
        amo_path = MAP_ROOT / "working/dp010v9sgkx_NS_Abandoned_Mines.zip"
        for source_path in (geometry_path, amo_path):
            result = subprocess.run(
                ["git", "check-ignore", "-q", str(source_path.relative_to(REPO_ROOT))],
                cwd=REPO_ROOT,
                check=False,
            )
            self.assertEqual(result.returncode, 0)
        self.assertEqual(
            (MAP_ROOT / "working/.gitignore").read_text(encoding="utf-8"),
            "# Raw NSPRD geometry and downloaded GIS source archives are local build caches.\n"
            "*\n"
            "!.gitignore\n",
        )

    def test_proof_images_have_echo_video_master_dimensions(self) -> None:
        for name in (
            "inverness-all-properties-orientation.png",
            "inverness-lien-01-aerial.png",
        ):
            image_path = MAP_ROOT / "exports" / name
            data = image_path.read_bytes()
            self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
            self.assertEqual(data[12:16], b"IHDR")
            self.assertEqual(struct.unpack(">II", data[16:24]), (2560, 1440))

    def test_renderer_preserves_required_attribution(self) -> None:
        renderer = (MAP_ROOT / "scripts/render_qgis_maps.py").read_text(
            encoding="utf-8"
        )
        module = ast.parse(renderer)
        attribution_node = next(
            node
            for node in module.body
            if isinstance(node, ast.Assign)
            if any(
                isinstance(target, ast.Name) and target.id == "ATTRIBUTION"
                for target in node.targets
            )
        )
        self.assertEqual(ast.literal_eval(attribution_node.value), ATTRIBUTION)

    def test_atlas_prototype_specs_are_owner_free_and_outside_canonical_manifest(
        self,
    ) -> None:
        specs = json.loads(ATLAS_SPEC_PATH.read_text(encoding="utf-8"))
        listing = json.loads(LISTING_PATH.read_text(encoding="utf-8"))
        evidence = json.loads(
            (RESEARCH_ROOT / "evidence-notes.json").read_text(encoding="utf-8")
        )
        listing_by_lien = {item["lien"]: item for item in listing["listings"]}
        valid_claim_ids = {claim["id"] for claim in evidence["claims"]}

        self.assertEqual(specs["assetStatus"], "review-candidate")
        self.assertFalse(specs["canonicalFigureManifestChanged"])
        self.assertFalse(specs["propertyOnlineUsed"])
        self.assertFalse(specs["assessedOwnerNamesIncluded"])
        self.assertEqual([card["lien"] for card in specs["cards"]], [1, 8, 11])

        for card in specs["cards"]:
            source = listing_by_lien[card["lien"]]
            self.assertEqual(card["municipalFacts"]["aan"], source["aan"])
            self.assertEqual(card["municipalFacts"]["pids"], source["pids"])
            self.assertEqual(card["municipalFacts"]["location"], source["location"])
            self.assertEqual(
                card["municipalFacts"]["recoveryAmount"],
                source["recoveryAmount"],
            )
            self.assertTrue(set(card["evidenceClaimIds"]) <= valid_claim_ids)
            self.assertIn("not legal access", " ".join(card["limitations"]).lower())
            self.assertIn("not a title opinion", " ".join(card["limitations"]).lower())

        mine_card = specs["cards"][1]
        self.assertEqual(mine_card["archetype"], "mine-record-screening")
        self.assertIn("incomplete", " ".join(mine_card["limitations"]).lower())
        self.assertIn("50 metres", " ".join(mine_card["limitations"]).lower())

    def test_atlas_prototype_receipt_binds_three_qgis4_renders(self) -> None:
        specs = json.loads(ATLAS_SPEC_PATH.read_text(encoding="utf-8"))
        receipt = json.loads(ATLAS_RECEIPT_PATH.read_text(encoding="utf-8"))

        self.assertEqual(receipt["assetStatus"], "review-candidate")
        self.assertEqual(
            receipt["humanAcceptance"]["status"],
            "accepted-prototype-direction",
        )
        self.assertEqual(receipt["humanAcceptance"]["verbatimQuote"], "I like them.")
        self.assertFalse(receipt["canonicalFigureManifestChanged"])
        self.assertFalse(receipt["propertyOnlineUsed"])
        self.assertEqual(receipt["renderer"], "QGIS 4")
        self.assertRegex(receipt["qgisVersion"], r"^4\.")
        self.assertEqual(
            receipt["specSHA256"],
            hashlib.sha256(ATLAS_SPEC_PATH.read_bytes()).hexdigest(),
        )
        self.assertEqual(
            receipt["listingDataSHA256"],
            hashlib.sha256(LISTING_PATH.read_bytes()).hexdigest(),
        )
        self.assertEqual(len(receipt["files"]), 3)
        self.assertEqual({item["lien"] for item in receipt["files"]}, {1, 8, 11})

        expected_names = {card["filename"] for card in specs["cards"]}
        self.assertEqual(
            {item["filename"] for item in receipt["files"]}, expected_names
        )
        for item in receipt["files"]:
            path = ATLAS_ROOT / item["filename"]
            data = path.read_bytes()
            self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
            self.assertEqual(struct.unpack(">II", data[16:24]), (2560, 1440))
            self.assertEqual(item["sha256"], hashlib.sha256(data).hexdigest())
            self.assertEqual((item["width"], item["height"]), (2560, 1440))

        self.assertEqual(receipt["mineScreening"]["recordedOpeningCount"], 4)
        self.assertGreater(
            receipt["mineScreening"]["nearestRecordedOpeningMetres"], 1000
        )
        self.assertLess(receipt["mineScreening"]["nearestRecordedOpeningMetres"], 4000)
        self.assertEqual(
            {(item["width"], item["height"]) for item in receipt["reviewAids"]},
            {(3840, 720), (1920, 360)},
        )
        for item in receipt["reviewAids"]:
            path = ATLAS_ROOT / item["filename"]
            self.assertEqual(
                item["sha256"], hashlib.sha256(path.read_bytes()).hexdigest()
            )

    def test_orientation_uses_phone_legible_halo_markers(self) -> None:
        renderer = (MAP_ROOT / "scripts/render_qgis_maps.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("styled_orientation_markers", renderer)
        self.assertIn("OpenStreetMap", renderer)
        self.assertIn("QgsGeometryGeneratorSymbolLayer", renderer)
        self.assertIn("setLabelsEnabled(False)", renderer)

    def test_multi_municipality_map_handoff_is_owner_free_and_fail_closed(self) -> None:
        register = json.loads(MUNICIPAL_SOURCE_REGISTER.read_text(encoding="utf-8"))
        events = {event["id"]: event for event in register["events"]}

        self.assertEqual(events["cbrm-2026-07-21"]["expectedListingCount"], 67)
        self.assertEqual(events["cbrm-2026-07-21"]["expectedPIDCount"], 68)
        self.assertEqual(
            events["pictou-county-2026-01"]["expectedWithdrawnRowCount"], 3
        )
        self.assertEqual(events["richmond-county-2026-06-12"]["expectedPIDCount"], 3)
        self.assertEqual(
            events["annapolis-county-2026"]["mapReadiness"],
            "blocked-pending-verifiable-pid-extraction",
        )
        self.assertEqual(events["chester-2026"]["eventStatusAsOfCheck"], "no-sale")

        public_fields = {
            field.lower()
            for event in events.values()
            for field in event.get("publicFields", [])
        }
        self.assertFalse({"owner", "ownername", "successfulbidder"} & public_fields)

        prompt = NS_MARKS_PROMPT.read_text(encoding="utf-8")
        self.assertIn("67 listings/68 unique PIDs", prompt)
        self.assertIn("Historical 2026 events", prompt)
        self.assertIn("Do not add parcel records yet", prompt)
        self.assertIn("Never write those names", prompt)


if __name__ == "__main__":
    unittest.main()
