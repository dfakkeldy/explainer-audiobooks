from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import unittest
from dataclasses import asdict, replace
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parents[1] / "skill" / "scripts"))
from cover_receipts import (
    PairedSelectionReceipt,
    SelectedCandidate,
    SelectedVariant,
    SelectionReceipt,
)
import sync_selected_cover


def receipt(selected_at: str = "2026-07-12T13:00:00-03:00", cover_hash: str = "a" * 64) -> SelectionReceipt:
    return SelectionReceipt(1, "rodents-in-the-walls", "corrected-v2", "c1", "Full Bleed", 1, "1" * 64, "2" * 64, cover_hash, 1, "3" * 64, (1600, 2560), "RGB", selected_at, "explicit-user-choice", {"classification": "public-safe", "permission_to_publish": "granted"})


def write_receipt(path: Path, value: SelectionReceipt) -> Path:
    path.write_text(json.dumps(asdict(value)), encoding="utf-8")
    return path


def write_source_package(root: Path) -> tuple[Path, Path, Path, Path]:
    source = root / "source"
    source.mkdir()
    cover = source / "cover.png"
    epub = source / "book.epub"
    m4b = source / "book.m4b"
    cover.write_bytes(b"new-cover")
    epub.write_bytes(b"new-epub")
    m4b.write_bytes(b"new-m4b")
    selection = write_receipt(
        source / "cover-selection.json",
        receipt(cover_hash=hashlib.sha256(cover.read_bytes()).hexdigest()),
    )
    return selection, cover, epub, m4b


PAIRED_NAMES = (
    "cover.png", "m4b-cover.png", "cover-thumbnail.png",
    "m4b-cover-thumbnail.png", "cover-spec.json", "m4b-cover-spec.json",
    "cover-render.json", "m4b-cover-render.json", "cover-selection.json",
)


def write_paired_package(root: Path, *, include_m4b: bool = True):
    source = root / "paired-source"
    source.mkdir()
    artifacts: dict[str, Path] = {}
    for name in PAIRED_NAMES[:-1]:
        path = source / name
        path.write_bytes(f"new-{name}".encode())
        artifacts[name] = path
    def variant(stem: str, dimensions: tuple[int, int]) -> SelectedVariant:
        return SelectedVariant(
            hashlib.sha256(artifacts[f"{stem}-spec.json"].read_bytes()).hexdigest(),
            hashlib.sha256(artifacts[f"{stem}-render.json"].read_bytes()).hexdigest(),
            hashlib.sha256(artifacts[f"{stem}.png"].read_bytes()).hexdigest(),
            dimensions,
            hashlib.sha256(artifacts[f"{stem}-thumbnail.png"].read_bytes()).hexdigest(),
            stem == "cover",
        )
    selected = PairedSelectionReceipt(
        2, "fixture-book", "public-v1", SelectedCandidate("c1", "Pair"),
        "1" * 64, {
            "portrait": variant("cover", (1600, 2560)),
            "square": variant("m4b-cover", (2400, 2400)),
        },
        "2" * 64, "user", "2026-07-13T12:00:00-03:00",
        {"classification": "public-safe", "permission_to_publish": True},
    )
    selection = source / "cover-selection.json"
    selection.write_text(json.dumps(asdict(selected)), encoding="utf-8")
    artifacts[selection.name] = selection
    epub = source / "book.epub"; epub.write_bytes(b"new-epub")
    m4b = source / "book.m4b"; m4b.write_bytes(b"new-m4b")
    return selected, artifacts, epub, m4b if include_m4b else None


class SyncSelectedCoverTests(unittest.TestCase):
    def test_classifies_new_reuse_supersede_and_conflict(self) -> None:
        source = receipt()
        self.assertEqual("new", sync_selected_cover.classify_destination(source, None, "reuse"))
        self.assertEqual("supersede-unreceipted", sync_selected_cover.classify_destination(source, None, "supersede", destination_has_artifacts=True))
        with self.assertRaisesRegex(ValueError, "unreceipted cover artifacts"):
            sync_selected_cover.classify_destination(source, None, "reuse", destination_has_artifacts=True)
        self.assertEqual("reuse", sync_selected_cover.classify_destination(source, source, "reuse"))
        older = receipt("2026-07-11T13:00:00-03:00", "b" * 64)
        self.assertEqual("supersede", sync_selected_cover.classify_destination(source, older, "supersede"))
        with self.assertRaisesRegex(ValueError, "cover receipt conflict"):
            sync_selected_cover.classify_destination(source, older, "reuse")
        newer = receipt("2026-07-13T13:00:00-03:00", "b" * 64)
        with self.assertRaisesRegex(ValueError, "not newer"):
            sync_selected_cover.classify_destination(source, newer, "supersede")

    def test_public_destination_requires_public_safe_permission(self) -> None:
        private = replace(receipt(), privacy={"classification": "private", "permission_to_publish": "not-requested"})
        with self.assertRaisesRegex(ValueError, "public-safe and permissioned"):
            sync_selected_cover.require_public_permission(private)

    def test_apply_updates_only_cover_artifacts_receipt_and_existing_checksums(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = root / "source"
            destination = root / "destination"
            source.mkdir(); destination.mkdir()
            cover = source / "cover.png"; cover.write_bytes(b"new-cover")
            epub = source / "book.epub"; epub.write_bytes(b"new-epub")
            m4b = source / "book.m4b"; m4b.write_bytes(b"new-m4b")
            selection = write_receipt(source / "cover-selection.json", receipt(cover_hash=hashlib.sha256(cover.read_bytes()).hexdigest()))
            (destination / "cover.png").write_bytes(b"old-cover")
            (destination / "book.epub").write_bytes(b"old-epub")
            (destination / "book.m4b").write_bytes(b"old-m4b")
            write_receipt(destination / "cover-selection.json", receipt("2026-07-11T13:00:00-03:00", "b" * 64))
            untouched = destination / "alignment.json"; untouched.write_bytes(b"untouched")
            checksums = destination / "SHA256SUMS"
            checksums.write_text(f"{'0' * 64}  cover.png\n{'1' * 64}  alignment.json\n", encoding="utf-8")
            with mock.patch.object(sync_selected_cover, "verify_package"):
                result = sync_selected_cover.sync_selected_cover(selection, cover, epub, m4b, destination, intent="supersede", apply=True, checksum_manifest=checksums, public_destination=False)
            self.assertEqual("supersede", result.decision)
            self.assertEqual(b"new-cover", (destination / "cover.png").read_bytes())
            self.assertEqual(b"untouched", untouched.read_bytes())
            self.assertIn(hashlib.sha256(b"new-cover").hexdigest(), checksums.read_text(encoding="utf-8"))
            self.assertIn(f"{'1' * 64}  alignment.json", checksums.read_text(encoding="utf-8"))

    def test_failure_rolls_back_every_touched_file(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = root / "source"; destination = root / "destination"
            source.mkdir(); destination.mkdir()
            cover = source / "cover.png"; epub = source / "book.epub"; m4b = source / "book.m4b"
            cover.write_bytes(b"new-cover"); epub.write_bytes(b"new-epub"); m4b.write_bytes(b"new-m4b")
            selection = write_receipt(source / "cover-selection.json", receipt(cover_hash=hashlib.sha256(cover.read_bytes()).hexdigest()))
            originals = {"cover.png": b"old-cover", "book.epub": b"old-epub", "book.m4b": b"old-m4b"}
            for name, payload in originals.items():
                (destination / name).write_bytes(payload)
            with mock.patch.object(sync_selected_cover, "verify_package"), self.assertRaisesRegex(RuntimeError, "injected sync failure"):
                sync_selected_cover.sync_selected_cover(selection, cover, epub, m4b, destination, intent="supersede", apply=True, fail_after=2)
            for name, payload in originals.items():
                self.assertEqual(payload, (destination / name).read_bytes())
            self.assertFalse((destination / "cover-selection.json").exists())

    def test_rejects_duplicate_artifact_basenames(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            selection, cover, _epub, _m4b = write_source_package(root)
            first = root / "first"
            second = root / "second"
            first.mkdir(); second.mkdir()
            epub = first / "package.bin"
            m4b = second / "package.bin"
            epub.write_bytes(b"epub")
            m4b.write_bytes(b"m4b")
            destination = root / "destination"

            with mock.patch.object(sync_selected_cover, "verify_package") as verify, self.assertRaisesRegex(ValueError, "artifact names collide"):
                sync_selected_cover.sync_selected_cover(
                    selection, cover, epub, m4b, destination,
                    intent="reuse", apply=False,
                )

            verify.assert_not_called()
            self.assertFalse(destination.exists())

    def test_rejects_final_artifact_targets_that_alias(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            selection, cover, epub, m4b = write_source_package(root)
            destination = root / "destination"
            destination.mkdir()
            destination_cover = destination / "cover.png"
            destination_cover.write_bytes(b"old-cover")
            (destination / epub.name).symlink_to(destination_cover.name)
            (destination / m4b.name).write_bytes(b"old-m4b")

            with mock.patch.object(sync_selected_cover, "verify_package") as verify, self.assertRaisesRegex(ValueError, "artifact targets collide"):
                sync_selected_cover.sync_selected_cover(
                    selection, cover, epub, m4b, destination,
                    intent="supersede", apply=False,
                )

            verify.assert_not_called()
            self.assertEqual(b"old-cover", destination_cover.read_bytes())
            self.assertTrue((destination / epub.name).is_symlink())

    def test_dry_run_does_not_create_or_modify_destination(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            selection, cover, epub, m4b = write_source_package(root)
            destination = root / "destination"

            with mock.patch.object(sync_selected_cover, "verify_package") as verify:
                result = sync_selected_cover.sync_selected_cover(
                    selection, cover, epub, m4b, destination,
                    intent="reuse", apply=False,
                )

            self.assertEqual("new", result.decision)
            self.assertFalse(result.applied)
            self.assertFalse(destination.exists())
            verify.assert_called_once_with(
                selection,
                cover,
                epub_path=epub,
                m4b_path=m4b,
                receipt_path=selection,
            )

    def test_failure_restores_existing_and_dangling_symlinks(self) -> None:
        for raw_target, target_exists in (("cover-target.png", True), ("missing-cover.png", False)):
            with self.subTest(target=raw_target), tempfile.TemporaryDirectory() as raw:
                root = Path(raw)
                selection, cover, epub, m4b = write_source_package(root)
                destination = root / "destination"
                destination.mkdir()
                target = destination / raw_target
                if target_exists:
                    target.write_bytes(b"linked-cover")
                destination_cover = destination / "cover.png"
                destination_cover.symlink_to(raw_target)

                with mock.patch.object(sync_selected_cover, "verify_package"), self.assertRaisesRegex(RuntimeError, "injected sync failure"):
                    sync_selected_cover.sync_selected_cover(
                        selection, cover, epub, m4b, destination,
                        intent="supersede", apply=True, fail_after=1,
                    )

                self.assertTrue(destination_cover.is_symlink())
                self.assertEqual(raw_target, os.readlink(destination_cover))
                if target_exists:
                    self.assertEqual(b"linked-cover", target.read_bytes())
                else:
                    self.assertFalse(target.exists())

    def test_each_publish_uses_a_unique_same_directory_incoming_file(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            selection, cover, epub, m4b = write_source_package(root)
            destination = root / "destination"
            destination.mkdir()
            fixed_incoming = {
                destination / f".{name}.incoming": b"sentinel"
                for name in ("cover.png", epub.name, m4b.name, "cover-selection.json")
            }
            for path, payload in fixed_incoming.items():
                path.write_bytes(payload)
            real_replace = os.replace
            incoming: list[Path] = []

            def record_replace(source: Path, target: Path) -> None:
                source_path = Path(source)
                if source_path.suffix == ".incoming":
                    incoming.append(source_path)
                real_replace(source, target)

            with mock.patch.object(sync_selected_cover, "verify_package"), mock.patch.object(sync_selected_cover.os, "replace", side_effect=record_replace):
                for intent in ("reuse", "reuse"):
                    sync_selected_cover.sync_selected_cover(
                        selection, cover, epub, m4b, destination,
                        intent=intent, apply=True,
                    )

            self.assertEqual(8, len(incoming))
            self.assertEqual(8, len(set(incoming)))
            self.assertTrue(all(path.parent == destination for path in incoming))
            for path, payload in fixed_incoming.items():
                self.assertEqual(payload, path.read_bytes())

    def test_rollback_continues_after_one_restore_error(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            selection, cover, epub, m4b = write_source_package(root)
            destination = root / "destination"
            destination.mkdir()
            originals = {
                "cover.png": b"old-cover",
                epub.name: b"old-epub",
                m4b.name: b"old-m4b",
                "cover-selection.json": selection.read_bytes(),
            }
            for name, payload in originals.items():
                (destination / name).write_bytes(payload)
            real_replace = os.replace
            rolling_back = False

            def verify_then_fail(*_args, **_kwargs) -> None:
                nonlocal rolling_back
                if not rolling_back:
                    rolling_back = True
                    return
                raise ValueError("destination verification failed")

            def fail_one_restore(source: Path, target: Path) -> None:
                source_path = Path(source)
                target_path = Path(target)
                if rolling_back and target_path == destination / m4b.name and "backup" in source_path.name:
                    raise OSError("M4B restore failed")
                real_replace(source, target)

            with mock.patch.object(sync_selected_cover, "verify_package", side_effect=verify_then_fail), mock.patch.object(sync_selected_cover.os, "replace", side_effect=fail_one_restore), self.assertRaisesRegex(RuntimeError, "rollback failed"):
                sync_selected_cover.sync_selected_cover(
                    selection, cover, epub, m4b, destination,
                    intent="reuse", apply=True,
                )

            self.assertEqual(originals["cover.png"], (destination / "cover.png").read_bytes())
            self.assertEqual(originals[epub.name], (destination / epub.name).read_bytes())
            self.assertEqual(originals["cover-selection.json"], (destination / "cover-selection.json").read_bytes())

    def test_checksum_publish_failure_restores_exact_original_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            selection, cover, epub, m4b = write_source_package(root)
            destination = root / "destination"
            destination.mkdir()
            originals = {
                "cover.png": b"old-cover",
                epub.name: b"old-epub",
                m4b.name: b"old-m4b",
                "cover-selection.json": selection.read_bytes(),
            }
            for name, payload in originals.items():
                (destination / name).write_bytes(payload)
            checksums = destination / "SHA256SUMS"
            original_manifest = (
                f"{'1' * 64}  alignment.json\n"
                f"{'0' * 64}  cover.png\n"
            ).encode("utf-8")
            checksums.write_bytes(original_manifest)
            real_replace = os.replace
            failed = False

            def fail_after_checksum_replace(source: Path, target: Path) -> None:
                nonlocal failed
                if Path(target) == checksums and not failed:
                    failed = True
                    real_replace(source, target)
                    raise OSError("checksum publish failed after replacement")
                real_replace(source, target)

            with mock.patch.object(sync_selected_cover, "verify_package"), mock.patch.object(sync_selected_cover.os, "replace", side_effect=fail_after_checksum_replace), self.assertRaisesRegex(OSError, "checksum publish failed"):
                sync_selected_cover.sync_selected_cover(
                    selection, cover, epub, m4b, destination,
                    intent="reuse", apply=True, checksum_manifest=checksums,
                )

            for name, payload in originals.items():
                self.assertEqual(payload, (destination / name).read_bytes())
            self.assertEqual(original_manifest, checksums.read_bytes())
            self.assertEqual([], list(destination.glob(".*.incoming")))

    def test_paired_apply_has_exact_ordered_changed_set_and_preserves_unrelated_files(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            selected, artifacts, epub, m4b = write_paired_package(root)
            destination = root / "destination"; destination.mkdir()
            unrelated = destination / "alignment.json"; unrelated.write_bytes(b"unrelated")
            rodents = destination / "rodents-legacy-fixture.epub"; rodents.write_bytes(b"rodents")
            checksums = destination / "SHA256SUMS"
            checksums.write_text(f"{'f' * 64}  alignment.json\n", encoding="utf-8")

            with mock.patch.object(sync_selected_cover, "verify_package") as verify:
                result = sync_selected_cover.sync_selected_cover(
                    artifacts["cover-selection.json"], artifacts["cover.png"], epub,
                    m4b, destination, intent="reuse", apply=True,
                    checksum_manifest=checksums, public_destination=True,
                    artifact_map=artifacts,
                )

            self.assertEqual(PAIRED_NAMES + ("book.epub", "book.m4b"), result.files)
            self.assertEqual(b"unrelated", unrelated.read_bytes())
            self.assertEqual(b"rodents", rodents.read_bytes())
            self.assertEqual(set(PAIRED_NAMES + ("book.epub", "book.m4b", "SHA256SUMS", "alignment.json", "rodents-legacy-fixture.epub")), {p.name for p in destination.iterdir()})
            manifest = checksums.read_text(encoding="utf-8")
            self.assertIn(f"{'f' * 64}  alignment.json", manifest)
            for name in PAIRED_NAMES:
                self.assertIn(f"  {name}\n", manifest)
            self.assertGreaterEqual(verify.call_count, 2)
            self.assertEqual(selected, sync_selected_cover.load_selection(destination / "cover-selection.json"))

    def test_paired_dry_run_is_immutable_and_optional_m4b_is_omitted(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            _selected, artifacts, epub, _m4b = write_paired_package(root, include_m4b=False)
            destination = root / "destination"; destination.mkdir()
            marker = destination / "marker"; marker.write_bytes(b"same")
            before = {p.name: p.read_bytes() for p in destination.iterdir()}
            with mock.patch.object(sync_selected_cover, "verify_package"):
                result = sync_selected_cover.sync_selected_cover(
                    artifacts["cover-selection.json"], artifacts["cover.png"], epub,
                    None, destination, intent="reuse", apply=False,
                    artifact_map=artifacts,
                )
            self.assertEqual(PAIRED_NAMES + ("book.epub",), result.files)
            self.assertEqual(before, {p.name: p.read_bytes() for p in destination.iterdir()})

    def test_paired_rejects_unknown_missing_and_aliased_sources_before_verification(self) -> None:
        for mutation, message in (("unknown", "canonical"), ("missing", "exactly"), ("alias", "source artifacts alias")):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as raw:
                root = Path(raw)
                _selected, artifacts, epub, m4b = write_paired_package(root)
                if mutation == "unknown":
                    artifacts["surprise.png"] = artifacts["cover.png"]
                elif mutation == "missing":
                    artifacts.pop("m4b-cover-spec.json")
                else:
                    artifacts["m4b-cover.png"].unlink()
                    os.link(artifacts["cover.png"], artifacts["m4b-cover.png"])
                with mock.patch.object(sync_selected_cover, "verify_package") as verify, self.assertRaisesRegex(ValueError, message):
                    sync_selected_cover.sync_selected_cover(
                        artifacts["cover-selection.json"], artifacts["cover.png"], epub,
                        m4b, root / "destination", intent="reuse", apply=False,
                        artifact_map=artifacts,
                    )
                verify.assert_not_called()

    def test_paired_failure_after_each_cover_rolls_back_regular_absent_and_symlink_targets(self) -> None:
        for fail_after in (1, 2):
            with self.subTest(fail_after=fail_after), tempfile.TemporaryDirectory() as raw:
                root = Path(raw)
                _selected, artifacts, epub, m4b = write_paired_package(root)
                destination = root / "destination"; destination.mkdir()
                (destination / "cover.png").write_bytes(b"old-portrait")
                link_target = destination / "old-square.png"; link_target.write_bytes(b"old-square")
                (destination / "m4b-cover.png").symlink_to(link_target.name)
                unrelated = destination / "keep"; unrelated.write_bytes(b"keep")
                with mock.patch.object(sync_selected_cover, "verify_package"), self.assertRaisesRegex(RuntimeError, "injected sync failure"):
                    sync_selected_cover.sync_selected_cover(
                        artifacts["cover-selection.json"], artifacts["cover.png"], epub,
                        m4b, destination, intent="supersede", apply=True,
                        artifact_map=artifacts, fail_after=fail_after,
                    )
                self.assertEqual(b"old-portrait", (destination / "cover.png").read_bytes())
                self.assertTrue((destination / "m4b-cover.png").is_symlink())
                self.assertEqual(link_target.name, os.readlink(destination / "m4b-cover.png"))
                self.assertFalse((destination / "cover-thumbnail.png").exists())
                self.assertEqual(b"keep", unrelated.read_bytes())

    def test_paired_checksums_refresh_existing_package_rows_without_adding_missing_rows(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            _selected, artifacts, epub, m4b = write_paired_package(root)
            destination = root / "destination"; destination.mkdir()
            checksums = destination / "SHA256SUMS"
            checksums.write_text(
                f"{'a' * 64}  book.epub\n{'b' * 64}  book.m4b\n"
                f"{'c' * 64}  alignment.json\n",
                encoding="utf-8",
            )
            with mock.patch.object(sync_selected_cover, "verify_package"):
                sync_selected_cover.sync_selected_cover(
                    artifacts["cover-selection.json"], artifacts["cover.png"], epub,
                    m4b, destination, intent="reuse", apply=True,
                    artifact_map=artifacts, checksum_manifest=checksums,
                )
            manifest = checksums.read_text(encoding="utf-8")
            self.assertIn(f"{hashlib.sha256(epub.read_bytes()).hexdigest()}  book.epub", manifest)
            self.assertIn(f"{hashlib.sha256(m4b.read_bytes()).hexdigest()}  book.m4b", manifest)
            self.assertIn(f"{'c' * 64}  alignment.json", manifest)

            without_package_rows = destination / "OTHER-SHA256SUMS"
            without_package_rows.write_text(f"{'c' * 64}  alignment.json\n", encoding="utf-8")
            with mock.patch.object(sync_selected_cover, "verify_package"):
                sync_selected_cover.sync_selected_cover(
                    artifacts["cover-selection.json"], artifacts["cover.png"], epub,
                    m4b, destination, intent="reuse", apply=True,
                    artifact_map=artifacts, checksum_manifest=without_package_rows,
                )
            second = without_package_rows.read_text(encoding="utf-8")
            self.assertNotIn("  book.epub", second)
            self.assertNotIn("  book.m4b", second)
            for name in PAIRED_NAMES:
                self.assertIn(f"  {name}\n", second)

    def test_paired_staged_copy_corruption_aborts_before_destination_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            _selected, artifacts, epub, m4b = write_paired_package(root)
            destination = root / "destination"; destination.mkdir()
            marker = destination / "marker"; marker.write_bytes(b"unchanged")
            real_copy2 = sync_selected_cover.shutil.copy2

            def corrupt_thumbnail(source: Path, target: Path):
                result = real_copy2(source, target)
                if Path(target).name == "cover-thumbnail.png":
                    Path(target).write_bytes(b"corrupted-after-copy")
                return result

            with mock.patch.object(sync_selected_cover, "verify_package"), mock.patch.object(
                sync_selected_cover.shutil, "copy2", side_effect=corrupt_thumbnail,
            ), self.assertRaisesRegex(ValueError, "cover-thumbnail.png"):
                sync_selected_cover.sync_selected_cover(
                    artifacts["cover-selection.json"], artifacts["cover.png"], epub,
                    m4b, destination, intent="reuse", apply=True,
                    artifact_map=artifacts,
                )

            self.assertEqual({"marker"}, {path.name for path in destination.iterdir()})
            self.assertEqual(b"unchanged", marker.read_bytes())


if __name__ == "__main__":
    unittest.main()
