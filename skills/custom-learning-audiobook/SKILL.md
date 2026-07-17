---
name: custom-learning-audiobook
description: Use when making a custom, personalized, beta-test, Echo-ready, or topic-request learning audiobook from a plain-language request such as "I want to learn X"; use for coworker/local tester books, sample learning books, public-safe library additions, or private learning packages; also use when a longform-book-development handoff packet is ready for production.
---

# Custom Learning Audiobook

Make a listener-specific learning audiobook from a topic request. The requester
should feel helped, not assigned homework: ask only useful questions, do the
research, write one coherent manuscript, and package the result for Echo. Run
all commands from the explainer-audiobooks repo root.

## Production mode comes first

Read `../../skill/references/unattended-production.md` before intake. A request
for an overnight, ready-to-listen, delegated, or multi-book result selects
`unattended-first-listen`: use documented defaults, record
`research/unattended-decisions.json`, and finish a private package without
routine questions. Treat unconditional human approval language below as the
`governed-final` lane. In unattended mode, use the shared editorial outline,
pilot, pronunciation, cover, delivery, and package-or-blocker rules. Never infer
permission to publish.

## Universal paired-cover publishing contract

Every new run creates exactly three coordinated portrait/square candidates.
Use `render_cover_pair(...)` in `skill/scripts/cover_pairs.py` to produce
`cover.png` at 1600×2560 and `m4b-cover.png` at 2400×2400 plus thumbnails and
receipts. Require review and explicit pair selection: human review in
governed-final or editorial rubric review for a private unattended-first-listen
package. Then use `cover_receipts.py select-pair --selection-source user` (or
`requested-mix`) for the paired receipt. Build with `build_book.py --cover ...
--m4b-cover ... --cover-selection ...`. Echo resolves the OPF-declared cover
before export and binds the exact resulting M4B bytes into the pronunciation
audit. Never run `replace_m4b_cover.py` or otherwise mutate an audited Echo M4B
after narration. Run `cover_receipts.py verify --cover ... --m4b-cover ...
--epub ... --m4b ...` for post-embed verification, then dry-run and apply
`sync_selected_cover.py --paired-artifact-dir ...` for governed
public/iCloud/site sync under the public/private rules below.

Order: research → three source directions → portrait/square render pairs →
thumbnail review → explicit pair selection → paired receipt → EPUB portrait +
M4B square embedding → post-embed verification → governed public/iCloud/site
sync. Legacy single-cover selection is verification-only compatibility.

Run the complete paired command sequence from the
"Complete paired command example" in `references/package-and-qc.md` —
including its rule for when `--permission-to-publish` may be passed — rather
than retyping it from memory.

## Required References

- Read `references/intake-and-research.md` before intake, safety checks, or
  research.
- Read `../../skill/references/unattended-production.md` before choosing whether
  the run is unattended-first-listen or governed-final.
- Read `references/package-and-qc.md` before building EPUB/Markdown, rendering
  M4B/alignment, copying packages, or reporting completion.
- Before any Echo render, create `research/pronunciation-plan.json`. Include
  listener-named risks such as `hyperparameter` and `hyperparameters`, plus
  risks found in the coverage ledger and manuscript. Use the governed partial
  probe and `build_pronunciation_probe_reel.py`; full narration requires
  accepted, hash-bound human listening evidence.
- Reuse the existing explainer tooling from this repo:
  - `../../skill/references/road-book-mode.md` for the default driving/delivery
    listening context, narrative teaching infrastructure, cognitive-load
    limits, optional-study boundary, and human comprehension authority.
  - `../../skill/references/learning-design.md` for learner orientation,
    grounded evidence notes, argument-level outlines, structured chapter teaching
    plans, section draft contexts, narrow revision passes, final learning review,
    and the hash-bound learning receipt.
  - `../../skill/references/curriculum-patterns.md` for choosing and recording a
    question-led narrative, mechanism-first spiral, end-to-end trace, or problem
    progression.
  - `../../skill/references/narration-style.md` for spoken style and QC sweeps.
  - `../../skill/references/frontier-manuscript-pipeline.md` for the artifactized
    research-outline-draft-revision pipeline, voice calibration, frontier-author
    / cheaper-worker split, continuity ledger, and citation-first reader review.
  - `../../skill/references/humanizer-pass.md` for the bounded `humanizer` pass
    that removes AI tics without replacing the frontier author's voice.
  - `../../skill/references/declaudification.md` for drafting-time prevention,
    phrase-family density review, and the hash-bound prose receipt.
  - `../../skill/references/cover-art.md` for cover concepts, visual quality,
    and the signature accent-colour rule.
  - `../../skill/scripts/build_book.py` for EPUB and combined Markdown.
  - `../../skill/scripts/make_cover.py` for cover rendering.
- If the request came from `longform-book-development`, read its handoff packet
  first — by convention at
  `.build/longform-book-development/<slug>/handoff/handoff-packet.md`; keep the
  same `<slug>` for this production run so the two workspaces cross-reference.
  Preserve every decision the packet records — outline, source, figure, voice,
  pronunciation-risk, pilot, revision-plan, and humanizer decisions — unless
  the user changes them, and copy approved figure assets from the longform
  workspace's `visuals/` folder into this run's `chapters/images/` per the
  packet's figure plan. A packet marked **development draft** cannot start
  pilot or canonical production; return it to `longform-book-development`
  instead of filling the gaps yourself.

## Defaults

| Decision | Default |
|---|---|
| Length | Standard beta book: about 2 hours, roughly 18,000-22,000 words |
| Deep mode | About 4 hours, roughly 40,000-45,000 words |
| Sampler | 45-75 minutes when the topic is vague or commitment is light |
| Audience | Curious beginner unless the request says otherwise |
| Listening mode | `road-book`, for driving and delivering mail; use `focused-study` only when the listener explicitly expects pause/rewind/visual work |
| Narrator | `am_michael`; automatic fallback `am_puck`; `af_heart` is an approved alternative only when the listener explicitly selects or accepts it |
| Audio renderer | Native Echo/Kokoro through the governed narration wrapper; no raw Debug CLI or Apple/system-voice substitute |
| Author metadata | `Dan Fakkeldy` |
| Writing model metadata | Record the frontier author as contributor/source note |
| Model routing | Separate calls and artifacts: cheaper workers prepare grounded evidence; the frontier model owns the argument-level outline, section-by-section Markdown prose, and substantive single-job revisions; cheaper workers handle citation checks, diagnostics, package/render/QC only. |
| Build folder | `.build/custom-learning-audiobooks/<slug>/` |
| Delivery copy | Public-safe: iCloud Drive `Books/<Title>/` by default. Private/sensitive: agreed private project folder; iCloud Books reading copy only on explicit user request. |

## Workflow

1. **Create a run folder.** Use
   `.build/custom-learning-audiobooks/<slug>/` with `research/`, `chapters/`,
   and `dist/` subfolders. Seed `research/` by copying the schema-v2 starter
   records from `../../skill/templates/learning-design/` and reading its
   `instructions.md`, rather than hand-building each JSON record. Keep source
   notes and scratch artifacts out of public book folders.

2. **Clarify only what matters.** In governed-final, ask at most 3-5 useful
   questions from `references/intake-and-research.md`. In unattended-first-listen,
   do not ask about routine preferences: choose conservative defaults and bind
   them in `research/unattended-decisions.json`.
   Create `research/learning-brief.json` with the learner outcome, actual prior
   knowledge, audience level, `road-book` listening context (driving and
   delivering mail by default), revision mode, opening orientation (context,
   promise, route), original/current word estimates, estimated range, drafting
   status, and scope history. Use `first-edition-plus` when an earlier book
   taught successfully. Never lower the target after drafting begins without
   explicit user approval recorded under
   `../../skill/references/learning-design.md`; word count is not a packaging
   floor.

3. **Classify safety and public/private status before writing.** Decide whether
   the book is public-safe, private, or sensitive/high-stakes. Sensitive topics
   need narrowing, refusal, or educational-only framing. Private books never go
   into the public repo or public KB.

4. **Research for the listener.** Use quick, deep, Open Notebook, user-supplied,
   or mixed research mode. Label source confidence. The requester does not have
   to provide sources. Browse current or high-stakes topics when needed. Cheaper
   workers may extract and reconcile evidence, but their deliverable is
   `research/evidence-notes.md` plus hash-bound
   `research/evidence-notes.json`, stable claim IDs, citations, precise locators,
   contradictions, and uncertainty — never a substitute manuscript. Set
   `claimPolicy: traceable-only`; later phases may make only claims traceable to
   this artifact.

   If the user names private books or audio as an enjoyable technical-writing
   reference, create a private `research/voice-source-profile.md`. Extract only
   high-level craft: opening move, evidence-to-example movement, plain-language
   mechanism, direct address, humor boundary, uncertainty, rhythm, practical
   landing, and visual-to-audio adaptations. Bind the voice-source profile in
   `comprehension-pilot.json`; do not commit source files or raw excerpts, and do
   not request a pastiche. The accepted first section becomes the actual voice
   exemplar.

5. **Build and authorize the argument-level outline.** Build a short table of
   contents around a governing question and what the listener wants to
   understand or do. A beginner road-book chooses six to ten durable outcomes,
   no more than two or three new core terms per chapter, people/history anchors,
   varied real-world applications, a narrative spine, at least four chapter
   jobs, analogy contracts, and an optional-study layer for derivations and
   specialist terminology. For every core concept, record its problem before
   name, real applications, expected ability, and retrieval after a gap. Vary
   chapter jobs and target estimates; do not divide the total word count into
   identical chapters. Governed-final pauses for human road-book approval before
   pilot prose. Unattended-first-listen records independent editorial
   authorization and continues under the shared contract.

   Record the approved progression and evidence in
   `research/learning-outline.json`, including the selection, reason, and fit
   evidence required by `../../skill/references/curriculum-patterns.md`. Every
   planned section records its job, argument, specific evidence-note claim IDs,
   throughline advance, narrative or metaphor payoff, intellectual or emotional
   landing beat, and what it must not repeat. Obtain human approval for this
   argument-level outline before pilot prose. Create the complete structured
   `research/chapter-plans.json` and `research/coverage-ledger.json` before
   canonical drafting. A topic or terminology inventory is not a learning arc.
   Every concept row needs its durable outcome, definition, reason, mechanism,
   concrete case, problem before name, real-world applications, useful boundary
   or explicit not-applicable reason, misconception, expected ability, analogy
   contract or omission reason, named chapter uses, and planned retrieval.

6. **Calibrate the first section and accept the narrated comprehension pilot.**
   Give the frontier author the full outline, grounded notes, voice-source
   profile, section job, and no-repeat list. Revise only that first section until
   the human accepts its teaching and voice, then preserve the project-authored
   `research/voice-exemplar.md`. Record the outline and first-section human
   checkpoints in `research/comprehension-pilot.json` before remaining drafting.

   Use only enough frontier-authored material for 10 to 15 representative minutes, including
   the opening and first technical passage. Build it with
   `build_book.py --learning-pilot` and a mandatory `-pilot` slug, then render it
   through the dedicated governed `scripts/echo_learning_pilot_narrate.sh`
   wrapper. This
   isolated pre-receipt path does not require final cover selection or accepted
   full-book pronunciation evidence, and it must not be replaced with the final
   package wrapper or a raw `echo-cli narrate` call. In `governed-final`, the
   intended listener hears it in a representative context and records one
   lightweight `continue` or `revise` verdict against the exact audio hash.
   Accept optional listener notes, but do not ask comprehension questions or
   require a written explanation. In `unattended-first-listen`, an independent
   editorial reviewer records the pilot verdict and human comprehension remains
   pending; never fabricate a listener decision. Do not start the remaining
   manuscript without the first-section checkpoint and the decision required by
   the selected lane. An autonomous-run request does not waive human
   comprehension authority: it preserves that authority as pending. Follow
   `../../skill/references/unattended-production.md` before drafting the rest.

7. **Plan any interior pictures.** If the user wants pictures, or a handoff
   packet includes a figure plan, gather only usable images: user-supplied,
   generated, self-created, public-domain, permissively licensed, or explicitly
   permissioned. Save them under `chapters/images/`, keep a provenance note in
   `research/visuals.md`, and plan chapter placement with alt text and captions.
   Treat unclear web images as visual references, not package assets.

8. **Write section by section with one lead writer — a frontier model.** The frontier model owns the
   outline,
   explanation choices, voice, canonical Markdown chapters, and every substantive
   revision. Do not fan out chapter writing or generate the book in one call.
   Before each section, complete its `research/continuity.json.draftContexts`
   entry and provide the full argument-level outline, relevant claim IDs and fact
   pack, coverage-ledger rows, accepted voice exemplar, previous section text or
   faithful running summary, the current section job, and what it must not repeat.
   Update `research/continuity.md` and structured `research/continuity.json` after
   each section with terms already defined, examples/analogies used, deliberate
   callbacks, unresolved promises, retrievals, listener load, and no-repeat
   constraints.
   Also provide the listener's **AI-writing patterns to avoid** and the complete
   `declaudification.md` drafting rule. State facts directly instead of managing
   the listener's reaction with `hold`, `sit with`, `notice`, or synonym-cycled
   commands.

9. **Keep Markdown canonical; use cheap workers as evidence and production
   sidecars.** Save the frontier author's chapter files under `chapters/`. Cheap
   workers may produce cited research, a beginner-reader report, prose-lint
   findings, cover candidates, and manifest templates, but not a competing prose
   draft. EPUB/M4B assembly waits until the accepted manuscript clears Step 11.
   A cheap model may make only meaning-preserving mechanical fixes; send all
   depth, factual, structural, and voice repairs back to the frontier author. Add
   approved figures as standalone Markdown image paragraphs, for example
   `![Alt text](images/example.png "Caption")`.

10. **Design and render the cover candidates.** Create **exactly three award-worthy,
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

   Save the shared art and both schema-v2 specs in each candidate directory,
   then use the complete `render_cover_pair(...)` call above for candidates 1
   through 3. Human-review every full-size portrait and square render and
   generated 160-pixel thumbnail with its art-and-type brief, font/palette note,
   and warnings. The renderer never selects automatically; a requested mix
   becomes a new specification and render. Record the human choice with
   `selection_source=user` (or `requested-mix`), but defer the
   `cover-selection.json` command and governed EPUB build until the canonical
   Markdown finishes humanization, prose QC, frontier-author acceptance, and
   every substantive repair.

11. **Humanize and complete prose QC before packaging.** Start with the narrow
    revision ledger; humanization remains a later bounded voice pass.
    Do not issue one vague "make it better" request. Complete
    `research/revision-passes.json` as separate single-job calls:
    `claim-traceability`, `tightening`, `de-listification`, `sentence-rhythm`,
    and a rendered `ear-pass`. Use Echo or Kokoro for the ear-pass and record
    each narration stumble and each point where the listener loses the thread.
    Bind the revision ledger to the final canonical chapter hashes.

    Then run
    `python3 skill/scripts/prose_qc.py --chapters-dir <build>/chapters --out
    <build>/research/prose-qc-before.md --fail-on-style` for the initial
    independent inventory, then have a cheaper reviewer produce only
    citation-first findings for redundancy, unexplained leaps, shallow concepts,
    jargon without a concrete case, and formulaic openings/closings, saved as
    `research/editorial-review.md`. Compare each
    finding with the coverage ledger. The frontier author accepts or rejects each
    finding and makes every accepted substantive, factual, structural, depth, and
    voice repair in the canonical Markdown before any EPUB or audio build.

    Before humanizing, run the independent structure review and a blind
    sequential beginner review using
    `../../skill/references/learning-design.md`. Give the blind reviewer only the
    manuscript heard so far, not the outline, ledger, expected abilities, or
    author rationale. The frontier author resolves accepted findings; reviewers
    do not supply replacement chapters.

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
    Markdown must be final before Step 12 starts.

    Run the independent inventory and final family-density gate exactly as
    specified in `../../skill/references/declaudification.md`. The final command
    uses `--fail-on-style`, records accepted and rejected decisions, and writes
    `research/prose-style-receipt.json` bound to the final chapter hashes.

    Rerun both learning reviews after every accepted voice edit. Record their
    distinct reviewers, passing verdicts, citation-first decisions, and final
    `reviewedChapterSHA256` map in `research/learning-review.json`. Generate the
    separate learning receipt:

    ```bash
    python3 skill/scripts/learning_design_qc.py \
      --run-root "$RUN_ROOT" \
      --receipt-out "$RUN_ROOT/research/learning-design-receipt.json"
    ```

    The learning and prose receipts must bind the same canonical chapter hashes.
    The learning receipt proves process evidence and an accepted pilot, not
    learning transfer; later negative human listening evidence overrides it.

12. **Build the governed EPUB.** Only now follow the paired selection and EPUB
    sections in `references/package-and-qc.md`: create the paired receipt with
    `cover_receipts.py select-pair`, then run the governed `build_book.py`
    command with `--cover`, `--m4b-cover`, and `--cover-selection`. The EPUB and combined
    Markdown are downstream renderings of the accepted manuscript; standalone
    Markdown figures remain embedded and copied beside the combined Markdown.
    New builds also pass `--prose-receipt
    "$RUN_ROOT/research/prose-style-receipt.json"` and `--learning-receipt
    "$RUN_ROOT/research/learning-design-receipt.json"`; packaging stops if
    either is missing, failed, or stale.

13. **Render native Echo audio.** First create
   `research/pronunciation-plan.json` if it does not already exist: record each
   risky term and every spoken variant, its source (`listener`,
   `coverage-ledger`, or `author`), why it matters, and the chapters where all
   forms occur. A planned record permits only a bounded partial render; promote
   required terms to `accepted` only after human listening to the governed
   reel.

   Narrate through the governed Echo narration wrapper from
   `references/package-and-qc.md` with `--voice am_michael` first and `am_puck`
   only as an automatic Echo voice fallback. When the listener explicitly
   selects or accepts `af_heart` from an audition, use it through the same
   governed wrapper instead. The wrapper owns the Release preflight,
   content-addressed paths, FD-backed resource leases, and locked pre/post hash
   verification for everything it emits; the reference documents those
   internals, and the scripts enforce them regardless of caller behavior.
   Do not bypass the wrapper with a direct CLI command. Supply and record the
   reviewed `APPROVED_ECHO_PRONUNCIATION_SHA`; the preflight fails closed
   unless it exactly equals the clean Echo source `HEAD` being built.

   Echo audio is part of the delivery contract: do not impose your own time
   limit, deadline, or "too slow" threshold just because synthesis may take
   hours. Let long renders run, resume partial renders through the wrapper, or
   report the exact live blocker. Do not replace Echo/Kokoro with macOS `say`,
   Apple system voices, AVSpeechSynthesizer, audiobook-app TTS, or any other
   non-Echo renderer unless the user explicitly asks for that non-Echo
   preview/fallback after you name the tradeoff. Produce the run-scoped
   `<slug>.m4b` and `<slug>.alignment.json` whenever the CLI can run.

   Pronunciation review is on by default and produces a pronunciation audit
   plus an optional pronunciation reel. Do not pass `--no-pronunciation-review`
   for a governed render. For a governed real-book pronunciation probe, use the
   wrapper's `--max-chapters 1`, listen to the sealed chapter capture, and
   continue with `--resume --max-chapters 1`; CLI exit 2 means the run is
   partial and has no accepted M4B or deliverable sidecar yet. A render is
   complete only when the wrapper publishes the schema-v2 success receipt and
   atomically replaces the current-accepted selector, as specified in the
   reference. If native Echo audio is blocked and the user has not approved a
   non-Echo substitute, surface only the EPUB/Markdown from the run folder as
   clearly labelled interim files and report the blocker. Do not call that an
   Echo-ready or complete governed package, and do not proceed to delivery
   sync.

14. **Final-verify the governed package.** After native Echo narration succeeds,
    verify that the paired receipt matches the portrait, square, EPUB, and M4B.
    Also verify the render-success receipt and pronunciation audit. Never replace
    the cover or otherwise rewrite the audited M4B after Echo emits it.
    Legacy single-cover receipts are verification-only compatibility; their
    preserved command shapes live in `references/package-and-qc.md`. New
    packages verify the pair:

    ```bash
    SELECTED="<selected candidate number>"
    DIST=".build/custom-learning-audiobooks/$SLUG/dist"
    PAIR="$DIST/candidate-$SELECTED"
    : "${AUDIOBOOK:?set from the verified current-accepted selector as shown in package-and-qc.md}"
    /usr/local/bin/python3 skill/scripts/cover_receipts.py verify \
      --selection "$DIST/cover-selection.json" \
      --cover "$PAIR/cover.png" \
      --m4b-cover "$PAIR/m4b-cover.png" \
      --epub "$DIST/$SLUG.epub" \
      --m4b "$AUDIOBOOK" \
      --receipt "$DIST/cover-selection.json"
    ```

    Parse alignment JSON, run `verify-sidecar`, inspect M4B duration with
    `ffprobe`, validate pronunciation-audit schema/coverage/watch counts, inspect
    the pronunciation reel when present, run any available Echo QA, and verify
    EPUB figures before delivery. Keep human listening explicitly `pending` until
    the reel or matching final-audiobook passages have actually been heard. A
    failed receipt or media check returns to the build/audio step; it never falls
    through to copying.

15. **Package and copy.** Write `README.md` or `manifest.json` in `dist/`, then
    follow `references/package-and-qc.md`. Run `sync_selected_cover.py` first as
    a dry run, read its destination classification, and add `--apply` only after
    the result and chosen `reuse`/`supersede` intent are expected. Public-safe
    packages keep the default iCloud Books delivery behavior and may publish to
    the public repo only when permission and repo artifact policy allow the
    governed sync. Private or sensitive packages stay in the agreed private
    project folder and receive an iCloud Books reading copy only on an explicit
    user request. Private/sensitive artifacts never enter the public repo or
    public KB. Use `~/Downloads/book-inbox` only as optional import staging.

16. **Report plainly.** Include title, slug, privacy status, research mode,
    source-confidence label, word count, runtime, narrator, frontier author
    model, lower-cost review/production roles used, output paths, the actual
    delivery folder, receipt/destination classifications, and which QC gates
    passed or were skipped. Include the pronunciation audit, optional
    pronunciation reel, coverage/watch-count summary, human listening status,
    approved/source Echo revisions, and EPUB/CLI hashes from the render-input
    receipt. Report an iCloud Books path only when a copy was actually created.
    If the book includes pictures, report figure count and any image rights/privacy
    caveats.

## Hard Rules

- Do not make the requester look up sources.
- Do not collapse research, argument outlining, section drafting, and revision
  into one call. Each phase produces the artifact required by the next.
- Do not commit raw passages from a private voice source or ask for a close
  pastiche; preserve the bounded craft profile and project-authored exemplar.
- Do not replace road-book mode with a terminology syllabus. Driving and
  delivering mail is the default listening context; derivations, symbolic
  chains, and specialist catalogs belong in optional study material or a short
  focused lesson.
- In governed-final, do not draft the full manuscript before the intended
  listener accepts the first-section voice exemplar and hash-bound narrated
  comprehension pilot. In unattended-first-listen, require the shared
  hash-bound editorial checkpoints and preserve human comprehension as pending.
- Do not treat an autonomous-run request, learning receipt, prose receipt, or
  valid package as authority over a negative human comprehension verdict.
- Do not fan out substantive chapter prose or let a cheaper model replace a
  frontier-authored chapter. Cheaper workers may report evidence and apply only
  meaning-preserving mechanical corrections; the frontier author decides and
  writes depth, structural, factual, and voice changes.
- Do not turn medical, legal, financial, safety-critical, workplace-private,
  customer, confidential, or professional-advice topics into advice books.
- Do not publish or commit a requester book unless it is public-safe and the
  user has permission to add it to the public learning library.
- Do not copy private generated artifacts into the public repo or public KB.
- Keep `am_michael` as the default narrator. Use `af_heart` only when the
  listener explicitly selects it or accepts it from a voice audition; never
  make it a silent fallback.
- Do not invent a timebox for audio rendering. A multi-hour Echo/Kokoro render
  is allowed work, not a reason to downgrade the package.
- Do not use Apple/macOS/system narration as a fallback for Echo audio unless
  the user explicitly asks for a non-Echo preview or substitute.
- Do not bypass the governed narration wrapper with a raw `echo-cli narrate` or
  DerivedData `Debug/echo-cli` command.
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
- Do not use `--legacy-without-learning-receipt` for a new or revised
  manuscript, edition, or current-workflow claim. It is old-artifact
  reproduction only. `--learning-pilot` is for the explicitly named nonpackage
  comprehension pilot and cannot support a completion or delivery claim.
