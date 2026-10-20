# Pronunciation decisions for book production

Use this across nonfiction, fiction, learning books, and classic adaptations.
Pronunciation is an authored part of the listening edition. Preserve ordinary
spelling in visible text; carry the chosen sounds separately into narration.
A clean audit or a plausible IPA string does not establish that the audio sounds
right. Report authored decisions, embedded annotations, renderer application,
and actual listening verification separately.

## Choose the pronunciation in context

Use Echo PR #600's EPUB instructions proactively across the whole listening
edition, before the first full render. Review every narrated block, including
headings, quotations, dialogue, captions, and Michael's guide passages. Keep a
chapter/section coverage record so a short watch list or sampled scan cannot
stand in for complete manuscript review. Unsupported annotation surfaces still
need a recorded pronunciation decision and a supported handling path.

Inventory all context-dependent pronunciations, names and places, unfamiliar or
foreign terms, technical vocabulary, abbreviations and initialisms, numbers and
symbols with ambiguous spoken forms, and archaic or poetic syllable/stress choices.
Include casing, possessives, and inflected forms actually present. Resolve each
candidate from its sentence and surrounding context, then embed every supported,
resolved decision. Do not wait for the listener to discover a mispronunciation,
cap the number of corrections, or leave known decisions only in research notes.

Every occurrence of **content**, **record**, and **read** is mandatory, but these
are the starting cases. Also look for words such as lead, wind, bow, wound, tear,
minute, live, present, object, and produce wherever their reading depends on
meaning or grammatical role. This list is illustrative, not exhaustive. For
classics, inspect syllable choices such as learned or blessed in their actual
passages. Search inventories candidates; the author resolves the intended reading.

| Word | Distinctions to preserve |
|---|---|
| content | Material or contents takes first-syllable stress; satisfied takes second-syllable stress. |
| record | A noun such as a historical record takes first-syllable stress; the verb meaning capture or document takes second-syllable stress. |
| read | Present/base forms sound like “reed”; past and past-participle forms sound like “red.” “I read every day” needs narrative tense/context; “I have read it” is a past participle. |

These are meaning reminders, not phoneme strings to feed the renderer. Do not
apply a book-wide pronunciation to a spelling with multiple senses. Use an
occurrence-specific annotation for each resolved context-dependent reading,
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

Use inline IPA for occurrence-specific choices and supported phrases; use linked
PLS lexicons for consistent recurring terms across every document that uses them.
Reuse verified decisions across the book, checking each match and each exception.
For ordinary unambiguous words with no pronunciation concern, retain normal
handling; filling every sentence with guessed IPA adds errors and interferes with
normalization. Extensive use means complete coverage of meaningful pronunciation
choices, with supported, evidence-backed annotations wherever they are needed.

## Embed using the verified Echo contract

Echo [PR #600](https://github.com/dfakkeldy/Echo/pull/600) implements the English
Kokoro contract `epub.*.ipa-v1`. Use its
[pinned authoring contract](https://github.com/dfakkeldy/Echo/blob/0198f39b290dadab2d7a648dcfaabe29e4cedcde/docs/epub-pronunciation-authoring.md)
and reusable fixture at
`Tools/Pronunciation/fixtures/pronunciation-annotated.epub` in Echo. That source
revision is a compatibility reference, not approval to install or select a
renderer. Verify that the installed renderer selected for the run includes this
support; a merged PR does not upgrade an installed package. Record the actual
renderer identity and contract revision in the production notes.

Use standard IPA without slash/bracket delimiters or Kokoro capital-letter
shorthand. Echo normalizes English diphthongs and affricates; it rejects unsupported
symbols, including syllabification dots, syllabic-consonant diacritics, and tone
marks. Each instruction is limited to 300 characters and must contain speech
symbols. Consult the contract's exact supported alphabet for each candidate.

### Inline occurrences

Declare the namespace and alphabet on the XHTML root; keep the words unchanged:

```xml
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:ssml="http://www.w3.org/2001/10/synthesis"
      xml:lang="en-US" ssml:alphabet="ipa">
  <head><title>Example</title></head>
  <body>
    <p>I will <span ssml:ph="ɹiːd">read</span> it tomorrow.</p>
    <p>I have <span ssml:ph="ɹɛd">read</span> it already.</p>
  </body>
</html>
```

These read examples illustrate the format and tense distinction, not a listening
verdict for a particular voice. Supply evidence-backed IPA for each occurrence
of content and record in the same way, preserving the chosen accent and stress.

Annotate whole words or phrases within one imported paragraph or heading.
Inline formatting is supported; nested pronunciation spans, cross-block spans,
empty annotations, and annotated text containing `[]()/` are not. Instructions
on code, images, head content, or captions are unsupported. Review those spoken
surfaces too, but do not force unsupported markup onto them: use a separately
verified override path or report the remaining limitation.

An annotated block bypasses Echo's deterministic text rewriting and optional
Foundation Models text normalization for the whole block. Check abbreviations,
numbers, and identifiers elsewhere in that paragraph and add supported spoken
instructions where necessary. Automatic pronunciation still handles unannotated
words, but do not assume the usual text expansion will occur.

### Recurring terms

For a chosen fictional-name pronunciation, a lexicon can contain:

```xml
<lexicon xmlns="http://www.w3.org/2005/01/pronunciation-lexicon"
         version="1.0" alphabet="ipa" xml:lang="en-US">
  <lexeme>
    <grapheme>Portia</grapheme>
    <grapheme>PORTIA</grapheme>
    <phoneme>ˈpɔɹʃə</phoneme>
  </lexeme>
</lexicon>
```

Save it as UTF-8 `names.pls`. If it sits beside the OPF, add this item inside the
existing OPF manifest (namespace `http://www.idpf.org/2007/opf`):

```xml
<item id="pronunciation-names" href="names.pls" media-type="application/pls+xml"/>
```

Inside the head of **each XHTML document that uses the lexicon**, add:

```xml
<link rel="pronunciation" type="application/pls+xml"
      hreflang="en-US" href="names.pls"/>
```

Adjust each href relative to its containing OPF or XHTML file; these examples
assume sibling files. Lexicons are document-scoped, local to the EPUB, and must
be declared in the manifest. Remote URLs, absolute paths, fragments, query strings,
and escaping paths are rejected. Do not add the PLS file to the reading spine.

Matching is case-sensitive, whole-word, leftmost-longest. Add explicit spelling,
casing, and possessive variants with their appropriate IPA: `Portia` does not
match `Portia's`. Each lexeme has one or more graphemes and exactly one phoneme;
conflicting entries reject import. Do not put ambiguous content, record, or read
in a global dictionary. English lexicons only; maximum 1 MiB per file, 32 links
per document, and 200 characters per grapheme. Aliases, roles, DTDs, and entity
declarations are unsupported. Follow the full contract for remaining restrictions.

### Assembly and precedence

Explicit user occurrence corrections win over per-book and global user
corrections, then inline EPUB instructions, linked PLS entries, and automatic
handling. A user correction overlapping an annotated phrase suppresses the whole
phrase instruction; inspect the other words rather than assuming they retain it.

`build_book.py` has no pronunciation-plan option. Build the draft EPUB first,
then embed with `../scripts/epub_pronunciation.py`, which every book skill shares:

1. `scan --epub draft.epub --out candidates.json` lists every candidate in the
   narrated text, with its context: content, record and read, other heteronyms,
   numerals, file names and initialisms. It's the coverage record to work from.
2. Author a decisions file. Each occurrence gives its word, its IPA and a quoted
   context that appears once in the book. Readings give file names and numerals
   that sit in annotated blocks. Lexicon entries cover recurring names. The
   script's docstring shows the format.
3. `apply --epub draft.epub --decisions decisions.json --out book.epub` writes a
   new EPUB. It declares the namespace, links the lexicon from every narrated
   document, adds the manifest item, keeps the mimetype entry first and stored,
   and confirms the visible text is unchanged. It fails on missing or ambiguous
   contexts, and writes nothing unless its own `check` passes.
4. Freeze `book.epub`.

`check --epub book.epub` is the narration gate, and the governed preflight runs
it before every fresh render. It refuses an EPUB with narrated text but no IPA,
with any content, record or read left without an inline reading (captions and
alt text included, where Echo can't take one), or with markup Echo can't use.
It also refuses three problems found in production:

- A lexicon grapheme that touches a dotted or hyphenated token. A lexeme for
  `md` matched inside `open-loops.md`, and synthesis stopped mid-render.
- A numeral, file name or symbol left without a reading in an annotated block,
  where Echo skips text expansion.
- Annotated text containing a slash. One span on `tiles/mail.json` made Echo
  import none of the book's blocks. Leave such a block unannotated instead.

Non-linear spine documents (such as a non-narrated appendix) and the nav
document aren't narrated, so the gate skips them. Do not claim the builder
embeds IPA by itself or write Misaki Markdown links into the reader's text.

If the installed renderer lacks support, preserve the pronunciation plan and
report that specific installation dependency. Continue independent manuscript
work; do not describe Echo's implementation itself as pending. A glossary or
IPA footnote is not an applied instruction, and an uncorrected render is not
pronunciation-verified.

Add the annotations before the final EPUB is hashed and frozen.
Inspect the packaged XHTML, lexicons, and manifest to confirm that the builder
actually preserved them. Keep visible spelling and character/guide boundaries
intact. Export the real Echo inventory from that final EPUB and bind decisions
to its occurrences using the supported contract. A markup-only EPUB change still
changes source bytes: refresh source-bound inventories, voice plans, and render
receipts through their normal workflows. Never patch a frozen package in place
or reuse evidence from its previous hash.

## Verify what was spoken

Inspect the audit’s `epubInline` and `epubLexicon` decisions. Check every required
occurrence against renderer evidence: intended IPA, actual
selected phonemes, and whether the annotation applied. Diagnose missing or
conflicting annotations and rejected symbols; successful import alone is not
proof of application. Respect explicit user pronunciation corrections and surface
conflicts with the authored plan. Do not silently strip unsupported phonemes.

Reconcile the full pronunciation plan with the final EPUB and render audit:
record reviewed blocks, planned occurrences, embedded inline/lexicon matches,
user-correction overrides, applied decisions, and unresolved or unsupported cases.
Check every planned occurrence, not just the number of annotations or the presence
of one successful `epubInline` decision. A user correction can legitimately win;
record that outcome and verify it. Explain every mismatch and resolve required
pronunciation gaps before calling the listening package complete. If none are
needed in a reviewed section, record that result rather than adding dummy markup.

Render targeted samples with the actual assigned voice and surrounding sentence.
Include every distinct authored pronunciation in its sentence and assigned voice,
including the senses of content, record, and read present in the book. Repeated
identical decisions can share a listening sample, but verify application at every
occurrence. Recheck changed context and any corrected or uncertain passage. For Michael's
passages use `am_michael`; a different speaker's successful sample does not verify
Michael's rendering. Check both sound and text/audio alignment. Use the existing
governed narration and pronunciation-review workflow for these samples and final
audio; this reference does not authorize a renderer build or bypass its checks.

Reimport an annotated EPUB to update persisted instructions; an existing M4B
does not change by itself. After manuscript changes, reassess affected contexts and regenerate their
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

### Permanent shared dictionary

`pronunciation-dictionary.json` is the version-controlled source for common
pronunciations. The standard `skill/scripts/build_book.py` builder embeds its
`entries` automatically in narrated spine documents; no per-book config is
needed. `epub_pronunciation.py apply` also merges these defaults. Whole-token,
case-sensitive matches preserve visible prose and skip unsupported surfaces.
Add spelling/case variants explicitly. Shared spans carry
`data-pronunciation="shared"`, so applying later per-book occurrences, readings
or lexicons can replace them. Existing authored spans and lexicons take priority.

The dictionary seeds email, assignee, ADHD, GitHub and past-tense misread, plus
existing public book lexicons. For present-tense misread use an occurrence
reading `mɪsˈɹiːd`. `contextual_readings` retain the existing authored inline IPA
(including heteronyms); `audit_readings` retain observed renderer output, which
may contain Kokoro shorthand or wrong selections. Neither is applied globally.
These migrated readings are not listening-verified. Normal narration checks
still apply: embedding defaults can make a block bypass Echo text expansion,
so its numbers/file names may need authored token readings before narration.

Investigation of reports grok-bots #252/#257: the public checkout contains no
Nothing Slips source EPUB, pronunciation audit, or narration input to reproduce
the reported extra vowel. The pre-change builder only escapes prose and adds
HTML; the pronunciation tool inserts the supplied IPA verbatim in `ssml:ph` or
PLS `phoneme` fields. Neither has a GitHub-specific prefix or vowel insertion
rule. The contract above notes that annotations bypass Echo text normalization;
that can change which renderer path handles a word, but does not establish the
cause of this report. The new GitHub default is `ˈɡɪtˌhʌb`, beginning with a
consonant, with no leading vowel. A renderer G2P/tokenization or synthesis issue
remains possible; the affected input and renderer audit are needed to locate it.
No extra-vowel fix is claimed and no audio was regenerated.

For the general IPA-tagged-word investigation and exact engine-boundary trace,
see [ipa-vowel-investigation.md](ipa-vowel-investigation.md). No vowel-insertion
cause or audio repair has been established.
