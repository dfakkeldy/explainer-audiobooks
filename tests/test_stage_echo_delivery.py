from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import shutil
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).parents[1]
MODULE_PATH = (
    ROOT / "skills" / "fiction-audiobook" / "scripts" / "stage_echo_delivery.py"
)
SPEC = importlib.util.spec_from_file_location("stage_echo_delivery_test_module", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {MODULE_PATH}")
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


def tree_hash(root: Path) -> str:
    """Hash names, kinds, and file bytes for a test fixture tree."""
    digest = hashlib.sha256()
    for path in sorted(
        root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()
    ):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            kind = "symlink"
            payload = path.readlink().as_posix().encode()
        elif path.is_dir():
            kind = "directory"
            payload = b""
        else:
            kind = "file"
            payload = path.read_bytes()
        digest.update(
            kind.encode() + b"\0" + relative.encode() + b"\0" + payload + b"\0"
        )
    return digest.hexdigest()


class StageEchoDeliveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        self.inputs = self.root / "inputs"
        self.inputs.mkdir()
        self.m4b = self.inputs / "fixture.m4b"
        self.epub = self.inputs / "fixture.epub"
        self.alignment = self.inputs / "fixture.alignment.json"
        self.cover = self.inputs / "cover.png"
        self.m4b.write_bytes(b"audio")
        self.epub.write_bytes(b"epub")
        self.alignment.write_text('{"anchors": [1]}\n', encoding="utf-8")
        self.cover.write_bytes(b"png")

        self.production = self.root / "production"
        for name in ("source", "checks", "narration", "covers", "publication", "previous"):
            directory = self.production / name
            directory.mkdir(parents=True)
            if name != "previous":
                (directory / f"{name}.txt").write_text(
                    f"{name} evidence\n", encoding="utf-8"
                )
        self.destination = self.root / "library" / "fixture"
        self.destination.parent.mkdir()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def request(self, **changes: object) -> object:
        request = module.DeliveryRequest(
            slug="fixture",
            edition_id="fixture-v2",
            m4b=self.m4b,
            epub=self.epub,
            alignment=self.alignment,
            cover=self.cover,
            production=self.production,
            destination=self.destination,
        )
        return replace(request, **changes)

    def stages(self) -> list[Path]:
        return list(self.destination.parent.glob(".fixture.staging-*"))

    def test_apply_promotes_only_four_loadable_files_and_production(self) -> None:
        result = module.stage_delivery(self.request(), apply=True)

        self.assertEqual("promoted", result.decision)
        self.assertTrue(result.applied)
        self.assertEqual(
            {
                "fixture.m4b",
                "fixture.epub",
                "fixture.alignment.json",
                "cover.png",
                "_production",
            },
            {path.name for path in self.destination.iterdir()},
        )
        manifest_path = self.destination / "_production/checks/delivery-manifest.json"
        self.assertTrue(manifest_path.is_file())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(1, manifest["schemaVersion"])
        self.assertEqual("fixture", manifest["slug"])
        self.assertEqual("fixture-v2", manifest["editionId"])
        self.assertEqual(
            {
                "fixture.m4b": hashlib.sha256(b"audio").hexdigest(),
                "fixture.epub": hashlib.sha256(b"epub").hexdigest(),
                "fixture.alignment.json": hashlib.sha256(
                    b'{"anchors": [1]}\n'
                ).hexdigest(),
                "cover.png": hashlib.sha256(b"png").hexdigest(),
            },
            manifest["rootArtifacts"],
        )

    def test_internal_narration_evidence_stays_below_production_root(self) -> None:
        internal_evidence = {
            "narration/echo-voice-plan.json": b"authored plan",
            "narration/echo-voice-plan-plan-" + "b" * 64 + ".json": b"canonical plan",
            "narration/echo-voice-plan-resolution-plan-" + "b" * 64 + ".json": b"resolution receipt",
            "narration/echo-render-inputs-fixture.env": b"input receipt",
            "narration/echo-render-success-fixture.json": b"success receipt",
            "narration/audio-work-fixture/.anchors-ch1.json": b"capture",
            "narration/listening/fixture/attempt/pronunciation-reel.m4a": b"reel",
            "checks/fixture.pronunciation-audit.json": b"audit",
        }
        for relative, payload in internal_evidence.items():
            destination = self.production / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(payload)

        module.stage_delivery(self.request(), apply=True)

        root_entries = list(self.destination.iterdir())
        self.assertEqual(
            {
                "fixture.m4b",
                "fixture.epub",
                "fixture.alignment.json",
                "cover.png",
                "_production",
            },
            {path.name for path in root_entries},
        )
        self.assertEqual(1, sum(path.suffix == ".m4b" for path in root_entries))
        self.assertEqual(1, sum(path.suffix == ".epub" for path in root_entries))
        self.assertEqual(
            1,
            sum(path.name.endswith(".alignment.json") for path in root_entries),
        )
        self.assertEqual(1, sum(path.name == "cover.png" for path in root_entries))
        self.assertEqual(1, sum(path.name == "_production" for path in root_entries))
        self.assertTrue((self.destination / "_production").is_dir())

        staged_evidence = {
            path.relative_to(self.destination / "_production").as_posix(): path.read_bytes()
            for path in (self.destination / "_production").rglob("*")
            if path.is_file()
            and path.relative_to(self.destination / "_production").as_posix()
            in internal_evidence
        }
        self.assertEqual(internal_evidence, staged_evidence)
        self.assertFalse(
            any(
                path.name in {Path(relative).name for relative in internal_evidence}
                for path in root_entries
            )
        )

    def test_empty_destination_created_in_rename_window_is_not_replaced(self) -> None:
        real_rename_stage = module._rename_stage
        intruder_identity: tuple[int, int] | None = None

        def create_destination_then_rename(stage: Path, destination: Path) -> None:
            nonlocal intruder_identity
            destination.mkdir()
            opened = destination.stat(follow_symlinks=False)
            intruder_identity = (opened.st_dev, opened.st_ino)
            real_rename_stage(stage, destination)

        with mock.patch.object(
            module, "_rename_stage", side_effect=create_destination_then_rename
        ), self.assertRaisesRegex(ValueError, "appeared|destination|exclusive"):
            module.stage_delivery(self.request(), apply=True)

        self.assertIsNotNone(intruder_identity)
        current = self.destination.stat(follow_symlinks=False)
        self.assertEqual(intruder_identity, (current.st_dev, current.st_ino))
        self.assertEqual([], list(self.destination.iterdir()))
        self.assertTrue(self.stages())

    def test_stage_symlink_rejected_during_first_promotion_is_rolled_back(self) -> None:
        real_rename_stage = module._rename_stage
        parked_stage: Path | None = None

        def replace_stage_with_symlink(stage: Path, destination: Path) -> None:
            nonlocal parked_stage
            parked_stage = stage.with_name(f"{stage.name}.parked")
            stage.rename(parked_stage)
            stage.symlink_to(parked_stage, target_is_directory=True)
            real_rename_stage(stage, destination)

        with mock.patch.object(
            module, "_rename_stage", side_effect=replace_stage_with_symlink
        ), self.assertRaises((OSError, ValueError)):
            module.stage_delivery(self.request(), apply=True)

        self.assertFalse(self.destination.exists())
        self.assertFalse(self.destination.is_symlink())
        stages = self.stages()
        self.assertEqual(2, len(stages))
        self.assertEqual(1, sum(path.is_symlink() for path in stages))
        self.assertIsNotNone(parked_stage)
        self.assertTrue(parked_stage.is_dir())

    def test_unexpected_root_item_is_preserved_and_blocks_promotion(self) -> None:
        module.stage_delivery(self.request(), apply=True)
        note = self.destination / "my-note.txt"
        note.write_text("keep me", encoding="utf-8")
        self.m4b.write_bytes(b"new audio")

        with self.assertRaisesRegex(ValueError, "my-note.txt"):
            module.stage_delivery(self.request(), apply=True)

        self.assertEqual("keep me", note.read_text(encoding="utf-8"))
        self.assertEqual(b"audio", (self.destination / "fixture.m4b").read_bytes())
        self.assertTrue(self.stages())

    def test_item_added_after_validation_is_preserved_and_blocks_promotion(self) -> None:
        module.stage_delivery(self.request(), apply=True)
        before = tree_hash(self.destination)
        self.m4b.write_bytes(b"replacement")
        real_promote = module._promote
        note = self.destination / "notes.m4a"

        def inject_then_promote(
            stage: Path,
            destination: Path,
            expected_destination: object,
        ) -> None:
            note.write_bytes(b"user recording")
            real_promote(stage, destination, expected_destination)

        with mock.patch.object(
            module, "_promote", side_effect=inject_then_promote
        ), self.assertRaisesRegex(ValueError, "notes.m4a|changed.*validation"):
            module.stage_delivery(self.request(), apply=True)

        self.assertEqual(b"user recording", note.read_bytes())
        note.unlink()
        self.assertEqual(before, tree_hash(self.destination))
        self.assertTrue(self.stages())
        self.assertEqual([], list(self.destination.parent.glob(".fixture.backup-*")))

    def test_destination_replaced_before_atomic_exchange_preserves_every_tree(self) -> None:
        module.stage_delivery(self.request(), apply=True)
        self.m4b.write_bytes(b"replacement")
        moved_original = self.destination.parent / "externally-moved-original"
        real_exchange = module._rename_exchange
        replaced = False

        def replace_then_exchange(source: Path, destination: Path) -> None:
            nonlocal replaced
            if not replaced:
                replaced = True
                destination.rename(moved_original)
                destination.mkdir()
                (destination / "notes.m4a").write_bytes(b"user replacement")
            real_exchange(source, destination)

        with mock.patch.object(
            module, "_rename_exchange", side_effect=replace_then_exchange
        ), self.assertRaisesRegex(ValueError, "prior destination.*changed"):
            module.stage_delivery(self.request(), apply=True)

        self.assertEqual(
            b"user replacement", (self.destination / "notes.m4a").read_bytes()
        )
        self.assertEqual(b"audio", (moved_original / "fixture.m4b").read_bytes())
        self.assertTrue(self.stages())
        self.assertEqual([], list(self.destination.parent.glob(".fixture.backup-*")))

    def test_dangling_stage_symlink_during_exchange_restores_old_destination(self) -> None:
        module.stage_delivery(self.request(), apply=True)
        self.m4b.write_bytes(b"replacement")
        real_exchange = module._rename_exchange
        parked_stage: Path | None = None
        swapped = False

        def replace_stage_then_exchange(source: Path, destination: Path) -> None:
            nonlocal parked_stage, swapped
            if not swapped:
                swapped = True
                parked_stage = source.with_name(f"{source.name}.verified")
                source.rename(parked_stage)
                source.symlink_to(source.parent / "missing-stage-target")
            real_exchange(source, destination)

        with mock.patch.object(
            module, "_rename_exchange", side_effect=replace_stage_then_exchange
        ), self.assertRaisesRegex(ValueError, "promoted delivery|symlink"):
            module.stage_delivery(self.request(), apply=True)

        self.assertEqual(b"audio", (self.destination / "fixture.m4b").read_bytes())
        self.assertEqual(1, sum(path.is_symlink() for path in self.stages()))
        self.assertIsNotNone(parked_stage)
        self.assertEqual(b"replacement", (parked_stage / "fixture.m4b").read_bytes())

    def test_promotion_failure_restores_the_complete_old_edition(self) -> None:
        module.stage_delivery(self.request(), apply=True)
        before = tree_hash(self.destination)
        self.m4b.write_bytes(b"replacement")

        with mock.patch.object(
            module, "_rename_exchange", side_effect=OSError("injected")
        ):
            with self.assertRaisesRegex(OSError, "injected"):
                module.stage_delivery(self.request(), apply=True)

        self.assertEqual(before, tree_hash(self.destination))

    def test_item_added_to_renamed_backup_is_restored_instead_of_deleted(self) -> None:
        module.stage_delivery(self.request(), apply=True)
        self.m4b.write_bytes(b"replacement")
        real_rename_exclusive = module._rename_exclusive

        def mutate_prior_then_archive(source: Path, destination: Path) -> None:
            if destination.name == "previous":
                (source / "notes.m4a").write_bytes(b"late user recording")
            real_rename_exclusive(source, destination)

        with mock.patch.object(
            module, "_rename_exclusive", side_effect=mutate_prior_then_archive
        ), self.assertRaisesRegex(ValueError, "archived prior destination.*changed"):
            module.stage_delivery(self.request(), apply=True)

        self.assertEqual(
            b"late user recording", (self.destination / "notes.m4a").read_bytes()
        )
        self.assertEqual(b"audio", (self.destination / "fixture.m4b").read_bytes())
        self.assertTrue(self.stages())
        self.assertEqual([], list(self.destination.parent.glob(".fixture.backup-*")))

    def test_rollback_restores_old_live_before_staging_repair_failure(self) -> None:
        module.stage_delivery(self.request(), apply=True)
        self.m4b.write_bytes(b"replacement")
        real_rename_exclusive = module._rename_exclusive
        real_mkdir = module.Path.mkdir

        def mutate_prior_then_archive(source: Path, destination: Path) -> None:
            if destination.name == "previous":
                (source / "notes.m4a").write_bytes(b"late user recording")
            real_rename_exclusive(source, destination)

        def fail_previous_recreation(path: Path, *args: object, **kwargs: object):
            if path.name == "previous":
                raise OSError("injected previous mkdir failure")
            return real_mkdir(path, *args, **kwargs)

        with mock.patch.object(
            module, "_rename_exclusive", side_effect=mutate_prior_then_archive
        ), mock.patch.object(
            module.Path, "mkdir", autospec=True, side_effect=fail_previous_recreation
        ), self.assertRaisesRegex(OSError, "injected previous mkdir failure"):
            module.stage_delivery(self.request(), apply=True)

        self.assertEqual(b"audio", (self.destination / "fixture.m4b").read_bytes())
        self.assertEqual(
            b"late user recording", (self.destination / "notes.m4a").read_bytes()
        )
        self.assertTrue(self.stages())

    def test_prior_destination_is_never_recursively_deleted_after_promotion(self) -> None:
        module.stage_delivery(self.request(), apply=True)
        self.m4b.write_bytes(b"replacement")
        real_rmtree = module.shutil.rmtree

        def reject_old_destination_deletion(path: Path, *args: object, **kwargs: object):
            if Path(path).name.startswith(".fixture.backup-"):
                raise AssertionError("validated prior destination must never be deleted")
            return real_rmtree(path, *args, **kwargs)

        with mock.patch.object(
            module.shutil, "rmtree", side_effect=reject_old_destination_deletion
        ):
            result = module.stage_delivery(self.request(), apply=True)

        self.assertEqual("promoted", result.decision)
        previous = self.destination / "_production/previous"
        self.assertEqual(b"audio", (previous / "fixture.m4b").read_bytes())

    def test_redo_archives_one_prior_generated_edition_and_is_idempotent(self) -> None:
        module.stage_delivery(self.request(), apply=True)
        self.m4b.write_bytes(b"replacement")
        module.stage_delivery(self.request(), apply=True)
        previous = self.destination / "_production/previous"

        self.assertEqual(b"audio", (previous / "fixture.m4b").read_bytes())
        self.assertEqual(b"epub", (previous / "fixture.epub").read_bytes())
        self.assertTrue((previous / "_production/checks/checks.txt").is_file())
        self.assertTrue((previous / "_production/previous").is_dir())
        self.assertEqual([], list((previous / "_production/previous").iterdir()))

        before = tree_hash(self.destination)
        result = module.stage_delivery(self.request(), apply=True)
        self.assertEqual("reuse", result.decision)
        self.assertEqual(before, tree_hash(self.destination))
        self.assertEqual([], self.stages())

    def test_repeated_promotions_preserve_the_complete_prior_chain(self) -> None:
        module.stage_delivery(self.request(), apply=True)
        self.m4b.write_bytes(b"second")
        module.stage_delivery(self.request(), apply=True)
        self.m4b.write_bytes(b"third")
        module.stage_delivery(self.request(), apply=True)

        previous = self.destination / "_production/previous"
        first = previous / "_production/previous"
        self.assertEqual(b"third", (self.destination / "fixture.m4b").read_bytes())
        self.assertEqual(b"second", (previous / "fixture.m4b").read_bytes())
        self.assertEqual(b"audio", (first / "fixture.m4b").read_bytes())
        self.assertEqual([], list(self.destination.parent.glob(".fixture.backup-*")))
        self.assertEqual([], self.stages())

    def test_m4b_epub_and_sidecar_must_have_the_slug_stem(self) -> None:
        for field, name in (
            ("m4b", "other.m4b"),
            ("epub", "other.epub"),
            ("alignment", "other.alignment.json"),
        ):
            with self.subTest(field=field):
                path = self.inputs / name
                path.write_bytes(getattr(self, field).read_bytes())
                with self.assertRaisesRegex(
                    ValueError, f"fixture.*{field}|{field}.*fixture"
                ):
                    module.stage_delivery(self.request(**{field: path}), apply=True)
                self.assertFalse(self.destination.exists())
                self.assertEqual([], self.stages())

    def test_alignment_must_exist_and_contain_nonempty_valid_json(self) -> None:
        missing = self.inputs / "fixture.alignment.json"
        self.alignment.unlink()
        with self.assertRaisesRegex(ValueError, "alignment"):
            module.stage_delivery(self.request(alignment=missing), apply=True)

        cases = (
            (b"", "alignment"),
            (b"not json", "JSON"),
            (b"{}", "nonempty"),
            (b"[]", "nonempty"),
            (b'"text"', "object or array"),
            (b'{"value": NaN}', "JSON"),
            (b'{"value": Infinity}', "JSON"),
            (b'{"value": -Infinity}', "JSON"),
        )
        for payload, message in cases:
            with self.subTest(payload=payload):
                self.alignment.write_bytes(payload)
                with self.assertRaisesRegex(ValueError, message):
                    module.stage_delivery(self.request(), apply=True)
                self.assertFalse(self.destination.exists())
                self.assertEqual([], self.stages())

    def test_staged_hash_drift_is_rejected_before_promotion(self) -> None:
        real_copy = module._copy_root_artifact

        def drifting_copy(source: Path, destination: Path) -> None:
            real_copy(source, destination)
            if destination.name == "fixture.m4b":
                destination.write_bytes(b"changed while staging")

        with mock.patch.object(module, "_copy_root_artifact", side_effect=drifting_copy):
            with self.assertRaisesRegex(ValueError, "hash.*drift|drift.*hash"):
                module.stage_delivery(self.request(), apply=True)

        self.assertFalse(self.destination.exists())
        self.assertEqual([], self.stages())

    def test_extra_root_audio_is_preserved_and_blocks_promotion(self) -> None:
        module.stage_delivery(self.request(), apply=True)
        extra = self.destination / "chapter-one.mp3"
        extra.write_bytes(b"competing audio")
        before = tree_hash(self.destination)
        self.m4b.write_bytes(b"replacement")

        with self.assertRaisesRegex(ValueError, "chapter-one.mp3"):
            module.stage_delivery(self.request(), apply=True)

        self.assertEqual(before, tree_hash(self.destination))
        self.assertTrue(self.stages())

    def test_source_and_destination_symlinks_are_rejected(self) -> None:
        target = self.inputs / "target.m4b"
        target.write_bytes(b"audio")
        self.m4b.unlink()
        self.m4b.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "symlink"):
            module.stage_delivery(self.request(), apply=True)
        self.m4b.unlink()
        self.m4b.write_bytes(b"audio")

        nested_target = self.root / "outside.txt"
        nested_target.write_text("outside", encoding="utf-8")
        (self.production / "checks/link.txt").symlink_to(nested_target)
        with self.assertRaisesRegex(ValueError, "symlink"):
            module.stage_delivery(self.request(), apply=True)
        (self.production / "checks/link.txt").unlink()

        destination_target = self.root / "destination-target"
        destination_target.mkdir()
        self.destination.symlink_to(destination_target, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            module.stage_delivery(self.request(), apply=True)
        self.assertEqual([], list(destination_target.iterdir()))

    def test_symlink_inside_an_existing_destination_is_a_preserved_conflict(self) -> None:
        module.stage_delivery(self.request(), apply=True)
        real_audio = self.root / "real-audio"
        (self.destination / "fixture.m4b").rename(real_audio)
        (self.destination / "fixture.m4b").symlink_to(real_audio)
        before = tree_hash(self.destination)
        self.m4b.write_bytes(b"replacement")

        with self.assertRaisesRegex(ValueError, "symlink"):
            module.stage_delivery(self.request(), apply=True)

        self.assertEqual(before, tree_hash(self.destination))
        self.assertTrue(self.stages())

    def test_dry_run_validates_without_mutating_or_staging(self) -> None:
        before = tree_hash(self.root)

        result = module.stage_delivery(self.request(), apply=False)

        self.assertFalse(result.applied)
        self.assertEqual("promote", result.decision)
        self.assertIsNone(result.staging_directory)
        self.assertEqual(before, tree_hash(self.root))
        self.assertFalse(self.destination.exists())
        self.assertEqual([], self.stages())

    def test_dry_run_rejects_an_existing_destination_conflict_without_staging(self) -> None:
        module.stage_delivery(self.request(), apply=True)
        note = self.destination / "my-note.txt"
        note.write_text("keep", encoding="utf-8")
        before = tree_hash(self.root)

        with self.assertRaisesRegex(ValueError, "my-note.txt"):
            module.stage_delivery(self.request(), apply=False)

        self.assertEqual(before, tree_hash(self.root))
        self.assertEqual([], self.stages())

    def test_slug_edition_and_production_shape_are_validated(self) -> None:
        for slug in ("", "Fixture", "fixture_name", "-fixture", "fixture-"):
            with self.subTest(slug=slug):
                with self.assertRaisesRegex(ValueError, "slug"):
                    module.stage_delivery(self.request(slug=slug), apply=True)
        with self.assertRaisesRegex(ValueError, "edition"):
            module.stage_delivery(self.request(edition_id=""), apply=True)

        extra = self.production / "scratch"
        extra.mkdir()
        with self.assertRaisesRegex(ValueError, "scratch"):
            module.stage_delivery(self.request(), apply=True)
        extra.rmdir()

        (self.production / "previous").rmdir()
        (self.production / "previous").write_text("not a directory", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "previous"):
            module.stage_delivery(self.request(), apply=True)

    def test_existing_destination_must_have_every_generated_entry(self) -> None:
        module.stage_delivery(self.request(), apply=True)
        (self.destination / "cover.png").unlink()
        before = tree_hash(self.destination)

        with self.assertRaisesRegex(ValueError, "cover.png"):
            module.stage_delivery(self.request(), apply=True)

        self.assertEqual(before, tree_hash(self.destination))
        self.assertTrue(self.stages())

    def test_existing_destination_requires_a_hash_bound_generated_manifest(self) -> None:
        mutations = {
            "missing": None,
            "malformed": b"{",
            "wrong schema": {"schemaVersion": 2},
            "wrong slug": {"slug": "other"},
            "empty edition": {"editionId": ""},
            "wrong artifact names": {
                "rootArtifacts": {
                    "fixture.m4b": hashlib.sha256(b"audio").hexdigest()
                }
            },
            "wrong live hash": {
                "rootArtifacts": {
                    "fixture.m4b": "0" * 64,
                    "fixture.epub": hashlib.sha256(b"epub").hexdigest(),
                    "fixture.alignment.json": hashlib.sha256(
                        b'{"anchors": [1]}\n'
                    ).hexdigest(),
                    "cover.png": hashlib.sha256(b"png").hexdigest(),
                }
            },
        }
        for label, mutation in mutations.items():
            with self.subTest(label=label):
                if self.destination.exists():
                    shutil.rmtree(self.destination)
                for stage in self.stages():
                    shutil.rmtree(stage)
                module.stage_delivery(self.request(), apply=True)
                previous_marker = self.destination / "_production/previous/keep.txt"
                previous_marker.write_text("preserve prior archive", encoding="utf-8")
                manifest_path = (
                    self.destination / "_production/checks/delivery-manifest.json"
                )
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                if mutation is None:
                    manifest_path.unlink()
                elif isinstance(mutation, bytes):
                    manifest_path.write_bytes(mutation)
                else:
                    manifest.update(mutation)
                    manifest_path.write_text(
                        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8",
                    )
                before = tree_hash(self.destination)

                with self.assertRaisesRegex(ValueError, "delivery manifest"):
                    module.stage_delivery(self.request(), apply=True)

                self.assertEqual(before, tree_hash(self.destination))
                self.assertEqual(
                    "preserve prior archive",
                    previous_marker.read_text(encoding="utf-8"),
                )
                self.assertTrue(self.stages())

    def test_cli_prints_sorted_dry_run_result_without_mutation(self) -> None:
        output = io.StringIO()
        arguments = [
            "--slug", "fixture",
            "--edition-id", "fixture-v2",
            "--m4b", str(self.m4b),
            "--epub", str(self.epub),
            "--alignment", str(self.alignment),
            "--cover", str(self.cover),
            "--production", str(self.production),
            "--destination", str(self.destination),
        ]

        with contextlib.redirect_stdout(output):
            exit_code = module.main(arguments)

        self.assertEqual(0, exit_code)
        payload = json.loads(output.getvalue())
        self.assertEqual("promote", payload["decision"])
        self.assertFalse(payload["applied"])
        self.assertEqual(output.getvalue(), json.dumps(payload, sort_keys=True) + "\n")
        self.assertFalse(self.destination.exists())


if __name__ == "__main__":
    unittest.main()
