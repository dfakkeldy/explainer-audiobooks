from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cover_fonts import DEFAULT_MANIFEST, CoverFontError, FontManifest, FontRecord, load_font_manifest, read_ttf_codepoints

VARIANT_CANVASES = {
    "portrait": (1600, 2560, 96),
    "square": (2400, 2400, 120),
}

# Portrait defaults remain exported for renderer compatibility while rendering
# migrates to the per-spec dimensions exposed by ValidatedCoverSpec.
WIDTH, HEIGHT, SAFE_MARGIN = VARIANT_CANVASES["portrait"]
COLOUR = re.compile(r"^#[0-9A-Fa-f]{6}$")
BLENDS = {"normal", "multiply", "screen", "overlay", "soft-light"}
ART_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}
TEXT_KEYS = {
    "kind",
    "role",
    "title_order",
    "text",
    "font_id",
    "font_variation",
    "box",
    "size",
    "line_height",
    "tracking",
    "align",
    "colour",
    "opacity",
    "rotation",
    "baseline_shift",
    "outline",
    "shadow",
    "runs",
    "contrast_against",
    "blend_mode",
}
TEXT_REQUIRED_KEYS = {
    "kind",
    "role",
    "text",
    "font_id",
    "box",
    "size",
    "line_height",
    "tracking",
    "align",
    "colour",
    "opacity",
    "rotation",
    "baseline_shift",
}
FIELD_KEYS = {"kind", "box", "fill", "opacity", "blend_mode", "purpose"}
SHAPE_KEYS = {
    "kind",
    "shape",
    "box",
    "fill",
    "stroke",
    "stroke_width",
    "radius",
    "opacity",
    "rotation",
    "blend_mode",
    "purpose",
}
LINE_KEYS = {"kind", "start", "end", "colour", "width", "opacity", "purpose"}
RUN_KEYS = {"text", "colour", "size_scale", "rotation", "baseline_shift", "dx", "tracking"}
class CoverSpecError(ValueError):
    pass


@dataclass(frozen=True)
class ValidatedCoverSpec:
    path: Path
    data: dict[str, Any]
    metadata: dict[str, str]
    variant: str
    width: int
    height: int
    dimensions: tuple[int, int]
    art_path: Path
    spec_sha256: str
    art_sha256: str
    font_manifest: FontManifest
    fonts: dict[str, FontRecord]
    warnings: tuple[str, ...]


def _canonical_digest(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _safe_child(root: Path, raw: str, label: str) -> Path:
    try:
        resolved_root = root.resolve()
        candidate = (resolved_root / raw).resolve()
    except (OSError, RuntimeError, ValueError) as error:
        raise CoverSpecError(f"{label} path is invalid: {raw}") from error
    try:
        candidate.relative_to(resolved_root)
    except ValueError as error:
        raise CoverSpecError(f"{label} path escapes run folder: {raw}") from error
    return candidate


def _number(value: object, low: float, high: float, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise CoverSpecError(f"{label} must be numeric")
    try:
        result = float(value)
    except (OverflowError, TypeError, ValueError) as error:
        raise CoverSpecError(f"{label} must be numeric") from error
    if not low <= result <= high:
        raise CoverSpecError(f"{label} must be between {low:g} and {high:g}")
    return result


def _box(
    value: object,
    label: str,
    canvas: tuple[int, int],
) -> tuple[float, float, float, float]:
    if not isinstance(value, list) or len(value) != 4:
        raise CoverSpecError(f"{label} must contain x, y, width, height")
    canvas_width, canvas_height = canvas
    x = _number(value[0], -canvas_width, canvas_width * 2, f"{label} x")
    y = _number(value[1], -canvas_height, canvas_height * 2, f"{label} y")
    width = _number(value[2], 1, canvas_width * 2, f"{label} width")
    height = _number(value[3], 1, canvas_height * 2, f"{label} height")
    return x, y, width, height


def _point(value: object, label: str, canvas: tuple[int, int]) -> tuple[float, float]:
    if not isinstance(value, list) or len(value) != 2:
        raise CoverSpecError(f"{label} must contain x and y")
    return (
        _number(value[0], -canvas[0], canvas[0] * 2, f"{label} x"),
        _number(value[1], -canvas[1], canvas[1] * 2, f"{label} y"),
    )


def _colour(value: object, label: str) -> str:
    if not isinstance(value, str) or not COLOUR.fullmatch(value):
        raise CoverSpecError(f"{label} must be #RRGGBB")
    return value.upper()


def _is_choice(value: object, choices: set[str]) -> bool:
    return isinstance(value, str) and value in choices


def _tokens(value: str) -> list[str]:
    normalized = unicodedata.normalize("NFC", unicodedata.normalize("NFC", value).casefold())
    tokens: list[str] = []
    current: list[str] = []
    for index, character in enumerate(normalized):
        if character.isalnum():
            current.append(character)
        elif (
            character in {"'", "’"}
            and current
            and index + 1 < len(normalized)
            and normalized[index + 1].isalnum()
        ):
            current.append("'")
        elif current:
            tokens.append("".join(current))
            current = []
    if current:
        tokens.append("".join(current))
    return tokens


def _validate_glyphs(value: str, font: FontRecord, label: str) -> None:
    codepoints = read_ttf_codepoints(font.path)
    for character in unicodedata.normalize("NFC", value):
        codepoint = ord(character)
        if character.isspace():
            continue
        if codepoint in codepoints:
            continue
        name = unicodedata.name(character, f"U+{codepoint:04X}")
        raise CoverSpecError(f"{label} contains unsupported glyph {name} for {font.font_id}")


def _luminance(value: str) -> float:
    components = [int(value[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        component / 12.92
        if component <= 0.04045
        else ((component + 0.055) / 1.055) ** 2.4
        for component in components
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast(first: str, second: str) -> float:
    high, low = sorted((_luminance(first), _luminance(second)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def _validate_fill(fill: object, label: str, canvas: tuple[int, int]) -> None:
    if not isinstance(fill, dict):
        raise CoverSpecError(f"{label} must be an object")
    if fill.get("kind") == "solid":
        if set(fill) != {"kind", "colour"}:
            raise CoverSpecError(f"{label} solid fill has unknown keys")
        _colour(fill.get("colour"), f"{label} colour")
        return
    if fill.get("kind") != "linear-gradient":
        raise CoverSpecError(f"{label} kind must be solid or linear-gradient")
    if set(fill) != {"kind", "start", "end", "stops"}:
        raise CoverSpecError(f"{label} gradient has unknown keys")
    _point(fill.get("start"), f"{label} start", canvas)
    _point(fill.get("end"), f"{label} end", canvas)
    stops = fill.get("stops")
    if not isinstance(stops, list) or len(stops) < 2:
        raise CoverSpecError(f"{label} requires at least two stops")
    previous = -1.0
    for index, stop in enumerate(stops):
        if not isinstance(stop, dict):
            raise CoverSpecError(f"{label} stop {index + 1} must be an object")
        if set(stop) != {"offset", "colour", "opacity"}:
            raise CoverSpecError(f"{label} stop {index + 1} has unknown keys")
        offset = _number(stop.get("offset"), 0, 1, f"{label} stop offset")
        if offset < previous:
            raise CoverSpecError(f"{label} stop offsets must be sorted")
        previous = offset
        _colour(stop.get("colour"), f"{label} stop colour")
        _number(stop.get("opacity"), 0, 1, f"{label} stop opacity")


def _validate_runs(runs: object, layer: dict[str, Any], index: int) -> None:
    text = layer["text"]
    if "\n" in text or not isinstance(runs, list) or not runs:
        raise CoverSpecError(f"layer {index} runs require one non-empty line")
    run_texts: list[str] = []
    for run_index, run in enumerate(runs):
        if not isinstance(run, dict):
            raise CoverSpecError(f"layer {index} run {run_index + 1} is invalid")
        unknown = set(run) - RUN_KEYS
        if unknown:
            raise CoverSpecError(f"layer {index} run {run_index + 1} has unknown keys")
        run_text = run.get("text")
        if not isinstance(run_text, str) or not run_text:
            raise CoverSpecError(f"layer {index} run {run_index + 1} is invalid")
        run_texts.append(run_text)
        if "colour" in run:
            _colour(run["colour"], f"layer {index} run colour")
        _number(run.get("size_scale", 1), 0.5, 1.5, f"layer {index} run size_scale")
        _number(run.get("rotation", 0), -12, 12, f"layer {index} run rotation")
        _number(run.get("baseline_shift", 0), -80, 80, f"layer {index} run baseline_shift")
        _number(run.get("dx", 0), -80, 80, f"layer {index} run dx")
        _number(
            run.get("tracking", layer["tracking"]),
            -8,
            40,
            f"layer {index} run tracking",
        )
    if "".join(run_texts) != text:
        raise CoverSpecError(f"layer {index} runs must concatenate to layer text")


def _validate_font_variation(value: object, font: FontRecord) -> None:
    if not isinstance(value, dict):
        raise CoverSpecError(f"font {font.font_id} variation must be an object")
    for axis, axis_value in value.items():
        if axis not in font.axes:
            raise CoverSpecError(f"font {font.font_id} does not support axis {axis}")
        low, high = font.axes[axis]
        _number(axis_value, low, high, f"axis {axis}")


def _validate_outline(value: object, index: int) -> None:
    if not isinstance(value, dict):
        raise CoverSpecError(f"layer {index} outline must be an object")
    unknown = set(value) - {"colour", "width"}
    if unknown:
        raise CoverSpecError(f"layer {index} outline has unknown keys")
    if set(value) != {"colour", "width"}:
        raise CoverSpecError(f"layer {index} outline requires colour and width")
    _colour(value["colour"], f"layer {index} outline colour")
    _number(value["width"], 0, 16, f"layer {index} outline width")


def _validate_shadow(value: object, index: int) -> None:
    if not isinstance(value, dict):
        raise CoverSpecError(f"layer {index} shadow must be an object")
    allowed = {"colour", "dx", "dy", "blur", "opacity"}
    unknown = set(value) - allowed
    if unknown:
        raise CoverSpecError(f"layer {index} shadow has unknown keys")
    if set(value) != allowed:
        raise CoverSpecError(f"layer {index} shadow requires colour, dx, dy, blur, and opacity")
    _colour(value["colour"], f"layer {index} shadow colour")
    _number(value["dx"], -48, 48, f"layer {index} shadow dx")
    _number(value["dy"], -48, 48, f"layer {index} shadow dy")
    _number(value["blur"], 0, 48, f"layer {index} shadow blur")
    _number(value["opacity"], 0, 1, f"layer {index} shadow opacity")


def _validate_text(
    layer: dict[str, Any],
    index: int,
    manifest: FontManifest,
    warnings: list[str],
    canvas: tuple[int, int],
    safe_margin: int,
) -> FontRecord:
    unknown = set(layer) - TEXT_KEYS
    if unknown:
        raise CoverSpecError(f"layer {index} has unknown keys: {sorted(unknown)}")
    missing = TEXT_REQUIRED_KEYS - set(layer)
    if missing:
        raise CoverSpecError(f"layer {index} text has missing keys: {sorted(missing)}")
    role = layer.get("role")
    if not _is_choice(role, {"title", "subtitle", "author", "label"}):
        raise CoverSpecError(f"layer {index} has invalid text role")
    text = layer.get("text")
    if not isinstance(text, str) or not text.strip():
        raise CoverSpecError(f"layer {index} text is empty")
    if "title_order" in layer:
        title_order = layer["title_order"]
        if isinstance(title_order, bool) or not isinstance(title_order, int) or title_order < 1:
            raise CoverSpecError(f"layer {index} title_order must be a positive integer")
    elif role == "title":
        raise CoverSpecError(f"layer {index} title requires title_order")
    font_id = layer.get("font_id")
    if not isinstance(font_id, str) or not font_id:
        raise CoverSpecError(f"layer {index} font_id must be a non-empty string")
    font = manifest.require(font_id, role=role)
    _validate_glyphs(text, font, f"layer {index}")
    x, y, width, height = _box(layer.get("box"), f"layer {index} box", canvas)
    if (
        x < safe_margin
        or y < safe_margin
        or x + width > canvas[0] - safe_margin
        or y + height > canvas[1] - safe_margin
    ):
        raise CoverSpecError(f"layer {index} text is outside {safe_margin}px safe margin")
    minimum = {"title": 72, "subtitle": 36, "author": 28, "label": 28}[role]
    size = _number(layer.get("size"), minimum, 420, f"layer {index} size")
    line_height = _number(layer.get("line_height"), minimum, 500, f"layer {index} line_height")
    tracking = _number(layer.get("tracking"), -8, 40, f"layer {index} tracking")
    _number(layer.get("opacity"), 0, 1, f"layer {index} opacity")
    _number(layer.get("rotation"), -12, 12, f"layer {index} rotation")
    _number(layer.get("baseline_shift"), -80, 80, f"layer {index} baseline_shift")
    if not _is_choice(layer.get("align"), {"left", "center", "right"}):
        raise CoverSpecError(f"layer {index} align must be left, center, or right")
    if not _is_choice(layer.get("blend_mode", "normal"), BLENDS):
        raise CoverSpecError(f"layer {index} has invalid blend_mode")
    colour = _colour(layer.get("colour"), f"layer {index} colour")
    lines = text.split("\n")
    if len(lines) * line_height > height:
        raise CoverSpecError(f"layer {index} text exceeds box height")
    longest = max(lines, key=len)
    estimated = len(longest) * size * font.width_factor + max(0, len(longest) - 1) * tracking
    if estimated > width * 1.12:
        raise CoverSpecError(f"layer {index} text exceeds box width estimate")
    if "runs" in layer:
        _validate_runs(layer["runs"], layer, index)
    _validate_font_variation(layer.get("font_variation", {}), font)
    if "outline" in layer:
        _validate_outline(layer["outline"], index)
    if "shadow" in layer:
        _validate_shadow(layer["shadow"], index)
    against = layer.get("contrast_against")
    if against is None:
        warnings.append(f"layer {index} contrast is unverified over complex art")
    else:
        background = _colour(against, f"layer {index} contrast_against")
        ratio = _contrast(colour, background)
        if ratio < 4.5:
            warnings.append(f"layer {index} advisory contrast ratio is {ratio:.2f}:1")
    return font


def _validate_field(layer: dict[str, Any], index: int, kind: str, canvas: tuple[int, int]) -> None:
    if set(layer) - FIELD_KEYS:
        raise CoverSpecError(f"layer {index} has unknown keys")
    _box(layer.get("box"), f"layer {index} box", canvas)
    _validate_fill(layer.get("fill"), f"layer {index} fill", canvas)
    _number(layer.get("opacity"), 0, 1, f"layer {index} opacity")
    if not _is_choice(layer.get("blend_mode"), BLENDS):
        raise CoverSpecError(f"layer {index} has invalid blend_mode")
    purpose = layer.get("purpose")
    if not isinstance(purpose, str) or not purpose.strip():
        raise CoverSpecError(f"{kind} layer requires compositional purpose")


def _validate_shape(layer: dict[str, Any], index: int, canvas: tuple[int, int]) -> None:
    if set(layer) - SHAPE_KEYS:
        raise CoverSpecError(f"layer {index} has unknown keys")
    if not _is_choice(layer.get("shape"), {"rect", "ellipse"}):
        raise CoverSpecError(f"layer {index} has invalid shape")
    _box(layer.get("box"), f"layer {index} box", canvas)
    _validate_fill(layer.get("fill"), f"layer {index} fill", canvas)
    _number(layer.get("opacity"), 0, 1, f"layer {index} opacity")
    _number(layer.get("rotation"), -180, 180, f"layer {index} rotation")
    _number(layer.get("stroke_width", 0), 0, 40, f"layer {index} stroke_width")
    _number(layer.get("radius", 0), 0, 300, f"layer {index} radius")
    if "stroke" in layer:
        _colour(layer["stroke"], f"layer {index} stroke")
    purpose = layer.get("purpose")
    if (
        not _is_choice(layer.get("blend_mode"), BLENDS)
        or not isinstance(purpose, str)
        or not purpose.strip()
    ):
        raise CoverSpecError(f"layer {index} shape requires valid blend_mode and purpose")


def _validate_line(layer: dict[str, Any], index: int, canvas: tuple[int, int]) -> None:
    if set(layer) - LINE_KEYS:
        raise CoverSpecError(f"layer {index} has unknown keys")
    _point(layer.get("start"), f"layer {index} start", canvas)
    _point(layer.get("end"), f"layer {index} end", canvas)
    _colour(layer.get("colour"), f"layer {index} colour")
    _number(layer.get("width"), 1, 40, f"layer {index} width")
    _number(layer.get("opacity"), 0, 1, f"layer {index} opacity")
    purpose = layer.get("purpose")
    if not isinstance(purpose, str) or not purpose.strip():
        raise CoverSpecError("line layer requires compositional purpose")


def _load_manifest(path: Path) -> FontManifest:
    try:
        return load_font_manifest(path)
    except CoverFontError:
        raise
    except (AttributeError, IndexError, KeyError, TypeError, ValueError) as error:
        raise CoverFontError(f"invalid font manifest: {path}") from error


def load_cover_spec(
    path: Path,
    font_manifest_path: Path = DEFAULT_MANIFEST,
    *,
    canonical_title: str | None = None,
    canonical_subtitle: str | None = None,
    canonical_author: str | None = None,
    canonical_label: str | None = None,
) -> ValidatedCoverSpec:
    try:
        spec_path = Path(path).resolve()
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise CoverSpecError(f"invalid cover specification path: {path}") from error
    try:
        payload = json.loads(spec_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CoverSpecError(f"invalid cover specification: {spec_path}") from error
    if not isinstance(payload, dict):
        raise CoverSpecError("cover specification must be an object")
    schema_version = payload.get("schema_version")
    if (
        isinstance(schema_version, bool)
        or not isinstance(schema_version, (int, float))
        or schema_version != 1
    ):
        raise CoverSpecError("schema_version must be 1")
    if set(payload) != {"schema_version", "variant", "candidate", "metadata", "canvas", "art", "layers"}:
        raise CoverSpecError("cover specification has missing or unknown top-level fields")

    variant = payload.get("variant")
    if not isinstance(variant, str) or variant not in VARIANT_CANVASES:
        raise CoverSpecError("variant must be portrait or square")
    width, height, safe_margin = VARIANT_CANVASES[variant]

    candidate = payload.get("candidate")
    if not isinstance(candidate, dict):
        raise CoverSpecError("candidate requires a slug-like id and direction_name")
    candidate_id = candidate.get("id")
    direction_name = candidate.get("direction_name")
    if (
        not isinstance(candidate_id, str)
        or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", candidate_id)
        or not isinstance(direction_name, str)
        or not direction_name
    ):
        raise CoverSpecError("candidate requires a slug-like id and direction_name")
    if set(candidate) != {"id", "direction_name"}:
        raise CoverSpecError("candidate has missing or unknown fields")

    metadata = payload.get("metadata")
    if not isinstance(metadata, dict) or set(metadata) != {"title", "subtitle", "author", "label"}:
        raise CoverSpecError("metadata must contain title, subtitle, author, and label")
    if (
        any(not isinstance(metadata[key], str) for key in metadata)
        or not metadata["title"]
        or not metadata["author"]
        or not metadata["label"]
    ):
        raise CoverSpecError("canonical metadata strings are invalid")

    canvas = payload.get("canvas")
    if not isinstance(canvas, dict) or (
        canvas.get("width"), canvas.get("height"), canvas.get("safe_margin")
    ) != (width, height, safe_margin):
        raise CoverSpecError(
            f"{variant} canvas must be {width}x{height} with {safe_margin}px safe margin"
        )
    if set(canvas) != {"width", "height", "background", "safe_margin"}:
        raise CoverSpecError("canvas has missing or unknown fields")
    _colour(canvas.get("background"), "canvas background")
    canvas_dimensions = (width, height)

    art = payload.get("art")
    if not isinstance(art, dict):
        raise CoverSpecError("art must be an object")
    if set(art) - {"path", "mode", "anchor", "box", "opacity", "blend_mode", "mask"}:
        raise CoverSpecError("art has unknown fields")
    raw_art_path = art.get("path")
    if not isinstance(raw_art_path, str) or not raw_art_path:
        raise CoverSpecError("art path must be a non-empty string")
    art_path = _safe_child(spec_path.parent, raw_art_path, "art")
    if not art_path.is_file() or art_path.suffix.lower() not in ART_SUFFIXES:
        raise CoverSpecError("art must be an existing SVG, PNG, JPEG, WebP, or GIF")
    if not _is_choice(art.get("mode"), {"bleed", "fit", "crop"}) or not _is_choice(
        art.get("anchor"),
        {"center", "center-top", "center-bottom", "left", "right"},
    ):
        raise CoverSpecError("art mode or anchor is invalid")
    _box(art.get("box"), "art box", canvas_dimensions)
    _number(art.get("opacity"), 0, 1, "art opacity")
    if not _is_choice(art.get("blend_mode"), BLENDS):
        raise CoverSpecError("art blend_mode is invalid")
    if "mask" in art:
        mask = art["mask"]
        if not isinstance(mask, dict) or not _is_choice(mask.get("shape"), {"rect", "ellipse"}):
            raise CoverSpecError("art mask must be rect or ellipse")
        if set(mask) - {"shape", "box", "radius"}:
            raise CoverSpecError("art mask has unknown fields")
        _box(mask.get("box"), "art mask box", canvas_dimensions)
        _number(mask.get("radius", 0), 0, 300, "art mask radius")

    try:
        manifest_path = Path(font_manifest_path)
    except (TypeError, ValueError) as error:
        raise CoverFontError(f"invalid font manifest: {font_manifest_path}") from error
    manifest = _load_manifest(manifest_path)
    layers = payload.get("layers")
    if not isinstance(layers, list) or not layers:
        raise CoverSpecError("layers must be a non-empty array")
    warnings: list[str] = []
    fonts: dict[str, FontRecord] = {}
    for index, layer in enumerate(layers, start=1):
        if not isinstance(layer, dict):
            raise CoverSpecError(f"layer {index} must be an object")
        kind = layer.get("kind")
        if kind == "text":
            font = _validate_text(
                layer, index, manifest, warnings, canvas_dimensions, safe_margin
            )
            fonts[font.font_id] = font
        elif _is_choice(kind, {"field", "scrim"}):
            _validate_field(layer, index, kind, canvas_dimensions)
        elif kind == "shape":
            _validate_shape(layer, index, canvas_dimensions)
        elif kind == "line":
            _validate_line(layer, index, canvas_dimensions)
        else:
            raise CoverSpecError(f"unknown layer kind: {kind}")

    title_layers = sorted(
        (layer for layer in layers if layer.get("kind") == "text" and layer.get("role") == "title"),
        key=lambda layer: layer["title_order"],
    )
    expected_title = canonical_title if canonical_title is not None else metadata["title"]
    if canonical_title is not None and metadata["title"] != canonical_title:
        raise CoverSpecError("metadata title must match canonical title")
    if _tokens(" ".join(layer["text"] for layer in title_layers)) != _tokens(expected_title):
        raise CoverSpecError("title layers must reproduce canonical title")
    canonical_metadata = {
        "subtitle": canonical_subtitle,
        "author": canonical_author,
        "label": canonical_label,
    }
    for role in ("subtitle", "author", "label"):
        expected = canonical_metadata[role]
        if expected is not None:
            if role == "subtitle" and variant == "square" and metadata[role] == "":
                expected = ""
            elif metadata[role] != expected:
                raise CoverSpecError(f"metadata {role} must match canonical {role}")
        displayed = " ".join(
            layer["text"]
            for layer in layers
            if layer.get("kind") == "text" and layer.get("role") == role
        )
        if _tokens(displayed) != _tokens(expected if expected is not None else metadata[role]):
            raise CoverSpecError(f"{role} layers must reproduce canonical metadata")
    try:
        art_sha256 = hashlib.sha256(art_path.read_bytes()).hexdigest()
        spec_sha256 = _canonical_digest(payload)
    except (OSError, TypeError, ValueError) as error:
        raise CoverSpecError("cover specification content could not be hashed") from error
    return ValidatedCoverSpec(
        path=spec_path,
        data=payload,
        metadata={key: value for key, value in metadata.items()},
        variant=variant,
        width=width,
        height=height,
        dimensions=canvas_dimensions,
        art_path=art_path,
        spec_sha256=spec_sha256,
        art_sha256=art_sha256,
        font_manifest=manifest,
        fonts=fonts,
        warnings=tuple(warnings),
    )
