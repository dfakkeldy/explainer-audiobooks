#!/usr/bin/env python3
"""Render silent landscape and portrait review reels in chapter cue order."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from stage_visual_chapters import load_placements


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_set_sha256(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.name.encode("utf-8"))
        digest.update(bytes.fromhex(sha256_file(path)))
    return digest.hexdigest()


def ffconcat_path(path: Path) -> str:
    return path.resolve().as_posix().replace("'", "'\\''")


def render_profile(
    *,
    name: str,
    images_dir: Path,
    output: Path,
    width: int,
    height: int,
    seconds_per_image: float,
    filenames: list[str],
) -> dict[str, object]:
    images = [images_dir / filename for filename in filenames]
    missing = [str(path) for path in images if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing {name} review images: {missing}")

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".ffconcat") as manifest:
        manifest.write("ffconcat version 1.0\n")
        for image in images:
            manifest.write(f"file '{ffconcat_path(image)}'\n")
            manifest.write(f"duration {seconds_per_image:.3f}\n")
        manifest.write(f"file '{ffconcat_path(images[-1])}'\n")
        manifest.flush()

        video_filter = (
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=0x13242b,"
            "setsar=1,fps=30,format=yuv420p"
        )
        subprocess.run(
            [
                "ffmpeg",
                "-loglevel",
                "error",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                manifest.name,
                "-vf",
                video_filter,
                "-an",
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "19",
                "-movflags",
                "+faststart",
                str(output),
            ],
            check=True,
        )

    probe = json.loads(
        subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width,height:format=duration",
                "-of",
                "json",
                str(output),
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    )
    stream = probe["streams"][0]
    return {
        "profile": name,
        "file": output.name,
        "sha256": sha256_file(output),
        "dimensions": [stream["width"], stream["height"]],
        "durationSeconds": float(probe["format"]["duration"]),
        "sourceSetSha256": source_set_sha256(images),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--landscape-images", type=Path, required=True)
    parser.add_argument("--mobile-images", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seconds-per-image", type=float, default=2.0)
    args = parser.parse_args()

    placements = load_placements()
    filenames = [str(placement["filename"]) for placement in placements]
    figure_ids = [str(placement["id"]) for placement in placements]
    outputs = [
        render_profile(
            name="landscape",
            images_dir=args.landscape_images,
            output=args.output_dir / "tax-sale-54-figure-landscape-review.mp4",
            width=1920,
            height=1080,
            seconds_per_image=args.seconds_per_image,
            filenames=filenames,
        ),
        render_profile(
            name="portrait",
            images_dir=args.mobile_images,
            output=args.output_dir / "tax-sale-54-figure-portrait-review.mp4",
            width=1080,
            height=1920,
            seconds_per_image=args.seconds_per_image,
            filenames=filenames,
        ),
    ]
    receipt = {
        "schemaVersion": 1,
        "status": "silent-visual-review-only",
        "figureCount": len(filenames),
        "secondsPerFigure": args.seconds_per_image,
        "audioIncluded": False,
        "narrationAlignmentClaimed": False,
        "publicationClaimed": False,
        "figureIdsInCueOrder": figure_ids,
        "outputs": outputs,
    }
    receipt_path = args.output_dir / "video-proof-receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
