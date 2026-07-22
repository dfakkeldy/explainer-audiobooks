import importlib.util
import inspect
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image


REPO_ROOT = Path(__file__).resolve().parents[1]
RENDERER_PATH = (
    REPO_ROOT
    / "docs"
    / "nova-scotia-tax-sale-book"
    / "figures"
    / "render_visual_expansion.py"
)


class TaxSaleVisualExpansionTests(unittest.TestCase):
    def load_renderer(self):
        self.assertTrue(RENDERER_PATH.exists(), "visual expansion renderer is missing")
        spec = importlib.util.spec_from_file_location("render_visual_expansion", RENDERER_PATH)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_renderer_declares_every_missing_approved_figure(self) -> None:
        module = self.load_renderer()

        expected = {"figure-01", "figure-02"}
        expected.update({f"figure-{number:02d}" for number in range(9, 39)})
        self.assertEqual(set(module.PLANNED_FIGURES), expected)

    def test_renderer_creates_profile_specific_complete_review_sets(self) -> None:
        module = self.load_renderer()
        self.assertTrue(
            hasattr(module, "render_review_set"),
            "paired review-set renderer is missing",
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            scene_sources = {}
            for figure_id in ("figure-01", "figure-09"):
                scene_sources[figure_id] = {}
                for profile, size in {
                    "landscape": (320, 180),
                    "mobile": (180, 320),
                }.items():
                    source = root / f"{figure_id}-{profile}-source.png"
                    Image.new("RGB", size, "#173C5B").save(source)
                    scene_sources[figure_id][profile] = source

            receipt = module.render_review_set(
                root / "rendered",
                scene_sources=scene_sources,
                profile_sizes={"landscape": (320, 180), "mobile": (180, 320)},
            )

            self.assertEqual(receipt["assetStatus"], "review-candidate")
            self.assertEqual(len(receipt["figures"]), 32)
            self.assertEqual(
                {figure["id"] for figure in receipt["figures"]},
                set(module.PLANNED_FIGURES),
            )
            for profile, size in {"landscape": (320, 180), "mobile": (180, 320)}.items():
                paths = sorted((root / "rendered" / profile).glob("figure-*.png"))
                self.assertEqual(len(paths), 32)
                for path in paths:
                    with Image.open(path) as image:
                        self.assertEqual(image.size, size)
                        self.assertEqual(image.mode, "RGB")

    def test_renderer_closes_every_image_buffer_that_it_saves(self) -> None:
        module = self.load_renderer()
        original_save = Image.Image.save
        original_close = Image.Image.close
        saved_ids = set()
        closed_ids = set()

        def tracking_save(image, *args, **kwargs):
            saved_ids.add(id(image))
            return original_save(image, *args, **kwargs)

        def tracking_close(image):
            closed_ids.add(id(image))
            return original_close(image)

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            scene_sources = {}
            for figure_id in ("figure-01", "figure-09"):
                scene_sources[figure_id] = {}
                for profile, size in {
                    "landscape": (320, 180),
                    "mobile": (180, 320),
                }.items():
                    source = root / f"{figure_id}-{profile}-source.png"
                    Image.new("RGB", size, "#173C5B").save(source)
                    scene_sources[figure_id][profile] = source

            with patch.object(Image.Image, "save", tracking_save), patch.object(
                Image.Image, "close", tracking_close
            ):
                module.render_review_set(
                    root / "rendered",
                    scene_sources=scene_sources,
                    profile_sizes={"landscape": (320, 180), "mobile": (180, 320)},
                )

        self.assertTrue(saved_ids)
        self.assertEqual(saved_ids - closed_ids, set(), "saved image buffers leaked")

    def test_profile_receipts_merge_without_losing_rendition_hashes(self) -> None:
        module = self.load_renderer()
        self.assertTrue(
            hasattr(module, "merge_profile_receipts"),
            "profile receipt merger is missing",
        )
        partials = []
        for profile, dimensions, digest in (
            ("landscape", (2560, 1440), "a" * 64),
            ("mobile", (1080, 1920), "b" * 64),
        ):
            partials.append(
                {
                    "schemaVersion": 1,
                    "assetStatus": "review-candidate",
                    "scope": "approved missing figures 01, 02, and 09 through 38",
                    "profiles": {
                        profile: {"width": dimensions[0], "height": dimensions[1]}
                    },
                    "figures": [
                        {
                            "id": "figure-01",
                            "filename": "figure-01-auction-morning.png",
                            "chapter": 1,
                            "title": "Auction morning is collection work",
                            "caption": "A tax sale begins as collection work.",
                            "kind": "scene",
                            "renditions": {profile: {"sha256": digest}},
                        }
                    ],
                    "boundaries": ["review only"],
                }
            )

        merged = module.merge_profile_receipts(partials)

        self.assertEqual(set(merged["profiles"]), {"landscape", "mobile"})
        self.assertEqual(
            set(merged["figures"][0]["renditions"]), {"landscape", "mobile"}
        )
        self.assertEqual(
            merged["figures"][0]["renditions"]["landscape"]["sha256"],
            "a" * 64,
        )
        self.assertEqual(
            merged["figures"][0]["renditions"]["mobile"]["sha256"],
            "b" * 64,
        )

    def test_default_card_layouts_keep_text_inside_every_card(self) -> None:
        module = self.load_renderer()
        self.assertTrue(
            hasattr(module, "card_layout_overflows"),
            "card text-fit validator is missing",
        )
        failures = []
        for figure in module.FIGURES.values():
            if figure["kind"] in {
                "scene",
                "case-map",
                "municipal-map",
                "ratio-chart",
            }:
                continue
            for profile, size in module.DEFAULT_PROFILE_SIZES.items():
                for item_label in module.card_layout_overflows(figure, size):
                    failures.append(f"{figure['id']}:{profile}:{item_label}")

        self.assertEqual(failures, [])

    def test_renderer_can_render_a_selected_figure_subset(self) -> None:
        module = self.load_renderer()
        self.assertIn(
            "figure_ids",
            inspect.signature(module.render_review_set).parameters,
            "selected-figure rendering is missing",
        )


if __name__ == "__main__":
    unittest.main()
