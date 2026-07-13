---
name: custom-learning-audiobook
description: Use when making a custom, personalized, beta-test, Echo-ready, or topic-request learning audiobook from a plain-language request such as "I want to learn X"; use for coworker/local tester books, sample learning books, public-safe library additions, or private learning packages.
---

# Custom Learning Audiobook

## Universal paired-cover publishing contract

Every new run creates exactly three coordinated portrait/square candidates.
Use `render_cover_pair` in `skill/scripts/cover_pairs.py` to produce `cover.png`
at 1600×2560 and `m4b-cover.png` at 2400×2400 plus thumbnails and receipts.
Require human review and explicit pair selection, then use `cover_receipts.py
select-pair` for the paired receipt. Build with `build_book.py --cover ...
--m4b-cover ... --cover-selection ...`; after narration use
`replace_m4b_cover.py --cover ... --portrait-cover ... --cover-selection ...`
to preserve audio. Run `cover_receipts.py verify --cover ... --m4b-cover ...
--epub ... --m4b ...` for post-embed verification, then dry-run and apply
`sync_selected_cover.py --paired-artifact-dir ...` for governed
public/iCloud/site sync under the public/private rules below.

Order: research → three source directions → portrait/square render pairs →
thumbnail review → explicit pair selection → paired receipt → EPUB portrait +
M4B square embedding → post-embed verification → governed public/iCloud/site
sync. Legacy single-cover selection is verification-only compatibility.

Make a listener-specific learning audiobook from a topic request. The requester
should feel helped, not assigned homework: ask only useful questions, do the
research, write one coherent manuscript, and package the result for Echo.

## Required References

- Read `references/intake-and-research.md` before intake, safety checks, or
  research.
- Read `references/package-and-qc.md` before building EPUB/Markdown, rendering
  M4B/alignment, copying packages, or reporting completion.
- Reuse the existing explainer tooling from this repo:
  - `../../skill/references/narration-style.md` for spoken style and QC sweeps.
  - `../../skill/references/frontier-manuscript-pipeline.md` for the frontier-author
    / cheaper-worker split, continuity ledger, and citation-first reader review.
  - `../../skill/references/humanizer-pass.md` for the bounded `humanizer` pass
    that removes AI tics without replacing the frontier author's voice.
  - `../../skill/references/cover-art.md` for cover concepts, visual quality,
    and the signature accent-colour rule.
  - `../../skill/scripts/build_book.py` for EPUB and combined Markdown.
  - `../../skill/scripts/make_cover.py` for cover rendering.
- If the request came from `longform-book-development`, read its handoff packet
  first and preserve approved outline, source, and figure decisions unless the
  user changes them.

## Defaults

| Decision | Default |
|---|---|
| Length | Standard beta book: about 2 hours, roughly 18,000-22,000 words |
| Deep mode | About 4 hours, roughly 40,000-45,000 words |
| Sampler | 45-75 minutes when the topic is vague or commitment is light |
| Audience | Curious beginner unless the request says otherwise |
| Narrator | `am_michael`; fallback `am_puck`; do not default to `af_heart` |
| Audio renderer | Native Echo/Kokoro through `echo-cli narrate`; no Apple/system-voice substitute |
| Author metadata | `Dan Fakkeldy` |
| Writing model metadata | Record the frontier author as contributor/source note |
| Model routing | Frontier model: outline, Markdown prose, substantive revisions. Cheaper workers: research extraction, citation checks, diagnostics, package/render/QC only. |
| Build folder | `.build/custom-learning-audiobooks/<slug>/` |
| Delivery copy | Public-safe: iCloud Drive `Books/<Title>/` by default. Private/sensitive: agreed private project folder; iCloud Books reading copy only on explicit user request. |

## Workflow

1. **Create a run folder.** Use
   `.build/custom-learning-audiobooks/<slug>/` with `research/`, `chapters/`,
   and `dist/` subfolders. Keep source notes and scratch artifacts out of
   public book folders.

2. **Clarify only what matters.** If the request is broad, ask at most 3-5
   questions from `references/intake-and-research.md`. If the requester is not
   available, choose conservative defaults and state them in the manifest.

3. **Classify safety and public/private status before writing.** Decide whether
   the book is public-safe, private, or sensitive/high-stakes. Sensitive topics
   need narrowing, refusal, or educational-only framing. Private books never go
   into the public repo or public KB.

4. **Research for the listener.** Use quick, deep, Open Notebook, user-supplied,
   or mixed research mode. Label source confidence. The requester does not have
   to provide sources. Browse current or high-stakes topics when needed. Cheaper
   workers may extract and reconcile evidence, but their deliverable is a cited
   fact pack and uncertainty list — never a substitute manuscript.

5. **Outline the book and build the learning ledger.** Build a short table of
   contents around what the listener wants to understand or do. For every core
   concept, record in `research/coverage-ledger.md`: its first explanation,
   planned later retrieval/deepening/application, a real example, an expected
   listener ability, and why any repeated mention earns its place. Vary chapter
   jobs and target ranges; do not divide the total word count into identical
   chapters. For Dan/internal runs, get outline approval unless the user
   explicitly asked for a full autonomous run.

6. **Plan any interior pictures.** If the user wants pictures, or a handoff
   packet includes a figure plan, gather only usable images: user-supplied,
   generated, self-created, public-domain, permissively licensed, or explicitly
   permissioned. Save them under `chapters/images/`, keep a provenance note in
   `research/visuals.md`, and plan chapter placement with alt text and captions.
   Treat unclear web images as visual references, not package assets.

7. **Write with one lead writer — a frontier model.** The frontier model owns the
   outline,
   explanation choices, voice, canonical Markdown chapters, and every substantive
   revision. Do not fan out chapter writing. If the book is too long for one
   context, write `ch01.md`, `ch02.md`, and so on sequentially with the same
   frontier author; before each chapter provide the approved TOC, the relevant
   fact pack, the coverage-ledger rows, and `research/continuity.md`. Update that
   record after each chapter with terms already defined, examples/analogies used,
   deliberate callbacks, and promises that later chapters must resolve.

8. **Keep Markdown canonical; use cheap workers as evidence and production
   sidecars.** Save the frontier author's chapter files under `chapters/`. Cheap
   workers may produce cited research, a beginner-reader report, prose-lint
   findings, cover candidates, and manifest templates, but not a competing prose
   draft. EPUB/M4B assembly waits until the accepted manuscript clears Step 10.
   A cheap model may make only meaning-preserving mechanical fixes; send all
   depth, factual, structural, and voice repairs back to the frontier author. Add
   approved figures as standalone Markdown image paragraphs, for example
   `![Alt text](images/example.png "Caption")`.

9. **Design and render the cover candidates.** Create **exactly three award-worthy,
   complete art-and-type cover candidates by default**, then ask the user to
   choose or request a mix.
   Follow `../../skill/references/cover-art.md` for the research-derived visual
   directions, genre calibration, candidate briefs, acceptance bar, and
   rights-safe provenance rules. The three candidates must differ in metaphor,
   composition, palette, material language, and title strategy.
   Font, line breaks, scale, placement, and effects are part of the candidate—not
   a shared footer applied afterward.

   Use original generated raster art from the strongest available image tool
   (use it directly, e.g. `image_gen`) whenever one is available. Do not
   substitute bespoke SVG, programmatic vector art, diagrams, or icon
   compositions merely because they are faster or deterministic. SVG is allowed
   only when the user explicitly requests vector art, or when no image-generation
   tool is available and the user approves that fallback after seeing the
   limitation. Rights-cleared raster photography or art remains acceptable when
   it is the stronger editorial choice. Use the copy-ready editorial prompt in
   `../../skill/references/cover-art.md` to keep each visual thesis and physical
   metaphor specific and give it an eye-catching 2–4-colour palette. Keep
   generated art text-free: no lettering, logos, watermarks, interface,
   infographic, mockup frame, or close imitation of a named existing
   cover/designer. Reject and regenerate weak or generic output, and include one
   bright/high-key candidate unless the subject truly requires three dark
   directions.

   Save each art file beside its validated `cover-spec-N.json`, then render each
   complete candidate with the specification-driven path:

   ```bash
   SLUG="<slug>"
   RUN_ROOT=".build/custom-learning-audiobooks/$SLUG"
   /usr/local/bin/python3 skill/scripts/make_cover.py \
     --spec "$RUN_ROOT/dist/cover-spec-1.json" \
     --out "$RUN_ROOT/dist/cover-1.png"
   ```

   Repeat for candidates 2 and 3. Human-review every full-size render and
   generated 160-pixel thumbnail with its art-and-type brief, font/palette note,
   and warnings. The renderer never selects automatically; a requested mix
   becomes a new specification and render. Record the human choice with
   `selection_source=explicit-user-choice` (or `requested-mix`), but defer the
   `cover-selection.json` command and governed EPUB build until the canonical
   Markdown finishes humanization, prose QC, frontier-author acceptance, and
   every substantive repair.

10. **Humanize and complete prose QC before packaging.** Run
    `python3 skill/scripts/prose_qc.py --chapters-dir <build>/chapters --out
    <build>/research/prose-qc.md`, then have a cheaper reviewer produce only
    citation-first findings for redundancy, unexplained leaps, shallow concepts,
    jargon without a concrete case, and formulaic openings/closings. Compare each
    finding with the coverage ledger. The frontier author accepts or rejects each
    finding and makes every accepted substantive, factual, structural, depth, and
    voice repair in the canonical Markdown before any EPUB or audio build.

    After those substantive repairs, load the `humanizer` skill and follow
    `../../skill/references/humanizer-pass.md`. Make only targeted voice edits:
    remove AI-isms, generic signposting, inflated claims, filler, and repetitive
    rhythm while preserving facts, citations, technical names, teaching
    structure, intentional retrieval, and the frontier author's voice. Do not invent
    anecdotes, feelings, opinions, first-person experience, sources, jokes, or new
    claims; do not rewrite the book wholesale. The frontier author
    reviews and accepts every non-mechanical suggestion. Record touched chapters
    and rejected/skipped suggestions, then rerun factual, coverage-ledger,
    narration, sensitive-term, figure-provenance, and prose checks. The canonical
    Markdown must be final before Step 11 starts.

11. **Build the governed EPUB.** Only now follow the paired selection and EPUB
    sections in `references/package-and-qc.md`: create the paired receipt with
    `cover_receipts.py select-pair`, then run the governed `build_book.py`
    command with `--cover`, `--m4b-cover`, and `--cover-selection`. The EPUB and combined
    Markdown are downstream renderings of the accepted manuscript; standalone
    Markdown figures remain embedded and copied beside the combined Markdown.

12. **Render native Echo audio.** Use Echo's `echo-cli narrate` path from
   `references/package-and-qc.md` with `--voice am_michael` first and `am_puck`
   only as an Echo voice fallback. Echo audio is part of the delivery contract:
   do not impose your own time limit, deadline, or "too slow" threshold just
   because synthesis may take hours. Let long renders run, resume partial
   renders, or report the exact live blocker. Do not replace Echo/Kokoro with
   macOS `say`, Apple system voices, AVSpeechSynthesizer, audiobook-app TTS, or
   any other non-Echo renderer unless the user explicitly asks for that
   non-Echo preview/fallback after you name the tradeoff. Produce `<slug>.m4b`
   and `<slug>.alignment.json` whenever the CLI can run. If native Echo audio is
   blocked and the user has not approved a non-Echo substitute, surface only the
   EPUB/Markdown from the run folder as clearly labelled interim files and report
   the blocker. Do not call that an Echo-ready or complete governed package, and
   do not proceed to delivery sync.

13. **Final-verify the governed package.** After native Echo narration succeeds,
    verify that the paired receipt matches the portrait, square, EPUB, and M4B.
    The older command below is verification-only compatibility for legacy
    single-cover receipts; new packages use the paired verification command in
    `references/package-and-qc.md`:

    ```bash
    SELECTED="<selected candidate number>"
    DIST=".build/custom-learning-audiobooks/$SLUG/dist"
    /usr/local/bin/python3 skill/scripts/cover_receipts.py verify \
      --selection "$DIST/cover-selection.json" \
      --cover "$DIST/cover-$SELECTED.png" \
      --epub "$DIST/$SLUG.epub" \
      --m4b "$DIST/$SLUG.m4b" \
      --receipt "$DIST/cover-selection.json"
    ```

    Parse alignment JSON, inspect M4B duration with `ffprobe`, run any available
    Echo QA, and verify EPUB figures before delivery. A failed receipt or media
    check returns to the build/audio step; it never falls through to copying.

14. **Package and copy.** Write `README.md` or `manifest.json` in `dist/`, then
    follow `references/package-and-qc.md`. Run `sync_selected_cover.py` first as
    a dry run, read its destination classification, and add `--apply` only after
    the result and chosen `reuse`/`supersede` intent are expected. Public-safe
    packages keep the default iCloud Books delivery behavior and may publish to
    the public repo only when permission and repo artifact policy allow the
    governed sync. Private or sensitive packages stay in the agreed private
    project folder and receive an iCloud Books reading copy only on an explicit
    user request. Private/sensitive artifacts never enter the public repo or
    public KB. Use `~/Downloads/book-inbox` only as optional import staging.

15. **Report plainly.** Include title, slug, privacy status, research mode,
    source-confidence label, word count, runtime, narrator, frontier author
    model, lower-cost review/production roles used, output paths, the actual
    delivery folder, receipt/destination classifications, and which QC gates
    passed or were skipped. Report an iCloud Books path only when a copy was
    actually created. If the book includes pictures, report figure count and any
    image rights/privacy caveats.

## Hard Rules

- Do not make the requester look up sources.
- Do not fan out substantive chapter prose or let a cheaper model replace a
  frontier-authored chapter. Cheaper workers may report evidence and apply only
  meaning-preserving mechanical corrections; the frontier author decides and
  writes depth, structural, factual, and voice changes.
- Do not turn medical, legal, financial, safety-critical, workplace-private,
  customer, confidential, or professional-advice topics into advice books.
- Do not publish or commit a requester book unless it is public-safe and the
  user has permission to add it to the public learning library.
- Do not copy private generated artifacts into the public repo or public KB.
- Do not use `af_heart` as the default narrator.
- Do not invent a timebox for audio rendering. A multi-hour Echo/Kokoro render
  is allowed work, not a reason to downgrade the package.
- Do not use Apple/macOS/system narration as a fallback for Echo audio unless
  the user explicitly asks for a non-Echo preview or substitute.
- Do not leave a public-safe finished package only in `~/Downloads/book-inbox`
  or the transient `.build/` folder; use the governed default iCloud delivery.
- Private or sensitive packages stay in the agreed private project folder and
  receive an iCloud Books reading copy only on an explicit user request.
- Do not include pictures in a public package unless their rights and privacy
  status are clear. Keep private, client, workplace, and personally sensitive
  images out of public repo and KB surfaces.
- Do not include decorative images without a learning, evidence, reference, or
  orientation purpose.
- Do not ship a generic title-on-colour cover when generating a cover yourself:
  make a real image-led cover, and make the derived accent colour visible enough
  to work as the book's library identity.
- Do not default every candidate to a dark background; bright covers are allowed
  and should be offered when they better sell the book.
- Do not use SVG or programmatic vector artwork for a generated cover when an
  image-generation tool is available. Generate raster artwork and inspect it at
  full size and thumbnail size as part of each complete art-and-type candidate.
- Do not select a cover automatically or build a new package without its
  explicit `cover-selection.json` receipt.
