# Award-Worthy Audiobook Covers

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
  image. Build art with clear room for the compositor's title block.
- **A confident system, not decoration.** A grid, repeated mark, archival label,
  rough paper texture, colour field, or precise diagram creates a visual world.
  It should feel intentional at thumbnail size, not like a generic presentation
  background.
- **Controlled contrast and negative space.** Premium covers often use fewer
  elements, larger scale, and breathing room. A bright cover can be as serious as
  a dark one when the silhouette and hierarchy are strong.
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

Prepare exactly three candidates, all rendered at the final 1600×2560 size. They
must differ in **central metaphor, composition, palette, and visual language** —
not merely in background colour or crop. Give each a one-line art-direction name
and a short rationale before rendering.

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

Write a five-line brief for each direction:

1. **Audience promise:** the emotional or intellectual pull at a glance.
2. **Central metaphor:** one object, scene, system, or visual paradox.
3. **Composition:** scale, crop, negative space, and where the title will live.
4. **Material and palette:** 2–4 core colours, texture language, and signature
   accent (`#RRGGBB`).
5. **Anti-brief:** the genre clichés and visual treatments this candidate refuses.

A candidate is not ready to render if its central idea could fit any book, or if
its anti-brief is empty.

## Making the Art

Use the strongest available original-art route for the book:

1. **Generated image art** when an image-generation tool is available. Prompt for
   the composition and material language above, at portrait ratio, **with no
   text, lettering, logos, watermarks, mockup frame, or imitation of a named
   cover/designer**. Treat generated art as visual illustration, not documentary
   evidence.
2. **Bespoke SVG illustration** when a graphic, diagrammatic, or typographic
   system will be stronger or when image generation is unavailable. SVG must look
   like deliberate editorial art, not a slide icon.
3. **User-supplied, self-created, official, public-domain, or permissively
   licensed photography/art** only when the rights and provenance are clear.

`make_cover.py --art` accepts self-contained SVG plus PNG, JPEG, WebP, and GIF
art. For raster artwork it embeds the file into the composed SVG, so the final
PNG render remains portable. Keep all visual content comfortably inside the
central safe area: `bleed` crops edges, whereas `hero` frames the complete image.

The title, subtitle, author, and audiobook label are added by `make_cover.py`.
Do **not** bake text into the art itself; generated text is unreliable, fights the
metadata, and rarely reads well at thumbnail size.

## Render and Compare

For each candidate:

1. Save art as `cover-concept-1.<svg|png|jpg|webp>`, and similarly for 2/3.
2. Pass the art's visible accent to `--accent`; the same colour must appear in the
   artwork, not only as a thin border.
3. Deliberately vary `--layout` and `--tone` where that serves the concept. At
   least one candidate should be high-key/bright unless the subject genuinely
   demands three dark directions.
4. Render with `make_cover.py` at 1600×2560.
5. Inspect at full size **and at thumbnail scale**. Send all three candidates to
   the user; invite a pick or a mix.

Example:

```bash
python3 scripts/make_cover.py \
  --title "<Book Title>" \
  --subtitle "<one-line subtitle>" \
  --author "Dan Fakkeldy" \
  --label "AUDIOBOOK" \
  --art <build>/dist/cover-concept-1.webp \
  --accent "#2ee8b6" \
  --tone bright \
  --layout bleed \
  --out <build>/dist/cover-1.png
```

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

- SVG should be a complete `<svg viewBox="0 0 1200 1400">…</svg>` with
  self-contained shapes, gradients, and patterns. Namespace IDs to avoid
  collisions with the compositor.
- Raster art may be PNG, JPEG, WebP, or GIF. Use high-resolution portrait art;
  no external image URLs are embedded.
- Make the signature accent unmistakable enough for Echo/library colour derivation
  to find it, but do not flatten the whole cover into one colour.
- Preserve safe margins. `bleed` fills and crops; `hero` keeps the full artwork in
  a panel.
- A complete SVG example remains available at
  `references/cover-art-example.svg`; use it as a structural reference, not a
  visual template.
