# Pronunciation decisions for book production

Use this across nonfiction, fiction, learning books, and classic adaptations.
Pronunciation is an authored part of the listening edition. Preserve ordinary
spelling in visible text; carry the chosen sounds separately into narration.
A clean audit or a plausible IPA string does not establish that the audio sounds
right. Report authored decisions, embedded annotations, renderer application,
and actual listening verification separately.

## Choose the pronunciation in context

Before packaging a new audiobook, review every occurrence of **content**,
**record**, and **read**, including headings, quotations, captions, and spoken
guide passages. Check other ambiguous words encountered in the manuscript too,
plus names, place names, abbreviations, and technical or archaic vocabulary.
Search is an inventory aid, not a pronunciation decision: inspect the sentence
and enough surrounding prose to determine sense, grammatical role, and tense.

| Word | Distinctions to preserve |
|---|---|
| content | Material or contents takes first-syllable stress; satisfied takes second-syllable stress. |
| record | A noun such as a historical record takes first-syllable stress; the verb meaning capture or document takes second-syllable stress. |
| read | Present/base forms sound like “reed”; past and past-participle forms sound like “red.” “I read every day” needs narrative tense/context; “I have read it” is a past participle. |

These are meaning reminders, not phoneme strings to feed the renderer. Do not
apply a book-wide pronunciation to a spelling with multiple senses. Use an
occurrence-specific annotation for each resolved instance of these three words,
even when automatic pronunciation currently happens to agree. Include relevant
inflected forms in the review; derive their actual pronunciation rather than
copying the base word's IPA. Unresolved context stays an explicit open decision.
Do not rewrite accepted prose merely to steer automatic pronunciation.

Keep a durable `pronunciation-plan.md` beside the book's source or research notes.
For each decision, record the original word or phrase, source file/section and
exact quoted context, which repeated occurrence is meant, intended sense/tense,
IPA, language/accent, evidence or author decision, intended scope, and verification
status. A word-level dictionary entry is appropriate for a name that has a single
chosen pronunciation throughout the book. Preserve exceptions per occurrence.
Use source locators during drafting; never invent Echo block IDs or rely on raw
word offsets surviving later edits.

Verify real-word IPA against a suitable dictionary or authoritative pronunciation
source in the intended accent. For fictional names, record the author's chosen
pronunciation; do not present it as dictionary evidence. Resolve uncertainty with
context and evidence before making a candidate authoritative. Keep standard IPA
and any renderer-specific representation distinct. Preserve approved name choices
across books while reassessing ambiguous words in their new sentences.

## Embed using the verified Echo contract

The intended transport is an EPUB containing inline `ssml:ph` with
`ssml:alphabet="ipa"` for individual occurrences, and linked PLS lexicons for
recurring terms. W3C describes these mechanisms in its
[EPUB text-to-speech note](https://w3c.github.io/epub-specs/wg-notes/tts/);
reader support is not universal. Echo owns the exact authoring/import contract,
IPA normalization and validation, override precedence, and supported diagnostics.

Before embedding, locate the Echo project's delivered authoring documentation
and fixture, and verify support in the installed renderer selected for this run.
Record the contract location/revision and renderer identity in the production
notes. Follow that contract's XHTML namespaces, PLS links and package entries,
annotation boundaries, supported alphabets, and user-correction precedence.
Use its supported authoring path; do not invent builder flags or assume
`build_book.py` preserves raw markup or bundles lexicons automatically.

While Echo integration is pending or unavailable, complete and retain the
pronunciation plan and continue independent manuscript work. Mark embedding and
renderer application pending; do not claim that a glossary or IPA in a footnote
controls narration. Use an existing supported override path only when its
application can be verified for the exact book and source occurrence. If no
supported path applies the required decisions, report that narration dependency
rather than presenting an uncorrected render as pronunciation-verified.

Once supported, add the annotations before the final EPUB is hashed and frozen.
Inspect the packaged XHTML, lexicons, and manifest to confirm that the builder
actually preserved them. Keep visible spelling and character/guide boundaries
intact. Export the real Echo inventory from that final EPUB and bind decisions
to its occurrences using the supported contract. A markup-only EPUB change still
changes source bytes: refresh source-bound inventories, voice plans, and render
receipts through their normal workflows. Never patch a frozen package in place
or reuse evidence from its previous hash.

## Verify what was spoken

Check every required occurrence against renderer evidence: intended IPA, actual
selected phonemes, and whether the annotation applied. Diagnose missing or
conflicting annotations and rejected symbols; successful import alone is not
proof of application. Respect explicit user pronunciation corrections and surface
conflicts with the authored plan. Do not silently strip unsupported phonemes.

Render targeted samples with the actual assigned voice and surrounding sentence.
Include each distinct sense of content, record, and read present in the book,
recurring unusual names, and any corrected or uncertain passage. For Michael's
passages use `am_michael`; a different speaker's successful sample does not verify
Michael's rendering. Check both sound and text/audio alignment. Use the existing
governed narration and pronunciation-review workflow for these samples and final
audio; this reference does not authorize a renderer build or bypass its checks.

After manuscript changes, reassess affected contexts and regenerate their
annotations; after pronunciation changes, invalidate affected audio through
Echo's supported workflow. Keep previous accepted artifacts recoverable. Existing
books are revised only when requested. Never claim words will always be correct:
report remaining uncertainty and distinguish phoneme verification from actual
human listening acceptance.

## Development-only handoff

Manuscript and concept-development skills collect known pronunciation decisions
and open questions in the same plan and include its path in the production
handoff. During concept work, a risk list is sufficient; complete the occurrence
review against the actual final manuscript during production. Keep annotations
outside accepted Markdown chapter bytes. A pronunciation plan does not authorize
EPUB creation, narration, or delivery in a manuscript-only task.
