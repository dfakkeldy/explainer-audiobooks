from pathlib import Path
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / 'skills/echo-narration/scripts/epub_pronunciation.py'
SPEC = importlib.util.spec_from_file_location('epub_pronunciation_under_test', TOOL)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

# A stand-in for the renderer's misaki lexicon: every word the fixtures speak.
FIXTURE_WORDS = '''
a about after again agreed already ambiguous and at authors book can chapter close
daily deal does everything fell five gap have help here how i in is it keep label
met model needs nothing of on only percentage plain points ray read reading
record reports rose see shirt shows that the they this today tomorrow twelve use
we well who will with words based china level work walked gray saw plane
'''.split()
RENDERER_ENV = ('ECHO_RESOURCE_DIR', 'APPROVED_ECHO_PRONUNCIATION_SHA', 'ECHO_RENDERER_ROOT')


def write_lexicon(directory, gold, silver=('silverword',)):
    directory.mkdir(parents=True, exist_ok=True)
    (directory / 'us_gold.json').write_text(json.dumps({w: 'x' for w in gold}), encoding='utf-8')
    (directory / 'us_silver.json').write_text(json.dumps({w: 'x' for w in silver}), encoding='utf-8')
    return directory

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
        self.dir = Path(self.tmp.name).resolve()
        self.addCleanup(self.tmp.cleanup)
        self.lexicon = write_lexicon(self.dir / 'lexicon', FIXTURE_WORDS)

    def run_tool(self, *args, lexicon=True, env=None):
        """Run the tool hermetically; `check` reads the fixture lexicon unless told not to."""
        args = [str(a) for a in args]
        if lexicon and args[0] == 'check' and '--lexicon-dir' not in args:
            args += ['--lexicon-dir', str(self.lexicon)]
        environment = {k: v for k, v in os.environ.items() if k not in RENDERER_ENV}
        environment.update(env or {})
        return subprocess.run([sys.executable, str(TOOL), *args], capture_output=True, text=True,
                              env=environment)

    def book(self, chapters, appendix=None, name='book.epub', declare=True):
        path = self.dir / name
        write_epub(path, chapters, appendix, declare)
        return path

    def apply(self, epub, decisions, out='out.epub', *extra):
        path = self.dir / 'decisions.json'
        path.write_text(json.dumps(decisions, ensure_ascii=False), encoding='utf-8')
        return (self.run_tool('apply', '--epub', epub, '--decisions', path, '--out', self.dir / out, *extra),
                self.dir / out)

    def test_shared_defaults_allow_occurrence_override_and_keep_token_edges(self):
        epub = self.book(['<p>GitHub Githubish email misread.</p>'])
        result, first = self.apply(epub, {}, 'first.epub')
        self.assertEqual(result.returncode, 0, result.stderr)
        result, second = self.apply(first, {'occurrences': [
            {'word': 'misread', 'ipa': 'mɪsˈɹiːd', 'context': 'email misread'}
        ]}, 'second.epub')
        self.assertEqual(result.returncode, 0, result.stderr)
        with zipfile.ZipFile(second) as archive:
            source = archive.read('OEBPS/chap00.xhtml').decode()
        self.assertIn('<span ssml:ph="mɪsˈɹiːd">misread</span>', source)
        self.assertIn('>GitHub</span> Githubish', source)
        self.assertEqual(source.count('>GitHub</span>'), 1)
        self.assertEqual(visible(first, 'OEBPS/chap00.xhtml'), visible(second, 'OEBPS/chap00.xhtml'))

    def test_book_reading_overrides_shared_default(self):
        epub = self.book(['<p>GitHub email.</p>'])
        result, out = self.apply(epub, {'readings': [
            {'text': 'GitHub', 'ipa': 'ɡɪt hʌb'}]})
        self.assertEqual(result.returncode, 0, result.stderr)
        with zipfile.ZipFile(out) as archive:
            self.assertIn('<span ssml:ph="ɡɪt hʌb">GitHub</span>',
                          archive.read('OEBPS/chap00.xhtml').decode())

    def test_book_lexicon_overrides_shared_default(self):
        epub = self.book(['<p>GitHub email.</p>'])
        result, out = self.apply(epub, {'lexicon': [
            {'graphemes': ['GitHub'], 'ipa': 'ɡɪt hʌb'}]})
        self.assertEqual(result.returncode, 0, result.stderr)
        with zipfile.ZipFile(out) as archive:
            source = archive.read('OEBPS/chap00.xhtml').decode()
            self.assertNotIn('>GitHub</span>', source)
            self.assertIn('ɡɪt hʌb', archive.read('OEBPS/names.pls').decode())

    def test_exact_ipa_serialization_preserves_surrounding_text(self):
        body = '<p>“Before,” Portia said: GitHub, then assignee.</p>'
        epub = self.book([body])
        result, out = self.apply(epub, {
            'occurrences': [
                {'word': 'GitHub', 'ipa': 'ˈɡɪtˌhʌb', 'context': 'said: GitHub, then'},
                {'word': 'assignee', 'ipa': 'əˌsaɪˈniː', 'context': 'then assignee'}],
            'lexicon': [{'graphemes': ['Portia'], 'ipa': 'ˈpɔɹʃə'}]})
        self.assertEqual(result.returncode, 0, result.stderr)
        with zipfile.ZipFile(out) as archive:
            source = archive.read('OEBPS/chap00.xhtml').decode()
            paragraph = re.search(r'<p>.*?</p>', source).group()
            self.assertEqual(paragraph,
                '<p>“Before,” Portia said: <span ssml:ph="ˈɡɪtˌhʌb">GitHub</span>, '
                'then <span ssml:ph="əˌsaɪˈniː">assignee</span>.</p>')
            self.assertEqual(archive.read('OEBPS/names.pls').decode(),
                '<?xml version="1.0" encoding="utf-8"?>\n'
                '<lexicon xmlns="http://www.w3.org/2005/01/pronunciation-lexicon" '
                'version="1.0" alphabet="ipa" xml:lang="en-US">\n'
                '  <lexeme>\n    <grapheme>Portia</grapheme>\n'
                '    <phoneme>ˈpɔɹʃə</phoneme>\n  </lexeme>\n</lexicon>\n')
        self.assertEqual(visible(epub, 'OEBPS/chap00.xhtml'), visible(out, 'OEBPS/chap00.xhtml'))

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
        epub = self.book(['<p>Read the 43 Folders post and project the content. What does A-I do?</p>'])
        result = self.run_tool('scan', '--epub', epub)
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = json.loads(result.stdout)
        kinds = {(row['kind'], row['word']) for row in rows}
        self.assertTrue({('mandatory', 'Read'), ('mandatory', 'content'), ('mandatory', 'project'),
                         ('watch', 'does'), ('token', '43'), ('hyphen-initialism', 'A-I')} <= kinds)
        self.assertIn('heteronyms without IPA: 3', result.stderr)
        self.assertIn('pass --lexicon-dir', result.stderr)

    def test_scan_lists_words_echo_would_guess_with_a_lexicon(self):
        epub = self.book(['<p>The labeller met Ryan.</p>'])
        result = self.run_tool('scan', '--epub', epub, '--lexicon-dir', self.lexicon)
        self.assertEqual(result.returncode, 0, result.stderr)
        guessed = {row['word'] for row in json.loads(result.stdout) if row['kind'] == 'fallback'}
        self.assertEqual(guessed, {'labeller', 'Ryan'})

    # Pre-render gate: hyphen-spelled initialisms (A-I is read "uh-EYE").

    def test_hyphen_spelled_initialisms_fail_with_count_and_closed_form(self):
        epub = self.book(['<p>We <span ssml:ph="ɹɛd">read</span> about A-I today.</p>'
                          '<p>The A-I gap and the A-P-Is rose with G-D-P.</p>'])
        result = self.run_tool('check', '--epub', epub)
        self.assertEqual(result.returncode, 1)
        self.assertIn("'A-I' x2 spells an initialism with hyphens", result.stderr)
        self.assertIn('write the closed form (AI)', result.stderr)
        self.assertIn("'A-P-Is' x1", result.stderr)
        self.assertIn("'G-D-P' x1", result.stderr)
        self.assertIn('read about [[A-I]] today', result.stderr)
        self.assertEqual(result.stderr.count("'A-I' x2"), 1)

    def test_closed_initialisms_and_ordinary_hyphenated_words_pass(self):
        epub = self.book(['<p>We <span ssml:ph="ɹɛd">read</span> about AI and APIs and GDP today.</p>'
                          '<p>The X-Ray and T-shirt and <span ssml:ph="ˌeɪˈaɪ">A-I</span> rose.</p>'])
        result = self.run_tool('check', '--epub', epub)
        self.assertEqual(result.returncode, 0, result.stderr)

    # Pre-render gate: words Echo would guess, tested against the renderer's lexicon.

    def test_words_missing_from_the_renderer_lexicon_fail_once_per_word(self):
        epub = self.book(['<p>The labeller met Ryan. They <span ssml:ph="ɹɛd">read</span> it.</p>',
                          '<p>Ryan and the labellers agreed.</p>'])
        result = self.run_tool('check', '--epub', epub)
        self.assertEqual(result.returncode, 1)
        self.assertIn("chap00.xhtml: 'labeller' x1 isn't in the renderer's lexicon", result.stderr)
        self.assertIn("'Ryan' x2 isn't in the renderer's lexicon", result.stderr)
        self.assertIn("'labellers' x1", result.stderr)
        self.assertIn('The labeller met [[Ryan]] . They', result.stderr)
        self.assertEqual(result.stderr.count("'Ryan' x2"), 1)

    def test_a_lexicon_entry_or_inline_reading_covers_a_missing_word(self):
        epub = self.book(['<p>The labeller met Ryan. Ryan agreed.</p>'])
        result, out = self.apply(epub, {
            'occurrences': [{'word': 'labeller', 'ipa': 'ˈleɪbələɹ', 'context': 'The labeller met'}],
            'lexicon': [{'graphemes': ['Ryan'], 'ipa': 'ˈɹaɪən'}]}, 'out.epub', '--lexicon-dir', self.lexicon)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("word coverage wasn't checked", result.stderr)
        self.assertEqual(self.run_tool('check', '--epub', out).returncode, 0)

    def test_apply_with_a_lexicon_writes_nothing_while_echo_would_guess(self):
        epub = self.book(['<p>The labeller met Ryan.</p>'])
        decisions = {'lexicon': [{'graphemes': ['Ryan'], 'ipa': 'ˈɹaɪən'}]}
        result, out = self.apply(epub, decisions, 'out.epub', '--lexicon-dir', self.lexicon)
        self.assertEqual(result.returncode, 1)
        self.assertIn("'labeller' x1 isn't in the renderer's lexicon", result.stderr)
        self.assertFalse(out.exists())
        result, out = self.apply(epub, decisions, 'plain.epub')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("word coverage wasn't checked", result.stderr)
        self.assertEqual(self.run_tool('check', '--epub', out).returncode, 1)

    def test_misaki_morphology_and_letter_readings_count_as_known(self):
        lexicon = MODULE.RendererLexicon({'label', 'story', 'box', 'teacher', 'open', 'stop', 'make'}, {'zz'})
        for word in ('label', 'Label', 'LABEL', 'labels', 'labeled', 'labeling', 'label’s', 'stories',
                     'boxes', "teacher's", 'stopping', 'making', 'LLM', 'LLMs', 'NASA', 'OpenAI', 'x',
                     'Fakkeldy', 'résumé'):
            with self.subTest(word=word):
                self.assertTrue(lexicon.knows(word))
        for word in ('labeller', 'labellers', 'Ryan', "Ryan's", 'McTavish', 'labelly', 'transformatively',
                     'José'):
            with self.subTest(word=word):
                self.assertFalse(lexicon.knows(word))

    def test_numbers_and_punctuation_are_out_of_scope(self):
        epub = self.book(['<p>We <span ssml:ph="ɹɛd">read</span> it.</p>',
                          '<p>In 1990s and 2nd, 3.5 and 12% at 3pm, 4K, 3D, 10x and COVID-19 rose.</p>'])
        result = self.run_tool('check', '--epub', epub)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_tokens_echo_would_mangle_fail(self):
        epub = self.book(['<p>We <span ssml:ph="ɹɛd">read</span> it.</p>',
                          '<p>See Claude.ai today. The gap fell 5pp and 8.9pp. They keep LLMs.</p>'])
        result = self.run_tool('check', '--epub', epub)
        self.assertEqual(result.returncode, 1)
        self.assertIn("'Claude.ai' x1 has a period inside it", result.stderr)
        self.assertIn("'5pp' x1 joins a number to letters", result.stderr)
        self.assertIn("'8.9pp' x1 joins a number to letters", result.stderr)
        self.assertIn("'LLMs' x1 is followed by a period", result.stderr)
        self.assertIn('LLMiz', result.stderr)

    def test_readings_cover_mangled_tokens_and_spoken_abbreviations_pass(self):
        epub = self.book(['<p>See <span ssml:ph="klɔd dɑt ˌeɪˈaɪ">Claude.ai</span> today.</p>',
                          '<p>The gap rose five percentage points, e.g. in the U.S. with Dr. Who.</p>'])
        result = self.run_tool('check', '--epub', epub)
        self.assertEqual(result.returncode, 0, result.stderr)

    # Echo speaks only "Code listing." for a <pre>, so nothing inside it is narrated.

    def test_code_listings_in_pre_are_not_checked(self):
        epub = self.book(['<p>We <span ssml:ph="ɹɛd">read</span> it.</p>',
                          '<pre><code>read the record; A-I zzqx foo.bar\n'
                          '<span><em>content</em></span> Claude.ai</code></pre>'])
        result = self.run_tool('check', '--epub', epub)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_tool('scan', '--epub', epub)
        self.assertNotIn('"content"', result.stdout)

    def test_inline_code_outside_pre_is_still_checked(self):
        epub = self.book(['<p>We <span ssml:ph="ɹɛd">read</span> it.</p>',
                          '<p>We use <code>record</code> and <code>zzqx</code> daily.</p>'])
        result = self.run_tool('check', '--epub', epub)
        self.assertEqual(result.returncode, 1)
        self.assertIn("'record' in <code> can't carry IPA", result.stderr)
        self.assertIn("'zzqx' x1 isn't in the renderer's lexicon", result.stderr)

    # Dotted forms are tested per hyphen part: U.S.-based is U.S. plus based.

    def test_dotted_initialism_before_a_hyphen_passes(self):
        epub = self.book(['<p>We <span ssml:ph="ɹɛd">read</span> it.</p>',
                          '<p>The U.S.-based and U.S.-China and Ph.D.-level work rose.</p>'
                          '<p>The Claude.ai-based gap rose.</p>'])
        result = self.run_tool('check', '--epub', epub)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr.count('has a period inside it'), 1, result.stderr)
        self.assertIn("'Claude.ai' x1 has a period inside it", result.stderr)

    # Echo expands abbreviations only in blocks without IPA spans, and only as TextNormalizer does.

    def test_expanded_abbreviations_follow_echo_text_expansion(self):
        epub = self.book(['<p>We <span ssml:ph="ɹɛd">read</span> it with Dr. Who.</p>',
                          '<p>We met Dr. Who on Jan. 5, e.g. at work, and saw Ms. Gray.</p>'
                          '<p>We met in Feb. today.</p>'])
        result = self.run_tool('check', '--epub', epub)
        self.assertEqual(result.returncode, 1)
        self.assertIn("'Ms' x1 is a title that Echo's text expansion reads as 'Miz'", result.stderr)
        # No expansion in an annotated block, so the lexicon decides.
        self.assertIn("'Dr' x1 isn't in the renderer's lexicon", result.stderr)
        self.assertIn('read it with [[Dr]] . Who', result.stderr)
        # A month is expanded only before a day or year.
        self.assertIn("'Feb' x1 isn't in the renderer's lexicon", result.stderr)
        self.assertNotIn("'Jan'", result.stderr)
        self.assertNotIn("'e.g'", result.stderr)

    def test_glued_title_rule_skips_annotated_blocks(self):
        epub = self.book(['<p>They <span ssml:ph="ɹɛd">read</span> about LLMs.</p>',
                          '<p>They keep LLMs.</p>'])
        result = self.run_tool('check', '--epub', epub)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr.count('LLMiz'), 1, result.stderr)
        self.assertIn('They keep [[LLMs]]', result.stderr)

    def test_unit_symbols_echo_expands_pass(self):
        epub = self.book(['<p>We <span ssml:ph="ɹɛd">read</span> it.</p>',
                          '<p>We walked 5 km in 2 hrs. The km/h gap and 40km rose.</p>'])
        result = self.run_tool('check', '--epub', epub)
        self.assertEqual(result.returncode, 1)
        self.assertIn("'km' x1 isn't in the renderer's lexicon", result.stderr)
        self.assertIn('The [[km]] /h gap', result.stderr)
        self.assertIn("'40km' x1 joins a number to letters", result.stderr)
        self.assertNotIn("'hrs'", result.stderr)
        epub = self.book(['<p>We <span ssml:ph="ɹɛd">read</span> it in 2 hrs.</p>'], name='annotated.epub')
        result = self.run_tool('check', '--epub', epub)
        self.assertIn("'hrs' x1 isn't in the renderer's lexicon", result.stderr)

    def test_a_pls_match_makes_its_block_annotated(self):
        # Echo stores a linked PLS match as a pronunciation span, so that block skips text
        # expansion exactly like a block with an inline span.
        epub = self.book(['<p>Portia walked 5 km in 2 hrs.</p><p>We walked it in 2 hrs.</p>'])
        lexicon = [{'graphemes': ['Portia'], 'ipa': 'ˈpɔɹʃə'}]
        result, _ = self.apply(epub, {'lexicon': lexicon})
        self.assertEqual(result.returncode, 1)
        self.assertIn("'5' sits in an annotated block", result.stderr)
        self.assertNotIn('We walked it in [[2]]', result.stderr)
        result, out = self.apply(epub, {'lexicon': lexicon, 'occurrences': [
            {'word': '5', 'ipa': 'fˈaɪv', 'context': 'walked 5 km'},
            {'word': '2', 'ipa': 'tˈu', 'context': 'km in 2 hrs'}]})
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_tool('check', '--epub', out)
        self.assertEqual(result.returncode, 1)
        self.assertIn("'hrs' x1 isn't in the renderer's lexicon", result.stderr)
        self.assertIn("'km' x1 isn't in the renderer's lexicon", result.stderr)
        self.assertIn('[[hrs]]', result.stderr)
        self.assertNotIn('We walked it in 2 [[hrs]]', result.stderr)
        self.assertNotIn("'Portia'", result.stderr)

    def test_token_readings_reach_a_block_annotated_only_by_the_pls(self):
        epub = self.book(['<p>Portia walked 5 miles.</p><p>We walked 5 miles too.</p>'])
        readings = [{'text': '5', 'ipa': 'fˈaɪv'}]
        result, out = self.apply(epub, {'lexicon': [{'graphemes': ['Portia'], 'ipa': 'ˈpɔɹʃə'}],
                                        'readings': readings})
        self.assertEqual(result.returncode, 0, result.stderr)
        source = zipfile.ZipFile(out).read('OEBPS/chap00.xhtml').decode('utf-8')
        self.assertIn('Portia walked <span ssml:ph="fˈaɪv">5</span> miles.', source)
        self.assertIn('We walked 5 miles too.', source)
        # A PLS the book already links (no inline spans yet) counts the same way.
        plain = self.book(['<p>Portia walked 5 miles.</p><p>We walked 5 miles too.</p>'], name='plain.epub')
        linked = self.dir / 'linked.epub'
        with zipfile.ZipFile(plain) as source, zipfile.ZipFile(linked, 'w', zipfile.ZIP_DEFLATED) as target:
            for info in source.infolist():
                data = source.read(info.filename).decode('utf-8')
                if info.filename == 'OEBPS/content.opf':
                    data = data.replace('</manifest>', '<item id="pls" href="names.pls" '
                                        'media-type="application/pls+xml"/>\n</manifest>')
                elif info.filename == 'OEBPS/chap00.xhtml':
                    data = data.replace('</title>', '</title><link rel="pronunciation" '
                                        'type="application/pls+xml" href="names.pls"/>')
                target.writestr(info, data)
            target.writestr('OEBPS/names.pls', (
                '<?xml version="1.0" encoding="UTF-8"?>\n<lexicon '
                'xmlns="http://www.w3.org/2005/01/pronunciation-lexicon" version="1.0" alphabet="ipa" '
                'xml:lang="en-US"><lexeme><grapheme>Portia</grapheme><phoneme>ˈpɔɹʃə</phoneme></lexeme>'
                '</lexicon>\n'))
        result, out = self.apply(linked, {'readings': readings}, 'linked-out.epub')
        self.assertEqual(result.returncode, 0, result.stderr)
        source = zipfile.ZipFile(out).read('OEBPS/chap00.xhtml').decode('utf-8')
        self.assertIn('Portia walked <span ssml:ph="fˈaɪv">5</span> miles.', source)
        self.assertIn('We walked 5 miles too.', source)

    def test_two_letter_hyphen_forms_offer_an_inline_reading(self):
        epub = self.book(['<p>We <span ssml:ph="ɹɛd">read</span> the A-Z list on the X-Y plane.</p>'])
        result = self.run_tool('check', '--epub', epub)
        self.assertEqual(result.returncode, 1)
        self.assertIn("'A-Z' x1 spells an initialism with hyphens", result.stderr)
        self.assertIn("'X-Y' x1", result.stderr)
        self.assertIn('keep the hyphen and give each use an inline reading', result.stderr)

    # misaki reads camelCase parts apart (except after Mc), so a whole-word key doesn't help.

    def test_camel_case_words_resolve_part_by_part_like_misaki(self):
        lexicon = MODULE.RendererLexicon({'SaaS', 'VoIP', 'LaTeX', 'arXiv', 'MacGyver', 'OxyContin', 'EpiPen',
                                          'mac', 'pen', 'phone', 'McDonald', 'land', 'model', 'open'}, {'zz'})
        for word in ('SaaS', 'VoIP', 'LaTeX', 'arXiv', 'MacGyver', 'OxyContin', 'EpiPen', 'McDonaldLand',
                     'GPTModel', 'XMLHttpPhone'):
            with self.subTest(word=word):
                self.assertFalse(lexicon.knows(word))
        for word in ('McDonald', 'iPhone', 'IPhone', 'OpenAI', 'MacPen', 'PhoneLand'):
            with self.subTest(word=word):
                self.assertTrue(lexicon.knows(word))
        self.assertEqual(MODULE.misaki_subtokens('XMLHttpPhone'), ['XMLHttp', 'Phone'])
        self.assertEqual(MODULE.misaki_subtokens('IPhone'), ['I', 'Phone'])

    # Pre-render gate: heteronyms, with no exemption for headings, number blocks or compounds.

    def test_heteronyms_need_readings_in_headings_number_blocks_and_compounds(self):
        epub = self.book(['<h2>How we use records</h2>\n'
                          '<p>In 2024 we <span ssml:ph="ɹɛd">read</span> twelve reports.</p>\n'
                          '<p>A well-read gap can close; the API records rose. It does.</p>'])
        result = self.run_tool('check', '--epub', epub)
        self.assertEqual(result.returncode, 1)
        for word in ('use', 'records', 'read', 'close'):
            with self.subTest(word=word):
                self.assertIn(f"'{word}' has no IPA reading", result.stderr)
        self.assertEqual(result.stderr.count("'records' has no IPA reading"), 2)
        self.assertIn('A well- [[read]] gap', result.stderr)
        self.assertIn("'2024' sits in an annotated block", result.stderr)
        self.assertNotIn("'does'", result.stderr)

    def test_heteronyms_never_go_in_the_lexicon(self):
        epub = self.book(['<p>Uses.</p>'])
        result, _ = self.apply(epub, {'lexicon': [{'graphemes': ['uses'], 'ipa': 'ˈjusɪz'}]})
        self.assertEqual(result.returncode, 65)
        self.assertIn('reads differently by sense', result.stderr)

    # Finding the renderer's lexicon: explicit, environment, installed renderer; else fail closed.

    def test_check_fails_closed_without_a_renderer_lexicon(self):
        epub = self.book(['<p>I <span ssml:ph="ɹid">read</span> daily.</p>'])
        result = self.run_tool('check', '--epub', epub, lexicon=False)
        self.assertEqual(result.returncode, 65)
        self.assertIn('--lexicon-dir', result.stderr)
        self.assertIn('APPROVED_ECHO_PRONUNCIATION_SHA', result.stderr)
        empty = self.dir / 'empty'
        empty.mkdir()
        result = self.run_tool('check', '--epub', epub, '--lexicon-dir', empty)
        self.assertEqual(result.returncode, 65)
        self.assertIn('lacks us_gold.json, us_silver.json', result.stderr)

    def test_check_without_narrated_text_needs_no_lexicon(self):
        epub = self.book([], appendix='<p>The record stays in print only.</p>')
        self.assertEqual(self.run_tool('check', '--epub', epub, lexicon=False).returncode, 0)

    def test_check_finds_the_lexicon_of_the_installed_renderer(self):
        sha, manifest = 'a' * 40, 'b' * 64
        root = self.dir / 'Renderers'
        write_lexicon(root / sha / manifest / 'EchoNarrationResources', FIXTURE_WORDS)
        (root / sha / 'approved-renderer.json').write_text(json.dumps(
            {'schemaVersion': 1, 'echoSourceSHA': sha, 'manifestSHA256': manifest}), encoding='utf-8')
        epub = self.book(['<p>I <span ssml:ph="ɹid">read</span> about the labeller daily.</p>'])
        for env in ({'APPROVED_ECHO_PRONUNCIATION_SHA': sha, 'ECHO_RENDERER_ROOT': str(root)},
                    {'ECHO_RESOURCE_DIR': str(self.lexicon)}):
            with self.subTest(env=sorted(env)):
                result = self.run_tool('check', '--epub', epub, lexicon=False, env=env)
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn("'labeller' x1 isn't in the renderer's lexicon", result.stderr)
        result = self.run_tool('check', '--epub', epub, lexicon=False,
                               env={'APPROVED_ECHO_PRONUNCIATION_SHA': 'c' * 40, 'ECHO_RENDERER_ROOT': str(root)})
        self.assertEqual(result.returncode, 65)
        self.assertIn('cannot find installed Echo renderer', result.stderr)


class NarrationGateTests(unittest.TestCase):
    def test_preflight_runs_the_gate_before_hashing_the_epub(self):
        preflight = (TOOL.parent / 'echo_pronunciation_preflight.sh').read_text(encoding='utf-8')
        gate = preflight.index('epub_pronunciation.py" check --epub "$EPUB"')
        self.assertLess(gate, preflight.index('EPUB_SHA256=$(/usr/bin/shasum'))
        # The check reads the attested renderer's own lexicon, never a system word list.
        self.assertIn('--lexicon-dir "$ECHO_RESOURCE_DIR"', preflight[gate:gate + 200])
        self.assertLess(preflight.index('echo_pronunciation_attest_renderer || return'), gate)
        self.assertNotIn('/usr/share/dict', (TOOL.read_text(encoding='utf-8')))

    def test_every_book_skill_points_at_the_tool(self):
        for skill in ('skill/SKILL.md', 'skills/fiction-audiobook/SKILL.md',
                      'skills/classic-literature-adaptation/SKILL.md'):
            with self.subTest(skill=skill):
                self.assertIn('epub_pronunciation.py', (ROOT / skill).read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
