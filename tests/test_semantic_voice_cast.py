from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
MODULE_PATH = ROOT / "skill" / "scripts" / "semantic_voice_cast.py"
SPEC = importlib.util.spec_from_file_location("semantic_voice_cast_test_module", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {MODULE_PATH}")
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SemanticCastFixture:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.run_root = (self.root / "run").resolve()
        self.narration = self.run_root / "_production" / "narration"
        self.research = self.run_root / "research"
        self.dist = self.run_root / "dist"
        self.cast = self.narration / "semantic-voice-cast.json"
        self.plan = self.narration / "echo-voice-plan.json"
        self.epub = self.dist / "fixture.epub"
        self.inventory = self.research / "echo-block-inventory-fixture.json"
        for directory in (self.narration, self.research, self.dist):
            directory.mkdir(parents=True, exist_ok=True)
        self.epub.write_bytes(b"frozen fixture EPUB")
        self.write_inventory()
        self.write_plan()
        self.write_cast()

    @staticmethod
    def canonical(payload: object) -> bytes:
        return (json.dumps(payload, sort_keys=True, indent=2) + "\n").encode("utf-8")

    def write_json(self, path: Path, payload: object) -> None:
        path.write_bytes(self.canonical(payload))

    def inventory_payload(self) -> dict[str, object]:
        blocks = [
            {
                "id": f"s0-b{index}",
                "kind": "paragraph",
                "text": f"Fixture paragraph {index}.",
                "chapterIndex": 0,
                "sequenceIndex": index,
                "wordCount": 3,
            }
            for index in range(20)
        ]
        return {
            "version": 1,
            "source": {"epubSHA256": digest(self.epub)},
            "blocks": blocks,
        }

    def plan_payload(self) -> dict[str, object]:
        return {
            "schemaVersion": 1,
            "source": {"epubSHA256": digest(self.epub)},
            "defaultSpeakerID": "guide",
            "speakers": [
                {"id": "guide", "voiceID": "am_michael"},
                {"id": "memory", "voiceID": "bf_emma"},
            ],
            "assignments": [{"speakerID": "memory", "blocks": ["s0-b4"]}],
        }

    def cast_payload(self) -> dict[str, object]:
        return {
            "schemaVersion": 1,
            "narrationMode": "semantic-block",
            "source": {
                "epubFileName": self.epub.name,
                "epubSHA256": digest(self.epub),
                "inventoryFileName": self.inventory.name,
                "inventorySHA256": digest(self.inventory),
            },
            "defaultRoleID": "guide",
            "roles": [
                {"roleID": "guide", "voiceID": "am_michael"},
                {"roleID": "memory", "voiceID": "bf_emma"},
            ],
            "groups": [
                {"groupID": "memory-001", "roleID": "memory", "blocks": ["s0-b4"]}
            ],
            "authoredVoicePlan": {"fileName": self.plan.name, "sha256": digest(self.plan)},
            "singleVoiceWaiver": None,
        }

    def write_inventory(self) -> None:
        self.write_json(self.inventory, self.inventory_payload())

    def write_plan(self) -> None:
        self.write_json(self.plan, self.plan_payload())

    def write_cast(self) -> None:
        self.write_json(self.cast, self.cast_payload())


class SemanticVoiceCastTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.fixture = SemanticCastFixture(Path(self.temporary.name))

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def fresh_fixture(self) -> SemanticCastFixture:
        root = Path(self.temporary.name) / self.id().rsplit(".", 1)[-1]
        root.mkdir(exist_ok=True)
        return SemanticCastFixture(root)

    def validate(self, fixture: SemanticCastFixture | None = None) -> object:
        current = fixture or self.fixture
        return module.validate_cast(current.cast, current.inventory, current.plan, current.epub)

    def test_valid_cast_binds_epub_inventory_roles_and_plan(self) -> None:
        result = module.validate_cast(
            self.fixture.cast, self.fixture.inventory,
            self.fixture.plan, self.fixture.epub,
        )
        self.assertEqual(self.fixture.plan, result.voice_plan)
        self.assertEqual(20, result.paragraph_block_count)
        self.assertEqual(19, result.guide_block_count)
        self.assertEqual({"memory": 1}, result.role_block_counts)

    def test_rejects_duplicate_unknown_and_noncanonical_json(self) -> None:
        cases: list[tuple[str, bytes, str]] = []
        duplicate = self.fixture.cast.read_bytes().replace(
            b'{\n', b'{\n  "schemaVersion": 1,\n', 1
        )
        cases.append(("duplicate", duplicate, "duplicate"))
        unknown = copy.deepcopy(self.fixture.cast_payload())
        unknown["extra"] = True
        cases.append(("unknown", self.fixture.canonical(unknown), "unexpected keys"))
        noncanonical = json.dumps(self.fixture.cast_payload(), sort_keys=True).encode("utf-8")
        cases.append(("canonical", noncanonical, "canonical"))

        for name, content, pattern in cases:
            with self.subTest(name=name):
                fixture = self.fresh_fixture()
                fixture.cast.write_bytes(content)
                with self.assertRaisesRegex(module.SemanticVoiceCastError, pattern):
                    self.validate(fixture)

    def test_rejects_stale_or_mismatched_source_bytes(self) -> None:
        for name, mutate, pattern in (
            ("EPUB bytes", lambda f: f.epub.write_bytes(b"changed EPUB"), "EPUB hash"),
            ("inventory bytes", lambda f: f.inventory.write_bytes(f.inventory.read_bytes() + b" "), "inventory hash"),
            ("source EPUB filename", lambda f: self._rewrite_cast(f, "epubFileName", "other.epub"), "EPUB filename"),
            ("inventory filename", lambda f: self._rewrite_cast(f, "inventoryFileName", "other.json"), "inventory filename"),
            ("authored plan bytes", lambda f: f.plan.write_bytes(f.plan.read_bytes() + b" "), "authored voice-plan hash"),
            ("authored plan filename", lambda f: self._rewrite_plan_name(f, "other.json"), "authored voice-plan filename"),
        ):
            with self.subTest(name=name):
                fixture = self.fresh_fixture()
                mutate(fixture)
                with self.assertRaisesRegex(module.SemanticVoiceCastError, pattern):
                    self.validate(fixture)

    def test_rejects_inventory_with_a_stale_epub_digest(self) -> None:
        inventory = self.fixture.inventory_payload()
        source = inventory["source"]
        assert isinstance(source, dict)
        source["epubSHA256"] = "f" * 64
        self.fixture.write_json(self.fixture.inventory, inventory)
        self.fixture.write_cast()

        with self.assertRaisesRegex(module.SemanticVoiceCastError, "inventory source EPUB hash"):
            self.validate()

    @staticmethod
    def _rewrite_cast(fixture: SemanticCastFixture, key: str, value: str) -> None:
        cast = fixture.cast_payload()
        source = cast["source"]
        assert isinstance(source, dict)
        source[key] = value
        fixture.write_json(fixture.cast, cast)

    @staticmethod
    def _rewrite_plan_name(fixture: SemanticCastFixture, value: str) -> None:
        cast = fixture.cast_payload()
        authored = cast["authoredVoicePlan"]
        assert isinstance(authored, dict)
        authored["fileName"] = value
        fixture.write_json(fixture.cast, cast)

    def test_rejects_noncanonical_symlinked_or_nonregular_paths(self) -> None:
        for label, attribute in (
            ("cast", "cast"),
            ("inventory", "inventory"),
            ("voice plan", "plan"),
            ("EPUB", "epub"),
        ):
            for kind in ("relative", "symlink", "missing", "directory"):
                with self.subTest(label=label, kind=kind):
                    fixture = self.fresh_fixture()
                    original = getattr(fixture, attribute)
                    if kind == "relative":
                        replacement = original.relative_to(fixture.root)
                    elif kind == "symlink":
                        replacement = original.with_name(f"linked-{original.name}")
                        replacement.symlink_to(original)
                    elif kind == "missing":
                        replacement = original.with_name(f"missing-{original.name}")
                    else:
                        replacement = original.with_name(f"directory-{original.name}")
                        replacement.mkdir()
                    arguments = [fixture.cast, fixture.inventory, fixture.plan, fixture.epub]
                    arguments[("cast", "inventory", "plan", "epub").index(attribute)] = replacement
                    with self.assertRaises(module.SemanticVoiceCastError):
                        module.validate_cast(*arguments)


if __name__ == "__main__":
    unittest.main()
