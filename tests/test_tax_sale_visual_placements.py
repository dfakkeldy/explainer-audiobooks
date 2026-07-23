import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BOOK_ROOT = REPO_ROOT / "docs" / "nova-scotia-tax-sale-book"
STAGER_PATH = BOOK_ROOT / "figures" / "stage_visual_chapters.py"
SCREENSHOT_RECEIPT_PATH = BOOK_ROOT / "figures" / "map-chapter-screenshot-receipt.json"


class TaxSaleVisualPlacementTests(unittest.TestCase):
    def load_stager(self):
        self.assertTrue(STAGER_PATH.exists(), "visual chapter stager is missing")
        spec = importlib.util.spec_from_file_location("stage_visual_chapters", STAGER_PATH)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_manifest_covers_all_54_figures_with_unique_anchors(self) -> None:
        module = self.load_stager()
        placements = module.load_placements()

        self.assertEqual(len(placements), 54)
        self.assertEqual(
            {placement["id"] for placement in placements},
            {f"figure-{number:02d}" for number in range(1, 55)},
        )
        self.assertEqual(
            len({(placement["chapter"], placement["anchor"]) for placement in placements}),
            54,
        )
        for placement in placements:
            chapter = BOOK_ROOT / "chapters" / placement["chapter"]
            self.assertEqual(chapter.read_text().count(placement["anchor"]), 1)

    def test_staging_inserts_54_standalone_figures_without_changing_prose(self) -> None:
        module = self.load_stager()
        with tempfile.TemporaryDirectory() as temporary_directory:
            destination = Path(temporary_directory) / "chapters"
            receipt = module.stage_visual_chapters(destination)

            self.assertEqual(receipt["figureCount"], 54)
            self.assertEqual(receipt["proseParity"], "exact-after-removing-figures")

            image_lines = []
            for source in sorted((BOOK_ROOT / "chapters").glob("ch*.md")):
                staged = destination / source.name
                image_lines.extend(
                    line for line in staged.read_text().splitlines() if line.startswith("![")
                )
                self.assertEqual(
                    module.remove_figure_blocks(staged.read_text()),
                    source.read_text(),
                    source.name,
                )
            self.assertEqual(len(image_lines), 54)
            chapter_13 = (destination / "ch13.md").read_text()
            self.assertLess(
                chapter_13.index("visual-figure-start:figure-33"),
                chapter_13.index("visual-figure-start:figure-34"),
            )

    def test_map_capture_profiles_are_hash_bound_at_native_dimensions(self) -> None:
        receipt = json.loads(SCREENSHOT_RECEIPT_PATH.read_text())
        self.assertEqual(receipt["captureSource"]["browserConsole"], {"warnings": 0, "errors": 0})
        self.assertEqual(len(receipt["profiles"]), 2)

        expected_dimensions = {"landscape": (2560, 1440), "mobile": (390, 844)}
        for profile in receipt["profiles"]:
            self.assertEqual(len(profile["outputs"]), 14)
            for output in profile["outputs"]:
                image_path = BOOK_ROOT / output["file"]
                image_bytes = image_path.read_bytes()
                self.assertEqual(image_bytes[:8], b"\x89PNG\r\n\x1a\n", image_path)
                self.assertEqual(
                    (int.from_bytes(image_bytes[16:20], "big"), int.from_bytes(image_bytes[20:24], "big")),
                    expected_dimensions[profile["name"]],
                    image_path,
                )
                self.assertEqual(hashlib.sha256(image_bytes).hexdigest(), output["sha256"], image_path)


if __name__ == "__main__":
    unittest.main()
