# Audiobook Writing Quality Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace post-hoc receipt gates with generation-time budgets, and give the nonfiction book skills positive voice control plus a narrative spine, so books stop reading as filled-in forms.

**Architecture:** New pure-function module `skill/scripts/prose_metrics.py` holds every new measure and is imported by `prose_qc.py`, keeping the existing 381-line script from bloating and making each measure unit-testable in isolation. Measures land first and advisory; budgets that consume them land second; governance and prose-craft references land third; the `book_qc.py` consolidation lands last because it is the only task that can break packaging.

**Tech Stack:** Python 3.11+, stdlib only (`re`, `statistics`, `dataclasses`, `json`, `hashlib`), pytest.

## Global Constraints

- Design spec: `docs/superpowers/specs/2026-07-25-audiobook-writing-quality-design.md`.
- Stdlib only. No new third-party dependencies.
- All new measures ship **advisory** (reported, never failing) until Task 6 proves the corpus split. Only Task 7 promotes any measure to blocking.
- Receipt schemas are **additive only**. An existing `prose-style-receipt.json` must keep validating; `build_book.py --prose-receipt` must keep accepting receipts produced before this change.
- Arithmetic density is **never** an absolute cap — always a ratio against the brief's declared tier. Ed1 scored the corpus maximum (7.1/10k) and taught successfully.
- Paragraph CV is measured and reported but never a threshold (separates 0.37/0.43 good vs 0.30 weak — too narrow).
- Contract tests pin SKILL.md phrasing (`tests/test_skill_prose_contract.py`, `test_skill_learning_contract.py`, `test_fiction_book_development_contract.py`, `test_custom_learning_audiobook_install_contract.py`). Any reference-doc edit must run the full suite.
- Private/generated artifacts stay uncommitted. `build/` is gitignored and holds the QM ed1 corpus — never add it.
- Run the full suite with `python3 -m pytest tests/ -q` plus `python3 tools/validate_skills.py` before every commit.

## File Structure

| File | Responsibility |
|---|---|
| `skill/scripts/prose_metrics.py` | **New.** Pure measure functions: rhythm, coordinate lists, abstract subjects, concept load, arithmetic density. No I/O, no argparse. |
| `skill/scripts/prose_qc.py` | Existing. Imports `prose_metrics`, adds a `metrics` block to the report and receipt. |
| `tests/test_prose_metrics.py` | **New.** Unit tests per measure. |
| `tests/test_prose_qc_metrics.py` | **New.** Integration: report and receipt contain the metrics block. |
| `tests/test_corpus_regression.py` | **New.** The three-book split. Skips cleanly when corpora are absent. |
| `skill/references/voice-design.md` | **New.** Nonfiction voice control panel. |
| `skill/references/narration-style.md` | Budgets table; delete "or running summary"; modal-conversion rule. |
| `skill/references/learning-design.md` | Verdict collapse 6→3; preserve-on-by-default; ledger `surface` column. |
| `skill/references/declaudification.md` | Demoted to QC-time density review. |

---

### Task 1: Rhythm metrics

**Files:**
- Create: `skill/scripts/prose_metrics.py`
- Test: `tests/test_prose_metrics.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `split_sentences(text: str) -> list[str]`; `rhythm(paragraph_texts: list[str]) -> dict[str, float]` returning keys `paragraph_cv`, `sentence_cv`, `paragraph_mean`, `sentence_mean`, `paragraph_count`, `sentence_count`. All later tasks import from this module.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_prose_metrics.py
import importlib.util
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "prose_metrics",
    Path(__file__).resolve().parents[1] / "skill" / "scripts" / "prose_metrics.py",
)
prose_metrics = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prose_metrics)


def test_split_sentences_handles_terminators_and_abbreviations():
    text = "One two three. Four five! Six seven? Eight."
    assert prose_metrics.split_sentences(text) == [
        "One two three.", "Four five!", "Six seven?", "Eight.",
    ]


def test_rhythm_uniform_paragraphs_score_zero_cv():
    # Three identical paragraphs of identical sentences -> no variance at all.
    para = "aa bb cc dd ee. ff gg hh ii jj."
    result = prose_metrics.rhythm([para, para, para])
    assert result["paragraph_cv"] == 0.0
    assert result["sentence_cv"] == 0.0
    assert result["paragraph_count"] == 3
    assert result["sentence_count"] == 6


def test_rhythm_varied_paragraphs_score_positive_cv():
    short = "aa bb."
    long = " ".join(["word"] * 60) + ". " + " ".join(["word"] * 5) + "."
    result = prose_metrics.rhythm([short, long])
    assert result["paragraph_cv"] > 0.5
    assert result["sentence_cv"] > 0.5


def test_rhythm_empty_input_is_safe():
    result = prose_metrics.rhythm([])
    assert result["paragraph_cv"] == 0.0
    assert result["sentence_cv"] == 0.0
    assert result["paragraph_count"] == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_prose_metrics.py -q`
Expected: FAIL — `FileNotFoundError` or `ModuleNotFoundError` for `prose_metrics.py`.

- [ ] **Step 3: Write minimal implementation**

```python
#!/usr/bin/env python3
"""Pure prose measures for audiobook manuscripts.

Every function here is side-effect free and takes plain strings, so each
measure can be unit-tested without touching the filesystem or argparse.
`prose_qc.py` is the only caller that does I/O.

Design note: these measures describe *shape*, not vocabulary. The existing
phrase-family checks in prose_qc.py catch what the prose says; these catch
how uniformly it says it, which is the more reliable AI signature.
"""

from __future__ import annotations

import re
import statistics

SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def split_sentences(text: str) -> list[str]:
    """Split on sentence terminators followed by whitespace."""
    flat = re.sub(r"\s+", " ", text).strip()
    if not flat:
        return []
    return [part for part in SENTENCE_SPLIT_RE.split(flat) if part]


def _cv(values: list[int]) -> float:
    """Coefficient of variation: stdev / mean. Zero when undefined."""
    if len(values) < 2:
        return 0.0
    mean = statistics.mean(values)
    if mean == 0:
        return 0.0
    return statistics.pstdev(values) / mean


def rhythm(paragraph_texts: list[str]) -> dict[str, float]:
    """Variance in paragraph and sentence length.

    Uniformity is the signal. Human nonfiction puts one-sentence paragraphs
    next to nine-sentence ones; generated prose tends to a single length.
    """
    para_lengths = [len(p.split()) for p in paragraph_texts if p.strip()]
    sent_lengths: list[int] = []
    for paragraph in paragraph_texts:
        sent_lengths.extend(len(s.split()) for s in split_sentences(paragraph))
    return {
        "paragraph_cv": round(_cv(para_lengths), 4),
        "sentence_cv": round(_cv(sent_lengths), 4),
        "paragraph_mean": round(statistics.mean(para_lengths), 2) if para_lengths else 0.0,
        "sentence_mean": round(statistics.mean(sent_lengths), 2) if sent_lengths else 0.0,
        "paragraph_count": len(para_lengths),
        "sentence_count": len(sent_lengths),
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_prose_metrics.py -q`
Expected: PASS, 4 passed.

- [ ] **Step 5: Commit**

```bash
git add skill/scripts/prose_metrics.py tests/test_prose_metrics.py
git commit -m "feat: add rhythm variance measures for audiobook prose"
```

---

### Task 2: Coordinate-list detector

**Files:**
- Modify: `skill/scripts/prose_metrics.py`
- Test: `tests/test_prose_metrics.py`

**Interfaces:**
- Consumes: `split_sentences` from Task 1.
- Produces: `coordinate_lists(paragraph_texts: list[str]) -> dict[str, object]` returning `count`, `per_1k_sentences`, and `examples` (list of matched strings, max 20).

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_prose_metrics.py
def test_coordinate_lists_flags_four_item_series():
    text = ("Non-diminishing use does not erase planning law, tenancy, "
            "occupancy, safety, or the continuing redemption right.")
    result = prose_metrics.coordinate_lists([text])
    assert result["count"] == 1
    assert "planning law, tenancy" in result["examples"][0]


def test_coordinate_lists_ignores_three_item_series():
    # Three items is ordinary English; four or more is the tell.
    text = "He brought bread, cheese, and wine."
    assert prose_metrics.coordinate_lists([text])["count"] == 0


def test_coordinate_lists_per_1k_sentences_is_normalised():
    listed = ("alpha, beta, gamma, delta, and epsilon follow. ") * 2
    plain = "Short one. " * 8
    result = prose_metrics.coordinate_lists([listed + plain])
    assert result["count"] == 2
    assert result["per_1k_sentences"] == 200.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_prose_metrics.py -q`
Expected: FAIL — `AttributeError: module 'prose_metrics' has no attribute 'coordinate_lists'`.

- [ ] **Step 3: Write minimal implementation**

```python
# add to skill/scripts/prose_metrics.py
COORDINATE_LIST_RE = re.compile(
    r"(?:[\w'-]+(?:\s+[\w'-]+){0,3},\s+){3,}(?:and|or)\s+[\w'-]+",
    re.IGNORECASE,
)


def coordinate_lists(paragraph_texts: list[str]) -> dict[str, object]:
    """Count exhaustive coordinated series of four or more items.

    Four-plus item lists are the prose signature of completeness-seeking:
    the writer enumerates the whole category instead of choosing the one
    item that carries the point. Three items is ordinary English and is
    deliberately not flagged.
    """
    examples: list[str] = []
    sentence_total = 0
    for paragraph in paragraph_texts:
        sentence_total += len(split_sentences(paragraph))
        for match in COORDINATE_LIST_RE.finditer(paragraph):
            examples.append(re.sub(r"\s+", " ", match.group(0)).strip())
    per_1k = round(len(examples) / sentence_total * 1000, 2) if sentence_total else 0.0
    return {
        "count": len(examples),
        "per_1k_sentences": per_1k,
        "examples": examples[:20],
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_prose_metrics.py -q`
Expected: PASS, 7 passed.

- [ ] **Step 5: Commit**

```bash
git add skill/scripts/prose_metrics.py tests/test_prose_metrics.py
git commit -m "feat: detect exhaustive coordinate lists in narrated prose"
```

---

### Task 3: Abstract-subject detector

**Files:**
- Modify: `skill/scripts/prose_metrics.py`
- Test: `tests/test_prose_metrics.py`

**Interfaces:**
- Consumes: `split_sentences` from Task 1.
- Produces: `abstract_subjects(paragraph_texts: list[str]) -> dict[str, object]` returning `count`, `share_of_sentences`, `examples`.

This measure is **permanently advisory**. It reports locations for editorial judgment and never gains a threshold.

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_prose_metrics.py
def test_abstract_subjects_flags_concept_in_subject_slot():
    text = ("The document matters because a bid and a paid sale differ. "
            "Each power arrives with a boundary.")
    result = prose_metrics.abstract_subjects([text])
    assert result["count"] == 2


def test_abstract_subjects_ignores_concrete_actors():
    text = "The treasurer registers the certificate. Gazzaniga asked why."
    assert prose_metrics.abstract_subjects([text])["count"] == 0


def test_abstract_subjects_share_is_normalised():
    text = "The document matters. A clerk signed it."
    assert prose_metrics.abstract_subjects([text])["share_of_sentences"] == 0.5
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_prose_metrics.py -q`
Expected: FAIL — `AttributeError: module 'prose_metrics' has no attribute 'abstract_subjects'`.

- [ ] **Step 3: Write minimal implementation**

```python
# add to skill/scripts/prose_metrics.py
ABSTRACT_NOUNS = frozenset({
    "document", "power", "duty", "protection", "obligation", "requirement",
    "boundary", "distinction", "mechanism", "process", "approach", "concept",
    "principle", "framework", "structure", "pattern", "relationship",
    "uncertainty", "ambiguity", "tension", "tradeoff", "trade-off",
    "difference", "similarity", "importance", "significance", "value",
    "question", "answer", "point", "issue", "problem", "solution",
    "insurance", "redemption", "use", "rent", "notice", "certificate",
    "statute", "provision", "rule", "law", "right", "interest", "position",
    "stage", "state", "step", "phase", "case", "result", "effect", "cause",
    "reason", "purpose", "goal", "benefit", "cost", "risk", "consequence",
})

ABSTRACT_SUBJECT_RE = re.compile(
    r"^(?:The|A|An|Each|Every|This|That)\s+([\w'-]+)\s+(?:\w+s|is|are|was|were|has|have|can|may|must|does|do)\b",
    re.IGNORECASE,
)


def abstract_subjects(paragraph_texts: list[str]) -> dict[str, object]:
    """Count sentences whose grammatical subject is an abstract noun.

    Advisory only. Real writers put people and things in the subject slot
    and concepts in the predicate; "The document matters" is the inversion.
    The noun list is curated rather than exhaustive, so this reports
    candidates for a human, never a verdict.
    """
    examples: list[str] = []
    sentences: list[str] = []
    for paragraph in paragraph_texts:
        sentences.extend(split_sentences(paragraph))
    for sentence in sentences:
        match = ABSTRACT_SUBJECT_RE.match(sentence.strip())
        if match and match.group(1).lower() in ABSTRACT_NOUNS:
            examples.append(sentence.strip()[:160])
    share = round(len(examples) / len(sentences), 4) if sentences else 0.0
    return {
        "count": len(examples),
        "share_of_sentences": share,
        "examples": examples[:20],
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_prose_metrics.py -q`
Expected: PASS, 10 passed.

- [ ] **Step 5: Commit**

```bash
git add skill/scripts/prose_metrics.py tests/test_prose_metrics.py
git commit -m "feat: report abstract-noun sentence subjects as advisory signal"
```

---

### Task 4: Concept load and arithmetic tier density

**Files:**
- Modify: `skill/scripts/prose_metrics.py`
- Test: `tests/test_prose_metrics.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `arithmetic_density(text: str) -> dict[str, float]` returning `count`, `per_10k_words`; and `ARITHMETIC_TIERS: dict[str, tuple[float, float]]` mapping tier name to `(low, high)` band per 10k words.

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_prose_metrics.py
def test_arithmetic_density_counts_operation_language():
    text = "You multiply the weights, take the gradient, then the chain rule applies."
    result = prose_metrics.arithmetic_density(text)
    assert result["count"] == 3


def test_arithmetic_density_normalises_per_10k_words():
    text = ("multiply " + "filler " * 999)
    assert prose_metrics.arithmetic_density(text)["per_10k_words"] == 10.0


def test_arithmetic_tiers_place_ed1_baseline_in_light():
    # Question Machine ed1 measured 7.1 arithmetic terms per 10k words and
    # taught successfully. "light" must contain that value.
    low, high = prose_metrics.ARITHMETIC_TIERS["light"]
    assert low <= 7.1 <= high


def test_arithmetic_tiers_none_excludes_ed1_baseline():
    low, high = prose_metrics.ARITHMETIC_TIERS["none"]
    assert not (low <= 7.1 <= high)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_prose_metrics.py -q`
Expected: FAIL — `AttributeError: module 'prose_metrics' has no attribute 'arithmetic_density'`.

- [ ] **Step 3: Write minimal implementation**

```python
# add to skill/scripts/prose_metrics.py
ARITHMETIC_RE = re.compile(
    r"\b(?:multiply|multiplied|divide[ds]?|subtract(?:ed)?|sum of|product of"
    r"|square(?:d|s|\s+root)?|derivative|gradient|slope|chain rule|matrix"
    r"|matrices|vector|dot product|weighted sum|partial derivative"
    r"|logarithm|exponent(?:ial)?|coefficient)\b",
    re.IGNORECASE,
)

# Bands are arithmetic terms per 10,000 words. Calibrated from The Question
# Machine ed1 (7.1/10k), which taught successfully and scored the corpus
# maximum. An absolute cap would have failed the book we are reproducing,
# so density is always judged against the brief's declared tier.
ARITHMETIC_TIERS: dict[str, tuple[float, float]] = {
    "none": (0.0, 2.0),
    "light": (2.0, 12.0),
    "quantitative": (12.0, 30.0),
    "symbolic": (30.0, 1000.0),
}


def arithmetic_density(text: str) -> dict[str, float]:
    """Rate of arithmetic-operation language per 10,000 words."""
    total_words = len(text.split())
    count = len(ARITHMETIC_RE.findall(text))
    per_10k = round(count / total_words * 10000, 2) if total_words else 0.0
    return {"count": count, "per_10k_words": per_10k}


def arithmetic_tier_verdict(per_10k: float, tier: str) -> dict[str, object]:
    """Compare measured density against the brief's declared tier band."""
    if tier not in ARITHMETIC_TIERS:
        return {"tier": tier, "known": False, "within_band": True}
    low, high = ARITHMETIC_TIERS[tier]
    return {
        "tier": tier,
        "known": True,
        "band": [low, high],
        "measured": per_10k,
        "within_band": low <= per_10k <= high,
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_prose_metrics.py -q`
Expected: PASS, 14 passed.

- [ ] **Step 5: Commit**

```bash
git add skill/scripts/prose_metrics.py tests/test_prose_metrics.py
git commit -m "feat: measure arithmetic density against declared brief tier"
```

---

### Task 5: Wire measures into the prose_qc report and receipt

**Files:**
- Modify: `skill/scripts/prose_qc.py`
- Test: `tests/test_prose_qc_metrics.py`

**Interfaces:**
- Consumes: `rhythm`, `coordinate_lists`, `abstract_subjects`, `arithmetic_density` from Tasks 1–4.
- Produces: a `metrics` key in the report text and in `prose-style-receipt.json`. Additive only — every existing key keeps its meaning and position.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_prose_qc_metrics.py
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "skill" / "scripts" / "prose_qc.py"


def _write_chapters(tmp_path):
    chapters = tmp_path / "chapters"
    chapters.mkdir()
    (chapters / "ch01.md").write_text(
        "## Chapter 1 - Test\n\n"
        "A clerk signed the form. She waited.\n\n"
        "The treasurer registered it, filed it, stamped it, indexed it, and left.\n",
        encoding="utf-8",
    )
    return chapters


def test_report_contains_metrics_section(tmp_path):
    chapters = _write_chapters(tmp_path)
    out = tmp_path / "report.md"
    subprocess.run(
        [sys.executable, str(SCRIPT), "--chapters-dir", str(chapters), "--out", str(out)],
        check=True, cwd=REPO,
    )
    text = out.read_text(encoding="utf-8")
    assert "Shape metrics" in text
    assert "sentence_cv" in text


def test_receipt_contains_metrics_block(tmp_path):
    chapters = _write_chapters(tmp_path)
    out = tmp_path / "report.md"
    decisions = tmp_path / "decisions.json"
    receipt = tmp_path / "receipt.json"
    decisions.write_text(json.dumps({
        "reviewer": "test", "model": "test", "skillVersion": "test",
        "humanizer_applied": True, "accepted": [], "rejected": [],
        "rerunChecks": ["factual", "coverage-ledger", "narration", "prose"],
    }), encoding="utf-8")
    subprocess.run(
        [sys.executable, str(SCRIPT), "--chapters-dir", str(chapters),
         "--out", str(out), "--decisions", str(decisions),
         "--style-receipt-out", str(receipt)],
        check=True, cwd=REPO,
    )
    data = json.loads(receipt.read_text(encoding="utf-8"))
    assert "metrics" in data
    assert "rhythm" in data["metrics"]
    assert data["metrics"]["coordinate_lists"]["count"] == 1


def test_metrics_never_fail_the_run(tmp_path):
    """Measures are advisory in this task; --fail-on-style must ignore them."""
    chapters = tmp_path / "chapters"
    chapters.mkdir()
    (chapters / "ch01.md").write_text(
        "## Chapter 1\n\n" + ("Alpha, beta, gamma, delta, and epsilon follow. " * 10),
        encoding="utf-8",
    )
    out = tmp_path / "report.md"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--chapters-dir", str(chapters),
         "--out", str(out), "--fail-on-style"],
        cwd=REPO,
    )
    assert result.returncode == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_prose_qc_metrics.py -q`
Expected: FAIL — `assert "Shape metrics" in text`.

- [ ] **Step 3: Write minimal implementation**

In `skill/scripts/prose_qc.py`, add the import after the existing stdlib imports:

```python
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prose_metrics  # noqa: E402
```

Add a collector function beside `analyse_style`:

```python
def analyse_metrics(paragraphs: list[Paragraph], arithmetic_tier: str | None = None) -> dict[str, object]:
    """Shape measures. Advisory: reported, never a failure condition.

    Kept separate from analyse_style because the style families judge what
    the prose says, while these judge how uniformly it says it.
    """
    texts = [paragraph.text for paragraph in paragraphs]
    joined = "\n\n".join(texts)
    arith = prose_metrics.arithmetic_density(joined)
    block: dict[str, object] = {
        "rhythm": prose_metrics.rhythm(texts),
        "coordinate_lists": prose_metrics.coordinate_lists(texts),
        "abstract_subjects": prose_metrics.abstract_subjects(texts),
        "arithmetic": arith,
    }
    if arithmetic_tier:
        block["arithmetic_tier"] = prose_metrics.arithmetic_tier_verdict(
            float(arith["per_10k_words"]), arithmetic_tier
        )
    return block
```

In `report(...)`, append before the return:

```python
    metrics = analyse_metrics(paragraphs)
    lines.append("")
    lines.append("## Shape metrics (advisory)")
    lines.append("")
    rhythm_block = metrics["rhythm"]
    lines.append(f"- paragraph_cv: {rhythm_block['paragraph_cv']} (advisory, no threshold)")
    lines.append(f"- sentence_cv: {rhythm_block['sentence_cv']}")
    coord = metrics["coordinate_lists"]
    lines.append(f"- coordinate_lists: {coord['count']} ({coord['per_1k_sentences']} per 1k sentences)")
    abstract = metrics["abstract_subjects"]
    lines.append(f"- abstract_subjects: {abstract['count']} ({abstract['share_of_sentences']} of sentences)")
    lines.append(f"- arithmetic: {metrics['arithmetic']['per_10k_words']} per 10k words")
```

In `write_style_receipt(...)`, add `"metrics": analyse_metrics(paragraphs),` to the payload dict alongside the existing keys.

Add the CLI flag in `main()`:

```python
    parser.add_argument(
        "--arithmetic-tier",
        choices=sorted(prose_metrics.ARITHMETIC_TIERS),
        help="Brief's declared arithmetic tier; enables the band comparison.",
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_prose_qc_metrics.py tests/test_prose_metrics.py -q`
Expected: PASS, 17 passed.

Run the full suite to confirm the receipt change broke nothing:
`python3 -m pytest tests/ -q && python3 tools/validate_skills.py`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add skill/scripts/prose_qc.py tests/test_prose_qc_metrics.py
git commit -m "feat: report shape metrics in prose QC report and receipt"
```

---

### Task 6: Corpus regression test

**Files:**
- Test: `tests/test_corpus_regression.py`

**Interfaces:**
- Consumes: `prose_metrics` from Tasks 1–4.
- Produces: the empirical proof that thresholds split the corpus. Task 7 may not promote a measure to blocking unless this test passes.

The three corpora live outside version control. The test **skips** rather than fails when a corpus is absent, so CI stays green on a fresh clone.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_corpus_regression.py
"""Empirical thresholds, validated against three real books.

Known verdicts, from the design spec:
  Question Machine ed1        taught well   sentence_cv 0.72, lists 0
  Is There Anyone in Here?    good          sentence_cv 0.65, lists 0
  NS tax-sale book            weak          sentence_cv 0.51, lists 12

A threshold that does not reproduce this split is wrong.
"""
import importlib.util
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "prose_metrics", REPO / "skill" / "scripts" / "prose_metrics.py"
)
prose_metrics = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prose_metrics)

SENTENCE_CV_FLOOR = 0.60
COORDINATE_LIST_CEILING = 3.0

CORPORA = {
    "qm_ed1": REPO / "build" / "the-question-machine" / "chapters-narration",
    "consciousness": REPO / ".build" / "custom-learning-audiobooks"
                          / "is-there-anyone-in-here" / "chapters",
    "tax_sale": REPO / "docs" / "nova-scotia-tax-sale-book" / "chapters",
}


def _paragraphs(directory: Path) -> list[str]:
    texts: list[str] = []
    for path in sorted(directory.glob("ch*.md")):
        body = "\n".join(
            line for line in path.read_text(encoding="utf-8").splitlines()
            if not line.startswith("#")
        )
        texts.extend(
            block for block in body.split("\n\n") if len(block.split()) > 15
        )
    return texts


def _load(name: str) -> list[str]:
    directory = CORPORA[name]
    if not directory.is_dir():
        pytest.skip(f"corpus {name} not present at {directory}")
    paragraphs = _paragraphs(directory)
    if not paragraphs:
        pytest.skip(f"corpus {name} has no chapters")
    return paragraphs


@pytest.mark.parametrize("name", ["qm_ed1", "consciousness"])
def test_good_books_clear_the_sentence_cv_floor(name):
    result = prose_metrics.rhythm(_load(name))
    assert result["sentence_cv"] >= SENTENCE_CV_FLOOR


def test_weak_book_fails_the_sentence_cv_floor():
    result = prose_metrics.rhythm(_load("tax_sale"))
    assert result["sentence_cv"] < SENTENCE_CV_FLOOR


@pytest.mark.parametrize("name", ["qm_ed1", "consciousness"])
def test_good_books_clear_the_coordinate_list_ceiling(name):
    result = prose_metrics.coordinate_lists(_load(name))
    assert result["per_1k_sentences"] <= COORDINATE_LIST_CEILING


def test_weak_book_exceeds_the_coordinate_list_ceiling():
    result = prose_metrics.coordinate_lists(_load("tax_sale"))
    assert result["per_1k_sentences"] > COORDINATE_LIST_CEILING


def test_arithmetic_tier_does_not_penalise_the_book_that_taught():
    """Ed1 scored the corpus maximum for arithmetic and taught successfully."""
    joined = "\n\n".join(_load("qm_ed1"))
    density = prose_metrics.arithmetic_density(joined)
    verdict = prose_metrics.arithmetic_tier_verdict(
        float(density["per_10k_words"]), "light"
    )
    assert verdict["within_band"] is True
```

- [ ] **Step 2: Run test to verify it fails or skips honestly**

Run: `python3 -m pytest tests/test_corpus_regression.py -v`
Expected: 6 tests, each either PASS or SKIP with a named missing corpus. Any FAIL means a threshold is wrong — **stop and report the measured value; do not adjust the threshold to make the test green.**

- [ ] **Step 3: Record measured values in the plan**

Append the actual measured numbers as a comment block at the top of the test file so a future reader sees what the thresholds were calibrated against.

- [ ] **Step 4: Run the full suite**

Run: `python3 -m pytest tests/ -q && python3 tools/validate_skills.py`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add tests/test_corpus_regression.py
git commit -m "test: pin shape thresholds to the three-book corpus split"
```

---

### Task 7: Budgets in the author-facing references

**Files:**
- Modify: `skill/references/narration-style.md`
- Test: `tests/test_skill_prose_contract.py`

**Prerequisite:** Task 6 passes with no FAIL. If any corpus test failed, the sentence-CV floor stays advisory and this task ships the table with `advisory` in the enforcement column for that row.

- [ ] **Step 1: Add the budgets table**

Insert after the `NOVELTY AND DEPTH` block in the verbatim voice block:

```markdown
BUDGETS — these are caps you write toward, checked after every chapter:
- At most three genuinely new core terms per chapter.
- Six to ten durable book outcomes across the whole book.
- At most three temporary values and three symbolic steps in a spoken calculation.
- At least one real, sourced story anchor per chapter, or a recorded exemption.
- Arithmetic language stays inside the brief's declared tier band.
- Avoid coordinated lists of four or more items; name the one that carries the
  point. Three is ordinary English; four is a form being filled in.
- Vary sentence and paragraph length deliberately. Uniform rhythm is the most
  reliable signature of assembled prose.
```

- [ ] **Step 2: Delete the running-summary escape hatch**

In the `SECTION INPUT` block, change `the previous section text or running summary` to `the previous section text`. A running summary hands the author facts and strips cadence.

- [ ] **Step 3: Add the modal-conversion rule**

Append to the `NUMBERS, JARGON, FORM` block:

```markdown
- Convert statutory and API modals into people doing things. "The holder may
  collect rent" becomes "The rent cheques start coming to you." Where the modal
  must stay, name who is bound by it. Inherited modal stacks are what make
  regulatory subjects sound conditional and lifeless.
```

- [ ] **Step 4: Run the contract tests**

Run: `python3 -m pytest tests/test_skill_prose_contract.py -v`
Expected: PASS. If a pinned phrase assertion fails, read the assertion and update the test **only** when the phrase it pins was deliberately changed by this task; otherwise restore the phrase.

- [ ] **Step 5: Run the full suite and commit**

```bash
python3 -m pytest tests/ -q && python3 tools/validate_skills.py
git add skill/references/narration-style.md tests/
git commit -m "feat: give the author generation-time budgets instead of only receipts"
```

---

### Task 8: Verdict collapse and preserve-on-by-default

**Files:**
- Modify: `skill/references/learning-design.md`
- Test: `tests/test_skill_learning_contract.py`, `tests/test_learning_design_gate.py`

- [ ] **Step 1: Collapse the six verdicts to three**

Replace the `## Independent verdicts` list. Curriculum, chapter teaching, blind sequential beginner review, and comprehension pilot merge into **Teaching** (they measure one question). Prose style and narration merge into **Craft**. Packaging and acoustic become **Package**. Keep the existing sentence that the human listening verdict overrides all machine verdicts — it is already correct and must survive verbatim.

Add to the Teaching verdict:

```markdown
   **Prerequisite-before-use:** for every core concept, each declared
   prerequisite is taught, in narratable form, before the concept's first
   substantive use. Chapter plans already carry `prerequisites`; this checks
   delivery order, which is what a listener actually experiences.
```

- [ ] **Step 2: Flip the revision default**

Change the `revisionMode` default in the schema block from `"new-book"` to `"unset"`, and add below it:

```markdown
`revisionMode` must be set explicitly before drafting. Any brief that references
an existing book — by name, by edition, or through feedback about a book already
delivered — sets `first-edition-plus` and blocks until `preserve` is populated
with the governing question, narrative spine, successful examples, and chapter
jobs that are being kept.

**Gap feedback is an instruction to add, never to replace.** A listener saying
"I didn't learn X" means insert X's foundation into the existing spine. It does
not authorise re-planning the book around X. Record where the new material
inserts and name what stays. The Question Machine lost a working Descartes-to-
neural-nets spine to exactly this failure: the lineage was the explanation, and
with it gone the only remaining way to say what a neural net is was the notation.
```

- [ ] **Step 3: Add the ledger surface column**

In the coverage-ledger description, add a `surface` field taking `narration` or
`reference`, and state that the explanation-stack check applies book-wide across
the union of both surfaces rather than per chapter.

- [ ] **Step 4: Route math to the appendix**

Add to the gate order, after the drafting step:

```markdown
Symbols, derivations, and worked arithmetic belong in the non-narrated appendix
(`--non-narrated-appendix`), not in `chapters/`. Narrated chapters carry the
intuition and the lineage.
```

- [ ] **Step 5: Run tests and commit**

```bash
python3 -m pytest tests/ -q && python3 tools/validate_skills.py
git add skill/references/learning-design.md tests/
git commit -m "feat: collapse six verdicts to three and preserve spines by default"
```

---

### Task 9: Voice control panel and story ledger

**Files:**
- Create: `skill/references/voice-design.md`
- Modify: `skill/references/declaudification.md`, `skill/references/narration-style.md`
- Test: `tests/test_skill_prose_contract.py`

- [ ] **Step 1: Write the control panel**

Create `skill/references/voice-design.md` modeled on
`skills/fiction-book-development/references/style-and-scene-craft.md`: a table of
ten dials with observable ranges (narrator stance, sentence movement, diction,
evidence handling, concession, humour, exposition, story density, emphasis,
direct address), a requirement for 3–5 positive sample sentences written for the
project, and a pointer to `declaudification.md` for the prohibitions.

- [ ] **Step 2: Demote the ban list**

Add a header note to `declaudification.md` stating it is read at QC time, not at
drafting time, and that `voice-design.md` is the drafting-time instruction. Do
not delete any existing family — they still run in the linter.

- [ ] **Step 3: Add the story ledger contract**

Add to `narration-style.md` a `research/story-ledger.md` requirement: each entry
records what happened, named actors/place/date, source citation, the concept it
carries, and **the reversal** — what a reasonable person would have expected
instead. No reversal means it is an example, not a story. Sources are documented
and institutional only: published decisions, papers, post-mortems, news, real
repository history, named public figures acting in public roles. No private
individuals. Chapter plans name a ledger entry or record an exemption with a
reason.

- [ ] **Step 4: Run tests and commit**

```bash
python3 -m pytest tests/ -q && python3 tools/validate_skills.py
git add skill/references/voice-design.md skill/references/declaudification.md skill/references/narration-style.md
git commit -m "feat: add nonfiction voice control panel and story ledger contract"
```

---

### Task 10: Script consolidation (highest risk — attempt last)

**Files:**
- Create: `skill/scripts/book_qc.py`
- Modify: `skill/references/*.md` invocation examples

**Stop condition:** if the contract tests or `build_book.py` receipt verification
resist, **stop and report**. Do not weaken a test to make the merge land. The
value of this plan is in Tasks 1–9; this task is ergonomics.

- [ ] **Step 1:** Create `book_qc.py` as a thin dispatcher with
  `--profile learning|fiction` that calls the existing `prose_qc` and
  `learning_design_qc` entry points and emits one combined report with per-axis
  verdicts. Do **not** move code out of the existing scripts in this task.
- [ ] **Step 2:** Add `tests/test_book_qc_dispatch.py` asserting both profiles
  produce a combined report and that the existing receipts are unchanged
  byte-for-byte.
- [ ] **Step 3:** Run `python3 -m pytest tests/ -q && python3 tools/validate_skills.py`.
- [ ] **Step 4:** Commit only if green.

---

### Task 11: Docs and KB

**Files:**
- Modify: `docs/how-these-were-made.md`, `skills/longform-book-development/references/handoff-packet.md`
- Create: KB page in a separate `~/Developer/knowledge-base` worktree

- [ ] **Step 1:** Update both docs for the coverage-ledger `surface` column, the
  story ledger, and the voice control panel.
- [ ] **Step 2:** Draft `bundle/questions/audiobook-gate-consolidation.md` in the
  KB reconciling with `audiobook-learning-comprehension-gate.md` and
  `audiobook-prose-declaudification.md`, run `python3 tools/kb_lint.py` until
  clean, and open a KB PR. **Do not** edit the KB directly.
- [ ] **Step 3:** Commit repo docs; KB goes in its own PR.

---

## Self-Review

**Spec coverage:** PR1 measurement → Tasks 1–6. PR2 budgets and verdict collapse
→ Tasks 7–8. PR3 revision protection → Task 8 steps 2 and 4. PR4 prose craft →
Task 9. Script consolidation → Task 10 (resequenced last, rationale in
Architecture). Docs and KB obligations → Task 11. No spec section is unmapped.

**Type consistency:** `rhythm`, `coordinate_lists`, `abstract_subjects`,
`arithmetic_density`, `arithmetic_tier_verdict`, `split_sentences`,
`ARITHMETIC_TIERS` are defined in Tasks 1–4 and used under those exact names in
Tasks 5–6.

**Known deviation from spec:** the spec's PR1 merged the two QC scripts. This
plan defers that merge to Task 10 and ships the measures additively first. Same
scope, dependency-safe order, and the merge cannot break packaging on a night
when nobody is awake to catch it.
