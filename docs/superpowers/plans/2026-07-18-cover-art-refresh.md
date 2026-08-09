# Cover Art Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the flat-graphic cover look a first-class, contract-tested direction and stop generated raster covers from reading as AI, per `docs/superpowers/specs/2026-07-18-cover-art-refresh-design.md`.

**Architecture:** Text-only changes to four skill surfaces (`skill/references/cover-art.md`, `skill/SKILL.md`, `skills/custom-learning-audiobook/SKILL.md`, `skills/custom-learning-audiobook/references/package-and-qc.md`), driven TDD-style by new assertions in `tests/test_skill_cover_contract.py`. No pipeline, script, schema, or receipt changes.

**Tech Stack:** Markdown skill files; Python `unittest` (plain stdlib, no pytest). Interpreter: `/usr/local/bin/python3`.

## Global Constraints

- Working directory: the worktree at `/Users/dfakkeldy/Developer/explainer-audiobooks/.claude/worktrees/question-machine-audiobook-49cd42`, branch `claude/skill-cover-images-a52a59`.
- Every existing contract marker must survive, notably: "exactly three", "1600×2560", "2400×2400", "explicit pair selection", "paired receipt", "post-embed verification", "title strategy", "font", "line breaks", "Never run `replace_m4b_cover.py`", the complete paired command example, and every verification-only compatibility section. Never edit those sections.
- The at-least-one sentence uses the direction's capitalized proper name, verbatim where it appears: "At least one of the three candidates must be a Designed flat graphic or type-led direction".
- Wrap new Markdown prose at ~80 columns to match the surrounding files. The new tests compare against whitespace-flattened text, so wrapping is safe.
- Run the contract test with: `/usr/local/bin/python3 -m unittest tests.test_skill_cover_contract -v`. Full suite: `/usr/local/bin/python3 -m unittest discover -s tests`.
- This repo has no nightly/weekly ladder; PRs go straight to `main`.

---

### Task 1: Add failing contract tests

**Files:**
- Modify: `tests/test_skill_cover_contract.py` (append two methods and one helper inside `SkillCoverContractTests`)

**Interfaces:**
- Consumes: existing module-level `FILES` dict (keys "cover", "long", "custom", "package").
- Produces: `flattened(key)` helper plus marker strings that Tasks 2–3 must make true. Marker strings are the interface — copy them exactly.

- [ ] **Step 1: Append the helper and two test methods**

Add inside the `SkillCoverContractTests` class, after the last existing test method:

```python
    def flattened(self, key: str) -> str:
        return " ".join(FILES[key].read_text(encoding="utf-8").split())

    def test_route_parity_and_flat_graphic_slot(self) -> None:
        for key in ("cover", "package"):
            text = self.flattened(key)
            for marker in (
                "Designed flat graphic",
                "route follows the direction",
                "flat graphic or type-led direction",
            ):
                with self.subTest(file=key, marker=marker):
                    self.assertIn(marker, text)
        for key in ("cover", "long", "custom", "package"):
            text = self.flattened(key)
            for stale in (
                "generated raster art is mandatory",
                "Never choose SVG merely",
                "approved vector fallback",
                "Do not use SVG or programmatic vector artwork",
                "Do not substitute bespoke SVG",
            ):
                with self.subTest(file=key, stale=stale):
                    self.assertNotIn(stale, text)

    def test_raster_prompt_bans_ai_render_tells(self) -> None:
        text = self.flattened("cover")
        for marker in (
            "airbrushed radial glow",
            "winding road or river",
            "hyper-smooth 3D product render",
            "melted or smeared detail",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)
        for stale in ("cinematic editorial photograph", "painterly realism"):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, text)
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run: `/usr/local/bin/python3 -m unittest tests.test_skill_cover_contract -v 2>&1 | tail -20`
Expected: FAIL. `test_route_parity_and_flat_graphic_slot` fails on missing "Designed flat graphic" markers and on present stale phrases ("Never choose SVG merely" in cover, "generated raster art is mandatory" in package, "approved vector fallback" in cover and long, "Do not use SVG or programmatic vector artwork" in custom). `test_raster_prompt_bans_ai_render_tells` fails on all four missing anti-tell markers and both present stale phrases. All 16 pre-existing tests still pass.

Do not commit yet — the tree stays red until Task 3; the single green commit happens there.

---

### Task 2: Rewrite `skill/references/cover-art.md`

**Files:**
- Modify: `skill/references/cover-art.md` (nine edits: direction menu ~lines 186–193, Non-Negotiable Default ~174–184, Making the Art ~237–252, copy-ready prompt ~283–300, acceptance bar ~333–346, technical contract ~354–366)

**Interfaces:**
- Consumes: marker strings from Task 1.
- Produces: cover-file half of the new assertions. Task 3 mirrors the same sentences in the other three files.

Apply each edit with exact old→new replacement (old text is verbatim from the file):

- [ ] **Step 1: Add the Designed flat graphic row to the direction menu**

Old:
```markdown
| **Graphic spectacle** | High-impact colour field or dark void with one impossible visual event, distorted scale, or visual paradox; confident, sparse, emotionally immediate. | Futurism, psychology, high-concept ideas, ambitious popular nonfiction |
```

New:
```markdown
| **Graphic spectacle** | High-impact colour field or dark void with one impossible visual event, distorted scale, or visual paradox; confident, sparse, emotionally immediate. | Futurism, psychology, high-concept ideas, ambitious popular nonfiction |
| **Designed flat graphic** | Bold flat-ink illustration: one confident geometric or character mark, two-to-four flat colours, strong silhouette, mid-century poster sensibility; lively but not childish; built as compositor-native vector or flat raster art. | Technology, ideas, playful explainers, learning journeys, series identity |
```

- [ ] **Step 2: Add the at-least-one guarantee to Non-Negotiable Default**

Old:
```markdown
Choose the three most appropriate directions from this menu. Do not use a
weak/placeholder direction just to fill the count.
```

New:
```markdown
Choose the three most appropriate directions from this menu. Do not use a
weak/placeholder direction just to fill the count. At least one of the three
candidates must be a Designed flat graphic or type-led direction (Typographic
graphic system counts), so a designed, non-generated look is always offered.
```

- [ ] **Step 3: Make Documentary still life read as film photography**

Old:
```markdown
| **Documentary still life** | A real or generated physical scene, tool, specimen, artifact, or close crop lit like an editorial photograph; evocative rather than stock; subtle grain and depth. | History, practical skills, food, place, science, craft |
```

New:
```markdown
| **Documentary still life** | A real or generated physical scene, tool, specimen, artifact, or close crop lit like an editorial film photograph — visible grain, imperfect natural light, real-world staging; evocative rather than stock; never a glossy smooth 3D render. | History, practical skills, food, place, science, craft |
```

- [ ] **Step 4: Replace Making the Art items 1–2 with route parity**

Old:
```markdown
1. **Generated image art** when an image-generation tool is available. Use the
   image tool directly (for example, `image_generate`), not a cheap text model
   inventing a generic SVG of icons, cards, arrows, or a house-shaped diagram.
   Generate at portrait ratio, then compose the chosen art at 1600×2560. Treat
   generated art as visual illustration, not documentary evidence.
2. **Bespoke SVG illustration is an explicit fallback, not a peer default.** Use
   it only when the user specifically requests vector art, or when image
   generation is unavailable and the user approves the fallback after the
   limitation is explained. Never choose SVG merely because it is faster,
   deterministic, or easier for a text model to produce. SVG must still look
   like deliberate editorial art, not a slide icon.
```

New:
```markdown
1. **The render route follows the direction, not tool availability.** Designed
   flat graphic and Typographic graphic system candidates are built as
   compositor-native SVG or flat raster art with the same craft bar as any
   editorial illustration — deliberate geometry, one confident mark, flat
   inks — never a slide icon. Photographic, collage, and illustrative print
   directions use the image-generation tool directly (for example,
   `image_generate`), not a cheap text model inventing a generic SVG of icons,
   cards, arrows, or a house-shaped diagram. Neither route is a fallback for
   the other.
2. **Generated image art** comes out of the image tool at portrait ratio; then
   compose the chosen art at 1600×2560. Treat generated art as visual
   illustration, not documentary evidence.
```

- [ ] **Step 5: Replace the visual-language menu in the copy-ready prompt**

Old:
```text
Visual language: [CHOOSE ONE: cinematic editorial photograph / tactile cut-paper
collage / expressive ink and gouache / refined screen print / painterly realism /
surreal editorial illustration].
```

New:
```text
Visual language: [CHOOSE ONE: refined screen print / risograph print / woodcut
or linocut / gouache poster illustration / halftone editorial illustration /
tactile cut-paper collage / grainy film photograph with natural, imperfect
light].
```

- [ ] **Step 6: Append the AI-tell anti-brief to the negative block**

Old:
```text
mockup, no audiobook icon, no interface, no dashboard, no floating UI cards, no
generic infographic, no stock-photo look, no random symbols, no collage of tiny
objects, no split-screen, no decorative icon cloud, no close imitation of any
named artist, designer, publisher, or existing book cover.
```

New:
```text
mockup, no audiobook icon, no interface, no dashboard, no floating UI cards, no
generic infographic, no stock-photo look, no random symbols, no collage of tiny
objects, no split-screen, no decorative icon cloud, no close imitation of any
named artist, designer, publisher, or existing book cover. No AI-render tells:
no centered glowing object, no airbrushed radial glow, no perfectly smooth
gradients, no paper-cut layered landscape with a winding road or river, no
hyper-smooth 3D product render, no melted or smeared detail, no uniform digital
sheen.
```

- [ ] **Step 7: Add the AI-clocked rejection line to the acceptance bar**

Old:
```markdown
- uses an unearned premium cliché (gold foil effect, arbitrary smoke, faux
  luxury marble, generic starfield) instead of a visual argument;
```

New:
```markdown
- uses an unearned premium cliché (gold foil effect, arbitrary smoke, faux
  luxury marble, generic starfield) instead of a visual argument;
- would be clocked as AI-generated at a glance — waxy smoothness, airbrushed
  glow, melted or smeared detail, or a trope composition such as a glowing
  centered orb or a paper-cut valley with a winding path;
```

- [ ] **Step 8: Update the two Technical Contract bullets that demote SVG**

Old:
```markdown
- Raster art may be PNG, JPEG, WebP, or GIF. Self-contained SVG remains an
  explicit-request or approved-unavailable-image-tool fallback. Use
  high-resolution portrait art and no external image URLs.
```

New:
```markdown
- Raster art may be PNG, JPEG, WebP, or GIF. Self-contained SVG is a peer
  route for Designed flat graphic and type-led candidates. Use
  high-resolution portrait art and no external image URLs.
```

Old:
```markdown
- A complete SVG example remains available at
  `references/cover-art-example.svg`; use it only as a structural reference for
  an approved vector fallback, not a visual template.
```

New:
```markdown
- A complete SVG example remains available at
  `references/cover-art-example.svg`; use it only as a structural reference for
  vector-route candidates, not a visual template.
```

- [ ] **Step 9: Run the new tests — cover-file assertions now pass**

Run: `/usr/local/bin/python3 -m unittest tests.test_skill_cover_contract -v 2>&1 | tail -15`
Expected: `test_raster_prompt_bans_ai_render_tells` PASSES. `test_route_parity_and_flat_graphic_slot` still FAILS, but only on: missing markers in "package"; stale "generated raster art is mandatory" and "Do not substitute bespoke SVG" in "package"; stale "approved vector fallback" in "long"; stale "Do not use SVG or programmatic vector artwork" and "Do not substitute bespoke SVG" in "custom". No "cover" subtest fails. All 16 pre-existing tests still pass.

---

### Task 3: Rewrite the other three surfaces and go green

**Files:**
- Modify: `skills/custom-learning-audiobook/references/package-and-qc.md` (~lines 431–439)
- Modify: `skills/custom-learning-audiobook/SKILL.md` (~lines 285–292 and 536–538)
- Modify: `skill/SKILL.md` (~lines 477–479 and 627–630)

**Interfaces:**
- Consumes: marker strings from Task 1; the same at-least-one sentence and route-parity phrase used in Task 2.
- Produces: a fully green contract test.

- [ ] **Step 1: Replace the raster-mandatory paragraph in package-and-qc.md**

Old:
```markdown
When an image-generation tool is available, generated raster art is mandatory;
keep it text-free, with no logos or watermarks. Do not substitute bespoke SVG,
programmatic vector art, diagrams, or icon compositions. Use SVG only when the
user explicitly requests vector art or approves it as a fallback after image
generation is confirmed unavailable. Rights-cleared raster art remains
acceptable; never copy or closely imitate a specific existing cover. Include a
bright/high-key option unless three dark directions are truly warranted, and
reject a generic template, slide icon, AI wallpaper, or recolour before the user
sees it.
```

New:
```markdown
The render route follows the direction, not tool availability. At least one of
the three candidates must be a Designed flat graphic or type-led direction,
composed as compositor-native SVG or flat raster art; photographic, collage,
and illustrative print directions use the image-generation tool. Keep generated
art text-free, with no logos or watermarks, and follow the print-native visual
languages and AI-tell anti-brief in `cover-art.md`; reject any candidate a
stranger would clock as AI-generated. Rights-cleared raster art remains
acceptable; never copy or closely imitate a specific existing cover. Include a
bright/high-key option unless three dark directions are truly warranted, and
reject a generic template, slide icon, AI wallpaper, or recolour before the user
sees it.
```

- [ ] **Step 2: Replace the raster-first paragraph in the custom-learning SKILL.md**

Old:
```markdown
   Use original generated raster art from the strongest available image tool
   (use it directly, e.g. `image_gen`) whenever one is available. Do not
   substitute bespoke SVG, programmatic vector art, diagrams, or icon
   compositions merely because they are faster or deterministic. SVG is allowed
   only when the user explicitly requests vector art, or when no image-generation
   tool is available and the user approves that fallback after seeing the
   limitation. Rights-cleared raster photography or art remains acceptable when
   it is the stronger editorial choice. Use the copy-ready editorial prompt in
```

New:
```markdown
   The render route follows the direction, not tool availability. At least one
   of the three candidates must be a Designed flat graphic or type-led
   direction, composed as deliberate vector or flat raster art; photographic,
   collage, and illustrative print directions use the strongest available image
   tool directly (e.g. `image_gen`), never a lazy icon composition.
   Rights-cleared raster photography or art remains acceptable when
   it is the stronger editorial choice. Use the copy-ready editorial prompt in
```

- [ ] **Step 3: Replace the no-SVG bullet in the custom-learning SKILL.md**

Old:
```markdown
- Do not use SVG or programmatic vector artwork for a generated cover when an
  image-generation tool is available. Generate raster artwork and inspect it at
  full size and thumbnail size as part of each complete art-and-type candidate.
```

New:
```markdown
- Match the render route to the direction: vector or flat raster art for
  Designed flat graphic and type-led candidates, image-tool raster for
  photographic and collage candidates. Inspect every render at full size and
  thumbnail size as part of each complete art-and-type candidate.
```

- [ ] **Step 4: Update the route sentence in skill/SKILL.md**

Old:
```markdown
Use the strongest available image-generation tool directly for the art (for
example, `image_generate`), rather than asking a cheaper text model to draw a
generic SVG of icons, cards, arrows, or diagrams. Follow the copy-ready prompt in
```

New:
```markdown
Match the render route to the direction: compose flat-graphic and type-led
candidates as deliberate vector or flat raster art, and use the strongest
available image-generation tool directly for photographic, collage, and
illustrative print art (for example, `image_generate`), rather than asking a
cheaper text model to draw a generic SVG of icons, cards, arrows, or diagrams.
Follow the copy-ready prompt in
```

- [ ] **Step 5: Update the reference-list bullet in skill/SKILL.md**

Old:
```markdown
- `references/cover-art.md` — how to design, render, review, and explicitly
  select three complete art-and-type candidates; ships with
  `cover-art-example.svg` as a structural reference for an approved vector
  fallback.
```

New:
```markdown
- `references/cover-art.md` — how to design, render, review, and explicitly
  select three complete art-and-type candidates; ships with
  `cover-art-example.svg` as a structural reference for vector-route
  candidates.
```

- [ ] **Step 6: Run the contract test — everything green**

Run: `/usr/local/bin/python3 -m unittest tests.test_skill_cover_contract -v 2>&1 | tail -6`
Expected: `Ran 18 tests` … `OK`.

- [ ] **Step 7: Sweep for leftover demotion language**

Run: `grep -rn -i 'vector fallback\|raster art is mandatory\|Never choose SVG' skill/ skills/`
Expected: no output. If anything appears, replace it using the route-parity phrasing from Step 1 and re-run Step 6.

- [ ] **Step 8: Run the full suite**

Run: `/usr/local/bin/python3 -m unittest discover -s tests 2>&1 | tail -3`
Expected: all tests pass, `OK`.

- [ ] **Step 9: Commit**

```bash
git add tests/test_skill_cover_contract.py skill/references/cover-art.md \
  skill/SKILL.md skills/custom-learning-audiobook/SKILL.md \
  skills/custom-learning-audiobook/references/package-and-qc.md
git commit -m "feat: flat-graphic cover direction + de-AI'd raster prompts

Route follows direction (vector is a peer route, not a fallback), at
least one flat-graphic/type-led candidate per book, print-native visual
languages, AI-tell anti-brief, all pinned by contract tests.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: Amend the spec, push, and open the PR

**Files:**
- Modify: `docs/superpowers/specs/2026-07-18-cover-art-refresh-design.md` (Change 1 and Change 3 sections)

**Interfaces:**
- Consumes: the final marker list from Task 1 and the surface list from Tasks 2–3.
- Produces: a spec that matches what shipped; the PR.

- [ ] **Step 1: Record the widened scope in the spec**

In the spec's "Change 1" section, after the package-and-qc.md bullet list, append:

```markdown
Files: `skill/SKILL.md` and `skills/custom-learning-audiobook/SKILL.md`
(scope widened during planning)

- Both skill bodies carried their own copies of the demotion rule — including
  a hard "Do not use SVG or programmatic vector artwork for a generated cover
  when an image-generation tool is available" bullet in the custom-learning
  SKILL.md that would have overridden the reference fix at runtime. Both are
  replaced with the same route-parity rule.
```

In the spec's "Change 3" section, replace the final paragraph (the one beginning "Also assert the removed rules stay removed") with:

```markdown
Also assert the removed rules stay removed across all four surfaces
("cover", "long", "custom", "package"), on whitespace-flattened text:
`assertNotIn` for "generated raster art is mandatory", "Never choose SVG
merely", "approved vector fallback", "Do not use SVG or programmatic vector
artwork", and "Do not substitute bespoke SVG".
```

- [ ] **Step 2: Commit the spec amendment**

```bash
git add docs/superpowers/specs/2026-07-18-cover-art-refresh-design.md
git commit -m "docs: widen cover-art refresh scope to both SKILL.md surfaces

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

- [ ] **Step 3: Push and open the PR (base main — this repo has no nightly ladder)**

```bash
git push -u origin claude/skill-cover-images-a52a59
gh pr create --base main \
  --title "Cover art refresh: flat-graphic direction + de-AI'd raster prompts" \
  --body "$(cat <<'EOF'
## Summary
- Adds **Designed flat graphic** as a first-class cover direction; the render
  route now follows the direction instead of tool availability, and every
  book's three candidates must include at least one flat-graphic or type-led
  option.
- De-AIs the raster route: print-native visual languages, an explicit AI-tell
  anti-brief in the image prompt, and an acceptance-bar rejection for covers a
  stranger would clock as AI.
- Pins all of it in `test_skill_cover_contract.py` (18 tests green), including
  assertNotIn guards so the old raster-mandatory / SVG-fallback rules cannot
  silently return.

Spec: `docs/superpowers/specs/2026-07-18-cover-art-refresh-design.md`
Plan: `docs/superpowers/plans/2026-07-18-cover-art-refresh.md`

## Test plan
- [x] `/usr/local/bin/python3 -m unittest discover -s tests` — all green
- [x] `grep -rn -i 'vector fallback|raster art is mandatory|Never choose SVG' skill/ skills/` — empty

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Expected: PR URL printed. Report it and run `git status --short --branch` to confirm a clean tree.
