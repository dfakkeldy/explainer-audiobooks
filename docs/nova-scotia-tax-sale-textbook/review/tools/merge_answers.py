"""Rebuild src/chapters/97-answers.md from src/appendix-answers/chNN.md (headings demoted one level)."""
import pathlib
import re

P = pathlib.Path(__file__).resolve().parents[2]
TITLE = "# Answers to Check Your Understanding\n"

target = P / "src/chapters/97-answers.md"
front = target.read_text().split(TITLE, 1)[0]
parts = []
for frag in sorted((P / "src/appendix-answers").glob("ch[0-9][0-9].md")):
    text = re.sub(r"^(#+) ", lambda m: "#" + m.group(1) + " ", frag.read_text(), flags=re.M)
    parts.append(text.strip())
target.write_text(front + TITLE + "\n" + "\n\n".join(parts) + "\n")
print(f"merged {len(parts)} fragments into {target.relative_to(P)}")
