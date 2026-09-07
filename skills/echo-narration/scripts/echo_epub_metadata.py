#!/usr/bin/env python3
"""Read audiobook attribution from the frozen EPUB instead of the operator."""
from __future__ import annotations

from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile


def source_author(epub: Path) -> str:
    with zipfile.ZipFile(epub) as archive:
        container = ET.fromstring(archive.read('META-INF/container.xml'))
        rootfile = container.find(
            '{urn:oasis:names:tc:opendocument:xmlns:container}rootfiles/'
            '{urn:oasis:names:tc:opendocument:xmlns:container}rootfile'
        )
        if rootfile is None or not rootfile.get('full-path'):
            raise ValueError('EPUB has no package document')
        package = ET.fromstring(archive.read(rootfile.attrib['full-path']))
        creators = package.findall(
            '{http://www.idpf.org/2007/opf}metadata/'
            '{http://purl.org/dc/elements/1.1/}creator'
        )
        names = [' '.join(''.join(node.itertext()).split()) for node in creators]
        names = [name for name in names if name]
        if not names:
            raise ValueError('EPUB has no nonempty dc:creator; set its author before narration')
        return '; '.join(names)


def main() -> int:
    if len(sys.argv) != 2:
        print('usage: echo_epub_metadata.py EPUB', file=sys.stderr)
        return 64
    try:
        author = source_author(Path(sys.argv[1]))
    except (OSError, KeyError, ValueError, ET.ParseError, zipfile.BadZipFile) as error:
        print(f'Cannot read source author: {error}', file=sys.stderr)
        return 65
    print(author)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
