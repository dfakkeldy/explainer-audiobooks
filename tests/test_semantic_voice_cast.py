from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
MODULE_PATH = ROOT / "skill" / "scripts" / "semantic_voice_cast.py"
SEMANTIC_REFERENCE = ROOT / "skill" / "references" / "semantic-voice-casting.md"
ECHO_V2_GOLDEN_INVENTORY = ROOT / "tests" / "fixtures" / "echo-export-blocks-v2-golden.json"
# Contract reviewed from Echo f02c045f: export-blocks v2 emits only blocks,
# source, and version, with source.epub plus source.epubSHA256.  This is
# audiobook-side fixture evidence, not a claim that Echo was built or run here.
ECHO_EXPORT_BLOCKS_V2_CONTRACT_COMMIT = "f02c045f"
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
            "version": 2,
            "source": {"epub": self.epub.name, "epubSHA256": digest(self.epub)},
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

    @staticmethod
    def documented_json_example(text: str, heading: str) -> tuple[str, dict[str, object]]:
        section = text.split(heading, 1)[1]
        body = section.split("```json\n", 1)[1].split("\n```", 1)[0]
        value = json.loads(body)
        assert isinstance(value, dict)
        return body, value

    @staticmethod
    def _write_bound_cast(
        fixture: SemanticCastFixture,
        *,
        roles: list[dict[str, object]] | None = None,
        groups: list[dict[str, object]] | None = None,
        waiver: object = None,
        use_waiver: bool = False,
        plan: dict[str, object] | None = None,
    ) -> None:
        cast = fixture.cast_payload()
        if roles is not None:
            cast["roles"] = roles
        if groups is not None:
            cast["groups"] = groups
        if use_waiver:
            cast["singleVoiceWaiver"] = waiver
        if plan is None:
            cast_roles = cast["roles"]
            cast_groups = cast["groups"]
            assert isinstance(cast_roles, list) and isinstance(cast_groups, list)
            plan = fixture.plan_payload()
            plan["speakers"] = [
                {"id": role["roleID"], "voiceID": role["voiceID"]}
                for role in cast_roles
            ]
            plan["assignments"] = [
                {"speakerID": group["roleID"], "blocks": group["blocks"]}
                for group in cast_groups
            ]
        fixture.write_json(fixture.plan, plan)
        authored = cast["authoredVoicePlan"]
        assert isinstance(authored, dict)
        authored["sha256"] = digest(fixture.plan)
        fixture.write_json(fixture.cast, cast)

    @staticmethod
    def _group(role: str, *blocks: str, number: int = 1) -> dict[str, object]:
        return {"groupID": f"{role}-{number:03d}", "roleID": role, "blocks": list(blocks)}

    def test_valid_cast_binds_epub_inventory_roles_and_plan(self) -> None:
        result = module.validate_cast(
            self.fixture.cast, self.fixture.inventory,
            self.fixture.plan, self.fixture.epub,
        )
        self.assertEqual(self.fixture.plan, result.voice_plan)
        self.assertEqual(20, result.paragraph_block_count)
        self.assertEqual(19, result.guide_block_count)
        self.assertEqual({"memory": 1}, result.role_block_counts)

    def test_validates_synthetic_echo_v2_golden_inventory_with_matching_frozen_epub(self) -> None:
        """Reject a validator regression that accepts v1 or omits the EPUB name."""
        fixture = self.fresh_fixture()
        inventory = json.loads(ECHO_V2_GOLDEN_INVENTORY.read_text(encoding="utf-8"))
        self.assertEqual(["blocks", "source", "version"], list(inventory))
        source = inventory["source"]
        assert isinstance(source, dict)
        self.assertEqual(["epub", "epubSHA256"], list(source))
        self.assertEqual(2, inventory["version"])
        fixture.epub.write_bytes(b"Echo v2 golden fixture EPUB bytes\n")
        self.assertEqual(fixture.epub.name, source["epub"])
        self.assertEqual(digest(fixture.epub), source["epubSHA256"])
        fixture.inventory.write_bytes(ECHO_V2_GOLDEN_INVENTORY.read_bytes())
        fixture.write_plan()
        fixture.write_cast()

        self.validate(fixture)

    def test_documented_cast_examples_are_canonical_and_validate_when_materialized(self) -> None:
        reference = SEMANTIC_REFERENCE.read_text(encoding="utf-8")
        normal_bytes, normal_cast = self.documented_json_example(
            reference, "### Minimal normal cast"
        )
        waiver_bytes, waiver_cast = self.documented_json_example(
            reference, "### Minimal guide-only waiver cast"
        )
        normal_plan_bytes, normal_plan = self.documented_json_example(
            reference, "### Authored Echo voice-plan shapes"
        )
        waiver_section = reference.split("A guide-only waiver has one guide speaker", 1)[1]
        waiver_plan_body = waiver_section.split("```json\n", 1)[1].split("\n```", 1)[0]
        waiver_plan = json.loads(waiver_plan_body)
        assert isinstance(waiver_plan, dict)

        for name, raw, payload in (
            ("normal cast", normal_bytes, normal_cast),
            ("waiver cast", waiver_bytes, waiver_cast),
            ("normal plan", normal_plan_bytes, normal_plan),
            ("waiver plan", waiver_plan_body, waiver_plan),
        ):
            with self.subTest(name=name):
                self.assertEqual(module.canonical_json(payload), (raw + "\n").encode("utf-8"))

        normal_fixture = self.fresh_fixture()
        normal_cast["source"] = normal_fixture.cast_payload()["source"]
        normal_plan["source"] = {"epubSHA256": digest(normal_fixture.epub)}
        normal_fixture.write_json(normal_fixture.plan, normal_plan)
        normal_authored = normal_cast["authoredVoicePlan"]
        assert isinstance(normal_authored, dict)
        normal_authored["fileName"] = normal_fixture.plan.name
        normal_authored["sha256"] = digest(normal_fixture.plan)
        normal_fixture.write_json(normal_fixture.cast, normal_cast)
        self.validate(normal_fixture)

        waiver_fixture = self.fresh_fixture()
        waiver_cast["source"] = waiver_fixture.cast_payload()["source"]
        waiver_plan["source"] = {"epubSHA256": digest(waiver_fixture.epub)}
        waiver_fixture.write_json(waiver_fixture.plan, waiver_plan)
        waiver_authored = waiver_cast["authoredVoicePlan"]
        assert isinstance(waiver_authored, dict)
        waiver_authored["fileName"] = waiver_fixture.plan.name
        waiver_authored["sha256"] = digest(waiver_fixture.plan)
        waiver_fixture.write_json(waiver_fixture.cast, waiver_cast)
        result = self.validate(waiver_fixture)
        self.assertEqual({}, result.role_block_counts)

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

    def test_rejects_v1_or_unbound_echo_inventory_source(self) -> None:
        cases = (
            ("v1", lambda source, inventory: inventory.__setitem__("version", 1), "inventory version"),
            ("null digest", lambda source, inventory: source.__setitem__("epubSHA256", None), "inventory source EPUB hash"),
            ("wrong digest", lambda source, inventory: source.__setitem__("epubSHA256", "f" * 64), "inventory source EPUB hash"),
            ("wrong filename", lambda source, inventory: source.__setitem__("epub", "other.epub"), "inventory source EPUB filename"),
            ("unknown source key", lambda source, inventory: source.__setitem__("extra", True), "inventory source"),
            ("unknown root key", lambda source, inventory: inventory.__setitem__("extra", True), "inventory has unexpected keys"),
            ("path filename", lambda source, inventory: source.__setitem__("epub", "dist/fixture.epub"), "inventory source EPUB filename"),
        )
        for name, mutate, pattern in cases:
            with self.subTest(name=name):
                fixture = self.fresh_fixture()
                inventory = fixture.inventory_payload()
                source = inventory["source"]
                assert isinstance(source, dict)
                mutate(source, inventory)
                fixture.write_json(fixture.inventory, inventory)
                fixture.write_cast()
                with self.assertRaisesRegex(module.SemanticVoiceCastError, pattern):
                    self.validate(fixture)

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

    def test_roles_are_ordered_unique_known_stable_and_used(self) -> None:
        guide = {"roleID": "guide", "voiceID": "am_michael"}
        memory = {"roleID": "memory", "voiceID": "bf_emma"}
        field = {"roleID": "field", "voiceID": "af_heart"}
        invalid = (
            ("missing-memory", [guide], [], "memory"),
            ("wrong-order", [memory, guide], [self._group("memory", "s0-b4")], "order"),
            ("duplicate-role", [guide, memory, memory], [self._group("memory", "s0-b4")], "duplicate role"),
            ("duplicate-voice", [guide, {"roleID": "memory", "voiceID": "am_michael"}], [self._group("memory", "s0-b4")], "duplicate voice"),
            ("unknown-voice", [guide, {"roleID": "memory", "voiceID": "not_a_voice"}], [self._group("memory", "s0-b4")], "unknown Echo voice"),
            ("unused-field", [guide, memory, field], [self._group("memory", "s0-b4")], "field.*group"),
            ("guide-group", [guide, memory], [{"groupID": "memory-001", "roleID": "guide", "blocks": ["s0-b4"]}], "secondary"),
        )
        for name, roles, groups, pattern in invalid:
            with self.subTest(name=name):
                fixture = self.fresh_fixture()
                self._write_bound_cast(fixture, roles=roles, groups=groups)
                with self.assertRaisesRegex(module.SemanticVoiceCastError, pattern):
                    self.validate(fixture)

    def test_cast_groups_match_echo_assignments_exactly(self) -> None:
        for name, mutate in (
            ("speaker order", lambda p: p.__setitem__("speakers", list(reversed(p["speakers"])))),
            ("default speaker", lambda p: p.__setitem__("defaultSpeakerID", "memory")),
            ("speaker voice", lambda p: p["speakers"][1].__setitem__("voiceID", "af_heart")),
            ("assignment order", lambda p: p.__setitem__("assignments", list(reversed(p["assignments"]))),),
            ("speaker ID", lambda p: p["assignments"][0].__setitem__("speakerID", "guide")),
            ("block order", lambda p: p["assignments"][0].__setitem__("blocks", ["s0-b5", "s0-b4"])),
            ("range", lambda p: p["assignments"][0].__setitem__("range", {"start": "s0-b4", "end": "s0-b4"})),
            ("omitted group", lambda p: p.__setitem__("assignments", [])),
            ("unrecorded assignment", lambda p: p.__setitem__("assignments", p["assignments"] + [{"speakerID": "memory", "blocks": ["s0-b5"]}])),
        ):
            with self.subTest(name=name):
                fixture = self.fresh_fixture()
                roles = [
                    {"roleID": "guide", "voiceID": "am_michael"},
                    {"roleID": "memory", "voiceID": "bf_emma"},
                    {"roleID": "field", "voiceID": "af_heart"},
                ]
                groups = [self._group("memory", "s0-b4"), self._group("field", "s0-b7")]
                plan = fixture.plan_payload()
                plan["speakers"] = [{"id": item["roleID"], "voiceID": item["voiceID"]} for item in roles]
                plan["assignments"] = [{"speakerID": group["roleID"], "blocks": group["blocks"]} for group in groups]
                mutate(plan)
                self._write_bound_cast(fixture, roles=roles, groups=groups, plan=plan)
                with self.assertRaises(module.SemanticVoiceCastError):
                    self.validate(fixture)

    def test_accepts_budget_boundaries(self) -> None:
        cases = (
            ("memory 3/20", [
                {"roleID": "guide", "voiceID": "am_michael"},
                {"roleID": "memory", "voiceID": "bf_emma"},
            ], [self._group("memory", "s0-b4", "s0-b5", "s0-b6")], {"memory": 3}),
            ("field plus coach 3/20", [
                {"roleID": "guide", "voiceID": "am_michael"},
                {"roleID": "memory", "voiceID": "bf_emma"},
                {"roleID": "field", "voiceID": "af_heart"},
                {"roleID": "coach", "voiceID": "af_bella"},
            ], [self._group("memory", "s0-b2"), self._group("field", "s0-b5", "s0-b6"), self._group("coach", "s0-b9")], {"memory": 1, "field": 2, "coach": 1}),
            ("all secondary 5/20", [
                {"roleID": "guide", "voiceID": "am_michael"},
                {"roleID": "memory", "voiceID": "bf_emma"},
                {"roleID": "field", "voiceID": "af_heart"},
                {"roleID": "coach", "voiceID": "af_bella"},
            ], [self._group("memory", "s0-b2", "s0-b3"), self._group("field", "s0-b6", "s0-b7"), self._group("coach", "s0-b10")], {"memory": 2, "field": 2, "coach": 1}),
        )
        for name, roles, groups, counts in cases:
            with self.subTest(name=name):
                fixture = self.fresh_fixture()
                self._write_bound_cast(fixture, roles=roles, groups=groups)
                result = self.validate(fixture)
                self.assertEqual(counts, result.role_block_counts)

    def test_rejects_budget_excesses(self) -> None:
        guide = {"roleID": "guide", "voiceID": "am_michael"}
        memory = {"roleID": "memory", "voiceID": "bf_emma"}
        field = {"roleID": "field", "voiceID": "af_heart"}
        coach = {"roleID": "coach", "voiceID": "af_bella"}
        cases = (
            ("memory", [guide, memory], [self._group("memory", "s0-b4", "s0-b5", "s0-b6", "s0-b7")], "memory exceeds"),
            ("field coach", [guide, memory, field, coach], [self._group("memory", "s0-b2"), self._group("field", "s0-b5", "s0-b6"), self._group("coach", "s0-b9", "s0-b10")], "field plus coach exceeds"),
            ("all secondary", [guide, memory, field, coach], [self._group("memory", "s0-b2", "s0-b3", "s0-b4"), self._group("field", "s0-b7", "s0-b8"), self._group("coach", "s0-b11")], "secondary roles exceed"),
        )
        for name, roles, groups, pattern in cases:
            with self.subTest(name=name):
                fixture = self.fresh_fixture()
                self._write_bound_cast(fixture, roles=roles, groups=groups)
                with self.assertRaisesRegex(module.SemanticVoiceCastError, pattern):
                    self.validate(fixture)

    def test_rejects_invalid_semantic_groups_and_inventory(self) -> None:
        for name, alter_inventory, groups, pattern in (
            ("heading", lambda inventory: inventory["blocks"][4].__setitem__("kind", "heading"), [self._group("memory", "s0-b4")], "eligible paragraph"),
            ("image", lambda inventory: self._make_image(inventory, 4), [self._group("memory", "s0-b4")], "eligible paragraph"),
            ("code", lambda inventory: inventory["blocks"][4].__setitem__("kind", "code"), [self._group("memory", "s0-b4")], "eligible paragraph"),
            ("empty paragraph", lambda inventory: inventory["blocks"][4].__setitem__("text", "  "), [self._group("memory", "s0-b4")], "eligible paragraph"),
            ("duplicate block", lambda inventory: None, [self._group("memory", "s0-b4", "s0-b4")], "duplicate"),
            ("more than four", lambda inventory: None, [self._group("memory", "s0-b4", "s0-b5", "s0-b6", "s0-b7", "s0-b8")], "one to four"),
            ("mixed group ID", lambda inventory: None, [{"groupID": "field-001", "roleID": "memory", "blocks": ["s0-b4"]}], "groupID"),
            ("noncontiguous", lambda inventory: None, [self._group("memory", "s0-b4", "s0-b6")], "consecutive"),
            ("zero guide gap", lambda inventory: None, [self._group("memory", "s0-b4"), self._group("field", "s0-b5")], "guide paragraphs"),
            ("one guide gap", lambda inventory: None, [self._group("memory", "s0-b4"), self._group("field", "s0-b6")], "guide paragraphs"),
            ("unsorted", lambda inventory: None, [self._group("memory", "s0-b8"), self._group("field", "s0-b4")], "ordered"),
        ):
            with self.subTest(name=name):
                fixture = self.fresh_fixture()
                inventory = fixture.inventory_payload()
                alter_inventory(inventory)
                fixture.write_json(fixture.inventory, inventory)
                roles = [
                    {"roleID": "guide", "voiceID": "am_michael"},
                    {"roleID": "memory", "voiceID": "bf_emma"},
                ]
                if any(group["roleID"] == "field" for group in groups):
                    roles.append({"roleID": "field", "voiceID": "af_heart"})
                self._write_bound_cast(fixture, roles=roles, groups=groups)
                with self.assertRaisesRegex(module.SemanticVoiceCastError, pattern):
                    self.validate(fixture)

        for name, mutate in (
            ("duplicate ID", lambda inventory: inventory["blocks"][1].__setitem__("id", "s0-b0")),
            ("duplicate sequence", lambda inventory: inventory["blocks"][1].__setitem__("sequenceIndex", 0)),
        ):
            with self.subTest(name=name):
                fixture = self.fresh_fixture()
                inventory = fixture.inventory_payload()
                mutate(inventory)
                fixture.write_json(fixture.inventory, inventory)
                self._write_bound_cast(fixture)
                with self.assertRaisesRegex(module.SemanticVoiceCastError, "duplicate"):
                    self.validate(fixture)

    def test_rejects_unhashable_inventory_kind_in_api_and_cli(self) -> None:
        fixture = self.fresh_fixture()
        inventory = fixture.inventory_payload()
        blocks = inventory["blocks"]
        assert isinstance(blocks, list) and isinstance(blocks[0], dict)
        blocks[0]["kind"] = []
        fixture.write_json(fixture.inventory, inventory)
        self._write_bound_cast(fixture)

        with self.assertRaisesRegex(
            module.SemanticVoiceCastError,
            "inventory block 0 has an invalid kind",
        ):
            self.validate(fixture)

        command = [
            sys.executable, str(MODULE_PATH), "validate-cast",
            "--cast", str(fixture.cast),
            "--inventory", str(fixture.inventory),
            "--voice-plan", str(fixture.plan),
            "--epub", str(fixture.epub),
        ]
        for output_format in ("json", "argv0"):
            with self.subTest(output_format=output_format):
                result = subprocess.run(command + ["--format", output_format], capture_output=True)
                self.assertEqual(65, result.returncode)
                self.assertEqual(b"", result.stdout)
                self.assertEqual(
                    b"semantic voice cast: inventory block 0 has an invalid kind\n",
                    result.stderr,
                )

    def test_cli_rejects_malformed_v2_inventory_shapes_without_handoff(self) -> None:
        """A malformed v2 inventory must never reach either CLI handoff format."""
        cases = (
            ("version", lambda inventory: inventory.__setitem__("version", "2"), "inventory version must be 2"),
            ("source", lambda inventory: inventory.__setitem__("source", []), "inventory source has unexpected keys"),
            ("epub", lambda inventory: inventory["source"].__setitem__("epub", []), "inventory source EPUB filename must be nonempty text"),
            ("epubSHA256", lambda inventory: inventory["source"].__setitem__("epubSHA256", []), "inventory source EPUB hash must be a lowercase SHA-256"),
            ("blocks", lambda inventory: inventory.__setitem__("blocks", {}), "inventory blocks must be an array"),
        )
        for name, mutate, message in cases:
            with self.subTest(name=name):
                fixture = self.fresh_fixture()
                inventory = fixture.inventory_payload()
                mutate(inventory)
                fixture.write_json(fixture.inventory, inventory)
                fixture.write_cast()
                with self.assertRaisesRegex(module.SemanticVoiceCastError, message):
                    self.validate(fixture)

                command = [
                    sys.executable, str(MODULE_PATH), "validate-cast",
                    "--cast", str(fixture.cast),
                    "--inventory", str(fixture.inventory),
                    "--voice-plan", str(fixture.plan),
                    "--epub", str(fixture.epub),
                ]
                for output_format in ("json", "argv0"):
                    with self.subTest(name=name, output_format=output_format):
                        result = subprocess.run(
                            command + ["--format", output_format], capture_output=True
                        )
                        self.assertEqual(65, result.returncode)
                        self.assertEqual(b"", result.stdout)
                        self.assertEqual(
                            f"semantic voice cast: {message}\n".encode("utf-8"),
                            result.stderr,
                        )

    def test_rejects_unhashable_group_role_id_in_api_and_cli(self) -> None:
        fixture = self.fresh_fixture()
        self._write_bound_cast(
            fixture,
            groups=[{"groupID": "memory-001", "roleID": [], "blocks": ["s0-b4"]}],
        )
        with self.assertRaisesRegex(
            module.SemanticVoiceCastError,
            "cast group 0 roleID must be a secondary role",
        ):
            self.validate(fixture)

        command = [
            sys.executable, str(MODULE_PATH), "validate-cast",
            "--cast", str(fixture.cast),
            "--inventory", str(fixture.inventory),
            "--voice-plan", str(fixture.plan),
            "--epub", str(fixture.epub),
        ]
        for output_format in ("json", "argv0"):
            with self.subTest(output_format=output_format):
                result = subprocess.run(command + ["--format", output_format], capture_output=True)
                self.assertEqual(65, result.returncode)
                self.assertEqual(b"", result.stdout)
                self.assertEqual(
                    b"semantic voice cast: cast group 0 roleID must be a secondary role\n",
                    result.stderr,
                )

    def test_filename_runtime_matches_schema_for_control_characters(self) -> None:
        schema = json.loads(
            (ROOT / "skill" / "schemas" / "semantic-voice-cast-v1.schema.json").read_text(
                encoding="utf-8"
            )
        )
        top_level = schema["properties"]
        assert isinstance(top_level, dict)
        source = top_level["source"]
        assert isinstance(source, dict)
        source_properties = source["properties"]
        assert isinstance(source_properties, dict)
        authored_plan = top_level["authoredVoicePlan"]
        assert isinstance(authored_plan, dict)
        authored_properties = authored_plan["properties"]
        assert isinstance(authored_properties, dict)
        definitions = (
            ("epubFileName", source_properties["epubFileName"]),
            ("inventoryFileName", source_properties["inventoryFileName"]),
            ("authoredVoicePlan.fileName", authored_properties["fileName"]),
        )
        for key, definition in definitions:
            assert isinstance(definition, dict)
            pattern = definition["pattern"]
            assert isinstance(pattern, str)
            for value in ("line\nbreak.epub", "line\rbreak.epub"):
                with self.subTest(key=key, value=repr(value)):
                    self.assertIsNone(re.fullmatch(pattern, value))
                    with self.assertRaisesRegex(module.SemanticVoiceCastError, "safe filename"):
                        module._require_filename(value, key)

    @staticmethod
    def _make_image(inventory: dict[str, object], index: int) -> None:
        block = inventory["blocks"][index]
        assert isinstance(block, dict)
        block["kind"] = "image"
        block["imagePath"] = "figure.png"

    def test_single_voice_waiver_is_exact_and_fail_closed(self) -> None:
        guide = [{"roleID": "guide", "voiceID": "am_michael"}]
        waiver = {"recordedIn": "source/brief.md", "reason": "Listener explicitly requested one voice."}
        fixture = self.fresh_fixture()
        self._write_bound_cast(fixture, roles=guide, groups=[])
        with self.assertRaisesRegex(module.SemanticVoiceCastError, "waiver"):
            self.validate(fixture)

        fixture = self.fresh_fixture()
        self._write_bound_cast(fixture, roles=guide, groups=[], waiver=waiver, use_waiver=True)
        result = self.validate(fixture)
        self.assertEqual(20, result.guide_block_count)
        self.assertEqual({}, result.role_block_counts)

        invalid = (
            ("memory", [{"roleID": "guide", "voiceID": "am_michael"}, {"roleID": "memory", "voiceID": "bf_emma"}], []),
            ("group", guide, [self._group("memory", "s0-b4")]),
            ("recordedIn", guide, []),
            ("empty reason", guide, []),
            ("extra", guide, []),
        )
        for name, roles, groups in invalid:
            with self.subTest(name=name):
                fixture = self.fresh_fixture()
                altered = copy.deepcopy(waiver)
                if name == "recordedIn":
                    altered["recordedIn"] = "source/other.md"
                elif name == "empty reason":
                    altered["reason"] = ""
                elif name == "extra":
                    altered["extra"] = True
                self._write_bound_cast(fixture, roles=roles, groups=groups, waiver=altered, use_waiver=True)
                with self.assertRaises(module.SemanticVoiceCastError):
                    self.validate(fixture)

    def test_cli_emits_compact_json_and_exact_argv0(self) -> None:
        command = [
            sys.executable, str(MODULE_PATH), "validate-cast",
            "--cast", str(self.fixture.cast),
            "--inventory", str(self.fixture.inventory),
            "--voice-plan", str(self.fixture.plan),
            "--epub", str(self.fixture.epub),
        ]
        expected = json.dumps({
            "guideBlockCount": 19,
            "paragraphBlockCount": 20,
            "roleBlockCounts": {"memory": 1},
            "voicePlan": str(self.fixture.plan),
        }, sort_keys=True, separators=(",", ":")).encode() + b"\n"
        json_run = subprocess.run(command + ["--format", "json"], capture_output=True)
        self.assertEqual(0, json_run.returncode)
        self.assertEqual(expected, json_run.stdout)
        argv_run = subprocess.run(command + ["--format", "argv0"], capture_output=True)
        self.assertEqual(b"--voice-plan\0" + os.fsencode(self.fixture.plan) + b"\0", argv_run.stdout)
        self.assertEqual(b"", argv_run.stderr)

    def test_cli_failure_emits_no_handoff_and_exits_65(self) -> None:
        self.fixture.cast.write_bytes(self.fixture.cast.read_bytes() + b" ")
        command = [
            sys.executable, str(MODULE_PATH), "validate-cast",
            "--cast", str(self.fixture.cast),
            "--inventory", str(self.fixture.inventory),
            "--voice-plan", str(self.fixture.plan),
            "--epub", str(self.fixture.epub),
        ]
        for output_format in ("json", "argv0"):
            with self.subTest(output_format=output_format):
                result = subprocess.run(command + ["--format", output_format], capture_output=True)
                self.assertEqual(65, result.returncode)
                self.assertEqual(b"", result.stdout)
                self.assertRegex(result.stderr.decode(), r"^semantic voice cast: .+\n$")


if __name__ == "__main__":
    unittest.main()
