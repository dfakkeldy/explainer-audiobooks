"""Pronunciation hooks for the EPUB only (the PDF never changes).

Reads src/pronunciations.yaml (optional):

    lang: en-US                  # the lexicon's language (default: book.yaml lang)
    lexicon_file: names.pls      # where lexicon entries go (beside the OPF)
    entries:
      - word: Pandoc             # a whole word or phrase, as printed
        ipa: ˈpændɑk             # standard IPA, no /slashes/ or [brackets], no syllable dots
        case: insensitive        # default sensitive (also matches "pandoc")
        forms: {"pandoc's": ˈpændɑks}   # other spellings, each with its own IPA
        lexicon: false           # true: also list it in names.pls (single-pronunciation names only)
        inline: true             # false: lexicon only, no inline spans
        expect: {public: 3}      # optional: exact inline count per edition (or one number); else the build fails
      - match: 'I have (read) it'    # a regex with context; group 1 (if any) is the annotated text
        ipa: ɹɛd

Inline annotations follow the Echo EPUB contract (epub-pronunciation.md in the
echo-narration skill): <span ssml:ph="…">word</span> with ssml:alphabet on the
root, whole words inside one text run of one paragraph or heading, never inside
links, code, captions, images or head content, never nested. Words whose sense
changes the sound (content, record, read …) need a `match` with context and are
never put in a lexicon.
"""
import os, re, sys
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import BOOK, SRC, load_yaml  # noqa: E402

PATH = os.path.join(SRC, "pronunciations.yaml")
SSML_NS = "http://www.w3.org/2001/10/synthesis"
PLS_NS = "http://www.w3.org/2005/01/pronunciation-lexicon"
# Spellings whose pronunciation depends on sense or tense: occurrence-specific only.
AMBIGUOUS = {"content", "record", "read", "lead", "wind", "bow", "wound", "tear", "minute", "live", "present",
             "object", "produce", "learned", "blessed", "close", "desert", "refuse", "row", "use", "contract", "permit"}
NO_WRAP = {"a", "code", "pre", "kbd", "samp", "script", "style", "svg", "math", "figcaption", "img", "title", "head", "nav"}
BAD_TEXT = set("[]()/")
APOS = "['’]"


def _word_rx(word, flags):
    body = re.sub(r"\\?['’]", lambda m: APOS, re.escape(word))     # either apostrophe matches either
    return re.compile(r"(?<![\w'’\-])" + body + r"(?![\w\-]|" + APOS + r"\w)", flags)


def _check_ipa(ipa, where):
    if not ipa or not str(ipa).strip():
        return f"{where}: empty ipa"
    ipa = str(ipa)
    if len(ipa) > 300:
        return f"{where}: ipa longer than 300 characters"
    if re.search(r"[/\[\]]", ipa):
        return f"{where}: ipa '{ipa}' has slash or bracket delimiters; give the bare IPA"
    if "." in ipa:
        return f"{where}: ipa '{ipa}' has syllable dots, which Echo rejects"
    if re.search(r"[A-Z]", ipa):
        return f"{where}: ipa '{ipa}' has capital letters (Kokoro shorthand); use standard IPA"
    if not re.search(r"[^\sˈˌ]", ipa):
        return f"{where}: ipa '{ipa}' has no speech symbols"
    return None


class Pronunciations:
    def __init__(self, edition):
        self.edition = edition
        data = load_yaml(PATH, None)
        if isinstance(data, list):
            data = {"entries": data}
        self.data = data or {}
        self.lang = self.data.get("lang", BOOK.get("lang", "en"))
        self.lexicon_file = self.data.get("lexicon_file", "names.pls")
        self.rules = []          # (regex, group, ipa, alphabet, entry_index)
        self.lex = []            # (regex, ipa, declared spelling, entry_index)
        self.entries = self.data.get("entries") or []
        self.counts = {}         # entry index -> inline annotations made
        self.seen = {}           # entry index -> {spelling: ipa} actually matched (for the lexicon)
        self.report = []         # (doc, entry word, text, context)
        errs = []
        for i, e in enumerate(self.entries):
            where = f"pronunciations.yaml entry {i + 1} ({e.get('word') or e.get('match')})"
            flags = re.I if str(e.get("case", "sensitive")).lower().startswith("insens") else 0
            alpha = e.get("alphabet", self.data.get("alphabet", "ipa"))
            forms = {**({e["word"]: e["ipa"]} if e.get("word") else {}), **(e.get("forms") or {})}
            for spelling, ipa in forms.items():
                err = _check_ipa(ipa, f"{where} '{spelling}'")
                if err:
                    errs.append(err)
                if BAD_TEXT & set(spelling):
                    errs.append(f"{where}: '{spelling}' contains one of []()/ which Echo can't annotate")
                if spelling.lower().strip("'’") in AMBIGUOUS:
                    errs.append(f"{where}: '{spelling}' sounds different by sense; use `match:` with its context for each occurrence")
            if e.get("match"):
                if e.get("lexicon"):
                    errs.append(f"{where}: a context match can't go in the lexicon")
                err = _check_ipa(e.get("ipa"), where)
                if err:
                    errs.append(err)
                try:
                    rx = re.compile(e["match"], flags)
                except re.error as ex:
                    errs.append(f"{where}: bad regex: {ex}")
                    continue
                if e.get("inline", True):
                    self.rules.append((rx, 1 if rx.groups else 0, str(e["ipa"]), alpha, i))
            elif e.get("word"):
                for spelling, ipa in forms.items():
                    rx = _word_rx(spelling, flags)
                    if e.get("inline", True):
                        self.rules.append((rx, 0, str(ipa), alpha, i))
                    if e.get("lexicon"):
                        if alpha != "ipa":
                            errs.append(f"{where}: the lexicon is IPA only")
                        self.lex.append((rx, str(ipa), spelling, i))
            else:
                errs.append(f"{where}: needs `word:` or `match:`")
        if errs:
            sys.exit("pronunciations.yaml:\n  " + "\n  ".join(errs))

    def __bool__(self):
        return bool(self.rules or self.lex)

    # ------------------------------------------------------------ inline
    def find(self, text):
        """Non-overlapping matches, leftmost-longest: (start, end, ipa, alphabet, entry)."""
        cands = []
        for rx, grp, ipa, alpha, i in self.rules:
            for m in rx.finditer(text):
                st, en = m.span(grp)
                if en > st:
                    cands.append((st, -(en - st), en, ipa, alpha, i))
        cands.sort()
        out, last = [], -1
        for st, _, en, ipa, alpha, i in cands:
            if st >= last:
                out.append((st, en, ipa, alpha, i))
                last = en
        return out

    def apply(self, soup, doc, frag):
        """Wrap matches in <span ssml:ph>. Returns the number of spans added."""
        n = 0
        for s in list(soup.find_all(string=True)):
            if any(p.name in NO_WRAP or p.has_attr("ssml:ph") for p in s.parents):
                continue
            text = str(s)
            hits = self.find(text)
            if not hits:
                continue
            pieces, pos = [], 0
            for st, en, ipa, alpha, i in hits:
                seg = text[st:en]
                if (st and re.match(r"\w", text[st - 1])) or (en < len(text) and re.match(r"\w", text[en])):
                    sys.exit(f"pronunciations.yaml entry {i + 1}: match «{seg}» in {doc} is part of a longer word")
                if BAD_TEXT & set(seg):
                    sys.exit(f"pronunciations.yaml entry {i + 1}: «{seg}» contains one of []()/")
                a = "" if alpha == "ipa" else f' ssml:alphabet="{escape(alpha, quote=True)}"'
                pieces.append(escape(text[pos:st]))
                pieces.append(f'<span ssml:ph="{escape(ipa, quote=True)}"{a}>{escape(seg)}</span>')
                pos = en
                n += 1
                self.counts[i] = self.counts.get(i, 0) + 1
                block = next((p for p in s.parents if p.name in ("p", "li", "td", "th", "dd", "dt", "h1", "h2", "h3", "h4", "h5", "h6")), None)
                ctx = re.sub(r"\s+", " ", (block or s.parent).get_text())
                self.report.append((doc, seg, ipa, ctx))
            pieces.append(escape(text[pos:]))
            s.replace_with(frag("".join(pieces)))
        return n

    # ------------------------------------------------------------ lexicon
    def lexicon_hits(self, text):
        """Spellings of lexicon entries in text, case as printed."""
        hits = []
        for rx, ipa, spelling, i in self.lex:
            for m in rx.finditer(text):
                hits.append((m.group(0), ipa, i))
        return hits

    def note_lexicon(self, text):
        found = self.lexicon_hits(text)
        for spelling, ipa, i in found:
            self.seen.setdefault(i, {})[spelling] = ipa
        return bool(found)

    def pls(self):
        """names.pls: one lexeme per phoneme, graphemes as printed. None when there is no lexicon."""
        if not self.lex:
            return None
        by_ipa, owner = {}, {}
        for rx, ipa, spelling, i in self.lex:
            printed = sorted(sp for sp, ip in self.seen.get(i, {}).items() if ip == ipa)
            gs = by_ipa.setdefault(ipa, [])
            for g in [spelling] + printed:          # as declared, and as printed (case, curly apostrophes)
                if g in owner and owner[g] != ipa:
                    sys.exit(f"pronunciations.yaml: '{g}' has two lexicon pronunciations ({owner[g]}, {ipa})")
                if len(g) > 200:
                    sys.exit(f"pronunciations.yaml: grapheme '{g[:40]}…' is longer than 200 characters")
                owner[g] = ipa
                if g not in gs:
                    gs.append(g)
        lex = "".join(f"  <lexeme>\n{''.join(f'    <grapheme>{escape(g)}</grapheme>{chr(10)}' for g in gs)}"
                      f"    <phoneme>{escape(ipa)}</phoneme>\n  </lexeme>\n" for ipa, gs in by_ipa.items())
        xml = (f'<?xml version="1.0" encoding="UTF-8"?>\n<lexicon xmlns="{PLS_NS}" version="1.0" alphabet="ipa" '
               f'xml:lang="{escape(self.lang)}">\n{lex}</lexicon>\n')
        if len(xml.encode("utf-8")) > 1024 * 1024:
            sys.exit("pronunciations.yaml: the lexicon is over 1 MiB")
        return xml

    # ------------------------------------------------------------ after the build
    def verify(self):
        """Fail on entries whose `expect` count doesn't match; warn on entries that matched nothing."""
        errs = []
        for i, e in enumerate(self.entries):
            exp = e.get("expect")
            if isinstance(exp, dict):
                exp = exp.get(self.edition)
            got = self.counts.get(i, 0)
            name = e.get("word") or e.get("match")
            if exp is not None and got != int(exp):
                errs.append(f"entry {i + 1} ({name}): expected {exp} inline annotations in {self.edition}, made {got}")
            elif e.get("inline", True) and not got and exp is None:
                print(f"[{self.edition}] note: pronunciation '{name}' matched nothing in this edition", file=sys.stderr)
        if errs:
            sys.exit("pronunciations.yaml:\n  " + "\n  ".join(errs))

    def write_report(self, path):
        lines = [f"# Pronunciation annotations: {self.edition} edition", "",
                 "Embedded in the EPUB only. Check each in context; an annotated paragraph skips Echo's text",
                 "normalisation, so check its abbreviations and numbers too (flagged below).", ""]
        for doc, seg, ipa, ctx in self.report:
            flag = " **check abbreviations/numbers in this block**" if re.search(r"\d|\b[A-Z]{2,}\b", ctx) else ""
            lines.append(f"- `{doc}` «{seg}» → `{ipa}`{flag}: {ctx[:220]}")
        for i, sp in sorted(self.seen.items()):
            lines.append(f"- lexicon entry {i + 1}: printed as {', '.join(sorted(sp))}")
        with open(path, "w") as f:
            f.write("\n".join(lines) + "\n")
