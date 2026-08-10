from __future__ import annotations

import unittest
from pathlib import Path


REPO = Path(__file__).parents[1]
AUDIOBOOK = REPO / "skill" / "SKILL.md"
SEMANTIC_REFERENCE = REPO / "skill" / "references" / "semantic-voice-casting.md"
LEARNING = REPO / "skill" / "references" / "learning-design.md"
ROAD_BOOK = REPO / "skill" / "references" / "road-book-mode.md"
NARRATION = REPO / "skill" / "references" / "narration-style.md"
LONGFORM = REPO / "skills" / "longform-book-development" / "SKILL.md"
PACKET = (
    REPO
    / "skills"
    / "longform-book-development"
    / "references"
    / "handoff-packet.md"
)
FICTION = REPO / "skills" / "fiction-audiobook" / "SKILL.md"
README = REPO / "README.md"


class SemanticMultivoiceSkillContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.audiobook = AUDIOBOOK.read_text(encoding="utf-8")
        self.semantic_reference = SEMANTIC_REFERENCE.read_text(encoding="utf-8")
        self.learning = LEARNING.read_text(encoding="utf-8")
        self.road_book = ROAD_BOOK.read_text(encoding="utf-8")
        self.narration = NARRATION.read_text(encoding="utf-8")
        self.longform = LONGFORM.read_text(encoding="utf-8")
        self.packet = PACKET.read_text(encoding="utf-8")
        self.fiction = FICTION.read_text(encoding="utf-8")
        self.readme = README.read_text(encoding="utf-8")
        self.combined = " ".join(
            "\n".join(
                (
                    self.audiobook,
                    self.semantic_reference,
                    self.learning,
                    self.road_book,
                    self.narration,
                    self.longform,
                    self.packet,
                )
            ).split()
        )
        self.normalized_guidance = " ".join(
            "\n".join(
                (self.semantic_reference, self.learning, self.road_book, self.narration)
            ).split()
        )
        self.nonfiction_section = self.audiobook.split("## Produce and deliver", 1)[0]

    def test_nonfiction_uses_stable_semantic_roles_not_chapter_rotation(self) -> None:
        for marker in (
            "`guide`",
            "`memory`",
            "`field`",
            "`coach`",
            "75 percent",
            "15 percent",
            "25 percent",
        ):
            self.assertIn(marker, self.combined)
        self.assertIn("semantic-voice-casting.md", self.audiobook)
        self.assertIn("semantic_voice_cast.py", self.semantic_reference)
        self.assertNotIn(
            "For a mixed-voice book, pass one repeatable mapping",
            self.nonfiction_section,
        )

    def test_memory_voice_follows_teaching_and_uses_complete_paragraphs(self) -> None:
        for marker in (
            "after",
            "already-taught",
            "self-contained paragraph",
            "missed the preceding thirty seconds",
        ):
            self.assertIn(marker, self.normalized_guidance)

    def test_longform_handoff_plans_roles_but_never_guesses_echo_blocks(self) -> None:
        for marker in (
            "Semantic Voice Plan",
            "candidate Echo voices",
            "secondary role",
            "frozen EPUB",
        ):
            self.assertIn(marker, self.packet)
        self.assertIn("does not contain Echo block IDs", self.packet)

    def test_single_voice_requires_an_explicit_listener_waiver(self) -> None:
        self.assertIn("single-voice", self.combined)
        self.assertIn("source/brief.md", self.combined)
        self.assertIn("explicit listener waiver", self.combined)
        self.assertNotIn("silently fall back", self.combined)

    def test_editorial_ledger_uses_the_canonical_book_root_path(self) -> None:
        ledger = "<BOOK_ROOT>/source/narration-role-ledger.md"
        for document in (self.semantic_reference, self.longform, self.packet):
            with self.subTest(document=document):
                self.assertIn(ledger, document)
        self.assertNotIn("semantic-voice-ledger.md", self.combined)

    def test_validator_handoff_requires_canonical_absolute_regular_files(self) -> None:
        for marker in (
            "SEMANTIC_CAST",
            "INVENTORY",
            "VOICE_PLAN",
            "EPUB",
            "absolute canonical regular file paths",
            "relative paths, symlinks, and directories",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.semantic_reference)

    def test_fiction_uses_standard_source_bound_character_level_casting(self) -> None:
        for document in (self.fiction, self.readme):
            for marker in ("character-level", "source-bound", "standard"):
                with self.subTest(document=document, marker=marker):
                    self.assertIn(marker, document)
            self.assertNotIn("chapter-level multi-voice Echo cast", document)


if __name__ == "__main__":
    unittest.main()
