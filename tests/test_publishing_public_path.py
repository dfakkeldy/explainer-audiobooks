from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).parents[1]
sys.path.insert(0, str(REPO / "skill" / "scripts"))

import sync_selected_cover
from tests.test_sync_selected_cover import PAIRED_NAMES, write_paired_package


class PublishingPublicPathTests(unittest.TestCase):
    def test_documented_pair_directory_executes_as_public_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            _selected, artifacts, epub, m4b = write_paired_package(root)
            pair = artifacts["cover.png"].parent
            destination = root / "public-destination"

            self.assertEqual(pair / "cover-selection.json", artifacts["cover-selection.json"])
            self.assertEqual(
                set(PAIRED_NAMES),
                {path.name for path in artifacts.values()},
            )

            with mock.patch.object(sync_selected_cover, "verify_package"):
                result = sync_selected_cover.sync_selected_cover(
                    pair / "cover-selection.json",
                    pair / "cover.png",
                    epub,
                    m4b,
                    destination,
                    intent="reuse",
                    apply=False,
                    public_destination=True,
                    artifact_map={
                        name: pair / name
                        for name in sync_selected_cover.PAIRED_ARTIFACT_NAMES
                    },
                )

            self.assertEqual("new", result.decision)
            self.assertFalse(result.applied)
            self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
