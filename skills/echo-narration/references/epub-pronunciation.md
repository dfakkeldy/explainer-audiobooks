# Pronunciation decisions for book production

Use this across nonfiction, fiction, learning books and classic adaptations.
Pronunciation is an authored part of the listening edition. Keep ordinary
spelling in the visible text and carry the chosen sounds separately into
narration. A clean audit or a plausible IPA string doesn't prove the audio
sounds right. Report authored decisions, embedded annotations, renderer
application and listening separately. Never claim listening, and never list it
as a follow-up or blocker for Dan.

## The rule

1. **Every word Echo would guess gets IPA before the render.** Echo reads a
   word from its misaki lexicon (`us_gold.json`, `us_silver.json`) or guesses
   it by letter rules, a "G2P fallback". Names (Ryan, Kyle, Eva), British
   spellings (labeller), coined words, file names (`Claude.ai`) and unit
   tokens (`5pp`) are guessed, and guesses sound wrong. Give each one a PLS
   lexeme or an inline reading, or write it out in words.
2. **Check words against the renderer's own lexicon.** Never use a system word
   list: `/usr/share/dict/words` has labeller, Kyle and Eva, and misaki has
   none of them. `epub_pronunciation.py check` reads the lexicon of the
   renderer that will narrate.
3. **Write initialisms closed and give each one reading per book.** Write AI,
   API, GDP, never A-I or A-P-I. Echo reads a capital A before a hyphen as the
   article "uh", so A-I becomes "uh-EYE". Then one initialism gets one
   pronunciation everywhere: all inline, all lexicon, or all left to misaki.
4. **Every heteronym gets an inline reading at every use.** This covers read,
   record, content, use, close, lead, present, estimate, increase and the rest
   of the family in `epub_pronunciation.py`. Headings, blocks with numbers and
   hyphenated compounds (`well-read`, `A-P-I records`) are not exempt.
5. **Probe-render every chapter that has new names.** Its captures must show
   zero fallbacks before the full render (see "Probe render" below).
6. **Delivery is refused when the post-render gate fails.** The narration
   wrapper runs `pronunciation_audit_gate.py` on every render's audit and
   leaves a failing render unaccepted. Fix the EPUB and render again.

The rest of this page says how.

## Choose the pronunciation in context

Review every narrated block before the first full render: headings, quotations,
dialogue, captions and the guide's passages included. Keep a chapter and
section coverage record, so a short watch list or a sample can't stand in for
the whole manuscript.

List the candidates: words the renderer would guess, heteronyms, names and
places, foreign and technical terms, abbreviations and initialisms, numbers and
symbols with more than one spoken form, and archaic syllable or stress choices
(learned, blessed). Include the casing, possessive and inflected forms that
actually occur. Resolve each one from its sentence, then embed the decision.
Don't wait for the listener to find a mistake, and don't cap the number of
corrections.

| Word | Distinctions to keep |
|---|---|
| content | Material or contents: first-syllable stress. Satisfied: second-syllable stress. |
| record | A noun such as a historical record: first-syllable stress. The verb (capture, document): second-syllable stress. |
| read | Present and base forms sound like "reed". Past and past participle sound like "red": "I have read it". |

These are meaning reminders, not phoneme strings. Never give a spelling with
more than one sense a book-wide pronunciation: annotate each occurrence, even
where Echo happens to agree today. Derive inflected forms; don't copy the base
word's IPA. An unresolved context stays an open decision. Don't rewrite
accepted prose only to steer automatic pronunciation; closing a hyphen-spelled
initialism or spelling out `5pp` is a pronunciation fix, not a style edit.

Keep a durable `pronunciation-plan.md` beside the book's source or research
notes. For each decision record the word or phrase, its source file and section,
the exact quoted context, which occurrence is meant, the sense or tense, the
IPA, the accent, the evidence or author decision, the scope and the
verification status. Use source locators while drafting; never invent Echo
block IDs or rely on word offsets surviving later edits.

Check real-word IPA against a dictionary or other authority in the intended
accent. For fictional names, record the author's choice; don't present it as
dictionary evidence. Keep standard IPA and any renderer-specific form apart.
Reuse approved name choices across books, but reassess ambiguous words in each
new sentence.

Use inline IPA for one occurrence and for phrases. Use a linked PLS lexicon for
a name or term with one pronunciation throughout the book. Leave ordinary,
unambiguous words that the lexicon knows alone: guessed IPA on every word adds
errors and switches off text expansion.

## Embed using the verified Echo contract

Echo [PR #600](https://github.com/dfakkeldy/Echo/pull/600) implements the
English Kokoro contract `epub.*.ipa-v1`. Use its
[pinned authoring contract](https://github.com/dfakkeldy/Echo/blob/0198f39b290dadab2d7a648dcfaabe29e4cedcde/docs/epub-pronunciation-authoring.md)
and the fixture `Tools/Pronunciation/fixtures/pronunciation-annotated.epub` in
Echo. That revision is a compatibility reference, not approval to install or
select a renderer. Check that the installed renderer you will narrate with
supports it, and record its identity in the production notes.

Use standard IPA with no slash or bracket delimiters and no Kokoro capital
shorthand. Echo normalizes English diphthongs and affricates. It rejects
syllable dots, syllabic-consonant marks and tone marks. Each instruction is at
most 300 characters and must contain speech symbols.

### Inline occurrences

Declare the namespace and alphabet on the XHTML root and keep the words:

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

Annotate whole words or phrases inside one paragraph or heading. Inline
formatting is fine. Nested spans, spans across blocks, empty spans and
annotated text containing `[]()/` are not. Code, images, head content and
captions can't carry instructions: review them too, and reword where needed.
Echo speaks only a cue ("Code listing.", or the figure caption) for a `<pre>`
block, never its code, so the check skips everything inside `<pre>`. Inline
`<code>` in a paragraph is spoken, and the check covers it.

An annotated block skips Echo's text expansion and optional Foundation Models
normalization for the whole block. A block is annotated when it has an inline
`ssml:ph` span or a word from a PLS its document links: Echo stores both as
pronunciation spans. Write numbers, abbreviations and identifiers in that
block as words, or give them readings.

### Recurring terms

A lexicon for a chosen name:

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

Save it as UTF-8 `names.pls`. Beside the OPF, declare it in the manifest:

```xml
<item id="pronunciation-names" href="names.pls" media-type="application/pls+xml"/>
```

and link it from the head of **each XHTML document that uses it**:

```xml
<link rel="pronunciation" type="application/pls+xml"
      hreflang="en-US" href="names.pls"/>
```

Hrefs are relative to their file. Remote URLs, absolute paths, fragments,
queries and escaping paths are rejected. Don't put the PLS in the spine.

Matching is case-sensitive, whole-word and leftmost-longest. Add spelling, case
and possessive variants with their own IPA: `Portia` doesn't match `Portia's`.
Each lexeme has one or more graphemes and exactly one phoneme. English only;
at most 1 MiB per file, 32 links per document and 200 characters per grapheme.
Never put a heteronym in a lexicon.

### Precedence

Explicit user occurrence corrections win over per-book and global user
corrections, then inline EPUB instructions, linked PLS entries and automatic
handling. A user correction that overlaps an annotated phrase suppresses the
whole phrase instruction.

## The tool

`build_book.py` has no pronunciation-plan option. Build the draft EPUB, then
embed with `../scripts/epub_pronunciation.py`, which every book skill shares.
Pass the renderer's resource directory as `--lexicon-dir`, for example
`~/Library/Application Support/Echo/Renderers/<source-sha>/<manifest-sha>/EchoNarrationResources`.

1. `scan --epub draft.epub --lexicon-dir DIR --out candidates.json` lists every
   candidate with its context: heteronyms (`mandatory`), hyphen-spelled
   initialisms, numerals and file names, initialisms, and the words Echo would
   guess (`fallback`). It's the coverage record to work from.
2. Author a decisions file: occurrences (word, IPA and a quoted context that
   appears once), readings for file names and numerals in annotated blocks, and
   lexicon entries for recurring names. The script's docstring shows the format.
3. `apply --epub draft.epub --decisions decisions.json --lexicon-dir DIR --out book.epub`
   writes a new EPUB. It declares the namespace, links the lexicon from every
   narrated document, adds the manifest item, keeps the mimetype entry first
   and stored, and confirms the visible text is unchanged. It writes nothing
   unless its own check passes.
4. `check --epub book.epub --lexicon-dir DIR` must pass. Then freeze
   `book.epub`. Outside the wrapper, `check` exits 65 without a lexicon.

`check` is the narration gate, and the governed preflight runs it, with the
attested renderer's lexicon, before every fresh render. It finds the lexicon
from `--lexicon-dir`, then `$ECHO_RESOURCE_DIR`, then the installed renderer
named by `$APPROVED_ECHO_PRONUNCIATION_SHA`. It fails closed when there is
none. It refuses:

- narrated text with no IPA at all, or markup Echo can't use;
- a word missing from the lexicon (with misaki's own plural, possessive, -ed
  and -ing rules), once per word with its count and first context. misaki
  reads the parts of a camelCase word apart (`SaaS` is `Saa` + `S`, except
  after `Mc`), so each part must be known even when the whole word is a key;
- a hyphen-spelled initialism (`A-I`, `A-P-Is`). Where the letters stand
  apart (`A-Z`, an `X-Y` plane), keep the hyphen and give each use a reading;
- a token Echo mangles: a period inside a word (`Claude.ai`, `CLAUDE.md`;
  `U.S.-based` is fine), letters after a number (`5pp`, `40km`), or a word
  that ends in Mr., Ms., Mrs. or Dr. before a period (`LLMs.` is read
  "LLMiz");
- the title `Ms.`, which Echo's text expansion reads as "Miz", a guessed word.
  That expansion runs only in blocks without IPA, so `Dr.`, `e.g.`, a month
  before a number (`Jan. 5`) and a standalone `km` or `hrs` pass there; in an
  annotated block they are read raw and need readings like any other word;
- a heteronym without an inline reading anywhere, including headings, number
  blocks, compounds, captions and alt text (reword where IPA can't go);
- a lexicon grapheme that touches a dotted or hyphenated token (`md` inside
  `open-loops.md` stopped synthesis mid-render);
- a numeral, file name or symbol without a reading in an annotated block;
- annotated text containing a slash (one such span made Echo import none of
  the book).

`scan` also lists does, row, address and polish. The renderer reads each one
way and the other sense is rare, so `check` doesn't require them; annotate one
where its sentence needs the other sense.

The lexicon test approximates Echo. It counts Echo's built-in overrides and
contextual words as known, but not Echo's supplemental CMU pack: `check` asks
for IPA for words only that pack knows, because its automatic entries have
given wrong stress and vowels (`long-distance` read "DEE-stance"). The
post-render gate is the backstop.

Non-linear spine documents (such as a non-narrated appendix) and the nav
document aren't narrated, so the gate skips them. Don't claim the builder
embeds IPA by itself, and don't write Misaki Markdown links into the reader's
text. A glossary or IPA footnote is not an applied instruction.

Add annotations before the final EPUB is hashed and frozen. A markup-only
change still changes source bytes: refresh source-bound inventories, voice
plans and render receipts through their normal workflows. Never patch a frozen
package in place or reuse evidence from its previous hash.

## Probe render

Before the full render, render each chapter that introduces new names with
the wrapper's partial mode (`--max-chapters 1`, then `--resume ...
--max-chapters 1`; see [narrating](narrating.md)). Run the gate on the
captures:

```bash
RUN_ID=$(/usr/local/bin/python3 -c \
  'import json,sys; print(json.load(open(sys.argv[1]))["runID"])' \
  "$RUN_ROOT/research/echo-render-current-attempt.json")
/usr/local/bin/python3 "$EXPLAINER_ROOT/skills/echo-narration/scripts/pronunciation_audit_gate.py" \
  "$RUN_ROOT/audio-work-$RUN_ID"/.anchors-ch*.json
```

It must print `pronunciation_gate: clean`. Fix every fallback in the EPUB and
probe again.

## Verify what was spoken

After every render the wrapper runs `pronunciation_audit_gate.py` on the audit
and refuses the render, which stays unaccepted for diagnosis, when:

- any decision came from the fallback (`source` "fallback", rule IDs
  `g2p.fallback.*` and `g2p.compound.*`);
- an "A" was read as the article "uh" (ɐ) as the first letter of a
  hyphen-spelled initialism ("A GPU" is a real article and passes);
- one initialism (two to six capitals, optional s) has more than one reading.

Each problem prints the word, its count, and the time and context of every use.
Fix the EPUB and render again. A name that truly can't be fixed goes in
`$RUN_ROOT/research/pronunciation-gate-accepted.json`, word by word, each with
a reason; there is none by default:

```json
{"schemaVersion": 1,
 "accepted": [{"check": "fallback", "word": "Quorvane",
               "reason": "why no reading can fix it"}]}
```

Then check the audit's `epubInline` and `epubLexicon` decisions against the
plan: intended IPA, selected phonemes, and whether each annotation applied.
Check every planned occurrence, not only the count of annotations. A user
correction can legitimately win; record that outcome. Explain every mismatch
and resolve required gaps before calling the package complete. Respect explicit
user corrections; don't silently strip unsupported phonemes.

Render targeted samples with the assigned voice and the surrounding sentence
for each distinct authored pronunciation, including each sense of content,
record and read in the book. For the guide's passages use `am_michael`; another
speaker's sample doesn't verify the guide. Use the governed narration workflow
for samples and final audio; this page doesn't authorize a renderer build or
bypass its checks.

Reimport an annotated EPUB to update persisted instructions; an existing M4B
doesn't change by itself. After manuscript changes, reassess the affected
contexts and regenerate their annotations; after pronunciation changes,
invalidate the affected audio through Echo's supported workflow. Keep earlier
accepted artifacts recoverable. Revise existing books only when asked. Never
claim words will always be right: report remaining uncertainty, and keep
phoneme verification apart from human listening.

If the installed renderer lacks support, keep the pronunciation plan and report
that installation dependency. Continue independent manuscript work. An
uncorrected render is not pronunciation-verified.

## Development-only handoff

Manuscript and concept skills collect known pronunciation decisions and open
questions in the same plan and name its path in the production handoff. During
concept work a risk list is enough; review every occurrence against the final
manuscript during production. Keep annotations outside accepted Markdown
chapter bytes. A pronunciation plan doesn't authorize EPUB creation, narration
or delivery in a manuscript-only task.

### Permanent shared dictionary

`pronunciation-dictionary.json` is the version-controlled source for common
pronunciations. `skill/scripts/build_book.py` embeds its `entries` in narrated
spine documents automatically, and `epub_pronunciation.py apply` merges them
too. Whole-token, case-sensitive matches keep visible prose and skip
unsupported surfaces. Add spelling and case variants explicitly. Shared spans
carry `data-pronunciation="shared"`, so later per-book occurrences, readings or
lexicons can replace them; existing authored spans and lexicons win.

The dictionary seeds email, assignee, ADHD, GitHub and past-tense misread, plus
the public books' lexicons. For present-tense misread use an occurrence reading
`mɪsˈɹiːd`. `contextual_readings` keep existing authored inline IPA
(heteronyms included); `audit_readings` keep observed renderer output, which may
contain Kokoro shorthand or wrong selections. Neither is applied globally, and
neither is listening-verified. Embedded defaults can make a block skip text
expansion, so its numbers and file names may need readings.

Reports grok-bots #252 and #257 (an extra vowel before IPA-tagged words) are
not reproduced: the public checkout has no affected input or audit, and neither
the builder nor this tool adds a vowel. The GitHub default is `ˈɡɪtˌhʌb`. See
[ipa-vowel-investigation.md](ipa-vowel-investigation.md); no cause or audio
repair is established.
