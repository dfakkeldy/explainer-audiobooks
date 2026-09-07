from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / 'skills/echo-narration/scripts/echo_epub_metadata.py'


class EPUBAuthorTests(unittest.TestCase):
    def run_metadata(self, metadata):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'book.epub'
            with zipfile.ZipFile(path, 'w') as archive:
                archive.writestr('META-INF/container.xml', '<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="nested/book.opf" media-type="application/oebps-package+xml"/></rootfiles></container>')
                archive.writestr('nested/book.opf', '<package xmlns="http://www.idpf.org/2007/opf"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/">' + metadata + '</metadata></package>')
            return subprocess.run([sys.executable, str(HELPER), str(path)], capture_output=True, text=True)

    def test_uses_source_creator_not_operator(self):
        result = self.run_metadata('<dc:creator>William Shakespeare</dc:creator>')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, 'William Shakespeare\n')

    def test_multiple_creators_preserve_order_and_decode_xml(self):
        result = self.run_metadata('<dc:creator>A &amp; B</dc:creator><dc:creator>Zoë</dc:creator>')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, 'A & B; Zoë\n')

    def test_missing_creator_fails_without_guessing(self):
        result = self.run_metadata('<dc:title>A book</dc:title>')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('creator', result.stderr)
        self.assertEqual(result.stdout, '')

    def test_shell_metacharacters_are_literal_metadata(self):
        result = self.run_metadata('<dc:creator>Writer $(touch SHOULD_NOT_EXIST) `literal`</dc:creator>')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, 'Writer $(touch SHOULD_NOT_EXIST) `literal`\n')

    def test_wrapper_passes_source_author_as_one_argument(self):
        wrapper = (HELPER.parent / 'echo_pronunciation_narrate.sh').read_text()
        self.assertIn('echo_epub_metadata.py" "$EPUB"', wrapper)
        self.assertIn('--author "$SOURCE_AUTHOR"', wrapper)
        self.assertNotIn('--author "Dan Fakkeldy"', wrapper)
