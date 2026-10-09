"""Shared by the build and the checks: book.yaml, editions, and chapter loading.

The checks read chapters exactly as the build does (same pandoc call, same
edition filtering), so a check can't pass on text the build never saw.
"""
import glob, os, re, subprocess, warnings
import yaml
from bs4 import BeautifulSoup
try:                                    # the EPUB checks read its XML files with the HTML parser on purpose
    from bs4 import XMLParsedAsHTMLWarning
    warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
except ImportError:
    pass

BUILD = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BUILD)
OUT = os.path.join(ROOT, "out")
SRC = os.path.join(ROOT, "src")
CHAPTERS = os.path.join(SRC, "chapters")


def load_yaml(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path) as f:
        return yaml.safe_load(f) or default


BOOK = load_yaml(os.path.join(ROOT, "book.yaml"), {})
GLOSSARY = load_yaml(os.path.join(SRC, "glossary.yaml"), [])
CARDS = load_yaml(os.path.join(SRC, "cards.yaml"), {})


def editions():
    """{name: config}; every edition has 'file', 'epub_file' and 'contents'."""
    eds = BOOK.get("editions") or {"book": {}}
    out = {}
    for name, cfg in eds.items():
        cfg = dict(cfg or {})
        cfg.setdefault("file", f"{re.sub(r'[^a-z0-9]+', '-', BOOK.get('title', 'book').lower()).strip('-')}-{name}.pdf")
        cfg.setdefault("epub_file", re.sub(r"\.pdf$", "", cfg["file"], flags=re.I) + ".epub")
        if not cfg.get("contents"):
            files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(CHAPTERS, "*.md")))
            cfg["contents"] = ["@cover", "@toc"] + files + ["@glossary"]
        out[name] = cfg
    return out


def chapter_files(cfg):
    return [os.path.join(CHAPTERS, c) for c in cfg["contents"] if not c.startswith("@")]


def pandoc(md):
    return subprocess.run(["pandoc", "-f", "markdown+smart-auto_identifiers", "-t", "html5", "--wrap=none"],
                          input=md, capture_output=True, text=True, check=True).stdout


def split_front_matter(md):
    m = re.match(r"(?s)^---\n(.*?)\n---\n", md)
    if not m:
        return {}, md
    return (yaml.safe_load(m.group(1)) or {}), md[m.end():]


def for_edition(soup, edition):
    """Keep `::: {.only editions="a,b"}` blocks only in the named editions.
    Pandoc writes a fenced div that opens with a heading as <section>, so
    both tags are handled here and everywhere else."""
    for d in soup.find_all(["div", "section"], class_="only"):
        names = re.split(r"[,\s]+", (d.get("data-editions") or d.get("editions") or d.get("data-edition") or "").strip())
        if edition in names:
            d.unwrap()
        else:
            d.decompose()
    return soup


def load_chapter(path, edition):
    """(front matter dict, BeautifulSoup of the chapter body for this edition)."""
    with open(path) as f:
        fm, md = split_front_matter(f.read())
    soup = BeautifulSoup(pandoc(md), "html.parser")
    return fm, for_edition(soup, edition)


def out_path(edition, kind):
    return os.path.join(OUT, f"{edition}-{kind}")


# ---------------------------------------------------------------- EPUB
def epub_settings():
    """book.yaml `epub:` block; `epub: false` (or enabled: false) turns EPUBs off."""
    e = BOOK.get("epub", {})
    if e is False:
        return {"enabled": False}
    e = dict(e or {})
    e.setdefault("enabled", True)
    return e


def epub_file(cfg):
    """The edition's EPUB path, or None when EPUBs are off for it (epub_file: false)."""
    if not epub_settings()["enabled"] or cfg.get("epub_file") is False:
        return None
    return os.path.join(ROOT, cfg["epub_file"])


def read_epub(path):
    """Open a built EPUB for the checks: {'opf': soup, 'names': [...], 'raw': {name: bytes},
    'items': {id: (href, media_type)}, 'spine': [(id, href, soup)]} with hrefs relative to the zip root."""
    import posixpath, zipfile
    z = zipfile.ZipFile(path)
    raw = {n: z.read(n) for n in z.namelist()}
    container = BeautifulSoup(raw["META-INF/container.xml"], "html.parser")
    opf_path = container.find("rootfile")["full-path"]
    base = posixpath.dirname(opf_path)
    opf = BeautifulSoup(raw[opf_path], "html.parser")
    items = {i["id"]: (posixpath.normpath(posixpath.join(base, i["href"])), i["media-type"]) for i in opf.find_all("item")}
    spine = []
    for ref in opf.find("spine").find_all("itemref"):
        href = items[ref["idref"]][0]
        spine.append((ref["idref"], href, BeautifulSoup(raw[href].decode("utf-8"), "html.parser")))
    return {"opf": opf, "opf_path": opf_path, "names": list(raw), "raw": raw, "items": items, "spine": spine}
