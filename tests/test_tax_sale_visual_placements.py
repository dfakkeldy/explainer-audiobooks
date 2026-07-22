import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BOOK_ROOT = REPO_ROOT / "docs" / "nova-scotia-tax-sale-book"
STAGER_PATH = BOOK_ROOT / "figures" / "stage_visual_chapters.py"


class TaxSaleVisualPlacementTests(unittest.TestCase):
    def load_stager(self):
        self.assertTrue(STAGER_PATH.exists(), "visual chapter stager is missing")
        spec = importlib.util.spec_from_file_location("stage_visual_chapters", STAGER_PATH)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_manifest_covers_all_51_figures_with_unique_anchors(self) -> None:
        module = self.load_stager()
        placements = module.load_placements()

        self.assertEqual(len(placements), 51)
        self.assertEqual(
            {placement["id"] for placement in placements},
            {f"figure-{number:02d}" for number in range(1, 52)},
        )
        self.assertEqual(
            len({(placement["chapter"], placement["anchor"]) for placement in placements}),
            51,
        )
        for placement in placements:
            chapter = BOOK_ROOT / "chapters" / placement["chapter"]
            self.assertEqual(chapter.read_text().count(placement["anchor"]), 1)

    def test_staging_inserts_51_standalone_figures_without_changing_prose(self) -> None:
        module = self.load_stager()
        with tempfile.TemporaryDirectory() as temporary_directory:
            destination = Path(temporary_directory) / "chapters"
            receipt = module.stage_visual_chapters(destination)

            self.assertEqual(receipt["figureCount"], 51)
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
            self.assertEqual(len(image_lines), 51)
            chapter_13 = (destination / "ch13.md").read_text()
            self.assertLess(
                chapter_13.index("visual-figure-start:figure-33"),
                chapter_13.index("visual-figure-start:figure-34"),
            )


if __name__ == "__main__":
    unittest.main()
