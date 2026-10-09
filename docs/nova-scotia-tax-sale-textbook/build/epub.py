#!/usr/bin/env python3
"""Build each edition's EPUB 3 from the same source as its PDF.

    .venv/bin/python build/epub.py [edition ...]      (build.py runs this after each PDF)

The chapters go through the same pandoc load, edition filtering and block
conversion as the PDF (build.add_chapter, linkify, enrich), in the edition's
`contents` order. Each chapter opening starts a new XHTML document; the blocks
are then made reflowable: side heads become a label line above their text,
source notes labelled asides, cards keep their header and meters. The page
footers become popup notes: the first use of each glossary word in a chapter
links to a note at the chapter's end, which links to the full glossary. Optional
src/pronunciations.yaml adds ssml:ph spans and a names.pls lexicon (EPUB only;
see pronounce.py). Writes the .epub beside the PDF and the unzipped package to
out/<edition>-epub/ for inspection.
"""
import io, os, posixpath, re, shutil, subprocess, sys, uuid, zipfile
from datetime import datetime, timezone
from html import escape
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B  # noqa: E402
from common import BOOK, CHAPTERS, GLOSSARY, OUT, ROOT, SRC, editions, epub_file, epub_settings, out_path  # noqa: E402
from pronounce import Pronunciations, SSML_NS  # noqa: E402

T, L = B.T, B.L
E = epub_settings()
MEDIA = {".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif",
         ".webp": "image/webp"}
DROP_CLS = {"blk", "main", "full", "rb", "atomic", "first", "sec-gap", "cont", "keep-group", "nolabel", "no-gloss", "acr-only"}
KEEP_ATTRS = {"id", "class", "href", "src", "alt", "title", "lang", "colspan", "rowspan", "role", "style", "scope", "headers",
              "start", "type", "reversed", "value", "width", "height", "dir", "cite", "datetime"}
NAV_PROP, NCX_ATTR = ' properties="nav"', ' toc="ncx"'
NO_NOTEREF = {"a", "h1", "h2", "h3", "h4", "h5", "h6", "header", "nav", "figcaption"}
CHROMES = [os.environ.get("CHROME"), "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
           "/Applications/Chromium.app/Contents/MacOS/Chromium", "/usr/bin/google-chrome", "/usr/bin/google-chrome-stable",
           "/usr/bin/chromium", "/usr/bin/chromium-browser"]


class Doc:
    def __init__(self, id, href, kind, title=""):
        self.id, self.href, self.kind, self.title = id, href, kind, title
        self.blocks, self.soup = [], None
        self.ssml = self.pls = False
        self.epub_type = None


# ====================================================================== documents
def split_docs(edition, cfg):
    """Docs in spine order (chapters as blocks, plus cover/nav/glossary markers) and the contents entries."""
    F = B.Flow()
    docs, cur = [], None

    def new_chapter():
        d = Doc(f"ch{sum(1 for x in docs if x.kind == 'chapter') + 1:02d}", "", "chapter")
        d.href = d.id + ".xhtml"
        docs.append(d)
        return d

    for item in cfg["contents"]:
        if item == "@cover":
            docs.append(Doc("cover", "cover.xhtml", "cover", L.get("cover", "Cover")))
            cur = None
        elif item == "@toc":
            docs.append(Doc("nav", "nav.xhtml", "nav", L["contents"]))
            cur = None
        elif item == "@glossary":
            docs.append(Doc("glossary", "glossary.xhtml", "glossary", L["glossary"]))
            F.toc.append((1, "glossary", escape(L["glossary"])))
            cur = None
        elif item.startswith("@"):
            sys.exit(f"unknown contents entry {item}")
        else:
            start = len(F.blocks)
            B.add_chapter(F, os.path.join(CHAPTERS, item), edition)
            for b in F.blocks[start:]:
                if b.startswith('<div class="rh-set"'):
                    continue
                if re.match(r'<div class="blk full chapter-head', b) or cur is None:
                    cur = new_chapter()
                cur.blocks.append(b)
    for d in docs:
        if d.kind == "chapter":
            m = re.search(r'<h1 class="ch-title">(.*?)</h1>', d.blocks[0], re.S)
            d.title = B.frag(m.group(1)).get_text().strip() if m else BOOK.get("title", "")
    return docs, F.toc


def new(soup, name, cls=None, **attrs):
    t = soup.new_tag(name)
    if cls:
        t["class"] = cls if isinstance(cls, list) else cls.split()
    for k, v in attrs.items():
        t[k.replace("_", "-") if k.startswith("aria") else k] = v
    return t


def move_children(src, dst):
    for c in list(src.contents):
        dst.append(c.extract())
    return dst


def reflow(soup):
    """Turn the paginator's blocks into plain reflowable XHTML structure."""
    for d in soup.select("div.chapter-head"):
        h = new(soup, "header", "chapter-head", id=d["id"])
        lab, kick, h1 = d.select_one(".ch-label"), d.select_one(".ch-kicker"), d.select_one("h1")
        if lab:
            h.append(move_children(lab, new(soup, "p", "ch-label")))
        if kick and kick.get_text(strip=True):
            h.append(move_children(kick, new(soup, "p", "ch-kicker")))
        h.append(h1.extract())
        d.replace_with(h)
    for d in soup.select("div.rb"):
        lab = d.find("div", class_="rail-label", recursive=False)
        if "src-wrap" in d.get("class", []):
            aside = new(soup, "aside", "source-note", aria_label=lab.get_text().strip())
            aside.append(move_children(lab, new(soup, "p", "side-head")))
            lab.decompose()
            for src in d.select(".src"):
                src.unwrap()
            move_children(d, aside)
            d.replace_with(aside)
        else:
            if lab is not None:
                lab.replace_with(move_children(lab, new(soup, "p", "side-head")))
            if "opener" in d.get("class", []):       # objectives, key terms, research chain: keep the box
                d["class"] = [c for c in d["class"] if c not in DROP_CLS]
            else:
                d.unwrap()
    for d in soup.select("div.card-wrap"):
        head = d.select_one(".card-head")
        head["id"] = d["id"]
        for sel in (".card-code", ".card-action > span"):   # keep words apart for readers and speech
            for sp in head.select(sel):
                sp.insert_after(" ")
        for r in head.select(".card-ratings"):
            del r["style"]
        d.unwrap()
    for d in soup.select("div.keep-group"):
        d.unwrap()
    for d in soup.select(".fig-terms"):          # PDF footers only; the EPUB's notes come from the text
        d.decompose()


def clean(soup):
    """Drop layout classes and attributes the EPUB doesn't use."""
    for el in soup.find_all(True):
        for k in list(el.attrs):
            if not (k in KEEP_ATTRS or k.startswith(("aria-", "epub:", "ssml:"))):
                del el[k]
        if "class" in el.attrs:
            cls = [c for c in el["class"] if c not in DROP_CLS]
            if cls:
                el["class"] = cls
            else:
                del el["class"]


def gloss_ids():
    ids, used = {}, set()
    for g in GLOSSARY:
        base = "gl-" + (re.sub(r"[^A-Za-z0-9]+", "-", g["key"]).strip("-") or "term")
        i, n = base, 2
        while i in used:
            i, n = f"{base}-{n}", n + 1
        used.add(i)
        ids[g["key"]] = i
    return ids


def definition(g):
    return escape(g["short"]) + escape(B.joiner(g)) + escape(g.get("more") or "")


def noterefs(doc, gloss, gid):
    """First use of each glossary word in the chapter -> a noteref to a popup note; acronyms elsewhere -> <abbr>."""
    soup, seen = doc.soup, []
    for sp in soup.select("span.gt"):
        key = sp["data-t"]
        g = gloss.entries[key]
        blocked = any(p.name in NO_NOTEREF or {"side-head", "card-top", "ch-label"} & set(p.get("class") or [])
                      for p in sp.parents)
        if key not in seen and not blocked:
            seen.append(key)
            a = new(soup, "a", "gt-ref", href="#n-" + gid[key], id="r-" + gid[key], role="doc-noteref")
            a["epub:type"] = "noteref"
            sp.replace_with(move_children(sp, a))
        elif g["kind"] == "acronym":
            sp.replace_with(move_children(sp, new(soup, "abbr", title=g["short"])))
        else:
            sp.unwrap()
    if not seen:
        return
    label = L.get("epub_notes", "Words in this chapter")
    notes = [f'<aside epub:type="footnote" role="doc-footnote" class="gloss-note" id="n-{gid[k]}"><p>'
             f'<a href="glossary.xhtml#{gid[k]}"><dfn>{escape(k)}</dfn></a> {definition(gloss.entries[k])}</p></aside>' for k in seen]
    sec = B.frag(f'<section class="footnotes" epub:type="footnotes" aria-label="{escape(label, quote=True)}">'
                 f'<p class="fn-label">{escape(label)}</p>{"".join(notes)}</section>')
    B.linkify(sec)
    soup.append(sec)


# ====================================================================== cover
def find_chrome():
    return next((p for p in CHROMES if p and os.path.exists(p)), None)


def render_cover(edition, cfg, dest_stem):
    """The PDF's cover page as an image, rendered by headless Chrome. Returns (path, media type) or None."""
    chrome = find_chrome()
    if not chrome:
        return None
    img = BOOK.get("cover_image")
    src = B.rel_from_out(os.path.join(ROOT, img)) if img else None
    html = out_path(edition, "epub-cover.html")
    with open(html, "w") as f:
        f.write(f'<!doctype html><html><head><meta charset="utf-8"><style>{B.fonts_css()}html,body{{margin:0;background:#fff}}'
                f'</style></head><body>{T.cover(BOOK, edition, cfg, src, BOOK.get("cover_alt", ""))}</body></html>')
    png = dest_stem + ".png"
    scale = E.get("cover_scale", 1.5)
    args = [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
            "--font-render-hinting=none", "--virtual-time-budget=5000", f"--window-size={T.W},{T.H}",
            f"--force-device-scale-factor={scale}", f"--screenshot={png}", "file://" + os.path.abspath(html)]
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        args.insert(1, "--no-sandbox")
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode or not os.path.exists(png):
        print(f"[{edition}] warning: Chrome couldn't render the cover ({r.stderr.strip()[-200:]}); using a text cover", file=sys.stderr)
        return None
    magick = shutil.which("magick") or shutil.which("convert")
    if E.get("cover_format", "jpeg") in ("jpeg", "jpg") and magick:
        jpg = dest_stem + ".jpg"
        if subprocess.run([magick, png, "-quality", "88", jpg], capture_output=True).returncode == 0:
            os.remove(png)
            return jpg, "image/jpeg"
    return png, "image/png"


def raster(path, dest_stem):
    """An SVG as PNG (rsvg-convert or ImageMagick), for readers that want a raster cover."""
    png = dest_stem + ".png"
    for cmd in ([shutil.which("rsvg-convert"), "-w", "1600", "-o", png, path],
                [shutil.which("magick") or shutil.which("convert"), "-density", "192", path, png]):
        if cmd[0] and subprocess.run(cmd, capture_output=True).returncode == 0 and os.path.exists(png):
            return png
    return None


# ====================================================================== fonts
def parse_ranges(s):
    out = []
    for part in s.split(","):
        part = part.strip().upper().replace("U+", "")
        if "-" in part:
            a, b = part.split("-")
            out.append((int(a, 16), int(b, 16)))
        elif "?" in part:
            out.append((int(part.replace("?", "0"), 16), int(part.replace("?", "F"), 16)))
        elif part:
            out.append((int(part, 16), int(part, 16)))
    return out


def embed_fonts(chars):
    """Subsets of the static fonts fonts.py cut, limited to the characters the EPUB uses.
    Returns (css, [(zip name, bytes)])."""
    p = os.path.join(ROOT, "fonts", "fonts.css")
    if not E.get("embed_fonts", True) or not os.path.exists(p):
        if E.get("embed_fonts", True):
            print("warning: fonts/fonts.css missing (run build/fonts.py); the EPUB uses the reader's fonts", file=sys.stderr)
        return "", []
    from fontTools import subset
    faces = re.findall(r"@font-face\{(.*?)\}", open(p).read())
    faces.sort(key=lambda b: 1 if "-latin.ttf" in b else 0)   # basic Latin last: readers that ignore unicode-range use it
    css, files = [], []
    codes = {ord(c) for c in chars} | set(range(0x20, 0x7F))
    for body in faces:
        fam = re.search(r"font-family:'([^']+)'", body).group(1)
        style = re.search(r"font-style:(\w+)", body).group(1)
        weight = re.search(r"font-weight:(\d+)", body).group(1)
        url = re.search(r"url\('([^']+)'\)", body).group(1)
        rng = re.search(r"unicode-range:([^;]+)", body).group(1)
        ranges = parse_ranges(rng)
        want = {c for c in codes if any(a <= c <= b for a, b in ranges)}
        src = os.path.normpath(os.path.join(OUT, url))
        if not want or not os.path.exists(src):
            continue
        opts = subset.Options()
        opts.layout_features, opts.name_IDs, opts.name_languages, opts.notdef_outline = ["*"], ["*"], ["*"], True
        font = subset.load_font(src, opts)
        sub = subset.Subsetter(opts)
        sub.populate(unicodes=want)
        sub.subset(font)
        buf = io.BytesIO()
        subset.save_font(font, buf, opts)
        name = "fonts/" + os.path.basename(src)
        files.append((name, buf.getvalue()))
        css.append(f"@font-face {{ font-family:'{fam}'; font-style:{style}; font-weight:{weight}; "
                   f"src:url('{name}') format('truetype'); unicode-range:{rng.strip()}; }}")
    return "\n".join(css) + "\n", files


# ====================================================================== package
def xhtml(doc, body, lang, private_mark, pls_href=None):
    ns = f' xmlns:ssml="{SSML_NS}"' if doc.ssml else ""
    alpha = ' ssml:alphabet="ipa"' if doc.ssml else ""
    link = (f'\n<link rel="pronunciation" type="application/pls+xml" hreflang="{escape(pls_href[1])}" href="{escape(pls_href[0])}"/>'
            if doc.pls and pls_href else "")
    mark = f'<p class="private-mark">{escape(private_mark)}</p>\n' if private_mark else ""
    cls = ' class="cover"' if doc.kind == "cover" else ""
    et = f' epub:type="{doc.epub_type}"' if doc.epub_type else ""
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE html>\n'
            f'<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops"{ns} '
            f'xml:lang="{lang}" lang="{lang}"{alpha}>\n<head>\n<meta charset="utf-8"/>\n<title>{escape(doc.title)}</title>\n'
            f'<link rel="stylesheet" type="text/css" href="style.css"/>{link}\n</head>\n<body{cls}{et}>\n{mark}{body}\n</body>\n</html>\n')


def toc_tree(toc, depth, where):
    """Nested [(title_html, href, children)] from the flow's contents entries, to toc_depth."""
    root, stack = [], []
    for level, sid, title in toc:
        if level > depth or sid not in where:
            continue
        title = re.sub(r'(<span class="toc-code">.*?</span>)', r"\1 ", title)
        node = (title, f"{where[sid]}#{sid}", [])
        while stack and stack[-1][0] >= level:
            stack.pop()
        (stack[-1][1][2] if stack else root).append(node)
        stack.append((level, node))
    return root


def nav_ol(nodes):
    def title(t):
        s = B.frag(t)
        for a in s.find_all("a"):
            a.unwrap()
        return str(s)
    return "<ol>" + "".join(f'<li><a href="{escape(h, quote=True)}">{title(t)}</a>{nav_ol(c) if c else ""}</li>'
                            for t, h, c in nodes) + "</ol>"


def ncx(ident, title, nodes):
    n = [0]

    def points(ns):
        out = []
        for t, h, c in ns:
            n[0] += 1
            out.append(f'<navPoint id="np-{n[0]}" playOrder="{n[0]}"><navLabel><text>{escape(B.frag(t).get_text())}</text></navLabel>'
                       f'<content src="{escape(h, quote=True)}"/>{points(c)}</navPoint>')
        return "".join(out)
    body = points(nodes)
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">\n'
            f'<head><meta name="dtb:uid" content="{escape(ident)}"/><meta name="dtb:depth" content="2"/>'
            f'<meta name="dtb:totalPageCount" content="0"/><meta name="dtb:maxPageNumber" content="0"/></head>\n'
            f'<docTitle><text>{escape(title)}</text></docTitle>\n<navMap>{body}</navMap>\n</ncx>\n')


def source_time():
    """dcterms:modified: SOURCE_DATE_EPOCH, else the newest source file, so a rebuild of the same text is byte-identical."""
    if os.environ.get("SOURCE_DATE_EPOCH"):
        t = int(os.environ["SOURCE_DATE_EPOCH"])
    else:
        paths = [os.path.join(ROOT, "book.yaml")] + [os.path.join(dp, f) for dp, _, fs in os.walk(SRC) for f in fs]
        t = int(max(os.path.getmtime(p) for p in paths if os.path.exists(p)))
    return datetime.fromtimestamp(t, timezone.utc)


def metadata(edition, cfg, ident, modified, has_images, has_ssml):
    title = cfg.get("title", BOOK.get("title", "Book"))
    full = cfg.get("epub_title") or cfg.get("pdf_title") or title + ("" if len(editions()) == 1 else f" ({edition} edition)")
    sub = cfg.get("subtitle", BOOK.get("subtitle", ""))
    m = [f'<dc:identifier id="bookid">{escape(ident)}</dc:identifier>',
         f'<dc:title id="title">{escape(full)}</dc:title>', '<meta refines="#title" property="title-type">main</meta>']
    if sub:
        m += [f'<dc:title id="subtitle">{escape(sub)}</dc:title>', '<meta refines="#subtitle" property="title-type">subtitle</meta>']
    m.append(f'<dc:language>{escape(BOOK.get("lang", "en"))}</dc:language>')
    authors = BOOK.get("author") or BOOK.get("authors") or []
    for i, a in enumerate([authors] if isinstance(authors, str) else authors, 1):
        m += [f'<dc:creator id="creator-{i}">{escape(str(a))}</dc:creator>',
              f'<meta refines="#creator-{i}" property="role" scheme="marc:relators">aut</meta>']
    for key in ("publisher", "rights"):
        if cfg.get(key, BOOK.get(key)):
            m.append(f'<dc:{key}>{escape(str(cfg.get(key, BOOK.get(key))))}</dc:{key}>')
    blurb = cfg.get("blurb", BOOK.get("blurb"))
    if blurb:
        m.append(f'<dc:description>{escape(str(blurb).strip())}</dc:description>')
    m.append(f'<meta property="dcterms:modified">{modified.strftime("%Y-%m-%dT%H:%M:%SZ")}</meta>')
    feats = ["structuralNavigation", "tableOfContents", "readingOrder", "displayTransformability"]
    if has_images:
        feats.append("alternativeText")
    if has_ssml:
        feats.append("ttsMarkup")
    modes = ["textual"] + (["visual"] if has_images else [])
    summary = E.get("accessibility_summary") or (
        "Reflowable text with a contents list, a heading for every chapter and section, and a glossary: the first use of each "
        "term in a chapter links to its definition. Every image has a text alternative and every rating is given in words as "
        "well as on a meter, so nothing depends on colour or pictures alone."
        + (" Pronunciation markup guides text-to-speech for some names." if has_ssml else ""))
    m += [f'<meta property="schema:accessMode">{x}</meta>' for x in modes]
    m.append('<meta property="schema:accessModeSufficient">textual</meta>')
    m += [f'<meta property="schema:accessibilityFeature">{x}</meta>' for x in feats]
    m.append('<meta property="schema:accessibilityHazard">none</meta>')
    m.append(f'<meta property="schema:accessibilitySummary">{escape(summary)}</meta>')
    return full, m


def build_epub(edition, cfg):
    dest = epub_file(cfg)
    if not dest:
        return
    lang = BOOK.get("lang", "en")
    mark = cfg.get("private_mark", "")
    gloss = B.Glossary(GLOSSARY)
    gid = gloss_ids()
    P = Pronunciations(edition)
    docs, toc = split_docs(edition, cfg)
    chapters = [d for d in docs if d.kind == "chapter"]
    for d in chapters:
        d.soup = B.frag("\n".join(d.blocks))
        B.linkify(d.soup)
        B.enrich(d.soup, gloss)
        reflow(d.soup)
        sec = new(d.soup, "section", "chapter", role="doc-chapter")
        sec["epub:type"] = "chapter"
        for c in list(d.soup.contents):
            sec.append(c.extract())
        d.soup.append(sec)

    # images: copy into the package; every one needs a text alternative
    files, images, bad = [], {}, []
    for d in chapters:
        for img in d.soup.find_all("img"):
            src = img.get("src", "")
            if not (img.get("alt") or "").strip():
                bad.append(f"{d.title}: {src}")
            if re.match(r"^[a-z]+:", src):
                sys.exit(f"[{edition}] EPUB: remote or data image {src[:60]} (in {d.title}); save it in src/assets")
            path = os.path.normpath(os.path.join(OUT, src))
            if not os.path.exists(path):
                sys.exit(f"[{edition}] EPUB: image not found: {path}")
            if path not in images:
                ext = os.path.splitext(path)[1].lower()
                if ext not in MEDIA:
                    sys.exit(f"[{edition}] EPUB: unsupported image type {ext}: {path}")
                stem, n = os.path.splitext(os.path.basename(path))[0], 2
                name = f"images/{re.sub(r'[^A-Za-z0-9._-]+', '-', stem)}{ext}"
                while name in {v[0] for v in images.values()}:
                    name, n = f"images/{stem}-{n}{ext}", n + 1
                images[path] = (name, MEDIA[ext])
                files.append((name, open(path, "rb").read()))
            img["src"] = images[path][0]
    if bad:
        sys.exit(f"[{edition}] EPUB: every image needs alt text (the caption in ![caption](file)); missing:\n  " + "\n  ".join(bad))

    # links between documents
    where = {}
    for d in chapters:
        for el in d.soup.find_all(id=True):
            where[el["id"]] = d.href
    where["glossary"] = "glossary.xhtml"
    for d in chapters:
        for a in d.soup.select('a[href^="#"]'):
            target = a["href"][1:]
            if target not in where:
                print(f"[{edition}] warning: EPUB link to #{target} has no target in this edition; unlinked", file=sys.stderr)
                a.unwrap()
            elif where[target] != d.href:
                a["href"] = f"{where[target]}#{target}"

    # glossary: words used, popup notes, the glossary document
    used = set()
    for d in chapters:
        used |= B.used_terms(d.soup, gloss)
    for d in chapters:
        noterefs(d, gloss, gid)
    for d in docs:
        if d.kind == "glossary":
            rows = "".join(f'<dt epub:type="glossterm" id="{gid[g["key"]]}"><dfn>{escape(g["key"])}</dfn></dt>'
                           f'<dd epub:type="glossdef">{definition(g)}</dd>' for g in B.glossary_items(used))
            d.soup = B.frag(f'<section epub:type="glossary" role="doc-glossary" id="glossary"><h1 class="sec-title">{escape(L["glossary"])}</h1>'
                            f'<p class="sec-sub">{escape(L.get("epub_glossary_sub", "Every abbreviation and term this book explains."))}</p>'
                            f'<dl class="glossary">{rows}</dl></section>')
            B.linkify(d.soup)

    # pronunciation (EPUB only)
    for d in docs:
        if d.soup is not None and P:
            d.ssml = P.apply(d.soup, d.href, B.frag) > 0
            d.pls = P.note_lexicon(d.soup.get_text(" "))
    P.verify()
    pls = P.pls()

    # contents
    depth = BOOK.get("toc_depth", 2)
    tree = toc_tree(toc, depth, where)
    first_body = next((d for i, d in enumerate(docs) if d.kind == "chapter" and any(x.kind == "nav" for x in docs[:i])),
                      chapters[0] if chapters else None)
    marks = [("cover", "cover.xhtml", L.get("cover", "Cover"))] if any(d.kind == "cover" for d in docs) else []
    marks.append(("toc", "nav.xhtml#toc", L["contents"]))
    if first_body:
        marks.append(("bodymatter", first_body.href, first_body.title))
    if any(d.kind == "glossary" for d in docs):
        marks.append(("glossary", "glossary.xhtml", L["glossary"]))
    # no aria-label(ledby) on either nav: EPUBCheck 5 rejects them there (RSC-005); the h1 names the toc
    nav_body = (f'<nav epub:type="toc" role="doc-toc" id="toc"><h1 class="sec-title" id="toc-title">'
                f'{escape(L["contents"])}</h1>{nav_ol(tree)}</nav>\n<nav epub:type="landmarks" hidden="hidden"><ol>'
                + "".join(f'<li><a epub:type="{t}" href="{h}">{escape(x)}</a></li>' for t, h, x in marks) + "</ol></nav>")
    nav = next((d for d in docs if d.kind == "nav"), None) or Doc("nav", "nav.xhtml", "nav", L["contents"])

    # cover
    cover_img = None
    stem = out_path(edition, "epub-cover")
    title_full, meta = metadata(edition, cfg, cfg.get("epub_identifier") or E.get("identifier") or
                                "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, f"textbook-pdf/{BOOK.get('title', 'book')}/{edition}")),
                                source_time(), bool(images), any(d.ssml for d in docs))
    for d in docs:
        if d.kind != "cover":
            continue
        d.epub_type = "cover"
        title = cfg.get("title", BOOK.get("title", ""))
        sub = cfg.get("subtitle", BOOK.get("subtitle", ""))
        alt = f'{L.get("cover", "Cover")}: {title}' + (f". {sub}" if sub else "") + "."
        got = render_cover(edition, cfg, stem) if E.get("cover", "render") == "render" else None
        if got:
            cover_img = ("images/cover" + os.path.splitext(got[0])[1], got[1], got[0])
            body = f'<section class="cover-img" epub:type="cover"><img src="{cover_img[0]}" alt="{escape(alt, quote=True)}"/></section>'
        else:
            band = ""
            if BOOK.get("cover_image"):
                p = os.path.join(ROOT, BOOK["cover_image"])
                r = raster(p, stem) if p.lower().endswith(".svg") else p
                r = r or p
                ext = os.path.splitext(r)[1].lower()
                cover_img = ("images/cover" + ext, MEDIA[ext], r)
                band = f'<p class="cover-img"><img src="{cover_img[0]}" alt="{escape(BOOK.get("cover_alt") or alt, quote=True)}"/></p>'
            kicker = cfg.get("kicker", BOOK.get("kicker", ""))
            body = (f'<section class="cover-text" epub:type="cover">{band}<p class="kicker">{escape(kicker)}</p><h1>{escape(title)}</h1>'
                    f'<p class="subtitle">{escape(sub)}</p><p class="blurb">{escape(cfg.get("blurb", BOOK.get("blurb", "")))}</p>'
                    f'<p class="edition"><b>{escape(cfg.get("cover_line", f"{edition.capitalize()} edition"))}</b> {escape(BOOK.get("date", ""))}</p></section>')
        d.soup = B.frag(body)
    if cover_img:
        files.append((cover_img[0], open(cover_img[2], "rb").read()))

    # serialize the documents
    pls_href = (P.lexicon_file, P.lang) if pls else None
    texts = []
    out_docs = []
    for d in docs + ([] if any(x.kind == "nav" for x in docs) else [nav]):
        if d.kind == "nav":
            body = nav_body
        else:
            clean(d.soup)
            body = d.soup.decode(formatter="minimal")
        x = xhtml(d, body, lang, mark if d in docs else "", pls_href)
        try:
            ET.fromstring(x.encode("utf-8"))
        except ET.ParseError as ex:
            dump = out_path(edition, "bad-" + d.href)
            open(dump, "w").write(x)
            sys.exit(f"[{edition}] EPUB: {d.href} is not well-formed XML ({ex}); see {dump}")
        out_docs.append((d, x))
        texts.append(B.frag(body).get_text())
    font_css, font_files = embed_fonts("".join(texts) + mark + title_full)
    files += font_files
    css = font_css + T.epub_css()

    # the package document
    ident = re.search(r">([^<]+)</dc:identifier>", meta[0]).group(1)
    man = [f'<item id="{d.id}" href="{d.href}" media-type="application/xhtml+xml"{NAV_PROP if d.kind == "nav" else ""}/>'
           for d, _ in out_docs]
    man.append('<item id="css" href="style.css" media-type="text/css"/>')
    for i, (name, media) in enumerate(sorted(images.values())):
        man.append(f'<item id="img-{i + 1}" href="{name}" media-type="{media}"/>')
    if cover_img:
        man.append(f'<item id="cover-image" href="{cover_img[0]}" media-type="{cover_img[1]}" properties="cover-image"/>')
        meta.append('<meta name="cover" content="cover-image"/>')
    for i, (name, _) in enumerate(font_files):
        man.append(f'<item id="font-{i + 1}" href="{name}" media-type="font/ttf"/>')
    if pls:
        man.append(f'<item id="pronunciation-names" href="{P.lexicon_file}" media-type="application/pls+xml"/>')
    use_ncx = E.get("ncx", True)
    if use_ncx:
        man.append('<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>')
    spine = "".join(f'<itemref idref="{d.id}"/>' for d, _ in out_docs if d in docs)
    opf = (f'<?xml version="1.0" encoding="UTF-8"?>\n<package xmlns="http://www.idpf.org/2007/opf" version="3.0" '
           f'unique-identifier="bookid" xml:lang="{lang}">\n<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">\n'
           + "\n".join(meta) + "\n</metadata>\n<manifest>\n" + "\n".join(man) + "\n</manifest>\n"
           f'<spine{NCX_ATTR if use_ncx else ""}>{spine}</spine>\n</package>\n')

    pkg = [("META-INF/container.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<container version="1.0" '
            'xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" '
            'media-type="application/oebps-package+xml"/></rootfiles></container>\n'),
           ("OEBPS/content.opf", opf), ("OEBPS/style.css", css)]
    pkg += [("OEBPS/" + d.href, x) for d, x in out_docs]
    if use_ncx:
        pkg.append(("OEBPS/toc.ncx", ncx(ident, title_full, tree)))
    if pls:
        pkg.append(("OEBPS/" + P.lexicon_file, pls))
    pkg += [("OEBPS/" + n, b) for n, b in files]

    when = source_time().timetuple()[:6]
    tmp = dest + ".tmp"
    with zipfile.ZipFile(tmp, "w") as z:
        zi = zipfile.ZipInfo("mimetype", when)
        zi.compress_type = zipfile.ZIP_STORED
        z.writestr(zi, b"application/epub+zip")
        for name, data in pkg:
            zi = zipfile.ZipInfo(name, when)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            z.writestr(zi, data.encode("utf-8") if isinstance(data, str) else data)
    os.replace(tmp, dest)
    unz = out_path(edition, "epub")
    shutil.rmtree(unz, ignore_errors=True)
    with zipfile.ZipFile(dest) as z:
        z.extractall(unz)
    if P.report:
        P.write_report(out_path(edition, "pronunciations.md"))
    n_ph = len(P.report)
    print(f"[{edition}] epub: {len(out_docs)} documents, {len(images)} images, {len(font_files)} font files, "
          f"{n_ph} pronunciation spans{', lexicon ' + P.lexicon_file if pls else ''}, {os.path.getsize(dest) // 1024} KB")
    print(f"[{edition}] wrote {dest}")


if __name__ == "__main__":
    eds = editions()
    for ed in sys.argv[1:] or list(eds):
        if ed not in eds:
            sys.exit(f"no edition '{ed}' in book.yaml (have: {', '.join(eds)})")
        build_epub(ed, eds[ed])
