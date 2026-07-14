from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
SKILL = ROOT / "skills" / "fiction-book-development"


class FictionBookDevelopmentContractTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (SKILL / relative).read_text(encoding="utf-8")

    def test_skill_is_dedicated_to_fiction_manuscript_work(self) -> None:
        text = self.read("SKILL.md")
        for phrase in (
            "One manuscript owner",
            "Causality over chronology",
            "Style by observable choices",
            "Continuity is active",
            "Revision is staged",
            "Production is opt-in",
            "No production work occurred without explicit authorization",
        ):
            self.assertIn(phrase, text)

    def test_skill_links_every_required_support_file(self) -> None:
        text = self.read("SKILL.md")
        for relative in (
            "references/story-bible-and-continuity.md",
            "references/style-and-scene-craft.md",
            "references/revision-passes.md",
            "templates/fiction-project.md",
        ):
            with self.subTest(relative=relative):
                self.assertTrue((SKILL / relative).is_file())
                self.assertIn(relative, text)

    def test_story_contract_tracks_causal_and_continuity_state(self) -> None:
        text = self.read("references/story-bible-and-continuity.md")
        for phrase in (
            "Character engine",
            "World constraints",
            "Turn architecture",
            "Timeline and location",
            "Knowledge and secrets",
            "Character state",
            "Objects and world state",
            "Promises and payoffs",
            "Research and representation ledger",
            "Chapter handoff",
        ):
            self.assertIn(phrase, text)

    def test_style_reference_uses_observable_controls_and_original_voice(self) -> None:
        text = self.read("references/style-and-scene-craft.md")
        for phrase in (
            "Style control panel",
            "Narrative distance",
            "Sentence movement",
            "Image system",
            "Do not imitate a living author",
            "Prose modes",
            "Scene engine",
            "Read-aloud test",
        ):
            self.assertIn(phrase, text)

    def test_revision_moves_from_structure_to_final_canon(self) -> None:
        text = self.read("references/revision-passes.md")
        expected = [
            "Pass 1: Premise and structure",
            "Pass 2: Character and causality",
            "Pass 3: Scene function",
            "Pass 4: Continuity and world logic",
            "Pass 5: Pacing and tension",
            "Pass 6: POV and dialogue",
            "Pass 7: Prose and image system",
            "Pass 8: Read-aloud and final canon",
        ]
        offsets = [text.index(heading) for heading in expected]
        self.assertEqual(offsets, sorted(offsets))
        self.assertIn("reverse-outline the manuscript actually written", text)
        self.assertIn("Reader feedback triage", text)

    def test_project_template_tracks_research_risk_and_reader_effects(self) -> None:
        text = self.read("templates/fiction-project.md")
        self.assertIn("Research and Representation Ledger", text)
        self.assertIn("Targeted reader / expert needed", text)
        self.assertIn("Reader Feedback", text)
        self.assertIn("Observed effect", text)

    def test_nonfiction_longform_routes_fiction_to_dedicated_skill(self) -> None:
        text = (ROOT / "skills" / "longform-book-development" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("route fiction to", text)
        self.assertIn("`fiction-book-development`", text)


if __name__ == "__main__":
    unittest.main()
