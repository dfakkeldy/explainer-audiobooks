# Task 1 Report

Status: DONE

## Files changed

- `skill/scripts/refresh_epub_cover.py`
- `tests/test_refresh_epub_cover.py`

## Commit

- `f729552 feat: add safe EPUB cover replacement`

## Commands and exact test outcomes

1. `python3 -m unittest tests.test_refresh_epub_cover -v`
   - Red phase: failed to import `tests.test_refresh_epub_cover` with `ModuleNotFoundError: No module named 'refresh_epub_cover'`.
2. `python3 -m unittest tests.test_refresh_epub_cover -v`
   - Green phase: `Ran 7 tests in 0.309s` / `OK`.
3. `python3 -m unittest discover -s tests -v`
   - Full suite: `Ran 12 tests in 3.107s` / `OK`.
4. `git diff --check`
   - Passed with no output.

## Self-review

- Confirmed OPF discovery is namespace-tolerant and requires one internal rootfile.
- Confirmed modern `cover-image` lookup takes precedence and legacy metadata fallback resolves by manifest ID.
- Confirmed missing, ambiguous, external, traversal, non-PNG, and wrong-size paths fail closed before replacing the requested output.
- Confirmed the rebuilt EPUB preserves member ordering and bytes except for the declared cover, with `mimetype` first and stored.
- Confirmed temporary output is validated before atomic `os.replace`, including same-path input/output safety.
- Confirmed the result reports OPF path, cover member, dimensions, and SHA-256 of the new cover.
- Confirmed only the two Task 1 source/test files were committed.

## Concerns

None.

---

## Fix Report

Status: DONE

### Files changed

- `skill/scripts/refresh_epub_cover.py`
- `tests/test_refresh_epub_cover.py`

### Commit

- `48a1b31 fix: harden EPUB cover replacement validation`

### Commands and exact test outcomes

1. `python3 -m unittest tests.test_refresh_epub_cover -v`
   - Red phase: `Ran 10 tests in 0.429s` / `FAILED (failures=2, errors=1)`.
   - The valid-header truncated PNG and fragment href were incorrectly accepted; rebuilt-payload validation did not exist.
2. `python3 -m unittest tests.test_refresh_epub_cover.RefreshEpubCoverTests.test_rejects_png_with_decodable_zlib_but_incomplete_pixels -v`
   - Additional red phase: `Ran 1 test in 0.112s` / `FAILED (failures=1)` because an empty but valid zlib stream was accepted as image data.
3. `python3 -m unittest tests.test_refresh_epub_cover -v`
   - Green phase: `Ran 11 tests in 0.426s` / `OK`.
4. `python3 -m unittest discover -s tests -v`
   - Full suite: `Ran 16 tests in 3.528s` / `OK`.
5. `git diff --check`
   - Passed with no output.

### Self-review

- PNG validation now walks the full chunk stream, verifies each CRC, requires well-formed IHDR/IDAT/IEND structure, fully decompresses IDAT data, and validates scanline lengths and filter bytes for both non-interlaced and Adam7 images.
- Regression coverage includes a truncated PNG with a valid signature and IHDR plus a structurally complete PNG whose zlib stream contains insufficient pixel data.
- Internal EPUB paths now reject URL fragments explicitly instead of silently discarding them during cover-member resolution.
- Before `os.replace`, rebuilt validation independently compares the complete member-name/order list and byte-compares every non-cover payload against the source, in addition to checking stored-first `mimetype` and exact cover bytes/dimensions.
- Temporary-file cleanup and same-path input/output behavior remain unchanged.

### Concerns

None.
