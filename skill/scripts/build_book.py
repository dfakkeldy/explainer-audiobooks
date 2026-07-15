#!/usr/bin/env python3
"""Assemble narration-ready chapter Markdown into an EPUB + a combined Markdown file.

Reads a directory of chapter files named ch00.md, ch01.md, ... (zero-padded, in
order). Each file must begin with a single heading line (for example
"## Chapter 0 - Title") followed by spoken prose in blank-line-separated
paragraphs. A paragraph that is exactly a Markdown image — for example
![Tab bars in the HIG](images/hig-tab-bars.png "Apple's tab bar anatomy") —
becomes an embedded figure with a caption; image paths resolve relative to the
chapters directory. Produces:
  <out-dir>/<slug>.epub   a chaptered EPUB 3 with BOTH a nav document and an
                          NCX table of contents (older readers + apps that parse
                          NCX both work)
  <out-dir>/<slug>.md     a single combined Markdown copy

An optional Markdown file passed with ``--non-narrated-appendix`` is included
in both reading formats and their tables of contents, but its EPUB spine item
is marked ``linear="no"`` so Echo excludes it from narration. Its words are not
included in the narrated word count. The appendix filename must not start with
``ch``; that prefix is reserved for narrated chapters.

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
import shutil
import tempfile
import uuid
import zipfile
from pathlib import Path

from cover_receipts import load_selection, sha256_file, verify_package
from learning_design_qc import verify_learning_receipt
from prose_qc import verify_style_receipt

IMG_RE = re.compile(r'^!\[(?P<alt>[^\]]*)\]\((?P<src>[^)\s]+)(?:\s+"(?P<cap>[^"]*)")?\)$')


def inline_md_to_html(text):
    """Escape HTML, then apply a tiny subset of inline Markdown (bold/italic)."""
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__(.+?)__", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"(?<!_)_(?!_)(.+?)(?<!_)_(?!_)", r"<em>\1</em>", text)
    return text


def parse_chapter(path):
    """Return (title, [items]) — items are ("p", text) or ("img", alt, src, caption)."""
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
    items = []
    for chunk in re.split(r"\n\s*\n", body):
        c = chunk.strip()
        if not c:
            continue
        c = re.sub(r"\s*\n\s*", " ", c)  # collapse single newlines (prose, not verse)
        m = IMG_RE.match(c)
        if m:
            alt = m.group("alt").strip()
            items.append(("img", alt, m.group("src"), (m.group("cap") or alt).strip()))
            continue
        if c.startswith("#"):
            c = re.sub(r"^#+\s*", "", c)
        items.append(("p", c))
    return title, items


def build(chapters_dir, out_dir, title, author, subtitle, slug, lang="en", cover=None,
          contributor="", cover_selection=None, m4b_cover=None, prose_receipt=None,
          learning_receipt=None, non_narrated_appendix=None):
    if learning_receipt is not None:
        verify_learning_receipt(Path(chapters_dir), Path(learning_receipt))
    if prose_receipt is not None:
        verify_style_receipt(Path(chapters_dir), Path(prose_receipt))
    selection_path = Path(cover_selection) if cover_selection else None
    if selection_path is not None:
        if not cover or not os.path.exists(cover):
            raise ValueError("--cover-selection requires an existing --cover")
        selected = load_selection(selection_path)
        if selected.book_slug != slug:
            raise ValueError(
                f"selection book_slug {selected.book_slug} does not match build slug {slug}"
            )
        if hasattr(selected, "rendered_cover_sha256"):
            if sha256_file(Path(cover)) != selected.rendered_cover_sha256:
                raise ValueError("selected cover hash does not match --cover")
        verify_package(
            selection_path, Path(cover),
            **({"m4b_cover_path": Path(m4b_cover)} if m4b_cover is not None else {}),
        )

    os.makedirs(out_dir, exist_ok=True)
    files = sorted(glob.glob(os.path.join(chapters_dir, "ch*.md")))
    if not files:
        raise SystemExit("No chapter files (ch*.md) found in " + chapters_dir)

    img_exts = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".gif": "image/gif", ".svg": "image/svg+xml", ".webp": "image/webp"}
    chapters = []
    figures = {}  # zip filename -> source path

    def load_document(path, image_base):
        t, raw_items = parse_chapter(path)
        items = []
        for it in raw_items:
            if it[0] == "img":
                src = it[2]
                p = src if os.path.isabs(src) else os.path.join(image_base, src)
                ext = os.path.splitext(p)[1].lower()
                if not os.path.exists(p) or ext not in img_exts:
                    print("WARNING: dropping figure (missing or unsupported): " + src)
                    continue
                name = os.path.basename(p)
                if name in figures and os.path.abspath(figures[name]) != os.path.abspath(p):
                    name = uuid.uuid4().hex[:6] + "-" + name
                figures[name] = p
                items.append(("img", it[1], name, it[3]))
            else:
                items.append(it)
        return {"title": t, "items": items,
                "words": sum(len(it[1].split()) for it in items if it[0] == "p")}

    for path in files:
        chapters.append(load_document(path, chapters_dir))

    appendix = None
    if non_narrated_appendix is not None:
        appendix_path = Path(non_narrated_appendix)
        if not appendix_path.is_file():
            raise ValueError("--non-narrated-appendix must name an existing Markdown file")
        if appendix_path.name.startswith("ch"):
            raise ValueError("non-narrated appendix filename must not start with 'ch'")
        appendix = load_document(str(appendix_path), str(appendix_path.parent))
    total_words = sum(c["words"] for c in chapters)

    # ---- combined Markdown ----
    md = ["# " + title, ""]
    if subtitle:
        md += ["_" + subtitle + "_", ""]
    md += ["by " + author, "",
           "Roughly " + format(total_words, ",d") + " words.", "", "---", ""]
    for c in chapters:
        md += ["## " + c["title"], ""]
        for it in c["items"]:
            if it[0] == "img":
                md += ["![" + it[1] + "](images/" + it[2] + ")", ""]
            else:
                md += [it[1], ""]
        md += ["---", ""]
    if appendix is not None:
        md += ["## " + appendix["title"], ""]
        for it in appendix["items"]:
            if it[0] == "img":
                md += ["![" + it[1] + "](images/" + it[2] + ")", ""]
            else:
                md += [it[1], ""]
    md_path = os.path.join(out_dir, slug + ".md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    if figures:  # copy figures next to the .md so its image links resolve too
        img_out = os.path.join(out_dir, "images")
        os.makedirs(img_out, exist_ok=True)
        for name, p in figures.items():
            shutil.copyfile(p, os.path.join(img_out, name))

    # ---- EPUB ----
    uid = "urn:uuid:" + str(uuid.uuid4())
    css = (
        "body{font-family:Georgia,'Times New Roman',serif;line-height:1.6;margin:5% 6%;}"
        "h1{font-size:1.5em;line-height:1.25;margin:0 0 1em;}"
        "p{margin:0 0 1em;text-align:justify;}"
        ".title-page{text-align:center;margin-top:25%;}.title-page h1{font-size:1.8em;}"
        ".title-page .author{font-size:1.1em;margin-top:1.5em;font-style:italic;}"
        ".title-page .sub{margin-top:2em;color:#444;}"
        "figure{margin:1.5em 0;text-align:center;}"
        "figure img{max-width:100%;height:auto;}"
        "figcaption{font-size:0.85em;color:#555;margin-top:0.5em;font-style:italic;text-align:center;}"
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
        parts = []
        for it in c["items"]:
            if it[0] == "img":
                cap = ('<figcaption>' + inline_md_to_html(it[3]) + '</figcaption>') if it[3] else ''
                parts.append('<figure><img src="images/' + it[2] + '" alt="'
                             + html.escape(it[1], quote=True) + '"/>' + cap + '</figure>')
            else:
                parts.append("<p>" + inline_md_to_html(it[1]) + "</p>")
        ps = "\n".join(parts)
        inner = '<h1>' + html.escape(c["title"]) + '</h1>\n' + ps
        chapter_docs.append(("chap%02d.xhtml" % i, c["title"], xhtml(c["title"], inner, "chapter")))

    appendix_doc = None
    if appendix is not None:
        parts = []
        for it in appendix["items"]:
            if it[0] == "img":
                cap = ('<figcaption>' + inline_md_to_html(it[3]) + '</figcaption>') if it[3] else ''
                parts.append('<figure><img src="images/' + it[2] + '" alt="'
                             + html.escape(it[1], quote=True) + '"/>' + cap + '</figure>')
            else:
                parts.append("<p>" + inline_md_to_html(it[1]) + "</p>")
        inner = '<h1>' + html.escape(appendix["title"]) + '</h1>\n' + "\n".join(parts)
        appendix_doc = xhtml(appendix["title"], inner, "bibliography")

    nav_items = "\n".join('<li><a href="%s">%s</a></li>' % (fn, html.escape(t))
                          for fn, t, _ in chapter_docs)
    if appendix is not None:
        nav_items += '\n<li><a href="appendix.xhtml">%s</a></li>' % html.escape(
            appendix["title"]
        )
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
    if appendix is not None:
        appendix_index = len(chapter_docs)
        navpoints += (
            '\n<navPoint id="np%d" playOrder="%d"><navLabel><text>%s</text></navLabel>'
            '<content src="appendix.xhtml"/></navPoint>'
        ) % (appendix_index, appendix_index + 1, html.escape(appendix["title"]))
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
    if appendix is not None:
        manifest.append(
            '<item id="appendix" href="appendix.xhtml" media-type="application/xhtml+xml"/>'
        )
        spine.append('<itemref idref="appendix" linear="no"/>')
    for j, name in enumerate(sorted(figures)):
        manifest.append('<item id="fig%03d" href="images/%s" media-type="%s"/>'
                        % (j, name, img_exts[os.path.splitext(name)[1].lower()]))

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
    staged_epub = None
    epub_write_path = epub_path
    if selection_path is not None:
        descriptor, staged_epub = tempfile.mkstemp(
            prefix=f".{Path(epub_path).name}.",
            suffix=".incoming",
            dir=out_dir,
        )
        os.close(descriptor)
        epub_write_path = staged_epub
    try:
        with zipfile.ZipFile(epub_write_path, "w", zipfile.ZIP_DEFLATED) as z:
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
            if appendix_doc is not None:
                z.writestr("OEBPS/appendix.xhtml", appendix_doc)
            for name, p in figures.items():
                with open(p, "rb") as imf:
                    z.writestr("OEBPS/images/" + name, imf.read())

        if selection_path is not None:
            verify_package(
                selection_path, Path(cover),
                **({"m4b_cover_path": Path(m4b_cover)} if m4b_cover is not None else {}),
                epub_path=Path(epub_write_path),
            )
            os.replace(epub_write_path, epub_path)
            staged_epub = None
    finally:
        if staged_epub is not None:
            Path(staged_epub).unlink(missing_ok=True)

    print("Chapters:", len(chapters))
    for i, c in enumerate(chapters):
        print("  %2d. %-6d words  %s" % (i, c["words"], c["title"]))
    print("TOTAL WORDS:", format(total_words, ",d"))
    # rough audiobook runtime: ~150 wpm at 1.0x, ~187 wpm at 1.25x
    print("Est. runtime: ~%.1f h at 1.0x, ~%.1f h at 1.25x"
          % (total_words / 150 / 60, total_words / 187 / 60))
    print("FIGURES:", len(figures))
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
    ap.add_argument("--cover-selection", default=None,
                    help="Selection receipt that must match --cover and the built EPUB")
    ap.add_argument("--m4b-cover", default=None,
                    help="Square cover required by paired selection receipts")
    ap.add_argument("--prose-receipt", default=None,
                    help="Passed prose receipt that must match the canonical chapters")
    ap.add_argument(
        "--non-narrated-appendix",
        default=None,
        help="Optional Markdown appendix included for reading with EPUB spine linear=no",
    )
    learning_gate = ap.add_mutually_exclusive_group()
    learning_gate.add_argument(
        "--learning-receipt",
        default=None,
        help="Passed learning-design receipt that must match the canonical chapters",
    )
    learning_gate.add_argument(
        "--legacy-without-learning-receipt",
        action="store_true",
        help="Reproduce a legacy artifact only; forbidden for new or revised books",
    )
    learning_gate.add_argument(
        "--learning-pilot",
        action="store_true",
        help="Build a nonpackage narrated-comprehension pilot before full drafting",
    )
    a = ap.parse_args()
    if a.learning_pilot and not a.slug.endswith("-pilot"):
        ap.error("pilot builds require --slug ending in -pilot")
    if (
        a.learning_receipt is None
        and not a.legacy_without_learning_receipt
        and not a.learning_pilot
    ):
        ap.error(
            "current builds require --learning-receipt; use "
            "--learning-pilot for a nonpackage pilot or "
            "--legacy-without-learning-receipt only to reproduce an old artifact"
        )
    if a.learning_pilot:
        print("PILOT ONLY: not a governed book package or learning-completion claim")
    build(a.chapters_dir, a.out_dir, a.title, a.author, a.subtitle, a.slug, a.lang, a.cover,
          a.contributor, a.cover_selection, a.m4b_cover, a.prose_receipt,
          a.learning_receipt, a.non_narrated_appendix)


if __name__ == "__main__":
    main()
