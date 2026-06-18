#!/usr/bin/env python3
"""Assemble narration-ready chapter Markdown into an EPUB + a combined Markdown file.

Reads a directory of chapter files named ch00.md, ch01.md, ... (zero-padded, in
order). Each file must begin with a single heading line (for example
"## Chapter 0 - Title") followed by spoken prose in blank-line-separated
paragraphs. Produces:
  <out-dir>/<slug>.epub   a chaptered EPUB 3 with BOTH a nav document and an
                          NCX table of contents (older readers + apps that parse
                          NCX both work)
  <out-dir>/<slug>.md     a single combined Markdown copy

Standard library only. Designed for the explainer-audiobook skill.

Example:
  python3 build_book.py \
    --chapters-dir ./chapters \
    --out-dir ./dist \
    --title "Echo, From the Inside" \
    --author "Dan Fakkeldy" \
    --subtitle "A beginner's guide to iOS development" \
    --slug Echo-From-The-Inside
"""

import argparse
import glob
import html
import os
import re
import uuid
import zipfile


def inline_md_to_html(text):
    """Escape HTML, then apply a tiny subset of inline Markdown (bold/italic)."""
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__(.+?)__", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"(?<!_)_(?!_)(.+?)(?<!_)_(?!_)", r"<em>\1</em>", text)
    return text


def parse_chapter(path):
    """Return (title, [paragraphs]) from a chapter Markdown file."""
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read().strip()
    lines = raw.split("\n")
    title = None
    body_start = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("#"):
            title = re.sub(r"^#+\s*", "", line.strip())
            body_start = i + 1
            break
    if title is None:
        title = os.path.splitext(os.path.basename(path))[0]
        body_start = 0
    body = "\n".join(lines[body_start:]).strip()
    paras = []
    for chunk in re.split(r"\n\s*\n", body):
        c = chunk.strip()
        if not c:
            continue
        c = re.sub(r"\s*\n\s*", " ", c)  # collapse single newlines (prose, not verse)
        if c.startswith("#"):
            c = re.sub(r"^#+\s*", "", c)
        paras.append(c)
    return title, paras


def build(chapters_dir, out_dir, title, author, subtitle, slug, lang="en", cover=None,
          contributor=""):
    os.makedirs(out_dir, exist_ok=True)
    files = sorted(glob.glob(os.path.join(chapters_dir, "ch*.md")))
    if not files:
        raise SystemExit("No chapter files (ch*.md) found in " + chapters_dir)

    chapters = []
    for path in files:
        t, paras = parse_chapter(path)
        chapters.append({"title": t, "paras": paras,
                         "words": sum(len(p.split()) for p in paras)})
    total_words = sum(c["words"] for c in chapters)

    # ---- combined Markdown ----
    md = ["# " + title, ""]
    if subtitle:
        md += ["_" + subtitle + "_", ""]
    md += ["by " + author, "",
           "Roughly " + format(total_words, ",d") + " words.", "", "---", ""]
    for c in chapters:
        md += ["## " + c["title"], ""]
        for p in c["paras"]:
            md += [p, ""]
        md += ["---", ""]
    md_path = os.path.join(out_dir, slug + ".md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    # ---- EPUB ----
    uid = "urn:uuid:" + str(uuid.uuid4())
    css = (
        "body{font-family:Georgia,'Times New Roman',serif;line-height:1.6;margin:5% 6%;}"
        "h1{font-size:1.5em;line-height:1.25;margin:0 0 1em;}"
        "p{margin:0 0 1em;text-align:justify;}"
        ".title-page{text-align:center;margin-top:25%;}.title-page h1{font-size:1.8em;}"
        ".title-page .author{font-size:1.1em;margin-top:1.5em;font-style:italic;}"
        ".title-page .sub{margin-top:2em;color:#444;}"
    )

    def xhtml(title_text, inner, epub_type):
        return (
            '<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n'
            '<html xmlns="http://www.w3.org/1999/xhtml" '
            'xmlns:epub="http://www.idpf.org/2007/ops" lang="' + lang + '">\n'
            '<head><meta charset="utf-8"/><title>' + html.escape(title_text) + '</title>'
            '<link rel="stylesheet" type="text/css" href="style.css"/></head>\n'
            '<body><section epub:type="' + epub_type + '">' + inner + '</section></body></html>'
        )

    sub_line = html.escape(subtitle) if subtitle else ""
    title_doc = xhtml(title, (
        '<h1>' + html.escape(title) + '</h1>'
        '<p class="author">by ' + html.escape(author) + '</p>'
        + ('<p class="sub">' + sub_line + '</p>' if sub_line else '')
    ), "titlepage").replace('<section epub:type="titlepage">',
                            '<section epub:type="titlepage" class="title-page">')

    chapter_docs = []
    for i, c in enumerate(chapters):
        ps = "\n".join("<p>" + inline_md_to_html(p) + "</p>" for p in c["paras"])
        inner = '<h1>' + html.escape(c["title"]) + '</h1>\n' + ps
        chapter_docs.append(("chap%02d.xhtml" % i, c["title"], xhtml(c["title"], inner, "chapter")))

    nav_items = "\n".join('<li><a href="%s">%s</a></li>' % (fn, html.escape(t))
                          for fn, t, _ in chapter_docs)
    nav = (
        '<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n'
        '<html xmlns="http://www.w3.org/1999/xhtml" '
        'xmlns:epub="http://www.idpf.org/2007/ops" lang="' + lang + '">\n'
        '<head><meta charset="utf-8"/><title>Table of Contents</title>'
        '<link rel="stylesheet" type="text/css" href="style.css"/></head>\n'
        '<body><nav epub:type="toc" id="toc"><h1>Table of Contents</h1><ol>\n'
        + nav_items + '\n</ol></nav></body></html>'
    )

    navpoints = "\n".join(
        ('<navPoint id="np%d" playOrder="%d"><navLabel><text>%s</text></navLabel>'
         '<content src="%s"/></navPoint>') % (i, i + 1, html.escape(t), fn)
        for i, (fn, t, _) in enumerate(chapter_docs))
    ncx = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">\n'
        '<head><meta name="dtb:uid" content="' + uid + '"/></head>\n'
        '<docTitle><text>' + html.escape(title) + '</text></docTitle>\n'
        '<navMap>\n' + navpoints + '\n</navMap></ncx>'
    )

    # Optional cover: embed as the library-thumbnail image AND a full-bleed first page
    cover_bytes = cover_name = cover_doc = None
    cover_meta = ""
    if cover and os.path.exists(cover):
        ext = os.path.splitext(cover)[1].lower()
        media = "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"
        cover_name = "cover.jpg" if media == "image/jpeg" else "cover.png"
        with open(cover, "rb") as cf:
            cover_bytes = cf.read()
        cover_meta = '<meta name="cover" content="cover-image"/>\n'
        cover_doc = (
            '<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n'
            '<html xmlns="http://www.w3.org/1999/xhtml" '
            'xmlns:epub="http://www.idpf.org/2007/ops" lang="' + lang + '">\n'
            '<head><meta charset="utf-8"/><title>Cover</title>'
            '<style>html,body{margin:0;padding:0;height:100%}'
            'img{display:block;width:100%;height:auto}</style></head>\n'
            '<body><section epub:type="cover"><img src="' + cover_name +
            '" alt="' + html.escape(title) + ' cover"/></section></body></html>'
        )

    manifest = [
        '<item id="css" href="style.css" media-type="text/css"/>',
        '<item id="titlepage" href="titlepage.xhtml" media-type="application/xhtml+xml"/>',
        '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
        '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>',
    ]
    spine = ['<itemref idref="titlepage"/>']
    if cover_bytes is not None:
        manifest.insert(0, '<item id="cover-image" href="%s" media-type="%s" properties="cover-image"/>' % (cover_name, media))
        manifest.insert(1, '<item id="coverpage" href="cover.xhtml" media-type="application/xhtml+xml"/>')
        spine.insert(0, '<itemref idref="coverpage"/>')
    for i, (fn, _, _) in enumerate(chapter_docs):
        iid = "chap%02d" % i
        manifest.append('<item id="%s" href="%s" media-type="application/xhtml+xml"/>' % (iid, fn))
        spine.append('<itemref idref="%s"/>' % iid)

    meta_sub = ('<meta name="calibre:subtitle" content="' + sub_line + '"/>') if sub_line else ""
    contributor_meta = (('<dc:contributor>' + html.escape(contributor) + '</dc:contributor>\n')
                        if contributor else "")
    opf = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid">\n'
        '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">\n'
        '<dc:identifier id="bookid">' + uid + '</dc:identifier>\n'
        '<dc:title>' + html.escape(title) + '</dc:title>\n'
        '<dc:creator>' + html.escape(author) + '</dc:creator>\n'
        + contributor_meta +
        '<dc:language>' + lang + '</dc:language>\n'
        '<meta property="dcterms:modified">2026-01-01T00:00:00Z</meta>\n'
        + meta_sub + '\n' + cover_meta + '</metadata>\n'
        '<manifest>\n' + "\n".join(manifest) + '\n</manifest>\n'
        '<spine toc="ncx">\n' + "\n".join(spine) + '\n</spine>\n</package>'
    )

    epub_path = os.path.join(out_dir, slug + ".epub")
    with zipfile.ZipFile(epub_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml",
                   '<?xml version="1.0" encoding="utf-8"?>\n'
                   '<container version="1.0" '
                   'xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
                   '<rootfiles><rootfile full-path="OEBPS/content.opf" '
                   'media-type="application/oebps-package+xml"/></rootfiles></container>')
        z.writestr("OEBPS/style.css", css)
        z.writestr("OEBPS/content.opf", opf)
        z.writestr("OEBPS/nav.xhtml", nav)
        z.writestr("OEBPS/toc.ncx", ncx)
        z.writestr("OEBPS/titlepage.xhtml", title_doc)
        if cover_bytes is not None:
            z.writestr("OEBPS/" + cover_name, cover_bytes)
            z.writestr("OEBPS/cover.xhtml", cover_doc)
        for fn, _, doc in chapter_docs:
            z.writestr("OEBPS/" + fn, doc)

    print("Chapters:", len(chapters))
    for i, c in enumerate(chapters):
        print("  %2d. %-6d words  %s" % (i, c["words"], c["title"]))
    print("TOTAL WORDS:", format(total_words, ",d"))
    # rough audiobook runtime: ~150 wpm at 1.0x, ~187 wpm at 1.25x
    print("Est. runtime: ~%.1f h at 1.0x, ~%.1f h at 1.25x"
          % (total_words / 150 / 60, total_words / 187 / 60))
    print("COVER:", cover if (cover and os.path.exists(cover)) else "(none)")
    print("EPUB:", epub_path)
    print("MD  :", md_path)


def main():
    ap = argparse.ArgumentParser(description="Assemble chapter Markdown into EPUB + Markdown.")
    ap.add_argument("--chapters-dir", required=True, help="Directory of ch00.md, ch01.md, ...")
    ap.add_argument("--out-dir", required=True, help="Where to write the .epub and .md")
    ap.add_argument("--title", required=True)
    ap.add_argument("--author", default="")
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--slug", required=True, help="Output filename base (no extension)")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--cover", default=None, help="Optional cover image (PNG/JPEG) to embed")
    ap.add_argument("--contributor", default="",
                    help="Optional second name credited in metadata (e.g., the human owner)")
    a = ap.parse_args()
    build(a.chapters_dir, a.out_dir, a.title, a.author, a.subtitle, a.slug, a.lang, a.cover,
          a.contributor)


if __name__ == "__main__":
    main()
