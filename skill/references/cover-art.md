# Award-Worthy Audiobook Covers

## Universal paired-cover rule

Every new book develops exactly three coordinated portrait/square candidates.
Each direction shares one source-art identity but has two deliberately composed
specifications: `cover.png` at 1600×2560 for the EPUB portrait and
`m4b-cover.png` at 2400×2400 for the M4B square. Review both full-size images and
both thumbnails together. The user makes an explicit pair selection; never mix
variants or select automatically. That choice becomes a paired receipt before
packaging, followed by post-embed verification.

The chronological contract is: research → three source directions →
portrait/square render pairs → thumbnail review → explicit pair selection →
paired receipt → EPUB portrait + M4B square embedding → post-embed verification
→ governed public/iCloud/site sync. Legacy single-cover receipts and renderer
flags are verification-only compatibility; do not teach them for new work.


### Complete paired command example

Create exactly three directories, `candidate-1/`, `candidate-2/`, and
`candidate-3/`. Each contains schema-v2 `cover-spec.json` and
`m4b-cover-spec.json`, shared source art, and portrait/square outputs,
thumbnails, and receipts. Repeat this call for candidates 1 through 3:

```python
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path("skill/scripts").resolve()))
from cover_pairs import render_cover_pair

PAIR = Path(os.environ["PAIR"])
render_cover_pair(
    portrait_spec=PAIR / "cover-spec.json",
    square_spec=PAIR / "m4b-cover-spec.json",
    portrait_output=PAIR / "cover.png",
    square_output=PAIR / "m4b-cover.png",
    portrait_thumbnail=PAIR / "cover-thumbnail.png",
    square_thumbnail=PAIR / "m4b-cover-thumbnail.png",
    portrait_receipt=PAIR / "cover-render.json",
    square_receipt=PAIR / "m4b-cover-render.json",
)
```

After human review selects one pair, run the complete governed sequence:

```bash
PAIR="$DIST/candidate-$SELECTED"
/usr/local/bin/python3 skill/scripts/cover_receipts.py select-pair \
  --portrait-render-receipt "$PAIR/cover-render.json" \
  --square-render-receipt "$PAIR/m4b-cover-render.json" \
  --out "$DIST/cover-selection.json" \
  --book-slug "$SLUG" \
  --edition-id "$EDITION_ID" \
  --selection-source user \
  --selected-at "$SELECTED_AT" \
  --privacy-classification "$CLASSIFICATION" \
  --permission-to-publish
cp "$DIST/cover-selection.json" "$PAIR/cover-selection.json"

/usr/local/bin/python3 skill/scripts/build_book.py \
  --chapters-dir "$RUN_ROOT/chapters" \
  --out-dir "$DIST" \
  --title "$TITLE" \
  --author "Dan Fakkeldy" \
  --contributor "$CONTRIBUTOR" \
  --subtitle "$SUBTITLE" \
  --slug "$SLUG" \
  --cover "$PAIR/cover.png" \
  --m4b-cover "$PAIR/m4b-cover.png" \
  --cover-selection "$DIST/cover-selection.json" \
  --learning-receipt "$RUN_ROOT/research/learning-design-receipt.json" \
  --prose-receipt "$RUN_ROOT/research/prose-style-receipt.json"

/usr/local/bin/python3 skill/scripts/replace_m4b_cover.py \
  --m4b "$DIST/$SLUG.m4b" \
  --cover "$PAIR/m4b-cover.png" \
  --out "$DIST/$SLUG.covered.m4b" \
  --cover-selection "$DIST/cover-selection.json" \
  --portrait-cover "$PAIR/cover.png"
mv "$DIST/$SLUG.covered.m4b" "$DIST/$SLUG.m4b"

/usr/local/bin/python3 skill/scripts/cover_receipts.py verify \
  --selection "$DIST/cover-selection.json" \
  --cover "$PAIR/cover.png" \
  --m4b-cover "$PAIR/m4b-cover.png" \
  --epub "$DIST/$SLUG.epub" \
  --m4b "$DIST/$SLUG.m4b" \
  --receipt "$DIST/cover-selection.json"

/usr/local/bin/python3 skill/scripts/sync_selected_cover.py \
  --selection "$DIST/cover-selection.json" \
  --cover "$PAIR/cover.png" \
  --epub "$DIST/$SLUG.epub" \
  --m4b "$DIST/$SLUG.m4b" \
  --paired-artifact-dir "$PAIR" \
  --destination "$DELIVERY_DIR" \
  --intent reuse

/usr/local/bin/python3 skill/scripts/sync_selected_cover.py \
  --selection "$DIST/cover-selection.json" \
  --cover "$PAIR/cover.png" \
  --epub "$DIST/$SLUG.epub" \
  --m4b "$DIST/$SLUG.m4b" \
  --paired-artifact-dir "$PAIR" \
  --destination "$DELIVERY_DIR" \
  --intent reuse \
  --apply
```


A cover is not a title placed on a coloured rectangle. It is a compact editorial
argument for why a person should choose this book. The default is **three fully
rendered, genuinely different, award-worthy cover candidates for every book**.
Do this without waiting for a special request. The listener chooses the final one
(or asks to combine aspects); never auto-pick a cover merely because it rendered
first.

## Research Lens: What Premium Covers Repeatedly Do

Use galleries such as [The Book Cover Archive](https://bookcoverarchive.com/) as
**visual research**, not a source of assets to copy. A visual review of its
editorial, literary, history, science, and design covers points to transferable
patterns:

- **One arresting visual idea.** A strange but legible object, a single altered
  specimen, a cropped detail, or a bold symbolic action does more than a literal
  inventory of the subject.
- **Type is part of the composition.** The title has a deliberate field, scale,
  contrast, and relationship to the art. It does not look pasted over a stock
  image. Build art around the intended relationship between image and type.
- **A confident system, not decoration.** A grid, repeated mark, archival label,
  rough paper texture, colour field, or precise diagram creates a visual world.
  It should feel intentional at thumbnail size, not like a generic presentation
  background.
- **Controlled contrast and negative space.** Premium covers often use fewer
  elements, larger scale, and breathing room. A bright cover can be as serious as
  a dark one when the silhouette and hierarchy are strong. Negative space must
  still feel designed. Generate art for the intended candidate composition;
  negative space may be top, bottom, side, central, interrupted, or supplied by
  an integrated band when the brief makes that relationship deliberate.
- **Tactility and imperfection.** Paper grain, ink bleed, collage edges, an
  imperfect line, a physical object, or restrained photo realism can add human
  presence. Use one texture language, not a pile of effects.
- **Genre signal without genre cliché.** The visual should tell the right
  audience what kind of journey this is, while avoiding the predictable brain,
  lightbulb, handshake, laptop-on-desk, random galaxy, or title-on-gradient
  shortcut.

Never reproduce, trace, imitate too closely, or lift typography/art from a
specific existing cover. Borrow the **design principle**, not the cover.

## Non-Negotiable Default: Three Distinct Directions

Prepare exactly three complete art-and-type candidates, all rendered at the final
1600×2560 size. The three candidates must differ in metaphor, composition,
palette, material language, and title strategy. Font, line breaks, scale,
placement, and effects are part of the candidate—not a shared footer applied
afterward. Give each a one-line art-direction name and a short rationale before
rendering.

Choose the three most appropriate directions from this menu. Do not use a
weak/placeholder direction just to fill the count.

| Direction | Put the style into words | Best fit |
|---|---|---|
| **Editorial hero object** | One oversized, surprising, precisely chosen object or scene; cinematic crop; crisp silhouette; restrained palette; the object carries the thesis before the title is read. | Science, technology, history, craft, biography, practical learning |
| **Typographic graphic system** | Bold geometric field, repeated mark, diagrammatic rhythm, or designed pattern with generous negative space; title is treated as a major visual mass, not a caption. | Business, ideas, philosophy, systems, productivity, design |
| **Tactile collage / illustration** | Layered paper, ink, printmaking, cut-paper, field-note, or hand-drawn language; one coherent material world; lively but not childish. | Nature, culture, creativity, memoir, learning journeys |
| **Documentary still life** | A real or generated physical scene, tool, specimen, artifact, or close crop lit like an editorial photograph; evocative rather than stock; subtle grain and depth. | History, practical skills, food, place, science, craft |
| **Institutional artifact** | An archival card, blueprint, label, map fragment, lab plate, schematic, or dossier transformed into a beautiful object; precise hierarchy, disciplined spacing, singular accent. | Technical explainers, research, process, architecture, operations |
| **Graphic spectacle** | High-impact colour field or dark void with one impossible visual event, distorted scale, or visual paradox; confident, sparse, emotionally immediate. | Futurism, psychology, high-concept ideas, ambitious popular nonfiction |

### Genre Calibration

- **Technology / product / AI:** show a human-scale consequence or engineered
  object, not generic code rain, floating UI cards, glowing brains, or a laptop
  mockup. Precision, a physical metaphor, and one vivid accent work well.
- **Science / history / research:** use a specimen, era-appropriate artifact,
  data trace, or visual transformation. It must feel researched, not like a
  random museum photo pasted under type.
- **Business / productivity / self-development:** choose a strong system,
  constraint, tool, or visual paradox. Avoid arrows, ladders, handshakes,
  chess pieces, and motivational stock photography.
- **Nature / field guide / hobby / craft:** favor a close physical encounter,
  field-note texture, specimen arrangement, or beautiful process detail. Avoid
  generic landscape wallpaper.
- **Culture / creativity / memoir:** favor collage, print texture, an object with
  emotional history, or a tailored illustration that leaves the title room to
  breathe.

## Candidate Brief Before Making Art

Write one complete art-and-type brief per candidate before image generation:

1. Audience promise.
2. Central metaphor.
3. Composition, crop, and intended title field.
4. Material language and two-to-four-colour palette.
5. Anti-brief.
6. Title archetype and font roles.
7. Planned line breaks and hierarchy.
8. Title anchor, alignment, and approximate occupied area.
9. Intended relationship between title and art.
10. Subtitle, author, and AUDIOBOOK placement.

The three candidates must differ in metaphor, composition, palette, material
language, and title strategy. Font, line breaks, scale, placement, and effects
are part of the candidate—not a shared footer applied afterward.

A candidate is not ready to render if its central idea could fit any book, if
its anti-brief is empty, or if a text model produced vector art without first
using an available image-generation tool.

## Making the Art

Use the strongest available original-art route for the book. Do not accept the
first technically valid image: the bar is a beautiful, specific, image-led cover
that could sit in a serious bookstore or audiobook storefront.

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
3. **User-supplied, self-created, official, public-domain, or permissively
   licensed photography/art** only when the rights and provenance are clear.

The validated specification may reference self-contained SVG, PNG, JPEG, WebP,
or GIF art. Keep generated artwork text-free: title, subtitle, author, and the
audiobook label belong to the specification, where their font, line breaks,
scale, placement, and effects remain reproducible. Generated text is unreliable,
fights the metadata, and rarely reads well at thumbnail size.

### Copy-ready image-generation prompt

For a generated candidate, fill in the bracketed fields and send this as one
complete prompt to the image model. The art model should make the visual world;
the compositor should make the typography. Keep the prompt concrete rather than
asking for “a nice cover” or “something professional.”

```text
Create original portrait editorial artwork for a premium nonfiction audiobook
cover about [SUBJECT]. The book's audience is [AUDIENCE], and its promise is
[AUDIENCE PROMISE]. The single visual thesis is [ONE SENTENCE VISUAL THESIS].

Show one unforgettable central metaphor: [SPECIFIC OBJECT, SCENE, OR VISUAL
PARADOX]. Make that subject large, beautifully art-directed, and immediately
legible at a small thumbnail. Use [COMPOSITION: CLOSE CROP / WIDE STILL LIFE /
SINGLE FIGURE / DIAGONAL ACTION], with a strong silhouette and one clear focal
point. Compose around [INTENDED TITLE FIELD AND RELATIONSHIP TO ART]; that field
may be top, bottom, side, central, interrupted, or an integrated band. The image
should feel like finished editorial cover artwork, not an illustration for a
slide deck.

Visual language: [CHOOSE ONE: cinematic editorial photograph / tactile cut-paper
collage / expressive ink and gouache / refined screen print / painterly realism /
surreal editorial illustration]. Material and surface: [PAPER GRAIN, PRINT
TEXTURE, FABRIC, METAL, GLASS, WEATHER, OR OTHER SINGLE MATERIAL LANGUAGE]. Use a
confident, eye-catching palette of [2–4 COLOURS], including a vivid signature
accent [HEX COLOUR] that is visibly present in the main image. Use sophisticated
colour relationships, controlled contrast, dimensional light, and deliberate
texture; avoid a washed-out pastel gradient. Make the result emotionally [MOOD]
and genre-appropriate without using genre clichés.

High-end art direction, specific physical detail, elegant composition, premium
print sensibility, visual hierarchy, subtle human imperfection, striking colour,
strong thumbnail read, original concept. No title, no subtitle, no author name,
no lettering, no typography, no logo, no watermark, no border, no mockup, no book
mockup, no audiobook icon, no interface, no dashboard, no floating UI cards, no
generic infographic, no stock-photo look, no random symbols, no collage of tiny
objects, no split-screen, no decorative icon cloud, no close imitation of any
named artist, designer, publisher, or existing book cover.
```

For each candidate, change the **visual thesis**, central metaphor, composition,
material language, and palette—not just the colour values. If the output is a
generic gradient, diagram, icon illustration, cluttered scene, or weak literal
stock image, discard it and regenerate with a sharper physical metaphor and
stronger art direction. Ask for a clean image with no lettering even when the
model claims to handle typography; encode all text and layout afterward in each
candidate specification.

## Render, Compare, and Select

Assign `SLUG` from the approved run metadata. Keep generated artwork text-free.
Save the shared art and both schema-v2 specs in each candidate directory. Use
the complete `render_cover_pair(...)` call above for candidates 1 through 3.
Review every full-size portrait and square render, generated 160-pixel
thumbnail, art-and-type brief, font/palette note, and warning. In governed-final,
ask the user to choose or request a mix. In unattended-first-listen, apply the
rubric in `unattended-production.md` and record the editorial choice and reason.
A mix becomes a new specification and render.

Use `cover_receipts.py select-pair` as described by the universal rule. A paired
user choice uses `selection_source=user`; a requested mix uses `requested-mix`;
and a private, non-publishing unattended choice uses
`editorial-autoselection`. The receipt validator rejects editorial
auto-selection unless classification is private and publication permission is
false. The renderer itself never selects automatically.
The old single-render receipt and title/art/accent/tone/layout paths are
verification-only compatibility for existing packages.

## Award-Worthy Acceptance Bar

Reject and replace any candidate that:

- could be mistaken for a stock-template cover, slide icon, logo, AI wallpaper,
  or generic title-on-gradient design;
- has more than one competing visual idea, or no idea beyond the literal subject;
- hides the title behind visual noise or leaves it with no intentional field;
- looks good only at full size but collapses at a 160px thumbnail;
- repeats the same composition, palette, or central metaphor as another
  candidate;
- uses an unearned premium cliché (gold foil effect, arbitrary smoke, faux
  luxury marble, generic starfield) instead of a visual argument;
- uses rights-unclear web imagery, watermarks, or a misleading “documentary”
  scene for a topic that requires evidence;
- would look out of place in a serious bookstore or audiobook storefront.

## Technical Contract

- Each validated JSON specification owns its candidate metadata, 1600×2560
  canvas, art placement, ordered fields/shapes/type, and bundled font IDs.
- Raster art may be PNG, JPEG, WebP, or GIF. Self-contained SVG remains an
  explicit-request or approved-unavailable-image-tool fallback. Use
  high-resolution portrait art and no external image URLs.
- Each spec-driven render writes the full-size RGB cover, a 160×256 thumbnail,
  and a `.render.json` receipt. Treat every warning as part of human review.
- Keep the candidate's signature accent unmistakable enough for Echo/library
  colour derivation to find it, but do not flatten the whole cover into one
  colour.
- The legacy title, art, accent, tone, and layout flags exist only for compatible
  existing calls. Do not use them for a new-book workflow.
- A complete SVG example remains available at
  `references/cover-art-example.svg`; use it only as a structural reference for
  an approved vector fallback, not a visual template.
