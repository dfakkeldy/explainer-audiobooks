# Task 6 Follow-up Report

## RED

The strengthened skill contract failed with 75 findings. It caught active
single-cover `make_cover.py --spec ... cover-N.png` guidance, missing complete
paired API/CLI arguments, incomplete candidate layout, and chronology assertions
that were not robust to Markdown line wrapping.

## GREEN

- Replaced active single-cover render examples in both skills and both cover/QC
  references with three candidate directories and complete
  `render_cover_pair(...)` examples using all eight artifact paths.
- Added complete executable examples for `select-pair`, paired `build_book.py`,
  `replace_m4b_cover.py`, paired `verify`, and paired dry-run/apply sync.
- Corrected the package layout to show both schema-v2 variants, outputs,
  thumbnails, render receipts, and the selected paired receipt.
- Rewrote the remaining unqualified public single-cover assembly paragraph.
- Strengthened both unit contracts and `validate_skills.py` to require the
  complete interfaces and reject active single-cover renderer commands.

Verification:

- Focused skill-cover contract: 15 tests passed.
- Skill validator: clean.
- Full suite: 166 tests passed.
- `git diff --check`: clean.

No private/generated book artifact or installed-skill symlink was changed.
