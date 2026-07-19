from __future__ import annotations

import io
import sys
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "skill" / "scripts"))
import build_book


class NonNarratedAppendixTests(unittest.TestCase):
    def test_appendix_is_readable_but_outside_narration_spine_and_word_total(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            chapters = root / "chapters"
            out = root / "dist"
            chapters.mkdir()
            (chapters / "ch01.md").write_text(
                "# One\n\nThese four words are narrated.\n", encoding="utf-8"
            )
            appendix = root / "sources.md"
            appendix.write_text(
                "# Sources\n\nThese appendix words are never narrated.\n", encoding="utf-8"
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                build_book.build(
                    chapters,
                    out,
                    "Fixture",
                    "Dan",
                    "",
                    "fixture-book",
                    non_narrated_appendix=appendix,
                )

            self.assertIn("Chapters: 1", stdout.getvalue())
            self.assertIn("TOTAL WORDS: 5", stdout.getvalue())
            combined = (out / "fixture-book.md").read_text(encoding="utf-8")
            self.assertIn("## Sources", combined)
            self.assertIn("These appendix words are never narrated.", combined)

            with zipfile.ZipFile(out / "fixture-book.epub") as archive:
                opf = archive.read("OEBPS/content.opf").decode("utf-8")
                nav = archive.read("OEBPS/nav.xhtml").decode("utf-8")
                ncx = archive.read("OEBPS/toc.ncx").decode("utf-8")
                appendix_doc = archive.read("OEBPS/appendix.xhtml").decode("utf-8")

            self.assertIn('<item id="appendix" href="appendix.xhtml"', opf)
            self.assertNotIn('<itemref idref="appendix"', opf)
            self.assertIn('<a href="appendix.xhtml">Sources</a>', nav)
            self.assertIn('<content src="appendix.xhtml"/>', ncx)
            self.assertIn('epub:type="bibliography"', appendix_doc)


if __name__ == "__main__":
    unittest.main()
