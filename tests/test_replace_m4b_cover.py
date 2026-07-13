from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from PIL import Image

sys.path.insert(0, str(Path(__file__).parents[1] / "skill" / "scripts"))
from cover_receipts import normalized_image_sha256, normalized_m4b_art_sha256
import replace_m4b_cover as subject
from replace_m4b_cover import MediaSignature, media_signature, replace_m4b_cover


def fixture_signature(*, duration: str = "0.250000") -> MediaSignature:
    return MediaSignature(
        audio_packet_sha256="a" * 64,
        streams=(("audio", "aac"), ("video", "png")),
        duration=duration,
        chapters=(),
        format_tags=(("title", "Fixture"),),
    )


def completed(command: list[str], stdout: bytes = b"") -> subprocess.CompletedProcess[bytes]:
    return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr=b"")


@unittest.skipUnless(all(shutil.which(tool) for tool in ("AtomicParsley", "ffmpeg", "ffprobe", "magick")), "media tools required")
class ReplaceM4BCoverTests(unittest.TestCase):
    def test_replaces_only_artwork_and_preserves_media_signature(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            old_art = root / "old.png"
            new_art = root / "new.png"
            Image.new("RGB", (1600, 2560), "#132238").save(old_art)
            Image.new("RGB", (1600, 2560), "#EF5735").save(new_art)
            audio = root / "audio.m4b"
            tagged = root / "tagged.m4b"
            output = root / "output.m4b"
            subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", "0.25", "-c:a", "aac", "-metadata", "title=Fixture", str(audio)], check=True)
            subprocess.run(["AtomicParsley", str(audio), "--artwork", str(old_art), "--output", str(tagged)], check=True, capture_output=True)
            before = media_signature(tagged)
            result = replace_m4b_cover(tagged, new_art, output)
            self.assertEqual(before, media_signature(output))
            self.assertEqual(before.audio_packet_sha256, result.audio_packet_sha256)
            self.assertEqual(normalized_image_sha256(new_art), normalized_m4b_art_sha256(output))

    def test_failure_does_not_replace_existing_output(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            output = root / "output.m4b"
            output.write_bytes(b"keep-me")
            with self.assertRaisesRegex(ValueError, "AtomicParsley"):
                replace_m4b_cover(root / "missing.m4b", root / "missing.png", output)
            self.assertEqual(b"keep-me", output.read_bytes())

    def test_output_cannot_alias_cover_or_cover_hardlink(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = root / "source.m4b"
            cover = root / "cover.png"
            source.write_bytes(b"source")
            cover.write_bytes(b"cover")
            symlink = root / "cover-symlink.m4b"
            symlink.symlink_to(cover.name)
            hardlink = root / "cover-hardlink.m4b"
            os.link(cover, hardlink)
            original = cover.read_bytes()

            for name, output in {
                "direct": cover,
                "symlink": symlink,
                "hardlink": hardlink,
            }.items():
                with self.subTest(name=name), mock.patch.object(
                    subject,
                    "media_signature",
                    side_effect=AssertionError("alias validation ran too late"),
                ):
                    with self.assertRaisesRegex(ValueError, "cover|alias"):
                        replace_m4b_cover(source, cover, output)

            self.assertEqual(original, cover.read_bytes())

    def test_atomicparsley_failures_are_normalized_and_preserve_output(self) -> None:
        failures = {
            "nonzero": subprocess.CalledProcessError(
                1,
                ["AtomicParsley"],
                stderr=b"replacement failed",
            ),
            "launch": OSError("could not launch"),
        }
        for name, failure in failures.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as raw:
                root = Path(raw)
                source = root / "source.m4b"
                cover = root / "cover.png"
                output = root / "output.m4b"
                source.write_bytes(b"source")
                cover.write_bytes(b"cover")
                output.write_bytes(b"keep-me")
                with mock.patch.object(
                    subject,
                    "media_signature",
                    return_value=fixture_signature(),
                ), mock.patch.object(
                    subject.subprocess,
                    "run",
                    side_effect=failure,
                ), self.assertRaisesRegex(ValueError, "AtomicParsley"):
                    replace_m4b_cover(source, cover, output)

                self.assertEqual(b"keep-me", output.read_bytes())
                self.assertEqual([], list(root.glob(".output.m4b.*")))

    def test_ffprobe_failures_and_invalid_json_are_normalized(self) -> None:
        cases: dict[str, object] = {
            "nonzero": subprocess.CalledProcessError(
                1,
                ["ffprobe"],
                stderr=b"probe failed",
            ),
            "launch": OSError("could not launch"),
            "invalid JSON": completed(["ffprobe"], b"not-json"),
        }
        with tempfile.TemporaryDirectory() as raw:
            source = Path(raw) / "source.m4b"
            source.write_bytes(b"source")
            for name, outcome in cases.items():
                with self.subTest(name=name), mock.patch.object(
                    subject.shutil,
                    "which",
                    return_value="/tool",
                ), mock.patch.object(
                    subject.subprocess,
                    "run",
                    side_effect=outcome if isinstance(outcome, BaseException) else None,
                    return_value=None if isinstance(outcome, BaseException) else outcome,
                ), self.assertRaisesRegex(ValueError, "ffprobe"):
                    media_signature(source)

    def test_ffmpeg_failures_are_normalized(self) -> None:
        payload = json.dumps(
            {
                "streams": [
                    {"codec_type": "audio", "codec_name": "aac"},
                    {"codec_type": "video", "codec_name": "png"},
                ],
                "chapters": [],
                "format": {
                    "duration": "0.250000",
                    "tags": {"title": "Fixture"},
                },
            }
        ).encode("utf-8")
        failures = {
            "nonzero": subprocess.CalledProcessError(
                1,
                ["ffmpeg"],
                stderr=b"packet extraction failed",
            ),
            "launch": OSError("could not launch"),
        }
        with tempfile.TemporaryDirectory() as raw:
            source = Path(raw) / "source.m4b"
            source.write_bytes(b"source")
            for name, failure in failures.items():
                with self.subTest(name=name), mock.patch.object(
                    subject.shutil,
                    "which",
                    return_value="/tool",
                ), mock.patch.object(
                    subject.subprocess,
                    "run",
                    side_effect=[completed(["ffprobe"], payload), failure],
                ), self.assertRaisesRegex(ValueError, "ffmpeg"):
                    media_signature(source)

    def test_post_replacement_mismatches_preserve_existing_output(self) -> None:
        before = fixture_signature()
        mismatched = fixture_signature(duration="9.000000")

        def write_atomicparsley_output(
            command: list[str],
            **_: object,
        ) -> subprocess.CompletedProcess[bytes]:
            temporary = Path(command[command.index("--output") + 1])
            temporary.write_bytes(b"candidate")
            return completed(command)

        cases = {
            "signature": {
                "signatures": [before, mismatched],
                "image_hash": "b" * 64,
                "m4b_hash": "b" * 64,
                "message": "signature",
            },
            "artwork": {
                "signatures": [before, before],
                "image_hash": "b" * 64,
                "m4b_hash": "c" * 64,
                "message": "artwork",
            },
        }
        for name, case in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as raw:
                root = Path(raw)
                source = root / "source.m4b"
                cover = root / "cover.png"
                output = root / "output.m4b"
                source.write_bytes(b"source")
                cover.write_bytes(b"cover")
                output.write_bytes(b"keep-me")
                with mock.patch.object(
                    subject,
                    "media_signature",
                    side_effect=case["signatures"],
                ), mock.patch.object(
                    subject,
                    "normalized_image_sha256",
                    return_value=case["image_hash"],
                ), mock.patch.object(
                    subject,
                    "normalized_m4b_art_sha256",
                    return_value=case["m4b_hash"],
                ), mock.patch.object(
                    subject.subprocess,
                    "run",
                    side_effect=write_atomicparsley_output,
                ), self.assertRaisesRegex(ValueError, str(case["message"])):
                    replace_m4b_cover(source, cover, output)

                self.assertEqual(b"keep-me", output.read_bytes())
                self.assertEqual([], list(root.glob(".output.m4b.*")))


if __name__ == "__main__":
    unittest.main()
