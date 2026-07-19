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
MUNICIPAL_SOURCE_REGISTER = (
    PACKET_ROOT / "research/municipal-map-source-register.json"
)
NS_MARKS_PROMPT = (
    PACKET_ROOT / "research/ns-marks-multi-municipality-map-prompt.md"
)
ATTRIBUTION = (
    "Contains information obtained under license from the Province of Nova "
    "Scotia which is provided without warranty or liability for errors or "
    "omissions."
)


class NovaScotiaTaxSaleDevelopmentTests(unittest.TestCase):
    def test_learning_evidence_matches_validator_contract(self) -> None:
        evidence_path = RESEARCH_ROOT / "evidence-notes.json"
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))

        self.assertEqual(
            evidence["notesSHA256"],
            hashlib.sha256((RESEARCH_ROOT / "evidence-notes.md").read_bytes()).hexdigest(),
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
        self.assertEqual(brief["currentTargetWords"], 42800)
        self.assertEqual(len(brief["scopeHistory"]), 6)
        for decision in brief["scopeHistory"]:
            self.assertRegex(decision["recordedAt"], r"^2026-07-(18|19)T")
            self.assertTrue(decision["verbatimQuote"])
            self.assertEqual(decision["evidence"], decision["verbatimQuote"])

    def test_outline_gate_is_not_backfilled_without_user_approval(self) -> None:
        outline = json.loads(
            (RESEARCH_ROOT / "learning-outline.json").read_text(encoding="utf-8")
        )

        self.assertEqual(outline["authorization"]["status"], "pending")
        self.assertIn("No verbatim approval", outline["authorization"]["evidence"])

    def test_required_planning_handoff_artifacts_exist(self) -> None:
        conversation = (RESEARCH_ROOT / "conversation-log.md").read_text(encoding="utf-8")
        handoff = (PACKET_ROOT / "handoff-packet.md").read_text(encoding="utf-8")
        pronunciation = json.loads(
            (RESEARCH_ROOT / "pronunciation-plan.json").read_text(encoding="utf-8")
        )

        terms = {entry["term"] for entry in pronunciation["terms"]}
        self.assertTrue(
            {"Mabou", "Whycocomagh", "Judique", "AAN", "PID", "NSPRD", "MGA"}
            <= terms
        )
        self.assertIn("development draft", handoff)
        self.assertIn("No outline approval", conversation)

    def test_payment_and_stage_outcomes_are_distinct(self) -> None:
        ledger = json.loads(
            (RESEARCH_ROOT / "coverage-ledger.json").read_text(encoding="utf-8")
        )
        concepts = {item["name"]: item for item in ledger["concepts"]}
        self.assertNotEqual(
            concepts["payment performance"]["durableOutcome"],
            concepts["staged responsibility"]["durableOutcome"],
        )
        self.assertIn("three-business-day", concepts["payment performance"]["durableOutcome"])

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

    def test_visual_category_math_matches_the_forty_row_manifest(self) -> None:
        visuals = (RESEARCH_ROOT / "visuals.md").read_text(encoding="utf-8")
        ids = {
            int(match.group(1))
            for match in re.finditer(r"^\| `figure-(\d{2})-", visuals, re.MULTILINE)
        }
        map_ids = set(range(13, 23)) | set(range(33, 38))
        editorial_ids = {1, 9}
        retrieval_ids = {38}
        diagram_ids = ids - map_ids - editorial_ids - retrieval_ids

        self.assertEqual(ids, set(range(1, 41)))
        self.assertEqual(
            (len(map_ids), len(diagram_ids), len(editorial_ids), len(retrieval_ids)),
            (15, 22, 2, 1),
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
        self.assertIn("Keep this raw geometry snapshot local", metadata["publicDistributionBoundary"])

    def test_qgis_project_is_version_4_and_uses_only_relative_working_geometry(self) -> None:
        with zipfile.ZipFile(PROJECT_PATH) as archive:
            project_names = [name for name in archive.namelist() if name.endswith(".qgs")]
            self.assertEqual(len(project_names), 1)
            project_xml = archive.read(project_names[0]).decode("utf-8")

        self.assertIn('version="4.0.2-Norrköping"', project_xml)
        self.assertIn("../working/inverness-tax-sale-parcels.geojson", project_xml)
        self.assertNotIn("/Users/", project_xml)
        self.assertNotIn("source-snapshots", project_xml)

    def test_raw_geometry_is_not_tracked(self) -> None:
        geometry_path = MAP_ROOT / "working/inverness-tax-sale-parcels.geojson"
        result = subprocess.run(
            ["git", "check-ignore", "-q", str(geometry_path.relative_to(REPO_ROOT))],
            cwd=REPO_ROOT,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            (MAP_ROOT / "working/.gitignore").read_text(encoding="utf-8"),
            "# Raw NSPRD geometry is a local restricted-service build cache.\n"
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
        self.assertEqual(events["pictou-county-2026-01"]["expectedWithdrawnRowCount"], 3)
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
