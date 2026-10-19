from pathlib import Path
import json
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / 'skills/echo-narration/scripts/epub_pronunciation.py'

CONTAINER = ('<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">'
             '<rootfiles><rootfile full-path="OEBPS/content.opf" '
             'media-type="application/oebps-package+xml"/></rootfiles></container>')


def chapter(title, body, declare=True):
    ssml = ' xmlns:ssml="http://www.w3.org/2001/10/synthesis" ssml:alphabet="ipa"' if declare and 'ssml:ph' in body else ''
    return ('<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n'
            f'<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops"{ssml} lang="en">\n'
            f'<head><meta charset="utf-8"/><title>{title}</title></head>\n'
            f'<body><section epub:type="chapter"><h1>{title}</h1>\n{body}\n</section></body></html>\n')


def write_epub(path, chapters, appendix=None, declare=True):
    """A build_book-shaped EPUB: nav, linear chapters, optional linear="no" appendix."""
    items, refs = [], []
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(zipfile.ZipInfo('mimetype'), 'application/epub+zip',
                         compress_type=zipfile.ZIP_STORED)
        archive.writestr('META-INF/container.xml', CONTAINER)
        archive.writestr('OEBPS/nav.xhtml', chapter('Contents', '<nav epub:type="toc"><p>Read me</p></nav>'))
        items.append('<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>')
        for index, body in enumerate(chapters):
            name = f'chap{index:02d}.xhtml'
            archive.writestr(f'OEBPS/{name}', chapter(f'Chapter {index + 1}', body, declare))
            items.append(f'<item id="c{index}" href="{name}" media-type="application/xhtml+xml"/>')
            refs.append(f'<itemref idref="c{index}"/>')
        if appendix is not None:
            archive.writestr('OEBPS/appendix.xhtml', chapter('Appendix', appendix))
            items.append('<item id="appendix" href="appendix.xhtml" media-type="application/xhtml+xml"/>')
            refs.append('<itemref idref="appendix" linear="no"/>')
        archive.writestr('OEBPS/content.opf', (
            '<?xml version="1.0"?>\n<package xmlns="http://www.idpf.org/2007/opf" version="3.0">\n'
            '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>Fixture</dc:title></metadata>\n'
            '<manifest>\n' + '\n'.join(items) + '\n</manifest>\n'
            '<spine>' + ''.join(refs) + '</spine>\n</package>\n'))


def visible(epub, name):
    source = zipfile.ZipFile(epub).read(name).decode('utf-8').split('<body', 1)[1]
    return re.sub(r'<[^>]+>', '', source)


class EPUBPronunciationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def run_tool(self, *args):
        return subprocess.run([sys.executable, str(TOOL), *map(str, args)], capture_output=True, text=True)

    def book(self, chapters, appendix=None, name='book.epub', declare=True):
        path = self.dir / name
        write_epub(path, chapters, appendix, declare)
        return path

    def apply(self, epub, decisions, out='out.epub'):
        path = self.dir / 'decisions.json'
        path.write_text(json.dumps(decisions, ensure_ascii=False), encoding='utf-8')
        return self.run_tool('apply', '--epub', epub, '--decisions', path, '--out', self.dir / out), self.dir / out

    def test_check_refuses_narrated_text_without_ipa(self):
        epub = self.book(['<p>Plain words only, nothing ambiguous.</p>'])
        result = self.run_tool('check', '--epub', epub)
        self.assertEqual(result.returncode, 1)
        self.assertIn('no IPA pronunciations are embedded', result.stderr)

    def test_check_requires_every_content_record_read(self):
        epub = self.book(['<p>I have <span ssml:ph="ɹɛd">read</span> the record.</p>'], declare=False)
        result = self.run_tool('check', '--epub', epub)
        self.assertEqual(result.returncode, 1)
        self.assertIn("'record' has no IPA reading", result.stderr)
        self.assertIn('declare', result.stderr)  # spans without the ssml namespace on the root

    def test_apply_embeds_context_occurrences_and_passes_check(self):
        epub = self.book(['<p>I will read it tomorrow. I have read it already.</p>\n'
                          '<p>The <em>record</em> shows we record everything.</p>'])
        result, out = self.apply(epub, {'occurrences': [
            {'word': 'read', 'ipa': 'ɹid', 'context': 'I will read it tomorrow'},
            {'word': 'read', 'ipa': 'ɹɛd', 'context': 'I have read it already'},
            {'word': 'record', 'ipa': 'ˈɹɛkɚd', 'context': 'The record shows'},
            {'word': 'record', 'ipa': 'ɹɪˈkɔɹd', 'context': 'we record everything'},
        ]})
        self.assertEqual(result.returncode, 0, result.stderr)
        source = zipfile.ZipFile(out).read('OEBPS/chap00.xhtml').decode('utf-8')
        self.assertIn('I will <span ssml:ph="ɹid">read</span> it', source)
        self.assertIn('I have <span ssml:ph="ɹɛd">read</span> it', source)
        self.assertIn('<em><span ssml:ph="ˈɹɛkɚd">record</span></em>', source)
        self.assertIn('xmlns:ssml="http://www.w3.org/2001/10/synthesis"', source)
        self.assertIn('ssml:alphabet="ipa"', source)
        self.assertEqual(visible(epub, 'OEBPS/chap00.xhtml'), visible(out, 'OEBPS/chap00.xhtml'))
        first = zipfile.ZipFile(out).infolist()[0]
        self.assertEqual((first.filename, first.compress_type), ('mimetype', zipfile.ZIP_STORED))
        self.assertEqual(self.run_tool('check', '--epub', out).returncode, 0)

    def test_apply_fails_on_missing_or_ambiguous_context_and_writes_nothing(self):
        epub = self.book(['<p>We read. We read.</p>'])
        result, out = self.apply(epub, {'occurrences': [
            {'word': 'read', 'ipa': 'ɹid', 'context': 'We read'},
            {'word': 'read', 'ipa': 'ɹid', 'context': 'They read'},
        ]})
        self.assertEqual(result.returncode, 65)
        self.assertIn('appears 2 times', result.stderr)
        self.assertIn('context not found', result.stderr)
        self.assertFalse(out.exists())

    def test_context_edge_does_not_match_inside_a_longer_word(self):
        epub = self.book(['<p>She reads the content daily.</p>'])
        result, _ = self.apply(epub, {'occurrences': [
            {'word': 'read', 'ipa': 'ɹid', 'context': 'She read'},
        ]})
        self.assertEqual(result.returncode, 65)
        self.assertIn('appears 0 times', result.stderr)

    def test_annotated_block_needs_readings_for_numbers_and_file_names(self):
        epub = self.book(['<p>Model 299 is on record in REQUESTS.md today.</p>'])
        occurrence = {'word': 'record', 'ipa': 'ˈɹɛkɚd', 'context': 'on record in'}
        result, _ = self.apply(epub, {'occurrences': [occurrence]})
        self.assertEqual(result.returncode, 1)
        self.assertIn("'299' sits in an annotated block", result.stderr)
        self.assertIn("'REQUESTS.md' sits in an annotated block", result.stderr)
        result, out = self.apply(epub, {'occurrences': [occurrence], 'readings': [
            {'text': '299', 'ipa': 'tu ˈnaɪnti ˈnaɪn'},
            {'text': 'REQUESTS.md', 'ipa': 'ɹɪˈkwɛsts dɑt ɛm ˈdi'},
        ]})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('<span ssml:ph="tu ˈnaɪnti ˈnaɪn">299</span>',
                      zipfile.ZipFile(out).read('OEBPS/chap00.xhtml').decode('utf-8'))

    def test_readings_with_a_slash_are_refused(self):
        epub = self.book(['<p>It writes tiles/mail.json and keeps a record.</p>'])
        result, _ = self.apply(epub, {
            'occurrences': [{'word': 'record', 'ipa': 'ˈɹɛkɚd', 'context': 'keeps a record'}],
            'readings': [{'text': 'tiles/mail.json', 'ipa': 'taɪlz slæʃ meɪl'}],
        })
        self.assertEqual(result.returncode, 65)
        self.assertIn("can't annotate text containing []()/", result.stderr)

    def test_lexicon_grapheme_inside_a_dotted_token_is_refused(self):
        epub = self.book(['<p>The rulebook is open-loops.md, read daily.</p>'])
        decisions = {'occurrences': [{'word': 'read', 'ipa': 'ɹɛd', 'context': 'md, read daily'}],
                     'readings': [{'text': 'open-loops.md', 'ipa': 'ˈoʊpən lups dɑt ɛm ˈdi'}],
                     'lexicon': [{'graphemes': ['md'], 'ipa': 'ɛm ˈdi'}]}
        result, _ = self.apply(epub, decisions)
        self.assertEqual(result.returncode, 1)
        self.assertIn("grapheme 'md' matches inside a dotted or hyphenated token", result.stderr)

    def test_lexicon_is_written_linked_and_declared(self):
        epub = self.book(['<p>Portia read it.</p>', '<p>Portia again.</p>'])
        result, out = self.apply(epub, {
            'occurrences': [{'word': 'read', 'ipa': 'ɹɛd', 'context': 'Portia read it'}],
            'lexicon': [{'graphemes': ['Portia'], 'ipa': 'ˈpɔɹʃə'}],
        })
        self.assertEqual(result.returncode, 0, result.stderr)
        archive = zipfile.ZipFile(out)
        self.assertIn('<phoneme>ˈpɔɹʃə</phoneme>', archive.read('OEBPS/names.pls').decode('utf-8'))
        self.assertIn('media-type="application/pls+xml"', archive.read('OEBPS/content.opf').decode('utf-8'))
        for name in ('OEBPS/chap00.xhtml', 'OEBPS/chap01.xhtml'):
            self.assertIn('rel="pronunciation"', archive.read(name).decode('utf-8'))

    def test_ambiguous_words_never_go_in_the_lexicon(self):
        epub = self.book(['<p>Content.</p>'])
        result, _ = self.apply(epub, {'lexicon': [{'graphemes': ['content'], 'ipa': 'ˈkɑntɛnt'}]})
        self.assertEqual(result.returncode, 65)
        self.assertIn('reads differently by sense', result.stderr)

    def test_captions_and_alt_text_cannot_hide_a_mandatory_word(self):
        epub = self.book(['<p>I <span ssml:ph="ɹid">read</span> daily.</p>'
                          '<figure><img src="a.png" alt="A record"/><figcaption>Read this</figcaption></figure>'])
        result = self.run_tool('check', '--epub', epub)
        self.assertEqual(result.returncode, 1)
        self.assertIn("'Read' in <figcaption> can't carry IPA", result.stderr)
        self.assertIn("'record' in image alt text", result.stderr)

    def test_non_linear_appendix_and_nav_are_not_narrated(self):
        epub = self.book(['<p>Nothing here needs <span ssml:ph="ɹidɪŋ">reading</span> help.</p>'],
                         appendix='<p>The record and the content stay in print only.</p>')
        result = self.run_tool('check', '--epub', epub)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_epub_without_narrated_documents_passes(self):
        path = self.dir / 'empty.epub'
        with zipfile.ZipFile(path, 'w') as archive:
            archive.writestr('META-INF/container.xml', CONTAINER)
            archive.writestr('OEBPS/content.opf', '<package xmlns="http://www.idpf.org/2007/opf" version="3.0">'
                             '<manifest/></package>')
        self.assertEqual(self.run_tool('check', '--epub', path).returncode, 0)

    def test_unreadable_epub_is_an_input_error(self):
        path = self.dir / 'junk.epub'
        path.write_bytes(b'not a zip')
        self.assertEqual(self.run_tool('check', '--epub', path).returncode, 65)

    def test_bad_ipa_is_refused(self):
        epub = self.book(['<p>I read.</p>'])
        result, _ = self.apply(epub, {'occurrences': [{'word': 'read', 'ipa': '/ɹɛd/', 'context': 'I read'}]})
        self.assertEqual(result.returncode, 65)
        self.assertIn('slash or bracket delimiters', result.stderr)

    def test_scan_lists_candidates_with_context(self):
        epub = self.book(['<p>Read the 43 Folders post and project the content.</p>'])
        result = self.run_tool('scan', '--epub', epub)
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = json.loads(result.stdout)
        kinds = {(row['kind'], row['word']) for row in rows}
        self.assertTrue({('mandatory', 'Read'), ('mandatory', 'content'), ('watch', 'project'),
                         ('token', '43')} <= kinds)
        self.assertIn('content/record/read without IPA: 2', result.stderr)


class NarrationGateTests(unittest.TestCase):
    def test_preflight_runs_the_gate_before_hashing_the_epub(self):
        preflight = (TOOL.parent / 'echo_pronunciation_preflight.sh').read_text(encoding='utf-8')
        gate = preflight.index('epub_pronunciation.py" check --epub "$EPUB"')
        self.assertLess(gate, preflight.index('EPUB_SHA256=$(/usr/bin/shasum'))

    def test_every_book_skill_points_at_the_tool(self):
        for skill in ('skill/SKILL.md', 'skills/fiction-audiobook/SKILL.md',
                      'skills/classic-literature-adaptation/SKILL.md'):
            with self.subTest(skill=skill):
                self.assertIn('epub_pronunciation.py', (ROOT / skill).read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
