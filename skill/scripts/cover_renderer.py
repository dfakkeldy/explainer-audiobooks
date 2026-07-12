from __future__ import annotations

import base64
import hashlib
import json
import mimetypes
import os
import shutil
import struct
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from cover_fonts import DEFAULT_MANIFEST, FontRecord
from cover_spec import HEIGHT, WIDTH, ValidatedCoverSpec, load_cover_spec

RENDERER_VERSION = 1


class CoverRenderError(ValueError):
    pass


@dataclass(frozen=True)
class RenderResult:
    output_path: Path
    thumbnail_path: Path
    receipt_path: Path
    cover_sha256: str
    thumbnail_sha256: str


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    if path.suffix.lower() == ".svg":
        mime = "image/svg+xml"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def _font_css(fonts: dict[str, FontRecord]) -> str:
    rules = []
    for font_id in sorted(fonts):
        record = fonts[font_id]
        encoded = base64.b64encode(record.path.read_bytes()).decode("ascii")
        rules.append(
            f"@font-face{{font-family:'Cover-{font_id}';"
            f"src:url(data:font/ttf;base64,{encoded}) format('truetype');}}"
        )
    return "".join(rules)


def _blend(value: str) -> str:
    return "normal" if value == "normal" else value


def _fill(fill: dict[str, Any], identity: str, definitions: list[str]) -> str:
    if fill["kind"] == "solid":
        return fill["colour"]
    x1, y1 = fill["start"]
    x2, y2 = fill["end"]
    stops = "".join(
        f'<stop offset="{stop["offset"] * 100:g}%" '
        f'stop-color="{stop["colour"]}" stop-opacity="{stop["opacity"]:g}"/>'
        for stop in fill["stops"]
    )
    definitions.append(
        f'<linearGradient id="{identity}" x1="{x1:g}" y1="{y1:g}" '
        f'x2="{x2:g}" y2="{y2:g}" gradientUnits="userSpaceOnUse">'
        f"{stops}</linearGradient>"
    )
    return f"url(#{identity})"


def _art_markup(spec: ValidatedCoverSpec, definitions: list[str]) -> str:
    art = spec.data["art"]
    x, y, width, height = art["box"]
    anchor = {
        "center": "xMidYMid",
        "center-top": "xMidYMin",
        "center-bottom": "xMidYMax",
        "left": "xMinYMid",
        "right": "xMaxYMid",
    }[art["anchor"]]
    fit = "meet" if art["mode"] == "fit" else "slice"
    mask_attribute = ""
    if "mask" in art:
        mask = art["mask"]
        mx, my, mw, mh = mask["box"]
        if mask["shape"] == "ellipse":
            shape = (
                f'<ellipse cx="{mx + mw / 2:g}" cy="{my + mh / 2:g}" '
                f'rx="{mw / 2:g}" ry="{mh / 2:g}" fill="white"/>'
            )
        else:
            shape = (
                f'<rect x="{mx:g}" y="{my:g}" width="{mw:g}" height="{mh:g}" '
                f'rx="{mask.get("radius", 0):g}" fill="white"/>'
            )
        definitions.append(f'<mask id="art-mask">{shape}</mask>')
        mask_attribute = ' mask="url(#art-mask)"'
    return (
        f'<image href="{_data_uri(spec.art_path)}" x="{x:g}" y="{y:g}" '
        f'width="{width:g}" height="{height:g}" '
        f'preserveAspectRatio="{anchor} {fit}" opacity="{art["opacity"]:g}" '
        f'style="mix-blend-mode:{_blend(art["blend_mode"])}"{mask_attribute}/>'
    )


def _text_markup(layer: dict[str, Any], index: int, definitions: list[str]) -> str:
    x, y, width, _height = layer["box"]
    anchor = {"left": "start", "center": "middle", "right": "end"}[layer["align"]]
    origin_x = {
        "left": x,
        "center": x + width / 2,
        "right": x + width,
    }[layer["align"]]
    origin_y = y + layer["size"] + layer["baseline_shift"]
    style = [f"mix-blend-mode:{_blend(layer.get('blend_mode', 'normal'))}"]
    variations = layer.get("font_variation", {})
    if variations:
        axes = ",".join(
            f"'{name}' {value:g}" for name, value in sorted(variations.items())
        )
        style.append(f"font-variation-settings:{axes}")
    outline = layer.get("outline")
    stroke = ""
    if outline:
        stroke = (
            f' stroke="{outline["colour"]}" stroke-width="{outline["width"]:g}" '
            'paint-order="stroke fill"'
        )
    filter_attribute = ""
    shadow = layer.get("shadow")
    if shadow:
        identity = f"shadow-{index}"
        definitions.append(
            f'<filter id="{identity}" x="-30%" y="-30%" width="160%" height="160%">'
            f'<feDropShadow dx="{shadow["dx"]:g}" dy="{shadow["dy"]:g}" '
            f'stdDeviation="{shadow["blur"] / 2:g}" flood-color="{shadow["colour"]}" '
            f'flood-opacity="{shadow["opacity"]:g}"/></filter>'
        )
        filter_attribute = f' filter="url(#{identity})"'
    transform = (
        f"rotate({layer['rotation']:g} {origin_x:g} {origin_y:g})"
        if layer["rotation"]
        else ""
    )
    common = (
        f'x="{origin_x:g}" y="{origin_y:g}" text-anchor="{anchor}" '
        f'font-family="Cover-{layer["font_id"]}" font-size="{layer["size"]:g}" '
        f'letter-spacing="{layer["tracking"]:g}" fill="{layer["colour"]}" '
        f'fill-opacity="{layer["opacity"]:g}" style="{";".join(style)}"'
        f"{stroke}{filter_attribute}"
    )
    if transform:
        common += f' transform="{transform}"'
    if layer.get("runs"):
        runs = []
        for run in layer["runs"]:
            attrs = [f'fill="{run.get("colour", layer["colour"])}"']
            attrs.append(f'font-size="{layer["size"] * run.get("size_scale", 1):g}"')
            attrs.append(f'letter-spacing="{run.get("tracking", layer["tracking"]):g}"')
            attrs.append(f'dx="{run.get("dx", 0):g}"')
            attrs.append(f'baseline-shift="{run.get("baseline_shift", 0):g}"')
            if run.get("rotation", 0):
                attrs.append(f'rotate="{run["rotation"]:g}"')
            runs.append(f'<tspan {" ".join(attrs)}>{escape(run["text"])}</tspan>')
        body = "".join(runs)
    else:
        lines = layer["text"].split("\n")
        body = "".join(
            f'<tspan x="{origin_x:g}" '
            f'dy="{0 if line_index == 0 else layer["line_height"]:g}">'
            f"{escape(line)}</tspan>"
            for line_index, line in enumerate(lines)
        )
    return f"<text {common}>{body}</text>"


def build_svg(spec: ValidatedCoverSpec) -> str:
    definitions: list[str] = []
    body = [
        f'<rect width="{WIDTH}" height="{HEIGHT}" '
        f'fill="{spec.data["canvas"]["background"]}"/>'
    ]
    body.append(_art_markup(spec, definitions))
    for index, layer in enumerate(spec.data["layers"], start=1):
        kind = layer["kind"]
        if kind in {"field", "scrim", "shape"}:
            x, y, width, height = layer["box"]
            fill = _fill(layer["fill"], f"fill-{index}", definitions)
            if kind == "shape" and layer["shape"] == "ellipse":
                element = (
                    f'<ellipse cx="{x + width / 2:g}" cy="{y + height / 2:g}" '
                    f'rx="{width / 2:g}" ry="{height / 2:g}"'
                )
            else:
                element = (
                    f'<rect x="{x:g}" y="{y:g}" width="{width:g}" '
                    f'height="{height:g}" rx="{layer.get("radius", 0):g}"'
                )
            stroke = (
                f' stroke="{layer["stroke"]}" '
                f'stroke-width="{layer.get("stroke_width", 0):g}"'
                if layer.get("stroke")
                else ""
            )
            rotation = layer.get("rotation", 0)
            transform = (
                f' transform="rotate({rotation:g} {x + width / 2:g} '
                f'{y + height / 2:g})"'
                if rotation
                else ""
            )
            body.append(
                f'{element} fill="{fill}" opacity="{layer["opacity"]:g}" '
                f'style="mix-blend-mode:{_blend(layer["blend_mode"])}"'
                f"{stroke}{transform}/>"
            )
        elif kind == "line":
            body.append(
                f'<line x1="{layer["start"][0]:g}" y1="{layer["start"][1]:g}" '
                f'x2="{layer["end"][0]:g}" y2="{layer["end"][1]:g}" '
                f'stroke="{layer["colour"]}" stroke-width="{layer["width"]:g}" '
                f'opacity="{layer["opacity"]:g}"/>'
            )
        else:
            body.append(_text_markup(layer, index, definitions))
    defs = f'<defs><style>{_font_css(spec.fonts)}</style>{"".join(definitions)}</defs>'
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}">{defs}{"".join(body)}</svg>'
    )


def _render(svg_path: Path, destination: Path, width: int, height: int) -> None:
    raw = destination.with_name(f".{destination.name}.raw.png")
    normalized = destination.with_name(f".{destination.name}.normalized.png")
    try:
        if shutil.which("rsvg-convert"):
            command = [
                "rsvg-convert",
                "-w",
                str(width),
                "-h",
                str(height),
                str(svg_path),
                "-o",
                str(raw),
            ]
        elif shutil.which("magick"):
            command = [
                "magick",
                "-background",
                "none",
                str(svg_path),
                "-resize",
                f"{width}x{height}!",
                str(raw),
            ]
        else:
            raise CoverRenderError("no SVG rasterizer found")
        subprocess.run(command, check=True, capture_output=True)
        if not shutil.which("magick"):
            raise CoverRenderError("ImageMagick is required to normalize RGB PNG output")
        subprocess.run(
            [
                "magick",
                str(raw),
                "-alpha",
                "off",
                "-colorspace",
                "sRGB",
                "-strip",
                f"PNG24:{normalized}",
            ],
            check=True,
            capture_output=True,
        )
        payload = normalized.read_bytes()
        if (
            payload[:8] != b"\x89PNG\r\n\x1a\n"
            or struct.unpack(">II", payload[16:24]) != (width, height)
            or payload[25] != 2
        ):
            raise CoverRenderError(
                f"renderer did not produce {width}x{height} RGB PNG"
            )
        os.replace(normalized, destination)
    except subprocess.CalledProcessError as error:
        detail = error.stderr.decode("utf-8", errors="replace").strip()
        message = f"renderer command failed: {detail}" if detail else "renderer command failed"
        raise CoverRenderError(message) from error
    except OSError as error:
        raise CoverRenderError(f"renderer could not write {destination.name}: {error}") from error
    finally:
        raw.unlink(missing_ok=True)
        normalized.unlink(missing_ok=True)


def _publish(staged: list[tuple[Path, Path]], staging: Path) -> None:
    backups: dict[Path, tuple[str, Path | str]] = {}
    for index, (_source, destination) in enumerate(staged):
        if destination.is_symlink():
            backups[destination] = ("symlink", os.readlink(destination))
        elif destination.exists():
            backup = staging / f"backup-{index}"
            shutil.copy2(destination, backup)
            backups[destination] = ("file", backup)

    published: list[Path] = []
    try:
        for source, destination in staged:
            os.replace(source, destination)
            published.append(destination)
    except Exception as publish_error:
        rollback_errors: list[str] = []
        for destination in reversed(published):
            try:
                backup = backups.get(destination)
                if backup is None:
                    destination.unlink(missing_ok=True)
                elif backup[0] == "symlink":
                    destination.unlink(missing_ok=True)
                    os.symlink(backup[1], destination)
                else:
                    os.replace(backup[1], destination)
            except Exception as rollback_error:
                rollback_errors.append(f"{destination}: {rollback_error}")
        if rollback_errors:
            raise CoverRenderError(
                "artifact publication failed and rollback failed: "
                + "; ".join(rollback_errors)
            ) from publish_error
        raise


def _validate_artifact_paths(
    spec: ValidatedCoverSpec,
    artifacts: dict[str, Path],
) -> None:
    resolved_artifacts: dict[str, Path] = {}
    names_by_path: dict[Path, str] = {}
    for name, artifact in artifacts.items():
        try:
            resolved = artifact.resolve()
        except (OSError, RuntimeError, ValueError) as error:
            raise CoverRenderError(f"{name} artifact path is invalid: {artifact}") from error
        try:
            resolved.relative_to(spec.path.parent)
        except ValueError as error:
            raise CoverRenderError(
                f"{name} path escapes specification run folder"
            ) from error
        if resolved in names_by_path:
            raise CoverRenderError(
                f"artifact paths collide: {names_by_path[resolved]} and {name}"
            )
        names_by_path[resolved] = name
        resolved_artifacts[name] = resolved

    protected_inputs = {
        spec.path.resolve(),
        spec.art_path.resolve(),
        spec.font_manifest.path.resolve(),
    }
    for record in spec.font_manifest.fonts.values():
        protected_inputs.add(record.path.resolve())
        protected_inputs.add(record.license_path.resolve())
    for name, resolved in resolved_artifacts.items():
        if resolved in protected_inputs:
            raise CoverRenderError(
                f"artifact path aliases renderer input: {name} -> {resolved}"
            )


def render_cover_spec(
    spec_path: Path,
    output_path: Path,
    font_manifest_path: Path = DEFAULT_MANIFEST,
) -> RenderResult:
    spec = load_cover_spec(Path(spec_path), Path(font_manifest_path))
    output = Path(output_path).resolve()
    try:
        output.relative_to(spec.path.parent)
    except ValueError as error:
        raise CoverRenderError("output path escapes specification run folder") from error

    thumbnail = output.with_name(f"{output.stem}-thumbnail.png")
    receipt = output.with_name(f"{output.stem}.render.json")
    _validate_artifact_paths(
        spec,
        {"output": output, "thumbnail": thumbnail, "receipt": receipt},
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    svg = build_svg(spec)

    with tempfile.TemporaryDirectory(prefix=".cover-render-", dir=output.parent) as raw:
        staging = Path(raw)
        raw_svg = staging / "cover.svg"
        staged_output = staging / output.name
        staged_thumbnail = staging / thumbnail.name
        staged_receipt = staging / receipt.name
        raw_svg.write_text(svg, encoding="utf-8")
        _render(raw_svg, staged_output, WIDTH, HEIGHT)
        _render(raw_svg, staged_thumbnail, 160, 256)
        payload = {
            "receipt_version": 1,
            "renderer_version": RENDERER_VERSION,
            "schema_version": 1,
            "candidate": spec.data["candidate"],
            "spec": spec.path.name,
            "spec_sha256": spec.spec_sha256,
            "source_art": spec.art_path.name,
            "source_art_sha256": spec.art_sha256,
            "font_manifest_version": spec.font_manifest.version,
            "font_manifest_sha256": spec.font_manifest.sha256,
            "fonts": {
                font_id: record.sha256
                for font_id, record in sorted(spec.fonts.items())
            },
            "output": output.name,
            "output_sha256": _sha(staged_output),
            "thumbnail": thumbnail.name,
            "thumbnail_sha256": _sha(staged_thumbnail),
            "dimensions": [WIDTH, HEIGHT],
            "colour_mode": "RGB",
            "warnings": list(spec.warnings),
        }
        staged_receipt.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        try:
            _publish(
                [
                    (staged_output, output),
                    (staged_thumbnail, thumbnail),
                    (staged_receipt, receipt),
                ],
                staging,
            )
        except OSError as error:
            raise CoverRenderError(f"rendered artifacts could not be published: {error}") from error

    return RenderResult(
        output,
        thumbnail,
        receipt,
        payload["output_sha256"],
        payload["thumbnail_sha256"],
    )
