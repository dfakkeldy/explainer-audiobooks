import hashlib
import json
import os
import subprocess
import unittest
from pathlib import Path

from skill.scripts.verify_public_first_listen import verify_public_package


ROOT = Path(__file__).resolve().parents[1]
PRIVATE_ROOT = Path(
    os.environ.get(
        "CLAUDE_PLATFORM_PRIVATE_BOOK_ROOT",
        Path.home() / "Documents" / "Codex" / "custom-learning-audiobooks",
    )
)

CASES = {
    "claude-platform-01-the-message": {
        "chapters": 12,
        "anchors": 571,
        "duration": (7409, 7410),
        "title": "The Message",
        "private_directory": "claude-platform-01-the-message-road-book-v2",
        "private_stem": "claude-platform-01-the-message-road-book-v2",
    },
    "claude-platform-02-thinking-and-reliable-responses": {
        "chapters": 13,
        "anchors": 346,
        "duration": (5316, 5317),
        "title": "Making Claude Think and Respond Reliably",
        "private_directory": "claude-platform-02-thinking-and-reliable-responses",
        "private_stem": "claude-platform-02-thinking-and-reliable-responses",
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe_m4b(path: Path) -> dict[str, object]:
    completed = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration:format_tags=title,artist:chapter=start_time,end_time",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


class ClaudePlatformPublicSeriesTests(unittest.TestCase):
    def test_public_packages_are_complete_and_public_safe(self) -> None:
        for slug, expected in CASES.items():
            with self.subTest(slug=slug):
                book_dir = ROOT / "books" / slug
                verify_public_package(book_dir)

                alignment = json.loads(
                    (book_dir / f"{slug}.alignment.json").read_text(encoding="utf-8")
                )
                self.assertEqual(
                    expected["anchors"],
                    len(alignment),
                    f"{slug}: unexpected alignment anchor count",
                )

                media = probe_m4b(book_dir / f"{slug}.m4b")
                chapters = media.get("chapters")
                self.assertIsInstance(chapters, list, f"{slug}: ffprobe returned no chapter list")
                self.assertEqual(
                    expected["chapters"],
                    len(chapters),
                    f"{slug}: unexpected embedded chapter count",
                )
                media_format = media.get("format")
                self.assertIsInstance(media_format, dict, f"{slug}: ffprobe returned no format metadata")
                duration = float(media_format["duration"])
                self.assertGreaterEqual(
                    duration,
                    expected["duration"][0],
                    f"{slug}: duration is shorter than the approved runtime",
                )
                self.assertLess(
                    duration,
                    expected["duration"][1],
                    f"{slug}: duration is longer than the approved runtime",
                )
                tags = media_format.get("tags", {})
                self.assertEqual(expected["title"], tags.get("title"), f"{slug}: wrong M4B title")
                self.assertEqual("Dan Fakkeldy", tags.get("artist"), f"{slug}: wrong M4B artist")

                for path in book_dir.rglob("*"):
                    relative = path.relative_to(book_dir)
                    lowered_parts = {part.casefold() for part in relative.parts}
                    lowered_name = path.name.casefold()
                    self.assertNotIn("research", lowered_parts, f"{slug}: forbidden path {relative}")
                    self.assertFalse(
                        lowered_name.startswith("echo-render-")
                        or "pronunciation-audit" in lowered_name
                        or "pronunciation-reel" in lowered_name
                        or "resume-state" in lowered_name,
                        f"{slug}: forbidden file {relative}",
                    )

    def test_public_media_matches_available_private_masters(self) -> None:
        for slug, expected in CASES.items():
            with self.subTest(slug=slug):
                private_dir = PRIVATE_ROOT / expected["private_directory"]
                if not private_dir.exists():
                    continue

                private_stem = expected["private_stem"]
                pairs = (
                    (f"{slug}.m4b", f"{private_stem}.m4b"),
                    (f"{slug}.alignment.json", f"{private_stem}.alignment.json"),
                )
                for public_name, private_name in pairs:
                    public_path = ROOT / "books" / slug / public_name
                    private_path = private_dir / private_name
                    if not private_path.is_file():
                        continue
                    self.assertEqual(
                        sha256(private_path),
                        sha256(public_path),
                        f"{slug}: public {public_name} differs from private master {private_name}",
                    )


if __name__ == "__main__":
    unittest.main()
