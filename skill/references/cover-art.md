# Award-Worthy Audiobook Covers

Contents: Paired-cover rendering · Research Lens · Three Distinct Directions ·
Genre Calibration · Candidate Brief Before Making Art · Making the Art ·
Copy-ready image-generation prompt · Render, Compare, and Select · Award-Worthy
Acceptance Bar · Technical Contract.

## Universal paired-cover rule

Every new book develops exactly three coordinated portrait/square candidates.
Each direction shares one source-art identity but has two deliberately composed
specifications: `cover.png` at 1600×2560 for the EPUB portrait and
`m4b-cover.png` at 2400×2400 for the M4B square. Review both full-size images and
both thumbnails together. Never mix variants. Select the strongest complete pair
on subject specificity, thumbnail legibility, title hierarchy, portrait/square
coherence, absence of defects, and distinctiveness, then report the choice.

The governed Echo narration wrapper embeds the selected square cover itself and
holds its FD-backed resource leases through narration. Treat the emitted M4B as
immutable.

### Render a paired candidate

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

For the rare public promotion flow, use
`references/publishing-a-public-edition.md`.


A cover is not a title placed on a coloured rectangle. It is a compact editorial
argument for why a person should choose this book. The default is **three fully
rendered, genuinely different, award-worthy cover candidates for every book**.
Do this without waiting for a special request. Select the best complete pair on
the rubric after reviewing every render; never choose merely because it rendered
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
weak/placeholder direction just to fill the count. At least one of the three
candidates must be a Designed flat graphic or type-led direction (Typographic
graphic system counts), so a designed, non-generated look is always offered.

| Direction | Put the style into words | Best fit |
|---|---|---|
| **Editorial hero object** | One oversized, surprising, precisely chosen object or scene; cinematic crop; crisp silhouette; restrained palette; the object carries the thesis before the title is read. | Science, technology, history, craft, biography, practical learning |
| **Typographic graphic system** | Bold geometric field, repeated mark, diagrammatic rhythm, or designed pattern with generous negative space; title is treated as a major visual mass, not a caption. | Business, ideas, philosophy, systems, productivity, design |
| **Tactile collage / illustration** | Layered paper, ink, printmaking, cut-paper, field-note, or hand-drawn language; one coherent material world; lively but not childish. | Nature, culture, creativity, memoir, learning journeys |
| **Documentary still life** | A real or generated physical scene, tool, specimen, artifact, or close crop lit like an editorial film photograph — visible grain, imperfect natural light, real-world staging; evocative rather than stock; never a glossy smooth 3D render. | History, practical skills, food, place, science, craft |
| **Institutional artifact** | An archival card, blueprint, label, map fragment, lab plate, schematic, or dossier transformed into a beautiful object; precise hierarchy, disciplined spacing, singular accent. | Technical explainers, research, process, architecture, operations |
| **Graphic spectacle** | High-impact colour field or dark void with one impossible visual event, distorted scale, or visual paradox; confident, sparse, emotionally immediate. | Futurism, psychology, high-concept ideas, ambitious popular nonfiction |
| **Designed flat graphic** | Bold flat-ink illustration: one confident geometric or character mark, two-to-four flat colours, strong silhouette, mid-century poster sensibility; lively but not childish; built as compositor-native vector or flat raster art. | Technology, ideas, playful explainers, learning journeys, series identity |

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

The differentiation rule from Non-Negotiable Default above applies to every
brief: differ in metaphor, composition, palette, material language, and title
strategy, with typography designed per candidate.

A candidate is not ready to render if its central idea could fit any book, if
its anti-brief is empty, or if vector art was substituted for a direction whose
render route is the image-generation tool.

## Making the Art

Use the strongest available original-art route for the book. Do not accept the
first technically valid image: the bar is a beautiful, specific, image-led cover
that could sit in a serious bookstore or audiobook storefront.

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

Visual language: [CHOOSE ONE: refined screen print / risograph print / woodcut
or linocut / gouache poster illustration / halftone editorial illustration /
tactile cut-paper collage / grainy film photograph with natural, imperfect
light]. Material and surface: [PAPER GRAIN, PRINT
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
named artist, designer, publisher, or existing book cover. No AI-render tells:
no centered glowing object, no airbrushed radial glow, no perfectly smooth
gradients, no paper-cut layered landscape with a winding road or river, no
hyper-smooth 3D product render, no melted or smeared detail, no uniform digital
sheen.
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
thumbnail, art-and-type brief, font/palette note, and warning. Score the complete
pairs on subject specificity, thumbnail legibility, title hierarchy,
portrait/square coherence, absence of defects, and distinctiveness. Select and
report the strongest. A later request to mix directions becomes a new
specification and render.

### Publisher brand mark

Schema-v2 paired covers may add one `brand_mark` layer. This is a separately
hashed compositor input, not part of the generated source art and not a
post-render watermark. Copy the selected transparent mark into the candidate
directory, choose the version intended for the local light or dark surface, and
place it inside the canvas safe margin. The layer is composited in declared
order and its exact source bytes are recorded in the render receipt.

```json
{
  "kind": "brand_mark",
  "path": "brand-mark.png",
  "box": [1324, 96, 180, 180],
  "opacity": 0.9,
  "blend_mode": "normal",
  "purpose": "identify KinNoKi Labs as the publisher"
}
```

Use the transparent tree mark by default. A portrait mark around 180 pixels and
a square mark around 240 pixels are useful starting sizes, but placement remains
part of each candidate's art direction. Keep it clear of the title, author,
`AUDIOBOOK` label, focal subject, and trim edge; reduce opacity only when the
real thumbnail remains unmistakably legible. Do not bake the mark into generated
art, use the full black-background wordmark as a generic badge, add more than one
brand mark, or retrofit it after rendering. Portrait and square specifications
may use different light/dark variants when their local surfaces differ.

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
- would be clocked as AI-generated at a glance — waxy smoothness, airbrushed
  glow, melted or smeared detail, or a trope composition such as a glowing
  centered orb or a paper-cut valley with a winding path;
- uses rights-unclear web imagery, watermarks, or a misleading “documentary”
  scene for a topic that requires evidence;
- would look out of place in a serious bookstore or audiobook storefront.

## Technical Contract

- Each validated JSON specification owns its candidate metadata, 1600×2560
  canvas, art placement, ordered fields/shapes/type, and bundled font IDs.
  Validate specs against `skill/schemas/cover-spec-v1.schema.json` (it accepts
  schema versions 1 and 2; new specs use version 2).
- Raster art may be PNG, JPEG, WebP, or GIF. Self-contained SVG is a peer
  route for Designed flat graphic and type-led candidates. Use
  high-resolution portrait art and no external image URLs.
- Each spec-driven render writes the full-size RGB cover, a 160×256 thumbnail,
  and a `.render.json` receipt. Treat every warning as part of human review.
- One optional schema-v2 `brand_mark` layer may reference a local SVG, PNG,
  JPEG, WebP, or GIF. It must remain inside the safe margin; the renderer binds
  its filename and SHA-256 in a version-2 render receipt, while version-1
  receipts remain valid compatibility inputs.
- Keep the candidate's signature accent unmistakable enough for Echo/library
  colour derivation to find it, but do not flatten the whole cover into one
  colour.
- The legacy title, art, accent, tone, and layout flags exist only for compatible
  existing calls. Do not use them for a new-book workflow.
- A complete SVG example remains available at
  `references/cover-art-example.svg`; use it only as a structural reference for
  vector-route candidates, not a visual template.
- `skill/scripts/make_cover_contact_sheet.py` builds a side-by-side contact
  sheet of all candidate renders and thumbnails for review.

Public promotion and legacy compatibility commands live only in
`references/publishing-a-public-edition.md`.
