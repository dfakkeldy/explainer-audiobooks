from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "validate_skills.py"
SPEC = importlib.util.spec_from_file_location("validate_skills_under_test", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


class SkillFrontmatterParserTests(unittest.TestCase):
    def test_accepts_quoted_name_and_folded_description(self) -> None:
        metadata = validator.frontmatter(
            "---\n"
            'name: "quoted-skill"\n'
            "description: >-\n"
            "  Use when a valid folded description\n"
            "  spans more than one line.\n"
            "---\n"
        )
        self.assertEqual("quoted-skill", metadata["name"])
        self.assertEqual(
            "Use when a valid folded description spans more than one line.",
            metadata["description"],
        )
        self.assertEqual(
            "owner's-skill",
            validator.frontmatter(
                "---\nname: 'owner''s-skill'\ndescription: text\n---\n"
            )["name"],
        )

    def test_preserves_every_current_skill_frontmatter(self) -> None:
        expected = {
            "skill/SKILL.md": "audiobook",
            "skills/longform-book-development/SKILL.md": "longform-book-development",
            "skills/fiction-book-development/SKILL.md": "fiction-book-development",
            "skills/fiction-audiobook/SKILL.md": "fiction-audiobook",
        }
        for relative, name in expected.items():
            with self.subTest(relative=relative):
                metadata = validator.frontmatter(
                    (ROOT / relative).read_text(encoding="utf-8")
                )
                self.assertEqual(name, metadata["name"])
                self.assertIsInstance(metadata["description"], str)
                self.assertTrue(metadata["description"])

    def test_rejects_duplicate_keys(self) -> None:
        with self.assertRaisesRegex(AssertionError, "duplicate"):
            validator.frontmatter(
                "---\nname: first\nname: second\ndescription: text\n---\n"
            )

    def test_rejects_nested_list_and_non_string_values(self) -> None:
        invalid_documents = (
            "---\nname: skill\ndescription:\n  nested: value\n---\n",
            "---\nname: skill\ndescription:\n  - list item\n---\n",
            "---\nname: skill\ndescription: [list, item]\n---\n",
            "---\nname: skill\ndescription: {nested: value}\n---\n",
            "---\nname: skill\ndescription: true\n---\n",
            "---\nname: skill\ndescription: 42\n---\n",
            "---\nname: skill\ndescription: 0x2a\n---\n",
            "---\nname: skill\ndescription: .inf\n---\n",
            "---\nname: skill\ndescription: null\n---\n",
            "---\nname: skill\ndescription: 2026-08-08T12:34:56Z\n---\n",
            "---\nname: skill\ndescription: # comment-only null\n---\n",
        )
        for document in invalid_documents:
            with self.subTest(document=document), self.assertRaises(AssertionError):
                validator.frontmatter(document)

    def test_rejects_malformed_indentation_and_unterminated_quotes(self) -> None:
        invalid_documents = (
            "---\nname: skill\ndescription: >-\n  first line\n second line\n---\n",
            "---\nname: skill\n  description: text\n---\n",
            '---\nname: "unterminated\ndescription: text\n---\n',
            "---\nname: skill\ndescription: 'unterminated\n---\n",
            "---\nname:\tdescription: text\n---\n",
        )
        for document in invalid_documents:
            with self.subTest(document=document), self.assertRaises(AssertionError):
                validator.frontmatter(document)


class AgentMetadataParserTests(unittest.TestCase):
    def test_accepts_exact_interface_mapping_and_prompt(self) -> None:
        metadata = validator.parse_agent_metadata(
            (ROOT / "skills/fiction-audiobook/agents/openai.yaml").read_text(
                encoding="utf-8"
            ),
            "fiction-audiobook",
        )
        self.assertEqual(
            {
                "display_name": "Fiction Audiobook",
                "short_description": "Turn one premise into an Echo-ready fiction book",
                "default_prompt": (
                    "Use $fiction-audiobook to turn my premise into a complete "
                    "narrated fiction package."
                ),
            },
            metadata,
        )

    def test_rejects_wrong_shape_duplicates_and_non_string_prompt(self) -> None:
        invalid_documents = (
            "interface:\n  display_name: Name\n  short_description: Short\n",
            (
                "interface:\n  display_name: Name\n  display_name: Again\n"
                "  short_description: Short\n  default_prompt: Use $fiction-audiobook.\n"
            ),
            (
                "interface:\n  display_name: Name\n  short_description: Short\n"
                "  default_prompt: [Use, $fiction-audiobook]\n"
            ),
            (
                "interface:\n  display_name: Name\n  short_description: Short\n"
                "  default_prompt: Use another skill.\n  extra: value\n"
            ),
            (
                "interface:\n  display_name: Name\n  short_description: Short\n"
                "  default_prompt: Use $fiction-audiobook-extra.\n"
            ),
        )
        for document in invalid_documents:
            with self.subTest(document=document), self.assertRaises(AssertionError):
                validator.parse_agent_metadata(document, "fiction-audiobook")


if __name__ == "__main__":
    unittest.main()
