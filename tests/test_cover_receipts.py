from __future__ import annotations

import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from PIL import Image

sys.path.insert(0, str(Path(__file__).parents[1] / "skill" / "scripts"))
import cover_receipts


VALID_SELECTION = {
    "book_slug": "rodents-in-the-walls",
    "edition_id": "corrected-v2",
    "selection_source": "explicit-user-choice",
    "selected_at": "2026-07-12T13:00:00-03:00",
    "classification": "public-safe",
    "permission_to_publish": "granted",
}


def make_cover(
    path: Path,
    colour: str = "#132238",
    *,
    mode: str = "RGB",
    size: tuple[int, int] = (1600, 2560),
) -> Path:
    Image.new(mode, size, colour).save(path)
    return path


def make_epub(path: Path, cover: bytes) -> Path:
    container = (
        '<?xml version="1.0"?><container '
        'xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
        '<rootfiles><rootfile full-path="OEBPS/content.opf" '
        'media-type="application/oebps-package+xml"/></rootfiles></container>'
    )
    opf = (
        '<package xmlns="http://www.idpf.org/2007/opf"><metadata/><manifest>'
        '<item id="cover" href="cover.png" media-type="image/png" '
        'properties="cover-image"/></manifest><spine/></package>'
    )
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            "mimetype",
            "application/epub+zip",
            compress_type=zipfile.ZIP_STORED,
        )
        archive.writestr("META-INF/container.xml", container)
        archive.writestr("OEBPS/content.opf", opf)
        archive.writestr("OEBPS/cover.png", cover)
    return path


def render_payload(cover: Path) -> dict[str, object]:
    return {
        "receipt_version": 1,
        "renderer_version": 1,
        "schema_version": 1,
        "candidate": {
            "id": "c1-full-bleed",
            "direction_name": "Full Bleed Display",
        },
        "spec": "cover-spec-1.json",
        "spec_sha256": "1" * 64,
        "source_art": "cover-source.png",
        "source_art_sha256": "2" * 64,
        "font_manifest_version": 1,
        "font_manifest_sha256": "3" * 64,
        "fonts": {"display-condensed": "4" * 64},
        "output": cover.name,
        "output_sha256": hashlib.sha256(cover.read_bytes()).hexdigest(),
        "thumbnail": "cover-thumbnail.png",
        "thumbnail_sha256": "5" * 64,
        "dimensions": [1600, 2560],
        "colour_mode": "RGB",
        "warnings": [],
    }


def paired_render_payload(
    root: Path,
    cover: Path,
    variant: str,
    *,
    candidate_id: str = "open-machine",
    source_hash: str = "2" * 64,
    subtitle: str | None = None,
) -> dict[str, object]:
    dimensions = (1600, 2560) if variant == "portrait" else (2400, 2400)
    thumbnail_dimensions = (160, 256) if variant == "portrait" else (160, 160)
    metadata_subtitle = "The Exact Subtitle" if subtitle is None else subtitle
    spec = {
        "schema_version": 2,
        "variant": variant,
        "candidate": {"id": candidate_id, "direction_name": "The Open Machine"},
        "metadata": {
            "title": "Fixture Book",
            "subtitle": metadata_subtitle,
            "author": "Dan Fakkeldy",
            "label": "AUDIOBOOK",
        },
    }
    spec_path = root / f"{variant}.json"
    spec_path.write_text(json.dumps(spec), encoding="utf-8")
    thumbnail = root / f"{variant}-thumbnail.png"
    make_cover(thumbnail, size=thumbnail_dimensions)
    return {
        "receipt_version": 1,
        "renderer_version": 1,
        "schema_version": 1,
        "variant": variant,
        "candidate": {"id": candidate_id, "direction_name": "The Open Machine"},
        "spec": spec_path.name,
        "spec_sha256": hashlib.sha256(spec_path.read_bytes()).hexdigest(),
        "source_art": "cover-source.png",
        "source_art_sha256": source_hash,
        "font_manifest_version": 1,
        "font_manifest_sha256": "3" * 64,
        "fonts": {"display-condensed": "4" * 64},
        "output": cover.name,
        "output_sha256": hashlib.sha256(cover.read_bytes()).hexdigest(),
        "thumbnail": thumbnail.name,
        "thumbnail_sha256": hashlib.sha256(thumbnail.read_bytes()).hexdigest(),
        "dimensions": list(dimensions),
        "thumbnail_dimensions": list(thumbnail_dimensions),
        "colour_mode": "RGB",
        "warnings": [],
    }


def write_json(path: Path, payload: object) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def raw_selection_receipt(
    cover_hash: str,
    *,
    duplicate_top_level: str = "",
    duplicate_privacy: str = "",
) -> str:
    return f"""{{
  "receipt_version": 1,
  "book_slug": "rodents-in-the-walls",
  {duplicate_top_level}
  "edition_id": "corrected-v2",
  "selected_candidate": "c1-full-bleed",
  "direction_name": "Full Bleed Display",
  "schema_version": 1,
  "spec_sha256": "{'1' * 64}",
  "source_art_sha256": "{'2' * 64}",
  "rendered_cover_sha256": "{cover_hash}",
  "font_manifest_version": 1,
  "font_manifest_sha256": "{'3' * 64}",
  "dimensions": [1600, 2560],
  "colour_mode": "RGB",
  "selected_at": "2026-07-12T13:00:00-03:00",
  "selection_source": "explicit-user-choice",
  "privacy": {{
    "classification": "public-safe",
    "permission_to_publish": "granted"{duplicate_privacy}
  }}
}}"""


def raw_render_receipt(
    cover: Path,
    *,
    duplicate_top_level: str = "",
    duplicate_candidate: str = "",
) -> str:
    return f"""{{
  "receipt_version": 1,
  "renderer_version": 1,
  "schema_version": 1,
  "candidate": {{
    "id": "c1-full-bleed",
    "direction_name": "Full Bleed Display"{duplicate_candidate}
  }},
  "spec": "cover-spec-1.json",
  {duplicate_top_level}
  "spec_sha256": "{'1' * 64}",
  "source_art": "cover-source.png",
  "source_art_sha256": "{'2' * 64}",
  "font_manifest_version": 1,
  "font_manifest_sha256": "{'3' * 64}",
  "fonts": {{"display-condensed": "{'4' * 64}"}},
  "output": "{cover.name}",
  "output_sha256": "{hashlib.sha256(cover.read_bytes()).hexdigest()}",
  "thumbnail": "cover-thumbnail.png",
  "thumbnail_sha256": "{'5' * 64}",
  "dimensions": [1600, 2560],
  "colour_mode": "RGB",
  "warnings": []
}}"""


def make_render_receipt(
    root: Path,
    cover: Path,
    payload: object | None = None,
) -> Path:
    return write_json(
        root / "cover.render.json",
        render_payload(cover) if payload is None else payload,
    )


def create_valid_selection(root: Path, cover: Path) -> Path:
    selection = root / "cover-selection.json"
    cover_receipts.create_selection(
        make_render_receipt(root, cover),
        selection,
        **VALID_SELECTION,
    )
    return selection


class CoverReceiptTests(unittest.TestCase):
    def create_pair_fixture(self, root: Path):
        portrait = make_cover(root / "portrait.png")
        square = make_cover(root / "square.png", size=(2400, 2400))
        portrait_render = write_json(
            root / "portrait.render.json",
            paired_render_payload(root, portrait, "portrait"),
        )
        square_render = write_json(
            root / "square.render.json",
            paired_render_payload(root, square, "square", subtitle=""),
        )
        receipt = cover_receipts.create_paired_selection(
            portrait_render,
            square_render,
            root / "selection.json",
            book_slug="fixture-book",
            edition_id="public-v1",
            selection_source="user",
            selected_at="2026-07-13T12:00:00-03:00",
            privacy_classification="public-safe",
            permission_to_publish=True,
        )
        return receipt, portrait, square, portrait_render, square_render

    def test_creates_one_selection_binding_both_variants(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            receipt, *_ = self.create_pair_fixture(Path(raw))
            self.assertEqual(set(receipt.variants), {"portrait", "square"})
            self.assertEqual(receipt.candidate.id, "open-machine")
            self.assertEqual(receipt.variants["portrait"].dimensions, (1600, 2560))
            self.assertEqual(receipt.variants["square"].dimensions, (2400, 2400))

    def test_rejects_mixed_candidate_ids_or_source_hashes(self) -> None:
        for changed, pattern in (("candidate", "candidate"), ("source", "source")):
            with self.subTest(changed=changed), tempfile.TemporaryDirectory() as raw:
                root = Path(raw)
                portrait = make_cover(root / "portrait.png")
                square = make_cover(root / "square.png", size=(2400, 2400))
                portrait_render = write_json(
                    root / "portrait.render.json",
                    paired_render_payload(root, portrait, "portrait"),
                )
                square_payload = paired_render_payload(
                    root,
                    square,
                    "square",
                    subtitle="",
                    candidate_id="other" if changed == "candidate" else "open-machine",
                    source_hash="9" * 64 if changed == "source" else "2" * 64,
                )
                square_render = write_json(root / "square.render.json", square_payload)
                with self.assertRaisesRegex(ValueError, pattern):
                    cover_receipts.create_paired_selection(
                        portrait_render,
                        square_render,
                        root / "selection.json",
                        book_slug="fixture-book",
                        edition_id="public-v1",
                        selection_source="user",
                        selected_at="2026-07-13T12:00:00-03:00",
                        privacy_classification="public-safe",
                        permission_to_publish=True,
                    )

    def test_rejects_automatic_paired_selection_source(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            portrait = make_cover(root / "portrait.png")
            square = make_cover(root / "square.png", size=(2400, 2400))
            portrait_render = write_json(
                root / "portrait.render.json",
                paired_render_payload(root, portrait, "portrait"),
            )
            square_render = write_json(
                root / "square.render.json",
                paired_render_payload(root, square, "square", subtitle=""),
            )
            with self.assertRaisesRegex(ValueError, "selection_source"):
                cover_receipts.create_paired_selection(
                    portrait_render,
                    square_render,
                    root / "selection.json",
                    book_slug="fixture-book",
                    edition_id="public-v1",
                    selection_source="first-valid",
                    selected_at="2026-07-13T12:00:00-03:00",
                    privacy_classification="public-safe",
                    permission_to_publish=True,
                )

    def test_rejects_duplicate_nested_variant_fields(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.create_pair_fixture(root)
            path = root / "selection.json"
            payload = path.read_text(encoding="utf-8").replace(
                '"cover_sha256":',
                '"cover_sha256": "' + "0" * 64 + '", "cover_sha256":',
                1,
            )
            path.write_text(payload, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate"):
                cover_receipts.load_selection(path)

    def test_rejects_stale_portrait_or_square_render(self) -> None:
        for variant in ("portrait", "square"):
            with self.subTest(variant=variant), tempfile.TemporaryDirectory() as raw:
                root = Path(raw)
                _receipt, portrait, square, *_ = self.create_pair_fixture(root)
                (portrait if variant == "portrait" else square).write_bytes(b"stale")
                with self.assertRaisesRegex(ValueError, variant):
                    cover_receipts.verify_package(
                        root / "selection.json",
                        portrait,
                        m4b_cover_path=square,
                    )

    def test_rejects_rewritten_square_subtitle(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            portrait = make_cover(root / "portrait.png")
            square = make_cover(root / "square.png", size=(2400, 2400))
            portrait_render = write_json(
                root / "portrait.render.json",
                paired_render_payload(root, portrait, "portrait"),
            )
            square_render = write_json(
                root / "square.render.json",
                paired_render_payload(
                    root, square, "square", subtitle="Shortened words"
                ),
            )
            with self.assertRaisesRegex(ValueError, "subtitle"):
                cover_receipts.create_paired_selection(
                    portrait_render,
                    square_render,
                    root / "selection.json",
                    book_slug="fixture-book",
                    edition_id="public-v1",
                    selection_source="user",
                    selected_at="2026-07-13T12:00:00-03:00",
                    privacy_classification="public-safe",
                    permission_to_publish=True,
                )

    def test_rejects_render_identity_that_disagrees_with_spec(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            portrait = make_cover(root / "portrait.png")
            square = make_cover(root / "square.png", size=(2400, 2400))
            portrait_payload = paired_render_payload(root, portrait, "portrait")
            square_payload = paired_render_payload(root, square, "square", subtitle="")
            square_spec = root / str(square_payload["spec"])
            spec = json.loads(square_spec.read_text(encoding="utf-8"))
            spec["candidate"]["id"] = "different-in-spec"
            square_spec.write_text(json.dumps(spec), encoding="utf-8")
            square_payload["spec_sha256"] = hashlib.sha256(
                square_spec.read_bytes()
            ).hexdigest()
            portrait_render = write_json(
                root / "portrait.render.json", portrait_payload
            )
            square_render = write_json(root / "square.render.json", square_payload)

            with self.assertRaisesRegex(ValueError, "candidate"):
                cover_receipts.create_paired_selection(
                    portrait_render,
                    square_render,
                    root / "selection.json",
                    book_slug="fixture-book",
                    edition_id="public-v1",
                    selection_source="user",
                    selected_at="2026-07-13T12:00:00-03:00",
                    privacy_classification="public-safe",
                    permission_to_publish=True,
                )

    def test_verifies_paired_epub_and_m4b_artwork(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            _receipt, portrait, square, *_ = self.create_pair_fixture(root)
            epub = make_epub(root / "book.epub", portrait.read_bytes())
            m4b = root / "book.m4b"
            m4b.write_bytes(b"fixture")
            with mock.patch.object(
                cover_receipts, "normalized_m4b_art_sha256", return_value="a" * 64
            ), mock.patch.object(
                cover_receipts, "normalized_image_sha256", return_value="a" * 64
            ):
                result = cover_receipts.verify_package(
                    root / "selection.json",
                    portrait,
                    m4b_cover_path=square,
                    epub_path=epub,
                    m4b_path=m4b,
                    receipt_path=root / "selection.json",
                )
            self.assertEqual(
                result.checks,
                (
                    "portrait-standalone-bytes",
                    "square-standalone-bytes",
                    "epub-portrait-bytes",
                    "m4b-square-normalized-pixels",
                    "paired-receipt-identity",
                ),
            )

    def test_cli_select_pair_requires_both_render_receipts(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(Path(cover_receipts.__file__)),
                "select-pair",
                "--portrait-render-receipt",
                "portrait.render.json",
            ],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("--square-render-receipt", completed.stderr)

    def test_rejects_duplicate_top_level_key_in_selection_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            cover = make_cover(root / "cover.png")
            selection = root / "duplicate-selection.json"
            selection.write_text(
                raw_selection_receipt(
                    hashlib.sha256(cover.read_bytes()).hexdigest(),
                    duplicate_top_level='"receipt_version": 1,',
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "duplicate key|invalid .*receipt"):
                cover_receipts.load_selection(selection)

    def test_rejects_duplicate_nested_privacy_key_in_selection_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            cover = make_cover(root / "cover.png")
            selection = root / "duplicate-privacy.json"
            selection.write_text(
                raw_selection_receipt(
                    hashlib.sha256(cover.read_bytes()).hexdigest(),
                    duplicate_privacy=',\n    "classification": "public-safe"',
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "duplicate key|invalid .*receipt"):
                cover_receipts.load_selection(selection)

    def test_rejects_duplicate_top_level_key_in_render_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            cover = make_cover(root / "cover.png")
            render = root / "duplicate.render.json"
            render.write_text(
                raw_render_receipt(
                    cover,
                    duplicate_top_level='"receipt_version": 1,',
                ),
                encoding="utf-8",
            )
            output = root / "selection.json"
            output.write_bytes(b"existing selection")

            with self.assertRaisesRegex(ValueError, "duplicate key|invalid .*receipt"):
                cover_receipts.create_selection(
                    render,
                    output,
                    **VALID_SELECTION,
                )
            self.assertEqual(b"existing selection", output.read_bytes())

    def test_rejects_duplicate_nested_candidate_key_in_render_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            cover = make_cover(root / "cover.png")
            render = root / "duplicate-candidate.render.json"
            render.write_text(
                raw_render_receipt(
                    cover,
                    duplicate_candidate=',\n    "id": "c1-full-bleed"',
                ),
                encoding="utf-8",
            )
            output = root / "selection.json"

            with self.assertRaisesRegex(ValueError, "duplicate key|invalid .*receipt"):
                cover_receipts.create_selection(
                    render,
                    output,
                    **VALID_SELECTION,
                )
            self.assertFalse(output.exists())

    def test_creates_explicit_selection_from_verified_render(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            cover = make_cover(root / "cover.png")
            receipt = cover_receipts.create_selection(
                make_render_receipt(root, cover),
                root / "cover-selection.json",
                **VALID_SELECTION,
            )

            cover_hash = hashlib.sha256(cover.read_bytes()).hexdigest()
            self.assertEqual(cover_hash, receipt.rendered_cover_sha256)
            self.assertEqual("c1-full-bleed", receipt.selected_candidate)
            self.assertEqual("Full Bleed Display", receipt.direction_name)
            self.assertEqual("1" * 64, receipt.spec_sha256)
            self.assertEqual("2" * 64, receipt.source_art_sha256)
            self.assertEqual("3" * 64, receipt.font_manifest_sha256)
            self.assertEqual((1600, 2560), receipt.dimensions)
            self.assertEqual(
                {
                    "classification": "public-safe",
                    "permission_to_publish": "granted",
                },
                receipt.privacy,
            )
            self.assertTrue((root / "cover-selection.json").is_file())

    def test_requested_mix_is_an_explicit_selection_source(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            cover = make_cover(root / "cover.png")
            arguments = dict(VALID_SELECTION)
            arguments["selection_source"] = "requested-mix"

            receipt = cover_receipts.create_selection(
                make_render_receipt(root, cover),
                root / "selection.json",
                **arguments,
            )

            self.assertEqual("requested-mix", receipt.selection_source)

    def test_rejects_automatic_or_tampered_selection(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            cover = make_cover(root / "cover.png")
            render = make_render_receipt(root, cover)
            arguments = dict(VALID_SELECTION)
            arguments["selection_source"] = "first-valid"
            with self.assertRaisesRegex(ValueError, "selection_source"):
                cover_receipts.create_selection(
                    render,
                    root / "selection.json",
                    **arguments,
                )

            cover.write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "rendered cover hash mismatch"):
                cover_receipts.create_selection(
                    render,
                    root / "selection.json",
                    **VALID_SELECTION,
                )

    def test_verifies_cover_epub_and_receipt_identity(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            cover = make_cover(root / "cover.png")
            selection = create_valid_selection(root, cover)
            epub = make_epub(root / "book.epub", cover.read_bytes())

            result = cover_receipts.verify_package(
                selection,
                cover,
                epub_path=epub,
                receipt_path=selection,
            )

            self.assertEqual(
                ("standalone-bytes", "epub-cover-bytes", "receipt-identity"),
                result.checks,
            )

    def test_rejects_stale_epub_and_normalizes_m4b_art(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            cover = make_cover(root / "cover.png")
            selection = create_valid_selection(root, cover)
            stale = make_cover(root / "stale.png", "#FFFFFF")
            epub = make_epub(root / "stale.epub", stale.read_bytes())
            with self.assertRaisesRegex(ValueError, "EPUB cover bytes do not match"):
                cover_receipts.verify_package(selection, cover, epub_path=epub)

            m4b = root / "book.m4b"
            m4b.write_bytes(b"fixture")
            with mock.patch.object(
                cover_receipts,
                "normalized_image_sha256",
                return_value="a" * 64,
            ), mock.patch.object(
                cover_receipts,
                "normalized_m4b_art_sha256",
                return_value="a" * 64,
            ):
                result = cover_receipts.verify_package(
                    selection,
                    cover,
                    m4b_path=m4b,
                )
            self.assertIn("m4b-normalized-pixels", result.checks)

    def test_rejects_render_output_path_escape_and_absolute_reference(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            workspace = Path(raw)
            root = workspace / "run"
            root.mkdir()
            cover = make_cover(root / "cover.png")
            outside = make_cover(workspace / "outside.png")
            cases = {
                "parent escape": "../outside.png",
                "absolute": str(cover.resolve()),
            }
            for name, output in cases.items():
                with self.subTest(name=name):
                    payload = render_payload(cover)
                    payload["output"] = output
                    payload["output_sha256"] = hashlib.sha256(
                        (outside if name == "parent escape" else cover).read_bytes()
                    ).hexdigest()
                    render = make_render_receipt(root, cover, payload)
                    with self.assertRaisesRegex(ValueError, "render output"):
                        cover_receipts.create_selection(
                            render,
                            root / "selection.json",
                            **VALID_SELECTION,
                        )

    def test_rejects_malformed_render_receipt_shapes_types_and_unknown_fields(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            cover = make_cover(root / "cover.png")
            base = render_payload(cover)
            cases: dict[str, object] = {
                "root array": [],
                "unknown top-level": {**base, "unexpected": True},
                "boolean receipt version": {**base, "receipt_version": True},
                "candidate array": {**base, "candidate": []},
                "candidate unknown field": {
                    **base,
                    "candidate": {
                        "id": "c1-full-bleed",
                        "direction_name": "Full Bleed Display",
                        "rank": 1,
                    },
                },
                "fonts array": {**base, "fonts": []},
                "bad font hash": {**base, "fonts": {"display-condensed": True}},
                "warnings contain boolean": {**base, "warnings": [False]},
                "bad output hash": {**base, "output_sha256": "xyz"},
            }
            for name, payload in cases.items():
                with self.subTest(name=name):
                    render = make_render_receipt(root, cover, payload)
                    output = root / "selection.json"
                    with self.assertRaises(ValueError):
                        cover_receipts.create_selection(
                            render,
                            output,
                            **VALID_SELECTION,
                        )
                    self.assertFalse(output.exists())

    def test_rejects_invalid_identity_privacy_and_naive_timestamp_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            cover = make_cover(root / "cover.png")
            render = make_render_receipt(root, cover)
            cases: dict[str, object] = {
                "book_slug": "Rodents In The Walls",
                "edition_id": "../corrected-v2",
                "selection_source": True,
                "selected_at": "2026-07-12T13:00:00",
                "classification": True,
                "permission_to_publish": False,
            }
            for field, value in cases.items():
                with self.subTest(field=field):
                    arguments = dict(VALID_SELECTION)
                    arguments[field] = value
                    output = root / "nested" / "selection.json"
                    with self.assertRaises(ValueError):
                        cover_receipts.create_selection(
                            render,
                            output,
                            **arguments,
                        )
                    self.assertFalse(output.exists())
                    self.assertFalse(output.parent.exists())

    def test_rejects_malformed_selection_shapes_types_and_unknown_fields(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            cover = make_cover(root / "cover.png")
            selection = create_valid_selection(root, cover)
            base = json.loads(selection.read_text(encoding="utf-8"))
            cases: dict[str, object] = {
                "root array": [],
                "unknown top-level": {**base, "unexpected": True},
                "boolean version": {**base, "receipt_version": True},
                "direction type": {**base, "direction_name": 4},
                "candidate path": {**base, "selected_candidate": "../candidate"},
                "edition path": {**base, "edition_id": "../v2"},
                "naive timestamp": {
                    **base,
                    "selected_at": "2026-07-12T13:00:00",
                },
                "bad dimensions": {**base, "dimensions": "1600x2560"},
                "bad hash": {**base, "spec_sha256": "A" * 64},
                "privacy array": {**base, "privacy": []},
                "privacy unknown field": {
                    **base,
                    "privacy": {
                        "classification": "public-safe",
                        "permission_to_publish": "granted",
                        "approved_by": "agent",
                    },
                },
            }
            for name, payload in cases.items():
                with self.subTest(name=name):
                    candidate = write_json(root / "candidate-selection.json", payload)
                    with self.assertRaises(ValueError):
                        cover_receipts.load_selection(candidate)

    def test_missing_or_malformed_files_fail_with_value_errors(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            cover = make_cover(root / "cover.png")
            with self.assertRaises(ValueError):
                cover_receipts.create_selection(
                    root / "missing.render.json",
                    root / "selection.json",
                    **VALID_SELECTION,
                )

            render = make_render_receipt(root, cover)
            cover.unlink()
            with self.assertRaisesRegex(ValueError, "rendered cover"):
                cover_receipts.create_selection(
                    render,
                    root / "selection.json",
                    **VALID_SELECTION,
                )

            cover = make_cover(root / "cover.png")
            selection = create_valid_selection(root, cover)
            with self.assertRaisesRegex(ValueError, "standalone cover"):
                cover_receipts.verify_package(selection, root / "missing.png")

            malformed_epub = root / "malformed.epub"
            malformed_epub.write_bytes(b"not a zip")
            with self.assertRaisesRegex(ValueError, "EPUB"):
                cover_receipts.verify_package(
                    selection,
                    cover,
                    epub_path=malformed_epub,
                )

    def test_rejects_actual_cover_with_wrong_dimensions_or_colour_mode(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            cases = {
                "dimensions": {"size": (16, 25), "mode": "RGB"},
                "colour mode": {"size": (1600, 2560), "mode": "L"},
            }
            for name, options in cases.items():
                with self.subTest(name=name):
                    cover = make_cover(
                        root / f"{name.replace(' ', '-')}.png",
                        "#132238" if options["mode"] == "RGB" else 19,
                        mode=str(options["mode"]),
                        size=options["size"],
                    )
                    payload = render_payload(cover)
                    render = make_render_receipt(root, cover, payload)
                    with self.assertRaisesRegex(ValueError, "1600x2560 RGB"):
                        cover_receipts.create_selection(
                            render,
                            root / "selection.json",
                            **VALID_SELECTION,
                        )

    def test_selection_output_cannot_alias_render_receipt_or_cover(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            cover = make_cover(root / "cover.png")
            render = make_render_receipt(root, cover)
            original_render = render.read_bytes()
            original_cover = cover.read_bytes()
            symlink = root / "selection-symlink.json"
            symlink.symlink_to(cover.name)
            hardlink = root / "selection-hardlink.json"
            os.link(cover, hardlink)
            aliases = {
                "render receipt": render,
                "rendered cover": cover,
                "rendered cover symlink": symlink,
                "rendered cover hardlink": hardlink,
            }
            for name, output in aliases.items():
                with self.subTest(name=name):
                    with self.assertRaisesRegex(ValueError, "selection output aliases"):
                        cover_receipts.create_selection(
                            render,
                            output,
                            **VALID_SELECTION,
                        )
            self.assertEqual(original_render, render.read_bytes())
            self.assertEqual(original_cover, cover.read_bytes())

    def test_validation_failure_writes_nothing_and_atomic_failure_cleans_up(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            cover = make_cover(root / "cover.png")
            render = make_render_receipt(root, cover)
            invalid = dict(VALID_SELECTION)
            invalid["selected_at"] = "not-a-time"
            nested_output = root / "nested" / "selection.json"
            with self.assertRaises(ValueError):
                cover_receipts.create_selection(
                    render,
                    nested_output,
                    **invalid,
                )
            self.assertFalse(nested_output.parent.exists())

            output = root / "selection.json"
            output.write_bytes(b"existing receipt")
            with mock.patch.object(
                cover_receipts.os,
                "replace",
                side_effect=OSError("publish failed"),
            ), self.assertRaisesRegex(ValueError, "selection receipt"):
                cover_receipts.create_selection(
                    render,
                    output,
                    **VALID_SELECTION,
                )
            self.assertEqual(b"existing receipt", output.read_bytes())
            self.assertEqual([], list(root.glob(".selection.json.*.tmp")))

    def test_receipt_identity_detects_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            cover = make_cover(root / "cover.png")
            selection = create_valid_selection(root, cover)
            payload = json.loads(selection.read_text(encoding="utf-8"))
            payload["edition_id"] = "v3"
            delivered = write_json(root / "delivered-selection.json", payload)

            with self.assertRaisesRegex(ValueError, "receipt does not match"):
                cover_receipts.verify_package(
                    selection,
                    cover,
                    receipt_path=delivered,
                )

    def test_normalized_artwork_hash_includes_oriented_dimensions(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            image = root / "art.png"
            image.write_bytes(b"fixture")
            pixels = b"\x10\x20\x30" * 2
            one_by_two = subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout=b"P6\n1 2\n255\n" + pixels,
                stderr=b"",
            )
            two_by_one = subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout=b"P6\n2 1\n255\n" + pixels,
                stderr=b"",
            )
            with mock.patch.object(
                cover_receipts.shutil,
                "which",
                return_value="/usr/local/bin/magick",
            ), mock.patch.object(
                cover_receipts.subprocess,
                "run",
                side_effect=[one_by_two, two_by_one],
            ) as run:
                first = cover_receipts.normalized_image_sha256(image)
                second = cover_receipts.normalized_image_sha256(image)

            self.assertNotEqual(first, second)
            for call in run.call_args_list:
                command = call.args[0]
                self.assertIn("-auto-orient", command)
                self.assertEqual("PPM:-", command[-1])

    def test_normalization_subprocess_failures_are_value_errors(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            image = root / "art.png"
            image.write_bytes(b"fixture")
            failure = subprocess.CalledProcessError(
                1,
                ["magick"],
                stderr=b"decoder failed",
            )
            with mock.patch.object(
                cover_receipts.shutil,
                "which",
                return_value="/usr/local/bin/magick",
            ), mock.patch.object(
                cover_receipts.subprocess,
                "run",
                side_effect=failure,
            ), self.assertRaisesRegex(
                ValueError, "ImageMagick"
            ):
                cover_receipts.normalized_image_sha256(image)

            m4b = root / "book.m4b"
            m4b.write_bytes(b"fixture")
            with mock.patch.object(
                cover_receipts.shutil,
                "which",
                return_value="/usr/local/bin/ffmpeg",
            ), mock.patch.object(
                cover_receipts.subprocess,
                "run",
                side_effect=subprocess.CalledProcessError(
                    1,
                    ["ffmpeg"],
                    stderr=b"no artwork",
                ),
            ), self.assertRaisesRegex(
                ValueError, "ffmpeg"
            ):
                cover_receipts.normalized_m4b_art_sha256(m4b)

    def test_select_cli_prints_machine_readable_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            cover = make_cover(root / "cover.png")
            render = make_render_receipt(root, cover)
            output = root / "selection.json"
            argv = [
                "cover_receipts.py",
                "select",
                "--render-receipt",
                str(render),
                "--out",
                str(output),
                "--book-slug",
                "rodents-in-the-walls",
                "--edition-id",
                "corrected-v2",
                "--selection-source",
                "explicit-user-choice",
                "--selected-at",
                "2026-07-12T13:00:00-03:00",
                "--classification",
                "public-safe",
                "--permission-to-publish",
                "granted",
            ]
            stdout = io.StringIO()
            with mock.patch.object(sys, "argv", argv), redirect_stdout(stdout):
                self.assertEqual(0, cover_receipts.main())

            payload = json.loads(stdout.getvalue())
            self.assertEqual("rodents-in-the-walls", payload["book_slug"])
            self.assertEqual("c1-full-bleed", payload["selected_candidate"])
            self.assertTrue(output.is_file())


if __name__ == "__main__":
    unittest.main()
