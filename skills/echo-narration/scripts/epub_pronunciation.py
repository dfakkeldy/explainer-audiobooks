#!/usr/bin/env python3
"""Embed and check IPA pronunciations in an EPUB for Echo narration.

  scan   list every pronunciation candidate in the narrated text, with context
  apply  embed authored decisions (inline IPA, token readings, a PLS lexicon)
         into a new EPUB, then run `check` on it
  check  the narration gate: fail when narrated text lacks required IPA,
         would make Echo guess a word, or breaks Echo's epub.*.ipa-v1
         annotation contract

Narrated text is the body of every spine document that isn't `linear="no"` and
isn't the nav document. The rules follow references/epub-pronunciation.md and
the traps found in production:

- A lexicon grapheme matches inside dotted or hyphenated tokens (`md` inside
  `open-loops.md`), and synthesis then fails mid-render.
- An annotated block skips Echo's text expansion, so numerals and file names
  in it need their own readings.
- An inline span whose text contains a slash makes Echo import nothing at all.
- A hyphen-spelled initialism (`A-I`) is read "uh-EYE": the capital A is tagged
  as the article.
- A word missing from the renderer's misaki lexicons (us_gold, us_silver) is
  guessed by letter rules (`labeller`, `Ryan`, `Claude.ai`, `5pp`), and Echo's
  text expansion turns `LLMs.` into "LLMiz".
- A heteronym read by the engine can take the wrong sense (`read` as "reed"
  in the past tense), in headings and number blocks as much as anywhere.

`check` tests words against the lexicon of the renderer that will narrate:
`--lexicon-dir`, else `$ECHO_RESOURCE_DIR`, else the installed renderer named
by `$APPROVED_ECHO_PRONUNCIATION_SHA` (and `$ECHO_RENDERER_ROOT`). It fails
closed when none is found. `apply` and `scan` test words only with an explicit
`--lexicon-dir`.

Decisions file (JSON) for `apply`:

    {
      "lang": "en-US",
      "occurrences": [
        {"word": "read", "ipa": "ɹɛd", "context": "I have read it already",
         "doc": "chap03.xhtml", "nth": 1}
      ],
      "readings": [{"text": "REQUESTS.md", "ipa": "ɹɪˈkwɛsts dɑt ɛm ˈdi"}],
      "lexicon": [{"graphemes": ["Portia", "PORTIA"], "ipa": "ˈpɔɹʃə"}]
    }

An occurrence's context is quoted from the book and must appear exactly once
in narrated text (narrowed by `doc`, the document's file name, when given); the
word must appear once inside it, or `nth` picks one. Readings apply to every
whole-token use of their text inside blocks that carry other annotations
(an inline span, an occurrence, a shared-dictionary word or a linked PLS word).
Exit codes: 0 pass, 1 check failed, 64 usage, 65 unreadable input.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import posixpath
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Mapping

OPF_NS = "http://www.idpf.org/2007/opf"
CONTAINER_NS = "urn:oasis:names:tc:opendocument:xmlns:container"
SSML_NS = "http://www.w3.org/2001/10/synthesis"
PLS_NS = "http://www.w3.org/2005/01/pronunciation-lexicon"
XHTML_TYPES = {"application/xhtml+xml"}

# Each spelling has two pronunciations that depend on sense or tense.
MANDATORY = ("re-read", "reread", "contents", "content", "records", "record", "read")
# Other spellings whose sound depends on meaning.
WATCH = (
    "lead", "leads", "live", "lives", "close", "closes", "minute", "minutes", "wind", "wound",
    "tear", "tears", "present", "presents", "object", "objects", "produce", "project", "projects",
    "use", "uses", "used", "separate", "estimate", "estimates", "update", "updates", "permit",
    "conduct", "contract", "desert", "refuse", "progress", "subject", "perfect", "alternate",
    "duplicate", "row", "rows", "resume", "digest", "deliberate", "graduate", "advocate",
    "associate", "moderate", "appropriate", "learned", "blessed", "aged", "bass", "polish",
    "Polish", "address", "addresses", "invite", "bow", "bows", "does", "dove", "sow",
    "increase", "increases",
)
# The renderer reads these one way and their other sense is rare in modern prose,
# so `scan` lists them but `check` doesn't require a reading. Annotating every
# "does" would switch off text expansion in most blocks for no gain.
SCAN_ONLY = ("does", "row", "rows", "address", "addresses", "polish", "Polish")
# The heteronym family: every occurrence needs an inline reading, in headings,
# number blocks and hyphenated compounds too (`well-read`, `A-P-I records`).
HETERONYMS = MANDATORY + tuple(w for w in WATCH if w not in SCAN_ONLY)
HETERONYM_SET = frozenset(w.lower() for w in HETERONYMS)
BLOCKS = {"p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "dd", "dt", "td",
          "th", "figcaption", "caption", "pre", "div", "section", "article", "aside", "body"}
# Echo's contract: no instructions on code, images, head content or captions.
# Links are left alone too, as in the earlier textbook build.
UNSUPPORTED = {"head", "title", "figcaption", "caption", "code", "pre", "kbd", "samp", "a",
               "script", "style", "svg", "math", "nav"}
BAD_SPAN_TEXT = set("[]()/")
# Tokens Echo would normally expand, which an annotated block reads raw.
RAW_TOKEN = re.compile(r"[\w'’-]*\d[\w'’-]*|\w+(?:[./]\w+)+|[&%$#@+=<>~^*_|\\]")
CAPS = re.compile(r"\b[A-Z]{2,6}s?\b")
WORD_EDGE_L = r"(?<![\w'’\-])"
WORD_EDGE_R = r"(?![\w\-]|['’]\w)"
TAG = re.compile(r"<!--.*?-->|<!\[CDATA\[.*?\]\]>|<\?.*?\?>|<![^>]*>|<[^>]+>", re.S)
ENTITY = re.compile(r"&(#\d+|#[xX][0-9a-fA-F]+|[A-Za-z][A-Za-z0-9]*);")
# Hyphens don't end a heteronym: misaki splits `well-read` and tags `read` alone.
HETERONYM_RX = re.compile(r"(?<![\w'’])(" + "|".join(map(re.escape, sorted(set(HETERONYMS), key=len, reverse=True)))
                          + r")(?![\w]|['’]\w)", re.I)
SCAN_ONLY_RX = re.compile(WORD_EDGE_L + "(" + "|".join(map(re.escape, SCAN_ONLY)) + ")" + WORD_EDGE_R)
# A-I, A-P-I, G-D-P: misaki splits the hyphens and reads a capital A as the article.
HYPHEN_INITIALISM = re.compile(r"\b[A-Z](?:-[A-Z])+s?\b")
# Echo's text expansion (TextNormalizer) runs only on blocks without IPA spans.
# It replaces these anywhere, even inside a word: `LLMs.` -> "LLMiz".
GLUED_ABBREVIATION = re.compile(r"[A-Za-z0-9](?:Mrs|Mr|Ms|Dr|Prof)\.")
# Abbreviations it speaks as words, matched at the token's start in the block text.
# Dr., Mrs., Mr., Prof. and St. expand anywhere; the rest need no letter, digit or
# underscore before them; a month needs a day or year after it ("Jan. 5").
EXPANDED_ABBREVIATION = re.compile(
    r"(?:Dr|Mrs|Mr|Prof|St)\.|(?<!\w)(?:e\.g|i\.e|etc|vs|approx|Mt)\."
    r"|(?<!\w)(?:Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept?|Oct|Nov|Dec)\.(?=\s+[0-9])")
# "Ms." becomes "Miz", which isn't in the lexicon either.
MS_TITLE = re.compile(r"Ms\.")
# Unit symbols it speaks as words: a whole token, not after / . - and not before / -.
EXPANDED_UNIT = re.compile(r"(?<![\w/.\-])(?:km|hrs)(?![\w/\-])")
# Letters misaki reads after a number: 2nd, 1990s, 3pm.
NUMBER_SUFFIXES = {"st", "nd", "rd", "th", "s", "ed", "ing", "am", "pm"}
TOKEN = re.compile(r"[^\s—–/]+")
NOT_NARRATED = {"script", "style", "svg", "math"}
LEXICON_FILES = ("us_gold.json", "us_silver.json")
# misaki's subtokenizer (EnglishG2P.subtokenizeRegexPattern): it splits a word at
# case changes (`McTavish` -> Mc + Tavish, `SaaS` -> Saa + S).
_UP, _LOW, _LETTER = "A-ZÀ-ÖØ-Þ", "a-zß-öø-ÿ", r"[^\W\d_]"
SUBTOKEN = re.compile(rf"[{_UP}](?=[{_UP}][{_LOW}])|{_LETTER}*?(?:'{_LETTER})*?[{_LOW}](?=[{_UP}])"
                      rf"|{_LETTER}+(?:'{_LETTER})*")
MISAKI_SUBTOKEN = re.compile(rf"^'+|[{_UP}](?=[{_UP}][{_LOW}])|(?:^-)?(?:\d?[,.]?\d)+|[-_]+|'{{2,}}"
                             rf"|{_LETTER}*?(?:'{_LETTER})*?[{_LOW}](?=[{_UP}])|{_LETTER}+(?:'{_LETTER})*"
                             r"|[^\w'\-]|'+$")


class InputError(Exception):
    """The EPUB or decisions file can't be read."""


def word_rx(word: str, flags: int = 0) -> re.Pattern:
    return re.compile(WORD_EDGE_L + re.escape(word) + WORD_EDGE_R, flags)


def check_ipa(ipa: str) -> str | None:
    if not isinstance(ipa, str) or not ipa.strip():
        return "empty IPA"
    if len(ipa) > 300:
        return "IPA longer than 300 characters"
    if re.search(r"[/\[\]]", ipa):
        return f"IPA {ipa!r} has slash or bracket delimiters; give the bare IPA"
    if "." in ipa:
        return f"IPA {ipa!r} has syllable dots, which Echo rejects"
    if re.search(r"[A-Z]", ipa):
        return f"IPA {ipa!r} has capital letters (Kokoro shorthand); use standard IPA"
    if not re.search(r"[^\sˈˌ]", ipa):
        return f"IPA {ipa!r} has no speech symbols"
    return None


def unescape_with_map(raw: str) -> tuple[str, list[int]]:
    """Unescaped text plus, for each of its characters, the raw start index (and a final end)."""
    out, starts, pos = [], [], 0
    for m in ENTITY.finditer(raw):
        for i in range(pos, m.start()):
            out.append(raw[i]); starts.append(i)
        decoded = html.unescape(m.group(0))
        for ch in decoded:
            out.append(ch); starts.append(m.start())
        pos = m.end()
    for i in range(pos, len(raw)):
        out.append(raw[i]); starts.append(i)
    starts.append(len(raw))
    return "".join(out), starts


@dataclass
class Segment:
    raw: str
    is_text: bool
    in_body: bool = False
    block: int | None = None
    block_tag: str = ""
    annotated: bool = False
    unsupported: str = ""          # innermost unsupported element, if any
    in_pre: bool = False           # inside <pre>: Echo speaks "Code listing." instead
    text: str = ""
    starts: list[int] = field(default_factory=list)


@dataclass
class Block:
    uid: int
    tag: str
    segments: list[int] = field(default_factory=list)
    has_span: bool = False


class Doc:
    def __init__(self, name: str, source: str):
        self.name = name
        self.source = source
        self.segments: list[Segment] = []
        self.blocks: dict[int, Block] = {}
        self.alts: list[str] = []
        self._parse()

    def _parse(self) -> None:
        stack: list[tuple[str, int, bool]] = []      # (tag, uid, carries ssml:ph)
        uid = 0
        pos = 0

        def add_text(raw: str) -> None:
            seg = Segment(raw=raw, is_text=True)
            names = [n for n, _, _ in stack]
            seg.in_body = "body" in names
            seg.annotated = any(ph for _, _, ph in stack)
            seg.unsupported = next((n for n in reversed(names) if n in UNSUPPORTED), "")
            seg.in_pre = "pre" in names
            for n, u, _ in reversed(stack):
                if n in BLOCKS:
                    seg.block, seg.block_tag = u, n
                    break
            seg.text, seg.starts = unescape_with_map(raw)
            self.segments.append(seg)
            if seg.in_body and seg.block is not None:
                self.blocks.setdefault(seg.block, Block(seg.block, seg.block_tag)).segments.append(
                    len(self.segments) - 1)

        for m in TAG.finditer(self.source):
            if m.start() > pos:
                add_text(self.source[pos:m.start()])
            tag = m.group(0)
            self.segments.append(Segment(raw=tag, is_text=False))
            pos = m.end()
            if tag.startswith(("<!", "<?")):
                continue
            name = re.match(r"</?\s*([A-Za-z][\w.:-]*)", tag)
            if not name:
                continue
            local = name.group(1).split(":")[-1].lower()
            if tag.startswith("</"):
                while stack:
                    if stack.pop()[0] == local:
                        break
                continue
            if local == "img" and any(n == "body" for n, _, _ in stack):
                alt = re.search(r"\balt\s*=\s*(\"([^\"]*)\"|'([^']*)')", tag)
                if alt:
                    self.alts.append(html.unescape(alt.group(2) if alt.group(2) is not None else alt.group(3)))
            if tag.endswith("/>"):
                continue
            uid += 1
            ph = local == "span" and re.search(r"\bssml:ph\s*=", tag) is not None
            stack.append((local, uid, ph))
            if ph:
                for n, u, _ in reversed(stack[:-1]):
                    if n in BLOCKS:
                        self.blocks.setdefault(u, Block(u, n)).has_span = True
                        break
        if pos < len(self.source):
            add_text(self.source[pos:])

    def block_text(self, block: Block) -> tuple[str, list[tuple[int, int]]]:
        """Block text plus, per character, (segment index, offset in that segment's text)."""
        parts, where = [], []
        for si in block.segments:
            seg = self.segments[si]
            parts.append(seg.text)
            where.extend((si, k) for k in range(len(seg.text)))
        return "".join(parts), where

    def visible_text(self) -> str:
        return "".join(s.text for s in self.segments if s.is_text and s.in_body)

    def has_span(self) -> bool:
        return any(b.has_span for b in self.blocks.values())


class Epub:
    def __init__(self, path: Path):
        self.path = path
        try:
            self.zip = zipfile.ZipFile(path)
            container = ET.fromstring(self.zip.read("META-INF/container.xml"))
            rootfile = container.find(f"{{{CONTAINER_NS}}}rootfiles/{{{CONTAINER_NS}}}rootfile")
            if rootfile is None or not rootfile.get("full-path"):
                raise InputError("EPUB has no package document")
            self.opf_path = rootfile.get("full-path")
            self.opf_text = self.zip.read(self.opf_path).decode("utf-8")
            package = ET.fromstring(self.opf_text)
        except (OSError, KeyError, zipfile.BadZipFile, ET.ParseError, UnicodeDecodeError) as error:
            raise InputError(f"cannot read EPUB {path}: {error}") from error
        self.opf_dir = posixpath.dirname(self.opf_path)
        self.manifest: dict[str, tuple[str, str, str]] = {}
        for item in package.iter(f"{{{OPF_NS}}}item"):
            href = posixpath.normpath(posixpath.join(self.opf_dir, item.get("href", "")))
            self.manifest[item.get("id", "")] = (href, item.get("media-type", ""), item.get("properties", ""))
        self.narrated: list[str] = []
        for ref in package.iter(f"{{{OPF_NS}}}itemref"):
            href, media, props = self.manifest.get(ref.get("idref", ""), ("", "", ""))
            if ref.get("linear", "yes") == "no" or media not in XHTML_TYPES or "nav" in props.split():
                continue
            self.narrated.append(href)
        self.docs: dict[str, Doc] = {}
        for href in self.narrated:
            try:
                self.docs[href] = Doc(href, self.zip.read(href).decode("utf-8"))
            except (KeyError, UnicodeDecodeError) as error:
                raise InputError(f"cannot read spine document {href}: {error}") from error
        self.lexicons: list[tuple[str, list[tuple[str, str]]]] = []
        for href, media, _ in self.manifest.values():
            if media == "application/pls+xml":
                self.lexicons.append((href, self._read_pls(href)))

    def _read_pls(self, href: str) -> list[tuple[str, str]]:
        try:
            root = ET.fromstring(self.zip.read(href))
        except (KeyError, ET.ParseError) as error:
            raise InputError(f"cannot read lexicon {href}: {error}") from error
        entries = []
        for lexeme in root.iter(f"{{{PLS_NS}}}lexeme"):
            phoneme = (lexeme.findtext(f"{{{PLS_NS}}}phoneme") or "").strip()
            for grapheme in lexeme.iter(f"{{{PLS_NS}}}grapheme"):
                entries.append(((grapheme.text or "").strip(), phoneme))
        return entries

    def linked_lexicon(self, doc: Doc) -> bool:
        return re.search(r"<link\b[^>]*\brel\s*=\s*[\"']pronunciation[\"']", doc.source) is not None


def context_of(text: str, start: int, end: int, width: int = 60) -> str:
    a, b = max(0, start - width), min(len(text), end + width)
    return " ".join(text[a:start].split()) + " [[" + text[start:end] + "]] " + " ".join(text[end:b].split())


# ---------------------------------------------------------------- renderer lexicon


def _grow(words: set[str]) -> set[str]:
    """misaki's growDictionary: lower-case keys gain a capitalised form, and back."""
    grown = set(words)
    for word in words:
        if len(word) < 2:
            continue
        if word == word.lower():
            grown.add(word.capitalize())
        elif word == word.lower().capitalize():
            grown.add(word.lower())
    return grown


def misaki_subtokens(word: str) -> list[str]:
    """EnglishG2P.subtokenize: the regex matches plus the text between them."""
    parts, cursor = [], 0
    for m in MISAKI_SUBTOKEN.finditer(word):
        if m.start() > cursor:
            parts.append(word[cursor:m.start()])
        parts.append(m.group(0))
        cursor = m.end()
    if cursor < len(word):
        parts.append(word[cursor:])
    return parts


def misaki_splits_camel_case(word: str, parts: list[str]) -> bool:
    """True when misaki reads each part of `word` on its own (preserveCamelCaseWordBreaks):
    the word has a case boundary, and two neighbouring parts both hold letters and the
    first isn't `Mc`. misaki then never looks the whole word up."""
    if len(parts) < 2 or not any(
            (word[i].isupper() and word[i - 1].islower())
            or (i + 1 < len(word) and word[i - 1].isupper() and word[i].isupper() and word[i + 1].islower())
            for i in range(1, len(word))):
        return False
    return any(any(c.isalpha() for c in a) and any(c.isalpha() for c in b) and a.lower() != "mc"
               for a, b in zip(parts, parts[1:]))


class RendererLexicon:
    """The words Echo's misaki G2P can read without its letter-rule fallback.

    Mirrors misaki's lexicon lookup (exact and case-grown keys, initialisms read
    letter by letter, and the -s, -'s, -es, -ies, -ed, -ied and -ing stems). It
    leaves out misaki's closed-compound guess, which Echo's audit records as a
    fallback, and Echo's supplemental pack, which isn't misaki.
    """

    def __init__(self, gold: set[str], silver: set[str], source: str = ""):
        self.gold = _grow(gold)
        self.words = self.gold | _grow(silver)
        self.source = source
        self._cache: dict[str, bool] = {}
        # Echo reads its built-in overrides and contextual homographs before misaki;
        # the audit validator keeps this vocabulary in step with the renderer.
        scripts = str(Path(__file__).resolve().parent)
        if scripts not in sys.path:
            sys.path.insert(0, scripts)
        from validate_pronunciation_audit import WATCH_WORDS
        self.echo_words = frozenset(WATCH_WORDS)

    @classmethod
    def load(cls, directory: Path) -> "RendererLexicon":
        keys = []
        for name in LEXICON_FILES:
            path = directory / name
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
                raise InputError(f"cannot read the renderer lexicon {path}: {error}") from error
            if not isinstance(data, dict) or not data:
                raise InputError(f"{path} is not a misaki lexicon (a JSON object of words)")
            keys.append(set(data))
        return cls(keys[0], keys[1], str(directory))

    def _known(self, word: str) -> bool:
        if word in self.words:
            return True
        if not re.fullmatch(r"[A-Za-z'-]+", word):
            return False
        if len(word) == 1 or (word.isupper() and word.lower() in self.gold):
            return True
        return word[1:] == word[1:].upper()      # an initialism, read letter by letter

    def _stem_s(self, word: str) -> bool:
        if not word.endswith("s") or not (len(word) >= 3 or (len(word) == 2 and word[0].isupper())):
            return False
        if not word.endswith("ss") and self._known(word[:-1]):
            return True
        if (word.endswith("'s") or (len(word) > 4 and word.endswith("es") and not word.endswith("ies"))) \
                and self._known(word[:-2]):
            return True
        return len(word) > 4 and word.endswith("ies") and self._known(word[:-3] + "y")

    def _stem_ed(self, word: str) -> bool:
        if len(word) < 4 or not word.endswith("d"):
            return False
        if not word.endswith("dd") and self._known(word[:-1]):
            return True
        if len(word) > 4 and word.endswith("ied") and self._known(word[:-3] + "y"):
            return True
        return len(word) > 4 and word.endswith("ed") and not word.endswith("eed") and self._known(word[:-2])

    def _stem_ing(self, word: str) -> bool:
        if len(word) < 5 or not word.endswith("ing"):
            return False
        if (len(word) > 5 and self._known(word[:-3])) or self._known(word[:-3] + "e"):
            return True
        return (len(word) > 5 and re.search(r"([bcdgklmnprstvxz])\1ing$|cking$", word) is not None
                and self._known(word[:-4]))

    def _stems(self, word: str) -> bool:
        return self._stem_s(word) or self._stem_ed(word) or self._stem_ing(word)

    def _resolves(self, word: str) -> bool:
        lower = word.lower()
        candidate = word
        if (len(word) > 1 and word.replace("'", "").isalpha() and word != lower and word not in self.words
                and (word == word.upper() or word[1:] == word[1:].lower())
                and (lower in self.words or self._stems(lower))):
            candidate = lower
        if self._known(candidate):
            return True
        if candidate.endswith("s'") and self._known(candidate[:-2] + "'s"):
            return True
        if candidate.endswith("'") and self._known(candidate[:-1]):
            return True
        return self._stems(candidate)

    def knows(self, word: str) -> bool:
        """True when misaki reads `word` (letters and apostrophes) from its lexicon."""
        word = unicodedata.normalize("NFKC", word.replace("’", "'").replace("‘", "'"))
        if word not in self._cache:
            parts = misaki_subtokens(word)
            if word.lower() in self.echo_words:
                known = True
            elif misaki_splits_camel_case(word, parts):
                # `SaaS` is a lexicon key, but misaki reads `Saa` and `S` apart.
                known = all(self._resolves(part) for part in parts if re.search(_LETTER, part))
            else:
                known = self._resolves(word)
                if not known:
                    parts = SUBTOKEN.findall(word)
                    known = len(parts) > 1 and all(self._resolves(part) for part in parts)
            self._cache[word] = known
        return self._cache[word]


def installed_renderer_resources(source_sha: str, renderer_root: str | None) -> Path:
    """EchoNarrationResources of the installed renderer the narration wrapper would select."""
    scripts = str(Path(__file__).resolve().parent)
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    try:
        import echo_installed_renderer as installed

        if not re.fullmatch(r"[0-9a-f]{40}", source_sha):
            raise ValueError("APPROVED_ECHO_PRONUNCIATION_SHA must be a 40-character commit SHA")
        root = installed.canonical_renderer_root(renderer_root)
        selector = installed.strict_json_object(root / source_sha / "approved-renderer.json",
                                                "renderer selector")
        manifest = selector.get("manifestSHA256")
        if selector.get("echoSourceSHA") != source_sha or not isinstance(manifest, str) \
                or not re.fullmatch(r"[0-9a-f]{64}", manifest):
            raise ValueError("renderer selector doesn't name an installed build for this source")
        return root / source_sha / manifest / "EchoNarrationResources"
    except (ImportError, OSError, ValueError) as error:
        raise InputError(f"cannot find installed Echo renderer {source_sha}: {error}") from error


def find_lexicon_dir(explicit: Path | None, environ: Mapping[str, str] | None = None) -> Path:
    """The directory holding the renderer's us_gold.json and us_silver.json; fails closed."""
    environ = os.environ if environ is None else environ
    if explicit is not None:
        directory = explicit
    elif environ.get("ECHO_RESOURCE_DIR"):
        directory = Path(environ["ECHO_RESOURCE_DIR"])
    elif environ.get("APPROVED_ECHO_PRONUNCIATION_SHA"):
        directory = installed_renderer_resources(environ["APPROVED_ECHO_PRONUNCIATION_SHA"],
                                                 environ.get("ECHO_RENDERER_ROOT") or None)
    else:
        raise InputError("cannot find the renderer's lexicon, so the check can't tell which words Echo "
                         "would guess. Pass --lexicon-dir <renderer>/EchoNarrationResources, or set "
                         "APPROVED_ECHO_PRONUNCIATION_SHA to the Echo renderer you will narrate with")
    missing = [name for name in LEXICON_FILES if not (directory / name).is_file()]
    if missing:
        raise InputError(f"renderer lexicon directory {directory} lacks {', '.join(missing)}; point "
                         "--lexicon-dir at the renderer's EchoNarrationResources")
    return directory


# ---------------------------------------------------------------- check


class _Tally:
    """Problems grouped by word: count plus the first place each was seen."""

    def __init__(self) -> None:
        self.counts: Counter[tuple[str, str]] = Counter()
        self.first: dict[tuple[str, str], tuple[str, str]] = {}

    def add(self, kind: str, word: str, doc: str, context: str) -> None:
        self.counts[(kind, word)] += 1
        self.first.setdefault((kind, word), (doc, context))

    def items(self):
        for key, (doc, context) in self.first.items():
            yield key[0], key[1], self.counts[key], doc, context


def hyphen_initialism_errors(epub: Epub) -> list[str]:
    """`A-I`, `A-P-I`: Echo reads the capital A as the article ("uh-EYE")."""
    tally = _Tally()
    for name, doc in epub.docs.items():
        for block in doc.blocks.values():
            text, where = doc.block_text(block)
            for m in HYPHEN_INITIALISM.finditer(text):
                seg = doc.segments[where[m.start()][0]]
                if not seg.annotated and not seg.in_pre:
                    tally.add("initialism", m.group(0), name, context_of(text, m.start(), m.end()))
        for alt in doc.alts:
            for m in HYPHEN_INITIALISM.finditer(alt):
                tally.add("initialism", m.group(0), name, "image alt text: " + context_of(alt, m.start(), m.end()))
    return [f"{doc}: '{word}' x{count} spells an initialism with hyphens, so Echo reads each letter as its "
            f"own word and a capital A as the article 'uh' (A-I becomes 'uh-EYE'); write the closed form "
            f"({word.replace('-', '')}) and give it one reading for the whole book, or, if the letters stand "
            f"apart (A-Z, an X-Y plane), keep the hyphen and give each use an inline reading: {context}"
            for _, word, count, doc, context in tally.items()]


def _pls_patterns(epub: Epub) -> list[re.Pattern]:
    """One pattern per PLS grapheme, with the word edges Echo's applyLexicons uses."""
    return [re.compile(r"(?<![\w'’])" + re.escape(g) + r"(?![\w'’])")
            for g in sorted({g for _, entries in epub.lexicons for g, _ in entries if g})]


def _pls_matches(epub: Epub, doc: Doc, text: str, rxs: list[re.Pattern]) -> list[tuple[int, int]]:
    """Where Echo applies the PLS in this block: only in documents that link it."""
    if not epub.linked_lexicon(doc):
        return []
    return [(m.start(), m.end()) for rx in rxs for m in rx.finditer(text)]


def _spoken_tokens(epub: Epub):
    """(doc, token, start, end, block text, block annotated) for narrated text with no IPA
    from a span or the PLS. A block is annotated when it has an inline span or a PLS
    match: Echo stores both as pronunciation spans and then skips its text expansion."""
    rxs = _pls_patterns(epub)
    for name, doc in epub.docs.items():
        for block in doc.blocks.values():
            text, where = doc.block_text(block)
            covered = _pls_matches(epub, doc, text, rxs)
            annotated = block.has_span or bool(covered)
            for m in TOKEN.finditer(text):
                segments = [doc.segments[si] for si in {where[i][0] for i in range(m.start(), m.end())}]
                if any(s.annotated or s.in_pre or s.unsupported in NOT_NARRATED for s in segments):
                    continue
                if any(a < m.end() and m.start() < b for a, b in covered):
                    continue
                yield name, m.group(0), m.start(), m.end(), text, annotated


def _whole_token(rx: re.Pattern, text: str, offset: int, length: int) -> bool:
    """True when `rx` matches exactly `length` characters of `text` at `offset`."""
    m = rx.match(text, offset)
    return m is not None and m.end() == offset + length


def spoken_token_errors(epub: Epub, lexicon: RendererLexicon | None) -> list[str]:
    """Tokens Echo would mangle or guess. Without a lexicon, only the shape rules run."""
    tally = _Tally()
    for name, chunk, start, end, text, annotated_block in _spoken_tokens(epub):
        token = re.sub(r"^[\W_]+|[\W_]+$", "", chunk)
        offset = start + max(chunk.find(token), 0)
        context = context_of(text, offset, offset + len(token))
        if not annotated_block:
            # Echo's text expansion runs only here; an annotated block reads every token raw.
            if GLUED_ABBREVIATION.search(chunk):
                tally.add("glued", token, name, context)
                continue
            if _whole_token(MS_TITLE, text, offset, len(token) + 1):
                tally.add("miz", token, name, context)
                continue
            if _whole_token(EXPANDED_ABBREVIATION, text, offset, len(token) + 1) \
                    or _whole_token(EXPANDED_UNIT, text, offset, len(token)):
                continue
        if not re.search(r"[^\W\d_]", token):
            continue                                    # numbers and punctuation
        for part in re.split(r"[-_‐‑]+", token):
            if not re.search(r"[^\W\d_]", part):
                continue
            if re.search(r"[^\W_]\.[^\W\d_]", part):
                # U.S., e.g. and Ph.D. are read as letters, also before a hyphen (U.S.-based);
                # in an annotated block the numeral and file-name rule already asks for a reading.
                if any(len(piece) > 2 for piece in part.split(".")) and not annotated_block:
                    tally.add("dotted", part, name, context)
                continue
            if re.search(r"\d", part):
                if annotated_block:
                    continue
                for run in re.finditer(r"[^\W\d_]+", part):
                    letters = run.group(0)
                    after_number = run.start() > 0 and part[run.start() - 1].isdigit()
                    if len(letters) < 2 or letters.isupper() \
                            or (after_number and letters.lower() in NUMBER_SUFFIXES) \
                            or (lexicon.knows(letters) if lexicon else not after_number):
                        continue
                    tally.add("unit", part, name, context)
                    break
            elif lexicon is not None and not lexicon.knows(part):
                tally.add("fallback", part, name, context)
    messages = {
        "glued": "is followed by a period, and Echo's text expansion reads its Mr., Mrs., Ms. or Dr. ending "
                 "as a title ('LLMs.' becomes 'LLMiz'); give it a reading or reword so no period follows it",
        "dotted": "has a period inside it, so Echo reads it as one unknown word and guesses; write it in "
                  "words (for example 'Claude dot AI') or give it a reading",
        "unit": "joins a number to letters Echo can't read, so it guesses them; write it out (for example "
                "'five percentage points') or give it a reading",
        "miz": "is a title that Echo's text expansion reads as 'Miz', a word the renderer guesses; drop "
               "the title, or give it a reading (an annotated block skips the expansion)",
        "fallback": "isn't in the renderer's lexicon, so Echo would guess it by letter rules; give it IPA "
                    "(a lexicon entry, or a reading at each use)",
    }
    return [f"{doc}: '{word}' x{count} {messages[kind]}: {context}"
            for kind, word, count, doc, context in tally.items()]


def heteronym_errors(epub: Epub) -> list[str]:
    """Every heteronym needs an inline reading: headings, number blocks and compounds too."""
    errors = []
    for name, doc in epub.docs.items():
        for block in doc.blocks.values():
            text, where = doc.block_text(block)
            for m in HETERONYM_RX.finditer(text):
                seg = doc.segments[where[m.start()][0]]
                if seg.annotated or seg.in_pre:
                    continue
                if seg.unsupported:
                    errors.append(f"{name}: '{m.group(0)}' in <{seg.unsupported}> can't carry IPA; reword it "
                                  f"or move it out: {context_of(text, m.start(), m.end())}")
                else:
                    errors.append(f"{name}: '{m.group(0)}' has no IPA reading: {context_of(text, m.start(), m.end())}")
        for alt in doc.alts:
            for m in HETERONYM_RX.finditer(alt):
                errors.append(f"{name}: '{m.group(0)}' in image alt text can't carry IPA; reword it: "
                              f"{context_of(alt, m.start(), m.end())}")
    return errors


def check(epub: Epub, lexicon: RendererLexicon | Callable[[], RendererLexicon] | None = None
          ) -> tuple[list[str], list[str]]:
    """The narration gate. `lexicon` (or a loader for it) turns on the word-coverage rule."""
    errors: list[str] = []
    warnings: list[str] = []
    narrated_words = sum(len(d.visible_text().split()) for d in epub.docs.values())
    if not narrated_words:
        return errors, ["no narrated text found; nothing to pronounce"]
    if callable(lexicon):
        lexicon = lexicon()
    graphemes = {word for _, entries in epub.lexicons for g, _ in entries for word in [g, *g.split()]}
    pls_rxs = _pls_patterns(epub)
    any_ipa = False
    for name, doc in epub.docs.items():
        linked = epub.linked_lexicon(doc)
        any_ipa = any_ipa or linked or doc.has_span()
        if doc.has_span():
            root = re.search(r"<html\b[^>]*>", doc.source)
            if not root or SSML_NS not in root.group(0) or not re.search(r"ssml:alphabet\s*=", root.group(0)):
                errors.append(f"{name}: has ssml:ph spans but the <html> root doesn't declare "
                              f"xmlns:ssml=\"{SSML_NS}\" and ssml:alphabet")
        for m in re.finditer(r"<span\b[^>]*\bssml:ph\s*=\s*\"([^\"]*)\"[^>]*>", doc.source):
            problem = check_ipa(html.unescape(m.group(1)))
            if problem:
                errors.append(f"{name}: {problem}")
        for si, seg in enumerate(doc.segments):
            if not seg.is_text or not seg.in_body:
                continue
            if seg.annotated:
                if BAD_SPAN_TEXT & set(seg.text):
                    errors.append(f"{name}: annotated text {seg.text.strip()!r} contains one of []()/ — "
                                  "Echo drops every block of the book on import")
                if seg.unsupported:
                    errors.append(f"{name}: ssml:ph inside <{seg.unsupported}>, which Echo can't annotate")
        nested = re.findall(r"<span\b[^>]*ssml:ph[^>]*>(?:(?!</span>).)*<span\b[^>]*ssml:ph", doc.source, re.S)
        if nested:
            errors.append(f"{name}: nested ssml:ph spans")
        for block in doc.blocks.values():
            text, where = doc.block_text(block)
            pls = _pls_matches(epub, doc, text, pls_rxs)
            if not block.has_span and not pls:
                continue
            for m in RAW_TOKEN.finditer(text):
                si, _ = where[m.start()]
                if doc.segments[si].annotated or doc.segments[si].in_pre:
                    continue
                if any(a < m.end() and m.start() < b for a, b in pls):
                    continue
                errors.append(f"{name}: '{m.group(0)}' sits in an annotated block, where Echo skips text "
                              f"expansion; add a reading for it: {context_of(text, m.start(), m.end())}")
            for m in CAPS.finditer(text):
                si, _ = where[m.start()]
                if not doc.segments[si].annotated and m.group(0) not in graphemes:
                    warnings.append(f"{name}: '{m.group(0)}' sits unexpanded in an annotated block; "
                                    "consider a lexicon entry")
    errors.extend(heteronym_errors(epub))
    errors.extend(hyphen_initialism_errors(epub))
    errors.extend(spoken_token_errors(epub, lexicon))
    for href, entries in epub.lexicons:
        for grapheme, phoneme in entries:
            problem = check_ipa(phoneme)
            if problem:
                errors.append(f"{href}: lexeme {grapheme!r}: {problem}")
            if grapheme.lower() in HETERONYM_SET:
                errors.append(f"{href}: {grapheme!r} reads differently by sense; give each occurrence "
                              "an inline reading instead of a lexicon entry")
            rx = re.compile(r"(?<![\w'’])" + re.escape(grapheme) + r"(?![\w'’])")
            for name, doc in epub.docs.items():
                for block in doc.blocks.values():
                    text, _ = doc.block_text(block)
                    for m in rx.finditer(text):
                        before = text[max(0, m.start() - 2):m.start()]
                        after = text[m.end():m.end() + 2]
                        if re.fullmatch(r"\w[.\-/]", before) or re.fullmatch(r"[.\-/]\w", after):
                            errors.append(f"{href}: grapheme {grapheme!r} matches inside a dotted or "
                                          f"hyphenated token in {name}, which stops synthesis: "
                                          f"{context_of(text, m.start(), m.end())}")
                            break
    if not any_ipa:
        errors.insert(0, "no IPA pronunciations are embedded: no narrated document has ssml:ph spans "
                         "or a linked pronunciation lexicon")
    return errors, warnings


# ---------------------------------------------------------------- scan


def scan(epub: Epub, lexicon: RendererLexicon | None = None) -> list[dict]:
    """Candidates by kind: mandatory (heteronyms), watch, token, caps, hyphen-initialism
    and, with a lexicon, fallback (words Echo would guess)."""
    kinds = [("mandatory", HETERONYM_RX), ("watch", SCAN_ONLY_RX), ("token", RAW_TOKEN), ("caps", CAPS),
             ("hyphen-initialism", HYPHEN_INITIALISM)]
    rows = []
    for name, doc in epub.docs.items():
        for bi, block in enumerate(doc.blocks.values()):
            text, where = doc.block_text(block)
            for kind, rx in kinds:
                for m in rx.finditer(text):
                    seg = doc.segments[where[m.start()][0]]
                    if seg.in_pre:
                        continue                        # Echo speaks "Code listing." for <pre>
                    rows.append({"doc": posixpath.basename(name), "block": bi, "tag": block.tag, "kind": kind,
                                 "word": m.group(0), "annotated": seg.annotated,
                                 "surface": seg.unsupported or block.tag,
                                 "context": " ".join(text[max(0, m.start() - 50):m.end() + 50].split())})
    if lexicon is not None:
        for name, chunk, start, end, text, _ in _spoken_tokens(epub):
            token = re.sub(r"^[\W_]+|[\W_]+$", "", chunk)
            for part in re.split(r"[-_‐‑]+", token):
                if re.fullmatch(r"[^\W\d_]+(?:['’][^\W\d_]+)*", part) and not lexicon.knows(part):
                    rows.append({"doc": posixpath.basename(name), "block": None, "tag": "", "kind": "fallback",
                                 "word": part, "annotated": False, "surface": "",
                                 "context": " ".join(text[max(0, start - 50):end + 50].split())})
    return rows


# ---------------------------------------------------------------- apply


def _norm(text: str) -> tuple[str, list[int]]:
    """Whitespace-collapsed, quote-folded text and each character's index in the original."""
    out, idx, space = [], [], False
    for i, ch in enumerate(text):
        if ch.isspace():
            if not space and out:
                out.append(" "); idx.append(i)
            space = True
            continue
        space = False
        out.append({"’": "'", "‘": "'", "“": '"', "”": '"'}.get(ch, ch)); idx.append(i)
    return "".join(out), idx


def load_decisions(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise InputError(f"cannot read decisions {path}: {error}") from error
    if not isinstance(data, dict):
        raise InputError("decisions file must be a JSON object")
    problems = []
    for key in ("occurrences", "readings", "lexicon"):
        if not isinstance(data.get(key, []), list):
            problems.append(f"'{key}' must be a list")
    for i, d in enumerate(data.get("occurrences", [])):
        where = f"occurrence {i + 1} ({d.get('word')!r})"
        for k in ("word", "ipa", "context"):
            if not isinstance(d.get(k), str) or not d[k].strip():
                problems.append(f"{where}: needs '{k}'")
        if isinstance(d.get("ipa"), str) and check_ipa(d["ipa"]):
            problems.append(f"{where}: {check_ipa(d['ipa'])}")
        if isinstance(d.get("word"), str) and BAD_SPAN_TEXT & set(d["word"]):
            problems.append(f"{where}: annotated text can't contain []()/")
    for i, r in enumerate(data.get("readings", [])):
        where = f"reading {i + 1} ({r.get('text')!r})"
        if not isinstance(r.get("text"), str) or not r["text"].strip():
            problems.append(f"{where}: needs 'text'")
        elif BAD_SPAN_TEXT & set(r["text"]):
            problems.append(f"{where}: Echo can't annotate text containing []()/; leave that block "
                            "unannotated so normal expansion reads it")
        if check_ipa(r.get("ipa", "")):
            problems.append(f"{where}: {check_ipa(r.get('ipa', ''))}")
    owner: dict[str, str] = {}
    for i, lex in enumerate(data.get("lexicon", [])):
        where = f"lexeme {i + 1}"
        graphemes = lex.get("graphemes")
        if not isinstance(graphemes, list) or not graphemes:
            problems.append(f"{where}: needs a non-empty 'graphemes' list")
            continue
        if check_ipa(lex.get("ipa", "")):
            problems.append(f"{where}: {check_ipa(lex.get('ipa', ''))}")
        for g in graphemes:
            if not isinstance(g, str) or not g.strip() or len(g) > 200:
                problems.append(f"{where}: bad grapheme {g!r}")
            elif g.lower() in HETERONYM_SET:
                problems.append(f"{where}: {g!r} reads differently by sense; use per-occurrence readings")
            elif g in owner and owner[g] != lex.get("ipa"):
                problems.append(f"{where}: {g!r} already has the pronunciation {owner[g]!r}")
            else:
                owner[g] = lex.get("ipa")
    if problems:
        raise InputError("decisions file:\n  " + "\n  ".join(problems))
    return data


def _locate(epub: Epub, d: dict) -> tuple[str, int, int, int] | str:
    """(doc, segment index, raw start, raw end) for one occurrence, or an error message."""
    ctx, _ = _norm(d["context"].strip())
    word_n, _ = _norm(d["word"].strip())
    hits = []
    for name, doc in epub.docs.items():
        if d.get("doc") and posixpath.basename(name) != d["doc"]:
            continue
        for block in doc.blocks.values():
            text, where = doc.block_text(block)
            norm, back = _norm(text)
            start = norm.find(ctx)
            while start != -1:
                hits.append((name, doc, text, where, norm, back, start))
                start = norm.find(ctx, start + 1)
    label = f"occurrence {d['word']!r} in context {d['context']!r}"
    if not hits:
        return f"{label}: context not found in narrated text"
    if len(hits) > 1:
        docs = sorted({posixpath.basename(h[0]) for h in hits})
        return f"{label}: context appears {len(hits)} times ({', '.join(docs)}); quote more of the sentence"
    name, doc, text, where, norm, back, start = hits[0]
    # Search the whole block so word edges see the real neighbours, not the context's ends.
    inner = [m for m in word_rx(word_n).finditer(norm) if start <= m.start() and m.end() <= start + len(ctx)]
    nth = d.get("nth")
    if nth is None:
        if len(inner) != 1:
            return f"{label}: the word appears {len(inner)} times in the context; add 'nth'"
        m = inner[0]
    else:
        if not isinstance(nth, int) or not 1 <= nth <= len(inner):
            return f"{label}: 'nth' {nth!r} is out of range (the word appears {len(inner)} times)"
        m = inner[nth - 1]
    first, last = back[m.start()], back[m.end() - 1]
    si, off = where[first]
    sj, off_end = where[last]
    if si != sj:
        return f"{label}: the word crosses inline markup; annotate a phrase inside one text run"
    seg = doc.segments[si]
    if seg.annotated:
        return f"{label}: already inside an ssml:ph span"
    if seg.unsupported:
        return f"{label}: sits in <{seg.unsupported}>, which Echo can't annotate"
    return name, si, seg.starts[off], seg.starts[off_end + 1]


def load_dictionary() -> dict:
    path = Path(__file__).resolve().parents[1] / "references/pronunciation-dictionary.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        for entry in data["entries"]:
            if not entry["text"] or BAD_SPAN_TEXT & set(entry["text"]) or check_ipa(entry["ipa"]):
                raise ValueError(f"invalid entry: {entry!r}")
        return data
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise InputError(f"cannot load shared pronunciation dictionary: {error}") from error


def apply_dictionary(epub_path: Path) -> None:
    """Build-time defaults; the final narration gate still checks contextual IPA."""
    out = epub_path.with_name(epub_path.name + ".pronunciation")
    epub = Epub(epub_path)
    try:
        apply(epub, {}, out, validate=False)
    finally:
        epub.zip.close()
    out.replace(epub_path)


def apply(epub: Epub, decisions: dict, out: Path, lexicon_name: str = "names.pls", *, validate: bool = True,
          lexicon: RendererLexicon | None = None) -> tuple[list[dict], list[str]]:
    # Rebuild shared spans so later per-book decisions can replace defaults.
    for name, doc in list(epub.docs.items()):
        source = re.sub(r'<span ssml:ph="[^"]*" data-pronunciation="shared">([^<]*)</span>',
                        r'\1', doc.source)
        if source != doc.source:
            epub.docs[name] = Doc(name, source)
    lang = decisions.get("lang", "en-US")
    edits: dict[str, dict[int, list[tuple[int, int, str]]]] = {}
    problems: list[str] = []
    report: list[dict] = []
    shared_spans: set[tuple[str, int, int, int]] = set()
    dictionary = load_dictionary()
    for d in decisions.get("occurrences", []):
        found = _locate(epub, d)
        if isinstance(found, str):
            problems.append(found)
            continue
        name, si, a, b = found
        edits.setdefault(name, {}).setdefault(si, []).append((a, b, d["ipa"]))
        report.append({"doc": posixpath.basename(name), "word": d["word"], "ipa": d["ipa"],
                       "context": d["context"], "kind": "occurrence"})
    # A PLS match is a pronunciation span in Echo too, so token readings reach its block.
    # The book's own PLS applies where a document links it; this run's lexicon is linked
    # to every document that it writes.
    book_pls = _pls_patterns(epub)
    run_pls = [re.compile(r"(?<![\w'’])" + re.escape(g) + r"(?![\w'’])")
               for g in sorted({g for lex in decisions.get("lexicon", []) for g in lex["graphemes"] if g})]
    for name, doc in epub.docs.items():
        doc_edits = edits.get(name, {})
        pls_rxs = run_pls + (book_pls if epub.linked_lexicon(doc) else [])
        for block in doc.blocks.values():
            shared_match = any(word_rx(entry["text"]).search(doc.segments[si].text)
                               for si in block.segments for entry in dictionary["entries"])
            pls_match = bool(pls_rxs) and any(rx.search(doc.block_text(block)[0]) for rx in pls_rxs)
            if not block.has_span and not any(si in doc_edits for si in block.segments) \
                    and not shared_match and not pls_match:
                continue
            for r in decisions.get("readings", []):
                rx = word_rx(r["text"])
                for si in block.segments:
                    seg = doc.segments[si]
                    if seg.annotated or seg.unsupported:
                        continue
                    for m in rx.finditer(seg.text):
                        doc_edits.setdefault(si, []).append((seg.starts[m.start()], seg.starts[m.end()], r["ipa"]))
                        report.append({"doc": posixpath.basename(name), "word": r["text"], "ipa": r["ipa"],
                                       "context": "", "kind": "reading"})
        if doc_edits:
            edits[name] = doc_edits
    # Authored occurrences, token readings, inline spans and book lexicons win.
    overridden = {g for lex in decisions.get("lexicon", []) for g in lex["graphemes"]}
    overridden.update(g for _, entries in epub.lexicons for g, _ in entries)
    for name, doc in epub.docs.items():
        for si, seg in enumerate(doc.segments):
            if not seg.is_text or not seg.in_body or seg.annotated or seg.unsupported:
                continue
            spans = edits.setdefault(name, {}).setdefault(si, [])
            for entry in dictionary["entries"]:
                if entry["text"] in overridden:
                    continue
                for match in word_rx(entry["text"]).finditer(seg.text):
                    a, b = seg.starts[match.start()], seg.starts[match.end()]
                    if any(a < end and b > start for start, end, _ in spans):
                        continue
                    spans.append((a, b, entry["ipa"]))
                    shared_spans.add((name, si, a, b))
                    report.append({"doc": posixpath.basename(name), "word": match.group(),
                                   "ipa": entry["ipa"], "kind": "dictionary", "context": ""})
            if not spans:
                edits[name].pop(si, None)
        if not edits.get(name):
            edits.pop(name, None)
    if problems:
        raise InputError("cannot place every decision:\n  " + "\n  ".join(problems))

    changed: dict[str, str] = {}
    for name, doc in epub.docs.items():
        doc_edits = edits.get(name, {})
        parts = []
        for si, seg in enumerate(doc.segments):
            spans = sorted(doc_edits.get(si, []))
            for (a1, b1, _), (a2, _, _) in zip(spans, spans[1:]):
                if a2 < b1:
                    raise InputError(f"{name}: two decisions overlap in {seg.text.strip()[:60]!r}")
            raw, pos = seg.raw, 0
            for a, b, ipa in spans:
                parts.append(raw[pos:a])
                marker = ' data-pronunciation="shared"' if (name, si, a, b) in shared_spans else ''
                parts.append(f'<span ssml:ph="{html.escape(ipa, quote=True)}"{marker}>{raw[a:b]}</span>')
                pos = b
            parts.append(raw[pos:])
        source = "".join(parts)
        if doc_edits or doc.has_span():
            source = _declare_root(source, lang)
        if decisions.get("lexicon") and not epub.linked_lexicon(doc):
            href = posixpath.relpath(posixpath.join(epub.opf_dir, lexicon_name), posixpath.dirname(name) or ".")
            link = (f'<link rel="pronunciation" type="application/pls+xml" '
                    f'hreflang="{html.escape(lang, quote=True)}" href="{html.escape(href, quote=True)}"/>')
            source, count = re.subn(r"<head\b[^>]*>", lambda m: m.group(0) + link, source, count=1)
            if not count:
                raise InputError(f"{name}: no <head> to link the lexicon from")
        if source != epub.zip.read(name).decode("utf-8"):
            if Doc(name, source).visible_text() != doc.visible_text():
                raise InputError(f"{name}: embedding changed the visible text")
            changed[name] = source

    opf = epub.opf_text
    pls_path = posixpath.join(epub.opf_dir, lexicon_name) if decisions.get("lexicon") else None
    if pls_path and not any(href == posixpath.normpath(pls_path) for href, _, _ in epub.manifest.values()):
        item = f'<item id="pronunciation-lexicon" href="{html.escape(lexicon_name, quote=True)}" media-type="application/pls+xml"/>'
        opf, count = re.subn(r"(<manifest\b[^>]*>)", lambda m: m.group(1) + "\n" + item, opf, count=1)
        if not count:
            raise InputError("package document has no <manifest>")
    tmp = out.with_name(out.name + ".tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        for info in epub.zip.infolist():
            if info.filename == "mimetype" or (pls_path and info.filename == pls_path):
                continue
            if info.filename == epub.opf_path:
                z.writestr(info, opf.encode("utf-8"), compress_type=zipfile.ZIP_DEFLATED)
            elif info.filename in changed:
                z.writestr(info, changed[info.filename].encode("utf-8"), compress_type=zipfile.ZIP_DEFLATED)
            else:
                z.writestr(info, epub.zip.read(info.filename))
        if pls_path:
            z.writestr(pls_path, build_pls(decisions["lexicon"], lang))
    errors, warnings = check(Epub(tmp), lexicon) if validate else ([], [])
    if errors:
        tmp.unlink()
        raise CheckFailed(errors, warnings)
    tmp.replace(out)
    return report, warnings


class CheckFailed(Exception):
    def __init__(self, errors: list[str], warnings: list[str]):
        super().__init__("\n".join(errors))
        self.errors, self.warnings = errors, warnings


def _declare_root(source: str, lang: str) -> str:
    m = re.search(r"<html\b[^>]*>", source)
    if not m:
        raise InputError("XHTML document has no <html> root")
    tag = m.group(0)
    extra = []
    if "xmlns:ssml=" not in tag:
        extra.append(f'xmlns:ssml="{SSML_NS}"')
    if "ssml:alphabet=" not in tag:
        extra.append('ssml:alphabet="ipa"')
    if "xml:lang=" not in tag:
        extra.append(f'xml:lang="{html.escape(lang, quote=True)}"')
    if not extra:
        return source
    closing = "/>" if tag.endswith("/>") else ">"
    new = tag[: -len(closing)].rstrip() + " " + " ".join(extra) + closing
    return source[: m.start()] + new + source[m.end():]


def build_pls(entries: list[dict], lang: str) -> str:
    lines = ['<?xml version="1.0" encoding="utf-8"?>',
             f'<lexicon xmlns="{PLS_NS}" version="1.0" alphabet="ipa" xml:lang="{html.escape(lang, quote=True)}">']
    for lex in entries:
        lines.append("  <lexeme>")
        lines.extend(f"    <grapheme>{html.escape(g, quote=False)}</grapheme>" for g in lex["graphemes"])
        lines.append(f"    <phoneme>{html.escape(lex['ipa'], quote=False)}</phoneme>")
        lines.append("  </lexeme>")
    lines.append("</lexicon>")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- CLI


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    lexicon_help = "the renderer's EchoNarrationResources directory (holds us_gold.json and us_silver.json)"
    p_scan = sub.add_parser("scan", help="list pronunciation candidates in narrated text")
    p_scan.add_argument("--epub", required=True, type=Path)
    p_scan.add_argument("--out", type=Path, help="write JSON here instead of stdout")
    p_scan.add_argument("--lexicon-dir", type=Path, help=lexicon_help + "; adds words Echo would guess")
    p_apply = sub.add_parser("apply", help="embed decisions into a new EPUB")
    p_apply.add_argument("--epub", required=True, type=Path)
    p_apply.add_argument("--decisions", required=True, type=Path)
    p_apply.add_argument("--out", required=True, type=Path)
    p_apply.add_argument("--report", type=Path, help="write the embedded decisions as JSON")
    p_apply.add_argument("--lexicon-dir", type=Path, help=lexicon_help + "; also checks word coverage")
    p_check = sub.add_parser("check", help="the narration gate")
    p_check.add_argument("--epub", required=True, type=Path)
    p_check.add_argument("--lexicon-dir", type=Path,
                         help=lexicon_help + "; default $ECHO_RESOURCE_DIR, then the installed renderer "
                              "named by $APPROVED_ECHO_PRONUNCIATION_SHA")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exit_:
        return 0 if exit_.code == 0 else 64
    try:
        if args.command == "scan":
            lexicon = RendererLexicon.load(find_lexicon_dir(args.lexicon_dir)) if args.lexicon_dir else None
            rows = scan(Epub(args.epub), lexicon)
            payload = json.dumps(rows, ensure_ascii=False, indent=1) + "\n"
            if args.out:
                args.out.write_text(payload, encoding="utf-8")
            else:
                sys.stdout.write(payload)
            names = ("mandatory", "watch", "token", "caps", "hyphen-initialism", "fallback")
            kinds = {k: sum(1 for r in rows if r["kind"] == k) for k in names}
            open_mandatory = sum(1 for r in rows if r["kind"] == "mandatory" and not r["annotated"])
            print(f"candidates: {kinds}; heteronyms without IPA: {open_mandatory}", file=sys.stderr)
            if lexicon is None:
                print("words Echo would guess aren't listed; pass --lexicon-dir to add them", file=sys.stderr)
            return 0
        if args.command == "apply":
            if args.out.resolve() == args.epub.resolve():
                print("apply writes a new EPUB; --out must differ from --epub", file=sys.stderr)
                return 64
            lexicon = RendererLexicon.load(find_lexicon_dir(args.lexicon_dir)) if args.lexicon_dir else None
            try:
                report, warnings = apply(Epub(args.epub), load_decisions(args.decisions), args.out,
                                         lexicon=lexicon)
            except CheckFailed as failed:
                for line in failed.errors:
                    print(f"ERROR {line}", file=sys.stderr)
                print(f"pronunciation check failed with {len(failed.errors)} error(s); nothing written",
                      file=sys.stderr)
                return 1
            for line in warnings:
                print(f"warning {line}", file=sys.stderr)
            if args.report:
                args.report.write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            occurrences = sum(1 for r in report if r["kind"] == "occurrence")
            print(f"embedded {occurrences} occurrence and {len(report) - occurrences} token readings; "
                  f"wrote {args.out}")
            if lexicon is None:
                print("word coverage wasn't checked; run check (it finds the renderer lexicon) before "
                      "narration", file=sys.stderr)
            return 0
        errors, warnings = check(Epub(args.epub),
                                 lambda: RendererLexicon.load(find_lexicon_dir(args.lexicon_dir)))
        for line in warnings:
            print(f"warning {line}", file=sys.stderr)
        for line in errors:
            print(f"ERROR {line}", file=sys.stderr)
        if errors:
            print(f"pronunciation check failed: {len(errors)} error(s) in {args.epub}", file=sys.stderr)
            return 1
        print(f"pronunciation check passed: {args.epub}")
        return 0
    except InputError as error:
        print(str(error), file=sys.stderr)
        return 65


if __name__ == "__main__":
    raise SystemExit(main())
