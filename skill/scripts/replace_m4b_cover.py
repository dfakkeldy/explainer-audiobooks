#!/usr/bin/env python3
"""Replace M4B cover artwork without changing immutable media content."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

from cover_receipts import normalized_image_sha256, normalized_m4b_art_sha256, verify_package


@dataclass(frozen=True)
class MediaSignature:
    audio_packet_sha256: str
    streams: tuple[tuple[str, str], ...]
    duration: str
    chapters: tuple[tuple[str, str, str], ...]
    format_tags: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class M4BCoverReplacement:
    output: str
    artwork_sha256: str
    normalized_artwork_sha256: str
    audio_packet_sha256: str
    chapter_count: int


def _path(value: object, label: str) -> Path:
    try:
        return Path(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as error:
        raise ValueError(f"invalid {label} path") from error


def _file(value: object, label: str) -> Path:
    path = _path(value, label)
    try:
        if not path.is_file():
            raise OSError("not a file")
        return path.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise ValueError(f"{label} is missing or invalid: {path}") from error


def _run(command: list[str]) -> subprocess.CompletedProcess[bytes]:
    tool = Path(command[0]).name
    try:
        return subprocess.run(command, check=True, capture_output=True)
    except subprocess.CalledProcessError as error:
        stderr = error.stderr
        detail = (
            stderr.decode("utf-8", errors="replace").strip()
            if isinstance(stderr, bytes)
            else str(stderr).strip() if stderr else ""
        )
        suffix = f": {detail}" if detail else ""
        raise ValueError(f"{tool} command failed{suffix}") from error
    except (OSError, ValueError) as error:
        raise ValueError(f"{tool} command failed") from error


def _parse_probe(payload: bytes) -> tuple[
    tuple[tuple[str, str], ...],
    str,
    tuple[tuple[str, str, str], ...],
    tuple[tuple[str, str], ...],
]:
    try:
        decoded = json.loads(payload)
        raw_streams = decoded["streams"]
        raw_chapters = decoded.get("chapters", [])
        raw_format = decoded["format"]
        raw_tags = raw_format.get("tags", {})
        if not isinstance(raw_streams, list):
            raise TypeError("streams")
        if not isinstance(raw_chapters, list):
            raise TypeError("chapters")
        if not isinstance(raw_format, dict) or not isinstance(raw_tags, dict):
            raise TypeError("format")
        streams = tuple(
            (str(stream["codec_type"]), str(stream["codec_name"]))
            for stream in raw_streams
        )
        chapters = tuple(
            (
                str(chapter["start_time"]),
                str(chapter["end_time"]),
                str(chapter.get("tags", {}).get("title", "")),
            )
            for chapter in raw_chapters
        )
        duration = str(raw_format["duration"])
        tags = tuple(sorted((str(key), str(value)) for key, value in raw_tags.items()))
    except (
        AttributeError,
        json.JSONDecodeError,
        KeyError,
        TypeError,
        UnicodeError,
    ) as error:
        raise ValueError("ffprobe returned invalid JSON metadata") from error
    if not streams or not duration:
        raise ValueError("ffprobe returned incomplete media metadata")
    return streams, duration, chapters, tags


def media_signature(path: Path) -> MediaSignature:
    source = _file(path, "M4B")
    if not shutil.which("ffprobe") or not shutil.which("ffmpeg"):
        raise ValueError("ffmpeg and ffprobe are required")
    probe = _run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_streams",
            "-show_chapters",
            "-show_format",
            "-of",
            "json",
            str(source),
        ]
    )
    streams, duration, chapters, tags = _parse_probe(probe.stdout)
    packets = _run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            str(source),
            "-map",
            "0:a:0",
            "-c",
            "copy",
            "-f",
            "data",
            "-",
        ]
    )
    if not packets.stdout:
        raise ValueError("ffmpeg audio packet extraction produced no data")
    return MediaSignature(
        hashlib.sha256(packets.stdout).hexdigest(),
        streams,
        duration,
        chapters,
        tags,
    )


def _validated_output(value: object, source: Path, cover: Path) -> Path:
    output = _path(value, "M4B output")
    try:
        resolved = output.resolve()
        exists = output.exists()
        if exists and not output.is_file():
            raise OSError("output is not a file")
        if resolved == cover or (exists and os.path.samefile(output, cover)):
            raise ValueError("M4B output aliases the input cover")
        if resolved == source or (exists and os.path.samefile(output, source)):
            raise ValueError(
                "M4B output aliases the source M4B; "
                "in-place replacement is not supported"
            )
    except (OSError, RuntimeError) as error:
        raise ValueError(f"invalid M4B output path: {output}") from error
    return output


def replace_m4b_cover(
    source: Path,
    cover: Path,
    output: Path,
    *,
    selection_path: Path | None = None,
    portrait_cover_path: Path | None = None,
) -> M4BCoverReplacement:
    if not shutil.which("AtomicParsley"):
        raise ValueError("AtomicParsley is required")
    source_path = _file(source, "AtomicParsley source M4B")
    cover_path = _file(cover, "AtomicParsley cover")
    output_path = _validated_output(output, source_path, cover_path)
    if selection_path is not None:
        if portrait_cover_path is None:
            raise ValueError("portrait cover is required with a cover selection")
        verify_package(selection_path, portrait_cover_path, m4b_cover_path=cover_path)
    before = media_signature(source_path)

    temporary: Path | None = None
    descriptor: int | None = None
    try:
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            descriptor, raw = tempfile.mkstemp(
                prefix=f".{output_path.name}.",
                suffix=".m4b",
                dir=output_path.parent,
            )
            temporary = Path(raw)
            os.close(descriptor)
            descriptor = None
            temporary.unlink()
        except (OSError, RuntimeError) as error:
            raise ValueError(
                f"M4B temporary output could not be created: {output_path}"
            ) from error

        _run(
            [
                "AtomicParsley",
                str(source_path),
                "--artwork",
                "REMOVE_ALL",
                "--artwork",
                str(cover_path),
                "--output",
                str(temporary),
            ]
        )
        if not temporary.is_file():
            raise ValueError("AtomicParsley produced no M4B output")
        after = media_signature(temporary)
        if after != before:
            raise ValueError("M4B media signature changed while replacing artwork")
        if sum(codec_type == "video" for codec_type, _ in after.streams) != 1:
            raise ValueError("M4B replacement must contain exactly one artwork item")

        normalized = normalized_image_sha256(cover_path)
        if normalized_m4b_art_sha256(temporary) != normalized:
            raise ValueError("M4B replacement artwork does not match source cover")
        if selection_path is not None:
            verify_package(
                selection_path, portrait_cover_path,
                m4b_cover_path=cover_path, m4b_path=temporary,
            )
        try:
            artwork_sha256 = hashlib.sha256(cover_path.read_bytes()).hexdigest()
        except OSError as error:
            raise ValueError(f"AtomicParsley cover could not be read: {cover_path}") from error
        result = M4BCoverReplacement(
            str(output_path),
            artwork_sha256,
            normalized,
            after.audio_packet_sha256,
            len(after.chapters),
        )

        try:
            os.replace(temporary, output_path)
        except OSError as error:
            raise ValueError(f"M4B output could not be published: {output_path}") from error
        temporary = None
        return result
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--m4b", required=True, type=Path)
    parser.add_argument("--cover", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--cover-selection", type=Path)
    parser.add_argument("--portrait-cover", type=Path)
    arguments = parser.parse_args()
    print(
        json.dumps(
            asdict(replace_m4b_cover(
                arguments.m4b, arguments.cover, arguments.out,
                selection_path=arguments.cover_selection,
                portrait_cover_path=arguments.portrait_cover,
            )),
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
