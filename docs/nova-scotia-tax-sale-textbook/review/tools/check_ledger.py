"""Check a chapter claims ledger (review/claims-ledger-plan.md, section 7, checks 1-3 and 6).

    python3 review/tools/check_ledger.py 01

- every row has a status from the allowed set (no "dropped");
- every "Original (exact)" quote is found within +-4 lines of its md: line in the frozen manuscript;
- every "Rewrite (exact)" quote is found in the chapter file, its answers fragment, or one of the
  chapter's figure SVGs (whitespace-normalized, Markdown marks and typographic quotes folded);
- the rewritten chapter contains no eight-digit number other than the five the original prints.
Prints problems and the counts; exits 1 on any problem.
"""
import html
import re
import sys
from pathlib import Path

P = Path(__file__).resolve().parents[2]
REPO = P.parents[1]
MD = REPO / "books/beyond-the-tax-sale-packet/beyond-the-tax-sale-packet.md"
STATUSES = {"kept", "kept-figure", "kept-note", "moved", "merged", "flagged-kept"}
ALLOWED_IDS = {"50292390", "50308311", "00542589", "15234636", "00616672"}


def norm(s: str) -> str:
    s = html.unescape(s)
    s = s.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    s = s.replace("—", "-").replace("–", "-").replace("•", "-")
    s = re.sub(r"\*\*|`|\\", "", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"^\s*[-*]\s+|^\s*\d+\.\s+", " ", s, flags=re.M)
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


def main(ch: str):
    ledger = P / f"review/claims/ch{ch}.md"
    # the ledger header names its chapter file; fall back to the first match (engine samples such
    # as 02-cards.md share the number prefix)
    named = re.search(rf"src/chapters/({ch}-[\w-]+\.md)", ledger.read_text())
    chapter = (P / "src/chapters" / named.group(1)) if named else \
        next((P / "src/chapters").glob(f"{ch}-*.md"))
    targets = [chapter, P / f"src/appendix-answers/ch{ch}.md"]
    targets += sorted((P / "src/assets/figures").glob(f"fig-{ch}-*.svg"))
    corpus = " ".join(norm(t.read_text()) for t in targets)
    # SVG text is split into lines; also index each svg's text joined line by line
    svg_text = " ".join(norm(" ".join(re.findall(r"<text[^>]*>([^<]*)</text>", t.read_text())))
                        for t in targets if t.suffix == ".svg")
    corpus += " " + svg_text
    md_lines = MD.read_text().splitlines()

    problems, counts, n = [], {}, 0
    for row in ledger.read_text().splitlines():
        if not row.startswith(f"| ch{ch}-"):
            continue
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if len(cells) < 9:
            problems.append(f"short row: {row[:60]}")
            continue
        cid, line, _type, orig, status, _dest, rew = cells[:7]
        n += 1
        st = status.split()[0]
        counts[st] = counts.get(st, 0) + 1
        if st not in STATUSES:
            problems.append(f"{cid}: bad status {status!r}")
        q = orig.strip('"')
        if line.isdigit():
            ln = int(line)
            window = norm(" ".join(md_lines[max(0, ln - 5): ln + 4]))
            parts = [x for qq in (re.findall(r'"([^"]+)"', orig) or [q]) for x in qq.split("…")]
            if not all(norm(part) in window for part in parts if part.strip()):
                problems.append(f"{cid}: original not found near md:{line}: {q[:50]!r}")
        for part in re.findall(r'"([^"]+)"', rew) or [rew]:
            for piece in part.split("…"):
                if piece.strip() and norm(piece) not in corpus:
                    problems.append(f"{cid}: rewrite not found: {piece[:60]!r}")

    for m in re.findall(r"\b\d{8}\b", chapter.read_text()):
        if m not in ALLOWED_IDS:
            problems.append(f"forbidden eight-digit identifier {m}")

    for p in problems:
        print("!", p)
    print(f"claims {n}; " + "; ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main(sys.argv[1])
