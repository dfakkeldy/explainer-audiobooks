import ast
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import unittest
import zipfile


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKET_ROOT = REPO_ROOT / "docs/nova-scotia-tax-sale-book"
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
