from __future__ import annotations

import hashlib
import importlib
import json
import shutil
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
        self.work = self.root / "work"
        self.out = self.root / "dist" / "probe.m4b"
        self.evidence = self.research / "pronunciation-probe-evidence.json"
        self.research.mkdir()
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
