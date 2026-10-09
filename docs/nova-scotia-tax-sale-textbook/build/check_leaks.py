#!/usr/bin/env python3
"""Check an edition for material that must not be in it, and private marks.

    .venv/bin/python build/check_leaks.py <edition>

From book.yaml, for this edition:
  forbid: [regex, ...]    must not match any page's text or any link target
                          (case-sensitive; start a pattern with (?i) to ignore case)
  private_mark: "..."     if set: the text must appear on every page, and the
                          PDF's file name must contain "private"
Editions without a private_mark must not contain any other edition's mark.
The EPUB gets the same checks: every document's text and links, its metadata,
contents and lexicon, the mark in every document of the reading order, and
"private" in its file name.
"""
import os, re, subprocess, sys
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, editions, epub_file, out_path, read_epub  # noqa: E402


def squash(t):
    return re.sub(r"\s+", " ", t)


def main(ed):
    eds = editions()
    cfg = eds[ed]
    pdf = os.path.join(ROOT, cfg["file"])
    text = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True, check=True).stdout
    pages = [squash(p) for p in text.split("\f")]
    if pages and not pages[-1].strip():
        pages.pop()
    hrefs = [a.get("href", "") for a in BeautifulSoup(open(out_path(ed, "paged.html")).read(), "html.parser").select("a[href]")]
    fails = []
    for pat in cfg.get("forbid") or []:
        rx = re.compile(pat)
        for i, p in enumerate(pages, 1):
            for m in rx.finditer(p):
                fails.append(f"page {i}: forbidden /{pat}/ matched «{p[max(0, m.start() - 40):m.end() + 40].strip()}»")
        for h in hrefs:
            if rx.search(h):
                fails.append(f"link target matches forbidden /{pat}/: {h}")
    mark = cfg.get("private_mark")
    if mark:
        if "private" not in os.path.basename(cfg["file"]).lower():
            fails.append(f"private edition's file name doesn't say so: {cfg['file']}")
        m = squash(mark)
        missing = [i for i, p in enumerate(pages, 1) if m not in p]
        if missing:
            fails.append(f"private mark missing on pages {', '.join(map(str, missing[:30]))}")
    else:
        for other, ocfg in eds.items():
            om = ocfg.get("private_mark")
            if other != ed and om:
                hits = [i for i, p in enumerate(pages, 1) if squash(om) in p]
                if hits:
                    fails.append(f"{other}'s private mark appears on pages {', '.join(map(str, hits[:30]))}")
    epub = epub_file(cfg)
    if epub:
        fails += check_epub(ed, eds, cfg, epub)
    print(f"[{ed}] leak check: {len(pages)} pages{' and the EPUB' if epub else ''}, {len(cfg.get('forbid') or [])} forbidden patterns, "
          f"private mark {'required' if mark else 'absent'}: {'FAIL' if fails else 'PASS'}")
    for f in fails[:60]:
        print("  " + f)
    return 1 if fails else 0


def check_epub(ed, eds, cfg, path):
    if not os.path.exists(path):
        return [f"EPUB missing: {os.path.basename(path)} (run build/build.py)"]
    E = read_epub(path)
    texts, hrefs = [], []
    for name, data in E["raw"].items():
        if name.endswith((".xhtml", ".opf", ".ncx", ".pls")):
            soup = BeautifulSoup(data.decode("utf-8"), "html.parser")
            texts.append((name, squash(soup.get_text(" "))))
            hrefs += [(name, el.get("href") or el.get("src") or "") for el in soup.find_all(["a", "link", "img", "item", "content"])]
    fails = []
    for pat in cfg.get("forbid") or []:
        rx = re.compile(pat)
        for name, t in texts:
            for m in rx.finditer(t):
                fails.append(f"EPUB {name}: forbidden /{pat}/ matched «{t[max(0, m.start() - 40):m.end() + 40].strip()}»")
        for name, h in hrefs:
            if rx.search(h):
                fails.append(f"EPUB {name}: link target matches forbidden /{pat}/: {h}")
        for name in E["names"]:
            if rx.search(name):
                fails.append(f"EPUB file name matches forbidden /{pat}/: {name}")
    mark = cfg.get("private_mark")
    if mark:
        if "private" not in os.path.basename(path).lower():
            fails.append(f"private edition's EPUB name doesn't say so: {os.path.basename(path)}")
        missing = [href for _, href, soup in E["spine"] if squash(mark) not in squash(soup.get_text(" "))]
        if missing:
            fails.append(f"private mark missing from EPUB documents {', '.join(missing[:20])}")
    else:
        for other, ocfg in eds.items():
            om = ocfg.get("private_mark")
            if other != ed and om:
                hits = [name for name, t in texts if squash(om) in t]
                if hits:
                    fails.append(f"{other}'s private mark appears in the EPUB: {', '.join(hits[:20])}")
    return fails


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
