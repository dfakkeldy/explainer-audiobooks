import json
import tempfile
import unittest
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FIGURE_DIR = ROOT / "docs" / "nova-scotia-tax-sale-book" / "figures"
SPEC_PATH = FIGURE_DIR / "figure-specs.json"
RENDERER_PATH = FIGURE_DIR / "render_slideshow_figures.py"


def load_renderer():
    spec = spec_from_file_location("tax_sale_figure_renderer", RENDERER_PATH)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class NovaScotiaTaxSaleFigureTests(unittest.TestCase):
    def setUp(self):
        self.spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))

    def test_first_batch_is_complete_and_review_only(self):
        figures = self.spec["figures"]
        self.assertEqual([item["id"] for item in figures], [f"figure-{number:02d}" for number in range(3, 9)])
        self.assertEqual(self.spec["assetStatus"], "review-candidate")
        self.assertTrue(all(item["status"] == "review-candidate" for item in figures))

    def test_specs_include_learning_provenance_and_accessibility_fields(self):
        for item in self.spec["figures"]:
            with self.subTest(figure=item["id"]):
                self.assertGreaterEqual(len(item["title"]), 10)
                self.assertGreaterEqual(len(item["caption"]), 20)
                self.assertGreaterEqual(len(item["altText"]), 40)
                self.assertTrue(item["teachingJob"])
                self.assertTrue(item["claimIds"])
                self.assertTrue(item["legalLocators"])
                self.assertTrue(item["rights"])

    def test_public_specs_do_not_contain_private_or_recommendation_fields(self):
        serialized = json.dumps(self.spec).lower()
        for prohibited in ("owner name", "maximum bid", "recommended parcel", "/users/"):
            self.assertNotIn(prohibited, serialized)

    def test_renderer_produces_echo_sized_rgb_pngs_and_contact_sheet(self):
        renderer = load_renderer()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "images"
            contact_sheet = root / "contact.png"
            paths = renderer.render_all(SPEC_PATH, output, contact_sheet)
            self.assertEqual(len(paths), 6)
            self.assertTrue(contact_sheet.exists())
            for path in paths:
                with self.subTest(path=path.name), Image.open(path) as image:
                    self.assertEqual(image.size, (2560, 1440))
                    self.assertEqual(image.mode, "RGB")
                    self.assertEqual(image.format, "PNG")

    def test_renderer_registry_matches_manifest(self):
        renderer = load_renderer()
        self.assertEqual(set(renderer.RENDERERS), {item["id"] for item in self.spec["figures"]})

    def test_receipt_binds_rendered_pixels_to_the_spec(self):
        renderer = load_renderer()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = renderer.render_all(SPEC_PATH, root / "images", root / "contact.png")
            receipt_path = root / "receipt.json"
            renderer.write_receipt(paths, SPEC_PATH, receipt_path)
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertEqual(receipt["specSHA256"], renderer.sha256(SPEC_PATH))
            self.assertEqual(receipt["humanAcceptance"], "pending")
            self.assertEqual(len(receipt["files"]), 6)
            for entry in receipt["files"]:
                self.assertEqual((entry["width"], entry["height"], entry["mode"]), (2560, 1440, "RGB"))


if __name__ == "__main__":
    unittest.main()
