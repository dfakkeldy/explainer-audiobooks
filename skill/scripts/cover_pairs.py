from __future__ import annotations

import json
import os
import shutil
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path

from cover_fonts import DEFAULT_MANIFEST
from cover_renderer import CoverRenderError, RenderResult, render_cover_spec
from cover_spec import ValidatedCoverSpec, load_cover_spec


@dataclass(frozen=True)
class CoverPairRenderResult:
    candidate_id: str
    source_sha256: str
    portrait: RenderResult
    square: RenderResult


_replace = os.replace


def _same_file(first: Path, second: Path) -> bool:
    if first.resolve() == second.resolve():
        return True
    try:
        return first.exists() and second.exists() and os.path.samefile(first, second)
    except OSError:
        return False


def _protected_inputs(specs: tuple[ValidatedCoverSpec, ...]) -> set[Path]:
    paths: set[Path] = set()
    for spec in specs:
        paths.update((spec.path, spec.art_path, spec.font_manifest.path))
        for font in spec.font_manifest.fonts.values():
            paths.update((font.path, font.license_path))
    return paths


def _validate_aliases(
    specs: tuple[ValidatedCoverSpec, ValidatedCoverSpec], outputs: tuple[Path, ...]
) -> None:
    protected = _protected_inputs(specs)
    for index, output in enumerate(outputs):
        for other in outputs[index + 1 :]:
            if _same_file(output, other):
                raise CoverRenderError("pair artifact paths alias each other")
        for source in protected:
            if _same_file(output, source):
                raise CoverRenderError("pair artifact path aliases renderer input")


def _validate_identity(
    portrait: ValidatedCoverSpec, square: ValidatedCoverSpec
) -> None:
    if (portrait.variant, square.variant) != ("portrait", "square"):
        raise CoverRenderError("pair variants must be portrait then square")
    if portrait.data["candidate"]["id"] != square.data["candidate"]["id"]:
        raise CoverRenderError("pair candidate IDs must match")
    if portrait.art_sha256 != square.art_sha256:
        raise CoverRenderError("pair source-art SHA-256 values must match")
    for field in ("title", "author"):
        if portrait.metadata[field] != square.metadata[field]:
            raise CoverRenderError(f"pair metadata {field} values must match")
    if square.metadata["subtitle"] not in ("", portrait.metadata["subtitle"]):
        raise CoverRenderError("square subtitle must match portrait or be empty")


def _publish_pair(staged: list[tuple[Path, Path]], staging: Path) -> None:
    backups: dict[Path, tuple[str, Path | str]] = {}
    for index, (_source, destination) in enumerate(staged):
        if destination.is_symlink():
            backups[destination] = ("symlink", os.readlink(destination))
        elif destination.exists():
            backup = staging / f"pair-backup-{index}"
            shutil.copy2(destination, backup)
            backups[destination] = ("file", backup)

    published: list[Path] = []
    try:
        for source, destination in staged:
            _replace(source, destination)
            published.append(destination)
    except Exception:
        rollback_errors: list[Exception] = []
        for destination in reversed(published):
            try:
                backup = backups.get(destination)
                if backup is None:
                    destination.unlink(missing_ok=True)
                elif backup[0] == "symlink":
                    destination.unlink(missing_ok=True)
                    os.symlink(backup[1], destination)
                else:
                    _replace(backup[1], destination)
            except Exception as error:
                rollback_errors.append(error)
        if rollback_errors:
            raise CoverRenderError("pair publication and rollback failed")
        raise


def render_cover_pair(
    portrait_spec: Path,
    square_spec: Path,
    portrait_output: Path,
    square_output: Path,
    portrait_thumbnail: Path,
    square_thumbnail: Path,
    portrait_receipt: Path,
    square_receipt: Path,
    font_manifest_path: Path = DEFAULT_MANIFEST,
) -> CoverPairRenderResult:
    """Validate one identity, stage both renders, and publish all outputs atomically."""
    portrait = load_cover_spec(Path(portrait_spec), Path(font_manifest_path))
    square = load_cover_spec(Path(square_spec), Path(font_manifest_path))
    _validate_identity(portrait, square)

    if portrait.path.parent != square.path.parent:
        raise CoverRenderError("pair specifications must share one run folder")
    outputs = tuple(
        Path(path).resolve()
        for path in (
            portrait_output,
            square_output,
            portrait_thumbnail,
            square_thumbnail,
            portrait_receipt,
            square_receipt,
        )
    )
    for output in outputs:
        try:
            output.relative_to(portrait.path.parent)
        except ValueError as error:
            raise CoverRenderError("pair artifact path escapes specification run folder") from error
    _validate_aliases((portrait, square), outputs)
    for output in outputs:
        output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(
        prefix=".cover-pair-", dir=portrait.path.parent
    ) as raw:
        staging = Path(raw)
        staged = tuple(staging / f"artifact-{index}{path.suffix}" for index, path in enumerate(outputs))
        portrait_result = render_cover_spec(
            portrait.path, staged[0], staged[2], staged[4], font_manifest_path
        )
        square_result = render_cover_spec(
            square.path, staged[1], staged[3], staged[5], font_manifest_path
        )
        for receipt_index, output_index, thumbnail_index in ((4, 0, 2), (5, 1, 3)):
            payload = json.loads(staged[receipt_index].read_text(encoding="utf-8"))
            payload["output"] = outputs[output_index].name
            payload["thumbnail"] = outputs[thumbnail_index].name
            staged[receipt_index].write_text(
                json.dumps(payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        _publish_pair(list(zip(staged, outputs)), staging)

    return CoverPairRenderResult(
        candidate_id=portrait.data["candidate"]["id"],
        source_sha256=portrait.art_sha256,
        portrait=replace(
            portrait_result,
            output_path=outputs[0], thumbnail_path=outputs[2], receipt_path=outputs[4]
        ),
        square=replace(
            square_result,
            output_path=outputs[1], thumbnail_path=outputs[3], receipt_path=outputs[5]
        ),
    )
