#!/usr/bin/env python3
"""Check an edition's EPUB.

    .venv/bin/python build/check_epub.py <edition>

1. epubcheck: no fatal errors or errors (warnings are listed). Uses $EPUBCHECK_JAR
   (java -jar; the current release from github.com/w3c/epubcheck is recommended),
   else `epubcheck` on the PATH (run with java -jar if it is the jar itself).
   Skipped, with a note, when neither is installed.
2. Words: the EPUB's chapters hold the same words, in the same order, as the
   edition's flow (out/<edition>-flow.html, which the PDF is laid out from),
   leaving aside the cover, contents, running heads, popup notes and private
   marks; its glossary holds the same entries; and every paragraph, list item,
   cell, heading, side head and card title of the chapter files is in it.
3. Images: every <img> has non-empty alt text.
4. Markup: every noteref reaches a note; pronunciation spans are non-empty,
   unnested, outside links, captions and code, in documents that declare the
   ssml namespace; a linked lexicon is in the manifest.
Passes (with a note) when the edition has no EPUB (epub: false in book.yaml).
"""
import difflib, os, re, shutil, subprocess, sys
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import chapter_files, editions, epub_file, load_chapter, out_path, read_epub  # noqa: E402
from check_source import attr_texts, leaf_texts, squash  # noqa: E402
from pronounce import SSML_NS  # noqa: E402


def words(nodes):
    """Words and punctuation marks as separate tokens, so markup the EPUB adds or drops
    around a word (a note link, an <abbr>) doesn't count as a change."""
    out = []
    for n in nodes:
        for el in n.select(".toc-n, .gl-pg, svg, script, style"):
            el.decompose()
        out.extend(re.findall(r"\w+|[^\w\s]", n.get_text(" ")))
    return out


def epubcheck_cmd():
    """$EPUBCHECK_JAR first (the current release; Debian's packaged 4.2.6 is old), else the PATH."""
    jar = os.environ.get("EPUBCHECK_JAR")
    if jar and not shutil.which("java"):
        return None
    if jar and os.path.isfile(jar):
        return ["java", "-jar", jar]
    if jar:
        print(f"EPUBCHECK_JAR={jar} not found; trying epubcheck on the PATH")
    exe = shutil.which("epubcheck")
    if not exe:
        return None
    with open(os.path.realpath(exe), "rb") as f:
        if f.read(2) == b"PK":           # a packaged jar on the PATH (Debian's /usr/bin/epubcheck)
            return ["java", "-jar", exe] if shutil.which("java") else None
    return [exe]


def run_epubcheck(ed, path):
    cmd = epubcheck_cmd()
    if not cmd:
        print(f"[{ed}] epubcheck: not installed (set EPUBCHECK_JAR or put epubcheck on the PATH); skipped")
        return []
    r = subprocess.run(cmd + [path], capture_output=True, text=True)
    out = r.stdout + r.stderr
    m = re.search(r"Messages:\s*(\d+) fatals? / (\d+) errors? / (\d+) warnings? / (\d+) infos?", out)
    fatals, errors, warns = (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else (0, 0 if r.returncode == 0 else 1, 0)
    v = re.search(r"using EPUB version ([\d.]+) rules", out)   # 3.4 under EPUBCheck 5.x, 3.2 under 4.2.x
    print(f"[{ed}] epubcheck{f' (EPUB {v.group(1)} rules)' if v else ''}: {fatals} fatal, {errors} errors, {warns} warnings")
    for line in out.splitlines():
        if line.startswith(("FATAL", "ERROR", "WARNING")):
            print("  " + line[:300])
    return [f"epubcheck reports {fatals} fatal and {errors} errors"] if fatals or errors else []


def flow_parts(ed):
    flow = BeautifulSoup(open(out_path(ed, "flow.html")).read(), "html.parser").select_one("#flow")
    gl = [r.extract() for r in flow.select(".gl-row")]
    for sel in ('[data-page-class*="cover"]', ".rh-set", ".toc-row", "#contents", "#glossary", "#gl-placeholder"):
        for el in flow.select(sel):
            el.decompose()
    return flow, gl


def main(ed):
    cfg = editions()[ed]
    path = epub_file(cfg)
    if not path:
        print(f"[{ed}] epub check: no EPUB for this edition (epub off in book.yaml): PASS")
        return 0
    if not os.path.exists(path):
        print(f"[{ed}] epub check: FAIL: {os.path.basename(path)} is missing; run build/build.py")
        return 1
    fails = run_epubcheck(ed, path)
    E = read_epub(path)

    # 2. words
    chap, gloss_doc = [], None
    for idref, href, soup in E["spine"]:
        if re.fullmatch(r"ch\d+", idref):
            body = BeautifulSoup(str(soup.body), "html.parser")
            for el in body.select(".footnotes, .private-mark"):
                el.decompose()
            chap.append(body)
        elif idref == "glossary":
            gloss_doc = BeautifulSoup(str(soup.body), "html.parser")
    flow, gl_rows = flow_parts(ed)
    a, b = words([flow]), words(chap)
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    bad = [op for op in sm.get_opcodes() if op[0] != "equal"]
    print(f"[{ed}] epub words and marks: flow {len(a)}, EPUB chapters {len(b)}, differences {len(bad)}")
    for tag, i1, i2, j1, j2 in bad[:20]:
        fails.append(f"{tag}: flow «{' '.join(a[max(0, i1 - 5):i2 + 5])}» EPUB «{' '.join(b[max(0, j1 - 5):j2 + 5])}»")
    if gl_rows or gloss_doc is not None:
        ga = words(gl_rows)
        gb = words([gloss_doc.find("dl")]) if gloss_doc is not None and gloss_doc.find("dl") else []
        if ga != gb:
            d = next(op for op in difflib.SequenceMatcher(a=ga, b=gb, autojunk=False).get_opcodes() if op[0] != "equal")
            fails.append(f"glossary differs from the PDF's: «{' '.join(ga[max(0, d[1] - 5):d[2] + 5])}» vs «{' '.join(gb[max(0, d[3] - 5):d[4] + 5])}»")
    etxt = squash("".join(c.get_text("") for c in chap))
    blocks = []
    for p in chapter_files(cfg):
        _, soup = load_chapter(p, ed)
        blocks += [(os.path.basename(p), t) for t in leaf_texts(soup) + attr_texts(soup, ed)]
    missing = [(src, t) for src, t in blocks if squash(t) not in etxt]
    print(f"[{ed}] epub source blocks: {len(blocks)}, missing: {len(missing)}")
    fails += [f"source text missing from the EPUB: {src}: {t[:120]}" for src, t in missing[:40]]

    # 3. images, 4. markup
    n_img = n_ph = n_ref = 0
    manifest = {href: media for href, media in E["items"].values()}
    for idref, href, soup in E["spine"]:
        ids = {el["id"] for el in soup.find_all(id=True)}
        for img in soup.find_all("img"):
            n_img += 1
            if not (img.get("alt") or "").strip():
                fails.append(f"{href}: image without alt text: {img.get('src')}")
        for a in soup.select('a[epub\\:type~="noteref"]'):
            n_ref += 1
            t = a.get("href", "")
            if not (t.startswith("#") and t[1:] in ids) or "footnote" not in (soup.find(id=t[1:]).get("epub:type") or ""):
                fails.append(f"{href}: noteref to {t} doesn't reach a note in the same document")
        spans = soup.find_all(attrs={"ssml:ph": True})
        n_ph += len(spans)
        if spans and soup.html.get("xmlns:ssml") != SSML_NS:
            fails.append(f"{href}: ssml:ph used but the ssml namespace isn't declared on <html>")
        for sp in spans:
            txt = sp.get_text()
            if not txt.strip() or not sp["ssml:ph"].strip():
                fails.append(f"{href}: empty pronunciation span")
            if set("[]()/") & set(txt):
                fails.append(f"{href}: pronunciation span text «{txt}» contains []()/")
            if sp.find(attrs={"ssml:ph": True}) or any(p.name in ("a", "figcaption", "code", "pre") for p in sp.parents):
                fails.append(f"{href}: pronunciation span «{txt}» is nested or inside a link, caption or code")
        for ln in soup.select('link[rel="pronunciation"]'):
            target = os.path.normpath(os.path.join(os.path.dirname(href), ln.get("href", ""))).replace(os.sep, "/")
            if manifest.get(target) != "application/pls+xml" or target not in E["raw"]:
                fails.append(f"{href}: lexicon {ln.get('href')} isn't in the package manifest as application/pls+xml")
    print(f"[{ed}] epub markup: {n_img} images, {n_ref} noterefs, {n_ph} pronunciation spans")
    print(f"[{ed}] epub check: {'FAIL' if fails else 'PASS'}")
    for f in fails[:60]:
        print("  " + f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
