#!/usr/bin/env python3
"""Embed and check IPA pronunciations in an EPUB for Echo narration.

  scan   list every pronunciation candidate in the narrated text, with context
  apply  embed authored decisions (inline IPA, token readings, a PLS lexicon)
         into a new EPUB, then run `check` on it
  check  the narration gate: fail when narrated text lacks required IPA or
         breaks Echo's epub.*.ipa-v1 annotation contract

Narrated text is the body of every spine document that isn't `linear="no"` and
isn't the nav document. The rules follow references/epub-pronunciation.md and
three traps found in production:

- A lexicon grapheme matches inside dotted or hyphenated tokens (`md` inside
  `open-loops.md`), and synthesis then fails mid-render.
- An annotated block skips Echo's text expansion, so numerals and file names
  in it need their own readings.
- An inline span whose text contains a slash makes Echo import nothing at all.

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
whole-token use of their text inside blocks that carry other annotations.
Exit codes: 0 pass, 1 check failed, 64 usage, 65 unreadable input.
"""
from __future__ import annotations

import argparse
import html
import json
import posixpath
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

OPF_NS = "http://www.idpf.org/2007/opf"
CONTAINER_NS = "urn:oasis:names:tc:opendocument:xmlns:container"
SSML_NS = "http://www.w3.org/2001/10/synthesis"
PLS_NS = "http://www.w3.org/2005/01/pronunciation-lexicon"
XHTML_TYPES = {"application/xhtml+xml"}

# Every occurrence must carry an inline reading: each spelling has two
# pronunciations that depend on sense or tense.
MANDATORY = ("re-read", "reread", "contents", "content", "records", "record", "read")
# Other spellings whose sound depends on meaning; `scan` lists them for review.
WATCH = (
    "lead", "leads", "live", "lives", "close", "closes", "minute", "minutes", "wind", "wound",
    "tear", "tears", "present", "presents", "object", "objects", "produce", "project", "projects",
    "use", "uses", "used", "separate", "estimate", "estimates", "update", "updates", "permit",
    "conduct", "contract", "desert", "refuse", "progress", "subject", "perfect", "alternate",
    "duplicate", "row", "rows", "resume", "digest", "deliberate", "graduate", "advocate",
    "associate", "moderate", "appropriate", "learned", "blessed", "aged", "bass", "polish",
    "Polish", "address", "addresses", "invite", "bow", "bows", "does", "dove", "sow",
)
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
MANDATORY_RX = re.compile(WORD_EDGE_L + "(" + "|".join(map(re.escape, MANDATORY)) + ")" + WORD_EDGE_R, re.I)


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


# ---------------------------------------------------------------- check


def check(epub: Epub) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    narrated_words = sum(len(d.visible_text().split()) for d in epub.docs.values())
    if not narrated_words:
        return errors, ["no narrated text found; nothing to pronounce"]
    graphemes = {word for _, entries in epub.lexicons for g, _ in entries for word in [g, *g.split()]}
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
            for m in MANDATORY_RX.finditer(text):
                si, _ = where[m.start()]
                seg = doc.segments[si]
                if seg.annotated:
                    continue
                if seg.unsupported:
                    errors.append(f"{name}: '{m.group(0)}' in <{seg.unsupported}> can't carry IPA; reword it "
                                  f"or move it out: {context_of(text, m.start(), m.end())}")
                else:
                    errors.append(f"{name}: '{m.group(0)}' has no IPA reading: {context_of(text, m.start(), m.end())}")
            if not block.has_span:
                continue
            for m in RAW_TOKEN.finditer(text):
                si, _ = where[m.start()]
                if doc.segments[si].annotated:
                    continue
                errors.append(f"{name}: '{m.group(0)}' sits in an annotated block, where Echo skips text "
                              f"expansion; add a reading for it: {context_of(text, m.start(), m.end())}")
            for m in CAPS.finditer(text):
                si, _ = where[m.start()]
                if not doc.segments[si].annotated and m.group(0) not in graphemes:
                    warnings.append(f"{name}: '{m.group(0)}' sits unexpanded in an annotated block; "
                                    "consider a lexicon entry")
        for alt in doc.alts:
            for m in MANDATORY_RX.finditer(alt):
                errors.append(f"{name}: '{m.group(0)}' in image alt text can't carry IPA; reword it: "
                              f"{context_of(alt, m.start(), m.end())}")
    for href, entries in epub.lexicons:
        for grapheme, phoneme in entries:
            problem = check_ipa(phoneme)
            if problem:
                errors.append(f"{href}: lexeme {grapheme!r}: {problem}")
            if grapheme.lower() in MANDATORY:
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


def scan(epub: Epub) -> list[dict]:
    watch = re.compile(WORD_EDGE_L + "(" + "|".join(map(re.escape, sorted(set(WATCH), key=len, reverse=True)))
                       + ")" + WORD_EDGE_R)
    rows = []
    for name, doc in epub.docs.items():
        for bi, block in enumerate(doc.blocks.values()):
            text, where = doc.block_text(block)
            for kind, rx in (("mandatory", MANDATORY_RX), ("watch", watch), ("token", RAW_TOKEN), ("caps", CAPS)):
                for m in rx.finditer(text):
                    seg = doc.segments[where[m.start()][0]]
                    rows.append({"doc": posixpath.basename(name), "block": bi, "tag": block.tag, "kind": kind,
                                 "word": m.group(0), "annotated": seg.annotated,
                                 "surface": seg.unsupported or block.tag,
                                 "context": " ".join(text[max(0, m.start() - 50):m.end() + 50].split())})
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
            elif g.lower() in MANDATORY:
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


def apply(epub: Epub, decisions: dict, out: Path, lexicon_name: str = "names.pls", *, validate: bool = True) -> tuple[list[dict], list[str]]:
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
    for name, doc in epub.docs.items():
        doc_edits = edits.get(name, {})
        for block in doc.blocks.values():
            shared_match = any(word_rx(entry["text"]).search(doc.segments[si].text)
                               for si in block.segments for entry in dictionary["entries"])
            if not block.has_span and not any(si in doc_edits for si in block.segments) and not shared_match:
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
    errors, warnings = check(Epub(tmp)) if validate else ([], [])
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
    p_scan = sub.add_parser("scan", help="list pronunciation candidates in narrated text")
    p_scan.add_argument("--epub", required=True, type=Path)
    p_scan.add_argument("--out", type=Path, help="write JSON here instead of stdout")
    p_apply = sub.add_parser("apply", help="embed decisions into a new EPUB")
    p_apply.add_argument("--epub", required=True, type=Path)
    p_apply.add_argument("--decisions", required=True, type=Path)
    p_apply.add_argument("--out", required=True, type=Path)
    p_apply.add_argument("--report", type=Path, help="write the embedded decisions as JSON")
    p_check = sub.add_parser("check", help="the narration gate")
    p_check.add_argument("--epub", required=True, type=Path)
    try:
        args = parser.parse_args(argv)
    except SystemExit as exit_:
        return 0 if exit_.code == 0 else 64
    try:
        if args.command == "scan":
            rows = scan(Epub(args.epub))
            payload = json.dumps(rows, ensure_ascii=False, indent=1) + "\n"
            if args.out:
                args.out.write_text(payload, encoding="utf-8")
            else:
                sys.stdout.write(payload)
            kinds = {k: sum(1 for r in rows if r["kind"] == k) for k in ("mandatory", "watch", "token", "caps")}
            open_mandatory = sum(1 for r in rows if r["kind"] == "mandatory" and not r["annotated"])
            print(f"candidates: {kinds}; content/record/read without IPA: {open_mandatory}", file=sys.stderr)
            return 0
        if args.command == "apply":
            if args.out.resolve() == args.epub.resolve():
                print("apply writes a new EPUB; --out must differ from --epub", file=sys.stderr)
                return 64
            try:
                report, warnings = apply(Epub(args.epub), load_decisions(args.decisions), args.out)
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
            return 0
        errors, warnings = check(Epub(args.epub))
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
