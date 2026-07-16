from __future__ import annotations

import hashlib
import importlib
import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
SCRIPTS = ROOT / "skill" / "scripts"
sys.path.insert(0, str(SCRIPTS))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "ffmpeg required")
class PronunciationProbeReelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.research = self.root / "research"
        self.chapters = self.root / "chapters"
        self.work = self.root / "work"
        self.out = self.root / "dist" / "probe.m4b"
        self.evidence = self.research / "pronunciation-probe-evidence.json"
        self.timing_db = self.root / "narration.sqlite"
        self.research.mkdir()
        self.chapters.mkdir()
        self.work.mkdir()
        self.audio = self.work / "chapter-0.m4a"
        subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-f",
                "lavfi",
                "-i",
                "sine=frequency=440:duration=4",
                "-c:a",
                "aac",
                "-y",
                str(self.audio),
            ],
            check=True,
        )
        self.write_plan()
        self.write_anchor()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def module(self):
        return importlib.import_module("build_pronunciation_probe_reel")

    def write_plan(self) -> None:
        (self.research / "pronunciation-plan.json").write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "terms": [
                        {
                            "term": "hyperparameter",
                            "variants": ["hyperparameters"],
                            "source": "listener",
                            "reason": "Explicit listener request.",
                            "expectedChapters": ["ch01.md"],
                            "required": True,
                            "status": "planned",
                            "decision": None,
                            "evidence": None,
                        }
                    ],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

    def write_anchor(
        self,
        *,
        audio_hash: str | None = None,
        words: list[dict] | None = None,
        decisions: list[dict] | None = None,
    ) -> None:
        if words is None:
            words = [
                {"word": "hyperparameter", "start": 0.75, "end": 1.25},
                {"word": "hyperparameters", "start": 2.25, "end": 2.9},
            ]
        (self.work / ".anchors-ch0.json").write_text(
            json.dumps(
                {
                    "duration": 4.0,
                    "anchors": [{"suffix": "s0-b0", "time": 0.0, "words": words}],
                    "identity": {
                        "schemaVersion": 1,
                        "chapterIndex": 0,
                        "audioFileName": self.audio.name,
                        "audioSHA256": audio_hash or sha256(self.audio),
                    },
                    "pronunciationEvidence": {
                        "decisions": decisions or [],
                        "diagnostics": [],
                    },
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

    def test_builds_reel_and_hash_bound_evidence_for_every_form(self) -> None:
        result = self.module().build_reel(self.root, self.work, self.out, self.evidence)

        self.assertTrue(self.out.is_file())
        self.assertEqual(sha256(self.out), result["reelSHA256"])
        self.assertEqual(
            ["hyperparameter", "hyperparameters"],
            [clip["variantHeard"] for clip in result["clips"]],
        )
        probe = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(self.out),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertGreater(float(probe.stdout.strip()), 0)

    def test_rejects_capture_whose_hash_does_not_match_identity(self) -> None:
        self.write_anchor(audio_hash="0" * 64)
        with self.assertRaisesRegex(ValueError, "capture SHA-256"):
            self.module().build_reel(self.root, self.work, self.out, self.evidence)

    def test_rejects_required_form_without_exact_word_timing(self) -> None:
        self.write_anchor(words=[{"word": "hyperparameter", "start": 0.75, "end": 1.25}])
        with self.assertRaisesRegex(ValueError, "missing timed pronunciation form"):
            self.module().build_reel(self.root, self.work, self.out, self.evidence)

    def test_uses_pronunciation_decision_range_when_exact_word_timing_is_missing(self) -> None:
        self.write_anchor(
            words=[{"word": "hyperparameters", "start": 2.25, "end": 2.9}],
            decisions=[
                {
                    "sourceWord": "hyperparameter",
                    "normalizedWord": "hyperparameter",
                    "timingPrecision": "blockAnchorFallback",
                    "chapterRelativeAudioRange": {"start": 0.5, "end": 1.5},
                    "selectedIPA": "h-test",
                    "ruleID": "g2p.fallback.hyperparameter",
                }
            ],
        )

        result = self.module().build_reel(self.root, self.work, self.out, self.evidence)

        singular = result["clips"][0]
        self.assertEqual("pronunciationDecision", singular["timingSource"])
        self.assertEqual("blockAnchorFallback", singular["timingPrecision"])
        self.assertEqual("g2p.fallback.hyperparameter", singular["ruleID"])
        self.assertEqual(0.0, singular["sourceStart"])
        self.assertEqual(2.75, singular["sourceEnd"])

    def test_uses_narration_database_words_when_capture_omits_them(self) -> None:
        self.write_anchor(words=[])
        with sqlite3.connect(self.timing_db) as database:
            database.executescript(
                """
                CREATE TABLE epub_block (
                    id TEXT PRIMARY KEY,
                    spine_index INTEGER NOT NULL,
                    block_index INTEGER NOT NULL
                );
                CREATE TABLE word_timing (
                    epub_block_id TEXT NOT NULL,
                    word_index INTEGER NOT NULL,
                    word TEXT NOT NULL,
                    audio_start_time REAL NOT NULL,
                    audio_end_time REAL NOT NULL,
                    source TEXT NOT NULL
                );
                INSERT INTO epub_block VALUES ('book-s0-b0', 0, 0);
                INSERT INTO word_timing VALUES
                    ('book-s0-b0', 0, 'hyperparameter', 0.75, 1.25, 'synthesized'),
                    ('book-s0-b0', 1, 'hyperparameters', 2.25, 2.9, 'synthesis');
                """
            )

        result = self.module().build_reel(
            self.root,
            self.work,
            self.out,
            self.evidence,
            timing_db=self.timing_db,
        )

        self.assertEqual(
            ["narrationDatabaseWord", "narrationDatabaseWord"],
            [clip["timingSource"] for clip in result["clips"]],
        )
        self.assertRegex(result["timingSnapshotSHA256"], r"^[0-9a-f]{64}$")

    def test_infers_missing_term_range_from_timed_source_neighbors(self) -> None:
        (self.research / "pronunciation-plan.json").write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "terms": [
                        {
                            "term": "J-space",
                            "variants": [],
                            "expectedChapters": ["ch01.md"],
                            "required": True,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (self.chapters / "ch01.md").write_text(
            "# Chapter One\n\nSo the first step toward J-space is not a verdict.\n",
            encoding="utf-8",
        )
        self.write_anchor(
            words=[
                {"word": "step", "start": 0.4, "end": 0.7},
                {"word": "toward", "start": 0.75, "end": 1.1},
                {"word": "is", "start": 1.8, "end": 1.95},
                {"word": "not", "start": 2.0, "end": 2.2},
            ]
        )

        result = self.module().build_reel(self.root, self.work, self.out, self.evidence)

        clip = result["clips"][0]
        self.assertEqual("sourceNeighborInference", clip["timingSource"])
        self.assertEqual("adjacentSourceNeighbors", clip["timingPrecision"])
        self.assertEqual(["step", "toward"], clip["leftContextWords"])
        self.assertEqual(["is", "not"], clip["rightContextWords"])
        self.assertEqual(0.0, clip["sourceStart"])
        self.assertEqual(3.05, clip["sourceEnd"])

    def test_infers_whole_unaligned_source_span_from_timed_brackets(self) -> None:
        (self.research / "pronunciation-plan.json").write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "terms": [
                        {
                            "term": "J-space",
                            "variants": [],
                            "expectedChapters": ["ch01.md"],
                            "required": True,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (self.chapters / "ch01.md").write_text(
            "# Chapter One\n\n"
            "Settle the result in advance. "
            "So the first step toward J-space is not a new theory. "
            "Parameters are the slow residue.\n",
            encoding="utf-8",
        )
        self.write_anchor(
            words=[
                {"word": "advance", "start": 0.4, "end": 0.9},
                {"word": "Parameters", "start": 3.1, "end": 3.6},
            ]
        )

        result = self.module().build_reel(self.root, self.work, self.out, self.evidence)

        clip = result["clips"][0]
        self.assertEqual("sourceSpanInference", clip["timingSource"])
        self.assertEqual("unalignedSourceSpan", clip["timingPrecision"])
        self.assertEqual(["advance"], clip["leftContextWords"])
        self.assertEqual(["parameters"], clip["rightContextWords"])
        self.assertEqual(11, clip["unalignedSourceWordCount"])
        self.assertEqual(0.0, clip["sourceStart"])
        self.assertEqual(4.0, clip["sourceEnd"])

    def test_builds_one_clip_for_multi_word_form_from_adjacent_timings(self) -> None:
        (self.research / "pronunciation-plan.json").write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "terms": [
                        {
                            "term": "Messages API",
                            "variants": [],
                            "required": True,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        self.write_anchor(
            words=[
                {"word": "Messages", "start": 0.75, "end": 1.25},
                {"word": "API", "start": 1.4, "end": 1.9},
            ]
        )

        result = self.module().build_reel(self.root, self.work, self.out, self.evidence)

        self.assertEqual(1, len(result["clips"]))
        self.assertEqual("Messages API", result["clips"][0]["variantHeard"])
        self.assertEqual(0.0, result["clips"][0]["sourceStart"])
        self.assertEqual(3.15, result["clips"][0]["sourceEnd"])

    def test_rejects_invalid_word_range(self) -> None:
        self.write_anchor(
            words=[
                {"word": "hyperparameter", "start": 1.25, "end": 0.75},
                {"word": "hyperparameters", "start": 2.25, "end": 2.9},
            ]
        )
        with self.assertRaisesRegex(ValueError, "word timing"):
            self.module().build_reel(self.root, self.work, self.out, self.evidence)


if __name__ == "__main__":
    unittest.main()
