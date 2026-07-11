# Public Audiobook Cover Refresh — July 2026

**Date:** 2026-07-11

**Scope:** Eleven tracked public Explainer Audiobooks titles

**Collection review:** [Labelled contact sheet](contact-sheet.png)

## Collection contract

Each title received three genuinely different original raster-art directions through the built-in image-generation tool. The approved autonomous-selection process chose one direction per title, using full-size and 160-pixel inspection plus a collection-wide contact-sheet review. Candidate art contains no title, subtitle, author, lettering, logo, watermark, UI, dashboard, mockup frame, or intentional imitation of an existing cover or named designer. The repository compositor, `skill/scripts/make_cover.py`, applied typography deterministically after generation and rendered every final RGB PNG at 1600 × 2560.

Bright/high-key artwork is the collection default. Nine covers use the bright compositor treatment; *The New Deal* and *Why It Feels Right* use bright or mid-key art with justified dark lower typography fields. The corrected binding layout rule is that visual energy, texture, structure, shadow, or movement continues through the top and middle, while only the lower 25–35% is reserved as the calmer title field. Earlier upper-title-field language in production notes is superseded.

All generated visual art is original illustrative artwork, not documentary evidence. No third-party art was incorporated. Discarded candidate binaries and local generation source paths remain ignored build artifacts; only selected covers and the public provenance below are committed. The built-in tool returned the tool path and generated output, but did **not** return reliable model name, model version, seed, or other reproducibility metadata, so none is claimed here.

## Title records

## Chicken Predators (`chicken-predators`)

- **Title / slug:** Chicken Predators / `chicken-predators`
- **Directions:**
  - **A — Feather at Dawn:** Single feather caught in a humane live-trap threshold at documentary dawn.
  - **B — Tracks Around the Egg:** Cut-paper predator tracks circling one intact egg.
  - **C — The Latch:** Weathered coop latch lit like a forensic artifact.
- **Selected:** A — Feather at Dawn
- **Accent / tone / layout:** `#F28C28` / `bright` / `bleed`
- **Generated-art filename:** `candidate-a-art.png`
- **Final / legacy cover:** `books/chicken-predators/cover.png` / `books/chicken-predators/cover-legacy.png`
- **EPUB / declared cover member:** `books/chicken-predators/chicken-predators.epub` / `OEBPS/cover.png`
- **Inspection:** full size — pass; 160-pixel thumbnail — pass. Dawn trap/feather metaphor is specific, warm but not duplicative, and active across the top/middle; lower peach field supports a clear two-line title.
- **Final cover SHA-256:** `cda44d7334f6f8f9de81ea0b7513330d13ec6d6ff415afbeccc80cb8fa1d1d23`

**Exact prompt for the selected art:**

```text
Create original portrait editorial artwork for a premium nonfiction audiobook cover about Chicken Predators. The book's audience is backyard flock keepers who need calm, humane, evidence-led predator protection, and its promise is a clear, humane and memorable way into Chicken Predators. The single visual thesis is single feather caught in a humane live-trap threshold at documentary dawn.

Show one unforgettable central metaphor: single feather caught in a humane live-trap threshold at documentary dawn. Make that subject large, beautifully art-directed, and immediately legible at a small thumbnail. Use wide documentary still life, trap threshold low in frame, quiet upper third, with a strong silhouette, one clear focal point, and generous intentional negative space for title typography. The image should feel like a finished editorial book cover image, not an illustration for a slide deck.

Visual language: cinematic editorial photograph. Material and surface: weathered wood, cool dawn blue, straw gold, humane-safety orange. Use a confident, eye-catching palette including a vivid signature accent #F28C28 that is visibly present in the main image. Use sophisticated colour relationships, controlled contrast, dimensional light, and deliberate texture; avoid a washed-out pastel gradient. Make the result emotionally specific, grounded, and genre-appropriate without using genre clichés.

High-end art direction, specific physical detail, elegant composition, premium print sensibility, visual hierarchy, subtle human imperfection, striking colour, strong thumbnail read, original concept. No title, no subtitle, no author name, no lettering, no typography, no logo, no watermark, no border, no mockup, no book mockup, no audiobook icon, no interface, no dashboard, no floating UI cards, no generic infographic, no stock-photo look, no random symbols, no collage of tiny objects, no split-screen, no decorative icon cloud, no close imitation of any named artist, designer, publisher, or existing book cover.
```

## Echo, From the Inside (`echo-from-the-inside`)

- **Title / slug:** Echo, From the Inside / `echo-from-the-inside`
- **Directions:**
  - **A — Calm Inner Machine:** Exploded physical music box revealing a calm, intelligible inner machine.
  - **B — Listening Chamber:** Translucent layered book pages becoming an app-shaped listening chamber.
  - **C — Sketch to Glass:** Hand-built bridge from rough sketches to polished glass.
- **Selected:** C — Sketch to Glass
- **Accent / tone / layout:** `#F5A623` / `bright` / `bleed`
- **Generated-art filename:** `candidate-c-art.png`
- **Final / legacy cover:** `books/echo-from-the-inside/cover.png` / `books/echo-from-the-inside/cover-legacy.png`
- **EPUB / declared cover member:** `books/echo-from-the-inside/echo-from-the-inside.epub` / `OEBPS/cover.png`
- **Inspection:** full size — pass; 160-pixel thumbnail — pass. Sketch-to-glass bridge remains unique; sky gradient, diagonal panel, hand, paper, and bridge carry the upper/middle while the lower field supports the title.
- **Final cover SHA-256:** `39efbe10e0fef2583de444c93e282e7f37fd5bb074e5a2fe24e13c28f8360828`

**Exact prompt for the selected art:**

```text
Create original portrait editorial artwork for a premium nonfiction audiobook cover about Echo, From the Inside. Audience: AI-assisted builders who want to understand the real app they made. Single visual thesis: a hand-built bridge transforming from rough paper sketches into polished glass. The bridge crosses the lower half from tactile paper to luminous glass, leaving a broad sky-like upper title field. Tactile collage merging into refined glass realism; warm paper white, graphite, pale aqua, vivid amber #F5A623. Binding collection direction: bright, high-key daylight, optimistic and airy, controlled contrast. One central metaphor and strong 160px silhouette. No title, subtitle, author, letters, typography, logo, watermark, border, mockup, phone UI, interface, dashboard, floating cards, robot, generic glowing technology, code texture, random symbols, icon cloud, or stock imagery.
```

## Findable (`findable`)

- **Title / slug:** Findable / `findable`
- **Directions:**
  - **A — The Luminous Spine:** One luminous book spine found inside a city-scale shelf.
  - **B — Search Compass:** Brass search compass aligning with a tiny storefront doorway.
  - **C — Quiet Signal:** A signal flare reflected in a field of quiet app-like tiles without UI or logos.
- **Selected:** B — Search Compass
- **Accent / tone / layout:** `#20A878` / `bright` / `hero`
- **Generated-art filename:** `candidate-b-art.png`
- **Final / legacy cover:** `books/findable/cover.png` / `books/findable/cover-legacy.png`
- **EPUB / declared cover member:** `books/findable/findable.epub` / `OEBPS/cover.png`
- **Inspection:** full size — pass; 160-pixel thumbnail — pass. Compass and storefront read immediately; green hero inset is now the collection's sole framed template rather than a repeated system.
- **Final cover SHA-256:** `44e65dcac396a753017e8cd1b0e54f5c3e5720d8421d98911cb7af4bca873d2d`

**Exact prompt for the selected art:**

```text
Create original portrait editorial artwork for a premium nonfiction audiobook cover about Findable. The book's audience is indie developers trying to help the right small audience discover a useful app, and its promise is a clear, humane and memorable way into Findable. The single visual thesis is brass search compass aligning with a tiny storefront doorway.

Show one unforgettable central metaphor: brass search compass aligning with a tiny storefront doorway. Make that subject large, beautifully art-directed, and immediately legible at a small thumbnail. Use oversized compass foreground, doorway on its bearing, clear sky-like top field, with a strong silhouette, one clear focal point, and generous intentional negative space for title typography. The image should feel like a finished editorial book cover image, not an illustration for a slide deck.

Visual language: tactile cut-paper collage. Material and surface: aged brass, slate, cream plaster, discovery green. Use a confident, eye-catching palette including a vivid signature accent #20A878 that is visibly present in the main image. Use sophisticated colour relationships, controlled contrast, dimensional light, and deliberate texture; avoid a washed-out pastel gradient. Make the result emotionally specific, grounded, and genre-appropriate without using genre clichés.

High-end art direction, specific physical detail, elegant composition, premium print sensibility, visual hierarchy, subtle human imperfection, striking colour, strong thumbnail read, original concept. No title, no subtitle, no author name, no lettering, no typography, no logo, no watermark, no border, no mockup, no book mockup, no audiobook icon, no interface, no dashboard, no floating UI cards, no generic infographic, no stock-photo look, no random symbols, no collage of tiny objects, no split-screen, no decorative icon cloud, no close imitation of any named artist, designer, publisher, or existing book cover.
```

## Git Happens (`git-happens`)

- **Title / slug:** Git Happens / `git-happens`
- **Directions:**
  - **A — The Deliberate Knot:** Branching red thread repaired with one deliberate knot.
  - **B — Clean Fault Line:** Geological strata of paper commits with one clean fault line.
  - **C — Branching Specimen:** A battered field case containing a pristine branching specimen.
- **Selected:** A — The Deliberate Knot
- **Accent / tone / layout:** `#D62828` / `bright` / `bleed`
- **Generated-art filename:** `candidate-a-art.png`
- **Final / legacy cover:** `books/git-happens/cover.png` / `books/git-happens/cover-legacy.png`
- **EPUB / declared cover member:** `books/git-happens/git-happens.epub` / `OEBPS/cover.png`
- **Inspection:** full size — pass; 160-pixel thumbnail — pass. Red-thread knot has the clearest single-symbol read in the set; textile texture and branching strands animate the upper/middle before the calm pink title field.
- **Final cover SHA-256:** `fc12ad8dee431de5af930b2eaba8407798a45d41c376bd000cc87a72f543b546`

**Exact prompt for the selected art:**

```text
Create original portrait editorial artwork for a premium nonfiction audiobook cover about Git Happens. The book's audience is self-taught builders who want Git to feel like a controllable safety system, and its promise is a clear, humane and memorable way into Git Happens. The single visual thesis is branching red thread repaired with one deliberate knot.

Show one unforgettable central metaphor: branching red thread repaired with one deliberate knot. Make that subject large, beautifully art-directed, and immediately legible at a small thumbnail. Use macro textile close-up crossing lower half, generous linen field above, with a strong silhouette, one clear focal point, and generous intentional negative space for title typography. The image should feel like a finished editorial book cover image, not an illustration for a slide deck.

Visual language: cinematic editorial photograph. Material and surface: natural linen, black thread, repair red, warm cream. Use a confident, eye-catching palette including a vivid signature accent #D62828 that is visibly present in the main image. Use sophisticated colour relationships, controlled contrast, dimensional light, and deliberate texture; avoid a washed-out pastel gradient. Make the result emotionally specific, grounded, and genre-appropriate without using genre clichés.

High-end art direction, specific physical detail, elegant composition, premium print sensibility, visual hierarchy, subtle human imperfection, striking colour, strong thumbnail read, original concept. No title, no subtitle, no author name, no lettering, no typography, no logo, no watermark, no border, no mockup, no book mockup, no audiobook icon, no interface, no dashboard, no floating UI cards, no generic infographic, no stock-photo look, no random symbols, no collage of tiny objects, no split-screen, no decorative icon cloud, no close imitation of any named artist, designer, publisher, or existing book cover.
```

## Rodents in the Walls (`rodents-in-the-walls`)

- **Title / slug:** Rodents in the Walls / `rodents-in-the-walls`
- **Directions:**
  - **A — Telltale Trail:** House wall cutaway with one telltale trail of dust and whisker shadow.
  - **B — Gnawed Threshold:** An oversized gnawed wooden threshold as a forensic still life.
  - **C — Field Guide Evidence:** Bright field-guide collage of tracks, nesting fibre, and one sealed gap.
- **Selected:** A — Telltale Trail
- **Accent / tone / layout:** `#20B8B5` / `bright` / `bleed`
- **Generated-art filename:** `candidate-a-art.png`
- **Final / legacy cover:** `books/rodents-in-the-walls/cover.png` / `books/rodents-in-the-walls/cover-legacy.png`
- **EPUB / declared cover member:** `books/rodents-in-the-walls/rodents-in-the-walls.epub` / `OEBPS/cover.png`
- **Inspection:** full size — pass; 160-pixel thumbnail — pass. Full-bleed wall cutaway, dust/fibre trail, cedar, and turquoise sealed gap are readable at 160px and no longer repeat Findable.
- **Final cover SHA-256:** `7637fcd86a87700eab2f30642d1f41fce82559571f1de4a5947012232175756d`

**Exact prompt for the selected art:**

```text
Use case: stylized-concept
Asset type: portrait raster artwork for a premium nonfiction audiobook cover
Primary request: TARGETED COLLECTION-LEVEL REGENERATION for Rodents in the Walls. Replace the repeated mint framed hero-inset template with a full-bleed, bright forensic wall-cutaway scene that remains clear at 160px.
Scene/backdrop: a sunlit plaster-and-timber house wall opened in one clean vertical cutaway, with a single unmistakable trail of pale dust, one delicate whisker shadow, nesting fibre, and a precisely sealed gap; no animal body.
Subject: the evidence trail is the hero—dust and fibre sweep diagonally from the upper-left through the middle toward the sealed gap, making hidden movement legible without horror.
Style/medium: tactile documentary still life blended with refined field-guide collage; physical plaster, torn paper edges, wood grain, and one coherent material world.
Composition/framing: strict PORTRAIT 2:3, full-bleed vertical composition, no inset frame or centered small picture. Carry active evidence, wall structure, and diagonal movement through the top and middle. Reserve ONLY the lower 25–35 percent as a calmer continuous warm-plaster field for later title typography, while retaining subtle texture and tonal variation.
Lighting/mood: bright high-key morning daylight, investigative, humane, practical, airy rather than ominous.
Color palette: warm plaster white, sunlit cedar, charcoal dust, vivid turquoise accent #20B8B5 visibly present as one sealing strip at the gap; avoid mint-dominant or green-wash treatment.
Text (verbatim): none.
Constraints: one focal evidence trail; strong silhouette and contrast at 160px; no rodent anatomy; no dead vacant upper half; no hero panel, border, frame, card, or repeated template; lower 25–35 percent remains calm enough for title type.
Avoid: title, subtitle, author, words, letters, numbers, typography, logo, watermark, book mockup, UI, screen, dashboard, code, glowing technology, icons, symbols, stock-photo cliché, gore, horror, dark void, tiny centered object, mint background.
```

## Tests First (`tests-first`)

- **Title / slug:** Tests First / `tests-first`
- **Directions:**
  - **A — Protected Mechanism:** A porcelain mechanism protected by a ring of precise gauges.
  - **B — Safety Block:** A bright row of dominoes stopped by one transparent safety block.
  - **C — Inspected Stitch:** Repaired parachute stitching inspected under a work lamp.
- **Selected:** B — Safety Block
- **Accent / tone / layout:** `#2364FF` / `bright` / `bleed`
- **Generated-art filename:** `candidate-b-art.png`
- **Final / legacy cover:** `books/tests-first/cover.png` / `books/tests-first/cover-legacy.png`
- **EPUB / declared cover member:** `books/tests-first/tests-first.epub` / `OEBPS/cover.png`
- **Inspection:** full size — pass; 160-pixel thumbnail — pass. Cobalt domino collision and transparent safety block remain crisp; diagonal blue shadows and paper texture carry upward while the lower blue field stays quiet.
- **Final cover SHA-256:** `5f16eca3d70db64c9c55424f4be6bc069881aa9853ba950a08d4b11aabf30c99`

**Exact prompt for the selected art:**

```text
Use case: stylized-concept
Asset type: portrait raster artwork for a premium nonfiction audiobook cover
Primary request: TARGETED REGENERATION for Tests First. Create a bright portrait domino safety-block metaphor with compositional energy continuing upward.
Scene/backdrop: warm-white tactile studio surface with atmospheric cobalt shadows and subtle paper-grain texture extending through the composition, not a blank empty top.
Subject: one vivid row of smooth blank cobalt dominoes actively falling and stopped by one tall transparent crystal safety block; the stopped collision is unmistakable.
Style/medium: refined screen-print-meets-editorial still life, physical and tactile, premium print sensibility.
Composition/framing: strict PORTRAIT 2:3 vertical composition. Domino action begins in the lower field and travels diagonally upward so shadows and compositional energy carry into the middle. Reserve ONLY the upper 25–35 percent as a calm but textured title-safe field. Do not create a huge dead blank top.
Lighting/mood: bright high-key daylight, optimistic confidence, crisp controlled shadows, energetic but orderly.
Color palette: warm white, cobalt blue, clear crystal, vivid #2364FF accent.
Text (verbatim): none.
Constraints: one focal point; strong 160px thumbnail silhouette; dominoes completely blank with no dots or markings; atmospheric shadows, paper texture, and visual energy extend upward; title-safe area limited to upper 25–35 percent.
Avoid: square or landscape output, dead blank upper half, empty white void, title, subtitle, author, words, letters, numbers, typography, logo, watermark, border, book mockup, UI, screen, dashboard, code, generic glowing technology, symbols, icons.
```

## The Bug Is a Clue (`the-bug-is-a-clue`)

- **Title / slug:** The Bug Is a Clue / `the-bug-is-a-clue`
- **Directions:**
  - **A — Revealing Shadow:** A single beetle casting the shadow of a magnifying glass.
  - **B — One Red Thread:** A detective evidence board reduced to one red thread and one broken component.
  - **C — Missing Tooth:** A bright machine room where one missing flywheel tooth and the matching loose tooth reveal the exact fault.
- **Selected:** A — Revealing Shadow
- **Accent / tone / layout:** `#F28C28` / `bright` / `bleed`
- **Generated-art filename:** `candidate-a-art.png`
- **Final / legacy cover:** `books/the-bug-is-a-clue/cover.png` / `books/the-bug-is-a-clue/cover-legacy.png`
- **EPUB / declared cover member:** `books/the-bug-is-a-clue/the-bug-is-a-clue.epub` / `OEBPS/cover.png`
- **Inspection:** full size — pass; 160-pixel thumbnail — pass. Beetle plus magnifying shadow is immediate and distinctive; foliage and shadows keep the upper/middle alive and the lower peach field readable.
- **Final cover SHA-256:** `a941979e3e22299fe8c552060803feb8759d43accd3962c95ca0bff09c6da417`

**Exact prompt for the selected art:**

```text
Use case: stylized-concept
Asset type: portrait raster artwork for a premium nonfiction audiobook cover
Primary request: TARGETED REGENERATION for The Bug Is a Clue. Preserve the beetle-and-magnifying-shadow clue metaphor while eliminating the dead blank top.
Scene/backdrop: warm fibrous paper surface with botanical foliage, paper grain, and natural shadow energy continuing upward through the whole field.
Subject: one small real beetle in the lower-middle casting an impossible, crisp, unmistakable magnifying-glass-shaped shadow; the beetle plus shadow reads instantly as a debugging clue.
Style/medium: surreal cinematic editorial photograph, tactile and premium, curious rather than ominous.
Composition/framing: strict PORTRAIT 2:3 vertical composition. The magnifier shadow travels diagonally upward and foliage edge shadows carry visual rhythm through the middle. Reserve ONLY the upper 25–35 percent as title-safe, but keep it alive with subtle paper texture, soft foliage shadow, and tonal variation. No dead empty top.
Lighting/mood: bright high-key sunlight, precise natural texture, investigative curiosity, controlled contrast.
Color palette: warm paper white, charcoal, botanical green, visible orange accent #F28C28.
Text (verbatim): none.
Constraints: magnifier-shadow metaphor must remain clear at 160px; paper texture, shadow, and foliage energy extend into the upper field; one focal idea; title-safe area limited to upper 25–35 percent.
Avoid: square or landscape output, dead blank upper half, empty white void, title, subtitle, author, words, letters, numbers, typography, logo, watermark, border, mockup, UI, dashboard, robot, generic glowing technology, code texture, random symbols, icons, stock-photo cliché.
```

## The New Deal (`the-new-deal`)

- **Title / slug:** The New Deal / `the-new-deal`
- **Directions:**
  - **A — Paper Mailbox:** A rural mailbox rebuilt from layered contract paper and route twine.
  - **B — Road and Grid:** A weathered postal satchel balanced between an old road and a new measured grid.
  - **C — Folded Route:** A bright Cape Breton route map folded into a handshake-shaped landscape without logos.
- **Selected:** B — Road and Grid
- **Accent / tone / layout:** `#F2B705` / `dark` / `bleed`
- **Generated-art filename:** `candidate-b-art.png`
- **Final / legacy cover:** `books/the-new-deal/cover.png` / `books/the-new-deal/cover-legacy.png`
- **EPUB / declared cover member:** `books/the-new-deal/the-new-deal.epub` / `OEBPS/cover.png`
- **Inspection:** full size — pass; 160-pixel thumbnail — pass. Satchel on old-road/new-grid seam is collection-unique; dark lower field is a justified contrast treatment over tactile, active art rather than a dark-art default.
- **Final cover SHA-256:** `abd82438a29e37808da5c153a9b5d7bc9775a6aa328736d79f4f1f328d1eb457`

**Exact prompt for the selected art:**

```text
Use case: stylized-concept
Asset type: original portrait raster artwork for a premium nonfiction audiobook cover, art only
Primary request: Regenerate selected Candidate B for The New Deal, an educational book about Canada Post, CUPW, institutional change, and rural mail. Preserve the central thesis: a weathered postal satchel stands at the transition from an old rural road to a new measured service grid.
Scene/backdrop: a tactile Cape Breton rural landscape rendered as layered cut paper and weathered cartographic material; an old winding gravel road and stone edges transition visibly into a precise blue measured grid and route geometry.
Subject: one unbranded, well-used brown leather postal satchel with plain hardware, large and unmistakable, placed at the seam where the organic old road becomes the new measured grid. The satchel is the human-scale bridge between inherited rural service and measured institutional change.
Style/medium: premium tactile cut-paper collage with editorial realism, worn surfaces, dimensional paper edges, restrained hand-made imperfection.
Composition/framing: strict PORTRAIT 2:3 vertical composition. Place the satchel and road-to-grid seam through the upper and middle 65-75% of the canvas. The road rises and bends through the upper field while measured grid lines cross and organize the middle, keeping both areas active. Reserve ONLY the bottom 25-35% as a calmer dark-blue textured field for later title typography, with the grid fading softly into it. Strong 160-pixel thumbnail silhouette.
Lighting/mood: bright coastal daylight, grounded, humane, sober but hopeful; controlled dimensional shadows.
Color palette: worn leather brown, road grey, slate and coastal blue, cream paper, vivid route-yellow accent #F2B705.
Materials/textures: cracked unbranded leather, rough gravel paper, torn map layers, blueprint paper, thin route-yellow thread or painted line.
Text (verbatim): none.
Constraints: one central satchel; old-road/new-measured-grid transition must be instantly legible; active top and middle; only lower 25-35% calm; no organization branding or claims.
Avoid: Canada Post logo, CUPW logo, crown symbols, postal trademarks, false labels, fake stamps, propaganda poster styling, heroic worker propaganda, flags, title, subtitle, author, words, letters, numbers, typography, watermark, border, mockup, UI, dashboard, literal infographic, generic corporate stock art, crowded collage.
```

## The Voice in the Machine (`the-voice-in-the-machine`)

- **Title / slug:** The Voice in the Machine / `the-voice-in-the-machine`
- **Directions:**
  - **A — Sentence to Sound:** A paper sentence entering a small acoustic machine and leaving as a waveform ribbon.
  - **B — Phonetic Microphone:** An intimate microphone still life containing layered phonetic textures without text.
  - **C — Contained Voice Box:** A palm-sized maple-and-brass cutaway encloses bellows, reeds, a diaphragm, felt chambers, and an internal vibration path.
- **Selected:** A — Sentence to Sound
- **Accent / tone / layout:** `#FF9F1C` / `bright` / `bleed`
- **Generated-art filename:** `candidate-a-art.png`
- **Final / legacy cover:** `books/the-voice-in-the-machine/cover.png` / `books/the-voice-in-the-machine/cover-legacy.png`
- **EPUB / declared cover member:** `books/the-voice-in-the-machine/the-voice-in-the-machine.epub` / `OEBPS/cover.png`
- **Inspection:** full size — pass; 160-pixel thumbnail — pass. Blank paper enters a contained roller, resonating chamber, copper diaphragm, and horn before emerging as a physical amber sound ribbon; the top and middle carry the sequence while the lower field stays calm.
- **Final cover SHA-256:** `9ecdf6c46c44b5c906855f69a76f036af4cc8a5088a15ce21483eb316d7d0f17`

**Exact prompt for the selected art:**

```text
Use case: precise-object-edit
Asset type: portrait raster artwork for a premium nonfiction audiobook cover, art only
Input images: Image 1 is the edit target and current regenerated Voice A artwork.
Primary request: Recompose this exact paper -> contained acoustic machine -> amber sound ribbon still life so the physical transformation occupies and activates the upper 70-75% of the portrait, leaving only the bottom 25-30% as the calm title field.
Change only composition and framing: enlarge the existing paper strip, enclosed brushed-metal acoustic mechanism, copper diaphragm, horn channel, and amber ribbon slightly and extend their diagonal presence farther down through the middle. Preserve the same machine design, materials, bright high-key editorial style, warm ivory background, shadows, and amber #FF9F1C ribbon.
Composition/framing: strict PORTRAIT 2:3. Keep the top active with the large amber ribbon loop and tactile shadow. Keep the middle dominated by the blank paper -> machine -> sound transition. Begin the calm warm textured field at approximately 72% canvas height, not halfway down. No vacant pale upper half.
Text (verbatim): none.
Constraints: paper remains completely blank; machine remains physical, enclosed, acoustic, and human-scale; ribbon remains a physical sound-energy ribbon, not UI; lower calm field is only 25-30%; preserve all other visual qualities.
Avoid: changing the concept, removing the top ribbon, increasing blank lower field, title, subtitle, author, words, letters, numbers, typography, logo, watermark, border, mockup, phone, screen, UI, dashboard, code, robot, generic glowing technology, futuristic product render.
```

## Why It Feels Right (`why-it-feels-right`)

- **Title / slug:** Why It Feels Right / `why-it-feels-right`
- **Directions:**
  - **A — The Inviting Control:** Three tactile controls where only one correctly invites the hand.
  - **B — Teapot Grid:** An elegant teapot silhouette transformed into a spatial design grid.
  - **C — Settling Balance:** Bright layered glass, paper, and type-sized blocks settling into visual balance without text.
- **Selected:** B — Teapot Grid
- **Accent / tone / layout:** `#FF7A30` / `dark` / `bleed`
- **Generated-art filename:** `candidate-b-art.png`
- **Final / legacy cover:** `books/why-it-feels-right/cover.png` / `books/why-it-feels-right/cover-legacy.png`
- **EPUB / declared cover member:** `books/why-it-feels-right/why-it-feels-right.epub` / `OEBPS/cover.png`
- **Inspection:** full size — pass; 160-pixel thumbnail — pass. Teapot-to-design-grid metaphor is bold and tactile; black/orange geometry distinguishes it, and the dark lower field gives the long subtitle and title reliable contrast.
- **Final cover SHA-256:** `8b1ed29ae679522cff85d0716528e2a637d92f9e4ba16f558aeba5b8ac2cb5f7`

**Exact prompt for the selected art:**

```text
Create original portrait editorial artwork for a premium nonfiction audiobook cover about Why It Feels Right. The book's audience is new designers and SwiftUI builders learning why interfaces invite, guide, and settle, and its promise is a clear, humane and memorable way into Why It Feels Right. The single visual thesis is an elegant teapot silhouette transformed into a spatial design grid.

Show one unforgettable central metaphor: an elegant teapot silhouette transformed into a spatial design grid. Make that subject large, beautifully art-directed, and immediately legible at a small thumbnail. Use single teapot silhouette spans lower half and resolves into measured grid upward, with a strong silhouette, one clear focal point, and generous intentional negative space for title typography. The image should feel like a finished editorial book cover image, not an illustration for a slide deck.

Visual language: tactile cut-paper collage. Material and surface: ink black, warm cream, grid grey, expressive orange. Use a confident, eye-catching palette including a vivid signature accent #FF7A30 that is visibly present in the main image. Use sophisticated colour relationships, controlled contrast, dimensional light, and deliberate texture; avoid a washed-out pastel gradient. Make the result emotionally specific, grounded, and genre-appropriate without using genre clichés.

High-end art direction, specific physical detail, elegant composition, premium print sensibility, visual hierarchy, subtle human imperfection, striking colour, strong thumbnail read, original concept. No title, no subtitle, no author name, no lettering, no typography, no logo, no watermark, no border, no mockup, no book mockup, no audiobook icon, no interface, no dashboard, no floating UI cards, no generic infographic, no stock-photo look, no random symbols, no collage of tiny objects, no split-screen, no decorative icon cloud, no close imitation of any named artist, designer, publisher, or existing book cover.
```

## You Are the Architect (`you-are-the-architect`)

- **Title / slug:** You Are the Architect / `you-are-the-architect`
- **Directions:**
  - **A — Final Keystone:** A human hand placing the final keystone into an AI-built structure.
  - **B — Calibration Gate:** A blueprint becoming a real workshop with verification tools in the foreground.
  - **C — Directed Construction:** A conductor's baton directing modular construction pieces without robots or glowing brains.
- **Selected:** C — Directed Construction
- **Accent / tone / layout:** `#E43D30` / `bright` / `bleed`
- **Generated-art filename:** `candidate-c-art.png`
- **Final / legacy cover:** `books/you-are-the-architect/cover.png` / `books/you-are-the-architect/cover-legacy.png`
- **EPUB / declared cover member:** `books/you-are-the-architect/you-are-the-architect.epub` / `OEBPS/cover.png`
- **Inspection:** full size — pass; 160-pixel thumbnail — pass. Baton-directed construction arc has the most kinetic silhouette in the set; red, wood, plaster, and black stay distinct while the lower pink field remains calm.
- **Final cover SHA-256:** `c3fb6b82f0fa1de9a957f92eacfe9051afbfaf2dde4a55ffe92e1a270e7fe214`

**Exact prompt for the selected art:**

```text
Create original portrait editorial artwork for a premium nonfiction audiobook cover about You Are the Architect. The book's audience is AI-assisted software builders ready to replace prompting luck with direction and proof, and its promise is a clear, humane and memorable way into You Are the Architect. The single visual thesis is a conductor's baton directing modular construction pieces without robots or glowing brains.

Show one unforgettable central metaphor: a conductor's baton directing modular construction pieces without robots or glowing brains. Make that subject large, beautifully art-directed, and immediately legible at a small thumbnail. Use baton enters from lower-left, pieces assemble in one sweeping arc, quiet upper-right, with a strong silhouette, one clear focal point, and generous intentional negative space for title typography. The image should feel like a finished editorial book cover image, not an illustration for a slide deck.

Visual language: surreal editorial illustration. Material and surface: black lacquer, raw wood, plaster white, electric red. Use a confident, eye-catching palette including a vivid signature accent #E43D30 that is visibly present in the main image. Use sophisticated colour relationships, controlled contrast, dimensional light, and deliberate texture; avoid a washed-out pastel gradient. Make the result emotionally specific, grounded, and genre-appropriate without using genre clichés.

High-end art direction, specific physical detail, elegant composition, premium print sensibility, visual hierarchy, subtle human imperfection, striking colour, strong thumbnail read, original concept. No title, no subtitle, no author name, no lettering, no typography, no logo, no watermark, no border, no mockup, no book mockup, no audiobook icon, no interface, no dashboard, no floating UI cards, no generic infographic, no stock-photo look, no random symbols, no collage of tiny objects, no split-screen, no decorative icon cloud, no close imitation of any named artist, designer, publisher, or existing book cover.
```

## Collection review, regenerations, and limitations

The labelled eleven-cover review passed after one targeted collection-level regeneration: **Rodents in the Walls, Candidate A — Telltale Trail**. Its earlier mint framed hero-inset repeated *Findable* and became muddy at thumbnail scale; the accepted full-bleed wall cutaway removed that template repetition while preserving bright treatment and the corrected lower-title-field rule. No further collection-level regeneration was warranted.

Earlier per-title review also regenerated **Tests First B** after a square output and then an overly vacant upper field, and **The Bug Is a Clue A** after a dead upper field. Task 6 re-audited the final three-title batch against the actual lower-third compositor and replaced or recomposed art as needed. These interventions explain why some selected prompts are targeted-regeneration prompts rather than the original direction prompts.

Final whole-branch review added five separate built-in image-generation calls: a selected Voice A regeneration plus targeted recomposition, a selected New Deal B regeneration, and valid replacements for rejected Bug C and Voice C. The build ledger records every exact prompt, tool path, generated source, copied path, decision, history, and current status. All 33 current comparison slots now have complete, accepted images; every selected image has exact prompt provenance. Two discarded historical calls still lack recoverable exact prompts: **Why It Feels Right A, call 2** and **You Are the Architect B, call 2**. Those outputs were not selected, and no missing historical prompt was reconstructed.

The contact-sheet review found eleven unique selected-cover hashes and no publication-blocking outlier. Warm peach lower fields recur because the shared compositor derives them consistently, but title-specific metaphors, silhouettes, accents, camera angles, and material languages keep the collection distinct. Generated art remains illustrative; deterministic typography and package embedding happened after image generation.

## iCloud package sync

- Chicken Predators — updated
- Echo, From the Inside — no matching public package
- Findable — no matching public package
- Git Happens — no matching public package
- Rodents in the Walls — updated
- Tests First — no matching public package
- The Bug Is a Clue — no matching public package
- The New Deal — updated
- The Voice in the Machine — no matching public package
- Why It Feels Right — no matching public package
- You Are the Architect — no matching public package
