# Bright Cover Default Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make bright/high-key the default tone for newly composed audiobook covers while retaining an explicit dark option.

**Architecture:** `make_cover.py` owns the command-line default and passes its tone value unchanged to the SVG and raster composition paths. A focused CLI regression test captures the generated temporary SVG to prove an omitted `--tone` uses bright rendering and an explicit `--tone dark` still selects dark rendering.

**Tech Stack:** Python 3 standard library, `unittest`, `argparse`.

## Global Constraints

- Change future cover defaults only; do not alter existing cover artifacts.
- Preserve `--tone dark` as a supported explicit command-line choice.
- Do not add dependencies or automatic artwork-brightness analysis.
- Use a red-green test cycle before changing production code.

---

### Task 1: Bright command-line default and regression coverage

**Files:**
- Modify: `tests/test_make_cover.py`
- Modify: `skill/scripts/make_cover.py:18-25,457-467`

**Interfaces:**
- Consumes: `make_cover.main()` and its existing `argparse` command-line interface.
- Produces: omitted `--tone` renders with the bright palette; `--tone dark` renders with the dark palette.

- [ ] **Step 1: Write the failing CLI regression test**

```python
def test_cli_defaults_to_bright_tone_and_keeps_dark_opt_in(self) -> None:
    def render_svg(arguments: list[str]) -> str:
        captured: list[str] = []

        def capture(svg_path: str, _png_path: str) -> bool:
            captured.append(Path(svg_path).read_text(encoding="utf-8"))
            return True

        with tempfile.TemporaryDirectory() as raw_dir, \\
                mock.patch.object(sys, "argv", [str(SCRIPT), *arguments,
                                                 "--out", str(Path(raw_dir) / "cover.png")]), \\
                mock.patch.object(make_cover, "rasterize", side_effect=capture):
            self.assertEqual(0, make_cover.main())
        return captured[0]

    bright_svg = render_svg(["--title", "A Better System"])
    dark_svg = render_svg(["--title", "A Better System", "--tone", "dark"])

    self.assertIn('fill="#17130F"', bright_svg)
    self.assertIn('fill="#F6F3EE"', dark_svg)
```

- [ ] **Step 2: Run the focused test to verify it fails because the current default is dark**

Run: `python3 -m unittest tests.test_make_cover.MakeCoverArtLoadingTests.test_cli_defaults_to_bright_tone_and_keeps_dark_opt_in -v`

Expected: `FAIL` because the omitted tone produces `fill="#F6F3EE"` instead of the bright ink colour.

- [ ] **Step 3: Make the minimal production change**

```python
ap.add_argument("--tone", default="bright", choices=("dark", "bright"),
                help="Cover background tone; defaults to bright; use dark for cinematic covers")
```

Update the module-level option list to say `--tone bright` is the default high-key background and `--tone dark` is the explicit cinematic alternative.

- [ ] **Step 4: Run the focused test to verify it passes**

Run: `python3 -m unittest tests.test_make_cover.MakeCoverArtLoadingTests.test_cli_defaults_to_bright_tone_and_keeps_dark_opt_in -v`

Expected: `OK` with one test run.

- [ ] **Step 5: Run repository verification**

Run: `python3 -m unittest discover -s tests -v && python3 tools/validate_skills.py && git diff --check`

Expected: all Python tests and the skill validator exit 0; `git diff --check` emits no whitespace errors.

- [ ] **Step 6: Commit the implementation**

```bash
git add skill/scripts/make_cover.py tests/test_make_cover.py
git commit -m "fix: default audiobook covers to bright"
```
